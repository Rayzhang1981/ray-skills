#!/usr/bin/env python3
"""工程单位换算器 — 化工/过程工程常用单位换算 CLI 工具."""

import sys

# =============================================================================
# 基础换算因子：所有单位先换算到 base 单位，再从 base 换算到目标单位
# =============================================================================

CONVERSIONS = {
    "pressure": {
        "base": "Pa",
        "factors": {
            "Pa": 1.0,
            "kPa": 1000.0,
            "MPa": 1_000_000.0,
            "bar": 100_000.0,
            "atm": 101_325.0,
            "psi": 6894.76,
            "mmHg": 133.322,
            "mmH2O": 9.80665,
        },
    },
    "flow_rate": {
        "base": "m3/s",
        "factors": {
            "m3/h": 1.0 / 3600.0,
            "L/s": 0.001,
            "L/min": 0.001 / 60.0,
            "GPM": 0.00378541 / 60.0,
            "CFM": 0.0283168 / 60.0,
        },
    },
    "length": {
        "base": "m",
        "factors": {
            "mm": 0.001,
            "cm": 0.01,
            "m": 1.0,
            "km": 1000.0,
            "in": 0.0254,
            "ft": 0.3048,
        },
    },
    "mass": {
        "base": "kg",
        "factors": {
            "g": 0.001,
            "kg": 1.0,
            "t": 1000.0,
            "lb": 0.453592,
        },
    },
    "energy": {
        "base": "J",
        "factors": {
            "J": 1.0,
            "kJ": 1000.0,
            "kcal": 4184.0,
            "BTU": 1055.06,
            "kWh": 3_600_000.0,
        },
    },
    "viscosity_dynamic": {
        "base": "Pa·s",
        "factors": {
            "cP": 0.001,
            "Pa·s": 1.0,
        },
    },
    "density": {
        "base": "kg/m3",
        "factors": {
            "kg/m3": 1.0,
            "g/cm3": 1000.0,
            "lb/ft3": 16.0185,
        },
    },
    "htc": {
        "base": "W/m2K",
        "factors": {
            "W/m2K": 1.0,
            "kcal/h·m2·C": 1.163,
            "BTU/h·ft2·F": 5.67826,
        },
    },
}

CATEGORY_LABELS = {
    "pressure": "压力",
    "flow_rate": "流量",
    "temperature": "温度",
    "length": "长度",
    "mass": "质量",
    "energy": "能量",
    "viscosity_dynamic": "动力粘度",
    "density": "密度",
    "htc": "传热系数",
}

# =============================================================================
# 温度换算（非线性公式，非线性因子）
# =============================================================================


def _temp_c_to_k(c: float) -> float:
    return c + 273.15


def _temp_c_to_f(c: float) -> float:
    return c * 9.0 / 5.0 + 32.0


def _temp_k_to_c(k: float) -> float:
    return k - 273.15


def _temp_f_to_c(f: float) -> float:
    return (f - 32.0) * 5.0 / 9.0


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:
    """温度单位转换 (C ↔ F ↔ K)."""
    if from_unit == to_unit:
        return value

    # 统一先转成 Celsius
    if from_unit == "C":
        c = value
    elif from_unit == "K":
        c = _temp_k_to_c(value)
    elif from_unit == "F":
        c = _temp_f_to_c(value)
    else:
        raise ValueError(f"不支持的温度单位: {from_unit}")

    # 再从 Celsius 转到目标
    if to_unit == "C":
        return c
    elif to_unit == "K":
        return _temp_c_to_k(c)
    elif to_unit == "F":
        return _temp_c_to_f(c)
    else:
        raise ValueError(f"不支持的温度单位: {to_unit}")


# =============================================================================
# 类别检测 & 换算
# =============================================================================


def find_category(unit: str) -> str | None:
    """扫描所有类别，找到包含该单位的类别名。"""
    # 温度不走 CONVERSIONS dict
    if unit in ("C", "F", "K"):
        return "temperature"
    for cat, info in CONVERSIONS.items():
        if unit in info["factors"]:
            return cat
    return None


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """执行单位换算，自动检测类别。"""
    cat = find_category(from_unit)
    if cat is None:
        raise ValueError(f"未知单位: {from_unit}")
    if find_category(to_unit) != cat:
        raise ValueError(
            f"单位 '{from_unit}' ({CATEGORY_LABELS.get(cat, cat)}) "
            f"与 '{to_unit}' ({CATEGORY_LABELS.get(find_category(to_unit), '未知')}) 不属同一类别，无法换算"
        )

    # 温度单独处理
    if cat == "temperature":
        return convert_temperature(value, from_unit, to_unit)

    # 线性单位
    info = CONVERSIONS[cat]
    base_value = value * info["factors"][from_unit]  # → base
    return base_value / info["factors"][to_unit]  # base → target


# =============================================================================
# CLI
# =============================================================================


def print_list() -> None:
    """打印所有支持的类别及单位。"""
    print("支持的换算类别及单位:")
    print("-" * 56)
    for cat, info in CONVERSIONS.items():
        label = CATEGORY_LABELS.get(cat, cat)
        units = ", ".join(info["factors"].keys())
        print(f"  [{label}] {units}")
    # 温度单独列出
    print(f"  [{CATEGORY_LABELS['temperature']}] C, F, K")
    print("-" * 56)
    print("用法: python convert.py <数值> <原单位> <目标单位>")
    print("示例: python convert.py 100 kPa bar")


def main() -> None:
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print("工程单位换算器 (Engineering Unit Converter)")
        print()
        print("用法: python convert.py <数值> <原单位> <目标单位>")
        print("      python convert.py --list")
        print()
        print("示例:")
        print("  python convert.py 100 kPa bar")
        print("  python convert.py 25 C F")
        print("  python convert.py 50 L/s GPM")
        print("  python convert.py 5000 W/m2K BTU/h·ft2·F")
        return

    if "--list" in args or "-l" in args:
        print_list()
        return

    if len(args) != 3:
        print("错误: 需要 3 个参数: <数值> <原单位> <目标单位>", file=sys.stderr)
        print("运行 python convert.py --help 查看帮助", file=sys.stderr)
        sys.exit(1)

    value_str, from_unit, to_unit = args

    try:
        value = float(value_str)
    except ValueError:
        print(f"错误: 无法将 '{value_str}' 解析为数值", file=sys.stderr)
        sys.exit(1)

    try:
        result = convert(value, from_unit, to_unit)
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    # 输出格式: 保留合适的小数位数
    # 若结果接近整数则显示整数，否则保留最多 6 位有效数字
    if abs(result) >= 1e6 or (abs(result) < 1e-4 and result != 0):
        print(f"{value} {from_unit} = {result:.6e} {to_unit}")
    elif abs(result - round(result)) < 1e-10:
        print(f"{value} {from_unit} = {int(round(result))} {to_unit}")
    else:
        formatted = f"{result:.6g}"
        print(f"{value} {from_unit} = {formatted} {to_unit}")


if __name__ == "__main__":
    main()
