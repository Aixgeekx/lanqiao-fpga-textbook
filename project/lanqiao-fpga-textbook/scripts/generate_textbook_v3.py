#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蓝桥杯FPGA开发教程 - 详细代码注释版 + 目录页码索引 + 美化排版
作者: Aix，极道工作室
"""

import os
import re
import gc
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor, black, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Preformatted, KeepTogether, Flowable, Image as RLImage
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image as PILImage
try:
    import fitz
except ImportError:
    fitz = None

# ==================== 颜色主题 ====================
C = {
    'primary':    HexColor('#1a365d'),   # 深蓝主色
    'secondary':  HexColor('#2b6cb0'),   # 中蓝
    'accent':     HexColor('#3182ce'),   # 亮蓝
    'light_bg':   HexColor('#ebf8ff'),   # 浅蓝背景
    'card_bg':    HexColor('#f7fafc'),   # 卡片背景
    'border':     HexColor('#bee3f8'),   # 边框蓝
    'text':       HexColor('#1a202c'),   # 正文黑
    'text_light': HexColor('#4a5568'),   # 副文灰
    'muted':      HexColor('#a0aec0'),   # 淡灰
    'warn_bg':    HexColor('#fffff0'),   # 警告黄背景
    'warn_border':HexColor('#ecc94b'),   # 警告黄边框
    'code_bg':    HexColor('#2d3748'),   # 代码深色背景
    'code_fg':    HexColor('#e2e8f0'),   # 代码前景色
    'comment_fg': HexColor('#63b3ed'),   # 注释蓝色
}

# ==================== 字体注册 ====================
def register_fonts():
    font_dir = "E:/素材/字体/font"
    for name, file in [("MapleMono", "MapleMono-NF-CN-Medium.ttf"),
                        ("MapleMono-Italic", "MapleMono-NF-CN-MediumItalic.ttf")]:
        p = os.path.join(font_dir, file)
        if os.path.exists(p):
            pdfmetrics.registerFont(TTFont(name, p))
    for path, name in [("C:/Windows/Fonts/simhei.ttf", "SimHei"),
                        ("C:/Windows/Fonts/msyh.ttc", "MSYH")]:
        if os.path.exists(path):
            try:
                idx = 0 if path.endswith('.ttc') else None
                pdfmetrics.registerFont(TTFont(name, path, subfontIndex=idx) if idx is not None else TTFont(name, path))
            except: pass

# ==================== 目录页码追踪 ====================
class ChapterMarker(Flowable):
    """插入章节标记，用于记录页码"""
    def __init__(self, key, chapter_map):
        Flowable.__init__(self)
        self.key = key
        self.chapter_map = chapter_map
        self.width = 0
        self.height = 0
    def draw(self):
        self.chapter_map[self.key] = self.canv.getPageNumber()

chapter_pages = {}  # 全局页码记录
table_counter = 0   # 表格编号计数器
figure_counter = 0  # 图片编号计数器

# ==================== 样式定义 ====================
def S():
    s = {}
    # 封面
    s['cover_title'] = ParagraphStyle('CT', fontName='SimHei', fontSize=32, leading=44, alignment=TA_CENTER, textColor=C['primary'])
    s['cover_sub'] = ParagraphStyle('CS', fontName='SimHei', fontSize=22, leading=30, alignment=TA_CENTER, textColor=C['secondary'])
    s['cover_info'] = ParagraphStyle('CI', fontName='MSYH', fontSize=11, alignment=TA_CENTER, textColor=C['text_light'])
    # 章节标题
    s['ch_title'] = ParagraphStyle('CHT', fontName='SimHei', fontSize=22, leading=30, textColor=C['primary'], spaceBefore=5*mm, spaceAfter=3*mm)
    s['sec_title'] = ParagraphStyle('ST', fontName='SimHei', fontSize=13, leading=18, textColor=C['secondary'], spaceBefore=6*mm, spaceAfter=2*mm)
    s['sub_title'] = ParagraphStyle('SUB', fontName='SimHei', fontSize=10.5, leading=15, textColor=HexColor('#2c5282'), spaceBefore=4*mm, spaceAfter=1.5*mm)
    # 正文
    s['body'] = ParagraphStyle('BD', fontName='MSYH', fontSize=9, leading=14, textColor=C['text'], spaceAfter=2*mm)
    # 文件标题
    s['file_title'] = ParagraphStyle('FT', fontName='SimHei', fontSize=11, leading=15, textColor=white, backColor=C['secondary'], borderPadding=7, spaceBefore=6*mm, spaceAfter=2*mm)
    # 描述框
    s['desc_box'] = ParagraphStyle('DB', fontName='MSYH', fontSize=8.5, leading=13, textColor=C['text'], backColor=C['card_bg'], borderWidth=1, borderColor=C['border'], borderPadding=8, spaceAfter=2*mm)
    # 注释框
    s['comment'] = ParagraphStyle('CM', fontName='MSYH', fontSize=8, leading=12, textColor=HexColor('#2c5282'), backColor=C['light_bg'], borderWidth=0, borderPadding=6, spaceAfter=2*mm, leftIndent=8)
    # 提示框
    s['tip'] = ParagraphStyle('TP', fontName='MSYH', fontSize=8, leading=12, textColor=HexColor('#744210'), backColor=C['warn_bg'], borderWidth=1, borderColor=C['warn_border'], borderPadding=6, spaceAfter=3*mm)
    # 代码
    s['code'] = ParagraphStyle('CD', fontName='MapleMono-Italic', fontSize=6.5, leading=8.5, spaceAfter=0, spaceBefore=0, textColor=HexColor('#1a202c'))
    # 表格
    s['th'] = ParagraphStyle('TH', fontName='SimHei', fontSize=8, textColor=white, alignment=TA_CENTER)
    s['td'] = ParagraphStyle('TD', fontName='MSYH', fontSize=7.5, textColor=C['text'], alignment=TA_CENTER)
    s['td_l'] = ParagraphStyle('TDL', fontName='MSYH', fontSize=7.5, textColor=C['text'], alignment=TA_LEFT)
    s['caption'] = ParagraphStyle('CAP', fontName='MSYH', fontSize=7.5, leading=10, textColor=C['text_light'], alignment=TA_CENTER, spaceBefore=1*mm, spaceAfter=1.5*mm)
    s['quote'] = ParagraphStyle('QT', fontName='MSYH', fontSize=9, leading=14, textColor=C['text'], backColor=HexColor('#f8fafc'), borderWidth=1, borderColor=C['border'], borderPadding=8, leftIndent=4*mm, rightIndent=4*mm, spaceAfter=3*mm)
    s['manual'] = ParagraphStyle('MAN', fontName='SimHei', fontSize=10, leading=15, textColor=C['primary'], backColor=C['light_bg'], borderWidth=1, borderColor=C['border'], borderPadding=7, spaceBefore=1.5*mm, spaceAfter=1.5*mm)
    # 目录
    s['toc_title'] = ParagraphStyle('TOCT', fontName='SimHei', fontSize=22, alignment=TA_CENTER, textColor=C['primary'], spaceBefore=8*mm, spaceAfter=8*mm)
    s['toc_ch'] = ParagraphStyle('TOCCH', fontName='SimHei', fontSize=11, textColor=C['primary'], spaceBefore=4*mm, spaceAfter=1*mm)
    s['toc_entry'] = ParagraphStyle('TOCE', fontName='MSYH', fontSize=9, textColor=C['text_light'], leftIndent=8*mm)
    s['toc_page'] = ParagraphStyle('TOCP', fontName='MSYH', fontSize=9, textColor=C['text_light'], alignment=TA_RIGHT)
    # 图表编号
    s['table_caption'] = ParagraphStyle('TCAP', fontName='MSYH', fontSize=8, leading=11, textColor=C['text_light'], alignment=TA_CENTER, spaceBefore=1*mm, spaceAfter=2*mm)
    s['figure_caption'] = ParagraphStyle('FCAP', fontName='MSYH', fontSize=8, leading=11, textColor=C['text_light'], alignment=TA_CENTER, spaceBefore=1*mm, spaceAfter=2*mm)
    return s

# ==================== 图表编号函数 ====================
def next_table_num():
    global table_counter
    table_counter += 1
    return table_counter

def next_figure_num():
    global figure_counter
    figure_counter += 1
    return figure_counter

def table_caption(st, text):
    """生成带编号的表格标题"""
    num = next_table_num()
    return Paragraph(f"表 {num}  {text}", st['table_caption'])

def figure_caption(st, text):
    """生成带编号的图片标题"""
    num = next_figure_num()
    return Paragraph(f"图 {num}  {text}", st['figure_caption'])

# ==================== 装饰元素 ====================
class DecorLine(Flowable):
    """水平装饰线"""
    def __init__(self, width=16*cm, color=C['secondary'], thickness=1.5):
        Flowable.__init__(self)
        self.width = width
        self.height = 3*mm
        self.color = color
        self.thickness = thickness
    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, 1.5*mm, self.width, 1.5*mm)

class ColorBar(Flowable):
    """彩色装饰条"""
    def __init__(self, width=16*cm, height=2*mm, colors=None):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.colors = colors or [C['primary'], C['secondary'], C['accent']]
    def draw(self):
        seg = self.width / len(self.colors)
        for i, c in enumerate(self.colors):
            self.canv.setFillColor(c)
            self.canv.rect(i*seg, 0, seg+1, self.height, fill=1, stroke=0)

class ChapterSideBar(Flowable):
    """章节标题左侧彩色竖条装饰"""
    def __init__(self, height=10*mm, width=3*mm, color=None):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.color = color or C['primary']
    def draw(self):
        self.canv.setFillColor(self.color)
        self.canv.roundRect(0, 0, self.width, self.height, 1, fill=1, stroke=0)

class CoverFrame(Flowable):
    """封面装饰边框"""
    def __init__(self, width=16*cm, height=22*cm):
        Flowable.__init__(self)
        self.width = width
        self.height = height
    def draw(self):
        c = self.canv
        # 外框
        c.setStrokeColor(C['secondary'])
        c.setLineWidth(2)
        c.roundRect(0, 0, self.width, self.height, 3, fill=0, stroke=1)
        # 内框
        c.setStrokeColor(C['accent'])
        c.setLineWidth(0.5)
        c.roundRect(3*mm, 3*mm, self.width-6*mm, self.height-6*mm, 2, fill=0, stroke=1)
        # 四角装饰
        for x, y in [(2*mm, 2*mm), (self.width-5*mm, 2*mm), (2*mm, self.height-5*mm), (self.width-5*mm, self.height-5*mm)]:
            c.setFillColor(C['primary'])
            c.rect(x, y, 3*mm, 3*mm, fill=1, stroke=0)

# ==================== 页眉页脚 ====================
total_pages = 0  # 全局总页数，由第一遍构建后设置

def header_footer(canvas, doc):
    canvas.saveState()
    # 页眉装饰线
    canvas.setStrokeColor(C['secondary'])
    canvas.setLineWidth(2)
    canvas.line(2*cm, A4[1]-1.4*cm, A4[0]-2*cm, A4[1]-1.4*cm)
    # 页眉文字
    canvas.setFont("SimHei", 8)
    canvas.setFillColor(C['primary'])
    canvas.drawString(2*cm, A4[1]-1.2*cm, "蓝桥杯FPGA开发教程")
    canvas.setFont("MSYH", 7)
    canvas.setFillColor(C['muted'])
    canvas.drawRightString(A4[0]-2*cm, A4[1]-1.2*cm, "Aix · 极道工作室")
    # 页脚
    canvas.setStrokeColor(C['border'])
    canvas.setLineWidth(0.8)
    canvas.line(2*cm, 2*cm, A4[0]-2*cm, 2*cm)
    # 页码居中（含总页数）
    canvas.setFont("SimHei", 9)
    canvas.setFillColor(C['secondary'])
    total_str = f" / {total_pages}" if total_pages else ""
    canvas.drawCentredString(A4[0]/2, 1.4*cm, f"— {doc.page}{total_str} —")
    canvas.restoreState()

def cover_header_footer(canvas, doc):
    """封面页无页眉页脚"""
    pass

# ==================== 读取Verilog文件 ====================
MODULE_ORDER = {
    'driver': [
        'key_ctrl.v', 'led_display.v', 'frequency_driver.v', 'iic_drive.v',
        'adc_ctrl.v', 'dac_ctrl.v', 'eeprom_read_ctrl.v', 'eeprom_write_ctrl.v',
        'uart_tx.v', 'uart_rx.v', 'spi_master.v', 'ds1302_wr_drive.v',
        'ds1302_io_convert.v', 'sram_ctrl.v', 'w25q128_ctrl.v', 'seg_driver.v'
    ],
    'user': [
        'led_proc.v', 'key_proc.v', 'uart_parser.v', 'uart_string_sender.v',
        'seg_proc.v', 'ds1302_test.v', 'top_board.v', 'top.v'
    ],
}

def read_verilog(folder):
    files = []
    folder_key = os.path.basename(folder).lower()
    order = {name: idx for idx, name in enumerate(MODULE_ORDER.get(folder_key, []))}
    names = sorted(os.listdir(folder), key=lambda name: (order.get(name, 999), name))
    for f in names:
        if f.endswith('.v'):
            with open(os.path.join(folder, f), 'r', encoding='utf-8') as fh:
                files.append((f, fh.read()))
    return files

def get_module_desc(fname):
    d = {
        'key_ctrl.v': '按键消抖与边沿检测', 'led_display.v': 'LED显示取反驱动',
        'iic_drive.v': 'I2C底层多字节读写驱动', 'eeprom_read_ctrl.v': 'AT24C02 EEPROM读控制',
        'adc_ctrl.v': 'ADC081C021 ADC读取控制', 'dac_ctrl.v': 'DAC5571 DAC写入控制',
        'eeprom_write_ctrl.v': 'AT24C02 EEPROM写控制', 'uart_tx.v': 'UART串口发送模块',
        'uart_rx.v': 'UART串口接收模块', 'spi_master.v': 'SPI主控模块',
        'ds1302_wr_drive.v': 'DS1302 RTC完整读写控制', 'ds1302_io_convert.v': 'DS1302 IO与数据转换',
        'sram_ctrl.v': 'IS63WV1288 SRAM控制器', 'w25q128_ctrl.v': 'W25Q128 Flash控制器',
        'seg_driver.v': '数码管段码与位选驱动', 'frequency_driver.v': '通用分频器',
        'led_proc.v': 'LED模式控制逻辑', 'key_proc.v': '按键处理与模式切换',
        'uart_parser.v': 'UART数据解析状态机', 'uart_string_sender.v': 'UART字符串批量发送',
        'seg_proc.v': '数码管动态扫描处理', 'ds1302_test.v': 'DS1302 RTC测试控制',
        'top_board.v': '板级顶层引脚映射', 'top.v': '系统顶层功能集成',
    }
    return d.get(fname, 'Verilog模块')

# ==================== 封面 ====================
def build_cover(st):
    story = []
    story.append(Spacer(1, 1*cm))
    story.append(CoverFrame())
    story.append(Spacer(1, 1.5*cm))
    story.append(ColorBar(colors=[C['primary'], C['secondary'], C['accent'], C['secondary'], C['primary']]))
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph("极道工作室  出品", st['cover_info']))
    story.append(Spacer(1, 2*cm))
    # 主标题
    story.append(Paragraph("蓝桥杯 FPGA", st['cover_title']))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph("赛场手册与开发教程", st['cover_sub']))
    story.append(Spacer(1, 8*mm))
    story.append(ColorBar(width=8*cm, colors=[C['accent'], C['secondary'], C['accent']]))
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("纸质速查 · 零基础教学 · 出版预备版", ParagraphStyle('VT', fontName='MSYH', fontSize=13, alignment=TA_CENTER, textColor=C['text_light'])))
    story.append(Spacer(1, 1.5*cm))
    # 信息框
    box = ParagraphStyle('BOX', fontName='MSYH', fontSize=10, alignment=TA_CENTER, textColor=C['text'],
                         backColor=C['card_bg'], borderWidth=1.5, borderColor=C['border'], borderPadding=14, spaceAfter=3*mm)
    story.append(Paragraph("作者：Aix，极道工作室", box))
    story.append(Paragraph("极道工作室  ·  JIDAO STUDIO", st['cover_info']))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("基于 DP2026 竞赛实训平台", st['cover_info']))
    story.append(Paragraph("CT137X 开发板 · Xilinx Spartan-7 XC7S6", st['cover_info']))
    story.append(Spacer(1, 2*cm))
    story.append(ColorBar(colors=[C['primary'], C['secondary'], C['accent'], C['secondary'], C['primary']]))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("V3.0 · 2026年5月", ParagraphStyle('V3', fontName='MSYH', fontSize=9, alignment=TA_CENTER, textColor=C['muted'])))
    story.append(PageBreak())
    return story

def build_front_matter(st):
    story = []
    story.append(ChapterMarker("front", chapter_pages))
    story.append(Spacer(1, 1.2*cm))
    story.append(Paragraph("出版说明", st['ch_title']))
    story.append(DecorLine())
    story.append(Paragraph("本书定位为蓝桥杯FPGA赛场纸质使用手册与零基础教学教程。纸质手册要求“翻得快、查得准、能落地”，教学教程要求“讲清原理、给出路径、让初学者能独立复现”。因此本书采用两层结构：前部给出速查卡和硬件事实，正文解释协议、状态机和外设时序，后部保留完整代码和题面。", st['quote']))
    story.append(Paragraph("作者署名：Aix，极道工作室。当前版本为出版预备稿，后续会继续整理题面版权说明、图表编号、参考文献、页眉页脚规范和印刷版封面。", st['body']))
    story.append(Paragraph("纸质使用建议", st['sec_title']))
    guide = [
        [Paragraph("场景", st['th']), Paragraph("优先翻阅位置", st['th']), Paragraph("原因", st['th'])],
        [Paragraph("忘记引脚", st['td']), Paragraph("第一章硬件表、第二章XDC、附录官方依据", st['td']), Paragraph("赛场最常见错误是端口名、电平和引脚不一致。", st['td_l'])],
        [Paragraph("协议不会写", st['td']), Paragraph("第三章I2C/UART/SPI、第四章对应驱动", st['td']), Paragraph("先理解时序规则，再照驱动模板改参数。", st['td_l'])],
        [Paragraph("综合题卡住", st['td']), Paragraph("第三章国赛算法拆解、第五章top结构", st['td']), Paragraph("按采集、存储、计算、显示、上报拆模块。", st['td_l'])],
        [Paragraph("硬件现象异常", st['td']), Paragraph("赛场速查卡、附录、电源/复位/消抖说明", st['td']), Paragraph("先排查极性、复位、时钟域和外设忙状态。", st['td_l'])],
    ]
    t = Table(guide, colWidths=[3*cm, 5.2*cm, 6.8*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(table_caption(st, "纸质使用建议"))
    story.append(t)

    story.append(Paragraph("零基础14天学习路线", st['sec_title']))
    route = [
        [Paragraph("阶段", st['th']), Paragraph("目标", st['th']), Paragraph("必须完成的手上动作", st['th'])],
        [Paragraph("D1-D2", st['td']), Paragraph("认识CT137X硬件和XDC", st['td_l']), Paragraph("点亮LED、让数码管显示固定数字，确认低有效极性。", st['td_l'])],
        [Paragraph("D3-D4", st['td']), Paragraph("掌握时钟、复位、按键消抖", st['td_l']), Paragraph("写一个按键加减计数器，观察一次按键只触发一次。", st['td_l'])],
        [Paragraph("D5-D6", st['td']), Paragraph("掌握状态机和动态扫描", st['td_l']), Paragraph("用三段式状态机控制LED模式，并把状态显示到数码管。", st['td_l'])],
        [Paragraph("D7-D9", st['td']), Paragraph("学习UART、I2C、SPI", st['td_l']), Paragraph("串口发字符串；读ADC；理解DS1302/W25Q128命令帧。", st['td_l'])],
        [Paragraph("D10-D12", st['td']), Paragraph("做综合题拆分", st['td_l']), Paragraph("把题目拆成采集、存储、计算、显示、上报五层模块。", st['td_l'])],
        [Paragraph("D13-D14", st['td']), Paragraph("赛前压测和错题复盘", st['td_l']), Paragraph("按本书题面限时训练，记录错误原因和对应知识点。", st['td_l'])],
    ]
    t = Table(route, colWidths=[2.2*cm, 4.4*cm, 8.4*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "零基础14天学习路线"))
    story.append(t)

    story.append(PageBreak())
    story.append(Paragraph("考场时间分配与提交包检查", st['sec_title']))
    story.append(Paragraph("蓝桥杯FPGA题目的难点不只在知识点，也在时间管理。初学者常见问题是前面调界面花太久，最后没有时间压测、保存和打包。下面两张表建议直接贴便签：一张管时间，一张管最后提交的ZIP压缩包。", st['body']))
    time_plan = [
        [Paragraph("时间段", st['th']), Paragraph("主要动作", st['th']), Paragraph("产出物", st['th'])],
        [Paragraph("0-15min", st['td']), Paragraph("通读题面，圈出输入、输出、计时、显示、通信和存储要求", st['td_l']), Paragraph("模块拆分草图和端口清单", st['td_l'])],
        [Paragraph("15-35min", st['td']), Paragraph("建立工程、加入XDC、写顶层端口和基础LED/数码管自检", st['td_l']), Paragraph("可综合、可下载的空框架", st['td_l'])],
        [Paragraph("35-95min", st['td']), Paragraph("先实现确定性模块：按键、计数器、显示、UART或I2C底层驱动", st['td_l']), Paragraph("每个模块都有板上可观察现象", st['td_l'])],
        [Paragraph("95-150min", st['td']), Paragraph("连接业务状态机，完成题目核心流程，保留调试LED或串口输出", st['td_l']), Paragraph("主功能闭环跑通", st['td_l'])],
        [Paragraph("150-190min", st['td']), Paragraph("处理边界：复位、最大/最小值、按键连按、通信忙状态、显示格式", st['td_l']), Paragraph("关键边界不出错", st['td_l'])],
        [Paragraph("最后20min", st['td']), Paragraph("重新生成bit，按比赛要求压缩工程包，上传前本地解压抽检", st['td_l']), Paragraph("最终ZIP提交包", st['td_l'])],
    ]
    t = Table(time_plan, colWidths=[2.4*cm, 7.4*cm, 5.2*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "考场时间分配建议"))
    story.append(t)

    zip_checks = [
        [Paragraph("检查项", st['th']), Paragraph("要求", st['th']), Paragraph("为什么要查", st['th'])],
        [Paragraph("格式", st['td']), Paragraph("发行版和提交包统一使用标准.zip格式", st['td_l']), Paragraph("Windows可直接打开，GitHub发布和比赛系统兼容性最好。", st['td_l'])],
        [Paragraph("文件名", st['td']), Paragraph("比赛提交包按赛题命名；发布包用版本号，如v0.2.2.zip", st['td_l']), Paragraph("便于评测端识别，也便于自己回溯版本。", st['td_l'])],
        [Paragraph("内容", st['td']), Paragraph("提交包按赛题包含工程；发布包包含PDF、MD、脚本、源码、题面和硬件资料索引", st['td_l']), Paragraph("不要把临时缓存、旧bit、无关个人文件混入最终包。", st['td_l'])],
        [Paragraph("路径", st['td']), Paragraph("压缩包内使用相对路径，避免只在本机有效的绝对路径", st['td_l']), Paragraph("换电脑或评测环境后仍能解压阅读。", st['td_l'])],
        [Paragraph("抽检", st['td']), Paragraph("上传前另建临时目录解压一次，确认PDF可打开、工程可识别、脚本可运行", st['td_l']), Paragraph("压缩成功不等于内容完整，最后一步必须抽检。", st['td_l'])],
    ]
    t = Table(zip_checks, colWidths=[2.5*cm, 7.1*cm, 5.4*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "ZIP压缩包检查单"))
    story.append(t)
    story.append(PageBreak())

    story.append(Paragraph("赛场速查卡", st['ch_title']))
    story.append(DecorLine())
    cards = [
        ("一页判断工程方向", "先确定顶层端口和XDC一致，再确认复位极性、LED/数码管低有效、时钟50MHz。功能拆成输入采样、状态机控制、数据存储、算法计算、显示输出五层。"),
        ("按键", "机械抖动按10ms到20ms处理。低有效按键先同步再消抖，只给业务逻辑一个单周期脉冲，不要把物理按键直接接状态跳转。"),
        ("UART", "115200/8N1：空闲高、起始位低、8位数据低位先发、停止位高。50MHz下每位约434个时钟，接收要在位中心采样。"),
        ("I2C", "SCL高时SDA稳定；SCL低时改变SDA。START是SCL高时SDA下降，STOP是SCL高时SDA上升。地址后第9拍看ACK。"),
        ("SPI", "CS选中器件，SCLK给节拍，MOSI发，MISO收。先确认CPOL/CPHA，再确认MSB first还是LSB first。DS1302是三线类SPI。"),
        ("数码管", "共阳极低有效。段选决定显示数字，位选决定哪一位亮。约1kHz切位，先关位选再换段码，避免重影。"),
        ("Flash", "W25Q128写/擦除前发0x06写使能。页编程0x02，扇区擦除0x20，操作后轮询0x05状态寄存器WIP。"),
        ("SRAM", "异步并口存储。写：地址和数据先稳定，再拉WE。读：地址稳定后拉OE，等待访问时间再采样数据。"),
    ]
    card_data = []
    for i in range(0, len(cards), 2):
        row = []
        for title, body in cards[i:i+2]:
            row.append(Paragraph(f"<b>{title}</b><br/>{body}", st['manual']))
        card_data.append(row)
    t = Table(card_data, colWidths=[7.5*cm, 7.5*cm])
    t.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('LEFTPADDING', (0,0), (-1,-1), 3),
                           ('RIGHTPADDING', (0,0), (-1,-1), 3), ('TOPPADDING', (0,0), (-1,-1), 3),
                           ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "赛场速查卡"))
    story.append(t)
    story.append(PageBreak())

    story.append(Paragraph("赛场上板调试清单", st['ch_title']))
    story.append(DecorLine())
    story.append(Paragraph("纸质手册最重要的价值，是在板子现象不对时快速缩小问题范围。调试时不要同时怀疑所有模块，按“工程能否生成bit、管脚是否正确、基础IO是否正常、外设握手是否成立、业务状态机是否走到目标状态”的顺序排查。每一步都要让板上有可观察输出，例如LED、数码管、串口日志或ILA波形。", st['quote']))
    checks = [
        [Paragraph("阶段", st['th']), Paragraph("必须确认", st['th']), Paragraph("失败时先查", st['th'])],
        [Paragraph("1. 综合前", st['td']), Paragraph("顶层模块名、端口名、文件加入工程、Verilog语法均正确", st['td_l']), Paragraph("端口拼写、未保存文件、重复模块名、中文路径或非法字符", st['td_l'])],
        [Paragraph("2. 约束", st['td']), Paragraph("每个顶层IO都有XDC管脚和IOSTANDARD LVCMOS33", st['td_l']), Paragraph("端口名大小写、引脚表版本、复位和按键有效电平", st['td_l'])],
        [Paragraph("3. 实现", st['td']), Paragraph("无多驱动、无锁存器警告、时钟来自50MHz主时钟", st['td_l']), Paragraph("同一reg被多个always赋值、组合always缺默认值、派生时钟乱用", st['td_l'])],
        [Paragraph("4. 下载", st['td']), Paragraph("bitstream可生成，Hardware Manager能识别器件并完成Program", st['td_l']), Paragraph("JTAG线、电源、驱动、开发板模式、电缆连接", st['td_l'])],
        [Paragraph("5. 基础IO", st['td']), Paragraph("LED流水、按键脉冲、数码管固定数字均可独立工作", st['td_l']), Paragraph("低有效极性、消抖、位选段选顺序、复位释放", st['td_l'])],
        [Paragraph("6. 外设", st['td']), Paragraph("I2C有ACK、SPI有片选和时钟、UART能收发已知字符串", st['td_l']), Paragraph("上拉、片选极性、CPOL/CPHA、波特率计数、三态方向", st['td_l'])],
        [Paragraph("7. 综合题", st['td']), Paragraph("输入采样、状态机、存储、算法、显示、串口分层验证", st['td_l']), Paragraph("先看状态编号，再看计数器边界，最后看数据格式化", st['td_l'])],
    ]
    t = Table(checks, colWidths=[2.5*cm, 6.2*cm, 6.3*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "赛场上板七步调试清单"))
    story.append(t)

    story.append(Paragraph("常见板上现象排查表", st['sec_title']))
    faults = [
        [Paragraph("现象", st['th']), Paragraph("高概率原因", st['th']), Paragraph("定位动作", st['th'])],
        [Paragraph("LED全灭或全亮", st['td']), Paragraph("低有效极性写反、复位未释放、XDC端口错", st['td_l']), Paragraph("先写固定8'h55/8'haa测试，再核对CT137X引脚表。", st['td_l'])],
        [Paragraph("数码管乱码/重影", st['td']), Paragraph("段码表不匹配、位选低有效、切位时未先关位", st['td_l']), Paragraph("只点亮一位显示8，再逐位扫描，确认COM和SEG顺序。", st['td_l'])],
        [Paragraph("按键按一次跳多次", st['td']), Paragraph("没有消抖或直接用物理按键驱动状态机", st['td_l']), Paragraph("观察消抖后单周期脉冲，确认业务逻辑只接debounced_pulse。", st['td_l'])],
        [Paragraph("I2C无ACK", st['td']), Paragraph("地址错、SDA方向没释放、SCL/SDA引脚反、总线缺上拉", st['td_l']), Paragraph("先扫地址或读已知器件，确认第9拍SDA被从机拉低。", st['td_l'])],
        [Paragraph("UART乱码", st['td']), Paragraph("波特率计数不准、收发线接反、数据位顺序或停止位错误", st['td_l']), Paragraph("先发送固定字符串，核对115200/8N1和50MHz计数值434。", st['td_l'])],
        [Paragraph("SPI读回全FF/全00", st['td']), Paragraph("CS未选中、CPOL/CPHA错、MISO未采样、Flash仍忙", st['td_l']), Paragraph("先读W25Q128 JEDEC ID 0x9F，再轮询状态寄存器WIP。", st['td_l'])],
        [Paragraph("仿真正常板上偶发死机", st['td']), Paragraph("跨时钟域亚稳态、异步输入未同步、计数器边界遗漏", st['td_l']), Paragraph("给外部输入加两级同步器，状态跳转条件全部打一拍观察。", st['td_l'])],
    ]
    t = Table(faults, colWidths=[3.3*cm, 5.6*cm, 6.1*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "常见板上现象排查表"))
    story.append(t)

    flow_block = [
        Paragraph("上板故障定位流程", st['sec_title']),
        Paragraph("板上现象不对时，先按可观察层级排查，不要直接改业务代码。每一步只验证一个问题：工程能不能下载、基础IO能不能独立工作、协议握手是否成立、状态机是否走到目标状态。这样能把“看起来全错”的系统拆成几个可证明的小问题。", st['body'])
    ]
    flow = [
        [Paragraph("观察到的现象", st['th']), Paragraph("先判断什么", st['th']), Paragraph("下一步动作", st['th'])],
        [Paragraph("bit生成失败", st['td']), Paragraph("综合/实现阶段是否已经报错或严重警告", st['td_l']), Paragraph("先修multiple drivers、latch inferred、端口未连接和位宽问题，不上板调业务。", st['td_l'])],
        [Paragraph("下载失败", st['td']), Paragraph("硬件管理器是否识别器件，JTAG和电源是否正常", st['td_l']), Paragraph("换USB口、重新上电、检查开发板模式和线缆；确认后再看代码。", st['td_l'])],
        [Paragraph("LED固定测试失败", st['td']), Paragraph("XDC端口名、管脚号、低有效极性是否正确", st['td_l']), Paragraph("用8'h55和8'haa交替测试，先证明板级输出路径正确。", st['td_l'])],
        [Paragraph("按键触发异常", st['td']), Paragraph("物理按键是否低有效，消抖后是否只有一个脉冲", st['td_l']), Paragraph("把消抖脉冲接到LED观察，再接入状态机。", st['td_l'])],
        [Paragraph("数码管异常", st['td']), Paragraph("段选、位选、小数点和刷新顺序是否匹配SEG_TABLE", st['td_l']), Paragraph("先固定只亮一位，再逐位扫描，不要同时调显示格式和业务数据。", st['td_l'])],
        [Paragraph("协议外设无响应", st['td']), Paragraph("I2C ACK、SPI CS/SCLK、UART波特率是否可单独观测", st['td_l']), Paragraph("先跑最小读ID或固定字符串测试，再接入题目流程。", st['td_l'])],
        [Paragraph("业务状态不走", st['td']), Paragraph("当前状态编号、关键计数器和done/busy信号是否符合预期", st['td_l']), Paragraph("把state低位、busy、done映射到LED或串口日志，先定位停在哪个条件。", st['td_l'])],
        [Paragraph("偶发死机", st['td']), Paragraph("异步输入、跨时钟域、复位释放和计数边界是否安全", st['td_l']), Paragraph("外部输入先两级同步，复位统一释放，所有计数器检查N-1边界。", st['td_l'])],
    ]
    t = Table(flow, colWidths=[3.1*cm, 5.8*cm, 6.1*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    flow_block.extend([table_caption(st, "上板故障定位流程"), t])
    story.append(KeepTogether(flow_block))

    story.append(Paragraph("调试信号分配建议", st['sub_title']))
    probes = [
        [Paragraph("信号", st['th']), Paragraph("建议含义", st['th']), Paragraph("用途", st['th'])],
        [Paragraph("LD1", st['td']), Paragraph("1Hz心跳", st['td_l']), Paragraph("证明时钟和复位释放正常。", st['td_l'])],
        [Paragraph("LD2", st['td']), Paragraph("按键消抖脉冲", st['td_l']), Paragraph("确认一次按键只产生一次业务触发。", st['td_l'])],
        [Paragraph("LD3-LD5", st['td']), Paragraph("state[2:0]", st['td_l']), Paragraph("快速判断状态机停在哪个状态。", st['td_l'])],
        [Paragraph("LD6", st['td']), Paragraph("peripheral_busy", st['td_l']), Paragraph("判断I2C/SPI/UART是否卡在忙状态。", st['td_l'])],
        [Paragraph("LD7", st['td']), Paragraph("error_flag", st['td_l']), Paragraph("显示阈值、超时、协议无ACK等异常。", st['td_l'])],
        [Paragraph("LD8", st['td']), Paragraph("done_flag", st['td_l']), Paragraph("证明一次计算或发送流程已经闭环。", st['td_l'])],
    ]
    t = Table(probes, colWidths=[2.5*cm, 4.4*cm, 8.1*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "调试信号分配建议"))
    story.append(t)
    story.append(PageBreak())

    story.append(Paragraph("Verilog综合规则与赛场写法清单", st['ch_title']))
    story.append(DecorLine())
    story.append(Paragraph("初学者写Verilog时，最容易把它当成C语言顺序程序。赛场上必须记住：能下载到FPGA里的不是“语句”，而是由语句描述出的触发器、组合逻辑、存储器和连线。下面这页用于快速判断代码是否适合综合，以及报错时该先改哪里。", st['quote']))
    synth = [
        [Paragraph("写法", st['th']), Paragraph("综合含义", st['th']), Paragraph("赛场建议", st['th'])],
        [Paragraph("wire", st['td']), Paragraph("连续连线，通常由assign或模块输出驱动", st['td_l']), Paragraph("组合表达式和子模块输出优先用wire。", st['td_l'])],
        [Paragraph("reg", st['td']), Paragraph("在always块中被赋值的信号，不一定都是触发器", st['td_l']), Paragraph("时序always里的reg多为触发器；组合always里的reg只是组合逻辑临时量。", st['td_l'])],
        [Paragraph("assign", st['td']), Paragraph("连续赋值，右侧变化会立刻反映到左侧", st['td_l']), Paragraph("简单组合逻辑用assign，避免写多余always。", st['td_l'])],
        [Paragraph("always @(posedge clk)", st['td']), Paragraph("时序逻辑，综合为触发器", st['td_l']), Paragraph("状态、计数器、寄存器数组写入都放这里。", st['td_l'])],
        [Paragraph("always @(*)", st['td']), Paragraph("组合逻辑，综合为LUT和连线", st['td_l']), Paragraph("先给默认值，再写case/if，避免锁存器。", st['td_l'])],
        [Paragraph("<=", st['td']), Paragraph("非阻塞赋值，时钟边沿统一更新", st['td_l']), Paragraph("时序always一律用非阻塞赋值。", st['td_l'])],
        [Paragraph("=", st['td']), Paragraph("阻塞赋值，按语句顺序立即生效", st['td_l']), Paragraph("组合always可用；不要在同一时序块里混用。", st['td_l'])],
    ]
    t = Table(synth, colWidths=[3*cm, 5.8*cm, 6.2*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "Verilog可综合写法速查"))
    story.append(t)

    story.append(Paragraph("常见综合报错与修正", st['sec_title']))
    fixes = [
        [Paragraph("现象", st['th']), Paragraph("根因", st['th']), Paragraph("修正动作", st['th'])],
        [Paragraph("multiple drivers", st['td']), Paragraph("同一个reg或wire被多个always/assign驱动", st['td_l']), Paragraph("让每个寄存器只在一个always块中赋值。", st['td_l'])],
        [Paragraph("latch inferred", st['td']), Paragraph("组合always没有覆盖所有分支", st['td_l']), Paragraph("always @(*)开头先写默认值，case加default。", st['td_l'])],
        [Paragraph("端口未连接", st['td']), Paragraph("模块例化端口名拼错或漏接", st['td_l']), Paragraph("用命名端口连接，按模块声明逐项核对。", st['td_l'])],
        [Paragraph("位宽截断", st['td']), Paragraph("左右位宽不一致，综合自动截断或补零", st['td_l']), Paragraph("给常数写明确位宽，如8'd0、16'd50000。", st['td_l'])],
        [Paragraph("仿真与板上不一致", st['td']), Paragraph("初值依赖、异步输入未同步、复位条件不完整", st['td_l']), Paragraph("所有关键寄存器写复位值，外部输入先同步。", st['td_l'])],
    ]
    t = Table(fixes, colWidths=[3.3*cm, 5.8*cm, 5.9*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "常见综合报错修正表"))
    story.append(t)

    story.append(Paragraph("赛场默认模板", st['sec_title']))
    story.append(Preformatted("""// 时序逻辑：只在时钟沿更新，复位给确定初值
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        cnt <= 16'd0;
    end else begin
        cnt <= cnt + 1'b1;
    end
