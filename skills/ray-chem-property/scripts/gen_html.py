# -*- coding: utf-8 -*-
"""Step 3b — 生成横版 HTML 报告（一行一物料，带「导出 Excel」按钮）。

读取 <out>/merged_*.json，生成：
  - 横版表格：一行一个物料，106 列按字段分区分组，物料名/表头冻结，可横向滚动
  - 「导出 Excel」按钮：SheetJS 前端把数据写进用户模板的 106 列表头结构（多级表头+合并单元格），
    下载为 .xlsx，列位与「工艺物料安全物性数据表」完全一致。

用法：
  python gen_html.py --outdir output/ --template "<模板.xlsx>" --output report.html
  （--template 可选；提供则导出按钮按模板真实表头重建，否则用两行简化表头）
"""
import argparse
import glob
import html
import json
import os
import re
import sys

import openpyxl.utils  # noqa: F401  # column_index_from_string 用于列宽抽取

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "field_schema.json")

GROUP_CN = {
    "identifiers": "化学品标识", "physical": "物理特性",
    "ghs_physical": "物理危害", "ghs_health": "健康危害", "ghs_env": "环境危害",
    "regulatory": "法规名录", "nfpa": "NFPA 704", "flammability": "燃爆数据",
    "exposure": "接触限值", "toxicity": "毒性数据", "other": "其他",
    "emergency": "应急准则", "supplementary": "补充数据",
}

GROUP_COLOR = {
    "identifiers": "#e2e8f0", "physical": "#dbeafe", "ghs_physical": "#fee2e2",
    "ghs_health": "#fef3c7", "ghs_env": "#dcfce7", "regulatory": "#f3e8ff",
    "nfpa": "#e0f2fe", "flammability": "#ffe4e6", "exposure": "#ffedd5",
    "toxicity": "#fae8ff", "other": "#e2e8f0",
    "emergency": "#fde8e8", "supplementary": "#e2e8f0",
}

# 重新生成报告用此命令（自动复制 xlsx-js-style.min.js 到 HTML 同目录）：
#   python gen_html.py --outdir output/ --template <模板.xlsx> --output report.html
XLSX_LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xlsx-js-style.min.js")


def load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _safe_rgb(color, wb=None):
    """安全提取 8 位 ARGB hex；支持 theme 色（经工作簿主题解析）；无法解析返回 None。"""
    if color is None:
        return None
    try:
        v = color.rgb
    except Exception:
        v = None
    if isinstance(v, str) and re.fullmatch(r"[0-9A-Fa-f]{8}", v):
        return v
    # theme 色：从工作簿主题调色板取基色，再按 tint 调明暗
    try:
        theme_idx = color.theme
        if theme_idx is not None and wb is not None:
            base = _theme_rgb(wb, theme_idx)
            if base:
                tint = getattr(color, "tint", 0) or 0
                return _apply_tint(base, tint)
    except Exception:
        pass
    # indexed 色（旧版调色板，如 41=浅灰）：openpyxl.styles.colors.COLOR_INDEX（8位但 alpha=00，需改 FF）
    try:
        idx = color.indexed
        if idx is not None:
            from openpyxl.styles.colors import COLOR_INDEX
            if 0 <= idx < len(COLOR_INDEX):
                v = COLOR_INDEX[idx]
                return "FF" + v[2:] if isinstance(v, str) and len(v) == 8 else v
    except Exception:
        pass
    return None


# openpyxl 主题调色板顺序：dk1 lt1 dk2 lt2 accent1-6 hlink folHlink
def _theme_rgb(wb, idx):
    """从工作簿主题 XML 解析第 idx 个主题色 → 'RRGGBB'。"""
    try:
        from openpyxl.xml.functions import fromstring
        xml = wb.loaded_theme
        if not xml:
            return None
        root = fromstring(xml)
        ns = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
        scheme = root.find(".//a:clrScheme", ns)
        if scheme is None:
            return None
        # openpyxl 的 color.theme 用 Excel 内部顺序：lt1 dk1 lt2 dk2 accent1-6 hlink folHlink
        # （与 clrScheme XML 里的 dk1 lt1 ... 不同，背景/文字交错在前两位）
        order = ["lt1", "dk1", "lt2", "dk2", "accent1", "accent2", "accent3",
                 "accent4", "accent5", "accent6", "hlink", "folHlink"]
        if idx >= len(order):
            return None
        node = scheme.find(f"a:{order[idx]}", ns)
        if node is None:
            return None
        # sysClr（如 windowText/window）或 srgbClr
        srgb = node.find("a:srgbClr", ns)
        if srgb is not None:
            return srgb.get("val")
        sysc = node.find("a:sysClr", ns)
        if sysc is not None:
            return sysc.get("lastClr")
    except Exception:
        return None
    return None


