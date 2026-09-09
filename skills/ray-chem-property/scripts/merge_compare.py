# -*- coding: utf-8 -*-
"""Step 2 — 信息分析对比、去重、确定最终结果。

输入：<out>/raw_{cas}.json（PubChem 原始）+ <out>/supplement_{cas}.json（Agent 补采，可选）
输出：
  <out>/merged_{cas}.json —— 每个字段的候选值 + 来源 + 置信度（供人工审查）
  <out>/final_{cas}.json   —— 裁决后的最终值（供 export_excel / gen_html 消费）

裁决规则（见 references/conflict_rules.md）：
  人工补采 > PubChem 数据库汇总值 > 推导值
  物理量解析优先 SI 单位（°C / kg/m³ / mbar），冲突时保留全部候选值。
"""
import argparse
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "field_schema.json")

# ---------- GHS H-code → (字段键, 类别) ----------
HCODE_MAP = {
    "H200": ("haz_explosive", "不稳定爆炸物"), "H201": ("haz_explosive", "类别1"),
    "H202": ("haz_explosive", "类别1.4"), "H203": ("haz_explosive", "类别1.5"),
    "H204": ("haz_explosive", "类别1.6"), "H205": ("haz_explosive", "类别-"),
    "H220": ("haz_flam_gas", "类别1"), "H221": ("haz_flam_gas", "类别2"),
    "H222": ("haz_aerosol", "类别1"), "H223": ("haz_aerosol", "类别2"),
    "H224": ("haz_flam_liq", "类别1"), "H225": ("haz_flam_liq", "类别2"),
    "H226": ("haz_flam_liq", "类别3"), "H227": ("haz_flam_liq", "类别4"),
    "H228": ("haz_flam_solid", "类别1/2"),
    "H240": ("haz_self_react", "类别1"), "H241": ("haz_self_react", "类别2"),
    "H242": ("haz_self_heat", "类别1/2"),
    "H250": ("haz_pyro_liq", "类别1"), "H251": ("haz_self_heat", "类别1"),
    "H252": ("haz_self_heat", "类别2"),
    "H260": ("haz_water_flam", "类别1"), "H261": ("haz_water_flam", "类别2"),
    "H262": ("haz_water_flam", "类别3"),
    "H270": ("haz_ox_gas", "类别1"),
    "H271": ("haz_ox_solid", "类别1"), "H272": ("haz_ox_solid", "类别2/3"),
    "H280": ("haz_press_gas", "类别-"), "H281": ("haz_press_gas", "类别-"),
    "H290": ("haz_metal_corr", "类别1"),
    "H300": ("haz_acute_tox", "类别1/2"), "H301": ("haz_acute_tox", "类别3"),
    "H302": ("haz_acute_tox", "类别4"), "H303": ("haz_acute_tox", "类别5"),
    "H310": ("haz_acute_tox", "类别1/2"), "H311": ("haz_acute_tox", "类别3"),
    "H312": ("haz_acute_tox", "类别4"), "H313": ("haz_acute_tox", "类别5"),
    "H330": ("haz_acute_tox", "类别1/2"), "H331": ("haz_acute_tox", "类别3"),
    "H332": ("haz_acute_tox", "类别4"), "H333": ("haz_acute_tox", "类别5"),
    "H314": ("haz_skin_corr", "类别1"), "H315": ("haz_skin_corr", "类别2"),
    "H318": ("haz_eye_dam", "类别1"), "H319": ("haz_eye_dam", "类别2"), "H320": ("haz_eye_dam", "类别2"),
    "H317": ("haz_sens", "类别1"), "H334": ("haz_sens", "类别1"),
    "H340": ("haz_mutagen", "类别1"), "H341": ("haz_mutagen", "类别2"),
    "H350": ("haz_carcinogen", "类别1"), "H351": ("haz_carcinogen", "类别2"),
    "H360": ("haz_repro", "类别1"), "H361": ("haz_repro", "类别2"),
    "H370": ("haz_stot_se", "类别1"), "H371": ("haz_stot_se", "类别2"),
    "H335": ("haz_stot_se", "类别3"), "H336": ("haz_stot_se", "类别3"),
    "H372": ("haz_stot_re", "类别1"), "H373": ("haz_stot_re", "类别2"),
    "H304": ("haz_aspiration", "类别1"), "H305": ("haz_aspiration", "类别1"),
    "H400": ("haz_aquatic_acute", "类别1"), "H401": ("haz_aquatic_acute", "类别2"),
    "H402": ("haz_aquatic_acute", "类别3"),
    "H410": ("haz_aquatic_chronic", "类别1"), "H411": ("haz_aquatic_chronic", "类别2"),
    "H412": ("haz_aquatic_chronic", "类别3"), "H413": ("haz_aquatic_chronic", "类别4"),
    "H420": ("haz_ozone", "类别1"),
}


