# 坑点与经验（按需加载——遇到对应问题再读）

> 来源：已发布 v1.0.1 完整版恢复。
>
## 常见坑点与修复经验

### 坑点 1：JS 顶层代码 null reference 导致整个 `<script>` 中断

**现象**：页面功能完全无反应（按钮点击无效果、无报错提示）

**根因**：CSS 定义了某个组件的样式，但 HTML body 中缺少对应 DOM 元素。JS 在 `<script>` 顶层对查询结果调用方法时抛出 TypeError，导致**整个 `<script>` 块被中断**，后续所有函数定义全部丢失。

**典型案例**：
- CSS 中定义了 `.theme-toggle` 样式（含 `.sun-icon` / `.moon-icon` 子元素）
- HTML body 中**没有** `.theme-toggle` 元素
- JS 执行 `document.querySelector('.theme-toggle').addEventListener(...)` → 返回 null → TypeError
- 结果：`setMode()`、`calc()`、`toast()` 等函数**全部未定义**
- 表现：模式切换按钮点击无反应、计算按钮点击无反应

**修复方案**：
1. 确保 HTML 中有 CSS 引用的所有 DOM 元素（添加缺失元素）
2. JS 中所有 DOM 查询后做 null 检查，或将事件绑定包裹在 IIFE 中

```javascript
// ✅ 正确做法：包裹在 IIFE + null 检查
(function() {
    const toggle = document.querySelector('.theme-toggle');
    if (toggle) {
        toggle.addEventListener('click', () => { /* ... */ });
    }
})();
```

### 坑点 2：`calc()` 函数缺少 try-catch

**现象**：计算时报错，但页面无任何提示，用户不知道发生了什么。

**修复**：给 `calc()` 包裹 try-catch，错误信息通过 toast 显示：

```javascript
function calc(){
    try {
        // ... 计算逻辑 ...
        toast('✅ 计算完成');
    } catch(e) {
        console.error('Calculation error:', e);
        toast('⚠️ 计算出错: ' + e.message, true);
    }
}
```

### 坑点 3：输入框未绑定 oninput 导致实时计算不触发

**修复**：所有 `<input type="number">` 均需绑定 `oninput="triggerRealtime()"`（详见下方「实时计算模块」章节）

### 坑点 4：DOM ID 重复导致 getElementById 只返回第一个

**现象**：SVG 区域和表格中使用了相同的 `f_ball` 等 ID，导致 JS 只能操作第一个元素。

**修复**：
- 确保 每个 `id` 在整个 HTML 中唯一
- 合并面板后自然消除了重复 ID
- 删除旧的 `.ft-wrap` 表格区域（或设为 `display:none` 隐藏而非删除，避免样式引用断裂）

---


---

## 坑点 5：Edge 浏览器中 tip 弹出框表格第一列不显示/显示不全

**严重程度**：⭐⭐⭐⭐⭐（仅 Edge 复现，Chrome/Firefox 正常）

### 现象

在 `position: absolute` 的 tooltip/tip 弹出框内使用 `<table>` 显示预设值参考表时：
- **第一列（如 β/d₀/D 列）被截断或完全不显示**
- 第二列（如 C 参考值）正常显示
- 截图显示第一列数字只露出最右侧 1~2 位

**已复现环境**：Microsoft Edge（Chromium 内核），Windows 11

### 根因分析

Edge 对 `position: absolute` 容器内复杂 `<table>` 结构存在渲染 bug：

| 因素 | Edge 行为 |
|------|-----------|
| `<colgroup>` + 固定列宽 + `!important` | **忽略**所有强制宽度设置 |
| `table-layout: fixed` + `!important` 覆盖 | `!important` 与 Edge 渲染引擎冲突，规则失效 |
| `thead` / `tbody` 结构化标签 | 触发 Edge 特殊渲染路径，列宽分配异常 |
| 默认左对齐 + 长内容 | 左侧溢出容器边界被 clip |

**关键发现**：同一项目中「管道压力降」页面的 tip 表格（管壁粗糙度参考）在 Edge 中**正常显示**，其结构为极简模式。

### ✅ 最终解决方案（4 轮迭代验证）

#### ❌ 第 1~2 轮：失败方案

