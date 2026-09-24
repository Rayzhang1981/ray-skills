// ============================================================
// Ray-MM 纪要生成脚本模板（v2.0.0 固化版）
// 用法：复制本文件为 gen_minutes.js
//       ① 改 OUTPUT 路径
//       ② 填 topics（议题数组）与 actions（待办数组）
//       ③ NODE_PATH=<node_modules> node gen_minutes.js
// 格式标准见 references/format-spec.md —— 无需任何模板 DOCX
// ============================================================
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat,
  BorderStyle, WidthType, ShadingType, PageNumber,
} = require("docx");

// ---------- ① 输出路径（必改） ----------
const OUTPUT = "C:/output/会议纪要-主题-0825-2026.docx";
// 页眉标题（一般与表头标题一致）
const HEADER_TEXT = "会议纪要";

// ---------- 固定样式常量（勿改，见 format-spec.md） ----------
const FONT_CN = "等线";
const BLUE = "002060";
const RED = "C00000";

// ============ 编号配置 ============
const numberingConfig = [{
  reference: "content",
  levels: [
    { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
    { level: 1, format: LevelFormat.DECIMAL, text: "%1.%2.", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 1080, hanging: 360 } } } },
    { level: 2, format: LevelFormat.LOWER_LETTER, text: "%3)", alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 1440, hanging: 360 } } } },
  ],
}];

// ============ 通用辅助函数 ============
function secHeader(text) {
  return new Paragraph({
    numbering: { reference: "content", level: 0 },
    spacing: { before: 200, after: 80 },
    children: [new TextRun({ text, font: FONT_CN, size: 22, bold: true, color: BLUE })],
  });
}
function headItem(text) {
  return new Paragraph({
    numbering: { reference: "content", level: 1 },
    spacing: { line: 360, lineRule: "auto" },
    children: [new TextRun({ text, font: FONT_CN, size: 21, bold: true })],
  });
}
function detailItem(text) {
  return new Paragraph({
    numbering: { reference: "content", level: 2 },
    spacing: { line: 360, lineRule: "auto" },
    children: [new TextRun({ text, font: FONT_CN, size: 21 })],
  });
}
function bodyPara(text, opts = {}) {
  return new Paragraph({
    spacing: { line: 360, lineRule: "auto" },
    indent: { firstLine: 420 },
    children: [new TextRun({ text, font: FONT_CN, size: 21,
      color: opts.color || "000000", italics: opts.italics || false })],
  });
}
function sectionTitle(prefix, text) {
  return new Paragraph({
    spacing: { before: 240, after: 120 },
    children: [
      new TextRun({ text: prefix + "  ", font: "Garamond", size: 22, bold: true, color: BLUE }),
      new TextRun({ text, font: FONT_CN, size: 22, bold: true, color: BLUE }),
    ],
  });
}
function spacer() {
  return new Paragraph({ spacing: { before: 60, after: 60 }, children: [] });
}

// ============ 表格构建 ============
function makeTC(text, width, textOpts, shading, align) {
  const border = { style: BorderStyle.SINGLE, size: 4, color: "999999" };
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    borders: { top: border, bottom: border, left: border, right: border },
    shading,
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    children: [new Paragraph({
      alignment: align || AlignmentType.LEFT,
      spacing: { line: 300, lineRule: "auto" },
      children: [new TextRun({ text, ...textOpts })],
    })],
  });
}

function makeHeaderTable(title) {
  const w = [1560, 2760, 1560, 2760];
  const tblW = 8640;
  const labelOpts = { font: "Garamond", size: 22, bold: true, color: "000000" };
  const valOpts = { font: "Garamond", size: 20, italics: true, color: "404040" };
  const titleRow = new TableRow({
    children: [new TableCell({
      columnSpan: 4,
      width: { size: tblW, type: WidthType.DXA },
      borders: { top: { style: BorderStyle.SINGLE, size: 4, color: "999999" },
                 bottom: { style: BorderStyle.SINGLE, size: 4, color: "999999" } },
      margins: { top: 120, bottom: 120 },
      children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: title, font: "微软雅黑", size: 28, bold: true })] })],
    })],
  });
  const timeRow = new TableRow({
    children: [
      makeTC("时间:", w[0], labelOpts, undefined, AlignmentType.RIGHT),
      makeTC("待补充", w[1], valOpts),
      makeTC("地点:", w[2], labelOpts, undefined, AlignmentType.RIGHT),
      makeTC("待补充", w[3], valOpts),
    ],
  });
  const personRow = new TableRow({
    children: [
      makeTC("人员:", w[0], labelOpts, undefined, AlignmentType.RIGHT),
      makeTC("待补充（详见签到表）", w[1], valOpts),
      makeTC("CC抄送:", w[2], labelOpts, undefined, AlignmentType.RIGHT),
      makeTC("待补充", w[3], valOpts),
    ],
  });
  return new Table({ width: { size: tblW, type: WidthType.DXA },
    columnWidths: w, rows: [titleRow, timeRow, personRow] });
}

