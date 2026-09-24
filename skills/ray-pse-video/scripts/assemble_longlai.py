#!/usr/bin/env python
"""
assemble_longlai.py - 江西隆莱"12·31"窒息事故培训视频组装脚本
Usage: python assemble_longlai.py <work_dir>
"""
import os, sys, json, subprocess, asyncio, shutil, re, glob as globmod
from pathlib import Path

# ============ Configuration ============
WORK_DIR = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
VOICE = "zh-CN-YunjianNeural"  # Male, professional
RATE = "+5%"
TOTAL_SLIDES = 12
FONT_NAME_ASS = "微软雅黑"
FONT_NAME_DRAWTEXT = "Microsoft YaHei"
WM_TEXT = "Ray谈化工 \u00b7 PSE Video"

# Detect ffmpeg
def find_ffmpeg():
    ff = shutil.which('ffmpeg')
    if ff: return ff
    known = os.path.expandvars(r'%USERPROFILE%\.workbuddy\binaries\ffmpeg\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe')
    if os.path.exists(known): return known
    legacy = os.path.expandvars(r'%USERPROFILE%\.workbuddy\binaries\python\versions\3.13.12\Lib\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe')
    if os.path.exists(legacy): return legacy
    raise RuntimeError("ffmpeg not found")

FFMPEG = find_ffmpeg()
NODE_EXE = r'C:\Users\rayzh\.workbuddy\binaries\node\versions\22.22.2\node.exe'
NODE_PATH = r'C:\Users\rayzh\.workbuddy\binaries\node\workspace\node_modules'

print(f"Work dir: {WORK_DIR}")
print(f"FFmpeg: {FFMPEG}")
os.makedirs(WORK_DIR, exist_ok=True)