def _apply_tint(rgb6, tint):
    """按 tint（-1~1）调整 'RRGGBB' 明暗，返回 8 位 ARGB。"""
    def adj(ch):
        v = int(ch, 16)
        if tint < 0:
            v = int(v * (1.0 + tint))
        else:
            v = int(v * (1.0 - tint) + 255 * tint)
        return f"{max(0, min(255, v)):02X}"
    return "FF" + "".join(adj(rgb6[i:i + 2]) for i in (0, 2, 4))


def _cell_style(c, wb=None):
    """openpyxl 单元格 → SheetJS 样式 dict（仅非默认项；theme 色经主题解析）。"""
    s = {}
    f = c.fill
    if f and f.patternType:
        rgb = _safe_rgb(f.fgColor, wb)
        if rgb and rgb != "00000000":
            s["fill"] = {"patternType": f.patternType, "fgColor": {"rgb": rgb}}
    ft = c.font
    if ft:
        fo = {}
        if ft.name:
            fo["name"] = ft.name
        if ft.sz:
            fo["sz"] = int(ft.sz)
        if ft.bold:
            fo["bold"] = True
        if ft.italic:
            fo["italic"] = True
        rgb = _safe_rgb(ft.color, wb)
        if rgb and rgb != "FF000000":
            fo["color"] = {"rgb": rgb}
        if fo:
            s["font"] = fo
    al = c.alignment
    if al:
        a = {}
        if al.horizontal:
            a["horizontal"] = al.horizontal
        if al.vertical:
            a["vertical"] = al.vertical
        if al.wrap_text:
            a["wrapText"] = True
        if a:
            s["alignment"] = a
    bd = c.border
    if bd:
        b = {}
        for side, obj in (("top", bd.top), ("bottom", bd.bottom), ("left", bd.left), ("right", bd.right)):
            if obj and obj.style:
                side_style = {"style": obj.style}
                rgb = _safe_rgb(obj.color, wb)
                if rgb:
                    side_style["color"] = {"rgb": rgb}
                b[side] = side_style
        if b:
            s["border"] = b
    return s


def extract_template_header(path):
    """读模板行 1-8 的表头 + 样式 → {cells, merges, colWidths, rowHeights, headerStyles, dataStyle}。

    - cells/merges：0 基坐标，供 SheetJS
    - colWidths：定长数组（index=列索引），SheetJS !cols 直接可用
    - rowHeights：{行索引: hpt}（表头 8 行，SheetJS !rows）
    - headerStyles：{r,c: 样式}（非默认样式才存）
    - dataBorder：{text, num} 母版成品行文本列/数值列边框（SheetJS 格式）
    - dataStyle：{textStyle, numStyle} 参考模板成品数据行（文本列/数值列两种样式，不含 border）
    """
    from openpyxl import load_workbook
    wb = load_workbook(path, data_only=True)
    ws = wb["物性汇总表"]
    cells = {}
    for r in range(1, 9):
        for c in range(1, 112):
            v = ws.cell(row=r, column=c).value
            if v is not None and str(v) != "":
                cells[f"{r - 1},{c - 1}"] = str(v)
    merges = []
    for rng in ws.merged_cells.ranges:
        merges.append({
            "s": {"r": rng.min_row - 1, "c": rng.min_col - 1},
            "e": {"r": rng.max_row - 1, "c": rng.max_col - 1},
        })
    # 列宽（定长数组，index=列索引，SheetJS !cols 直接可用）
    col_widths = [None] * 111
    for col_letter, dim in ws.column_dimensions.items():
        if dim.width:
            try:
                idx = openpyxl.utils.column_index_from_string(col_letter) - 1
                if 0 <= idx < 111:
                    col_widths[idx] = round(dim.width, 2)
            except Exception:
                pass
    # 表头行高
    row_heights = {}
    for r in range(1, 9):
        rd = ws.row_dimensions.get(r)
        if rd and rd.height:
            row_heights[r - 1] = round(rd.height, 2)
    # 表头样式（全量存，含默认样式的空格——SheetJS 重建时无论有值/空格都需母版字体/填充）
    # 母版表头空格多为 MS Sans Serif 10（合并区 MergedCell 读不到样式），空 dict 兜底为该字体。
    header_default_font = {"font": {"name": "MS Sans Serif", "sz": 10}}
    header_styles = {}
    for r in range(1, 9):
        for c in range(1, 112):
            st = _cell_style(ws.cell(row=r, column=c), wb)
            if not st:
                st = dict(header_default_font)  # 空格兜底字体
            header_styles[f"{r - 1},{c - 1}"] = st
    # 参考数据行样式：按列抽取母版成品区「首行/中间行」两套完整样式（含 border/align/fill/font）
    # 母版成品行是逐列定制（hair 网格 + thin/thick/medium 分区边界），按列复制才能还原分区观感。
    # 末行不单独参照（母版末尾行常是残例行、顶线为 None），数据末行沿用中间行样式即可。
    data_rows = [r for r in range(9, ws.max_row + 1) if ws.cell(row=r, column=3).value]
    ref_first = data_rows[0] if data_rows else 9
    ref_mid = data_rows[1] if len(data_rows) > 1 else ref_first

    def _row_styles(rr):
        """抽取某一行 1-106 列的完整样式 → {c0: style}（0 基列）。"""
        d = {}
        for c in range(1, 112):
            st = _cell_style(ws.cell(row=rr, column=c), wb)
            d[c - 1] = st  # 含 border/align/fill/font（空 dict 也存，便于清空）
        return d

    row_styles = {"first": _row_styles(ref_first), "mid": _row_styles(ref_mid), "last": _row_styles(ref_mid)}
    # 表头统一边框：母版表头是 thick/medium/thin/hair/None 混杂，用户要求 R1-8 统一实线
    header_border = {s: "thin" for s in ("left", "right", "top", "bottom")}
    return {"cells": cells, "merges": merges, "colWidths": col_widths,
            "rowHeights": row_heights, "headerStyles": header_styles,
            "headerBorder": header_border,
            "rowStyles": row_styles}


