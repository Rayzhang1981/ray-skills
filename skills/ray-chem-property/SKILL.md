---
name: ray-chem-property
slug: ray-chem-property
displayName: 化学品物性数据搜集整理
version: 3.6.0
category: 化工安全
agent_created: true
description: >-
  输入化学品清单（中文名/英文名/CAS/简写，可批量；也支持从设备一览表/工艺描述/半成品表提取物料），
  自动检索 PubChem/IMA(CAMEO)/chemicalbook/NIST/whpdj 等权威源，分析对比去重后，
  把 111 列工艺物料安全物性数据（标识/物理特性/GHS危害/法规名录/NFPA/燃爆/接触限值/毒理/应急准则/UN运输/临界常数）
  生成横版可视化 HTML 报告（一行一物料 + 导出 Excel 按钮，导出样式与母版一致 + 单元格来源注释），
  并回填到用户指定的「工艺物料安全物性数据表」Excel 模板。
  内置 13 类本地离线索引（CAMEO 1306/AEGL 196/PAC 3063/法规名录/危险品全书 999/CRC 3460/兰氏 2709/Perry 254/SARA 1694/TDG 2311 等，秒查）。
  另有反应性补充索引 2 类（2026-09-23 增）：CAMEO 材质反应性段（与水/常见材料/聚合/阻聚剂）+ 危险品全书禁配物段（危险反应/禁配物/分解产物）。
  触发词：化学品物性、物性数据搜集、物料安全物性表、工艺物料物性、CAS 物性查询、物性数据表、CAMEO 导航、设备物料介质提取、危险品安全技术全书、CRC、兰氏、Perry、禁配物、水敏、遇水反应、聚合风险、阻聚剂、CG 配伍组、材质相容。
---

# 化学品物性数据搜集整理（ray-chem-property）

## 这个 skill 做什么

输入化学品（中文名/英文名/CAS/简写），产出：
1. **HTML 可视化报告**（NFPA 菱形 + GHS 徽章 + 分区详表 + 每字段来源/置信度标注）
2. **回填后的 Excel**（严格按用户「工艺物料安全物性数据表」111 列模板格式）

三阶段流水线：**信息检索 → 分析对比去重 → 可视化 + 导出 Excel**。

## 何时用

- 用户给一份化学品清单，要查它们的物性数据（熔点/沸点/密度/闪点/爆炸极限/毒性/GHS 分类/NFPA/法规名录等）
- 用户要把新物料的物性补进「工艺物料安全物性数据表」
- 用户提到「CAS 物性查询」「物料安全物性数据表」「化学品物性搜集」

## 前置条件

- Python venv（`~/.workbuddy/binaries/python/envs/default/Scripts/python.exe`），已装 `openpyxl`
- 联网可访问 PubChem（脚本用 urllib 直连，无需额外包）
- IMA 知识库（可选）：需用户在连接器面板连接 `ima 知识库`，MCP 工具 `mcp__ima-mcp__search_knowledge`
  （**运行层差异**：DSH 侧经本地 stdio 桥接器同样有 `search_knowledge` / `get_knowledge_list` / `get_knowledge_base_list`；
  单文件读取 `fetch_media_content` 与写入类 `create_media` / `add_knowledge` **仅 WorkBuddy 侧有**——详见 Step 4 的注）
- 模板 Excel：用户指定的「工艺物料安全物性数据表」（111 列，2026-08-26 新增 Emergency Guidelines/UN编号/运输类别/临界温度/临界压力），路径按对话提供

## 工作流程（4 步 + 验证）

### Step 0 — 输入解析：名称/CAS → 标准化

**四态输入形态（2026-08-17 补，对齐外部同类 skill 的最佳实践）**：

