"""
事故概念示意图生成器
根据事故类型和描述生成 SVG 概念图，用于卡片模板的图片区。

支持类型：
- 泄漏扩散 (gas_leak)
- 气柜失效 (gas_holder)
- 反应失控 (thermal_runaway)
- 爆炸火灾 (explosion_fire)
- 管道隔离失效 (isolation_failure)
- 通用事故 (generic)
"""

import sys, os, json
sys.stdout.reconfigure(encoding="utf-8")

# === SVG Generator per accident type ===

def svg_gas_holder_failure(data):
    """气柜卡顿/倾斜 → 水封失效 → 泄漏扩散 → 火源引爆"""
    return """<svg viewBox="0 0 460 280" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E3F2FD"/><stop offset="100%" stop-color="#BBDEFB"/></linearGradient>
    <linearGradient id="tank" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#90A4AE"/><stop offset="100%" stop-color="#607D8B"/></linearGradient>
    <linearGradient id="gas" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FFCC80"/><stop offset="100%" stop-color="#FF9800"/></linearGradient>
    <linearGradient id="water" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#81D4FA"/><stop offset="100%" stop-color="#0288D1"/></linearGradient>
    <filter id="blur"><feGaussianBlur stdDeviation="2"/></filter>
  </defs>

  <!-- Background -->
  <rect width="460" height="280" fill="url(#sky)" rx="6"/>

  <!-- Ground -->
  <rect x="0" y="230" width="460" height="50" fill="#A5D6A7"/>
  <line x1="0" y1="230" x2="460" y2="230" stroke="#4CAF50" stroke-width="2"/>

  <!-- Gas holder body (tilted) -->
  <g transform="translate(140,85) rotate(5)">
    <!-- Outer shell -->
    <rect x="0" y="0" width="180" height="140" rx="4" fill="url(#tank)" stroke="#37474F" stroke-width="2"/>
    <!-- Bell/top dome (slightly shifted = damaged) -->
    <path d="M-5,-10 Q90,-30 185,-10 L185,0 L-5,0 Z" fill="#546E7A" stroke="#37474F" stroke-width="1.5"/>
    <!-- Water seal ring -->
    <rect x="-3" y="55" width="186" height="8" rx="2" fill="url(#water)" stroke="#0277BD" stroke-width="1"/>
    <!-- Gas inside -->
    <rect x="18" y="18" width="144" height="50" rx="3" fill="url(#gas)" opacity="0.6"/>
    <!-- Damaged seal indicator (X) -->
    <text x="80" y="62" font-size="16" fill="#D50032" font-weight="bold">✕ 水封失效</text>
  </g>

  <!-- Leaking gas cloud -->
  <g filter="url(#blur)" opacity="0.7">
    <ellipse cx="310" cy="180" rx="45" ry="30" fill="#FF9800"/>
    <ellipse cx="350" cy="195" rx="35" ry="22" fill="#FFAB40"/>
    <ellipse cx="280" cy="200" rx="30" ry="20" fill="#FB8C00"/>
    <ellipse cx="390" cy="185" rx="25" ry="18" fill="#FFA726"/>
    <ellipse cx="420" cy="200" rx="30" ry="20" fill="#F57C00"/>
  </g>

  <!-- Wind arrow -->
  <line x1="330" y1="140" x2="430" y2="140" stroke="#666" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="340" y="135" font-size="11" fill="#666">风向 → 扩散至厂外</text>

  <!-- Ignition source -->
  <g transform="translate(430,210)">
    <polygon points="0,-12 -8,8 8,8" fill="#FF1744"/>
    <polygon points="0,-18 -5,-2 5,-2" fill="#FF6D00" opacity="0.7"/>
  </g>
  <text x="420" y="245" font-size="8" fill="#D50032">遇火源</text>

  <!-- Road -->
  <rect x="0" y="248" width="460" height="32" fill="#BDBDBD" opacity="0.5"/>
  <line x1="0" y1="264" x2="460" y2="264" stroke="#FFF" stroke-width="1" stroke-dasharray="10,6"/>
  <text x="340" y="275" font-size="9" fill="#616161">108国道</text>

  <!-- Labels -->
  <text x="8" y="20" font-size="12" font-weight="bold" fill="#37474F">气柜失效 → 泄漏 → 爆燃 示意图</text>
  <text x="208" y="62" font-size="8" fill="#78909C">1#氯乙烯气柜</text>
  <text x="10" y="220" font-size="8" fill="#D50032">泄漏氯乙烯（重于空气）沿地面扩散</text>

  <!-- Distance indicator -->
  <text x="10" y="175" font-size="8" fill="#666">厂区</text>
  <line x1="10" y1="180" x2="10" y2="225" stroke="#999" stroke-dasharray="3,3"/>
  <text x="440" y="175" font-size="8" fill="#666">厂外</text>
</svg>"""

def svg_gas_leak(data):
    """有毒/易燃气体泄漏扩散"""
    return """<svg viewBox="0 0 460 280" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E8EAF6"/><stop offset="100%" stop-color="#C5CAE9"/></linearGradient>
    <filter id="blur"><feGaussianBlur stdDeviation="3"/></filter>
    <marker id="arrow" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#666"/>
    </marker>
  </defs>

  <rect width="460" height="280" fill="url(#sky)" rx="6"/>

  <!-- Ground -->
  <rect x="0" y="240" width="460" height="40" fill="#C8E6C9"/>
  <line x1="0" y1="240" x2="460" y2="240" stroke="#66BB6A" stroke-width="1.5"/>

  <!-- Equipment (simplified pipe/vessel) -->
  <rect x="30" y="140" width="80" height="100" rx="4" fill="#90A4AE" stroke="#455A64" stroke-width="2"/>
  <text x="70" y="195" font-size="9" fill="white" text-anchor="middle">储罐/管道</text>

  <!-- Leak point -->
  <rect x="95" y="165" width="30" height="6" fill="#B0BEC5" stroke="#607D8B" stroke-width="1"/>
  <circle cx="120" cy="168" r="4" fill="#D50032"/>
  <text x="135" y="165" font-size="8" fill="#D50032">泄漏点</text>

  <!-- Gas cloud (heavy gas, along ground) -->
  <g filter="url(#blur)" opacity="0.65">
    <ellipse cx="200" cy="235" rx="60" ry="18" fill="#FF9800"/>
    <ellipse cx="260" cy="228" rx="50" ry="15" fill="#FFA726"/>
    <ellipse cx="320" cy="232" rx="45" ry="14" fill="#FB8C00"/>
    <ellipse cx="380" cy="225" rx="40" ry="12" fill="#F57C00"/>
    <ellipse cx="150" cy="240" rx="35" ry="15" fill="#FFAB40"/>
  </g>

  <!-- Wind arrow -->
  <line x1="180" y1="170" x2="380" y2="170" stroke="#666" stroke-width="2" marker-end="url(#arrow)"/>
  <text x="220" y="165" font-size="9" fill="#666">风向（扩散方向）</text>

  <!-- Ground-level diffusion -->
  <text x="340" y="255" font-size="8" fill="#BF360C">重气沿地面扩散</text>

  <!-- No detection -->
  <g transform="translate(320,120)">
    <rect x="0" y="0" width="100" height="30" rx="4" fill="#FFCDD2" stroke="#EF5350" stroke-width="1"/>
    <text x="50" y="20" font-size="9" fill="#C62828" text-anchor="middle">⚠ 无气体检测报警</text>
  </g>

  <text x="10" y="20" font-size="12" font-weight="bold" fill="#37474F">气体泄漏扩散示意图</text>
</svg>"""

