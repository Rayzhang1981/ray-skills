# -*- coding: utf-8 -*-
"""
ray-chem-compat 三件交付物统一生成器（v1.3.0 · 版式契约内建）
   用法：python build_deliverables.py [--in 清单.json] [--out-dir 目录] [--tag 标签]
        清单缺省＝ data/chem_index.json 48 名；--in 支持 [dict...]（含 cas/groups）或 [名字...]
   输出三件：交互矩阵.html / xlsx（2 sheet：判定半矩阵 + 材质矩阵）/ 危害标签 html
   契约：沿对角线只保左下半（i≥j）右上空置；实写 = N(N+1)/2；配色五码；
        Excel 表头行 2/3/4 全宽；图例只留底部；材质轴 √/×/—。
"""
import sys, io, os, re, json, collections, argparse
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
SK = r"C:\Users\rayzh\.workbuddy\skills\ray-chem-compat"
D = os.path.join(SK, "data")
sys.path.insert(0, os.path.join(SK, "scripts"))
import compat_engine as CE

CAMEO_IDX = None


def en_name(it):
    """CAMEO CAS→大写英文名（CHRIS 表内 title 化名）；查不到给 CAS 串"""
    global CAMEO_IDX
    if CAMEO_IDX is None:
        CAMEO_IDX = json.load(open(os.path.join(D, "cameo_reactivity.json"),
                                   encoding="utf-8"))
    cas = str(it.get("cas") or "").strip()
    for r in CAMEO_IDX.values():
        if str(r.get("cas") or "").strip() == cas and r.get("name"):
            return str(r["name"]).upper()
    return ""


PALETTE = {"X": "5B9BD5", "N": "FF0000", "C": "FFFF00", "Y": "00FF00", "SR": "FFC000"}
ORDER_LAB = ["R1", "R2", "R3", "R4", "E", "F", "G", "C", "T", "UR"]


def load(fn):
    return json.load(open(os.path.join(D, fn), encoding="utf-8"))


def items_from_args(a):
    if not a.fin:
        idx = load("chem_index.json")
        out = []
        for it in idx["chemicals"]:
            if it["cn"] in ("碳钢", "不锈钢304", "不锈钢316L"):
                continue
            cn = "氮气" if it["cn"] == "液氮" else it["cn"]
            out.append({"cn": cn, "cas": it.get("cas") or "", "groups": it.get("groups", [])})
        return out
    raw = json.load(open(a.fin, encoding="utf-8"))
    if isinstance(raw, list) and raw and isinstance(raw[0], str):   #名单模式 → 从索引/扩展联动
        base = {}
        idx = load("chem_index.json")
        for it in idx["chemicals"]:
            base.setdefault(it["cn"], it)
        if os.path.exists(os.path.join(D, "chem_index_ext.json")):
            for it in load("chem_index_ext.json"):
                base.setdefault(it.get("cn"), it)
        out = []
        for x in raw:
            if isinstance(x, dict):
                out.append(x)
            elif x in base:
                out.append(dict(base[x], cn=x))
            else:
                out.append({"cn": x, "cas": "", "groups": []})
        return out
    return raw                                                      # [{cn,cas,groups}]


