# 复盘经验总结 + 常见坑位速查

> 本文件从 SKILL.md 分层卸载而来（低频内容，按需加载）。
> 触发时机：遇到具体坑位、需要排查问题、或复盘迭代时阅读。
> 正常执行流程（Step 1-11）不需要读此文件。

## 复盘经验总结

基于衢州巨化"9·4"事故、伊犁新天煤化工"10·16"窒息事故、及江西隆莱"12·31"窒息事故三个培训视频的完整迭代，总结如下可复用的经验。

### 0. SRT 字幕同步：SentenceBoundary + clip 时长

| 项目 | 经验 |
|------|------|
| **正确做法** | TTS 生成时用 `SubMaker` 捕获 `SentenceBoundary` 事件 → 句子级时间戳 |
| **错误做法** | 每页旁白按持续时间等分拆 → 字幕与语音完全不对齐 |
| **偏移计算** | 用 **clip 实际时长**（非音频时长）累加，因 `-loop 1 -shortest` 的 clip 比 MP3 长约 2s |
| **追加步骤** | TTS 生成后 `ffmpeg -i clip.mp4` 获取各 clip 真实 Duration 作为偏移 |

> 本项目教训：SRT 总时长 400s，视频 426s，字幕提前 27s 结束。根因是偏移用了音频时长而非 clip 时长。

### 0b-extra. edge_tts SubMaker API：Subtitle 对象，不是 tuple

```python
# ❌ 错误：假设 sub.cues 返回 tuple 列表
for td_start, td_end, content in sub.cues:
    # TypeError: cannot unpack non-iterable Subtitle object

# ✅ 正确：SubMaker.cues 是 Subtitle 对象列表
for item in sub.cues:
    start_sec = item.start.total_seconds()   # timedelta
    end_sec = item.end.total_seconds()
    text = item.content.strip()
```

> edge_tts 的 `SubMaker.cues` 返回 `List[Subtitle]`，每个 `Subtitle` 有 `.index`、`.start`（timedelta）、`.end`（timedelta）、`.content`（str）四个属性。文档中的 `(start, end, content)` 写法是示意性的，不能直接解包。

### 0b. SRT 字幕样式：force_style 控制字号和位置

| 项目 | 经验 |
|------|------|
| **正确做法** | `force_style='Fontsize=14,MarginV=2,Alignment=2'` |
| **错误做法** | 默认 SRT 样式（字号约 20px、位置偏高 → 遮挡 PPT 正文） |
| **MarginV 方向** | **越小越贴底**（MarginV=70 反而上移；MarginV=2 才是贴底） |
| **适用场景** | 1080p 培训视频，PPT 本身文字密集 → 字幕必须小 + 贴底 + 不抢眼 |

> 注意：ASS 字幕的 MarginV 推荐 80px（防播放器控件遮挡），SRT force_style 的 MarginV 推荐 2px（贴底避让正文）。两者方向不同是因为 ASS 基线从底部算，SRT force_style 的 libass 渲染有不同默认偏移。

### 0c. 人名去敏化：全流程统一替换

| 项目 | 经验 |
|------|------|
| **范围** | PPT 文本 + 旁白脚本 + TTS 音频 + SRT 字幕 → 四者必须统一 |
| **规则** | 3 字名 → X某某；2 字名 → X某 |
| **实现** | 先建 NAME_MAP → `anonymize()` 替换旁白 → 重建 TTS(音频)+SRT(字幕) |
| **误区** | 不能只改 SRT → 字幕显示"某某"但语音说的是真名，反而更糟 |

### 0d. Windows Unicode 路径处理：全程用 Python，避免 Shell 命令

中文目录名（尤其是含全角引号如 `"3·8"`）在 Windows 不同 shell 中行为不一致，是最隐蔽的坑。

| 环境 | 现象 | 可靠度 |
|------|------|--------|
| Git Bash `ls` | 目录名显示为乱码或 `No such file` | ❌ 不可用 |
| Git Bash `set`/`export` | 中文变量值被截断或乱码 | ❌ 不可用 |
| PowerShell `Get-ChildItem` | 部分字符显示为 `?`（如 `"3?8"`） | ⚠️ 查找可用，变量展开易出错 |
| PowerShell `Set-Content -Encoding ASCII` | 中文全部变为 `????` | ❌ 致命 |
| Python `os.scandir()` | 完整保留原始 Unicode | ✅ 唯一可靠方案 |

