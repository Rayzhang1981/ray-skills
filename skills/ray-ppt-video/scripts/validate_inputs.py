#!/usr/bin/env python3
"""
ray-PPT-TrVideo — 输入文件校验脚本。
在流水线启动前验证 PPTX 和演讲稿格式。

Usage:
    python validate_inputs.py --pptx slides.pptx --narration narration.json
    python validate_inputs.py --pptx slides.pptx --narration narration.json --reference-voice voice.wav --strict
"""

import argparse
import json
import os
import re
import subprocess
import sys


# ────────────────────────────────────────────────
# Color
# ────────────────────────────────────────────────

class C:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


def _ok(msg):
    print(f"  {C.GREEN}OK{C.END}  {msg}")


def _warn(msg):
    print(f"  {C.YELLOW}WARN{C.END} {msg}")


def _fail(msg):
    print(f"  {C.RED}FAIL{C.END} {msg}")


def _tip(msg):
    print(f"      {C.CYAN}TIP:{C.END} {msg}")


# ────────────────────────────────────────────────
# Validators
# ────────────────────────────────────────────────

def validate_pptx(path: str) -> tuple:
    """Validate PPTX file. Returns (ok, slide_count, warnings)."""
    warnings = []

    if not os.path.isfile(path):
        _fail(f"PPTX 不存在: {path}")
        return False, 0, ["文件不存在"]

    if not path.lower().endswith(".pptx"):
        _warn("文件扩展名不是 .pptx")

    size_mb = os.path.getsize(path) / (1024 * 1024)
    if size_mb < 0.01:
        _fail(f"PPTX 太小 ({size_mb:.2f} MB)，可能损坏")
        return False, 0, ["文件太小"]
    if size_mb > 200:
        _warn(f"PPTX 很大 ({size_mb:.0f} MB)，处理可能较慢")
        warnings.append("文件较大")

    # Count slides
    try:
        from pptx import Presentation
        prs = Presentation(path)
        count = len(prs.slides)
        if count == 0:
            _fail("PPTX 没有幻灯片")
            return False, 0, ["无幻灯片"]
        _ok(f"PPTX: {count} 页, {size_mb:.1f} MB")
        return True, count, warnings
    except Exception as e:
        _fail(f"无法打开 PPTX: {e}")
        return False, 0, [str(e)]


def validate_narration(path: str, expected_slides: int = 0) -> tuple:
    """Validate narration JSON. Returns (ok, slide_count, warnings, tips)."""
    warnings = []
    tips = []

    if not os.path.isfile(path):
        _fail(f"旁白 JSON 不存在: {path}")
        return False, 0, warnings, tips

    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        _fail(f"JSON 解析失败: {e}")
        return False, 0, [str(e)], tips

    if not isinstance(data, list) or len(data) == 0:
        _fail("JSON 格式错误: 应为非空数组")
        return False, 0, warnings, tips

    # Check structure
    slide_nums = set()
    valid = True
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            _fail(f"第 {i+1} 项不是对象")
            valid = False
            continue
        if "slide" not in item:
            _fail(f"第 {i+1} 项缺少 slide 字段")
            valid = False
            continue
        if "text" not in item or not item["text"].strip():
            _warn(f"Slide {item['slide']}: 内容为空")
            warnings.append(f"Slide {item['slide']} 无内容")
        slide_nums.add(item["slide"])

    slide_count = len(data)
    _ok(f"旁白 JSON: {slide_count} 页")

    # Check slide number continuity
    expected = set(range(1, slide_count + 1))
    if slide_nums != expected:
        _warn(f"页码不连续: {sorted(slide_nums)}")
        warnings.append("页码不连续")
        tips.append("确保 slide 字段从 1 开始连续编号")

    # Check against PPTX
    if expected_slides > 0 and slide_count != expected_slides:
        _warn(f"旁白 ({slide_count} 页) vs PPTX ({expected_slides} 页) 不匹配")
        warnings.append("页数不匹配")
        tips.append("确保每页 PPT 都有对应的旁白")

    # Check content length
    total_chars = sum(len(item.get("text", "")) for item in data)
    if total_chars < 100:
        _warn("旁白内容较少，视频可能很短")
        warnings.append("内容较少")

    # Check for problematic chars
    for item in data:
        text = item.get("text", "")
        if re.search(r'[【】「」『』]', text):
            _warn(f"Slide {item['slide']}: 含特殊括号，可能影响 TTS")
            tips.append("建议将特殊括号替换为普通括号")

    return valid, slide_count, warnings, tips


