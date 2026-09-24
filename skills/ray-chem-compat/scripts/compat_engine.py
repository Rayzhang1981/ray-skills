# -*- coding: utf-8 -*-
"""
compat_engine —— 化学品相容性判定引擎内核

输入：各化学品的反应性基团集（Ga）
知识库：group_pair_rules.json（68 基团 / 2346 对）
输出：字母码矩阵 + 逐格判定明细（触发基团对 / 判定代码 / 潜在气体 / 依据文本）

严格对齐 CRW 官方语义：
  · 只做 pairwise；同一化学品的多个基团之间**互不配算**
  · 化学品对结论 = 其基团对结论取最严重者（N > C > Y）
  · 对角格：含自反应基团 → SR；否则 X
  · 自反应基团集**从知识库推导**（对角码为 SR 的基团），不硬编码
"""
import os, json, functools

B = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
B = os.path.normpath(B)
# v1.2.0 修复（2026-09-24 回流）：默认 KB 路径原为 ../build（该目录不存在，default_kb() 必报
# FileNotFoundError）。三库数据实际归档在 ../data/（build_*.py 生成后人工归档），故默认改指 data/。

SEVERITY = {"N": 3, "?": 2, "C": 1, "Y": 0, "SR": -1, "X": -1}

# 两个**不同**化学品恰好共享同一基团时，(g,g) 自对格该给什么结论。
# 自对格的 symbol 是 X/SR（"无自反应"的自对标记），**不是相容性结论**，故须另行规范化。
# 规则来自实测证据，非推测：
#   codes == {NR}  → Y   （证据：母版 27 格）
#   codes == {UR}  → C   （证据：母版 2 格：Peroxides²、Acids Strong Oxidizing²）
#   其余组合       → '?' （无证据，显式标未判定，不猜）
SELF_PAIR_RULE = {("NR",): "Y", ("UR",): "C"}


def load_kb(path=None, path_groups=None):
    kb = json.load(open(path or os.path.join(B, "group_pair_rules.json"), encoding="utf-8"))
    rules = {}
    for r in kb["rules"]:
        rules[(r["group_a"], r["group_b"])] = r
        rules[(r["group_b"], r["group_a"])] = r
    sr_groups = {r["group_a"] for r in kb["rules"] if r["self_pair"] and r["symbol"] == "SR"}
    # 每个基团的「跨化学品自对」规范结论
    self_pair_verdict = {}
    for r in kb["rules"]:
        if r["self_pair"]:
            cs = tuple(sorted(set(r["codes"])))
            self_pair_verdict[r["group_a"]] = SELF_PAIR_RULE.get(cs, "?")
    return {"kb": kb, "rules": rules, "sr_groups": sr_groups,
            "groups": set(kb["groups"]), "self_pair_verdict": self_pair_verdict}


@functools.lru_cache(maxsize=1)
def default_kb():
    return load_kb()


def predict_cell(kb, Ga, Gb, same_chem=False):
    """返回 (symbol, detail)。Ga/Gb 为基团名集合。"""
    if same_chem:
        sym = "SR" if (set(Ga) & kb["sr_groups"]) else "X"
        detail = {"reason": "self", "sr_groups": sorted(set(Ga) & kb["sr_groups"])}
        return sym, detail

    hits, unknown = [], []
    for ga in Ga:
        for gb in Gb:
            r = kb["rules"].get((ga, gb))
            if r is None:
                unknown.append((ga, gb))
                continue
            if ga == gb:
                # 两个不同化学品共享同一基团 → 用规范化的自对结论，不取自对格的 X/SR
                sym = kb["self_pair_verdict"].get(ga, "?")
                hits.append({"group_a": ga, "group_b": gb, "symbol": sym,
                             "codes": r["codes"], "potential_gases": r["potential_gases"],
                             "documentation": r["documentation"]})
                continue
            hits.append(r)
    if not hits:
        return "?", {"reason": "no_rule", "unresolved_group_pairs": unknown}

    worst = max(hits, key=lambda r: SEVERITY.get(r["symbol"], 0))
    sym = worst["symbol"]
    codes, gases, trig = set(), set(), []
    for r in hits:
        if r["symbol"] == sym:
            codes |= set(r["codes"])
            gases |= set(r["potential_gases"])
            trig.append({"groups": [r["group_a"], r["group_b"]],
                         "codes": r["codes"], "docs": r["documentation"][:900]})
    return sym, {"reason": "group_pairs", "n_group_pairs": len(hits),
                 "codes": sorted(codes), "potential_gases": sorted(gases),
                 "triggers": trig[:4], "unresolved_group_pairs": unknown}


def _nm(x):
    """兼容索引里的 cn / name 两种键名"""
    return x.get("name") or x.get("cn") or "?"


def build_matrix(kb, items):
    """
    items: [{"name"/"cn":..., "groups":[..] or None}, ...]（顺序即矩阵顺序）
    返回 N×N 下三角字母码 + 明细。groups 为 None 者 → '?'（未判定）
    """
    n = len(items)
    codes = {}
    details = {}
    for i in range(n):
        for j in range(i + 1):
            A, B = items[i], items[j]
            if not A["groups"] or not B["groups"]:
                codes[(i, j)] = "?"
                details[(i, j)] = {"reason": "no_groups",
                                   "missing": [_nm(A) if not A["groups"] else None,
                                               _nm(B) if not B["groups"] else None]}
                continue
            sym, det = predict_cell(kb, A["groups"], B["groups"], same_chem=(i == j))
            codes[(i, j)] = sym
            details[(i, j)] = det
    return codes, details


def coverage_report(kb, items):
    known = [_nm(x) for x in items if x["groups"]]
    unknown = [_nm(x) for x in items if not x["groups"]]
    used = set()
    for x in items:
        used |= set(x["groups"] or [])
    return {"known": known, "unknown": unknown,
            "groups_used": sorted(used),
            "groups_in_kb": len(kb["groups"]),
            "groups_missing_from_kb": sorted(set(used) - kb["groups"])}
