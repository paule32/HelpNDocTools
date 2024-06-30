# ---------------------------------------------------------------------------
# File:   observer.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------

# -----------------------------------------------------------------------
# global used application stuff. try to catch import exceptions ...
# ---------------------------------------------------------------------------
try:
    import os            # operating system stuff
    import sys           # system specifies
    import traceback
    
    if getattr(sys, 'frozen', False):
        import pyi_splash
except Exception as e:
    exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
    tb = traceback.extract_tb(e.__traceback__)[-1]
    
    print(f"Exception occur:")
    print(f"type : {exc_type.__name__}")
    print(f"value: {exc_value}")
    print(misc.StringRepeat("-",40))
    #
    print(f"file : {tb.filename}")
    print(f"line : {tb.lineno}")
    sys.exit(1)

# ---------------------------------------------------------------------------
# under the windows console, python paths can make problems ...
# ---------------------------------------------------------------------------
if 'PYTHONHOME' in os.environ:
    del os.environ['PYTHONHOME']
if 'PYTHONPATH' in os.environ:
    del os.environ['PYTHONPATH']

# ---------------------------------------------------------------------------
# to hide global variables from other packages, i use this class for a common
# container. the reference of this class is declared later in the source.
# i assume, that the os package is strict available by the current/latest
# Python version...
# ---------------------------------------------------------------------------
class globalEnv:
    def __init__(self):
        self.v__app__debug        = False
        
        self.v__app__app_dir__    = os.path.dirname(os.path.abspath(__file__))
        self.v__app__modul__      = os.path.join(self.v__app__app_dir__, "")
        self.v__app__inter__      = os.path.join(self.v__app__app_dir__, "interpreter")
        
        self.v__app__name         = "observer"
        self.v__app__name_mo      = self.v__app__name + ".mo"
        
        self.v__app__cdn_host     = "http://localhost/cdn"
        self.v__app__internal__   = os.path.join(self.v__app__modul__, "_internal")
        #
        self.v__app__logfile      = os.path.join(self.v__app__internal__, self.v__app__name) + ".log"
        self.v__app__config_ini   = os.path.join(self.v__app__internal__, self.v__app__name) + ".ini"
        self.v__app__logging      = None
        
        self.v__app__img__int__   = os.path.join(self.v__app__internal__, "img")
        
        self.v__app__doxygen__    = os.path.join(self.v__app__img__int__, "doxygen")
        self.v__app__hlpndoc__    = os.path.join(self.v__app__img__int__, "helpndoc")
        self.v__app__helpdev__    = os.path.join(self.v__app__img__int__, "help")
        self.v__app__pythonc__    = os.path.join(self.v__app__img__int__, "python")
        self.v__app__lispmod__    = os.path.join(self.v__app__img__int__, "lisp")
        self.v__app__ccpplus__    = os.path.join(self.v__app__img__int__, "cpp")
        self.v__app__cpp1dev__    = os.path.join(self.v__app__img__int__, "c")
        self.v__app__dbasedb__    = os.path.join(self.v__app__img__int__, "dbase")
        self.v__app__javadev__    = os.path.join(self.v__app__img__int__, "java")
        self.v__app__javadoc__    = os.path.join(self.v__app__img__int__, "javadoc")
        self.v__app__freepas__    = os.path.join(self.v__app__img__int__, "freepas")
        self.v__app__locales__    = os.path.join(self.v__app__img__int__, "locales")
        self.v__app__com_c64__    = os.path.join(self.v__app__img__int__, "c64")
        self.v__app__keybc64__    = os.path.join(self.v__app__img__int__, "c64keyboard.png")
        self.v__app__discc64__    = os.path.join(self.v__app__img__int__, "disk2.png")
        self.v__app__datmc64__    = os.path.join(self.v__app__img__int__, "mc2.png")
        self.v__app__logoc64__    = os.path.join(self.v__app__img__int__, "logo2.png")
        
        # ------------------------------------------------------------------------
        # some state flags ...
        # ------------------------------------------------------------------------
        self.currentTextChanged_connected  = False
        self.currentIndexChanged_connected = False
        
        self.view_pressed_connected          = False
        self.rhs_stateChanged_connected      = False
        self.blockCountChanged_connected     = False
        self.cursorPositionChanged_connected = False
        
        self.btn_add_connected    = False
        self.btn_addsrc_connected = False
        self.btn_close_connected  = False
        
        self.helpButton_connected = False
        self.prevButton_connected = False
        self.exitButton_connected = False
        
        self.v__app_object        = None
        self.v__app_win           = None
        #
        self.v__app__img_ext__    = ".png"
        self.v__app__font         = "Arial"
        self.v__app__font_edit    = "Consolas"
        
        self.v__app__framework    = "PyQt5.QtWidgets.QApplication"
        self.v__app__exec_name    = sys.executable
        
        self.v__app__error_level  = "0"
        
        self.v__app__scriptname__ = "./examples/dbase/example1.prg"
        
        # ------------------------------------------------------------------------
        self.v__app__config   = None
        
        self.css_model_header = ""
        self.css_tabs = ""
        self.css__widget_item = ""
        self.css_button_style = ""
        
        # ------------------------------------------------------------------------
        # branding water marks ...
        # ------------------------------------------------------------------------
        self.__version__ = "Version 0.0.1"
        self.__authors__ = "paule32"
        
        self.__date__    = "2024-01-04"
        
        self.EXIT_SUCCESS = 0
        self.EXIT_FAILURE = 1
        
        self.basedir = os.path.dirname(__file__)
        # ------------------------------------------------------------------------
                
        self.error_result = 0
        self.topic_counter = 1
        
        self.c64_painter = None
        
        self.tr = None
        self.sv_help = None
        
        self.doxy_env   = "DOXYGEN_PATH"  # doxygen.exe
        self.doxy_hhc   = "DOXYHHC_PATH"  # hhc.exe
        
        self.doxy_path  = self.v__app__internal__
        self.hhc__path  = ""
        
        self.doxyfile   = os.path.join(self.v__app__internal__, "Doxyfile")
        
        self.error_fail = False
        
        self.byte_code = None

# ---------------------------------------------------------------------------
global genv
genv = globalEnv()

# ---------------------------------------------------------------------------
# extent the search paths for supported interpreters and tools ...
# ---------------------------------------------------------------------------
sys.path.append(os.path.join(genv.v__app__inter__, "pascal"))
sys.path.append(os.path.join(genv.v__app__inter__, "dbase"))
sys.path.append(os.path.join(genv.v__app__inter__, "doxygen"))
sys.path.append(os.path.join(genv.v__app__inter__, ""))
sys.path.append(os.path.join(genv.v__app__modul__, "tools"))

class IgnoreOuterException(Exception):
    pass

# ---------------------------------------------------------------------------
# application imports ...
# ---------------------------------------------------------------------------
try:
    import re             # regular expression handling
    import requests       # get external url stuff
    
    import time           # thread count
    import datetime       # date, and time routines
    
    import threading      # multiple action simulator
    
    import glob           # directory search
    import atexit         # clean up
    import subprocess     # start sub processes
    import platform       # Windows ?
    
    import gzip           # pack/de-pack data
    import base64         # base64 encoded data
    import shutil         # shell utils
    
    import pkgutil        # attached binary data utils
    import json           # json lists
    import csv            # simplest data format
    
    import gettext        # localization
    import locale         # internal system locale
    import polib          # create .mo locales files from .po files
    
    import io             # memory streams
    
    import random         # randome numbers
    import string
    
    import ctypes         # windows ip info
    
    import sqlite3        # database: sqlite
    import configparser   # .ini files
    
    import traceback      # stack exception trace back
    
    import textwrap
    import marshal        # bytecode exec
    import inspect        # stack
    
    import logging
    
    # ------------------------------------------------------------------------
    # Qt5 gui framework
    # ------------------------------------------------------------------------
    from PyQt5.QtWidgets          import *
    from PyQt5.QtWebEngineWidgets import *
    from PyQt5.QtCore             import *
    from PyQt5.QtGui              import *
    
    from pathlib import Path
    
    # ------------------------------------------------------------------------
    # developers own modules ...
    # ------------------------------------------------------------------------
    from collection import *     # exception: templates
    
    from VisualComponentLibrary import *
    
    from EParserException import *     # exception handling for use with parser
    from RunTimeLibrary   import *     # rtl functions for parser
    
    from ParserDSL        import *
    
    from colorama   import init, Fore, Back, Style  # ANSI escape
    from pascal     import *     # pascal interpreter
    from doxygen    import *     # doxygen script

    # -------------------------------------------------------------------
    # for debuging, we use python logging library ...
    # -------------------------------------------------------------------
    file_path = genv.v__app__logfile
    file_path = file_path.replace("\\", "/")
    
    if not os.path.exists(file_path):
        Path(file_path).touch()
    
    genv.v__app__logging = logging.getLogger(file_path)
    logging.basicConfig(
        format="%(asctime)s: %(levelname)s: %(message)s",
        filename=file_path,
        encoding="utf-8",
        filemode="w",
        level=logging.DEBUG)
    genv.v__app__logging.info("init ok: session start...")
    
    # ------------------------------------------------------------------------
    # forward initializations ...
    # ------------------------------------------------------------------------
    genv.v__app__config = configparser.ConfigParser()
    genv.v__app__config.read(genv.v__app__config_ini)
    
    # ------------------------------------------------------------------------
    # global used locales constants ...
    # ------------------------------------------------------------------------
    genv.v__locale__    = os.path.join(genv.v__app__internal__, "locales")
    genv.v__locale__enu = "en_us"            # enu
    genv.v__locale__deu = "de_de"            # deu
    genv.v__locale__sys = locale.getlocale() # system locale
    
    # ------------------------------------------------------------------------
    # selected list of flags for translation localization display ...
    # ------------------------------------------------------------------------
    cdn_host = genv.v__app__cdn_host + "/observer/img/flags/"
    cdn_suff = ".gif"
    genv.v__app__cdn_flags = [
        [ "AFG", cdn_host + "AFG" + cdn_suff ],
        [ "ALB", cdn_host + "ALB" + cdn_suff ],
        [ "DZA", cdn_host + "DZA" + cdn_suff ],
        [ "AND", cdn_host + "AND" + cdn_suff ],
        [ "AGO", cdn_host + "AGO" + cdn_suff ],
        [ "ATG", cdn_host + "ATG" + cdn_suff ],
        [ "ARG", cdn_host + "ARG" + cdn_suff ],
        [ "ARM", cdn_host + "ARM" + cdn_suff ],
        [ "AUS", cdn_host + "AUS" + cdn_suff ],
        [ "AUT", cdn_host + "AUT" + cdn_suff ],
        [ "AZE", cdn_host + "AZE" + cdn_suff ],
        [ "BHS", cdn_host + "BHS" + cdn_suff ],
        [ "BHR", cdn_host + "BHR" + cdn_suff ],
        [ "BGD", cdn_host + "BGD" + cdn_suff ],
        [ "BRB", cdn_host + "BRB" + cdn_suff ],
        [ "BLR", cdn_host + "BLR" + cdn_suff ],
        [ "BEL", cdn_host + "BEL" + cdn_suff ],
        [ "BLZ", cdn_host + "BLZ" + cdn_suff ],
        [ "BEN", cdn_host + "BEN" + cdn_suff ],
        [ "BTN", cdn_host + "BTN" + cdn_suff ],
        [ "BOL", cdn_host + "BOL" + cdn_suff ],
        [ "BIH", cdn_host + "BIH" + cdn_suff ],
        [ "BWA", cdn_host + "BWA" + cdn_suff ],
        [ "BRA", cdn_host + "BRA" + cdn_suff ],
        [ "BRN", cdn_host + "BRN" + cdn_suff ],
        [ "BGR", cdn_host + "BGR" + cdn_suff ],
        [ "BFA", cdn_host + "BFA" + cdn_suff ],
        [ "BDI", cdn_host + "BDI" + cdn_suff ],
        [ "CPV", cdn_host + "CPV" + cdn_suff ],
        [ "KHM", cdn_host + "KHM" + cdn_suff ],
        [ "CMR", cdn_host + "CMR" + cdn_suff ],
        [ "CAN", cdn_host + "CAN" + cdn_suff ],
        [ "CAF", cdn_host + "CAF" + cdn_suff ],
        [ "TCD", cdn_host + "TCD" + cdn_suff ],
        [ "CHL", cdn_host + "CHL" + cdn_suff ],
        [ "CHN", cdn_host + "CHN" + cdn_suff ],
        [ "COL", cdn_host + "COL" + cdn_suff ],
        [ "COM", cdn_host + "COM" + cdn_suff ],
        [ "COD", cdn_host + "COD" + cdn_suff ],
        [ "COG", cdn_host + "COG" + cdn_suff ],
        [ "CRI", cdn_host + "CRI" + cdn_suff ],
        [ "CIV", cdn_host + "CIV" + cdn_suff ],
        [ "HRV", cdn_host + "HRV" + cdn_suff ],
        [ "CUB", cdn_host + "CUB" + cdn_suff ],
        [ "CYP", cdn_host + "CYP" + cdn_suff ],
        [ "CZE", cdn_host + "CZE" + cdn_suff ],
        [ "DNK", cdn_host + "DNK" + cdn_suff ],
        [ "DJI", cdn_host + "DJI" + cdn_suff ],
        [ "DMA", cdn_host + "DMA" + cdn_suff ],
        [ "DOM", cdn_host + "DOM" + cdn_suff ],
        [ "ECU", cdn_host + "ECU" + cdn_suff ],
        [ "EGY", cdn_host + "EGY" + cdn_suff ],
        [ "SLV", cdn_host + "SLV" + cdn_suff ],
        [ "GNQ", cdn_host + "GNQ" + cdn_suff ],
        [ "ERI", cdn_host + "ERI" + cdn_suff ],
        [ "EST", cdn_host + "EST" + cdn_suff ],
        [ "SWZ", cdn_host + "SWZ" + cdn_suff ],
        [ "ETH", cdn_host + "ETH" + cdn_suff ],
        [ "FJI", cdn_host + "FJI" + cdn_suff ],
        [ "FIN", cdn_host + "FIN" + cdn_suff ],
        [ "FRA", cdn_host + "FRA" + cdn_suff ],
        [ "GAB", cdn_host + "GAB" + cdn_suff ],
        [ "GMB", cdn_host + "GMB" + cdn_suff ],
        [ "GEO", cdn_host + "GEO" + cdn_suff ],
        [ "DEU", cdn_host + "DEU" + cdn_suff ],
        [ "GHA", cdn_host + "GHA" + cdn_suff ],
        [ "GRC", cdn_host + "GRC" + cdn_suff ],
        [ "GRD", cdn_host + "GRD" + cdn_suff ],
        [ "GTM", cdn_host + "GTM" + cdn_suff ],
        [ "GIN", cdn_host + "GIN" + cdn_suff ],
        [ "GNB", cdn_host + "GNB" + cdn_suff ],
        [ "GUY", cdn_host + "GUY" + cdn_suff ],
        [ "HTI", cdn_host + "HTI" + cdn_suff ],
        [ "VAT", cdn_host + "VAT" + cdn_suff ],
        [ "HND", cdn_host + "HND" + cdn_suff ],
        [ "HUN", cdn_host + "HUN" + cdn_suff ],
        [ "ISL", cdn_host + "ISL" + cdn_suff ],
        [ "IND", cdn_host + "IND" + cdn_suff ],
        [ "IDN", cdn_host + "IDN" + cdn_suff ],
        [ "IRN", cdn_host + "IRN" + cdn_suff ],
        [ "IRQ", cdn_host + "IRQ" + cdn_suff ],
        [ "IRL", cdn_host + "IRL" + cdn_suff ],
        [ "ISR", cdn_host + "ISR" + cdn_suff ],
        [ "ITA", cdn_host + "ITA" + cdn_suff ],
        [ "JAM", cdn_host + "JAM" + cdn_suff ],
        [ "JPN", cdn_host + "JPN" + cdn_suff ],
        [ "JOR", cdn_host + "JOR" + cdn_suff ],
        [ "KAZ", cdn_host + "KAZ" + cdn_suff ],
        [ "KEN", cdn_host + "KEN" + cdn_suff ],
        [ "KIR", cdn_host + "KIR" + cdn_suff ],
        [ "PRK", cdn_host + "PRK" + cdn_suff ],
        [ "KOR", cdn_host + "KOR" + cdn_suff ],
        [ "KWT", cdn_host + "KWT" + cdn_suff ],
        [ "KGZ", cdn_host + "KGZ" + cdn_suff ],
        [ "LAO", cdn_host + "LAO" + cdn_suff ],
        [ "LVA", cdn_host + "LVA" + cdn_suff ],
        [ "LBN", cdn_host + "LBN" + cdn_suff ],
        [ "LSO", cdn_host + "LSO" + cdn_suff ],
        [ "LBR", cdn_host + "LBR" + cdn_suff ],
        [ "LBY", cdn_host + "LBY" + cdn_suff ],
        [ "LIE", cdn_host + "LIE" + cdn_suff ],
        [ "LTU", cdn_host + "LTU" + cdn_suff ],
        [ "LUX", cdn_host + "LUX" + cdn_suff ],
        [ "MDG", cdn_host + "MDG" + cdn_suff ],
        [ "MWI", cdn_host + "MWI" + cdn_suff ],
        [ "MYS", cdn_host + "MYS" + cdn_suff ],
        [ "MDV", cdn_host + "MDV" + cdn_suff ],
        [ "MLI", cdn_host + "MLI" + cdn_suff ],
        [ "MLT", cdn_host + "MLT" + cdn_suff ],
        [ "MHL", cdn_host + "MHL" + cdn_suff ],
        [ "MRT", cdn_host + "MRT" + cdn_suff ],
        [ "MUS", cdn_host + "MUS" + cdn_suff ],
        [ "MEX", cdn_host + "MEX" + cdn_suff ],
        [ "FSM", cdn_host + "FSM" + cdn_suff ],
        [ "MDA", cdn_host + "MDA" + cdn_suff ],
        [ "MCO", cdn_host + "MCO" + cdn_suff ],
        [ "MNG", cdn_host + "MNG" + cdn_suff ],
        [ "MNE", cdn_host + "MNE" + cdn_suff ],
        [ "MAR", cdn_host + "MAR" + cdn_suff ],
        [ "MOZ", cdn_host + "MOZ" + cdn_suff ],
        [ "MMR", cdn_host + "MMR" + cdn_suff ],
        [ "NAM", cdn_host + "NAM" + cdn_suff ],
        [ "NRU", cdn_host + "NRU" + cdn_suff ],
        [ "NPL", cdn_host + "NPL" + cdn_suff ],
        [ "NLD", cdn_host + "NLD" + cdn_suff ],
        [ "NZL", cdn_host + "NZL" + cdn_suff ],
        [ "NIC", cdn_host + "NIC" + cdn_suff ],
        [ "NER", cdn_host + "NER" + cdn_suff ],
        [ "NGA", cdn_host + "NGA" + cdn_suff ],
        [ "NOR", cdn_host + "NOR" + cdn_suff ],
        [ "OMN", cdn_host + "OMN" + cdn_suff ],
        [ "PAK", cdn_host + "PAK" + cdn_suff ],
        [ "PLW", cdn_host + "PLW" + cdn_suff ],
        [ "PSE", cdn_host + "PSE" + cdn_suff ],
        [ "PAN", cdn_host + "PAN" + cdn_suff ],
        [ "PNG", cdn_host + "PNG" + cdn_suff ],
        [ "PRY", cdn_host + "PRY" + cdn_suff ],
        [ "PER", cdn_host + "PER" + cdn_suff ],
        [ "PHL", cdn_host + "PHL" + cdn_suff ],
        [ "POL", cdn_host + "POL" + cdn_suff ],
        [ "PRT", cdn_host + "PRT" + cdn_suff ],
        [ "QAT", cdn_host + "QAT" + cdn_suff ],
        [ "MKD", cdn_host + "MKD" + cdn_suff ],
        [ "ROU", cdn_host + "ROU" + cdn_suff ],
        [ "RUS", cdn_host + "RUS" + cdn_suff ],
        [ "RWA", cdn_host + "RWA" + cdn_suff ],
        [ "KNA", cdn_host + "KNA" + cdn_suff ],
        [ "LCA", cdn_host + "LCA" + cdn_suff ],
        [ "VCT", cdn_host + "VCT" + cdn_suff ],
        [ "WSM", cdn_host + "WSM" + cdn_suff ],
        [ "SMR", cdn_host + "SMR" + cdn_suff ],
        [ "STP", cdn_host + "STP" + cdn_suff ],
        [ "SAU", cdn_host + "SAU" + cdn_suff ],
        [ "SEN", cdn_host + "SEN" + cdn_suff ],
        [ "SRB", cdn_host + "SRB" + cdn_suff ],
        [ "SYC", cdn_host + "SYC" + cdn_suff ],
        [ "SLE", cdn_host + "SLE" + cdn_suff ],
        [ "SGP", cdn_host + "SGP" + cdn_suff ],
        [ "SVK", cdn_host + "SVK" + cdn_suff ],
        [ "SVN", cdn_host + "SVN" + cdn_suff ],
        [ "SLB", cdn_host + "SLB" + cdn_suff ],
        [ "SOM", cdn_host + "SOM" + cdn_suff ],
        [ "ZAF", cdn_host + "ZAF" + cdn_suff ],
        [ "SSD", cdn_host + "SSD" + cdn_suff ],
        [ "ESP", cdn_host + "ESP" + cdn_suff ],
        [ "LKA", cdn_host + "LKA" + cdn_suff ],
        [ "SDN", cdn_host + "SDN" + cdn_suff ],
        [ "SUR", cdn_host + "SUR" + cdn_suff ],
        [ "SWE", cdn_host + "SWE" + cdn_suff ],
        [ "CHE", cdn_host + "CHE" + cdn_suff ],
        [ "SYR", cdn_host + "SYR" + cdn_suff ],
        [ "TJK", cdn_host + "TJK" + cdn_suff ],
        [ "TZA", cdn_host + "TZA" + cdn_suff ],
        [ "THA", cdn_host + "THA" + cdn_suff ],
        [ "TLS", cdn_host + "TLS" + cdn_suff ],
        [ "TGO", cdn_host + "TGO" + cdn_suff ],
        [ "TON", cdn_host + "TON" + cdn_suff ],
        [ "TTO", cdn_host + "TTO" + cdn_suff ],
        [ "TUN", cdn_host + "TUN" + cdn_suff ],
        [ "TUR", cdn_host + "TUR" + cdn_suff ],
        [ "TKM", cdn_host + "TKM" + cdn_suff ],
        [ "TUV", cdn_host + "TUV" + cdn_suff ],
        [ "UGA", cdn_host + "UGA" + cdn_suff ],
        [ "UKR", cdn_host + "UKR" + cdn_suff ],
        [ "ARE", cdn_host + "ARE" + cdn_suff ],
        [ "GBR", cdn_host + "GBR" + cdn_suff ],
        [ "USA", cdn_host + "USA" + cdn_suff ],
        [ "URY", cdn_host + "URY" + cdn_suff ],
        [ "UZB", cdn_host + "UZB" + cdn_suff ],
        [ "VUT", cdn_host + "VUT" + cdn_suff ],
        [ "VEN", cdn_host + "VEN" + cdn_suff ],
        [ "VNM", cdn_host + "VNM" + cdn_suff ],
        [ "YEM", cdn_host + "YEM" + cdn_suff ],
        [ "ZMB", cdn_host + "ZMB" + cdn_suff ],
        [ "ZWE", cdn_host + "ZWE" + cdn_suff ],
    ]

    check_path = Path(genv.v__locale__)
    if not check_path.is_dir():
        print("Error: loacles directory not found.")
        print("abort.")
        sys.exit(1)
    try:
        genv.v__app__locale = os.path.join(genv.v__locale__, "LC_MESSAGES")
        genv.v__app__locale = os.path.join(genv.v__app__locale, genv.v__app__config["common"]["language"])
        genv.v__app__locale = os.path.join(genv.v__app__locale, genv.v__app__name_mo)
        #
        if len(genv.v__app__locale) < 5:
            print("Error: locale out of seed.")
            print("abort.")
            sys.exit(1)
        #
        raise IgnoreOuterException
    except:
        genv.v__app__locale = os.path.join(genv.v__locale__, "LC_MESSAGES")
        genv.v__app__locale = os.path.join(genv.v__app__locale, genv.v__locale__sys[0])
        genv.v__app__locale = os.path.join(genv.v__app__locale, genv.v__app__name_mo)
        #
        raise IgnoreOuterException

except IgnoreOuterException:
    print(genv.v__app__locale)
    pass
except configparser.NoOptionError as e:
    print("Exception: option 'language' not found.")
    print("abort.")
    sys.exit(1)
except configparser.NoSectionError as e:
    print("Exception: section 'kanguage' not found.\n")
    print("abort.")
    sys.exit(1)
except configparser.Error as e:
    print("Exception: config error occur.")
    print("abort.")
    sys.exit(1)
except Exception as e:
    exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
    tb = traceback.extract_tb(e.__traceback__)[-1]
    #
    if exc_type.__name__ == "NoOptionError":
        genv.v__app__locale = os.path.join(genv.v__locale__, "LC_MESSAGES")
        genv.v__app__locale = os.path.join(genv.v__app__locale, genv.v__locale__sys[0])
        genv.v__app__locale = os.path.join(genv.v__app__locale, genv.v__app__name_mo)
        pass
    else:
        print(f"Exception occur at module import:")
        print(f"type : {exc_type.__name__}")
        print(f"value: {exc_value}")
        print(misc.StringRepeat("-",40))
        #
        print(f"file : {tb.filename}")
        print(f"line : {tb.lineno}")
        sys.exit(1)

# ------------------------------------------------------------------------
# when the user start the application script under Windows 7 and higher:
# ------------------------------------------------------------------------
try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'kallup-nonprofit.helpndoc.observer.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    print("windll error")

# ------------------------------------------------------------------------
# constants, and varibales that are used multiple times ...
# ------------------------------------------------------------------------
__copy__ = (""
    + "HelpNDoc.com FileWatcher 0.0.1\n"
    + "(c) 2024 by paule32\n"
    + "all rights reserved.\n")

__error__os__error = (""
    + "can not determine operating system.\n"
    + "start aborted.")

__error__locales_error = "" \
    + "no locales file for this application."

# ------------------------------------------------------------------------
# style sheet definition's:
# ------------------------------------------------------------------------
css_model_header   = "model_hadr"
css_combobox_style = "combo_actn"

class consoleApp():
    def __init__(self):
        init(autoreset = True)
        sys.stdout.write(Fore.RESET + Back.RESET + Style.RESET_ALL)
        return
    
    def cls(self):
        sys.stdout.write("\033[H\033[2J")
        sys.stdout.flush()
        return
    
    def gotoxy(self, xpos, ypos):
        sys.stdout.write("\033["
        + str(ypos) + ";"
        + str(xpos) + "H")
        sys.stdout.flush()
        return
    
    def print(self, data):
        sys.stdout.write(data)
        sys.stdout.flush()
        return
    
    def print_date(self):
        dat = datetime.datetime.now()
        sys.stdout.write(dat.strftime("%Y-%m-%d"))
        sys.stdout.flush()

genv.dbase_console = None
genv.dbase_console = consoleApp()

