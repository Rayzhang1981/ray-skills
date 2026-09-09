# 代码模板库（按需加载，勿全量载入上下文）

> 使用规则：生成 PPTX 时按需**复制粘贴**对应函数到脚本，改参数即可。所有函数基于 python-pptx，页面尺寸统一 `13.333" × 7.5"`（16:9）。

## 0. 环境与公共辅助函数

```python
# -*- coding: utf-8 -*-
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

PRS_WIDTH = Inches(13.333)
PRS_HEIGHT = Inches(7.5)

# === 颜色 ===
SAFE_BLUE    = RGBColor(0x00, 0x52, 0x93)  # 主色：安全蓝
ACCENT_ORANGE = RGBColor(0xE6, 0x7E, 0x22) # 强调色：警示橙
DARK_TEXT    = RGBColor(0x2C, 0x3E, 0x50)  # 正文：深灰蓝
WHITE        = RGBColor(0xFF, 0xFF, 0xFF)
LIGHT_BG     = RGBColor(0xF8, 0xF9, 0xFA)
RED          = RGBColor(0xC0, 0x39, 0x2B)
GREEN        = RGBColor(0x27, 0xAE, 0x60)
WARN_BG      = RGBColor(0xFD, 0xED, 0xEC)
WARN_BORDER  = RGBColor(0xE7, 0x4C, 0x3C)
# === 五级灰阶文字（v3.4 新增）——比单一正文色更有层次 ===
TEXT_MAIN   = RGBColor(0x20, 0x2B, 0x36)  # ①正文
TEXT_BODY   = RGBColor(0x2C, 0x3E, 0x50)  # ②正文（=DARK_TEXT）
TEXT_SUB    = RGBColor(0x5E, 0x6E, 0x80)  # ③次要
TEXT_MUTED  = RGBColor(0x8A, 0x99, 0xA8)  # ④弱化（来源/标注）
TEXT_FAINT  = RGBColor(0xC7, 0xD2, 0xDE)  # ⑤最弱（页标签/深底上的弱字）

def set_fill(shape, color):
    shape.fill.solid()
    shape.fill.fore_color.rgb = color

def set_font(run, name='Microsoft YaHei', size=Pt(14), bold=False, color=DARK_TEXT):
    run.font.name = name
    run.font.size = size
    run.font.bold = bold
    run.font.color.rgb = color

def add_text(slide, text, x, y, w, h, size=Pt(14), bold=False, color=None, align='left'):
    """添加文字（自动换行 + 自动字体）——所有文本框必须 word_wrap=True 防中文溢出"""
    if color is None:
        color = DARK_TEXT
    box = slide.shapes.add_textbox(x, y, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = text
    set_font(p.runs[0], size=size, bold=bold, color=color)
    if align == 'center':
        p.alignment = PP_ALIGN.CENTER
    return box

def add_title_bar(slide, title, subtitle="", tag="", num="", chapter=""):
    """标题栏 v2（2026-09-04 事故制度 deck 实战升级）：三件套页眉。
    - num: 橙色圆角编号徽章（如 "04"），制度/规程类课件编号感强
    - chapter: 页眉右上角章节名（如 "模块二 · 分级与时限"），听众随时知道讲到哪
    - tag: 右下角条款定位小字（如 "制度 §5.2 / 附录3"）
    注意：chapter 放在色带顶部 9.5pt（不与标题抢层级），tag 在色带底部右侧。"""
    BAND_H = Inches(1.35)
    shape = slide.shapes.add_shape(1, 0, 0, PRS_WIDTH, BAND_H)
    shape.fill.solid(); shape.fill.fore_color.rgb = SAFE_BLUE
    shape.line.fill.background()
    # 页眉行：左=系列名，右=章节名
    add_text(slide, "公司名 · 安全教育培训系列", Inches(0.7), Inches(0.09),
             Inches(5.5), Inches(0.26), size=Pt(9), color=RGBColor(0x8F,0xB3,0xD4))
    if chapter:
        add_text(slide, chapter, PRS_WIDTH - Inches(5.2), Inches(0.08),
                 Inches(4.5), Inches(0.28), size=Pt(9.5), bold=True,
                 color=GOLD, align='right')
    # 编号徽章
    tx = Inches(0.7)
    if num:
        nb = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7),
                                    Inches(0.46), Inches(0.72), Inches(0.62))
        nb.fill.solid(); nb.fill.fore_color.rgb = ACCENT_ORANGE
        nb.line.fill.background()
        tfn = nb.text_frame; tfn.word_wrap = False
        tfn.margin_left=0; tfn.margin_right=0; tfn.margin_top=0; tfn.margin_bottom=0
        tfn.vertical_anchor = MSO_ANCHOR.MIDDLE
        pn = tfn.paragraphs[0]; pn.text = num; pn.alignment = PP_ALIGN.CENTER
        set_font(pn.runs[0], size=Pt(22), bold=True, color=WHITE)
        tx = Inches(1.66)
    tb = slide.shapes.add_textbox(tx, Inches(0.42), PRS_WIDTH - tx - Inches(0.55), Inches(0.6))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = title
    set_font(p.runs[0], size=Pt(26), bold=True, color=WHITE)
    if subtitle:
        p2 = tf.add_paragraph(); p2.text = subtitle
        set_font(p2.runs[0], size=Pt(12.5), color=RGBColor(0xC9,0xDC,0xEE))
    if tag:
        tg = slide.shapes.add_textbox(PRS_WIDTH - Inches(5.2), Inches(1.02),
                                      Inches(4.5), Inches(0.28))
        ttf = tg.text_frame; ttf.word_wrap = False
        tp = ttf.paragraphs[0]; tp.text = tag
        set_font(tp.runs[0], size=Pt(10), color=RGBColor(0xC7,0xD2,0xDE))
        tp.alignment = PP_ALIGN.RIGHT

def add_source_note(slide, text, colors=None, x=Inches(0.7), y=None, w=Inches(11.9)):
    """数据来源标注（v3.4 新增）：技术/学术课件数据页底部一行 9.5pt 灰色来源说明。
    例：'数据来源：GB 51283—2020 条文说明' / '上海化工研究院检测中心'。
    默认放在页脚上方；可用 x/y/w 覆盖位置。"""
    if y is None:
        y = PRS_HEIGHT - Inches(0.72)
    color = RGBColor(0x8A, 0x99, 0xA8)  # 弱灰（五级灰阶第4级）
    tb = slide.shapes.add_textbox(x, y, w, Inches(0.32))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = text
    set_font(p.runs[0], size=Pt(9.5), color=color)
    p.alignment = PP_ALIGN.LEFT

def add_footer(slide, page_num, total=25, company="公司名称", reg_no=None):
    """页脚 v2：左下建议放制度/文件编号（reg_no）而非公司名——编号对听课者更有用，
    也满足"培训可追溯"审计要求。深底页传浅色文字。"""
    left_txt = reg_no or company
    t1 = slide.shapes.add_textbox(Inches(0.7), PRS_HEIGHT - Inches(0.40), Inches(6.5), Inches(0.3))
    tf1 = t1.text_frame; tf1.word_wrap = False
    p1 = tf1.paragraphs[0]; p1.text = left_txt
    set_font(p1.runs[0], size=Pt(8.5), color=RGBColor(0x8B, 0x9A, 0xA9))
    p1.alignment = PP_ALIGN.LEFT
    t2 = slide.shapes.add_textbox(PRS_WIDTH - Inches(2.0), PRS_HEIGHT - Inches(0.40), Inches(1.3), Inches(0.3))
    tf2 = t2.text_frame; tf2.word_wrap = False
    p2 = tf2.paragraphs[0]; p2.text = "%02d / %02d" % (page_num, total)
    set_font(p2.runs[0], size=Pt(9), color=RGBColor(0x8B, 0x9A, 0xA9))
    p2.alignment = PP_ALIGN.RIGHT


def chip(slide, text, x, y, w, h, fill, size=Pt(13.5), bold=True, color=WHITE):
    """圆角标签块（chip）：文字水平垂直居中的圆角矩形，万能构件。
    用途：范围标签/步骤徽章/站名/图例/矩阵卡片头——凡"色块+居中短词"都用它。"""
    c = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    c.fill.solid(); c.fill.fore_color.rgb = fill; c.line.fill.background()
    tf = c.text_frame; tf.word_wrap = False
    tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = text; p.alignment = PP_ALIGN.CENTER
    set_font(p.runs[0], size=size, bold=bold, color=color)
    return c


def num_circle(slide, n, x, y, d, fill, size=Pt(14), color=WHITE):
    """数字圆点：步骤编号/列表序号。d 为直径（Emu）。"""
    c = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, y, d, d)
    c.fill.solid(); c.fill.fore_color.rgb = fill; c.line.fill.background()
    tf = c.text_frame; tf.word_wrap = False
    tf.margin_left=0; tf.margin_right=0; tf.margin_top=0; tf.margin_bottom=0
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    p = tf.paragraphs[0]; p.text = str(n); p.alignment = PP_ALIGN.CENTER
    set_font(p.runs[0], size=size, bold=True, color=color)
    return c


def ribbon(slide, y, h):
    """底部渐变彩带：四色段（绿→黄→橙→蓝）横贯页底，封面/结束页收尾装饰。
    颜色按主题替换；段宽均分，总宽=页宽。"""
    from pptx.enum.shapes import MSO_SHAPE as _SHP
    cols = [RGBColor(0x2A,0x9D,0x8F), RGBColor(0xE9,0xC4,0x6A),
            RGBColor(0xE7,0x6F,0x51), RGBColor(0x3E,0x7C,0xB8)]
    seg = int(PRS_WIDTH / 4)
    for i, c in enumerate(cols):
        x = i * seg
        w = seg if i < 3 else (PRS_WIDTH - 3 * seg)
        r = slide.shapes.add_shape(_SHP.RECTANGLE, x, y, w, h)
        r.fill.solid(); r.fill.fore_color.rgb = c; r.line.fill.background()

def add_speaker_notes(slide, notes_text):
    """为幻灯片添加演讲者备注（逐字稿）"""
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.text = notes_text

def add_top_accent_bar(slide, colors):
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, Inches(0.12))
    set_fill(bar, colors['primary']); bar.line.fill.background()

def add_decorative_circles(slide, colors):
    c1 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(10.5), Inches(-1), Inches(4), Inches(4))
    set_fill(c1, colors['secondary']); c1.line.fill.background()
    c2 = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(-1), Inches(5.5), Inches(3), Inches(3))
    set_fill(c2, colors['secondary']); c2.line.fill.background()
```

