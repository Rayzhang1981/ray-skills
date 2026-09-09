#!/usr/bin/env python3
"""
管道压降计算器 (Pipe Pressure Drop Calculator)
基于 Darcy-Weisbach 方程 + Colebrook-White 摩擦系数公式。

支持液体单相流和气体单相流（不可压缩假设，ΔP/P < 10%）。
"""

import argparse
import math
import sys
import io

# 确保 stdout/stderr 使用 UTF-8，避免 Windows GBK 终端编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# 理想气体常数
R_GAS = 8.314  # J/(mol·K)


def friction_factor_colebrook(re, rr, max_iter=50, tol=1e-8):
    """
    Colebrook-White 公式求解摩擦系数 f，使用 Newton-Raphson 迭代。

    参数
    ----
    re : float
        雷诺数。
    rr : float
        相对粗糙度 ε/D。
    max_iter : int
        最大迭代次数。
    tol : float
        收敛容差。

    返回
    ----
    f : float
        Darcy 摩擦系数。
    """
    if re <= 0:
        return 0.0

    # 层流：f = 64/Re
    if re < 2100:
        return 64.0 / re

    # 湍流区 / 过渡区：Newton-Raphson 迭代
    f = 0.02  # 初始猜测
    for _ in range(max_iter):
        sqrt_f = math.sqrt(f)
        left = 1.0 / sqrt_f
        term1 = rr / 3.7
        term2 = 2.51 / (re * sqrt_f)
        val = left + 2.0 * math.log10(term1 + term2)

        # 牛顿法更新 f
        # d(val)/df 用于 Newton 步长
        dval_df = (-0.5 / (f * sqrt_f)
                   - (2.0 * 0.5) / (math.log(10) * (term1 + term2))
                   * (2.51 / re) * (-0.5 / (f * sqrt_f)))
        # 更稳健的数值求导：直接用解析式太复杂，用公式变换
        # 令 g(f) = 1/√f + 2·log₁₀[ε/(3.7D) + 2.51/(Re·√f)] = 0
        # 使用更简洁的迭代策略：不动点迭代 f ← 0.25 / log₁₀²(...)
        # 这是 Colebrook-White 的一个等价形式，收敛极快
        f_new = 0.25 / (math.log10(term1 + term2) ** 2)
        if abs(f_new - f) < tol:
            return f_new
        f = f_new

    # 未收敛，返回最后迭代值并发出警告
    print(f"警告: Colebrook-White 迭代未收敛 (Re={re:.0f}, ε/D={rr:.6f}), f≈{f:.6f}", file=sys.stderr)
    return f


def compute_gas_density(mw, t_celsius, p_kpag):
    """
    由理想气体状态方程计算气体密度。

    参数
    ----
    mw : float
        分子量 (g/mol)。
    t_celsius : float
        温度 (°C)。
    p_kpag : float
        表压 (kPaG)，内部转为绝压 Pa。

    返回
    ----
    rho : float
        密度 (kg/m³)。
    """
    t_kelvin = t_celsius + 273.15
    p_abs_pa = (p_kpag + 101.325) * 1000.0  # kPaG → Pa abs
    mw_kg = mw / 1000.0  # g/mol → kg/mol
    return (p_abs_pa * mw_kg) / (R_GAS * t_kelvin)