def svg_explosion_fire(data):
    """爆炸/火灾事故"""
    return """<svg viewBox="0 0 460 280" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FFF3E0"/><stop offset="100%" stop-color="#FFE0B2"/></linearGradient>
    <radialGradient id="fire" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#FFEB3B"/><stop offset="40%" stop-color="#FF9800"/><stop offset="100%" stop-color="#F44336"/></radialGradient>
    <filter id="glow"><feGaussianBlur stdDeviation="4"/></filter>
  </defs>

  <rect width="460" height="280" fill="url(#bg)" rx="6"/>

  <!-- Ground -->
  <rect x="0" y="240" width="460" height="40" fill="#BCAAA4"/>

  <!-- Equipment (simplified) -->
  <g transform="translate(30,120)">
    <rect x="0" y="0" width="90" height="120" rx="3" fill="#78909C" stroke="#455A64" stroke-width="1.5"/>
    <rect x="0" y="0" width="90" height="25" rx="3" fill="#546E7A"/>
    <text x="45" y="65" font-size="8" fill="white" text-anchor="middle">反应器/设备</text>
  </g>

  <!-- Explosion center -->
  <g transform="translate(160,170)" filter="url(#glow)">
    <circle cx="0" cy="0" r="45" fill="url(#fire)" opacity="0.8"/>
    <circle cx="0" cy="0" r="25" fill="#FFF59D" opacity="0.9"/>
  </g>

  <!-- Shock wave -->
  <circle cx="160" cy="170" r="70" fill="none" stroke="#FF5722" stroke-width="2" opacity="0.4" stroke-dasharray="8,4"/>
  <circle cx="160" cy="170" r="90" fill="none" stroke="#FF5722" stroke-width="1.5" opacity="0.25" stroke-dasharray="6,6"/>

  <!-- Fire plume -->
  <g filter="url(#glow)" opacity="0.7">
    <ellipse cx="250" cy="140" rx="20" ry="50" fill="#FF6D00"/>
    <ellipse cx="240" cy="120" rx="18" ry="40" fill="#FF9100"/>
    <ellipse cx="260" cy="100" rx="15" ry="35" fill="#FFAB40"/>
    <ellipse cx="250" cy="80" rx="12" ry="25" fill="#FFCC80"/>
  </g>

  <!-- Debris -->
  <rect x="300" y="130" width="8" height="12" rx="1" fill="#607D8B" transform="rotate(30,304,136)" opacity="0.6"/>
  <rect x="340" y="150" width="6" height="10" rx="1" fill="#795548" transform="rotate(-20,343,155)" opacity="0.5"/>
  <circle cx="360" cy="140" r="3" fill="#455A64" opacity="0.5"/>

  <!-- Safety barriers -->
  <g transform="translate(350,180)">
    <rect x="0" y="0" width="80" height="28" rx="4" fill="#FFCDD2" stroke="#EF5350" stroke-width="1"/>
    <text x="40" y="18" font-size="8" fill="#C62828" text-anchor="middle">保护层全部失效</text>
  </g>

  <text x="10" y="20" font-size="12" font-weight="bold" fill="#37474F">爆炸/火灾事故示意图</text>
  <text x="130" y="260" font-size="10" fill="#BF360C" font-weight="bold" text-anchor="middle">爆燃中心</text>
</svg>"""

def svg_isolation_failure(data):
    """管道/设备隔离失效"""
    return """<svg viewBox="0 0 460 280" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg2" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#ECEFF1"/><stop offset="100%" stop-color="#CFD8DC"/></linearGradient>
    <marker id="arrow2" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#666"/></marker>
  </defs>

  <rect width="460" height="280" fill="url(#bg2)" rx="6"/>

  <!-- Main pipe -->
  <rect x="20" y="120" width="420" height="16" rx="3" fill="#90A4AE" stroke="#546E7A" stroke-width="1.5"/>

  <!-- Valve 1 (closed, leaking) -->
  <g transform="translate(150,118)">
    <rect x="-12" y="-8" width="24" height="20" rx="2" fill="#FF8A80" stroke="#D50032" stroke-width="1.5"/>
    <text x="0" y="3" font-size="7" fill="white" text-anchor="middle">阀A</text>
  </g>

  <!-- Valve 2 (closed, leaking) -->
  <g transform="translate(280,118)">
    <rect x="-12" y="-8" width="24" height="20" rx="2" fill="#FF8A80" stroke="#D50032" stroke-width="1.5"/>
    <text x="0" y="3" font-size="7" fill="white" text-anchor="middle">阀B</text>
  </g>

  <!-- Broken flange -->
  <g transform="translate(360,118)">
    <rect x="-8" y="-10" width="16" height="20" rx="2" fill="#FFCDD2" stroke="#D50032" stroke-width="2"/>
    <line x1="-4" y1="-4" x2="4" y2="4" stroke="#D50032" stroke-width="2"/>
    <line x1="4" y1="-4" x2="-4" y2="4" stroke="#D50032" stroke-width="2"/>
  </g>

  <!-- Text: valves leaking -->
  <text x="155" y="102" font-size="8" fill="#D50032" text-anchor="middle">内漏</text>
  <text x="285" y="102" font-size="8" fill="#D50032" text-anchor="middle">内漏</text>

  <!-- Internal flow (false isolation) -->
  <line x1="180" y1="128" x2="270" y2="128" stroke="#D50032" stroke-width="2" stroke-dasharray="4,3"/>

  <!-- Process fluid indicator -->
  <text x="70" y="113" font-size="8" fill="#37474F">工艺流体</text>
  <line x1="80" y1="128" x2="140" y2="128" stroke="#1565C0" stroke-width="2"/>

  <!-- Leak from flange -->
  <g>
    <ellipse cx="390" cy="180" rx="18" ry="12" fill="#FFAB40" opacity="0.6"/>
    <ellipse cx="410" cy="185" rx="14" ry="9" fill="#FF9800" opacity="0.5"/>
    <ellipse cx="370" cy="188" rx="12" ry="8" fill="#FB8C00" opacity="0.5"/>
  </g>
  <path d="M365,130 Q380,150 390,168" fill="none" stroke="#FF9800" stroke-width="2" stroke-dasharray="3,2" opacity="0.6"/>

  <!-- Worker -->
  <g transform="translate(430,130)">
    <circle cx="0" cy="-18" r="6" fill="#FFCCBC"/>
    <rect x="-6" y="-12" width="12" height="18" rx="2" fill="#90A4AE"/>
    <text x="0" y="5" font-size="7" fill="#D50032" text-anchor="middle">无PPE!</text>
  </g>

  <text x="10" y="20" font-size="12" font-weight="bold" fill="#37474F">管道隔离失效示意图</text>
  <text x="120" y="250" font-size="9" fill="#37474F" text-anchor="middle">阀门「假隔离」→ 管内残压/残料 → 开设备即泄漏</text>
  <text x="370" y="260" font-size="8" fill="#D50032" text-anchor="middle">作业人员暴露</text>
</svg>"""

