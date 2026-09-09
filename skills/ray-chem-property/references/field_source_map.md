# 字段 → 数据源路由矩阵

> 本文件是 ray-chem-property 的"大脑"：106 列按字段组绑定主源 + 备选源 + 冲突裁决优先级。
> 字段键与列字母的完整映射见 `scripts/field_schema.json`。

## 一、字段分组总览

| 分组 | 字段键前缀 | 列范围 | 字段数 |
|------|-----------|--------|--------|
| 化学品标识 | name_cn / name_en / cas / abbrev / formula / mw | B–H | 7 |
| 物理特性 | mp / bp / cp / density_* / visc_* / sol_* / vp_* / antoine_* / hvap / state20 | I–AD | 24 |
| 临界常数 | critical_temp / critical_pressure（Tc K / Pc MPa） | AE–AF | 2 |
| 物理危害 GHS | haz_explosive … haz_metal_corr（16 类） | AG–AV | 16 |
| 健康危害 GHS | haz_acute_tox … haz_aspiration（10 类） | AW–BF | 10 |
| 环境危害 GHS | haz_ozone / haz_aquatic_*（3 类） | BG–BI | 3 |
| 法规名录 | reg_hazchem / reg_precursor / reg_expl_precursor / reg_key_superv / reg_high_toxic | BJ–BN | 5 |
| NFPA 704 | nfpa_health / nfpa_flam / nfpa_react / nfpa_special / nfpa_diamond | BO–BS | 5 |
| 燃爆数据 | fp_* / fire_class / ignition_temp / autoignition / lel / uel / locc / mie / flame_speed / conductivity / heat_combustion / expl_group / ign_temp_group | BT–CG | 14 |
| 接触限值 | erpg1-3 / aegl*_10/60 / pac1-3 / teel1-3 / idlh | CH–CW | 16 |
| 毒性数据 | ld50_oral / lc50_inh / tox_class_gbz230 / acute_tox_class | CX–DA | 4 |
| 应急准则 | emergency_guidelines（泄漏/火灾/中毒/急救要点） | DB | 1 |
| 其他 | odor / odor_threshold | DC–DD | 2 |
| 运输信息 | un_number / transport_category（UN 编号 + 运输类别） | DE–DF | 2 |
| 备注 | remark | DG | 1 |

> ⚠️ 列重排说明（2026-08-26）：用户将「临界常数」从尾部 DD–DG 提前到 AE–AF（物理特性之后、
> GHS 之前），导致 GHS 及之后所有列整体后移 2 列；应急准则 CZ→DB、UN/运输 DD/DE→DE/DF、备注 DC→DG。
> 本表已对齐用户「调整后的 111 列模板」。列字母以 field_schema.json 的 col 字段为准。

## 二、数据源路由（按优先级）

| 字段组 | ① 脚本主干（PubChem） | ② Agent 补采（WebFetch） | ③ IMA 知识库 |
|--------|----------------------|--------------------------|--------------|
| 标识 / 分子式 / 分子量 | ✅ PUG-REST property | CAS Common Chemistry / NIST | 标准全文佐证 |
| 熔沸点 / 密度 / 蒸气压 / 黏度 / Cp / 汽化热 / Antoine | ✅ PUG-View 实验值 | **NIST Webbook**（标识页直抓核验 + 物性子页面交叉验证）/ chemdb（中文） | 补中文物性 |
| 燃爆（闪点/自燃/LEL/UEL/燃烧热） | ✅ PUG-View | **CAMEO Chemicals**（NFPA/ERPG 出处） | 标准阈值 |
| GHS 危害类别 | ✅ PUG-View GHS Classification | ECHA C&L（核对分类比例） | GB 30000 分类阈值 |
| NFPA 704 | ✅ PUG-View | CAMEO（复核） | — |
| 法规名录（危化品/易制毒/易制爆/高毒/重点监管） | ❌ | **应急管理部 whpdj 登记系统** / 中国化学品名录 | **判定依据全文** |
| ERPG / AEGL / PAC / TEEL / IDLH | ⚠️ IDLH 可解析，其余仅存原文 | **EPA AEGL 表 / CAMEO SCAPA(PAC/TEEL) / NIOSH(IDLH)** | — |
| LD50 / LC50 | ✅ PUG-View 毒理 | ECHA / chemicalbook | 中文毒理 |
| 中文名 / 气味中文 / 检测阈值 / 火灾危险类别 | ❌（仅英文） | **chemicalbook（中文唯一可靠源）** | 补中文 |