def esc(v):
    return html.escape(str(v)) if v not in (None, "") else ""


def cell_html(key, entry, wide=False):
    val = entry.get("value", "")
    cands = entry.get("candidates", [])
    if not val:
        if cands:
            return '<td class="warn" title="有候选待确认">待确认</td>'
        return f'<td class="miss{" wide" if wide else ""}">·</td>'
    conflict = len(cands) > 1
    # 冲突值悬停增强：原生 title 兜底 + 自定义 .tip 悬浮卡（候选值×来源对照表）
    title = html.escape("；".join(f"{c['value']}({c['source']})" for c in cands))
    tip = ""
    if conflict:
        rows = "".join(
            f'<tr><td>{esc(c["value"])}</td><td>{esc(c.get("source", ""))}</td></tr>'
            for c in cands[:6])
        tip = (f'<span class="tipwrap"><span class="cf" title="{title}">⚠</span>'
               f'<span class="tip"><b>多源候选对照</b><table>{rows}</table></span></span>')
    # 火灾危险性类别着色（GB 50016：甲红/乙橙/丙黄/非可燃白）；宽文本列加 .wide
    base_cls = "celltxt wide" if wide else "celltxt"
    cls = base_cls
    if key == "fire_class":
        v = str(val)
        if v.startswith("甲"):
            cls = "fc-a"
        elif v.startswith("乙"):
            cls = "fc-b"
        elif v.startswith("丙"):
            cls = "fc-c"
        elif "非可燃" in v or "不可燃" in v or v == "—":
            cls = "fc-n"
    # 应急准则等宽文本列：超 4 行折叠，点击展开/收起
    if key == "emergency_guidelines":
        text = esc(val)
        if len(text) > 320:  # 约 560px 宽 × 4 行的字符量阈值
            short = text[:320]
            return (f'<td class="{cls}"><div class="fold"><div class="fold-txt">{short}'
                    f'<span class="dots">…</span><span class="more">{text[len(short):]}</span></div>'
                    f'<button class="foldbtn" onclick="toggleFold(this)">展开全文 ▾</button></div>{tip}</td>')
    return f'<td class="{cls}" title="{title}">{esc(val)}{tip}</td>'


