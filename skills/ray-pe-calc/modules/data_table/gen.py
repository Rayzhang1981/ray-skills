#!/usr/bin/env python3
"""
数据表格生成器 (Data Table Generator)
=====================================
从结构化 JSON 数据生成专业工程表格，输出 Markdown 或 HTML 格式。

用法:
    python gen.py --type comparison --input data.json --output result.md
    python gen.py --type summary --data '[...]' --output result.md
    python gen.py --type pipe-select --output result.md
    python gen.py --type pipe-select --medium gas --flow 2000 --pressure 1.0
"""

import sys
import json
import os
import argparse
import re
import math
from typing import List, Dict, Any, Optional, Union


# =============================================================================
# Core table rendering
# =============================================================================

def _escape_cell(value: str) -> str:
    """Escape pipe characters in cell content for Markdown."""
    return str(value).replace("|", "\\|").replace("\n", "<br>")


def _format_cell(value: Any) -> str:
    """Format a cell value for display."""
    if value is None:
        return "-"
    if isinstance(value, float):
        # Show reasonable precision
        if abs(value) >= 10000 or (abs(value) < 0.01 and value != 0):
            return f"{value:.4g}"
        return f"{value:.2f}"
    return str(value)


def _column_widths(headers: List[str], rows: List[List[str]]) -> List[int]:
    """Calculate optimal column widths based on content."""
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                # Approximate CJK character width as 2
                w = sum(2 if ord(c) > 127 else 1 for c in str(cell))
                widths[i] = max(widths[i], w)
    return widths


def render_markdown_table(headers: List[str], rows: List[List[Any]],
                          max_width: int = 80) -> str:
    """Render a table as well-formatted Markdown."""
    if not headers:
        return ""

    # Convert all cells to strings
    str_rows = [[_format_cell(cell) for cell in row] for row in rows]

    # Build separator line
    sep = "|" + "|".join("---" for _ in headers) + "|"

    # Build header line
    header_line = "| " + " | ".join(headers) + " |"

    # Build data lines
    data_lines = []
    for row in str_rows:
        # Pad row to match header count
        padded = row + ["-"] * (len(headers) - len(row))
        line = "| " + " | ".join(padded[:len(headers)]) + " |"
        data_lines.append(line)

    # Assemble
    lines = [header_line, sep] + data_lines
    return "\n".join(lines)


def render_html_table(headers: List[str], rows: List[List[Any]],
                      table_type: str = "custom",
                      title: str = "") -> str:
    """Render a table as a styled HTML document."""
    css = """
    <style>
        table.eng-table {
            border-collapse: collapse;
            width: 100%;
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            font-size: 13px;
            margin: 16px 0;
        }
        table.eng-table th {
            background: #1a5276;
            color: #fff;
            padding: 8px 10px;
            text-align: center;
            font-weight: 600;
            border: 1px solid #1a5276;
        }
        table.eng-table td {
            padding: 6px 10px;
            border: 1px solid #d5dbdb;
            text-align: center;
        }
        table.eng-table tr:nth-child(even) td {
            background: #f2f4f4;
        }
        table.eng-table tr:nth-child(odd) td {
            background: #fff;
        }
        table.eng-table td:first-child {
            text-align: left;
            font-weight: 500;
            background: #eaf2f8;
        }
        table.eng-table tr.category-row td {
            background: #d4e6f1;
            font-weight: 700;
            text-align: left;
            padding: 5px 10px;
            font-size: 12px;
            letter-spacing: 1px;
        }
        .highlight-best { color: #27ae60; font-weight: 700; }
        .highlight-warn { color: #e67e22; font-weight: 700; }
        .pipe-ok { color: #27ae60; }
        .pipe-warn { color: #e67e22; }
        .pipe-bad { color: #e74c3c; }
        .title { font-size: 16px; font-weight: 700; color: #1a5276; margin: 12px 0 4px; }
    </style>
    """

    html_rows = []
    for row in rows:
        str_cells = [_format_cell(cell) for cell in row]
        padded = str_cells + ["-"] * (len(headers) - len(str_cells))
        cells = padded[:len(headers)]

        # Check if this is a category row
        is_category = False
        cat_text = ""
        if len(row) >= 1 and isinstance(row[0], str) and row[0].startswith("**"):
            # Single bold cell or bold first cell with empty rest → category row
            all_rest_empty = all(
                not isinstance(c, str) or c.strip() == ""
                for c in row[1:]
            )
            if all_rest_empty or len(row) == 1:
                is_category = True
                cat_text = row[0].strip("*")

        if is_category:
            html_rows.append(
                '<tr class="category-row"><td colspan="{}">{}</td></tr>'.format(
                    len(headers), cat_text))
        else:
            tds = []
            for j, cell in enumerate(cells):
                cls = ""
                if "✅" in cell:
                    cls = ' class="highlight-best"'
                elif "⭐" in cell:
                    cls = ' class="highlight-best"'
                elif "▼" in cell:
                    cls = ' class="highlight-best"'
                tds.append(f"<td{cls}>{cell}</td>")
            html_rows.append("<tr>" + "".join(tds) + "</tr>")

    ths = "".join(f"<th>{h}</th>" for h in headers)
    title_html = f'<div class="title">{title}</div>' if title else ""

    return f"""{css}
{title_html}
<table class="eng-table">
<thead><tr>{ths}</tr></thead>
<tbody>
{chr(10).join(html_rows)}
</tbody>
</table>"""


