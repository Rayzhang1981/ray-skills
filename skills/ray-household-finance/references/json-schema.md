# 标准化持仓 JSON — 完整 Schema 与字段说明

> 本文档是「标准化持仓 JSON」的完整定义，供需要精确字段说明时按需查阅。SKILL.md 正文只保留核心字段索引。

## 完整 JSON 示例

```json
{
  "date": "2024-01-15",           // 快照日期（示例为虚构数据）
  "source": "excel",               // 数据源标识：excel|screenshot|manual|api|...
  "mm_funds": [                    // 活期宝/货基
    {"name": "示例货基A", "yield_rate": "0.3000（1.2000%）",
     "shares": 10000, "unpaid": 0, "cumulative_gain": 0}
  ],
  "funds": [                       // 非货币基金
    {"name": "示例短债基金（000000）", "type_info": "债券型|最新净值：1.0000（01-12）",
     "acls": "bond", "amount": 123456, "status": "正常",
     "gain": 1000, "gpct": 0.0081, "gpct_s": "0.0081", "nav": "1.0000"}
  ],
  "mm_total": 1000000, "fund_total": 500000, "grand_total": 1500000,
  "class_totals": {"mm": 1000000, "bond": 400000, "index": 50000, "qdii": 50000},
  "class_gains":  {"mm": 0, "bond": 0, "index": 0, "qdii": 0}
}
```

## 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `date` | str | 快照日期 `YYYY-MM-DD` |
| `source` | str | 数据源标识，用于追溯数据来自哪个 adapter |
| `mm_funds` | list | 货基/活期宝列表，每项含 `name`(名称)、`yield_rate`(7日年化字符串，如 `0.3558（1.3190%）`)、`shares`(总份额)、`unpaid`(未付收益)、`cumulative_gain`(累计收益) |
| `funds` | list | 非货币基金列表，每项含 `name`(名称+6位代码)、`type_info`(类型+净值原文)、`acls`(资产分类)、`amount`(金额)、`status`(状态)、`gain`(持仓收益)、`gpct`/`gpct_s`(收益率数值/字符串)、`nav`(最新净值) |
| `mm_total` | float | 活期宝总额 |
| `fund_total` | float | 非货币基金总额 |
| `grand_total` | float | 总资产 = mm_total + fund_total |
| `class_totals` | dict | 各类资产金额汇总，键 `mm|bond|index|qdii|mixed|other` |
| `class_gains` | dict | 各类资产收益汇总，键同上 |

## 关键约定

1. **`acls` 四类**：`bond`(债券型) / `index`(指数型) / `qdii`(QDII) / `mixed`(混合型) / `other`(其他)
2. **四类资产口径**（用于比例控制模型）：活期宝 / 国内债基 / 美债QDII / ETF权益。其中「ETF权益」= 指数型 + 纳指QDII。
3. **`yield_rate` 是字符串**（如 `0.3558（1.3190%）`），解析 7 日年化需提取括号内百分比：`float(yield_rate.split('（')[1].rstrip('%）'))`。
4. **`gpct_s` 是字符串**，可能为 `--`（无数据），`gpct` 为数值（无数据时为 0）。
5. **`status` 四态**：`有在途交易` / `到期` / `未到期` / `将到期`，影响基金 sheet 块高（见 SKILL.md 第1步）。

## 新增数据源 adapter 时的映射要求

任何新 adapter（screenshot/manual/api）只需产出符合上述 schema 的 JSON，下游分析（对比/轮动/加仓/比例/预测/可视化）零改动。映射时注意：

- 截图 OCR：货基收益率文案与基金名称/金额/收益的正则提取，务必保留 `name` 中的 6 位代码（下游用代码匹配目标债基）
- 手动录入：用户口述持仓时，`source` 填 `manual`，金额/收益逐项确认
- API：`source` 填 `api`，注意净值日期可能不同步，`date` 用持仓快照日期而非净值日期

## 交易流水 JSON（transactions，v2.2 新增）

与持仓快照并列的第二契约：**快照=现状，流水=历史（append-only）**。完整示例：

```json
{
  "version": 1,
  "transactions": [
    {"date": "2024-02-01", "fund_code": "000001", "fund_name": "示例债基（000001）",
     "type": "buy", "amount": 20000, "nav": 1.1029, "fee": 0},
    {"date": "2024-03-15", "fund_code": "000001", "type": "sell", "amount": 5000, "nav": 1.1100, "fee": 0},
    {"date": "2024-04-01", "fund_code": "000001", "type": "dividend", "amount": 120.5}
  ]
}
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `date` | ✅ | 交易确认日期 `YYYY-MM-DD` |
| `fund_code` | ✅ | 6 位代码锚点；无代码的自定标识须全局唯一 |
| `fund_name` | buy 时 | 基金名称，下游展示用 |
| `type` | ✅ | `buy`(买入) / `sell`(卖出/赎回) / `dividend`(分红到账) |
| `amount` | ✅ | 成交金额（元）；buy 为实际扣款（含费） |
| `nav` | 建议 | 成交净值；缺省该笔只计金额口径，不参与份额法成本 |
| `fee` | – | 申购/赎回费（元），默认 0 |

### 关键约定

1. **append-only**：只追加，不修改不删除历史记录；文件被误覆盖时从备份恢复
2. **历史无法回补**：从启用日起记流水，之前的交易接受缺失，成本基准以流水起点为准
3. **计算口径**（`scripts/cost_basis.py` 实现）：真实收益率 = (期末现值+累计回收−累计投入)/累计投入；加权平均成本 = Σ买入净额/Σ买入份额；XIRR = 现金流年化内部收益率
4. **敏感数据**：流水含交易行为，同受 SKILL.md 红线 7 约束（本地处理、分享前确认）
