# -*- coding: utf-8 -*-
"""Step 1b — 本地索引自动补采：从 data/ 索引为每个 CAS 生成 supplement_{cas}.json。

把本地 10 项数据资产（法规/AEGL/PAC/CAMEO）自动合并成补采数据，供 merge_compare 使用：
- 危化品目录索引 → reg_hazchem（是/否）、reg_high_toxic（剧毒）、中文 GHS 类别写入 remark
- 有毒气体目录索引 → reg_high_toxic（高毒判定）
- GBZ_OEL索引 → 职业接触限值写入 remark（GBZ 2.1-2007）
- AEGL索引 → aegl1/2/3_10 / aegl1/2/3_60
- PAC索引 → pac1/2/3
- 中文名映射（--names "CAS:中文名,..." 或自动读 output/input.json 的 input）

用法：
  python scripts/auto_supplement.py --out output/
  python scripts/auto_supplement.py --out output/ --names "1310-73-2:氢氧化钠,50-00-0:甲醛"
  python scripts/auto_supplement.py --out output/ --dry-run   # 只看每个 CAS 命中哪些索引

产出：output/supplement_{cas}.json（{"fields": {...}} 格式，与 SKILL.md Step 1c 一致）
"""
import argparse
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "data"))

INDEX_FILES = {
    "hazcat": os.path.join(DATA_DIR, "危化品目录索引.json"),
    "gbz": os.path.join(DATA_DIR, "GBZ_OEL索引.json"),
    "toxic": os.path.join(DATA_DIR, "有毒气体目录索引.json"),
    "aegl": os.path.join(DATA_DIR, "AEGL索引.json"),
    "pac": os.path.join(DATA_DIR, "PAC索引.json"),
    "book": os.path.join(DATA_DIR, "危险品全书-通用卷索引.json"),
    "crc": os.path.join(DATA_DIR, "CRC97-索引.json"),
    "lange": os.path.join(DATA_DIR, "兰氏15-索引.json"),  # 无 CAS，list；按名称查
    "perry": os.path.join(DATA_DIR, "Perry8-临界常数索引.json"),  # 临界常数 Tc/Pc/Vc/Zc/acentric
    "sara": os.path.join(DATA_DIR, "SARA-物性索引.json"),  # 无 CAS，list 按名称查；Tc/Pc/Mw/NBP + 蒸气压20/25/60 + 系数
    "emergency": os.path.join(DATA_DIR, "应急准则索引.json"),  # 按 CAS 键 dict；急救/消防/泄漏处置/操作储存四要素
    "erg": os.path.join(DATA_DIR, "ERG2024-索引.json"),  # 按 UN 号键 dict；ERG2024 Yellow Table 1 隔离/防护距离
}

# 大部头书索引（book）字段 → 106 列 skill 字段键。值需手工做单位/格式清理。
BOOK_MAP = {
    "appearance": "appearance", "ph": "ph", "mp": "mp", "bp": "bp",
    "density": "density_20", "vd": "vd", "vp": "vp", "heat_of_combustion": "heat_combustion",
    "critical_temp": "critical_temp", "critical_pressure": "critical_pressure",
    "logkow": "logkow", "fp": "fp_closed", "autoignition": "autoignition_temp",
    "lel": "lel", "uel": "uel", "decomposition_temp": "decomp_temp",
    "viscosity": "viscosity_20", "solubility": "solubility",
    "un_number": "un_number",
}


def load_indexes():
    idx = {}
    for k, p in INDEX_FILES.items():
        if os.path.exists(p):
            with open(p, encoding="utf-8") as f:
                idx[k] = json.load(f)
        else:
            idx[k] = {}
    return idx


