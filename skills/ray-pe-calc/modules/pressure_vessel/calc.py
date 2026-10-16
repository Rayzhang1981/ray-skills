#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pressure vessel MAWP estimation · 压力容器最大允许工作压力估算
per GB/T 150.3-2011（式 3-1 筒体 / 式 5-1 标准椭圆封头，反解）+ 外压量级估算。

覆盖四件事（一次调用全出）：
  ① 内压筒体 MAWP          [Pw] = 2·[σ]t·φ·δe /(Di + δe)
  ② 标准椭圆封头 MAWP（K=1） [Pw] = 2·[σ]t·φ·δe /(Di + 0.5δe)
  ③ 外压（真空工况）量级     p_cr = 2.59·E·(δe/Do)^2.5/(L/Do)，[p] = p_cr/3
  ④ 材质使用限制检查 + 加强圈间距反算

⚠️ 四条口径红线（填错即系统性偏离）
  · `--D`  —— **内径 Di**（不是外径）
  · `--dn` —— **名义厚度**，脚本自动减 C1/C2 得 δe；若只有 δe 用 `--de` 直接给
  · `--S`  —— **设计温度下**的许用应力；用 `--mat` 则由材料库取（**带可信度告警**）
  · `--basis` —— **取值口径**（2026-10-08 新增，仅对奥氏体不锈钢可多档）：
      `2024row1` = GB/T 150.2-2024 表C.2 **第一行** → **筒体/封头**等允许微量永久变形之元件
      `2024row2` = 同表 **第二行** → **法兰、平盖**等不允许微量永久变形之元件
      `2011`     = GB/T 150.2-2011 表5 第一行 → **既有设备且材质证明未取得**时的保守口径
      ⚠️ S30408 的**默认口径是 `2011`（保守）**——因 2024 版提高后的第一行（≤100 ℃ 153 MPa）
         **以钢板符合 GB/T 713.7-2023（Rp0.2≥230 MPa）为前提**；既有设备取不到证明时不得用。
      ⚠️ 两版**不是单向保守**：≤150 ℃ 档 2011（137）低于 2024（153）；575 ℃ 档 2011（79）
         反而**高于** 2024（67）⇒ 换口径须按设计温度逐档核算，不可整体二选一。

⚠️ 「使用限制」与「许用应力」同等重要：前者决定材料**准不准用**（常是一票否决），
   如 Q235B 的使用温度下限 20 ℃、不得用于极度/高度危害介质（GB/T 150.2-2024 附录D）。

示例
  python calc.py --D 1000 --dn 5 --mat Q235B --T 20
  python calc.py --D 1900 --dn 5 --mat S30408 --T 50 --L 1500   # 加 --L 即算外压（真空）
  python calc.py --D 1900 --dn 5 --mat S30408 --T 50 --basis 2024row1   # 仅当材质证明齐备
  python calc.py --D 1000 --dn 5 --mat S31603 --T 150 --basis 2024row1  # S31603 2024 已核，须显式选口径
  python calc.py --D 1000 --dn 5 --mat S31603 --T 120 --S 120           # 或直接给 --S
  python calc.py --list-materials
  python calc.py --selftest
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import materials  # noqa: E402

E_MOD = 1.95e5          # 弹性模量 MPa（量级；碳钢/不锈钢常温近似）
ATM = 101.3e-3          # MPa


def console_safe():
    """控制台输出护栏（2026-10-09）。

    中文 Windows 控制台默认 cp936(GBK)。**当 stdout 被重定向或经管道捕获时**
    （自动验证 / 日志 / subprocess PIPE —— 本生态生成器正是 PIPE 捕获），
    Python 按 locale 编码写流；遇到 GBK 无法表示的字符即抛 UnicodeEncodeError，
    **整段输出中断**。而交互式控制台走 WriteConsoleW(UTF-16)，同一字符却无碍
    => 该缺陷只在「捕获输出」时显形，最易漏测（2026-10-09 实证：--selftest 被它打断）。

    处理：**保持流原编码不变**（确保中文在 GBK 控制台仍正常显示），
    仅把不可表示的字符降级为 '?'，从而永不中断。
    注意：不要改成 encoding="utf-8" —— 那会让 GBK 控制台下的中文变乱码。
    """
    for name in ("stdout", "stderr"):
        s = getattr(sys, name, None)
        try:
            if s is not None and hasattr(s, "reconfigure"):
                s.reconfigure(errors="replace")
        except Exception:
            pass


