#!/usr/bin/env python3
"""换热器面积估算器 — 基于 LMTD 法的快速估算工具."""

import argparse
import math
import sys
import io

# Fix Unicode output on Windows (GBK codec)
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
if sys.stderr.encoding != "utf-8":
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


# ---------------------------------------------------------------------------
# U-value presets for common services (W/(m²·°C))
# ---------------------------------------------------------------------------
U_PRESETS = {
    "water-water": 1100,
    "steam-water": 2000,
    "gas-water": 40,
    "gas-gas": 20,
    "organic-condenser": 500,
    "steam-organic": 800,
    "reboiler-steam": 1500,
    "oil-cooler": 200,
}


# ---------------------------------------------------------------------------
# Core calculation functions
# ---------------------------------------------------------------------------

def calc_heat_load(htype, hot_flow, hot_cp, hot_lambda, hot_tin, hot_tout):
    """Calculate heat load Q in kW."""
    if htype == "sensible":
        if hot_cp is None:
            raise ValueError("显热计算需要 --hot_cp (热侧比热容)")
        Q = hot_flow * hot_cp * (hot_tin - hot_tout) / 3600.0
    elif htype in ("condensation", "evaporation"):
        if hot_lambda is None:
            raise ValueError(f"{htype} 计算需要 --hot_lambda (潜热)")
        Q = hot_flow * hot_lambda / 3600.0
    else:
        raise ValueError(f"未知换热类型: {htype}")
    return Q


def calc_lmtd(htype, hot_tin, hot_tout, cold_tin, cold_tout):
    """Calculate LMTD for counter-current flow."""
    if htype in ("condensation", "evaporation"):
        # Isothermal on hot side
        T_hot = hot_tin
        dT1 = T_hot - cold_tout
        dT2 = T_hot - cold_tin
    else:
        dT1 = hot_tin - cold_tout
        dT2 = hot_tout - cold_tin

    if dT1 <= 0 or dT2 <= 0:
        return dT1, dT2, None, True  # temperature cross

    if abs(dT1 - dT2) < 1e-9:
        LMTD = dT1
    else:
        LMTD = (dT1 - dT2) / math.log(dT1 / dT2)

    return dT1, dT2, LMTD, False


def calc_area(Q_kW, U, LMTD, F):
    """Calculate required area in m²."""
    # Q in kW → W:  × 1000
    A = Q_kW * 1000.0 / (U * LMTD * F)
    return A


def calc_design_area(A, margin):
    """Calculate design area with margin."""
    return A * (1.0 + margin / 100.0)


def recommend_type(U):
    """Recommend exchanger type based on U-value."""
    if U <= 100:
        return "板式换热器 或 翅片管式"
    elif U <= 500:
        return "管壳式 (1-2 程)"
    else:
        return "管壳式 或 板式"


def check_temperature(hot_tin, hot_tout, cold_tin, cold_tout):
    """Return (approach, warnings list)."""
    warnings = []
    approach = min(hot_tout - cold_tin, hot_tin - cold_tout)

    if hot_tout <= cold_tin:
        warnings.append("温度交叉！冷侧出口温度高于热侧出口温度，无法实现，需调整参数")
    elif approach < 5:
        warnings.append(f"温端温差过小 ({approach:.1f} °C)，可能需要更大面积或增加换热器台数")
    elif approach < 10:
        warnings.append(f"温端温差偏小 ({approach:.1f} °C)，建议关注")

    return approach, warnings


def check_terminal(hot_tin, cold_tout, hot_tout, cold_tin):
    """Check temperature cross for sensible heat exchangers."""
    if hot_tin <= cold_tout:
        return "⚠️ 温端温差过大警告：热侧进口温度不明显高于冷侧出口，换热驱动力不足"
    return None


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def fmt_num(n):
    """Format number with comma separators for readability."""
    if isinstance(n, float):
        return f"{n:,.1f}" if abs(n) < 10000 else f"{n:,.0f}"
    return str(n)