## 1. 配色方案库 PALETTES

```python
PALETTES = {
    'navy-executive': {
        'name': '商务深蓝', 'primary': (30,39,97), 'secondary': (202,220,252),
        'accent': (255,255,255), 'bg': (255,255,255), 'text': (30,39,97), 'text_light': (107,114,128)
    },
    'tech-dark': {
        'name': '科技深空', 'primary': (13,17,23), 'secondary': (88,166,255),
        'accent': (255,255,255), 'bg': (22,27,34), 'text': (240,246,252), 'text_light': (139,148,158)
    },
    'ocean-gradient': {
        'name': '海洋渐变', 'primary': (6,90,130), 'secondary': (28,114,147),
        'accent': (255,255,255), 'bg': (255,255,255), 'text': (6,90,130), 'text_light': (107,114,128)
    },
    'teal-trust': {
        'name': '青绿信任', 'primary': (2,128,144), 'secondary': (0,168,150),
        'accent': (2,195,154), 'bg': (255,255,255), 'text': (6,90,96), 'text_light': (55,65,81)
    },
    'warm-terracotta': {
        'name': '暖陶简约', 'primary': (184,80,66), 'secondary': (231,232,209),
        'accent': (167,190,174), 'bg': (253,251,247), 'text': (61,61,61), 'text_light': (107,114,128)
    },
    'charcoal-minimal': {
        'name': '炭灰极简', 'primary': (54,69,79), 'secondary': (242,242,242),
        'accent': (33,33,33), 'bg': (255,255,255), 'text': (54,69,79), 'text_light': (139,148,158)
    },
}
```

## 2. 页面类型模板函数（12 种）

### 2.1 封面页

```python
def add_cover_slide(prs, title, subtitle, colors, layout):
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['primary']); bg.line.fill.background()
    for cx, cy, cr in [(Inches(9.5), Inches(-1.5), 5), (Inches(-1), Inches(5), 4)]:
        dec = slide.shapes.add_shape(MSO_SHAPE.OVAL, cx, cy, Inches(cr), Inches(cr))
        set_fill(dec, colors['secondary']); dec.line.fill.background()
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(2.5), Inches(11.5), Inches(1.5))
    tf = tb.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = title; p.alignment = PP_ALIGN.CENTER
    set_font(p.runs[0], size=Pt(48), bold=True, color=colors['accent'])
    if subtitle:
        stb = slide.shapes.add_textbox(Inches(0.8), Inches(4.2), Inches(11.5), Inches(0.8))
        tf2 = stb.text_frame; p2 = tf2.paragraphs[0]
        p2.text = subtitle; p2.alignment = PP_ALIGN.CENTER
        set_font(p2.runs[0], size=Pt(20), color=colors['secondary'])
```

### 2.2 目录页

```python
def add_toc_slide(prs, items, colors, layout):
    """items: list of (编号, 标题, 描述) 三元组"""
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['bg']); bg.line.fill.background()
    add_text(slide, "目录", Inches(0.8), Inches(0.4), Inches(5), Inches(0.8),
             Pt(36), True, colors['primary'])
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.4), Inches(0.08), Inches(5.5))
    set_fill(bar, colors['primary']); bar.line.fill.background()
    for i, (num, title, desc) in enumerate(items):
        y = Inches(1.6) + int(i) * Inches(1.1)
        add_text(slide, num, Inches(1.2), y, Inches(0.6), Inches(0.5), Pt(24), True, colors['secondary'])
        add_text(slide, title, Inches(2.0), y, Inches(4.5), Inches(0.5), Pt(18), True, colors['text'])
        add_text(slide, desc, Inches(2.0), y + Inches(0.4), Inches(9), Inches(0.4), Pt(12), False, colors['text_light'])
```

