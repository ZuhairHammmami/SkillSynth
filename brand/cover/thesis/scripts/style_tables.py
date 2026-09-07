# -*- coding: utf-8 -*-
"""Task 4: Restyle the 3 tables to Warm Craft — hairline borders (line/line-strong),
paper-2 shaded header row, bold header text. No wording changes."""
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

LINE = 'E4DAC8'
LINE_STRONG = 'CFC3AE'
PAPER2 = 'F3EDE1'

SRC = 'work/unpacked/word/document.xml'
tree = etree.parse(SRC)
root = tree.getroot()

for tbl in root.iter(q('tbl')):
    tp = tbl.find(q('tblPr'))
    if tp is None:
        tp = etree.Element(q('tblPr'))
        tbl.insert(0, tp)
    # table borders
    tb = tp.find(q('tblBorders'))
    if tb is None:
        tb = etree.Element(q('tblBorders'))
        tp.append(tb)
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = tb.find(q(edge))
        if e is None:
            e = etree.SubElement(tb, q(edge))
        e.set(q('val'), 'single')
        e.set(q('sz'), '4')
        e.set(q('space'), '0')
        e.set(q('color'), LINE_STRONG)

    # header row: shade + bold
    rows = list(tbl.iter(q('tr')))
    if rows:
        hdr = rows[0]
        for tc in hdr.findall(q('tc')):
            tcpr = tc.find(q('tcPr'))
            if tcpr is None:
                tcpr = etree.Element(q('tcPr'))
                tc.insert(0, tcpr)
            shd = tcpr.find(q('shd'))
            if shd is None:
                shd = etree.SubElement(tcpr, q('shd'))
            shd.set(q('val'), 'clear')
            shd.set(q('color'), 'auto')
            shd.set(q('fill'), PAPER2)
            # bold the runs in this header cell
            for r in tc.iter(q('r')):
                rpr = r.find(q('rPr'))
                if rpr is None:
                    rpr = etree.Element(q('rPr'))
                    r.insert(0, rpr)
                if rpr.find(q('b')) is None:
                    etree.SubElement(rpr, q('b'))

tree.write(SRC, xml_declaration=True, encoding='UTF-8', standalone=True)
print('tables styled')
