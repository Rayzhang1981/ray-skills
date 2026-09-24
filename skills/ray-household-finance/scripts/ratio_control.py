# -*- coding: utf-8 -*-
"""比例控制模型：四类资产按目标比例渐进收敛的 36 个月模拟。

机制（2026-08-05 确立）：
    每月 ¥10,000 充入活期宝 → 计算四类目标额 = 总资产 × 目标比例
    → 活期宝超配部分按缺口比例流向低配类（债基/QDII/ETF）
    → 受「月转出上限」+「QDII 限购」约束 → 渐进收敛

用法：
    python ratio_control.py [--target 30,50,12,8] [--cap 50000] [--months 36] [--band 5]

漂移带（band rebalance，v2.2.0 新增）：
    某类资产实际占比偏离目标比例 < band 个百分点时，当月不做调仓（带内不动），
    避免月月微调；超带才按缺口比例调仓。默认 5，设 0 恢复逐月精确调仓。

输出：
    每月：活期宝/债基/QDII/ETF 余额、总资产、建议转出额、各类建议投入额
    关键节点：活期宝收敛月份、总资产里程碑、加权年化
"""
import sys

# ===== 默认参数 =====
# 初始状态（四类：活期宝/国内债基/美债QDII/ETF权益）
INIT = [1132171.0, 430270.0, 23195.0, 39062.0]
# 年化收益假设（活期宝/债基/QDII/ETF）
RATES = [0.013, 0.025, 0.035, 0.05]
NAMES = ['活期宝', '国内债基', '美债QDII', 'ETF权益']

MONTHLY_IN = 10000.0    # 每月充入活期宝
QDII_CAP = 10000.0      # QDII 月度限购

TARGET = [30, 50, 12, 8]   # 方案A 目标比例（%）
CAP = 50000.0              # 月转出上限
MONTHS = 36
BAND = 5.0                 # 漂移带（百分点）：偏离目标 < band 时当月不动


def parse_args():
    global TARGET, CAP, MONTHS, BAND
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--target':
            TARGET = [float(x) for x in args[i + 1].split(',')]
            i += 2
        elif args[i] == '--cap':
            CAP = float(args[i + 1])
            i += 2
        elif args[i] == '--months':
            MONTHS = int(args[i + 1])
            i += 2
        elif args[i] == '--band':
            BAND = float(args[i + 1])
            i += 2
        else:
            i += 1


def simulate(target, cap, months, init=None, monthly_in=MONTHLY_IN, qdii_cap=QDII_CAP,
             rates=None, band=BAND):
    """核心模拟。返回 (rows, meta)，rows 每项为 dict。

    注意：内部 append 用 bal[:] 深拷贝（列表引用复用会导致误报偏差）。
    band>0 时启用漂移带：各类占比偏离目标 < band 个百分点则该类当月不调仓。
    """
    init = init or list(INIT)
    rates = rates or RATES
    monthly_r = [r / 12 for r in rates]
    T = [t / sum(target) for t in target]  # 归一化
    bal = list(init)
    rows = []

    for m in range(1, months + 1):
        bal[0] += monthly_in  # 充值进活期宝
        grown = [bal[i] * (1 + monthly_r[i]) for i in range(4)]
        total = sum(grown)
        gaps = [T[i] * total - grown[i] for i in range(4)]
        # 漂移带：偏离目标 < band 个百分点的类当月不参与调仓
        drift = [abs(grown[i] / total * 100 - T[i] * 100) for i in range(4)]
        active = [i for i in range(4) if band <= 0 or drift[i] >= band]
        need = sum(max(0, gaps[i]) for i in active if i > 0)   # 低配类总缺口（带外）
        overflow = max(0, grown[0] - T[0] * total)       # 活期宝可流出上限
        transfer = min(need, overflow, cap)              # 实际转出
        gap_pos = [max(0, gaps[i]) if i in active else 0.0 for i in range(4)]
        gap_sum = sum(gap_pos)
        invest = [0.0] * 4
        if gap_sum > 0:
            for i in range(1, 4):
                invest[i] = transfer * gap_pos[i] / gap_sum
            # QDII 限购：超额转债基
            if invest[2] > qdii_cap:
                invest[1] += invest[2] - qdii_cap
                invest[2] = qdii_cap
            transfer = invest[1] + invest[2] + invest[3]
        bal = [grown[0] - transfer] + [grown[i] + invest[i] for i in range(1, 4)]
        rows.append({
            'month': m,
            'bal': bal[:],
            'total': sum(bal),
            'transfer': transfer,
            'invest': invest[:],
            'pct': [bal[i] / sum(bal) * 100 for i in range(4)],
        })

    # 关键节点
    conv = next((r for r in rows if abs(r['pct'][0] - T[0] * 100) < 2), None)
    meta = {
        'target_pct': [round(t / sum(target) * 100, 1) for t in target],
        'weighted_annual': sum(T[i] * rates[i] * 100 for i in range(4)),
        'final_total': rows[-1]['total'],
        'conv_month': conv['month'] if conv else None,
    }
    return rows, meta


def main():
    parse_args()
    rows, meta = simulate(TARGET, CAP, MONTHS, band=BAND)
    final = rows[-1]

    print(f'=== 比例控制模型 [{"/".join(map(str, TARGET))}] 月转出上限 ¥{CAP:,.0f} '
          f'漂移带 ±{BAND:.0f}% ===')
    print(f'目标比例: {"/".join(f"{p:.0f}%" for p in meta["target_pct"])}')
    print(f'加权年化: {meta["weighted_annual"]:.2f}%')
    print(f'{MONTHS}月后总资产: ¥{final["total"]:,.0f}')
    for i, n in enumerate(NAMES):
        print(f'  {n}: ¥{final["bal"][i]:,.0f} ({final["pct"][i]:.1f}%)')
    if meta['conv_month']:
        print(f'活期宝收敛到目标: 第 {meta["conv_month"]} 个月')
    print()
    print('月份 | 活期宝 | 债基 | QDII | ETF | 总资产 | 建议转出')
    for r in rows[:12]:
        print(f'{r["month"]:>2}月 | {r["bal"][0]:>9,.0f} | {r["bal"][1]:>7,.0f} | {r["bal"][2]:>6,.0f} | {r["bal"][3]:>6,.0f} | {r["total"]:>10,.0f} | {r["transfer"]:>8,.0f}')


if __name__ == '__main__':
    main()
