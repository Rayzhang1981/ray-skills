# CAMEO 导航文件构建全流程（让 IMA 物性库精确查表）

> 2026-08-15 实测跑通。核心目标：把 IMA「1-物性数据/CAMEO」文件夹（1306 个单化学品文件，文件名是 3 字母缩写）
> 变成可精确定位的索引，让 `search_knowledge` → `fetch_media_content` 链路稳定命中。
> 导航文件已上传 IMA（`CAMEO物性导航-增强版.md`），且随 skill 自带副本（`data/`），开箱即用。

## 背景：为什么需要导航文件

- CAMEO 文件是短结构化文本（NFPA/闪点/自燃/沸点/密度/蒸气压/TLV 等章节），文件名是 3 字母缩写（ACT=丙酮、VCM=氯乙烯），关键词稀疏；
- IMA `search_knowledge` 是语义检索：搜英文名**能命中** CAMEO 文件（highlight 精确高亮），但两个问题：① `folder_id` 不严格限定（混入 Ullmann/CRC/API 泛化文档）；② CAMEO 文件排序靠后被淹没；
- 导航文件是"高密度关键词索引"：缩写 + 英文名 + 中文名 + CAS + 同义词集中出现，语义检索稳命中，且**直接给 media_id** 免翻找。
- **能力边界（2026-08-15 认知修正）**：导航只解决"英文/中文检索定位"，解决不了"整本手册（化学化工物性手册 182MB 等）fetch 超 token"的问题——整本手册只能靠 IMA 客户端对话（完整 RAG）拿数值。

## 数据流全景

```
get_knowledge_list（27 页分页）→ page_01~27.jsonl（title/intro/media_id）
        ↓ build_cameo_index.py
CAMEO物性导航.md（精简版：缩写+英文名+同义词+media_id）
        ↓ 中文名翻译（Agent 人工，1306 条）+ batch_cas.py（PubChem 查 CAS）+ fix_cas.py（简化名补充）
cn_map_all.jsonl + cas_results.jsonl
        ↓ gen_enhanced_nav.py
CAMEO物性导航-增强版.md（+中文名 100% + CAS 82.4%）
        ↓ create_media → cos-upload.cjs → add_knowledge
入库 IMA「1-物性数据」文件夹
```

## 步骤 1：遍历 CAMEO 清单（分页）

**必须用后台 Agent 子任务**（27 次分页 × 50 条会撑爆主对话上下文），Agent 用 `DeferExecuteTool` 逐页调用 + `Write` 落盘：

```
mcp__ima-mcp__get_knowledge_list
  knowledge_base_id: "7410596022594182"
  folder_id: "folder_7455529366471323"   # CAMEO 子文件夹
  limit: 50                              # 上限 50，不可调大
  sort_type: "TITLE_SORT_TYPE"           # 字母序；末页缺失可用 TITLE_DESC_SORT_TYPE 补
  cursor: ""                             # 第一次空串，之后传返回的 next_cursor
```

- 落盘格式（每页一个文件，UTF-8）：
  `{"title": "BHP.pdf", "intro": "<英文名+同义词段>", "media_id": "pdf_..."}`
- 断点机制：`resume_state.json` 存"当前 next_cursor + 已完成条数"；网络抖动 `fetch failed` 时等 5 秒重试，连续失败就停，恢复后从断点续传。
- 已验证：1306 条 = 27 页，零重复；末尾 6 个 Z 开头文件（ZSL/ZSF/ZPS/ZPP/ZPF/ZPC）用降序第一页补齐。

**⚠️ 网络红线**：connector-proxy 到 IMA 是**间歇性 fetch failed**（时通时断，非鉴权非限流）。批量 MCP 调用（27 次分页）极易中断，必须：后台 Agent + 断点续传 + 每页落盘。

## 步骤 2：生成精简版导航

```
python scripts/build_cameo_index.py --pages cameo_pages_full.jsonl --out CAMEO物性导航.md
```

- 输入：合并后的 page jsonl（`cat page_*.jsonl > cameo_pages_full.jsonl`）；
- 输出表头：`| 缩写 | 英文名 | 同义词 | media_id |`；
- `parse_intro` 规则：去 `#` 噪声前缀 → 去末尾 3 字母缩写 → 英文名；`Common Synonyms` 段切同义词；
- 质量基线（1306 条实测）：英文名覆盖 100%、同义词 67.7%（剩余是 CAMEO 同义词在表格里的情况）、零 `\ufffd`。

## 步骤 3：补中文名（Agent 翻译）

**PubChem 无中文名**（REST/PUG-View/网页版/description 接口全部验证）——中文名只能靠 AI 翻译或第三方源：