def build_table(schema, records):
    fields = schema["fields"]
    sticky_key = "name_cn"
    display_fields = [f for f in fields if f["key"] != sticky_key]

    # 宽文本列（应急准则/备注等长文本）：HTML 限宽 + 自动换行，不再一行到底拉爆横向宽度
    WIDE_KEYS = {"emergency_guidelines", "remark", "handling_storage_note", "odor_character"}

    # 表头：分组带 + 字段名（中英双语，对齐母版 Excel 表头风格）
    # 第一行：分组（合并）；第二行：字段名中文 + 英文小字（含单位）
    group_row_cells = []
    field_row_cells = []
    i = 0
    n = len(display_fields)
    while i < n:
        grp = display_fields[i]["group"]
        j = i
        while j < n and display_fields[j]["group"] == grp:
            j += 1
        span = j - i
        color = GROUP_COLOR.get(grp, "#e2e8f0")
        group_row_cells.append(
            f'<th colspan="{span}" style="background:{color}">{esc(GROUP_CN.get(grp, grp))}</th>')
        for fd in display_fields[i:j]:
            unit = fd.get("unit", "")
            u = f'<span class="u">{esc(unit)}</span>' if unit else ""
            en = fd.get("en") or ""
            e = f'<span class="en">{esc(en)}</span>' if en and en != "#" else ""
            wide_cls = ' class="fld fld-wide"' if fd["key"] in WIDE_KEYS else ' class="fld"'
            # data-g=分组：列显隐开关按此过滤
            field_row_cells.append(
                f'<th{wide_cls} data-g="{esc(fd["group"])}">{esc(fd["cn"])}{e}{u}</th>')
        i = j

    # 数据行：一行一物料；data-s=搜索索引（名称+CAS 小写，供顶部过滤框即时匹配）。
    # 数据 td 的列显隐由 JS 按单元格索引映射分组（display 顺序与表头 data-g 一致），
    # 不给 109×N 个 td 全部塞 data-g，保持 DOM 精简。
    body_rows = []
    for rec in records:
        f = rec["fields"]
        name = f.get(sticky_key, {}).get("value", "") or rec.get("input", "")
        cas = f.get("cas", {}).get("value", "")
        s_idx = esc(f"{name} {cas}".lower())
        tds = [f'<td class="sticky"><b>{esc(name)}</b><span class="cas">{esc(cas)}</span></td>']
        for fd in display_fields:
            tds.append(cell_html(fd["key"], f.get(fd["key"], {}),
                                 wide=fd["key"] in WIDE_KEYS))
        body_rows.append(f'<tr data-s="{s_idx}">{"".join(tds)}</tr>')

    head = f'''<thead>
<tr class="grouphdr"><th rowspan="2" class="stickyhdr">物料</th>{''.join(group_row_cells)}</tr>
<tr class="fieldhdr">{''.join(field_row_cells)}</tr>
</thead>'''
    body = f'<tbody>{"".join(body_rows)}</tbody>'
    # <colgroup> 全列显式定宽（table-layout:fixed 配套）：应急准则 560px、备注 340px。
    # ⚠ 必须先补第 0 列（物料 sticky 列）的 <col>，否则整体错位一列——08-27 实测踩坑：
    # 少了 sticky 列的 col，560px 落到前一毒性列，应急准则仍显示窄条
    # 固定布局下列宽不参与协商；auto 布局下 td min/width 组合会被整表分配打败（~90px 窄条）。
    WIDE_COL_W = {"emergency_guidelines": 560, "remark": 340,
                  "handling_storage_note": 280, "odor_character": 150}
    STICKY_W, DEFAULT_W = 150, 92
    widths = [STICKY_W]
    for fd in display_fields:
        widths.append(WIDE_COL_W.get(fd["key"], DEFAULT_W))
    cols = [f'<col style="width:{w}px">' for w in widths]
    colgroup = f'<colgroup>{"".join(cols)}</colgroup>'
    table_w = sum(widths)
    return (f'<div class="twrap"><table class="hgrid fixed" style="width:{table_w}px">'
            f'{colgroup}{head}{body}</table></div>')