**铁律：**

```python
# ✅ 文件发现、路径拼接、目录创建 — 全部用 Python
import os
base = r'E:\LingXi\PS Training Video'
for entry in os.scandir(base):
    if '闪爆' in entry.name:  # Python 的 Unicode 比较始终可靠
        work_dir = os.path.join(entry.path, 'video_work')

# ✅ 文件写入 — 始终显式 UTF-8
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

# ✅ 运行外部命令 — 用 Python subprocess，cwd 参数避免路径拼接问题
subprocess.run(cmd, cwd=work_dir, capture_output=True, text=True)
```

> 教训：本次项目中信诺立兴报告路径含 `"3˙8"`（全角引号+U+0307），导致 `ls` 无法列出目录、PowerShell 变量展开后部分字符变为 `?`、ASCII 编码的 concat 列表全部路径损坏。改用 Python 全程处理后零问题。

### 0d-extra. Bash 内联 Python 命令 + 全角引号路径：三重逃生链路

当报告目录含全角引号字符（U+201C/U+201D），且需要在 Bash shell 中执行含 Python 代码的长命令时，**三重转义叠加**导致命令无法正确传递：

```
层1: Bash 解析 → 全角引号可能被当作普通引号吞掉
层2: Python -c → 字符串引号与代码引号冲突
层3: 代码中的全角引号 → 被层1或层2截断
```

**❌ 致命错误**：

```bash
# Bash -c 中 Python 字符串含全角引号 → shell 直接吞掉，SyntaxError
bash -c "python -c \"print('事故\\u201C9·16\\u201D')\""
# 实际传给 Python 的可能是：print('事故「9·16」) → 截断

# 单行 python -c 中含 \\n → 被 Bash 解释为换行，命令断裂
```

**✅ 铁律：当路径含全角引号时，禁止 Bash 内联 Python 命令**。

三条逃生路径，按推荐度排列：

| 路径 | 做法 | 适用场景 |
|------|------|----------|
| **路径 1（首选）**：Write 工具写 `.py` 文件到系统 Temp 目录 | `Write("~/.workbuddy/AppData/Local/Temp/stage.py", code)` → `python -u temp/stage.py` | **任何含全角引号路径的项目** |
| **路径 2**：Python `subprocess.run()` 用 `cwd=` 参数 | Bash 只调 `python -u script.py`，脚本内部用 Python 拼路径 | TTS 生成、clip 编码 |
| **路径 3**：Write 工具直接写 JS/Python 源文件到工作目录 | 但 Write 工具对全角引号路径也可能失败 → 降级为路径 1 | 能成功写入时可用 |

```python
# ✅ 路径 1 — 写临时脚本 + 执行
# 第一步：Write 工具写到临时目录（纯 ASCII 路径，零风险）
Write("~/.workbuddy/AppData/Local/Temp/make_clips.py", code)
# 第二步：shell 执行
python -u "~/.workbuddy/AppData/Local/Temp/make_clips.py"

# ❌ 不要这样 — Bash 解析会破坏引号嵌套
python -u -c "
import os
base = r'E:\LingXi\PS Training Video'
for entry in os.scandir(base):
    if '\u589e\u57ce' in entry.name:  # ← Bash 可能吞掉引号
        ...
"
```

> **增城项目教训**：报告目录含 `"9·16"`（全角引号），Bash `-c` 传 Python 代码时引号被 shell 吞掉 → 命令根本执行不了 → 才改用「Write 临时脚本 + shell 执行脚本」模式。此前信诺立兴项目也踩过这个坑，但当时 markitdown 在 Python 内部 subprocess 跑，侥幸绕过。增城项目中 TTS/水印编码涉及多层 ffmpeg 参数嵌套，彻底暴露了这个逃生链的刚性需求。

### 0e. Concat 列表编码陷阱：UTF-8 是生死线

`ffmpeg concat` 的输入列表如果路径含中文，**必须用 UTF-8 编码写入**。ASCII/ANSI 编码会导致中文全部变为 `?`，ffmpeg 找不到文件但**不报错**，静默跳过 → 合并后视频时长远短于预期。

