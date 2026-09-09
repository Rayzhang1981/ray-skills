"""
ray-PPT-TrVideo — Step 5/6: Assemble MP4 from slides + audio + subtitles.
Supports: hard-burned subtitles (SRT/ASS), soft subtitles (mov_text), FFmpeg filter detection.

Usage:
  python assemble_video.py narration.json slides/ audio/ subtitles.srt output.mp4
  python assemble_video.py ... --subtitle-mode soft
  python assemble_video.py ... --subtitle-mode both --font-name "Microsoft YaHei"
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile


# ────────────────────────────────────────────────
# FFmpeg
# ────────────────────────────────────────────────

def get_ffmpeg_path(custom=None):
    if custom:
        return custom
    # Try system PATH first
    ff = shutil.which("ffmpeg")
    if ff:
        return ff
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def ffmpeg_has_filter(ffmpeg: str, name: str) -> bool:
    """Check if FFmpeg supports a named filter."""
    try:
        r = subprocess.run([ffmpeg, "-filters"], capture_output=True, text=True)
        for line in r.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 2 and name in parts:
                return True
        return False
    except Exception:
        return False


def get_duration(ffmpeg: str, path: str) -> float:
    r = subprocess.run([ffmpeg, "-i", path], capture_output=True,
                       text=True, errors="replace")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", r.stderr)
    if m:
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    return 5.0


def get_video_info(ffmpeg: str, path: str) -> dict:
    try:
        r = subprocess.run(
            [ffmpeg.replace("ffmpeg", "ffprobe") if "ffprobe" not in ffmpeg
             else ffmpeg.replace("ffmpeg", "ffprobe"),
             "-v", "error", "-show_entries",
             "format=duration,size:stream=width,height,r_frame_rate,codec_name",
             "-of", "json", path],
            capture_output=True, text=True
        )
        if r.returncode == 0:
            return json.loads(r.stdout)
    except Exception:
        pass
    return {}


# ────────────────────────────────────────────────
# Clip generation
# ────────────────────────────────────────────────

def make_clip(ffmpeg: str, slide_num: int, img_path: str, audio_path: str,
              duration: float, tmp_dir: str) -> str:
    """Create a single slide MP4 clip."""
    clip_path = os.path.join(tmp_dir, f"clip_{slide_num:02d}.mp4")

    if not os.path.exists(img_path):
        print(f"  [WARN] Missing slide image: {img_path}")
        return None

    vf = ("scale=1920:1080:force_original_aspect_ratio=decrease,"
          "pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p")

    if os.path.exists(audio_path):
        cmd = [
            ffmpeg, "-y", "-loop", "1", "-i", img_path, "-i", audio_path,
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-pix_fmt", "yuv420p", "-r", "24",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-t", str(duration), "-shortest",
            clip_path
        ]
    else:
        cmd = [
            ffmpeg, "-y", "-loop", "1", "-i", img_path,
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast", "-crf", "22",
            "-pix_fmt", "yuv420p", "-r", "24",
            "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
            "-t", str(duration), "-shortest",
            clip_path
        ]

    result = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if result.returncode != 0:
        print(f"  [ERROR] slide {slide_num}: {result.stderr[-300:]}")
        return None

    print(f"  [ok] clip {slide_num:02d} ({duration:.1f}s)")
    return clip_path


# ────────────────────────────────────────────────
# Subtitle generation
# ────────────────────────────────────────────────

def secs_to_srt(secs: float) -> str:
    ms = int((secs % 1) * 1000)
    s = int(secs) % 60
    m = int(secs // 60) % 60
    h = int(secs // 3600)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def secs_to_ass(secs: float) -> str:
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = int(secs % 60)
    c = int((secs % 1) * 100)
    return f"{h}:{m:02d}:{s:02d}.{c:02d}"


def split_text_semantic(text: str, max_len: int = 38) -> list:
    """按语义拆分长文本为适合字幕显示的短句列表。"""
    sentences = re.split(r'([。！？;；])', text)
    parts = []
    i = 0
    while i < len(sentences):
        if i + 1 < len(sentences) and sentences[i + 1] in '。！？;；':
            parts.append(sentences[i] + sentences[i + 1])
            i += 2
        else:
            if sentences[i].strip():
                parts.append(sentences[i])
            i += 1

    result = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) <= max_len:
            result.append(part)
            continue

        sub_parts = re.split(r'([,，、])', part)
        sub_sentences = []
        j = 0
        while j < len(sub_parts):
            if j + 1 < len(sub_parts) and sub_parts[j + 1] in ',，、':
                sub_sentences.append(sub_parts[j] + sub_parts[j + 1])
                j += 2
            else:
                if sub_parts[j].strip():
                    sub_sentences.append(sub_parts[j])
                j += 1

        current = ""
        for sp in sub_sentences:
            sp = sp.strip()
            if not sp:
                continue
            if len(current) + len(sp) <= max_len:
                current += sp
            else:
                if current:
                    result.append(current)
                current = sp
        if current:
            result.append(current)

    final = []
    for r in result:
        while len(r) > max_len:
            cut = max_len
            for k in range(max_len - 1, max_len // 2, -1):
                if r[k] in '，,、;；':
                    cut = k + 1
                    break
            final.append(r[:cut])
            r = r[cut:]
        if r.strip():
            final.append(r.strip())
    return final if final else [text]


def generate_srt(narrations: list, audio_dir: str, ffmpeg: str, output_path: str):
    """Generate SRT subtitle file with semantic splitting."""
    lines = []
    idx = 1
    cumulative = 0.0

    for item in narrations:
        slide = item["slide"]
        text = item["text"]
        mp3 = os.path.join(audio_dir, f"slide_{slide:02d}.mp3")
        dur = (get_duration(ffmpeg, mp3) if os.path.exists(mp3)
               else max(len(text) / 5.0, 3.0))

        segments = split_text_semantic(text, max_len=38)
        total_chars = sum(len(s) for s in segments)
        if total_chars == 0:
            total_chars = 1

        seg_start = cumulative
        for seg in segments:
            seg_ratio = len(seg) / total_chars
            seg_dur = dur * seg_ratio
            seg_dur = max(seg_dur, 1.5)
            seg_end = seg_start + seg_dur

            display_seg = seg
            if len(seg) > 34:
                display_lines = []
                words = seg
                while len(words) > 34:
                    cut = 34
                    for k in range(34, 17, -1):
                        if words[k] in '，,、;；':
                            cut = k + 1
                            break
                    display_lines.append(words[:cut])
                    words = words[cut:]
                if words:
                    display_lines.append(words)
                display_seg = "\n".join(display_lines[:2])

            lines.append(str(idx))
            lines.append(f"{secs_to_srt(seg_start)} --> {secs_to_srt(seg_end)}")
            lines.append(display_seg)
            lines.append("")
            idx += 1
            seg_start = seg_end

        cumulative = seg_start

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[SRT] Generated: {output_path}")
    lines = []
    idx = 1

    for item in narrations:
        slide = item["slide"]
        text = item["text"]
        mp3 = os.path.join(audio_dir, f"slide_{slide:02d}.mp3")

        # Duration from audio or estimate
        if os.path.exists(mp3):
            start = 0
            dur = get_duration(ffmpeg, mp3)
        else:
            dur = max(len(text) / 5.0, 3.0)

        start_t = idx - 1  # simplified: use index as time marker
        # Actually compute from previous slides' audio
        # (simplified for now — in real use, durations accumulate)

        # Split long text to ≤40 chars, max 2 lines
        segs = []
        remaining = text
        while len(remaining) > 40:
            segs.append(remaining[:40])
            remaining = remaining[40:]
        if remaining:
            segs.append(remaining)
        sub_text = "\n".join(segs[:2])

        total_dur = sum(
            get_duration(ffmpeg, os.path.join(audio_dir, f"slide_{s['slide']:02d}.mp3"))
            if os.path.exists(os.path.join(audio_dir, f"slide_{s['slide']:02d}.mp3"))
            else max(len(s['text']) / 5.0, 3.0)
            for s in narrations[:idx]
        )
        prev_end = total_dur - dur
        end_time = total_dur

        lines.append(str(idx))
        lines.append(f"{secs_to_srt(prev_end)} --> {secs_to_srt(end_time)}")
        lines.append(sub_text)
        lines.append("")
        print(f"  SRT {idx:02d}: {secs_to_srt(prev_end)} → {secs_to_srt(end_time)} | {text[:40]}...")
        idx += 1

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[SRT] Generated: {output_path}")


def generate_ass(narrations: list, audio_dir: str, ffmpeg: str, output_path: str,
                 font_name="Microsoft YaHei", font_size=32,
                 resolution="1920x1080"):
    """Generate ASS subtitle file with rich styling."""
    width, height = resolution.split("x")

    header = f"""[Script Info]
