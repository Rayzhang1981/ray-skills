# 已有 Deck 扩充模式（2026-08-27 实战沉淀：23 页 → 47 页 EHS 课件）

> 场景：用户给了**已有 PPTX**，要加新模块/新页、改部分文字，且**保持原格式风格一致**。
> 触发语："以这份 PPT 为底""在这个课件基础上扩充""保持原格式/风格"。
> **不要从零重造**——原 deck 的字体/色板/装饰细节很难完全复刻，且重造工作量大、必然走样。

## 流程总览（五步）

```
1. 摸底     → dump 原 deck 样式（颜色/字体/画布尺寸/版式坐标/形状命名规律）
2. 建共享库 → build_lib.py（色板常量 + add_rect/add_text/add_title 等助手 + reorder_slides）
3. 分片构建 → build_part1.py（改原页+建新页→中间产物）/ build_part2.py（打开中间产物继续→最终文件）
4. 机械 QA  → 页数 / 每页标题清单 / CJK 或乱码扫描 / 备注覆盖 / 议程表全文核对
5. 视觉 QA  → COM 导 PNG → **先 Read 试原生看图**（2026-09 起主流模型已原生多模态）→ 读不了图才走 ray-ppt-ocr-eyes（VL 描述）逐页确认
```

## 第 1 步：摸底（动手前必做）

用 python-pptx dump 原 deck 的完整样式，写成一个 `dump_style.py`：

- 画布尺寸：`prs.slide_width / slide_height`（EMU，÷914400 得英寸）
- 每页每个 shape：名称（命名规律如 `AutoShape N`）、位置尺寸、填充色、字体、字号、颜色
- 主题色：从高频填充色归纳出色板常量（`C_TITLE / C_BODY / C_GREEN ...`）
- 版式规律：标题栏坐标、正文起始 y、页脚位置、装饰元素（角部圆等）的复用模式

> 实战：马来西亚 EHS 课件项目用 `dump_layout.py / dump_shapes.py / dump_colors.py` 三个脚本完成摸底，
> 摸清"Poppins 标题 + Noto Sans SC 正文 + 16:9 + #F5F5F5 章节页 + 角部装饰圆"后才动手。

## 第 2 步：共享库（build_lib.py 核心函数）

```python
# -*- coding: utf-8 -*-
"""共享样式助手——常量从原 deck 摸底结果归纳"""
import copy
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn

C_TITLE = RGBColor(0x33, 0x33, 0x33)   # ← 从原 deck 提取
C_BODY  = RGBColor(0x52, 0x52, 0x52)
F_HEAD  = "Poppins"                     # ← 原 deck 标题字体
F_BODY  = "Noto Sans SC"                # ← 原 deck 正文字体

def _set_eastasia(run, font_name):
    """CJK 字体必须同时设 eastAsia，否则中文回落宋体"""
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn('a:ea'))
    if ea is None:
        ea = rPr.makeelement(qn('a:ea'), {})
        rPr.append(ea)
    ea.set('typeface', font_name)

def set_shape_text(shape, text, size=None, bold=None, color=None, font=None,
                   para=0, keep_runs=1):
    """替换某段文字并保留原 run 的 rPr（字体/颜色/字号随原样式）。
    ⚠️ 段落越界坑见下文「保格式改文字」。"""
    tf = shape.text_frame
    p = tf.paragraphs[para]
    if p.runs:
        r0 = p.runs[0]
        r0.text = text
        for r in p.runs[1:]:
            r._r.getparent().remove(r._r)
    else:
        r0 = p.add_run()
        r0.text = text
    if size  is not None: r0.font.size = Pt(size)
    if bold  is not None: r0.font.bold = bold
    if color is not None: r0.font.color.rgb = color
    if font  is not None:
        r0.font.name = font
        _set_eastasia(r0, font)
    return r0

def add_para(shape, text, size=None, bold=None, color=None, font=None):
    """向已有 shape 追加一个段落（正文多段时用）"""
    p = shape.text_frame.add_paragraph()
    r = p.add_run()
    r.text = text
    if size  is not None: r.font.size = Pt(size)
    if bold  is not None: r.font.bold = bold
    if color is not None: r.font.color.rgb = color
    if font  is not None:
        r.font.name = font
        _set_eastasia(r, font)
    return p

def clear_paragraphs(shape, keep=1):
    tf = shape.text_frame
    while len(tf.paragraphs) > keep:
        p = tf.paragraphs[-1]
        p._p.getparent().remove(p._p)

def set_notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text

def reorder_slides(prs, order):
    """重建 sldIdLst 使 slides 按 order（slide 对象列表）排列。
    比逐页 move_slide 可靠——move 依赖 rId 反查容易失败。"""
    sldIdLst = prs.slides._sldIdLst
    ids = list(sldIdLst)
    el2id = {}
    for sldId in ids:
        try:
            rid = sldId.rId
        except Exception:
            rid = sldId.get(qn('r:id'))
        if rid is None:
            continue
        rel = prs.part.rels[rid]
        el2id[rel.target_part._element] = sldId
    for sldId in el2id.values():
        sldIdLst.remove(sldId)
    for s in order:
        if s._element in el2id:
            sldIdLst.append(el2id[s._element])
    return len(order)
```

