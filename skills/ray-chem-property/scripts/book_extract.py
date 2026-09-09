# -*- coding: utf-8 -*-
"""大部头物性书 → 按 CAS 索引的 JSON（方案 A：本地索引资产）。

解析《危险化学品安全技术全书》类 PDF（有文本层、按 GB/T 16483 的 16 大项编排）：

  条目标记: 紧邻「第一部分 化学品标识」前的独立行 = 化学品名（条目起始）
  CAS 锚点: 「第三部分 成分/组成信息」→ CASNo. 行
  理化字段: 「第九部分 理化特性」→ "字段名 值 (单位)" 同行逐行解析
  GHS/法规: 第二部分（危险性概述）/ 第十五部分（法规信息）抽取关键值

产出 data/<书名>-索引.json：
  {"<CAS>": {"name_cn": ..., "name_en": ..., "formula": ..., "mp": ..., "bp": ...,
             "fp": ..., "density": ..., "vp": ..., "autoignition": ...,
             "lel": ..., "uel": ..., "solubility": ..., "ph": ..., "ghs": [...], ...}}

用法:
  python book_extract.py "<PDF>" --output data/危险品全书-通用卷索引.json [--debug]
"""
import argparse
import json
import os
import re
import sys

try:
    import fitz  # PyMuPDF
except ImportError:
    print("需要 PyMuPDF: pip install pymupdf", file=sys.stderr)
    sys.exit(1)

# 理化字段: 书名用名 → skill 字段键（106 列模板的键）
PHYS_FIELDS = {
    "外观与性状": "appearance",
    "pH 值": "ph",
    "熔点(℃)": "mp",
    "沸点(℃)": "bp",
    "相对密度(水=1)": "density",
    "相对蒸气密度(空气=1)": "vd",
    "饱和蒸气压(kPa)": "vp",
    "燃烧热(kJ/mol)": "heat_of_combustion",
    "临界温度(℃)": "critical_temp",
    "临界压力(MPa)": "critical_pressure",
    "辛醇/水分配系数": "logkow",
    "闪点(℃)": "fp",
    "自燃温度(℃)": "autoignition",
    "爆炸下限(%)": "lel",
    "爆炸上限(%)": "uel",
    "分解温度(℃)": "decomposition_temp",
    "黏度(mPa·s)": "viscosity",
    "溶解性": "solubility",
}

CAS_RE = re.compile(r"\b(\d{2,7}-\d{2}-\d)\b")
SECTION_RE = re.compile(r"^第([一二三四五六七八九十]+)部分")


def cn_to_int(cn):
    m = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8,
         "九": 9, "十": 10, "十一": 11, "十二": 12, "十三": 13, "十四": 14, "十五": 15, "十六": 16}
    return m.get(cn, 0)


def clean(text):
    """去掉 PDF 文本的迷之空白，保留中文标点。"""
    return re.sub(r"\s+", "", text)


def parse_phys_line(line):
    """解析一行内可能含的多个 "字段名 值" 对（PDF 常把两个字段挤一行，
    如 "pH 值 无资料 熔点(℃) -95"）。返回 [(key, val), ...]。"""
    results = []
    hits = []  # [(idx, key, variant, len)] 所有字段名出现位置
    for name, key in PHYS_FIELDS.items():
        variants = [name]
        if name.replace(" ", "") != name:
            variants.append(name.replace(" ", ""))
        for variant in variants:
            idx = 0
            while True:
                idx = line.find(variant, idx)
                if idx == -1:
                    break
                hits.append((idx, key, variant))
                idx += len(variant)
    if not hits:
        return results
    hits.sort()
    # 同 idx 同 key 只保留最长变体（避免 "熔点(℃)" 与无空格变体重复）
    dedup = []
    for h in hits:
        if dedup and dedup[-1][0] == h[0] and dedup[-1][1] == h[1]:
            if len(h[2]) > len(dedup[-1][2]):
                dedup[-1] = h
            continue
        dedup.append(h)
    for i, (idx, key, variant) in enumerate(dedup):
        nxt = dedup[i + 1][0] if i + 1 < len(dedup) else len(line)
        val = line[idx + len(variant):nxt].strip()
        results.append((key, val))
    return results