Title: PPT Training Video Subtitles
ScriptType: v4.00+
WrapStyle: 0
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{font_name},{font_size},&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,2,1,2,30,30,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    events = []
    idx = 1
    cumulative = 0.0

    for item in narrations:
        slide = item["slide"]
        text = item["text"]
        mp3 = os.path.join(audio_dir, f"slide_{slide:02d}.mp3")
        dur = (get_duration(ffmpeg, mp3) if os.path.exists(mp3)
               else max(len(text) / 5.0, 3.0))

        segments = split_text_semantic(text, max_len=38)
        total_chars = sum(len(s) for s in segments)
        if total_chars == 0:
            total_chars = 1

        seg_start = cumulative
        for seg in segments:
            seg_ratio = len(seg) / total_chars
            seg_dur = dur * seg_ratio
            seg_dur = max(seg_dur, 1.5)
            seg_end = seg_start + seg_dur

            text_escaped = seg.replace("\n", "\\N")
            events.append(
                f"Dialogue: 0,{secs_to_ass(seg_start)},{secs_to_ass(seg_end)},"
                f"Default,,0,0,0,,{text_escaped}"
            )
            seg_start = seg_end

        cumulative = seg_start

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(header)
        f.write("\n".join(events))
        f.write("\n")
    print(f"[ASS] Generated: {output_path}")


