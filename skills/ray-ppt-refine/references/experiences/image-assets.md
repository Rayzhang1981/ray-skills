# Image Assets Experiences — 配图/图像素材类

> 分类：配图来源、生图 prompt、图片核验、图片与文字的冲突。Step 4 配图执行前必读。

## LRN-20260818-001：批量配图填充右下留白四要点

**Date**: 2026-08-18
**Problem**: 给已有 deck 批量配图填充右下留白时的判断陷阱。
**Fix**: ①**"框底部≠视觉空白"**——文本框有高但文字短，判断留白要用**正文区行高估算器**（每 textbox：lines=ceil(len/cpl)，cpl=宽in*72/pt，used=lines*pt*1.45/72，取实际底边）；②**自适应落位**：y=正文底+0.18、h=min(1.45, 6.72-y)、w=h*3.4 右对齐 x=12.9-w、无空位(h<0.7)跳过、已有配图页跳过——一条脚本覆盖多页零重叠；③真正会空的只有 3-5 短条目内容页+双栏对照页，章节页(自带全幅背景)/表格/事件链不空，**别硬塞**；④**换图前必核验 Pexels 描述主题**（"construction worker"想当然标高处作业，实为货仓工人，被用户纠错）。
**Rule**: 配图决策链 + 行高估算器公式已收录进 refine-matrix.yaml 的 whitespace_detection。
**Status**: pending

## LRN-20260818-002：图库 16 种图铺 54 页必然相邻撞车

**Date**: 2026-08-18
**Problem**: P11/P14/P15 大量相邻重复（用户反馈）。
**Fix**: **去重策略 = ImageGen 按"相邻页主题差异"补图**（18 张 gen2_：权利/义务/气瓶/氨泄漏/火灾分类/压力表/报警/演练/低姿逃生/手套/护目镜/全身 PPE/职业健康检查/取样/触电急救/隐患报告/作业场所/废液处置），全部 VL 核验内容 + PIL 裁水印 8%×6% → 相邻重复 8→1 处（仅 P56-57 安全帽同主题可接受）。
**Rule**: 图库规模必须 ≥ 页数 / 3，否则必撞车；同一章内复用相近图是大忌。
**Status**: pending

## LRN-20260818-003：VL 模型核验配图内容的判定

**Date**: 2026-08-18
**Problem**: 脚本按关键词机械判匹配会误判（15 张误判 14 张）。
**Fix**: **"关键词不含≠内容不符"**——VL 描述是语义化句子，判定"跑偏"要看描述实质而非机械匹配关键词；"需图标对应文字"的主题图（火灾分类）prompt 要写具体可燃物（木/油/气/金属/电器/油锅）而非抽象符号；逃生类 prompt 3 次跑偏 → 第 3 次写"低姿匍匐+湿布捂口鼻+绿色光源"才成功，**越具体越好**。
**Rule**: VL 核验判定逻辑写进 refine_gate_check.py；prompt 写法规范进 design-languages 各 profile。
**Status**: pending

## LRN-20260819-001：ImageGen 写实人物图必须加 normal adult body proportions

**Date**: 2026-08-19
**Problem**: 裸 prompt 出"儿童穿大人装备"卡通比例（2.5-3 头身）概率高（full_ppe 首版翻车）。
**Fix**: ①**全身人物写实图必须加 `normal adult body proportions`**——加关键词后 6-6.5 头身可用；②**生图后必须 VL 核验人物比例**（问"比例是否正常/有无 AI 瑕疵"），不能只看主题匹配；③写实 prompt 模板 `realistic photo, professional photography, grayscale monochrome, sharp focus, vertical composition, no text, no watermark` 批量 35 张一次成图率高。
**Rule**: 已入 ray-ppt-ocr-eyes 生图主流程；refine 侧直接复用模板。
**Status**: resolved

## LRN-20260819-002：批量生成图替换后必须导出关键页预览 + VL 页面级核验

**Date**: 2026-08-19
**Problem**: 只做图片级 VL 核验，full_ppe 卡通比例图混入交付件。
**Fix**: **批量生成图全部替换后，必须导出关键页预览 + VL 核验"页面级"效果**（版式/压字/协调性）——本轮的 full_ppe 卡通比例就是预览页核验（P56）发现而非图片级核验发现；顺带修复 v4 遗留的 P56/P57 共用旧插画相邻重复。
**Rule**: refine_gate_check.py 的 page_level_vl_check 阶段必须包含。
**Status**: pending
