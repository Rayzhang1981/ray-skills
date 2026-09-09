#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ray-skill-generator — Skill 脚手架生成器 v1.1

用法:
  python init_skill.py <skill-name> [--type workflow] [--path <目录>]

生成:
  <skill-name>/
  ├── SKILL.md           # 模板（含 TODO 占位 + Definition of Done + Gotchas）
  ├── scripts/           # 空目录 + .gitkeep
  ├── references/        # 空目录 + .gitkeep
  └── assets/            # 空目录 + .gitkeep
"""
import os
import re
import sys
import argparse
from datetime import date

SKILLS_DIR = os.path.expanduser("~/.workbuddy/skills")

TYPES = ["tool", "workflow", "capability", "scenario"]

TEMPLATE = """---
name: {name}
slug: {name}
displayName: {display_name}
version: 1.0.0
description: >
  TODO: 一句话说明这个 skill 做什么 + 何时用（触发词）。
  Use when the user says: "触发词1", "触发词2".
agent_created: true
---

# {display_name}

> TODO: 一句话定位。

## 目的

TODO: 这个 skill 解决什么问题？（几句话）

## 何时使用

TODO: 用户说什么话会触发这个 skill？列出具体触发词。

## 使用方式

TODO: 实际怎么用？引用所有 scripts/references/assets 资源。

{type_section}

## 参考资料

- `references/` — TODO: 按需加载的文档（schema/规范/清单）

## Definition of Done

- [ ] TODO: 可测量的完成标准（如"健康分 ≥B"、"≥3 个示例 prompt"、"核心脚本跑通"）
- [ ] frontmatter 含 name/description/version
- [ ] 触发双向验证：3 个 should-trigger + 3 个 near-miss 反例

## Gotchas

> 环境专属怪癖（ defy 合理假设的事实）。构建中踩的坑、验证时发现的行为都记这里，随运行累积。
> ⚠️ `None known` 是合法值——禁止编造 gotcha 凑数，假怪癖会教模型错误约束。

- None known

## 维护记录

> ⚠️ 脱敏提示：维护记录不列第三方 skill 名（写"对比外部 skill 吸收 N 项"）；不写个人隐私数据（真实金额/账号/基金名）。

| 日期 | 变更 |
|------|------|
| {today} | v1.0.0：初始创建 |
"""

TYPE_SECTIONS = {
    "tool": "## 输入/输出\n\nTODO: 明确输入格式、输出格式、参数说明。\n\n## 错误处理\n\nTODO: 成功/失败/异常三条路径。",
    "workflow": "## 执行步骤\n\nTODO: Step 1/2/3 顺序流程，关键决策点加 🔴 CHECKPOINT。\n\n## 失败分支\n\nTODO: 如果 X 失败 → Y（≥3 处）。",
    "capability": "## 领域规则\n\nTODO: 这个领域的核心规则、判断标准。\n\n## 何时不用\n\nTODO: 什么情况不适用这个 skill。",
    "scenario": "## 角色设定\n\nTODO: 扮演什么角色、行为准则。\n\n## 边界\n\nTODO: 什么不能做（红线）。",
}


def validate_name(name: str) -> str:
    """校验并规范 skill 名：小写连字符"""
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9-]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    if not name:
        print("❌ skill 名无效（只能含小写字母/数字/连字符）")
        sys.exit(1)
    return name


def main():
    parser = argparse.ArgumentParser(description="ray-skill-generator 脚手架生成器")
    parser.add_argument("name", help="skill 名称（小写连字符，如 my-skill）")
    parser.add_argument("--type", choices=TYPES, default="workflow", help="skill 类型（默认 workflow）")
    parser.add_argument("--path", default="", help="输出目录（默认 ~/.workbuddy/skills/）")
    args = parser.parse_args()

    name = validate_name(args.name)
    skill_type = args.type
    base = args.path if args.path else SKILLS_DIR
    dest = os.path.join(base, name)

    if os.path.exists(dest):
        print(f"⚠️ {dest} 已存在，跳过（如需重建请先删除）")
        sys.exit(1)

    # 创建目录
    os.makedirs(dest)
    for sub in ["scripts", "references", "assets"]:
        subdir = os.path.join(dest, sub)
        os.makedirs(subdir)
        # .gitkeep 占位
        open(os.path.join(subdir, ".gitkeep"), "w").close()

    # 生成 SKILL.md
    display_name = name.replace("-", " ").title()
    content = TEMPLATE.format(
        name=name,
        display_name=display_name,
        type_section=TYPE_SECTIONS[skill_type],
        today=date.today().isoformat(),
    )
    with open(os.path.join(dest, "SKILL.md"), "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ 已生成 {name}（类型: {skill_type}）")
    print(f"   位置: {dest}")
    print(f"   结构: SKILL.md + scripts/ + references/ + assets/")
    print(f"\n下一步:")
    print(f"   1. 编辑 SKILL.md 填 TODO 占位")
    print(f"   2. 验证: python ~/.workbuddy/skills/ray-skill-evolve/scripts/health_check.py {dest}")


if __name__ == "__main__":
    main()
