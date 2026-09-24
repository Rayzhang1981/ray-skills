# 验证工具箱（按需加载）

> 本文件是 SKILL.md「Step 5.5 / Step 6 / Step 7」与「COM 对拍台」的**详细配方**。
> 正文只留判断规则与一句锚点提示；要写代码/跑脚本时再来读这里。
> **节编号 = 门编号**：A 回执模板／B 离线自包含／C 运行时冒烟／D 人工感知／E 视口机检；COM 对拍台不带编号（v2.4.0 前编号为 D，与 D 门撞字母）。

---

## A. 交付回执模板（Step 5.5）

```text
artifact: <绝对路径>
artifact_sha256: <值>
artifact_bytes: <值>
A 确定性检查:   passed|failed|skipped   （比对点位 N，差异 M）
B 离线自包含:   passed|failed|skipped   （外部子资源 0 / 工程护栏 4）
C 运行时行为:   passed|failed|skipped   （断言 N/M）
D 人工感知:     passed|partial|failed|skipped   （截图 <路径> + DOM 探针 <路径>；无读图能力走 D0 机器代偿）
correction_rounds: 0|1|2
```

> 📌 **门字母以 SKILL.md Step 5.5 为唯一规范**：A 确定性／B 离线自包含／C 运行时行为／D 人工感知。
> ⚠️ **v2.4.0 修正**：本模板此前把 B 写成「运行时行为」、C 写成「感知评审」，**且整道「离线自包含」门缺失**——同一句"B passed"在 SKILL.md 与本文件指两道不同的门。已对齐（G1）。
> ⚠️ **四门必须逐个交代状态词**：未执行的门写 `skipped (缺什么)`，**不得省略**——省略会让读者默认四门全过（CHEF 4.5 承接复核轮实证：只做了 A/B/C，D 未执行也未报 skipped）。D 门无读图能力时**先走 D0 机器代偿**，不得直接写 `skipped`。
> ⚠️ **哈希必须写进交付件/交接件本身**（HANDOFF、README-P*.md），不能只留在会话报告里（G2）。

**五态状态词**：`passed` / `partial`（**仅 D 门机器代偿用**，见 D0；不许在 A/B/C/E 门使用）/ `failed` / `skipped`（**仅当环境不具备**，必须写明缺什么）/ ⚠️ 禁止把"运行失败或采集中断"归一化为 `skipped` —— 失败就是 `failed`。

**哈希命令**：

```powershell
Get-FileHash -Algorithm SHA256 <交付文件>
(Get-Item <交付文件>).Length
```

**修正轮次上限 2 轮**：两轮聚焦修正后仍不过 → 停下汇报（防无限返工掩盖真实设计问题）。

---

## B. 离线自包含断言（Step 6）

**判据**：交付 HTML 的外部子资源集合必须为**空数组**。

`assets/check_offline.mjs` 的拒绝清单（解析后逐项断言）：

| 位置 | 命中形态 |
|------|---------|
| `<link>` | `rel` 含 `stylesheet` / `preconnect` / `dns-prefetch` / `preload` / `modulepreload` / `prefetch` / `icon`，且 `href` 为远程 |
| `<style>` / 内联 `style` / `@import` | `url(//…)`、`@import //…` |
| 标签属性 | `src` / `poster` / `data` 为远程 |
| `<img srcset>` | 任意 `//…` 候选 |
| SVG | `<image>` / `<use>` / `<feImage>` 的 `href` 为远程 |
| `<iframe srcdoc>` | **递归**解析其内嵌文档，各自都要满足契约 |

**核心实现要点**：

```javascript
const REMOTE = (v) => /^(?:https?:)?\/\//i.test(v || '');   // 协议相对 //host 也要咬住
// 用 parse5 解析成 DOM 再遍历；不要正则扫全文
// iframe：attrs.srcdoc != null → inspectDocuments(attrs.srcdoc, `${subject}/srcdoc[${i}]`)
```

**必守三条**：
1. **解析**而非扫字符串 —— 注释与脚本字符串里的 URL 会误报，`srcdoc` 嵌套文档会漏检
2. 远程判定必须覆盖**协议相对** `//host/path`（最常见的漏网形态）
3. 失败处理是**把资源内联**（字体转 base64、库源码贴入、图标改内联 SVG），**不是**删断言或放宽判据

**脚本附带 4 项工程化护栏**（本生态高频真 bug）：localStorage 必包 `try`、`navigator.clipboard` 必先探测、尾零正则不得作用于整数、必须含溯源信息。

```bash
node assets/check_offline.mjs <交付文件.html>     # 零依赖
```

---

## C. 运行时行为冒烟测试（Step 7）

**为什么必须有**：数据与公式全对，页面仍可能整体不可用。CHEF 4.5 项目实证两个真 bug 在数据层验证下**结构性不可见**：

