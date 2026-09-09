#!/usr/bin/env python3
"""
计算书生成器 (Calculation Report Generator)

Generates structured engineering calculation reports in design institute style.
Supports Markdown and HTML output with built-in templates for common calculations.
"""

import argparse
import json
import sys
import os
import io
from datetime import datetime

# Handle Windows console encoding for CJK characters
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer, encoding="utf-8", errors="replace"
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.buffer, encoding="utf-8", errors="replace"
    )


# ---------------------------------------------------------------------------
# Built-in templates
# ---------------------------------------------------------------------------

TEMPLATES = {
    "pump-npsh": {
        "title": "离心泵 NPSH 计算书",
        "project": "某化工装置泵选型校核",
        "doc_no": "CAL-P-NPSH-001",
        "standard": "API 610 / GB/T 5656 / ANSI/HI 9.6.1",
        "inputs": [
            {"name": "流量 Q", "value": "", "unit": "m³/h", "note": "额定工况"},
            {"name": "介质", "value": "", "unit": "—", "note": ""},
            {"name": "密度 ρ", "value": "", "unit": "kg/m³", "note": "操作温度"},
            {"name": "饱和蒸气压 Pv", "value": "", "unit": "kPa(a)", "note": "操作温度"},
            {"name": "吸入压力 P₁", "value": "", "unit": "kPa(a)", "note": "吸入侧"},
            {"name": "吸入管径", "value": "", "unit": "mm", "note": "内径"},
            {"name": "安装高度 z", "value": "", "unit": "m", "note": "+液面在泵上，-液面在泵下"},
            {"name": "NPSHr", "value": "", "unit": "m", "note": "泵样本数据"},
            {"name": "安全裕量", "value": "0.5", "unit": "m", "note": "按 API 610"},
        ],
        "steps": [
            {
                "title": "吸入管流速",
                "formula": "v = Q / A = 4Q / (3600 × π × d²)",
                "calc": "",
                "result": "",
                "check": "v 应在经济流速范围内（液体吸入管 0.5~2.0 m/s）",
            },
            {
                "title": "吸入管路沿程摩阻 hf",
                "formula": "hf = f × (L/d) × v²/(2g)",
                "calc": "",
                "result": "",
                "check": "",
            },
            {
                "title": "NPSHa 计算",
                "formula": "NPSHa = (P₁ - Pv) / (ρ × g) + v²/(2g) - hf + z",
                "calc": "",
                "result": "",
                "check": "NPSHa ≥ NPSHr + 裕量 (≥0.5m)",
            },
            {
                "title": "汽蚀裕量校核",
                "formula": "ΔNPSH = NPSHa - NPSHr",
                "calc": "",
                "result": "",
                "check": "ΔNPSH ≥ 安全裕量 0.5m",
            },
        ],
        "conclusion": "待填入数据后得出结论。",
        "attachments": ["泵性能曲线", "管道 ISO 图"],
    },
    "safety-valve": {
        "title": "安全阀喉径计算书",
        "project": "安全阀选型计算",
        "doc_no": "CAL-PSV-001",
        "standard": "API 520 Part I / GB/T 12241",
        "inputs": [
            {"name": "介质", "value": "", "unit": "—", "note": "如蒸汽、空气、水等"},
            {"name": "所需泄放量 W", "value": "", "unit": "kg/h", "note": "最大工况"},
            {"name": "整定压力 P_set", "value": "", "unit": "MPa(g)", "note": ""},
            {"name": "背压 Pb", "value": "", "unit": "MPa(g)", "note": "叠加背压"},
            {"name": "排放温度 T", "value": "", "unit": "°C", "note": ""},
            {"name": "绝热指数 k", "value": "", "unit": "—", "note": "仅用于气体/蒸汽"},
            {"name": "压缩因子 Z", "value": "1.0", "unit": "—", "note": "仅用于气体/蒸汽"},
        ],
        "steps": [
            {
                "title": "确定排放压力 Pd",
                "formula": "Pd = 1.1 × P_set + 0.1013 （气相）\n或 Pd = 1.2 × P_set + 0.1013 （液相）",
                "calc": "",
                "result": "",
                "check": "",
            },
            {
                "title": "判定流型",
                "formula": "Pb/Pd 与临界压力比比较",
                "calc": "",
                "result": "",
                "check": "亚临界 / 临界流动",
            },
            {
                "title": "计算所需喉径面积 A",
                "formula": "气体: A = W / (C × Kd × Pd × Kb × Kc) × √(T×Z/M)\n液体: A = W / (Kd × Kw × Kc × Kv × √(ρ×(Pd-Pb)))",
                "calc": "",
                "result": "",
                "check": "",
            },
            {
                "title": "选型校核",
                "formula": "选取 API 标准孔口代号，A_selected ≥ A_required",
                "calc": "",
                "result": "",
                "check": "API D~T 口系列，需确认制造厂实际面积",
            },
        ],
        "conclusion": "待填入数据后得出结论。",
        "attachments": ["泄放工况分析表", "安全阀样本"],
    },
    "heat-exchanger": {
        "title": "换热器面积计算书",
        "project": "换热器选型计算",
        "doc_no": "CAL-EX-001",
        "standard": "GB/T 151 / TEMA",
        "inputs": [
            {"name": "热负荷 Q", "value": "", "unit": "kW", "note": "工艺侧"},
            {"name": "热流进口温度 T₁,in", "value": "", "unit": "°C", "note": ""},
            {"name": "热流出口温度 T₁,out", "value": "", "unit": "°C", "note": ""},
            {"name": "冷流进口温度 T₂,in", "value": "", "unit": "°C", "note": ""},
            {"name": "冷流出口温度 T₂,out", "value": "", "unit": "°C", "note": ""},
            {"name": "总传热系数 U", "value": "", "unit": "W/(m²·K)", "note": "经验值或校核值"},
            {"name": "污垢热阻 Rf", "value": "", "unit": "m²·K/W", "note": "按 TEMA 推荐"},
        ],
        "steps": [
            {
                "title": "对数平均温差 LMTD",
                "formula": "LMTD = (ΔT₁ - ΔT₂) / ln(ΔT₁/ΔT₂)\nΔT₁ = T₁,in - T₂,out\nΔT₂ = T₁,out - T₂,in",
                "calc": "",
                "result": "",
                "check": "若 ΔT₁/ΔT₂ < 2，可取算术平均温差",
            },
            {
                "title": "温差校正系数 Ft",
                "formula": "查取校正系数（与换热器型式、流道数有关）",
                "calc": "",
                "result": "",
                "check": "Ft 一般 ≥ 0.8",
            },
            {
                "title": "计算所需面积 A",
                "formula": "A = Q / (U × LMTD × Ft)",
                "calc": "",
                "result": "",
                "check": "",
            },
            {
                "title": "考虑污垢裕量",
                "formula": "A_design = A × (1 + 裕量%)",
                "calc": "",
                "result": "",
                "check": "通常取 10%~25% 设计裕量",
            },
        ],
        "conclusion": "待填入数据后得出结论。",
        "attachments": ["换热器数据表", "物性数据来源"],
    },
    "pipe-drop": {
        "title": "管道压降计算书",
        "project": "管道水力计算",
        "doc_no": "CAL-PIPE-001",
        "standard": "GB 50316 / ASME B31.3",
        "inputs": [
            {"name": "介质", "value": "", "unit": "—", "note": ""},
            {"name": "流量 Q", "value": "", "unit": "m³/h", "note": "操作工况"},
            {"name": "密度 ρ", "value": "", "unit": "kg/m³", "note": "操作温度"},
            {"name": "黏度 μ", "value": "", "unit": "mPa·s", "note": "操作温度"},
            {"name": "管径 D", "value": "", "unit": "mm", "note": "内径"},
            {"name": "管长 L", "value": "", "unit": "m", "note": "含当量长度"},
            {"name": "绝对粗糙度 ε", "value": "", "unit": "mm", "note": "碳钢 0.05，不锈钢 0.015"},
        ],
        "steps": [
            {
                "title": "流速计算",
                "formula": "v = 4Q / (3600 × π × D²)",
                "calc": "",
                "result": "",
                "check": "液体推荐 1~3 m/s，气体推荐 5~30 m/s",
            },
            {
                "title": "雷诺数 Re",
                "formula": "Re = ρ × v × D / μ",
                "calc": "",
                "result": "",
                "check": "Re<2000 层流，Re>4000 湍流",
            },
            {
                "title": "摩擦系数 f（Colebrook-White）",
                "formula": "1/√f = -2 log₁₀[ ε/(3.7D) + 2.51/(Re×√f) ]",
                "calc": "",
                "result": "",
                "check": "",
            },
            {
                "title": "沿程压降 ΔP",
                "formula": "ΔP = f × (L/D) × (ρ × v² / 2)",
                "calc": "",
                "result": "",
                "check": "ΔP 应在工艺允许范围内",
            },
        ],
        "conclusion": "待填入数据后得出结论。",
        "attachments": ["管道 ISO 图"],
    },
    "tank-breather": {
        "title": "储罐呼吸量计算书",
        "project": "储罐呼吸阀选型",
        "doc_no": "CAL-TANK-001",
        "standard": "API 2000 / GB/T 50761",
        "inputs": [
            {"name": "储罐容积", "value": "", "unit": "m³", "note": ""},
            {"name": "储罐内径", "value": "", "unit": "m", "note": ""},
            {"name": "储罐高度", "value": "", "unit": "m", "note": ""},
            {"name": "介质闪点", "value": "", "unit": "°C", "note": "影响呼出量系数"},
            {"name": "泵入流量", "value": "", "unit": "m³/h", "note": ""},
            {"name": "泵出流量", "value": "", "unit": "m³/h", "note": ""},
            {"name": "设计温度范围", "value": "", "unit": "°C", "note": "最低~最高"},
            {"name": "保温状况", "value": "", "unit": "—", "note": "有保温/无保温"},
        ],
        "steps": [
            {
                "title": "热呼吸吸入量",
                "formula": "Vi_thermal = C × V_tank^0.7 × Ri\nC: 系数（按储罐容积查 API 2000 表）\nRi: 保温折减系数",
                "calc": "",
                "result": "",
                "check": "按 API 2000 表 1 查取 C 值",
            },
            {
                "title": "热呼吸呼出量",
                "formula": "Vo_thermal = 0.5 × Vi_thermal （闪点≥37.8°C 保温）\nVo_thermal = Vi_thermal （闪点<37.8°C 无保温）",
                "calc": "",
                "result": "",
                "check": "按 API 2000 表 2 确定系数",
            },
            {
                "title": "工作呼吸吸入量",
                "formula": "Vi_working = 0.94 × Qpump_out （m³/h → Nm³/h 空气）",
                "calc": "",
                "result": "",
                "check": "",
            },
            {
                "title": "工作呼吸呼出量",
                "formula": "Vo_working = 2.02 × Qpump_in （m³/h → Nm³/h 空气）",
                "calc": "",
                "result": "",
                "check": "挥发性液体取大值",
            },
            {
                "title": "总呼吸量",
                "formula": "Vi_total = Vi_thermal + Vi_working\nVo_total = Vo_thermal + Vo_working",
                "calc": "",
                "result": "",
                "check": "",
            },
            {
                "title": "呼吸阀选型",
                "formula": "按总吸入量/呼出量选型，阀口径满足 ± 10% 设定压力时全量排放",
                "calc": "",
                "result": "",
                "check": "吸入量按呼出阀的 50% 能力校核",
            },
        ],
        "conclusion": "待填入数据后得出结论。",
        "attachments": ["储罐数据表", "呼吸阀样本"],
    },
}