# ────────────────────────────────────────────────
# Video assembly
# ────────────────────────────────────────────────

def burn_subtitles(ffmpeg: str, video_path: str, sub_path: str,
                   output_path: str, sub_format="ass") -> bool:
    """Burn (hardcode) subtitles into video. Returns True on success."""
    # subtitles filter supports both SRT and ASS. Use forward slashes and escape colons.
    escaped = os.path.abspath(sub_path).replace("\\", "/").replace(":", "\\:")
    if sub_format == "ass":
        vf = f"subtitles='{escaped}'"
    else:
        vf = (f"subtitles='{escaped}':"
              f"force_style='FontSize=14,PrimaryColour=&HFFFFFF,"
              f"OutlineColour=&H000000,BackColour=&H80000000,"
              f"Bold=-1,Outline=2,Shadow=1,Alignment=2,MarginV=60'")

    cmd = [
        ffmpeg, "-y",
        "-i", os.path.abspath(video_path),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "medium", "-crf", "21",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-map", "0:v", "-map", "0:a",
        "-movflags", "+faststart",
        os.path.abspath(output_path)
    ]

    print(f"  Burning subtitles ({sub_format})...")
    result = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if result.returncode != 0:
        err = result.stderr.strip()
        if not err and result.stdout:
            err = result.stdout.strip()
        if not err:
            err = f"exit code {result.returncode} (no output)"
        print(f"  [WARN] Failed: {err[:500]}")
        return False
    print(f"  [ok] Subtitles burned: {output_path}")
    return True


