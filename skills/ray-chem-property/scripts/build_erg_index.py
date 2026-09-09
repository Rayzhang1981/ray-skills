# -*- coding: utf-8 -*-
"""ERG 2024 (US DOT Emergency Response Guidebook) → data/ERG2024-索引.json

提取 Yellow Table 1（Initial Isolation + Protective Action Distances，按 UN 号）。
来源价值：TIH 物料的隔离距离/下风向防护距离——中文全书与 TDG 均无此数据，是
emergency_guidelines 列的国际权威补充（与危险品全书应急段互补：书给处置文本，ERG 给量化距离）。

PDF 结构（2026-08-27 词坐标 + 渲染图双重确认，页293/printed 291 为基准）：
  - Yellow Table 1 数据页 ≈ P292-P334（42页），横排 3 栏旋转 90°：
      x 轴 = 条目（每条 ≈13.4pt，值词与 ID 词同 x 起点）
      y 轴 = 字段行。每条物料仅占一行，Small/Large 两组值上下堆叠：
        ── Small spills（上半）──                ── Large spills（下半）──
        y≈498-514 UN号(ID)                       y≈184-198 ISO (m)
        y≈478-494 Guide号                        y≈150-164 ISO (ft)
        y≈405-460 物料名（主名行 x≈cx）           y≈119-136 DAY (km)
        y≈358-372 ISO (m)  y≈324-340 (ft)        y≈84-101  DAY (mi)
        y≈296-312 DAY (km) y≈268-284 (mi)        y≈50-69   NIGHT (km)
        y≈240-256 NIGHT(km) y≈208-226 (mi)       y≈18-36   NIGHT (mi)
  - 同 UN 可出现两行 = 两个不同物料（1079=光气+二氧化硫），或交叉引用行
    （1082 Refrigerant gas R-1113 → 无数值，正行为 Trifluorochloroethylene），
    或 "(when spilled in water)" 变体行（水中泄漏距离不同，自带数值）。
  - 大泄漏数值被 "Refer to Table 3" 替代的条目（常见 TIH 气体）→ refer_table3=true。

去重规则：同 UN 多行时——有数值行优先为正条目；无数值交叉引用行名收进 aliases；
"(when spilled in water)" 有值变体单独存 "<UN>-water" 键。

产出：
  {"<UN>": {"un","guide","name","aliases":[...],
            "small": {"iso_m","iso_ft","day_km","day_mi","night_km","night_mi"},
            "large": {...} 或 refer_table3: true}}

用法:
  python build_erg_index.py "<ERG PDF>" [--output ../data/ERG2024-索引.json] [--debug]
"""
import argparse
import json
import os
import re
import sys

try:
    import fitz
except ImportError:
    print("需要 PyMuPDF: pip install pymupdf", file=sys.stderr)
    sys.exit(1)

# 字段行 y 带定标（页293 实测；±容差覆盖全部 Yellow 页）。
# ⚠️ 页面旋转 90°：真实列序（y 小→大）= NIGHT.mi, NIGHT.km, DAY.mi, DAY.km,
#   ISO.ft, ISO.m —— 已按 UN1005 官方值 (DAY 0.1km/0.1mi, NIGHT 0.2km/0.1mi)
#   比对确认，勿再凭直觉写反。Large spills 各带在 y 更小处（图面更下方）。
Y_BANDS = {
    "un":        (498, 514),
    "guide":     (478, 494),
    "name":      (396, 462),   # ⚠️ 下界396：斜体续行/water变体下探到y398（2-Methyl…@404）
    # Small spills
    "iso_m":     (356, 374),
    "iso_ft":    (322, 342),
    "day_km":    (294, 314),
    "day_mi":    (266, 286),
    "night_km":  (238, 258),
    "night_mi":  (206, 228),
    # Large spills（同列下半区，y 更小）
    "l_iso_m":   (182, 200),
    "l_iso_ft":  (148, 166),
    "l_day_km":  (117, 138),
    "l_day_mi":  (82, 103),
    "l_night_km": (48, 70),
    "l_night_mi": (16, 38),
}

SMALL_BANDS = ("iso_m", "iso_ft", "day_km", "day_mi", "night_km", "night_mi")
LARGE_BANDS = ("l_iso_m", "l_iso_ft", "l_day_km", "l_day_mi", "l_night_km", "l_night_mi")

UN_RE = re.compile(r"^\d{4}$")
WATER_RE = re.compile(r"when spilled in water", re.I)


def cluster_columns(un_words):
    """把 UN 词按 x 聚类成条目列。UN(ID)+Guide 在每条目左缘，间隔≈13pt。"""
    xs = sorted(w[0] for w in un_words)
    clusters = []
    for x in xs:
        if clusters and x - clusters[-1][-1] < 6:
            clusters[-1].append(x)
        else:
            clusters.append([x])
    return [c[0] for c in clusters]


def words_in_band(words, y0, y1, x0, x1):
    out = [w for w in words if y0 <= w[1] <= y1 and x0 <= w[0] < x1]
    out.sort(key=lambda w: (w[1], w[0]))
    return out


def parse_page(page):
    """解析一页 Yellow Table 1，返回 (cx, entry) 列表。
    entry: {band: [token,...]}（name 带保留 fitz 词元组）。"""
    words = page.get_text("words")
    un_words = [w for w in words
                if Y_BANDS["un"][0] <= w[1] <= Y_BANDS["un"][1] and UN_RE.match(w[4])]
    if not un_words:
        return []
    col_starts = cluster_columns(un_words)
    entries = []
    for i, cx in enumerate(col_starts):
        nxt = col_starts[i + 1] if i + 1 < len(col_starts) else 10**9
        x0 = cx - 0.5   # 浮点边界容差（ID 词与名称词 x0 有 ~0.1pt 微差）
        x1 = min(cx + 13.4, nxt)  # 每条目占宽 ≈13.4pt；值词与 ID 同 x 起点
        e = {}
        for band, (y0, y1) in Y_BANDS.items():
            ws = words_in_band(words, y0, y1, x0, x1)
            if band == "name":
                e[band] = ws
            else:
                e[band] = [w[4] for w in ws]
        entries.append((cx, e))
    return entries


