# -*- coding: utf-8 -*-
"""Step 1b — IMA 化工工艺数据库检索 + 补充数据规范化。

IMA 检索由 Agent 通过 MCP 工具 `mcp__ima-mcp__search_knowledge` 完成（脚本无法直连 MCP）。
本脚本负责两件事：
  1) 打印 IMA 检索规范（KB ID / 关键词策略 / 结果格式），供 Agent 参考；
  2) 把 Agent 手工补采的字段值（WebFetch chemicalbook/NIST/CAMEO/whpdj 或 IMA 结果）规范化
     为 <out>/supplement_{cas}.json，字段键按 field_schema.json 校验。

用法：
  python search_ima.py --guide                     # 打印 IMA 检索指引
  python search_ima.py --cas 67-64-1 --json 补采.json --out output   # 规范化补采数据

补采 JSON 格式（字段键见 field_schema.json）：
  {"cas": "67-64-1", "fields": {"odor": "甜、水果味", "fp_closed": "-20", "fire_class": "甲B"}}
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "field_schema.json")

GUIDE = """\
========== IMA 化工工艺数据库 检索指引 ==========
- 知识库：Ray谈化工「化工工艺数据库」
  KB ID：7410596022594182
  分享链接：https://ima.qq.com/wiki/?shareId=5a0b01041d935139413c9758eb0cd5c319b2e8817f722883cc6c5afc8a5101bf

【重点检索目录】1-物性数据 文件夹：
  folder_id = folder_7411216628582850（16 文件 + 6 子文件夹）
  内含权威物性源：
    · CAMEO 数据库（子文件夹 folder_7455529366471323，1306 文件）→ NFPA/闪点/ERPG/反应性
    · 化学化工物性数据手册 有机卷/无机卷（刘光启主编）→ 熔点/沸点/密度/蒸气压/焓
    · CRC Handbook / 兰氏化学手册 / 石油化工基础数据手册
    · Bretherick 反应性化学危害手册 / 气液物性估算手册(Poling)
    · TDG 危险货物运输建议书 / 化工物性算图手册

- MCP 检索（重点搜物性数据文件夹）：
    mcp__ima-mcp__search_knowledge
    参数：knowledge_base_id="7410596022594182",
          folder_id="folder_7411216628582850",   ← 限定在 1-物性数据
          query="<CAS号 或 英文名 + 物性限定词>"

- 列文件夹/子文件夹（找具体文件）：
    mcp__ima-mcp__get_knowledge_list
    参数：knowledge_base_id="7410596022594182", folder_id="<文件夹id>", limit=50

- 关键词策略：`CAS号 + 物性`（如 "105-64-6 flash point"）＞ `英文名 + 物性`（CAMEO 是英文）
  ＞ `中文名 + 物性`（化学化工物性手册是中文）；避免纯中文泛化词（100+ 条溢出）

- 【精确文件定位】CAMEO 文件是 3 字母缩写（CMH=异丙苯过氧化氢、BHP=叔丁基过氧化氢、ACT=丙酮、
  VCM=氯乙烯），搜英文名可命中（highlight 高亮化学品名），但 folder_id 不严格限定、结果排序靠后。
  定位到 CAMEO 文件后，用 `mcp__ima-mcp__fetch_media_content`（media_id）精确读取，
  从内容解析：NFPA 704(8.5节)/闪点(4.1)/自燃(4.7)/沸点(9.3)/密度(9.7)/蒸气压(9.25)/TLV(3.4)/MOCC(4.14)。
  批量建索引：Agent 用 get_knowledge_list 分页收集 → scripts/build_cameo_index.py 生成导航 MD → 上传 IMA。

- 结果过大（>10 万字符）自动落盘 tool-results/，用 Python 提取 title 快速筛选

- IMA 定位：权威物性手册「佐证/补白」+ 标准全文（GB 30000 分类阈值）+ 法规名录判定依据；
  精确查表仍以 PubChem（结构化）+ chemicalbook（中文）为主。
================================================
"""


def load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--guide", action="store_true", help="打印 IMA 检索指引")
    ap.add_argument("--cas", help="CAS 号（用于输出文件名）")
    ap.add_argument("--json", dest="json_in", help="补采字段 JSON 文件")
    ap.add_argument("--out", default="output")
    args = ap.parse_args()

    if args.guide:
        print(GUIDE)
        return

    if not args.json_in:
        print(GUIDE)
        print("未提供 --json，仅打印指引。补采数据请构造 JSON 后传入。")
        return

    schema = load_schema()
    valid_keys = {f["key"] for f in schema["fields"]}

    data = json.load(open(args.json_in, encoding="utf-8"))
    fields = data.get("fields", data if isinstance(data, dict) else {})
    normalized = {}
    for k, v in fields.items():
        if k not in valid_keys:
            print(f"  [warn] 忽略未知字段键 '{k}'")
            continue
        normalized[k] = {"value": str(v), "source": "IMA/人工补采", "confidence": "人工补充"}

    cas = args.cas or data.get("cas") or "supplement"
    safe = str(cas).replace("/", "_").replace(" ", "_")
    out_path = os.path.join(args.out, f"supplement_{safe}.json")
    os.makedirs(args.out, exist_ok=True)
    payload = {"cas": cas, "fields": normalized}
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"[supplement] {len(normalized)} 个字段已规范化 → {out_path}")


if __name__ == "__main__":
    main()
