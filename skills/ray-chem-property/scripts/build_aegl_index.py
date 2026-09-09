# -*- coding: utf-8 -*-
"""构建 EPA AEGL 本地索引：下载 Compiled AEGL PDF → 解析 → JSON 索引。

背景（2026-08-15 实测）：
- EPA AEGL 导航页 https://www.epa.gov/aegl/access-acute-exposure-guideline-levels-aegls-values#final
  是索引页（按 Final/Interim/Proposed 列化学品链接），本身不含数值；
- 真正的全量数据入口是 Compiled AEGL values 页 → 一个按 CAS 排序的 PDF：
  https://www.epa.gov/sites/default/files/2018-08/documents/compiled_aegls_update_27jul2018.pdf (1.61MB, 76页, 188 个 Final AEGLs)
- PDF 数据块格式（可正则解析）：
    56-23-5 Carbon tetrachloride (ppm)
    10 min 30 min 60 min 4 hr 8 hr
    AEGL 1 NR NR NR NR NR
    AEGL 2 27 18 13 7.6 5.8
    AEGL 3 700 450 340 200 150

用法：
  python scripts/build_aegl_index.py                          # 下载并解析 → ../data/AEGL索引.json
  python scripts/build_aegl_index.py --pdf 已下载.pdf          # 用本地 PDF
  python scripts/build_aegl_index.py --query 67-64-1          # 只查一个 CAS

输出：data/AEGL索引.json
  {"67-64-1": {"name": "Acetone", "unit": "ppm", "aegl1_10": null, "aegl1_60": null,
               "aegl2_10": "2500", "aegl2_60": "1500", "aegl3_10": "20000", "aegl3_60": "12000", "note": ""}, ...}
字段键与 field_schema.json 的 aegl*_10/_60（模板 CI~CN 列）对齐。
"""
import argparse
import json
import os
import re
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "data"))
PDF_URL = "https://www.epa.gov/sites/default/files/2018-08/documents/compiled_aegls_update_27jul2018.pdf"
DEFAULT_PDF = os.path.join(HERE, "compiled_aegls.pdf")

# 块头：CAS 名称 (单位) [可选第二单位]
BLOCK_RE = re.compile(
    r"(?m)^(\d{2,7}-\d{2}-\d)\s+([^\n]*?)\s+\(([^)]+)\)(?:\[([^\]]+)\])?\s*\n"
    r"(?:\d+\s+min|\d+\s+hr)[^\n]*\n"          # 表头 10 min 30 min ...
    r"((?:\s*AEGL\s*[123][^\n]*\n){2,4})"      # AEGL 1/2/3 行（可能双单位 6 行）
)
VAL_RE = re.compile(r"AEGL\s*([123])\s+(.+)")
# 值 token：NR / 千位逗号数字（2,700）/ 小数 / 科学计数 / 数字+单位（50 mg/m3）
_VTOKEN = r"(?:NR|[\d,]+(?:\.\d+)?(?:E[-+]?\d+)?(?:\s*[A-Za-z/]+)?)"
# 行内 5 个值（10/30/60min/4h/8h），NR → None；注意每个 token 必须是捕获组
ROW_RE = re.compile(r"\s*".join(["(" + _VTOKEN + ")"] * 5) + r"\s*$")


def norm(v):
    """'NR' → None；数值原样返回字符串（去掉千位逗号，保留单位如 '50 mg/m3'）。"""
    if not v or v.strip().upper() == "NR":
        return None
    return v.strip().replace(",", "")


