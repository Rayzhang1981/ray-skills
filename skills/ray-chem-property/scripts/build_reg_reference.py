# -*- coding: utf-8 -*-
"""构建本地法规参考索引：GBZ OEL / 危化品目录 / 有毒气体目录 → JSON。

背景（2026-08-15）：外部同场景 skill（chem-properties-excel）的 3 份本地离线法规参考数据
（GBZ 2.1 OEL 295 种 / 危化品目录 2674 种含中文 GHS 类别 / 有毒气体检测目录 271 种）
正好补齐本地 skill 的法规名录字段（reg_hazchem/reg_high_toxic）与中文 GHS 类别——
本地法规名录目前只能靠 whpdj 浏览器补采（国内网络不可达），这 3 份数据实现本地秒查。
法规数据本身公有（来源为 GBZ 2.1 / 《危险化学品目录》(2015版) 等法规文件），
此处仅做格式重建，不复制外部 skill 的任何组织文本。

用法：
  python scripts/build_reg_reference.py          # 从 data/raw-*.md 重建 3 个 JSON 索引
  python scripts/build_reg_reference.py --query 67-64-1   # 查询某 CAS 在各目录的命中情况

输出（data/）：
  GBZ_OEL索引.json     {cas: {name_cn, name_en, mac, twa, stel}}          # 接触限值（mg/m³）
  危化品目录索引.json   {cas: {hazards: "中文GHS类别", toxic: bool}}        # reg_hazchem + haz_* 中文
  有毒气体目录索引.json {cas: {name, sources: [来源], mac, twa, stel}}     # reg_high_toxic 判定
"""
import argparse
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.normpath(os.path.join(HERE, "..", "data"))
RAW = {
    "gbz": os.path.join(DATA_DIR, "raw-GBZ-OEL.md"),
    "hazcat": os.path.join(DATA_DIR, "raw-危化品目录.md"),
    "toxic": os.path.join(DATA_DIR, "raw-有毒气体目录.md"),
}