end

// 组合逻辑：先默认，后分支，避免锁存器
always @(*) begin
    next_state = state;
    case (state)
        IDLE: if (start) next_state = WORK;
        WORK: if (done)  next_state = IDLE;
        default: next_state = IDLE;
    endcase
end""", st['code']))
    story.append(PageBreak())

    story.append(Paragraph("50MHz计数参数与定时器写法速查", st['ch_title']))
    story.append(DecorLine())
    story.append(Paragraph("CT137X主时钟为50MHz，一个时钟周期是20ns。所有延时、闪烁、扫描、PWM和串口波特率，本质都是把“时间”换算成“时钟个数”。赛场上不要临时心算，优先查本表，再把参数写成localparam，减少边界错误。", st['quote']))
    timing = [
        [Paragraph("用途", st['th']), Paragraph("目标", st['th']), Paragraph("50MHz计数", st['th']), Paragraph("常用写法", st['th'])],
        [Paragraph("1us节拍", st['td']), Paragraph("1us", st['td']), Paragraph("50周期", st['td']), Paragraph("cnt == 49", st['td_l'])],
        [Paragraph("1ms节拍", st['td']), Paragraph("1ms", st['td']), Paragraph("50,000周期", st['td']), Paragraph("cnt == 49_999", st['td_l'])],
        [Paragraph("按键消抖", st['td']), Paragraph("20ms", st['td']), Paragraph("1,000,000周期", st['td']), Paragraph("cnt == 999_999", st['td_l'])],
        [Paragraph("数码管切位", st['td']), Paragraph("1kHz", st['td']), Paragraph("50,000周期", st['td']), Paragraph("8位平均每位125Hz", st['td_l'])],
        [Paragraph("LED报警闪烁", st['td']), Paragraph("0.2s", st['td']), Paragraph("10,000,000周期", st['td']), Paragraph("cnt == 9_999_999后翻转", st['td_l'])],
        [Paragraph("1秒倒计时", st['td']), Paragraph("1s", st['td']), Paragraph("50,000,000周期", st['td']), Paragraph("cnt == 49_999_999", st['td_l'])],
        [Paragraph("UART 115200", st['td']), Paragraph("8N1", st['td']), Paragraph("约434周期/bit", st['td']), Paragraph("发送每434拍换位，接收半位217拍采样", st['td_l'])],
        [Paragraph("1kHz PWM 90%", st['td']), Paragraph("周期1ms", st['td']), Paragraph("高45,000 / 周期50,000", st['td']), Paragraph("pwm_cnt < 45_000", st['td_l'])],
        [Paragraph("1kHz PWM 10%", st['td']), Paragraph("周期1ms", st['td']), Paragraph("高5,000 / 周期50,000", st['td']), Paragraph("pwm_cnt < 5_000", st['td_l'])],
    ]
    t = Table(timing, colWidths=[3*cm, 2.6*cm, 4*cm, 5.4*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "50MHz常用计数参数表"))
    story.append(t)

    story.append(Paragraph("计数器边界写法", st['sec_title']))
    add_paras(story, [
        "如果一个事件需要N个时钟周期，计数器通常从0数到N-1，因此比较值应写成N-1，而不是N。比如1ms需要50,000个周期，计数器取值范围是0到49,999；当cnt==49_999时产生tick并清零。",
        "位宽按最大计数值选择：1秒需要计到49,999,999，小于2^26，所以26位足够；20ms需要计到999,999，小于2^20，所以20位足够。为了赛场稳妥，参数可用localparam integer定义，寄存器位宽略宽一两位也可以。"
    ], st)
    story.append(Preformatted("""localparam integer CLK_HZ = 50_000_000;