def add_soft_subtitles(ffmpeg: str, video_path: str, sub_path: str,
                       output_path: str) -> str:
    """Add subtitles as separate track (soft subs)."""
    cmd = [
        ffmpeg, "-y",
        "-i", os.path.abspath(video_path),
        "-i", os.path.abspath(sub_path),
        "-c:v", "copy", "-c:a", "copy",
        "-c:s", "mov_text",
        "-metadata:s:s:0", "language=chi",
        os.path.abspath(output_path)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        print(f"  [WARN] Soft subtitle failed: {r.stderr[:200]}")
        return None
    print(f"  [ok] Soft subtitles added: {output_path}")
    return output_path


# ────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Assemble training video from slides + audio")
    parser.add_argument("narration_json", help="Path to narration.json")
    parser.add_argument("slides_dir", help="Directory containing slide PNGs")
    parser.add_argument("audio_dir", help="Directory containing MP3 files")
    parser.add_argument("srt_file", help="Path to subtitles.srt")
    parser.add_argument("output_mp4", help="Output MP4 file path")
    parser.add_argument("--ffmpeg", help="Path to ffmpeg binary")
    parser.add_argument("--keep-clips", action="store_true",
                        help="Keep temp clips")
    parser.add_argument("--subtitle-mode", choices=["burn", "soft", "both"],
                        default="burn", help="Subtitle mode (default: burn)")
    parser.add_argument("--font-name", default="Microsoft YaHei",
                        help="Subtitle font (default: Microsoft YaHei)")
    parser.add_argument("--font-size", type=int, default=32,
                        help="Subtitle font size (default: 32)")
    args = parser.parse_args()

    ffmpeg = get_ffmpeg_path(args.ffmpeg)

    # Load narration data
    with open(args.narration_json, encoding="utf-8") as f:
        narrations = json.load(f)

    output_dir = os.path.dirname(os.path.abspath(args.output_mp4))
    os.makedirs(output_dir, exist_ok=True)

    # Check subtitle capabilities
    has_ass = ffmpeg_has_filter(ffmpeg, "ass")
    has_srt_sub = ffmpeg_has_filter(ffmpeg, "subtitles")
    can_burn = has_ass or has_srt_sub

    print(f"[FFmpeg] ASS filter: {has_ass}, SRT/subtitles filter: {has_srt_sub}")

    actual_mode = args.subtitle_mode
    if args.subtitle_mode == "burn" and not can_burn:
        print("[FFmpeg] 未编译 libass，硬字幕不可用，回退到软字幕模式")
        actual_mode = "soft"
    elif args.subtitle_mode == "both" and not can_burn:
        actual_mode = "soft"

    tmp_dir = tempfile.mkdtemp(prefix="trvideo_")
    print(f"Temp: {tmp_dir}")

    # ── Generate subtitles ──
    ass_path = os.path.join(output_dir, "subtitles.ass")
    generate_ass(narrations, args.audio_dir, ffmpeg, ass_path,
                 font_name=args.font_name, font_size=args.font_size)

    # Copy ASS to tmp_dir for safe path (avoid colons/special chars in filter paths)
    ass_tmp = os.path.join(tmp_dir, "subtitles.ass")
    shutil.copy(ass_path, ass_tmp)

    # Re-generate SRT with proper timing (reuse existing or create fresh)
    srt_safe = os.path.join(tmp_dir, "subtitles.srt")
    # Copy the input SRT if it exists, otherwise generate fresh
    if os.path.isfile(args.srt_file):
        shutil.copy(args.srt_file, srt_safe)
    else:
        generate_srt(narrations, args.audio_dir, ffmpeg, srt_safe)

    # ── Step 1: Build per-slide clips ──
    print(f"\n=== Building {len(narrations)} slide clips (44100Hz stereo) ===")
    clip_paths = []
    for item in narrations:
        slide = item["slide"]
        img = os.path.join(args.slides_dir, f"slide_{slide:02d}.png")
        audio = os.path.join(args.audio_dir, f"slide_{slide:02d}.mp3")
        dur = (get_duration(ffmpeg, audio) if os.path.exists(audio)
               else max(len(item["text"]) / 5.0, 3.0))
        clip = make_clip(ffmpeg, slide, img, audio, dur, tmp_dir)
        if clip:
            clip_paths.append(clip)

    if not clip_paths:
        print("[ERROR] No clips generated!")
        return 1

    # ── Step 2: Concat clips ──
    print(f"\n=== Concatenating {len(clip_paths)} clips ===")
    concat_txt = os.path.join(tmp_dir, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for cp in clip_paths:
            f.write(f"file '{cp}'\n")

    merged_no_subs = os.path.join(tmp_dir, "merged_no_subs.mp4")
    concat_cmd = [
        ffmpeg, "-y", "-f", "concat", "-safe", "0",
        "-i", concat_txt,
        "-c:v", "libx264", "-preset", "medium", "-crf", "21",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        "-map", "0:v", "-map", "0:a",
        merged_no_subs
    ]
    subprocess.run(concat_cmd, capture_output=True, check=True)
    print("  [ok] Clips concatenated")

    # ── Step 3: Apply subtitles ──
    if actual_mode in ("burn", "both"):
        print(f"\n=== Burning subtitles ({actual_mode}) ===")
        success = False

        if has_ass:
            success = burn_subtitles(
                ffmpeg, merged_no_subs, ass_tmp,
                args.output_mp4, sub_format="ass"
            )
        if not success and has_srt_sub:
            success = burn_subtitles(
                ffmpeg, merged_no_subs, srt_safe,
                args.output_mp4, sub_format="srt"
            )

        if not success:
            print("[WARN] 硬字幕烧录失败，回退为软字幕")
            actual_mode = "soft"
            # Copy merged to output, then add soft subs
            shutil.copy(merged_no_subs, args.output_mp4)

        if actual_mode == "both":
            soft_out = args.output_mp4.replace(".mp4", "_softsub.mp4")
            add_soft_subtitles(ffmpeg, merged_no_subs, srt_safe, soft_out)

    if actual_mode == "soft":
        print(f"\n=== Adding soft subtitles ===")
        # Copy merged without subs first
        if not os.path.exists(args.output_mp4):
            shutil.copy(merged_no_subs, args.output_mp4)
        add_soft_subtitles(ffmpeg, args.output_mp4, srt_safe,
                           args.output_mp4)

    # ── Summary ──
    info = get_video_info(ffmpeg, args.output_mp4)
    size_mb = os.path.getsize(args.output_mp4) / (1024 * 1024)

    print(f"\n{'='*50}")
    print(f"  Output:   {args.output_mp4}")
    print(f"  Size:     {size_mb:.1f} MB")
    print(f"  Slides:   {len(narrations)}")
    print(f"  Subtitles: {actual_mode}")
    print(f"  SRT:      {srt_safe}")
    print(f"  ASS:      {ass_path}")
    print(f"{'='*50}")

    # Cleanup
    if not args.keep_clips:
        print("Cleaning temp files...")
        for f in glob.glob(os.path.join(tmp_dir, "*")):
            try:
                os.remove(f)
            except OSError:
                pass
        try:
            os.rmdir(tmp_dir)
        except OSError:
            pass

    print("Done!")
    return 0


if __name__ == "__main__":
    exit(main())