| 输入形态 | 例子 | 处理方式 |
|---------|------|---------|
| **干净列表** | `乙腈、甲苯、甲醇` | 直接走 resolve_identifiers.py |
| **脏数据** | 大段工艺描述、SDS 全文、会议记录 | 先让 Agent 从中提取化学品名清单 → **用户确认** → 走 resolve |
| **设备一览表** | 含"物料介质"列的 xlsx | 提取介质列 → **归并变体**（异体字/错别字/浓度前缀如"50%氢氧化钠"→氢氧化钠）→ 去重 → 走 resolve |
| **半成品** | 名称 + 部分物性已有 | 按模板列对齐已有列，仅补缺字段（跳过已有列避免覆盖） |

> 设备表提取时注意：同一 CAS 可能有多个浓度/形态变体（如"氢氧化钠溶液"与"氢氧化钠固体"），归并后**保留用户原始名称**（写入 `name_cn`），不要丢失浓度/形态信息——这会直接影响 20℃状态列和后续解读。

```
python scripts/resolve_identifiers.py 丙酮 甲醛 --out output/
# 或文本清单：python scripts/resolve_identifiers.py --file 清单.txt --out output/
# 或 JSON：python scripts/resolve_identifiers.py --json 清单.json --out output/
```

⚠️ **中文名不能直接走 PubChem**：PubChem 名称解析以英文为主。中文名先转 CAS：
1. 先查用户模板 Excel 的 C/D/E 列（中文名↔英文名↔CAS 字典）；
2. 否则 WebFetch chemicalbook（`https://www.chemicalbook.com/Search_CN.aspx?keyword=<中文名>`）拿 CAS；
3. 英文名/CAS 直接传给脚本。

产出 `output/input.json`（每个物料含 CID/CAS/分子式/分子量/混合物标记）。

**输入校验边界（2026-08-17 补）**：请求超范围或缺关键输入时**显式止步**，不静默扩大任务。典型情况：
- 输入只是闲聊/无化学品清单 → 不执行，请用户给出清单；
- 输入物料超出模板能力（如放射性物质、需要反应动力学数据的场景）→ 说明本 skill 只做物性数据，建议其他工具；
- 用户要求"顺便"加做无关任务 → 拒绝，保持单一职责。

### Step 1 — 信息检索（并行）

**脚本主干（PubChem，覆盖 ~70% 字段）**：
```
python scripts/search_web.py --out output/
```
产出 `output/raw_{cas}.json`（标识/物性/燃爆/GHS/NFPA/毒理/接触限值原始数据）。

**Agent 补采（WebFetch 多源，覆盖脚本缺的 30%）**：
- **中文名/气味中文/检测阈值/火灾危险类别** → chemicalbook
- **法规名录**（危化品/易制毒/易制爆/高毒/重点监管）→ 应急管理部 whpdj 登记系统（⚠️ 412 反爬，需浏览器）
- **ERPG/AEGL/PAC/TEEL** → **AEGL：本地全量索引开箱即用**（`data/AEGL索引.json`，196 个 Final AEGLs 按 CAS 查；
  重建 `python scripts/build_aegl_index.py` 自动下载 EPA Compiled PDF 解析。EPA 入口：导航页
  `epa.gov/aegl/access-acute-exposure-guideline-levels-aegls-values#final` 是索引，**全量数据在 compiled PDF**
  `epa.gov/sites/default/files/2018-08/documents/compiled_aegls_update_27jul2018.pdf`；Interim 值（丙酮/甲醛/苯等）
  不在 compiled PDF，需从 EPA 各化学品结果页补）；**PAC：本地全量索引开箱即用**（`data/PAC索引.json`，3063 个
  化学品 PAC-1/2/3 按 CAS 查；`python scripts/build_pac_index.py --xlsx <DOE数据库.xlsx>` 重建。DOE 官方源
  `emhub1.energy.gov/pacteel` 国内网络不可达，Excel 需在美网络/代理下载；PAC 层级 = Final AEGL(60min) > Interim
  AEGL > ERPG > TEEL）；ERPG → AIHA（无免费全量表，靠 CAMEO/chemicalbook）；IDLH → NIOSH
