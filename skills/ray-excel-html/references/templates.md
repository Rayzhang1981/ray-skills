# 模板库（按需加载——生成 HTML 时复制对应模板）

> 来源：已发布 v1.0.1 完整版恢复。生成单文件 HTML 计算工具时，按需复制以下模板。
>
## UI 可视化设计规范（基于 V2.Visual 实践）

### 设计理念

将**工程示意图（SVG矢量图标）**与**数据输入框**合并为统一面板，让用户一眼看到设备类型、输入数量、当量参数，无需在两处来回跳转。

**已验证参考**：`D:\RayClaw\PE Calculation\01-Pipelines\不可压缩流体压力降计算-Pipe Pressure Drop-V2.Visual.html`

### SVG 工业图标设计规范

#### viewBox 统一标准
```html
<svg class="valve-svg" viewBox="0 0 100 60" fill="none" xmlns="http://www.w3.org/2000/svg">
```

- 宽高比 **5:3**，适合横向排列的设备/管件示意
- 所有图标统一 viewBox，确保 Grid 布局中大小一致

#### 图标绘制原则
- **线条风格**：stroke-based，linecap/linejoin round，线条清晰
- **填充策略**：默认 `fill="none"`，通过 CSS `stroke` 和 `currentColor` 控制颜色
- **关键元素突出**：阀门本体用粗线（stroke-width: 2.5），管道用细线（stroke-width: 1.5）
- **中英文标注**：SVG 内不写文字，文字放在 DOM 中（便于 i18n 和 CSS 控制）

#### 10 种标准管件图标

| 管件 | SVG 关键特征 | 当量长度 |
|------|-------------|---------|
| 球阀 Ball Valve | 圆形阀体 + 两侧水平管 | 30d |
| 闸阀 Gate Valve | 三角楔形 + 升降杆 | 8d |
| 截止阀 Globe Valve | S 形流道 + 垂直阀杆 | 340d |
| 蝶阀 Butterfly Valve | 圆盘在管道内偏转 | 45d |
| 90°弯头 90° Elbow | L 形弯管 | 30d |
| 45°弯头 45° Elbow | 45° 斜弯管 | 16d |
| 180°弯头 180° Bend | U 形回转弯管 | 50d |
| 三通直通 Tee-Run | T 形，直通方向 | 20d |
| 三通支流 Tee-Branch | T 形，支流方向 | 60d |
| 变径 Reducer | 锥形渐缩/渐扩管 | 自定义 Le |

#### SVG 颜色与主题适配

```css
/* 亮色模式 - 图标颜色 */
.valve-svg { stroke: var(--brand-primary); opacity: 0.7; transition: all 0.3s ease; }

/* 暗色模式 - 霓虹发光效果 */
[data-theme="dark"] .valve-svg { stroke: var(--neon-cyan); opacity: 0.6; }
[data-theme="dark"] .valve-item.active .valve-svg {
    stroke: var(--neon-cyan); opacity: 1;
    filter: drop-shadow(0 0 6px rgba(0, 229, 255, 0.5));
}

/* 选中/激活状态 */
.valve-item.active .valve-svg { opacity: 1; stroke-width-adjust: 1.2; }
```

### 合并式可视化输入面板（Valve Grid Panel）

#### 设计原则

将「设备示意图」和「数量输入框」合并为一个 `.valve-item` 单元：
- 上方：SVG 图标 + 设备名称 + 当量长度标注
- 下方：数量输入框
- 激活时：图标高亮 + 输入框绿色边框

#### HTML 结构模板

```html
<div class="card">
    <h3 class="sec-title">管件当量长度 (个数)</h3>
    <div class="valve-grid">
        <!-- 每个管件一个 valve-item -->
        <div class="valve-item" id="valve_ball">
            <svg class="valve-svg" viewBox="0 0 100 60">
                <!-- 球阀 SVG 路径 -->
            </svg>
            <div class="valve-name">球阀 Ball Valve</div>
            <div class="valve-le">30d</div>
            <input type="number" class="valve-input" id="f_ball" value="0" min="0"
                   oninput="highlightFit(this, 'ball'); triggerRealtime()">
        </div>
        <!-- 更多管件... -->
    </div>
</div>
```