class BookParser:
    def __init__(self, pdf_path, debug=False):
        self.doc = fitz.open(pdf_path)
        self.debug = debug

    def sections_of_page(self, page_idx):
        """返回该页从某索引开始命中的 (部分号, 行文本) 列表，用于状态机。"""
        t = self.doc[page_idx].get_text()
        lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
        out = []
        for ln in lines:
            m = SECTION_RE.match(ln)
            if m:
                out.append((cn_to_int(m.group(1)), ln, lines))
        return out

    def extract(self):
        records = []
        cur = None          # 当前累积的记录 dict
        cur_section = 0     # 当前行所属部分号（逐行状态机）
        pending_title = None  # 跨页待创建的条目标题（本页遇到'第一部分'前的预读）
        waiting_cas = False # 第三部分中：刚看到 CASNo. 标记，下一数据行即 CAS
        for pi in range(self.doc.page_count):
            t = self.doc[pi].get_text()
            lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
            for ln in lines:
                # A. 部分标记切换
                m = SECTION_RE.match(ln)
                if m and ('标识' in ln or '概述' in ln or '成分' in ln or '理化' in ln
                          or '稳定' in ln or '急救' in ln or '消防' in ln or '泄漏' in ln
                          or '操作' in ln or '接触' in ln or '毒理' in ln or '生态' in ln
                          or '废弃' in ln or '运输' in ln or '法规' in ln or '其他' in ln):
                    sec = cn_to_int(m.group(1))
                    # 「第一部分」→ 收尾旧条目，且其紧前一行是条目标题
                    if sec == 1:
                        if cur is not None:
                            if self.debug:
                                print(f"[book] 收尾: {cur.get('name_cn')} (P{pi + 1})")
                            records.append(cur)
                            cur = None
                        # 标题 = 本页「第一部分」行往前 3 行内的最后一行独立短行
                        cur_section = 1
                        waiting_cas = False
                        # 在 lines 里找当前行（第一部分）的索引
                        j = lines.index(ln)
                        cand = lines[max(0, j - 3):j]
                        if cand:
                            title = cand[-1].replace(" ", "")
                            if title not in ("参考文献", "免责声明") and len(title) <= 24:
                                cur = {"name_cn": title}
                                if self.debug:
                                    print(f"[book] 新条目: {title} (P{pi + 1})")
                        continue
                    cur_section = sec
                    if sec != 3:
                        waiting_cas = False
                    continue
                # B. 无部分标记的正常内容行
                if cur is None:
                    # 未进入任何条目：跳过（条目由「第一部分」行触发，标题行也在同页处理）
                    continue
                if cur_section == 1:
                    if ln.startswith("化学品中文名"):
                        cur["name_cn"] = ln.replace("化学品中文名", "").strip()
                    elif ln.startswith("化学品英文名"):
                        cur["name_en"] = ln.replace("化学品英文名", "").strip()
                    elif ln.startswith("分子式"):
                        s = ln.replace("分子式", "").strip()
                        cur["formula"] = s.split()[0] if s else ""
                    elif ln.startswith("相对分子质量"):
                        v = re.findall(r"[\d.]+", ln.replace("相对分子质量", ""))
                        if v:
                            cur["mw"] = v[0]
                    elif ln.startswith("化学品的推荐及限制"):
                        pass  # 结构式行噪声，忽略
                elif cur_section == 3:
                    # CAS 严格定位：CASNo. 标记后的第一个形如 CAS 的行
                    if "CASNo" in ln or "CAS No" in ln:
                        waiting_cas = True
                        continue
                    if waiting_cas:
                        cas_hit = CAS_RE.search(ln)
                        if cas_hit and "cas" not in cur:
                            cur["cas"] = cas_hit.group(1)
                            if self.debug:
                                print(f"  [{cur.get('name_cn','?')}] CAS={cas_hit.group(1)} (P{pi + 1})")
                            waiting_cas = False
                        elif not cas_hit:
                            # CASNo. 之后第一行可能不是 CAS（混合物的组分列），继续等
                            pass
                elif cur_section == 9:
                    for key, val in parse_phys_line(ln):
                        if val and val not in ("无资料", "无意义", "未确定"):
                            cur[key] = val
                elif cur_section == 14:
                    # 运输信息：UN号/运输名称/危险性类别/包装类别
                    if "联合国危险货物编号" in ln or "UN 号" in ln or "UN号" in ln:
                        m = re.search(r"(\d{4})", ln)
                        if m:
                            cur["un_number"] = m.group(1)
                    elif "联合国运输名称" in ln:
                        cur["un_name"] = ln.replace("联合国运输名称", "").strip()
                    elif "联合国危险性类别" in ln or "危险性类别" in ln:
                        m = re.search(r"([1-9](?:\.\d)?[A-Z]?)", ln)
                        if m:
                            cur["un_class"] = m.group(1)
                    elif "包装类别" in ln:
                        cur["un_packing"] = ln.replace("包装类别", "").strip()
        if cur is not None:
            records.append(cur)
        return records

    def close(self):
        self.doc.close()