```python
# ❌ 致命错误：PowerShell Set-Content -Encoding ASCII
# file 'E:\...\4-????????????.mp4' → ffmpeg 找不到 → 静默跳过

# ❌ 同样致命：Python 默认编码写入（可能随系统 locale 变化）
with open('concat_list.txt', 'w') as f:  # 默认 gbk 编码，中文丢失
    f.write(content)

# ✅ 必须显式 UTF-8
with open('concat_list.txt', 'w', encoding='utf-8') as f:
    f.write(content)
```

**验证规则**：合并后必须用 `ffmpeg -i merged.mp4` 检查 Duration 是否等于所有 clip 时长之和。如本次：预期 376s，第一版只有 216s（仅合并了前 6-7 个 clip），根因即 ASCII 编码列表。

### 0f. clip 时长漂移：`-shortest` 陷阱与 `-t` 修复

**根因**：`ffmpeg -loop 1 -i slide.png -i audio.mp3 -shortest` 生成的 clip，h264 编码的 GOP 缓冲导致视频比音频长约 2 秒/段。12 段累积约 27s 漂移 → concat 后视频总长 284s ≠ 音频总长 257s → SRT 字幕（基于音频时间戳生成）同步仅覆盖到 257s，末尾 27s 空白 + 字幕提前结束。

```bash
# ❌ -shortest：视频比音频长约 2s/clip，漂移累积
ffmpeg -loop 1 -i slide.png -i audio.mp3 -shortest clip.mp4

# ✅ -t {精确时长}：视频 = 音频时长，零漂移
ffmpeg -loop 1 -i slide.png -i audio.mp3 -t {audio_duration} clip.mp4
```

**验证**：每个 clip 生成后立即验证 `video_duration ≈ audio_duration`（差距 < 0.5s）。12 段全部通过后再 merge。

**教训**：首次合成后必须做「音频总长 vs 合并视频总长」对比审计。`-shortest` 不能保证精确。

| 项目 | 现象 | 修复 |
|------|------|------|
| 鹏凯 v1 | 音频 257s, 视频 284s | 12 段全部用 `-t` 重生成 → merge 257.8s ✓ |
| 信诺立兴 v1 | 音频 376s, 视频 426s（估算） | 同样修复 |
| 增城 v1 | 音频 453s, 视频 454s | 直接用 `-t` 零漂移 ✓ |

### 0g. TTS SentenceBoundary cues 持久化：断了必须能续

**问题**：首次 TTS 生成时，`SubMaker` 捕获的 `SentenceBoundary` cues 没有单独保存到磁盘。如果脚本在 TTS 完成后中断（超时/报错），续跑时虽然 `audio/slide_XX.mp3` 文件存在，但 **cues 数据已丢失**。

**影响**：续跑时无法直接从 MP3 推算句子级时间戳，必须重新调用 edge_tts 获取 cues → 增加网络开销，且 TTS 结果可能有微小差异。

```python
# ❌ TTS 生成脚本做完就没了 — cues 没保存
# Step 4 生成 mp3 + sub.cues → 脚本结束 → cues 全丢
# 续跑时只能重新 TTS

# ✅ 生成时立即保存 cues 到 JSON
import json
cues_data = {}
for slide_idx, cues in enumerate(all_cues):
    cues_data[str(slide_idx+1)] = [
        {"start": c["start"], "end": c["end"], "text": c["text"]} 
        for c in cues
    ]
with open('cues_data.json', 'w', encoding='utf-8') as f:
    json.dump(cues_data, f, ensure_ascii=False, indent=2)

# ✅ 续跑时优先加载已有 cues
if os.path.exists('cues_data.json'):
    with open('cues_data.json', 'r', encoding='utf-8') as f:
        all_cues = list(json.load(f).values())
else:
    all_cues = asyncio.run(re_fetch_cues())  # 回退到重 TTS
```

**教训**：TTS cues 是所有后续步骤（SRT 生成、字幕同步）的基础数据。它和 `narration_data.json` 同等重要，必须一同持久化。增城项目中首次脚本在 TTS 完成后超时（烧字幕+水印合一个脚本），续跑时不得不重新调用 edge_tts。

### 0h. ffmpeg PATH 在 Python subprocess 中偶尔失效

**现象**：`subprocess.run(["ffmpeg", "-i", ...])` 有时报 `FileNotFoundError: [WinError 2]`，即 ffmpeg 在 PATH 中不可见。