### 2.3 数据卡片页（核心数字）

```python
def add_big_number_page(prs, title, numbers, colors, layout):
    """numbers: list of (value, label) — 每行 3 张卡片最佳"""
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['bg']); bg.line.fill.background()
    add_text(slide, title, Inches(0.8), Inches(0.4), Inches(6), Inches(0.8), Pt(32), True, colors['primary'])
    card_w, card_h = Inches(3.5), Inches(2.5)
    start_x, start_y, gap = Inches(0.8), Inches(2.2), Inches(0.5)
    for i, (value, label) in enumerate(numbers):
        x = start_x + int(i) * (card_w + gap)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, start_y, card_w, card_h)
        set_fill(card, colors['primary']); card.line.fill.background()
        add_text(slide, value, x, start_y + Inches(0.5), card_w, Inches(1), Pt(44), True, colors['accent'], 'center')
        add_text(slide, label, x, start_y + Inches(1.7), card_w, Inches(0.5), Pt(14), False, colors['secondary'], 'center')
```

### 2.4 内容页（左图标条 + 右文字）

```python
def add_content_slide(prs, title, items, colors, layout):
    """items: list of (color_tuple, 标题, 描述文字)"""
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['bg']); bg.line.fill.background()
    top_bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, Inches(0.12))
    set_fill(top_bar, colors['primary']); top_bar.line.fill.background()
    add_text(slide, title, Inches(0.8), Inches(0.4), Inches(6), Inches(0.8), Pt(32), True, colors['primary'])
    for i, (color, item_title, desc) in enumerate(items):
        y = Inches(1.8) + int(i) * Inches(1.3)
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), y, Inches(0.12), Inches(1.0))
        set_fill(bar, RGBColor(*color)); bar.line.fill.background()
        add_text(slide, item_title, Inches(1.2), y, Inches(5), Inches(0.45), Pt(16), True, colors['text'])
        add_text(slide, desc, Inches(1.2), y + Inches(0.45), Inches(11), Inches(0.65), Pt(12), False, colors['text_light'])
```

### 2.5 总结页（深色 + 序号圆点）

```python
def add_summary_slide(prs, title, points, colors, layout):
    """points: list of 文字"""
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['primary']); bg.line.fill.background()
    add_text(slide, title, Inches(0.8), Inches(0.4), Inches(5), Inches(1), Pt(36), True, colors['accent'])
    for i, point in enumerate(points):
        y = Inches(1.8) + int(i) * Inches(1.1)
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8), y + Inches(0.1), Inches(0.35), Inches(0.35))
        set_fill(dot, colors['accent']); dot.line.fill.background()
        add_text(slide, str(i+1), Inches(0.8), y + Inches(0.05), Inches(0.35), Inches(0.35), Pt(14), True, colors['primary'], 'center')
        add_text(slide, point, Inches(1.4), y, Inches(10), Inches(0.7), Pt(18), False, colors['accent'])
```

### 2.6 结束页

```python
def add_end_slide(prs, colors, layout, message="谢谢观看"):
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['primary']); bg.line.fill.background()
    dec = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(4), Inches(1.5), Inches(5), Inches(5))
    set_fill(dec, colors['secondary']); dec.line.fill.background()
    add_text(slide, message, Inches(0), Inches(3), PRS_WIDTH, Inches(1.5), Pt(48), True, colors['accent'], 'center')
```

### 2.7 过渡页（Section）

```python
def add_section_slide(prs, title, colors, layout, subtitle=""):
    """章节过渡页：纯色背景 + 大编号 + 标题"""
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['primary']); bg.line.fill.background()
    num = slide.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(4), Inches(3))
    ntf = num.text_frame; p = ntf.paragraphs[0]
    p.text = f"{len(prs.slides):02d}"
    set_font(p.runs[0], size=Pt(120), bold=True, color=colors['secondary'])
    add_text(slide, title, Inches(0.8), Inches(4.5), Inches(11), Inches(1.2), Pt(40), True, colors['accent'])
    if subtitle:
        add_text(slide, subtitle, Inches(0.8), Inches(5.8), Inches(11), Inches(0.8), Pt(18), False, colors['secondary'])
```

### 2.8 双栏对比页（Two Column）

```python
def add_two_column_slide(prs, title, left_title, left_items, right_title, right_items, colors, layout):
    """双栏对比：左右各一栏，中间分隔线"""
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['bg']); bg.line.fill.background()
    add_text(slide, title, Inches(0.8), Inches(0.4), Inches(10), Inches(0.8), Pt(32), True, colors['primary'])
    add_text(slide, left_title, Inches(0.8), Inches(1.5), Inches(5.5), Inches(0.6), Pt(18), True, colors['primary'])
    add_text(slide, right_title, Inches(7.0), Inches(1.5), Inches(5.5), Inches(0.6), Pt(18), True, colors['primary'])
    sep = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.6), Inches(1.5), Inches(0.04), Inches(5.3))
    set_fill(sep, colors['secondary']); sep.line.fill.background()
    for i, item in enumerate(left_items):
        y = Inches(2.3) + int(i) * Inches(0.8)
        add_text(slide, item, Inches(0.8), y, Inches(5.5), Inches(0.7), Pt(14), False, colors['text'])
    for i, item in enumerate(right_items):
        y = Inches(2.3) + int(i) * Inches(0.8)
        add_text(slide, item, Inches(7.0), y, Inches(5.5), Inches(0.7), Pt(14), False, colors['text'])
```

### 2.9 表格页（Table）

```python
def add_table_slide(prs, title, headers, rows, colors, layout):
    """表格页：隔行变色，表头底色"""
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['bg']); bg.line.fill.background()
    add_text(slide, title, Inches(0.8), Inches(0.4), Inches(10), Inches(0.8), Pt(32), True, colors['primary'])
    n_rows, n_cols = len(rows) + 1, len(headers)
    table_shape = slide.shapes.add_table(n_rows, n_cols, Inches(0.8), Inches(1.6), Inches(11.7), Inches(5.0))
    table = table_shape.table
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        p = cell.text_frame.paragraphs[0]
        set_font(p.runs[0], size=Pt(14), bold=True, color=WHITE)
        cell.fill.solid(); cell.fill.fore_color.rgb = colors['primary']
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.text = str(val)
            p = cell.text_frame.paragraphs[0]
            set_font(p.runs[0], size=Pt(13), color=colors['text'])
            if i % 2 == 0:
                cell.fill.solid(); cell.fill.fore_color.rgb = colors['secondary']
    if table.first_row: table.first_row = True
    if table.horz_banding: table.horz_banding = True
```

### 2.10 时间线页（Timeline）