localparam integer TICK_1MS = CLK_HZ / 1000;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        cnt_1ms <= 16'd0;
        tick_1ms <= 1'b0;
    end else if (cnt_1ms == TICK_1MS - 1) begin
        cnt_1ms <= 16'd0;
        tick_1ms <= 1'b1;
    end else begin
        cnt_1ms <= cnt_1ms + 1'b1;
        tick_1ms <= 1'b0;
    end
end""", st['code']))
    story.append(PageBreak())
    return story

# ==================== 目录（带页码） ====================
def build_toc(st):
    story = []
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("目    录", st['toc_title']))
    story.append(DecorLine(color=C['secondary'], thickness=2))
    story.append(Spacer(1, 5*mm))

    # TOC条目：key = chapter_pages中的key
    toc_items = [
        ("front", "出版说明、速查卡、时间分配与调试清单", True),
        ("ch1",  "第一章  硬件平台概览", True),
        ("ch1_1","1.1  DP2026 FPGA竞赛实训平台", False),
        ("ch1_2","1.2  硬件资源配置", False),
        ("ch1_3","1.3  I2C设备地址表", False),
        ("ch1_4","1.4  数码管段码表", False),
        ("ch1_5","1.5  电源配置", False),
        ("ch2",  "第二章  引脚约束与配置", True),
        ("ch2_1","2.1  XDC约束文件说明", False),
        ("ch2_2","2.2  Vivado工程创建流程", False),
        ("ch2_3","2.3  完整引脚映射表", False),
        ("ch3",  "第三章  核心原理与真题实战", True),
        ("ch3_1","3.1  数字系统设计方法", False),
        ("ch3_2","3.2  I2C/UART/SPI通信协议", False),
        ("ch3_3","3.3  板载外设时序原理", False),
        ("ch3_4","3.4  第16届国赛算法拆解", False),
        ("ch3_5","3.5  全部真题与模拟题题面", False),
        ("ch4",  "第四章  Driver 驱动模块详解", True),
        ("ch4_1","4.1   key_ctrl.v — 按键消抖", False),
        ("ch4_2","4.2   led_display.v — LED驱动", False),
        ("ch4_3","4.3   frequency_driver.v — 分频器", False),
        ("ch4_4","4.4   iic_drive.v — I2C驱动", False),
        ("ch4_5","4.5   adc_ctrl.v — ADC控制", False),
        ("ch4_6","4.6   dac_ctrl.v — DAC控制", False),
        ("ch4_7","4.7   eeprom_read_ctrl.v — EEPROM读", False),
        ("ch4_8","4.8   eeprom_write_ctrl.v — EEPROM写", False),
        ("ch4_9","4.9   uart_tx.v — 串口发送", False),
        ("ch4_10","4.10  uart_rx.v — 串口接收", False),
        ("ch4_11","4.11  spi_master.v — SPI主控", False),
        ("ch4_12","4.12  ds1302_wr_drive.v — RTC读写", False),
        ("ch4_13","4.13  ds1302_io_convert.v — RTC IO转换", False),
        ("ch4_14","4.14  sram_ctrl.v — SRAM控制", False),
        ("ch4_15","4.15  w25q128_ctrl.v — Flash控制", False),
        ("ch4_16","4.16  seg_driver.v — 数码管驱动", False),
        ("ch5",  "第五章  User 应用模块详解", True),
        ("ch5_1","5.1   led_proc.v — LED模式控制", False),
        ("ch5_2","5.2   key_proc.v — 按键处理", False),
        ("ch5_3","5.3   uart_parser.v — 串口解析", False),
        ("ch5_4","5.4   uart_string_sender.v — 串口发送", False),
        ("ch5_5","5.5   seg_proc.v — 数码管扫描", False),
        ("ch5_6","5.6   ds1302_test.v — RTC测试", False),
        ("ch5_7","5.7   top_board.v — 板级顶层", False),
        ("ch5_8","5.8   top.v — 系统顶层", False),
        ("appendix", "附录  参考表格", True),
    ]

    toc_dot_style = ParagraphStyle('TOCDOT', fontName='MSYH', fontSize=7, textColor=C['muted'], alignment=TA_CENTER)
    toc_data = []
    for key, title, is_chapter in toc_items:
        if is_chapter:
            toc_data.append([
                Paragraph(f"<b>{title}</b>", st['toc_ch']),
                "",
                Paragraph(f"<b>{chapter_pages.get(key, '…')}</b>",
                          ParagraphStyle('TCP', fontName='SimHei', fontSize=11, textColor=C['primary'], alignment=TA_RIGHT))
            ])
        else:
            toc_data.append([
                Paragraph(title, st['toc_entry']),
                Paragraph("· " * 12, toc_dot_style),
                Paragraph(str(chapter_pages.get(key, '…')), st['toc_page'])
            ])

    table = Table(toc_data, colWidths=[9*cm, 4*cm, 3*cm])
    table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('LINEBELOW', (0,0), (-1,0), 0.8, C['border']),
    ]))
    story.append(table)
    story.append(PageBreak())
    return story

# ==================== 代码注释字典 ====================
def get_line_explanations(fname):
    E = {}
    if fname == 'key_ctrl.v':
        E = {
            'module key_ctrl': '▶ 模块定义：按键消抖与边沿检测。输入100Hz时钟(由frequency_divider从50MHz分频)，输出down(按下)和up(释放)单周期脉冲',
            'input  wire       clk_100': '▶ 100Hz消抖时钟：周期10ms，天然过滤机械按键抖动(通常<10ms)',
            'input  wire [3:0] key_in': '▶ 按键输入：CT137X板S1(M5)/S2(M4)/S3(P5)/S4(N4)，低电平有效',
            'output reg  [3:0] down': '▶ 按下脉冲：检测到下降沿(1→0)时输出一个时钟周期高脉冲',
            'output reg  [3:0] up': '▶ 释放脉冲：检测到上升沿(0→1)时输出一个时钟周期高脉冲',
            'reg [3:0] val': '▶ 当前采样值：每个clk_100周期锁存key_in',
            'reg [3:0] old': '▶ 上周期值：与val比较实现边沿检测',
            'val  <= 4\'b1111': '▶ 复位：假设未按下(高电平)，因按键低电平有效',
            'old <= val': '▶ 保存当前值：下一周期用于与新采样值比较',
            'val <= key_in': '▶ 采样：锁存当前按键物理电平',
            'down <= val & (val ^ old)': '▶ 下降沿检测：异或找变化位，与val相与找1→0的位(按下瞬间)',
            'up   <= ~val & (val ^ old)': '▶ 上升沿检测：异或找变化位，与~val相与找0→1的位(释放瞬间)',
        }
    elif fname == 'led_display.v':
        E = {
            'module led_display': '▶ LED驱动：CT137X板LED阳极经电阻接3.3V，FPGA输出低电平点亮，需取反',
            'led = ~led_pattern': '▶ 取反输出：逻辑1=亮 → 物理0=亮，匹配硬件电路',
        }
    elif fname == 'frequency_driver.v':
        E = {
            'module frequency_divider': '▶ 通用分频器：输入基准频率和目标频率，输出分频时钟',
            'input  wire [31:0] clkbase': '▶ 基准频率(Hz)：如50MHz传入50_000_000',
            'input  wire [31:0] clkdiv': '▶ 目标频率(Hz)：如1kHz传入1000',
            'limit = clkbase / (2 * clkdiv)': '▶ 计数上限：50MHz/(2×1kHz)=25000，每25000个时钟翻转一次',
            'clkout  <= ~clkout': '▶ 翻转输出：计到上限时翻转，产生方波',
        }
    elif fname == 'iic_drive.v':
        E = {
            'module iic_drive': '▶ I2C底层驱动：支持多字节读写，CT137X板ADC/DAC/EEPROM共用I2C总线(SCL=E11,SDA=M10)',
            'P_SYS_CLK = 28\'d50_000_000': '▶ 系统时钟50MHz(G11引脚有源晶振)',
            'P_IIC_SCL = 28\'d125_000': '▶ I2C时钟125kHz(标准100k~快速400k之间)',
            'P_DEVICE_ADDR = 7\'b1010_100': '▶ 器件地址：ADC=1010100, EEPROM=1010XXX, DAC=1001100',
            'SCL_CNT_MAX = P_SYS_CLK / P_IIC_SCL - 1': '▶ SCL分频：50MHz/125kHz-1=399，每400系统时钟一个SCL周期',
            'assign active = iic_start && iic_ready': '▶ 激活：外部请求 且 模块空闲时启动传输',
            'start_device_write = {1\'b0,P_DEVICE_ADDR,1\'b0}': '▶ 写命令拼接：起始位+7位地址+写标志(0)',
            'start_device_read = {1\'b0,P_DEVICE_ADDR,1\'b1}': '▶ 读命令拼接：起始位+7位地址+读标志(1)',
            'assign sda_in = !sda_ctrl ? iic_sda : 1\'b1': '▶ 三态门输入：sda_ctrl=0时读SDA线',
            'assign iic_sda = sda_ctrl ? sda_out : 1\'bz': '▶ 三态门输出：sda_ctrl=1时驱动SDA，否则高阻',
            'scl_nedge_flag <= (cnt_scl == 0)': '▶ SCL下降沿：计数器到0时产生',
            'scl_pedge_flag <= (cnt_scl == SCL_CNT_MAX / 2)': '▶ SCL上升沿：计数器到一半时产生',
            'w_sda_flag <= (cnt_scl == SCL_CNT_MAX / 4)': '▶ SDA写时机：SCL低电平1/4处更新数据',
            'r_sda_flag <= (cnt_scl == SCL_CNT_MAX * 3 / 4)': '▶ SDA读时机：SCL高电平3/4处采样数据',
        }
    elif fname == 'adc_ctrl.v':
        E = {
            'module adc_ctrl': '▶ ADC081C021控制：电位器RV1模拟电压→8位数字量(0-127)，I2C接口',
            'P_DEVICE_ADDR = 7\'b1010_100': '▶ ADC器件地址1010100(数据手册规定)',
            'iic_rw_flag(1\'b1)': '▶ 固定读操作：ADC只需读取转换结果',
            'assign ad_data = iic_r_data[11:4]': '▶ 提取有效位：16位原始数据取bit[11:4]作为8位输出',
        }
    elif fname == 'dac_ctrl.v':
        E = {
            'module dac_ctrl': '▶ DAC5571控制：8位数字→模拟电压，输出到D4指示灯和TP1测试点',
            'P_DEVICE_ADDR = 7\'b100_1100': '▶ DAC器件地址1001100',
            'assign iic_w_data = {4\'b0000, da_data, 4\'b0000}': '▶ 格式转换：8位数据放中间，前后补4个0，匹配DAC5571的12位格式',
        }
    elif fname == 'eeprom_read_ctrl.v':
        E = {
            'module eeprom_read_ctrl': '▶ AT24C02读控制：2Kbit(256字节)EEPROM，I2C接口，1字节地址寻址',
            'P_DEVICE_ADDR = 7\'b101_0000': '▶ EEPROM地址1010XXX，A2A1A0全接地=000',
        }
    elif fname == 'uart_tx.v':
        E = {
            'module uart_tx': '▶ UART发送：CT137X板TX→F12→CH340C→USB→电脑，115200/8N1',
            'BAUD_CNT_MAX = CLK_FREQ / UART_BPS': '▶ 波特率计数：50MHz/115200≈434，每434时钟发1位',
            'localparam IDLE': '▶ 空闲：TX保持高电平',
            'localparam START': '▶ 起始位：TX拉低1个波特率周期',
            'localparam DATA': '▶ 数据位：LSB first逐位发送8位',
            'localparam STOP': '▶ 停止位：TX拉高1个波特率周期',
            'tx <= pi_data[bit_cnt]': '▶ 位输出：bit_cnt 0→7，先发最低位',
        }
    elif fname == 'uart_rx.v':
        E = {
            'module uart_rx': '▶ UART接收：RX←E12←CH340C←USB←电脑',
            'rx_reg1 <= rx': '▶ 一级同步：将异步rx同步到系统时钟域',
            'rx_reg2 <= rx_reg1': '▶ 二级同步：消除亚稳态',
            'if (!rx_reg2)': '▶ 起始位检测：rx下降沿表示一帧开始',
            'baud_cnt == BAUD_CNT_MAX / 2 - 1': '▶ 中点采样：起始位中间确认有效，避免毛刺',
            'rx_data <= {rx_reg2, rx_data[7:1]}': '▶ 右移接收：8位全部收完后rx_data=完整数据',
        }
    elif fname == 'spi_master.v':
        E = {
            'module spi_master': '▶ SPI主控：驱动DS1302 RTC，DS1302用类SPI接口(CE高有效，与标准SPI相反)',
            'SPI_CPOL = 1\'b0': '▶ 时钟极性0：空闲时SCLK低',
            'SPI_CPHA = 1\'b0': '▶ 时钟相位0：上升沿采样，下降沿更新',
            'spi_mosi = mosi_shift[7]': '▶ MOSI：始终发移位寄存器最高位(MSB first)',
            'mosi_shift <= {mosi_shift[6:0],mosi_shift[7]}': '▶ 左移发送：每完成一位左移',
            'miso_shift <= {miso_shift[6:0],spi_miso}': '▶ 左移接收：逐位从MISO接收',
        }
    elif fname == 'ds1302_wr_drive.v':
        E = {
            'module ds1302_wr_drive': '▶ DS1302完整读写控制：一次操作可读/写全部7个时间寄存器',
            'WRITE_WP: write_addr <= 8\'h8e': '▶ 写保护解除：向0x8E写0x00关闭写保护',
            'WRITE_SEC: write_addr <= 8\'h80': '▶ 秒寄存器写地址0x80',
            'READ_SEC: read_addr <= 8\'h81': '▶ 秒寄存器读地址0x81(=写地址+1)',
        }
    elif fname == 'ds1302_io_convert.v':
        E = {
            'module ds1302_io_convert': '▶ DS1302 IO转换：①LSB↔MSB位序翻转 ②单IO↔双IO端口转换 ③CE极性转换',
            'ds1302_data = ~ds1302_io_ctrl ? ds1302_mosi : 1\'bz': '▶ 三态门：写时驱动，读时高阻',
            'ds1302_read_data <= {receive_data[0],...,receive_data[7]}': '▶ 位序翻转：SPI的MSB-first→DS1302的LSB-first',
        }
    elif fname == 'sram_ctrl.v':
        E = {
            'module sram_ctrl': '▶ IS63WV1288 SRAM：128K×8位异步SRAM，17位地址+8位数据',
            'sram_ce_n = ... ? 1\'b0 : 1\'b1': '▶ 片选：读写时拉低CE',
            'sram_oe_n = ... ? 1\'b0 : 1\'b1': '▶ 输出使能：仅读时拉低OE',
            'sram_we_n = ... ? 1\'b0 : 1\'b1': '▶ 写使能：仅写时拉低WE',
        }
    elif fname == 'w25q128_ctrl.v':
        E = {
            'module w25q128_ctrl': '▶ W25Q128 Flash：128Mbit SPI NOR Flash，支持读ID/读/写/擦除',
            'OP_READ_JEDEC_ID': '▶ 读JEDEC ID：0x9F命令，返回3字节厂商+设备ID',
            'OP_READ_BYTE': '▶ 读字节：0x03+3字节地址，返回1字节',
            'OP_WRITE_BYTE': '▶ 写字节：0x02+3字节地址+1字节数据，需先发WREN(0x06)',
            'OP_SECTOR_ERASE': '▶ 扇区擦除：0x20+3字节地址，擦除4KB',
            'S_LAUNCH_WREN': '▶ 写使能：写/擦除前必须发0x06',
            'S_LAUNCH_POLL': '▶ 轮询：读状态寄存器bit0(WIP)等待操作完成',
        }
    elif fname == 'seg_driver.v':
        E = {
            'module seg_driver': '▶ 数码管驱动：共阳极8段，段选D3-A5，位选B2-F2，低电平有效',
            'SEG_0 = 8\'b1100_0000': '▶ 数字0段码：A~F亮(0)，G灭(1)=0xC0',
            'SEG_NULL = 8\'b1111_1111': '▶ 全灭：所有段都灭=0xFF',
            'if (current_dp) segment_data[7] = 1\'b0': '▶ 小数点：bit[7]=SEGDP，0=点亮',
            'digit_sel = ~(8\'b0000_0001 << position)': '▶ 位选译码：左移后取反(COM低有效)',
        }
    elif fname == 'seg_proc.v':
        E = {
            'module seg_proc': '▶ 数码管扫描：32位数据→8位数码管，1kHz扫描(每1ms切一位)',
            'current_num = seg_number_in[(7-bits)*4+:4]': '▶ 位选择：根据扫描索引提取4位数字',
            'bits <= (bits == 3\'d7) ? 3\'d0 : bits + 3\'d1': '▶ 扫描循环：0→1→...→7→0，125Hz刷新',
        }
    elif fname == 'led_proc.v':
        E = {
            'module led_proc': '▶ LED模式控制：4种模式(左移/右移/闪烁/固定)，1Hz驱动',
            '{led_pattern[6:0], led_pattern[7]}': '▶ 左移循环：流水灯左移',
            '{led_pattern[0], led_pattern[7:1]}': '▶ 右移循环：流水灯右移',
            '~led_pattern': '▶ 闪烁：每秒取反',
            '8\'b1010_1010': '▶ 固定：奇数位亮偶数位灭',
        }
    elif fname == 'key_proc.v':
        E = {
            'module key_proc': '▶ 按键处理：集成消抖+模式切换，S1-S4分别选模式0-3',
            'frequency_divider u_frequency_divider': '▶ 分频：50MHz→100Hz供消抖',
            'key_ctrl key_ctrl_inst': '▶ 消抖实例：输出消抖后的按下脉冲',
        }
    elif fname == 'uart_parser.v':
        E = {
            'module uart_parser': '▶ 串口解析：接收\\r\\n结尾的字符串命令，解析首字符为命令码',
            'if (po_data == 8\'h0D)': '▶ 检测\\r(0x0D)',
            'if (po_data == 8\'h0A)': '▶ 检测\\n(0x0A)，\\r\\n确认命令结束',
            '"A": cmd_signal <= 8\'h01': '▶ 命令解析：A→0x01, W→0x00',
        }
    elif fname == 'uart_string_sender.v':
        E = {
            'module uart_string_sender': '▶ 串口批量发送：宽总线→逐字节UART发送，支持动态长度',
            'pi_data <= string_data[(data_length-1-cnt)*8+:8]': '▶ 字节提取：从宽总线取当前字节',
        }
    elif fname == 'ds1302_test.v':
        E = {
            'module ds1302_test': '▶ DS1302测试控制：管理RTC初始化、CH位清除、读写流程',
            'CH = read_second[7]': '▶ CH位：秒寄存器最高位，=1表示时钟暂停',
            'write_second_reg <= {1\'b0, read_second[6:0]}': '▶ 清除CH：保持秒值，最高位清零',
        }
    elif fname == 'top_board.v':
        E = {
            'module top_board': '▶ 板级顶层：CT137X物理引脚名→内部信号名映射',
            'assign sys_rst_n = ~RESET': '▶ 复位转换：板上RESET高有效→内部低有效',
            'assign key = {S4, S3, S2, S1}': '▶ 按键拼接：4个独立按键→4位总线',
            'top u_top': '▶ 实例化系统顶层：所有逻辑在top模块中',
        }
    elif fname == 'top.v':
        E = {
            'module top': '▶ 系统顶层：集成按键/LED/数码管/蜂鸣器全部功能',
            'BUZ_ACTIVE_LOW = 1\'b1': '▶ 蜂鸣器低有效(NPN三极管驱动)',
            'key_ctrl u_key': '▶ 消抖实例：S1加1/S2减1/S3切LED模式/S4切蜂鸣器模式',
            'led_proc u_led_proc': '▶ LED实例：根据led_mode控制显示模式',
            'seg_proc u_seg_proc': '▶ 数码管实例：COM1-4计数值，COM5LED模式，COM6蜂鸣器模式',
        }
    return E

def get_usage_info(fname):
    info = {
        'key_ctrl.v': "▶ 硬件：S1(M5)/S2(M4)/S3(P5)/S4(N4)，低电平有效。需先用frequency_divider分频到100Hz作为消抖时钟。",
        'led_display.v': "▶ 硬件：LD1(N14)~LD8(P11)，阳极经电阻接3.3V，FPGA输出低电平点亮。",
        'iic_drive.v': "▶ 硬件：I2C总线SCL(E11)+SDA(M10)，连接ADC(1010100)/DAC(1001100)/EEPROM(1010000)。SDA需上拉电阻(板上已集成)。",
        'adc_ctrl.v': "▶ 硬件：ADC081C021连接电位器RV1(0~3.3V)，断开R90可测外部信号。输出8位(0-127)。",
        'dac_ctrl.v': "▶ 硬件：DAC5571输出接D4指示灯和TP1测试点，断开R74可驱动外部电路。",
        'uart_tx.v': "▶ 硬件：TX→F12→CH340C→USB→电脑。电脑端串口助手设置115200/8N1。",
        'uart_rx.v': "▶ 硬件：RX←E12←CH340C←USB←电脑。两级寄存器消除亚稳态。",
        'seg_driver.v': "▶ 硬件：段选SEGA(D3)~SEGDP(A5)，位选COM1(B2)~COM8(F2)，共阳极低电平有效。",
        'sram_ctrl.v': "▶ 硬件：IS63WV1288，17位地址A0-A16，8位数据D0-D7，CE/OE/WE低有效。",
        'w25q128_ctrl.v': "▶ 硬件：CS(D12)/SCK(D13)/IO0(G14)/IO1(F14)/IO2(F13)/IO3(E13)。U3=配置Flash，U10=用户Flash。",
        'ds1302_wr_drive.v': "▶ 硬件：SCLK(A10)/CE(A12)/DATA(A13)。需配合ds1302_io_convert和spi_master使用。",
        'frequency_driver.v': "▶ 用法：frequency_divider #(.clkbase(50M), .clkdiv(100)) 产生100Hz时钟。",
    }
    return info.get(fname, "")

# ==================== 带注释代码块 ====================
def build_annotated_code(fname, content, st):
    elements = []
    explanations = get_line_explanations(fname)
    lines = content.split('\n')
    annotated = []
    for line in lines:
        stripped = line.strip()
        matched = None
        for key, exp in explanations.items():
            if key in stripped:
                matched = exp
                break
        if matched:
            annotated.append(f"// {matched}")
        annotated.append(line)

    chunk_size = 55
    for i in range(0, len(annotated), chunk_size):
        chunk = '\n'.join(annotated[i:i+chunk_size])
        elements.append(Preformatted(chunk, st['code']))
    return elements

# ==================== 硬件章节 ====================
def build_chapter1(st):
    story = []
    story.append(ChapterMarker("ch1", chapter_pages))
    story.append(Paragraph("第一章  硬件平台概览", st['ch_title']))
    story.append(DecorLine())
    story.append(Spacer(1, 3*mm))

    story.append(ChapterMarker("ch1_1", chapter_pages))
    story.append(Paragraph("1.1  DP2026 FPGA竞赛实训平台", st['sec_title']))
    story.append(Paragraph("蓝桥杯FPGA竞赛实训平台由四梯科技设计生产，基于Xilinx Spartan-7 XC7S6-1FTGB196。"
                           "芯片提供6000 Logic Cells、7500 CLB、180KB Block RAM、2个CMT、100个IO，适合中等规模设计。", st['body']))

    story.append(ChapterMarker("ch1_2", chapter_pages))
    story.append(Paragraph("1.2  硬件资源配置", st['sec_title']))

    def th(t): return Paragraph(t, st['th'])
    def td(t): return Paragraph(t, st['td'])

    hw = [
        [th("外设"), th("型号"), th("接口"), th("FPGA引脚")],
        [td("系统时钟"), td("50MHz有源晶振"), td("单端"), td("G11")],
        [td("复位按键"), td("RESET 高有效"), td("GPIO"), td("B6")],
        [td("按键S1-S4"), td("低有效"), td("GPIO"), td("M5/M4/P5/N4")],
        [td("LED LD1-LD8"), td("低电平点亮"), td("GPIO"), td("N14~P11")],
        [td("ADC"), td("ADC081C021 8位"), td("I2C"), td("SCL=E11,SDA=M10")],
        [td("DAC"), td("DAC5571 8位"), td("I2C"), td("共用I2C")],
        [td("EEPROM"), td("AT24C02 2Kbit"), td("I2C"), td("共用I2C")],
        [td("Flash"), td("W25Q128 128Mbit"), td("SPI"), td("CS=D12,SCK=D13")],
        [td("RTC"), td("DS1302"), td("类SPI"), td("SCLK=A10,CE=A12,IO=A13")],
        [td("SRAM"), td("IS63WV1288 128Kx8"), td("并口"), td("A0-A16,D0-D7")],
        [td("数码管"), td("8位共阳极8段"), td("段+位"), td("SEG=D3~A5,COM=B2~F2")],
        [td("UART"), td("CH340C USB转串口"), td("UART"), td("TX=F12,RX=E12")],
        [td("蜂鸣器"), td("无源,NPN驱动"), td("GPIO"), td("L5")],
    ]
    story.append(table_caption(st, "CT137X 硬件资源配置"))
    t = Table(hw, colWidths=[2.8*cm, 3.5*cm, 2.2*cm, 4.8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C['primary']),
        ('TEXTCOLOR', (0,0), (-1,0), white),
        ('GRID', (0,0), (-1,-1), 0.5, C['border']),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 3*mm))

    story.append(ChapterMarker("ch1_3", chapter_pages))
    story.append(Paragraph("1.3  I2C设备地址表", st['sec_title']))
    story.append(Paragraph("ADC/DAC/EEPROM共用I2C总线(SCL=E11, SDA=M10)，通过7位器件地址区分。", st['body']))
    i2c = [
        [th("器件"), th("型号"), th("7位地址"), th("读地址"), th("写地址"), th("说明")],
        [td("ADC"), td("ADC081C021"), td("1010100"), td("0xA9"), td("0xA8"), td("8位ADC，测电位器")],
        [td("DAC"), td("DAC5571"), td("1001100"), td("0x99"), td("0x98"), td("8位DAC，模拟输出")],
        [td("EEPROM"), td("AT24C02"), td("1010000"), td("0xA1"), td("0xA0"), td("2Kbit，256字节")],
    ]
    t = Table(i2c, colWidths=[1.6*cm, 2.3*cm, 2*cm, 1.8*cm, 1.8*cm, 3.8*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C['primary']),
        ('GRID', (0,0), (-1,-1), 0.5, C['border']),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(table_caption(st, "I2C设备地址表"))
    story.append(t)

    story.append(ChapterMarker("ch1_4", chapter_pages))
    story.append(Paragraph("1.4  数码管段码表（共阳极）", st['sec_title']))
    seg = [
        [th("数字"), th("段码(二进制)"), th("十六进制"), th("点亮的段")],
        [td("0"), td("1100_0000"), td("0xC0"), td("A,B,C,D,E,F")],
        [td("1"), td("1111_1001"), td("0xF9"), td("B,C")],
        [td("2"), td("1010_0100"), td("0xA4"), td("A,B,D,E,G")],
        [td("3"), td("1011_0000"), td("0xB0"), td("A,B,C,D,G")],
        [td("4"), td("1001_1001"), td("0x99"), td("B,C,F,G")],
        [td("5"), td("1001_0010"), td("0x92"), td("A,C,D,F,G")],
        [td("6"), td("1000_0010"), td("0x82"), td("A,C,D,E,F,G")],
        [td("7"), td("1111_1000"), td("0xF8"), td("A,B,C")],
        [td("8"), td("1000_0000"), td("0x80"), td("A,B,C,D,E,F,G")],
        [td("9"), td("1001_0000"), td("0x90"), td("A,B,C,D,F,G")],
        [td("灭"), td("1111_1111"), td("0xFF"), td("无")],
    ]
    t = Table(seg, colWidths=[1.5*cm, 3.5*cm, 2.5*cm, 4.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C['primary']),
        ('GRID', (0,0), (-1,-1), 0.5, C['border']),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(table_caption(st, "数码管段码表（共阳极）"))
    story.append(t)

    story.append(ChapterMarker("ch1_5", chapter_pages))
    story.append(Paragraph("1.5  电源配置", st['sec_title']))
    pwr = [
        [th("电源"), th("电压"), th("说明")],
        [td("VCCINT"), td("+1.0V"), td("FPGA内核电压")],
        [td("VCCBRAM"), td("+1.0V"), td("Block RAM供电")],
        [td("VCCAUX"), td("+1.8V"), td("模拟组件电压")],
        [td("VCCO_14"), td("+3.3V"), td("Bank14 IO(RTC/LED/ADC等)")],
        [td("VCCO_34"), td("+3.3V"), td("Bank34 IO(数码管/按键/SRAM)")],
    ]
    t = Table(pwr, colWidths=[3*cm, 2*cm, 8.3*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C['primary']),
        ('GRID', (0,0), (-1,-1), 0.5, C['border']),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(table_caption(st, "电源配置"))
    story.append(t)
    story.append(Paragraph("<b>重要：</b>所有IO Bank均为3.3V，Vivado中必须设置IOSTANDARD为LVCMOS33。", st['tip']))
    story.append(PageBreak())
    return story

# ==================== 引脚约束章节 ====================
def build_chapter2(st):
    story = []
    story.append(ChapterMarker("ch2", chapter_pages))
    story.append(Paragraph("第二章  引脚约束与配置", st['ch_title']))
    story.append(DecorLine())
    story.append(Spacer(1, 3*mm))

    story.append(ChapterMarker("ch2_1", chapter_pages))
    story.append(Paragraph("2.1  XDC约束文件说明", st['sec_title']))
    story.append(Paragraph("XDC文件定义FPGA引脚物理约束。CT137X使用Spartan-7 XC7S6-1FTGB196，所有IO为LVCMOS33。", st['body']))
    xdc = """# 必须包含的基础配置
