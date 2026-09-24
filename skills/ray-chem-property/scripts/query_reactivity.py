# -*- coding: utf-8 -*-
"""
ray-chem-property 反应性字段本地秒查（B3 · 独立于 ray-chem-compat，不产生跨 skill 依赖）：
   query_reactivity.py --cas 10217-52-4 ｜ --name hydrazine ｜ --max 6
   读取本 skill data/ 的两件新索引：
     禁配物-危险品全书.json（CAS → 危险反应/避免接触/禁配物/分解产物/pages）
     材质反应性-CAMEO.json （CAS → water/common_materials/polymerize/inhibitor/CG组）
   ⚠️ 判定与矩阵归 ray-chem-compat；本脚本只服务「物性表反应性字段补全」。
"""
import sys, io, os, json, re, argparse, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
D = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def load(fn):
    return json.load(open(os.path.join(D, fn), encoding="utf-8"))


ap = argparse.ArgumentParser()
ap.add_argument("--cas")
ap.add_argument("--name")
ap.add_argument("--max", type=int, default=6)
a = ap.parse_args()
if not (a.cas or a.name):
    ap.error("至少给 --cas / --name 之一")
whp = load("禁配物-危险品全书.json")
cml = load("材质反应性-CAMEO.json")

kw_cas = (a.cas or "").strip()
kw_name = (a.name or "").strip().lower()

results = collections.defaultdict(list)

def _texts(rec):
    """聚合一条记录可做包含匹配的文本"""
    return " ¦ ".join(str(v) for v in rec.get("react", {}).values() if v) \
        + " " + str(rec.get("name") or "")

# ① 危险品全书（CAS 精确 > 名称包含）
for cas, r in whp.items():
    hit = 0
    if kw_cas and cas == kw_cas:
        hit = 3
    elif kw_name and (kw_name in str(r.get("name") or "").lower()):
        hit = 1
    if hit:
        results["危险品全书·禁配物"].append({**r, "cas": cas, "score": hit})
for v in results["危险品全书·禁配物"]:
    v.pop("score", None)

# ② CAMEO
for cas, r in cml.items():
    if cas == "_names":
        continue
    hit = 0
    if kw_cas and cas == kw_cas:
        hit = 3
    elif kw_name and kw_name in str(r.get("name") or "").lower():
        hit = 1
    if hit:
        results["CAMEO·材质反应性"].append({**r, "cas": cas, "score": hit})
if kw_name and "_names" in cml:                      # 无 CAS 的数据表按名补
    for rec in cml["_names"]:
        if kw_name in str(rec.get("name") or "").lower():
            results["CAMEO·无CAS(按名)"].append(rec)
for v in results["CAMEO·材质反应性"]:
    v.pop("score", None)

out = {k: v[: a.max] for k, v in results.items() if v}
print(json.dumps({"query": {"cas": a.cas, "name": a.name},
                  "n": {k: len(v) for k, v in out.items()},
                  "results": out}, ensure_ascii=False, indent=1))
