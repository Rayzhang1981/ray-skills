# Ray Skills — 化工 / 过程安全 AI Skill 集（WorkBuddy）

> **Rayzhang1981 原创** · 过程安全工程师视角 · 化工 + 过程安全 + 工具链

> 🌐 **English version:** [README_EN.md](README_EN.md)

本仓库是 Ray 系列 WorkBuddy Skills 的**源仓库（Source）**，与 [SkillHub](https://skillhub.cn) 分发市场构成双轨：

| 轨道 | 角色 | 链接 |
|------|------|------|
| **GitHub（本仓库）** | 源码 + 版本演变历史 + Issue/PR 协作 | `github.com/Rayzhang1981/ray-skills` |
| **SkillHub** | 一键安装 + 更新 + 审核背书 | [Ray 的技能页](https://skillhub.cn/skills/user_fb8bdb79) |

两个轨道互相导流：SkillHub 简介指向本仓库源码，本 README 指向 SkillHub 安装。

---

## 在架技能（SkillHub 已发布 · 21 个）

✅ = 源码已在本仓库 `skills/`；⏳ = 版权/隐私原因，源码不公开（SkillHub 版不受影响）

| 技能 | 版本 | 一句话 | 源码 | SkillHub |
|------|------|--------|:---:|----------|
| ray-excel-html | 2.2.0 | Excel/工程计算表 → 单文件 HTML 计算工具（离线可用） | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-excel-html) |
| ray-pe-calc | 2.2.0 | 七大工艺计算模块工具箱 + 计算书输出 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-pe-calc) |
| ray-html-miniprogram | 1.2.0 | 化工计算 HTML → 微信小程序模块 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-html-miniprogram) |
| ray-ps-inforgraphic | 2.2.0 | 化工安全主题信息图生成器 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-ps-inforgraphic) |
| ray-skill-generator | 1.12.0 | 从零创建 Skill 的元工具 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-skill-generator) |
| ray-file-distil | 1.13.0 | 书籍/长文档蒸馏为 Skill 的元工具 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-file-distil) |
| ray-data-analysis | 1.2.0 | 完整数据分析工作流 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-data-analysis) |
| ray-ppt-generator | 3.19.0 | python-pptx 快速生成可编辑 PPTX | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-ppt-generator) |
| ray-ppt-refine | 2.5.0 | 已有 PPTX 排版美化与合规验收 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-ppt-refine) |
| ray-ppt-video | 2.7.0 | PPTX → 配音培训视频（FFmpeg） | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-ppt-video) |
| ray-deep-research | 1.3.2 | 溯源对比法深度研究对象 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-deep-research) |
| ray-synth-search | 1.7.1 | 多源检索 + 交叉验证的日常搜索主力 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-synth-search) |
| ray-standard-search | 3.0.1 | 化工标准与法规快查（IMA 为可选源） | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-standard-search) |
| ray-pse-sharing | 1.13.0 | 事故报告 → 一页 A4 分享卡 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-pse-sharing) |
| ray-pse-video | 2.4.0 | 事故报告 → 安全培训视频 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-pse-video) |
| ray-self-reflection | 3.15.0 | 自我反思 · 经验萃取 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-self-reflection) |
| ray-translate | 3.3.3 | 化工安全文档中英双向翻译 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-translate) |
| ray-hazop-lopa | 1.3.1 | HAZOP/LOPA 定量分析报告生成器 | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-hazop-lopa) |
| ray-chem-property | 3.5.0 | 化学品物性数据批量搜集（索引库随 SkillHub 版分发） | ✅* | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-chem-property) |
| ray-household-finance | 2.4.1 | 家庭财务管理框架（示例为虚构数据） | ✅ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-household-finance) |
| ray-rca | 1.1.0 | 事故根本原因分析（RCA）端到端 | ⏳ | [安装](https://skillhub.cn/skills/user_fb8bdb79/ray-rca) |

> \* ray-chem-property 开源版含脚本与流程，完整物性索引库（授权数据）仅随 SkillHub 版分发。
> ⏳ ray-rca 融合第三方专有方法（ABS SOURCE™），源码不公开。
> 另有 30+ 技能（CCPS 方法论认知层 17 个等）仅在私有环境分发，未公开源码。

---

## 本地安装（不经 SkillHub）

```bash
git clone https://github.com/Rayzhang1981/ray-skills.git
# 把需要的技能复制到 WorkBuddy 技能目录
cp -r ray-skills/skills/<name> ~/.workbuddy/skills/
# 重启会话后生效
```

## 目录结构

```
ray-skills/
├── skills/                 # 已开源技能（一个目录一个，SKILL.md + scripts + references）
├── scripts/sync_from_local.sh   # 从 ~/.workbuddy/skills 一键同步本仓库（白名单=skills/ 现有目录）
├── README.md / README_EN.md   # 双轨索引（中文 / English）
├── AGENTS.md               # 给 AI 协作者的结构说明
└── LICENSE                 # MIT
```

## 同步策略

`skills/<name>/` 是本地 `~/.workbuddy/skills/<name>` 当前版的**发布镜像**（只收录通过分层评估的技能）。
日常更新：改本地 → SkillHub 发布 → `bash scripts/sync_from_local.sh` 同步仓库 → push。

> sync 脚本自动排除：`data/`（如 chem-property 授权索引库）、`anchor_db.json`（pse-sharing 本地锚点库）、运行时产物。

## 贡献

欢迎 Issue 报 bug、PR 改进、Discussions 交流。涉及工艺安全内容的修改请附依据（标准号/指南出处）。

## License

[MIT](LICENSE) © 2026 Rayzhang（张瑞超）