# =============================================================================
# Table type: comparison (方案对比表)
# =============================================================================

# Regex patterns for auto-highlight detection
LOWER_IS_BETTER = re.compile(
    r'(投资|价格|费用|成本|电耗|能耗|压降|阻力|损耗|损失|'
    r'NPSHr?|汽蚀余量|温升|重量|体积|占地|投资额|年费用|'
    r'单重|总重|比摩阻|摩阻|压损|功率)',
    re.IGNORECASE
)

HIGHER_IS_BETTER = re.compile(
    r'(效率|扬程|周期|寿命|时间|流量|出力|能力|'
    r'可靠性|可用率|换热系数|传热系数)',
    re.IGNORECASE
)

PRESSURE_DROP = re.compile(
    r'(压降|压损|阻力降|比摩阻|摩阻|压力损失|△P|ΔP|dP)',
    re.IGNORECASE
)


def _parse_numeric(value: str) -> Optional[float]:
    """Extract numeric value from a cell string. Returns None if non-numeric."""
    if not isinstance(value, str):
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    # Try to extract a number from the string
    cleaned = value.replace(",", "").replace(" ", "").replace("~", "")
    # Handle percentage
    if cleaned.endswith("%"):
        cleaned = cleaned[:-1]
    match = re.match(r'^([\d.]+)', cleaned)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None


def _process_comparison_rows(headers: List[str],
                              rows: List[Union[List, Dict]]) -> List[List]:
    """
    Process comparison rows: normalize format and apply auto-highlighting.
    Returns processed rows ready for rendering.

    Supports two row formats:
    1. List: ["参数名", "值A", "值B", ...]
    2. Dict with "category" key for section headers, and column-name keys for data
    """
    if len(headers) < 2:
        return [[str(r)] for r in rows]

    processed_rows = []

    for row in rows:
        if isinstance(row, dict):
            if "category" in row:
                cat_name = row["category"]
                sep_cells = [f"**{cat_name}**"] + [""] * (len(headers) - 1)
                processed_rows.append(sep_cells)
                continue

            # Build row from dict
            if "name" in row or "item" in row or "参数" in row:
                name = row.get("name") or row.get("item") or row.get("参数") or ""
                cells = [name]
                for h in headers[1:]:
                    cells.append(row.get(h, ""))
                processed_rows.append(cells)
                continue

            # Fallback: use dict keys matching header names
            cells = [row.get(h, "") for h in headers]
            processed_rows.append(cells)

        elif isinstance(row, list):
            processed_rows.append(list(row))
        else:
            processed_rows.append([str(row)])

    # Auto-highlighting pass
    _apply_auto_highlight(headers, processed_rows)
    return processed_rows