def _looks_numeric(s):
    """看似数值（含 .(0.x) 精度后缀 / 负号 / 小数）。"""
    s = s.strip().strip(".")
    if not s:
        return False
    return bool(re.fullmatch(r"-?\d+\.?\d*(?:\([0-9.]+\))?", s))


def _assign_phys_value(cur, ln):
    """把物性列值分配到 mp/bp/density/nd/solubility（特征识别，容忍缺列）。

    CRC 数值惯例：mp/bp = 整数或带小数+精度后缀，如 -94.9(0.4)、56.08(0.07)；
    density = 6 位小数（如 0.784525）；nD = 6 位小数 1.3x-1.7x（如 1.358820）。"""
    s = ln.strip()
    # 密度/nD（6 位小数）优先：0.5~3.9 或 1.3~1.8 的六位小数
    if re.fullmatch(r"\d\.\d{6}", s) or re.fullmatch(r"\d\.\d{5}", s):
        v = float(s)
        if 1.3 <= v <= 1.8 and "nd" not in cur and "density" in cur:
            cur["nd"] = s
        else:
            cur["density"] = s
        return
    # 带精度后缀的数值 → mp/bp 候选（可能同行两个值：mp 与 bp 被 PDF 合并）
    m2 = re.fullmatch(r"(-?\d+\.?\d*)\(([0-9.]+)\)\s+(-?\d+\.?\d*)\(([0-9.]+)\)", s)
    if m2:
        v1, v2 = float(m2.group(1)), float(m2.group(3))
        p1, p2 = m2.group(2), m2.group(4)
        if "mp" not in cur:
            cur["mp"] = f"{m2.group(1)}({p1})"
            cur["bp"] = f"{m2.group(3)}({p2})"
        else:
            cur["bp"] = f"{m2.group(1)}({p1})"
            cur.setdefault("mw_extra", f"{m2.group(3)}({p2})")
        return
    m = re.fullmatch(r"(-?\d+\.?\d*)\(([0-9.]+)\)", s)
    if m:
        v = float(m.group(1))
        if "mp" not in cur and -300 <= v <= 600:
            cur["mp"] = s
        elif "bp" not in cur:
            cur["bp"] = s
        elif v < 0:
            cur["mp"] = s
        else:
            cur.setdefault("mw_extra", s)
        return
    # 简单数值（整数/1-3 位小数）
    if re.fullmatch(r"-?\d+\.?\d*", s):
        v = float(s)
        if "mp" not in cur and -300 <= v <= 600:
            cur["mp"] = s
        elif "bp" not in cur and -300 <= v <= 1200:
            cur["bp"] = s
        elif v < 0:
            cur["mp"] = s
        elif 1.3 <= v <= 1.7 and "nd" not in cur and "density" in cur:
            cur["nd"] = s
        elif 0.5 <= v <= 4.0 and "density" not in cur:
            cur["density"] = s
        else:
            cur.setdefault("mw_extra", s)
        return
    # 文本 → solubility 累加
    cur["solubility"] = cur.get("solubility", "") + (" " if cur.get("solubility") else "") + s