## 三、中文名解析的坑（重要）

- PubChem PUG-REST **不能直接解析中文名**（如「丙酮」「双氧水」返回空）。
- 中文名 → CAS/英文名 的三条路径（按优先级）：
  1. **模板已有映射**：用户的「工艺物料安全物性数据表」C/D/E 列本身就是 中文名↔英文名↔CAS 字典，先查它；
  2. **chemicalbook**：`https://www.chemicalbook.com/Search_CN.aspx?keyword=<中文名>` 支持中文检索，返回 CAS；
  3. **PubChem 中文同义词**：部分化合物 PubChem 收录中文同义词，但命中率不稳，仅兜底。

## 四、数据源网址速查

| 源 | 用途 | 入口 |
|----|------|------|
| PubChem | 主干（API 程序化） | PUG-REST / PUG-View |
| NIST Webbook | 标识核验/别名/物性交叉验证 | https://webbook.nist.gov/chemistry/ |
| CAMEO Chemicals | NFPA 704 / ERPG / 反应性 | https://cameochemicals.noaa.gov/ |
| chemicalbook | 中文名/别名/中文气味/检测阈值/火灾类别 | https://www.chemicalbook.com/ |
| 应急管理部危化品登记 | 法规名录（危化品/易制毒/易制爆） | https://whpdj.mem.gov.cn/publicInternet/chemicalsData |
| EPA AEGL | **本地索引开箱即用**（`data/AEGL索引.json` 196 条，按 CAS 查）| 导航页 https://www.epa.gov/aegl/access-acute-exposure-guideline-levels-aegls-values#final（索引页）；**全量数据在 compiled PDF** https://www.epa.gov/sites/default/files/2018-08/documents/compiled_aegls_update_27jul2018.pdf；重建 `scripts/build_aegl_index.py` |
| DOE PAC/TEEL | **本地索引开箱即用**（`data/PAC索引.json` 3063 条，按 CAS 查）| 官方源 https://emhub1.energy.gov/pacteel（⚠️ 国内网络不可达，Excel 需在美网络/代理下载）；重建 `scripts/build_pac_index.py --xlsx <Excel>`；PAC 层级 = Final AEGL(60min) > Interim AEGL > ERPG > TEEL |
| NIOSH | IDLH | https://www.cdc.gov/niosh/idlh/ |
| IMA 化工工艺数据库 | 标准全文/中文物性/法规判定依据 | KB ID 7410596022594182 |
| 化学数据库 csdb | 中文物性补白 | http://www.chemdb.csdb.cn/chemdb/home |
| ChemSpider | 结构/别名/物性交叉验证 | https://www.chemspider.com/ |
| MolAid 摩贝 | 厂商数据/SDS | https://chem.molaid.com/home |

## 五、用户常用 4 站接入实测（2026-08-15）

> 用户常用的 4 个物性网站，逐一实测了可达性与抓取方式。结论：**仅 NIST 可程序化直抓（已固化 nist_verify.py），其余 3 站需浏览器/API**。
> 定位统一为「Agent 补采/交叉验证源」，不进主流水线（主流水线只有 PubChem）。