| # | bug | 后果 |
|---|-----|------|
| ① | `localStorage` 在 `file://`／隐私模式抛异常且未包 `try` | 主题初始化中断 → **后续全部脚本连崩、整页白屏** |
| ② | `navigator.clipboard` 在非安全上下文为 `undefined`，未探测即调用 | 抛未捕获 `TypeError`（复制/导出按钮直接失效） |

**骨架**：

```javascript
const { JSDOM, VirtualConsole } = require('jsdom');
const errors = [];
const vc = new VirtualConsole().on('jsdomError', e => errors.push(e.message));
const dom = new JSDOM(fs.readFileSync(html, 'utf8'), {
  runScripts: 'dangerously',
  pretendToBeVisual: true,
  url: 'https://local.test/',   // ⚠️ 必须给真实来源
  virtualConsole: vc
});
```

> ⚠️ **`url` 不给会退化成 opaque origin，`localStorage` 直接抛异常 —— 于是测试失败的是环境而不是产物，结论被污染。** 这是本文件里最容易踩的一条。

**必测断言**：

1. 页面加载无未捕获异常
2. 关键容器渲染出**预期数量**的子元素
3. 搜索／筛选真的收窄结果，且命中数与数据口径一致
4. 计算结果与数据层基准值一致（可独立算出的期望值）
5. 复制／导出等 API 缺失时走降级、不抛错
6. 主题切换、Tab 切换等主交互生效

**断言纪律（防"假 PASS"）**：

- 断言失败**必须返回 `false`**；禁止返回描述字符串冒充通过（计数函数会把错误信息当成功）
- 不写"命中数 > 0"这类无脑门槛，要写"与数据口径一致"
- 从错误集合剔除环境噪声（如 jsdom 未实现 `scrollTo`）时，**必须显式列出被剔除项**，不得静默过滤

**必要条件**：`npm i -D jsdom`（仅开发期，不进交付物）。无 node 环境 → B 层报 `skipped (node/jsdom unavailable)`，**不得**报 `passed`。

---

## D. 人工感知评审（Step 5.5 的 D 门）

> 判据：**人（或读图模型）真看渲染结果**。机检能覆盖的部分（视口溢出）见 E 节；本节管"真看"。

### D0. 无读图能力时的机器代偿路径（**降级，不是免检**）

> ⚠️ 旧版此门只有一句「无读图能力报 `skipped`」——那等于给 D 门留了个黑洞：**越是弱模型/无多模态环境，越容易整门跳过**，而 D 门恰恰是唯一能抓到「A/B/C 全绿但文本说错了」的门（见 D3 第二条实证）。故 v2.6.0 补代偿路径。

**能代偿什么（可量化的视觉事实）**：

| # | 代偿断言 | 替代"D 门的哪一眼" | 工具 |
|---|---------|------------------|------|
| ① | **元素真渲染**：容器存在性 + `minChildren: N` + 文本断言（把"应该出现什么"写成机器断言） | "看到页面有内容、不是白屏" | `probe_template.js` 的 `containers` / `asserts` |
| ② | **可辨性**：配对像素采样取 RGB → 算相对亮度 `ΔL` 与 `rel` | "这块板和背景看得出区别"（**近色板压近色墙的唯一机器抓手**） | `probe_template.js` 的 `samples` + `expectContrast` |
| ③ | **层级正确**：`elementFromPoint` 落点守卫（`must` 必中、`ban` 必不中） | "这个点量到的确实是那个元素，不是盖在上面的装饰层" | 同上，内建两道守卫 |
| ④ | **结构完整**：编码无乱码 / 标签配对 / 占位符零残留 / 关键 id·class 在位 | "看起来是完整交付件，不是半成品" | `struct_check_html.py` |

**代偿不了什么（必须明说）**：好不好看 / 版式是否失衡 / 视觉重心是否偏 / 是否误读了设计意图 / 色彩搭配是否得体。**这些只能人判，机器代偿后仍须在交付说明里留一句「主观视觉未复核」。**

**四步纪律**：

1. **先证检查器可信**：跑 `probe_template.js --selftest`（8 项夹具断言）+ `struct_check_html.py --selftest`（10 项）。**检查器自身错了却去改产物，会把好产物改坏。**
2. **采样前把缩放强制 100%**（用 `preSteps` 点缩放按钮 + `asserts` 断言结果，别靠假设）——低于 100% 会降采样糊化，更糟的是采样点**落在别的元素上**（实证：50% 时"板底"点落在铺满图位的 `<svg>` 上，量到的是"插图 vs 墙"，整组对比度数字全废）。
3. **判据从产物推导，禁写魔数**——阈值要么取自设计要求，要么取自本轮实测分布；写死一个"看起来合适"的数会把判据变成摆设。
4. **留痕可复核**：采样点坐标、命中元素 `tag`/`class`、`rgb`、`ΔL`/`rel` 一并写进 `--json` 结果或 DOM 探针件。**"机器代偿"的证据必须比"人看了一眼"更硬，否则不许叫代偿。**

