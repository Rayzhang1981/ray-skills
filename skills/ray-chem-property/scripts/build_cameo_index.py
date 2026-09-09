# -*- coding: utf-8 -*-
"""把 CAMEO 文件夹的文件清单（get_knowledge_list 逐页收集）汇总成「导航 MD」。

用法：
  Agent 用 mcp__ima-mcp__get_knowledge_list 遍历 CAMEO 文件夹（folder_id=folder_7455529366471323），
  每页把 knowledge_list 追加保存到 <out>/cameo_pages.jsonl（每行一个 JSON 对象，字段 title/introduction/media_id）。
  全部 1306 条收集完后运行本脚本：
    python build_cameo_index.py --pages cameo_pages.jsonl --out CAMEO物性导航.md

导航 MD 用于上传回 IMA「1-物性数据」文件夹，让语义检索能稳定命中 → 定位 media_id → fetch_media_content 精确读取。
"""
import argparse
import json
import re


def parse_intro(intro):
    """从 CAMEO 文件 introduction 里提取英文名 + 同义词。

    introduction 格式形如：
      "ACETONEACT#   CAUTIONARY RESPONSE INFORMATION|Common SynonymsDimethyl ketonePropanone2-Propanone|Watery liquid|..."
    第一段（# 前）是「英文名+缩写」；Common Synonyms 后到下一个 | 之间是同义词。
    """
    if not intro:
        return "", []
    # 去掉开头的 # 与空白噪声（部分文件 OCR 后带 "#   " 前缀）
    s = re.sub(r"^[#\s]+", "", intro)
    # 英文名：取第一个 # 之前（形如 "ACETONEACT"），末尾 3 字母是缩写，前面是英文名
    head = s.split("#")[0].strip()
    name = re.sub(r"[A-Z]{3}$", "", head).strip()
    if not name:
        name = head
    # 同义词：Common Synonyms 之后的第一个单元格
    syns = []
    m = re.search(r"Common Synonyms(.*?)(?:\||$)", intro, re.S)
    if m:
        # 同义词之间无分隔符，通常是连写；按大写字母边界切分是近似法，这里只做粗提取
        raw = m.group(1).strip()
        if raw and len(raw) < 200:
            # 按常见分隔拆分，否则整段作为一条
            syns = [s.strip() for s in re.split(r"[;\n]+", raw) if s.strip()]
            if not syns:
                syns = [raw]
    return name, syns


def load_pages(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            # 兼容两种结构：直接是 item，或包在 knowledge_list 里
            items = obj.get("knowledge_list", [obj])
            for it in items:
                rows.append({
                    "title": it.get("title", ""),
                    # 兼容两种字段名：intro（Agent 落盘用）与 introduction（MCP 原始返回）
                    "intro": it.get("intro", "") or it.get("introduction", ""),
                    "media_id": it.get("media_id", ""),
                })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", required=True, help="cameo_pages.jsonl 文件")
    ap.add_argument("--out", default="CAMEO物性导航.md")
    args = ap.parse_args()

    rows = load_pages(args.pages)
    lines = [
        "# CAMEO 物性数据导航",
        "",
        "本文件是「1-物性数据/CAMEO」文件夹（1306 个 CAMEO 化学品数据表）的索引。",
        "",
        "## 检索规则（Agent 专用）",
        "1. 用户给出中文名/英文名/CAS/缩写，先定位到下表对应行；",
        "2. 取该行的 media_id；",
        "3. 调 `mcp__ima-mcp__fetch_media_content`（media_id）精确读取该文件；",
        "4. 从内容解析 NFPA 704(8.5)/闪点(4.1)/自燃(4.7)/沸点(9.3)/密度(9.7)/蒸气压(9.25)/TLV(3.4) 等。",
        "",
        "| 缩写 | 英文名 | 同义词 | media_id |",
        "|------|--------|--------|----------|",
    ]
    for r in sorted(rows, key=lambda x: x["title"]):
        name, syns = parse_intro(r["intro"])
        syn_str = " ".join(syns)[:80]
        lines.append(f"| {r['title'].replace('.pdf','')} | {name} | {syn_str} | {r['media_id']} |")

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"[build] 已生成 {len(rows)} 条索引 → {args.out}")


if __name__ == "__main__":
    main()
