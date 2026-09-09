"""
安全事故分享卡片 - 自动化管道 v2.5
=====================================
输入：事故调查报告文本（或JSON数据）
输出：A4 PDF 文档 + 中间 HTML 文件

v2.5 改进：
  - 新增 HSE工具 模块（安全要素标签）
  - 输出 A4 PDF（非 PNG 截图）
  - 文件名格式：编号-事故名称.pdf
  - 使用系统 Edge 浏览器 print-to-pdf

使用方法：
    python pipeline_v2.py --json shenghua_data_v2.json
    python pipeline_v2.py --json my_accident.json
    python pipeline_v2.py --json my_accident.json --no-shot  # 仅 HTML
"""

import sys, os, json, argparse, base64, re, subprocess, tempfile, shutil
sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_HTML = os.path.join(BASE_DIR, "template.html")

# Edge 浏览器路径（Windows 默认安装位置）
EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

def find_edge():
    """查找系统 Edge 浏览器"""
    for p in EDGE_PATHS:
        if os.path.exists(p):
            return p
    return None

# ========================================
#  Image builder (photo or concept SVG)
# ========================================

def build_image_html(img_info: dict, data: dict) -> str:
    img_type = img_info.get("type", "")

    if img_type == "photo":
        photo_path = img_info.get("path", "")
        if photo_path and os.path.exists(photo_path):
            try:
                with open(photo_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                ext = os.path.splitext(photo_path)[1].lower()
                mime = {".png":"image/png", ".jpg":"image/jpeg",
                        ".jpeg":"image/jpeg", ".gif":"image/gif",
                        ".webp":"image/webp"}.get(ext, "image/png")
                return f'<img src="data:{mime};base64,{b64}" alt="事故现场照片"/>'
            except Exception as e:
                print(f"      ⚠ 无法加载照片: {e}")
                return f'<div class="no-image">⚠ 照片加载失败</div>'
        return f'<div class="no-image">⚠ 照片路径无效</div>'

    elif img_type == "svg":
        try:
            from concept_diagram import generate_concept_diagram
            return generate_concept_diagram(data)
        except ImportError:
            return '<div class="no-image">概念图生成失败</div>'

    else:
        return '<div class="no-image">📷 无事故图片<br/><span style="font-size:9px">（报告未包含相关照片）</span></div>'


# ========================================
#  Template filler
# ========================================

def fill_template(html: str, data: dict, layout: str = "auto") -> str:
    ai = data.get("accident_info", {})
    img = data.get("image", {})

    # --- Layout detection ---
    desc = data.get("description", "")
    if layout == "auto":
        n_know = len(data.get("knowledge", []))
        n_act = len(data.get("what_to_do", []))
        # stack 适用：描述长(>400字) 或 知识/行动条目多(≥5条)——左右并列更紧凑，避免侧边式右侧空白
        if len(desc) > 400 or n_know >= 5 or n_act >= 5:
            layout = "stack"
        else:
            layout = "side"
    layout_class = f"layout-{layout}"
    html = html.replace("{{layout_class}}", layout_class)
    print(f"      布局: {layout} (描述{len(desc)}字)")

    # --- Simple text replacements ---
    html = html.replace("{{date}}", ai.get("date", ""))
    html = html.replace("{{location}}", ai.get("location", ""))
    html = html.replace("{{type}}", ai.get("type", ""))
    html = html.replace("{{severity}}", ai.get("severity", ""))
    html = html.replace("{{material}}", ai.get("material", ""))
    html = html.replace("{{title}}", data.get("accident_title", ""))
    html = html.replace("{{share_date}}", data.get("share_date", ""))
    html = html.replace("{{takeaway}}", data.get("takeaway", ""))

    ft = data.get("footer", {})
    html = html.replace("{{card_number}}", ft.get("number", ""))

    # --- Severity class ---
    sev_class = ai.get("severity_class", "high")
    html = html.replace("severity-class", f"severity-{sev_class}")

    # --- Image ---
    img_html = build_image_html(img, data)
    html = html.replace("<!-- IMAGE -->", img_html)

    # --- Description HTML ---
    highlight = data.get("highlight", [])
    desc_html = build_description_html(desc, highlight)
    html = html.replace("{{description_html}}", desc_html)

    # --- Protection failure tags ---
    pf_items = data.get("protection_failure", [])
    pf_html = "\n          ".join(f'<span class="pf-tag">{item}</span>' for item in pf_items)
    html = html.replace("{{protection_tags}}", pf_html)

    # --- HSE tools tags ---
    hse_items = data.get("hse_tools", [])
    ht_html = "\n          ".join(f'<span class="ht-tag">{item}</span>' for item in hse_items)
    html = html.replace("{{hse_tools_tags}}", ht_html)

    # --- History accidents (optional full-width band above protect-fail) ---
    history = data.get("history", [])
    if history:
        hs_html = ('<div class="history-box">'
                   '<div class="hs-title">🏛️ 历史事故</div>'
                   '<div class="hs-items">'
                   + "\n          ".join(f'<span class="hs-tag">{item}</span>' for item in history)
                   + '</div></div>')
    else:
        hs_html = ""
    html = html.replace("{{history_html}}", hs_html)

    # --- Knowledge items ---
    knowledge = data.get("knowledge", [])
    k_html = "\n            ".join(f"<li>{item}</li>" for item in knowledge)
    html = html.replace("{{knowledge_items}}", k_html)

    # --- Reference line (optional, rendered above takeaway) ---
    ref = data.get("reference", "")
    ref_html = f'<div class="reference-line">🔗 {ref}</div>' if ref else ""
    html = html.replace("{{reference_html}}", ref_html)

    # --- Action items ---
    actions = data.get("what_to_do", [])
    a_html = "\n            ".join(f"<li>{item}</li>" for item in actions)
    html = html.replace("{{action_items}}", a_html)

    return html


def build_description_html(text: str, highlight_terms: list = None) -> str:
    """Convert plain text to HTML paragraphs, highlighting terms from JSON `highlight` field."""
    highlight_terms = highlight_terms or []
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    paragraphs = []
    for i, line in enumerate(lines):
        style = "" if i == 0 else ' style="margin-top:8px;"'
        for term in highlight_terms:
            if term and term in line:
                line = line.replace(term, f'<span class="highlight">{term}</span>')
        paragraphs.append(f'<p{style}>{line}</p>')
    return "\n        ".join(paragraphs)


# ========================================
#  PDF generation via Edge headless
# ========================================

def html_to_pdf(html_path: str, pdf_path: str) -> bool:
    """使用 Edge 浏览器 headless print-to-pdf 生成 A4 PDF

    Windows 注意：Edge --print-to-pdf 参数不接受 CJK 字符路径或正斜杠路径，
    因此先输出到安全临时路径（不含中文），再复制到目标位置。
    """
    edge = find_edge()
    if not edge:
        print("      ⚠ 未找到 Edge 浏览器，回退 Playwright ...")
        return html_to_pdf_playwright(html_path, pdf_path)

    file_url = f"file:///{html_path.replace(os.sep, '/')}"

    # 使用临时路径避免 Edge 的 CJK/正斜杠路径兼容性问题
    tmp_pdf = os.path.join(tempfile.gettempdir(), "card_tmp.pdf")

    cmd = [
        edge,
        "--headless",
        "--disable-gpu",
        "--run-all-compositor-stages-before-draw",
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={tmp_pdf}",
        file_url
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if os.path.exists(tmp_pdf) and os.path.getsize(tmp_pdf) > 1000:
            size_kb = os.path.getsize(tmp_pdf) / 1024
            # 复制到目标路径并清理临时文件
            os.makedirs(os.path.dirname(pdf_path) or '.', exist_ok=True)
            shutil.copy(tmp_pdf, pdf_path)
            os.remove(tmp_pdf)
            print(f"      PDF 已生成: {pdf_path} ({size_kb:.0f} KB)")
            return True
        else:
            print(f"      ⚠ Edge 生成失败（文件太小或不存在），回退 Playwright ...")
            return html_to_pdf_playwright(html_path, pdf_path)
    except subprocess.TimeoutExpired:
        print("      ⚠ Edge 超时（30秒），回退 Playwright ...")
        return html_to_pdf_playwright(html_path, pdf_path)
    except Exception as e:
        print(f"      ⚠ Edge 生成异常: {e}，回退 Playwright ...")
        return html_to_pdf_playwright(html_path, pdf_path)


def html_to_pdf_playwright(html_path: str, pdf_path: str) -> bool:
    """Playwright + Chromium headless 渲染 HTML → A4 PDF（Edge 失效时的回退方案）

    要点：必须用同步 API（async 在本机 exit 1 无输出）；先输出 TEMP 纯 ASCII
    路径，再 shutil.copy 到中文目标路径（避开 CJK 路径坑）。
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("      ⚠ Playwright 未安装，无法渲染 PDF。请手动用浏览器打开 HTML 打印。")
        return False

    try:
        file_url = f"file:///{html_path.replace(os.sep, '/')}"
        tmp_pdf = os.path.join(tempfile.gettempdir(), "card_pw.pdf")
        if os.path.exists(tmp_pdf):
            os.remove(tmp_pdf)
        # 手动生命周期（红线：禁用 with sync_playwright() + browser.close()，
        # 本环境 close() 永久挂起 → 沙箱杀进程树 → SIGTERM/exit 1 吞 stdout）
        pw = sync_playwright().start()
        try:
            browser = pw.chromium.launch()
            page = browser.new_page()
            page.goto(file_url)
            page.wait_for_timeout(1500)  # 等 SVG/字体渲染完
            page.pdf(path=tmp_pdf, format="A4", print_background=True, prefer_css_page_size=True)
        finally:
            pw.stop()
        if os.path.exists(tmp_pdf) and os.path.getsize(tmp_pdf) > 1000:
            size_kb = os.path.getsize(tmp_pdf) / 1024
            os.makedirs(os.path.dirname(pdf_path) or '.', exist_ok=True)
            shutil.copy(tmp_pdf, pdf_path)
            os.remove(tmp_pdf)
            print(f"      PDF 已生成(Playwright): {pdf_path} ({size_kb:.0f} KB)")
            return True
        else:
            print("      ⚠ Playwright 生成的 PDF 太小或不存在")
            return False
    except Exception as e:
        print(f"      ⚠ Playwright 渲染异常: {e}")
        return False


# ========================================
#  Main pipeline
# ========================================

def main():
    parser = argparse.ArgumentParser(description="安全事故分享卡片 - 自动化管道 v2.5")
    parser.add_argument("--json", required=True, help="JSON 数据文件路径")
    parser.add_argument("--out", default=None, help="输出 PDF 路径（默认：编号-事故名称.pdf）")
    parser.add_argument("--layout", default="auto", choices=["auto","side","stack"],
                        help="排版模式: auto(自动), side(侧边式), stack(堆叠式)")
    parser.add_argument("--no-shot", action="store_true", help="仅生成 HTML，不输出 PDF")
    args = parser.parse_args()

    print("=" * 60)
    print("安全事故分享卡片 - 自动化管道 v2.5")
    print("=" * 60)

    # Load template
    print(f"\n[1/5] 加载模板: {os.path.basename(TEMPLATE_HTML)}")
    with open(TEMPLATE_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    # Load JSON data
    print(f"[2/5] 加载数据: {args.json}")
    with open(args.json, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Fill template
    print("[3/5] 填充模板 → HTML ...")
    filled_html = fill_template(html, data, args.layout)

    out_html = os.path.join(BASE_DIR, "output_card.html")
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(filled_html)
    print(f"      HTML 已生成: {os.path.basename(out_html)}")

    # Determine output PDF filename
    if args.no_shot:
        out_path = out_html
    else:
        if args.out:
            out_pdf = args.out
        else:
            ft = data.get("footer", {})
            card_num = ft.get("number", "PSI-0000")
            safe_num = re.sub(r'[\\/:*?"<>|]', '-', card_num)
            title = data.get("accident_title", "accident")
            safe_title = re.sub(r'[\\/:*?"<>|]', '-', title)[:50]
            out_pdf = os.path.join(BASE_DIR, f"{safe_num}-{safe_title}.pdf")

        print(f"[4/5] Edge headless → A4 PDF ...")
        print(f"      输出文件: {os.path.basename(out_pdf)}")
        success = html_to_pdf(out_html, out_pdf)
        out_path = out_pdf if success else out_html

        if not success:
            print(f"      ⚠ Edge 与 Playwright 均失败，请手动用浏览器打开 {os.path.basename(out_html)} 并打印为 PDF")

    print(f"\n[5/5] ✅ 完成！")
    print(f"      HTML 中间文件: {os.path.basename(out_html)}")
    if not args.no_shot:
        ft = data.get("footer", {})
        print(f"      卡片 PDF: {os.path.basename(out_path)}")
    else:
        print(f"      卡片 HTML: {os.path.basename(out_path)}")


if __name__ == "__main__":
    main()