set_property CFGBVS VCCO [current_design]           # 配置Bank电压=VCCO(3.3V)
set_property CONFIG_VOLTAGE 3.3 [current_design]     # 配置电压3.3V

# 系统时钟 50MHz (G11引脚)
set_property -dict {PACKAGE_PIN G11 IOSTANDARD LVCMOS33} [get_ports {clk}]
create_clock -period 20.000 -name clk [get_ports {clk}]  # 20ns=50MHz

# 复位按键 (B6引脚，高有效！)
set_property -dict {PACKAGE_PIN B6 IOSTANDARD LVCMOS33} [get_ports {rst}]

# 用户按键 (低有效)
set_property -dict {PACKAGE_PIN M5 IOSTANDARD LVCMOS33} [get_ports {key[0]}]  # S1
set_property -dict {PACKAGE_PIN M4 IOSTANDARD LVCMOS33} [get_ports {key[1]}]  # S2"""
    story.append(Preformatted(xdc, st['code']))
    story.append(Spacer(1, 3*mm))

    story.append(ChapterMarker("ch2_2", chapter_pages))
    story.append(Paragraph("2.2  Vivado工程创建流程", st['sec_title']))
    story.append(Paragraph("零基础最容易卡在“代码没问题但工程建错”。建议每个赛题都按固定流程建立工程，减少隐性环境差异。", st['body']))
    def th(t): return Paragraph(t, st['th'])
    def td(t): return Paragraph(t, st['td'])
    flow = [
        [th("步骤"), th("动作"), th("检查点")],
        [td("1"), td("Create Project，选择RTL Project，不勾选Do not specify sources"), td("工程名用英文和下划线，避免中文路径导致工具异常")],
        [td("2"), td("选择器件XC7S6-1FTGB196或按板卡手册选择对应Spartan-7型号"), td("器件型号错误会导致引脚约束无法匹配")],
        [td("3"), td("添加driver和user中的Verilog源文件"), td("顶层只保留一个top_board或比赛要求的顶层模块")],
        [td("4"), td("添加XDC约束文件并核对端口名"), td("get_ports名称必须和顶层端口完全一致")],
        [td("5"), td("Run Synthesis -> Run Implementation -> Generate Bitstream"), td("先看Critical Warning，再看Timing是否通过")],
        [td("6"), td("下载bit文件到板卡并做最小硬件验证"), td("先测LED/数码管/按键，再接入复杂外设")],
    ]
    t = Table(flow, colWidths=[1.4*cm, 6.2*cm, 7.4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C['primary']),
        ('GRID', (0,0), (-1,-1), 0.5, C['border']),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(table_caption(st, "Vivado工程创建流程"))
    story.append(t)
    story.append(Paragraph("<b>赛场原则：</b>不要一上来就把所有模块接进顶层。先建立能综合、能下载、能看到LED变化的最小工程，再逐个接外设。每接入一个外设，都保留一个可观察输出作为验收点。", st['tip']))

    story.append(ChapterMarker("ch2_3", chapter_pages))
    story.append(Paragraph("2.3  完整引脚映射表", st['sec_title']))
    pins = [
        [th("功能"), th("引脚"), th("FPGA"), th("功能"), th("引脚"), th("FPGA")],
        [td("S1"), td("key[0]"), td("M5"), td("LD1"), td("led[0]"), td("N14")],
        [td("S2"), td("key[1]"), td("M4"), td("LD2"), td("led[1]"), td("M14")],
        [td("S3"), td("key[2]"), td("P5"), td("LD3"), td("led[2]"), td("P12")],
        [td("S4"), td("key[3]"), td("N4"), td("LD4"), td("led[3]"), td("P13")],
        [td("UART TX"), td("uart_tx"), td("F12"), td("LD5"), td("led[4]"), td("N10")],
        [td("UART RX"), td("uart_rx"), td("E12"), td("LD6"), td("led[5]"), td("N11")],
        [td("I2C SCL"), td("scl"), td("E11"), td("LD7"), td("led[6]"), td("P10")],
        [td("I2C SDA"), td("sda"), td("M10"), td("LD8"), td("led[7]"), td("P11")],
        [td("蜂鸣器"), td("buz"), td("L5"), td("RTC SCLK"), td("rtc_sclk"), td("A10")],
        [td("RTC CE"), td("rtc_ce"), td("A12"), td("RTC DATA"), td("rtc_data"), td("A13")],
    ]
    t = Table(pins, colWidths=[1.8*cm, 1.8*cm, 1.3*cm, 1.8*cm, 1.8*cm, 1.3*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C['primary']),
        ('GRID', (0,0), (-1,-1), 0.5, C['border']),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(table_caption(st, "完整引脚映射表"))
    story.append(t)
    story.append(Paragraph("完整约束见CT137X_full_template.xdc，使用智能proc自动匹配多种端口命名。", st['tip']))
    story.append(PageBreak())
    return story

def add_paras(story, paras, st, style='body'):
    for para in paras:
        story.append(Paragraph(para, st[style]))

def safe_xml(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def exam_image_groups(base_dir):
    img_dir = os.path.join(base_dir, "真题模拟题", "extracted_images")
    if not os.path.isdir(img_dir):
        return []
    groups = {}
    for name in os.listdir(img_dir):
        if name.lower().endswith(".png"):
            key = re.sub(r"_page\d+\.png$", "", name)
            groups.setdefault(key, []).append(os.path.join(img_dir, name))
    def page_no(path):
        m = re.search(r"_page(\d+)\.png$", os.path.basename(path))
        return int(m.group(1)) if m else 0
    order = [
        "第十六届 蓝桥杯（电子类）FPGA设计与开发省赛真题",
        "第十七届蓝桥杯FPGA省赛真题",
        "第十七届蓝桥杯FPGA省赛真题_设计题",
        "十六届蓝桥杯FPGA模拟试题I",
        "十六届蓝桥杯FPGA模拟试题Ⅱ",
        "十六届蓝桥杯FPGA模拟试题Ⅲ",
        "第十七届FPGA模拟考试Ⅰ",
        "第十七届FPGA模拟考试Ⅱ",
        "第十七届FPGA模拟考试Ⅲ",
    ]
    return [(name, sorted(groups[name], key=page_no)) for name in order if name in groups]

def add_exam_image(story, path, st):
    image_path = compressed_exam_image(path)
    with PILImage.open(image_path) as img:
        w, h = img.size
    max_w, max_h = 15.8*cm, 20.8*cm
    scale = min(max_w / w, max_h / h)
    img_flow = RLImage(image_path, width=w*scale, height=h*scale)
    img_flow.hAlign = 'CENTER'
    panel_w = min(17.0*cm, w*scale + 8*mm)
    panel = Table([[img_flow]], colWidths=[panel_w])
    panel.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), white),
        ('BOX', (0,0), (-1,-1), 0.8, C['border']),
        ('LEFTPADDING', (0,0), (-1,-1), 4*mm),
        ('RIGHTPADDING', (0,0), (-1,-1), 4*mm),
        ('TOPPADDING', (0,0), (-1,-1), 3*mm),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3*mm),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(panel)
    story.append(Paragraph(f"源图：{os.path.basename(path)}", st['caption']))

