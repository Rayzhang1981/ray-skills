# -*- coding: utf-8 -*-
"""
L2-B/C：Bretherick 8th Ed → breth_entries.json（v9 · 双栏感知 + 视觉行重建 + 状态机）
   ① 每页把 fitz dict 行按【栏（x<260=左 / 其余右）× y 排序】重建视觉行序
   ② 条目锚＝左缘 AdvP193F@≈10 的 ^\d{1,4}[a-z]? 行（可与标题同行或分行）
   ③ 标题＝锚后第一行非 See/非纯头行；CAS=[NN-NN-N]；See/related/other 引用
"""
import sys, io, os, re, json, hashlib, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import fitz

PDF = (r"D:\Work\02-Tech Documents\Process Designing\Calculation Tools\Property Data"
       r"\Property Reference Books\Bretherick‘s Handbook of Reactive Chemical Hazards"
       r"\Bretherick‘s Handbook of Reactive Chemical Hazards 8thEd-2017.pdf")
OUT = r"E:\LingXi-DSH\sessions\Chemical Compatible Matrix\_process\build\breth_entries.json"
CAS_RE = re.compile(r"\[(\d{2,7}-\d{2}-\d[0-9A-Za-z*]*)\]")
NO_LINE = re.compile(r"^†?†?\s*(\d{1,4}[a-z]?)(?:\s+([^\[\n]{2,110}))?$")
# ⚠️ 高危条目编号带 † 前缀（‡/† 两段实为 Bretherick 危度记号）——实测 p995 '†4515'


def page_rows(doc_pno):
    """一页 → 按栏×y 重建的行序列[(x0, font0, size0, text)]"""
    d = doc_pno.get_text("dict")
    rows = []
    for blk in d["blocks"]:
        if blk.get("type") != 0:
            continue
        for ln in blk.get("lines", []):
            spans = [s for s in ln.get("spans", []) if s["text"].strip()]
            if not spans:
                continue
            txt = " ".join(s["text"].strip() for s in spans).strip()
            if not txt:
                continue
            col = 0 if spans[0]["bbox"][0] < 305 else 1   # 栏界实测 ≈305（左栏正文含公式符号 x 到 ~280）
            rows.append((col, round(ln["bbox"][1], 0), round(spans[0]["bbox"][0], 0),
                         spans[0]["font"], round(spans[0]["size"], 1), txt))
    rows.sort(key=lambda r: (r[0], r[1]))          # 栏 × y
    return [(x, f, s, t) for _, _, x, f, s, t in rows]


doc = fitz.open(PDF)
entries, cur = [], None


def new_entry(no, page, title0, dag=False):
    return {"no": no, "title": (title0 or "")[:140], "page": page, "cas": None,
            "refs": [], "related": [], "head": [], "dag": bool(dag)}


def flush():
    global cur
    if cur is not None and cur.get("no") is not None:
        rec = dict(cur)
        rec["head"] = "".join(rec["head"])[:380]
        entries.append(rec)
        cur = None


for pno in range(doc.page_count):
    for x, f, sz, line_txt in page_rows(doc[pno]):
        styl = (f.startswith("AdvP193F") and abs(sz - 10.0) < 0.4
                and (50 <= x <= 100 or 295 <= x <= 335))   # 左栏缘 / 右栏缘 两个栏位起点
        mm = NO_LINE.match(line_txt) if styl else None
        if mm:                                     # 条目锚
            flush()
            dag = line_txt.lstrip().startswith("†")     # †＝Bretherick 高危记号
            cur = new_entry(mm.group(1), pno + 1, mm.group(2), dag)
            continue
        if cur is None:
            continue
        if not cur["title"] and not CAS_RE.search(line_txt) \
           and not line_txt.lower().startswith("see "):
            cur["title"] = line_txt[:140]          # 标题＝锚后第一行非 See 行
            continue
        styl_t = (f.startswith("AdvP193F") and abs(sz - 10.0) < 0.35)
        if styl_t and len(cur["title"]) < 120 and not CAS_RE.search(cur["title"]):
            cur["title"] = (cur["title"] + " " + line_txt).strip()[:140]
            continue
        m = CAS_RE.search(line_txt)
        if m and cur["cas"] is None:
            cur["cas"] = m.group(1)
        low = line_txt
        if re.match(r"^See\s+related\s+", low, re.I):
            if len(cur["related"]) < 18:
                cur["related"].append(re.sub(r"^See\s+related\s+", "", low, flags=re.I).upper())
        elif re.match(r"^See\s+other\s+", low, re.I):
            if len(cur["related"]) < 18:
                cur["related"].append(re.sub(r"^See\s+other\s+", "", low, flags=re.I).upper())
        elif re.match(r"^See\s+[A-Z(]", low) and len(low) < 90 and len(cur["refs"]) < 26:
            cur["refs"].append(re.sub(r"^See\s+", "", low))
        elif len(" ".join(cur["head"])) < 360:
            cur["head"].append(line_txt)
doc.close()
flush()

print(f"[1] 条目 {len(entries)}")
nos = [int(re.match(r"(\d+)", str(e["no"])).group(1)) for e in entries]
uniq = len(set(str(e["no"]) for e in entries))
print(f"    编号 {min(nos)}–{max(nos)}｜唯一 {uniq}｜范围占比 {len(nos)/(max(nos)-min(nos)+1)*100:.0f}%")
mono = sum(1 for a, b in zip(nos, nos[1:]) if b > a)
print(f"    单调递增 {mono}/{len(nos)-1}")
cas_n = sum(1 for e in entries if e["cas"])
rel_n = sum(1 for e in entries if e["related"])
ref_n = sum(len(e["refs"]) for e in entries)
print(f"    CAS {cas_n}｜related 条目 {rel_n}｜refs {ref_n}")
hyd = [(e["no"], e["title"], e["page"]) for e in entries if e["cas"] == "302-01-2"]
print("  肼 302-01-2:", hyd[:4])
for kw in ("Ethylene oxide", "Octylamine"):
    hh = [e for e in entries if kw.lower() in (e["title"] or "").lower()]
    print(f"  {kw}: {len(hh)} 条", [(x["no"], x["title"][:30]) for x in hh[:5]])

json.dump({str(e["no"]): {k: v for k, v in e.items() if k != "no"} for e in entries},
          open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"[EXIT] {OUT} = {os.path.getsize(OUT):,} B  "
      f"SHA-256 = {hashlib.sha256(open(OUT, 'rb').read()).hexdigest().upper()[:16]}")