def _apply_auto_highlight(headers: List[str], processed_rows: List[List]) -> None:
    """Apply auto-highlight emoji indicators to best values in each comparison row."""
    if len(headers) < 2:
        return

    for col_idx in range(1, len(headers)):
        values = []
        for r in processed_rows:
            if len(r) > col_idx and not (len(r) > 0 and isinstance(r[0], str) and r[0].startswith("**")):
                val_str = str(r[col_idx]) if col_idx < len(r) else ""
                num = _parse_numeric(val_str)
                values.append((r, col_idx, num))

        if not values:
            continue

        for row_data, c_idx, num_val in values:
            if num_val is None:
                continue
            row_label = str(row_data[0]) if row_data else ""

            # Find all numeric values in the same row across columns
            row_numeric = []
            for r2 in processed_rows:
                if len(r2) > 0 and str(r2[0]) == row_label:
                    for j in range(1, len(headers)):
                        if j < len(r2):
                            n2 = _parse_numeric(str(r2[j]))
                            if n2 is not None:
                                row_numeric.append((j, n2, r2))
                    break

            if len(row_numeric) < 2:
                continue

            # Decide direction
            if PRESSURE_DROP.search(row_label):
                indicator = "▼"
                best_fn = min
            elif LOWER_IS_BETTER.search(row_label):
                indicator = "✅"
                best_fn = min
            elif HIGHER_IS_BETTER.search(row_label):
                indicator = "⭐"
                best_fn = max
            else:
                continue

            # Find best value
            best_val = best_fn(n for _, n, _ in row_numeric)
            best_count = sum(1 for _, n, _ in row_numeric if n == best_val)
            if best_count != 1:
                continue

            # Apply indicator
            for j, n, r2 in row_numeric:
                if n == best_val and j == c_idx:
                    cell = str(r2[j])
                    if indicator not in cell:
                        r2[j] = f"{cell} {indicator}"


def generate_comparison_table(headers: List[str],
                               rows: List[Union[List, Dict]]) -> str:
    """Generate a comparison table with auto-highlighting."""
    processed_rows = _process_comparison_rows(headers, rows)
    return render_markdown_table(headers, processed_rows)


# =============================================================================
# Table type: summary (工况汇总表)
# =============================================================================

def generate_summary_table(headers: List[str],
                            rows: List[Union[List, Dict]]) -> str:
    """
    Generate a parameter summary table across operating conditions.

    Auto-adds a units column if not present.
    """
    processed_rows = []

    for row in rows:
        if isinstance(row, dict):
            cells = [row.get("参数") or row.get("参数名称") or row.get("item", "")]
            for h in headers[1:]:
                cells.append(row.get(h, row.get("值", "")))
            processed_rows.append(cells)
        elif isinstance(row, list):
            processed_rows.append(list(row))
        else:
            processed_rows.append([str(row)])

    return render_markdown_table(headers, processed_rows)


# =============================================================================
# Table type: material (材料表)
# =============================================================================

MATERIAL_HEADERS = ["序号", "名称", "规格", "材质", "单位", "数量", "单重(kg)", "总重(kg)", "备注"]


def generate_material_table(headers: List[str],
                             rows: List[Union[List, Dict]]) -> str:
    """
    Generate a material take-off table.

    Auto-calculates total weight (总重 = 数量 * 单重).
    """
    if not headers:
        headers = list(MATERIAL_HEADERS)

    processed_rows = []
    total_weight = 0.0

    for row in rows:
        if isinstance(row, dict):
            cells = []
            for h in headers:
                val = row.get(h, "")
                cells.append(val)
            # Auto-calculate total weight
            qty_idx = _find_column_index(headers, ["数量"])
            unit_wt_idx = _find_column_index(headers, ["单重(kg)", "单重"])
            total_wt_idx = _find_column_index(headers, ["总重(kg)", "总重"])

            if qty_idx is not None and unit_wt_idx is not None and total_wt_idx is not None:
                qty = _parse_numeric(str(cells[qty_idx])) if qty_idx < len(cells) else None
                unit_wt = _parse_numeric(str(cells[unit_wt_idx])) if unit_wt_idx < len(cells) else None
                if qty is not None and unit_wt is not None:
                    total = qty * unit_wt
                    cells[total_wt_idx] = round(total, 1)
                    total_weight += total

            processed_rows.append(cells)
        elif isinstance(row, list):
            cells = list(row)
            qty_idx = _find_column_index(headers, ["数量"])
            unit_wt_idx = _find_column_index(headers, ["单重(kg)", "单重"])
            total_wt_idx = _find_column_index(headers, ["总重(kg)", "总重"])

            if qty_idx is not None and unit_wt_idx is not None and total_wt_idx is not None:
                if qty_idx < len(cells) and unit_wt_idx < len(cells):
                    qty = _parse_numeric(str(cells[qty_idx]))
                    unit_wt = _parse_numeric(str(cells[unit_wt_idx]))
                    if qty is not None and unit_wt is not None:
                        total = qty * unit_wt
                        if total_wt_idx < len(cells):
                            cells[total_wt_idx] = round(total, 1)
                        else:
                            while len(cells) <= total_wt_idx:
                                cells.append("")
                            cells[total_wt_idx] = round(total, 1)
                        total_weight += total

            processed_rows.append(cells)
        else:
            processed_rows.append([str(row)])

    # Add total row
    if total_weight > 0:
        total_row = [""] * len(headers)
        total_row[0] = "**合计**"
        total_wt_idx = _find_column_index(headers, ["总重(kg)", "总重"])
        if total_wt_idx is not None:
            total_row[total_wt_idx] = f"**{round(total_weight, 1)}**"
        processed_rows.append(total_row)

    return render_markdown_table(headers, processed_rows)