#### CSS 响应式 Grid 布局

```css
.valve-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);  /* 桌面端5列 */
    gap: 12px;
}

/* 平板端 */
@media (max-width: 900px) {
    .valve-grid { grid-template-columns: repeat(4, 1fr); }
}

/* 小平板/大手机 */
@media (max-width: 680px) {
    .valve-grid { grid-template-columns: repeat(3, 1fr); }
}

/* 手机 */
@media (max-width: 440px) {
    .valve-grid { grid-template-columns: repeat(2, 1fr); }
}
```

#### 输入框样式

```css
.valve-input {
    width: 100%;
    padding: 7px 4px;
    text-align: center;
    font-family: var(--font-mono);
    font-size: 0.85rem;
    background: rgba(0, 0, 0, 0.04);
    border: 1px solid var(--bd);
    border-radius: 6px;
    color: var(--txt-primary);
    transition: all 0.25s ease;
}

/* 有值时 - 绿色高亮 */
.valve-input.has-value {
    color: var(--ok);
    border-color: rgba(0, 230, 118, 0.3);
    background: rgba(0, 230, 118, 0.04);
}

[data-theme="dark"] .valve-input {
    background: rgba(0, 0, 0, 0.25);
}
[data-theme="dark"] .valve-input.has-value {
    color: var(--ok);
    border-color: rgba(0, 230, 118, 0.35);
    background: rgba(0, 230, 118, 0.06);
}
```

#### 当量长度标注

```css
.valve-le {
    font-family: var(--font-mono);
    font-size: 0.58rem;
    color: var(--txt-muted);
    margin-bottom: 8px;
}
```

#### 管件名称

```css
.valve-name {
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--txt-secondary);
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
```

### JS 交互逻辑

#### valveMap 映射表

```javascript
const valveMap = {
    'f_ball': 'ball',
    'f_gate': 'gate',
    'f_globe': 'globe',
    'f_butterfly': 'butterfly',
    'f_90elbow': '90elbow',
    'f_45elbow': '45elbow',
    'f_180bend': '180bend',
    'f_tee_run': 'tee_run',
    'f_tee_branch': 'tee_branch'
};
```

#### 高亮与状态更新

```javascript
function updateValveVisual() {
    for (const [inputId, valveType] of Object.entries(valveMap)) {
        const input = document.getElementById(inputId);
        if (!input) continue;
        const count = parseInt(input.value) || 0;
        const valveItem = document.getElementById('valve_' + valveType);
        if (valveItem) {
            input.classList.toggle('has-value', count > 0);
            if (count > 0) {
                valveItem.classList.add('active', 'valve-active');
            } else {
                valveItem.classList.remove('active', 'valve-active');
            }
        }
    }
}

function highlightFit(el, valveType) {
    updateValveVisual();
}
```

#### 关键注意事项
- **DOM ID 唯一性**：每个 `f_*` 输入框 ID 在整个 HTML 中只能出现一次（旧版曾出现 SVG 区域和表格中重复 ID 的问题）
- **初始化调用**：页面加载后调用一次 `updateValveVisual()` 以恢复默认状态
- **输入框必须绑定**：`oninput="highlightFit(this, 'xxx'); triggerRealtime()"`

### 其他工业设备图标扩展

当需要为其他过程工程场景（安全阀、换热器、泵、容器等）添加 SVG 图标时：
1. 遵循统一的 `viewBox="0 0 100 60"` 标准
2. 使用 stroke-based 绘制，保持线条风格一致
3. 添加 `.valve-item` / `.valve-grid` 同样的响应式布局
4. 确保暗色模式下的霓虹发光效果

---


---

## 管道压力降计算 HTML 设计规范（HG/T 20570.7-95）