- **中国法规名录（本地离线秒查，替代 whpdj 浏览器补采）**：
  - `data/危化品目录索引.json`（2552 种，含**中文 GHS 类别** + 剧毒标记 147）→ `reg_hazchem` 判定 + `haz_*` 中文类别核对 + `reg_high_toxic`（剧毒）
  - `data/GBZ_OEL索引.json`（295 种 MAC/PC-TWA/PC-STEL，mg/m³）→ 职业接触限值补白（备注 GBZ 2.1-2007 提取，2019 为现行，未命中联网确认）
  - `data/有毒气体目录索引.json`（244 种：高毒 54 + GB/T 50493 附录B + HG/T 20660 附录A + 剧毒清单）→ `reg_high_toxic` 判定
  - 重建：`python scripts/build_reg_reference.py`（从 `data/raw-*.md` 解析）；原始数据 `data/raw-GBZ-OEL.md` 等
- **火灾危险性类别（fire_class）**：按 GB 50016-2014 表 3.1.1 判定（闪点<28℃甲 / 28-60℃乙 / ≥60℃丙 / 氧化剂酸碱遇水品非可燃），规则见 `references/conflict_rules.md` 第五节；HTML/Excel 按甲红/乙橙/丙黄着色
- **应急准则（emergency_guidelines，v3.3.0 本地离线秒查）**：`data/应急准则索引.json`（999 条按 CAS 键，与危险品全书物性索引同源同覆盖）
  ——从全书第四部分（急救）/第五部分（消防）/第六部分（泄漏应急处理）/第七部分（操作处置与储存）提取，
  每条含 first_aid/fire/spill/handling_storage 四要素子字段 dict（如 急救-吸入/皮肤接触/眼睛接触/食入、消防-灭火剂/特别危险性）。
  auto_supplement 自动拼成 `【急救】…｜【消防】…｜【泄漏处置】…｜【操作储存】…` 文本（≤800 字截断）写入 emergency_guidelines 列。
  重建：`python scripts/build_emergency_index.py "<通用卷PDF路径>"`（2094 页约 2 分钟）。水（7732-18-5）不在书中属正常——全书只收录危险化学品
- **ERG2024 隔离/防护距离（v3.4.0，TIH 物料量化应急数据）**：`data/ERG2024-索引.json`（261 UN 键，US DOT Emergency Response Guidebook 2024 Yellow Table 1）
  ——每条含 guide（Guide 号）/small+large（Initial Isolation + Protective Action Distance：iso_m/iso_ft/day_km/day_mi/night_km/night_mi）/refer_table3（10 个常见 TIH 气体大泄漏距离查 Table 3）/aliases。
  ERG 按 UN 键，补采链路借危险品全书物性索引的 un_number 字段做 CAS→UN 桥接（999 CAS 中 100 个可桥接，苯/丙酮等非 TIH 物料不在 Table 1 属正常）。
  auto_supplement 拼成 `【ERG2024隔离防护】小量泄漏：隔离30m，白天0.1/夜间0.2km｜大量泄漏：…` 放在应急文本最前（量化数据优先，防截断）。
  重建：`python scripts/build_erg_index.py "<ERG2024 PDF路径>"`（词坐标法，42 数据页约 20 秒）
- **标识核验/别名/物性交叉验证** → NIST Webbook（`python scripts/nist_verify.py <英文名或CAS> --out output/`，直抓 `cbook.cgi` 返回标识页：CAS/分子式/分子量/InChI/别名；`--by-cas` 按 CAS 查）
- **中文物性补白** → chemdb 中科院化学数据库（⚠️ JS 应用，需浏览器）；ChemSpider（⚠️ 网页搜索已 404，走 REST API 需 token）
- **IMA 知识库**（可选）→ KB ID 7410596022594182，「1-物性数据」文件夹 `folder_id="folder_7411216628582850"`（CAMEO 1306 文件 + 化学化工物性手册 + CRC/兰氏/Bretherick 等）

> 4 个常用站的接入实测（搜索 URL/反爬/能拿什么）见 `references/field_source_map.md` 第五节。

