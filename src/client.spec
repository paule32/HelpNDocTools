# ---------------------------------------------------------------------------
# \file    client.spec
# \autror  (c) 2024, 2025 Jens Kallup - paule32
#          All rights reserved
#
# \notes   pyinstaller client.spec
# ---------------------------------------------------------------------------
import os
import pathlib
import warnings
# ---------------------------------------------------------------------------
# pyinstaller spec. import stuff ...
# ---------------------------------------------------------------------------
from pprint import pprint, pformat
from PyInstaller.utils.hooks import (
    collect_submodules,
    collect_data_files,
    collect_dynamic_libs,
    collect_all
)
# ---------------------------------------------------------------------------
# set "silent" filter mode for some harmful user warnings ...
# ---------------------------------------------------------------------------
# 1) Konkrete Meldung aus altgraph unterdrücken
warnings.filterwarnings(
    "ignore",
    message  = r"pkg_resources is deprecated as an API\.",
    category = UserWarning,
    module   = r"altgraph.*",
)
# 2) Alle DeprecationWarnings aus numpy ausblenden
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    module=r"numpy(\.|$)",
)
# ---------------------------------------------------------------------------
# installer from src directory ...
# ---------------------------------------------------------------------------
spec_dir = pathlib.Path(os.getcwd()).resolve()
src_dir  = spec_dir / "."

# ---------------------------------------------------------------------------
# pyinstaller lists ...
# ---------------------------------------------------------------------------
hidden = []
datapp = []
datbin = []

# ---------------------------------------------------------------------------
# check the pyinstaller lists of tupples ...
# ---------------------------------------------------------------------------
def ensure_pairs(name, seq, max_show=5):
    bad = [x for x in seq if not (isinstance(x, (tuple, list)) \
    and len(x) == 2)]
    if bad:
        msg = (""
            + f"{name}: Erwartet nur 2er-Tupel (src, dest), "
            + f"aber gefunden: {len(bad)} ungültige Einträge.\n"
            + f"Beispiele:\n{pformat(bad[:max_show])}\n"
            + "Typischer Fehler: collect_all(...) ungeordnet angehängt oder "
            + "Strings statt [('<src>','<dest>')] benutzt."
        )
        raise ValueError(msg)

# ---------------------------------------------------------------------------
# BeautifulSoup & Parser
# ---------------------------------------------------------------------------
hidden += [
    'bs4.builder._lxml',
    'bs4.builder._html5lib',
    'html5lib',
    'lxml',
    'chardet']
# ---------------------------------------------------------------------------
# PyQt5 / Qt5
# ---------------------------------------------------------------------------
hidden += ['PyQt5.sip']                # sip wird oft dynamisch benötigt
datapp += collect_data_files('PyQt5')  # sichert auch Plugins/Fallbacks

# ---------------------------------------------------------------------------
# Qt-Plugin-DLLs (falls Hooks nicht alles finden)
# ---------------------------------------------------------------------------
datbin += collect_dynamic_libs('PyQt5')

# ---------------------------------------------------------------------------
# QtWebEngine zwingend hinzufügen
# ---------------------------------------------------------------------------
hidden += [
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtWebEngineCore',
    'PyQt5.QtWebEngine']

we_datas, we_bins, we_hidden = collect_all('PyQt5.QtWebEngine')
datapp += we_datas
datbin += we_bins
hidden += we_hidden

# ---------------------------------------------------------------------------
# (Optional, aber oft hilfreich) QtWebEngineCore
# ---------------------------------------------------------------------------
core_datas, core_bins, core_hidden = collect_all('PyQt5.QtWebEngineCore')
datapp += core_datas
datbin += core_bins
hidden += core_hidden

# ---------------------------------------------------------------------------
# pefile: Code + Daten
# ---------------------------------------------------------------------------
pefile_data, pefile_bins, pefile_hidden = collect_all('pefile')
datapp += pefile_data   # -> List[ (src, dest) ]
datbin += pefile_bins   # -> List[ (src, dest) ]
hidden += pefile_hidden

# ---------------------------------------------------------------------------
# regex: .pyd/.so einsammeln + Hidden-Import absichern
# ---------------------------------------------------------------------------
reg_dat, reg_bin, reg_hid = collect_all('regex')
datapp += reg_dat       # -> List[ (src, dest) ]
datbin += reg_bin       # -> List[ (src, dest) ]
hidden += reg_hid

# ---------------------------------------------------------------------------
# numpy (C-Extensions, DLLs, Daten)
# ---------------------------------------------------------------------------
np_datas, np_bins, np_hidden = collect_all('numpy')
datapp += np_datas      # -> List[ (src, dest) ]
datbin += np_bins       # -> List[ (src, dest) ]

# ---------------------------------------------------------------------------
# sympy & mpmath (viele Submodule, pure Python)
# ---------------------------------------------------------------------------
hidden += collect_submodules('sympy')
hidden += collect_submodules('mpmath')

