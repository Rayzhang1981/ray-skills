# -*- coding: utf-8 -*-
"""
Accurate subtitle generator for ray-ppt-video (EN).
Calls edge-tts live, captures SentenceBoundary offsets => SRT aligned to speech.
Also (optionally) re-saves mp3 with the same call.
"""
import asyncio, edge_tts, json, os, re, sys

VOICE = "en-US-GuyNeural"   # override with --voice
RATE = "-15%"               # natural narration pace (~127 wpm); override with --rate
SENT_SPLIT = True  # subtitle per sentence (accurate); fallback to clause if too long


def secs(x):
    """100ns -> srt timestamp"""
    s = x / 1e7
    ms = int(round((s % 1) * 1000))
    s = int(s)
    if ms >= 1000:
        ms = 0
        s += 1
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{sec:02d},{ms:03d}"


def split_long_sentence(sent: str, max_chars: int = 60) -> list:
    """If a SentenceBoundary is too long for one subtitle line, split at commas
    but keep the SAME sentence-level time span (assign proportional spans)."""
    if len(sent) <= max_chars:
        return [sent]
    chunks = re.split(r"([,;:])", sent)
    units = []
    i = 0
    while i < len(chunks):
        if i + 1 < len(chunks) and chunks[i + 1] in ",;:":
            units.append(chunks[i] + chunks[i + 1])
            i += 2
        else:
            if chunks[i].strip():
                units.append(chunks[i])
            i += 1
    merged, cur = [], ""
    for u in units:
        u = u.strip()
        if not u:
            continue
        if len(cur) + len(u) <= max_chars:
            cur = (cur + " " if cur else "") + u
        else:
            if cur:
                merged.append(cur)
            cur = u
    if cur:
        merged.append(cur)
    return merged or [sent]


def fmt_lines(seg: str, max_line: int = 42) -> str:
    if len(seg) <= max_line:
        return seg
    cut = seg.rfind(" ", 0, max_line)
    if cut <= 0:
        cut = max_line
    return seg[:cut] + "\n" + seg[cut:].strip()


async def gen_slide(idx: int, text: str, out_mp3: str, write_audio: bool = True, rate: str = RATE):
    """Return list of (start_s, end_s, display_text) aligned to real speech."""
    tts = edge_tts.Communicate(text, VOICE, rate=rate)
    sents = []          # (offset_ns, duration_ns, text)
    audio_parts = []
    async for chunk in tts.stream():
        if chunk["type"] == "audio":
            audio_parts.append(chunk["data"])
        elif chunk["type"] == "SentenceBoundary":
            sents.append((chunk["offset"], chunk["duration"], chunk["text"].strip()))
    if write_audio and audio_parts:
        with open(out_mp3, "wb") as f:
            for p in audio_parts:
                f.write(p)
    subs = []
    for off, dur, stext in sents:
        start = off / 1e7
        end = (off + dur) / 1e7
        # if sentence longer than ~58 chars, split on commas with proportional time
        segs = split_long_sentence(stext, 58)
        total_chars = max(sum(len(s) for s in segs), 1)
        t = start
        span = (end - start)
        for seg in segs:
            d = span * (len(seg) / total_chars)
            subs.append((t, t + d, fmt_lines(seg)))
            t += d
        # clamp last sub to the sentence end (never beyond)
        if subs:
            last = subs[-1]
            if last[1] > end + 0.001:
                subs[-1] = (last[0], max(last[0] + 0.2, end), last[2])
    return subs


async def main():
    import argparse
    global VOICE
    ap = argparse.ArgumentParser(description="edge-tts TTS + sentence-accurate SRT (EN)")
    ap.add_argument("narration_json")
    ap.add_argument("audio_dir")
    ap.add_argument("out_srt")
    ap.add_argument("--srt-only", action="store_true", help="skip writing mp3")
    ap.add_argument("--rate", default=RATE, help="edge-tts rate, e.g. -15% / +0%")
    ap.add_argument("--voice", default=VOICE, help="edge-tts voice (default en-US-GuyNeural)")
    args = ap.parse_args()
    VOICE = args.voice
    rate = args.rate
    narration_json, audio_dir, out_srt = args.narration_json, args.audio_dir, args.out_srt
    srt_only = args.srt_only
    if not srt_only:
        os.makedirs(audio_dir, exist_ok=True)
    with open(narration_json, encoding="utf-8") as f:
        narrations = json.load(f)
    all_subs = []
    cumulative = 0.0  # video timeline offset (sum of audio durations)
    sub_idx = 1
    for item in narrations:
        slide = item["slide"]
        text = item["text"]
        mp3 = os.path.join(audio_dir, f"slide_{slide:02d}.mp3")
        subs = await gen_slide(slide, text, mp3, write_audio=not srt_only, rate=rate)
        # per-slide monotonic clamp (slide-internal overlaps only)
        prev_end = 0.0
        clamped = []
        for s, e, disp in subs:
            if s < prev_end:
                s = prev_end
            if e <= s:
                e = s + 0.3
            clamped.append((s, e, disp))
            prev_end = e
        subs = clamped
        for s, e, disp in subs:
            all_subs.append((cumulative + s, cumulative + e, disp))
        # advance by audio length = last sentence end (or estimate)
        slide_len = subs[-1][1] if subs else max(len(text) / 15.0, 3.0)
        cumulative += slide_len
        print(f"slide {slide:02d}: {len(subs)} subs, slide dur {slide_len:.2f}s")

    with open(out_srt, "w", encoding="utf-8") as f:
        for s, e, disp in all_subs:
            f.write(f"{sub_idx}\n{secs(int(s*1e7))} --> {secs(int(e*1e7))}\n{disp}\n\n")
            sub_idx += 1
    print(f"SRT -> {out_srt}; total {cumulative:.1f}s ({cumulative/60:.1f} min), {sub_idx-1} subs")


if __name__ == "__main__":
    asyncio.run(main())
