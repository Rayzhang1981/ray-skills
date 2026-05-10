# 配色方案详解

## 方案概览

| 方案 | 适用场景 | 关键词 |
|------|----------|--------|
| 暖灰中性 | 默认/通用 | 琥珀金、稳重，专业 |
| **科技绿松石** | **管道/化工计算** | **绿松石+琥珀、双主题、科技感** |
| 科技深色 | 数据可视化 | 霓虹、深邃、粒子背景 |
| 简洁明快 | 轻量工具 | 浅色、干净、易读 |

---

## 方案三：科技绿松石（管道压力降计算推荐）

**特点**：绿松石+琥珀配色，清新专业，适合化工管道计算场景
**参考文件**：`D:\RayClaw\PE Calculation\01-Pipelines\不可压缩流体压力降计算-Pipe Pressure Drop-Incompressible.html`

### CSS Variables

```css
:root,
[data-theme="light"] {
    --brand-primary: #2aa889;
    --brand-primary-dk: #197c67;
    --brand-primary-lt: #c8f0e6;
    --brand-primary-bg: rgba(42, 168, 137, 0.08);
    --brand-accent: #e7a642;
    --brand-accent-dk: #b87f1e;
    --brand-accent-lt: #f5e8cc;
    --brand-accent-bg: rgba(231, 166, 66, 0.08);
    --bg-page: #f4faf7;
    --bg-card: rgba(255, 255, 255, 0.88);
    --bg-card2: rgba(255, 255, 255, 0.72);
    --bg-card-solid: #ffffff;
    --bg-input: #f8fcfa;
    --txt-primary: #1a3c36;
    --txt-secondary: #4f6f69;
    --txt-muted: #8aa09b;
    --bd: rgba(42, 168, 137, 0.18);
    --bd-focus: #2aa889;
    --bd-error: #c9403e;
    --ok: #2aa889;
    --warn: #c98f38;
    --err: #c9403e;
    --neon-cyan: #00E5FF;
    --neon-purple: #7B61FF;
    --ok-glow: rgba(42, 168, 137, 0.25);
    --warn-glow: rgba(201, 147, 56, 0.25);
    --err-glow: rgba(201, 64, 62, 0.25);
    --glass-blur: blur(14px);
    --shadow-sm: 0 1px 4px rgba(31, 88, 74, 0.06);
    --shadow-md: 0 4px 16px rgba(31, 88, 74, 0.08);
    --shadow-lg: 0 8px 32px rgba(31, 88, 74, 0.10);
    --font-body: 'Noto Sans SC', -apple-system, sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
    --font-tech: 'Orbitron', monospace;
    --r-sm: 6px;
    --r-md: 10px;
    --r-lg: 16px;
    --r-xl: 20px;
    --page-bg: linear-gradient(180deg, #f7fbf8 0%, #eef7f2 55%, #f7fbf8 100%);
}

[data-theme="dark"] {
    --bg-page: #040d1a;
    --page-bg: linear-gradient(180deg, #040d1a 0%, #081428 50%, #0a1628 100%);
    --bg-card: rgba(10, 20, 42, 0.88);
    --bg-card2: rgba(8, 18, 38, 0.72);
    --bg-card-solid: #081428;
    --bg-input: rgba(4, 10, 24, 0.85);
    --txt-primary: #dde8f5;
    --txt-secondary: #7b9ab5;
    --txt-muted: #3d5a72;
    --bd: rgba(0, 229, 255, 0.13);
    --bd-focus: var(--neon-cyan);
    --ok: #00e676;
    --warn: #ffab00;
    --err: #ff1744;
    --brand-primary: #00E5FF;
    --brand-primary-dk: #0097a7;
    --brand-primary-lt: rgba(0, 229, 255, 0.28);
    --brand-primary-bg: rgba(0, 229, 255, 0.07);
    --brand-accent: #7c4dff;
    --brand-accent-dk: #651fff;
    --brand-accent-lt: rgba(124, 77, 255, 0.28);
    --brand-accent-bg: rgba(124, 77, 255, 0.07);
    --ok-glow: rgba(0, 230, 118, 0.25);
    --warn-glow: rgba(255, 171, 0, 0.25);
    --err-glow: rgba(255, 23, 68, 0.25);
    --shadow-sm: 0 1px 4px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
    --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
}
```

### 粒子背景（暗色模式）

