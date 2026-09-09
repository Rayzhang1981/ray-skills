# -*- coding: utf-8 -*-
"""anchor_db.py — ray-pse-sharing 历史事故锚点数据库管理 CLI（v2.0.0）

设计原则（2026-08-29 用户确认）：
    1. 首要任务是「扩库」——覆盖各类工艺安全事故类型，量足够大才能"快速定位直接应用"。
    2. 锚点典型性三条款：
         a. 影响大、较为知名（重大伤亡/重大社会影响优先）
         b. 与事故类型适配
         c. 新事故优于旧事故（特别出名的经典事故除外）
    3. 「毕业机制」= 典型性复审，不是使用次数上限：
         - 重要事故允许反复使用（事故分享就是要反复揣摩学习）
         - 不满足典型性的锚点（影响小/类型错配/陈旧且非经典）→ retired 淘汰
       used_count 仅作信息记录 + 批内防扎堆软提示，不构成硬约束。

锚点分级 tier：
    S — 经典知名事故（不限使用次数，跨类型优先选用）
    A — 典型行业事故（本类型首选池）
    B — 补充案例（同类不足时选用；复审不达标淘汰）

状态 lifecycle：pending(未核实) → active(可用) → retired(典型性复审不通过,毕业淘汰)

子命令：
    list      [--type <类型>] [--tier <S|A|B>] [--status <pending|active|retired>] [--all]
    search    <关键词>
    pick      <类型> [--from N --to M] [--top K]   # 推荐锚点：类型适配(b) → S级优先(a)
                                                   #   → 年份新优先(c) → 本批已用少优先(防扎堆)
    scan-cards <卡片目录> [--from N --to M]        # 全量对账：更新 used_count/used_by；
                                                   #   违规仅两种：pending/retired 被引用；
                                                   #   同批同锚点≥3次 → 软提示（建议替换但不强制）
    review    <id> --retire|--restore --reason ...  # 典型性复审（毕业机制人工执行）
    verify    <id> [--date --casualty --cause --source --tier]   # 核实后转 active
    add       --file <anchor.json>
    stats
"""
import argparse
import io
import json
import os
import re
import sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(SKILL_DIR, "assets", "anchor_db.json")

TIER_ORDER = {"S": 0, "A": 1, "B": 2}


def load_db():
    with open(DB_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_db(db):
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"[saved] {DB_PATH}")


def norm_label(text):
    m = re.match(r"(\d{4})年([^：:]+)[：:]?", text)
    if m:
        return f"{m.group(1)}年{m.group(2).strip()}"
    return text[:30]


def match_anchor(anchor, history_line):
    key = norm_label(history_line)
    for alias in anchor.get("aliases", []):
        if key == alias or key.startswith(alias) or alias in key or key in alias:
            return True
    ev_core = re.sub(r"[（(].*?[)）]", "", anchor["event"])
    return bool(ev_core) and ev_core in history_line


