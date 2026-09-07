# -*- coding: utf-8 -*-
"""Task 3: Core formatting of document.xml — box English/number runs, fix chapter
titles (-> Heading 1), style captions (-> Caption), replace static TOC with a
live field. No wording changes."""
import os
import re
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

SKIP_BOX = os.environ.get('SKIP_BOX') == '1'
SKIP_TOC = os.environ.get('SKIP_TOC') == '1'
SKIP_HEADS = os.environ.get('SKIP_HEADS') == '1'

BOX_COLOR = 'CFC3AE'
BOX_SZ = '6'
BOX_SPACE = '1'
LAT_BODY = 'Public Sans'

# Correct CT_RPr child order (ECMA-376) — w:bdr must precede shd/vertAlign/rtl/cs/lang
RPR_ORDER = ['rStyle','rFonts','b','bCs','i','iCs','caps','smallCaps','strike','dstrike',
             'outline','shadow','emboss','imprint','noProof','snapToGrid','vanish','webHidden',
             'color','spacing','w','kern','position','sz','szCs','highlight','u','effect',
             'bdr','shd','fitText','vertAlign','rtl','cs','em','lang','eastAsianLayout',
             'specVanish','oMath']

def insert_in_order(rpr, newtag):
    """Insert an rPr child at its correct OOXML sequence position."""
    newpos = RPR_ORDER.index(newtag)
    idx = len(rpr)
    for i, ch in enumerate(rpr):
        ln = etree.QName(ch).localname
        if ln in RPR_ORDER and RPR_ORDER.index(ln) > newpos:
            idx = i
            break
    el = etree.Element(q(newtag))
    rpr.insert(idx, el)
    return el

def add_border(rpr):
    old = rpr.find(q('bdr'))
    if old is not None:
        rpr.remove(old)
    bdr = insert_in_order(rpr, 'bdr')
    bdr.set(q('val'), 'single')
    bdr.set(q('sz'), BOX_SZ)
    bdr.set(q('space'), BOX_SPACE)
    bdr.set(q('color'), BOX_COLOR)

SRC = 'work/unpacked/word/document.xml'
tree = etree.parse(SRC)
root = tree.getroot()

# ---- boxable token regex: word starting & ending with alnum, internal punct allowed ----
TOKEN = re.compile(r'[A-Za-z0-9]+(?:[._%+/\-][A-Za-z0-9]+)*')
HAS_BOX = re.compile(r'[A-Za-z0-9]')

def process_run(run):
    """If the run has boxable chars and is a simple text run, split it into
    boxed/unboxed runs preserving text byte-for-byte. Returns True if the run
    was replaced (caller removes original)."""
    # only simple runs: children subset of {rPr, t, tab, br, noBreakHyphen}
    children = list(run)
    if len(children) == 0:
        return False
    for ch in children:
        if ch.tag not in (q('rPr'), q('t'), q('tab'), q('br'), q('noBreakHyphen')):
            return False
    # concatenated text
    t_nodes = [c for c in children if c.tag == q('t')]
    if not t_nodes:
        return False
    text = ''.join((t.text or '') for t in t_nodes)
    if not HAS_BOX.search(text):
        return False
    rpr = run.find(q('rPr'))
    if rpr is None:
        return False
    # tokenize
    segs = []
    idx = 0
    for m in TOKEN.finditer(text):
        if m.start() > idx:
            segs.append((False, text[idx:m.start()]))
        segs.append((True, m.group()))
        idx = m.end()
    if idx < len(text):
        segs.append((False, text[idx:]))
    # build new runs
    new_runs = []
    for boxed, seg in segs:
        newr = etree.Element(q('r'))
        rp = etree.SubElement(newr, q('rPr'))
        # deep copy relevant rPr children (skip bdr)
        for oldch in rpr:
            if oldch.tag != q('bdr'):
                rp.append(etree.fromstring(etree.tostring(oldch)))
        if boxed:
            add_border(rp)
        t = etree.SubElement(newr, q('t'))
        if seg[:1].isspace() or seg[-1:].isspace() or not seg.strip():
            t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        t.text = seg
        new_runs.append(newr)
    any_boxed = any(boxed for boxed, _ in segs)
    if not any_boxed:
        return False  # nothing to box in this run; leave untouched
    return new_runs

def box_document(root):
    replaced = 0
    for run in list(root.iter(q('r'))):
        parent = run.getparent()
        if parent is not None and etree.QName(parent).localname in ('hyperlink', 'fldSimple', 'ins', 'del'):
            continue
        res = process_run(run)
        if res is False:
            continue
        for r in res:
            run.addprevious(r)
        parent = run.getparent()
        parent.remove(run)
        replaced += 1
    return replaced

if not SKIP_BOX:
    count = box_document(root)
    print('boxed runs replaced:', count)
else:
    print('box skipped')

def para_text(p):
    return ''.join(t.text or '' for t in p.iter(q('t')))

