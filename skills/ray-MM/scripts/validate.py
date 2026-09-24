# -*- coding: utf-8 -*-
"""
ray-MM 纪要验证 v1：检查生成的 DOCX

用法：
    python validate.py <output.docx> [--need "关键词1,关键词2"] [--rows N]

检查项：
1. 是否为合法 zip 且含 word/document.xml
2. 编码：全文无 U+FFFD 替换字符（中文乱码零容忍）
3. 统计段落数 / 表格数 / 表格行数
4. 关键内容存在性（--need 逗号分隔，默认抽样常用词）
"""
import argparse
import io
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def collect_texts(xml):
    root = ET.fromstring(xml)
    texts = []
    for p in root.findall(".//w:p", NS):
        t = "".join(n.text or "" for n in p.iter("{%s}t" % NS["w"]))
        if t.strip():
            texts.append(t.strip())
    # 表格内文字也纳入（表格里每格有自己的 w:p，上面已覆盖）
    return texts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("docx")
    ap.add_argument("--need", default="", help="逗号分隔的关键词，缺失时报错")
    ap.add_argument("--rows", type=int, default=None,
                    help="期望的待办表格数据行数（含表头），不匹配则警告")
    args = ap.parse_args()

    try:
        z = zipfile.ZipFile(args.docx)
        xml = z.read("word/document.xml").decode("utf-8")
    except Exception as e:
        print(f"[FAIL] 无法读取 docx: {e}")
        sys.exit(1)

    print(f"[OK] 文件可读: {args.docx}")

    n_bad = xml.count("\ufffd")
    if n_bad:
        print(f"[FAIL] 发现 {n_bad} 个 U+FFFD 乱码字符！")
        sys.exit(1)
    print("[OK] 编码检查：无乱码 (0 个 U+FFFD)")

    texts = collect_texts(xml)
    n_tbl = len(ET.fromstring(xml).findall(".//w:tbl", NS))
    print(f"[OK] 段落数={len(texts)} 表格数={n_tbl}")

    if args.rows is not None:
        rows = len(ET.fromstring(xml).findall(".//w:tbl", NS)[-1].findall("w:tr", NS))
        status = "OK" if rows == args.rows else "WARN(实际≠期望)"
        print(f"[{status}] 最后一张表格行数={rows}（期望 {args.rows}）")

    full = "".join(texts)
    missing = [k for k in [k.strip() for k in args.need.split(",") if k.strip()]
               if k not in full]
    if missing:
        print(f"[FAIL] 缺少关键内容: {missing}")
        sys.exit(1)
    if args.need:
        print(f"[OK] 关键内容全部存在: {args.need}")

    print("[OK] 验证通过 ✅")


if __name__ == "__main__":
    main()