**状态词写法**：
- 代偿跑通 → `passed (机器代偿：<工具> <项数> 佐证；主观视觉未复核)`
- 代偿只覆盖了一部分 → `partial (机器代偿：<覆盖项>；缺 <未覆盖项>)` —— ⚠️ **禁止把 `partial` 写回 `passed`**
- **连代偿也不可用**（无 node / 无 Edge / 工具缺失）→ 才写 `skipped (机器代偿不可用：缺 <具体什么>)`
- 代偿中抓到视觉缺陷（如对比度不足、落点压装饰层）→ 就是 `failed`，回 Step 7 改产物

### D1. 截图（零安装，用系统自带浏览器）

```powershell
$exe = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"   # 或 Chrome
& $exe --headless=new --disable-gpu --hide-scrollbars `
       --virtual-time-budget=8000 --screenshot="$out.png" `
       --window-size=1440,900 "file:///<绝对路径，分隔符用正斜杠>"
```

实测：CHEF 4.5 P4（1.26 MB）**3.3 s** 出图，中文目录名无需转义，但路径分隔符必须用 `/`。

### D2. ⚠️ 截图必须与 DOM 探针成对使用（本节最重要的一条）

**headless 截图常只捕获静态 DOM，不捕获 JS 生成的面板。** CHEF 4.5 P4 实测：**30 s 虚拟时间预算 + 3600 px 视口，正文区仍全空白**；而同一文件在 jsdom 里 `#chemList` 已渲染 **223** 行、`#chemCount` = 「223 / 223 种」、未捕获异常 0。
→ **只看截图就会把「捕获未含 JS 渲染」误判成「页面白屏」**（本轮差点据此报出假缺陷）。

配对探针（jsdom，`url` 必给）：

```javascript
const { JSDOM, VirtualConsole } = require('jsdom');
const errors = [];
const dom = new JSDOM(fs.readFileSync(html, 'utf8'),
  { runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://local.test/',
    virtualConsole: new VirtualConsole().on('jsdomError', e => errors.push(e.message)) });
const d = dom.window.document;
console.log(errors.length, d.getElementById('chemList').children.length,
            d.getElementById('chemCount').textContent);
```

**判读规则**：

| 截图 | DOM 探针 | 结论 |
|---|---|---|
| 有内容 | 有内容 | D `passed` |
| **空白** | **有内容** | **捕获 artifact，不是缺陷** → 记 `passed (DOM 探针佐证)`，必要时换窗口高度重拍 |
| 空白 | 空 / 有未捕获异常 | **真缺陷** → D `failed`，回 Step 7 排查 |

### D3. 判读纪律

- **绝不在未真正查看渲染结果时报 D `passed`**；无读图能力**不得直接报 `skipped`**——按 **D0** 先走机器代偿（凡能代偿的量化事实必须代偿），再写 `passed (机器代偿：…)` 或 `partial (机器代偿，缺主观判断)`；**只有连代偿路径都不可用**（无 node / 无 Edge / 工具缺失）才写 `skipped (机器代偿不可用：缺 …)`。未执行就写 `skipped`，不许省略。
- **D 门能抓到 A/B/C 抓不到的东西**（实战实证）：CHEF 4.5 的 P4 交付件——90 728 点位零差异、34/34 冒烟、零外部子资源**全绿**——**却把溯源 Footer 停在「P1 · 25 842 点位」**（实为 P4 · 90 728）。数值门永远看不见"写死的文本说错了阶段、说少了覆盖"。凡断言**覆盖率/阶段/来源**的文本，都必须在 D 门或专门的内容判据里对一次账。
- 视觉/版式类修改属"改动既有资产"，**先出清单再动手**。

---

## COM 对拍台（Excel 实算）

缓存值通常只有一个工况，**随机 + 边界工况对拍**才能证明引擎正确。用 COM 驱动 Excel **副本**实算（**只操作副本，绝不碰源文件**）：

```python
app = win32.DispatchEx('Excel.Application')
app.DisplayAlerts = False
app.AskToUpdateLinks = False        # 源文件常带指向缺失工作簿的外部链接
app.EnableEvents = False
app.AutomationSecurity = 3          # 禁宏，防弹窗
bk = app.Workbooks.Open(copy, UpdateLinks=0, ReadOnly=True)
sh = bk.Worksheets('<计算表>'); sh.Unprotect()
sh.Range('<输入单元格>').Value = 工况值
app.Calculate()                     # ⚠️ 用 Calculate，绝不用 CalculateFull
...读取结果单元格，与 HTML 引擎逐点位比对...
bk.Close(SaveChanges=False); app.Quit()
```

