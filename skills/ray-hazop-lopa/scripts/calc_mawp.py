# -*- coding: utf-8 -*-
"""
ray-hazop-lopa · 计算模块③：MAWP 估算（薄壁圆筒）
P = 2·S·E·t / (D + 0.8·t)
用法: python calc_mawp.py            # 默认示例双罐参数
      python calc_mawp.py --D 1800 --t 10 --S 105 --E 0.8 --name "R203"
单位红线：D/t 用 mm，S 用 MPa，输出 bar（1 MPa = 10 bar）。
"""
import argparse, math

def main():
    ap = argparse.ArgumentParser(description="MAWP 薄壁圆筒估算")
    ap.add_argument('--D', type=float, default=1900.0, help='公称直径 mm')
    ap.add_argument('--t', type=float, default=8.0, help='壁厚 mm')
    ap.add_argument('--S', type=float, default=117.0, help='材料许用应力 MPa（304 常温~117，高温取~105）')
    ap.add_argument('--E', type=float, default=0.8, help='焊接接头系数')
    ap.add_argument('--name', default='设备', help='设备名称')
    ap.add_argument('--factor', type=float, default=1.0, help='工程折减系数（保守取 0.55~0.6）')
    a = ap.parse_args()

    P_MPa = 2*a.S*a.E*a.t/(a.D+0.8*a.t)
    P = P_MPa*10.0                  # bar（1 MPa = 10 bar，勿除反）
    Pc = P*a.factor
    print(f"== MAWP 估算：{a.name} ==")
    print(f"  P = 2×{a.S}×{a.E}×{a.t}/({a.D}+0.8×{a.t}) = {P_MPa:.2f} MPa = {P:.1f} bar")
    if a.factor != 1.0:
        print(f"  工程取值（×{a.factor}）: {Pc:.1f} bar")
    print(f"  判定提示: 泄放工况压力须 < MAWP；正式设计按 GB 150 复核")

if __name__ == '__main__':
    main()