```
方案1: table-layout:fixed + !important 强制列宽     → Edge 忽略 !important
方案2: 合并两列为单列（β和C用<br>换行）              → 更糟，全白
```

#### ✅ 第 3~4 轮：成功方案

**核心策略：最大简化 table 结构，照搬已验证可用的参考文件**

```html
<!-- ✅ 正确 HTML 结构 — 极简模式 -->
<div class="tip">
    <div class="tip-head">流量系数 C 近似值参考表</div>
    <table>
        <tr><th>β (d₀/D)</th><th>C 参考值</th></tr>
        <tr><td>0.20</td><td class="tv" onclick="fillC(0.60)">0.60</td></tr>
        <!-- 更多行... -->
    </table>
    <div class="tip-foot">点击数值自动填入，或手动输入实测值</div>
</div>
```

**要点**：
- ❌ 不用 `<colgroup>`
- ❌ 不用 `<thead>` / `<tbody>`
- ✅ 用裸 `<table>` + `<tr>` / `<th>` / `<td>`
- ✅ `width: 100%` + `table-layout: fixed`（让浏览器均分列宽）

```css
/* ✅ 正确 CSS */
.tip table {
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;        /* 关键：均分列宽 */
}
.tip th, .tip td {
    padding: 6px 6px;           /* 收紧内边距，留更多空间给内容 */
    text-align: center;         /* 关键：居中对齐防止截断 */
}
.tip .tv {
    font-family: var(--font-mono);
    font-weight: 600;
    color: var(--brand);
    cursor: pointer;
    /* 不要设 text-align:right，统一 center */
}
.tip-foot {
    text-align: center;
    padding-left: 24px;         /* 微调提示文字位置 */
}
```

### 经验总结清单

| # | 检查项 | 通过标准 |
|---|--------|----------|
| 1 | 无 `<colgroup>` | 已删除 |
| 2 | 无 `<thead>` / `<tbody>` | 已删除 |
| 3 | 有 `table-layout: fixed` | 两列均分宽度 |
| 4 | 单元格 `text-align: center` | 居中防截断 |
| 5 | 无任何 `!important` | 避免与 Edge 渲染冲突 |
| 6 | padding 收紧至 ≤ 6px | 为内容留空间 |

**参考文件**（已验证 Edge 正常）：`D:\RayClaw\PE Calculation\01-Pipelines\不可压缩流体压力降计算-Pipe Pressure Drop-V1.1.html` 中「管壁粗糙度 ε ⬡ 参考」的 tip 表格

---


---

## 坑点 6：工程标准关系图（C-Re-d₀/D 等）的处理策略

> ⚠️ **v2.4.0 补注——本节结论受硬约束限制（G4）**：Step 3/6 已把「**零外部子资源**」定为单文件交付的**硬约束**（明确禁外链图片）。
> 故下文「**外部图片 + 同目录部署**」**仅适用于不要求单文件交付的场景**；**单文件交付必须把图内联**——base64 内联（体积 ×4/3，工程查图表通常可接受）或改内联 SVG/Canvas 重绘。
> 下文「为什么不用 SVG/Canvas 重绘？」的结论表（把 Base64 内嵌列为缺点、结论"外部图片最务实"）**只对多文件部署成立**，单文件交付下不适用。
> 教训通式：**硬约束升级时，改动范围不是"写约束的那一节"，而是整个资产里所有与之冲突的表述**——references 走"按需加载"，老章节的违规要等读者真去查时才引爆。

### 问题场景

化工计算工具常需引用**工程标准中的曲线图/图表**（非公式可表达），例如：
- HG/T 20570.15-95 图 5.0.4：限流孔板流量系数 C 与雷诺数 Re 及 d₀/D 的关系图
- 摩擦系数 λ-Re 曲线（Moody 图）
- 其他标准查图表

这些图的共同特点：**无法用数学公式精确表示**，用户需要"看图查值"。

### 推荐方案：外部图片 + Tab 页懒加载 + 全屏放大

#### 方案架构