class CRCParser:
    """CRC Handbook of Chemistry and Physics 表格解析。

    Section 3/4 数据页特征: 表头含 "CAS RN" + "Mol. Form."。
    每行数据按列顺序逐 cell 一行输出:
      No. → Name → Synonym → Mol. Form. → CAS RN → Mol. Wt. → Phys. Form
      → mp/˚C → bp/˚C → den → nD → Solubility(可多行)
    行号(纯数字)是行开始锚点。分子结构式页(无表头)跳过。"""
    HEADER_MARKS = ("CAS RN", "Mol. Form.")

    # 列名 → 输出键
    COL_KEYS = None  # 延迟初始化（下面定义）

    def __init__(self, pdf_path, debug=False):
        self.doc = fitz.open(pdf_path)
        self.debug = debug
        self._col_keys = {
            "formula": "Mol. Form.", "cas": "CAS RN", "mw": "Mol. Wt.",
            "physical_form": "Physical Form", "mp": "mp/˚C", "bp": "bp/˚C",
            "density": "den", "nd": "nD", "solubility": "Solubility",
        }

    def _is_data_page(self, text):
        return "CAS RN" in text and "Mol. Form." in text

    def _parse_page(self, lines):
        """把一页的表头后行流解析为记录列表。返回 (records, 下一页待续状态)。"""
        # 定位表头结束：最后一个表头标记行之后
        head_end = 0
        for j, ln in enumerate(lines):
            if "CAS RN" in ln or "Mol. Form." in ln:
                head_end = j + 1
        if head_end == 0:
            return [], None
        data = lines[head_end:]
        records = []
        cur = None
        pending_sol = None  # 上一记录的溶解性续行
        i = 0
        while i < len(data):
            ln = data[i]
            # 行号锚点：纯数字
            if re.fullmatch(r"\d{1,4}", ln):
                if cur is not None:
                    # 上一行收尾
                    if cur.get("cas"):
                        records.append(cur)
                    elif self.debug:
                        print(f"[crc] 无CAS丢弃: {cur.get('name','')}")
                cur = {"no": ln}
                i += 1
                continue
            # 页脚页码（如 3-6）/ 书眉（Physical Constants…）跳过
            if re.fullmatch(r"\d+-\d+", ln) or "Physical Constants of" in ln or ln in ("Organic", "Inorganic", "No.", "Name", "Synonym"):
                i += 1
                continue
            if cur is None:
                i += 1
                continue
            # 分配列：前 6 列按序（Name/Synonym/Formula/CAS/MW/PhysForm 格式稳定），
            # 后 5 列用值特征识别（部分行缺 mp/bp 会错位，纯顺序不可靠）
            if "name" not in cur:
                cur["name"] = ln
            elif "synonym" not in cur:
                cur["synonym"] = ln if not _looks_numeric(ln) else "—"
            elif "formula" not in cur:
                cur["formula"] = ln
            elif "cas" not in cur:
                cur["cas"] = ln if CAS_RE.match(ln) else "—"
            elif "mw" not in cur:
                cur["mw"] = ln if _looks_numeric(ln) else "—"
            elif "physical_form" not in cur:
                if ln in ("cry", "liq", "lid", "gas", "sol", "cryst") or \
                   (re.match(r"^[a-z]{2,6}$", ln) and ln.startswith(("c","l")) and not _looks_numeric(ln)):
                    cur["physical_form"] = ln
                else:
                    # 不是物态（可能行缺列，直接是物性值）→ 不设 physical_form 继续物性分派
                    _assign_phys_value(cur, ln)
            else:
                _assign_phys_value(cur, ln)
            i += 1
        if cur is not None:
            if cur.get("cas"):
                records.append(cur)
        return records, None

    def extract(self):
        records = []
        for pi in range(self.doc.page_count):
            t = self.doc[pi].get_text()
            if not self._is_data_page(t):
                continue
            lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
            page_recs, _ = self._parse_page(lines)
            if self.debug and page_recs:
                print(f"[crc] P{pi+1}: {len(page_recs)} 条 (例: {page_recs[0].get('name','')} {page_recs[0].get('cas','')})")
            records.extend(page_recs)
        return records

    def close(self):
        self.doc.close()