**根因**：Python `subprocess.run` 继承的环境变量可能与 shell 不完全一致。当通过 WorkBuddy 的 Bash/PowerShell 启动 Python 脚本时，ffmpeg 的 PATH 条目（`~/.workbuddy/binaries/ffmpeg/.../bin/`）可能未被包含。

```python
# ❌ 不稳定的写法
FFMPEG = "ffmpeg"  # subprocess.run 可能找不到

# ✅ 铁律：脚本内统一用绝对路径
import os
FFMPEG = os.path.expandvars(
    r"%USERPROFILE%\.workbuddy\binaries\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
)
# 或探测多个可能位置
def find_ffmpeg():
    candidates = [
        os.path.expandvars(r"%USERPROFILE%\.workbuddy\binaries\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"),
        os.path.expandvars(r"%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"),
    ]
    for c in candidates:
        if os.path.exists(c): return c
    raise RuntimeError("ffmpeg not found")

FFMPEG = find_ffmpeg()
```

> **增城项目教训**：全流程脚本中第一次用 `"ffmpeg"` 短名成功（通过 bash -c 转发时继承 PATH），但第二次脚本（burn+watermark）在同一 Python 进程中调用时失败 → 排查发现 PATH 继承不一致 → 统一改用绝对路径后零失败。

### 0i. safe-delete 沙箱删除拦截（收尾清理必踩）

**现象**：收尾清理时 `os.remove(tmp)` / `shutil.rmtree(dir)` 报：
```
OSError: [safe-delete][SAFE_DELETE_FAIL_CLOSED]
{"target": "...", "reason": "windows-sandbox-recycle-bin-unavailable"}
```

**根因**：WorkBuddy 沙箱环境回收站不可用，safe-delete 安全钩子对**任何程序化删除**（`os.remove` / `shutil.rmtree` / `unlink`）fail-closed 拒绝。这是环境特性，不是代码 bug。

**影响**：脚本在收尾清理步骤报错退出，但**成品视频（video_final.mp4）在删除动作之前已生成**，不受影响。只有中间临时文件（如烧录的 out_tmp.mp4）清不掉。

**解决**：
```python
# ✅ 删除操作必须 try/except 包裹，忽略失败
try:
    os.remove(tmp)
except OSError:
    pass  # 沙箱 safe-delete 拦截，临时文件留着不影响成品

# ✅ 清理策略降级：不删，只保留 keep 列表（Step 11「仅保留母版」）
# 临时文件留在 video_work/，后续手工清理
```

> **2026-08-26 赛科测试**：烧录字幕最后一步 `os.remove(out_tmp.mp4)` 被 safe-delete 拦截，脚本报错退出，但 video_final.mp4（262.88s）已正常生成。out_tmp.mp4 与 final 等大（约 6.4MB），留着不影响交付。

### 1. 品牌水印：fontfile 不如 font + PPT 页脚与视频水印分离

#### 视频水印文本

使用 `drawtext` 滤镜，水印文本统一为 **`Ray谈化工 · PSE Video`**。

| 项目 | 经验 |
|------|------|
| **正确做法** | `drawtext=font='Microsoft YaHei':text='Ray谈化工 \u00B7 PSE Video'` |
| **错误做法** | `drawtext=fontfile=C:/Windows/Fonts/msyh.ttc:text='Ray谈化工'` |
| **失败原因** | Windows 路径中的 `:` 被 ffmpeg 解析为 filter 参数分隔符，导致字体加载失败，中文回退为占位方块 □ |
| **前置检查** | `ffmpeg -version \| grep fontconfig` —— 必须包含 `--enable-fontconfig` |
| **字体选择** | 优先用 `Microsoft YaHei`（系统自带、.ttc 集合、字重完整）；备选 `SimHei` |

> 教训：Windows 上 ffmpeg drawtext/fontfile 与文件路径天然冲突。`font` 参数通过 fontconfig 间接查找，绕过了路径解析问题。**即使路径表面看起来正确（如 `/Windows/Fonts/msyh.ttc`），也应优先用 font 名称。**

#### PPT 页脚与视频水印分离

**原则**：PPT 课件不再放置任何页脚/品牌标识（如 "Ray谈化工 · PS Infographic"），品牌标识仅通过视频水印叠加。这样 PPT 源文件保持干净（可用于其他用途），品牌归属由视频水印统一管理。

