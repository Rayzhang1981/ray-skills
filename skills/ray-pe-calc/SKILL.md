---
name: ray-pe-calc
slug: ray-pe-calc
displayName: 工艺计算工具箱
version: 2.2.0
description: |
  化工工艺计算工具箱。整合单位换算、管道压降、换热器面积、泵NPSH、安全阀喉径、
  储罐呼吸量、控制阀口径七大工艺计算模块 + 计算书生成 + 数据表格生成两大输出模块。
  基于自然语言意图识别自动路由到对应计算子模块，无需手动选择。
  预留扩展接口：新增计算模块仅需三步（建脚本 + 写说明 + 注册路由）。
agent_created: true
---

# 工艺计算工具箱 (Process Engineering Calculator)

化工/过程工程工艺计算统一入口。覆盖七大核心工艺计算 + 两大输出模块。

---

## 判断与路由机制

本技能内置 **模块路由表**（见下方），WorkBuddy 根据用户的自然语言描述自动识别意图，路由到正确的计算子模块。

**路由逻辑**：
1. 从用户描述中识别"计算类型"（管道压降？换热面积？安全阀？……）
2. 提取用户提供的参数（流量、压力、管径、温度等）
3. 调用对应子模块脚本执行计算
4. 解释结果，必要时调用 `calc_report` 生成计算书或 `data_table` 生成对比表

**如果用户描述模糊无法判断，主动追问计算类型**，不猜测。

---

## 模块路由表

| # | 模块 | 功能 | 触发场景与关键词 | 脚本路径 |
|---|------|------|----------------|---------|
| 1 | `unit_converter` | 工程单位换算 | "单位换算""换算""转换单位""kPa转MPa""GPM转m³/h""摄氏度转华氏度""bar转psi" | `modules/unit_converter/convert.py` |
| 2 | `pipe_pressure_drop` | 管道压降 | "管道压降""管损""水力计算""Darcy""压降计算""摩擦阻力" | `modules/pipe_pressure_drop/calc.py` |
| 3 | `heat_exchanger` | 换热器面积估算 | "换热器""换热面积""LMTD""热负荷""冷凝器""蒸发器""U值" | `modules/heat_exchanger/calc.py` |
| 4 | `pump_npsh` | 泵NPSH与扬程 | "NPSH""汽蚀余量""泵扬程""离心泵""泵选型""气蚀""泵计算" | `modules/pump_npsh/calc.py` |
| 5 | `safety_valve` | 安全阀喉径(API 520) | "安全阀""泄放阀""安全阀计算""喉径""API 520""泄放面积""PSV sizing" | `modules/safety_valve/calc.py` |
| 6 | `tank_breather` | 储罐呼吸阀(API 2000) | "呼吸阀""储罐呼吸""API 2000""热呼吸""工作呼吸""breather valve""储罐通气" | `modules/tank_breather/calc.py` |
| 7 | `calc_report` | 计算书生成 | "生成计算书""出计算报告""计算书""设计院格式""正式计算文件" | `modules/calc_report/gen.py` |
| 8 | `data_table` | 工程表格生成 | "生成表格""对比表""设备选型对比""工况汇总表""材料表""管径比选表" | `modules/data_table/gen.py` |
| 9 | `control_valve` | 控制阀口径(ISA 75.01.01) | "控制阀""调节阀""阀门口径""Cv计算""Kv""ISA 75""阀门选型""control valve sizing""阀选型" | `modules/control_valve/calc.py` |

### 适用边界（不适用场景必须提示用户改用专业方法）

各模块为初筛/快速核算工具，以下场景**超出公式假设，结果不可直接用于设计**，必须向用户声明：

| 模块 | ❌ 不适用场景 | 应改用 |
|------|-------------|--------|
| `pipe_pressure_drop` | 两相流/闪蒸流、可压缩临界（阻塞）流、非牛顿流体 | 两相流专门方法（如 Lockhart-Martinelli）、等熵流计算 |
| `heat_exchanger` | 严密壳侧分析、沸腾/冷凝两相设计、U 值未知（应先算两侧膜系数） | Bell-Delaware 法、分区冷凝计算 |
| `pump_npsh` | 非牛顿/固液混合浆液、变频泵全特性曲线 | 厂商 NPSH 曲线实测数据 |
| `safety_valve` | 两相/闪蒸泄放（DIERS 方法）、火灾工况（需先按 API 521 算泄放量）、最终设计 | DIERS/OMEGA 方法 + 权威 API 520/521/526 原文 |
| `control_valve` | 低温/浆料/高粘等需厂商降额的特殊工况、噪声预估 | 制造商选型软件与实测降额数据 |
| `tank_breather` | 低压储罐（设计压力 >2.5 kPa 表压）、特殊介质挥发特性 | API 2000 逐条核算 + 厂商选型 |

