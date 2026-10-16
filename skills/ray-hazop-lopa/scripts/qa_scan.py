# -*- coding: utf-8 -*-
"""
ray-hazop-lopa · 质量自检②：报告 HTML 自动扫描（12 点清单自动化子集）
检查项：
  Q1  乱码：\ufffd 计数 = 0
  Q2  HTML 结构：<section>/</section> 配对、</html> 闭合、<table> 配对
  Q3  场景编号：按「同一张表内」去重（跨表重复属正常多视图），逐表判定
  Q4  统计口径：风险统计表中"编号场景/定量场景/行动项场景"三行数量一致性（人工核对提示）
  Q5  Rf 完整性：按表头定位 Rf 列逐行取值（行/<td> 匹配均容忍 class 与配色 span）
  Q6  矩阵维度：是否标注 7×5（防 5×5 错标）
  Q7  IPL 三态：是否出现"待验证/不成立"（有则提示人工确认 PFD 处理）
  Q8  残余风险：是否含"残余风险"章节
用法: python qa_scan.py <报告.html>
退出码：0=全部通过，1=存在 FAIL。
"""
import argparse, re, sys

import sys
def _console_safe():
    """控制台编码护栏（2026-10-09 舰队级修复）。

    中文 Windows 下 stdout/stderr 走 cp936(GBK)。**输出被重定向或经管道捕获时**
    （自动验证 / 日志 / CI / subprocess PIPE），Python 按 locale 编码写流，
    遇到 GBK 无法表示的字符即抛 UnicodeEncodeError，**整段输出中断**；
    而交互式控制台走 WriteConsoleW(UTF-16)，同一字符却无碍
    => 该缺陷只在「捕获输出」时显形，最易漏测。

    处理：**保持流原编码不变**（中文在 GBK 控制台仍正常），
    仅把不可表示的字符降级为 '?'，从而永不中断。
    注意：不要改成 encoding="utf-8" —— 那会让 GBK 控制台下的中文变乱码。
    """
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(errors="replace")
        except Exception:
            pass


_console_safe()