class FileSystemWatcher(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.watcher = QFileSystemWatcher()
        self.fileContents = {}
    
    def addFile(self, filePath):
        print("--> " + filePath)
        self.watcher.addPath(filePath)
        self.fileContents[filePath] = self.readFromFile(filePath)  # Initialen Inhalt der Datei einlesen
    
    def fileChangedSlot(self, filePath):
        newContent = self.readFromFile(filePath)
        if self.fileContents.get(filePath) != newContent:
            self.fileContents[filePath] = newContent
            return newContent
    
    def readFromFile(self, filePath):
        fileContent = ""
        file = QFile(filePath)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            fileContent = stream.readAll()
            file.close()
        return fileContent

class ListInstructionError(Exception):
    def __init__(self):
        print((""
        + "Exception: List instructions error.\n"
        + "note: Did you miss a parameter ?\n"
        + "note: Add more information."))
        error_result = 1
        return

class ListMustBeInstructionError(Exception):
    def __init__(self):
        print("Exception: List must be of class type: InstructionItem")
        error_result = 1
        return
class ListIndexOutOfBoundsError(Exception):
    def __init__(self):
        print("Exception: List index out of bounds.")
        error_result = 1
        return

class ENoParserError(Exception):
    def __init__(self, message=None):
        if message == None:
            self.message = "this exception marks no error, but end of data."
        else:
            self.message = message
    def __str__(self):
        error_result = 0
        return str(self.message)

class EParserErrorEOF(Exception):
    def __init__(self, message=None):
        if message == None:
            self.message = "this exception marks no error, but end of data."
        else:
            self.message = message
    def __str__(self):
        error_result = 0
        return str(self.message)

class EParserErrorUnknowID(Exception):
    def __init__(self, message, lineno):
        print("Exception: unknown id: " + message)
        print("Line     : " + str(lineno))
        error_result = 1
        return

class EInvalidParserError(Exception):
    def __init__(self, message, lineno):
        self.message  = "Exception: invalid id: '" + message + "'\n"
        self.message += "line: " + str(lineno)
    
    def __str__(self):
        error_result = 1
        return str(self.message)

# ------------------------------------------------------------------------
# date / time week days
# ------------------------------------------------------------------------
class Weekday:
    def __init__(self):
        self.MONDAY    = 1
        self.TUESDAY   = 2
        self.WEDNESDAY = 3
        self.THURSDAY  = 4
        self.FRIDAY    = 5
        self.SATURDAY  = 6
        self.SUNDAY    = 7
    
    def today(cls):
        print('today is %s' % cls(date.today().isoweekday()).name)

# ------------------------------------------------------------------------
# convert the os path seperator depend ond the os system ...
# ------------------------------------------------------------------------
def convertPath(text):
    if os_type == os_type_windows:
        result = text.replace("/", "\\")
    elif os_type == os_type_linux:
        result = text.replace("\\", "/")
    else:
        showApplicationError(__error__os__error)
        sys.exit(genv.EXIT_FAILURE)
    return result

class dbase_function:
    def __init__(self, src, name):
        self.what   = "func"
        self.owner  = src
        self.name   = name
        self.result = "tztz"
        self.add(src)
    def add(self):
        self.owner.AST.append(self)
        return self

class dbase_val_variable:
    def __init__(self, src, value=0):
        self.what  = "val"
        self.owner = src
        self.value = value
        self.add(src)
    def add(self):
        self.owner.AST.append(self)
        return self

class dbase_str_variable:
    def __init__(self, src, value=""):
        self.what  = "str"
        self.owner = src
        self.value = value
        self.add(src)
    def add(self):
        self.owner.AST.append(self)
        return self

class dbase_symbol:
    def __init__(self, src, name, link=None):
        self.what  = "symbol"
        self.owner = src
        self.name  = name
        self.link  = link
        self.add(src)
    def add(self):
        self.owner.AST.append(self)
        return self

class dbase_loop:
    def __init__(self, src, start, end):
        self.what  = "loop"
        seöf.owner = src
        self.start = start
        self.end   = end
        self.add(src)
    def add(self):
        self.owner.AST.append(self)
        return self

class dbase_command:
    def __init__(self, src, name, link=None):
        print("---> " + name)
        self.what  = "keyword"
        self.owner = src
        self.name  = name
        self.proc  = None
        self.prev  = None
        self.link  = link
    def add(self):
        self.owner.AST.append(self)
        return self

# ---------------------------------------------------------------------------
# only for testing ...
# ---------------------------------------------------------------------------
class dbase_test_array_struct:
    def __init__(self):
        test_proc = dbase_function(self, "test")
        test_loop = dbase_loop(self, 1,5)
        #
        test_var1 = dbase_val_variable(self, 1234)
        test_var2 = dbase_str_variable(self, "fuzzy")
        #
        test_sym1 = dbase_symbol(self, "foo", test_var1)
        test_sym2 = dbase_symbol(self, "bar", test_var2)
        test_sym3 = dbase_symbol(self, "baz", test_proc)
        #
        test_symA = dbase_symbol(self, "L", test_loop)
        
        self.AST = [
            test_sym1,
            test_sym2,
            test_sym3,
            test_symA
        ]
        for obj in self.AST:
            if isinstance(obj, dbase_symbol):
                print("dbase:")
                print("\tObject: " + obj.name)
                #print("--> " + str(obj.what))
            if isinstance(obj.link, dbase_function):
                #print("gfun")
                print("\t\tfunc type  : " + obj.link.what)
                print("\t\tfunc name  : " + obj.link.name)
                print("\t\tfunc result: " + obj.link.result)
            elif isinstance(obj.link, dbase_val_variable):
                print("\t\tfunc type  : " + obj.link.what)
                print("\t\tfunc value : " + str(obj.link.value))
            elif isinstance(obj.link, dbase_str_variable):
                print("\t\tfunc type  : " + obj.link.what)
                print("\t\tfunc value : " + obj.link.value)
            elif isinstance(obj.link, dbase_loop):
                print("\t\tfunc type  : " + obj.link.what)
                print("\t\tfunc start : " + str(obj.link.start))
                print("\t\tfunc end   : " + str(obj.link.end))
        
        sys.exit(20)

# ---------------------------------------------------------------------------
# \brief  class for interpreting dBase related stuff ...
#         the constructor need a string based script name that shall be read
#         and execute from memory.
#
# \param  filename - a named string for the script name
# \return objref - ctor's return the created object referenz from an memory
#         internal address that is managed by the operating system logic.
#
# \author paule32
# \since  1.0.0
# ---------------------------------------------------------------------------
class interpreter_dBase:
    def __init__(self, fname):
        self.script_name = fname
        
        self.line_row    = 1
        self.line_col    = 1
        
        self.pos         = -1
        
        self.token_id    = ""
        self.token_prev  = ""
        self.token_str   = ""
        
        self.parse_data  = []
        
        self.token_macro_counter = 0
        self.token_comment_flag  = 0
        
        self.in_comment = 0
        
        self.AST = []
        
        self.byte_code = ""
        self.text_code = ""
        self.text_code = """
import os
import sys           # system specifies
import time          # thread count
import datetime      # date, and time routines

import builtins
print = builtins.print

from dbaseConsole import *

if __name__ == '__main__':
    global con
    con = consoleApp()
"""
        
        genv.v__app__logging.info("start parse: " + self.script_name)
        
        self.parser_stop = False
        self.parse_open(self.script_name)
        self.source = self.parse_data[0]
    
    # -----------------------------------------------------------------------
    # \brief finalize checks and cleaning stuff ...
    # -----------------------------------------------------------------------
    def finalize(self):
        genv.v__app__logging.debug("macro   : " + str(self.token_macro_counter))
        genv.v__app__logging.debug("comment : " + str(self.token_comment_flag))
        if self.command_ok == False:
            raise EParserErrorEOF("command not finished.")
        if self.token_macro_counter < 0:
            genv.v__app__logging.debug("\aerror: unbound macro.")
            sys.exit(1)
    
    # -----------------------------------------------------------------------
    # \brief open a script file, and append the readed lines to the source
    #        object of this class. step one read the lines (maybe not need
    #        in future releases. step two read the content of the given file
    #        as one dimensional list which is used to parse the memory stream
    #        quicker than reading from storage disks.
    #        this function have a little payload, yes - but the time of read-
    #        ing the source data informations into the memory is quantitative
    #        better as doing read/write operations by the operation system.
    #
    # \param  filename - a string that identify the file/script that should
    #                    be loaded and parsed.
    # \author paule32
    # \since  1.0.0
    # -----------------------------------------------------------------------
    def parse_open(self, file_name):
        self.parse_data.clear()
        with open(self.script_name, 'r', encoding="utf-8") as self.file:
            self.file.seek(0)
            lines  = 0
            lines  = len(self.file.readlines())
            self.file.seek(0)
            
            source = ""
            source = self.file.read()
            
            self.file.close()
        self.parse_data.append(source)
    
    def add_command(self, name, link):
        self.token_command = dbase_command(self, name, link)
        return self.token_command
    
    def run(self):
        self.finalize()
        print("----------------------")
        print(self.text_code)
        input("press enter to start...")
        
        #self.text_code += "print('Hello World !')\n"
        
        bytecode_text = compile(
            self.text_code,
            "<string>",
            "exec")
        self.byte_code = None
        self.byte_code = marshal.dumps(bytecode_text)
        
        # ---------------------
        # save binary code ...
        # ---------------------
        cachedir = "__cache__"
        if not os.path.exists(cachedir):
            print("oooooo")
            os.makedirs(cachedir)
        filename = os.path.basename(self.script_name)
        filename = os.path.splitext(filename)[0]
        filename = cachedir+"/"+filename+".bin"
        print("filename: " + filename)
        try:
            with open(filename,"wb") as bytefile:
                bytefile.write(self.byte_code)
                bytefile.close()
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        
        # ---------------------
        # load binary code ...
        # ---------------------
        try:
            with open(filename,"rb") as bytefile:
                bytecode = bytefile.read()
                bytefile.close()
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise
        
        # ---------------------
        # execute binary code:
        # ---------------------
        #bytecode = marshal.loads(self.byte_code)
        #exec(bytecode)
    
    # -----------------------------------------------------------------------
    # \brief  get one char from the input stream/source line.
    #         the internal position cursor self.pos for the self.source will
    #         be incdrement by 1 character. for statistics, the line column
    #         position wull be updated.
    #         if the sel.pos cursor is greater as self.source codem then the
    #         end of data is marked, and python raise a silent "no errpr"
    #         exception to stop the processing of data (to prevent data/buffer
    #         overflow.
    #
    # \param  nothing
    # \return char - The "non" whitespace character that was found between
    #                existing comment types.
    # \author paule32
    # \since  1.0.0
    # -----------------------------------------------------------------------
    def getChar(self):
        self.line_col += 1
        self.pos += 1

        if self.pos >= len(self.source):
            if self.in_comment > 0:
                raise EParserErrorEOF("\aunterminated string reached EOF.")
            else:
                self.parser_stop = True
                c = '\0'
                #raise ENoParserError("\aend of file reached.")
        else:
            c = self.source[self.pos]
            return c
    
    def ungetChar(self, num):
        self.line_col -= num;
        self.pos -= num;
        c = self.source[self.pos]
        return c
    
    def getIdent(self):
        while True:
            c = self.getChar()
            if c.isspace():
                return self.token_str
            elif c.isalnum():
                self.token_str += c
            else:
                self.pos -= 1
                return self.token_str
    
    def getNumber(self):
        while True:
            c = self.getChar()
            if c.isdigit():
                self.token_str += c
            else:
                self.pos -= 1
                return self.token_str
    
    # -----------------------------------------------------------------------
    # \brief skip all whitespaces. whitespaces are empty lines, lines with
    #        one or more spaces (0x20): " ", \t, "\n".
    # -----------------------------------------------------------------------
    def skip_white_spaces(self):
        while True:
            c = self.getChar()
            if c == '\0' or self.parser_stop == True:
                return c
            elif c == "\t" or c == " ":
                self.line_col += 1
                continue
            elif c == "\n" or c == "\r":
                self.line_col  = 1
                self.line_row += 1
                continue
            elif c == '/':
                c = self.getChar()
                if c == '*':
                    self.in_comment += 1
                    while True:
                        c = self.getChar()
                        if c == "\n":
                            self.line_col  = 1
                            self.line_row += 1
                            continue
                        if c == '*':
                            c = self.getChar()
                            if c == '/':
                                self.in_comment -= 1
                                break
                    return self.skip_white_spaces()
                elif c == '/':
                    self.handle_oneline_comment()
                    continue
                else:
                    self.ungetChar(1)
                    c = "/"
                    return c
            elif c == '&':
                c = self.getChar()
                if c == '&':
                    self.handle_oneline_comment()
                    continue
                else:
                    self.__unexpectedChar('&')
            elif c == '*':
                c = self.getChar()
                if c == '*':
                    self.handle_oneline_comment()
                    continue
                else:
                    self.__unexpectedChar('*')
            else:
                return c
    
    # -----------------------------------------------------------------------
    # \brief parse a one line comment: // for c++, ** and && for dBase ...
    # -----------------------------------------------------------------------
    def handle_oneline_comment(self):
        while True:
            c = self.getChar()
            if c == "\n":
                self.line_row += 1
                self.line_col  = 1
                break
    
    def handle_commands(self):
        if self.token_str.lower() == "date":
            c = self.skip_white_spaces()
            if c == '(':
                c = self.skip_white_spaces()
                if c == ')':
                    print("dater")
                    self.text_code   += ("    con.gotoxy(" +
                    self.xpos + ","   +
                    self.ypos + ")\n" +  "    con.print_date()\n")
                    
                    self.command_ok = True
                else:
                    self.__unexpectedChar(c)
            else:
                self.__unexpectedChar(c)
        elif self.token_str.lower() == "str":
            c = self.skip_white_spaces()
            if c == '(':
                c = self.skip_white_spaces()
                if c == ')':
                    print("strrr")
                    self.command_ok = True
                else:
                    self.__unexpectedChar(c)
            else:
                self.__unexpectedChar(c)
        else:
            self.__unexpectedToken()
    
    def handle_string(self):
        while True:
            c = self.getChar()
            if c == '"':
                break
            elif c == '\\':
                c = self.getChar()
                if c == "\n" or c == "\r":
                    self.__unexpectedEndOfLine()
                elif c == " ":
                    self.__unexpectedEscapeSign()
                elif c == '\\':
                    self.token_str += "\\"
                elif c == 't':
                    self.token_str += "    "
                elif c == 'n':
                    self.token_str += "\n"
                elif c == 'r':
                    self.token_str += "\r"
                elif c == 'a':
                    self.token_str += "\a"
                else:
                    self.token_str += c
                continue
            else:
                self.token_str += c
                continue
        c = self.skip_white_spaces()
        if c == '+':
            c = self.skip_white_spaces()
            if c == '"':
                self.handle_string()
                print("---> " + self.token_str)
                return
            elif c.isalpha():
                self.token_str = c
                self.getIdent()
                self.handle_commands()
                print("---> " + self.token_str)
                return
            else:
                self.__unexpectedChar(c)
        if c == '@':
            self.ungetChar(1)
            return
        else:
            self.__unexpectedChar(c)
    
    def handle_say(self):
        self.command_ok = False
        c = self.skip_white_spaces()
        print("==> " + c)
        if c.isdigit():
            self.token_str = c
            self.getNumber()                        # row
            self.ypos = self.token_str
            c = self.skip_white_spaces()
            if c == ',':
                c = self.skip_white_spaces()
                if c.isdigit():
                    self.token_str = c
                    self.getNumber()                # col
                    self.xpos = self.token_str
                    c = self.skip_white_spaces()
                    if c.isalpha():
                        self.token_str = c
                        self.getIdent()
                        if self.token_str.lower() == "say":
                            self.prev = "say"
                            c = self.skip_white_spaces()
                            if c.isalpha():
                                self.token_str = c
                                self.getIdent()
                                self.handle_commands()
                            elif c == '"':
                                print("ssss")
                                self.token_str = ""
                                self.handle_string()
                                print("eeeee")
                        else:
                            raise Exception("say expected.")
                    else:
                        raise Exception("say expected.")
                else:
                    raise Exception("number expected.")
            else:
                raise Exception("comma expected.")
    
    def parse(self):
        self.token_str = ""
        self.text_code = ""
        
        with open(self.script_name, 'r', encoding="utf-8") as self.file:
            self.file.seek(0)
            self.total_lines = 0
            self.total_lines = len(self.file.readlines())
            self.file.seek(0)
            
            self.source = ""
            self.source = self.file.read()
            
            genv.v__app__logging.debug("lines: " + str(self.total_lines))
            self.file.close()
        
        if len(self.source) < 1:
            print("no data available.")
            return
        
        # ------------------------------------
        # ------------------------------------
        while True:
            c = self.skip_white_spaces()
            if c == '\0' or self.parser_stop == True:
                break
            elif c == '@':
                self.handle_say()
            elif c.isalpha():
                self.token_str = c
                self.getIdent()
                if self.token_str == "clear":
                    print("clear")
                    c = self.skip_white_spaces()
                    if c.isalpha():
                        self.token_str = c
                        self.getIdent()
                        if self.token_str == "screen":
                            print("scre")
                            self.text_code += "    con.cls()\n";
                        elif self.token_str == "memory":
                            print("mem")
                        else:
                            print("--> " + self.token_str)
                            self.ungetChar(len(self.token_str))
                    else:
                        self.ungetChar(1)
                        continue
                if self.token_str == "show":
                    print("--> " + self.token_str)
    
    def __unexpectedToken(self):
        __msg = "unexpected token: '" + self.token_str + "'"
        __unexpectedError(__msg)
    
    def __unexpectedChar(self, chr):
        __msg = "unexpected character: '" + chr + "'"
        __unexpectedError(__msg)
    
    def __unexpectedEndOfLine(self):
        __unexpectedError("unexpected end of line")
    
    def __unexpectedEscapeSign(self):
        __unexpectedError("nunexpected escape sign")
    
    def __unexpectedError(self, message):
        calledFrom = inspect.stack()[1][3]
        msg = "\a\n" + message + " at line: '%d' in: '%s'.\n"
        msg = msg % (
            self.line_row,
            self.script_name)
        print(msg)
        sys.exit(1)
    
# ---------------------------------------------------------------------------
# \brief  provide dBase DSL (domain source language)- dBL (data base language
#         class for handling and programming database applications.
#
# \param  filename - a string based file/script that shall be handled.
# \return objref - ctor's return the created object referenz from an memory
#         internal address that is managed by the operating system logic.
#
# \author paule32
# \since  1.0.0
# ---------------------------------------------------------------------------
class dBaseDSL():
    def __init__(self, script_name):
        self.script = None
        
        self.parser = None
        self.parser = interpreter_dBase(script_name)
        self.parser.parse()

# ------------------------------------------------------------------------
# read a file into memory ...
# ------------------------------------------------------------------------
def read_gzfile_to_memory(file_path):
    check_file = Path(file_path)
    print(check_file)
    if not check_file.exists():
        print("Error: gzfile directory exists, but file could not found.")
        print("abort.")
        sys.exit(1)
    if check_file.is_dir():
        print("Error: gzfile is not a file.")
        print("abort.")
        sys.exit(1)
    if check_file.is_file():
        with open(check_file, "rb") as file:
            file_header = file.read(3)
            if file_header == b'\x1f\x8b\x08':
                print("packed")
                file.seek(0)
                file_data = file.read()
                compressed_data = io.BytesIO(file_data)
                with gzip.GzipFile(fileobj=compressed_data, mode="rb") as gzip_file:
                    uncompressed_data = gzip_file.read()
                file.close()
                mo_file = io.BytesIO(uncompressed_data)
                translations = gettext.GNUTranslations(mo_file)
                translations.install()
                _ = translations.gettext
                return _
            elif file_header == b'\xde\x12\x04':
                print("not packed")
                file.seek(0)
                file_data = file.read()
                mo_file = io.BytesIO(file_data)
                translations = gettext.GNUTranslations(mo_file)
                translations.install()
                _ = translations.gettext
                return _
            else:
                file.close()
                print("Error: language mo file could not be load.")
                print("abort.")
                sys.exit(1)
    return None

# ------------------------------------------------------------------------
# get the locale, based on the system locale settings ...
# ------------------------------------------------------------------------
def getLangIDText(text):
    return _(text)

def handle_language(lang):
    try:
        # todo: .ini over write
        # os.path.join(genv.v__locale__,genv.v__locale__sys[0])
        #
        file_path = os.path.join(genv.v__locale__, genv.v__locale__enu)
        file_path = os.path.join(file_path, "LC_MESSAGES")
        file_path = os.path.join(file_path, genv. v__app__name_mo + ".gz")
        #
        _ = read_gzfile_to_memory(file_path)
        return _
    except Exception as e:
        exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
        tb = traceback.extract_tb(e.__traceback__)[-1]
        
        print(f"Exception occur during handle language:")
        print(f"type : {exc_type.__name__}")
        print(f"value: {exc_value}")
        print(misc.StringRepeat("-",40))
        #
        print(f"file : {tb.filename}")
        print(f"llline : {tb.lineno}")
        #
        sys.exit(genv.EXIT_FAILURE)

# ------------------------------------------------------------------------
# check, if the gui application is initialized by an instance of app ...
# ------------------------------------------------------------------------
def isApplicationInit():
    if genv.v__app_object == None:
        genv.v__app_object = QApplication(sys.argv)
    # ----------------------------------------------
    if genv.v__app_object.instance() == None:
        genv.v__app_object = QApplication(sys.argv)
    return True

# ------------------------------------------------------------------------
# methode to show information about this application script ...
# ------------------------------------------------------------------------
def showInfo(text):
    if not genv.v__app_object:
        genv.v__app_object = QApplication(sys.argv)
    
    infoWindow = QMessageBox()
    infoWindow.setIcon(QMessageBox.Information)
    infoWindow.setWindowTitle("Information")
    infoWindow.setText(text)
    infoWindow.exec_()

def showApplicationInformation(text):
    if isApplicationInit() == False:
        genv.v__app_object = QApplication(sys.argv)
        showInfo(text)
    else:
        print(text)

# ------------------------------------------------------------------------
# methode to show error about this application script ...
# ------------------------------------------------------------------------
def showError(text):
    if not isApplicationInit():
        genv.v__app_object = QApplication(sys.argv)
    
    infoWindow = QMessageBox()
    infoWindow.setIcon(QMessageBox.Critical)
    infoWindow.setWindowTitle("Error")
    infoWindow.setText(text)
    infoWindow.show()
    infoWindow.exec_()

def showApplicationError(text):
    if isApplicationInit() == False:
        genv.v__app_object = QApplication(sys.argv)
        showError(text)
    else:
        print(text)

# ------------------------------------------------------------------------
# get current time, and date measured on "now" ...
# ------------------------------------------------------------------------
def get_current_time():
    return datetime.datetime.now().strftime("%H_%M")

def get_current_date():
    return datetime.datetime.now().strftime("%Y_%m_%d")

def handleExceptionApplication(func,arg1=""):
    global error_fail, error_result
    error_fail = False
    error_result = 0
    try:
        func(arg1)
    except NoOptionError:
        print("----")
        genv.v__app__locale = os.path.join(genv.v__locale__, "LC_MESSAGES")
        genv.v__app__locale = os.path.join(genv.v__app__locale, genv.v__locale__sys[0])
        genv.v__app__locale = os.path.join(genv.v__app__locale, genv.v__app__name_mo)
        print("==> " + genv.v__app__locale)
    except ListInstructionError as ex:
        ex.add_note("Did you miss a parameter ?")
        ex.add_note("Add more information.")
        print("List instructions error.")
        error_result = 1
    except ZeroDivisionError as ex:
        ex.add_note("1/0 not allowed !")
        print("Handling run-time error:", ex)
        error_result = 1
    except OSError as ex:
        print("OS error:", ex)
        error_result = 1
    except ValueError as ex:
        print("Could not convert data:", ex)
        error_result = 1
    except Exception as ex:
        exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
        tb = traceback.extract_tb(ex.__traceback__)[-1]
        
        print(f"Exception occur:")
        print(f"type : {exc_type.__name__}")
        print(f"value: {exc_value}")
        print(misc.StringRepeat("-",40))
        #
        print(f"file : {tb.filename}")
        print(f"line : {tb.lineno}")
        #
        print(misc.StringRepeat("-",40))
        
        s = f"{ex.args}"
        parts = [part.strip() for part in s.split("'") if part.strip()]
        parts.pop( 0)   # delete first element
        parts.pop(-1)   # delete last  element
        
        err = "error: Exception occured: "
        if type(ex) == NameError:
            err += "NameError\n"
            err += "text: '" + parts[0]+"' not defined\n"
        elif type(ex) == AttributeError:
            err += "AttributeError\n"
            err += "class: " + parts[0]+"\n"
            err += "text : " + parts[2]+": "+parts[1]+"\n"
        else:
            err += "type  : " + "default  \n"
        
        error_ex = err
        
        error_result = 1
        error_fail   = True
        print(ex)
    finally:
        # ---------------------------------------------------------
        # when all is gone, stop the running script ...
        # ---------------------------------------------------------
        if error_result > 0:
            print("abort.")
            sys.exit(error_result)
        
        print("Done.")
        sys.exit(0)

# ------------------------------------------------------------------------
# custom widget for QListWidgetItem element's ...
# ------------------------------------------------------------------------
class customQListWidgetItem(QListWidgetItem):
    def __init__(self, name, parent):
        super().__init__()
        
        self.name = name
        self.parent = parent
        
        element = QListWidgetItem(name, parent)
        
        self.setSizeHint(element.sizeHint())
        self.setData(0, self.name)

# ------------------------------------------------------------------------
#
# ------------------------------------------------------------------------
class myLineEdit(QLineEdit):
    def __init__(self, name=""):
        super().__init__()
        self.name = name
        self.init_ui()
    
    def init_ui(self):
        self.setMinimumHeight(26)
        self.setMaximumWidth(250)
        self.setText(self.name)
        self.cssColor = _("edit_css")
        self.setStyleSheet(self.cssColor)

class myDBaseTextEditor(QTextEdit):
    def __init__(self, name=None):
        super().__init__()
        font = QFont("Courier New", 10)
        self.setFont(font)
        self.setMaximumHeight(545)
        self.setMinimumHeight(545)
        self.setLineWrapMode(QTextEdit.NoWrap)
        
        #try:
        #    #if not name == None:
        #    #    self.script_name = genv.v__app__scriptname__
        #    #    with open(self.script_name, "r") as file:
        #    #        text = file.read()
        #    #        self.setText(text)
        #    #        file.close()
        #except Exception as e:
        #    exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
        #    tb = traceback.extract_tb(e.__traceback__)[-1]
        #    
        #    print(f"Exception occur during file load:")
        #    print(f"type : {exc_type.__name__}")
        #    print(f"value: {exc_value}")
        #    print(misc.StringRepeat("-",40))
        #    #
        #    print(f"file : {tb.filename}")
        #    print(f"line : {tb.lineno}")
        #    #
        #    print(misc.StringRepeat("-",40))
        #    print("file not found.")
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F2:
            print("\a")
        else:
            super().keyPressEvent(event)

# ------------------------------------------------------------------------
#
# ------------------------------------------------------------------------
class myTextEdit(QTextEdit):
    def __init__(self, name=""):
        super().__init__()
        self.name = name
        self.cssColor = _("text_css")
        self.setStyleSheet(self.cssColor)
        self.setText(self.name)
    
    def mousePressEvent(self, event):
        self.anchor = self.anchorAt(event.pos())
        if self.anchor:
            QApplication.setOverrideCursor(Qt.PointingHandCursor)
    
    def mouseReleaseEvent(self, event):
        if self.anchor:
            QDesktopServices.openUrl(QUrl(self.anchor))
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.anchor = None

# ------------------------------------------------------------------------
#
# ------------------------------------------------------------------------
class OverlayWidget(QWidget):
    def __init__(self, parent, text):
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.ToolTip)
        
        self.xpos = 100
        self.ypos = 100
        
        self.setGeometry(
        self.xpos,
        self.ypos, 250, 120)
        self.setStyleSheet(_("overlaycss"))
        
        self.caption = text
        
        font = QFont(genv.v__app__font)
        font.setPointSize(11)
        font.setBold(True)
        
        self.vlayout = QVBoxLayout  ()
        self.label1  = QLabel(self.caption)
        self.label1.setMinimumHeight(100)
        self.label1.setAlignment(Qt.AlignBottom)
        self.label1.setFont(font)
        
        self.vlayout.addWidget(self.label1)
        self.setLayout(self.vlayout)

class myIconLabel(QLabel):
    def __init__(self, parent, text, mode):
        super().__init__(parent)
        
        self.overlay = OverlayWidget(self, text)
        self.caption = text
        self.mode    = mode
        self.parent  = parent
    
    def show_overlay(self):
        self.overlay.move(
            QCursor().pos().x()+50,
            QCursor().pos().y())
        self.overlay.show()
    
    def hide_overlay(self):
        self.overlay.hide()
    
    def mousePressEvent(self, event):
        parent = self.parent.parent
        if event.button() == Qt.LeftButton:
            #print(self.caption)
            if self.mode == 0:
                self.btn_clicked(self.parent,parent.help_tabs)
            elif self.mode == 1:
                self.btn_clicked(self.parent,parent.dbase_tabs)
            elif self.mode == 2:
                self.btn_clicked(self.parent,parent.pascal_tabs)
            elif self.mode == 3:
                self.btn_clicked(self.parent,parent.isoc_tabs)
            elif self.mode == 4:
                self.btn_clicked(self.parent,parent.java_tabs)
            elif self.mode == 5:
                self.btn_clicked(self.parent,parent.python_tabs)
            elif self.mode == 6:
                self.btn_clicked(self.parent,parent.lisp_tabs)
            elif self.mode == 10:
                self.btn_clicked(self.parent,parent.locale_tabs)
            elif self.mode == 11:
                self.btn_clicked(self.parent,parent.c64_tabs)
    
    def enterEvent(self, event):
        self.show_overlay()
    
    def leaveEvent(self, event):
        self.hide_overlay()
    
    def hide_tabs(self):
        parent = self.parent.parent
        
        parent.help_tabs.hide()
        parent.dbase_tabs.hide()
        parent.pascal_tabs.hide()
        parent.isoc_tabs.hide()
        parent.java_tabs.hide()
        parent.python_tabs.hide()
        parent.lisp_tabs.hide()
        parent.locale_tabs.hide()
        parent.c64_tabs.hide()
    
    def btn_clicked(self,btn,tabs):
        if not self.parent.parent.c64_screen.worker_thread == None:
            self.parent.parent.c64_screen.worker_thread.stop()
            self.parent.parent.c64_screen.worker_thread = None
        
        self.hide_tabs()
        tabs.show()
        
        self.set_null_state()
        btn.state = 2
        btn.set_style()
    
    def set_null_state(self):
        parent = self.parent.parent
        side_buttons = [
            parent.side_btn1,
            parent.side_btn2,
            parent.side_btn3,
            parent.side_btn4,
            parent.side_btn5,
            parent.side_btn6,
            parent.side_btn7,
            parent.side_btn8,
            parent.side_btn9,
        ]
        for btn in side_buttons:
            btn.state = 0
            btn.set_style()

class myIconButton(QWidget):
    def __init__(self, parent, mode, label_text, text):
        super().__init__()
        
        self.parent = parent
        
        self.vl = QVBoxLayout()
        self.pix_label = myIconLabel(self, text, mode)
        
        self.txt_fonda = QFont(genv.v__app__font,10)
        self.txt_fonda.setBold(True)
        #
        self.txt_label = QLabel(label_text)
        self.txt_label.setAlignment(Qt.AlignCenter)
        self.txt_label.setFont(self.txt_fonda)
        
        self.pix_label.setObjectName("lbl-image")
        self.txt_label.setObjectName("lbl-text")
        
        self.vl.addWidget(self.pix_label)
        self.vl.addWidget(self.txt_label)
        #
        self.setLayout(self.vl)
        
        self.caption = text
        self.mode    = mode
        self.state   = 0
        
        self.bordercolor = "lightgray"
        self.parent      = parent
        self.state       = 0
        
        fg = str(1) + genv.v__app__img_ext__
        bg = str(2) + genv.v__app__img_ext__
        
        self.pix_label.setMinimumWidth (79)
        self.pix_label.setMinimumHeight(79)
        #
        self.pix_label.setMaximumWidth (79)
        self.pix_label.setMaximumHeight(79)
        
        ptx = ""
        
        self.image_fg = ptx + genv.v__app__helpdev__ + fg
        self.image_bg = ptx + genv.v__app__helpdev__ + bg
        
        parent.side_layout.addWidget(self)
        
        if mode == 0:
            self.image_fg = ptx + genv.v__app__helpdev__ + fg
            self.image_bg = ptx + genv.v__app__helpdev__ + bg
        
        elif mode == 1:
            self.image_fg = ptx + genv.v__app__dbasedb__ + fg
            self.image_bg = ptx + genv.v__app__dbasedb__ + bg
        
        elif mode == 2:
            self.image_fg = ptx + genv.v__app__freepas__ + fg
            self.image_bg = ptx + genv.v__app__freepas__ + bg
        
        elif mode == 3:
            self.image_fg = ptx + genv.v__app__cpp1dev__ + fg
            self.image_bg = ptx + genv.v__app__cpp1dev__ + bg
        
        elif mode == 4:
            self.image_fg = ptx + genv.v__app__javadev__ + fg
            self.image_bg = ptx + genv.v__app__javadev__ + bg
        
        elif mode == 5:
            self.image_fg = ptx + genv.v__app__pythonc__ + fg
            self.image_bg = ptx + genv.v__app__pythonc__ + bg
        
        elif mode == 6:
            self.image_fg = ptx + genv.v__app__lispmod__ + fg
            self.image_bg = ptx + genv.v__app__lispmod__ + bg
        
        elif mode == 10:
            self.image_fg = ptx + genv.v__app__locales__ + fg
            self.image_bg = ptx + genv.v__app__locales__ + bg
        
        elif mode == 11:
            self.image_fg = ptx + genv.v__app__com_c64__ + fg
            self.image_bg = ptx + genv.v__app__com_c64__ + bg
        
        self.set_style()
    
    def set_style(self):
        if self.state == 2:
            self.bordercolor = "lime"
        else:
            self.bordercolor = "lightgray"
        
        style = _("labelico_css")        \
        .replace("{fg}", self.image_fg.replace("\\","/"))  \
        .replace("{bg}", self.image_bg.replace("\\","/"))  \
        .replace("{bc}", self.bordercolor)
        
        self.pix_label.setStyleSheet(style)
    
    def enterEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "gray";
            self.set_style()
        self.setCursor(QCursor(Qt.PointingHandCursor))
    
    def leaveEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "lightgray";
            self.set_style()
        self.setCursor(QCursor(Qt.ArrowCursor))

class myCustomLabel(QLabel):
    def __init__(self, text, helpID, helpText):
        super().__init__(text)
        
        self.helpID     = helpID
        self.helpText   = helpText
        
        self.helpAnchor = "pupu"
    
    def enterEvent(self, event):
        sv_help.setText(self.helpText)
    
    def mousePressEvent(self, event):
        QApplication.setOverrideCursor(Qt.PointingHandCursor)
        return
    
    def mouseReleaseEvent(self, event):
        QDesktopServices.openUrl(QUrl(self.helpAnchor))
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        return

# ------------------------------------------------------------------------
# create a scroll view for the mode tab on left side of application ...
# ------------------------------------------------------------------------
class iconComboBox(QComboBox):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), Qt.white)
        
        for i in range(self.count()):
            item_rect = self.view().visualRect(
            self.model().index(i, 0))
            
            icon = self.itemIcon(i)
            text = self.itemText(i)
            
            if not item_rect.isNull():
                if not icon.isNull():
                    icon_size = icon.actualSize(
                        QSize(
                            item_rect.height(),
                            item_rect.height()))
                    icon_rect = QRect(
                        item_rect.left() + 4,
                        item_rect.top(), 56,
                        item_rect.height())
                    icon.paint(painter,
                        icon_rect,
                        Qt.AlignCenter,
                        QIcon.Normal,
                        QIcon.Off)
                if not icon.isNull():
                    right_icon_rect = QRect(
                        item_rect.right() - item_rect.height(),
                        item_rect.top(),
                        icon_size.width(),
                        icon_size.height())
                    icon.paint(painter,
                        right_icon_rect,
                        Qt.AlignCenter,
                        QIcon.Normal,
                        QIcon.Off)
        
        arrow_icon = self.style().standardIcon(self.style().SP_ArrowDown)
        arrow_rect = QRect(
            self.width() - 20,  0, 20,
            self.height())
        arrow_icon.paint(painter,
            arrow_rect,
            Qt.AlignCenter,
            QIcon.Normal,
            QIcon.Off)
        
        boxrect = event.rect()
        boxrect.setWidth(boxrect.width() - 22)
        
        painter.setPen(Qt.black)
        painter.fillRect(boxrect, Qt.white)
        painter.drawRect(boxrect)
        
        selected_text = self.currentText()
        if selected_text:
            selected_text_rect = QRect(14, 0,
                self.width() - 24,
                self.height())
            painter.drawText(
                selected_text_rect, Qt.AlignLeft | Qt.AlignVCenter,
                selected_text)