**IMA 数据的两条用法（2026-08-15 认知修正，务必区分）**：
- **CAMEO（MCP 可精确查表）**：搜英文名命中 CAMEO 单文件（CMH=异丙苯过氧化氢、BHP=叔丁基过氧化氢、ACT=丙酮、VCM=氯乙烯…）→ 取 `media_id` → `fetch_media_content` 读完整数据（16KB 单文件）。解析章节：NFPA(8.5)/闪点(4.1)/自燃(4.7)/沸点(9.3)/密度(9.7)/蒸气压(9.25)/TLV(3.4)/MOCC(4.14)。
- **整本手册（MCP 拿不到完整数值）**：`search_knowledge` 只返回片段摘要（highlight 几十字），且"沸点/密度"等高频词会淹没主体词（实测搜"锌粉 熔点 沸点 密度"命中 100 条全是泛化）；fetch 大文件超 token。**正确用法 = IMA 客户端直接对话**（完整 RAG：语义理解+检索+LLM 生成，能查到《物性数据手册》的锌粉熔点 419.53℃ 这类完整数据）。

### Step 1c（可选）— IMA 客户端对话补充（人机协同）

用户用 **IMA 客户端直接对话**查整本手册物性（完整 RAG，MCP 拿不到的数值），
把答案原文粘贴给 Agent → 解析成 supplement 字段（"熔点: 419.53 °C"→`mp="419.53"`）。
IMA 答案来自权威手册，冲突按「权威手册 > PubChem」裁决（`references/conflict_rules.md`）；
**单位未明确的值不硬填**（J/g 与 kJ/mol 差 65 倍）。

补采写入 `output/supplement_{cas}.json`
（格式 `{"fields": {<字段键>: {"value": ...}}}`，键见 field_schema.json；
可用 `python scripts/search_ima.py --cas <cas> --json 补采.json --out output/` 规范化）。

### Step 2 — 分析对比去重、确定最终结果

```
python scripts/merge_compare.py --out output/
```
- 按字段归并 PubChem + supplement，标注来源 + 置信度；
- 冲突裁决按 `references/conflict_rules.md`（人工补采 > 监管数据 > PubChem 汇总值 > 推导值）；
- 产出 `merged_{cas}.json`（含完整候选证据链，供人工审查）+ `final_{cas}.json`（裁决值）。

**人工审查闸门**：`merged_*.json` 中 `candidates > 1` 的字段是冲突点，`value` 空但有候选的是「待确认」。
必要时用 Edit 改 `final_{cas}.json` 或重写 supplement 后重跑 merge。

### Step 3 — 输出

```
python scripts/gen_html.py --outdir output/ --template <模板.xlsx> --output report.html   # 横版报告（一行一物料 + 导出按钮）
python scripts/export_excel.py --template <模板.xlsx> --outdir output/ --output 结果.xlsx   # 回填模板（追加到母版）
```

- **HTML**：横版表格，一行一个物料，111 列按分区分组；物料名/表头冻结，可横向滚动；悬停看来源、⚠ 标冲突。
- **「导出 Excel」按钮**：前端 xlsx-js-style（SheetJS 社区 fork，支持写样式）把数据写进你模板的 106 列表头结构，
  列位 + **样式与母版逐列一致**（多级表头 8 行 + 107 合并区 + 列宽 + 表头行高 + 标题字体/边框 +
  **数据区逐列继承母版成品行样式**——首行/中间行/末行三套参照，分区边框 hair 网格+thin/thick/medium 边界、
  名称列 left 对齐+solid 底色），浏览器直接下载 .xlsx。**离线可用**：`gen_html.py` 会把
  `scripts/xlsx-js-style.min.js`（npm xlsx-js-style@1.2.0，已从 unpkg 下架、CDN 404）复制到 HTML 同目录，
  report.html 用相对路径引用，**无需联网**。SheetJS CE 版不支持写样式，勿换回。数据从模板 R9（0 基 r=8）起。