```javascript
!function(){
    const cv=document.getElementById('cvs'),ctx=cv.getContext('2d');
    let W,H,pts=[];
    function resize(){W=cv.width=innerWidth;H=cv.height=innerHeight;}
    resize(); window.addEventListener('resize',resize);
    function P(){
        this.x=Math.random()*W; this.y=Math.random()*H;
        this.vx=(Math.random()-.5)*.28; this.vy=(Math.random()-.5)*.28;
        this.r=Math.random()*1.4+.4; this.a=Math.random()*.35+.08;
    }
    const n=Math.min(70,Math.floor(innerWidth*innerHeight/22000));
    for(let i=0;i<n;i++) pts.push(new P());
    function draw(){
        ctx.clearRect(0,0,W,H);
        for(let i=0;i<pts.length;i++){
            let p=pts[i];
            p.x+=p.vx; p.y+=p.vy;
            if(p.x<0)p.x=W; if(p.x>W)p.x=0;
            if(p.y<0)p.y=H; if(p.y>H)p.y=0;
            ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
            ctx.fillStyle=`rgba(0,229,255,${p.a})`; ctx.fill();
            for(let j=i+1;j<pts.length;j++){
                let q=pts[j],dx=p.x-q.x,dy=p.y-q.y,d=Math.sqrt(dx*dx+dy*dy);
                if(d<140){
                    ctx.beginPath(); ctx.moveTo(p.x,p.y); ctx.lineTo(q.x,q.y);
                    ctx.strokeStyle=`rgba(0,229,255,${.055*(1-d/140)})`; ctx.lineWidth=.5; ctx.stroke();
                }
            }
        }
        requestAnimationFrame(draw);
    }
    draw();
}();
```

---

## 方案一：暖灰中性（推荐默认）

**特点**：温暖、稳重、专业，适合工程计算场景

### CSS Variables

```css
:root,
[data-theme="light"] {
    /* 品牌色 · 暖红棕系 */
    --brand-primary: #8B4239;
    --brand-primary-dk: #6B3029;
    --brand-primary-lt: #E8D0CA;
    --brand-primary-bg: rgba(139, 66, 57, 0.06);

    /* 强调色 · 琥珀金系 */
    --brand-accent: #C7742A;
    --brand-accent-dk: #9A5622;
    --brand-accent-lt: #F5DFC7;
    --brand-accent-bg: rgba(199, 116, 42, 0.06);

    /* 辅助色 · 暖金 */
    --brand-gold: #D4983C;
    --brand-gold-lt: #F0E1CB;
    --brand-gold-bg: rgba(212, 152, 60, 0.06);

    /* 页面 & 卡片 */
    --bg-page: #FAF7F2;
    --bg-card: rgba(255, 255, 255, 0.82);
    --bg-card-solid: #FFFFFF;
    --bg-input: #FCFAF7;
    --bg-stripe: rgba(200, 188, 175, 0.18);

    /* 文字 */
    --txt-primary: #3E3230;
    --txt-secondary: #5C4F4B;
    --txt-muted: #8A7D78;
    --txt-placeholder: #B0A59F;

    /* 边框 */
    --bd: rgba(180, 165, 150, 0.28);
    --bd-focus: var(--brand-accent);
    --bd-error: #B5493A;

    /* 语义色 */
    --ok: #3B6E47;
    --warn: #C7742A;
    --err: #B5493A;

    /* 段位色 */
    --seg1-bg: #F7EFE6;
    --seg1-c: #9A5622;
    --seg1-bd: #E0CEB5;
    --seg2-bg: #F5F1EB;
    --seg2-c: #C7742A;
    --seg2-bd: #DDD0BE;
    --seg3-bg: #F3E9E6;
    --seg3-c: #8B4239;
    --seg3-bd: #E0CAC3;

    /* 玻璃拟态强度 */
    --glass-blur: blur(14px);
    --glass-border: rgba(255, 255, 255, 0.12);
    --glass-bg: rgba(255, 255, 255, 0.78);

    /* 页面背景 */
    --page-bg: linear-gradient(180deg, #F5EDE4 0%, #FAF7F2 35%, #F0EBE6 100%);

    /* 阴影 */
    --shadow-sm: 0 1px 4px rgba(62, 50, 48, 0.04), 0 0 0 1px rgba(180, 165, 150, 0.18);
    --shadow-md: 0 4px 16px rgba(62, 50, 48, 0.06), 0 1px 4px rgba(62, 50, 48, 0.03);
    --shadow-lg: 0 8px 32px rgba(62, 50, 48, 0.08), 0 2px 8px rgba(62, 50, 48, 0.04);

    /* 字体 */
    --font-body: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-mono: 'JetBrains Mono', 'Consolas', monospace;
    --font-tech: 'Orbitron', 'JetBrains Mono', monospace;

    /* 圆角 */
    --r-sm: 6px;
    --r-md: 10px;
    --r-lg: 16px;
    --r-xl: 20px;
}
```

