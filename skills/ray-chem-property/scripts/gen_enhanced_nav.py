# -*- coding: utf-8 -*-
"""生成增强版导航 MD：缩写 + 英文名 + 中文名 + CAS + 同义词 + media_id。
输入：en_names.jsonl（abbr/en/media_id）+ cn_map_all.jsonl（abbr/cn）+ cas_results.jsonl（abbr/cas）
输出：CAMEO物性导航-增强版.md
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

def load_jsonl(path, key_field):
    d = {}
    if not os.path.exists(path):
        return d
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                o = json.loads(line)
                d[o.get(key_field)] = o
            except Exception:
                pass
    return d

def parse_intro(intro):
    """提取英文名 + 同义词（与 build_cameo_index.py 一致）。"""
    if not intro:
        return "", []
    s = re.sub(r"^[#\s]+", "", intro)
    head = s.split("#")[0].strip()
    name = re.sub(r"[A-Z]{3}$", "", head).strip()
    if not name:
        name = head
    syns = []
    m = re.search(r"Common Synonyms(.*?)(?:\||$)", intro, re.S)
    if m:
        raw = m.group(1).strip()
        if raw and len(raw) < 200:
            syns = [x.strip() for x in re.split(r"[;\n]+", raw) if x.strip()]
            if not syns:
                syns = [raw]
    return name, syns

def main():
    en_map = load_jsonl(os.path.join(HERE, "en_names.jsonl"), "abbr")
    cn_map = load_jsonl(os.path.join(HERE, "cn_map_all.jsonl"), "abbr")
    cas_map = load_jsonl(os.path.join(HERE, "cas_results.jsonl"), "abbr")

    # 从 page 文件拿 intro（en_names 里没有 intro）
    intro_map = {}
    for i in range(1, 28):
        fn = os.path.join(HERE, f"page_{i:02d}.jsonl")
        if not os.path.exists(fn):
            continue
        with open(fn, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        o = json.loads(line)
                        intro_map[o["title"].replace(".pdf", "")] = o.get("intro", "")
                    except Exception:
                        pass

    lines = [
        "# CAMEO 物性数据导航（增强版）",
        "",
        "本文件是「1-物性数据/CAMEO」文件夹（1306 个 CAMEO 化学品数据表）的索引，含中文名与 CAS。",
        "",
        "## 检索规则（Agent 专用）",
        "1. 用户给出中文名/英文名/CAS/缩写，先定位到下表对应行；",
        "2. 取该行的 media_id；",
        "3. 调 `mcp__ima-mcp__fetch_media_content`（media_id）精确读取该文件；",
        "4. 从内容解析 NFPA 704(8.5)/闪点(4.1)/自燃(4.7)/沸点(9.3)/密度(9.7)/蒸气压(9.25)/TLV(3.4) 等。",
        "",
        "| 缩写 | 英文名 | 中文名 | CAS | 同义词 | media_id |",
        "|------|--------|--------|-----|--------|----------|",
    ]

    n_cas = 0
    n_cn = 0
    for abbr in sorted(en_map.keys()):
        en = en_map[abbr].get("en", "")
        cn = cn_map.get(abbr, {}).get("cn", "") if abbr in cn_map else ""
        cas = cas_map.get(abbr, {}).get("cas", "") if abbr in cas_map else ""
        intro = intro_map.get(abbr, "")
        _, syns = parse_intro(intro)
        syn_str = " ".join(syns)[:80]
        media_id = en_map[abbr].get("media_id", "")
        if cas:
            n_cas += 1
        if cn:
            n_cn += 1
        lines.append(f"| {abbr} | {en} | {cn} | {cas} | {syn_str} | {media_id} |")

    out = os.path.join(HERE, "CAMEO物性导航-增强版.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[gen] 已生成 {len(en_map)} 条增强版导航 → {out}")
    print(f"[gen] 中文名覆盖 {n_cn}/{len(en_map)}（{n_cn/len(en_map)*100:.1f}%），CAS 覆盖 {n_cas}/{len(en_map)}（{n_cas/len(en_map)*100:.1f}%）")

if __name__ == "__main__":
    main()