# ============ Step 1: Create PPT JS file ============
def write_ppt_js():
    """Generate create_ppt.js"""
    js = os.path.join(WORK_DIR, 'create_ppt.js')
    
    # Build slides data
    slides = [
        # Slide 1: Title
        {"type": "title", "title": "江西隆莱生物制药有限公司\n\u201c12\u00b731\u201d较大窒息事故调查报告",
         "subtitle": "事故教训中成长 \u2014 培训视频",
         "desc": "2025年12月31日 \u00b7 南昌进贤 \u00b7 3死3伤 \u00b7 直接经济损失407.86万元"},
        
        # Slide 2: Overview
        {"type": "content", "title": "事故概览", "items": [
            "时间：2025年12月31日 22时25分许",
            "地点：江西省南昌市进贤产业园",
            "单位：江西隆莱生物制药有限公司",
            "伤亡：3人死亡，3人受伤",
            "直接经济损失：约407.86万元人民币",
            "事故性质：较大生产安全责任事故",
            "事故类型：窒息事故（氮气反窜入呼吸供气管线）"
        ]},
        
        # Slide 3: Equipment
        {"type": "content", "title": "装置背景 \u2014 供气系统", "items": [
            "105车间制氮系统：空压机压缩空气 \u2192 空气储罐 \u2192 冷干机 \u2192 制氮装置 \u2192 氮气储罐（24h连续运行）",
            "105车间空气供应系统：同一空压机为长管呼吸器供气管网提供压缩空气",
            "110车间空气供应系统：独立空压机，供应工艺用气 + 长管呼吸器用气",
            "两套系统互为备用，通常每15天切换一次",
            "关键隐患：制氮系统与呼吸供气系统共用空压机气源",
            "2020年4月投入使用，期间105/110系统交替使用"
        ]},
        
        # Slide 4: Timeline
        {"type": "content", "title": "事故经过 \u2014 关键时间线", "items": [
            "20:00 \u2014 晚班组完成交接班，5个车间使用长管呼吸器",
            "21:51 \u2014 101车间操作员反馈佩戴呼吸器后身体不适",
            "22:00 \u2014 104车间操作人员反馈同样情况",
            "22:21 \u2014 107车间发现操作员昏迷倒地（佩戴呼吸器）",
            "22:30 \u2014 105车间操作员感不适摘除面罩，发现两名同事倒地",
            "22:30 \u2014 106车间两名操作员昏迷倒地（仍佩戴呼吸器）",
            "22:30 \u2014 厂方通知禁止使用长管呼吸器",
            "22:40 \u2014 救护车到达现场，3人经抢救无效死亡"
        ]},
        
        # Slide 5: Direct cause
        {"type": "content", "title": "直接原因 \u2014 氮气反窜机理", "items": [
            "空压机电机轴承损坏 \u2192 电流过载 \u2192 故障跳停 \u2192 压缩空气气源压力下降",
            "气源压力不足（<0.5MPa）\u2192 气动阀门控制失效",
            "吸附器进出气动阀反向内漏（检测：0.17~0.31MPa即泄漏）",
            "氮气管线止逆阀旁通阀处于一定开启状态",
            "氮气窜入吸附器出口管线 \u2192 反向泄漏至呼吸用压缩空气管线",
            "员工吸入氧含量远低于正常值的空气 \u2192 昏迷 \u2192 休克 \u2192 死亡"
        ]},
        
        # Slide 6: Root cause 1 - Change Management
        {"type": "content", "title": "根因分析(1) \u2014 变更管理失控", "items": [
            "2020年企业自行改造：在制氮系统增加缓冲罐和压缩空气管线，给长管呼吸器集中供气",
            "改造未经过充分技术论证，未执行变更管理程序",
            "制氮系统与呼吸供气系统共用气源 \u2192 埋下氮气反窜的重大隐患",
            "变更后未进行风险再评估：未识别\u201c氮气可能窜入呼吸管线致人窒息\u201d这一致命风险",
            "变更管理是企业过程安全管理的核心要素之一",
            "本案中变更管理完全缺失，是事故最深层的历史原因"
        ]},
        
        # Slide 7: Root cause 2 - Risk & inspection
        {"type": "content", "title": "根因分析(2) \u2014 风险辨识与隐患排查缺失", "items": [
            "风险辨识不全：未识别\u201c氮气回流至长管呼吸器供气管线\u201d的风险",
            "隐患排查不到位：未及时发现空压机轴承损坏、气动阀密封失效",
            "设备维护保养制度未严格落实：气动阀未定期检测密封性能",
            "空压机频繁报警未引起重视，\u201c狼来了\u201d效应导致麻痹大意",
            "隐患报告机制失效：员工多次反馈身体不适，但信息未有效传递",
            "思想麻痹：\u201c以前没出过事\u201d心态导致风险管控长期缺位"
        ]},
        
        # Slide 8: Root cause 3 - Emergency & training
        {"type": "content", "title": "根因分析(3) \u2014 应急响应与培训不足", "items": [
            "企业未制定长管呼吸器使用的专项应急预案",
            "缺乏针对\u201c气源中断、氮气窜入\u201d等特定情景的处置指引",
            "中控室视频巡检和夜间巡检未有效发挥作用",
            "从第一人倒下到被发现，中间延误约20分钟",
            "安全培训流于表面，未讲解气源异常、窒息应急等关键内容",
            "一线人员应急处置能力严重不足，自救互救知识匮乏"
        ]},
        
        # Slide 9: Accountability
        {"type": "content", "title": "追责情况", "items": [
            "移送司法机关：2人（涉嫌构成犯罪）",
            "移交纪检监察机关：12名公职人员履职问题线索",
            "行政处罚：企业法定代表人及5名事故责任人",
            "企业行政处罚：江西隆莱生物制药有限公司",
            "书面检查：南昌市应急管理局、进贤县人民政府",
            "深刻检查：进贤产业园管委会、县卫健委、县应急局、县工信局、县市监局"
        ]},
        
        # Slide 10: Lessons
        {"type": "content", "title": "事故主要教训", "items": [
            "风险辨识存在严重盲区 \u2014 风险辨识流于形式，未能深入工艺/设备/管理的本质关联进行系统性分析",
            "隐患排查流于形式 \u2014 排查多而不细，对空压机频繁报警、气动阀密封性能等核心隐患失察",
            "应急处置能力严重不足 \u2014 从首人倒下到被发现延误20分钟，专项预案缺失",
            "变更管理完全缺失 \u2014 自行改造供气系统未评估风险，源头上制造了事故条件",
            "一线员工安全意识欠缺 \u2014 多次反馈不适但隐患报告机制失效",
            "安全培训缺乏针对性 \u2014 未覆盖气源异常识别、窒息应急等核心内容"
        ]},
        
        # Slide 11: Prevention
        {"type": "content", "title": "整改与防范措施", "items": [
            "立即拆除制氮系统与呼吸供气系统的直接连接管路",
            "设置物理隔离、止逆阀、气体检测报警等多重防护装置",
            "制定长管呼吸器使用专项管理制度及操作规程",
            "建立设备全生命周期管理制度，强化异常状态监测预警",
            "开展全员安全再培训，覆盖气源异常识别、窒息应急流程",
            "组织气源中断、氮气窜入等场景的实战应急演练",
            "严格执行变更管理程序，变更后必须开展风险再评估"
        ]},
        
        # Slide 12: Conclusion
        {"type": "title", "title": "以案为鉴 \u00b7 警钟长鸣",
         "subtitle": "\u2014 江西隆莱生物制药 \u201c12\u00b731\u201d窒息事故 \u2014",
         "desc": "\u201c风险管控的关键在于\u2018预\u2019。企业必须建立科学、动态的风险评估更新机制，\n尤其在实施技术改造、变更管理时，必须严格执行风险再评估程序，\n确保所有潜在危险源被识别，从根本防止风险失控。\u201d\n\n\u2014 事故调查报告"}
    ]
    
    # Helper to escape JS string
    def js_str(s):
        return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    
    lines = []
    lines.append('// create_ppt.js - auto-generated')
    lines.append('var pptxgen = require("pptxgenjs");')
    lines.append('var outputPath = process.argv[2] || "output.pptx";')
    lines.append('var pptx = new pptxgen();')
    lines.append('pptx.layout = "LAYOUT_WIDE";')
    lines.append('pptx.author = "Ray谈化工";')
    lines.append('')
    lines.append('var C = {')
    lines.append('  bg: "0D1117", bgCard: "161B22", accent: "E74C3C", accent2: "F39C12",')
    lines.append('  accent3: "27AE60", white: "ECF0F1", gray: "868E96", lightGray: "B0B8C1",')
    lines.append('  dimWhite: "C8D6E5", darkRed: "C0392B", blue: "3498DB"')
    lines.append('};')
    lines.append('')
    
    # Helper functions
    lines.append('function titleSlide(title, subtitle, desc) {')
    lines.append('  var s = pptx.addSlide();')
    lines.append('  s.background = { color: C.bg };')
    lines.append('  s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: "100%", h: 0.06, fill: { color: C.accent } });')
    lines.append('  s.addText(title, { x: 0.8, y: 1.2, w: "85%", h: 1.5, fontSize: 36, fontFace: "Microsoft YaHei", color: C.white, bold: true, align: "left", valign: "bottom" });')
    lines.append('  if (subtitle) s.addText(subtitle, { x: 0.8, y: 2.8, w: "85%", h: 0.8, fontSize: 20, fontFace: "Microsoft YaHei", color: C.accent, align: "left" });')
    lines.append('  if (desc) s.addText(desc, { x: 0.8, y: 3.5, w: "78%", h: 1.2, fontSize: 15, fontFace: "Microsoft YaHei", color: C.gray, align: "left", lineSpacingMultiple: 1.5 });')
    lines.append('  s.addShape(pptx.shapes.RECTANGLE, { x: 0.8, y: 5.1, w: 2.5, h: 0.04, fill: { color: C.accent } });')
    lines.append('}')
    lines.append('')
    
    lines.append('function cs(title, items) {')
    lines.append('  var s = pptx.addSlide();')
    lines.append('  s.background = { color: C.bg };')
    lines.append('  s.addShape(pptx.shapes.RECTANGLE, { x: 0, y: 0, w: "100%", h: 0.05, fill: { color: C.accent } });')
    lines.append('  s.addText(title, { x: 0.7, y: 0.4, w: "88%", h: 0.75, fontSize: 28, fontFace: "Microsoft YaHei", color: C.white, bold: true, align: "left" });')
    lines.append('  s.addShape(pptx.shapes.RECTANGLE, { x: 0.7, y: 1.2, w: 1.8, h: 0.04, fill: { color: C.accent } });')
    lines.append('  var bt = items.map(function(x) { return x.t; }).join("\\n");')
    lines.append('  s.addText(bt, { x: 0.7, y: 1.55, w: "85%", h: 3.8, fontSize: 16, fontFace: "Microsoft YaHei", color: C.dimWhite, bullet: { type: "number", color: C.accent }, lineSpacingMultiple: 1.55, align: "left", valign: "top" });')
    lines.append('}')
    lines.append('')
    
    # Generate slides
    for i, slide in enumerate(slides):
        lines.append(f'// === SLIDE {i+1} ===')
        if slide["type"] == "title":
            lines.append(f'titleSlide("{js_str(slide["title"])}", "{js_str(slide.get("subtitle", ""))}", "{js_str(slide.get("desc", ""))}");')
        else:
            items_str = ',\n    '.join(['{t: "' + js_str(item) + '"}' for item in slide["items"]])
            lines.append(f'cs("{js_str(slide["title"])}", [\n    {items_str}\n  ]);')
        lines.append('')
    
    lines.append('pptx.writeFile({ fileName: outputPath })')
    lines.append('  .then(function() { console.log("PPT created: " + outputPath); })')
    lines.append('  .catch(function(err) { console.error("Error:", err); });')
    
    content = '\n'.join(lines)
    with open(js, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  create_ppt.js written: {len(content)} chars")
    return js

# ============ Step 2: Run pptxgenjs ============
def create_pptx():
    js_path = os.path.join(WORK_DIR, 'create_ppt.js')
    pptx_path = os.path.join(WORK_DIR, 'output.pptx')
    
    env = os.environ.copy()
    env['NODE_PATH'] = NODE_PATH
    
    print(f"  Running pptxgenjs...")
    result = subprocess.run(
        [NODE_EXE, js_path, pptx_path],
        cwd=WORK_DIR,
        env=env,
        capture_output=True,
        text=True,
        timeout=60
    )
    print(f"  stdout: {result.stdout.strip()}")
    if result.stderr:
        print(f"  stderr: {result.stderr.strip()[:500]}")
    
    if not os.path.exists(pptx_path):
        raise RuntimeError(f"PPTX not created: {pptx_path}")
    
    size_mb = os.path.getsize(pptx_path) / 1024 / 1024
    print(f"  PPTX created: {size_mb:.1f} MB")
    return pptx_path

# ============ Step 3: Narration script ============
def get_narration():
    """Return narration for each slide"""
    return [
        # Slide 1 (0-12s)
        "大家好，欢迎收看本期事故教训培训视频。今天我们要分析的是江西隆莱生物制药有限公司\u201c12\u00b731\u201d较大窒息事故。这起事故发生在2025年12月31日，造成3人死亡、3人受伤，直接经济损失407.86万元。",
        
        # Slide 2 (12-30s)
        "先看事故概览。2025年12月31日晚上10点25分左右，位于江西省南昌市进贤产业园的江西隆莱生物制药有限公司发生了一起较大窒息事故。事故造成3人死亡、3人受伤，经调查认定为较大生产安全责任事故。省安委会对该起事故进行了挂牌督办。",
        
        # Slide 3 (30-52s)
        "现在我们来了解事故涉及的装置背景。该公司有两套供气系统：105车间的制氮系统和空气供应系统共用同一台空压机，这是一个关键隐患点。110车间有独立空压机，供工艺用气和呼吸器用气。两套系统互为备用，通常每15天切换一次。但问题在于，制氮系统和呼吸供气系统共用气源，这个设计埋下了致命隐患。",
        
        # Slide 4 (52-82s)
        "接下来看事故发生的关键时间线。当晚8点，晚班组完成交接班，5个车间使用长管呼吸器。9点51分，101车间操作员反馈佩戴呼吸器后身体不适。10点整，104车间也反馈了同样情况。10点21分，107车间发现一名操作员昏迷倒地。10点30分，105和106车间相继发现多人倒地，厂方才紧急通知禁止使用呼吸器。但为时已晚，3人经抢救无效死亡。从首人反馈到禁令发布，中间延误了近40分钟。",
        
        # Slide 5 (82-110s)
        "现在分析事故的直接原因。空压机电机轴承损坏导致电流过载、故障跳停，压缩空气气源压力下降到正常值以下。气源压力不足导致气动阀门控制失效。更严重的是，检测发现吸附器的三个气动阀在0.17到0.31兆帕时就已经出现反向内漏。同时，氮气管线上的止逆阀旁通阀处于一定开启状态。这些因素叠加，导致氮气窜入吸附器出口管线，反向泄漏至呼吸用的压缩空气管线。员工吸入的是氧含量远低于正常值的空气，逐渐昏迷、休克、直至死亡。三层防护同时失效，这是典型的瑞士奶酪模型。",
        
        # Slide 6 (110-138s)
        "第一个根因是变更管理完全失控。2020年，企业在没有充分技术论证的情况下，自行改造了供气系统，将制氮系统的压缩空气管线连接到长管呼吸器的供气管网。这一改造没有执行变更管理程序，没有进行风险再评估，直接制造了氮气可能反窜入呼吸管线致人窒息的致命风险。变更管理是过程安全管理的核心要素，在本案中却完全缺失。",
        
        # Slide 7 (138-165s)
        "第二个根因是风险辨识与隐患排查双重缺失。企业虽然建立了风险评估机制，但未能识别氮气可能回流至呼吸供气管线这一重大风险，风险辨识流于形式。同时，隐患排查多而不细，空压机频繁报警没引起重视，气动阀密封性能长期未检测。员工多次反馈身体不适，但隐患报告机制形同虚设。\u201c以前没出过事\u201d的麻痹心态，让风险管控长期处于真空状态。",
        
        # Slide 8 (165-190s)
        "第三个根因是应急响应与培训严重不足。企业没有针对长管呼吸器制定专项应急预案，缺少对气源中断、氮气窜入等特定情景的处置指引。中控室和夜间巡检都没有有效发挥作用。从第一个人倒下到被发现，中间延误了约20分钟。安全培训只走形式，一线人员缺乏气源异常识别和窒息应急处置能力。应急预案若缺乏针对性和实操性，等于形同虚设。",
        
        # Slide 9 (190-210s)
        "来看追责情况。2人被移送司法机关追究刑事责任，12名公职人员的问题线索移交纪检监察机关。企业法定代表人及5名事故责任人被行政处罚，公司本身也被依法处罚。此外，南昌市应急管理局、进贤县人民政府等多个政府部门被要求作出书面检查或深刻检查。从企业到监管，全链条追责。",
        
        # Slide 10 (210-238s)
        "总结事故的主要教训。首先，风险辨识存在严重盲区，未能深入工艺、设备、管理的本质关联进行系统分析。其次，隐患排查流于形式，对核心隐患失察。第三，应急处置能力严重不足，专项预案缺失导致延误。第四，变更管理完全缺失，在源头上制造了事故条件。第五，一线员工安全意识欠缺，隐患报告机制失效。第六，安全培训缺乏针对性，未覆盖核心内容。这六条教训，每一条都是用生命换来的。",
        
        # Slide 11 (238-265s)
        "最后看整改与防范措施。企业被要求立即拆除制氮系统与呼吸供气系统的直接连接管路，设置物理隔离和多重防护装置。同时要制定专项管理制度，建立设备全生命周期管理，强化异常状态监测预警。还要开展全员安全再培训和实战应急演练，严格执行变更管理程序。监管部门也被要求补齐短板、强化联动、提升监管效能。",
        
        # Slide 12 (265-280s)
        "\u201c风险管控的关键在于预。企业必须建立科学、动态的风险评估更新机制，尤其在实施技术改造、变更管理时，必须严格执行风险再评估程序，确保所有潜在危险源被识别，从根本防止风险失控。\u201d这是事故调查报告的总结，也是我们每一位安全从业者必须铭记的准则。以案为鉴，警钟长鸣。"
    ]

# ============ Step 4: TTS + SRT generation ============
async def generate_tts_and_srt():
    import edge_tts
    
    narration = get_narration()
    audio_dir = os.path.join(WORK_DIR, 'audio')
    os.makedirs(audio_dir, exist_ok=True)
    
    # Generate TTS with SentenceBoundary timing
    all_cues = []  # Store cues per slide
    audio_durations = []
    
    for i, text in enumerate(narration):
        slide_num = i + 1
        mp3_path = os.path.join(audio_dir, f'slide_{slide_num:02d}.mp3')
        
        print(f"  TTS slide {slide_num}/{TOTAL_SLIDES} ({len(text)} chars)...")
        
        comm = edge_tts.Communicate(text, VOICE, rate=RATE)
        sub = edge_tts.SubMaker()
        audio_data = []
        
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio_data.append(chunk["data"])
            elif chunk["type"] == "SentenceBoundary":
                sub.feed(chunk)
        
        with open(mp3_path, "wb") as f:
            for d in audio_data:
                f.write(d)
        
        # Get actual audio duration using ffmpeg
        probe = subprocess.run(
            [FFMPEG, '-i', mp3_path, '-f', 'null', '-'],
            capture_output=True, text=True
        )
        dur_str = None
        for line in probe.stderr.split('\n'):
            if 'Duration' in line:
                import re
                m = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', line)
                if m:
                    dur_str = float(m.group(1))*3600 + float(m.group(2))*60 + float(m.group(3))
        audio_durations.append(dur_str or 0)
        
        # Extract cues
        cues = []
        for item in sub.cues:
            cues.append((item.start.total_seconds(), item.end.total_seconds(), item.content.strip()))
        all_cues.append(cues)
        
        print(f"    Audio: {dur_str:.1f}s, {len(cues)} cues")
    
    # Generate SRT with clip-duration offsets
    srt_path = os.path.join(WORK_DIR, 'subtitles.srt')
    # For now, use audio durations as first approximation (will be adjusted after clip generation)
    offset = 0.0
    srt_index = 1
    
    with open(srt_path, 'w', encoding='utf-8') as f:
        for slide_cues in all_cues:
            for start, end, text in slide_cues:
                abs_start = offset + start
                abs_end = offset + end
                
                # Split long text into ~22 char chunks
                chunks = split_text_for_srt(text, 22)
                for chunk in chunks:
                    chunk_dur = (abs_end - abs_start) / len(chunks)
                    chunk_end = abs_start + chunk_dur
                    
                    f.write(f"{srt_index}\n")
                    f.write(f"{format_srt_time(abs_start)} --> {format_srt_time(chunk_end)}\n")
                    f.write(f"{chunk}\n\n")
                    
                    srt_index += 1
                    abs_start = chunk_end
            
            offset += audio_durations[len(all_cues) - len(slide_cues)] if slide_cues else 0
    
    # Use the correct offset from the last slide
    offset = 0.0
    srt_index = 1
    slide_offsets = []
    for i, cues in enumerate(all_cues):
        slide_offsets.append(offset)
        offset += audio_durations[i]
    
    # Regenerate SRT with correct offsets
    with open(srt_path, 'w', encoding='utf-8') as f:
        for slide_idx, cues in enumerate(all_cues):
            base_offset = slide_offsets[slide_idx]
            for start, end, text in cues:
                abs_start = base_offset + start
                abs_end = base_offset + end
                chunks = split_text_for_srt(text, 22)
                for chunk in chunks:
                    chunk_dur = (abs_end - abs_start) / len(chunks)
                    chunk_end = abs_start + chunk_dur
                    f.write(f"{srt_index}\n")
                    f.write(f"{format_srt_time(abs_start)} --> {format_srt_time(chunk_end)}\n")
                    f.write(f"{chunk}\n\n")
                    srt_index += 1
                    abs_start = chunk_end
    
    print(f"  SRT generated: {srt_path} ({srt_index - 1} entries)")
    return audio_durations, slide_offsets, all_cues

def split_text_for_srt(text, max_chars=22):
    """Split text into chunks of max_chars each"""
    if len(text) <= max_chars:
        return [text]
    # Simple split - try to break at punctuation
    chunks = []
    remaining = text
    while remaining:
        if len(remaining) <= max_chars:
            chunks.append(remaining)
            break
        # Find break point
        bp = max_chars
        for sep in '\uff0c\u3002\uff1b\uff01\uff1f\u2014,.;!?':
            idx = remaining[:max_chars].rfind(sep)
            if idx > max_chars // 2:
                bp = idx + 1
                break
        chunks.append(remaining[:bp])
        remaining = remaining[bp:]
    return chunks

def format_srt_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    ms = int((s - int(s)) * 1000)
    return f"{h:02d}:{m:02d}:{int(s):02d},{ms:03d}"

# ============ Step 5: Export slides as PNG via win32com ============
def export_slides(pptx_path):
    try:
        from win32com import client
        import pythoncom
    except ImportError:
        print("  win32com not available, trying alternative...")
        return export_slides_fallback(pptx_path)
    
    slides_dir = os.path.join(WORK_DIR, 'slides')
    os.makedirs(slides_dir, exist_ok=True)
    
    print("  Exporting slides via PowerPoint COM...")
    pythoncom.CoInitialize()
    ppt = client.Dispatch('PowerPoint.Application')
    ppt.Visible = 1
    
    pres = ppt.Presentations.Open(pptx_path, True, False, False)
    
    for i in range(1, pres.Slides.Count + 1):
        out_path = os.path.join(slides_dir, f'slide_{i:02d}.png')
        pres.Slides.Item(i).Export(out_path, 'PNG', 1920, 1080)
        print(f"    Slide {i}/{pres.Slides.Count} exported")
    
    pres.Close()
    ppt.Quit()
    pythoncom.CoUninitialize()
    
    print(f"  Slides exported to: {slides_dir}")
    return slides_dir

def export_slides_fallback(pptx_path):
    """Use python-pptx + manual rendering if COM not available"""
    slides_dir = os.path.join(WORK_DIR, 'slides')
    os.makedirs(slides_dir, exist_ok=True)
    
    # Try using LibreOffice if available
    # Fallback: create simple PNGs with PIL
    from PIL import Image, ImageDraw, ImageFont
    import textwrap
    
    print("  Creating slides via PIL fallback...")
    for i in range(TOTAL_SLIDES):
        img = Image.new('RGB', (1920, 1080), color=(13, 17, 23))
        draw = ImageDraw.Draw(img)
        
        try:
            font_large = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 72)
            font_med = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 40)
        except:
            font_large = ImageFont.load_default()
            font_med = ImageFont.load_default()
        
        # Draw accent line
        draw.rectangle([0, 0, 1920, 6], fill=(231, 76, 60))
        
        # Slide number
        draw.text((40, 20), f"Slide {i+1}", fill=(134, 142, 150), font=font_med)
        
        out_path = os.path.join(slides_dir, f'slide_{i+1:02d}.png')
        img.save(out_path)
        print(f"    Slide {i+1} created (placeholder)")
    
    return slides_dir

