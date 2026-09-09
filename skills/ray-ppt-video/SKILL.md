---
name: ray-ppt-video
slug: ray-ppt-video
displayName: PPT转培训视频
version: 2.7.0
description: Use when converting a technical training PPTX into a narrated training video. Triggers: "PPT转视频", "生成培训视频", "PPT to training video", "课件转视频", or any request to turn slide decks into MP4 videos with AI voiceover and subtitles.
agent_created: true
---

# ray-PPT-TrVideo — PPT 转培训视频

将技术培训 PPTX 自动化转换为带 AI 配音 + 同步字幕的 MP4 培训视频。

---

## ⚠️ 核心原则：以 PPT 为纲，紧扣主线展开（最高优先级）

> **这是本 skill 最重要、最不可妥协的规则。任何违反此原则的输出均为不合格产品。**

### 正确理解「一致性」

旁白与 PPT 的一致性，**不是照本宣科逐字朗读** PPT 上的文字，而是：

```
PPT内容的文字
    ↓
作为讲解的骨架和主线     ← 旁白的边界，不可越界
    ↓
进行合理的展开和阐释     ← 讲师的发挥空间
    ↓
始终服务于对 PPT 内容的深化解读
```

| ✅ 正确的做法（讲解） | ❌ 错误的做法 |
|------|------|
| 用更口语化的语言转述 PPT 要点 | 逐字逐句朗读 PPT 原文 |
| 对 PPT 上的要点做 1-2 句补充解释 | 添加 PPT 上没有的新话题、新案例 |
| 为 PPT 中的流程图/数据做口头串联 | 根据主题自由发挥一段"即兴演讲" |
| 将 PPT 上的术语/缩写做简单说明 | 偏离 PPT 主线去讲"相关但没写在 PPT 上的知识" |

### 边界判断标准

旁白是否合格的唯一标准：**听众看到 PPT 画面 + 听到旁白时，能否感受到二者是紧密配合的**——旁白在解释画面上的内容，画面是旁白在讲的事。

- 把旁白文本盖住，只看 PPT 画面 → 能猜到旁白大概在讲什么 → ✅ 合格
- 把 PPT 画面盖住，只听旁白 → 讲的内容和 PPT 页面对不上 → ❌ 跑题
- 旁白中出现了 PPT 上没有的人名、地名、数据、案例 → ❌ 越界

### 硬性规则

| 规则 | 说明 |
|------|------|
| **以 PPT 为纲** | 每页PPT的标题和要点即为该页旁白的骨架，不可脱离 |
| **可阐释不可越界** | 允许对 PPT 上的要点做口语化转述和简短补充，不允许引入 PPT 之外的主题、数据或案例 |
| **以 PPT 术语为准** | 若 PPT 上的术语/流程表述与通用说法不一致，**以 PPT 的表述为准** |
| **发现偏离即停** | 旁白稿抽样检查中若发现任一页偏离了 PPT 主线，**必须立即停止，整批重新生成** |
| **图片页必须确认** | 含图片/截图的页面必须导出 PNG 查看后写旁白，无法识别则暂停向用户报告 |

### 执行流程

```
1. 提取 PPT 每页原始文本（标题 + 正文 + 图表标题），这是旁白的骨架
2. 逐页生成旁白：以该页PPT要点为纲，用口语化表述展开阐释（每要点1-2句补充）
3. 图片页特殊处理：导出 PNG 后逐张查看确认内容，无法识别则暂停任务向用户报告
4. 一致性校验：每页核对——旁白讲了PPT上没有的主题？→ 不合格；旁白跳过了PPT上的关键要点？→ 不合格
5. 不合格 → 返回步骤 2 重新生成；合格 → 继续 TTS
```

### 图片页识别规则

- 纯文字页：优先使用提取的文本内容生成旁白
- 含图片/截图/表格的页面：必须**导出 PNG 后逐张查看**，确认内容再写旁白
- 图片无法识别时：**必须暂停任务**，告知用户哪些图片无法识别，建议请用户提供文字说明
- **严禁**根据 PPT 标题"脑补"图片内容

---

## ⚠️ 时长确认铁律（2026-09-04 用户明确要求）

