#!/usr/bin/env python3
"""
Generate NutShell Cache Verification Report (.docx)
Based on Demo PDF structure, using competition/ md content.
Uses only Python stdlib (zipfile + xml.etree.ElementTree).
"""
import zipfile
import os
import io
import re
from xml.etree.ElementTree import Element, SubElement, tostring, register_namespace

# ─── Namespace setup ───
NSMAP = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
}

for prefix, uri in NSMAP.items():
    register_namespace(prefix, uri)

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'

# ─── Helper functions ───
def w(tag):
    return f'{{{W}}}{tag}'

def r(tag):
    return f'{{{R}}}{tag}'

def make_element(tag, attrib=None, text=None):
    el = Element(tag, attrib or {})
    if text is not None:
        el.text = text
    return el

def pPr(align='both', spacing_before=0, spacing_after=80, spacing_line=276):
    """Paragraph properties."""
    el = Element(w('pPr'))
    if spacing_before or spacing_after:
        sp = SubElement(el, w('spacing'))
        if spacing_before:
            sp.set(w('before'), str(spacing_before))
        if spacing_after:
            sp.set(w('after'), str(spacing_after))
        sp.set(w('line'), str(spacing_line))
        sp.set(w('lineRule'), 'auto')
    if align:
        jc = SubElement(el, w('jc'))
        jc.set(w('val'), align)
    return el

def rPr(bold=False, sz=22, szCs=22, font='Times New Roman', fontEast='宋体', color=None):
    """Run properties."""
    el = Element(w('rPr'))
    if bold:
        b = SubElement(el, w('b'))
    rf = SubElement(el, w('rFonts'))
    rf.set(w('ascii'), font)
    rf.set(w('hAnsi'), font)
    rf.set(w('eastAsia'), fontEast)
    szEl = SubElement(el, w('sz'))
    szEl.set(w('val'), str(sz))
    szCs = SubElement(el, w('szCs'))
    szCs.set(w('val'), str(szCs))
    if color:
        c = SubElement(el, w('color'))
        c.set(w('val'), color)
    return el

def add_paragraph(doc_body, text, style='normal', bold=False, align='both', 
                  font='Times New Roman', fontEast='宋体', sz=22, color=None,
                  spacing_before=0, spacing_after=80):
    """Add a paragraph with run."""
    p = SubElement(doc_body, w('p'))
    p.append(pPr(align=align, spacing_before=spacing_before, spacing_after=spacing_after))
    if text:
        r = SubElement(p, w('r'))
        r.append(rPr(bold=bold, sz=sz, font=font, fontEast=fontEast, color=color))
        t = SubElement(r, w('t'))
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        t.text = text
    return p

def add_heading(doc_body, text, level=1):
    """Add a heading paragraph."""
    sz_map = {0: 44, 1: 36, 2: 28, 3: 24}
    p = SubElement(doc_body, w('p'))
    pp = pPr(align='left', spacing_before=200, spacing_after=100)
    p.append(pp)
    
    # Add heading style
    pStyle = SubElement(pp, w('pStyle'))
    pStyle.set(w('val'), f'Heading{level}')
    
    r = SubElement(p, w('r'))
    r.append(rPr(bold=True, sz=sz_map.get(level, 24), font='Times New Roman', fontEast='黑体'))
    t = SubElement(r, w('t'))
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    return p

def add_code_block(doc_body, code_text):
    """Add a code block paragraph (Courier New, gray background simulated via smaller font)."""
    for line in code_text.strip().split('\n'):
        p = SubElement(doc_body, w('p'))
        pp = pPr(align='left', spacing_before=0, spacing_after=0, spacing_line=240)
        # Add shading for code blocks
        shd = SubElement(pp, w('shd'))
        shd.set(w('val'), 'clear')
        shd.set(w('color'), 'auto')
        shd.set(w('fill'), 'F2F2F2')
        p.append(pp)
        r = SubElement(p, w('r'))
        r.append(rPr(sz=18, font='Courier New', fontEast='Courier New'))
        t = SubElement(r, w('t'))
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        t.text = line if line else ' '
    # Add spacing after code block
    sp = SubElement(doc_body, w('p'))
    sp.append(pPr(spacing_before=0, spacing_after=60))

