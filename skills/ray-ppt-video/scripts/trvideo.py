"""
ray-PPT-TrVideo — Main orchestrator: PPTX → Training Video (one-stop).
Usage: python trvideo.py input.pptx [--tts-engine qwen3] [--voice zh-CN-YunjianNeural] [--output output.mp4]

Requirements: PowerPoint (Windows COM), python-pptx, edge-tts or qwen-tts, ffmpeg.
"""
import argparse
import json
import os
import subprocess
import sys
import time

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))


# ────────────────────────────────────────────────
# Pipeline Lock (cross-platform)
# ────────────────────────────────────────────────

class PipelineLock:
    """Simple PID-file based lock."""

    def __init__(self, output_dir: str):
        os.makedirs(output_dir, exist_ok=True)
        self.lock_path = os.path.join(output_dir, ".pipeline.lock")
        self.lock_fd = None

    def acquire(self) -> bool:
        if os.path.exists(self.lock_path):
            try:
                with open(self.lock_path, "r") as f:
                    pid = int(f.read().strip())
                os.kill(pid, 0)
                print(f"[LOCK] 另一个流水线 (PID {pid}) 正在运行此目录。", file=sys.stderr)
                return False
            except (ValueError, ProcessLookupError, OSError):
                print("[LOCK] 过期锁文件，自动清理。")
                try:
                    os.remove(self.lock_path)
                except OSError:
                    pass
        try:
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
# Dependency check
# ────────────────────────────────────────────────

def check_deps():
    deps = {}
    try:
        import pptx; deps["python-pptx"] = True
    except ImportError:
        deps["python-pptx"] = False
    try:
        import edge_tts; deps["edge-tts"] = True
    except ImportError:
        deps["edge-tts"] = False
    try:
        from qwen_tts import Qwen3TTSModel; deps["qwen-tts"] = True
    except ImportError:
        deps["qwen-tts"] = False
    return deps


def find_ffmpeg():
    """Find ffmpeg binary."""
    import shutil
    # Try system PATH first
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    # Try imageio-ffmpeg
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        pass
    return "ffmpeg"


# ────────────────────────────────────────────────
# PPT processing
# ────────────────────────────────────────────────

def extract_text(pptx_path: str) -> list:
    """Extract slide text content from PPTX."""
    from pptx import Presentation
    prs = Presentation(pptx_path)
    slides = []
    for i, slide in enumerate(prs.slides, 1):
        texts = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                t = shape.text_frame.text.strip()
                if t:
                    texts.append(t)
        slides.append({"slide": i, "text": "\n".join(texts)})
    return slides


def export_slides(pptx_path: str, out_dir: str, width: int = 1920, height: int = 1080):
    """Export slides to PNG using PowerPoint COM automation."""
    ps_script = f'''
$ErrorActionPreference = "Stop"
$pp = New-Object -ComObject PowerPoint.Application
$pp.Visible = 1
$pres = $pp.Presentations.Open("{pptx_path}", $true, $false, $false)
$total = $pres.Slides.Count
for ($i = 1; $i -le $total; $i++) {{
    $s = $pres.Slides.Item($i)
    $out = Join-Path "{out_dir}" ("slide_{{0:D2}}.png" -f $i)
    $s.Export($out, "PNG", {width}, {height})
    Write-Host "  slide $i / $total"
}}
$pres.Close()
$pp.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($pres) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($pp) | Out-Null
Write-Host "DONE: $total slides exported"
'''
    ps_file = os.path.join(out_dir, "_export_slides.ps1")
    # Use UTF-8 BOM for PowerShell compatibility with Chinese paths
    with open(ps_file, "w", encoding="utf-8-sig") as f:
        f.write(ps_script)

    result = subprocess.run(
        ["powershell", "-ExecutionPolicy", "Bypass", "-File", ps_file],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"ERROR: {result.stderr}")
    try:
        os.remove(ps_file)
    except OSError:
        pass


def detect_image_heavy_slides(pptx_path: str) -> list:
    """Detect slides with mostly pictures/screenshots."""
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE

    prs = Presentation(pptx_path)
    image_slides = []
    for i, slide in enumerate(prs.slides, 1):
        total = pictures = 0
        for shape in slide.shapes:
            if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                pictures += 1
                total += 1
            elif shape.has_text_frame:
                total += 1
        if pictures > 0 and (pictures / max(total, 1)) >= 0.5:
            image_slides.append({
                "slide": i, "picture_count": pictures, "total_shapes": total
            })
    return image_slides