def _gbk_unsafe():
    """扫出**可能进入控制台**却无法用 GBK 编码的字符，返回 ["文件:L行 U+XXXX", ...]。

    覆盖面 = calc.py / materials.py 的**全部非 docstring 字符串字面量**
    （涵盖 print 实参、argparse 帮助文本，以及 materials.py 中由 describe() /
    check_limits() 返回、再由 calc.py 打印的数据字段）。
    护栏 console_safe() 能防崩溃，但会把这类字符降级成 '?' —— 故仍须源头可编码。
    """
    import ast
    bad = []
    here = os.path.dirname(os.path.abspath(__file__))
    for fn in ("calc.py", "materials.py"):
        with open(os.path.join(here, fn), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        doc_ids = set()
        for n in ast.walk(tree):
            body = getattr(n, "body", None)
            # 注意：Lambda / IfExp 也有 body，但它是**表达式**不是语句列表 —— 必须先判 list
            if (isinstance(body, list) and body
                    and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)):
                doc_ids.add(id(body[0].value))
        for n in ast.walk(tree):
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in doc_ids:
                for ch in n.value:
                    try:
                        ch.encode("gbk")
                    except UnicodeEncodeError:
                        bad.append("%s:L%d U+%04X" % (fn, n.lineno, ord(ch)))
    return bad



def p_cyl(sig, phi, de, Di):
    return 2.0 * sig * phi * de / (Di + de)


def p_ell(sig, phi, de, Di):
    return 2.0 * sig * phi * de / (Di + 0.5 * de)


def pcr_short(de, L, Do):
    return 2.59 * E_MOD * (de / Do) ** 2.5 / (L / Do)


def L_required(de, Do, target_pcr):
    return 2.59 * E_MOD * (de / Do) ** 2.5 * Do / target_pcr


def header(t):
    print("\n" + "=" * 74)
    print(t)
    print("=" * 74)


