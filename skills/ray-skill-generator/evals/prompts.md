# 触发用例套件 — ray-skill-generator

> 用途：`description` 的**回归用例**。每次改动 description（或本 skill 的路由边界）后重跑本套件，确认路由未退化。
> 来源：Phase 3「触发双向验证」的 3 should-trigger + 3 near-miss。
> 判据：should-trigger 全部命中本 skill；near-miss 全部**不**命中本 skill、且命中注明的相邻 skill。
> ⚠️ 本套件是**自举产物**——本 skill 教别人「触发用例写完即落盘」，自己亦须在册。

## should-trigger（应命中本 skill）

| # | 用户会说 | 预期 |
|---|---------|------|
| 1 | 帮我做个 skill，把 C 盘清理的流程固化下来 | 命中本 skill（从零创建 → Phase 0 起走五阶段） |
| 2 | 写个技能：输入工艺参数、输出计算书 | 命中本 skill（CREATE 场景，先设计再构建） |
| 3 | 新建一个 skill，触发词是「查标准」「标准在哪」 | 命中本 skill（CREATE；顺带按 Phase 0 设计 description 触发词） |

## near-miss（不应命中本 skill，关键词相似）

| # | 用户会说 | 预期 |
|---|---------|------|
| 1 | 优化一下 ray-cclean 这个 skill，看看别人怎么做的 | 不命中本 skill → 命中 `ray-skill-evolve`（**已有** skill 优化＝EVOLVE 场景，本 skill 只管从零创建） |
| 2 | 盘点一下技能库，哪些该退役 | 不命中本 skill → 命中 `ray-skill-manager`（盘点/编排属 manager 主场） |
| 3 | 把这个会话复盘一下，沉淀经验 | 不命中本 skill → 命中 `ray-self-reflection`（对象是**任务**，不是 skill 的创建） |

## 路由边界备注

- 本 skill 与 `ray-skill-evolve` 的分界：**从零创建（CREATE）** vs **已有 skill 优化（EVOLVE）**。
  用户说「做个 skill」但宾语其实是**已存在的 skill**（如「把那个 skill 做好点」）时，应路由 evolve。
- 本 skill 与 `ray-file-distil` 的分界：资料蒸馏（「把这本书做成 skill」）走 `ray-file-distil`，
  本 skill 管**没有现成资料**、需要从需求澄清开始的创建。
