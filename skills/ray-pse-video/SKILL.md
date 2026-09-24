---
name: ray-pse-video
slug: ray-pse-video
displayName: 事故报告转安全培训视频
description: >-
  Use when converting a process safety incident report (PDF/Word/image) into a narrated safety training video with PPT, TTS, hard subtitles, and FFmpeg MP4 assembly. Triggers: "事故报告转视频", "安全培训视频", "incident report to training video", or converting any structure document into a slide-video workflow.
agent_created: true
version: 2.4.1
---

# ray-PSE-Video — 事故报告转安全培训视频

将化工过程安全事故调查报告自动化转换为带 AI 配音 + 硬字幕的 MP4 培训视频。

## 流程概览

```
事故报告 PDF/扫描件 → OCR提取文本 → AI分析 → PPT课件(pptxgenjs) → 旁白脚本
    → Qwen3-TTS/edge-tts 双引擎配音 → PowerPoint COM导出幻灯片PNG → 逐段生成clip
    → 合并clip → 烧录SRT字幕(两步法) → 验证 → MP4
```

**v2.0 新特性** (2026-07-16):
- 🎙️ Qwen3-TTS + edge-tts 双引擎配音
- 🎤 Qwen3-TTS 声音克隆（5-15 秒参考音频）
- 🎛️ 5 种 Qwen3 预设音色 + 6 种 edge-tts 推荐语音

## 执行铁律 ⚠️

基于多次会话中断、任务丢失的教训，全流程必须遵守以下铁律。

### 1. 前台同步执行，禁止后台任务

**❌ 致命错误**：用 `run_in_background=true` 跑关键编码步骤。
- 会话刷新后 `task_id` 丢失，进程状态不可见
- 错误信息卡在缓冲区无法诊断
- 本次隆莱项目 clip 编码中断两次，全因后台任务丢失

**✅ 正确做法**：所有步骤前台同步执行，timeout 给够。

```python
# ❌ 后台 → 会话刷新丢失
subprocess.run(cmd, run_in_background=True)  # 不！

# ✅ 前台 + 足够 timeout
subprocess.run(cmd, timeout=600)  # 10 分钟，够编码完
# Shell 调用加 -u 解缓冲
python -u -c "..."
```

### 2. 分步执行，每步验证

全流程拆为独立步骤，每步产出保存到磁盘，验证通过再进下一步。

```
Step 1: OCR → 保存 report_ocr.md，检查文件大小 > 10KB
Step 2: PPT  → 保存 output.pptx，检查文件存在
Step 3: 旁白 → 硬编码在 Python 函数中
Step 4: TTS  → 保存 audio/slide_XX.mp3 + narration_data.json，检查 12 个文件
Step 5: 导出 → 保存 slides/slide_XX.png，检查 12 个文件
Step 6: clip  → 保存 clips/clip_XX.mp4 + clip_data.json，每段验证 v≈a
Step 7: 合并 → 保存 video_merged.mp4，验证 Duration 匹配
Step 8: 烧录 → 保存 video_final.mp4，ffmpeg -v error 验证
Step 9: 水印 → 保存 video_output.mp4 → 复制到最终路径
```

### 3. 状态持久化，断了能续

每步关键数据保存到 JSON，步与步之间解耦。

```python
# Step 4 完成后保存
json.dump({'audio_durations': [...], 'slide_offsets': [...]}, 
    open('narration_data.json', 'w'))

# Step 6 完成后保存
json.dump({'clip_durations': [...]}, 
    open('clip_data.json', 'w'))

# 恢复时检查已有文件，跳过已完成步骤
if os.path.exists(clip_mp4):
    clip_durations.append(probe_duration(clip_mp4))
    continue  # 跳过，不重编
```

### 4. PowerPoint 文件锁处理

COM 导出后 PowerPoint 可能未完全释放文件锁 → 再次写入 PPTX 时报 `PermissionError`。

```python
# 重新生成 PPTX 前，先杀 PowerPoint 进程
subprocess.run(['taskkill', '/F', '/IM', 'POWERPNT.EXE'], capture_output=True)

# 或保存到新文件名再替换
prs.save(tmp_path)
os.remove(original_path)
os.rename(tmp_path, original_path)
```

### 5. 强制确认关口（TTS 前让人过一眼）

TTS 是返工成本最高的步骤（改旁白 → 重生成音频 → 重生成 SRT → 重烧录，全链路重做）。**生成音频前**，以下两项必须让用户过目确认，不确认不进 TTS：

