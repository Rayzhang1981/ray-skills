"""
ray-PPT-TrVideo — Step 4/5: Generate SRT subtitles from narration JSON + audio durations.
Usage: python generate_srt.py narration.json audio/ output.srt [--ffmpeg PATH]

v2.1: 字幕按语义分段显示，匹配语速，避免遮挡
"""
import json
import os
import re
import subprocess
import sys
import argparse


def get_ffmpeg_path(custom_path=None):
    if custom_path:
        return custom_path
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


def get_duration(ffmpeg: str, mp3_path: str) -> float:
    """Get audio duration via ffprobe/ffmpeg."""
    result = subprocess.run(
        [ffmpeg, "-i", mp3_path],
        capture_output=True, text=True, errors="replace"
    )
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", result.stderr)
    if m:
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    return 5.0  # fallback


def secs_to_srt(secs: float) -> str:
    ms = int((secs % 1) * 1000)
    s = int(secs) % 60
    m = int(secs // 60) % 60
    h = int(secs // 3600)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def split_text_semantic(text: str, max_len: int = 38) -> list:
    """按语义拆分长文本为适合字幕显示的短句列表。

    策略：
    1. 先按句号、问号、感叹号拆分成句子
    2. 长句再按分号、逗号拆分
    3. 确保每个片段不超过 max_len 字符
    """
    # 第一步：按句子结束符拆分
    sentences = re.split(r'([。！？;；])', text)
    # 重组：把分隔符加回前一句
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

    # 第二步：长句按逗号、顿号进一步拆分
    result = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) <= max_len:
            result.append(part)
            continue

        # 按逗号、顿号拆分
        sub_parts = re.split(r'([,，、])', part)
        # 重组
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

        # 合并短片段，确保每段不超过 max_len
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

    # 最后检查：如果还有超长片段，强制截断
    final = []
    for r in result:
        while len(r) > max_len:
            # 在 max_len 处找最近的标点
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


def format_subtitle_text(seg: str, max_line: int = 34) -> str:
    """将字幕片段格式化为SRT显示文本，控制每行长度，最多2行。"""
    if len(seg) <= max_line:
        return seg
    # 尝试在 max_line 处按标点拆分
    lines = []
    words = seg
    while len(words) > max_line:
        cut = max_line
        for k in range(max_line, max_line // 2, -1):
            if words[k] in '，,、;；':
                cut = k + 1
                break
        lines.append(words[:cut])
        words = words[cut:]
    if words:
        lines.append(words)
    return "\n".join(lines[:2])


def main():
    parser = argparse.ArgumentParser(description="Generate SRT subtitles")
    parser.add_argument("narration_json", help="Path to narration.json")
    parser.add_argument("audio_dir", help="Directory containing MP3 files")
    parser.add_argument("output_srt", help="Output SRT file path")
    parser.add_argument("--ffmpeg", help="Path to ffmpeg binary")
    args = parser.parse_args()

    ffmpeg = get_ffmpeg_path(args.ffmpeg)

    with open(args.narration_json, encoding="utf-8") as f:
        narrations = json.load(f)

    lines = []
    cumulative = 0.0
    sub_idx = 1

    for item in narrations:
        slide = item["slide"]
        text = item["text"]
        mp3_path = os.path.join(args.audio_dir, f"slide_{slide:02d}.mp3")

        duration = get_duration(ffmpeg, mp3_path) if os.path.exists(mp3_path) else max(len(text) / 5.0, 3.0)

        # 按语义拆分
        segments = split_text_semantic(text, max_len=38)

        # 按字数比例分配时间
        total_chars = sum(len(s) for s in segments)
        if total_chars == 0:
            total_chars = 1

        seg_start = cumulative
        for seg in segments:
            seg_ratio = len(seg) / total_chars
            seg_dur = duration * seg_ratio
            seg_dur = max(seg_dur, 1.5)  # 每段至少显示1.5秒
            seg_end = seg_start + seg_dur

            display_seg = format_subtitle_text(seg, max_line=34)

            lines.append(str(sub_idx))
            lines.append(f"{secs_to_srt(seg_start)} --> {secs_to_srt(seg_end)}")
            lines.append(display_seg)
            lines.append("")

            sub_idx += 1
            seg_start = seg_end

        cumulative = seg_start
        print(f"Slide {slide:02d}: {len(segments)} segments, total {duration:.1f}s")

    with open(args.output_srt, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\nSRT → {args.output_srt}")
    print(f"Total: {cumulative:.0f}s ({cumulative/60:.1f} min), {sub_idx - 1} subtitle segments")


if __name__ == "__main__":
    main()