class myCustomScrollArea(QScrollArea):
    def __init__(self, name):
        super().__init__()
        
        self.name = name
        self.font = QFont(genv.v__app__font)
        self.font.setPointSize(10)
        
        self.type_label        = 1
        self.type_edit         = 2
        self.type_spin         = 3
        self.type_combo_box    = 4
        self.type_check_box    = 5
        self.type_push_button  = 6
        self.type_radio_button = 7
        
        font_primary   = genv.v__app__font_edit
        font_secondary = "Courier New"
        
        self.font_a = QFont(genv.v__app__font_edit); self.font_a.setPointSize(11)
        self.font_b = QFont(genv.v__app__font);      self.font_a.setPointSize(10)
        
        self.font_a.setFamily(font_primary)
        font_id = QFontDatabase.addApplicationFont(self.font_a.family())
        if font_id != -1:
            self.font_a.setFamily(font_primary)
            self.font_a.setPointSize(11)
        else:
            self.font_a.setFamily(font_secondary)
            self.font_a.setPointSize(11)
        
        self.supported_langs = _("supported_langs")
        
        self.content_widget = QWidget(self)
        self.content_widget.setMinimumHeight(self.height()-150)
        self.content_widget.setMinimumWidth (self.width()-50)
        self.content_widget.setFont(self.font)
        
        self.layout = QVBoxLayout(self.content_widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.label_1 = QLabel(self.name)
        
        self.layout.addWidget(self.label_1)
        self.content_widget.setLayout(self.layout)
        
        #self.setWidgetResizable(False)
        self.setWidget(self.content_widget)
    
    def setName(self, name):
        self.name = name
        self.label_1.setText(self.name)
    
    def setElementBold(self, w):
        self.font.setBold(True); w.setFont(self.font)
        self.font.setBold(False)
        
    def addPushButton(self, text, l = None):
        w = QPushButton(text)
        w.setFont(self.font_a)
        w.font().setPointSize(14)
        w.font().setBold(True)
        w.setMinimumWidth(32)
        w.setMinimumHeight(32)
        if not l == None:
            l.addWidget(w)
        else:
            self.layout.addWidget(w)
        return w
    
    def addCheckBox(self, text, bold=False):
        w = QCheckBox(text)
        if bold == True:
            self.setElementBold(w)
        else:
            w.setFont(self.font)
        self.layout.addWidget(w)
        return w
    
    def addRadioButton(self, text):
        w = QRadioButton(text)
        w.setFont(self.font)
        self.layout.addWidget(w)
        return w
    
    def addFrame(self, lh = None):
        w = QFrame()
        w.setFrameShape (QFrame.HLine)
        w.setFrameShadow(QFrame.Sunken)
        if not lh == None:
            lh.addWidget(w)
        else:
            self.layout.addWidget(w)
        return w
    
    def addHelpLabel(self, text, helpID, helpText, lh=None):
        w = myCustomLabel( text, helpID, helpText)
        if not lh == None:
            w.setFont(self.font_a)
            lh.addWidget(w)
        else:
            self.layout.addWidget(w)
        return w
    
    def addLabel(self, text, bold=False, lh=None):
        w = QLabel(text)
        if bold == True:
            self.setElementBold(w)
        else:
            w.setFont(self.font)
        if not lh == None:
            w.setFont(self.font_a)
            lh.addWidget(w)
        else:
            self.layout.addWidget(w)
        return w
    
    def addLineEdit(self, text = "", lh = None):
        w = myLineEdit(text)
        w.setMinimumHeight(21)
        w.setFont(self.font_a)
        if not lh == None:
            lh.addWidget(w)
        else:
            self.layout.addWidget(w)
        return w
    
    def addElements(self, elements, hid):
        for i in range(0, len(elements)):
            lv_0 = QVBoxLayout()
            lh_0 = QHBoxLayout()
            
            # -----------------------------------------
            # the help string for a doxygen tag ...
            # -----------------------------------------
            helpID   = hid + i + 1
            helpText = _("h" + f"{helpID:04X}")
            tokennum = _("A" + f"{helpID:04X}")
            
            vw_1 = self.addHelpLabel(   \
                tokennum,  \
                helpID,    \
                helpText,  \
                lh_0)
            vw_1.setMinimumHeight(14)
            vw_1.setMinimumWidth(200)
            
            if elements[i][1] == self.type_edit:
                self.addLineEdit("",lh_0)
                                    
                if elements[i][2] == 1:
                    self.addPushButton("+",lh_0)
                    
                elif elements[i][2] == 3:
                    self.addPushButton("+",lh_0)
                    self.addPushButton("-",lh_0)
                    self.addPushButton("R",lh_0)
                    
                    vw_3 = myTextEdit()
                    vw_3.setFont(self.font_a)
                    vw_3.setMinimumHeight(96)
                    vw_3.setMaximumHeight(96)
                    lv_0.addWidget(vw_3)
            
            elif elements[i][1] == self.type_check_box:
                vw_2 = QCheckBox()
                vw_2.setMinimumHeight(21)
                vw_2.setFont(self.font_a)
                vw_2.setChecked(elements[i][3])
                lh_0.addWidget(vw_2)
            
            elif elements[i][1] == self.type_combo_box:
                vw_2 = iconComboBox(self)
                vw_2.setMinimumHeight(26)
                vw_2.setFont(self.font)
                vw_2.font().setPointSize(14)
                lh_0.addWidget(vw_2)
                
                if elements[i][2] == 4:
                    data = json.loads(self.supported_langs)
                    elements[i][3] = data
                    for j in range(0, len(data)):
                        img = os.path.join(genv.v__app__img__int__, "flag_"  \
                        + elements[i][3][j]    \
                        + genv.v__app__img_ext__)
                        img = img.lower()
                        
                        vw_2.addItem(QIcon(img), elements[i][3][j-1])
                        #vw_2.setStyleSheet("""
                        #QComboBox QAbstractItemView {
                        #    selection-background-color: lightGray;
                        #    selection-color: black;
                        #    color: black;
                        #}
                        #""")
                
                elif elements[i][2] == 2:
                    for j in range(0, len(elements[i][3])):
                        vw_2.addItem(elements[i][3][j])
            
            elif elements[i][1] == self.type_spin:
                vw_2 = QSpinBox()
                vw_2.setFont(self.font_a)
                vw_2.setMinimumHeight(21)
                lh_0.addWidget(vw_2)
            
            lv_0.addLayout(lh_0)
            self.layout.addLayout(lv_0)

# ------------------------------------------------------------------------
# create a scroll view for the project tab on left side of application ...
# ------------------------------------------------------------------------
class customScrollView_1(myCustomScrollArea):
    def __init__(self, name="uuuu"):
        super().__init__(name)
        
        self.name = name
        self.init_ui()
    
    def init_ui(self):
        content_widget = QWidget(self)
        content_widget.setMaximumWidth(500)
        
        layout = QVBoxLayout(content_widget)
        layout.setAlignment(Qt.AlignLeft)
        
        font = QFont(genv.v__app__font)
        font.setPointSize(10)
        
        w_layout_0 = QHBoxLayout()
        w_layout_0.setAlignment(Qt.AlignLeft)
        widget_1_label_1 = self.addLabel("Provide some informations about the Project you are documenting", True)
        widget_1_label_1.setMinimumWidth(250)
        widget_1_label_1.setMaximumWidth(450)
        w_layout_0.addWidget(widget_1_label_1)
        layout.addLayout(w_layout_0)
        
        h_layout_1 = QHBoxLayout()
        h_widget_1 = QWidget()
        #h_widget_1.setMinimumWidth(300)
        
        v_layout_1 = QVBoxLayout()
        v_widget_1 = QWidget()
        
        l_label_1 = self.addLabel("Project name:"           , False, v_layout_1)
        l_label_2 = self.addLabel("Project author:"         , False, v_layout_1)
        l_label_3 = self.addLabel("Project version or id:  ", False, v_layout_1)
        
        l_label_1.setFont(font)
        l_label_2.setFont(font)
        l_label_3.setFont(font)
        ##
        v_layout_2 = QVBoxLayout()
        v_widget_2 = QWidget()
        
        e_field_1 = self.addLineEdit("", v_layout_2)
        e_field_2 = self.addLineEdit("", v_layout_2)
        e_field_3 = self.addLineEdit("", v_layout_2)
        
        ##
        h_layout_1.addLayout(v_layout_1)
        h_layout_1.addLayout(v_layout_2)
        
        layout.addLayout(h_layout_1)
        
        
        
        layout_4 = QHBoxLayout()
        layout_4.setAlignment(Qt.AlignLeft)
        widget_4_label_1 = self.addLabel("Project logo:", False, layout_4)
        widget_4_label_1.setFont(font)
        widget_4_label_1.setMaximumWidth(160)
        layout_4.addWidget(widget_4_label_1)
        #
        widget_4_pushb_1 = self.addPushButton("Select", layout_4)
        widget_4_pushb_1.setMinimumHeight(32)
        widget_4_pushb_1.setMinimumWidth(84)
        widget_4_pushb_1.setMaximumWidth(84)  ; font.setBold(True)
        widget_4_pushb_1.setFont(font)        ; font.setBold(False)
        #
        widget_4_licon_1 = self.addLabel("", False, layout_4)
        widget_4_licon_1.setPixmap(QIcon(
            os.path.join(genv.v__app__img__int__, "floppy-disk" + genv.v__app__img_ext__)).pixmap(42,42))
        #
        layout.addLayout(layout_4)
        
        layout_5 = QHBoxLayout()
        layout_5.setAlignment(Qt.AlignLeft)
        frame_5 = self.addFrame(layout_5)
        frame_5.setMinimumWidth(460)
        frame_5.setMaximumWidth(460)
        layout_5.addWidget(frame_5)
        #
        layout.addLayout(layout_5)
        
        
        layout_6 = QHBoxLayout()
        layout_6.setAlignment(Qt.AlignLeft)
        widget_6_label_1 = self.addLabel("Source dir:", False, layout_6)
        widget_6_label_1.setMinimumWidth(100)
        widget_6_label_1.setMaximumWidth(100)
        widget_6_label_1.setFont(font)
        #
        widget_6_edit_1  = self.addLineEdit("E:\\temp\\src", layout_6)
        widget_6_edit_1.setMinimumWidth(280)
        widget_6_edit_1.setMaximumWidth(280)
        widget_6_edit_1.setFont(font)
        #
        widget_6_pushb_1 = self.addPushButton("Select", layout_6)
        widget_6_pushb_1.setMinimumHeight(40)
        widget_6_pushb_1.setMaximumHeight(40)
        widget_6_pushb_1.setMinimumWidth(84)
        widget_6_pushb_1.setMaximumWidth(84) ; font.setBold(True)
        widget_6_pushb_1.setFont(font)       ; font.setBold(False)
        ##
        layout.addLayout(layout_6)
        
        layout_7 = QHBoxLayout()
        layout_7.setAlignment(Qt.AlignLeft)
        widget_7_label_1 = self.addLabel("Destination dir:", False, layout_7)
        widget_7_label_1.setMinimumWidth(100)
        widget_7_label_1.setMaximumWidth(100)
        widget_7_label_1.setFont(font)
        #
        widget_7_edit_1  = self.addLineEdit("E:\\temp\\src\\html", layout_7)
        widget_7_edit_1.setMinimumWidth(280)
        widget_7_edit_1.setMaximumWidth(280)
        widget_7_edit_1.setFont(font)
        #
        widget_7_pushb_1 = self.addPushButton("Select", layout_7)
        widget_7_pushb_1.setMinimumHeight(40)
        widget_7_pushb_1.setMaximumHeight(40)
        widget_7_pushb_1.setMinimumWidth(84)
        widget_7_pushb_1.setMaximumWidth(84) ; font.setBold(True)
        widget_7_pushb_1.setFont(font)       ; font.setBold(False)
        ##
        layout.addLayout(layout_7)
        
        
        layout_61 = QHBoxLayout()
        layout_61.setAlignment(Qt.AlignLeft)
        frame_61 = self.addFrame(layout_61)
        frame_61.setMinimumWidth(460)
        frame_61.setMaximumWidth(460)
        layout_61.addWidget(frame_61)
        #
        layout.addLayout(layout_61)
        
        
        layout_9 = QHBoxLayout()
        layout_9.setAlignment(Qt.AlignLeft)
        widget_9_checkbutton_1 = self.addCheckBox("Scan recursive")
        widget_9_checkbutton_1.setMaximumWidth(300)
        widget_9_checkbutton_1.setFont(font)
        layout_9.addWidget(widget_9_checkbutton_1)
        layout.addLayout(layout_9)
        
        layout_10 = QVBoxLayout()
        widget_10_button_1 = QPushButton("Convert" ,self); widget_10_button_1.setStyleSheet(css_button_style)
        widget_10_button_2 = QPushButton("HelpNDoc",self); widget_10_button_2.setStyleSheet(css_button_style)
        #
        layout_10.addWidget(widget_10_button_1)
        layout_10.addWidget(widget_10_button_2)
        #
        layout.addLayout(layout_10)
        
        #self.setWidgetResizable(False)
        self.setWidget(content_widget)
    
    def btn_clicked_3(self):
        print("HelpNDoc")

class customScrollView_2(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        
        label_2 = self.addLabel(_("opti00"), True)
        label_2.setMinimumHeight(30)
        label_2.setMinimumWidth(200)
        
        self.addRadioButton(_("opti01"))
        self.addRadioButton(_("opti02"))
        self.addCheckBox   (_("opti03"))
        
        self.addFrame()
        
        self.addLabel("Select programming language to optimize the results for:", True)
        
        for x in range(2,9):
            self.addRadioButton(_("opti0" + str(x+1)))

# ------------------------------------------------------------------------
# create a scroll view for the output tab on left side of application ...
# ------------------------------------------------------------------------
class customScrollView_3(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        
        self.addLabel("Select the output format(s) to generate:", True)
        
        # HTML
        self.addCheckBox("HTML", True)
        #
        self.addRadioButton("plain HTML")
        self.addRadioButton("with navigation Panel")
        self.addRadioButton("prepare for compressed HTML .chm")
        self.addCheckBox("with search function")
        
        self.addFrame()
        
        # LaTeX
        self.addCheckBox("LaTeX", True)
        #
        self.addRadioButton("an intermediate format for hypter-linked PDF")
        self.addRadioButton("an intermediate format for PDF")
        self.addRadioButton("an intermediate format for PostScript")
        
        self.addFrame()
        
        # misc
        self.addCheckBox("Man pages")
        self.addCheckBox("Rich Text Format - RTF")
        self.addCheckBox("XML")
        self.addCheckBox("DocBook")

# ------------------------------------------------------------------------
# create a scroll view for the diagrams tab on left side of application ...
# ------------------------------------------------------------------------
class customScrollView_4(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        
        self.addLabel("Diagrams to generate:", True)
        
        self.addRadioButton("No diagrams")
        self.addRadioButton("Text only")
        self.addRadioButton("Use built-in diagram generator")
        self.addRadioButton("Use Dot-Tool from the GrappVz package")
        
        self.addFrame()
        
        self.addLabel("Dot graphs to generate:", True)
        
        self.addCheckBox("Class graph")
        self.addCheckBox("Colaboration diagram")
        self.addCheckBox("Overall Class hiearchy")
        self.addCheckBox("Include dependcy graphs")
        self.addCheckBox("Included by dependcy graphs")
        self.addCheckBox("Call graphs")
        self.addCheckBox("Called-by graphs")

class customScrollView_5(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(2000)
        
        ## 0xA0100
        label_1_elements = [
            # <text>,                  <type 1>,             <help>, <type 2>,  <list 1>
            [0xA0101, self.type_edit,       0],
            
            [0xA0102, self.type_edit,       0, "My Project"],
            [0xA0103, self.type_edit,       0],
            [0xA0104, self.type_edit,       0],
            [0xA0105, self.type_edit,       1],
            [0xA0106, self.type_edit,       1],
            
            [0xA0107, self.type_edit,       1],
            [0xA0108, self.type_check_box,  0, True],
            [0xA0109, self.type_spin,       0],
            
            [0xA010A, self.type_check_box,  0, False],
            [0xA010B, self.type_combo_box,  4, [] ],
            
            [0xA010C, self.type_check_box,   0, True],
            [0xA010D, self.type_check_box,   0, True],
            [0xA010E, self.type_edit,       3],
            [0xA010F, self.type_check_box,   0, True],
            [0xA0110, self.type_check_box,   0, True],
            
            [0xA0111, self.type_check_box,   0, True],
            [0xA0112, self.type_edit,        3],
            [0xA0113, self.type_edit,        3],
            
            [0xA0114, self.type_check_box,   0, False],
            
            [0xA0115, self.type_check_box,   0, True ],
            [0xA0116, self.type_check_box,   0, False],
            
            [0xA0117, self.type_check_box,   0, False],
            
            [0xA0118, self.type_check_box,   0, False],
            [0xA0119, self.type_check_box,   0, True ],
            [0xA011A, self.type_check_box,   0, True ],
            [0xA011B, self.type_check_box,   0, False],
            
            [0xA011C, self.type_spin,        0],
            [0xA011D, self.type_edit,        3],
            
            [0xA011E, self.type_check_box,   0, True ],
            [0xA011F, self.type_check_box,   0, False],
            [0xA0120, self.type_check_box,   0, False],
            [0xA0121, self.type_check_box,   0, False],
            [0xA0122, self.type_check_box,   0, False],
            
            [0xA0123, self.type_edit,        3],
            
            [0xA0124, self.type_check_box,   0, True ],
            [0xA0125, self.type_spin,        0],
            [0xA0126, self.type_combo_box,   2, ["DOXYGEN", "CIT"]],
            [0xA0127, self.type_check_box,   0, True ],
            
            [0xA0128, self.type_check_box,   0, True ],
            [0xA0129, self.type_check_box,   0, True ],
            [0xA012A, self.type_check_box,   0, False],
            [0xA012B, self.type_check_box,   0, True ],
            
            [0xA012C, self.type_check_box,   0, False],
            [0xA012D, self.type_check_box,   0, False],
            [0xA012E, self.type_check_box,   0, True ],
            
            [0xA012F, self.type_check_box,   0, False],
            [0xA0130, self.type_check_box,   0, False],
            [0xA0131, self.type_check_box,   0, False],
            
            [0xA0132, self.type_spin,        0],
            [0xA0133, self.type_spin,        0],
            
            [0xA0134, self.type_combo_box,   2, ["NO","YES"]]
        ]
        self.addElements(label_1_elements, 0x100)
    
    # ----------------------------------------------
    # show help text when mouse move over the label
    # ----------------------------------------------
    def label_enter_event(self, text):
        sv_help.setText(text)

class customScrollView_6(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1400)
        
        ## 0xA0200
        label_1_elements = [
            [0xA0201, self.type_check_box, 0, False ],
            [0xA0202, self.type_check_box, 0, False ],
            [0xA0203, self.type_check_box, 0, False ],
            [0xA0204, self.type_check_box, 0, False ],
            [0xA0205, self.type_check_box, 0, True  ],
            [0xA0206, self.type_check_box, 0, True  ],
            [0xA0207, self.type_check_box, 0, True  ],
            [0xA0208, self.type_check_box, 0, True  ],
            [0xA0209, self.type_check_box, 0, True  ],
            [0xA020A, self.type_check_box, 0, False ],
            [0xA020B, self.type_check_box, 0, False ],
            [0xA020C, self.type_check_box, 0, False ],
            [0xA020D, self.type_check_box, 0, False ],
            [0xA020E, self.type_check_box, 0, True  ],
            
            [0xA020F, self.type_combo_box, 2, ["SYSTEM", "NO", "YES"] ],
            
            [0xA0210, self.type_check_box, 0, False ],
            [0xA0211, self.type_check_box, 0, False ],
            
            [0xA0212, self.type_check_box, 0, True  ],
            [0xA0213, self.type_check_box, 0, True  ],
            
            [0xA0214, self.type_check_box, 0, False ],
            [0xA0215, self.type_check_box, 0, False ],
            [0xA0216, self.type_check_box, 0, False ],
            [0xA0217, self.type_check_box, 0, False ],
            [0xA0218, self.type_check_box, 0, False ],
            [0xA0219, self.type_check_box, 0, False ],
            
            [0xA021A, self.type_check_box, 0, False ],
            [0xA021B, self.type_check_box, 0, False ],
            [0xA021C, self.type_check_box, 0, False ],
            
            [0xA021D, self.type_check_box, 0, False ],
            [0xA021E, self.type_check_box, 0, False ],
            [0xA021F, self.type_check_box, 0, False ],
            [0xA0220, self.type_check_box, 0, False ],
            
            [0xA0221, self.type_edit,      3 ],
            [0xA0222, self.type_spin,      0 ],
            
            [0xA0223, self.type_check_box, 0, True  ],
            [0xA0224, self.type_check_box, 0, True  ],
            [0xA0225, self.type_check_box, 0, True  ],
            
            [0xA0226, self.type_edit,      1 ],
            [0xA0227, self.type_edit,      1 ],
            [0xA0228, self.type_edit,      3 ]
        ]
        self.addElements(label_1_elements, 0x200)

class customScrollView_7(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA0300
        label_1_elements = [
            [0xA0301, self.type_check_box, 0, True  ],
            [0xA0302, self.type_check_box, 0, True  ],
            
            [0xA0303, self.type_check_box, 0, False ],
            [0xA0304, self.type_check_box, 0, True  ],
            [0xA0305, self.type_check_box, 0, True  ],
            
            [0xA0306, self.type_check_box, 0, False ],
            [0xA0307, self.type_check_box, 0, False ],
            
            [0xA0308, self.type_spin,      0 ],
            
            [0xA0309, self.type_edit,      0 ],
            [0xA030A, self.type_edit,      0 ],
            [0xA030B, self.type_edit,      1 ]
        ]
        self.addElements(label_1_elements, 0x0300)

class customScrollView_8(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1700)
        
        ## 0xA0400
        label_1_elements = [
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      0],
            [0xA0401, self.type_edit,      1],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_check_box, 0, True  ],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_check_box, 0, False ],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      0, False ],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      1],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_check_box, 0, False ],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      0],
            [0xA0401, self.type_spin,      0]
        ]
        self.addElements(label_1_elements, 0x0400)