```
┌─────────────────────────────────────┐
│  [设计计算] [操作计算] [关系图 ★]    │ ← Tab 切换
├─────────────────────────────────────┤
│                                     │
│      ┌───────────────────┐          │
│      │                   │          │
│      │   关系图 (jpg)     │          │ ← <img> 加载外部图片
│      │   点击可放大       │          │
│      │                   │          │
│      └───────────────────┘          │
│                                     │
│  📌 使用说明（步骤引导）              │
│  📊 来源：HG/T xxxxx-95 图 x.x.x   │
│  [🔍 放大查看]                       │
└─────────────────────────────────────┘
```

#### HTML 实现

```html
<!-- Tab 按钮 -->
<button class="tab-btn" id="btnTabChart" onclick="switchTab('chart')">📈 RELATION CHART · 关系图</button>

<!-- Tab 内容：关系图 -->
<div class="tab-content" id="tabChart">
    <div class="card">
        <div class="ctitle">
            <span class="ico">📈</span>
            <div class="ctitle-text">
                <div class="ctitle-main">C-RE-D₀/D RELATION CHART</div>
                <div class="ctitle-sub">限流孔板流量系数关系图 · HG/T 20570.15-95</div>
            </div>
        </div>

        <!-- 图片区域 -->
        <div style="text-align:center; padding:12px 0 20px;">
            <img id="chartImg" src="" alt="C-Re-d0/D 关系图"
                 style="max-width:100%; height:auto; border-radius:var(--r-md);
                        box-shadow:var(--shadow-md); cursor:zoom-in;"
                 onclick="zoomChart()">
            <div class="diagram-label" style="margin-top:14px;">
                限流孔板 C-Re-d₀/D 关系图 · 流量系数 C 与雷诺数 Re 及 d₀/D 的关系
            </div>
        </div>

        <!-- 使用说明 -->
        <div style="margin-top:18px; padding:14px 18px;
                    background:var(--brand-lt);
                    border:1px solid rgba(42,168,137,0.15);
                    border-radius:var(--r-md); font-size:.82rem;
                    color:var(--txt-secondary); line-height:2;">
            <div style="font-weight:700; color:var(--brand-dk); margin-bottom:8px;">📌 使用说明</div>
            <div>① 根据设计计算得到的 <strong>d₀/D 比值</strong>，在图中找到对应曲线</div>
            <div>② 根据雷诺数 <strong>Re</strong>，在曲线上查得对应的 <strong>C 值</strong></div>
            <div>③ 将查得的 C 值填入输入框，重新计算</div>
            <div>④ 计算后对比 C' 与 C，偏差 <strong>&lt; 5%</strong> 为校核合格 ✓</div>
        </div>

        <!-- 来源标注 + 放大按钮 -->
        <div style="margin-top:16px; display:flex; gap:10px; flex-wrap:wrap;">
            <span class="info-tag">关系图来源：HG/T 20570.15-95 图 5.0.4</span>
            <button class="btn-sm" onclick="zoomChart()" style="margin-left:auto;">🔍 放大查看</button>
        </div>
    </div>
</div>
```

#### JS — Tab 切换时懒加载图片（节省首屏加载）

```javascript
function switchTab(tab) {
    // ... tab 切换逻辑 ...

    // 懒加载：仅在切换到 chart tab 时才加载图片
    if (tab === 'chart') {
        const chartImg = document.getElementById('chartImg');
        if (!chartImg.src || chartImg.src === window.location.href) {
            chartImg.src = '关系图.jpg';  // 图片文件与 HTML 同目录
        }
    }
}
```

#### JS — 全屏放大功能（点击图片触发）

```javascript
function zoomChart() {
    const img = document.getElementById('chartImg');
    if (!img.src || img.src === window.location.href) {
        toast('⚠️ 请先切换到「关系图」标签页查看图表', true);
        return;
    }

    // 创建全屏遮罩层
    const overlay = document.createElement('div');
    overlay.id = 'chartOverlay';
    overlay.style.cssText =
        'position:fixed;inset:0;background:rgba(0,0,0,0.88);z-index:9999;' +
        'display:flex;align-items:center;justify-content:center;' +
        'cursor:zoom-out;animation:fadeIn .25s ease;';
    overlay.onclick = () => { document.body.removeChild(overlay); };

    // 克隆图片
    const imgClone = document.createElement('img');
    imgClone.src = img.src;
    imgClone.style.cssText =
        'max-width:95vw;max-height:95vh;object-fit:contain;' +
        'border-radius:8px;box-shadow:0 8px 40px rgba(0,0,0,0.5);';

    // 底部提示
    const caption = document.createElement('div');
    caption.textContent = '点击任意处关闭';
    caption.style.cssText =
        'position:absolute;bottom:20px;left:50%;transform:translateX(-50%);' +
        'color:#fff;font-family:var(--font-mono);font-size:.75rem;' +
        'letter-spacing:1px;opacity:.7;';

    overlay.appendChild(imgClone);
    overlay.appendChild(caption);
    document.body.appendChild(overlay);

    toast('🔍 放大查看 — 点击任意处关闭');
}

// 补充 fadeIn 动画定义（CSS 中）
// @keyframes fadeIn { from{opacity:0} to{opacity:1} }
```