def _find_column_index(headers: List[str], names: List[str]) -> Optional[int]:
    """Find the index of a column by possible name variants."""
    for i, h in enumerate(headers):
        for name in names:
            if name in h or h in name:
                return i
    return None


# =============================================================================
# Table type: pipe-select (管径比选, built-in template)
# =============================================================================

PIPE_HEADERS = ["管径", "外径×壁厚(mm)", "内径(mm)", "流速(m/s)",
                "Re (×10⁴)", "比摩阻(Pa/m)", "比摩阻(Pa/100m)", "推荐"]


def _compute_pipe_properties(dn: int, od: float, wall: float, flow: float,
                              medium: str, pressure: float, temperature: float) -> dict:
    """
    Compute hydraulic properties for a pipe diameter.

    Args:
        dn: Nominal diameter
        od: Outer diameter in mm
        wall: Wall thickness in mm
        flow: Flow rate in m³/h (liquid) or Nm³/h (gas)
        medium: "liquid" or "gas"
        pressure: Pressure in MPa (abs, for gas)
        temperature: Temperature in °C

    Returns dict with velocity, Re, specific pressure drop
    """
    id_mm = od - 2 * wall  # inner diameter in mm
    id_m = id_mm / 1000.0
    area = math.pi * (id_m ** 2) / 4.0

    if medium == "liquid":
        # Liquid: flow is m³/h
        flow_m3s = flow / 3600.0
        velocity = flow_m3s / area if area > 0 else 0

        # Properties: water at ~20°C
        rho = 1000.0  # kg/m³
        mu = 0.001    # Pa·s (dynamic viscosity)
        roughness = 0.000045  # m (commercial steel)

    else:  # gas
        # Gas: flow is in Nm³/h, need actual flow rate
        # P_abs = pressure + 0.101325 (gauge to absolute)
        p_abs = (pressure + 0.101325) * 1e6  # Pa
        t_abs = temperature + 273.15  # K
        # Assuming air: R = 287 J/(kg·K)
        rho = p_abs / (287.0 * t_abs)

        # Actual volumetric flow
        # Normal conditions: 0°C, 101.325 kPa
        rho_n = 101325.0 / (287.0 * 273.15)  # ~1.293 kg/m³
        mass_flow = flow * rho_n / 3600.0  # kg/s
        flow_m3s = mass_flow / rho if rho > 0 else 0
        velocity = flow_m3s / area if area > 0 else 0

        # Gas viscosity ~ 0.018 cP = 1.8e-5 Pa·s
        mu = 1.8e-5
        roughness = 0.000045

    # Reynolds number
    re_num = rho * velocity * id_m / mu if mu > 0 else 0

    # Darcy friction factor (Swamee-Jain approximation)
    if re_num > 0 and id_m > 0:
        f = 0.25 / (math.log10(roughness / (3.7 * id_m) + 5.74 / (re_num ** 0.9))) ** 2
    else:
        f = 0.02

    # Specific pressure drop (Pa/m): dP/L = f * (L/D) * (ρ * v² / 2)
    dp_per_m = f * (1.0 / id_m) * (rho * velocity ** 2 / 2.0) if id_m > 0 else 0

    return {
        "dn": dn,
        "od": od,
        "wall": wall,
        "id_mm": round(id_mm, 1),
        "velocity": round(velocity, 2),
        "re": round(re_num / 10000, 2),  # in 10⁴
        "dp_pa_m": round(dp_per_m, 1),
        "dp_pa_100m": round(dp_per_m * 100, 0),
    }


