# Ray Skills — AI Skills for Chemical Engineering & Process Safety (WorkBuddy)

> **Original by Rayzhang1981** · Built from a process safety engineer's perspective · Chemical engineering + process safety + productivity tooling

This repository is the **source repo** of the Ray series of WorkBuddy Skills, running dual-track with the [SkillHub marketplace (my skill page)](https://skillhub.cn/skills/user_fb8bdb79):

| Track | Role | Link |
|-------|------|------|
| **GitHub (this repo)** | Source code + full version history + Issue/PR collaboration | `github.com/Rayzhang1981/ray-skills` |
| **SkillHub** | One-click install + updates + review endorsement | [Ray's skill page](https://skillhub.cn/skills/user_fb8bdb79) |

Each track feeds the other: SkillHub listings point back to this source repo, and this README points to SkillHub for installation.

> 🌐 **中文版:** [README_CN.md](README_CN.md)

---

## Skills on the marketplace (SkillHub · 21)

✅ = source code in this repo's `skills/`; ⏳ = source not public (copyright/privacy reasons; SkillHub version unaffected)

| Skill | Version | One-liner | Source | SkillHub |
|-------|---------|-----------|:---:|----------|
| ray-excel-html | 2.2.0 | Convert Excel/engineering calc sheets to standalone offline HTML tools | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-excel-html) |
| ray-pe-calc | 2.2.0 | 7-module process engineering calculator toolbox + calc reports | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-pe-calc) |
| ray-html-miniprogram | 1.2.0 | Turn chem-calc HTML tools into WeChat Mini Program modules | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-html-miniprogram) |
| ray-ps-inforgraphic | 2.2.0 | Chemical safety infographic generator | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-ps-inforgraphic) |
| ray-skill-generator | 1.12.0 | Meta tool to create WorkBuddy skills from scratch | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-skill-generator) |
| ray-file-distil | 1.13.0 | Distill books/long documents into atomic reusable skills | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-file-distil) |
| ray-data-analysis | 1.2.0 | Complete data analysis workflow (SQL → viz → dashboard → validation) | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-data-analysis) |
| ray-ppt-generator | 3.19.0 | Generate editable PPTX decks with python-pptx | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-ppt-generator) |
| ray-ppt-refine | 2.5.0 | PPTX layout beautification & compliance gate (edit-only, no content change) | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-ppt-refine) |
| ray-ppt-video | 2.7.0 | Turn training PPTX into narrated MP4 videos (TTS + hard subtitles) | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-ppt-video) |
| ray-deep-research | 1.3.2 | Deep research on a target via source-tracing & horizontal comparison | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-deep-research) |
| ray-synth-search | 1.7.1 | Daily multi-source search with cross-validation & confidence scoring | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-synth-search) |
| ray-standard-search | 3.0.1 | Chemical/process standards & regulations quick search (IMA optional) | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-standard-search) |
| ray-pse-sharing | 1.13.0 | Incident report → one-page A4 sharing card PDF | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-pse-sharing) |
| ray-pse-video | 2.4.0 | Incident report → narrated safety training video | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-pse-video) |
| ray-self-reflection | 3.15.0 | Self-reflection & experience distillation for AI agents | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-self-reflection) |
| ray-translate | 3.3.3 | CN↔EN translation for chemical safety documents | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-translate) |
| ray-hazop-lopa | 1.3.1 | HAZOP/LOPA quantitative report generator | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-hazop-lopa) |
| ray-chem-property | 3.5.0 | Batch chemical property data collection (111 fields; index DB via SkillHub) | ✅* | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-chem-property) |
| ray-household-finance | 2.4.1 | Household finance management framework (examples are fictional) | ✅ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-household-finance) |
| ray-rca | 1.1.0 | Root cause analysis end-to-end | ⏳ | [Install](https://skillhub.cn/skills/user_fb8bdb79/ray-rca) |

> \* ray-chem-property open-source edition includes scripts & workflow; the full property index database (licensed data) ships only with the SkillHub edition.
> ⏳ ray-rca integrates third-party proprietary methodology (ABS SOURCE™), source code is not public.
> 30+ more skills (e.g. 17 CCPS methodology cognition skills) are distributed privately only.

---

## Local installation (without SkillHub)

```bash
git clone https://github.com/Rayzhang1981/ray-skills.git
# Copy the skill(s) you need into the WorkBuddy skills directory
cp -r ray-skills/skills/<name> ~/.workbuddy/skills/
# Restart the session to take effect
```

## Repository layout

```
ray-skills/
├── skills/                 # Open-source skills (one dir each: SKILL.md + scripts + references)
├── scripts/sync_from_local.sh   # One-click mirror from ~/.workbuddy/skills (whitelist = dirs in skills/)
├── README.md / README_CN.md     # Dual-track index (EN / 中文)
├── AGENTS.md               # Structure notes for AI collaborators
└── LICENSE                 # MIT
```

## Sync policy

`skills/<name>/` is a **publish mirror** of the current local `~/.workbuddy/skills/<name>` (only skills passing the open-source review are included).
Daily workflow: edit locally → publish to SkillHub → `bash scripts/sync_from_local.sh` → push.

> The sync script automatically excludes `data/` (e.g. chem-property's licensed index DB), `anchor_db.json` (pse-sharing local anchor DB), runtime artifacts — and post-processes local paths into placeholders so sanitized versions survive future syncs.

## Contributing

Issues for bugs, PRs for improvements, Discussions for ideas. For process-safety-related changes, please cite your basis (standard number / guideline source).

## License

[MIT](LICENSE) © 2026 Rayzhang (张瑞超)