def compute_pressure_drop(args):
    """
    核心计算逻辑。

    返回计算结果字典，供格式化输出使用。
    """
    # -------- 单位换算 --------
    diameter_m = args.id / 1000.0          # mm → m
    length_m = args.length                 # m
    roughness_mm = args.roughness          # mm
    roughness_m = roughness_mm / 1000.0    # mm → m
    viscosity_cp = args.viscosity          # cP
    viscosity_pas = viscosity_cp / 1000.0  # cP → Pa·s

    # 确定密度
    if args.gas:
        if args.density is not None:
            density = args.density
        elif args.mw is not None and args.T is not None and args.P is not None:
            density = compute_gas_density(args.mw, args.T, args.P)
            print(f"由理想气体方程计算密度: {density:.2f} kg/m³")
        else:
            print("错误: 气体计算需提供 --density 或 (--mw + --T + --P)", file=sys.stderr)
            sys.exit(1)
    else:
        density = args.density
        if density is None:
            print("错误: 液体计算需提供 --density", file=sys.stderr)
            sys.exit(1)

    # 确定体积流量 (m³/s)
    unit = args.unit.lower()
    if unit in ("m3/h", "m³/h"):
        q_m3h = args.flow
        q_m3s = q_m3h / 3600.0
    elif unit in ("kg/h",):
        mass_flow_kgh = args.flow
        q_m3s = mass_flow_kgh / (density * 3600.0) if density > 0 else 0.0
    else:
        print(f"错误: 不支持的流量单位 '{args.unit}'，请使用 m3/h 或 kg/h", file=sys.stderr)
        sys.exit(1)

    # -------- 基本参数 --------
    area = math.pi * diameter_m ** 2 / 4.0
    if area <= 0 or q_m3s <= 0:
        # 零流量或零管径 — 输出全零
        return {
            "velocity": 0.0,
            "re": 0.0,
            "regime": "零流量",
            "friction_factor": 0.0,
            "dp_straight": 0.0,
            "dp_fittings": 0.0,
            "dp_total": 0.0,
            "dp_per_100m": 0.0,
        }

    velocity = q_m3s / area

    # 警告：流速过高可能引起冲蚀
    if not args.gas and velocity > 5.0:
        print(f"警告: 流速 {velocity:.2f} m/s > 5 m/s，液流可能引起管道冲蚀", file=sys.stderr)
    if args.gas and velocity > 30.0:
        print(f"警告: 气速 {velocity:.2f} m/s > 30 m/s，可能造成噪声/振动", file=sys.stderr)

    # -------- 雷诺数与流态 --------
    re = density * velocity * diameter_m / viscosity_pas if viscosity_pas > 0 else 0

    if re <= 2100:
        regime = "层流 (Laminar)"
    elif re < 4000:
        regime = "过渡流 (Transitional)"
    else:
        regime = "湍流 (Turbulent)"

    # -------- 摩擦系数 --------
    rr = roughness_m / diameter_m if diameter_m > 0 else 0.0
    f = friction_factor_colebrook(re, rr)

    # -------- 压降计算 --------
    # 动态压力项
    dynamic_pressure = density * velocity ** 2 / 2.0  # Pa

    # 直管压降 (Pa → kPa)
    dp_straight_pa = f * (length_m / diameter_m) * dynamic_pressure if diameter_m > 0 else 0.0
    dp_straight = dp_straight_pa / 1000.0

    # 管件压降
    k_total = args.fittings
    dp_fittings = (k_total * dynamic_pressure) / 1000.0  # Pa → kPa

    dp_total = dp_straight + dp_fittings

    # 单位长度压降 (kPa/100m)
    dp_per_100m = (dp_total / length_m * 100.0) if length_m > 0 else 0.0

    # 气体可压缩性校验
    if args.gas and args.P is not None and args.P > 0:
        p_abs_kpa = args.P + 101.325
        if dp_total / p_abs_kpa > 0.10:
            print("注意: ΔP/P > 10%，不可压缩假设可能不准确，建议分段计算或使用可压缩流模型", file=sys.stderr)

    return {
        "velocity": velocity,
        "re": re,
        "regime": regime,
        "friction_factor": f,
        "dp_straight": dp_straight,
        "dp_fittings": dp_fittings,
        "dp_total": dp_total,
        "dp_per_100m": dp_per_100m,
    }