### 为什么不用 SVG/Canvas 重绘？

| 方案 | 优点 | 缺点 |
|------|------|------|
| **外部图片 (推荐)** ✅ | 保真度高、实现简单、懒加载快 | 文件体积稍大 |
| SVG 矢量重绘 | 无限缩放、体积小 | 工程曲线难以精确还原、开发量大 |
| Canvas 绘制 | 可交互 | 同上 + 性能开销 |
| Base64 内嵌 | 单文件无依赖 | HTML 体积暴增（图片转 base64 约 ×4/3） |

**结论**：对于工程标准查图表，**外部图片 + 同目录部署是最务实的方案**。

### 输入框联动提示

在需要查图填值的输入框 label 上明确提示用户：

```html
<label>校核流量系数 C' (查限流孔板 C-Re-d0/D 关系图后填入)</label>
<input type="number" id="d_Cp" value="0.6" ...>
```

---

## 坑点 7：检查器自身的缺陷——三类复发（v2.4.0 新增，G5）

> **前提**：验证的价值全押在检查器上。检查器错了，**"全绿"反而是最危险的结论**（掩盖真缺陷）。
> 铁律：判 FAIL 先怀疑检查器（`repr()` / 读原始数据复核），改产物前先证伪检查器。

| # | 缺陷形态 | 症状 | 纠正 |
|---|---|---|---|
| ① | **`must_keep` 语义误用** | 把"**打算删掉的行**"写进不变量清单 → 合法修改被自己判成违规，或反向：该守的没守 | `must_keep` 只放**改后仍必须存在**的内容；"要删的"永远不进清单。写前闸门（plan_apply 阶段 0）标"改前就存在"，缺一即整批不写 |
| ② | **`''` → `null` 空值编码错误** | 对拍台报**假差异**：两侧"看着都是空"，实际一侧 `''`（空字符串，算术→`#VALUE!`）另一侧 `null`（空单元格，数值上下文当 0） | 空值编码在**两侧统一**后再比；`isBlank`/`toNum` 语义见 `runtime.js` 注释；拿不准先 `repr()` 打印看类型 |
| ③ | **断言失败返回描述串冒充通过** | 计数函数把错误信息当成功，**假 PASS** | 断言失败**必须返回 `false`**；禁止返回字符串。计数型断言还要剔除环境噪声并**显式列出被剔除项** |

**死路（试过并否决）**：靠"断言写得细一点"来兜这三类——**无效**，因为①③是"判据与对象错位"、②是"两侧口径不统一"，都不在断言语义层，必须在**检查器的结构**上修（清单语义 / 编码归一 / 返回值契约）。

---

## 坑点 8：验证的三类假信号（v2.4.0 新增，CHEF 4.5 承接复核轮实证）

> 三类都**不报错、看着正常**，只有换一种验证手段才暴露。