> **视频时长不是硬指标，是「估算→确认」流程。用户未确认前不得为凑时长返工。**

流程：
1. **估算先行**：旁白稿写完后，按字数估算时长（edge-tts zh-CN-YunjianNeural +5% ≈ 300字/min），向用户报告「预计 X 分钟」
2. **确认后再做**：TTS 前把估算时长告诉用户，得到确认（如「18.85 分钟可以的」）才开始配音
3. **禁止自动重调语速凑时长**：成品与用户确认值差 1-2 分钟属正常波动，**绝不为凑整数（如 20 分钟）自动改 `--rate` 重跑**——这会部分覆盖已完成音频、破坏一致性（2026-09-04 实证：误启 -8% 重生成 → 音频混合损坏 → 全量重做 4 分钟 + 重合成 10 分钟的无用功）
4. **用户说「X 分钟可以的」= 锁定该时长**，后续任何操作只以恢复/保持该版本为目的

| 错误做法 | 正确做法 |
|------|------|
| 目标 20 分钟，做出 18.85 → 自动减速重跑 | 18.85 ≈ 20，报告用户即可 |
| 用户确认后仍"顺手优化"语速 | 确认后时长冻结，不再碰 TTS 参数 |
| 重跑前不清点已完成产物 | 重跑会覆盖！先确认是否真的需要重跑 |

---

## 流程概览

```
PPTX → 提取文本 → 导出幻灯片 PNG → 生成旁白稿 → 估算时长→用户确认 → TTS 配音 → SRT/ASS 字幕 → FFmpeg 合成 MP4
```

**双引擎 TTS**:
- **Qwen3-TTS**（推荐）：阿里通义千问开源模型，本地运行，支持**声音克隆** + 9 种预设音色
- **edge-tts**（备选）：微软在线服务，6 种预设音色，需联网

**v2.0 新特性** (2026-07-08):
- 🎙️ Qwen3-TTS 双引擎 + 声音克隆
- 🔒 流水线进程锁（防止并发冲突）
- ⏯️ TTS 断点续传 + 单句重生成
- 🔍 一键环境检查 (`check_environment.py`)
- ✅ 输入文件校验 (`validate_inputs.py`)
- 📝 发音规范化引擎（路径/术语/数字 TTS 优化）
- 🎨 ASS 字幕 + 软字幕支持
- 🔧 FFmpeg 滤镜能力自动检测

---

## 环境依赖

| 依赖 | 用途 | 安装方式 |
|------|------|----------|
| `python-pptx` | 提取 PPT 文本 | `pip install python-pptx` |
| PowerPoint (COM) | 导出幻灯片为高清 PNG | Windows 自带 Office |
| `qwen-tts` | AI 语音合成（推荐） | `pip install -U qwen-tts` |
| `edge-tts` | AI 语音合成（备选） | `pip install edge-tts` |
| `imageio-ffmpeg` | 视频编码（自带二进制） | `pip install imageio-ffmpeg` |

### 环境缺失处理指南（v2.2 新增）

运行 `check_environment.py` 发现缺失时，按下表处理：

| 缺失项 | 处理方式 |
|--------|---------|
| `ffmpeg` / `imageio-ffmpeg` 无法定位 | **Windows**：https://www.gyan.dev/ffmpeg/builds/ → 下载 `essentials_build` → 解压 → 将 `bin/` 加入 PATH 或用 `--ffmpeg` 显式指定路径。**Linux**：`sudo apt install ffmpeg` / `brew install ffmpeg` |
| `edge-tts` 安装失败（国内网络） | `pip install edge-tts==7.2.8 -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| `qwen-tts` 安装失败 | `pip install -U qwen-tts -i https://pypi.tuna.tsinghua.edu.cn/simple` |
| 任何 pip 包安装失败 | 统一追加国内镜像：`-i https://pypi.tuna.tsinghua.edu.cn/simple` 重试 |
| Qwen3-TTS 模型下载慢 | `export HF_ENDPOINT=https://hf-mirror.com` |

### 一键环境检查

```bash
python scripts/check_environment.py        # 检查所有依赖
python scripts/check_environment.py --fix  # 自动安装缺失项
```