### 设计参考文件
- 用户认可的设计：`D:\RayClaw\PE Calculation\01-Pipelines\不可压缩流体压力降计算-Pipe Pressure Drop-Incompressible-Ver2.1.html`
- 生成文件示例：`D:\RayClaw\PE Calculation\01-Pipelines\不可压缩流体压力降计算-Pipe Pressure Drop-Incompressible.html`
- Visual 版本：`D:\RayClaw\PE Calculation\01-Pipelines\不可压缩流体压力降计算-Pipe Pressure Drop-V2.Visual.html`

### INPUT PARAMETERS 必须包含的 5 个子项

| 序号 | 名称 | 内容 |
|------|------|------|
| ① | 基本参数 Basic Data | 流量输入方式切换（体积/质量）、密度、粘度、管内径 |
| ② | 管道总长度 Pipe Length | 直管段长度、管壁粗糙度（含参考tooltip）、管件当量长度（可视化面板） |
| ③ | 静压降参数 Static Pressure Drop | 进出口标高 Z₁、Z₂ |
| ④ | 速度压降 Velocity Pressure Drop | 进出口截面积、公式说明：ΔPv = ρ(u₂²−u₁²)/2 × 10⁻³ KPa |
| ⑤ | 设备压降 Equipment ΔP | 换热器、流量计、过滤器、其他设备 |

### 流量输入方式（必须实现）
```html
<!-- 模式切换按钮 -->
<div class="mode-toggle">
    <button class="mode-btn active" onclick="setMode('vol')">体积流量 qv (m³/h)</button>
    <button class="mode-btn" onclick="setMode('mass')">质量流量 qm (kg/h)</button>
</div>
<!-- 体积流量输入 -->
<div id="grpVol">
    <label>体积流量 qv (m³/h)</label>
    <input type="number" id="qv" oninput="syncFlow('vol')">
</div>
<!-- 质量流量输入 -->
<div id="grpMass" style="display:none">
    <label>质量流量 qm (kg/h)</label>
    <input type="number" id="qm" oninput="syncFlow('mass')">
</div>
```

- 切换时同步显示另一字段的值
- `syncFlow()` 函数根据密度自动换算

### 管壁粗糙度参考（必须实现）
- 使用 `.tip-wrap` 包裹粗糙度输入框
- Hover 显示常见管材粗糙度表格
- 点击表格中的数值自动填入输入框

```html
<div class="fg tip-wrap">
    <label>管壁粗糙度 ε (mm) <span class="tip-hint">⬡ 参考</span></label>
    <input type="number" id="eps" value="0.2">
    <div class="tip">
        <div class="tip-head">常见管材粗糙度参考值</div>
        <table>
            <tr><td>碳钢管（无缝）</td><td class="tv" onclick="pickEps(0.2)">0.2</td></tr>
            <!-- 更多管材... -->
        </table>
    </div>
</div>
```

### 管件当量长度（推荐使用可视化面板）

**推荐方案**：使用上方的「合并式可视化输入面板」替代传统表格。

| 管件 | 默认值 | 当量长度系数（×d） |
|------|--------|-------------------|
| 球阀 | 0 | 30d |
| 闸阀 | 5 | 8d |
| 截止阀 | 0 | 340d |
| 蝶阀 | 0 | 45d |
| 90°弯头 | 10 | 30d |
| 45°弯头 | 0 | 16d |
| 180°弯头 | 0 | 50d |
| 三通-直通 | 0 | 20d |
| 三通-支流 | 0 | 60d |
| 变径 | 0 | 需单独输入 Le |

### 摩擦系数计算流程
1. 判断流态：Re < 2000 → 层流（λ = 64/Re）
2. 湍流：Swamee-Jain 初值 → Colebrook 迭代（50次收敛）
3. 条件判据：`crit = 1/(ε/d × Re × √λ)`
   - crit < 0.05 → 完全湍流区，采用尼库拉则-卡门公式
   - crit ≥ 0.05 → 过渡/光滑区，采用 Colebrook 结果

### 压力降分解
- 摩擦压降 ΔPf = λ × (L/d) × (ρu²/2) × 10⁻³ kPa
- 静压降 ΔPs = ρg(Z₂-Z₁) × 10⁻³ kPa
- 速度压降 ΔPv = ρ(u₂²-u₁²)/2 × 10⁻³ kPa
- 设备压降 ΔPe = 换热器 + 流量计 + 过滤器 + 其他

