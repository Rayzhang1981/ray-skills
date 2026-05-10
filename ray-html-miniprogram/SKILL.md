---
name: ray-html-miniprogram
description: 当用户需要将化工计算 HTML 文件转换为微信小程序模块，或有 HTML 计算工具想转成小程序、从现有HTML提取计算逻辑创建新小程序页面、将化工/过程工程计算工具移动端化时使用此技能。
agent_created: true
---

# HTML转微信小程序 Skill

## 概述

将现有的化工计算HTML文件转换为微信小程序模块，提取计算逻辑、优化UI/UX、确保参数准确性。基于真实项目经验，避免常见坑点。

## ⚠️ 关键约束（必须严格遵守）

### 约束1：一对一严格转化，不允许自由发挥
- **必须**严格基于HTML源文件进行转化
- **禁止**自行添加HTML中没有的选项、功能或参数
- **禁止**修改或省略HTML中的任何选项（如封头类型、储罐类型等）
- 案例：重力流储罐排空时间HTML有"立式储罐"、"卧式储罐"选项卡，小程序**必须**包含这些选项卡，不能省略

### 约束2：所有计算模块UI风格必须统一
- 参照已优化的计算模块（储罐容积计算、管道压力降-液体）风格
- 统一使用紫色渐变主题 (#667eea → #764ba2)
- 统一输入框样式：font-size: 36rpx，带边框和focus效果
- 统一按钮样式：圆角渐变按钮
- 统一结果卡片：渐变背景 + 金色高亮数值

## 典型触发场景

- "将这个HTML转成微信小程序"
- "创建小程序模块：压力降计算"
- "我的HTML有储罐计算，帮我做成小程序"
- 用户提供了HTML文件，要求进行小程序化

## 核心工作流程

### 第一步：分析HTML文件

1. **读取HTML源码**，重点关注：
   - JavaScript中的计算函数和参数定义
   - 输入字段（input/select）及其默认值
   - 计算公式和常数（如C值、摩擦因子等）

2. **提取关键参数**：
   - 所有物理常数和系数的定义
   - 计算公式的数学逻辑
   - 封头类型、流体类型等枚举值

**⚠️ 经验教训 #1**：参数必须与HTML源码严格一致！
- 案例：储罐计算HTML只有3种封头类型（elliptic/dish/hemi），C值分别为0.5/0.255/1.0
- 错误做法：小程序中定义了9种封头类型，导致用户看到的选择项与HTML不一致
- 正确做法：用`grep`或Read工具精确提取HTML中的参数定义，直接使用

### 第二步：创建计算逻辑模块

在`utils/`目录下创建独立的JS模块，例如：

```javascript
// utils/calc.js - 储罐容积计算
const HEAD_PARAMS = {
  'elliptic': { C: 0.5, label: '椭圆形封头 Ellipsoidal' },
  'dish': { C: 0.255, label: '碟型封头 Torispherical' },
  'hemi': { C: 1.0, label: '半球形封头 Hemispherical' }
};

function calcHeadVol(D, headType) {
  const C = HEAD_PARAMS[headType].C;
  return (Math.PI * Math.pow(D, 3) / 6) * C;
}

// ... 其他计算函数

module.exports = { HEAD_PARAMS, calcHeadVol, /* ... */ };
```

**⚠️ 经验教训 #2**：计算逻辑要从HTML中完整提取，不要"智能推断"！
- 使用Read工具读取HTML源码
- 复制粘贴关键函数和常数，不要自己重写
- 特别注意迭代计算（如Colebrook-White方程要50次迭代）

### 第三步：创建小程序页面

使用微信小程序标准结构：

```
pages/[module_name]/
├── [module_name].js      # 页面逻辑
├── [module_name].json    # 页面配置
├── [module_name]_wxml_reference.txt    # 页面结构（原 .wxml）
└── [module_name]_wxss_reference.txt    # 页面样式（原 .wxss）
```

**⚠️ 经验教训 #3**：输入框字体要够大！
- 用户反馈："数字都太小了，输入看不清楚"
- 错误做法：font-size: 28rpx（太小）
- 正确做法：font-size: 36rpx，并添加边框和focus效果

```css
/* 输入框优化样式 */
.input {
  font-size: 36rpx;  /* 足够大，清晰可见 */
  border: 2rpx solid #e0e0e0;
  border-radius: 8rpx;
  padding: 16rpx;
}

.input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3rpx rgba(102, 126, 234, 0.1);
}
```

### 第四步：UI优化模式（统一风格）

**⚠️ 所有模块必须使用统一的UI风格，参照储罐容积计算(volume)和压力降计算(pressure_drop)模块：**

**统一主题色**：紫色渐变 #667eea → #764ba2

**区块样式模板**：
```css
/* 区块通用样式 */
.section {
  background: white;
  border-radius: 20rpx;
  padding: 30rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 16rpx rgba(0,0,0,0.08);
}

/* 区块标题 */
.section-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 24rpx;
  padding-left: 16rpx;
  border-left: 6rpx solid #4a90e2;
}
```

**按钮样式模板**：
```css
.calc-btn {
  width: 100%;
  height: 100rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 36rpx;
  font-weight: 600;
  border: none;
  border-radius: 50rpx;
  margin: 32rpx 0;
  box-shadow: 0 8rpx 24rpx rgba(102, 126, 234, 0.4);
}
```

**结果卡片高亮**：
```css
.result-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16rpx;
  padding: 32rpx;
}

.result-value.highlight {
  color: #ffd700;  /* 金色高亮关键数值 */
  font-size: 48rpx;
  font-weight: bold;
}
```

### 第五步：添加默认值和测试数据

在页面的`data`中添加默认值，方便快速测试：

```javascript
data: {
  tanD: '2.0',   // 储罐直径
  tanL: '5.0',   // 储罐长度
  tanSF: '50',   // 安全容积百分比
  rho: '1000',   // 密度
  hInput: '1.0', // 液位高度
  // ... 其他字段
}
```

### 第六步：注册页面和导航

1. **在app.json中注册页面**：
```json
{
  "pages": [
    "pages/index/index",
    "pages/volume/volume",
    "pages/pressure_drop/pressure_drop"
  ]
}
```

2. **在首页添加入口**：
```xml
<!-- pages/index/index_wxml_reference.txt -->
<view class="module-card" bindtap="goToVolume">
  <text class="module-title">储罐容积计算 Tank Volume</text>
</view>
```

```javascript
// pages/index/index.js
goToVolume() {
  wx.navigateTo({ url: '/pages/volume/volume' });
}
```

## 特殊计算场景

### 压力降计算（Incompressible Fluid）

关键要点：
1. **Reynolds数判断**：层流（Re<2000）用λ=64/Re，湍流用Colebrook-White
2. **Colebrook-White方程**：需要50次迭代求解λ
3. **临界区判断**：当ε/d < 0.05时，选择Nikuradse公式
4. **局部阻力**：支持多个管件的当量长度系数输入（通常12个常见管件）

```javascript
function calcFriction(Re, eps_d) {
  if (Re < 2000) {
    return 64 / Re;  // 层流
  }
  
  // 湍流：Colebrook-White迭代
  let lambda = 0.02;  // 初始猜测
  for (let i = 0; i < 50; i++) {
    const rhs = -2 * Math.log10(eps_d / 3.7 + 2.51 / (Re * Math.sqrt(lambda)));
    lambda = 1 / (rhs * rhs);
  }
  return lambda;
}
```

### 储罐容积计算

关键要点：
1. **三种封头类型**：elliptic (C=0.5), dish (C=0.255), hemi (C=1.0)
2. **水平储罐**：需要计算弓形面积（segArea函数）
3. **垂直储罐**：需要考虑封头部分的体积
4. **容积表生成**：使用genTable函数生成不同液位高度对应的容积

## 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|---------|
| 计算结果与HTML不一致 | 参数定义不匹配 | 用Read工具重新检查HTML源码中的参数定义 |
| 封头类型选项过多 | 未严格按照HTML定义 | 只保留HTML中实际使用的类型 |
| 输入框数字太小 | font-size过小 | 设置为36rpx，添加边框和focus效果 |
| 页面无法跳转 | 未在app.json注册 | 检查app.json的pages数组 |
| 计算逻辑报错 | JS模块未正确导出 | 检查module.exports是否正确 |

## ⚠️ 版本保存（重要！必须执行）

### 为什么必须保存版本？
- 避免样式错乱后回滚困难
- 每次完成重要功能后，可以回溯到稳定状态
- 节省空间，使用 Git Tag（几乎零额外空间）

### 何时保存版本？
- 完成一个新模块的转换后
- 完成 UI 优化后
- 完成计算逻辑验证后
- **完成重要功能后，必须询问用户："本版本是否保存？"**

### 如何保存版本？

**方式一：询问用户（推荐）**
```
在完成重要功能后，主动询问用户：
"本版本是否保存为 v1.X？"
如果用户选择"保存"，执行：
1. git add . && git commit -m "描述本次更改"
2. git tag -a v1.X -m "版本说明"
3. 更新 VERSION_LOG.md
```

**方式二：使用保存脚本**
```bash
# Windows (双击运行)
save_version.bat

# Git Bash
./save_version.sh
```

脚本会自动：
1. 检查未提交的更改
2. 自动递增版本号（v1.0 → v1.1）
3. 创建 Git 标签
4. 更新 VERSION_LOG.md

### 版本回滚方法
```bash
# 回滚到指定版本（临时查看）
git checkout v1.0

# 返回最新版本
git checkout master

# 查看所有版本
git tag -l | sort -V
```

### 版本号规则
- 格式：`v主版本.次版本`（如 v1.0, v1.1, v2.0）
- 小改动递增次版本号（v1.0 → v1.1）
- 大功能更新递增主版本号（v1.9 → v2.0）

---

## 质量保证检查清单

完成转换后，务必检查：
- [ ] 所有物理常数和参数与HTML源码完全一致
- [ ] 封头类型/流体类型等枚举项与HTML一致
- [ ] 输入框字体≥36rpx，有边框和focus效果
- [ ] 按钮使用渐变色，符合模块主题色
- [ ] 结果卡片有高亮显示（金色或主题色）
- [ ] 页面data中包含默认值，便于测试
- [ ] app.json已注册新页面
- [ ] 首页有导航入口
- [ ] 计算逻辑经过实际数据验证
- [ ] **版本已保存，Git 标签已创建**

## 资源文件

本skill包含以下参考资源：

### references/
- `html_extraction_guide.md` - HTML源码提取技巧和注意事项

### assets/
- `page_template/` - 小程序页面模板目录
- `common_styles_wxss_reference.txt` - 通用样式片段（原 .wxss）

---

## 📌 版本控制提醒

**重要**：本项目已配置 Git 版本控制！

- **版本保存脚本**：`save_version.sh` / `save_version.bat`
- **版本日志**：`VERSION_LOG.md`
- **当前版本**：v1.0（2026-05-07）

**每次完成重要功能后，必须询问用户是否保存版本！**

---

**记住**：这个skill基于真实项目经验，每一步都有血泪教训。严格遵循工作流程，不要"聪明地"跳过步骤！
