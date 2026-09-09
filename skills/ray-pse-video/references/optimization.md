# Step 10 迭代优化 P0-P3（按需加载）

> 来源：ray-pse-video SKILL.md 分层卸载（v2.2.0）。

## Step 10: 迭代优化（P0→P1→P2）

首版视频产出后，按优先级逐级优化。

### P0 — 画质提升

```python
# 首版用 CRF 22，可升级到 CRF 18（牺牲编码速度换画质）
-c:v libx264 -preset medium -crf 18
```

### P0 — 背景音乐（ffmpeg 合成）

无需下载外部文件，用 ffmpeg 音频合成生成低频氛围音：

```python
dur = 260  # 与视频等长
cmd = [ffmpeg, '-y', '-f', 'lavfi', '-i',
    f'aevalsrc=sin(100*PI*t)*0.12+sin(150*PI*t)*0.08+sin(200*PI*t)*0.06:duration={dur}',
    '-filter_complex', f'lowpass=f=300,aecho=0.8:0.7:60:0.4,afade=t=in:d=4,afade=t=out:st={dur-6}:d=6',
    '-ac', '2', '-ar', '44100', '-b:a', '128k', 'bgm_ambient.mp3']
```

BGM 极低音量混入（避免干扰人声）：

```python
# [1:a]volume=0.06 约为 -25dB
af = '[0:a]volume=1.0[voice];[1:a]volume=0.06[bgm];[voice][bgm]amix=inputs=2:duration=first'
```

### P1 — 时长压缩策略

首版旁白往往偏长（8+ 分钟），浓缩到 4-6 分钟：

| 技巧 | 示例 |
|------|------|
| 删除填充词 | "值得强调的是""首先"→ 直接讲 |
| 合并冗余 | 两个根因共用"三层失效"一页讲完 |
| 精简数字 | "事故造成部分设备、管道等损坏"→ "设备管道损坏" |
| 保留 punchline | "这次没伤亡是运气，不是管理的结果"不可删 |

浓缩后 TTS 重生成 → 重编码。总旁白从 ~460s 可压至 ~260s。

### P1 — Ken Burns 动态缩放

静态 PPT 用 zoompan 滤镜添加缓慢缩放效果：

```python
# 4 分钟视频，1.0 → 1.08 极慢缩放，视觉不枯燥
zoompan = "zoompan=z='min(zoom+0.0003,1.08)':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=24"
```

⚠️ zoompan 渲染极慢（每帧需要计算），12 段 × 4 分钟总计约 5-8 分钟。

### P2 — ASS 字幕优化

SRT 默认样式字小、无描边、贴底。升级为 ASS 格式：

```
[V4+ Styles]
Style: Default,微软雅黑,38,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,3,1,2,40,40,80,1
```

| 参数 | 值 | 效果 |
|------|-----|------|
| Fontsize | 38 | 1080p 培训视频推荐值，横竖屏清晰（28px 偏小，34px 变化不明显） |
| Outline | 3 | 黑色描边，任何背景可读 |
| Shadow | 1 | 轻微投影 |
| MarginV | 80 | 离底部 80px，不被播放器控件遮挡 |
| Alignment | 2 | 底部居中 |

ASS 字幕需要 fontconfig 支持，Windows 下默认已内置。

### P2 — 品牌水印

在视频右下角叠加半透明品牌 Logo 文字：

```bash
ffmpeg -i input.mp4 \
  -vf "drawtext=font='Microsoft YaHei':text='Ray谈化工':fontsize=22:fontcolor=white@0.5:shadowcolor=black@0.35:shadowx=2:shadowy=2:x=w-tw-28:y=h-th-28, format=yuv420p" \
  -c:v libx264 -crf 23 -preset medium -c:a copy output.mp4
```

⚠️ **中文字体渲染关键教训**：

```bash
# ❌ 使用 fontfile 指定路径 → 中文字符显示为方块 □□□
fontfile=/Windows/Fonts/msyh.ttc
fontfile=C:/Windows/Fonts/simhei.ttf

# ❌ 带盘符的绝对路径 → 冒号被解析为 ffmpeg filter 分隔符
fontfile=C\:/Windows/Fonts/simhei.ttf  # "No option name near '/Windows/Fonts/...'"

# ✅ 使用 fontconfig 字体名称（前提：ffmpeg 需 --enable-fontconfig）
font='Microsoft YaHei'
font='SimHei'

# 确认 ffmpeg 是否支持 fontconfig：
ffmpeg -version 2>&1 | grep fontconfig
```

