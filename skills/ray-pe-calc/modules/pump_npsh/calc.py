#!/usr/bin/env python3
"""
泵扬程与NPSH计算器 (Centrifugal Pump NPSH & Head Calculator)

计算离心泵的 NPSHa（有效汽蚀余量），与 NPSHr 比较并判断安全裕量，
同时计算总扬程（含吸入管与排出管摩擦损失）。

摩擦系数使用 Colebrook-White 公式 + Newton-Raphson 迭代。
"""

import argparse
import math
import sys
import io

# 确保 Windows GBK 终端下正确输出中文
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------
G = 9.81             # 重力加速度 (m/s²)
PATM_KPA = 101.325   # 标准大气压 (kPa 绝压)


# ---------------------------------------------------------------------------
# 摩擦系数: Colebrook-White Newton-Raphson
# ---------------------------------------------------------------------------

def friction_factor_colebrook(re, rr, max_iter=50, tol=1e-8):
    """
    Colebrook-White 公式求解 Darcy 摩擦系数 f。

    参数
    ----
    re : float  雷诺数
    rr : float  相对粗糙度 ε/D
    max_iter : int  最大迭代次数
    tol : float  收敛容差

    返回
    ----
    f : float  Darcy 摩擦系数
    """
    if re <= 0:
        return 0.0

    # 层流: f = 64/Re
    if re < 2100:
        return 64.0 / re

    # 湍流/过渡区: 不动点迭代
    f = 0.02
    for _ in range(max_iter):
        sqrt_f = math.sqrt(f)
        term1 = rr / 3.7
        term2 = 2.51 / (re * sqrt_f)
        denom = math.log10(term1 + term2)
        if denom == 0:
            return f
        f_new = 0.25 / (denom ** 2)
        if abs(f_new - f) < tol:
            return f_new
        f = f_new

    print(f"警告: Colebrook-White 迭代未收敛 (Re={re:.0f}, ε/D={rr:.6f}), f≈{f:.6f}",
          file=sys.stderr)
    return f


# ---------------------------------------------------------------------------
# 管道流速与压降
# ---------------------------------------------------------------------------

def pipe_hydraulics(flow_m3s, diameter_m, density, viscosity_pas, length_m,
                    roughness_mm):
    """
    计算单段管道的流速和摩擦压降（液柱高度 m）。

    返回
    ----
    (velocity, re, f, hf, velocity_head)
    """
    area = math.pi * diameter_m ** 2 / 4.0
    if area <= 0 or flow_m3s <= 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0

    velocity = flow_m3s / area
    velocity_head = velocity ** 2 / (2 * G)

    # 雷诺数
    if viscosity_pas <= 0:
        re = 0.0
    else:
        re = density * velocity * diameter_m / viscosity_pas

    # 相对粗糙度
    roughness_m = roughness_mm / 1000.0
    rr = roughness_m / diameter_m if diameter_m > 0 else 0.0

    # 摩擦系数
    f = friction_factor_colebrook(re, rr)

    # 压降 (m 液柱)
    if diameter_m > 0:
        hf = f * (length_m / diameter_m) * velocity_head
    else:
        hf = 0.0

    return velocity, re, f, hf, velocity_head


# ---------------------------------------------------------------------------
# 综合计算
# ---------------------------------------------------------------------------

