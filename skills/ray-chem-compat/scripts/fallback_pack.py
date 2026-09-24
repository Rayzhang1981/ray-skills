# -*- coding: utf-8 -*-
"""
ray-chem-compat 技术兜底层（v1.4.0）——检索规格包生成器（按 T1–T8 决策表）
  触发口径（照实施计划 §7.1）：
    **以化学品为中心**，不逐对搜——一次 SDS 检索覆盖该物质对"整类"物质的禁忌。
    T1 某化学品无基团指派 → 化学品级 pack 条目
    T2 某化学品对在 L1 判 `?` → pair 级 pack 条目（带上/code 上下文）
    T3/T4/T5/T6/T7 由用户 --pairs / --note 显式声明才生成（引擎不知现场与专有权属）
    T8 库判有据且场景匹配 → 不搜（成本闸门）
  分工固化：本脚本只产「检索规格包」，若化学品无 CAS 缺口会标注"T7"，检索词自动降级到中文名；
    真正执行 = agent 层调 ray-synth-search（六步法/一致性/深链/GAPS），hit 后回填 fallback_cache.jsonl。
  阈值闸门：
    score≥80 且 ≥2 独立源（含 ≥1 权威）→ 建议码 + * （唯一可改码）｜60–79 → ?｜矛盾 → ⚠｜搜不到 → ?（严禁无据填 Y 或自动"相容"）
"""
import sys, io, os, re, json, argparse, datetime, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
SK = r"C:\Users\rayzh\.workbuddy\skills\ray-chem-compat"
D = os.path.join(SK, "data")
sys.path.insert(0, os.path.join(SK, "scripts"))
import compat_engine as CE


def load(fp):
    return json.load(open(fp, encoding="utf-8"))


def items_from_args(a):
    if not a.fin:
        idx = load(os.path.join(D, "chem_index.json"))
        out = []
        for it in idx["chemicals"]:
            if it["cn"] in ("碳钢", "不锈钢304", "不锈钢316L"):
                continue
            cn = "氮气" if it["cn"] == "液氮" else it["cn"]
            out.append({"cn": cn, "cas": it.get("cas") or "", "groups": it.get("groups", [])})
        return out
    raw = load(a.fin)
    if isinstance(raw[0], str):
        base = {}
        for it in load(os.path.join(D, "chem_index.json"))["chemicals"]:
            base.setdefault(it["cn"], it)
        if os.path.exists(os.path.join(D, "chem_index_ext.json")):
            for it in load(os.path.join(D, "chem_index_ext.json")):
                base.setdefault(it.get("cn"), it)
        return [base.get(x) or {"cn": x, "cas": "", "groups": []} for x in raw]
    return raw