def collect_fields(cas, idx, name_en=None):
    """为单个 CAS 收集可补采字段。返回 (fields, notes)。"""
    fields, notes = {}, []
    # 大部头物性书（最高优先级来源：应急管理部登记中心/青岛安工院编，权威性 > PubChem）
    bk = idx["book"].get(cas)
    if bk:
        filled = []
        for src_key, dst_key in BOOK_MAP.items():
            v = bk.get(src_key)
            if v:
                fields[dst_key] = {"value": str(v)}
                filled.append(f"{dst_key}={v}")
        if filled:
            notes.append(f"危险品安全技术全书(通用卷): {'; '.join(filled[:8])}")
        if bk.get("formula") and not fields.get("formula"):
            fields["formula"] = {"value": bk["formula"]}
        # UN 运输类别：un_class + un_packing 组合 → transport_category
        if bk.get("un_class") and not fields.get("transport_category"):
            tc = bk["un_class"]
            if bk.get("un_packing") and bk["un_packing"] != "-":
                tc += f"，{bk['un_packing']}"
            fields["transport_category"] = {"value": tc}
            filled.append(f"transport={tc}")
    # CRC Handbook（英文补充源：book 未覆盖的字段用 CRC 补，冲突时 book 优先）
    cr = idx["crc"].get(cas)
    if cr:
        filled = []
        for src_key, dst_key in (("mp", "mp"), ("bp", "bp"), ("density", "density_20"),
                                  ("formula", "formula"), ("mw", "mw")):
            v = cr.get(src_key)
            if v and not fields.get(dst_key):
                fields[dst_key] = {"value": str(v)}
                filled.append(f"{dst_key}={v}")
        if cr.get("nd") and not fields.get("nd"):
            fields["nd"] = {"value": str(cr["nd"])}
            filled.append(f"nd={cr['nd']}")
        if filled:
            notes.append(f"CRC Handbook 97th: {'; '.join(filled[:6])}")
    # Perry 8th 临界常数（Tc/Pc/Vc/Zc/acentric，直接值）
    pr = idx["perry"].get(cas)
    if pr:
        filled = []
        for src_key, dst_key in (("tc", "critical_temp"), ("pc", "critical_pressure"),
                                  ("zc", "zc"), ("acentric", "acentric_factor")):
            v = pr.get(src_key)
            if v and not fields.get(dst_key):
                fields[dst_key] = {"value": str(v)}
                filled.append(f"{dst_key}={v}")
        if filled:
            notes.append(f"Perry 8th 临界常数: {'; '.join(filled)}")
    # SARA 物性库（按名称查：Tc/Pc/Mw/NBP + 蒸气压 20/25/60℃ 计算值）
    if name_en:
        sr = match_sara(name_en, idx)
        if sr:
            filled = []
            for src_key, dst_key in (("tc_c", "critical_temp"), ("pc_bar", "critical_pressure"),
                                      ("mw", "mw"), ("nbp_c", "bp")):
                v = sr.get(src_key)
                if v and not fields.get(dst_key):
                    fields[dst_key] = {"value": str(v)}
                    filled.append(f"{dst_key}={v}")
            for T in (20, 25, 60):
                v = sr.get(f"vp_{T}c_pa")
                if v and not fields.get(f"vp_{T}"):
                    fields[f"vp_{T}"] = {"value": str(round(v / 1000, 2))}  # Pa → kPa
                    filled.append(f"vp_{T}={round(v/1000,2)}kPa")
            if filled:
                notes.append(f"SARA物性库: {'; '.join(filled[:8])}")
    # 应急准则（危险品全书第四~七部分，同 book 源）
    emg = match_emergency(cas, idx)
    if emg:
        text = format_emergency(emg)
        if text:
            fields["emergency_guidelines"] = {"value": text}
            notes.append(f"应急准则: 危险品全书通用卷（{emg.get('name_cn','')}）")
    # ERG2024 隔离/防护距离（UN 键 → 经 book 的 un_number 字段桥接 CAS）
    # 与 book 应急段互补：两者都命中时拼接（book 处置文本 + ERG 量化距离）。
    # ⚠️ ERG 段是量化核心数据（相比 book 长文本价值密度更高），拼接后统一截断，
    # 且 ERG 段放前面防止被截掉——调整顺序：ERG 段在前，book 应急段在后。
    erg_rec = match_erg(cas, idx)
    if erg_rec:
        text = format_erg(erg_rec)
        if text:
            prev = fields.get("emergency_guidelines", {}).get("value", "")
            fields["emergency_guidelines"] = {"value": (text + "｜" + prev) if prev else text}
            notes.append(f"应急准则: US DOT ERG2024 Table 1（{erg_rec.get('name','')}）")

    # 兜底：emergency_guidelines 总长统一截断（book 段内部已有 800 cap，
    # ERG 段拼接后会超长，这里统一保证 ≤900）
    emg = fields.get("emergency_guidelines")
    if emg and len(emg.get("value", "")) > 900:
        emg["value"] = emg["value"][:899] + "…"
    # 危化品目录
    hc = idx["hazcat"].get(cas)
    if hc:
        fields["reg_hazchem"] = {"value": "是"}
        if hc.get("toxic"):
            fields["reg_high_toxic"] = {"value": "是（危化品目录剧毒）"}
        haz = hc.get("hazards", "")
        if haz:
            notes.append(f"危化品目录2015: {haz[:150]}")
    # 有毒气体目录（高毒物品目录等）
    tg = idx["toxic"].get(cas)
    if tg and tg.get("sources"):
        srcs = "/".join(tg["sources"])
        fields["reg_high_toxic"] = {"value": f"是（{srcs}）"}
        if tg.get("twa") and not fields.get("reg_high_toxic"):
            notes.append(f"有毒气体目录 TWA={tg['twa']}")
    # GBZ OEL
    gz = idx["gbz"].get(cas)
    if gz:
        vals = []
        if gz.get("mac"):
            vals.append(f"MAC={gz['mac']}")
        if gz.get("twa"):
            vals.append(f"PC-TWA={gz['twa']}")
        if gz.get("stel"):
            vals.append(f"PC-STEL={gz['stel']}")
        if vals:
            notes.append(f"GBZ 2.1-2007职业接触限值: {' '.join(vals)} mg/m³（2019版为现行，需核对）")
    # AEGL（Final 值）
    ag = idx["aegl"].get(cas)
    if ag:
        for k in ("aegl1_10", "aegl1_60", "aegl2_10", "aegl2_60", "aegl3_10", "aegl3_60"):
            v = ag.get(k)
            if v:
                fields[k] = {"value": v}
        notes.append(f"AEGL 单位: {ag.get('unit','ppm')}")
    # PAC
    pc = idx["pac"].get(cas)
    if pc:
        for k in ("pac1", "pac2", "pac3"):
            v = pc.get(k)
            if v:
                fields[k] = {"value": v}
        if pc.get("unit"):
            notes.append(f"PAC 单位: {pc['unit']}")
    return fields, notes


