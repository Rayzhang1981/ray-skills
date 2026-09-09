---
name: ray-hazop-lopa
slug: ray-hazop-lopa
displayName: "HAZOP/LOPA 定量分析报告生成器"
description: 工艺技术文件→HAZOP/LOPA 分析报告端到端工作流。输入工艺规程、反应热评估报告（RC1/ARC/DSC）、设备清单、参考文献 PDF，输出 26 列 LOPA 定量报告（可交付 HTML，主报告+附件分页 Tab 切换）。触发词：HAZOP、LOPA、工艺危害分析、生成HAZOP报告、泄放面积校核、SIL定级、热风险评估报告分析、HAZOP记录审查。基于企业内部 LOPA 项目实战沉淀。
version: 1.3.1
category: process-safety
tags: [HAZOP, LOPA, 工艺安全, 热风险评估, 泄放面积, SIL, 过程安全]
author: Rayzhang
license: MIT
platforms: [WorkBuddy]
agent_created: true
---

# ray-hazop-lopa

工艺安全 HAZOP+LOPA 定量分析报告生成器。融合团队正式报告框架（26 列 LOPA 全链路）与 AI 定量分析深度（动力学/泄放/MAWP），输出可直接交付的 HTML 报告。

## 适用场景

| 场景 | 输入 | 输出 |
|------|------|------|
| 生成新报告 | 工艺规程 + 反应热评估报告 + 设备清单 + 参考文献 | LOPA 定量报告 HTML（主报告+附件） |
| 审查已有报告 | HAZOP 分析记录 xlsm（团队版） | 深度分析 + 12 点优化建议 |
| 专项校核 | 热评估报告 / 泄放需求 | 附件级计算（动力学/泄放/MAWP） |

## 角色边界（v1.2.0 新增）

**本 skill 是 HAZOP 参与专家的分析助手，不是 HAZOP 主席，更不是最终裁决者。**
- ✅ 做：提取证据、标注缺口（缺失/矛盾/弱证据）、起草会议提问（给主席/工艺/设备/仪表/电气/消防/业主各专业）、给出候选原因/后果/待核实保护层、计算校核
- ❌ 不做：签发 HAZOP 结论、关闭行动项、批准设计、替代正式研讨会记录
- 所有输出定性为「供会议讨论的专家预案」，不是正式工作表结论——交付时在报告显著位置注明

## Red-team 复查（v1.2.0 新增，报告生成后必做）

生成报告后逐图（逐节点）做一轮对抗性复查，与 12 点自检互补（自检管格式，复查管内容）：

| 复查动作 | 说明 |
|---------|------|
| 删除不适用行 | 与图纸/数据不符的偏差行直接删，不留"以防万一" |
| 合并重复 | 同节点内重复场景合并（保留证据最强者） |
| 标记矛盾 | 与源图纸、拓扑证据、后期澄清矛盾的场景打红旗，写入行动项 |
| 证据回指 | 每个结论必须能指回来源（工艺规程页码/热评估曲线/计算书）——指不回 = 删 |
| 查漏 | 每张 P&ID 至少过一遍：泄压/联锁/止回/放空/双阀/惰化 六类保护是否都被问到 |

## 工作流（五步）

1. **输入收集与解析**
   - 读工艺规程（PDF/Word）、反应热评估报告（RC1/ARC/DSC/TSU）、设备数据表、参考文献 PDF
   - PDF/Word 转文本：markitdown / pdf 技能；xlsm 用 openpyxl（venv：`C:\Users\rayzh\.workbuddy\binaries\python\envs\default\Scripts\python.exe`，read_only+data_only 模式）

2. **数据提取与来源审计**
   - 提取关键参数：反应热/ΔTad/MTSR/TMRad（RC1/ARC）、热稳定性（起始分解温度/分解热/温升速率/Phi）、设备 MAWP
   - 建立**数据来源审计表**三态：实测 ✅ / 估算 🟡 / 缺口 ❌；估算项不进 LOPA 概率定级，仅定性支持

3. **定量分析（按需模块）**
   - 热风险：ΔTad/MTSR/TMRad/Stoessel 矩阵分级（热评估报告实测数据优先）
   - 双氧水/过氧化物分解动力学：两点 Arrhenius 外推（Ea/R = ln(k2/k1)/(1/T1−1/T2)），数值积分求温升时间线；污染 kF 放大坍缩
   - 泄放面积：API 520 纯气体（下限）｜DIERS/OMEGA 两相流（主方法）｜刘嚆储罐泄压口（常压设计）｜赵红乔 kF 污染修正——四方法交叉
   - MAWP：P = 2·S·E·t/(D+0.8t)（GB 150 薄壁圆筒）

