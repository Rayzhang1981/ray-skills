#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""闸门④「体系覆盖」对账器 —— 防「references 写了、引擎没编码」。

## 为什么需要它
`ray-material-selection` 已在 **NaOH 45%/220 ℃** 真实案例上吃过一次：
`references/gate-04-scc.md` 列了 **13 个 SCC 体系**，而引擎 `SCC_RULES` 只编码了 **5 条**
⇒ 碳钢/304/316L **全部被判 ✅**，而它们都在碱脆高危区。
**这类缺口不会自己报错**（文件在、条目在、门禁全绿），只有真实案例撞上来才暴露。

## 判据（三条，任一不满足即 FAIL）
1. **两侧同集**：`gate-04-scc.md` 的 `### 1.N` 小节 ↔ 引擎 `GATE04_SYSTEMS` 的键，**必须完全相等**。
2. **每个体系都有「处置声明」**：∈ `SCC_RULES.section`（编码为规则）
   ∪ `NOT_A_RULE`（刻意不设为规则，须写理由）∪ `SHUTDOWN_NOTES.section`（停工窗口提醒）。
   —— **"没编码"不是问题，"没声明"才是问题**：声明了的缺口是可核查的，未声明的缺口是静默的。
3. **没有孤儿规则**：`SCC_RULES` 里每条规则的 `section` 必须存在于 `GATE04_SYSTEMS`。

## 用法
    python check_rule_coverage.py            # 对账；0 = 通过，1 = 有缺口，2 = 环境错
    python check_rule_coverage.py --selftest # 负控：构造"缺规则/多体系"，断言必被咬出
"""
import io
import os
import re
import sys


def _safe():
    """控制台编码护栏（同 evaluate_material._console_safe 的分工：不动编码，只降级不可表示字符）。"""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(errors="replace")
        except Exception:
            pass


_safe()

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(os.path.dirname(HERE), "references", "gate-04-scc.md")


def ref_sections(path=REF):
    """从 gate-04-scc.md 抽 `### 1.N` 小节号。"""
    txt = io.open(path, encoding="utf-8").read()
    got = set(re.findall(r"^###\s+(1\.\d+)", txt, re.M))
    return sorted(got, key=lambda s: tuple(int(x) for x in s.split(".")))


def engine_facts():
    """从引擎读四张表（**不复制**，直接 import 取真值）。"""
    sys.path.insert(0, HERE)
    import evaluate_material as E                      # noqa: E402
    return {
        "systems": set(E.GATE04_SYSTEMS),
        "rules": {r.get("section") for r in E.SCC_RULES},
        "not_a_rule": set(E.NOT_A_RULE),
        "shutdown": {n.get("section") for n in E.SHUTDOWN_NOTES},
        "n_rules": len(E.SCC_RULES),
    }


def check(ref=None, facts=None):
    """返回 (problems: list[str], info: dict)。"""
    ref = list(ref if ref is not None else ref_sections())
    f = facts if facts is not None else engine_facts()
    declared = f["rules"] | f["not_a_rule"] | f["shutdown"]
    problems = []

    both = sorted(set(ref) & f["systems"],
                  key=lambda s: tuple(int(x) for x in s.split(".")))
    only_ref = sorted(set(ref) - f["systems"],
                      key=lambda s: tuple(int(x) for x in s.split(".")))
    only_eng = sorted(f["systems"] - set(ref),
                      key=lambda s: tuple(int(x) for x in s.split(".")))
    unhandled = sorted(set(ref) - declared,
                       key=lambda s: tuple(int(x) for x in s.split(".")))
    orphan = sorted(f["rules"] - set(ref),
                    key=lambda s: tuple(int(x) for x in s.split(".")))
    bad_orphan = sorted(x for x in f["rules"] if x is None)

    if only_ref:
        problems.append("判据 1 破：gate-04 有而引擎覆盖表**无** = %s" % only_ref)
    if only_eng:
        problems.append("判据 1 破：引擎覆盖表有而 gate-04 **无** = %s（references 删过？）" % only_eng)
    if unhandled:
        problems.append("判据 2 破：**无处置声明**的体系 = %s "
                        "（既不在 SCC_RULES，也不在 NOT_A_RULE/SHUTDOWN_NOTES）" % unhandled)
    if orphan:
        problems.append("判据 3 破：SCC_RULES 引用了覆盖表外的 section = %s" % orphan)
    if bad_orphan:
        problems.append("判据 3 破：SCC_RULES 有规则缺 `section` 键（%d 条）" % len(bad_orphan))

    info = {
        "gate-04 小节数": len(ref),
        "引擎覆盖表条数": len(f["systems"]),
        "规则条数": f["n_rules"],
        "两侧同集": both,
        "编码为规则": sorted(x for x in f["rules"] if x),
        "刻意不设为规则": sorted(f["not_a_rule"]),
        "停工窗口提醒": sorted(x for x in f["shutdown"] if x),
    }
    return problems, info


def selftest():
    """负控：检查器**必须**能咬出构造出来的缺口（只跑正例等于没验）。"""
    base = engine_facts()
    cases = []

    # 负控 1：引擎侧删掉 §1.3 硝脆的规则（模拟"references 有、引擎没有"）
    f1 = dict(base, rules=base["rules"] - {"1.3"})
    cases.append(("删掉 §1.3 规则", f1, True))

    # 负控 2：引擎覆盖表多出一条 references 没有的体系
    f2 = dict(base, systems=base["systems"] | {"1.99"})
    cases.append(("覆盖表多出 §1.99", f2, True))

    # 负控 3：把 §1.11 从 SHUTDOWN_NOTES 里拿掉且不设规则（模拟"漏声明"）
    f3 = dict(base, shutdown=base["shutdown"] - {"1.11"})
    cases.append(("§1.11 既无规则也无声明", f3, True))

    # 正控：真身必须通过
    cases.append(("正控 · 真身", base, False))

    ok = True
    for label, facts, want_fail in cases:
        probs, _ = check(facts=facts)
        got_fail = bool(probs)
        good = (got_fail == want_fail)
        ok &= good
        print("  [%s] %-26s 期望%s 实得%s  %s"
              % ("PASS" if good else "FAIL", label,
                 "FAIL" if want_fail else "PASS", "FAIL" if got_fail else "PASS",
                 ("| " + probs[0][:70]) if probs else ""))
    print("\n负控结论：%s" % ("全部符合预期" if ok else "**有负控不符合预期，检查器口径有问题**"))
    return 0 if ok else 1


def main():
    if "--selftest" in sys.argv:
        return selftest()
    if not os.path.exists(REF):
        print("找不到 references/gate-04-scc.md：%s" % REF)
        return 2
    probs, info = check()
    print("=" * 76)
    print("闸门④ 体系覆盖对账：references/gate-04-scc.md vs scripts/evaluate_material.py")
    print("=" * 76)
    for k, v in info.items():
        print("  %-16s %s" % (k, v))
    print("-" * 76)
    if probs:
        print("结论：FAIL（%d 项）" % len(probs))
        for p in probs:
            print("  [X] " + p)
        return 1
    print("结论：PASS —— %d 个体系**全部有处置声明**，无静默缺口。" % info["gate-04 小节数"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