CSS = """
*{box-sizing:border-box}
body{font-family:"Segoe UI","Microsoft YaHei",sans-serif;margin:0;background:#f1f5f9;color:#0f172a}
.wrap{max-width:100%;padding:20px 24px}
.bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:12px}
h1{font-size:22px;margin:0}
.sub{color:#64748b;font-size:13px}
button.btn{background:#1d4ed8;color:#fff;border:none;padding:10px 20px;border-radius:8px;font-size:14px;cursor:pointer;font-weight:600}
button.btn:hover{background:#1e40af}
.twrap{overflow:auto;max-height:78vh;border:1px solid #e2e8f0;border-radius:10px;background:#fff}
table.hgrid{border-collapse:separate;border-spacing:0;font-size:12px;white-space:nowrap;vertical-align:top}
table.hgrid.fixed,table.hgrid.fixed td,table.hgrid.fixed th{white-space:normal}
table.hgrid.fixed td.celltxt,table.hgrid.fixed td:not(.wide){white-space:nowrap}
table.hgrid td.wide{vertical-align:top}
/* 表头双语：中文名 + 英文小字 */
.fld .en{display:block;color:#94a3b8;font-weight:400;font-size:9px;letter-spacing:.02em;margin-top:1px}
table.hgrid th,table.hgrid td{border:1px solid #eef2f7;padding:5px 8px;text-align:center;min-width:52px}
table.hgrid thead th{position:sticky;top:0;z-index:3;font-weight:600}
.grouphdr th{font-size:13px;color:#1e293b;border-bottom:2px solid #cbd5e1}
.fieldhdr th{font-size:11px;color:#475569;background:#f8fafc;top:34px}
.fld{line-height:1.15}
.u{display:block;color:#94a3b8;font-weight:400;font-size:10px}
th.stickyhdr{background:#0f172a;color:#fff;font-size:13px;min-width:110px}
td.sticky{position:sticky;left:0;z-index:2;background:#f8fafc;text-align:left;min-width:110px;font-weight:600}
td.sticky .cas{display:block;color:#94a3b8;font-weight:400;font-size:10px}
tbody tr:nth-child(even) td{background:#fbfcfe}
tbody tr:nth-child(even) td.sticky{background:#f1f5f9}
.miss{color:#cbd5e1}
/* 宽文本列（应急准则/备注）：colgroup 全列定宽 + fixed 布局，换行压行高 */
table.hgrid.fixed{table-layout:fixed}
td.wide,th.fld-wide{white-space:normal !important;word-break:break-word}
th.fld-wide{line-height:1.25;text-align:left}
td.wide{vertical-align:top;text-align:left;line-height:1.45;font-size:11px;color:#334155}
td.celltxt{white-space:nowrap}
tr:hover td{filter:brightness(0.985)}
.warn{color:#d97706;background:#fffbeb}
.cf{color:#dc2626;font-weight:bold}
/* ── a+b 工具栏：搜索框 + 分组列显隐 ── */
.tools{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
.tools input[type=search]{padding:8px 14px;border:1px solid #cbd5e1;border-radius:8px;font-size:13px;width:260px;outline:none}
.tools input[type=search]:focus{border-color:#1d4ed8;box-shadow:0 0 0 3px #dbeafe}
.grpbtn{padding:5px 12px;border:1px solid #cbd5e1;background:#fff;border-radius:16px;font-size:12px;cursor:pointer;color:#475569;user-select:none}
.grpbtn.on{background:#1d4ed8;color:#fff;border-color:#1d4ed8}
#hitinfo{font-size:12px;color:#64748b;min-width:90px}
/* ── c 冲突值悬浮卡 ── */
.tipwrap{position:relative;display:inline-block;margin-left:2px}
.tipwrap .tip{display:none;position:absolute;left:50%;transform:translateX(-50%);bottom:130%;
  background:#0f172a;color:#e2e8f0;border-radius:8px;padding:8px 10px;z-index:50;
  font-size:11px;font-weight:400;white-space:nowrap;box-shadow:0 6px 18px rgba(15,23,42,.35);text-align:left}
.tipwrap .tip table{border-collapse:collapse;margin-top:4px}
.tipwrap .tip td{border:1px solid #334155;padding:2px 8px;color:#e2e8f0;text-align:left}
.tipwrap .tip b{color:#fbbf24;font-weight:600}
.tipwrap:hover .tip{display:block}
/* ── f 应急长文本折叠 ── */
.fold .more{display:none}
.fold.open .more{display:inline}
.fold.open .dots{display:none}
.fold-txt{display:block;max-height:6.2em;overflow:hidden}
.fold.open .fold-txt{max-height:none}
.foldbtn{background:none;border:none;color:#1d4ed8;cursor:pointer;font-size:11px;padding:2px 0;margin-top:3px;display:block}
.foldbtn:hover{text-decoration:underline}
/* ── d sticky 首列在 fixed 布局下的背景修正（滚动时不透底） ── */
table.hgrid.fixed td.sticky,table.hgrid.fixed tbody tr:nth-child(even) td.sticky{position:sticky;left:0}
/* ── e 打印友好：A3 横版、隐藏交互元素、表头不重复悬浮 ── */
@media print{
  @page{size:A3 landscape;margin:10mm}
  body{background:#fff}
  .bar,.tools,.foldbtn,.ai-note{display:none !important}
  .twrap{overflow:visible;max-height:none;border:none}
  table.hgrid thead th{position:static}
  table.hgrid.fixed td.sticky{position:static}
  tr{page-break-inside:avoid}
  .tipwrap .tip{display:none}
}
.fc-a{background:#ffcccc;font-weight:bold;text-align:center}
.fc-b{background:#ffe0b2;font-weight:bold;text-align:center}
.fc-c{background:#fff9c4;font-weight:bold;text-align:center}
.fc-n{background:#ffffff;text-align:center}
.legend{font-size:12px;color:#64748b;margin-top:8px}
.ai-note{font-size:11px;color:#94a3b8;margin-top:6px;border-top:1px dashed #cbd5e1;padding-top:6px}
"""


