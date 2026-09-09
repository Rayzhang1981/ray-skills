# -*- coding: utf-8 -*-
"""NIST Webbook 标识页直抓：英文名/CAS → CAS/分子式/分子量/InChI/别名。

定位：ray-chem-property 的「标识核验 + 交叉验证」源（Step 1 Agent 补采）。
NIST `cbook.cgi` 返回的标识页包含 CAS/Formula/Molecular weight/InChI/别名列表，
是 PubChem 之外唯一可程序化直抓的权威标识源（实测 2026-08-15，urllib 即可）。

用法：
  python nist_verify.py acetone --out output/          # 英文名（默认）
  python nist_verify.py acetone formaldehyde --out output/   # 批量
  python nist_verify.py 67-64-1 --by cas --out output/ # 按 CAS 查
  python nist_verify.py 丙酮 --out output/             # 中文名会提示转 CAS/英文名

输出：output/nist_{cas or name}.json（无 CAS 时用查询名），每字段带 source_url。
"""
import argparse
import html as html_mod
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0 nist-verify/1.0"}


def fetch(url, retry=4):
    """抓取页面，带重试。返回 HTML 文本或 None。"""
    for i in range(retry):
        try:
            req = urllib.request.Request(url, headers=UA)
            r = urllib.request.urlopen(req, timeout=25)
            return r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(1.5 * (i + 1))
        except Exception:
            time.sleep(1.5 * (i + 1))
    return None


def _val(html_text, label):
    """提取 '<label...>:</strong> <值>' 中的值（容忍 <a>/<sub> 等标签穿插）。

    实测 NIST 页面结构（2026-08-15）：
      <li><strong><a ...>Formula</a>:</strong> C<sub>3</sub>H<sub>6</sub>O</li>
      <li><strong>CAS Registry Number:</strong> 67-64-1</li>
    """
    m = re.search(re.escape(label) + r".*?:\s*</strong>\s*(.*?)</li>", html_text, re.S)
    if not m:
        return ""
    t = re.sub(r"<[^>]+>", "", m.group(1))  # 去 <sub>/<span>/<a> 等标签
    t = html_mod.unescape(t)
    return re.sub(r"\s+", "", t).strip()


def parse_identifier_page(html_text):
    """解析 NIST 标识页 → dict。返回 None 表示页面不是有效结果页。"""
    if not html_text or '<h1 id="Top">' not in html_text:
        return None
    out = {"name": "", "cas": "", "formula": "", "mw": "", "inchi": "", "inchikey": "", "aliases": []}

    # 名称：<h1 id="Top">Acetone</h1>
    m = re.search(r'<h1 id="Top">(.*?)</h1>', html_text, re.S)
    if m:
        out["name"] = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()

    # CAS
    m = re.search(r"CAS Registry Number.*?(\d{2,7}-\d{2}-\d)", html_text)
    if m:
        out["cas"] = m.group(1)

    # Formula（去空格还原，如 C 3 H 6 O → C3H6O）
    out["formula"] = _val(html_text, "Formula")

    # Molecular weight
    m = re.search(r"Molecular weight.*?:\s*</strong>\s*([\d.]+)", html_text)
    if m:
        out["mw"] = m.group(1)

    # InChI / InChIKey（<span class="inchi-text"> 内）
    m = re.search(r"IUPAC Standard InChI:\s*</strong>\s*<span class=\"inchi-text\">([^<]+)", html_text)
    if m:
        out["inchi"] = m.group(1).strip()
    m = re.search(r"IUPAC Standard InChIKey:\s*</strong>\s*<span class=\"inchi-text\">([^<]+)", html_text)
    if m:
        out["inchikey"] = m.group(1).strip()

    # Other names（分号分隔）
    m = re.search(r"Other names:\s*</strong>\s*(.*?)</li>", html_text, re.S)
    if m:
        raw = html_mod.unescape(re.sub(r"<[^>]+>", "", m.group(1)))
        out["aliases"] = [x.strip() for x in re.split(r";\s*", raw) if x.strip()]

    return out


def verify(name_or_cas, by_cas=False):
    """查一个标识。返回 dict（含 query/url/数据），失败时 cas/name 为空。

    注意：NIST 的 cbook.cgi 不支持 CAS 作为 URL 参数（?CAS= 会 400），
    CAS 也要走 Name 参数（?Name=<CAS> 等效于表单 CAS 输入，实测有效）。
    """
    if by_cas:
        url = f"https://webbook.nist.gov/cgi/cbook.cgi?Name={urllib.parse.quote(name_or_cas)}&Units=SI"
        key = name_or_cas
    else:
        url = f"https://webbook.nist.gov/cgi/cbook.cgi?Name={urllib.parse.quote(name_or_cas)}&Units=SI"
        key = name_or_cas
    html_text = fetch(url)
    rec = parse_identifier_page(html_text)
    if rec is None:
        return {"query": name_or_cas, "by_cas": by_cas, "found": False, "url": url}
    rec.update({"query": name_or_cas, "by_cas": by_cas, "found": True, "url": url})
    return rec


def main():
    ap = argparse.ArgumentParser(description="NIST Webbook 标识页直抓（交叉核验）")
    ap.add_argument("names", nargs="+", help="英文名或 CAS 号（可多个）")
    ap.add_argument("--by-cas", action="store_true", help="输入按 CAS 解析")
    ap.add_argument("--out", default=".", help="输出目录（默认当前目录）")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    all_recs = []
    for n in args.names:
        print(f"[nist] 查询: {n} ({'CAS' if args.by_cas else 'Name'})", flush=True)
        rec = verify(n, by_cas=args.by_cas)
        all_recs.append(rec)
        if rec.get("found"):
            print(f"  -> {rec['name']} | CAS {rec['cas']} | {rec['formula']} | MW {rec['mw']} | 别名 {len(rec['aliases'])} 个", flush=True)
        else:
            print(f"  -> 未命中（NIST 无此条目）", flush=True)
        # 落盘：nist_<cas 或 query>.json
        fname = rec["cas"] if rec.get("found") and rec["cas"] else re.sub(r"[^\w.-]", "_", n)
        fp = os.path.join(args.out, f"nist_{fname}.json")
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(rec, f, ensure_ascii=False, indent=2)
        print(f"  -> 已保存 {fp}", flush=True)
        time.sleep(0.5)  # 礼貌限速

    print(f"[nist] DONE: {len(all_recs)} 条，命中 {sum(1 for r in all_recs if r.get('found'))}")


if __name__ == "__main__":
    main()
