# 关键坑全集 + 实战经验归档（v3.5.0 从 SKILL.md 卸载）

> 按需加载——执行到对应脚本/步骤时遇问题，回来查完整条目；正文只留高频坑速查。

## 关键坑（务必读）

❌ **反例一**：**不要**用前端 SheetJS CE 重建 Excel 表头（社区版不写样式），导出走 xlsx-js-style 或后端模板回填。
❌ **反例二**：**切勿**用 `?CAS=` 参数查 NIST（400 非法），CAS 必须走 `?Name=<CAS>`；IMA 批量分页**不要**在主对话手动做（撑爆上下文），用后台 Agent + 断点续传。

1. **中文名解析**：PubChem 不认中文名，先经模板/chemicalbook 转 CAS（见 Step 0）。
2. **Excel 回填用「模板母版复制 + 列映射」，绝不用前端 SheetJS 重建**——否则丢失 106 列多级表头/合并单元格/单位行。
3. **蒸气压/密度/黏度要按温度路由到 20/25/60℃ 列**（脚本已做 °F→°C 换算）。
4. **GHS 少数派分类**：PubChem 聚合多家供应商通知，个别 H-code 来自少数派，需核对分类比例。
5. **混合物/聚合物无单一 CAS**：溶液按「组分 CAS+浓度」，聚合物沸点/分子量标 `—`。
6. **TEEL 不在 PubChem**，只能从 CAMEO SCAPA 补采。
7. **有机过氧化物**：PubChem 可能把分解温度误标为沸点（如 IPP 17.2℃）→ state20 误判"气体"；沸点对有机过氧化物无实际意义，标 `—` + 备注分解温度/SADT。
8. **分子式多源冲突**：PubChem 与 chemicalbook 可能给不同分子式（叔戊基过氧新癸酸酯 C15H30O3 vs C15H28O4），用化学式原子计算裁决。
9. **IMA 精确查表**：CAMEO 文件是 3 字母缩写（CMH/BHP/ACT/VCM），搜英文名可命中（highlight 高亮），但
   folder_id 不严格限定、结果排序靠后；命中后 `fetch_media_content` 精确读单文件（含 NFPA/闪点/自燃/沸点/密度/蒸气压）。
   整本手册（化学化工物性手册等）只能命中"表号"定位，fetch 大文件超 token。
10. **IMA OpenAPI 直连走不通**：`~/.config/ima` 的 skill 凭证调 `openapi/wiki/v1/get_knowledge_list` 报
    `skill auth failed`（code 200002）——knowledge-base 操作需要用户级 OAuth，只有 MCP connector 有。
    **必须走 MCP 工具**，不能 Python 直连。
11. **批量分页必须用后台 Agent**：27 次分页 × 50 条会撑爆主对话上下文；且 connector-proxy 到 IMA 是
    **间歇性 fetch failed**（时通时断，非鉴权非限流）——用后台 Agent + 每页落盘 + `resume_state.json` 断点续传。
12. **PubChem 无中文名**：REST/PUG-View/网页版/description 接口全部验证无中文名——中文名只能 AI 翻译（CAMEO 导航场景）或经模板/chemicalbook 转 CAS（Step 0）。
13. **xlsx-js-style CDN 已下架（2026-08-17 实测）**：npm 包 `xlsx-js-style@1.2.0` 从 unpkg/jsdelivr 撤下（404），
    HTML 导出按钮若依赖 CDN 会静默失败（`XLSX undefined`）。**必须离线内置**：`scripts/xlsx-js-style.min.js`
    （来自本机 npm 包 dist/xlsx.min.js）由 gen_html.py 复制到 HTML 同目录。验证导出正确性用 Node 本地模拟
    （NODE_PATH 指向 node_modules，抽取 report.html 的 DATA/HEADER/COL_MAP 跑 exportExcel 逻辑，openpyxl 复核起始行 R9/样式）。
14. **母版 Excel 有"幽灵行"**：名称列空但 CAS 列有值的占位行（如二甲苯 3 个 CAS 拆 3 行只有首行有名）、
    以及 R96+ 的 `=IF(#REF!>0,#REF!,"")` 公式残留行。`export_excel.py` 找追加位置必须用「整行全空」判定，
    不能只看名称/CAS 两列（否则追加块会插到母版数据中间）。
