#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""query_fallback.py -- chemical-glossary 备查池查询（候选池，永不直接采用）

Usage:
  python query_fallback.py reactor            # EN -> ZH
  python query_fallback.py 储罐               # ZH -> EN（查询词含中文自动识别）
  python query_fallback.py reactor -d chemical_engineering -n 15

Data: ~/.workbuddy/local-refs/chemical-glossary/data/
  glossary_all.json  151,337 entries [{en, zh}, ...]
  by_domain.json     16 域分组（general_chemistry / chemical_engineering / ...）

流程规则：命中只是"候选"，不是裁决 --
  1) 应回裁决优先级 1-3 级（术语在线 / 国标 / CNKI）验证；
  2) 验证通过后按六列 schema 写入 data/termbase/（来源列标验证源，不标本数据集）；
  3) 数据集收录旧译名（矽/比重年代词），验证时注意规范更替。
"""
import argparse
import io
import json
import os
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


DEFAULT_DATA = os.path.expanduser(
    "~/.workbuddy/local-refs/chemical-glossary/data/glossary_all.json"
)


def load(domain=None):
    if domain:
        path = os.path.join(os.path.dirname(DEFAULT_DATA), "by_domain.json")
        groups = json.load(io.open(path, encoding="utf-8"))
        if domain not in groups:
            sys.exit("unknown domain: %s (keys in by_domain.json)" % domain)
        return groups[domain], domain
    return json.load(io.open(DEFAULT_DATA, encoding="utf-8")), "all"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    ap = argparse.ArgumentParser(
        description="chemical-glossary fallback query (candidates only, never adopt directly)"
    )
    ap.add_argument("term", help="query term (EN or ZH, auto-detected)")
    ap.add_argument("-d", "--domain", default=None,
                    help="restrict to one domain, e.g. chemical_engineering")
    ap.add_argument("-n", "--num", type=int, default=10,
                    help="max output rows (default 10)")
    args = ap.parse_args()

    term = args.term.strip()
    if not term:
        sys.exit("empty term")

    data, src = load(args.domain)

    # 含中文 => ZH->EN；否则 EN->ZH
    key, other = ("zh", "en") if any("\u4e00" <= c <= "\u9fff" for c in term) else ("en", "zh")
    tl = term.lower()

    exact, prefix, sub = [], [], []
    for row in data:
        v = (row.get(key) or "").strip()
        if not v:
            continue
        vl = v.lower()
        if vl == tl:
            exact.append(row)
        elif vl.startswith(tl):
            prefix.append(row)
        elif tl in vl:
            sub.append(row)

    seen = set()
    hits = []
    for rows in (exact, prefix, sub):
        for r in rows:
            k = (r.get("en"), r.get("zh"))
            if k not in seen:
                seen.add(k)
                hits.append(r)
    hits = hits[: args.num]

    print("SOURCE: %s | QUERY: %s | HITS: %d" % (src, term, len(hits)))
    print("RULE: candidates only -- verify via adjudication tier 1-3 before adopting")
    if not hits:
        print("NO HIT")
        return
    for r in hits:
        v = (r.get(key) or "").strip().lower()
        tag = "EXACT " if v == tl else ("PREFIX" if v.startswith(tl) else "SUBSTR")
        print("%s  %s  ->  %s" % (tag, r.get(key), r.get(other)))


if __name__ == "__main__":
    main()
