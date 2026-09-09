"""Playwright 同步API 渲染 HTML → A4 PDF（替代失效的 Edge headless）"""
import os, sys, traceback, shutil
sys.stdout.reconfigure(encoding="utf-8")

HTML_PATH = r"C:\Users\rayzh\.workbuddy\skills\ray-pse-sharing\assets\output_card.html"
DST_PDF = r"E:\LingXi\2026-08-02-包钢球罐BLEVE事故分享\PSI-2026-008-包钢1.18饱和水球罐BLEVE事故分享.pdf"

def main():
    try:
        from playwright.sync_api import sync_playwright
        url = "file:///" + HTML_PATH.replace(os.sep, "/")
        tmp = os.path.join(os.environ.get("TEMP", r"C:\Users\rayzh\AppData\Local\Temp"), "card_pw.pdf")
        if os.path.exists(tmp):
            os.remove(tmp)
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(1500)
            page.pdf(path=tmp, format="A4", print_background=True, prefer_css_page_size=True)
            browser.close()
        size = os.path.getsize(tmp)
        print(f"临时PDF OK: {size} bytes")
        shutil.copy(tmp, DST_PDF)
        os.remove(tmp)
        print(f"目标PDF OK: {os.path.exists(DST_PDF)} {os.path.getsize(DST_PDF)} bytes")
    except Exception:
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
