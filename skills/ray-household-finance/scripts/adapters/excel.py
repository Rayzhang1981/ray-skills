# -*- coding: utf-8 -*-
"""数据源适配器：天天基金持仓 Excel → 标准化持仓 JSON。

本文件是「数据源适配层」的一个 adapter。职责单一：把天天基金 Excel
映射成标准化持仓 JSON（见 SKILL.md「标准化持仓 JSON」章节），下游分析零依赖。

用法：
    python excel.py <excel路径> <日期YYYY-MM-DD> [输出json路径]

示例：
    python excel.py E:/LingXi/Financial/Financial-0809.xlsx 2026-08-09

输出 _portfolio_data.json，字段：
    mm_funds: [{name, yield_rate, shares, unpaid, cumulative_gain}]
    funds: [{name, type_info, acls, amount, status, gain, gpct, gpct_s, nav}]
    mm_total / fund_total / grand_total / class_totals / class_gains / date
"""
import openpyxl
import json
import os
import sys

# ===== 参数 =====
if len(sys.argv) < 3:
    print(__doc__)
    sys.exit(1)

excel_path = sys.argv[1]
date_str = sys.argv[2]
# 默认输出到技能包外的数据目录（家庭财务敏感数据不进技能包——发布安全 + 换环境可移植）；第 3 参数可覆盖
_DEFAULT_DATA_DIR = os.path.join(os.path.expanduser('~'), '.workbuddy', 'data', 'ray-household-finance')
os.makedirs(_DEFAULT_DATA_DIR, exist_ok=True)
out_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(_DEFAULT_DATA_DIR, '_portfolio_data.json')

