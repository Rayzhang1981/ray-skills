# Crowl 4e 增量详情 — ray-chem-compat（CRW 使用边界与 CHETAH 定位）

> 来源：Crowl & Louvar《Chemical Process Safety: Fundamentals with Applications》4th ed. §8-3「化学相容性」；页位＝该书 PDF 页（可 `===== PDFPAGE N =====` 回查）。
> 提取文本：`sessions\2026-10-06-crowl-distil\_process\src_ch08-09.txt`。
> 骨架归属：`skeleton-ch08-09.md` **M2 化学相容性矩阵与 CRW 预测（Table 8-5/8-6）**，§四判 **"重复"** —— 理由：**本 skill 的 CRW/NOAA 基团规则库已是 L1 判定层**。
> ⇒ **本批不重抄矩阵方法论，只取真增量**（使用边界 / 工具定位 / 源谱系 / 一条须标注的作者观点）。
> 建立：2026-10-06｜功易安｜Fold-in 批：Crowl 4e → ray-chem-compat

---

## 0 定位：为什么"重复"条目仍值得落

本 skill 的判定引擎＝**CRW／NOAA 基团规则库（L1 判定层）**。教材该条给的**不是另一套判定方法**，而是**围绕该引擎的四类"元信息"**：

| # | 增量 | 为什么对本 skill 有价值 |
|---|---|---|
| 1 | **三条 CRW 使用边界判据**（教材原话） | 直接约束"**L1 结果能不能直接当结论、怎么用**" |
| 2 | **CHETAH 的定位**（初筛，非判定） | 给"多源工具谱系"补一个**明确定位**的成员 |
| 3 | **信息源谱系 Table 8-6（8 源）** | 本 skill 的 L2/L3 兜底之外，还缺**哪些非 CRW 通道**可核 |
| 4 | 一条**须标注"作者观点"**的论断 | 防"把教材论断当定论"的误用 |

---

## 1 三条 CRW 使用边界判据（教材原话，逐条可回查）

### 判据 ① CRW 偏保守 ⇒ 结果必须"谨慎解读"

> "**Because the CRW tends to be conservative in its predictions of binary interactions, the results must be carefully interpreted.**"（PDFPAGE 225）

**判据化**：CRW 的二元相互作用预测**系统性偏保守**（会把"实际不反应/反应不剧烈"的组合也判成需注意）⇒ **不得把 CRW 的 `N`（不相容）当作"一定出事"**，而是"**按此管理、并把解读成本写进交付说明**"；反过来，CRW 判 `Y` **不能推翻**现场证据。

### 判据 ② CRW 只给**常温常压**相容性 ⇒ 异温异压外推须小心

> "**Also, the CRW program provides chemical compatibility information only at room temperature and pressure; thus, care must be taken in applying CRW results at different temperatures and pressures.**"（PDFPAGE 225）

**判据化（本条最易被违反）**：CRW 的适用域＝**室温 + 常压**。
⚠️ **凡工艺条件偏离常温常压**（加热/冷冻/加压/真空/汽化），**必须显式声明"CRW 结果系外推"**，并回 L2\L3 证据层（含 SDS 的"禁配物/危险反应"段、Bretherick's）或做专门评估——**不得把常温结论直接搬进高温高压工况**。
**与本 skill 的关系**：本 skill 的"**温度依赖**"判据（若有具体温度阈值**一律回 出处源取、不在此复述**）与此条同源；教材在此只给**适用域声明**，不给阈值。

### 判据 ③ **水必须入列**

> Example 8-1 解题注：**"Note that water must also be included since the sulfuric acid is aqueous."**（PDFPAGE 226／§8 例题区）

**判据化**：**水（及水溶液载体）是相容性矩阵的必列成员**——酸性/碱性水溶液、含水物料、以及工艺中可能引入的水（清洗、蒸汽、冷却水泄漏）都可能构成反应路径；**漏掉水＝漏掉一整类情景**（遇水放热/放气、稀释热、酸雾、腐蚀耦合）。
**与本 skill 的关系**：本 skill 的矩阵构建规则中**水/介质归属**是输入侧前置；本条把"必列"上升为**判据**（而非操作习惯）。

---

## 2 CHETAH 定位：初筛工具，不是判定工具