15. **SheetJS 0 基 vs openpyxl 1 基行号换算**：模板数据从 Excel R9 起（1 基）= SheetJS `dataStart: 8`（0 基）。
    0 基 r=8 ↔ 1 基 R9。gen_html 导出 `var r = dataStart + i`（dataStart=8），export_excel `first_blank_row(start=9)`。
    搞反会导致数据整体下移一行。
16. **母版边框是"逐列分区设计"，不是统一网格**：hair 细虚线作底 + thin/thick/medium 分区边界实线 +
    合并单元格只在左上格存边框。数据区必须**逐列继承母版成品行样式**（首行/中间行/末行三套），
    不能套统一边框（会丢分区视觉）；表头 R1-8 可统一 thin（用户偏好）。
17. **openpyxl 单元格颜色三种来源**：`fgColor.rgb`（8位 hex）/ `fgColor.indexed`（索引色 41=浅青 CCFFFF）/
    `fgColor.theme`（主题色）。`_safe_rgb` 必须三种都解析，否则背景色丢失。
    **theme 索引是 Excel 内部顺序 lt1 dk1 lt2 dk2...**（非绘图顺序 dk1 lt1），theme0=lt1=window=白色。
18. **xlsx-js-style 对"有填充色的空值单元格"丢字体**（fill+font 组合的空值格写入时 font 被吞）——
    视觉不可见，属库底层限制，不必修。数据区和有值格字体完全正确。
19. **MergedCell 只读**：openpyxl 改合并单元格非左上格的 fill/border 会报错或被忽略。
    需先 `unmerge_cells` → 逐格改 → 重新 `merge_cells`；或直接用 `ws._cells[(r,c)]` 绕过 MergedCell 代理。
20. **大部头 PDF 提取（book_extract.py，2026-08-26 实测）**：《危险化学品安全技术全书》类书
    有文本层、按 GB/T 16483 的「第 N 部分」分节，逐行扫描状态机提取条目：条目标题 = 「第一部分 化学品标识」
    紧前独立行；CAS 只在「第三部分」且 `CASNo.` 标记后的第一数据行（否则会误抓正文里的其他 CAS）；
    理化字段同行可含多字段（如 "pH 值 无资料 熔点(℃) -95"），须解析整行全部字段而非只取第一个；
    "无资料/无意义" → 跳过不写（缺失≠无害）。2094 页提取 999 条 ≈ 1.8 分钟，索引 457KB。
21. **CRC 手册表格提取（book_extract.py --format crc）**：数据页表头含 "CAS RN"+"Mol. Form."（其余页跳过），
    行号（纯数字）是行锚点，列按 Name→Synonym→Formula→CAS→MW→PhysForm→物性顺序；**物性列须特征识别**
    而非固定顺序——部分行缺 mp/bp 会错位，且 mp/bp 同行合并成 "−114.14(0.03) 78.24(0.09)" 双值须拆分；
    密度（6 位小数 0.5~4）/折射率（1.3~1.7）也须用小数位特征区分。2643 页有机表区 3460 条 ≈ 45 秒，索引 839KB。
22. **兰氏手册15版提取（book_extract.py --format lange，2026-08-26 实测）**：文本型 PDF（Table 1.15 无图片
    OCR），行号=字母+数字（o11/e50）锚点，列 Name→Formula→Weight→Beilstein→Density→nD→mp→bp→fp→Solubility。
    **大坑：跳行条件里的 `\d+\.\d+` 会误杀所有小数数据行**（密度 1.06020 / 分子量 172.23 / 折射率 1.604020
    全被当页码跳过）——页码是 `\d+-\d+`（3-6）格式，不能用 `\d+\.\d+` 匹配。密度为 5 位小数（1.06020）
    不像 CRC 的 6 位，须 `\d\.\d{5,6}`。无 CAS 列，产出 list + `auto_supplement.match_lange()` 按名称查
    （归一化后词首匹配，避免 Acetone→Dichloroacetone 子串误匹配）。2709 条 ≈ 9 秒，索引 580KB。
23. **Perry 8th 临界常数提取（--format perry，2026-08-26 实测）**：TABLE 2-141 临界常数表
    （Cmpd.no→Name→Formula→CAS→MW→Tc,K→Pc,MPa→Vc→Zc→acentric），行号纯数字锚点。
    **坑：行号正则 `^\d{1,4}$` 会误匹配物性值**（乙醇 Tc=514 被当新行号导致 tc 丢失）——
    行号锚点须加"后一行是字母开头名称"的预读条件。Tc 单位 K（与危险品全书 ℃ 不同，
    book 优先填 ℃，Perry 只补 book 缺的字段）。254 条 ≈ 2 秒，索引 56KB。