> 原理：ffmpeg drawtext filter 的 `fontfile` 参数在 Windows 上容易因路径格式（冒号、反斜杠）而解析失败。`font` 参数通过 fontconfig 系统查找字体，自动处理路径和字体集合（.ttc），对中文渲染更可靠。

### PPT 视觉优化（P0→P1→P2）

> 详见 [Step 2 → PPT 设计规范与优化体系](#-ppt-设计规范与优化体系--德凯项目两轮迭代经验)。以下按优化优先级列出快速检查清单。

| 优先级 | 检查项 | 症状 | 修复 |
|:---:|------|------|------|
| **P0** | 底栏高度 | 视频水印 `drawtext` 遮挡进度条和页码 | `botBar` 的 `bY` 从 7.36 → 7.12，留出底部 0.4" |
| **P0** | 分栏/卡片字号 | 视频中窄栏文字太小看不清 | 正文 ≥18pt，行间距同步调大 |
| **P0** | 文字溢出 | 文本超出卡片/框外 | 检查 layout 尺寸与坐标匹配（LAYOUT_WIDE=13.33"×7.5"） |
| **P0** | 元素重叠 | 日期卡片文字叠在一起 | 增大卡片高度或拆分多行 |
| **P0** | 结果框遮挡 | 流程图下方的结果框挡住步骤 | 结果框放在流程图 **下方居中** 而非同行 |
| **P1** | 内容页单调 | 连续 5 页纯 bullet 列表 | 4 种差异化样式：卡片分组 / 响应链 / 警示 / 清单 |
| **P1** | 色彩滥用 | 到处用红色失去警示意义 | 按语义分配：红=危险、橙=过渡、黄=中性、绿=行动 |
| **P2** | 颜色码 | 3 位 hex 导致颜色不正确 | 始终用 6 位 hex |
| **P2** | 字体 | 视频中文字渲染异常 | `fontFace: 'Microsoft YaHei'`（完整名） |

### P3 — 事故报告照片插入

如果事故调查报告 PDF 中嵌有现场照片或技术图纸，可提取并插入视频对应位置，大幅提升真实感和培训冲击力。

**照片提取（pymupdf）**：

```python
import fitz
doc = fitz.open("accident_report.pdf")
for i in range(len(doc)):
    for img in doc[i].get_images(full=True):
        xref = img[0]
        base = doc.extract_image(xref)
        if len(base['image']) > 50 * 1024:  # 只提取 >50KB 的大图
            with open(f"photo_p{page.number+1}.{base['ext']}", "wb") as f:
                f.write(base['image'])
doc.close()
```

**照片选择策略**：

| 类型 | 优先级 | 插入位置建议 |
|------|--------|-------------|
| 事故现场全景/残骸 | ⭐⭐⭐⭐⭐ | "事故概览""直接原因"页之后，视觉冲击力最强 |
| DCS/工艺流程图 | ⭐⭐⭐ | "装置背景"页之后，帮助理解系统 |
| 技术图纸/数据表 | ⭐⭐ | 偏技术细节，通常不适合培训视频 |
| 印章/Logo/小图标 | ⭐ | 跳过，视频中不可读 |

**AI生成辅助示意图**：如事故机理需要可视化（如相变过程、连锁反应），可用 ImageGen 生成简单流程图：

```python
# 提示词示例
prompt = "Clean engineering flow diagram, dark background, 6 connected boxes with arrows: "
"化学品自聚 → 冷凝器堵塞 → 压力攀升 → 贮罐超压 → 罐体破裂 → 闪燃爆炸. "
"Red/orange accent colors, white text, 1920x1080, professional safety training style."
```

**插入实现要点**：

1. 照片片段时长由旁白决定（非固定 5 秒），配 zoompan 慢缩放效果（1.0→1.12 合适）
2. 插入后总时长增加，需**自动偏移所有后续字幕时间戳**
3. 插入位置计算：基于原 clip 时长累计，每次插入后偏移量累加
4. 交错合并时 concat 列表用 UTF-8 写入，合并后立即验证时长

```python
# 照片 clip 生成 — zoompan 慢缩放
zoom_end = 1.12
fps = 24
total_frames = int(audio_dur * fps)
zoom_step = (zoom_end - 1.0) / total_frames
zoompan = f"zoompan=z='min(zoom+{zoom_step:.6f},{zoom_end:.2f})':d=1:" \
          f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps={fps}"

# 字幕时间偏移逻辑
offsets = [(insert_time_1, photo_dur), (insert_time_2, photo_dur), ...]
for subtitle in ass_file:
    shift = sum(dur for t, dur in offsets if subtitle.start >= t)
    subtitle.start += shift
    subtitle.end += shift
```

**⚠️ 常见陷阱**：

| 陷阱 | 现象 | 根因 | 修复 |
|------|------|------|------|
| **selected 照片数 ≠ narration 数** | `IndexError: list index out of range` | PDF 提取 3 张照片但只写了 2 段旁白，`selected` 遍历到第 3 张时 `photo_results[2]` 不存在 | 用 `photo_sel_indexes = [0, 2]` 精确指定哪几张对应旁白，而不是遍历全部 selected |
| **gen_photo_audio cache 判断不完整** | `ValueError: too many values to unpack` | "跳过时只检查 mp3 存在 → `return mp3_path` 只返回 1 个值，但调用方 `mp3, cues = asyncio.run(...)` 期望 2 个值 | cache 判断须同时检查 mp3 + cues.json 存在 → 存在就 load cues 并返回 2 元组 |
| **重复运行时旧 clip 用了错图** | photo_02 展示错误照片 | 上次 TTS 生成时已经做好了 clip，重跑时 skip → 照片索引纠正了但旧 clip 没重建 | 修改 selected 映射后，必须删除旧 photo clip 让脚本重建 |

```python
# ✅ 正确的 cache 判断
mp3_path = os.path.join(WORK, 'audio', f'photo_{idx+1:02d}.mp3')
cues_path = os.path.join(WORK, f'cues_photo_{idx+1:02d}.json')
if os.path.exists(mp3_path) and os.path.exists(cues_path):
    with open(cues_path, 'r', encoding='utf-8') as f:
        cues = json.load(f)
    return mp3_path, cues  # 返回 2 元组，与调用方解包一致
```

### 优化版本演进参考

| 版次 | 时长 | 画质 | 画面 | 字幕 | BGM | 水印 | 大小 |
|------|------|------|------|------|-----|------|------|
| v1 | 8:08 | CRF 21 | 静态 | SRT 默认 | 无 | 无 | 20 MB |
| P0+P1 | 4:20 | CRF 18 | Ken Burns | SRT 默认 | 无 | 无 | 11 MB |
| P2 | 4:20 | CRF 18 | Ken Burns | ASS 28px | -25dB | 无 | 10 MB |
| P2+WM (bug) | 4:20 | CRF 18 | Ken Burns | ASS 28px | -25dB | Ray□□□ | 10 MB |
| P2+WM fixed | 4:20 | CRF 18 | Ken Burns | ASS 28px | -25dB | Ray谈化工 | 9.3 MB |
| **P2+34px** | **4:20** | **CRF 18** | **Ken Burns** | **ASS 34px** | **-25dB** | **Ray谈化工** | **11 MB** |
| **P2+38px** | **4:20** | **CRF 18** | **Ken Burns** | **ASS 38px** | **-25dB** | **Ray谈化工** | **11 MB** |
| **P3+照片** | **4:40** | **CRF 18** | **Ken Burns + 实景照片** | **ASS 38px** | **-25dB** | **Ray谈化工** | **12 MB** |
| **信诺立兴 v1** | **6:17** | **CRF 21** | **静态** | **SRT 14px** | **无** | **无** | **12.7 MB** |
| **增城 v1** | **7:36** | **CRF 21** | **静态** | **SRT 14px** | **无** | **PSE Video** | **15.9 MB** |
| **增城 v2+照片** | **8:16** | **CRF 21** | **静态 + 实景照片(zoompan)** | **SRT 14px** | **无** | **PSE Video** | **18.3 MB** |
| **德凯 v1** | **5:01** | **CRF 21** | **静态（基础PPT）** | **SRT 14px** | **无** | **PSE Video** | **11.1 MB** |
| **德凯 v6（P0+P1+P2）** | **5:01** | **CRF 21** | **静态（优化PPT：5种视觉风格）** | **SRT 14px** | **无** | **PSE Video** | **9.9 MB** |