---

## 子模块详细说明

### 1. unit_converter — 工程单位换算

**功能**：化工/过程工程常用单位换算，覆盖压力、流量、温度、长度、质量、能量、粘度、密度、传热系数九大类。

**调用方式**：
```bash
python modules/unit_converter/convert.py <value> <from_unit> <to_unit>
# 示例
python modules/unit_converter/convert.py 100 kPa bar
python modules/unit_converter/convert.py 50 m3/h L/s
python modules/unit_converter/convert.py 100 C F
```

**列出支持的单位**：
```bash
python modules/unit_converter/convert.py --list
```

**支持类别**：pressure | flow_rate | temperature | length | mass | energy | viscosity_dynamic | density | htc（传热系数）

**注意**：温度是°C↔°F↔K公式转换，非温差转换。

---

### 2. pipe_pressure_drop — 管道压降

**功能**：基于 Darcy-Weisbach 方程和 Colebrook-White 摩擦系数的管道压降计算。支持液体和气体，含直管+管件局部阻力(K-factor法)。

**公式**：ΔP = f × (L/D) × (ρv²/2)

**调用方式**：
```bash
python modules/pipe_pressure_drop/calc.py \
  --flow 50 --unit m3/h --id 100 --density 1000 --viscosity 1.0 \
  --length 100 --roughness 0.046 --fittings 5.0
```

**关键参数**：
- flow(流量) | unit(m3/h 或 kg/h) | id(内径 mm) | density(kg/m³)
- viscosity(cP) | length(m) | roughness(mm, 默认 0.046 碳钢) | fittings(K 系数)
- --gas(气体标志)；气体额外：--mw(分子量 g/mol) | --T(温度°C) | --P(压力 kPaG)

---

### 3. heat_exchanger — 换热器面积估算

**功能**：基于 LMTD 对数平均温差法的换热器面积快速估算。支持显热加热/冷却、冷凝、蒸发三种类型。内置常见工况U值参考。

**公式**：A = Q / (U × ΔT_lm × F)

**调用方式**：
```bash
python modules/heat_exchanger/calc.py \
  --type sensible --hot_flow 10000 --hot_cp 4.18 \
  --hot_tin 120 --hot_tout 80 --cold_tin 30 --cold_tout 70 \
  --u_value 800 --margin 15
```

**关键参数**：--type(sensible/condensation/evaporation) | --hot_flow(kg/h) | --hot_cp(kJ/kg·°C)
- --u_value(W/m²·°C) | --margin(%, 默认15)

**内置典型U值参考**（W/m²·°C）：水-水 800-1500 | 蒸汽-水 1000-4000 | 气体-气体 10-40 | 有机冷凝器 300-800 | 再沸器 500-1500

---

### 4. pump_npsh — 泵NPSH与扬程

**功能**：离心泵 NPSHa（有效汽蚀余量）和总扬程核算。自动判断汽蚀风险（NPSHa - NPSHr ≥ 0.5m）。

**公式**：NPSHa = (P₁ - Pv)/(ρg) + v₁²/(2g) - hf_suction ± z

**调用方式**：
```bash
python modules/pump_npsh/calc.py \
  --flow 50 --suction_pres 101.325 --vapor_pres 47.4 \
  --density 972 --suction_id 100 --suction_len 10 --elevation 2.0 \
  --discharge_pres 500 --discharge_len 50 --discharge_id 80 --npshr 3.0
```

**关键参数**：
- flow(m³/h) | suction_pres(kPa 绝压) | vapor_pres(kPa 绝压) | density(kg/m³)
- suction_id(mm) | suction_len(m) | elevation(m, 正=液面在泵上)
- discharge_pres(kPaG) | npshr(m)

---

### 5. safety_valve — 安全阀喉径(API 520)

**功能**：基于 API 520 Part I 的安全阀喉径计算。支持气体/蒸气（临界流/亚临界流自动判断）、水蒸气、液体四种工况。输出所需喉径面积并推荐 API 标准喉径代号。