def build_js(schema, records, header_json):
    col_map = {f["key"]: f["num"] for f in schema["fields"]}  # num 已是 0 基列索引（B=1…DG=110），勿再 -1
    data = []
    for rec in records:
        row = {}
        for k, entry in rec["fields"].items():
            v = entry.get("value", "")
            if v not in (None, ""):
                row[k] = v
        data.append(row)
    header_js = json.dumps(header_json, ensure_ascii=False) if header_json else "null"
    # Emergency Guidelines 列的 0 基索引（供前端导出固化 wch=120）
    emg_idx = next((f["num"] for f in schema["fields"] if f["key"] == "emergency_guidelines"), None)
    return {
        "col_map": json.dumps(col_map),
        "data": json.dumps(data, ensure_ascii=False),
        "header": header_js,
        "emg_col": emg_idx if emg_idx is not None else 105,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default="output")
    ap.add_argument("--output", default="report.html")
    ap.add_argument("--template", help="模板 xlsx（提供则导出按钮按真实表头重建）")
    args = ap.parse_args()

    # 批量保序命名（01_merged_xxx.json）优先；否则取常规 merged_xxx.json
    prefixed = sorted(glob.glob(os.path.join(args.outdir, "*_merged_*.json")))
    merged_files = prefixed if prefixed else \
        sorted(glob.glob(os.path.join(args.outdir, "merged_*.json")))
    if not merged_files:
        print("[html] 未找到 merged_*.json，请先运行 merge_compare.py")
        sys.exit(1)
    records = [json.load(open(p, encoding="utf-8")) for p in sorted(merged_files)]
    schema = load_schema()

    header_json = None
    if args.template and os.path.exists(args.template):
        header_json = extract_template_header(args.template)

    table = build_table(schema, records)
    js = build_js(schema, records, header_json)

    # a+b 工具栏：搜索框 + 分组列显隐按钮（按 schema 实际分组出现顺序生成，identifiers 是 sticky 列组不设开关）
    seen_groups = []
    for fd in schema["fields"]:
        g = fd.get("group", "")
        if g not in seen_groups:
            seen_groups.append(g)
    grp_btns = "".join(
        f'<button class="grpbtn on" data-g="{esc(g)}" '
        f'onclick="toggleGroup(this)">{esc(GROUP_CN.get(g, g))}</button>'
        for g in seen_groups if g != "identifiers")
    toolbar = f'''<div class="tools">
  <input type="search" id="q" placeholder="🔍 输入名称或 CAS 过滤…" oninput="filterRows()">
  <span id="hitinfo"></span>
  <span style="width:1px;height:22px;background:#e2e8f0"></span>
  <span style="font-size:12px;color:#94a3b8">列显隐：</span>{grp_btns}
</div>'''

    page = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>工艺物料安全物性数据表</title><style>{CSS}</style>
<script src="xlsx-js-style.min.js"></script></head>
<body><div class="wrap">
<div class="bar">
  <div><h1>工艺物料安全物性数据表</h1>
  <div class="sub">共 {len(records)} 个物料 · 一行一物料 · 悬停看来源 · ⚠ 多源冲突 · 导出格式与你模板一致</div></div>
  <button class="btn" onclick="window.print()">🖨 打印 / A3</button>
  <button class="btn" onclick="exportExcel()">⬇ 导出 Excel</button>
</div>
{toolbar}
{table}
<div class="legend">单位见字段下方小字；空单元格 · 表示未查到；黄底「待确认」为有候选值需人工裁决；⚠ 悬停看多源对照</div>
<div class="ai-note">⚠ AI 辅助生成 · 数据来自 PubChem/NIST/CAMEO/监管名录等公开源，未逐一人工核实，仅供专业审查参考，请核实后用于安全决策</div>
</div>
<script>
var COL_MAP = {js['col_map']};
var DATA = {js['data']};
var HEADER = {js['header']};

/* ── a 搜索过滤：按 data-s（名称+CAS 小写）即时过滤行 ── */
function filterRows() {{
  var q = document.getElementById('q').value.trim().toLowerCase();
  var rows = document.querySelectorAll('tbody tr');
  var hit = 0;
  rows.forEach(function(r) {{
    var show = !q || (r.dataset.s || '').indexOf(q) >= 0;
    r.style.display = show ? '' : 'none';
    if (show) hit++;
  }});
  document.getElementById('hitinfo').textContent = q ? ('命中 ' + hit + '/' + rows.length + ' 个物料') : '';
}}

