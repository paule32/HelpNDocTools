# ---------------------------------------------------------------------------
# \file    client.spec
# \autror  (c) 2024, 2025 Jens Kallup - paule32
#          All rights reserved
#
# \notes   pyinstaller client.spec
# ---------------------------------------------------------------------------
import os
import pathlib

spec_dir = pathlib.Path(os.getcwd()).resolve()
src_dir  = spec_dir / "."

a = Analysis(
    [
        str(src_dir / '__main__.py'),
        str(src_dir / 'client.py')
    ],
    pathex = [ str(src_dir) ],
    binaries=[],
    datas = [
        ('_internal/observer.ini', '_internal'),
    ],
    hiddenimports = [
        'resources_rc'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive = False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz, a.scripts, [],
    exclude_binaries = True,
    name = 'client',
    debug = False,
    bootloader_ignore_signals=False,
    strip = False,
    upx = True,
    console = True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='client',
)
