# -*- coding: utf-8 -*-
"""
ray-MM 音频/视频转写 v1：录音/录像 → 带时间戳转写文本（transcript.md）

用途：把会议录音（.mp3/.wav/.m4a）或会议录像（.mp4/.avi/.mov）转写为文本，
供纪要生成步骤消费。

用法：
    python transcribe_audio.py <音频或视频文件> [--model small] [--out <输出目录>]

依赖（首次使用安装，约 1-2GB 随模型）：
    pip install faster-whisper
    视频抽音轨需 ffmpeg（PATH 中可用；或用 IMAGEIO_FFMPEG_EXE 指定）

模型选择：
    tiny/base  → 快但中文差；small/medium → 中文可用；large-v3 → 质量最好但慢
    建议默认 small，中文会议用 medium 更稳

输出：<同名>.transcript.md，格式：
    == 00:00:00 == 转写文本行
"""
import argparse
import os
import sys
import io
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

AUDIO_EXTS = (".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg")
VIDEO_EXTS = (".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv")


def find_ffmpeg():
    for cand in [os.environ.get("FFMPEG_PATH"), os.environ.get("IMAGEIO_FFMPEG_EXE"),
                 "ffmpeg"]:
        if cand:
            try:
                subprocess.run([cand, "-version"], capture_output=True, check=True)
                return cand
            except Exception:
                continue
    return None


def extract_audio_ffmpeg(src, ffmpeg, out_wav):
    subprocess.run([ffmpeg, "-y", "-i", src, "-ar", "16000", "-ac", "1",
                    out_wav], capture_output=True, check=True)


def transcribe(src, model_size, out_dir):
    if src.lower().endswith(AUDIO_EXTS):
        audio_path = src
    elif src.lower().endswith(VIDEO_EXTS):
        ffmpeg = find_ffmpeg()
        if not ffmpeg:
            return "[ERROR] 未找到 ffmpeg，请安装或设置 IMAGEIO_FFMPEG_EXE"
        wav = os.path.join(os.path.dirname(os.path.abspath(src)),
                           "_ray_mm_audio.wav")
        print(f"抽音轨: {wav}")
        try:
            extract_audio_ffmpeg(src, ffmpeg, wav)
        except subprocess.CalledProcessError as e:
            return f"[ERROR] ffmpeg 抽音轨失败: {e}"
        audio_path = wav
    else:
        return "[ERROR] 不支持的媒体格式: " + src

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return ("[ERROR] 缺少 faster-whisper: pip install faster-whisper。"
                "（首次会下载模型，中文建议 model=medium）")

    print(f"转写中（model={model_size}）……")
    model = WhisperModel(model_size, device="auto", compute_type="int8")
    segments, info = model.transcribe(audio_path, language="zh",
                                      vad_filter=True)

    base = os.path.splitext(os.path.basename(src))[0]
    out_dir = out_dir or os.path.dirname(os.path.abspath(src))
    out_path = os.path.join(out_dir, base + ".transcript.md")
    lines = [f"# {os.path.basename(src)} 转写文本",
             f"\n> 来源: {src}（whisper {model_size}，语言: zh）\n"]
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        for seg in segments:
            ts = seg.start
            h, m, s = int(ts // 3600), int(ts % 3600 // 60), int(ts % 60)
            f.write(f"\n== {h:02d}:{m:02d}:{s:02d} == {seg.text.strip()}")

    if audio_path != src and os.path.exists(audio_path):
        os.remove(audio_path)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="音频或视频文件")
    ap.add_argument("--model", default="small", help="whisper 模型: tiny/base/small/medium/large-v3")
    ap.add_argument("--out", default=None, help="输出目录（默认与源同目录）")
    args = ap.parse_args()

    if not os.path.exists(args.src):
        print(f"[ERROR] 文件不存在: {args.src}")
        sys.exit(1)

    try:
        out = transcribe(args.src, args.model, args.out)
        print("OK  -> " + str(out))
    except Exception as e:
        print(f"[ERROR] 转写失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()