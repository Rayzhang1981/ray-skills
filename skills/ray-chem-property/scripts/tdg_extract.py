# -*- coding: utf-8 -*-
"""TDG 危险货物一览表 → UN 编号 + 运输类别 索引。
P203-679 表格：UN编号(x<90) | 名称(乱码) | 主类别 | 副危险 | 包装类 | ...
用严格类别正则识别主类别/副危险，避开乱码名称。"""
import fitz, re, json, os, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else r"D:/Work/02-Tech Documents/Process Designing/Calculation Tools/Property Data/Property Reference Books/TDG第23版第1卷+第2卷.pdf"
OUT = sys.argv[2] if len(sys.argv) > 2 else r"~/LingXi/2026-08-26-物性书索引构建/output/TDG-UN索引.json"

CLASS_RE = re.compile(r'^(1\.[1-6][A-Z]?|2\.[1-3]|3|4\.[1-3]|5\.[12]|6\.[12]|7|8|9)$')
UN_RE = re.compile(r'^\d{4}$')

doc = fitz.open(SRC)
index = {}
for pi in range(doc.page_count):
    words = doc[pi].get_text("words")
    # 按行聚类
    rows = {}
    for w in words:
        y = round(w[1])
        rows.setdefault(y, []).append(w)
    for y in sorted(rows):
        ws = sorted(rows[y], key=lambda w: w[0])
        # UN 编号：x<90 的 4 位数字
        un = [w[4] for w in ws if UN_RE.match(w[4]) and w[0] < 90]
        if not un:
            continue
        un_no = un[0]
        # 主类别 + 副危险：都在 x 200-300 区间，按顺序第一个是主类别，后续是副危险
        main_cls = None
        sub_risk = []
        for w in ws:
            if 200 < w[0] < 300 and CLASS_RE.match(w[4]):
                if main_cls is None:
                    main_cls = w[4]
                else:
                    sub_risk.append(w[4])
        if main_cls:
            index[un_no] = {
                'class': main_cls,
                'subsidiary': sub_risk if sub_risk else None,
            }
doc.close()

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=1)
print('TDG UN 索引:', len(index), '条,', os.path.getsize(OUT)//1024, 'KB')