24. **SARA 物性库提取（sara_extract.py，2026-08-26 实测）**：physical-properties sheet 1694 行×69 列
    = 基本信息(Tc/Pc/Mw/NBP) + 7 组 DIPPR 多项式系数(汽化热/蒸气压/气液 Cp/液密度/气液黏度)。
    **坑①：`read_only=True` 下循环随机 cell 访问卡死**（无报错无输出，进程假死）——必须去掉 read_only 加载进内存；
    **坑②：7 组系数 code 列偏移**（hvap=C7 / vp=C16 / cpg=C25 / cpl=C34 / denl=C43 / visg=C52 / visl=C61，每组 9 列 = code+tmin+tmax+6 系数），vp 在 C16 非 C17；
    **坑③：DIPPR 蒸气压式 `lnP = C1 + C2/T + C3·lnT + C4·T^C5`（P 单位 Pa、T 单位 K）**，
    算出 20/25/60℃ 蒸气压后**用沸点自检**（沸点处 P≈101325 Pa，丙烯酸 141℃→0.994 atm 验证）。无 CAS 列按名称匹配。1694 条，索引 2.2MB。
25. **TDG 危险货物表提取（tdg_extract.py，2026-08-26 实测）**：**中文文本层乱码（ToUnicode 映射损坏）
    但 UN 编号（4 位数字）与类别列（ASCII `1.1D`/`3`/`2.3`）可提取**——用 `get_text("words")` 坐标定位
    （UN x<90、主类别 x 200-260、副危险 x≈258 紧随）绕开乱码名称列。CAS→UN 映射来自危险品全书
    「第十四部分运输信息」（UN号+运输名称+危险性类别+包装类别，补提 section 14）。2311 条 UN 记录 + 957 种 CAS→UN。
26. **openpyxl 中部插列三连坑（2026-08-26 模板 106→111 列实测）**：①`insert_cols` 移动单元格值但**不移动合并区域**（残留错位）；
    ②`unmerge_cells` 批量删除合并区**崩溃（KeyError）**；③`merge_cells` 后**只保留左上角值**（非左上格值被清）。
    **结论：中部插列（需移动大量合并区）风险极高 → 改「尾部追加」零风险**（新列放 Remark 之后，不碰现有合并区）。
    若必须中部插列：备份→一步到位→「先写值再 merge」→重建合并区，且用 `ws._cells[(r,c)]` 绕过 MergedCell 代理。

27. **field_schema.json 的 num 是 0 基列索引（2026-08-26 实测）**：B=1…DG=110。gen_html 曾写 `col_map=num-1`
    导致整表左移一列；而 export_excel 用 `column_index_from_string(col)` 按字母定位本来就正确。
    **同一索引在两处消费者语义必须统一验证**（HTML 表头 vs 导出 Excel 列位），改 schema 后先跑
    Node 模拟导出逐格 diff 再交付。112 行数据区模板 106→111 硬编码处同步更新。
28. **PubChem 规范名 ≠ 常用名，SARA/CRC/Lange 本地索引按 name_en 匹配会 miss**（2026-08-26 实测）：
    resolve 后的英文名是 PubChem 规范名（propan-2-one、oxidane、hexane），本地书库索引用常用名
    （acetone、water、n-hexane）——auto_supplement 的 match_* 必须内置 ALIAS 别名表回退，
    否则补采静默跳过（无报错，纯漏数据）。main() 读 input.json 时字段键是 `r["resolved"]["name_en"]`。
29. **全书应急段提取（build_emergency_index.py，2026-08-27 实测）**：①条目组装时 **CAS 必须写进 rec dict**
    （漏写则按 CAS 过滤全部丢弃 → 0 条产出且无报错——首跑踩过）；②应急内容实际在第四~七部分（急救/消防/泄漏/操作储存），
    以 PDF 实际文本为准勿照抄 GB/T 16483 目录猜；③PDF 硬换行拆段 → 按「第N部分」切章后整章 clean_join 再用子字段锚点定位；
    ④页眉品名行 + 竖排页码数字（"3/0/1"三行）混入正文 → `is_noise` 过滤纯数字行；⑤子字段锚点需含书中原文变体
    （如「泄漏化学品的收容、清除方法及所使用的处置材料」）。