def match_lange(name, idx):
    """按名称在兰氏索引（list，无 CAS）中查记录。返回记录 dict 或 None。

    匹配优先级：①归一化后完全相等 ②目标名是兰氏 name 的词首（如 Ethanol→Ethanol;Ethyl alcohol）
    ③目标名含于兰氏 name 且长度>=6。避免子串误匹配（Acetone 不应匹配 Dichloroacetone）。"""
    if not name or "lange" not in idx:
        return None

    def norm(s):
        return s.lower().replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace("’", "")

    target = norm(name)
    if len(target) < 4:
        return None
    best = None
    for rec in idx["lange"]:
        nm = norm(rec.get("name") or "")
        if not nm:
            continue
        # ① 完全相等
        if target == nm:
            return rec
        # ② 词首匹配（Ethanol 在 "Ethanol;Ethyl alcohol" 开头）
        if nm.startswith(target) and len(target) >= 4:
            if best is None or len(nm) < len(best.get("name") or ""):
                best = rec
        # ③ 兰氏名是目标的词首变体（"Ethanol" 是 "Ethanolamine" 前缀不匹配）
    return best


def match_sara(name, idx):
    """按名称在 SARA 索引（dict, key=小写名）查记录。返回记录 dict 或 None。

    PubChem 规范名与 SARA 常用名不一致时（propan-2-one→acetone、
    hexane→n-hexane、oxidane→water），经 ALIAS 别名表回退，否则会漏 SARA
    蒸气压/临界常数三档值。"""
    if not name or "sara" not in idx:
        return None
    target = name.lower().strip()
    # 别名回退：PubChem 规范名 → SARA 常用名
    ALIAS = {
        "propan-2-one": "acetone", "propanone": "acetone", "acetone": "acetone",
        "2-propanone": "acetone", "hexane": "n-hexane", "n-hexane": "n-hexane",
        "normal-hexane": "n-hexane", "oxidane": "water", "water": "water",
        "dihydrogen oxide": "water", "ethanoic acid": "acetic acid",
        "acetic acid": "acetic acid", "methanal": "formaldehyde",
        "formaldehyde": "formaldehyde", "benzenamine": "aniline",
        "aniline": "aniline", "methyl alcohol": "methanol",
        "ethyl alcohol": "ethanol", "toluol": "toluene",
        "sulfuric acid": "sulfuric acid", "sulphuric acid": "sulfuric acid",
        "sodium hydroxide": "sodium hydroxide", "caustic soda": "sodium hydroxide",
        "caustic": "sodium hydroxide", "ethyl acetate": "ethyl acetate",
        "acetic acid ethyl ester": "ethyl acetate", "benzene": "benzene",
        "toluene": "toluene", "methylbenzene": "toluene",
        "acetonitrile": "acetonitrile", "cyanomethane": "acetonitrile",
        "isopropanol": "2-propanol", "isopropyl alcohol": "2-propanol",
        "2-propanol": "2-propanol", "dimethyl ether": "dimethyl ether",
        "dimethyl ether (methoxymethane)": "dimethyl ether",
        "methylene chloride": "dichloromethane", "dichloromethane": "dichloromethane",
        "methyl chloride": "chloromethane", "chloromethane": "chloromethane",
        "vinyl chloride": "vinyl chloride", "chloroethene": "vinyl chloride",
        "hydrogen chloride": "hydrogen chloride", "hydrochloric acid": "hydrogen chloride",
        "ammonia": "ammonia", "ammonium hydroxide": "ammonia",
        "nitric acid": "nitric acid", "hydrogen peroxide": "hydrogen peroxide",
        "hydrogen dioxide": "hydrogen peroxide", "carbon monoxide": "carbon monoxide",
        "carbon dioxide": "carbon dioxide", "carbon disulfide": "carbon disulfide",
    }
    if target in ALIAS:
        target = ALIAS[target]
    if target in idx["sara"]:
        return idx["sara"][target]
    # 模糊：去空格/连字符后匹配
    norm = target.replace(" ", "").replace("-", "")
    if len(norm) < 4:
        return None
    for k, rec in idx["sara"].items():
        if k.replace(" ", "").replace("-", "") == norm:
            return rec
    return None


