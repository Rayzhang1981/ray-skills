# ray-pse-sharing — 踩坑经验全记录

> 本文件按需加载，SKILL.md 正文只保留核心流程与红线。
> 内容来自 15+ 轮迭代与多起真实事故卡片任务，按「核心教训 → 实战经验」组织。

---

## 一、核心教训（15+ 轮迭代总结）

1. **先定字数，再定字号** — 不要反过来。400/200/200 的字数基准是反复试出来的最优平衡点。
2. **字体无终点** — 每轮放大 1-2px，填满为止。没有人能一次猜对 A4 最佳字号。
3. **参考真实模板** — 化工行业单页分享模板（如 CCPS Beacon）的排版密度教会我们：一页 A4 可以承载远比想象中更多的信息。
4. **JSON 数据模型是灵魂** — 模板和管道只是壳，数据质量决定最终卡片质量。
5. **emoji 要差异化** — 统一前缀单调乏味，独立配图才有辨识度。
6. **PDF 是交付标准** — PNG 有分辨率问题，PDF 才是专业交付物。
7. **保护层分析 + HSE 工具 = 完整闭环** — 前者追溯失效，后者指明预防，缺一不可。
8. **`height` vs `min-height` 是血泪教训** — 固定高度 + overflow:hidden 会静默截断底部内容。宁可 `min-height` 让内容自然展开，也别用 `height` 硬卡。
9. **溢出先查容器，别急于压缩内容** — 遇到截断问题，第一步检查 CSS 容器约束（height / overflow），第二步才考虑压缩字号。

---

## 二、管道与文件系统（第 10-14 条）

### 10. 管道模板文件名与 pipeline.py 必须一致

**问题**：pipeline.py 中 `TEMPLATE_HTML` 硬编码了旧模板名，但 assets 目录下实际只有 `template.html`。SKILL.md 也写的是 `template.html`。三处不一致，首次运行直接 FileNotFoundError。

**修复**：pipeline.py 改为 `template.html`，并确认 `{{placeholder}}` 与 fill_template 替换逻辑兼容。

**教训**：修改模板文件名时，要同步更新 pipeline.py 中的常量。**SKILL.md 是真相来源，其他文件必须对齐。**

### 11. Edge headless PDF — Windows 路径三大坑

- **坑 1 — CJK 路径静默失败**：Edge `--print-to-pdf` 参数含中文路径会静默退出（exit 0），不报错但不生成文件。**解决**：先输出到不含中文的临时路径，再 `shutil.copy` 到目标。
- **坑 2 — 正斜杠路径不生成文件**：bash 风格正斜杠（`E:/<工作区>/out.pdf`）同样静默失败。**必须用反斜杠**（`E:\<工作区>\out.pdf`），Python `subprocess.run` 中传 `os.path.join` 默认反斜杠正确。
- **坑 3 — `file:///` URL 正常**：HTML 输入 URL 用正斜杠（`file:///E:/path/to/card.html`）不受限制。

### 12. 大 PDF 文件读取 — markitdown 桥接

**场景**：源 PDF >256KB 时 Read 工具拒绝读取。**解决**：先 `cp` 到工作区，再用 markitdown CLI 转 Markdown，最后 Read 读 .md。

```bash
# markitdown 需在 managed Python venv 预装：pip install 'markitdown[pdf]'
.../envs/default/Scripts/markitdown input.pdf -o output.md
```

### 13. 特殊 Unicode 文件名 — 先 cp 再操作

**场景**：PDF 文件名含中文弯引号（U+201C/U+201D），Read 工具无法定位。**解决**：用 bash glob 先复制到简单路径再操作。

**通用原则**：Read 报 FileNotFoundError 但 `ls`/`find` 确认文件存在时，别浪费时间调编码——直接 cp 到不含特殊字符的路径。

### 14. 多起同类型事故的合并卡片

