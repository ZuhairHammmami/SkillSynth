# -*- coding: utf-8 -*-
"""Task 2: Recolor + refont styles.xml toward Warm Craft. No text changes."""
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(tag): return '{%s}%s' % (W, tag)

INK = '2A2521'
INK_SOFT = '4A4238'
INK_SOFT2 = '5B5348'
OCHRE_DEEP = '8A6520'
SAGE_DEEP = '5F6C50'
LINE = 'E4DAC8'

AR_BODY = 'Noto Sans Arabic'
AR_DISPLAY = 'El Messiri'
LAT_BODY = 'Public Sans'
LAT_DISPLAY = 'Bricolage Grotesque'

SRC = 'work/unpacked/word/styles.xml'
tree = etree.parse(SRC)
root = tree.getroot()


def set_color(rpr, val):
    for c in rpr.findall(q('color')):
        rpr.remove(c)
    c = etree.SubElement(rpr, q('color'))
    c.set(q('val'), val)


def set_fonts(rpr, lat, aradb):
    rf = rpr.find(q('rFonts'))
    if rf is None:
        rf = etree.Element(q('rFonts'))
        rpr.insert(0, rf)
    for attr in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
        rf.attrib.pop(q(attr), None)
    for attr in ('hint',):
        rf.attrib.pop(q(attr), None)
    rf.set(q('ascii'), lat)
    rf.set(q('hAnsi'), lat)
    rf.set(q('eastAsia'), aradb)
    rf.set(q('cs'), aradb)


def toggle_italic(rpr, on=False):
    for tag in ('i', 'iCs'):
        for el in rpr.findall(q(tag)):
            rpr.remove(el)
    if on:
        etree.SubElement(rpr, q('i'))
        etree.SubElement(rpr, q('iCs'))


# ---- 1. docDefaults rPrDefault ----
for rpr in root.iter(q('rPrDefault')):
    n = rpr.find(q('rPr'))
    set_fonts(n, LAT_BODY, AR_BODY)
    set_color(n, INK)

# ---- 2. paragraph default: justify-ish already has line; keep ----

# ---- 3. Heading styles 831-834 ----
HEAD = {
    '831': {'color': INK, 'lat': LAT_DISPLAY, 'ar': AR_DISPLAY, 'bold': True},
    '832': {'color': INK, 'lat': LAT_DISPLAY, 'ar': AR_DISPLAY, 'bold': True},
    '833': {'color': INK_SOFT, 'lat': LAT_DISPLAY, 'ar': AR_DISPLAY, 'bold': True},
    '834': {'color': INK_SOFT, 'lat': LAT_BODY, 'ar': AR_BODY, 'bold': False},
}
for st in root.iter(q('style')):
    sid = st.get(q('styleId'))
    if sid in HEAD:
        rpr = st.find(q('rPr'))
        cfg = HEAD[sid]
        set_color(rpr, cfg['color'])
        set_fonts(rpr, cfg['lat'], cfg['ar'])
        toggle_italic(rpr, False)
        # bold
        for b in rpr.findall(q('b')):
            rpr.remove(b)
        etree.SubElement(rpr, q('b'))
        # bottom hairline for H1
        if sid == '831':
            ppr = st.find(q('pPr'))
            bdr = etree.Element(q('pBdr'))
            bot = etree.SubElement(bdr, q('bottom'))
            bot.set(q('val'), 'single'); bot.set(q('sz'), '8')
            bot.set(q('space'), '4'); bot.set(q('color'), OCHRE_DEEP)
            old = ppr.find(q('pBdr'))
            if old is not None:
                ppr.remove(old)
            # insert pBdr in correct pPr order: after the leading control elements
            # keepNext/keepLines/pageBreakBefore/widowControl/numPr/suppressLineNumbers
            anchor = None
            for tag in ('keepNext','keepLines','pageBreakBefore','widowControl','numPr','suppressLineNumbers'):
                el = ppr.find(q(tag))
                if el is not None:
                    anchor = el  # last of the leading sequence
            if anchor is not None:
                anchor.addnext(bdr)
            else:
                ppr.insert(0, bdr)

# ---- 4. Caption 869 ----
for st in root.iter(q('style')):
    if st.get(q('styleId')) == '869':
        rpr = st.find(q('rPr'))
        set_color(rpr, INK_SOFT)
        set_fonts(rpr, LAT_BODY, AR_BODY)
        toggle_italic(rpr, False)
        for b in rpr.findall(q('b')):
            rpr.remove(b)
        etree.SubElement(rpr, q('b'))

tree.write(SRC, xml_declaration=True, encoding='UTF-8', standalone=True)
print('styles.xml updated')