**调用方式**：
```bash
python modules/safety_valve/calc.py \
  --fluid gas --rate 5000 --unit kg/h --mw 92.14 \
  --k 1.13 --T 150 --Z 1.0 --pset 500 --pbp 50 --kd 0.975
```

**关键参数**：--fluid(gas/steam/liquid) | --rate(泄放量) | --unit(kg/h 或 m³/h)
- --pset(整定压力 kPaA) | --pbp(背压 kPaA) | --kd(泄放系数, 默认 0.975)
- 其他可选：--ovp(超压%, 默认10) | --kb(背压修正系数) | --kc(爆破片组合系数)

**API标准喉径代号**：D(71mm²) → T(16774mm²)，共14级

---

### 6. tank_breather — 储罐呼吸阀(API 2000)

**功能**：基于 API 2000 第7版的常压储罐呼吸量计算。计算热呼吸（呼出/吸入）和工作呼吸（呼出/吸入），合计总呼吸量，推荐呼吸阀规格。

**调用方式**：
```bash
# 闪点 <37.8°C 用 --flashpoint low，≥37.8°C 用 --flashpoint high
python modules/tank_breather/calc.py \
  --volume 1000 --flashpoint low --pump_in 50 --pump_out 50
```

**关键参数**：--volume(储罐容积m³) | --flashpoint(high/low, 闪点等级) | --pump_in(最大泵入量m³/h)
- --pump_out(最大泵出量m³/h)；可选 --insulated(保温) | --tank_diameter/--tank_height(火灾工况)

**关键区分**：闪点 ≥ 37.8°C → 热呼出系数 1.01（--flashpoint high）；闪点 < 37.8°C → 热呼出系数 1.69（--flashpoint low）

---

### 7. calc_report — 计算书生成

**功能**：将计算过程格式化为设计院风格计算书（Markdown/HTML），含输入条件、公式、分步过程、结果、标准依据。

**调用方式**：
```bash
python modules/calc_report/gen.py --title "管道压降计算书" --standard "Darcy-Weisbach" \
  --input params.json --output 计算书.md
```

**输入格式 (params.json)**：title | project | doc_no | standard | inputs[] | steps[] | conclusion

**典型用法**：执行计算模块后，将结果传递给本模块生成正式计算文件。例如管道压降计算完成后，把流速、Re、压降等结果填入 params.json 生成计算书。

---

### 8. data_table — 工程表格生成

**功能**：从结构化数据生成专业工程表格，支持五种表格类型。

**调用方式**：
```bash
# 对比表
python modules/data_table/gen.py --type comparison --input data.json --output result.md

# 参数汇总表
python modules/data_table/gen.py --type summary --data '...'

# 管径比选表（内置模板）
python modules/data_table/gen.py --type pipe-select --output result.md
```

**表格类型**：comparison(对比表) | summary(参数汇总) | material(材料表) | pipe-select(管径比选) | equipment-list(设备一览表)

---


### 9. control_valve — 控制阀口径(ISA 75.01.01)（v2.0 新增）

**功能**：基于 ISA 75.01.01 / IEC 60534 的控制阀口径计算。支持液体（Cv = Q√(Gf/ΔP)）与气体（含 Y 膨胀因子 + 阻塞流自动判断）两种工况。输出 Cv（US gpm）与 Kv（m³/h）。

**调用方式**：
```bash
# 液体
python modules/control_valve/calc.py --fluid liquid --q 500 --gf 0.9 --dp 10
# 气体（流量单位必须 scfh 或 nm3h）
python modules/control_valve/calc.py --fluid gas --q 5000 --qunit scfh --gg 0.62 \
  --p1 200 --p2 150 --t1 300 --k 1.4 --z 1.0 --xt 0.7
```

**关键参数**：
- --fluid(liquid/gas) | --q(流量) | --gf(液体比重) | --dp(液体压差 psi)
- --gg(气体比重) | --p1/--p2(阀前后压力 psia) | --t1(入口温度°F)
- --k(比热比) | --xt(极限压降比, 默认 0.7)

**要点**：
- 气体工况压降比 x ≥ Fk·xT 时自动判定**阻塞流**并用 xT 代 x
- 选型取 Cv 的 1.2~1.5 倍留裕量
- 不适用安全阀（走 `safety_valve` API 520）、不适用低温/浆料等需制造商降额的特殊工况

## 失败模式与反例（v2.1 新增）

### 失败模式与回退