def svg_insulation_fire(data):
    """导热油泄漏 → 保温棉浸渍 → 蓄热自燃"""
    return """<svg viewBox="0 0 460 280" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg5" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FFF8E1"/><stop offset="100%" stop-color="#FFECB3"/></linearGradient>
    <linearGradient id="vessel" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stop-color="#90A4AE"/><stop offset="50%" stop-color="#B0BEC5"/><stop offset="100%" stop-color="#78909C"/></linearGradient>
    <linearGradient id="oil" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FF6F00"/><stop offset="100%" stop-color="#E65100"/></linearGradient>
    <radialGradient id="flame" cx="50%" cy="80%" r="80%"><stop offset="0%" stop-color="#FFEB3B"/><stop offset="30%" stop-color="#FF9800"/><stop offset="70%" stop-color="#F44336"/><stop offset="100%" stop-color="#B71C1C" stop-opacity="0"/></radialGradient>
    <filter id="blur2"><feGaussianBlur stdDeviation="2.5"/></filter>
  </defs>

  <rect width="460" height="280" fill="url(#bg5)" rx="6"/>

  <!-- Title -->
  <text x="230" y="20" font-size="13" font-weight="bold" fill="#37474F" text-anchor="middle">导热油泄漏 → 保温棉浸渍 → 蓄热自燃 示意图</text>

  <!-- === LEFT: Reaction Kettle (R-2702A) === -->
  <g transform="translate(25,55)">
    <!-- Vessel body -->
    <rect x="0" y="0" width="130" height="150" rx="8" fill="url(#vessel)" stroke="#455A64" stroke-width="2"/>
    <!-- Head (top) -->
    <path d="M0,0 Q65,-20 130,0" fill="#546E7A" stroke="#455A64" stroke-width="1.5"/>
    <!-- Bottom head -->
    <path d="M0,150 Q65,170 130,150" fill="#546E7A" stroke="#455A64" stroke-width="1.5"/>
    <text x="65" y="82" font-size="9" fill="white" text-anchor="middle" font-weight="bold">R-2702A 反应釜</text>
    <text x="65" y="94" font-size="7" fill="#CFD8DC" text-anchor="middle">（含物料）</text>

    <!-- Agitator -->
    <line x1="65" y1="-5" x2="65" y2="-25" stroke="#607D8B" stroke-width="3"/>
    <text x="65" y="-30" font-size="6" fill="#607D8B" text-anchor="middle">搅拌</text>

    <!-- === Half-pipe coil on vessel wall (left side) === -->
    <path d="M-8,30 Q-12,35 -8,40" fill="none" stroke="#E65100" stroke-width="2.5" opacity="0.8"/>
    <path d="M-8,55 Q-12,60 -8,65" fill="none" stroke="#E65100" stroke-width="2.5" opacity="0.8"/>
    <path d="M-8,80 Q-12,85 -8,90" fill="none" stroke="#E65100" stroke-width="2.5" opacity="0.8"/>
    <path d="M-8,105 Q-12,110 -8,115" fill="none" stroke="#E65100" stroke-width="2.5" opacity="0.8"/>
    <text x="-10" y="72" font-size="6" fill="#E65100" text-anchor="end">半管（夹套管）</text>

    <!-- === LEAK POINT on half-pipe === -->
    <g transform="translate(-12,80)">
      <circle cx="0" cy="0" r="4" fill="#D50032"/>
      <circle cx="0" cy="0" r="7" fill="none" stroke="#D50032" stroke-width="1" opacity="0.5"/>
      <text x="-5" y="-10" font-size="7" fill="#D50032" font-weight="bold" text-anchor="end">✕ 泄漏点</text>
    </g>

    <!-- === Insulation jacket (around vessel, left side, below leak) === -->
    <g transform="translate(-22,88)">
      <rect x="0" y="0" width="28" height="55" rx="3" fill="#FFCC80" stroke="#E65100" stroke-width="1.5"/>
      <text x="14" y="25" font-size="6" fill="#BF360C" text-anchor="middle" font-weight="bold">保温棉</text>
      <text x="14" y="34" font-size="5" fill="#BF360C" text-anchor="middle">（矿棉/玻璃棉）</text>
      <path d="M8,5 L10,15 M18,5 L16,15 M14,15 L14,25" stroke="#E65100" stroke-width="1" stroke-dasharray="2,1"/>
      <text x="14" y="48" font-size="5" fill="#D50032" text-anchor="middle">灯芯效应→浸渍</text>
    </g>

    <!-- Oil dripping from leak into insulation -->
    <path d="M-12,84 L-14,92 L-10,96" fill="none" stroke="#E65100" stroke-width="1.5" opacity="0.7"/>
    <circle cx="-14" cy="92" r="2" fill="#E65100" opacity="0.6"/>
    <circle cx="-10" cy="96" r="2" fill="#E65100" opacity="0.6"/>

    <!-- === FIRE in insulation (below) === -->
    <g transform="translate(-25,140)">
      <ellipse cx="20" cy="15" rx="18" ry="22" fill="url(#flame)" opacity="0.85" filter="url(#blur2)"/>
      <ellipse cx="20" cy="18" rx="12" ry="16" fill="url(#flame)" opacity="0.7"/>
      <ellipse cx="20" cy="22" rx="7" ry="10" fill="#FFEB3B" opacity="0.6"/>
      <ellipse cx="20" cy="-5" rx="14" ry="10" fill="#9E9E9E" opacity="0.35" filter="url(#blur2)"/>
      <ellipse cx="20" cy="-15" rx="18" ry="12" fill="#BDBDBD" opacity="0.25" filter="url(#blur2)"/>
      <text x="20" y="45" font-size="8" fill="#D50032" font-weight="bold" text-anchor="middle">保温棉着火!</text>
    </g>

    <!-- Temperature label -->
    <g transform="translate(-20,170)">
      <rect x="0" y="0" width="65" height="16" rx="3" fill="#FFCDD2" stroke="#EF5350" stroke-width="0.8"/>
      <text x="32" y="12" font-size="6" fill="#C62828" text-anchor="middle">T = 280~320°C</text>
    </g>
  </g>

  <!-- === MIDDLE: Process chain arrows === -->
  <g transform="translate(170,80)">
    <rect x="0" y="0" width="80" height="30" rx="4" fill="#E3F2FD" stroke="#1565C0" stroke-width="1"/>
    <text x="40" y="13" font-size="7" fill="#1565C0" text-anchor="middle">① 半管泄漏</text>
    <text x="40" y="24" font-size="6" fill="#666" text-anchor="middle">导热油渗出</text>
    <line x1="80" y1="15" x2="100" y2="15" stroke="#1565C0" stroke-width="1.5" marker-end="url(#arrow5)"/>

    <rect x="0" y="45" width="80" height="30" rx="4" fill="#FFF3E0" stroke="#E65100" stroke-width="1"/>
    <text x="40" y="58" font-size="7" fill="#E65100" text-anchor="middle">② 灯芯效应</text>
    <text x="40" y="69" font-size="6" fill="#666" text-anchor="middle">油扩展至巨大表面积</text>
    <line x1="80" y1="60" x2="100" y2="60" stroke="#E65100" stroke-width="1.5" marker-end="url(#arrow5)"/>

    <rect x="0" y="90" width="80" height="30" rx="4" fill="#FCE4EC" stroke="#C62828" stroke-width="1"/>
    <text x="40" y="103" font-size="7" fill="#C62828" text-anchor="middle">③ 氧化蓄热</text>
    <text x="40" y="114" font-size="6" fill="#666" text-anchor="middle">保温层阻碍散热</text>
    <line x1="80" y1="105" x2="100" y2="105" stroke="#C62828" stroke-width="1.5" marker-end="url(#arrow5)"/>

    <rect x="0" y="135" width="80" height="30" rx="4" fill="#FFCDD2" stroke="#D50032" stroke-width="1.5"/>
    <text x="40" y="148" font-size="7" fill="#D50032" text-anchor="middle">④ 超过自燃点</text>
    <text x="40" y="159" font-size="6" fill="#D50032" text-anchor="middle">~350-380°C → 起火!</text>
  </g>

  <defs>
    <marker id="arrow5" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#666"/>
    </marker>
  </defs>

  <!-- === RIGHT: Summary / Key takeaway === -->
  <g transform="translate(290,55)">
    <rect x="0" y="0" width="155" height="170" rx="6" fill="white" stroke="#E65100" stroke-width="1.5" opacity="0.9"/>
    <text x="77" y="16" font-size="9" font-weight="bold" fill="#BF360C" text-anchor="middle">⚠ 蓄热自燃（Self-heating）</text>

    <g transform="translate(15,28)">
      <rect x="0" y="0" width="60" height="40" rx="2" fill="#FFCC80" stroke="#E65100" stroke-width="1" opacity="0.7"/>
      <circle cx="15" cy="12" r="3" fill="#E65100" opacity="0.5"/>
      <circle cx="25" cy="20" r="3" fill="#E65100" opacity="0.5"/>
      <circle cx="35" cy="10" r="3" fill="#E65100" opacity="0.5"/>
      <circle cx="40" cy="25" r="3" fill="#E65100" opacity="0.5"/>
      <circle cx="20" cy="30" r="3" fill="#E65100" opacity="0.5"/>
      <circle cx="45" cy="18" r="2.5" fill="#E65100" opacity="0.4"/>
      <text x="30" y="52" font-size="6" fill="#BF360C" text-anchor="middle">保温棉（多孔结构）</text>

      <path d="M70,10 L75,5 M70,20 L78,15 M70,30 L76,28" stroke="#D50032" stroke-width="1" opacity="0.6"/>
      <text x="80" y="22" font-size="5" fill="#D50032">热量无法散出</text>

      <g transform="translate(0,58)">
        <line x1="0" y1="0" x2="125" y2="0" stroke="#D50032" stroke-width="1.5" stroke-dasharray="4,2"/>
        <text x="62" y="10" font-size="6" fill="#D50032" text-anchor="middle" font-weight="bold">自燃点 ~350-380°C</text>
      </g>
    </g>

    <g transform="translate(10,115)">
      <text x="0" y="0" font-size="7" fill="#37474F">▸ 不是"接触空气就自燃"</text>
      <text x="0" y="14" font-size="7" fill="#37474F">▸ 是"高温+大表面积+绝热"</text>
      <text x="0" y="28" font-size="7" fill="#37474F">▸ 三要素缺一不可</text>
      <text x="0" y="46" font-size="8" fill="#D50032" font-weight="bold">浸渍保温棉必须整体更换！</text>
      <text x="0" y="60" font-size="6" fill="#666">表面擦拭无法清除内部油分</text>
    </g>
  </g>

  <!-- === BOTTOM: Time delay warning === -->
  <g transform="translate(25,235)">
    <rect x="0" y="0" width="410" height="32" rx="4" fill="#FFF3E0" stroke="#E65100" stroke-width="1"/>
    <text x="205" y="14" font-size="8" fill="#BF360C" text-anchor="middle" font-weight="bold">关键教训：20:42 监控已显示明火 → 21:28 对面公司保安报警 → 48分钟延迟</text>
    <text x="205" y="26" font-size="7" fill="#666" text-anchor="middle">保温棉着火初期无明火（仅烟雾），发现时已晚。定期巡检保温层外表是唯一的早期预警手段。</text>
  </g>
</svg>"""

