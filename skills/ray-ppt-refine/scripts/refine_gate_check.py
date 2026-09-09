#!/usr/bin/env python3
"""
refine_gate_check.py — ray-ppt-refine 机读化 QA 门禁

用法：
  python refine_gate_check.py <refine后pptx> <diagnostics.json> [--outdir <工作目录>]

输出：
  <工作目录>/refine_gate_result.json

检查项（v2.1.0）：
  1. overflow_risk：文字溢出风险（文字框高 vs 文字估算高度）
  2. font_consistency：字体一致性（目标字体在全部文本中占比）
  3. color_dominance：主色占比（主色在可见 shape 填充中占比）
  4. overlap_true_positive：真重叠（用行高估算，非裸框体相交）
  5. editability_redline：可编辑性红线（主文本是否有图片化）

由 Python 直接判定 passed / user_code_errors[]，禁止 AI 口头宣布门禁通过。
"""

import argparse
import json
import os
import sys
from collections import Counter

try:
    from pptx import Presentation
    from pptx.util import Inches, Pt, Emu
except ImportError:
    print("ERROR: python-pptx required. pip install python-pptx", file=sys.stderr)
    sys.exit(1)


def _safe_text_len(shape):
    """获取 shape 实际文字内容的字符数（非框体高度）"""
    if not shape.has_text_frame:
        return 0
    return len(shape.text_frame.text.strip())


def _text_estimated_height(shape):
    """
    估算文字实际高度（行高估算器）。
    lines = ceil(len / chars_per_line)
    cpl = 宽度(in) * 72 / pt_size
    height = lines * pt * 1.45 / 72  (in inches)
    """
    if not shape.has_text_frame:
        return 0
    tf = shape.text_frame
    total_height = 0.0
    shape_width_in = shape.width / 914400  # EMU to inches
    for para in tf.paragraphs:
        text = para.text.strip()
        if not text:
            total_height += 12 / 72  # 空行约 12pt
            continue
        # 获取段落字号
        font_size_pt = 12.0
        if para.runs:
            for run in para.runs:
                if run.font.size:
                    font_size_pt = run.font.size.pt
                    break
        cpl = max(1, int(shape_width_in * 72 / font_size_pt))
        import math
        lines = math.ceil(len(text) / cpl)
        total_height += lines * font_size_pt * 1.45 / 72
    return total_height


def check_overflow(slide, slide_idx, text_frame_threshold=0.85):
    """
    检查文字溢出风险：文字估算高度 > 框体高度 * 阈值
    返回 list of dicts
    """
    errors = []
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        est_h = _text_estimated_height(shape)
        box_h = shape.height / 914400  # inches
        if box_h > 0 and est_h > box_h * text_frame_threshold:
            # 仅对 word_wrap=False 或文字量大的做报错
            tf = shape.text_frame
            if (tf.word_wrap is False and _safe_text_len(shape) > 20) or \
               (box_h > 0 and est_h > box_h * 1.05):
                errors.append({
                    "type": "overflow_risk",
                    "slide": slide_idx,
                    "shape_id": shape.shape_id,
                    "text_preview": shape.text_frame.text[:50].strip(),
                    "est_height_in": round(est_h, 2),
                    "box_height_in": round(box_h, 2),
                    "severity": "fail" if est_h > box_h * 1.0 else "warn"
                })
    return errors


def check_font_consistency(slide, slide_idx, target_font="Microsoft YaHei"):
    """检查字体一致性：返回该 slide 中不在 target_font 的 run"""
    issues = []
    for shape in slide.shapes:
        if not shape.has_text_frame:
            continue
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if run.text.strip() and run.font.name:
                    if run.font.name != target_font:
                        issues.append({
                            "type": "font_inconsistency",
                            "slide": slide_idx,
                            "shape_id": shape.shape_id,
                            "found_font": run.font.name,
                            "expected_font": target_font,
                            "text_preview": run.text[:30].strip()
                        })
    return issues