def load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------- 物理量解析 ----------
def _num(s):
    m = re.search(r"-?\d+(?:\.\d+)?", str(s))
    return m.group(0) if m else None


def _temp_c(s):
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*°C", str(s))
    return m.group(1) if m else None


def _temp_any_c(s):
    """提取温度（°C 优先，°F 自动换算为 °C）。"""
    t = _temp_c(s)
    if t:
        return t
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*°F", str(s))
    if m:
        return str(round((float(m.group(1)) - 32) * 5 / 9))
    return None


def _has_c(s):
    return "°C" in str(s) or "deg C" in str(s).lower()


def _f_to_c(s):
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*°F", str(s))
    return str(round((float(m.group(1)) - 32) * 5 / 9, 1)) if m else None


def _density_kgm3(s):
    """'0.7845 g/cu cm at 20 °C' → (kg/m3, temp_c)"""
    m = re.search(r"([\d.]+)\s*g/(?:cu\s*cm|cm3|cm³|ml|mL)", str(s))
    if m:
        kgm3 = round(float(m.group(1)) * 1000, 1)
        return str(kgm3), _temp_any_c(s)
    return None, None


def _vp_mbar(s):
    """'231 mm Hg at 25 °C' → (mbar, temp_c)"""
    m = re.search(r"([\d.]+)\s*(?:mm\s*Hg|mmHg)", str(s))
    if m:
        mbar = round(float(m.group(1)) * 1.33322, 1)
        return str(mbar), _temp_any_c(s)
    m = re.search(r"([\d.]+)\s*kPa", str(s))
    if m:
        return str(round(float(m.group(1)) * 10, 1)), _temp_any_c(s)
    return None, None


def _visc_cp(s):
    m = re.search(r"([\d.]+)\s*(?:cP|cp|mPa\.s)", str(s))
    if m:
        return str(m.group(1)), _temp_any_c(s)
    return None, None


def _kj_mol(s):
    m = re.search(r"(-?[\d.]+)\s*kJ/mol", str(s))
    return m.group(1) if m else None


def _ppm(s):
    m = re.search(r"([\d.]+)\s*(?:\[?ppm\]?|ppm)", str(s))
    return m.group(1) if m else None


def _percent(s):
    """'2.6%' / 'lower 2.6%' / '2.6 %' → 数值"""
    m = re.search(r"([\d.]+)\s*%", str(s))
    return m.group(1) if m else None


def _mg_kg(s):
    m = re.search(r"([\d.]+)\s*mg/kg", str(s))
    return m.group(1) if m else None


class Field:
    """一个字段的候选值集合 + 裁决。"""
    def __init__(self, key):
        self.key = key
        self.candidates = []  # list of dict(value, source, confidence, raw)

    def add(self, value, source, confidence, raw=""):
        if value in (None, ""):
            return
        v = str(value).strip()
        if not v:
            return
        # 去重：同值不同来源保留，但记录
        if not any(c["value"] == v for c in self.candidates):
            self.candidates.append({"value": v, "source": source, "confidence": confidence, "raw": raw})

    def best(self):
        """按优先级返回最终值。"""
        order = {"人工补采": 0, "PubChem": 1, "推导值": 2}
        cands = sorted(self.candidates, key=lambda c: order.get(c["source"], 9))
        return cands[0] if cands else None