**场景**：一个 PDF 报告涵盖同一企业一个月内两起同类事故，做一张合并卡片比分开两张更有冲击力——对比才能揭示系统性管理的溃败。

**做法**：
- `description` 用多段落：`【5·29 ...】\n\n【6·24 ...】\n\n总结段`
- `protection_failure` 提炼两起事故的**共性失效模式**（而非分开列）
- `accident_title` 用对比式标题（如"一月内两起...同类错误为何重复上演？"）
- `accident_info.date` 填两个日期；`severity` 合并统计

---

## 三、模板与符号控制（第 15-21 条）

### 15. takeaway `★` 星星策略——CSS 伪元素 vs 文本控制

**问题**：模板 CSS `.takeaway::before`/`::after` 伪元素与 JSON takeaway 字段中的 `★` 叠加，出现 `★★` 双星或截断星。

**修复**：彻底删除这两条 CSS 规则，星星完全由 takeaway 文本控制。

**原则**：装饰符号应由**数据层（JSON）**控制，非样式层（CSS）强加。CSS 伪元素是隐式装饰，用户看不见改不了，一旦冲突极难排查。

### 16. JSON 中文弯引号转义陷阱

**问题**：JSON 字符串内中文弯引号 `""` 导致 `JSONDecodeError`（U+201C 被误认字符串终止符）。

```json
// ❌ 报错
"低沸点溶剂去"推"高粘物料"
// ✅ 转义
"低沸点溶剂去\u201c推\u201d高粘物料"
```

**排查技巧**：JSON 报错先查行号附近中文引号，用 `\u201c`/`\u201d` 替换。

### 17. PDF 文件被预览占用——覆盖失败

**场景**：present_files 打开的 PDF 预览面板锁定文件句柄，`shutil.copy2` 覆盖报 `[WinError 32]`。

**解决链**：① `os.unlink(dst)` 先删 → ② 内容读写方式覆盖 → ③ `-v2` 后缀生成新文件。

**教训**：覆盖前先 unlink，不要假定 copy2 能直接覆盖打开的文件。

### 18. Edge headless PDF 超时回退

**场景**：pipeline 内置 Edge 调用偶尔 30 秒超时，但 msedge.exe 命令行正常。

**回退**：直接命令行打印（`--print-to-pdf` 用反斜杠 Windows 路径）。

### 19. 图片型 PDF 的 OCR 工作流

**场景**：源 PDF `fitz.get_text()` 返回 0 字符——纯扫描件，markitdown 也无法提取。

**工作流**：① PyMuPDF 转图片（`page.get_pixmap(dpi=200)`）→ ② Tesseract.js OCR（`node ocr.js page.png --lang chi_sim`）→ ③ 人工整合。`dpi=200` 是清晰度/速度平衡点。

### 20. PDF 渲染结果验证方法

**验证三步法**：① 查 HTML 源码（grep 目标 CSS/文本）→ ② PyMuPDF 转图片（`get_pixmap(dpi=150)`）→ ③ Read 工具肉眼检查。

**教训**：CSS 改没改对、PDF 是否被缓存、用户看到的是否最新——静态检查无法确认，**必须渲染出来看一眼**。

### 21. 文件覆盖后——强制刷新

**检查清单**：① `ls -la` 确认 mtime/size 最新 → ② PyMuPDF 转图片肉眼验证 → ③ 提醒用户关掉重开（或 Ctrl+F5）→ ④ 仍有问题用 `-v2` 后缀排除缓存。

---

## 四、示意图与内容精确性（第 22-26 条）

### 22. knowledge/what_to_do 栏前缀符号策略

**决策**：不在模板/管道硬编码添加前缀符号（如 `•`）——保持 JSON 层控制。与第 15 条（takeaway ★）一脉相承：**装饰符号由 JSON 控制，CSS 不做隐式装饰**。

### 23. 示意图与事故场景精准匹配——新建专用类型

**问题**：用错示意图会让读者产生错误事故联想（如用 thermal_runaway 画保温棉自燃）。