```python
def add_timeline_slide(prs, title, milestones, colors, layout):
    """milestones: list of (阶段名, 描述) — 横向时间线"""
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['bg']); bg.line.fill.background()
    add_text(slide, title, Inches(0.8), Inches(0.4), Inches(10), Inches(0.8), Pt(32), True, colors['primary'])
    axis_y = Inches(3.0)
    axis = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), axis_y, Inches(11.7), Inches(0.06))
    set_fill(axis, colors['secondary']); axis.line.fill.background()
    n = len(milestones)
    total_w = Inches(11.7)
    for i, (label, desc) in enumerate(milestones):
        x = Inches(0.8) + int(i) * (total_w / n)
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, x, axis_y + Inches(0.12), Inches(0.35), Inches(0.35))
        set_fill(dot, colors['accent']); dot.line.fill.background()
        add_text(slide, label, x - Inches(0.5), axis_y - Inches(0.9), Inches(2.2), Inches(0.6), Pt(15), True, colors['primary'])
        add_text(slide, desc, x - Inches(0.5), axis_y + Inches(0.7), Inches(2.2), Inches(1.5), Pt(11), False, colors['text_light'])
```

### 2.11 引用页（Quote）

```python
def add_quote_slide(prs, quote, attribution, colors, layout):
    """引用/金句页：大字居中 + 作者署名"""
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['primary']); bg.line.fill.background()
    q = slide.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.8), Inches(0.6), Inches(1.0), Inches(1.0))
    set_fill(q, colors['secondary']); q.line.fill.background()
    add_text(slide, quote, Inches(1.5), Inches(2.2), Inches(10.3), Inches(3.0), Pt(36), True, colors['accent'], 'center')
    if attribution:
        add_text(slide, f"— {attribution}", Inches(1.5), Inches(5.6), Inches(10.3), Inches(0.8), Pt(16), False, colors['secondary'], 'center')
```

### 2.12 联系/结束信息页（Contact）

```python
def add_contact_slide(prs, title, info_list, colors, layout):
    """结尾联系页：标题 + 联系方式列表（居中）"""
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['bg']); bg.line.fill.background()
    add_text(slide, title, Inches(0), Inches(1.8), PRS_WIDTH, Inches(1.0), Pt(44), True, colors['primary'], 'center')
    for i, item in enumerate(info_list):
        y = Inches(3.2) + int(i) * Inches(0.9)
        add_text(slide, item, Inches(0), y, PRS_WIDTH, Inches(0.7), Pt(18), False, colors['text'], 'center')
```

### 2.13 竖向事件链页（Vertical Chain，v3.4 新增）

> 适用：**流程 / 因果链 / 时间线 / 事故还原**。比横排卡片能装更长描述（每步一行 10.5pt 可写全）。
> 结构：左侧贯穿竖线 + 每行「编号圆点 → 标题(粗) + 描述(小字)」+ 行间橙色小箭头向下连接。

```python
def add_vertical_chain_slide(prs, title, steps, colors, layout, tag=""):
    """竖向事件链：编号圆点 + 标题描述行 + 行间箭头连接器 + 左侧贯穿竖线。
    steps: list of (步骤标题, 描述文字)。tag: 右上角页标签（可选）。"""
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['bg']); bg.line.fill.background()
    add_top_accent_bar(slide, colors)
    add_text(slide, title, Inches(0.8), Inches(0.35), Inches(9.5), Inches(0.7), Pt(25), True, colors['primary'])
    if tag:
        add_text(slide, tag, Inches(9.9), Inches(0.48), Inches(2.9), Inches(0.4), Pt(10), False, colors['text_light'], 'right')
    n = len(steps)
    top = Inches(1.55)
    row_h = Inches(0.95)                 # 每行高
    gap = Inches(0.18)                   # 行间间隙（放箭头）
    dot_x = Inches(0.62)                 # 圆点 x
    dot_d = Inches(0.42)                 # 圆点直径
    text_x = Inches(1.25)                # 文字 x
    text_w = PRS_WIDTH - text_x - Inches(1.0)
    # 左侧贯穿竖线（从首圆点中心到末圆点中心）
    line_top = top + dot_d / 2
    line_bot = top + (n - 1) * (row_h + gap) + dot_d / 2
    vline = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, dot_x + dot_d/2 - Pt(1), line_top, Pt(2), line_bot - line_top)
    set_fill(vline, colors['secondary']); vline.line.fill.background()
    for i, (t, desc) in enumerate(steps):
        y = top + i * (row_h + gap)
        # 编号圆点
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, dot_x, y, dot_d, dot_d)
        set_fill(dot, colors['primary']); dot.line.fill.background()
        add_text(slide, str(i + 1), dot_x, y + Inches(0.02), dot_d, dot_d - Inches(0.04), Pt(12), True, colors['accent'], 'center')
        # 标题 + 描述
        add_text(slide, t, text_x, y - Inches(0.04), text_w, Inches(0.4), Pt(14.5), True, colors['text'])
        add_text(slide, desc, text_x, y + Inches(0.36), text_w, Inches(0.6), Pt(10.5), False, colors['text_light'])
        # 行间向下箭头（非末行）
        if i < n - 1:
            ar = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW, dot_x + dot_d/2 - Inches(0.09), y + dot_d + Inches(0.01), Inches(0.18), gap - Inches(0.02))
            set_fill(ar, colors['accent']); ar.line.fill.background()
    return slide
```

### 2.14 数字徽章配对页（Stat Callout，v3.4 新增）

> 适用：**KPI / 关键数值 / 标准阈值 / 检测结论**。数字是主角、说明是配角。
> 结构：每行「大字数值徽章(浅底色块) + 右侧一行说明文字」，可排列多行；也可嵌进内容页当局部强调。

```python
def add_stat_callout(slide, x, y, w, value, label, colors, val_w=Inches(1.55), row_h=Inches(0.62)):
    """单个数字徽章：浅底色块大字数值 + 右侧说明。返回下一行 y。
    value: 大字数值（如 '3 mJ'）；label: 右侧说明文字。"""
    badge = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, val_w, row_h)
    set_fill(badge, colors['secondary']); badge.line.fill.background()
    add_text(slide, value, x, y + Inches(0.05), val_w, row_h - Inches(0.1), Pt(17), True, colors['primary'], 'center')
    add_text(slide, label, x + val_w + Inches(0.18), y, w - val_w - Inches(0.18), row_h, Pt(10.5), False, colors['text_light'])
    return y + row_h + Inches(0.18)

def add_stat_panel_slide(prs, title, stats, colors, layout, tag="", source=""):
    """整页数字徽章面板：标题 + 多行 数值徽章+说明。source: 底部数据来源标注。"""
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['bg']); bg.line.fill.background()
    add_top_accent_bar(slide, colors)
    add_text(slide, title, Inches(0.8), Inches(0.35), Inches(9.5), Inches(0.7), Pt(25), True, colors['primary'])
    if tag:
        add_text(slide, tag, Inches(9.9), Inches(0.48), Inches(2.9), Inches(0.4), Pt(10), False, colors['text_light'], 'right')
    # 浅底大卡片
    panel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.7), Inches(1.5), PRS_WIDTH - Inches(1.4), Inches(5.0))
    set_fill(panel, colors['light_bg'] if 'light_bg' in colors else colors['secondary']); panel.line.fill.background()
    y = Inches(1.85)
    for value, label in stats:
        y = add_stat_callout(slide, Inches(1.0), y, PRS_WIDTH - Inches(2.0), value, label, colors)
    if source:
        add_source_note(slide, source, colors)
    return slide
```

