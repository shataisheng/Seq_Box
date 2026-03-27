# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('seqbox', 'seqbox')]
binaries = []
hiddenimports = ['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'seqbox.core', 'seqbox.core.alphabets', 'seqbox.core.sequence', 'seqbox.io', 'seqbox.io.fasta', 'seqbox.dna', 'seqbox.dna.basic', 'seqbox.dna.convert', 'seqbox.protein', 'seqbox.protein.property', 'seqbox.protein.convert', 'seqbox.protein.analysis', 'seqbox.gui', 'seqbox.gui.main_window', 'seqbox.gui.pages', 'seqbox.gui.pages.base_page', 'seqbox.gui.pages.fasta_page', 'seqbox.gui.pages.dna_page', 'seqbox.gui.pages.protein_page', 'seqbox.gui.pages.history_page', 'seqbox.gui.pages.settings_page']
tmp_ret = collect_all('PyQt6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['launch.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SeqBox',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SeqBox',
)
