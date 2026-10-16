#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ray-hazop-lopa · MAWP 估算入口（**薄封装**，2026-10-08 起）

⚠️ 已收口：MAWP 的**唯一实现**现位于 `ray-pe-calc` 模块 10：
      ray-pe-calc/modules/pressure_vessel/{calc.py, materials.py}
   本文件仅作**兼容入口**（旧参数名 → 新参数的映射 + 委派），不再自行实现公式，
   以避免"同一公式两份实现、各自漂移"。

── 为什么搬迁 ──────────────────────────────────────────────────────────────
MAWP 是**设备承压能力的数值计算**，属"设备定尺"族；本生态既有分工已把同类
计算（泄放面积/安全阀喉径数值）指向 `ray-pe-calc`。MAWP 同理归执行层，
`ray-hazop-lopa` 保留入口但不持公式。

── 新入口能力（本次一并获得）────────────────────────────────────────────────
  · 内压筒体（GB/T 150.3-2011 式3-1 反解）
  · **标准椭圆封头**（式5-1 反解，K=1）
  · **外压/真空量级** + **加强圈间距反算**
  · **材质库（带可信度分级）+ 材质使用限制检查**（Q235B 的 20 ℃ 下限等一票否决项）
  · φ 0.85/1.0 两档、δe 自动计算、受控自检（正例/负控/单位/边界）

── 旧参数 → 新参数 ─────────────────────────────────────────────────────────
  --t <δe>      →  --de <δe>      （**语义不变：都要求有效厚度，不是名义厚度**）
  --S <MPa>     →  --S <MPa>      （同）
  --E <φ>       →  --phi <φ>      （同）
  --D <内径mm>  →  --D <内径mm>   （同）
  --code gb     →  （默认即 GB/T 150.3）；asme 请直接用 ray-pe-calc 模块并 --phi
  --name "…"    →  仅用于回显，新入口不接收（设备名由调用方写进报告）

── 用法 ────────────────────────────────────────────────────────────────────
  python calc_mawp.py --D 1600 --t 3.7 --S 120 --E 0.85 --name "容器A"
  python calc_mawp.py --D 1000 --t 3.55 --S 116 --E 0.85 --ext-L 2000
  python calc_mawp.py --selftest            # 委派到新模块自检
  python calc_mawp.py --where               # 只打印新模块位置
"""
import argparse
import os
import subprocess
import sys

def _console_safe():
    """控制台编码护栏（2026-10-09 舰队级修复）。

    中文 Windows 下 stdout/stderr 走 cp936(GBK)。**输出被重定向或经管道捕获时**
    （自动验证 / 日志 / CI / subprocess PIPE），Python 按 locale 编码写流，
    遇到 GBK 无法表示的字符即抛 UnicodeEncodeError，**整段输出中断**；
    而交互式控制台走 WriteConsoleW(UTF-16)，同一字符却无碍
    => 该缺陷只在「捕获输出」时显形，最易漏测。

    处理：**保持流原编码不变**（中文在 GBK 控制台仍正常），
    仅把不可表示的字符降级为 '?'，从而永不中断。
    注意：不要改成 encoding="utf-8" —— 那会让 GBK 控制台下的中文变乱码。
    """
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(errors="replace")
        except Exception:
            pass


_console_safe()


HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable

# 新模块定位：兄弟目录优先（skills/ray-hazop-lopa → skills/ray-pe-calc）
CANDIDATES = [
    os.path.join(HERE, "..", "..", "ray-pe-calc", "modules", "pressure_vessel", "calc.py"),
    os.path.expanduser("~/.workbuddy/skills/ray-pe-calc/modules/pressure_vessel/calc.py"),
    os.path.expanduser("~/.agents/skills/ray-pe-calc/modules/pressure_vessel/calc.py"),
]


def locate():
    for c in CANDIDATES:
        p = os.path.normpath(c)
        if os.path.isfile(p):
            return p
    return None


def main():
    # 控制台护栏：stdout 被重定向/管道捕获时，GBK 控制台遇非 GBK 字符会中断整个输出
    # （2026-10-09 实证：本封装 --selftest 委派的子进程曾因此中断）。保持原编码，仅降级不可编码字符。
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(errors="replace")
        except Exception:
            pass

    ap = argparse.ArgumentParser(
        description="MAWP 估算（薄封装 → ray-pe-calc 模块 10）")
    ap.add_argument("--D", type=float, help="**内径 Di** mm")
    ap.add_argument("--t", type=float, help="**有效厚度 δe** mm（= 名义厚度 - C1 - C2）")
    ap.add_argument("--S", type=float, help="设计温度下许用应力 [σ]t MPa")
    ap.add_argument("--E", type=float, default=0.85, help="焊接接头系数 φ（局部 RT 0.85；100%% RT 1.0）")
    ap.add_argument("--code", choices=["gb", "asme"], default="gb", help="（仅回显）默认 gb")
    ap.add_argument("--name", default="设备", help="（仅回显）设备名")
    ap.add_argument("--ext-L", dest="extL", type=float, default=None,
                    help="另算外压：给无支撑长度 mm")
    ap.add_argument("--selftest", action="store_true", help="委派到新模块自检")
    ap.add_argument("--where", action="store_true", help="只打印新模块位置")
    a = ap.parse_args()

    target = locate()
    if a.where:
        print("MAWP 唯一实现位置：%s" % (target or "**未找到**（请检查 ray-pe-calc 是否已安装）"))
        return 0 if target else 3
    if not target:
        print("[中止] 找不到 ray-pe-calc 的 pressure_vessel 模块。已尝试：")
        for c in CANDIDATES:
            print("   %s" % os.path.normpath(c))
        print("-> 请确认 ray-pe-calc 已安装；或直接调用：python <ray-pe-calc>/modules/pressure_vessel/calc.py --help")
        return 3

    if a.selftest:
        return subprocess.call([PY, target, "--selftest"])

    if a.D is None or a.t is None:
        print("[中止] 须给 --D（内径 mm）与 --t（**有效厚度 δe** mm，不是名义厚度）。")
        return 2

    cmd = [PY, target, "--D", "%g" % a.D, "--de", "%g" % a.t, "--phi", "%g" % a.E]
    if a.S is not None:
        cmd += ["--S", "%g" % a.S]
    if a.extL is not None:
        cmd += ["--L", "%g" % a.extL]

    print("── %s ──（经薄封装调用 ray-pe-calc/pressure_vessel）" % a.name)
    if a.code == "asme":
        print("[!] --code asme 为新模块未覆盖的口径（新模块默认 GB/T 150.3）；")
        print("   如需 ASME UG-27 口径请自行换算 R = Di/2 后按 UG-27 计算，或在 ray-pe-calc 增补模块。")
    rc = subprocess.call(cmd)
    if rc == 0:
        print("\n注：参数语义三连——`--D` 内径 ｜ `--t/--de` **有效厚度** ｜ `--S` **设计温度下**许用应力。")
        print("    材质使用限制（准不准用）与许用应力（能承多少压）**同等重要**，勿只算前者。")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