def _velocity_check(velocity: float, medium: str) -> str:
    """Check if velocity is within recommended range."""
    if medium == "liquid":
        if 1.0 <= velocity <= 3.5:
            return "✅ 推荐"
        elif 0.5 <= velocity < 1.0 or 3.5 < velocity <= 5.0:
            return "⚠ 可用"
        else:
            return "❌ 偏出"
    else:  # gas
        if 10 <= velocity <= 30:
            return "✅ 推荐"
        elif 5 <= velocity < 10 or 30 < velocity <= 45:
            return "⚠ 可用"
        else:
            return "❌ 偏出"


# Standard pipe data: DN -> (OD mm, wall thickness mm)
# Sch40 for DN<=300, Sch20 for larger
PIPE_DIMENSIONS = {
    25:  (33.7, 3.2),
    32:  (42.4, 3.6),
    40:  (48.3, 3.7),
    50:  (60.3, 3.9),
    65:  (73.0, 5.2),
    80:  (88.9, 5.5),
    100: (114.3, 6.0),
    125: (139.7, 6.6),
    150: (168.3, 7.1),
    200: (219.1, 8.2),
    250: (273.0, 9.3),
    300: (323.9, 10.3),
    350: (355.6, 9.5),
    400: (406.4, 9.5),
    450: (457.0, 9.5),
    500: (508.0, 9.5),
    600: (610.0, 9.5),
}


def generate_pipe_select_table(medium: str = "liquid",
                                flow: float = 50.0,
                                pressure: float = 0.0,
                                temperature: float = 20.0,
                                dn_list: Optional[List[int]] = None) -> str:
    """
    Generate pipe diameter comparison table.

    Args:
        medium: "liquid" or "gas"
        flow: Flow rate in m³/h (liquid) or Nm³/h (gas)
        pressure: Pressure in MPa(g) for gas
        temperature: Temperature in °C
        dn_list: List of DN sizes to compare
    """
    if dn_list is None:
        if medium == "liquid":
            dn_list = [50, 65, 80, 100, 125, 150, 200]
        else:
            dn_list = [25, 40, 50, 65, 80, 100, 125, 150]

    headers = list(PIPE_HEADERS)
    rows = []

    for dn in dn_list:
        if dn not in PIPE_DIMENSIONS:
            continue
        od, wall = PIPE_DIMENSIONS[dn]
        props = _compute_pipe_properties(dn, od, wall, flow, medium, pressure, temperature)
        rec = _velocity_check(props["velocity"], medium)

        row = [
            f"DN{dn}",
            f"{od}×{wall}",
            str(props["id_mm"]),
            str(props["velocity"]),
            str(props["re"]),
            str(props["dp_pa_m"]),
            str(props["dp_pa_100m"]),
            rec,
        ]
        rows.append(row)

    # Add flow condition header as a note
    if medium == "liquid":
        condition_note = f"介质: 液体 | 流量: {flow} m³/h | 温度: {temperature}°C"
        recommended_range = "推荐流速: 1.5~3.0 m/s"
    else:
        condition_note = f"介质: 气体 | 流量: {flow} Nm³/h | 压力: {pressure} MPa(g) | 温度: {temperature}°C"
        recommended_range = "推荐流速: 15~30 m/s"

    title = f"### 管径比选 — {condition_note}"
    footer = f"\n*{recommended_range}*"

    return title + "\n\n" + render_markdown_table(headers, rows) + "\n" + footer


# =============================================================================
# Table type: equipment-list (设备一览表)
# =============================================================================

EQUIPMENT_HEADERS = ["序号", "设备位号", "设备名称", "规格型号", "数量", "材质", "备注"]


def generate_equipment_list(headers: List[str],
                             rows: List[Union[List, Dict]]) -> str:
    """Generate an equipment list table."""
    if not headers:
        headers = list(EQUIPMENT_HEADERS)

    processed_rows = []
    for row in rows:
        if isinstance(row, dict):
            cells = [row.get(h, "") for h in headers]
            processed_rows.append(cells)
        elif isinstance(row, list):
            processed_rows.append(list(row))
        else:
            processed_rows.append([str(row)])

    return render_markdown_table(headers, processed_rows)


# =============================================================================
# Table type: custom (自定义表)
# =============================================================================