| 源 | 搜索 URL 格式 | 实测结果 | 能拿什么 | 接入定位 |
|----|--------------|---------|---------|---------|
| **NIST Webbook** | `https://webbook.nist.gov/cgi/cbook.cgi?Name=<英文名或CAS>&Units=SI`（**CAS 无独立参数**，`?CAS=` 会 400，CAS 也走 Name 参数） | ✅ 200，直接返回标识页 | 名称/CAS/分子式/分子量/InChI/InChIKey/别名列表（英文） | **脚本已固化**：`scripts/nist_verify.py <英文名或CAS> [--by-cas] --out output/` → 标识核验 + 别名 + 物性交叉验证（熔点/沸点等实验值在子页面链接，抓取成本高，作佐证不作主源） |
| **应急部 whpdj** | `https://whpdj.mem.gov.cn/publicInternet/chemicalsData`（查询需点开化学品详情） | ⚠️ 412 Precondition Failed（政务反爬，加 Referer 也 412） | 法规名录判定（危化品/易制毒/易制爆登记信息） | **浏览器补采**：用 agent-browser skill 或人工查询；脚本 urllib 不可行 |
| **chemdb（中科院）** | `http://www.chemdb.csdb.cn/chemdb/home`（JS 应用，搜索交互） | ✅ 首页 200，但主体是 JS 框架（初始 HTML 仅 ~500B） | 中文物性（中文检索友好） | **浏览器补采**（JS 渲染，urllib 拿不到内容）；人工/agent-browser |
| **ChemSpider** | 网页 `https://www.chemspider.com/Search.aspx?q=` 已 **404**；REST API 需注册 token（developer.rsc.org） | ⚠️ 网页搜索 404（JS 应用） | 结构/别名/部分物性 | **REST API（有 token 时）**或人工浏览器；urllib 网页路径不可行 |

**使用顺序建议**（物性补采）：NIST（程序化最快）→ chemicalbook（中文）→ chemdb（中文，浏览器）→ ChemSpider（API/浏览器）→ whpdj（法规名录专用，浏览器）。

### 数据源完整 URL 与查询方法（2026-08-15 外部对比补充）

| 来源 | 完整 URL | 查询方法 |
|------|---------|---------|
| **PubChem** | `https://pubchem.ncbi.nlm.nih.gov/compound/<CAS号>` | 用 CAS 搜；Sections: Chemical & Physical Properties / Solubility / Safety & Hazards |
| **NIST WebBook** | `https://webbook.nist.gov/cgi/cbook.cgi?Name=<CAS或英文名>&Units=SI` | 标识页（CAS/公式/分子量/别名）；Phase change data（熔沸点）、Gas phase thermochemistry（蒸气密度）在子链接 |
| **Sigma-Aldrich SDS** | `https://www.sigmaaldrich.com/` 搜产品 → Download SDS | SDS Section 9: Physical & Chemical Properties（闪点/密度/物态） |
| **ChemicalBook** | `https://www.chemicalbook.com/Search_CN.aspx?keyword=<名称>` | 搜 CAS/中文名，首页即熔点/沸点/闪点/密度/物态表 |
| **CAMEO Chemicals** | `https://cameochemicals.noaa.gov/chemical/<CAS号>` | Reactivity: 遇水反应性；Flammability: 爆炸极限；Health: 灭火禁忌 |
| **NIOSH Pocket Guide** | `https://www.cdc.gov/niosh/npg/npgd<编号>.html` | Explosive limits（LEL/UEL）、IDLH、蒸气密度（需先按化学品查 NPG 编号） |
| **ChemSpider** | REST API 需 token（developer.rsc.org） | Properties 部分含物态、密度 |
| **GB 50016-2014** | `https://openstd.samr.gov.cn/` | 表 3.1.1 火灾危险性分类（判定规则见 conflict_rules.md 第五节） |
| **GBZ 2.1-2019** | 本地索引 `data/GBZ_OEL索引.json`（295 种，基于 2007 版提取，2019 为现行，未命中联网确认） | CAS 号直接比对 MAC/PC-TWA/PC-STEL |
| **危险化学品目录 2015** | 本地索引 `data/危化品目录索引.json`（2552 种含中文 GHS 类别 + 剧毒标记） | CAS 号直接比对"是否列入 + GHS 类别" |
| **有毒气体检测目录** | 本地索引 `data/有毒气体目录索引.json`（244 种：高毒 54 + GB/T 50493 附录B + HG/T 20660 附录A + 剧毒清单） | CAS 号比对 reg_high_toxic 判定 |

> 中国法规索引由 `scripts/build_reg_reference.py` 从 `data/raw-*.md` 重建（法规数据公有，来源标注法规文件本身）。

### IMA「1-物性数据」文件夹（重点检索目录）