---


---

## 实时计算模块（Realtime Calculation）

参考 `assets/html-template.html` 中的实现，为所有计算页面添加实时计算能力。

### 效果

- 修改任意输入参数 → **300ms 防抖后自动重新计算**
- 计算时按钮显示 `"REAL TIME CALCULATING 自动计算中..."` + 呼吸光效动画
- 手动点击按钮 → 停止实时模式，恢复正常按钮样式

### CSS 部分

```css
/* 按钮文字切换 */
.btn-calc .btn-text { display: inline; }
.btn-calc .btn-live { display: none; }
.btn-calc.live-mode .btn-text { display: none; }
.btn-calc.live-mode .btn-live { display: inline-flex; align-items: center; gap: 6px; }

/* 呼吸光效 */
.btn-calc.live-mode { animation: liveGlow 2s ease-in-out infinite; }
@keyframes liveGlow {
    0%, 100% { box-shadow: 0 4px 20px rgba(42, 168, 137, 0.2); }
    50% { box-shadow: 0 4px 30px rgba(42, 168, 137, 0.45), 0 0 50px rgba(42, 168, 137, 0.1); }
}

/* 暗色主题呼吸光效 */
[data-theme="dark"] .btn-calc.live-mode { animation-name: liveGlowDark; }
@keyframes liveGlowDark {
    0%, 100% { box-shadow: 0 4px 20px rgba(0, 229, 255, 0.15); }
    50% { box-shadow: 0 4px 30px rgba(0, 229, 255, 0.4), 0 0 50px rgba(0, 229, 255, 0.1); }
}

/* 闪烁绿点 */
.live-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 8px rgba(74, 222, 128, 0.6);
    animation: liveBlink .8s ease-in-out infinite;
}
@keyframes liveBlink { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: .4; transform: scale(.7); } }
```

### HTML 部分

```html
<button class="btn-calc" id="btnCalc" onclick="calc(true)">
    <span class="btn-text"><span>▶</span> EXECUTE CALCULATION · 执行计算</span>
    <span class="btn-live"><span class="live-dot"></span>REAL TIME CALCULATING 自动计算中...</span>
</button>
```

### JS 部分

```javascript
let realtimeTimer = null;
let isLive = false;

/* 实时计算触发器（防抖 300ms）*/
function triggerRealtime() {
    if (realtimeTimer) clearTimeout(realtimeTimer);
    realtimeTimer = setTimeout(() => {
        calc(false);  // false = 实时触发，不重置 live 状态
        if (!isLive) {
            isLive = true;
            const btn = document.getElementById('btnCalc');
            if (btn) btn.classList.add('live-mode');
        }
    }, 300);
}

/* calc 函数增加 manual 参数 */
function calc(manual = false){
    try {
        // manual=true 是手动点击，重置 live 状态
        if (manual) {
            if (realtimeTimer) { clearTimeout(realtimeTimer); realtimeTimer = null; }
            isLive = false;
            const btn = document.getElementById('btnCalc');
            if (btn) btn.classList.remove('live-mode');
        }
        // ... 计算逻辑 ...
    } catch(e) { /* ... */ }
}
```

### 输入框绑定规则

所有 `<input type="number">` 均需绑定 `oninput="triggerRealtime()"`：

| 类型 | 示例 | 绑定方式 |
|------|------|----------|
| 无 oninput | `<input id="mu">` | 添加 `oninput="triggerRealtime()"` |
| 有 oninput | `<input oninput="syncFlow('vol')">` | 追加 `; triggerRealtime()` → `oninput="syncFlow('vol'); triggerRealtime()"` |
| 管件输入 | `<input oninput="highlightFit(this)">` | 追加 `; triggerRealtime()` → `oninput="highlightFit(this); triggerRealtime()"` |

---


---

## Excel 转 HTML 通用 UI 规范（V1.1 经验总结）

