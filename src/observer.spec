# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['shutil', 'types', '_ctypes', 'encodings', 'ctypes.util', 'collections', 'operator', 'reprlib', 'functools', 'enum', 'sip', 'collections.abc', 'warnings', 'linecache', 're', 'sre_compile', 'sre_parse', 'sre_constants', 'copyreg']
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/appcollection.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/__init__.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/tools/collection.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/tools/data001.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/tools/data002.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/tools/data003.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/tools/data004.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/tools/data005.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/tools/misc.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/tools/__init__.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/interpreter/EParserException.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/interpreter/ParserDSL.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/interpreter/RunTimeLibrary.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/interpreter/VisualComponentLibrary.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/interpreter/doxygen/doxygen.py')
hiddenimports += collect_submodules('E:/Projekte/HelpNDocTools/src/interpreter/pascal/pascal.py')


a = Analysis(
    ['E:/Projekte/HelpNDocTools/src/observer.py'],
    pathex=['./', 'C:/Windows/System32', 'C:/Windows/SysWOW64', 'E:/Projekte/HelpNDocTools/src/interpreter/doxygen', 'E:/Projekte/HelpNDocTools/src/interpreter/pascal', 'E:/Projekte/HelpNDocTools/src/interpreter/dbase', 'E:/Projekte/HelpNDocTools/src/interpreter', 'E:/Projekte/HelpNDocTools/src/tools', 'E:/Projekte/HelpNDocTools/src'],
    binaries=[],
    datas=[('E:/Projekte/HelpNDocTools/src/locales', 'locales/'), ('E:/Projekte/HelpNDocTools/src/img', 'img/'), ('E:/Projekte/HelpNDocTools/LICENSE', '.'), ('E:/Projekte/HelpNDocTools/README.md', '.'), ('E:/Projekte/HelpNDocTools/CONTRIBUTING.md', '.'), ('E:/Projekte/HelpNDocTools/CODE_OF_CONDUCT.md', '.'), ('E:/Projekte/HelpNDocTools/src/topics.txt', '.')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)
splash = Splash(
    'E:/Projekte/HelpNDocTools/src/_internal/img/splash.png',
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
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='E:\\Projekte\\HelpNDocTools\\src\\version.info',
    icon=['E:\\Projekte\\HelpNDocTools\\src\\_internal\\img\\floppy-disk.ico'],
    hide_console='minimize-late',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    splash.binaries,
    strip=True,
    upx=True,
    upx_exclude=[],
    name='observer',
)