def assemble(e, cx):
    """把一条目的 token 组装为记录。返回 None 表示无 ID。"""
    toks = e.get("un", [])
    if not toks:
        return None
    un = toks[0]
    g = e.get("guide", [])
    guide = g[0] if g else ""

    # 名称：旋转布局一个"视觉行" = 相同 x 的词列（y 降序读）。
    #   主名行 x≈cx；斜体续行 x≈cx+9（含 ", stabilized" / "(when spilled in water)"）。
    #   ⚠️ 分组阈值不能用 cx+9 定值：cx 取整簇起点（如38.5→39.0 浮点），主名词
    #   x=38.5 与续行词 x=47.5 距 cx 分别 -0.5/+8.5，用 cx+9 会把续行吞进主行。
    #   改用带内词自身 x 聚类（阈值3pt），第一簇 = 主行，其余簇按 x 序拼接。
    name_ws = e.get("name", [])
    name = ""
    if name_ws:
        xs = sorted(w[0] for w in name_ws)
        xclusters = [[xs[0]]]
        for x in xs[1:]:
            if x - xclusters[-1][-1] < 3:
                xclusters[-1].append(x)
            else:
                xclusters.append([x])
        lines = []
        for xc in xclusters:
            lo = xc[0] - 0.5
            ws_line = [w for w in name_ws if lo <= w[0] < xc[0] + 3]
            lines.append(" ".join(w[4] for w in sorted(ws_line, key=lambda w: -w[1])))
        name = " ".join(lines).strip()

    def num_text(band):
        """带内 token 形如 ['m','30'] / ['km','0.1'] / ['ft)','(100'] —— 数值 = 末 token。"""
        ts = e.get(band, [])
        if not ts:
            return ""
        return str(ts[-1]).replace("(", "").strip()

    small = {b: num_text(b) for b in SMALL_BANDS}
    large = {b: num_text(b) for b in LARGE_BANDS}
    # Refer to Table 3 检测：Large 区任一带出现 'Refer'（整段竖排跨带，取词面判断）
    refer3 = any("Refer" in str(t) or "Table" in str(t) for t in
                 (tok for b in LARGE_BANDS for tok in e.get(b, [])))
    if refer3:
        large = {}

    return {"un": un, "guide": guide, "name": name, "aliases": [],
            "small": small, "large": large, "refer_table3": refer3}


def has_values(rec):
    return any(v for v in rec["small"].values()) or any(v for v in rec["large"].values())


def main():
    ap = argparse.ArgumentParser(description="ERG2024 Yellow Table 1 提取")
    ap.add_argument("pdf")
    ap.add_argument("--output", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                     "..", "data", "ERG2024-索引.json"))
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    data_pages = []
    for pi in range(doc.page_count):
        words = doc[pi].get_text("words")
        n = sum(1 for w in words if Y_BANDS["un"][0] <= w[1] <= Y_BANDS["un"][1]
                and UN_RE.match(w[4]))
        if n >= 8:
            data_pages.append(pi)
    print(f"[erg] Yellow Table 1 data pages: {len(data_pages)} "
          f"({data_pages[0]+1 if data_pages else '-'}~{data_pages[-1]+1 if data_pages else '-'})")

    all_entries = []
    for pi in data_pages:
        for cx, e in parse_page(doc[pi]):
            a = assemble(e, cx)
            if a:
                all_entries.append(a)
    print(f"[erg] raw entries: {len(all_entries)}")

    # ── 去重合并：同 UN 多行（正行/交叉引用行/水中变体）──
    index = {}
    for a in all_entries:
        un = a["un"]
        if un not in index:
            index[un] = a
        elif has_values(a) and not has_values(index[un]):
            # 先前是交叉引用空行 → 正行顶替，旧名收为别名
            old = index.pop(un)
            if old["name"]:
                a["aliases"].append(old["name"])
            index[un] = a
        elif has_values(index[un]) and not has_values(a):
            if a["name"]:
                index[un]["aliases"].append(a["name"])
        # 两行都有值（罕见）→ 保留首行

    # 兜底：残留空名条目继承前一有名条目 + water 场景标注（water 变体行名称
    # 位于前一列，无法直接取到，只能按 ERG 排版惯例继承）
    prev_name = ""
    for a in all_entries:
        if a["name"]:
            prev_name = a["name"]
        elif prev_name and not a["name"]:
            a["name"] = prev_name
            prev_name = a["name"]  # 连续多个变体行也逐个继承
    empty_named = [a for a in index.values() if not a["name"]]
    if empty_named:
        print(f"[erg] WARN: {len(empty_named)} entries still nameless: "
              f"{[a['un'] for a in empty_named]}")

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print(f"[erg] unique keys: {len(index)} → {os.path.abspath(args.output)}")

    if args.debug:
        for k in ("1005", "1005-water", "1079", "1082"):
            if k in index:
                r = index[k]
                print(f"  {k}: {r['name'][:45]!r} guide={r['guide']} "
                      f"small={ {b: r['small'][b] for b in ('iso_m','day_km','night_km')} } "
                      f"large={ {b: r['large'].get(b, '') for b in ('l_iso_m','l_day_km','l_night_km')} } "
                      f"t3={r['refer_table3']}")
    doc.close()


if __name__ == "__main__":
    main()