| ⚠️ 坑 | 症状 | 正解 |
|---|---|---|
| **`CalculateFull()`** | 含外部链接的工作簿上**实测卡死 10 分钟无响应** | 用 **`Calculate()`**，配 `AskToUpdateLinks=False` + `Open(UpdateLinks=0)`（实测 13 秒完成） |
| **进程清理** | `Stop-Process -Name EXCEL` 全杀会**误杀用户正在用的 Excel 会话**（已实际发生一次） | **精确 PID**：派发前快照已有 PID，收尾只清理本次新建者；或 `taskkill /F /PID <本次pid>` |
| 宏与弹窗 | 打开即弹"更新链接／启用宏" | `AutomationSecurity=3` + `EnableEvents=False` |
| 工作表保护 | 写输入单元格被拒 | `ReadOnly=True` 仍可 `Unprotect()` 后改内存值，但**绝不保存**（`Close(SaveChanges=False)`） |
| 只读源文件 | 误改用户原始数据 | 先 `shutil.copy2` 到临时目录再打开，源文件全程只读 |

**对拍要求**：每模块 ≥20 组工况（正常／边界／极值／零值），**全中间列比对**（不只最终结果）——只在终点比对，差异定位不了。

---

## E. 视口机检判据（感知层可机检的部分）

| 档位 | 判据 |
|------|------|
| 1440×900 / 1600×1000 / 1920×1080（+ 大屏加 2048×1320） | `document.documentElement.scrollWidth <= window.innerWidth` 且 `scrollHeight <= window.innerHeight` |
| 最大档位 | 额外目视：主面板与结论卡应**均衡占满**可用高度，不得塌成浅条 |
| 溢出时 | 先删**真正冗余**的内容或压缩间距，**不得**靠隐藏溢出、裁剪内容、加内部滚动条、缩小字号来"通过测量" |

> ⚠️ 窄屏/移动端允许纵向滚动，上述硬约束只针对桌面档位。

### E1. 必须**逐变体**跑，不能只跑默认态（v2.6.0 补，实测教训）

页面有**多个视觉状态**时（主题切换 / 风格切换 / Tab 切换 / 视图切换 / 折叠展开），**每个状态各自量一遍**——溢出与可辨性都是**状态相关**的，默认态全绿不代表别的态没问题。

**实证（双控文化墙任务，2026-09-18）**：「近色板压近色墙」这类真缺陷**只在某些变体上暴露**——四套风格里部分变体的板/墙 `ΔL` 逼近阈值。若只量默认态，会全绿放行。判据本身也来自这一轮：**不锁方向的"可辨性"** —— `|ΔL| ≥ minAbsL` **或** `rel ≥ minRel` **任一满足即通过**（深色风格靠 rel、浅色风格靠 ΔL，锁死单方向会把好产物判死）。

**机检写法**（`probe_template.js` 的 `samples[].click`）：先点该变体按钮 → 等过渡走完（`wait`，**过渡未完成会采到中间态**）→ 再取点。控件遍历（`controls`）逐项点完还要**回退到基线态**，验证"切换可回退"。

### E2. 纵向滚动的放行条件（机器判据，非人工通融）

| 产物类型 | 横向溢出 | 纵向溢出 |
|---|---|---|
| 看板 / 报告页 / 单屏工具 | **硬约束**：任何档位都不许有 | **硬约束**：必须整屏放下 |
| **效果图 / 文化墙 / 展板 / 长页文档** | **硬约束**：任何档位都不许有 | ⚠️ **纵向滚动是设计意图** → 须在验收配置里**显式声明放行**（`allowVerticalScroll: true`），并在报告中标注"允许纵向滚动" |

> **放行必须是显式的**：默认严格，是因为"忘了关"和"设计如此"从数字上看一模一样——显式声明这一步，就是逼验收人对"这是不是设计意图"表态。**横向永远不允许放行**（横向溢出只可能是缺陷）。

> 🧰 **可执行工具（零依赖现成实现）**：D0 与 E 的渲染量测在本生态已落地为 `ray-doc-toolbox` 的两个附带脚本——`assets/struct_check_html.py`（结构体检：编码 / 标签配对 / 占位符 / 关键 id·class / 硬编码色清单）与 `assets/probe_template.js`（无头 Edge 量测：多视口溢出 / 像素采样含两道守卫 / 文本断言 / 逐变体 `click` 采样 / 控件遍历回退 / 高清截图，配置驱动 + `--selftest` 自证）。**工序与采样纪律**见该 skill 的 `references/html-visual-sop.md`。**用之前先 `--selftest`。**
