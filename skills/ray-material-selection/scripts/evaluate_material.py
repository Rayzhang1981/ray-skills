#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""八道闸门判定引擎（串联否决 / fail-closed）。

设计原则（与 SKILL.md §一 一致）：
  · **串联否决**：任一闸门 FAIL ⇒ 结论 🔴，不被其他闸门的 PASS 抵消。
  · **fail-closed**：数据不足 ⇒ 🟠，**绝不默认放行**。
  · **不做评分排序**：输出的是「哪一闸门、失败/通过、判据出处」，不是分数。

数据源：腐蚀数据（Alleima 主库）**不在 skill 目录内**（红线），
        须由 `--data-root` 或环境变量 `RAY_MATSELECT_DB` 提供；未提供 ⇒ 闸门⑤⑥ 判 🟠。

用法：
    python evaluate_material.py --demo
    python evaluate_material.py --case case.json --material "Carbon steel" [--data-root <目录>] [--json]

退出码：0=✅/🟡 ｜ 3=🟠 ｜ 4=🔴 ｜ 2=用法/解析错误
"""
import argparse
import csv
import json
import os
import re
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

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
try:
    from normalize_input import validate as validate_contract   # 闸门① 复用同一判据
except Exception:                                              # pragma: no cover
    validate_contract = None

OK, YELLOW, ORANGE, RED = "✅", "🟡", "🟠", "🔴"

# 控制台友好显示名（2026-10-09 修：`_DISP` 在 main() 里被引用却**从未定义** ⇒
# 默认（非 --json）输出路径直接 NameError 崩、退出码 1 —— 而 `--json` 路径完全正常，
# 故此前"测试全绿"掩盖了它（**只测了 JSON 路径 = 覆盖面缺口**）。
# ⚠️ 本行**必须 GBK 安全**（生态回归门 `gbk_console_check.py` 已固化该政策）：人读路径会被
#    重定向/管道捕获，emoji 在 cp936 下退化为 '?' ⇒ 显示串只用「中文 + ASCII」；
#    emoji 常量（OK/…）只进 --json 契约——那条路已强制 UTF-8。
_DISP = {OK: "[通过 PASS]", YELLOW: "[有条件推荐 COND]", ORANGE: "[暂不判定 HOLD]", RED: "[否决 FAIL]"}

# ============================================================ 闸门③ 温度边界
# ⚠️ 本表有两类**语义完全不同**的行，靠 kind 区分（2026-10-09 实测抓出的真 bug：
#    首版把两者混在一张表里，导致 Q235B 被判成"0℃ < 上限300℃ ⇒ 落入脆性区"的错逻辑）：
#      kind="dbtt"  → lo~hi 是**脆性转变带**：低于 hi 即进入脆性/转变区（材料固有属性）
#      kind="allow" → lo~hi 是**标准允许使用区间**：低于 lo 或高于 hi 才算**违规**（合规边界）
#    这两者**不是同一个量，也不可互相顶替**（见 SKILL.md §一 立场 3）。
DBTT = [
    # (牌号正则, 口径说明, lo, hi, kind, 出处)
    (r"^20#|^20钢|^20$",    "热轧态（出厂常用态）", -10, -6,  "dbtt", "《20钢冻结管低温性能试验分析》A_KV=21 J 判据"),
    (r"^20#|^20钢|^20$",    "正火态 860~910℃",     -40, -20, "dbtt", "《热处理对20钢韧脆转变温度的影响》"),
    (r"^10#|^16MnR?$",      "曲线B 允许使用下限",   -20, None, "allow", "GB/T 20801.2-2020 曲线B"),
    (r"^Q235B$",            "**管道**允许使用下限", -10, None, "allow", "GB/T 20801.2-2020 曲线A"),
    (r"^Q235B$",            "**容器**允许使用区间", 20, 300,   "allow", "GB/T 150.2-2024 附录D e（**与管道口径不同量**）"),
    (r"^Q235C$",            "**容器**允许使用区间", 0, 300,    "allow", "GB/T 150.2-2024 附录D e"),
    (r"^304|^316L?$|^321$", "奥氏体 FCC：**无韧脆转变**；允许使用下限", -269, None, "allow",
     "GB/T 150.2-2024 4.10 b)（≥-196℃ 免做冲击试验）；GB/T 14976"),
    (r"^2205$|^SAF.*2205",  "双相（DBTT 约）",      None, -50, "dbtt",  "多源数据表一致"),
    (r"镍|Nickel|Ni\s*2\d\d|哈氏|Hastelloy|Inconel|Incoloy|Monel|C-?276|C-?22",
     "无韧脆转变（单相奥氏体/面心立方）", None, None, "dbtt",
     "镍基合金为面心立方、无韧脆转变（材料属性）；**许用应力与高温氧化/渗碳另判**（本表只判低温侧）"),
    (r"^钛|TA[0-9]|Titanium", "无韧脆转变（密排六方，低温仍具韧性）", None, None, "dbtt",
     "钛在低温下仍保持韧性（工程共识）；**高温碱/氢环境另判**"),
    (r"^430$",              "铁素体（DBTT）",       -20, 0,   "dbtt",  "多源一致（比 20# 热轧态还差）"),
    (r"^410$|^420$",        "马氏体（DBTT）",       20, 30,   "dbtt",  "单一源，随热处理变化；**常温即脆**"),
]


def _judge_row(state, lo, hi, kind, tmin, tmax):
    """按 kind 分派两种完全不同的判法。返回 (是否越限, 说明)。"""
    if kind == "dbtt":
        if tmin is not None and hi is not None and tmin < hi:
            return True, f"⚠️ 最低温 {tmin}℃ 低于转变带上限 {hi}℃ ⇒ **进入脆性/转变区**"
        return False, "高于转变带上限，未进入脆性区"
    # kind == "allow"：标准允许使用区间
    bad = []
    if tmin is not None and lo is not None and tmin < lo:
        bad.append(f"最低温 {tmin}℃ < 允许下限 {lo}℃")
    if tmax is not None and hi is not None and tmax > hi:
        bad.append(f"最高温 {tmax}℃ > 允许上限 {hi}℃")
    return (bool(bad), "⚠️ **超出标准允许区间**：" + "；".join(bad)) if bad else (False, "落在标准允许区间内")


def gate3_temperature(case, material):
    """返回 (status, detail)。低温侧为主；高温侧只给提示。"""
    t = case.get("media", {}).get("temperature") or {}
    tmin = t.get("min", t.get("normal"))
    tmax = t.get("max", t.get("normal"))
    dev = (case.get("equipment", {}).get("type") or "")
    hits = [r for r in DBTT if re.search(r[0], str(material), re.I)]
    if not hits:
        return ORANGE, {
            "缺": f"牌号 {material!r} 不在本引擎的内置门槛表内",
            "动作": "查 references/gate-03-temperature.md 的材料表；无覆盖则标未覆盖（**不得外推**）",
        }
    lines = []
    worst = OK
    for _, state, lo, hi, kind, src in hits:
        over, judgement = _judge_row(state, lo, hi, kind, tmin, tmax)
        if over:
            worst = RED
        lines.append({"口径": state, "类型": "脆性转变带" if kind == "dbtt" else "允许使用区间",
                      "lo": lo, "hi": hi, "出处": src, "判定": judgement})
    if re.search("Q235B", str(material), re.I):
        lines.append({"提醒": "Q235B：**容器 20~300℃  vs  管道 −10℃ —— 两者不同量，差 30 K**",
                      "当前设备类别": dev,
                      "出处": "GB/T 150.2-2024 附录D e ／ GB/T 20801.2-2020 曲线A"})
    return worst, {"温度": {"min": tmin, "max": tmax}, "材料口径": lines,
                   "高温侧": "本引擎未做定量判定；**粗筛门槛**（GB/T 30579-2022 附录 C.4 b)，资料性/A−，已亲核物理页 153）："
                             "**<400 ℃ 可先排除材质劣化类损伤、<300 ℃ 可先排除蠕变**；"
                             "高温氢腐蚀见 Nelson 曲线区＋4 条机理注文（Mo 提高抗力／Cr·V·Ti·Nb 有利／Mn·Cu·Si·Al 无补／"
                             "破坏=脱碳+晶界腐蚀+失强）⇒ references/gate-03-temperature.md",
                   "判据句": "**材料脆性门槛（何时变脆）≠ 标准允许使用范围（能用到多少度）；两条都要过**"}

# ============================================================ 材料族归一（闸门④⑦ 共用）
# ⚠️ 2026-10-09 实测抓出的真 bug：SCC 规则原按**字面**匹配材料（如 `碳钢|carbon steel`），
#    于是真实牌号 `20# 无缝管` / `Q345R` / `A105` **全部漏判** —— 规则对但**用法错**。
#    修法：建**材料族**归一表，规则判「族」不判字面。（与 Alleima 的 ALIAS 同源思路）
MAT_FAMILY = [
    ("carbon_steel",     r"碳钢|碳素钢|20\s*#|20\s*钢|10\s*#|Q235|Q245|Q275|Q345|16Mn|A105|A106|WCB|WCC|"
                         r"carbon\s*steel|\bCS\b|\b20G\b"),
    ("low_alloy",        r"低合金|16MnR|Q345R|15CrMo|12CrMo|1\.25Cr|2\.25Cr|Cr-?Mo|铬钼|SA-?387"),
    ("austenitic_ss",    r"304|316|321|347|904L|奥氏体|austenitic|18-?8|2RK65|254\s*SMO|654\s*SMO|Sanicro|3R60|3R12"),
    ("duplex_ss",        r"2205|2507|2304|2906|2707|3207|双相|duplex|SAF"),
    ("ferritic_ss",      r"430|446|铁素体|ferritic"),
    ("martensitic_ss",   r"\b410\b|\b420\b|440|马氏体|martensitic|13\s*Cr"),
    ("copper",           r"铜|\bCu\b|brass|黄铜|bronze|青铜|cupronickel|白铜|Monel"),
    ("nickel_alloy",     r"哈氏|Hastelloy|Inconel|Incoloy|Monel|镍基|镍\s*2\d\d|纯镍|Nickel\s*2\d\d|\bnickel\b|Ni\s*2\d\d|C-?276|C-?22|合金\s*B"),
    ("titanium",         r"钛|\bTi\b|TA[0-9]|Titanium"),
    # ⚠️ 2026-10-10 P0-2 轮修：原 `\bZr\b|Zirconium` **漏判真实牌号**——`Zr702`（无词边界）、
    #    `Zircaloy-2/4`（无 Zirconium 字样）全部落空 ⇒ 锆的禁忌规则对最常用的两个写法**静默不触发**。
    #    判据同「真实牌号漏判」族：按名称匹配的表必须把**牌号写法**收全（这里：Zr70x / Zr-2.5Nb / Zircaloy）。
    ("zirconium",        r"锆|Zr\s*70\d|Zr-?2\.?5|Zircaloy|zircaloy|\bZr\b|Zirconium"),
    ("hafnium",          r"铪|Hf-|\bHf\b|hafnium"),
    ("silver",           r"银|\bAg\b|Silver"),
    ("aluminium",        r"铝|\bAl\b|Aluminium|Aluminum"),
    ("polymer",          r"PVC|CPVC|PP\b|HDPE|PTFE|PVDF|FRP|塑料|聚乙烯|聚丙烯|聚四氟"),
]


def mat_families(material):
    """把牌号/材质名归一为材料族集合。**命中即返回族名**（可多族）。"""
    s = str(material)
    return {fam for fam, pat in MAT_FAMILY if re.search(pat, s, re.I)}


# ============================================================ 闸门④ 环境开裂
# 每条规则 = (触发条件, 结论, 出处)。**只收有出处的硬门槛**；没门槛的只报"需查表"。
# -------------------- 环境侧线索取值器（闸门④ 各规则共用）
def _case_text(case):
    """整个 case 序列化为小写文本 —— 供"环境侧线索"（如镀锌件、涂层）检索。
    用途限定：只在 case 里没有专门字段时兜底（如 §1.13 的锌污染来源）。"""
    try:
        return json.dumps(case, ensure_ascii=False).lower()
    except Exception:
        return str(case).lower()


def _media_text(c):
    m = c.get("media", {}) or {}
    return " ".join(str(m.get(k, "")) for k in ("name", "impurities", "notes"))


def _tmax(c):
    t = (c.get("media", {}) or {}).get("temperature") or {}
    v = t.get("max", t.get("normal"))
    try:
        return float(v) if v is not None else None
    except Exception:
        return None


def _pwht(c):
    return bool((c.get("equipment") or {}).get("pwht"))


# ============================================================ 闸门④ 环境开裂
# 每条规则 = (触发条件, 结论, 出处)。
# **只收有出处的判据**；没门槛的只报"需查表"（need_verify=True ⇒ 整体判 🟠，不硬判 🔴）。
#
# ⚠️ 2026-10-09（本轮）修的真缺口：首版只编码 5 条，而 `gate-04-scc.md` 列了 **13 个体系**
#    ⇒ **文件里有 ≠ 引擎会用**（NaOH 案例已吃过一次）。本轮补齐到 **13 体系全部有处置声明**，
#    并加 `GATE04_SYSTEMS` / `NOT_A_RULE` 两张表 + `scripts/check_rule_coverage.py` 机检，
#    让"references 加了、引擎没加"**无法再静默发生**。
#
# 分档原则（判据）：**源给了可判定的门槛 ⇒ 命中即 🔴；源未给门槛 ⇒ 命中但 🟠（need_verify，须人工定档）**。
SCC_RULES = [
    # ---------------- §1.1 氯化物 + 奥氏体不锈钢
    dict(section="1.1", name="氯化物 + 奥氏体不锈钢",
         when=lambda c: ("austenitic_ss" in mat_families(c.get("material", "")))
                        and re.search(r"氯|盐酸|氢氯酸|chlorid|hydrochloric|\bHCl\b|Cl-|Cl⁻",
                                      _media_text(c), re.I),
         verdict="可能命中：Cl⁻ 应力腐蚀开裂（含保温层下 CLSCC）",
         source="见 references/gate-04-scc.md §1.1（本引擎**不内置其温度/浓度门槛**，避免臆造）",
         action="⚠️ 本引擎**不给结论**，必须查 gate-04-scc.md 的门槛表",
         need_verify=True),

    # ---------------- §1.2 碱脆（碳钢/低合金）
    dict(section="1.2", name="碱脆（碱液 + 碳钢/低合金钢，caustic embrittlement）",
         when=lambda c: re.search(r"氢氧化钠|烧碱|苛性钠|液碱|sodium\s*hydroxide|caustic|\bNaOH\b",
                                  _media_text(c), re.I)
                        and ({"carbon_steel", "low_alloy"} & mat_families(c.get("material", "")))
                        and (float((c["media"].get("concentration") or {}).get("value", 0) or 0) >= 5)
                        and (float((c["media"].get("temperature") or {}).get("max", 0) or 0) > 50),
         verdict="命中：碱脆（碱应力腐蚀开裂）风险区",
         source="**两源口径并列（不代裁）**——① gate-04 §1.2（源自 asm-v13/gailun）：NaOH **15%~48%**；"
                "约 **30% < 82 ℃ 不发生**、**50% 在 52 ℃ 即发生**；② L1b 备注（人工汇编）："
                "碱脆三角区 **NaOH≥5% 但 <50 ℃ 基本安全**；**50% 液碱 48 ℃ 附近即临界**；**>40% 且 >80 ℃ 应用 Ni 合金**；"
                 "③ **《腐蚀数据与选材手册》(1995) 第三源**——正文 p639（物理 656）：『**镍是耐热浓碱液腐蚀的最好的材料**』；"
                 "正文 p662（物理 679）：Monel『对热浓碱液也有优良的耐蚀性，但不及纯镍』；"
                 "**附图 3（正文 p1302）为碳钢/镍合金在烧碱中的适用区域图（图形件，浓度-温度边界查原图）**；"
                 "④ **同书第十二章正文（正文 202~212／物理 219~229，A−）**——**「>30%＋>50 ℃＋应力＝碱脆三要素」**；"
                 "50%/65 ℃≈0.2、70%/105 ℃≈1.5、熔碱 400 ℃≈10~20 mm/a（碳钢）；**316 并不优于 304（碱介质无钼增益）**；"
                 "镍系一切浓度温度（熔融 280 ℃；50% 蒸浓 0.002 mm/a）；**熔碱锅 75~98%/300~500 ℃＋应力→晶间应力腐蚀破裂，用前退火**；"
                 "高镍铸铁（Ni15~30%）至无水熔碱；铸铁加 3~5% Ni 腐蚀率近减半",
         action="⚠️ 两源门槛形态不同 ⇒ **按更保守一侧执行**：本案例 45%/220 ℃ **远超两源的任一临界**。"
                "措施：PWHT 消除应力 + 硬度控制，或**升级为镍基/高镍合金**（碱的经典选材）",
         ),

    # ---------------- §1.2 延伸：碱 + 奥氏体不锈钢
    dict(section="1.2", name="碱 + 奥氏体不锈钢（高浓高温）",
         when=lambda c: re.search(r"氢氧化钠|烧碱|苛性钠|液碱|sodium\s*hydroxide|caustic|\bNaOH\b",
                                  _media_text(c), re.I)
                        and ("austenitic_ss" in mat_families(c.get("material", "")))
                        and (float((c["media"].get("concentration") or {}).get("value", 0) or 0) >= 30)
                        and (float((c["media"].get("temperature") or {}).get("max", 0) or 0) > 100),
         verdict="可能命中：高浓高温碱环境下奥氏体不锈钢的碱致开裂/腐蚀",
         source="L1b 备注：『304/316 ≤100 ℃ 基本可用』（**>100 ℃ 的边界该源未给数值**）"
                "；gate-04 §1.2 亦未给不锈钢的碱门槛 ⇒ **⚠️待核实**",
         action="⚠️ **本引擎不给结论**：须查 gate-04-scc.md §1.2 与 L1 数据；"
                "45%/220 ℃ 属该源明确未覆盖区间",
         need_verify=True),

    # ---------------- §1.3 硝脆（本轮新增）
    dict(section="1.3", name="硝脆（硝酸盐/亚硝酸盐 + 碳钢/低合金钢）",
         # ⚠️ 本轮自测抓出的**真 bug**：首版只写 `硝酸盐`（通称），而用户实际写的是 **`硝酸钠`**
         #    ——「硝酸钠」**不含子串「硝酸盐」** ⇒ 规则存在却**点不着火**（= "判据对但用错"）。
         #    修：通称 + **逐个硝酸盐/亚硝酸盐品名** + 常见分子式。判据句：**按名称匹配的判据，
         #    必须把「通称」与「实物品名」两套都收全**，否则真实牌号/品名会被静默漏掉（同 MAT_FAMILY 那条教训）。
         when=lambda c: re.search(r"硝酸盐|亚硝酸盐|硝铵|硝石"
                                  r"|硝酸[金银铜铁镍锌铅锶钠钾铵钙镁锂钡铝锰钴镉汞]"
                                  r"|亚硝酸[钠钾钙]"
                                  r"|nitrate|nitrite|\bNaNO3\b|\bKNO3\b|\bNH4NO3\b|\bNaNO2\b",
                                  _media_text(c), re.I)
                        and ({"carbon_steel", "low_alloy"} & mat_families(c.get("material", ""))),
         verdict="命中：硝酸盐硝脆环境（碳钢/低合金钢）",
         source="gate-04 §1.3（gailun p.112）：**含碳 0.04% 即容易硝脆** ⇒ 敏感性绑定**含碳量**；"
                "碳钢在硝酸盐**焊后未热处理区**高发",
         action="措施：**焊后消应力热处理（首选）**／规避硝酸盐与碳钢接触／控浓度与温度。"
                "⚠️ 源**未给浓度/温度门槛** ⇒ 须回查标准/手册确认本工况是否仍属敏感区",
         need_verify=True),

    # ---------------- §1.4 液氨 + 碳钢/低合金钢
    dict(section="1.4", name="液氨 + 碳钢/低合金钢",
         when=lambda c: re.search("氨|ammonia", str(c["media"].get("name", "")), re.I)
                        and ({"carbon_steel", "low_alloy"} & mat_families(c.get("material", "")))
                        and (c["media"].get("water_content") or {}).get("value", 0) is not None
                        and float((c["media"].get("water_content") or {}).get("value", 100)) <= 0.2
                        and float((c["media"].get("temperature") or {}).get("max", 0) or 0) > -5,
         verdict="命中：液氨应力腐蚀环境",
         source="三源口径并列——① HG/T 20581-2011 第 7.8.4.1 条（四者同时：液态氨 + 含水量≤0.2% + 可能受空气污染 + "
                "使用温度 > -5℃）；② GB/T 30579-2022 §6.5.4（gate-04 §1.A）：含水量 **0.005%~0.2% 区间最危险**"
                "（<0.005% 干态敏感性亦较低，但须连氧含量一起核——asm：氧是促发剂）；焊接接头硬度 ≤HB225；"
                "③ 《腐蚀数据与选材手册》1995 第十三章（gate-04 §1.4 增补块）：碳钢干氨/液氨 <0.1 mm/a、湿氨/氨水 <1 mm/a"
                "——**碳钢是氨系统标准材质，速率判据与 SCC 防护判据两套都要过**",
         action="低于 −5℃ 几乎不发生（GB/HG/T 档位，保守侧；asm 记 ≤−33℃，并列留痕于 gate-04 §1.A）；"
                "须核含水量与空气污染两个前提；防护：PWHT ≥595 ℃ + 焊缝硬度 ≤HB225 + 限低强度钢"),

    # ---------------- §1.5 湿 H₂S
    dict(section="1.5", name="湿 H₂S（硫化物应力开裂 SSC）",
         when=lambda c: re.search(r"H2S|硫化氢|酸气|sour", _media_text(c), re.I),
         verdict="可能命中：湿 H₂S 环境开裂",
         source="gate-04 §1.5（asm-v13 p.1657；NACE MR-01-75）：**绝对压力 >0.45 MPa（65 psi）且 "
                "H₂S 分压 >345 Pa（0.05 psi）** ⇒ 有 SSC 风险；**>80 ℃ 失效减少**；屈服 >690 MPa 高危",
         action="⚠️ 需按分区判据核（ISO 15156 / NACE MR0175 现行版，本引擎不代判）。"
                "措施：按 MR-01-75 选材（含硬度上限）／控硬度限强度／升温 >80 ℃ 可减失效；"
                "**镍基 Ni ≥42%、Mo ≥3%**。"
                "【§1.8 CO₂ 的切换判据】gate-04 §1.8 明示 **CO₂ 不是 SCC 体系**（首要机制是均匀/台地状金属损失）"
                "⇒ 判据为 **CO₂/H₂S 分压比 >500 以 H₂S 主导**（此时按本条判），否则 CO₂ 本体腐蚀转**闸门⑤**",
         need_verify=True),

    # ---------------- §1.6 氨 + 铜及铜合金（本轮新增）
    dict(section="1.6", name="氨 + 铜及铜合金（氨脆/季裂）",
         when=lambda c: re.search(r"氨|ammonia|NH3|铵", _media_text(c), re.I)
                        and ("copper" in mat_families(c.get("material", "")))
                        and ("nickel_alloy" not in mat_families(c.get("material", ""))),
         verdict="命中：铜合金氨脆（季裂）环境",
         source="gate-04 §1.6（gailun p.208 + 《腐蚀数据与选材手册》1995 第十三章互证）：**微量氨即足**——"
                "「即使是微量的氨，也是引起黄铜 SCC 的主要环境因素」（gailun）＝「只含微量氨的大气中即可能发生应力腐蚀、"
                "**一般都不宜使用铜和铜合金**」（手册 1995 13-03/13-14，两源互证 ✓）；"
                "Zn 越高越敏感（gailun：Zn<20% 一般未见倾向；GB/T 30579：Zn>15% 即明显——15%~20% 段保守取 15%）；"
                "admiralty metal（C44300）换热管反复开裂",
         action="措施：**退火消除残余应力**（源称「无疑是一种有效措施」）／阴极保护／加 Si／隔绝氨；"
                "抽芯后**极稀硫酸中和残氨**。"
                "⚠️ **「干氨不腐蚀铜」不构成用铜的理由**——手册 1995：**只要有微量水分存在，铜就被迅速腐蚀**"
                "（绝对无水工程上几乎不可证）；"
                "⚠️ 替代选材边界（手册 1995 13-15）：湿氨环境**只有镍铬铁合金耐蚀优良——镍铜合金（Monel）只耐 2% 以下"
                "室温氨水、纯镍只耐 1% 以下** ⇒ 「换 Monel/镍」不是无条件升级。"
                "⚠️ 开裂**多在停工期间** ⇒ 开停工窗口为重点检查时机。"
                "⚠️ 本规则**已显式排除 Monel**（Ni-Cu 合金同时落入 copper 与 nickel_alloy 两族 ⇒ "
                "该走 §1.10 的 HF 判据，按氨判会误报）"),

    # ---------------- §1.7 氢脆/氢致开裂（本轮新增）
    dict(section="1.7", name="氢脆 / 氢致开裂（含高强度螺栓）",
         when=lambda c: re.search(r"氢气|加氢|\bH2\b|hydrogen", _media_text(c), re.I)
                        and ({"carbon_steel", "low_alloy", "martensitic_ss"}
                             & mat_families(c.get("material", ""))),
         verdict="**可能**命中：氢环境下的氢脆/氢致开裂（须核强度与硬度）",
         source="gate-04 §1.7（asm-v13 p.3215/3218）：氢源＝湿 H₂S/酸性水（阴极析氢）、含氢气体分解、制造带入；"
                "**韧性钢或已正确 PWHT 的钢不开裂**；三形态**勿混**：氢脆／氢鼓泡／氢应力开裂",
         action="⚠️ 门槛（临界氢浓度、螺栓 HRC/强度上限）**源未给** ⇒ 须核 NACE MR0175 / ISO 15156 与 "
                "API 941 原文。措施：正确焊后热处理；限强度硬度（**屈服 >690 MPa（100 ksi）高危**）；"
                "低氢焊材 + 烘干 + 预热后热；冶炼除气缓冷；**镀后/酸洗后除氢**。"
                "检测：**氢活性探针 + 冷凝水化学分析**",
         need_verify=True),

    # ---------------- §1.9 胺液 + 碳钢（本轮新增，拆两态）
    dict(section="1.9", name="胺液 + 碳钢 · **未做 PWHT（决定性前置未满足）**",
         when=lambda c: re.search(r"胺液|胺|MEA|DEA|MDEA|amine|Sulfinol|脱硫|脱碳", _media_text(c), re.I)
                        and ({"carbon_steel", "low_alloy"} & mat_families(c.get("material", "")))
                        and not _pwht(c),
         verdict="命中：胺液（碱性 SCC 族）环境 ＋ **未做焊后热处理（决定性前置未满足）**",
         source="gate-04 §1.9（asm-v13 p.3213）：旧判据「**<88 ℃ 不成问题**」**已被推翻**——40~60 ℃、"
                "50~95 ℃ 均开裂 ⇒ **现行不论温度全须防**；**未做 PWHT 是决定性前置条件**；"
                "**不限 MEA**（DEA、Sulfinol 亦裂）；裂纹**平行于焊缝**、与焊缝硬度无关",
         action="措施：**胺液工况碳钢件一律焊后热处理（不论温度）**（旧「620 ℃ 且 >95 ℃ 才做」已加严）；"
                "无法炉处理用**局部 PWHT 或喷丸**；**逐件磁粉检测**（储罐/吸收塔/闪蒸罐/贫胺塔/管道据此排查）"),

    dict(section="1.9", name="胺液 + 碳钢 · 已做 PWHT",
         when=lambda c: re.search(r"胺液|胺|MEA|DEA|MDEA|amine|Sulfinol|脱硫|脱碳", _media_text(c), re.I)
                        and ({"carbon_steel", "low_alloy"} & mat_families(c.get("material", "")))
                        and _pwht(c),
         verdict="命中：胺液（碱性 SCC 族）环境；**本案已做 PWHT ⇒ 决定性前置已满足**",
         source="同 §1.9（asm-v13 p.3213）——「**未做 PWHT 是决定性前置条件**」的反面读法："
                "做了 PWHT 即消除了该体系的决定性前置",
         action="⚠️ 非硬否决，但**不可就此放行**：仍须① **逐件磁粉检测**（本体/焊缝/HAZ）② 硬度核查 ③ "
                "确认 PWHT 覆盖全部焊缝（含现场组焊的环缝）——一条未覆盖即回到上一态",
         need_verify=True),

    # ---------------- §1.10 氢氟酸（本轮新增）
    dict(section="1.10", name="氢氟酸 + **钛（不推荐）**",
         when=lambda c: re.search(r"氢氟酸|氟化氢|hydrofluoric|\bHF\b|氟化物", _media_text(c), re.I)
                        and ("titanium" in mat_families(c.get("material", ""))),
         verdict="命中：**钛被 HF（极稀亦然）迅速侵蚀 ⇒ 不推荐**",
         source="gate-04 §1.10（asm-v13 p.738）：『钛被 HF（极稀亦然）迅速侵蚀 ⇒ 不推荐』",
         action="换材：**Monel 400（N04400）**最广用（须**退火态/消应力态**）；镍基 690/600 最耐但非免疫。"
                "另：**多数腐蚀问题发生在停工之后**，游离氧加速 ⇒ 停工后清洗中和"),

    dict(section="1.10", name="氢氟酸 + 镍基/铜镍合金（Monel 类）",
         when=lambda c: re.search(r"氢氟酸|氟化氢|hydrofluoric|\bHF\b|氟化物", _media_text(c), re.I)
                        and ({"nickel_alloy", "copper"} & mat_families(c.get("material", ""))),
         verdict="**可能**命中：Monel 400 冷作态/焊态对 SCC 敏感（退火态敏感度更低）",
         source="gate-04 §1.10（asm-v13 p.738）：Monel 400 最广用，**但冷作态/焊态对 SCC 敏感**；"
                "**HF 浓度/温度门槛源未给**（另注 roberge p.684）",
         action="⚠️ 门槛缺失 ⇒ 须核手册原文。措施：**用退火态或消应力态**；**热消应力 ≥540 ℃ + 缓冷**；"
                "隔绝氧；停工后清洗中和",
         need_verify=True),

    # ---------------- §1.12 氢氰酸/酸性氰化物（本轮新增）
    dict(section="1.12", name="氢氰酸 / 酸性氰化物 + 碳钢",
         when=lambda c: re.search(r"氰化物|氢氰酸|氰化|HCN|cyanide", _media_text(c), re.I)
                        and ({"carbon_steel", "low_alloy"} & mat_families(c.get("material", ""))),
         verdict="**可能**命中：酸性氰化物 + 碳钢（**穿晶型** SCC / 氢鼓泡）",
         source="gate-04 §1.12（asm-v13 p.735/736）：酸性氰化物水溶液是碳钢 SCC 经典环境；"
                "温酸性氰化物中为**穿晶型**（热氢氧化物/硝酸盐为晶间型）；炼厂**废酸水回炼 → 回流罐 HCN 累积**",
         action="措施：**废酸水直接送污水处理，不得回炼回流罐**；**注水洗涤**；缓蚀剂（氰化物仍在亦有效）；"
                "**消应力 ≥650 ℃**。监测：**氢活性探针 + 冷凝水化学分析**。"
                "⚠️ 浓度/温度门槛**源未给**，须回查标准",
         need_verify=True),

    # ---------------- §1.13 液态金属脆化（本轮新增）
    dict(section="1.13", name="液态金属脆化（LME）——**锌**",
         when=lambda c: re.search(r"镀锌|锌|galvaniz|\bzinc\b", _case_text(c), re.I)
                        and _tmax(c) is not None
                        and ((({"austenitic_ss", "nickel_alloy"} & mat_families(c.get("material", "")))
                              and _tmax(c) >= 419)
                             or (({"carbon_steel", "low_alloy"} & mat_families(c.get("material", "")))
                                 and _tmax(c) >= 370)),
         verdict="命中：锌致液态金属脆化（LME）温区",
         source="gate-04 §1.13（asm-v13 p.755/3224）：**碳钢 >370 ℃（700 ℉）长时间**；"
                "**奥氏体不锈钢/镍基：熔锌即裂**（锌熔点 419.5 ℃），**与镀锌钢焊接「几乎立即」开裂**；"
                "螺栓配**镀锌螺母**为实证",
         action="措施：**源头避免锌污染**——不锈钢周边**不用镀锌件**；富锌涂料**优先车间预涂**，"
                "现场涂装须在**焊接及保温完成后**；已污染件打磨后**酸洗（5%~10% 硝酸/磷酸/硫酸）+ 水洗，"
                "禁用盐酸**。⚠️ **LME 一般不算腐蚀** ⇒ 断口须查（被液态金属覆盖、脆性沿晶、裂纹内富锌析出物），"
                "**腐蚀速率表与本闸门②均查不出**"),

    # ---------------- §1.15 碳酸盐 SCC（GB/T 30579 §6.2，2026-10-10 增）
    dict(section="1.15", name="碳酸盐应力腐蚀开裂（碳酸盐/CO₂ + 碳钢/低合金钢）",
         when=lambda c: re.search(r"碳酸[盐钠钾]|\bCO2\b|二氧化碳|carbonate", _media_text(c), re.I)
                       and ({"carbon_steel", "low_alloy"} & mat_families(c.get("material", ""))),
         verdict="**可能**命中：碳酸盐 SCC 环境（碳钢/低合金钢敏感）",
         source="gate-04 §1.15（GB/T 30579-2022 §6.2.4，物理 P0051/正文 45）：**四组条件任一即可能发生**——"
                "① **pH>9.0 且 CO₃²⁻>100×10⁻⁶**；② **pH 8.0~9.0 且 CO₃²⁻>400×10⁻⁶**；③ **CO₂>2%（质量）且 T>93 ℃**；"
                "④ **H₂S≥50×10⁻⁶ 且 pH≥7.6**；物料含**氰化物**时敏感性升高",
         action="⚠️ 输入契约无结构化 pH/CO₃²⁻ 字段 ⇒ 本引擎**不代判具体门槛**，须按上列四组条件人工核对（任一命中即否决）。"
                "措施：整体 300系不锈钢或复合板（§6.2.3/6.2.6 c）；控制酸性水 pH 与 CO₃²⁻。"
                "⚠️ **在线腐蚀监测无意义**（工况微变可致偶然快速开裂）⇒ 只能定期化验酸性水 pH/CO₃²⁻（§6.2.7 a）",
         need_verify=True),

    # ---------------- §1.16 高温水 SCC（GB/T 30579 §6.11，2026-10-10 增）
    dict(section="1.16", name="高温水应力腐蚀开裂（>300 ℃ 水环境，300系/镍基）",
         when=lambda c: re.search(r"高温水|锅炉水|给水|蒸汽|水蒸气|\bwater\b|\bsteam\b", _media_text(c), re.I)
                       and ({"austenitic_ss", "nickel_alloy"} & mat_families(c.get("material", "")))
                       and (_tmax(c) is not None and _tmax(c) > 300),
         verdict="**可能**命中：高温水 SCC 定义区（GB/T 30579：>300 ℃ 的水环境，300系不锈钢/镍基合金敏感）",
         source="gate-04 §1.16（GB/T 30579-2022 §6.11.1/6.11.3，物理 P0062~63/正文 56~57）：高温水定义 **>300 ℃**；"
                "受影响材料=300系不锈钢、镍基合金",
         action="措施：水化学控制——**中和至 pH≈7.0** 可降敏感性（§6.11.6 b）；控氯/氧。"
                "⚠️ 同一工况若含 Cl⁻ 须另过 §1.1 氯化物判据（两体系可叠加）",
         need_verify=True),

    # ---------------- §1.17 乙醇 SCC（GB/T 30579 §6.14，2026-10-10 增）
    dict(section="1.17", name="乙醇应力腐蚀开裂（乙醇燃料 + 碳钢）",
         when=lambda c: re.search(r"乙醇|酒精|ethanol|燃料乙醇", _media_text(c), re.I)
                       and ({"carbon_steel", "low_alloy"} & mat_families(c.get("material", ""))),
         verdict="**可能**命中：乙醇 SCC 环境（碳钢敏感；乙醇/汽油混合物低至 20%（体积）即可开裂）",
         source="gate-04 §1.17（GB/T 30579-2022 §6.14.4，物理 P0066/正文 60）：**含水 0.1%~4.5%（体积）区间敏感性最大**；"
                "**完全密闭环境通常不发生**（通风/通氧均可引起）",
         action="⚠️ 含水量窗口与密闭状态须人工核对（契约无体积分数字段）。措施：完全密闭（隔氧）；"
                "含水量控制避开 0.1%~4.5% 敏感窗。车用乙醇汽油储运碳钢设施为本模式典型场景",
         need_verify=True),

    # ---------------- §1.18 硫酸盐 SCC（GB/T 30579 §6.15，2026-10-10 增）
    dict(section="1.18", name="硫酸盐应力腐蚀开裂（硫酸盐溶液 + 铜合金）",
         when=lambda c: re.search(r"硫酸盐|sulfate|sulphate", _media_text(c), re.I)
                       and ("copper" in mat_families(c.get("material", "")))
                       and ("nickel_alloy" not in mat_families(c.get("material", ""))),
         verdict="命中：硫酸盐 SCC 环境（铜合金敏感，**海军黄铜尤为明显**；**Cu90Ni10/Cu70Ni30 比较耐**）",
         source="gate-04 §1.18（GB/T 30579-2022 §6.15.3/6.15.4，物理 P0067/正文 61）：开裂潜伏**可长达 10~15 年**才现管束泄漏",
         action="措施：选 **Cu90Ni10/Cu70Ni30** 白铜替代敏感黄铜；敏感铜合金管束**定期清洗（每 5 年）**（§6.15.6 a）。"
                "⚠️ 长潜伏期 ⇒ **不能以「多年未漏」当作无损伤证据**",
         ),

    # ---------------- §1.19 锆与铪的 SCC 黑名单（2026-10-10 P0-2 增）
    dict(section="1.19", name="锆/铪 SCC 黑名单（FeCl₃·CuCl₂／甲醇+卤素／浓 HNO₃／液态汞·铯）",
         when=lambda c: ({"zirconium", "hafnium"} & mat_families(c.get("material", "")))
                        and (re.search(r"氯化铁|三氯化铁|FeCl3|FeCl₃|氯化铜|CuCl2|CuCl₂|ferric\s*chloride|cupric\s*chloride",
                                       _media_text(c), re.I)
                             or re.search(r"甲醇|methanol", _media_text(c), re.I)
                             or re.search(r"汞|铯|mercury|cesium", _media_text(c), re.I)
                             or (re.search(r"硝酸|nitric", _media_text(c), re.I)
                                 and float((c["media"].get("concentration") or {}).get("value", 0) or 0) > 70)),
         verdict="命中：锆/铪的 SCC 黑名单介质（环境开裂）",
         source="ASM Vol.13〈锆与铪〉(1987) p1865：**SCC 黑名单 5 类**——FeCl₃/CuCl₂ 溶液／甲醇+HCl 或甲醇+碘混合物／"
                "浓 HNO₃（>70%）／液态汞或铯。⭐**白名单（不裂）**：NaCl、HCl、MgCl₂、NaOH、H₂S"
                "（46% MgCl₂ 沸腾 U 弯不失效——不锈钢在同一介质中开裂）",
         action="换材或改工况（改环境/避免高持续拉应力/织构控制/保持表面膜/电化学保护五项）。"
                "⚠️ **浓 HNO₃ 的界限是 >70%**——本规则按浓度值判断，**未给浓度则不触发**（须人工核）；"
                "⚠️ 甲醇条目须确认是否含卤素/碘（无卤素时可人工推翻并留证）",
         ),

    # ---------------- §1.20 钛及钛合金的 SCC（卤代烃）（2026-10-10 P0-2 增）
    # ⚠️ 只收「介质侧已确认致害」的卤代烃族。**熔盐/热盐刻意不设为触发条件**——ASM 明示热盐开裂
    #    「限于实验室、至今无现场失效归因」⇒ 设成命中会造噪声（工程可豁免，见 §1.20 表）。
    #    status 有意为 🟠（need_verify）：本体系的真门槛是**合金成分/组织**（Al≥5%、O 0.20~0.25%、Sn），
    #    引擎无从获知 ⇒ **命中即"须人工核成分"，不代替工程师给最终结论**。
    dict(section="1.20", name="钛的 SCC：卤代烃（含 Freon）",
         when=lambda c: ("titanium" in mat_families(c.get("material", "")))
                        and re.search(r"四氯化碳|四氯甲烷|CCl4|二氯甲烷|二碘甲烷|三氯乙烯|四氯乙烯|氯仿|三氯甲烷|"
                                      r"三氯氟|八氟环丁烷|[Ff]reon|carbon\s*tetrachloride|methylene\s*chloride|"
                                      r"trichloroethylene|chloroform",
                                      _media_text(c), re.I),
         verdict="命中：钛合金在**卤代烃**中的 SCC 风险（含 Freon 族）",
         source="ASM Vol.13〈钛及钛合金〉(1987) p1756~1757：已确认致 SCC 清单——**四氯化碳、二氯甲烷、二碘甲烷、"
                "三氯乙烯、三氯氟甲烷、三氯氟乙烷、八氟环丁烷**；多数须**预裂纹试样**才能暴露；"
                "**CCl₄ 中裂纹速度约为甲醇中的 10 倍**；受累合金集中于 **Ti-8Al-1Mo-1V 与 Ti-5Al-2.5Sn**，"
                "STA 态 Ti-6Al-4V 对 Freon 敏感；⚠️**商业纯钛在常见烃类中未做过试验**（源内明示的数据缺口）",
         action="⚠️ **必须追问牌号与热处理状态**（本体系真门槛＝合金成分/组织）：**水溶液 SCC 需 Al ≥5%**、"
                "**Ti-O 临界氧 0.20~0.25%**（＝**ASTM Gr.2 与 Gr.3 的分界**）、**加 Sn 降抗性**、**Mo 一般有利**；"
                "**商业纯钛（Gr.1~4）在多数 SCC 体系最安全**（但纯钛在卤代烃**无试验数据**，不得据「CP 安全」外推）。"
                "完整冶金判据与热盐/熔盐窗（**热盐 285~425 ℃，且至今无现场失效＝工程可豁免**）见 gate-04 §1.20",
         need_verify=True),
]

# ============================================================ gate-04 十七体系「处置声明」总表
# ⚠️ 这张表是**缺口的机器可查面**：`scripts/check_rule_coverage.py` 会拿它去对账
#    `references/gate-04-scc.md` 的 `### 1.N` 小节，任一侧多出/缺失即 FAIL。
#    目的：让「references 写了、引擎没编码」这类缺口**无法再静默存在**。
#    （§1.15~§1.18 为 2026-10-10 增：GB/T 30579-2022 §6 折叠轮新增四体系）
GATE04_SYSTEMS = {
    "1.1":  "氯化物应力腐蚀开裂（Cl-SCC，奥氏体不锈钢）",
    "1.2":  "碱脆（碱液 + 碳钢，caustic cracking）",
    "1.3":  "硝脆（硝酸盐 + 低碳钢，nitrate cracking）",
    "1.4":  "液氨 + 碳钢/低合金钢（无水氨 SCC）",
    "1.5":  "湿 H₂S（硫化物应力开裂 SSC）",
    "1.6":  "氨 + 铜及铜合金（氨脆 / 季裂）",
    "1.7":  "氢脆 / 氢致开裂（含高强度螺栓）",
    "1.8":  "CO₂ 腐蚀（含「它到底算不算 SCC」的边界）",
    "1.9":  "胺液 + 碳钢（amine SCC，碱性 SCC 族）",
    "1.10": "氢氟酸（HF）",
    "1.11": "连多硫酸 + 奥氏体不锈钢（polythionic acid SCC，停工型）",
    "1.12": "氢氰酸致气孔/应力开裂（酸性氰化物 + 炼厂 HCN 富集）",
    "1.13": "液态金属脆化（LME / 液态金属致脆）",
    "1.14": "扩展 SCC 体系清单（《腐蚀数据与选材手册》1995 附录二，A− 待核原图）",
    "1.15": "碳酸盐应力腐蚀开裂（碳酸盐/CO₂ + 碳钢/低合金钢，GB/T 30579 §6.2）",
    "1.16": "高温水应力腐蚀开裂（>300 ℃ 水环境，300系/镍基，GB/T 30579 §6.11）",
    "1.17": "乙醇应力腐蚀开裂（乙醇燃料 + 碳钢，GB/T 30579 §6.14）",
    "1.18": "硫酸盐应力腐蚀开裂（硫酸盐溶液 + 铜合金，GB/T 30579 §6.15）",
    "1.19": "锆与铪：SCC 白/黑名单与点蚀判据（ASM Vol.13〈锆与铪〉1987，p1860~1871）",
    "1.20": "钛及钛合金的 SCC 与特殊介质（ASM Vol.13〈钛及钛合金〉1987，p1755~1787）",
}

# **刻意不设为「运行工况规则」**的两条（设了会造"假否决"）——理由必须写清，否则后人会当漏项补上。
NOT_A_RULE = {
    "1.8": "⚠️ §1.8 源内**明示 CO₂ 不是 SCC 体系**（首要机制是均匀/台地状金属损失，防蚀靠 FeCO₃ 垢层）"
           "⇒ **本闸不设为规则**（设为 SCC 规则即造**假 🔴**）。其可用判据是**切换逻辑**"
           "「CO₂/H₂S 分压比 >500 以 H₂S 主导」，已并入 §1.5 规则的 action；**本体腐蚀转闸门⑤**（§5 系列）。",
    # ⚠️ §1.11 也「刻意不设为运行工况规则」，但它的**声明落在 SHUTDOWN_NOTES**（那里同时给出了处置措施）
    #    —— 一个体系**只在一处声明**，避免两处漂移（本轮负控 3 即因两处都声明而检不出"漏声明"）。
    # §1.14（2026-10-09 增）：扩展 SCC 体系清单（《腐蚀数据与选材手册》1995 附录二 p1298~1299）
    #    ⇒ **OCR A−、化学式讹误率高 ⇒ 只作扩展线索，逐条核原图后才定档**；故不设为规则。
    "1.14": "⚠️ §1.14 是「扩展体系线索表」（Monel/因科耐尔高温碱/20合金/钛红发烟硝酸·甲醇/铝/镁/锆 等），"
            "源为 OCR A−（化学式讹误多）⇒ **核原图（原书 p1298~1299）后才可升级为规则**；"
            "在此之前不得据其下判，只可作「须人工核对的体系清单」。",
}

# 停工窗口类风险（**不计入运行工况判定**，只作提醒输出）
SHUTDOWN_NOTES = [
    dict(section="1.11", name="连多硫酸 SCC（停工窗口）",
         when=lambda c: ("austenitic_ss" in mat_families(c.get("material", "")))
                        and re.search(r"硫化物|H2S|硫化氢|sour|含硫", _media_text(c), re.I),
         note="⚠️ **停工窗口风险（普通工况不发生）**：硫化物垢 + 停工期间氧 + 水 → 连多硫酸 ⇒ "
              "**未稳定化奥氏体不锈钢（304）焊缝邻接区**晶间 SCC（加氢/加氢裂化/催化裂化/火炬系统高发）。"
              "**开停工方案须单列 SCC 防护步骤**：按 NACE RP-01-70 **氮气吹扫**／**干空气露点 < −15 ℃**／"
              "**2% 纯碱水中和**（试压亦用，临时存放留残液）；敏感性试验按 **ASTM G 35**。"
              "⚠️ 破坏速率极快：源记「**12 mm 壁厚 8 h 被穿透**」（gate-04 §1.11，asm-v13 p.3213/3215/613）"),
]

def _gate4_coverage():
    """把「引擎已编码 vs 刻意不设为规则」摆到台面上 —— 让缺口**在运行时可被看见**。

    判据句：**「references 里有」≠「引擎会用」**；缺口必须**在输出里可见**，
    否则它会一直静默到下一次真实案例把它撞出来（本 skill 已在 NaOH 案例上吃过一次）。
    """
    encoded = sorted({r["section"] for r in SCC_RULES})
    shut = {n["section"] for n in SHUTDOWN_NOTES}
    declared = set(encoded) | set(NOT_A_RULE) | shut
    return {
        "gate-04 体系总数": len(GATE04_SYSTEMS),
        "已编码为规则": {s: GATE04_SYSTEMS.get(s, "?") for s in encoded},
        "规则条数": len(SCC_RULES),
        "刻意不设为运行工况规则": NOT_A_RULE,
        "停工窗口提醒条数": len(SHUTDOWN_NOTES),
        # 闭合式：编码 ∪ 不设 ∪ 停工 = 体系总数（不等即说明有体系未处置）
        "声明闭合式": "编码 %d + 不设 %d + 停工 %d = %d（体系总数 %d）%s"
                      % (len(encoded), len(NOT_A_RULE), len(shut), len(declared),
                         len(GATE04_SYSTEMS), "" if len(declared) == len(GATE04_SYSTEMS) else "  ⚠️ 不闭合"),
        "机检": "scripts/check_rule_coverage.py（对账本覆盖表 ↔ references/gate-04-scc.md）",
    }


def gate4_scc(case, material):
    c = dict(case); c["material"] = material
    fam = mat_families(material)
    hits = []
    need = False
    shutdown = []
    for n in SHUTDOWN_NOTES:
        try:
            if n["when"](c):
                shutdown.append({"体系": n["name"], "提醒": n["note"]})
        except Exception:
            pass
    if not fam:
        return ORANGE, {"说明": f"材料 {material!r} **未归一到任何材料族**（MAT_FAMILY 无命中）",
                        "动作": "补 MAT_FAMILY 别名，或人工比对 gate-04-scc.md 全表",
                        "停工窗口提醒": shutdown,
                        "覆盖声明": _gate4_coverage(),
                        "判据句": "**未归一 ≠ 无风险**；此处出 🟠 而非 ✅（fail-closed）"}
    for r in SCC_RULES:
        try:
            if r["when"](c):
                hits.append({"体系": r["name"], "§": r.get("section", "?"), "结论": r["verdict"],
                             "出处": r["source"], "动作": r["action"]})
                if r.get("need_verify") or "不给结论" in r["action"] or "不代判" in r["action"]:
                    need = True
        except Exception as e:
            hits.append({"体系": r["name"], "结论": "规则求值异常", "错误": str(e)})
    if not hits:
        return OK, {"命中数": 0, "材料族": sorted(fam),
                    "说明": "本引擎内置规则未命中；**不等于无 SCC 风险**——须人工比对 gate-04-scc.md 全表",
                    "停工窗口提醒": shutdown,
                    "覆盖声明": _gate4_coverage()}
    return (ORANGE if need else RED), {"命中数": len(hits), "材料族": sorted(fam), "命中": hits,
            "停工窗口提醒": shutdown,
            "覆盖声明": _gate4_coverage(),
            "判据句": "任一体系命中即否决；温度区间不重叠的开裂体系不能互相顶替"}

# ============================================================ 闸门⑤⑥ 腐蚀数据# ⚠️ 2026-10-09 真实案例测试②抓出：L1（Alleima）用**英文名**，用户写**中文** ⇒ 133 行数据被
#   **静默跳过**、只剩 L1b 兜底（L1b 是人工汇编，可信度更低）。这是"静默降级"，最危险。
#   修法：给常见介质建**中→英桥**（覆盖 L1b 表的 26 个中文名，便于与 L1 对接）。
CN2EN = {
    "氨水": "Ammonium hydroxide",
    "氢氧化钠": "Sodium hydroxide",
    "氢氧化钾": "Potassium hydroxide",
    "硫酸": "Sulphuric acid",
    "盐酸": "Hydrochloric acid",
    "硝酸": "Nitric acid",
    "磷酸": "Phosphoric acid",
    "氢氟酸": "Hydrofluoric acid",
    "冰醋酸": "Acetic acid",
    "醋酸": "Acetic acid",
    "甲酸": "Formic acid",
    "次氯酸钠": "Sodium hypochlorite",
    "双氧水": "Hydrogen peroxide",
    "过氧化氢": "Hydrogen peroxide",
    "氯化钙盐水": "Calcium chloride",
    "丙酮": "Acetone",
    "甲苯": "Toluene",
    "二甲苯": "Xylene",
    "二氯甲烷": "Methylene chloride",
    "四氯化碳": "Carbon tetrachloride",
    "汽油": "Petrol",
    "氯气": "Chlorine",
    "二氧化硫": "Sulphur dioxide",
    "碳酸钠": "Sodium carbonate",
    # 2026-10-10 硫章轮新增四桥（目标 Sulphur 为主库**精确化学品名**，30 行实证：
    # Molten 240 / Molten 445=BP / Vapour 570 三档；经 check_cn2en_bridges.py 普查通过）：
    "硫": "Sulphur",
    "硫磺": "Sulphur",
    "液硫": "Sulphur",
    "硫蒸气": "Sulphur",
    # ⚠️ 2026-10-10 撤回三条无效桥（盐水/氯化钠/食盐水 → "Sodium chloride"）：
    #    自证时 grep 命中的 338 行**全是组合化学品**（"Acetic acid + sodium chloride"、
    #    "Hydrochloric acid + sodium chloride" …），主库**无** "Sodium chloride" 独立行
    #    （365 个化学品名逐个核对，见 ch14 折叠轮验证记录）。
    #    教训：**"含该子串的行数" ≠ "该化学品存在"**——桥的落点必须是精确化学品名。
    #    盐水/海水体系的判据走 gate-05-06 §5.6 ＋ L1b（L1b 有「氯化钠盐水」行）。
}


ALIAS = [
    (r"^carbon\s*steel$", "Carbon steel"),
    (r"^13\s*%?\s*cr(-steel)?$", "13 Cr"),
    (r"^ti$|^titanium\s*\(\s*co?\s*p\s*ti\s*\)?$|^titanium\s*cp\s*ti\)?$", "Titanium (CP Ti)"),
    (r"^2rk65.*$", "Alleima® 2RK65 ('904L')"),
    (r"^18-?13-?3$", "18Cr13Ni3Mo 1)"),
    (r"^17-?14-?4$", "17Cr14Ni4Mo 2)"),
    (r"^18-?2$", "Alleima® 1802"),
]
RATING = {"0": "< 0.1 mm/a（轻微）", "1": "0.1–1.0 mm/a（中等）", "2": "> 1.0 mm/a（严重）"}
SUFFIX = {"p": "点蚀风险", "P": "点蚀**严重**风险", "c": "缝隙腐蚀风险", "C": "缝隙腐蚀**严重**风险",
          "s": "应力腐蚀开裂风险", "S": "应力腐蚀开裂**严重**风险", "ND": "无数据"}

def canon_material(name):
    n = str(name).strip()
    for pat, canon in ALIAS:
        if re.match(pat, n, re.I):
            return canon
    return n

def parse_cond(cond):
    """解析 'Conc. X%=v | Temp. °C=t' → dict。含 BP/20-BP 等符号温度。"""
    out = {"raw": cond, "temp": None, "conc": None, "temp_symbolic": None}
    for part in str(cond).split("|"):
        part = part.strip()
        m = re.search(r"Temp\.?\s*°?C\s*=\s*(.+)$", part, re.I)
        if m:
            v = m.group(1).strip()
            if re.fullmatch(r"-?\d+(\.\d+)?", v):
                out["temp"] = float(v)
            else:
                out["temp_symbolic"] = v
            continue
        m = re.search(r"%\s*=\s*(.+)$", part)
        if m:
            out["conc"] = m.group(1).strip()
    return out

def load_alleima(root):
    for cand in ("Alleima腐蚀数据_master/alleima腐蚀数据_master.csv",
                 "alleima腐蚀数据_master.csv"):
        p = os.path.join(root, cand)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8-sig", newline="") as f:
                return list(csv.DictReader(f)), p
    return None, None

# ============================================================ 闸门⑤⑥ L1b 兜底（非金属）
# L1b = 「化学品选材相容性矩阵」：27 化学品 × 20 材质，A/B/C/D 四档，**人工汇编**。
# 定位：L1（Alleima，仅金属）无覆盖时（尤其**非金属**）的兜底 ＋ 常驻交叉校核。
# ⚠️ **可信度低于 L1**（人工汇编；其自述来源为 Cole-Parmer / Bürkle / HFIPI / Eurofluor 等），
#    用它出的结论**必须标注来源等级**。
L1B_FILE = "化学品选材相容性矩阵.xlsx"
L1B_ALIAS = [
    (r"carbon\s*steel|碳钢|Q235|Q345|20#", "碳钢"),   # 2026-10-10 增英文写法（用户可能输入 "Carbon steel"）
    (r"^304",                       "304"),
    (r"^316L",                      "316L"),
    (r"^316",                       "316"),
    (r"Hastelloy|C-?276|哈氏",      "Hastelloy"),
    (r"钛|TA2|Ti\b",                "钛"),
    (r"PVC",                        "PVC"),
    (r"CPVC",                       "CPVC"),
    (r"^PP\b|聚丙烯",               "PP"),
    (r"HDPE",                       "HDPE"),
    (r"PTFE|聚四氟",                "PTFE"),
    (r"PVDF|聚偏氟",                "PVDF"),
    (r"FRP.*乙烯基|乙烯基酯",        "FRP(乙烯基酯)"),
    (r"FRP.*环氧|环氧树脂",          "FRP(环氧)"),
    (r"NBR|丁腈",                   "NBR"),
    (r"EPDM|三元乙丙",              "EPDM"),
    (r"^CR\b|氯丁",                 "CR"),
    (r"FKM|氟橡胶",                 "FKM"),
    (r"FFKM|全氟醚",                "FFKM"),
]


def lookup_l1b(root, chemical, material):
    """查 L1b。返回 dict 或 None。**不猜**——匹配不上就 None。"""
    p = os.path.join(root, L1B_FILE)
    if not os.path.exists(p):
        return None
    try:
        import openpyxl
        wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
        ws = wb["选材矩阵"]
        rows = list(ws.iter_rows(values_only=True))
        wb.close()
    except Exception as e:
        return {"error": "L1b 读取失败：%s" % e}
    if len(rows) < 5:
        return None
    # 表头：第 4 行（0-based 3）为材料名；第 3 行（0-based 2）为分组
    mat_row = rows[3]
    cols = {}
    for ci, cell in enumerate(mat_row):
        if cell:
            cols[ci] = str(cell).replace("\n", " ").strip()
    # 材料列匹配（先按别名表取关键词）
    want = None
    for pat, key in L1B_ALIAS:
        if re.search(pat, str(material), re.I):
            want = key
            break
    col = None
    if want:
        for ci, nm in cols.items():
            if want.lower() in nm.lower():
                col = ci
                break
    # 化学品行匹配：先精确、再子串（表里是中文名）
    chem = str(chemical).strip()
    hit = None
    for r in rows[4:]:
        if r and r[0] and str(r[0]).strip() == chem:
            hit = r
            break
    if hit is None and len(chem) >= 2:
        # ⚠️ 2026-10-10 硫章轮加防：**单字介质名禁走子串**——
        # 「硫」会子串命中「硫酸」（错行→错评级→结论翻转，ch15 轮实测）；
        # 「氨/盐/氯/水」同理。两字以上保留（盐水→氯化钠盐水、
        # 醋酸→冰醋酸/醋酸 为设计行为，见 ch14 验证记录）。
        for r in rows[4:]:
            if r and r[0] and chem in str(r[0]):
                hit = r
                break
    if hit is None:
        return {"说明": "L1b 无该化学品行（表内为中文名，共 27 种）", "化学品": chem}
    if col is None:
        return {"说明": "L1b 无该材质列", "材质": material,
                "可选材料列": list(cols.values())}
    grade = hit[col] if col < len(hit) else None
    note = hit[-1] if hit else None
    return {"来源": "L1b 化学品选材相容性矩阵（**人工汇编，可信度低于 L1**）",
            "化学品": hit[0], "浓度档": hit[1] if len(hit) > 1 else None,
            "材质列": cols.get(col), "评级": grade,
            "口径": "A=优 / B=良 / C=可 / D=不可（默认常温常压低流速）",
            "备注": note}


# ============================================================ 闸门⑤⑥ L1c 页锚索引（手册层）
# L1c = 《腐蚀数据与选材手册》(左景伊/左禹，化学工业出版社 1995) 的**页锚索引**：
#       只登记「哪一合金的数据表覆盖哪些介质、在哪一页」，**不含评级数值**——
#       原书为符号表（优良<0.05 / 良好 0.05~0.5 / 可用 0.5~1.5 / 不适用>1.5 mm/y ＋孔蚀/晶间/SCC 符号），
#       OCR 后符号变形 ⇒ 逐格提取不可靠、也不做（**数据本体留原书**）。
# 定位：L1/L1b 都未命中时的**有向指针**——把「死 🟠（无覆盖）」变成「查哪一页原图」的行动指令。
# ⚠️ **1995 年版**：数据与所引标准有时效性，凡引用必须标注版本。
# ⚠️ 文件在 --data-root（库外，与 L1/L1b 同目录）；**无此文件 ⇒ 本层静默跳过**（fail-closed 语义不变）。
L1C_FILE = "腐蚀数据与选材手册_页锚索引.csv"


def load_l1c(root):
    p = os.path.join(root, L1C_FILE)
    if not os.path.exists(p):
        return None
    try:
        with open(p, "r", encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))
    except Exception as e:
        return {"error": "L1c 读取失败：%s" % e}


def _chem_cn_aliases(chem):
    """介质的中文名候选：原名 ＋ CN2EN 反查（英文输入 → 原书中文名）。"""
    base = str(chem).strip()
    cands = [base]
    for cn, en in CN2EN.items():
        if base and base.lower() == en.lower():
            cands.append(cn)
    return [c for c in cands if c]


def lookup_l1c(root, chemical, material):
    """查 L1c 页锚索引。返回 dict 或 None（无文件/无命中都 None——不猜）。"""
    rows = load_l1c(root)
    if not rows or isinstance(rows, dict):
        return None
    fams = mat_families(material)
    if not fams:
        return None
    hits = []
    for r in rows:
        if (r.get("材料族") or "") not in fams:
            continue
        media = (r.get("介质清单摘要") or "")
        if not media:
            continue
        # ⚠️ 2026-10-10 硫章轮改判据：**token 级匹配，不做子串**——
        # 「硫」按子串会命中「硫酸/亚硫酸/硫化钠/二氧化硫」等化合物行
        # （ch15 轮实测假命中 4 张镍系表），与 ch14「桥有效性」同族：
        # 含该子串 ≠ 该化学品在表内。摘要为 | 分隔的介质名清单。
        toks = {t.strip() for t in media.split("|") if t.strip()}
        for t in list(toks):
            m = re.match(r"^(.*?)[（(]([^()]*)[）)]$", t)  # 「醋酸(乙酸)」类括注别名
            if m:
                toks.add(m.group(1).strip())
                for al in re.split(r"[/／]", m.group(2)):
                    if al.strip():
                        toks.add(al.strip())
        for c in _chem_cn_aliases(chemical):
            if c and c in toks:
                hits.append(r)
                break
    if not hits:
        return None
    return {"来源": "L1c《腐蚀数据与选材手册》(1995) 页锚索引——**仅登记覆盖位置，不含评级数值**",
            "命中数": len(hits),
            "条目": [{"材料族": h.get("材料族"), "原书名": h.get("材料名(原书)"),
                      "章节": h.get("章节号"), "表号": h.get("表号"),
                      "页锚": "正文 p%s~%s（物理 p%s~%s）" % (h.get("正文页起"), h.get("正文页止"),
                                                             h.get("物理页起"), h.get("物理页止")),
                      "介质覆盖": h.get("介质清单摘要"),
                      "判据要点": h.get("判据要点"),
                      "置信度": h.get("置信度", "A−")} for h in hits[:6]],
            "动作": "**查原书对应页的符号评级表**（库外原书/原图）；⚠️ 1995 年版数据须评估时效",
            "判据句": "L1c 命中 ≠ 有评级可用——它只是「书里这几页覆盖了这组介质×材料」的路标"}


# ============================================================ 闸门⑤⑥ 材料×介质热工况禁忌（硬否决，先于数据查询）
# ⚠️ 2026-10-10 验证轮新增（45% NaOH/220 ℃ 真实用例抓出）：L1/L1b 是**常温/低还口径的归纳评级，
#    不含温度边界**——L1b 给「钛 TA2 × 氢氧化钠」A 级，而 ASM Vol.13〈钛腐蚀〉专章明示
#    α 钛 **T>80 ℃ 且 pH≥12 即可能过度吸氢 → 氢化钛 → 氢脆**。数据源 A 级掩盖了热工况禁忌。
#    判据句：**数据源的评级不是"全工况通行证"——热工况禁忌对数据源评级有否决权**。
#    结构可扩展：新禁忌对按 (材料族, 介质正则, 温度门槛℃, 机理, 出处) 追加，引擎输出自动带判据。
CONTRAINDICATIONS = [
    # ① 钛 × 热浓碱（2026-10-10 验证轮，45% NaOH/220 ℃ 用例抓出）
    ("titanium", r"氢氧化钠|NaOH|氢氧化钾|KOH|烧碱|苛性钠|苛性钾", 80.0,
     "热浓碱吸氢→氢化钛→氢脆；且热浓苛性碱中腐蚀可跳档（表17：40% NaOH/66 ℃ 0.038 mm/a，73% NaOH 沸腾 0.13 mm/a，KOH 50% 沸腾 2.7 mm/a）",
     "ASM Handbook Vol.13〈Corrosion of Titanium and Titanium Alloys〉Alkaline Media 节：**氢吸留与氢脆 T>80 ℃ 且 pH≥12 即可能**（本地 PDF p1730~1731）；同族机理见 gate-05-06 §5.3 钛氢化"),
    # ② 钛 × 氟化物/氢氟酸（P0-2 轮，ASM Vol.13 p1725）——**任意温度**（tlim=None）
    ("titanium", r"氢氟酸|氟化氢|HF|氟化物|氟离子|氟硅酸|F\s*[-⁻]|fluori", None,
     "F⁻ 与钛生成稳定可溶络合物 ⇒ **全浓度、全温度范围攻击**（区别于其他介质多可钝化）。⚠️缓解条件（须写明）："
     "①氧化剂（HNO₃）可减缓腐蚀并抑制吸氢；②稀酸氟化物中若存在**过量络合金属离子（Fe³⁺/Al³⁺/Cr⁶⁺）**亦可抑制；"
     "③**无这些离子时，>20 ppm F⁻ 且 pH<6~7 即可攻击**（定量门槛，p1725）",
     "ASM Vol.13〈钛及钛合金〉（1987）Acid 章 Hydrofluoric Acid 节，PDF p1725"),
    # ③ 钛 × 甲醇（SCC；含卤化物时最凶）——P0-2 轮
    ("titanium", r"甲醇|methanol", None,
     "**甲醇 ＋ 卤化物（Cl⁻/Br⁻）→ 工业纯钛与钛合金晶间 SCC**（曾致 Ti-6Al-4V 压力容器试压爆裂）。⭐反直觉三条："
     "①**微量水会加剧**（达临界水量前失效时间缩短；卤化物越高，临界水量越高）；②**超过临界水量才转为抑制**；"
     "③**阴极极化（<−250 mV vs Ag/AgCl，或 −1.5~−1.0 V vs SCE）可防裂**——与氢脆的阴极极化方向**相反**。"
     "⭐⭐**工程解法（源给定量）**：**绝对甲醇必须至少加 1.5% H₂O**（p1732）；"
     "⭐**完全无水的有机流股本身即禁忌**——ppm 级痕量水即足以维持保护膜，**完全无水会阻止氧化膜修复**（p1732）⇒ "
     "本条按保守侧（无水/低水）判；介质含水充足且无卤素时可人工推翻并留证",
     "ASM Vol.13〈钛及钛合金〉（1987）SCC 章 Methanol 节 p1732／p1752；触发清单见 p1701/p1732"),
    # ④ 钛 × 干氯/干溴（放热卤化反应；**湿氯气不在此列**——钛恰是湿氯气的标准材料）
    ("titanium", r"干氯|干溴|无水氯|无水溴|dry\s*chlorine|dry\s*bromine|anhydrous\s*chlorine", None,
     "**干（无水）氯气/溴气 → 与钛发生危险放热卤化反应**（薄氧化膜更易触发，厚热氧化膜反而阻滞）。"
     "⭐**定量分界（ASM 钛篇）**：**干氯 <0.5% H₂O 室温即反应**；**湿氯 >1.5% H₂O 在 200 ℃ 仍 nil** ⇒ "
     "**湿氯气中钛是标准用材**（水维持钝化膜）。⚠️**干/湿必须分清**：本条只对「干/无水（<0.5% H₂O）」触发——"
     "用户若仅写「氯气」而未说明干湿，本表**不触发**，但须按 `MEDIA_NOTES` 的氯气注人工确认干湿；"
     "同类：**干 HCl 气 25~100 ℃ nil**（干态可用）、**HF 仅 1%/26 ℃ 即 127 mm/a**（HF 与氯/HCl 方向完全相反）",
     "ASM Vol.13〈钛及钛合金〉（1987）Gases 节，PDF p1737／p1779／p1782／p1785"),
    # ⑤ 钛 × N₂O₄ / 红发烟硝酸 / 镉（SCC 触发介质）
    ("titanium", r"四氧化二氮|N2O4|红发烟硝酸|red\s*fuming|镉|cadmium", None,
     "**钛合金 SCC 触发介质（ASTM 硬禁忌四类之三）**：①**无水 N₂O₄**——可发生快速自燃反应；⭐⭐**解法：少量加水或 0.6~1.0 wt% 硝酸可有效抑制**（p1738）；"
     "②**发烟（红烟）硝酸**——商用纯钛**室温、含 20% NO₂ 即开裂**，**NO₂ 低至 6.5% 且 H₂O <0.7% 即发生**，光滑试样上即见晶间开裂；"
     "⭐**白烟（<约 2% H₂O）室温点燃敏感、红烟（>约 2% H₂O）不敏感**；⭐⭐**腐蚀率低 ≠ 安全**（白烟硝酸 160 ℃ 仅 <0.127 mm/a 却点燃敏感）；"
     "**配比禁忌：H₂O <1.4~2.0% 或 NO₂ >6% ⇒ 冲击敏感（pyrophoric）反应**（同族：本 skill 另据 1995 手册表注 759 记录「钛＋无水红发烟硝酸→着火爆炸」）；"
     "③**液态/固态镉接触**（室温即可开裂，远低于镉熔点）",
     "ASM Vol.13〈钛及钛合金〉（1987）p1701／p1714／p1738／p1750~1752／p1789；互证见《腐蚀数据与选材手册》1995 表注 759"),
    # ══════════ P0-2 轮：锆 / 铪 ══════════
    # ⑥ 锆 × 氟化物/氢氟酸（p1833 等）——**绝对禁忌**（不像钛那样有"络合可救"的常规通道）
    ("zirconium", r"氢氟酸|氟化氢|HF|氟化物|氟离子|氟硅酸|F\s*[-⁻]|fluori", None,
     "**锆的绝对禁忌**：HF 全浓度区间室温即 >1.3 mm/a（F⁻ 与锆络合）。F⁻ 只有在**被络合**后才可用锆——"
     "有效络合剂：SiO₂／Al(NO₃)₃／**锆海绵**／Zr(NO₃)₄·5H₂O／**P₂O₅**；⚠️**可容忍 F⁻ 上限源未给**，须按实际介质做试验。"
     "氟化物盐同族禁忌且**温度是开关**：NaF 饱和 90 ℃ >1.3；KF 50% 无水熔融 241~377 ℃ >1.3；AlF₃ 20% 室温即 >1.3",
     "ASM Vol.13〈锆与铪〉（1987）p1833／p1840／p1841／p1829／p1852；同族铪禁忌见 p1870"),
    # ⑦ 锆 × FeCl₃ / CuCl₂（p1831/p1861）——重金属离子+卤素共存是致害组合
    ("zirconium", r"氯化铁|三氯化铁|FeCl3|FeCl₃|氯化铜|CuCl2|CuCl₂|ferric\s*chloride|cupric\s*chloride", None,
     "**FeCl₃／CuCl₂ 硬禁忌**（除极稀/极低温）：0~50% 沸腾三合金均 >1.3 mm/a；**Cu²⁺ 比 Fe³⁺ 更有害**。"
     "机理：**单独 Cl⁻ 不改变锆的耐蚀性**（p1852），致害是**重金属离子＋卤素共存**——Fe³⁺/Cu²⁺ 把电位抬过点蚀电位；"
     "⭐**pH 是开关**：沸腾 NaCl＋500 ppm Cu²⁺ 在 **pH≥5 时未焊/焊件双双 nil**、pH≤4.8 才点蚀（p1861）；"
     "热处理（760/870 ℃）可显著减轻点蚀（p1862）",
     "ASM Vol.13〈锆与铪〉（1987）p1831／p1861／p1852／p1862"),
    # ⑧ 锆 × 王水（p1830/p1833/p1857）
    ("zirconium", r"王水|aqua\s*regia", None,
     "**王水禁忌（含稀释王水）**：王水 3:1 室温 >1.3 mm/a；20%HCl+20%HNO₃、10%HCl+10%HNO₃ 室温记 **\"Dissolved\"**（溶解）",
     "ASM Vol.13〈锆与铪〉（1987）p1830／p1833／p1857"),
    # ⑨ 锆 × 湿氯气（**干氯气可用**——与钛恰好相反！）
    ("zirconium", r"湿氯|氯水|chlorine\s*water|wet\s*chlorine", None,
     "**湿氯气禁忌**：Cl₂ 含水 >0.13% H₂O、94 ℃ → >1.3 mm/a；氯水饱和液 75 ℃ → >1.3。"
     "⭐**与钛恰好相反**：**干氯气下锆可用**（室温 <0.13 mm/a；正文口径「锆不与卤素反应至约 200 ℃」），"
     "而**钛是干氯气危险、湿氯气可用**（Ti 靠水维持钝化膜）⇒ **「氯气」二字在两族上的结论相反，且都取决于水含量**："
     "凡涉及氯气选材，**第一步先问干湿**。⚠️用户若仅写「氯气」未说明干湿，本表不触发（须人工确认）",
     "ASM Vol.13〈锆与铪〉（1987）p1830／p1831／p1862；钛侧见同书 p1737 与 `references/asm13-titanium.md`"),
    # ⑩ 锆 × 甲醇+卤素（SCC 黑名单）
    ("zirconium", r"甲醇|methanol", None,
     "**甲醇＋卤素/碘混合物禁忌（SCC）**——锆 SCC 黑名单之一（CH₃OH+HCl、CH₃OH+碘混合物）。"
     "⚠️本条按保守侧对「甲醇」一律触发；若经确认介质**既无卤素也无碘**且无水敏条件，可人工推翻并留证",
     "ASM Vol.13〈锆与铪〉（1987）p1865"),
    # ⑪ 锆 × 熔融锌/铋/镁 与 液态汞/铯（熔融金属攻击清单 + SCC）
    ("zirconium", r"(熔融|液态|molten|liquid)\s*(锌|铋|镁|zinc|bismuth|magnesium)|熔融金属", None,
     "**熔融金属攻击清单（封闭三项）：锌、铋、镁**；另**液态汞或铯引起 SCC**（SCC 黑名单）。"
     "反面（可用，均 <0.025 mm/a）：液态 Pb ≤600 ℃、Li ≤800 ℃、**Hg ≤100 ℃**、Na ≤600 ℃。"
     "⭐熔融金属腐蚀速率**受微量杂质（O/H/N）支配**，不能只看金属种类",
     "ASM Vol.13〈锆与铪〉（1987）p1863／p1865"),
    # ⑫ 铪 × HF / 浓硫酸 / 王水（p1870）
    ("hafnium", r"氢氟酸|氟化氢|HF|氟化物|氟离子|F\s*[-⁻]|fluori", None,
     "**铪的水溶液禁忌①：HF 与氟化物**——铪在 HF 中可溶；⭐**少量可溶性氟化盐即显著加剧其与其它酸的反应**"
     "（⇒ 与锆同族：F⁻ 是这两族的共同杀手）",
     "ASM Vol.13〈锆与铪〉（1987）Hafnium 节，PDF p1870"),
    ("hafnium", r"王水|aqua\s*regia", None,
     "**铪的水溶液禁忌②：王水**（王水可溶铪）——与锆同为禁忌",
     "ASM Vol.13〈锆与铪〉（1987）p1870"),
    ("hafnium", r"浓硫酸|发烟硫酸|concentrated\s*sul[fp]huric|fuming\s*sul[fp]huric", None,
     "**铪的水溶液禁忌③：浓硫酸**（铪在浓硫酸中可溶）。⚠️**仅对「浓/发烟」触发**——铪**耐稀 H₂SO₄ 与稀 HCl**、"
     "全浓度 HNO₃ 不受影响、亦很耐碱（这些是铪相对锆的优势面）",
     "ASM Vol.13〈锆与铪〉（1987）p1870"),
]

# ============================================================ 闸门⑤⑥ 介质判据注（L3 手册层，有向指引）
# 与 CONTRAINDICATIONS 的分工：那张表是**硬否决**（改状态）；本表是**有向指引**（不改状态，只把
# 「查哪本书哪一页、按哪条判据」直接附在输出里，让 🟠 从"死缺口"变成"可执行动作"）。
# ⚠️ 来源为 L3（版权手册）⇒ 输出必须标注来源等级与版本；判据只写结论+页锚，不抄正文。
# 条目形态：(介质正则, 文本, 适用材料族集合或 None) —— 第三项为 None 时对**所有材料**附加；
# 指定材料族时只对该族附加（避免把「钛的缝隙腐蚀须知」挂到每个查氯化物的人头上）。
MEDIA_NOTES = [
    (r"氢氧化钠|NaOH|氢氧化钾|KOH|烧碱|苛性钠|苛性钾",
     "**热浓碱体系**（ASM Vol.13〈镍与镍基合金〉1987，p1643/p1649/p1653；L3 手册层，引用核现行版）："
     "①基准材料＝**Nickel 200 / 201**——适用于全浓度、全温度的 NaOH/KOH，**包括熔融碱**；**>315 ℃ 换 Ni 201**（避石墨析出致脆）；"
     "②**耐碱均匀腐蚀与碱 SCC 抗力随镍含量升高而升高** ⇒ 碱工况优先高镍；"
     "③**镍不耐 NH₄OH（氨水）**；"
     "④碱蒸发器杂质放大器：**氯酸盐／次氯酸盐／氯化物 ＋ 流速** ⇒ 腐蚀率上升；"
     "⑤⚠️**碱 SCC 不止碳钢**——已记录：**C-276 在 NaOH 175 ℃**、600/800/690 在 325 ℃、722 在 50% NaOH 315 ℃、400 在 10% NaOH 300 ℃ "
     "⇒ **数据源的常温评级不得外推到 >~150 ℃**（该结论与 L1b「C-276×NaOH=A」并列留痕，不代裁）；"
     "⑥完整判据（N1~N11／S5／H1~H8／焊接 W1~W7）→ `references/asm13-nickel.md`",
     None),
    # 钛 × 卤化物/硫酸盐（缝隙腐蚀与氢化）—— P0-2 轮，ASM Vol.13 钛篇
    (r"氯|溴|碘|氟|Cl|Br|氯化物|盐|海水|saline|chloride|brine",
     "**钛的缝隙腐蚀与氢化须知**（ASM Vol.13〈钛及钛合金〉1987，p1694~1695/p1725/p1734；L3 手册层）："
     "①**缝隙腐蚀门槛：T>70 ℃ ＋ 氯/溴/碘/氟/硫酸盐溶液 ＋ 紧缝隙**（垫片、管板胀接、沉积物/垢下）→ 缝隙内 pH 可低至 ≤1，局部活性腐蚀快速；"
     "②⭐⭐**阴阳离子方向相反**：**阳离子型氧化剂（O₂/Cl₂/Fe³⁺/Cu²⁺）抑制全面腐蚀、却加速缝隙腐蚀**（阴极去极化，进不了缝隙）；"
     "**阴离子型氧化剂（NO₃⁻/ClO⁻ 等）可迁入缝隙 → 抑制缝隙腐蚀** ⇒ 「加氧化剂就安全」是错的；"
     "③**牌号分档**：饱和 NaCl 盐水中 **Gr.12 比 Gr.2 抗**（Fig.3 案例）；④缝隙周围常见**氢化钛**析出（阴极析氢副产物）；"
     "⑤**阴极充氢在 T>80 ℃ 不建议**（与碱/氢化同一门槛）；⑥高温侧：**<300 ℃ 氧/含硫气体无明显退化；>340~370 ℃ 过度氧化＋间隙元素脆化**；"
     "⑦还原性稀酸（亚硫酸/H₂S 水溶液/硼酸/碳酸）近零腐蚀率且可至沸点以上；**强还原性酸需氧化剂抑制**（Fe³⁺ 百 ppm 级有效；"
     "HNO₃/硝酸盐**在 HCl 有效、在 H₂SO₄/H₃PO₄ 有限**）→ 完整判据见 `references/asm13-titanium.md`",
     {"titanium"}),
    # 锆 × 氯气（干湿反极性）
    (r"氯|chlorine",
     "**锆与氯气：干湿反极性**（ASM Vol.13〈锆与铪〉1987，p1830/p1831/p1862；L3 手册层）："
     "**湿氯气禁忌**（含水 >0.13% H₂O、94 ℃ → >1.3 mm/a；氯水饱和液 75 ℃ 同）；**干氯气可用**（室温 <0.13 mm/a，不与卤素反应至约 200 ℃）。"
     "⚠️**与钛相反**（钛＝干氯危险、湿氯可用）⇒ 先问干湿再选材。注意区分：**次氯酸钠/次氯酸钙等盐类是低腐蚀的**（6% 次氯酸钠 50 ℃ nil），"
     "与「湿氯气」不是一回事；判据应按**游离氯浓度**而非「含氯与否」。",
     {"zirconium"}),
    # 锆 × 硫酸（浓度断崖与工程条件）
    (r"硫酸|sulfuric|sulphuric",
     "**锆与硫酸**（ASM Vol.13〈锆与铪〉1987，p1848~1853/p1868；L3 手册层）："
     "①**≤70% 全浓度、至沸腾及以上均耐蚀**；⭐最有价值两区＝**40~60%** 与 **稀硫酸＋高温**（铁基/镍基在这两区腐蚀快）；"
     "②⭐**氧化剂容忍分界＝65%**：<65% 可容忍相当量 Fe³⁺/Cu²⁺/NO₃⁻，**>65% 即敏感**（70%＋3 ppm Cu²⁺ 已 0.13~0.25 起）；"
     "③**浓度断崖**：沸腾 **≥77.5% 三合金均 >1.3 mm/a**（高浓区氧化膜被硫酸锆/氢化物膜取代）；"
     "④⭐⭐**超限后可能出现自燃（pyrophoric）表面层**（77.5%＋200 ppm Fe³⁺、80 ℃）——**这是安全后果**，须热空气或蒸汽处理消除；"
     "⑤**真空/无压系统水蒸气被带走 ⇒ 酸浓可超限**（浓度限值会因系统形态被突破）；"
     "⑥**焊缝在 ≳55% 时优先腐蚀 ⇒ 必须 775±15 ℃、1 h/25.4 mm 热处理**；⑦**单独 Cl⁻ 不降低耐蚀**（致害是重金属离子＋卤素共存）；"
     "⑧硫酸回收系统可用条件是**无氟化物 ∧ 酸浓 ≤65%**（缺一不可）",
     {"zirconium"}),
    # 锆 × 氢/水蒸汽（吸氢窗口）
    (r"氢|hydrogen|水|蒸汽|steam|water",
     "**锆与氢（吸氢窗口）**（ASM Vol.13〈锆与铪〉1987，p1845~1848/p1862；L3 手册层）："
     "①**全氢气氛 310 ℃ 起吸氢**、氧化膜挡氢有效至 **760 ℃**（>750 ℃ 真空退火可脱氢）；"
     "②**吸氢基线（沸腾海水 365 d）**：未焊件 6~9 ppm H；⭐**含镍 Zr704 焊件＋钢偶合 → 450 ppm H，氢化物集中于焊缝热影响区**（该件过载后已失延性）；"
     "③**Zircaloy-4 吸氢约为 Zircaloy-2 的一半以下**，且**溶解氧降低吸氢**；"
     "④**预氧化/高压釜成膜可大幅降低吸氢速率**（19 MPa 去离子水 360 ℃×14 d；或 400 ℃/10 MPa 高纯蒸汽×1~3 d）；"
     "⑤水/蒸汽腐蚀**不规则**（受杂质支配）⇒ 数据按「带」处理：**N >40 ppm、C >300 ppm 即显著劣化**",
     {"zirconium"}),
]


def _media_notes(chem, material=""):
    fams = mat_families(material) if material else set()
    out = []
    for entry in MEDIA_NOTES:
        pat, note = entry[0], entry[1]
        need = entry[2] if len(entry) > 2 else None
        if need and not (fams & set(need)):
            continue
        if re.search(pat, str(chem), re.I):
            out.append(note)
    return out


def gate56_corrosion(case, material, data_root):
    """⑤⑥ 入口：外包一层「介质判据注」——**不改原始判定**，只把 L3 有向指引附到 detail。"""
    status, detail = _gate56_impl(case, material, data_root)
    notes = _media_notes(_media_text(case), material)   # ⚠️ 必须传 material——材料族限定的判据注靠它过滤
    if notes and isinstance(detail, dict):
        detail = dict(detail)
        detail["介质判据注（L3 手册层）"] = notes
    return status, detail


def _gate56_impl(case, material, data_root):
    # 材料×介质禁忌硬否决（2026-10-10 验证轮建／P0-2 轮扩展）：**不依赖数据源**（"已知的不能"先于一切查询）——
    # 数据源常温评级不能覆盖热工况禁忌（首例：钛×热浓碱，L1b=A vs ASM T>80 ℃ 吸氢氢脆）。
    # ⚠️ P0-2 轮两处升级：① 匹配面从「介质名」扩到 **_media_text（名＋杂质＋备注）**——这样
    #    「盐酸 + 杂质 F⁻ 50 ppm」也能触发钛-氟禁忌；② 支持 **tlim=None＝任意温度**（氟化物/甲醇/干氯/镉类禁忌无温度下限）。
    chem = str(case.get("media", {}).get("name", "")).strip()
    mtext = _media_text(case)
    t = (case.get("media", {}).get("temperature") or {})
    tmax = t.get("max", t.get("normal"))
    for fam, pat, tlim, mech, ref in CONTRAINDICATIONS:
        if fam in mat_families(material) and re.search(pat, mtext, re.I):
            fired = (tlim is None) or (tmax is not None and float(tmax) > float(tlim))
            if fired:
                gate_txt = "任意温度" if tlim is None else f"门槛 {tlim} ℃"
                return RED, {
                    "禁忌命中": f"「{material}」×「{chem}」@ {tmax if tmax is not None else '未给温度'} ℃（{gate_txt}）",
                    "机理": mech,
                    "出处": ref,
                    "与数据源的关系": "L1/L1b 的评级为**常温/低还口径**，不推翻本禁忌——"
                                     "两口径并列：常温评级可作 ≤门槛温度区间的参考，"
                                     "热工况以本禁忌为准（**宁严勿松**）",
                    "动作": "换用该介质热工况的适用材料（如热浓碱→镍 200/201、Monel；"
                            "以数据源与原书页锚复核）；**若判为可推翻，须逐条满足机理栏写明的缓解条件并留证**",
                    "判据句": "热工况禁忌对数据源评级有否决权——评级 A 不等于全工况通行证",
                }
    if not data_root:
        return ORANGE, {"缺": "未提供腐蚀数据源根目录（--data-root 或环境变量 RAY_MATSELECT_DB）",
                        "动作": "提供后重跑；**本题不得凭记忆填速率**",
                        "卡住": "闸门⑤【均匀腐蚀】与闸门⑥【局部腐蚀】"}
    rows, path = load_alleima(data_root)
    if rows is None:
        return ORANGE, {"缺": f"在 {data_root} 未找到 Alleima 主库 CSV", "动作": "核对 --data-root"}
    chem = str(case.get("media", {}).get("name", "")).strip()
    t = (case.get("media", {}).get("temperature") or {})
    tmax = t.get("max", t.get("normal"))
    cm = canon_material(material)
    # 化学品：先精确（不区分大小写），再子串
    cands = [r for r in rows if r["化学品"].strip().lower() == chem.lower()]
    match_mode = "精确匹配"
    bridge_hit = None
    if not cands and chem in CN2EN:
        en = CN2EN[chem]
        cands = [r for r in rows if r["化学品"].strip().lower() == en.lower()]
        bridge_hit = f"{chem}→{en}"
        match_mode = f"中→英桥（{bridge_hit}）"
    if not cands:
        cands = [r for r in rows if chem.lower() and chem.lower() in r["化学品"].lower()]
        # ⚠️ 2026-10-10 修措辞 bug：原写法把「桥命中但候选为空」也报成「桥未命中」，
        #    会让排查者以为 CN2EN 缺词条、去补一个**已存在**的桥。两态必须分开报。
        if bridge_hit:
            match_mode = f"子串匹配（中→英桥命中 {bridge_hit}，但主库无该化学品独立行）"
        else:
            match_mode = "子串匹配（中→英桥未命中）"
    cands = [r for r in cands if r["牌号/合金"].strip().lower() == cm.strip().lower()]
    if not cands:
        l1b = lookup_l1b(data_root, chem, material)
        if l1b and l1b.get("评级"):
            _g = str(l1b["评级"]).strip().upper()
            # ⚠️ 2026-10-09 实测修正：首版一律给 🟡，把 D（不可）也放过 ⇒ 分档。
            _st = RED if _g.startswith("D") else (YELLOW if _g.startswith("C") else OK)
            return _st, {"L1（Alleima）": f"无「{chem} × {cm}」组合（匹配模式：{match_mode}）",
                         "L1b 兜底": l1b,
                         "分档依据": {"D": "不可用 ⇒ 🔴 否决", "C": "可用性受限 ⇒ 🟡",
                                      "A/B": "可用 ⇒ 但仍须过其余闸门"}.get(_g[0], "未识别"),
                         "判据句": "L1b 是**人工汇编**（可信度低于 L1）⇒ **不得外推**为定量速率；"
                                   "判 🔴 时建议以 L1 / 标准原文复核后再签"}
        # ⚠️ 2026-10-09 增：L1/L1b 双未命中时查 L1c 手册页锚索引（有向指针，仍 fail-closed）
        l1c = lookup_l1c(data_root, chem, material)
        if l1c:
            return ORANGE, {"缺": f"L1（Alleima）与 L1b 均无「{chem} × {cm}」的定量评级",
                            "匹配模式": match_mode,
                            "L1c 手册页锚": l1c,
                            "结论": "🟠（**有向指针**：原书有覆盖，评级须查原图；**不是「可以用」**）",
                            "判据句": "数据不足不放行（立场 1），但给出去哪查——比裸 🟠 可执行"}
        return ORANGE, {"缺": f"数据源中无「{chem} × {cm}」组合，且 L1b/L1c 亦无覆盖",
                        "匹配模式": match_mode,
                        "L1b": l1b,
                        "动作": "换化学品名（L1 用英文名）或换牌号；**不得外推**"}
    # 就近取温（取 ≤ tmax 的最大记录）
    parsed = [(parse_cond(r["工况(浓度/温度等)"]), r) for r in cands]
    exact = [(c, r) for c, r in parsed if c["temp"] is not None]
    if tmax is not None and exact:
        le = [x for x in exact if x[0]["temp"] <= tmax]
        pick = max(le, key=lambda x: x[0]["temp"]) if le else min(exact, key=lambda x: x[0]["temp"])
        pick_note = f"取 ≤{tmax}℃ 的最高温度点" if le else "无 ≤ 该温度点，取最低温度点（偏保守）"
    else:
        pick = parsed[0]; pick_note = "无数值温度，取首条"
    cond, row = pick
    rating = str(row["评级"]).strip()
    base = rating[0] if rating and rating[0].isdigit() else None
    sufs = [ch for ch in rating[1:] if ch.isalpha()]
    risks = []
    i = 1
    while i < len(rating):
        two = rating[i:i+2]
        if two.upper() == "ND":
            risks.append(SUFFIX["ND"]); i += 2; continue
        if rating[i] in SUFFIX:
            risks.append(SUFFIX[rating[i]])
        i += 1
    status = RED if (base == "2") else (YELLOW if (base == "1" or risks) else OK)
    return status, {
        "数据源": "Alleima 腐蚀数据主库（本地工作库，库外）",
        "化学品": chem, "牌号(归一后)": cm, "匹配模式": match_mode,
        "命中工况": cond["raw"], "选点依据": pick_note,
        "评级": rating,
        "均匀腐蚀": RATING.get(base, f"未识别评级首字符 {base!r}"),
        "局部腐蚀": risks or ["未标风险后缀"],
        "原文链接": row["原文链接"],
        "⚠️ 时效": "该评级为该源的历史经验数据，**不等于本装置实际工况**；⑤⑥取值应优先用本装置测厚数据",
        "L1b 交叉校核": lookup_l1b(data_root, chem, material),
        "⚠️ 不一致时": "L1 与 L1b 结论若冲突 ⇒ **并列留痕、不代裁**（两者口径与来源均不同）",
    }

# ============================================================ 闸门⑦ 制造焊接
def gate7_fab(case, material):
    dev = case.get("equipment", {})
    notes = []
    if not dev.get("welded", True):
        return OK, {"说明": "未声明焊接；若有焊接件须按下列项核", "提示": []}
    notes.append("**焊缝与热影响区是绝对薄弱环节**（残余应力 + 晶粒粗化 + 气孔夹渣）")
    if re.search("Q235|Q345|20#|16Mn|碳钢|carbon", str(material), re.I):
        notes.append("碳钢/低合金钢：核碳当量 CE 与焊后热处理（PWHT）必要性")
    if not dev.get("pwht") and re.search("H2S|硫化氢|氨|碱", str(case.get("media", {}).get("name", "")), re.I):
        notes.append("⚠️ 介质提示开裂敏感 → 应核 PWHT 与硬度上限（湿 H₂S 环境通常要求 HB≤200 量级，须查标准原文）")
    # ⚠️ 2026-10-09 实测修正：本闸原**恒出 🟠** ⇒ 整体永远到不了 ✅（"✅ 推荐"形同虚设）。
    #   语义修正：本闸给的是**可验收前提**（须 PWHT / 硬度检查 / 镍基焊材…）⇒ 应映射 **🟡 有条件推荐**；
    #   仅当**材料未归一到任何族**（连可焊性都无从谈起）时才 🟠。
    fam = mat_families(material)
    if not fam:
        return ORANGE, {"说明": f"材料 {material!r} 未归一，无法判可焊性/焊材匹配",
                        "动作": "补 MAT_FAMILY 别名后重判"}
    return YELLOW, {"说明": "**判定为「有条件推荐」**——下列为可验收前提，须逐条落实并留证；"
                            "可焊性/焊材/异种钢连接的**细部**仍须查 references/gate-03/08 与设计文件",
                    "材料族": sorted(fam),
                    "可验收前提": notes}

# ============================================================ 闸门⑧ 标准合规
def gate8_standard(case, material):
    dev = str(case.get("equipment", {}).get("type", ""))
    rows = []
    if "容器" in dev or "储罐" in dev or "换热" in dev:
        rows.append({"设备类别": dev, "适用标准": "GB/T 150.1~150.4",
                     "口径": "按 GB/T 150.2 的允许使用温度与附录D（Q235 系列）",
                     "易混": "**不要用管道口径**"})
    if "管道" in dev:
        rows.append({"设备类别": dev, "适用标准": "GB/T 20801.1~20801.5",
                     "口径": "曲线 A/B 允许温度；第 3.1 条低温低应力工况豁免（**仅 GC2**）",
                     "易混": "**不要用容器口径**"})
    if re.search("Q235B", str(material), re.I):
        rows.append({"特别提醒": "Q235B：容器 20~300℃ vs 管道 −10℃ —— **同名不同量，差 30 K**",
                     "出处": "GB/T 150.2-2024 附录D e ／ GB/T 20801.2-2020 曲线A"})
    # 2026-10-09 增：氧气系统（GB/T 30579-2022 §9.10，判据已亲核物理页 117~119；O₂>25%(体) 触发）
    if re.search(r"氧气|纯氧|液氧|富氧|\bO2\b",
                 str(case.get("media", {}).get("name", "")) + str(case.get("media", {}).get("impurities", "")), re.I):
        rows.append({"特别提醒": "**氧气系统选材（GB/T 30579 §9.10 高含氧气体促发的燃烧爆炸，O₂>25% 体 即触发）**："
                                "①碳钢/低合金钢 ≥0.1 MPa 即可能燃烧；②奥氏体不锈钢 <1.38 MPa 耐燃；"
                                "③铜合金(Cu>55%)/镍基(Ni>50%)/蒙乃尔 400 按「不可燃」选用；"
                                "④铝不可用于氧气管道；⑤钛禁用（7 kPa 即持续燃烧；源 OCR 作「铁合金」，疑为钛，须核原文）；"
                                "⑥塑料/橡胶/润滑油严禁接触；⑦流速应降低（源举例 ≤30 m/s）、系统洁净度关键",
                     "出处": "GB/T 30579-2022 §9.10.3/§9.10.6（物理页 117~119，A− OCR 已亲核）；"
                             "该标准附录全为资料性 ⇒ 选材风险判据而非强制边界，正式设计回原文核"})
    if not rows:
        return ORANGE, {"缺": f"设备类别 {dev!r} 未映射到标准口径表", "动作": "查 references/gate-08-standard.md"}
    return OK, {"口径": rows, "判据句": "判容器必须用容器口径；按设备类别选口径，混用即违规"}

# ============================================================ 主流程
def evaluate(case, material, data_root):
    res = {}
    if validate_contract:
        _, missing = validate_contract(case)
        res["① 输入完整性"] = (ORANGE, {"缺": [m["meaning"] for m in missing]}) if missing else (OK, {"说明": "契约齐备"})
    else:
        res["① 输入完整性"] = (ORANGE, {"缺": "校验器未加载"})
    res["② 机械边界"] = (OK, {"说明": "本闸只判边界够不够；**强度/壁厚/MAWP 走 ray-pe-calc** 与 GB/T 150.3"})
    res["③ 温度边界"] = gate3_temperature(case, material)
    res["④ 环境开裂SCC"] = gate4_scc(case, material)
    res["⑤⑥ 腐蚀"] = gate56_corrosion(case, material, data_root)
    res["⑦ 制造焊接"] = gate7_fab(case, material)
    res["⑧ 标准合规"] = gate8_standard(case, material)
    # 串联否决
    st = [v[0] for v in res.values()]
    if RED in st:
        overall = RED
    elif ORANGE in st:
        overall = ORANGE
    elif YELLOW in st:
        overall = YELLOW
    else:
        overall = OK
    return overall, res

def main():
    ap = argparse.ArgumentParser(description="八道闸门判定引擎（串联否决 / fail-closed）")
    ap.add_argument("--case", help="输入 case JSON")
    ap.add_argument("--material", help="待判材质（完整牌号）")
    ap.add_argument("--data-root", default=os.environ.get("RAY_MATSELECT_DB"),
                    help="腐蚀数据源根目录（或环境变量 RAY_MATSELECT_DB）")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if a.demo:
        print(json.dumps({"material": "Carbon steel", "data_root_env": "RAY_MATSELECT_DB",
                          "用法": "python evaluate_material.py --case case.json --material \"Carbon steel\" --data-root <目录>"},
                         ensure_ascii=False, indent=2))
        return 0
    if not a.case or not a.material:
        ap.error("需要 --case 与 --material")
    try:
        case = json.load(open(a.case, encoding="utf-8-sig"))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False)); return 2

    overall, res = evaluate(case, a.material, a.data_root)
    payload = {"overall": overall, "material": a.material, "gates": {
        k: {"status": v[0], "detail": v[1]} for k, v in res.items()}}
    if a.json:
        # ⚠️ 2026-10-09（本轮）真实案例测试抓出的**真缺陷**：JSON 是**机器契约**，而默认走控制台
        #    代码页（中文 Windows = cp936/GBK）⇒ 🔴/🟠/✅ 在 GBK 中不可表示，被 _console_safe()
        #    降级为 '?' ⇒ **`overall` 与每个闸门的 `status` 全部退化成 '?'**（结论丢失）；
        #    而**退出码仍正确** ⇒ 既有测试"全绿"把它掩盖了（测试只 print 不断言、且按 utf-8 解码子进程）。
        #    修：JSON 路径强制 UTF-8（RFC 8259 §8.1 —— JSON 交互必须 UTF-8）；万一 reconfigure
        #    不可用，退回 `ensure_ascii=True`（纯 ASCII 转义）—— 两种都保证任何解码器都能读回正确符号。
        ok_utf8 = True
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            ok_utf8 = False
        print(json.dumps(payload, ensure_ascii=not ok_utf8, indent=2))
    else:
        print("=" * 72)
        print(f"八道闸门判定   材质：{a.material}    结论：{_DISP.get(overall, overall)}")
        print("=" * 72)
        for k, (s, d) in res.items():
            print(f"\n{_DISP.get(s, s)} {k}")
            for kk, vv in d.items():
                if isinstance(vv, list):
                    print(f"    {kk}:")
                    for it in vv:
                        print(f"      - {it if not isinstance(it, dict) else json.dumps(it, ensure_ascii=False)}")
                else:
                    print(f"    {kk}: {vv}")
        print("\n" + "-" * 72)
        print("[!] 本输出是**判定底稿**，须由有资质工程师在具体设计条件下复核签发。")
        if overall == ORANGE:
            print("[!] [HOLD] = 行动指令（去补数据），**不是「可以用」**。")
    return {OK: 0, YELLOW: 0, ORANGE: 3, RED: 4}[overall]

if __name__ == "__main__":
    sys.exit(main())
