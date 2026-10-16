#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""闸门① 输入契约校验器（fail-closed）。

用途：在八道闸门开跑之前，先判「输入够不够判」。缺任一必需项 ⇒ 结论 🟠 暂不判定，
并逐条报告「缺什么 → 卡住哪道闸门 → 补什么」。

用法：
    python normalize_input.py --input case.json            # JSON 文件
    python normalize_input.py --demo                       # 打印最小样例
    python normalize_input.py --input case.json --json     # 只出 JSON（机读）

退出码：0 = 通过（八道闸门可开跑）｜ 3 = 🟠（缺必需项）｜ 2 = 输入不可解析
"""
import argparse
import json
import os
import sys

def _console_safe():
    """控制台编码护栏（2026-10-09 舰队级修复，同 _sync_md_struct._console_safe）。

    中文 Windows 下 stdout/stderr 走 cp936(GBK)。**输出被重定向或经管道/subprocess 捕获时**
    遇 GBK 不可表示字符（如 ✅🟠⚠️）即抛 UnicodeEncodeError，**整段输出中断**；
    交互式控制台走 WriteConsoleW 却无碍 ⇒ 只在「捕获输出」时显形，最易漏测。
    处理：保持流原编码不变，仅把不可表示字符降级为 '?'。
    ⚠️ 不要改成 encoding="utf-8" —— 那会让 GBK 控制台下的中文变乱码。
    """
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(errors="replace")
        except Exception:
            pass


_console_safe()

# ---- 必需项定义：(路径, 中文名, 缺失时卡住的闸门, 为什么需要) --------------------
REQUIRED = [
    ("media.name",           "介质名称（或 CAS）", "①→全链", "决定查哪些腐蚀/开裂体系"),
    ("media.concentration",  "浓度（须带单位）",   "④⑤⑥",   "SCC 与腐蚀速率都强依赖浓度；无单位不可用"),
    ("media.temperature",    "温度（正常/最高/最低）", "③④⑤⑥", "温度是几乎所有判据的边界量"),
    ("media.pressure",       "压力",              "②③",     "定饱和温度（低温侧）与机械边界"),
    ("media.phase",          "相态",              "③④⑤",   "气/液/气液两相/含固，决定机理"),
    ("media.water_content",  "含水量",            "④",      "液氨/湿 H₂S 等 SCC 的含水量是硬门槛"),
    ("equipment.type",       "设备类别",          "⑧",      "决定取哪本标准（容器/管道口径不同量）"),
    ("equipment.design_life","设计寿命",          "⑤",      "均匀腐蚀速率 × 寿命 才能与腐蚀裕量比"),
    ("equipment.welded",     "是否焊接",          "⑦",      "焊缝/热影响区是最薄弱环节"),
]

# ---- 审核任务（任务 B）追加必需项 --------------------------------------------
REVIEW_REQUIRED = [
    ("review.grade",        "完整牌号",        "③⑤⑥", "只写「不锈钢」无法判定（430/410 与 304 结论相反）"),
    ("review.product_form", "产品形式（板/管/锻/铸）", "③⑦⑧", "标准与韧性要求随产品形式不同"),
    ("review.corrosion_allowance", "腐蚀裕量",  "⑤",    "没有裕量就没有比较的右边"),
]

DEMO = {
    "task": "B",  # A=选型(给介质求材质) / B=审查(给材质判合规)
    "media": {
        "name": "液氨", "cas": "7664-41-7",
        "concentration": {"value": 99.6, "unit": "wt%"},
        "temperature": {"normal": 40, "max": 50, "min": -33, "unit": "degC"},
        "pressure": {"value": 1.6, "unit": "MPa(G)"},
        "phase": "liquid",
        "water_content": {"value": 0.1, "unit": "wt%"},
        "impurities": ["air"],
        "flow_velocity": {"value": 0.5, "unit": "m/s"},
        "may_condense_or_dry": False
    },
    "equipment": {"type": "压力容器", "design_life": 20, "welded": True, "pwht": True},
    "review": {"grade": "Q345R", "product_form": "板", "corrosion_allowance": {"value": 3, "unit": "mm"}}
}


def get(d, path):
    cur = d
    for k in path.split("."):
        if not isinstance(cur, dict) or k not in cur:
            return None, False
        cur = cur[k]
    return cur, True


def is_blank(v):
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    if isinstance(v, dict):
        # 形如 {"value":..,"unit":..} 须 value 与 unit 齐备。
        # ⚠️ unit **键缺失**与 unit 为空**同等视同缺项**（2026-10-09 负控抓出：
        #    原实现只在"有 unit 键但为空"时报警，漏了"根本没有 unit 键"）。
        if "value" in v:
            if v.get("value") in (None, ""):
                return True
            return not str(v.get("unit", "")).strip()
        return not v
    return False


def validate(data):
    missing = []
    task = str(data.get("task", "A")).upper()
    req = list(REQUIRED) + (REVIEW_REQUIRED if task == "B" else [])
    for path, cn, gate, why in req:
        v, found = get(data, path)
        if not found or is_blank(v):
            unit_hint = ""
            if found and isinstance(v, dict) and "value" in v and not str(v.get("unit", "")).strip():
                unit_hint = "（有数值但缺单位 ⇒ 视同缺项）"
            missing.append({"field": path, "meaning": cn, "blocks_gate": gate,
                            "why": why + unit_hint})
    return task, missing


def main():
    ap = argparse.ArgumentParser(description="闸门① 输入契约校验（fail-closed）")
    ap.add_argument("--input", help="输入 JSON 文件")
    ap.add_argument("--demo", action="store_true", help="打印最小输入样例并退出")
    ap.add_argument("--json", action="store_true", help="只输出 JSON（机读）")
    a = ap.parse_args()

    if a.demo:
        print(json.dumps(DEMO, ensure_ascii=False, indent=2)); return 0
    if not a.input:
        ap.error("需要 --input，或 --demo")

    try:
        with open(a.input, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
    except Exception as e:
        print(json.dumps({"verdict": "输入不可解析", "error": str(e)}, ensure_ascii=False))
        return 2

    task, missing = validate(data)
    verdict = "OK 通过" if not missing else "🟠 暂不判定"
    out = {
        "gate": "① 输入完整性",
        "task": task,
        "verdict": verdict,
        "missing_count": len(missing),
        "missing": missing,
        "next": ("八道闸门可开跑" if not missing else
                 "补齐下列必需项后方可开跑；**不得推测补齐、不得默认放行**"),
    }
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=2)); return 0 if not missing else 3

    print("=" * 68)
    print(f"闸门① 输入完整性校验    任务类型：{'B 审查' if task == 'B' else 'A 选型'}")
    print("=" * 68)
    if not missing:
        print("[OK] 通过——九项必需字段齐备（含审核追加三项），八道闸门可开跑。")
        return 0
    print(f"[HOLD] 暂不判定——缺 {len(missing)} 项必需字段：\n")
    for m in missing:
        print(f"  · {m['meaning']:<22} [{m['field']}]")
        print(f"      卡住闸门：{m['blocks_gate']}")
        print(f"      为什么必需：{m['why']}")
    print("\n[!] 输出为 [HOLD]（暂不判定），不是「可以用」。[HOLD] 是一条行动指令：补齐上述字段。")
    print("[!] 禁止推测补齐；禁止把 [HOLD] 读成「大概可以」。")
    return 3


if __name__ == "__main__":
    sys.exit(main())
