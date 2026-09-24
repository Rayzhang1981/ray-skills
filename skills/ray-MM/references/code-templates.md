# 代码模板（按需加载）

> 来源：ray-MM SKILL.md 分层卸载（v1.2.0）。编写生成脚本时按需复制。

## #### 编号配置

```javascript
const numberingConfig = [{
  reference: "content",
  levels: [
    {
      level: 0, format: LevelFormat.DECIMAL, text: "%1.",
      alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } },
    },
    {
      level: 1, format: LevelFormat.DECIMAL, text: "%1.%2.",
      alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 1080, hanging: 360 } } },
    },
  ],
}];
```

## #### 通用辅助函数

```javascript
// 编号议题标题
function secHeader(text) {
  return new Paragraph({
    numbering: { reference: "content", level: 0 },
    spacing: { before: 200, after: 80 },
    children: [new TextRun({ text, font: "等线", size: 22, bold: true, color: "002060" })],
  });
}

// 子项（可选粗体前缀）
function subItem(text, boldPrefix) {
  const runs = [];
  if (boldPrefix) runs.push(new TextRun({ text: boldPrefix, font: "等线", size: 21, bold: true }));
  runs.push(new TextRun({ text, font: "等线", size: 21 }));
  return new Paragraph({
    numbering: { reference: "content", level: 1 },
    spacing: { line: 360, lineRule: "auto" },
    children: runs,
  });
}

// 红色备注项
function noteItem(text) {
  return new Paragraph({
    numbering: { reference: "content", level: 1 },
    spacing: { line: 360, lineRule: "auto" },
    children: [new TextRun({ text, font: "等线", size: 21, color: "C00000", italics: true })],
  });
}
```

## #### 表格构建（待办事项）

```javascript
function makeActionTable(rows) {
  const colWidths = [1600, 5040, 2000];
  const headerRow = new TableRow({
    children: [
      makeTC("责任人/部门", colWidths[0], { bold: true, color: "FFFFFF", size: 18, font: "等线" },
             { fill: "002060", type: ShadingType.CLEAR }, AlignmentType.CENTER),
      // ... 其他列同理
    ],
  });
  const dataRows = rows.map((row, i) => {
    const fill = i % 2 === 0 ? "F2F6FC" : "FFFFFF";
    // ... 构建数据行
  });
  return new Table({
    width: { size: 8640, type: WidthType.DXA },
    columnWidths: colWidths,
    rows: [headerRow, ...dataRows],
  });
}

function makeTC(text, width, textOpts, shading, align) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    borders: { /* 四边单线 */ },
    shading,
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    children: [new Paragraph({ alignment: align || AlignmentType.LEFT,
      children: [new TextRun({ text, ...textOpts })] })],
  });
}
```