4. **报告生成**
   - 26 列 LOPA 全链路表：场景号→偏移→原因→Cp→CF→Pp→S→Rp→IPL(PFD·状态)→Pr→Rr→缓解性保护→行动建议(PFD)→Rf
   - 结构：工艺与数据基线（含审计表）→ 风险矩阵与概率映射 → 节点划分 → 节点工作表 → 共因失效 → 残余风险声明 → 风险统计 → 行动项闭环 → SIL 衔接 → 版本记录
   - 附件分页化：估算项转独立附件页（计算细节+SVG 图表），单文件 Tab 切换（templates/lopa-report-template.html 骨架）

5. **质量自检（每版必做）**
   - 12 点检查清单逐项核对（checklists/lopa-12point-checklist.md）
   - 乱码扫描：`\ufffd` 计数 = 0
   - HTML 标签配对（`<section>` 开/关计数、`</html>` 闭合）
   - Edge headless 渲染验证（`--headless --screenshot`）

## LOPA 计算规则

- Pp = Cp × CF；Pr = Pp × Π(PFD)
- **仅"有效"状态预防性 IPL 计入 PFD**（待验证→不计或保守；不成立→明确标注）
- 缓解性保护（泄爆/隔爆/围堰/喷淋/锁气卸灰）在后果维度体现，不削减 Pr（NFPA 68 / ISO 16447 / GB/T 32857）
- 管理措施（SOP/检查表/防干转保护器）不计 PFD，作 CF 修正
- Cp↔矩阵等级映射：可能性等级 1-7 ↔ 年概率 <10⁻⁶ ~ >10⁻¹（矩阵为 7×可能性 × 5×严重性，四维后果：人员/财产/环境/声誉）

## 输出规范（可交付文件）

- **去过程化**：去掉版本说明卡片、自检对照、学习落地等元信息
- 矩阵维度标注准确（如 7×5，非 5×5）
- 附件页含计算细节+图表；估算与实测差异诚实呈现（不掩盖简化假设）
- 报告注明"AI 辅助初步分析，须由有资质 HAZOP 团队评审确认后方可作为正式文件"
- 残余风险声明页必含（所有边界条件结论如"DN100 仅 ≥30min 级"必须声明）

**工作表纪律（v1.3.0 新增，外部对比吸收）**——HAZOP 工作表/分析记录的硬性规则：
1. **空单元格写 "None" 绝不 blank**——blank 会被误读为"团队漏了这项"，None 表示"明确评估过、不适用/无"
2. **排除过的偏差要留痕**：对每条"不可信偏差"（引导词×参数组合被团队排除的）记一行理由——证明分析覆盖了全矩阵而非只挑有问题的查
3. **LOPA 转介行标准化**：HAZOP 表中标 LOPA 的行，转介信息按固定格式（偏差 / 引发原因+频率档 / 目标风险带 / 候选 IPL / 责任人 / 截止日期）——HAZOP 只负责"识别并转介"，不越界替 LOPA 定量

## 计算红线（工艺计算通用）

1. 单位换算必须双校验（Pa/kPa、kJ/min→W、m³/h vs kg/h——已两次踩坑）
2. 化学反应式先做原子平衡验证（C/H/N/O 数）
3. MAWP ≠ 设计压力（按实际壁厚/封头计算）
4. 用户给的数据先确认口径（单位？单台还是合计？）
5. 时间类计算脚本打印时单位标签必须与变量实际单位一致（跨函数传值先核对）
6. **nRT/V 分压计算 V 必须用 m³**（勿 ×1000 转 L）；**MPa→bar 是 ×10 不是 ÷10**（2026-08-11 calc_mawp/calc_massbal 双踩坑；手算 O₂ 分压曾把 MPa 当 bar）

## 参考数据（来自企业内部实战项目校验，可作同类装置评估基准）

> ⚠️ 本节原始数据含企业内部实测参数，不随开源版分发。评估同类装置时请以本企业/委托方的实测数据为准，方法可参考 scripts 与 checklists。

## 模板与清单

- `templates/lopa-report-template.html`：26 列 LOPA 报告 HTML 骨架（Tab 分页 + 附件占位）
- `checklists/lopa-12point-checklist.md`：12 点质量自检清单（勾选式）

## scripts 计算与工具（全部用 venv python 运行，如 `~/.workbuddy/binaries/python/envs/default/Scripts/python.exe`）