# ---------------------------------------------------------------------------
# Sample data for --sample mode
# ---------------------------------------------------------------------------

SAMPLE_DATA = {
    "title": "离心泵 NPSH 计算书",
    "project": "某化工装置循环水泵选型",
    "doc_no": "CAL-P-001",
    "standard": "API 610 / GB/T 5656",
    "calculator": "张三",
    "date": datetime.today().strftime("%Y-%m-%d"),
    "inputs": [
        {"name": "流量", "value": "50", "unit": "m³/h", "note": "额定工况"},
        {"name": "介质", "value": "水", "unit": "—", "note": "80°C"},
        {"name": "密度", "value": "972", "unit": "kg/m³", "note": "80°C"},
        {"name": "饱和蒸气压", "value": "47.4", "unit": "kPa(a)", "note": "80°C"},
        {"name": "吸入压力", "value": "101.3", "unit": "kPa(a)", "note": "常压罐"},
        {"name": "吸入管径", "value": "DN100", "unit": "mm", "note": "内径100mm"},
        {"name": "安装高度", "value": "+2.0", "unit": "m", "note": "液面在泵上"},
        {"name": "NPSHr", "value": "3.0", "unit": "m", "note": "泵样本数据"},
    ],
    "steps": [
        {
            "title": "吸入管流速",
            "formula": "v = Q / A",
            "calc": "v = 50/3600 / (π × 0.1²/4)",
            "result": "v = 1.77 m/s",
            "check": "✅  在推荐经济流速 1.5~3.0 m/s 内",
        },
        {
            "title": "NPSHa 计算",
            "formula": "NPSHa = (P₁-Pv)/(ρg) + v²/(2g) - hf + z",
            "calc": (
                "NPSHa = (101325-47400)/(972×9.81)"
                " + 1.77²/(2×9.81) - 0.42 + 2.0"
            ),
            "result": "NPSHa = 7.3 m",
            "check": "NPSHa - NPSHr = 4.3m ≥ 0.5m ✅  满足",
        },
    ],
    "conclusion": (
        "NPSHa = 7.3 m > NPSHr + 0.5m = 3.5 m，汽蚀余量充裕，泵选型满足要求。"
    ),
    "attachments": ["泵性能曲线 (供应商提供)", "管道 ISO 图"],
}

