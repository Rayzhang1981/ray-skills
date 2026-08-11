# -*- coding: utf-8 -*-
"""
ray-hazop-lopa · 计算模块④：物料平衡 / 富氧 / 异常加料温升压升
  A. 分解率 → 产氧量 → 尾气富氧% → 氮气稀释量
  B. 异常加料（如 500L H2O2 一次性加入）→ 放热 → ΔT → 产氧 mol → ΔP
用法: python calc_massbal.py --mode o2     # 尾气富氧
      python calc_massbal.py --mode dT     # 异常加料温升
单位红线：产氧 Nm³/h；浓度 wt%；压力 bar。
"""
import argparse, math

def main():
    ap = argparse.ArgumentParser(description="物料平衡与温升压升")
    ap.add_argument('--mode', default='o2', choices=['o2','dT'], help='o2=尾气富氧 dT=温升压升')
    # 富氧模式
    ap.add_argument('--decomp', type=float, default=32.7, help='分解率 wt%（H2O2 计）')
    ap.add_argument('--h2o2_use', type=float, default=51.4, help='每小时分解 H2O2 kg/h')
    ap.add_argument('--o2_dens', type=float, default=1.429, help='O2 密度 kg/Nm³')
    ap.add_argument('--o2_air', type=float, default=21.0, help='空气氧含量 %')
    ap.add_argument('--target_o2', type=float, default=17.0, help='氮气稀释目标 %')
    ap.add_argument('--n2_plan', type=float, default=100.0, help='计划氮气量 m³/h')
    # 温升模式
    ap.add_argument('--vol', type=float, default=500.0, help='H2O2 体积 L')
    ap.add_argument('--rho', type=float, default=1.196, help='50% H2O2 密度 kg/L')
    ap.add_argument('--frac', type=float, default=0.5, help='H2O2 浓度 wt%')
    ap.add_argument('--decomp_frac', type=float, default=0.30, help='分解比例（异常场景取 30%）')
    ap.add_argument('--H', type=float, default=2900.0, help='分解热 kJ/kg 纯')
    ap.add_argument('--cp', type=float, default=3.43, help='体系比热 kJ/(kg·K)')
    ap.add_argument('--m_sys', type=float, default=1600.0, help='体系总质量 kg')
    ap.add_argument('--T0', type=float, default=65.0, help='起始温度 ℃')
    ap.add_argument('--V_gas', type=float, default=5.5, help='釜气相空间 m³（ΔP 用，按釜实际；团队附件 6.7bar 对应 ~5.5m³，勿用计量罐容积）')
    a = ap.parse_args()

    if a.mode == 'o2':
        o2_mass = a.h2o2_use*(32.0/68.0)               # kg/h
        o2_vol = o2_mass/a.o2_dens                      # Nm³/h
        # 富氧%：x = (0.21Q + o2)/(Q + o2)，给定目标 x=27% 反解 Q
        x_target = 0.27
        Q = o2_vol*(1.0-x_target)/(x_target-a.o2_air/100.0)
        o2_total = a.o2_air/100.0*Q + o2_vol
        print("== 尾气富氧 ==")
        print(f"  每小时分解 H2O2 {a.h2o2_use} kg → 产氧 {o2_mass:.1f} kg/h = {o2_vol:.1f} Nm³/h")
        print(f"  尾气基础流量 Q = {Q:.0f} m³/h（使混合后 O2 = 27%）")
        print(f"  混合后 O2 总量 {o2_total:.1f} m³/h")
        # 氮气稀释
        V_n2 = o2_total/(a.target_o2/100.0) - (Q+o2_vol)
        o2_after = o2_total/(Q+o2_vol+a.n2_plan)*100.0
        print(f"  目标 {a.target_o2:.0f}%: 需氮气 {V_n2:.0f} m³/h")
        print(f"  工程方案（{a.n2_plan:.0f} m³/h）: 实际 O2 ≈ {o2_after:.1f}%")
    else:
        m_sol = a.vol*a.rho                                # kg 溶液
        m_pure = m_sol*a.frac                               # kg 纯 H2O2
        m_dec = m_pure*a.decomp_frac                        # kg 分解
        Q_heat = m_dec*a.H                                  # kJ
        dT = Q_heat/(a.m_sys*a.cp)
        o2_kg = m_dec*(32.0/68.0)
        o2_nm3 = o2_kg/a.o2_dens
        o2_mol = o2_kg/0.032
        P_abs = o2_mol*8.314*(a.T0+dT+273.15)/a.V_gas/1e5  # bar 绝压（V 必须用 m³，勿 ×1000 转 L）
        print("== 异常加料温升/压升 ==")
        print(f"  H2O2 溶液 {a.vol:.0f} L = {m_sol:.0f} kg | 纯 H2O2 {m_pure:.0f} kg | 分解 {m_dec:.0f} kg")
        print(f"  放热 {Q_heat/1000:.0f} MJ | 绝热温升 ΔT = {dT:.1f} K → {a.T0}℃ → {a.T0+dT:.1f}℃")
        print(f"  产氧 {o2_kg:.1f} kg = {o2_nm3:.1f} Nm³ = {o2_mol:.0f} mol")
        print(f"  O2 分压（V_gas={a.V_gas} m³, T={a.T0+dT:.1f}℃）≈ {P_abs-1:.1f} bar 表压（团队附件 6.7 bar 口径）")

if __name__ == '__main__':
    main()