- **`export_excel.py` 来源注释**：每个回填单元格带 Excel Comment（数据来源，同行不同列来源可不同），
  悬停红三角查看证据链——审查者能追溯每个数值的来源（对齐"数据来源审计"习惯）。
- **HTML 火灾类别着色**：fire_class 列按 GB 50016 甲红/乙橙/丙黄/非可燃白背景。
- 两种导出区别：HTML 按钮导出**仅含本次查询物料**（新表，样式同母版，数据从 R9 起）；
  `export_excel.py` 是**追加到你母版 Excel**（格式 100% 母版，自动定位首个整行空白行——
  跳过名称/CAS 缺失的占位行和 `=IF(#REF!...)` 公式残留行）。

### Step 4 — 验证（必做）

1. **扫 `\ufffd`**：`python -c "print('\ufffd' in open('output/report.html',encoding='utf-8').read())"` → False
2. **核对字段映射**：抽 1 个物料，比对模板同物料历史行的数值（模板已有 30+ 成品数据可当参照）
3. **复核数值**：抽熔沸点/闪点/自燃/LEL/UEL 与 NIST/CAMEO 交叉核对
4. **产物呈现**：`present_files` 展示 report.html + 结果.xlsx

### Step 5（可选）— CAMEO 导航构建（让 IMA 精确查表）

当需要把 IMA「1-物性数据/CAMEO」文件夹（1306 个单化学品文件）变成可精确定位的索引时使用。
**开箱即用**：`data/CAMEO物性导航-增强版.md` 已含 1306 条（缩写+英文名+中文名 100%+CAS 82.4%+同义词+media_id），
已上传 IMA「1-物性数据」文件夹；重建/更新导航的完整流程见 `references/cameo_nav_build.md`。

```
# 重新构建（需要 page_*.jsonl 原始清单）：
cat page_*.jsonl > cameo_pages_full.jsonl
python scripts/build_cameo_index.py --pages cameo_pages_full.jsonl --out ../data/CAMEO物性导航.md   # 精简版
python scripts/batch_cas.py     # 批量 PubChem 查 CAS（断点续传 + 限速，~30 分钟）
python scripts/fix_cas.py       # 失败补充（简化名重试）
python scripts/gen_enhanced_nav.py  # 增强版（+中文名+CAS）
# 上传回 IMA：create_media → cos-upload.cjs → add_knowledge（详见 cameo_nav_build.md 步骤 6）
```

**使用导航查物性**（Agent 链路）：用户给化学品 → 在导航表定位（中文名/英文名/CAS/缩写）→ 取 `media_id`
→ `mcp__ima-mcp__fetch_media_content` 精确读单文件 → 解析 NFPA(8.5)/闪点(4.1)/自燃(4.7)/沸点(9.3)/密度(9.7)/蒸气压(9.25)/TLV(3.4)。
> ⚠️ **运行层差异（2026-09-14 加）**：`fetch_media_content` 目前**只在 WorkBuddy 侧的 ima 连接器可用**；
> 在 DSH（本地 stdio 桥接器）只提供 `search_knowledge` / `get_knowledge_list` / `get_knowledge_base_list` / `ima_refresh_token`。
> 在 DSH 下走到这一步时：**优先用本地离线索引（1-物性数据索引等 13 类，秒查、无需网络）**；
> 本地索引缺项再请用户在 WorkBuddy 侧完成单文件读取，**不要**反复重试不存在的工具。
> 判断当前运行时：能调通 `mcp__ima-mcp__search_knowledge` 但 `fetch_media_content` 报 unknown tool 即为 DSH。
**中文检索局限**：独特中文名（如"苯酚磺酸锌"）能命中导航并高亮；高频词中文名（如"异丙苯过氧化氢"被"过氧化氢"稀释）
排序靠后——此时配合 CAS/英文名检索，或走 IMA 客户端对话。

## 反应性/相容性字段秒查（2026-09-23 增 · v3.6.0）

