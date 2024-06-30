# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['shutil', 'types', '_ctypes', 'encodings', 'ctypes.util', 'collections', 'operator', 'reprlib', 'functools', 'enum', 'sip', 'collections.abc', 'warnings', 'linecache', 're', 'sre_compile', 'sre_parse', 'sre_constants', 'copyreg']
hiddenimports += collect_submodules('src/appcollection.py')
hiddenimports += collect_submodules('src/__init__.py')
hiddenimports += collect_submodules('src/tools/collection.py')
hiddenimports += collect_submodules('src/tools/data001.py')
hiddenimports += collect_submodules('src/tools/data002.py')
hiddenimports += collect_submodules('src/tools/data003.py')
hiddenimports += collect_submodules('src/tools/data004.py')
hiddenimports += collect_submodules('src/tools/data005.py')
hiddenimports += collect_submodules('src/tools/misc.py')
hiddenimports += collect_submodules('src/tools/__init__.py')
hiddenimports += collect_submodules('src/interpreter/EParserException.py')
hiddenimports += collect_submodules('src/interpreter/ParserDSL.py')
hiddenimports += collect_submodules('src/interpreter/RunTimeLibrary.py')
hiddenimports += collect_submodules('src/interpreter/VisualComponentLibrary.py')
hiddenimports += collect_submodules('src/interpreter/doxygen/doxygen.py')
hiddenimports += collect_submodules('src/interpreter/pascal/pascal.py')


a = Analysis(
    ['src/observer.py'],
    pathex=['./', 'src/_internal', 'src/_internal/img', 'src/interpreter/doxygen', 'src/interpreter/pascal', 'src/interpreter/dbase', 'src/interpreter', 'src/tools', 'src'],
    binaries=[],
    datas=[('src/_internal/locales', '_internal/locales/'), ('src/_internal/img', '_internal/img/'), ('LICENSE', '.'), ('README.md', '.'), ('CONTRIBUTING.md', '.'), ('CODE_OF_CONDUCT.md', '.') ],
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
    'src/_internal/img/splash.png',
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
    version='version.info',
    icon=['_internal/img/floppy-disk.ico'],
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