def run(a):
    m = materials.MATERIALS.get(a.mat) if a.mat else None

    # ── 有效厚度 ──────────────────────────────────────────────────────────
    if a.de is not None:
        de, src_de = a.de, "--de 直接给定"
        C1 = C2 = None
    else:
        C1 = a.C1 if a.C1 is not None else (m["C1"] if m else 0.3)
        C2 = a.C2 if a.C2 is not None else (m["C2"] if m else 0.5)
        de = a.dn - C1 - C2
        src_de = "δe = δn(%g) - C1(%.2f) - C2(%.2f)" % (a.dn, C1, C2)
    if de <= 0:
        print("[中止] 有效厚度 δe = %.2f mm ≤ 0，参数有误。" % de)
        return 2

    # ── 许用应力 ──────────────────────────────────────────────────────────
    bas_name = bas_row = None
    if a.S is not None:
        sig, sig_ok, sig_src = a.S, True, "--S 用户给定"
    elif m:
        if a.basis is not None:
            bas_name, bas_row = materials.basis_of(a.mat, a.basis)
            if bas_row is None:
                print("[中止] 材质 %s 无口径 %r。可选：%s"
                      % (a.mat, a.basis, "、".join(sorted(m["rows"]))))
                return 2
        else:
            bas_name, bas_row = materials.basis_of(a.mat)
        sig, sig_ok = materials.sigma_at(a.mat, a.T, a.basis)
        sig_src = "材料库（%s ｜ 口径 %s）" % (m["std"], bas_name)
        if sig is None:
            print("[中止] 材质 %s 的 [σ]t 未收录（口径 %s），请用 --S 直接给定（并注明出处）。"
                  % (a.mat, bas_name))
            return 2
    else:
        print("[中止] 须给 --mat（用材料库）或 --S（手填许用应力）。")
        return 2

    header("压力容器 MAWP 估算")
    print("  几何：Di = %g mm（内径） ｜ δn = %s ｜ δe = %.2f mm" % (
        a.D, "%g" % a.dn if a.de is None else "—", de))
    print("  厚度口径：%s" % src_de)
    print("  材质：%s" % (m["full"] if m else "（未指定，按 --S）"))
    print("  设计温度：%s ℃ ｜ 许用应力 [σ]t = %g MPa（%s）"
          % ("%g" % a.T if a.T is not None else "—", sig, sig_src))
    if bas_row is not None:
        print("  取值口径：%s —— %s" % (bas_name, bas_row["label"]))
        print("  该口径数值可信度：%s（%s）" % (bas_row["verify"], bas_row["verify_note"][:96]))
    print("  焊接接头系数 φ = %.2f（%s）"
          % (a.phi, "局部 RT" if abs(a.phi - 0.85) < 1e-9 else
             ("100% RT" if abs(a.phi - 1.0) < 1e-9 else "用户指定")))

    # ── ① 内压筒体 / ② 封头 ───────────────────────────────────────────────
    pc = p_cyl(sig, a.phi, de, a.D)
    pe = p_ell(sig, a.phi, de, a.D)
    ctrl = "筒体控制" if pc <= pe else "封头控制"
    print("\n  ① 内压筒体   [Pw] = 2·[σ]t·φ·δe/(Di+δe)      = %.3f MPa（%.1f bar）" % (pc, pc * 10))
    print("  ② 标准椭圆封头 [Pw] = 2·[σ]t·φ·δe/(Di+0.5δe)  = %.3f MPa（%.1f bar）" % (pe, pe * 10))
    print("     -> **%s**（两式分母仅差 0.5δe，K=1 时差 %.2f%%）" % (ctrl, abs(pc - pe) / pc * 100))
    print("     [!] 封头由钢板成形，过渡区**成形减薄** 8~13%（5 mm 板最薄点名义仅 4.3~4.5 mm）；")
    print("        若未按 GB/T 25198 核实投料厚度，封头可能反超筒体成为控制项。")

    # ── ③ 外压 ────────────────────────────────────────────────────────────
    if a.L is not None:
        Do = a.D + 2 * a.dn if a.de is None else a.D + 2 * de
        pcr = pcr_short(de, a.L, Do)
        pa = pcr / 3.0
        print("\n  ③ 外压（真空工况）  δe=%.2f ｜ Do=%.0f ｜ L=%.0f ｜ Do/δe=%.0f ｜ L/Do=%.2f"
              % (de, Do, a.L, Do / de, a.L / Do))
        print("     p_cr = 2.59·E·(δe/Do)^2.5/(L/Do) = %.4f MPa" % pcr)
        print("     [p] = p_cr/3 = %.1f kPa   对 1 atm（101.3 kPa）：%s"
              % (pa * 1000, "OK 有余量" if pa > ATM else "NG **不足**"))
        if pa <= ATM:
            Lreq = L_required(de, Do, 3 * ATM)
            print("     -> 若需承受**全真空**，反算加强圈最大间距 = %.0f mm（现无支撑 %.0f mm）"
                  % (Lreq, a.L))
            print("       [!] 本项为「无任何支撑」最保守口径；塔盘/内件/加强圈均提供支撑。")
            print("       正式校核须按 GB/T 150.3-2011 第 4 章、以实际加强圈间距分段计算。")
        print("     [!] 仅当该容器**实际承受真空/减压工况**时本项才适用——须逐台确认。")
    else:
        print("\n  ③ 外压：未计算（如适用请加 --L <筒体长 mm>；减压/真空工况务必算）")

    # ── ④ 材质使用限制 ────────────────────────────────────────────────────
    if m:
        issues, warns = materials.check_limits(a.mat, T=a.T, P=a.P, dn=a.dn, basis=a.basis)
        print("\n  ④ 材质使用限制检查（%s）" % m["std"])
        for code, txt, sub in m["limits"]:
            print("     · %s%s%s" % ("（%s）" % code if code else "", txt,
                                     ("　→ %s" % sub) if sub else ""))
        if issues:
            print("     [X] 不合规/不适用：")
            for x in issues:
                print("        · %s" % x)
        if warns:
            print("     [!] 告警：")
            for x in warns:
                print("        · %s" % x)
        if not issues and not warns:
            print("     [OK] 已输入的参数未见与该材质使用限制冲突")
        if not sig_ok:
            print("     [!] **本结果所依据的 [σ]t 未读标准原文**（口径 %s），仅作量级参考；"
                  % (bas_name or "—"))
            print("        正式使用前必须查 GB/T 150.2-2024 附录C 表C.2 相应表/行。")

    print("\n  ── 三条必须分清 ──")
    print("  · MAWP（本估算）＝ 壳体材料在给定温度下**能承受**的最大压力（力学能力）")
    print("  · 设计压力       ＝ 设计文件给定值")
    print("  · 允许工作压力   ＝ 由呼吸阀/放空设定 + 设计压力共同决定的操作限值")
    print("  -> 本估算只回答第一条；不得据此提高设计压力或安全阀/呼吸阀设定值。")
    print("  -> 正式 MAWP 须由有资质设计人员按现行 GB/T 150 系列、以设计文件为准核定。")
    return 0