def validate_audio(path: str) -> tuple:
    """Validate reference audio. Returns (ok, duration, warnings)."""
    warnings = []

    if not path:
        return True, 0, []

    if not os.path.isfile(path):
        _fail(f"参考音频不存在: {path}")
        return False, 0, ["文件不存在"]

    ext = os.path.splitext(path)[1].lower()
    valid_exts = {".wav", ".mp3", ".m4a", ".flac", ".ogg", ".aac"}
    if ext not in valid_exts:
        _warn(f"音频格式 {ext} 可能不受支持")
        warnings.append("格式不常见")

    try:
        r = subprocess.run([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            path
        ], capture_output=True, text=True, timeout=10)
        dur = float(r.stdout.strip()) if r.returncode == 0 else 0

        if dur < 3:
            _warn(f"参考音频太短 ({dur:.1f}s)，声音克隆效果可能不佳")
            warnings.append("时长过短")
            _tip("建议 5-15 秒清晰人声")
        elif dur > 60:
            _warn(f"参考音频较长 ({dur:.1f}s)，将自动截取前 15 秒")
            warnings.append("时长较长")

        _ok(f"参考音频: {dur:.1f}s")
        return True, dur, warnings
    except Exception as e:
        _warn(f"无法分析音频: {e}")
        return True, 0, [str(e)]


# ────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PPT转视频 — 输入文件校验")
    parser.add_argument("--pptx", required=True, help="PPTX 幻灯片")
    parser.add_argument("--narration", default="", help="旁白 JSON (可选)")
    parser.add_argument("--reference-voice", default="", help="参考音频 (可选)")
    parser.add_argument("--strict", action="store_true", help="警告也视为错误")
    args = parser.parse_args()

    print(f"\n{C.BOLD}ray-PPT-TrVideo — 输入校验{C.END}\n")

    all_valid = True
    all_warnings = []
    all_tips = []

    # 1. PPTX
    print(f"{C.BOLD}1. PPTX 幻灯片{C.END}")
    pptx_ok, pptx_pages, w = validate_pptx(args.pptx)
    all_valid = all_valid and pptx_ok
    all_warnings.extend(w)

    # 2. Narration
    if args.narration:
        print(f"\n{C.BOLD}2. 旁白 JSON{C.END}")
        nar_ok, nar_pages, w, tips = validate_narration(args.narration, pptx_pages)
        all_valid = all_valid and nar_ok
        all_warnings.extend(w)
        all_tips.extend(tips)
    else:
        print(f"\n{C.BOLD}2. 旁白 JSON{C.END}")
        _warn("未提供，跳过校验")

    # 3. Reference audio
    if args.reference_voice:
        print(f"\n{C.BOLD}3. 参考音频{C.END}")
        audio_ok, _, w = validate_audio(args.reference_voice)
        all_valid = all_valid and audio_ok
        all_warnings.extend(w)

    # Summary
    print(f"\n{C.BOLD}{'='*50}{C.END}")
    print(f"{C.BOLD}  校验结果{C.END}")
    print(f"{C.BOLD}{'='*50}{C.END}\n")

    if all_valid and not all_warnings:
        print(f"  {C.GREEN}OK — 所有文件校验通过!{C.END}\n")
        return 0
    elif all_valid and all_warnings:
        print(f"  {C.YELLOW}WARN — 存在警告:{C.END}")
        for w in all_warnings:
            print(f"     - {w}")
        if all_tips:
            print(f"\n  {C.CYAN}建议:{C.END}")
            for t in all_tips:
                print(f"     - {t}")
        if args.strict:
            print(f"\n  {C.RED}严格模式: 警告视为错误{C.END}\n")
            return 1
        print(f"\n  可以继续，但可能影响质量。\n")
        return 0
    else:
        print(f"  {C.RED}FAIL — 存在问题，请修复。{C.END}")
        if all_tips:
            for t in all_tips:
                print(f"     - {t}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