> 适用场景：所有 Excel → 单文件 HTML 的转换任务。
> 目的：保持系列工具视觉风格统一，减少反复调整。

### 规范 1：字体统一用微软雅黑

CSS `:root` 中的 `--font-sans` 必须优先声明微软雅黑：

```css
:root {
    --font-sans: 'Microsoft YaHei', '微软雅黑', 'Noto Sans SC', 'PingFang SC', system-ui, sans-serif;
}
```

- ❌ 禁止：`SimSun`、`宋体` 作为正文或标题字体
- ✅ 正文、`label`、按钮文字均使用 `var(--font-sans)`
- 等宽字体用 `var(--font-mono)`（JetBrains Mono / Fira Code）

---

### 规范 2：主题切换必须用太阳/月亮图标

禁止使用文字按钮（"亮色"/"暗色"）。必须使用 **太阳☀️ + 月亮🌙 SVG 图标 + 标签文字** 的胶囊按钮。

#### CSS（直接复用，无需修改）

```css
.theme-toggle {
    position: fixed;
    top: 14px;
    right: 14px;
    z-index: 200;
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--bg-card);
    border: 1px solid var(--bd);
    border-radius: 100px;
    padding: 5px 14px 5px 8px;
    cursor: pointer;
    transition: all 0.3s;
    color: var(--txt-muted);
    font-family: var(--font-sans);
    font-size: 0.72rem;
    letter-spacing: 0.06em;
    box-shadow: var(--shadow);
}
.theme-toggle:hover {
    border-color: var(--brand);
    color: var(--brand);
    box-shadow: 0 0 12px var(--brand-dim), var(--shadow);
}
[data-theme="dark"] .theme-toggle {
    border-color: rgba(0,229,255,0.3);
    box-shadow: 0 0 12px rgba(0,229,255,0.08), var(--shadow);
}
[data-theme="dark"] .theme-toggle:hover {
    border-color: var(--brand);
    box-shadow: 0 0 14px rgba(0,229,255,0.15), var(--shadow);
}
.theme-toggle .sun-icon,
.theme-toggle .moon-icon {
    width: 16px; height: 16px;
    transition: transform 0.3s, opacity 0.3s;
    flex-shrink: 0;
}
.theme-toggle .sun-icon { display: block; }
.theme-toggle .moon-icon { display: none; }
[data-theme="dark"] .theme-toggle .sun-icon { display: none; }
[data-theme="dark"] .theme-toggle .moon-icon { display: block; }
.theme-toggle .tt-label { font-weight: 600; }
```

#### HTML（直接复用）

```html
<button class="theme-toggle" id="themeToggle" title="切换亮/暗主题" aria-label="切换主题">
  <svg class="sun-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
       stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="5"/>
    <line x1="12" y1="1"  x2="12" y2="3"/>
    <line x1="12" y1="21" x2="12" y2="23"/>
    <line x1="4.22"  y1="4.22"  x2="5.64"  y2="5.64"/>
    <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
    <line x1="1"  y1="12" x2="3"  y2="12"/>
    <line x1="21" y1="12" x2="23" y2="12"/>
    <line x1="4.22"  y1="19.78" x2="5.64"  y2="18.36"/>
    <line x1="18.36" y1="5.64"  x2="19.78" y2="4.22"/>
  </svg>
  <svg class="moon-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor"
       stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
  </svg>
  <span class="tt-label" id="ttLabel">DARK</span>
</button>
```

#### JS（直接复用）

```javascript
const themeToggle = document.getElementById('themeToggle');
const ttLabel      = document.getElementById('ttLabel');
if (themeToggle) {
    themeToggle.addEventListener('click', () => {
        const html  = document.documentElement;
        const theme = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', theme);
        if (ttLabel) ttLabel.textContent = theme === 'dark' ? 'LIGHT' : 'DARK';
    });
}
```

---

### 规范 3：标题格式统一（大气居中版式）

禁止使用 sticky 顶部窄栏标题。必须使用**居中大气版式**，参考 `储罐容积计算系统V1.1.html` 的标题风格。

#### 布局结构