```javascript
// ❌ 旧 PPT helper：每个 slide 底部有品牌页脚
function contentSlide(...) {
    ...
    s.addText('Ray谈化工 · PS Infographic', { ... });  // 删除此行
}

// ✅ 新 PPT helper：无页脚
function contentSlide(...) {
    ...
    // 不添加任何页脚
}
```

**水印参数（推荐）**：

```bash
ffmpeg -i input.mp4 \
  -vf "drawtext=font='Microsoft YaHei':text='Ray谈化工 · PSE Video':fontsize=22:fontcolor=white@0.5:shadowcolor=black@0.35:shadowx=2:shadowy=2:x=w-tw-28:y=h-th-28,format=yuv420p" \
  -c:v libx264 -crf 23 -preset medium -c:a copy output.mp4
```

> 注意：`·`（U+00B7 middle dot）在 ffmpeg drawtext 中直接写字符即可，**不要用 `\u00B7` 转义** — ffmpeg drawtext filter 不解析 `\u` Unicode 转义，会原样渲染为字面量 `u00B7`。

### 2. 字幕字号：从 28 → 34 → 38 的迭代教训

| 阶段 | 字号 | 用户反馈 | 教训 |
|------|------|---------|------|
| 初版 | 28px | — | 选择 28px 是因为参考了在线视频字幕的一般标准 |
| 第一次调整 | 34px | "看起来没有变化" | 28→34 增幅仅 21%，在小屏/缩放播放器上视觉差异极小 |
| 第二次调整 | 38px | 满意 | 28→38 增幅 36%，视觉差异明显 |

**结论**：
- **1080p 培训视频 ASS 字幕推荐 38px** 起步。培训场景受众可能有年龄偏大的学员，字幕宁可偏大。
- 字号调整是试错过程。建议首版直接用 38px，避免反复迭代。
- **ASS 文件是字幕样式的唯一真源（single source of truth）**。每次调字号只需改 Style 行的一个数字，重编一次即可，成本很低。

```bash
# 调字号只需改这一行的第三个字段
# Style: Default,微软雅黑,38,...  ← 改这个数字
```

### 3. 其他关键优化点

#### 3a. 合并字幕烧录与水印：一次编码，两项产出

```bash
# ✅ 一次编码同时完成字幕 + 水印（节省一次完整重编码）
-vf "subtitles=subtitles_v2.ass,drawtext=font='Microsoft YaHei':text='Ray谈化工':...,format=yuv420p"

# ❌ 不要分两次编码（字幕一次、水印一次），质量损失叠加
```

#### 3b. 保留无字幕中间产物（`video_merged_v2.mp4`）

字幕和水印作为硬字幕烧录后，无法无损去除。务必保留合并后的无字幕版本作为"母版"，后续调字号、改水印都从母版出发。

```
video_merged_v2.mp4     ← 母版：Ken Burns + BGM，无字幕无水印（必须保留）
  ├→ burn ASS 28px → safety_training_video_p2.mp4
  ├→ burn ASS 38px + WM → safety_training_video_38px.mp4
  └→ ... 未来所有变体都从这里派生
```

#### 3c. 两步法烧录字幕（不可跳过）

`-movflags +faststart` 与 `subtitles` 滤镜同时使用必导致 moov atom 缺失：
```
Step A: 编码（无 faststart） → Step B: -c copy remux（添加 faststart）
```
任何硬字幕/水印视频都适用此规则。

#### 3d. BGM 用 ffmpeg 合成，不依赖外部下载

Pixabay 等免费音效站 CDN 对无 Referer 的请求返回 403。ffmpeg `aevalsrc` 合成低频氛围音零依赖、零版权风险，且可精确控制时长和淡入淡出。

#### 3e. 字幕字体选择：ASS 用 `微软雅黑`，drawtext 用 `font='Microsoft YaHei'`

| 场景 | 写法 | 说明 |
|------|------|------|
| ASS 字幕 | `Fontname: 微软雅黑` | libass 通过 DirectWrite 查找，用中文名 |
| ffmpeg drawtext | `font='Microsoft YaHei'` | fontconfig 查找，用英文名 |

此 skill 对应的工作目录中保留了可复用脚本：

