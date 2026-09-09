# -*- coding: utf-8 -*-
"""
control_valve/calc.py — 控制阀口径计算（ISA 75.01.01 / IEC 60534）
自包含实现，不依赖第三方库。支持液体/气体两种工况，输出 Cv 与 Kv。

液体公式（ISA 75.01.01 Eq.1，无闪蒸/阻塞流）：
    Cv = Q * sqrt(Gf / dP)
    Q: 流量 gpm | Gf: 液体比重(水=1) | dP: 阀前后压差 psi

气体公式（ISA 75.01.01 Eq.9/10，一般流量，含 Y 膨胀因子）：
    Q = 1360 * Cv * P1 * Y * sqrt(x / (Gg * T1 * Z))
    x = dP / P1（压降比）| xT 极限压降比（默认 0.7）| Fk = k/1.4
    Y = 1 - x / (3 * Fk * xT)，临界判断：x >= Fk*xT → 用 xT 代 x（阻塞流）

输出：Cv（US gpm）与 Kv（m³/h，Kv = 0.865*Cv）
用法：
  python modules/control_valve/calc.py --fluid liquid --q 500 --gf 0.9 --dp 10
  python modules/control_valve/calc.py --fluid gas --q 5000 --qunit scfh --gg 0.62 \
      --p1 200 --p2 150 --t1 300 --k 1.4 --z 1.0 --xt 0.7
"""
import argparse
import math

GPM_TO_M3H = 0.227124707  # 1 gpm = 0.2271 m³/h
K_V = 0.865              # Cv → Kv 换算（Kv = 0.865 * Cv，1.15 倒数）


def liquid_cv(q_gpm: float, gf: float, dp_psi: float) -> float:
    """液体：Cv = Q*sqrt(Gf/dP)。Q 需为 gpm，dP 需为 psi。"""
    if dp_psi <= 0:
        raise ValueError("dP 必须 > 0")
    return q_gpm * math.sqrt(gf / dp_psi)


def gas_cv(q_scfh: float, gg: float, p1_psia: float, p2_psia: float,
           t1_rankine: float, k: float = 1.4, z: float = 1.0,
           xt: float = 0.7) -> tuple:
    """气体：返回 (Cv, 是否阻塞流)。Q 为 scfh，压力为 psia，温度为 °R。"""
    if p2_psia >= p1_psia:
        raise ValueError("P2 必须 < P1（阀必须有压降）")
    x = (p1_psia - p2_psia) / p1_psia
    fk = k / 1.4
    x_t = fk * xt
    choked = x >= x_t
    x_eff = x_t if choked else x
    y = 1 - x_eff / (3 * fk * xt)
    if y <= 0:
        raise ValueError("Y 膨胀因子异常，检查压降比")
    cv = q_scfh / (1360 * p1_psia * y * math.sqrt(x_eff / (gg * t1_rankine * z)))
    return cv, choked


def main():
    ap = argparse.ArgumentParser(description="控制阀口径计算（ISA 75.01.01）")
    ap.add_argument("--fluid", choices=["liquid", "gas"], required=True)
    ap.add_argument("--q", type=float, required=True, help="流量（液体 gpm / 气体 scfh）")
    ap.add_argument("--qunit", default="gpm", choices=["gpm", "m3h", "scfh", "nm3h"],
                    help="流量单位（液体：gpm/m3h；气体：scfh/nm3h）")
    ap.add_argument("--gf", type=float, default=1.0, help="液体比重(水=1)")
    ap.add_argument("--dp", type=float, help="液体压差 psi")
    ap.add_argument("--gg", type=float, default=0.62, help="气体比重(空气=1)")
    ap.add_argument("--p1", type=float, help="阀前压力 psia")
    ap.add_argument("--p2", type=float, help="阀后压力 psia")
    ap.add_argument("--t1", type=float, help="入口温度 °F（气体，自动转 °R）")
    ap.add_argument("--k", type=float, default=1.4, help="气体比热比 k（默认 1.4 空气）")
    ap.add_argument("--z", type=float, default=1.0, help="压缩因子（默认 1.0）")
    ap.add_argument("--xt", type=float, default=0.7, help="极限压降比 xT（默认 0.7）")
    args = ap.parse_args()

    if args.fluid == "liquid":
        q = args.q if args.qunit == "gpm" else args.q / GPM_TO_M3H
        if not args.dp:
            ap.error("液体工况需 --dp")
        cv = liquid_cv(q, args.gf, args.dp)
        print(f"液体控制阀口径（ISA 75.01.01）：")
        print(f"  流量: {q:.1f} gpm | Gf={args.gf} | dP={args.dp} psi")
        print(f"  Cv = {cv:.2f} (US gpm)")
        print(f"  Kv = {cv * K_V:.2f} (m³/h)")
        print(f"  选型建议: 取 Cv 的 1.2~1.5 倍选标准阀（正常工况留裕量）")
    else:
        if args.qunit not in ("scfh", "nm3h"):
            print(f"⚠️ 气体工况流量单位应为 scfh 或 nm3h（收到 {args.qunit}），按 scfh 处理")
        q = args.q if args.qunit == "scfh" else args.q / 0.0283168  # nm3h → scfh(近似)
        if not (args.p1 and args.p2 and args.t1):
            ap.error("气体工况需 --p1 --p2 --t1")
        t_r = args.t1 + 459.67  # °F → °R
        cv, choked = gas_cv(q, args.gg, args.p1, args.p2, t_r, args.k, args.z, args.xt)
        x = (args.p1 - args.p2) / args.p1
        print(f"气体控制阀口径（ISA 75.01.01）：")
        print(f"  流量: {q:.0f} scfh | Gg={args.gg} | P1={args.p1} psia | P2={args.p2} psia | T={args.t1}°F")
        print(f"  压降比 x = {x:.3f}" + (" → **阻塞流**（用 xT 计算）" if choked else ""))
        print(f"  Cv = {cv:.2f} (US gpm)")
        print(f"  Kv = {cv * K_V:.2f} (m³/h)")
        print(f"  选型建议: 取 Cv 的 1.2~1.5 倍选标准阀；阻塞流时核对制造商噪声/闪蒸数据")


if __name__ == "__main__":
    main()