def svg_thermal_runaway(data):
    """反应失控"""
    return """<svg viewBox="0 0 460 280" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg3" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#F3E5F5"/><stop offset="100%" stop-color="#E1BEE7"/></linearGradient>
    <linearGradient id="redhot" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FF1744"/><stop offset="100%" stop-color="#B71C1C"/></linearGradient>
  </defs>

  <rect width="460" height="280" fill="url(#bg3)" rx="6"/>

  <!-- Reactor -->
  <g transform="translate(30,90)">
    <rect x="0" y="0" width="120" height="140" rx="6" fill="#78909C" stroke="#455A64" stroke-width="2"/>
    <rect x="0" y="0" width="120" height="30" rx="6" fill="#546E7A"/>
    <!-- Hot content -->
    <g transform="translate(10,40)">
      <rect x="0" y="0" width="100" height="80" rx="3" fill="url(#redhot)" opacity="0.7"/>
      <text x="50" y="42" font-size="8" fill="white" text-anchor="middle">失控反应</text>
      <text x="50" y="55" font-size="8" fill="#FFCDD2" text-anchor="middle">T↑↑ P↑↑</text>
    </g>
    <!-- Agitator -->
    <line x1="60" y1="0" x2="60" y2="-20" stroke="#607D8B" stroke-width="3"/>
    <text x="60" y="-25" font-size="7" fill="#607D8B" text-anchor="middle">搅拌</text>
  </g>

  <!-- Cooling jacket (failed) -->
  <g transform="translate(165,115)">
    <rect x="0" y="0" width="20" height="90" rx="2" fill="#FFCDD2" stroke="#EF5350" stroke-width="1"/>
    <text x="10" y="48" font-size="6" fill="#C62828" text-anchor="middle" transform="rotate(-90,10,48)">冷却失效</text>
  </g>

  <!-- Pressure relief -->
  <path d="M150,100 L165,85 L175,85" stroke="#FF5722" stroke-width="2" fill="none"/>
  <g transform="translate(170,65)">
    <polygon points="0,0 15,-15 30,0" fill="#FF9800" stroke="#E65100" stroke-width="1"/>
    <text x="15" y="10" font-size="7" fill="#BF360C" text-anchor="middle">泄压</text>
  </g>

  <!-- Gas cloud from relief -->
  <g opacity="0.5">
    <ellipse cx="220" cy="55" rx="30" ry="15" fill="#FF9800"/>
    <ellipse cx="250" cy="48" rx="25" ry="12" fill="#FFB74D"/>
    <ellipse cx="270" cy="52" rx="20" ry="10" fill="#FFCC80"/>
  </g>

  <!-- Temperature/pressure curve -->
  <g transform="translate(250,140)">
    <!-- Axes -->
    <line x1="0" y1="0" x2="0" y2="80" stroke="#666" stroke-width="1"/>
    <line x1="0" y1="80" x2="160" y2="80" stroke="#666" stroke-width="1"/>
    <!-- Curve -->
    <path d="M0,75 Q30,70 50,60 Q70,40 90,20 Q110,5 140,3" fill="none" stroke="#D50032" stroke-width="2.5"/>
    <circle cx="140" cy="3" r="4" fill="#D50032"/>
    <text x="145" y="7" font-size="7" fill="#D50032">失控!</text>
    <!-- Labels -->
    <text x="-15" y="40" font-size="7" fill="#666" transform="rotate(-90,-15,40)">温度/压力</text>
    <text x="80" y="95" font-size="7" fill="#666" text-anchor="middle">时间 →</text>
  </g>

  <text x="10" y="20" font-size="12" font-weight="bold" fill="#37474F">反应失控 / 热失控示意图</text>
  <text x="30" y="260" font-size="8" fill="#607D8B">冷却失效 → 温度压力骤升 → 泄压/破裂 → 泄漏/爆炸</text>
</svg>"""