def generate_custom_table(headers: List[str],
                           rows: List[Union[List, Dict]]) -> str:
    """Generate a custom free-form table."""
    processed_rows = []
    for row in rows:
        if isinstance(row, dict):
            cells = [row.get(h, "") for h in headers]
            processed_rows.append(cells)
        elif isinstance(row, list):
            processed_rows.append(list(row))
        else:
            processed_rows.append([str(row)])

    return render_markdown_table(headers, processed_rows)


# =============================================================================
# Data loading
# =============================================================================

def load_data(input_file: Optional[str] = None,
              data_str: Optional[str] = None) -> Dict[str, Any]:
    """Load table data from file or JSON string.

    Returns a dict with "headers" and "rows" keys, or a list of row objects.
    """
    if input_file:
        with open(input_file, "r", encoding="utf-8") as f:
            raw = json.load(f)
    elif data_str:
        raw = json.loads(data_str)
    else:
        return {"headers": [], "rows": []}

    # Normalize: support both {headers, rows} dict and bare list
    if isinstance(raw, list):
        # Bare list of rows: auto-detect headers from first row keys
        if raw and isinstance(raw[0], dict):
            headers = list(raw[0].keys())
            rows = raw
        else:
            headers = []
            rows = raw
        return {"headers": headers, "rows": rows}

    if isinstance(raw, dict):
        headers = raw.get("headers", raw.get("header", []))
        rows = raw.get("rows", raw.get("data", []))
        return {"headers": headers, "rows": rows}

    return {"headers": [], "rows": []}


# =============================================================================
# Main dispatch
# =============================================================================

TABLE_GENERATORS = {
    "comparison": generate_comparison_table,
    "summary": generate_summary_table,
    "material": generate_material_table,
    "pipe-select": None,  # handled specially
    "equipment-list": generate_equipment_list,
    "custom": generate_custom_table,
}


def generate(args) -> str:
    """Main generation dispatch."""
    table_type = args.type

    if table_type == "pipe-select":
        medium = getattr(args, "medium", "liquid")
        flow = getattr(args, "flow", 50.0)
        pressure = getattr(args, "pressure", 0.0)
        temperature = getattr(args, "temperature", 20.0)
        dn_str = getattr(args, "dns", "")
        dn_list = None
        if dn_str:
            dn_list = [int(x.strip()) for x in dn_str.split(",") if x.strip().isdigit()]
        return generate_pipe_select_table(
            medium=medium, flow=flow, pressure=pressure,
            temperature=temperature, dn_list=dn_list)

    # For built-in templates without external data
    data = load_data(getattr(args, "input", None), getattr(args, "data", None))
    headers = data["headers"]
    rows = data["rows"]

    generator = TABLE_GENERATORS.get(table_type)
    if generator is None:
        return f"Error: unknown table type '{table_type}'. Supported: {list(TABLE_GENERATORS.keys())}"

    return generator(headers, rows)


def _make_html(headers, rows, table_type, title=""):
    """Generate HTML from data for the HTML output path.

    For comparison tables, applies auto-highlighting before rendering.
    """
    # For comparison: process rows with highlighting first
    if table_type == "comparison":
        processed_rows = _process_comparison_rows(headers, rows)
    else:
        processed_rows = []
        for row in rows:
            if isinstance(row, dict):
                if "category" in row:
                    processed_rows.append([f"**{row['category']}**"])
                    continue
                cells = [row.get("参数") or row.get("name") or row.get("item", "")]
                for h in headers[1:]:
                    cells.append(row.get(h, ""))
                processed_rows.append(cells)
            elif isinstance(row, list):
                processed_rows.append(list(row))
            else:
                processed_rows.append([str(row)])

    return render_html_table(headers, processed_rows, table_type, title)