class customScrollView_9(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(560)
        
        ## 0xA0500
        label_1_elements = [
            [0xA0501, self.type_check_box, 0, True  ],
            [0xA0502, self.type_check_box, 0, False ],
            [0xA0503, self.type_check_box, 0, False ],
            
            [0xA0504, self.type_check_box, 0, True  ],
            [0xA0505, self.type_check_box, 0, True  ],
            [0xA0506, self.type_check_box, 0, True  ],
            
            [0xA0507, self.type_check_box, 0, True  ],
            [0xA0508, self.type_check_box, 0, False ],
            [0xA0509, self.type_check_box, 0, True  ],
            
            [0xA050A, self.type_check_box, 0, False ],
            [0xA050B, self.type_check_box, 0, False ],
            [0xA050C, self.type_edit     , 3 ],
            [0xA050D, self.type_edit     , 1 ]
        ]
        self.addElements(label_1_elements, 0x0500)

class customScrollView_10(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA0600
        label_1_elements = [
            [0xA0601, self.type_check_box, 0, True ],
            [0xA0602, self.type_edit,      3 ]
        ]
        self.addElements(label_1_elements, 0x0600)

class customScrollView_11(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(2380)
        
        ## 0xA0700
        label_1_elements = [
            [0xA0701, self.type_check_box, 0, True  ],
            [0xA0702, self.type_edit,      1 ],
            [0xA0703, self.type_edit,      0 ],
            
            [0xA0704, self.type_edit,      1 ],
            [0xA0705, self.type_edit,      1 ],
            
            [0xA0706, self.type_edit,      1 ],
            [0xA0707, self.type_edit,      3 ],
            [0xA0708, self.type_edit,      3 ],
            
            [0xA0709, self.type_combo_box, 2, [ "LIGHT", "DARK", "AUTO_LIGHT", "AUTO_DARK", "TOOGLE" ] ],
            [0xA070A, self.type_spin,      0 ],
            [0xA070B, self.type_spin,      0 ],
            [0xA070C, self.type_spin,      0 ],
            [0xA070D, self.type_check_box, 0, True  ],
            [0xA070E, self.type_check_box, 0, False ],
            
            [0xA070F, self.type_check_box, 0, True  ],
            [0xA0710, self.type_check_box, 0, True  ],
            [0xA0711, self.type_edit,      0 ],
            [0xA0712, self.type_spin,      0 ],
            
            [0xA0713, self.type_check_box, 0, False ],
            [0xA0714, self.type_edit,      0 ],
            [0xA0715, self.type_edit,      0 ],
            [0xA0716, self.type_edit,      0 ],
            [0xA0717, self.type_edit,      0 ],
            [0xA0718, self.type_edit,      0 ],
            
            [0xA0719, self.type_check_box, 0, True  ],
            [0xA071A, self.type_edit,      1 ],
            [0xA071B, self.type_edit,      1 ],
            [0xA071C, self.type_check_box, 0, False ],
            [0xA071D, self.type_edit,      0 ],
            [0xA071E, self.type_check_box, 0, False ],
            [0xA071F, self.type_check_box, 0, False ],
            [0xA0720, self.type_edit,      0 ],
            
            [0xA0721, self.type_check_box, 0, False ],
            [0xA0722, self.type_edit,      1 ],
            [0xA0723, self.type_edit,      0 ],
            [0xA0724, self.type_edit,      0 ],
            [0xA0725, self.type_edit,      0 ],
            [0xA0726, self.type_edit,      0 ],
            [0xA0727, self.type_edit,      1 ],
            
            [0xA0728, self.type_check_box, 0, False ],
            [0xA0729, self.type_edit,      0 ],
            [0xA072A, self.type_check_box, 0, False ],
            
            [0xA072B, self.type_check_box, 0, True  ],
            [0xA072C, self.type_check_box, 0, False ],
            
            [0xA072D, self.type_spin,      0 ],
            [0xA072E, self.type_spin,      0 ],
            
            [0xA072F, self.type_check_box, 0, False ],
            [0xA0730, self.type_check_box, 0, True  ],
            
            [0xA0731, self.type_combo_box, 2, [ "png", "svg" ] ],
            [0xA0732, self.type_spin,      0 ],
            [0xA0733, self.type_edit,      1 ],
            
            [0xA0734, self.type_check_box, 0, False ],
            [0xA0735, self.type_combo_box, 2, [ "MathJax_2", "MathJax_3" ] ],
            [0xA0736, self.type_combo_box, 2, [ "HTML + CSS", "NativeXML", "chtml", "SVG" ] ],
            
            [0xA0737, self.type_edit,      1 ],
            [0xA0738, self.type_edit,      3 ],
            [0xA0739, self.type_edit,      0 ],
            
            [0xA073A, self.type_check_box, 0, False ],
            [0xA073B, self.type_check_box, 0, False ],
            [0xA073C, self.type_check_box, 0, False ],
            [0xA073D, self.type_edit,      0 ],
            [0xA073E, self.type_edit,      1 ],
            [0xA073F, self.type_edit,      0 ],
            [0xA0740, self.type_edit,      3 ]
        ]
        self.addElements(label_1_elements, 0x0700)

class customScrollView_12(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1000)
        
        ## 0xA0800
        label_1_elements = [
            [0xA0801, self.type_check_box, 0, False ],
            [0xA0802, self.type_edit,      1 ],
            [0xA0803, self.type_edit,      1 ],
            [0xA0804, self.type_edit,      0 ],
            [0xA0805, self.type_check_box, 0, False ],
            [0xA0806, self.type_combo_box, 2, [ "a4", "letter", "executive" ] ],
            [0xA0807, self.type_edit,      3 ],
            [0xA0808, self.type_edit,      1 ],
            [0xA0809, self.type_edit,      1 ],
            [0xA080A, self.type_edit,      3 ],
            [0xA080B, self.type_edit,      3 ],
            [0xA080C, self.type_check_box, 0, True  ],
            [0xA080D, self.type_check_box, 0, True  ],
            [0xA080E, self.type_combo_box, 2, [ "NO", "YWS", "BATCH", "NON-STOP", "SCROLL", "ERROR_STOP" ] ],
            [0xA080F, self.type_check_box, 0, False ],
            [0xA0810, self.type_edit,      0 ],
            [0xA0811, self.type_edit,      1 ]
        ]
        self.addElements(label_1_elements, 0x0800)

class customScrollView_13(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA0900
        label_1_elements = [
            [0xA0901, self.type_check_box, 0, False ],
            [0xA0902, self.type_edit,      1 ],
            [0xA0903, self.type_check_box, 0, False ],
            [0xA0904, self.type_check_box, 0, False ],
            [0xA0905, self.type_edit,      1 ],
            [0xA0906, self.type_edit,      1 ]
        ]
        self.addElements(label_1_elements, 0x0900)

class customScrollView_14(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1000
        label_1_elements = [
            [0xA1001, self.type_check_box, 0, False ],
            [0xA1002, self.type_edit,      1 ],
            [0xA1003, self.type_edit,      0 ],
            [0xA1004, self.type_edit,      0 ],
            [0xA1005, self.type_check_box, 0, False ],
        ]
        self.addElements(label_1_elements, 0x1000)

class customScrollView_15(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1100
        label_1_elements = [
            [0xA1101, self.type_check_box, 0, False ],
            [0xA1102, self.type_edit,      1 ],
            [0xA1103, self.type_check_box, 0, False ],
            [0xA1104, self.type_check_box, 0, False ]
        ]
        self.addElements(label_1_elements, 0x1100)

class customScrollView_16(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1400)
        
        ## 0xA1200
        label_1_elements = [
            [0xA1201, self.type_check_box, 0, False ],
            [0xA1202, self.type_edit,      1 ],
        ]
        self.addElements(label_1_elements, 0x1200)

class customScrollView_17(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1300
        label_1_elements = [
            [0xA1301,  self.type_check_box, 0, False ]
        ]
        self.addElements(label_1_elements, 0x1300)

class customScrollView_18(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1400
        label_1_elements = [
            [0xA1401, self.type_check_box, 0, False ],
            [0xA1402, self.type_edit,      1 ],
            [0xA1403, self.type_check_box, 0, True  ],
        ]
        self.addElements(label_1_elements, 0x1400)

class customScrollView_19(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1500
        label_1_elements = [
            [0xA1501, self.type_check_box, 0, False ],
            [0xA1502, self.type_check_box, 0, False ],
            [0xA1503, self.type_check_box, 0, False ],
            [0xA1504, self.type_edit,      1 ]
        ]
        self.addElements(label_1_elements, 0x1500)

class customScrollView_20(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(800)
        
        ## 0xA1600
        label_1_elements = [
            [0xA1601, self.type_check_box, 0, True  ],
            [0xA1602, self.type_check_box, 0, True  ],
            [0xA1603, self.type_check_box, 0, False ],
            [0xA1604, self.type_check_box, 0, False ],
            [0xA1605, self.type_edit,      3 ],
            [0xA1606, self.type_edit,      3 ],
            [0xA1607, self.type_edit,      3 ],
            [0xA1608, self.type_edit,      3 ],
            [0xA1609, self.type_check_box, 0, True  ]
        ]
        self.addElements(label_1_elements, 0x1600)

class customScrollView_21(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1700
        label_1_elements = [
            [0xA1701, self.type_edit,  3 ],
            [0xA1702, self.type_edit,  1 ],
            [0xA1703, self.type_check_box, 0, False ],
            [0xA1704, self.type_check_box, 0, True  ],
            [0xA1705, self.type_check_box, 0, True  ]
        ]
        self.addElements(label_1_elements, 0x1700)

class customScrollView_22(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1800)
        
        ## 0xA1800
        label_1_elements = [
            [0xA1801, self.type_check_box, 0, False ],
            [0xA1802, self.type_check_box, 0, False ],
            [0xA1803, self.type_spin     , 0 ],
            
            [0xA1804, self.type_edit, 0 ],
            [0xA1805, self.type_edit, 0 ],
            [0xA1806, self.type_edit, 0 ],
            [0xA1807, self.type_edit, 1 ],
            
            [0xA1808, self.type_combo_box, 2, [ "YES", "NO" ] ],
            [0xA1809, self.type_check_box, 0, True  ],
            [0xA180A, self.type_check_box, 0, True  ],
            [0xA180B, self.type_check_box, 0, False ],
            [0xA180C, self.type_spin     , 0 ],
            [0xA180D, self.type_combo_box, 2, [ "NO", "YES" ] ],
            [0xA180E, self.type_spin     , 0 ],
            
            [0xA180F, self.type_check_box, 0, False ],
            [0xA1810, self.type_check_box, 0, False ],
            [0xA1811, self.type_check_box, 0, False ],
            [0xA1812, self.type_check_box, 0, False ],
            [0xA1813, self.type_check_box, 0, False ],
            [0xA1814, self.type_check_box, 0, False ],
            [0xA1815, self.type_check_box, 0, False ],
            
            [0xA1816, self.type_spin     , 0 ],
            [0xA1817, self.type_combo_box, 2, [ "png", "svg" ] ],
            
            [0xA1818, self.type_check_box, 0, False ],
            
            [0xA1819, self.type_edit     , 1 ],
            [0xA181A, self.type_edit     , 3 ],
            
            [0xA181B, self.type_edit     , 1 ],
            [0xA181C, self.type_edit     , 3 ],
            
            [0xA181D, self.type_edit     , 1 ],
            [0xA181E, self.type_edit     , 1 ],
            [0xA181F, self.type_edit     , 3 ],
            
            [0xA1820, self.type_spin     , 0 ],
            [0xA1821, self.type_spin     , 0 ],
            
            [0xA1822, self.type_check_box, 0, False ],
            [0xA1823, self.type_check_box, 0, False ],
            [0xA1824, self.type_check_box, 0, True  ],
            [0xA1825, self.type_edit     , 1 ],
            [0xA1826, self.type_edit     , 3 ]
        ]
        self.addElements(label_1_elements, 0x1800)

class customScrollView_help(QTextEdit):
    def __init__(self):
        super().__init__()
        
        font = QFont(genv.v__app__font)
        font.setPointSize(11)
        
        self.setFont(font)
        self.setMinimumHeight(100)
        self.setMaximumHeight(100)

class CustomModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_item = None
    
    def index(self, row, column, parent):
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        
        if parent_item is None or row < 0 or column < 0 or row >= len(parent_item[1]):
            return QModelIndex()
        
        return self.createIndex(row, column, parent_item[1][row])
    
    def parent(self, index):
        # Hier wird der Elternindex des Elements zurückgegeben
        pass
    
    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return 1  # Anzahl der Hauptknoten
        item = parent.internalPointer()
        if item:
            return len(item[1])  # Anzahl der Unterknoten
        return 0
    
    def columnCount(self, parent=QModelIndex()):
        # Hier wird die Anzahl der Spalten unter einem gegebenen Index zurückgegeben
        return 1
    
    def data(self, index, role):
        # Hier werden Daten für das gegebene Indexelement und Rolle zurückgegeben
        pass

class ComboBoxDelegateStatus(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        # Add items to the combobox
        editor.addItem(QIcon(os.path.join(genv.v__app__img__int__, "icon_white"  + genv.v__app__img_ext__)), "Complete"     )
        editor.addItem(QIcon(os.path.join(genv.v__app__img__int__, "icon_blue"   + genv.v__app__img_ext__)), "Needs Review" )
        editor.addItem(QIcon(os.path.join(genv.v__app__img__int__, "icon_yellow" + genv.v__app__img_ext__)), "In Progress"  )
        editor.addItem(QIcon(os.path.join(genv.v__app__img__int__, "icon_red"    + genv.v__app__img_ext__)), "Out of Date"  )
        
        #editor.activated.connect(self.on_activated)
        if not genv.currentTextChanged_connected:
            genv.currentTextChanged_connected  = True
            genv.currentIndexChanged_connected = True
            #
            editor.currentTextChanged.connect(self.on_current_text_changed)
            editor.currentIndexChanged.connect(self.on_current_index_changed)
        return editor
    
    # index is text/string
    def on_current_index_changed(self, index):
        if type(index) == str:
            index = index.strip()
            if index == "Complete":
                return
            elif index == "Needs Review":
                return
            elif index == "In Progress":
                return
            elif index == "Out of Date":
                return
        return
    
    # index is number
    def on_current_text_changed(self, index):
        self.on_current_index_changed(index)
        return
    
    # index is number
    def on_activated(self, index):
        self.on_current_index_changed(index)
        return

class ComboBoxDelegateIcon(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        # Add items to the combobox
        editor.addItem("Option 1")
        editor.addItem("Option 2")
        editor.addItem("Option 3")
        return editor

class CheckableComboBox(QComboBox):
    def __init__(self, parent):
        super(CheckableComboBox, self).__init__(parent)
        if not genv.view_pressed_connected:
            genv.view_pressed_connected = True
            self.view().pressed.connect(self.handleItemPressed)
            self.setModel(QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

class ComboBoxDelegateBuild(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = CheckableComboBox(parent); i = 1
        i = 1
        ico_yellow = "icon_yellow" + genv.v__app__img_ext__
        
        liste = ["CHM", "HTML", "Word", "PDF", "EPub", "Kindle", "Qt Help", "MarkDown"]
        for item in liste:
            editor.addItem(QIcon(os.path.join(genv.v__app__img__int__, ico_yellow )), item + " " + str(i))
            it1 = editor.model().item(i-1, 0)
            it1.setCheckState(Qt.Unchecked)
            i = i + 1
        return editor

class SpinEditDelegateID(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        self.topic_counter = topic_counter
        editor.setValue(self.topic_counter)
        self.topic_counter = self.topic_counter + 1
        return editor

class CustomItem(QStandardItem):
    def __init__(self, text, icon):
        super().__init__(text)
        self.icon = icon
    
    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        
        icon_rect = option.rect.adjusted(4, 4, 20, -4)
        painter.drawPixmap(icon_rect, self.icon.pixmap(16, 16))

class MyItemRecord:
    def __init__(self, item_attr1, item_attr2):
        self.record_array = []
        
        self.attr1 = item_attr1
        self.attr2 = item_attr2
        
        self.add(self.attr1, self.attr2)
        return
    
    def add(self, item_attr1, item_attr2):
        self.record_array.insert(item_attr1, item_attr2)
        return

class doxygenImageTracker(QWidget):
    def __init__(self, parent=None):
        super(doxygenImageTracker, self).__init__(parent)
        
        self.img_origin_doxygen_label = QLabel(self)
        self.img_origin_doxygen_label.setObjectName("doxygen-image")
        self.img_origin_doxygen_label.move(30,10)
        self.img_origin_doxygen_label.setMinimumHeight(70)
        self.img_origin_doxygen_label.setMinimumWidth(238)
        
        self.bordercolor = "lightgray"
        self.parent      = parent
        self.state       = 0
        self.set_style()
    
    def set_style(self):
        style = _("doxtrack_css") \
        .replace("{1i}",genv.v__app__doxygen__ + str(1) + genv.v__app__img_ext__) \
        .replace("{1b}",self.bordercolor ) \
        .replace("{2i}",genv.v__app__doxygen__ + str(2) + genv.v__app__img_ext__) \
        .replace("{2b}",self.bordercolor )
        
        self.img_origin_doxygen_label.setStyleSheet(style.replace("\\","/"))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if img_hlpndoc.state == 2:
                img_hlpndoc.bordercolor = "lightgray"
                img_hlpndoc.state = 0
                img_hlpndoc.set_style()
            
            if self.state == 0:
                self.state = 2
                self.bordercolor = "lime";
                self.set_style()
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
            print("doxygen")
    
    def enterEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "gray";
            self.set_style()
        self.img_origin_doxygen_label.setCursor(QCursor(Qt.PointingHandCursor))
    
    def leaveEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "lightgray";
            self.set_style()
        self.img_origin_doxygen_label.setCursor(QCursor(Qt.ArrowCursor))

class helpNDocImageTracker(QWidget):
    def __init__(self, parent=None):
        super(helpNDocImageTracker, self).__init__(parent)
        
        self.img_origin_hlpndoc_label = QLabel(self)
        self.img_origin_hlpndoc_label.setObjectName("hlpndoc-image")
        self.img_origin_hlpndoc_label.move(32,24)
        self.img_origin_hlpndoc_label.setMinimumHeight(70)
        self.img_origin_hlpndoc_label.setMinimumWidth(230)
        
        self.bordercolor = "lightgray"
        self.parent      = parent
        self.state       = 0
        self.set_style()
    
    def set_style(self):
        txt1 = genv.v__app__hlpndoc__ + str(1) + genv.v__app__img_ext__
        txt2 = genv.v__app__hlpndoc__ + str(2) + genv.v__app__img_ext__
        
        style = _("doxtrack_css") \
        .replace("{1i}",txt1).replace("{1b}",self.bordercolor ) \
        .replace("{2i}",txt2).replace("{2b}",self.bordercolor )
        
        self.img_origin_hlpndoc_label.setStyleSheet(style.replace("\\","/"))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if img_doxygen.state == 2:
                img_doxygen.bordercolor = "lightgray"
                img_doxygen.state = 0
                img_doxygen.set_style()
            
            if self.state == 0:
                self.state = 2
                self.bordercolor = "lime";
                self.set_style()
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
            print("helpNDoc")
    
    def enterEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "gray";
            self.set_style()
        self.img_origin_hlpndoc_label.setCursor(QCursor(Qt.PointingHandCursor))
    
    def leaveEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "lightgray";
            self.set_style()
        self.img_origin_hlpndoc_label.setCursor(QCursor(Qt.ArrowCursor))

class ccpplusImageTracker(QWidget):
    def __init__(self, parent=None):
        super(ccpplusImageTracker, self).__init__(parent)
        
        #self.setMinimumHeight(120)
        #self.setMinimumWidth(120)
        self.img_origin_ccpplus_label = QLabel(self)
        self.img_origin_ccpplus_label.setObjectName("ccpplus-image")
        self.img_origin_ccpplus_label.move(15,0)
        self.img_origin_ccpplus_label.setMinimumHeight(107)
        self.img_origin_ccpplus_label.setMinimumWidth(104)
        
        self.bordercolor = "lightgray"
        self.parent      = parent
        self.state       = 0
        self.set_style()
    
    def set_style(self):
        style = _("doxtrack_css") \
        .replace("{1i}", genv.v__app__cpp1dev__ + str(1) + genv.v__app__img_ext__).replace("{1b}", self.bordercolor ) \
        .replace("{2i}", genv.v__app__cpp1dev__ + str(2) + genv.v__app__img_ext__).replace("{2b}", self.bordercolor )
        
        self.img_origin_ccpplus_label.setStyleSheet(style.replace("\\","/"))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if img_javadoc.state == 2:
                img_javadoc.bordercolor = "lightgray"
                img_javadoc.set_style()
                img_javadoc.state = 0
            #
            if img_freepas.state == 2:
                img_freepas.bordercolor = "lightgray"
                img_freepas.set_style()
                img_freepas.state = 0
            
            if self.state == 0:
                self.state = 2
                self.bordercolor = "lime";
                self.set_style()
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
            print("javadoc")
    
    def enterEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "gray";
            self.set_style()
        self.img_origin_ccpplus_label.setCursor(QCursor(Qt.PointingHandCursor))
    
    def leaveEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "lightgray";
            self.set_style()
        self.img_origin_ccpplus_label.setCursor(QCursor(Qt.ArrowCursor))

class javadocImageTracker(QWidget):
    def __init__(self, parent=None):
        super(javadocImageTracker, self).__init__(parent)
        
        self.img_origin_javadoc_label = QLabel(self)
        self.img_origin_javadoc_label.setObjectName("javadoc-image")
        self.img_origin_javadoc_label.move(14,0)
        self.img_origin_javadoc_label.setMinimumHeight(107)
        self.img_origin_javadoc_label.setMinimumWidth(104)
        
        self.bordercolor = "lightgray";
        self.parent      = parent
        self.state       = 0
        
        self.set_style()
        
    def set_style(self):
        style = _("doxtrack_css") \
        .replace("{1i}",genv.v__app__javadoc__ + str(1) + genv.v__app__img_ext__) \
        .replace("{1b}",self.bordercolor ) \
        .replace("{2i}",genv.v__app__javadoc__ + str(2) + genv.v__app__img_ext__) \
        .replace("{2b}",self.bordercolor )
        
        self.img_origin_javadoc_label.setStyleSheet(style.replace("\\","/"))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if img_ccpplus.state == 2:
                img_ccpplus.bordercolor = "lightgray"
                img_ccpplus.set_style()
                img_ccpplus.state = 0
            #
            if img_freepas.state == 2:
                img_freepas.bordercolor = "lightgray"
                img_freepas.set_style()
                img_freepas.state = 0
            
            if self.state == 0:
                self.state = 2
                self.bordercolor = "lime";
                self.set_style()
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
            print("javadoc")
    
    def enterEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "gray";
            self.set_style()
        self.img_origin_javadoc_label.setCursor(QCursor(Qt.PointingHandCursor))
    
    def leaveEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "lightgray";
            self.set_style()
        self.img_origin_javadoc_label.setCursor(QCursor(Qt.ArrowCursor))

class freepasImageTracker(QWidget):
    def __init__(self, parent=None):
        super(freepasImageTracker, self).__init__(parent)
        
        self.bordercolor = "lightgray"
        self.parent      = parent
        self.state       = 0
        
        self.img_origin_freepas_label = QLabel(self)
        self.img_origin_freepas_label.setObjectName("freepas-image")
        self.img_origin_freepas_label.move(30,10)
        self.img_origin_freepas_label.setMinimumHeight(70)
        self.img_origin_freepas_label.setMinimumWidth(218)
        
        self.set_style()
        
    def set_style(self):
        style = _("doxtrack_css") \
        .replace("{1i}",genv.v__app__freepas__ + str(1) + genv.v__app__img_ext__) \
        .replace("{1b}",self.bordercolor ) \
        .replace("{2i}",genv.v__app__freepas__ + str(2) + genv.v__app__img_ext__) \
        .replace("{2b}",self.bordercolor )
        
        self.img_origin_freepas_label.setStyleSheet(style.replace("\\","/"))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if img_javadoc.state == 2:
                img_javadoc.bordercolor = "lightgray"
                img_javadoc.set_style()
                img_javadoc.state = 0
            #
            if img_ccpplus.state == 2:
                img_ccpplus.bordercolor = "lightgray"
                img_ccpplus.set_style()
                img_ccpplus.state = 0
                
            if self.state == 0:
                self.state = 2
                self.bordercolor = "lime";
                self.set_style()
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
            print("freepas")
    
    def enterEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "gray";
            self.set_style()
        self.img_origin_freepas_label.setCursor(QCursor(Qt.PointingHandCursor))
    
    def leaveEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "lightgray";
            self.set_style()
        self.img_origin_freepas_label.setCursor(QCursor(Qt.ArrowCursor))

class MyPushButton(QLabel):
    def __init__(self, parent, mode):
        super().__init__("")
        self.setMaximumWidth(110)
        self.setMinimumWidth(110)
        self.setMinimumHeight(34)
        
        if mode == 1:
            self.btn_img_fg = os.path.join(genv.v__app__img__int__, "create1" + genv.v__app__img_ext__)
            self.btn_img_bg = os.path.join(genv.v__app__img__int__, "create2" + genv.v__app__img_ext__)
        elif mode == 2:
            self.btn_img_fg = os.path.join(genv.v__app__img__int__, "open1"   + genv.v__app__img_ext__)
            self.btn_img_bg = os.path.join(genv.v__app__img__int__, "open2"   + genv.v__app__img_ext__)
        elif mode == 3:
            self.btn_img_fg = os.path.join(genv.v__app__img__int__, "repro1"  + genv.v__app__img_ext__)
            self.btn_img_bg = os.path.join(genv.v__app__img__int__, "repro2"  + genv.v__app__img_ext__)
        elif mode == 4:
            self.btn_img_fg = os.path.join(genv.v__app__img__int__, "build1"  + genv.v__app__img_ext__)
            self.btn_img_bg = os.path.join(genv.v__app__img__int__, "build2"  + genv.v__app__img_ext__)
        
        fg = self.btn_img_fg.replace("\\","/")
        bg = self.btn_img_bg.replace("\\","/")
        
        style = _("push_css") \
        .replace("{fg}",fg)   \
        .replace("{bg}",bg)
        
        self.setStyleSheet(style)

class MyEllipseButton(QPushButton):
    def __init__(self, font):
        super().__init__("...")
        self.setFont(font)
        self.setMinimumHeight(36)
        self.setMinimumWidth (36)
        self.setMaximumWidth (36)

class myExitDialog(QDialog):
    def __init__(self, title, parent=None):
        super(myExitDialog, self).__init__(parent)
        
        self.setWindowTitle(title)
        
        font = QFont(genv.v__app__font, 10)
        font.setBold(True)
        self.setFont(font)
        
        self.hlayout    = QHBoxLayout()
        
        self.vlayout    = QVBoxLayout()
        self.helpButton = QPushButton(_("&Help"))
        self.prevButton = QPushButton(_("&Cancel"))
        self.exitButton = QPushButton(_("&Exit"))
        
        self.helpButton.setDefault(True)
        self.prevButton.setDefault(True)
        self.exitButton.setDefault(True)
        
        self.vlayout.addWidget(self.helpButton)
        self.vlayout.addWidget(self.prevButton)
        self.vlayout.addWidget(self.exitButton)
        
        if not genv.helpButton_connected:
            genv.helpButton_connected = True
            genv.prevButton_connected = True
            genv.exitButton_connected = True
            
            self.helpButton.clicked.connect(self.help_click)
            self.prevButton.clicked.connect(self.prev_click)
            self.exitButton.clicked.connect(self.exit_click)
        
        
        self.hexitText = QLabel(_("Would you realy exit the Application"))
        
        self.hlayout.addLayout(self.vlayout)
        self.hlayout.addWidget(self.hexitText)
        
        self.setLayout(self.hlayout)
    
    def help_click(self):
        print("help button")
        self.close()
        return
    def prev_click(self):
        print("reje")
        self.close()
        return
    def exit_click(self):
        print("exit")
        sys.exit(0)

class myMoveButton(QPushButton):
    def __init__(self, text, parent=None):
        super(myMoveButton, self).__init__(text, parent)
        
        self.parent = parent
        
        self.setMinimumWidth (84)
        self.setMinimumHeight(21)
        
        #self.parent.setAcceptDrops(True)
        
    def mouseMoveEvent(self, event):
        drag = QDrag(self)
        mime = QMimeData()
        drag.setMimeData(mime)
        drag.exec_(Qt.MoveAction)
    
    def dragEnterEvent(self, event):
        event.accept()
        print("enter")
    
    def dropEvent(self, event):
        pos = event.pos()
        widget = event.source()
        event.accept()
        print("drop")

class myGridViewerOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        event.accept()
        
    def dropEvent(self, event):
        pos = event.pos()
        widget = event.source()
        widget.move(pos.x(), pos.y())
        
        event.accept()
    def paintEvent(self, event):
        pen = QPen()
        
        painter = QPainter(self)
        painter.setPen(pen)
        
        points      = []
        gridSize    = 10
        
        x      = y  = -10
        
        width  = self.width()
        height = self.height()
        
        while y <= height:
            y += gridSize
            while x <= width:
                x += gridSize
                points.append(QPoint(x,y))
            x = 0
            points.append(QPoint(x,y))
        painter.drawPoints(points)

class addEventField(QLabel):
    def __init__(self, parent, text):
        super().__init__(text, parent)
        
        font1 = QFont(genv.v__app__font, 10); font1.setBold(True)
        font2 = QFont(genv.v__app__font, 10); font2.setBold(False)
        
        self.hlayout = QHBoxLayout()
        self.lhs     = self
        
        self.setMinimumWidth(112)
        self.setMaximumWidth(112)
        #
        self.setStyleSheet("margin:0px;border: 1px solid black;")
        self.setFont(font1)
        
        self.btn = QPushButton("E")
        self.btn.setMinimumWidth (15)
        self.btn.setMaximumWidth (15)
        #
        self.btn.setMaximumHeight(15)
        self.btn.setMaximumHeight(15)
        
        css_rhs = _("edit_css")
        
        self.rhs = QLineEdit()
        self.rhs.setMaximumWidth((self.width()+92)//2)
        self.rhs.setStyleSheet(css_rhs)
        self.rhs.setFont(font2)
        
        self.hlayout.addWidget(self.lhs)
        self.hlayout.addWidget(self.rhs)
        self.hlayout.addWidget(self.btn)
        
        parent.evt_vbox_layout.addLayout(self.hlayout)

class addPropertyCat(QLabel):
    def __init__(self, parent, text):
        super().__init__(text, parent)
        
        font = QFont(genv.v__app__font,12)
        font.setBold(True)
        
        self.setContentsMargins(2,0,0,2)
        self.setStyleSheet("background-color:gray;color:white")
        self.setMinimumHeight(16)
        self.resize(parent.pos_scroll_widget.width(),22)
        self.setFont(font)
        
        parent.pos_vbox_layout.addWidget(self)

class closeLabelX(QLabel):
    def __init__(self, text, parent):
        super().__init__(text, parent.close_btn)
        self.parent = parent
    
    def mousePressEvent(self, event):
        self.parent.close()

class addProperty(QLabel):
    def __init__(self, parent, kind, text):
        super().__init__(text, parent)
        
        font1 = QFont(genv.v__app__font, 10)
        font1.setBold(True)
        font2 = QFont(genv.v__app__font, 10)
        font2.setBold(False)
        
        self.hlayout = QHBoxLayout()
        self.lhs     = self
        
        if kind == 1:
            css_rhs = _("spin_css")
        
        elif kind == 2:
            css_rhs = _("edit_css")
        
        elif kind == 3:
            css_rhs = _("check_css")
        
        elif kind == 4:
            css_rhs = _("combo_css")
        
        self.ftext_spacer = ' ' * 9
        self.ttext_spacer = ' ' * 15
        
        if kind == 1:
            self.rhs = QSpinBox()
            self.rhs.setMaximumWidth((self.width()+100)//2)
        elif kind == 2:
            self.rhs = QLineEdit()
            self.rhs.setMaximumWidth((self.width()+100)//2)
            self.btn = QPushButton("E")
        elif kind == 3:
            self.rhs = QCheckBox()
            self.rhs.setText("FALSE" + self.ftext_spacer)
            self.rhs.setMaximumWidth((self.width()+100)//2)
            if not genv.rhs_stateChanged_connected:
                genv.rhs_stateChanged_connected = True
                self.rhs.stateChanged.connect(self.checkbox_changed)
        elif kind == 4:
            self.rhs = QComboBox()
            self.rhs.setMaximumWidth((self.width()+100)//2)
            self.rhs.addItem("black")
            self.rhs.addItem("white")
            self.rhs.addItem("red")
            self.rhs.addItem("green")
            self.rhs.addItem("yellow")
            self.rhs.addItem("blue")
        
        self.rhs.setStyleSheet(css_rhs)
        self.rhs.setFont(font2)
        
        self.hlayout.addWidget(self.lhs)
        self.hlayout.addWidget(self.rhs)
        
        if kind == 2:
            self.hlayout.addWidget(self.btn)
        
        self.setMinimumWidth(102)
        self.setMaximumWidth(102)
        #
        self.setStyleSheet("margin:0px;border: 1px solid black;")
        self.setFont(font1)
        
        parent.pos_vbox_layout.addLayout(self.hlayout)
    
    def checkbox_changed(self, int):
        if self.rhs.isChecked():
            self.rhs.setText("TRUE"  + self.ttext_spacer)
        else:
            self.rhs.setText("FALSE" + self.ftext_spacer)

class addInspectorItem():
    def __init__(self, parent, text, value):
        item = QTreeWidgetItem()
        item.setText(0,text)
        item.setText(1,str(value))
        #
        test1 = QTreeWidgetItem(item)
        test2 = QTreeWidgetItem(item)
        
        test1.setText(0,"TEST_A")
        test2.setText(0,"TEST_B")
        #
        parent.object_inspector.addTopLevelItem(item)


class CppSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        
        dark_green = QColor(0,100,0)
        
        self.commentFormat = QTextCharFormat()
        self.commentFormat.setForeground(dark_green)
        self.commentFormat.setFontWeight(QFont.Normal)  # Set the comment font weight to normal
        
        self.boldFormat = QTextCharFormat()
        self.boldFormat.setFont(QFont(genv.v__app__font_edit, 12))  # Set the font for keywords
        self.boldFormat.setFontWeight(QFont.Bold)
        
        # Definiere die Schlüsselwörter, die fettgedruckt sein sollen
        self.keywords = [
            ".AND.", ".OR.", ".NOR.", ".XOR.",
            "BREAK",
            "CASE",
            "CLASS",
            "DO",
            "IF",
            "ELSE",
            "ENDCASE",
            "ENDCLASS",
            "ENDFOR",
            "ENDIF",
            "ENDWHILE",
            "ENDWITH",
            "FOR",
            "RETURN",
            "TO",
            "WHILE", 
            "WITH"
        ]
        
        # Definiere die Muster für mehrzeilige Kommentare
        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(dark_green)
        self.commentStartExpression = QRegExp(r"/\*")
        self.commentEndExpression   = QRegExp(r"\*/")
    
    def highlightBlock(self, text):
        # Mehrzeilige Kommentare markieren
        self.setCurrentBlockState(0)
        
        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)
        
        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()
            self.setFormat(startIndex, commentLength, self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text, startIndex + commentLength)
        
        # Highlight single line comments
        single_line_comment_patterns = [r"//", r"\*\*", r"&&"]
        comment_positions = []
        
        # Suche nach einzeiligen Kommentaren und markiere sie
        for pattern in single_line_comment_patterns:
            for match in re.finditer(pattern, text):
                start = match.start()
                self.setFormat(start, len(text) - start, self.commentFormat)
                comment_positions.append((start, len(text) - start))
        
        # Suche nach Keywords und markiere sie
        for word in self.keywords:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                
                # Prüfen, ob das Keyword in einem Kommentar steht
                in_comment = any(start >= pos[0] and start < pos[0] + pos[1] for pos in comment_positions)
                
                # Prüfen, ob das Keyword in einem mehrzeiligen Kommentar steht
                if self.previousBlockState() != 1 and not in_comment:
                    self.setFormat(start, length, self.boldFormat)

class EditorTextEdit(QPlainTextEdit):
    def __init__(self, file_name):
        super().__init__()
        
        self.lineNumberArea = LineNumberArea(self)
        self.bookmarks = set()
        self.highlighter = CppSyntaxHighlighter(self.document())
        
        if not genv.blockCountChanged_connected:
            genv.blockCountChanged_connected = True
            genv.cursorPositionChanged_connected = True
            
            self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
            self.updateRequest.connect(self.updateLineNumberArea)
            self.cursorPositionChanged.connect(self.highlightCurrentLine)
        
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        
        # Schriftgröße und Schriftart setzen
        self.setFont(QFont(genv.v__app__font_edit, 12))
        
        if not os.path.exists(file_name):
            print(f"Error: file does not exists: {file_name}")
            return
        with open(file_name, 'r') as file:
            text = file.read()
            file.close()
        
        self.setPlainText(text)
    
    def lineNumberAreaWidth(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num /= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        icon_space = 20  # Platz für die Icons
        return space + icon_space
    
    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
    
    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))
    
    def highlightCurrentLine(self):
        extraSelections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            
            lineColor = QColor(Qt.yellow).lighter(160)
            
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        
        self.setExtraSelections(extraSelections)
    
    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)
        
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                rect = QRect(20, int(top), self.lineNumberArea.width() - 20, self.fontMetrics().height())
                painter.drawText(rect, Qt.AlignRight, number)
                
                # Zeichnen des Icons
                icon_rect = QRect(0, int(top), 20, self.fontMetrics().height())
                if blockNumber in self.bookmarks:
                    painter.setBrush(Qt.red)
                    painter.drawEllipse(icon_rect.center(), 5, 5)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            block = cursor.block()
            block_number = block.blockNumber()
            top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
            bottom = top + self.blockBoundingRect(block).height()
            
            # Überprüfen, ob der Klick innerhalb der Linie liegt
            if int(top) <= event.pos().y() <= int(bottom):
                if block_number in self.bookmarks:
                    self.bookmarks.remove(block_number)
                else:
                    self.bookmarks.add(block_number)
                self.lineNumberArea.update()
        
        super().mousePressEvent(event)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)
    
    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)
        self.setFont(QFont(genv.v__app__font_edit, 12))  # Schriftgröße und Schriftart für Zeilennummerbereich setzen


class myGridViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.parent = parent
        positions   = [(i, j) for i in range(3) for j in range(3)]
        
        self.layout           = QGridLayout()
        self.property_layout  = QVBoxLayout()
        
        self.layout         .setContentsMargins(0,0,0,0)
        self.property_layout.setContentsMargins(0,0,0,0)
        
        font1 = QFont(genv.v__app__font, 10); font1.setBold(False)
        font2 = QFont(genv.v__app__font, 10); font2.setBold(True)
        
        self.object_inspector = QTreeWidget()
        self.object_inspector.setIconSize(QSize(20,20))
        self.object_inspector.setFont(font1)
        self.object_inspector.setStyleSheet(_("inspect_css"))
        
        headerLabel = ["Name", "Count"]
        self.object_inspector.setColumnCount(len(headerLabel))
        self.object_inspector.setHeaderLabels(headerLabel)
        #
        addInspectorItem(self,"Objects's"  ,   0)
        addInspectorItem(self,"Classes"    ,   0)
        addInspectorItem(self,"Procedure's", 100)
        addInspectorItem(self,"Function's" , 200)
        addInspectorItem(self,"Variable's" , 300)
        
        
        self.property_page  = QTabWidget()
        self.property_page.setContentsMargins(0,0,0,0)
        self.property_page.setMinimumWidth(244)
        self.property_page.setMaximumWidth(244)
        self.property_page.setStyleSheet(_("tab_widget_2"))
        #
        self.property_tabs1 = QWidget()
        self.property_tabs2 = QWidget()
        #
        self.property_tabs1.setContentsMargins(0,0,0,0)
        self.property_tabs2.setContentsMargins(0,0,0,0)
        #
        self.property_tabs1.setMinimumWidth(244)
        self.property_tabs1.setMaximumWidth(244)
        #
        self.property_tabs2.setMinimumWidth(244)
        self.property_tabs2.setMaximumWidth(244)
        #
        self.property_tabs1.setStyleSheet("background-color:lightgray;")
        self.property_tabs2.setStyleSheet("background-color:lightgray;")
        #
        
        self.property_page.addTab(self.property_tabs1,"Properties")
        self.property_page.addTab(self.property_tabs2,"Events")
        
        self.pos_scroll_widget = QWidget()
        self.pos_scroll_widget.setContentsMargins(0,0,0,0)
        #
        self.evt_scroll_widget = QWidget()
        self.evt_scroll_widget.setContentsMargins(0,0,0,0)
                
        self.pos_vbox_layout = QVBoxLayout(); self.pos_vbox_layout.setContentsMargins(0,0,0,0)
        self.evt_vbox_layout = QVBoxLayout(); self.evt_vbox_layout.setContentsMargins(0,0,0,0)
        
        ### hier
        self.pos_cat1 = addPropertyCat(self,"Position")
        self.pos_cat1_prop_width  = addProperty(self, 1,"Width")
        self.pos_cat1_prop_height = addProperty(self, 1,"Height")
        self.pos_cat1_prop_top    = addProperty(self, 1,"Top")
        self.pos_cat1_prop_left   = addProperty(self, 1,"Left")
        
        self.pos_cat2 = addPropertyCat(self,"Font")
        self.pos_cat2_font_name      = addProperty(self,2,"Name")
        self.pos_cat2_font_size      = addProperty(self,1,"Size")
        self.pos_cat2_font_color_fg  = addProperty(self,4,"Foreground")
        self.pos_cat2_font_color_bg  = addProperty(self,4,"Background")
        self.pos_cat2_font_bold      = addProperty(self,3,"Bold")
        self.pos_cat2_font_italic    = addProperty(self,3,"Italic")
        self.pos_cat2_font_underline = addProperty(self,3,"Underline")
        self.pos_cat2_font_strike    = addProperty(self,3,"Strike")
        
        self.pos_cat3 = addPropertyCat(self,"Text")
        self.pos_cat3_object_name = addProperty(self,2,"Caption")
        self.pos_cat3_object_id   = addProperty(self,2,"Name")
        
        self.pos_cat4 = addPropertyCat(self,"Appearence")
        self.pos_cat4_background_color = addProperty(self,4,"BackColor")
        self.pos_cat4_border_color     = addProperty(self,4,"Border Color")
        self.pos_cat4_border_size      = addProperty(self,1,"Border Size")
        self.pos_cat4_border_radius    = addProperty(self,1,"Border Radius")
        self.pos_cat4_border_type      = addProperty(self,4,"Border Type")
        
        self.pos_cat5 = addPropertyCat(self,"Application")
        self.pos_cat4_app_name     = addProperty(self,2,"Name")
        self.pos_cat4_app_helpfile = addProperty(self,2,"Helpfile")
        self.pos_cat5_aüü_helpstr  = addProperty(self,2,"Help URL")
        self.pos_cat5_app_helpid   = addProperty(self,2,"Help ID")
        ####
        
        self.evt_on_enter       = addEventField(self,"OnGotFocus")
        self.evt_on_leave       = addEventField(self,"OnLeftFocus")
        self.evt_on_key_down    = addEventField(self,"OnKeyDown")
        self.evt_on_key_press   = addEventField(self,"OnKeyPress")
        self.evt_on_key_up      = addEventField(self,"OnKeyUp")
        self.evt_on_mouse_down  = addEventField(self,"OnMouseDown")
        self.evt_on_mouse_press = addEventField(self,"OnMousePress")
        self.evt_on_mouse_up    = addEventField(self,"OnMouseUp")
        
        self.evt_on_form_create = addEventField(self,"OnFormCreate")
        self.evt_on_form_close  = addEventField(self,"OnFormClose")
        self.evt_on_form_show   = addEventField(self,"OnFormShow")
        ### da
        #
        self.pos_scroll_widget.setLayout(self.pos_vbox_layout)
        self.evt_scroll_widget.setLayout(self.evt_vbox_layout)
        
        self.scroll = QScrollArea()
        self.scroll.setContentsMargins(0,0,0,0)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.pos_scroll_widget)
        #
        self.scroll2 = QScrollArea()
        self.scroll2.setContentsMargins(0,0,0,0)
        self.scroll2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll2.setMinimumWidth(244)
        self.scroll2.setMaximumWidth(244)
        self.scroll2.setWidgetResizable(True)
        self.scroll2.setWidget(self.evt_scroll_widget)
        
        self.vl = QVBoxLayout()
        self.vl.setContentsMargins(0,0,0,0)
        self.vl.addWidget(self.scroll)
        self.property_tabs1.setLayout(self.vl)
        #
        self.vl2 = QVBoxLayout()
        self.vl2.setContentsMargins(0,0,0,0)
        self.vl2.addWidget(self.scroll2)
        self.property_tabs2.setLayout(self.vl2)
        
        
        self.property_top    = QLabel("Object Inspector:")
        self.property_bottom = QLabel("B")
        #
        self.set_style(self.property_top)
        self.set_style(self.property_bottom)
        ####
        
        self.scroll_up    = QLabel("A"); self.scroll_up   .setFont(font1)
        self.scroll_down  = QLabel("B"); self.scroll_down .setFont(font1)
        self.scroll_left  = QLabel("C"); self.scroll_left .setFont(font1)
        self.scroll_right = QLabel("D"); self.scroll_right.setFont(font1)
        
        self.set_style(self.scroll_right)
        self.set_style(self.scroll_up)
        self.set_style(self.scroll_down)
        self.set_style(self.scroll_left)
        
        self.scroll_up   .setMaximumHeight(16)
        self.scroll_down .setMaximumHeight(16)
        #
        self.scroll_right.setMaximumWidth (16)
        self.scroll_left .setMaximumWidth (16)
        #
        self.content = myGridViewerOverlay(self.parent)
        #
        self.layout.addWidget(self.property_top   , 0,0)
        self.layout.addWidget(self.property_bottom, 2,0)
        #
        
        self.property_object = QGridLayout()
        self.property_object.setContentsMargins(0,0,0,0)
        self.property_object.addWidget(self.object_inspector,0,0)
        self.property_object.addWidget(self.property_page   ,1,0)
        #
        self.object_widget = QWidget()
        self.object_widget.setMaximumWidth(245)
        self.object_widget.setLayout(self.property_object)
        
        self.layout.addWidget(self.scroll_up    , 0,2)
        self.layout.addWidget(self.scroll_left  , 1,1)
        self.layout.addWidget(self.object_widget, 1,0)
        self.layout.addWidget(self.content      , 1,2)
        self.layout.addWidget(self.scroll_right , 1,3)
        self.layout.addWidget(self.scroll_down  , 2,2)
        #
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        #
        chr3 = "{0}".format(u'\u25c4')  # /\
        chr4 = "{0}".format(u'\u25ba')  # \/
        #
        self.scroll_right.setText(chr2)
        self.scroll_left .setText(chr1)
        self.scroll_up   .setText(chr3)
        self.scroll_down .setText(chr4)
        #
        self.scroll_down .setAlignment(Qt.AlignCenter)
        self.scroll_up   .setAlignment(Qt.AlignCenter)
        #
        self.setLayout(self.layout)
    
    def set_style(self, obj):
        obj.setStyleSheet("background-color:lightgray;")

class MySQLDialog(QFrame):
    def __init__(self, text):
        super().__init__()
        
        font = QFont(genv.v__app__font, 10)
        font.setBold(True)
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setContentsMargins(1,1,1,1)
        self.setMouseTracking(True)
        self.dragging = False
        
        self.setMaximumHeight(200)
        self.setMaximumWidth (100)
        
        self.titlebar = QWidget(self)
        self.titlebar.move(0,0)
        self.titlebar.resize(200,21)
        self.titlebar.setMaximumHeight(21)
        self.titlebar.setStyleSheet("border:1px solid black;background-color:yellow;")
        
        self.title = QLabel(text, self.titlebar)
        self.title.setStyleSheet("border:0px solid yellow;")
        self.title.setFont(font)
        self.title.move(3,3)
        
        self.close_btn = QWidget(self.titlebar)
        self.close_btn.setStyleSheet("background-color:red;")
        self.close_btn.move(74,2)
        self.close_btn.resize(20,20)
        
        self.close_btn_lbl = closeLabelX(" X ", self)
        self.close_btn_lbl.setStyleSheet("color: white;font-weight:bold;")
        
        
        self.textw = QWidget()
        self.setStyleSheet("background-color:white;")
        
        self.hlayout = QVBoxLayout()
        self.check_box_1 = QCheckBox("FiELD A")
        self.check_box_2 = QCheckBox("FiELD B")
        #
        self.hlayout.addWidget(self.check_box_1)
        self.hlayout.addWidget(self.check_box_2)
        
        
        layout = QVBoxLayout()
        layout.setContentsMargins(1,1,1,1)
        layout.addWidget(self.titlebar)
        layout.addLayout(self.hlayout)
        layout.addWidget(self.textw)
        
        
        self.setLayout(layout)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_position = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = QPoint(event.globalPos() - self.mapToGlobal(self.drag_start_position))
            self.move(self.x() + delta.x(), self.y() + delta.y())
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

class addDesignerTabs():
    def __init__(self, tab):
        self.tab = tab
        liste = [
            ["Standard", [
                "tmouse","tmainmenu","tpopupmenu","tlabel","tbutton","tedit","tmemo",
                "tlistbox","ttreeview","tcombobox","tradiobutton"
                ],
            ],
            ["System", [
                ],
            ],
            ["Data Controls", [
                ],
            ],
            ["Dialogs", [
                ],
            ],
            ["Indy Client", [
                ],
            ],
            ["Indy Server", [
                ],
            ],
        ]
        for tabitem in liste:
            tab_widget = QWidget()
            self.tab.addTab(tab_widget,tabitem[0])
            self._listwidget = QListWidget(tab_widget)
            self._listwidget.setViewMode(QListView.IconMode)
            self._listwidget.setResizeMode(QListView.Adjust)
            self._listwidget.setMinimumWidth(500)
            
            if len(tabitem[1]) > 0:
                for item in tabitem[1]:
                    list_item = QListWidgetItem("", self._listwidget)
                    list_item.setIcon(QIcon(os.path.join(genv.v__app__img__int__, item + "_150.bmp")))

class c64WorkerThread(threading.Thread):
    def __init__(self, parent):
        super().__init__()
        self.running = False
        self.parent  = parent
        #self.painter = parent.painter
    
    def run(self):
        count = 0
        while self.running:
            if count > 10000:
                count = 0
            count += 1
            time.sleep(0.75)
            print("debug text")
    
    def start(self):
        self.running = True
        super().start()
    
    def stop(self):
        self.running = False
    

class c64Bildschirm(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        #
        self.parent  = parent
        self.painter = QPainter()
        #
        self.setMinimumWidth ( 620 )
        self.setMaximumWidth ( 620 )
        #
        self.setMinimumHeight( 515 )
        self.setMaximumHeight( 515 )
        
        self.setStyleSheet("background-color:blue;")
        
        self.worker_thread = c64WorkerThread(self)
    
    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setBrush(QBrush(QColor(0, 158, 255)))
        self.painter.drawRect(1,1,320 + 64 + 20, 200 + 64 + 50)
        
        self.painter.setBrush(QBrush(QColor(0, 108, 255)))
        self.painter.drawRect(20,20,320 + 44, 200 + 64 + 14)
        
        font = QFont("C64 Elite Mono",11)
        font.setBold(True)
        
        self.painter.setPen(QColor(200, 228, 255))  # Blaue Schrift
        self.painter.setFont(font)
        
        self.painter.drawText(21,32,"1234567890" * 4)
        line = 11
        i    =  2
        while i < 26:
            self.painter.drawText(21,32+(line),str(i))
            self.painter.drawText(21,32+22,"HUCH")
            i += 1
            line += 11
        self.painter.end()

class addDataSourceDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Add Data Source...")
        self.setMaximumWidth (600)
        self.setMinimumWidth (400)
        #
        self.setMaximumHeight(600)
        self.setMaximumHeight(400)
        
        font = QFont(genv.v__app__font, 10)
        self.setFont(font)
        
class myAddTableDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Add Table")
        self.setMaximumWidth (600)
        self.setMinimumWidth (400)
        #
        self.setMaximumHeight(600)
        self.setMaximumHeight(400)
        
        font = QFont(genv.v__app__font, 10)
        self.setFont(font)
        
        self.layout_top = QVBoxLayout()
        #
        self.layout_top1 = QHBoxLayout()
        self.lbl_av_tables = QLabel("Available Tables:")
        self.lbl_in_tables = QLabel("Open Tables:")
        #
        self.layout_top1.addWidget(self.lbl_av_tables)
        self.layout_top1.addWidget(self.lbl_in_tables)
        
        self.layout_top2 = QHBoxLayout()
        self.tbl_av_tables = QListWidget()
        self.tbl_in_tables = QListWidget()
        #
        #
        self.layout_top3 = QVBoxLayout()
        self.btn_move_add_1 = QPushButton(">>")
        self.btn_move_del_1 = QPushButton("<<")
        self.btn_move_add_2 = QPushButton("Add")
        self.btn_move_clr_1 = QPushButton("Remove")
        self.btn_move_clr_2 = QPushButton("Clear")
        #
        self.layout_top3.addWidget(self.btn_move_add_1)
        self.layout_top3.addWidget(self.btn_move_del_1)
        self.layout_top3.addWidget(self.btn_move_add_2)
        self.layout_top3.addWidget(self.btn_move_clr_1)
        self.layout_top3.addWidget(self.btn_move_clr_2)
        #
        self.layout_top2.addWidget(self.tbl_av_tables)
        self.layout_top2.addLayout(self.layout_top3)
        self.layout_top2.addWidget(self.tbl_in_tables)
        
        ###
        self.layout_bottom = QHBoxLayout()
        #
        self.btn_add    = QPushButton("Add Table")
        self.btn_addsrc = QPushButton("Add Data Source")
        self.btn_close  = QPushButton("Close")
        
        self.btn_add   .setMinimumHeight(31)
        self.btn_addsrc.setMinimumHeight(31)
        self.btn_close .setMinimumHeight(31)
        
        self.layout_bottom.addWidget(self.btn_add)
        self.layout_bottom.addWidget(self.btn_addsrc)
        self.layout_bottom.addWidget(self.btn_close)
        
        self.layout_top.addLayout(self.layout_top1)
        self.layout_top.addLayout(self.layout_top2)
        self.layout_top.addLayout(self.layout_bottom)
        
        self.setLayout(self.layout_top)
        
        if not genv.btn_add_connected:
            genv.btn_add_connected    = True
            genv.btn_addsrc_connected = True
            genv.btn_close_connected  = True
            
            self.btn_add   .clicked.connect(self.btn_add_clicked)
            self.btn_addsrc.clicked.connect(self.btn_addsrc_clicked)
            self.btn_close .clicked.connect(self.btn_close_clicked)
        
        # ----------------------------------------
        # detect files in the current directory...
        # ----------------------------------------
        directory = "./"
        pattern = os.path.join(directory, "*.db")
        db_files = glob.glob(pattern)
        
        self.font1 = QFont(genv.v__app__font, 10)
        self.font1.setBold(True)
        
        self.font2 = QFont(genv.v__app__font, 10)
        self.font2.setBold(False)
        
        local_sqlite_item = QListWidgetItem("Local Data Files:")
        local_sqlite_item.setFlags(local_sqlite_item.flags() & ~Qt.ItemIsSelectable) # non-selectable
        local_sqlite_item.setBackground(QBrush(QColor("blue")))
        local_sqlite_item.setForeground(QBrush(QColor("white")))
        local_sqlite_item.setFont(self.font1)
        
        self.tbl_av_tables.addItem(local_sqlite_item)
        if len(db_files) > 0:
            tables = []
            for file_name in db_files:
                conn = sqlite3.connect(file_name)
                cursor = conn.cursor()
                
                # query for the table names:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                
                if len(tables) > 0:
                    for table in tables:
                        table_name = table[0]
                        cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                        row_count = cursor.fetchone()[0]
                        
                        if row_count > 0:
                            table_name = file_name + " => " + table_name
                            table_item = QListWidgetItem(table_name)
                            table_item.setFont(self.font2)
                            self.tbl_av_tables.addItem(table_item)
                conn.close()
                
        local_data_item = QListWidgetItem("Local Data Sources:")
        local_data_item.setFlags(local_data_item.flags() & ~Qt.ItemIsSelectable) # non-selectable
        local_data_item.setBackground(QBrush(QColor("blue")))
        local_data_item.setForeground(QBrush(QColor("white")))
        local_data_item.setFont(self.font1)
        
        self.tbl_av_tables.addItem(local_data_item)
        ###
        #
        remote_data_item = QListWidgetItem("Remote Data Sources:")
        remote_data_item.setFlags(remote_data_item.flags() & ~Qt.ItemIsSelectable) # non-selectable
        remote_data_item.setBackground(QBrush(QColor("blue")))
        remote_data_item.setForeground(QBrush(QColor("white")))
        remote_data_item.setFont(self.font1)
        
        self.tbl_av_tables.addItem(remote_data_item)
        ###
    
    def btn_add_clicked(self):
        print("add")
        return
    
    def btn_addsrc_clicked(self):
        datadialog = addDataSourceDialog(self)
        datadialog.exec_()
        return
    
    def btn_close_clicked(self):
        self.close()
    
    def shorten_string(self, s, maxlength):
        if len(s) <= maxlength:
            return s
        else:
            return s[:maxlength-3]+"..."

class myDataTabWidget(QWidget):
    class MaxLengthDelegate(QStyledItemDelegate):
        def __init__(self, max_length, parent=None):
            super().__init__(parent)
            self.max_length = max_length
        
        def createEditor(self, parent, option, index):
            editor = QLineEdit(parent)
            editor.setMaxLength(self.max_length)
            return editor
    
    class ComboBoxDelegate(QStyledItemDelegate):
        def __init__(self, items, parent=None):
            super().__init__(parent)
            self.items = items
        
        def createEditor(self, parent, option, index):
            editor = QComboBox(parent)
            editor.addItems(self.items)
            return editor
        
        def setEditorData(self, editor, index):
            super().setEditorData(editor, index)
            editor.showPopup()
    
    class CheckBoxDelegate(QStyledItemDelegate):
        def createEditor(self, parent, option, index):
            editor = QWidget(parent)
            layout = QHBoxLayout(editor)
            layout.setContentsMargins(0, 0, 0, 0)
            check_box = QCheckBox(parent)
            layout.addWidget(check_box)
            check_box.setTristate(False)
            check_box.setChecked(index.model().data(index, Qt.EditRole) == "YES")
            editor.setLayout(layout)
            return editor
        
        def setEditorData(self, editor, index):
            check_box = editor.findChild(QCheckBox)
            if check_box:
                value = index.model().data(index, Qt.EditRole)
                if value == "YES":
                    check_box.setChecked(True)
                    check_box.setText("YES")
                else:
                    check_box.setChecked(False)
                    check_box.setText("NO")
        
        def setModelData(self, editor, model, index):
            check_box = editor.findChild(QCheckBox)
            if check_box:
                value = "YES" if check_box.isChecked() else "NO"
                model.setData(index, value, Qt.EditRole)
        
        def updateEditorGeometry(self, editor, option, index):
            editor.setGeometry(option.rect)
    
    def __init__(self,parent):
        super().__init__()
        self.parent = parent
        
        self.vlayout = QVBoxLayout()
        self.hlayout = QHBoxLayout()
        
        self.top_widget = QWidget()
        self.top_widget.setStyleSheet("background-color: gray;")
        self.top_widget.setMinimumHeight(62)
        self.top_widget.setMaximumHeight(62)
        
        self.vlayout.addWidget(self.top_widget)
        #self.vlayout.addStretch()
        
        ###
        font = QFont(genv.v__app__font, 11)
        
        self.table_btn_add      = QPushButton("Add Table Field")
        self.table_btn_remove   = QPushButton("Remove Field")
        self.table_btn_clearall = QPushButton("Clear Table Dash")
        
        self.table_btn_add.setMinimumHeight(29)
        self.table_btn_add.setFont(font)
        #
        self.table_btn_remove.setMinimumHeight(29)
        self.table_btn_remove.setFont(font)
        #
        self.table_btn_clearall.setMinimumHeight(29)
        self.table_btn_clearall.setFont(font)
        
        self.hlayout.addWidget(self.table_btn_add)
        self.hlayout.addWidget(self.table_btn_remove)
        self.hlayout.addWidget(self.table_btn_clearall)
        
        self.table_btn_add     .clicked.connect(self.table_btn_add_clicked)
        self.table_btn_remove  .clicked.connect(self.table_btn_remove_clicked)
        self.table_btn_clearall.clicked.connect(self.table_btn_clearall_clicked)
        
        ###
        self.rlayout = QHBoxLayout()
        self.table_widget = QTableWidget(0,5)
        self.table_widget.setHorizontalHeaderLabels(["Name","Type","Len","Prec","PrKey"])
        
        horizontal_header = self.table_widget.horizontalHeader()
        vertical_header   = self.table_widget.verticalHeader()
        
        horizontal_header.setStyleSheet("QHeaderView::section { background-color: lightgreen; color: black; font-weight: bold; }")
        vertical_header  .setStyleSheet("QHeaderView::section { background-color: lightblue; color: black; font-weight: bold; }")
        
        
        # Delegate für die erste Spalte setzen
        self.delegate = self.MaxLengthDelegate(30, self.table_widget)
        self.table_widget.setItemDelegateForColumn(0, self.delegate)
        
        self.combo_items = ["Option 1", "Option 2", "Option 3"]
        
        # Delegate für die zweite Spalte setzen
        self.combo_box_delegate = self.ComboBoxDelegate(self.combo_items, self.table_widget)
        self.table_widget.setItemDelegateForColumn(1, self.combo_box_delegate)
        self.table_widget.itemChanged.connect(self.check_if_checkbox_clicked)
        
        # Delegate für die dritte Spalte setzen
        self.check_box_delegate = self.CheckBoxDelegate(self.table_widget)
        self.table_widget.setItemDelegateForColumn(4, self.check_box_delegate)
        
        
        self.rlayout.addWidget(self.table_widget)
        
        self.lbl_table = QLabel("Data Table Name:")
        self.lbl_table.setFont(font)
        #
        self.edt_table = QLineEdit("session")
        self.edt_table.setFont(font)
        #
        self.edt_button = QPushButton("Save Data Informations")
        self.edt_button.setFont(font)
        self.edt_button.setMinimumHeight(29)
        ###
        #
        self.lbl_source = QLabel("Data Source:")
        self.lbl_source.setFont(font)
        #
        self.edt_source = QLineEdit(".\\\\server1")
        self.edt_source.setFont(font)
        
        self.vlayout.addLayout(self.hlayout)
        self.vlayout.addLayout(self.rlayout)
        
        self.vlayout.addWidget(self.lbl_table)
        self.vlayout.addWidget(self.edt_table)
        self.vlayout.addWidget(self.edt_button)
        #
        self.vlayout.addWidget(self.lbl_source)
        self.vlayout.addWidget(self.edt_source)
        ###
        
        self.sql_label    = QLabel("SQL Query:")
        self.sql_window   = QPlainTextEdit()
        self.sql_exec_btn = QPushButton("Execute SQL Query Text")
        
        self.sql_label.setFont(font)
        #
        self.sql_exec_btn.setMinimumHeight(29)
        self.sql_exec_btn.setFont(font)
        
        self.vlayout.addWidget(self.sql_label)
        self.vlayout.addWidget(self.sql_window)
        self.vlayout.addWidget(self.sql_exec_btn)
        
        self.vlayout.addStretch()
        self.setLayout(self.vlayout)
    
    def add_row(self, table_widget):
        row_position = table_widget.rowCount()
        table_widget.insertRow(row_position)
        
        for col in range(table_widget.columnCount()):
            item = QTableWidgetItem()
            if col == 4:
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setCheckState(Qt.Unchecked)
                item.setText("NO")
            elif col == 0:
                item.setText(f"FIELD_{row_position+1}")
            elif col == 1:
                item.setText("Option 1")
            elif col == 2:
                item.setText("10")
            elif col == 3:
                item.setText("0")
            table_widget.setItem(row_position, col, item)
    
    def check_if_checkbox_clicked(self,item):
        if item.column() == 4:  # Überprüfen, ob die Spalte die CheckBox-Spalte ist
            if item.checkState() == Qt.Checked:
                item.setText("YES")
            else:
                item.setText("NO")
        
    def del_row(self, table_widget):
        current_row = table_widget.currentRow()
        if current_row != -1:
            table_widget.removeRow(current_row)
    
    def table_btn_add_clicked(self):
        self.add_row(self.table_widget)
        
    def table_btn_remove_clicked(self):
        self.del_row(self.table_widget)
    
    def table_btn_clearall_clicked(self):
        print("clr all")

class MyCountryProject(QWidget):
    def __init__(self, class_parent, parent, itemA, itemB):
        super().__init__()
        
        hlayout = QHBoxLayout()
        vlayout = QVBoxLayout()
        
        fontN = QFont(genv.v__app__font, 10)
        fontB = QFont(genv.v__app__font, 10)
        fontB.setBold(True)
        
        hlay = QHBoxLayout()
        mid1 = QLabel("USA", self)
        mid1.setFont(fontB)
        mid2 = QLabel("to:", self)
        mid2.setFont(fontN)
        mid3 = QLabel(itemB[0], self)
        mid3.setFont(fontB)
        
        hlay.addWidget(mid1)
        hlay.addWidget(mid2)
        hlay.addWidget(mid3)
        
        vlayout.addLayout(hlay)
        
        label_lhs = QLabel(self)
        label_rhs = QLabel(self)
        
        label_lhs.setAlignment(Qt.AlignCenter)
        label_rhs.setAlignment(Qt.AlignCenter)
        
        pixmap_lhs = self.get_pixmap_from_url("USA.gif")
        pixmap_rhs = self.get_pixmap_from_url(itemB[0] + ".gif")
        
        if not pixmap_lhs.isNull():
            label_lhs.setPixmap(pixmap_lhs)
        else:
            label_lhs.setText("Image not found")
        
        if not pixmap_rhs.isNull():
            label_rhs.setPixmap(pixmap_rhs)
        else:
            label_rhs.setText("Image not found")
        
        hlayout.addWidget(label_lhs)
        hlayout.addLayout(vlayout)
        hlayout.addWidget(label_rhs)
        
        self.setLayout(hlayout)
        
        listItem = QListWidgetItem(parent)
        listItem.setSizeHint(self.sizeHint())
        parent.setItemWidget(listItem, self)
    
    def get_pixmap_from_url(self, url):
        pict = os.path.join(genv.v__app__img__int__, "flags", url)
        pixmap = QPixmap(pict)
        return pixmap

class ExtensionFilterProxyModel(QSortFilterProxyModel):
    def __init__(self, extensions, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extensions = extensions
    
    def filterAcceptsRow(self, source_row, source_parent):
        index = self.sourceModel().index(source_row, 0, source_parent)
        if not index.isValid():
            return False
        
        file_path = self.sourceModel().filePath(index)
        file_name = os.path.basename(file_path)
        
        # Check if it's a directory
        if os.path.isdir(file_path):
            # Exclude hidden directories (starting with a dot)
            if file_name.startswith('.'):
                return False
            return True
        
        # Exclude hidden files (starting with a dot)
        if file_name.startswith('.'):
            return False
        
        # Check file extension
        file_extension = os.path.splitext(file_path)[1].lower()
        return file_extension in self.extensions

class setLocalesProjectSetting(QDialog):
    def __init__(self, parent, prop, value):
        super().__init__(parent)
        
        self.parent = parent
        self.parent.property_value = value
        self.parent.property_name  = prop
        
        self.prop   = prop
        self.value  = value
        self.initUI()
    
    def initUI(self):
        okbtn = QPushButton("Save and Close")
        clbtn = QPushButton("Close")
        
        okbtn.clicked.connect(self.save_and_close)
        clbtn.clicked.connect(self.reject)
        
        hbox  = QHBoxLayout()
        hbox.addWidget(okbtn)
        hbox.addWidget(clbtn)
        
        prop  = QLabel("Property:   " + self.prop)
        label = QLabel("Value:")
        #
        self.edit = QLineEdit("Value:")
        self.edit.setText(self.value)
        
        vbox  = QVBoxLayout()
        vbox.addWidget(prop)
        vbox.addWidget(label)
        vbox.addWidget(self.edit)
        
        vbox.addLayout(hbox)
        self.setLayout(vbox)
        
        self.set_custom_button_style(okbtn)
        self.set_custom_button_style(clbtn)
        
        self.set_custom_lineedit_style(self.edit)
        
        self.set_custom_font(prop)
        self.set_custom_font(label)
        
        self.setMinimumWidth(300)
        self.setWindowTitle("Locales properties")
    
    def save_and_close(self):
        self.parent.property_value = self.edit.text()
        self.close()
    
    def set_custom_button_style(self, button):
        button.setMinimumHeight(31)
        self.set_custom_font(button)
    
    def set_custom_font(self, widget):
        widget.setFont(QFont(genv.v__app__font, 10))
    
    def set_custom_lineedit_style(self, lineedit):
        lineedit.setFont(QFont(genv.v__app__font_edit, 11))
    
class OpenProFileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.property_value = ""
        self.property_name  = ""
        
        self.initUI()
        self.load_favorites_from_ini()
        self.load_drives()
        
        noan = "n/a"
        #
        self.project_name    = noan
        self.project_author  = noan
        self.project_version = noan
        self.project_email   = noan
        self.project_lastmod = noan
        #
        self.project_content_type     = noan
        self.project_content_encoding = noan
        self.project_mime_type        = noan
        self.project_language_team    = noan
        self.project_last_translater  = noan
        self.project_pot_create_date  = noan
        self.project_po_revision_date = noan
    
    def initUI(self):
        hbox = QHBoxLayout(self)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Create the favorites tree
        self.favorites_tree = QTreeWidget()
        self.favorites_tree.setHeaderLabels(["Project Name", "Path"])
        self.favorites_tree.setColumnWidth(0, 150)
        self.favorites_tree.header().setSectionResizeMode(0, QHeaderView.Interactive)
        self.favorites_tree.header().setSectionResizeMode(1, QHeaderView.Interactive)
        self.favorites_tree.setMaximumWidth(380)
        self.favorites_tree.itemDoubleClicked.connect(self.on_favorite_double_clicked)
        self.favorites_tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.favorites_tree.setSizeAdjustPolicy(QTreeWidget.AdjustToContents)
        self.favorites_tree.setStyleSheet("QHeaderView::section { background-color: lightblue }")
        
        # Create the drives tree
        self.drives_tree = QTreeWidget()
        self.drives_tree.setHeaderLabels(["Drive", "Available Space", "Total Size"])
        self.drives_tree.setMaximumHeight(120)
        self.drives_tree.setMaximumWidth(380)
        self.drives_tree.header().setSectionResizeMode(QHeaderView.Interactive)
        self.drives_tree.itemClicked.connect(self.on_drive_clicked)
        self.drives_tree.setStyleSheet("QHeaderView::section { background-color: lightgreen }")
        
        
        ##
        self.project_tree = QTreeWidget()
        self.project_tree.setHeaderLabels(["Name", "Path"])
        self.project_tree.setMaximumHeight(100)
        self.project_tree.setMaximumWidth(380)
        self.project_tree.header().setSectionResizeMode(QHeaderView.Interactive)
        self.project_tree.itemClicked.connect(self.on_project_clicked)
        self.project_tree.setStyleSheet("QHeaderView::section { background-color: lightgreen }")
        ##
        
        
        # Create the directory view
        self.dir_model = QFileSystemModel()
        self.dir_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        self.dir_model.setRootPath(QDir.rootPath())
        
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.dir_model)
        self.tree_view.setRootIndex(self.dir_model.index(QDir.rootPath()))
        self.tree_view.setMinimumWidth(300)
        self.tree_view.clicked.connect(self.on_tree_view_clicked)
        self.tree_view.setHeaderHidden(False)
        self.tree_view.header().setSectionResizeMode(QHeaderView.Interactive)
        self.tree_view.setStyleSheet("QHeaderView::section { background-color: lightblue }")
        
        # Create the file list view
        self.file_list = QTreeWidget()
        self.file_list.setHeaderLabels(["Key", "Value"])
        self.file_list.header().setSectionResizeMode(0, QHeaderView.Interactive)
        self.file_list.header().setSectionResizeMode(1, QHeaderView.Interactive)
        self.file_list.itemDoubleClicked.connect(self.on_file_double_clicked)
        
        # Create the path input
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        self.set_custom_lineedit_style(self.path_input)
        
        # Create the filter input
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText('Filter files...')
        self.filter_input.textChanged.connect(self.filter_files)
        self.set_custom_lineedit_style(self.filter_input)
        
        # Create the label
        self.label = QLabel('No file selected.', self)
        self.set_custom_font(self.label)
        
        # Create the buttons
        self.add_favorite_button = QPushButton('Add to Favorites', self)
        self.add_favorite_button.clicked.connect(self.add_to_favorites)
        
        self.remove_favorite_button = QPushButton('Remove from Favorites', self)
        self.remove_favorite_button.clicked.connect(self.remove_from_favorites)
        
        self.open_button = QPushButton('Open', self)
        self.open_button.clicked.connect(self.open_file)
        self.open_button.setEnabled(False)
        
        self.save_button = QPushButton('Save', self)
        self.save_button.clicked.connect(self.save_file)
        self.save_button.setEnabled(True)
        
        self.cancel_button = QPushButton('Cancel', self)
        self.cancel_button.clicked.connect(self.reject)
        
        # Customize buttons
        self.set_custom_button_style(self.add_favorite_button)
        self.set_custom_button_style(self.remove_favorite_button)
        self.set_custom_button_style(self.open_button)
        self.set_custom_button_style(self.save_button)
        self.set_custom_button_style(self.cancel_button)
        
        button_layout  = QVBoxLayout()
        #
        button1_layout = QHBoxLayout()
        button1_layout.addWidget(self.add_favorite_button)
        button1_layout.addWidget(self.remove_favorite_button)
        #
        button2_layout = QHBoxLayout()
        button2_layout.addWidget(self.open_button)
        button2_layout.addWidget(self.save_button)
        button2_layout.addWidget(self.cancel_button)
        #
        button_layout.addLayout(button1_layout)
        button_layout.addLayout(button2_layout)
        
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.path_input)
        right_layout.addWidget(self.filter_input)
        right_layout.addWidget(self.tree_view)
        right_layout.addWidget(self.file_list)
        right_layout.addWidget(self.label)
        right_layout.addLayout(button_layout)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        left_layout = QVBoxLayout()
        left_layout.addWidget(self.favorites_tree)
        left_layout.addWidget(self.drives_tree)
        left_layout.addWidget(self.project_tree)
        
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        hbox.addWidget(splitter)
        
        self.setLayout(hbox)
        self.setWindowTitle('Open .pro File')
        self.setGeometry(300, 300, 750, 450)
    
    def set_custom_button_style(self, button):
        button.setMinimumHeight(31)
        button.setFont(QFont(genv.v__app__font, 10))
    
    def set_custom_font(self, widget):
        widget.setFont(QFont(genv.v__app__font, 10))
    
    def set_custom_lineedit_style(self, lineedit):
        lineedit.setFont(QFont(genv.v__app__font_edit, 11))
    
    def load_favorites_from_ini(self):
        genv.v__app__config.read('favorites.ini')
        if 'Favorites' in genv.v__app__config:
            for name, path in genv.v__app__config['Favorites'].items():
                item = QTreeWidgetItem([name, path])
                self.favorites_tree.addTopLevelItem(item)
    
    def save_favorites_to_ini(self):
        genv.v__app__config['Favorites'] = {}
        for index in range(self.favorites_tree.topLevelItemCount()):
            item = self.favorites_tree.topLevelItem(index)
            genv.v__app__config['Favorites'][item.text(0)] = item.text(1)
        with open('favorites.ini', 'w') as configfile:
            genv.v__app__config.write(configfile)
    
    def load_drives(self):
        drives = [drive for drive in QDir.drives()]
        for drive in drives:
            total_size, available_space = self.get_drive_info(drive.absolutePath())
            item = QTreeWidgetItem([drive.absolutePath(), available_space, total_size])
            self.drives_tree.addTopLevelItem(item)
    
    def get_drive_info(self, drive):
        try:
            total, used, free = shutil.disk_usage(drive)
            return self.format_size(total), self.format_size(free)
        except Exception as e:
            return "N/A", "N/A"
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
    
    def on_drive_clicked(self, item):
        drive_path = item.text(0)
        self.path_input.setText(drive_path)
        
        self.project_tree.clear()
        self.file_list.clear()
        
        self.tree_view.setRootIndex(self.dir_model.index(drive_path))
    
    def save_file(self):
        return
    
    def on_project_clicked(self, item):
        file_name = item.text(0)
        file_path = os.path.join(item.text(1), file_name)
        
        self.path_input.setText(file_path)
        self.label.setText(f'Selected file: {file_name}')
        
        self.path_input.setText(file_path)
        self.update_file_list(file_path)
        
        self.tree_view.setRootIndex(self.dir_model.index(item.text(1)))
        return
    
    def on_tree_view_clicked(self, index):
        dir_path = self.dir_model.filePath(index)
        self.path_input.setText(dir_path)
        self.update_file_list(dir_path)
        
        files = os.listdir(dir_path)
        pro_files = []
        
        self.project_tree.clear()
        for file in files:
            if file.endswith(".pro"):
                if os.path.isfile(os.path.join(dir_path, file)):
                    item = QTreeWidgetItem([file, dir_path])
                    self.project_tree.addTopLevelItem(item)
        
    def update_project_files(self, dir_path):
        dir_path, file_name = os.path.split(dir_path)
        files = os.listdir(dir_path)
        pro_files = []
        
        self.project_tree.clear()
        for file in files:
            if file.endswith(".pro"):
                if os.path.isfile(os.path.join(dir_path, file)):
                    item = QTreeWidgetItem([file, dir_path])
                    self.project_tree.addTopLevelItem(item)
    
    def update_file_list(self, dir_path):
        dir_full = dir_path.replace("\\","/")
        dir_path, file_name = os.path.split(dir_full)
        #
        if dir_full.endswith(".pro"):
            self.file_list.clear()
            
            genv.v__app__config.read(dir_full)
            noan = "n/a"
            #
            self.project_file    = file_name
            self.project_name    = noan
            self.project_author  = noan
            self.project_version = noan
            self.project_email   = noan
            self.project_lastmod = noan
            #
            self.project_content_type     = noan
            self.project_content_encoding = noan
            self.project_mime_type        = noan
            self.project_language_team    = noan
            self.project_last_translater  = noan
            self.project_pot_create_date  = noan
            self.project_po_revision_date = noan
            
            genv.v__app__config.read(dir_full)
            pro = "project"
            #
            try:
                self.project_name = self.maxLength(genv.v__app__config[pro]["name"],126)
            except Exception as e:
                if e == 'name':
                    self.project_name = noan
                pass
            try:
                self.project_author = self.maxLength(genv.v__app__config[pro]["author"],64)
            except Exception as e:
                if e == 'author':
                    self.project_author = noan
                pass
            try:
                self.project_version = self.maxLength(genv.v__app__config[pro]["version"],32)
            except Exception as e:
                if e == 'version':
                    self.project_version = noan
                pass
            try:
                self.project_email = self.maxLength(genv.v__app__config[pro]["e-mail"],64)
            except Exception as e:
                if e == 'e-mail':
                    self.project_email = noan
                pass
            try:
                self.project_lastmod = self.maxLength(genv.v__app__config[pro]["lastmod"],32)
            except Exception as e:
                if e == 'lastmod':
                    self.project_lastmod = noan
                pass
            try:
                self.project_content_type = self.maxLength(genv.v__app__config[pro]["content-type"],32)
            except Exception as e:
                if e == 'content-type':
                    self.project_content_type = noan
                pass
            try:
                self.project_content_encoding = self.maxLength(genv.v__app__config[pro]["content-encoding"],32)
            except Exception as e:
                if e == 'content-encoding':
                    self.project_content_encoding = noan
                pass
            try:
                self.project_mime_type = self.maxLength(genv.v__app__config[pro]["mime-type"],32)
            except Exception as e:
                if e == 'mime-type':
                    self.project_mime_type = noan
                pass
            try:
                self.project_language_team = self.maxLength(genv.v__app__config[pro]["language-team"],32)
            except Exception as e:
                if e == 'language-team':
                    self.project_language_team = noan
                pass
            try:
                self.project_last_translater = self.maxLength(genv.v__app__config[pro]["last-translater"],32)
            except Exception as e:
                if e == 'last-translater':
                    self.project_last_translater = noan
                pass
            try:
                self.project_pot_create_date = self.maxLength(genv.v__app__config[pro]["pot-create-date"],32)
            except Exception as e:
                if e == 'pot-create-date':
                    self.project_pot_create_date = noan
                pass
            try:
                self.project_po_revision_date = self.maxLength(genv.v__app__config[pro]["po-revision-date"],32)
            except Exception as e:
                if e == 'po-revision-date':
                    self.project_po_revision_date = noan
                pass
            
            items = [
                ['Name', self.project_name],
                ['File', self.project_file],
                ['Author', self.project_author],
                ['Version', self.project_version],
                ['E-Mail', self.project_email],
                ['Last-Modified', self.project_lastmod],
                ['Content-Type', self.project_content_type],
                ['Content-Encoding', self.project_content_encoding],
                ['MIME-Type', self.project_mime_type],
                ['Language-Team', self.project_language_team],
                ['Last-Translater', self.project_last_translater],
                ['POT-Create-Date', self.project_pot_create_date],
                ['PO-Revision-Date', self.project_po_revision_date]
            ]
            for item in items:
                witem = QTreeWidgetItem([item[0], item[1]])
                self.file_list.addTopLevelItem(witem)
    
    def maxLength(self, input_string, length):
        if len(input_string) > length:
            msg = None
            msg = QMessageBox()
            msg.setWindowTitle("Information")
            msg.setText(
                "The maximal string exceeds valid length:\n"
                "maximum is: " + str(length) + "\n"+
                "Result string will is truncated !")
            msg.setIcon(QMessageBox.Information)
            btn_ok = msg.addButton(QMessageBox.Ok)
            
            msg.setStyleSheet(_("msgbox_css"))
            result = msg.exec_()
            return input_string[:length]
        else:
            return input_string
    
    def filter_files(self):
        filter_text = self.filter_input.text().lower()
        self.file_list.clear()
        filtered_files = [f for f in self.current_files if filter_text in f.lower()]
        for file in filtered_files:
            project_name = self.get_project_name(os.path.join(self.path_input.text(), file))
            item = None
            item = QTreeWidgetItem([file, project_name])
            self.file_list.addTopLevelItem(item)
    
    def get_project_name(self, file_path):
        genv.v__app__config.read(file_path)
        if 'Project' in genv.v__app__config and 'Name' in genv.v__app__config['Project']:
            return genv.v__app__config['Project']['Name']
        return "Unknown"
    
    # -----------------------------------------------------
    # right lower box - properties of locales .pro file(s).
    # -----------------------------------------------------
    def on_file_double_clicked(self, item):
        # ------------------------------------
        # .pro files shall not be changed ...
        # ------------------------------------
        if item.text(0).lower() == "file":
            msg = None
            msg = QMessageBox()
            msg.setWindowTitle("Information")
            msg.setText(
                "The locales project file name for the Application\n"
                "Can't be changed/rename !")
            msg.setIcon(QMessageBox.Information)
            btn_ok = msg.addButton(QMessageBox.Ok)
            
            msg.setStyleSheet(_("msgbox_css"))
            result = msg.exec_()
            return
        
        setting_dialog = None
        setting_dialog = setLocalesProjectSetting(self, item.text(0),item.text(1))
        setting_dialog.exec_()
        
        #print(self.property_name + " : " + self.property_value)
        
        if self.project_tree.currentItem == None:
            if not self.favorites_tree.currentItem == None:
                pro_name = self.favorites_tree.currentItem().text(0)
                pro_path = self.favorites_tree.currentItem().text(1)
            else:
                pro_name = self.project_tree.currentItem().text(0)
                pro_path = self.project_tree.currentItem().text(1)
        else:
            pro_name = self.favorites_tree.currentItem().text(0)
            pro_path = self.favorites_tree.currentItem().text(1)
        
        pro_file = pro_path.replace("\\", "/")
        
        # read try block
        try:
            genv.v__app__config.read(pro_file)
            #
            if self.property_name.lower() == "last-modified":
                self.property_name = "lastmod"
            #
            genv.v__app__config.set("project", self.property_name, self.property_value)
        except:
            msg = None
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText(
                "The locales project file for the Application\n"
                "Could not be read !")
            msg.setIcon(QMessageBox.Warning)
            btn_ok = msg.addButton(QMessageBox.Ok)
            
            msg.setStyleSheet(_("msgbox_css"))
            result = msg.exec_()
            msg = None
            pass
        # write try block
        try:
            with open(pro_file,"w") as configfile:
                genv.v__app__config.write(configfile)
                configfile.close()
                configfile = None
        except:
            msg = None
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText(
                "The locales project file for the Application\n"
                "Could not be saved !")
            msg.setIcon(QMessageBox.Warning)
            btn_ok = msg.addButton(QMessageBox.Ok)
            
            msg.setStyleSheet(_("msgbox_css"))
            result = msg.exec_()
            pass
        # read try block
        try:
            genv.v__app__config.read(pro_file)
            self.update_file_list(pro_file)
        except:
            msg = None
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText(
                "The locales project file for the Application\n"
                "Could not be read !")
            msg.setIcon(QMessageBox.Warning)
            btn_ok = msg.addButton(QMessageBox.Ok)
            
            msg.setStyleSheet(_("msgbox_css"))
            result = msg.exec_()
            pass
        #
        return
    
    def open_file(self):
        selected_file = self.label.text().replace('Selected file: ', '')
        if selected_file:
            print(f'Opening file: {selected_file}')
            self.accept()
        else:
            self.label.setText('No file selected.')
    
    def add_to_favorites(self):
        current_item = self.project_tree.currentItem()
        if current_item:
            file_name = current_item.text(0)
            file_path = os.path.join(current_item.text(1), file_name)
            item = QTreeWidgetItem([file_name, file_path])
            self.favorites_tree.addTopLevelItem(item)
            self.save_favorites_to_ini()
        else:
            self.add_favorite_button.setEnabled(False)
            self.remove_favorite_button.setEnabed(False)
    
    def remove_from_favorites(self):
        selected_items = self.favorites_tree.selectedItems()
        if selected_items:
            for item in selected_items:
                index = self.favorites_tree.indexOfTopLevelItem(item)
                if index != -1:
                    self.favorites_tree.takeTopLevelItem(index)
            self.save_favorites_to_ini()
    
    def on_favorite_double_clicked(self, item):
        dir_path = item.text(1)
        dir_path = dir_path.replace("\\", "/")
        #
        path, file_name = os.path.split(dir_path)
        
        self.path_input.setText(dir_path)
        self.update_file_list(dir_path)
        self.update_project_files(dir_path)
        
        self.tree_view.setRootIndex(self.dir_model.index(path))

class doubleClickLocalesLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("example.pro")
    
    def mouseDoubleClickEvent(self, event):
        self.on_lineedit_double_clicked()
        super().mouseDoubleClickEvent(event)
    
    def on_lineedit_double_clicked(self):
        dialog = None
        dialog = OpenProFileDialog(self)
        dialog.exec_()
        return

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

class CustomWidget1(QWidget):
    def __init__(self, parent_class):
        super().__init__()
        self.parent_class = parent_class
        self.initUI()
    
    def initUI(self):
        self.setFixedSize(42, 42)  # Set fixed size for the widget
    
    def mousePressEvent(self, event):
        file_path = ""
        if event.button() == Qt.LeftButton:
            msg = None
            msg = QMessageBox()
            msg.setWindowTitle("Confirmation")
            msg.setText(
                "The source file content will be overwrite if you choose YES !\n"
                "Would you save the current content ?")
            msg.setIcon(QMessageBox.Question)
            
            btn_yes = msg.addButton(QMessageBox.Yes)
            btn_no  = msg.addButton(QMessageBox.No)
            
            msg.setStyleSheet(_("msgbox_css"))
            result = msg.exec_()
            
            if result == QMessageBox.Yes:
                if self.parent_class.dbase_tabs_editor1.hasFocus():
                    file_path = os.path.join(genv.v__app__app_dir__, "examples/dbase/example1.prg")
                    file_path = file_path.replace("\\", "/")
                    #
                    with open(file_path, "w") as file:
                        file.write(self.parent_class.dbase_tabs_editor1.toPlainText())
                        file.close()
                elif self.parent_class.dbase_tabs_editor2.hasFocus():
                    file_path = os.path.join(genv.v__app__app_dir__, "examples/dbase/example2.prg")
                    file_path = file_path.replace("\\", "/")
                    #
                    with open(file_path) as file:
                        file.write(self.parent_class.dbase_tabs_editor2.toPlainText())
                        file.close()
                event.accept()
            else:
                event.ignore()
    
    def paintEvent(self, event):
        painter = None
        pixmap  = None
        
        painter = QPainter(self)
        pixmap  = QPixmap(os.path.join(genv.v__app__img__int__, "floppy-disk.png"))
        
        painter.drawPixmap(QRect(0, 0, self.width(), self.height()), pixmap)
        painter.end()

class CustomWidget0(QWidget):
    def __init__(self, parent_class):
        super().__init__()
        self.parent_class = parent_class
        self.initUI()
    
    def initUI(self):
        self.setFixedSize(42, 42)  # Set fixed size for the widget
        
        self.context_menu = None
        self.context_menu = QMenu(self)
        self.context_menu.setStyleSheet(_("css_menu_button"))
        
        self.action01 = None
        self.action02 = None
        self.action01 = QAction("./examples/dbase/Example1.prg\tdBASE ", self)
        self.action02 = QAction("./examples/dbase/Example2.prg\tdBASE ", self)
        #
        self.action11 = None
        self.action11 = QAction("./examples/pascal/Example1.prg\tPascal", self)
        #
        self.action21 = None
        self.action22 = None
        self.action21 = QAction("./examples/lisp/Example1.prg\tLISP  ", self)
        self.action22 = QAction("./examples/lisp/Example1.prg\tLISP  ", self)
        
        self.action01.triggered.connect(self.action01_triggered)
        self.action02.triggered.connect(self.action02_triggered)
        #
        self.action11.triggered.connect(self.action11_triggered)
        #
        self.action21.triggered.connect(self.action21_triggered)
        self.action22.triggered.connect(self.action22_triggered)
        
        self.context_menu.addAction(self.action01)
        self.context_menu.addAction(self.action02)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.action11)
        self.context_menu.addSeparator()
        self.context_menu.addAction(self.action21)
        self.context_menu.addAction(self.action22)
                
        pict = os.path.join(genv.v__app__img__int__, "arrowsmall.png")
        pixmpa = None
        pixmap = QPixmap(pict)
        
        self.arrow_button = None
        self.arrow_button = ClickableLabel(self)
        self.arrow_button.setPixmap(pixmap)
        self.arrow_button.resize(15, 42)
        self.arrow_button.setStyleSheet("background-color: transparent; border: none;")
        self.arrow_button.move(self.width() - 15, 0)
        self.arrow_button.clicked.connect(self.show_context_menu)
    
    def action01_triggered(self):
        self.interpreter = self.action01.text()[-6:]
        self.script_name = self.action01.text()[:-7]
        self.open_script(self.parent_class.dbase_tabs)
        return
    def action02_triggered(self):
        self.interpreter = self.action02.text()[-6:]
        self.script_name = self.action02.text()[:-7]
        self.open_script(self.parent_class.dbase_tabs)
        return
        
    def action11_triggered(self):
        self.interpreter = self.action11.text()[-6:]
        self.script_name = self.action11.text()[:-7]
        self.open_script(self.parent_class.pascal_tabs)
        return
        
    def action21_triggered(self):
        self.interpreter = self.action21.text()[-6:]
        self.script_name = self.action21.text()[:-7]
        self.open_script(self.parent_class.lisp_tabs)
        return
    def action22_triggered(self):
        self.interpreter = self.action22.text()[-6:]
        self.script_name = self.action22.text()[:-7]
        self.open_script(self.parent_class.lisp_tabs)
        return
    
    def open_script(self, tabser):
        self.parent_class.help_tabs.hide()
        self.parent_class.dbase_tabs.hide()
        self.parent_class.pascal_tabs.hide()
        self.parent_class.isoc_tabs.hide()
        self.parent_class.java_tabs.hide()
        self.parent_class.python_tabs.hide()
        self.parent_class.lisp_tabs.hide()
        self.parent_class.locale_tabs.hide()
        self.parent_class.c64_tabs.hide()
        #
        tabser.show()
        
        self.set_null_state()
        self.parent_class.side_btn1.set_style()
        #self.parent_class.set_style()
    
    def set_null_state(self):
        parent = self.parent_class
        side_buttons = [
            parent.side_btn1,
            parent.side_btn2,
            parent.side_btn3,
            parent.side_btn4,
            parent.side_btn5,
            parent.side_btn6,
            parent.side_btn7,
            parent.side_btn8,
            parent.side_btn9,
        ]
        for btn in side_buttons:
            btn.state = 0
            btn.set_style()
        return
        
    def show_context_menu(self):
        self.context_menu.exec_(self.mapToGlobal(self.arrow_button.pos()))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.open_dialog()
    
    def open_dialog(self):
        dialog = None
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Custom Dialog")
        dialog.setFixedSize(200, 150)
        
        layout = None
        label  = None
        
        layout = QVBoxLayout()
        label  = QLabel("This is a custom dialog", dialog)
        
        layout.addWidget(label)
        dialog.setLayout(layout)
        
        dialog.exec_()
        dialog = None
    
    def paintEvent(self, event):
        painter = None
        painter = QPainter(self)
        pixmap  = QPixmap(os.path.join(genv.v__app__img__int__, "open-folder.png"))
        painter.drawPixmap(QRect(0, 0, self.width(), self.height()), pixmap)
        painter.end()

class CustomWidget2(QWidget):
    def __init__(self, parent_class):
        super().__init__()
        self.parent_class = parent_class
        self.initUI()
    
    def initUI(self):
        self.setFixedSize(42, 42)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.parent_class.dbase_tabs_editor1.hasFocus():
                script_name = "./examples/dbase/example1.prg"
                if not os.path.exists(script_name):
                    print(f"Error: file does not exists: {script_name}.")
                    return
                
                prg = None
                prg = dBaseDSL(script_name)
                #prg.parser.parse()
                print("\nend of data")
                
                #prg.parser.run()
                #prg.parser.finalize()
                
            elif self.parent_class.dbase_tabs_editor2.hasFocus():
                script_name = "./examples/dbase/example2.prg"
                if not os.path.exists(script_name):
                    print(f"Error: file does not exists: {script_name}.")
                    return
                
                prg = None
                prg = dBaseDSL(script_name)
                #prg.parser.parse()
                print("\nend of data")
                
                #prg.parser.run()
                #prg.parser.finalize()
            else:
                print("no editor selected.")
    
    def paintEvent(self, event):
        painter = None
        painter = QPainter(self)
        pixmap  = QPixmap(os.path.join(genv.v__app__img__int__, "play.png"))
        painter.drawPixmap(QRect(0, 0, self.width(), self.height()), pixmap)
        painter.end()

class FileWatcherGUI(QDialog):
    def __init__(self):
        super().__init__()
        
        genv.css_menu_item_style  = _("css_menu_item_style")
        genv.css_menu_label_style = _("css_menu_label_style")
        genv.css_menu_item        = _("css_menu_item")
        
        self.font = QFont(genv.v__app__font, 10)
        self.setFont(self.font)
        self.setContentsMargins(0,0,0,0)
        self.setStyleSheet("padding:0px;margin:0px;")
        #self.setStyleSheet("font-family:'Arial';font-size:12pt;")
        
        self.worker_hasFocus = False
        
        self.my_list = MyItemRecord(0, QStandardItem(""))
        self.init_ui()
            
    # --------------------
    # dialog exit ? ...
    # --------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F1:
            help_chm = "help.chm"
            if os.path.exists(help_chm):
                os.startfile(help_chm)
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Warnin")
                msg.setText(
                    "The help file for  the Application\n"
                    "Could not be found !")
                msg.setIcon(QMessageBox.Warning)
                
                btn_ok = msg.addButton(QMessageBox.Ok)
                
                msg.setStyleSheet(_("msgbox_css"))
                result = msg.exec_()
        
        elif event.key() == Qt.Key_Escape:
            exitBox = myExitDialog(_("Exit Dialog"))
            exitBox.exec_()
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.worker_hasFocus == True:
                # c64
                print("xxx")
        else:
            super().keyPressEvent(event)
    
    def menu_help_clicked_about(self):
        QMessageBox.information(self,
        "About...",
        "This is HelpNDoc.com FileChecker v.0.0.1\n" +
        "(c) 2024 by Jens Kallup - paule32\n" +
        "all rights reserved.")
        return
    
    def menu_edit_clicked_clearall(self):
        return
    
    def tab0_file_tree_clicked(self, index):
        self.tab0_path = self.tab0_dir_model.fileInfo(index).absoluteFilePath()
        self.tab0_file_list.setRootIndex(self.tab0_file_model.setRootPath(self.tab0_path))
        return
    
    def tab1_file_tree_clicked(self, index):
        self.tab1_path = self.tab1_dir_model.fileInfo(index).absoluteFilePath()
        self.tab1_file_list.setRootIndex(self.tab1_file_model.setRootPath(self.tab1_path))
        return
    
    def tab0_file_list_clicked(self, index):
        self.tab0_path_file = self.tab0_dir_model.fileInfo(index).absoluteFilePath()
        print("---> " + self.tab0_path_file)
        return
    
    def tab1_file_list_clicked(self, index):
        self.tab1_path_file = self.tab1_dir_model.fileInfo(index).absoluteFilePath()
        self.tab1_path_lineEdit.setText(f"{self.tab1_path_file}")
        return
    
    def populate_tree_view(self, file_path, icon):
        with open(file_path, 'r') as file:
            roots = []
            stack = [self.tab2_tree_model.invisibleRootItem()]
            
            self.topic_counter = 1
            
            for line in file:
                line = line.rstrip('\n')
                num_plus = 0
                while line[num_plus] == '+':
                    num_plus += 1
                
                item_name = line.strip('+').strip()
                
                new_item = QStandardItem(item_name)
                new_item.setIcon(QIcon(icon))
                
                global item2
                item1 = QStandardItem(str(self.topic_counter))
                item2 = QStandardItem(" ") #item2.setIcon(QIcon(icon))
                item3 = QStandardItem(" ")
                item4 = QStandardItem(" ")
                
                self.my_list.add(self.topic_counter, item1)
                
                self.topic_counter = self.topic_counter + 1
                
                while len(stack) > num_plus + 1:
                    stack.pop()
                
                stack[-1].appendRow([new_item, item1, item2, item3, item4])
                stack.append(new_item)
                
    
    def add_tree_item(self, parent_item, item_name):
        new_item = QStandardItem(item_name)
        parent_item.appendRow(new_item)
    
    def helpMenuClicked_about(self):
        print("about")
        return
    
    def menu_file_clicked_new(self):
        return
    def menu_file_clicked_open(self):
        return
    def menu_file_clicked_save(self):
        return
    def menu_file_clicked_saveas(self):
        return
    def menu_file_clicked_exit(self):
        return
    def menu_edit_clicked_undo(self):
        return
    def menu_edit_clicked_redo(self):
        return
    def menu_edit_clicked_clearall(self):
        return
    
    # --------------------------------------------------------------------
    # add sub menu item to the menuBar menu item.
    # --------------------------------------------------------------------
    def add_menu_item(self, name, shortcut, menu, callback):
        self.menu_action = QWidgetAction(menu)
        
        self.menu_widget = QWidget()
        self.menu_layout = QHBoxLayout(self.menu_widget)
        self.menu_layout.setContentsMargins(0,0,0,0)
        #
        self.menu_icon = QWidget()
        self.menu_icon.setFixedWidth(26)
        self.menu_icon.setContentsMargins(0,0,0,0)
        #
        self.menu_label = QLabel(name)
        self.menu_label.setContentsMargins(0,0,0,0)
        self.menu_label.setStyleSheet(genv.css_menu_label_style)
        self.menu_label.setMinimumWidth(160)
        #
        self.menu_shortcut = QLabel(shortcut)
        self.menu_shortcut.setContentsMargins(0,0,0,0)
        self.menu_shortcut.setMinimumWidth(100)
        self.menu_shortcut.setStyleSheet(genv.css_menu_item)
        
        self.menu_layout.addWidget(self.menu_icon)
        self.menu_layout.addWidget(self.menu_label)
        self.menu_layout.addWidget(self.menu_shortcut)
        
        self.menu_action.setDefaultWidget(self.menu_widget)
        self.menu_action.triggered.connect(callback)
        
        menu.addAction(self.menu_action)
        return
        
    def init_ui(self):
        # mouse tracking
        self.setMouseTracking(True)
        # Layout
        #self.setMaximumWidth (1024)
        self.setMinimumWidth (1200)
        #
        #self.setMaximumHeight(730)
        #self.setMaximumHeight(730)
        
        self.setContentsMargins(0,0,0,0)
        self.setStyleSheet("padding:0px;margin:0px;")
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        
        # menu bar
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setStyleSheet(genv.css_menu_item_style)
        
        self.menu_style_bg = "background-color:navy;"
        menu_list = [
            ["&File",
                [
                    ["New"       , "Ctrl+N", self.menu_file_clicked_new   ],
                    ["Open"      , "Ctrl+O", self.menu_file_clicked_open  ],
                    ["Save"      , "Ctrl+S", self.menu_file_clicked_save  ],
                    ["Save As...", ""      , self.menu_file_clicked_saveas],
                    ["Exit"      , "Ctrl+X", self.menu_file_clicked_exit  ]
                ]
            ],
            ["&Edit",
                [
                    ["Undo"     , ""      , self.menu_edit_clicked_undo     ],
                    ["Redo"     , ""      , self.menu_edit_clicked_redo     ],
                    ["Clear All", "Ctrl+0", self.menu_edit_clicked_clearall ]
                ]
            ],
            ["&Help",
                [
                    ["About...", "F1", self.menu_help_clicked_about ]
                ]
            ]
        ]
        for item in menu_list:
            name = item[0]; menu = item[1]
            mbar = self.menu_bar.addMenu(name)
            mbar.setStyleSheet(self.menu_style_bg)
            for menu_item in menu:
                subs = menu_item
                self.add_menu_item(subs[0], subs[1], mbar, subs[2])
        
        self.layout.addWidget( self.menu_bar )
        self.menu_bar.show()
        
        # tool bar
        self.tool_bar = QToolBar()
        self.tool_bar.setContentsMargins(0,0,0,0)
        self.tool_bar.setStyleSheet(_("toolbar_css"))
        
        self.tool_bar_button_exit = QToolButton()
        self.tool_bar_button_exit.setText("Clear")
        self.tool_bar_button_exit.setCheckable(True)
        
        self.tool_bar_action_new1 = QAction(QIcon(os.path.join(genv.v__app__img__int__, "floppy-disk" + genv.v__app__img_ext__)), "Flopp", self)
        self.tool_bar_action_new2 = QAction(QIcon(os.path.join(genv.v__app__img__int__, "floppy-disk" + genv.v__app__img_ext__)), "Flopp", self)
        self.tool_bar_action_new3 = QAction(QIcon(os.path.join(genv.v__app__img__int__, "floppy-disk" + genv.v__app__img_ext__)), "Flopp", self)
        
        self.tool_bar.addAction(self.tool_bar_action_new1)
        self.tool_bar.addAction(self.tool_bar_action_new2)
        self.tool_bar.addAction(self.tool_bar_action_new3)
        
        self.tool_bar.addWidget(self.tool_bar_button_exit)
        
        self.layout.addWidget(self.tool_bar)
        self.tool_bar.show()
        
        # status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready", 0)
        self.status_bar.setStyleSheet("background-color:gray;")
        
        
        # side toolbar
        self.main_layout = QHBoxLayout()
        self.main_widget = QWidget()
        
        self.main_widget.setContentsMargins(0,0,0,0)
        self.main_widget.setStyleSheet("padding:0px;margin:0px;")
        
        
        self.side_scroll = QScrollArea()
        self.side_widget = QWidget()
        self.side_layout = QVBoxLayout()
        #
        self.side_widget.setContentsMargins(0,0,0,0)
        self.side_scroll.setContentsMargins(0,0,0,0)
        
        self.side_btn1 = myIconButton(self,  0, "Help"   , "Help Authoring for/with:\no doxygen\no HelpNDoc")
        self.side_btn2 = myIconButton(self,  1, "dBASE"  , "dBASE data base programming\nlike in the old days...\nbut with SQLite -- dBase keep alive !")
        self.side_btn3 = myIconButton(self,  2, "Pascal" , "Pascal old school programming\no Delphi\no FPC")
        self.side_btn4 = myIconButton(self,  3, "ISO C"  , "C / C++ embeded programming\nor cross platform")
        self.side_btn5 = myIconButton(self,  4, "Java"   , "Java modern cross programming\nfor any device")
        self.side_btn6 = myIconButton(self,  5, "Python" , "Python modern GUI programming\nlets rock AI\nand TensorFlow")
        self.side_btn7 = myIconButton(self,  6, "LISP"   , "LISP traditional programming\nultimate old school")
        #
        self.side_btn8 = myIconButton(self, 10, "Locales", "" \
            + "Localization your Application with different supported languages\n" \
            + "around the World.\n" \
            + "Used tools are msgfmt - the Unix Tool for generationg .mo files.\n")
        #
        self.side_btn9 = myIconButton(self,  11, "C-64", "The most popular Commodore C-64\from int the 1980er")
        
        
        self.side_btn1.bordercolor = "lime"
        self.side_btn1.state       = 2
        self.side_btn1.set_style()
        
        self.side_widget.setMaximumWidth(120)
        self.side_widget.setLayout(self.side_layout)
        
        self.side_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.side_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.side_scroll.setWidgetResizable(True)
        self.side_scroll.setMinimumWidth(130)
        self.side_scroll.setMaximumWidth(130)
        self.side_scroll.setWidget(self.side_widget)
        
        ####
        self.main_layout.addWidget(self.side_scroll)
        
        
        self.handleDBase()
        self.handlePascal()
        self.handleIsoC()
        self.handleJava()
        self.handlePython()
        self.handleLISP()
        self.handleLocales()
        self.handleCommodoreC64()
        
        
        
        # first register card - action's ...
        self.help_tabs = QTabWidget()
        self.help_tabs.setStyleSheet(css_tabs)
        
        # help
        self.tab0_0 = QWidget()
        self.tab1_0 = QWidget()
        self.tab2   = QWidget()
        self.tab3   = QWidget()
        self.tab4   = QWidget()
        
        # add tabs
        self.help_tabs.addTab(self.tab0_0, "Help Project")
        self.help_tabs.addTab(self.tab1_0, "Pre-/Post Actions")
        self.help_tabs.addTab(self.tab2, "Topics")
        self.help_tabs.addTab(self.tab3, "DoxyGen")
        self.help_tabs.addTab(self.tab4, "Content")
        
        self.tab_widget_tabs = QTabWidget(self.tab4)
        self.tab_widget_tabs.setMinimumWidth(830)
        self.tab_widget_tabs.setMinimumHeight(650)
        self.tab_dbase  = QWidget()
        self.tab_pascal = QWidget()
        self.tab_html   = QWidget()
        self.tab_widget_tabs.addTab(self.tab_dbase , "dBase" )
        self.tab_widget_tabs.addTab(self.tab_pascal, "Pascal")
        self.tab_widget_tabs.addTab(self.tab_html  , "HTML"  )
        
        
        self.tab_dbase_layout = QVBoxLayout(self.tab_dbase)
        self.tab_dbase_layout.setAlignment(Qt.AlignTop)
        self.tab_dbase_editor = myDBaseTextEditor(self)
        self.tab_dbase_layout.addWidget(self.tab_dbase_editor)
        
        #
        self.main_layout.addWidget(self.help_tabs)
        
        self.tab_html.setMinimumWidth(500)
        self.tab_html.setMaximumHeight(500)
        
        # create project tab
        self.tab2_top_layout = QHBoxLayout(self.tab2)
        self.tab3_top_layout = QHBoxLayout(self.tab3)
        self.tab4_top_layout = QHBoxLayout(self.tab_widget_tabs)
        self.tab5_top_layout = QHBoxLayout(self.tab_html)
        
        ####
        # devices
        font = QFont(genv.v__app__font,14)
        font.setBold(True)
        
        ####
        self.devices_scroll = QScrollArea()
        self.devices_widget = QWidget()
        self.devices_layout = QVBoxLayout()
        
        #
        self.devices_scroll.setMinimumWidth(240)
        self.devices_scroll.setMaximumWidth(240)
        #
        self.devices_widget.setMinimumWidth(240)
        self.devices_widget.setMaximumWidth(240)
        #
        self.devices_widget.setContentsMargins(1,0,0,1)
        self.devices_layout.setContentsMargins(1,0,0,1)
        
        self.devices_label_printers = QPushButton("  Printers:  ")
        self.devices_label_printers.setMinimumWidth(240)
        self.devices_label_printers.setMaximumWidth(240)
        self.devices_label_printers.setFont(font)
        self.devices_layout.addWidget(self.devices_label_printers)
        #
        self.devices_list_printers = QListWidget()
        self.devices_list_printers.setIconSize(QSize(40,40))
        self.devices_list_printers.setFont(font)
        self.devices_layout.addWidget(self.devices_list_printers)
        
        #
        items = [
            {"text": "Printer p:1", "icon": os.path.join(genv.v__app__img__int__, "printer" + genv.v__app__img_ext__) },
            {"text": "Printer p:2", "icon": os.path.join(genv.v__app__img__int__, "printer" + genv.v__app__img_ext__) },
            {"text": "Printer p:3", "icon": os.path.join(genv.v__app__img__int__, "printer" + genv.v__app__img_ext__) }
        ]
        for item in items:
            devices_list_item = QListWidgetItem(item["text"])
            devices_list_item.setIcon(QIcon(item["icon"]))
            self.devices_list_printers.addItem(devices_list_item)
        #
        
        
        self.devices_tabs_storages = QPushButton()
        self.devices_tabs_storages.setText("  Storages:  ")
        self.devices_tabs_storages.setFont(font)
        self.devices_layout.addWidget(self.devices_tabs_storages)
        #
        self.devices_list_storages = QListWidget()
        self.devices_list_storages.move(0,264)
        self.devices_list_storages.setIconSize(QSize(40,40))
        self.devices_list_storages.setFont(font)
        self.devices_layout.addWidget(self.devices_list_storages)
        #
        items = [
            {"text": "Storage  s:1", "icon": os.path.join(genv.v__app__img__int__, "storage"  + genv.v__app__img_ext__) },
            {"text": "Database d:2", "icon": os.path.join(genv.v__app__img__int__, "database" + genv.v__app__img_ext__) },
            {"text": "Database d:3", "icon": os.path.join(genv.v__app__img__int__, "database" + genv.v__app__img_ext__) }
        ]
        for item in items:
            devices_list_item = QListWidgetItem(item["text"])
            devices_list_item.setIcon(QIcon(item["icon"]))
            self.devices_list_storages.addItem(devices_list_item)
        #
        
        
        self.devices_tabs_label3 = QPushButton()
        self.devices_tabs_label3.setText("  Team Server:  ")
        self.devices_tabs_label3.setFont(font)
        self.devices_layout.addWidget(self.devices_tabs_label3)
        #
        self.devices_list_widget3 = QListWidget()
        self.devices_list_widget3.setMaximumHeight(100)
        self.devices_list_widget3.setIconSize(QSize(40,40))
        self.devices_list_widget3.setFont(font)
        self.devices_layout.addWidget(self.devices_list_widget3)
        #
        items = [
            {"text": "Meeting m:1", "icon": os.path.join(genv.v__app__img__int__, "meeting" + genv.v__app__img_ext__) },
            {"text": "Session c:2", "icon": os.path.join(genv.v__app__img__int__, "session" + genv.v__app__img_ext__) }
        ]
        for item in items:
            devices_list_item = QListWidgetItem(item["text"])
            devices_list_item.setIcon(QIcon(item["icon"]))
            self.devices_list_widget3.addItem(devices_list_item)
        #
        
        self.devices_widget.setLayout(self.devices_layout)
        
        self.devices_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.devices_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.devices_scroll.setWidgetResizable(True)
        self.devices_scroll.setLayout(self.devices_layout)
        #
        #
        self.dl = QVBoxLayout()
        self.dl.setContentsMargins(1,0,0,1)
        self.dl.addWidget(self.devices_scroll)
        ####
        self.main_layout.addLayout(self.dl)
        
        ################
        ##self.tab1_layout = QHBoxLayout()
        ##self.tab1_widget = QWidget()
        
        self.widget_font = QFont(genv.v__app__font, 12)
        self.widget_font.setBold(True)
        
        self.tab_widget_1 = QTabWidget()
        
        tab_1 = QWidget()
        tab_2 = QWidget()
        tab_3 = QWidget()
        
        tab_1.setFont(self.widget_font)
        tab_2.setFont(self.widget_font)
        tab_3.setFont(self.widget_font)
        
        self.tab_widget_1.addTab(tab_1, "Wizard")
        self.tab_widget_1.addTab(tab_2, "Expert")
        self.tab_widget_1.addTab(tab_3, "Run")
        
        list_layout_a = QVBoxLayout(tab_1)
        
        list_layout_1 = QHBoxLayout()
        list_widget_1 = QListWidget()
        
        list_layout_a.addLayout(list_layout_1)
        
        list_widget_1.setFocusPolicy(Qt.NoFocus)
        list_widget_1.setStyleSheet(css__widget_item)
        list_widget_1.setMinimumHeight(300)
        list_widget_1.setMaximumWidth(200)
        self.list_widget_1_elements = ["Project", "Mode", "Output", "Diagrams" ]
        #
        #
        for element in self.list_widget_1_elements:
            list_item = customQListWidgetItem(element, list_widget_1)
        
        list_widget_1.setCurrentRow(0)
        list_widget_1.itemClicked.connect(self.handle_item_click)
        list_layout_1.addWidget(list_widget_1)
        
        self.sv_1_1 = customScrollView_1("Project")
        self.sv_1_2 = customScrollView_2("Mode");     self.sv_1_2.hide()
        self.sv_1_3 = customScrollView_3("Output");   self.sv_1_3.hide()
        self.sv_1_4 = customScrollView_4("Diagrams"); self.sv_1_4.hide()
        
        for i in range(1, 5):
            s = "sv_1_" + str(i)
            list_layout_1.addWidget(getattr(self, f"{s}"))
        
        # progress bar
        self.lv_1 = QVBoxLayout()
        self.hw_1 = QWidget()
        
        hlp = customScrollView_help()
        bar = QProgressBar()
        bar.setTextVisible(False)
        #
        bar.setMinimum(1)
        bar.setMaximum(100)
        #
        bar.setValue(18)
        
        self.lv_1.addWidget(hlp)
        self.lv_1.addWidget(bar)
        
        list_layout_a.addLayout(self.lv_1)
        ########################
        list_layout_b = QVBoxLayout(tab_2)
        
        list_layout_2 = QHBoxLayout()
        list_widget_2 = QListWidget()
        
        list_layout_b.addLayout(list_layout_2)
        
        list_widget_2.setFocusPolicy(Qt.NoFocus)
        list_widget_2.setStyleSheet(css__widget_item)
        list_widget_2.setMinimumHeight(300)
        list_widget_2.setMaximumWidth(200)
        self.list_widget_2_elements = [                                     \
            "Project", "Build", "Messages", "Input", "Source Browser",      \
            "Index", "HTML", "LaTeX", "RTF", "Man", "XML", "DocBook",       \
            "AutoGen", "SQLite3", "PerlMod", "Preprocessor", "External",    \
            "Dot" ]
        #
        #
        for element in self.list_widget_2_elements:
            list_item = customQListWidgetItem(element, list_widget_2)
        
        list_widget_2.setCurrentRow(0)
        list_widget_2.itemClicked.connect(self.handle_item_click)
        list_layout_2.addWidget(list_widget_2)
        
        tab1_classes = []
        i = 5
        while i < 23:
            s = "customScrollView_" + str(i)
            i = i + 1
            tab1_classes.append(s)
        
        objs = []
        i    = 0
        for item in tab1_classes:
            s = "sv_2_" + str(i+1)
            v1 = eval(item+"('')")
            v1.setName(self.list_widget_2_elements[i])
            objs.append(v1)
            setattr(self, s, v1)
            list_layout_2.addWidget(v1)
            v1.hide()
            i += 1
        
        self.sv_2_1.show()
        self.hw_2 = QWidget()
        
        list_layout_b.addWidget(sv_help)
        ########################
        self.tab3_top_layout.addWidget(self.tab_widget_1)
        
        
        self.tab2_file_path = os.path.join(genv.v__app__internal__, "topics.txt")
        
        global tab2_tree_view
        tab2_tree_view = QTreeView()
        tab2_tree_view.setStyleSheet(_(css_model_header))
        self.tab2_tree_model = QStandardItemModel()
        self.tab2_tree_model.setHorizontalHeaderLabels(["Topic name", "ID", "Status", "Help icon", "In Build"])
        tab2_tree_view.setModel(self.tab2_tree_model)
        
        self.tab2_top_layout.addWidget(tab2_tree_view)
        self.populate_tree_view(self.tab2_file_path, os.path.join(genv.v__app__img__int__, "open-folder" + genv.v__app__img_ext__))
        
        self.delegateID     = SpinEditDelegateID     (tab2_tree_view)
        self.delegateStatus = ComboBoxDelegateStatus (tab2_tree_view)
        self.delegateIcon   = ComboBoxDelegateIcon   (tab2_tree_view)
        self.delegateBuild  = ComboBoxDelegateBuild  (tab2_tree_view)
        
        tab2_tree_view.setItemDelegateForColumn(1, self.delegateID)
        tab2_tree_view.setItemDelegateForColumn(2, self.delegateStatus)
        tab2_tree_view.setItemDelegateForColumn(3, self.delegateIcon)
        tab2_tree_view.setItemDelegateForColumn(4, self.delegateBuild)
        
        #self.tab2_top_layout.
        
        
        # create project tab
        self.tab0_top_layout    = QHBoxLayout(self.tab0_0)
        self.tab0_left_layout   = QVBoxLayout()
        
        #
        self.tab0_topV_vlayout = QVBoxLayout()
        #
        self.tab0_topA_hlayout = QHBoxLayout()
        self.tab0_topB_hlayout = QHBoxLayout()
        self.tab0_topC_hlayout = QHBoxLayout()
        self.tab0_topD_hlayout = QHBoxLayout()
        #
        self.tab0_topA_hlayout = QHBoxLayout()
        self.tab0_topA_vlayout = QVBoxLayout()
        #
        self.tab0_topB_hlayout = QHBoxLayout()
        self.tab0_topB_vlayout = QVBoxLayout()
        #
        self.tab0_top0_vlayout = QVBoxLayout()
        #
        self.tab0_top1_vlayout = QVBoxLayout()
        self.tab0_top2_vlayout = QVBoxLayout()
        #
        self.tab0_top1_hlayout = QHBoxLayout()
        self.tab0_top2_hlayout = QHBoxLayout()
        #
        #
        self.tab0_top1_vlayout.setAlignment(Qt.AlignTop)
        self.tab0_top2_vlayout.setAlignment(Qt.AlignTop)
        #
        self.tab0_topA_vlayout.setAlignment(Qt.AlignTop)
        self.tab0_topB_vlayout.setAlignment(Qt.AlignTop)
        #
        #
        font = QFont(genv.v__app__font, 11)
        font.setPointSize(11)
        #
        self.tab0_fold_text1 = QLabel("Directory:")
        self.tab0_fold_text1.setMaximumWidth(84)
        self.tab0_fold_text1.setFont(font)
        
        self.tab0_fold_edit1 = myLineEdit()
        self.tab0_fold_edit1.returnPressed.connect(self.tab0_fold_edit1_return)
        
        self.tab0_fold_push1 = MyEllipseButton(font)
        self.tab0_fold_userd = QDir.homePath()
        
        if (self.tab0_fold_userd[1:1] == ":") or (":" in self.tab0_fold_userd):
            self.tab0_fold_userd = ("/" +
            self.tab0_fold_userd[0:1]   +
            self.tab0_fold_userd[2:])
        
        self.tab0_fold_push1.clicked.connect(self.tab0_fold_push1_clicked)
        self.tab0_fold_edit1.setFont(font)
        self.tab0_fold_edit1.setText(self.tab0_fold_userd)
        
        self.tab0_fold_scroll1 = QScrollArea()
        self.tab0_fold_scroll1.setMinimumWidth(300)
        self.tab0_fold_scroll1.setMaximumWidth(300)
        self.tab0_fold_push11  = MyPushButton("Create", 1)
        self.tab0_fold_push12  = MyPushButton("Open"  , 2)
        self.tab0_fold_push13  = MyPushButton("Repro" , 3)
        self.tab0_fold_push14  = MyPushButton("Build" , 4)
        #
        self.tab0_fold_text2   = QLabel("Project-Name:")
        self.tab0_fold_text2.setMaximumWidth(84)
        self.tab0_fold_text2.setFont(font)
        self.tab0_fold_edit2   = myLineEdit()
        self.tab0_fold_push2   = MyEllipseButton(font)
        
        self.tab0_fold_scroll2 = QScrollArea()
        self.tab0_fold_scroll2.setMaximumWidth(300)
        self.tab0_fold_push21  = MyPushButton("Create", 1)
        self.tab0_fold_push22  = MyPushButton("Open"  , 2)
        self.tab0_fold_push23  = MyPushButton("Repro" , 3)
        self.tab0_fold_push24  = MyPushButton("Build" , 4)
        
        #
        self.tab0_top1_hlayout.addWidget(self.tab0_fold_text1)
        self.tab0_top1_hlayout.addWidget(self.tab0_fold_edit1)
        self.tab0_top1_hlayout.addWidget(self.tab0_fold_push1)
        #
        #
        self.tab0_top2_hlayout.addWidget(self.tab0_fold_text2)
        self.tab0_top2_hlayout.addWidget(self.tab0_fold_edit2)
        self.tab0_top2_hlayout.addWidget(self.tab0_fold_push2)
        #
        #
        self.tab0_topA_vlayout.addWidget(self.tab0_fold_push11)
        self.tab0_topA_vlayout.addWidget(self.tab0_fold_push12)
        self.tab0_topA_vlayout.addWidget(self.tab0_fold_push13)
        self.tab0_topA_vlayout.addWidget(self.tab0_fold_push14)
        self.tab0_topA_hlayout.addWidget(self.tab0_fold_scroll1)
        #
        self.tab0_topC_hlayout.addLayout(self.tab0_topA_vlayout)
        self.tab0_topC_hlayout.addLayout(self.tab0_topA_hlayout)
        #
        self.tab0_topB_vlayout.addWidget(self.tab0_fold_push21)
        self.tab0_topB_vlayout.addWidget(self.tab0_fold_push22)
        self.tab0_topB_vlayout.addWidget(self.tab0_fold_push23)
        self.tab0_topB_vlayout.addWidget(self.tab0_fold_push24)
        self.tab0_topB_hlayout.addWidget(self.tab0_fold_scroll2)
        #
        self.tab0_topD_hlayout.addLayout(self.tab0_topB_vlayout)
        self.tab0_topD_hlayout.addLayout(self.tab0_topB_hlayout)
        #
        self.tab0_top0_vlayout.addLayout(self.tab0_topC_hlayout)
        self.tab0_top0_vlayout.addLayout(self.tab0_topD_hlayout)
        #
        self.tab0_topV_vlayout.addLayout(self.tab0_top1_hlayout)
        self.tab0_topV_vlayout.addLayout(self.tab0_top0_vlayout)
        self.tab0_topV_vlayout.addLayout(self.tab0_top2_hlayout)
        self.tab0_topV_vlayout.addLayout(self.tab0_top0_vlayout)
        #
        #
        self.tab0_fold_scroll1_contentWidget = QWidget()
        #self.tab0_fold_scroll1_contentWidget.setGeometry(QRect(10,10,297,235))
        #self.tab0_fold_scroll1_contentWidget.setStyleSheet("background-color:gray;")
        #
        #
        #
        self.tab0_fold_scroll2_contentWidget = QWidget()
        #self.tab0_fold_scroll2_contentWidget.setGeometry(QRect(10,10,297,235))
        #self.tab0_fold_scroll2_contentWidget.setStyleSheet("background-color:gray;")
        #
        self.tab0_fold_scroll1.setWidget(self.tab0_fold_scroll1_contentWidget)
        self.tab0_fold_scroll2.setWidget(self.tab0_fold_scroll2_contentWidget)
        #
        #
        self.img_scroll1_layout = QVBoxLayout(self.tab0_fold_scroll1)
        self.img_scroll1_layout.addWidget(self.tab0_fold_scroll1)
        #
        global img_doxygen
        global img_hlpndoc
        #
        img_doxygen = doxygenImageTracker ()
        img_hlpndoc = helpNDocImageTracker()
        #
        #
        self.img_scroll1_layout.addWidget(img_doxygen)
        self.img_scroll1_layout.addWidget(img_hlpndoc)
        #
        self.img_scroll2_layout = QGridLayout(self.tab0_fold_scroll2)
        #
        #self.img_scroll2_layout.addWidget(self.tab0_fold_scroll2)
        #
        
        global img_ccpplus
        global img_javadoc
        global img_freepas
        #
        img_ccpplus = ccpplusImageTracker()
        img_javadoc = javadocImageTracker()
        img_freepas = freepasImageTracker()
        #
        #
        self.img_scroll2_layout.addWidget(img_ccpplus, 0, 0)
        self.img_scroll2_layout.addWidget(img_javadoc, 0, 1)
        self.img_scroll2_layout.addWidget(img_freepas, 2, 0, 1, 2)
        #
        #
        self.tab0_top_layout.addLayout(self.tab0_topV_vlayout)
        
        
        self.tab0_file_text = QLabel("File:", self.tab0_0)
        
        self.tab0_left_layout.addWidget(self.tab0_file_text)
        self.tab0_path = QDir.homePath()
        
        self.tab0_dir_model = QFileSystemModel()
        self.tab0_dir_model.setRootPath(self.tab0_path)
        self.tab0_dir_model.setFilter(QDir.NoDotAndDotDot | QDir.Dirs)
        
        self.tab0_file_model = QFileSystemModel()
        self.tab0_file_model.setNameFilters(['*.pro'])
        self.tab0_file_model.setNameFilterDisables(False)
        self.tab0_file_model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        
        
        self.tab0_file_tree = QTreeView()
        self.tab0_file_list = QListView()
        
        self.tab0_file_tree.setStyleSheet(_(css_model_header))
        
        self.tab0_file_tree.setModel(self.tab0_dir_model)
        self.tab0_file_list.setModel(self.tab0_file_model)
        
        self.tab0_file_tree.setRootIndex(self.tab0_dir_model.index(self.tab0_path))
        self.tab0_file_list.setRootIndex(self.tab0_file_model.index(self.tab0_path))
        ###
        # Kontextmenü für QTreeView verbinden
        self.tab0_file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab0_file_tree.customContextMenuRequested.connect(self.openContextMenuTreeView)
        
        self.tab0_help_list   = QListWidget()
        self.tab0_help_list.setMinimumWidth(260)
        self.tab0_help_list.setIconSize(QSize(34,34))
        self.tab0_help_list.setFont(QFont(genv.v__app__font, 12))
        self.tab0_help_list.font().setBold(True)
        
        liste = [
            ["Empty Project"         , os.path.join("emptyproject" + genv.v__app__img_ext__) ],
            ["Recipe"                , os.path.join("recipe"       + genv.v__app__img_ext__) ],
            ["API Project"           , os.path.join("api"          + genv.v__app__img_ext__) ],
            ["Software Documentation", os.path.join("software"     + genv.v__app__img_ext__) ],
        ]
        for item in liste:
            self.list_item1 = QListWidgetItem(_(item[0]),self.tab0_help_list)
            self.list_item1.setIcon(QIcon(os.path.join(genv.v__app__img__int__, item[1])))
            self.list_item1.setFont(self.tab0_help_list.font())
        
        self.tab0_help_layout = QHBoxLayout()
        self.tab0_help_layout.addWidget(self.tab0_file_list)
        self.tab0_help_layout.addWidget(self.tab0_help_list)
        
        self.tab0_left_layout.addWidget(self.tab0_file_tree)
        self.tab0_left_layout.addWidget(self.tab0_file_text)
        self.tab0_left_layout.addLayout(self.tab0_help_layout)
        
        self.tab0_file_tree.clicked.connect(self.tab0_file_tree_clicked)
        self.tab0_file_list.clicked.connect(self.tab0_file_list_clicked)
        
        
        #####
        # help templates
        
        
        # create action tab
        self.tab1_top_layout    = QHBoxLayout(self.tab1_0)
        self.tab1_left_layout   = QVBoxLayout()
        self.tab1_middle_layout = QVBoxLayout()
        self.tab1_right_layout  = QVBoxLayout()
        
        # ------------------
        # left, top part ...
        # ------------------
        self.tab1_fold_text = QLabel('Directory:', self.tab1_0)
        self.tab1_file_text = QLabel("File:", self.tab1_0)
        #
        self.tab1_left_layout.addWidget(self.tab1_fold_text)
        
        # pre
        self.tab1_pre_action_label = QLabel('Pre-Actions:', self.tab1_0)
        self.tab1_middle_layout.addWidget(self.tab1_pre_action_label);
        
        # post
        self.tab1_post_action_label = QLabel('Post-Actions:', self.tab1_0)
        self.tab1_right_layout.addWidget(self.tab1_post_action_label);
        
        # ----------------------------
        # left side directory view ...
        # ----------------------------
        self.tab1_path = QDir.homePath()
        
        self.tab1_dir_model = QFileSystemModel()
        self.tab1_dir_model.setRootPath(self.tab1_path)
        self.tab1_dir_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        
        self.tab1_file_model = QFileSystemModel()
        self.tab1_file_model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        
        self.tab1_file_tree = QTreeView()
        self.tab1_file_list = QListView()
        
        self.tab1_file_tree.setStyleSheet(_(css_model_header))
        
        self.tab1_file_tree.setModel(self.tab1_dir_model)
        self.tab1_file_list.setModel(self.tab1_file_model)
        
        self.tab1_file_tree.setRootIndex(self.tab1_dir_model.index(self.tab1_path))
        self.tab1_file_list.setRootIndex(self.tab1_file_model.index(self.tab1_path))
        
        self.tab1_left_layout.addWidget(self.tab1_file_tree)
        self.tab1_left_layout.addWidget(self.tab1_file_text)
        self.tab1_left_layout.addWidget(self.tab1_file_list)
        
        self.tab1_file_tree.clicked.connect(self.tab1_file_tree_clicked)
        self.tab1_file_list.clicked.connect(self.tab1_file_list_clicked)
        
        
        # Eingabezeile für den Pfad
        self.tab1_path_lineEdit = QLineEdit(self.tab1_0)
        self.tab1_path_lineEdit.setStyleSheet(css_button_style)
        self.tab1_path_lineButton = QPushButton("...")
        self.tab1_path_lineButton.setMinimumWidth(28)
        self.tab1_path_lineButton.setMaximumHeight(28)
        self.tab1_path_lineButton.setMaximumWidth(32)
        
        self.tab1_path_layout = QHBoxLayout()
        
        self.tab1_path_layout.addWidget(self.tab1_path_lineEdit)
        self.tab1_path_layout.addWidget(self.tab1_path_lineButton)
        #
        self.tab1_left_layout.addLayout(self.tab1_path_layout)
        
        # Start und Stop Buttons
        self.tab1_startButton = QPushButton("Start", self.tab1_0)
        self.tab1_startButton.setStyleSheet(css_button_style)
        self.tab1_startButton.clicked.connect(self.startWatching)
        self.tab1_left_layout.addWidget(self.tab1_startButton)
        
        self.tab1_stopButton = QPushButton('Stop', self.tab1_0)
        self.tab1_stopButton.setStyleSheet(css_button_style)
        self.tab1_stopButton.clicked.connect(self.stopWatching)
        self.tab1_left_layout.addWidget(self.tab1_stopButton)
        
        # ComboBox für Zeitangaben
        self.tab1_timeComboBox = QComboBox(self.tab1_0)
        self.tab1_timeComboBox.addItems(["10", "15", "20", "25", "30", "60", "120"])
        self.tab1_timeComboBox.setStyleSheet(css_button_style)
        self.tab1_timeComboBox.setMaximumWidth(49)
        self.tab1_left_layout.addWidget(self.tab1_timeComboBox)
        
        # Label für den Countdown
        self.tab1_countdownLabel = QLabel('Select time:', self.tab1_0)
        self.tab1_left_layout.addWidget(self.tab1_countdownLabel)
        
        # mitte Seite
        self.tab1_preActionList = QListWidget(self.tab1_0)
        self.tab1_preActionList_Label  = QLabel("Content:", self.tab1_0)
        self.tab1_preActionList_Editor = QPlainTextEdit()
        #
        self.tab1_middle_layout.addWidget(self.tab1_preActionList)
        self.tab1_middle_layout.addWidget(self.tab1_preActionList_Label)
        self.tab1_middle_layout.addWidget(self.tab1_preActionList_Editor)
        
        #
        self.tab1_preActionComboBox = QComboBox(self.tab1_0)
        self.tab1_preActionComboBox.addItems([" Message", " Script", " URL", " FTP"])
        self.tab1_preActionComboBox.setStyleSheet(_(css_combobox_style))
        self.tab1_timeComboBox.setMaximumWidth(49)
        self.tab1_middle_layout.addWidget(self.tab1_preActionComboBox)
        
        self.tab1_preEditLineLabel = QLabel("Text / File:", self.tab1_0)
        self.tab1_middle_layout.addWidget(self.tab1_preEditLineLabel)
        #
        self.tab1_pre_layout = QHBoxLayout()
        
        self.tab1_preEditLineText = QLineEdit(self.tab1_0)
        self.tab1_preEditLineText.setStyleSheet(css_button_style)
     
        self.tab1_path_lineButton.setMaximumHeight(28)
        
        #
        self.tab1_pre_layout.addWidget(self.tab1_preEditLineText)
        
        self.tab1_middle_layout.addLayout(self.tab1_pre_layout)
        
        self.tab1_preAddButton = QPushButton("Add")
        self.tab1_preAddButton.setStyleSheet(css_button_style)
        #
        self.tab1_preDelButton = QPushButton("Delete")
        self.tab1_preDelButton.setStyleSheet(css_button_style)
        #            
        self.tab1_preClrButton = QPushButton("Clear All")
        self.tab1_preClrButton.setStyleSheet(css_button_style)
        
        self.tab1_preAddButton.clicked.connect(self.button_clicked_preadd)
        self.tab1_preDelButton.clicked.connect(self.button_clicked_preDel)
        self.tab1_preClrButton.clicked.connect(self.button_clicked_preClr)
        #
        self.tab1_middle_layout.addWidget(self.tab1_preAddButton)
        self.tab1_middle_layout.addWidget(self.tab1_preDelButton)
        self.tab1_middle_layout.addWidget(self.tab1_preClrButton)
        
        
        # rechte Seite
        self.tab1_postActionList = QListWidget(self.tab1_0)
        self.tab1_postActionList_Label  = QLabel("Content:", self.tab1_0)
        self.tab1_postActionList_Editor = QPlainTextEdit()
        #
        self.tab1_right_layout.addWidget(self.tab1_postActionList)
        self.tab1_right_layout.addWidget(self.tab1_postActionList_Label)
        self.tab1_right_layout.addWidget(self.tab1_postActionList_Editor)
        
        self.tab1_postActionComboBox = QComboBox(self.tab1_0)
        self.tab1_postActionComboBox.addItems([" Message", " Script", " URL", " FTP"])
        self.tab1_postActionComboBox.setStyleSheet(_(css_combobox_style))
        self.tab1_right_layout.addWidget(self.tab1_postActionComboBox)
        
        self.tab1_postEditLineLabel = QLabel("Text / File:", self.tab1_0)
        self.tab1_right_layout.addWidget(self.tab1_postEditLineLabel)
        #
        self.tab1_post_layout = QHBoxLayout()
        
        self.tab1_postEditLineText = QLineEdit(self.tab1_0)
        self.tab1_postEditLineText.setStyleSheet(css_button_style)
        #
        self.tab1_post_layout.addWidget(self.tab1_postEditLineText)
        self.tab1_right_layout.addLayout(self.tab1_post_layout)
        
        self.tab1_postAddButton = QPushButton("Add")
        self.tab1_postAddButton.setStyleSheet(css_button_style)
        #
        self.tab1_postDelButton = QPushButton("Delete")
        self.tab1_postDelButton.setStyleSheet(css_button_style)
        #
        self.tab1_postClrButton = QPushButton("Clear All")
        self.tab1_postClrButton.setStyleSheet(css_button_style)
        
        self.tab1_postAddButton.clicked.connect(self.button_clicked_postadd)
        self.tab1_postDelButton.clicked.connect(self.button_clicked_postDel)
        self.tab1_postClrButton.clicked.connect(self.button_clicked_postClr)
        #
        self.tab1_right_layout.addWidget(self.tab1_postAddButton)
        self.tab1_right_layout.addWidget(self.tab1_postDelButton)
        self.tab1_right_layout.addWidget(self.tab1_postClrButton)
        
        
        # ------------------
        # alles zusammen ...
        # ------------------
        self.webView1 = QWebEngineView(self.tab_html)
        self.profile1 = QWebEngineProfile("storage1", self.webView1)
        self.page1    = QWebEnginePage(self.profile1, self.webView1)
        self.webView1.setPage(self.page1)
        self.webView1.setHtml(html_content, baseUrl = QUrl. fromLocalFile('.'))
        
        self.tab5_top_layout.addWidget(self.webView1);            
        self.tab0_top_layout.addLayout(self.tab0_left_layout)
        
        self.tab1_top_layout.addLayout(self.tab1_left_layout)
        self.tab1_top_layout.addLayout(self.tab1_middle_layout)
        self.tab1_top_layout.addLayout(self.tab1_right_layout)
        
        self.layout.addLayout(self.main_layout)
        self.layout.addWidget(self.status_bar)
        
        self.setLayout(self.layout)
        self.setWindowTitle('HelpNDoc File Watcher v0.0.1 - (c) 2024 Jens Kallup - paule32')
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateCountdown)
        
        self.interval = 0
        self.currentTime = 0
        
    # folder tree
    def openContextMenuTreeView(self, position):
        indexes = self.tab0_file_tree.selectedIndexes()
        if indexes:
            font = QFont(genv.v__app__font, 11)
            font.setBold(True)
            
            # Popup-Menü erstellen
            menu = QMenu()
            menu.setFont(font)
            menu.setStyleSheet(_("menu_css"))
            
            # Aktionen zum Menü hinzufügen
            enters_action = QAction("Enter Directory", self)
            create_action = QAction("Create", self)
            delete_action = QAction("Delete", self)
            rename_action = QAction("Rename", self)
            
            menu.addAction(enters_action)
            menu.addAction(create_action)
            menu.addAction(delete_action)
            menu.addAction(rename_action)
            
            # Aktionen verbinden
            enters_action.triggered.connect(lambda: self.entersDirectory(indexes[0]))
            create_action.triggered.connect(lambda: self.createDirectory(indexes[0]))
            delete_action.triggered.connect(lambda: self.deleteDirectory(indexes[0]))
            rename_action.triggered.connect(lambda: self.renameDirectory(indexes[0]))
            
            # Menü anzeigen
            menu.exec_(self.tab0_file_tree.viewport().mapToGlobal(position))
    
    def expand_entry(self, tree_view, model, path):
        index = model.index(path)
        if index.isValid():
            tree_view.expand(index)
    def entersDirectory(self, index):
        dir_path = self.tab0_dir_model.filePath(index)
        if os.path.isdir(dir_path):
            os.chdir(dir_path)
            self.expand_entry(
                self.tab0_file_tree,
                self.tab0_dir_model,
                dir_path)
            
            font = QFont(genv.v__app__font, 11)
            
            dialog = QMessageBox(self)
            dialog.setWindowTitle("Enter Directory")
            dialog.setText(
                "Operation successfully !\n"
                "No Error.")
            dialog.setFont(font)
            
            btn_ok = dialog.addButton(QMessageBox.Ok)
            btn_ok.setFont(font)
                    
            dialog.setStyleSheet(_("msgbox_css"))
            dialog.exec_()
    
    def createDirectory(self, index):
        dir_path = self.tab0_dir_model.filePath(index)
        if os.path.isdir(dir_path):
            font = QFont(genv.v__app__font, 11)
            
            dialog = QInputDialog(self)
            dialog.setWindowTitle("Create new directory")
            dialog.setLabelText("Type-In the name:")
            dialog.setFont(font)
            
            if dialog.exec_() == QInputDialog.Accepted:
                folder_name  = dialog.textValue()
                new_dir_path = os.path.join(dir_path, folder_name)
                new_dir_path = new_dir_path.replace('/',"\\")
                try:
                    if not os.path.exists(new_dir_path):
                        os.makedirs(new_dir_path, exist_ok=True)
                        
                        msg = QMessageBox()
                        msg.setWindowTitle("Information")
                        msg.setFont(font)
                        msg.setText(
                            "The directpry was create successfully.\n"
                            "No errors")
                        msg.setIcon(QMessageBox.Information)
                        
                        btn_ok = msg.addButton(QMessageBox.Ok)
                        btn_ok.setFont(font)
                        
                        msg.setStyleSheet(_("msgbox_css"))
                        result = msg.exec_()
                    else:
                        msg = QMessageBox()
                        msg.setWindowTitle("Error")
                        msg.setFont(font)
                        msg.setText(
                            "The directpry already exists.\n"
                            "Error.")
                        msg.setIcon(QMessageBox.Information)
                        
                        btn_ok = msg.addButton(QMessageBox.Ok)
                        btn_ok.setFont(font)
                        
                        msg.setStyleSheet(_("msgbox_css"))
                        result = msg.exec_()
                    
                except PermissionError:
                    msg = QMessageBox()
                    msg.setWindowTitle("Error")
                    msg.setFont(font)
                    msg.setText("No permissions to crrate this directpry !\n")
                    msg.setIcon(QMessageBox.Warning)
                    
                    btn_ok = msg.addButton(QMessageBox.Ok)
                    btm_ok.setFont(font)
                    
                    msg.setStyleSheet(_("msgbox_css"))
                    msg.exec_()
                    
                except FileExistsError:
                    msg = QMessageBox()
                    msg.setWindowTitle("Warning")
                    msg.setFont(font)
                    msg.setText(
                        "A directpry with the same name already exists !\n"
                        "Please try again, and giva a unique file name.")
                    msg.setIcon(QMessageBox.Warning)
                    
                    btn_ok = msg.addButton(QMessageBox.Ok)
                    btm_ok.setFont(font)
                    
                    msg.setStyleSheet(_("msgbox_css"))
                    msg.exec_()
                    
                except Exception as e:
                    print(e)
                    msg = QMessageBox()
                    msg.setWindowTitle("Warning")
                    msg.setFont(font)
                    msg.setText(
                        "The directpry could not be created !\n"
                        "Please try again, with different file name.")
                    msg.setIcon(QMessageBox.Warning)
                    
                    btn_ok = msg.addButton(QMessageBox.Ok)
                    btn_ok.setFont(font)
                    
                    msg.setStyleSheet(_("msgbox_css"))
                    msg.exec_()
                
    
    def deleteDirectory(self, index):
        file_path = self.tab0_dir_model.filePath(index)
        print(f"Löschen: {file_path}")
    
    def renameDirectory(self, index):
        file_path = self.tab0_dir_model.filePath(index)
        print(f"Umbenennen: {file_path}")
    
    # dbase
    def dbase_file_editor0_checkmessage(self, obj, file_path):
        if obj.hasFocus():
            msg = QMessageBox()
            msg.setWindowTitle("Confirmation")
            msg.setText(
                "The file content has been changed on file system.\n"
                "Would you reload the new content ?")
            msg.setIcon(QMessageBox.Question)
            
            btn_yes = msg.addButton(QMessageBox.Yes)
            btn_no  = msg.addButton(QMessageBox.No)
            
            msg.setStyleSheet(_("msgbox_css"))
            result = msg.exec_()
            
            if result == QMessageBox.Yes:
                new_content = self.readFromFile(file_path)
                obj.setPlainText(new_content)
    
    def readFromFile(self, file_path):
        file_content = ""
        file = QFile(file_path)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            file_content = stream.readAll()
            file.close()
        return file_content
    
    def dbase_file_editor1_changed(self, file_path):
        self.dbase_file_editor0_checkmessage(self.dbase_tabs_editor1, file_path)
    #
    def dbase_file_editor2_changed(self, file_path):
        self.dbase_file_editor0_checkmessage(self.dbase_tabs_editor2, file_path)
    
    def handleDBase(self):
        self.dbase_tabs = QTabWidget()
        self.dbase_tabs.setStyleSheet(css_tabs)
        self.dbase_tabs.hide()
        
        self.dbase_tabs_project_widget = QWidget()
        self.dbase_tabs_editors_widget = QWidget()
        self.dbase_tabs_designs_widget = QWidget()
        self.dbase_tabs_builder_widget = QWidget()
        self.dbase_tabs_datatab_widget = myDataTabWidget(self)
        self.dbase_tabs_reports_widget = QWidget()
        #
        #
        self.dbase_tabs.addTab(self.dbase_tabs_project_widget, "dBASE Project")
        self.dbase_tabs.addTab(self.dbase_tabs_editors_widget, "dBASE Editor")
        self.dbase_tabs.addTab(self.dbase_tabs_designs_widget, "dBASE Designer")
        self.dbase_tabs.addTab(self.dbase_tabs_builder_widget, "dBASE SQL Builder")
        self.dbase_tabs.addTab(self.dbase_tabs_datatab_widget, "dBASE Data Tables")
        self.dbase_tabs.addTab(self.dbase_tabs_reports_widget, "dBASE Reports")
        ####
        self.dbase_tabs_editors_layout = QVBoxLayout()
        self.dbase_tabs_editors_layout.setContentsMargins(2,2,2,2)
        
        self.dbase_tabs_editor_menu = QWidget()
        self.dbase_tabs_editor_menu.setStyleSheet("background-color:gray;")
        self.dbase_tabs_editor_menu.setMinimumHeight(64)
        #
        ####
        self.dbase_tabs_data_tables_layout = QVBoxLayout()
        self.dbase_tabs_data_tables_layout.setContentsMargins(2,2,2,2)
        
        self.dbase_tabs_data_tables_menu = QWidget()
        self.dbase_tabs_data_tables_menu.setStyleSheet("background-color:gray;")
        self.dbase_tabs_data_tables_menu.setMinimumHeight(64)
        #
        ####
        self.dbase_tabs_reports_layout = QVBoxLayout()
        self.dbase_tabs_reports_layout.setContentsMargins(2,2,2,2)
        
        self.dbase_tabs_reports_menu = QWidget()
        self.dbase_tabs_reports_menu.setStyleSheet("background-color:gray;")
        self.dbase_tabs_reports_menu.setMinimumHeight(64)
        #
        
        self.dbase_file_layout1 = QVBoxLayout()
        self.dbase_file_layout1.setContentsMargins(1,0,0,1)
        self.dbase_file_widget1 = QWidget()
        
        self.dbase_file_hlay = QHBoxLayout()
        
        custom_widget0 = CustomWidget0(self)
        custom_widget1 = CustomWidget1(self)
        custom_widget2 = CustomWidget2(self)
        
        self.dbase_file_hlay.addWidget(custom_widget0)
        self.dbase_file_hlay.addWidget(custom_widget1)
        self.dbase_file_hlay.addWidget(custom_widget2)
        self.dbase_file_hlay.addStretch()
        #
        self.dbase_tabs_editor_menu.setLayout(self.dbase_file_hlay)
        
        self.dbase_file_layout2 = QVBoxLayout()
        self.dbase_file_layout2.setContentsMargins(1,0,0,1)
        self.dbase_file_widget2 = QWidget()
        
        ####
        file_path = os.path.join(genv.v__app__app_dir__, "examples/dbase/example1.prg")
        file_path = file_path.replace("\\","/")
        
        self.dbase_tabs_editor1 = EditorTextEdit(file_path)
        self.dbase_file_layout1.addWidget(self.dbase_tabs_editor1)
        self.dbase_file_widget1.setLayout(self.dbase_file_layout1)
        #
        if os.path.exists(file_path):
            print("ok")
            self.dbase_file_editor1_filewatcher = FileSystemWatcher()
            self.dbase_file_editor1_filewatcher.addFile(file_path)
            self.dbase_file_editor1_filewatcher.watcher.fileChanged.connect(self.dbase_file_editor1_changed)
        ####
        file_path = os.path.join(genv.v__app__app_dir__, "examples/dbase/example2.prg")
        file_path = file_path.replace("\\","/")
        
        self.dbase_tabs_editor2 = EditorTextEdit(file_path)
        self.dbase_file_layout2.addWidget(self.dbase_tabs_editor2)
        self.dbase_file_widget2.setLayout(self.dbase_file_layout2)
        #
        if os.path.exists(file_path):
            print("ok")
            self.dbase_file_editor2_filewatcher = FileSystemWatcher()
            self.dbase_file_editor2_filewatcher.addFile(file_path)
            self.dbase_file_editor2_filewatcher.watcher.fileChanged.connect(self.dbase_file_editor2_changed)
        ####
        #
        self.dbase_tabs_files  = QTabWidget()
        self.dbase_tabs_files.setStyleSheet(css_tabs)
        self.dbase_tabs_files.addTab(self.dbase_file_widget1, "Example1.prg")
        self.dbase_tabs_files.addTab(self.dbase_file_widget2, "Example2.prg")
        
        self.dbase_tabs_editors_layout.addWidget(self.dbase_tabs_editor_menu)
        self.dbase_tabs_editors_layout.addWidget(self.dbase_tabs_files)
        
        
        self.dbase_tabs_editors_widget.setLayout(self.dbase_tabs_editors_layout)
        ####
        self.dbase_builder_layout = QVBoxLayout()
        self.dbase_builder_layout.setContentsMargins(2,2,2,2)
        
        self.dbase_builder_widget_table = QWidget()
        self.dbase_builder_widget_table.setStyleSheet(_("bggy"))
        self.dbase_builder_widget_table.setMaximumHeight(56)
        
        
        self.dbase_builder_widget_view = myGridViewerOverlay(self.dbase_tabs_builder_widget)
        self.dbase_builder_widget_view.setLayout(QVBoxLayout())
        
        
        self.dbase_builder_window_1 = MySQLDialog("Table A")
        self.dbase_builder_window_2 = MySQLDialog("Table B")
        #
        self.dbase_builder_widget_view.layout().addWidget(self.dbase_builder_window_1)
        self.dbase_builder_widget_view.layout().addWidget(self.dbase_builder_window_2)
        
        self.dbase_builder_widget_join = QTableWidget()
        self.dbase_builder_widget_join.setStyleSheet(_("join_build"))
        
        self.dbase_builder_widget_join.horizontalHeader().setStretchLastSection(True) 
        self.dbase_builder_widget_join.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        
        self.dbase_builder_widget_join.setRowCount(4)
        self.dbase_builder_widget_join.setColumnCount(4)
        
        self.dbase_builder_widget_join.setMinimumHeight(180)
        self.dbase_builder_widget_join.setMaximumHeight(180)
        
        self.dbase_builder_widget_join.setHorizontalHeaderLabels(["Table 1","Table2","TableA","TableB"])
        self.dbase_builder_widget_join.setVerticalHeaderLabels([" ID  "," ROW1  "," NAME  "," TEXT  "])
        
        header = self.dbase_builder_widget_join.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        ###
        self.dbase_builder_layout.addWidget(self.dbase_builder_widget_table)
        
        font = QFont(genv.v__app__font,11)
        self.db_hlayout = QHBoxLayout()
                
        self.dbase_builder_btn1 = QPushButton("Add Table")
        self.dbase_builder_btn2 = QPushButton("Add Data Source")
        self.dbase_builder_btn3 = QPushButton("Clear Dashboard")
        #
        self.dbase_builder_btn1.setFont(font)
        self.dbase_builder_btn2.setFont(font)
        self.dbase_builder_btn3.setFont(font)
        
        self.dbase_builder_btn1.setMinimumHeight(29)
        self.dbase_builder_btn2.setMinimumHeight(29)
        self.dbase_builder_btn3.setMinimumHeight(29)
        #
        self.db_hlayout.addWidget(self.dbase_builder_btn1)
        self.db_hlayout.addWidget(self.dbase_builder_btn2)
        self.db_hlayout.addWidget(self.dbase_builder_btn3)
        
        self.dbase_builder_layout.addLayout(self.db_hlayout)
        #
        self.dbase_builder_btn1.clicked.connect(self.dbase_builder_btn1_clicked)
        self.dbase_builder_btn2.clicked.connect(self.dbase_builder_btn2_clicked)
        
        self.dbase_builder_layout.addWidget(self.dbase_builder_widget_view)
        self.dbase_builder_layout.addWidget(self.dbase_builder_widget_join)
        ###
        
        self.dbase_tabs_builder_widget.setLayout(self.dbase_builder_layout)
        
        ####
        self.dbase_designs_layout  = QVBoxLayout()
        self.dbase_designs_layout.setContentsMargins(2,2,2,2)
        self.dbase_designs_palette = QWidget()
        self.dbase_designs_palette.setStyleSheet(_("bggy"))
        self.dbase_designs_palette.setMinimumHeight(85)
        self.dbase_designs_palette.setMaximumHeight(85)
        #
        self.dbase_palette_layout  = QHBoxLayout()
        self.dbase_palette_layout.setContentsMargins(2,2,2,2)
        self.dbase_palette_widget_lhs  = QLabel ()
        self.dbase_palette_widget_mid  = QWidget()
        self.dbase_palette_widget_rhs  = QLabel ()
        #
        self.dbase_palette_widget_lhs.setMaximumWidth(20)
        self.dbase_palette_widget_rhs.setMaximumWidth(20)
        
        font = QFont("Times New Roman", 16)
        #font.setBold(True)
        
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        
        self.dbase_palette_widget_lhs.setFont(font)
        self.dbase_palette_widget_rhs.setFont(font)
        #
        self.dbase_palette_widget_lhs.setText(chr1)
        self.dbase_palette_widget_rhs.setText(chr2)
        #
        self.dbase_palette_widget_lhs.setStyleSheet(_("bglg"))
        self.dbase_palette_widget_mid.setStyleSheet(_("bggy"))
        self.dbase_palette_widget_rhs.setStyleSheet(_("bglg"))
        #
        #
        self.dbase_palette_widget_mid_layout = QHBoxLayout()
        self.dbase_palette_widget_mid_tabs   = QTabWidget()
        self.dbase_palette_widget_mid_tabs.setStyleSheet(_("designertab"))
        
        #######
        addDesignerTabs(self.dbase_palette_widget_mid_tabs)
        
        self.dbase_palette_widget_mid_layout.addWidget(self.dbase_palette_widget_mid_tabs)
        #
        self.dbase_palette_layout.addWidget(self.dbase_palette_widget_lhs)
        self.dbase_palette_layout.addLayout(self.dbase_palette_widget_mid_layout)
        self.dbase_palette_layout.addWidget(self.dbase_palette_widget_rhs)
        #
        self.dbase_designs_palette.setLayout(self.dbase_palette_layout)
        ####
        
        self.dbase_designs_viewer  = myGridViewer(self)
        self.dbase_designs_viewer.setStyleSheet(_("bgwh"))
        
        self.dbase_designs_layout.addWidget(self.dbase_designs_palette)
        self.dbase_designs_layout.addWidget(self.dbase_designs_viewer)
        #
        self.dbase_tabs_designs_widget.setLayout(self.dbase_designs_layout)
        ####
        self.main_layout.addWidget(self.dbase_tabs)
        #################
        font = QFont(genv.v__app__font, 12)
        self.dbase_btn1 = myMoveButton(" move me A ", self.dbase_designs_viewer.content)
        self.dbase_btn2 = myMoveButton(" move me B ", self.dbase_designs_viewer.content)
        self.dbase_btn3 = myMoveButton(" move me C ", self.dbase_designs_viewer.content)
        #
        self.dbase_btn1.move(20,20)
        self.dbase_btn2.move(40,40)
        self.dbase_btn3.move(60,60)
        #
        self.dbase_btn1.setFont(font)
        self.dbase_btn2.setFont(font)
        self.dbase_btn3.setFont(font)
        #
        self.dbase_btn1.setStyleSheet("background-color:red;color:yellow;")
        self.dbase_btn2.setStyleSheet("background-color:yellow;color:black;")
        self.dbase_btn3.setStyleSheet("background-color:blue;color:white;")
    
    def dbase_builder_btn1_clicked(self):
        tableDialog = myAddTableDialog(self)
        tableDialog.exec_()
    
    def dbase_builder_btn2_clicked(self):
        sourceDialog = addDataSourceDialog(self)
        sourceDialog.exec_()
    
    # pascal
    def handlePascal(self):
        self.pascal_tabs = QTabWidget()
        self.pascal_tabs.setStyleSheet(css_tabs)
        self.pascal_tabs.hide()
        
        self.pascal_tabs_project_widget = QWidget()
        self.pascal_tabs_editors_widget = QWidget()
        self.pascal_tabs_designs_widget = QWidget()
        #
        self.pascal_tabs.addTab(self.pascal_tabs_project_widget, "Pascal Project")
        self.pascal_tabs.addTab(self.pascal_tabs_editors_widget, "Pascal Editor")
        self.pascal_tabs.addTab(self.pascal_tabs_designs_widget, "Pascal Designer")
        
        self.pascal_designs_layout  = QVBoxLayout()
        self.pascal_designs_layout.setContentsMargins(2,2,2,2)
        self.pascal_designs_palette = QWidget()
        self.pascal_designs_palette.setStyleSheet(_("bggy"))
        self.pascal_designs_palette.setMaximumHeight(80)
        #
        self.pascal_palette_layout  = QHBoxLayout()
        self.pascal_palette_layout.setContentsMargins(2,2,2,2)
        self.pascal_palette_widget_lhs  = QLabel ()
        self.pascal_palette_widget_mid  = QWidget()
        self.pascal_palette_widget_rhs  = QLabel ()
        #
        self.pascal_palette_widget_lhs.setMaximumWidth(20)
        self.pascal_palette_widget_rhs.setMaximumWidth(20)
        
        font = QFont("Times New Roman", 16)
        #font.setBold(True)
        
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        
        self.pascal_palette_widget_lhs.setFont(font)
        self.pascal_palette_widget_rhs.setFont(font)
        #
        self.pascal_palette_widget_lhs.setText(chr1)
        self.pascal_palette_widget_rhs.setText(chr2)
        #
        self.pascal_palette_widget_lhs.setStyleSheet(_("bglg"))
        self.pascal_palette_widget_mid.setStyleSheet(_("bgwh"))
        self.pascal_palette_widget_rhs.setStyleSheet(_("bglg"))
        #
        #
        self.pascal_palette_widget_mid_layout = QHBoxLayout()
        self.pascal_palette_widget_mid_tabs   = QTabWidget()
        self.pascal_palette_widget_mid_tabs.setStyleSheet(_("designertab"))
        
        #######
        addDesignerTabs(self.pascal_palette_widget_mid_tabs)
        
        self.pascal_palette_widget_mid_layout.addWidget(self.pascal_palette_widget_mid_tabs)
        #
        self.pascal_palette_layout.addWidget(self.pascal_palette_widget_lhs)
        self.pascal_palette_layout.addLayout(self.pascal_palette_widget_mid_layout)
        self.pascal_palette_layout.addWidget(self.pascal_palette_widget_rhs)
        #
        self.pascal_designs_palette.setLayout(self.pascal_palette_layout)
        ####
        
        self.pascal_designs_viewer  = myGridViewer(self)
        self.pascal_designs_viewer.setStyleSheet("background-color:cyan;")
        
        self.pascal_designs_layout.addWidget(self.pascal_designs_palette)
        self.pascal_designs_layout.addWidget(self.pascal_designs_viewer)
        #
        self.pascal_tabs_designs_widget.setLayout(self.pascal_designs_layout)
        ####
        self.main_layout.addWidget(self.pascal_tabs)
        #################
        self.pascal_btn1 = myMoveButton("move me D", self.pascal_designs_viewer)
        self.pascal_btn2 = myMoveButton("move me E", self.pascal_designs_viewer)
        self.pascal_btn3 = myMoveButton("move me F", self.pascal_designs_viewer)
        #
        self.pascal_btn1.move(120,20)
        self.pascal_btn2.move(140,40)
        self.pascal_btn3.move(160,60)
        
    # isoc
    def handleIsoC(self):
        self.isoc_tabs = QTabWidget()
        self.isoc_tabs.setStyleSheet(css_tabs)
        self.isoc_tabs.hide()
        
        self.isoc_tabs_project_widget = QWidget()
        self.isoc_tabs_editors_widget = QWidget()
        self.isoc_tabs_designs_widget = QWidget()
        #
        self.isoc_tabs.addTab(self.isoc_tabs_project_widget, "ISO C Project")
        self.isoc_tabs.addTab(self.isoc_tabs_editors_widget, "ISO C Editor")
        self.isoc_tabs.addTab(self.isoc_tabs_designs_widget, "ISO C Designer")
        
        self.isoc_designs_layout  = QVBoxLayout()
        self.isoc_designs_layout.setContentsMargins(2,2,2,2)
        self.isoc_designs_palette = QWidget()
        self.isoc_designs_palette.setStyleSheet(_("bggy"))
        self.isoc_designs_palette.setMaximumHeight(80)
        #
        self.isoc_palette_layout  = QHBoxLayout()
        self.isoc_palette_layout.setContentsMargins(2,2,2,2)
        self.isoc_palette_widget_lhs  = QLabel ()
        self.isoc_palette_widget_mid  = QWidget()
        self.isoc_palette_widget_rhs  = QLabel ()
        #
        self.isoc_palette_widget_lhs.setMaximumWidth(20)
        self.isoc_palette_widget_rhs.setMaximumWidth(20)
        
        font = QFont("Times New Roman", 16)
        #font.setBold(True)
        
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        
        self.isoc_palette_widget_lhs.setFont(font)
        self.isoc_palette_widget_rhs.setFont(font)
        #
        self.isoc_palette_widget_lhs.setText(chr1)
        self.isoc_palette_widget_rhs.setText(chr2)
        #
        self.isoc_palette_widget_lhs.setStyleSheet(_("bglg"))
        self.isoc_palette_widget_mid.setStyleSheet(_("bgwh"))
        self.isoc_palette_widget_rhs.setStyleSheet(_("bglg"))
        #
        #
        self.isoc_palette_widget_mid_layout = QHBoxLayout()
        self.isoc_palette_widget_mid_tabs   = QTabWidget()
        self.isoc_palette_widget_mid_tabs.setStyleSheet(_("designertab"))
        
        #######
        addDesignerTabs(self.isoc_palette_widget_mid_tabs)
        
        
        self.isoc_palette_widget_mid_layout.addWidget(self.isoc_palette_widget_mid_tabs)
        #
        self.isoc_palette_layout.addWidget(self.isoc_palette_widget_lhs)
        self.isoc_palette_layout.addLayout(self.isoc_palette_widget_mid_layout)
        self.isoc_palette_layout.addWidget(self.isoc_palette_widget_rhs)
        #
        self.isoc_designs_palette.setLayout(self.isoc_palette_layout)
        ####
        
        self.isoc_designs_viewer  = myGridViewer(self)
        self.isoc_designs_viewer.setStyleSheet("background-color:cyan;")
        
        self.isoc_designs_layout.addWidget(self.isoc_designs_palette)
        self.isoc_designs_layout.addWidget(self.isoc_designs_viewer)
        #
        self.isoc_tabs_designs_widget.setLayout(self.isoc_designs_layout)
        ####
        self.main_layout.addWidget(self.isoc_tabs)
    
    # java
    def handleJava(self):
        # java
        self.java_tabs = QTabWidget()
        self.java_tabs.setStyleSheet(css_tabs)
        self.java_tabs.hide()
        
        self.java_tabs_project_widget = QWidget()
        self.java_tabs_editors_widget = QWidget()
        self.java_tabs_designs_widget = QWidget()
        #
        self.java_tabs.addTab(self.java_tabs_project_widget, "Java Project")
        self.java_tabs.addTab(self.java_tabs_editors_widget, "Java Editor")
        self.java_tabs.addTab(self.java_tabs_designs_widget, "Java Designer")
        
        self.java_designs_layout  = QVBoxLayout()
        self.java_designs_layout.setContentsMargins(2,2,2,2)
        self.java_designs_palette = QWidget()
        self.java_designs_palette.setStyleSheet(_("bggy"))
        self.java_designs_palette.setMaximumHeight(80)
        #
        self.java_palette_layout  = QHBoxLayout()
        self.java_palette_layout.setContentsMargins(2,2,2,2)
        self.java_palette_widget_lhs  = QLabel ()
        self.java_palette_widget_mid  = QWidget()
        self.java_palette_widget_rhs  = QLabel ()
        #
        self.java_palette_widget_lhs.setMaximumWidth(20)
        self.java_palette_widget_rhs.setMaximumWidth(20)
        
        font = QFont("Times New Roman", 16)
        #font.setBold(True)
        
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        
        self.java_palette_widget_lhs.setFont(font)
        self.java_palette_widget_rhs.setFont(font)
        #
        self.java_palette_widget_lhs.setText(chr1)
        self.java_palette_widget_rhs.setText(chr2)
        #
        self.java_palette_widget_lhs.setStyleSheet(_("bglg"))
        self.java_palette_widget_mid.setStyleSheet(_("bgwh"))
        self.java_palette_widget_rhs.setStyleSheet(_("bglg"))
        #
        #
        self.java_palette_widget_mid_layout = QHBoxLayout()
        self.java_palette_widget_mid_tabs   = QTabWidget()
        self.java_palette_widget_mid_tabs.setStyleSheet(_("designertab"))
        
        #######
        addDesignerTabs(self.java_palette_widget_mid_tabs)
        
        
        self.java_palette_widget_mid_layout.addWidget(self.java_palette_widget_mid_tabs)
        #
        self.java_palette_layout.addWidget(self.java_palette_widget_lhs)
        self.java_palette_layout.addLayout(self.java_palette_widget_mid_layout)
        self.java_palette_layout.addWidget(self.java_palette_widget_rhs)
        #
        self.java_designs_palette.setLayout(self.java_palette_layout)
        ####
        
        self.java_designs_viewer  = myGridViewer(self)
        self.java_designs_viewer.setStyleSheet("background-color:cyan;")
        
        self.java_designs_layout.addWidget(self.java_designs_palette)
        self.java_designs_layout.addWidget(self.java_designs_viewer)
        #
        self.java_tabs_designs_widget.setLayout(self.java_designs_layout)
        ####
        self.main_layout.addWidget(self.java_tabs)
    
    # python
    def handlePython(self):
        self.python_tabs = QTabWidget()
        self.python_tabs.setStyleSheet(css_tabs)
        self.python_tabs.hide()
        
        self.python_tabs_project_widget = QWidget()
        self.python_tabs_editors_widget = QWidget()
        self.python_tabs_designs_widget = QWidget()
        #
        self.python_tabs.addTab(self.python_tabs_project_widget, "Python Project")
        self.python_tabs.addTab(self.python_tabs_editors_widget, "Python Editor")
        self.python_tabs.addTab(self.python_tabs_designs_widget, "Python Designer")
        
        self.python_designs_layout  = QVBoxLayout()
        self.python_designs_layout.setContentsMargins(2,2,2,2)
        self.python_designs_palette = QWidget()
        self.python_designs_palette.setStyleSheet(_("bggy"))
        self.python_designs_palette.setMaximumHeight(80)
        #
        self.python_palette_layout  = QHBoxLayout()
        self.python_palette_layout.setContentsMargins(2,2,2,2)
        self.python_palette_widget_lhs  = QLabel ()
        self.python_palette_widget_mid  = QWidget()
        self.python_palette_widget_rhs  = QLabel ()
        #
        self.python_palette_widget_lhs.setMaximumWidth(20)
        self.python_palette_widget_rhs.setMaximumWidth(20)
        
        font = QFont("Times New Roman", 16)
        #font.setBold(True)
        
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        
        self.python_palette_widget_lhs.setFont(font)
        self.python_palette_widget_rhs.setFont(font)
        #
        self.python_palette_widget_lhs.setText(chr1)
        self.python_palette_widget_rhs.setText(chr2)
        #
        self.python_palette_widget_lhs.setStyleSheet(_("bglg"))
        self.python_palette_widget_mid.setStyleSheet(_("bgwh"))
        self.python_palette_widget_rhs.setStyleSheet(_("bglg"))
        #
        #
        self.python_palette_widget_mid_layout = QHBoxLayout()
        self.python_palette_widget_mid_tabs   = QTabWidget()
        self.python_palette_widget_mid_tabs.setStyleSheet(_("designertab"))
        
        #######
        addDesignerTabs(self.python_palette_widget_mid_tabs)
        
        self.python_palette_widget_mid_layout.addWidget(self.python_palette_widget_mid_tabs)
        #
        self.python_palette_layout.addWidget(self.python_palette_widget_lhs)
        self.python_palette_layout.addLayout(self.python_palette_widget_mid_layout)
        self.python_palette_layout.addWidget(self.python_palette_widget_rhs)
        #
        self.python_designs_palette.setLayout(self.python_palette_layout)
        ####
        
        self.python_designs_viewer  = myGridViewer(self)
        self.python_designs_viewer.setStyleSheet("background-color:cyan;")
        
        self.python_designs_layout.addWidget(self.python_designs_palette)
        self.python_designs_layout.addWidget(self.python_designs_viewer)
        #
        self.python_tabs_designs_widget.setLayout(self.python_designs_layout)
        ####
        self.main_layout.addWidget(self.python_tabs)
    
    # lisp
    def handleLISP(self):
        self.lisp_tabs = QTabWidget()
        self.lisp_tabs.setStyleSheet(css_tabs)
        self.lisp_tabs.hide()
        
        self.lisp_tabs_project_widget = QWidget()
        self.lisp_tabs_editors_widget = QWidget()
        self.lisp_tabs_designs_widget = QWidget()
        #
        self.lisp_tabs.addTab(self.lisp_tabs_project_widget, "LISP Project")
        self.lisp_tabs.addTab(self.lisp_tabs_editors_widget, "LISP Editor")
        self.lisp_tabs.addTab(self.lisp_tabs_designs_widget, "LISP Designer")
        
        self.lisp_designs_layout  = QVBoxLayout()
        self.lisp_designs_layout.setContentsMargins(2,2,2,2)
        self.lisp_designs_palette = QWidget()
        self.lisp_designs_palette.setStyleSheet(_("bggy"))
        self.lisp_designs_palette.setMaximumHeight(80)
        #
        self.lisp_palette_layout  = QHBoxLayout()
        self.lisp_palette_layout.setContentsMargins(2,2,2,2)
        self.lisp_palette_widget_lhs  = QLabel ()
        self.lisp_palette_widget_mid  = QWidget()
        self.lisp_palette_widget_rhs  = QLabel ()
        #
        self.lisp_palette_widget_lhs.setMaximumWidth(20)
        self.lisp_palette_widget_rhs.setMaximumWidth(20)
        
        font = QFont("Times New Roman", 16)
        #font.setBold(True)
        
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        
        self.lisp_palette_widget_lhs.setFont(font)
        self.lisp_palette_widget_rhs.setFont(font)
        #
        self.lisp_palette_widget_lhs.setText(chr1)
        self.lisp_palette_widget_rhs.setText(chr2)
        #
        self.lisp_palette_widget_lhs.setStyleSheet(_("bglg"))
        self.lisp_palette_widget_mid.setStyleSheet(_("bgwh"))
        self.lisp_palette_widget_rhs.setStyleSheet(_("bglg"))
        #
        #
        self.lisp_palette_widget_mid_layout = QHBoxLayout()
        self.lisp_palette_widget_mid_tabs   = QTabWidget()
        self.lisp_palette_widget_mid_tabs.setStyleSheet(_("designertab"))
        
        #######
        addDesignerTabs(self.lisp_palette_widget_mid_tabs)
        
        self.lisp_palette_widget_mid_layout.addWidget(self.lisp_palette_widget_mid_tabs)
        #
        self.lisp_palette_layout.addWidget(self.lisp_palette_widget_lhs)
        self.lisp_palette_layout.addLayout(self.lisp_palette_widget_mid_layout)
        self.lisp_palette_layout.addWidget(self.lisp_palette_widget_rhs)
        #
        self.lisp_designs_palette.setLayout(self.lisp_palette_layout)
        ####
        
        self.lisp_designs_viewer  = myGridViewer(self)
        self.lisp_designs_viewer.setStyleSheet("background-color:cyan;")
        
        self.lisp_designs_layout.addWidget(self.lisp_designs_palette)
        self.lisp_designs_layout.addWidget(self.lisp_designs_viewer)
        #
        self.lisp_tabs_designs_widget.setLayout(self.lisp_designs_layout)
        ####
        self.main_layout.addWidget(self.lisp_tabs)
    
    # locale
    def handleLocales(self):
        self.locale_tabs = QTabWidget()
        self.locale_tabs.setStyleSheet(css_tabs)
        self.locale_tabs.hide()
        
        self.locale_tabs_project_widget = QWidget()
        self.locale_tabs_editors_widget = QWidget()
        self.locale_tabs_designs_widget = QWidget()
        #
        self.locale_tabs.addTab(self.locale_tabs_project_widget, "Locales Project")
        self.locale_tabs.addTab(self.locale_tabs_editors_widget, "Locales Editor")
        self.locale_tabs.addTab(self.locale_tabs_designs_widget, "Locales Designer")
        ####
        self.main_layout.addWidget(self.locale_tabs)
        
        self.handleLocalesProject()
        self.handleLocalesEditor()
    
    def handleLocalesEditor(self):
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()
        
        font  = QFont(genv.v__app__font, 10)
        font2 = QFont(genv.v__app__font_edit, 11)
        
        self.list_widget = QListWidget()
        self.list_widget.setFont(font2)
        self.list_widget.setMaximumWidth(320)
        self.list_widget.currentItemChanged.connect(self.on_list_item_changed)
        
        self.text_edit = QPlainTextEdit()
        self.text_edit.setFont(font2)
        
        self.load_button = QPushButton('Load .mo File')
        self.load_button.setFont(font)
        self.load_button.setMinimumHeight(31)
        self.load_button.clicked.connect(self.load_mo_file)
        
        self.save_button = QPushButton('Save Changes')
        self.save_button.setFont(font)
        self.save_button.setMinimumHeight(31)
        self.save_button.clicked.connect(self.save_changes)
        
        self.status_label = QLabel('Load a .mo file to begin editing.')
        self.status_label.setFont(font)
        
        hbox.addWidget(self.list_widget)
        hbox.addWidget(self.text_edit)
        
        vbox.addLayout(hbox)
        vbox.addWidget(self.load_button)
        vbox.addWidget(self.save_button)
        vbox.addWidget(self.status_label)
        
        self.locale_tabs_editors_widget.setLayout(vbox)
        return
        
    def load_mo_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open .mo file', '', 'MO Files (*.mo)')
        if file_name:
            self.po = polib.mofile(file_name)
            self.list_widget.clear()
            for entry in self.po:
                self.list_widget.addItem(entry.msgid)
            self.status_label.setText(f'Loaded: {file_name}')
            self.current_file = file_name
    
    def on_list_item_changed(self, current, previous):
        if current:
            msgid = current.text()
            entry = self.po.find(msgid)
            if entry:
                self.text_edit.setPlainText(entry.msgstr)
    
    def save_changes(self):
        current_item = self.list_widget.currentItem()
        if current_item:
            msgid = current_item.text()
            entry = self.po.find(msgid)
            if entry:
                entry.msgstr = self.text_edit.toPlainText()
            self.po.save(self.current_file)
            self.status_label.setText('Changes saved.')
    
    def on_item_double_clicked(self, item):
        index = self.countryList.row(item)
        el = genv.v__app__cdn_flags[index][1][-7:]
        el = el[:3]
        print(el)
    
    def handleLocalesProject(self):
        edit_css = _("edit_css")
        
        font = QFont(genv.v__app__font, 10)
        self.locale_tabs_project_widget.setFont(font)
        
        vlayout0 = QVBoxLayout()
        templateLabel = QLabel("Templates:")
        templateLabel.setFont(font)
        
        push1 = MyPushButton("Create", 1)
        push2 = MyPushButton("Open"  , 2)
        push3 = MyPushButton("Repro" , 3)
        push4 = MyPushButton("Build" , 4)
        #
        vlayout0.addWidget(templateLabel)
        vlayout0.addWidget(push1)
        vlayout0.addWidget(push2)
        vlayout0.addWidget(push3)
        vlayout0.addWidget(push4)
        #
        vlayout0.addStretch()
        
        vlayout1 = QVBoxLayout()
        lbl = QLabel("Project name:")
        lbl.setFont(font)
        vlayout1.addWidget(lbl)
        #
        font2 = QFont(genv.v__app__font_edit, 10)
        edit1 = QLineEdit()
        edit1.setFont(font2)
        edit1.setStyleSheet(edit_css)
        edit1.setPlaceholderText("Example Project")
        vlayout1.addWidget(edit1)
        #
        lblA = QLabel("Project File:")
        lblA.setFont(font)
        vlayout1.addWidget(lblA)
        #
        editA = doubleClickLocalesLineEdit(self)
        editA.setFont(font2)
        editA.setStyleSheet(edit_css)
        editA.setPlaceholderText("example.pro")
        vlayout1.addWidget(editA)
        #
        lbl2 = QLabel("Description:")
        lbl2.setFont(font)
        vlayout1.addWidget(lbl2)
        #
        edit2 = QPlainTextEdit()
        edit2.setFont(font2)
        vlayout1.addWidget(edit2)
        #
        vlayout1.addStretch()
        
        hlayout0 = QHBoxLayout()
        hlayout0.addLayout(vlayout0)
        hlayout0.addLayout(vlayout1)
        
        # left scroll area
        scroll_area0 = QScrollArea()
        scroll_area0.setWidgetResizable(True)
        
        container_widget0 = QWidget()
        country_layout = QVBoxLayout()
        
        # ------------------------------------
        # read in external url image data ...
        # ------------------------------------
        self.countryList = QListWidget()
        self.countryList.setMinimumHeight(212)
        countries = []
        
        self.countryList.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        for itemlistA in genv.v__app__cdn_flags:
            if itemlistA[0] == "USA":
                for itemlistB in genv.v__app__cdn_flags:
                    MyCountryProject(self, self.countryList, itemlistA, itemlistB)
                break

        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        
        groupBox = QGroupBox("")
        groupBox.setMinimumWidth(400)
        groupBox.setFont(font)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        container_widget = QWidget()
        groupvLayout = QVBoxLayout()
        
        #
        self.localeliste = [
            [ QLabel(" Project-ID-Version:"),        QLineEdit(), self.e1_on_return_pressed, "1.0.0" ],
            [ QLabel(" POT-Creation-Date:"),         QLineEdit(), self.e2_on_return_pressed, "2024-04-06 20:33+0200" ],
            [ QLabel(" PO-Revision-Date:"),          QLineEdit(), self.e3_on_return_pressed, "2024-04-06 20:15+0200" ],
            [ QLabel(" Last-Translator:"),           QLineEdit(), self.e4_on_return_pressed, "John Jonsen <jhon@example.com" ],
            [ QLabel(" Language-Team:"),             QLineEdit(), self.e5_on_return_pressed, "English <jhon@example.com>" ],
            [ QLabel(" MIME-Version:"),              QLineEdit(), self.e6_on_return_pressed, "1.0" ],
            [ QLabel(" Content-Type:"),              QLineEdit(), self.e7_on_return_pressed, "text/plain; charset=cp1252" ],
            [ QLabel(" Content-Transfer-Encoding:"), QLineEdit(), self.e8_on_return_pressed, "8bit" ]
        ]
        for item in self.localeliste:
            item[0].setFont(font)
            #
            item[1].setPlaceholderText(item[3])
            item[1].setFont(font2)
            item[1].setStyleSheet(_(edit_css))
            item[1].returnPressed.connect(item[2])
            #
            groupvLayout.addWidget(item[0])
            groupvLayout.addWidget(item[1])
        #
        groupvLayout.addStretch()
        
        container_widget.setLayout(groupvLayout)
        scroll_area.setWidget(container_widget)
        
        group_layout = QVBoxLayout()
        group_layout.addWidget(scroll_area)
        
        groupBox.setLayout(group_layout)
        
        extensions = [".pro"]
        directory  = QDir.homePath() 
        
        self.modelLocales = QFileSystemModel()
        self.modelLocales.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
        self.modelLocales.setRootPath(directory)
        
        self.proxyModelLocales = ExtensionFilterProxyModel(extensions)
        self.proxyModelLocales.setSourceModel(self.modelLocales)
        
        # Create the drives tree
        self.drives_treeLocales = QTreeWidget()
        self.drives_treeLocales.setHeaderLabels(["Drive", "Available Space", "Total Size"])
        self.drives_treeLocales.setMinimumHeight(120)
        #self.drives_treeLocales.setMaximumWidth(380)
        self.drives_treeLocales.header().setSectionResizeMode(QHeaderView.Interactive)
        self.drives_treeLocales.itemClicked.connect(self.on_driveLocales_clicked)
        self.drives_treeLocales.setStyleSheet("QHeaderView::section { background-color: lightgreen }")
        
        
        self.treeLocales = QTreeView()
        self.treeLocales.setModel(self.proxyModelLocales)
        self.treeLocales.setRootIndex(self.proxyModelLocales.mapFromSource(self.modelLocales.index(directory)))
        self.treeLocales.setMinimumHeight(200)
        self.treeLocales.clicked.connect(self.on_treeLocales_double_clicked)
        
        
        # Hide the "Size" and "Type" columns
        self.treeLocales.setColumnHidden(1, True)  # Size
        self.treeLocales.setColumnHidden(2, True)  # Type
        
        self.treeLocales.setColumnWidth(0, 250)
        self.treeLocales.setAlternatingRowColors(True)
        self.treeLocales.setSortingEnabled(True)
        
        self.treeLocales.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeLocales.customContextMenuRequested.connect(self.openContextMenuLocales)
        
        #projects = QListWidget
        country_layout.addWidget(self.countryList)
        country_layout.addWidget(self.drives_treeLocales)
        country_layout.addWidget(self.treeLocales)
        
        container_widget0.setLayout(country_layout)
        scroll_area0.setWidget(container_widget0)
        
        groupBox0 = QGroupBox("")
        groupBox0.setMinimumWidth(360)
        groupBox0_layout = QVBoxLayout()
        groupBox0_layout.addWidget(scroll_area0)
        
        groupBox0.setLayout(groupBox0_layout)
        
        vlayout.addWidget(groupBox0)
        #vlayout.addWidget(self.treeLocales)
        
        hlayout.addLayout(vlayout)
        hlayout.addWidget(groupBox)
        
        vlayout2 = QVBoxLayout()
        vlayout2.addLayout(hlayout0)
        vlayout2.addLayout(hlayout)
        #
        vlayout2.addStretch()
        
        ###
        font.setPointSize(11) #öööö
        
        btnLoad = QPushButton("Load") # todo
        btnSave = QPushButton("Save")
        
        btnLoad.setMinimumHeight(32)
        btnSave.setMinimumHeight(32)
        
        btnLoad.setFont(font)
        btnSave.setFont(font)
        
        hlayout2 = QHBoxLayout()
        hlayout2.addWidget(btnLoad)
        hlayout2.addWidget(btnSave)
        
        vlayout2.addLayout(hlayout2)
        
        btnLoad.clicked.connect(self.btnOpenLocales_clicked)
        btnSave.clicked.connect(self.btnSaveLocales_clicked)
        
        self.locale_tabs_project_widget.setLayout(vlayout2)
        
        self.load_drives()
        return
    
    def on_treeLocales_double_clicked(self, index):
        indexes = self.treeLocales.selectedIndexes()
        if indexes:
            index = self.proxyModelLocales.mapToSource(indexes[0])
            file_path = self.modelLocales.filePath(index)
            file_full = file_path.replace("\\", "/")
            
            file_path, file_name = os.path.split(file_path)
            
            if os.path.isfile(file_full):
                if file_name.endswith(".pro"):
                    with open(file_full, "rb") as file:
                        header = file.read(3)
                        if header == b"\x1f\x8b\x08":
                            print("file: " + file_name + " is packed.")
                        else:
                            print("file: " + file_name + " is not packed.")
                        file.close()
                    print(self.localeliste[0][0].text())
        return
    
    def load_drives(self):
        drives = [drive for drive in QDir.drives()]
        for drive in drives:
            total_size, available_space = self.get_drive_info(drive.absolutePath())
            item = QTreeWidgetItem([drive.absolutePath(), available_space, total_size])
            self.drives_treeLocales.addTopLevelItem(item)
    
    def get_drive_info(self, drive):
        try:
            total, used, free = shutil.disk_usage(drive)
            return self.format_size(total), self.format_size(free)
        except Exception as e:
            return "N/A", "N/A"
    
    def format_size(self, size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
    
    def on_driveLocales_clicked(self, item):
        drive_path = item.text(0)
        self.treeLocales.setRootIndex(self.proxyModelLocales.mapFromSource(self.modelLocales.index(drive_path)))
        return
    
    def e1_on_return_pressed(self):
        self.e2Locales.setFocus()
        return
    def e2_on_return_pressed(self):
        self.e3Locales.setFocus()
        return
    def e3_on_return_pressed(self):
        self.e4Locales.setFocus()
        return
    def e4_on_return_pressed(self):
        self.e5Locales.setFocus()
        return
    def e5_on_return_pressed(self):
        self.e6Locales.setFocus()
        return
    def e6_on_return_pressed(self):
        self.e7Locales.setFocus()
        return
    def e7_on_return_pressed(self):
        self.e8Locales.setFocus()
        return
    def e8_on_return_pressed(self):
        self.e1Locales.setFocus()
        return
        
    def openContextMenuLocales(self, position):
        indexes = self.treeLocales.selectedIndexes()
        if indexes:
            index = self.proxyModelLocales.mapToSource(indexes[0])
            file_path = self.modelLocales.filePath(index)
            
            font = QFont(genv.v__app__font, 11)
            font.setBold(True)
            
            # Popup-Menü erstellen
            menu = QMenu()
            menu.setFont(font)
            menu.setStyleSheet(_("menu_css"))
            
            # Aktionen zum Menü hinzufügen
            newone_action = QAction("New Project ...", self)
            openex_action = QAction("Open", self)
            rename_action = QAction("Rename", self)
            tempel_action = QAction("Template", self)
            
            menu.addAction(newone_action)
            menu.addAction(openex_action)
            menu.addAction(rename_action)
            menu.addAction(tempel_action)
            
            # Aktionen verbinden
            newone_action.triggered.connect(lambda: self.newoneLocales(file_path))
            openex_action.triggered.connect(lambda: self.openexLocales(file_path))
            rename_action.triggered.connect(lambda: self.renameLocales(file_path))
            tempel_action.triggered.connect(lambda: self.tempelLocales(file_path))
            
            menu.exec_(self.treeLocales.viewport().mapToGlobal(position))
    
    def newoneLocales(self, filepath):
        print(filepath)
        return
    def openexLocales(self, filepath):
        print(filepath)
        return
    def renameLocales(self, filepath):
        print(filepath)
        return
    def tempelLocales(self, filepath):
        print(filepath)
        return
    
    def openFile(self, file_path):
        print(f"Opening file: {file_path}")
        # Hier können Sie den Code hinzufügen, um die Datei zu öffnen
    
    def deleteFile(self, file_path):
        print(f"Deleting file: {file_path}")
        # Hier können Sie den Code hinzufügen, um die Datei zu löschen
    
    
    def btnOpenLocales_clicked(self):
        print("open locales")
        return
    
    def btnSaveLocales_clicked(self):
        print("save locales")
        return
    
    # commodore c64
    def onC64TabChanged(self, index):
        if index == 0 or index == 2:
            print("end")
            if not self.c64_screen.worker_thread == None:
                self.c64_screen.worker_thread.stop()
            self.worker_hasFocus = False
        elif index == 1:
            print("start")
            if not self.c64_screen.worker_thread == None:
                self.c64_screen.worker_thread.stop()
            self.c64_screen.worker_thread = None
            self.c64_screen.worker_thread = c64WorkerThread(self)
            self.c64_screen.worker_thread.start()
            self.worker_hasFocus = True
    
    def handleCommodoreC64(self):
        self.c64_tabs = QTabWidget()
        self.c64_tabs.setStyleSheet(css_tabs)
        self.c64_tabs.hide()
        
        
        self.c64_tabs_project_widget = QWidget()
        self.c64_tabs_editors_widget = QWidget()
        self.c64_tabs_designs_widget = QWidget()
        #
        self.c64_tabs.addTab(self.c64_tabs_project_widget, "C-64 Project")
        self.c64_tabs.addTab(self.c64_tabs_editors_widget, "C-64 Editor")
        self.c64_tabs.addTab(self.c64_tabs_designs_widget, "C-64 Designer")
        
        self.c64_layout = QVBoxLayout()
        self.c64_frame_oben  = QFrame()
        self.c64_frame_unten = QFrame()
        
        self.c64_frame_oben.setMinimumHeight(320)
        self.c64_frame_oben.setMaximumHeight(320)
        
        self.c64_frame_oben .setStyleSheet("background-color:lightgray;")
        self.c64_frame_unten.setStyleSheet("background-color:lightgray;")
        
        
        self.c64_keyboard_label = QLabel(self.c64_frame_unten)
        self.c64_keyboard_pixmap = QPixmap(genv.v__app__keybc64__)
        self.c64_keyboard_label.setPixmap(self.c64_keyboard_pixmap)
        
        
        #####
        c64_logo_label  = QLabel(self.c64_frame_unten)
        c64_logo_label_pixmap = QPixmap(genv.v__app__logoc64__)
        c64_logo_label.setPixmap(c64_logo_label_pixmap)
        c64_logo_label.move(502,1)
        #####
        
        
        self.c64_screen = c64Bildschirm(self.c64_frame_oben)
        
        self.c64_tabs.currentChanged.connect(self.onC64TabChanged)
        
        _listpush_apps = QPushButton("Applications")
        _listpush_game = QPushButton("Games")
        
        _listwidget = QListWidget()
        _listwidget.setViewMode  (QListView.IconMode)
        _listwidget.setResizeMode(QListView.Adjust)
        _listwidget.setStyleSheet("background-color:white;")
        
        _listwidget   .setParent(self.c64_frame_oben)
        _listpush_apps.setParent(self.c64_frame_oben)
        _listpush_game.setParent(self.c64_frame_oben)
        
        font = QFont(genv.v__app__font, 11)
        font.setBold(True)
        
        _listwidget   .move(430,40); _listwidget   .resize(400,200)
        _listpush_apps.move(430,10); _listpush_apps.resize(100,30)
        _listpush_game.move(540,10); _listpush_game.resize(100,30)
        #
        _listpush_apps.setFont(font)
        _listpush_game.setFont(font)
        
        c64_disc1_label  = QLabel(self.c64_frame_oben)
        c64_disc1_pixmap = QPixmap(genv.v__app__discc64__)
        c64_disc1_label.setPixmap(c64_disc1_pixmap)
        #
        c64_disc2_label  = QLabel(self.c64_frame_oben)
        c64_disc2_pixmap = QPixmap(genv.v__app__discc64__)
        c64_disc2_label.setPixmap(c64_disc2_pixmap)
        #
        c64_mc1_label  = QLabel(self.c64_frame_oben)
        c64_mc1_pixmap = QPixmap(genv.v__app__datmc64__)
        c64_mc1_label.setPixmap(c64_mc1_pixmap)
        #
        
        #
        c64_disc1_label.move(440,240)
        c64_disc2_label.move(540,240)
        c64_mc1_label  .move(690,240)
        
        
        self.c64_layout.addWidget(self.c64_frame_oben)
        self.c64_layout.addWidget(self.c64_frame_unten)
        
        self.c64_tabs_editors_widget.setLayout(self.c64_layout)
        
        ####
        self.main_layout.addWidget(self.c64_tabs)
    
    def closeEvent(self, event):
        msg = QMessageBox()
        msg.setWindowTitle("Confirmation")
        msg.setText("Would you close the Application ?")
        msg.setIcon(QMessageBox.Question)
        
        btn_yes = msg.addButton(QMessageBox.Yes)
        btn_no  = msg.addButton(QMessageBox.No)
        
        msg.setStyleSheet(_("msgbox_css"))
        result = msg.exec_()
        
        if result == QMessageBox.Yes:
            if not self.c64_screen.worker_thread == None:
                self.c64_screen.worker_thread.stop()
            event.accept()
        else:
            event.ignore()
    
    # ------------------------------------------------------------------------
    # class member to get the widget item from list_widget_1 or list_widget_2.
    # The application script will stop, if an internal error occur ...
    # ------------------------------------------------------------------------
    def handle_item_click(self, item):
        tab_index = self.tab_widget_1.currentIndex()
        if tab_index == 1:
            for i in range(0, len(self.list_widget_2_elements)):
                if item.data(0) == self.list_widget_2_elements[i]:
                    print("t: " + str(i) + ": " + self.list_widget_2_elements[i])
                    self.hideTabItems_2(i)
                    s = "sv_2_" + str(i+1)
                    w = getattr(self, f"{s}")
                    w.show()
                    break
        elif tab_index == 0:
            for i in range(0, len(self.list_widget_1_elements)):
                if item.data(0) == self.list_widget_1_elements[i]:
                    self.hideTabItems_1(i)
                    s = "sv_1_" + str(i+1)
                    w = getattr(self, f"{s}")
                    w.show()
                    return
    
    def hideTabItems_1(self, it):
        for i in range(0, len(self.list_widget_1_elements)):
            s = "sv_1_" + str(i+1)
            w = getattr(self, f"{s}")
            w.hide()
            if i == it:
                w.show()
    
    def hideTabItems_2(self, it):
        for i in range(0, len(self.list_widget_2_elements)):
            s = "sv_2_" + str(i+1)
            w = getattr(self, f"{s}")
            w.hide()
            if i == it:
                w.show()
    
    # project tab: top push
    def tab0_fold_push1_clicked(self):
        oldtext = self.tab0_fold_userd
        openDir = str(QFileDialog.getExistingDirectory(self,
        "Select Directory"))
        if len(openDir.strip()) < 1:
            self.tab0_fold_edit1.setText(self.tab0_fold_userd)
            self.tab0_fold_edit1_return()
        else:
            self.tab0_fold_userd = openDir
            self.tab0_fold_edit1_return()
    
    def tab0_fold_edit1_return(self):
        oldtext = self.tab0_fold_userd.strip()
        
        self.tab0_fold_userd = self.tab0_fold_userd \
        .replace(":" ,"/") \
        .replace("\\","/") \
        .replace("//","/")
        
        if not self.tab0_fold_userd.startswith("/"):
            self.tab0_fold_userd = "/" + self.tab0_fold_userd
        
        is_windows = any(platform.win32_ver())
        if is_windows:
            windowsdir = self.tab0_fold_userd[1:2] + ":" + self.tab0_fold_userd[2:]
            windowsdir = windowsdir.replace("/", "\\")
        else:
            windowsdir = self.tab0_fold_userd
        
        if os.path.exists(windowsdir) and os.path.isdir(windowsdir):
            self.tab0_dir_model .setRootPath(windowsdir)
            self.tab0_file_model.setRootPath(windowsdir)
            #
            self.tab0_file_tree.setRootIndex(self.tab0_dir_model.index(windowsdir))
            #self.tab0_file_list.setRootIndex(self.tab0_file_model_proxy.index(windowsdir))
            #
            self.tab0_fold_edit1.setText(self.tab0_fold_userd)
        else:
            self.tab0_fold_userd = oldtext
            self.tab0_dir_model .setRootPath(oldtext)
            self.tab0_file_model.setRootPath(oldtext)
            #
            self.tab0_file_tree.setRootIndex(self.tab0_dir_model.index(oldtext))
            self.tab0_file_list.setRootIndex(self.tab0_file_model_proxy.mapFromSource(self.tab0_file_model.index(oldtext)))
            #
            self.tab0_fold_edit1.setText(self.tab0_fold_userd)
    
    def generate_random_string(self, length):
        characters = string.ascii_uppercase + string.digits
        random_string = ''.join(random.sample(characters, length))
        return random_string
    
    # pre-fixed
    def button_clicked_preadd(self):
        random_string = self.generate_random_string(random.randint(8,32))
        item = QListWidgetItem(random_string)
        self.tab1_preActionList.addItem(item)
        return
    
    def button_clicked_preDel(self):
        listItems = self.tab1_preActionList.selectedItems()
        if not listItems: return        
        for item in listItems:
            self.tab1_preActionList.takeItem(self.tab1_preActionList.row(item))
        return
    
    def button_clicked_preClr(self):
        self.tab1_preActionList.clear()
        return
    
    # post-fixed
    def button_clicked_postadd(self):
        random_string = self.generate_random_string(random.randint(8,32))
        item = QListWidgetItem(random_string)
        self.tab1_postActionList.addItem(item)
        return
    
    def button_clicked_postDel(self):
        listItems = self.tab1_postActionList.selectedItems()
        if not listItems: return        
        for item in listItems:
            self.tab1_postActionList.takeItem(self.tab1_postActionList.row(item))
        return
    
    def button_clicked_postClr(self):
        self.tab1_postActionList.clear()
        return
    
    def startWatching(self):
        # Timer starten
        self.interval = int(self.tab1_timeComboBox.currentText())
        self.currentTime = self.interval
        self.updateCountdownLabel()
        self.timer.start(1000)
    
    def stopWatching(self):
        # Timer stoppen
        self.timer.stop()
        self.tab1_countdownLabel.setText('Select time.')
    
    def updateCountdown(self):
        self.currentTime -= 1
        if self.currentTime <= 0:
            self.currentTime = self.interval
            # Dateiüberwachung ausführen
            self.checkFileExistence()
        self.updateCountdownLabel()
    
    def updateCountdownLabel(self):
        self.tab1_countdownLabel.setText(f'Next check in: {self.currentTime} Seconds')
    
    def checkFileExistence(self):
        filePath = self.tab1_path_lineEdit.text()
        if os.path.exists(filePath):
            print(f"File {filePath} exists.")
            # weitere Aktionen durchführen, wenn die Datei existiert
        else:
            print(f"File {filePath} not found.")
            # ktionen durchführen, wenn die Datei nicht existiert

# ------------------------------------------------------------------------
# inform the user about the rules/license of this application script ...
# ------------------------------------------------------------------------
class licenseWindow(QDialog):
    def __init__(self):
        super().__init__()
        
        self.returnCode = 0
        
        self.file_content = ""
        self.file_path = os.path.join(genv.v__app__internal__, "LICENSE")
        try:
            with open(self.file_path, "r") as file:
                self.file_content = file.read()
            
        except FileNotFoundError:
            print("error: license file not found.")
            print("abort.")
            sys.exit(genv.EXIT_FAILURE)
            
        except Exception as e:
            exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
            tb = traceback.extract_tb(e.__traceback__)[-1]
            
            print(f"Exception occur at license view:")
            print(f"type : {exc_type.__name__}")
            print(f"value: {exc_value}")
            print(misc.StringRepeat("-",40))
            #
            print(f"file : {tb.filename}")
            print(f"line : {tb.lineno}")
            #
            print(misc.StringRepeat("-",40))
            sys.exit(genv.EXIT_FAILURE)
        
        self.setWindowTitle("LICENSE - Please read, before you start.")
        self.setMinimumWidth(820)
        
        font = QFont("Courier New", 10)
        self.setFont(font)
        
        layout = QVBoxLayout()
        
        button1 = QPushButton("Accept")
        button2 = QPushButton("Decline")
        
        button1.clicked.connect(self.button1_clicked)
        button2.clicked.connect(self.button2_clicked)
        
        textfield = QTextEdit(self)
        textfield.setReadOnly(True)
        
        layout.addWidget(textfield)
        layout.addWidget(button1)
        layout.addWidget(button2)
        
        self.setLayout(layout)
        
        # ---------------------------------------------------------
        # get license to front, before the start shot ...
        # ---------------------------------------------------------
        textfield.setPlainText(self.file_content)
    
    def button1_clicked(self):
        #self.returnCode = 0
        self.close()
    
    def button2_clicked(self):
        #self.returnCode = 1
        #self.close()
        sys.exit(genv.EXIT_FAILURE)

# ------------------------------------------------------------------------
# atexit: callback when sys.exit() is handled, and come back to console...
# ------------------------------------------------------------------------
def ApplicationAtExit():
    print("Thank's for using.")
    return

# ------------------------------------------------------------------------
# this is our "main" entry point, where the application will start.
# ------------------------------------------------------------------------
def EntryPoint(arg1=None):
    atexit.register(ApplicationAtExit)
    
    genv.v__app__comment_hdr  = ("# " + misc.StringRepeat("-",78) + "\n")
    
    global conn
    global conn_cursor
    
    error_fail    = False
    error_result  = 0
    
    topic_counter = 1
    
    #if not arg1 == None:
    #    genv.v__app__scriptname__ = arg1
    #    print("--> " + genv.v__app__scriptname__)
    #    if not os.path.exists(genv.v__app__scriptname__):
    #        print("script does not exists !")
    #        error_result = 1
    #        sys.exit(1)
    
    # ---------------------------------------------------------
    # init pascal interpreter ...
    # ---------------------------------------------------------
    #pas = interpreter_Pascal()
    #pas.ShowInstructions()
    #pas.Emulate()
    
    #sys.exit(1)
    
    # ---------------------------------------------------------
    # scoped global stuff ...
    # ---------------------------------------------------------
    pcount     = len(sys.argv) - 1
    
    # ---------------------------------------------------------
    # doxygen.exe directory path ...
    # ---------------------------------------------------------
    if not genv.doxy_env in os.environ:
        if genv.v__app__debug == True:
            os.environ["DOXYGEN_PATH"] = "E:/doxygen/bin"
        else:
            try:
                print(genv.v__app__config.get("doxygen","path"))
            except Exception as e:
                showError("error: "
                "no section: 'doxygen' or option: 'path'\n"
                "(missing) in observer.ini")
                sys.exit(1)
            
            file_path = genv.v__app__config["doxygen"]["path"]
            
            if len(file_path) < 1:
                showError("error: " + genv.doxy_env +
                " is not set in your system settings.")
                sys.exit(genv.EXIT_FAILURE)
            else:
                os.environ["DOXYGEN_PATH"] = file_path
    else:
        genv.doxy_path = os.environ[genv.doxy_env]
    
    # ---------------------------------------------------------
    # Microsoft Help Workshop path ...
    # ---------------------------------------------------------
    if not genv.doxy_hhc in os.environ:
        if genv.v__app__debug == True:
            os.environ["DOXYHHC_PATH"] = "E:/doxygen/hhc"
        else:
            try:
                file_path = genv.v__app__config["doxygen"]["hhc"]
            except Exception as e:
                showError("error: "
                "no section: 'doxygen' or option: 'hhc'\n"
                "(missing) in observer.ini")
                sys.exit(1)
            
            file_path = genv.v__app__config["doxygen"]["hhc"]
            
            if len(file_path) < 1:
                showError("error: " + genv.doxy_hhc +
                " is not set in your system settings.")
                sys.exit(genv.EXIT_FAILURE)
            else:
                os.environ["DOXYHHC_PATH"] = file_path
    else:
        genv.hhc__path = os.environ[genv.doxy_hhc]
    
    # ---------------------------------------------------------
    # first, we check the operating system platform:
    # 0 - unknown
    # 1 - Windows
    # 2 - Linux
    # ---------------------------------------------------------
    global os_type, os_type_windows, os_type_linux
    
    os_type_unknown = 0
    os_type_windows = 1
    os_type_linux   = 2
    
    os_type = os_type_windows
    
    # -----------------------------------------------------
    # show a license window, when readed, and user give a
    # okay, to accept it, then start the application ...
    # -----------------------------------------------------
    genv.v__app_object = QApplication(sys.argv)
    
    license_window = licenseWindow()
    # -------------------------------
    # close tje splash screen ...
    # -------------------------------
    if getattr(sys, 'frozen', False):
        pyi_splash.close()
        
    license_window.exec_()
    
    # ---------------------------------------------------------
    # when config.ini does not exists, then create a small one:
    # ---------------------------------------------------------
    if not os.path.exists(genv.v__app__config_ini):
        with open(genv.v__app__config_ini, "w", encoding="utf-8") as output_file:
            content = (""
            + "[common]\n"
            + "language = en_us\n")
            output_file.write(content)
            output_file.close()
            ini_lang = "en_us" # default is english; en_us
    else:
        try:
            genv.v__app__config.read(genv.v__app__config_ini)
            ini_lang = genv.v__app__config.get("common", "language")
        except:
            ini_lang = "en_us"
            pass
    
    _ = handle_language(ini_lang)
    
    # ---------------------------------------------------------
    # when config file not exists, then spite a info message,
    # and create a default template for doxygen 1.10.0
    # ---------------------------------------------------------
    if not os.path.exists(genv.doxyfile):
        print("info: config: '" \
        + f"{genv.doxyfile}" + "' does not exists. I will fix this by create a default file.")
        
        file_content_warn = [
            ["QUIET", "YES"],
            ["WARNINGS", "YES"],
            ["",""],
            ["WARN_IF_UNDOCUMENTED", "NO"],
            ["WARN_IF_UNDOC_ENUM_VAL", "NO"],
            ["WARN_IF_DOC_ERROR", "YES"],
            ["WARN_IF_INCOMPLETE_DOC", "YES"],
            ["WARN_AS_ERROR", "NO"],
            ["WARN_FORMAT", "\"$file:$line: $text\""],
            ["WARN_LINE_FORMAT", "\"at line $line of file $file\""],
            ["WARN_LOGFILE", "warnings.log"]
        ]
        with open(doxyfile, 'w') as file:
            file.write(genv.v__app__comment_hdr)
            file.write("# File: Doxyfile\n")
            file.write("# Author: (c) 2024 Jens Kallup - paule32 non-profit software\n")
            file.write("#"  + (" " *  9) + "all rights reserved.\n")
            file.write("#\n")
            file.write("# optimized for: # Doxyfile 1.10.1\n")
            file.write(genv.v__app__comment_hdr)
            
            for i in range(0, len(file_content)):
                if len(file_content[i][0]) > 1:
                    file.write("{0:<32} = {1:s}\n".format( \
                    file_content[i][0],\
                    file_content[i][1]))
                else:
                    file.write("\n")
            
            file.write(genv.v__app__comment_hdr)
            file.write("# warning settings ...\n")
            file.write(genv.v__app__comment_hdr)
            
            for i in range(0, len(file_content_warn)):
                if len(file_content_warn[i][0]) > 1:
                    file.write("{0:<32} = {1:s}\n".format( \
                    file_content_warn[i][0],\
                    file_content_warn[i][1]))
                else:
                    file.write("\n")
            
            file.close()
    
    global sv_help
    sv_help = customScrollView_help()
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H:%M:%S")
    
    conn = sqlite3.connect(os.path.join(genv.v__app__internal__, "data.db"))
    conn_cursor = conn.cursor()
    conn.close()
    
    try:
        if genv.v__app_object == None:
            genv.v__app_object = QApplication(sys.argv)
        
        genv.v__app_win = FileWatcherGUI()
        genv.v__app_win.move(100, 100)
        genv.v__app_win.exec_()
        
    except UnboundLocalError as e:
        tb = traceback.extract_tb(e.__traceback__)
        filename, lineno, funcname, text = tb[-1]
        if genv.v__app_win == None:
            print(f"Exception: {e}")
            print(f"Error occurred in file: {filename}")
            print(f"Function: {funcname}")
            print(f"Line number: {lineno}")
            print(f"Line text: {text}")
        else:
            txt = (
                f"Exception: {e}\n"
                f"Error occurred in file: {filename}\n"
                f"Function: {funcname}\n"
                f"Line number: {lineno}\n"
                f"Line text: {text}")
            #
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText(txt)
            msg.setIcon(QMessageBox.Warning)
            
            btn_ok = msg.addButton(QMessageBox.Ok)
            
            msg.setStyleSheet(_("msgbox_css"))
            msg.exec_()

# ---------------------------------------------------------------------------
# parse binary data:
# --------------------------------------------------------------------------
class parserBinary:
    def __init__(self, script_name):
        try:
            # ---------------------
            # load binary code ...
            # ---------------------
            with open(script_name,"rb") as self.bytefile:
                self.bytecode = self.bytefile.read()
                self.bytefile.close()
            # ---------------------
            # execute binary code:
            # ---------------------
            self.byte_code = marshal.loads(self.bytecode)
            exec(self.byte_code)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

# ---------------------------------------------------------------------------
# parse dBase script ...
# ---------------------------------------------------------------------------
class parserDBasePoint:
    def __init__(self, script_name):
        prg = None
        prg = dBaseDSL(script_name)
        try:
            prg.parse()
            #prg.run()
        except ENoParserError as noerror:
            prg.finalize()
            print("\nend of data")

# ---------------------------------------------------------------------------
# parse Doxyfile script ...
# ---------------------------------------------------------------------------
class parserDoxyGen:
    def __init__(self, script_name):
        prg = doxygenDSL(script_name)
        try:
            prg.parse()
            #prg.run()
        except ENoParserError as noerror:
            prg.finalize()
            print("\nend of data")

# ---------------------------------------------------------------------------
# parse Pascal script ...
# ---------------------------------------------------------------------------
class parserPascalPoint:
    def __init__(self, script_name):
        self.prg = None
        self.prg = interpreter_Pascal(script_name)
        try:
            self.prg.parse()
            #self.prg.run()
        except ENoParserError as noerror:
            self.finalize()
            print("\nend of data")

# ---------------------------------------------------------------------------
# the mother of all: the __main__ start point ...
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    
    # The Python 2.7+ or 3.3+ is required.
    major = sys.version_info[0]
    minor = sys.version_info[1]
    if (major == 2 and minor < 7) or (major == 3 and minor < 0):
        print("Python 2.7+ or Python 3.0+ are required for the script")
        sys.exit(1)
    
    # Determine the path to the script and its name.
    script = os.path.abspath(sys.argv[0])
    script_path, script_name = os.path.split(script)
    script_path = os.path.abspath(script_path)    
    
    genv.v__app__observers = "observer --"
    genv.v__app__file__    = "file."
    genv.v__app__space__   = "       "
    genv.v__app__parameter = (""
    + "Usage: "            + genv.v__app__observers + "dbase   " + genv.v__app__file__ + "prg\n"
    + genv.v__app__space__ + genv.v__app__observers + "pascal  " + genv.v__app__file__ + "pas\n"
    + genv.v__app__space__ + genv.v__app__observers + "doxygen " + genv.v__app__file__ + "dox\n"
    + genv.v__app__space__ + genv.v__app__observers + "exec    " + genv.v__app__file__ + "bin\n"
    + genv.v__app__space__ + genv.v__app__observers + "gui\n")
    
    genv.v__app__tmp3 = "parse..."
    if len(sys.argv) < 2:
        print("no arguments given.")
        print(genv.v__app__parameter)
        sys.exit(1)
    
    if len(sys.argv) >= 1:
        if sys.argv[1] == "--gui":
            #if len(sys.argv) == 2:
            #    sys.argv.append("test.txt")
            #genv.v__app__scriptname__ = sys.argv[2]
            #handleExceptionApplication(EntryPoint,genv.v__app__scriptname__)
            handleExceptionApplication(EntryPoint)
            sys.exit(0)
        elif sys.argv[1] == "--doxygen":
            if len(sys.argv) == 2:
                sys.argv.append("Doxyfile")
            genv.v__app__scriptname__ = sys.argv[2]
            handleExceptionApplication(parserDoxyGen,sys.argv[2])
            sys.exit(0)
        elif sys.argv[1] == "--exec":
            genv.v__app__scriptname__ = sys.argv[2]
            handleExceptionApplication(parserBinary,sys.argv[2])
        elif sys.argv[1] == "--dbase":
            print(genv.v__app__tmp3)
            try:
                handleExceptionApplication(parserDBasePoint,sys.argv[2])
                sys.exit(0)
            except Exception as ex:
                sys.exit(1)
        elif sys.argv[1] == "--pascal":
            print(genv.v__app__tmp3)
            genv.v__app__scriptname__ = sys.argv[2]
            handleExceptionApplication(parserPascalPoint,sys.argv[2])
            sys.exit(0)
        else:
            print("parameter unknown.")
            print(genv.v__app__parameter)
            sys.exit(1)
        
# ----------------------------------------------------------------------------
# E O F  -  End - Of - File
# ----------------------------------------------------------------------------