**做法**：现有类型无法匹配时，**新建专用示意图函数**，不凑合用最接近的。

### 24. 技术描述必须精确（蓄热自燃 vs 常温自燃）

**问题**：初版写"接触空气氧化放热可自燃"，误导读者以为导热油一接触空气就烧。

**精确表述**：高温导热油（~280-320℃）渗入多孔保温棉产生"灯芯效应"扩展表面积，空气氧化放热而保温层阻散热，蓄热累积超自燃点（~350-380℃）着火。浸渍保温棉须整体更换，表面擦拭无效。

**教训**：knowledge 栏是技术根因总结不是科普，务必区分 pyrophoric（常温自燃）与 self-heating（蓄热自燃）。

### 25. 示意图注册——三处同步

新建示意图函数后必须同步三处：① 定义函数 ② 注册 `GENERATORS["xxx"]` 映射 ③ auto-detect 加关键词。漏一处会 fallback 到 generic。SKILL.md 的 Image 类型表也要更新。

### 26. 信息脱敏——地点替换为通用代称

脱敏在 **JSON 数据源层**完成（`replace_all` 全文替换 location/title/description），不要在 PDF/HTML 层改，否则重新生成时脱敏丢失。

---

## 五、渲染引擎与批量生产（第 27-28 条）

### 27. Edge headless 静默失效 → Playwright 回退（2026-08-02 包钢任务）

**问题**：本机 Edge headless `--print-to-pdf` 完全静默失败——`--dump-dom` 无输出、exit 0、stderr 空。尝试 `--headless=new`、`--no-sandbox`、独立 `--user-data-dir`、`--virtual-time-budget` 均无效。疑似 Edge 被策略锁定（非 CJK 路径问题，纯 ASCII 路径也失败）。

**回退方案（已验证可靠）**：Playwright + Chromium headless-shell：
- venv：`~/.workbuddy/binaries/python/envs/default/Scripts/python.exe`
- 浏览器：`chromium-headless-shell`/`chromium-1223`（ms-playwright 已有）
- playwright 报 `__dirlock` 错误时删 `$LOCALAPPDATA/ms-playwright/__dirlock` 重试

**渲染要点**（模板见 assets/playwright_pdf.py）：
1. **必须用同步 API**（`playwright.sync_api`），async 在本机 exit 1 无输出
2. `page.pdf(format="A4", print_background=True, prefer_css_page_size=True)` 保持 min-height:297mm 语义
3. `page.goto()` 后 `wait_for_timeout(1500)` 等 SVG/字体渲染完
4. PDF 先输出 TEMP 纯 ASCII 路径，再 `shutil.copy` 到中文目标路径
5. 脚本 print/traceback 常被吞（exit 1 无输出）——别依赖 stdout，直接检查目标文件是否生成

**教训**：Edge 失败试 2-3 种组合仍无效就直接切 Playwright，时间成本最低。此问题与第 11/18 条（CJK 路径、超时）根因不同。

### 28. 批量生产渲染并发坑（2026-08-12 PSE 193 份任务）

**批量场景**：多子代理并行共用同一 temp HTML 路径或多个 chromium 实例同时渲染，导致 PDF 异常分页（1 页内容撑成 2-6 页）。

**解决（三选一并行，推荐组合）**：
1. **HTML 路径唯一化**：默认 `card_{pdf_stem}.html`，各进程互不覆盖
2. **串行渲染**：for 循环单进程顺序调用，不起多个 chromium 并发
3. **渲染必须前台执行**：后台任务环境下 chromium 启动卡死

**子进程调用渲染脚本大坑**：
- ❌ `os.system("python batch_card.py ...")` — cmd.exe 解析含中文路径报错
- ❌ `subprocess.run([...], capture_output=True)` — chromium 后代进程继承 stdout 管道，communicate() 永不返回 → 120s 超时
- ✅ **同进程 import 渲染函数**：`from batch_card import render_card; render_card(jf, pdf)`，顺序循环，每次 with sync_playwright() 独立启闭

