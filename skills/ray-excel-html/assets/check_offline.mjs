/* 离线自包含断言（offline self-containment）
   机制来源（外部对比）：成熟 HTML 产物技能把"零外部源"作为硬断言，
   并要求"解析 HTML 而不是扫字符串"（避免注释/脚本里的 URL 误报与漏检）。
   适配：本工具不内嵌字体，故只断言"零外部子资源 + 零外部导航依赖可选"。
   用法: node check_offline.mjs <html文件...>
*/
import fs from 'node:fs';
import path from 'node:path';
import { parse } from 'parse5';

const REMOTE = (v) => /^(?:https?:)?\/\//i.test(v || '');

export function inspectDocuments(html, subject = 'artifact') {
  const doc = { subject, styles: [], scripts: [], resources: [], children: [] };
  function cssResources(css) {
    const clean = css.replace(/\/\*[\s\S]*?\*\//g, '');
    for (const m of clean.matchAll(/(?:url\(\s*|@import\s+)["']?((?:https?:)?\/\/[^"')\s;]+)/gi)) {
      doc.resources.push({ where: subject + ' css', url: m[1] });
    }
  }
  function visit(node) {
    const attrs = Object.fromEntries((node.attrs || []).map(({ name, value }) => [name, value]));
    const text = (node.childNodes || []).filter(c => c.nodeName === '#text').map(c => c.value).join('');
    if (node.tagName === 'style') { doc.styles.push(text); cssResources(text); }
    if (node.tagName === 'script') doc.scripts.push(text);
    if (attrs.style) cssResources(attrs.style);
    for (const n of ['src', 'poster', 'data']) if (REMOTE(attrs[n])) doc.resources.push({ where: subject + ' @' + n, url: attrs[n] });
    if (attrs.srcset) for (const m of attrs.srcset.matchAll(/(?:^|[\s,])((?:https?:)?\/\/[^\s,]+)/g)) doc.resources.push({ where: subject + ' @srcset', url: m[1] });
    if (['image', 'use', 'feImage'].includes(node.tagName)) { if (REMOTE(attrs.href)) doc.resources.push({ where: subject + ' <' + node.tagName + '>', url: attrs.href }); }
    if (node.tagName === 'link' && /\b(stylesheet|preconnect|dns-prefetch|preload|modulepreload|prefetch|icon)\b/.test(attrs.rel || '')) {
      if (REMOTE(attrs.href)) doc.resources.push({ where: subject + ' <link rel=' + attrs.rel + '>', url: attrs.href });
    }
    if (node.tagName === 'iframe' && attrs.srcdoc != null) doc.children.push(...inspectDocuments(attrs.srcdoc, `${subject}/srcdoc[${doc.children.length}]`));
    for (const c of node.childNodes || []) visit(c);
  }
  visit(parse(html));
  return [doc, ...doc.children];
}

/* 额外的工程化断言（本工具特有）*/
export function checkEngineeringGuards(html) {
  const issues = [];
  // 1. 主题初始化必须保护 localStorage（file:// / 隐私模式会抛异常 → 整页脚本崩）
  if (/localStorage/.test(html) && !/try\s*\{[^}]*localStorage/s.test(html)) {
    issues.push('localStorage 访问未见 try 保护（受限来源下会中断整页脚本）');
  }
  // 2. clipboard 必须先探测再调用（非安全上下文为 undefined）
  if (/navigator\.clipboard\.writeText/.test(html) && !/navigator\.clipboard\s*&&/.test(html)) {
    issues.push('navigator.clipboard 未探测即调用（可能抛未捕获 TypeError）');
  }
  // 3. 尾零剥离不得作用于整数（/\.?0+$/ 会把 "1000" 剥成 "1"）
  if (/replace\(\/\\\.\?0\+\$\/[^)]*\)/.test(html)) {
    issues.push('疑似使用 /\\.?0+$/ 剥离尾零（整数会被破坏），应排除无小数点/科学计数的串');
  }
  // 4. 溯源 footer 必须存在
  if (!/chef-calculation|源文件|派生自/.test(html)) issues.push('缺少溯源信息（源文件名/派生说明）');
  return issues;
}

const files = process.argv.slice(2);
if (!files.length) { console.error('用法: node check_offline.mjs <html...>'); process.exit(2); }
let bad = 0;
for (const f of files) {
  const html = fs.readFileSync(f, 'utf8');
  const docs = inspectDocuments(html, path.basename(f));
  const resources = docs.flatMap(d => d.resources);
  const guards = checkEngineeringGuards(html);
  const bytes = fs.statSync(f).size;
  console.log('='.repeat(68));
  console.log('产物: ' + path.basename(f) + '   ' + bytes + ' 字节   ' + docs.length + ' 个文档');
  if (resources.length === 0) console.log('  ✓ 离线自包含：零外部子资源（解析式检查，非字符串扫描）');
  else { bad++; console.log('  ✗ 发现 ' + resources.length + ' 个外部子资源：'); resources.forEach(r => console.log('      ' + r.where + ' → ' + r.url)); }
  if (guards.length === 0) console.log('  ✓ 工程化护栏：4 项全部通过');
  else { bad++; console.log('  ✗ 工程化护栏问题：'); guards.forEach(g => console.log('      · ' + g)); }
}
console.log('='.repeat(68));
console.log(bad === 0 ? '✅ 离线自包含检查通过' : '⛔ 离线自包含检查发现 ' + bad + ' 项问题');
process.exitCode = bad === 0 ? 0 : 1;