def add_exam_reading_guide(story, st):
    story.append(Paragraph("扫描题面阅读规范", st['sub_title']))
    story.append(Paragraph("扫描题面是本书保留原始试卷信息的依据。纸质训练时不要把它当作单纯截图，而要按固定符号快速标记：先圈硬件对象，再划状态和时序，最后写错因。这样做能把图片题面转化为可复盘的工程任务。", st['body']))
    rows = [
        [Paragraph("标记对象", st['th']), Paragraph("纸上动作", st['th']), Paragraph("转化成代码时看什么", st['th'])],
        [Paragraph("硬件对象", st['td']), Paragraph("圈出LED、数码管、按键、UART、I2C、SPI、ADC、SRAM、Flash等名词", st['td_l']), Paragraph("对应顶层端口、XDC引脚、外设驱动实例。", st['td_l'])],
        [Paragraph("时间要求", st['td']), Paragraph("给1s、20ms、0.2s、1kHz、115200等数字加框", st['td_l']), Paragraph("换算50MHz计数值，写成localparam。", st['td_l'])],
        [Paragraph("状态/流程", st['td']), Paragraph("用箭头连接IDLE、设置、运行、报警、结束等流程词", st['td_l']), Paragraph("转成三段式FSM状态和跳转条件。", st['td_l'])],
        [Paragraph("显示格式", st['td']), Paragraph("下划线标出小数点、空白、单位、闪烁、滚动等显示要求", st['td_l']), Paragraph("对应数码管位选、段选、BCD转换和刷新节拍。", st['td_l'])],
        [Paragraph("提交要求", st['td']), Paragraph("最后单独写出工程名、压缩包格式和上传检查动作", st['td_l']), Paragraph("按ZIP检查单解压抽检，不把缓存和无关文件混入。", st['td_l'])],
    ]
    t = Table(rows, colWidths=[2.5*cm, 6.8*cm, 5.7*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "扫描题面阅读标记规范"))
    story.append(t)

