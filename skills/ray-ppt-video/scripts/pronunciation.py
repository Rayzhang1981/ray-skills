#!/usr/bin/env python3
"""
ray-PPT-TrVideo — Pronunciation normalization module.
Provides path normalization and term pronunciation mapping for TTS quality.

Usage:
    from pronunciation import normalize_pronunciation
    tts_text = normalize_pronunciation("HAZOP 分析在 ~/.codebuddy/skills/ 目录")
    # → "哈扎普 分析在 家目录下 codebuddy skills 目录"
"""

import json
import os
import re

_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
PRONUNCIATION_CONFIG = os.path.join(
    os.path.dirname(_CONFIG_DIR), "config", "pronunciation_map.json"
)

# Cache
_PRONUNCIATION_RULES = None


def _load_rules() -> list:
    """Load pronunciation rules from config JSON."""
    global _PRONUNCIATION_RULES
    if _PRONUNCIATION_RULES is not None:
        return _PRONUNCIATION_RULES

    if not os.path.isfile(PRONUNCIATION_CONFIG):
        _PRONUNCIATION_RULES = []
        return []

    try:
        with open(PRONUNCIATION_CONFIG, "r", encoding="utf-8") as f:
            data = json.load(f)
        rules = []
        for entry in data.get("rules", []):
            pat = entry.get("pattern", "")
            rep = entry.get("replacement", "")
            if not pat:
                continue
            # Wrap with word boundaries (unless pattern contains dot)
            if "\\." in pat:
                rules.append((rf'\b{pat}(?!\w)', rep))
            else:
                rules.append((rf'\b{pat}\b', rep))
        _PRONUNCIATION_RULES = rules
        return rules
    except Exception:
        _PRONUNCIATION_RULES = []
        return []


def _normalize_paths(text: str) -> str:
    """
    Convert file/directory paths to TTS-friendly spoken form.

    Rules:
      ~/  → "家目录下"
      ./  → "当前目录下"
      .hidden_dir/ → "hidden_dir 目录" (strip leading dot)
      trailing / → "目录"
      file.ext → "file点ext"
    """
    _PATH_CHARS = set(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_.-'
    )

    result = []
    i = 0
    n = len(text)

    while i < n:
        start = i
        prefix = ''

        # Check ~/ or ./ prefix
        if text[i] == '~' and i + 1 < n and text[i + 1] == '/':
            prefix = '~/'
            i += 2
        elif (text[i] == '.' and i + 1 < n and text[i + 1] == '/' and
              (start == 0 or not text[start - 1].isalnum())):
            prefix = './'
            i += 2

        # Read path segments
        segments = []
        seg_start = i
        found_slash = False

        while i < n and (text[i] in _PATH_CHARS or text[i] == '/'):
            if text[i] == '/':
                seg = text[seg_start:i]
                if seg:
                    segments.append(seg)
                found_slash = True
                i += 1
                seg_start = i
            else:
                i += 1

        trailing_seg = text[seg_start:i]
        is_dir = (not trailing_seg and found_slash)
        if trailing_seg:
            segments.append(trailing_seg)

        # Not a path
        if not found_slash and not prefix:
            result.append(text[start:i] if i > start else text[start])
            if i == start:
                i += 1
            continue

        if not segments and not prefix:
            result.append(text[start:i])
            continue

        # Not preceded by word char
        if not prefix and start > 0 and (text[start - 1].isalnum() or text[start - 1] == '_'):
            result.append(text[start:i])
            continue

        # Build spoken form
        parts = []
        if prefix == '~/':
            parts.append('家目录下')
        elif prefix == './':
            parts.append('当前目录下')

        for idx, seg in enumerate(segments):
            clean = seg.lstrip('.')
            if not clean:
                continue
            # File extension for last segment
            if not is_dir and idx == len(segments) - 1 and '.' in clean:
                name, ext = clean.rsplit('.', 1)
                if name and ext and ext.isalnum():
                    parts.append(f'{name}点{ext}')
                    continue
            parts.append(clean)

        if is_dir:
            following = text[i:i + 5].lstrip()
            if not following.startswith(('目录', '下')):
                parts.append('目录')

        if parts:
            result.append(' '.join(parts))
        else:
            result.append(text[start:i])

    return ''.join(result)


