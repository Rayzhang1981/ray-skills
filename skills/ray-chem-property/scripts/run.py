# -*- coding: utf-8 -*-
"""一键编排：resolve → search → merge → export → html。

用法：
  python run.py --names 丙酮 甲醛 --template "<模板.xlsx>" --out output/
  python run.py --file 清单.txt --template "<模板.xlsx>" --out output/

说明：中文名需先转 CAS（模板/chemicalbook），否则 resolve 会解析失败；补采数据放
      output/supplement_{cas}.json 后重跑 merge 即可（supplement 优先于 PubChem）。
"""
import argparse
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PY = r"C:\Users\rayzh\.workbuddy\binaries\python\envs\default\Scripts\python.exe"


def run(args):
    print(">>", " ".join(args))
    r = subprocess.run(args, cwd=HERE)
    if r.returncode != 0:
        print(f"[run] 步骤失败退出码 {r.returncode}：{' '.join(args)}")
        sys.exit(r.returncode)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--names", nargs="*", help="化学品名称/CAS")
    ap.add_argument("--file", help="文本清单，每行一个")
    ap.add_argument("--json", help="JSON 清单")
    ap.add_argument("--template", help="模板 xlsx 路径（导出用，可选）")
    ap.add_argument("--out", default="output")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    cmd0 = [PY, os.path.join(HERE, "resolve_identifiers.py"), "--out", args.out]
    if args.file:
        cmd0 += ["--file", args.file]
    elif args.json:
        cmd0 += ["--json", args.json]
    else:
        cmd0 += list(args.names)
    run(cmd0)
    run([PY, os.path.join(HERE, "search_web.py"), "--out", args.out])
    run([PY, os.path.join(HERE, "merge_compare.py"), "--out", args.out])
    cmd_html = [PY, os.path.join(HERE, "gen_html.py"), "--outdir", args.out]
    if args.template:
        cmd_html += ["--template", args.template, "--output", os.path.join(args.out, "report.html")]
    run(cmd_html)
    if args.template:
        run([PY, os.path.join(HERE, "export_excel.py"), "--template", args.template, "--outdir", args.out])

    print("\n[run] 完成。产物在", args.out)
    print("  - 补充中文名/法规名录等：编辑 supplement_{cas}.json 后重跑 merge + gen_html + export")


if __name__ == "__main__":
    main()