def add_exam_annotation_template(story, st):
    story.append(Paragraph("真题纸面批注模板", st['sub_title']))
    story.append(Paragraph("每做一页扫描题面，都按这张模板写一遍。模板的作用不是多写字，而是强迫自己把题面语言翻译成工程语言：端口、计数值、状态、协议、显示格式和提交风险。训练时把这张表夹在题面后面，赛后只看批注就能知道错在哪里。", st['body']))
    rows = [
        [Paragraph("项目", st['th']), Paragraph("纸面填写", st['th']), Paragraph("工程化检查点", st['th'])],
        [Paragraph("题组/页码", st['td']), Paragraph("__________  第 ____ 页", st['td_l']), Paragraph("对应本书图号和源图文件名，便于回查。", st['td_l'])],
        [Paragraph("硬件对象", st['td']), Paragraph("LED / SEG / KEY / UART / I2C / SPI / ADC / RTC / SRAM / Flash：__________", st['td_l']), Paragraph("每个对象都要能找到顶层端口和驱动实例。", st['td_l'])],
        [Paragraph("输入输出", st['td']), Paragraph("输入：__________    输出：__________", st['td_l']), Paragraph("输入先同步/消抖；输出先确认低有效或高有效。", st['td_l'])],
        [Paragraph("时间参数", st['td']), Paragraph("____ ms / ____ s / ____ Hz / 波特率：__________", st['td_l']), Paragraph("全部换算成50MHz计数localparam。", st['td_l'])],
        [Paragraph("状态流程", st['td']), Paragraph("IDLE → __________ → __________ → DONE/ERROR", st['td_l']), Paragraph("先画状态图，再写三段式FSM。", st['td_l'])],
        [Paragraph("协议帧", st['td']), Paragraph("地址/命令：__________  ACK/CS/忙标志：__________", st['td_l']), Paragraph("I2C看ACK，SPI看CS和模式，UART看8N1。", st['td_l'])],
        [Paragraph("显示格式", st['td']), Paragraph("数码管位：__________  小数点/闪烁/空白：__________", st['td_l']), Paragraph("显示格式单独写mux，不和业务状态混在一起。", st['td_l'])],
        [Paragraph("最大风险", st['td']), Paragraph("概念 / 时序 / 极性 / 接口 / 提交：__________", st['td_l']), Paragraph("写出一个最可能扣分点，训练后复盘验证。", st['td_l'])],
    ]
    t = Table(rows, colWidths=[2.4*cm, 6.8*cm, 5.8*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(table_caption(st, "真题纸面批注模板"))
    story.append(t)

    checklist = [
        [Paragraph("完成标记", st['th']), Paragraph("问题", st['th']), Paragraph("通过标准", st['th'])],
        [Paragraph("□", st['td']), Paragraph("题面里所有硬件对象是否都圈出来了？", st['td_l']), Paragraph("能逐一对应到端口、XDC或驱动文件。", st['td_l'])],
        [Paragraph("□", st['td']), Paragraph("所有时间数字是否都换算为50MHz计数？", st['td_l']), Paragraph("写出N和N-1两个值，避免边界错。", st['td_l'])],
        [Paragraph("□", st['td']), Paragraph("状态流程是否能用一句话解释？", st['td_l']), Paragraph("每个状态有进入条件、保持条件和退出条件。", st['td_l'])],
        [Paragraph("□", st['td']), Paragraph("显示和通信格式是否单独列出？", st['td_l']), Paragraph("不会把显示格式、UART格式和算法计算混在同一个always里。", st['td_l'])],
        [Paragraph("□", st['td']), Paragraph("提交包风险是否检查？", st['td_l']), Paragraph("最终ZIP能另建目录解压，PDF/工程/脚本都能打开。", st['td_l'])],
    ]
    t = Table(checklist, colWidths=[2.2*cm, 6.4*cm, 6.4*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('ALIGN', (0,1), (0,-1), 'CENTER'), ('TOPPADDING', (0,0), (-1,-1), 3),
                           ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(KeepTogether([table_caption(st, "真题批注完成检查"), t]))

def compressed_exam_image(path, max_width=1200, quality=78):
    marker = os.sep + "真题模拟题" + os.sep
    base_dir = os.path.abspath(path).split(marker)[0]
    cache_dir = os.path.join(base_dir, "Aix_tools", "pdf_assets", "exam_images")
    os.makedirs(cache_dir, exist_ok=True)
    name = os.path.splitext(os.path.basename(path))[0] + ".jpg"
    out_path = os.path.join(cache_dir, name)
    if os.path.exists(out_path) and os.path.getmtime(out_path) >= os.path.getmtime(path):
        return out_path
    with PILImage.open(path) as img:
        img = img.convert("RGB")
        if img.width > max_width:
            ratio = max_width / img.width
            img = img.resize((max_width, int(img.height * ratio)), PILImage.Resampling.LANCZOS)
        img.save(out_path, "JPEG", quality=quality, optimize=True)
    return out_path

def read_pdf_text(base_dir, filename):
    if fitz is None:
        return ""
    pdf_path = os.path.join(base_dir, "真题模拟题", filename)
    if not os.path.exists(pdf_path):
        return ""
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text("text") for page in doc).strip()

def add_pdf_text_block(story, title, text, st, max_chars=None):
    story.append(Paragraph(safe_xml(title), st['sub_title']))
    if not text:
        story.append(Paragraph("未能读取文字层，后续以题面图片或人工整理方式补充。", st['tip']))
        return
    cleaned = re.sub(r"\s+", " ", text).strip()
    if max_chars:
        cleaned = cleaned[:max_chars]
    for i in range(0, len(cleaned), 650):
        story.append(Paragraph(safe_xml(cleaned[i:i+650]), st['body']))

def add_17th_province_summary(story, st):
    story.append(Paragraph("第17届省赛题目摘要", st['sub_title']))
    story.append(Paragraph("完整原题以扫描页形式保留在后续题面页中。这里先整理为纸质手册可快速复盘的结构化摘要，便于赛场前训练时抓住命题目标。", st['body']))
    rows = [
        [Paragraph("试题", st['th']), Paragraph("考点", st['th']), Paragraph("复盘重点", st['th'])],
        [Paragraph("客观题", st['td']), Paragraph("FPGA资源、复位、SPI、移位寄存器、差分信号、RS-232、ESD、卡诺图、I2C吞吐、亚稳态", st['td_l']), Paragraph("每题都要能反推到硬件或时序原因，不能只背选项。", st['td_l'])],
        [Paragraph("程序设计题", st['td']), Paragraph("串行工序控制器：IDLE、LOAD、PROCESS、INSPECT、UNLOAD、ERROR", st['td_l']), Paragraph("典型FSM综合题，核心是状态跳转、倒计时、ADC阈值、暂停恢复和显示映射。", st['td_l'])],
    ]
    t = Table(rows, colWidths=[2.6*cm, 7.2*cm, 5.2*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 4), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(table_caption(st, "第17届省赛题目摘要"))
    story.append(t)
    states = [
        [Paragraph("状态", st['th']), Paragraph("进入/保持条件", st['th']), Paragraph("动作", st['th'])],
        [Paragraph("IDLE", st['td']), Paragraph("复位后默认；ADC<128时S1无效", st['td_l']), Paragraph("LD1亮，等待原材料就绪和启动", st['td_l'])],
        [Paragraph("LOAD", st['td']), Paragraph("ADC>=128且S1按下", st['td_l']), Paragraph("持续5秒，LD2亮", st['td_l'])],
        [Paragraph("PROCESS", st['td']), Paragraph("LOAD计时结束", st['td_l']), Paragraph("持续8秒，输出1kHz 90%占空比，LD3亮", st['td_l'])],
        [Paragraph("INSPECT", st['td']), Paragraph("PROCESS计时结束", st['td_l']), Paragraph("持续8秒，输出1kHz 10%占空比；ADC<32立即进ERROR", st['td_l'])],
        [Paragraph("UNLOAD", st['td']), Paragraph("INSPECT正常结束", st['td_l']), Paragraph("持续5秒；N>1则N减1回LOAD，否则回IDLE", st['td_l'])],
        [Paragraph("ERROR", st['td']), Paragraph("检测中ADC<32", st['td_l']), Paragraph("LD6每0.2秒闪烁，S4人工重置回IDLE", st['td_l'])],
    ]
    story.append(Paragraph("程序设计题FSM速查", st['sub_title']))
    t = Table(states, colWidths=[2.4*cm, 5.8*cm, 6.8*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "程序设计题FSM速查"))
    story.append(t)

def add_exam_training_index(story, st):
    story.append(Paragraph("真题训练索引与错题复盘表", st['sub_title']))
    story.append(Paragraph("扫描题面已经完整保留在后续页面。纸质训练时先看本表，知道每组题对应哪些知识点；做完后把错因写在题号旁，再回到对应章节补知识。", st['body']))
    rows = [
        [Paragraph("题面", st['th']), Paragraph("重点知识点", st['th']), Paragraph("错题回看位置", st['th'])],
        [Paragraph("第16届省赛真题", st['td']), Paragraph("逻辑门、D触发器、PLL、Verilog基础、FPGA资源", st['td_l']), Paragraph("第三章数字系统设计、第二章约束、第四章基础驱动", st['td_l'])],
        [Paragraph("第17届省赛客观题", st['td']), Paragraph("FPGA资源、复位、SPI、移位寄存器、差分信号、RS-232、I2C吞吐、亚稳态", st['td_l']), Paragraph("第三章协议与亚稳态、赛场速查卡", st['td_l'])],
        [Paragraph("第17届省赛设计题", st['td']), Paragraph("串行工序FSM、ADC阈值、倒计时、按键、LED、数码管", st['td_l']), Paragraph("第三章FSM拆解、第五章top结构", st['td_l'])],
        [Paragraph("十六届模拟I/II/III", st['td']), Paragraph("Verilog声明、组合/时序逻辑、工程流程、状态机和接口概念", st['td_l']), Paragraph("零基础学习路线、第三章核心原理", st['td_l'])],
        [Paragraph("十七届模拟I/II/III", st['td']), Paragraph("同步复位、有符号位宽、always敏感列表、外设控制、综合常识", st['td_l']), Paragraph("第三章设计方法、第四章驱动源码", st['td_l'])],
    ]
    t = Table(rows, colWidths=[3.3*cm, 6.7*cm, 5*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "真题训练索引与错题复盘"))
    story.append(t)

    story.append(Paragraph("真题模拟题训练顺序", st['sub_title']))
    story.append(Paragraph("零基础训练不要一上来就做完整综合题。先用模拟题扫概念和语法，再用省赛客观题查漏，最后做设计题和国赛综合题。每次训练都要限制时间，因为赛场问题往往不是不会，而是来不及定位。", st['body']))
    plan = [
        [Paragraph("顺序", st['th']), Paragraph("题组", st['th']), Paragraph("限时", st['th']), Paragraph("训练目标", st['th']), Paragraph("通过标准", st['th'])],
        [Paragraph("1", st['td']), Paragraph("十六届模拟I/II/III", st['td_l']), Paragraph("每套30min", st['td']), Paragraph("扫Verilog语法、组合/时序逻辑、工程流程", st['td_l']), Paragraph("错题能归类到语法、时序或硬件概念。", st['td_l'])],
        [Paragraph("2", st['td']), Paragraph("第十六届省赛真题", st['td_l']), Paragraph("45min", st['td']), Paragraph("复核逻辑门、触发器、PLL、FPGA资源基础", st['td_l']), Paragraph("每题能说出排除错误选项的理由。", st['td_l'])],
        [Paragraph("3", st['td']), Paragraph("第十七届省赛客观题", st['td_l']), Paragraph("25min", st['td']), Paragraph("训练SPI、I2C、RS-232、亚稳态和硬件常识", st['td_l']), Paragraph("10题至少8题正确，并能解释硬件原因。", st['td_l'])],
        [Paragraph("4", st['td']), Paragraph("第十七届省赛设计题", st['td_l']), Paragraph("90min", st['td']), Paragraph("按状态机拆工序控制、ADC阈值、PWM和显示", st['td_l']), Paragraph("先画状态图，再写顶层模块划分。", st['td_l'])],
        [Paragraph("5", st['td']), Paragraph("十七届模拟I/II/III", st['td_l']), Paragraph("每套35min", st['td']), Paragraph("压测同步复位、位宽、有符号数、综合语义", st['td_l']), Paragraph("能把错误对应到本书前置速查页。", st['td_l'])],
        [Paragraph("6", st['td']), Paragraph("第16届国赛综合题", st['td_l']), Paragraph("150min", st['td']), Paragraph("完整拆采集、存储、算法、显示、串口上报", st['td_l']), Paragraph("先完成可观察最小系统，再逐步加算法。", st['td_l'])],
    ]
    t = Table(plan, colWidths=[1.4*cm, 3.4*cm, 2*cm, 4.2*cm, 4*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('ALIGN', (0,1), (0,-1), 'CENTER'), ('TOPPADDING', (0,0), (-1,-1), 3),
                           ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "真题模拟题训练顺序"))
    story.append(t)

    record = [
        [Paragraph("日期", st['th']), Paragraph("题组", st['th']), Paragraph("正确率/完成度", st['th']), Paragraph("最大问题", st['th']), Paragraph("回看章节", st['th'])],
        [Paragraph("____", st['td']), Paragraph("____", st['td']), Paragraph("____", st['td']), Paragraph("____", st['td']), Paragraph("____", st['td'])],
        [Paragraph("____", st['td']), Paragraph("____", st['td']), Paragraph("____", st['td']), Paragraph("____", st['td']), Paragraph("____", st['td'])],
        [Paragraph("____", st['td']), Paragraph("____", st['td']), Paragraph("____", st['td']), Paragraph("____", st['td']), Paragraph("____", st['td'])],
    ]
    t = Table(record, colWidths=[2.2*cm, 3.2*cm, 3.2*cm, 3.6*cm, 2.8*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('ALIGN', (0,1), (-1,-1), 'CENTER'), ('TOPPADDING', (0,0), (-1,-1), 5),
                           ('BOTTOMPADDING', (0,0), (-1,-1), 5)]))
    story.append(KeepTogether([
        Paragraph("训练记录栏", st['sub_title']),
        table_caption(st, "真题训练记录栏"),
        t,
    ]))

    review = [
        [Paragraph("错因", st['th']), Paragraph("典型表现", st['th']), Paragraph("修正动作", st['th'])],
        [Paragraph("概念不清", st['td']), Paragraph("能选答案但说不出原因", st['td_l']), Paragraph("回到对应协议/状态机小节，用一句话解释规则。", st['td_l'])],
        [Paragraph("时序错误", st['td']), Paragraph("仿真能跑，板上偶发错误", st['td_l']), Paragraph("检查同步器、消抖、计数边界、状态跳转条件。", st['td_l'])],
        [Paragraph("极性错误", st['td']), Paragraph("LED/数码管/按键表现相反", st['td_l']), Paragraph("查CT137X引脚表和原理图，确认低有效或高有效。", st['td_l'])],
        [Paragraph("接口混淆", st['td']), Paragraph("把I2C ACK、SPI片选、UART帧格式混在一起", st['td_l']), Paragraph("画出一帧时序，标出谁驱动线、谁采样线。", st['td_l'])],
    ]
    story.append(Paragraph("错题复盘模板", st['sub_title']))
    t = Table(review, colWidths=[2.6*cm, 5.4*cm, 7*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "错题复盘模板"))
    story.append(t)

def add_16th_national_summary(story, st):
    story.append(Paragraph("第16届国赛题目完整结构", st['sub_title']))
    story.append(Paragraph("第16届国赛题不是单一外设题，而是“动态数据采集 + 算法处理 + 显示交互 + 串口上报”的综合系统题。纸质手册复盘时要先抓住系统边界，再看四个算法细节。", st['body']))
    overview = [
        [Paragraph("模块", st['th']), Paragraph("题目要求", st['th']), Paragraph("工程实现抓手", st['th'])],
        [Paragraph("硬件资源", st['td']), Paragraph("50MHz时钟、复位、2个4位8段数码管、4个独立按键、LED、USB转串口、DS1302、ADC081C021", st['td_l']), Paragraph("顶层端口先按CT137X引脚表固定，RTC提供时间戳，ADC提供0-127采样值。", st['td_l'])],
        [Paragraph("性能", st['td']), Paragraph("按键响应小于等于0.1秒；至少支持16个数据输入；数码管稳定无重影", st['td_l']), Paragraph("按键用10ms/20ms消抖；数据数组按至少16深度设计；数码管1kHz左右扫描。", st['td_l'])],
        [Paragraph("数据录入", st['td']), Paragraph("ADC把0-3.3V映射为0-127，S1触发录入当前转换值", st['td_l']), Paragraph("ADC持续刷新current_adc，S1脉冲把current_adc写入data_mem[wr_ptr]并记录RTC时间。", st['td_l'])],
        [Paragraph("算法", st['td']), Paragraph("极值统计、无损压缩、滑动平均滤波、最大-最小归一化", st['td_l']), Paragraph("S4启动多拍计算状态机；每个时钟处理一个元素，完成后置done并进入结果界面。", st['td_l'])],
        [Paragraph("显示", st['td']), Paragraph("录入界面显示界面标识、最近录入值、当前ADC值；结果界面显示算法结果", st['td_l']), Paragraph("显示控制单独写成display_mux，按界面状态和算法编号选择8位数码管内容。", st['td_l'])],
        [Paragraph("串口", st['td']), Paragraph("115200/8N1字符串输出；录入数据和算法结果带时间戳", st['td_l']), Paragraph("先把结果格式化为ASCII缓冲区，再由uart_string_sender逐字节发送。", st['td_l'])],
    ]
    t = Table(overview, colWidths=[2.3*cm, 6.3*cm, 6.4*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "第16届国赛模块与要求"))
    story.append(t)

    story.append(Paragraph("界面与按键功能速查", st['sub_title']))
    keys = [
        [Paragraph("按键", st['th']), Paragraph("录入界面", st['th']), Paragraph("结果界面", st['th']), Paragraph("设计注意", st['th'])],
        [Paragraph("S1", st['td']), Paragraph("录入当前ADC数字量", st['td_l']), Paragraph("无定义，保持当前状态", st['td_l']), Paragraph("只响应消抖后的单周期脉冲。", st['td_l'])],
        [Paragraph("S2", st['td']), Paragraph("切换算法：A1极值、A2压缩、A3滤波、A4归一化", st['td_l']), Paragraph("任意界面下有效，循环切换算法", st['td_l']), Paragraph("算法编号和显示标识必须同步更新。", st['td_l'])],
        [Paragraph("S3", st['td']), Paragraph("串口输出当前已录入数据", st['td_l']), Paragraph("切换显示当前算法的下一条结果", st['td_l']), Paragraph("录入上报和结果翻页是同一个按键的两种语义。", st['td_l'])],
        [Paragraph("S4", st['td']), Paragraph("按当前算法执行计算并更新结果", st['td_l']), Paragraph("清除录入数据和计算结果，返回录入界面", st['td_l']), Paragraph("清零时要同时清wr_ptr、result_ptr和done标志。", st['td_l'])],
        [Paragraph("RESET", st['td']), Paragraph("全局复位", st['td_l']), Paragraph("全局复位", st['td_l']), Paragraph("恢复初始状态，界面回录入界面。", st['td_l'])],
    ]
    t = Table(keys, colWidths=[1.6*cm, 4.4*cm, 4.4*cm, 4.6*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "界面与按键功能速查"))
    story.append(t)

    story.append(Paragraph("串口上报格式", st['sub_title']))
    uart = [
        [Paragraph("类型", st['th']), Paragraph("触发条件", st['th']), Paragraph("格式", st['th']), Paragraph("例子/说明", st['th'])],
        [Paragraph("录入数据上报", st['td']), Paragraph("录入界面按S3", st['td_l']), Paragraph("[时间戳][数值][时间戳][数值]...", st['td_l']), Paragraph("时间戳来自每个数值的录入时间。", st['td_l'])],
        [Paragraph("极值统计", st['td']), Paragraph("S4计算完成", st['td_l']), Paragraph("[时间戳][A1][(最小值,位置),(最大值,位置)]", st['td_l']), Paragraph("例：[145643][A1][(8,6),(99,3)]", st['td_l'])],
        [Paragraph("无损压缩", st['td']), Paragraph("S4计算完成", st['td_l']), Paragraph("[时间戳][A2][(数值,游程长度),数值...]", st['td_l']), Paragraph("游程长度>=2输出二元组，否则输出单值。", st['td_l'])],
        [Paragraph("滑动平均", st['td']), Paragraph("S4计算完成", st['td_l']), Paragraph("[时间戳][A3][滤波结果序列]", st['td_l']), Paragraph("窗口固定为3，输出长度为N-2。", st['td_l'])],
        [Paragraph("归一化", st['td']), Paragraph("S4计算完成", st['td_l']), Paragraph("[时间戳][A4][0.xx结果序列]", st['td_l']), Paragraph("定点放大100倍实现两位小数。", st['td_l'])],
    ]
    t = Table(uart, colWidths=[2.2*cm, 3*cm, 5.4*cm, 4.4*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "串口上报格式"))
    story.append(t)

    story.append(Paragraph("推荐顶层状态划分", st['sub_title']))
    add_paras(story, [
        "建议至少拆成三个互不混乱的控制状态机：界面状态机负责INPUT/RESULT两个界面；算法状态机负责IDLE/CALC/DONE；串口状态机负责IDLE/FORMAT/SEND。不要让一个always块同时处理按键、算法循环、数码管和UART，否则调试时很难判断是哪一层出错。",
        "赛场实现时，先保证S1录入、数码管显示ADC和已录入值，再接入S2算法编号，随后实现S4计算，最后补S3串口上报。这个顺序能保证每一步都有可观察输出，不会在最后集成时一次暴露太多问题。"
    ], st)

# ==================== 真题实战章节 ====================
def build_chapter3(st, base_dir=None):
    story = []
    story.append(ChapterMarker("ch3", chapter_pages))
    story.append(Paragraph("第三章  核心原理与真题实战", st['ch_title']))
    story.append(DecorLine())
    story.append(Spacer(1, 3*mm))

    story.append(ChapterMarker("ch3_1", chapter_pages))
    story.append(Paragraph("3.1  数字系统设计方法", st['sec_title']))
    add_paras(story, [
        "FPGA不是按顺序执行程序的单片机，而是在芯片内部生成真实的并行数字电路。Verilog代码中的每个寄存器、组合表达式和状态机，综合后都会变成触发器、查找表、连线和片上存储资源。因此读题时不能只问“这段程序怎么跑”，而要问“这条数据通路在哪里、寄存器什么时候更新、控制信号由哪个状态产生”。",
        "竞赛工程最稳的拆法是五层：输入采样层负责按键、串口、ADC等异步或低速输入；时序控制层负责分频、计数和状态机；数据存储层负责寄存器数组、SRAM或Flash；算法层负责最大最小、滤波、压缩等计算；显示输出层负责数码管、LED和UART上报。这样拆分后，单个模块容易仿真，也便于在赛场上快速定位问题。",
        "状态机是FPGA控制逻辑的核心。三段式状态机把“当前状态寄存器”“下一状态判断”“输出控制”分开写，优点是波形清楚、组合环路风险低、综合结果稳定。Moore型状态机的输出只取决于当前状态，输出更稳；Mealy型状态机的输出同时取决于状态和输入，响应更快但更容易产生毛刺。竞赛中外设时序优先用Moore，按键触发或握手响应可适当使用Mealy。",
        "亚稳态来自跨时钟域或异步输入。例如UART_RX、按键和外部IO都不一定和50MHz系统时钟对齐，信号刚好在采样边沿附近变化时，触发器可能短时间处于不确定电平。工程上常用两级同步器：第一级承担亚稳态风险，第二级输出给后续逻辑，虽然不能把风险降为零，但能把故障概率降到工程可接受范围。",
        "机械按键不是理想开关，按下和松开时金属触点会抖动，持续时间通常为几毫秒到十几毫秒。如果直接用50MHz采样，一个按键动作可能被识别成很多次。常见做法是先分频到100Hz或50Hz，相当于每10ms或20ms采样一次；只有相邻采样值稳定变化时，才输出一个系统可识别的单周期按下脉冲。"
    ], st)
    story.append(Paragraph("三段式状态机模板", st['sub_title']))
    story.append(Preformatted("""// 1. 当前状态寄存器：只在时钟边沿更新
always @(posedge clk or negedge rst_n) begin
    if (!rst_n) state <= IDLE;
    else        state <= next_state;
end

// 2. 下一状态组合逻辑：根据当前状态和输入决定跳转
always @(*) begin
    next_state = state;
    case (state)
        IDLE: if (start) next_state = WORK;
        WORK: if (done)  next_state = IDLE;
    endcase
end

// 3. 输出逻辑：把控制信号集中在状态含义里
always @(*) begin
    wr_en = (state == WORK);
end""", st['code']))

    story.append(ChapterMarker("ch3_2", chapter_pages))
    story.append(Paragraph("3.2  I2C/UART/SPI通信协议", st['sec_title']))
    story.append(Paragraph("I2C协议", st['sub_title']))
    add_paras(story, [
        "I2C用SCL和SDA两根线连接多个器件。两根线空闲时都被上拉为高电平，任何器件只能主动拉低，不能主动输出高电平，所以多个器件共享总线时不会直接短路。CT137X上的ADC081C021、DAC5571和AT24C02 EEPROM共用同一组I2C引脚，靠7位器件地址区分目标设备。",
        "一次I2C传输从起始条件开始：SCL保持高电平时，SDA从高变低。随后主机发送7位地址和1位读写方向位，方向位为0表示写，为1表示读。每发送8位数据后，第9个时钟是应答位，接收方把SDA拉低表示ACK；如果SDA保持高电平，则表示NACK，通常代表器件不存在、忙或不接受更多数据。",
        "I2C时序最容易错的地方是SDA变化时机。规则是：SCL高电平期间SDA必须稳定，SCL低电平期间才允许改变数据；只有起始和停止条件例外。因此驱动中通常在SCL低电平的1/4周期更新SDA，在SCL高电平的3/4周期采样SDA。"
    ], st)
    story.append(Preformatted("""I2C字节传输：
SDA: START A6 A5 A4 A3 A2 A1 A0 R/W ACK D7 ... D0 ACK STOP
SCL:       _|‾|_|‾|_|‾|_|‾|_|‾|_|‾|_|‾|_|‾|_|‾|_|‾|_
规则：SCL高电平采样，SCL低电平改变SDA。""", st['code']))
    story.append(Paragraph("UART协议", st['sub_title']))
    add_paras(story, [
        "UART是异步串口，没有专用时钟线，发送端和接收端必须约定同一个波特率。常见配置115200/8N1表示每秒115200个符号，8个数据位，无校验位，1个停止位。线路空闲为高电平，一帧数据以低电平起始位开始，随后按低位在前发送8位数据，最后用高电平停止位结束。",
        "在50MHz系统时钟下，115200波特率对应的计数值约为50_000_000 / 115200 = 434。发送模块每计满434个系统时钟切换到下一位；接收模块检测到下降沿后，先等半个波特周期在起始位中间确认，再每隔一个波特周期采样数据位，这样能避开边沿抖动。"
    ], st)
    story.append(Preformatted("""UART 8N1帧：
空闲  起始位  bit0 bit1 bit2 bit3 bit4 bit5 bit6 bit7  停止位
  1      0      LSB ---------------------------> MSB     1""", st['code']))
    story.append(Paragraph("SPI协议", st['sub_title']))
    add_paras(story, [
        "SPI是主从式同步总线，主机控制CS片选和SCLK时钟，MOSI负责主机到从机，MISO负责从机到主机。和UART不同，SPI每一位都跟随SCLK边沿移动，因此速率可以更高，时序也更直接。标准SPI在发送MOSI的同时采样MISO，所以天然支持全双工。",
        "CPOL决定SCLK空闲电平，CPHA决定第几个边沿采样。CPOL=0时空闲低，CPOL=1时空闲高；CPHA=0表示第一个有效边沿采样，CPHA=1表示第二个有效边沿采样。主从双方的CPOL/CPHA必须一致，否则会出现整体位移一位或采样到错误数据。",
        "DS1302常被称为类SPI器件，但它不是标准四线SPI：它使用CE、SCLK和单根双向DATA，且数据位序通常是LSB first。工程中可先用通用SPI主机产生时钟和移位，再通过ds1302_io_convert模块处理三态方向、CE极性和位序翻转。"
    ], st)
    spi_tbl = [[Paragraph(x, st['th']) for x in ["模式", "CPOL", "CPHA", "空闲时钟", "采样边沿"]],
               [Paragraph(x, st['td']) for x in ["0", "0", "0", "低", "第1边沿"]],
               [Paragraph(x, st['td']) for x in ["1", "0", "1", "低", "第2边沿"]],
               [Paragraph(x, st['td']) for x in ["2", "1", "0", "高", "第1边沿"]],
               [Paragraph(x, st['td']) for x in ["3", "1", "1", "高", "第2边沿"]]]
    t = Table(spi_tbl, colWidths=[2*cm, 2*cm, 2*cm, 3*cm, 3*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('ALIGN', (0,0), (-1,-1), 'CENTER')]))
    story.append(table_caption(st, "SPI模式配置"))
    story.append(t)

    story.append(ChapterMarker("ch3_3", chapter_pages))
    story.append(Paragraph("3.3  板载外设时序原理", st['sec_title']))
    story.append(Paragraph("数码管动态扫描", st['sub_title']))
    add_paras(story, [
        "CT137X使用8位共阳极数码管，段选和位选都是低电平有效。多位数码管不是8位同时各接一套段线，而是共用同一组段选线，再用位选逐位点亮。控制器在很短时间内依次显示第1位、第2位直到第8位，只要刷新足够快，人眼因为视觉暂留会认为所有位同时亮。",
        "如果扫描频率过低会闪烁，如果位切换前没有先关断段选，可能出现重影。常用策略是1kHz左右切位，8位平均下来每位约125Hz；每次切换时先关闭所有位选，更新段码，再打开目标位选。"
    ], st)
    story.append(Paragraph("SRAM读写时序", st['sub_title']))
    add_paras(story, [
        "IS63WV1288是异步SRAM，没有SCLK输入，读写靠地址线、数据线和CE/OE/WE控制。写操作时先给出稳定地址和数据，再拉低CE和WE，保持足够写脉宽后释放WE；读操作时先给出地址并拉低CE/OE，等待访问时间后再采样数据总线。",
        "地址建立时间表示控制信号有效前地址必须提前稳定多久，保持时间表示控制信号释放后地址还要继续保持多久。FPGA里通常用状态机把一次访问拆成SETUP、ACCESS、HOLD几个时钟周期，即使板卡和芯片速度足够快，也不要把地址、WE和数据在同一个组合表达式里瞬间改变。"
    ], st)
    story.append(Paragraph("DS1302 RTC", st['sub_title']))
    add_paras(story, [
        "DS1302保存秒、分、时、日、月、星期、年等BCD寄存器。BCD不是普通二进制，例如十进制59表示为0x59，高4位是十位5，低4位是个位9。读出时间后，如果要显示到数码管，BCD格式反而很方便；如果要做加减运算，则应先转成普通二进制。",
        "DS1302通信使用CE、SCLK、DATA三线。CE拉高后开始传输命令字，命令最低位决定读写方向，地址位选择寄存器。它也支持突发读写：先发送burst命令，然后连续读出或写入多个时间寄存器，减少重复片选和命令开销。上电后要注意秒寄存器最高位CH，CH=1表示时钟暂停，需要清零才能让晶振运行。"
    ], st)
    story.append(Paragraph("W25Q128 Flash", st['sub_title']))
    add_paras(story, [
        "W25Q128是128Mbit SPI NOR Flash，容量为16MByte。它的擦除粒度通常大于写入粒度：可以按页编程，一页常见为256字节；但擦除必须按扇区或块进行，常用4KB扇区擦除。Flash只能把1写成0，不能直接把0写回1，所以写入前若目标区域不是全0xFF，必须先擦除。",
        "常用命令包括0x9F读JEDEC ID、0x06写使能、0x05读状态寄存器、0x03读数据、0x02页编程、0x20扇区擦除。页编程和擦除都是内部耗时操作，发完命令不能立刻认为完成，必须轮询状态寄存器WIP位，直到WIP=0再进行下一次访问。"
    ], st)

    story.append(ChapterMarker("ch3_4", chapter_pages))
    story.append(Paragraph("3.4  第16届蓝桥杯FPGA国赛算法拆解", st['sec_title']))
    story.append(Paragraph("基于FPGA设计动态数据采集系统：ADC产生128个数字量，按键触发录入，集成极值统计、"
                           "无损压缩、滑动平均滤波、归一化四种算法，数码管显示结果，串口上报数据。", st['body']))
    add_16th_national_summary(story, st)
    add_paras(story, [
        "这类综合题不要先写顶层，而要先把系统分成“采集、存储、计算、显示、上报”五个可验证模块。ADC模块持续刷新当前电压对应的0到127数字量；S1只在按键脉冲到来时把当前ADC值写入数组，同时记录RTC时间戳；S2只改变当前算法编号；S4触发计算状态机；S3根据当前界面选择串口上报或结果翻页。",
        "数据量至少16个，题目又要求支持128个数字量范围，所以存储宽度可按7位或8位设计。为了简化串口格式化，内部通常用8位保存采样值，用额外计数器保存已录入数量。算法计算不要在一个时钟里写完所有循环，应该设计为多拍扫描状态机：每个时钟处理一个元素，处理完后置done标志。"
    ], st)

    for name, desc, example, method in [
        ("极值统计", "统计最小值和最大值及其出现次数",
         "[62,88,88,99,99,9,8,88] → MIN=(8,6), MAX=(99,3)",
         "遍历数组，两个寄存器记录当前最小/最大值，计数器记录次数。O(n)时间复杂度。"),
        ("无损压缩(游程编码)", "对连续重复数据进行RLE压缩",
         "[88,88,88,99,99,9,8,88] → (88,3),(99,2),9,8,88",
         "顺序扫描，当前值与前值相同则计数+1，不同则输出(值,计数)对。游程≥2输出对，否则直接输出值。"),
        ("滑动平均滤波", "窗口=3的滑动平均，保留整数",
         "[62,88,88,99,99,9,8,88] → [79,91,95,69,38,35]",
         "对每个位置i(1~N-2)，取(data[i-1]+data[i]+data[i+1])/3取整。输出长度=N-2。"),
        ("最大-最小归一化", "归一化到[0,1]，保留2位小数",
         "[127,8,10,2,8] → [1.00,0.05,0.06,0.00,0.05]",
         "公式：(value-min)/(max-min)。定点数实现：先×100再÷(max-min)。注意max==min时除零保护。"),
    ]:
        story.append(Paragraph(f"① {name}" if name == "极值统计" else
                               f"② {name}" if "无损" in name else
                               f"③ {name}" if "滑动" in name else f"④ {name}", st['sub_title']))
        story.append(Paragraph(f"<b>功能：</b>{desc}", st['body']))
        story.append(Paragraph(f"<b>示例：</b>{example}", st['body']))
        story.append(Paragraph(f"<b>实现：</b>{method}", st['comment']))

    story.append(Paragraph("串口通信格式", st['sub_title']))
    story.append(Paragraph("115200/8N1，字符串格式输出。", st['body']))
    story.append(Paragraph("录入上报：[时间戳][数值][时间戳][数值]...", st['body']))
    story.append(Paragraph("算法上报：[时间戳][A1/A2/A3/A4][结果数据]", st['body']))

    story.append(ChapterMarker("ch3_5", chapter_pages))
    story.append(Paragraph("3.5  全部真题与模拟题题面", st['sec_title']))
    if base_dir:
        story.append(Paragraph("第17届省赛结构化整理", st['sub_title']))
        add_paras(story, [
            "第17届省赛资料中，客观题和程序设计题带有可抽取文字层，本版直接纳入教材。客观题适合作为赛前概念自测；程序设计题是典型FSM综合题，要求把工序控制、ADC阈值判断、按键、LED和数码管显示组合成完整系统。",
        ], st)
        add_17th_province_summary(story, st)
    add_paras(story, [
        "本节把已提取的扫描题面逐页嵌入教材，便于离线复习和对照训练。扫描页主要来自四梯练习系统的个人练习结果解析，题型以客观选择题为主，覆盖FPGA基础、Verilog语法、组合/时序逻辑、复位、PLL、计数器、通信协议和外设应用。由于这些PDF没有可抽取文字层，本版采用原图保真嵌入，后续迭代会继续补充人工文字化解析。",
        "使用方法：先遮住正确答案独立作答，再对照页内答案；错题不要只记选项，要回到本章前面的协议、状态机和时序原理重新解释一遍。能够用自己的话解释错误原因，比单纯记住答案更接近赛场可迁移能力。"
    ], st)
    add_exam_reading_guide(story, st)
    add_exam_annotation_template(story, st)

    # ==================== 第17届省赛客观题逐题解析 ====================
    story.append(Paragraph("第17届省赛客观题逐题解析", st['sub_title']))
    story.append(Paragraph("以下为10道客观题的正确答案和逐题分析，每题1.5分，共15分。错题不要只记选项，要回到对应章节重新理解原理。", st['body']))
    obj_qa = [
        ("01", "FPGA内部资源包含哪些", "ABCD", "FPGA四大核心资源：RAM(BRAM)、布线资源、可编程逻辑块(CLB)、可编程IO单元(IOB)。"),
        ("02", "FPGA复位电路说法", "ACD", "异步复位立即生效(A对)，但抗干扰不如同步复位(B错)；可设高低有效(C对)；同步复位需时钟沿(D对)。"),
        ("03", "SPI通信协议说法", "AB", "SPI支持全双工(A对)、有独立SCK(B对)；用CS片选而非地址(C错)；无ACK机制(D错)。"),
        ("04", "移位寄存器说法", "BCD", "移位寄存器是时序电路(A错)；可由触发器级联(B对)、实现延迟(C对)、串并转换(D对)。"),
        ("05", "差分信号线优点", "ABD", "抗共模干扰(A对)、降EMI(B对)；差分需两根线(C错)；低压高速(D对)。"),
        ("06", "RS-232串口说法", "AC", "负逻辑电平(A对)；单端信号非差分(B错)；异步无时钟(C对)；TTL需电平转换(D错)。"),
        ("07", "USB2.0 ESD防护参数", "ABC", "结电容(A)、导通电压(B)、封装寄生(C)是关键；散热功率(D)非关键。"),
        ("08", "卡诺图化简目的", "BC", "找最简表达式(B对)、减少逻辑门(C对)；与时序违例(A)和工作频率(D)无关。"),
        ("09", "I2C 400kHz发4KB需时", "B", "4096字节x9时钟/字节=36864, 36866/400kHz\u224892ms。"),
        ("10", "仿真正常硬件偶尔死机", "CD", "电源噪声(C)和跨时钟域亚稳态(D)是常见硬件独有bug。"),
    ]
    for num, question, answer, explanation in obj_qa:
        story.append(Paragraph(f"<b>{num}. {question}</b>  \u2192 {answer}", st['body']))
        story.append(Paragraph(explanation, st['comment']))

    # ==================== 第17届省赛设计题实现指南 ====================
    story.append(Paragraph("第17届省赛设计题实现指南", st['sub_title']))
    story.append(Paragraph("串行工序控制器：IDLE\u2192LOAD\u2192PROCESS\u2192INSPECT\u2192UNLOAD循环，支持N次循环、暂停恢复、ADC阈值检测和1kHz PWM输出。以下为关键实现要点。", st['body']))

    design_rows = [
        [Paragraph("设计要素", st['th']), Paragraph("具体要求", st['th']), Paragraph("实现抓手", st['th'])],
        [Paragraph("状态机", st['td']), Paragraph("6状态：IDLE/LOAD/PROCESS/INSPECT/UNLOAD/ERROR", st['td_l']), Paragraph("三段式FSM，跳转条件见状态表", st['td_l'])],
        [Paragraph("倒计时", st['td']), Paragraph("LOAD/UNLOAD=5秒，PROCESS/INSPECT=8秒", st['td_l']), Paragraph("50MHz计数器，状态切换时重载", st['td_l'])],
        [Paragraph("按键有效性", st['td']), Paragraph("S1/S2仅IDLE有效，S3仅工序状态有效，S4仅ERROR有效", st['td_l']), Paragraph("用state条件门控消抖后的按键脉冲", st['td_l'])],
        [Paragraph("PWM输出", st['td']), Paragraph("PROCESS: 1kHz 90%占空比；INSPECT: 1kHz 10%占空比", st['td_l']), Paragraph("50000周期计数器，比较阈值切换", st['td_l'])],
        [Paragraph("ERROR触发", st['td']), Paragraph("INSPECT中ADC<32立即跳ERROR", st['td_l']), Paragraph("在INSPECT状态内检测ADC值", st['td_l'])],
        [Paragraph("LED指示", st['td']), Paragraph("LD1-LD5各对应一个工序，LD6在ERROR时0.2s闪烁", st['td_l']), Paragraph("LD6用10M周期计数器翻转", st['td_l'])],
    ]
    t = Table(design_rows, colWidths=[2.5*cm, 5.5*cm, 6*cm])
    t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), C['primary']), ('GRID', (0,0), (-1,-1), 0.5, C['border']),
                           ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                           ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(table_caption(st, "17届省赛设计题关键实现要素"))
    story.append(t)

    add_exam_training_index(story, st)
    summaries = {
        "第十六届 蓝桥杯（电子类）FPGA设计与开发省赛真题": "省赛真题客观题，重点覆盖逻辑门、D触发器、PLL、Verilog语法、FPGA资源和基础时序概念。",
        "第十七届蓝桥杯FPGA省赛真题": "第17届省赛客观题，共10题，覆盖FPGA资源、复位、SPI、移位寄存器、差分信号、RS-232、ESD、卡诺图、I2C吞吐和亚稳态。",
        "第十七届蓝桥杯FPGA省赛真题_设计题": "第17届省赛程序设计题，串行工序控制器，重点考FSM、ADC阈值、倒计时、按键控制、LED报警和数码管显示。",
        "十六届蓝桥杯FPGA模拟试题I": "模拟试题I，重点覆盖FPGA与ASIC区别、Verilog寄存器声明、组合逻辑、基础时序和常用接口概念。",
        "十六届蓝桥杯FPGA模拟试题Ⅱ": "模拟试题II，重点覆盖数字逻辑、Verilog表达式、时钟复位、存储器和通信协议基础。",
        "十六届蓝桥杯FPGA模拟试题Ⅲ": "模拟试题III，重点覆盖FPGA工程流程、时序约束、状态机、串口/I2C/SPI和板载外设理解。",
        "第十七届FPGA模拟考试Ⅰ": "第17届模拟考试I，重点覆盖同步复位、FPGA可重构优势、有符号位宽、Verilog always敏感列表和协议选择。",
        "第十七届FPGA模拟考试Ⅱ": "第17届模拟考试II，重点覆盖Verilog综合语义、时钟域处理、外设控制、数码管显示和常见赛题知识点。",
        "第十七届FPGA模拟考试Ⅲ": "第17届模拟考试III，重点覆盖FPGA基础概念、Verilog语义、外设接口和综合设计常识。",
    }
    groups = exam_image_groups(base_dir) if base_dir else []
    if not groups:
        story.append(Paragraph("未找到 extracted_images 目录，跳过扫描题面嵌入。", st['tip']))
    for exam_name, pages in groups:
        story.append(PageBreak())
        story.append(Paragraph(safe_xml(exam_name), st['sec_title']))
        story.append(Paragraph(summaries.get(exam_name, "扫描题面页。"), st['desc_box']))
        story.append(Paragraph("阅读动作：先用本节的标记规范圈出硬件对象和时间参数，再回到前面的协议、状态机、计数器和板卡资料章节查证。完成一套后，把错因写入“真题训练记录栏”。", st['tip']))
        for idx, img_path in enumerate(pages, 1):
            story.append(Paragraph(f"题面页 {idx}/{len(pages)}", st['sub_title']))
            add_exam_image(story, img_path, st)
            story.append(figure_caption(st, f"{safe_xml(exam_name)} 题面页 {idx}"))
            if idx != len(pages):
                story.append(PageBreak())
    story.append(PageBreak())
    return story