def generate_narration_prompt(slides: list) -> str:
    """Build LLM prompt for narration generation."""
    slide_texts = "\n\n".join(
        f"== Slide {s['slide']} ==\n{s['text']}" for s in slides
    )
    return f"""你是一位化工安全培训讲师。请根据以下 PPT 的**实际内容**，为每页幻灯片生成口语化的中文讲解旁白。

**关键要求**:
1. **严格对齐 PPT 内容**：旁白必须解释"这页 PPT 上写了什么"，不能凭主题自由发挥。
2. **以 PPT 文字/图片为准**：如果 PPT 使用了特定术语、方法、图表名称，必须原样讲解，不能替换为通用知识或相似概念。
3. **图片页需识别后讲解**：如果某页包含图片、截图、漫画、表格海报，必须查看导出的 PNG 图片并依据实际内容写旁白，不能臆造。
4. 正式培训风格，专业但不生硬；每段 10-60 秒（中文约 5 字/秒估算）。
5. 包含口语衔接词，如"接下来我们看…"、"总结一下…"。
6. 不要机械照读 PPT 原文，要用讲师口吻解释，但不得偏离 PPT 实际内容。

输出格式：JSON 数组，每页一个对象，slide 字段为页码，text 字段为旁白文字。
[
  {{"slide": 1, "text": "大家好，欢迎参加..."}},
  ...
]

PPT 内容：
{slide_texts}"""