### 2.15 原生可编辑图表页（Chart，v3.7 新增）

> 适用：**数据趋势 / 对比 / 占比**。用 python-pptx 原生图表（非图片）——观众可在 PowerPoint 里直接编辑数据，比贴图专业、比表格直观。
> 函数内 import：`from pptx.chart.data import CategoryChartData` / `from pptx.enum.chart import XL_CHART_TYPE`

```python
def add_chart_slide(prs, title, categories, series_dict, colors, layout, chart_type='bar', tag="", source=""):
    """原生可编辑图表页。categories: X轴标签列表；series_dict: {'系列名': [值...]}；
    chart_type: 'bar'柱状 / 'line'折线 / 'pie'饼图。source: 底部数据来源标注。"""
    from pptx.chart.data import CategoryChartData
    from pptx.enum.chart import XL_CHART_TYPE
    slide = prs.slides.add_slide(layout)
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, PRS_WIDTH, PRS_HEIGHT)
    set_fill(bg, colors['bg']); bg.line.fill.background()
    add_top_accent_bar(slide, colors)
    add_text(slide, title, Inches(0.8), Inches(0.35), Inches(9.5), Inches(0.7), Pt(25), True, colors['primary'])
    if tag:
        add_text(slide, tag, Inches(9.9), Inches(0.48), Inches(2.9), Inches(0.4), Pt(10), False, colors['text_light'], 'right')
    chart_data = CategoryChartData()
    chart_data.categories = categories
    for name, values in series_dict.items():
        chart_data.add_series(name, values)
    ctype = {'bar': XL_CHART_TYPE.COLUMN_CLUSTERED,
             'line': XL_CHART_TYPE.LINE,
             'pie': XL_CHART_TYPE.PIE}[chart_type]
    slide.shapes.add_chart(ctype, Inches(0.9), Inches(1.5), PRS_WIDTH - Inches(1.8), Inches(5.2), chart_data)
    if source:
        add_source_note(slide, source, colors)
    return slide
```

### 2.16 横向时间轴页（硬时限/里程碑，2026-09-04 实战验证 ★）

> 与 2.10 timeline 的区别：2.10 是"阶段名"时间线；本模板是"**时限值徽章**"时间轴——徽章里放"立即/1小时/24小时"这类硬数字，轴下挂说明卡。制度宣贯/应急响应/审批流程类内容首选。实战反馈：全 deck 评价最高的一页。

```python
def timeline_deadline_slide(prs, title, stats, chapter="", tag=""):
    """stats: list of (时限值, 说明, 颜色) 3-5 项；颜色用 CORAL(急)/DEEP(常规)/TEAL(收尾)"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(s, title, num="", chapter=chapter, tag=tag)
    axis_y = Inches(3.05)
    add_shape(s, MSO_SHAPE.RECTANGLE, Inches(0.8), axis_y, Inches(11.75), Inches(0.09),
              fill=RGBColor(0xC9,0xD4,0xDE))  # 主轴
    n = len(stats)
    for i, (val, label, c) in enumerate(stats):
        cx = Inches(1.35) + i * Inches(11.0 / (n - 1) if n > 1 else 0)
        chip(s, val, cx - Inches(0.85), axis_y - Inches(1.05), Inches(1.7), Inches(0.72), fill=c, size=Pt(18))
        add_shape(s, MSO_SHAPE.OVAL, cx - Inches(0.11), axis_y - Inches(0.08), Inches(0.26), Inches(0.26), fill=c)
        add_shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, cx - Inches(1.12), axis_y + Inches(0.5),
                  Inches(2.3), Inches(1.85), fill=(LIGHT_BG if i % 2 == 0 else PANEL_BLUE))
        add_text(s, label, cx - Inches(0.97), axis_y + Inches(0.68), Inches(2.0), Inches(1.55),
                 size=Pt(11), color=TEXT_BODY, line_spacing=1.2)
    # 底部口诀条（可选）：时限类内容配一句记忆口诀，好评率极高
    return s
```

### 2.17 卡片矩阵页（3+2 / 2×2 网格，2026-09-04 实战验证 ★）

> 目录页、职责分工页、要点归纳页通用。核心：左色条 + 数字圆点 + 标题 + 一行描述。比列表页可扫读性强一个量级。

```python
def card_matrix_slide(prs, title, cards, layout="3+2", chapter="", tag=""):
    """cards: list of (标题, 描述, 颜色)；layout: "3+2"(5项) 或 "2x3"(6项) 或 "2x2"(4项)"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(s, title, num="", chapter=chapter, tag=tag)
    if layout == "3+2":
        pos = [(0.7,1.85),(5.07,1.85),(9.44,1.85),(2.88,4.35),(7.25,4.35)]; cw,chh = 3.87,2.15
    elif layout == "2x3":
        pos = [(0.7,1.75),(6.9,1.75),(0.7,3.25),(6.9,3.25),(0.7,4.75),(6.9,4.75)]; cw,chh = 5.73,1.35
    else:  # 2x2
        pos = [(0.7,1.7),(6.9,1.7),(0.7,4.15),(6.9,4.15)]; cw,chh = 5.73,2.3
    for i, ((t, d, c), (x, y)) in enumerate(zip(cards, pos)):
        X, Y, W, H = Inches(x), Inches(y), Inches(cw), Inches(chh)
        card = add_shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, X, Y, W, H, fill=WHITE, line_color=RGBColor(0xC9,0xD4,0xDE))
        add_shape(s, MSO_SHAPE.RECTANGLE, X, Y, Inches(0.14), H, fill=c)  # 左色条
        num_circle(s, i+1, X+Inches(0.4), Y+Inches(0.32), Inches(0.6), c, size=Pt(20))
        add_text(s, t, X+Inches(1.2), Y+Inches(0.38), W-Inches(1.4), Inches(0.5), size=Pt(19), bold=True, color=DEEP)
        add_text(s, d, X+Inches(0.4), Y+Inches(1.25), W-Inches(0.75), Inches(0.75), size=Pt(12.5), color=TEXT_SUB)
    return s
```

### 2.18 红绿灯对比页（DO / DON'T，2026-09-04 实战验证 ★）

> 行为规范/红线清单页。左右绿红双卡 + 中央信号灯立柱。信号灯是"纪律红线"的图形隐喻，比纯双色卡多一层记忆锚点。

