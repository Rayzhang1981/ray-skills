"""CN2EN 桥有效性普查（2026-10-10 建，ch14 折叠轮教训固化）
判据：桥的落点必须是**主库精确化学品名**——"含该子串的行数"不算自证。
用法：python check_cn2en_bridges.py --data-root <腐蚀数据根>
退出码：有无效桥 = 1（fail-closed，供 CI/回归挂用）。
"""
import importlib.util, os, sys, argparse

SKILL = r"C:\Users\rayzh\.workbuddy\skills\ray-material-selection"
ENGINE = os.path.join(SKILL, "scripts", "evaluate_material.py")


def load_engine():
    spec = importlib.util.spec_from_file_location("em", ENGINE)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-root", required=True)
    a = ap.parse_args()
    m = load_engine()
    rows, path = m.load_alleima(a.data_root)
    if rows is None:
        print("[FAIL] 未找到 Alleima 主库 CSV：%s" % a.data_root)
        return 2
    exact = {r["化学品"].strip().lower() for r in rows}
    bad, ok = [], []
    for cn, en in m.CN2EN.items():
        (ok if en.strip().lower() in exact else bad).append((cn, en))
    print("CN2EN 词条 %d 条：有效 %d ／ 无效 %d" % (len(m.CN2EN), len(ok), len(bad)))
    for cn, en in ok:
        print("  [OK]   %s -> %s" % (cn, en))
    for cn, en in bad:
        # 附上"含该子串"的行数，指出假自证的来源
        sub = sum(1 for r in rows if en.lower() in r["化学品"].lower())
        print("  [BAD]  %s -> %s （主库无此独立化学品名；含该子串的组合行 %d 条 ← 假自证来源）"
              % (cn, en, sub))
    if bad:
        print("\n结论：**FAIL**——无效桥会让查询静默空转并把排查者引向错误方向（去补已存在的词条）。")
        return 1
    print("\n结论：PASS——全部桥的落点均为主库精确化学品名。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
