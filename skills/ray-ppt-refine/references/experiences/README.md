# Experiences Index — 经验分类索引

> 按主题分类存储，SKILL.md 主文件只保留最近 3 条 + 待回流 pending 条目。
> Step 3 诊断确认 / Step 4 修复执行前，按主题读对应文件。

| 文件 | 主题 | 条目数 | 何时读 |
|------|------|:---:|------|
| `overflow.md` | 文字溢出、版式超出、高度计算 | 6 | Step 4 修复执行前（重叠/卡片/字号）|
| `layout-pitfalls.md` | 版式选择、批量注入、模板沉淀 | 6 | Step 2 设计语言选择 / Step 4 批量操作前 |
| `image-assets.md` | 配图来源、生图 prompt、VL 核验 | 5 | Step 4 配图执行前 |
| `template-skin.md` | 换肤意图、模板套用、配色迁移 | 1 | Step 3 换肤确认前 |

## 经验写入格式（LRN 模板）

```markdown
## LRN-YYYYMMDD-NNN：标题

**Date**: YYYY-MM-DD
**Problem**: 现象（用户反馈 / 自发现）
**Root Cause**: 根因（为什么会发生）
**Fix**: 修复方案（具体到代码/参数/规则）
**Rule**: 沉淀到哪（哪个文件哪个表 / 哪个脚本哪段）
**Status**: pending | resolved
```

## pending 条目跟踪

> 待回流到主流程的 pending 条目（优化时优先回流这些）：

- overflow.md：LRN-20260817-003（重叠检测行高估算）
- layout-pitfalls.md：LRN-20260817-002（自产 deck 改源）/ LRN-20260819-003（高手版六语言）/ LRN-20260819-007（资源完整性自检）/ LRN-20260819-008（DNA 提取重绘）
- image-assets.md：LRN-20260818-001（行高估算器）/ LRN-20260818-002（图库规模）/ LRN-20260818-003（VL 判定）/ LRN-20260819-002（页面级 VL 核验）
