#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract_terms.py — 译前术语提取与锁定（CAT 三段式 ① 的执行器）

作用：把「人工挑词 grep」升级为「程序化全量提取 → 自动对库 → 输出锁定表 + 缺口清单」。
      锁定表直接注入 spec；缺口清单走权威源核验后入库。

用法：
  # 从源文档程序化提取（推荐）
  python extract_terms.py source.txt --lang en -n 400
  # 目标准备清单（兼容旧流程，检查手工候选表的覆盖率）
  python extract_terms.py --from-list candidates.txt
  # 中→英方向
  python extract_terms.py source_zh.txt --lang zh -n 300
  # 自检（非空断言 + 已知命中 + SABOTAGE 负控）
  python extract_terms.py --selftest

输出（默认与源文件同目录，--outdir 可改）：
  <stem>_locked.md   命中的锁定表（六列 schema，可直接拷进 spec）
  <stem>_gaps.md     缺口清单（按频次排序 + 上下文样例，供权威源核验）
  <stem>_terms.json  机器可读结果

判据要点（踩坑换来的）：
  · EN 匹配用「词边界子串」+ 别名拆分，禁「整格全等」——否则 compound 词条下的词被误判为缺（v3.5.0）
  · 英式/美式拼写并收（rationalisation/rationalization），两侧都要能命中（v3.5.0）
  · 缺口≠错误：通用词（湍流/浮力/等熵）无争议，可直接采用；领域专有词（rainout/congestion）必须权威源确证