---

## 快速开始

### 一键运行

```bash
python scripts/trvideo.py training.pptx
```

### 指定 TTS 引擎和音色

```bash
# Qwen3-TTS 预设音色（推荐，本地运行）
python scripts/trvideo.py training.pptx --tts-engine qwen3 --speaker Vivian

# Qwen3-TTS 声音克隆（提供参考音频，5-15 秒人声）
python scripts/trvideo.py training.pptx --tts-engine qwen3 --reference-voice voice.wav

# edge-tts 在线音色
python scripts/trvideo.py training.pptx --tts-engine edge --voice zh-CN-YunjianNeural
```

### 完整参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--tts-engine` | `auto` | TTS 引擎：`auto`/`qwen3`/`edge` |
| `--voice` | `zh-CN-YunjianNeural` | edge-tts 语音 |
| `--speaker` | `Vivian` | Qwen3-TTS 预设音色 |
| `--reference-voice` | — | 参考音频（Qwen3-TTS 声音克隆） |
| `--instruct` | — | Qwen3-TTS CustomVoice 指令 |
| `--subtitle-mode` | `burn` | 字幕模式：`burn`/`soft`/`both` |
| `--regenerate` | — | 重生成指定 slide 编号 |
| `--skip-steps` | — | 跳过指定步骤 (1-6) |
| `--resume-from` | — | 从第 N 步续跑（自动跳过 1~N-1，v2.2 新增）|
| `--output` / `-o` | — | 输出 MP4 路径 |

### 可用音色

**Qwen3-TTS 预设音色**:

| 音色 | 描述 |
|------|------|
| Vivian | 明亮的年轻女声（默认） |
| Serena | 温暖、温柔的年轻女声 |
| Uncle_Fu | 成熟的男性声音，醇厚音色 |
| Dylan | 年轻的北京男声 |
| Eric | 活泼的成都男声 |

**edge-tts 推荐语音**:

| 语音 | 描述 |
|------|------|
| zh-CN-YunjianNeural | 云健（男，沉稳大气） |
| zh-CN-YunxiNeural | 云希（男，年轻阳光） |
| zh-CN-XiaoxiaoNeural | 晓晓（女，温暖自然） |
| zh-CN-YunyangNeural | 云扬（男，新闻播报） |
| zh-CN-XiaoyiNeural | 晓伊（女，亲切活泼） |

---

## 执行步骤

### Step 1: 提取 PPT 文本内容

```powershell
python -X utf8 -c "
from pptx import Presentation
prs = Presentation('input.pptx')
for i, slide in enumerate(prs.slides):
    for shape in slide.shapes:
        if shape.has_text_frame:
            txt = shape.text_frame.text.strip()
            if txt: print(txt)
"
```

### Step 2: 导出幻灯片为 PNG

**必须使用 PowerShell COM 调用 PowerPoint**——Windows 上保真度最高的方案：

```powershell
$pptPath = "完整路径\input.pptx"
$outDir = "slides"
$pp = New-Object -ComObject PowerPoint.Application
$pp.Visible = 1
$pres = $pp.Presentations.Open($pptPath, $true, $false, $false)
for ($i = 1; $i -le $pres.Slides.Count; $i++) {
    $slide = $pres.Slides.Item($i)
    $outFile = Join-Path $outDir ("slide_{0:D2}.png" -f $i)
    $slide.Export($outFile, "PNG", 1920, 1080)
}
$pres.Close(); $pp.Quit()
```

分辨率: 1920×1080，与最终视频一致，避免二次缩放失真。

### Step 3: 生成旁白稿（严格对齐 PPT 内容）

这是整个流程中最容易出错、也最关键的环节。

#### 3.1 先看 PPT 实际内容，再写旁白

1. 读取提取的原始文本，**逐页列出标题、正文和关键图表**。
2. 旁白应解释"这页 PPT 上写了什么"，不能凭主题自由发挥。
3. 如果 PPT 上出现的术语、方法名称与通用知识不一致，**以 PPT 为准**。

#### 3.2 图片页必须人工识别，不可臆造

