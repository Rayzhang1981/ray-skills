# _hits — 任务命中台账（动态库的频次信号源）

> 每次任务收尾（术语审计时）追加**一行**，不展开、不写长文。格式：
>
> `YYYY-MM-DD | 任务一句话 | 命中词条1, 词条2, ...`
>
> 迁移判定（攒 10 个任务或月度做一次，不逐任务调）：
> - **升级**：台账高频且无歧义 → 晋升 `_hot.md`（上限 80，晋升一条退回一条）
> - **毕业**：入库 90 天以上且台账零命中 → 移入 `_graduated.md`（永不删除）

## 台账

2026-09-08 | 设备分类详解PPT备注英文化（147页，EN.pptx 备注中文→英文） | kettle, canned motor pump, breather valve, RTO (regenerative thermal oxidizer)
2026-09-08 | CHEF Manual v2.0 英→中全文（189页，方向三+并行子代理15个） | airborne quantity, source model, flash fraction, plume/puff, enabling condition, conditional modifier, TNR, de minimis consequence, occupied building, human action IPL（新增17条入 safety.md）
2026-09-12 | ANSI/ISA-18.2-2016 报警管理系统标准 英→中全文（方向三：13 并行子代理 + spec 驱动 + Word COM，74 页交付 PDF） | 报警原则, 审查, 抑制, 依据设计抑制, 搁置, 停用, 触发状态, 确认, 报警泛滥, 干扰报警, 抖动报警, 瞬时报警, 陈旧报警, 合理化, 报警优先级, 报警设定值, 报警延迟, 报警解除延迟, 报警死区, 通告器, 操作员（新增 69 条入 safety.md）
2026-09-13 | EEMUA Publication 191 第 3 版 报警系统设计、管理与采购指南 英→中全文（源 PDF 274 页，方向三：58 作业 + 6 并行子代理 + 表格择优 v6 + Word COM，216 页交付 PDF） | 报警系统性能指标, 稳态运行, 扰动工况, 优先级矩阵, 风险降低系数, PFDavg, 安全相关报警, 报警响应定义, 常驻报警, 报警负荷, 报警日志, 长期归档, 报警系统审核, 基准比对, 瞬时报警, 合理化, 人机界面, 非计划停车, 报警系统生命周期, 异常工况管理, 本质安全, 报警生成, 报警显示, 报警处理, 报警配置, 采购, 试车, 可用性, 态势感知, 报警系统规格书（新增 36 条入 safety.md 十三节；英式拼写并收敛）
2026-09-14 | PGS 2 黄皮书 2005《物理效应计算方法》英→中全文（870 页，方向三·版式保持型原位回贴 + 101 并行分片） | 新增 37 条入 safety.md 十四节（后果建模）：源项, 射流, 闪火, 池火, 蒸气云爆炸, 喷射火, 火球, 概率单位, TNT当量, 扩散, 减缓措施, 事故升级, 太阳辐射, 相对湿度, 个体风险（以上经 AQ/T 3046-2013 / DB32/T 4745-2024 / T/COSHA 71-2026 确证）；流出, 重气, 被动扩散, 透射率, 爆炸波, 冲量, 多能法, 障碍物密集度, 受限程度 等 23 条标记待核；LFL/UFL 并入既有 LEL/UEL 行
2026-09-14 | PGS 2 术语审计·权威源二次核验（SH/T 3226-2024 / GB/T 37243-2019 / DB32/T 4745-2024 / AQ/T 3046-2013 读图核验） | 纠错 1 条：rainout 液滴沉降→**液滴降落**（SH/T 3226 3.1.16 明文）；新增 29 条（可信事故场景CAS, 过流阀, LSIR, IRPA, PLL, ALARP, 抗爆设防荷载, FN曲线, 早期/晚期池火, SLOD, SLOT, 立即/延迟点火, 灾难性破裂, 连续/瞬时释放, IDLH, ERPG, 泄漏单元, 系统隔离设施, 点火能力, 热辐射, 超压, 外部安全防护距离, 点火源 等）；BLEVE 变体并收（沸腾液体扩展蒸气云爆炸 ↔ 沸腾液体扩展蒸气爆炸）
2026-09-15 | CHEF Calculation Aid v4.5 xlsm 英→中全量（方向一：XML 手术式替换 + 462 单元格字面量/枚举三处一致 + Excel 全量重算对账 44,365 单元格零数值差） | release, aerosol fraction, head space, building or head space explosion, flash back, business loss, Class 1 dust, deflagration index, fundamental burning velocity, loss of containment, time at risk, incident outcome, spray distance, revealed failure / unrevealed failure, fragment range, peak overpressure, scaled overpressure, impulse, vapor quality, blast wave, dense gas, congestion, occupant（新增 23 条入 safety.md 十五节，含 3 条同源冲突标注）
2026-10-08 | CCPS 中英文术语词汇表 2026-10-07 吸收（526 条源 → 四库 1141→1497：合并 29 冗余 + 新增 385，18 条不收；口径统一 23 处） | PHA 过程危害分析, CCPS 化学过程安全中心, PSM 过程安全管理, RCA 根原因分析, MI 设备完好性, IPL 独立保护层, LOPA 保护层分析, SIL 安全完整性等级, SIS 安全仪表系统, SIF 安全仪表功能, PHA, IDLH 立即威胁生命和健康浓度, ERPG 紧急响应计划指南, PPE 个体防护装备, P&ID 管道及仪表流程图, FMEA/FMECA 失效模式, MSDS 化学品安全技术说明书, LOTO 挂牌上锁, SLA/SLOD/SLOT 毒性终点, RBI/PSSR/HAZID/PDCA/ITPM, BPCS/PAC/SCADA/DCS, 机构名 40+（AIChE/AIHA/ACGIH/ASME 系/NFPA 系…）（新增 385 条，来源列标「CCPS词汇表2026-10-07」+ 源状态）