def parse_gbz(path):
    """GBZ OEL 表格：| 序号 | 名称 | 英文名 | CAS | MAC | PC-TWA | PC-STEL | 备注 |"""
    recs = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("|") or "---" in line or line.startswith("| 序号"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 6:
            continue
        cas = cols[3]
        if not re.match(r"^\d{2,7}-\d{2}-\d$", cas):
            continue
        recs[cas] = {
            "name_cn": cols[1],
            "name_en": cols[2],
            "mac": cols[4] or None,
            "twa": cols[5] or None,
            "stel": cols[6] if len(cols) > 6 else None,
            "note": cols[7] if len(cols) > 7 else "",
        }
    return recs


def parse_hazcat(path):
    """危化品目录：| CAS号 | 危险性类别 |（分号分隔的中文 GHS 类别）"""
    recs = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line.startswith("|") or "---" in line or line.startswith("| CAS"):
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        if len(cols) < 2:
            continue
        cas = cols[0]
        if not re.match(r"^\d{2,7}-\d{2}-\d$", cas):
            continue
        hazards = cols[1] if len(cols) > 1 else ""
        recs[cas] = {
            "hazards": hazards,
            "toxic": "剧毒" in hazards,  # 备注栏剧毒 → 高毒判定
        }
    return recs


def parse_toxic(path):
    """有毒气体目录：4 章节（高毒54 / GB50493补充3 / HG20660 66 / 危化品目录剧毒清单），表格列各异。"""
    recs = {}
    current_src = ""
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("##"):
            # 章节标题 → 来源
            if "高毒物品目录" in line:
                current_src = "高毒物品目录2003"
            elif "GB/T 50493" in line:
                current_src = "GB/T 50493-2019附录B"
            elif "HG/T 20660" in line:
                current_src = "HG/T 20660-2017附录A"
            elif "剧毒" in line:
                current_src = "危化品目录2015剧毒"
            continue
        if not line.startswith("|") or "---" in line or "序号" in line or "CAS" in line:
            continue
        cols = [c.strip() for c in line.strip("|").split("|")]
        # 找 CAS 列（含连字符数字）；剧毒清单章节可能只有 CAS
        cas = ""
        name = ""
        for c in cols:
            if re.match(r"^\d{2,7}-\d{2}-\d$", c):
                cas = c
                break
        if not cas:
            continue
        # 名称：CAS 前面最近的非数字列
        if cas in cols:
            i = cols.index(cas)
            if i > 0 and not re.match(r"^\d+$", cols[i - 1]):
                name = cols[i - 1]
        # MAC/TWA/STEL：CAS 后的数字列（可能 None）
        mac = twa = stel = None
        rest = cols[cols.index(cas) + 1:]
        nums = [c for c in rest if c and re.match(r"^[\d.]+$", c)]
        if len(nums) >= 1:
            twa = nums[0]
        if len(nums) >= 2:
            stel = nums[1]
        if cas not in recs:
            recs[cas] = {"name": name, "sources": [], "mac": mac, "twa": twa, "stel": stel}
        if current_src and current_src not in recs[cas]["sources"]:
            recs[cas]["sources"].append(current_src)
        if mac and not recs[cas]["mac"]:
            recs[cas]["mac"] = mac
        if twa and not recs[cas]["twa"]:
            recs[cas]["twa"] = twa
        if stel and not recs[cas]["stel"]:
            recs[cas]["stel"] = stel
    # 补充：纯 CAS 列表（如第 4 章节"剧毒"清单的代码块 `CAS, CAS, ...`）
    text = open(path, encoding="utf-8").read()
    for blk in re.findall(r"```\s*([^`]*?)\s*```", text, re.S):
        for cas in re.findall(r"\d{2,7}-\d{2}-\d", blk):
            if cas not in recs:
                recs[cas] = {"name": "", "sources": [], "mac": None, "twa": None, "stel": None}
            if current_src and current_src not in recs[cas]["sources"]:
                recs[cas]["sources"].append(current_src)
    return recs


def main():
    ap = argparse.ArgumentParser(description="构建本地法规参考索引")
    ap.add_argument("--query", help="查询某 CAS 在各目录的命中情况")
    ap.add_argument("--outdir", default=DATA_DIR)
    args = ap.parse_args()

    gbz = parse_gbz(RAW["gbz"])
    hazcat = parse_hazcat(RAW["hazcat"])
    toxic = parse_toxic(RAW["toxic"])

    if args.query:
        q = args.query.strip()
        print(f"=== CAS {q} 命中情况 ===")
        if q in gbz:
            print(f"  GBZ OEL: {gbz[q]}")
        else:
            print("  GBZ OEL: 未收录")
        if q in hazcat:
            h = hazcat[q]
            print(f"  危化品目录: 已列入{'（剧毒）' if h['toxic'] else ''}")
            print(f"    GHS 类别: {h['hazards'][:120]}")
        else:
            print("  危化品目录: 未列入")
        if q in toxic:
            print(f"  有毒气体目录: {toxic[q]}")
        else:
            print("  有毒气体目录: 未收录")
        return

    os.makedirs(args.outdir, exist_ok=True)
    for fname, recs in (
        ("GBZ_OEL索引.json", gbz),
        ("危化品目录索引.json", hazcat),
        ("有毒气体目录索引.json", toxic),
    ):
        with open(os.path.join(args.outdir, fname), "w", encoding="utf-8") as f:
            json.dump(recs, f, ensure_ascii=False, indent=1)
        n_toxic = sum(1 for r in recs.values() if isinstance(r, dict) and r.get("toxic"))
        print(f"[reg] {fname}: {len(recs)} 条{'（剧毒 ' + str(n_toxic) + '）' if fname.startswith('危化品') else ''}")

    print(f"[reg] DONE: GBZ {len(gbz)} / 危化品 {len(hazcat)} / 有毒气体 {len(toxic)}")


if __name__ == "__main__":
    main()
