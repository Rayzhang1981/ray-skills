# Refine 工具库（按需加载，勿全量载入上下文）

> 使用规则：美化已有 PPTX 时按需**复制粘贴**对应函数到脚本，改参数即可。检测用 python-pptx（只读解析），修改用 Win32COM（保留渐变/阴影效果）。**任何修改前先备份 `_backup.pptx`**。

## 0. 辅助函数

```python
def rgb_to_bgr(hex_color: str) -> int:
    """#7CBD3E → 0x3EBD7C（COM 的 .RGB 是 BGR 顺序）"""
    r = int(hex_color[1:3], 16); g = int(hex_color[3:5], 16); b = int(hex_color[5:7], 16)
    return (b << 16) | (g << 8) | r
```

## 1. 读取解析 + 排版扫描器（python-pptx，只读）

> 检测已有 PPTX 的排版问题，产出初筛报告。**只读，不修改文件**。

```python
def scan_pptx(pptx_path):
    """排版问题初筛：字体/字号分布 + 溢出风险页 + 页数。"""
    from pptx import Presentation
    from collections import Counter
    prs = Presentation(pptx_path)
    fonts, sizes, overflow_risk = Counter(), Counter(), []
    for idx, slide in enumerate(prs.slides, 1):
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            tf = shape.text_frame
            # 溢出风险：word_wrap 关闭 且 文字偏多
            if tf.word_wrap is False and len(tf.text) > 30:
                overflow_risk.append((idx, shape.shape_id, "word_wrap关闭且文字多"))
            for para in tf.paragraphs:
                for run in para.runs:
                    if run.font.name:
                        fonts[run.font.name] += 1
                    if run.font.size:
                        sizes[round(run.font.size.pt, 1)] += 1
    return {
        "slides": len(prs.slides),
        "fonts": fonts.most_common(),        # 多种字体 → 不统一
        "sizes": sizes.most_common(),        # 字号过杂 → 层级不清
        "overflow_risk": overflow_risk,      # 溢出风险页
    }

def scan_colors(pptx_path):
    """统计正文颜色分布：颜色种类过多 / 默认蓝 → 配色混乱。"""
    from pptx import Presentation
    from collections import Counter
    prs = Presentation(pptx_path)
    colors = Counter()
    for slide in prs.slides:
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    try:
                        rgb = run.font.color.rgb
                        if rgb is not None:
                            colors[str(rgb)] += 1
                    except Exception:
                        pass  # 主题色继承，跳过
    return colors.most_common()
```

**解读**：`fonts` 出现宋体/Calibri 混入 → 需统一微软雅黑；`colors` 种类 >5 或含默认 Office 蓝 → 建议换肤；`overflow_risk` 非空 → 需修复溢出。

## 2. 转图片视觉 QA（Win32COM）

> **核心检测手段**：扫描器给数据，图片给真相。逐页看 PNG 找溢出/重叠/对齐/美观问题。

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
    n = pres.Slides.Count
    pres.Close(); ppt.Quit()
    print(f"已导出 {n} 页到 {outdir}")
```

### 备选：PowerShell 原生 COM（venv 无 pywin32 时，2026-08-27 实战验证）

```powershell
$pp = New-Object -ComObject PowerPoint.Application
$pres = $pp.Presentations.Open("E:\...\final.pptx", 0, 0, 0)   # ReadOnly, Untitled, WithWindow 全 0
foreach ($n in @(15,16,35,40)) { $pres.Slides.Item($n).Export("E:\...\_render\S$n.png", "PNG", 1280, 720) }
$pres.Close(); $pp.Quit()
```

⚠️ **首次调用可能"看似无输出但已成功"**（exit 0 无打印）——先 `ls` 输出目录确认，别盲目重试。

### ⚠️ 读不了图时的"看图"降级链路（2026-08-27 实战验证，23 页逐页通过；**2026-09-12 起：先试原生 Read**）

**先试原生 Read**：2026-09 起主流模型普遍原生多模态（deepseek-flash-V4.1、glm-flash-5.3 等），多数情况直接 Read PNG 即可看图——**只有 Read 报"不支持读图"（或宿主模型确为纯文本）时**，才需要下面的降级链路：

```bash
# ray-ppt-ocr-eyes：OCR 文字层 + VL 视觉描述层（opencode-go 默认，key 已固化）
PY="~/.workbuddy/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
for n in 30 32 35 40; do
  "$PY" "~/.workbuddy/.workbuddy/skills/ray-ppt-ocr-eyes/scripts/ocr_eyes.py" \
        "E:\\LingXi\\...\\_render\\S$n.png" --provider opencode-go 2>&1 \
    | sed -n '/【视觉描述/,$p'
