# -*- coding: utf-8 -*-
"""
ray-MM 输入适配层 v1：多格式会议材料 → 统一转写文本（transcript.md）

用途：把「任意格式会议材料」提取为结构化的 Markdown 转写文本，供纪要生成步骤消费。
支持：.md/.txt/.pdf/.docx/.xlsx/.xlsm/.pptx/.jpg/.jpeg/.png（OCR）

用法：
    python input-extract.py <输入文件或目录> [--ocr] [--out <输出目录>]

规则：
- 单文件 → 输出 <同名>.transcript.md（与源文件同目录，或 --out 指定目录）
- 目录 → 遍历目录内所有受支持文件，逐个输出
- 文本类（md/txt）直接复制内容；PDF 优先文本层，无文本层则提示 --ocr
- 图片 OCR 用 Tesseract（chi_sim+eng），tessdata 默认在 ~/.workbuddy/tessdata/
- 失败的文件打印 ERROR 行，不中断批量
"""
import argparse
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SUPPORTED = {
    ".md": "text", ".txt": "text", ".markdown": "text",
    ".pdf": "pdf",
    ".docx": "docx", ".doc": "docx_legacy",
    ".xlsx": "xlsx", ".xlsm": "xlsx",
    ".pptx": "pptx",
    ".jpg": "ocr", ".jpeg": "ocr", ".png": "ocr", ".bmp": "ocr", ".tiff": "ocr",
}


def extract_text(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def extract_pdf(path, ocr=False):
    try:
        import pdfplumber
    except ImportError:
        return "[ERROR] 缺少 pdfplumber：pip install pdfplumber"
    parts = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            parts.append(f"\n===== 第 {i+1} 页 =====")
            txt = page.extract_text() or ""
            if txt.strip():
                parts.append(txt)
            elif ocr:
                img_text = ocr_pdf_page(page)
                parts.append(img_text if img_text.strip() else "[本页 OCR 无结果]")
            else:
                parts.append("[本页无文本层，建议加 --ocr 或确认扫描件]")
    return "\n".join(parts)


def ocr_pdf_page(page):
    """将 PDF 页面渲染为图片再 OCR（需 PyMuPDF 渲染）。"""
    import tempfile
    try:
        import fitz  # PyMuPDF

        pix = page.to_image(resolution=200)
        img_path = os.path.join(tempfile.gettempdir(), "_ray_mm_tmp_page.png")
        pix.save(img_path)
        try:
            return extract_ocr(img_path)
        finally:
            if os.path.exists(img_path):
                os.remove(img_path)
    except ImportError:
        return "[ERROR] 页面无文本层且缺 PyMuPDF：pip install pymupdf"
    except Exception as e:
        return f"[ERROR] 页面 OCR 失败：{e}"


def extract_docx(path):
    try:
        import docx  # python-docx
    except ImportError:
        return "[ERROR] 缺少 python-docx：pip install python-docx"
    d = docx.Document(path)
    parts = []
    for p in d.paragraphs:
        if p.text.strip():
            parts.append(p.text)
    for t in d.tables:
        parts.append("\n[表格]")
        for row in t.rows:
            parts.append(" | ".join(c.text.strip() for c in row.cells))
    return "\n".join(parts)


def extract_xlsx(path):
    try:
        import openpyxl
    except ImportError:
        return "[ERROR] 缺少 openpyxl：pip install openpyxl"
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    parts = []
    for ws in wb.worksheets:
        parts.append(f"\n===== Sheet: {ws.title} =====")
        for row in ws.iter_rows(values_only=True):
            vals = [str(v) if v is not None else "" for v in row]
            if any(vals):
                parts.append(" | ".join(vals))
    return "\n".join(parts)


def extract_pptx(path):
    try:
        from pptx import Presentation
    except ImportError:
        return "[ERROR] 缺少 python-pptx：pip install python-pptx"
    prs = Presentation(path)
    parts = []
    for i, slide in enumerate(prs.slides, 1):
        parts.append(f"\n===== 幻灯片 {i} =====")
        for shape in slide.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    t = "".join(r.text for r in para.runs)
                    if t.strip():
                        parts.append(t)
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text
            if notes.strip():
                parts.append("[备注] " + notes)
    return "\n".join(parts)


def extract_ocr(path):
    """图片 OCR：优先 pytesseract，回退 tesseract CLI。"""
    tessdata = os.path.expanduser("~/.workbuddy/tessdata")
    lang = "chi_sim+eng"
    env = dict(os.environ)
    if os.path.isdir(tessdata):
        env["TESSDATA_PREFIX"] = tessdata
    try:
        from PIL import Image
        import pytesseract
        try:
            pytesseract.pytesseract.tesseract_cmd
        except AttributeError:
            pass
        img = Image.open(path)
        return pytesseract.image_to_string(img, lang=lang, config="--psm 6")
    except ImportError as e:
        return f"[ERROR] 图片 OCR 依赖缺失：{e}。请 pip install pillow pytesseract 且安装 Tesseract 本体"
    except Exception as e:
        return f"[ERROR] OCR 失败：{e}"


def convert_one(path, ocr_flag, out_dir=None):
    ext = os.path.splitext(path)[1].lower()
    kind = SUPPORTED.get(ext)
    if kind is None:
        return None
    name = os.path.basename(path)
    if kind == "text":
        content = extract_text(path)
    elif kind == "pdf":
        content = extract_pdf(path, ocr_flag)
    elif kind == "docx":
        content = extract_docx(path)
    elif kind == "xlsx":
        content = extract_xlsx(path)
    elif kind == "pptx":
        content = extract_pptx(path)
    elif kind == "ocr":
        content = extract_ocr(path)
    elif kind == "doc_legacy":
        return "[ERROR] .doc 旧格式请先用 Word/WPS 另存为 .docx 再提取"
    else:
        return "[ERROR] 不支持格式: " + ext

    base = os.path.splitext(name)[0]
    out_dir = out_dir or os.path.dirname(os.path.abspath(path))
    out_path = os.path.join(out_dir, base + ".transcript.md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(f"# {name} 转写文本\n\n> 来源文件: {path}\n\n")
        f.write(content)
    return out_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="输入文件或目录")
    ap.add_argument("--ocr", action="store_true", help="PDF 无文本层时也尝试 OCR")
    ap.add_argument("--out", default=None, help="输出目录（默认与源同目录）")
    args = ap.parse_args()

    if os.path.isdir(args.src):
        files = []
        for root, _, names in os.walk(args.src):
            for n in names:
                if os.path.splitext(n)[1].lower() in SUPPORTED:
                    files.append(os.path.join(root, n))
        print(f"发现 {len(files)} 个支持的文件")
    else:
        files = [args.src]

    ok = 0
    for f in sorted(files):
        try:
            out = convert_one(f, args.ocr, args.out)
            if out:
                print("OK  -> " + out)
                ok += 1
            else:
                print("SKIP-> " + f + " (不支持的格式)")
        except Exception as e:
            print(f"ERROR-> {f}: {e}")
    print(f"完成：{ok}/{len(files)} 个文件已转换为 .transcript.md")


if __name__ == "__main__":
    main()