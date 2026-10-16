# -*- coding: utf-8 -*-
"""方案 B 收尾验收：① 案例回环（property 路径）；② JSON 可解析体检；③ 结构自检（SKILL.md 锚点）；④ 指纹"""
import sys, io, subprocess, json, hashlib, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
SK = r"C:\Users\rayzh\.workbuddy\skills\ray-chem-property"
Q = os.path.join(SK, "scripts", "query_reactivity.py")
ok = True

def run(args):
    r = subprocess.run([sys.executable, Q, *args], capture_output=True, text=True, encoding="utf-8")
    return json.loads(r.stdout)

print("=== ① 案例回环（property 路径）===")
a = run(["--cas", "10217-52-4"])
r1 = a["results"].get("危险品全书·禁配物", [])
ok &= bool(r1) and "氧化汞" in (r1[0].get("禁配物") or "")
print(f"  水合肼 10217-52-4 → 危险品全书 五字段 {'[v]' if r1 else '[x]'}（pages {r1[0]['pages'] if r1 else '-'}）")
b = run(["--name", "hydrogen peroxide"])
r2 = b["results"].get("CAMEO·材质反应性", []) + b["results"].get("CAMEO·无CAS(按名)", [])
ok &= bool(r2) and "metals" in str(r2[0].get("react", {}).get("common_materials") or "").lower()
print(f"  双氧水 name 查询 → CAMEO {'[v]' if r2 else '[x]'}"
      f"（{'CAS 主键' if b['results'].get('CAMEO·材质反应性') else '无CAS 按名兜底'})")
c = run(["--cas", "75-21-8"])
r3 = c["results"].get("CAMEO·材质反应性", [])
ok &= bool(r3) and "slow" in str(r3[0]["react"].get("water") or "").lower()
print(f"  环氧乙烷 75-21-8 → water 慢反应 {'[v]' if r3 else '[x]'}")

print("=== ② JSON 全件可解析 ===")
for f in ("禁配物-危险品全书.json", "材质反应性-CAMEO.json"):
    p = os.path.join(SK, "data", f)
    json.load(open(p, encoding="utf-8"))
    print(f"  [v] data/{f}  {os.path.getsize(p):,} B  "
          f"SHA={hashlib.sha256(open(p,'rb').read()).hexdigest().upper()[:16]}")

print("=== ③ SKILL.md 结构锚点 ===")
t = open(os.path.join(SK, "SKILL.md"), encoding="utf-8").read()
anchors = ["version: 3.6.0", "反应性/相容性字段秒查", "禁配物-危险品全书.json",
           "材质反应性-CAMEO.json", "query_reactivity.py", "2026-09-23", "分工铁律"]
for s in anchors:
    has = s in t
    print(f"  [{'[v]' if has else '[x]'}] 含 {s!r}")
    ok &= has
bad = t.count("version: 3.5.0")
print(f"  [{'[v]' if bad == 0 else '[x]'}] 旧版本号残留 {bad}")
ok &= bad == 0
# frontmatter 可被 yaml 解析
import re

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

fm = re.match(r"^---\n(.*?)\n---", t, re.S).group(1)
ok &= "ray-chem-property" in fm and "3.6.0" in fm
print("  [v] frontmatter 含 name+version")

print("=== ③b 既有索引零破坏（hash 抽查 3 个）===")
for f in ("AEGL索引.json", "危险品全书-通用卷索引.json", "SARA-物性索引.json"):
    p = os.path.join(SK, "data", f)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest().upper()[:16]
    print(f"  {f}: {h}")

print(f"\n总体：{'全部通过 [v]' if ok else '存在 FAIL'}")
sys.exit(0 if ok else 1)