> "Another source of information on reactive chemicals is a program called **CHETAH (Chemical Thermodynamics and Energy Release Evaluation)**. This program is able to predict the reactive chemical hazards using **heats of formation, Gibbs energy, and functional groups**. CHETAH was originally developed by **Dow Chemical** and is **very useful as an initial screening tool** for reactive chemical hazards."（PDFPAGE 226）

**判据化**：
- **方法学**：以**生成热 / Gibbs 能 / 官能团法**做**反应性危害预测**（热力学倾向 + 官能团经验）；
- **定位（教材原话）＝ "initial screening tool"（初筛工具）** ⇒ **不是判定工具**：其输出用于**决定"要不要进一步查/测"**，**不得当作相容性结论**（本 skill 的 `Y/N/C/X/SR` 判定**不引 CHETAH**）；
- **源**：原由 **Dow Chemical** 开发，现由 **ASTM** 提供（见 §3）。

---

## 3 信息源谱系（**Table 8-6**，只登记表号 + 页码 + 一句话）

> **Table 8-6「Sources of Information on Chemical Reactivity Hazards」**（教材 PDFPAGE 226，"另见 §8-3 前文 p225"）：**共 8 源**——① 企业自有数据库；② **SDS**（厂商/网上）；③ **CRW**（NOAA/EPA/CCPS 免费）；④ **Bretherick's Handbook of Reactive Chemical Hazards, 8th ed.**（Urben 编，2017）；⑤ **Sax's Dangerous Properties of Industrial Materials, 12th ed.**（Lewis 编，2012）；⑥ Sigma-Aldrich 化学品安全数据库（Lenga 编，1988）；⑦ **NFPA Fire Protection Guide to Hazardous Materials**（2010）；⑧ **CHETAH**（ASTM）。
> ⚠️ **本表只登记"有哪几源、各在谁家"，URL/版次细节不复制**——用前回原书该页；**数值/条目一律不抄**（本 skill 数值纪律）。

**判据化**：CRW **不是唯一通道**——**Bretherick's / Sax's / NFPA** 三条"非 CRW 通道"是本 skill L2 兜底（CAMEO/Bretherick/危险化学品全书）之外**可补的核验面**；当 CRW 判 `?`/不确定时，**优先按此表换通道核**，而不是硬判。

---

## 4 须标注"作者观点"的论断（⚠️ 不得当定论）

教材论断（p225 附近，M2 骨架摘录）："**二元全部识别后，多元组合新增危害不太可能**"（大意：多化学品组合虽会出现在应急情形，但逐一识别二元相互作用后，多元组合带来的**新增**危害**不太可能**发生）。

**本 skill 的处置（并列留痕、不代裁）**：
- **这是教材（作者）观点，不是实验结论**——教材**未给**支撑该论断的实证或边界条件；
- ⇒ **采用时应保守**：**不得**据此**省略**多元/同室组合的专门评估（尤其**催化剂/引发剂/微量杂质**参与、**温度压力偏离常温常压**、**延迟混合**三类情形）；
- ⇒ 若客户/审查依赖此论断，**须显式标注"教材作者观点、建议保守处理"**，并说明本 skill 的 L1（二元规则库）**不覆盖三元及以上交互**这一事实边界。

---

## 5 验证留痕（本批）

- **反编造回查（源文本逐句命中）**：
  - 判据①原句 → `src_ch08-09.txt` L352–353；
  - 判据②原句 → L353–355；
  - 判据③（水必须入列）→ L1303；
  - CHETAH 段 → L396–399；
  - Table 8-6 标题与八源 → L360–394。
- **公式两道自检：本条不含公式**（判据/定位类）⇒ 量纲/回代 **N/A**；本批**未触及**本工程已实证的"PDF 文字层系统性丢符号"（**无式可丢**）。
- **与既有重叠的处理（只写指针、不铺陈）**：矩阵构建与判定链 → 本 skill 正文（**L1 CRW/NOAA 规则库**）；L2/L3 兜底 → `references/` 既有册；**本批不重述** `Y/N/C/X/SR` 判定术、半矩阵契约、交付三件套。
- **不进 skill 的内容**：Table 8-5 的矩阵内容（CRW4.02 输出）、Table 8-6 的 URL 与版次细节、Example 8-1 的四化学品判读结果（**只取其"水必须入列"这一条判据**）。