def compute(args):
    """核心计算逻辑。返回结果字典。"""
    # ---- 单位换算 ----
    flow_m3s = args.flow / 3600.0               # m³/h → m³/s
    density = args.density                       # kg/m³
    viscosity_pas = args.viscosity / 1000.0      # cP → Pa·s

    d_suction_m = args.suction_id / 1000.0       # mm → m
    d_discharge_m = args.discharge_id / 1000.0   # mm → m

    suction_pres_pa = args.suction_pres * 1000.0     # kPa abs → Pa abs
    vapor_pres_pa = args.vapor_pres * 1000.0         # kPa abs → Pa abs
    discharge_pres_pag_pa = args.discharge_pres * 1000.0  # kPaG → Pa gauge

    # ---- 吸入侧水力计算 ----
    v_suction, re_suction, f_suction, hf_suction, vel_head_suction = pipe_hydraulics(
        flow_m3s, d_suction_m, density, viscosity_pas,
        args.suction_len, args.roughness
    )

    # ---- 排出侧水力计算 ----
    v_discharge, re_discharge, f_discharge, hf_discharge, vel_head_discharge = pipe_hydraulics(
        flow_m3s, d_discharge_m, density, viscosity_pas,
        args.discharge_len, args.roughness
    )

    # ---- NPSHa 计算 ----
    # NPSHa = (P₁ - Pv)/(ρg) + v²/(2g) - hf_suction + z
    # z: 液面在泵之上为正 (flooded suction)，之下为负 (suction lift)
    pressure_head = (suction_pres_pa - vapor_pres_pa) / (density * G)
    elevation_head = args.elevation
    npsha = pressure_head + vel_head_suction - hf_suction + elevation_head

    # ---- 总扬程计算 ----
    # H = 排出侧表压(m) + 吸入摩擦损失 + 排出摩擦损失
    # 注: 排出侧表压已包含终点的静压头需求
    static_head = discharge_pres_pag_pa / (density * G)
    hf_total = hf_suction + hf_discharge
    total_head = static_head + hf_total

    # ---- 安全裕量 ----
    margin = npsha - args.npshr
    margin_ok = margin >= 0.5

    return {
        # 吸入侧
        "v_suction": v_suction,
        "re_suction": re_suction,
        "f_suction": f_suction,
        "hf_suction": hf_suction,
        "vel_head_suction": vel_head_suction,
        # NPSH
        "npsha": npsha,
        "npshr": args.npshr,
        "margin": margin,
        "margin_ok": margin_ok,
        "pressure_head": pressure_head,
        "elevation_head": elevation_head,
        # 排出侧
        "v_discharge": v_discharge,
        "re_discharge": re_discharge,
        "f_discharge": f_discharge,
        "hf_discharge": hf_discharge,
        "vel_head_discharge": vel_head_discharge,
        # 总扬程
        "static_head": static_head,
        "hf_total": hf_total,
        "total_head": total_head,
    }


# ---------------------------------------------------------------------------
# 格式化输出
# ---------------------------------------------------------------------------

