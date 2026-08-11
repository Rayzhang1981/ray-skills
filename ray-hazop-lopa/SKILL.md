---
name: ray-hazop-lopa
description: 工艺技术文件→HAZOP/LOPA 分析报告端到端工作流。输入工艺规程、反应热评估报告（RC1/ARC/DSC）、设备清单、参考文献 PDF，输出 26 列 LOPA 定量报告（可交付 HTML，主报告+附件分页 Tab 切换）。触发词：HAZOP、LOPA、工艺危害分析、生成HAZOP报告、泄放面积校核、SIL定级、热风险评估报告分析、HAZOP记录审查。基于 701 项目实战沉淀（2026-08-11 V2.0 融合版）。
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

## 计算红线（工艺计算通用）

1. 单位换算必须双校验（Pa/kPa、kJ/min→W、m³/h vs kg/h——已两次踩坑）
2. 化学反应式先做原子平衡验证（C/H/N/O 数）
3. MAWP ≠ 设计压力（按实际壁厚/封头计算）
4. 用户给的数据先确认口径（单位？单台还是合计？）
5. 时间类计算脚本打印时单位标签必须与变量实际单位一致（跨函数传值先核对）

## 参考数据（701 项目已校验，可作同类装置基准）

- 50% H₂O₂：起始分解 66.1℃（ARC Phi=5.45）、分解热 2888 kJ/kg 纯、2.8℃/min@118.3℃、Ea≈104.5 kJ/mol、45→130℃ 绝热 15.2h（洁净）、Fe²⁺ 46.6 mg/kg 坍缩至 7.7s
- DN100（8171mm²）对 21m³ 储罐全罐分解：DIERS 需求 8443mm² → 不足；刘嚆常压法 DN300+
- 分解率 32.7% 是碱催化工艺固有（pH 9~10），应作基准工况非最坏工况

## 模板与清单

- `templates/lopa-report-template.html`：26 列 LOPA 报告 HTML 骨架（Tab 分页 + 附件占位）
- `checklists/lopa-12point-checklist.md`：12 点质量自检清单（勾选式）

## scripts 计算与工具（全部用 venv python 运行：`C:\Users\rayzh\.workbuddy\binaries\python\envs\default\Scripts\python.exe`）

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

验证基准（701 项目实测）：kinetics Ea=104.5/15.2h；relief DIERS 8443>DN102 8171；mawp 7.9/9.3 bar；massbal 16.9Nm³/h/ΔT47.4K/6.7bar。

## 生态联动（与其他技能/专家协同）

| 场景 | 调用 | 说明 |
|------|------|------|
| 场景生成/工作表展开 | `hazop-worksheet`（功易安专家） | 8 节点 × 参数×引导词全展开 |
| 热风险等级判定 | `thermal-risk`（Stoessel 矩阵） | RC1/ARC/DSC 数据 → 严重度/可能性分级 |
| SIL 定级与验证 | `sis-sil-eval` | LOPA PFD 需求 → SIL 等级 → PFDavg/HFT 验证 |
| 标准检索 | `standard-search` / ima 化工工艺数据库 | GB/AQ/API/NFPA 条款引用 |
| 事故培训视频/信息图 | `ray-pse-video` / `ray-ps-inforgraphic` | 报告结论 → 培训素材 |
| SkillHub 发布 | GitHub Rayzhang1981/ray-skills | README.md 已备，随 ray- 家族更新 |
