# -*- coding: utf-8 -*-
"""
ray-hazop-lopa · 输入自动化③：从工艺/热评估文本提取关键参数
用法:
  1) 先用 markitdown / pdf 技能把 PDF 转文本（txt/md）
  2) python extract_inputs.py report.md            # 单文件
     python extract_inputs.py 目录/                # 目录批量
输出: 参数名: 值 + 单位 + 原文摘录（便于人工核对）
提取项：反应热、绝热温升 ΔTad、MTSR、TMRad、起始分解温度、分解热、
        最大温升速率、Phi、MAWP、浓度、密度、SADT 等。
"""
import argparse, os, re, sys

# 关键词 → (参数名, 正则, 单位后缀提示)
RULES = [
    (r'绝热温升|ΔTad|ΔT_ad|Delta T',        'ΔTad (K)',     r'(\d{2,4}(?:\.\d+)?)\s*(K|℃|°C)'),
    (r'MTSR',                                'MTSR (℃)',     r'(\d{1,3}(?:\.\d+)?)\s*(℃|°C)'),
    (r'TMRad|TD8|TD24',                      'TMRad (℃)',    r'(\d{1,3}(?:\.\d+)?)\s*(℃|°C)'),
    (r'反应热',                               '反应热 (kJ/kg)', r'(\d{2,6}(?:\.\d+)?)\s*(kJ/kg|kJ·kg)'),
    (r'分解热',                               '分解热 (J/g)',   r'(\d{2,6}(?:\.\d+)?)\s*(J/g|kJ/g)'),
    (r'起始放热|起始分解|起始分解温度',        '起始分解 (℃)',   r'(\d{1,3}(?:\.\d+)?)\s*(℃|°C)'),
    (r'最大温升速率',                         '最大温升 (℃/min)', r'(\d{1,3}(?:\.\d+)?)\s*(℃/min|K/min)'),
    (r'Phi\s*=|φ\s*=|phi\s*=',               'Phi',          r'(\d{1,2}(?:\.\d+)?)'),
    (r'MAWP|最大允许工作压力',                'MAWP (bar)',   r'(\d{1,2}(?:\.\d+)?)\s*(bar|MPa|kPa)'),
    (r'密度',                                 '密度 (kg/L)',   r'(\d\.\d{2,3})\s*(kg/L|g/mL|g/cm)'),
    (r'浓度|含量',                            '浓度 (wt%)',    r'(\d{1,3})\s*[%％]'),
    (r'SADT',                                 'SADT (℃)',     r'(\d{1,3}(?:\.\d+)?)\s*(℃|°C)'),
    (r'停留时间|保压时间|滴加时间',            '时间 (h)',      r'(\d{1,3}(?:\.\d+)?)\s*(h|小时|hr)'),
]

def extract(text):
    """关键词就近匹配：收集关键词所有出现位置的候选值（去重，最多 3 个），供人工核对"""
    out = []
    for kw, name, pat in RULES:
        vals = []
        for m_kw in re.finditer(kw, text, re.I):
            win = text[max(0, m_kw.start()-30): m_kw.end()+150]
            m = re.search(pat, win, re.I)
            if m and m.group(1) not in vals:
                vals.append(m.group(1))
            if len(vals) >= 3:
                break
        for v in vals:
            out.append((name, v, ''))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('path', help='文件或目录（目录则批量处理 *.md/*.txt）')
    ap.add_argument('--show-ctx', action='store_true', help='显示原文摘录')
    a = ap.parse_args()

    files = []
    if os.path.isdir(a.path):
        for root, _, fs in os.walk(a.path):
            files += [os.path.join(root, f) for f in fs if f.endswith(('.md', '.txt'))]
    else:
        files = [a.path]

    for f in files:
        try:
            text = open(f, encoding='utf-8').read()
        except UnicodeDecodeError:
            text = open(f, encoding='gbk', errors='ignore').read()
        print(f"\n== {os.path.basename(f)} ==")
        rows = extract(text)
        if not rows:
            print("  （未匹配到参数，检查文本是否已转 Markdown）")
        for name, val, ctx in rows:
            line = f"  {name}: {val}"
            if a.show_ctx:
                line += f"\n      摘录: {ctx}"
            print(line)
    print("\n提示: 提取值为正则首匹配，须人工核对上下文；估算/缺口项按数据来源审计三态标注。")

if __name__ == '__main__':
    main()
