# -*- coding: utf-8 -*-
"""
ray-hazop-lopa · 计算模块①：分解动力学
两点 Arrhenius 外推（Ea）→ 各温度绝热温升速率 → 温升时间线（数值积分）→ 污染 kF 放大坍缩
用法: python calc_kinetics.py [--T1 66.1 --r1 0.109 --T2 118.3 --r2 15.26 --T0 45 --Tend 130]
      python calc_kinetics.py --mass 20000 --cp 3.43 --H 2888 --phi 5.45 --kf "1.46,11.6,98.9,1398,10366,107415"
默认参数为 50% 双氧水（No.2026PG0096 实测锚点）。
单位红线：r 为绝热温升速率 ℃/min；输入 ARC 样品速率时须 ×Phi（--r1 0.02*5.45 形式）。
"""
import argparse, math

def main():
    ap = argparse.ArgumentParser(description="分解动力学 Arrhenius 外推")
    ap.add_argument('--T1', type=float, default=66.1, help='锚点1温度 ℃（起始分解）')
    ap.add_argument('--r1', type=float, default=0.02*5.45, help='锚点1绝热温升速率 ℃/min')
    ap.add_argument('--T2', type=float, default=118.3, help='锚点2温度 ℃（最大温升）')
    ap.add_argument('--r2', type=float, default=2.8*5.45, help='锚点2绝热温升速率 ℃/min')
    ap.add_argument('--T0', type=float, default=45.0, help='起始温度（联锁点）℃')
    ap.add_argument('--Tend', type=float, default=130.0, help='终止温度 ℃')
    ap.add_argument('--mass', type=float, default=20000.0, help='体系质量 kg（50% 溶液）')
    ap.add_argument('--cp', type=float, default=3.43, help='比热 kJ/(kg·K)')
    ap.add_argument('--H', type=float, default=2888.0, help='分解热 kJ/kg 纯')
    ap.add_argument('--kf', default='1.46,11.6,98.9,1398,10366,107415', help='赵红乔 kF 列表（逗号分隔）')
    a = ap.parse_args()

    T1, T2 = a.T1+273.15, a.T2+273.15
    EaR = math.log(a.r2/a.r1)/(1/T1-1/T2)
    print(f"== Arrhenius 拟合 ==")
    print(f"  Ea/R = {EaR:.0f} K | Ea = {EaR*8.314/1000:.1f} kJ/mol")

    def rate(Tc):
        return a.r1*math.exp(EaR*(1/T1-1/(Tc+273.15)))

    def t_span(fr, to, n=600):
        """返回从 fr℃ 到 to℃ 的时间（小时）"""
        dT=(to-fr)/n; t=0.0
        for i in range(n):
            t += dT/rate(fr+(i+0.5)*dT)
        return t/60.0

    print("\n== 各温度绝热温升速率 ==")
    for Tc in [40,45,50,60,66.1,70,80,90,100,110,118.3,130]:
        print(f"  {Tc:6.1f} ℃ : {rate(Tc):8.3f} ℃/min")

    print("\n== 绝热温升时间线（数值积分）==")
    tot=0.0
    for fr,to in [(a.T0,66.1),(66.1,80),(80,100),(100,118.3),(118.3,a.Tend)]:
        if to<=fr: continue
        dt=t_span(fr,to); tot+=dt
        print(f"  {fr:6.1f} → {to:6.1f} ℃ : {dt*60:7.1f} min（累计 {tot:6.2f} h）")
    print(f"  {a.T0} → {a.Tend} ℃ 总计: {tot:.2f} h = {tot*60:.0f} min")

    print("\n== 产氧速率（全罐，Nm³/h；O2 密度 1.429）==")
    for Tc in [66.1,80,90,100,110,118.3,130]:
        r=rate(Tc)
        if r<=0: continue
        P=a.mass*a.cp*r/60.0          # kW
        o2=P/a.H*(32.0/68.0)/1.429*3600.0
        print(f"  {Tc:6.1f} ℃ : {r:8.3f} ℃/min | 产氧 {o2:9.0f} Nm³/h")

    print("\n== 污染 kF 放大坍缩（时间反比）==")
    for k in [float(x) for x in a.kf.split(',')]:
        amp=k/1.46
        print(f"  kF={k:>8.0f}: ×{amp:9.0f} → {a.T0}→{a.Tend}℃ 时间 {tot*60/amp:8.1f} min = {tot/amp*60/60:6.2f} h")

if __name__ == '__main__':
    main()
