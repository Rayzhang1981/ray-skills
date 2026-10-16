# -*- coding: utf-8 -*-
"""verify_skill_cases.py —— ray-chem-compat 案例回环（验收锚点自动复核）

定位
    把 SKILL.md「验收纪律」里的**验收锚点**从「人工回放」升级为**一条带退出码的命令**。
    改动数据层（group_pair_rules / chem_index / 各兜底库）任何一步后跑它。

覆盖范围（**如实标注边界**）
    ✅ 引擎健康不变量：规则对 2346 / 基团 68（数值取自 SKILL.md 明文，非本文件编造）
    ✅ 已点名单例：`水合肼×磷酸 = C`、`水合肼×二氧化碳 = Y`（2026-09-24 案例回环的既有结论）
    ✅ 自组对规范化路径：`codes == {UR}` 的同组两化学品 → **C**；`codes == {NR}` → **Y**
       （即 SKILL.md 里 `硫酸×硝酸=C` 的机制锚点——「Acids, Strong Oxidizing² → UR→C」）
    ❌ **两项集合级标尺**（`水合肼 18 项标尺` / `叔辛胺 15 项 SDS 禁配`）**无法自动重放**：
       其**成员名单**（哪 18 个 / 哪 15 个）未随库归档，只有聚合期望（16N+1C+1Y / 13N+2C）
       ⇒ 仍须**人工回放**；本脚本会在输出尾部打印其期望值提示，便于人工对账。

用法
    python verify_skill_cases.py              # 复核，退出码 0=全过 / 1=有判错 / 2=环境错误
    python verify_skill_cases.py --selftest   # 自测（含负控：注入错误期望必须被判错）
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import compat_engine as CE  # noqa: E402

DATA = os.path.normpath(os.path.join(HERE, "..", "data"))


def load_index():
    with io.open(os.path.join(DATA, "chem_index.json"), encoding="utf-8") as fh:
        return {c.get("cn"): c for c in json.load(fh)["chemicals"]}


def build_checks(kb, idx, inject_bad=False):
    """返回 [(名称, 实际值, 期望值)]；期望值全部来自 SKILL.md 明文或知识库派生。"""
    checks = []

    def verdict(a, b):
        ca, cb = idx.get(a), idx.get(b)
        if not ca or not cb or not ca.get("groups") or not cb.get("groups"):
            raise RuntimeError("案例化学品缺基团：%s / %s" % (a, b))
        return CE.predict_cell(kb, ca["groups"], cb["groups"])[0]

    # 1) 引擎健康（数值出自 SKILL.md：len(kb['kb']['rules'])==2346、len(kb['groups'])==68）
    checks.append(("engine.rules_count", len(kb["kb"]["rules"]), 2346))
    checks.append(("engine.groups_count", len(kb["groups"]), 68))

    # 2) 已点名单例（2026-09-24 案例回环结论）
    checks.append(("case.水合肼×磷酸", verdict("水合肼", "磷酸"), "C"))
    checks.append(("case.水合肼×二氧化碳", verdict("水合肼", "二氧化碳"), "Y"))

    # 3) 自组对规范化：{UR}→C / {NR}→Y（机制锚点，期望由知识库 self_pair 语义派生）
    seen_ur, seen_nr = [], []
    for r in kb["kb"]["rules"]:
        if not r.get("self_pair"):
            continue
        codes = tuple(sorted(set(r.get("codes") or [])))
        if codes == ("UR",):
            seen_ur.append(r["group_a"])
        elif codes == ("NR",):
            seen_nr.append(r["group_a"])
    if seen_ur:
        g = sorted(set(seen_ur))[0]
        checks.append(("selfpair.UR→C(%s)" % g, CE.predict_cell(kb, {g}, {g})[0], "C"))
    else:
        checks.append(("selfpair.UR→C", "<无 UR 自对基团>", "C"))
    if seen_nr:
        g = sorted(set(seen_nr))[0]
        checks.append(("selfpair.NR→Y(%s)" % g, CE.predict_cell(kb, {g}, {g})[0], "Y"))

    if inject_bad:                      # 负控：把期望改成必错值，检查器必须咬出
        checks.append(("selftest.injected_bad", len(kb["groups"]), 68 + 1))
    return checks


MANUAL_HINT = [
    "【人工回放提示】以下两项为**集合级标尺**，成员名单未随库归档，脚本不代判：",
    "  · 水合肼 18 项标尺 —— 期望 16 项判 N、1 项判 C（磷酸）、1 项判 Y（二氧化碳）；化学轴 0 处判错",
    "  · 叔辛胺 15 项 SDS 禁配 —— 期望 0 处判成 Y（强氧化剂 N,N,N,N,C；酸类 N,N,N,N,C,N,N,N；酰氯 N；酸酐 N）",
]


def main(argv):
    inject_bad = "--selftest" in argv
    try:
        kb = CE.default_kb()
        idx = load_index()
        checks = build_checks(kb, idx, inject_bad=inject_bad)
    except Exception as e:                                  # 环境/数据问题 ≠ 判错
        sys.stderr.write("ENV_ERROR: %s\n" % e)
        return 2

    bad = []
    for name, got, want in checks:
        ok = (got == want)
        if not ok:
            bad.append(name)
        print("%-4s %-44s got=%-6s want=%s" % ("PASS" if ok else "FAIL", name, got, want))

    for line in MANUAL_HINT:
        print(line)

    if inject_bad:                                          # 自测断言：负控必须被咬出
        caught = "selftest.injected_bad" in bad
        print("\nSELFTEST: 负控被咬出 = %s / 正例是否全过 = %s"
              % (caught, "是" if all(n != "selftest.injected_bad" for n in bad) else "否"))
        sys.stderr.write("selftest: negative control caught = %s\n" % caught)
        return 0 if caught else 1

    print("\nSUMMARY: %d/%d 通过%s" % (len(checks) - len(bad), len(checks),
                                       "" if not bad else "  判错项=%s" % bad))
    sys.stderr.write("verify_skill_cases: %d/%d passed\n" % (len(checks) - len(bad), len(checks)))
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