/* ── b 列显隐：按表头 th[data-g] 找同组单元格序号隐藏（colgroup col 同步 display）── */
function toggleGroup(btn) {{
  var g = btn.dataset.g;
  var on = btn.classList.toggle('on');   // on=显示 off=隐藏
  var table = document.querySelector('table.hgrid');
  // 数据 td 序号 = 表头 fieldhdr 行内该 th 的前序位置 + 1（第0列为 sticky 物料列）
  var hdrs = Array.from(document.querySelectorAll('tr.fieldhdr th'));
  var idxs = [];
  hdrs.forEach(function(th, i) {{ if (th.dataset.g === g) idxs.push(i + 1); }});
  // 分组头（grouphdr）同组 colspan 一并处理：隐藏整组时把分组 th 也藏掉
  idxs.forEach(function(ci) {{
    table.querySelectorAll('thead tr.fieldhdr th:nth-child(' + (ci+1) + ')').forEach(function(el){{ el.style.display = on?'':'none'; }});
    var colEl = table.querySelectorAll('colgroup col')[ci];
    if (colEl) colEl.style.display = on ? '' : 'none';
    table.querySelectorAll('tbody tr').forEach(function(tr) {{
      var td = tr.children[ci];
      if (td) td.style.display = on ? '' : 'none';
    }});
  }});
  // 隐藏/恢复 grouphdr 对应的合并列（按组内列数求起止，取组首 th 显示状态控制）
}}

/* ── f 折叠展开 ── */
function toggleFold(b) {{
  var d = b.parentElement;
  var open = d.classList.toggle('open');
  b.textContent = open ? '收起 ▴' : '展开全文 ▾';
}}

