# -*- coding: utf-8 -*-
"""
ray-hazop-lopa · 双输出④：HTML 报告 → PDF / Word
  PDF: Edge headless --print-to-pdf（Windows 保真）
  Word: 优先 pandoc（存在时）；否则提示可用浏览器"另存为 docx"
用法: python to_word_pdf.py report.html --pdf
      python to_word_pdf.py report.html --word
      python to_word_pdf.py report.html --both
"""
import argparse, os, shutil, subprocess, sys

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

def find_edge():
    for p in EDGE_CANDIDATES:
        if os.path.isfile(p):
            return p
    return shutil.which('msedge')

def to_pdf(html, out=None):
    edge = find_edge()
    if not edge:
        print("[ERROR] 未找到 Edge，无法转 PDF")
        return False
    out = out or os.path.splitext(html)[0] + '.pdf'
    uri = 'file:///' + html.replace('\\', '/')
    cmd = [edge, '--headless', '--disable-gpu', '--print-to-pdf=' + out, uri]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if os.path.isfile(out):
        print(f"[OK] PDF: {out}（{os.path.getsize(out)//1024} KB）")
        return True
    print(f"[FAIL] 转 PDF 失败: {r.stderr[:300]}")
    return False

def to_word(html, out=None):
    out = out or os.path.splitext(html)[0] + '.docx'
    if shutil.which('pandoc'):
        r = subprocess.run(['pandoc', html, '-o', out, '--standalone'],
                           capture_output=True, text=True, timeout=120)
        if os.path.isfile(out):
            print(f"[OK] Word: {out}（{os.path.getsize(out)//1024} KB，pandoc 转换）")
            return True
        print(f"[WARN] pandoc 失败: {r.stderr[:200]}，尝试浏览器另存")
    print("[提示] 无 pandoc：请在浏览器打开 HTML → 打印 → 另存为 Word（或装 pandoc 后重试）")
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('html')
    ap.add_argument('--pdf', action='store_true')
    ap.add_argument('--word', action='store_true')
    ap.add_argument('--both', action='store_true')
    a = ap.parse_args()
    if not os.path.isfile(a.html):
        print("[ERROR] 文件不存在")
        sys.exit(1)
    ok = True
    if a.pdf or a.both:
        ok &= to_pdf(a.html)
    if a.word or a.both:
        ok &= to_word(a.html)
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