> **分工铁律**：相容性**判定**与矩阵归 `ray-chem-compat`（L1 规则引擎 + 仲裁顺序）；
> 本 skill 只做**物性表反应性字段补全**（111 列模板的"补充备注"级使用，不加列、不造判定）。

```powershell
# 本地秒查（零外部依赖，data/ 两件新索引）
python scripts/query_reactivity.py --cas 10217-52-4     # 危险品全书：危险反应/禁配物/分解产物/pages
python scripts/query_reactivity.py --name hydrazine     # CAMEO：与水/常见材料/聚合/阻聚剂 + CG 配伍组
```

| data/ 文件（新） | 键 | 字段 |
|---|---|---|
| `禁配物-危险品全书.json`（997 CAS） | CAS | 危险反应 / 避免接触的条件 / 禁配物 / 危险的分解产物 / pages（原书页码溯源） |
| `材质反应性-CAMEO.json`（999 CAS + 269 无 CAS 按名） | CAS | water / common_materials / polymerize / inhibitor / CG 配伍组 |

数据源：**与 ray-chem-compat 同源同书**（CAMEO 1306 份 CHRIS 数据表、危险品全书·通用卷 3rd Ed 原书 PDF），
参照其 `_process/scripts/build_sheet1...`（对应本机两份独立生成器），**查询语义两条铁律**：
①「未查到 ≠ 无害」（空白字段标"未查到"）；② 引用只作**描述性字段**，不构成判定结论（判定 → ray-chem-compat）。

## 目录结构（完整版见 references/field_source_map.md 附录）

```
ray-chem-property/
├── SKILL.md              # 主文档（Step 0-5 工作流）
├── scripts/ (17 个)      # field_schema.json + query_reactivity + 15 脚本（见附录）
├── references/ (4 个)    # field_source_map / conflict_rules / cameo_nav_build / pitfalls（31坑+18经验）
├── data/ (20 个)         # 上列 18 + 禁配物-危险品全书 + 材质反应性-CAMEO（2026-09-23 增，反应性字段秒查）
└── templates/            # 预留
```

## 安全红线（必守，2026-08-17 补）

> 对齐 SDS 起草类外部 skill 的核心原则，化工安全场景的红线级规则：

1. **「未查到 ≠ 无害」**：缺失字段只能标注"未查到 / 无数据"，**绝不默认填"无"或跳过**——
   没有数据的字段在危害角度意味着未知，不是安全。Excel 空单元格记 `·`，HTML 显示 rem 提示，绝不暗示"该危害不存在"。
2. **不编造数据**：任何数值必须有来源（PubChem/NIST/监管名录/手册）；查不到就留空标注，**禁止用常识推断冒充实测值**（如"水肯定闪点高"→ 不能填）。
3. **单位未明确不硬填**：查到的值若单位不清晰（如汽化热 J/g vs kJ/mol 差 65 倍），标"待确认"而不是猜一个。
4. **特殊危害如实标注**：剧毒/易制爆/涉恐前体等物料，如实标注其法规地位，**不因敏感而淡化**；同时提示安全处理要求。
5. **输出带 AI 生成声明**：交付物（HTML/Excel）中注明"AI 辅助生成，数据需专业核实后使用"——化工数据直接用于安全决策，必须保留人工审查闸门。

## 关键坑速查（高频 Top 8，完整 31 条见 `references/pitfalls.md`）

> ⚠️ 完整坑库已卸载至 `references/pitfalls.md`（31 条关键坑 + 18 条实战经验）——执行到对应脚本/步骤遇问题时按需查阅。此处只留最易踩的 8 条：