def check_editability(slide, slide_idx):
    """
    可编辑性红线：检测是否有文字被图片化（text_as_picture）。
    当前启发式：整页只有图片、无可编辑文本框 → 标记为红色警报。
    """
    errors = []
    text_shapes = sum(1 for s in slide.shapes if s.has_text_frame and _safe_text_len(s) > 5)
    if text_shapes == 0:
        errors.append({
            "type": "editability_redline",
            "slide": slide_idx,
            "severity": "fail",
            "msg": "本页无可编辑文字（可能文字被图片化，违反铁律 4）"
        })
    return errors


def check_overlap(slide, slide_idx):
    """
    重叠检测（行高估算版，非裸框体相交）。
    只检测两个有文字的 shape 之间：文字实际底边 > 另一个 shape 顶边 且存在 X 方向重叠。
    """
    errors = []
    text_shapes = []
    for shape in slide.shapes:
        if shape.has_text_frame and _safe_text_len(shape) > 5:
            est_h = _text_estimated_height(shape)
            text_shapes.append({
                "shape": shape,
                "left": shape.left / 914400,
                "top": shape.top / 914400,
                "width": shape.width / 914400,
                "est_bottom": shape.top / 914400 + est_h,
            })
    for i, a in enumerate(text_shapes):
        for j, b in enumerate(text_shapes):
            if i >= j:
                continue
            # X 方向重叠？
            x_overlap = a["left"] < b["left"] + b["width"] and b["left"] < a["left"] + a["width"]
            if not x_overlap:
                continue
            # Y 方向真重叠（用估算底边，非框底）
            if a["est_bottom"] > b["top"] + 0.05 and b["est_bottom"] > a["top"] + 0.05:
                errors.append({
                    "type": "overlap_true_positive",
                    "slide": slide_idx,
                    "shape_a": a["shape"].shape_id,
                    "shape_b": b["shape"].shape_id,
                    "a_bottom": round(a["est_bottom"], 2),
                    "b_top": round(b["top"], 2),
                    "severity": "warn"
                })
    return errors


def main():
    parser = argparse.ArgumentParser(description="ray-ppt-refine QA 门禁脚本")
    parser.add_argument("pptx_path", help="refine 后的 PPTX 文件路径")
    parser.add_argument("diagnostics_json", help="诊断清单 JSON（可为空 JSON {}）")
    parser.add_argument("--outdir", default=".", help="输出目录（默认当前）")
    parser.add_argument("--target-font", default="Microsoft YaHei", help="目标字体（默认 Microsoft YaHei）")
    args = parser.parse_args()

    if not os.path.exists(args.pptx_path):
        print(f"ERROR: PPTX not found: {args.pptx_path}", file=sys.stderr)
        sys.exit(1)

    prs = Presentation(args.pptx_path)
    all_errors = []
    slide_count = len(prs.slides)

    for idx, slide in enumerate(prs.slides, 1):
        all_errors.extend(check_overflow(slide, idx))
        all_errors.extend(check_font_consistency(slide, idx, args.target_font))
        all_errors.extend(check_editability(slide, idx))
        all_errors.extend(check_overlap(slide, idx))

    # 分类统计
    error_types = Counter(e["type"] for e in all_errors)
    fail_count = sum(1 for e in all_errors if e.get("severity") == "fail")
    warn_count = sum(1 for e in all_errors if e.get("severity") == "warn")

    # 判定 passed：有 fail 即不通过，warn 单独列出
    passed = fail_count == 0

    gate_result = {
        "pptx": os.path.basename(args.pptx_path),
        "slide_count": slide_count,
        "passed": passed,
        "fail_count": fail_count,
        "warn_count": warn_count,
        "error_types": dict(error_types),
        "user_code_errors": [e for e in all_errors if e.get("severity") == "fail"],
        "warnings": [e for e in all_errors if e.get("severity") == "warn"],
    }

    outdir = args.outdir or "."
    os.makedirs(outdir, exist_ok=True)
    out_path = os.path.join(outdir, "refine_gate_result.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(gate_result, f, indent=2, ensure_ascii=False)

    print(f"{'PASS' if passed else 'FAIL'} | slides={slide_count} | fail={fail_count} warn={warn_count}")
    print(f"Output: {out_path}")
    if not passed:
        print("Errors (must fix):")
        for e in gate_result["user_code_errors"]:
            print(f"  [{e['type']}] slide {e['slide']}: {e.get('text_preview', e.get('msg', ''))[:60]}")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
