#!/usr/bin/env python3
"""
ray-translate 核心翻译脚本模板
适合化工/过程安全 Excel 工作簿 (.xlsm/.xlsx) 的英译中批量翻译
策略：分批加载/处理/保存，避免内存溢出
"""
import os
import re
import shutil
import openpyxl
import sys
import time

# ============================================================
# 1. 术语字典 — 按需增删，保持"长串在前"排序规则
#    每对 "English Phrase": "中文翻译"
# ============================================================
RAW_TERMS = {
    # === 工作表名 ===
    "Sheet1": "工作表1",
    "Sheet2": "工作表2",

    # === 核心标题 ===
    "Version": "版本",
    "Disclaimer": "免责声明",
    "Copyright": "版权所有",
    "Revision Date": "修订日期",

    # === 通用 UI 元素 ===
    "Print": "打印",
    "Save": "保存",
    "Close": "关闭",
    "Next": "下一页",
    "Previous": "上一页",
    "Back": "返回",
    "Return": "返回",
    "Top": "顶部",
    "Input": "输入",
    "Output": "输出",
    "Unit": "单位",
    "Value": "值",
    "Name": "名称",
    "Description": "描述",
    "Note": "备注",
    "Notes": "备注",
    "Reference": "参考",
    "References": "参考文献",
    "Example": "示例",
    "Result": "结果",
    "Equation": "方程",
    "Table": "表",
    "Figure": "图",

    # === 化工安全通用术语 ===
    "Chemical": "化学品",
    "Chemical Name": "化学品名称",
    "CAS Number": "CAS 号",
    "Molecular Weight": "分子量",
    "Mol Weight": "分子量",
    "Boiling Point": "沸点",
    "Melting Point": "熔点",
    "Flash Point": "闪点",
    "Autoignition Temperature": "自燃温度",
    "Vapor Pressure": "蒸气压",
    "Temperature": "温度",
    "Pressure": "压力",
    "Volume": "体积",
    "Mass": "质量",
    "Flow Rate": "流量",
    "Volumetric Flow": "体积流量",
    "Mass Flow": "质量流量",
    "Density": "密度",
    "Vapor Density": "蒸气密度",
    "Liquid Density": "液体密度",
    "Heat Capacity": "热容",
    "Viscosity": "粘度",
    "Thermal Conductivity": "导热系数",
    "Concentration": "浓度",
    "Reaction": "反应",
    "Reaction Rate": "反应速率",
    "Heat of Reaction": "反应热",
    "Activation Energy": "活化能",
    "Yield": "收率",
    "Conversion": "转化率",
    "Selectivity": "选择性",

    # === 安全与风险 ===
    "Hazard": "危害",
    "Risk": "风险",
    "Consequence": "后果",
    "Probability": "概率",
    "Frequency": "频率",
    "Scenario": "场景",
    "Initiating Event": "初始事件",
    "Loss Event": "损失事件",
    "Failure": "故障",
    "Failure Rate": "故障率",
    "Exposure": "暴露",
    "Release": "释放",
    "Leak": "泄漏",
    "Rupture": "破裂",
    "Explosion": "爆炸",
    "Fire": "火灾",
    "Flash Fire": "闪火",
    "Jet Fire": "喷射火",
    "Pool Fire": "池火",
    "Fireball": "火球",
    "BLEVE": "BLEVE",
    "Vapor Cloud Explosion": "蒸气云爆炸",
    "Dust Explosion": "粉尘爆炸",
    "Mitigation": "缓解",
    "Safeguard": "安全措施",
    "Protection Layer": "保护层",
    "LOPA": "LOPA",
    "HAZOP": "HAZOP",
    "What-If": "假设分析",
    "Checklist": "检查表",
    "FMEA": "FMEA",
    "Fault Tree": "故障树",
    "Event Tree": "事件树",

    # === 设备 ===
    "Vessel": "容器",
    "Tank": "储罐",
    "Reactor": "反应器",
    "Column": "塔",
    "Heat Exchanger": "换热器",
    "Pump": "泵",
    "Compressor": "压缩机",
    "Valve": "阀门",
    "Pipe": "管道",
    "Piping": "管道",
    "Nozzle": "管嘴",
    "Flange": "法兰",
    "Gasket": "垫片",
    "Instrument": "仪表",
    "Sensor": "传感器",
    "Controller": "控制器",
    "Actuator": "执行机构",

    # === 单位缩写（保留英文形式但保持显示一致性） ===
    "kg/m3": "kg/m³",
    "kg/m^3": "kg/m³",
    "m3": "m³",
    "m^3": "m³",
    "g/cc": "g/cm³",
    "cal/g-C": "cal/(g·°C)",
    "cal/g": "cal/g",
    "g/mol": "g/mol",
    "kPa": "kPa",
    "ppm": "ppm",
    "vol": "体积",
    "wt": "质量",
}