- **结果异常（数量级离谱/负值/NaN）**：先查物性参数来源（密度/粘度/分子量是否对介质、是否表压绝压混用），再查公式参数单位——**先物性后公式**。
- **Re 处于过渡区（2300 < Re < 4000）**：Colebrook-White 不再可靠，输出时**必须标注过渡区不确定性**，建议设计裕量加大或改用实验关联式。
- **公式假设不满足**（如用不可压公式算高压气体）：明确输出警告，**不静默出数**；无法计算时明确说"此工况超出本工具适用范围"并指向适用边界表。
- **参数缺失**：用户未给的参数（如粗糙度、U 值）询问或声明默认值，不虚构。

### 交付前验证（计算结果必须交叉核对后才交付）

- **公式 ↔ 规范原文对照（v2.2.0 新增，源头验证层）**：交付前抽查关键公式（限流孔板/安全阀/压降等），对照**规范原文**（GB/T/HG/T/API 相应条款）核实公式形式与系数——**中间文档（Excel/计算书/脚本）可能有笔误，规范原文才是权威**；仅凭中间文档发现的问题只能标"可疑"，须规范原文确认后才定"错误"。用户无法提供规范原文时，结论标注置信度。
- 结果与手算/已知操作范围/厂商样本数据交叉核对，量级一致才交付；
- 单位自检：kPa vs psi、m³/h vs gpm、绝压 vs 表压——**单位错是计算事故第一来源**。

### ❌ 反例黑名单（踩过的坑，禁止重犯）

- ❌ 公称直径（DN100）当内径用——必须用内径（DN100 管内径约 106mm，随壁厚系列变化）
- ❌ 商业钢管粗糙度取 0（"光滑管"）——碳钢新管 0.046mm，旧管更大
- ❌ 运动/动力粘度混用——本工具箱粘度参数一律 cP（动力粘度）
- ❌ 用水的物性算烃类管线（或反之）——密度/粘度差一个数量级
- ❌ 过渡区 Re 不标注直接报数
- ❌ 表压/绝压混用——safety_valve 的 P1 是绝压(kPaA)，P2 是绝压(kPaA)，混用导致喉径错数倍
- ❌ 控制阀气体流量单位用错——必须是 scfh 或 nm3h，不是 kg/h

## 典型工作流

### 场景一：管道压降计算 + 出计算书

```
用户：帮我算一下这条管道的压降，内径100mm，水流量50m³/h，长100米，有5个弯头

→ 路由到 pipe_pressure_drop
→ 执行计算，输出 ΔP, v, Re, 流态
→ 用户：帮我生成计算书
→ 路由到 calc_report
→ 生成 管道压降计算书.md
```

### 场景二：换热器估算 + 泵NPSH + 表格对比

```
用户：我需要选一台换热器，热水10000kg/h从120°C冷到80°C，冷却水30°C进70°C出

→ 路由到 heat_exchanger
→ 计算出面积

用户：泵装在液面以上2米，帮我算NPSH够不够

→ 路由到 pump_npsh
→ 计算 NPSHa vs NPSHr

用户：把几种换热器方案做个对比表

→ 路由到 data_table
→ 生成 comparison 表格
```

---


### 场景三：控制阀选型（v2.0 新增）

```
用户：帮我算控制阀口径，水 500gpm，压差 10psi，比重 0.9

→ 路由到 control_valve
→ Cv=150, Kv=129.75，建议取 1.2~1.5 倍选标准阀
```

## 扩展指南 — 新增工艺计算模块

如需新增计算模块（如：精馏塔估算、搅拌器功率、火炬计算等），按以下三步操作：

### Step 1：创建模块脚本

在 `modules/` 下新建子目录和脚本：

```
modules/new_module/
└── calc.py        # 计算脚本，必须支持 --help 输出使用说明
```

**脚本规范**：
- 接受命令行参数（推荐 argparse）
- 输出结构化结果（数值 + 单位 + 判定结论）
- 必须支持 `--help` 输出参数说明
- 建议也支持 `--json` 输出模式（便于 calc_report 调用）

### Step 2：在 SKILL.md 模块路由表中注册

在模块路由表末尾添加一行：

```markdown
| 9 | `new_module` | 新模块功能简述 | "触发词1""触发词2""英文触发" | `modules/new_module/calc.py` |
```

### Step 3：添加子模块详细说明

在子模块说明区域添加调用方式和参数说明，格式与现有模块一致。

### 无需修改现有代码
所有模块独立运行，新增不影响已有模块。

## 维护记录

历史变更详见 `references/changelog.md`（v2.1.0 起卸载至此，正文只留索引）。