| 脚本 | 功能 | 用法示例 |
|------|------|---------|
| `calc_kinetics.py` | 分解动力学：两点 Arrhenius→Ea→温升时间线→污染 kF 坍缩 | `calc_kinetics.py --T1 66.1 --r1 0.109 --T2 118.3 --r2 15.26` |
| `calc_relief.py` | 泄放面积四方法：API520/DIERS/刘嚆/赵红乔 kF + 判定 | `calc_relief.py --DN 102 --Pset 50` |
| `calc_mawp.py` | MAWP 薄壁圆筒：P=2SEt/(D+0.8t) | `calc_mawp.py --D 1800 --t 10 --S 105 --name R203` |
| `calc_massbal.py` | 物料平衡/尾气富氧/异常加料温升压升 | `calc_massbal.py --mode o2` / `--mode dT` |
| `qa_scan.py` | 报告质量扫描：乱码/标签配对/场景编号/Rf/矩阵维度/残余风险 | `qa_scan.py 报告.html`（退出码 0=通过） |
| `extract_inputs.py` | 从工艺/热评估文本（markitdown 转换后）提取关键参数候选 | `extract_inputs.py 报告.md --show-ctx` |
| `to_word_pdf.py` | HTML→PDF（Edge headless）/ Word（pandoc） | `to_word_pdf.py 报告.html --both` |
| `export_actions.py` | 报告行动项表 → Excel（openpyxl） | `export_actions.py 报告.html` |
| `sync_publish.sh` | 更新后同步三处副本 + SkillHub 预检/发布 | `bash sync_publish.sh --pub "v1.2.0 说明"` |

验证基准：脚本正确性以各 calc 脚本内置单元断言为准（运行 `python <script> --selftest` 或对照工艺手册手算复核）。

## 版本更新与同步（Junction 单一源模式：改源=改专家，无需同步）

**机制（2026-08-11 已启用）**：专家插件目录中本 skill 的位置已由"静态副本"改为 **Windows Junction → 用户级源**（`C:\Users\rayzh\.workbuddy\plugins\marketplaces\my-experts\plugins\gong-yi-an\skills\ray-hazop-lopa` → `C:\Users\rayzh\.workbuddy\skills\ray-hazop-lopa`）。**用户级源更新 = 功易安即时使用新版，零同步成本**（已验证即时生效）。

**其他已 junction 化的 ray-* skill**：ray-pse-sharing、ray-pse-video、ray-ps-inforgraphic（同模式）。

**更新流程（每次迭代后）**：
```bash
# 1. 直接改用户级源（SKILL.md frontmatter 递增 version）
# 2. 功易安自动生效（junction 即时可见，无需同步）
# 3. 可选：发布新版到 SkillHub（市场分发）
bash ~/.workbuddy/skills/ray-hazop-lopa/scripts/sync_publish.sh --pub "v1.2.0 说明"
```

**注意**：WorkBuddy 插件市场更新/重装可能重建专家 skills 目录覆盖 junction——若发现专家目录下本 skill 变为普通目录，重跑重建命令：
```powershell
New-Item -ItemType Junction -Path "C:\...\gong-yi-an\skills\ray-hazop-lopa" -Target "C:\Users\rayzh\.workbuddy\skills\ray-hazop-lopa"
```
（删除旧目录后执行；管理员权限非必需。）

**版本管理**：每次内容变更递增 frontmatter `version`（1.1.0 → 1.1.1 / 1.2.0）；changelog 写入 README 版本记录表；上架状态验证 `skillhub search ray-hazop-lopa`。

> 脚本速查表见上文「scripts 计算与工具」章节（含 sync_publish.sh）。

## 生态联动（与其他技能/专家协同）

| 场景 | 调用 | 说明 |
|------|------|------|
| 场景生成/工作表展开 | `hazop-worksheet`（功易安专家） | 8 节点 × 参数×引导词全展开 |
| 热风险等级判定 | `thermal-risk`（Stoessel 矩阵） | RC1/ARC/DSC 数据 → 严重度/可能性分级 |
| SIL 定级与验证 | `sis-sil-eval` | LOPA PFD 需求 → SIL 等级 → PFDavg/HFT 验证 |
| 标准检索 | `standard-search` / ima 化工工艺数据库 | GB/AQ/API/NFPA 条款引用 |
| 事故培训视频/信息图 | `ray-pse-video` / `ray-ps-inforgraphic` | 报告结论 → 培训素材 |
| SkillHub 发布 | GitHub Rayzhang1981/ray-skills | README.md 已备，随 ray- 家族更新 |
