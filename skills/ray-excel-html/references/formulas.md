# 储罐容积计算公式

## 符号说明

| 符号 | 含义 | 单位 |
|------|------|------|
| D | 储罐直径 | m |
| R | 储罐半径 (R = D/2) | m |
| L | 直筒长度 | m |
| SF | 直边长度（每侧） | m |
| SL | 直筒总长 (SL = L + 2×SF) | m |
| C | 封头高度系数 | - |
| h / h_liq | 液位高度 | m |
| h' | 上封头相对高度 | m |
| ρ | 介质密度 | kg/m³ |
| V | 容积 | m³ |
| W | 质量 (W = V × ρ) | kg |

### 封头类型系数

| 封头类型 | C 值 | 说明 |
|----------|------|------|
| 椭圆形 Elliptical | 0.5 | 半轴比 R:C = 2:1 |
| 碟型 Dished | 0.3 | 标准碟型 |
| 半球形 Hemispherical | 1.0 | 半球体 |

---

## 1. 封头体积

旋转椭球体体积公式（通用）：
```
V_head = (2/3) × π × C × R³
```

| 封头类型 | 公式 |
|----------|------|
| 椭圆形 | V = (2/3) × π × 0.5 × R³ = (1/3) × π × R³ |
| 碟型 | V = (2/3) × π × 0.3 × R³ |
| 半球形 | V = (2/3) × π × 1.0 × R³ = (2/3) × π × R³ |

---

## 2. 圆缺面积（截面积）

液面与罐体截面面积：
```
A_seg(r, h) = r² × arccos((r-h)/r) - (r-h) × √(2rh - h²)
```

- 当 h ≤ 0 时：A = 0
- 当 h ≥ 2r 时：A = π × r²

---

## 3. 卧式储罐容积

### 总体公式
```
V_horiz = A_seg(R, h_liq) × SL + V_head_part
```

- **直筒部分**：截面积 × 直筒总长
- **封头部分**：两端封头 Simpson 数值积分

### 封头部分（Simpson 积分）

封头为旋转椭球体，沿轴向 x (0 → C×R) 积分：
- 位置 x 处截面半径：`rx = R × √(1 - x²/(C×R)²)`
- 截面液体面积：`A_sec = segArea(rx, h_liq - R + rx)`
- 封头液位体积：`V_head = ∫₀^{CR} A_sec dx`

使用 50 段 Simpson 积分，误差 < 5×10⁻⁵ m³

---

## 4. 立式储罐容积

三段计算：

### 第 1 段：下封头区 (0 < h ≤ C×R)
```
V = π × h² × (3×C×R - h) / (3 × C²)
```

### 第 2 段：直筒区 (C×R < h ≤ L + C×R)
```
V = V_head_full + π × R² × (h - C×R)
```

其中：`V_head_full = (2/3) × π × C × R³`

### 第 3 段：上封头区 (L + C×R < h ≤ L + 2×C×R)
```
h' = h - L - C×R  （进入上封头的高度）
V = V_head_full + V_cyl_full + V_top(h')
```

其中：`V_top(h') = π × h'² × (3×C×R - h') / (3 × C²)`

---

## 5. 质量计算

```
W = V × ρ / 1000  （单位：T）
```

---

## 6. JavaScript 实现要点

### Simpson 积分实现
```javascript
function calcHorizOneHeadVol(R, C, h_liq) {
    const CR = C * R;
    const n = 50; // 偶数
    const dt = 1.0 / n;
    let s = 0;
    for (let i = 0; i <= n; i++) {
        const t = i * dt;
        const rx = R * Math.sqrt(Math.max(0, 1 - t * t));
        const h_sec = h_liq - R + rx;
        const fa = segArea(rx, h_sec);
        const w = (i === 0 || i === n) ? 1 : (i % 2 === 1 ? 4 : 2);
        s += w * fa;
    }
    return s * CR * dt / 3;
}
```

### 数值稳定性
- `arccos` 输入限制在 [-1, 1] 范围内
- 平方根内确保非负：`Math.max(0, 2*r*h - h*h)`