30. **ERG2024 Yellow Table 1 提取（build_erg_index.py，2026-08-27 实测）**：①**旋转 90° 表格 y 带定标勿凭直觉**——
    真实列序（y 小→大）= NIGHT.mi, NIGHT.km, DAY.mi, DAY.km, ISO.ft, ISO.m，已按 UN1005 官方值比对确认（day/night 写反会全表错且不易察觉）；
    ②**每条物料仅占一行**，Small/Large 两组值上下堆叠在同一列 y 轴（Small 上半 y222-372，Large 下半 y18-198）——
    同 UN 出现两次≠两行泄漏规模，而是**两个不同物料或交叉引用行**（1079=光气+二氧化硫；1082 R-1113 是 Trifluorochloroethylene 的 xref）；
    ③**名称带下界必须放宽到 y396**（斜体续行/water 变体下探到 y398，用 405 会裁掉 Trifluorochloroethylene 等首词）；
    ④**名称拼接按带内词自身 x 聚类分组**（阈值 3pt）各组 y 降序再连——用 `x < cx+9` 定主行会被浮点簇起点（38.5→39.0）坑成乱序名；
    ⑤同 UN 去重**有数值行优先为正条目**（交叉引用空行名收进 aliases），37 个 n.o.s. 泛称条目无距离值属 ERG 原版式非 bug；
    ⑥ERG 按 UN 键，补采借 book 物性索引 un_number 字段桥接（999 CAS→100 命中）。
31. **111 列大表列宽控制（gen_html.py，2026-08-27 实测）**：**td 的 width/min-width 在 auto 布局下被整表分配打败**
    （111 列挤压宽列回缩 ~90px，用户截图证实无效）——**必须 `table-layout:fixed` + `<colgroup>` 全列显式定宽 +
    `<table style="width:总宽px">` 写死**；**colgroup 第 0 列必须补 sticky 物料列的 `<col>`**（漏了整体错位一列，
    560px 落到前一毒性列、应急准则仍窄条）。JSON 列序重排/增列后先核对 colgroup 数量 = 表格总列数（含 sticky 首列）。
    验证渲染用 Edge headless：`msedge --headless --disable-gpu --screenshot=out.png file:///...html`（先注入
    `t.scrollLeft=t.scrollWidth` 截右端视图），眼见为实再交付，别让用户截图替你做验收。

## 二、实战经验归档（18 条）