# ---------------------------------------------------------------------------
# HTML CSS template
# ---------------------------------------------------------------------------

HTML_CSS = """
<style>
  body { font-family: "SimSun", "Microsoft YaHei", serif; max-width: 210mm;
         margin: 0 auto; padding: 20px; color: #333; line-height: 1.8;
         background: #fff; }
  h1 { text-align: center; font-size: 22pt; border-bottom: 3px double #000;
       padding-bottom: 12px; margin-bottom: 24px; }
  h2 { font-size: 14pt; border-bottom: 1px solid #999; padding-bottom: 4px;
       margin-top: 28px; }
  h3 { font-size: 12pt; margin-top: 20px; }
  table { border-collapse: collapse; width: 100%; margin: 12px 0; }
  th, td { border: 1px solid #666; padding: 6px 10px; text-align: left; }
  th { background: #f0f0f0; font-weight: bold; }
  .header-table td:first-child { font-weight: bold; width: 120px;
                                 background: #f8f8f8; }
  .formula { background: #f5f5f5; border-left: 3px solid #333;
             padding: 8px 14px; margin: 8px 0; font-family: "Courier New", monospace; }
  .calc { background: #fffef0; border-left: 3px solid #c90;
          padding: 8px 14px; margin: 8px 0; font-family: "Courier New", monospace; }
  .result { font-weight: bold; color: #1565c0; margin: 6px 0; }
  .check { color: #2e7d32; margin: 6px 0; }
  .conclusion { background: #e8f5e9; border: 1px solid #81c784;
                padding: 14px 18px; margin: 16px 0; border-radius: 4px; }
  hr { border: none; border-top: 1px solid #ccc; margin: 20px 0; }
  ul { padding-left: 24px; }
  @media print { body { padding: 0; } }
</style>
"""


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_params(params):
    """Check for missing required fields and print warnings."""
    warnings = []
    required = ["title", "inputs", "steps", "conclusion"]
    for key in required:
        if key not in params or not params[key]:
            warnings.append(f"缺少必填字段: {key}")

    if "inputs" in params:
        for i, inp in enumerate(params["inputs"], 1):
            if "name" not in inp or not inp["name"]:
                warnings.append(f"输入条件 #{i} 缺少参数名称")
    if "steps" in params:
        for i, step in enumerate(params["steps"], 1):
            if "title" not in step or not step["title"]:
                warnings.append(f"计算步骤 #{i} 缺少标题")
    return warnings