class LangeParser:
    """Lange's Handbook of Chemistry (15th Ed) 表格解析。

    Table 1.15 Physical Constants of Organic Compounds（文本型 PDF）：
      No. → Name(可多行) → Formula → Weight → Beilstein → Density,g/mL
      → Refractive index → Melting point,°C → Boiling point,°C → Flash point,°C
      → Solubility(可多行)
    行号是"字母+数字"（o11/o12/a290），是行开始锚点。"""

    ROW_NO_RE = re.compile(r"^[a-z]{1,3}\d{1,4}$")

    def __init__(self, pdf_path, debug=False):
        self.doc = fitz.open(pdf_path)
        self.debug = debug

    def _is_data_page(self, text):
        return "Physical Constants of Organic" in text and "Melting" in text and "Boiling" in text

    def _parse_page(self, lines):
        # 表头结束：末个 "parts solvent" 或 "No." 之后
        head_end = 0
        for j, ln in enumerate(lines):
            if "parts solvent" in ln or ln in ("No.", "Name", "Formula", "Beilstein"):
                head_end = j + 1
        if head_end == 0:
            return [], None
        data = lines[head_end:]
        records = []
        cur = None
        i = 0
        while i < len(data):
            ln = data[i]
            # 行号锚点：字母+数字（o11, a290, al01…）
            if self.ROW_NO_RE.match(ln):
                if cur is not None and cur.get("name"):
                    if self.debug:
                        print(f"[lange] {cur.get('no')} {cur.get('name','')[:28]} → mp={cur.get('mp')} bp={cur.get('bp')} den={cur.get('density')}")
                    records.append(cur)
                cur = {"no": ln}
                i += 1
                continue
            # 页眉页码（如 3-6 / 2.67 书眉顶部）/ 书眉/表格标题 / 表头词跳过
            if re.fullmatch(r"\d+-\d+", ln) or "TABLE" in ln or "Physical Constants" in ln \
               or ln in ("(Continued)", "No.", "Name", "Formula", "Beilstein", "reference"):
                i += 1
                continue
            if cur is None:
                i += 1
                continue
            # 分配列：Name(多行) → Formula → MW → Beilstein → 物性区（复用 _assign_phys_value 特征识别）
            if "name" not in cur:
                cur["name"] = ln
            elif "formula" not in cur:
                if _looks_formula(ln):
                    cur["formula"] = ln
                elif _looks_numeric(ln):
                    cur["mw"] = ln
                    cur.setdefault("formula", "—")
                elif re.fullmatch(r"[\d,\s]+", ln):
                    cur["beilstein"] = ln
                    cur.setdefault("formula", "—")
                else:
                    if "=" in ln or "≡" in ln or re.search(r"[A-Z][a-z]?\d", ln) or "(" in ln:
                        cur["formula"] = ln
                    else:
                        cur["name"] = cur["name"] + " " + ln
            elif "mw" not in cur:
                if _looks_numeric(ln):
                    cur["mw"] = ln
                elif re.fullmatch(r"[\d,\s]+", ln):
                    cur["beilstein"] = ln
                else:
                    cur.setdefault("mw", "—")
            elif "beilstein" not in cur:
                if re.fullmatch(r"[\d,\s]+", ln):
                    cur["beilstein"] = ln
                elif _looks_numeric(ln) and cur.get("mw", "—") == "—":
                    cur["mw"] = ln
                else:
                    cur.setdefault("beilstein", "—")
            elif "mw" not in cur and _looks_numeric(ln):
                cur["mw"] = ln
            else:
                # 物性区：Lange 专用特征识别（密度 5-6 位小数、nD 1.3-1.8、温度上标跳过）
                _assign_lange_phys(cur, ln)
            i += 1
        if cur is not None and cur.get("name"):
            records.append(cur)
        return records, None

    def extract(self):
        records = []
        for pi in range(self.doc.page_count):
            t = self.doc[pi].get_text()
            if not self._is_data_page(t):
                continue
            lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
            page_recs, _ = self._parse_page(lines)
            records.extend(page_recs)
        return records

    def close(self):
        self.doc.close()


