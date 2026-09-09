#!/usr/bin/env python3
"""
ray-PPT-TrVideo — Step 3/4: Generate TTS audio from narration JSON.
Dual engine: Qwen3-TTS (local, voice cloning) + edge-tts (online, preset voices).

Usage:
  # edge-tts (default)
  python generate_tts.py narration.json audio/ --voice zh-CN-YunjianNeural

  # Qwen3-TTS preset voice
  python generate_tts.py narration.json audio/ --tts-engine qwen3 --speaker Vivian

  # Qwen3-TTS voice cloning
  python generate_tts.py narration.json audio/ --tts-engine qwen3 --reference-voice voice.wav

  # Regenerate specific slides
  python generate_tts.py narration.json audio/ --regenerate 1 3 5
"""
import argparse
import asyncio
import json
import os
import sys
import time
import warnings

# Suppress noisy torch/future warnings
warnings.filterwarnings("ignore", category=FutureWarning)


# ────────────────────────────────────────────────
# Voice presets
# ────────────────────────────────────────────────

QWEN3_SPEAKERS = {
    "Vivian":       "明亮的年轻女声（默认推荐）",
    "Serena":       "温暖、温柔的年轻女声",
    "Uncle_Fu":     "成熟的男性声音，醇厚音色",
    "Dylan":        "年轻的北京男声",
    "Eric":         "活泼的成都男声",
    "Ryan":         "富有节奏感的英文男声",
    "Aiden":        "阳光的美国男声",
}

EDGE_VOICES = {
    "zh-CN-XiaoxiaoNeural":  "晓晓（女，温暖自然）",
    "zh-CN-XiaoyiNeural":    "晓伊（女，亲切活泼）",
    "zh-CN-YunjianNeural":   "云健（男，沉稳大气）",
    "zh-CN-YunxiNeural":     "云希（男，年轻阳光）",
    "zh-CN-YunyangNeural":   "云扬（男，新闻播报）",
}


# ────────────────────────────────────────────────
# Dependency checks
# ────────────────────────────────────────────────

def _has_qwen3():
    try:
        from qwen_tts import Qwen3TTSModel  # noqa: F401
        return True
    except ImportError:
        return False


def _has_edge_tts():
    try:
        import edge_tts  # noqa: F401
        return True
    except ImportError:
        return False


def _has_torch():
    try:
        import torch  # noqa: F401
        return True
    except ImportError:
        return False


def _detect_torch_device():
    """Detect best available torch device and dtype."""
    try:
        import torch
        if torch.cuda.is_available():
            return "cuda:0", torch.bfloat16, "flash_attention_2"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps", torch.bfloat16, "sdpa"
        return "cpu", torch.float32, "eager"
    except ImportError:
        return "cpu", None, "eager"


# ────────────────────────────────────────────────
# Pipeline Lock (cross-platform)
# ────────────────────────────────────────────────

class PipelineLock:
    """Simple PID-file based lock for preventing concurrent runs."""

    def __init__(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        self.lock_path = os.path.join(output_dir, ".tts.lock")
        self.lock_fd = None

    def acquire(self) -> bool:
        if os.path.exists(self.lock_path):
            try:
                with open(self.lock_path, "r") as f:
                    pid = int(f.read().strip())
                os.kill(pid, 0)
                print(f"[LOCK] 另一个 TTS 进程 (PID {pid}) 正在运行，退出。",
                      file=sys.stderr)
                return False
            except (ValueError, ProcessLookupError, OSError):
                print("[LOCK] 检测到过期锁文件，自动清理。")
                try:
                    os.remove(self.lock_path)
                except OSError:
                    pass

        try:
            import tempfile
            fd = os.open(self.lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            self.lock_fd = fd
            return True
        except OSError:
            return False

    def release(self):
        if self.lock_fd is not None:
            try:
                os.close(self.lock_fd)
            except OSError:
                pass
            self.lock_fd = None
        if os.path.exists(self.lock_path):
            try:
                os.remove(self.lock_path)
            except OSError:
                pass


# ────────────────────────────────────────────────
# Audio utility
# ────────────────────────────────────────────────

def _get_audio_duration(path: str) -> float:
    """Get audio duration from file."""
    try:
        import subprocess, re
        r = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
             path],
            capture_output=True, text=True, timeout=10
        )
        if r.returncode == 0 and r.stdout.strip():
            return float(r.stdout.strip())
    except Exception:
        pass
    return -1.0


def _audio_exists_valid(path: str, min_duration: float = 0.5) -> bool:
    """Check if audio file exists and is valid (non-zero, reasonable duration)."""
    if not os.path.exists(path):
        return False
    if os.path.getsize(path) < 1024:  # < 1KB is likely broken
        return False
    dur = _get_audio_duration(path)
    return dur >= min_duration