- 纯文字页：优先使用提取的文本内容生成旁白。
- 含图片/截图/表格的页面：必须**导出 PNG 后逐张查看**，确认内容再写旁白。
- 图片无法识别时：**必须暂停任务**，告知用户哪些图片无法识别，建议使用更强模型或请用户提供文字说明。
- **严禁**根据 PPT 标题"脑补"图片内容。

#### 3.3 输出格式

旁白 JSON（`narration.json`） 支持扩展字段：

```json
[
  {"slide": 1, "text": "大家好，欢迎参加本次培训...",
   "tts_text": "大家好，欢迎参加本次培训..."},
  {"slide": 2, "text": "首先，让我们进入第一部分..."}
]
```

- `text`: 用于字幕显示的原始文本
- `tts_text`（可选）: 发音规范化后的 TTS 文本。不填时自动由 `scripts/pronunciation.py` 生成，处理路径口语化（`~/.codebuddy/` → "家目录下 codebuddy"）、术语映射（`HAZOP` → "哈扎普"）和数字读法。

---

### Step 4: 批量 TTS 配音

```bash
# Qwen3-TTS 预设音色（默认）
python scripts/generate_tts.py narration.json audio/ --tts-engine qwen3 --speaker Vivian

# Qwen3-TTS 声音克隆
python scripts/generate_tts.py narration.json audio/ --tts-engine qwen3 --reference-voice voice.wav

# edge-tts 在线
python scripts/generate_tts.py narration.json audio/ --tts-engine edge --voice zh-CN-YunjianNeural

# edge-tts 控制语速（时长微调）：--rate=-10% 减速约10%，--rate=+5% 加速
# 实测参考（zh-CN-YunjianNeural）：+0%≈284字/min，-5%≈270字/min，-10%≈255字/min
python scripts/generate_tts.py narration.json audio/ --tts-engine edge --rate=-10%

# 重新生成指定幻灯片
python scripts/generate_tts.py narration.json audio/ --regenerate 1 3 5
```

> **注意**：`--rate` 参数值以 `-` 开头时必须用等号形式 `--rate=-10%`，否则 argparse 会误判为选项。默认 `+5%`（与历史版本一致）。控制总时长可先测 2-3 页实际字/分钟再换算：`目标字/分钟 = 总字数 ÷ 目标分钟数`。

**特性**:
- 🔒 进程锁：同一输出目录只允许一个 TTS 实例运行
- ⏯️ 断点续传：已有音频自动跳过，中断后继续
- 🔄 引擎一致性：切换 TTS 引擎自动清理旧音频
- 🎯 单句重生成：`--regenerate` 精确指定重生成 slide

### Step 5: 生成字幕

```bash
python scripts/generate_srt.py narration.json audio/ output.srt
```

自动生成 SRT 字幕，从音频文件精确获取时长。

### Step 6: FFmpeg 合成视频

```bash
python scripts/assemble_video.py narration.json slides/ audio/ subtitles.srt output.mp4

# 软字幕模式（字幕可开关）
python scripts/assemble_video.py ... --subtitle-mode soft

# 双字幕（硬烧录 + 软字幕）
python scripts/assemble_video.py ... --subtitle-mode both
```

**两步法**（内存友好）:
1. 逐段生成 slide clip（幻灯片 + 音频）
2. 合并所有 clips + 烧录/附加字幕

**字幕模式**:
| 模式 | 说明 |
|------|------|
| `burn` | 硬字幕，烧录到视频流（默认） |
| `soft` | 软字幕，mov_text 独立轨道（播放器可开关） |
| `both` | 同时输出硬字幕和软字幕版本 |

---

## ⚠️ 英文视频场景（English deck → English video，2026-09-03 血泪沉淀）

> 源 PPT 与配音都是英文时（如 Rianlon 马来西亚新员工 EHS 培训），**默认走英文专用脚本链**，不要直接套用中文步骤。以下 4 条是本场景踩过的坑，违反任何一条都会出问题。

### E1. 英文字幕必须用 `tts_srt_en.py`（句子级精确时间轴）

