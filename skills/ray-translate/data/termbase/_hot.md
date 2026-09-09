# _hot — 热词表（译前默认注入，免逐词 grep）

> **动态库 v3.1.0**：从四库晋升的"高频且无歧义"条目。每次翻译任务开工前按默认词典注入，无需逐词 grep。
> 三条铁律：
> ① **只收无歧义词**——base/charge/feed 类多义词永不入表，留在主库靠语境/辨析列；
> ② **硬顶 80 条**——晋升一条 = 同类使用最少的一条退回主库；
> ③ 热词表只免"译前查"，**译后拒用❌零命中扫描照做**。
> Schema 六列与主库一致；来源列统一标 `_hot v3.1.0`。

| EN | 推荐 ZH | 拒用❌ | 语境/辨析 | 来源 | 日期 |
|----|---------|--------|-----------|------|------|
| reactor | 反应器 | ❌反应堆(核语境) | 核心反应设备 | _hot v3.1.0 | 2026-09-06 |
| storage tank | 储罐 | — | 常压/压力储存 | _hot v3.1.0 | 2026-09-06 |
| heat exchanger | 换热器 | — | — | _hot v3.1.0 | 2026-09-06 |
| distillation column | 精馏塔 | — | — | _hot v3.1.0 | 2026-09-06 |
| centrifugal pump | 离心泵 | — | — | _hot v3.1.0 | 2026-09-06 |
| compressor | 压缩机 | — | — | _hot v3.1.0 | 2026-09-06 |
| control valve | 控制阀/调节阀 | — | — | _hot v3.1.0 | 2026-09-06 |
| safety valve | 安全阀 | — | — | _hot v3.1.0 | 2026-09-06 |
| check valve | 止回阀 | ❌检查阀 | 俗称单向阀 | _hot v3.1.0 | 2026-09-06 |
| rupture disc | 爆破片 | — | — | _hot v3.1.0 | 2026-09-06 |
| pressure gauge | 压力表 | — | — | _hot v3.1.0 | 2026-09-06 |
| flowmeter | 流量计 | — | — | _hot v3.1.0 | 2026-09-06 |
| P&ID | 管道仪表流程图 | — | 俗称 PID 图 | _hot v3.1.0 | 2026-09-06 |
| PFD | 工艺流程图 | — | — | _hot v3.1.0 | 2026-09-06 |
| residence time | 停留时间 | ❌居留时间 | 反应器设计 | _hot v3.1.0 | 2026-09-06 |
| pressure drop | 压降 | — | — | _hot v3.1.0 | 2026-09-06 |
| batch process | 间歇过程 | ❌批量过程 | 又译批处理过程 | _hot v3.1.0 | 2026-09-06 |
| pilot plant | 中试装置 | — | — | _hot v3.1.0 | 2026-09-06 |
| commissioning | 试车 | ❌调试(泛) | — | _hot v3.1.0 | 2026-09-06 |
| startup | 开车 | — | 装置开车 | _hot v3.1.0 | 2026-09-06 |
| shutdown | 停车 | ❌关机 | 装置停车 | _hot v3.1.0 | 2026-09-06 |
| steam | 蒸汽 | ❌蒸气(指水蒸气时) | 专指水蒸气；vapor 泛指蒸气 | _hot v3.1.0 | 2026-09-06 |
| cooling water | 冷却水 | — | — | _hot v3.1.0 | 2026-09-06 |
| instrument air | 仪表空气 | — | 俗称仪表风 | _hot v3.1.0 | 2026-09-06 |
| packing | 填料 | ❌包装 | 塔内件语境 | _hot v3.1.0 | 2026-09-06 |
| tray | 塔板 | ❌托盘/盘子 | 板式塔内件 | _hot v3.1.0 | 2026-09-06 |
| reflux ratio | 回流比 | — | — | _hot v3.1.0 | 2026-09-06 |
| benzene | 苯 | ❌笨(字形误) | — | _hot v3.1.0 | 2026-09-06 |
| toluene | 甲苯 | — | — | _hot v3.1.0 | 2026-09-06 |
| methanol | 甲醇 | ❌木精(旧) | — | _hot v3.1.0 | 2026-09-06 |
| ethanol | 乙醇 | — | 口语"酒精" | _hot v3.1.0 | 2026-09-06 |
| acetone | 丙酮 | — | — | _hot v3.1.0 | 2026-09-06 |
| sodium hydroxide | 氢氧化钠 | — | 俗名烧碱 caustic soda | _hot v3.1.0 | 2026-09-06 |
| sulfuric acid | 硫酸 | — | — | _hot v3.1.0 | 2026-09-06 |
| ethylene | 乙烯 | — | — | _hot v3.1.0 | 2026-09-06 |
| catalyst | 催化剂 | — | — | _hot v3.1.0 | 2026-09-06 |
| polymer | 聚合物 | — | — | _hot v3.1.0 | 2026-09-06 |
| monomer | 单体 | — | — | _hot v3.1.0 | 2026-09-06 |
| solvent | 溶剂 | — | — | _hot v3.1.0 | 2026-09-06 |
| corrosion | 腐蚀 | ❌锈蚀(泛用) | — | _hot v3.1.0 | 2026-09-06 |
| maintenance | 维修/维护 | — | — | _hot v3.1.0 | 2026-09-06 |
| inspection | 检验/检查 | — | — | _hot v3.1.0 | 2026-09-06 |
| equipment | 设备 | ❌装备 | — | _hot v3.1.0 | 2026-09-06 |
| medium | 介质 | ❌媒介 | 工艺介质 | _hot v3.1.0 | 2026-09-06 |
| utility | 公用工程 | ❌公共事业 | 水电汽风 | _hot v3.1.0 | 2026-09-06 |
| runaway reaction | 失控反应 | — | — | _hot v3.1.0 | 2026-09-06 |
| thermal runaway | 热失控 | — | — | _hot v3.1.0 | 2026-09-06 |
| incompatible materials | 不相容物料 | ❌不兼容 | 混配禁忌 | _hot v3.1.0 | 2026-09-06 |
| hydrogen gas | 氢气 | — | — | _hot v3.1.0 | 2026-09-06 |
| PSM | 过程安全管理 | — | process safety management | _hot v3.1.0 | 2026-09-06 |
| PHA | 工艺危害分析 | — | process hazard analysis | _hot v3.1.0 | 2026-09-06 |
| HAZOP | 危险与可操作性分析 | — | hazard and operability study | _hot v3.1.0 | 2026-09-06 |
| LOPA | 保护层分析 | — | layer of protection analysis | _hot v3.1.0 | 2026-09-06 |
| SIL | 安全完整性等级 | — | safety integrity level | _hot v3.1.0 | 2026-09-06 |
| SIS | 安全仪表系统 | — | safety instrumented system | _hot v3.1.0 | 2026-09-06 |
| MOC | 变更管理 | — | management of change | _hot v3.1.0 | 2026-09-06 |
| mechanical integrity | 机械完整性 | — | PSM 要素 | _hot v3.1.0 | 2026-09-06 |
| SDS | 安全技术说明书 | — | safety data sheet；旧称 MSDS | _hot v3.1.0 | 2026-09-06 |
| confined space | 受限空间 | ❌limited space | — | _hot v3.1.0 | 2026-09-06 |
| hot work | 动火作业 | ❌fire work | — | _hot v3.1.0 | 2026-09-06 |
| LOTO | 挂牌上锁 | ❌stop, tag, lock | lockout/tagout | _hot v3.1.0 | 2026-09-06 |
| PPE | 劳动防护用品 | — | personal protective equipment | _hot v3.1.0 | 2026-09-06 |
| flammable range | 爆炸极限 | ❌explosive range | LEL–UEL | _hot v3.1.0 | 2026-09-06 |
| LEL | 爆炸下限 | — | lower explosive limit | _hot v3.1.0 | 2026-09-06 |
| deflagration | 爆燃 | — | 与爆轰 detonation 区分 | _hot v3.1.0 | 2026-09-06 |
| detonation | 爆轰 | — | — | _hot v3.1.0 | 2026-09-06 |
| fire extinguisher | 灭火器 | — | — | _hot v3.1.0 | 2026-09-06 |
| evacuation | 疏散 | — | — | _hot v3.1.0 | 2026-09-06 |
| emergency plan | 应急预案 | — | — | _hot v3.1.0 | 2026-09-06 |
| safety culture | 安全文化 | — | — | _hot v3.1.0 | 2026-09-06 |
| near miss | 未遂事件 | — | 又译险肇事故 | _hot v3.1.0 | 2026-09-06 |
| dust explosion | 粉尘爆炸 | — | — | _hot v3.1.0 | 2026-09-06 |
| static electricity | 静电 | — | 静电接地 static grounding | _hot v3.1.0 | 2026-09-06 |
