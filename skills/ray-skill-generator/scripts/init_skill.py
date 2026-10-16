#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ray-skill-generator — Skill 脚手架生成器 v1.2

用法:
  python init_skill.py <skill-name> [--type workflow] [--path <目录>]

生成（v1.2 起自带「经验回流口」——新建 skill 一律必带，不做筛选）:
  <skill-name>/
  ├── SKILL.md                       # 模板（TODO 占位 + Definition of Done + Gotchas 合并回流口）
  ├── scripts/                       # 空目录 + .gitkeep
  ├── references/
  │   ├── experience-archive.md      # 回流口归档件（配合容量熔断）
  │   └── .gitkeep
  ├── evals/
  │   ├── prompts.md                 # 触发用例套件（Phase 3 的 3+3 落盘处）
  │   └── .gitkeep
  └── assets/                        # 空目录 + .gitkeep

⚠️ 改本节头规范原文（REFLOW_STUB）时，必须同步回填工具
   （会话过程件 backfill_gotchas.py），否则新旧 skill 的口径会分叉。
   一致性可用一条断言核验：全库各 skill 的 `## Gotchas` 节头必须含同一份规范原文。
"""
import os
import re
import sys
import argparse
from datetime import date

def _console_safe():
    """控制台编码护栏（2026-10-09 舰队级修复）。

    中文 Windows 下 stdout/stderr 走 cp936(GBK)。**输出被重定向或经管道捕获时**
    （自动验证 / 日志 / CI / subprocess PIPE），Python 按 locale 编码写流，
    遇到 GBK 无法表示的字符即抛 UnicodeEncodeError，**整段输出中断**；
    而交互式控制台走 WriteConsoleW(UTF-16)，同一字符却无碍
    => 该缺陷只在「捕获输出」时显形，最易漏测。

    处理：**保持流原编码不变**（中文在 GBK 控制台仍正常），
    仅把不可表示的字符降级为 '?'，从而永不中断。
    注意：不要改成 encoding="utf-8" —— 那会让 GBK 控制台下的中文变乱码。
    """
    for _s in (sys.stdout, sys.stderr):
        try:
            _s.reconfigure(errors="replace")
        except Exception:
            pass


_console_safe()


SKILLS_DIR = os.path.expanduser("~/.workbuddy/skills")

TYPES = ["tool", "workflow", "capability", "scenario"]

# —— 经验回流口规范原文（canonical stub）——
# 这两行必须与既有 skill 的口逐字一致；改这里 = 改全生态口径，须回填存量。
REFLOW_STUB = (
    "> 新回流条目带前缀：`- YYYY-MM-DD｜[LRN-YYYYMMDD-XXX]｜计数:N｜状态:…`（判重与归档用）；历史条目保持原样。\n"
    "> 归档阈值：本节 > 40 行 或 SKILL.md > 90 KB → 最旧批次移入 `references/experience-archive.md`，保留最近 3 轮。"
)

GOTCHAS_SECTION = """## Gotchas

> 经验回流口（合并原「环境怪癖」与「实战经验」两处落点）。构建与运行中踩的坑记这里，随运行累积。
> ⚠️ `None known` 是合法值——禁止编造 gotcha 凑数，假怪癖会教模型错误约束。
{stub}

- None known
""".format(stub=REFLOW_STUB)

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

{gotchas}
## 参考资料

- `references/` — TODO: 按需加载的文档（schema/规范/清单）
- `references/experience-archive.md` — 回流口归档件（配合容量熔断，超阈时把最旧批次移入）

## Definition of Done

- [ ] TODO: 可测量的完成标准（如"健康分 ≥B"、"≥3 个示例 prompt"、"核心脚本跑通"）
- [ ] frontmatter 含 name/description/version
- [ ] 触发双向验证：3 个 should-trigger + 3 个 near-miss 反例，**并已落盘到 `evals/prompts.md`**
- [ ] `evals_runner.py --bless` 已跑，本 skill 已在回归门禁网内

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

ARCHIVE_MD = """# 经验归档 — {name}