# ────────────────────────────────────────────────
# Qwen3-TTS Engine
# ────────────────────────────────────────────────

class Qwen3Engine:
    """Qwen3-TTS wrapper supporting clone/custom/voice-design modes."""

    BASE_MODELS = [
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
    ]
    CUSTOM_MODELS = [
        "Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
        "Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice",
    ]
    VOICEDESIGN_MODELS = [
        "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
    ]

    # Sampling params for consistent tone across sentences
    TEMPERATURE = 0.3
    TOP_K = 30
    TOP_P = 0.8
    SEED = 42
    PERIODIC_RELOAD = 30  # sentences before model reload

    def __init__(self, speaker="Vivian", reference_voice="", ref_text="",
                 voice_design="", instruct=""):
        self.speaker = speaker
        self.reference_voice = reference_voice
        self.ref_text = ref_text
        self.voice_design = voice_design
        self.instruct = instruct
        self.model = None
        self.model_name = ""
        self.sample_rate = 24000
        self.is_clone = bool(reference_voice and os.path.isfile(reference_voice))
        self.is_design = bool(voice_design)
        self.x_vector_only = False
        self._clone_prompt = None
        self._sentences_since_reload = 0

        device, dtype, attn = _detect_torch_device()
        print(f"[Qwen3-TTS] 设备: {device}, 精度: {dtype}")

        if self.is_clone:
            print(f"[Qwen3-TTS] 声音克隆模式")
            candidates = self.BASE_MODELS
        elif self.is_design:
            print(f"[Qwen3-TTS] 语音设计模式: {voice_design}")
            candidates = self.VOICEDESIGN_MODELS
        else:
            print(f"[Qwen3-TTS] 预设音色模式: {speaker}")
            if not self.instruct:
                self.instruct = "用标准的新闻播音腔朗读，字正腔圆，语速稍快，节奏稳定"
            candidates = self.CUSTOM_MODELS

        from qwen_tts import Qwen3TTSModel
        loaded = False
        for mid in candidates:
            try:
                print(f"[Qwen3-TTS] 加载: {mid}")
                self.model = Qwen3TTSModel.from_pretrained(
                    mid, device_map=device, dtype=dtype,
                    attn_implementation=attn
                )
                self.model_name = mid
                loaded = True
                break
            except Exception as e:
                print(f"[Qwen3-TTS] 跳过 {mid}: {e}")

        if not loaded:
            raise RuntimeError("无法加载任何 Qwen3-TTS 模型")

        # Pre-warm voice clone prompt if applicable
        if self.is_clone:
            self._warm_clone()

    def _warm_clone(self):
        """Build voice clone prompt from reference audio."""
        dur = _get_audio_duration(self.reference_voice)
        print(f"[Qwen3-TTS] 参考音频时长: {dur:.1f}s")

        # Trim reference to 15s max for ICL mode
        ref_path = self.reference_voice
        if dur > 15:
            import subprocess, tempfile
            tmp = os.path.join(tempfile.gettempdir(), "ref_trim_15s.wav")
            subprocess.run([
                "ffmpeg", "-y", "-i", self.reference_voice,
                "-t", "15", "-acodec", "pcm_s16le", "-ar", "24000",
                "-ac", "1", tmp
            ], capture_output=True)
            if os.path.isfile(tmp):
                ref_path = tmp
                print(f"[Qwen3-TTS] 参考音频已截取为 15s")

        # Transcribe with whisper if no ref_text
        if not self.ref_text:
            try:
                import whisper
                m = whisper.load_model("base")
                result = m.transcribe(ref_path, language="zh")
                self.ref_text = result.get("text", "").strip()
                if self.ref_text:
                    print(f"[Whisper] 转录: {self.ref_text[:80]}...")
            except Exception as e:
                print(f"[Whisper] 转录失败: {e}")

        # Build ICL prompt (only if ref is short enough)
        if dur <= 15 and self.ref_text:
            print("[Qwen3-TTS] 使用 ICL 模式（声音克隆效果最佳）")
            self._clone_prompt = self.model.generate_voice_clone_prompt(
                ref_audio=ref_path, ref_text=self.ref_text
            )
        else:
            print("[Qwen3-TTS] 使用 x_vector_only 模式（仅声纹嵌入）")
            self.x_vector_only = True

    def _reload(self):
        """Periodic model reload to maintain quality."""
        from qwen_tts import Qwen3TTSModel
        device, dtype, attn = _detect_torch_device()
        self.model = Qwen3TTSModel.from_pretrained(
            self.model_name, device_map=device, dtype=dtype,
            attn_implementation=attn
        )
        self._sentences_since_reload = 0
        if self.is_clone:
            self._warm_clone()

    def _check_reload(self):
        self._sentences_since_reload += 1
        if self._sentences_since_reload >= self.PERIODIC_RELOAD:
            print(f"    [定期重载] {self._sentences_since_reload} 句后重载模型...")
            self._reload()

    def _max_tokens(self, text: str) -> int:
        """Estimate max_new_tokens for given Chinese text."""
        chars = len(text)
        return max(128, min(chars * 12, 2048))

    def generate(self, text: str) -> tuple:
        """Generate audio for text. Returns (numpy_array, sample_rate)."""
        import torch
        torch.manual_seed(self.SEED)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.SEED)

        max_tok = self._max_tokens(text)

        if self.is_clone:
            if self._clone_prompt is not None:
                wavs, sr = self.model.generate_voice_clone(
                    text=text, language="Chinese",
                    voice_clone_prompt=self._clone_prompt,
                    temperature=self.TEMPERATURE,
                    top_k=self.TOP_K, top_p=self.TOP_P,
                    max_new_tokens=max_tok,
                )
            else:
                wavs, sr = self.model.generate_voice_clone(
                    text=text, language="Chinese",
                    ref_audio=self.reference_voice,
                    ref_text=self.ref_text if not self.x_vector_only else None,
                    x_vector_only_mode=self.x_vector_only,
                    temperature=self.TEMPERATURE,
                    top_k=self.TOP_K, top_p=self.TOP_P,
                    max_new_tokens=max_tok,
                )
        elif self.is_design:
            wavs, sr = self.model.generate_voice_design(
                text=text, instruct=self.voice_design,
                language="Chinese",
                temperature=self.TEMPERATURE,
                top_k=self.TOP_K, top_p=self.TOP_P,
                max_new_tokens=max_tok,
            )
        else:
            kwargs = dict(
                text=text, language="Chinese", speaker=self.speaker,
                temperature=self.TEMPERATURE,
                top_k=self.TOP_K, top_p=self.TOP_P,
                max_new_tokens=max_tok,
            )
            if self.instruct:
                kwargs["instruct"] = self.instruct
            wavs, sr = self.model.generate_custom_voice(**kwargs)

        self._check_reload()
        return wavs, sr