- **文件夹 ID**：`folder_7411216628582850`（在「化工工艺数据库」KB 内）
- 检索时用 `search_knowledge` 传 `folder_id=folder_7411216628582850` 限定范围
- 内含权威物性源（子文件夹 + 手册 PDF）：
  - **CAMEO**（子文件夹 `folder_7455529366471323`，1306 文件）→ NFPA 704 / 闪点 / ERPG / 反应性
  - 化学化工物性数据手册 有机卷/无机卷（刘光启主编）→ 熔沸点/密度/蒸气压/焓
  - CRC Handbook、兰氏化学手册、石油化工基础数据手册、气液物性估算手册(Poling)、Bretherick 反应性手册
- 注意（2026-08-15 认知修正）：**两条路分开用**——
  - **CAMEO（MCP 可精确查表）**：搜英文名命中单文件 → `fetch_media_content` 读完整数据；
  - **整本手册（MCP 拿不到完整数值）**：`search_knowledge` 只返回片段摘要（highlight 几十字），且高频词淹没主体词；fetch 大文件超 token → **正确用法是 IMA 客户端直接对话**（完整 RAG：检索+LLM 生成，能查到《物性数据手册》锌粉熔点 419.53℃ 这类完整物性），作为 Step 1c 可选补充源，Agent 整合。

## 附录：skill 完整目录结构

```
ray-chem-property/
├── SKILL.md                     # 主文档（Step 0-5 工作流）
├── scripts/（14 个）
│   ├── field_schema.json        # 106 列 → 字段键 规范映射（全脚本共享）
│   ├── pubchem_api.py           # PubChem PUG-REST/View 公共抓取
│   ├── resolve_identifiers.py   # Step 0 名称/CAS → CID
│   ├── search_web.py            # Step 1 PubChem 主干
│   ├── search_ima.py            # Step 1 IMA + supplement 规范化
│   ├── nist_verify.py           # Step 1 NIST 标识页直抓（CAS/分子式/分子量/别名，交叉核验）
│   ├── merge_compare.py         # Step 2 归并 + 裁决
│   ├── gen_html.py              # Step 3a 横版 HTML + 导出按钮（--template 可选）
│   ├── export_excel.py          # Step 3b 模板回填 + 来源注释
│   ├── build_cameo_index.py     # Step 5 精简版导航（pages → MD）
│   ├── batch_cas.py             # Step 5 批量 PubChem 查 CAS（断点续传+限速）
│   ├── fix_cas.py               # Step 5 CAS 失败补充（简化名重试）
│   ├── gen_enhanced_nav.py      # Step 5 增强版导航（+中文名+CAS）
│   ├── build_aegl_index.py      # Step 1 AEGL 本地索引（下载 EPA compiled PDF → JSON）
│   ├── build_pac_index.py       # Step 1 PAC 本地索引（DOE PAC Excel → JSON，多级表头适配）
│   └── build_reg_reference.py   # Step 1 中国法规索引（raw-*.md → 3 个 JSON）
├── references/
│   ├── field_source_map.md      # 字段 → 数据源路由矩阵 + URL 指南 + 目录结构
│   ├── conflict_rules.md        # 冲突裁决 + 单位换算 + 火灾类别判定
│   └── cameo_nav_build.md       # CAMEO 导航构建全流程（分页/翻译/CAS/上传）
├── data/
│   ├── CAMEO物性导航-增强版.md  # 1306 条索引（缩写+英文+中文+CAS+同义词+media_id）
│   ├── CAMEO物性导航.md         # 精简版（缩写+英文+同义词+media_id）
│   ├── AEGL索引.json            # 196 个 Final AEGLs（aegl1/2/3 × 10/30/60min/4h/8h，按 CAS）
│   ├── PAC索引.json             # 3063 个化学品 PAC-1/2/3（DOE 数据库，按 CAS）
│   ├── GBZ_OEL索引.json         # 295 种职业接触限值 MAC/PC-TWA/PC-STEL（按 CAS）
│   ├── 危化品目录索引.json       # 2552 种（中文 GHS 类别 + 剧毒标记 147，按 CAS）
│   ├── 有毒气体目录索引.json     # 244 种（高毒54 + GB/T50493 + HG/T20660 + 剧毒清单）
│   └── raw-*.md                 # 法规原始数据（GBZ-OEL / 危化品目录 / 有毒气体目录）
└── templates/                   # （预留 HTML 模板目录）
```