def _normalize_math(text: str) -> str:
    """
    Convert math symbols to spoken form (borrowed from video-tutorial-v2-publish).

    Rules:
      -5 → 负5
      5+3 → 5加3
      5-3 → 5减3 (when between digits)
      5×3 → 5乘3
      5÷3 → 5除以3
      5/3 → 5除以3 (when between digits)
      ≈ → 约等于
      < / > → 小于 / 大于 (when between digits)
    """
    # × ÷ symbols
    text = text.replace("×", "乘").replace("÷", "除以")
    text = text.replace("≈", "约等于")
    # + between digits → 加
    text = re.sub(r"(\d)\s*\+\s*(\d)", r"\1加\2", text)
    # - between digits → 减 (but NOT leading negative sign, handled below)
    text = re.sub(r"(\d)\s*-\s*(\d)", r"\1减\2", text)
    # leading minus before a number → 负 (avoid breaking paths like ~/.codebuddy)
    # Only convert when preceded by whitespace, start, or CJK char
    text = re.sub(r"(^|[\s，。；：、）)])(-)(\d+(?:\.\d+)?)",
                  r"\1负\3", text)
    # division slash between digits → 除以
    text = re.sub(r"(\d)\s*/\s*(\d)", r"\1除以\2", text)
    # < > between numbers
    text = re.sub(r"(\d)\s*<\s*(\d)", r"\1小于\2", text)
    text = re.sub(r"(\d)\s*>\s*(\d)", r"\1大于\2", text)
    # 2.5 → 二点五 (spell decimal points in Chinese, common in TTS)
    # Keep as-is; edge-tts handles digit decimals fine. Skipped.
    return text


_POLYPHONE_RE = re.compile(r"([\u4e00-\u9fff])\{([a-z]+\d)\}")


def _strip_polyphone_marks(text: str) -> str:
    """Strip polyphone marks like 倒{dao3}角 → 倒角 (for subtitle display)."""
    return _POLYPHONE_RE.sub(r"\1", text)


def _expand_polyphone_marks(text: str) -> str:
    """
    Expand polyphone marks into TTS-friendly pinyin readings.
    E.g. 倒{dao3}角 → 倒(dao3)角  [kept as annotation for engines that
    understand it; for edge-tts/Qwen3 the mark is stripped and the model
    infers from context].
    """
    def _repl(m: "re.Match") -> str:
        ch, py = m.group(1), m.group(2)
        # Keep the character + pinyin in parentheses for engines that
        # support SSML-like annotations; strip otherwise in caller.
        return f"{ch}({py})"
    return _POLYPHONE_RE.sub(_repl, text)


def normalize_pronunciation(text: str) -> str:
    """
    Normalize text for TTS pronunciation.
    1. Convert paths to spoken form
    2. Convert math symbols to spoken form (v2.2)
    3. Apply term-level pronunciation rules from config
    4. Expand/strip polyphone marks (v2.2)
    """
    # Step 1: Math symbols FIRST (before paths, so 5/3 isn't eaten as a path)
    text = _normalize_math(text)

    # Step 2: Path normalization
    text = _normalize_paths(text)

    # Step 3: Term rules
    for pattern, replacement in _load_rules():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Step 4: Polyphone marks — strip for TTS output (let TTS infer context).
    # The raw text (with marks) is used for subtitles only when explicitly requested.
    text = _strip_polyphone_marks(text)

    return text


def add_narration_tts_text(narrations: list) -> list:
    """
    Add 'tts_text' field to each narration entry with pronunciation-normalized text.
    Modifies in place.
    """
    for item in narrations:
        if "tts_text" not in item:
            item["tts_text"] = normalize_pronunciation(item.get("text", ""))
    return narrations


# ────────────────────────────────────────────────
# CLI test
# ────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    tests = [
        "HAZOP 分析在 ~/.codebuddy/skills/ 目录",
        "LOPA 和 SIL 定级方法",
        "管道压力为 500 kPa",
        "参照 NFPA 标准执行",
        "PC-TWA 和 PC-STEL 的测定",
        "./config/api.md 配置文件",
        # v2.2 数学符号
        "温度从 -5 度升到 10 度",
        "产量 5+3 万吨",
        "转化率 3×4 倍",
        "效率提高 5÷2 倍",
        "压力 5/3 MPa",
        # v2.2 多音字标注
        "化学中 倒{dao3}角 处理",
        "重{zhong4}要工序",
    ]
    for t in tests:
        print(f"  IN:  {t}")
        print(f"  OUT: {normalize_pronunciation(t)}")
        print()