> 本文件是 `{name}` 的 `## Gotchas` 节**归档件**：按批次存放已移出正文的历史条目。
> 触发归档：`## Gotchas` 节 > 40 行，或 SKILL.md > 90 KB。归档时保留最近 3 轮在主文件。
> 条目格式：`- YYYY-MM-DD｜[LRN-YYYYMMDD-XXX]｜计数:N｜状态:…｜<正文>`

（暂无归档批次）
"""

EVALS_MD = """# 触发用例套件 — {name}

> 用途：`description` 的**回归用例**。每次优化 description 后重跑本套件，确认路由未退化。
> 来源：Phase 3「触发双向验证」的 3 should-trigger + 3 near-miss——**写完即落盘，勿留在会话里**。
> 判据：should-trigger 全部命中本 skill；near-miss 全部**不**命中本 skill、且命中注明的相邻 skill。

## should-trigger（应命中本 skill）

| # | 用户会说 | 预期 |
|---|---------|------|
| 1 | TODO | 命中本 skill |
| 2 | TODO | 命中本 skill |
| 3 | TODO | 命中本 skill |

## near-miss（不应命中本 skill，关键词相似）

| # | 用户会说 | 预期 |
|---|---------|------|
| 1 | TODO | 不命中本 skill → 命中 TODO（相邻 skill） |
| 2 | TODO | 不命中本 skill → 命中 TODO（相邻 skill） |
| 3 | TODO | 不命中本 skill → 命中 TODO（相邻 skill） |
"""


def validate_name(name: str) -> str:
    """校验并规范 skill 名：小写连字符"""
    name = name.strip().lower()
    name = re.sub(r"[^a-z0-9-]+", "-", name)
    name = re.sub(r"-+", "-", name).strip("-")
    if not name:
        print("[X] skill 名无效（只能含小写字母/数字/连字符）")
        sys.exit(1)
    return name


def write_file(path: str, content: str) -> None:
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


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
        print(f"[!] {dest} 已存在，跳过（如需重建请先删除）")
        sys.exit(1)

    # 目录骨架
    os.makedirs(dest)
    for sub in ["scripts", "references", "evals", "assets"]:
        subdir = os.path.join(dest, sub)
        os.makedirs(subdir)
        open(os.path.join(subdir, ".gitkeep"), "w").close()

    # SKILL.md
    display_name = name.replace("-", " ").title()
    write_file(
        os.path.join(dest, "SKILL.md"),
        TEMPLATE.format(
            name=name,
            display_name=display_name,
            type_section=TYPE_SECTIONS[skill_type],
            gotchas=GOTCHAS_SECTION,
            today=date.today().isoformat(),
        ),
    )

    # 回流口配套两件（v1.2 新增）
    write_file(os.path.join(dest, "references", "experience-archive.md"), ARCHIVE_MD.format(name=name))
    write_file(os.path.join(dest, "evals", "prompts.md"), EVALS_MD.format(name=name))

    print(f"[OK] 已生成 {name}（类型: {skill_type}）")
    print(f"   位置: {dest}")
    print(f"   结构: SKILL.md + scripts/ + references/(含回流归档件) + evals/(触发用例) + assets/")
    print(f"\n下一步:")
    print(f"   1. 编辑 SKILL.md 填 TODO 占位（Gotchas 槽位已就位，无需另建）")
    print(f"   2. 验证: python ~/.workbuddy/skills/ray-skill-evolve/scripts/health_check.py {dest}")
    print(f"   3. 接进回归门禁: python ~/.workbuddy/scripts/evals_runner.py --bless")
    print(f"      [!] 全库 bless；库内若有「待确认的既有漂移」，先逐项确认再跑，否则会把漂移一并追认为正常")


if __name__ == "__main__":
    main()
