# AGENTS.md — 给 AI 协作者

本仓库是 WorkBuddy Skill 集合的**发布镜像仓库**，不是独立开发的代码库。

## 关键约束

1. **内容源在别处**：`skills/<name>/` 是本地 `~/.workbuddy/skills/<name>` 的发布快照。修改 Skill 本体请在本地技能目录进行（或开 Issue 讨论），**不要直接在本仓库内改技能逻辑**——下次同步会被覆盖。
2. **分层收录**：仓库只收录通过"分层评估"（✅ 公开组）的技能。缺失 ≠ 不存在：CCPS 方法论层、含版权数据（如 chem-property 的 CRC/Perry/兰氏索引）、含企业素材的技能**有意不收**。
3. **同步方式**：`bash scripts/sync_from_local.sh`（白名单 = `skills/` 现有目录，逐个从本地覆盖拷贝，排除 `__pycache__`/`*.pyc`）。
4. **提交纪律**：一次同步一个语义提交，信息格式 `sync: <技能名> vX.Y.Z（一句话变更）` 或 `repo: 结构变更说明`。

## 结构速查

- `skills/<name>/SKILL.md` — 技能入口（frontmatter: name/slug/displayName/version/description + agent_created）
- `skills/<name>/scripts|references/` — 脚本与参考
- `README.md` — 双轨索引（GitHub 源 ⇄ SkillHub 分发）