def set_pstyle(p, sid):
    """Insert <w:pStyle> as the FIRST child of pPr (OOXML order), replacing any.""" 
    ppr = p.find(q('pPr'))
    if ppr is None:
        ppr = etree.Element(q('pPr'))
        p.insert(0, ppr)
    old = ppr.find(q('pStyle'))
    if old is not None:
        old.set(q('val'), sid)
        return ppr
    st = etree.Element(q('pStyle'))
    st.set(q('val'), sid)
    ppr.insert(0, st)
    return ppr

paras = list(root.iter(q('p')))

# ---- Chapter 1 & 2 title lines -> Heading 1 (831) ----
if not SKIP_HEADS:
    CHAPTER_TITLES = set('الفصل الأول الفصل الثاني الفصل الثالث الفصل الرابع الفصل الخامس الفصل السادس الفصل السابع الفصل اﻷول الفصل الثامن'.split())
    def is_chapter_title(t):
        return t in CHAPTER_TITLES or t.startswith('الفصل ')
    for i, p in enumerate(paras):
        t = para_text(p).strip()
        if is_chapter_title(t) and len(t) < 20:
            # only chapter title lines (not the ": ..." toc-like ones)
            if ':' in t or '…' in t or '....' in t.replace('....',''):
                continue
            set_pstyle(p, '831')
            # subtitle right after: also 831 (matches other chapters' 2-line pattern)
            if i + 1 < len(paras):
                set_pstyle(paras[i+1], '831')
            continue

    # ---- Captions -> Caption style (869), centered ----
    for p in paras:
        t = para_text(p).strip()
        if re.match(r'^(الشكل|الجدول)\b', t) and not re.match(r'^الشكل.+\.\.\.', t):
            ppr = set_pstyle(p, '869')
            # jc center: pPr already has jc (after ind); set its value in place
            jc = ppr.find(q('jc'))
            if jc is None:
                jc = etree.Element(q('jc'))
                # jc must come after ind/spacing; insert before outlineLvl/rPr if present
                anchor = ppr.find(q('outlineLvl'))
                if anchor is not None:
                    anchor.addprevious(jc)
                else:
                    ppr.append(jc)
            jc.set(q('val'), 'center')

# ---- Replace static TOC (paras 45..56 in original) with a live TOC field ----
# Identify the TOC block: 'فهرس المحتويات' heading line to the 'ملحق (أ)' entry.
toc_start = toc_end = None
if not SKIP_TOC:
    for i, p in enumerate(paras):
        t = para_text(p).strip()
        if toc_start is None and t.startswith('فهرس المحتويات'):
            toc_start = i
        if toc_start is not None and i > toc_start and t.startswith('ملحق (أ)'):
            toc_end = i + 1
            break
    print('TOC block:', toc_start, toc_end)

# Build replacement paragraphs: keep heading line, replace entries with field.
# We build: [heading 'فهرس المحتويات'] then a TOC field paragraph.
if toc_start is not None and toc_end is not None:
    heading_para = paras[toc_start]
    # keep heading para; delete the entries
    for i in range(toc_end - 1, toc_start, -1):
        p = paras[i]
        p.getparent().remove(p)
    # append TOC field paragraph after heading (if not already)
    # build field para
    fld = etree.SubElement(heading_para.getparent(), q('p'))
    # move: insert right after heading para
    heading_para.addnext(fld)
    def r_with(begin=None, instr=None, end=None, text=None, style=None):
        r = etree.Element(q('r'))
        if style:
            rpr = etree.SubElement(r, q('rPr'))
            rfonts = etree.SubElement(rpr, q('rFonts'))
            rfonts.set(q('ascii'), LAT_BODY)
        return r
    # begin
    rb = etree.SubElement(fld, q('r'))
    fldchar1 = etree.SubElement(rb, q('fldChar')); fldchar1.set(q('fldCharType'), 'begin'); fldchar1.set(q('dirty'), 'true')
    rc = etree.SubElement(fld, q('r'))
    instr = etree.SubElement(rc, q('instrText')); instr.set('{http://www.w3.org/XML/1998/namespace}space','preserve'); instr.text=' TOC \\o "1-3" \\h \\z \\u '
    rf = etree.SubElement(fld, q('r'))
    fldchar2 = etree.SubElement(rf, q('fldChar')); fldchar2.set(q('fldCharType'), 'separate')
    rsep = etree.SubElement(fld, q('r'))
    tt = etree.SubElement(rsep, q('t')); tt.text = 'حدّث حقول الجدول (Ctrl+A ثم F9) لتوليد فهرس المحتويات.'
    r_end = etree.SubElement(fld, q('r'))
    fldchar3 = etree.SubElement(r_end, q('fldChar')); fldchar3.set(q('fldCharType'), 'end')
    # place TOC on its own, leave paragraph style normal
    print('TOC field inserted')

tree.write(SRC, xml_declaration=True, encoding='UTF-8', standalone=True)
print('format_thesis.py done')