def selftest():
    """自检：正例 + 负控 + 口径语义 + 单位 + 边界。返回 0=通过、2=失败。"""
    res = []

    def chk(name, ok, detail=""):
        res.append((name, bool(ok), detail))

    # ── 正例：Q235B Φ1000、δn=5、C1=0.45、C2=1.0、φ=0.85、20 ℃（116 MPa）──
    de = 5 - 0.45 - 1.0
    sig, ok = materials.sigma_at("Q235B", 20.0)
    chk("Q235B @20 ℃ 取到 [σ]t=116 且标记已读原文",
        ok and abs(sig - 116.0) < 1e-9, "%g ｜ %s" % (sig, ok))
    v = p_cyl(sig, 0.85, de, 1000.0)
    chk("正例 Φ1000/δe=3.55/S=116/φ=0.85", abs(v - 0.69759) < 5e-5, "%.5f" % v)
    ve = p_ell(sig, 0.85, de, 1000.0)
    chk("封头正例（应略高于筒体）", ve > v and abs(ve - 0.69883) < 5e-5, "%.5f" % ve)

    # ── 正例：S30408 三档口径（2026-10-08 新增，源＝GB/T 150.2-2024 表C.2 原文图像）──
    s11, o11 = materials.sigma_at("S30408", 20.0)                     # 默认 = 2011
    chk("S30408 默认口径为 2011（保守）且 @20 ℃ =137",
        s11 == 137.0 and o11 is False, "%g ｜ ok=%s" % (s11, o11))
    s24a, o24a = materials.sigma_at("S30408", 100.0, "2024row1")      # 第一行(筒体/封头)
    chk("S30408 2024row1 @100 ℃ =153 且标记已读原文",
        s24a == 153.0 and o24a is True, "%g ｜ ok=%s" % (s24a, o24a))
    s24b, o24b = materials.sigma_at("S30408", 100.0, "2024row2")      # 第二行(法兰/平盖)
    chk("S30408 2024row2 @100 ℃ =114 且标记已读原文",
        s24b == 114.0 and o24b is True, "%g ｜ ok=%s" % (s24b, o24b))
    chk("两行语义：第一行 ≥ 第二行（100 ℃ 153>114）", s24a > s24b, "%g > %g" % (s24a, s24b))

    # ── 负控 1：把 δe 误填成名义厚度 5.0 → 应显著高估 ──
    v_bad = p_cyl(sig, 0.85, 5.0, 1000.0)
    chk("负控 δe 误用名义厚度应高估 >30%", (v_bad - v) / v > 0.30,
        "高估 %.1f%%" % ((v_bad - v) / v * 100))

    # ── 负控 2：Q235B 在 15 ℃（低于下限 20 ℃）必须报 issue ──
    iss, _ = materials.check_limits("Q235B", T=15.0)
    chk("负控 Q235B@15 ℃ 必须判「不适用」", any("下限" in x for x in iss), "; ".join(iss)[:60])

    # ── 负控 3：Q235B 在 2.0 MPa 设计压力下必须报 issue ──
    iss2, _ = materials.check_limits("Q235B", P=2.0)
    chk("负控 Q235B@2.0 MPa 必须判超范围", any("1.6" in x for x in iss2), "; ".join(iss2)[:60])

    # ── 负控 4：未核实材质（默认口径为 todo）必须被拒 ──
    iss4, _ = materials.check_limits("S31603", T=50.0)
    chk("负控 S31603 默认口径须判「工具拒绝估算」",
        any("工具拒绝估算" in x for x in iss4), "; ".join(iss4)[:60])
    s316, o316 = materials.sigma_at("S31603", 50.0)
    chk("负控 S31603 默认取值为 None（工具拒绝）", s316 is None and o316 is False, "%s" % (s316,))

    # ── 正例 7：S31603 2024 口径已收录（2026-10-09 核；表C.2 标准页 32 / PDF p38 图像）──
    s316a, o316a = materials.sigma_at("S31603", 150.0, "2024row1")
    chk("S31603 2024row1 @150 ℃ = 117 且标记已读原文",
        s316a == 117.0 and o316a is True, "%g ｜ ok=%s" % (s316a, o316a))
    s316b, _ = materials.sigma_at("S31603", 200.0, "2024row2")
    chk("S31603 2024row2 @200 ℃ = 80（法兰/平盖行）", s316b == 80.0, "%g" % s316b)
    # 反演交叉：row1 = min(0.9*Rp0.2(t), 140)、row2 = Rp0.2(t)/1.5（9 档 |偏差|<=0.5）
    _dev = max(abs(min(0.9 * (r2 * 1.5), 210.0 / 1.5) - r1)
               for r1, r2 in zip(materials._S31603_2024_ROW1, materials._S31603_2024_ROW2))
    chk("S31603 两行反演自洽（9 档最大偏差 <= 0.5 MPa）", _dev <= 0.5, "%.2f MPa" % _dev)
    _, w316 = materials.check_limits("S31603", T=150.0, basis="2024row1")
    chk("S31603 选 2024 口径须告警「2011 未收录/既有设备」",
        any("2011 口径" in x for x in w316), "; ".join(w316)[:70])

    # ── 负控 5（口径语义）：选 2011 口径必须告警「保守口径」 ──
    _, w11 = materials.check_limits("S30408", T=50.0, basis="2011")
    chk("负控 S30408@2011 口径须告警「保守口径」",
        any("保守口径" in x for x in w11), "; ".join(w11)[:70])
    _, w2 = materials.check_limits("S30408", T=50.0, basis="2024row2")
    chk("负控 S30408@2024row2 须告警「第二行/法兰平盖」",
        any("第二行" in x for x in w2), "; ".join(w2)[:70])

    # ── 负控 6：超出表列最高温度档必须告警（不得外推当设计依据）──
    _, w7 = materials.check_limits("S30408", T=750.0, basis="2024row1")
    chk("负控 S30408@750 ℃ 超表列须告警",
        any("超出表列最高温度档" in x for x in w7), "; ".join(w7)[:70])

    # ── 单位红线 ──
    chk("单位红线 0.6976 MPa → 6.976 bar", abs(v * 10 - 6.9759) < 1e-3, "%.4f" % (v * 10))

    # ── 外压正例（Φ1000×1600、δe=4.2、Do=1010）──
    pa = pcr_short(4.2, 1600.0, 1010.0) / 3.0
    chk("外压正例 Φ1000×1600/δe=4.2 ≈ 118.5 kPa", abs(pa * 1000 - 118.5) < 0.5, "%.1f kPa" % (pa * 1000))

    # ── 边界 ──
    chk("边界 δe=0 → P=0", p_cyl(116.0, 0.85, 0.0, 1000.0) == 0.0)
    chk("边界 σ=0 → P=0", p_cyl(0.0, 0.85, 4.2, 1000.0) == 0.0)

    # -- 回归门：进入控制台的字符串必须 GBK 可编码（2026-10-09 实证缺陷；已跑负控）--
    _bad_gbk = _gbk_unsafe()
    chk("控制台兼容：print/帮助文本均可 GBK 编码", not _bad_gbk,
        "；".join(_bad_gbk[:3]))


    print("== pressure_vessel/calc.py 自检 ==")
    for n, o, d in res:
        print("  [%s] %-46s %s" % ("OK  " if o else "FAIL", n, d))
    bad = sum(1 for _, o, _ in res if not o)
    print("合计 %d 项，失败：%d" % (len(res), bad))
    return 0 if bad == 0 else 2


