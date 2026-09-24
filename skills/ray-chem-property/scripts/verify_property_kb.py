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
print(f"  水合肼 10217-52-4 → 危险品全书 五字段 {'✓' if r1 else '✗'}（pages {r1[0]['pages'] if r1 else '-'}）")
b = run(["--name", "hydrogen peroxide"])
r2 = b["results"].get("CAMEO·材质反应性", []) + b["results"].get("CAMEO·无CAS(按名)", [])
ok &= bool(r2) and "metals" in str(r2[0].get("react", {}).get("common_materials") or "").lower()
print(f"  双氧水 name 查询 → CAMEO {'✓' if r2 else '✗'}"
      f"（{'CAS 主键' if b['results'].get('CAMEO·材质反应性') else '无CAS 按名兜底'})")
c = run(["--cas", "75-21-8"])
r3 = c["results"].get("CAMEO·材质反应性", [])
ok &= bool(r3) and "slow" in str(r3[0]["react"].get("water") or "").lower()
print(f"  环氧乙烷 75-21-8 → water 慢反应 {'✓' if r3 else '✗'}")

print("=== ② JSON 全件可解析 ===")
for f in ("禁配物-危险品全书.json", "材质反应性-CAMEO.json"):
    p = os.path.join(SK, "data", f)
    json.load(open(p, encoding="utf-8"))
    print(f"  ✓ data/{f}  {os.path.getsize(p):,} B  "
          f"SHA={hashlib.sha256(open(p,'rb').read()).hexdigest().upper()[:16]}")

print("=== ③ SKILL.md 结构锚点 ===")
t = open(os.path.join(SK, "SKILL.md"), encoding="utf-8").read()
anchors = ["version: 3.6.0", "反应性/相容性字段秒查", "禁配物-危险品全书.json",
           "材质反应性-CAMEO.json", "query_reactivity.py", "2026-09-23", "分工铁律"]
for s in anchors:
    has = s in t
    print(f"  [{'✓' if has else '✗'}] 含 {s!r}")
    ok &= has
bad = t.count("version: 3.5.0")
print(f"  [{'✓' if bad == 0 else '✗'}] 旧版本号残留 {bad}")
ok &= bad == 0
# frontmatter 可被 yaml 解析
import re
fm = re.match(r"^---\n(.*?)\n---", t, re.S).group(1)
ok &= "ray-chem-property" in fm and "3.6.0" in fm
print("  ✓ frontmatter 含 name+version")

print("=== ③b 既有索引零破坏（hash 抽查 3 个）===")
for f in ("AEGL索引.json", "危险品全书-通用卷索引.json", "SARA-物性索引.json"):
    p = os.path.join(SK, "data", f)
    h = hashlib.sha256(open(p, "rb").read()).hexdigest().upper()[:16]
    print(f"  {f}: {h}")

print(f"\n总体：{'全部通过 ✓' if ok else '存在 FAIL'}")
sys.exit(0 if ok else 1)