```
[固定右上角]  .theme-toggle 按钮（见规范2）
[居中标题区] .page-header
  ├── .hd-badge     胶囊徽章（闪烁圆点 + 编号/标准）
  ├── h1             英文主标题 + 中文高亮
  ├── p.sub          副标题（计算方法说明）
  └── .brand-bar    渐变分隔线
```

#### CSS（直接复用）

```css
.page-header {
    text-align: center;
    padding: 36px 20px 28px;
    animation: fadeDown 0.6s ease both;
}
.hd-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--brand-dim);
    border: 1px solid rgba(42,168,137,0.2);
    border-radius: 100px;
    padding: 5px 18px;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 1.5px;
    color: var(--brand);
    text-transform: uppercase;
    margin-bottom: 18px;
    transition: all 0.3s;
}
.hd-badge::before {
    content: '';
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--brand);
    animation: blink 2.2s ease infinite;
}
[data-theme="dark"] .hd-badge {
    border-color: rgba(0,229,255,0.25);
    box-shadow: 0 0 12px rgba(0,229,255,0.08);
}
[data-theme="dark"] .hd-badge::before {
    background: var(--brand);
    box-shadow: 0 0 8px var(--brand);
}
.page-header h1 {
    font-size: clamp(1.2rem, 3vw, 1.9rem);
    font-weight: 700;
    letter-spacing: 2px;
    color: var(--txt-primary);
    margin-bottom: 10px;
}
.page-header h1 .accent-amb {
    color: var(--amber);
    font-weight: 500;
}
[data-theme="dark"] .page-header h1 .accent-amb { color: var(--brand); }
.page-header .sub {
    font-size: 0.82rem;
    color: var(--txt-sec);
    letter-spacing: 0.5px;
}
.brand-bar {
    width: 100px; height: 3px;
    margin: 16px auto 0;
    background: linear-gradient(90deg, var(--brand), var(--amber));
    border-radius: 2px;
    opacity: 0.7;
}
@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes blink {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.3; }
}
```

#### HTML 模板（按实际内容替换）

```html
<!-- 固定右上角主题切换按钮（规范2已定义） -->
<button class="theme-toggle" id="themeToggle" title="切换亮/暗主题">...</button>

<!-- 居中标题区 -->
<div class="page-header">
  <div class="hd-badge">
    [英文工具名]&nbsp;·&nbsp; VER X.X &nbsp;·&nbsp; [标准号]&nbsp;·&nbsp; [中文工具名]
  </div>
  <h1>[英文主标题] <span class="accent-amb">[中文副标题]</span></h1>
  <p class="sub">[计算方法一] · [计算方法二]&nbsp;|&nbsp; [标准依据]</p>
  <div class="brand-bar"></div>
</div>
```

---

### 规范 4：标题徽章必须含版本号

`.hd-badge` 内容格式固定为：

```
[英文工具名] · VER X.X · [标准号] · [中文工具名]
```

- 版本号格式：`VER X.X`（全大写，空格，小数点分隔）
- 各段用 `&nbsp;·&nbsp;` 分隔
- 示例：`PIPE DIAMETER CALC &nbsp;·&nbsp; VER 1.1 &nbsp;·&nbsp; HG/T 20570.6-95 &nbsp;·&nbsp; 管径计算`

#### 检查清单（每次生成 HTML 后自查）

| # | 检查项 | 通过标准 |
|---|--------|----------|
| 1 | `--font-sans` 首选项是微软雅黑 | 无宋体/SimSun 出现 |
| 2 | 主题按钮是太阳/月亮图标 | 无"亮色"/"暗色"文字按钮 |
| 3 | 标题是居中大气版式 | 无 sticky 窄栏 |
| 4 | `.hd-badge` 含 `VER X.X` | 版本号存在且格式正确 |
| 5 | 暗色模式切换后标签文字变化 | 亮色→显示`DARK`；暗色→显示`LIGHT` |

---


---

## 坑点 7：导出功能（Excel / PDF）及中文乱码问题

### Excel 导出 — SheetJS (xlsx.js)