**沙箱 SAFE_DELETE 坑**：os.remove/os.unlink 被沙箱拦截，**不要用文件锁做跨进程同步**（锁删除失败残留 → 死锁）。用 HTML 唯一路径 + 串行即可。

**事故日期确认（文件名≠事故日期）**：微信文章转 PDF 文件名后缀年份是**发布年份**不是事故年份！事故日期从正文提取，写入 `sort_date`（YYYYMMDD），PDF 命名 `{sort_date}-{标题}.pdf` 按年代排序。

**内容长度与单页约束**：描述 >380 字 + knowledge >200 字 + hse_tools >8 条会把 footer 挤出第 1 页。批量 JSON 控制：描述 ≤380 / knowledge ≤200 / what_to_do ≤180 / hse_tools ≤8。

**批量验收（无图像模型时）**：用 fitz 纯文本层验证——页数=1、第1页含 ★、含品牌串、无 `\ufffd`。

**批量流水线脚本（PSE Sharing 目录）**：
- `extract_text.py` — fitz 批量提取 PDF 文本
- `batch_card.py` — 渲染单卡（render_card 可 import 复用）
- `rerender_all.py` — 批量重渲 + 自动验证页数
- 黄金示例 JSON：`_json/_GOLDEN_EXAMPLE.json`（风格锚点）

---

## 六、批量续产与质量基建（第 29-35 条，2026-08-29 148 项批次）

### 29. 历史锚点台账法（已被第 36 条数据库法升级取代）

**问题**：148 卡批量中同一锚点被反复复用——台账统计 Norco 12 次 / BP德州 10 次 / Buncefield 9 次 / 昆山中荣 8 次，远超合理密度。读者连看三张卡都是同一场事故，history 金色带失去「差异化警示」价值。

**机制**：建 `anchor_library.md` 锚点池（按 12 类型分组，~60 条）+ `anchor_ledger.py` 台账脚本（扫描全部 JSON 的 history 字段统计使用次数）：
- **同一锚点全套最多用 3 次**，已达上限的锚点停用【v1.9 废止——重要事故允许反复使用，防的是"相邻卡扎堆"不是"总量"】
- **零使用锚点优先调度**：台账列出 23 个零使用条目（受限空间 7 / 静电 6 / 装卸车 4 几乎全闲置），写新卡先从这里挑
- **聚类预判**：批次开工前对剩余条目按事故类型聚类（如泄漏 33 / 火灾 25 / 人身 18 / 爆炸 12），预判哪类锚点将紧缺，提前突围

**教训**：锚点是稀缺资源。批量前先跑台账再动笔，不要写到哪算哪——写到后半程才发现无锚点可用只能硬凑。

### 30. 批量 precheck 三档语义（P0 / EN 白名单 / legacy）

**问题**：25 张卡人工目检是注意力极限；但自动预检首版误报泛滥——GB/LEL/SDS/DV/XV 等正常术语被当英文残留，213-277 字的 description 被判过短（阈值 280-440 定得太严），每轮十几条假警报淹没真问题。

**机制**：precheck.py 三档语义：
- **P0 必修**：JSON parse 失败 / 必填字段缺失 / 脱敏词残留 / `\ufffd` 乱码 / PDF 页数≠1 / footer 编号缺失——零容忍
- **EN 白名单**：60+ 正常术语白名单（GB/LEL/SDS/SSR/DV/XV/DN/MOC/NBR/PTFE/CO/VOC/mJ/RH/kV/AC/RCO/LOTO 等），白名单外连续英文单词才报
- **`--legacy` 档**：早期卡（v1.0 时代 history=1/knowledge=3 属基线）放宽检查不阻塞——用 `LEGACY_CARDS` 集合分档，区分「早期基线」与「真缺陷」