| 关口 | 确认内容 | 为什么 |
|------|---------|--------|
| ① 旁白脚本 | 每段 text 与 PPT 页一一对应、无脑补、时长合理 | 旁白错了，音频+字幕全白做 |
| ② 人名去敏化映射表 | `NAME_MAP` 覆盖报告中全部真实人名 | 漏一个名字 = 隐私泄露 + 全流程重做 |

> 机器验证（文件存在/时长匹配）挡不住"内容错了"，人审确认挡得住。

## 环境依赖

| 依赖 | 用途 | 安装 |
|------|------|------|
| `markitdown[all]` | PDF/DOCX 文本提取（首选） | `pip install markitdown[all]` |
| `pymupdf` | PDF 页面渲染（OCR 备选） | `pip install pymupdf` |
| `pytesseract` + tesseract.js bridge | 中文 OCR | 已通过 `ocr-pdf-images` skill 配置 |
| `pptxgenjs` (Node.js) | PPT 创作 | `npm install pptxgenjs` |
| `python-pptx` | PPT 文本提取 | `pip install python-pptx` |
| `edge-tts` | AI 语音合成（备选，在线） | `pip install edge-tts` |
| `qwen-tts` | AI 语音合成（推荐，本地含声音克隆） | `pip install -U qwen-tts` |
| `ffmpeg` | 视频编码、字幕烧录、水印叠加 | 见下方 ffmpeg 安装说明 |
| PowerPoint (COM) | 幻灯片导出 PNG | Windows 自带 Office |

## ffmpeg 安装说明（按需加载）

> 见 `references/env-setup.md`。正常流程不需要读，用到时再加载。
## Step 1: PDF 文本提取 — 两条路径

### 路径 A：markitdown（文字型 PDF）

```bash
markitdown 事故报告.pdf -o report.md
```

若 `report.md` 为空或仅数行 → 报告是扫描版，走路径 B。

### 路径 B：pymupdf + pytesseract（图像型 PDF）

```python
import fitz, pytesseract, io
from PIL import Image

doc = fitz.open("accident.pdf")
with open("report_ocr.md", "w", encoding="utf-8") as f:
    for i in range(len(doc)):
        pix = doc[i].get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes('png')))
        text = pytesseract.image_to_string(img, lang='chi_sim+eng')
        f.write(f'## 第{i+1}页\n\n{text}\n\n---\n\n')
doc.close()
```

> `pdf2image` 需要 poppler，Windows 上不可用。pymupdf 是零依赖替代。

## Step 2: PPT 课件制作 — pptxgenjs

使用 Node.js pptxgenjs 创建 12 页 16:9 课件，暗色主题 + 红色警示色调。

**关键教训：**

```javascript
// ❌ Git Bash 下 set NODE_PATH=xxx 不生效
// ✅ 必须用 bash export 语法
NODE_PATH="C:/path/to/node_modules" node create_ppt.js

// ❌ 中文引号破坏 JS 语法
"衢州巨化"9·4"事故"   // SyntaxError
// ✅ Unicode escape
"衢州巨化\u201C9\u00B74\u201D事故"

// ❌ 3 位颜色码不被支持
color: "555"   // 静默降级为 "000000"
// ✅ 始终用 6 位 hex
color: "868E96"
```

**Windows Unicode 路径下的 pptxgenjs 运行方式**：

```python
# ✅ 用 Python subprocess 启动 Node.js，设置 NODE_PATH 环境变量
# 避免 Git Bash/PowerShell 对中文路径的展开问题
import subprocess, os
env = os.environ.copy()
env['NODE_PATH'] = '~/.workbuddy/.workbuddy/binaries/node/workspace/node_modules'
subprocess.run([node_exe, js_path, pptx_path], cwd=work_dir, env=env)
```

**PPT 结构模板**（12 页，~7-8 分钟）：
1. 标题页（暗色） 2. 事故概览 3. 装置背景 4. 时间线
5. 直接原因 6-8. 根因分析 9. 追责 10. 教训 11. 防范措施 12. 结语（暗色）

### ⚠️ titleSlide 布局参数 — 防文本重合

`titleSlide` 函数中 subtitle 和 desc 的 y 坐标必须留有足够间距。**默认值已修正**：

```javascript
function titleSlide(title, subtitle, desc) {
    // Title:  y=1.2, h=1.5 → 结束于 2.7
    // Subtitle: y=2.8, h=0.8 → 结束于 3.6
    // Desc:    y=3.8, h=1.2 → 结束于 5.0
    // Accent:  y=5.1
    // 间距: title→subtitle 0.1", subtitle→desc 0.2"
    s.addText(title,    { y: 1.2, h: 1.5, ... });
    s.addText(subtitle, { y: 2.8, h: 0.8, ... });  // 如果存在
    s.addText(desc,     { y: 3.8, h: 1.2, ... });  // ⚠️ y=3.5 会与 subtitle 重叠！
}
```