**坑**：skill 自带 `generate_srt.py`/`assemble_video.py` 内部字幕只按**中文标点**（`。！？；`）拆分，英文句号不拆 → 字幕整段超长遮挡。
**根因**：edge-tts 7.2.8 只有 `SentenceBoundary`（句子级 offset+duration），**无 WordBoundary**；`Communicate.save()` 完全不返回边界。
**解法**：`scripts/tts_srt_en.py` —— 实时 stream 收集 SentenceBoundary，按真实语音句子切字幕，误差 <50ms：

```bash
# 同时生成 TTS 音频 + 精确字幕（音频可复用，TTS 可重复）
python scripts/tts_srt_en.py narration.json audio_en/ subtitles_en.srt
# 只出字幕不重写音频（音频已有时）
python scripts/tts_srt_en.py narration.json audio_en/ subtitles_en.srt --srt-only
# 指定语速/音色（--rate 负数须用等号形式，如 --rate=-15%）
python scripts/tts_srt_en.py narration.json audio_en/ subtitles_en.srt --rate=-10% --voice en-US-JennyNeural
```
> 默认 `-15%`（约 127 wpm，自然讲解节奏）。选语速前先测：取 45 词旁白试听，目标 125-145 wpm 对非母语听众友好。

### E2. 字幕烧录必须用 ASS 文件（禁 force_style）

**坑**：`subtitles` 滤镜 + `force_style='MarginV=24,Alignment=2'` 在部分 ffmpeg build **不生效** → 字幕渲染到**画面中部**叠 PPT 内容（用户连续 2 次反馈"字幕挡内容"）。
**解法**：SRT → ASS（MarginV=18 贴底、FontSize=19、BorderStyle=4 半透明黑底、事件间加 50ms gap 防同帧闪烁），用 `ass=` 滤镜烧：

```bash
python scripts/reburn_subs_en.py clean_nosub.mp4 subtitles.ass output_FINAL.mp4
```
> `reburn_subs_en.py` 自动识别 .ass 输入走 ass 滤镜，.srt 走 force_style。

### E3. 🚨 禁止在带字幕的视频上重烧字幕（叠层！）

**坑**：每次"重烧修复"都在**已带字幕的视频**上再叠一层 → 旧字幕 + 新字幕两层共存（用户反馈"上面一处大字、底部一处小字"）。浪费 ~1.5h 才定位。
**铁律**：烧字幕必须从**无字幕母版**开始。母版用 `build_clean_en.py` 从原始素材重建：

```bash
python scripts/build_clean_en.py narration.json slides/ audio_en/ clean_nosub.mp4
# 然后
python scripts/reburn_subs_en.py clean_nosub.mp4 subtitles.ass FINAL.mp4
```

### E4. 验证单层字幕：像素带对比法

母版 vs FINAL 同帧逐带对比（PIL ImageChops.difference），差异带**应只在底部字幕区**（y 950-1080），中部零差异 = 单层确认。避免靠 VL/OCR 猜（会把 PPT 自身文字误当字幕）。

ASS 字幕同时生成，提供更丰富的排版样式。

---

## 编码参数速查

| 参数 | 值 | 说明 |
|------|-----|------|
| 分辨率 | 1920×1080 | 16:9 标准 |
| 帧率 | 24 fps | 幻灯片足够 |
| 视频编码 | libx264, CRF 21 | 高质量 |
| 音频编码 | AAC 192kbps | — |
| 采样率 | **44100 Hz** | 关键！TTS 默认 24kHz 需重采样 |
| 声道 | **stereo (2)** | 关键！默认 mono 音质差 |
| 字幕字号 | FontSize=32 | 1080p 清晰可读（v2.7.0 由 24 调大，用户实测 24 偏小）；搭配分段显示不遮挡 |
| 字幕位置 | Alignment=2 | 底部居中 |
| 字幕字体 | Microsoft YaHei | Windows 默认中文字体 |
| 字幕底部边距 | MarginV=60 | 增大边距，避免遮挡底部内容 |

### 字幕分段显示策略（v2.1）

> 2026-07-08 新增：解决字幕一次性显示过多文字遮挡PPT的问题

**问题**：原方案每页旁白作为一个字幕条目，长页（200+ 字）全部显示在画面中，严重遮挡PPT。

