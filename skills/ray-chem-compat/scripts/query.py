# -*- coding: utf-8 -*-
"""
ray-chem-compat 统一查询入口（L1 判定层常驻；L2 证据层按需查）：
   query.py --cas 10217-52-4 ｜ --name 水合肼 ｜ --title Hydrazine ｜ --pair "水合肼,二氧化碳"
     [--source cameo|whpdj|breth|rules]  [--max 6]
   冲突不静默合流：并列输出，标注来源，人工裁决。
"""
import sys, io, os, json, re, argparse, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SK = r"C:\Users\rayzh\.workbuddy\skills\ray-chem-compat"
D = os.path.join(SK, "data")


def load(fn):
    return json.load(open(os.path.join(D, fn), encoding="utf-8"))


def fp(kw):
    """多关键词归一 → 小写去空格"""
    return re.sub(r"\s+", "", str(kw or "")).lower()


def cameo_match(kw, mx):
    kw, out = str(kw).strip().lower(), []
    for code, r in came.items():
        if str(r.get("cas") or "").lower() == kw or kw in str(r.get("name") or "").lower():
            out.append({"code": code, "name": r.get("name"), "cas": r.get("cas"),
                        "reactive_group": r.get("reactive_group"), "react": r["react"]})
            if len(out) >= mx:
                break
    return out


def whpdj_match(kw, mx):
    kw = str(kw).strip()
    out = []
    for name, r in whpdj.items():
        if r.get("cas") == kw or (kw and (kw in name or name in kw)):
            out.append({**r, "name": name})
            if len(out) >= mx:
                break
    return out


def breth_match(kw, mx):
    kw, out = str(kw).strip().lower(), []
    for no, r in breth.items():
        t = (r.get("title") or "").lower()
        score = 0
        if str(r.get("cas") or "").lower() == kw:
            score = 3
        elif kw and t == kw:
            score = 3
        elif kw and kw in t:
            score = 1
        if score:
            out.append({"no": no, "title": r.get("title"), "page": r.get("page"),
                        "cas": r.get("cas"), "refs": r.get("refs", [])[:6],
                        "related": r.get("related", [])[:6], "dag": r.get("dag"),
                        "score": score})
    out.sort(key=lambda x: (-x["score"], (x.get("title") or "").lower()))
    return out[:mx]


def breth_pages(kw, mx):
    """Bretherick 页缓存兜底：原书回源"""
    hits, cnt = [], 0
    for k, v in sorted(pcache.items(), key=lambda x: int(x[0])):
        if str(kw).lower() in v.lower():
            for m in re.finditer(re.escape(str(kw)), v, re.I):
                seg = v[max(0, m.start() - 180): m.start() + 420].replace("\n", " ¦ ")
                hits.append({"page": k, "ctx": re.sub(r"\s+", " ", seg)[:480]})
                cnt += 1
                if cnt >= mx:
                    return hits
    return hits


ap = argparse.ArgumentParser()
ap.add_argument("--cas")
ap.add_argument("--name")
ap.add_argument("--pair")
ap.add_argument("--source", default="all", choices=["cameo", "whpdj", "breth", "all"])
ap.add_argument("--max", type=int, default=6)
a = ap.parse_args()
if not (a.cas or a.name or a.pair):
    ap.error("至少给 --cas / --name / --pair 之一")

came = load("cameo_reactivity.json")
whpdj = load("whpdj_incompat.json")
breth = load("breth_entries.json")
pcache = load("cache_breth8_pages.json")

keys = []
if a.cas:
    keys.append(a.cas)
if a.name:
    keys.append(a.name)
if a.pair:
    keys += [x.strip() for x in re.split(r"[,，；;]", a.pair) if x.strip()]

results = collections.defaultdict(list)
for kw in keys:
    if a.source in ("cameo", "all"):
        results["CAMEO"].extend(cameo_match(kw, a.max))
    if a.source in ("whpdj", "all"):
        results["危险品全书"].extend(whpdj_match(kw, a.max))
    if a.source in ("breth", "all"):
        results["Bretherick"].extend(breth_match(kw, a.max))
    if a.source in ("breth", "all") and not results["Bretherick"]:
        results["Bretherick页缓存"].extend(breth_pages(kw, 3))

out = {k: v for k, v in results.items() if v}
print(json.dumps({"query": {k: a.__dict__[k] for k in ("cas", "name", "pair", "source")},
                  "n": {k: len(v) for k, v in out.items()},
                  "results": out}, ensure_ascii=False, indent=1))
