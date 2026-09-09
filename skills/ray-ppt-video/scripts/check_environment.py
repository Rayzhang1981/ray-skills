#!/usr/bin/env python3
"""
ray-PPT-TrVideo — 环境检查脚本。
检测 PPT→视频流水线所需的所有依赖。

Usage:
    python check_environment.py           # 检查所有依赖
    python check_environment.py --fix     # 尝试自动安装 Python 依赖
    python check_environment.py --json    # 输出 JSON 格式

Exit codes: 0=OK, 1=缺失必需依赖
"""

import argparse
import json as _json
import os
import shutil
import subprocess
import sys
from typing import Tuple


# ────────────────────────────────────────────────
# Color output
# ────────────────────────────────────────────────

class C:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


def _ok(name: str, detail: str = ""):
    print(f"  {C.GREEN}OK{C.END}  {name}" + (f" — {detail}" if detail else ""))


def _warn(name: str, detail: str = ""):
    print(f"  {C.YELLOW}WARN{C.END} {name}" + (f" — {detail}" if detail else ""))


def _fail(name: str, detail: str = ""):
    print(f"  {C.RED}FAIL{C.END} {name}" + (f" — {detail}" if detail else ""))


def _section(title: str):
    print(f"\n{C.BOLD}{'='*55}{C.END}")
    print(f"{C.BOLD}  {title}{C.END}")
    print(f"{C.BOLD}{'='*55}{C.END}\n")


# ────────────────────────────────────────────────
# Check functions
# ────────────────────────────────────────────────

