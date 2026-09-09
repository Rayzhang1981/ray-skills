# -*- coding: utf-8 -*-
"""《危险化学品安全技术全书》通用卷 应急段提取 → data/应急准则索引.json

从 2094 页 PDF 中按 CAS 键提取每条物料的应急相关段落：
  - 第四部分 急救措施        → emergency (first_aid)
  - 第五部分 消防措施        → fire
  - 第六部分 泄漏应急处理    → spill
  - 第七部分 操作处置与储存  → handling_storage

提取策略（与 book_extract.py 状态机一致）:
  条目触发 = 「第一部分 化学品标识」紧前独立短行；
  CAS      = 第三部分 CASNo. 标记后首个 CAS 格式串；
  第四~七部分按「第N部分」切换，段内以子字段锚点切分、PDF 硬换行拼接成完整段落。

坑位防御:
  - 页眉品名行 / 竖排页码数字 / 参考文献噪声 → 过滤
  - "无资料/无意义" 段落 → 跳过不写（缺失≠无害）
  - 产出 JSON 必扫 \ufffd

用法:
  python build_emergency_index.py "<PDF路径>" [--output ../data/应急准则索引.json] [--limit N] [--debug]
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

SECTION_RE = re.compile(r"^第([一二三四五六七八九十]+)部分")
CAS_RE = re.compile(r"\b(\d{2,7}-\d{2}-\d)\b")

CN_NUM = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8,
          "九": 9, "十": 10}

# 目标章节: 部分号 → 值键
TARGET_SECTIONS = {4: "first_aid", 5: "fire", 6: "spill", 7: "handling_storage"}

# 子字段锚点（段落起始标记），按书中实际文本。命中即开启新子段。
SUBFIELD_MARKS = {
    "first_aid": ["吸入", "皮肤接触", "眼睛接触", "食入", "对保护施救者的忠告",
                  "对医生的特别提示"],
    "fire": ["灭火剂", "特别危险性", "灭火注意事项及防护措施"],
    "spill": ["作业人员防护措施", "环境保护措施",
              "泄漏化学品的收容、清除方法及所使用的处置材料"],
    "handling_storage": ["操作注意事项", "储存注意事项"],
}

NO_DATA_PAT = re.compile(r"^(无资料|无意义|无|未制定标准?|/)$")


def clean_join(text):
    """把 PDF 硬换行拆碎的段落拼回一句话（中文拼接去空格；标点后去多余空白）。"""
    s = text.replace("\n", "")
    s = re.sub(r"\s+", "", s)
    return s.strip()


def is_noise(line):
    """过滤页码碎片（纯数字1-3位）/孤立标点等页眉页脚噪声。"""
    t = line.strip()
    if not t:
        return True
    if re.fullmatch(r"\d{1,4}", t):
        return True
    return False


def split_subfields(raw_text, vkey):
    """把整章原文按子字段锚点切成 dict。返回 {} 表示该章整体无有效内容。"""
    # 先把全文合成一整串，再按锚点分割（锚点必出现于串中）
    joined = clean_join(raw_text)
    marks = SUBFIELD_MARKS.get(vkey, [])
    positions = []
    for m in marks:
        idx = 0
        while True:
            i = joined.find(m, idx)
            if i == -1:
                break
            positions.append((i, m))
            idx = i + len(m)
    if not positions:
        # 整章没有已知锚点：若内容非"无资料"，作为 unknown 整体返回
        if joined and not NO_DATA_PAT.match(joined):
            return {"_full": joined}
        return {}
    positions.sort()
    # 同位置只留最长锚点
    dedup = []
    for p in positions:
        if dedup and dedup[-1][0] == p[0]:
            if len(p[1]) > len(dedup[-1][1]):
                dedup[-1] = p
            continue
        dedup.append(p)
    out = {}
    for i, (pos, mark) in enumerate(dedup):
        end = dedup[i + 1][0] if i + 1 < len(dedup) else len(joined)
        seg = joined[pos + len(mark):end]
        if seg and not NO_DATA_PAT.match(seg):
            out[mark] = seg
    return out


def main():
    ap = argparse.ArgumentParser(description="危险品全书应急段提取")
    ap.add_argument("pdf", help="通用卷 PDF 路径")
    ap.add_argument("--output", default=os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                     "..", "data", "应急准则索引.json"))
    ap.add_argument("--limit", type=int, default=0, help="调试用：只处理前 N 页")
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args()

    doc = fitz.open(args.pdf)
    records = []
    cur = None            # 当前记录 {"name_cn":..., "cas":..., values...}
    cur_section = 0
    sec_buf = []          # 当前目标章节的原始行缓冲
    waiting_cas = False
    pending_title = None  # 「第一部分」前一行标题跨页暂存

    def close_current():
        nonlocal cur, sec_buf
        if cur is None:
            sec_buf = []
            return
        cas = cur.get("cas")
        vals = {}
        for vkey, buf in sec_buf_map.items():
            txt = "\n".join(buf)
            sub = split_subfields(txt, vkey)
            if sub:
                vals[vkey] = sub
        if cas:
            rec = {"name_cn": cur.get("name_cn", "")}
            rec.update(vals)
            records.append(rec)
        cur = None
        sec_buf = []

    # 用一个 dict 让 close_current 能访问多个缓冲
    sec_buf_map = {v: [] for v in TARGET_SECTIONS.values()}

    for pi in range(doc.page_count):
        if args.limit and pi >= args.limit:
            break
        t = doc[pi].get_text()
        lines = [ln.rstrip() for ln in t.split("\n")]
        stripped_lines = [ln.strip() for ln in lines]
        page_texts = [ln for ln in stripped_lines if ln]
        for si, raw in enumerate(lines):
            ln = raw.strip()
            m = SECTION_RE.match(ln) if ln else None
            is_section = bool(m and ('标识' in ln or '概述' in ln or '成分' in ln or '理化' in ln
                                     or '稳定' in ln or '急救' in ln or '消防' in ln or '泄漏' in ln
                                     or '操作' in ln or '接触' in ln or '毒理' in ln or '生态' in ln
                                     or '废弃' in ln or '运输' in ln or '法规' in ln or '其他' in ln))
            if is_section:
                sec_num = CN_NUM.get(m.group(1), 0)
                if sec_num == 1:
                    # 收尾旧条目
                    _flush_entry(records, cur, sec_buf_map)
                    cur = None
                    sec_buf_map = {v: [] for v in TARGET_SECTIONS.values()}
                    # 条目标题 = 本页「第一部分」行往前 3 行内最后一独立短行
                    j = page_texts.index(ln) if ln in page_texts else None
                    cand = [x for x in page_texts[max(0, (page_texts.index(ln) if ln in page_texts else 0) - 3):page_texts.index(ln)]]
                    if cand:
                        title = cand[-1].replace(" ", "")
                        if title not in ("参考文献", "免责声明") and len(title) <= 24:
                            cur = {"name_cn": title}
                            if args.debug:
                                print(f"[emg] 新条目: {title} (P{pi+1})")
                    cur_section = 1
                    continue
                # 其它部分切换：若正处目标段，先终结缓冲（但不要 flush 掉 cur）
                cur_section = sec_num
                continue
            # ---- 非部分标记行 ----
            if cur is None:
                continue
            if cur_section == 3:
                if "CASNo" in ln or "CAS No" in ln:
                    waiting_cas = True
                    continue
                if waiting_cas and "cas" not in cur:
                    hit = CAS_RE.search(ln)
                    if hit:
                        cur["cas"] = hit.group(1)
                        if args.debug:
                            print(f"  [{cur['name_cn']}] CAS={cur['cas']} (P{pi+1})")
                continue
            if cur_section in TARGET_SECTIONS:
                if is_noise(ln):
                    continue
                sec_buf_map[TARGET_SECTIONS[cur_section]].append(ln)
            # 其余部分忽略
    # 收尾最后一条
    _flush_entry(records, cur, sec_buf_map)

    index = {}
    dup = 0
    for r in records:
        cas = r.pop("cas", None)
        if not cas:
            continue
        name = r.get("name_cn", "")
        if cas in index:
            dup += 1
            # 保留字段更多的那条
            old_fields = sum(len(v) for v in index[cas].values() if isinstance(v, dict))
            new_fields = sum(len(v) for v in r.values() if isinstance(v, dict))
            if new_fields > old_fields:
                index[cas] = r
            continue
        index[cas] = r

    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)

    n_first = sum(1 for v in index.values() if v.get("first_aid"))
    n_fire = sum(1 for v in index.values() if v.get("fire"))
    n_spill = sum(1 for v in index.values() if v.get("spill"))
    n_hs = sum(1 for v in index.values() if v.get("handling_storage")
               or (v.get("first_aid") or v.get("fire") or v.get("spill")))
    print(f"[emg] 提取完成: {len(index)} CAS 记录（重复CAS {dup} 个保留字段最全者）")
    print(f"[emg] first_aid 覆盖 {n_first}, fire {n_fire}, spill {n_spill}")
    print(f"[emg] 输出: {os.path.abspath(args.output)}")
    doc.close()


def _flush_entry(records, cur, sec_buf_map):
    """把当前条目的各章缓冲解析成子字段 dict 并入 records（仅当有 CAS）。"""
    if cur is None:
        return
    cas = cur.get("cas")
    if not cas:
        return
    rec = {"name_cn": cur.get("name_cn", ""), "cas": cas}
    for vkey, buf in sec_buf_map.items():
        txt = "\n".join(buf)
        sub = split_subfields(txt, vkey)
        if sub:
            rec[vkey] = sub
    records.append(rec)


if __name__ == "__main__":
    main()