def main():
    # Ensure UTF-8 output on Windows
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    parser = argparse.ArgumentParser(
        description="数据表格生成器 — 从结构化数据生成专业工程表格",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python gen.py --type comparison --input data.json --output result.md
  python gen.py --type summary --data '[{"参数":"流量","工况1":"50","工况2":"80"}]'
  python gen.py --type pipe-select --medium gas --flow 2000 --pressure 1.0
  python gen.py --type pipe-select --output result.md
  python gen.py --type material --input bom.json --output bom.html --format html
        """,
    )

    parser.add_argument("--type", "-t", required=True,
                        choices=["comparison", "summary", "material",
                                 "pipe-select", "equipment-list", "custom"],
                        help="表格类型")

    # Data source (mutually exclusive)
    data_group = parser.add_mutually_exclusive_group()
    data_group.add_argument("--input", "-i",
                            help="JSON 输入文件路径")
    data_group.add_argument("--data", "-d",
                            help="JSON 字符串输入 (inline)")

    # Output options
    parser.add_argument("--output", "-o",
                        help="输出文件路径 (不指定则打印到 stdout)")
    parser.add_argument("--format", "-f", choices=["md", "html"], default="md",
                        help="输出格式: md (Markdown) 或 html (默认: md)")

    # Pipe-select specific options
    parser.add_argument("--medium", choices=["liquid", "gas"], default="liquid",
                        help="介质类型 (pipe-select 模板使用, 默认: liquid)")
    parser.add_argument("--flow", type=float, default=50.0,
                        help="流量: m³/h (液体) 或 Nm³/h (气体)")
    parser.add_argument("--pressure", "-p", type=float, default=0.0,
                        help="压力 MPa(g) (气体管径比选使用)")
    parser.add_argument("--temperature", type=float, default=20.0,
                        help="温度 °C (默认: 20)")
    parser.add_argument("--dns", type=str, default="",
                        help="管径列表，逗号分隔 (如: 50,80,100,150)")

    parser.add_argument("--title", default="",
                        help="表格标题 (HTML 格式使用)")

    args = parser.parse_args()

    # Validate: non-pipe-select types need data
    if args.type != "pipe-select" and not args.input and not args.data:
        parser.error(f"--type {args.type} 需要 --input 或 --data 提供数据")

    markdown = generate(args)

    if args.format == "html":
        # For HTML, re-process with HTML render
        if args.type == "pipe-select":
            # pipe-select has its own output format, just wrap in HTML
            title = args.title or f"管径比选表"
            css = """<style>
                body { font-family: 'Segoe UI','Microsoft YaHei',sans-serif; padding: 20px; color: #333; }
                table { border-collapse: collapse; width: 100%; margin: 16px 0; }
                th { background: #1a5276; color: #fff; padding: 8px 10px; text-align: center; border:1px solid #1a5276; }
                td { padding: 6px 10px; border: 1px solid #d5dbdb; text-align: center; }
                tr:nth-child(even) td { background: #f2f4f4; }
                td:first-child { text-align: left; font-weight: 500; background: #eaf2f8; }
                h3 { color: #1a5276; }
                .pipe-ok { color: #27ae60; font-weight: 700; }
                .pipe-warn { color: #e67e22; font-weight: 700; }
                .pipe-bad { color: #e74c3c; }
            </style>"""
            # Convert markdown table to HTML
            lines = markdown.strip().split("\n")
            html_parts = [css, f"<h2>{title}</h2>"]

            in_table = False
            for line in lines:
                if line.startswith("|"):
                    cells = [c.strip() for c in line.split("|")[1:-1]]
                    if not in_table:
                        html_parts.append("<table><thead><tr>")
                        html_parts.append("".join(f"<th>{c}</th>" for c in cells))
                        html_parts.append("</tr></thead><tbody>")
                        in_table = "---" not in line
                    elif all(c.replace("-", "").strip() == "" for c in cells):
                        continue  # separator line
                    else:
                        tds = []
                        for c in cells:
                            cls = ""
                            if "✅" in c:
                                cls = ' class="pipe-ok"'
                            elif "⚠" in c:
                                cls = ' class="pipe-warn"'
                            elif "❌" in c:
                                cls = ' class="pipe-bad"'
                            tds.append(f"<td{cls}>{c}</td>")
                        html_parts.append("<tr>" + "".join(tds) + "</tr>")
                elif in_table and not line.startswith("|"):
                    html_parts.append("</tbody></table>")
                    in_table = False
                elif line.startswith("*"):
                    html_parts.append(f"<p><em>{line.strip('* ')}</em></p>")

            if in_table:
                html_parts.append("</tbody></table>")

            markdown = "\n".join(html_parts)
        else:
            data = load_data(args.input, args.data)
            title = args.title or f"{args.type} 表格"
            markdown = _make_html(data["headers"], data["rows"], args.type, title)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"表格已保存到: {args.output}", file=sys.stderr)
    else:
        print(markdown)


if __name__ == "__main__":
    main()
