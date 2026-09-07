# -*- coding: utf-8 -*-
"""Bisect harness: extract fresh from thesis-work.docx into work/unpacked, apply
a subset of pipeline steps, repack, render. Usage: bisect.py <steplist>
(comma list from: style,format,tables,headers,section). Prints render result."""
import zipfile, os, shutil, sys, subprocess
from lxml import etree

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
def q(t): return '{%s}%s' % (W, t)
SRC_ZIP = 'work/thesis-work.docx'
UNPACK = 'work/unpacked'
OUT = '/tmp/bs/variant.docx'

def extract():
    if os.path.exists(UNPACK): shutil.rmtree(UNPACK)
    os.makedirs(UNPACK)
    zipfile.ZipFile(SRC_ZIP).extractall(UNPACK)

def repack():
    if os.path.exists(OUT): os.remove(OUT)
    z = zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED)
    for b, _, fs in os.walk(UNPACK):
        for f in fs:
            full = os.path.join(b, f)
            z.write(full, os.path.relpath(full, UNPACK))
    z.close()

def apply_section():
    SRC = f'{UNPACK}/word/document.xml'
    tree = etree.parse(SRC); root = tree.getroot()
    sect = root.find(q('body')).find(q('sectPr'))
    pg = sect.find(q('pgSz')); pg.set(q('w'),'11906'); pg.set(q('h'),'16838'); pg.set(q('orient'),'portrait')
    mm = sect.find(q('mirrorMargins'))
    if mm is not None: sect.remove(mm)
    tree.write(SRC, xml_declaration=True, encoding='UTF-8', standalone=True)

def render():
    r = subprocess.run(['soffice','-env:UserInstallation=file:///tmp/lob_bisect2','--headless',
                        '--convert-to','pdf','--outdir','/tmp/bs',OUT],
                       capture_output=True, text=True, timeout=180)
    return os.path.exists('/tmp/bs/variant.pdf'), (r.stdout + r.stderr)[-400:]

steps = sys.argv[1].split(',')
extract()
os.chdir('/run/media/zuhair/Extra/SkillSynth/brand/cover/thesis')
if 'style' in steps: os.system('python3 scripts/style_themes.py')
if 'format' in steps: os.system('python3 scripts/format_thesis.py')
if 'tables' in steps: os.system('python3 scripts/style_tables.py')
if 'headers' in steps: os.system('python3 scripts/style_header_footer.py')
if 'section' in steps: apply_section()
repack()
ok, err = render()
print(f'steps={steps} -> rendered={ok}')
if not ok: print(err)