**解决方案**：

| 策略 | 说明 |
|------|------|
| 语义拆分 | 按句号→分号→逗号的优先级逐级拆分，每段 ≤38 字符 |
| 时间分配 | 按字数比例计算每段时间，每段最短 1.5s |
| 行宽控制 | 字幕每行 ≤34 字符，最多 2 行 |
| 总段数参考 | 30 页 19 分钟课件，约生成 220-250 个分段 |

**ASS 硬字幕样式**：
```
FontSize=32, MarginV=60, Outline=2, Shadow=1, BorderStyle=1
```

---

## 发音规范化

`scripts/pronunciation.py` 提供 TTS 发音优化：

**路径转换**:
| 输入 | TTS 输出 |
|------|----------|
| `~/.codebuddy/skills/` | 家目录下 codebuddy skills 目录 |
| `./config/api.md` | 当前目录下 config api点md |

**术语映射** (`config/pronunciation_map.json`):
| 原文 | TTS 读取 |
|------|----------|
| HAZOP | 哈扎普 |
| LOPA | 洛帕 |
| SIL | S-I-L |
| kPa | 千帕 |
| P&ID | 管道仪表图 |
| ... | ... |

支持自定义修改 `config/pronunciation_map.json` 添加化工行业术语。

**数学符号口语化（v2.2 新增）**:
| 输入 | TTS 输出 |
|------|----------|
| `-5` 度 | 负5 度 |
| `5+3` 万吨 | 5加3 万吨 |
| `3×4` 倍 | 3乘4 倍 |
| `5÷2` 倍 | 5除以2 倍 |
| `5/3` MPa | 5除以3 兆帕 |

**多音字标注（v2.2 新增）**:

在旁白文本中用 `字{拼音+声调}` 标记多音字读音，如 `倒{dao3}角`、`重{zhong4}要`。`pronunciation.py` 会自动**剥离标注**，让 TTS 引擎根据上下文发音（edge-tts/Qwen3 均支持上下文推断）。若引擎对个别字仍读错，可在 `pronunciation_map.json` 里加 `"倒角": "dao3角"` 精确纠正。

---

## 输入校验

运行前验证文件格式：

```bash
python scripts/validate_inputs.py --pptx slides.pptx --narration narration.json
python scripts/validate_inputs.py --pptx slides.pptx --narration narration.json --reference-voice voice.wav --strict
```

检查项：PPTX 有效性/页数 | 旁白格式/页数匹配 | 参考音频时长/格式 | 特殊字符 TTS 兼容性

---

## 关键质量红线

> 另有最高优先级的「核心原则：旁白必须与 PPT 内容完全一致」，见文件顶部。

### 音频与字幕质量

---

## 常见问题 / 经验复盘

**按需加载（遇到对应问题再读）**：见 `references/pitfalls.md`——含 7 条 FAQ（采样率/字幕乱码/Windows 路径/遮挡/烧录/模型下载/并发锁）+ 两大经验复盘（字幕优化踩坑 2026-07-08、bash 中文路径乱码致音频静音 2026-07-29，含根因链与诊断速查）。

## 分享前脱敏检查（v2.2 新增）

> **当用户要求「创建分享副本」「发布技能」「脱敏分享」本 skill 时，必须逐项检查，不得跳过。**

### 必须清除的敏感信息

| 检查项 | 关键词/模式 | 替换为 |
|--------|------------|--------|
| 声音克隆参考音频路径 | `reference-voice.*\.wav` | `<你的参考音频路径>` |
| 输出文件中的私有路径 | `E:/LingXi/`、`D:/Work/` 等绝对路径 | `<示例路径>` |
| Qwen 模型密钥/环境变量 | `QWEN_API_KEY` 等含密钥的行 | `<你的KEY>` |
| 用户名目录 | `C:\\Users\\<用户名>`（如用户名出现在脚本硬编码中） | `<用户目录>` |

### 执行步骤