"""
import argparse
import io
import json
import os
import re
import sys
from collections import Counter, defaultdict

HOME = os.path.expanduser("~")
TB_DIR = os.path.join(HOME, ".workbuddy", "skills", "ray-translate", "data", "termbase")
LIB_FILES = ("core.md", "chem.md", "chem-eng.md", "safety.md", "_hot.md", "_graduated.md")

EN_STOP = set("""a an the and or but if then than that this these those of in on at by for with from to into
over under between during after before above below is are was were be been being do does did have has had
will would shall should can could may might must not no nor so as it its their there here when where which
who whom whose what how why all any both each few more most other some such only own same too very s t
also however therefore thus hence e g i e etc vs fig figure table equation section chapter annex appendix
one two three four five first second third new used using given based per figure""".split())

ZH_STOP = set("的了在是和与及或与及其为对从到把被将由使可以能够进行以及并且但是因为所以这那这些那些一个"
              "我们你们他们它们其中所谓上述如下见表如图所示情况问题方法过程条件要求规定标准中之时后前")

# 程序词/单位/样板词：出现在 n-gram 中即丢（来自"计算步骤/公式编号/单位/参考文献"等排版区）
NOISE = set("""nr no et al min max mg kg mol bar kpa mpa mm cm km hr sec step steps formula eq equation
page pages book table figure fig ref refs appendix annex chapter section part vol pp ed eds isbn doi
http www com org net gov edu pdf doc txt xls ppt following above below case cases
total sub value values data note notes item items type types level levels phase phases""".split())


def load_library(tb_dir=TB_DIR):
    """四库 + 热词 + 毕业库 → {别名: (EN原文, ZH, 拒用, 来源)}"""
    alias_map = {}
    rows = []
    for fn in LIB_FILES:
        p = os.path.join(tb_dir, fn)
        if not os.path.exists(p):
            continue
        for line in io.open(p, encoding="utf-8"):
            line = line.strip()
            if not line.startswith("|"):
                continue
            cols = [c.strip() for c in line.strip("|").split("|")]
            if len(cols) < 3 or not cols[0] or cols[0] == "EN" or re.match(r"^-+$", cols[0]):
                continue
            en, zh = cols[0], cols[1]
            src = cols[4] if len(cols) > 4 else ""
            rows.append((en, zh, cols[2] if len(cols) > 2 else "", src))
            for a in aliases(en):
                alias_map.setdefault(a, (en, zh, src))
                sing = " ".join(singular(w) for w in a.split())
                if sing != a:
                    alias_map.setdefault(sing, (en, zh, src))
    return alias_map, rows


def singular(w):
    """粗粒度单复数归一（pool fires → pool fire；gases → gas）"""
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 4 and w.endswith("ses"):
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def aliases(en):
    """EN 词条 → 别名集合（拆 / , ; 、括号内缩写；词边界子串匹配的基础）"""
    s = en.lower()
    paren = re.findall(r"\(([^)]*)\)", s)
    s = re.sub(r"\([^)]*\)", " ", s)
    parts = re.split(r"[/,;、]| or | and ", s)
    out = set()
    for p in parts + paren:
        p = re.sub(r"\s+", " ", p).strip(" .—-")
        if len(p) >= 2:
            out.add(p)
    return out


def norm(s):
    return re.sub(r"\s+", " ", s.lower()).strip()


def build_index(alias_map):
    """按首词建倒排索引：contains 检查只看首词命中的别名（O(候选×库) → O(候选×少量)）"""
    idx = defaultdict(list)
    for a, v in alias_map.items():
        if len(a) >= 4:
            idx[a.split()[0]].append((a, v))
    return idx


def lookup(term, alias_map, rows, idx=None):
    """三级判定：① 精确别名（含单复数归一） ② 词边界子串 ③ 未命中"""
    t = norm(term)
    for cand in (t, " ".join(singular(w) for w in t.split())):
        if cand in alias_map:
            return "exact", alias_map[cand]
    # ② term 内部含已收录词条（如 dense gas dispersion ⊃ dense gas）——走倒排索引
    toks = set(t.split())
    for w in toks:
        for a, v in (idx or {}).get(w, ()):
            if re.search(r"(?<![a-z0-9])" + re.escape(a) + r"(?![a-z0-9])", t):
                return "contains", v
    return None, None


def extract_en(text, min_freq=3, top=400, max_n=3, min_words=2):
    """EN 候选：句内 n-gram（min_words~max_n），去过尾词、去停用词、**去页眉页脚样板词**、
       按 频次×(1+0.5×词数) 排序（多词术语优先——单词多为通用词，注入价值低）"""
    # 页覆盖：样板词（页眉/页脚）过滤——出现在 >25% 页面的短语视为排版样板，非术语
    pages = re.split(r"<<<PAGE \d+>>>", text)
    npage = max(1, len(pages))
    pagecnt = Counter()
    for pg in pages:
        low = set(re.findall(r"[A-Za-z][A-Za-z\-']{1,}", pg.lower()))
        for w in low:
            pagecnt[w] += 1
    boiler = {w for w, c in pagecnt.items() if npage >= 20 and c > 0.25 * npage}

    sents = re.split(r"(?<=[.;:!?])\s+|\n{2,}", text)
    freq = Counter()
    ctx = defaultdict(list)
    for sent in sents:
        toks = re.findall(r"[A-Za-z][A-Za-z\-']{1,}", sent)
        low = [t.lower() for t in toks]
        for n in range(min_words, max_n + 1):
            for i in range(len(low) - n + 1):
                g = low[i:i + n]
                if g[0] in EN_STOP or g[-1] in EN_STOP:
                    continue
                if all(w in EN_STOP for w in g):
                    continue
                if any(w in boiler for w in g):        # 样板词参与即丢
                    continue
                if any(w in NOISE for w in g):         # 程序词/单位参与即丢
                    continue
                if any(len(w) < 3 or w.endswith("-") for w in g):   # 碎片防护（如 e-）
                    continue
                if any("-" in w and len(w) <= 4 for w in g):       # 公式变量碎片（c-t / c-b）
                    continue
                if max(len(w) for w in g) < 5:                     # 全为短词 → 非术语
                    continue
                phrase = " ".join(g)
                if n == 1 and len(phrase) < 4:
                    continue
                freq[phrase] += 1
                if len(ctx[phrase]) < 2:
                    ctx[phrase].append(re.sub(r"\s+", " ", sent)[:120])
    cand = [(p, c) for p, c in freq.items() if c >= min_freq]
    cand.sort(key=lambda x: (-(x[1] * (1 + 0.5 * len(x[0].split()))), x[0]))
    return cand[:top], ctx


def extract_zh(text, min_freq=3, top=300, min_len=2, max_len=6):
    """ZH 候选：连续汉字 n-gram，去含停用字的串、去被更长高频串包含的子串"""
    freq = Counter()
    ctx = defaultdict(list)
    for seg in re.findall(r"[\u4e00-\u9fff]+", text):
        for n in range(min_len, max_len + 1):
            for i in range(len(seg) - n + 1):
                g = seg[i:i + n]
                if any(ch in ZH_STOP for ch in g):
                    continue
                freq[g] += 1
    cand = [(p, c) for p, c in freq.items() if c >= min_freq]
    cand.sort(key=lambda x: (-(x[1] * len(x[0])), x[0]))
    # 去子串：若某串被更长且频次相近的串包含，则丢短串
    keep = []
    for p, c in cand:
        if any(p != q and p in q and rc >= c * 0.6 for q, rc in cand[:top]):
            continue
        keep.append((p, c))
        if len(keep) >= top:
            break
    return keep, ctx


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="译前术语提取与锁定（CAT 三段式 ① 执行器）")
    ap.add_argument("source", nargs="?", help="源文档（txt/md）或 --from-list 的候选表")
    ap.add_argument("--from-list", action="store_true", help="把 source 当作手工候选表（每行一词/一短语）")
    ap.add_argument("--lang", default="en", choices=("en", "zh"), help="源语言（默认 en）")
    ap.add_argument("-n", "--top", type=int, default=400, help="**锁定表**上限（注入 spec 的量，宜少而准）")
    ap.add_argument("--max-gaps", type=int, default=3000,
                    help="**缺口清单**上限（核对清单，按频次排序完整输出；勿按排名截断，否则低频领域词被挤掉）")
    ap.add_argument("--min-freq", type=int, default=3, help="最低频次")
    ap.add_argument("--min-words", type=int, default=2,
                    help="候选最少词数（默认 2：多词术语才是锁定重点；设 1 则纳入单词，噪声显著上升）")
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--tb", default=TB_DIR, help="术语库目录")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest(a.tb)

    alias_map, rows = load_library(a.tb)
    idx = build_index(alias_map)
    assert alias_map, "术语库为空，检查 --tb 路径"
    print("术语库：%d 行 / %d 个别名" % (len(rows), len(alias_map)))

    text = io.open(a.source, encoding="utf-8", errors="replace").read()
    if a.from_list:
        cands = [(ln.strip(), 1) for ln in text.splitlines() if ln.strip() and not ln.startswith("#")]
        ctx = {}
        print("模式：手工候选表（%d 条）" % len(cands))
    elif a.lang == "en":
        cands, ctx = extract_en(text, a.min_freq, 10 ** 9, min_words=a.min_words)
        print("模式：EN 程序化提取（源 %d 字 → 候选 %d，min_words=%d）" % (len(text), len(cands), a.min_words))
    else:
        cands, ctx = extract_zh(text, a.min_freq, 10 ** 9)
        print("模式：ZH 程序化提取（源 %d 字 → 候选 %d）" % (len(text), len(cands)))

    locked, gaps = [], []
    for phrase, c in cands:
        kind, hit = lookup(phrase, alias_map, rows, idx)
        if hit:
            locked.append((phrase, hit[1], hit[0], hit[2], c, kind))
        else:
            gaps.append((phrase, c, (ctx.get(phrase) or [""])[0]))
    locked_all, gaps_all = len(locked), len(gaps)
    locked = locked[:a.top]            # 锁定表按"注入价值"截断
    gaps = gaps[:a.max_gaps]           # 缺口按频次完整输出（不按排名截断）

    outdir = a.outdir or os.path.dirname(os.path.abspath(a.source)) or "."
    os.makedirs(outdir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(a.source))[0]
    lp = os.path.join(outdir, stem + "_locked.md")
    gp = os.path.join(outdir, stem + "_gaps.md")

    with io.open(lp, "w", encoding="utf-8", newline="\n") as f:
        f.write("# 锁定术语表（译前提取命中，直接注入 spec）\n\n")
        f.write("> 生成：extract_terms.py ｜ 命中 %d 条 ｜ **本表即 spec 的术语节来源，勿手工另编**\n\n" % len(locked))
        f.write("| EN | 推荐 ZH | 拒用❌ | 语境/辨析 | 来源 | 日期 |\n|----|---------|--------|-----------|------|------|\n")
        for phrase, zh, en, src, c, kind in sorted(locked, key=lambda x: -x[4]):
            f.write("| %s | %s | — | 源文出现 %d 次；库内条目「%s」 | %s | auto |\n"
                    % (phrase, zh, c, en, src or "—"))
    with io.open(gp, "w", encoding="utf-8", newline="\n") as f:
        f.write("# 术语缺口清单（四库未覆盖，**逐条判定后再决定去留**）\n\n")
        f.write("> 生成：extract_terms.py ｜ 缺口 %d 条 ｜ 判定规则见下\n\n" % len(gaps))
        f.write("**处置规则**：① 领域专有词（有争议/易错）→ 必须权威源核验后入库；"
                "② 通用词（流体力学/气象学/数学）→ 译法无争议，可直接采用；"
                "③ 噪声（句子片段/非术语）→ 剔除。**勿整表直接入库。**\n\n")
        f.write("| 候选 | 频次 | 上下文样例 | 判定 |\n|------|------|-----------|------|\n")
        for phrase, c, sample in sorted(gaps, key=lambda x: -x[1]):
            f.write("| %s | %d | %s | ☐ |\n" % (phrase, c, sample.replace("|", "/")[:100]))
    json.dump({"locked": [{"term": p, "zh": z, "lib_en": e, "src": s, "freq": c, "match": k}
                          for p, z, e, s, c, k in locked],
               "gaps": [{"term": p, "freq": c, "sample": s} for p, c, s in gaps]},
              io.open(os.path.join(outdir, stem + "_terms.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    print("命中锁定 %d 条（输出 %d）→ %s" % (locked_all, len(locked), lp))
    print("缺口     %d 条（输出 %d）→ %s" % (gaps_all, len(gaps), gp))
    print("\n缺口 Top15：")
    for p, c, _ in sorted(gaps, key=lambda x: -x[1])[:15]:
        print("   %-38s ×%d" % (p[:38], c))
    if not gaps:
        print("\n⚠️ 缺口为 0 —— 请确认源文档非空且术语确有覆盖（防空转假 PASS）")


def selftest(tb):
    """自证三件套：正向（真实库命中） + 非空断言 + SABOTAGE（伪造词必须落缺口）"""
    alias_map, rows = load_library(tb)
    idx = build_index(alias_map)
    ok = True
    # ① 非空断言
    if not rows or len(rows) < 500:
        print("FAIL 非空断言：库行数 %d" % len(rows)); ok = False
    else:
        print("PASS 非空断言：库 %d 行 / %d 别名" % (len(rows), len(alias_map)))
    # ② 正向控制：真实存在的库词条必须判为命中
    hits = [t for t in ("reactor", "storage tank", "check valve", "probit", "rainout") if lookup(t, alias_map, rows, idx)[0]]
    if len(hits) >= 4:
        print("PASS 正向控制：%s 判为命中" % hits)
    else:
        print("FAIL 正向控制：仅命中 %s" % hits); ok = False
    # ③ 负控（SABOTAGE）：伪造词必须落缺口
    fake = "zzqx nonexistentterm qwertyuiop"
    if lookup(fake, alias_map, rows, idx)[0] is None:
        print("PASS 负控：伪造词正确落缺口")
    else:
        print("FAIL 负控：伪造词被误判命中"); ok = False
    print("\nVERDICT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main() or 0)
