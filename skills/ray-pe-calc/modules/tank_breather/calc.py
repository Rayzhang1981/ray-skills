#!/usr/bin/env python3
"""储罐呼吸量计算器 — API 2000 (7th Edition, 2014).

Naming convention:
- Nm³/h: normal cubic meters per hour at 0 °C, 1 atm (API 2000 standard reference)
- Actual m³/h: at flowing temperature / pressure; this tool works exclusively in Nm³/h.

Example:
    python calc.py --volume 500 --flashpoint high --pump_in 50 --pump_out 50
"""

import argparse
import math
import sys

# Ensure UTF-8 output on Windows consoles
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# API 2000 coefficients (vertical cone/dome roof, volume ≤ 31800 m³)
# ---------------------------------------------------------------------------
COEFF = {
    "high": {"th_out": 1.01, "th_in": 0.845, "desc": "高 (≥37.8°C)"},
    "low": {"th_out": 1.69, "th_in": 0.845, "desc": "低 (<37.8°C)"},
}

WORK_COEFF = {"out": 2.02, "in": 0.94}  # Nm³/h per m³/h of liquid pumped

# ---------------------------------------------------------------------------
# Standard breather valve capacities (approximate, Nm³/h @ set pressure)
# ---------------------------------------------------------------------------
VALVE_CAPS = {
    "2": 34,
    "3": 85,
    "4": 184,
    "6": 425,
    "8": 793,
    "10": 1274,
    "12": 1982,
}
VALVE_SIZES = sorted(VALVE_CAPS.items(), key=lambda x: x[1])  # ascending


def select_valve(q_required: float) -> tuple[int, str, float]:
    """Return (quantity, size_str, per_valve_capacity_Nm3h) to meet q_required."""
    if q_required <= 0:
        return 0, "-", 0.0

    # Single valve
    for size_str, cap in VALVE_SIZES:
        if cap >= q_required:
            return 1, f'{size_str}"', cap

    # Multiple of largest size
    max_size, max_cap = VALVE_SIZES[-1]
    n = math.ceil(q_required / max_cap)
    return n, f'{max_size}"', max_cap


def fire_estimate(volume: float, diam: float | None, height: float | None) -> float | None:
    """API 2000 emergency venting (fire case).

    Returns Q_fire in Nm³/h, or None if estimation is unreliable / skipped.
    """
    if volume <= 0:
        return None

    if diam is not None and height is not None and diam > 0 and height > 0:
        # Wetted wall area — assume 70% of shell height is wetted
        a_wetted = math.pi * diam * (0.7 * height)
    else:
        # Rough approximation from volume alone
        a_wetted = 4.5 * (volume ** 0.67)

    # API 2000 fire formula (adequate drainage, no insulation)
    q_scfh = 21.0 * (a_wetted * 10.764) ** 0.82  # m² → ft²
    q_nm3h = q_scfh * 0.0283168  # SCFH → Nm³/h
    return round(q_nm3h, 1)


def fmt_flow(v: float) -> str:
    return f"{v:.1f}"


