# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['shutil', 'types', '_ctypes', 'encodings', 'ctypes.util', 'collections', 'operator', 'reprlib', 'functools', 'enum', 'sip', 'collections.abc', 'warnings', 'linecache', 're', 'sre_compile', 'sre_parse', 'sre_constants', 'copyreg']
hiddenimports += collect_submodules('T:/a/HelpNDocTools/HelpNDocTools/src/src/__init__.py')


a = Analysis(
    ['T:/a/HelpNDocTools/HelpNDocTools/src/observer.py'],
    pathex=['./', 'C:/Windows/System32', 'C:/Windows/SysWOW64', 'T:/a/HelpNDocTools/HelpNDocTools/src/src'],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'tk', 'tk86t', 'tcl86t'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
splash = Splash(
    'T:/a/HelpNDocTools/HelpNDocTools/src/_internal/img/splash.png',
    binaries=a.binaries,
    datas=a.datas,
    text_pos=None,
    text_size=12,
    minify_script=True,
    always_on_top=True,
)

exe = EXE(
    pyz,
    a.scripts,
    splash,
    [],
    exclude_binaries=True,
    name='observer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=False,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='T:\\a\\HelpNDocTools\\HelpNDocTools\\src\\version.info',
    icon=['T:\\a\\HelpNDocTools\\HelpNDocTools\\src\\_internal\\img\\floppy-disk.ico'],
    hide_console='minimize-late',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    splash.binaries,
    strip=True,
    upx=False,
    upx_exclude=[],
    name='observer',
)
