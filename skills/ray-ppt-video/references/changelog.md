# ray-ppt-video 维护记录

> 从 SKILL.md 卸载（2026-09-02），遵守"维护记录不常驻正文"原则。按需加载。

| 日期 | 变更 |
|------|------|
| 2026-09-04 | v2.7.0：①**时长确认铁律**（用户明确要求）——估算时长→报告→用户确认后才 TTS；确认后时长冻结，禁止为凑整数自动改 --rate 重跑（实证：18.85 vs 20 分钟，未确认重跑致音频混合损坏→全量重做）；②字幕默认字号 24→**32**（用户截图反馈 24 偏小；assemble_video.py 两处默认值 + 编码参数表同步）；③实战经验 ERR-20260904-001 |
| 2026-09-03 | v2.6.1：tts_srt_en.py 增加 `--rate`/`--voice` 参数（默认 -15%≈127wpm 自然讲解节奏；argparse 负数须等号形式 `--rate=-10%`）；SKILL.md E1 用法更新 |
| 2026-09-03 | v2.6.0：**英文视频场景支持**（48页英文EHS课件实战沉淀）——①新增英文专用脚本链 scripts/tts_srt_en.py（edge-tts SentenceBoundary 句子级精确时间轴，无词级但句子级够用）+ build_clean_en.py（slides+audio 重建无字幕母版）+ reburn_subs_en.py（ASS 烧录）；②SKILL.md 新增"⚠️ 英文视频场景"章节（E1-E4：英文必须 tts_srt_en/ASS 烧录/禁在带字幕视频上重烧叠层/像素带验证单层）；③实战经验区 3 条 ERR 沉淀（叠层/force_style 浮中部/单层验证） |
| 2026-09-02 | v2.5.0：维护记录从 SKILL.md 卸载至 references/changelog.md（按需加载原则），SKILL.md 减负 |
| 2026-08-12 | v2.4.0：分层卸载——FAQ 7 条 + 两大经验复盘（字幕优化/bash 中文路径静音）移入 references/pitfalls.md（按需加载），SKILL.md 580→约 420 行，健康分 47→85+。功能不变 |
| 2026-08-12 | v2.3.0：来源署名脱敏——移除外部 skill 名称引用，保留机制描述。IP 风险预防，功能不变。 |
| 2026-08-11 | v2.2.0：新增：①数学符号口语化（pronunciation.py _normalize_math）；②多音字标注语法 `{拼音+声调}`（_strip_polyphone_marks）；③环境缺失处理指南（ffmpeg 下载地址 + pip 国内镜像）；④`--resume-from N` 断点续跑（trvideo.py）；⑤分享前脱敏检查清单。保留反编造铁律/Qwen3双引擎/字幕分段等优势。 |
