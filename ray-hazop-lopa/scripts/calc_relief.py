# -*- coding: utf-8 -*-
"""
ray-hazop-lopa · 计算模块②：泄放面积四方法交叉校核
  方法一  API 520 纯气体（参考下限）
  方法二  DIERS/OMEGA 两相流（主方法）
  方法三  刘嚆储罐泄压口（常压设计，法一/法二/经验值）
  方法四  赵红乔 kF 污染逐点核算
用法: python calc_relief.py                 # 默认 701 储罐 V1101A 参数
      python calc_relief.py --DN 125 --Pset 60
单位红线：P 压力统一 kPa；面积输出 mm² 与 cm² 并列；管径 mm。
"""
import argparse, math

def main():
    ap = argparse.ArgumentParser(description="泄放面积四方法校核")
    # API 520（纯气体）
    ap.add_argument('--W', type=float, default=1507.0, help='质量流量 kg/h（产氧）')
    ap.add_argument('--MW', type=float, default=32.0, help='分子量')
    ap.add_argument('--k', type=float, default=1.4, help='比热比')
    ap.add_argument('--T', type=float, default=383.0, help='泄放温度 K')
    ap.add_argument('--Pset', type=float, default=50.0, help='整定表压 kPaG')
    ap.add_argument('--Kd', type=float, default=0.975, help='泄放系数')
    ap.add_argument('--Pback', type=float, default=5.0, help='超压叠加 kPa')
    # DIERS
    ap.add_argument('--m', type=float, default=21349.0, help='体系质量 kg')
    ap.add_argument('--cp', type=float, default=3.43, help='比热 kJ/(kg·K)')
    ap.add_argument('--dTdt_r', type=float, default=15.3, help='泄放点温升 ℃/min（全罐分解基准取最大 15.3；保守估算档 10）')
    ap.add_argument('--dTdt_m', type=float, default=15.3, help='最大温升 ℃/min')
    ap.add_argument('--rho_v', type=float, default=0.58, help='蒸汽密度 kg/m³')
    ap.add_argument('--hfg', type=float, default=2230.0, help='汽化潜热 kJ/kg')
    ap.add_argument('--hfg_eff', type=float, default=136.9, help='DIERS 修正潜热 kJ/kg')
    ap.add_argument('--G', type=float, default=2.86e4, help='单位面积泄放能力 kg/(m²·s)')
    # 刘嚆 / 赵红乔
    ap.add_argument('--c', type=float, default=50.0, help='H2O2 浓度 wt%')
    ap.add_argument('--Kf', type=float, default=1500.0, help='刘嚆法一 Kf')
    ap.add_argument('--p', type=float, default=5000.0, help='常压泄放压力 Pa')
    ap.add_argument('--t_pure', type=float, default=10.674, help='纯 H2O2 当量 t')
    ap.add_argument('--V', type=float, default=21.0, help='罐容积 m³')
    ap.add_argument('--a', type=float, default=6.74, help='刘嚆法二系数（50%）')
    ap.add_argument('--DN', type=float, default=102.0, help='现有管径内径 mm（DN100 按 102）')
    a = ap.parse_args()

    print("== 方法一：API 520 纯气体（参考下限）==")
    C = 520*math.sqrt(a.k*(2.0/(a.k+1.0))**((a.k+1.0)/(a.k-1.0)))
    P_abs = a.Pset + 101.3 + a.Pback   # kPaA
    A_api = 13160.0*a.W*math.sqrt(a.T*1.0)/(C*a.Kd*P_abs*math.sqrt(a.MW))
    print(f"  C={C:.1f} P_abs={P_abs:.1f} kPaA | A = {A_api:.0f} mm² = {A_api/100:.1f} cm²")

    print("\n== 方法二：DIERS/OMEGA 两相流（主方法）==")
    Qv = a.m*a.cp*(a.dTdt_r/60.0)/(a.rho_v*a.hfg)          # m³/s 蒸汽
    QG = 0.059                                              # m³/s 气体（简化/输入）
    pv_pr = Qv/(Qv+QG)
    q = 0.5*a.cp*(a.dTdt_r+a.dTdt_m)*1000.0/60.0            # W/kg
    W = 1.77*(q*a.m)/(a.hfg_eff*1000.0)                     # kg/s
    A_diers = W/a.G*1e6                                     # mm²
    print(f"  Qv={Qv:.2f} m³/s QG={QG:.3f} m³/s | 蒸汽占比 {pv_pr:.3f} ({'缓和混合' if pv_pr>0.1 else '欠缓和'})")
    print(f"  q={q:.0f} W/kg | W={W:.1f} kg/s | A = {A_diers:.0f} mm² = {A_diers/100:.1f} cm²")

    print("\n== 方法三：刘嚆储罐泄压口（常压设计）==")
    A1t = 0.35*(a.c/(100.0-a.c))*(a.Kf/math.sqrt(0.01*a.p))
    A1 = A1t*a.t_pure
    d1 = math.sqrt(4*A1/math.pi)*10
    d2 = a.a*a.V**0.493          # cm
    A2 = math.pi/4.0*d2**2
    A3 = 200.0*a.t_pure
    print(f"  法一(Kf={a.Kf:.0f},p={a.p:.0f}Pa): {A1t:.1f} cm²/t → 总 {A1:.0f} cm² → 直径 {d1:.0f} mm")
    print(f"  法二(d=a·V^0.493): d={d2*10:.0f} mm → A={A2:.0f} cm²")
    print(f"  法三(200 cm²/t): 总 {A3:.0f} cm² → 直径 {math.sqrt(4*A3/math.pi)*10:.0f} mm")

    print("\n== 方法四：赵红乔 kF 污染逐点核算 ==")
    for fe,kf in [(0.12,1.46),(7.76,11.6),(31.04,98.9),(38.81,1398),(46.6,10366)]:
        A = 0.35*(a.c/(100.0-a.c))*(kf/math.sqrt(0.01*a.p))*a.t_pure
        d = math.sqrt(4*A/math.pi)*10
        print(f"  Fe²⁺ {fe:6.2f} mg/kg (kF={kf:>7.0f}): 总 {A:7.0f} cm² → 直径 {d:6.0f} mm")

    print("\n== 判定 ==")
    dn_a = math.pi/4.0*(a.DN**2)
    print(f"  现有 DN{a.DN:.0f}: {dn_a:.0f} mm² = {dn_a/100:.1f} cm²")
    print(f"  DIERS 需求 {A_diers:.0f} mm² {'>' if A_diers>dn_a else '<'} DN{a.DN:.0f} → {'不足，需升级' if A_diers>dn_a else '足够'}")
    print(f"  API520 下限 {A_api:.0f} mm² {'>' if A_api>dn_a else '<'} DN{a.DN:.0f}（仅参考）")

if __name__ == '__main__':
    main()
