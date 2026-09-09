# -*- coding: utf-8 -*-
"""从母版模板派生「纯 N 物料」Excel：复制表头 R1-8 + 清空旧数据行 + 写入 final_*.json 数据。

与 export_excel.py（追加到母版）不同：本脚本产出只含本次物料的独立新表，
数据行从 R9 起（样式继承母版成品行），带来源注释 + AI 声明。

用法:
  python new_from_template.py --template <母版.xlsx> --outdir output --output 结果.xlsx
"""
import argparse
import copy
import glob
import json
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from openpyxl import load_workbook  # noqa: E402
from openpyxl.comments import Comment  # noqa: E402
from openpyxl.utils import column_index_from_string  # noqa: E402

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "field_schema.json")
HDR_END = 8          # 表头 R1-8
DATA_START = 9       # 数据从 R9 起
REF_FIRST = 9        # 样式参照：首行（顶线 medium）
REF_MID = 10         # 样式参照：中间行（hair 网格）
MAX_COL = 106


def load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True)
    ap.add_argument("--outdir", default="output")
    ap.add_argument("--output", help="输出 xlsx 路径（默认 <outdir>/物性汇总表-新表.xlsx）")
    args = ap.parse_args()

    schema = load_schema()
    col_of = {f["key"]: f["col"] for f in schema["fields"]}

    # 批量保序命名（01_final_xxx.json）优先；否则取常规 final_xxx.json
    prefixed = sorted(glob.glob(os.path.join(args.outdir, "*_final_*.json")))
    final_files = prefixed if prefixed else \
        sorted(glob.glob(os.path.join(args.outdir, "final_*.json")))
    if not final_files:
        print("[new] 未找到 final_*.json")
        sys.exit(1)

    out_path = args.output or os.path.join(args.outdir, "物性汇总表-新表.xlsx")
    shutil.copyfile(args.template, out_path)
    wb = load_workbook(out_path)
    ws = wb["物性汇总表"]

    # 1) 清空旧数据行（R9 起所有内容 + 注释），保留表头
    for r in range(DATA_START, ws.max_row + 1):
        for c in range(1, MAX_COL + 1):
            cell = ws.cell(row=r, column=c)
            cell.value = None
            cell.comment = None
    # 2) 数据区样式继承：用母版成品行（首行/中间行）逐列样式做基底
    base_style_rows = {REF_FIRST: REF_FIRST, REF_MID: REF_MID}
    first_styles = {}
    mid_styles = {}
    for c in range(1, MAX_COL + 1):
        first_styles[c] = ws.cell(row=REF_FIRST, column=c)._style
        mid_styles[c] = ws.cell(row=REF_MID, column=c)._style

    # 3) 写 17 个物料
    for i, ff in enumerate(final_files, start=1):
        final = json.load(open(ff, encoding="utf-8"))
        mf = ff.replace("final_", "merged_")
        mfields = {}
        if os.path.exists(mf):
            try:
                mfields = json.load(open(mf, encoding="utf-8")).get("fields", {})
            except Exception:
                pass
        r = DATA_START + i - 1
        ws.cell(row=r, column=2, value=i)  # 序号
        # 样式：首行用 first_styles（含 medium 顶线），其余用 mid_styles
        styles = first_styles if r == REF_FIRST else mid_styles
        for c in range(1, MAX_COL + 1):
            ws.cell(row=r, column=c)._style = copy.copy(styles[c])
        for key, val in final.items():
            if key not in col_of or val in (None, ""):
                continue
            cell = ws.cell(row=r, column=column_index_from_string(col_of[key]), value=str(val))
            mf_item = mfields.get(key, {})
            srcs = []
            for cand in mf_item.get("candidates", []):
                s = cand.get("source") or mf_item.get("source")
                if s and s not in srcs:
                    srcs.append(s)
            if not srcs and mf_item.get("source"):
                srcs.append(mf_item["source"])
            if srcs:
                cm = Comment("数据来源:\n" + "\n".join(srcs[:4]), "ray-chem-property")
                cm.width, cm.height = 260, 60
                cell.comment = cm
        # 行高
        if ws.row_dimensions[REF_MID].height:
            ws.row_dimensions[r].height = ws.row_dimensions[REF_MID].height
        # 序号列样式单独（首行参照）
        ws.cell(row=r, column=2)._style = copy.copy(styles[2])

    # 4) 删除多余行（R9+n 之后全部清掉）
    n = len(final_files)
    extra = ws.max_row - (DATA_START + n - 1)
    if extra > 0:
        ws.delete_rows(DATA_START + n, extra)

    # 5) Appendix AI 声明
    from datetime import datetime
    app = wb["Appendix"] if "Appendix" in wb.sheetnames else wb.create_sheet("Appendix")
    merged_coords = set()
    for rng in app.merged_cells.ranges:
        for rr in range(rng.min_row, rng.max_row + 1):
            for cc in range(rng.min_col, rng.max_col + 1):
                if (rr, cc) != (rng.min_row, rng.min_col):
                    merged_coords.add((rr, cc))
    note_row = 1
    while note_row <= 60:
        if (note_row, 1) in merged_coords:
            note_row += 1
            continue
        if app.cell(row=note_row, column=1).value in (None, ""):
            break
        note_row += 1
    app.cell(row=note_row, column=1,
             value=f"AI 辅助生成（{datetime.now():%Y-%m-%d %H:%M}）· 数据来自 PubChem/NIST/CAMEO/监管名录等公开源，"
                   f"未逐一人工核实；本表用于专业审查参考，请核实后用于安全决策")

    wb.save(out_path)
    print(f"[new] 纯 {n} 物料新表 → {out_path}（数据 R{DATA_START}-R{DATA_START + n - 1}）")


if __name__ == "__main__":
    main()