def strip_tags(s):
    """去标签取纯文本：<td class="num"><span class="lv-danger">3</span></td> → '3'。

    校验器必须与渲染形式解耦 —— 风险值被配色 span 包裹是正常渲染，
    不能因此判成「缺值」（历史缺陷：只认裸数字，见 2026-09-30 修复记）。
    """
    return re.sub(r'<[^>]+>', '', s).replace('&nbsp;', ' ').strip()
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
        passes.append(f"Q2 HTML 结构: section {sc_open}/{sc_close} table {tb_open}/{tb_close} </html> [OK]")
    else:
        fails.append(f"Q2 HTML 结构: section {sc_open}/{sc_close} table {tb_open}/{tb_close} </html>={html_close} [X] FAIL")

    # Q3 场景编号（**同一张表内**去重；跨表重复属正常的多视图呈现）
    #   旧版对全文做去重 → 工作表/速览/行动项表各出现一次同一编号即被全判「疑似重复」，
    #   70+ 条噪声淹没真信号。改为逐表判定：一张表内同一编号出现两次才是真缺陷。
    dup_tables = []
    for tbl in re.findall(r'<table[^>]*>(.*?)</table>', s, re.S):
        trs = re.findall(r'<tr[^>]*>(.*?)</tr>', tbl, re.S)
        if not trs:
            continue
        hdr = [strip_tags(c) for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', trs[0], re.S)]
        if '场景' not in hdr:
            continue
        col = hdr.index('场景')
        seen_t, dup_t = set(), []
        for tr in trs[1:]:
            cells = [strip_tags(c) for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', tr, re.S)]
            if len(cells) <= col:
                continue
            m = re.match(r'([1-8]\.\d{1,2})', cells[col])
            if not m:
                continue
            v = m.group(1)
            if v in seen_t and v not in dup_t:
                dup_t.append(v)
            seen_t.add(v)
        if dup_t:
            dup_tables.append(dup_t)
    if dup_tables:
        warns.append(f"Q3 场景编号: 存在同一表内重复 {dup_tables} [!] 请人工核对")
    else:
        passes.append("Q3 场景编号: 各表内编号无重复 [OK]（断号需人工核对节点表）")
    # Q4 统计口径
    if '统计口径' in s:
        passes.append("Q4 统计口径: 存在统计口径表 [OK]（数量一致性请人工核对）")
    else:
        warns.append("Q4 统计口径: 未找到统计口径表 [!] 检查")

    # Q5 Rf 完整性（**按表头定位 Rf 列**后逐行取值，与渲染形式解耦）
    #   旧版两个缺陷：① 行匹配只认裸 <tr>，带 class 的行动行整表漏检（空匹配假通过）；
    #   ② 值判定只认裸数字，被配色 span 包裹时误判「缺 Rf」。此处一并修掉。
    act_rows, missing_rf, dash_rf = [], [], []
    for tbl in re.findall(r'<table[^>]*>(.*?)</table>', s, re.S):
        trs = re.findall(r'<tr[^>]*>(.*?)</tr>', tbl, re.S)
        if not trs:
            continue
        hdr = [strip_tags(c) for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', trs[0], re.S)]
        if 'Rf' not in hdr:
            continue
        col = hdr.index('Rf')
        for tr in trs[1:]:
            cells = [strip_tags(c) for c in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', tr, re.S)]
            if not cells or not re.fullmatch(r'A\d+', cells[0]):
                continue
            rid = cells[0]
            val = cells[col] if col < len(cells) else ''
            act_rows.append(rid)
            if re.fullmatch(r'[0-4]', val):
                continue
            if '—' in val:
                dash_rf.append(rid)
            else:
                missing_rf.append(f"{rid}({val or '空'})")
    if not act_rows:
        warns.append("Q5 Rf 完整性: 未找到行动项表（要求表头含 Rf 列、首列为 A1 形式）[!] 请核对表格结构")
    elif not missing_rf:
        passes.append(f"Q5 Rf 完整性: 行动项 {len(act_rows)} 条，Rf 均有值 [OK]")
    else:
        fails.append(f"Q5 Rf 完整性: 行动项 {len(act_rows)} 条，缺 Rf: {missing_rf} [X] FAIL")
    if dash_rf:
        warns.append(f"Q5 Rf: 管理/核实类行动项 {dash_rf} 用 '—'（建议补预期 Rf 便于闭环）[!]")
    # Q6 矩阵维度
    if re.search(r'矩阵（7×5', s) or re.search(r'7×5', s):
        passes.append("Q6 矩阵维度: 标注 7×5 [OK]")
    elif re.search(r'5×5', s):
        fails.append("Q6 矩阵维度: 标注 5×5 [X] FAIL（应为 7×5）")
    else:
        warns.append("Q6 矩阵维度: 未找到矩阵维度标注 [!]")

    # Q7 IPL 三态
    if '待验证' in s or '不成立' in s:
        warns.append("Q7 IPL 三态: 存在待验证/不成立标注 [!] 请确认 PFD 处理符合规则")
    else:
        passes.append("Q7 IPL 三态: 无待验证/不成立标注（如无相关场景即正常）[OK]")

    # Q8 残余风险
    if '残余风险' in s:
        passes.append("Q8 残余风险: 含残余风险声明 [OK]")
    else:
        fails.append("Q8 残余风险: 缺少残余风险声明 [X] FAIL")

    print("== 质量扫描结果 ==")
    for p in passes: print("  ", p)
    for w in warns:  print("  ", w)
    for f in fails:  print("  ", f)
    print(f"\n通过 {len(passes)} | 警告 {len(warns)} | 失败 {len(fails)}")
    sys.exit(0 if not fails else 1)

if __name__ == '__main__':
    main()