```python
def traffic_light_slide(prs, title, dos, donts, chapter="", tag=""):
    """dos/donts: list of str，各 3-4 条"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(s, title, num="", chapter=chapter, tag=tag)
    # 中央信号灯
    lx = Inches(6.28)
    add_shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, lx, Inches(2.0), Inches(0.78), Inches(2.3), fill=TEXT_MAIN)
    for j, c in enumerate([RED, AMBER, TEAL]):
        add_shape(s, MSO_SHAPE.OVAL, lx+Inches(0.13), Inches(2.16+j*0.73), Inches(0.52), Inches(0.52), fill=c)
    # 左绿卡 / 右红卡
    for (items, x, bg, c, mark) in [(dos, 0.7, GREEN_BG, TEAL, "✓"), (donts, 7.33, RED_BG, RED, "×")]:
        add_shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(1.65), Inches(5.3), Inches(5.15), fill=bg)
        yy = Inches(2.65)
        for it in items:
            add_shape(s, MSO_SHAPE.OVAL, Inches(x+0.35), yy+Inches(0.07), Inches(0.34), Inches(0.34), fill=c)
            add_text(s, mark, Inches(x+0.35), yy+Inches(0.06), Inches(0.34), Inches(0.34),
                     size=Pt(14), bold=True, color=WHITE, align='center')
            add_text(s, it, Inches(x+0.85), yy, Inches(4.25), Inches(0.8), size=Pt(12), color=TEXT_BODY, line_spacing=1.1)
            yy = yy + Inches(1.02)
    return s
```

### 2.19 热力图表格页（梯度考核/风险矩阵，2026-09-04 实战验证 ★）

> 表格页变体：每行整行铺梯度底色（绿→黄→橙→红），"颜色越深=后果越重"不言自明。适合考核标准、风险等级、响应分级。

```python
def heatmap_table_slide(prs, title, headers, rows, chapter="", tag="", source=None):
    """rows: list of (单元格们..., 行底色, 行强调色)；底色梯度如 TINT_TEAL→TINT_GOLD→TINT_CORAL→TINT_RED"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(s, title, num="", chapter=chapter, tag=tag)
    tbl = s.shapes.add_table(len(rows)+1, len(headers), Inches(0.7), Inches(1.62),
                             Inches(11.93), Inches(0.55*(len(rows)+1))).table
    for j, h in enumerate(headers):
        c = tbl.cell(0, j); c.text = h
        p = c.text_frame.paragraphs[0]
        set_font(p.runs[0], size=Pt(14), bold=True, color=WHITE)
        c.fill.solid(); c.fill.fore_color.rgb = DEEP
    for i, row in enumerate(rows, start=1):
        bg, strong = row[-2], row[-1]     # 约定：行尾两个元素是底色和强调色
        for j in range(len(headers)):
            c = tbl.cell(i, j); c.text = row[j]
            p = c.text_frame.paragraphs[0]
            set_font(p.runs[0], size=Pt(13), bold=(j==0 or j==len(headers)-1), color=(strong if j in (0, len(headers)-1) else TEXT_BODY))
            c.fill.solid(); c.fill.fore_color.rgb = bg
    if source:
        add_source_note(s, source)
    return s
```

### 2.20 双通道地铁图页（分级上报/双路径流程，2026-09-04 实战验证 ★）

> 多通道上报/审批分流页：每条通道一条水平"地铁线"+站点圆+站名+交错说明。比左右两栏卡更直观表达"路径"概念。通道数 2-3 条；底部加"拿不准走哪条→先按高的报"类兜底提示。

```python
def metro_lines_slide(prs, title, lines, chapter="", tag=""):
    """lines: list of (通道名, 线色, [(站名, 说明), ...])；每线 3-4 站"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(s, title, num="", chapter=chapter, tag=tag)
    y = Inches(1.7)
    for (lname, lc, stations) in lines:
        add_text(s, lname, Inches(0.75), y, Inches(6.5), Inches(0.4), size=Pt(15.5), bold=True, color=lc)
        line_y = y + Inches(1.1)
        add_shape(s, MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.75), line_y, Inches(11.9), Inches(0.16), fill=lc)
        n = len(stations)
        for i, (st, desc) in enumerate(stations):
            cx = Inches(1.4) + i * Inches(10.5 / max(n - 1, 1))
            add_shape(s, MSO_SHAPE.OVAL, cx - Inches(0.26), line_y - Inches(0.18), Inches(0.52), Inches(0.52), fill=WHITE, line_color=lc)
            add_text(s, str(i+1), cx - Inches(0.26), line_y - Inches(0.10), Inches(0.52), Inches(0.4),
                     size=Pt(15), bold=True, color=lc, align='center')
            add_text(s, st, cx - Inches(0.85), line_y - Inches(0.72), Inches(1.7), Inches(0.4),
                     size=Pt(13), bold=True, color=TEXT_BODY, align='center')
            ty = line_y + Inches(0.42) if i % 2 == 0 else line_y + Inches(0.95)  # 说明交错高度防横排互撞
            add_text(s, desc, cx - Inches(0.95), ty, Inches(1.9), Inches(0.6),
                     size=Pt(9), color=TEXT_SUB, align='center', line_spacing=1.05)
        y = y + Inches(2.35)
    return s
```

### 2.21 阶梯分级页（四级/五级梯度，2026-09-04 实战验证 △有坑）

> 事故分级/风险等级/响应级别页：从左到右台阶逐级升高（颜色绿→黄→橙→红）。**坑**：①台阶高度必须预留标题栏下方空间（最高台阶顶 ≥1.7"，标题栏高 1.35"）；②台阶体上只放"级别名·副标"一行白字，说明文字放台阶下部白色内嵌区（两区之间留 ≥0.3" 色带隔离，否则文本框贴边被判重叠）；③右上角不要放提示行（会撞最高台阶），提示放左上空区。

```python
def stair_levels_slide(prs, title, levels, base_y=6.35, chapter="", tag="", source=None):
    """levels: list of (级别名, 副标, 颜色, 说明, 台阶高in)；高度递增如 [1.7, 2.85, 4.0, 4.95]"""
    s = prs.slides.add_slide(prs.slide_layouts[6])
    add_title_bar(s, title, num="", chapter=chapter, tag=tag)
    card_w, gap = Inches(2.86), Inches(0.15)
    inner_h = Inches(1.30)  # 白色说明区高
    for i, (name, sub, color, desc, ch_h) in enumerate(levels):
        x = Inches(0.6) + i * (card_w + gap)
        y = int(Inches(base_y) - Inches(ch_h))
        add_shape(s, MSO_SHAPE.RECTANGLE, x, y, card_w, Inches(ch_h), fill=color)
        add_text(s, name + " · " + sub, x + Inches(0.2), y + Inches(0.08),
                 card_w - Inches(0.4), Inches(0.32), size=Pt(15), bold=True, color=WHITE)
        add_shape(s, MSO_SHAPE.RECTANGLE, x + Inches(0.14), int(Inches(base_y) - inner_h - Inches(0.12)),
                  card_w - Inches(0.28), inner_h, fill=WHITE)
        add_text(s, desc, x + Inches(0.26), int(Inches(base_y) - inner_h + Inches(0.16)),
                 card_w - Inches(0.52), inner_h - Inches(0.34), size=Pt(10.5), color=TEXT_BODY, line_spacing=1.12)
        if i < len(levels) - 1:
            add_shape(s, MSO_SHAPE.RIGHT_ARROW, x + card_w + Inches(0.01), y - Inches(0.42),
                      gap + Inches(0.13), Inches(0.32), fill=AMBER)
    if source:
        add_source_note(s, source)
    return s
```