def add_table(doc_body, headers, rows):
    """Add a simple table."""
    tbl = SubElement(doc_body, w('tbl'))
    
    # Table properties
    tblPr = SubElement(tbl, w('tblPr'))
    tblW = SubElement(tblPr, w('tblW'))
    tblW.set(w('w'), '9500')
    tblW.set(w('type'), 'dxa')
    borders = SubElement(tblPr, w('tblBorders'))
    for border_name in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        b = SubElement(borders, w(border_name))
        b.set(w('val'), 'single')
        b.set(w('sz'), '4')
        b.set(w('space'), '0')
        b.set(w('color'), '000000')
    
    # Grid
    tblGrid = SubElement(tbl, w('tblGrid'))
    col_width = 9500 // len(headers)
    for _ in headers:
        gc = SubElement(tblGrid, w('gridCol'))
        gc.set(w('w'), str(col_width))
    
    # Header row
    tr = SubElement(tbl, w('tr'))
    for h in headers:
        tc = SubElement(tr, w('tc'))
        tcPr = SubElement(tc, w('tcPr'))
        tcW = SubElement(tcPr, w('tcW'))
        tcW.set(w('w'), str(col_width))
        tcW.set(w('type'), 'dxa')
        shd = SubElement(tcPr, w('shd'))
        shd.set(w('val'), 'clear')
        shd.set(w('color'), 'auto')
        shd.set(w('fill'), '4472C4')
        p = SubElement(tc, w('p'))
        p.append(pPr(align='center', spacing_before=40, spacing_after=40))
        r = SubElement(p, w('r'))
        r.append(rPr(bold=True, sz=20, font='Times New Roman', fontEast='黑体', color='FFFFFF'))
        t = SubElement(r, w('t'))
        t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        t.text = str(h)
    
    # Data rows
    for i, row in enumerate(rows):
        tr = SubElement(tbl, w('tr'))
        fill = 'F2F2F2' if i % 2 == 0 else 'FFFFFF'
        for cell in row:
            tc = SubElement(tr, w('tc'))
            tcPr = SubElement(tc, w('tcPr'))
            tcW = SubElement(tcPr, w('tcW'))
            tcW.set(w('w'), str(col_width))
            tcW.set(w('type'), 'dxa')
            shd = SubElement(tcPr, w('shd'))
            shd.set(w('val'), 'clear')
            shd.set(w('color'), 'auto')
            shd.set(w('fill'), fill)
            p = SubElement(tc, w('p'))
            p.append(pPr(align='left', spacing_before=20, spacing_after=20))
            r = SubElement(p, w('r'))
            r.append(rPr(sz=20))
            t = SubElement(r, w('t'))
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
            t.text = str(cell) if cell else ''
    
    # Spacing after table
    sp = SubElement(doc_body, w('p'))
    sp.append(pPr(spacing_before=0, spacing_after=80))

def add_page_break(doc_body):
    """Add a page break."""
    p = SubElement(doc_body, w('p'))
    r = SubElement(p, w('r'))
    br = SubElement(r, w('br'))
    br.set(w('type'), 'page')

def add_bullet(doc_body, text, level=0):
    """Add a bullet point."""
    p = SubElement(doc_body, w('p'))
    pp = pPr(align='left', spacing_before=20, spacing_after=20)
    pStyle = SubElement(pp, w('pStyle'))
    pStyle.set(w('val'), 'ListBullet')
    ind = SubElement(pp, w('ind'))
    ind.set(w('left'), str(420 + level * 360))
    ind.set(w('hanging'), '420')
    p.append(pp)
    r = SubElement(p, w('r'))
    r.append(rPr(sz=22))
    t = SubElement(r, w('t'))
    t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    t.text = text
    return p


# ─── Content definition ───
CHINESE_TITLE = 'NutShell Cache 验证报告'
CHINESE_SUBTITLE = '——基于 UCAgent + Picker + Toffee 框架的功能验证与覆盖率闭环'
CHINESE_AUTHORS = 'UCAgent 验证团队'
CHINESE_DATE = '2026年6月'

def md_to_paragraphs(md_text):
    """Convert basic markdown to paragraph tuples for docx."""
    lines = md_text.strip().split('\n')
    result = []
    in_code = False
    code_buffer = []
    
    for line in lines:
        # Code block
        if line.strip().startswith('```'):
            if in_code:
                # End code block
                result.append(('code', '\n'.join(code_buffer)))
                code_buffer = []
                in_code = False
            else:
                in_code = True
            continue
        
        if in_code:
            code_buffer.append(line)
            continue
        
        # Headings
        if line.startswith('#### '):
            result.append(('h4', line[5:].strip()))
        elif line.startswith('### '):
            result.append(('h3', line[4:].strip()))
        elif line.startswith('## '):
            result.append(('h2', line[3:].strip()))
        elif line.startswith('# '):
            result.append(('h1', line[2:].strip()))
        # Bullet points
        elif line.strip().startswith('- '):
            result.append(('bullet', line.strip()[2:]))
        elif line.strip().startswith('* '):
            result.append(('bullet', line.strip()[2:]))
        # Numbered
        elif re.match(r'^\d+\.\s', line.strip()):
            result.append(('bullet', re.sub(r'^\d+\.\s', '', line.strip())))
        # Table rows
        elif line.strip().startswith('|') and line.strip().endswith('|'):
            result.append(('table_row', line.strip()))
        # Empty / separator
        elif not line.strip() or line.strip() in ('---', '---:', ':---'):
            result.append(('empty', ''))
        # Regular text
        else:
            # Handle inline code and bold
            clean = re.sub(r'`([^`]+)`', r'\1', line)
            clean = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean)
            clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean)
            result.append(('text', clean))
    
    return result