1. **复制 skill 目录**到分享位置（如 `~/.workbuddy/skills/ray-ppt-video-share/`）
2. **逐文件 grep** 敏感片段，确认全部命中位置
3. **替换所有命中**为占位符
4. **删除 `__pycache__/`** 目录（含 .pyc 可能嵌入路径）
5. **再次 grep 验证**零残留
6. 告知用户：「分享副本已就绪，无敏感信息泄露」

> **注意**：不修改原始 skill（保留你的实际配置），只操作分享副本。

---

## 实战经验

- 2026-09-04｜[ERR-20260904-001]｜**未经确认自动重调语速凑时长 → 音频损坏无用功**｜场景：用户要求"20分钟视频"，+5% 语速实际做出 18.85 分钟，我未询问用户直接改 -8% 重跑想凑 20 分钟 → 部分覆盖已完成音频（部分 -8%/部分 0 字节），被迫全量重做｜死路：中断重跑时音频已处于混合状态；二次重跑又扩大损坏｜解法：①rm 全部音频 + 全量 +5% 重生成恢复一致 ②固化为「时长确认铁律」（见流程概览上方）：估算时长→用户确认→才 TTS；确认后时长冻结，禁止为凑整数自动改 --rate｜计数：1｜状态：resolved（已写主流程）
- 2026-09-03｜场景：**英文 PPT 转英文培训视频**｜经验：英文项目**必须走英文专用脚本链**（`tts_srt_en.py` + `build_clean_en.py` + `reburn_subs_en.py`，见上文"英文视频场景"章节）——自带脚本字幕按中文标点拆、force_style 位置不可靠、无句子级时间轴｜来源：Rianlon 48页英文EHS课件→2h28m
- 2026-09-03｜场景：**纯文本模型看 PPT 图片**｜经验：DeepSeek 等看不了 PNG → 用 `ray-ppt-ocr-eyes`（opencode-go qwen3.8-flash 默认）逐页 VL 描述，识别装饰图/信息图，确认无隐藏数据后再写旁白｜来源：同上
- 2026-09-03｜[ERR-20260903-001]｜**禁止在带字幕视频上重烧字幕**（叠层！）｜场景：修复字幕位置/大小，每轮都在已带字幕视频上再烧 → 两层字幕共存（用户反馈"上下各一处字幕"）｜死路：试图在 fixed/v2 视频上继续改＝越改越多层｜解法：必须从无字幕母版（build_clean_en.py 重建）开始，只烧一次｜计数：1｜状态：resolved（已写主流程 E3）
- 2026-09-03｜[ERR-20260903-002]｜**ffmpeg subtitles 滤镜 force_style 的 MarginV/Alignment 不可靠**（浮中部）｜场景：命令行 force_style 设 MarginV=24 想让字幕贴底，实际渲染到画面中部叠 PPT 内容（用户 2 次反馈"字幕挡内容"）｜死路：反复调 MarginV 值无效、怀疑 VL 误读浪费大量验证｜解法：用 ASS 文件（样式写死在文件里）+ `ass=` 滤镜，libass 可靠执行贴底｜计数：1｜状态：resolved（已写主流程 E2）
- 2026-09-03｜[ERR-20260903-003]｜**烧字幕必须验证单层**（像素带对比）｜场景：交付前以为修好了，实际两层字幕叠加未察觉｜解法：母版 vs 成品逐带对比（ImageChops），差异应只在底部字幕带；勿靠 VL/OCR 猜（会把 PPT 自身文字误当字幕）｜计数：1｜状态：resolved（已写主流程 E4）
- 2026-07-30｜场景：Windows环境首次运行｜经验：IMAGEIO_FFMPEG_EXE 需手动设置为ffmpeg.exe路径，脚本不会自动探测PATH；`--ffmpeg`参数需显式传入assemble_video.py｜来源：员工安全知识手册培训.pptx→MP4
- 2026-07-30｜场景：bash+中文文件｜经验：`cd 进入中文目录 + 相对路径调用Python` 在bash下安全，可作为PowerShell（stdout截断）的替代方案；此方法避开了bash命令行参数编码问题｜来源：员工安全知识手册培训.pptx→MP4

---

## 维护记录

完整维护记录见 `references/changelog.md`（v2.5.0 卸载，按需加载）。最近变更：v2.5.0（维护记录卸载至 references）。
