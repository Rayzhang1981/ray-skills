# -*- coding: utf-8 -*-
"""
ray-hazop-lopa · 行动项闭环⑤：从报告 HTML 导出行动项 Excel（openpyxl）
用法: python export_actions.py 报告.html [-o 输出.xlsx]
依赖: venv python（含 openpyxl）:
  C:\\Users\\rayzh\\.workbuddy\\binaries\\python\\envs\\default\\Scripts\\python.exe
"""
import argparse, os, re, sys

def strip_tags(s):
    s = re.sub(r'<[^>]+>', '', s)
    return s.replace('&nbsp;', ' ').replace('&gt;', '>').replace('&lt;', '<').replace('&amp;', '&').strip()

def parse(html):
    """解析行动项闭环表：找含 A\\d+ 编号的 <tr>，按 <td> 切列"""
    rows = []
    for m in re.finditer(r'<tr>\s*<td[^>]*class="num">(A\d+)</td>(.*?)</tr>', html, re.S):
        rid = m.group(1)
        tds = re.findall(r'<td[^>]*>(.*?)</td>', m.group(2), re.S)
        cells = [strip_tags(t) for t in tds]
        # 列序：# | 场景 | 行动建议 | 优先级 | Rf | 责任人 | 截止 | 状态
        row = {'#': rid}
        keys = ['场景', '行动建议', '优先级', 'Rf', '责任人', '截止', '状态']
        for i, k in enumerate(keys):
            row[k] = cells[i] if i < len(cells) else ''
        rows.append(row)
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('html')
    ap.add_argument('-o', '--out', default=None)
    a = ap.parse_args()
    try:
        import openpyxl
    except ImportError:
        print("[ERROR] 需要 openpyxl，请用 venv python 运行")
        sys.exit(1)
    rows = parse(open(a.html, encoding='utf-8').read())
    if not rows:
        print("[WARN] 未解析到行动项（检查表头格式：首列为 <td class=\"num\">A1</td>）")
        sys.exit(1)
    out = a.out or os.path.splitext(a.html)[0] + '-行动项.xlsx'
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = '行动项'
    header = ['#', '场景', '行动建议', '优先级', '改进行动后风险Rf', '责任人', '截止日期', '状态']
    ws.append(header)
    for r in rows:
        ws.append([r['#'], r['场景'], r['行动建议'], r['优先级'], r['Rf'], r['责任人'], r['截止'], r['状态']])
    widths = [6, 10, 60, 8, 10, 10, 10, 8]
    for i, w in enumerate(widths):
        ws.column_dimensions[chr(65+i)].width = w
    for cell in ws[1]:
        cell.font = openpyxl.styles.Font(bold=True)
    wb.save(out)
    print(f"[OK] 行动项 {len(rows)} 条 → {out}")

if __name__ == '__main__':
    main()
