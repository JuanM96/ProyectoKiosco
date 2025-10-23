# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['tkinter.ttk', 'PIL._tkinter_finder']
hiddenimports += collect_submodules('tkinter')
hiddenimports += collect_submodules('pandas')
hiddenimports += collect_submodules('sqlite3')
hiddenimports += collect_submodules('PIL')


a = Analysis(
    ['pos-kiosco-python.py'],
    pathex=[],
    binaries=[],
    datas=[('img', 'img')],
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
    a.binaries,
    a.datas,
    [],
    name='Kiosco-POS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\ProyectoKiosco\\img\\kiosco.ico'],
)