**图形隐喻使用纪律（2026-09-04 教训）**：图形修辞做一半不如不做——环形流程图若无循环箭头连线就是"散点图"（退回条带布局更诚实）；旋转椭圆拼"五瓣花"生硬且难复现（不回流）。**隐喻要么连同连接语言（箭头/连线）完整实现，要么放弃**。

### 2.22 设计网格系统（20pt 基准网格 + 4pt 磁吸，2026-09-04 用户版拆解回流 ★★）

> 对比用户手工/外部工具美化版时发现的最强隐性差异：**用户版 73% 的坐标值落在 20pt（0.278"）整数倍网格上，我方原版只有 4%**。"看起来专业"的第一功臣不是配色也不是字体，是**所有元素都站在同一张隐形网格上**。字号也全部取整（10/11/12/13/14/15/16/18/20/24pt），无 10.8/12.5/13.5 之类小数档。

```python
# 设计网格常量（放 common 模块顶部，全 deck 引用）
GRID = Inches(20 / 72)          # 20pt 基准格 ≈ 0.278"
MARGIN = 2 * GRID               # 页边距 40pt ≈ 0.556"（内容区统一从 0.556 起）

def gx(n):
    """第 n 格的坐标（in float，最后一步才 Inches() 包装）"""
    return n * 20.0 / 72.0

# 用法：布局坐标全部取 gx(n)，如 gx(2)=0.556、gx(4)=1.111、gx(8)=2.222
# 生成后自检：dump 所有 shape 坐标，落在 20pt 网格 ±0.02 的比例应 ≥60%
```

**配套纪律**：①字号只取整数 pt（正文 11-13、条目标题 15-17、页标题 24、封面 48）；②页边距/卡片间距用网格倍数（40pt 边距、8-10pt 间隙）；③文字容器与徽章/圆点错位叠加时，用同一网格原点分别定位（外层 20pt 格、内层 10pt 半格），天然对齐。验证法：python-pptx 重读文件统计 `round(coord*72/20)` 命中率。

### 2.23 序列同色相明度递进（单页 5 步流程配色，2026-09-04 用户版拆解回流 ★）

> 我方旧做法：流程 1-5 步配 蓝蓝橙紫绿 五个色相乱跳（观感"花"）。用户版：**同一逻辑链内用"同色系明度递进 + 端点强调"**——`#0F4C81→#156096→#1E78B4→#E87722→#BE5014`（蓝→浅蓝→橙→深橙，色温从冷到暖渐进升温），既保持序列感又暗示"越往后越紧急/越重要"。并列卡片组（目录/职责）同理：5 张卡左色条依次取这 5 色，末卡用警示色收尾。

```python
SEQ_LADDER = ['#0F4C81', '#156096', '#1E78B4', '#E87722', '#BE5014']  # 冷→暖 5 档
# 4 步序取前 4；6 步序在中间插 '#4A90B8' 过渡。规则：序列页禁用 3+ 个不同色相，
# 用"主色系明度递进 + 强调色只给端点（首/尾）"表达顺序感。
```

### 2.24 文字覆盖层模式（形状本体承载底色、文字放独立透明框，2026-09-04 用户版拆解回流 ★）

> 外部 AI 生成 deck 的标志性结构：每个可见形状 = 两个叠加 shape——**底层 roundRect 承载填充/描边，上层透明 rect 只放文字**（`fill=nofill`）。好处：①文字框与装饰边界解耦，改文案不碰版式；②文字锚点/边距独立可控，不会出现"文字被圆角挤到边上"；③批量换文案时只动文字层，装饰层零风险。python-pptx 里实现即 `add_shape(...)` 后在其上叠加 `add_text(...)`（坐标同原点同尺寸）。**代价是 shape 数量翻倍**（21 页 ~660 shapes），页数多时权衡使用——重点页（封面/流程/卡片页）用覆盖层，纯文本页不必。

### 2.25 图标素材能力边界（iconfont/PNG 可用，SVG 原生不支持，2026-09-04 探针验证）

> 图标资源（iconfont 等）能否用进 python-pptx deck，取决于**格式与库能力匹配**：
> - **PNG**（含透明底）：✅ `add_picture` 直接可用——做"图标徽章/小方块图标"首选。iconfont 单色图标可下 PNG（16-256px），改色需在下载时选色或 PIL 重染。
> - **SVG**：❌ **python-pptx 原生不支持**（`add_picture` 对 SVG 抛 UnidentifiedImageError，实测确认）。venv 未装 cairosvg/svglib。两条可行路线：①装 `cairosvg` 转 PNG 再插入（代价：新增依赖 + 转换精度损失）；②**拆 SVG path 数据用 python-pptx 自由曲线重绘**（`MSO_SHAPE.FREEFORM`，保矢量可编辑、颜色可改）——单色图标 path 通常简洁，值得；复杂多色图标不值得（重绘成本高）。
> - **图标字体**：iconfont 可把图标集转成字体（前端玩法），python-pptx 无原生字形插入支持，❌ 不适用。
> - 适用场景分层：**1-2 色简单语义图标**（盾牌/警报/齿轮/对勾）→ 用统一 PNG 池或 FREEFORM 重绘；**多色复杂插画** → 仍走 ImageGen/图库路线。
> 插入规范（与 refine 诊断库对齐）：等比缩放不拉伸、避开页脚与标题栏、不遮正文、统一风格（全 deck 同一线条风格）。

### 2.26 内建安全图标池 + add_icon 函数（2026-09-04 实战验证 ★★）

> **40 个安全语义图标（外置资产，非 skill 内置）**：PNG 池归档在 `<icon-archive>/ray-ppt-generator-icon-pool-20260904/`（256×256 透明底，Lucide 线性风格，ISC 可商用）——**skill 目录内不放任何图片**（SkillHub 发布拒收 .png，故外置）。覆盖防护/警示（shield/shield-alert/triangle-alert/bell/flame/skull/radiation/siren）、安全行为（check/x/eye/search/list-checks/clipboard-check/user-check）、管理（settings/file-text/book-open/graduation-cap/clock/timer/target/megaphone/phone-call）等。命名规范 `{语义}_{色值}.png`（如 `shield_0F4C81.png`）。

