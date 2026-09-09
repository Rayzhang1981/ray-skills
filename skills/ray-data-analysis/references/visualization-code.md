# Python 可视化代码模板

> 画图时读本文件。交互图用 plotly，静态图用 seaborn/matplotlib。

## 基础模板（matplotlib）

```python
import matplotlib.pyplot as plt
import pandas as pd

# Load data
df = pd.DataFrame({...})

# Create figure
fig, ax = plt.subplots(figsize=(10, 6))

# Plot
ax.plot(df['x'], df['y'])  # 或 .bar() / .scatter()

# Style
ax.set_title('Clear, Descriptive Title', fontsize=14, fontweight='bold')
ax.set_xlabel('X Axis Label')
ax.set_ylabel('Y Axis Label')
ax.grid(axis='y', alpha=0.3)

# Show
plt.tight_layout()
plt.show()
```

## 常用图表（matplotlib + seaborn）

```python
import matplotlib.pyplot as plt
import seaborn as sns

# 样式
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# 折线图（趋势）
plt.figure(figsize=(10, 6))
plt.plot(df['date'], df['value'], marker='o')
plt.title('Trend Over Time')
plt.xlabel('Date')
plt.ylabel('Value')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('trend.png', dpi=150)

# 柱状图（对比）
plt.figure(figsize=(10, 6))
sns.barplot(data=df, x='category', y='amount')
plt.title('Amount by Category')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('comparison.png', dpi=150)

# 热力图（相关性矩阵）
plt.figure(figsize=(10, 8))
sns.heatmap(df.corr(), annot=True, cmap='coolwarm', center=0)
plt.title('Correlation Matrix')
plt.tight_layout()
plt.savefig('correlation.png', dpi=150)
```

## 设计原则

- **清晰**：去掉 chart junk，标签明确
- **准确**：柱状图从 0 开始，不截断轴夸大差异
- **可访问**：色盲友好配色
- **上下文**：关键点加参考线、注释

## 图表明细规则

- 柱状图 Y 轴必须从 0 开始（否则视觉夸大差异）
- 饼图 ≤5 类，超过用条形图
- 坐标轴都要有标签和单位
- 标题写"洞察"不写"指标名"（如"转化率连续 3 月下滑"而非"转化率"）