| 信号 | 实证 | 判据 / 处置 |
|---|---|---|
| **假白屏**（感知层） | headless 截图正文区全空白（30 s 预算 + 3600 px 视口），jsdom 探针却显示默认 Tab 已渲染 223 行、零未捕获异常 → 差点报出"默认 Tab 空白"的**假缺陷** | 截图**必须与 DOM 探针成对**使用（见 verification-toolkit D2）；截图空白 + 探针有内容 = **捕获 artifact**，不是缺陷 |
| **假覆盖率**（溯源文本） | P1/P2/P3/P4 四个交付件的 Footer 全停在「**P1 · 25 842 点位**」，而 P4 实为 90 728 点位——数值门全绿也看不见 | 凡断言**阶段/覆盖率/来源**的写死文本，都要在 D 门或专门内容判据里对账；`Footer 阶段名 == 文件名阶段`、`点位数 == 该阶段对拍合计` |
| **假绿**（缺门不报） | 只跑了 A/B/C 三层门，D 门未执行，报告按"A/B/C"表述、**未写 skipped** → 读者默认四门全过 | **未执行的门必须显式报 `skipped (缺什么)`**；四门逐个交代状态词，省略 = 误导 |

**通式**：**"没报错"和"验证过了"是两件事**。验证的结论只有四种状态（`passed` / `failed` / `skipped` / 假信号），凡说不清状态词的，就是没验证。



---

## 坑点 9：数据提取层的静默损坏——**你自己的提取代码改坏了数据**（v2.5.0 新增，2026-09-17）

> **与坑点 7/8 的区别**：那两个讲"检查器错"与"假信号"；本坑讲**喂给检查器的数据在提取环节就被悄悄改坏了**——上游文件完好、脚本不报错、退出码 0。

**症状**：下游出现**物理上不可能的曲线**（实测：液体密度线性拟合 R²=0.04），而提取脚本一路"正常"。

**实证（CHEF 化学品库扩容）**：为剔除小节号写了 `seg.replace("9.20", " ")`——**全局替换**，而 `"9.20"` 会出现在**数据值内部**：
`"69.209".replace("9.20", " ")` → `"6 . 9"`，一个数被拆成 `6` 和 `9` 两个；数字总数 +1 后，"取前半为温度、后半为数值"的切分又**吞掉最后一个值** → **整条曲线错位**。受影响范围 = 任何值里含节号子串的表。

**同族子缺陷**：**边界判据用形状而非结构**。用 `^\d+\.\d+$` 判"这是小节标题行"，而数据值 `0.487` 也长这样 → 表格被提前截断（实测 18 个温度点只剩 9 个）。

**纠正（四条，缺一仍会漏）**：
1. **禁跨越字段的整串替换**——要剔除的标记用**行首锚点**精确匹配，不用全局 `replace`
2. **优先行级解析**：源数据若"一行一数"，就按行取数——本路线完全绕开上面两坑
3. **加结构闸门**：温度列须等步递增／密度须单调降／蒸气压须单调升；不满足即**显式标质量等级**，不静默采信
4. **边界判据用结构判别式**：小节标题后跟的是**标题文字行**；数据行后跟的**仍是数字行**

**死路（试过并否决）**：靠"再跑一遍对比"发现——**发现不了**。错位后的曲线长得**很合理**，本次仅因乙酸密度表 R²=0.04 这种极端才露头；若错位均匀，会被当成正常数据一路用到交付。

---

## 坑点 10：扩充存量表——身份键去重 ＋ 拿"存量自身惯例"当合规尺（v2.5.0 新增，2026-09-17）

> 触发场景：往已有数据表里**追加新行**（扩表），尤其是新行由外部数据源拼装而来时。

**症状 A**：候选池里**同一实体多张记录**（同义名／固体与溶液／不同卡片），直接追加造成重复行。
**症状 B**：判断"新记录**留空**是否合规"无据可依，容易误判成"必须补齐全部字段才能入库"。

**纠正 A —— 去重仲裁者必须用物理不变量，不能用名字**：

| 判据 | 处置 |
|---|---|
| 身份键相同（如 CAS）且**物理量互相矛盾**（实测：分子量 108 vs 164） | 该记录的**身份键错配** → 整组剔除，人工核 |
| 身份键相同且物理量不矛盾（或另一侧物理量缺失） | 同一实体 → **合并留一条**，别名记入备注供复核 |

- **死路 ①（试过并否决）**：用"本方与另一数据源的**匹配名**是否一致"判冲突 —— 匹配名自身会因**物理量撞车挑错同分异构体**（2-戊酮 vs 3-甲基-2-丁酮，分子量同为 86.13），把同实体的两张同义记录误判成冲突，一次多剔 14 条
- **死路 ②**：用"另一张按身份键编排的索引表"当仲裁者 —— 那张表若**就是同一批记录的副本**，则同键多行、**无仲裁力**（实测该表 1306 行与源记录一一对应）