def svg_spherical_tank_bleve(data):
    """球罐饱和水闪蒸 BLEVE：腐蚀穿透壁厚 → 环缝撕裂 → 球罐解体 → 瞬间闪蒸爆炸"""
    return """<svg viewBox="0 0 460 280" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="skysp" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#E3F2FD"/><stop offset="100%" stop-color="#BBDEFB"/></linearGradient>
    <linearGradient id="steel" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#B0BEC5"/><stop offset="100%" stop-color="#78909C"/></linearGradient>
    <linearGradient id="wat" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#4FC3F7"/><stop offset="100%" stop-color="#0277BD"/></linearGradient>
    <linearGradient id="stm" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FFFFFF"/><stop offset="100%" stop-color="#E0F7FA"/></linearGradient>
    <filter id="blursp"><feGaussianBlur stdDeviation="2.5"/></filter>
    <marker id="arrsp" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#D50032"/></marker>
  </defs>

  <rect width="460" height="280" fill="url(#skysp)" rx="6"/>

  <!-- Title -->
  <text x="8" y="20" font-size="12" font-weight="bold" fill="#37474F">球罐 BLEVE（饱和水闪蒸）机理示意</text>

  <!-- Timeline -->
  <line x1="8" y1="42" x2="452" y2="42" stroke="#90A4AE" stroke-width="1.5"/>
  <circle cx="70" cy="42" r="3.5" fill="#78909C"/><text x="60" y="32" font-size="8" fill="#546E7A" text-anchor="middle">13:30 渗漏</text>
  <circle cx="235" cy="42" r="3.5" fill="#EF6C00"/><text x="225" y="32" font-size="8" fill="#E65100" text-anchor="middle">14:00 扩大</text>
  <circle cx="400" cy="42" r="4" fill="#D50032"/><text x="390" y="32" font-size="8" font-weight="bold" fill="#D50032" text-anchor="middle">15:01 爆炸</text>
  <line x1="70" y1="42" x2="400" y2="42" stroke="#D50032" stroke-width="1.5" stroke-dasharray="5,3" opacity="0.6"/>

  <!-- ═══ Left: spherical tank ═══ -->
  <g transform="translate(15,52)">
    <!-- Tank legs -->
    <line x1="58" y1="172" x2="46" y2="200" stroke="#546E7A" stroke-width="5"/>
    <line x1="142" y1="172" x2="154" y2="200" stroke="#546E7A" stroke-width="5"/>
    <rect x="30" y="198" width="140" height="6" rx="2" fill="#78909C"/>
    <!-- Sphere body -->
    <circle cx="100" cy="120" r="58" fill="url(#steel)" stroke="#455A64" stroke-width="2"/>
    <!-- Steam zone (upper) -->
    <ellipse cx="100" cy="102" rx="46" ry="22" fill="url(#stm)" opacity="0.85"/>
    <text x="100" y="106" font-size="9" fill="#546E7A" text-anchor="middle">蒸汽</text>
    <!-- Water zone (lower) -->
    <path d="M42,120 Q60,160 100,166 Q140,160 158,120 A58,58 0 0 1 42,120 Z" fill="url(#wat)" opacity="0.95"/>
    <text x="100" y="152" font-size="9" fill="#E1F5FE" text-anchor="middle">饱和水 245℃</text>
    <!-- Lower circumferential weld (dashed ellipse) -->
    <ellipse cx="100" cy="158" rx="50" ry="12" fill="none" stroke="#B71C1C" stroke-width="1.2" stroke-dasharray="4,3"/>
    <text x="205" y="150" font-size="7" fill="#B71C1C" text-anchor="end">下环焊缝</text>
    <!-- Crack (X) at north side of lower weld -->
    <g transform="translate(52,152)">
      <line x1="-7" y1="-7" x2="7" y2="7" stroke="#D50032" stroke-width="2.5"/>
      <line x1="-7" y1="7" x2="7" y2="-7" stroke="#D50032" stroke-width="2.5"/>
      <circle r="3" fill="#D50032"/>
    </g>
    <text x="42" y="140" font-size="7" fill="#D50032" font-weight="bold">裂纹穿透</text>
    <!-- Steam jet from leak -->
    <g filter="url(#blursp)" opacity="0.8">
      <ellipse cx="25" cy="168" rx="16" ry="10" fill="#FFFFFF"/>
      <ellipse cx="8" cy="180" rx="13" ry="9" fill="#E0F7FA"/>
      <ellipse cx="18" cy="192" rx="11" ry="8" fill="#FFFFFF"/>
    </g>
    <line x1="50" y1="160" x2="8" y2="182" stroke="#0288D1" stroke-width="1.5" stroke-dasharray="3,2" marker-end="url(#arrsp)"/>
    <text x="8" y="205" font-size="7" fill="#0277BD">蒸汽喷射</text>
  </g>

  <!-- ═══ Right: BLEVE mechanism chain ═══ -->
  <g transform="translate(228,58)">
    <!-- Step 1 -->
    <rect x="0" y="0" width="215" height="38" rx="5" fill="#ECEFF1" stroke="#90A4AE" stroke-width="1"/>
    <circle cx="15" cy="19" r="9" fill="#607D8B"/><text x="15" y="23" font-size="10" fill="white" text-anchor="middle" font-weight="bold">1</text>
    <text x="30" y="17" font-size="9.5" font-weight="bold" fill="#37474F">碱SCC+腐蚀疲劳</text>
    <text x="30" y="30" font-size="8" fill="#607D8B">损伤穿透壁厚 → 下环缝渗漏</text>
    <line x1="108" y1="42" x2="108" y2="52" stroke="#90A4AE" stroke-width="1.5" marker-end="url(#arrsp)"/>
    <!-- Step 2 -->
    <rect x="0" y="55" width="215" height="38" rx="5" fill="#FFF3E0" stroke="#FB8C00" stroke-width="1"/>
    <circle cx="15" cy="74" r="9" fill="#EF6C00"/><text x="15" y="78" font-size="10" fill="white" text-anchor="middle" font-weight="bold">2</text>
    <text x="30" y="72" font-size="9.5" font-weight="bold" fill="#E65100">未处置 · 压力超极限</text>
    <text x="30" y="85" font-size="8" fill="#BF360C">环焊缝整圈快速撕裂</text>
    <line x1="108" y1="97" x2="108" y2="107" stroke="#FB8C00" stroke-width="1.5" marker-end="url(#arrsp)"/>
    <!-- Step 3 -->
    <rect x="0" y="110" width="215" height="38" rx="5" fill="#FFEBEE" stroke="#EF5350" stroke-width="1"/>
    <circle cx="15" cy="129" r="9" fill="#D50032"/><text x="15" y="133" font-size="10" fill="white" text-anchor="middle" font-weight="bold">3</text>
    <text x="30" y="127" font-size="9.5" font-weight="bold" fill="#B71C1C">球罐瞬间解体</text>
    <text x="30" y="140" font-size="8" fill="#C62828">内压骤降至大气压</text>
    <line x1="108" y1="152" x2="108" y2="162" stroke="#EF5350" stroke-width="1.5" marker-end="url(#arrsp)"/>
    <!-- Step 4: flash + blast -->
    <rect x="0" y="165" width="215" height="44" rx="5" fill="#FFCDD2" stroke="#D50032" stroke-width="1.5"/>
    <circle cx="15" cy="187" r="9" fill="#B71C1C"/><text x="15" y="191" font-size="10" fill="white" text-anchor="middle" font-weight="bold">4</text>
    <text x="30" y="184" font-size="9.5" font-weight="bold" fill="#B71C1C">641m³饱和水瞬间闪蒸</text>
    <text x="30" y="197" font-size="8" fill="#C62828">体积膨胀~1000倍 → 冲击波</text>
    <!-- Blast rings -->
    <g opacity="0.7">
      <circle cx="222" cy="187" r="10" fill="none" stroke="#D50032" stroke-width="1.5"/>
      <circle cx="222" cy="187" r="17" fill="none" stroke="#D50032" stroke-width="1.2" opacity="0.7"/>
      <circle cx="222" cy="187" r="24" fill="none" stroke="#D50032" stroke-width="0.8" opacity="0.4"/>
    </g>
  </g>

  <!-- Bottom info bar -->
  <line x1="8" y1="250" x2="452" y2="250" stroke="#B0BEC5" stroke-width="1"/>
  <text x="8" y="266" font-size="9" fill="#455A64">650m³球罐 · 245℃ · 2.2MPa · RH精炼炉动力源</text>
  <text x="452" y="266" font-size="9" fill="#D50032" font-weight="bold" text-anchor="end">残骸飞出2km · 10死84伤</text>
</svg>"""


