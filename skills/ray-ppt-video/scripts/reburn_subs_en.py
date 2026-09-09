# -*- coding: utf-8 -*-
"""
Re-burn subtitles onto an EXISTING mp4 (no re-TTS needed).
Keeps original audio stream, re-encodes video with new hard subs.
Usage: reburn_subs.py <input.mp4> <subs.srt> <output.mp4> [font]
"""
import os, shutil, subprocess, sys

FFMPEG = os.environ.get("IMAGEIO_FFMPEG_EXE") or shutil.which("ffmpeg") or r"C:\ffmpeg\bin\ffmpeg.exe"


def main():
    src, sub, out = sys.argv[1], sys.argv[2], sys.argv[3]
    # sub can be .srt (force_style) or .ass (styles in file - RELIABLE bottom position)
    if sub.lower().endswith(".ass"):
        sub_esc = sub.replace("\\", "/").replace(":", "\\:")
        vf = f"ass={sub_esc}"
    else:
        font = sys.argv[4] if len(sys.argv) > 4 else "Arial"
        sub_esc = sub.replace("\\", "/").replace(":", "\\:")
        vf = (f"subtitles='{sub_esc}':force_style='"
              f"FontName={font},FontSize=17,PrimaryColour=&H00FFFFFF,"
              f"OutlineColour=&H00000000,BackColour=&HCC000000,"
              f"BorderStyle=4,Outline=0,Shadow=0,"
              f"Alignment=2,MarginV=24'")
    cmd = [FFMPEG, "-y", "-i", src, "-vf", vf,
           "-c:v", "libx264", "-preset", "medium", "-crf", "21",
           "-c:a", "copy", "-movflags", "+faststart", out]
    print("running:", " ".join(cmd[:6]), "...")
    r = subprocess.run(cmd, capture_output=True, errors="replace")
    if r.returncode != 0:
        print("ERR", (r.stderr or "")[-600:], file=sys.stderr)
        sys.exit(1)
    print("OK ->", out)


if __name__ == "__main__":
    main()