> **教训**：隆莱项目末尾页 subtitle（"— 江西隆莱生物制药…—"）与 desc 重合。根因是 desc 的 y 从 3.5 移到 3.8 时才留下足够间距。subtitle 在 y=2.8 结束于 y=3.6，desc 从 y=3.8 开始 → 0.2" 间距刚好。若 desc 行数多（≥4 行），h 保持 1.2 不变。

## PPT 设计规范与优化体系（按需加载）

> 见 `references/ppt-design.md`。正常流程不需要读，用到时再加载。
## Step 3: 旁白脚本

格式：
```json
[{"slide": 1, "text": "大家好..."}, {"slide": 2, "text": "..."}]
```

**规则**：
- 正式培训风格，中文约 5 字/秒估算时长
- 每段 15-30 秒
- 旁白必须与 PPT 实际内容一一对应，不可脑补
- 包含口语衔接（"接下来我们看...""总结一下..."）

## Step 4: TTS 配音 — 双引擎（Qwen3-TTS + edge-tts）

### 引擎选择速查

| 引擎 | 运行方式 | 音色数 | 声音克隆 | 适用场景 |
|------|---------|--------|---------|---------|
| **Qwen3-TTS**（推荐） | 本地 | 5 预设 + 克隆 | ✅ 支持 | 离线/批量/定制化音色 |
| **edge-tts**（备选） | 在线 | 6+ 推荐 | ❌ 不支持 | 快速/临时/零配置 |

### TTS 音色与批量生成（按需加载）

> 见 `references/tts.md`（预设音色/声音克隆/edge-tts 音色/批量生成脚本）。
## Step 5: 幻灯片导出 PNG — Python win32com (推荐)

⚠️ **PowerShell 脚本编码陷阱**：UTF-8 写的 .ps1 通过 `-File` 执行时，含 Unicode（中文）的路径会被 ANSI 编码破坏 → 文件导出到错误位置甚至不导出。

**✅ 推荐：Python win32com 直接操作 COM**

```python
from win32com import client
import pythoncom

pythoncom.CoInitialize()
ppt = client.Dispatch('PowerPoint.Application')
ppt.Visible = 1   # 必须可见，Export 才能工作
pres = ppt.Presentations.Open(pptx_path, True, False, False)
for i in range(1, pres.Slides.Count + 1):
    out_path = os.path.join(slides_dir, f'slide_{i:02d}.png')
    pres.Slides.Item(i).Export(out_path, 'PNG', 1920, 1080)
pres.Close(); ppt.Quit()
pythoncom.CoUninitialize()
```

> **教训**：含中文路径时，Python win32com 通过 pywin32 直接走 COM 接口，路径不经过 shell 转码，零编码问题。PowerShell 的 `-File` 参数对 UTF-8 文件默认用 ANSI 解码，中文路径必然损坏。

## Step 6: SRT 字幕生成（精确同步）

### ⚠️ 核心原则：字幕必须与语音精确对齐

**❌ 错误做法**：每页旁白按持续时间等分拆字幕 → 字幕与语音完全不对齐。

**✅ 正确做法**：

| TTS 引擎 | 字幕同步方案 |
|----------|-------------|
| **edge-tts** | 捕获 `SentenceBoundary` 事件 → 句子级时间戳（精确） |
| **Qwen3-TTS** | 预估语速 5 字/秒 → 按字数比例分配 + `ffprobe` 实测时长修正 |
| **Qwen3-TTS（需精确时）** | 本地 ASR 转写 → 词级时间戳（见下方补强方案） |

### Qwen3-TTS 精确字幕：ASR 词级时间戳补强

Qwen3-TTS 不返回句子时间戳，默认"预估 5 字/秒"方案字幕与语音存在偏差。**当字幕精度要求高**（逐词对齐/字幕带时间轴后制）时，对 Qwen3 生成的音频再跑一遍本地 ASR，拿词级时间戳生成 SRT：

```python
# faster-whisper 词级时间戳 → 精确 SRT（需 pip install faster-whisper）
from faster_whisper import WhisperModel
model = WhisperModel("small", device="cpu", compute_type="int8")
segments, _ = model.transcribe("audio/slide_01.mp3", language="zh",
                               word_timestamps=True)
for seg in segments:
    for w in seg.words:      # w.start / w.end = 词级时间戳（秒）
        pass                 # 按词聚合回句子 → 生成 SRT 时间轴
```