def svg_thermal_oil_dry_heating(data):
    """电加热导热油炉干烧：联轴器断裂→电机空转→加热未停干烧→加热棒烧毁"""
    return """<svg viewBox="0 0 460 280" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgth" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FFF3E0"/><stop offset="100%" stop-color="#FFE0B2"/></linearGradient>
    <linearGradient id="oil" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FFB74D"/><stop offset="100%" stop-color="#E65100"/></linearGradient>
    <linearGradient id="hot" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FF1744"/><stop offset="100%" stop-color="#B71C1C"/></linearGradient>
    <filter id="blurth"><feGaussianBlur stdDeviation="2"/></filter>
  </defs>

  <rect width="460" height="280" fill="url(#bgth)" rx="6"/>

  <!-- Title -->
  <text x="8" y="20" font-size="12" font-weight="bold" fill="#37474F">电加热导热油炉 干烧 机理示意</text>

  <!-- ═══ Left: 导热油系统简图 ═══ -->
  <g transform="translate(8,38)">
    <!-- 高位膨胀槽 (4楼) -->
    <rect x="8" y="8" width="52" height="34" rx="3" fill="#90A4AE" stroke="#455A64" stroke-width="1.5"/>
    <text x="34" y="22" font-size="7" fill="#FFF" text-anchor="middle">膨胀槽</text>
    <text x="34" y="32" font-size="6" fill="#CFD8DC" text-anchor="middle">高位·液封</text>
    <!-- 主油管（竖） -->
    <line x1="34" y1="42" x2="34" y2="70" stroke="#E65100" stroke-width="3"/>
    <!-- 循环泵 -->
    <circle cx="34" cy="82" r="11" fill="#607D8B" stroke="#37474F" stroke-width="1.5"/>
    <text x="34" y="86" font-size="6" fill="#FFF" text-anchor="middle">循环泵</text>
    <!-- 联轴器断裂 X -->
    <g transform="translate(48,70)">
      <line x1="-6" y1="-6" x2="6" y2="6" stroke="#D50032" stroke-width="2.5"/>
      <line x1="-6" y1="6" x2="6" y2="-6" stroke="#D50032" stroke-width="2.5"/>
    </g>
    <text x="66" y="68" font-size="6.5" fill="#D50032" font-weight="bold">联轴器断裂</text>
    <!-- 油管到电加热炉 -->
    <line x1="45" y1="82" x2="78" y2="82" stroke="#E65100" stroke-width="3"/>
    <!-- 电加热炉（干烧红色） -->
    <rect x="80" y="58" width="46" height="48" rx="3" fill="#78909C" stroke="#455A64" stroke-width="1.5"/>
    <rect x="84" y="78" width="38" height="22" rx="2" fill="url(#hot)" opacity="0.9"/>
    <text x="103" y="92" font-size="7" fill="#FFF" text-anchor="middle" font-weight="bold">干烧!</text>
    <text x="103" y="54" font-size="6.5" fill="#37474F" text-anchor="middle">电加热炉</text>
    <!-- 加热棒烧毁标记 -->
    <text x="134" y="66" font-size="6.5" fill="#D50032" font-weight="bold">加热棒</text>
    <text x="134" y="76" font-size="6.5" fill="#D50032" font-weight="bold">烧毁×4</text>
    <!-- 冒烟 -->
    <g filter="url(#blurth)" opacity="0.8">
      <ellipse cx="103" cy="44" rx="12" ry="7" fill="#B0BEC5"/>
      <ellipse cx="110" cy="36" rx="9" ry="6" fill="#CFD8DC"/>
    </g>
    <text x="112" y="30" font-size="6.5" fill="#546E7A">蓝烟</text>
    <!-- 热用户 -->
    <line x1="126" y1="82" x2="150" y2="82" stroke="#E65100" stroke-width="3"/>
    <rect x="150" y="66" width="40" height="32" rx="3" fill="#B0BEC5" stroke="#546E7A" stroke-width="1.2"/>
    <text x="170" y="84" font-size="6.5" fill="#37474F" text-anchor="middle">造粒机</text>
    <!-- 回路回油 -->
    <path d="M170,98 L170,110 L34,110 L34,93" fill="none" stroke="#E65100" stroke-width="2.5" stroke-dasharray="4,2"/>
  </g>

  <!-- ═══ Middle: 失效链 (右移) ═══ -->
  <g transform="translate(205,42)">
    <!-- Step 1 -->
    <rect x="0" y="0" width="118" height="34" rx="4" fill="#ECEFF1" stroke="#90A4AE" stroke-width="1"/>
    <circle cx="11" cy="17" r="8" fill="#607D8B"/><text x="11" y="20" font-size="8" fill="white" text-anchor="middle" font-weight="bold">1</text>
    <text x="23" y="14" font-size="8" font-weight="bold" fill="#37474F">软连接断裂</text>
    <text x="23" y="26" font-size="6.5" fill="#607D8B">油路停止循环</text>
    <!-- Step 2 -->
    <rect x="0" y="44" width="118" height="34" rx="4" fill="#FFF3E0" stroke="#FB8C00" stroke-width="1"/>
    <circle cx="11" cy="61" r="8" fill="#EF6C00"/><text x="11" y="64" font-size="8" fill="white" text-anchor="middle" font-weight="bold">2</text>
    <text x="23" y="58" font-size="8" font-weight="bold" fill="#E65100">电机空转</text>
    <text x="23" y="70" font-size="6.5" fill="#BF360C">无停机信号→加热未停</text>
    <!-- Step 3 -->
    <rect x="0" y="88" width="118" height="34" rx="4" fill="#FFEBEE" stroke="#EF5350" stroke-width="1"/>
    <circle cx="11" cy="105" r="8" fill="#D50032"/><text x="11" y="108" font-size="8" fill="white" text-anchor="middle" font-weight="bold">3</text>
    <text x="23" y="102" font-size="8" font-weight="bold" fill="#B71C1C">电加热干烧</text>
    <text x="23" y="114" font-size="6.5" fill="#C62828">油温持续升高超自燃点</text>
    <!-- Step 4 -->
    <rect x="0" y="132" width="118" height="34" rx="4" fill="#FFCDD2" stroke="#D50032" stroke-width="1.5"/>
    <circle cx="11" cy="149" r="8" fill="#B71C1C"/><text x="11" y="152" font-size="8" fill="white" text-anchor="middle" font-weight="bold">4</text>
    <text x="23" y="146" font-size="8" font-weight="bold" fill="#B71C1C">加热棒烧毁</text>
    <text x="23" y="158" font-size="6.5" fill="#C62828">渗油冒烟·护板红斑</text>
    <!-- arrows -->
    <line x1="59" y1="36" x2="59" y2="42" stroke="#FB8C00" stroke-width="1.5"/>
    <line x1="59" y1="80" x2="59" y2="86" stroke="#EF5350" stroke-width="1.5"/>
    <line x1="59" y1="124" x2="59" y2="130" stroke="#D50032" stroke-width="1.5"/>
  </g>

  <!-- ═══ Right: 联锁值对比 ═══ -->
  <g transform="translate(333,52)">
    <rect x="0" y="0" width="120" height="150" rx="5" fill="#1A1414" stroke="#D50032" stroke-width="1.2"/>
    <text x="60" y="18" font-size="8.5" font-weight="bold" fill="#FFCDD2" text-anchor="middle">出口压力低联锁</text>
    <!-- 压力标尺 -->
    <line x1="20" y1="38" x2="20" y2="132" stroke="#616161" stroke-width="1.5"/>
    <!-- 40KPa 静压线 -->
    <line x1="14" y1="66" x2="108" y2="66" stroke="#4CAF50" stroke-width="2.5"/>
    <text x="112" y="70" font-size="7.5" fill="#4CAF50" font-weight="bold">40KPa</text>
    <text x="24" y="62" font-size="6.5" fill="#A5D6A7">系统静压（高位差）</text>
    <!-- 10KPa 设定线 -->
    <line x1="14" y1="122" x2="108" y2="122" stroke="#D50032" stroke-width="2.5" stroke-dasharray="5,3"/>
    <text x="112" y="126" font-size="7.5" fill="#FF8A80" font-weight="bold">10KPa</text>
    <text x="24" y="118" font-size="6.5" fill="#FFCDD2">联锁设定值</text>
    <!-- 永不触发箭头 -->
    <path d="M28,122 L28,84" fill="none" stroke="#FFD54F" stroke-width="1.5" stroke-dasharray="3,2" marker-end="url(#arrth)"/>
    <text x="30" y="100" font-size="6.5" fill="#FFD54F" font-weight="bold">泵停压力</text>
    <text x="30" y="110" font-size="6.5" fill="#FFD54F" font-weight="bold">也>10KPa!</text>
    <text x="60" y="146" font-size="7" fill="#FF8A80" text-anchor="middle">保护层永不触发</text>
  </g>

  <defs>
    <marker id="arrth" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto"><path d="M0,0 L8,3 L0,6 Z" fill="#FFD54F"/></marker>
  </defs>

  <!-- Bottom bar -->
  <line x1="8" y1="250" x2="452" y2="250" stroke="#B0BEC5" stroke-width="1"/>
  <text x="8" y="266" font-size="9" fill="#455A64">180kW电加热炉 · LQD-350 · 工作温度300℃ &gt; 闪点186℃</text>
  <text x="452" y="266" font-size="9" fill="#D50032" font-weight="bold" text-anchor="end">损失2.6万 · 隐患S=4（多人重伤/死亡）</text>
</svg>"""