# ============ Step 6: Assemble video ============
def assemble_video(slides_dir, audio_durations):
    clips_dir = os.path.join(WORK_DIR, 'clips')
    os.makedirs(clips_dir, exist_ok=True)
    
    # Step A: Generate individual clips using -t for exact duration
    clip_durations = []
    for i in range(TOTAL_SLIDES):
        slide_num = i + 1
        slide_png = os.path.join(slides_dir, f'slide_{slide_num:02d}.png')
        audio_mp3 = os.path.join(WORK_DIR, 'audio', f'slide_{slide_num:02d}.mp3')
        clip_mp4 = os.path.join(clips_dir, f'clip_{slide_num:02d}.mp4')
        
        if not os.path.exists(slide_png):
            print(f"  Warning: Slide PNG not found: {slide_png}")
            continue
        
        dur = audio_durations[i]
        print(f"  Clip {slide_num}/{TOTAL_SLIDES}: {dur:.1f}s...")
        
        cmd = [
            FFMPEG, '-y',
            '-loop', '1', '-i', slide_png,
            '-i', audio_mp3,
            '-t', str(dur),  # Exact duration matching audio
            '-vf', 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p',
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
            '-pix_fmt', 'yuv420p', '-r', '24',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-ac', '2',
            clip_mp4
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        # Verify clip duration
        probe = subprocess.run(
            [FFMPEG, '-i', clip_mp4, '-f', 'null', '-'],
            capture_output=True, text=True
        )
        import re
        m = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', probe.stderr)
        clip_dur = float(m.group(1))*3600 + float(m.group(2))*60 + float(m.group(3)) if m else 0
        clip_durations.append(clip_dur)
        print(f"    Video: {clip_dur:.1f}s (audio: {dur:.1f}s)")
    
    # Step B: Create concat list (UTF-8)
    concat_path = os.path.join(WORK_DIR, 'concat_list.txt')
    with open(concat_path, 'w', encoding='utf-8') as f:
        for i in range(TOTAL_SLIDES):
            clip_path = os.path.join(clips_dir, f'clip_{i+1:02d}.mp4')
            # Use forward slashes for ffmpeg
            clip_path_ff = clip_path.replace('\\', '/')
            f.write(f"file '{clip_path_ff}'\n")
    
    # Step C: Merge clips
    merged_path = os.path.join(WORK_DIR, 'video_merged.mp4')
    print(f"  Merging {len(clip_durations)} clips...")
    
    cmd = [
        FFMPEG, '-y', '-f', 'concat', '-safe', '0',
        '-i', concat_path,
        '-c', 'copy',
        merged_path
    ]
    subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    
    # Verify merged duration
    probe = subprocess.run(
        [FFMPEG, '-i', merged_path, '-f', 'null', '-'],
        capture_output=True, text=True
    )
    m = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', probe.stderr)
    total_dur = float(m.group(1))*3600 + float(m.group(2))*60 + float(m.group(3)) if m else 0
    expected = sum(clip_durations)
    print(f"  Merged: {total_dur:.1f}s (expected: {expected:.1f}s)")
    
    # Step D: Regenerate SRT with clip-based offsets
    srt_path = os.path.join(WORK_DIR, 'subtitles.srt')
    # Recalculate slide_offsets using actual clip durations
    slide_offsets = [0.0]
    for d in clip_durations[:-1]:
        slide_offsets.append(slide_offsets[-1] + d)
    
    all_cues = []
    for i in range(TOTAL_SLIDES):
        all_cues.append([])  # We need the original cues from TTS step
    
    # Actually we need the cues from TTS generation - let's regenerate SRT later
    # For now, save the merged video and slide offsets
    
    return merged_path, clip_durations, slide_offsets

# ============ Step 7: Burn subtitles + watermark ============
def burn_subtitles_and_watermark(merged_path, srt_path):
    """Two-step: encode with subtitles, then remux with faststart"""
    tmp_path = os.path.join(WORK_DIR, 'video_tmp.mp4')
    output_path = os.path.join(WORK_DIR, 'video_final.mp4')
    
    # Check if ffmpeg supports fontconfig
    has_fontconfig = False
    ver_check = subprocess.run([FFMPEG, '-version'], capture_output=True, text=True)
    if 'fontconfig' in ver_check.stdout:
        has_fontconfig = True
    
    # Build filter
    vf_parts = []
    
    # Subtitles
    srt_rel = os.path.relpath(srt_path, WORK_DIR).replace('\\', '/')
    vf_parts.append(f"subtitles={srt_rel}:force_style='Fontsize=14,MarginV=2,Alignment=2,Outline=1,Shadow=1'")
    
    # Watermark
    if has_fontconfig:
        wm_filter = f"drawtext=font='{FONT_NAME_DRAWTEXT}':text='{WM_TEXT}':fontsize=22:fontcolor=white@0.5:shadowcolor=black@0.35:shadowx=2:shadowy=2:x=w-tw-28:y=h-th-28"
    else:
        wm_filter = f"drawtext=fontfile=C\\:/Windows/Fonts/simhei.ttf:text='{WM_TEXT}':fontsize=22:fontcolor=white@0.5:x=w-tw-28:y=h-th-28"
    vf_parts.append(wm_filter)
    
    vf_parts.append("format=yuv420p")
    vf = ','.join(vf_parts)
    
    print(f"  Burning subtitles + watermark...")
    print(f"  Filter: {vf[:200]}...")
    
    # Step A: Encode (no faststart)
    cmd_encode = [
        FFMPEG, '-y',
        '-i', merged_path,
        '-vf', vf,
        '-c:v', 'libx264', '-crf', '21', '-preset', 'medium',
        '-c:a', 'aac', '-b:a', '192k',
        tmp_path
    ]
    
    result = subprocess.run(cmd_encode, cwd=WORK_DIR, capture_output=True, text=True, timeout=300)
    if result.returncode != 0:
        print(f"  Encode error: {result.stderr[-500:]}")
        # Try without watermark
        print("  Retrying without watermark...")
        vf_simple = f"subtitles={srt_rel}:force_style='Fontsize=14,MarginV=2,Alignment=2,Outline=1,Shadow=1',format=yuv420p"
        cmd_simple = [
            FFMPEG, '-y',
            '-i', merged_path,
            '-vf', vf_simple,
            '-c:v', 'libx264', '-crf', '21', '-preset', 'medium',
            '-c:a', 'aac', '-b:a', '192k',
            tmp_path
        ]
        result2 = subprocess.run(cmd_simple, cwd=WORK_DIR, capture_output=True, text=True, timeout=300)
        if result2.returncode != 0:
            print(f"  Still failed: {result2.stderr[-300:]}")
            return None
    
    # Step B: Remux with faststart
    cmd_remux = [
        FFMPEG, '-y',
        '-i', tmp_path,
        '-c', 'copy',
        '-movflags', '+faststart',
        output_path
    ]
    subprocess.run(cmd_remux, capture_output=True, text=True, timeout=60)
    
    if os.path.exists(output_path):
        size_mb = os.path.getsize(output_path) / 1024 / 1024
        print(f"  Final video: {size_mb:.1f} MB")
        return output_path
    return None

# ============ Step 8: Validation ============
def validate_video(video_path):
    result = subprocess.run(
        [FFMPEG, '-v', 'error', '-i', video_path, '-f', 'null', '-'],
        capture_output=True, text=True
    )
    if result.stderr.strip():
        print(f"  Validation errors: {result.stderr[:500]}")
        return False
    else:
        print(f"  Validation: OK")
        return True

# ============ Main ============
async def main():
    print("=" * 60)
    print("江西隆莱\u201c12\u00b731\u201d窒息事故培训视频组装")
    print("=" * 60)
    
    # Step 1: Generate PPT JS
    print("\n[Step 1] Generating PPT JS...")
    write_ppt_js()
    
    # Step 2: Create PPTX
    print("\n[Step 2] Creating PPTX...")
    pptx_path = create_pptx()
    
    # Step 3: Narration (embedded in get_narration)
    print("\n[Step 3] Narration script ready")
    
    # Step 4: TTS + initial SRT
    print("\n[Step 4] Generating TTS audio...")
    audio_durations, _, all_cues = await generate_tts_and_srt()
    print(f"  Total audio: {sum(audio_durations):.1f}s")
    
    # Step 5: Export slides
    print("\n[Step 5] Exporting slides...")
    slides_dir = export_slides(pptx_path)
    
    # Step 6: Assemble video clips
    print("\n[Step 6] Assembling video...")
    merged_path, clip_durations, slide_offsets = assemble_video(slides_dir, audio_durations)
    
    # Regenerate SRT with clip-based offsets
    print("\n[Step 6b] Regenerating SRT with clip-based offsets...")
    await regenerate_srt_with_offsets(all_cues, clip_durations)
    
    # Step 7: Burn subtitles + watermark
    print("\n[Step 7] Burning subtitles + watermark...")
    srt_path = os.path.join(WORK_DIR, 'subtitles.srt')
    final_video = burn_subtitles_and_watermark(merged_path, srt_path)
    
    if final_video:
        # Step 8: Validate
        print("\n[Step 8] Validating...")
        validate_video(final_video)
        
        # Step 9: Rename to final name
        final_name = "事故教训中成长-江西隆莱生物制药有限公司\u201c12\u00b731\u201d较大窒息事故调查报告.mp4"
        # Save to the report directory (parent of video_work)
        report_dir = os.path.dirname(WORK_DIR)
        final_path = os.path.join(report_dir, final_name)
        shutil.copy2(final_video, final_path)
        print(f"\n{'='*60}")
        print(f"Final video: {final_path}")
        print(f"Size: {os.path.getsize(final_path)/1024/1024:.1f} MB")
        print(f"{'='*60}")
    else:
        print("\nERROR: Video assembly failed!")

async def regenerate_srt_with_offsets(all_cues, clip_durations):
    """Regenerate SRT using actual clip durations as slide offsets"""
    srt_path = os.path.join(WORK_DIR, 'subtitles.srt')
    
    # Calculate slide offsets from clip durations
    slide_offsets = [0.0]
    for d in clip_durations[:-1]:
        slide_offsets.append(slide_offsets[-1] + d)
    
    srt_index = 1
    with open(srt_path, 'w', encoding='utf-8') as f:
        for slide_idx in range(TOTAL_SLIDES):
            if slide_idx >= len(all_cues):
                break
            cues = all_cues[slide_idx]
            if not cues:
                continue
            base_offset = slide_offsets[slide_idx]
            for start, end, text in cues:
                abs_start = base_offset + start
                abs_end = base_offset + end
                chunks = split_text_for_srt(text, 22)
                for chunk in chunks:
                    chunk_dur = (abs_end - abs_start) / len(chunks) if chunks else (abs_end - abs_start)
                    chunk_end = abs_start + chunk_dur
                    f.write(f"{srt_index}\n")
                    f.write(f"{format_srt_time(abs_start)} --> {format_srt_time(chunk_end)}\n")
                    f.write(f"{chunk}\n\n")
                    srt_index += 1
                    abs_start = chunk_end
    
    print(f"  SRT regenerated: {srt_index - 1} entries, total duration: {slide_offsets[-1] + (clip_durations[-1] if clip_durations else 0):.1f}s")

if __name__ == '__main__':
    asyncio.run(main())