# ────────────────────────────────────────────────
# TTS Generation
# ────────────────────────────────────────────────

def _save_audio(data, sr: int, path: str):
    """Save numpy audio array to MP3."""
    import numpy as np
    import subprocess, tempfile

    # Normalize
    peak = np.max(np.abs(data))
    if peak > 0:
        data = data / peak * 0.95
    data = (data * 32767).astype(np.int16)

    # Write WAV temp, convert to MP3
    tmp_wav = path.replace(".mp3", ".tmp.wav")
    try:
        import wave
        with wave.open(tmp_wav, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(data.tobytes())

        subprocess.run([
            "ffmpeg", "-y", "-i", tmp_wav,
            "-codec:a", "libmp3lame", "-b:a", "192k",
            "-ar", "44100", "-ac", "2",
            path
        ], capture_output=True, check=True)
    finally:
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)


async def _generate_edge_tts(slide_num: int, text: str, voice: str,
                              out_dir: str, force: bool, rate: str = "+5%"):
    """Generate single slide audio via edge-tts."""
    out_path = os.path.join(out_dir, f"slide_{slide_num:02d}.mp3")
    if not force and _audio_exists_valid(out_path):
        print(f"  [skip] slide {slide_num:02d}")
        return
    import edge_tts
    communicate = edge_tts.Communicate(text, voice, rate=rate)
    await communicate.save(out_path)
    print(f"  [done] slide {slide_num:02d}")


def _generate_qwen_tts(slide_num: int, text: str, engine: Qwen3Engine,
                        out_dir: str, force: bool):
    """Generate single slide audio via Qwen3-TTS."""
    out_path = os.path.join(out_dir, f"slide_{slide_num:02d}.mp3")
    if not force and _audio_exists_valid(out_path):
        print(f"  [skip] slide {slide_num:02d}")
        return

    max_retries = 3
    for attempt in range(max_retries):
        try:
            wavs, sr = engine.generate(text)
            _save_audio(wavs, sr, out_path)
            print(f"  [done] slide {slide_num:02d}")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  [retry] slide {slide_num:02d}: {e}")
                time.sleep(2)
            else:
                print(f"  [FAIL] slide {slide_num:02d}: {e}")
                raise