#### CDN 引入

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
```

#### 导出函数模板

```javascript
function exportDesignXLSX() {
    try {
        if (typeof XLSX === 'undefined') {
            toast('⚠️ 正在加载 Excel 库，请稍候重试', true);
            return;
        }

        // 1. 收集数据
        const qv  = document.getElementById('d_qv').value;
        const rho = document.getElementById('d_rho').value;
        // ... 更多字段 ...

        // 2. 构建工作簿
        const wb = XLSX.utils.book_new();
        const data = [
            ['限流孔板设计计算 / Orifice Design Calculation'],
            ['HG/T 20570.15-95', '生成日期：' + new Date().toLocaleDateString('zh-CN')],
            [],
            ['参数名', '数值', '单位', '备注'],
            ['体积流量 qv', parseFloat(qv), 'm³/h', ''],
            // ... 更多行 ...
        ];

        // 3. 创建工作表并设置列宽
        const ws = XLSX.utils.aoa_to_sheet(data);
        ws['!cols'] = [{wch:22}, {wch:14}, {wch:12}, {wch:30}];

        // 4. 导出下载
        XLSX.utils.book_append_sheet(wb, ws, '设计计算');
        XLSX.writeFile(wb, '限流孔板设计计算_' + new Date().toISOString().slice(0,10) + '.xlsx');

        toast('✅ Excel 已导出');
    } catch(e) {
        toast('⚠️ Excel 导出失败: ' + e.message, true);
    }
}
```

#### 中文处理

SheetJS (xlsx.js)**原生支持 Unicode/中文**，无需特殊编码处理。直接传入中文字符串即可正确写入 `.xlsx` 文件。

**注意**：`.xlsx` 格式基于 XML（内部 UTF-8），不存在 GBK 乱码问题。只有旧版 `.xls` (BIFF格式) 才可能遇到编码问题。

### PDF 导出 — window.print() 方案（推荐）

#### 为什么不用 jsPDF？

| 方案 | 中文支持 | 表格支持 | 样式还原 | 复杂度 |
|------|----------|----------|----------|--------|
| **window.print()** ✅ | 完美（浏览器原生） | 完整 CSS 表格 | 100% 还原 | 低 |
| jsPDF + autoTable | 需额外字体文件 | 基础表格 | 有限 | 高 |
| html2canvas + jsPDF | 完美但模糊 | 截图方式 | 像素级但大文件 | 中 |

**结论**：对于含大量中文的工程计算报告，**window.print() 是最佳方案**——利用浏览器原生渲染能力，中文完美支持，样式完全保留。

#### PDF 导出函数模板

```javascript
function exportDesignPDF() {
    try {
        // 1. 收集数据（同 Excel）
        const qv  = document.getElementById('d_qv').value;
        // ...

        // 2. 构建 HTML 内容（用于打印）
        const today = new Date().toLocaleDateString('zh-CN');
        const htmlContent = `\uFEFF<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>限流孔板设计计算报告</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: 'Microsoft YaHei', '微软雅黑', SimSun, Arial, sans-serif;
    font-size: 12pt; color: #1a1a1a;
    padding: 30px 40px; background: #fff;
  }
  /* 报告标题区 */
  .header {
    text-align: center; margin-bottom: 30px;
    border-bottom: 2px solid #2aa889; padding-bottom: 16px;
  }
  .header h1 { font-size: 18pt; color: #2aa889; margin-bottom: 6px; }
  .header p { font-size: 10pt; color: #666; }

  /* 数据表格 */
  table { width: 100%; border-collapse: collapse; margin: 16px 0; }
  th {
    background: #2aa889; color: #fff; padding: 8px 12px;
    font-size: 10pt; text-align: left;
  }
  td {
    padding: 7px 12px; border: 1px solid #ddd; font-size: 10pt;
  }
  tr:nth-child(even) td { background: #f8f9fa; }

  /* 页脚信息 */
  .footer {
    margin-top: 24px; padding-top: 12px;
    border-top: 1px solid #ddd; font-size: 9pt; color: #999;
  }

  /* 打印优化 */
  @media print {
    body { padding: 20px; }
    .no-print { display: none !important; }
    page { margin: 15mm; }
  }
</style>
</head>
<body>
  <div class="header">
    <h1>限流孔板设计计算报告</h1>
    <p>Orifice Plate Design Calculation Report · HG/T 20570.15-95</p>
    <p style="font-size:9pt;color:#999;margin-top:4px;">生成日期：${today}</p>
  </div>

  <table>
    <thead>
      <tr><th>参数名</th><th>数值</th><th>单位</th><th>备注</th></tr>
    </thead>
    <tbody>
      <tr><td>体积流量 qv</td><td>${parseFloat(qv)}</td><td>m³/h</td><td></td></tr>
      <!-- 更多行... -->
    </tbody>
  </table>

  <div class="footer">
    <p>本报告由限流孔板计算工具自动生成 · 依据 HG/T 20570.15-95</p>
  </div>
</body>
</html>`;

        // 3. 打开新窗口并写入 HTML
        const printWindow = window.open('', '_blank');
        printWindow.document.write(htmlContent);
        printWindow.document.close();

        // 4. 触发打印对话框
        setTimeout(() => { printWindow.print(); }, 500);

        toast('📄 PDF 导出：请在打印对话框选择"另存为 PDF"');
    } catch(e) {
        toast('⚠️ PDF 导出失败', true);
    }
}
```

### 🔑 中文乱码问题的完整解决方案

#### 场景 1：PDF 导出中文乱码 → ✅ `\uFEFF` BOM

**问题**：通过 `window.open()` 写入 HTML 字符串时，部分浏览器/打印场景下中文显示为乱码（□□ 或 ???）

**解决**：在 HTML 内容字符串开头添加 **UTF-8 BOM (`\uFEFF`)**

```javascript
// ✅ 正确：BOM 让浏览器识别为 UTF-8 编码
const htmlContent = `\uFEFF<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
...
```