---

## 方案二：科技深色（完整定义）

**特点**：深邃，专业、科技感强，适合数据密集型场景

### CSS Variables

```css
[data-theme="dark"] {
    /* 页面背景 */
    --bg-page: #0B0F15;
    --page-bg: linear-gradient(180deg, #0B0F15 0%, #0F1623 50%, #111827 100%);

    /* 卡片 · 玻璃拟态 */
    --bg-card: rgba(15, 22, 42, 0.72);
    --bg-card-solid: #111827;
    --bg-input: rgba(15, 22, 42, 0.6);
    --glass-bg: rgba(15, 22, 42, 0.72);
    --glass-blur: blur(18px);
    --glass-border: rgba(0, 229, 255, 0.12);

    /* 文字 */
    --txt-primary: #E2EAF2;
    --txt-secondary: #8899AA;
    --txt-muted: #4A5568;
    --txt-placeholder: #3A4555;

    /* 边框 */
    --bd: rgba(0, 229, 255, 0.08);
    --bd-focus: var(--neon-cyan);
    --bd-error: #FF4D6D;

    /* 品牌色 · 暗色降饱和处理 */
    --brand-primary: #E07060;
    --brand-primary-dk: #C05040;
    --brand-primary-lt: rgba(224, 112, 96, 0.15);
    --brand-primary-bg: rgba(224, 112, 96, 0.08);

    --brand-accent: #00E5FF;
    --brand-accent-dk: #00C4D6;
    --brand-accent-lt: rgba(0, 229, 255, 0.12);
    --brand-accent-bg: rgba(0, 229, 255, 0.06);

    --brand-gold: #D4983C;
    --brand-gold-lt: rgba(212, 152, 60, 0.12);
    --brand-gold-bg: rgba(212, 152, 60, 0.06);

    /* 语义色 */
    --ok: #00FF94;
    --warn: #FFB300;
    --err: #FF4D6D;

    /* 段位色 · 暗色模式适配 */
    --seg1-bg: rgba(0, 229, 255, 0.06);
    --seg1-c: #00E5FF;
    --seg1-bd: rgba(0, 229, 255, 0.18);
    --seg2-bg: rgba(123, 97, 255, 0.06);
    --seg2-c: #7B61FF;
    --seg2-bd: rgba(123, 97, 255, 0.18);
    --seg3-bg: rgba(255, 60, 172, 0.06);
    --seg3-c: #FF3CAC;
    --seg3-bd: rgba(255, 60, 172, 0.18);

    /* 霓虹色 */
    --neon-cyan: #00E5FF;
    --neon-cyan-dim: rgba(0, 229, 255, 0.15);
    --neon-cyan-glow: rgba(0, 229, 255, 0.35);
    --neon-purple: #7B61FF;
    --neon-purple-dim: rgba(123, 97, 255, 0.15);
    --neon-purple-glow: rgba(123, 97, 255, 0.35);
    --neon-pink: #FF3CAC;
    --neon-green: #00FF94;

    /* 阴影 · 暗色发光 */
    --shadow-sm: 0 1px 4px rgba(0, 0, 0, 0.3),
        0 0 0 1px rgba(0, 229, 255, 0.08),
        0 0 16px rgba(0, 229, 255, 0.04);
    --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4),
        0 0 0 1px rgba(0, 229, 255, 0.1),
        0 0 24px rgba(0, 229, 255, 0.06);
    --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5),
        0 0 0 1px rgba(0, 229, 255, 0.12),
        0 0 40px rgba(0, 229, 255, 0.08);
}
```

### Canvas 粒子背景（暗色专属）