**纠正 B —— 拿"存量自身的填充惯例"当新记录的合规尺**：
**先测存量表每个字段的实际填充率**，以它为标准。实测某存量表 10 个系数列 **0% 空**（硬不变量），而 UFL **87% 空**、自燃温度 **89% 空**、MIE／Flame Speed／液体电导率 **100% 空**。
→ 结论：**新记录留空与存量同形**，"要不要改引擎支持 N/A"这个争论**自动消解**——**不需要动引擎**。
→ 通用式：新数据的合规标准应与存量表的既有数据质量**对齐**，而不是与理想完备性对齐。

---

## 泵系统公式对齐坑点（原 SKILL.md「常见陷阱与修复」陷阱 1-4 ＋ 检查清单，2026-09-16 迁入）

> 触发场景：多工况／多模块／复杂单元格引用的工程计算表转换（HG/T 20570.5-95 泵系统实战）。
### 常见陷阱与修复

#### 陷阱 1：跨工况混搭引用

**现象**：Excel 中 `F31 = F32 - F30`，但 F32 是设计工况，F30 中 F29 却用了正常工况。

**根因**：Excel 设计者可能在不同时间修改了不同部分，导致工况不一致。

**修复**：
- 不要假设"同一行的单元格就是同一工况"
- 逐个追踪每个单元格的引用源
- 在映射表中明确标注每个单元格的**实际工况**（不是所在行号）

#### 陷阱 2：单位标注与实际量纲不符

**现象**：变量名标注为 "(m)"，但实际公式中已经是 "(m 液柱)"，不需要再乘 `9.81*gamma`。

**案例**：
```javascript
// ❌ 错误：H1acc 标注为 (m)，但已经是 m 液柱，重复乘了 9.81*gamma
Hg = Ps_s*10/(9.81*gamma) - H1 - 9.81*gamma*H1acc - NPSHr;

// ✅ 正确：H1acc 直接减（已是 m 液柱）
Hg = Ps_s*10/(9.81*gamma) - H1 - H1acc - NPSHr;
```

**修复**：
- 不要轻信变量名后的单位标注
- 用量纲分析验证：`[m] = [kPa] / ([m/s²] * [kg/m³]) = [m]` ✅
- 对可疑公式，先写出量纲方程再编码

#### 陷阱 3：阈值/系数的业务含义不清

**现象**：控制阀 Cvc/CV 的阈值写成 `> 0.5`，但实际标准是 `> 0.3`（对应 >30%）。

**根因**：凭印象写了 0.5，没有对照标准原文。

**修复**：
- 所有阈值、系数必须**对照标准原文确认**
- 在 HTML 注释中标注标准出处：
  ```javascript
  // HG/T 20570.5-95 第 X.X 条：Cvc/CV 应 > 0.3
  const CV_THRESHOLD = 0.3;
  ```
- UI 提示文字同步更新：`(>30%)` 而非 `(>50%)`

#### 陷阱 4：UI 布局在宽屏下出现左侧空白

**现象**：泵数据用 `auto-fill` 导致 1366px 屏幕下左侧出现大片空白。

**修复**：
```css
/* ❌ 错误：auto-fill 在宽屏下会产生空白列 */
.pump-data .form-row { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }

/* ✅ 正确：明确 4 列，每列等宽 */
.pump-data .form-row { grid-template-columns: repeat(4, 1fr); }
```

### 经验总结检查清单

| # | 检查项 | 通过标准 |
|---|--------|----------|
| 1 | 已建立逐单元格映射表 | Excel 单元格 ↔ HTML 变量，标注工况 |
| 2 | 已用 openpyxl 双模式验证 | 公式提取 + 数值提取，误差 < 0.001 |
| 3 | 跨工况引用已标注 | 混合工况（如 P24 = F31/F29）明确说明 |
| 4 | 单位已用量纲分析验证 | 可疑公式写出 [M][L][T] 方程 |
| 5 | 阈值已对照标准原文 | 标注标准号、章节号 |
| 6 | UI 布局已测试 1366px+ 宽屏 | 无左侧空白，无元素溢出 |