# ==================== 模块代码章节 ====================
def build_code_chapter(title, files, ch_num, st):
    story = []
    key = f"ch{ch_num}"
    story.append(ChapterMarker(key, chapter_pages))
    story.append(Paragraph(title, st['ch_title']))
    story.append(DecorLine())
    story.append(Spacer(1, 3*mm))

    for idx, (fname, content) in enumerate(files, 1):
        sub_key = f"ch{ch_num}_{idx}"
        story.append(ChapterMarker(sub_key, chapter_pages))
        story.append(Paragraph(f"{ch_num}.{idx}  {fname}", st['file_title']))
        story.append(Paragraph(f"<b>功能：</b>{get_module_desc(fname)}", st['desc_box']))
        usage = get_usage_info(fname)
        if usage:
            story.append(Paragraph(usage, st['comment']))
        story.extend(build_annotated_code(fname, content, st))
        story.append(Spacer(1, 3*mm))

    story.append(PageBreak())
    return story

# ==================== 附录 ====================
def build_appendix(st):
    story = []
    story.append(ChapterMarker("appendix", chapter_pages))
    story.append(Paragraph("附    录", ParagraphStyle('AT', fontName='SimHei', fontSize=22, alignment=TA_CENTER,
                                                      textColor=C['primary'], spaceBefore=1.5*cm, spaceAfter=8*mm)))
    story.append(DecorLine(color=C['secondary'], thickness=2))
    story.append(Spacer(1, 5*mm))

    def th(t): return Paragraph(t, st['th'])
    def td(t): return Paragraph(t, st['td'])

    story.append(Paragraph("A. DS1302寄存器地址表", st['sec_title']))
    ds = [
        [th("寄存器"), th("写地址"), th("读地址"), th("数据范围")],
        [td("秒"), td("0x80"), td("0x81"), td("00-59, bit7=CH暂停位")],
        [td("分"), td("0x82"), td("0x83"), td("00-59")],
        [td("时"), td("0x84"), td("0x85"), td("00-23(24h制)")],
        [td("日"), td("0x86"), td("0x87"), td("01-31")],
        [td("月"), td("0x88"), td("0x89"), td("01-12")],
        [td("星期"), td("0x8A"), td("0x8B"), td("01-07")],
        [td("年"), td("0x8C"), td("0x8D"), td("00-99")],
        [td("写保护"), td("0x8E"), td("0x8F"), td("bit7=WP, 0=可写")],
    ]
    t = Table(ds, colWidths=[2.5*cm, 2*cm, 2*cm, 5.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C['primary']),
        ('GRID', (0,0), (-1,-1), 0.5, C['border']),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(table_caption(st, "DS1302寄存器地址表"))
    story.append(t)
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph("B. W25Q128 SPI命令表", st['sec_title']))
    fl = [
        [th("命令"), th("功能"), th("格式")],
        [td("0x06"), td("Write Enable (WREN)"), td("1字节命令")],
        [td("0x05"), td("Read Status Register"), td("命令+1字节返回")],
        [td("0x03"), td("Read Data"), td("命令+3字节地址+N字节返回")],
        [td("0x02"), td("Page Program (Write)"), td("命令+3字节地址+N字节数据")],
        [td("0x20"), td("Sector Erase (4KB)"), td("命令+3字节地址")],
        [td("0x9F"), td("Read JEDEC ID"), td("命令+3字节返回")],
    ]
    t = Table(fl, colWidths=[2*cm, 4*cm, 6*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C['primary']),
        ('GRID', (0,0), (-1,-1), 0.5, C['border']),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(table_caption(st, "W25Q128 SPI命令表"))
    story.append(t)

    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("C. 官方资料依据速查", st['sec_title']))
    story.append(Paragraph("本书的硬件事实优先来自项目 `title` 目录中的官方资料。纸质手册使用时，若代码、网络资料和本表冲突，优先按官方用户手册、引脚表、原理图和芯片数据手册核对。", st['body']))
    docs = [
        [th("资料"), th("用途"), th("赛场查什么")],
        [td("CT137X_UM.pdf"), td("开发板用户手册"), td("平台资源、扩展接口、电源和基本使用方法")],
        [td("CT137X_PIN.pdf/xlsx"), td("官方引脚表"), td("顶层端口到FPGA管脚的唯一依据")],
        [td("CT137X_SCH.pdf"), td("原理图"), td("LED/数码管/蜂鸣器有效电平和外设连接")],
        [td("SEG_TABLE.pdf"), td("段码表"), td("共阳极数码管0-9、空白和特殊符号段码")],
        [td("ADC081C021.pdf"), td("ADC数据手册"), td("I2C地址、8位转换结果、数据格式")],
        [td("DAC5571.pdf"), td("DAC数据手册"), td("I2C写格式、8位输出、上电复位行为")],
        [td("AT24C02.pdf"), td("EEPROM数据手册"), td("页写入、地址字节、写周期等待")],
        [td("DS1302.PDF"), td("RTC数据手册"), td("三线通信、BCD寄存器、CH/WP位、突发读写")],
        [td("IS63WV1288.pdf"), td("SRAM数据手册"), td("异步读写时序、地址/数据/CE/OE/WE")],
        [td("W25Q128.pdf"), td("SPI Flash数据手册"), td("0x9F/0x06/0x05/0x03/0x02/0x20命令")],
    ]
    t = Table(docs, colWidths=[3.6*cm, 4.1*cm, 7.2*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C['primary']),
        ('GRID', (0,0), (-1,-1), 0.5, C['border']),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(table_caption(st, "官方资料依据速查"))
    story.append(t)

    story.append(Paragraph("官方资料查证路径", st['sec_title']))
    story.append(Paragraph("出版稿和赛场手册最怕“凭印象写硬件”。遇到硬件事实不确定时，按下面顺序查证：先定板卡事实，再定芯片协议，最后回到代码和XDC。这样可以避免把网络资料、旧板卡经验或仿真假设误当成当前竞赛平台事实。", st['body']))
    paths = [
        [th("遇到的问题"), th("先查资料"), th("确认后落实到哪里")],
        [td("端口或管脚不确定"), td("CT137X_PIN.pdf/xlsx"), td("顶层端口名、XDC PACKAGE_PIN、IOSTANDARD")],
        [td("LED/数码管极性不确定"), td("CT137X_SCH.pdf + SEG_TABLE.pdf"), td("驱动是否取反、段码表、位选顺序和小数点位置")],
        [td("I2C地址或数据格式不确定"), td("ADC081C021、DAC5571、AT24C02数据手册"), td("器件地址、寄存器地址、读写位、ACK等待和数据位切片")],
        [td("RTC时间读写异常"), td("DS1302.PDF"), td("CH位、WP位、BCD格式、读写地址、三线IO方向")],
        [td("SRAM读写不稳定"), td("IS63WV1288.pdf"), td("地址建立/保持、CE/OE/WE时序和双向数据总线控制")],
        [td("Flash写入或擦除失败"), td("W25Q128.pdf"), td("WREN、WIP轮询、页编程、扇区擦除、3字节地址")],
    ]
    t = Table(paths, colWidths=[4*cm, 4.6*cm, 6.4*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C['primary']),
        ('GRID', (0,0), (-1,-1), 0.5, C['border']),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(table_caption(st, "官方资料查证路径"))
    story.append(t)

    story.append(Paragraph("D. CT137X关键硬件事实", st['sec_title']))
    facts = [
        [th("项目"), th("事实")],
        [td("核心芯片"), td("Xilinx Spartan-7 XC7S6-1FTGB196，板载50MHz时钟接G11")],
        [td("复位"), td("RESET/B6为板级高有效，常在顶层转换为内部低有效sys_rst_n")],
        [td("按键"), td("S1/S2/S3/S4分别接M5/M4/P5/N4，低电平有效")],
        [td("LED"), td("LD1-LD8低电平点亮，输出显示模式前需按硬件极性取反")],
        [td("数码管"), td("8位共阳极，段选SEGA-SEGDP低有效，位选COM1-COM8低有效")],
        [td("I2C"), td("ADC、DAC、EEPROM共用SCL=E11、SDA=M10")],
        [td("RTC"), td("DS1302使用SCLK=A10、CE/RST=A12、DATA=A13")],
        [td("UART"), td("CH340C USB转串口，TX=F12、RX=E12")],
        [td("Flash"), td("W25Q128用户Flash使用CS=D12、SCK=D13、IO0=G14、IO1=F14、IO2=F13、IO3=E13")],
    ]
    t = Table(facts, colWidths=[3.2*cm, 11.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C['primary']),
        ('GRID', (0,0), (-1,-1), 0.5, C['border']),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(table_caption(st, "CT137X关键硬件事实"))
    story.append(t)

    story.append(Spacer(1, 2*cm))
    story.append(DecorLine(color=C['muted'], thickness=0.5))

    # ==================== 参考文献 ====================
    story.append(Spacer(1, 8*mm))

    # ==================== FPGA术语速查 ====================
    story.append(Paragraph("E. FPGA术语速查", st['sec_title']))
    glossary = [
        [th("术语"), th("英文"), th("简要解释")],
        [td("可编程逻辑块"), td("CLB"), td("FPGA基本逻辑单元，包含LUT和触发器")],
        [td("查找表"), td("LUT"), td("实现组合逻辑的基本结构，常见4输入或6输入")],
        [td("触发器"), td("FF / Flip-Flop"), td("时序逻辑基本单元，每个CLB内含2个")],
        [td("块RAM"), td("BRAM"), td("片上存储器，用于FIFO、查找表等")],
        [td("时钟管理单元"), td("CMT / MMCM / PLL"), td("时钟倍频、分频和相移调整")],
        [td("可编程IO"), td("IOB"), td("FPGA引脚单元，支持LVCMOS33等多种电平")],
        [td("综合"), td("Synthesis"), td("Verilog代码→门级网表的转换过程")],
        [td("布局布线"), td("Place & Route"), td("将综合结果映射到FPGA具体资源并连线")],
        [td("比特流"), td("Bitstream"), td("最终下载到FPGA的配置文件，.bit格式")],
        [td("异步复位"), td("Async Reset"), td("复位信号立即生效，不等时钟沿")],
        [td("同步复位"), td("Sync Reset"), td("复位信号需在时钟沿到来时才生效")],
        [td("亚稳态"), td("Metastability"), td("触发器采样边沿附近变化时的不确定状态")],
        [td("两级同步器"), td("2-FF Synchronizer"), td("解决跨时钟域亚稳态的标准方法")],
        [td("状态机"), td("FSM"), td("控制逻辑的核心结构，贵在三段式写法")],
        [td("阻塞赋值"), td("Blocking (=)"), td("组合逻辑中使用，立即生效")],
        [td("非阻塞赋值"), td("Non-blocking (<="), td("时序逻辑中使用，时钟沿统一更新")],
    ]
    t = Table(glossary, colWidths=[3*cm, 3.5*cm, 8.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C['primary']),
        ('GRID', (0,0), (-1,-1), 0.5, C['border']),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2),
    ]))
    story.append(table_caption(st, "FPGA\u672f\u8bed\u901f\u67e5"))
    story.append(t)
    story.append(Spacer(1, 5*mm))

    # ==================== 常见Verilog错误速查 ====================
    story.append(Paragraph("F. 常见Verilog错误与修正", st['sec_title']))
    err_rows = [
        [th("错误写法"), th("正确写法"), th("原因")],
        [td("always @(posedge clk) a = b;"), td("always @(posedge clk) a <= b;"), td("时序块必须用非阻塞赋值")],
        [td("always @(*) a <= b;"), td("always @(*) a = b;"), td("组合块必须用阻塞赋值")],
        [td("assign a = b + 1; (a是reg)"), td("wire a; assign a = b+1;"), td("assign只能驱动wire")],
        [td("reg a; always @(*) a = in;"), td("wire a; assign a = in;"), td("简单赋值用assign更清晰")],
        [td("always @(posedge clk) if(rst) ..."), td("always @(posedge clk or negedge rst_n) if(!rst_n) ..."), td("异步复位需加入敏感列表")],
        [td("case 缺少 default"), td("case ... default: ... endcase"), td("综合器会生成销存器")],
        [td("for (i=0; i<8; i=i+1) ..."), td("generate for ... endgenerate"), td("for循环在always外需用generate")],
    ]
    t = Table(err_rows, colWidths=[5*cm, 5.5*cm, 4.5*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), C['primary']),
        ('GRID', (0,0), (-1,-1), 0.5, C['border']),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [white, C['card_bg']]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('FONTSIZE', (0,0), (-1,-1), 7),
    ]))
    story.append(table_caption(st, "常见Verilog错误与修正"))
    story.append(t)

    story.append(Paragraph("参考文献", st['sec_title']))
    refs = [
        "1. Xilinx. 7 Series FPGAs Data Sheet: Overview (DS180).",
        "2. Xilinx. Spartan-7 FPGA Packaging and Pinout (UG475).",
        "3. 四梯科技. CT137X FPGA竞赛实训平台用户手册 (CT137X_UM.pdf).",
        "4. 四梯科技. CT137X引脚分配表 (CT137X_PIN.pdf).",
        "5. 四梯科技. CT137X原理图 (CT137X_SCH.pdf).",
        "6. Texas Instruments. ADC081C021 8-Bit ADC with ALERT Data Sheet.",
        "7. Texas Instruments. DAC5571 8-Bit DAC Data Sheet.",
        "8. Microchip. AT24C02 2Kbit EEPROM Data Sheet.",
        "9. Maxim Integrated. DS1302 Trickle Charge Timekeeping Chip Data Sheet.",
        "10. ISSI. IS63WV1288 128Kx8 Low Power SRAM Data Sheet.",
        "11. Winbond. W25Q128FV 128Mbit SPI Flash Data Sheet.",
        "12. 蓝桥杯大赛组委会. 第16/17届蓝桥杯FPGA省赛/国赛真题.",
    ]
    for ref in refs:
        story.append(Paragraph(ref, st['body']))
    story.append(Paragraph("© 2026 极道工作室 · JIDAO STUDIO · 版权所有", ParagraphStyle('CR', fontName='MSYH', fontSize=9, alignment=TA_CENTER, textColor=C['muted'])))
    return story