done
```

逐页读输出确认：**OCR 层**核文字内容、**视觉描述层**核布局（无溢出/无重叠/风格一致）。

⚠️ **路径必须 Windows 格式 `E:\\...`**——Git Bash 的 `/e/...` 路径 Python 不认（报"找不到图片"）。
⚠️ 左右分栏页的 OCR 会把两栏同一水平线的文字合并成一行（假象），布局判断以 VL 描述层为准。

## 3. Win32COM 批量修复

> ⚠️ COM 索引从 1 开始，`True = -1`，`.RGB` 是 BGR。**修改前务必备份**。

```python
def unify_font(pptx_path, new_font="Microsoft YaHei"):
    """批量统一字体（保留字号/粗体/颜色，只改字体名）"""
    import win32com.client, shutil
    shutil.copy2(pptx_path, pptx_path.replace(".pptx", "_backup.pptx"))
    ppt = win32com.client.Dispatch("PowerPoint.Application"); ppt.Visible = True
    pres = ppt.Presentations.Open(pptx_path, WithWindow=False, ReadOnly=False)
    for i in range(1, pres.Slides.Count + 1):
        for shape in pres.Slides(i).Shapes:
            if shape.HasTextFrame == -1:
                shape.TextFrame.TextRange.Font.Name = new_font
    pres.Save(); pres.Close(); ppt.Quit()

def fix_overflow(pptx_path):
    """修复文字溢出：所有文本框启用 word_wrap"""
    import win32com.client, shutil
    shutil.copy2(pptx_path, pptx_path.replace(".pptx", "_backup.pptx"))
    ppt = win32com.client.Dispatch("PowerPoint.Application"); ppt.Visible = True
    pres = ppt.Presentations.Open(pptx_path, WithWindow=False, ReadOnly=False)
    for i in range(1, pres.Slides.Count + 1):
        for shape in pres.Slides(i).Shapes:
            if shape.HasTextFrame == -1:
                shape.TextFrame.WordWrap = -1  # True
    pres.Save(); pres.Close(); ppt.Quit()

def adjust_spacing(pptx_path, space_before=4, space_after=6, line_spacing=1.5):
    """批量调整段落间距，让版面呼吸"""
    import win32com.client, shutil
    shutil.copy2(pptx_path, pptx_path.replace(".pptx", "_backup.pptx"))
    ppt = win32com.client.Dispatch("PowerPoint.Application"); ppt.Visible = True
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

## 4. 配色方案库 + 一键换肤