| 脚本 | 用途 |
|------|------|
| `create_ppt.js` | pptxgenjs PPT 模板 |
| `generate_tts.py` | 双引擎批量配音（Qwen3-TTS + edge-tts） |
| `generate_srt.py` | 从 MP3 生成 SRT 字幕 |
| `assemble_video.py` | 视频合成（含两步法字幕） |

## 常见坑位速查

| 问题 | 现象 | 根因 | 解决 |
|------|------|------|------|
| PDF 无文字 | markitdown 输出空 | 扫描版 PDF | pymupdf + pytesseract OCR |
| pptxgenjs 找不到 | MODULE_NOT_FOUND | Git Bash `set` 不生效 | `NODE_PATH=path node` |
| 中文引号报错 | SyntaxError | `""` 在 js 中被解析 | Unicode `\u201C` `\u201D` |
| 颜色不显示 | 文字消失 | 3 位 hex `"555"` | 6 位 `"868E96"` |
| 无独立 ffprobe | FileNotFoundError | imageio-ffmpeg 不含 ffprobe | 用 ffmpeg `-i file` 解析 Duration |
| 字幕滤镜解析错误 | "Unable to parse option" | Windows 盘符 `D:` | cd 到目录用相对路径 |
| moov atom 缺失 | 视频无法播放 | faststart + subtitles 同时用 | 两步法：先编码再 remux |
| 编码后 merged 被清理 | FileNotFoundError | 上轮脚本删了中间文件 | 保留 clips 目录，需要时重 merge |
| BGM 下载 403 | curl 被 Pixabay CDN 拒绝 | 无 Referer | 用 ffmpeg aevalsrc 合成 |
| lowpass 滤镜名称错误 | Filter not found | imageio-ffmpeg 用 `lowpass` 非 `alowpass` | 统一用 `lowpass=f=300` |
| 中文字体渲染为方块 | "Ray□□□" | fontfile 路径含冒号被解析为分隔符 | 用 `font='Microsoft YaHei'` 代替 `fontfile=` |
| 字幕与语音不同步 | 字幕跑在语音前面，越到后面偏差越大 | SRT 等分每页时长，未对齐句子级节奏 | 用 SubMaker 捕获 SentenceBoundary 事件 |
| 字幕结束过早 | SRT 6分37秒结束，视频 7分06秒 | 用音频时长累加偏移，clip 比 MP3 长~2s | 用 clip 实际时长做偏移基准 |
| 字幕遮挡 PPT 正文 | 字幕区域覆盖画面文字 | SRT 默认字号大、位置高 | force_style: `Fontsize=14,MarginV=2` |
| 人名未去敏 | 视频中出现真实姓名 | 旁白/PPT 直接引用报告原文 | Step 9 全流程替换，重建 TTS+SRT |
| 中文路径乱码 | `ls` 报 No such file，PowerShell 显示 `???` | Git Bash/PS 对含全角引号路径处理不一致 | 全程用 Python `os.scandir()` + `subprocess` |
| 合并后时长远短于预期 | merged 246s，实际应 376s | concat 列表用 ASCII 编码，中文路径变 `?`，文件静默跳过 | 列表文件必须 UTF-8 编码写入；合并后立即验证时长 |
| SubMaker cues 解包报错 | `TypeError: cannot unpack non-iterable Subtitle object` | `sub.cues` 返回 Subtitle 对象列表，非 tuple 列表 | 用 `item.start` / `item.end` / `item.content` |
| Get-ChildItem 找到旧项目文件 | 导出错误的 PPTX | `-Recurse` 搜到了其他视频目录的 output.pptx | 限定搜索目录，用 `-match "闪爆" -and -match "信诺"` 精确匹配 |
| `-shortest` 致 clip 视频比音频长 | 合并后视频 284s，音频仅 257s，SRT 提前 27s 结束 | h264 GOP 缓冲，每段 clip 比音频多 ~2s，12 段累积 | 用 `-t {audio_dur}` 替代 `-shortest`，生成后验证每段 v≈a |
| PPT 页脚干扰 + 水印命名不一致 | PPT 底部有旧品牌文字 "Ray谈化工 · PS Infographic" | 旧版 PPT 在所有页面固定了品牌页脚 | PPT 去页脚，水印统一用 `Ray谈化工 · PSE Video` |
| 字幕精确同步制作 | — | — | TTS 时捕获 SentenceBoundary → SRT 时间戳基于音频而非视频 |
| Python 旁白中文引号 | `SyntaxError: invalid syntax` | 旁白脚本中 ASCII `"运气"` 被解析为 Python 字符串结束符 | 中文语境下的引号用 Unicode 弯引号 `\u201c` `\u201d` 或改用 `「」` |
| **ffmpeg 未安装** | `RuntimeError: No ffmpeg exe could be found` | 首次运行时未预装 ffmpeg | 见环境依赖 → ffmpeg 安装说明（三档：预装 > pip安装 > imageio缓存降级） |
| **幻灯片导出编码**：PS 脚本乱码 | PowerPoint "Export OK" 但 PNG 文件不存在 | PowerShell 的 `-File` 对 UTF-8 文件默认用 ANSI 解码 → 中文路径损坏 | 改用 Python win32com 直接操作 COM（Step 5） |
| **Python 输出缓冲** | 进程运行中但无任何输出，无法判断进度 | stdout 非 TTY 时 Python 默认缓冲 | 加 `-u` 参数：`python -u -c "..."` |
| **后台任务丢失** | 编码到一半停了，task_id 不存在 | 会话刷新 → 后台进程状态不可恢复 | 关键步骤一律前台同步跑，timeout 给够 |
| **PPTX 文件锁定** | `PermissionError` 保存 PPTX | PowerPoint COM 未释放文件句柄 | 保存前 `taskkill /F /IM POWERPNT.EXE` |
| **PPT 末页文本重合** | subtitle 与 desc 区域交叠 | `titleSlide` 中 desc y=3.5 与 subtitle 底边 y=3.6 重叠 | desc y 改为 3.8，留 0.2" 间距 |
| **tesseract 路径** | `TesseractNotFoundError` | 托管 Python 的 PATH 无 tesseract.cmd | 显式设置：`pytesseract.pytesseract.tesseract_cmd = r'C:\Users\rayzh\.local\bin\tesseract.cmd'` |
| **全角引号幽灵目录** | 报告目录旁边多出一个短名空目录，内部路径分裂 | 工具将 `"`(U+201C) `"`(U+201D) 误解析为路径分隔符 | Step 11 排查脚本，删除空幽灵目录 |
| **Bash 内联 Python + 全角引号** | `SyntaxError: unterminated string` 命令执行失败 | Bash 解析层吞掉 Python 代码中的全角引号，三层转义叠加 | 写 `.py` 文件到 Temp 目录再执行，禁止 Bash 内联含全角引号的 Python 命令 |
| **TTS cues 未持久化** | 续跑时 `all_cues` 为空/null，SRT 无法生成 | TTS 生成后 cues 只在内存里，脚本中断即丢失 | TTS 完成后立即 `json.dump(cues_data, ...)` 保存 |
| **ffmpeg PATH 在 subprocess 中不解析** | `FileNotFoundError: [WinError 2] 系统找不到指定文件` | 不同进程的 PATH 继承不一致 | 脚本内统一用 ffmpeg 绝对路径 (`%USERPROFILE%\.workbuddy\binaries\ffmpeg\...\ffmpeg.exe`) |
| **Write 工具对全角引号路径失败** | `ENOENT: no such file or directory` 写文件报错 | 含 U+201C/U+201D 的目录名被工具误解释 | 降级到 Temp 目录写 `.py` 脚本，再用 Python `os.scandir()` + `open()` 写入目标目录 |
| **照片数量 ≠ 旁白数量** | `IndexError: list index out of range` 在生成 photo clips 时 | `selected` 有 N 张照片但 `photo_narrations` 只有 M 段（M < N）→ `photo_results[i]` 越界 | 用 `photo_sel_indexes` 精确映射到旁白，而非遍历全部 selected |
| **照片 cache 判断不完整** | `ValueError: too many values to unpack` 续跑时 | gen_photo_audio 跳过时只返回 mp3_path（1 值），调用方期望 (mp3, cues)（2 值） | cache 检查须同时判 mp3 + cues.json 存在 → load cues 返回 2 元组 |
| **旧 clip 与修正后的 selected 不一致** | 照片 clip 展示了错误的图片 | 上次运行已生成 clip → 重跑时 skip，未用修正后的照片目标 | 修改 selected 映射后，必须先删除旧 photo clip → 脚本才会重建 |
| **含中文引号路径下 Write 工具全部不可用** | `ENOENT` 每个文件写入都失败 | Write 工具对含全角引号目录名的路径解析失败 | 全程走 Temp 目录 + Python os.scandir + open() 写入目标（三重逃生链路之路径 3） |
| **PPT 布局尺寸不匹配** | 文字大面积溢出框外 | `pptx.layout = 'LAYOUT_16x9'`（10"宽）但坐标按 13.33" 设计 | 统一用 `LAYOUT_WIDE`（13.33"×7.5"），坐标与布局一致 |
| **PPT 底栏被视频水印截断** | 视频底部进度条和页码显示不全 | `botBar` 的 `bY=7.36` 与 `drawtext y=h-th-28` 重叠 | `bY` 降至 7.12，留出底部 0.4" 给水印 |
| **PPT 分栏文字在视频中过小** | 窄栏内容播放时难以辨认 | 3.3" 宽栏用 16pt → 1080p 视频中偏小 | 分栏/卡片正文 ≥18pt，行间距同步调大 |
| **PPT 内容页视觉单调** | 连续 5 页纯 bullet 列表，观众疲劳 | 所有内容页共用同一 `contentSlide` 函数 | 按内容类型匹配 4 种视觉隐喻：卡片分组 / 响应链 / 警示 / 清单 |
| **pptxgenjs `alpha` 属性不生效** | 透明度没有变化 | `fill: { ..., alpha: 65 }` — pptxgenjs 无 `alpha` 属性 | 用 `transparency: 65`（0-100，值越大越透明） |
| **pptxgenjs `rightTriangle` 形状报错** | 运行时抛出 shape type 错误 | 部分 ShapeType 枚举值未实现 | 降级为 `pptx.ShapeType.rect` |
| **PowerPoint COM 对智能引号路径报错** | `pywintypes.com_error: (-2147024893)` 无法打开 | 路径中的 `\u201c`/`\u201d` 全角引号导致 COM Open() 失败 | 复制 pptx 到 Temp ASCII 路径 → 导出 → 复制回 |
| **subprocess capture_output 解码 ffmpeg stderr 失败** | `UnicodeDecodeError: 'gbk' codec can't decode byte 0x80` | `capture_output=True, text=True` 用系统默认 GBK 解码 ffmpeg 二进制 stderr | 用 `text=False` + `ffprobe` 单独验证时长，或 `decode('utf-8', errors='replace')` |