```javascript
(function initBgCanvas() {
    const canvas = document.getElementById('bgCanvas');
    const ctx = canvas.getContext('2d');
    let W, H, particles = [];
    const PARTICLE_COUNT = 55;

    function resize() {
        W = canvas.width = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    class Particle {
        constructor() { this.reset(true); }
        reset(initial) {
            this.x = Math.random() * W;
            this.y = initial ? Math.random() * H : H + 10;
            this.r = Math.random() * 1.5 + 0.3;
            this.vy = -(Math.random() * 0.3 + 0.08);
            this.vx = (Math.random() - 0.5) * 0.2;
            this.alpha = Math.random() * 0.5 + 0.1;
            this.pulse = Math.random() * Math.PI * 2;
            this.pulseSpeed = Math.random() * 0.02 + 0.005;
            this.color = Math.random() > 0.6 ? '0,229,255' : '123,97,255';
        }
        update() {
            this.y += this.vy;
            this.x += this.vx;
            this.pulse += this.pulseSpeed;
            if (this.y < -10) this.reset(false);
        }
        draw() {
            const a = this.alpha * (0.5 + 0.5 * Math.sin(this.pulse));
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${this.color},${a})`;
            ctx.fill();
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.r * 3, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(${this.color},${a * 0.2})`;
            ctx.fill();
        }
    }

    for (let i = 0; i < PARTICLE_COUNT; i++) {
        particles.push(new Particle());
    }

    function animate() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        if (!isDark) {
            ctx.clearRect(0, 0, W, H);
            requestAnimationFrame(animate);
            return;
        }
        ctx.clearRect(0, 0, W, H);
        particles.forEach(p => { p.update(); p.draw(); });
        requestAnimationFrame(animate);
    }
    animate();
})();
```

### 扫描线纹理

```css
body::before {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
        0deg,
        transparent,
        transparent 2px,
        rgba(0, 229, 255, 0.012) 2px,
        rgba(0, 229, 255, 0.012) 4px
    );
    z-index: 0;
    pointer-events: none;
    opacity: 0;
    transition: opacity .4s ease;
}
[data-theme="dark"] body::before {
    opacity: 1;
}
```

### 卡片呼吸光晕动画

```css
@keyframes cardPulse {
    0%, 100% { box-shadow: var(--shadow-md); }
    50% { box-shadow: var(--shadow-lg), 0 0 30px rgba(0, 229, 255, 0.04); }
}
[data-theme="dark"] .card {
    animation: fadeUp .6s ease both, cardPulse 4s ease-in-out infinite;
}
```

---

## 主题切换实现

### HTML 结构
```html
<html lang="zh-CN" data-theme="light">
    <!-- 内容 -->
    <button class="theme-toggle" onclick="toggleTheme()">
        <svg class="sun-icon">...</svg>
        <svg class="moon-icon">...</svg>
        <span class="tt-label" id="ttLabel">DARK</span>
    </button>
</html>
```

### JavaScript
```javascript
function toggleTheme() {
    const html = document.documentElement;
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('tank-calc-theme', next);
}

// 页面加载时恢复偏好
document.addEventListener('DOMContentLoaded', () => {
    const saved = localStorage.getItem('tank-calc-theme');
    if (saved) {
        document.documentElement.setAttribute('data-theme', saved);
    }
});
```

---

## 字体推荐

```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&family=Orbitron:wght@400;600;700&display=swap" rel="stylesheet">
```

| 用途 | 字体 | 特点 |
|------|------|------|
| 正文 | Noto Sans SC | 中文支持好，清晰易读 |
| 数字/代码 | JetBrains Mono | 等宽，专业感 |
| 标题/科技感 | Orbitron | 几何感，现代科技 |

---

## 玻璃拟态卡片

```css
.card {
    background: var(--glass-bg);
    backdrop-filter: var(--glass-blur);
    -webkit-backdrop-filter: var(--glass-blur);
    border: 1px solid var(--bd);
    border-radius: var(--r-xl);
    box-shadow: var(--shadow-md);
}
```

---

## 动效建议

### 数字跳动动画（easeOutExpo）
```javascript
function animateValue(element, start, end, duration = 600) {
    const startTime = performance.now();
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - progress, 4); // easeOutExpo
        const current = start + (end - start) * eased;
        element.textContent = current.toFixed(decimals);
        if (progress < 1) requestAnimationFrame(update);
    }
    requestAnimationFrame(update);
}
```

### 卡片入场动画
```css
.card {
    animation: fadeUp 0.6s ease both;
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
```