def _archive_snapshot(data):
    """快照归档（v2.9.0）：按日期追加存档 `_snapshots/portfolio_YYYYMMDD.json`，不覆盖。

    对比基线永远可从归档取（08-23 教训：单文件被覆盖后，只能从历史 HTML 正则提取做对账）。
    """
    d = str(data.get('date', ''))
    ymd = d.replace('-', '')[:8] if len(d) >= 8 else 'unknown'
    arc_dir = os.path.join(_DEFAULT_DATA_DIR, '_snapshots')
    os.makedirs(arc_dir, exist_ok=True)
    arc_path = os.path.join(arc_dir, f'portfolio_{ymd}.json')
    with open(arc_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return arc_path


wb = openpyxl.load_workbook(excel_path, data_only=True)

# ===== 版式探测（0928 起新格式：无表头/2行制/无表头区）=====
# 新格式特征：sheet1 第 1 行直接是货基数据（row[1] 匹配「万份收益（7日年化）」）；
# 旧格式特征：sheet1 第 1 行含「简称」表头。先探测再选解析器，禁猜。
import re as _re
_YIELD_PAT = _re.compile(r"^-?[\d.]+（-?[\d.]+%）$")
_CODE_PAT = _re.compile(r"（(\d{6})）")

def _is_new_format():
    # 判据用「数据行模式」而非「有无表头」——0928 首行也有「基金简称」表头，
    # 但第 2 列是『每万份收益（7日年化）』列头、第 3 行起才是数据且每只占 2 行（旧格式每只 1 行）
    ws1 = wb.worksheets[0]
    for row in ws1.iter_rows(max_row=8, values_only=True):
        if isinstance(row[0], str) and isinstance(row[1], str) and _YIELD_PAT.match(row[1].strip()):
            # 数据行命中：再看同 sheet 内相邻数据行是否被「日期行」隔开（新格式特征）
            return True
    return False

_NEW_FORMAT = _is_new_format()

if _NEW_FORMAT:
    # ============ 0928+ 新格式解析 ============
    # 活期宝：锚 = row[0] 字符串 + row[1] 收益率模式（数据行与日期行交错，锚点过滤）
    mm_funds = []
    mm_total = 0.0
    for row in wb.worksheets[0].iter_rows(values_only=True):
        name, yrate = row[0], row[1]
        if not (isinstance(name, str) and isinstance(yrate, str) and _YIELD_PAT.match(yrate.strip())):
            continue
        parts = str(row[2]).replace(',', '').split('/')
        shares = float(parts[-1].strip())
        unpaid = float(row[3]) if row[3] else 0.0
        cum = float(row[4]) if row[4] else 0.0
        mm_funds.append({'name': name.strip(), 'yield_rate': yrate.strip(),
                         'shares': shares, 'unpaid': unpaid, 'cumulative_gain': cum})
        mm_total += shares

    # 基金：锚 = 名称行含（\d{6}）；块 = 名称+类型+金额+[状态]+盈亏+收益率
    _STATUS = {'有在途交易', '到期', '未到期', '将到期'}
    rows = [r[0] for r in wb.worksheets[1].iter_rows(values_only=True)]
    funds = []
    i, n = 0, len(rows)
    while i < n:
        name = rows[i]
        if not (isinstance(name, str) and _CODE_PAT.search(name)):
            i += 1
            continue
        ft = str(rows[i + 1]) if rows[i + 1] else ''
        amt = float(rows[i + 2]) if rows[i + 2] else 0.0
        j = i + 3
        status = ''
        if j < n and isinstance(rows[j], str) and rows[j].strip() in _STATUS:
            status = rows[j].strip()
            j += 1
        gv = rows[j] if j < n else 0.0
        gain = float(gv) if gv not in (None, '--') else 0.0
        pv = rows[j + 1] if j + 1 < n else '--'
        gpct_s = str(pv) if pv not in (None, '--') else '--'
        nav = ''
        if '最新净值' in ft:
            nav = ft.split('：')[-1].split('（')[0].split('(')[0].strip()
        if '债券型' in ft:
            acls = 'bond'
        elif '指数型' in ft:
            acls = 'index'
        elif 'QDII' in ft:
            acls = 'qdii'
        elif '混合型' in ft:
            acls = 'mixed'
        else:
            acls = 'other'
        try:
            gpct = float(gpct_s) if gpct_s != '--' else 0.0
        except ValueError:
            gpct = 0.0
        funds.append({'name': name.strip(), 'type_info': ft, 'acls': acls,
                      'amount': round(amt, 2), 'status': status,
                      'gain': round(gain, 2), 'gpct': round(gpct, 6),
                      'gpct_s': gpct_s, 'nav': nav})
        i = j + 2

    funds.sort(key=lambda x: x['amount'], reverse=True)
    fund_total = sum(f['amount'] for f in funds)
    grand_total = mm_total + fund_total
    ct, cg = {}, {}
    for f in funds:
        ct[f['acls']] = ct.get(f['acls'], 0) + f['amount']
        cg[f['acls']] = cg.get(f['acls'], 0) + f['gain']
    ct['mm'] = mm_total
    cg['mm'] = sum(m['cumulative_gain'] for m in mm_funds)

    data = {'mm_funds': mm_funds, 'funds': funds,
            'mm_total': round(mm_total, 2), 'fund_total': round(fund_total, 2),
            'grand_total': round(grand_total, 2),
            'class_totals': {k: round(v, 2) for k, v in ct.items()},
            'class_gains': {k: round(v, 2) for k, v in cg.items()},
            'date': date_str, 'format_version': '0928-two-row-mm'}

    # 闸门：防漏抓（0928 事故教训——活期宝回退错 sheet 时输出 0 且不报错）
    assert len(mm_funds) >= 15, 'FATAL: 活期宝仅 %d 只，疑漏抓' % len(mm_funds)
    assert len(funds) >= 10, 'FATAL: 基金仅 %d 只，疑漏抓' % len(funds)
    assert abs(sum(f['amount'] for f in funds) + mm_total - grand_total) < 0.01
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    _arc = _archive_snapshot(data)
    print(f'OK(new fmt): {len(funds)} funds, {len(mm_funds)} MM, total={grand_total:,.2f}')
    print(f'Classes: { {k: round(v, 0) for k, v in ct.items()} }')
    print(f'Snapshot archived: {_arc}')
    sys.exit(0)

# ============ 旧格式解析（下方原逻辑不动） ============

# ===== 活期宝 sheet =====
# sheet 名可能为「活期宝 / Sheet1 / Sheet2 ...」——按位置取：第一个 sheet 为活期宝
# （天天基金导出：活期宝在前、基金在后；0823 版导出名为 Sheet1/Sheet2）
_ws0 = wb.worksheets[0]
if '简称' in str(_ws0.cell(1, 1).value or ''):
    ws_mm = _ws0
else:
    ws_mm = wb.worksheets[1]
    # 找不到活期宝表头时，回退按名字匹配
    for _n in ['活期宝', '货币', '余额宝']:
        if _n in wb.sheetnames:
            ws_mm = wb[_n]
            break
mm_funds = []
mm_total = 0.0
for row in ws_mm.iter_rows(min_row=1, max_row=ws_mm.max_row, values_only=True):
    non_none = [v for v in row if v is not None]
    if len(non_none) < 5:
        continue
    name = row[0]
    if not isinstance(name, str):
        continue
    if '简称' in name or '操作' in name:
        continue
    # 份额：'可用 / 可取 / 总份额'，取最后一段
    parts = str(row[2]).replace(',', '').split('/') if row[2] else ['0']
    total_shares = float(parts[-1].strip())
    unpaid = float(row[3]) if row[3] else 0.0
    cumulative = float(row[4]) if row[4] else 0.0
    mm_funds.append({
        'name': name,
        'yield_rate': str(row[1]) if row[1] else '',
        'shares': total_shares,
        'unpaid': unpaid,
        'cumulative_gain': cumulative
    })
    mm_total += total_shares

# ===== 基金 sheet =====
# 每只基金占一个块：名称行(含6位代码) + 类型行 + 金额行 + 状态行 + 盈亏行 + 收益率行
# 状态值「有在途交易/到期/未到期/将到期」使块高为 7；否则为 6
# sheet 名可能为「基金 / Sheet2 ...」——取另一个 sheet（活期宝之外的）
ws_fund = None
for _n in ['基金', 'fund', 'Fund']:
    if _n in wb.sheetnames:
        ws_fund = wb[_n]
        break
if ws_fund is None:
    ws_fund = wb.worksheets[1] if len(wb.worksheets) > 1 else wb.worksheets[0]
all_rows = [row[0] for row in ws_fund.iter_rows(min_row=1, max_row=ws_fund.max_row, values_only=True)]

STATUS_VALUES = ['有在途交易', '到期', '未到期', '将到期']

funds = []
i = 4
while i < len(all_rows):
    name = all_rows[i]
    if name is None or not isinstance(name, str):
        i += 1
        continue
    # 跳过表头/分隔行
    if any(k in name for k in ['买入卖出', '按产品', '金额', '持仓收益', '操作']):
        i += 1
        continue

    ft = str(all_rows[i + 1]) if all_rows[i + 1] else ''
    amt = float(all_rows[i + 2]) if all_rows[i + 2] else 0.0

    nv = all_rows[i + 3]
    status = ''
    gain = 0.0
    gpct_s = ''

    if isinstance(nv, str) and nv in STATUS_VALUES:
        # 有状态值：块高 7
        status = nv
        gain = float(all_rows[i + 4]) if all_rows[i + 4] and all_rows[i + 4] != '--' else 0.0
        gv = all_rows[i + 5]
        gpct_s = str(gv) if gv is not None and gv != '--' else '--'
        i += 7
    else:
        # 无状态值：块高 6
        gain = float(nv) if nv and nv != '--' else 0.0
        gv = all_rows[i + 4]
        gpct_s = str(gv) if gv is not None and gv != '--' else '--'
        i += 6

    # 资产分类
    if '债券型' in ft:
        acls = 'bond'
    elif '指数型' in ft:
        acls = 'index'
    elif 'QDII' in ft:
        acls = 'qdii'
    elif '混合型' in ft:
        acls = 'mixed'
    else:
        acls = 'other'

    # 提取净值
    nav = ''
    if '最新净值' in ft:
        nav = ft.split('：')[-1].split('（')[0].split('(')[0].strip()

    try:
        gpct = float(gpct_s) if gpct_s not in ('', '--') else 0.0
    except ValueError:
        gpct = 0.0

    funds.append({
        'name': name,
        'type_info': ft,
        'acls': acls,
        'amount': round(amt, 2),
        'status': status,
        'gain': round(gain, 2),
        'gpct': round(gpct, 6),
        'gpct_s': gpct_s,
        'nav': nav
    })

funds.sort(key=lambda x: x['amount'], reverse=True)
fund_total = sum(f['amount'] for f in funds)
grand_total = mm_total + fund_total

# 类别汇总
ct = {}
cg = {}
for f in funds:
    ct[f['acls']] = ct.get(f['acls'], 0) + f['amount']
    cg[f['acls']] = cg.get(f['acls'], 0) + f['gain']
ct['mm'] = mm_total
cg['mm'] = sum(mf['cumulative_gain'] for mf in mm_funds)

data = {
    'mm_funds': mm_funds,
    'funds': funds,
    'mm_total': round(mm_total, 2),
    'fund_total': round(fund_total, 2),
    'grand_total': round(grand_total, 2),
    'class_totals': {k: round(v, 2) for k, v in ct.items()},
    'class_gains': {k: round(v, 2) for k, v in cg.items()},
    'date': date_str
}

with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'OK: {len(funds)} funds, {len(mm_funds)} MM, total={grand_total:,.2f}')
print(f'Classes: { {k: round(v, 0) for k, v in ct.items()} }')
print(f'Snapshot archived: {_archive_snapshot(data)}')