function makeActionTable(rows) {
  const colWidths = [1600, 5040, 2000];
  const tblW = 8640;
  const border = { style: BorderStyle.SINGLE, size: 4, color: "999999" };
  const headerRow = new TableRow({
    children: [
      makeTC("责任人/部门", colWidths[0], { bold: true, color: "FFFFFF", size: 18, font: FONT_CN },
             { fill: BLUE, type: ShadingType.CLEAR }, AlignmentType.CENTER),
      makeTC("任务内容", colWidths[1], { bold: true, color: "FFFFFF", size: 18, font: FONT_CN },
             { fill: BLUE, type: ShadingType.CLEAR }, AlignmentType.CENTER),
      makeTC("截止时间", colWidths[2], { bold: true, color: "FFFFFF", size: 18, font: FONT_CN },
             { fill: BLUE, type: ShadingType.CLEAR }, AlignmentType.CENTER),
    ],
  });
  const dataRows = rows.map((r, i) => {
    const fill = i % 2 === 0 ? "F2F6FC" : "FFFFFF";
    const shd = { fill, type: ShadingType.CLEAR };
    return new TableRow({
      children: [
        makeTC(r.who, colWidths[0], { font: FONT_CN, size: 19, bold: true }, shd, AlignmentType.CENTER),
        makeTC(r.task, colWidths[1], { font: FONT_CN, size: 19 }, shd, AlignmentType.LEFT),
        makeTC(r.ddl, colWidths[2], { font: FONT_CN, size: 19 }, shd, AlignmentType.CENTER),
      ],
    });
  });
  return new Table({ width: { size: tblW, type: WidthType.DXA },
    columnWidths: colWidths, rows: [headerRow, ...dataRows] });
}

// ============================================================
// ---------- ② 内容区（必填）
// topics: [{ title, items: [{ head, details: [..] }] }]
// actions: [{ who, task, ddl }]  —— 忠实引用纪律：全部来自材料，缺信息标"未明确"
// ============================================================
const topics = [
  // 例：
  // { title: "议题一标题", items: [
  //   { head: "要点小标题", details: ["细节 1", "细节 2"] },
  // ]},
];

const actions = [
  // 例： { who: "责任人", task: "任务内容", ddl: "截止时间" },
];

// ============ 文档组装（结构固定，见 format-spec.md §6） ============
const children = [];
const DOC_TITLE = HEADER_TEXT + "会议纪要";

children.push(makeHeaderTable(DOC_TITLE));
children.push(spacer());

children.push(sectionTitle("TOPIC", "会议主题（从材料提取）"));
children.push(bodyPara("（会议综述：材料首段/v总结，忠实引用，不润色）"));

children.push(sectionTitle("CONTENT", "会议内容"));
for (const t of topics) {
  children.push(secHeader(t.title));
  for (const it of t.items) {
    children.push(headItem(it.head));
    for (const d of it.details) children.push(detailItem(d));
  }
}

children.push(sectionTitle("ACTION", "待办事项"));
children.push(makeActionTable(actions));

children.push(sectionTitle("APPENDIX", "附件与说明"));
children.push(bodyPara("本纪要根据会议材料整理，涉及具体数据与专业术语请以实际会议记录为准。"));
children.push(bodyPara("【待核实】事项：列出材料中存疑/缺失项。", { color: RED, italics: true }));

const doc = new Document({
  numbering: { config: numberingConfig },
  styles: { default: { document: { run: { font: FONT_CN, size: 21 } } } },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1800, bottom: 1440, left: 1800, header: 720, footer: 720 },
      },
    },
    headers: { default: new Header({
      children: [new Paragraph({ alignment: AlignmentType.RIGHT,
        children: [new TextRun({ text: HEADER_TEXT, font: "微软雅黑", size: 18, italics: true, color: "808080" })] })],
    }) },
    footers: { default: new Footer({
      children: [new Paragraph({ alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "第 ", font: "Garamond", size: 18 }),
                   new TextRun({ children: [PageNumber.CURRENT], font: "Garamond", size: 18 }),
                   new TextRun({ text: " 页", font: "Garamond", size: 18 })] })],
    }) },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUTPUT, buf);
  console.log("OK -> " + OUTPUT + " (" + buf.length + " bytes)");
}).catch((e) => { console.error("FAIL", e); process.exit(1); });