# ray-hazop-lopa

工艺技术文件 → HAZOP/LOPA 定量分析报告的端到端工作流。输入工艺规程、反应热评估报告（RC1/ARC/DSC）、设备清单、参考文献 PDF，输出 26 列 LOPA 定量报告（可交付 HTML，主报告 + 附件分页 Tab 切换），并可选导出 PDF / Word / 行动项 Excel。

基于企业内部 LOPA 项目实战沉淀（2026-08-11 V2.0 融合版），由「功易安」工艺安全专家工作流提炼。

## 功能

- **五步工作流**：输入解析 → 数据来源审计三态（实测✅/估算🟡/缺口❌）→ 定量分析（动力学/泄放/MAWP/物料平衡）→ 26 列 LOPA 报告生成 → 12 点质量自检
- **LOPA 计算规则固化**：Pp=Cp×CF、仅"有效"预防性 IPL 计 PFD、缓解性保护（泄爆/隔爆）归后果维度（GB/T 32857）、Cp↔矩阵等级映射
- **8 个工具脚本**：动力学/泄放四方法/MAWP/物料平衡计算 + 质量扫描 + 参数提取 + PDF/Word 双输出 + 行动项 Excel 导出
- **可交付规范**：去过程化元信息、矩阵维度准确（7×5）、残余风险声明、0 乱码、标签配对、Edge 渲染验证

## 安装

```bash
# 复制到用户技能目录
cp -r ray-hazop-lopa ~/.workbuddy/skills/
# 依赖：openpyxl（行动项导出/回读）——用 WorkBuddy 托管 venv 已含
```

## 用法

```bash
# 报告生成：直接描述任务（AI 调用本 skill 执行五步工作流）
# 工具脚本（venv python）：
PY=~/.workbuddy/binaries/python/envs/default/Scripts/python.exe
$PY scripts/calc_kinetics.py            # 动力学
$PY scripts/calc_relief.py              # 泄放四方法
$PY scripts/calc_mawp.py                # MAWP
$PY scripts/calc_massbal.py --mode o2   # 尾气富氧
$PY scripts/qa_scan.py 报告.html        # 质量扫描
$PY scripts/extract_inputs.py 报告.md   # 参数提取
$PY scripts/to_word_pdf.py 报告.html --both
$PY scripts/export_actions.py 报告.html # 行动项 Excel
```

## 目录结构

```
ray-hazop-lopa/
├── SKILL.md                        # 工作流 + 规则 + 红线 + 生态联动
├── checklists/
│   └── lopa-12point-checklist.md   # 12 点质量自检（14 项勾选）
├── templates/
│   └── lopa-report-template.html   # 26 列 LOPA 报告骨架（Tab 分页）
└── scripts/
    ├── calc_kinetics.py  calc_relief.py  calc_mawp.py  calc_massbal.py
    ├── qa_scan.py       extract_inputs.py  to_word_pdf.py  export_actions.py
```

## 计算红线（内置）

1. 单位换算双校验（Pa/kPa、kJ/min→W、m³/h vs kg/h——已两次踩坑）
2. 反应式原子平衡（C/H/N/O 数）
3. MAWP ≠ 设计压力（按实际壁厚/封头）
4. 用户数据先确认口径（单位/单台/合计）
5. 时间类脚本打印单位与变量实际单位一致

## 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-08-11 | 初版：五步工作流 + 模板 + 12 点清单 |
| v1.1 | 2026-08-11 | +8 个工具脚本（计算/QA/提取/输出/导出）；生态联动 |
| v1.2 | 2026-08-26 | 角色边界 + Red-team 复查（报告生成后必做） |
| v1.3 | 2026-09-02 | 工作表纪律（外部对比吸收）：空单元格写 None 绝不 blank / 排除偏差留痕 / LOPA 转介行标准化 |
| v1.3.1 | 2026-09-06 | 12 点清单新增 11.5「需求值 ≠ 信用值」：需求 PFD 不得填入 SIF 概率列当信用值，信用取定级带值（SIL1 取 0.1）；识别特征=减缓后频率恒等于容忍标准（f×(T/f)≡T） |

## Roadmap

- [ ] 质量扫描脚本扩展：统计口径数字一致性自动核对
- [ ] 计算脚本集成到报告模板（参数化自动生成附件图表）
- [ ] 与 hazop-worksheet / thermal-risk / sis-sil-eval 深度联动
- [ ] 跨车间场景知识库（同类偏差/后果/保护层复用）

## 许可与说明

本技能为 AI 辅助工具，报告输出须由有资质 HAZOP 团队评审确认后方可作为正式文件。数据与标准引用以最新版本为准。