```python
PALETTES = {
    'navy-executive':   {'name':'商务深蓝','primary':(30,39,97),'text':(30,39,97),'text_light':(107,114,128)},
    'tech-dark':        {'name':'科技深空','primary':(13,17,23),'text':(240,246,252),'text_light':(139,148,158)},
    'ocean-gradient':   {'name':'海洋渐变','primary':(6,90,130),'text':(6,90,130),'text_light':(107,114,128)},
    'teal-trust':       {'name':'青绿信任','primary':(2,128,144),'text':(6,90,96),'text_light':(55,65,81)},
    'warm-terracotta':  {'name':'暖陶简约','primary':(184,80,66),'text':(61,61,61),'text_light':(107,114,128)},
    'charcoal-minimal': {'name':'炭灰极简','primary':(54,69,79),'text':(54,69,79),'text_light':(139,148,158)},
    'paper-sketch':     {'name':'纸张手绘风','primary':(157,90,55),'text':(37,37,37),'text_light':(88,88,88),'bg':(244,242,238)},
}
# 纸张手绘风（v1.2 新增，对比高手版《RBPS 意识培训》）：F4F2EE 米白底 / 9D5A37 棕褐强调 / 252525 近黑正文。
# 配合灰度插图 + 细长线元素（freeform 高 ~0.3"）→ "图纸感"，工程师/技术受众亲和。
SAFE_BLUE = "#005293"  # 化工安全主色

def apply_text_color(pptx_path, body_color="#2C3E50"):
    """换肤基础步：批量统一正文颜色（保留字体/字号，只改颜色）。标题栏/配色块需按形状另映射。"""
    import win32com.client, shutil
    shutil.copy2(pptx_path, pptx_path.replace(".pptx", "_backup.pptx"))
    ppt = win32com.client.Dispatch("PowerPoint.Application"); ppt.Visible = True
    pres = ppt.Presentations.Open(pptx_path, WithWindow=False, ReadOnly=False)
    bgr = rgb_to_bgr(body_color)
    for i in range(1, pres.Slides.Count + 1):
        for shape in pres.Slides(i).Shapes:
            if shape.HasTextFrame == -1:
                shape.TextFrame.TextRange.Font.Color.RGB = bgr
    pres.Save(); pres.Close(); ppt.Quit()
```

> **换肤说明**：完整换肤 = 统一字体（`unify_font`）+ 统一正文色（`apply_text_color`）+ 标题栏/配色块按 PALETTES 主色映射。配色块（形状填充）需按 `shape.Fill.ForeColor.RGB` 逐个替换为 palette 的 primary/secondary——逐页视觉确认后执行，别盲改。

## 5. 复验

修复后重新跑 `export_slides_to_images()` 导出**受影响页**，逐页复验：溢出是否消失、字体是否统一、配色是否生效、有无引入新重叠。全绿才交付。

## 6. 配图工具（v1.3 新增，cover 裁切消除竖框留白）

```python
def add_pic_card(s, img_path, l, t, w, h, line_color, cover=True, PHOTO_DIR=''):
    """白框图片卡：cover=True 居中裁成框同比例撑满（横向图进竖框零留白）；白框围绕图片实际位置（单一基准）"""
    from PIL import Image
    iw, ih = Image.open(img_path).size
    if cover:
        target = w / h; src = iw / ih
        if src > target:
            nw = int(ih * target); nx = (iw - nw) // 2; box = (nx, 0, nx + nw, ih)
        else:
            nh = int(iw / target); ny = (ih - nh) // 2; box = (0, ny, iw, ny + nh)
        im = Image.open(img_path).crop(box)
        tmp = os.path.join(PHOTO_DIR, '_crop_tmp.jpg'); im.save(tmp, quality=90)
        path = tmp; pw, ph = int(w), int(h)
    else:
        r = min(w / iw, h / ih); pw, ph = int(iw * r), int(ih * r); path = img_path
    px = int(l + (w - pw) / 2); py = int(t + (h - ph) / 2)
    rect(s, px - Emu(int(0.05*914400)), py - Emu(int(0.05*914400)),
         pw + Emu(int(0.1*914400)), ph + Emu(int(0.1*914400)), fill=WHITE, line=line_color)
    s.shapes.add_picture(path, px, py, width=pw, height=ph)
```

**配图决策链**：扫描空白（右半区→网格→精确小区域逐层收敛）→ 有空白直接配 → 无空白不硬塞（遮内容）→ 布局让位（公共函数收窄文字宽批量让出侧栏）→ 配图后专项检查插图底边 vs 相邻元素。