def svg_generic(data):
    """通用安全概念图"""
    title = data.get("accident_title", "事故")[:20]
    return f"""<svg viewBox="0 0 460 280" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg4" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#FFF8E1"/><stop offset="100%" stop-color="#FFECB3"/></linearGradient>
  </defs>

  <rect width="460" height="280" fill="url(#bg4)" rx="6"/>

  <!-- Title -->
  <text x="230" y="40" font-size="14" font-weight="bold" fill="#37474F" text-anchor="middle">事故情景示意</text>
  <text x="230" y="58" font-size="10" fill="#78909C" text-anchor="middle">{title}</text>

  <!-- Swiss cheese model (protection layers) -->
  <!-- Layer 1: Equipment integrity -->
  <g transform="translate(60,90) rotate(-5)">
    <rect x="0" y="0" width="80" height="120" rx="2" fill="#E8EAF6" stroke="#5C6BC0" stroke-width="1.5"/>
    <!-- Hole -->
    <ellipse cx="40" cy="55" rx="12" ry="8" fill="#D50032" opacity="0.4"/>
    <text x="40" y="135" font-size="7" fill="#5C6BC0" text-anchor="middle">设备完整性</text>
  </g>

  <!-- Layer 2: Procedure/Training -->
  <g transform="translate(160,90) rotate(3)">
    <rect x="0" y="0" width="80" height="120" rx="2" fill="#E8F5E9" stroke="#43A047" stroke-width="1.5"/>
    <ellipse cx="35" cy="50" rx="10" ry="7" fill="#D50032" opacity="0.4"/>
    <text x="40" y="135" font-size="7" fill="#43A047" text-anchor="middle">操作规程</text>
  </g>

  <!-- Layer 3: Detection/Monitoring -->
  <g transform="translate(260,90) rotate(-2)">
    <rect x="0" y="0" width="80" height="120" rx="2" fill="#FFF3E0" stroke="#EF6C00" stroke-width="1.5"/>
    <ellipse cx="45" cy="45" rx="9" ry="6" fill="#D50032" opacity="0.4"/>
    <text x="40" y="135" font-size="7" fill="#EF6C00" text-anchor="middle">检测/报警</text>
  </g>

  <!-- Layer 4: Emergency Response -->
  <g transform="translate(360,90) rotate(4)">
    <rect x="0" y="0" width="80" height="120" rx="2" fill="#FCE4EC" stroke="#E91E63" stroke-width="1.5"/>
    <ellipse cx="30" cy="48" rx="11" ry="7" fill="#D50032" opacity="0.4"/>
    <text x="40" y="135" font-size="7" fill="#E91E63" text-anchor="middle">应急响应</text>
  </g>

  <!-- Hazard arrow going through all holes -->
  <line x1="30" y1="75" x2="440" y2="165" stroke="#D50032" stroke-width="2.5" stroke-dasharray="8,4"/>
  <polygon points="440,165 432,158 432,172" fill="#D50032"/>

  <text x="230" y="255" font-size="9" fill="#D50032" font-weight="bold" text-anchor="middle">保护层被逐个击穿 → 事故发生</text>
  <text x="230" y="272" font-size="7" fill="#78909C" text-anchor="middle">（瑞士奶酪模型 / Swiss Cheese Model）</text>
</svg>"""