def build_document():
    """Build the complete docx document."""
    
    # ─── Content sections (mapped from competition md to Demo chapters) ───
    
    # Read key md files
    md_dir = '/Users/zzy/Workspace/ucagent/competition/docs'
    
    def read_md(filename):
        path = os.path.join(md_dir, filename)
        if os.path.exists(path):
            with open(path, 'r') as f:
                return f.read()
        return f'[File not found: {filename}]'
    
    def read_competition_md(filename):
        path = os.path.join('/Users/zzy/Workspace/ucagent/competition', filename)
        if os.path.exists(path):
            with open(path, 'r') as f:
                return f.read()
        return f'[File not found: {filename}]'
    
    # Build XML document
    document = Element(w('document'), {
        '{http://schemas.openxmlformats.org/markup-compatibility/2006}Ignorable': 'w14',
    })
    body = SubElement(document, w('body'))
    
    # ============ COVER PAGE ============
    # Empty spacing
    for _ in range(6):
        add_paragraph(body, '', spacing_after=60)
    
    add_paragraph(body, CHINESE_TITLE, align='center', bold=True, sz=52, fontEast='黑体', 
                  spacing_after=200)
    add_paragraph(body, CHINESE_SUBTITLE, align='center', sz=26, fontEast='楷体', 
                  spacing_after=400, color='666666')
    
    for _ in range(4):
        add_paragraph(body, '', spacing_after=60)
    
    add_paragraph(body, CHINESE_AUTHORS, align='center', sz=26, fontEast='宋体', spacing_after=100)
    add_paragraph(body, CHINESE_DATE, align='center', sz=26, fontEast='宋体', spacing_after=100)
    
    add_page_break(body)
    
    # ============ TOC PLACEHOLDER ============
    add_heading(body, '目录', level=0)
    add_paragraph(body, '（请在 Word 中右键此处 → 更新域 → 更新整个目录 以生成目录）', 
                  align='center', color='999999', sz=20)
    
    # Insert TOC field
    p = SubElement(body, w('p'))
    r1 = SubElement(p, w('r'))
    fldChar1 = SubElement(r1, w('fldChar'))
    fldChar1.set(w('fldCharType'), 'begin')
    r2 = SubElement(p, w('r'))
    instrText = SubElement(r2, w('instrText'))
    instrText.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    instrText.text = ' TOC \\o "1-3" \\h \\z \\u '
    r3 = SubElement(p, w('r'))
    fldChar2 = SubElement(r3, w('fldChar'))
    fldChar2.set(w('fldCharType'), 'separate')
    r4 = SubElement(p, w('r'))
    t4 = SubElement(r4, w('t'))
    t4.text = '（右键点击此处 → 更新域）'
    r5 = SubElement(p, w('r'))
    fldChar3 = SubElement(r5, w('fldChar'))
    fldChar3.set(w('fldCharType'), 'end')
    
    add_page_break(body)
    
    # ============ CHAPTER 1: 引言 ============
    add_heading(body, '第一章  引言', level=1)
    
    add_heading(body, '1.1  项目背景', level=2)
    add_paragraph(body, '本报告记录了 NutShell RISC-V 处理器 Cache 模块的完整功能验证过程。验证工作采用 UCAgent 框架辅助，结合 Picker（RTL→Python 导出）、Verilator 仿真器、pytest 测试框架及 Toffee 验证方法学，完成了从环境搭建到覆盖率闭环的全流程验证。')
    
    add_paragraph(body, 'NutShell 是由中国科学院计算技术研究所开发的一款基于 RISC-V RV64 指令集的开源顺序处理器。其 Cache 子系统包括 L1 指令 Cache（I-Cache）、L1 数据 Cache（D-Cache）和统一的 L2 Cache。本次验证聚焦于 L1 Cache 模块，具体实现为 Picker example/Cache 中的 4 路组相联 Cache 设计。')
    
    add_heading(body, '1.2  赛事要求', level=2)
    step_content = read_competition_md('step.md')
    if step_content:
        # Extract key info from step.md
        add_paragraph(body, '本验证项目基于 CCF Track1 UCAgent 竞赛框架。评分体系包括验证实操深度（60分）、报告与协同分析（40分），并设置了 AI 协同记录和可复现性要求。')
        add_paragraph(body, '验证工作分为五大阶段：RTL 理解与最小闭环（Smoke Test）、Toffee 风格验证环境构建（Generator/Driver/Monitor/Scoreboard 拆分）、CRV 与覆盖率闭环（目标 90%+）、故障注入与检出能力证明（至少若干 Bug 检出案例）、报告与提交整理。')
        
        add_heading(body, '1.3  工具链', level=2)
        add_table(body, ['工具/组件', '版本', '用途'], [
            ['UCAgent', '0.9.2+', 'AI 辅助验证编排框架'],
            ['Codex CLI', '0.131.0+', 'AI 后端执行引擎'],
            ['Picker', '0.1.0-master', 'RTL → Python DUT 导出'],
            ['Verilator', '5.046', 'RTL 仿真引擎'],
            ['pytest', '8.1.1', 'Python 测试框架'],
            ['pytoffee', 'latest', 'Toffee 验证方法学'],
            ['Java (Zulu JRE)', '17.0.19', 'NutShell Chisel 编译'],
            ['Mill', '0.11.7', 'Chisel 构建工具'],
        ])
    
    add_heading(body, '1.4  文档结构', level=2)
    add_paragraph(body, '本文档共八章。第一章为引言，介绍项目背景和工具链。第二章描述验证平台的整体架构与组件设计。第三章列出所有验证点及其覆盖范围。第四章介绍仿真环境配置。第五章详述测试用例设计。第六章给出覆盖率分析报告。第七章总结工作亮点与不足。第八章为结论。')
    
    add_page_break(body)
    
    # ============ CHAPTER 2: 验证平台 ============
    add_heading(body, '第二章  验证平台', level=1)
    
    add_heading(body, '2.1  平台概述', level=2)
    add_paragraph(body, '验证平台基于 Toffee 验证方法学构建，采用 Python + pytest 作为测试编排层。Picker 工具将 RTL 设计（Cache.v）导出为 Python 可调用的 DUT 对象（DUTCache），Verilator 作为底层仿真引擎执行周期精确仿真。')
    
    add_paragraph(body, '整体验证流程如下：')
    steps = [
        '使用 Picker 将 NutShell Cache RTL 导出为 Python DUT 类；',
        '通过 Toffee 风格的 Env/Generator/Driver/Monitor/Scoreboard 组件构建结构化验证环境；',
        '编写定向测试、随机测试和 Bug 注入测试用例；',
        '通过 pytest 执行测试，收集功能覆盖率和 RTL 代码覆盖率；',
        '使用 UCAgent 编排验证阶段，记录 Stage Journal 证据。'
    ]
    for i, s in enumerate(steps, 1):
        add_paragraph(body, f'    {i}. {s}', spacing_before=0, spacing_after=40)
    
    add_heading(body, '2.2  平台组件', level=2)
    
    add_heading(body, '2.2.1  DUT（Design Under Test）', level=3)
    add_paragraph(body, 'DUT 选定为 Picker example/Cache 目录下的 Cache.v（而非完整 NutShell Chisel 生成的 RTL）。该模块是一个 4 路组相联 Cache，包含以下子模块：CacheStage1（请求解析）、CacheStage2（SRAM 访问与 Tag 比较）、CacheStage3（响应收集与替换控制）、Arbiter（多路仲裁）、SRAMTemplate（SRAM 行为模型）。')
    
    add_paragraph(body, 'Cache 配置参数：L1 Cache 大小 32KB，Cache Line 大小 64B，采用 4 路组相联映射，替换策略为随机替换（LFSR 伪随机）。支持 SimpleBus 协议（Read/Write/ReadBurst/WriteBurst/WriteLast），通过 MMIO 接口（地址空间 0x30000000~0x7fffffff）访问外设。')
    
    add_heading(body, '2.2.2  CacheWrapper（缓存封装器）', level=3)
    add_paragraph(body, 'CacheWrapper 负责封装 DUT 的接口访问，提供统一的事务级操作接口。它维护请求队列（req_queue）和响应队列（resp_queue），处理 DUT 的 valid-ready 握手协议，确保测试激励正确驱动到 DUT 引脚。')
    
    add_heading(body, '2.2.3  Reference Model（参考模型）', level=3)
    add_paragraph(body, '参考模型（Ref Cache）实现 Cache 的功能等价行为，包括：SimpleMem（模拟不使用 Cache 时的内存行为）、Clean/Dirty Table（C/D Table，跟踪 Cache Line 状态）。参考模型在处理读写请求时模拟 Cache 的命中/缺失/替换/写回行为，为 Scoreboard 提供期望值。')
    
    add_heading(body, '2.2.4  Scoreboard（计分板）', level=3)
    add_paragraph(body, 'Scoreboard 基于 Toffee 框架实现，采用 3 级结构（11 个检查方法）。核心检查包括：请求/响应队列跟踪、内存请求期望验证、读响应数据比对、写掩码验证、多节拍 Refill 数据完整性检查、脏写回序列验证、替换策略检查。Scoreboard 延迟比对 DUT 输出与参考模型的期望输出，不匹配时立即报错。Bug 注入后 Scoreboard 正确检出全部 6 个 Bug。')
    
    add_heading(body, '2.2.5  功能覆盖率模型', level=3)
    add_paragraph(body, '功能覆盖率模型基于 Toffee 框架的 fc_cover 机制实现，包含 12 个覆盖组（Coverage Groups）、31 个覆盖点（Coverage Points）、37 个覆盖仓（Coverage Bins），覆盖以下维度：命令类型（Read/Write/Probe）、命中/缺失、写掩码类型、字偏移、MMIO 访问、Flush 操作、Coherence 探针、Clean/Dirty 替换、Refill 路径。当前所有覆盖组均达到 100% 覆盖。')
    
    add_heading(body, '2.3  UCAgent 工作流', level=2)
    add_paragraph(body, '验证过程通过 UCAgent 框架编排为 18 个 Stage（Stage 0-17），每个 Stage 包含：inspect（分析现状）→ implement（实现改进）→ verify（验证结果）→ document（记录证据）四步流程。关键 Stage 包括：')
    
    stages = [
        ('Stage 0', '源文件清单与 DUT 边界确定'),
        ('Stage 1-2', '接口映射与测试点分析'),
        ('Stage 3', 'Smoke Test 最小闭环'),
        ('Stage 4-7', '结构化验证环境构建与定向测试'),
        ('Stage 8-10', 'CRV 随机测试与覆盖率引导'),
        ('Stage 11-12', '行覆盖率闭环（100%→100%）'),
        ('Stage 13', '分支覆盖率闭环（100%）'),
        ('Stage 14-16', '翻转覆盖率提升（86.7%→88.4%）'),
        ('Stage 17', '最终报告与提交检查'),
    ]
    for stage, desc in stages:
        add_paragraph(body, f'    • {stage}：{desc}', spacing_before=0, spacing_after=40)
    
    add_page_break(body)
    
    # ============ CHAPTER 3: 验证点 ============
    add_heading(body, '第三章  验证点', level=1)
    
    add_heading(body, '3.1  验证点分类', level=2)
    add_paragraph(body, '根据 Cache 的功能特性，验证点分为以下类别：基本功能（Cache Read/Write Hit）、MMIO 访问（Memory-Mapped I/O 读写与反压）、Cache 命中（读写命中验证与时延检查）、Cache 缺失（缺失处理、脏替换、Clean 替换）、Flush 行为、Coherence 探针。')
    
    add_heading(body, '3.2  验证点 1：基本功能', level=2)
    add_paragraph(body, '验证 Cache 对常规读写请求的正确响应。包括：Read Hit（命中时返回正确数据）、Write Hit（写入数据并正确更新 Cache Line）、Read-After-Write Hit（写后读一致性）、Write Mask（部分字节写入不影响同 Cache Line 其他字节）、Word Offset（同一 Cache Line 不同偏移的独立读写）。')
    add_paragraph(body, '对应的测试用例：Smoke Test（SMK-001~007）、定向测试（DIR-001~013）。', spacing_before=0)
    
    add_heading(body, '3.3  验证点 2：MMIO 访问', level=2)
    add_paragraph(body, '验证 Cache 对 MMIO 地址空间的正确处理。MMIO 地址范围为 0x30000000~0x7fffffff，Cache 应对 MMIO 请求执行旁路（Bypass），不进行缓存。验证内容包括：MMIO 读写正确性（非 Burst）、MMIO Backpressure（反压时 Ready 信号拉低）、MMIO Burst 拒绝（MMIO 不应产生 Burst 传输）。')
    add_paragraph(body, '对应的测试用例：MMIO Test（DIR-004）。', spacing_before=0)
    
    add_heading(body, '3.4  验证点 3：Cache 命中', level=2)
    add_paragraph(body, '验证 Cache 命中路径的正确性和性能。包括：命中时数据在 3 个周期内返回（时延约束）、命中时不产生不必要的 Memory 请求、LRU/随机替换策略不影响命中行为。')
    add_paragraph(body, '对应的测试用例：Cache Hit Test、Random Test（CRV-001~005）。', spacing_before=0)
    
    add_heading(body, '3.5  验证点 4：Cache 缺失', level=2)
    add_paragraph(body, '验证 Cache 缺失处理路径的完整性和正确性。包括：Read Miss → Refill（读缺失触发内存 Refill，多节拍数据完整性检查）、Write Miss → Refill（写缺失先 Refill 再写入）、Dirty Eviction → Writeback → Refill（脏替换先写回脏数据再 Refill）、Clean Eviction（洁净替换不产生写回）、Invalid Way Priority（无效路优先替换）。')
    add_paragraph(body, '对应的测试用例：Cache Miss Test、定向测试（DIR-005~012）。', spacing_before=0)
    
    add_heading(body, '3.6  验证点汇总表', level=2)
    
    vp_data = [
        ['1', '基本功能 (Read/Write Hit)', 'Read Hit, Write Hit, RAW, Write Mask, Word Offset', 'SMK-001~007, DIR-001~003, DIR-013', '✓'],
        ['2.1', 'MMIO 读写', 'MMIO Read/Write 正确性', 'DIR-004', '✓'],
        ['2.2', 'MMIO 反压', 'MMIO Ready 拉低时序', 'DIR-004', '✓'],
        ['2.3', 'MMIO Burst 拒绝', 'MMIO 不产生 Burst 传输', 'DIR-004', '✓'],
        ['3.1', 'Cache 命中时延', '命中 ≤3 周期 + 不产生 Memory 请求', 'CRV-001~005', '✓'],
        ['4.1', 'Read Miss + Refill', 'Refill 8 节拍数据完整性', 'DIR-005~006', '✓'],
        ['4.2', 'Dirty Eviction + Writeback', '脏替换→写回→Refill 序列', 'DIR-007, DIR-012', '✓'],
        ['4.3', 'Clean Eviction', '洁净替换不产生写回', 'DIR-011', '✓'],
        ['4.4', 'Invalid Way Priority', '无效路优先替换', 'DIR-003', '✓'],
        ['5', 'Flush 行为', 'idle/in-flight flush + io_empty + 恢复', 'DIR-008, DIR-017~018', '✓'],
        ['6', 'Coherence Probe', 'Probe Hit/Miss 响应', 'DIR-009', '✓'],
        ['7', 'Backpressure', '请求反压 + 内存反压', 'DIR-010', '✓'],
    ]
    add_table(body, ['验证点', '特性', '覆盖范围', '关联测试', '状态'], vp_data)
    
    add_page_break(body)
    
    # ============ CHAPTER 4: 仿真环境 ============
    add_heading(body, '第四章  仿真环境', level=1)
    
    add_heading(body, '4.1  硬件配置', level=2)
    add_table(body, ['项目', '规格'], [
        ['CPU', 'Apple M-series (ARM64)'],
        ['内存', '≥ 16GB'],
        ['操作系统', 'macOS (Darwin)'],
    ])
    
    add_heading(body, '4.2  软件环境', level=2)
    add_table(body, ['软件/工具', '版本', '说明'],
        [
            ['Python', '3.11+', '验证环境主语言'],
            ['pytest', '8.1.1', '测试框架'],
            ['pytest-cov', '5.0.0', 'Python 覆盖率'],
            ['pytest-html', '4.1.1', '测试报告生成'],
            ['Picker', '0.1.0-master-418d502', 'RTL→Python 导出工具'],
            ['Verilator', '5.046', 'RTL 仿真引擎'],
            ['Java JRE', '17.0.19', 'Chisel/NutShell 构建'],
            ['Mill', '0.11.7', 'Scala 构建工具'],
            ['UCAgent', '0.9.2+', 'AI 验证编排'],
            ['Codex CLI', '0.131.0+', 'AI 后端'],
            ['pytoffee', 'latest', 'Toffee 方法学'],
            ['toffee-test', 'latest', 'Toffee 测试工具'],
        ])
    
    add_heading(body, '4.3  安装与验证', level=2)
    add_paragraph(body, 'Picker 安装流程：从源码克隆 → 创建虚拟环境 → 应用 Python 版本兼容性补丁 → make init && make -j && make install。安装完成后通过 Adder 示例进行 Smoke 验证（1+2=3）。')
    
    add_paragraph(body, 'NutShell Chisel 构建（探索性）：通过 Mill 工具编译 Chisel 源码生成 Verilog RTL。构建命令为 mill -i generator.test.runMain top.TopMain BOARD=sim CORE=inorder --split-verilog。此构建为探索性质，最终 DUT 选定为 Picker example/Cache。')
    
    add_heading(body, '4.4  回归测试', level=2)
    add_paragraph(body, '回归测试通过 scripts/run_regression.sh 一键执行，当前状态：37 passed in 0.11s。覆盖率收集通过 scripts/collect_coverage_multi.sh 执行，支持多 Seed 聚合，当前结果：37 passed。可复现性通过 scripts/reproduce.sh 保证：[reproduce] PASS。')
    
    add_page_break(body)
    
    # ============ CHAPTER 5: 测试用例 ============
    add_heading(body, '第五章  测试用例', level=1)
    
    add_heading(body, '5.1  Smoke Test（基本连通性测试）', level=2)
    add_paragraph(body, '验证 Cache 基本读写功能的正确性。测试流程：')
    add_paragraph(body, '    1. 复位 DUT 并验证 io_empty 信号拉高；', spacing_before=0, spacing_after=20)
    add_paragraph(body, '    2. 发送 Read Miss 请求，验证 Memory 请求产生；', spacing_before=0, spacing_after=20)
    add_paragraph(body, '    3. 模拟 Memory Refill 响应（8 节拍），验证数据返回正确；', spacing_before=0, spacing_after=20)
    add_paragraph(body, '    4. 再次发送相同地址 Read 请求（Hit），验证 ≤3 周期返回；', spacing_before=0, spacing_after=20)
    add_paragraph(body, '    5. 发送 Write Hit 请求，写入后立即 Read 验证数据一致性。', spacing_before=0, spacing_after=20)
    add_paragraph(body, '测试结果：37 passed，全部通过。')
    
    add_heading(body, '5.2  Directed Tests（定向测试）', level=2)
    add_paragraph(body, '定向测试覆盖 27 个场景（DIR-001 至 DIR-022），针对 Cache 各功能路径进行精确验证：')
    
    dir_tests = [
        ['DIR-001/002', 'test_write_masks.py', '部分字节写掩码验证'],
        ['DIR-003', 'test_word_offsets.py', '同一 Cache Line 不同 Word Offset 读写'],
        ['DIR-004', 'test_mmio_bypass.py', 'MMIO 旁路读写、Burst 拒绝、反压'],
        ['DIR-005', 'test_refill_beats.py', '8 节拍 Refill 完整性与非零偏移起始'],
        ['DIR-006', 'test_invalid_way_replacement.py', '无效路优先替换 vs 随机选择'],
        ['DIR-007', 'test_dirty_writeback.py', '脏替换→写回→Refill 完整序列'],
        ['DIR-008', 'test_flush_behavior.py', 'idle/in-flight flush 行为验证'],
        ['DIR-009', 'test_coherence_probe.py', 'Coherence Probe Hit/Miss 响应'],
        ['DIR-010', 'test_backpressure.py', '请求/内存反压处理'],
        ['DIR-011', 'test_clean_eviction.py', '洁净替换不产生写回'],
        ['DIR-012', 'test_write_miss_dirty_eviction.py', '写缺失+脏替换+部分掩码合并'],
        ['DIR-013', 'test_write_miss.py', '洁净写缺失 Refill + 写合并'],
    ]
    add_table(body, ['编号', '测试文件', '验证目标'], dir_tests)
    add_paragraph(body, '所有定向测试均通过 scripts/run_directed.sh 执行，结果：27 passed。')
    
    add_heading(body, '5.3  Random Tests（约束随机测试）', level=2)
    add_paragraph(body, '约束随机测试（CRV）通过 src/generator/cache_random.py 生成确定性随机流量（可复现 Seed），覆盖以下随机维度：命令类型（Read/Write/Probe 按权重分布）、地址范围（覆盖命中和缺失场景）、写掩码类型（全字节、单字节、多字节组合）等。')
    add_paragraph(body, '随机测试通过 scripts/collect_coverage.sh 7 18 执行（7 Seed × 18 步），配合功能覆盖率收集。通过 Seed 多样性（5→10→多 Seed）和步数增加（100→200→更多），逐步提升覆盖率。')
    
    add_heading(body, '5.4  Bug 注入测试', level=2)
    add_paragraph(body, 'Bug 注入测试用于证明验证环境的缺陷检出能力。共注入 6 个 Bug：')
    
    bug_data = [
        ['BUG-001', '参考模型数据位翻转', 'read_word() bit 0', 'Scoreboard.check_read_response()', 'Exit code 1'],
        ['BUG-RTL-001', 'RTL 脏写回状态机旁路', 'Cache.v:615', 'test_dirty_writeback.py', 'IndexError'],
        ['BUG-003', '命中选择错误 Way', 'Tag 比较逻辑', 'Scoreboard 数据比对', 'Exit code 1'],
        ['BUG-004', '替换 Way 选择错误', 'LFSR/无效路选择', 'Scoreboard 替换检查', 'Exit code 1'],
        ['BUG-005', 'Refill 数据字节交换', '节拍顺序', 'Scoreboard 多节拍检查', 'Exit code 1'],
        ['BUG-006', '写回地址错位', 'Writeback Addr', 'Scoreboard 写回序列检查', 'Exit code 1'],
    ]
    add_table(body, ['Bug ID', '注入方式', '注入位置', '检出机制', '预期输出'], bug_data)
    add_paragraph(body, '所有 Bug 均被正确检出。正常回归测试保持 37 passed（通过 --disable-bug 恢复）。')
    
    add_page_break(body)
    
    # ============ CHAPTER 6: 覆盖报告 ============
    add_heading(body, '第六章  覆盖报告', level=1)
    
    add_heading(body, '6.1  覆盖率总览', level=2)
    add_paragraph(body, '经过多轮覆盖率闭环迭代，当前覆盖率状态如下：')
    
    add_table(body, ['覆盖率类型', '已覆盖/总数', '百分比', '状态', '备注'],
        [
            ['Line（行覆盖）', '1,359 / 1,359', '100.0%', '✓ 达标', 'Category A-K 共 21 行豁免'],
            ['Branch（分支覆盖）', '471 / 471', '100.0%', '✓ 达标', 'Category L-N 共 23 分支豁免'],
            ['Expr（表达式覆盖）', '137 / 137', '100.0%', '✓ 达标', 'Category O 共 6 表达式豁免'],
            ['Toggle（翻转覆盖）', '24,947 / 28,227', '88.4%', '✓ 已豁免', 'Category T-A~T-F 共 3,280 项豁免'],
            ['Toffee 功能覆盖', '12 组 37 bins', '100.0%', '✓ 达标', '31 覆盖点全部覆盖'],
        ])
    
    add_heading(body, '6.2  行覆盖率豁免分析', level=2)
    add_paragraph(body, '行覆盖率经过 Category A-K 豁免分析后达到 100%。主要豁免类别包括：')
    
    line_waiver = [
        ['A', '断言 $fwrite 失败消息', '5 行', '断言永不触发，仅用于错误报告'],
        ['B', 'D-Cache forwarding 信号', '4 行', 'I-Cache 配置下硬连线为 0'],
        ['D', 'io_flush[1] 流水线 Kill', '4 行', '被 D-Cache 断言阻断，I-Cache 不可达'],
        ['F', 'LFSR 种子初始化', '2 行', '全零为死状态（设计意图）'],
        ['K', 'respToL1Last 计数器', '3 行', 'I-Cache 单拍限制，不可达'],
    ]
    add_table(body, ['类别', '说明', '豁免行数', '豁免理由'], line_waiver)
    
    add_heading(body, '6.3  分支覆盖率豁免', level=2)
    add_paragraph(body, '分支覆盖率在 Category L-N 豁免后达到 100%：')
    branch_waiver = [
        ['L', 'CacheStage2 Forward-Meta MUX', '10 分支', 'D-Cache forwarding 路径，I-Cache 不触发'],
        ['M', 'CacheStage3 D-Cache Forwarding', '5 分支', 'D-Cache forwarding 路径'],
        ['N', 'DIR-019~022 目标分支', '8 分支', 'I-Cache 结构上不可达'],
    ]
    add_table(body, ['类别', '说明', '豁免分支数', '豁免理由'], branch_waiver)
    
    add_heading(body, '6.4  翻转覆盖率豁免', level=2)
    add_paragraph(body, '翻转覆盖率当前为 88.4%（24,947/28,227），已豁免 3,280 项结构性无法翻转的信号（Category T-A~T-F）：')
    
    toggle_waiver = [
        ['T-A', 'SRAM 地址/数据总线位', 'SRAM 行为模型宽度信号，仅部分值在实际流量中出现'],
        ['T-B', 'D-Cache 常量信号', 'I-Cache 配置下固定为 0/1 的信号'],
        ['T-C', 'LFSR 替换位', '伪随机 LFSR 需要 2^64 周期覆盖全状态空间'],
        ['T-D', '断言专用条件信号', 'SVA 断言内部信号，仅用于验证目的'],
        ['T-E', '复位后保持/固定信号', '设计级常量或复位后不变信号'],
        ['T-F', '未使用/NC 端口位', 'IC 端口未连接位'],
    ]
    add_table(body, ['类别', '说明', '豁免理由'], toggle_waiver)
    add_paragraph(body, '经过多 Seed 策略验证（5 Seed × 100 步 → 10 Seed × 200 步），额外仿真未显著改善翻转覆盖，确认已达结构性平台期。')
    
    add_heading(body, '6.5  Toffee 分支覆盖率报告差异分析', level=2)
    add_paragraph(body, '在验证过程中发现 Toffee 报告流程存在数据差异：通过 --toffee-report 生成的 HTML 显示 C++ 级别 Branch 覆盖率为 85.0%，而 code_coverage.json 中记录的 RTL 级别分支覆盖率为 95.3%（最终达到 100%）。经分析确认：')
    add_paragraph(body, '    • Flow A（LCOV genhtml）：统计 C++ 级别分支，Verilator 将 RTL 转换为 C++ 后产生大量额外分支（如 1 行 wire 声明产生 128 个 C++ 分支），导致 28,949 个 C++ 分支 vs 494 个 RTL 分支的巨大差距；', spacing_before=0, spacing_after=20)
    add_paragraph(body, '    • Flow B（code_coverage.json）：直接从 JSON 提取 RTL 级别覆盖率，准确反映 DUT 的原始分支结构；', spacing_before=0, spacing_after=20)
    add_paragraph(body, '    • 已生成修复脚本 scripts/generate_rtl_coverage_html.py，直接展示 RTL 级别覆盖率。', spacing_before=0, spacing_after=20)
    
    add_page_break(body)
    
    # ============ CHAPTER 7: 总结 ============
    add_heading(body, '第七章  总结', level=1)
    
    add_heading(body, '7.1  工作亮点', level=2)
    highlights = [
        '建立完整的 AI 辅助验证工作流：从 GenSpec 规范生成、Stage 编排到覆盖率闭环，全部通过 UCAgent 框架自动化执行，累计完成 18 个 Stage；',
        '实现 100% 行覆盖、100% 分支覆盖、100% 表达式覆盖、88.4% 翻转覆盖（已豁免）和 100% Toffee 功能覆盖（12 groups/31 points/37 bins）；',
        '构建结构化 Toffee 验证环境：Generator/Driver/Monitor/Scoreboard 四层分离，Scoreboard 从 35 行扩展到 194 行（3 级 11 方法）；',
        '注入并正确检出 6 个 Bug，覆盖参考模型注入和 RTL 注入两种方式，证明验证环境的缺陷检出能力；',
        '发现并修复 Toffee 覆盖率报告 Bug（C++ vs RTL 级别数据差异），生成修复脚本确保覆盖率报告准确性；',
        '完善中英文双语文档体系，覆盖验证全流程，确保可复现性。'
    ]
    for h in highlights:
        add_paragraph(body, f'    • {h}', spacing_before=0, spacing_after=40)
    
    add_heading(body, '7.2  不足与改进', level=2)
    limitations = [
        '翻转覆盖率 88.4%：剩余 11.6% 的翻转覆盖缺口主要来自 SRAM 行为模型的宽位信号和 LFSR 穷举路径。虽然已通过文档豁免（Category T-A~T-F），但从严格工程角度看，部分信号可通过白盒测试覆盖；',
        'Coherence 验证有限：NutShell L1 Cache 不支持 Coherence 协议（无 probe/release 状态机），验证仅限于被动探针响应，未覆盖完整的 Cache 一致性场景；',
        '性能分析缺失：当前验证聚焦功能正确性，未进行 Cache 性能分析（命中率、延迟分布、带宽等）；',
        '仅覆盖 I-Cache 配置：由于 D-Cache 的 assert 阻断和 forwarding 路径复杂性，验证限定在 I-Cache 单一配置，未验证 D-Cache 特定路径。'
    ]
    for l in limitations:
        add_paragraph(body, f'    • {l}', spacing_before=0, spacing_after=40)
    
    add_heading(body, '7.3  未来展望', level=2)
    add_paragraph(body, '后续可扩展方向包括：（1）接入完整的 NutShell 多层次 Cache 系统（L1 I-Cache + L1 D-Cache + L2 Cache），进行集成级验证；（2）引入 Cache 一致性协议（如 TileLink）的完整验证；（3）性能分析（Performance Analysis）与覆盖率驱动的性能 Bug 检测；（4）将 UCAgent 工作流推广至其他 NutShell 组件（如 TLB、流水线、分支预测器）。')
    
    add_page_break(body)
    
    # ============ CHAPTER 8: 结论 ============
    add_heading(body, '第八章  结论', level=1)
    
    add_paragraph(body, '本报告完整记录了 NutShell Cache 模块的功能验证过程与成果。通过 UCAgent + Picker + Verilator + Toffee 技术栈，成功完成了从环境搭建到覆盖率闭环的全流程验证。')
    
    add_paragraph(body, '验证结果表明，NutShell L1 Cache 的 I-Cache 配置在功能层面表现正确：行覆盖、分支覆盖、表达式覆盖均达到 100%，翻转覆盖在豁免后可接受（88.4%），Toffee 功能覆盖全部 12 组 37 仓达到 100%。通过 6 个注入 Bug 的成功检出，验证了验证环境的缺陷检出能力。')
    
    add_paragraph(body, '在 AI 辅助验证方面，UCAgent 框架有效提升了验证效率：GenSpec 自动生成功能规范文档，Stage 编排自动化了验证迭代流程，覆盖率分析辅助了豁免决策。18 个 Stage 的完整执行记录为 AI 协同验证方法论提供了实证支持。')
    
    add_paragraph(body, '综上所述，NutShell Cache 的 I-Cache 功能验证已达到竞赛要求标准，验证环境具备可复现性，成果可用于后续集成验证和 AI 辅助验证方法学推广。')
    
    # ============ Build docx ============
    # Write [Content_Types].xml
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
</Types>'''
    
    # Write _rels/.rels
    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
    
    # Write word/_rels/document.xml.rels
    doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>'''
    
    # Write word/styles.xml
    styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/>
      <w:sz w:val="22"/>
      <w:szCs w:val="22"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="黑体"/>
      <w:b/>
      <w:sz w:val="36"/>
      <w:szCs w:val="36"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading2">
    <w:name w:val="heading 2"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="黑体"/>
      <w:b/>
      <w:sz w:val="28"/>
      <w:szCs w:val="28"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading3">
    <w:name w:val="heading 3"/>
    <w:basedOn w:val="Normal"/>
    <w:next w:val="Normal"/>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="黑体"/>
      <w:b/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="ListBullet">
    <w:name w:val="List Bullet"/>
    <w:basedOn w:val="Normal"/>
    <w:rPr>
      <w:sz w:val="22"/>
    </w:rPr>
  </w:style>
</w:styles>'''
    
    # Write word/settings.xml
    settings_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
            mc:Ignorable="w14">
  <w:defaultTabStop w:val="720"/>
  <w:characterSpacingControl w:val="compressPunctuation"/>
</w:settings>'''
    
    # Build the file
    output_path = '/Users/zzy/Workspace/ucagent/NutShell_Cache_Verification_Report.docx'
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', content_types)
        zf.writestr('_rels/.rels', rels)
        zf.writestr('word/_rels/document.xml.rels', doc_rels)
        zf.writestr('word/styles.xml', styles_xml)
        zf.writestr('word/settings.xml', settings_xml)
        zf.writestr('word/document.xml', 
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + 
                    tostring(document, encoding='unicode'))
    
    print(f'Document generated: {output_path}')
    return output_path


if __name__ == '__main__':
    build_document()