# 提示：术语字典可扩展至 700-1500 条（按项目需要）
# 对于大型项目（如 CHEF 的 13 个 Sheet），参考以下分组：
# - 工作表名 (13)
# - 核心标题/版权 (20)
# - 通用 UI (30)
# - Section 目录 (50)
# - 各 Sheet 专业术语 (200-500)
# - 表单字段 (100-200)
# - 化学名列表 (200-400)
# - 中英混合长句 (50-100)


# ============================================================
# 2. 核心翻译引擎
# ============================================================

def make_patterns():
    """将术语字典转为排序后的 (正则模式, 中文) 列表"""
    items = sorted(RAW_TERMS.items(), key=lambda x: len(x[0]), reverse=True)
    return [(re.escape(eng), cn) for eng, cn in items]


def translate(val, patterns):
    """核心替换函数：正则整词匹配，跳过公式"""
    if not val or not isinstance(val, str) or val.startswith("="):
        return val
    result = val
    for pat, cn in patterns:
        result = re.sub(r'\b' + pat + r'\b', cn, result)
    return result


def translate_sheet(ws, patterns):
    """翻译单个 sheet 中所有文本 cell"""
    count = 0
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row, max_col=ws.max_column):
        for cell in row:
            if cell.value is None:
                continue
            val = cell.value
            if isinstance(val, str) and not val.startswith("="):
                if re.search(r'[a-zA-Z]{2,}', val):
                    translated = translate(val, patterns)
                    if translated != val:
                        cell.value = translated
                        count += 1
    return count


# ============================================================
# 3. 主流程
# ============================================================

def main():
    # === 配置区域（每次使用时修改） ===
    SHEETS = [
        "Sheet1",
        "Sheet2",
        # ... 按实际 Sheet 名填写
    ]

    SRC = r"path\to\source.xlsm"
    OUT = r"path\to\translated_CN.xlsm"
    BATCH_SIZE = 3
    # ==============================

    patterns = make_patterns()
    print(f"载入 {len(RAW_TERMS)} 条术语, {len(patterns)} 条正则模式")

    # 首次：复制源文件（含 VBA）到输出
    if os.path.exists(OUT):
        os.remove(OUT)
    shutil.copy2(SRC, OUT)
    print(f"已复制源文件到: {OUT}")

    total_translated = 0

    for i in range(0, len(SHEETS), BATCH_SIZE):
        batch = SHEETS[i:i + BATCH_SIZE]
        print(f"\n--- 批次 {i // BATCH_SIZE + 1}: {batch} ---")
        sys.stdout.flush()

        t0 = time.time()
        wb = openpyxl.load_workbook(OUT, keep_vba=True)
        for sname in batch:
            ws = wb[sname]
            n = translate_sheet(ws, patterns)
            total_translated += n
            print(f"  {sname}: 翻译 {n} 个 cell")
        wb.save(OUT)
        print(f"  保存完成 ({time.time() - t0:.1f}s)")

        # 小延迟让系统释放内存
        time.sleep(0.5)

    print(f"\n{'=' * 50}")
    print(f"总计翻译 cell: {total_translated}")
    print(f"输出文件: {OUT}")


if __name__ == "__main__":
    main()