# ---------------------------------------------------------------------------
# Auto-numbering
# ---------------------------------------------------------------------------

def auto_number_steps(steps):
    """Auto-number steps that don't already have a number prefix."""
    numbered = []
    for i, step in enumerate(steps, 1):
        s = dict(step)
        title = s.get("title", "")
        # Check if already numbered like "步骤N:" or "4.1" pattern
        already = False
        for char in title[:4]:
            if char.isdigit():
                already = True
                break
        if not already:
            s["title"] = "步骤{}: {}".format(i, title)
        numbered.append(s)
    return numbered


# ---------------------------------------------------------------------------
# Markdown report generator
# ---------------------------------------------------------------------------

def generate_report(params):
    """Generate a complete Markdown calculation report from params dict."""
    lines = []

    # ---- Section 1: Cover / Header ----
    title = params.get("title", "计算书")
    lines.append("# {}".format(title))
    lines.append("")
    lines.append("| 项目 | 内容 |")
    lines.append("|------|------|")
    lines.append("| 项目名称 | {} |".format(params.get("project", "—")))
    lines.append("| 文档编号 | {} |".format(params.get("doc_no", "—")))
    lines.append("| 依据标准 | {} |".format(params.get("standard", "—")))
    lines.append("| 计算 | {} |".format(params.get("calculator", "—")))
    lines.append("| 日期 | {} |".format(params.get("date", "—")))
    lines.append("| 版本 | Rev.0 |")
    lines.append("")
    lines.append("---")
    lines.append("")

    # ---- Section 2: 设计依据 ----
    lines.append("## 2. 设计依据")
    lines.append("")
    standard = params.get("standard", "")
    if standard:
        lines.append("依据标准：{}".format(standard))
    else:
        lines.append("依据标准：（未指定）")
    lines.append("")

    # ---- Section 3: 输入条件 ----
    lines.append("## 3. 输入条件")
    lines.append("")
    inputs = params.get("inputs", [])
    if inputs:
        lines.append("| 序号 | 参数 | 数值 | 单位 | 备注 |")
        lines.append("|------|------|------|------|------|")
        for idx, inp in enumerate(inputs, 1):
            name = inp.get("name", "")
            value = inp.get("value", "")
            unit = inp.get("unit", "—")
            note = inp.get("note", "")
            lines.append(
                "| {} | {} | {} | {} | {} |".format(
                    idx, name, value, unit, note
                )
            )
    else:
        lines.append("（未提供输入条件）")
    lines.append("")

    # ---- Section 4: 计算过程 ----
    lines.append("## 4. 计算过程")
    lines.append("")
    steps = params.get("steps", [])
    steps = auto_number_steps(steps)
    for idx, step in enumerate(steps, 1):
        title = step.get("title", "步骤{}".format(idx))
        lines.append("### 4.{} {}".format(idx, title))
        lines.append("")

        formula = step.get("formula", "")
        if formula:
            lines.append("**计算公式：**  `{}`".format(formula))
            lines.append("")

        calc = step.get("calc", "")
        if calc:
            lines.append("**代入计算：**  {}".format(calc))
            lines.append("")

        result = step.get("result", "")
        if result:
            lines.append("**计算结果：**  {}".format(result))
            lines.append("")

        check = step.get("check", "")
        if check:
            lines.append("**校验：**  {}".format(check))
            lines.append("")

    # ---- Section 5: 计算结论 ----
    lines.append("## 5. 计算结论")
    lines.append("")
    conclusion = params.get("conclusion", "（未提供结论）")
    lines.append(conclusion)
    lines.append("")

    # ---- Section 6: 附件 ----
    lines.append("## 6. 附件")
    lines.append("")
    attachments = params.get("attachments", [])
    if attachments:
        for att in attachments:
            lines.append("- {}".format(att))
    else:
        lines.append("- （无附件）")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML report generator