- 2026-08-27｜[LRN-20260827-031]｜场景：布局反馈歧义（用户说"太宽"实指"太高"）｜经验：**布局类需求先对齐坐标系再动手**——用户口语里"列太宽/太高"可能指"内容太挤导致行高爆炸"，08-27 先按"减宽"做 v2（限宽 360px）被纠正"说反了"；正确动作是先截图当前渲染 + 询问"是列窄导致的换行多、行高爆，还是列太宽占屏"；**交付前用 Edge headless 渲染自截图**（注入 `t.scrollLeft=t.scrollWidth` 截右端），别让用户截图替你验收｜死路：①凭字面理解直接改（做反）②信 td width 在 111 列 auto 布局有效（回缩 90px）｜来源：B批 HTML 布局迭代 v2→v5｜计数：1｜状态：pending
- 2026-08-26｜[LRN-20260826-016]｜场景：field_schema 列序重排后 HTML/Excel 一致性验证｜经验：**HTML 所见即导出所得须双链路统一列索引**——num 是 0 基索引，gen_html 用 `col_map={key:num}`（勿再 -1），export 用字母定位；改完用 Node+xlsx-js-style 模拟前端导出与目标 xlsx 逐格 diff（表头+数据 0 差异才算过）｜死路：只改 HTML 不验证导出（所见≠所得）｜来源：111 列按 update.xlsx 重排｜计数：1｜状态：pending
- 2026-08-26｜[LRN-20260826-015]｜场景：openpyxl 母版 Excel 插列（106→111 列）｜经验：**中部插列三连坑 → 改尾部追加零风险**——`insert_cols` 不移合并区、`unmerge_cells` 批量删除崩溃(KeyError)、`merge_cells` 只留左上角值；新列放尾部（Remark 后）不碰现有合并区，与 Emergency 列同套路；必须插中部时「备份→一步到位→先写值再 merge→`ws._cells` 绕过 MergedCell」｜死路：中部插入（BL-BM/CE-CF 间隙，unmerge 批量崩溃两次）｜来源：111 列模板升级｜计数：1｜状态：pending
- 2026-08-26｜[LRN-20260826-014]｜场景：TDG 危险货物表 PDF 提取（乱码文本层）｜经验：**中文文本层乱码但 ASCII 列可提取**——UN 编号(4位数字)/类别(`1.1D`/`3`)是 ASCII，用 `get_text("words")` 坐标定位（UN x<90、类别 x 200-260）绕开乱码名称列；CAS→UN 映射走危险品全书 section 14（UN号+运输名称+类别+包装类）｜死路：①硬解中文名称列（ToUnicode 损坏，全是乱码）②只看正文引用页（P926 是引用，真表在 P203-679）｜来源：TDG 第23版 2311 条｜计数：1｜状态：pending
- 2026-08-26｜[LRN-20260826-013]｜场景：SARA 物性库 xlsm（DIPPR 系数）提取｜经验：**DIPPR 蒸气压式算 20/25/60℃ + 沸点自检**——`lnP=C1+C2/T+C3·lnT+C4·T^C5`(Pa/K) 算出三档蒸气压（丙酮 30.75kPa 误差<1%），用沸点处 P≈101325Pa 自检；7 组系数 code 列固定偏移（vp=C16 非 C17）；`read_only=True` 循环随机 cell 访问卡死→去 read_only｜死路：①read_only 模式随机访问（进程假死无输出）②code 列偏移 1 列（vp 全 0）③bash 中文路径跑 .py 静默崩（exit1 无输出）→走 PowerShell+英文路径副本｜来源：SARA v4.3 1694 种｜计数：1｜状态：pending
- 2026-08-26｜[LRN-20260826-012]｜场景：兰氏化学手册15版（文本型）表格提取｜经验：**文本型表比图片表好办，但跳行条件会误伤数据**——解析时用 `\d+\.\d+` 跳过"页码"导致密度/分子量/折射率全被吞（页面码是 `3-6` 破折号格式）→ 改 `\d+-\d+`；密度 5 位小数（1.06020）非 6 位；无 CAS 的表产出 list + 按名称匹配函数（归一化词首，禁子串）｜死路：①`\d+\.\d+` 跳行（小数数据全丢，mw 变 4）②名称子串包含匹配（Acetone 匹配 Dichloroacetone）｜来源：兰氏15 有机表 2709 条｜计数：1｜状态：pending
- 2026-08-26｜[LRN-20260826-011]｜场景：英文表格类手册（CRC）PDF 结构化提取｜经验：**「表头锚点 + 特征识别」**——数据页按表头特征串（CAS RN+Mol. Form.）判定、行号纯数字为行锚点；物性列不能用固定顺序（缺列错位），须按值特征分类（mp/bp=带精度后缀数值、密度=6位小数0.5~4、nD=1.3~1.7、溶解性=文本），同行双值（mp+bp 合并）须拆分｜死路：固定列序推进（Ethanol 密度被当 bp）、仅按数值范围分派（0.789320 被当 mp）｜来源：CRC97 有机表 3460 条｜计数：1｜状态：pending
- 2026-08-26｜[LRN-20260826-010]｜场景：大部头物性书 PDF 结构化提取｜经验：**「逐行扫描状态机」提取 GB/T 16483 编排的书**——部分标记（"第 N 部分"）驱动状态，条目标题=「第一部分」紧前独立行、CAS 仅第三部分 CASNo. 标记后第一数据行、理化行可含多字段须全解析；"无资料"跳过；2094 页 999 条 1.8 分钟｜死路：①按页取第一个部分号（同页多部分丢失）②全文搜 CAS（正文其他编号误抓）③只取行内第一个字段（同行 "pH 值 无资料 熔点(℃)" 丢 mp）｜来源：危险品安全技术全书通用卷索引｜计数：1｜状态：pending
- 2026-08-14｜[LRN-20260814-001]｜场景：前端导出按钮验证｜经验：HTML 的 SheetJS 导出按钮无法在浏览器外验证，本地用 Node 装 xlsx 模拟浏览器导出 + openpyxl 复核列位｜死路：直接盲信 SheetJS JS 代码正确（无法本地验证）｜来源：ray-chem-property 横版报告｜计数：1｜状态：pending
- 2026-08-14｜[LRN-20260814-002]｜场景：PubChem 数据抓取｜经验：API 文档不可尽信——PUG-REST 文档称支持实验物性，实测 MeltingPoint 等全 400，须走 PUG-View；且 GHS/NFPA 是 Information 的 Name/Value 对（非 TOCHeading）｜死路：凭 PUG-REST 文档猜测属性名直接解析（全 400）｜来源：ray-chem-property 检索主干｜计数：1｜状态：pending
- 2026-08-15｜[LRN-20260815-003]｜场景：IMA 批量分页遍历｜经验：connector-proxy 到 IMA 是间歇性 fetch failed（时通时断），27 次分页必须后台 Agent + 每页落盘 + resume_state 断点续传，网络恢复后从 next_cursor 无缝续传；末尾缺失条目可用 TITLE_DESC_SORT_TYPE 降序补齐｜死路：主对话里手动 27 次分页（撑爆上下文）或一次性重试（网络抖动即全丢）｜来源：CAMEO 1306 文件遍历｜计数：2｜状态：pending
- 2026-08-15｜[LRN-20260815-004]｜场景：批量 CAS 查询｜经验：英文名→PubChem name/cids→synonyms 提取 CAS 可行（正则 `\d{2,7}-\d{2}-\d`），1306 条 ~30 分钟；失败项用"简化名"重试（去括号/去 SOLUTION 后缀/OCR 修正 CHOR→CHLOR）可再补 ~74 条；fix 脚本必须边处理边落盘（一次性重写文件遇崩溃全丢）｜死路：一次重写 cas_results.jsonl（fix_cas 崩溃丢全部修改）｜来源：增强版导航构建｜计数：1｜状态：pending
- 2026-08-15｜[LRN-20260815-005]｜场景：中文名获取｜经验：PubChem 全接口（REST/PUG-View/网页版/description）均无中文名；中文名只能 AI 翻译（1306 条 5 批完成）或第三方源；IMA 客户端对话（完整 RAG）能查《物性数据手册》锌粉熔点 419.53℃ 这类整本手册精确值，而 MCP search_knowledge 只返回片段摘要（高频词稀释主体）｜死路：依赖 PubChem 中文名（100% 拿不到）｜来源：增强版导航 + IMA 认知修正｜计数：2｜状态：pending
- 2026-08-15｜[LRN-20260815-006]｜场景：物性数据全量本地化｜经验：**「本地索引模式」**——优先找官方「一次性全量数据源」（CAMEO 1306 文件清单 / EPA compiled AEGL PDF / DOE PAC Excel / 法规参考 md），下载后解析成按 CAS 的本地 JSON 索引，查询变本地秒查，远优于逐条在线检索；4 次成功应用（CAMEO 导航/AEGL 196/PAC 3063/法规 2552+295+244）｜死路：依赖 whpdj 等反爬网站逐条查（412/不可达）｜来源：ray-chem-property data/ 资产构建｜计数：4｜状态：pending
- 2026-08-17｜[LRN-20260817-007]｜场景：HTML 导出 Excel 与母版逐列样式对齐｜经验：**「三参照行逐列样式继承」**——母版成品区数据行边框/对齐/填充是逐列分区设计（非统一网格），数据区需抽「首行/中间行/末行」三套参照逐列继承（gen_html.py 的 rowStyles + extract_24.py）；首行顶线 medium、中间行 hair 网格、末行底线实线，名称列 left 对齐+solid 底色。对齐验证用 Node 模拟导出 + openpyxl 全量对比（3286 格 border/fill/align 零差异）｜死路：①套统一边框（丢分区视觉）②只抽 textStyle/numStyle 两种样式（丢逐列差异）｜来源：24 物料批量导出对齐｜计数：1｜状态：pending
- 2026-08-17｜[LRN-20260817-008]｜场景：openpyxl 颜色解析｜经验：单元格色有三种来源——rgb(8位hex)/indexed(索引色 41=浅青CCFFFF)/theme(主题色)，`_safe_rgb` 必须全解析；**theme 索引用 Excel 内部顺序 lt1 dk1 lt2 dk2...**（非绘图顺序 dk1 lt1），theme0=lt1=window=白色；indexed 色 alpha 00 需改 FF（00=全透明）｜死路：只认 8 位 hex（theme/indexed 色全丢，背景色消失）｜来源：表头背景色丢失排查｜计数：1｜状态：pending
- 2026-08-17｜[LRN-20260817-009]｜场景：合并单元格样式修改｜经验：openpyxl 的 MergedCell 只读——改合并区非左上格 fill/border 需先 unmerge→逐格改→重合并，或直接用 `ws._cells[(r,c)]` 绕过代理；xlsx-js-style 对「有填充色的空值单元格」写入时丢字体（fill+font 组合的空值格 font 被吞），视觉不可见属库底层限制｜死路：直接改 MergedCell.fill（报错或静默忽略）｜来源：表头边框统一 + 仅24物料生成｜计数：1｜状态：pending