1. **中文名不能直查 PubChem**（不认中文名）：先经模板 C/D/E 列字典 → chemicalbook → CAS（见 Step 0）。
2. **Excel 导出绝不用前端 SheetJS CE 重建**（不写样式）：走 xlsx-js-style 或后端 `export_excel.py` 模板回填。
3. **"未查到 ≠ 无害"**：缺失字段标"未查到/无数据"，绝不默认填"无"（安全红线）。
4. **NIST 查 CAS 用 `?Name=<CAS>`**，勿用 `?CAS=`（400 非法）。
5. **IMA 批量分页用后台 Agent + 断点续传**（主对话 27 次分页撑爆上下文；connector-proxy 间歇 fetch failed）。
6. **本地索引优先**：CAMEO/AEGL/PAC/法规/ERG/书库都有离线 JSON 索引，秒查优于逐条在线（见 Step 1）。
7. **有机物查沸点防误判**：有机过氧化物 PubChem 可能把分解温度标成沸点 → state20 误判气体，需人工核对。
8. **openpyxl 中部插列三连坑**（insert_cols 不动合并区/unmerge 崩溃/merge 只留左上角）→ 改尾部追加零风险。

**实战经验归档**：18 条历史经验（PDF 提取/HTML 样式/Excel 对齐等）已移入 `references/pitfalls.md` 第二节，不再常驻正文。

## 复现示例（丙酮，验证脚本正确性）

```bash
cd scripts/
python resolve_identifiers.py 67-64-1 --out /tmp/t
python search_web.py --out /tmp/t
python merge_compare.py --out /tmp/t
python gen_html.py --outdir /tmp/t
python export_excel.py --template "<模板.xlsx>" --outdir /tmp/t
```

## 人机协同完整流程（2026-08-15 实测验证）

```
Step 0  输入解析（名称/CAS）
Step 1  我走 MCP 主干：PubChem（结构化）+ CAMEO（导航→fetch 单文件）+ chemicalbook（中文）
Step 1c 你用 IMA 客户端对话查整本手册（可选）→ 把答案原样粘贴给我
Step 2  我整合：主流程结果 vs 你的 IMA 参考答案，冲突按「权威手册 > PubChem」裁决
Step 3  输出 HTML + 回填 Excel
```

- 实测（4 种有机过氧化物）：TBHP/CHP/IPP 的 IMA 答案补齐了闪点（CHP 79℃ 修正 CAMEO 48.9℃）、
  有机过氧化物型（C/D/E/F）、TDG 温控（TAPND 0℃/+10℃、IPP -15℃/-5℃ + UN 3112）、分解温度定 47℃；
- IMA 答案里的**单位未明确**值（如"汽化热 2592.0"）不硬填，留空标注"待确认"（J/g 与 kJ/mol 差 65 倍，填错是红线级事故）；
- 整合时把 IMA 答案的原文 + 裁决理由写进 `remark`，保留证据链供人工审查。

## 维护记录

| 日期 | 变更 |
|------|------|
| 2026-09-02 | v3.5.0：token 瘦身（16972→<9000 tok，超限 2 倍问题修复）。①「关键坑」31 条 +「实战经验」18 条整体卸载至 `references/pitfalls.md`（124 行），正文只留「高频坑速查 Top 8」（最易踩 8 条 + 索引）；②description 的本地索引清单精简为一行概览（明细正文有，触发面不重复）；③目录结构 references 数 3→4。按需加载原则：完整坑库执行到对应脚本/步骤遇问题时才查，不常驻上下文。 |
| 2026-09-23 | v3.6.0：**反应性字段秒查**（方案 B · 副本独立）。新增 `data/禁配物-危险品全书.json`（997 CAS：危险反应/禁配物/分解产物/pages 溯源）+ `data/材质反应性-CAMEO.json`（999 CAS + 269 无 CAS 按名：water/common_materials/polymerize/inhibitor/CG 配伍组）+ `scripts/query_reactivity.py`；SKILL.md 增「反应性/相容性字段秒查」节与分工铁律（判定归 ray-chem-compat，本 skill 只做字段补全）；触发词 +7（禁配物/水敏/遇水反应/聚合风险/阻聚剂/CG 配伍组/材质相容）。数据源与 ray-chem-compat 同源同书（双份漂移对策＝同书重建 + 指纹对账）；111 列 schema 与母版模板**未动**（加列属 MOC 级变更，另行立项）。 |