# ---------------------------------------------------------------------------

def generate_html_report(params):
    """Generate a styled HTML calculation report."""
    lines = []

    lines.append("<!DOCTYPE html>")
    lines.append("<html lang=\"zh-CN\">")
    lines.append("<head>")
    lines.append("<meta charset=\"UTF-8\">")
    lines.append("<title>{}</title>".format(params.get("title", "计算书")))
    lines.append(HTML_CSS)
    lines.append("</head>")
    lines.append("<body>")

    # ---- Header ----
    title = params.get("title", "计算书")
    lines.append("<h1>{}</h1>".format(title))
    lines.append("<table class=\"header-table\">")
    for label, key in [
        ("项目名称", "project"),
        ("文档编号", "doc_no"),
        ("依据标准", "standard"),
        ("计算", "calculator"),
        ("日期", "date"),
        ("版本", None),
    ]:
        if key is None:
            lines.append(
                "<tr><td>版本</td><td>Rev.0</td></tr>"
            )
        else:
            lines.append(
                "<tr><td>{}</td><td>{}</td></tr>".format(
                    label, params.get(key, "—")
                )
            )
    lines.append("</table>")
    lines.append("<hr>")

    # ---- 设计依据 ----
    lines.append("<h2>2. 设计依据</h2>")
    standard = params.get("standard", "")
    lines.append("<p>依据标准：{}</p>".format(standard or "（未指定）"))

    # ---- 输入条件 ----
    lines.append("<h2>3. 输入条件</h2>")
    inputs = params.get("inputs", [])
    if inputs:
        lines.append("<table>")
        lines.append("<tr><th>序号</th><th>参数</th><th>数值</th><th>单位</th><th>备注</th></tr>")
        for idx, inp in enumerate(inputs, 1):
            lines.append(
                "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                    idx,
                    inp.get("name", ""),
                    inp.get("value", ""),
                    inp.get("unit", "—"),
                    inp.get("note", ""),
                )
            )
        lines.append("</table>")
    else:
        lines.append("<p>（未提供输入条件）</p>")

    # ---- 计算过程 ----
    lines.append("<h2>4. 计算过程</h2>")
    steps = params.get("steps", [])
    steps = auto_number_steps(steps)
    for idx, step in enumerate(steps, 1):
        title = step.get("title", "步骤{}".format(idx))
        lines.append("<h3>4.{} {}</h3>".format(idx, title))

        formula = step.get("formula", "")
        if formula:
            lines.append("<div class=\"formula\"><strong>计算公式：</strong><br>")
            for line in formula.split("\n"):
                lines.append("<code>{}</code><br>".format(line))
            lines.append("</div>")

        calc = step.get("calc", "")
        if calc:
            lines.append(
                "<div class=\"calc\"><strong>代入计算：</strong><br>{}</div>".format(
                    calc
                )
            )

        result = step.get("result", "")
        if result:
            lines.append(
                "<p class=\"result\"><strong>计算结果：</strong>{}</p>".format(result)
            )

        check = step.get("check", "")
        if check:
            lines.append(
                "<p class=\"check\"><strong>校验：</strong>{}</p>".format(check)
            )

    # ---- 计算结论 ----
    lines.append("<h2>5. 计算结论</h2>")
    conclusion = params.get("conclusion", "（未提供结论）")
    lines.append("<div class=\"conclusion\">{}</div>".format(conclusion))

    # ---- 附件 ----
    lines.append("<h2>6. 附件</h2>")
    attachments = params.get("attachments", [])
    if attachments:
        lines.append("<ul>")
        for att in attachments:
            lines.append("<li>{}</li>".format(att))
        lines.append("</ul>")
    else:
        lines.append("<p>（无附件）</p>")

    lines.append("</body>")
    lines.append("</html>")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        description="计算书生成器 (Calculation Report Generator)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python gen.py --sample
  python gen.py --input params.json --output report.md
  python gen.py --input params.json --format html --output report.html
  python gen.py --template pump-npsh --output 泵NPSH计算书.md
        """,
    )

    parser.add_argument(
        "--input", "-i",
        help="JSON 参数文件路径",
    )
    parser.add_argument(
        "--output", "-o",
        help="输出文件路径（默认 stdout）",
    )
    parser.add_argument(
        "--title",
        help="计算书标题（覆盖 JSON 中的 title）",
    )
    parser.add_argument(
        "--standard",
        help="依据标准（覆盖 JSON 中的 standard）",
    )
    parser.add_argument(
        "--template", "-t",
        choices=list(TEMPLATES.keys()),
        help="使用内置模板: {}".format(", ".join(TEMPLATES.keys())),
    )
    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="列出所有可用模板",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["md", "html"],
        default="md",
        help="输出格式: md (Markdown) 或 html (默认: md)",
    )
    parser.add_argument(
        "--sample", "-s",
        action="store_true",
        help="输出示例计算书到 stdout",
    )
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="跳过输入验证",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # List templates
    if args.list_templates:
        print("可用模板:")
        for name, tpl in TEMPLATES.items():
            print("  {}  — {}".format(name, tpl["title"]))
        return

    # Sample mode
    if args.sample:
        report = generate_report(SAMPLE_DATA)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(report)
            print("示例计算书已保存至: {}".format(args.output), file=sys.stderr)
        else:
            print(report)
        return

    # Load / determine params
    params = {}

    if args.template:
        if args.template not in TEMPLATES:
            print("错误: 未知模板 '{}'".format(args.template), file=sys.stderr)
            sys.exit(1)
        params = dict(TEMPLATES[args.template])
        print("已加载模板: {}".format(args.template), file=sys.stderr)

    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                loaded = json.load(f)
        except FileNotFoundError:
            print("错误: 文件不存在 '{}'".format(args.input), file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print("错误: JSON 解析失败 '{}': {}".format(args.input, e), file=sys.stderr)
            sys.exit(1)
        # Merge: loaded params override template defaults
        params.update(loaded)

    # CLI overrides
    if args.title:
        params["title"] = args.title
    if args.standard:
        params["standard"] = args.standard

    if not params:
        print("错误: 请指定 --input, --template 或 --sample", file=sys.stderr)
        parser.print_help(sys.stderr)
        sys.exit(1)

    # Validate
    if not args.no_validate:
        warnings = validate_params(params)
        for w in warnings:
            print("警告: {}".format(w), file=sys.stderr)

    # Generate
    if args.format == "html":
        output = generate_html_report(params)
    else:
        output = generate_report(params)

    # Write
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print("计算书已保存至: {}".format(args.output), file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
