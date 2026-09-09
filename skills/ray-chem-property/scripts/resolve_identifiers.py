# -*- coding: utf-8 -*-
"""Step 0 — 输入解析：化学品清单 → 标准化 input.json。

输入形式（三种任选）：
  1) 命令行参数：多个名称/CAS，空格分隔
     python resolve_identifiers.py 丙酮 67-64-1 "氢氧化钠"
  2) 文本文件：每行一个名称/CAS
     python resolve_identifiers.py --file chemicals.txt
  3) JSON 清单：--json [{...}]

输出：<out_dir>/input.json —— 每个物料含 resolved（cid/cas/name/formula/mw/...）+ 混合物/聚合物标记。

核心原则：CAS 是唯一主键；中文名/英文名/简写仅作检索入口，先解析成 CAS。
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pubchem_api import name_to_cid, get_properties, IDENTIFIER_PROPS  # noqa: E402


def resolve(name):
    """单个名称/CAS → 标准化记录。"""
    rec = {"input": name, "resolved": None, "is_mixture": False, "is_polymer": False}
    cid = name_to_cid(name)
    if cid is None:
        rec["error"] = "PubChem 未解析到 CID"
        return rec

    props = get_properties(cid, IDENTIFIER_PROPS) or {}
    resolved = {
        "cid": cid,
        "name_en": props.get("IUPACName") or "",
        "formula": props.get("MolecularFormula") or "",
        "mw": props.get("MolecularWeight"),
        "smiles": props.get("CanonicalSMILES") or "",
        "isomeric_smiles": props.get("IsomericSMILES") or "",
        "inchikey": props.get("InChIKey") or "",
    }
    # CAS 从输入直接判断：若输入本身就是 CAS（纯数字-连字符），直接采用
    stripped = name.strip()
    if _looks_like_cas(stripped):
        resolved["cas"] = stripped
    rec["resolved"] = resolved

    # 混合物/聚合物启发式标记（可人工修正）
    low = name.lower()
    if any(k in name for k in ("溶液", "混合", "%")) or any(k in low for k in ("mixture", "solution")):
        rec["is_mixture"] = True
    if any(k in low for k in ("poly", "resin", "pe ", "pp ", "polymer")):
        rec["is_polymer"] = True
    return rec


def _looks_like_cas(s):
    parts = s.split("-")
    return len(parts) >= 3 and all(p.isdigit() for p in parts[:-1]) and parts[-1].isdigit()


def load_inputs(args):
    items = []
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            items = [ln.strip() for ln in f if ln.strip()]
    elif args.json:
        data = json.load(open(args.json, encoding="utf-8"))
        if isinstance(data, list):
            items = [x.get("name") or x.get("cas") or str(x) for x in data]
        elif isinstance(data, dict):
            items = [data.get("name") or data.get("cas")]
    else:
        items = args.names
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("names", nargs="*", help="化学品名称/CAS，空格分隔")
    ap.add_argument("--file", help="文本文件，每行一个名称/CAS")
    ap.add_argument("--json", help="JSON 清单文件")
    ap.add_argument("--out", default="output", help="输出目录，默认 output/")
    args = ap.parse_args()

    items = load_inputs(args)
    if not items:
        print("未提供任何输入。用法示例：\n  python resolve_identifiers.py 丙酮 67-64-1")
        sys.exit(1)

    os.makedirs(args.out, exist_ok=True)
    results = [resolve(n) for n in items]

    out_path = os.path.join(args.out, "input.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    n_ok = sum(1 for r in results if r.get("resolved"))
    print(f"[resolve] 解析 {len(results)} 个，成功 {n_ok} 个 → {out_path}")
    for r in results:
        if r.get("resolved"):
            print(f"  ✓ {r['input']} → CID {r['resolved']['cid']}  CAS {r['resolved'].get('cas','?')}")
        else:
            print(f"  ✗ {r['input']} → {r.get('error','未解析')}")
    return out_path


if __name__ == "__main__":
    main()