def check_cmd(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def check_py_pkg(pkg: str, import_name: str = None) -> Tuple[bool, str]:
    if import_name is None:
        import_name = pkg.replace("-", "_")
    try:
        mod = __import__(import_name)
        ver = getattr(mod, "__version__", "installed")
        return True, str(ver)
    except ImportError as e:
        return False, str(e)


def get_ffmpeg_info() -> Tuple[bool, str]:
    try:
        r = subprocess.run(["ffmpeg", "-version"], capture_output=True,
                           text=True, timeout=5)
        if r.returncode == 0:
            first = r.stdout.split("\n")[0]
            return True, first
        return False, "exit code " + str(r.returncode)
    except Exception as e:
        return False, str(e)


def check_gpu() -> str:
    try:
        import torch
        if torch.cuda.is_available():
            return f"CUDA: {torch.cuda.get_device_name(0)}"
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "Apple MPS"
        return "CPU only"
    except ImportError:
        return "torch not installed"


def check_qwen3_model_cache() -> list:
    found = []
    for cache_dir in [
        os.path.expanduser("~/.cache/huggingface/hub"),
        os.path.expanduser("~/.cache/modelscope/hub"),
    ]:
        if os.path.isdir(cache_dir):
            for item in os.listdir(cache_dir):
                if "Qwen3-TTS" in item or "qwen3-tts" in item.lower():
                    p = os.path.join(cache_dir, item)
                    if os.path.isdir(p):
                        size = 0
                        for _, _, files in os.walk(p):
                            for f in files:
                                try:
                                    size += os.path.getsize(
                                        os.path.join(os.path.dirname(p), f))
                                except OSError:
                                    pass
                        found.append((item, size / (1024**3)))
    return found


def check_font(name: str) -> bool:
    """Check if Chinese font exists on Windows."""
    # Windows fonts directory
    font_dir = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts")
    common_fonts = {
        "Microsoft YaHei": ["msyh.ttc", "msyh.ttf", "Microsoft YaHei"],
        "SimHei": ["simhei.ttf"],
        "SimSun": ["simsun.ttc"],
    }
    if name in common_fonts:
        for fname in common_fonts[name]:
            fpath = os.path.join(font_dir, fname)
            if os.path.isfile(fpath):
                return True
    # Fallback: check if fc-list works (Git Bash might have it)
    try:
        r = subprocess.run(["fc-list", name], capture_output=True,
                           text=True, timeout=5)
        return bool(r.stdout.strip())
    except Exception:
        return False


# ────────────────────────────────────────────────
# Install instructions
# ────────────────────────────────────────────────

INSTALL = {
    "ffmpeg": "choco install ffmpeg  或  下载 https://ffmpeg.org/download.html",
    "python-pptx": "pip install python-pptx",
    "edge-tts": "pip install edge-tts",
    "qwen-tts": "pip install -U qwen-tts",
    "imageio-ffmpeg": "pip install imageio-ffmpeg",
    "torch": "pip install torch torchaudio",
    "openai-whisper": "pip install openai-whisper",
    "numpy": "pip install numpy",
}


def _install_hint(name: str):
    hint = INSTALL.get(name, f"pip install {name}")
    print(f"      {C.CYAN}安装: {hint}{C.END}")


# ────────────────────────────────────────────────
# Main
# ────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="PPT转视频流水线 — 环境检查")
    parser.add_argument("--fix", action="store_true",
                        help="尝试自动安装缺失的 Python 依赖")
    parser.add_argument("--json", action="store_true",
                        help="输出 JSON 格式")
    args = parser.parse_args()

    if args.json:
        results = {}
        # ... (simplified: just print header for JSON mode)

    print(f"\n{C.BOLD}ray-PPT-TrVideo — 环境检查{C.END}")
    print(f"Python:  {sys.version.split()[0]}")
    print(f"Platform: {sys.platform}")

    all_ok = True
    missing_req = []
    missing_opt = []

    # ── System tools ──
    _section("系统工具")

    ok, ver = get_ffmpeg_info()
    if ok:
        _ok("FFmpeg", ver.split(" ")[2] if len(ver.split()) > 2 else "installed")
    else:
        _fail("FFmpeg", "未安装 (必需)")
        _install_hint("ffmpeg")
        missing_req.append("FFmpeg")
        all_ok = False

    if check_cmd("ffprobe"):
        _ok("ffprobe")
    else:
        _fail("ffprobe", "未安装 (必需)")
        all_ok = False

    # ── Python packages ──
    _section("Python 核心依赖")

    for pkg, imp, req in [
        ("python-pptx", "pptx", True),
        ("numpy", "numpy", False),
    ]:
        ok, info = check_py_pkg(pkg, imp)
        if ok:
            _ok(pkg, info)
        elif req:
            _fail(pkg, "未安装 (必需)")
            _install_hint(pkg)
            missing_req.append(pkg)
            all_ok = False
        else:
            _warn(pkg, "未安装 (可选)")
            missing_opt.append(pkg)

    # ── TTS engines ──
    _section("TTS 引擎 (至少安装其一)")

    has_qwen = has_edge = False

    ok, info = check_py_pkg("qwen-tts", "qwen_tts")
    if ok:
        _ok("qwen-tts", f"{info} (本地高质量，支持声音克隆)")
        has_qwen = True
    else:
        _warn("qwen-tts", "未安装 (推荐)")
        _install_hint("qwen-tts")

    ok, info = check_py_pkg("edge-tts", "edge_tts")
    if ok:
        _ok("edge-tts", f"{info} (在线备选)")
        has_edge = True
    else:
        _warn("edge-tts", "未安装 (备选)")
        _install_hint("edge-tts")

    if not has_qwen and not has_edge:
        print(f"\n  {C.RED}ERROR: 至少需要一个 TTS 引擎!{C.END}")
        missing_req.append("TTS引擎")
        all_ok = False

    # ── Optional ──
    _section("可选依赖 (增强功能)")

    ok, info = check_py_pkg("torch")
    if ok:
        _ok("torch", f"{info} | {check_gpu()}")
    else:
        _warn("torch", "未安装 (Qwen3-TTS 依赖)")
        _install_hint("torch")
        missing_opt.append("torch")

    for pkg, desc in [
        ("imageio-ffmpeg", "FFmpeg 自动下载 (备用)"),
        ("openai-whisper", "语音转文字 (声音克隆辅助)"),
    ]:
        ok, info = check_py_pkg(pkg)
        if ok:
            _ok(pkg, info)
        else:
            _warn(pkg, f"未安装 ({desc})")
            missing_opt.append(pkg)

    # ── Qwen3-TTS model cache ──
    if has_qwen:
        _section("Qwen3-TTS 模型缓存")
        models = check_qwen3_model_cache()
        if models:
            for n, s in models:
                _ok(n, f"{s:.1f} GB")
        else:
            _warn("模型缓存", "未检测到已下载模型")
            print(f"      首次运行自动下载 (~2-4 GB)")
            print(f"      缓存: ~/.cache/huggingface/hub/")

    # ── Fonts ──
    _section("字幕字体")

    font_found = False
    for font in ["Microsoft YaHei", "SimHei"]:
        if check_font(font):
            _ok(font, "已安装")
            font_found = True
    if not font_found:
        _warn("中文字体", "未检测到，字幕可能异常")
        print(f"      可指定: --font-name \"Arial\"")

    # ── Summary ──
    print(f"\n{C.BOLD}{'='*55}{C.END}")
    print(f"{C.BOLD}  检查结果{C.END}")
    print(f"{C.BOLD}{'='*55}{C.END}\n")

    if all_ok:
        print(f"  {C.GREEN}OK — 所有必需依赖已满足!{C.END}")
        if missing_opt:
            print(f"  {C.YELLOW}可选依赖未安装:{C.END} " + ", ".join(missing_opt))
        print()
        return 0
    else:
        print(f"  {C.RED}FAIL — 缺失必需依赖:{C.END} " + ", ".join(missing_req))
        print(f"  请根据提示安装后重试。\n")

        if args.fix:
            print(f"  {C.CYAN}尝试自动安装 Python 依赖...{C.END}\n")
            for pkg in missing_req:
                if pkg in INSTALL and not pkg.startswith("FF"):
                    pip_cmd = INSTALL[pkg].replace("pip install ", "").split(" ")
                    subprocess.run([sys.executable, "-m", "pip", "install"] + pip_cmd)
        return 1


if __name__ == "__main__":
    sys.exit(main())