def format_results(r):
    """格式化打印计算结果。"""
    print("=" * 60)
    print("管道压降计算结果")
    print("=" * 60)

    # 流速
    print(f"流速:          {r['velocity']:.2f} m/s")

    # 雷诺数 (整数格式)
    if r['re'] >= 1e6:
        print(f"雷诺数 Re:     {r['re']:,.0f}")
    else:
        print(f"雷诺数 Re:     {r['re']:,.0f}")

    # 流态
    print(f"流态:          {r['regime']}")

    # 摩擦系数
    if r['re'] < 2100:
        print(f"摩擦系数 f:    {r['friction_factor']:.4f}  (f = 64/Re)")
    else:
        print(f"摩擦系数 f:    {r['friction_factor']:.4f}")

    print()
    print(f"直管压降:      {r['dp_straight']:.2f} kPa")
    print(f"管件压降:      {r['dp_fittings']:.2f} kPa")
    print(f"总压降:        {r['dp_total']:.2f} kPa")
    print(f"单位压降:      {r['dp_per_100m']:.2f} kPa/100m")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="管道压降计算器 - Darcy-Weisbach + Colebrook-White",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
常用管壁绝对粗糙度 (ε, mm):
  碳钢新管:       0.046
  不锈钢:          0.015
  镀锌钢管:        0.15
  混凝土管:        0.3 - 3.0
  PVC / 塑料管:    0.0015
  铸铁管:          0.26

示例:
  # 液体管道
  python calc.py --flow 50 --unit m3/h --id 100 --density 1000 \\
      --viscosity 1.0 --length 100 --roughness 0.046 --fittings 5.0

  # 气体管道 (理想气体方程自动计算密度)
  python calc.py --flow 500 --unit kg/h --id 200 --density 2.5 \\
      --viscosity 0.018 --length 50 --gas

  # 气体管道 (提供操作条件，自动计算密度)
  python calc.py --flow 100 --unit m3/h --id 150 --viscosity 0.018 \\
      --length 80 --gas --mw 28.96 --T 25 --P 200
        """,
    )

    # ---- 基本参数 ----
    parser.add_argument("--flow", type=float, required=True,
                        help="流量 (体积 m³/h 或质量 kg/h，取决于 --unit)")
    parser.add_argument("--unit", type=str, default="m3/h",
                        help="流量单位: m3/h (体积) 或 kg/h (质量, 需配合 --density)")
    parser.add_argument("--id", type=float, required=True,
                        help="管道内径 (mm)")
    parser.add_argument("--density", type=float, default=None,
                        help="介质密度 (kg/m³)。液体必须提供；气体可选（若无则从理想气体方程计算）")
    parser.add_argument("--viscosity", type=float, required=True,
                        help="动力粘度 (cP)")
    parser.add_argument("--length", type=float, required=True,
                        help="直管段长度 (m)")
    parser.add_argument("--roughness", type=float, default=0.046,
                        help="管壁绝对粗糙度 (mm)，默认 0.046 (碳钢新管)")
    parser.add_argument("--fittings", type=float, default=0.0,
                        help="管件总 K 系数 (无量纲)，默认 0")

    # ---- 气体专用参数 ----
    parser.add_argument("--gas", action="store_true",
                        help="标记为气体流动。启用后可使用 --mw, --T, --P 计算密度")
    parser.add_argument("--mw", type=float, default=None,
                        help="气体分子量 (g/mol)，仅气体模式")
    parser.add_argument("--T", type=float, default=None,
                        help="气体温度 (°C)，仅气体模式")
    parser.add_argument("--P", type=float, default=None,
                        help="操作压力 (kPaG)，仅气体模式")

    args = parser.parse_args()

    # 基本参数校验
    if args.flow <= 0:
        print("错误: 流量必须 > 0", file=sys.stderr)
        sys.exit(1)
    if args.id <= 0:
        print("错误: 管径必须 > 0", file=sys.stderr)
        sys.exit(1)
    if args.length <= 0:
        print("错误: 管长必须 > 0", file=sys.stderr)
        sys.exit(1)
    if args.viscosity <= 0:
        print("错误: 粘度必须 > 0", file=sys.stderr)
        sys.exit(1)

    results = compute_pressure_drop(args)
    format_results(results)


if __name__ == "__main__":
    main()