**原理**：`\uFEFF` 是 UTF-8 BOM（Byte Order Mark），写在文件/流的最开头，告诉解析器"这是 UTF-8 编码"。没有 BOM 时，某些 Windows 浏览器的打印引擎可能按系统默认编码（GBK/GB2312）解析，导致中文乱码。

#### 场景 2：Excel 导出中文乱码 → ✅ 使用 .xlsx 格式

| 格式 | 编码 | 中文支持 |
|------|------|----------|
| **`.xlsx`** (Office Open XML) ✅ | 内部 UTF-8 XML | 完美支持 |
| `.xls` (BIFF5/8) | 二进制格式 | 可能乱码 |
| CSV | 取决于编辑器编码 | 极易乱码 |

**解决**：始终使用 `XLSX.writeFile()` 生成 `.xlsx` 格式（默认行为），不要指定 `.xls` 或 `.csv`。

#### 场景 3：HTML 文件本身打开乱码 → ✅ `<meta charset="UTF-8">`

```html
<!-- 主 HTML 文件头部必须包含 -->
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">   <!-- 必须！ -->
    ...
```

#### 中文编码速查表

| 场景 | 解决方案 | 代码位置 |
|------|----------|----------|
| PDF 导出 window.print() | 内容前加 `\uFEFF` BOM | JS 字符串模板开头 |
| Excel 导出 SheetJS | 使用 `.xlsx` 格式（默认） | `XLSX.writeFile(wb, 'name.xlsx')` |
| HTML 主文件 | `<meta charset="UTF-8">` | `<head>` 第一行 |
| 外部 CSS/JS 文件 | UTF-8 with BOM 保存 | 文件保存时选择编码 |
| @font-face 中文字体 | Google Fonts Noto Sans SC | `<link>` 引入 |

### UI 导出按钮布局

```html
<div class="exl">EXPORT · 导出</div>
<div style="display:flex; gap:8px; flex-wrap:wrap;">
    <button class="btn-sm xl" onclick="exportDesignXLSX()">📊 Excel</button>
    <button class="btn-sm" onclick="exportDesignPDF()">📄 PDF</button>
</div>
```

---


---
