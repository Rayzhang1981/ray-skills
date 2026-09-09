# 交互式仪表板 HTML 模板

> 做交互式 dashboard 时读本文件。基于 Chart.js（CDN），浏览器直接打开，无服务器。

## 完整模板

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Title</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body { font-family: -apple-system, sans-serif; margin: 0; background: #f5f6f8; }
        .container { max-width: 1200px; margin: 0 auto; padding: 24px; }
        .header { display: flex; justify-content: space-between; align-items: center; }
        .kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 24px 0; }
        .kpi-card { background: white; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .kpi-value { font-size: 32px; font-weight: bold; margin: 8px 0 0; }
        .chart-card { background: white; border-radius: 8px; padding: 20px; margin: 16px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        canvas { max-height: 400px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Dashboard Title</h1>
            <select id="filter"><option value="all">All</option></select>
        </div>
        <div class="kpi-row">
            <div class="kpi-card"><div>Total Revenue</div><div class="kpi-value">$1.2M</div></div>
        </div>
        <div class="chart-card"><canvas id="mainChart"></canvas></div>
    </div>
    <script>
        const data = { /* 嵌入数据 */ };
        // 图表初始化、过滤器联动
    </script>
</body>
</html>
```

## 布局规范

1. **Header**：标题、日期范围、关键过滤器
2. **KPI 卡片**：3-5 个最重要数字
3. **主图表**：2-3 个主要可视化
4. **明细区**：下钻表格或次级图表
5. **Footer**：方法论、数据源、更新时间

## 交互清单

- 下拉过滤：类别 / 时间范围 / 分段
- 图表交互：悬停 tooltip、点击下钻
- 表格排序：点列头排序
- 动态更新：过滤器联动所有图表

## 注意事项

- 数据直接内嵌进 JS（`const data = {...}`），不依赖外部文件
- 过滤器变化时重新渲染所有图表
- 移动端响应式（grid auto-fit）
