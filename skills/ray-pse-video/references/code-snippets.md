# 关键代码片段（按需加载）

> 来源：ray-pse-video SKILL.md 分层卸载（v2.2.0）。Step 流程中如需要对应实现，复制到工作脚本。

## edge-tts SentenceBoundary 脚本

```python
import asyncio, edge_tts

async def generate_with_timing(text, mp3_path):
    comm = edge_tts.Communicate(text, VOICE, rate=RATE)
    sub = edge_tts.SubMaker()
    audio_data = []

    async for chunk in comm.stream():
        if chunk["type"] == "audio":
            audio_data.append(chunk["data"])
        elif chunk["type"] == "SentenceBoundary":
            sub.feed(chunk)  # 记录句子起止时间

    with open(mp3_path, "wb") as f:
        for d in audio_data: f.write(d)

    # sub.cues = [Subtitle(start=timedelta, end=timedelta, content=str), ...]
    # ⚠️ Subtitle 是对象，不是 tuple，不能解包 → 用 item.start / item.end / item.content
    # 对每个 cue 按 22 字/行拆分为更小字幕段 → 生成 SRT
    return [(item.start, item.end, item.content) for item in sub.cues]
```

## 烧录字幕关键教训（路径/faststart）

```python
# ❌ 使用绝对路径（含 D:）→ subtitles 滤镜解析失败
vf = f'subtitles=D:/path/to/subtitles.srt'
# Error: "Unable to parse option value '/RayClaw/...' as image size"

# ✅ 使用相对路径（cd 到目录后执行）
vf = 'subtitles=subtitles.srt'
subprocess.run(cmd, cwd=work_dir)

# ❌ -movflags +faststart 与 subtitles 同时使用 → moov atom 未写入
# Error: "moov atom not found" → 视频损坏无法播放

# ✅ 两步法：先编码（无 faststart），再 remux
# Step A: 编码 + 字幕
ffmpeg -i merged.mp4 -vf subtitles=subs.srt -c:v libx264 -crf 21 -c:a aac out_tmp.mp4
# Step B: remux 添加 faststart
ffmpeg -i out_tmp.mp4 -c copy -movflags +faststart output.mp4
```

## 幽灵目录清理脚本

```python
import os, shutil

base = r'E:\LingXi\PS Training Video'
report_keyword = 'xx事故'  # 示例：事故报告目录关键词

# 找出所有同名前缀的目录
dirs = []
for entry in os.scandir(base):
    if report_keyword in entry.name:
        dirs.append((len(entry.name), entry.path, entry.name))

# 最短的那个通常是幽灵目录
dirs.sort()
for _, path, name in dirs[1:]:  # 跳过最长的（正确目录）
    # 验证是空的幽灵目录
    file_count = sum(1 for _ in os.walk(path) for __ in _[2])
    if file_count == 0:
        shutil.rmtree(path)
        print(f'Deleted ghost: {name}')
    else:
        print(f'WARNING: {name} has {file_count} files — check before deleting!')
```