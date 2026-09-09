#!/usr/bin/env python3
"""
ray-translate 残留英文诊断 — 通用版
扫描翻译后文件中的残留英文，统计词频并输出示例单元格
用法：
    python check_remaining.py <翻译后文件.xlsm> [--sheets Sheet1 Sheet2 ...]
"""
import openpyxl
import re
import sys
from collections import Counter


def load_sheets_from_wb(wb):
    """默认使用工作簿中的所有非空 sheet"""
    return wb.sheetnames


def scan_remaining(filepath, target_sheets=None):
    wb = openpyxl.load_workbook(filepath, keep_vba=True, data_only=False)
    sheets = target_sheets if target_sheets else load_sheets_from_wb(wb)

    all_remaining = []

    for sname in sheets:
        ws = wb[sname]
        remaining = []
        for row_idx, row in enumerate(
            ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column), 1
        ):
            for col_idx, cell in enumerate(row, 1):
                if cell.value is None:
                    continue
                val = cell.value
                if isinstance(val, str) and not val.startswith("="):
                    # 提取 >=3 字母的英文单词
                    eng_words = re.findall(r'\b[A-Za-z]{3,}(?:/[A-Za-z]{3,})*\b', val)
                    if eng_words:
                        remaining.append({
                            'sheet': sname,
                            'row': row_idx,
                            'col': col_idx,
                            'value': val[:120],
                            'eng_words': eng_words,
                        })

        if remaining:
            print(f"\n{'=' * 60}")
            print(f"Sheet: {sname} -- {len(remaining)} cells with English")
            print(f"{'=' * 60}")
            word_freq = Counter()
            for r in remaining:
                for w in r['eng_words']:
                    word_freq[w] += 1

            print("Top remaining English words (Top 40):")
            for word, count in word_freq.most_common(40):
                print(f"  {word}: {count}")

            print(f"\nSample cells (first 15):")
            for r in remaining[:15]:
                print(f"  [{r['row']},{r['col']}] {r['value'][:100]}")

            all_remaining.extend(remaining)

    print(f"\n{'=' * 60}")
    print(f"OVERALL: {len(all_remaining)} cells still have English content")
    return all_remaining


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python check_remaining.py <翻译后文件.xlsm> [--sheets Sheet1 Sheet2 ...]")
        sys.exit(1)

    filepath = sys.argv[1]
    target_sheets = None

    if "--sheets" in sys.argv:
        idx = sys.argv.index("--sheets")
        target_sheets = sys.argv[idx + 1:]

    scan_remaining(filepath, target_sheets)