# === Generator mapping ===
GENERATORS = {
    "gas_leak": svg_gas_leak,
    "gas_holder": svg_gas_holder_failure,
    "explosion_fire": svg_explosion_fire,
    "isolation_failure": svg_isolation_failure,
    "insulation_fire": svg_insulation_fire,
    "thermal_runaway": svg_thermal_runaway,
    "spherical_tank_bleve": svg_spherical_tank_bleve,
    "thermal_oil_dry_heating": svg_thermal_oil_dry_heating,
    "generic": svg_generic,
}


def _generate_concept_diagram_original(data: dict) -> str:
    """
    Generate an SVG concept diagram based on accident data.

    Returns SVG string suitable for embedding in HTML.

    Use data['diagram_type'] to select the diagram type,
    or auto-detect from accident_type field.
    """
    # diagram_type can be at top level or inside image block
    diagram_type = data.get("diagram_type", "") or data.get("image", {}).get("diagram_type", "")

    # Auto-detect from accident_type if not specified
    if not diagram_type:
        atype = (data.get("accident_info", {}).get("type", "") or "").lower()
        title = (data.get("accident_title", "") or "").lower()
        combined = atype + " " + title
        # Chinese keywords
        if "干烧" in combined or "导热油" in combined or "热载体炉" in combined or "dry_heating" in combined:
            diagram_type = "thermal_oil_dry_heating"
        elif "球罐" in combined or "饱和水" in combined or "闪蒸" in combined or "bleve" in combined:
            diagram_type = "spherical_tank_bleve"
        elif "气柜" in combined or "水封" in combined or "gas_holder" in combined:
            diagram_type = "gas_holder"
        elif ("泄漏" in combined and ("爆燃" in combined or "爆炸" in combined or "火灾" in combined)):
            diagram_type = "explosion_fire"
        elif "爆炸" in combined or "火灾" in combined or "explosion" in combined or "fire" in combined:
            diagram_type = "explosion_fire"
        elif "泄漏" in combined or "扩散" in combined or "gas_leak" in combined:
            diagram_type = "gas_leak"
        elif "隔离" in combined or "阀门" in combined or "isolation" in combined:
            diagram_type = "isolation_failure"
        elif "反应" in combined or "失控" in combined or "thermal" in combined or "runaway" in combined:
            diagram_type = "thermal_runaway"
        else:
            diagram_type = "generic"

    gen = GENERATORS.get(diagram_type, svg_generic)
    return gen(data)


# === CLI ===
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", help="JSON data file")
    parser.add_argument("--out", default=None, help="Output SVG path")
    parser.add_argument("--type", default="gas_holder", help="Diagram type")
    args = parser.parse_args()

    if args.data:
        with open(args.data, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"accident_info": {"type": args.type}}

    svg = generate_concept_diagram(data)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"SVG saved: {args.out}")
    else:
        print(svg[:500] + "...")


# === Failure-point annotation layer (v1.6.0 Beacon-style) ===
FAILURE_ANCHORS = {
    "gas_leak": (120, 168, '泄漏点'),
    "gas_holder": (230, 150, '失效点'),
    "explosion_fire": (230, 150, '引燃点'),
    "isolation_failure": (360, 118, '失效点'),
    "insulation_fire": (230, 140, '引燃点'),
    "thermal_runaway": (230, 150, '失控点'),
    "spherical_tank_bleve": (230, 140, '爆裂点'),
    "thermal_oil_dry_heating": (230, 140, '干烧点'),
    "generic": (230, 150, '失效点')
}

def _annotation_svg(cx, cy, label):
    """Red dashed circle + leader line + label, drawn ABOVE content."""
    r = 16
    lx = cx + 28 if cx < 340 else cx - 28
    anchor = "start" if lx > cx else "end"
    return (
        f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#D50032" '
        f'stroke-width="2.5" stroke-dasharray="5,3" opacity="0.95"/>'
        f'<line x1="{cx + r if lx > cx else cx - r}" y1="{cy}" x2="{lx}" y2="{cy}" '
        f'stroke="#D50032" stroke-width="1.5"/>'
        f'<text x="{lx + (4 if lx > cx else -4)}" y="{cy - 6}" font-size="10" '
        f'font-weight="bold" fill="#D50032" text-anchor="{anchor}">{label}</text>'
    )


def generate_concept_diagram(data: dict) -> str:
    diagram = _generate_concept_diagram_original(data)
    # determine diagram_type again for anchor lookup
    dt = data.get("diagram_type", "") or data.get("image", {}).get("diagram_type", "")
    mark = data.get("image", {}).get("mark_point") or {}
    if dt in FAILURE_ANCHORS or mark:
        cx = mark.get("x", FAILURE_ANCHORS.get(dt, (230, 150, "失效点"))[0])
        cy = mark.get("y", FAILURE_ANCHORS.get(dt, (230, 150, "失效点"))[1])
        label = mark.get("label", FAILURE_ANCHORS.get(dt, (230, 150, "失效点"))[2])
        inject = _annotation_svg(int(cx), int(cy), label)
        diagram = diagram.replace("</svg>", inject + "</svg>")
    return diagram