def parse_pdf(pdf_path):
    import pdfplumber
    recs = {}
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join((p.extract_text() or "") for p in pdf.pages)
    # 去掉每页页眉/页脚噪声
    text = re.sub(r"^July 27, 2018.*?$\n?", "", text, flags=re.M)
    text = re.sub(r"^Page \d+ of \d+.*?$\n?", "", text, flags=re.M)
    text = re.sub(r"^Final AEGLs \(\d+\)\s*$\n?", "", text, flags=re.M)
    text = re.sub(r"^TABLE OF CONTENTS\s*$\n?", "", text, flags=re.M)
    text = re.sub(r"^NR = Not recommended due to insufficient data\s*$\n?", "", text, flags=re.M)

    for m in BLOCK_RE.finditer(text):
        cas, name, unit, unit2, body = m.groups()
        name = re.sub(r"\s+", " ", name).strip()
        rows = {}
        dup_note = ""
        for rm in VAL_RE.finditer(body):
            lvl = rm.group(1)
            vals = rm.group(2).strip()
            fm = ROW_RE.match(vals)
            if fm:
                v = [norm(x) for x in fm.groups()]
                if lvl in rows:
                    dup_note = f"多单位组，取第一组（{unit}）；另有 {unit2 or '第二单位'}"
                    continue
                rows[lvl] = v  # [10,30,60,4h,8h]
        if not rows:
            continue
        a = {lvl: rows[lvl] for lvl in ("1", "2", "3") if lvl in rows}
        recs[cas] = {
            "name": name,
            "unit": unit.strip(),
            "aegl1_10": a.get("1", [None]*5)[0],
            "aegl1_60": a.get("1", [None]*5)[2],
            "aegl2_10": a.get("2", [None]*5)[0],
            "aegl2_60": a.get("2", [None]*5)[2],
            "aegl3_10": a.get("3", [None]*5)[0],
            "aegl3_60": a.get("3", [None]*5)[2],
            "aegl1_30": a.get("1", [None]*5)[1],
            "aegl1_4h": a.get("1", [None]*5)[3],
            "aegl1_8h": a.get("1", [None]*5)[4],
            "aegl2_30": a.get("2", [None]*5)[1],
            "aegl2_4h": a.get("2", [None]*5)[3],
            "aegl2_8h": a.get("2", [None]*5)[4],
            "aegl3_30": a.get("3", [None]*5)[1],
            "aegl3_4h": a.get("3", [None]*5)[3],
            "aegl3_8h": a.get("3", [None]*5)[4],
            "note": dup_note,
        }
    return recs


def main():
    ap = argparse.ArgumentParser(description="构建 EPA AEGL 本地索引")
    ap.add_argument("--pdf", default=DEFAULT_PDF, help="本地 PDF 路径（默认先尝试下载到脚本目录）")
    ap.add_argument("--query", help="只查询某个 CAS 并打印")
    ap.add_argument("--out", default=os.path.join(DATA_DIR, "AEGL索引.json"))
    args = ap.parse_args()

    if not os.path.exists(args.pdf):
        print(f"[aegl] 下载 PDF → {args.pdf}")
        req = urllib.request.Request(PDF_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=120) as r, open(args.pdf, "wb") as f:
            f.write(r.read())
    else:
        print(f"[aegl] 使用本地 PDF: {args.pdf}")

    recs = parse_pdf(args.pdf)
    print(f"[aegl] 解析到 {len(recs)} 个化学品")

    if args.query:
        q = args.query.strip()
        hit = recs.get(q)
        if not hit:  # 尝试按名称模糊匹配
            for cas, r in recs.items():
                if q.lower() in r["name"].lower():
                    hit = r
                    q = cas
                    break
        if hit:
            print(f"  {q} {hit['name']} ({hit['unit']})")
            for k in ("aegl1_10", "aegl1_60", "aegl2_10", "aegl2_60", "aegl3_10", "aegl3_60"):
                print(f"    {k}: {hit[k]}")
        else:
            print(f"  CAS {q} 未收录")
        return

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(recs, f, ensure_ascii=False, indent=1)
    print(f"[aegl] 已保存 {args.out}")
    # 统计
    n1 = sum(1 for r in recs.values() if r["aegl1_10"])
    n2 = sum(1 for r in recs.values() if r["aegl2_10"])
    n3 = sum(1 for r in recs.values() if r["aegl3_10"])
    print(f"[aegl] AEGL-1/2/3 有值: {n1}/{n2}/{n3}")


if __name__ == "__main__":
    main()
