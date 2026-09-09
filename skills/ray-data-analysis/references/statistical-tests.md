# 描述统计 + 统计检验速查

> 做统计分析时读本文件。

## 描述统计

| 统计量 | 说明 | 用途 |
|--------|------|------|
| Mean（均值）| 平均值 | 集中趋势 |
| Median（中位数）| 中间值 | 抗离群点 |
| Mode（众数）| 最常见值 | 分类数据 |
| Std Dev（标准差）| 围绕均值的离散度 | 变异性 |
| Min/Max | 范围 | 数据边界 |
| Percentiles（百分位）| 分布形状 | 基准对比 |

## Python 快速统计

```python
# 完整描述统计
stats = df['amount'].describe()
print(stats)

# 补充统计
print(f"Median: {df['amount'].median()}")
print(f"Mode: {df['amount'].mode()[0]}")
print(f"Skewness: {df['amount'].skew()}")
print(f"Kurtosis: {df['amount'].kurtosis()}")

# 相关性
correlation = df['sales'].corr(df['marketing_spend'])
print(f"Correlation: {correlation:.3f}")
```

## 统计检验速查

| 检验 | 用途 | 假设条件 | 效应量 | Python |
|------|------|---------|--------|--------|
| T-test | 比较两组均值 | 正态性、方差齐性、独立性 | Cohen's d | `scipy.stats.ttest_ind(a, b)` |
| Chi-square | 分类独立性 | 期望频数≥5 | Cramér's V | `scipy.stats.chi2_contingency(table)` |
| ANOVA | 比较 3+ 组均值 | 正态性、方差齐性、独立性 | η² | `scipy.stats.f_oneway(a, b, c)` |
| Pearson | 线性相关 | 连续变量、正态、线性 | r 本身 | `scipy.stats.pearsonr(x, y)` |
| Spearman | 等级相关（非正态）| 单调关系 | ρ 本身 | `scipy.stats.spearmanr(x, y)` |

## 检验前必查：假设条件

**三大假设**（参数检验通用）：

1. **正态性**：数据是否正态分布（`scipy.stats.shapiro` 或看直方图）
2. **方差齐性**：各组方差是否相等（`scipy.stats.levene`）
3. **独立性**：样本是否互相独立

**假设不满足怎么办**：
- 非正态 → 用非参数检验（Mann-Whitney U 代替 t 检验、Kruskal-Wallis 代替 ANOVA）
- 方差不齐 → 用 Welch's t 检验
- 先检查假设，再选检验——**参数检验用在非参数数据上 = 检验误用**

## 报告规范：APA 格式 + 效应量

> 原则：**不只报告 p 值，还要效应量和置信区间**。p 值只回答"是否有差异"，效应量回答"差异有多大"。

```
t 检验：
t(58) = 2.45, p = .017, d = 0.63, 95% CI [0.12, 1.14]

ANOVA：
F(2, 87) = 5.67, p = .005, η² = 0.12

相关分析：
r(98) = .45, p < .001, 95% CI [.28, .59]
```

**效应量解读（Cohen's d）**：
- 0.2 = 小效应 / 0.5 = 中效应 / 0.8 = 大效应

## 选平均还是中位数

- 分布对称、无极端值 → **均值**（信息量更大）
- 分布偏斜、有离群点 → **中位数**（更稳健）
- 报告里两个都给最稳妥，注明用哪个做主要结论

## 常见检验误用

❌ 非参数数据用参数检验（先查正态性）
❌ 只报告 p 值不报告效应量
❌ 相关=因果
❌ 多重比较不做校正（Bonferroni）