function exportExcel() {{
  if (typeof XLSX === 'undefined') {{ alert('导出库未找到：请确认 xlsx-js-style.min.js 与本 HTML 在同一目录'); return; }}
  var wb = XLSX.utils.book_new();
  var ws = {{}};
  var nCols = 111, nData = DATA.length, dataStart = 8;  // 表头占 R1-8（0基 r0-7），数据从 R9（0基 r=8）起
  // 1. 表头（模板行1-8，含合并单元格 + 样式）
  if (HEADER) {{
    for (var k in HEADER.cells) {{
      var p = k.split(','); var r = +p[0], c = +p[1];
      var cell = {{ t:'s', v: HEADER.cells[k] }};
      if (HEADER.headerStyles && HEADER.headerStyles[k]) cell.s = HEADER.headerStyles[k];
      ws[XLSX.utils.encode_cell({{r:r, c:c}})] = cell;
    }}
    ws['!merges'] = HEADER.merges;
    if (HEADER.colWidths) {{
      // Emergency 列（DB，0基索引见 EMG_COL）宽固化 120 —— 与 export_excel.py 对齐；
      // 模板未调宽时（仍 15.8）前端导出会继承窄列导致行高爆炸，这里强制同用户定标值
      var EMG_COL = {js['emg_col']};
      ws['!cols'] = HEADER.colWidths.map(function(w, ci) {{
        var v = (ci === EMG_COL) ? 120.0 : w;
        return v ? {{wch: Math.round((v - 0.83) * 10) / 10}} : null;
      }});
    }}
    if (HEADER.rowHeights) {{
      var rows = [];
      for (var ri = 0; ri < 8; ri++) rows.push(HEADER.rowHeights[ri] ? {{hpt: HEADER.rowHeights[ri]}} : null);
      // 数据行高统一 50pt（2026-08-27 用户实测定标：Emergency 列宽120 + 行高50，
      // 与 export_excel.py 的 ws.row_dimensions[row].height = 50.0 对齐）
      for (var di = 0; di < nData; di++) rows[8 + di] = {{hpt: 50}};
      ws['!rows'] = rows;
    }}
  }} else {{
    var groups = {json.dumps([f["cn"] for f in schema["fields"]])};
    XLSX.utils.sheet_add_aoa(ws, [groups], {{origin:'A1'}});
  }}
  // 工具：边框字符串 → SheetJS 对象
  function borderObj(bd) {{
    if (!bd) return null;
    var b = {{}};
    ['left','right','top','bottom'].forEach(function(s){{ if (bd[s]) b[s] = {{style: bd[s]}}; }});
    return Object.keys(b).length ? b : null;
  }}
  // 2. 表头 R1-8 统一边框（母版是 thick/medium/thin/hair 混杂，统一为实线 headerBorder）；
  //    空单元格同时套 headerStyles 里的完整样式（font/fill/align），避免只补 border 丢字体
  var hdrBd = (HEADER && HEADER.headerBorder) ? borderObj(HEADER.headerBorder) : null;
  if (HEADER && hdrBd) {{
    for (var hr = 0; hr < 8; hr++) for (var hc = 0; hc < nCols; hc++) {{
      var haddr = XLSX.utils.encode_cell({{r:hr, c:hc}});
      var hk = hr + ',' + hc;
      var baseStyle = (HEADER.headerStyles && HEADER.headerStyles[hk]) ? HEADER.headerStyles[hk] : {{}};
      if (!ws[haddr]) ws[haddr] = {{t:'s', v:''}};
      // 先铺 headerStyles 的完整样式（font/fill/align），再覆盖统一边框
      var hs = {{}};
      for (var sk in baseStyle) hs[sk] = baseStyle[sk];
      hs.border = hdrBd;  // 覆盖原有混杂边框
      ws[haddr].s = hs;
    }}
  }}
  // 3. 数据行：先按行（首/中/末）+按列铺母版逐列完整样式（含 border/align/fill/font），再填值
  var RS = (HEADER && HEADER.rowStyles) ? HEADER.rowStyles : null;
  for (var i = 0; i < nData; i++) {{
    var r = (HEADER ? dataStart : 1) + i;
    var rowStyle = RS ? (i===0 ? RS.first : (i===nData-1 ? RS.last : RS.mid)) : null;
    // 3a. 每列先建单元格并套母版样式（含空单元格）
    if (rowStyle) {{
      for (var cc = 0; cc < nCols; cc++) {{
        var addr0 = XLSX.utils.encode_cell({{r:r, c:cc}});
        if (!ws[addr0]) ws[addr0] = {{t:'s', v:''}};
        var st = rowStyle[cc];
        if (st) ws[addr0].s = st;
      }}
    }}
    // 3b. 填值（保留已铺的样式）
    var row = DATA[i];
    for (var key in row) {{
      if (COL_MAP[key] !== undefined) {{
        var addr = XLSX.utils.encode_cell({{r:r, c:COL_MAP[key]}});
        var exist = ws[addr];
        ws[addr] = {{ t:'s', v: String(row[key]) }};
        if (exist && exist.s) ws[addr].s = exist.s;
      }}
    }}
    // 3c. 序号自动分配（第 i 行 = i+1，seq 字段数据里无值）
    if (COL_MAP['seq'] !== undefined) {{
      var seqAddr = XLSX.utils.encode_cell({{r:r, c:COL_MAP['seq']}});
      var seqExist = ws[seqAddr];
      ws[seqAddr] = {{ t:'s', v: String(i + 1) }};
      if (seqExist && seqExist.s) ws[seqAddr].s = seqExist.s;
    }}
    // 3d. Emergency 列强制 wrap_text + 顶端对齐（列宽120 + 行高50 布局配套）
    var emgAddr = XLSX.utils.encode_cell({{r:r, c: {js['emg_col']} }});
    var emgCell = ws[emgAddr];
    if (emgCell) {{
      var es = emgCell.s || {{}};
      es.alignment = Object.assign({{}}, es.alignment, {{wrapText: true, vertical: 'top'}});
      emgCell.s = es;
    }}
  }}
  ws['!ref'] = XLSX.utils.encode_range({{s:{{r:0,c:0}}, e:{{r:(HEADER?dataStart:1)+nData-1, c:nCols-1}}}});
  XLSX.utils.book_append_sheet(wb, ws, '物性汇总表');
  XLSX.writeFile(wb, '物性汇总表-导出.xlsx');
}}
</script>
</body></html>"""

    out_path = args.output
    # 相对路径输出到「当前工作目录」而非 outdir（避免 HTML 藏在 output/ 子目录里用户找不到）
    if not os.path.isabs(out_path):
        out_path = os.path.abspath(out_path)
    # 把 xlsx-js-style 库复制到报告同目录（离线导出），HTML 用相对路径引用
    import shutil
    lib_dst = os.path.join(os.path.dirname(out_path), "xlsx-js-style.min.js")
    if os.path.exists(XLSX_LIB) and os.path.abspath(XLSX_LIB) != os.path.abspath(lib_dst):
        shutil.copyfile(XLSX_LIB, lib_dst)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"[html] 横版报告已生成 → {out_path}（{len(records)} 个物料"
          f"{'，含模板表头' if header_json else '，简化表头'}，导出库已离线内置）")


if __name__ == "__main__":
    main()
