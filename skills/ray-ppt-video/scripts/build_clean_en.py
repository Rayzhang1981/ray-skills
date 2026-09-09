# -*- coding: utf-8 -*-
"""
Clean rebuild: slides + mp3 -> concatenated NO-SUBTITLE master mp4.
From pristine sources only (slide PNG + TTS audio), so we can burn subs
exactly once without ever stacking subtitle layers.
Usage: build_clean.py narration.json slides/ audio/ out_no_subs.mp4
"""
import json, os, re, shutil, subprocess, sys, tempfile

FFMPEG = os.environ.get("IMAGEIO_FFMPEG_EXE") or shutil.which("ffmpeg") or r"C:\ffmpeg\bin\ffmpeg.exe"


def get_duration(path):
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+)\.(\d+)", out)
    if m:
        return int(m.group(1))*3600+int(m.group(2))*60+int(m.group(3))+int(m.group(4))/100
    return 5.0


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, errors="replace")
    if r.returncode != 0:
        print("[ERR]", " ".join(cmd[:5]), "...", (r.stderr or "")[-400:], file=sys.stderr)
        sys.exit(1)
    return r


def main():
    narration_json, slides_dir, audio_dir, out = sys.argv[1:5]
    with open(narration_json, encoding="utf-8") as f:
        narrations = json.load(f)
    tmp = tempfile.mkdtemp(prefix="cleanbuild_")
    clips = []
    for item in narrations:
        slide = item["slide"]
        img = os.path.join(slides_dir, f"slide_{slide:02d}.png")
        mp3 = os.path.join(audio_dir, f"slide_{slide:02d}.mp3")
        if not (os.path.exists(img) and os.path.exists(mp3)):
            print(f"[skip] slide {slide} missing", file=sys.stderr)
            continue
        dur = get_duration(mp3)
        clip = os.path.join(tmp, f"clip_{slide:02d}.mp4")
        run([FFMPEG, "-y", "-loop", "1", "-i", img, "-i", mp3,
             "-t", f"{dur:.3f}", "-r", "24",
             "-c:v", "libx264", "-preset", "medium", "-crf", "21",
             "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
             "-pix_fmt", "yuv420p", "-shortest", clip])
        clips.append(clip)
        print(f"[clip] slide {slide:02d} ({dur:.1f}s)")
    concat_txt = os.path.join(tmp, "concat.txt")
    with open(concat_txt, "w", encoding="utf-8") as f:
        for c in clips:
            f.write(f"file '{c}'\n")
    run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
         "-c", "copy", out])
    print("[ok] clean no-subs ->", out)
    for c in clips:
        os.remove(c)
    os.remove(concat_txt)
    os.rmdir(tmp)


if __name__ == "__main__":
    main()