def run(items, tag, out_dir):
    N = len(items)
    kb = CE.default_kb()
    codes, _ = CE.build_matrix(kb, items)
    print(f"[L1] {N} 名｜{N*(N+1)//2} 格｜{dict(collections.Counter(codes[(i,j)] for i in range(N) for j in range(i+1)))}")

    # 详情（N/C）
    det = {}
    for i in range(N):
        for j in range(i + 1):
            e = codes[(i, j)]
            if e not in ("N", "C"):
                continue
            hits = [r for ga in items[i].get("groups", []) for gb in items[j].get("groups", [])
                    for r in [kb["rules"].get((ga, gb))] if r is not None
                    and (kb["self_pair_verdict"].get(ga, "?") if ga == gb else r["symbol"]) == e]
            docs = []
            for r in hits:
                txt = r["documentation"][:900] + ("…（截断）" if len(r["documentation"]) > 900 else "")
                docs.append(f"{r['group_a']} WITH {r['group_b']}|{txt}")
            det[f"{i},{j}"] = {"c": sorted({x for r in hits for x in r["codes"]}),
                               "g": sorted({g for r in hits for g in r["potential_gases"]}),
                               "t": "; ".join(f"{r['group_a']}×{r['group_b']}" for r in hits),
                               "n": len(hits), "d": docs}

    # ---------- ① 交互矩阵 HTML（左下半） ----------
    payload = {"members": [[it["cn"], (it.get("cas") or "")] for it in items],
               "N": N,
               "sym": [[codes[(i, j)] for j in range(i + 1)] for i in range(N)],
               "det": {k: {**v, "d": [{"t": x.split("|", 1)[0], "d": x.split("|")[1] if True else x}
                                        for x in v["d"]]}
                        for k, v in det.items()}}
    f1 = os.path.join(out_dir, f"相容性矩阵-{tag}-引擎版.html")
    open(f1, "w", encoding="utf-8").write(
        open(os.path.join(D, "_tmpl_matrix.html"), encoding="utf-8").read()
        .replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False, separators=(",", ":"))))

    # ---------- ② xlsx（判定半矩阵 + 材质矩阵 sheet；版式对齐参考件 Compat_matrix-.xlsx） ----------
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
    BD = Border(left=Side(style="thin"), right=Side(style="thin"),
                top=Side(style="thin"), bottom=Side(style="thin"))
    CTR = Alignment(horizontal="center", vertical="center", wrap_text=True)
    from openpyxl.comments import Comment
    from openpyxl.utils import get_column_letter as _GL
    F_GRAY = PatternFill("solid", fgColor="F2F2F2")            # theme0 -0.05（label 带）
    wb = Workbook(); ws = wb.active; ws.title = "1-相容性矩阵(引擎版)"
    # —— 行 2：序号（浅灰底/居中/MS Sans Serif 10） ——
    for i in range(N):
        c = ws.cell(row=2, column=6 + i); c.value = i + 1
        c.font = Font(name="MS Sans Serif", size=10)
        c.alignment = Alignment(horizontal="center")
        c.fill = F_GRAY
    # —— 行 3：中文名（旋转 90°，行高 23.6，浅灰） ——
    ws.row_dimensions[3].height = 85.2
    for i, it in enumerate(items):
        c = ws.cell(row=3, column=6 + i); c.value = it["cn"]
        c.font = Font(name="MS Sans Serif", size=10)
        c.alignment = Alignment(text_rotation=90, horizontal="center")
        c.fill = F_GRAY
    # —— 行 4：英文全大写加粗（rot 90°，行高 218，瘦高竖排） ——
    ws.row_dimensions[4].height = 133.2
    for i, it in enumerate(items):
        en = (it.get("en") or en_name(it) or (it.get("cas") or "?")).upper()
        c = ws.cell(row=4, column=6 + i); c.value = en
        c.font = Font(name="Arial", size=9, bold=True)
        c.alignment = Alignment(text_rotation=90, horizontal="center")
    # —— 行 5..：A 序号（浅灰居中）/ B:D 合并中文名（浅灰）/ E 英文右靠加粗 ——
    for i, it in enumerate(items):
        r = 5 + i
        ws.merge_cells(f"B{r}:D{r}")
        ca = ws.cell(row=r, column=1); ca.value = i + 1
        ca.font = Font(name="MS Sans Serif", size=10)
        ca.alignment = Alignment(horizontal="center"); ca.fill = F_GRAY
        cb = ws.cell(row=r, column=2); cb.value = it["cn"]
        cb.font = Font(name="MS Sans Serif", size=10)
        cb.alignment = Alignment(horizontal="center"); cb.fill = F_GRAY
        ce = ws.cell(row=r, column=5); ce.value = en_name(it)
        ce.font = Font(name="Arial", size=9, bold=True)
        ce.alignment = Alignment(vertical="center", horizontal="right")
    # —— 值区（左下半，Arial 9 居中，无边框，五码着色） ——
    for i in range(N):
        for j in range(i + 1):
            e = codes[(i, j)]
            cc = ws.cell(row=5 + i, column=6 + j)
            cc.value = e
            col = "5B9BD5" if e == "X" else PALETTE[e]
            cc.fill = PatternFill("solid", fgColor=col)
            cc.font = Font(name="Arial", size=9)
            cc.alignment = Alignment(horizontal="center")
            drec = det.get(f"{i},{j}")
            if drec:
                doc = "\n".join(f"[{d.split('|')[0]}]\n{d.split('|',1)[1]}" for d in drec["d"])
                txt = (f"判定：{e}\n触发基团对：{drec['t']}\n判定代码：{', '.join(drec['c'])}\n"
                       f"潜在气体：{', '.join(drec['g'])}\n依据：\n{doc}")
                cc.comment = Comment(txt[:900] + ("…（截断）" if len(txt) > 900 else ""),
                                     "ray-chem-compat")
    # —— 图例（values_end + 6；LEGEND 行 F:T 合并；代码 G:L 英文 / M:T 中文；底部页脚） ——
    legend_top = 5 + N + 5
    ws.merge_cells(f"F{legend_top}:T{legend_top}")
    lt = ws.cell(row=legend_top, column=6); lt.value = "LEGEND  图例说明"
    lt.font = Font(name="宋体", size=11, bold=True)
    ws.row_dimensions[legend_top].height = 16.2
    LEGEND = [("?", "Undetermined", "未判定 — 无足够规则或基团集缺失，不猜", None),
              ("⚠", "Evidence conflict", "证据冲突 — 多源证据彼此矛盾，需人工裁决", None),
              ("*", "Non-library (inferred)", "非库判 — 基团集为兜底推断（B 级）", None),
              ("X", "No self reaction", "不会自身发生反应（仅用于对角格）", "5B9BD5"),
              ("N", "Not Compatible", "不相容，存在危险化学反应", "FF0000"),
              ("C", "Caution", "警告，可能存在较小的危险性反应", "FFFF00"),
              ("Y", "Compatible", "相容的，不会发生危险反应", "00FF00"),
              ("SR", "Self Reactive", "潜在的自反应", "FFC000")]
    for k, (code, en, zh, col) in enumerate(LEGEND):
        rr = legend_top + 1 + k
        ws.merge_cells(f"G{rr}:L{rr}"); ws.merge_cells(f"M{rr}:T{rr}")
        cc = ws.cell(row=rr, column=6); cc.value = code
        cc.font = Font(name="微软雅黑", size=11, bold=True)
        cc.alignment = Alignment(horizontal="center")
        ws.row_dimensions[rr].height = 16.2
        if col:
            cc.fill = PatternFill("solid", fgColor=col)
        ws.cell(row=rr, column=7).value = en
        ws.cell(row=rr, column=7).font = Font(name="微软雅黑", size=11)
        ws.cell(row=rr, column=13).value = zh
        ws.cell(row=rr, column=13).font = Font(name="微软雅黑", size=11)
    foot = legend_top + 10
    ws.merge_cells(f"F{foot}:AJ{foot+9}")
    ws.cell(row=foot, column=6).value = (
        " Compatibility Chart for :\n\nCreated by: ray-chem-compat (L1 引擎 × 2346 条规则)\n"
        "\nLast Reviewed by: \n\n适用场景刚性：≤35 °C、非气密隔热容器、混合存放 ≤1 天；"
        "沿对角线只保左下半（右上空置）。")
    ws.freeze_panes = "F5"
    ws.column_dimensions["A"].width = 4.1
    ws.column_dimensions["E"].width = 45.66

    # 材质 sheet
    wsm = wb.create_sheet("2-材质矩阵(引擎版)")
    wsm.row_dimensions[2].height = 17.4
    mats = ["铸铁", "碳钢", "304 不锈钢", "316 不锈钢", "PE", "PP", "PTFE"]
    for _col, _w in (("A", 8.6), ("B", 17.9), ("C", 15.0)):
        wsm.column_dimensions[_col].width = _w
    mmap = load("material_map.json")
    sh1 = load("sheet1_material.json")
    if isinstance(sh1, dict):
        rows = sh1["rows"]
    else:
        rows = sh1
    mat_rows = {str(rw[1]).strip(): [x if x is not None else "—" for x in rw[2]]
                for rw in rows}
    wsm.merge_cells(start_row=2, start_column=1, end_row=2, end_column=10)
    c2 = wsm.cell(row=2, column=1)
    c2.value = "化学品与材质相容性矩阵（引擎版 · 数据源＝母版 Sheet1 材质轴）"
    c2.font = Font(bold=True, size=12)
    wsm.merge_cells(start_row=4, start_column=1, end_row=5, end_column=2)
    c3 = wsm.cell(row=4, column=1)
    c3.value = "化学品 ＼ 材质"
    c3.font = Font(bold=True)
    c3.alignment = CTR
    for k, m in enumerate(mats):
        wsm.cell(row=4, column=3 + k).value = k + 1
        wsm.cell(row=5, column=3 + k).value = m
        for rr in (4, 5):
            cc = wsm.cell(row=rr, column=3 + k)
            cc.border = BD
            cc.alignment = CTR
            cc.font = Font(name="微软雅黑", size=11, bold=(rr == 5))
    n_src = n_dash = 0
    for i, it in enumerate(items):
        r = 6 + i
        wsm.cell(row=r, column=1).value = i + 1
        wsm.cell(row=r, column=2).value = it["cn"]
        wsm.cell(row=r, column=1).border = BD
        wsm.cell(row=r, column=2).border = BD
        for k in range(1, 10):
            wsm.cell(row=r, column=k).font = Font(name="微软雅黑", size=11)
        key = mmap.get(it["cn"])
        marks = mat_rows.get(key) if key else None
        if marks:
            n_src += 1
        else:
            marks = ["—"] * 7
            n_dash += 1
        for k, v in enumerate(marks):
            cc = wsm.cell(row=r, column=3 + k)
            cc.value = v
            cc.border = BD
            cc.alignment = CTR
            # ⚠ 判定标记着色（用户经验反解）：√=92D050 / ×=FF0000 / —=FFFF00
            cc.fill = ({
                "√": PatternFill("solid", fgColor="92D050"),
                "×": PatternFill("solid", fgColor="FF0000"),
                "—": PatternFill("solid", fgColor="FFFF00"),
            }).get(v) or cc.fill
        wsm.row_dimensions[r].height = 16.2
    r2 = 6 + N + 1
    LEGEND_FILL = {1: PatternFill("solid", fgColor="92D050"),
                   2: PatternFill("solid", fgColor="FF0000"),
                   3: PatternFill("solid", fgColor="FFFF00")}
    for j, txt in enumerate(["LEGEND  图例说明", "√  相容（该材质可用于该化学品）",
                             "×  不相容（不可使用）", "—  无数据（母版 Sheet1 未收录，未评估）",
                             "⚠ 材质轴与化学轴独立；√ 不代表混存安全（判定归相容性矩阵）",
                             "⚠ 母版 Sheet1 未注明评估依据，本表如实继承不带二次判断"]):
        cc = wsm.cell(row=r2 + j, column=1)
        cc.value = txt
        cc.font = Font(name="微软雅黑", size=11, bold=(j == 0))
        if j in LEGEND_FILL:
            cc.fill = LEGEND_FILL[j]

    f2 = os.path.join(out_dir, f"相容性矩阵-{tag}-引擎版.xlsx")
    wb.save(f2)
    print(f"[2] {os.path.basename(f2)} {os.path.getsize(f2):,} B｜材质：有源 {n_src}/无源 {n_dash}")

    # ---------- ③ 中文危害标签 HTML ----------
    lab = {s["code"]: [s["label_zh"], s["statement_zh"]] for s in load("hazard_statements.json")
           if s["code"]}
    pairs = []
    chk = {i: collections.Counter() for i in range(N)}
    for i in range(N):
        for j in range(i + 1):
            e = codes[(i, j)]
            if e not in ("N", "C"):
                continue
            cs_all = det.get(f"{i},{j}", {}).get("c", [])
            cs_sub = [c for c in cs_all if c != "NR"]
            pairs.append({"a": items[j]["cn"], "b": items[i]["cn"], "s": e,
                          "sub": cs_sub,
                          "cs": cs_all, "nr": int("NR" in cs_all)})
            for k in (i, j):
                for c in cs_sub:
                    chk[k][c] += 1
    payload_h = {"lab": lab, "order": ORDER_LAB,
                 "chem": [{"name": it["cn"],
                           "cnt": {c: chk[i].get(c, 0) for c in ORDER_LAB if chk[i].get(c, 0)},
                           "pairs": sum(1 for p in pairs if p["a"] == it["cn"] or p["b"] == it["cn"])}
                          for i, it in enumerate(items)],
                 "pairs": pairs}
    f3 = os.path.join(out_dir, f"中文危害标签矩阵-{tag}.html")
    open(f3, "w", encoding="utf-8").write(
        open(os.path.join(D, "_tmpl_hazard.html"), encoding="utf-8").read().replace(
            "__PAYLOAD__", json.dumps(payload_h, ensure_ascii=False, separators=(",", ":"))))
    print(f"[3] {os.path.basename(f3)} {os.path.getsize(f3):,} B")
    return f1, f2, f3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="fin", help="化学品清单（[{cn,cas,groups}] 或 [名字...]）")
    ap.add_argument("--out-dir", default=None)
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    items = items_from_args(a := args) if False else items_from_args(args)
    N = len(items)
    out_dir = args.out_dir or r"E:\LingXi-DSH\sessions\Chemical Compatible Matrix"
    os.makedirs(out_dir, exist_ok=True)
    tag = (args.tag or f"{N}化学品")
    run(items, tag, out_dir)


if __name__ == "__main__":
    main()