def match_emergency(cas, idx):
    """按 CAS 在应急准则索引（dict, key=CAS）中查记录。返回记录 dict 或 None。

    来源：《危险化学品安全技术全书》通用卷第四~七部分（急救/消防/泄漏应急/操作储存），
    与物性索引 book 同源同 CAS 键，故无需 ALIAS 回退——直接 CAS 精确命中。
    无效/占位键（_nocas 等）天然不在 dict 中。"""
    if not cas or "emergency" not in idx:
        return None
    rec = idx["emergency"].get(cas)
    return rec if isinstance(rec, dict) else None


def format_emergency(rec):
    """把应急准则记录拼成 emergency_guidelines 单元格文本。

    格式：『急救：…；泄漏：…』式分段，每段取子字段文本拼接，段间用 ｜ 分隔。
    控制总长在 Excel 可读范围（≤800 字），超长截断加省略号。"""
    if not rec:
        return ""
    parts = []
    for label, vkey in (("急救", "first_aid"), ("消防", "fire"),
                        ("泄漏处置", "spill"), ("操作储存", "handling_storage")):
        sub = rec.get(vkey)
        if not isinstance(sub, dict):
            continue
        segs = [f"{k}：{v}" for k, v in sub.items() if isinstance(v, str) and v.strip()]
        if segs:
            parts.append(f"【{label}】" + " ".join(segs))
    text = "｜".join(parts)
    if len(text) > 800:
        text = text[:799] + "…"
    return text


def match_erg(cas, idx):
    """按 CAS 查 ERG2024 Table 1 记录。ERG 索引键是 UN 号，借 book 物性索引的
    un_number 字段做 CAS→UN 桥接（book 与本函数查的 cas 同源）。
    命中条件：ERG 条目有实际距离值或 refer_table3（交叉引用空行不算命中）。"""
    if not cas or "erg" not in idx:
        return None
    bk = idx.get("book", {}).get(cas) or {}
    un = str(bk.get("un_number", "")).strip()
    if not un:
        return None
    rec = idx["erg"].get(un)
    if not isinstance(rec, dict):
        return None
    has_val = any(rec.get("small", {}).values()) or any(rec.get("large", {}).values())
    if not has_val and not rec.get("refer_table3"):
        return None
    return rec