# ==================== 主函数 ====================
def main():
    register_fonts()
    st = S()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(script_dir)
    driver_files = read_verilog(os.path.join(base_dir, "driver"))
    user_files = read_verilog(os.path.join(base_dir, "user"))
    results_dir = os.path.join(base_dir, "results")
    os.makedirs(results_dir, exist_ok=True)

    output_path = os.path.join(results_dir, "蓝桥杯FPGA开发教程_详细注释版.pdf")

    # ========== 第一遍：生成正文，记录页码 ==========
    # 先生成不含目录的完整内容
    content_story = []
    content_story.extend(build_cover(st))
    content_story.extend(build_front_matter(st))
    # 目录占位（用于让第一遍页码与最终版一致）
    content_story.extend(build_toc(st))
    content_story.extend(build_chapter1(st))
    content_story.extend(build_chapter2(st))
    content_story.extend(build_chapter3(st, base_dir))
    content_story.extend(build_code_chapter("第四章  Driver 驱动模块详解", driver_files, 4, st))
    content_story.extend(build_code_chapter("第五章  User 应用模块详解", user_files, 5, st))
    content_story.extend(build_appendix(st))

    # 第一遍构建，记录页码
    doc1 = SimpleDocTemplate(output_path + ".tmp", pagesize=A4,
                             leftMargin=1.5*cm, rightMargin=1.5*cm,
                             topMargin=2*cm, bottomMargin=2.5*cm)
    doc1.build(list(content_story), onFirstPage=cover_header_footer, onLaterPages=header_footer)
    global total_pages
    total_pages = doc1.page
    print(f"Pass 1 done, page map: {chapter_pages}, total pages: {total_pages}")
    del content_story
    del doc1
    gc.collect()

    # ========== 第二遍：带页码的目录 + 正文 ==========
    global table_counter, figure_counter
    table_counter = 0
    figure_counter = 0
    final_story = []
    final_story.extend(build_cover(st))
    final_story.extend(build_front_matter(st))
    final_story.extend(build_toc(st))
    final_story.extend(build_chapter1(st))
    final_story.extend(build_chapter2(st))
    final_story.extend(build_chapter3(st, base_dir))
    final_story.extend(build_code_chapter("第四章  Driver 驱动模块详解", driver_files, 4, st))
    final_story.extend(build_code_chapter("第五章  User 应用模块详解", user_files, 5, st))
    final_story.extend(build_appendix(st))

    doc2 = SimpleDocTemplate(output_path, pagesize=A4,
                             leftMargin=1.5*cm, rightMargin=1.5*cm,
                             topMargin=2*cm, bottomMargin=2.5*cm)
    doc2.build(final_story, onFirstPage=cover_header_footer, onLaterPages=header_footer)

    # 清理临时文件
    try: os.remove(output_path + ".tmp")
    except: pass

    print(f"PDF generated: {output_path}")

if __name__ == "__main__":
    main()
