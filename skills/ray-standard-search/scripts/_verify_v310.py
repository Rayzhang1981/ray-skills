# -*- coding: utf-8 -*-
"""v3.1.0 验收器（落盘执行，避开 bash 转义吃反斜杠的坑）"""
import re
import py_compile

P = r"C:\Users\rayzh\.workbuddy\skills\ray-standard-search\SKILL.md"
S = r"C:\Users\rayzh\.workbuddy\skills\ray-standard-search\scripts\wx_article_fulltext.py"

b = open(P, "rb").read()
t = b.decode("utf-8")

# 版本行用字面匹配（不用 \s 正则，排除转义干扰）
fm_ver = re.search(r"version: ([0-9.]+)", t).group(1)

final = {
    "frontmatter version == 3.1.0": fm_ver == "3.1.0",
    "维护记录 v3.1.0 行": "v3.1.0：**2d" in t,
    "2d SOP 标题": "2d. 微信公众号搜索（可执行 SOP）" in t,
    "site: 词法": "site:mp.weixin.qq.com" in t,
    "白名单（河北EHS）": "河北EHS" in t,
    "搜狗仅人工": "禁止脚本自动化" in t,
    "脚本引用": "wx_article_fulltext.py" in t,
    "LRN-20260925-001": "LRN-20260925-001" in t,
    "旧占位消失": "同步搜索公众号文章：" not in t,
    "无乱码": t.count(chr(0xFFFD)) == 0,
}
ok = True
for k, v in final.items():
    print(("PASS" if v else "FAIL"), k)
    ok = ok and v

crlf = b.count(b"\r\n")
bare_lf = b.count(b"\n") - crlf
eol_ok = bare_lf == 0
print(f"EOL: CRLF={crlf}, bareLF={bare_lf} ->", "PASS 纯CRLF" if eol_ok else "FAIL MIXED")

py_compile.compile(S, doraise=True)
print("PASS 脚本语法编译通过")

print("size:", len(b))
print("=== ALL PASS ===" if ok and eol_ok else "=== HAS FAIL ===")