### 28. 字幕/水印渲染验证 — 像素统计法（2026-08-02 包钢任务）

**场景**：视频烧录完成后需要确认字幕和水印真的渲染出来了，但模型不支持读图、tesseract bridge 本机故障（`tesseract.cmd --version` 报 "'M' 不是内部或外部命令"）。 ⚠️ **2026-09-12 补记**：本条前提已变——2026-09 起主流模型原生读图已普遍可用，像素统计法改为「读不了图时」的降级手段；判定以实测为准，不按模型名预设。

**像素统计法（零依赖，纯 PIL）**：
```python
from PIL import Image
img = Image.open(frame_png).convert('RGB')
w, h = img.size
px = img.load()
# 字幕区：底部 90%-97% 白色像素（SRT 白字+黑描边，暗色 PPT 上对比强）
white_bottom = sum(1 for y in range(int(h*0.90), int(h*0.97)) for x in range(0, w, 3)
                   if px[x,y][0]>200 and px[x,y][1]>200 and px[x,y][2]>200)
# 水印区：右下角 70%-100% 白色半透明像素
white_wm = sum(1 for y in range(int(h*0.92), int(h*0.98)) for x in range(int(w*0.70), w, 2)
               if px[x,y][0]>150 and px[x,y][1]>150 and px[x,y][2]>150)
# 字幕>50 像素 ✓，水印>20 像素 ✓
```

**要点**：
1. 抽 3 帧（前/中/后）验证，某帧字幕区 0 像素可能是**句子间隙**（正常），再补抽相邻帧确认即可
2. ffmpeg subtitles/drawtext 滤镜如果字体加载失败会直接报错退出——**滤镜执行成功本身已证明渲染成功**，像素法只是双保险
3. 抽帧用 `ffmpeg -ss {t} -i video.mp4 -frames:v 1 out.png`（-ss 在 -i 前，快速定位）
