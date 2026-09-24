# -*- coding: utf-8 -*-
"""
L2-A：CAMEO 1306 份 PDF → cameo_reactivity.json
   抽取字段（每份按 5.x 节结构化）：
     5.1 Reactivity with Water / 5.2 Reactivity with Common Materials /
     5.3 Stability During Transport / 5.4 Neutralizing Agents /
     5.5 Polymerization / 5.6 Inhibitor of Polymerization
   另抽头部标识（名称/公式），与 ray-chem-property 的 CAMEO 导航对得上
"""
import sys, io, os, re, json, glob, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import fitz

D = r"D:\Work\02-Tech Documents\Process Designing\Calculation Tools\Property Data\CAMEO"
OUT = r"E:\LingXi-DSH\sessions\Chemical Compatible Matrix\_process\build\cameo_reactivity.json"

SECTIONS = [
    ("water", r"5\.1?\s*Reactivity with Water"),
    ("common_materials", r"5\.2\s*Reactivity with Common Materials"),
    ("transport", r"5\.3\s*Stability During Transport"),
    ("neutralizer", r"5\.4\s*Neutralizing Agents for Acids and Caustics"),
    ("polymerize", r"5\.5\s*Polymerization"),
    ("inhibitor", r"5\.6\s*Inhibitor of Polymerization"),
]
# 截断边界＝各节标题的正则（标题内部可能有硬换行 → 空格放宽为 \s+；勿再 escape）
FLEX = [re.sub(r"(?<!\\) ", r"\\s+", p) for _, p in SECTIONS]
HEAD_RE_ALT = "|".join(FLEX)
FLEX_PAIRS = list(zip([k for k, _ in SECTIONS], FLEX))   # 匹配与边界都用放宽版
END = re.compile(r"6\.\s*WATER POLLUTION|6\.1\s*Aquatic")
NEXT_HEAD = re.compile(HEAD_RE_ALT + r"|6\.\s*WATER POLLUTION|6\.1\s*Aquatic")


def parse(t, flex_pairs):
    rec = {}
    for k, pat in flex_pairs:
        m = re.search(pat, t)
        if not m:
            rec[k] = None
            continue
        rest = t[m.end():]
        m2 = NEXT_HEAD.search(rest)          # 截到下一节标题（修复横向洇段）
        seg = rest[:m2.start()] if m2 else rest[:800]
        seg = re.sub(r"\s+", " ", seg).strip(" :. ")
        rec[k] = seg or None
    return {k: v for k, v in rec.items()}


def header(t, fname):
    name = None
    for line in t.splitlines()[:4]:
        ln = line.strip()
        if 3 <= len(ln) <= 60 and ln.isupper() and re.match(r"^[A-Z0-9 ,\-\(\)' ]+$", ln):
            name = ln.title()
            break
    code = os.path.splitext(os.path.basename(fname))[0]
    cas = re.search(r"CAS Registry No\.\s*[:\.]?\s*(\d{2,7}-\d{2}-\d)", t)
    formula = re.search(r"2\.2\s+Formula\s*[:\.]\s*([^\n]{1,60})", t)
    rg = re.search(r"CG\s+Compatibility Group\s*[:\.]\s*([^\n]{1,80})", t)
    return {"file": code + ".pdf", "name": name, "cas": cas.group(1) if cas else None,
            "formula": formula.group(1).strip() if formula else None,
            "reactive_group": rg.group(1).strip() if rg else None,
            "reactive_group_field": "CG Compatibility Group (CHRIS 2.1)",
            "react": parse(t, FLEX_PAIRS)}


files = sorted(glob.glob(os.path.join(D, "*.pdf")))
print(f"PDF 总数 {len(files)}")
out = {}
bad = []
for k, p in enumerate(files):
    try:
        doc = fitz.open(p)
        t = "\n".join(doc[i].get_text() for i in range(doc.page_count))
        doc.close()
        if not t.strip():
            bad.append(os.path.basename(p) + "(空文字层)")
            continue
        out[os.path.splitext(os.path.basename(p))[0]] = header(t, p)
    except Exception as e:
        bad.append(os.path.basename(p) + f"({e})")
    if (k + 1) % 200 == 0:
        print(f"  …{k+1}/{len(files)}")
print(f"完成 {len(out)} 份；失败 {len(bad)} {bad[:6]}")

# 抽样自检：3 份的 5.2 段与水反应性
import random
random.seed(7)
for fid in random.sample(list(out.keys()), 3):
    r = out[fid]
    print(f"\n样例 {fid}: {r['name']!r} cas={r['cas']}")
    for k, v in r["react"].items():
        print(f"   {k}: {str(v)[:90]}")

json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(f"\n[EXIT] {OUT} = {os.path.getsize(OUT):,} B")