class PerryParser:
    """Perry's Chemical Engineers' Handbook (8th) Critical Constants 表解析。

    TABLE 2-141 Critical Constants and Acentric Factors（含 CAS 的行式表）：
      Cmpd.no → Name → Formula → CAS no. → Mol.wt → Tc,K → Pc,MPa → Vc,m3/kmol → Zc → Acentric factor
    行号（纯数字）是行锚点。表头特征 "CAS no."，页特征 "Critical Constants"。"""

    ROW_NO_RE = re.compile(r"^\d{1,4}$")

    def __init__(self, pdf_path, debug=False):
        self.doc = fitz.open(pdf_path)
        self.debug = debug

    def _is_critical_table(self, text):
        return ("Critical Constants" in text or "Critical constants" in text) and "CAS no." in text

    def _parse_page(self, lines):
        # 表头结束：最后一个 "factor" 或 "Zc" 表头行之后
        head_end = 0
        for j, ln in enumerate(lines):
            if ln in ("factor", "Zc", "CAS no.", "Mol. wt."):
                head_end = j + 1
        if head_end == 0:
            return [], None
        data = lines[head_end:]
        records = []
        cur = None
        i = 0
        while i < len(data):
            ln = data[i]
            # 行号锚点：纯数字，且【后一行是名称开头】（避免物性值如 Tc=514 被误当行号）
            if self.ROW_NO_RE.match(ln) and i + 1 < len(data) and \
               re.match(r"[A-Za-z]", data[i + 1]) and not CAS_RE.match(data[i + 1]):
                if cur is not None and cur.get("name"):
                    if self.debug:
                        print(f"[perry] {cur.get('no')} {cur.get('name','')[:26]} → CAS={cur.get('cas')} Tc={cur.get('tc')}")
                    records.append(cur)
                cur = {"no": ln}
                i += 1
                continue
            if re.fullmatch(r"\d+-\d+", ln) or "TABLE" in ln or "Critical Constants" in ln \
               or ln in ("CRITICAL CONSTANTS", "(Continued)", "Cmpd.", "Name", "Formula", "CAS no."):
                i += 1
                continue
            if cur is None:
                i += 1
                continue
            # 分配列：Name→Formula→CAS→MW→Tc→Pc→Vc→Zc→factor（数值列用特征）
            if "name" not in cur:
                cur["name"] = ln
            elif "formula" not in cur:
                if _looks_formula(ln):
                    cur["formula"] = ln
                elif CAS_RE.match(ln):
                    cur["cas"] = ln
                    cur.setdefault("formula", "—")
                else:
                    cur["name"] = cur["name"] + " " + ln
            elif "cas" not in cur:
                cur["cas"] = ln if CAS_RE.match(ln) else "—"
            elif "mw" not in cur:
                cur["mw"] = ln if _looks_numeric(ln) else "—"
            elif "tc" not in cur:
                cur["tc"] = ln if _looks_numeric(ln) else "—"
            elif "pc" not in cur:
                cur["pc"] = ln if _looks_numeric(ln) else "—"
            elif "vc" not in cur:
                cur["vc"] = ln if _looks_numeric(ln) else "—"
            elif "zc" not in cur:
                cur["zc"] = ln if _looks_numeric(ln) else "—"
            elif "acentric" not in cur:
                cur["acentric"] = ln if _looks_numeric(ln) else "—"
            i += 1
        if cur is not None and cur.get("name"):
            records.append(cur)
        return records, None

    def extract(self):
        records = []
        for pi in range(self.doc.page_count):
            t = self.doc[pi].get_text()
            if not self._is_critical_table(t):
                continue
            lines = [ln.strip() for ln in t.split("\n") if ln.strip()]
            page_recs, _ = self._parse_page(lines)
            records.extend(page_recs)
        return records

    def close(self):
        self.doc.close()


def _looks_lange_temp(s):
    """Lange 温度值：如 44-45 / 288100mm / -95 / 13–19 / 61-43mmHg / 5.5。"""
    s = s.replace(" ", "")
    if re.fullmatch(r"-?\d+\.?\d*(?:[–—-]\d+\.?\d*)?", s):
        return True
    if re.fullmatch(r"-?\d+[a-zA-Z°]*", s):
        return True
    return False


def _looks_formula(s):
    """公式/结构式特征：含元素符号+数字（C2H6O、[(CH3)2CH]2O）或结构标记。排除 Beilstein（纯数字逗号）。"""
    if re.fullmatch(r"[\d,\s]+", s):
        return False
    if "C" in s or "H" in s or "O" in s or "N" in s or "S" in s or "Cl" in s or "Br" in s:
        if re.search(r"[A-Z][a-z]?\d", s) or "=" in s or "≡" in s or "(" in s or ")" in s:
            return True
    return False


