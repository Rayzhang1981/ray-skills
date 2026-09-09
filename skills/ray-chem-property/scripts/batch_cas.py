# -*- coding: utf-8 -*-
"""批量查 CAS：英文名 -> PubChem CID -> synonyms -> CAS。断点续传 + 限速。"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "en_names.jsonl")
OUT = os.path.join(HERE, "cas_results.jsonl")

def get_json(url, retry=4):
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 chem-collector/1.0"})
            r = urllib.request.urlopen(req, timeout=25)
            return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            if e.code == 429:
                time.sleep(2.5 * (i + 1))
                continue
            time.sleep(1.5 * (i + 1))
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None

def name_to_cid(name):
    q = urllib.parse.quote(name)
    d = get_json(f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{q}/cids/JSON")
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

def main():
    # 读取已有进度（断点续传）
    done = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        o = json.loads(line)
                        done[o["abbr"]] = o
                    except Exception:
                        pass
    print(f"[cas] 已有进度 {len(done)} 条", flush=True)

    rows = []
    with open(SRC, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))

    with open(OUT, "a", encoding="utf-8") as out:
        n_ok = 0
        n_fail = 0
        for idx, row in enumerate(rows):
            abbr = row["abbr"]
            if abbr in done:
                continue
            en = row["en"]
            cid = name_to_cid(en)
            cas = ""
            if cid:
                cas = cid_to_cas(cid)
            rec = {"abbr": abbr, "en": en, "cid": cid, "cas": cas}
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")
            out.flush()
            if cas:
                n_ok += 1
            else:
                n_fail += 1
            if (idx + 1) % 25 == 0:
                print(f"[cas] 进度 {idx+1}/{len(rows)}，CAS 成功 {n_ok}，失败 {n_fail}", flush=True)
            time.sleep(0.3)  # 限速 ~3 rps
    print(f"[cas] DONE: 成功 {n_ok}，失败 {n_fail}，总 {len(rows)}", flush=True)

if __name__ == "__main__":
    main()