def _engine_consistency_check(out_dir: str, engine: str) -> str:
    """Check if TTS engine changed; clean old audio if so."""
    marker = os.path.join(out_dir, ".tts_engine")
    if os.path.exists(marker):
        with open(marker, "r") as f:
            prev = f.read().strip()
        if prev != engine:
            print(f"[TTS] 引擎变更: {prev} → {engine}，清理旧音频...")
            for fname in os.listdir(out_dir):
                if fname.startswith("slide_") and fname.endswith(".mp3"):
                    try:
                        os.remove(os.path.join(out_dir, fname))
                    except OSError:
                        pass
    with open(marker, "w") as f:
        f.write(engine)
    return engine


# ────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Generate TTS audio from narration JSON")
    parser.add_argument("narration_json", help="Path to narration.json")
    parser.add_argument("output_dir", help="Output directory for MP3 files")

    # Engine selection
    parser.add_argument("--tts-engine", choices=["auto", "qwen3", "edge"],
                        default="auto", help="TTS engine (default: auto)")
    parser.add_argument("--voice", default="zh-CN-YunjianNeural",
                        help="edge-tts voice name")
    parser.add_argument("--speaker", default="Vivian",
                        help="Qwen3-TTS speaker name")
    parser.add_argument("--reference-voice", default="",
                        help="Reference audio for Qwen3-TTS voice cloning")
    parser.add_argument("--ref-text", default="",
                        help="Transcript of reference audio (optional)")
    parser.add_argument("--voice-design", default="",
                        help="Voice design instruction for Qwen3-TTS")
    parser.add_argument("--instruct", default="",
                        help="CustomVoice instruct for Qwen3-TTS")

    # Behavior
    parser.add_argument("--force", action="store_true",
                        help="Overwrite existing audio files")
    parser.add_argument("--regenerate", nargs="*", type=int, default=[],
                        help="Regenerate only specified slide numbers")
    parser.add_argument("--concurrency", type=int, default=5,
                        help="Concurrency for edge-tts (default: 5)")
    parser.add_argument("--rate", default="+5%",
                        help="edge-tts speech rate (e.g. +5% faster, -8% slower)")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # Acquire lock
    lock = PipelineLock(args.output_dir)
    if not lock.acquire():
        sys.exit(1)
    try:
        # Load narration
        with open(args.narration_json, encoding="utf-8") as f:
            narrations = json.load(f)

        # Filter by --regenerate
        regen_set = set(args.regenerate)
        if regen_set:
            print(f"[TTS] 重新生成模式: slides {sorted(regen_set)}")
            narrations = [n for n in narrations if n["slide"] in regen_set]
            args.force = True

        if not narrations:
            print("[TTS] 没有需要生成的幻灯片")
            return

        # Determine engine
        if args.tts_engine == "auto":
            if _has_qwen3():
                engine_type = "qwen3"
            elif _has_edge_tts():
                engine_type = "edge"
            else:
                print("[ERROR] 未安装任何 TTS 引擎！", file=sys.stderr)
                print("  pip install -U qwen-tts   (推荐，本地高质量)", file=sys.stderr)
                print("  pip install edge-tts       (备选，需联网)", file=sys.stderr)
                sys.exit(1)
        else:
            engine_type = args.tts_engine
            if engine_type == "qwen3" and not _has_qwen3():
                print("[ERROR] Qwen3-TTS 未安装: pip install -U qwen-tts", file=sys.stderr)
                sys.exit(1)
            if engine_type == "edge" and not _has_edge_tts():
                print("[ERROR] edge-tts 未安装: pip install edge-tts", file=sys.stderr)
                sys.exit(1)

        # Engine consistency
        _engine_consistency_check(args.output_dir, engine_type)

        print(f"[TTS] 引擎: {engine_type}")
        print(f"[TTS] 幻灯片: {len(narrations)}")

        if engine_type == "qwen3":
            # Qwen3-TTS path
            engine = Qwen3Engine(
                speaker=args.speaker,
                reference_voice=args.reference_voice,
                ref_text=args.ref_text,
                voice_design=args.voice_design,
                instruct=args.instruct,
            )
            for item in narrations:
                slide = item["slide"]
                text = item.get("tts_text", item["text"])
                _generate_qwen_tts(slide, text, engine, args.output_dir, args.force)
        else:
            # edge-tts path
            tasks = [
                _generate_edge_tts(
                    item["slide"],
                    item.get("tts_text", item["text"]),
                    args.voice,
                    args.output_dir,
                    args.force,
                    args.rate
                )
                for item in narrations
            ]
            for i in range(0, len(tasks), args.concurrency):
                batch = tasks[i:i + args.concurrency]
                await asyncio.gather(*batch)
                print(f"  batch {i // args.concurrency + 1}/"
                      f"{(len(tasks) + args.concurrency - 1) // args.concurrency} done")

        print("[TTS] 全部完成!")
    finally:
        lock.release()


if __name__ == "__main__":
    asyncio.run(main())
