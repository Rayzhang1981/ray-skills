# 踩坑记录（按需加载——遇到问题再读）

## 常见问题 FAQ

### Q: 音频采样率只有 24kHz？
**A**: TTS 输出 MP3 可能是 24kHz mono。合成时**必须**加 `-ar 44100 -ac 2` 重采样为立体声。

### Q: 字幕中文乱码？
**A**: SRT 文件必须 UTF-8 编码。FFmpeg 的 `subtitles` 滤镜路径中冒号需转义 `\:`。

### Q: Windows 路径含中文/冒号导致字幕烧录失败？
**A**: FFmpeg `ass` 滤镜无法处理 `C:\Users\...` 格式的 Windows 路径（冒号被解析为参数分隔符，反斜杠被当作转义字符吃掉）。解决方案：改用 `subtitles` 滤镜 + 路径转义规则：
```python
# 路径转义：反斜杠→正斜杠，冒号→\:
escaped = path.replace("\\", "/").replace(":", "\\:")
vf = f"subtitles='{escaped}'"  # 不用 force_style 即可烧录 ASS
```
`subtitles` 滤镜内部使用 libass，完全支持 ASS 格式的样式。

### Q: 字幕文字太多遮挡PPT怎么办？
**A**: 在 SKILL.md「字幕分段显示策略」中已定义规则：
- `generate_srt.py` 和 `assemble_video.py` 的 `generate_ass` 均内置 `split_text_semantic()`
- 按语义拆分每段 ≤38 字，按字数比例分配时间
- ASS 硬字幕使用 FontSize=24 + MarginV=60（分段显示后不遮挡画面）

### Q: 硬盘字幕烧录失败？
**A**: FFmpeg 可能未编译 libass。脚本会自动检测并回退到软字幕模式。

### Q: Qwen3-TTS 模型下载慢？
**A**: 设置 HuggingFace 镜像：`export HF_ENDPOINT=https://hf-mirror.com`。

### Q: 多个流水线同时运行？
**A**: 内置进程锁自动阻止同一输出目录的并发运行。

---

## 经验复盘：字幕优化踩坑（2026-07-08）

### 核心教训

| # | 教训 | 详情 |
|---|------|------|
| 1 | **遮挡根源是文字量，不是字号** | 原 24pt + 整页 200 字一次性显示 → 严重遮挡。拆成 227 段短句后，24pt 完全可用。如果一开始只做拆分不改字号，可省去 24→18→22→24 三轮回调 |
| 2 | **`ass` 滤镜不支持 Windows 中文路径** | `C:\Users\...` 中冒号被解析为参数分隔符、反斜杠被当转义吃掉。正确解法：[见 FAQ](#q-windows-路径含中文冒号导致字幕烧录失败) |
| 3 | **`subprocess.run` 错误处理脆弱** | 当 FFmpeg 退出无 stderr 输出时，`result.stderr[:300]` 为空，排错困难。已加固为同时检查 stdout + returncode |

### 字幕方案最佳实践（固化）

```
方案：语义拆分 + 原始字号 + 增大边距
├── split_text_semantic()    # 按句号→分号→逗号逐级拆分，≤38 字/段
├── 时间分配                  # 按字数比例，最短 1.5s/段
├── FontSize=24              # 原始大小，分段后不遮挡
├── MarginV=60               # 底部边距从 30 增大到 60
└── 行宽 ≤34 字，≤2 行        # ASS + SRT 行宽控制

FFmpeg 路径转义（Windows 中文路径）：
  path.replace("\\", "/").replace(":", "\\:")
  vf = f"subtitles='{escaped}'"    # ASS 格式直接用 subtitles 滤镜
```

### 脚本改进备忘

- `generate_srt.py` 和 `assemble_video.py` 的 `split_text_semantic()` 实现有重复，后续可提取为 `scripts/subtitle_utils.py` 公共模块
- `assemble_video.py` 的 `subprocess.run` 错误处理已加固（v2.1），检查 stdout + returncode
- 所有默认字号已统一为 24（`generate_ass` 签名、`argparse` default、SKILL.md 全部更新）

---

## 经验复盘：bash 中文路径乱码导致音频静音（2026-07-29）

> **这是迄今踩过最大的坑，3 轮完整运行才定位根因。每次 90 片段重建耗时 20+ 分钟。**

### 现象

- 视频有 AAC 44100Hz 立体声音频流，但完全静音（mean_volume = -91.0 dB）
- 单个片段仅 92 KB（正常 470 KB），AAC 比特率仅 2-4 kbps（正常 ~48 kbps）

### 根因链

```
bash 传递中文路径参数 → 中文字符乱码
  → TTS 脚本输出到乱码目录（如 监护人培[乱码]202604_output/audio/）
  → assembly 脚本查找正确目录（监护人培训202604_output/audio/）
  → os.path.exists() 返回 False
  → make_clip() 回退到静音源 anullsrc
  → 全片静音
```

### 核心教训

| # | 教训 | 详情 |
|---|------|------|
| 1 | **涉及中文路径的命令必须用 PowerShell** | bash（Git Bash）无法正确处理 Windows 中文路径，传给 Python 的命令行参数中文字符会被破坏。TTS 和 assembly 步骤都必须通过 PowerShell 执行 |
| 2 | **AAC 2kbps = 静音诊断信号** | 正常语音 AAC 编码约 48 kbps。如果片段 AAC 仅 2-4 kbps，说明音频源是 `anullsrc`（静音发生器），而非真实音频文件 |
| 3 | **片段体积快速诊断** | 92 KB 无声 vs 470 KB 有声 —— 文件体积是最快的诊断手段，无需运行 volumedetect |
| 4 | **TS concat 协议不能用于大量文件** | `concat:` 协议拼接 90 个 TS 文件会无限挂起。坚持用 `concat demuxer` + `-map 0:v -map 0:a` 更可靠 |
| 5 | **`-map 0:v -map 0:a` 显式流映射** | FFmpeg 的 `-vf` 简单滤镜在某些条件下不自动包含音频流，显式映射是保险措施 |

### 诊断速查

```python
# 快速判断片段/视频是否有声（无需完整 volumedetect）
import os
size = os.path.getsize('clip_01.mp4')
if size < 150_000:     # 92KB → 大概率静音（只有视频帧）
    print("SILENT - check audio source!")
elif size > 300_000:   # 470KB+ → 正常音频
    print("OK")
```

### 变更清单

| 文件 | 变更 |
|------|------|
| `assemble_video.py` — `burn_subtitles()` | `-c:a copy` → `-c:a aac -b:a 192k` + `-map 0:v -map 0:a` |
| `assemble_video.py` — `concat_cmd` | 同上，添加显式流映射 |
| 执行环境 | **强制 PowerShell**（不再用 bash 传递中文路径） |

### 增量更新优化（2026-07-29）

当 PPT 仅首页标题变更时，可复用 89 页已有资产，只需重建首页：
1. 复制旧 output 目录中 slides 2-90、全部 audio
2. 重新导出 slide_01.png
3. 更新 narration.json 仅 slide 1
4. `--regenerate 1` 仅重建 slide 1 的 TTS
5. 重新合成 → 节省 80%+ 处理时间