def sds_spec(chem, cas, kind, note=""):
    """单个 pack 条目（化学品级 SDS 取证 或 pair 级双向取证）"""
    o = {"kind": kind, "target": chem, "cas": cas, "note": note}
    if kind == "T1_T7":
        o["queries"] = [
            f'"{chem}" SDS "应避免的物质"',
            f'"{chem}" Stability and Reactivity section 10',
            f'"{chem}" incompatible with 扫描 GB 15603 储存禁忌']
        o["why"] = ["T1_T7", note]
        o["question"] = (f"{chem}（含杂质与工艺标定浓度）的 SDS §10「应避免的物质/条件」是什么？"
                         "期望格式：名单式应避免物质 + 触发条件 + 温度边界")
        o["expected_hazards"], o["evidence"] = "全类禁忌列表", "S/A"
        return o
        o["queries"] = [
            f'"{chem}" SDS "应避免的物质"',
            f'"{chem}" Stability and Reactivity section 10',
            f'"{chem}" incompatible with 扫描 GB 15603 储存禁忌']
        o["why"] = ["T1_T7", note]
        o["question"] = (f"{chem}（含杂质与工艺标定浓度）的 SDS §10「应避免的物质/条件」是什么？"
                         "期望格式：名单式应避免物质 + 触发条件 + 温度边界")
        o["expected_hazards"], o["evidence"] = "全类禁忌列表", "S/A"
        return o
    else:  # pair 级
        other = chem  # 此处 chem 实际是 (a,b) 二元组，见调用处
        a, b = other
        pos = [
            f'"{a}" "{b}" 相互作用 OR 起火 OR 爆炸 OR 混合危害',
            f'"{a}" SDS "应避免的物质" 中是否点名 "{b}"',
            f'"{b}" SDS "应避免的物质" 中是否点名 "{a}"',]
        rev = [f'"{a}" "{b}" 兼容 OR 相共存 OR 混合安全（反向查，反确认偏误）']
        o["pos"] = pos
        o["rev"] = rev
        o["question"] = f"{a} 与 {b} 混合（常温常压、并考虑更高工况）是否能共存？"
        o["evidence_required"] = ["SDS §10", "Bretherick", "CSB/事故", "GB 15603"]
        o["min_gate"] = 80
        o["note"] = note or "T2/T3/T4/T5/T6 之一"
    return o


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="fin")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--tag", default=None)
    ap.add_argument("--pairs", help='"A,B;C,D"（T5/T3/T4/T6 人工指定）')
    ap.add_argument("--note", help="T5/T3 等的人工备注（写入 pack，便于审计）")
    args = ap.parse_args()
    items = items_from_args(args)
    N = len(items)
    kb = CE.default_kb()
    codes, _ = CE.build_matrix(kb, items)
    OUT = args.out_dir or os.getcwd()
    tag = args.tag or f"{N}化学品"

    chem_items, pair_items = [], []
    # T1/T7：化学品级（缺 groups 或缺 cas 的成员）
    for it in items:
        if not it.get("groups") or not str(it.get("cas") or ""):
            chem_items.append({"cn": it["cn"], "cas": it.get("cas") or "",
                               "why": ("T1" if not it.get("groups") else "") +
                                      ("T7" if not str(it.get("cas") or "") else "")})
    # T2：pair 判 "?"
    for i in range(N):
        for j in range(i + 1):
            if codes[(i, j)] == "?":
                pair_items.append({"a": items[j]["cn"], "b": items[i]["cn"],
                                   "why": ["T2"]})
    # T5：用户指定对
    if args.pairs:
        for s in re.split(r"\s*[;；]\s*", args.pairs):
            seg = [x.strip() for x in re.split(r"[,，]", s) if x.strip()]
            okp = [x for x in seg if any(it["cn"] == x for it in items)]
            if len(okp) == 2:
                pair_items.append({"a": okp[0], "b": okp[1],
                                   "why": ["T5"], "note": args.note or ""})
    pack = {
        "meta": {"generated": datetime.datetime.now().isoformat(timespec="seconds"),
                 "tag": tag,
                 "engine": "ray-chem-compat L1 × 2346 基团对规则",
                 "sources_rank": {"S": "供应商 SDS §10（应避免的物质／条件）",
                                   "A": "Bretherick/NFPA 491M/Sax ＋ 事故调查 ＋ GB 15603",
                                   "B": "厂商技术资料/材质相容表（仅线索）",
                                   "C": "网页百科论坛（仅线索）"}},
        "chem_level": [sds_spec(kind="T1_T7", chem=c["cn"], cas=c["cas"],
                                note=";".join(c.get("why", ["缺 groups 或缺 cas"])))
                       for c in chem_items],
        "pair_level": [sds_spec_pair(p, args.note or "") for p in pair_items],
        "acceptance": {"score≥80 & ≥2 独立源+1 权威": "建议码 + * + 来源批注"
                        "（唯一可改）",
                       "60-79 / 单源": "?（只存档）",
                       "20-39": "⚠ 冲突（两说并列 人工仲裁）",
                       "低于 20 / 未覆盖": "?（严禁未证写 Y）"},
        "cache": "${OUT}/fallback_cache.jsonl",
    }
    fn_pack = os.path.join(OUT, f"fallback_pack-{tag}.json")
    json.dump(pack, open(fn_pack, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    fn_cache = os.path.join(OUT, f"fallback_cache-{tag}.jsonl")
    if not os.path.exists(fn_cache):
        card = {"key": "物质对|温度|条件", "answer": "不相容/相容/证据不足",
                "score": 0, "evidence": [{"rank": "S/A/B/C", "url": "", "quote": ""}],
                "gaps": [], "decision": "?|⚠|*", "operator": ""}
        open(fn_cache, "w", encoding="utf-8").write(json.dumps(card,
                                                               ensure_ascii=False) + "\n")
    print(json.dumps({"pack": fn_pack, "cache": fn_cache,
                      "chem_level": len(pack["chem_level"]),
                      "pair_level": len(pack["pair_level"]),
                      "T2_pairs": sum(1 for p in pair_items if "T2" in p["why"])},
                     ensure_ascii=False, indent=1))


def sds_spec_pair(p, note):
    return {"kind": "PAIR", "pair": [p["a"], p["b"]], "why": p["why"],
            "note": note,
            "pos_queries": [
            f'"{p["a"]}" SDS "应避免的物质" OR avoid contact with "{p["b"]}"',
            f'"{p["b"]}" SDS "应避免的物质" OR avoid contact with "{p["a"]}"',
            f'{p["a"]} {p["b"]} 混合 爆炸 OR 起火 OR 剧烈反应',
            f'"{p["a"]}" "{p["b"]}" GB 15603 储存隔离表'],
            "rev_queries": [f'"{p["a"]}" "{p["b"]}" 兼容 OR 相容 OR 可共存'],
            "evidence_required": ["S：SDS §10", "A：Bretherick/事故/法规",
                                   "B：厂商资料（线索）"],
            "gate": {"≥80 & ≥2 独立源 + 1 权威": "改码 + * + 来源批注",
                     "60-79/单源": "?（存档）", "20-39": "⚠ 冲突", "<20": "?（不许 Y）"}}


if __name__ == "__main__":
    main()