def main():
    console_safe()
    ap = argparse.ArgumentParser(
        description="压力容器 MAWP 估算（GB/T 150.3-2011 反解）+ 材质使用限制检查")
    ap.add_argument("--D", type=float, help="**内径 Di** mm")
    ap.add_argument("--dn", type=float, default=None, help="**名义厚度** mm（脚本自动减 C1/C2）")
    ap.add_argument("--de", type=float, default=None, help="有效厚度 δe mm（已知时直接用，覆盖 --dn）")
    ap.add_argument("--mat", default=None, help="材质牌号（查材料库；未知则用 --S）")
    ap.add_argument("--basis", default=None,
                    help="许用应力取值口径：2024row1（筒体/封头）｜2024row2（法兰/平盖）｜"
                         "2011（既有设备保守口径）。缺省用材质库 default_basis。")
    ap.add_argument("--T", type=float, default=None, help="设计温度 ℃")
    ap.add_argument("--S", type=float, default=None, help="设计温度下许用应力 [σ]t MPa（手填，优先于 --mat）")
    ap.add_argument("--phi", type=float, default=0.85, help="焊接接头系数（局部 RT 0.85；100%% RT 1.0）")
    ap.add_argument("--C1", type=float, default=None, help="钢板负偏差 mm（默认取材料库值）")
    ap.add_argument("--C2", type=float, default=None, help="腐蚀裕量 mm（默认取材料库值）")
    ap.add_argument("--L", type=float, default=None, help="筒体长（无支撑长度）mm；给则算外压")
    ap.add_argument("--P", type=float, default=None, help="设计压力 MPa（用于材质适用范围检查）")
    ap.add_argument("--list-materials", action="store_true", help="列出材料库全部记录")
    ap.add_argument("--selftest", action="store_true", help="运行自检（正例/负控/单位/边界）")
    a = ap.parse_args()

    if a.selftest:
        return selftest()
    if a.list_materials:
        header("材料库（每条带可信度标记）")
        for k in materials.MATERIALS:
            print(materials.describe(k))
            print()
        print("[!] 可信度：source=已读标准原文 ｜ cross=多源交叉未取原文 ｜ todo=未核实（工具拒绝）")
        print("[!] 奥氏体不锈钢（S30408）有三档口径：2024row1（筒体/封头）／2024row2（法兰/平盖）／")
        print("   2011（既有设备保守口径）。**默认偏保守**——取提高值须先有材质证明。")
        return 0

    if a.D is None:
        print("[中止] 须给 --D（内径 mm）。")
        return 2
    if a.dn is None and a.de is None:
        print("[中止] 须给 --dn（名义厚度）或 --de（有效厚度）。")
        return 2
    return run(a)


if __name__ == "__main__":
    raise SystemExit(main())
