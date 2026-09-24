# -*- coding: utf-8 -*-
"""
L2-D：危险化学品安全技术全书·通用卷 3rd Ed → whpdj_incompat.json
   抽每条目 第十部分「稳定性和反应性」五字段：
     稳定性 / 危险反应 / 避免接触的条件 / 禁配物 / 危险的分解产物
   锚＝「化学品中文名 <值>」行；CAS 由 ray-chem-property 既有索引按名称回填
"""
import sys, io, os, re, json, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import fitz

BOOK = (r"D:\Work\02-Tech Documents\Process Designing\Calculation Tools\Property Data"
        r"\Property Reference Books\危险化学品安全技术全书-通用卷-3rd Ed.pdf")
OUT = r"E:\LingXi-DSH\sessions\Chemical Compatible Matrix\_process\build\whpdj_incompat.json"
IDX = r"C:\Users\rayzh\.workbuddy\skills\ray-chem-property\data\危险品全书-通用卷索引.json"
FIELDS = ["稳定性", "危险反应", "避免接触的条件", "禁配物", "危险的分解产物"]

# ---------- ① 读全书，页级清洗 ----------
print("[1] 读全书…")
doc = fitz.open(BOOK)
pages_txt = []
for pg in range(doc.page_count):
    t = doc[pg].get_text()
    keep = [ln.strip() for ln in t.split("\n")
            if ln.strip() and not re.fullmatch(r"[\d\s·\-—]{1,8}", ln.strip())]
    pages_txt.append(f"@@P{pg}@@" + "\n".join(keep))
doc.close()
book = "\n".join(pages_txt)
print(f"  总字符 {len(book):,}")

# ---------- ② 条目锚（化学品中文名 行；别名串按 ; 切开取主名） ----------
seen, anchors = set(), []
for m in re.finditer(r"化学品中文名\s*([^\n]{2,60})", book):
    raw = m.group(1).strip()
    name = re.split(r"[;；]", raw)[0].strip()      # 主名（与既有索引同口径）
    if not name or name in seen:
        continue
    seen.add(name)
    anchors.append((name, raw, m.start()))
print(f"[2] 首现锚(主名) {len(anchors)}")

# ---------- ③ 逐块抽第十部分 ----------
P10 = re.compile(r"第十部分\s*稳定性和反应性")
P11 = re.compile(r"第十一部分")
LABEL_LINE = {f: re.compile(r"(?m)^[ \t]*" + re.escape(f) + r"[ \t]*") for f in FIELDS}

def page_span(s):
    tags = re.findall(r"@@P(\d+)@@", s)
    return [int(tags[0]), int(tags[-1])] if tags else []

def strip_tags_and_name(s, name):
    s = re.sub(r"@@P\d+@@", " ", s)
    s = re.sub(r"(?m)^" + re.escape(name) + r"\s*$", " ", s)   # 运行页眉重复条目名
    s = re.sub(r"\s+", "", s)                                  # 中文正文无空格
    return s.strip()

out = {}
n_with10 = 0
for k, (name, raw, pos0) in enumerate(anchors):
    pos1 = (anchors[k + 1][2] if k + 1 < len(anchors) else len(book))
    block = book[pos0:pos1]
    m10 = P10.search(block)
    if not m10:
        continue
    n_with10 += 1
    tail = P11.search(block, m10.end())
    seg = block[m10.start(): tail.start() if tail else len(block)]
    rec, residual = {}, seg
    # 按五个标签行首依次切（标签在全块中按预定顺序出现）
    for fi, f in enumerate(FIELDS):
        m = LABEL_LINE[f].search(residual)
        if not m:
            rec[f] = None
            continue
        nxt = LABEL_LINE[FIELDS[fi + 1]].search(residual, m.end()) if fi + 1 < len(FIELDS) else None
        value_raw = residual[m.end(): nxt.start() if nxt else len(residual)]
        rec[f] = strip_tags_and_name(value_raw, name) or None
    out[name] = {"name_full": raw, "cas": None, "fields": rec,
                 "pages": page_span(block),
                 "book": "危险化学品安全技术全书·通用卷 3rd Ed"}
print(f"[3] 有第十部分 {n_with10} 条")

# ---------- ④ CAS 回填（别名各段 + 去括号形态都试） ----------
idx = json.load(open(IDX, encoding="utf-8"))
name2cas = {}
for cas, e in idx.items():
    if not isinstance(e, dict):
        continue
    for alias in re.split(r"[;；]", str(e.get("name_cn", ""))):
        a = alias.strip()
        if not a:
            continue
        name2cas.setdefault(a, cas)
        base = re.sub(r"[\[［\(（].*$", "", a).strip()
        if base and base not in name2cas:
            name2cas.setdefault(base, cas)
n_cas = 0
for name, r in out.items():
    cands = [name]
    base = re.sub(r"[\[［\(（].*$", "", name).strip()
    if base and base != name:
        cands.append(base)
    for a in re.split(r"[;；]", r.get("name_full", "")):
        frag = a.strip()
        if frag:
            cands.append(frag)
    for c in cands:
        if c in name2cas:
            r["cas"], r["cas_key"] = name2cas[c], c
            n_cas += 1
            break
print(f"[4] CAS 回填 {n_cas}/{len(out)}")

# ---------- ⑤ 自检：水合肼 + 统计 ----------
for probe in ("水合肼[含水36%]", "双氧水", "环氧乙烷", "丙酮"):
    hit = out.get(probe)
    if not hit:
        print(f"  （未见 {probe}）")
        continue
    print(f"\n样例 {probe}（cas={hit['cas']} 页{hit['pages']}）")
    for f, v in hit["fields"].items():
        print(f"   {f}: {str(v)[:80]}")
cnt = collections.Counter()
for r in out.values():
    for f, v in r["fields"].items():
        cnt[f] += 1 if v and v not in ("无资料", "无资料。") else 0
print("\n字段非『无资料』计数:", dict(cnt))
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"[EXIT] {OUT} = {os.path.getsize(OUT):,} B")
