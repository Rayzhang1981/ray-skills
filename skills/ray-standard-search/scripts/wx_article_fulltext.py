#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
wx_article_fulltext.py — 微信公众号文章图片全文抓取管线（ray-standard-search 2d 动作4 配套工具）

用途：公众号文章"全文=图片影印件"时，抓取正文图片、甄别、合并 PDF。
用法：
    python wx_article_fulltext.py <article_url> <output_dir> [--keep-page N,N,N]

流程（2026-09-25 实证 76 号文跑通）：
    ① curl/urllib 拿完整 HTML
    ② 正则抽 js_content 内 <img data-src="...">
    ③ 下载图片（按文件头魔数判真实类型，不信 URL 后缀）
    ④ （人工/多模态 Read 甄别正文图 vs 二维码/推广图——本脚本只负责下载与列清单）
    ⑤ --keep-page 指定正文页序号（如 1,2,3）→ PIL 合并 PDF + 单页 JPG

注意：正文文字 <2000 字符即"图片全文"，才需要本脚本；纯文字文章直接 WebFetch。
"""
import re
import sys
import os
import html as H
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "ignore")


def extract_js_content(html: str) -> str:
    m = re.search(r'<div[^>]*id="js_content"[^>]*>(.*)', html, re.S)
    if not m:
        raise RuntimeError("js_content NOT FOUND（可能非公众号文章页或被反爬）")
    return m.group(1)


def text_len_of(content: str) -> int:
    """正文文字量（判断是文字文章还是图片影印件）"""
    c = re.sub(r"<script.*?</script>|<style.*?</style>", "", content, flags=re.S)
    t = re.sub(r"<[^>]+>", "", c)
    t = H.unescape(t)
    return len([ch for ch in t if not ch.isspace()])


def list_images(content: str):
    return re.findall(r'<img[^>]*data-src="([^"]+)"[^>]*>', content)


def sniff_ext(data: bytes) -> str:
    if data[:3] == b"\xff\xd8\xff":
        return "jpg"
    if data[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    return "png"


def download(imgs, img_dir: str):
    os.makedirs(img_dir, exist_ok=True)
    saved = []
    for i, u in enumerate(imgs):
        req = urllib.request.Request(u, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        ext = sniff_ext(data)
        fn = os.path.join(img_dir, f"p{i}.{ext}")
        with open(fn, "wb") as f:
            f.write(data)
        saved.append((i, fn))
        print(f"  [{i}] {fn} {len(data)} bytes")
    return saved


def merge_pdf(saved, keep_pages, out_dir: str, resolution: float = 150.0):
    from PIL import Image
    pages = []
    for idx in keep_pages:
        fn = dict(saved)[idx]
        im = Image.open(fn).convert("RGB")
        im.save(os.path.join(out_dir, f"第{idx + 1}页.jpg"), "JPEG", quality=92)
        pages.append(im)
    pdf = os.path.join(out_dir, "影印件合并.pdf")
    pages[0].save(pdf, save_all=True, append_images=pages[1:], resolution=resolution)
    with open(pdf, "rb") as f:
        head = f.read(5)
    assert head == b"%PDF-", "PDF 头校验失败"
    print(f"PDF: {pdf} ({os.path.getsize(pdf)} bytes)")


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    url, out_dir = sys.argv[1], sys.argv[2]
    keep = None
    if "--keep-page" in sys.argv:
        keep = [int(x) for x in sys.argv[sys.argv.index("--keep-page") + 1].split(",")]

    html = fetch_html(url)
    content = extract_js_content(html)
    n_text = text_len_of(content)
    print(f"正文文字量: {n_text} 字符 → {'图片全文（走本管线）' if n_text < 2000 else '文字文章（可直接 WebFetch，无需本管线）'}")

    imgs = list_images(content)
    print(f"正文图片: {len(imgs)} 张")
    if not imgs:
        sys.exit(0)

    img_dir = os.path.join(out_dir, "_imgs")
    saved = download(imgs, img_dir)
    print("\n>>> 下一步：多模态逐张 Read，甄别正文图 vs 二维码/推广图 <<<")
    if keep:
        merge_pdf(saved, keep, out_dir)


if __name__ == "__main__":
    main()