def scan_history_lines(cards_dir, lo, hi):
    for n in range(lo, hi + 1):
        p = os.path.join(cards_dir, f"card_{n:03d}.json")
        if not os.path.exists(p):
            continue
        try:
            d = json.load(open(p, encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            print(f"[warn] card_{n:03d}.json 读取失败: {e}")
            continue
        for h in d.get("history", []):
            yield n, h


def cmd_scan_cards(args):
    db = load_db()
    anchors = db["anchors"]
    usage = defaultdict(list)
    unknown = defaultdict(list)

    for n, h in scan_history_lines(args.dir, args.frm, args.to):
        hit = None
        for a in anchors:
            if match_anchor(a, h):
                hit = a
                break
        if hit:
            usage[hit["id"]].append(n)
        else:
            unknown[norm_label(h)].append(n)

    for a in anchors:
        a["used_by"] = sorted(usage.get(a["id"], []))
        a["used_count"] = len(a["used_by"])

    # 违规：pending/retired 被引用（未核实/已淘汰不得入卡）
    violations = []
    for a in anchors:
        if a["used_by"] and a["status"] == "pending":
            violations.append((a, "pending（未核实）锚点被引用"))
        if a["used_by"] and a["status"] == "retired":
            violations.append((a, f"retired（已毕业淘汰：{a.get('retire_reason','')}）锚点仍被引用"))

    # 批内防扎堆软提示（仅信息，不报错）
    batch_hot = [(a, a["used_by"]) for a in anchors
                 if len([c for c in a["used_by"] if args.frm <= c <= args.to]) >= 3]

    save_db(db)

    print(f"\n=== 扫描范围: card_{args.frm:03d} ~ card_{args.to:03d} ===")
    print(f"命中锚点: {len(usage)} 个 | 库外标签: {len(unknown)} 个")
    if unknown:
        print("\n--- 库外标签（不在库中，建议 add 入库）---")
        for k, cards in sorted(unknown.items()):
            print(f"  {k}  cards={cards}")
    if batch_hot:
        print("\n--- 批内高频软提示（可反复用，但相邻卡建议换脸）---")
        for a, cards in batch_hot:
            inbatch = [c for c in cards if args.frm <= c <= args.to]
            print(f"  [{a['tier']}] {a['event']} 本批 {len(inbatch)} 次 cards={inbatch}")
    if violations:
        print(f"\n!!! 违规 {len(violations)} 项:")
        for a, why in violations:
            print(f"  [{a['id']}] {a['event']}: {why}  cards={a['used_by']}")
        sys.exit(1)
    print("\n✅ 对账通过：全部 history 引用合规（active）")


def cmd_pick(args):
    db = load_db()
    batch_used = defaultdict(int)
    if args.dir:
        for n, h in scan_history_lines(args.dir, args.frm, args.to):
            for a in db["anchors"]:
                if match_anchor(a, h):
                    batch_used[a["id"]] += 1
    pool = [a for a in db["anchors"]
            if a["status"] == "active"
            and (a["type"] == args.type or args.type in a["type"])]
    pool.sort(key=lambda a: (TIER_ORDER.get(a.get("tier", "B"), 2),
                             -a.get("year", 0),          # c. 新者优先
                             batch_used.get(a["id"], 0),  # 防扎堆
                             a["used_count"]))
    print(f"=== 类型「{args.type}」推荐锚点（共 {len(pool)} 条可用；S级优先→年份新→批内少用）===")
    for a in pool[: args.top]:
        flag = f" ⚠️本批已用{batch_used[a['id']]}次" if batch_used.get(a["id"]) else ""
        print(f"  [{a['tier']}] {a.get('year','?')}年 余量记录{a['used_count']} | {a['label_30']}{flag}")
    if not pool:
        print("  ⚠️ 该类型无 active 锚点——WebSearch 核实新事故后 add + verify 入库")


def cmd_verify(args):
    db = load_db()
    for a in db["anchors"]:
        if a["id"] == args.id:
            a["verified"] = True
            a["status"] = "active"
            for field, val in [("casualty", args.casualty), ("cause", args.cause),
                               ("source", args.source), ("tier", args.tier)]:
                if val:
                    a[field] = val
            save_db(db)
            print(f"[verified] {a['id']} {a['event']} → active (tier={a.get('tier')})")
            return
    print(f"[error] 未找到 {args.id}")
    sys.exit(1)


def cmd_review(args):
    """典型性复审 = 毕业机制：不满足 a/b/c 三条款 → retired。"""
    db = load_db()
    for a in db["anchors"]:
        if a["id"] == args.id:
            if args.retire:
                a["status"] = "retired"
                a["retire_reason"] = args.reason or "典型性复审不通过（a影响/b适配/c时效）"
                print(f"[retired] {a['id']} {a['event']} | {a['retire_reason']}")
            else:
                a["status"] = "active"
                a.pop("retire_reason", None)
                print(f"[restored] {a['id']} {a['event']} → active")
            save_db(db)
            return
    print(f"[error] 未找到 {args.id}")
    sys.exit(1)


def cmd_stats(args):
    db = load_db()
    by_status = defaultdict(int)
    by_tier = defaultdict(lambda: defaultdict(int))
    by_type = defaultdict(lambda: defaultdict(int))
    for a in db["anchors"]:
        by_status[a["status"]] += 1
        by_tier[a.get("tier", "?")][a["status"]] += 1
        by_type[a["type"]][a["status"]] += 1
    print(f"=== 锚点库统计 ===")
    print(f"总计 {len(db['anchors'])} 条: " + " | ".join(f"{k} {v}" for k, v in sorted(by_status.items())))
    print("\n按分级（tier）:")
    for t in ["S", "A", "B", "?"]:
        if t in by_tier:
            m = by_tier[t]
            print(f"  {t}: 共{sum(m.values())}  active={m.get('active',0)} pending={m.get('pending',0)} retired={m.get('retired',0)}")
    print("\n按类型（type: active/pending/retired）:")
    for t, m in sorted(by_type.items()):
        print(f"  {t}: 共{sum(m.values())}  active={m.get('active',0)} pending={m.get('pending',0)} retired={m.get('retired',0)}")


def cmd_search(args):
    db = load_db()
    kw = args.keywords
    hits = [a for a in db["anchors"]
            if any(kw in s for s in [a["event"], a["label_30"], a.get("cause", ""), *a.get("aliases", []), a["type"]])]
    for a in hits:
        print(f"[{a['id']}] {a.get('tier','?'):1s} {a['status']:7s} 用{a['used_count']} {a['type']} | {a['label_30']}")
    if not hits:
        print("(无命中)")


def main():
    ap = argparse.ArgumentParser(description="锚点数据库 CLI v2.0（典型性毕业机制）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list")
    p.add_argument("--type"); p.add_argument("--tier"); p.add_argument("--status")
    def _list(a):
        for x in load_db()["anchors"]:
            if a.type and a.type not in x["type"]: continue
            if a.tier and x.get("tier") != a.tier: continue
            if a.status and x["status"] != a.status: continue
            print(f"[{x['id']}] {x.get('tier','?'):1s} {x['status']:7s} 用{x['used_count']} {x['type']} | {x['label_30']}")
    p.set_defaults(fn=_list)

    p = sub.add_parser("search"); p.add_argument("keywords"); p.set_defaults(fn=cmd_search)

    p = sub.add_parser("scan-cards")
    p.add_argument("dir"); p.add_argument("--from", dest="frm", type=int, default=1)
    p.add_argument("--to", dest="to", type=int, default=148)
    p.set_defaults(fn=cmd_scan_cards)

    p = sub.add_parser("pick")
    p.add_argument("type")
    p.add_argument("--dir", default=None); p.add_argument("--from", dest="frm", type=int, default=1)
    p.add_argument("--to", dest="to", type=int, default=148); p.add_argument("--top", type=int, default=10)
    p.set_defaults(fn=cmd_pick)

    p = sub.add_parser("verify"); p.add_argument("id")
    p.add_argument("--casualty"); p.add_argument("--cause"); p.add_argument("--source"); p.add_argument("--tier")
    p.set_defaults(fn=cmd_verify)

    p = sub.add_parser("review"); p.add_argument("id")
    p.add_argument("--retire", action="store_true"); p.add_argument("--restore", action="store_true")
    p.add_argument("--reason")
    p.set_defaults(fn=cmd_review)

    p = sub.add_parser("add"); p.add_argument("--file", required=True)
    def _add(a):
        db = load_db()
        new = json.load(open(a.file, encoding="utf-8"))
        items = new if isinstance(new, list) else [new]
        exist = {x["event"] for x in db["anchors"]}
        added = 0
        for it in items:
            if it["event"] in exist:
                print(f"[skip] 已存在: {it['event']}"); continue
            it.setdefault("id", f"ANC-{len(db['anchors'])+1:03d}")
            it.setdefault("verified", False); it.setdefault("status", "pending")
            it.setdefault("used_count", 0); it.setdefault("used_by", [])
            it.setdefault("aliases", []); it.setdefault("tier", "B")
            db["anchors"].append(it); added += 1
        save_db(db)
        print(f"[add] 新增 {added} 条")
    p.set_defaults(fn=_add)

    p = sub.add_parser("stats"); p.set_defaults(fn=cmd_stats)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
