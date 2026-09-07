# -*- coding: utf-8 -*-
"""Orchestrate a clean full rebuild of the formatted thesis from the untouched
original (work/thesis-work.docx): styles -> format -> tables -> header/footer ->
section (A4) -> repack."""
import zipfile, os, shutil
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)

UNPACK = 'work/unpacked'
SRC_ZIP = 'work/thesis-work.docx'

def run(name):
    print(f'== {name} ==')
    os.system(f'python3 scripts/{name}.py')

def main():
    # 1. fresh extraction
    if os.path.exists(UNPACK):
        shutil.rmtree(UNPACK)
    os.makedirs(UNPACK)
    zipfile.ZipFile(SRC_ZIP).extractall(UNPACK)
    print('== fresh extract ==')

    # 2. styles
    run('style_themes')
    # 3. core formatting (boxes, chapter titles, captions, TOC field)
    run('format_thesis')
    # 4. tables
    run('style_tables')
    # 5. header/footer
    run('style_header_footer')

    # 6. section layout: A4 portrait, symmetric margins, keep titlePg, no mirrorMargins
    SRC = f'{UNPACK}/word/document.xml'
    tree = etree.parse(SRC); root = tree.getroot()
    sect = root.find(q('body')).find(q('sectPr'))
    pgsz = sect.find(q('pgSz'))
    pgsz.set(q('w'), '11906'); pgsz.set(q('h'), '16838'); pgsz.set(q('orient'), 'portrait')
    mm = sect.find(q('mirrorMargins'))
    if mm is not None:
        sect.remove(mm)
    pgmar = sect.find(q('pgMar'))
    pgmar.set(q('top'), '1440'); pgmar.set(q('right'), '1440')
    pgmar.set(q('bottom'), '1440'); pgmar.set(q('left'), '1440')
    pgmar.set(q('header'), '720'); pgmar.set(q('footer'), '720'); pgmar.set(q('gutter'), '0')
    tree.write(SRC, xml_declaration=True, encoding='UTF-8', standalone=True)
    print('== section A4 set; titlePg:', sect.find(q('titlePg')) is not None)

    # 7. repack
    out = 'الأطروحة-formatted.docx'
    if os.path.exists(out):
        os.remove(out)
    z = zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED)
    for base, dirs, files in os.walk(UNPACK):
        for f in files:
            full = os.path.join(base, f)
            arc = os.path.relpath(full, UNPACK)
            z.write(full, arc)
    z.close()
    print('== repacked', out, os.path.getsize(out), 'bytes')

if __name__ == '__main__':
    main()
