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
