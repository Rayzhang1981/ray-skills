# -*- coding: utf-8 -*-
"""Step 3a — 把最终数据回填到 106 列模板 Excel（保留多级表头/合并单元格/单位行）。

以用户提供的「工艺物料安全物性数据表」模板为母版，复制出新文件，
把 final_{cas}.json 的字段值按 field_schema.json 的列映射回填成新数据行。

用法：
  python export_excel.py --template <模板.xlsx> --outdir output --output 结果.xlsx
"""
import argparse
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


def load_schema():
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        return json.load(f)


def is_blank_row(ws, r, max_col=111):
    """整行无实质内容（公式残留 / 纯空白都算空）。"""
    for c in range(2, max_col + 1):
        v = ws.cell(row=r, column=c).value
        if v in (None, ""):
            continue
        if isinstance(v, str) and v.strip().startswith("="):  # 公式残留（如 =IF(#REF!...)）
            continue
        return False
    return True


def first_blank_row(ws, start=9, max_col=111):
    """从 start 起找第一个整行全空的行（不管中间是否断档）。"""
    r = start
    limit = max(ws.max_row, start) + 100
    while r <= limit:
        if is_blank_row(ws, r, max_col):
            return r
        r += 1
    return r


def next_data_row(ws, col_name=3, col_cas=5, start=9):
    """兼容旧调用：等同于 first_blank_row。"""
    return first_blank_row(ws, start=start)


def max_seq(ws, col_seq=2, start=9):
    mx = 0
    for r in range(start, ws.max_row + 1):
        v = ws.cell(row=r, column=col_seq).value
        if isinstance(v, (int, float)):
            mx = max(mx, int(v))
        elif isinstance(v, str) and v.strip().isdigit():
            mx = max(mx, int(v.strip()))
    return mx


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--template", required=True, help="模板 xlsx 路径")
    ap.add_argument("--outdir", default="output", help="含 final_*.json 的目录")
    ap.add_argument("--output", help="输出 xlsx 路径（默认 <outdir>/物性汇总表-补充.xlsx）")
    args = ap.parse_args()

    schema = load_schema()
    col_of = {f["key"]: f["col"] for f in schema["fields"]}

    # 批量保序命名（01_final_xxx.json）优先；否则取常规 final_xxx.json
    prefixed = sorted(glob.glob(os.path.join(args.outdir, "*_final_*.json")))
    final_files = prefixed if prefixed else \
        sorted(glob.glob(os.path.join(args.outdir, "final_*.json")))
    if not final_files:
        print("[export] 未找到 final_*.json，请先运行 merge_compare.py")
        sys.exit(1)

    out_path = args.output or os.path.join(args.outdir, "物性汇总表-补充.xlsx")
    shutil.copyfile(args.template, out_path)
    wb = load_workbook(out_path)
    ws = wb["物性汇总表"]

    seq = max_seq(ws)
    row = first_blank_row(ws)
    print(f"[export] 现有最大序号 {seq}，首个空白数据行 R{row}")

    # Emergency Guidelines 应急准则列（DB）宽固化 120 + 数据行高 50
    # （2026-08-27 用户实测定标：默认 15.8 宽导致 auto-fit 行高爆炸；拉宽后 50pt 一行足够）
    emg_letter = col_of.get("emergency_guidelines")
    if emg_letter:
        ws.column_dimensions[emg_letter].width = 120.0
        # 确保应急单元格 wrap_text 开启（列宽 120 + 行高 50 才有意义）
        emg_idx = column_index_from_string(emg_letter)
        for r in range(row, row + len(final_files)):
            c = ws.cell(row=r, column=emg_idx)
            al = c.alignment.copy() if c.alignment else None
            from openpyxl.styles import Alignment

            ws.cell(row=r, column=emg_idx).alignment = Alignment(
                horizontal=(al.horizontal if al and al.horizontal else "left"),
                vertical="top", wrap_text=True)

    # AI 辅助声明 + 数据核实提醒（写入 Appendix 说明页，不污染物性汇总表表头/合并区）
    from datetime import datetime

    def _find_free_note_row(ws_t, max_scan=50):
        """找第一个【未合并且为空】的 A 列行；跳过合并区域（MergedCell 只读，写入会抛异常）。
        检查合并区域用公开 API：cell.coordinate 是否为某 merge range 的非左上格。"""
        merged_coords = set()
        for rng in ws_t.merged_cells.ranges:
            for rr in range(rng.min_row, rng.max_row + 1):
                for cc in range(rng.min_col, rng.max_col + 1):
                    if (rr, cc) != (rng.min_row, rng.min_col):  # 左上格可写，其余是 MergedCell
                        merged_coords.add((rr, cc))
        for r2 in range(1, max_scan + 1):
            if (r2, 1) in merged_coords:
                continue
            v = ws_t.cell(row=r2, column=1).value
            if v in (None, ""):
                return r2
        return max_scan + 1

    app = wb["Appendix"] if "Appendix" in wb.sheetnames else wb.create_sheet("Appendix")
    note_row = _find_free_note_row(app)
    app.cell(row=note_row, column=1,
             value=f"AI 辅助生成（{datetime.now():%Y-%m-%d %H:%M}）· 数据来自 PubChem/NIST/CAMEO/监管名录等公开源，"
                   f"未逐一人工核实；本表用于专业审查参考，请核实后用于安全决策")

    for ff in sorted(final_files):
        final = json.load(open(ff, encoding="utf-8"))
        # 来源证据链：同目录 merged_{cas}.json 的 fields[key] 含 source/candidates
        merged = None
        mfields = {}
        mf = ff.replace("final_", "merged_")
        if os.path.exists(mf):
            try:
                merged = json.load(open(mf, encoding="utf-8"))
                mfields = merged.get("fields", {})
            except Exception:
                pass
        seq += 1
        ws.cell(row=row, column=2, value=seq)  # 序号
        for key, val in final.items():
            if key not in col_of or val in (None, ""):
                continue
            cell = ws.cell(row=row, column=column_index_from_string(col_of[key]), value=str(val))
            # 来源注释（同行不同列来源可不同）
            mf_item = mfields.get(key, {})
            srcs = []
            cands = mf_item.get("candidates", [])
            for c in cands:
                s = c.get("source") or mf_item.get("source")
                if s and s not in srcs:
                    srcs.append(s)
            if not srcs and mf_item.get("source"):
                srcs.append(mf_item["source"])
            if srcs:
                text = "数据来源:\n" + "\n".join(srcs[:4])
                cm = Comment(text, "ray-chem-property")
                cm.width, cm.height = 260, 60
                cell.comment = cm
        # 应急准则长文本行高控制（2026-08-27 用户实测定标）：
        # Emergency 列宽拉到 ~120 后，每行高度固定 50pt 防止 auto-fit 撑爆；
        # 文本超出行高时 Excel 换行列内滚动可见（wrap_text 由母版样式继承）
        ws.row_dimensions[row].height = 50.0
        row += 1

    wb.save(out_path)
    start_row = row - len(final_files)
    print(f"[export] 已回填 {len(final_files)} 个物料 → {out_path}（起始行 {start_row}）")


if __name__ == "__main__":
    main()
