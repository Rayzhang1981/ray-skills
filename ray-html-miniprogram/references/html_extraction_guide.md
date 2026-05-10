# HTML源码提取指南

基于真实项目经验，总结从HTML提取计算逻辑的最佳实践。

## 为什么需要精确提取？

**血泪教训**：第一次转换储罐计算时，小程序定义了9种封头类型，但HTML只有3种。用户发现后问："这是为什么？你的小程序计算文件中，计算公式和封头类型是否匹配？"

**根本原因**：没有精确提取HTML源码中的参数定义，而是"智能推断"或"参考标准"。

## 提取步骤

### 1. 定位关键函数和参数

使用Read工具读取HTML文件，重点关注：

```html
<script>
// 封头参数定义
const HEAD_PARAMS = {
  'elliptic': { C: 0.5, label: '椭圆形封头' },
  'dish': { C: 0.255, label: '碟型封头' },
  'hemi': { C: 1.0, label: '半球形封头' }
};

// 计算函数
function calcHeadVol(D, headType) {
  const C = HEAD_PARAMS[headType].C;
  return (Math.PI * Math.pow(D, 3) / 6) * C;
}
</script>
```

**关键**：直接复制这些值，不要查标准、不要"优化"、不要"补全"！

### 2. 提取计算公式

完整复制计算函数，包括：
- 变量定义
- 循环逻辑（如Colebrook-White的50次迭代）
- 条件判断（如层流/湍流判断）

```javascript
// Colebrook-White方程 - 必须50次迭代
function calcFriction(Re, eps_d) {
  if (Re < 2000) {
    return 64 / Re;  // 层流
  }
  
  let lambda = 0.02;
  for (let i = 0; i < 50; i++) {  // 注意：必须是50次！
    const rhs = -2 * Math.log10(eps_d / 3.7 + 2.51 / (Re * Math.sqrt(lambda)));
    lambda = 1 / (rhs * rhs);
  }
  return lambda;
}
```

### 3. 提取输入字段和默认值

记录所有input、select元素及其默认值：

```html
<body>
  储罐直径 D (m): <input type="text" id="tanD" value="2.0"><br>
  储罐长度 L (m): <input type="text" id="tanL" value="5.0"><br>
  封头类型: 
  <select id="headType">
    <option value="elliptic">椭圆形封头</option>
    <option value="dish">碟型封头</option>
    <option value="hemi">半球形封头</option>
  </select>
</body>
```

这些默认值要放到小程序页面的`data`中。

### 4. 提取UI文本（中英文）

HTML中通常包含中英文混合的标签，要完整保留：

```javascript
const HEAD_PARAMS = {
  'elliptic': { C: 0.5, label: '椭圆形封头 Ellipsoidal' },
  'dish': { C: 0.255, label: '碟型封头 Torispherical' },
  'hemi': { C: 1.0, label: '半球形封头 Hemispherical' }
};
```

## 常见错误

| 错误做法 | 正确做法 |
|---------|---------|
| 根据"标准"补全参数 | 只使用HTML中定义的参数 |
| 自己重写计算函数 | 直接复制HTML中的函数 |
| 给封头类型添加"标准值" | 使用HTML源码中的确切C值 |
| 忽略迭代次数 | 严格复制循环次数（如50次） |
| 修改公式"优化" | 保持原汁原味 |

## 检查清单

提取完成后检查：
- [ ] 所有常数和HTML完全一致（不要"大约"）
- [ ] 枚举值（封头类型、流体类型等）数量和值完全一致
- [ ] 计算函数的逻辑完全一致（包括迭代次数）
- [ ] 默认值从HTML的value属性提取
- [ ] 中英文标签完整保留

## 工具使用

- **Read工具**：读取HTML文件，查看完整源码
- **Grep工具**：搜索关键函数名、参数名
- **复制粘贴**：不要让AI"理解"后重写，直接复制代码！

---

**记住**：用户提供的HTML是事实的唯一来源（Source of Truth）。任何"改进"或"标准化"都是画蛇添足！
