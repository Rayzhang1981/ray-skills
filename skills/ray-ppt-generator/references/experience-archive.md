# ray-ppt-generator 经验归档（resolved 条目，v3.15.0 从 SKILL.md 卸载）

> 按 LRN 状态机：resolved = 规则已入主流程/references，从正文缓冲区毕业，此处留档备查。
> 完整 changelog 见 `changelog.md`。

- 2026-08-16｜[LRN-20260816-002]｜场景：分片生成脚本｜教训：定义 p01-p22 后忘记在文件末尾调用 → 输出 0 页；每个 part 脚本必须有调用循环清单｜死路：无｜来源：RBPS培训PPT｜计数：1｜状态：resolved（p5/p6 均带调用循环验证通过）

- 2026-08-16｜[LRN-20260816-006]｜场景：大 deck 插入新页｜经验：追加→XML 重排 `prs.slides._sldIdLst`→按位置+正则重编号（footer 页码文本 `^\d{2} / \d+$`、标题栏编号方块位置 0.55/0.42 附近）三步走，避免全量重写｜死路：直接改每页 idx 参数（工作量大且易错）｜来源：RBPS培训PPT｜计数：4（90→95→89→93 四次迭代均用它）｜状态：resolved

- 2026-08-16｜[LRN-20260816-007]｜场景：90+ 页 deck 生成流水线｜经验：公共模块(rbps_common) + 分片生成(gen_p1..p6) + **链式 import 复用 prs**（p5 import p4、p6 import p5，模块顶层执行后取 .prs）+ reorder 定型｜死路：单脚本一次生成 90 页（脚本过长难维护）｜来源：RBPS培训PPT｜计数：3｜状态：resolved

- 2026-08-16｜[LRN-20260816-008]｜场景：横向对比高手版 PPT｜经验：同样任务（RBPS 90 页培训）的高手版揭示内容组织差距——每个要素按"定义→事故证据→行动标准→自检"四步闭环讲解，事故证据页用多起真实本土事故聚合（标题即教训+失效判断+能力要求），封面量化钩子、开场本土事故数据、收尾经济损失量化。已吸收为 doc-to-ppt.md「要素讲解四步闭环」模板｜死路：全盘照搬高手版版式（FREEFORM 手绘元素多，与 python-pptx 矩形体系不兼容）｜来源：RBPS高手版对比｜计数：1｜状态：resolved（模板已写入 doc-to-ppt.md）

- 2026-08-16｜[LRN-20260816-009]｜场景：高手作品对比方法｜经验：拆解"高手作品"三步——①shape 类型统计找视觉特征（FREEFORM 447 个/图 51 张/文本框 1252 个，一眼看出其手绘矢量路线）；②逐页文本 dump 找内容模板（事故证据页/行动标准页的固定结构）；③克制吸收方法论而非版式｜死路：只学视觉（FREEFORM 与 python-pptx 矩形体系不兼容）｜来源：RBPS高手版对比｜计数：1｜状态：resolved

- 2026-08-16｜[LRN-20260816-010]｜场景：页数收敛｜经验：**删页 = reorder 顺序表剔除索引**（不包含即可），不用改生成脚本；插页 = 顺序表插入。95→89（删 6 页）→93（插 4 页）全程零改 p1-p6 脚本｜死路：逐个改页面函数删页（工作量大）｜来源：RBPS培训PPT 页数迭代｜计数：2｜状态：resolved

- 2026-08-16｜[复发: LRN-001]｜场景：版式函数调用契约｜教训：v3.9 刚把"版式函数自带建页"写入主流程，p5 写 y01/y02/y05 又犯 3 次（先建页再调版式函数）——规则写入 ≠ 自动遵守，已在主流程补「生成前 grep 自查」钩子（v3.11）｜死路：无｜来源：RBPS培训PPT p5｜计数：3（复发）｜状态：resolved（grep 自查钩子已入主流程）

- 2026-08-27｜[LRN-20260827-001]｜场景：保格式就地改原 deck 文字（set_shape_text 段落越界）｜教训：`set_shape_text(shape, txt, para=1)` 对**段落数不足**的 shape 直接 IndexError——"para=0 写标题→clear_paragraphs(keep=1)→再写 para=1"必炸。正确姿势：para=0 写标题 → `clear_paragraphs(keep=1)` → **`add_para()` 追加**正文段落。另外跨脚本复用共享库时新常量漏 import 是高频 NameError 来源（`C_BODY2`），写完 import 块跑一次 `python -c "import 脚本"` 冒烟再执行｜死路：假设原 shape 与新内容段落数一致（双语/多级原文段落结构五花八门）｜来源：马来西亚新员工 EHS 课件 47 页扩充｜计数：2（NameError×1 + IndexError×1）｜状态：resolved（add_para 追加法已入 extend-deck.md）

- 2026-08-27｜[LRN-20260827-002]｜场景：纯文本模型（无多模态）的视觉 QA｜经验：当前模型读不了 PNG 时，视觉 QA 链路 = PowerShell COM `Slides.Item(n).Export(path,"PNG",1280,720)` 导出（首次调用看似无输出，实为已导出，ls 验证即可）→ `ray-ppt-ocr-eyes` 逐页 OCR+VL 描述确认布局（无溢出/重叠/风格一致）。**路径必须 Windows 格式 `E:\\...`**——Git Bash `/e/...` 路径 Python 不认（报找不到文件）｜死路：给纯文本模型直接 Read PNG（模型层报"不支持读图"）；bash 循环传 `/e/` 路径（脚本层报找不到文件）｜来源：马来西亚新员工 EHS 课件 47 页扩充（23 张新增页逐页视觉验证）｜计数：2（模型层+路径层各 1）｜状态：resolved（链路已入 extend-deck.md QA 节）

- 2026-08-27｜[LRN-20260827-003]｜场景：已有 deck 扩充的页序管理｜经验：新页 `add_slide` 追加在尾部 → 收集 `orig[:i] + new_pages + orig[i:]` 顺序表 → `reorder_slides`（重建 sldIdLst，按 slide._element 映射）一次定型。比逐页 move_slide 可靠（move 依赖 rId 查找易错）。原页英文化等就地修改在 add 新页**之前**做，避免索引漂移｜死路：逐页 move_slide（本会话曾因此失败重写为 reorder）；边插页边按旧索引引用原页（插页后索引全变）｜来源：马来西亚新员工 EHS 课件 47 页扩充｜计数：1｜状态：resolved（reorder_slides 代码已入 extend-deck.md）

- 2026-09-02｜[LRN-20260902-001]｜场景：EHS 课件连续插页（OSHA 页 7→8、SOP 页 27→28，两次同套路）｜经验：建页脚本**模板化**——`add_rect/add_text/add_badge/build_X_card` + `add_slide` 尾部追加 + `reorder_slides` 一次定型，插页任务只需换内容与插入位置（`orig[:n] + [new] + orig[n:]`）。第一次手写全套，第二次复制骨架改内容即用，全程零返工｜死路：每次从零写建页脚本（重复劳动）；先插页再改原页（索引漂移）｜来源：EHS 课件 OSHA/SOP 插页｜计数：1｜状态：resolved（骨架脚本 E:\LingXi\2026-09-01-EHS培训英译中\build_osha_page.py 可作模板）
