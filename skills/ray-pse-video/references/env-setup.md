# ffmpeg 安装说明（按需加载）

> 来源：ray-pse-video SKILL.md 分层卸载（v2.2.0）。

### ffmpeg 安装说明

本 skill 优先使用预装的独立 ffmpeg（编解码完整、PATH 全局可用）。

**情况 A：已预装（推荐）**

用户已安装 ffmpeg N-125258 至 `~/.workbuddy/binaries/ffmpeg/`，Bash/CMD/PowerShell 均可直接 `ffmpeg` 调用。

**情况 B：未预装 — 两种安装方式**

| 方式 | 命令 | 产物 | 优点 | 缺点 |
|------|------|------|------|------|
| pip 一键安装 | `pip install ffmpeg-downloader && python -m ffmpeg_downloader install` | 211MB 全编解码版 | 零配置，自动 PATH | 下载较慢（GitHub） |
| 手动下载 | 从 [BtbN Releases](https://github.com/BtbN/FFmpeg-Builds/releases) 下载 `ffmpeg-master-latest-win64-gpl.zip`，解压到 `~/.workbuddy/binaries/ffmpeg/` | 同上 | 可离线复用 | 需手动配置 PATH |

**情况 C：应急降级 — imageio-ffmpeg 缓存**

如果 pip 和手动下载均不可用，可复用系统 Python 中 imageio-ffmpeg 的缓存二进制：

```python
# 系统 Python 3.13.12 自带预下载的 ffmpeg v7.1
cached = r'C:\Users\rayzh\.workbuddy\binaries\python\versions\3.13.12\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe'
```

> ⚠️ 降级方案编解码支持有限（essentials build），无 libass/libx265/av1 等高级编码器，仅作应急使用。

**启动时检测逻辑（推荐放入 assembly 脚本）**：

```python
def get_ffmpeg():
    """按优先级查找 ffmpeg：PATH → 预装路径 → imageio 缓存 → 报错提示安装"""
    import shutil, os
    # 1. PATH 中已有（预装/手动安装后的正常情况）
    ff = shutil.which('ffmpeg')
    if ff: return ff
    # 2. 已知预装路径
    known = os.path.expandvars(r'%USERPROFILE%\.workbuddy\binaries\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe')
    if os.path.exists(known): return known
    # 3. imageio-ffmpeg 缓存降级
    legacy = os.path.expandvars(r'%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
    if os.path.exists(legacy): return legacy
    # 4. 均不可用 → 引导安装
    raise RuntimeError(
        'ffmpeg 未找到。请安装：\n'
        '  pip install ffmpeg-downloader && python -m ffmpeg_downloader install\n'
        '或下载 BtbN build 到 ~/.workbuddy/binaries/ffmpeg/'
    )
```
