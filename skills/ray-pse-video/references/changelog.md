# ray-pse-video 维护记录

> 从 SKILL.md 卸载（2026-09-02），遵守"维护记录不常驻正文"原则。按需加载。

| 日期 | 变更 |
|------|------|
| 2026-08-26 | v2.3.1：实测赛科"5·12"全流程跑通（12页 PPT→TTS→合成 262.88s）；补录 safe-delete 沙箱删除拦截坑（pitfalls 0i 节）+ Step 7 加 ffmpeg 绝对路径提示 |
| 2026-08-26 | v2.3.0：① Step 6 补 Qwen3-TTS 精确字幕的 ASR 词级时间戳补强方案（可选，绕开预估语速误差）；② 执行铁律新增「5. 强制确认关口」——TTS 前旁白脚本 + 人名去敏化映射表须人审确认，防返工 |
| 2026-08-12 | v2.2.0：分层卸载——PPT 设计规范/ffmpeg 安装/Step10 迭代优化/TTS 音色批量生成 4 块移入 references/（ppt-design/env-setup/optimization/tts.md），SKILL.md 990→约 460 行，健康分 40→80+。功能不变 |
