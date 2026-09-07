# -*- coding: utf-8 -*-
"""Task 6: Populate header (default+even) with STYLEREF section title + hairline,
and footer (default+even) with a centered PAGE field. 'first' versions stay blank.
No wording changes to the body."""
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

INK_SOFT = '4A4238'
LINE_STRONG = 'CFC3AE'
AR_BODY = 'Noto Sans Arabic'

def rpr(r, bold=True, sz='20', color=INK_SOFT):
    rp = etree.SubElement(r, q('rPr'))
    rf = etree.SubElement(rp, q('rFonts'))
    rf.set(q('ascii'), 'Public Sans')
    rf.set(q('hAnsi'), 'Public Sans')
    rf.set(q('eastAsia'), AR_BODY)
    rf.set(q('cs'), AR_BODY)
    if bold:
        etree.SubElement(rp, q('b'))
    etree.SubElement(rp, q('color')).set(q('val'), color)
    etree.SubElement(rp, q('sz')).set(q('val'), sz)
    etree.SubElement(rp, q('szCs')).set(q('val'), sz)

def text_run(txt, **kw):
    r = etree.Element(q('r'))
    rpr(r, **kw)
    t = etree.SubElement(r, q('t'))
    t.text = txt
    return r

def field_run(instr, cached):
    r = etree.Element(q('r'))
    rpr(r)
    fc = etree.SubElement(r, q('fldChar')); fc.set(q('fldCharType'), 'begin')
    r2 = etree.Element(q('r'))
    rpr(r2)
    it = etree.SubElement(r2, q('instrText'))
    it.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    it.text = instr
    r3 = etree.Element(q('r'))
    rpr(r3)
    fc2 = etree.SubElement(r3, q('fldChar')); fc2.set(q('fldCharType'), 'separate')
    r4 = text_run(cached)
    r5 = etree.Element(q('r'))
    rpr(r5)
    fc3 = etree.SubElement(r5, q('fldChar')); fc3.set(q('fldCharType'), 'end')
    return [r, r2, r3, r4, r5]

def header_para(root):
    p = etree.SubElement(root, q('p'))
    ppr = etree.SubElement(p, q('pPr'))
    bdr = etree.SubElement(ppr, q('pBdr'))
    bot = etree.SubElement(bdr, q('bottom'))
    bot.set(q('val'), 'single'); bot.set(q('sz'), '8')
    bot.set(q('space'), '4'); bot.set(q('color'), LINE_STRONG)
    etree.SubElement(ppr, q('bidi'))
    for el in field_run(' STYLEREF "Heading 1" \\n ', 'الفصل الأول'):
        p.append(el)
    return p

def footer_para(root):
    p = etree.SubElement(root, q('p'))
    ppr = etree.SubElement(p, q('pPr'))
    bdr = etree.SubElement(ppr, q('pBdr'))
    top = etree.SubElement(bdr, q('top'))
    top.set(q('val'), 'single'); top.set(q('sz'), '8')
    top.set(q('space'), '4'); top.set(q('color'), LINE_STRONG)
    etree.SubElement(ppr, q('bidi'))
    jc = etree.SubElement(ppr, q('jc')); jc.set(q('val'), 'center')
    for el in field_run(' PAGE ', '1'):
        p.append(el)
    return p

def clear_and_fill(path, builder):
    tree = etree.parse(path)
    root = tree.getroot()
    for child in list(root):
        root.remove(child)
    builder(root)
    tree.write(path, xml_declaration=True, encoding='UTF-8', standalone=True)

base = 'work/unpacked/word'
# default + even headers
clear_and_fill(f'{base}/header1.xml', header_para)
clear_and_fill(f'{base}/header2.xml', header_para)
# default + even footers
clear_and_fill(f'{base}/footer1.xml', footer_para)
clear_and_fill(f'{base}/footer2.xml', footer_para)
print('headers/footers populated (first left blank)')
