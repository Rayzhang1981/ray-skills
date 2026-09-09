# 可复用的翻译脚本模式（按需加载）

> 内容从 SKILL.md 卸载至此（2026-08-20，v2.3.0），需要时再查；SKILL.md 正文只留索引。
> 小块的「分批策略」「残留扫描」仍留在 SKILL.md 正文（紧贴说明文字）。

## 1. 核心翻译函数（英→中，translate_batch.py 已验证模式）

```python
# 术语字典 — 按字符串长度降序排列
RAW_TERMS = { "English Phrase": "中文翻译", ... }

def make_patterns():
    items = sorted(RAW_TERMS.items(), key=lambda x: len(x[0]), reverse=True)
    return [(re.escape(eng), cn) for eng, cn in items]

def translate(val, patterns):
    if not val or not isinstance(val, str) or val.startswith("="):
        return val  # 跳过公式
    result = val
    for pat, cn in patterns:
        result = re.sub(r'\b' + pat + r'\b', cn, result)  # \b 整词匹配
    return result

def translate_sheet(ws, patterns):
    count = 0
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column):
        for cell in row:
            if cell.value is None: continue
            val = cell.value
            if isinstance(val, str) and not val.startswith("="):
                if re.search(r'[a-zA-Z]{2,}', val):
                    translated = translate(val, patterns)
                    if translated != val:
                        cell.value = translated
                        count += 1
    return count
```

## 2. 精细残留诊断白名单（extract_real_remaining.py）

```python
# 白名单 — 以下内容不应翻译
KEEP_ENGLISH = {
    # 单位符号
    'kPa', 'ppm', 'ppmv', 'bar', 'min', 'sec', 'BTU', 'Btu', 'kcal',
    'atm', 'psi', 'mmHg', 'vol', 'gal', 'liter', 'mol', 'g', 'cal',
    'kg', 'm3', 'kW', 'kgsec', 'lbmin',
    # 专业缩写
    'NFPA', 'ERPG', 'ERPG1', 'ERPG2', 'ERPG3', 'LFL', 'UFL',
    'PFD', 'IEF', 'CAS', 'CCPS', 'CHEF', 'MTTR', 'MTBF',
    'BLEVE', 'VCE', 'TNT', 'LOPA', 'BPCS', 'SIF', 'IPL', 'DMSO',
    # 公式变量名
    'Psat', 'DHV', 'DHr', 'VPES', 'VEquip', 'QPV', 'QChem',
    'DHR', 'TNR', 'Tmax', 'TMax', 'Pmax', 'TBurst',
    'TAmb', 'T0', 'P0', 'PA', 'PB', 'Mw',
    # 机构/人名
    'AIChE', 'Dow', 'Baker', 'Strehlow', 'Tang', 'Britter', 'McQuaid',
    'Crowl', 'Louvar', 'Mannan', 'Perry', 'RAST', 'Lee',
}
# 过滤后输出真正需要翻译的残留内容
meaningful = [w for w in eng_words if w not in KEEP_ENGLISH and len(w) >= 2]
```