**教训**：预检阈值必须先跑一轮统计实测分布（如 description 实际 213-380 字）再定；假警报比没有警报更危险——它会训练人忽略警报。

### 31. 文件清理走回收站 + exists 复核（rc 不可信）

**问题**：73 张 QC 截图（17MB）用 `SHFileOperationW + FOF_ALLOWUNDO` 回收站删除，batch 模式（`\0` 连接多文件）返回 rc=2 报 FAILED——但文件实际已删。加 `_pack_(1)` 想修 rc 反而崩 access violation。

**解法**：
- 结构体保持默认对齐 + `argtypes/restype` 显式声明 + 单文件循环拼接
- **rc 仅作参考，删除成败以 `os.path.exists` 复核为准**（本环境 hook shell32 导致 rc 不可信）
- **不要用 `os.remove`**：沙箱 SAFE_DELETE 拦截且不可恢复；回收站删除给用户留反悔余地

**教训**：清理中间产物（QC PNG/临时 HTML）是批量标配动作，删除一律走回收站 + 事后 exists 复核双确认。

### 32. 已重命名 PDF 按编号前缀匹配

**问题**：预检按事故 type 主干重建文件名找 PDF，但交付 PDF 已按 `{编号}-{标题}.pdf` 规则重命名（type 主干 ≠ 实际文件名），014/016/017/018/028 全部误报「PDF 缺失」。

**解法**：`find_pdf(n, data)` 用 footer.number 编号前缀 glob 匹配（`*-{n:03d}-*.pdf`），不依赖 type。

**教训**：验证脚本要匹配「交付物的实际命名规则」，不要按「生成时的中间名」反推——文件会被重命名，编号不会。

### 33. description 字数实测基线 240-440（380 是溢出红线不是下限）

**问题**：文档写「≤380 字」被当成唯一约束，实际两极误用：有的卡 440 字没溢出，有的卡 213 字底部大块留白。

**实测基线**（A4@96dpi，stack 布局）：
- **下限 ~240 字**：062/068 卡 213/238 字实测底部留白明显，扩写失效链细节至 252/288 字解决
- **上限 ~440 字**：stack 布局实测仍未挤出一页，但 >380 必须逐卡验证页数

**教训**：字数约束分两层——「溢出红线」（硬性，模板决定，precheck 报错）和「饱满区间」（软性，实测决定，precheck 报警告）。

### 34. diagram_type 非规范名静默 fallback generic

**问题**：写卡时用了直觉性名称（explosion/fire/pipe/tank/filter/pump/reactor/splash），渲染全部 fallback 成 generic 瑞士奶酪图——无专属 SVG、无 FAILURE_ANCHORS 红圈标注，违反「示意图标注式」规范但渲染不报错。

**解法**：只用注册过的规范名：`explosion_fire / gas_leak / isolation_failure / insulation_fire / thermal_runaway / gas_holder / spherical_tank_bleve / thermal_oil_dry_heating / generic`。precheck 加 diagram_type 合法值校验。

**教训**：fallback 机制是静默降级——「能渲染」≠「渲染对了」。枚举类字段必须在数据层校验合法值。

### 35. 批量质量基建三件套（写卡→生成→预检闭环）

**机制**（2026-08-29 确立，049-073 批次 25 张零返工验证）：
1. **gen 脚本一体化**：JSON 校验 + 必填字段 + 脱敏词扫描 + PDF 页数自检写进同一生成脚本；支持单卡过滤参数（`gen.py 66`）断点重生成
2. **precheck 前置**：文本层问题（脱敏/乱码/字数/编号）全部自动化；人工目检只看「版式溢出/图表错位」两类机器看不出的问题
3. **consistency_check 批后跑**：8 维数值分布 + 结构检查（三段式/★/brand/emoji）+ 编号连续性，informational 输出——保证全套统一性

