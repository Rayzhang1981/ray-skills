# -*- coding: utf-8 -*-
"""
ray-hazop-lopa · 质量自检②：报告 HTML 自动扫描（12 点清单自动化子集）
检查项：
  Q1  乱码：\ufffd 计数 = 0
  Q2  HTML 结构：<section>/</section> 配对、</html> 闭合、<table> 配对
  Q3  场景编号：x.y 格式提取 → 检查重复与断号（提示）
  Q4  统计口径：风险统计表中"编号场景/定量场景/行动项场景"三行数量一致性（人工核对提示）
  Q5  Rf 完整性：行动项闭环表每行是否含改进行动后风险数字
  Q6  矩阵维度：是否标注 7×5（防 5×5 错标）
  Q7  IPL 三态：是否出现"待验证/不成立"（有则提示人工确认 PFD 处理）
  Q8  残余风险：是否含"残余风险"章节
用法: python qa_scan.py <报告.html>
退出码：0=全部通过，1=存在 FAIL。
"""
import argparse, re, sys

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('html')
    a = ap.parse_args()
    try:
        s = open(a.html, encoding='utf-8').read()
    except Exception as e:
        print(f"[ERROR] 无法读取: {e}")
        sys.exit(1)

    fails, warns, passes = [], [], []

    # Q1 乱码
    n = s.count('\ufffd')
    (passes if n == 0 else fails).append(f"Q1 乱码扫描: \ufffd = {n} {'✅' if n==0 else '❌ FAIL'}")

    # Q2 HTML 结构
    sc_open, sc_close = s.count('<section'), s.count('</section>')
    tb_open, tb_close = s.count('<table'), s.count('</table>')
    html_close = '</html>' in s
    if sc_open == sc_close and tb_open == tb_close and html_close:
        passes.append(f"Q2 HTML 结构: section {sc_open}/{sc_close} table {tb_open}/{tb_close} </html> ✅")
    else:
        fails.append(f"Q2 HTML 结构: section {sc_open}/{sc_close} table {tb_open}/{tb_close} </html>={html_close} ❌ FAIL")

    # Q3 场景编号（仅取场景号候选：x.y 且 y≤20，排除 kF 系数/密度等小数）
    ids = re.findall(r'([1-8])\.(\d{1,2})', s)
    cand = [f"{x}.{y}" for x, y in ids if int(y) <= 20]
    seen, dup = set(), []
    for i in cand:
        if i in seen and i not in dup: dup.append(i)
        seen.add(i)
    if dup:
        warns.append(f"Q3 场景编号: 疑似重复 {sorted(dup)} ⚠️ 请人工核对（模板生成通常无重复）")
    else:
        passes.append(f"Q3 场景编号: 候选 {len(seen)} 个，无重复 ✅（断号需人工核对节点表）")

    # Q4 统计口径
    if '统计口径' in s:
        passes.append("Q4 统计口径: 存在统计口径表 ✅（数量一致性请人工核对）")
    else:
        warns.append("Q4 统计口径: 未找到统计口径表 ⚠️ 检查")

    # Q5 Rf（行动项表：A\d+ 行中 Rf 列为 1-4 数字或 "—"；"—" 仅提示）
    rows = re.findall(r'<tr>\s*<td[^>]*class="num">(A\d+)</td>(.*?)</tr>', s, re.S)
    missing_rf = [rid for rid, body in rows
                  if not re.search(r'<td[^>]*class="num">[0-4]</td>', body) and '—' not in body]
    dash_rf = [rid for rid, body in rows if '—' in body]
    if not missing_rf:
        passes.append(f"Q5 Rf 完整性: 行动项 {len(rows)} 条，Rf 均有值 ✅")
    else:
        fails.append(f"Q5 Rf 完整性: 行动项 {len(rows)} 条，缺 Rf: {missing_rf} ❌ FAIL")
    if dash_rf:
        warns.append(f"Q5 Rf: 管理/核实类行动项 {dash_rf} 用 '—'（建议补预期 Rf 便于闭环）⚠️")

    # Q6 矩阵维度
    if re.search(r'矩阵（7×5', s) or re.search(r'7×5', s):
        passes.append("Q6 矩阵维度: 标注 7×5 ✅")
    elif re.search(r'5×5', s):
        fails.append("Q6 矩阵维度: 标注 5×5 ❌ FAIL（应为 7×5）")
    else:
        warns.append("Q6 矩阵维度: 未找到矩阵维度标注 ⚠️")

    # Q7 IPL 三态
    if '待验证' in s or '不成立' in s:
        warns.append("Q7 IPL 三态: 存在待验证/不成立标注 ⚠️ 请确认 PFD 处理符合规则")
    else:
        passes.append("Q7 IPL 三态: 无待验证/不成立标注（如无相关场景即正常）✅")

    # Q8 残余风险
    if '残余风险' in s:
        passes.append("Q8 残余风险: 含残余风险声明 ✅")
    else:
        fails.append("Q8 残余风险: 缺少残余风险声明 ❌ FAIL")

    print("== 质量扫描结果 ==")
    for p in passes: print("  ", p)
    for w in warns:  print("  ", w)
    for f in fails:  print("  ", f)
    print(f"\n通过 {len(passes)} | 警告 {len(warns)} | 失败 {len(fails)}")
    sys.exit(0 if not fails else 1)

if __name__ == '__main__':
    main()