class Merger:
    def __init__(self, schema):
        self.fields = {f["key"]: Field(f["key"]) for f in schema["fields"]}
        self.schema_fields = schema["fields"]
        self.by_col = {f["key"]: f["col"] for f in schema["fields"]}

    def set(self, key, value, source="PubChem", confidence="数据库汇总值", raw=""):
        if key in self.fields:
            self.fields[key].add(value, source, confidence, raw)

    # --- 物性映射 ---
    def map_identifiers(self, raw, supplement):
        ids = raw.get("identifiers", {})
        if raw.get("cas"):
            self.set("cas", raw["cas"], "PubChem", "数据库汇总值")
        self.set("formula", ids.get("MolecularFormula"), "PubChem", "数据库汇总值")
        if ids.get("MolecularWeight") is not None:
            self.set("mw", str(round(float(ids["MolecularWeight"]), 2)), "PubChem", "数据库汇总值")
        self.set("name_en", ids.get("IUPACName"), "PubChem", "数据库汇总值")
        # 中文名优先 supplement，其次输入
        sup = supplement.get("fields", {})
        self.set("name_cn", sup.get("name_cn", {}).get("value") if sup else None, "人工补采", "人工补充")

    def map_physical(self, raw):
        phy = raw.get("physical", {})

        # 熔沸点/闪点/自燃
        self._temp_field("mp", phy.get("melting_point", []))
        self._temp_field("bp", phy.get("boiling_point", []))
        self._flash(phy.get("flash_point", []))
        self._temp_field("autoignition", phy.get("autoignition", []))

        # 密度 → density_20/25
        for s in phy.get("density", []):
            kg, t = _density_kgm3(s)
            if kg:
                self.set(f"density_{t}" if t in ("20", "25") else "density_20", kg, "PubChem", "数据库汇总值", s)

        # 蒸气压 → vp_20/25/60
        for s in phy.get("vapor_pressure", []):
            mbar, t = _vp_mbar(s)
            if mbar:
                self.set(f"vp_{t}" if t in ("20", "25", "60") else "vp_25", mbar, "PubChem", "数据库汇总值", s)

        # 黏度 → visc_0/20/25/60
        for s in phy.get("viscosity", []):
            cp, t = _visc_cp(s)
            if cp:
                self.set(f"visc_{t}" if t in ("0", "20", "25", "60") else "visc_20", cp, "PubChem", "数据库汇总值", s)

        # 汽化热 / 燃烧热
        for s in phy.get("heat_of_vaporization", []):
            v = _kj_mol(s)
            if v:
                self.set("hvap", v, "PubChem", "数据库汇总值", s)
        for s in phy.get("heat_of_combustion", []):
            v = _kj_mol(s)
            if v:
                self.set("heat_combustion", v, "PubChem", "数据库汇总值", s)

        # 气味 / 检测阈值
        for s in phy.get("odor", []):
            self.set("odor", s, "PubChem", "数据库汇总值", s)
        for s in phy.get("odor_threshold", []):
            v = _ppm(s)
            if v:
                self.set("odor_threshold", v, "PubChem", "数据库汇总值", s)

        # 溶解度（水）
        for s in phy.get("solubility", []):
            if "water" in s.lower() or "miscible" in s.lower():
                self.set("sol_water", s, "PubChem", "数据库汇总值", s)

        # 20℃状态推导
        mp = self.fields["mp"].best()
        bp = self.fields["bp"].best()
        if mp and bp:
            try:
                m, b = float(mp["value"]), float(bp["value"])
                state = "固体" if m > 20 else ("气体" if b < 20 else "液体")
                self.set("state20", state, "推导值", "推导值")
            except ValueError:
                pass

    def _temp_field(self, key, cands):
        # 优先 °C，其次 °F 换算
        for s in cands:
            if _has_c(s):
                v = _temp_c(s)
                if v:
                    self.set(key, v, "PubChem", "数据库汇总值", s)
                    return
        for s in cands:
            v = _f_to_c(s)
            if v:
                self.set(key, v, "PubChem", "数据库汇总值", s)
                return

    def _flash(self, cands):
        closed, opened = None, None
        for s in cands:
            if "closed" in s.lower():
                closed = closed or (_temp_c(s) or _f_to_c(s))
            elif "open" in s.lower():
                opened = opened or (_temp_c(s) or _f_to_c(s))
            else:
                closed = closed or (_temp_c(s) or _f_to_c(s))
        if closed:
            self.set("fp_closed", closed, "PubChem", "数据库汇总值", cands[0] if cands else "")
        if opened:
            self.set("fp_open", opened, "PubChem", "数据库汇总值", cands[0] if cands else "")

    def map_flammability(self, raw):
        fl = raw.get("flammability", {})
        for s in fl.get("lel", []):
            v = _percent(s)
            if v:
                self.set("lel", v, "PubChem", "数据库汇总值", s)
                break
        for s in fl.get("uel", []):
            v = _percent(s)
            if v:
                self.set("uel", v, "PubChem", "数据库汇总值", s)
                break

    def map_ghs(self, raw):
        statements = raw.get("ghs", {}).get("hazard_statements", [])
        for st in statements:
            m = re.search(r"(H\d{3})", st)
            if not m:
                continue
            code = m.group(1)
            if code in HCODE_MAP:
                key, cat = HCODE_MAP[code]
                self.set(key, cat, "PubChem", "数据库汇总值", st)

    def map_nfpa(self, raw):
        nfpa = raw.get("nfpa", {})
        self.set("nfpa_health", nfpa.get("health"), "PubChem", "数据库汇总值")
        self.set("nfpa_flam", nfpa.get("fire"), "PubChem", "数据库汇总值")
        self.set("nfpa_react", nfpa.get("instability"), "PubChem", "数据库汇总值")
        self.set("nfpa_special", nfpa.get("special"), "PubChem", "数据库汇总值")
        # 文本兜底：形如 "N - ..."
        if not nfpa.get("health"):
            for t in nfpa.get("raw", []):
                m = re.match(r"^(\d)\s*-", t)
                if m:
                    self.set("nfpa_health", m.group(1), "PubChem", "数据库汇总值", t)
                    break

    def map_toxicity(self, raw):
        tox = raw.get("toxicity", {})
        # LD50 鼠经口
        for s in tox.get("ld50", []):
            if "rat" in s.lower() and "oral" in s.lower():
                v = _mg_kg(s)
                if v:
                    self.set("ld50_oral", v, "PubChem", "数据库汇总值", s)
                    break
        # LC50 鼠吸入
        for s in tox.get("lc50", []):
            if "rat" in s.lower():
                m = re.search(r"([\d.]+)\s*(?:mg/L|mg/m3|ppm)", s)
                if m:
                    self.set("lc50_inh", m.group(0), "PubChem", "数据库汇总值", s)
                    break

    def map_exposure(self, raw):
        exp = raw.get("exposure", {})
        # IDLH：单值，可解析
        for s in exp.get("idlh", []):
            v = _ppm(s)
            if v:
                self.set("idlh", v, "PubChem", "数据库汇总值", s)
                break
        # ERPG/AEGL/PAC/TEEL：多档 + 多时间窗，格式复杂，交由 Agent 补采精确值。
        # 原始文本已存 raw_*.json 的 exposure 节，Agent 据此构造 supplement。

    def apply_supplement(self, supplement):
        for key, entry in (supplement.get("fields", {})).items():
            if key in self.fields:
                self.set(key, entry.get("value"), "人工补采", "人工补充", entry.get("value", ""))

    def to_merged(self, raw, supplement):
        result = {"input": raw.get("input"), "cid": raw.get("cid"), "cas": raw.get("cas"),
                  "is_mixture": raw.get("is_mixture", False), "is_polymer": raw.get("is_polymer", False),
                  "fields": {}}
        for key, f in self.fields.items():
            result["fields"][key] = {
                "value": (f.best() or {}).get("value", ""),
                "source": (f.best() or {}).get("source", ""),
                "confidence": (f.best() or {}).get("confidence", ""),
                "candidates": f.candidates,
            }
        return result

    def to_final(self, merged):
        return {k: v["value"] for k, v in merged["fields"].items()}


