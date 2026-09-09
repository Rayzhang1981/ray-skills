# -*- coding: utf-8 -*-
"""CAS 失败补充：用简化/修正后的英文名重试失败的条目。
规则：去括号内容、去 SOLUTION/MIXTURE 等后缀、OCR 修正（CHOR->CHLOR 等）。
"""
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CAS_FILE = os.path.join(HERE, "cas_results.jsonl")

def get_json(url, retry=3):
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 chem-fix/1.0"})
            r = urllib.request.urlopen(req, timeout=25)
            return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(1.2 * (i + 1))
        except Exception:
            time.sleep(1.2 * (i + 1))
    return None

def name_to_cid(name):
    d = get_json(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{urllib.parse.quote(name)}/cids/JSON")
    if d:
        cids = d.get("IdentifierList", {}).get("CID", [])
        return cids[0] if cids else None
    return None

def cid_to_cas(cid):
    d = get_json(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/{cid}/synonyms/JSON")
    if d:
        syns = d.get("InformationList", {}).get("Information", [{}])[0].get("Synonym", [])
        for s in syns:
            if re.match(r"^\s*\d{2,7}-\d{2}-\d\s*$", s):
                return s.strip()
    return ""

def simplify(en):
    s = en.upper()
    # OCR 修正
    s = s.replace("CHORO", "CHLORO").replace("CHOR", "CHLOR")
    s = s.replace("DICHR", "DICHL").replace("BICR", "BICHRO")
    s = s.replace("DICHOR", "DICHLOR").replace("TRICHOR", "TRICHLOR")
    s = s.replace("HPOCHLORITE", "HYPOCHLORITE").replace("HPOCHL", "HYPOCHL")
    # 去括号内容
    s = re.sub(r"\([^)]*\)", "", s)
    # 去常见后缀/修饰
    for suf in [" SOLUTION", " (ALL ISOMERS)", " MIXTURE", " (ALL)", "SOLN"]:
        s = s.replace(suf, "")
    # 去掉末尾残留
    s = re.sub(r"\s+", " ", s).strip()
    # 截断过长的（OCR 噪声）
    if len(s) > 60:
        s = s[:60]
    return s

def main():
    # 读取现有结果
    rows = {}
    with open(CAS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    o = json.loads(line)
                    rows[o["abbr"]] = o
                except Exception:
                    pass

    fails = [o for o in rows.values() if not o.get("cas")]
    print(f"[fix] 待补充 {len(fails)} 条", flush=True)

    n_ok = 0
    for o in fails:
        try:
            en = simplify(o["en"])
            if not en or en == o["en"].upper():
                continue  # 简化无变化则跳过
            cid = name_to_cid(en)
            cas = cid_to_cas(cid) if cid else ""
            if cas:
                o["cid"] = cid
                o["cas"] = cas
                o["fixed"] = f"simplified:{en}"
                n_ok += 1
                print(f"[fix] {o['abbr']} {o['en'][:30]} -> {cas} (via {en[:30]})", flush=True)
            time.sleep(0.3)
        except Exception as e:
            print(f"[fix] {o['abbr']} error: {e}", flush=True)

    # 重写文件
    with open(CAS_FILE, "w", encoding="utf-8") as f:
        for abbr in sorted(rows.keys()):
            f.write(json.dumps(rows[abbr], ensure_ascii=False) + "\n")
    print(f"[fix] DONE: 补充成功 {n_ok} 条", flush=True)

if __name__ == "__main__":
    main()
