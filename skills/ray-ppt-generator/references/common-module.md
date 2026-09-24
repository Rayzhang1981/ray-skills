# 公共模块（code-templates.md 的缺件补齐）

> **为什么有这份文件（v3.20.0 新增，回流审计 G1）**：`references/code-templates.md` 的 2.16–2.21（时限时间轴 / 卡片矩阵 / 红绿灯对比 / 热力图表格 / 双通道地铁图 / 阶梯分级）在正文里调用了一个 `add_shape()` 辅助函数与若干色常量，**但它们此前在全 skill 目录内没有定义** —— 照抄那几段会直接 `NameError`。本文件把缺的那块补齐，复制到 `code-templates.md` 第 0 节一起用即可。

---

## 0-A. 色常量补遗（第 0 节已有 `SAFE_BLUE` 等，这里是 2.16–2.21 额外用到的）

```python
# === 2.16–2.21 额外用到的色常量（与第 0 节同风格）===
DEEP        = RGBColor(0x0D, 0x3B, 0x66)   # 深蓝：卡片标题 / 表格表头
GOLD        = RGBColor(0xE9, 0xC4, 0x6A)   # 页眉章节名
AMBER       = RGBColor(0xF0, 0xA0, 0x3C)   # 警示橙（次强）
TEAL        = RGBColor(0x2A, 0x9D, 0x8F)   # 青绿：正向 / 收尾
LIGHT_BG    = RGBColor(0xF5, 0xF8, 0xFB)   # 极浅底（卡片隔行）
PANEL_BLUE  = RGBColor(0xEA, 0xF2, 0xF9)   # 浅蓝面板
RED_BG      = RGBColor(0xFD, 0xED, 0xEC)   # 红底（高风险卡）
GREEN_BG    = RGBColor(0xE8, 0xF6, 0xEE)   # 绿底（低风险卡）
# 热力图（2.19）行底色梯度：绿 → 黄 → 橙 → 红（"颜色越深 = 后果越重"）
TINT_TEAL   = RGBColor(0xE8, 0xF6, 0xEE)
TINT_GOLD   = RGBColor(0xFD, 0xF6, 0xE3)
TINT_CORAL  = RGBColor(0xFD, 0xEF, 0xE6)
TINT_RED    = RGBColor(0xFD, 0xED, 0xEC)
```

## 0-B. `add_shape()` —— 2.16–2.21 的统一画形状入口

```python
def add_shape(slide, kind, x, y, w, h, fill=None, line_color=None, line_w=Pt(1.0)):
    """统一画形状：fill=None 留空（透明），line_color=None 无描边。
    全 deck 只用这一个入口画 rect/oval/roundRect/箭头，风格天然一致。
    ⚠️ x/y/w/h 传 Inches() 值；参数名用 line_color 以免与 .line 属性混淆。"""
    sp = slide.shapes.add_shape(kind, x, y, w, h)
    sp.shadow.inherit = False                 # 关掉 python-pptx 默认阴影（AI 痕迹）
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line_color is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line_color; sp.line.width = line_w
    return sp
```

## 0-C. `notes()` / `slide()` 短别名（页面函数里高频，可省字数）

```python
def slide(prs):
    """新建空白页（16:9，layout[6]）。⚠️ 自己建页的页函数才用它；
    调用任意 *_slide() 页面函数的页函数**不得**再调用它（双页根因，见核心原则 11）。"""
    return prs.slides.add_slide(prs.slide_layouts[6])

def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text
```

---

## 与 `code-templates.md` 的关系

| | 内容 | 命名风格 |
|---|---|---|
| `code-templates.md` 第 0 节 | `set_fill` / `set_font` / `add_text` / `add_title_bar` / `add_footer` / `chip` / `num_circle` / `add_source_note` | `add_*` |
| `code-templates.md` 2.1–2.12 | 早期页面函数 | `add_*_slide` |
| `code-templates.md` 2.13–2.26 | 后期页面函数 + 设计网格 / 序列配色 / 覆盖层 / 图标池 | `add_*` 与 `*_slide` 混用 |
| **本文件** | 上面缺的色常量 + `add_shape` + `slide` / `notes` 别名 | — |

**统一事实（核心原则 11 的判据基础）**：上表**每一个页面函数都在函数体内自己 `add_slide`** —— 所以调用它们的页函数**绝不能再自己建页**。函数名有两套（历史原因），**规则一条**：*页函数只写数据，或只自己建页，二选一*。机械核验走 `scripts/qa_ppt.py --dblpage gen_*.py`（v3.20.0 起，替换了原先的 grep 钩子）。