def format_erg(rec):
    """把 ERG Table 1 记录拼成应急准则量化段（中文标签 + 公制值）。

    格式：【ERG2024隔离防护】小量泄漏：隔离30m，白天0.1km/夜间0.2km（下风向防护距离）
    ｜大量泄漏：隔离60m，白天0.4km/夜间0.7km 或 查Table 3。"""
    if not rec:
        return ""

    def grp_text(grp, prefix):
        iso = grp.get(prefix + "iso_m", "")
        d = grp.get(prefix + "day_km", "")
        n = grp.get(prefix + "night_km", "")
        if not (iso or d or n):
            return ""
        seg = []
        if iso:
            seg.append(f"隔离{iso}m")
        if d or n:
            seg.append(f"白天{d or '?'}/夜间{n or '?'}km")
        return "，".join(seg)

    parts = []
    small = grp_text(rec.get("small", {}), "")
    if small:
        parts.append(f"小量泄漏：{small}")
    if rec.get("refer_table3"):
        parts.append("大量泄漏：距离查ERG Table 3（按小时变化预估）")
    else:
        large = grp_text(rec.get("large", {}), "l_")
        if large:
            parts.append(f"大量泄漏：{large}")
    if not parts:
        return ""
    return "【ERG2024隔离防护】" + "｜".join(parts)


def main():
    ap = argparse.ArgumentParser(description="本地索引自动补采 supplement")
    ap.add_argument("--out", default="output", help="输出目录（读 input.json，写 supplement_*.json）")
    ap.add_argument("--names", help="中文名映射 'CAS:中文名,CAS:中文名'（覆盖 input.json 的 input）")
    ap.add_argument("--dry-run", action="store_true", help="只打印命中情况，不写文件")
    args = ap.parse_args()

    idx = load_indexes()

    # CAS 列表：优先 --names，否则读 input.json
    cas_list = []
    name_map = {}
    name_en_map = {}
    if args.names:
        for pair in args.names.split(","):
            if ":" in pair:
                c, n = pair.split(":", 1)
                cas_list.append(c.strip())
                name_map[c.strip()] = n.strip()
        # --names 只给中文名；英文名仍从 input.json 取（resolve 产物，供 SARA 按名查）
        inp = os.path.join(args.out, "input.json")
        if os.path.exists(inp):
            data = json.load(open(inp, encoding="utf-8"))
            for r in data:
                if r.get("resolved") and r["resolved"].get("cas"):
                    en = r.get("input") or r["resolved"].get("name_en")
                    if en and str(en).strip() and not re.fullmatch(r"[\d\-]{6,}", str(en).strip()):
                        name_en_map[r["resolved"]["cas"]] = str(en).strip()
                    else:
                        name_en_map[r["resolved"]["cas"]] = r["resolved"].get("name_en") or ""
    else:
        inp = os.path.join(args.out, "input.json")
        if not os.path.exists(inp):
            raise SystemExit(f"[auto] 未找到 {inp}，请先 resolve 或传 --names")
        data = json.load(open(inp, encoding="utf-8"))
        for r in data:
            if r.get("resolved") and r["resolved"].get("cas"):
                cas_list.append(r["resolved"]["cas"])
                # 英文名（用于 SARA 按名查）：优先用户输入（r.input 如 Acetone/n-Hexane，
                # 与 SARA 常用名一致），其次 PubChem 规范名（resolved.name_en，如 propan-2-one）
                raw = str(r.get("input") or "").strip()
                if raw and (" " in raw or raw.isalpha()):
                    name_en_map[r["resolved"]["cas"]] = raw
                elif r.get("name"):
                    name_en_map[r["resolved"]["cas"]] = r["name"]
                elif r["resolved"].get("name_en"):
                    name_en_map[r["resolved"]["cas"]] = r["resolved"]["name_en"]

    for cas in sorted(set(cas_list)):
        fields, notes = collect_fields(cas, idx, name_en=name_en_map.get(cas))
        cn = name_map.get(cas, "")
        if cn:
            fields["name_cn"] = {"value": cn}
        if notes:
            remark = fields.get("remark", {}).get("value", "")
            fields["remark"] = {"value": (remark + " | " if remark else "") + "；".join(notes[:3])}
        if args.dry_run:
            hits = [k for k in ("hazcat", "gbz", "toxic", "aegl", "pac") if idx[k].get(cas)]
            print(f"  {cas} 命中: {hits or '无'} 字段数: {len(fields)}")
            continue
        if not fields:
            continue
        sup = {"fields": fields}
        p = os.path.join(args.out, f"supplement_{cas}.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump(sup, f, ensure_ascii=False, indent=1)
        print(f"[auto] {cas} → {p}（{len(fields)} 字段）")

    if args.dry_run:
        print(f"[auto] DRY-RUN 完成，共 {len(set(cas_list))} 个 CAS")
    else:
        print(f"[auto] DONE: {len(set(cas_list))} 个 CAS")


if __name__ == "__main__":
    main()
