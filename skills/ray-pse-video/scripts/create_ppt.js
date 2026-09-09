// create_ppt.js - auto-generated
var pptxgen = require("pptxgenjs");
var outputPath = process.argv[2] || "output.pptx";
var pptx = new pptxgen();
pptx.layout = "LAYOUT_WIDE";
pptx.author = "Ray谈化工";

var C = {
  bg: "0D1117", bgCard: "161B22", accent: "E74C3C", accent2: "F39C12",
  accent3: "27AE60", white: "ECF0F1", gray: "868E96", lightGray: "B0B8C1",
  dimWhite: "C8D6E5", darkRed: "C0392B", blue: "3498DB"
};

function titleSlide(title, subtitle, desc) {
  var s = pptx.addSlide();
  s.background = { color: C.bg };
  s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: "100%", h: 0.06, fill: { color: C.accent } });
  s.addText(title, { x: 0.8, y: 1.2, w: "85%", h: 1.5, fontSize: 36, fontFace: "Microsoft YaHei", color: C.white, bold: true, align: "left", valign: "bottom" });
  if (subtitle) s.addText(subtitle, { x: 0.8, y: 2.8, w: "85%", h: 0.8, fontSize: 20, fontFace: "Microsoft YaHei", color: C.accent, align: "left" });
  if (desc) s.addText(desc, { x: 0.8, y: 3.5, w: "78%", h: 1.2, fontSize: 15, fontFace: "Microsoft YaHei", color: C.gray, align: "left", lineSpacingMultiple: 1.5 });
  s.addShape(pptx.shapes.RECTANGLE, { x: 0.8, y: 5.1, w: 2.5, h: 0.04, fill: { color: C.accent } });
}

function cs(title, items) {
  var s = pptx.addSlide();
  s.background = { color: C.bg };
  s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: "100%", h: 0.05, fill: { color: C.accent } });
  s.addText(title, { x: 0.7, y: 0.4, w: "88%", h: 0.75, fontSize: 28, fontFace: "Microsoft YaHei", color: C.white, bold: true, align: "left" });
  s.addShape(pptx.shapes.RECTANGLE, { x: 0.7, y: 1.2, w: 1.8, h: 0.04, fill: { color: C.accent } });
  var bt = items.map(function(x) { return x.t; }).join("\n");
  s.addText(bt, { x: 0.7, y: 1.55, w: "85%", h: 3.8, fontSize: 16, fontFace: "Microsoft YaHei", color: C.dimWhite, bullet: { type: "number", color: C.accent }, lineSpacingMultiple: 1.55, align: "left", valign: "top" });
}

// ================= 示例调用（通用模板） =================
// 实际使用：按 SKILL.md 流程读取目标事故调查报告，生成以下调用序列。
// 本示例使用虚构事故信息演示 titleSlide / contentSlide 用法。

// === SLIDE 1：封面 ===
titleSlide('XX化工有限公司“X·X”事故警示教育', '事故教训中成长 — 培训视频', '日期 · 地点 · 伤亡 · 损失（按调查报告填写）');

// === SLIDE 2：事故经过（示例） ===
contentSlide('事故经过', [
  {t: '事故经过要点 1（按报告时间线归纳）'},
  {t: '事故经过要点 2'}
]);

// === SLIDE 3：事故教训（示例） ===
contentSlide('事故教训', [
  {t: '教训 1：管理原因与改进方向（对应报告原因分析）'},
  {t: '教训 2：…'}
]);

pptx.writeFile({ fileName: outputPath })
  .then(function() { console.log("PPT created: " + outputPath); })