1. 提取英文名清单：`en_names.jsonl`（abbr/en/media_id）；
2. Agent 分批翻译全部 1306 条 → `cn_map_part*.jsonl`（abbr/cn），合并为 `cn_map_all.jsonl`；
3. 翻译时修正 CAMEO OCR 变体：CHORINE→氯、DICHORO→二氯、TRICHOR→三氯等。

## 步骤 4：批量查 CAS（PubChem）

```
python scripts/batch_cas.py     # 后台运行，断点续传 + 限速 3rps，~30 分钟 1306 条
python scripts/fix_cas.py       # 失败补充：简化名重试（去括号/后缀/OCR 修正），边处理边落盘
```

- 链路：英文名 → `pug/compound/name/{name}/cids/JSON` → CID → `pug/compound/cid/{cid}/synonyms/JSON` → 正则匹配 `\d{2,7}-\d{2}-\d` 提取 CAS；
- 实测最终覆盖：**CAS 1076/1306（82.4%）**，失败项是溶液/混合物（ACRYLAMIDE SOLUTION 等）无单一 CAS；
- `fix_cas.py` 必须边处理边落盘（异常保护），一次性重写文件会在中途崩溃时丢失全部修改。

## 步骤 5：生成增强版导航

```
python scripts/gen_enhanced_nav.py
```

- 输入：`en_names.jsonl` + `cn_map_all.jsonl` + `cas_results.jsonl` + page 文件（取 intro）；
- 输出：`CAMEO物性导航-增强版.md`（表头 `| 缩写 | 英文名 | 中文名 | CAS | 同义词 | media_id |`）；
- 实测：中文名 100%、CAS 82.4%、零乱码。

## 步骤 6：上传回 IMA

> ⚠️ **运行层差异（2026-09-14 加）**：本步骤的 `create_media` / `add_knowledge` **仅 WorkBuddy 侧的 ima 连接器提供**。
> DSH 侧（本地 stdio 桥接器）只暴露 `search_knowledge` / `get_knowledge_list` / `get_knowledge_base_list` / `ima_refresh_token`，
> 因此**导航表的重建/上传请在 WorkBuddy 侧执行**；DSH 侧只做"读"（搜索 + 列举）。
> 上传完成后仍可在 DSH 侧用 `get_knowledge_list` 验证解析状态。

```
1. mcp__ima-mcp__create_media
     file_name/file_size/content_type/file_ext/knowledge_base_id → 返回 media_id + COS 凭证
2. node skills-marketplace/skills/ima-skills/knowledge-base/scripts/cos-upload.cjs
     --file <md> --secret-id --secret-key --token --bucket --region --cos-key
     --content-type text/markdown --start-time --expired-time
     （参数全部来自 create_media 返回；--cos-key 是 COS 对象路径）
3. mcp__ima-mcp__add_knowledge
     media_id（create_media 返回的 markdown_... 前缀）+ folder_id="folder_7411216628582850"
```

- 上传后验证：`get_knowledge_list` 查该文件 `media_state=2, parse_progress=100` 即解析完成；
- 检索验证：**独特中文名**（只出现在导航里的词，如"苯酚磺酸锌"）能命中导航并精确高亮；
  高频词中文名（如"异丙苯过氧化氢"被"过氧化氢"稀释）排序靠后，需配合 CAS/英文名或用 IMA 客户端对话。

## 已确认的关键 ID（2026-08-15）

| 项 | ID |
|----|-----|
| KB ID（化工工艺数据库） | `7410596022594182` |
| 「1-物性数据」文件夹 | `folder_7411216628582850` |
| CAMEO 子文件夹（1306 文件） | `folder_7455529366471323` |
| 导航文件 media_id | `markdown_1bed1a57fd48e5adea799dbf6b52a701_4aa712fc4f77c1cd0280cd9c904d4b607410596022594182` |

## 复现示例（第 2~6 步的本地重放）

```bash
cd <skill>/scripts
# 假设已有 page_01~27.jsonl 在 ./cameo_data/
cat cameo_data/page_*.jsonl > cameo_pages_full.jsonl
python build_cameo_index.py --pages cameo_pages_full.jsonl --out ../data/CAMEO物性导航.md
python batch_cas.py    # 需要 en_names.jsonl 在脚本同目录
python fix_cas.py
python gen_enhanced_nav.py
```

> 注：`batch_cas.py`/`fix_cas.py`/`gen_enhanced_nav.py` 的输入文件（en_names.jsonl/cn_map_all.jsonl/cas_results.jsonl/page_*.jsonl）默认放在脚本同目录，按需调整。
