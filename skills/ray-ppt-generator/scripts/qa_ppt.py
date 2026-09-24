# -*- coding: utf-8 -*-
"""PPT 生成后体检器（v3.20.0 新增）—— 一次跑三项机械检查 + 一项静态双页扫描

用法：
    python scripts/qa_ppt.py <文件.pptx>                     # 体检（越界/重叠/溢出）
    python scripts/qa_ppt.py <文件.pptx> --min-overlap 0.10  # 收紧重叠阈值
    python scripts/qa_ppt.py --dblpage gen_p01.py gen_p02.py # 双页隐患静态扫描（不读 pptx）

退出码：0 = 全部通过；1 = 有 FAIL；2 = 扫描器自身异常。
为什么需要它：文案写对了 ≠ 版式没坏。以下三类缺陷肉眼在 16:9 缩略图上看不出来，
但一定会在交付后被用户看到 —— 越界（元素出画布）、正文区重叠（文字压文字）、
文本溢出（word_wrap 后中文行数超出框高，字被裁掉）。
"""
import sys, math, unicodedata, argparse

EMU_IN = 914400.0
TOL = 0.02                      # 越界容差（in）
BODY_TOP, BODY_BOT = 1.55, 7.05  # 正文区（排除标题栏与页脚）


def em_len(s):
    """估算文本宽度（em 单位）：CJK/全角 = 1.0，ASCII ≈ 0.52，空格 ≈ 0.28"""
    n = 0.0
    for ch in s:
        if unicodedata.east_asian_width(ch) in ('W', 'F'):
            n += 1.0
        elif ch == ' ':
            n += 0.28
        else:
            n += 0.52
    return n


def _rect(sh):
    return (sh.left / EMU_IN, sh.top / EMU_IN, sh.width / EMU_IN, sh.height / EMU_IN)


def _has_text(sh):
    return sh.has_text_frame and sh.text_frame.text.strip() != ""


def _overflow(sh, rect):
    x, y, w, h = rect
    tf = sh.text_frame
    ml = tf.margin_left / EMU_IN if tf.margin_left else 0.1
    mr = tf.margin_right / EMU_IN if tf.margin_right else 0.1
    avail_pt = (w - ml - mr) * 72.0
    need, worst = 0.0, ""
    for p in tf.paragraphs:
        t = "".join(r.text for r in p.runs)
        if not t:
            continue
        sizes = [r.font.size.pt for r in p.runs if r.font.size]
        fs = max(sizes) if sizes else 12.0
        lines = max(1, math.ceil(em_len(t) / max(avail_pt / fs, 1.0)))
        ls = p.line_spacing if isinstance(p.line_spacing, float) else 1.25
        need += lines * fs * 1.22 * ls / 72.0
        if len(t) > len(worst):
            worst = t
    return (need - h, need, worst[:40]) if need > h + TOL else None


def check_pptx(path, min_overlap=0.06):
    from pptx import Presentation
    prs = Presentation(path)
    SW, SH = prs.slide_width / EMU_IN, prs.slide_height / EMU_IN
    print(f"=== {path} ｜ {SW:.3f} x {SH:.3f} in ｜ 共 {len(prs.slides._sldIdLst)} 页 ===")
    bad = 0
    for si, slide in enumerate(prs.slides, 1):
        issues, texts = [], []
        for sh in slide.shapes:
            rect = _rect(sh)
            x, y, w, h = rect
            if x < -TOL or y < -TOL or x + w > SW + TOL or y + h > SH + TOL:
                issues.append(f"  [越界] {sh.shape_type} rect=({x:.2f},{y:.2f},{w:.2f},{h:.2f})")
            if _has_text(sh):
                r = _overflow(sh, rect)
                if r:
                    issues.append(f"  [溢出] 需 {r[1]:.2f}\" 实 {h:.2f}\" 超 {r[0]:.2f}\" :: {r[2]}")
                if y + h > BODY_TOP and y < BODY_BOT and w > 0.3:
                    texts.append((x, y, w, h, sh.text_frame.text[:26]))
        for i in range(len(texts)):
            for j in range(i + 1, len(texts)):
                a, b = texts[i], texts[j]
                ox = max(0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
                oy = max(0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
                if ox * oy > min_overlap:
                    issues.append(f"  [重叠] {ox*oy:.2f} in²  「{a[4]}」 ↔ 「{b[4]}」")
        if issues:
            bad += 1
            print(f"\n--- P{si:02d} ---")
            print("\n".join(issues))
    print(f"\n{'✅ 全部通过' if bad == 0 else f'❌ {bad} 页有问题'}")
    return 1 if bad else 0


def scan_dblpage(py_files, page_funcs=("chain_slide", "card_slide", "stat_slide", "table_slide",
                                       "two_col_slide", "checklist_slide", "section_slide")):
    """静态扫描：页面函数内"自己建页 + 调用自带建页的页面函数" = 双页隐患。
    判据：同一 def 块内，既出现自建页（add_slide / slide(prs)），又出现页面函数调用。"""
    import re
    hits = []
    for f in py_files:
        try:
            # ⚠️ 必须用 utf-8-sig：PowerShell 的 Set-Content -Encoding UTF8 会写 BOM，
            # 而 BOM 会让 re.match(r"def\s+") 失配 → 整个文件被静默跳过（假阴性，2026-09-22 负控实测）
            src = open(f, encoding="utf-8-sig").read()
        except OSError as e:
            print(f"[跳过] {f}: {e}")
            continue
        # 按 def 切块（只取顶层缩进的 def）
        blocks = re.split(r"(?m)^(?=def\s)", src)
        for blk in blocks:
            m = re.match(r"def\s+(\w+)", blk)
            if not m:
                continue
            name = m.group(1)
            builds = ("add_slide(" in blk) or re.search(r"\bslide\(prs\)", blk)
            calls = [fn for fn in page_funcs if fn + "(" in blk]
            # 泛化：任何 x_slide( 调用（排除 add_slide 自身）
            calls += [g for g in re.findall(r"\b(\w+_slide)\(", blk) if g not in ("add_slide",) and g not in calls]
            if builds and calls:
                hits.append((f, name, sorted(set(calls))))
    if not hits:
        print("✅ 双页隐患扫描：0 命中")
        return 0
    print(f"❌ 双页隐患 {len(hits)} 处（该函数内既自建页、又调用自带建页的页面函数 → 会多出一页）：")
    for f, name, calls in hits:
        print(f"  {f} :: def {name}()  同时出现 自建页 + {calls}")
    print("  处置：删掉该函数里的自建页行（add_slide / s = slide(prs)），改为 s = <页面函数>(...)。")
    return 1


def main():
    ap = argparse.ArgumentParser(description="PPT 生成后体检器")
    ap.add_argument("target", nargs="+", help=".pptx 文件；--dblpage 模式下为 gen_*.py")
    ap.add_argument("--min-overlap", type=float, default=0.06, help="文本重叠面积阈值 in²（默认 0.06）")
    ap.add_argument("--dblpage", action="store_true", help="改做双页隐患静态扫描（不读 pptx）")
    a = ap.parse_args()
    if a.dblpage:
        return scan_dblpage(a.target)
    rc = 0
    for p in a.target:
        rc |= check_pptx(p, a.min_overlap)
    return rc


if __name__ == "__main__":
    sys.exit(main())
