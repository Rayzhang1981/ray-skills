# -*- coding: utf-8 -*-
"""交易流水 → 成本基准与真实收益率（金额口径 + 份额法 + XIRR）。

输入：
    1) transactions.json —— append-only 交易流水（schema 见 references/json-schema.md）
    2) [可选] 标准化持仓快照 JSON —— 提供期末现值，用于累计损益/真实收益率/XIRR

口径（v2.2.0 确立，金额口径为主、份额法为辅）：
    累计投入   = Σ buy 金额
    累计回收   = Σ sell 金额 + Σ dividend 金额
    累计损益   = 期末现值 + 累计回收 − 累计投入
    真实收益率 = 累计损益 / 累计投入
    加权平均成本 = Σ买入净额 / Σ买入份额（仅统计带 nav 的买入；卖出按当时均价出账）
    XIRR      = 现金流（买为负 / 卖与分红为正 / 期末现值）的年化内部收益率，二分法解 NPV=0

用法：
    python cost_basis.py <transactions.json> [snapshot.json]

注意：流水与快照同属家庭财务敏感数据，仅在本地处理（SKILL.md 红线 7）。
"""
import json
import re
import sys
from datetime import date, datetime

CODE_RE = re.compile(r'[（(](\d{6})[)）]')


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def parse_date(s):
    for fmt in ('%Y-%m-%d', '%Y/%m/%d'):
        try:
            return datetime.strptime(str(s), fmt).date()
        except ValueError:
            continue
    raise ValueError(f'无法解析日期: {s!r}')


def compute_positions(txns):
    """按时间序聚合每只基金：投入/回收/份额与加权成本/已实现损益。"""
    pos = {}
    for t in sorted(txns, key=lambda x: str(x.get('date', ''))):
        code = str(t.get('fund_code', '')).strip()
        typ = str(t.get('type', '')).strip().lower()
        amt = float(t.get('amount') or 0)
        fee = float(t.get('fee') or 0)
        nav = t.get('nav')
        p = pos.setdefault(code, {'name': t.get('fund_name') or code, 'invested': 0.0,
                                  'recovered': 0.0, 'shares': 0.0, 'cost': 0.0,
                                  'realized': 0.0, 'nav_missing': 0})
        if typ == 'buy':
            p['invested'] += amt
            p['name'] = t.get('fund_name') or p['name']
            if nav:
                net = amt - fee
                sh = net / float(nav)
                p['cost'] = (p['cost'] * p['shares'] + net) / (p['shares'] + sh)
                p['shares'] += sh
            else:
                p['nav_missing'] += 1
        elif typ == 'sell':
            p['recovered'] += amt
            if nav and p['shares'] > 0:
                sh = min(amt / float(nav), p['shares'])
                p['realized'] += amt - sh * p['cost']
                p['shares'] -= sh
            else:
                p['nav_missing'] += 1
        elif typ == 'dividend':
            p['recovered'] += amt
            p['realized'] += amt
        else:
            print(f'⚠️ 未知交易类型 {typ!r}（fund {code}），已跳过')
    return pos


def snapshot_values(snapshot):
    """从标准化持仓快照提取 fund_code → 现值。货基无代码，匹配不到会显式提示。"""
    values = {}
    for f in snapshot.get('funds', []):
        m = CODE_RE.search(str(f.get('name', '')))
        if m:
            values[m.group(1)] = float(f.get('amount') or 0)
    return values


def xirr(cfs):
    """cfs: [(date, amount)]，二分法解 NPV=0；现金流无变号或无解时返回 None。"""
    if len(cfs) < 2:
        return None
    cfs = sorted(cfs, key=lambda x: x[0])
    if not (any(a < 0 for _, a in cfs) and any(a > 0 for _, a in cfs)):
        return None
    d0 = cfs[0][0]

    def npv(rate):
        return sum(a / (1 + rate) ** max((d - d0).days / 365.0, 1e-9) for d, a in cfs)

    lo, hi = -0.9, 10.0
    f_lo, f_hi = npv(lo), npv(hi)
    if f_lo * f_hi > 0:
        return None
    for _ in range(200):
        mid = (lo + hi) / 2
        f_mid = npv(mid)
        if abs(f_mid) < 1e-7:
            return mid
        if f_lo * f_mid < 0:
            hi = mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    txns = load_json(sys.argv[1]).get('transactions', [])
    if not txns:
        print('⚠️ transactions 为空')
        sys.exit(1)
    snapshot = load_json(sys.argv[2]) if len(sys.argv) > 2 else None
    values = snapshot_values(snapshot) if snapshot else {}
    ref_date = parse_date(snapshot['date']) if snapshot and snapshot.get('date') else date.today()

    pos = compute_positions(txns)
    print(f'=== 成本基准（{len(txns)} 笔流水，期末日期 {ref_date}）===')
    print('代码 | 名称 | 累计投入 | 累计回收 | 现值 | 累计损益 | 收益率 | 加权成本 | 持有份额')
    tot_i = tot_r = tot_v = 0.0
    all_cfs = []
    for code, p in sorted(pos.items()):
        cur = values.get(code, 0.0)
        if code not in values and p['invested']:
            print(f'⚠️ {code} {p["name"]}: 快照中无现值，损益未计入该基金现值')
        gain = cur + p['recovered'] - p['invested']
        ret = gain / p['invested'] * 100 if p['invested'] else 0.0
        cost_s = f'{p["cost"]:.4f}' if p['cost'] else '--'
        miss = f'（nav缺失{p["nav_missing"]}笔）' if p['nav_missing'] else ''
        print(f'{code} | {p["name"]} | {p["invested"]:,.0f} | {p["recovered"]:,.0f} | '
              f'{cur:,.0f} | {gain:+,.0f} | {ret:+.2f}% | {cost_s} | {p["shares"]:,.0f}{miss}')
        tot_i += p['invested']
        tot_r += p['recovered']
        tot_v += cur
        for t in txns:
            if str(t.get('fund_code', '')).strip() != code:
                continue
            typ = str(t.get('type', '')).lower()
            amt = float(t.get('amount') or 0)
            all_cfs.append((parse_date(t['date']), -amt if typ == 'buy' else amt))
        if cur:
            all_cfs.append((ref_date, cur))

    print('-' * 72)
    total_gain = tot_v + tot_r - tot_i
    ret = total_gain / tot_i * 100 if tot_i else 0.0
    print(f'合计 | 投入 {tot_i:,.0f} | 回收 {tot_r:,.0f} | 现值 {tot_v:,.0f} | '
          f'累计损益 {total_gain:+,.0f} | 真实收益率 {ret:+.2f}%')
    if snapshot:
        print(f'快照核对：grand_total={snapshot.get("grand_total", "?")}，'
              f'流水基金现值合计={tot_v:,.0f}（差值=未记流水的持仓，属正常）')
    r = xirr(all_cfs)
    print(f'XIRR（资金加权年化）: {r * 100:+.2f}%' if r is not None
          else 'XIRR: 无法求解（现金流无变号或时间跨度不足）')


if __name__ == '__main__':
    main()