def _assign_lange_phys(cur, ln):
    """Lange 物性区特征识别（不能复用 CRC 的——Lange 密度为 5 位小数、温度上标干扰）。

    列序：Density(g/mL, 5-6位小数) → nD(1.3-1.8, 6位小数) → mp → bp → fp → Solubility
    温度上标：1-3 位纯数字排在两个小数之间时为密度/nD 的测量温度，跳过。"""
    s = ln.strip()
    # 密度/nD：5-6 位小数
    if re.fullmatch(r"\d\.\d{5,6}", s):
        v = float(s)
        if 1.3 <= v <= 1.8 and "nd" not in cur and "density" not in cur:
            cur["nd"] = s
        elif 0.5 <= v <= 4.0 and "density" not in cur:
            cur["density"] = s
        elif 1.3 <= v <= 1.8 and "density" in cur and "nd" not in cur:
            cur["nd"] = s
        elif v >= 4.0:  # 高密度固体，也是密度
            cur["density"] = s
        else:
            cur.setdefault("density", s)
        return
    # 温度上标：1-3 位纯数字，若已见密度/nd 则跳过（它不是 mp/bp）
    if re.fullmatch(r"\d{1,3}", s) and ("density" in cur or "nd" in cur):
        if "density" in cur and "nd" not in cur:
            cur.setdefault("temp_density", s)   # 密度测量温度上标
        return
    # 温度值：mp/bp/fp（含空格/±/范围/上标单位如 100mm）
    if _looks_lange_temp(s):
        if "mp" not in cur:
            cur["mp"] = s
        elif "bp" not in cur and _is_bp_like(s):
            cur["bp"] = s
        elif "fp" not in cur and ("fp" not in cur):
            cur["fp"] = s
        return
    # 带压力后缀的沸点（如 288100mm / 61-43mmHg）
    if re.search(r"\d+(mm|mmHg|torr)", s.replace(" ", "")):
        if "bp" not in cur:
            cur["bp"] = s
        elif "fp" not in cur:
            cur["fp"] = s
        return
    # 文本 → solubility
    cur["solubility"] = cur.get("solubility", "") + (" " if cur.get("solubility") else "") + s


def _is_bp_like(s):
    """判断是否更像沸点（大值或有压力后缀）而非熔点。"""
    s2 = s.replace(" ", "")
    m = re.fullmatch(r"-?\d+(?:[–—-]\d+)?", s2)
    if m:
        vals = [float(x) for x in re.findall(r"-?\d+", s2)]
        return max(vals) > 100 or len(vals) >= 2
    return "mm" in s2 or "torr" in s2 or "mmHg" in s2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--output", required=True)
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--format", default="auto", choices=["auto", "chs", "crc", "lange", "perry"],
                    help="auto=自动识别; chs=危险品安全技术全书; crc=CRC手册表格; lange=兰氏手册15版(文本型); perry=Perry手册临界常数表")
    args = ap.parse_args()

    # 自动识别
    fmt = args.format
    if fmt == "auto":
        head = os.path.basename(args.pdf).upper()
        if "LANG" in head or "兰氏" in os.path.basename(args.pdf):
            fmt = "lange"
        elif "PERRY" in head or "化工工艺设计手册" in os.path.basename(args.pdf):
            fmt = "perry"
        elif "CRC" in head or "HANDBOOK" in head:
            fmt = "crc"
        else:
            fmt = "chs"

    if fmt == "crc":
        parser = CRCParser(args.pdf, debug=args.debug)
    elif fmt == "lange":
        parser = LangeParser(args.pdf, debug=args.debug)
    elif fmt == "perry":
        parser = PerryParser(args.pdf, debug=args.debug)
    else:
        parser = BookParser(args.pdf, debug=args.debug)
    records = parser.extract()
    parser.close()

    # 组装索引：有 CAS → dict{CAS: 记录}；无 CAS（如兰氏）→ list[记录]+"_nocas" 键，保留全部
    with_cas = [r for r in records if r.get("cas")]
    no_cas = [r for r in records if not r.get("cas")]
    if with_cas:
        index = {r["cas"]: r for r in with_cas}
        if no_cas:
            index["_nocas"] = no_cas
    else:
        index = {"_nocas": no_cas}
    # 修正：检索引擎期望 CAS 键 dict；无 CAS 时也输出 list 由调用方决定
    if no_cas and not with_cas:
        index = no_cas  # 纯 list（兰氏/类似无 CAS 表）
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    n_full = len(with_cas)
    print(f"[book] 提取条目 {len(records)} 条，含 CAS {n_full} 条，无CAS {len(no_cas)} 条 → {args.output}")


if __name__ == "__main__":
    main()