def format_results(r, args):
    """中文化格式化输出计算结果。"""
    print("=" * 70)
    print("泵 NPSH 与扬程计算结果")
    print("=" * 70)

    # ---- 吸入侧 ----
    print("【吸入侧】")
    print(f"  吸入管流速:           {r['v_suction']:.2f} m/s")
    print(f"  吸入管压降 (hf):      {r['hf_suction']:.2f} m")
    print(f"  速度头 (v²/2g):       {r['vel_head_suction']:.2f} m")
    print(f"  液面绝对压力:         {args.suction_pres:.2f} kPa(a)")
    print(f"  饱和蒸气压:           {args.vapor_pres:.2f} kPa(a)")

    z_sign = "+" if args.elevation >= 0 else ""
    z_desc = "液面在泵之上" if args.elevation > 0 else ("液面在泵之下" if args.elevation < 0 else "液面与泵齐平")
    print(f"  安装高度 (z):          {z_sign}{args.elevation:.2f} m ({z_desc})")
    print()

    # ---- NPSH 核算 ----
    print("【NPSH 核算】")
    print(f"  NPSHa:                {r['npsha']:.2f} m")
    print(f"  NPSHr:                {r['npshr']:.2f} m")
    if r["margin"] >= 1.0:
        status = f"✅ 裕量充足"
    elif r["margin"] >= 0.5:
        status = f"⚠️ 裕量偏小，建议进一步核实"
    else:
        status = f"❌ 严重！裕量不足，有汽蚀风险！"
    print(f"  安全裕量 (NPSHa-NPSHr): {r['margin']:.2f} m  {status}")
    print()

    # ---- 排出侧 ----
    print("【排出侧】")
    print(f"  排出管流速:           {r['v_discharge']:.2f} m/s")
    print(f"  排出管压降 (hf):      {r['hf_discharge']:.2f} m")
    print()

    # ---- 总扬程 ----
    print("【总扬程】")
    print(f"  静扬程 (ΔP/ρg):       {r['static_head']:.2f} m")
    print(f"  总摩擦损失:           {r['hf_total']:.2f} m")
    print(f"  总扬程 H:             {r['total_head']:.2f} m")
    print()
    print("=" * 70)

    # ---- 结论 ----
    if r["margin_ok"]:
        print(f"✅ 结论: NPSH 校核通过，裕量充足。泵选型扬程需 ≥ {r['total_head']:.1f} m")
    else:
        print(f"❌ 结论: NPSH 校核失败！裕量 {r['margin']:.2f} m < 0.5 m 最低要求。请重新评估安装高度或管道配置。")
    print("=" * 70)


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="离心泵 NPSH 与扬程计算器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python calc.py --flow 50 --suction_pres 101.325 --vapor_pres 47.4 \\
      --density 972 --suction_id 100 --suction_len 10 --elevation 2.0 \\
      --discharge_pres 500 --discharge_len 50 --discharge_id 80 --npshr 3.0
        """,
    )

    parser.add_argument("--flow", type=float, required=True,
                        help="流量 (m³/h)")
    parser.add_argument("--suction_pres", type=float, default=101.325,
                        help="吸入液面压力 kPa(绝压)，默认 101.325")
    parser.add_argument("--vapor_pres", type=float, required=True,
                        help="操作温度下饱和蒸气压 kPa(绝压)")
    parser.add_argument("--density", type=float, default=1000.0,
                        help="介质密度 (kg/m³)，默认 1000")
    parser.add_argument("--viscosity", type=float, default=1.0,
                        help="动力粘度 (cP)，默认 1.0")
    parser.add_argument("--suction_id", type=float, required=True,
                        help="吸入管内径 (mm)")
    parser.add_argument("--suction_len", type=float, required=True,
                        help="吸入管当量长度，含管件 (m)")
    parser.add_argument("--elevation", type=float, default=0.0,
                        help="液面到泵中心线高差 (m)，正=液面在泵上，负=液面在泵下")
    parser.add_argument("--discharge_pres", type=float, required=True,
                        help="排出侧要求压力 (kPaG)")
    parser.add_argument("--discharge_len", type=float, required=True,
                        help="排出管当量长度，含管件 (m)")
    parser.add_argument("--discharge_id", type=float, required=True,
                        help="排出管内径 (mm)")
    parser.add_argument("--npshr", type=float, required=True,
                        help="泵必需汽蚀余量 NPSHr (m)")
    parser.add_argument("--roughness", type=float, default=0.046,
                        help="管壁粗糙度 (mm)，默认 0.046 (碳钢新管)")

    args = parser.parse_args()

    # 参数校验
    errors = []
    if args.flow <= 0:
        errors.append("流量必须 > 0")
    if args.density <= 0:
        errors.append("密度必须 > 0")
    if args.viscosity <= 0:
        errors.append("粘度必须 > 0")
    if args.suction_id <= 0:
        errors.append("吸入管内径必须 > 0")
    if args.suction_len <= 0:
        errors.append("吸入管长度必须 > 0")
    if args.discharge_id <= 0:
        errors.append("排出管内径必须 > 0")
    if args.discharge_len <= 0:
        errors.append("排出管长度必须 > 0")
    if args.npshr < 0:
        errors.append("NPSHr 不能为负")
    if args.vapor_pres < 0:
        errors.append("饱和蒸气压不能为负")

    if errors:
        for e in errors:
            print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    results = compute(args)
    format_results(results, args)


if __name__ == "__main__":
    main()