```python
# add_icon 便捷函数 —— 从外置图标池插一个图标（透明 PNG）
import os
ICON_ARCHIVE = r"<icon-archive>/ray-ppt-generator-icon-pool-20260904"

def _find_icon(key, color):
    """在外置池定位图标文件；池缺失/无此图标→提示跑重建脚本"""
    if not os.path.isdir(ICON_ARCHIVE):
        raise FileNotFoundError(
            f"图标池缺失：{ICON_ARCHIVE}\n→ 跑 scripts/build_icon_pool.py 重建（需联网拉 Lucide）")
    want = f"{key}_{color}.png" if color else None
    if want and os.path.exists(os.path.join(ICON_ARCHIVE, want)):
        return os.path.join(ICON_ARCHIVE, want)
    cands = [f for f in os.listdir(ICON_ARCHIVE) if f.startswith(key + "_")]
    if not cands:
        raise FileNotFoundError(f"图标池无 {key}（有 {len(os.listdir(ICON_ARCHIVE))} 个图标）")
    return os.path.join(ICON_ARCHIVE, cands[0])

def add_icon(slide, icon_key, x_in, y_in, size_in, color=None):
    pic = slide.shapes.add_picture(_find_icon(icon_key, color),
                                   Inches(x_in), Inches(y_in),
                                   Inches(size_in), Inches(size_in))
    return pic

# 用法：封面/卡片加盾牌
# add_icon(s, 'shield', 11.8, 0.15, 0.5)          # 蓝色盾牌
# add_icon(s, 'triangle-alert', 0.6, 1.5, 0.4, 'BE1E1E')  # 红警告
```

**重建脚本**：`scripts/build_icon_pool.py`（Lucide CDN + resvg_py 渲染，40 图标一键重建/增补，产物写入上述外置目录——脚本内 POOL 常量指向外置路径）。技术要点：①jsdelivr 需带 `Mozilla` UA（urllib 裸 UA 会 404）；②`resvg_py.svg_to_bytes(svg_string=..., zoom=256/24)`（API 名不是 `render`）；③SVG 是 `stroke=currentColor`，重染只需把 `currentColor` 替换成目标 hex。**若要新增图标**：改脚本 `ICONS` dict（name→(文件名,语义,建议色)）→ 重跑脚本 → 新 PNG 落入外置目录。

## 3. Win32COM 后处理（批量改字体/颜色/间距，需本机 PowerPoint）

> ⚠️ COM 索引从 1 开始（`Slides(1)` 是第一张），`True = -1`。修改前务必先备份原文件（`*_backup.pptx`）。`.RGB` 是 **BGR** 顺序（蓝-绿-红），不是 RGB。

### BGR 颜色转换

```python
def rgb_to_bgr(hex_color: str) -> int:
    """#7CBD3E → 0x3EBD7C"""
    r = int(hex_color[1:3], 16)
    g = int(hex_color[3:5], 16)
    b = int(hex_color[5:7], 16)
    return (b << 16) | (g << 8) | r
```

### 批量字体替换

```python
def replace_font(pptx_path, new_font="Microsoft YaHei"):
    import win32com.client, shutil
    backup = pptx_path.replace(".pptx", "_backup.pptx")
    shutil.copy2(pptx_path, backup)  # 先备份！
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    ppt.Visible = True
    pres = ppt.Presentations.Open(pptx_path, WithWindow=False, ReadOnly=False)
    for i in range(1, pres.Slides.Count + 1):
        for shape in pres.Slides(i).Shapes:
            if shape.HasTextFrame == -1:
                shape.TextFrame.TextRange.Font.Name = new_font
    pres.Save(); pres.Close(); ppt.Quit()
```

### 批量段落间距调整

```python
def adjust_spacing(pptx_path, space_before=4, space_after=6, line_spacing=1.5):
    import win32com.client
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    ppt.Visible = True
    pres = ppt.Presentations.Open(pptx_path, WithWindow=False, ReadOnly=False)
    for i in range(1, pres.Slides.Count + 1):
        for shape in pres.Slides(i).Shapes:
            if shape.HasTextFrame == -1:
                tr = shape.TextFrame.TextRange
                for p in range(1, tr.Paragraphs().Count + 1):
                    para = tr.Paragraphs(p)
                    para.ParagraphFormat.SpaceBefore = space_before
                    para.ParagraphFormat.SpaceAfter = space_after
                    para.ParagraphFormat.LineSpacing = line_spacing
    pres.Save(); pres.Close(); ppt.Quit()
```

### 文本替换

```python
def replace_text(pptx_path, find_str, replace_str, save_path=None):
    """全局查找替换文本"""
    import win32com.client
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    ppt.Visible = True
    pres = ppt.Presentations.Open(pptx_path, WithWindow=False, ReadOnly=False)
    for i in range(1, pres.Slides.Count + 1):
        for shape in pres.Slides(i).Shapes:
            if shape.HasTextFrame == -1:
                tr = shape.TextFrame.TextRange
                tr.Text = tr.Text.replace(find_str, replace_str)
    out = save_path or pptx_path
    pres.SaveAs(out); pres.Close(); ppt.Quit()
```

### 插入/删除幻灯片

```python
def insert_slide(pptx_path, index, layout_index=1, save_path=None):
    """在指定位置插入空白幻灯片（index 从 1 开始）"""
    import win32com.client
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    ppt.Visible = True
    pres = ppt.Presentations.Open(pptx_path, WithWindow=False, ReadOnly=False)
    pres.Slides.Add(index, layout_index)
    out = save_path or pptx_path
    pres.SaveAs(out); pres.Close(); ppt.Quit()

def delete_slide(pptx_path, index, save_path=None):
    """删除指定幻灯片"""
    import win32com.client
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    ppt.Visible = True
    pres = ppt.Presentations.Open(pptx_path, WithWindow=False, ReadOnly=False)
    pres.Slides(index).Delete()
    out = save_path or pptx_path
    pres.SaveAs(out); pres.Close(); ppt.Quit()
```

### 提取内嵌图片

```python
def extract_images(pptx_path, outdir):
    """提取 PPTX 中所有内嵌图片到目录"""
    import zipfile, os
    os.makedirs(outdir, exist_ok=True)
    with zipfile.ZipFile(pptx_path) as z:
        for name in z.namelist():
            if name.startswith('ppt/media/'):
                fn = os.path.join(outdir, os.path.basename(name))
                with open(fn, 'wb') as f:
                    f.write(z.read(name))
```

### 导出幻灯片为图片（视觉 QA 用，v3.3 新增）

```python
def export_slides_to_images(pptx_path, outdir="slide_imgs"):
    """用 PowerPoint COM 导出每页为 PNG，供视觉 QA 逐页检查"""
    import win32com.client, os
    ppt = win32com.client.Dispatch("PowerPoint.Application")
    ppt.Visible = False
    pres = ppt.Presentations.Open(pptx_path, WithWindow=False, ReadOnly=True)
    os.makedirs(outdir, exist_ok=True)
    for i in range(1, pres.Slides.Count + 1):
        pres.Slides(i).Export(os.path.join(outdir, f"slide-{i:02d}.png"), "PNG", 1280, 720)
    pres.Close(); ppt.Quit()
    print(f"已导出 {pres.Slides.Count} 页到 {outdir}")
```