配套：`desens_vocab.py` 脱敏词库模块化（BASE+COMPANY+PERSONS），生成与预检共用同一词库，两处口径一致。

**教训**：批量 >20 张时，质量保证必须从「人工逐张看」升级为「脚本防线 + 人工抽检」；把检查逻辑写进生成脚本是性价比最高的防线。

### 36. 锚点数据库 + 典型性毕业机制（v1.9，2026-08-29 用户定型）

**演进**：台账法（第 29 条，anchor_library.md + 3 次上限）→ 数据库法（assets/anchor_db.json + scripts/anchor_db.py）。升级动因：①台账脚本只扫已发卡范围，新批次用了已满锚点无告警（074-098 批实际漏拦 12 处）；②md 表格无别名机制，Norco/昆山中荣/DPC 多写法统计漂移；③「3 次上限」规则方向错误被用户纠偏。

**用户定型三原则（设计依据，不得回退）**：
1. **首要任务是扩库**——尽量涵盖各类事故类型（特别是工艺安全），量足够大才能「快速定位直接应用」；量大后靠典型性复审动态更新，不是靠限制使用
2. **典型性三条款**：a.事故影响大、较为知名；b.与事故类型适配；c.新事故优于旧事故（特别出名的经典除外）
3. **毕业 = 典型性复审**（`review --retire --reason`），不考虑用过几次、会不会重复——「我们做的是事故分享，重要事故就是反复揣摩学习，真正实现事故中成长」

**机制**：
- **分级**：S（经典知名：博帕尔/Piper Alpha/Flixborough/BP德州/天津港等，不限次数跨类型优先）/ A（典型行业事故，本类型首选）/ B（补充案例，复审不达标淘汰）
- **生命周期**：pending（未核实，不得入卡）→ active（可用）→ retired（典型性复审淘汰）；**新锚点必须 WebSearch 核实三要素后才 verify 转 active**
- **写卡调度**：`anchor_db.py pick <类型>` 输出 S级优先→年份新→批内少用 排序的推荐池
- **批后对账**：`anchor_db.py scan-cards <目录>` 全量扫描；硬违规仅两种（pending/retired 被引用）；批内同锚点≥3次仅软提示（防相邻卡扎堆，不强制）
- **库外标签**：扫描会列出不在库中的 history 写法——应补录入库（含别名）而非放任漂移

**教训**：质量规则设计先问「这个规则的目的是什么」——防扎堆用软提示就够，硬上限反而把重要事故挡在门外；台账/数据库扫描范围必须覆盖全部卡片（含未发批次），否则拦截形同虚设。

---

## 七、实战经验速记

