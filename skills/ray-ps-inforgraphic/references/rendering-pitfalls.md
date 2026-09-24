# 渲染防坑指南（按需加载——生成/导出遇到问题时读）

## html2canvas 集成代码模板（v2.2.0 自 SKILL.md 移入）

四件套集成（完整代码，生成 HTML 时照抄）：

**1. 引入库（head 区域）：**
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
```

**2. 下载按钮（body 区域，固定定位）：**
```html
<button id="downloadBtn" style="position:fixed;top:20px;right:20px;z-index:9999;
  background:linear-gradient(135deg,#C84B4B,#E8913A);
  color:#fff;border:none;padding:14px 28px;
  font:700 18px/1 var(--sans);border-radius:8px;cursor:pointer;
  box-shadow:0 4px 12px rgba(200,75,75,0.4);transition:all 0.3s;">
  下载 PNG 图片
</button>
```

**3. 截图脚本（script 标签）——关键参数：`scale:3`（高DPI手机必须≥3x）、`toBlob()`（优于 toDataURL，内存友好）、`useCORS:true`、`backgroundColor:'#FFFFFF'`：**
```javascript
document.getElementById('downloadBtn').onclick = function() {
  const btn = this;
  btn.disabled = true;
  btn.innerHTML = '正在生成高清图片(3x)...';

  html2canvas(document.querySelector('.page'), {
    scale: 3,                    // 3倍分辨率，适配高DPI手机屏幕
    backgroundColor: '#FFFFFF',   // 白色背景
    useCORS: true,               // 允许跨域图片
    logging: false,              // 关闭控制台日志
    allowTaint: false,           // 不允许污染canvas
    taintTest: true              // 测试canvas是否会被污染
  }).then(canvas => {
    canvas.toBlob(function(blob) {
      if (!blob) {
        alert('图片生成失败，请重试！');
        btn.disabled = false;
        btn.innerHTML = '下载 PNG 图片';
        return;
      }
      let link = document.createElement('a');
      link.download = '{关键词}_信息图.png';
      link.href = URL.createObjectURL(blob);
      link.click();
      setTimeout(() => URL.revokeObjectURL(link.href), 100);
      btn.disabled = false;
      btn.innerHTML = '✅ 下载完成 (3x高清)';
      setTimeout(() => {
        btn.innerHTML = '下载 PNG 图片';
      }, 3000);
    }, 'image/png');
  }).catch(err => {
    console.error('截图失败:', err);
    alert('截图失败，请重试！\n错误: ' + err.message);
    btn.disabled = false;
    btn.innerHTML = '下载 PNG 图片';
  });
};
```

**4. viewport meta（head 区域，charset 之后）：**
```html
<meta name="viewport" content="width=1080, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

---

## 文字排版防坑指南

> 背景：中文在 flex/grid 窄空间内逐字竖排（基于"预防中暑"信息图复盘）

### 核心问题：中文在 flex/grid 窄空间内逐字竖排

**根因分析：**
中文没有空格分词，浏览器在窄容器中无法找到断行点，只能逐字折行 → 4个字变成4行竖条。

**症状识别：**
- `<strong>技术措施</strong>` 渲染成"技/术/措/施"竖条
- 彩色标签"先兆中暑"变成窄竖条
- grid `1fr 1fr 1fr` 列内中文全部竖排

**标准修复方案：**

| 场景 | ❌ 错误写法 | ✅ 正确写法 |
|------|------------|------------|
| 图标列表 | `li { display:flex }` + 文字自然流 | `li { display:block; position:relative; padding-left:48px }` + `.ico { position:absolute; left:0 }` |
| 强调文字 | `<strong>技术措施：</strong>` | `<strong style="display:inline-block;white-space:nowrap">技术措施：</strong>` |
| 彩色标签 | `.label { width:80px }` 自然折行 | `.label { width:80px; white-space:nowrap }` 或手动 `<br>` 断行（如"先兆<br>中暑"） |
| grid 内标签 | `grid: 1fr 1fr 1fr` | `display:flex; flex-wrap:wrap` + `min-width:100px; white-space:nowrap` |
| 通用防护 | 无 | 所有中文标签/徽章/强调文字加 `white-space:nowrap` |

**图标列表最佳实践（替换原 flex 方案）：**
```css
.icon-list li {
  display: block;
  position: relative;
  padding: 9px 0 9px 48px;   /* 左侧留出图标空间 */
  border-bottom: 1px solid #F0F0F0;
  font-size: 22px;
  line-height: 1.5;
}
.icon-list .ico {
  position: absolute;
  left: 0;
  top: 9px;
  font-size: 28px;
  width: 40px;
  text-align: center;
}
.icon-list strong {
  display: inline-block;
  white-space: nowrap;
}
```

**手动断行规则（4字以上标签）：**
- 2字标签：不处理（如"一级"）
- 4字标签：两字一行（如"先兆<br>中暑"、"轻症<br>中暑"）
- 6字标签：三字一行（如"高温强辐射"→"高温强<br>辐射"）
- 原则：每行2-3个汉字，保持标签宽度与高度均衡

### ⚠️ 辨析：`nowrap` + `inline-block` ≠ 竖排（两类缺陷别混）

2026-09-12 用负控实测确认：**`white-space:nowrap` + `display:inline-block` 不会造成竖排** —— inline-block 的盒子会**撑宽到内容宽度**（4 个 36px 汉字 → 盒宽 144px、高 43px，规规矩矩一行）。两类缺陷的病因和治法完全不同：

| 写法 | 真实后果 | 属哪类缺陷 |
|------|---------|-----------|
| 容器**太窄**（宽度不足） | 中文逐字折行、竖排成条 | **排版缺陷** → 治「给足宽度 / block + max-width」 |
| `nowrap`+`inline-block` 用于**长文本** | 盒子撑得很宽 → 溢出父容器 → html2canvas 裁剪丢字 | **导出缺陷** → 治「长文本改 block」 |

- 要防**竖排** → 治容器太窄：图标列表用 `display:block; position:relative` + 图标绝对定位。
- 要防**导出丢字** → 治长文本上的 nowrap：长文本一律 `display:block` + 合理 `max-width`。
- **短标签（≤4 字）加 `nowrap` 是安全且推荐的** —— 防止标签被拆行；负控实测渲染为正常一行。
- 结论：「加 nowrap」与「去 nowrap」不矛盾，而是**按文本长度分流** —— 短标签留，长文本去。

---

## 分辨率优化指南

**scale 参数选择：**

| scale值 | 输出宽度 | 适用场景 | 文件大小 |
|---------|-----------|----------|----------|
| 1x | 1080px | 仅电脑端查看 | ~1-2MB |
| 2x | 2160px | 普通手机屏幕 | ~3-5MB |
| **3x（推荐）** | **3240px** | **高DPI手机（iPhone/Android旗舰）** | **~5-8MB** |
| 4x | 4320px | 印刷/超高清需求 | ~10-15MB |

**关键经验：**
1. **手机端必须用 ≥3x**：现代智能手机的DPI高达3x-4x，2x在手机上会显得模糊
2. **toBlob() 优于 toDataURL()**：
   - `toDataURL()` 返回 base64 字符串，内存占用大
   - `toBlob()` 返回 Blob 对象，更适合大文件下载
   - `toBlob()` 生成的 PNG 质量更高，文件更小
3. **viewport meta 标签必须添加**：
   - 防止手机浏览器自动缩放页面
   - 确保HTML在手机端以正确宽度显示
   - `width=1080` 锁定页面宽度，避免响应式缩放
4. **按钮状态管理**：
   - 禁用按钮防止重复点击
   - 显示进度提示（"正在生成..."）
   - 完成后显示确认信息（"下载完成"）
   - 使用 `URL.createObjectURL()` + `URL.revokeObjectURL()` 管理内存

**常见问题排查：**

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 截图空白 | 图片未加载完成 | 确保图片加载完成后再截图，或使用 `window.onload` |
| 跨域图片丢失 | CORS 限制 | 设置 `useCORS: true`，确保图片服务器允许跨域 |
| 文字模糊 | scale 太低 | 提高到 3x 或 4x |
| 文件太大 | scale 太高 | 降低到 2x，或压缩后再分发 |
| 手机端显示异常 | 缺少 viewport meta | 添加 `<meta name="viewport" content="width=1080,...">` |
| **HTML 可见但导出后文字消失** | CSS 写法触发 html2canvas 渲染 bug | 见下方「html2canvas CSS 渲染防坑指南」 |
| **点下载失败 / 导出图下半截空白** | 导出尺寸超 Chrome 画布单边上限 16384px | 乘数改为按上限反算，见下方「画布单边上限 16384px」节 |

---

## 画布单边上限 16384px（长图必读 · 2026-09-12 实测）

**症状**：点「下载 PNG」按钮无反应、弹「截图失败」，或导出的图下半截是空白。

**根因**：Chrome 的 canvas 单边上限是 **16384px**。竖版长图动辄 5000～7000px 高，固定 `scale:3` 会算出 15000～21000px —— **超过上限的导出必然失败，与代码写得对不对无关**。

| 页面尺寸（1080 宽竖版） | ×3 导出高度 | 结果 |
|------------------------|-----------|------|
| 1080 × 2000（常规海报） | 6,000px | ✅ 正常 |
| 1080 × 5,944（本次长图） | 17,832px | ❌ 超限 → 只能出 2x（11,890px） |
| 1080 × 6,426（压缩前） | 19,278px | ❌ 超限 |

**正解：乘数按上限反算，不要写死 3**

```javascript
var CANVAS_MAX = 16000;   /* Chrome 上限 16384px，留 384px 余量 */
function pickScale() {
  var w = page.scrollWidth, h = page.scrollHeight;
  return Math.max(1, Math.min(3, Math.floor(CANVAS_MAX / Math.max(w, h))));
}
```

- 取 16000 而非 16384：留余量，避免边界值因小数舍入踩线。
- `Math.min(3, …)` 让短图仍拿满 3x；`Math.max(1, …)` 让极长图至少出 1x，绝不返回 0。
- **按钮标签要显示实际乘数**（如「下载 PNG 图片 (2x)」），别硬写「3x 高清」—— 否则用户以为拿到了 3x。
- 判据：页面单边 ≤ 5,333px 时 3x 可用；再长就必须接受 2x（2,160px 宽对手机已足够清晰）。
- **本条优先于「分辨率优化指南」的「文字模糊 → 提高到 3x 或 4x」**：长图先看上限、再谈乘数；上限不允许时只能压缩版面高度，不能硬提乘数。

**交付前必算的自检判据**：`max(pageWidth, pageHeight) × scale ≤ 16384`。不成立 ⇒ 下载按钮一定会失败，必须先降乘数或压缩版面。

---

## html2canvas CSS 渲染防坑指南

> 背景：浏览器中正常显示的文本，html2canvas 导出 PNG 后完全消失（基于"检维修六把关"修复实战）

**核心问题：** 浏览器中正常显示的文本，html2canvas 导出 PNG 后完全消失。

**根因：** html2canvas 1.4.1 不是真正的浏览器渲染引擎，而是用 Canvas API 模拟重绘，以下 CSS 写法会导致元素丢失：

### 三大高危写法（禁止在 info 图 HTML 中使用）

| 高危写法 | 症状 | 原因 | 修复 |
|---------|------|------|------|
| `white-space: nowrap` + `display: inline-block` | 长文本溢出容器 → html2canvas 裁剪/丢失 | nowrap 阻止换行，inline-block 宽度计算不准，html2canvas 算出的渲染区域可能为 0 | 去掉 `white-space: nowrap`，改为 `display: block` + `max-width` 限制宽度 |
| CSS 变量用于 border 等短属性 | `border-left: 5px solid var(--orange)` → 边框消失或元素丢失 | html2canvas 对 `var()` 在短属性（border/margin/padding）上的解析不稳定 | 所有颜色值硬编码为十六进制（如 `#E8913A`），不使用 CSS 变量 |
| `background: linear-gradient(...)` | 渐变背景渲染异常或丢失 | html2canvas 的 Canvas gradient 对复杂渐变支持有限 | 改用纯色背景（如 `#FFF8E7`）；如果确实需要渐变，测试后再用 |

### 安全写法对照表

| 场景 | ❌ 危险写法 | ✅ 安全写法 |
|------|------------|------------|
| 韵文/口诀区域 | `.rhyme { display:inline-block; } .rhyme p { white-space:nowrap; }` | `.rhyme { display:block; max-width:780px; } .rhyme p { /* 不设 nowrap */ }` |
| 彩色边框 | `border-left: 5px solid var(--orange)` | `border-left: 5px solid #E8913A` |
| 装饰背景 | `background: linear-gradient(135deg, #FFF8E7, #FFF3D6)` | `background: #FFF8E7`（纯色） |
| Hero 区文字容器 | `display:inline-block` 包裹 `white-space:nowrap` | `display:block` + 合理 `max-width`，让文字自然折行 |

### 渲染前自检清单（生成 HTML 后必查）

- [ ] 所有 `white-space: nowrap` 的长文本区域 —— 改成 block + max-width
- [ ] 所有 `var(--xxx)` 在非颜色属性上 —— 硬编码为十六进制
- [ ] 所有 `linear-gradient / radial-gradient` 背景 —— 优先用纯色，渐变需实测验证
- [ ] 所有 `display: inline-block` 嵌套 nowrap 的组合 —— 改为 block 布局
- [ ] 韵文/金句/口诀区 —— 最容易出现这三类问题的区域，重点检查

### 核心原则

> **"浏览器能看 ≠ html2canvas 能导"**
> 生成 HTML 后，务必点"下载 PNG 图片"按钮实测导出效果。
> 以上三条高危写法在浏览器中 100% 正常，但在 html2canvas 中 90% 丢失。