# ---------------------------------------------------------------------------
# httpx-Stack
# ---------------------------------------------------------------------------
for mod in ['httpx', 'httpcore', 'anyio', 'sniffio', 'certifi']:
    dts, bins, hid = collect_all(mod)
    datapp += dts       # -> List[ (src, dest) ]
    datbin += bins      # -> List[ (src, dest) ]
    hidden += hid

# ---------------------------------------------------------------------------
# schupps woops imports stuffs ...
# ---------------------------------------------------------------------------
for mod in ['html5lib', '_suggestions', 'charset', 'lxml', 'sage', 'gymp2',
    'multiset', 'click', 'socksio', 'termios']:
    dts, bin, hid = collect_all(mod)
    datapp += dts       # -> List[ (src, dest) ]
    datbin += bins      # -> List[ (src, dest) ]
    hidden += hid
    
# ---------------------------------------------------------------------------
# capstone (enthält native Libs)
# ---------------------------------------------------------------------------
cap_datas, cap_bins, cap_hidden = collect_all('capstone')
datapp += cap_datas     # -> List[ (src, dest) ]
datbin += cap_bins      # -> List[ (src, dest) ]
hidden += cap_hidden

# ---------------------------------------------------------------------------
# rich & pygments (Theme/Style-Daten, viele Module)
# ---------------------------------------------------------------------------
rc_datas , rc_bins , rc_hidden  = collect_all('rich')
pyg_datas, pyg_bins, pyg_hidden = collect_all('pygments')

datapp += rc_datas + pyg_datas
datbin += rc_bins  + pyg_bins

hidden += collect_submodules('rich')
hidden += collect_submodules('pygments')

# ---------------------------------------------------------------------------
# polib / dbf (reine Python, evtl. Paketdaten)
# ---------------------------------------------------------------------------
for mod in ['polib', 'dbf']:
    dts, bins, hid = collect_all(mod)
    datapp += dts
    datbin += bins
    hidden += hid

# ---------------------------------------------------------------------------
# screeninfo (plattformabhängige Backends) - MS-Windows
# ---------------------------------------------------------------------------
hidden += collect_submodules('screeninfo')

# ---------------------------------------------------------------------------
# ipapi (falls externes Paket bei dir)
# ---------------------------------------------------------------------------
try:
    ip_datas, ip_bins, ip_hidd = collect_all('ipapi')
    datapp += ip_datas
    datbin += ip_bins
    hidden += ip_hidd
except Exception:
    pass  # ignorieren, wenn es kein installiertes Paket ist

# ---------------------------------------------------------------------------
# Stdlib-"Sicherheitsgurte"
# meist nicht nötig, schadet aber nicht
# ---------------------------------------------------------------------------
hidden += ['sqlite3']

# ---------------------------------------------------------------------------
# Submodule + Daten + evtl. Binaries
# ---------------------------------------------------------------------------
mpl_datas, mpl_bins, mpl_hidd = collect_all('matplotlib')
datapp += mpl_datas     # -> List[ (src, dest) ]
datbin += mpl_bins      # -> List[ (src, dest) ]
hidden += mpl_hidd

# ---------------------------------------------------------------------------
# pandas & time stuff ...
# ---------------------------------------------------------------------------
hidden += collect_submodules('pandas')
hidden += collect_submodules('pandas.plotting')
hidden += collect_submodules('dateutil')
hidden += collect_submodules('pytz')

hidden += collect_submodules('matplotlib.backends')
hidden += collect_submodules('PIL')
hidden += collect_submodules('httpx')
hidden += collect_submodules('httpcore')
hidden += collect_submodules('anyio')
hidden += collect_submodules('markdown_it')
hidden += collect_submodules('mdurl')
hidden += collect_submodules('pyparsing')

# häufig genutztes Qt5-Agg-Backend sicherstellen
hidden += ['matplotlib.backends.backend_qt5agg']

datapp += [('_internal/observer.ini', '_internal')]

# ---------------------------------------------------------------------------
# santy check of tupples ...
# ---------------------------------------------------------------------------
ensure_pairs("datas"   , datapp)
ensure_pairs("binaries", datbin)

a = Analysis(
    [
        str(src_dir / '__main__.py'),
        str(src_dir / 'client.py')
    ],
    pathex        = [ str(src_dir) ],
    binaries      = datbin,
    datas         = datapp,
    hiddenimports = hidden,
    hookspath     = [],
    hooksconfig   = {},
    runtime_hooks = [],
    excludes      = [],
    noarchive     = False,
    optimize      = 0,
)
pyz = PYZ(a.pure)

exe = EXE( pyz, a.scripts,
    exclude_binaries           = True,
    name                       = 'client',
    debug                      = False,
    bootloader_ignore_signals  = False,
    strip                      = False,
    upx                        = True,
    console                    = True,
    disable_windowed_traceback = False,
    argv_emulation             = False,
    target_arch                = None,
    codesign_identity          = None,
    entitlements_file          = None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip       = False,
    upx         = True,
    upx_exclude = [],
    name        = 'client',
)