> **原理**：把 Qwen3 输出的音频喂回 ASR，按实际发音重新对齐时间轴，绕开"预估语速"的累计误差。edge-tts 已有 `SentenceBoundary`，无需此步。**这是可选补强，默认流程仍用预估语速方案**（避免额外依赖）。

### edge-tts SentenceBoundary（精确同步）

> ⚠️ `SubMaker.cues` 返回 `Subtitle` **对象**（不是 tuple），文本属性是 `.content`（**不是 `.text`**）。用 `item.start.total_seconds()` / `item.content`，勿解包、勿用 `.text`。

> 代码片段见 `references/code-snippets.md`（edge-tts SentenceBoundary 脚本）。

### ⚠️ SRT 偏移必须用 clip 实际时长，不能用音频时长

```python
# ❌ 用音频时长累加偏移 → 视频 426s，SRT 只到 400s
slide_offsets = accumulate(audio_durations)

# ✅ 用 ffmpeg 实测各 clip 的实际时长做偏移
clip_durs = [get_duration(f"clips/clip_{i:02d}.mp4") for i in range(1,13)]
slide_offsets = accumulate(clip_durs)
```

> 根因：`-loop 1 -shortest` 生成的 clip 比音频长约 2s（静态图在音频结束后多停留），视频总长 426s ≠ 音频总长 400s。

### SRT 样式控制：force_style

```python
# ⚠️ SRT 默认字体偏大、位置偏高，遮挡 PPT 内容
# ✅ 用 force_style 控制：小字号、贴底端
# Fontsize=14（1080p 培训视频不易遮挡正文）
# MarginV=2（越小越贴底，0~2 即可）
# Alignment=2（底部居中）
vf = "subtitles=subtitles.srt:force_style='Fontsize=14,MarginV=2,Alignment=2,Outline=1,Shadow=1'"
```

> **MarginV 方向注意**：ffmpeg subtitles filter 的 `MarginV` 是离底部边距，**值越小字幕越靠下**。MarginV=70 反而上移，MarginV=2 才是贴底。

每段字幕 ≤22 字/行，≤2 行（1080p 培训视频）。

## Step 7: 视频合成（两步法）

> ⚠️ **ffmpeg 必须用绝对路径**：Python subprocess 裸 `ffmpeg` 会 `FileNotFoundError`（PATH 继承不一致）。用 `~/.workbuddy/binaries/ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe`，或读 `references/env-setup.md` 的 `get_ffmpeg()` / `references/pitfalls.md` 0h 节。

### 第一步：逐段生成 clip

```python
ffmpeg -y -loop 1 -i slide_XX.png -i audio/slide_XX.mp3 \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p" \
  -c:v libx264 -preset fast -crf 22 -pix_fmt yuv420p -r 24 \
  -c:a aac -b:a 192k -ar 44100 -ac 2 \
  -shortest clip_XX.mp4
```

### 第二步：合并 clip（`-c copy`，极快）

```bash
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy video_merged.mp4
```

⚠️ **合并后必须验证时长**：用 `ffmpeg -i video_merged.mp4 2>&1 | grep Duration` 检查总时长是否等于所有 clip 之和。如不符 → concat 列表编码有问题（见 0e 节）。

### ⚠️ 第三步：烧录字幕 — 关键教训

> 代码片段见 `references/code-snippets.md`（烧录字幕关键教训（路径/faststart））。

## Step 8: 验证

```bash
# 验证视频完整性
ffmpeg -v error -i output.mp4 -f null -
# 静默输出 = OK；任何错误 = 文件损坏
```

### 最终视频命名规范

**格式**：`在事故教训中成长-{去敏化后的PPT首页标题}.mp4`

**规则**：
- 前缀固定：`在事故教训中成长-`
- 后半部分 = PPT 首页的事故名称（已去敏化，含公司名和事故类型）
- 特殊字符保留原样（如 `·`、`"`），Unicode 文件名在现代 OS 上完全支持

**示例**：

| 报告原标题 | 最终视频名 |
|-----------|-----------|
| 山西XX建材有限公司"1·13"爆炸事故调查报告 | `在事故教训中成长-山西XX建材有限公司"1·13"爆炸事故调查报告.mp4` |
| 内蒙古利元科技"3·19"爆炸事故报告 | `在事故教训中成长-内蒙古利元科技"3·19"爆炸事故报告.mp4` |
| 重庆鹏凯精细化工"4·23"压力容器爆炸事故 | `在事故教训中成长-重庆鹏凯精细化工"4·23"压力容器爆炸事故.mp4` |

