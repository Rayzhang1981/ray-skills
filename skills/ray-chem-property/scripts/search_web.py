# -*- coding: utf-8 -*-
"""Step 1（联网主干）— 从 PubChem 结构化抓取物性/危害/毒性/接触限值。

读取 resolve_identifiers.py 产出的 <out>/input.json，对每个物料抓取数据块：
  - 标识（PUG-REST property）
  - 物性（PUG-View "Chemical and Physical Properties" → Experimental Properties）
  - 燃爆（PUG-View "Safety and Hazard Properties" → LEL/UEL）
  - GHS（PUG-View "GHS Classification" → Signal + GHS Hazard Statements）
  - NFPA 704（PUG-View "NFPA Hazard Classification"）
  - 毒理 LD50/LC50（PUG-View "Non-Human Toxicity Values"）
  - 接触限值（PUG-View "Exposure Control and Personal Protection" → IDLH/AEGL/PAC/ERPG）
输出 <out>/raw_{cas}.json。

PubChem 覆盖约 70% 字段；中文名/气味中文/检测阈值/法规名录/火灾危险类别/TEEL
需由 Agent 用 WebFetch 补采 chemicalbook / NIST / CAMEO / whpdj / IMA，
写入 <out>/supplement_{cas}.json。
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pubchem_api import get_properties, get_pugview, IDENTIFIER_PROPS  # noqa: E402


# ---------- PUG-View 通用遍历 ----------
def _find_sections(node, heading):
    """大小写不敏感的 TOCHeading 子串匹配。"""
    out = []
    key = heading.lower()
    def walk(n):
        if isinstance(n, dict):
            h = n.get("TOCHeading")
            if isinstance(h, str) and key in h.lower():
                out.append(n)
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(node)
    return out


def _texts(node):
    out = []
    def walk(n):
        if isinstance(n, dict):
            if "StringWithMarkup" in n:
                for m in n["StringWithMarkup"]:
                    if isinstance(m, dict) and m.get("String"):
                        out.append(m["String"].strip())
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(node)
    return [t for t in out if t]


def _name_values(node):
    """提取 Information 节点的 Name→Value 对。"""
    pairs = []
    def walk(n):
        if isinstance(n, dict):
            if "Name" in n and "Value" in n:
                pairs.append((str(n["Name"]), _texts(n["Value"])))
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(node)
    return pairs


def _leading_num(s):
    m = re.match(r"^\s*(\d)", str(s))
    return m.group(1) if m else ""


# ---------- 各数据块 ----------
PHYSICAL_HEADINGS = {
    "Boiling Point": "boiling_point",
    "Melting Point": "melting_point",
    "Flash Point": "flash_point",
    "Density": "density",
    "Vapor Pressure": "vapor_pressure",
    "Viscosity": "viscosity",
    "Autoignition Temperature": "autoignition",
    "Heat of Combustion": "heat_of_combustion",
    "Heat of Vaporization": "heat_of_vaporization",
    "Odor": "odor",
    "Odor Threshold": "odor_threshold",
    "Solubility": "solubility",
    "Color/Form": "color_form",
}


def fetch_identifiers(cid):
    return get_properties(cid, IDENTIFIER_PROPS) or {}


def fetch_physical(cid):
    view = get_pugview(cid, "Chemical and Physical Properties")
    out = {k: [] for k in PHYSICAL_HEADINGS.values()}
    if not view:
        return out
    for heading, key in PHYSICAL_HEADINGS.items():
        for node in _find_sections(view, heading):
            for t in _texts(node):
                if t not in out[key]:
                    out[key].append(t)
    return out


def fetch_flammability(cid):
    """LEL/UEL 等燃爆数据。"""
    view = get_pugview(cid, "Safety and Hazard Properties")
    out = {"lel": [], "uel": []}
    if not view:
        return out
    for node in _find_sections(view, "Lower Explosive Limit"):
        for t in _texts(node):
            out["lel"].append(t)
    for node in _find_sections(view, "Upper Explosive Limit"):
        for t in _texts(node):
            out["uel"].append(t)
    return out


def fetch_ghs(cid):
    view = get_pugview(cid, "GHS Classification")
    result = {"signal": "", "hazard_statements": []}
    if not view:
        return result
    for name, vals in _name_values(view):
        if name == "Signal":
            if vals and not result["signal"]:
                result["signal"] = vals[0]
        elif "Hazard Statements" in name:
            for v in vals:
                if v not in result["hazard_statements"]:
                    result["hazard_statements"].append(v)
    return result


def fetch_nfpa(cid):
    view = get_pugview(cid, "NFPA Hazard Classification")
    result = {"health": "", "fire": "", "instability": "", "special": ""}
    if not view:
        return result
    for name, vals in _name_values(view):
        low = name.lower()
        if "health" in low:
            result["health"] = _leading_num(vals[0]) if vals else ""
        elif "fire" in low:
            result["fire"] = _leading_num(vals[0]) if vals else ""
        elif "instability" in low:
            result["instability"] = _leading_num(vals[0]) if vals else ""
        elif "special" in low:
            result["special"] = vals[0] if vals else ""
    return result


def fetch_toxicity(cid):
    view = get_pugview(cid, "Non-Human Toxicity Values")
    result = {"ld50": [], "lc50": []}
    if not view:
        return result
    for node in _find_sections(view, "Non-Human Toxicity Values"):
        for t in _texts(node):
            if "LD50" in t or "LD 50" in t:
                result["ld50"].append(t)
            elif "LC50" in t or "LC 50" in t:
                result["lc50"].append(t)
    return result


def fetch_exposure(cid):
    view = get_pugview(cid, "Exposure Control and Personal Protection")
    result = {"erpg": [], "aegl": [], "pac": [], "teel": [], "idlh": []}
    if not view:
        return result
    probes = {
        "erpg": "Emergency Response Planning Guidelines",
        "aegl": "Acute Exposure Guideline Levels",
        "pac":  "Protective Action Criteria",
        "teel": "Temporary Emergency Exposure Limits",
        "idlh": "Immediately Dangerous to Life or Health",
    }
    for key, h in probes.items():
        for node in _find_sections(view, h):
            for t in _texts(node):
                if t not in result[key]:
                    result[key].append(t)
    return result


def build_raw(rec):
    resolved = rec.get("resolved") or {}
    cid = resolved.get("cid")
    raw = {
        "input": rec.get("input"),
        "cid": cid,
        "cas": resolved.get("cas", ""),
        "is_mixture": rec.get("is_mixture", False),
        "is_polymer": rec.get("is_polymer", False),
        "identifiers": {},
        "physical": {},
        "flammability": {},
        "ghs": {},
        "nfpa": {},
        "toxicity": {},
        "exposure": {},
        "error": rec.get("error"),
    }
    if cid is None:
        return raw
    raw["identifiers"] = fetch_identifiers(cid)
    raw["physical"] = fetch_physical(cid)
    raw["flammability"] = fetch_flammability(cid)
    raw["ghs"] = fetch_ghs(cid)
    raw["nfpa"] = fetch_nfpa(cid)
    raw["toxicity"] = fetch_toxicity(cid)
    raw["exposure"] = fetch_exposure(cid)
    return raw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="output", help="输出目录（含 input.json）")
    args = ap.parse_args()

    in_path = os.path.join(args.out, "input.json")
    if not os.path.exists(in_path):
        print(f"[search] 未找到 {in_path}，请先运行 resolve_identifiers.py")
        sys.exit(1)

    records = json.load(open(in_path, encoding="utf-8"))
    for rec in records:
        raw = build_raw(rec)
        cas = raw.get("cas") or raw.get("cid") or rec.get("input")
        safe = str(cas).replace("/", "_").replace(" ", "_")
        out_path = os.path.join(args.out, f"raw_{safe}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(raw, f, ensure_ascii=False, indent=2)
        n_phy = sum(len(v) for v in raw.get("physical", {}).values())
        n_ghs = len(raw.get("ghs", {}).get("hazard_statements", []))
        print(f"[search] {rec.get('input')} (CID {raw.get('cid')}) → {out_path}  物性 {n_phy} 条, GHS {n_ghs} 条")


if __name__ == "__main__":
    main()