# ---------------------------------------------------------------------------
def main() -> None:
    p = argparse.ArgumentParser(
        description="储罐呼吸量计算器 — API 2000 (7th Ed.) 常压储罐呼吸阀选型",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--volume", "-V", type=float, required=True, help="储罐容积 (m³)")
    p.add_argument(
        "--flashpoint",
        "-f",
        choices=("high", "low"),
        default="high",
        help="闪点等级: high (≥37.8°C) / low (<37.8°C)",
    )
    p.add_argument("--pump_in", type=float, default=0.0, help="最大进料速率 (m³/h)")
    p.add_argument("--pump_out", type=float, default=0.0, help="最大出料速率 (m³/h)")
    p.add_argument("--insulated", action="store_true", default=False, help="是否保温")
    p.add_argument(
        "--ifactor",
        type=float,
        default=None,
        help="保温削减系数 (默认保温=0.3, 非保温=1.0)",
    )
    p.add_argument("--tank_diameter", "-D", type=float, default=None, help="储罐直径 (m, 用于火灾计算)")
    p.add_argument("--tank_height", "-H", type=float, default=None, help="储罐高度 (m, 用于火灾计算)")
    args = p.parse_args()

    vol = args.volume
    fp = args.flashpoint
    insulated = args.insulated

    # Insulation factor
    if args.ifactor is not None:
        ifactor = args.ifactor
    else:
        ifactor = 0.3 if insulated else 1.0

    # -----------------------------------------------------------------------
    # Thermal breathing  (Nm³/h)
    # -----------------------------------------------------------------------
    coeff = COEFF[fp]
    th_out = coeff["th_out"] * (vol ** 0.7) * ifactor
    th_in = coeff["th_in"] * (vol ** 0.7) * ifactor

    # -----------------------------------------------------------------------
    # Working breathing  (Nm³/h)
    # -----------------------------------------------------------------------
    work_out = WORK_COEFF["out"] * args.pump_in
    work_in = WORK_COEFF["in"] * args.pump_out

    # -----------------------------------------------------------------------
    # Total
    # -----------------------------------------------------------------------
    total_out = th_out + work_out
    total_in = th_in + work_in

    # -----------------------------------------------------------------------
    # Valve selection
    # -----------------------------------------------------------------------
    n_out, sz_out, cap_out = select_valve(total_out)
    n_in, sz_in, cap_in = select_valve(total_in)

    # -----------------------------------------------------------------------
    # Fire case (emergency venting)
    # -----------------------------------------------------------------------
    q_fire = fire_estimate(vol, args.tank_diameter, args.tank_height)
    fire_note = "" if args.tank_diameter and args.tank_height else " (基于容积估算)"

    # -----------------------------------------------------------------------
    # Output
    # -----------------------------------------------------------------------
    sep = "=" * 70
    print(sep)
    print("储罐呼吸量计算 (API 2000)")
    print(sep)

    # Inputs
    print("【输入参数】")
    print(f"  储罐容积: {vol:.0f} m³")
    print(f"  闪点等级: {coeff['desc']}")
    print(f"  保温: {'是' if insulated else '否'}{' (系数=' + str(ifactor) + ')' if insulated else ''}")
    print(f"  最大进料: {args.pump_in:.1f} m³/h")
    print(f"  最大出料: {args.pump_out:.1f} m³/h")
    if args.tank_diameter and args.tank_height:
        print(f"  储罐尺寸: D={args.tank_diameter:.1f}m, H={args.tank_height:.1f}m")

    print()
    print("【热呼吸量】")
    print(f"  呼出: {fmt_flow(th_out)} Nm³/h")
    print(f"  吸入: {fmt_flow(th_in)} Nm³/h")

    print()
    print("【工作呼吸量】")
    print(f"  呼出 (泵入): {fmt_flow(work_out)} Nm³/h")
    print(f"  吸入 (泵出): {fmt_flow(work_in)} Nm³/h")

    print()
    print("【总呼吸量】")
    print(f"  总呼出: {fmt_flow(total_out)} Nm³/h")
    print(f"  总吸入: {fmt_flow(total_in)} Nm³/h")

    print()
    print("【选型建议】")
    if n_out == 0:
        print("  呼出侧: 无需呼吸阀")
    else:
        print(f"  呼出侧: {n_out} × {sz_out} 呼吸阀 (单阀容量 {fmt_flow(cap_out)} Nm³/h)")

    if n_in == 0:
        print("  吸入侧: 无需呼吸阀")
    else:
        print(f"  吸入侧: {n_in} × {sz_in} 呼吸阀 (单阀容量 {fmt_flow(cap_in)} Nm³/h)")

    if q_fire is not None:
        print()
        print("【火灾工况参考】")
        print(f"  紧急放空量: ~{fmt_flow(q_fire)} Nm³/h{fire_note}，需独立核算")
        print("  推荐: 独立紧急放空人孔或大尺寸呼吸阀")

    print()
    print(sep)
    print("⚠️  注意事项:")
    print("  1. 呼吸阀设定压力 ≤ 储罐设计压力")
    print("  2. 呼吸阀数量 ≥ 2 时需考虑冗余")
    print("  3. 最终选型需参照制造商实际性能曲线")
    print("  4. 火灾工况需设置独立紧急放空装置")
    print(sep)


if __name__ == "__main__":
    main()