| 日期 | 场景 | 经验/教训 |
|------|------|-----------|
| 2026-08-03 | bash 调用 Playwright 渲染 | bash 内联 Python 含反斜杠转义必炸（SyntaxError），一律 Write 脚本文件再执行 |
| 2026-08-03 | 渲染脚本 exit 1 无输出 | Playwright print/traceback 被吞是常态，别重试别调试——直接 `ls` 临时 PDF 是否存在，存在即成功 |
| 2026-08-03 | cp 复用渲染脚本改路径 | 路径替换要同时改目录+文件名两段，只 replace 文件名会把 PDF 写到旧目录 |
| 2026-08-24 | 布局自动选择 | 文档写「描述>400 **或 条目多**→stack」但代码只实现字数阈值（旧250/新400），标准卡片（5知识+5行动）误走 side → 右侧「你能做什么」大片空白。已补 `or n_know>=5 or n_act>=5`。教训：文档的多条件判断，代码必须逐条实现，不能只实现第一条 |
| 2026-08-28 | playwright browser.close() 挂起 | default venv 中 `browser.close()` 会**永久挂起且吞掉全部 stdout**（exit 1、空输出，极似「bash 中文静默崩」但与路径无关，about:blank 也复现）。QC 批量截图脚本：**不调 browser.close()**，`p = sync_playwright().start()` 手动管理、结束时 `p.stop()`，print 全部加 `flush=True`。二分法定位技巧：逐步加语句跑 `about:blank` 最小用例，看哪一步 stdout 消失 |
| 2026-08-28 | history 单元溢出排查 | 加 history 金色带后总高超 A4（1123px@96dpi）时，用 page.evaluate 逐区块量 getBoundingClientRect().height，与单页 OK 的卡对比各区块高度差，精准定位超高原。实测：001 卡 history 3条标签换行多占 32px（94 vs 62）——history 标签控制在 2 条或保证总宽不换行，再砍 1 条冗余 knowledge 即回单页。修复优先级：砍冗余 knowledge 条 > 精简 history 标签字数 > 动模板字号（最后手段） |
| 2026-08-28 | history 锚点真实性红线 | history 条目**必须逐条 WebSearch 核实**（年份/伤亡数/事故原因三要素），用户红线：「客观准确，不为凑数编造，没关系硬联系；没有就去掉单元」。实测 13 卡 26 条中 12 条有问题：年份错（山德士1988→1986）、伤亡数错（天津港725吨173人→800吨165+8失踪；Norco 42伤→48伤）、**查无实据**（2018泰兴RTO 2死、2019放料阀2死、2021高雄集尘4死、Boeing 1977铝粉、Finbow 1980、1976英国重氮化釜、2020山东装卸车——多为「看似合理」的编造）、**硬联系**（响水天嘉宜写成「仪表报警忽视」——实际是硝化废料自燃；007/008 把本卡事故放进 history）。修正原则：查实才留、改用权威口径（应急管理部/国务院调查报告/CSB/维基多源交叉）、无可靠锚点清空 history 字段（模板自动不渲染） |
| 2026-08-29 | 锚点换实体只改 label_30 | 锚点改用另一条事故时只改 label_30、漏改 event/aliases → scan-cards 把已入库锚点误报「库外标签」（ANC-096 误报 6 张卡）。换实体必须同步 event+aliases+label_30，核实后置 verified=true；aliases 要覆盖带省份前缀的完整写法 |
| 2026-08-29 | history 年份手打漂移 | 同一锚点在 7 张卡里出现 2024/2023/2019 三种年份（凭记忆手打）。history 整行复制 label_30 原文，不手打年份 |
| 2026-08-29 | 库外标签的两种成因 | scan-cards 报「库外标签」= ①卡内写法/年份错（改卡）②库内 event/aliases 缺该写法（改库）。先读 match_anchor/norm_label 判定逻辑再归因，不要一律当卡错 |
| 2026-08-29 | 承接长任务先实测磁盘 | 会话总结称「剩 37 张未写」，实测 001-148 全在。压缩态上下文滞后于磁盘，承接点以磁盘实测为准（ls + 字段校验），不信总结 |
| 2026-08-29 | glob 假阴性 | ls card_*.pdf = 0 差点误判「PDF 全未渲染」，实际命名是 {编号}-{事故名}.pdf。否定产物存在前先用多种 pattern 交叉验证 |
| 2026-09-04 | SIGTERM 怪癖根因 = skill 自带反模式（自举悖论实例） | 9-4 会话每张卡渲染 exit 1 无 stdout（SIGTERM），一直当「沙箱怪癖」绕过（PDF 落盘后靠文件存在性验证）。**根因查明：batch_card.py 与 skill 自带 pipeline.py 都在用 `with sync_playwright() + browser.close()`——正是红线#31 明令禁止的反模式**（close() 本环境永久挂起 → 沙箱杀进程树 → SIGTERM）。两处均改 `pw = sync_playwright().start()` + try/finally `pw.stop()` 后，同一命令 A/B 验证：exit 1 → exit 0、stdout 完整。教训：红线写了自己不遵守；「绕过怪癖」的容忍让反模式存活了多个会话——下次遇到「已知怪癖」先问「是不是有人在违反自己的红线」 |
