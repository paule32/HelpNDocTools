# -*- mode: python ; coding: utf-8 -*-
# ---------------------------------------------------------------------------
# File:   observer.spec - executable specified stuff
# Author: Jens Kallup - paule32
#
# Rights: (c) 2024 by kallup non-profit software
#         all rights reserved
#
# only for education, and for non-profit usage !!!
# commercial use ist not allowed.
# ---------------------------------------------------------------------------
a = Analysis(
    ['observer.py'],
    pathex   = [],
    binaries = [],
    datas    = [
        # -------------------------------------------------------------------
        # images, icons, etc..  <src, <dst>
        # -------------------------------------------------------------------
        ("img", "img")
    ],
    hiddenimports = [],
    hookspath     = [],
    hooksconfig   = {},
    runtime_hooks = [],
    excludes      = [],
    noarchive     = False,
)

# ---------------------------------------------------------------------------
# we love to display a loader splash screen image ...
# ---------------------------------------------------------------------------
splash = Splash("img/splash.png",
    binaries   = a.binaries,
    datas      = a.datas,
    text_pos   = (0, 0),
    text_size  = 8,
    text_color = 'black'
)

pyz = PYZ(a.pure)

exe = EXE(
    splash,
    splash.binaries,
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    debug                      = True,
    bootloader_ignore_signals  = False,
    strip                      = False,
    upx                        = True,
    upx_exclude                = [],
    runtime_tmpdir             = None,
    disable_windowed_traceback = False,
    argv_emulation             = False,
    target_arch                = None,
    codesign_identity          = None,
    entitlements_file          = None,
    
    # -----------------------------------------------------------------------
    # internal version information file for the Windows executable ...
    # -----------------------------------------------------------------------
    console = False,
    name    = "observer",
    version = "version.info"
)
