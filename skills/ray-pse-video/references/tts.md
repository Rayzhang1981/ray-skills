# TTS 音色与批量生成（按需加载）

> 来源：ray-pse-video SKILL.md 分层卸载（v2.2.0）。

### Qwen3-TTS 预设音色

```python
# 安装：pip install -U qwen-tts
# 首次使用自动下载模型（约 1.5GB）

from qwen_tts import Qwen3TTS

tts = Qwen3TTS()
SPEAKER = "Vivian"  # 从下表选择
tts.synthesize(text, speaker=SPEAKER, output_path=out_path)
```

| 音色 | 描述 |
|------|------|
| `Vivian` | 明亮的年轻女声（默认） |
| `Serena` | 温暖、温柔的年轻女声 |
| `Uncle_Fu` | 成熟的男性声音，醇厚音色 |
| `Dylan` | 年轻的北京男声 |
| `Eric` | 活泼的成都男声 |

### Qwen3-TTS 声音克隆（推荐）

```python
# 提供 5-15 秒干净人声参考音频，克隆音色
tts.synthesize(text, reference_voice="voice_sample.wav", output_path=out_path)
```

### edge-tts 在线语音

```python
import asyncio, edge_tts
VOICE = "zh-CN-YunjianNeural"   # 从下表选择
RATE = "+5%"

async def gen(text, out):
    comm = edge_tts.Communicate(text, VOICE, rate=RATE)
    await comm.save(out)

await asyncio.gather(*[gen(t, f"audio/slide_{s:02d}.mp3") for s, t in script])
```

| 语音 | 描述 |
|------|------|
| `zh-CN-YunjianNeural` | 云健（男，沉稳大气） |
| `zh-CN-YunxiNeural` | 云希（男，年轻阳光） |
| `zh-CN-XiaoxiaoNeural` | 晓晓（女，温暖自然） |
| `zh-CN-YunyangNeural` | 云扬（男，新闻播报） |
| `zh-CN-XiaoyiNeural` | 晓伊（女，亲切活泼） |
| `zh-CN-YunxiaNeural` | 云夏（男，综艺解说） |

### 批量生成（推荐脚本结构）

```python
import asyncio
from qwen_tts import Qwen3TTS

# === 选择引擎 ===
ENGINE = "qwen3"        # "qwen3" 或 "edge"
SPEAKER = "Vivian"      # Qwen3-TTS 预设音色
# REF_VOICE = "voice.wav"  # Qwen3-TTS 声音克隆（与 SPEAKER 二选一）
EDGE_VOICE = "zh-CN-YunjianNeural"  # edge-tts 语音
EDGE_RATE = "+5%"       # edge-tts 语速

async def generate_all(script, out_dir):
    if ENGINE == "qwen3":
        tts = Qwen3TTS()
        for slide, text in script:
            # tts.synthesize(text, speaker=SPEAKER, output_path=f"{out_dir}/slide_{slide:02d}.mp3")
            tts.synthesize(text, speaker=SPEAKER, output_path=f"{out_dir}/slide_{slide:02d}.mp3")
    else:
        import edge_tts
        async def gen_one(slide, text):
            comm = edge_tts.Communicate(text, EDGE_VOICE, rate=EDGE_RATE)
            await comm.save(f"{out_dir}/slide_{slide:02d}.mp3")
        await asyncio.gather(*[gen_one(s, t) for s, t in script])

asyncio.run(generate_all(script, "audio/"))
```

> ⚠️ **引擎差异注意**：Qwen3-TTS 不提供 edge-tts 的 `SentenceBoundary` 事件，字幕制作时需走备选路径（见 Step 6）。
