# -*- coding: utf-8 -*-
"""
Lucide 安全语义图标池 下载+渲染+验证 流水线
- 源: lucide-static (ISC 开源, 可商用)  via jsdelivr CDN (需 UA)
- 渲染: resvg_py.svg_to_bytes (纯 Rust, venv 已装 0.5.0)
- 输出: PNG 池 (256px 透明底, stroke=currentColor 重染成配置色)
- 用法: python build_icon_pool.py            # 全部默认色
        python build_icon_pool.py 蓝          # 只构建某个色
"""
import os, sys, io, time, urllib.request, re
from PIL import Image

CDN = "https://cdn.jsdelivr.net/npm/lucide-static@latest/icons/{}.svg"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
HERE = os.path.dirname(os.path.abspath(__file__))
# 图标池外置（SkillHub 发布拒收 .png，图片资产一律放 D:/RayClaw/skill-archives/）
POOL = r"D:\RayClaw\skill-archives\ray-ppt-generator-icon-pool-20260904"
SVG_TMP = os.path.join(HERE, "_svg_tmp")

# 安全主题图标清单 (name: (文件名, 中文语义, 建议色))
# 色: 蓝=主/信息 绿=安全/通过 红=危险/禁止 橙=警示 深=中性
ICONS = {
    # 防护/警示
    "shield":        ("shield.svg",            "安全防护",    "#0F4C81"),
    "shield-alert":  ("shield-alert.svg",      "防护警告",    "#E87722"),
    "triangle-alert":("triangle-alert.svg",    "警告",        "#BE1E1E"),
    "bell":          ("bell.svg",              "警报通知",    "#E87722"),
    "bell-ring":     ("bell-ring.svg",         "紧急警报",    "#BE1E1E"),
    "flame":         ("flame.svg",             "火灾",        "#BE1E1E"),
    "skull":         ("skull.svg",             "危险/剧毒",   "#BE1E1E"),
    "radiation":     ("radiation.svg",         "辐射危害",    "#E87722"),
    "alert-triangle":("alert-triangle.svg",    "三角形警告",  "#E87722"),
    # 安全行为
    "check":         ("check.svg",             "正确/合规",   "#228B22"),
    "check-circle":  ("check-circle.svg",      "完成/通过",   "#228B22"),
    "x":             ("x.svg",                 "错误/禁止",   "#BE1E1E"),
    "x-circle":      ("x-circle.svg",          "禁止/失败",   "#BE1E1E"),
    "eye":           ("eye.svg",               "检查/监督",   "#0F4C81"),
    "eye-off":       ("eye-off.svg",           "隐患隐蔽",    "#64748B"),
    "search":        ("search.svg",            "排查",        "#0F4C81"),
    "list-checks":   ("list-checks.svg",       "检查清单",    "#0F4C81"),
    "clipboard-check":("clipboard-check.svg",  "整改闭环",    "#0F4C81"),
    "user-check":    ("user-check.svg",        "人员确认",    "#0F4C81"),
    "users":         ("users.svg",             "团队/责任",   "#475569"),
    "settings":      ("settings.svg",          "管理/程序",   "#475569"),
    "siren":         ("siren.svg",             "警笛/疏散",   "#BE1E1E"),
    "phone-call":    ("phone-call.svg",        "报告电话",    "#0F4C81"),
    "megaphone":     ("megaphone.svg",         "宣贯/广播",   "#E87722"),
    "file-text":     ("file-text.svg",         "报告/制度",   "#475569"),
    "book-open":     ("book-open.svg",         "培训/学习",   "#0F4C81"),
    "graduation-cap":("graduation-cap.svg",    "培训教育",    "#0F4C81"),
    "clock":         ("clock.svg",             "时限/24h",    "#E87722"),
    "timer":         ("timer.svg",             "整改期限",    "#E87722"),
    "target":        ("target.svg",            "目标/事故调查", "#0F4C81"),
    "crosshair":     ("crosshair.svg",         "定位/精准",   "#0F4C81"),
    "message-square-warning": ("message-square-warning.svg", "上报提醒", "#E87722"),
    "help-circle":   ("help-circle.svg",       "疑问/求助",   "#64748B"),
    "info":          ("info.svg",              "信息/说明",   "#64748B"),
    "heart-pulse":   ("heart-pulse.svg",       "急救/生命",   "#BE1E1E"),
    "building-2":    ("building-2.svg",        "厂区/单位",   "#475569"),
    "hard-hat":      ("hard-hat.svg",          "安全帽/PPE",  "#E87722"),
    "factory":       ("factory.svg",           "工厂/生产",   "#475569"),
    "alert-octagon": ("alert-octagon.svg",     "八边形警告",  "#BE1E1E"),
    "circle-slash":  ("circle-slash.svg",      "禁止通行",    "#BE1E1E"),
}

ALIASES = {  # 旧名→新名修正
    "check-circle": "circle-check", "x-circle": "circle-x",
    "help-circle": "circle-help", "alert-triangle": "triangle-alert",
    "alert-octagon": "octagon-alert", "clipboard-check": "clipboard-check",
    "message-square-warning": "message-square-warning",
}

SIZE = 256  # 渲染尺寸 px


def fetch(name: str) -> str:
    """下载 SVG 文本，失败重试 2 次。"""
    url = CDN.format(name)
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode("utf-8")
        except Exception as e:
            if attempt == 2:
                raise
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"fetch failed: {name}")


def recolor(svg: str, hex_color: str) -> str:
    """把 stroke=currentColor / fill 的图标重染成目标色。Lucide 是 outline(描边)风格。"""
    color = hex_color
    svg = svg.replace("currentColor", color)
    # 个别面性图标用 fill 的也一并替换
    svg = svg.replace('stroke="none"', 'stroke="none"')
    return svg


def render(svg: str, out_png: str, size: int = SIZE) -> bool:
    from resvg_py import svg_to_bytes
    png = svg_to_bytes(svg_string=svg, zoom=size / 24.0)  # viewBox 24 → size px
    with open(out_png, "wb") as f:
        f.write(png)
    # 验证: 能打开 + 尺寸正确 + 非全透明
    im = Image.open(out_png)
    w, h = im.size
    bbox = im.getbbox()
    ok = bbox is not None
    return ok and w == size and h == size


def build_color(color_name: str | None):
    os.makedirs(POOL, exist_ok=True)
    os.makedirs(SVG_TMP, exist_ok=True)
    ok, fail = [], []
    for key, (fname, sem, default_color) in ICONS.items():
        if color_name and default_color != color_name:
            continue
        real = ALIASES.get(fname, fname)
        name = real.replace(".svg", "")  # fetch 传图标名，CDN 模板内部才补 .svg
        try:
            svg = fetch(name)
        except Exception as e:
            fail.append((key, f"fetch: {e}"))
            continue
        # 落一份原始 SVG 留档(可选)
        with open(os.path.join(SVG_TMP, real), "w", encoding="utf-8") as f:
            f.write(svg)
        color = default_color
        recolored = recolor(svg, color)
        out = os.path.join(POOL, f"{key}_{color[1:]}.png")
        try:
            if render(recolored, out):
                ok.append(key)
            else:
                fail.append((key, "render empty/尺寸错"))
        except Exception as e:
            fail.append((key, f"render: {type(e).__name__} {str(e)[:100]}"))
    print(f"✅ 成功 {len(ok)}: {ok}")
    if fail:
        print(f"❌ 失败 {len(fail)}:")
        for k, e in fail:
            print(f"   - {k}: {e}")
    return ok, fail


if __name__ == "__main__":
    build_color(sys.argv[1] if len(sys.argv) > 1 else None)