def print_report(args, htype_label, U, Q, dT1, dT2, LMTD, area, design_area,
                 approach, warnings, recommendation, service_used):
    """Print the estimation report in Chinese."""
    sep = "=" * 70

    print()
    print(sep)
    print("换热器面积估算")
    print(sep)

    # Input parameters
    print("【输入参数】")
    print(f"  换热类型: {htype_label}")
    print(f"  热侧流量: {fmt_num(args.hot_flow)} kg/h")

    if args.type == "sensible":
        print(f"  热侧 Cp: {args.hot_cp} kJ/(kg·°C)")
        print(f"  热侧: {args.hot_tin:.1f} → {args.hot_tout:.1f} °C")
    else:
        print(f"  热侧潜热: {args.hot_lambda} kJ/kg")

    if args.type == "sensible" and args.hot_tin == args.hot_tout:
        pass  # already printed
    elif args.type in ("condensation", "evaporation"):
        print(f"  热侧: {args.hot_tin:.1f} °C (等温{htype_label})")

    print(f"  冷侧: {args.cold_tin:.1f} → {args.cold_tout:.1f} °C")

    svc_tag = f" [{service_used}]" if service_used else ""
    print(f"  U 值: {U} W/(m²·°C){svc_tag}")
    print(f"  F 系数: {args.f_factor:.2f}")
    print(f"  设计裕量: {args.margin}%")

    # Calculation results
    print()
    print("【计算结果】")
    print(f"  热负荷: {Q:.1f} kW")

    if LMTD is None:
        print(f"  温差 ΔT₁: {dT1:.1f} °C")
        print(f"  温差 ΔT₂: {dT2:.1f} °C")
        print(f"  LMTD: 无法计算 (温度交叉)")
        print(f"  所需面积: — m²")
        print(f"  设计面积: — m²")
    else:
        print(f"  温差 ΔT₁: {dT1:.1f} °C")
        print(f"  温差 ΔT₂: {dT2:.1f} °C")
        print(f"  LMTD: {LMTD:.1f} °C")
        print(f"  所需面积: {area:.1f} m²")
        print(f"  设计裕量: {args.margin}%")
        print(f"  设计面积: {design_area:.1f} m²")

    # Temperature checks
    print()
    print("【温度检查】")
    if LMTD is None:
        print("  ❌ 温度交叉！无法实现，需调整参数")
    elif warnings:
        for w in warnings:
            if "过大" in w:
                print(f"  ⚠️  {w}")
            elif "过小" in w or "偏小" in w:
                print(f"  {w}")
    else:
        status = "合理" if approach >= 10 else "可接受"
        print(f"  温端趋近: {approach:.1f} °C  ✅ {status}")

    # Recommendation
    print()
    print("【推荐】")
    print(f"  换热器型式: {recommendation}")
    if LMTD is not None:
        recommended_area = math.ceil(area * (1 + args.margin / 100) / 5) * 5
        print(f"  推荐面积: {recommended_area} m²")

    # Footer
    print()
    print(sep)
    print("⚠️  此为初步估算，详细设计需用 HTRI 或 Aspen EDR 校核。")
    print("   实际 U 值受流速、污垢热阻、壳程结构等影响。")
    print(sep)
    print()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="换热器面积估算器 — 基于 LMTD 法的快速估算",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --type sensible --hot_flow 10000 --hot_cp 4.18 \\
      --hot_tin 120 --hot_tout 80 --cold_tin 30 --cold_tout 70 --u_value 800
  %(prog)s --type condensation --hot_flow 5000 --hot_lambda 2200 \\
      --hot_tin 150 --cold_tin 30 --cold_tout 80 --service steam-water
  %(prog)s --type evaporation --hot_flow 3000 --hot_lambda 500 \\
      --hot_tin -10 --cold_tin 30 --cold_tout 10 --u_value 500
        """,
    )

    # Required arguments
    parser.add_argument("--type", dest="type", required=True,
                        choices=["sensible", "condensation", "evaporation"],
                        help="换热类型: sensible(显热), condensation(冷凝), evaporation(蒸发)")

    # Flow & properties
    parser.add_argument("--hot_flow", type=float, required=True,
                        help="热侧质量流量 (kg/h)")
    parser.add_argument("--hot_cp", type=float, default=None,
                        help="热侧比热容 (kJ/(kg·°C)) — 显热计算必填")
    parser.add_argument("--hot_lambda", type=float, default=None,
                        help="热侧潜热 (kJ/kg) — 冷凝/蒸发计算必填")

    # Temperatures
    parser.add_argument("--hot_tin", type=float, required=True,
                        help="热侧进口温度 (°C)")
    parser.add_argument("--hot_tout", type=float, default=None,
                        help="热侧出口温度 (°C) — 显热必填; 冷凝/蒸发默认等于 hot_tin")
    parser.add_argument("--cold_tin", type=float, required=True,
                        help="冷侧进口温度 (°C)")
    parser.add_argument("--cold_tout", type=float, required=True,
                        help="冷侧出口温度 (°C)")

    # Design parameters
    parser.add_argument("--u_value", type=float, default=None,
                        help="总传热系数 (W/(m²·°C))")
    parser.add_argument("--service", type=str, default=None,
                        choices=list(U_PRESETS.keys()),
                        help="服务类型快捷选择 (自动填充 U 值)")
    parser.add_argument("--margin", type=float, default=15.0,
                        help="设计裕量 %% (默认 15)")
    parser.add_argument("--f_factor", type=float, default=0.9,
                        help="LMTD 修正系数 F (默认 0.9 for 1-2 shell-and-tube)")

    args = parser.parse_args()

    # ---- Validate arguments ----

    # Determine hot_tout
    if args.type == "sensible":
        if args.hot_tout is None:
            print("错误: 显热计算需要 --hot_tout", file=sys.stderr)
            sys.exit(1)
    else:
        # Condensation / evaporation: isothermal, hot_tout defaults to hot_tin
        if args.hot_tout is None:
            args.hot_tout = args.hot_tin
        elif args.hot_tout != args.hot_tin:
            print(f"警告: {args.type} 为等温过程，--hot_tout 将被忽略 (按 hot_tin={args.hot_tin} 计算)",
                  file=sys.stderr)

    # Resolve U value: --u_value takes priority over --service
    service_used = None
    if args.u_value is not None:
        U = args.u_value
    elif args.service is not None:
        U = U_PRESETS[args.service]
        service_used = args.service
    else:
        print("错误: 必须提供 --u_value 或 --service", file=sys.stderr)
        sys.exit(1)

    # Htype label for display
    HTYPE_LABELS = {
        "sensible": "显热加热/冷却",
        "condensation": "冷凝",
        "evaporation": "蒸发",
    }
    htype_label = HTYPE_LABELS[args.type]

    # ---- Calculations ----

    try:
        Q = calc_heat_load(args.type, args.hot_flow, args.hot_cp,
                           args.hot_lambda, args.hot_tin, args.hot_tout)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    dT1, dT2, LMTD, has_cross = calc_lmtd(
        args.type, args.hot_tin, args.hot_tout, args.cold_tin, args.cold_tout)

    if LMTD is not None:
        area = calc_area(Q, U, LMTD, args.f_factor)
        design_area = calc_design_area(area, args.margin)
    else:
        area = None
        design_area = None

    approach, warnings = check_temperature(
        args.hot_tin, args.hot_tout, args.cold_tin, args.cold_tout)

    terminal_warning = check_terminal(
        args.hot_tin, args.cold_tout, args.hot_tout, args.cold_tin)
    if terminal_warning:
        warnings.append(terminal_warning)

    recommendation = recommend_type(U)

    print_report(args, htype_label, U, Q, dT1, dT2, LMTD, area, design_area,
                 approach, warnings, recommendation, service_used)


if __name__ == "__main__":
    main()