```python
# 命名实现
final_name = f"在事故教训中成长-{ppt_title_anonymized}.mp4"
```

## Step 9: 人名去敏化（全流程）

事故报告中包含大量真实人名，为避讳和隐私保护，**从 PPT 到旁白到字幕**必须统一替换为匿名。

### 替换规则

| 原名字数 | 替换模式 | 示例 |
|----------|----------|------|
| 3 字 | X某某 | 王文祺 → 王某某、李军生 → 李某某 |
| 2 字 | X某 | 果伟 → 果某、孙庆 → 孙某 |

### 实现：先建映射表，再重建全流程

```python
NAME_MAP = {
    "王文祺": "王某某", "果伟": "果某", "李军生": "李某某",
    "徐永辉": "徐某某", "王海东": "王某某", "唐奇伟": "唐某某",
    "孙庆": "孙某", "王琦": "王某", "王毅": "王某",
}

def anonymize(text):
    for orig, anon in NAME_MAP.items():
        text = text.replace(orig, anon)
    return text

# 应用到 PPT 文本（create_ppt.js 中的全部文字）
# 应用到旁白文本（narration 中的每个 slide.text）
# → 重新生成 TTS + SRT + 烧录
```

### ⚠️ 去敏后必须做的事

去敏修改了旁白文本 → TTS 音频需要**重新生成** → SRT 需要重新**从 SentenceBoundary 生成** → 字幕需要**重新烧录**。不能只改 SRT，否则字幕和语音不匹配。

## Step 10 迭代优化 P0-P3（按需加载）

> 见 `references/optimization.md`。正常流程不需要读，用到时再加载。
## Step 11: 收尾清理

视频产出后，清理中间产物和工具操作产生的垃圾目录。

### 清理 video_work 目录

保留成品视频（已复制到报告目录），`video_work/` 可选择保留或删除：

| 保留策略 | 操作 |
|----------|------|
| **全保留** | 不删。适合后续要调字幕/水印/画质的场景（从母版 `video_merged.mp4` 重新派生） |
| **仅保留母版** | 只保留 `video_merged.mp4`，删 `clips/`、`audio/`、`slides/` 等可重建的中间文件 |
| **全清除** | `shutil.rmtree(work_dir)` |

```python
# 保留母版的最小清理
keep = ['video_merged.mp4', 'subtitles.srt', 'output.pptx', 'create_ppt.js']
for item in os.listdir(work_dir):
    if item not in keep:
        path = os.path.join(work_dir, item)
        if os.path.isfile(path): os.remove(path)
        else: shutil.rmtree(path)
```

### ⚠️ 清理 Unicode 引号路径导致的幽灵目录

当报告路径包含全角引号（如 `"12·31"`），某些工具（Write、mkdir）可能将 `"`（U+201C）和 `"`（U+201D）误解析为路径分隔符，在**上级目录中创建一个短名的幽灵目录**：

```
# 正确目录：
7-南昌进贤江西隆莱生物制药有限公司"12·31"较大窒息事故调查报告/

# 幽灵目录（同时出现）：
7-南昌进贤江西隆莱生物制药有限公司/
  ├── u201c12·31/
  │   └── u201d较大窒息事故调查报告/
  │       └── video_work/  ← 空的！
  └── video_work/          ← 也是空的！
```

**排查和清理**：

> 代码片段见 `references/code-snippets.md`（幽灵目录清理脚本）。

> **教训**：隆莱项目的报告路径含 `"12·31"`（全角引号），Write 工具写入 `create_ppt.js` 时在上级目录创建了幽灵目录，内部分裂为 `u201c12·31/u201d较大窒息事故调查报告/video_work/`。此目录空无一物，但容易被误认为有效工作目录。

## 维护记录

完整维护记录见 `references/changelog.md`（v2.4.0 卸载，按需加载）。最近变更：v2.4.1（看图前提补记，见 references/pitfalls.md 第 28 节）。

## 复盘经验总结 + 常见坑位速查

> ⚠️ 本章节已分层卸载至 `references/pitfalls.md`（低频内容，按需加载）。
>
> **什么时候读**：
> - 遇到具体报错/坑位时 → 读 `references/pitfalls.md`「常见坑位速查」表格（50+ 条速查）
> - 做迭代复盘、想知道"上次踩了什么坑"时 → 读「复盘经验总结」12 个子章节
> - 需要像素统计法验证字幕/水印渲染时 → 读文末「像素统计法」
>
> 正常执行 Step 1-11 流程**不需要**读此文件。