`add_rect / add_text / add_title / add_subtitle / add_table` 等助手按原 deck 版式封装
（坐标取摸底得到的规律值，如标题栏固定 `(0.83, 0.56, 11.67, 0.83)`）。

## 第 3 步：保格式改文字（最高频坑，2026-08-27 实测炸 2 次）

**坑 1：段落越界 IndexError。** 原 shape 段落数不足时 `set_shape_text(shape, txt, para=1)` 直接崩。
双语/多级原文的段落结构五花八门，**不要假设段落数**。

```python
# ❌ 错误：假设 shape 有 2 段（原 shape 只有 1 段 → IndexError）
set_shape_text(sh, title_txt, para=0, bold=True)
set_shape_text(sh, body_txt, para=1)          # ← 崩

# ✅ 正确：para=0 写标题 → 清到 1 段 → add_para 追加正文
set_shape_text(sh, title_txt, para=0, bold=True)
clear_paragraphs(sh, keep=1)
add_para(sh, body_txt, size=12, color=C_BODY, font=F_BODY)
```

**坑 2：共享库新常量漏 import。** part 脚本 `from build_lib import (...)` 列表漏了某常量
→ 运行时 NameError。防御：改完 import 块先冒烟 `python -c "import build_part2"` 再正式跑。

**坑 3：QA 脚本默认路径。** QA 脚本常把默认路径写成中间产物——跑最终文件**必须传参**，
否则对着旧文件 QA 全绿、真文件没查（本会话实测发生过）。

## 第 4 步：新页构建 + 页序收口

```python
prs = Presentation(SRC)
orig = list(prs.slides)          # 先快照原页（就地修改在 add 新页之前做，避免索引漂移）

# --- 就地修改原页（此时索引还是原始的） ---
s3 = prs.slides[3]
sh = find_by_name(s3, "AutoShape 6")
set_shape_text(sh, "English text ...", size=15, color=C_MID)

# --- 构建新页（add_slide 都追加在尾部）---
m6_pages = build_m6()            # 内部用 prs.slides.add_slide(...)，返回页对象列表
fa_pages = build_flame()

# --- 顺序表收口：原页段 + 新页段交错拼出最终顺序 ---
final = (orig[:28] + m6_pages + orig[28:31] + fa_pages + orig[31:] )
reorder_slides(prs, final)       # 一次重排定型
prs.save(OUT)
```

要点：
- **先改原页、后加新页**——add_slide 会让 `prs.slides` 索引漂移
- 新页建在尾部不着急挪，最后用顺序表一次性重排
- 中间产物链：part1 输出 `中间.pptx` → part2 打开它继续（避免单脚本过长）

## 第 5 步：QA（机械 + 视觉双层）

**机械 QA**（`qa_deep.py`，一次写好反复用）：
1. 页数断言（如 `== 47`）
2. 每页标题清单（人眼扫页序）
3. CJK / U+FFFD 全文扫描（shapes + tables + notes 三处；允许的对照页加白名单）
4. 备注覆盖率（`notes_slide.notes_text_frame.text.strip()` 非空计数）
5. 关键页全文打印（目录/议程表逐行核对时间轴）

**视觉 QA**（读不了图时的降级链路，2026-08-27 实战验证；**2026-09 起优先直接 Read 原生看图**）：

```powershell
# PowerShell COM 导出关键页 PNG（注意：首次调用可能看似无输出，实为已导出，ls 验证）
$pres = $pp.Presentations.Open("E:\...\final.pptx", 0, 0, 0)
$pres.Slides.Item(35).Export("E:\...\_render\S35.png", "PNG", 1280, 720)
```

```bash
# 视觉 QA：先 Read 试原生看图；读不了图（报 does not support reading images）才走 ray-ppt-ocr-eyes（VL 描述布局：溢出/重叠/风格）
# ⚠️ 路径必须 Windows 格式，Git Bash 的 /e/... Python 不认
PY="~/.workbuddy/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
"$PY" "~/.workbuddy/.workbuddy/skills/ray-ppt-ocr-eyes/scripts/ocr_eyes.py" \
      "E:\\LingXi\\...\\_render\\S35.png" --provider opencode-go
```

逐页读 VL 描述确认：无文字溢出、无元素重叠、风格与原 deck 一致（"扁平化商务风格"等描述吻合）。

## 与其他模式的边界

| 模式 | 输入 | 本文档职责 |
|---|---|---|
| 从头生成 | 主题 / 资料 | 不适用（走 SKILL.md 主流程 / doc-to-ppt.md） |
| **扩充** | **已有 PPTX + 扩充需求** | **本文档** |
| 深度美化 | 任意已有 PPTX | ray-ppt-refine（改排版不改内容结构） |