def run_merge(out_dir):
    schema = load_schema()
    raw_files = glob.glob(os.path.join(out_dir, "raw_*.json"))
    if not raw_files:
        print(f"[merge] 未找到 raw_*.json，请先运行 search_web.py")
        sys.exit(1)

    for rf in sorted(raw_files):
        raw = json.load(open(rf, encoding="utf-8"))
        cas = raw.get("cas") or raw.get("cid")
        safe = str(cas).replace("/", "_").replace(" ", "_")
        sup_path = os.path.join(out_dir, f"supplement_{safe}.json")
        supplement = json.load(open(sup_path, encoding="utf-8")) if os.path.exists(sup_path) else {"fields": {}}

        m = Merger(schema)
        m.map_identifiers(raw, supplement)
        m.map_physical(raw)
        m.map_flammability(raw)
        m.map_ghs(raw)
        m.map_nfpa(raw)
        m.map_toxicity(raw)
        m.map_exposure(raw)
        m.apply_supplement(supplement)

        merged = m.to_merged(raw, supplement)
        final = m.to_final(merged)

        with open(os.path.join(out_dir, f"merged_{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)
        with open(os.path.join(out_dir, f"final_{safe}.json"), "w", encoding="utf-8") as f:
            json.dump(final, f, ensure_ascii=False, indent=2)

        n_filled = sum(1 for v in final.values() if v)
        print(f"[merge] {raw.get('input')} (CAS {cas}) → 已填 {n_filled}/105 字段")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="output")
    args = ap.parse_args()
    run_merge(args.out)


if __name__ == "__main__":
    main()