# ────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PPTX → Training Video (one-stop)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default: auto-select TTS engine
  python trvideo.py training.pptx

  # Use edge-tts with specific voice
  python trvideo.py training.pptx --tts-engine edge --voice zh-CN-XiaoxiaoNeural

  # Use Qwen3-TTS preset voice
  python trvideo.py training.pptx --tts-engine qwen3 --speaker Uncle_Fu

  # Use Qwen3-TTS voice cloning
  python trvideo.py training.pptx --tts-engine qwen3 --reference-voice voice.wav

  # Regenerate specific slides
  python trvideo.py training.pptx --regenerate 1 3 5
        """
    )
    parser.add_argument("pptx", help="Input PPTX file path")
    parser.add_argument("--output", "-o", default=None,
                        help="Output MP4 path (default: same dir as PPTX)")
    parser.add_argument("--tts-engine", choices=["auto", "qwen3", "edge"],
                        default="auto", help="TTS engine (default: auto)")
    parser.add_argument("--voice", default="zh-CN-YunjianNeural",
                        help="edge-tts voice (default: zh-CN-YunjianNeural)")
    parser.add_argument("--speaker", default="Vivian",
                        help="Qwen3-TTS speaker (default: Vivian)")
    parser.add_argument("--reference-voice", default="",
                        help="Reference audio for Qwen3-TTS voice cloning")
    parser.add_argument("--instruct", default="",
                        help="Qwen3-TTS CustomVoice instruct")
    parser.add_argument("--subtitle-mode", choices=["burn", "soft", "both"],
                        default="burn", help="Subtitle mode (default: burn)")
    parser.add_argument("--work-dir", default=None,
                        help="Working directory (default: PPTX dir/_trvideo)")
    parser.add_argument("--regenerate", nargs="*", type=int, default=[],
                        help="Regenerate only specific slide numbers")
    parser.add_argument("--skip-steps", nargs="*", type=int, default=[],
                        help="Skip specific steps (1-6)")
    parser.add_argument("--resume-from", type=int, default=None,
                        help="Resume from step N (1-6): auto-skips steps < N "
                             "(v2.2, borrowed from video-tutorial-v2-publish)")
    args = parser.parse_args()

    # --resume-from N → auto-skip all steps < N
    if args.resume_from is not None:
        if args.resume_from < 1 or args.resume_from > 6:
            print(f"ERROR: --resume-from must be 1-6, got {args.resume_from}")
            return 1
        skip = set(args.skip_steps)
        for s in range(1, args.resume_from):
            skip.add(s)
        args.skip_steps = sorted(skip)
        print(f"Resuming from step {args.resume_from} → auto-skipping steps 1-{args.resume_from - 1}")

    # Check deps
    deps = check_deps()
    # At least one TTS engine must be available
    has_tts = deps.get("edge-tts", False) or deps.get("qwen-tts", False)
    if not deps.get("python-pptx", False):
        print("MISSING: python-pptx")
        print("  pip install python-pptx")
        return 1
    if not has_tts:
        print("MISSING: No TTS engine available!")
        print("  pip install edge-tts       (minimum)")
        print("  pip install -U qwen-tts    (recommended)")
        return 1

    pptx_abs = os.path.abspath(args.pptx)
    base_dir = args.work_dir or os.path.join(os.path.dirname(pptx_abs), "_trvideo")
    slides_dir = os.path.join(base_dir, "slides")
    audio_dir = os.path.join(base_dir, "audio")
    narration_json = os.path.join(base_dir, "narration.json")
    srt_file = os.path.join(base_dir, "subtitles.srt")
    output_mp4 = args.output or os.path.join(
        base_dir, os.path.splitext(os.path.basename(pptx_abs))[0] + "_video.mp4")

    os.makedirs(slides_dir, exist_ok=True)
    os.makedirs(audio_dir, exist_ok=True)

    # Acquire lock
    lock = PipelineLock(base_dir)
    if not lock.acquire():
        return 1

    try:
        t_start = time.time()

        print(f"Input:  {pptx_abs}")
        print(f"Output: {output_mp4}")
        print(f"TTS:    {args.tts_engine}")
        print()

        # Step 1: Extract text (unless skipping)
        if 1 not in args.skip_steps:
            print("=== Step 1: Extracting PPT content ===")
            slides = extract_text(pptx_abs)
            print(f"  Found {len(slides)} slides")
            for s in slides[:3]:
                print(f"  Slide {s['slide']}: {s['text'][:60]}...")
        else:
            print(f"=== Step 1: SKIPPED ===")

        # Step 2: Export slides (unless skipping)
        if 2 not in args.skip_steps:
            print("\n=== Step 2: Exporting slides to PNG (PowerPoint COM) ===")
            export_slides(pptx_abs, slides_dir)
        else:
            print(f"=== Step 2: SKIPPED ===")

        # Step 2b: Detect image-heavy slides
        print("\n=== Step 2b: Detecting image-heavy slides ===")
        image_slides = detect_image_heavy_slides(pptx_abs)
        if image_slides:
            print(f"  WARNING: Found {len(image_slides)} slides with mostly pictures:")
            for info in image_slides:
                print(f"    Slide {info['slide']:2d}: {info['picture_count']} pics / "
                      f"{info['total_shapes']} shapes")
            print("  ACTION: Inspect PNG exports before generating narration.")
            print("  Do NOT fabricate content for image-heavy slides!")
        else:
            print("  No image-heavy slides detected.")

        # Step 3: Narration script check
        if 3 not in args.skip_steps:
            print("\n=== Step 3: Narration script ===")
            if os.path.exists(narration_json):
                print(f"  Using existing: {narration_json}")
            else:
                prompt_file = os.path.join(base_dir, "_narration_prompt.txt")
                with open(prompt_file, "w", encoding="utf-8") as f:
                    f.write(generate_narration_prompt(slides))
                print(f"  Prompt saved to: {prompt_file}")
                print(f"  Generate narration and save as: {narration_json}")
                print(f"  Then re-run or continue with steps 4-6 manually.")
                return 0
        else:
            print(f"=== Step 3: SKIPPED ===")

        # Step 4: TTS
        if 4 not in args.skip_steps:
            print("\n=== Step 4: Generating TTS audio ===")
            tts_script = os.path.join(SKILL_DIR, "generate_tts.py")
            tts_cmd = [
                sys.executable, tts_script,
                narration_json, audio_dir,
                "--tts-engine", args.tts_engine,
            ]
            if args.tts_engine in ("edge", "auto"):
                tts_cmd += ["--voice", args.voice]
            if args.tts_engine in ("qwen3", "auto"):
                tts_cmd += ["--speaker", args.speaker]
            if args.reference_voice:
                tts_cmd += ["--reference-voice", args.reference_voice]
            if args.instruct:
                tts_cmd += ["--instruct", args.instruct]
            if args.regenerate:
                tts_cmd += ["--regenerate"] + [str(s) for s in args.regenerate]
            subprocess.run(tts_cmd, check=True)
        else:
            print(f"=== Step 4: SKIPPED ===")

        # Step 5: SRT subtitles
        if 5 not in args.skip_steps:
            print("\n=== Step 5: Generating subtitles ===")
            srt_script = os.path.join(SKILL_DIR, "generate_srt.py")
            subprocess.run([
                sys.executable, srt_script,
                narration_json, audio_dir, srt_file
            ], check=True)
        else:
            print(f"=== Step 5: SKIPPED ===")

        # Step 6: Assemble video
        if 6 not in args.skip_steps:
            print("\n=== Step 6: Assembling video ===")
            asm_script = os.path.join(SKILL_DIR, "assemble_video.py")
            asm_cmd = [
                sys.executable, asm_script,
                narration_json, slides_dir, audio_dir, srt_file, output_mp4,
                "--subtitle-mode", args.subtitle_mode,
            ]
            subprocess.run(asm_cmd, check=True)
        else:
            print(f"=== Step 6: SKIPPED ===")

        elapsed = time.time() - t_start
        print(f"\n{'='*50}")
        print(f"  FINISHED! ({elapsed:.0f}s / {elapsed/60:.1f} min)")
        print(f"  Video: {output_mp4}")
        print(f"  SRT:   {srt_file}")
        print(f"{'='*50}")
        return 0

    finally:
        lock.release()


if __name__ == "__main__":
    exit(main())
