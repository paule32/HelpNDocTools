# ---------------------------------------------------------------------------
# File:   client.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# global used application stuff. try to catch import exceptions ...
# ---------------------------------------------------------------------------
global os_name; os_name = ""
global res_file

res_file = 'resources_rc.cpython-313.pyc.gz'  # we use Python 3.13.3 !

# Dictionary to store the mapping from object instances to variable names
instance_names = {}

import importlib
import subprocess
import sys            # system specifies
import os             # operating system stuff
import platform

from   io     import StringIO

# ---------------------------------------------------------------------------
# support only for Microsoft Windows
# ---------------------------------------------------------------------------
if sys.platform.startswith("win"):
    print("Info: This application is optimized to run under Windows.")
    import ctypes
    from   ctypes import wintypes

    # -----------------------------------------------------------------------
    # Windows API structure for LOGFONT
    # -----------------------------------------------------------------------
    class LOGFONT(ctypes.Structure):
        _fields_ = [
            ("lfHeight"         , wintypes.LONG),
            ("lfWidth"          , wintypes.LONG),
            ("lfEscapement"     , wintypes.LONG),
            ("lfOrientation"    , wintypes.LONG),
            ("lfWeight"         , wintypes.LONG),
            ("lfItalic"         , wintypes.BYTE),
            ("lfUnderline"      , wintypes.BYTE),
            ("lfStrikeOut"      , wintypes.BYTE),
            ("lfCharSet"        , wintypes.BYTE),
            ("lfOutPrecision"   , wintypes.BYTE),
            ("lfClipPrecision"  , wintypes.BYTE),
            ("lfQuality"        , wintypes.BYTE),
            ("lfPitchAndFamily" , wintypes.BYTE),
            ("lfFaceName"       , wintypes.CHAR * 32)
        ]
    # ---------------------------------------------------------------------
    # entry point:
    # ---------------------------------------------------------------------
    ENUMFONTEXPROC = ctypes.WINFUNCTYPE(
        wintypes.INT,
        wintypes.LPARAM,
        wintypes.LPARAM,
        wintypes.DWORD,
        ctypes.POINTER(wintypes.LPARAM)
    )
    
if not "64bit" in platform.architecture():
    print("Error: This application is optimized for Windows 64-Bit.")
    sys.exit(1)
# ---------------------------------------------------------------------------

import traceback      # stack exception trace back

# ---------------------------------------------------------------------------
try:
    # -----------------------------------------------------------------------
    # under the windows console, python paths can make problems ...
    # -----------------------------------------------------------------------
    if 'PYTHONHOME' in os.environ:
        del os.environ['PYTHONHOME']
    if 'PYTHONPATH' in os.environ:
        del os.environ['PYTHONPATH']
    
    # -----------------------------------------------------------------------
    # error output function
    # -----------------------------------------------------------------------
    def DebugPrint(*args, **kwargs):
        #print((*args):", args)
        #print((**kwargs):", kwargs)
        
        # Beispiel: Verarbeitung der Argumente
        for i, arg in enumerate(args, start=1):
            print(f"{arg}")
        
        for key, value in kwargs.items():
            print(f"{key}: {value}")
    
    # ------------------------------------------------------------------------
    # check for installed modules ...
    # ------------------------------------------------------------------------
    def check_and_install_module():
        required_modules = [
            "dbf", "polib", "requests", "timer", "datetime", "gmpy2", "webbrowser",
            "locale", "io", "random", "ipapi", "ipcore", "string", "capstone",
            "httpx", "httpx-auth", "ctypes", "sqlite3", "configparser", "traceback",
            "marshal", "inspect", "logging", "PyQt5", "pathlib", "rich", "string",
            "codecs", 'screeninfo'
        ]
        
        for module in required_modules:
            try:
                importlib.import_module(module)
                DebugPrint(f"{module} is already installed.")
            except ImportError:
                try:
                    DebugPrint(f"error: {module} not found. Installing...")
                    result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--user", module],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                    DebugPrint(f"{module} installed successfully.")
                except:
                    try:
                        DebugPrint(f"error: upgrade pip...")
                        result = subprocess.run(
                        [sys.executable, "-m", "pip", "--upgrade", "pip"],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                        DebugPrint(f"info: pip installer upgrade ok.")
                        #
                        result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--user", module],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                        #
                    except Exception as e:
                        print(e)
                        DebugPrint(f"error: {module}: install fail.")
                        sys.exit(1)
    
    # ---------------------------------------------------------
    # check, if font installed ...
    # ---------------------------------------------------------
    def font_check_callback(lpelfe, lpntme, font_type, lparam):
        font_name = "Consolas"
        lf = ctypes.cast(lpelfe, ctypes.POINTER(LOGFONT)).contents
        if font_name.lower() == lf.lfFaceName.decode("utf-8").lower():
            lparam[0] = True
            return 0
        return 1
    
    # ---------------------------------------------------------
    # Lädt eine Schriftart aus einer Datei und gibt ihren
    # Namen zurück.
    # ---------------------------------------------------------
    def load_custom_font(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id == -1:
            print("Error: could not load font.")
            return None
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            return font_families[0]
        return None
        
    def font_check_installed(font_name):
        if sys.platform.startswith("win"):
            # ---------------------------------------------------------------------
            # windows: Handle zum Geräte-Kontext
            # ---------------------------------------------------------------------
            if os_name == "windows":
                hdc = ctypes.windll.user32.GetDC(0)
                
                # Erzeuge ein LOGFONT-Objekt
                logfont = LOGFONT()
                logfont.lfCharSet = 0  # DEFAULT_CHARSET
                
                # Überprüfungsvariable
                found = [False]
                
                # EnumFontFamiliesExW aufrufen
                ctypes.windll.gdi32.EnumFontFamiliesExW(
                    hdc,
                    ctypes.byref(logfont),
                    ENUMFONTEXPROC(font_check_callback),
                    ctypes.byref(ctypes.c_long(found[0])),
                    0
                )
                
                # Geräte-Kontext freigeben
                ctypes.windll.user32.ReleaseDC(0, hdc)
                
                return found[0]
        # ---------------------------------------------------------------------
        # linux:
        # ---------------------------------------------------------------------
        elif sys.platform.startswith("linux"):
            # TODO: Linux install ...
            font_path = ""
        
        return False
    
    # ---------------------------------------------------------
    # Überprüft, ob das Skript mit Administratorrechten
    # ausgeführt wird.
    # ---------------------------------------------------------
    def is_admin():
        try:
            if sys.platform.startswith("win"):
                return ctypes.windll.shell32.IsUserAnAdmin()
            elif os_name == "linux":
                return os.getuid() == 0
            else:
                return False
        except:
            print(_("Error:\ncold not determine admin or user mode."))
            print(_("abort."))
            return False
    
    # ---------------------------------------------------------
    # Startet das Programm neu ohne Administratorrechte.
    # ---------------------------------------------------------
    def drop_admin_privileges():
        try:
            if sys.platform.startswith("win"):
                # Token eines Standardbenutzers anfordern
                ctypes.windll.shell32.IsUserAnAdmin()
                shell_exec = ctypes.windll.shell32.ShellExecuteW
                shell_exec(None, "open", sys.executable, ' '.join(sys.argv), None, 1)
                DebugPrint("Neuer Prozess ohne Administratorrechte gestartet.")
                sys.exit(0)
            else:
                print("TODO admin")
                
        except Exception as e:
            DebugPrint(f"Fehler beim Entfernen der Administratorrechte: {e}")
            sys.exit(1)
    
    # ---------------------------------------------------------
    # Startet das Skript mit Administratorrechten.
    # ---------------------------------------------------------
    def run_as_admin():
        return
        if not is_admin():
            # Versuche, das Skript mit Administratorrechten neu zu starten
            script = sys.argv[0]
            params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
            try:
                if sys.platform.startswith("win"):
                    ctypes.windll.shell32.ShellExecuteW(
                        None, "runas", sys.executable, f'"{script}" {params}', None, 1
                    )
                    #sys.exit(0)
                    raise Exception("TODO: Admin")
                else:
                    raise Exception("TODO: root")
            except Exception as e:
                DebugPrint(f"Error: could not switch to admin: {e}")
                #sys.exit(1)
    
    # ---------------------------------------------------------
    # Installiert einen TrueType-Font (.ttf) auf Windows.
    # ---------------------------------------------------------
    def install_font(font_path):
        return
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font-Datei nicht gefunden: {font_path}")
        try:
            if sys.platform.startswith("win"):
                font_added = ctypes.windll.gdi32.AddFontResourceExW(font_path, FR_PRIVATE, None)
                if font_added == 0:
                    raise RuntimeError(f"Fehler beim Hinzufügen des Fonts: {font_path}")
        except RuntimeError as e:
            print(e)
            sys.exit(1)
        except Exception as e:
            print(e)
            sys.exit(1)
        
        if sys.platform.startswith("win"):
            hwnd_broadcast = 0xFFFF
            ctypes.windll.user32.SendMessageW(hwnd_broadcast, WM_FONTCHANGE, 0, 0)
        
        DebugPrint(f"SUCCESSFUL: font installed: {font_path}")
        
    # ---------------------------------------------------------------------
    # Fügt den Font dauerhaft zur Windows-Schriftartenliste hinzu,
    # indem er in der Registry registriert wird.
    # :param font_name: Der Name des Fonts (wie er angezeigt werden soll).
    # :param font_path: Der absolute Pfad zur Schriftartdatei (.ttf).
    # ---------------------------------------------------------------------
    def add_font_to_registry(font_name, font_path):
        if sys.platform.startswith("win"):
            fonts_key = r"Software\Microsoft\Windows NT\CurrentVersion\Fonts"
            try:
                with reg.OpenKey(            \
                    reg.HKEY_LOCAL_MACHINE,  \
                    fonts_key, 0,            \
                    reg.KEY_SET_VALUE) as key:
                    reg.SetValueEx(key, font_name, 0, reg.REG_SZ, font_path)
                    DebugPrint(f"Font in Registry eingetragen: {font_name}")
            except PermissionError:
                raise PermissionError(""
                + "Administratorrechte erforderlich, um den Font "
                + "in die Registry einzutragen.")
                sys.exit(1)
    
    try:
        foo = os.environ["observer_second"]
    except:
        os.environ["observer_second"] = ""
    
    # ---------------------------------------------------------------------
    # try to find, and instal C64 Pro Mono Font ...
    # ---------------------------------------------------------------------
    if not font_check_installed("C64 Pro Mono"):
        if sys.platform.startswith("win"):
            if os.environ["observer_second"] == "":
                check_and_install_module()
                os.environ["observer_second"] = "true"
                
                # ---------------------------------------------------------
                # Definieren der Windows-Konstanten
                # Installiert die Schriftart nur für die laufende Sitzung
                # ---------------------------------------------------------
                FR_PRIVATE    = 0x10  
                WM_FONTCHANGE = 0x001D
                
                import winreg as reg
                
                if not is_admin():
                    DebugPrint("ATTENTION: Admin rights requered for first start.")
                    run_as_admin()
                else:
                    DebugPrint(_("ATTENTION: Application run in Admin mode !"))
                
                c64_normal = "/_internal/fonts/C64_Pro-STYLE.ttf"
                c64_mono   = "/_internal/fonts/C64_Pro_Mono-STYLE.ttf"
                #
                font_file         = os.getcwd() + c64_mono
                font_display_name = "C64 Pro Mono"
                #
                install_font(font_file)
                #add_font_to_registry(font_display_name, font_file)
                
                DebugPrint("font OK")
        elif sys.platform.startswith("linux"):
            font_path = "/_internal/fonts/C64_Pro_Mono-STYLE.ttf"
            font_name = load_custom_font(font_path)
        else:
            print(_("no more supported operating system"))
            sys.exit(1)
    
    # ---------------------------------------------------------------------
    # this is a double check for application imports ...
    # ---------------------------------------------------------------------
    import re             # regular expression handling
    import requests       # get external url stuff
    import itertools

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
    import importlib.util # for resources import
    
    import pkgutil        # attached binary data utils
    import ast            # string to list
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
    import webbrowser

    import textwrap
    import marshal        # bytecode exec
    import inspect        # stack
    import gc             # garbage collector

    import logging
    import dbf            # good old data base file

    import pefile         # MS-Windows PE executable image
    import capstone       # disassembly
    
    # ------------------------------------------------------------------------
    # asmjit for Python ...
    # ------------------------------------------------------------------------
    if sys.platform.startswith("win"):
        from peachpy        import *
        from peachpy.x86_64 import *

    # ------------------------------------------------------------------------
    # windows os stuff ...
    # ------------------------------------------------------------------------
    if sys.platform.startswith("win"):
        try:
            import win32api
            import win32con
            
        except ImportError as e:
            match = re.search(r"No module named '([^']+)'", str(e))
            if match:
                missing_module = match.group(1)
                if missing_module == "win32api" \
                or missing_module == "win32con":
                    print("Win32Api functions not available.")
                
    from screeninfo import get_monitors

    # ------------------------------------------------------------------------
    # gnu multi precision version 2 (gmp2 for python)
    # ------------------------------------------------------------------------
    import gmpy2
    from   gmpy2 import mpz, mpq, mpfr, mpc

    # ------------------------------------------------------------------------
    # Qt5 gui framework
    # ------------------------------------------------------------------------
    from PyQt5.QtWidgets            import *
    from PyQt5.QtCore               import *
    from PyQt5.QtGui                import *
    from PyQt5.QtWebEngineWidgets   import *
    from PyQt5.QtNetwork            import *
    from PyQt5.QtWebChannel         import *
    
    # ------------------------------------------------------------------------
    # disassembly library
    # ------------------------------------------------------------------------
    from capstone import Cs, CS_ARCH_X86, CS_MODE_64
    
    # ------------------------------------------------------------------------
    # query IP addresses ...
    # ------------------------------------------------------------------------
    import ipapi
    import httpx
    
    import types
    from   types import *
    
except ImportError as e:
    # Extrahiere den Modulnamen aus der Fehlermeldung
    match = re.search(r"No module named '([^']+)'", str(e))
    if match:
        missing_module = match.group(1)
        DebugPrint(f"ImportError: Module '{missing_module}' could not be found.")
        DebugPrint(f"make sure, your are in the VENV of Python-Session.")
    else:
        DebugPrint(f"A ImportError was occured: {e}")
except FileNotFoundError as e:
    DebugPrint(e)
    sys.exit(1)
except PermissionError as e:
    DebugPrint(e)
    sys.exit(1)
except RuntimeError as e:
    DebugPrint(e)
    sys.exit(1)
except Exception as e:
    exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
    tb = traceback.extract_tb(e.__traceback__)[-1]
    
    DebugPrint(f"Exception occur:")
    DebugPrint(f"type : {exc_type.__name__}")
    DebugPrint(f"value: {exc_value}")
    DebugPrint(("-" * 40))
    #
    DebugPrint(f"file : {tb.filename}")
    DebugPrint(f"line : {tb.lineno}")
    sys.exit(1)

if getattr(sys, 'frozen', False):
    import pyi_splash

# ------------------------------------------------------------------------
# \brief  Überprüft, ob der String Unicode-Zeichen enthält, die nicht
#         ASCII sind.
#
# \param  input_string: Der zu prüfende String
# \return True, wenn Unicode-Zeichen enthalten sind, ansonsten False
# ------------------------------------------------------------------------
def contains_unicode(input_string):
    return any(ord(char) > 127 for char in input_string)

# ---------------------------------------------------------------------------
class unexpectedParserException(Exception):
    def __init__(self, text, value=1):
        self.value    = str(value)
        self.message  = text
        super().__init__(value)

class noDataNoError(Exception):
    def __init__(self, text="no more data"):
        self.message = _(text)
        super().__init__(0)
        
class e_no_more_data(Exception):
    def __init__(self, text="no more data"):
        self.message = _(text)
        super().__init__(0)

class e_expr_error(Exception):
    def __init__(self, message="too many closed paren", line=1, code=0):
        self.message = message
        self.code    = code
        super().__init__(0)

class e_expr_empty(Exception):
    def __init__(self, message="expression is empty", line=1):
        self.message = message + _("\nat line: ") + str(line)
        super().__init__(0)

class IgnoreOuterException(Exception):
    pass

# ------------------------------------------------------------------------
# \brief Generates all case variations of the input string.
# ------------------------------------------------------------------------
def gen_case_var(input_string):
    # --------------------------------------------------
    # Separate characters into a list
    # --------------------------------------------------
    chars = list(input_string)
    
    # --------------------------------------------------
    # Generate combinations of lower and upper case for
    # alphabetic characters
    # --------------------------------------------------
    variations = [
        [c.lower(), c.upper()] if re.match(r'[a-zA-Z]', c) else [c]
        for c in chars
    ]
    
    # --------------------------------------------------
    # Create all combinations
    # --------------------------------------------------
    all_variations = [''.join(variation) for variation \
    in itertools.product(*variations)]
    
    return all_variations

# ------------------------------------------------------------------------
# check, if the gui application is initialized by an instance of app ...
# ------------------------------------------------------------------------
def isApplicationInit():
    if genv.v__app_object == None:
        genv.v__app_object = QApplication(sys.argv)
        return True
    # ----------------------------------------------
    if genv.v__app_object.instance() == None:
        genv.v__app_object = QApplication(sys.argv)
        return True
    return False

# ------------------------------------------------------------------------
# message box code place holder ...
# ------------------------------------------------------------------------
class showMessage(QDialog):
    def __init__(self, text="", msgtype=0):
        super(showMessage, self).__init__()
        #
        msgtypes = [
            [ QMessageBox.Information, "Information" ],
            [ QMessageBox.Warning,     "Warning" ],
            [ QMessageBox.Critical,    "Error" ],
            [ QMessageBox.Critical,    "Exception" ]
        ]
        
        self.setWindowTitle(msgtypes[msgtype][1])
        self.setMinimumWidth(700)
        
        text_lay = QVBoxLayout()
        text_box = QPlainTextEdit()
        text_box.setFont(QFont("Consolas", 10))
        text_box.document().setPlainText(text)
        
        if msgtype == 2:
            text_no = QPushButton(_("No"))
            text_ok = QPushButton(_("No"))
            #
            text_no.setMinimumHeight(32)
            text_ok.setMinimumHeight(32)
            #
            text_no.setStyleSheet(_("msgbox_css"))
            text_ok.setStyleSheet(_("msgbox_css"))
            #
            text_no.clicked.connect(self.no_click)
            text_ok.clicked.connect(self.ok_click)
        
        text_btn = QPushButton(_("Close"))
        text_btn.setMinimumHeight(32)
        text_btn.setStyleSheet(_("msgbox_css"))
        text_btn.clicked.connect(self.no_click)
        
        text_lay.addWidget(text_box)
        text_lay.addWidget(text_btn)
        
        self.setLayout(text_lay)
        self.exec_()
        
    def no_click(self):
        genv.LastResult = False
        self.close()
        return True
    
    def ok_click(self):
        genv.LastResult = True
        self.close()
        return True

# ------------------------------------------------------------------------
# code shortner definitions ...
# ------------------------------------------------------------------------
def showInfo(text):
    showMessage(text, 0)
    return
def showWarning(text):
    showMessage(text, 1)
    return
def showError(text):
    return showMessage(text, 2)
# ------------------------------------------------------------------------------
# \brief  This definition displays a exception dialog if some exception is raise
#         by the developer.
# ------------------------------------------------------------------------------
def showException(text):
    showMessage(text, 3)
    return

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
        
        self.v__app__name         = "observer"
        self.v__app__help         = "help"
        
        self.v__app__name_mo      = self.v__app__name + ".mo"
        self.v__app__help_mo      = self.v__app__help + ".mo"
        
        self.v__app__cdn_host     = "http://localhost/cdn"
        self.v__app__internal__   = os.path.join(self.v__app__modul__, "_internal")
        #
        self.v__app__logfile      = os.path.join(self.v__app__internal__, self.v__app__name) + ".log"
        self.v__app__config_ini   = os.path.join(self.v__app__internal__, self.v__app__name) + ".ini"
        self.v__app__config_ini_help    = ""
        self.v__app__logging      = None
        
        #self.v__app__img__int__   = os.path.join(self.v__app__internal__, "img")
        self.v__app__img__int__   = ":/images/_internal/img/"
        self.v__app__helprojects  = []
        
        im_path = self.v__app__img__int__
        
        self.isGuiApplication = False
        self.parent_array    = []
        
        self.start_idx = 1
        self.end_idx   = 1
        
        self.header_code = ""
        
        self.worker_thread = None

        # ------------------------------------------------------------------------
        # constants, and varibales that are used multiple times ...
        # ------------------------------------------------------------------------
        self.__copy__ = (""
            + "HelpNDoc.com FileWatcher 0.0.1\n"
            + "(c) 2024 by paule32\n"
            + "all rights reserved.\n")

        self.__error__os__error = (""
            + "can not determine operating system.\n"
            + "start aborted.")

        self.__error__locales_error = "" \
            + "no locales file for this application."
        
        self.LastResult = True
        
        self.v__app__cdn_flags = []
        
        # ---------------------------------------------------------------------------
        # \brief currently onle two converters are supported:
        #        0 - not sprecified => unknown
        #        1 - doxygen
        #        2 - helpndoc.com
        # ---------------------------------------------------------------------------
        self.HelpAuthoringConverterMode = 0
        
        self.v__app__donate1__  = im_path + "donate.png"
        #
        self.v__app__doxygen__  = im_path + "doxygen"
        self.v__app__hlpndoc__  = im_path + "helpndoc"
        self.v__app__helpdev__  = im_path + "help"
        self.v__app__pythonc__  = im_path + "python"
        self.v__app__lispmod__  = im_path + "lisp"
        self.v__app__prologm__  = im_path + "prolog"
        self.v__app__fortran__  = im_path + "fortran"
        self.v__app__ccpplus__  = im_path + "cpp"
        self.v__app__cpp1dev__  = im_path + "c"
        self.v__app__dbasedb__  = im_path + "dbase"
        self.v__app__javadev__  = im_path + "java"
        self.v__app__javascr__  = im_path + "javascript"
        self.v__app__javadoc__  = im_path + "javadoc"
        self.v__app__freepas__  = im_path + "freepas"
        self.v__app__locales__  = im_path + "locales"
        self.v__app__basicbe__  = im_path + "basic"
        self.v__app__pewin32__  = im_path + "windows"
        self.v__app__elfin32__  = im_path + "linux"
        self.v__app__console__  = im_path + "console"
        self.v__app__todopro__  = im_path + "todo"
        self.v__app__setupro__  = im_path + "setup"
        self.v__app__certssl__  = im_path + "ssl"
        self.v__app__githubp__  = im_path + "github"
        self.v__app__apache2__  = im_path + "apache"
        self.v__app__mysqlcf__  = im_path + "mysql"
        self.v__app__squidwp__  = im_path + "squid"
        self.v__app__electro__  = im_path + "electro"
        self.v__app__com_c64__  = im_path + "c64"
        self.v__app__com_set__  = im_path + "settings"
        self.v__app__keybc64__  = im_path + "c64keyboard.png"
        self.v__app__discc64__  = im_path + "disk2.png"
        self.v__app__datmc64__  = im_path + "mc2.png"
        self.v__app__logoc64__  = im_path + "logo2.png"
        
        monitor = get_monitors()[0]
        self.monitor_width  = monitor.width
        self.monitor_height = monitor.height
        self.monitor_scale  = monitor.width_mm / monitor.width
        
        # ------------------------------------------------------------------------
        # dBase parser error code's:
        # ------------------------------------------------------------------------
        self.DBASE_EXPR_SYNTAX_ERROR   = 1000
        self.DBASE_EXPR_KEYWORD_ERROR  = 1001
        self.DBASE_EXPR_IS_EMPTY_ERROR = 1002

        self.default_file_path = os.getcwd() + "/examples/"
        
        self.source_comments  = []
        self.source_tokens    = []
        self.source_errors    = []
        
        self.code_error     = 0
        self.counter_if     = 0
        self.counter_endif  = 0

        self.char_prev = ''
        self.char_curr = '\0'
        self.char_next = ''
        
        self.temp_token = ""
        self.TOKEN_TEMP = 4000
        
        self.c64_parser  = None
        self.c64_parsed  = None
        self.c64_console = None
        
        # Konstante für Sicherheitsberechtigungen
        self.GENERIC_ALL = 0x10000000
        
        self.token_macro = ["define","ifdef","ifndef","else","endif"]
        
        # ------------------------------------------------------------------------
        # source code editors collector ...
        # ------------------------------------------------------------------------
        self.editors_entries = {
            "dbase": [],
            "pascal": [],
            "iosc": [],
            "java": [],
            "javascript": [],
            "python": [],
            "prolog": [],
            "lisp": [],
            "c64": []
        }
        
        # ------------------------------------------------------------------------
        # programming language stuff ...
        # ------------------------------------------------------------------------
        self.SIDE_BUTTON_HELP       =  0
        self.SIDE_BUTTON_DBASE      =  1
        self.SIDE_BUTTON_PASCAL     =  2
        self.SIDE_BUTTON_CPP        =  3
        self.SIDE_BUTTON_JAVA       =  4
        self.SIDE_BUTTON_JAVASCRIPT =  5
        self.SIDE_BUTTON_PYTHON     =  6
        self.SIDE_BUTTON_PROLOG     =  7
        self.SIDE_BUTTON_FORTRAN    =  8
        self.SIDE_BUTTON_LISP       =  9
        self.SIDE_BUTTON_C64        = 10
        
        self.radio_cpp          = None
        self.radio_java         = None
        self.radio_javascript   = None
        self.radio_python       = None
        self.radio_php          = None
        
        self.servers_scroll = None
        self.servers_widget = None
        self.servers_layout = None

        self.splitter = None
        
        self.active_side_button = -1
        
        self.tab_level = [
            0x0100, 0x0200, 0x0300, 0x0400, 0x0500, 0x0600,
            0x0700, 0x0800, 0x0900, 0x1000, 0x1100, 0x1200,
            0x1300, 0x1400, 0x1500, 0x1600, 0x1700, 0x1800,
            0x1900, 0x2000, 0x2100
        ]
        
        # ------------------------------------------------------------------------
        # string conversation ...
        # ------------------------------------------------------------------------
        self.octal_digits      = ['\060','\061','\062','\063','\064','\065','\066','\067','\070','\071']
        self.octal_alpha_upper = ['\101','\102','\103','\104','\105','\106','\107','\110','\111','\112',
                                  '\113','\114','\115','\116','\117','\120','\121','\122','\123','\124',
                                  '\125','\126','\127','\130','\131','\132' ]
        self.octal_alpha_lower = ['\141','\142','\143','\144','\145','\146','\147','\150','\151','\152',
                                  '\153','\154','\155','\156','\157','\160','\161','\162','\163','\164',
                                  '\165','\166','\167','\170','\171','\172' ]
        #
        self.octal_alpha = [ self.octal_alpha_upper, self.octal_alpha_lower ]
        self.ascii_charset = ['a','b','c','d','e','f','g','h','i','j','k','l','m',
                              'n','o','p','q','r','s','t','u','v','w','x','y','z',
                              '0','9','8','7','6','5','4','3','2','1',
                              '-','+','*','/',
                              '(',')',
                              '[',']',
                              '{','}','=' ]
        # ------------------------------------------------------------------------
        # some place holder variables to shorten and categorgraphic the code ...
        # ------------------------------------------------------------------------
        class editor_class:
            def __init__(self):
                self.rightBox = None
                #self.obj_1 = None
                #self.obj_2 = None
                #self.obj_3 = None
                #
                self.hlayout = None
                self.vlayout = None
        #
        self.editor = editor_class()
        self.editor_counter = 0
        
        self.editor_check = None
        self.editor_saveb = None
        
        self.copy_overlay_label_1 = None
        self.copy_overlay_label_2 = None
        
        self.current_focus = None
        
        self.img_doxygen = None
        self.img_hlpndoc = None
        
        # ------------------------------------------------------------------------
        # databse stuff ...
        # ------------------------------------------------------------------------
        self.f_edit = []  # field name
        self.t_edit = []  # field type
        self.l_edit = []  # field length
        self.p_edit = []  # precesion
        self.k_edit = []  # primary key
        #
        self.d_push = []  # delete button

        self.v_layout_f_edit = None
        self.v_layout_t_edit = None
        self.v_layout_l_edit = None
        self.v_layout_p_edit = None
        self.v_layout_k_edit = None
        #
        self.v_layout_d_push = None
        
        # ------------------------------------------------------------------------
        # parser generator state flags ...
        # ------------------------------------------------------------------------
        self.counter_digits = 0
        self.counter_indent = 1
        self.counter_for    = 0
        self.counter_brace  = 0
        
        self.parser_op = ['-','+','*','/']
        self.parser_token = False
        
        self.token_str   = ""
        self.digit_array = [chr(i) for i in range(ord('0'), ord('9') + 1)]
        self.current_token = ""
        
        self.open_pascal_comment_soft = 0
        self.open_pascal_comment_hard = 0
        
        self.actual_parser = 0
        
        self.TOK_INVALID        = 2000
        self.TOK_NUMBER         = 2001
        self.TOK_IDENT          = 2002
        self.TOK_SAY            = 2003
        #
        self.TOK_NEWLINE        = 2004
        self.TOK_WHITE_SPACES   = 2005
        #
        self.TOK_EOF     = 3000
        
        # ------------------------------------------------------------------------
        # dbase reserved keywords ...
        # ------------------------------------------------------------------------
        self.dbase_keywords = [
            'say', 'for', 'do', 'case', 'class', 'of', 'form', 'endclass',
            'set', 'color', 'to',
            'get', 'local', 'parameter', 'if', 'else', 'endif'
        ]

        self.TOKEN_IDENT = 3000
        
        self.text_code  = ""
        self.temp_code  = ""
        self.code_code  = ""
        self.class_code = ""

        self.open_paren  = 0
        self.close_paren = 0
        self.text_paren  = ""
        
        self.last_command = True

        self.ptNoMoreData = 2000

        self.have_errors = False
        self.in_expr = 0
        
        # ------------------------------------------------------------------------
        # console standard vga colors ...
        # ------------------------------------------------------------------------
        self.concolors = [
        'n','b','g','gb','bg','r','rb','br','rg','gr',
        'w','n+','b+','g+','gb+','bg+',
        'r+','rb+','br+','rg+', 'gr+' ,'w+'] 
        #
        self.convalues = [
        '#000000','#00008B','#006400','#8B008B','#8B008B',
        '#8B0000','#FF00FF','#FF00FF','#A52A2A','#A52A2A',
        '#D3D3D3','#A9A9A9','#0000FF','#00FF00','#ADD8E6',
        '#ADD8E6','#FF0000','#00FFFF','#00FFFF','#FFFF00',
        '#FFFF00','#FFFFFF']
        
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
        
        self.scrollview_1  = None
        self.scrollview_2  = None
        self.scrollview_3  = None
        self.scrollview_4  = None
        
        self.scrollview_5  = None; self.scrollview_6  = None; self.scrollview_7  = None
        self.scrollview_8  = None; self.scrollview_9  = None; self.scrollview_10 = None
        self.scrollview_11 = None; self.scrollview_12 = None; self.scrollview_13 = None
        self.scrollview_14 = None; self.scrollview_15 = None; self.scrollview_16 = None
        self.scrollview_17 = None; self.scrollview_18 = None; self.scrollview_19 = None
        self.scrollview_20 = None; self.scrollview_21 = None; self.scrollview_22 = None
        
        self.scrollers = [
            self.scrollview_5 , self.scrollview_6 , self.scrollview_7 , self.scrollview_8,
            self.scrollview_9 , self.scrollview_10, self.scrollview_11, self.scrollview_12,
            self.scrollview_13, self.scrollview_14, self.scrollview_15, self.scrollview_16,
            self.scrollview_17, self.scrollview_18, self.scrollview_19, self.scrollview_20,
            self.scrollview_21, self.scrollview_22
        ]
        
        self.list_widget_1 = None
        self.list_widget_1_elements = [
            "Project", "Mode", "Output", "Diagrams"]
        
        self.list_widget_2 = None
        self.list_widget_2_elements = [                                  \
            "Project", "Build", "Messages", "Input", "Source Browser",   \
            "Index", "HTML", "LaTeX", "RTF", "Man", "XML", "DocBook",    \
            "AutoGen", "SQLite3", "PerlMod", "Preprocessor", "External", \
            "Dot" ]
            
        self.v__app_object        = None
        self.v__app_win           = None
        #
        self.v__app__locales           = ""
        self.v__app__locales_messages  = ""
        self.v__app__locales_help      = ""
        
        self.v__app__img_ext__    = ".png"
        self.v__app__font         = "Arial"
        self.v__app__font_edit    = "Consolas"
        
        self.v__app__framework    = "PyQt5.QtWidgets.QApplication"
        self.v__app__exec_name    = sys.executable
        
        self.v__app__error_level  = "0"
        
        self.v__app__scriptname__ = "./examples/dbase/example1.prg"
        self.v__app__favorites    = self.v__app__internal__ + "/favorites.ini"

        self.saved_style = ""
        self.window_login = None
        self.client = None
        
        self.doxygen_project_file = " "
        self.DoxyGenElementLayoutList = []
        
        # ------------------------------------------------------------------------
        self.v__app__config      = None
        self.v__app__config_help = None
        # ------------------------------------------------------------------------
        self.v__app__devmode  = -1
        
        self.toolbar_css      = "toolbar_css"
        
        self.css__widget_item = "listview_css"
        self.css_model_header = "model_hadr"
        self.css_tabs         = "tabs_css"
        self.css_button_style = "button_style_css"
        
        self.hhc_compiler     = "E:/doxygen/hhc/hhc.exe"    # todo: .ini
        
        self.html_content = "html_content"
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
        
        self.project_not_known = (""
            + "Error: project type not known.\n\n"
            + "would you create a 'doxygen'  project ?\n"
            + "would you create a 'helpndoc' project ?\n\n"
            + "Dont forget to specify the kind of documentation (C, Java, Pascal) !\n\n"
            + "Please choose an option...")
        
        self.error_result = 0
        self.topic_counter = 1
        
        self.line_col = 1
        self.line_row = 1
        
        self.c64_painter = None
        
        self.current_pushedit = None
        
        self.os_name = platform.system().lower()

        self.v__app__config_project_ini = "unknown.pro"
        self.v__app__pro_config    = ""
        #
        self.doc_framework   = -1
        self.doc_template    = -1
        self.doc_lang        = -1
        self.doc_kind        = -1
        self.doc_type        = -1
        self.doc_type_out    = -1
        
        self.doc_srcdir   = ""
        self.doc_dstdir   = ""

        self.doc_logo     = ""
        self.doc_name     = ""
        self.doc_number   = ""
        self.doc_author   = ""

        self.doc_entries     = "0"
        self.doc_optimize    = "0"
        self.doc_cross       = "0"
        
        self.doc_recursiv = ""
        
        self.doc_output_html        = 0
        self.doc_output_plain_html  = 0
        self.doc_output_navi        = 0
        self.doc_output_prepare_chm = 0
        self.doc_output_search_func = 0
        
        self.doc_output_latex       = 0
        self.doc_output_latex_pdf   = 0
        self.doc_output_latex_imm   = 0
        self.doc_output_latex_ps    = 0
        
        self.doc_output_man = 0
        self.doc_output_rtf = 0
        self.doc_output_doc = 0
        self.doc_output_xml = 0
        
        self.doc_dia_not = 0
        self.doc_dia_txt = 0
        self.doc_dia_bin = 0
        self.doc_dia_dot = 0
        
        self.doc_dia_class  = 0
        self.doc_dia_colab  = 0
        self.doc_dia_overh  = 0
        self.doc_dia_inc    = 0
        self.doc_dia_incby  = 0
        self.doc_dia_call   = 0
        self.doc_dia_callby = 0
        
        self.type_label        = 1
        self.type_edit         = 2
        self.type_spin         = 3
        self.type_combo_box    = 4
        self.type_check_box    = 5
        self.type_push_button  = 6
        self.type_radio_button = 7
        self.type_textedit     = 8
        
        self.doc_project_open       = False
        
        self.DOC_LANG_CPP           = 0
        self.DOC_LANG_JAVA          = 1
        self.DOC_LANG_JAVASCRIPT    = 2
        self.DOC_LANG_PYTHON        = 3
        self.DOC_LANG_PHP           = 4
        self.DOC_LANG_FORTRAN       = 5
        
        self.DOC_TEMPLATE_API       = 0
        self.DOC_TEMPLATE_EMPTY     = 1
        self.DOC_TEMPLATE_RECIPE    = 2
        self.DOC_TEMPLATE_SOFTWARE  = 3
        
        self.DOC_DOCUMENT_HTML      = 0
        self.DOC_DOCUMENT_PDF       = 1
        
        self.DOC_FRAMEWORK_DOXYGEN  = 0
        self.DOC_FRAMEWORK_HELPNDOC = 1
        
        self.tr = None
        self.sv_help = None

        self.TARGET_DIRECTORY      = self.v__app__internal__ + "/temp"
        self.PROJECT_NAME          = "A Temporary Project"
        self.PROJECT_SOURCE        = self.v__app__internal__ + "/temp/test.html"
        self.GENERATE_DOC          = 0
        self.ADD_LINKS_TO_INDEX    = 1
        self.PAGE_FORMAT_LANDSCAPE = 0
        self.USE_TOPLEVEL_PROJECT  = 1
        self.DEFAULT_TOPIC         = "test.html"
        self.USE_DOC_TEMPLATE      = "pydocgen.dot"
        self.DOC_PAGE_BREAKS       = 0

        # needed for converting Unicode->Ansi (in local system codepage)
        DecodeUnicodeString = lambda x: codecs.latin_1_encode(x)[0]
        
        self.doxy_env   = "DOXYGEN_PATH"  # doxygen.exe
        self.doxy_hhc   = "DOXYHHC_PATH"  # hhc.exe
        
        self.doxy_path  = self.v__app__internal__
        self.hhc__path  = ""
        
        self.doxyfile   = os.path.join(self.v__app__internal__, "Doxyfile")

        self.error_fail = False
        self.byte_code = None
    
    def save_config_file(self):
        try:
            ## 0xA0100
            content = (""
            + "[common]\n"
            + "language = en_us\n"
            + "framework = "     + str(self.doc_framework)  + "\n"
            + "lang = "          + str(self.doc_lang)       + "\n"
            + "template = "      + str(self.doc_template)   + "\n"
            + "kind = "          + str(self.doc_kind)       + "\n"
            + "\n"
            
            + "[project]\n"
            + "type = "          + str(self.doc_type)       + "\n"
            + "doc_out = "       + str(self.doc_type_out)   + "\n"
            + "logo = "          + self.doc_logo            + "\n"
            + "name = "          + self.doc_name            + "\n"
            + "author = "        + self.doc_author          + "\n"
            + "number = "        + self.doc_number          + "\n"
            + "srcdir = "        + self.doc_srcdir          + "\n"
            + "dstdir = "        + self.doc_dstdir          + "\n"
            + "scan_recursiv = " + str(self.doc_recursiv)   + "\n"
            + "\n"
            
            + "[mode]\n"
            + "optimized = "     + str(self.doc_optimize)   + "\n"
            + "doc_entries = "   + str(self.doc_entries)    + "\n"
            + "cross = "         + str(self.doc_cross)      + "\n"
            + "\n"
            
            + "[output]\n"
            + "doc_html = "        + str(self.doc_output_html)        + "\n"
            + "doc_plain_html  = " + str(self.doc_output_plain_html)  + "\n"
            + "doc_navi = "        + str(self.doc_output_navi)        + "\n"
            + "doc_prepare_chm = " + str(self.doc_output_prepare_chm) + "\n"
            + "doc_search_func = " + str(self.doc_output_search_func) + "\n"
            
            + "doc_latex = "       + str(self.doc_output_latex)     + "\n"
            + "doc_latex_pdf = "   + str(self.doc_output_latex_pdf) + "\n"
            + "doc_latex_imm = "   + str(self.doc_output_latex_imm) + "\n"
            + "doc_latex_ps = "    + str(self.doc_output_latex_ps)  + "\n"
            
            + "doc_man = " + str(self.doc_output_man) + "\n"
            + "doc_rtf = " + str(self.doc_output_rtf) + "\n"
            + "doc_xml = " + str(self.doc_output_xml) + "\n"
            + "doc_doc = " + str(self.doc_output_doc) + "\n"
            + "\n"
            
            + "[diagrams]\n"
            + "dia_not = " + str(self.doc_dia_not) + "\n"
            + "dia_txt = " + str(self.doc_dia_txt) + "\n"
            + "dia_bin = " + str(self.doc_dia_bin) + "\n"
            + "dia_dot = " + str(self.doc_dia_dot) + "\n"
            + "\n"
            
            + "[graph]\n"
            + "class = "  + str(self.doc_dia_class)  + "\n"
            + "colab = "  + str(self.doc_dia_colab)  + "\n"
            + "overh = "  + str(self.doc_dia_overh)  + "\n"
            + "inc = "    + str(self.doc_dia_inc)    + "\n"
            + "incby = "  + str(self.doc_dia_incby)  + "\n"
            + "call = "   + str(self.doc_dia_call)   + "\n"
            + "callby = " + str(self.doc_dia_callby) + "\n"
            + "\n"
            )
            hid = 0
            for idx in range(5, 23):
                content += "\n[expert_"    + str(idx) + "]\n"
                elements = eval(_("label_" + str(idx) + "_elements"))
                
                #for item in elements:
                #    hexer = _(hex(item[0]).upper()[2:]).lower()
                #    typso = getattr(genv, "doc_" + hexer + "_object")
                #    infos = getattr(genv, "doc_" + hexer + "_type")
                #    
                #    if typso == None:
                #        showError(_("Error:\nelement item can not get object type."))
                #        return False
                #        
                #    #if isinstance(typso, QCheckBox):
                #    #    if typso.isChecked():
                #    #        setattr(genv, "doc_" + hexer, 1)
                #    #    else:
                #    #        setattr(genv, "doc_" + hexer, 0)
                #    #    value = getattr(genv, "doc_" + hexer)
                #    #    content += hexer + " = " + str(value) + "\n"
                #    #    continue
                #    #elif isinstance(typso, QRadioButton):
                #    #    if typso.isChecked():
                #    #        setattr(genv, "doc_" + hexer, 1)
                #    #    else:
                #    #        setattr(genv, "doc_" + hexer, 0)
                #    #    value = getattr(genv, "doc_" + hexer)
                #    #    content += hexer + " = " + str(value) + "\n"
                #    #    continue
                #    #else:
                #    #    if int(infos) == genv.type_edit:
                #    #        setattr(genv, "dbc_" + hexer, typso.text())
                #    #    elif int(infos) == genv.type_textedit:
                #    #        setattr(genv, "dbc_" + hexer, typso.toPlainText())
                #    #    value = typso.toPlainText()
                #    #    content += hexer + " = " + str(value) + "\n"
                #    #    continue
            #print("writter")
            with open(self.v__app__config_ini_help, "w") as config_file:
                config_file.write(content)
                config_file.close()
            return True
        except configparser.NoSectionError as e:
            showError(_("Error:\nsomething went wrong during saving settings (section)."))
            return False
            
        except configparser.NoOptionError as e:
            showError(_("Error:\nsomething went wrong during saving settings (option)."))
            return False
            
        except configparser.DuplicateSectionError as e:
            showError(_((""
            + "Error:\nsetting file logic error.\n"
            + "You can try to fix this error by remove all double section's."
            )))
            return False
            
        except configparser.DuplicateOptionError as e:
            showError(_((""
            + "Error:\nsetting file logic error.\n"
            + "You can try to fix this error by remove all double options."
            )))
            return False
            
        except AttributeError as e:
            print(e)
            return False
    
    def unexpectedToken(self, text):
        self.msg = f"unexpected token: '{text}'"
        self.unexpectedError(self.msg)
    
    def unexpectedChar(self, chr):
        self.msg = f"unexpected character: '{chr}'"
        self.unexpectedError(self.msg)
    
    def unexpectedEndOfLine(self):
        self.unexpectedError("unexpected end of line")
    
    def unexpectedEscapeSign(self):
        self.unexpectedError("nunexpected escape sign")
    
    def unexpectedError(self, message):
        try:
            calledFrom = inspect.stack()[1][3]
            genv.message = (""
                + f"{message}\n"
                + f"at line   : {genv.line_row}\n"
                + f"in file   : {self.v__app__scriptname__}.\n")
            showError(genv.message)
            return False
        except unexpectedParserException as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            tb = traceback.extract_tb(exc_traceback)[-1]
            
            padding = 10
            
            txt1 = _("Exception occur at parsing:\n")
            txt2 = _("type"  ).ljust( padding )
            txt3 = _("code"  ).ljust( padding )
            txt4 = _("reason").ljust( padding )
            
            msg  = f"{txt1}"
            msg += f"{txt2}: {exc_type.__name__}\n"
            msg += f"{txt3}: {exc_value}\n"
            msg += f"{txt4}: {e.message}\n"
            msg += ("-" * 40)
            msg += "\n"
            #
            #msg += f"file : {tb.filename}\n"
            #msg += f"line : {tb.lineno}"
            showException(msg)

# ---------------------------------------------------------------------------
global genv
genv = globalEnv()

# ------------------------------------------------------------------------
# resource data like pictures or icons ...
# ------------------------------------------------------------------------
#import resources_rc
def import_resource_module(gzip_path, module_name):
    """Lädt ein kompiliertes .pyc-Modul aus einer gzip-komprimierten Datei im Speicher."""
    with gzip.open(gzip_path, 'rb') as f:
        pyc_data = f.read()

    # Die ersten 16 Bytes (Header) ignorieren (Python 3.7+)
    code_obj = marshal.loads(pyc_data[16:])

    # Neues Modul aus Bytecode erstellen
    module = types.ModuleType(module_name)
    exec(code_obj, module.__dict__)

    # Modul im sys-Modulcache speichern
    sys.modules[module_name] = module
    return module

gmod = import_resource_module(res_file, 'resources_rc')

# ------------------------------------------------------------------------
# read a file into memory ...
# ------------------------------------------------------------------------
def read_gzfile_to_memory(file_path):
    check_file = Path(file_path)
    if not check_file.exists():
        showError(""
        + "Error:\n"
        + "gzfile directory exists, but file could not found.\n"
        + "aborted.")
        sys.exit(1)
    if not check_file.is_file():
        showError(""
        + "Error:\n"
        + "gzfile is not a file.\n"
        + "aborted.")
        sys.exit(1)
    if check_file.is_file():
        with open(check_file, "rb") as file:
            file_header = file.read(3)
            if file_header == b'\x1f\x8b\x08':
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
                file.seek(0)
                file_data = file.read()
                mo_file = io.BytesIO(file_data)
                translations = gettext.GNUTranslations(mo_file)
                translations.install()
                _ = translations.gettext
                return _
            else:
                file.close()
                showError(""
                + "Error:\n"
                + "language mo file could not be load.\n"
                + "aborted.\n\n"
                + "Python-Error: "
                + str(e)
                + "\nDetails:\n"
                + traceback.format_exc())
                sys.exit(1)
    return None

# ------------------------------------------------------------------------
# get the locale, based on the system locale settings ...
# ------------------------------------------------------------------------
def handle_language(lang):
    try:
        # todo: .ini over write
        # os.path.join(genv.v__locale__,genv.v__locale__sys[0])
        #
        #file_path = os.path.join(genv.v__app__locales, genv.v__locale__enu)
        #file_path = os.path.join(file_path, "LC_MESSAGES")
        #file_path = os.path.join(file_path, genv. v__app__name_mo + ".gz")
        #
        _ = read_gzfile_to_memory(genv.v__app__locales_messages)
        return _
    except Exception as e:
        exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
        tb = traceback.extract_tb(e.__traceback__)[-1]
        
        error_str = (""
        + "Exception occur during handle language:\n"
        + "type    : " + exc_type.__name__ + "\n"
        + "value   : " + exc_value         + "\n" + ("-" * 40) + "\n"
        + "file    : " + tb.filename       + "\n"
        + "at line : " + tb.lineno         + "\n")
        
        showError(error_str)
        sys.exit(genv.EXIT_FAILURE)
 
def handle_help(lang):
    try:
        _h = read_gzfile_to_memory(genv.v__app__locales_help)
        return _h
    except Exception as e:
        exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
        tb = traceback.extract_tb(e.__traceback__)[-1]
        
        error_str = (""
        + "Exception occur during handle language:\n"
        + "type    : " + exc_type.__name__ + "\n"
        + "value   : " + str(exc_value)    + "\n" + ("-" * 40) + "\n"
        + "file    : " + tb.filename       + "\n"
        + "at line : " + str(tb.lineno)    + "\n")
        
        showError(error_str)
        sys.exit(genv.EXIT_FAILURE)

# ---------------------------------------------------------------------------
# application imports ...
# ---------------------------------------------------------------------------
try:
    # ------------------------------------------------------------------------
    # Unter Windows können wir versuchen zu prüfen, ob eine GUI-basierte
    # Anwendung läuft,indem wir den Windows-GUI-Thread verwenden.
    # ------------------------------------------------------------------------
    try:
        # Check if sys.stdin is a tty (terminal)
        if sys.stdin.isatty():
            genv.run_in_console = True
        else:
            genv.run_in_console = False
    except AttributeError:
        genv.run_in_console = False
    
    try:
        user32 = ctypes.windll.user32
        if user32.GetForegroundWindow() != 0:
            genv.run_in_gui = True
        else:
            genv.run_in_gui = False
    except Exception:
        genv.run_in_gui = False
    
    if genv.run_in_console:
        DebugPrint("run in terminal")
    if genv.run_in_gui:
        DebugPrint("run in gui")
    
    from pathlib import Path
    
    # ------------------------------------------------------------------------
    # developers modules ...
    # ------------------------------------------------------------------------
    import string, codecs
    
    # ---------------------------------------------------------
    # when config.ini does not exists, then create a small one:
    # ---------------------------------------------------------
    if not os.path.exists(genv.v__app__config_ini):
        with open(genv.v__app__config_ini, "w", encoding="utf-8") as f:
            content = (""
            + "[common]\n"
            + "language = en_us\n"
            + "\n"
            + "[dBaseProject]\n"
            + "Form = "
            + "Report = "
            + "Program = "
            + "Tables = "
            + "Images = "
            + "SQL = "
            + "Other = ")
            f.write(content)
            f.close()
            ini_lang = "en_us" # default is english; en_us
    # ------------------------------------------------------------------------
    # forward initializations ...
    # ------------------------------------------------------------------------
    genv.v__app__config = configparser.ConfigParser()
    genv.v__app__config.read(genv.v__app__config_ini)
    
    try:
        genv.v__app__config.read(genv.v__app__config_ini)
        ini_lang = genv.v__app__config.get("common", "language")
    except:
        ini_lang = "en_us"
        pass
    
    # ------------------------------------------------------------------------
    # global used locales constants ...
    # ------------------------------------------------------------------------
    genv.v__locale__    = os.path.join(genv.v__app__internal__, "locales")
    genv.v__locale__enu = "en_us"            # enu
    genv.v__locale__deu = "de_de"            # deu
    genv.v__locale__sys = locale.getlocale() # system locale
    
    check_path = Path(genv.v__locale__)
    if not check_path.is_dir():
        DebugPrint("Error: loacles directory not found.")
        DebugPrint("abort.")
        sys.exit(1)

    DebugPrint(genv.v__app__config["common"]["language"])
    genv.v__app__locales = os.path.join(genv.v__app__internal__, "locales")
    genv.v__app__locales = os.path.join(genv.v__app__locales, genv.v__app__config["common"]["language"])
    
    genv.v__app__locales_messages = os.path.join(genv.v__app__locales, "LC_MESSAGES")
    genv.v__app__locales_help     = os.path.join(genv.v__app__locales, "LC_HELP")
    
    genv.v__app__locales_messages = os.path.join(genv.v__app__locales_messages, genv.v__app__name_mo + ".gz")
    genv.v__app__locales_help     = os.path.join(genv.v__app__locales_help    , genv.v__app__help_mo + ".gz")
    #
    if len(genv.v__app__locales) < 5:
        DebugPrint("Error: locale out of seed.")
        DebugPrint("abort.")
        sys.exit(1)
        
    _  = handle_language(ini_lang)
    _h = handle_help    (ini_lang)
    
    # ------------------------------------------------------------------------
    # determine on which operating the application script runs ...
    # ------------------------------------------------------------------------
    genv.os_name = platform.system().lower()
    DebugPrint("OS: " + genv.os_name)
    if genv.os_name == 'windows':
        DebugPrint("The Application runs under Windows.")
    elif genv.os_name == 'linux':
        DebugPrint("The Application runs under Linux.")
    elif genv.os_name == 'darwin':
        DebugPrint("The Application runs under macOS.")
    else:
        DebugPrint(f"Unknown Operating System: {genv.os_name}")
        sys.exit(1)
    
    # -------------------------------------------------------------------
    # for debuging, we use python logging library ...
    # -------------------------------------------------------------------
    genv.v__app__logfile = genv.v__app__logfile.replace("\\", "/")
    if not os.path.exists(genv.v__app__logfile):
        Path(genv.v__app__logfile).touch()
    genv.v__app__logging = logging.getLogger(genv.v__app__logfile)
    
    logging.basicConfig(
        format="%(asctime)s: %(levelname)s: %(message)s",
        filename=genv.v__app__logfile,
        encoding="utf-8",
        filemode="w",
        level=logging.DEBUG)
    genv.v__app__logging.info("init ok: session start...")
    
    # ------------------------------------------------------------------------
    # when the user start the application script under Windows 7 and higher:
    # ------------------------------------------------------------------------
    try:
        from ctypes import windll  # Only exists on Windows.
        myappid = 'kallup-nonprofit.helpndoc.observer.1'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        DebugPrint(_("windll error"))
    except Exception:
        DebugPrint(_("common exception occur"))

except IgnoreOuterException:
    DebugPrint(genv.v__app__locales)
    pass
except configparser.NoOptionError as e:
    DebugPrint("Exception: option 'language' not found.")
    DebugPrint("abort.")
    sys.exit(1)
except configparser.NoSectionError as e:
    DebugPrint("Exception: section not found.\n")
    DebugPrint(e)
    DebugPrint("abort.")
    sys.exit(1)
except configparser.Error as e:
    DebugPrint("Exception: config error occur.")
    DebugPrint("abort.")
    sys.exit(1)
except SyntaxError as e:
    exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
    tb = traceback.extract_tb(e.__traceback__)[-1]
    
    DebugPrint(f"Exception occur at module import:")
    DebugPrint(f"type : {exc_type.__name__}")
    DebugPrint(f"value: {exc_value}")
    DebugPrint(("-" * 40))
    #
    DebugPrint(f"file : {tb.filename}")
    DebugPrint(f"line : {tb.lineno}")
    sys.exit(1)
except Exception as e:
    exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
    tb = traceback.extract_tb(e.__traceback__)[-1]
    #
    if exc_type.__name__ == "NoOptionError":
        #genv.v__app__locales = os.path.join(genv.v__app__locales, genv.v__locale__sys[0])
        #genv.v__app__locales = os.path.join(genv.v__app__locales, "LC_MESSAGES")
        #genv.v__app__locales = os.path.join(genv.v__app__locales, genv.v__app__name_mo)
        pass
    else:
        DebugPrint(f"Exception occur at module import:")
        DebugPrint(f"type : {exc_type.__name__}")
        DebugPrint(f"value: {exc_value}")
        DebugPrint(("-"*40))
        #
        DebugPrint(f"file : {tb.filename}")
        DebugPrint(f"line : {tb.lineno}")
        sys.exit(1)

# ---------------------------------------------------------------------------
# \brief ClassObjects holds the TObject classes. TObject is the base of all
#        classes that used this framework. The array will be delete its
#        objects with the destructor definition __del__.
#
# \note  do not use this varuable directly - it is used for internal things.
# \since version 0.0.1
# ---------------------------------------------------------------------------
global ClassObjects
ClassObjects = []

# ---------------------------------------------------------------------------
# \brief TObject is the base class of all classes that used this framework.
#        You can use "Create" for __init__ and "Destroy" for __del__.
#        For each TObject, we use/save a hash string to unufy the object.
#        This makes it possible to search for objects.
#
# \since version 0.0.1
# ---------------------------------------------------------------------------
class TObject:
    # --------------------------------------------------------------------
    # constructor of class TObject
    # --------------------------------------------------------------------
    def Create(self, parent=None):
        # ----------------------------------------------------------------
        # ClassName returns the class name for the current class.
        # ----------------------------------------------------------------
        self.ClassName = str(__class__.__name__)
        
        # ----------------------------------------------------------------
        # to get the hash, we get the class name and the current date and
        # time will be add at end of string. But this is not enough so we
        # add a reference counter at finally string end.
        # the counter is simple the length of the ClassObjects container.
        # ----------------------------------------------------------------
        self.hashstring  = self.__class__.__name__
        self.hashstring += datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.hashstring += str(len(ClassObjects) + 1)
        
        self.hashString  = hashlib        \
        .sha256(self.hashstring.encode()) \
        .hexdigest()
        
        self.parentNode = {
            "class": {
                "parent": None,
                "name": self.__class__.__name__,
                "addr": self,
                "hash": self.hashString,
                "date": datetime.now()
            }
        }
        self.Add()
    
    # --------------------------------------------------------------------
    # dtor of class TObject
    # --------------------------------------------------------------------
    def Destroy(self):
        pass
    
    # --------------------------------------------------------------------
    # internal function: for add object informations to ClassObjects.
    # --------------------------------------------------------------------
    def Add(self):
        # ----------------------------------------------------------------
        # create a new child
        # ----------------------------------------------------------------
        child_node = {
            "class": {
                "parent": self.parentNode,
                "name": self.__class__.__name__,
                "addr": self,
                "obj_name": type(self).__name__,
                "hash": self.hashString,
                "date": datetime.now()
            }
        }
        # ----------------------------------------------------------------
        # append object informations ...
        # ----------------------------------------------------------------
        self.parentNode = child_node
        ClassObjects.append(child_node)
    
    def test(self):
        DebugPrint(ClassObjects[0]["class"]["hash"])
        DebugPrint(ClassObjects[1]["class"]["hash"])
    
    # --------------------------------------------------------------------
    # check for None and call destructor
    # --------------------------------------------------------------------
    def Free(self):
        current_node = ClassObjects[-1]
        while current_node is not None:
            try:
                addr = current_node["class"]["addr"]
                if addr is not None:
                    del addr
                
                current_node["class"]["addr"] = None
                parent_node = current_node["class"]["parent"]
                
                del current_node
                current_node = parent_node
                
                if current_node is None:
                    break
                
            except Exception as err:
                DebugPrint("error during element del.")
        
        # force garbage collector to remove allocated memory space
        gc.collect()
        self.Destroy()
    
    # --------------------------------------------------------------------
    # return a hash code for the object
    # --------------------------------------------------------------------
    def GetHashCode(self):
        return self.hashstring
    
    # --------------------------------------------------------------------
    # Equals returns True if the object instance pointer (Self) equals
    # the instance pointer Obj.
    # --------------------------------------------------------------------
    def Equals(self, AObject):
        if AObject == self:
            return True
        else:
            return False
    
    # --------------------------------------------------------------------
    # ClassNameIs checks whether Name equals the class name. It takes of
    # case sensitivity.
    # --------------------------------------------------------------------
    def ClassNameIs(self, name):
        if self.ClassName == name:
            return True
        else:
            return False
    
    def ToString(self):
        return str(self.ClassName)
    
    # --------------------------------------------------------------------
    # we re-assign the constructor and destructor for Turbo-Pascal feeling
    # --------------------------------------------------------------------
    __init__ = Create       # constructor - ctor
    __del__  = Destroy      # destructor  - dtor

# ---------------------------------------------------------------------------
# \brief A wrapper class to TObject.
# ---------------------------------------------------------------------------
class TClass(TObject):
    def Create(self, parent=None):
        super().Create(parent)
    
    def Destroy(self):
        if hasattr(super(), 'Destroy'):
            super().Destroy()
    
    # --------------------------------------------------------------------
    # we re-assign the constructor and destructor for Turbo-Pascal feeling
    # --------------------------------------------------------------------
    __init__ = Create       # constructor - ctor
    __del__  = Destroy      # destructor  - dtor

class TStream(TObject):
    # --------------------------------------------------------------------
    # ctor for the class TStream
    # --------------------------------------------------------------------
    def __init__(self):
        self.Position = 0       # the current position in the stream
        self.Size     = 0       # the current size of the stream
    
    # --------------------------------------------------------------------
    # reads data from the stream and returns the number of bytes written
    # --------------------------------------------------------------------
    def Read(self):
        pass
    def Seek(self):             # 
        pass
    
    # --------------------------------------------------------------------
    # writes data from a buffer to the stream
    # --------------------------------------------------------------------
    def Write(self):
        pass
    
    # --------------------------------------------------------------------
    # read a byte from the stream and retzrn its value
    # --------------------------------------------------------------------
    def ReadByte(self):
        pass
    
    # --------------------------------------------------------------------
    # read a word from the stream and return its value
    # --------------------------------------------------------------------
    def ReadWord(self):
        pass
    
    # --------------------------------------------------------------------
    # read a double word from the stream and return its value
    # --------------------------------------------------------------------
    def ReadDWord(self):
        pass
    
    # --------------------------------------------------------------------
    # read a quad word from the stream and return its value
    # --------------------------------------------------------------------
    def ReadQWord(self):
        pass
    
    # --------------------------------------------------------------------
    # write a byte to the stream
    # --------------------------------------------------------------------
    def WriteByte(self):
        pass
    
    # --------------------------------------------------------------------
    # write a word to the stream
    # --------------------------------------------------------------------
    def WriteWord(self):
        pass
    
    # --------------------------------------------------------------------
    # write a double word to the stream
    # --------------------------------------------------------------------
    def WriteDWord(self):
        pass
    
    # --------------------------------------------------------------------
    # write a quad word to the stream
    # --------------------------------------------------------------------
    def WriteQWord(self):
        pass

# ------------------------------------------------------------------------
# read a file into memory ...
# ------------------------------------------------------------------------
class TCustomMemoryStream(TStream):
    # --------------------------------------------------------------------
    # ctor for the class TCustomMemoryStream
    # --------------------------------------------------------------------
    def __init__(self):
        self.Memory = None
    
    # --------------------------------------------------------------------
    # read count byres from the stream into buffer
    # --------------------------------------------------------------------
    def Read(self):
        pass
    
    # --------------------------------------------------------------------
    # sets a new position in the stream
    # --------------------------------------------------------------------
    def Seek(self):
        pass
    
    # --------------------------------------------------------------------
    # writes contents of the memory stream to another stream
    # --------------------------------------------------------------------
    def SaveToStream(self, Stream=None):
        if Stream == None:
            showError(_("stream could not save."))
    
    # --------------------------------------------------------------------
    # writes contents of the stream to a file.
    # --------------------------------------------------------------------
    def SaveToFile(self, FileNamee="temp.tmp"):
        pass

class TList(TObject):
    # --------------------------------------------------------------------
    # ctor for class TList
    # --------------------------------------------------------------------
    def __init__(self):
        super(TList, self).__init__()
        self.Count = 0
        self.Items = []
        self.List  = 0
    
    # --------------------------------------------------------------------
    # dtor for class TList
    # --------------------------------------------------------------------
    def __del__(self):
        super(TList, self).__del__()
    
    # --------------------------------------------------------------------
    # Adds a new pointer to the list.
    # --------------------------------------------------------------------
    def Add(self, AItem):
        try:
            if isinstance(AItem, str):
                DebugPrint("item is string")
                return True
            elif isinstance(AItem, int):
                DebugPrint("item is integer")
                return True
            elif isinstance(AItem, float):
                DebugPrint("item is float")
                return True
            elif isinstance(AItme, None):
                raise TypeError("None is not allowed there.")
                return False
            else:
                raise TypeError("item kind unknown")
                return False
        except TypeError as err:
            raise TypeError(err)
    
    # --------------------------------------------------------------------
    # --------------------------------------------------------------------
    def Clear(self):
        pass
    # --------------------------------------------------------------------
    # --------------------------------------------------------------------
    def Delete(self):
        pass
    # --------------------------------------------------------------------
    # --------------------------------------------------------------------
    def Remove(self):
        pass
    
    # --------------------------------------------------------------------
    # --------------------------------------------------------------------
    def Pack(self):
        pass
    
    # --------------------------------------------------------------------
    # --------------------------------------------------------------------
    def First(self):
        pass
    
    # --------------------------------------------------------------------
    # --------------------------------------------------------------------
    def Last(self):
        pass

class TMenuBar(TObject):
    def Create(self, parent=None):
        super(TMenuBar, self).Create(parent)
        
        if not parent == None:
            if not isinstance(parent, TApplication.TApplication):
                QMessageBox.information(self,
                "Information",
                "parent must be TApplication")
                return
        else:
            QMessageBox.information(self,
            "Information",
            "parent must be given")
            return
        
        self.parent      = parent
        self.menu_bar    = parent.dialog.mainwindow.menuBar()
        
        self.file_menu   = self.menu_bar.addMenu("File")
        self.exit_action = QAction("Exit", parent.dialog.mainwindow)
        self.file_menu.addAction(self.exit_action)
    
    def show(self):
        self.menu_bar.show()
    
    def hide(self):
        self.menu_bar.hide()
    
    def Destroy(self):
        super().Destroy()
    
    # --------------------------------------------------------------------
    # we re-assign the constructor and destructor for Turbo-Pascal feeling
    # --------------------------------------------------------------------
    __init__ = Create       # constructor - ctor
    __del__  = Destroy      # destructor  - dtor

class TApplication(TObject):
    # --------------------------------------------------------------------
    # ctor for class TApplication
    # --------------------------------------------------------------------
    def Create(self, parent=None):
        super(TApplication, self).__init__(parent)
        #
        self.ParamCount = len(sys.argv)
        self.Params     = sys.argv
        self.app        = QApplication(sys.argv)
        self.dialog     = TMainWindow()
        #
        self.ExeName         = self.ParamStr(0)
        self.ApplicationName = "Python Application"
        #
        self.bar_menu   = TMenuBar.TMenuBar(self)
        self.bar_status = TStatusBar.TStatusBar(self)
        
    # --------------------------------------------------------------------
    # this definition member returns the n'th program argument parameter
    # --------------------------------------------------------------------
    def ParamStr(self, index):
        if index < len(self.Params):
            return self.Params[index]
        else:
            return ""
    
    # --------------------------------------------------------------------
    # dtor for class TApplication
    # --------------------------------------------------------------------
    def Destroy(self):
        if hasattr(super(), 'Destroy'):
            super().Destroy()
        pass
    
    # --------------------------------------------------------------------
    # runner def inition entry point.
    # --------------------------------------------------------------------
    def run(self):
        try:
            self.dialog.show()
            self.app.exec_()
        finally:
            self.bar_menu  .Free()
            self.bar_status.Free()
            #
            sys.exit(0)
    
    # --------------------------------------------------------------------
    # we re-assign the constructor and destructor for Turbo-Pascal feeling
    # --------------------------------------------------------------------
    __init__ = Create       # constructor - ctor
    __del__  = Destroy      # destructor  - dtor

class TStatusBar(TObject):
    def Create(self, parent=None):
        super(TStatusBar, self).Create(parent)
        
        if not parent == None:
            if not isinstance(parent, TApplication.TApplication):
                QMessageBox.information(self,
                "Information",
                "parent must be TApplication")
        else:
            QMessageBox.information(self,
            "Information",
            "parent must be given")
            return
        
        self.status_bar = parent.dialog.mainwindow.statusBar()
        self.status_bar.showMessage("Ready.")
        self.status_bar.setStyleSheet("background-color:lightgray;")
    
    def show(self):
        self.status_bar.show()
    
    def hide(self):
        self.status_bar.hide()
    
    def Destroy(self):
        super().Destroy()
    
    # --------------------------------------------------------------------
    # we re-assign the constructor and destructor for Turbo-Pascal feeling
    # --------------------------------------------------------------------
    __init__ = Create       # constructor - ctor
    __del__  = Destroy      # destructor  - dtor

# ------------------------------------------------------------------------
# style sheet definition's:
# ------------------------------------------------------------------------
css_combobox_style = "combo_actn"

# ------------------------------------------------------------------------
# our client login, and write/read class ...
# ------------------------------------------------------------------------
class ClientHandlerThread(QThread):
    new_data = pyqtSignal(QSslSocket, str)
    client_disconnected = pyqtSignal(QSslSocket)

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.client_socket.readyRead.connect(self.read_data)
        self.client_socket.disconnected.connect(lambda: self.handle_disconnection(self.client_socket))

    def read_data(self):
        try:
            if self.client_socket.state() == QSslSocket.ConnectedState:
                if self.client_socket.bytesAvailable() > 0:
                    data = self.client_socket.readAll().data().decode()
                    self.new_data.emit(self.client_socket, data)
                else:
                    showInfo(_("no data, close connection."))
                    self.client_socket.disconnectFromHost()
                    return True
        except Exception as e:
            showInfo(_("Error:\n file not found.\n") + e)
            return False
    
    def handle_disconnection(self):
        self.client_disconnected.emit(self.client_socket)

class SSLClient(QObject):
    # Eigene Signale (nur falls du sie brauchst, zur Weiterverarbeitung)
    connected        = pyqtSignal()
    disconnected     = pyqtSignal()
    newData          = pyqtSignal(str)
    sslErrorOccurred = pyqtSignal(str)

    def __init__(
        self,
        host     = 'localhost',
        port     = 1234
        #crt_file = os.getcwd() + '/_internal/ssl/client.crt',
        #key_file = os.getcwd() + '/_internal/ssl/client.key'
    ):
        super(SSLClient, self).__init__()
        
        self.host = host
        self.port = port
       
        #self.crt_file = crt_file
        #self.key_file = key_file
        
        self.socket = QTcpSocket()
        
        # Signale verbinden
        self.socket.connected.connect(self.on_connected)
        self.socket.readyRead.connect(self.on_ready_read)
        self.socket.disconnected.connect(self.on_disconnected)
        self.socket.errorOccurred.connect(self.on_error_occurred)

    def connect_to_server(self):
        """Stellt eine Verbindung zum Server her (non-blocking)."""
        print(f"Verbinde zu {self.host}:{self.port}...")
        self.socket.connectToHost(self.host, self.port)
        # Ab hier wird asynchron verbunden.
        # Wenn die Verbindung steht, wird 'on_connected' ausgelöst.

    def on_connected(self):
        print("Client: Verbindung hergestellt.")

        # Sobald wir verbunden sind, können wir Daten senden.
        test_message = "Hallo vom Client!"
        self.send_data(test_message)

    def send_data(self, message):
        """Daten an den Server senden (non-blocking)."""
        if self.socket.state() == QTcpSocket.ConnectedState:
            print(f"Client sendet: {message}")
            self.socket.write(message.encode())
            self.socket.flush()
        else:
            print("Client: Keine aktive Verbindung zum Server.")

    def on_ready_read(self):
        """Wird aufgerufen, sobald Daten vom Server angekommen sind."""
        data = self.socket.readAll().data().decode()
        print(f"Client hat empfangen: {data}")

    def on_disconnected(self):
        print("Client: Verbindung wurde getrennt.")

    def on_error_occurred(self, error):
        if error != QAbstractSocket.RemoteHostClosedError:
            print(f"Client-Socket-Fehler: {self.socket.errorString()}")

# ---------------------------------------------------------------------------
# \brief Überschreibe die Datenmethode, um den Dateityp anzupassen.
# ---------------------------------------------------------------------------
class CustomFileSystemModel(QFileSystemModel):
    def data(self, index, role):
        if role == Qt.DisplayRole and index.column() == 2:  # Spalte 2 ist "Type"
            file_info = self.fileInfo(index)
            if file_info.isDir():
                return _("Directory")
            elif file_info.isFile():
                # Benutzerdefinierte Dateityp-Anzeige
                file_str = _("File")
                return f"{file_info.suffix().upper()}-{file_str}"
            else:
                return _("Unknown")
        return super().data(index, role)

class FileExplorer(QWidget):
    def __init__(self, parent=None):
        super(FileExplorer, self).__init__(parent)
        
        self.setWindowTitle("Dateien und Laufwerke Explorer mit Dateigröße")
        self.resize(400, 600)
        
        # Layout erstellen
        layout = QVBoxLayout(self)
        
        # QTreeView erstellen
        self.tree_view = QTreeView(self)
        layout.addWidget(self.tree_view)
        
        # QFileSystemModel erstellen
        self.file_system_model = CustomFileSystemModel()
        self.file_system_model.setRootPath("")  # RootPath auf das Dateisystem setzen
        
        # Nur .exe und .dll Dateien anzeigen
        self.file_system_model.setNameFilters(["*.exe", "*.dll"])
        self.file_system_model.setNameFilterDisables(False)  # Nur gefilterte Dateien anzeigen
        
        # Model an die QTreeView binden
        self.tree_view.setModel(self.file_system_model)
        
        # Root-Index auf das Hauptlaufwerk setzen
        self.tree_view.setRootIndex(self.file_system_model.index(self.file_system_model.rootPath()))
        
        # Spalten anpassen
        self.tree_view.setColumnWidth(0, 200)  # Spaltenbreite für den Dateinamen
        self.tree_view.setColumnWidth(1, 100)  # Spaltenbreite für Dateigröße
        self.tree_view.setColumnWidth(2, 150)  # Spaltenbreite für den Typ
        self.tree_view.setColumnWidth(3, 150)  # Spaltenbreite für das Änderungsdatum
        
        # Optional: Header anpassen (z. B. Schriftart oder Stil)
        header = self.tree_view.header()
        header.setDefaultSectionSize(150)  # Standard-Spaltenbreite setzen
        
        # Signal für Doppelklick verbinden
        self.tree_view.doubleClicked.connect(self.on_double_click)
    
    def on_double_click(self, index):
        if index.isValid():
            # ----------------------------------
            # Dateipfad aus dem Model ermitteln
            # ----------------------------------
            file_path = self.file_system_model.filePath(index)
            
            # ----------------------------------
            # Datei- oder Ordnername
            # ----------------------------------
            file_name = self.file_system_model.filePath(
                index.sibling(
                index.row(),
                0))
            
            # ----------------------------------
            # Nachricht anzeigen
            # ----------------------------------
            if file_name.lower().endswith(".exe") \
            or file_name.lower().endswith(".dll"):
                QMessageBox.information(
                    self,
                    "Datei Doppelklick",
                    f"Dateiname: {file_name}\nPfad: {file_path}")

class CPUWorker(QThread):
    update_signal = pyqtSignal(dict, dict)  # Signal: Updated Registers and Flags
    
    def __init__(self, parent=None):
        super(CPUWorker, self).__init__(parent)
        self.running = True  # Control flag
    
    def run(self):
        while self.running:
            # Simuliere CPU-Register und Flags (hier zufällige Werte)
            registers = {
                "AX": 0x1234,
                "BX": 0x5678,
                "CX": 0x9ABC,
                "DX": 0xDEF0,
                "SP": 0xFFFE,
                "BP": 0x8000,
                "SI": 0x4000,
                "DI": 0x2000,
            }
            flags = {
                "Carry (CF)": 0,
                "Zero (ZF)": 1,
                "Sign (SF)": 0,
                "Overflow (OF)": 1,
                "Parity (PF)": 1,
                "Aux Carry (AF)": 0,
            }
            
            # Sende die aktualisierten Werte an die GUI
            self.update_signal.emit(registers, flags)
            time.sleep(1)  # 1 Sekunde warten (anpassbar)
    
    def stop(self):
        self.running = False

class CPUView(QWidget):
    def __init__(self, parent=None):
        super(CPUView, self).__init__(parent)
        
        self.registers = {
            "EAX": 0x1000,
            "EBX": 0x1000,
            "ECX": 0x1000,
            "EDX": 0x1000,
            "ESP": 0x1000,
            "EBP": 0x1000,
            "ESI": 0x1000,
            "EDI": 0x1000,
            "AX" : 0x1234,
            "BX" : 0x5678,
            "CX" : 0x9ABC,
            "DX" : 0xDEF0,
            "SP" : 0xFFFE,
            "BP" : 0x8000,
            "SI" : 0x4000,
            "DI" : 0x2000,
        }
        
        self.flags = {
            "Carry (CF)": 0,
            "Zero (ZF)": 1,
            "Sign (SF)": 0,
            "Overflow (OF)": 1,
            "Parity (PF)": 1,
            "Aux Carry (AF)": 0,
        }
        
        # Setup UI
        self.layout = QVBoxLayout(self)
        self.register_table = QTableWidget(self)
        self.flags_table = QTableWidget(self)
        
        # Configure tables
        self.setup_table(self.register_table, "Register", "Value", len(self.registers))
        self.setup_table(self.flags_table, "Flag", "State", len(self.flags))
        
        self.layout.addWidget(QLabel("Registers", self))
        self.layout.addWidget(self.register_table)
        self.layout.addWidget(QLabel("Flags", self))
        self.layout.addWidget(self.flags_table)
        
        # Timer for dynamic updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_view)
        self.timer.start(1000)  # Update every second
        
        self.update_view()  # Initialize view with current values
    
    def setup_table(self, table, column1, column2, row_count):
        table.setColumnCount(2)
        table.setRowCount(row_count)
        table.setHorizontalHeaderLabels([column1, column2])
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
    
    def update_view(self):
        try:
            self.register_table.setRowCount(len(self.registers))
            for i, (reg, value) in enumerate(self.registers.items()):
                #print(f"Setting register {reg} to {value}")
                self.register_table.setItem(i, 0, QTableWidgetItem(reg))
                self.register_table.setItem(i, 1, QTableWidgetItem(f"0x{value:04X}"))
            self.flags_table.setRowCount(len(self.flags))
            for i, (flag, state) in enumerate(self.flags.items()):
                #print(f"Setting flag {flag} to {state}")
                self.flags_table.setItem(i, 0, QTableWidgetItem(flag))
                self.flags_table.setItem(i, 1, QTableWidgetItem("1" if state else "0"))
                
        except Exception as e:
            print(f"Error in update_view: {e}")

class AssemblerLineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.marked_lines = set()
    
    def sizeHint(self):
        return self.editor.sizeHint()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.lightGray)
        
        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
        bottom = top + int(self.editor.blockBoundingRect(block).height())
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.width(), self.editor.fontMetrics().height(), Qt.AlignRight, number)
                
                # Markierung prüfen
                if block_number in self.marked_lines:
                    radius = 5
                    circle_x = self.width() - 15
                    circle_y = top + self.editor.fontMetrics().height() // 2
                    painter.setBrush(QColor("red"))
                    painter.drawEllipse(QPoint(circle_x, circle_y), radius, radius)
            
            block = block.next()
            top = bottom
            bottom = top + int(self.editor.blockBoundingRect(block).height())
            block_number += 1
    
    def mouseDoubleClickEvent(self, event):
        if event.x() > self.width() - 20:  # Bereich der Kreise
            y = event.y()
            block = self.editor.firstVisibleBlock()
            block_number = block.blockNumber()
            top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
            
            while block.isValid():
                if block.isVisible():
                    bottom = top + int(self.editor.blockBoundingRect(block).height())
                    if top <= y <= bottom:
                        if block_number in self.marked_lines:
                            self.marked_lines.remove(block_number)
                        else:
                            self.marked_lines.add(block_number)
                        self.update()
                        self.editor.viewport().update()
                        break
                block = block.next()
                top = bottom
                block_number += 1

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.line_number_area = AssemblerLineNumberArea(self)
        
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.highlight_current_line()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
    
    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        space = self.fontMetrics().horizontalAdvance('9') * digits + 20
        return space
    
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
    
    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
    
    def highlight_current_line(self):
        extra_selections = []
        
        # Konfiguration der Zeilenhervorhebung
        selection = QTextEdit.ExtraSelection()
        line_color = QColor(Qt.yellow).lighter(160)  # Gelbliche Farbe für die Zeile
        selection.format.setBackground(line_color)
        
        # Cursor auf die aktuelle Zeile setzen
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()  # Nur die Zeile hervorheben, ohne Text auszuwählen
        extra_selections.append(selection)
        
        # Anwenden der Hervorhebung
        self.setExtraSelections(extra_selections)

class DebugControls(QWidget):
    def __init__(self, parent=None):
        super(DebugControls, self).__init__(parent)
        
        font = QFont("Arial", 10)
        font.setBold(True)
        
        self.btn_set_brk   = QPushButton(_("Set break point"))
        self.btn_del_brk   = QPushButton(_("Del break point"))
        #
        self.btn_start     = QPushButton(_("Start"))
        self.btn_step_into = QPushButton(_("Step Into"))
        self.btn_step_next = QPushButton(_("Next"))
        self.btn_step_prev = QPushButton(_("Prev"))
        self.btn_stop      = QPushButton(_("Stop"))
        
        self.btn_set_brk  .setFont(font)
        self.btn_del_brk  .setFont(font)
        #
        self.btn_start    .setFont(font)
        self.btn_step_into.setFont(font)
        self.btn_step_next.setFont(font)
        self.btn_step_prev.setFont(font)
        self.btn_stop     .setFont(font)
        
        self.btn_set_brk  .clicked.connect(self.btn_set_brk_onclick)
        self.btn_del_brk  .clicked.connect(self.btn_del_brk_onclick)
        #
        self.btn_start    .clicked.connect(self.btn_start_onclick)
        self.btn_step_into.clicked.connect(self.btn_step_into_onclick)
        self.btn_step_next.clicked.connect(self.btn_step_next_onclick)
        self.btn_step_prev.clicked.connect(self.btn_step_prev_onclick)
        self.btn_stop     .clicked.connect(self.btn_stop_onclick)
        
        layout = QVBoxLayout()
        #
        layout.addWidget(self.btn_set_brk)
        layout.addWidget(self.btn_del_brk)
        #
        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_step_into)
        layout.addWidget(self.btn_step_next)
        layout.addWidget(self.btn_step_prev)
        layout.addWidget(self.btn_stop)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def btn_set_brk_onclick(self):
        print("set break")
    
    def btn_del_brk_onclick(self):
        print("sel break")
    
    def btn_start_onclick(self):
        print("start")
        
    def btn_step_into_onclick(self):
        print("step into")
        
    def btn_step_next_onclick(self):
        print("next")
        
    def btn_step_prev_onclick(self):
        print("prev")
        
    def btn_stop_onclick(self):
        print("stop")
        
class AssemblerViewer(CodeEditor):
    def __init__(self, parent=None):
        super().__init__()
        
        self.setReadOnly(False)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        
        self.setFont(QFont("Consolas", 10))  # Monospace-Schriftart
        
        # Beispiel: Bytes analysieren und anzeigen
        #byte_sequence = b"\x55\x48\x89\xe5\xb8\x04\x00\x00\x00\x5d\xc3"
        #asm_code = self.generate_assembler(byte_sequence)
        #self.setPlainText(asm_code)
    
    def generate_assembler(self, byte_sequence):
        pass
        #md = Cs(CS_ARCH_X86, CS_MODE_64)
        #asm_lines = []
        #for instr in md.disasm(byte_sequence, 0x1000):
        #    asm_lines.append(f"0x{instr.address:08x}:\t{instr.mnemonic}\t{instr.op_str}")
        #return "\n".join(asm_lines)

class HexEditComponent(QPlainTextEdit):
    def __init__(self, parent=None):
        super(HexEditComponent, self).__init__(parent)
        
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        self.setStyleSheet("QPlainTextEdit{padding:0px;}")
        
        self.hex_data = ""
        self.selected_index = -1  # Index des aktuell markierten Bytes
    
    def set_hex_data(self, data):
        self.hex_data = data.hex()
        formatted_lines = []
        
        # 8 Spalten zu je 2 Zeichen mit Trennzeichen nach Spalte 4
        for i in range(0, len(self.hex_data), 16):  # 8 Spalten * 2 Zeichen = 16
            line = " ".join(self.hex_data[j:j+2] for j in range(i, i+16, 2))
            # Füge Trennzeichen nach Spalte 4 ein
            split_line = line.split(" ")
            formatted_line = " ".join(split_line[:4]) + " | " + " ".join(split_line[4:])
            formatted_lines.append(formatted_line)
        
        self.setPlainText("\n".join(formatted_lines))
    
    def mousePressEvent(self, event):
        cursor = self.cursorForPosition(event.pos())
        cursor.select(QTextCursor.WordUnderCursor)
        selected_text = cursor.selectedText()
        
        # Finde den Index des angeklickten Bytes
        if len(selected_text) == 2 and all(c in "0123456789ABCDEFabcdef" for c in selected_text):
            # Konvertiere Zeilen und Spalten in einen linearen Index
            block_number  = cursor.blockNumber()
            column_number = cursor.columnNumber()

            # Berücksichtige die Trennung nach Spalte 4
            if column_number > 14:  # Spalten 5, 6, 7, 8
                adjusted_column = column_number - 3  # Verschiebung um die Länge von " | "
            else:
                adjusted_column = column_number

            byte_index = block_number * 8 + (adjusted_column // 3)

            if 0 <= byte_index < len(self.hex_data) // 2:
                self.selected_index = byte_index
                self.highlight_selection()
        else:
            super().mousePressEvent(event)
    
    def highlight_selection(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Start)
        
        # Entferne alte Markierungen
        fmt_clear = QTextCharFormat()
        
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(fmt_clear)
        
        if self.selected_index >= 0:
            cursor.movePosition(QTextCursor.Start)
            cursor.movePosition(QTextCursor.NextBlock    , QTextCursor.MoveAnchor,  self.selected_index // 8)
            cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.MoveAnchor, (self.selected_index %  8) * 3)
            cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, 2)
            
            if 0 <= self.selected_index % 8 <= 3:  # Spalten 1, 2, 3, 4
                # Kürze Markierung um 2 Zeichen von rechts
                cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, 0)
                #cursor.movePosition(QTextCursor.KeepAnchor, 0)
            elif 4 <= self.selected_index % 8 <= 6:  # Spalten 5, 6, 7
                # Verschiebe Markierung um 1 Zeichen nach rechts
                cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.MoveAnchor, 1)
                cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, 2)
            elif self.selected_index % 8 == 7:  # Spalte 8
                # Kürze Markierung um 2 Zeichen von links
                cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.MoveAnchor, 2)
                cursor.movePosition(QTextCursor.NextCharacter, QTextCursor.KeepAnchor, 2)
            
            # Setze das Hintergrundhighlight
            fmt = QTextCursor().charFormat()
            fmt.setBackground(QColor("yellow"))
            cursor.setCharFormat(fmt) 
    
    # --------------------------------------------------
    # Zeichnet eine vertikale Linie nach der 4. Spalte.
    # --------------------------------------------------
    def paintEvent(self, event):
        super().paintEvent(event)
        
        painter = QPainter(self.viewport())
        painter.setPen(QColor("gray"))
        
        # Position der vertikalen Linie berechnen
        font_metrics = self.fontMetrics()
        space_width  = font_metrics.horizontalAdvance(" ")
        char_width   = font_metrics.horizontalAdvance("0")
        
        # --------------------------------------------------
        # Nach der 4. Spalte (4x2 Zeichen + 3 Leerzeichen)
        # --------------------------------------------------
        line_x = (3 * (2 * char_width + space_width) + space_width * 3) + 6
        
        painter.drawLine(QPoint(line_x, 0), QPoint(line_x, self.height()))
        painter.end()

class AsciiEditComponent(QPlainTextEdit):
    def __init__(self, parent=None):
        super(AsciiEditComponent, self).__init__(parent)
        
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        self.setStyleSheet("QWidget{padding:0px;}")
        
        self.asc_data = ""
    
    def set_asc_data(self, data):
        self.asc_data = data
        def to_printable(byte):
            if 0x20 <= byte <= 0x7E:  # Printable ASCII
                return chr(byte)
            elif byte == 0x09:  # Tab
                return "\t"
            elif byte == 0x0A:  # Line Feed
                return "\n"
            elif byte == 0x0D:  # Carriage Return
                return "\r"
            else:
                return f"<{byte:02X}>"
        
        # Konvertiere die Bytes
        printable_text = "".join(to_printable(b) for b in data)
        
        # Setze den Text in die QPlainTextEdit
        self.setPlainText(printable_text)

class HexViewer(QWidget):
    def __init__(self, parent=None):
        super(HexViewer, self).__init__(parent)
        
        self.setStyleSheet("QWidget{padding:0px;}")
        layout = QVBoxLayout()
        
        # Splitter für Hex- und ASCII-Ansicht
        splitter = QSplitter(Qt.Vertical)
        
        # Hex-Ansicht
        self.hex_edit = HexEditComponent()
        self.hex_edit.setReadOnly(True)
        
        # ASCII/Unicode-Ansicht
        self.asc_edit = AsciiEditComponent()
        self.asc_edit.setReadOnly(True)
        
        splitter.addWidget(self.hex_edit)
        splitter.addWidget(self.asc_edit)
        
        layout.addWidget(splitter)
        
        # Initialisierung der Daten
        self.hex_data = ""
        self.selected_index = -1
        
        # Verbinde Mausklicks in der Hex-Ansicht
        self.hex_edit.mousePressEvent = self.hex_edit.mousePressEvent
        
        self.setLayout(layout)
    
    def set_data(self, dat):
        self.hex_edit.set_hex_data(dat)
        self.asc_edit.set_asc_data(dat)

class ExecutableExplorer(QWidget):
    def __init__(self, parent=None):
        try:
            super(ExecutableExplorer, self).__init__(parent)
            
            # ----------------------------------------------
            # Hauptlayout mit vertikalem Splitter
            # ----------------------------------------------
            main_layout = QVBoxLayout(self)
            
            tab_widget = QTabWidget()
            tab_widget.setTabPosition(QTabWidget.North)
            tab_widget.setTabShape(QTabWidget.Rounded)
            
            self.file_tree = FileExplorer()
            
            
            vertical_splitter = QSplitter(Qt.Vertical)
            upper_splitter    = QSplitter(Qt.Horizontal)
            
            # ----------------------------------------------
            # Links: QListTree für EXE und DLL Dateien
            # ----------------------------------------------
            self.exe_dll_tree = QTreeView()
            self.exe_dll_tree.setHeaderHidden(False)
            self.exe_dll_tree.setMaximumWidth(200)
            
            header = self.exe_dll_tree.header()
            
            self.exe_dll_tree.setModel(self._create_file_tree_model())
            self.exe_dll_tree.setToolTip("EXE und DLL Dateien")
            
            header.setSectionResizeMode(0, header.Stretch)  # Dynamisch
            #header.setSectionResizeMode(1, header.Stretch)  #
            #header.setSectionResizeMode(2, header.Stretch)  #
            
            header.resizeSection(0, 222)
            #header.resizeSection(1, 122)
            
            # ----------------------------------------------
            # Rechts: QListTree für Symbole und Funktionen
            # ----------------------------------------------
            self.symbols_tree = QTreeView()
            self.symbols_tree.setHeaderHidden(False)
            self.symbols_tree.setMinimumWidth(320)
            
            self.symbols_tree.setModel(self._create_symbols_model())
            self.symbols_tree.setToolTip("Symbole und Funktionen")
            
            header = self.symbols_tree.header()
            header.setSectionResizeMode(0, header.Stretch)  # Dynamisch
            header.setSectionResizeMode(1, header.Stretch)  #
            
            #header.resizeSection(0, 122)
            #header.resizeSection(1, 122)
            
            # ----------------------------------------------
            # Unterer Bereich: QListTree für Pfade und
            # Verzeichnisse
            # ----------------------------------------------
            splitter = QSplitter(Qt.Horizontal)
            
            # ----------------------------------------------
            # Untere Ansicht: Hex-View und bin-View
            # ----------------------------------------------
            data = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
            self.hex_view = HexViewer()
            self.hex_view.setStyleSheet("QWidget{padding:0px;}")
            self.hex_view.set_data(data)
            
            self.asm_view = AssemblerViewer()
            self.dbg_ctrl = DebugControls()
            
            splitter.addWidget(self.hex_view)
            splitter.addWidget(self.asm_view)
            splitter.addWidget(self.dbg_ctrl)
            
            # ----------------------------------------------
            # Layout zusammenfügen
            # ----------------------------------------------
            upper_splitter.addWidget(self.file_tree)
            upper_splitter.addWidget(self.exe_dll_tree)
            upper_splitter.addWidget(self.symbols_tree)
            
            vertical_splitter.addWidget(upper_splitter)
            vertical_splitter.addWidget(splitter)
            
            #
            mz_info = QWidget()
            pe_info = QWidget()
            
            # ----------------------------------------------
            # Tab einfügen
            # ----------------------------------------------
            tab_widget.addTab(vertical_splitter, _("Files"))
            tab_widget.addTab(mz_info, _("MZ-Info"))
            tab_widget.addTab(pe_info, _("PE-Info"))
            
            main_layout.addWidget(tab_widget)
            
            # ----------------------------------------------
            # Beispiel-Daten eintragen
            # ----------------------------------------------
            self.populate_example_data()
            
        except Exception as e:
            showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
            sys.exit(1)
    
    def _create_file_tree_model(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Dateien"])
        return model
    
    def _create_symbols_model(self):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Funktion", "Offset"])
        return model
    
    def populate_example_data(self):
        # ----------------------------------------------
        # EXE/DLL Dateien einfügen
        # ----------------------------------------------
        exe_item = QStandardItem("Programme (EXE)")
        dll_item = QStandardItem("Bibliotheken (DLL)")
        
        exe_item.appendRow([QStandardItem("test.exe"), QStandardItem("42"), QStandardItem("Info")])
        dll_item.appendRow([QStandardItem("test.dll"), QStandardItem("42"), QStandardItem("Info")])
        
        self.exe_dll_tree.model().appendRow(exe_item)
        self.exe_dll_tree.model().appendRow(dll_item)
        
        # ----------------------------------------------
        # Symbole und Funktionen einfügen
        # ----------------------------------------------
        sym_item1 = QStandardItem("Funktionen in explorer.exe")
        sym_item1.appendRow([QStandardItem("CreateWindow"),   QStandardItem("0x1000")])
        sym_item1.appendRow([QStandardItem("ShowWindow"),     QStandardItem("0x1000")])
        
        sym_item2 = QStandardItem("Funktionen in kernel32.dll")
        sym_item2.appendRow([QStandardItem("LoadLibrary"),    QStandardItem("0x1000")])
        sym_item2.appendRow([QStandardItem("GetProcAddress"), QStandardItem("0x1000")])
        
        self.symbols_tree.model().appendRow(sym_item1)
        self.symbols_tree.model().appendRow(sym_item2)
        
        # ----------------------------------------------
        # DLL-Pfade einfügen
        # ----------------------------------------------
        path_item = QStandardItem("DLL-Pfade")
        path_item.appendRow(QStandardItem("C:\\Windows\\System32\\kernel32.dll"))
        path_item.appendRow(QStandardItem("C:\\Windows\\System32\\user32.dll"))

if genv.GENERATE_DOC:
    word = win32com.client.Dispatch("Word.Application")
    doc = word.Documents.Add(genv.USE_DOC_TEMPLATE)
    if genv.PAGE_FORMAT_LANDSCAPE:
        doc.PageSetup.Orientation = win32com.client.constants.wdOrientLandscape
    else:
        doc.PageSetup.Orientation = win32com.client.constants.wdOrientPortrait

HTML_FILE_START = """<html>
<meta http-equiv='Content-Type' content='text/html; charset=iso-8859-1'>
<link rel='stylesheet' type='text/css' href='formate.css'>
<body>"""
HTML_FILE_STOP = """</body></html>"""

LINKS = {}
REVERSE_LINK_MAP = {}

class HTMLHelpSubject:
    "a help subject consists of a topic, and a filename"
    def __init__( self, topic, filename, keywords = [] ):
        self.topic, self.filename = topic, filename
        self.keywords = keywords + [topic]
        self.subjects = []
    
    def AsHHCString(self,tab):
        return f"""{tab}<LI> <OBJECT type='text/sitemap'>
{tab}    <param name='Name'  value='{self.topic}'>
{tab}    <param name='Local' value='{self.filename}'>
{tab}</OBJECT>"""
    
    def AsHHKString(self):
        result = ""
        for keyword in self.keywords:
            result += f"""    <LI> <OBJECT type='text/sitemap'>
        <param name='Name'  value='{keyword}'>
        <param name='Local' value='{self.filename}'>
    </OBJECT>"""
        return result

class HTMLHelpProject:
    def __init__(self,subject,filename="default.html",title=None):
        
        if title is None:
            title = subject
        
        # this is the root node for the help project. add subprojects here.
        if filename is not None:
            self.root = HTMLHelpSubject(subject, filename)
        else:
            self.root = HTMLHelpSubject(None, None)
        
        self.language      = "0x407 German (Germany)"
        self.index_file    = subject + ".hhk"
        self.default_topic = filename
        self.toc_file      = subject + ".hhc"
        self.compiled_file = subject + ".chm"
        self.project_file  = subject + ".hhp"
        self.title = title
        self.index = {}
        self.use_toplevel_project = 0
    
    def Generate(self,directory):
        # make sure, target directory exists
        try:
            os.makedirs(directory)
        except:
            pass
        
        # generate files
        self.GenerateHHP( os.path.join( directory, self.project_file ) )
        self.GenerateHHK( os.path.join( directory, self.index_file ) )
        self.GenerateTOC( os.path.join( directory, self.toc_file ) )
    
    def GenerateHHP(self,filename):
        "Helper function: Generate HtmlHelp Project."
        assert(self.root is not None)
        
        with open(filename,"w") as self.file:
            self.file.write(f"""[OPTIONS]
Compatibility=1.1 or later
Compiled file={self.compiled_file}
Contents file={self.toc_file}
Default topic={self.default_topic}
Display compile progress=No
Full-text search=Yes
Index file={self.index_file}
Language={self.language}
Title={self.title}

[FILES]

[INFOTYPES]\n\n
""")
    
    def GenerateTOCRecursive(self,file,subject,indent):
        tab = "\t" * indent
        for item in subject.subjects:
            self.file.write(item.AsHHCString(tab))
            if item.subjects:
                self.file.write(tab + "<UL>\n")
                self.GenerateTOCRecursive(file, item, indent+1)
                self.file.write(tab + "</UL>\n")
    
    def GenerateTOC(self,filename):
        "Helper function: Generate Table-of-contents."
        assert(self.root is not None)
        
        with open(filename,"w") as self.toc_file:
            self.toc_file.write("""<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<HTML>
  <HEAD>
    <meta name="GENERATOR" content="python">
  </HEAD>
<BODY>
  <OBJECT type="text/site properties">
    <param name="FrameName" value="right">
  </OBJECT>
""")
            #if not self.use_toplevel_project:
            
            self.toc_file.write("  <UL>\n")
            #
            self.toc_file.write("    <LI><OBJECT type=\"text/sitemap\">\n")
            self.toc_file.write("\t<param name=\"Local\" value=\"default.html\">\n")
            self.toc_file.write("\t<param name=\"Name\" value=\"Index\">\n")
            self.toc_file.write("    </OBJECT></LI>\n")
            #
            self.toc_file.write("  </UL>\n")
            
            #self.toc_file.write(self.root.AsHHCString("\t"))
            #self.GenerateTOCRecursive(self.file,self.root,2)
            #self.toc_file.write("  </UL>")
            #else:
            #    self.toc_file.write("  <UL>")
            #    self.GenerateTOCRecursive(self.file,self.root,1)
            #    self.toc_file.write("  </UL>")
            
            self.toc_file.write("</BODY>\n</HTML>\n")
            self.toc_file.close()
    
    def GenerateHHKRecursive(self,file,subject):
        for item in subject.subjects:
            self.file.write(item.AsHHKString())
            if item.subjects:
                self.GenerateHHKRecursive(file, item)
    
    def GenerateHHK(self,filename):
        "Helper function: Generate Index file."
        assert(self.root is not None)
        
        try:
            with open(filename,"w") as self.file:
                self.file.write("""<!DOCTYPE HTML PUBLIC '-//IETF//DTD HTML//EN'>
<HTML>
<HEAD>
<meta name='GENERATOR' content='Python'>
<!-- Sitemap 1.0 -->
</HEAD><BODY>
<UL>""")
                if self.root.topic:
                    self.file.write(self.root.AsHHKString())
                    
                self.GenerateHHKRecursive(self.file,self.root)
                self.file.write("</UL>\n</BODY></HTML>")
                self.file.close()
        except Exception as e:
            exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
            tb = traceback.extract_tb(e.__traceback__)[-1]
            
            dummy = ("-"*40)
            err_message = (f""
            + f"Exception occur at module import:\n"
            + f"type : {exc_type.__name__}\n"
            + f"value: {exc_value}\n"
            + f"{dummy}\n"
            + f"file : {tb.filename}\n"
            + f"line : {tb.lineno}")
            
            msg = QMessageBox()
            msg.setWindowTitle(_("Error"))
            msg.setText(err_message)
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(_("msgbox_css"))
            
            btn_ok = msg.addButton(QMessageBox.Ok)
            result = msg.exec_()
            pass

class Table():
    def __init__(self):
        self.rows = []
    
    def Generate(self):
        global doc, doc_index, doc_index_list
        
        doc_index = doc.Range().End-1
        doc_index_list.append(doc_index)
        
        table = self.rows
        
        # eine Tabelle ans Textende einfügen 
        doc_table = doc.Tables.Add(doc.Range(doc_index, doc_index),len(table),len(table[0]))
        
        # Zeile 0 ist die Überschriftszeile
        doc_table.Rows(1).HeadingFormat = ~0
        
        # Alle Zellen mit Text füllen
        for sri in xrange(len(table)):
            row = table[sri]
            for sci in xrange(len(row)):
                cell = row[sci]
                r = doc_table.Cell(sri+1,sci+1).Range
                r.Style = cell.style
                r.InsertAfter(cell.text)
                if cell.texture:
                    doc_table.Cell(sri+1,sci+1).Shading.Texture = cell.texture
        
        doc_table.Columns.AutoFit()
        
        doc_index = doc.Range().End-1
        doc_index_list.append(doc_index)        

class TC:
    def __init__(self,text,style="TAB"):
        self.text = text
        self.style = style.upper()
        self.texture = None
        if self.style == "TABHEAD":
            self.texture = win32com.client.constants.wdTexture10Percent

doc_index_list = []
doc_index = 0
last_body = ""
output = None    
data = ""

def isnumeric(token):
    try:
        int(token)
        return 1
    except:
        return 0

current_table = None
is_recording_preformatted = 0

# this function gets called for all tokens the parser finds
def Pass1_OnToken(token):
    global FILENAMES, project, output, last_body, file_index, is_recording_preformatted
    global doc_index_list, doc_index, current_table
    
    token_string = token
    token = map(string.lower,token.split())
    
    # end of header token -------------------------------------------------------------
    if token[0][:2] == '/h' and isnumeric(token[0][2:]):
        
        project.last_subject.topic = last_body
        project.last_subject.keywords[0] = last_body
        
        if genv.GENERATE_DOC:
            doc.Content.InsertAfter("\n")
            doc_index += 1
            doc.Range(
            doc_index_list[-1],
            doc_index).Style = getattr(win32com.client.constants,"wdStyleHeading%d" % project.last_subject.level)
            doc_index_list.append(doc_index)       
    
    elif token[0] == "a" and token[1][:5] == "href=":
        link_to = token[1]
        x = link_to.find('"')
        if x >= 0:
            link_to = link_to[x+1:]
        x = link_to.rfind('"')
        if x >= 0:
            link_to = link_to[:x]        
        if output:
            try:
                output.write('<a href="%s%s">' % (LINKS[link_to],link_to))
            except:
                DebugPrint(f"Warning, link '{link_to}' invalid or external.")
            return
    
    # table handling BEGIN ----------------------------------
    elif token[0] == "table" and genv.GENERATE_DOC:
        current_table = Table()
    
    elif token[0] == "tr" and genv.GENERATE_DOC and current_table:
        if len(current_table.rows) > 1:
            for item in current_table.rows[-1][:-1]:
                item.style = "TABC"
        
        current_table.rows.append([])
    
    elif token[0] == "/td" and genv.GENERATE_DOC and current_table:
        style = "TAB"
        if len(current_table.rows) == 1:
            style = "TABHEAD"
        
        current_table.rows[-1].append(TC(last_body,style))
    
    elif token[0] == "/table" and genv.GENERATE_DOC and current_table:
        if len(current_table.rows) > 1:
            for item in current_table.rows[-1][:-1]:
                item.style = "TABC"
        
        current_table.Generate()
        current_table = None
    
    # table handling END ----------------------------------    
    elif token[0] == "pre":
        is_recording_preformatted = 1
    
    # preprocessor define
    elif token[0] == '/pre':
        is_recording_preformatted = 0
        if genv.GENERATE_DOC:
            doc.Content.InsertAfter("\n")
            doc_index += 1
            doc.Range(doc_index_list[-1],doc_index).Style = "sourcecode"
            doc_index_list.append(doc_index)          
    
    # bullet-style list entry
    elif token[0] == '/li':
        if genv.GENERATE_DOC:
            doc.Content.InsertAfter("\n")
            doc_index += 1
            doc.Range(doc_index_list[-1],doc_index).Style = win32com.client.constants.wdStyleListBullet
            doc_index_list.append(doc_index)        
    
    # end of paragraph
    elif token[0] == '/p':
        if genv.GENERATE_DOC and not current_table:
            doc.Content.InsertAfter("\n")
            doc_index += 1
            doc_index_list.append(doc_index)
    
    # font-style BOLD
    elif token[0] == '/b':
        if genv.GENERATE_DOC:
            doc.Content.InsertAfter(" ")
            doc.Range(doc_index_list[-1],doc_index).Bold = 1
            doc_index += 1
            doc_index_list = doc_index_list[:-1]
    
    # font-style ITALIC
    elif token[0] == '/i':
        if genv.GENERATE_DOC:
            doc.Content.InsertAfter(" ")
            doc.Range(doc_index_list[-1],doc_index).Italic = 1
            doc_index += 1
            doc_index_list = doc_index_list[:-1]
    
    elif token[0] == "img":
        filename = token[1]
        x = filename.find('"')
        if x > 0:
            filename = filename[x+1:]
        x = filename.rfind('"')
        if x > 0:
            filename = filename[:x]
        filename = os.path.join(genv.TARGET_DIRECTORY,filename)
        if genv.GENERATE_DOC:
            doc.Content.InsertAfter("\n")
            DebugPrint("DATEINAME=" + filename)
            picture = doc.InlineShapes.AddPicture( filename, 1, 0,Range=doc.Range(doc_index,doc_index) )
            doc.Content.InsertAfter("\n")
            doc_index = doc.Range().End-1
            doc_index_list.append(doc_index)
    
    # start of header token
    elif token[0][:1] == 'h' and isnumeric(token[0][1:]):
        
        token = token[0]        
        
        # close old topic        
        if output:
            output.write(HTML_FILE_STOP)
            output.close()
        
        # generate new topic      
        filename = "file%d.htm" % file_index
        
        output = open( os.path.join(genv.TARGET_DIRECTORY,filename), "w" )
        file_index += 1
        output.write(HTML_FILE_START)
        
        subject = HTMLHelpSubject(filename, filename)
        project.last_subject = subject
        
        if genv.ADD_LINKS_TO_INDEX:
            try:
                for keyword in REVERSE_LINK_MAP[filename]:
                    subject.keywords.append(keyword[1:])
            except:
                pass
        
        subject.level = topic_level = int(token[1:])
        
        if topic_level == 1:
            # this is a root project
            project.root.subjects.append(subject)
            project.levels[1] = subject
        else:
            parent_topic_level = topic_level-1
            while (parent_topic_level > 0) and not project.levels.has_key(parent_topic_level):
                parent_topic_level = parent_topic_level-1
            
            if parent_topic_level == 0:
                project.root.subjects.append(subject)
                project.levels[1] = subject
            else:
                project.levels[parent_topic_level].subjects.append(subject)
            
            project.levels[topic_level] = subject
        
        if genv.GENERATE_DOC and genv.DOC_PAGE_BREAKS:
            doc.Range(doc_index,doc_index).InsertBreak(win32com.client.constants.wdPageBreak)
            doc_index = doc.Range().End-1
            doc_index_list.append(doc_index)
    
    if output:
        output.write("<"+token_string+">")

# this function gets called for all text bodies the parser finds. the default is to write the token to a file
def Pass1_OnBody(body):
    global output, last_body, doc, doc_index, current_table, is_recording_preformatted
    
    last_body = body
    if output:
        output.write(body)
    if genv.GENERATE_DOC and not current_table:
        if not is_recording_preformatted:
            body = body.replace("\n"," ")
        body = body.replace("&lt;","<")
        body = body.replace("&gt;",">").strip()
        if body:
            doc_index_list.append(doc_index)
            doc.Content.InsertAfter(body)
            doc_index += len(body)

# this function gets called for all tokens the parser finds
def Pass0_OnToken(token):
    global last_filename, LINKS, file_index
    
    if token[:7] == "a name=":
        x = token.find('"')
        if x >= 0:
            token = token[x+1:]
        x = token.rfind('"')
        if x >= 0:
            token = token[:x]
        if LINKS.has_key(token):
            DebugPrint(f"Warning, link '{token}' is used more than once.")
            
        LINKS[token] = last_filename
    
    elif token[:1] == 'h' and isnumeric(token[1:]):
        
        # generate new topic      
        last_filename = "file%d.htm" % file_index
        file_index += 1

# this function gets called for all text bodies the parser finds. the default is to write the token to a file
def Pass0_OnBody(body):
    pass

def ParseData(onbody,ontoken):
    global output, output_index
    output, output_index = None, 0
    
    current_token, current_body = None, None
    
    for i in range(len(data)):
        c = data[i]
        if c == '<':
            if current_body is not None:
                onbody(data[current_body:i])
                current_body = None
            current_token = i+1
        elif c == '>':
            if current_token is not None:
                ontoken(data[current_token:i])
            current_token = None
        elif current_body is None and current_token is None:
            current_body = i
    
    if current_body:
        onbody(data[current_body:i])

class createHTMLproject():
    def __init__(self):
        project = HTMLHelpProject( genv.PROJECT_NAME, genv.DEFAULT_TOPIC )
        project.levels = {}
        project.last_subject = None
        project.use_toplevel_project = genv.USE_TOPLEVEL_PROJECT
        
        with open(genv.PROJECT_SOURCE,"r") as file:
            data = file.read()
        
        file_index = 0
        ParseData(Pass0_OnBody,Pass0_OnToken)
        
        if genv.ADD_LINKS_TO_INDEX:
            for key in LINKS:
                file = LINKS[key]
                try:
                    REVERSE_LINK_MAP[file].append(key)
                except:
                    REVERSE_LINK_MAP[file] = [key]
        
        file_index = 0
        ParseData(Pass1_OnBody,Pass1_OnToken)
        
        if output:
            output.write(HTML_FILE_STOP)
            output.close()
        
        try:
            # -----------------------------------------
            # save stdout to restore later ...
            # -----------------------------------------
            self.console_old = sys.stdout
            self.console_new = DOSConsole(application_window)
            self.console_new.win.setWordWrapMode(QTextOption.WordWrap)
            
            # -----------------------------------------
            # non-blocking show dialog ...
            # -----------------------------------------
            self.console_new.show()
            self.console_new.win.append(_("generationg chm file..."))
            
            # -----------------------------------------
            # set redirect of stdout to dialog
            # -----------------------------------------
            self.process = QProcess(self.console_new)
            self.process.readyReadStandardOutput.connect(self.handle_stdout)
            self.process.readyReadStandardError.connect (self.handle_stderr)
            self.process.finished.connect(self.process_finished)
            
            # -----------------------------------------
            # generate a chm project file ...
            # -----------------------------------------
            project.Generate(genv.TARGET_DIRECTORY)
            
            # -----------------------------------------
            # create chm binary file ...
            # -----------------------------------------
            saved_working_dir = os.getcwd()
            os.chdir(genv.v__app__internal__ + "/temp")
            
            # todo: set hhc.exe path !
            parameter = '"' + genv.v__app__internal__ + "/temp/" + project.project_file + '"'
            #
            command   = '"' + genv.hhc_compiler  + '" ' +  parameter
            command   = command.replace('/', "\\")
            
            self.process.start(command)
            
            # -----------------------------------------
            # blocking show dialog - wait for user ...
            # -----------------------------------------
            self.console_new.exec_()
            
            # ---------------------------------
            # restore stdout
            # ---------------------------------
            sys.stdout = self.console_old
            os.chdir(saved_working_dir)
            
        except Exception as e:
            DebugPrint(e)
    
    def handle_stdout(self):
        datas  = self.process.readAllStandardOutput()
        stdout = bytes(datas).decode("utf8")
        stdout = stdout.replace('\r','')
        self.console_new.append(stdout)
    
    def handle_stderr(self):
        datas = self.process.readAllStandardError()
        stderr = bytes(datas).decode("utf8")
        stderr = stderr.replace('\r','')
        self.console_new.win.append(stderr)
    
    def process_finished(self):
        self.console_new.win.append(_("Command finished."))
        return

# ------------------------------------------------------------------------------
# convert string to list ...
# ------------------------------------------------------------------------------
def StrToList(string):
    liste = []
    lines = string.split("\r\n")
    
    for line in lines:
        line = re.sub(r"^(\[)|(\],$)|(\]$)", '', line)
        line = line.split(",")
        col1 = re.sub(r'^\"|\"$', '', line[0])
        col2 = re.sub(r'^PROJECT_.*\".*\"$|^\"', '', line[1])
        col2 = col2.replace("@",",")
        list_item = [ col1, col2 ]
        liste.append(list_item)
    return liste

# Custom function to register instances
def register_instance(name, instance):
    instance_names[id(instance)] = name

# Custom function to get instance name
def get_instance_name(instance):
    return instance_names.get(id(instance), None)

def octal_to_ascii(octal_string):
    octal_values = octal_string.split()
    ascii_string = ''.join([chr(int(octal, 8)) for octal in octal_values])
    return ascii_string

class RunTimeLibrary:
    # -----------------------------------------------------------------------
    # \brief __init__ is the initializator - maybe uneeded, because __new__
    #        is the constructor ...
    # -----------------------------------------------------------------------
    def __init__(self):
        self.version     = "1.0.0"
        self.author      = "paule32"
        self.initialized = False
    
    # -----------------------------------------------------------------------
    # \brief  this is the constructor of class "RunTimeLibrary" ...
    #         The return value is the created object pointer in memory space.
    #
    # \param  nothing
    # \return Object - a pointer to this class object
    # -----------------------------------------------------------------------
    def __new__(self):
        self.initialized = True
        return self
    
    def __enter__(self):
        return self
    
    # -----------------------------------------------------------------------
    # \brief  destructor for class "RunTimeLibrary" ...
    #
    # \param  nothing
    # \return nothing - destructors doesnt return values.
    # -----------------------------------------------------------------------
    def __del__(self):
        self.check_initialized(self)
        self.initialized = False
    
    # -----------------------------------------------------------------------
    # \brief  This function returns True if a file with "name" exists on the
    #         disk, False otherwise. On Microsoft Windows, the function will
    #         return False if a directory is passed as "name"
    #
    # \param  name  - the script file name to check.
    # \return False - when the checks fails
    #         True  - when the file checks success
    # -----------------------------------------------------------------------
    def FileExists(name):
        RunTimeLibrary.check_initialized()
        if not os.path.exists(name):
            return False
        elif os.path.isdir(name):
            return False
        elif os.path.isfile(name):
            return True
    
    # -----------------------------------------------------------------------
    # \brief  This function read the content of a text file, and return the
    #         readed content.
    #
    # \param  name - the file name that content should read
    # \return encoding text string content that was read from file.
    # -----------------------------------------------------------------------
    def ReadFile(name):
        RunTimeLibrary.check_initialized()
        if not RunTimeLibrary.FileExists(name):
            raise EParserError(10000)
        with open(name, "r", encoding="utf-8") as file:
            file.seek(0)
            data = file.read()
            file.close()
        return data
    
    # -----------------------------------------------------------------------
    # \brief  StringCompare compare the string "str" with the occurences of
    #         strings in the list. The string_list can contain multiple
    #         strings separated by a comma.
    #
    # \param  str  - the string to be check
    # \param  list - the list of strings which can contain "str"
    # \return True - if check is okay, True is the return value, else False
    # -----------------------------------------------------------------------
    def StringCompare(string, string_list):
        result = False
        if string in string_list:
            return True
        else:
            return False
    
    # -----------------------------------------------------------------------
    # \brief raise an exception, if the runtime libaray is not initialized...
    # -----------------------------------------------------------------------
    def check_initialized():
        if not RunTimeLibrary.initialized:
            raise EParserError(1000)

class TMenu:
    struct = [];
    def __init__(self,parent):
        DebugPrint(parent);
        return
    def add(self, menu_list):
        self.struct.append(menu_list)
        return
    def show(self, make_visible=True):
        if make_visible:
            DebugPrint(self.struct);
        return

# ---------------------------------------------------------------------------
# \brief this class provides accessible menubar for the application on the
#        top upper part line.
# ---------------------------------------------------------------------------
class TMenuBar2(TMenu):
    def __init__(self,parent):
        super().__init__(parent)
        font_name  = "Arial"
        font_size  = 10
        
        font_color = "white"
        back_color = "navy"
        back_str   = "background-color"
        
        str_font   = "font"
        str_size   = "size"
        str_color  = "color"
        
        self.standardMenuBar = {
        "File": [{
            "subitem": [{
                "New" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color }
                ],
                "Open" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color }
                ],
                "Save" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color }
                ],
                "Save As" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color }
                ],
                "Print" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color }
                ],
                "Exit" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color }
                ],
            }]
        }],
        "Edit": [{
            "subitem": [{
                "Undo" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color },
                ],
                "Redo" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color },
                ],
            }]
        }],
        "Help": [{
            "subitem": [{
                "Online" : [
                    { str_font  : font_name  },
                    { str_size  : font_size  },
                    { str_color : font_color },
                    { back_str  : back_color },
                ],
                "About"  : [
                    { str_font  : font_name  },
                    { str_size  : font_size  },
                    { str_color : font_color },
                    { back_str  : back_color }
                ]
            }]
        }]  }
        
        super().add(self.standardMenuBar)
        super().show(self)
        return

class FileSystemWatcher(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.watcher = QFileSystemWatcher()
        self.fileContents = {}
    
    def addFile(self, filePath):
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
        DebugPrint((""
        + "Exception: List instructions error.\n"
        + "note: Did you miss a parameter ?\n"
        + "note: Add more information."))
        error_result = 1
        return

class ListMustBeInstructionError(Exception):
    def __init__(self):
        DebugPrint("Exception: List must be of class type: InstructionItem")
        error_result = 1
        return
class ListIndexOutOfBoundsError(Exception):
    def __init__(self):
        DebugPrint("Exception: List index out of bounds.")
        error_result = 1
        return

class ENoSourceHeader(Exception):
    def __init__(self, message):
        self.message = message
        genv.have_errors = True
    def __str__(self):
        error_result = 0
        return str(self.message)

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
        DebugPrint("Exception: unknown id: " + message)
        DebugPrint("Line     : " + str(lineno))
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
        DebugPrint('today is %s' % cls(date.today().isoweekday()).name)

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

# ---------------------------------------------------------------------------
# \brief A dos-console Qt5 Dialog - used by DOS console Applications.
# ---------------------------------------------------------------------------
class DOSConsoleWindow(QTextEdit):
    def __init__(self, parent=None):
        super().__init__()
        
        self.setReadOnly(False)
        self.setStyleSheet("""
        background-color: black;
        font-family: 'Courier New';
        font-size: 10pt;
        color: gray;
        """)
        #
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy  (Qt.ScrollBarAlwaysOff)
        
        char_width, char_height = self.get_char_dimensions('A')
        #
        self.setMinimumWidth ((char_width  * 96) - 10)
        self.setMaximumWidth ((char_width  * 96) - 10)
        #
        self.setMinimumHeight((char_height * 33) - 5)
        self.setMaximumHeight((char_height * 33) - 5)
        
        self.cols   = 80
        self.rows   = 25
        
        self.current_x = 0
        self.current_y = 0
        
        self.fg_color  = "#FF0000"
        self.bg_color  = "#000000"
        
        # ------------------------------------------------
        # initial create/fill the buffer with a empty char
        # ------------------------------------------------
        self.buffer = [['&nbsp;'          for _ in range(self.cols)] for _ in range(self.rows)]
        self.colors = [['#ff0000:#000000' for _ in range(self.cols)] for _ in range(self.rows)]
    
    def get_char_dimensions(self, char):
        font         = self.font()
        font_metrics = QFontMetrics(font)
        
        char_width   = font_metrics.horizontalAdvance(char)
        char_height  = font_metrics.height()
        
        return char_width, char_height
    
    def setcolor(self, fg_color, bg_color):
        self.fg_color = fg_color
        self.bg_color = bg_color
        
        result = self.fg_color + ':' + self.bg_color
        return result
    
    def gotoxy(self, xpos, ypos):
        self.current_x = xpos - 1
        self.current_y = ypos - 1
        return
    
    # ---------------------------------------------------------
    # \brief  Print the current date.
    # \return string => the actual date as string.
    # ---------------------------------------------------------
    def print_date(self):
        result = datetime.now().strftime("%Y-%m-%d")
        return result
    
    def clear_screen(self):
        self.buffer.clear()
        self.colors.clear()
        
        self.buffer = [['&nbsp;'          for _ in range(self.cols)] for _ in range(self.rows)]
        self.colors = [['#ff0000:#000000' for _ in range(self.cols)] for _ in range(self.rows)]
        
        self.gotoxy(1, 1)
    
    # ---------------------------------------------------------
    # \brief  Print the text, given by the first parameter.
    #
    # \param  text - string
    # \param  fg   - string  foreground color for text
    # \param  bg   - string  background color for text
    # \return nothing
    # ---------------------------------------------------------
    def print_line(self,
        text,           # text
        fg_color=None,  # foreground color
        bg_color=None): # background color
        if fg_color == None:
            fg_color = self.fg_color
        if bg_color == None:
            bg_color = self.bg_color
        try:
            text_html = ""
            
            # ----------------------------
            # set text cursor ...
            # ----------------------------
            x = self.current_x
            y = self.current_y
            
            color = self.fg_color + ':' + self.bg_color
            i = 0
            for row in range(self.rows):
                if i >= len(text):
                    break
                if row > y:
                    break
                for col in range(self.cols):
                    if i >= len(text):
                        break
                    if (col >= x) and (col <= (x + i)):
                        if text[i] == ' ':
                            self.buffer[y][col] = '&nbsp;'
                            self.colors[y][col] = color
                        else:
                            self.buffer[y][col] = text[i]
                            self.colors[y][col] = color
                        i += 1
            
            for row in range(self.rows):
                for col in range(self.cols):
                    field_value = self.buffer[row][col]
                    color       = self.colors[row][col].split(':')
                    
                    if not field_value == '&nbsp;':
                        text_html += f'<span style="color:{color[0]};background-color:{color[1]};">'
                        text_html += field_value
                        text_html += '</span>'
                    else:
                        text_html += f'<span style="color:{color[0]};background-color:{color[1]};">'
                        text_html += field_value
                        text_html += '</span>'
                text_html += "<br>"
            self.setHtml(text_html)
        except Exception as e:
            DebugPrint(e)
    
    # ---------------------------------------------------------
    # \brief  This definition try to get the color value by the
    #         given color string.
    #
    # \param  color - string => the color to parse
    #
    # \return html formated color sting: #rrggbb
    # ---------------------------------------------------------
    def getColor(self, color):
        if color:
            pos = 0
            value = ""
            while True:
                if pos > len(color):
                    break;
                c = color[pos]
                if c == '#':
                    if len(value) < 1:
                        value += c
                        continue
                    else:
                        return "#000000"
                elif (c >= '0' and c <= '9'):
                    if len(value) >= 6:
                        if value[0] == '#':
                            return value
                    value += c
                    continue
                elif (c >= 'a' and c <= 'f') or (c >= 'A' and c <= 'F'):
                    if len(value) >= 6:
                        if value[0] == '#':
                            return value
                    value += c
                    continue
                elif (c >= 'g' and c <= 'z') or (c >= 'G' and c <= 'Z'):
                    if len(value) > 1:
                        if value[0] == '#':
                            return "#000000"
                    value += c
                    continue
                pos += 1
        else:
            return "#000000"

class DOSConsole(QDialog):
    def __init__(self, parent=None):
        super().__init__()
        
        dlg_layout = QHBoxLayout()
        lhs_layout = QVBoxLayout()
        rhs_layout = QVBoxLayout()
        
        printer_box = QListWidget()
        printer_box.setMaximumWidth(100)
        
        self.win = DOSConsoleWindow()
        self.win.setReadOnly(True)
        
        # close button, to close the QDialog
        btn_close  = QPushButton(_("Close"))
        btn_close.setMinimumHeight(32)
        btn_close.setFont(QFont(genv.v__app__font_edit,10))
        btn_close.clicked.connect(self.btn_close_clicked)
        
        lhs_layout.addWidget(printer_box)
        rhs_layout.addWidget(self.win)
        rhs_layout.addWidget(btn_close)
        
        dlg_layout.addLayout(lhs_layout)
        dlg_layout.addLayout(rhs_layout)
        
        self.setLayout(dlg_layout)
    
    def btn_close_clicked(self):
        self.close()

# ---------------------------------------------------------------------------
# \brief A dos-console Qt5 Dialog - used by dBase console Applications.
# ---------------------------------------------------------------------------
class C64ConsoleWindow(QTextEdit):
    class CursorOverlay(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            
            self.parent = parent
            
            self.setFont(QFont("C64 Pro Mono", 9))
            self.char_width, self.char_height = self.parent.get_char_dimensions('A')
            
            self.setAttribute  (Qt.WA_TransparentForMouseEvents)  # Ermöglicht Mausklicks auf den Hintergrund
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.SubWindow)  # Ohne Rahmen
            self.setAttribute  (Qt.WA_StyledBackground, True)
            
            self.setAutoFillBackground(True)
            
            self.setMinimumHeight (self.char_width )
            self.setMaximumHeight (self.char_width )
            #
            self.setMinimumWidth  (self.char_height)
            self.setMaximumWidth  (self.char_height)
            
            self.move(4,4)
                
            self.setStyleSheet("background-color: rgba(255,255,255, 128);")
            
        # ------------------------------------------------
        # Optional: Manuelles Zeichnen mit Alpha
        # ------------------------------------------------
        def tick(self, mode=False):
            if not mode: self.setStyleSheet("background-color: rgba(255, 255, 255,   0);")
            else:        self.setStyleSheet("background-color: rgba(255, 255, 255, 128);")
            
        def move_overlay(self, xpos, ypos):
            self.move(
                (self.char_width  * xpos) + 4,
                (self.char_height * ypos) + 4)
    
    def __init__(self, parent=None):
        super(C64ConsoleWindow, self).__init__(parent)
        
        # ------------------------------------------------
        # Drag-and-Drop deaktivieren
        # ------------------------------------------------
        self.setAcceptDrops(False)
        
        # ------------------------------------------------
        # Textauswahl ermöglichen, aber kein Drag-and-Drop
        # ------------------------------------------------
        self.setTextInteractionFlags(
            Qt.TextSelectableByMouse |
            Qt.TextSelectableByKeyboard)

        self.setViewportMargins(0, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)        
        
        self.setReadOnly(False)
        self.setWordWrapMode(QTextOption.NoWrap)
        
        self.overwrite_mode  = True
        self.cursor_visible  = True  # Status des blinkenden Cursors
        
        self.start_position  =  0
        self.key_count       =  0
        self.str_buffer      = ""
        
        self.setStyleSheet("""
        QTextEdit {
            background-color: black;
            border: none;       /* Kein Rahmen */
            padding: 0px;       /* Kein Innenabstand */
            margin: 0px;        /* Kein äußerer Abstand */
            font-family: 'C64 Pro Mono';
            font-size: 9pt;
            color: gray;
        }
        """)
        
        self.setFrameShape(QTextEdit.NoFrame)
        #
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy  (Qt.ScrollBarAlwaysOff)
        
        self.setFont(QFont("C64 Pro Mono", 9))
        char_width, char_height = self.get_char_dimensions('A')
        #
        self.font_min_height = ((char_height * 25) + (char_height)) - 5
        self.font_max_height = ((char_height * 25) + (char_height)) - 5
        #
        self.font_min_width  =  (char_width  * 41) - 4
        self.font_max_width  =  (char_width  * 41) - 4
        
        self.setMinimumWidth (self.font_min_width)
        self.setMaximumWidth (self.font_max_width)
        
        self.setMinimumHeight(self.font_min_height)
        self.setMaximumHeight(self.font_max_height)
                
        self.cursor_overlay = self.CursorOverlay(self)
        self.cols      = 40
        self.rows      = 25
        
        self.current_x = -1
        self.current_y = -1
        
        self.fg_color  = "#C0C0C0"
        self.bg_color  = "#6888FC"
        
        # ------------------------------------------------
        # initial create/fill the buffer with a empty char
        # ------------------------------------------------
        self.buffer = [['&nbsp;'          for _ in range(self.cols)] for _ in range(self.rows)]
        self.colors = [['#C0C0C0:#6888FC' for _ in range(self.cols)] for _ in range(self.rows)]
        
        # ------------------------------------------------
        # Timer für das Blinken des Block-Cursors
        # ------------------------------------------------
        self.cursor_timer = QTimer(self)
        self.cursor_timer.timeout.connect(self.toggle_cursor_visibility)
        self.cursor_timer.start(500)  # 500 ms für periodisches Blinken
    
    # ------------------------------------------------
    # Wechselt die Sichtbarkeit des Block-Cursors.
    # ------------------------------------------------
    def toggle_cursor_visibility(self):
        self.cursor_visible = not self.cursor_visible
        self.cursor_overlay.tick(self.cursor_visible)
        #self.viewport().update()  # Aktualisiert das Textfeld (ruft paintEvent auf)
    
    def get_char_dimensions(self, char):
        font         = self.font()
        font_metrics = QFontMetrics(font)
        
        char_width   = font_metrics.horizontalAdvance(char)
        char_height  = font_metrics.height()
        
        return char_width, char_height
    
    def setcolor(self, fg_color, bg_color):
        self.fg_color = fg_color
        self.bg_color = bg_color
        
        result = self.fg_color + ':' + self.bg_color
        return result
    
    def gotoxy(self, xpos, ypos):
        self.current_x = xpos - 1
        self.current_y = ypos - 1
        
        return
    
    # ---------------------------------------------------------
    # \brief  Print the current date.
    # \return string => the actual date as string.
    # ---------------------------------------------------------
    def print_date(self):
        result = datetime.now().strftime("%Y-%m-%d")
        return result
    
    def clear_screen(self):
        self.buffer.clear()
        self.colors.clear()
        
        self.buffer = [['&nbsp;'          for _ in range(self.cols)] for _ in range(self.rows)]
        self.colors = [['#C0C0C0:#6888FC' for _ in range(self.cols)] for _ in range(self.rows)]
        
        self.gotoxy(1, 1)
    
    # ---------------------------------------------------------
    # \brief  Print the text, given by the first parameter.
    #
    # \param  text - string
    # \param  fg   - string  foreground color for text
    # \param  bg   - string  background color for text
    # \return nothing
    # ---------------------------------------------------------
    def print_line(self,
        text,           # text
        fg_color=None,  # foreground color
        bg_color=None): # background color
        if fg_color == None:
            fg_color = self.fg_color
        if bg_color == None:
            bg_color = self.bg_color
        try:
            text_html = ""
            
            # ----------------------------
            # set text cursor ...
            # ----------------------------
            x = self.current_x
            y = self.current_y
            
            color = self.fg_color + ':' + self.bg_color
            i = 0
            for row in range(self.rows):
                if i >= len(text):
                    break
                if row > y:
                    break
                for col in range(self.cols):
                    if i >= len(text):
                        break
                    if (col >= x) and (col <= (x + i)):
                        if text[i] == ' ':
                            self.buffer[y][col] = '&nbsp;'
                            self.colors[y][col] = color
                        else:
                            self.buffer[y][col] = text[i]
                            self.colors[y][col] = color
                        i += 1
            
            for row in range(self.rows):
                for col in range(self.cols):
                    field_value = self.buffer[row][col]
                    color       = self.colors[row][col].split(':')
                    
                    if not field_value == '&nbsp;':
                        text_html += f'<span style="color:{color[0]};background-color:{color[1]};">'
                        text_html += field_value
                        text_html += '</span>'
                    else:
                        text_html += f'<span style="color:{color[0]};background-color:{color[1]};">'
                        text_html += field_value
                        text_html += '</span>'
                text_html += "<br>"
            self.setHtml(text_html)
        except Exception as e:
            self.gotoxy(0,1)
            #DebugPrint(e)
    
    # ---------------------------------------------------------
    # \brief  This definition try to get the color value by the
    #         given color string.
    #
    # \param  color - string => the color to parse
    #
    # \return html formated color sting: #rrggbb
    # ---------------------------------------------------------
    def getColor(self, color):
        if color:
            pos = 0
            value = ""
            while True:
                if pos > len(color):
                    break;
                c = color[pos]
                if c == '#':
                    if len(value) < 1:
                        value += c
                        continue
                    else:
                        return "#000000"
                elif (c >= '0' and c <= '9'):
                    if len(value) >= 6:
                        if value[0] == '#':
                            return value
                    value += c
                    continue
                elif (c >= 'a' and c <= 'f') or (c >= 'A' and c <= 'F'):
                    if len(value) >= 6:
                        if value[0] == '#':
                            return value
                    value += c
                    continue
                elif (c >= 'g' and c <= 'z') or (c >= 'G' and c <= 'Z'):
                    if len(value) > 1:
                        if value[0] == '#':
                            return "#000000"
                    value += c
                    continue
                pos += 1
        else:
            return "#000000"
    
    # ------------------------------------------
    # start/stop blink cursor - set to true.
    # ------------------------------------------
    def timer_start(self):
        self.cursor_timer.start(500)
        
    def timer_stop (self):
        if  self.cursor_timer.isActive():
            self.cursor_timer.stop()
            self.cursor_overlay.tick(True)
        
    # ------------------------------------------
    # Standard-Menü abrufen
    # ------------------------------------------
    def contextMenuEvent(self, event):
        menu = QMenu(self)

        # Aktionen hinzufügen
        undo_action = menu.addAction("Undo")
        redo_action = menu.addAction("Redo")
        menu.addSeparator()
        copy_action = menu.addAction("Copy")
        menu.addSeparator()
        select_all_action = menu.addAction("Select All")

        # Aktionen aktivieren/deaktivieren basierend auf Zustand
        undo_action.setEnabled(self.document().isUndoAvailable())
        redo_action.setEnabled(self.document().isRedoAvailable())
        copy_action.setEnabled(self.textCursor().hasSelection())

        # Aktion ausführen
        action = menu.exec_(event.globalPos())
        if action == undo_action:
            self.undo()
        elif action == redo_action:
            self.redo()
        elif action == copy_action:
            self.copy()
        elif action == select_all_action:
            self.selectAll()
    
    def mousePressEvent(self, event):
        # ------------------------------------------
        # Prüfen, ob die rechte Maustaste gedrückt
        # wurde, dann context menü manuell aufrufen
        # ------------------------------------------
        if event.button() == Qt.RightButton:
            self.contextMenuEvent(event)
        else:
            # Standard-Mausverhalten beibehalten
            super().mousePressEvent(event)
            
    # ------------------------------------------
    # Ermittelt den Text-Cursor
    # ------------------------------------------
    def keyHelper(self):
        xpos = self.current_x
        if xpos < 0:
            self.cursor_overlay.move_overlay(
            self.current_x + 1,
            self.current_y)
        else:
            self.cursor_overlay.move_overlay(
            self.current_x,
            self.current_y)
    
    # ------------------------------------------
    # Wird aufgerufen, wenn eine Taste
    # losgelassen wird.
    # ------------------------------------------
    def keyReleaseEvent(self, event):
        if  event.key() in [
            Qt.Key_Left,   Qt.Key_Right,
            Qt.Key_Up,     Qt.Key_Down,
            Qt.Key_Return, Qt.Key_Backspace ]:
            self.timer_start()
            return
            
        if  event.text().isalnum() \
        or  event.text().isspace():
            self.timer_start()
            return
            
    # ------------------------------------------
    # Bewegungstasten (nur Cursor verschieben,
    # ohne Text zu ändern)
    # ------------------------------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.timer_stop()
            
            self.str_buffer = ""
            self.current_x -= 1
            if self.current_x < 0:
                self.current_x = self.cols - 1
                self.current_y -= 1
                if self.current_y < 0:
                    self.current_y = self.rows - 1
            self.keyHelper()
            return
        elif event.key() == Qt.Key_Right:
            self.timer_stop()
            
            self.str_buffer = ""
            self.current_x += 1
            if self.current_x > self.cols - 1:
                self.current_x = 0
                self.current_y += 1
                if self.current_y >= self.rows:
                    self.current_y = 0
            self.keyHelper()
            return
        elif event.key() == Qt.Key_Up:
            self.timer_stop()
            
            self.str_buffer = ""
            self.current_y -= 1
            if self.current_y < 0:
                self.current_y = self.rows - 1
            self.keyHelper()
            return
        elif event.key() == Qt.Key_Down:
            self.timer_stop()
            
            self.str_buffer = ""
            self.current_y += 1
            if self.current_y >= self.rows:
                self.current_y = 0
            self.keyHelper()
            #super().keyPressEvent(event)
            return
        
        # ------------------------------------------
        # todo: auf commando prüfen !!!
        # ------------------------------------------
        elif event.key() == Qt.Key_Return:
            print(self.str_buffer)
            self.timer_stop()
            
            self.key_count  =  0
            self.current_y +=  1
            self.current_x  = -1
            if self.current_y >= self.rows:
                self.current_y = 0
            self.keyHelper()
            self.str_buffer = ""
            return
        # ------------------------------------------
        # Backspace: Cursor nach links verschieben,
        # ohne Text zu löschen
        # ------------------------------------------
        elif event.key() == Qt.Key_Backspace:
            self.timer_stop()
            self.del_buffer()
            
            self.current_x -= 1
            if self.current_x < 0:
                self.current_x = self.cols - 1
                self.current_y -= 1
                if self.current_y < 0:
                    self.current_y = self.rows - 1
            self.keyHelper()
            return
        
        # ------------------------------------------
        # Normale Eingabe: Überschreibmodus aktiv
        # ------------------------------------------
        if event.text().isalnum()\
        or event.text().isspace():
            self.timer_stop()
            
            self.current_x += 1
            self.key_count += 1
            if self.key_count >= 1:
                if  self.current_x >= 0 \
                and self.current_y == self.rows:
                    self.current_x  = 0
                    self.current_y  = 0
                    self.key_count  = 1
            #print(f"Xpos: {self.current_x}; Ypos: {self.current_y}; text: {event.text()}")
            if self.current_x >= self.cols:
                self.current_x = 0
                self.current_y += 1
                if self.current_y >= self.rows:
                    self.current_x = 0
                    self.current_y = 0
                    
            self.add_buffer(event.text())
            self.print_line(event.text())
            
            self.keyHelper()
            return
    
    def del_buffer(self):
        if len(self.str_buffer)> 0:
            self.str_buffer = \
            self.str_buffer[:-1]
            
    def add_buffer(self, ch):
        self.str_buffer += ch
        
    def toggle_overwrite_mode(self):
        """Umschalten zwischen Überschreib- und Einfügemodus."""
        self.overwrite_mode = not self.overwrite_mode
        
    def paintEvent(self, event):
        # Custom Painting (falls benötigt, z. B. ein Hintergrund zeichnen)
        painter = QPainter(self.viewport())
        painter.fillRect(self.rect(), QColor(64, 64, 248))
        painter.end()

        # Zeichne den Standardinhalt der QTextEdit
        super().paintEvent(event)
        
class C64ConsoleBorder(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        
        self.setStyleSheet("""
        QWidget {
            background-color: #4040F8;
            border: none;       /* Kein Rahmen */
            padding: 0px;       /* Kein Innenabstand */
            margin: 0px;        /* Kein äußerer Abstand */
        }
        """)
        
        w1 = QWidget()
        w2 = QWidget()
        w3 = QWidget()
        w4 = QWidget()
        w5 = QWidget()
        w6 = QWidget()
        w7 = QWidget()
        w8 = QWidget()
        
        w2.setStyleSheet("""
        background-image: url('./_internal/img/dresden.png');
        background-repeat: no-repeat;
        background-position: center;
        """)
        #vlayout = QVBoxLayout()
        #vlabel  = QLabel()
        #vlabel.setMaximumWidth(320)
        #vlabel.setMaximumHeight(64)
        #vlabel.setAlignment(Qt.AlignCenter)
        #pixmap  = QPixmap("./_internal/img/dresden.png")
        #vlabel .setPixmap(pixmap)
        #vlayout.addWidget(vlabel)
        
        wb = 39
        
        w1.setMinimumWidth (wb)
        w1.setMinimumHeight(wb)
        #
        w2.setMinimumWidth (wb)
        w2.setMinimumHeight(wb)
        #
        w3.setMinimumWidth (wb)
        w3.setMinimumHeight(wb)
        #
        w4.setMinimumWidth (wb)
        w4.setMinimumHeight(wb)
        #
        w5.setMinimumWidth (wb)
        w5.setMinimumHeight(wb)
        #
        w6.setMinimumWidth (wb)
        w6.setMinimumHeight(wb)
        #
        w7.setMinimumWidth (wb)
        w7.setMinimumHeight(wb)
        #
        w8.setMinimumWidth (wb)
        w8.setMinimumHeight(wb)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)
        
        grid_layout.addWidget(w1, 0, 0)
        grid_layout.addWidget(w2, 0, 1)
        grid_layout.addWidget(w3, 0, 2)
        grid_layout.addWidget(w4, 1, 0)
        grid_layout.addWidget(w5, 1, 2)
        grid_layout.addWidget(w6, 2, 0)
        grid_layout.addWidget(w7, 2, 1)
        grid_layout.addWidget(w8, 2, 2)
        
        grid_layout.addWidget(parent, 1, 1)  # Zeile 2, Spalte 0, über 2 Spalten
        
        self.setLayout(grid_layout)

class C64Console(QDialog):
    def __init__(self, parent=None):
        super(C64Console, self).__init__(parent)
        
        dlg_layout  = QHBoxLayout()
        lhs_layout  = QVBoxLayout()
        
        self.win = C64ConsoleWindow(self)
        self.win.gotoxy(1,1)
        self.win.setStyleSheet("""
        background-color: #6888FC;
        """)
        
        rhs_layout  = QVBoxLayout();
        rhs_layout.setSpacing(0)
        
        rhs_widget  = C64ConsoleBorder(self.win)
        printer_box = QListWidget()
        printer_box.setMaximumWidth(100)
        
        # close button, to close the QDialog
        btn_close = QPushButton(_("Close"))
        btn_close.setMinimumHeight(32)
        btn_close.setFont(QFont(genv.v__app__font_edit,10))
        btn_close.clicked.connect(self.btn_close_clicked)
        
        lhs_layout.addWidget(printer_box)
        
        rhs_layout.addWidget(rhs_widget)
        rhs_layout.addWidget(btn_close)
        
        dlg_layout.addLayout(lhs_layout)
        dlg_layout.addLayout(rhs_layout)
        
        self.setLayout(dlg_layout)
    
    def btn_close_clicked(self):
        self.close()

# ---------------------------------------------------------------------------
# \brief A parser generator class to create a DSL (domain source language)
#        parser with Python 3.12.
#
# \field files - an array of used script files
# \field data  - an array of used script files data
# \field info  - information about the parse processor (encoding, ...)
# \field stat  - for statistics
# \field rtl   - a link reference to the runtime library for this class
# ---------------------------------------------------------------------------
class ParserDSL:
    # -----------------------------------------------------------------------
    # \brief __init__ is the initializator - maybe uneeded, because __new__
    #        is the constructor ...
    # -----------------------------------------------------------------------
    def __init__(self):
        self.files  = []
        self.data   = []
        
        self.name   = ""
        
        self.info   = None
        self.stat   = None
        self.this   = None
        
        self.rtl    = None
        
        self.AST    = []
        
        self.initialized = False
    
    # -----------------------------------------------------------------------
    # \brief this is the constructor of class "ParserDSL" ...
    # -----------------------------------------------------------------------
    def __new__(self, lang="dbase"):
        self.name   = lang.lower()
        self.parser = self
        self.rtl    = RunTimeLibrary()
        self.AST    = []
        self.files  = [
            [ "root.src", "dbase", "** comment" ]
        ]
        self.initialized = True
        return self
    
    def __enter__(self):
        return self
    
    # -----------------------------------------------------------------------
    # \brief destructor for parser generator class ...
    # -----------------------------------------------------------------------
    def __del__(self):
        self.files.clear()
        self.data.clear()
    
    # -----------------------------------------------------------------------
    # \brief Add new script file to self.file array [].
    #
    # \param name - the file name of the script.
    # -----------------------------------------------------------------------
    def addFile(name):
        if not ParserDSL.rtl.FileExists(name):
            raise EParserError(10000)
        else:
            data = []
            code = ParserDSL.rtl.ReadFile(name)
            
            data.append(name)
            data.append(name)
            data.append(code)
            
            ParserDSL.files.append(data)
            #print(ParserDSL.files)
        return True
    
    # -------------------------------------------------------------------
    # \brief add comment types to the AST of a DSL parser.
    #        currently the following types are available:
    #
    #        dBase:
    #        ** one liner comment
    #        && one liner
    #        // one liner comment
    #        /* block */ dbase multi line comment block
    #
    #        C/C++:
    #        // C(C++ comment one liner
    #        /* block */ C++ multi line comment block
    #
    #        Bash, misc:
    #        # comment one liner
    #
    #        Assembly, LISP:
    #        ; one line comment
    # -------------------------------------------------------------------
    def add(object_type):
        if type(object_type) == ParserDSL.comment:
            self  = ParserDSL()
            which = ParserDSL.name.lower()
            
            # --------------------------
            # no syntax comments
            # --------------------------
            if which == "":
                comment = [[None,None]]
                comment_object = self.comment("unknown")
                comment_object.set(comment)
                self.AST.append(comment_object)
            # --------------------------
            # dBase 7 syntax comments
            # --------------------------
            if which == "dbase":
                comment = [
                    [ "**", None ],
                    [ "&&", None ],
                    [ "//", None ],
                    [ "/*", "*/" ],
                ]
                comment_object = self.comment(which)
                comment_object.set(comment)
                self.AST.append(comment_object)
            # --------------------------
            # modern C syntax comments
            # --------------------------
            elif which == "c":
                comment = [
                    ["/*", "*/" ],
                    ["//", None ],
                ]
                comment_object = self.comment(which)
                comment_object.set(comment)
                self.AST.append(comment_object)
            # --------------------------
            # modern C++ syntax comments
            # --------------------------
            elif self.rtl.StringCompare(which, ["c++","cc","cpp"]):
                comment = [
                    ["/*", "*/" ],
                    ["//", None ],
                ]
                comment_object = self.comment(which)
                comment_object.set(comment)
                self.AST.append(comment_object)
            # --------------------------
            # modern Pascal comments
            # --------------------------
            elif which == "pascal":
                comment = [
                    ["(*", "*)" ],
                    ["{" , "}"  ],
                    ["//", None ],
                ]
                comment_object = self.comment(which)
                comment_object.set(comment)
                self.AST.append(comment_object)
            # --------------------------
            # old ASM, and LISP comments
            # --------------------------
            elif self.rtl.StringCompare(which, ["asm","lisp"]):
                comment = [
                    [";", None ],
                ]
                comment_object = self.comment(which)
                comment_object.set(comment)
                self.AST.append(comment_object)
            # --------------------------
            # *nix tool style comments
            # --------------------------
            elif which == "bash":
                comment = [
                    ["#", None ],
                ]
                comment_object = self.comment(which)
                comment_object.set(comment)
                self.AST.append(comment_object)
            else:
                #"no known comment type"
                raise EParserError(1100)
    
    # -------------------------------------------------------------------
    # \brief class is used to mark a AST scope using comment type  ...
    # -------------------------------------------------------------------
    class comment:
        def __init__(self, argument=None):
            self.data   = []
            self.name   = "s"
            self.parent = ParserDSL
            
            # --------------------------
            # no argument given.
            # --------------------------
            if argument == None:
                DebugPrint("info: current scope without "
                + "comments initialized.")
            # --------------------------
            # argument type is a class
            # --------------------------
            elif argument == ParserDSL:
                self.parent = argument
                if self.parent.name != argument.name:
                    DebugPrint("info: current scope with: "
                    + argument.name
                    + " comments overwrite.")
                    self.parent.name = argument.name
                else:
                    DebugPrint("info: current scope not touched, because"
                    + " comments already initialized with: "
                    + argument.name
                    + ".")
            # --------------------------
            # argument type is a string
            # --------------------------
            elif type(argument) == str:
                supported_dsl = [
                    "dbase", "pascal", "c", "c++", "cpp", "cc",
                    "asm", "bash", "lisp"
                ]
                # --------------------------
                # dsl is in supported list:
                # --------------------------
                if argument in supported_dsl:
                    DebugPrint("info: current scope with: "
                    + argument
                    + " comments initialized.")
                    self.parent.name = argument
                # --------------------------
                # dsl not in supported list
                # --------------------------
                else:
                    DebugPrint("info: current scope with custom "
                    + "comments initialized.")
                    self.parent.name = argument
        
        # ---------------------------------------------------------------
        # \brief  add a comment type to the existing comment scope ...
        #
        # \param  name  - the name for the parser DSL
        # \param  kind  - a list with supported comment styles.
        #                 the format is: [ <start>, <end> ]; if None set
        #                 for <end>, then it is a one liner comment.
        # \return True  - if the kind list is append successfully to the
        #                 available data list.
        #         False - when other event was occured.
        # ---------------------------------------------------------------
        def add(self, name, kind):
            self.name = name
            self.data.append(kind)
            return True
        
        # ---------------------------------------------------------------
        # \brief set a new comment type to the existing comment scope ...
        #
        # \param name - the DSL parser language
        # \param kind - the comment styles that are available for <name>
        # ---------------------------------------------------------------
        def set(self, name, kind):
            self.name = name
            self.data = kind
            return True
        
        # ---------------------------------------------------------------
        # \brief  set the parser name for which the comments are ...
        #
        # \param  name - a string for parser name
        # \return True - boolean if successfully; else False
        # ---------------------------------------------------------------
        def set(self, name):
            self.name = name
            return True
        
        # ---------------------------------------------------------------
        # \brief  get the comment data list for the given comment scope.
        #
        # \param  nothing
        # \return data - the self.data list
        # ---------------------------------------------------------------
        def get(self):
            return self.data
        
        # ---------------------------------------------------------------
        # \brief  returns the name which comments stands for DSL name
        #
        # \param  nothing
        # \return string - the parser name
        # ---------------------------------------------------------------
        def getName(self):
            return self.name
    
    # -----------------------------------------------------------------------
    # \brief A class that act as record, to hold the informations about a
    #        decent parser...
    #
    # \field name     - a name for the parser
    # \field encoding - the source encoding of script file
    # -----------------------------------------------------------------------
    class parser_info:
        # -------------------------------------------------------------------
        # \brief __init__ is the initializator - maybe uneeded, because
        #        __new__  is the constructor ...
        # -------------------------------------------------------------------
        def __init__(self, name=None, encoding="utf-8"):
            self.name     = name
            self.encoding = encoding
        
        # -------------------------------------------------------------------
        # \brief this is the constructor of class "parser_info" ...
        # -------------------------------------------------------------------
        def __new__(self):
            return self
        
        def __enter__(self):
            return self
        
        # -------------------------------------------------------------------
        # \brief destructor for class "parser_info" ...
        # -------------------------------------------------------------------
        def __del__(self):
            self.name = ""
        
        # -------------------------------------------------------------------
        # setters for parser informations ...
        # -------------------------------------------------------------------
        def setName(self, name):
            self.name = name
        
        # -------------------------------------------------------------------
        # getters for parser informations ...
        # -------------------------------------------------------------------
        def getName(self):
            return self.name
    
    # -----------------------------------------------------------------------
    # \brief A class that act as record, to hold the statistically infos of a
    #        parse run...
    # \field time_start - time of start processing
    # \field time_end   - time of end   processing
    # -----------------------------------------------------------------------
    class parser_stat:
        # -------------------------------------------------------------------
        # \brief __init__ is the initializator - maybe uneeded, because
        #        __new__  is the constructor ...
        # -------------------------------------------------------------------
        def __init__(self):
            self.time_start = None
            self.time_end   = None
            self.encoding   = None
        
        # -------------------------------------------------------------------
        # \brief this is the constructor of class "parser_stat" ...
        # -------------------------------------------------------------------
        def __new__(self):
            return self
        
        def __enter__(self):
            return self
        
        # -------------------------------------------------------------------
        # \brief destructor for class "parser_stat" ...
        # -------------------------------------------------------------------
        def __del__(self):
            self.time_start = None
            self.time_end   = None
        
        # -------------------------------------------------------------------
        # setters for statistically informations ...
        # -------------------------------------------------------------------
        def setStart(self, time):
            self.time_start = time
        def setEnd(self, time):
            self.time_end   = time
        def setEncoding(self, encoding="utf-8"):
            self.encoding   = encoding
        
        # -------------------------------------------------------------------
        # getters for statistically informations ...
        # -------------------------------------------------------------------
        def getStart(self):
            return self.time_start
        def getEnd(self):
            return self.time_end
        def getEncoding(self):
            return self.encoding
    
    # -----------------------------------------------------------------------
    # \brief A class that act as record, to hold the script file data infos
    #        for used files...
    #
    # \field name    - the script name
    # \field size    - the size of the script in bytes
    # \field date    - the date of creation
    # \field datemod - the date of last modification
    # -----------------------------------------------------------------------
    class parser_file:
        # -------------------------------------------------------------------
        # \brief __init__ is the initializator - maybe uneeded, because
        #        __new__  is the constructor ...
        # -------------------------------------------------------------------
        def __init__(self, name):
            self.name    = name
            self.size    = 0
            self.date    = None
            self.datemod = None
        
        # -------------------------------------------------------------------
        # \brief this is the constructor of class "parser_file" ...
        # -------------------------------------------------------------------
        def __new__(self):
            return self
        
        def __enter__(self):
            return self
        
        # -------------------------------------------------------------------
        # \brief destructor for class "parser_file" ...
        # -------------------------------------------------------------------
        def __del__(self):
            self.name = None
    
    # -----------------------------------------------------------------------
    # \brief A class that act as record, to hold the data of a script file.
    #
    # \field name  - the script name
    # \field data  - the script data/source
    # \field lines - the lines of the script
    # -----------------------------------------------------------------------
    class parser_data:
        # -------------------------------------------------------------------
        # \brief __init__ is the initializator - maybe uneeded, because
        #        __new__  is the constructor ...
        # -------------------------------------------------------------------
        def __init__(self, name, data="", lines=0):
            self.name  = name
            self.data  = data
            self.lines = lines
        
        # -------------------------------------------------------------------
        # \brief this is the constructor of class "parser_data" ...
        # -------------------------------------------------------------------
        def __new__(self):
            return self
        
        def __enter__(self):
            return self
        
        # -------------------------------------------------------------------
        # \brief destructor for class "parser_data" ...
        # -------------------------------------------------------------------
        def __del__(self):
            self.name = None
        
        # -------------------------------------------------------------------
        # setters
        # -------------------------------------------------------------------
        def setLines(self, lines):
            self.lines = lines
        def setName(self, name):
            self.name  = name
        def setData(self, data):
            self.data  = data
        
        # -------------------------------------------------------------------
        # getters
        # -------------------------------------------------------------------
        def getLines(self):
            return self.lines
        def getName(self):
            return self.name
        def getData(self):
            return self.data

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
        self.owner = src
        self.start = start
        self.end   = end
        self.add(src)
    def add(self):
        self.owner.AST.append(self)
        return self

class dbase_command:
    def __init__(self, src, name, link=None):
        self.what  = "keyword"
        self.owner = src
        self.name  = name
        self.proc  = None
        self.prev  = None
        self.link  = link
    def add(self):
        self.owner.AST.append(self)
        return self

class dbase_TForm(QDialog):
    def __init__(self, parent=None):
        super(dbase_TForm, self).__init__(parent)
        self.setWindowTitle(_("Main Window"))
        self.setWindowFlags(
            Qt.Window or
            Qt.WindowMinimizeButtonHint or
            Qt.WindowMaximizeButtonHint)

    def readModal(self):
        self.exec_()

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
class interpreter_base():
    def __del__(self):
        print("destructor")
    
    def __init__(self, file_name):
        self.script_name = file_name
        genv.v__app__scriptname__ = file_name
        
        self.pos         = -1
        self.open_paren  =  0
        self.close_paren =  0
        
        # default, no error's at parse time ...
        genv.have_errors = False
        
        genv.open_paren = 0
        genv.text_paren = ""
        
        genv.code_code = """
import os
import sys
import time
import datetime

import builtins
print = builtins.print

"""
        genv.temp_code = ""
        genv.text_code = ""

        self.token_id    = ""
        self.token_prev  = ""
        self.token_str   = ""
        
        self.expr_is_empty = True
        
        self.token_macro_counter = 0
        self.token_comment_flag  = 0
        
        self.in_comment = 0
        
        self.dbase_parser      = 1
        self.pascal_parser     = 2
        self.java_parser       = 3
        self.isoc_parser       = 4
        self.prolog_parser     = 5
        self.lisp_parser       = 6
        self.javascript_parser = 7
        
        genv.counter_for    = 0
        genv.counter_indent = 1
        genv.counter_parens = 0
        
        genv.current_token  = ""
        
        genv.actual_parser = 0
        
        genv.open_pascal_comment_soft = 0
        genv.open_pascal_comment_hard = 0
        
        genv.v__app__logging.info("start parse: " + self.script_name)
        
        self.err_commentNC = _("comment not closed.")
        self.err_commandNF = _("command sequence not finished.")
        self.err_unknownCS = _("unknown command or syntax error.")
        
        self.current_state = "program"
        
        self.source    = ""

        self.parser_stop = False
        self.parse_open(self.script_name)
    
    def update_code(self, text):
        genv.text_code += text
        
        #if genv.isGuiApplication:
            #genv.text_code += (""
            #"\tpre_EntryPoint(True)\n"
            #)
    
    # -----------------------------------------------------------------------
    # \brief finalize checks and cleaning stuff ...
    # -----------------------------------------------------------------------
    def finalize(self):
        genv.v__app__logging.debug("macro   : " + str(self.token_macro_counter))
        genv.v__app__logging.debug("comment : " + str(self.token_comment_flag))
    
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
        with open(self.script_name, 'r', encoding="utf-8") as file:
            file.seek(0); self.source = file.read()
            file.close()
        DebugPrint("source: ", self.source)
    
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
    
    # -----------------------------------------------------------------------
    # \brief check the end of line, because windows and linux use differnt
    #        kind of endings. If there a '\r', and don't followed by a \n,
    #        then inform the user with a error message, if you under windows.
    #        #13#10 - Windows
    #        #10    - Linux
    # -----------------------------------------------------------------------
    def getChar(self):
        genv.line_col += 1
        self.pos += 1
        
        genv.have_errors = False
        genv.char_prev   = genv.char_curr
        
        if self.pos >= len(self.source):
            if genv.actual_parser == self.pascal_parser:
                if genv.open_pascal_comment_soft > 0 \
                or genv.open_pascal_comment_hard > 0 :
                    genv.have_errors = True
                    raise Exception(_("Error:\nno terminated comment found."))
                    
            raise Exception("no more data")
        else:
            genv.char_curr = self.source[self.pos]
            if genv.char_curr == '\n':
                genv.line_col  = 1
                genv.line_row += 1
                return True
                
            elif genv.char_curr == '\r':
                if self.pos >= len(self.source):
                    genv.have_errors = True
                    raise Exception(_("line ending error."))
                    
                self.pos += 1
                
                genv.char_prev = genv.char_curr
                genv.char_curr = self.source[self.pos]
                
                if genv.char_curr == '\n':
                    genv.line_col  = 1
                    genv.line_row += 1
                    
                    return True
                else:
                    genv.have_errors = True
                    raise Exception(_("Error:\nEnd Of Line error: ") + str(genv.line_row))
            else:
                return False
    
    def ungetChar(self, num):
        genv.line_col -= num
        self.pos -= num
        
        if genv.line_col < 1:  # check for \r\n
            genv.line_col = 1
            self.pos  += 1
            
        genv.char_prev = self.source[self.pos-1]
        genv.char_curr = self.source[self.pos]
        return genv.char_curr
    
    def check_token_white_spaces(self):
        if genv.char_curr == '\t' or genv.char_curr == ' ':
            return True
        elif genv.char_curr == '\n':
            genv.line_row += 1
            return True
        elif genv.char_curr == '\r':
            genv.line_row += 1
            self.getChar()
            if not genv.char_curr == '\n':
                genv.have_errors = True
                genv.unexpectedError(_("line error"))
                return False
            else:
                return True
        else:
            return False
    
    def check_token_alpha(self):
        if genv.char_curr.isalpha():
            return True
        return False
    
    def getIdent(self):
        self.token_str = genv.char_curr
        while True:
            genv.char_prev = genv.char_curr
            self.getChar()
            
            if genv.char_curr.isalnum():
                self.token_str += genv.char_curr
                continue
            else:
                self.ungetChar(1)
                #showInfo("===>>>> " + self.token_str)
                return True
                
        return False
    
    def getNumber(self):
        have_point = False
        self.token_str = ""
        while True:
            genv.char_prev = genv.char_curr
            self.getChar()
            
            if genv.char_curr.isdigit():
                self.token_str += genv.char_curr
                continue
                
            elif genv.char_curr == '.':
                if have_point == True:
                    genv.have_errors = True
                    raise Exception(_("Error:\ntoo many points."))
                else:
                    have_point = True
                    continue
            else:
                #self.ungetChar(1)
                return True
    
    def expect_ident(self, token=""):
        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
        if genv.char_curr.isalpha() or genv.char_curr == '_':
            self.getIdent()
            if len(token) > 0:
                if self.token_str.lower() == token.lower():
                    return True
                else:
                    self.ungetChar(len(token))
                    return False
            else:
                return False
        else:
            genv.unexpectedError(_("ident expected"))
            return False
    
    def expect_op(self):
        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
        if genv.char_curr in genv.parser_op:
            genv.temp_code += c
            return True
        else:
            self.ungetChar(1)
            return False
    
    def expect_expr(self):
        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
        if genv.char_curr.isdigit():
            self.token_str = genv.char_curr
            self.getNumber()
            #showInfo("token: " + self.token_str)
            genv.temp_code += self.token_str
            if self.expect_op():
                return self.expect_expr()
            else:
                return True
        elif genv.char_curr.isalpha() or genv.char_curr == '_':
            self.getIdent()
            genv.text_code += self.token_str
            return True
        elif self.expect_op():
            return self.expect_expr()
        elif genv.char_curr == '(':
            genv.text_code += '('
            return '('
        elif genv.char_curr == ')':
            self.ungetChar(1)
            return ')'
        else:
            return False
    
    def expect_assign(self):
        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
        if not genv.char_curr == '=':
            genv.unexpectedError(_("assign sign expected."))
            return '\0'
        return True
    
    def check_null(self, c):
        if self.pos >= len(self.source):
            showError("no more data.")
            return False
        if genv.char_curr == '\0':
            return True
        else:
            return False
    
    def check_white_spaces(self):
        while True:
            if genv.char_curr == '\n' \
            or genv.char_curr == '\t' \
            or genv.char_curr == ' ':
                return True
            else:
                #self.ungetChar(1)
                #showInfo("zzz>> " + genv.char_curr)
                return False
    
    def check_newline(self):
        if genv.char_curr == '\n':
            return True
        elif genv.char_curr == '\r':
            genv.char_prev = genv.char_curr
            self.getChar()
            
            if not genv.char_curr == '\n':
                raise Exception(_("Error:\nEnd of line error."))
            else:
                return True
    
    def check_char(self, c):
        if genv.char_curr == c:
            return True
        else:
            return False
            
    def check_number(self):
        genv.char_prev = genv.char_curr
        
        if genv.char_curr.isdigit():
            self.ungetChar(1)
            return self.getNumber()
            
        self.ungetChar(len(self.token_str))
        return False
        
    def check_alpha(self, ch):
        if ch.isalpha():
            return True
        else:
            #self.ungetChar(1)
            return False
    
    def check_ident(self):
        if genv.char_curr.isalpha():
            self.token_str = genv.char_curr
            self.getIdent()
            print("ident: " + self.token_str)
            return True
        else:
            print("checker: " + self.token_str + "\n> " + genv.char_curr)
            #self.ungetChar(1)
            return False
    
    def handle_pascal_comment_1(self):
        genv.open_pascal_comment_hard += 1
        while True:
            genv.char_prev = genv.char_curr
            self.getChar()
            
            if self.check_char('{'):
                genv.open_pascal_comment_hard += 1
                continue
                
            elif self.check_char('}'):
                genv.open_pascal_comment_hard -= 1
                
                if genv.open_pascal_comment_hard > 0:
                    continue
                else:
                    break
            else:
                continue
        return True
    
    def handle_pascal_comment_2(self):
        genv.char_prev = genv.char_curr
        self.getChar()
        
        if self.check_char('*'):
            genv.open_pascal_comment_soft += 1
            while True:
                genv.char_prev = genv.char_curr
                self.getChar()
                
                if self.check_char('*'):
                    genv.char_prev = genv.char_curr
                    self.getChar()
                    
                    if self.check_char(')'):
                        genv.open_pascal_comment_soft -= 1
                        return True
                    else:
                        continue
                else:
                    continue
        elif self.check_char(')'):
            print("==>> " + self.current_state)
            while True:
                if self.handle_pascal_white_spaces():
                    continue
                if genv.char_curr == ';':
                    print("semi ok")
                    break
                else:
                    raise Exception(_("SEmicolon expected."))
        elif genv.char_curr.isalpha():
            if self.check_ident():
                print("---> state: " + self.current_state)
                if self.current_state == "procedure":
                    self.current_state = "procedure_arg"
                    self.handle_pascal_argument()
                    #self.handle_pascal_procedure_name()
                elif self.current_state == "procedure_arg":
                    print("ARgument: " + self.token_str)
                    self.handle_pascal_argument()
            else:
                raise Exception(_("ident expected."))
        else:
            raise Exception(_("wrong char type."))
    
    def handle_pascal_argument(self):
        while True:
            if self.handle_pascal_white_spaces():
                continue
            if self.check_char(':'):
                print(":::::")
                while True:
                    if self.handle_pascal_white_spaces():
                        continue
                    if genv.char_curr.isalpha():
                        self.handle_pascal_argument_type()
                        
                        while True:
                            if self.handle_pascal_white_spaces():
                                continue
                            if self.check_char(')'):
                                print("list ende.")
                                self.handle_pascal_list_end()
                                break
                    else:
                        raise Exception(_("argument type expected."))
                    break
                break
            else:
                raise Exception(_("colon (:) expected."))
            break
            
    def handle_pascal_list_end(self):
        while True:
            genv.char_prev = genv.char_curr
            self.getChar()
            
            if self.check_white_spaces():
                continue
            elif self.check_char('{'):
                self.handle_pascal_comment_1()
                continue
            elif self.check_char('('):
                if self.current_state == "procedure" \
                or self.current_state == "function":
                    self.current_state = "procedure_arg"
                self.handle_pascal_comment_2() # todo: expr
                continue
            
            elif self.check_char(';'):
                print("procedure ende.")
                break
            else:
                raise Exception(_("semicolon (;) expected."))
    
    def handle_pascal_argument_type(self):
        #self.ungetChar(1)
        self.check_ident()
        print("argument type: " + self.token_str)
        
    # -----------------------------------------------------------------------
    # \brief skip all whitespaces. whitespaces are empty lines, lines with
    #        one or more spaces (0x20): " ", \t, "\n".
    # -----------------------------------------------------------------------
    def skip_white_spaces(self, parser_type):  # wöö
        genv.actual_parser = parser_type
        
        while True:
            genv.char_prev = genv.char_curr
            self.getChar()
            
            if self.check_white_spaces():
                continue
            
            elif self.check_char(';'):
                if parser_type == self.lisp_parser:
                    while True:
                        genv.char_prev = genv.char_curr
                        self.getChar()
                        
                        if self.check_newline():
                            break
                            
                        continue
                elif parser_type == self.pascal_parser:
                    return True
                else:
                    raise Exception("no supported parser.")
                        
            elif self.check_char(')'):
                genv.open_paren -= 1
                if genv.open_paren < 1:
                    genv.have_errors = True
                    raise Exception(_("paren underflow."))
                else:
                    continue
            
            elif self.check_char('}'):
                genv.open_pascal_comment_hard -= 1
                if genv.open_pascal_comment_hard < 1:
                    genv.have_errors = True
                    raise Exception(_("no comment start found."))
                else:
                    continue
                    
            elif self.check_char('{'):
                if parser_type == self.pascal_parser:
                    self.handle_pascal_comment_1()
                    continue
                else:
                    raise Exception(_("invalid character found."))
                    return
            
            elif self.check_char('/'):
                if parser_type == self.pascal_parser:
                    genv.char_prev = genv.char_curr
                    self.getChar()
                    
                    if self.check_char('/'):
                        while True:
                            genv.char_prev = genv.char_curr
                            self.getChar()
                            
                            if self.check_char('\n'):
                                break
                                
                            continue
                        continue
                    else:
                        raise Exception(_("C++ comment expected."))
                        
            elif self.check_char('('):
                genv.open_paren += 1
                if parser_type == self.pascal_parser:
                    self.handle_pascal_comment_2()
                    continue
                    
                elif parser_type == self.lisp_parser:
                    while True:
                        genv.char_prev = genv.char_curr
                        self.getChar()
                        
                        if self.check_white_spaces():
                            continue
                            
                        if self.check_number():
                            showInfo("lisp: " + self.token_str)
                            while True:
                                if self.check_char(')'):
                                    break
                                else:
                                    self.ungetChar(1)
                                    break
                        else:
                            showInfo("Ee: " + genv.char_curr)
                            break
                            
            elif self.check_ident():
                return True
                
            else:
                showError("token: " + self.token_str + "\n> " + genv.char_curr)
                return False
    
    def check_token_newline(self):
        if genv.char_curr == '\n':
            return True
        if genv.char_curr == '\r':
            genv.char_prev = genv.char_curr
            self.getChar()
            if not genv.char_curr == '\n':
                genv.have_errors = True
                genv.unexpectedError(_("invalide line end."))
                return False
            elif (genv.char_curr == '\n') or (genv.char_curr == '\t') or (genv.char_curr == ' '):
                return True
    
    # -----------------------------------------------------------------------
    # \brief parse a one line comment: // for c++, ** and && for dBase ...
    # -----------------------------------------------------------------------
    def handle_oneline_comment(self):
        while True:
            genv.line_col += 1
            self.getChar()
            if self.check_null(genv.char_curr):
                return '\0'
            if self.check_spaces(genv.char_curr):
                continue
            if self.check_newline(genv.char_curr):
                break
    
    def run(self):
        self.finalize()
        
        if genv.have_errors == True:
            showError(_("source code has errors."))
            return
        
        #genv.text_code += "\tcon.reset()\n"
        #genv.counter_indent -= 1
        return
        if genv.editor_check.isChecked():
            genv.text_code += ("\n\n"
            + "if __name__ == '__main__':\n"
            + "\tglobal console\n"
            + "\tconsole = DOSConsole()\n"
            + "\tpre_EntryPoint(True)\n"
            + "\tconsole.exec_()\n"
            )
        else:
            #genv.text_code = ("def pre_EntryPoint():\n" + genv.text_code)
            self.update_code("\n\n"
            + "if __name__ == '__main__':\n"
            + "\tglobal console\n"
            + "\tconsole = DOSConsole()\n"
            + "\tpre_EntryPoint()\n"
            + "\tconsole.exec_()\n"
            )
        
        #showInfo("runner:\n" + genv.text_code)
        
        #showInfo(genv.text_code)
        try:
            cachedir = genv.v__app__internal__ + "/__cache__"
            if not os.path.exists(cachedir):
                os.makedirs(cachedir)
            
            fname = os.path.basename(self.script_name)
            fname = os.path.splitext(fname)[0]
            fname = cachedir+"/"+fname+".bin"
            
            # ---------------------
            # compile text code ...
            # ---------------------
            bytecode = compile(
                genv.text_code,
                filename=fname,
                mode="exec")
                
            filename = fname
            
            # ---------------------
            # save binary code ...
            # ---------------------
            with open(filename,"wb") as bytefile:
                marshal.dump(bytecode , bytefile)
                bytefile.close()
            
            with open(filename,"rb") as bytefile:
                bytecode = marshal.load(bytefile)
                bytefile.close()
        
            # ---------------------
            # execute binary code:
            # ---------------------
            exec(bytecode, globals())
            
            # ---------------------
            # reset old code ...
            # ---------------------
            genv.class_code  = ""
            self.text_code   = ""
            genv.header_code = ""
        except Exception as e:
            genv.class_code  = ""
            self.text_code   = ""
            genv.header_code = ""
            showException(traceback.format_exc())

class interpreter_dBase(interpreter_base):
    def __init__(self, file_name):
        super(interpreter_dBase, self).__init__(file_name)
        
        # ----------------------------------------------
        # textual color values in RGB format ...
        # ----------------------------------------------
        self.token_colors = [
            [['n']         , '#000000' ], # black
            [['b']         , '#00008B' ], # dark blue
            [['g']         , '#006400' ], # green
            [['gb','bg']   , '#8B008B' ], # dark magenta
            [['r']         , '#8B0000' ], # dark red
            [['rb','br']   , '#FF00FF' ], # magenta
            [['rg','gr']   , '#A52A2A' ], # brown
            [['w']         , '#D3D3D3' ], # light gray
            [['n+']        , '#A9A9A9' ], # dark gray
            [['b+']        , '#0000FF' ], # blue
            [['g+']        , '#00FF00' ], # light green
            [['gb+','bg+'] , '#ADD8E6' ], # light blue
            [['r+']        , '#FF0000' ], # red
            [['rb+','br+'] , '#00FFFF' ], # magenta
            [['rg+','gr+'] , '#FFFF00' ], # yellow
            [['w+']        , '#FFFFFF' ]  # white
        ]
                
        self.fg_color  = "#FF0000"
        self.bg_color  = "#000000"
        
        genv.header_code = ""
        
        global textertext
        textertext = 'dBase DOS Shell Version 1.0.0\n(c) 2024 by Jens Kallup - paule32.'
        self.byte_code = ""
    
    def add_command(self, name, link):
        self.token_command = dbase_command(self, name, link)
        return self.token_command
    
    def handle_commands(self):
        if self.token_str.lower() == "date":
            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
            if genv.char_curr == '(':
                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                if genv.char_curr == ')':
                    genv.text_code += ('\t' * genv.counter_indent)
                    genv.text_code += ("console.win.gotoxy(" +
                    str(self.xpos) + ","   +
                    str(self.ypos) + ")\n" +
                    ('\t' * genv.counter_indent) + "console.win.print_date()\n")
                    
                    self.command_ok = True
                else:
                    genv.unexpectedChar(genv.char_curr)
            else:
                genv.unexpectedChar(genv.char_curr)
        elif self.token_str.lower() == "str":
            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
            if genv.char_curr == '(':
                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                if genv.char_curr == ')':
                    DebugPrint("strrr")
                    self.command_ok = True
                else:
                    genv.unexpectedChar(genv.char_curr)
            else:
                genv.unexpectedChar(genv.char_curr)
        else:
            genv.unexpectedToken(self.token_str)
    
    def handle_string(self, mode=0):
        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
        if genv.char_curr == '"':
            self.temp_code += '"'
            while True:
                genv.char_curr = self.getChar()
                if genv.char_curr == genv.ptNoMoreData:
                    return genv.char_curr
                elif genv.char_curr == '"':
                    self.temp_code += '"'
                    genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                    if genv.char_curr == '+':
                        self.temp_code += " + "
                        return self.handle_string()
                    else:
                        self.ungetChar(1)
                        return self.temp_code
                elif genv.char_curr == '\\':
                    genv.char_curr = self.getChar()
                    if genv.char_curr == "\n" or genv.char_curr == "\r":
                        genv.unexpectedEndOfLine(genv.line_row)
                    elif genv.char_curr == " ":
                        genv.unexpectedEscapeSign(genv.line_row)
                    elif genv.char_curr == '\\':
                        self.temp_code += "\\"
                    elif genv.char_curr == 't':
                        self.temp_code += "\t"
                    elif genv.char_curr == 'n':
                        self.temp_code += "\n"
                    elif genv.char_curr == 'r':
                        self.temp_code += "\r"
                    elif genv.char_curr == 'a':
                        self.temp_code += "\a"
                    else:
                        self.temp_code += genv.char_curr
                    continue
                else:
                    self.temp_code += genv.char_curr
                    continue
            return self.temp_code
    
    def handle_parens(self):
        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
        if genv.char_curr == '(':
            self.open_paren += 1
            genv.temp_code  += c
            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
            if genv.char_curr == genv.ptNoMoreData:
                genv.unexpectedError(_("no more data."))
            elif genv.char_curr == '(':
                self.ungetChar(1)
                self.handle_parens()
                return self.temp_code # todo !!!
            return self.get_brace_code()
        elif genv.char_curr == ')':
            genv.open_paren -= 1
            genv.temp_code  += genv.char_curr
            if genv.open_paren < 1:
                return genv.temp_code
        elif genv.char_curr in genv.parser_op:
            genv.temp_code += genv.char_curr
            return handle_parens()
        elif genv.char_curr.isdigit():
            self.token_str = genv.char_curr
            self.getNumber()
            genv.temp_code += self.token_str
            return self.get_brace_code()
        elif genv.char_curr.isalpha():
            self.token_str = genv.char_curr
            self.getIdent()
            genv.text_code += self.token_str
            return self.get_brace_code()
        elif genv.char_curr in genv.parser_op:
            genv.text_code += genv.char_curr
            return self.get_brace_code()
        elif genv.char_curr == ',':
            return genv.char_curr
        else:
            if genv.counter_brace > 0:
                raise unexpectedParserException(_("missing closed parens"), genv.line_row)
                return '\0'
        return False
    
    def handle_numalpha(self):
        while True:
            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
            if genv.char_curr.isdigit():
                self.token_str = genv.char_curr
                self.getNumber()
                genv.text_code += self.token_str
                continue
            elif genv.char_curr.isalpha() or genv.char_curr == '_':
                self.token_str = genv.char_curr
                self.getIdent()
                genv.text_code += self.token_str
                continue
            elif genv.char_curr in genv.parser_op:
                genv.text_code += genv.char_curr
                continue
            elif genv.char_curr == '(':
                genv.counter_brace += 1
                genv.text_code += genv.char_curr
                continue
            elif genv.char_curr == ')':
                genv.counter_brace -= 1
                if self.second_part:
                    return genv.char_curr
                continue
            elif genv.char_curr == ',':
                return genv.char_curr
        return '\0'
    
    def tokenString(self):
        self.token_str = ""
        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
        if genv.char_curr == '\"':
            genv.temp_code  = ('\t' * genv.counter_indent)
            genv.temp_code += 'console.win.print_line('
            genv.text_code += genv.temp_code
            genv.temp_code  = ""
            genv.last_command = False
            #
            self.ungetChar(1)
            self.handle_string()
            genv.text_code += ')\n'
            genv.last_command = True
            return True
        else:
            genv.unexpectedError(_("qoute expected"))
            return '\0'
    
    def handle_say(self):
        self.command_ok  = False
        self.second_part = False
        #
        self.temp_code   = ""
        self.text_paren  = ""
        #
        self.prev_sign   = False
        self.prev_expr   = False
        #
        while True:
            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
            if genv.char_curr.isdigit():
                self.token_str = genv.char_curr
                self.getNumber()
                genv.text_code += ('\t' * genv.counter_indent)
                genv.text_code += "console.win.gotoxy("
                genv.text_code += self.token_str
                #
                #showInfo("digit:\n" + genv.text_code)
                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                if genv.char_curr == ',':
                    genv.text_code += ","
                    genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                    if genv.char_curr.isdigit():
                        self.token_str = c
                        self.getNumber()
                        genv.text_code += self.token_str
                        genv.text_code += ")\n"
                        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                        if genv.char_curr.isalpha() or genv.char_curr == '_':
                            self.token_str = genv.char_curr
                            self.getIdent()
                            if self.token_str.lower() == "say":
                                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                if genv.char_curr == '"':
                                    self.ungetChar(1)
                                    self.token_str  = ('\t' * genv.counter_indent)
                                    self.token_str += "console.win.print_line("
                                    self.token_str += self.handle_string()
                                    self.token_str += ")\n"
                                    genv.text_code += self.token_str
                                    #showInfo("nachricht:\n\n" + genv.text_code)
                                return
                            elif self.token_str.lower() == "get":
                                #showInfo("getter")
                                return
                    else:
                        genv.unexpectedError(_(" l l k k k "))
                #
                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                if genv.char_curr in['-','+','*','/']:
                    self.temp_code += c
                    self.prev_sign = True
                    continue
                elif genv.char_curr == ',':
                    genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                    if c.isdigit():
                        self.token_str = c
                        self.getNumber()
                        genv.temp_code += "," + self.token_str + ")\n"
                        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                        if genv.char_curr.isalpha():
                            self.token_str = c
                            self.getIdent()
                            if self.token_str == "say":
                                genv.text_code += ('\t' * genv.counter_indent)
                                genv.text_code += "console.win.print("
                                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                if genv.char_curr == '"':
                                    self.ungetChar(1)
                                    self.token_str  = self.handle_string()
                                    genv.text_code += self.token_str
                                    genv.text_code += "\n"
                                    #showInfo("nachricht 22:\n\n" + genv.text_code)
                                    break
                            if self.token_str == "get":
                                showInfo("get not implemented")
                                break
                        else:
                            genv.unexpectedError(_("say or get expected"))
                    else:
                        genv.unexpectedError(_("prev comma"))
                else:
                    genv.unexpectedError(_("unexpected character found."))
            elif genv.char_curr.isalpha() or genv.char_curr == '_':
                #showInfo("a identerig")
                self.token_str = genv.char_curr
                self.getIdent()
                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                if c in['-','+','*','/']:
                    #showInfo("alpaha")
                    self.temp_code += genv.char_curr
                    self.prev_sign = True
                    continue
                elif genv.char_curr == ',':
                    if self.prev_expr:
                        genv.unexpectedError(_("comma prevv"))
                    self.prev_expr = True
                    continue
                else:
                    genv.unexpectedError(_("unexpected character found 2."))
            elif genv.char_curr == '(':
                genv.open_paren += 1
                genv.temp_code += '('
                continue
            elif genv.char_curr == ')':
                genv.open_paren -= 1
                if genv.open_paren < 1:
                    genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                    if genv.char_curr in['-','+','*','/']:
                        continue
                    elif genv.char_curr.isalpha() or genv.char_curr == '_':
                        self.token_str = genv.char_curr
                        self.getIdent()
                        if self.token_str.lower() == "say":
                            #showInfo("saaayyyyer 111")
                            break
                        elif self.token_str.lower() == "get":
                            #showInfo("getter")
                            break
                    elif genv.char_curr.isdigit():
                        self.token_str = genv.char_curr
                        self.getNumber()
                        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                        if genv.char_curr in['-','+','*','/']:
                            self.temp_code += genv.char_curr
                            self.prev_sign = True
                            continue
                        elif genv.char_curr == ',':
                            if self.prev_expr:
                                genv.unexpectedError(_("comma prevv"))
                            self.prev_expr = True
                            continue
                        else:
                            genv.unexpectedError(_("loliutz"))
                else:
                    continue
            elif genv.char_curr == ',':
                #showInfo("mupslochj")
                if self.prev_expr:
                    genv.unexpectedError(_("comma prevv 22"))
                self.prev_sign = True
                continue
            else:
                genv.unexpectedError(_("say command not okay."))
                return '\0'
    
    # -----------------------------------------------
    # CLASS ident OF FORM ... ENDCLASS
    # -----------------------------------------------
    def handle_class_commands(self):
        #showInfo("commando: " + str(self.pos));
        pass
    
    def handle_class(self):
        try:
            while True:
                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                if genv.char_curr == genv.ptNoMoreData:
                    raise e_no_more_data()
                if genv.char_curr.isalpha():
                    self.token_str = genv.char_curr
                    self.getIdent()
                    if self.token_str.lower() == "class":
                        genv.class_code += "class ";
                        self.token_str = ""
                        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                        if genv.char_curr == genv.ptNoMoreData:
                            raise e_no_more_data()
                        if genv.char_curr.isalpha():
                            self.token_str = genv.char_curr
                            self.getIdent()
                            ClassName = self.token_str
                            genv.class_code += self.token_str + "("
                            # class ClassName(
                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                            if genv.char_curr == genv.ptNoMoreData:
                                raise e_no_more_data()
                            elif genv.char_curr.isalpha():
                                self.token_str = genv.char_curr
                                self.getIdent()
                                if self.token_str.lower() == "of":
                                    genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                    if genv.char_curr == genv.ptNoMoreData:
                                        raise e_no_more_data()
                                    elif genv.char_curr.isalpha():
                                        self.token_str = genv.char_curr
                                        self.getIdent()
                                        if self.token_str.lower() == "container":
                                            genv.class_code += (""
                                            + "dbase_TContainer):\n"
                                            + ('\t' * genv.counter_indent)
                                            + "def __init__(self, parent=None):\n"
                                            + "\t\tsuper(" + ClassName + ", self).__init__(parent)\n"
                                            + "\t\tself.setText('My Container')\n"
                                            + "\t\tself.ClassName = '" + ClassName + "'\n"
                                            + "\t\tself.ClassType = 'CONTAINER'\n")
                                            genv.counter_indent += 1
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if not genv.char_curr == '(':
                                                genv.have_errors = True
                                                genv.unexpectedChar(genv.char_curr)
                                                return
                                            #showInfo("oooooooooooooooooo")
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if not genv.char_curr == ')':
                                                genv.have_errors = True
                                                genv.unexpectedChar(genv.char_curr)
                                                return
                                            elif genv.char_curr.isalpha():
                                                self.token_str = genv.char_curr
                                                self.getIdent()
                                                showInfo(self.token_str)
                                            showInfo("KLASSE:\n" + genv.class_code)
                                        elif self.token_str.lower() == "grid":
                                            genv.class_code += (""
                                            + "dbase_TPushButton):\n"
                                            + ('\t' * genv.counter_indent)
                                            + "def __init__(self, parent=None):\n"
                                            + "\t\tsuper(" + ClassName + ", self).__init__(parent)\n"
                                            + "\t\tself.setText('My Grid')\n"
                                            + "\t\tself.ClassName = '" + ClassName + "'\n"
                                            + "\t\tself.ClassType = 'GRID'\n")
                                            genv.counter_indent += 1
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if not genv.char_curr == '(':
                                                genv.have_errors = True
                                                genv.unexpectedChar(genv.char_curr)
                                                return
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if not genv.char_curr == ')':
                                                genv.have_errors = True
                                                genv.unexpectedChar(genv.char_curr)
                                                return
                                            showInfo("KLASSE:\n" + genv.class_code)
                                        elif self.token_str.lower() == "pushbutton":
                                            genv.class_code += (""
                                            + "dbase_TPushButton):\n"
                                            + ('\t' * genv.counter_indent)
                                            + "def __init__(self, parent=None):\n"
                                            + "\t\tsuper(" + ClassName + ", self).__init__(parent)\n"
                                            + "\t\tself.setText('My Button')\n"
                                            + "\t\tself.ClassName = '" + ClassName + "'\n"
                                            + "\t\tself.ClassType = 'PUSHBUTTON'\n")
                                            genv.counter_indent += 1
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if not genv.char_curr == '(':
                                                genv.have_errors = True
                                                genv.unexpectedChar(genv.char_curr)
                                                return
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if not genv.char_curr == ')':
                                                genv.have_errors = True
                                                genv.unexpectedChar(genv.char_curr)
                                                return
                                            showInfo("KLASSE:\n" + genv.class_code)
                                        elif self.token_str.lower() == "memo":
                                            genv.class_code += (""
                                            + "dbase_TMemo):\n"
                                            + ('\t' * genv.counter_indent)
                                            + "def __init__(self, parent=None):\n"
                                            + "\t\tsuper(" + ClassName + ", self).__init__(parent)\n"
                                            + "\t\tself.setText('My Button')\n"
                                            + "\t\tself.ClassName = '" + ClassName + "'\n"
                                            + "\t\tself.ClassType = 'MEMO'\n")
                                            genv.counter_indent += 1
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if not genv.char_curr == '(':
                                                genv.have_errors = True
                                                genv.unexpectedChar(genv.char_curr)
                                                return
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if not genv.char_curr == ')':
                                                genv.have_errors = True
                                                genv.unexpectedChar(genv.char_curr)
                                                return
                                            showInfo("KLASSE:\n" + genv.class_code)
                                        elif self.token_str.lower() == "text":
                                            genv.class_code += (""
                                            + "dbase_TLabelText):\n"
                                            + ('\t' * genv.counter_indent)
                                            + "def __init__(self, parent=None):\n"
                                            + "\t\tsuper(" + ClassName + ", self).__init__(parent)\n"
                                            + "\t\tself.setText('My Text')\n"
                                            + "\t\tself.ClassName = '" + ClassName + "'\n"
                                            + "\t\tself.ClassType = 'TEXT'\n")
                                            genv.counter_indent += 1
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if not genv.char_curr == '(':
                                                genv.have_errors = True
                                                genv.unexpectedChar(genv.char_curr)
                                                return
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if not genv.char_curr == ')':
                                                genv.have_errors = True
                                                genv.unexpectedChar(genv.char_curr)
                                                return
                                            showInfo("KLASSE:\n" + genv.class_code)
                                        elif self.token_str.lower() == "editfield":
                                            genv.class_code += (""
                                            + "dbase_TEditField):\n"
                                            + ('\t' * genv.counter_indent)
                                            + "def __init__(self, parent=None):\n"
                                            + "\t\tsuper(" + ClassName + ", self).__init__(parent)\n"
                                            + "\t\tself.setText('My EditField')\n"
                                            + "\t\tself.ClassName = '" + ClassName + "'\n"
                                            + "\t\tself.ClassType = 'EDITFIELD'\n")
                                            genv.counter_indent += 1
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if not genv.char_curr == '(':
                                                genv.have_errors = True
                                                genv.unexpectedChar(genv.char_curr)
                                                return
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if not genv.char_curr == ')':
                                                genv.have_errors = True
                                                genv.unexpectedChar(genv.char_curr)
                                                return
                                            showInfo("KLASSE:\n" + genv.class_code)
                                        elif self.token_str.lower() == "form":
                                            genv.class_code += (""
                                            + "dbase_TForm):\n"
                                            + ('\t' * genv.counter_indent)
                                            + "def __init__(self, parent=None):\n"
                                            + "\t\tsuper(" + ClassName + ", self).__init__(parent)\n"
                                            + "\t\tself.setWindowTitle('Main Dialog')\n"
                                            + "\t\tself.ClassName = '" + ClassName + "'\n"
                                            + "\t\tself.ClassType = 'FORM'\n")
                                            genv.counter_indent += 1
                                            #showInfo("KLASSE:\n" + genv.class_code)
                                            self.handle_class_commands()
                                    
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if genv.char_curr == genv.ptNoMoreData:
                                                raise e_no_more_data(_("endclass expected"))
                                            if genv.char_curr.isalpha():
                                                self.token_str = genv.char_curr
                                                self.getIdent()
                                                if self.token_str.lower() == "endclass":
                                                    raise e_no_more_data("classend") # + genv.temp_code)
                                                else:
                                                    genv.have_errors = True
                                                    genv.unexpectedError(_("endclass expected."))
                                            else:
                                                genv.have_errors = True
                                                genv.unexpectedError(_("alpha value expected"))
                                                return
                                        else:
                                            genv.have_errors = True
                                            genv.unexpectedError(_("OF expected"))
                                            return
                                    else:
                                        genv.have_errors = True
                                        genv.unexpectedError(_("alpha value expected"))
                                        return
                                else:
                                    genv.have_errors = True
                                    genv.unexpectedError(_("form expected."))
                                    return
                            else:
                                genv.have_errors = True
                                genv.unexpectedError(_("alpha value expected"))
                                return
                        else:
                            genv.have_errors = True
                            genv.unexpectedError(_("OF expected."))
                            return
                    else:
                        genv.have_errors = True
                        genv.unexpectedError(_("alpha value expected"))
                        return
                else:
                    genv.have_errors = True
                    genv.unexpectedError(_("alpha value expected"))
                    return
        except e_no_more_data as noerror:
            #showInfo(f"dBase class information:\n{noerror.message}")
            if noerror.message == "classend":
                genv.header_code += "\n\n"
                self.update_code(genv.header_code)
                self.update_code(genv.class_code)
                
                # delete first line:
                lines = genv.text_code.splitlines()
                rline = lines[1:]
                lines = "\n".join(rline)
                
                genv.text_code = lines
                
                #showInfo("braker:\n" + genv.text_code)
    
    def handle_scoped_commands(self):
        self.ident = ""
        while True:
            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
            showInfo('----> ' + str(genv.char_curr))
            return
            if genv.char_curr == genv.ptNoMoreData:
                return genv.char_curr
            elif genv.char_curr == '\n':
                continue
            elif genv.char_curr.isalpha() or genv.char_curr == '_':
                self.getIdent(genv.char_curr)
                if self.token_str.lower() == "class":
                    #showInfo("---------class------")
                    genv.class_code += "class "
                    self.handle_class()
                    return
                    
                elif self.token_str.lower() == "set":
                    #showInfo("token:  " + self.token_str)
                    self.token_str = ""
                    genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                    if genv.char_curr.isalpha() or genv.char_curr == '_':
                        self.token_str = genv.char_curr
                        self.getIdent(genv.char_curr)
                        #showInfo("22 token:  " + self.token_str)
                        if self.token_str.lower() == "color":
                            self.token_str = ""
                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                            if genv.char_curr.isalpha() or genv.char_curr == '_':
                                self.token_str = genv.char_curr
                                self.getIdent(genv.char_curr)
                                #showInfo("33 token:  " + self.token_str)
                                if self.token_str.lower() == "to":
                                    #showInfo("TTOOOOO")
                                    # ------------------------------------
                                    # fg / bg color: 1 / 2
                                    # ------------------------------------
                                    genv.char_curr = self.check_color_token(1)
                                    if genv.char_curr == 1000:
                                        genv.text_code += ('\t' * genv.counter_indent)
                                        genv.text_code += (
                                        f"console.win.setcolor('{self.fg_color}','{self.bg_color}')\n")
                                        #showInfo("connnnn:  " + genv.text_code)
                                        continue
                                    else:
                                        #showInfo('121212-------')
                                        break
                                        #sys.exit(1)
                                else:
                                    genv.unexpectedError(_("TO expected"))
                                    return '\0'
                            else:
                                genv.unexpectedError(_("TO expected"))
                                return '\0'
                        else:
                            genv.unexpectedToken(_("COLOR expected"))
                            return '\0'
                elif self.token_str.lower() == "for":
                    #showInfo("foooor")
                    genv.counter_for += 1
                    if not self.expect_ident():
                        genv.unexpectedError(_("expected ident."))
                    self.ident = self.token_str
                    self.temp_code = self.token_str
                    self.text_code += ("\t" * genv.counter_indent)
                    self.text_code += self.token_str
                    if not self.expect_assign():
                        genv.unexpectedError(_("assign sign expected."))
                    self.text_code += self.token_str
                    self.text_code += "_cnt = range("
                    if not self.expect_expr():
                        genv.unexpectedError(_("expr expected."))
                    self.text_code += self.temp_code
                    if not self.expect_ident("to"):
                        genv.unexpectedError(_("expect TO"))
                    self.text_code += ", "
                    if not self.expect_expr():
                        genv.unexpectedError(_("expr2 expected."))
                    self.text_code += self.temp_code
                    self.text_code += ")\n"
                    self.text_code += ('\t' * genv.counter_indent)
                    self.text_code += "for "
                    self.text_code += self.ident
                    self.text_code += " in "
                    self.text_code += self.ident + "_cnt:\n"
                    continue
                elif self.token_str.lower() == "next":
                    genv.counter_for -= 1
                    continue
                else:
                    str_closed = False
                    genv.temp_code  = ('\t' * genv.counter_indent)
                    genv.temp_code += self.token_str
                    #
                    self.token_str = ""
                    #
                    genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                    if genv.char_curr == genv.ptNoMoreData:
                        #showInfo(_("temp code"))
                        #showInfo(genv.class_code)
                        raise e_no_more_data("temp code")
                    if genv.char_curr == '=':
                        genv.temp_code += " = "
                        genv.text_code += genv.temp_code
                        genv.temp_code = ""
                        #showInfo(genv.text_code)
                        while True:
                            genv.char_curr = self.getChar()
                            if genv.char_curr == '\n':
                                break
                            elif genv.char_curr in genv.ascii_charset:
                                self.token_str += genv.char_curr
                                continue
                            #else:
                            #    break
                        genv.text_code += self.token_str
                        genv.text_code += '\n'
                        #showInfo("variable:  " + self.token_str)
                        #showInfo(genv.text_code)
                    elif genv.char_curr == '(':
                        # todo: callee
                        #showInfo("todo callee")
                        pass
                    elif genv.char_curr.isalpha():
                        self.token_str = genv.char_curr
                        self.getIdent(genv.char_curr)
                        #showInfo('oo\n' + self.token_str)
                    else:
                        genv.unexpectedError(_("variable can not assign."))
                        return '\0'
            elif genv.char_curr == '@':
                #showInfo('sayer')
                self.handle_say()
                #showInfo("next sayer")
                continue
            elif genv.char_curr == '?':
                genv.text_code += ('\t' * genv.counter_indent)
                genv.text_code += "console.win.print_line("
                genv.last_command = False
                #
                self.token_str = ""
                #
                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                if genv.char_curr == '[':
                    genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                    if genv.char_curr == '\"' or genv.char_curr == '\'':
                        self.ungetChar(1)
                        self.handle_string()
                        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                        if not genv.char_curr == ']':
                            genv.unexpectedError(_("] expected."))
                        else:
                            break
                        #showInfo("STRING: ", self.token_str)
                    else:
                        genv.unexpectedError(self.err_unknownCS)
                        return '\0'
                elif (genv.char_curr == '\"') or (genv.char_curr == '\''):
                    self.ungetChar(1)
                    self.handle_string(0)
            else:
                genv.unexpectedChar(genv.char_curr)
        return
    
    def parse(self):
        try:
            genv.counter_digits = 0
            genv.counter_indent = 1
            genv.counter_for    = 0
            genv.counter_brace  = 0
            
            genv.first_part  = False
            genv.second_part = False
            
            genv.line_row  = 1
            genv.line_col  = 1
            
            self.token_str = ""
                        
            if len(self.source) < 1:
                genv.unexpectedError(_("no data available."))
                return
            
            # ------------------------------------
            # dbase plus ?
            # ------------------------------------
            if not genv.editor_check.isChecked():
                self.handle_scoped_commands()
                return
            return
            if genv.editor_check.isChecked():
                content = self.source
                pattern = re.compile(r"\*\* END HEADER.*?\n(.*?)\n*[cC][lL][aA][sS][sS]", re.DOTALL)
                plus_code = self.source
                line_code = plus_code.splitlines()
                
                for i, line in enumerate(line_code):
                    if '**' in line:
                        genv.start_idx = i + 1
                    if "class" in line.lower():
                        genv.end_idx = i + 1
                        break
                match = pattern.search(plus_code)
                if not match:
                    try:
                        genv.editor_check.setChecked(False)
                        self.handle_scoped_commands()
                        return
                    except:
                        showError("nor header")
                        return
                    
                    raise ENoSourceHeader("Header not found.")
                    return
                
                # ------------------------------------
                # handle class header ...
                # ------------------------------------
                genv.line_col = 1
                genv.line_row = genv.start_idx
                
                self.pos      = -1
                
                genv.header_code = match.group(1).strip()
                self.source = genv.header_code
                
                if len(self.source) < 1:
                    showInfo(_("source have no header"))
                    return
                
                genv.isGuiApplication = True
                #showInfo(self.source)
                self.handle_dbase_header(self.source)
                
                # ------------------------------------
                # handle class ...
                # ------------------------------------
                genv.line_col = 1
                genv.line_row = genv.end_idx
                
                self.pos   = -1
                
                class_code = content
                class_text = re.sub(r"\*\* END HEADER.*?\n.*?\bCLASS\b",
                    "CLASS",
                    content,
                    flags = re.DOTALL or re.IGNORECASE)
                pattern   = re.compile(r"(CLASS.*ENDCLASS)",
                            re.DOTALL or re.IGNORECASE)
                match = pattern.search(class_text)
                if match:
                    class_text  = match.group(1).strip()
                    self.source = class_text
                    #showInfo(self.source)
                    self.handle_dbase_class(self.source)
                    return
                else:
                    showInfo(_("no class found"))
                    return
                    
        except noDataNoError:
            #showInfo("nachricht:\n\n" + self.temp_code)
            if not genv.last_command:
                genv.text_code += ")\n"
                genv.last_command = True
            #if len(genv.text_paren) > 0:
            #genv.text_code += genv.text_paren + "\n"
            genv.text_paren = ""
            #showInfo(genv.text_code)
            pass
        except e_expr_error as err:
            genv.have_errors = True
            genv.code_error  =   err.code
            genv.unexpectedError(err.message)
            return
        except e_expr_empty as err:
            genv.have_errors = True
            genv.unexpectedError(err.message)
            return
        except Exception as e:
            showError(f"Error: --> {e}")
            #showException(traceback.format_exc())
    
    def handle_dbase_class(self, code):
        self.source = code
        self.handle_class();
    
    # ----------------------------------------------------
    # \brief  dbase_expr handle a dBase expression.
    # \param  nothing
    # \return expr
    # ----------------------------------------------------
    def dbase_expr(self):
        while True:
            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
            if genv.char_curr == genv.ptNoMoreData:
                genv.have_errors = True
                raise e_expr_error(
                    message=_("syntax error."),
                    line=genv.line_row,
                    code=genv.DBASE_EXPR_SYNTAX_ERROR
                    )
            elif genv.char_curr == '(':
                genv.text_code += genv.char_curr
                continue
            elif genv.char_curr == ')':
                genv.text_code += '):'
                break
            elif genv.char_curr.isnumeric():
                self.token_str = genv.char_curr
                self.getNumber()
                genv.text_code += self.token_str
                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                if genv.char_curr in['-','+','*','/']:
                    genv.text_code += c
                    genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                    if genv.char_curr == genv.ptNoMoreData:
                        genv.have_errors = True
                        raise e_expr_error(
                            message=_("data out."),
                            line=genv.line.row,
                            code=genv.DBASE_EXPR_SYNTAX_ERROR
                            )
                        return 0
                    genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                    if genv.char_curr == '(':
                        genv.text_code += genv.char_curr
                        continue
                    elif genv.char_curr.isnumeric():
                        self.token_str = genv.char_curr
                        self.getNumber()
                        genv.text_code += self.token_str
                        continue
                    elif genv.char_curr.isalpha() or genv.char_curr == '_':
                        self.token_str = genv.char_curr
                        self.getIdent(genv.char_curr)
                        if self.token_str.lower() in genv.dbase_keywords:
                            genv.have_errors = True
                            raise e_expr_error(
                                message=_("keywords not allowed there."),
                                line=genv.line_row,
                                code=genv.DBASE_EXPR_KEYWORD_ERROR
                                )
                            return 0
                        genv.text_code += self.token_str
                        continue
                    else:
                        genv.have_errors = True
                        raise e_expr_error(
                            message=_("numeric or alpha expected."),
                            line=genv.line_row,
                            code=genv.DBASE_EXPR_SYNTAX_ERROR
                            )
                        return 0
                elif genv.char_curr == ')':
                    genv.text_code += c
                    continue
            elif genv.char_curr.isalpha() or genv.char_curr == '_':
                self.token_str = genv.char_curr
                self.getIdent(genv.char_curr)
                if self.token_str.lower() in genv.dbase_keywords:
                    genv.have_errors = True
                    raise e_expr_error(
                        message=_("keywords not allowed there."),
                        line=genv.line_row,
                        code=genv.DBASE_EXPR_KEYWORD_ERROR
                        )
                    return
                genv.text_code += self.token_str
                continue
            else:
                genv.have_errors = True
                raise e_expr_error(
                    message=_("if syntax error."),
                    line=genv.line_row
                    )
                return 0
    
    def handle_dbase_header(self, code):
        self.source = code
        try:
            while True:
                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                if genv.char_curr == genv.ptNoMoreData:
                    raise e_no_more_data();
                    return
                elif genv.char_curr.isalpha():
                    self.getIdent(genv.char_curr)
                    if self.token_str.lower() == "parameter":
                        self.temp_code = ""
                        while True:
                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                            if genv.char_curr == genv.ptNoMoreData:
                                raise e_no_more_data();
                            elif genv.char_curr.isalpha():
                                self.getIdent(genv.char_curr)
                                if self.token_str.lower() in genv.dbase_keywords:
                                    genv.have_errors = True
                                    genv.unexpectedError(_("keywords can not be used as variable"))
                                    return
                                genv.temp_code += self.token_str
                                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                if genv.char_curr == genv.ptNoMoreData:
                                    raise e_no_more_data();
                                elif genv.char_curr == ',':
                                    genv.temp_code += ","
                                    continue
                                else:
                                    self.ungetChar(1)
                                    genv.temp_code += "):\n"
                                    break
                        
                        genv.text_code = "def pre_EntryPoint(" + genv.temp_code
                        genv.temp_code = ""
                        
                        #showInfo("texter;\n" + genv.text_code)
                        #genv.text_code += "\n"
                        
                        #genv.text_code +=
                        
                        continue
                    elif self.token_str.lower() == "local":
                        showInfo("lokaler " + self.token_str + "\n>" + str(genv.char_curr))
                        genv.text_code += ('\t' * genv.counter_indent)
                        while True:
                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                            if genv.char_curr == genv.ptNoMoreData:
                                raise e_no_more_data();
                            if genv.char_curr.isalpha():
                                self.getIdent(genv.char_curr)
                                if self.token_str.lower() in genv.dbase_keywords:
                                    genv.have_errors = True
                                    genv.unexpectedError(_("keywords can not be used as variable"))
                                    return
                                genv.text_code += self.token_str
                                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                if genv.char_curr == genv.ptNoMoreData:
                                    raise e_no_more_data();
                                elif genv.char_curr == ',':
                                    genv.text_code += ","
                                    continue
                                else:
                                    self.ungetChar(1)
                                    genv.text_code += " = None\n"
                                    break
                        showInfo("local:\n" + genv.text_code)
                        #showInfo("parss: "  + self.token_str + "\n>" + str(genv.char_curr))
                        continue
                    elif self.token_str.lower() == "if":
                        genv.text_code += "if "
                        self.dbase_expr()
                        
                        genv.text_code += '\n'
                        
                        showInfo("if: ------\n" + genv.text_code)
                    elif self.token_str.lower() == "else":
                        genv.text_code += "\relse:\r\t"
                        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                        if genv.char_curr == genv.ptNoMoreData:
                            raise e_no_more_data()
                        elif genv.char_curr.isalpha():
                            self.getIdent(genv.char_curr)
                            genv.text_code += ('\t' * genv.counter_indent)
                            genv.text_code += self.token_str
                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                            if genv.char_curr == genv.ptNoMoreData:
                                raise e_no_more_data();
                            elif genv.char_curr == '.':
                                genv.text_code += "."
                                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                if genv.char_curr == genv.ptNoMoreData:
                                    raise e_no_more_data();
                                if genv.char_curr.isalpha():
                                    self.getIdent(genv.char_curr)
                                    if self.token_str.lower() == "open":
                                        genv.text_code += "open"
                                        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                        if genv.char_curr == genv.ptNoMoreData:
                                            raise e_no_more_data();
                                        elif genv.char_curr == '(':
                                            genv.text_code += "("
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if genv.char_curr == genv.ptNoMoreData:
                                                raise e_no_more_data();
                                            elif genv.char_curr == ')':
                                                genv.text_code += ")"
                                                #showInfo("else:\n" + genv.header_code)
                                                continue
                                            else:
                                                genv.have_errors = True
                                                genv.unexpectedError(_("closed paren expected."))
                                                return
                                        else:
                                            genv.have_errors = True
                                            genv.unexpectedError(_("open paren expected."))
                                            return
                                    else:
                                        genv.have_errors = True
                                        genv.unexpectedError(_("open expected."))
                                        return
                                else:
                                    genv.have_errors = True
                                    genv.unexpectedError(_("unexpected character fund."))
                                    return
                            elif genv.char_curr == '(':
                                showInfo("not implemented paren")
                                genv.have_errors = True
                                genv.unexpectedError(_("not implemented."))
                                return
                    elif self.token_str.lower() == "endif":
                        genv.counter_endif += 1
                        showInfo("IF:  " + str(genv.counter_if) + "\nBB: " + str(genv.counter_endif))
                        if not (genv.counter_if == genv.counter_endif):
                            genv.have_errors = True
                            genv.unexpectedError(_("closed paren overflow."))
                            return 0
                        continue
                    else:
                        genv.text_code += ('\t' * genv.counter_indent)
                        showInfo("--->>>\n" + self.token_str)
                        genv.text_code += self.token_str
                        showInfo("VV\n" + genv.text_code)
                        
                        self.check_point()
                        self.check_token_ident(genv.char_curr)
                        self.check_token_expr(["readmodal","open"])
                        if b == False:
                            genv.have_errors = True
                            genv.unexpectedError(_("readmodal or open expected."))
                            return False
                                
                            showInfo("zzzzzz\n" + genv.text_code)
                                
                            #    else:
                            #        #genv.text_code += self.token_str
                            #        #genv.text_code += current_ident
                            #        showInfo("ooo>>\n" + genv.text_code)
                            #        c = self.skip_white_spaces(self.dbase_parser)
                            #        if c == genv.ptNoMoreData:
                            #            genv.have_errors = True
                            #            raise e_no_more_data()
                            #            return
                            #        elif c == '(':
                            #            genv.text_code += '('
                            #            c = self.skip_white_spaces(self.dbase_parser)
                            #            if c == genv.ptNoMoreData:
                            #                genv.have_errors = True
                            #                genv.unexpectedError(_("open paren expected."))
                            #                return
                            #            elif c == ')':
                            #                genv.text_code += ')'
                            #                continue
                            #            else:
                            #                genv.have_errors = True
                            #                genv.unexpectedError(_("unknow character found."))
                            #                return
                            #        elif c == '=':
                            #            showInfo("equaallllll")
                            #            genv.text_code += " = "
                            #            c = self.skip_white_spaces(self.dbase_parser)
                            #            if c == genv.ptNoMoreData:
                            #                genv.have_errors = True
                            #                raise e_no_more_data()
                            #            elif c == '.':
                            #                boolval = 'f'
                            #                c = self.getChar()
                            #                if c.lower() == 'f' or c.lower() == 't':
                            #                    boolval = c.lower()
                            #                    c = self.getChar()
                            #                    if c == '.':
                            #                        if boolval == 'f':
                            #                            genv.text_code += 'False'
                            #                            continue
                            #                        elif boolval == 't':
                            #                            genv.text_code += 'True'
                            #                            continue
                            #                        else:
                            #                            genv.have_errors = True
                            #                            genv.unexpectedError(_(".f. or .t. expected"))
                            #                            return
                            #                    else:
                            #                        genv.have_errors = True
                            #                        genv.unexpectedError(_("dot '.' expected"))
                            #                        return
                            #                else:
                            #                    genv.have_errors = True
                            #                    genv.unexpectedError(_(".f. or .t. expected"))
                            #                    return
                            #            elif c.isnumeric():
                            #                showInfo("todo: c.isnumeric()")
                            #               genv.have_errors = True
                            #                break
                            #            elif c.isalpha():
                            #                self.getIdent(c)
                            #                showInfo("token:  " + self.token_str)
                            #                if self.token_str.lower() == "false":
                            #                    genv.text_code += "False\r"
                            #                elif self.token_str.lower() == "true":
                            #                    genv.text_code += "True\r"
                            #                else:
                            #                    genv.have_errors = True
                            #                    genv.unexpectedError(_("false or true or .t. or .f. expected."))
                            #                    return
                            #                showInfo("102\n" + genv.text_code)
                            #                continue
                            #            else:
                            #                genv.have_errors = True
                            #                genv.unexpectedError(_("boolean value expected."))
                            #                return
                            #else:
                            #    genv.text_code += self.token_str
                            #    return
                        elif genv.char_curr == '=':
                            showInfo("===\n" + genv.text_code)
                            genv.text_code += " = "
                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                            if genv.char_curr == genv.ptNoMoreData:
                                genv.have_errors = True
                                raise e_no_more_data();
                            elif genv.char_curr.isalpha() or genv.char_curr == '_':
                                self.getIdent(genv.char_curr)
                                if self.token_str.lower() == "new":
                                    showInfo("new er")
                                    genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                    if genv.char_curr == genv.ptNoMoreData:
                                        genv.have_errors = True
                                        genv.unexpectedError(_("new expected."))
                                        return
                                    elif genv.char_curr.isalpha() or genv.char_curr == '_':
                                        self.getIdent(genv.char_curr)
                                        if self.token_str.lower() in genv.dbase_keywords:
                                            genv.have_errors = True
                                            genv.unexpectedError(_("keywords not allowed there"))
                                            return
                                        genv.text_code += self.token_str
                                        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                        if genv.char_curr == genv.ptNoMoreData:
                                            genv.have_errors = True
                                            genv.unexpectedError(_("open paren expected."))
                                            return
                                        elif genv.char_curr == '(':
                                            genv.text_code += '('
                                            genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                                            if genv.char_curr == genv.ptNoMoreData:
                                                genv.have_errors = True
                                                genv.unexpectedError(_("open paren expected."))
                                                return
                                            elif genv.char_curr == ')':
                                                genv.text_code += ')\n'
                                                genv.text_code += ('\t' * genv.counter_indent)
                                                showInfo("parne:\n" + genv.text_code)
                                                continue
                                        else:
                                            raise e_expr_error()
                                            return
                                    else:
                                        raise e_expr_error()
                                        return
                                else:
                                    raise e_expr_error()
                                    return
                            else:
                                raise e_expr_error()
                                break
                        else:
                            raise e_expr_error()
                            break
                else:
                    genv.have_errors = True
                    genv.unexpectedError(_("unexpected syntax"))
                    return
                
                #showInfo("Line: " + str(genv.start_idx) + "\n" + self.text_code)
                #showInfo(genv.text_code)
                #self.update_code(genv.text_code)
            else:
                self.handle_scoped_commands()
        
        except e_no_more_data as ex:
            showInfo("-->IF:  " + str(genv.counter_if) + "\nBB: " + str(genv.counter_endif))
            if not (genv.counter_if == genv.counter_endif):
                genv.have_errors = True
                genv.unexpectedError(_("if/endif syntax error."))
    
    def check_point(self):
        genv.char_curr = self.check_token_no_more_data(_("check point"))
        if genv.char_curr == '.':
            genv.text_code += '.'
            return '.'
        else:
            genv.habe_errors = True
            genv.unexpectedError(_("point expected."))
            return False
    
    def check_token_ident_macro(self, token):
        if token in genv.token_macro:
            return True
        else:
            genv.have_errors = True
            genv.unexpectedError(_("macro condition expected."))
        return False
    
    def check_token_ident(self):
        self.check_token_no_more_data()
        if genv.char_curr.isalpha() or genv.char_curr == '_':
            self.getIdent(genv.check_curr)
            genv.text_code += self.token_str
            return True
        else:
            genv.have_errors = True
            genv.unexpectedError(_("ident expected."))
        return False
    
    def check_token_keywords(self, tokens):
        for item in tokens:
            if item in genv.dbase_keywords:
                genv.have_errors = True
                genv.unexpectedError(_("keywords not allowed there."))
                return False
            else:
                if item.lower() == self.token_str.lower():
                    return True
            return False
    
    def check_token_expr(self, tokens):
        if self.check_token_keywords(tokens) == False:
            self.check_token_char('(')
            self.expect_expr()
            self.check_token_char(')')
            return True
        return False
    
    def check_token_char(self, ch):
        if genv.char_curr == ch:
            return True
        return False
    
    def check_color_token(self, flag):
        self.token_str = ""
        #
        fg_color = "#FF0000"
        bg_color = "#000000"
        #
        fg_found = False
        bg_found = False
        #
        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
        if genv.char_curr.isalpha():
            self.token_str = genv.char_curr
            genv.char_curr = self.getChar()
            if genv.char_curr == '+':
                self.token_str += genv.char_curr
                fg_color = self.token_str
                if self.token_str in genv.concolors:
                    index    = genv.concolors.index(self.token_str)
                    fg_color = genv.convalues[index]
                    fg_found = True
                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                if genv.char_curr == '/':
                    genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                    if genv.char_curr.isalpha():
                        self.token_str = genv.char_curr
                        genv.char_curr = self.getChar()
                        if genv.char_curr == '+':
                            self.token_str += genv.char_curr
                        elif genv.char_curr.isalpha():
                            self.token_str += genv.char_curr
                        if self.token_str in genv.concolors:
                            if self.token_str in genv.concolors:
                                index    = genv.concolors.index(self.token_str)
                                bg_color = genv.convalues[index]
                                bg_found = True
                            else:
                                genv.unexpectedError(_("invalide bg color"))
                        else:
                            genv.unexpectedError(_("bg error"))
                    else:
                        self.ungetChar(1)
            elif genv.char_curr == '/':
                fg_color = self.token_str
                if self.token_str in genv.concolors:
                    index    = genv.concolors.index(self.token_str)
                    fg_color = genv.convalues[index]
                    fg_found = True
                genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                if genv.char_curr.isalpha():
                    self.token_str = genv.char_curr
                    genv.char_curr = self.getChar()
                    if genv.char_curr == '+':
                        self.token_str += genv.char_curr
                    elif genv.char_curr.isalpha():
                        self.token_str += genv.char_curr
                    if self.token_str in genv.concolors:
                        if self.token_str in genv.concolors:
                            index    = genv.concolors.index(self.token_str)
                            bg_color = genv.convalues[index]
                            bg_found = True
                        else:
                            genv.unexpectedError(_("invalide bg color"))
                    else:
                        genv.unexpectedError(_("bg error"))
                else:
                    self.ungetChar(1)
            elif genv.char_curr.isalpha():
                self.token_str += genv.char_curr
                fg_color = self.token_str
                if self.token_str in genv.concolors:
                    index    = genv.concolors.index(self.token_str)
                    fg_color = genv.convalues[index]
                    fg_found = True
                    genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                    if genv.char_curr == '/':
                        genv.char_curr = self.skip_white_spaces(self.dbase_parser)
                        if genv.char_curr.isalpha() or genv.char_curr == '_':
                            self.getIdent(genv.char_curr)
                            #showInfo('color: ' + self.token_str)
                            if self.token_str in genv.concolors:
                                index    = genv.concolors.index(self.token_str)
                                bg_color = genv.convalues[index]
                                bg_found = True
                            else:
                                genv.unexpectedError(_("invalide bg color"))
                        else:
                            genv.unexpectedError(_("bg error"))
                    else:
                        self.ungetChar(1)
                else:
                    # todo: variable !!!
                    genv.unexpectedError(_("invalide fg color"))
                    #
            else:
                genv.unexpectedError(_("color error"))
        self.fg_color = fg_color
        self.bg_color = bg_color
        
        #showInfo("-->FG_color:  \n" + self.fg_color + "\n" + self.bg_color)
        return 1000

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
        try:
            self.parser = None
            self.parser = interpreter_dBase(script_name)
        except ENoSourceHeader as e:
            showError(e.message)
            self.parser = None

class interpreter_Pascal(interpreter_base):
    def __init__(self, file_name):
        super(interpreter_Pascal, self).__init__(file_name)
        self.script_name   = file_name
    
    def parse(self):
        genv.line_col = 1
        genv.line_row = 1
        #
        open_paren    = 0
        
        self.pos = -1
        
        script_app_type = ""
        script_app_name = ""
        
        genv.actual_parser = self.pascal_parser
        
        while True:
            self.skip_white_spaces(self.pascal_parser)
            
            # <program> <name> <;>
            if self.token_str.lower() == "program":
                self.token_str = ""
                while True:
                    if self.handle_pascal_white_spaces():
                        continue
                    if self.check_ident():
                        self.handle_pascal_program_ident()
                        break
                    else:
                        raise Exception(_("ident expected."))
                break
    
    def handle_pascal_program_ident(self):
        while True:
            if self.handle_pascal_white_spaces():
                continue
            if self.check_char(';'):
                while True:
                    if self.handle_pascal_white_spaces():
                        continue                                    
                    if not self.check_ident():
                        raise Exception(_("ident expecred."))
                    if self.token_str.lower() == "begin":
                        self.handle_pascal_body()
                        #self.handle_pascal_tail()
                        break
                    elif self.token_str.lower() == "procedure":
                        self.handle_pascal_procedure_name()
                        print("AAAAA")
                        
                    elif self.token_str.lower() == "function":
                        self.handle_pascal_function()
            else:
                raise Exception(_("semicolon expected."))
    
    def handle_pascal_white_spaces(self):
        genv.char_prev = genv.char_curr
        self.getChar()

        if self.check_white_spaces():
            return True
        elif self.check_char('{'):
            self.handle_pascal_comment_1()
            return True
        elif self.check_char('('):
            self.handle_pascal_comment_2() # todo: expr
            return True
        else:
            return False
            
    def handle_pascal_procedure_name(self):
        while True:
            if self.handle_pascal_white_spaces():
                continue
            if self.check_ident():
                print("procedure name: " + self.token_str)
                self.current_state = "procedure"
                self.handle_pascal_white_spaces()
                return True
            else:
                return False
                
    def handle_pascal_function(self):
        while True:
            if self.handle_pascal_white_spaces():
                continue            
            elif self.check_ident():
                print("function name: " + self.token_str)
                self.current_state = "function"
                self.handle_pascal_white_spaces()
                break
                
    def handle_pascal_body(self):
        while True:
            if self.handle_pascal_white_spaces():
                continue
            if self.check_ident():
                if self.token_str.lower() == "end":
                    while True:
                        if self.handle_pascal_white_spaces():
                            continue
                        #if self.check_char('.'):
                        #    print("program end.")
                        #    return True
                        if self.check_char(';'):
                            print("ENDE")
                            while True:
                                if self.handle_pascal_white_spaces():
                                    continue
                                if self.check_ident():
                                    showInfo(self.token_str)
                                    if self.token_str.lower() == "begin":
                                        showInfo("333333333333")
                                        while True:
                                            if self.handle_pascal_white_spaces():
                                                continue 
                                            if self.check_ident():
                                                showInfo("o>> " + self.token_str)
                                                if self.token_str.lower() == "end":
                                                    while True:
                                                        if self.handle_pascal_white_spaces():
                                                            continue 
                                                        if self.check_char('.'):
                                                            break
                                                        else:
                                                            raise Exception("Point expected.")
                                                    break
                                                else:
                                                    raise Exception("end expected.")
                                            else:
                                                raise Exception("ident expected.")
                                        break
                                    elif self.token_str.lower() == "procedure":
                                        self.handle_pascal_procedure_name()
                                        showInfo("8888888888888888888")
                                        while True:
                                            if self.handle_pascal_white_spaces():
                                                continue
                                            if self.check_ident():
                                                showInfo("UUuii: " + self.token_str)
                                                if self.token_str.lower() == "begin":
                                                    while True:
                                                        if self.handle_pascal_white_spaces():
                                                            continue
                                                        if self.check_ident():
                                                            showInfo("ccccc> " + self.token_str)
                                                            if self.token_str.lower() == "end":
                                                                while True:
                                                                    self.getChar()
                                                                    if genv.char_curr == ' ':
                                                                        continue
                                                                    if genv.char_curr == ';':
                                                                        while True:
                                                                            if self.handle_pascal_white_spaces():
                                                                                continue
                                                                            if self.check_ident():
                                                                                if self.token_str == "begin":
                                                                                    while True:
                                                                                        if self.handle_pascal_white_spaces():
                                                                                            continue
                                                                                        if self.check_ident():
                                                                                            if self.token_str == "end":
                                                                                                while True:
                                                                                                    self.getChar()
                                                                                                    if genv.char_curr == '.':
                                                                                                        break
                                                                                                    elif genv.char_curr == ' ' \
                                                                                                    or   genv.char_curr == '\t'\
                                                                                                    or   genv.char_curr == '\n':
                                                                                                        continue
                                                                                                    elif self.handle_pascal_white_spaces():
                                                                                                        continue
                                                                                                    raise Exception("point expected.")
                                                                                            else:
                                                                                                raise Exception("end expected.")
                                                                                        else:
                                                                                            raise Exception("ident expected.")
                                                                                    break
                                                                        break
                                                                    if genv.char_curr == '.':
                                                                        print("pppppp")
                                                                        break
                                                                    else:
                                                                        print("g: " + genv.char_curr)
                                                                        print("t: " + self.token_str)
                                                                        raise Exception(_("Point expected."))
                                                                break
                                                    break
                                    else:
                                        raise Exception(f"Line: {genv.line_row}\nBegin expected.")
                            continue
                        elif self.check_ident():
                            if self.token_str.lower() == "procedure":
                                self.current_state = "procedure"
                                self.handle_pascal_procedure_name()
                                continue
                        else:
                            raise Exception(_("point (.) expected."))
                    break
                else:
                    raise Exception(_("syntax error."))
                
    def handle_pascal_begin(self):
        pass
    
    def handle_pascal_end(self):
        pass
        
    def handle_pascal_tail(self):
        while True:
            if self.handle_pascal_white_spaces():
                continue
            if self.check_ident():
                showInfo("oooo====>> " + self.token_str)
                break
    
    def handle_pascal_code(self, token):
        return
    
    def handle_pascal_commands(self):
        showInfo("oooooo---> " + self.token_str)

class pascalDSL():
    def __init__(self, script_name):
        self.script = None
        
        self.parser = None
        self.parser = interpreter_Pascal(script_name)
        self.parser.parse()

class interpreter_Python(interpreter_base):
    def __init__(self, file_name):
        super(interpreter_Pascal, self).__init__(file_name)
        
    def parse(self):
        self.token_str = ""

class pythonDSL():
    def __init__(self, script_name):
        self.script = None
        
        self.parser = None
        self.parser = interpreter_Python(script_name)
        self.parser.parse()

class interpreter_Java(interpreter_base):
    def __init__(self, file_name):
        super(interpreter_Java, self).__init__(file_name)
        
    def parse(self):
        self.token_str = ""

class javaDSL():
    def __init__(self, script_name):
        self.script = None
        
        self.parser = None
        self.parser = interpreter_Java(script_name)
        self.parser.parse()

class interpreter_JavaScript(interpreter_base):
    def __init__(self, file_name):
        super(interpreter_JavaScript, self).__init__(file_name)
        
    def parse(self):
        self.token_str = ""

class javaScriptDSL():
    def __init__(self, script_name):
        self.script = None
        
        self.parser = None
        self.parser = interpreter_JavaScript(script_name)
        self.parser.parse()

class interpreter_ISOC(interpreter_base):
    def __init__(self, file_name):
        super(interpreter_ISOC, self).__init__(file_name)
        
    def parse(self):
        self.token_str = ""

class interpreter_Prolog(interpreter_base):
    def __init__(self, file_name):
        super(interpreter_Prolog, self).__init__(file_name)

class interpreter_LISP(interpreter_base):
    def __init__(self, file_name):
        super(interpreter_LISP, self).__init__(file_name)
    
    def parse(self):
        genv.line_col = 1
        genv.line_row = 1
        #
        open_paren    = 0
        while True:
            if self.skip_white_spaces(self.lisp_parser):
                showInfo("pppp: " + self.token_str)
            break

class lispDSL():
    def __init__(self, script_name):
        self.script = None
        
        self.parser = None
        self.parser = interpreter_LISP(script_name)
        self.parser.parse()

class C64BasicWorkerThread(QThread):
    progress = pyqtSignal(int)
    def run(self):
        time.sleep(0.2)
        self.progress.emit(1)

class C64BasicParser:
    class CaseInsensitiveDict(dict):
        def __setitem__(self, key, value):
            super().__setitem__(key.lower(), value)

        def __getitem__(self, key):
            return super().__getitem__(key.lower())

        def __contains__(self, key):
            return super().__contains__(key.lower())

        def get(self, key, default=None):
            return super().get(key.lower(), default)
    
    def __init__(self, script_name):
        self.script_name = script_name
        self.code = ""
        
        self.func_lines = []
        self.c64_exec_thread_running = 0
        self.c64_exec_thread = None

        self.nbsp1 = (" " * 4)
        self.nbsp2 = self.nbsp1 + self.nbsp1
        self.nbsp3 = self.nbsp2 + self.nbsp1
        self.nbsp4 = self.nbsp2 + self.nbsp2
        self.nbsp5 = self.nbsp3 + self.nbsp2
        self.nbsp6 = self.nbsp3 + self.nbsp3
        
        self.workerThread   = "self.worker_thread"
        self.winco          = "self.console"
        self.wincoPrintLine = self.winco + ".win.print_line"
        
        self.token_index = 0
        
        with open(script_name, "r", encoding="utf-8") as file:
            self.code = file.read()
            file.close()
        
        # ----------------------------------------
        # Liste der BASIC-Schlüsselwörter mit ent-
        # sprechenden Opcodes
        # ----------------------------------------
        self.commands = self.CaseInsensitiveDict({
            "NEW":      0x9E00,
            
            "RUN":      0xA000,
            "INPUT":    0xA500,
            "PRINT":    0xA600,
            "IF":       0xA800,
            "GOTO":     0xA900,
            "GOSUB":    0xAA00,
            "RETURN":   0xAB00,
            "POKE":     0xAC00,
            "PEEK":     0xAD00,
            "FOR":      0xAE00,
            "NEXT":     0xAF00,
            
            "END":      0xB000,
            "STOP":     0xB100,
            "DIM":      0xB300,
            "READ":     0xB400,
            "DATA":     0xB500,
            "RESTORE":  0xB600,
            "ON":       0xB700,
            "SYS":      0xB900,
            "OPEN":     0xBA00,
            "CLOSE":    0xBB00,
            "VERIFY":   0xBC00,
            
            "CLR":      0xC000,
            
            "RIGHT":    0xD100,
            "LEFT":     0xD200
        })
        
        # ----------------------------------------
        # Reguläre Ausdrücke für BASIC-Elemente
        # ----------------------------------------
        self.token_patterns = {
            "NUMBER":       r"^\d+",
            "COMMAND":      r"^[a-zA-Z]+",
            "STRING":       r'^\"[^"]*\"',
            "VARIABLE":     r"^[a-zA-Z][0-9a-zA-Z]*",
            "SYMBOL":       r"^[=,+\-*/()]",
        }
    
    # ----------------------------------------
    # Zerlegt den BASIC-Code in Tokens.
    # ----------------------------------------
    def tokenize(self, code):
        tokens = []
        while code:
            code = code.lstrip()  # Leerzeichen entfernen
            matched = False
            for token_type, pattern in self.token_patterns.items():
                match = re.match(pattern, code, re.IGNORECASE)
                if match:
                    tokens.append((token_type, match.group(0)))
                    code = code[len(match.group(0)):]
                    matched = True
                    break
            if not matched:
                raise SyntaxError(f"Unbekanntes Token: {code}")
        return tokens
    
    # -------------------------------------
    # Parst einen BASIC-Code in eine Liste
    # von Befehlen.
    # -------------------------------------
    def parse(self):
        lines = self.code.splitlines()
        parsed_program = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # ----------------------------------
            # Extrahiere die Zeilennummer
            # ----------------------------------
            match = re.match(self.token_patterns["NUMBER"], line)
            if not match:
                raise SyntaxError(f"Fehlende Zeilennummer: {line}")

            line_number  = int(match.group(0))
            rest_of_line = line[len(match.group(0)):].strip()
            
            # ----------------------------------
            # Tokenisiere den Rest der Zeile
            # ----------------------------------
            tokens = self.tokenize(rest_of_line)
            
            # ----------------------------------
            # Überprüfe, ob der erste Token ein
            # gültiges BASIC-Schlüsselwort ist
            # ----------------------------------
            #showInfo(f"info:\n{tokens[0][0]}\n1: {tokens[0][1]}")
            if tokens[0][0] == "COMMAND":
                if not (tokens[0][1].upper() in (key.upper() for key in self.commands)):
                    raise SyntaxError(f"Unbekannter Befehl '{tokens[0][1]}' in Zeile {line_number}")
            
            # ----------------------------------
            # Übersetze die Tokens
            # ----------------------------------
            parsed_line = {"line_number": line_number, "tokens": tokens}
            parsed_program.append(parsed_line)

        return parsed_program
        
    # --------------------------------------
    # Erkennt Endlosschleifen im BASIC-Code.
    # --------------------------------------
    def detect_infinite_loops(self, parsed_program):
        graph = {}

        # Baue den Kontrollflussgraphen
        for line in parsed_program:
            line_number = line["line_number"]
            tokens = line["tokens"]

            if tokens and tokens[0][1] == "GOTO":
                target_line = int(tokens[1][1])
                if line_number not in graph:
                    graph[line_number] = []
                graph[line_number].append(target_line)

        # Zyklusprüfung im Graphen
        visited = set()
        stack = set()

        def visit(node):
            if node in stack:
                return True  # Zyklus gefunden
            if node in visited:
                return False

            visited.add(node)
            stack.add(node)

            for neighbor in graph.get(node, []):
                if visit(neighbor):
                    return True

            stack.remove(node)
            return False

        for node in graph:
            if visit(node):
                return True  # Endlosschleife erkannt

        return False
    
    # -------------------------------------------
    # Konvertiert den BASIC-Code in Python-Code.
    # -------------------------------------------
    def convert_to_python(self, parsed_program):
        python_code = []
        function_definitions = []
        
        # --------------------------------------------
        # Liste aller Zeilennummern erstellen
        # --------------------------------------------
        all_line_numbers = sorted({line["line_number"] for line in parsed_program})
        
        # ---------------------------------------------
        # Funktionen für alle Zeilennummern generieren
        # ---------------------------------------------
        for i, line_number in enumerate(all_line_numbers):
            next_line_number = all_line_numbers[i + 1] if i + 1 < len(all_line_numbers) else None
            function_code    =  [f"{self.nbsp1}def line_{line_number}(self):"]
            function_code.append(f"{self.nbsp2}self.current_line = None")  # Initialisierung von next_line
            str_num = ""
            
            # --------------------------------------------
            # Suche die passende Zeile im BASIC-Code
            # --------------------------------------------
            matching_lines = [line for line in parsed_program if line["line_number"] == line_number]
            if matching_lines:
                try:
                    self.token_index = 0
                    string = ""
                    tokens = matching_lines[self.token_index]["tokens"]
                    
                    # ----------------------------------
                    # Übersetzung für END-Befehl
                    # ----------------------------------
                    if tokens \
                    and (tokens[self.token_index][0] == "COMMAND") \
                    and (tokens[self.token_index][1] == "END"):
                        function_code.append(f"{self.nbsp2}self.running = 2")
                        function_code.append(f"{self.nbsp2}self.current_line = None")
                    
                    # ----------------------------------
                    # Übersetzung für PRINT-Befehl
                    # ----------------------------------
                    elif tokens \
                    and (tokens[self.token_index][0].upper().upper() == "COMMAND") \
                    and (tokens[self.token_index][1].upper() == "PRINT"):
                        print_parts = []
                        while self.token_index <= len(tokens):
                            self.token_index += 1
                            string = ""
                            if self.token_index >= len(tokens):
                                break
                            if tokens \
                            and (tokens[self.token_index][0].upper() == "COMMAND") \
                            and (tokens[self.token_index][1].upper() == "RIGHT"):
                                self.token_index += 1
                                if self.token_index >= len(tokens):
                                    break
                                if tokens \
                                and (tokens[self.token_index][0].upper() == "SYMBOL") \
                                and (tokens[self.token_index][1] == '('):
                                    self.token_index += 1
                                    if self.token_index >= len(tokens):
                                        break
                                    if tokens \
                                    and (tokens[self.token_index][0].upper() == "STRING"):
                                        string = tokens[self.token_index][1][1:-1]
                                        self.token_index += 1
                                        if self.token_index >= len(tokens):
                                            break
                                        if tokens \
                                        and (tokens[self.token_index][0].upper() == "SYMBOL") \
                                        and (tokens[self.token_index][1] == ','):
                                            self.token_index += 1
                                            if self.token_index >= len(tokens):
                                                break
                                            if tokens \
                                            and (tokens[self.token_index][0].upper() == "NUMBER"):
                                                number = int(tokens[self.token_index][1])
                                                print_parts.append(string[:-number])
                                                self.token_index += 1
                                                if self.token_index >= len(tokens):
                                                    break
                                                if tokens \
                                                and (tokens[self.token_index][0].upper() == "SYMBOL") \
                                                and (tokens[self.token_index][1] == ')'):
                                                    if self.token_index >= len(tokens):
                                                        break
                                                    continue
                                                else:
                                                    raise SyntaxError(_(f"symbol expected."))
                                            else:
                                                raise SyntaxError(_(f"number expected."))
                                        else:
                                            raise SyntaxError(_(f"SYmbol expected."))
                                    else:
                                        raise SyntaxError(_(f"string expected."))
                                else:
                                    raise SyntaxError(_(f"Symbol expected."))
                            elif tokens \
                            and (tokens[self.token_index][0].upper() == "COMMAND") \
                            and (tokens[self.token_index][1].upper() == "LEFT"):
                                self.token_index += 1
                                if self.token_index >= len(tokens):
                                    break
                                if tokens \
                                and (tokens[self.token_index][0].upper() == "SYMBOL") \
                                and (tokens[self.token_index][1] == '('):
                                    self.token_index += 1
                                    if self.token_index >= len(tokens):
                                        break
                                    if tokens \
                                    and (tokens[self.token_index][0].upper() == "STRING"):
                                        string = tokens[self.token_index][1][1:-1]
                                        self.token_index += 1
                                        if self.token_index >= len(tokens):
                                            break
                                        if tokens \
                                        and (tokens[self.token_index][0].upper() == "SYMBOL") \
                                        and (tokens[self.token_index][1] == ','):
                                            self.token_index += 1
                                            if self.token_index >= len(tokens):
                                                break
                                            if tokens \
                                            and (tokens[self.token_index][0].upper() == "NUMBER"):
                                                number = int(tokens[self.token_index][1])
                                                print_parts.append(string[number:])
                                                self.token_index += 1
                                                if self.token_index >= len(tokens):
                                                    break
                                                if tokens \
                                                and (tokens[self.token_index][0].upper() == "SYMBOL") \
                                                and (tokens[self.token_index][1] == ')'):
                                                    if self.token_index >= len(tokens):
                                                        break
                                                    continue
                                                else:
                                                    raise SyntaxError(_(f"symbol expected."))
                                            else:
                                                raise SyntaxError(_(f"number expected."))
                                        else:
                                            raise SyntaxError(_(f"SYmbol expected."))
                                    else:
                                        raise SyntaxError(_(f"string expected."))
                                else:
                                    raise SyntaxError(_(f"Symbol expected."))
                                continue
                            elif tokens \
                            and (tokens[self.token_index][0].upper() == "STRING"):
                                string = tokens[self.token_index][1][1:-1]
                                print_parts.append(string)
                                self.token_index += 1
                                if self.token_index >= len(tokens):
                                    break
                                if tokens \
                                and (tokens[self.token_index][0].upper() == "SYMBOL") \
                                and (tokens[self.token_index][1] == '+'):
                                    self.token_index += 1
                                    if self.token_index >= len(tokens):
                                        raise SyntaxError(_(f"string expected at line: {line_number}."))
                                    if tokens \
                                    and (tokens[self.token_index][0].upper() == "STRING"):
                                        string = tokens[self.token_index][1][1:-1]
                                        print_parts.append(string)
                                        if self.token_index+1 >= len(tokens):
                                            break
                                        continue
                                    elif tokens \
                                    and (tokens[self.token_index][0].upper().upper() == "COMMAND")\
                                    and (tokens[self.token_index][1].upper().upper() == "LEFT"):
                                        self.token_index += 1
                                        if tokens \
                                        and (tokens[self.token_index][0].upper() == "SYMBOL")\
                                        and (tokens[self.token_index][1] == '('):
                                            self.token_index += 1
                                            if tokens \
                                            and (tokens[self.token_index][0].upper() == "STRING"):
                                                string_left = tokens[self.token_index][1][1:-1]
                                                self.token_index += 1
                                                if tokens \
                                                and (tokens[self.token_index][0].upper() == "SYMBOL")\
                                                and (tokens[self.token_index][1] == ','):
                                                    self.token_index += 1
                                                    if tokens \
                                                    and (tokens[self.token_index][0].upper() == "NUMBER"):
                                                        number = int(tokens[self.token_index][1])
                                                        if number > len(string):
                                                            raise SyntaxError(_(f"string index out of bounds at line: {line_number}."))
                                                        string_left += " + " + string_left[number:]
                                                        print_parts.append('"'  + string + '"')
                                                        self.token_index += 1
                                                        if tokens \
                                                        and (tokens[self.token_index][0].upper() == "SYMBOL") \
                                                        and (tokens[self.token_index][1] == ')'):
                                                            string += "---"
                                                        else:
                                                            raise SyntaxError(_(f"closed paren expected at line: {line_number}."))
                                                    else:
                                                        raise SyntaxError(_(f"number expected at line: {line_number}."))
                                                else:
                                                    raise SyntacError(_(f"comma expected at line: {line_number}."))
                                            else:
                                                raise SyntaxError(_(f"string expected at line: {line_number}."))
                                        else:
                                            raise SyntaxError(_(f"open paren expected at line: {line_number}."))
                                    else:
                                        raise SyntaxError(_(f"command expected at line: {line_number}."))
                                else:
                                    raise SyntaxError(_(f"symbol expected at line: {line_number}."))
                            #else:
                            #    print_parts.append(token[1])
                        
                        s = ""
                        for word in print_parts:
                            s += word
                        
                        function_code.append(f"{self.nbsp2}{self.wincoPrintLine}(\"{s}\")")
                        function_code.append(f"{self.nbsp2}self.ypos += 1")
                        function_code.append(f"{self.nbsp2}{self.winco}.win.gotoxy(self.xpos, self.ypos)")
                        
                    # Übersetzung für GOTO-Befehl
                    elif tokens \
                    and (tokens[self.token_index][1] == "GOTO"):
                        showInfo("goootooo")
                        target_line = tokens[self.token_index][1]
                        function_code.append(f"{self.nbsp2}self.current_line = {target_line}")
                except IndexError as e:
                    showInfo(_(f"Index Error:\n{e}"))
                except ValueError as e:
                    showInfo(_(f"Value Error:\n{e}"))
                except Exception  as e:
                    showInfo(_(f"Exception Error:\n{e}"))
                
                # ----------------------------------
                # Standardabschluss der Funktion
                # ----------------------------------
                if next_line_number is not None:
                    function_code.append(f"{self.nbsp2}if self.current_line is None: self.current_line = {next_line_number}")
                function_code.append(f"{self.nbsp2}return self.current_line")
                function_definitions.append("\n".join(function_code))
            
        # --------------------------------------------
        # Main-Ausführungslogik
        # --------------------------------------------
        python_code.append("class main(QObject):")
        python_code.append(self.nbsp1 + "def __init__(self):")
        python_code.append(self.nbsp2 + "super().__init__()")
        python_code.append(self.nbsp2 + "self.current_line = 1")
        python_code.append(self.nbsp2 + "self.running = 0")
        python_code.append(self.nbsp2 + "self.xpos = 1")
        python_code.append(self.nbsp2 + "self.ypos = 1")
        
        python_code.append(self.nbsp2 + self.winco + " = C64Console(None)")
        python_code.append(self.nbsp2 + self.wincoPrintLine + "('holladiho')")
        
        python_code.append(self.nbsp2 + self.workerThread + " = C64BasicWorkerThread()")
        python_code.append(self.nbsp2 + self.workerThread + ".progress.connect(self.update_progress)")
        python_code.append(self.nbsp2 + self.workerThread + ".start()")
        
        python_code.append(self.nbsp1 + "def update_progress(self,value):")
        python_code.append(self.nbsp2 + "while True:")
        python_code.append(self.nbsp3 + "func_name = f'line_{self.current_line}'")
        python_code.append(self.nbsp3 + "if hasattr(self,func_name):")
        python_code.append(self.nbsp4 + self.winco + ".win.gotoxy(self.xpos,self.ypos)")
        python_code.append(self.nbsp4 + "method = getattr(self,func_name)")
        python_code.append(self.nbsp4 + "self.current_line = method()")
        python_code.append(self.nbsp4 + "if not self.current_line == None:")
        python_code.append(self.nbsp5 + "continue")
        python_code.append(self.nbsp4 + "else:")
        python_code.append(self.nbsp5 + "break")
        python_code.append(self.nbsp3 + "else:")
        python_code.append(self.nbsp4 + "self.current_line += 1")
        
        python_code.extend(function_definitions)
        
        python_code.append("main_func = main()")
        python_code.append("main_func.console.exec_()")
        return "\n".join(python_code)
    
    # -----------------------------------------------------------------------
    # Konvertiert einen ASCII-String in PETSCII.
    # Nur eine Basisimplementierung für Großbuchstaben und Zahlen.
    # -----------------------------------------------------------------------
    def ascii_to_petscii(self, ascii_str):
        petscii = bytearray()
        for char in ascii_str:
            char_code = ord(char)
            # ----------------------------------
            # Großbuchstaben
            # ----------------------------------
            if 'A' <= char <= 'Z':
                petscii.append(char_code)
            # ----------------------------------
            # Kleinbuchstaben (Konvertiere zu
            # PETSCII-Großbuchstaben)
            # ----------------------------------
            elif 'a' <= char <= 'z':
                petscii.append(char_code - 32)
            # ----------------------------------
            # Zahlen
            # ----------------------------------
            elif '0' <= char <= '9':
                petscii.append(char_code)
            # ----------------------------------
            # Leerzeichen
            # ----------------------------------
            elif char == ' ':
                petscii.append(0x20)
            # ----------------------------------
            # Einige Sonderzeichen
            # ----------------------------------
            elif char in '!"#$%&\'()*+,-./:;<=>?@[\\]^_':
                petscii.append(char_code)
            else:
                raise ValueError(f"Zeichen '{char}' kann nicht in PETSCII konvertiert werden.")
        return petscii
    
    # -----------------------------------------------------------------------
    # Konvertiert den geparsten BASIC-Code in das Commodore 64 BASIC
    # Dateiformat.
    # \param   parsed_program: Geparstes BASIC-Programm als Liste von Zeilen
    # \return: Bytes im C64 BASIC Dateiformat
    # -----------------------------------------------------------------------
    def convert_to_binbas(self, parsed_program):
        memory_address = 0x0801  # Standardadresse für BASIC-Programme im C64
        output = bytearray()

        for line in parsed_program:
            line_number = line["line_number"]
            tokens = line["tokens"]
            
            # ----------------------------------
            # Zeilenadresse (2 Bytes)
            # ----------------------------------
            line_address = memory_address + len(output) + 2  # +2 für Zeilenadresse selbst
            output.extend(line_address.to_bytes(2, "little"))
            
            # ----------------------------------
            # Zeilennummer (2 Bytes)
            # ----------------------------------
            output.extend(line_number.to_bytes(2, "little"))
            
            # ----------------------------------
            # Tokenisierte Zeile
            # ----------------------------------
            for token in tokens:
                if token[0] == "COMMAND" and token[1] in C64BasicParser(self.script_name).commands:
                    # ----------------------------------
                    # BASIC-Schlüsselwort in Tokenform
                    # ----------------------------------
                    token_value = C64BasicParser(self.script_name).commands[token[1]] & 0xFF
                    output.append(token_value)
                    
                elif token[0] == "STRING":
                    # ----------------------------------
                    # String in Anführungszeichen
                    # ----------------------------------
                    # Entferne Anführungszeichen
                    # ----------------------------------
                    petscii_string = self.ascii_to_petscii(token[1][1:-1])
                    output.extend(petscii_string)
                    
                elif token[0] == "NUMBER":
                    # ----------------------------------
                    # Zahl als ASCII
                    # ----------------------------------
                    output.extend(self.ascii_to_petscii(token[1]))
                    
                elif token[0] == "SYMBOL":
                    # ----------------------------------
                    # Symbole direkt hinzufügen
                    # ----------------------------------
                    output.extend(self.ascii_to_petscii(token[1]))
                    
                elif token[0] == "VARIABLE":
                    # ----------------------------------
                    # Variable direkt hinzufügen
                    # ----------------------------------
                    output.extend(self.ascii_to_petscii(token[1]))
            
            # ----------------------------------
            # End-of-line Marker
            # ----------------------------------
            output.append(0x00)
        
        # ----------------------------------
        # End-of-file Marker
        # ----------------------------------
        output.extend(b"\x00\x00")
        return bytes(output)
    
    def run_bytecode(self, bytecode_file):
        with open(bytecode_file, "rb") as f:
            loaded_code = marshal.load(f)
        exec(loaded_code, globals())
        
        #"""Führt den Bytecode in einem separaten Thread aus."""
        #def run():
        #    if genv.c64_parser.c64_exec_thread_running == 2:
        #        self.c64_exec_thread_stop()
        #        return
        #    with open(bytecode_file, "rb") as f:
        #        loaded_code = marshal.load(f)
        #        while self.c64_exec_thread_running < 2:
        #            exec(loaded_code, globals())
        #
        #self.c64_exec_thread = threading.Thread(target=run)
        #self.c64_exec_thread.start()
        #return self.c64_exec_thread
    
    # -----------------------------------
    # Stoppt die laufende Ausführung.
    # -----------------------------------
    def c64_exec_thread_stop(self):
        if not self.c64_exec_thread == None:
            self.c64_exec_thread_running = 2

class interpreter_C64(interpreter_base):
    def __init__(self, file_name):
        super(interpreter_C64, self).__init__(file_name)
        
    def parse(self):
        self.token_str = ""

class PascalParser:
    def __init__(self, script_name):
        self.script_name = script_name
        self.line_number = 0
        
        # Ergebnisse
        self.comments = []
        self.tokens = []
        self.errors = []
        
        # Pascal-Schlüsselwörter
        self.keywords = {"PROGRAM", "BEGIN", "END", "VAR", "PROCEDURE", "FUNCTION", "IF", "THEN", "ELSE", "WHILE", "DO"}

        # Muster für Tokenisierung
        self.token_patterns = [
            (r"[a-zA-Z_][a-zA-Z0-9_]*", "ident"),  # Identifikatoren und Schlüsselwörter
            (r"\d+", "number"),                    # Zahlen
            (r"[+\-*/:=<>();,.]", "symbol"),       # Trennzeichen
            (r"\"(?:[^\"]|(?<=\\)\")*\"", "string1"),  # Strings mit doppelten Anführungszeichen
            (r"'(?:[^\']|(?<=\\)')*'", "string2")   # Strings mit einfachen Anführungszeichen
        ]
        self.token_regex = re.compile("|".join(f"(?P<{name}>{pattern})" for pattern, name in self.token_patterns))
        self.macro_regex = re.compile(r"\{\$(ifdef|else|endif)\s*([a-zA-Z0-9_]*)\}")

        # Kommentar-Tokens
        self.comment_tokens = {
            "curly": {"start": "{", "end": "}"},
            "round": {"start": "(*", "end": "*)"},
            "single_line": {"start": "//"}  # Einzeiliger Kommentar
        }

        # Pascal-Grammatik als JSON
        self.pascal_grammar = """
        {
          "sequence": [
            {"type": "keyword", "value": "PROGRAM"},
            {"type": "ident"},
            {"type": "symbol", "value": ";"}
          ],
          "repeated": [
            {
              "type": "keyword", "value": "VAR",
              "declarations": [
                {"type": "ident"},
                {"type": "symbol", "value": ":"},
                {"type": "ident"},
                {"type": "symbol", "value": ";"},
                {
                  "optional": [
                    {"type": "symbol", "value": ","},
                    {"type": "ident"}
                  ]
                }
              ]
            }
          ]
        }
        """

    def parse(self):
        with open(self.script_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            stack = []  # Verschachtelungs-Stack für Makros und Kommentare

            for line in lines:
                self.line_number += 1
                i = 0

                while i < len(line):
                    # Prüfe auf Makro-Kommentare
                    macro_match = self.macro_regex.match(line[i:])
                    if macro_match:
                        macro_type = macro_match.group(1)  # ifdef, else, endif
                        macro_name = macro_match.group(2)  # Name des Makros (falls vorhanden)
                        position = i + macro_match.start() + 1

                        if macro_type == "ifdef":
                            stack.append({"type": "ifdef", "line": self.line_number, "pos": position, "name": macro_name, "else_used": False})
                            self.tokens.append((self.line_number, position, f"ifdef {macro_name}", "macro"))
                        elif macro_type == "else":
                            if not stack or stack[-1]["type"] != "ifdef":
                                self.errors.append((self.line_number, position, "Unerwartetes {$else} außerhalb eines {$ifdef}-Blocks."))
                            elif stack[-1]["else_used"]:
                                self.errors.append((self.line_number, position, "Mehrfache {$else} im selben {$ifdef}-Block."))
                            else:
                                stack[-1]["else_used"] = True
                                self.tokens.append((self.line_number, position, "else", "macro"))
                        elif macro_type == "endif":
                            if not stack or stack[-1]["type"] != "ifdef":
                                self.errors.append((self.line_number, position, "Unerwartetes {$endif} ohne passendes {$ifdef}."))
                            else:
                                stack.pop()
                                self.tokens.append((self.line_number, position, "endif", "macro"))

                        i += macro_match.end()  # Überspringe den gesamten Makro-Kommentar
                        continue

                    # Prüfe auf Kommentare
                    if line[i:i+2] == self.comment_tokens["single_line"]["start"]:
                        # Einzeiliger Kommentar
                        self.comments.append((self.line_number, i + 1, line[i:].strip()))
                        break  # Rest der Zeile ignorieren

                    elif line[i] == self.comment_tokens["curly"]["start"]:
                        # Mehrzeiliger Kommentar `{ ... }`
                        start_pos = i
                        i += 1
                        while i < len(line):
                            if line[i] == self.comment_tokens["curly"]["end"]:
                                self.comments.append((self.line_number, start_pos + 1, line[start_pos:i + 1]))
                                i += 1
                                break
                            else:
                                i += 1
                        continue

                    elif line[i:i+2] == self.comment_tokens["round"]["start"]:
                        # Mehrzeiliger Kommentar `(* ... *)`
                        start_pos = i
                        i += 2
                        while i < len(line):
                            if line[i:i+2] == self.comment_tokens["round"]["end"]:
                                self.comments.append((self.line_number, start_pos + 1, line[start_pos:i + 2]))
                                i += 2
                                break
                            else:
                                i += 1
                        continue

                    # Prüfe auf reguläre Tokens
                    token_match = self.token_regex.match(line[i:])
                    if token_match:
                        token = token_match.group()
                        token_type = token_match.lastgroup
                        position = i + 1

                        # Bestimme den Token-Typ
                        if token.upper() in self.keywords:
                            token_type = "keyword"
                        elif token_match.lastgroup == "number":
                            token_type = "number"
                        elif token_match.lastgroup == "symbol":
                            token_type = "symbol"
                        elif token_match.lastgroup == "string1":
                            token_type = "string"
                        elif token_match.lastgroup == "string2":
                            token_type = "string"
                        else:
                            token_type = "ident"
                        
                        self.tokens.append((self.line_number, position, token, token_type))
                        i += len(token)
                        continue
                    i += 1
        
        # Überprüfe auf nicht abgeschlossene Makros
        while stack:
            macro = stack.pop()
            if macro["type"] == "ifdef":
                self.errors.append((macro["line"], macro["pos"], f"Unvollständiger Makro-Block: $ifdef {macro['name']} wurde nicht geschlossen."))
        
        genv.source_comments = self.comments
        genv.source_tokens   = self.tokens
        genv.source_errors   = self.errors
        
        # Starte die Validierung der Struktur
        success, start_index = self.validate_structure(self.pascal_grammar)
        if not success:
            showError(_(f"syntax error:\n{genv.source_errors}"))
        return
        
    def handle_multi_line_comment(self, match, line_number):
        """Hilfsmethode zum Verarbeiten von mehrzeiligen Kommentaren."""
        self.comments.append((line_number, match.start(), match.group()))
        # Ersetze den Kommentar durch Leerzeichen, um die Token-Trennung beizubehalten
        return " " * (match.end() - match.start())
    
    # ------------------------------------------------
    # Validiert die Struktur der Tokens basierend
    # auf einer JSON-Vorlage.
    # ------------------------------------------------
    def validate_structure(self, grammar, start_index=0):
        try:
            structure = json.loads(grammar)
        except json.JSONDecodeError as e:
            self.errors.append((0, 0, f"JSON-Fehler in der Grammatik: {str(e)}"))
            return False, start_index

        sequence = structure.get("sequence", [])
        repeated = structure.get("repeated", [])
        token_index = start_index

        # Überprüfe die Sequenz
        for expected in sequence:
            if token_index >= len(self.tokens):
                self.errors.append((0, 0, f"Fehlendes Token: {expected}"))
                return False, token_index

            line, pos, token, token_type = self.tokens[token_index]

            # Überprüfe Typ und optionalen Wert
            if token_type != expected["type"]:
                self.errors.append((line, pos, f"Erwarteter Typ '{expected['type']}', gefunden '{token_type}'."))
                return False, token_index
            if "value" in expected and token.upper() != expected["value"]:
                self.errors.append((line, pos, f"Erwarteter Wert '{expected['value']}', gefunden '{token}'."))
                return False, token_index

            token_index += 1

        # Überprüfe wiederholte Abschnitte
        for repeat_section in repeated:
            while token_index < len(self.tokens):
                line, pos, token, token_type = self.tokens[token_index]

                # Prüfe, ob das Token dem Beginn des wiederholbaren Abschnitts entspricht
                if token_type == repeat_section["type"] and token.upper() == repeat_section["value"]:
                    token_index += 1  # Überspringe das Schlüsselwort (z. B. "VAR")

                    # Überprüfe die Deklarationen in diesem Abschnitt
                    for declaration in repeat_section["declarations"]:
                        if not isinstance(declaration, dict) or "type" not in declaration:
                            self.errors.append((line, pos, f"Ungültige Deklaration in der Grammatik: {declaration}"))
                            return False, token_index

                        if token_index >= len(self.tokens):
                            self.errors.append((line, pos, f"Fehlendes Token für Deklaration: {declaration}"))
                            return False, token_index

                        line, pos, token, token_type = self.tokens[token_index]

                        # Überprüfe Typ und optionalen Wert
                        if token_type != declaration["type"]:
                            self.errors.append((line, pos, f"Erwarteter Typ '{declaration['type']}', gefunden '{token_type}'."))
                            return False, token_index
                        if "value" in declaration and token.upper() != declaration["value"]:
                            self.errors.append((line, pos, f"Erwarteter Wert '{declaration['value']}', gefunden '{token}'."))
                            return False, token_index

                        token_index += 1

                    # Optionaler Abschnitt für Mehrfachdeklarationen
                    while token_index < len(self.tokens):
                        line, pos, token, token_type = self.tokens[token_index]

                        if token_type == "symbol" and token == ",":
                            token_index += 1  # Überspringe Komma

                            # Erwarte einen weiteren Bezeichner
                            if token_index < len(self.tokens) and self.tokens[token_index][3] == "ident":
                                token_index += 1
                            else:
                                self.errors.append((line, pos, "Fehlender Bezeichner nach ','."))
                                return False, token_index
                        else:
                            break
                else:
                    break  # Kein weiteres Schlüsselwort gefunden

        return True, token_index
    
    # -------------------------------------------
    # Konvertiert den Pascal-Code in Python-Code.
    # -------------------------------------------
    def convert_to_python(self, parsed_program):
        pass
        
class dBaseParser:
    def __init__(self, script_name):
        self.script_name = script_name
        self.line_number = 0
        self.start_line  = 0
        
        # -----------------------------------
        # Muster für einzeilige Kommentare
        # -----------------------------------
        self.single_line_patterns = [r"&&.*", r"\*\*.*", r"//.*"]
        self.single_line_regex    = re.compile("|".join(
        self.single_line_patterns))
        
        # -----------------------------------
        # Muster für mehrzeilige Kommentare
        # -----------------------------------
        self.multi_line_start_patterns = [r"\/\*"]
        self.multi_line_end_patterns   = [r"\*\/"]
        
        self.multi_line_start_regex    = re.compile("|".join(self.multi_line_start_patterns))
        self.multi_line_end_regex      = re.compile("|".join(self.multi_line_end_patterns))
        
        self.comments = {
            "single_line": [],
            "multi_line" : [],
            "errors"     : []
        }
        
        self.line_number = 0
    
    def parse(self):
        with open(self.script_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            inside_multi_line_comment = False
            multi_line_comment = ""
            start_line = 0

            for line in lines:
                self.line_number += 1
                stripped_line = line.strip()
                
                # Einzeilige Kommentare suchen
                single_line_match = self.single_line_regex.findall(stripped_line)
                if single_line_match:
                    self.comments["single_line"].append((
                    self.line_number, single_line_match))
                
                # Mehrzeilige Kommentare verarbeiten
                if inside_multi_line_comment:
                    multi_line_comment += f"\n{stripped_line}"
                    if self.multi_line_end_regex.search(stripped_line):
                        # Überprüfen auf fehlerhafte Abschlüsse
                        if  multi_line_comment.count("/*") > multi_line_comment.count("*/"):
                            self.comments["errors"].append((
                            start_line, self.line_number,
                            "Unvollständiger Kommentarabschluss",
                            multi_line_comment))
                        else:
                            self.comments["multi_line"].append((
                            start_line,
                            self.line_number, multi_line_comment))
                        inside_multi_line_comment = False
                        multi_line_comment = ""
                else:
                    multi_line_start = self.multi_line_start_regex.search(stripped_line)
                    if multi_line_start:
                        inside_multi_line_comment = True
                        start_line = self.line_number
                        multi_line_comment = stripped_line
                        if self.multi_line_end_regex.search(stripped_line):
                            if stripped_line.count("/*") > stripped_line.count("*/"):
                                self.comments["errors"].append((
                                    start_line,
                                    self.line_number,
                                    "Unvollständiger Kommentarabschluss",
                                    stripped_line))
                            else:
                                self.comments["multi_line"].append((
                                    start_line,
                                    self.line_number,
                                    stripped_line))
                            inside_multi_line_comment = False
                            multi_line_comment = ""
        return self.comments

    def convert_to_python(self, parsed_program):
        python_code = []
        function_definitions = []

# ---------------------------------------------------------------------------
# \brief  class for interpreting DoxyGen related stuff ...
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
class interpreter_DoxyGen(interpreter_base):
    def __init__(self, file_name, parent_gui=None):
        super(interpreter_ISOC, self).__init__(file_name)
        self.script_name = file_name
        self.parent_gui  = parent_gui
            
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
        genv.line_col += 1
        self.pos += 1
        
        if self.pos >= len(self.source):
            raise ENoParserError("")
        else:
            genv.char_curr = self.source[self.pos]
            return genv.char_curr
    
    def ungetChar(self, num):
        genv.line_col -= num;
        self.pos -= num;
        genv.char_curr = self.source[self.pos]
        return genv.char_curr
    
    def getIdent(self, ch):
        self.token_str = ch
        while True:
            genv.char_curr = self.getChar()
            if genv.char_curr.isalnum() or genv.char_curr == '_':    # 0-9 todo
                self.token_str += genv.char_curr
                continue
            elif genv.char_curr == '\t' or genv.char_curr == ' ':
                continue
            elif genv.char_curr == '\r':
                genv.char_curr = self.getChar()
                if not genv.char_curr == '\n':
                    genv.unexpectedToken("newline")
                    return 0
                genv.line_col  = 1
                genv.line_row += 1
                break
            elif genv.char_curr == '\n':
                genv.line_col  = 1
                genv.line_row += 1
                break
            elif genv.char_curr == '=':
                self.ungetChar(1)
                break
            else:
                genv.unexpectedChar(genv.char_curr)
                return 0
        return self.token_str
    
    def getNumber(self):
        while True:
            genv.char_curr = self.getChar()
            if genv.char_curr in genv.octal_digits:
                self.token_str += octal_to_ascii(genv.char_curr)
            else:
                self.ungetChar(1)
                return self.token_str
    
    # -----------------------------------------------------------------------
    # \brief skip all whitespaces. whitespaces are empty lines, lines with
    #        one or more spaces (0x20): " ", \t, "\n".
    # -----------------------------------------------------------------------
    def skip_white_spaces(self):
        while True:
            genv.char_curr = self.getChar()
            if genv.char_curr == '\0':
                return '\0'
            elif genv.char_curr == "\t" or genv.char_curr == " ":
                genv.line_col += 1
                continue
            elif genv.char_curr == "\r":
                genv.char_curr = self.getChar()
                if not genv.char_curr == "\n":
                    genv.unexpectedEndOfLine(genv.line_row)
                genv.line_col  = 1
                genv.line_row += 1
                continue
            elif genv.char_curr == '\n':
                genv.line_col  = 1
                genv.line_row += 1
                continue
            elif genv.char_curr == '#':
                while True:
                    genv.char_curr = self.getChar()
                    if genv.char_curr == '\r':
                        genv.char_curr = self.getChar()
                        if not genv.char_curr == '\n':
                            genv.unexpectedToken("newline")
                            return 0
                        genv.line_col  = 1
                        genv.line_row += 1
                        break
                    elif genv.char_curr == "\n":
                        genv.line_col  = 1
                        genv.line_row += 1
                        break
                continue
            else:
                return genv.char_curr
    
    # -----------------------------------------------------------------------
    # \brief parse a one line comment: // for c++, ** and && for dBase ...
    # -----------------------------------------------------------------------
    def handle_oneline_comment(self):
        while True:
            genv.char_curr = self.getChar()
            if genv.char_curr == '\r':
                genv.char_curr = self.getChar()
                if not genv.char_curr == '\n':
                    genv.unexpectedToken("newline")
                    return 0
                genv.line_row += 1
                genv.line_col  = 1
                break
            if genv.char_curr == "\n":
                genv.line_row += 1
                genv.line_col  = 1
                break
    
    def parse(self):
        if len(self.source) < 1:
            DebugPrint("no data available.")
            return
        
        while True:
            genv.char_curr = self.getChar()
            if genv.char_curr.isalpha() or genv.char_curr == '_':
                self.getIdent(genv.char_curr)
                DebugPrint("token: ", self.token_str)
                if self.check_token():
                    DebugPrint("OK")
            elif genv.char_curr == '\r':
                genv.char_curr = self.getChar()
                if not genv.char_curr == '\n':
                    genv.unexpectedToken("newline")
                    return 0
                genv.line_row += 1
                genv.line_col  = 1
                continue
            elif genv.char_curr == '\n':
                genv.line_row += 1
                genv.line_col  = 1
                continue
            elif genv.char_curr == '\t' or genv.char_curr == ' ':
                continue
            elif genv.char_curr == '#':
                self.handle_oneline_comment()
    
    def getConfigLine(self):
        self.token_str = ""
        self.close_str = False
        while True:
            genv.char_curr = self.getChar()
            if genv.char_curr == '"':
                while True:
                    genv.char_curr = self.getChar()
                    if genv.char_curr == '"':
                        self.close_str = True
                        break
                    elif genv.char_curr == '\r':
                        genv.char_curr = self.getChar()
                        if not genv.char_curr == '\n':
                            genv.unexpectedToken("newline")
                            return 0
                        else:
                            if self.close_str == False:
                                genv.unexpectedToken(_("string not terminated."))
                                return 0
                            genv.line_col  = 1
                            genv.line_row += 1
                            break
                    elif genv.char_curr == '\n':
                        if self.close_str == False:
                            genv.unexpectedToken(_("string not terminated."))
                            return 0
                        genv.line_col  = 1
                        genv.line_row += 1
                        break
                    else:
                        self.token_str += c
                if self.close_str:
                    continue
                else:
                    genv.unexpectedToken(_("string not terminated."))
                    return 0
            elif genv.char_curr == '\t' or genv.char_curr == ' ':
                genv.line_col += 1
                continue
            elif genv.char_curr == '\r':
                genv.char_curr = self.getChar()
                if not genv.char_curr == '\n':
                    genv.unexpectedToken("newline")
                    return 0
                genv.line_col  = 1
                genv.line_row += 1
                break
            elif genv.char_curr == '\n':
                genv.line_col  = 1
                genv.line_row += 1
                break
            elif genv.char_curr.isdigit():
                self.token_str += c
                continue
            elif genv.char_curr.isalpha():
                self.token_str += c
                while True:
                    genv.char_curr = self.getChar()
                    if genv.char_curr.isalpha():
                        self.token_str += genv.char_curr
                        continue
                    elif genv.char_curr.isdigit():
                        self.token_str += genv.char_curr
                        continue
                    elif genv.char_curr == '\t' or genv.char_curr == ' ':
                        continue
                    elif genv.char_curr == '\r':
                        genv.char_curr = self,getChar()
                        if not genv.char_curr == '\n':
                            genv.unexpectedToken("newline")
                            return 0
                        genv.line_col  = 1
                        genv.line_row += 1
                        break
                    elif genv.char_curr == '\n':
                        genv.line_col  = 1
                        genv.line_row += 1
                        break
                if genv.char_curr == '\n':
                    break
            else:
                genv.unexpectedToken("qoute")
                return 0
    
    def check_token(self):
        res = json.loads(_("doxytoken"))
        result = False
        if self.token_str in res:
            DebugPrint(f"token: {self.token_str} is okay.")
            result = True
            genv.char_curr = self.getChar()
            if genv.char_curr == '=':
                self.token_prop = self.token_str
                self.token_str = ""
                self.getConfigLine()
                
                myobject = findWidgetHelper(
                    self.parent_gui,
                    self.token_prop,
                    self.token_str , False, [
                    f"Error: no control for: {self.token_prop}.",
                    f"Error: no content given for: {self.token_prop}."
                ])
                if isinstance(myobject, QCheckBox):
                    if self.token_str.lower() == "yes":
                        myobject.setChecked(True)
                    elif self.token_str.lower() == "no":
                        myobject.setChecked(False)
                    else:
                        genv.unexpectedToken("for checkbox")
                        return 0
                if isinstance(myobject, QLineEdit):
                    myobject.setText(self.token_str)
                return
            else:
                genv.unexpectedChar(c)
        else:
            raise EInvalidParserError(self.token_str)
            return False

class doxygenDSL:
    def __init__(self, script_name, parent_gui):
        self.parent_gui = parent_gui
        try:
            self.parser = interpreter_DoxyGen(script_name, parent_gui)
            self.parser.parse()
            #prg.run()
        except ENoParserError as noerror:
            #prg.finalize()
            DebugPrint("\nend of data")
            chm = createHTMLproject()
    
    def parse(self):
        return
    
    def run(self):
        return

# ------------------------------------------------------------------------
# methode to show information about this application script ...
# ------------------------------------------------------------------------
def showApplicationInformation(text):
    if isApplicationInit() == False:
        genv.v__app_object = QApplication(sys.argv)
        showInfo(text)
    else:
        DebugPrint(text)

# ------------------------------------------------------------------------
# methode to show error about this application script ...
# ------------------------------------------------------------------------
def showApplicationError(text):
    if isApplicationInit() == False:
        genv.v__app_object = QApplication(sys.argv)
        showError(text)
    else:
        DebugPrint(text)

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
        DebugPrint("no ption error")
        #genv.v__app__locales = os.path.join(genv.v__app__locales, genv.v__locale__sys[0])
        #genv.v__app__locales = os.path.join(genv.v__aoo__locales, "LC_MESSAGES")
        #genv.v__app__locales = os.path.join(genv.v__app__locales, genv.v__app__name_mo)
    except ListInstructionError as ex:
        ex.add_note("Did you miss a parameter ?")
        ex.add_note("Add more information.")
        DebugPrint("List instructions error.")
        error_result = 1
    except ZeroDivisionError as ex:
        ex.add_note("1/0 not allowed !")
        DebugPrint("Handling run-time error:", ex)
        error_result = 1
    except OSError as ex:
        DebugPrint("OS error:", ex)
        error_result = 1
    except ValueError as ex:
        DebugPrint("Could not convert data:", ex)
        error_result = 1
    except Exception as ex:
        exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
        tb = traceback.extract_tb(ex.__traceback__)[-1]
        
        DebugPrint(f"Exception occur:")
        DebugPrint(f"type : {exc_type.__name__}")
        DebugPrint(f"value: {exc_value}")
        DebugPrint(("-"*40))
        #
        DebugPrint(f"file : {tb.filename}")
        DebugPrint(f"line : {tb.lineno}")
        #
        DebugPrint(("-"*40))
        
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
        DebugPrint(ex)
    finally:
        # ---------------------------------------------------------
        # when all is gone, stop the running script ...
        # ---------------------------------------------------------
        if error_result > 0:
            DebugPrint("abort.")
            sys.exit(error_result)
        
        DebugPrint("Done.")
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
# \brief  search the application instance for all widgets. If a given
#         widget is found, then return True; else False
# ------------------------------------------------------------------------
class widgetTypeHelper():
    def __init__(self, object_name, object_type, object_widget):
        self.object_name   = object_name
        self.object_type   = object_type
        self.object_widget = object_widget

class findWidgetHelper():
    def __init__(self, parent, key, value, verify, messages):
        try:
            for item in genv.DoxyGenElementLayoutList:
                text = item.objectName().split(':')
                if text[0] == key:
                    if isinstance(item, QLineEdit):
                        item.setText(value)
            return
        except Exception as e:
            DebugPrint(e)

# ------------------------------------------------------------------------
#
# ------------------------------------------------------------------------
class myLineEdit(QLineEdit):
    def __init__(self, name="", name_object="", callback=None):
        super(myLineEdit, self).__init__()
        
        self.callback = callback
        if name_object:
            self.setObjectName(name_object)
            self.callback = callback
            #register_instance(self, name_object)
            print(">> " + self.objectName())
        
        self.name = name
        self.init_ui()
    
    def init_ui(self):
        self.setMinimumHeight(26)
        self.setMaximumWidth(250)
        self.setText(self.name)
        self.cssColor = _("edit_css")
        self.setStyleSheet(self.cssColor)
    
    def mouseDoubleClickEvent(self, event):
        if not self.callback == None:
            self.callback()

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
            if self.mode == 0:
                genv.devices_scroll.hide()
                genv.cpuview_scroll.hide()
                genv.servers_scroll.setParent(parent.front_content_widget)
                genv.servers_scroll.show()
            if self.mode == 11:
                genv.devices_scroll.hide()
                genv.servers_scroll.hide()
                genv.cpuview_scroll.show()
            else:
                genv.servers_scroll.hide()
                genv.cpuview_scroll.hide()
                #genv.servers_scroll.setParent(parent.front_content_widget)
                #genv.devices_scroll.show()
            
            self.btn_clicked(self.parent,
            genv.parent_array[self.mode])
            genv.active_side_button = self.mode
    
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
        parent.javascript_tabs.hide()
        parent.python_tabs.hide()
        parent.prolog_tabs.hide()
        parent.fortran_tabs.hide()
        parent.lisp_tabs.hide()
        parent.basic_tabs.hide()
        parent.pe_windows_tabs.hide()
        parent.elf_linux_tabs.hide()
        parent.console_tabs.hide()
        parent.locale_tabs.hide()
        parent.todo_tabs.hide()
        parent.setup_tabs.hide()
        parent.certssl_tabs.hide()
        parent.github_tabs.hide()
        parent.apache_tabs.hide()
        parent.mysql_tabs.hide()
        parent.squid_tabs.hide()
        parent.electro_tabs.hide()
        parent.c64_tabs.hide()
        parent.settings_tabs.hide()
    
    def btn_clicked(self,btn,tabs):
        if not genv.worker_thread == None:
            genv.worker_thread.stop()
            genv.worker_thread = None
        
        self.hide_tabs()
        parent = self.parent.parent
        
        genv.splitter.addWidget(tabs)
        genv.splitter.addWidget(genv.servers_scroll)
        
        parent.front_content_layout.addWidget(genv.splitter)
        tabs.show()
        
        genv.servers_scroll.show()
        
        self.set_null_state()
        btn.state = 2
        btn.set_style()
    
    def set_null_state(self):
        parent = self.parent.parent
        side_buttons = [
            parent.side_btn0,
            parent.side_btn1,
            parent.side_btn2,
            parent.side_btn3,
            parent.side_btn4,
            parent.side_btn5,
            parent.side_btn6,
            parent.side_btn7,
            parent.side_btn8,
            parent.side_btn9,
            parent.side_btn10,
            parent.side_btn11,
            parent.side_btn12,
            parent.side_btn13,
            parent.side_btn14,
            parent.side_btn15,
            parent.side_btn16,
            parent.side_btn17,
            parent.side_btn18,
            parent.side_btn19,
            parent.side_btn20,
            parent.side_btn21,
            parent.side_btn22,
            parent.side_btn23,
            parent.side_btn24
        ]
        for btn in side_buttons:
            btn.state = 0
            btn.set_style()

class myIconButton(QWidget):
    def __init__(self, parent, mode, label_text, text):
        super().__init__()
        
        genv.v__app__devmode    = mode
        
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
        
        img_array = [
            genv.v__app__helpdev__,
            genv.v__app__dbasedb__,
            genv.v__app__freepas__,
            genv.v__app__cpp1dev__,
            genv.v__app__javadev__,
            genv.v__app__javascr__,
            genv.v__app__pythonc__,
            genv.v__app__prologm__,
            genv.v__app__fortran__,
            genv.v__app__lispmod__,
            genv.v__app__basicbe__,
            genv.v__app__pewin32__,
            genv.v__app__elfin32__,
            genv.v__app__console__,
            genv.v__app__locales__,
            genv.v__app__todopro__,
            genv.v__app__setupro__,
            genv.v__app__certssl__,
            genv.v__app__githubp__,
            genv.v__app__apache2__,
            genv.v__app__mysqlcf__,
            genv.v__app__squidwp__,
            genv.v__app__electro__,
            genv.v__app__com_c64__,
            genv.v__app__com_set__
        ]
        for idx in img_array:
            m = img_array.index(idx)
            if mode == m:
                genv.active_side_button = m
                
                self.image_fg = ptx + img_array[m] + fg
                self.image_bg = ptx + img_array[m] + bg
        
        self.set_style()
    
    def set_style(self):
        if self.state == 2:
            self.bordercolor = "lime"
        else:
            self.bordercolor = "lightgray"
        
        self.image_fg = self.image_fg.replace("\\", "/")
        self.image_bg = self.image_bg.replace("\\", "/")
        
        style = _("labelico_css")        \
        .replace("{fg}", self.image_fg)  \
        .replace("{bg}", self.image_bg)  \
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
        self.helpText   = _(helpText.replace('A', ''))
        
        self.helpToken  = _(f"{helpID:04X}")
        print("---> " + self.helpToken)
        self.helpAnchor = 'https://doxygen.nl/manual/config.html#cfg_' + self.helpToken.lower()
    
    def enterEvent(self, event):
        if genv.sv_help == None:
            genv.sv_help = customScrollView_help()
            genv.sv_help.setStyleSheet(_("ScrollBarCSS"))
        
        genv.sv_help.setText(self.helpText)
    
    def mousePressEvent(self, event):
        QApplication.setOverrideCursor(Qt.PointingHandCursor)
        return
    
    def mouseReleaseEvent(self, event):
        QDesktopServices.openUrl(QUrl(self.helpAnchor))
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        return

class addRadioButton(QRadioButton):
    def __init__(self, object_name="", text=""):
        super().__init__()
        
        self.setObjectName(object_name)
        self.setText(text)
        self.setFont(QFont("Arial",10))
 
class addCheckBox(QCheckBox):
    def __init__(self, object_name = "", text = "", bold=False):
        super().__init__()
        
        self.setObjectName(object_name)
        self.setText(text)
        
        self.setFont(QFont("Arial",10))
        self.font().setBold(bold)

class myCustomScrollArea(QScrollArea):
    def __init__(self, number, hid, name):
        super().__init__()
        
        self.number = number
        self.name   = name
        self.hid    = hid
        
        self.font   = QFont(genv.v__app__font)
        self.font.setPointSize(10)
        
        self.setWidgetResizable(True)
        
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
        self.content_widget.setMinimumWidth (self.width()-150)
        self.content_widget.setFont(self.font)
        
        self.layout = QVBoxLayout(self.content_widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.label_1 = QLabel(self.name)
        
        self.layout.addWidget(self.label_1)
        self.content_widget.setLayout(self.layout)
        
        self.setWidget(self.content_widget)
        
    def setName(self, name):
        self.name = name
        self.label_1.setText(self.name)
    
    def setElementBold(self, w):
        self.font.setBold(True); w.setFont(self.font)
        self.font.setBold(False)
        
    def addPushButton(self, text, l=None):
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
    
    def addComboBox(self, object_name = ""):
        w = QComboBox()
        w.setObjectName(object_name + ':QComboBox')
        self.layout.addWidget(w)
        return w
    
    def addLineEdit(self, callback=None, object_name = "", text = "", lh = None):
        w = myLineEdit(text, object_name, callback)
        w.setMinimumHeight(21)
        w.setFont(self.font_a)
        if not lh == None:
            lh.addWidget(w)
        else:
            self.layout.addWidget(w)
        return w
    
    def el_check_box_on_click(self):
        sender_object_name = self.sender().objectName().lower()
        sender_object      = self.sender()
        
        if sender_object.isChecked():
            sender_object.setText(" YES 1")
            setattr(genv, f"doc_{sender_object_name}", 1)
            genv.save_config_file()
            #showInfo("einser: " + str(getattr(genv, f"genv.doc_{sender_object_name}", 3)))
        else:
            sender_object.setText(" NO")
            setattr(genv, f"doc_{sender_object_name}", 0)
            genv.save_config_file()
            #showInfo("nuller: " + str(getattr(genv, f"doc_{sender_object_name}", 5)))
        
        #genv.v__app_win.write_config_part()
    
    def addElements(self, number, elements, hid):
        elements = eval(elements)
        for i in elements:  #range(0, len(elements)):
            lv_0 = QVBoxLayout()
            lh_0 = QHBoxLayout()
            
            h = ("h" + hex(i[0]).upper())
            h = h.replace('0XA', '')
            
            helpID   = i[0]
            helpText = _("h" + f"{helpID:04X}")
            tokennum = _(f"{helpID:04X}")
            
            vw_1 = self.addHelpLabel(
                tokennum,
                helpID,
                helpText,
                lh_0)
            vw_1.setMinimumHeight(14)
            vw_1.setMinimumWidth(200)
            
            doc0 = ("doc_" + tokennum.lower())
            setattr(genv, doc0, "0")
            
            if i[1] == genv.type_edit:
                w = self.addLineEdit(None, tokennum, "",lh_0)
                w.setObjectName(doc0)
                genv.DoxyGenElementLayoutList.append(w)
                #
                setattr(genv, doc0 + "_object", w)
                setattr(genv, doc0 + "_type"  , genv.type_edit)
                
                if i[2] == 1:
                    self.addPushButton("+",lh_0)
                
                elif i[2] == 3:
                    vw_3 = myTextEdit()
                    vw_3.setObjectName(doc0)
                    #
                    setattr(genv, doc0 + "_object", vw_3)
                    setattr(genv, doc0 + "_source", w)
                    setattr(genv, doc0 + "_type",   genv.type_textedit)
                    
                    p1 = self.addPushButton("+",lh_0)
                    p1.clicked.connect(self.addText2Edit)
                    p1.setObjectName(doc0)
                    
                    p2 = self.addPushButton("-",lh_0)
                    p2.clicked.connect(self.delText2Edit)
                    p2.setObjectName(doc0)
                    
                    p3 = self.addPushButton("R",lh_0)
                    p3.clicked.connect(self.clrText2Edit)
                    p3.setObjectName(doc0)
                    
                    vw_3.setFont(self.font_a)
                    vw_3.setMinimumHeight(96)
                    vw_3.setMaximumHeight(96)
                    
                    lv_0.addWidget(vw_3)
                    
            elif i[1] == genv.type_check_box:
                vw_2 = addCheckBox(tokennum, "", False)
                vw_2.setMinimumHeight(21)
                vw_2.setFont(self.font_a)
                vw_2.setChecked(i[3])
                vw_2.clicked.connect(self.el_check_box_on_click)
                
                #
                doc0 = ("doc_" + tokennum.lower())
                setattr(genv, doc0 + "_object", vw_2)
                setattr(genv, doc0 + "_type"  , genv.type_check_box)
                
                if vw_2.isChecked():
                    setattr(genv, doc0, 1)
                    vw_2.setText(_(" YES"))
                else:
                    setattr(genv, doc0, 0)
                    vw_2.setText(_(" NO"))
                #
                lh_0.addWidget(vw_2)
                
            elif i[1] == genv.type_combo_box:
                vw_2 = self.addComboBox(tokennum)
                vw_2.setMinimumHeight(26)
                vw_2.setFont(self.font)
                vw_2.font().setPointSize(14)
                lh_0.addWidget(vw_2)
                #
                doc0 = ("doc_" + tokennum.lower())
                setattr(genv, doc0 + "_object", vw_2)
                setattr(genv, doc0 + "_type"  , genv.type_combo_box)
                
                if i[2] == 4:
                    data = json.loads(self.supported_langs)
                    i[3] = data
                    for j in range(0, len(data)):
                        img = os.path.join(genv.v__app__img__int__, "flag_"  \
                        + i[3][j]    \
                        + genv.v__app__img_ext__)
                        img = img.lower()
                        
                        vw_2.addItem(QIcon(img), i[3][j-1])
                        #vw_2.setStyleSheet("""
                        #QComboBox QAbstractItemView {
                        #    selection-background-color: lightGray;
                        #    selection-color: black;
                        #    color: black;
                        #}
                        #""")
                    
                #elif i[2] == 2:
                #    for j in range(0, len(elements[i][3])):
                #        vw_2.addItem(elements[i][3][j])
                #    #return 4000
            
            elif i[1] == genv.type_spin:
                vw_2 = QSpinBox()
                vw_2.setObjectName(tokennum)
                vw_2.setFont(self.font_a)
                vw_2.setMinimumHeight(21)
                lh_0.addWidget(vw_2)
                #
                doc0 = ("doc_" + tokennum.lower())
                setattr(genv, doc0 + "_object", vw_2)
                setattr(genv, doc0 + "_type"  , genv.type_spin)
            
            lv_0.addLayout(lh_0)
            self.layout.addLayout(lv_0)
            
            #print("tokennum: " + tokennum)
            #print("helpID:   " + helpID)
            
        return True
        
    def addText2Edit(self):
        obj_name1 = self.sender().objectName() + "_object"
        obj_name2 = self.sender().objectName() + "_source"
        
        obj_dst  = getattr(genv, obj_name1)
        obj_src  = getattr(genv, obj_name2)
        
        if len(obj_src.text().strip()) < 1:
            showInfo(_("Error:\nsource input line is empty."))
            return False
        
        obj_dst.insertPlainText(obj_src.text() + "\r\n")
        return True
    
    def delText2Edit(self):
        obj_name1 = self.sender().objectName() + "_object"
        edit_box  = getattr(genv, obj_name1)
        
        text     = edit_box.toPlainText()
        lines    = text.splitlines()
        
        try:
            if len(lines) > 0:
                cursor = edit_box.textCursor()
                current_line = cursor.blockNumber()
                del lines[current_line]
                
        except IndexError:
            showInfo(_("Warning:\nIndex out of bounds.\nDid you set the right focus ?"))
            return False
            
        edit_box.setPlainText("\n".join(lines))
        return True
        
    def clrText2Edit(self):
        obj_name1 = self.sender().objectName() + "_object"
        edit_box  = getattr(genv, obj_name1)
        edit_box.setPlainText("")
        return True

# ------------------------------------------------------------------------
# create a scroll view for the project tab on left side of application ...
# ------------------------------------------------------------------------
class customScrollView_1(myCustomScrollArea):
    def __init__(self, parent, number, hid, name="uuuu"):
        super(customScrollView_1, self).__init__(number, hid, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        
        self.parent = parent
        self.name   = name
        print("1111")
        self.init_ui()
    
    def init_ui(self):
        content_widget = QWidget(self)
        content_widget.setMaximumWidth(500)
        
        layout = QVBoxLayout(content_widget)
        layout.setAlignment(Qt.AlignLeft)
        
        font = QFont("Consolas", 10)
        
        w_layout_0 = QHBoxLayout()
        w_layout_0.setAlignment(Qt.AlignLeft)
        widget_1_label_1 = self.addLabel(_("Provide some informations about the Project you are documenting"), True)
        widget_1_label_1.setMinimumWidth(250)
        widget_1_label_1.setMaximumWidth(450)
        w_layout_0.addWidget(widget_1_label_1)
        layout.addLayout(w_layout_0)
        
        h_layout_1 = QHBoxLayout()
        h_widget_1 = QWidget()
        #h_widget_1.setMinimumWidth(300)
        
        v_layout_1 = QVBoxLayout()
        v_widget_1 = QWidget()
        
        l_label_1 = self.addLabel(_("Project name:")          , False, v_layout_1)
        l_label_2 = self.addLabel(_("Project author:")        , False, v_layout_1)
        l_label_3 = self.addLabel(_("Project version or id: "), False, v_layout_1)
        
        l_label_1.setFont(font)
        l_label_2.setFont(font)
        l_label_3.setFont(font)
        ##
        v_layout_2 = QVBoxLayout()
        v_widget_2 = QWidget()
        
        e_field_1 = self.addLineEdit(None, "doxygen_project_name"  , "", v_layout_2)
        e_field_2 = self.addLineEdit(None, "doxygen_project_author", "", v_layout_2)
        e_field_3 = self.addLineEdit(None, "doxygen_project_number", "", v_layout_2)
        
        ##
        h_layout_1.addLayout(v_layout_1)
        h_layout_1.addLayout(v_layout_2)
        
        layout.addLayout(h_layout_1)
        
        
        layout_4 = QHBoxLayout()
        layout_4.setAlignment(Qt.AlignLeft)
        widget_4_label_1 = self.addLabel(_("Project logo:"), False, layout_4)
        widget_4_label_1.setFont(font)
        widget_4_label_1.setMaximumWidth(160)
        layout_4.addWidget(widget_4_label_1)
        #
        widget_4_pushb_1 = self.addPushButton(_("Select"), layout_4)
        widget_4_pushb_1.setMinimumHeight(32)
        widget_4_pushb_1.setMinimumWidth(84)
        widget_4_pushb_1.setMaximumWidth(84)  ; font.setBold(True)
        widget_4_pushb_1.setFont(font)        ; font.setBold(False)
        
        widget_4_pushb_1.clicked.connect(self.widget_4_pushb_1_click)
        #
        pixmap_name = os.path.join(genv.v__app__img__int__, "floppy-disk" + genv.v__app__img_ext__)
        
        widget_4_licon_1 = self.addLabel("", False, layout_4)
        widget_4_licon_1.setObjectName("doxygen_project_logo")
        widget_4_licon_1.setPixmap(QIcon(pixmap_name)
                        .pixmap(42,42))
        widget_4_licon_1.pixmap_name = pixmap_name
        
        #widget_4_licon_1.setObjectName("PROJECT_LOGO:1")
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
        widget_6_label_1 = self.addLabel(_("Source dir:"), False, layout_6)
        widget_6_label_1.setMinimumWidth(100)
        widget_6_label_1.setMaximumWidth(100)
        widget_6_label_1.setFont(font)
        #
        widget_6_edit_1  = self.addLineEdit(
            self.widget_6_edit_1_dblclick,
            "doxygen_project_srcdir",
            os.path.join(
            genv.v__app__app_dir__,
                "/examples/doxygen/"),
            layout_6)
        widget_6_edit_1.setMinimumWidth(280)
        widget_6_edit_1.setMaximumWidth(280)
        widget_6_edit_1.setFont(font)
        #
        widget_6_pushb_1 = self.addPushButton(_("Select"), layout_6)
        widget_6_pushb_1.setMinimumHeight(40)
        widget_6_pushb_1.setMaximumHeight(40)
        widget_6_pushb_1.setMinimumWidth(84)
        widget_6_pushb_1.setMaximumWidth(84) ; font.setBold(True)
        widget_6_pushb_1.setFont(font)       ; font.setBold(False)
        
        widget_6_pushb_1.clicked.connect(self.widget_6_pushb_1_click)
        ##
        layout.addLayout(layout_6)
        
        layout_7 = QHBoxLayout()
        layout_7.setAlignment(Qt.AlignLeft)
        widget_7_label_1 = self.addLabel(_("Destination dir:"), False, layout_7)
        widget_7_label_1.setMinimumWidth(100)
        widget_7_label_1.setMaximumWidth(100)
        widget_7_label_1.setFont(font)
        #
        widget_7_edit_1  = self.addLineEdit(
            self.widget_7_edit_1_dblclick,
            "doxygen_project_dstdir",
            "E:/temp/src/html",
            layout_7)
            
        widget_7_edit_1.setMinimumWidth(280)
        widget_7_edit_1.setMaximumWidth(280)
        widget_7_edit_1.setFont(font)
        #
        widget_7_pushb_1 = self.addPushButton(_("Select"), layout_7)
        widget_7_pushb_1.setMinimumHeight(40)
        widget_7_pushb_1.setMaximumHeight(40)
        widget_7_pushb_1.setMinimumWidth(84)
        widget_7_pushb_1.setMaximumWidth(84) ; font.setBold(True)
        widget_7_pushb_1.setFont(font)       ; font.setBold(False)
        
        widget_7_pushb_1.clicked.connect(self.widget_7_pushb_1_click)
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

        widget_9_checkbutton_1 = addCheckBox("doxygen_project_scan_recursiv",_("Scan recursive"))
        widget_9_checkbutton_1.setMaximumWidth(300)
        widget_9_checkbutton_1.setFont(font)
        
        layout_9.addWidget(widget_9_checkbutton_1)
        layout  .addLayout(layout_9)
        
        layout_10 = QVBoxLayout()
        widget_10_button_1 = QPushButton(_("Convert") ,self); widget_10_button_1.setStyleSheet(_(genv.css_button_style))
        widget_10_button_2 = QPushButton(_("HelpNDoc"),self); widget_10_button_2.setStyleSheet(_(genv.css_button_style))
        
        widget_10_button_1.clicked.connect(self.widget_10_button_1_click)
        #
        layout_10.addWidget(widget_10_button_1)
        layout_10.addWidget(widget_10_button_2)
        #
        layout.addLayout(layout_10)
        
        #self.setWidgetResizable(False)
        self.setWidget(content_widget)
    
    def widget_6_edit_1_dblclick(self):
        if genv.HelpAuthoringConverterMode == 0:
            dialog  = QFileDialog()
            
            dialog.setOption(QFileDialog.DontUseNativeDialog, True)
            dialog.setOption(QFileDialog.ShowDirsOnly, True)
            
            options         = dialog.options()
            genv.doc_srcdir = dialog.getExistingDirectory(
                None,
                _("Select source directory"),
                options=options)
            
            if len(genv.doc_srcdir.strip()) < 1:
                showError(_("Error:\ncould not select source directory."))
                return False
                
            item = self.findChild(myLineEdit, "doxygen_project_srcdir")
            if not item:
                showError(_("Error:\ncould not found source directory object."))
                return False
            
            if "_internal" in genv.doc_dstdir \
            or "_internal" in genv.doc_srcdir:
                showError(_("Error:\n_internal dir tree can not be delete."))
                _internal = True
                item.setText("")
                return False
            else:
                item.setText(genv.doc_srcdir)
                genv.v__app_win.write_config_part()
                return True
    
    def widget_7_edit_1_dblclick(self):
        if genv.HelpAuthoringConverterMode == 0:
            dialog  = QFileDialog()
            
            dialog.setOption(QFileDialog.DontUseNativeDialog, True)
            dialog.setOption(QFileDialog.ShowDirsOnly, True)
            
            options         = dialog.options()
            genv.doc_dstdir = dialog.getExistingDirectory(
                None,
                _("Select target directory"),
                options=options)
            
            if len(genv.doc_dstdir.strip()) < 1:
                showError(_("Error:\ncould not select target directory."))
                return False
                
            item = self.findChild(myLineEdit, "doxygen_project_dstdir")
            if not item:
                showError(_("Error:\ncould not found source directory object."))
                return False
            
            if "_internal" in genv.doc_dstdir \
            or "_internal" in genv.doc_srcdir:
                showError(_("Error:\n_Internal dir tree can not be delete."))
                _internal = True
                item.setText("")
                return False
            
            if len(genv.doc_dstdir.split()) < 1:
                showError(_("Error:\ndirectory string is empty."))
                return False
            else:
                item.setText(genv.doc_dstdir)
                genv.v__app_win.write_config_part()
                return True
                
            #item.setText(genv.doc_dstdir)
            #genv.doc_dstdir = item.text()
            #genv.v__app_win.write_config_part()
            
            return True
                
    def widget_4_pushb_1_click(self):
        if genv.HelpAuthoringConverterMode == 0:
            dialog       = QFileDialog()
            dialog.setOption(QFileDialog.DontUseNativeDialog, True)
            options      = dialog.options()
            file_filter  = "PNG Picture (*.png);;All Files (*)"
            file_name, p = dialog.getOpenFileName(
                None,
                _("Select Picture"),
                "",
                file_filter,
                options=options
            )
            if file_name:
                item = self.findChild(QLabel, "doxygen_project_logo")
                if item:
                    pixa = QPixmap(file_name)
                    item.setPixmap(pixa)
                else:
                    showError(_("Error:\nlogo pixmap object not found."))
                    return False
            else:
                showError(_("Error:\ncould not select picture"))
                return False
            return True
        
    def widget_6_pushb_1_click(self):
        if genv.HelpAuthoringConverterMode == 0:
            dialog = QFileDialog()
            
            dialog.setOption(QFileDialog.DontUseNativeDialog, True)
            dialog.setOption(QFileDialog.ShowDirsOnly, True)
            
            options         = dialog.options()
            genv.doc_srcdir = dialog.getExistingDirectory(
                None,
                _("Select directory"),
                options=options)
                
            if not genv.doc_srcdir:
                showError(_("Error:\ncould not select source directory"))
                return False
                
            item = self.findChild(myLineEdit, "doxygen_project_srcdir")
            if not item:
                showError(_("Error:\ncould not found source directory object."))
                return False
            
            if "_internal" in genv.doc_srcdir:
                showError(_("Error:\n_Internal dir tree can not be delete."))
                _internal = True
                item.setText("")
                return False
                
            item.setText(genv.doc_srcdir)
            return True
            
    def widget_7_pushb_1_click(self):
        if genv.HelpAuthoringConverterMode == 0:
            dialog = QFileDialog()
            dialog.setOption(QFileDialog.DontUseNativeDialog, True) 
            
            dialog = QFileDialog()
            
            dialog.setOption(QFileDialog.DontUseNativeDialog, True)
            dialog.setOption(QFileDialog.ShowDirsOnly, True)
            
            options         = dialog.options()
            genv.doc_dstdir = dialog.getExistingDirectory(
                None,
                _("Select directory"),
                options=options)
            
            if not genv.doc_dstdir:
                showError(_("Error:\ncould not select directory"))
                return False
            
            item = self.findChild(myLineEdit, "doxygen_project_dstdir")
            if not item:
                showError(_("Error:\ncould not found target directory object."))
                return False
            
            if "_internal" in genv.doc_dstdir:
                showError(_("Error:\n_Internal dir tree can not be delete."))
                _internal = True
                item.setText("")
                return False
                
            item.setText(genv.doc_dstdir)
            return True
    
    def widget_10_button_1_click(self):
        if genv.HelpAuthoringConverterMode == 0:
            msg = QMessageBox()
            msg.setWindowTitle(_("Error"))
            msg.setText(_("no project type given.\n"
            + "currently only DOXYGEN and HELPNDOC"))
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(_("msgbox_css"))
            
            btn_ok = msg.addButton(QMessageBox.Ok)
            result = msg.exec_()            
            return False
        if len(genv.doxygen_project_file) < 2:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText(_("no project file given."))
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(_("msgbox_css"))
            
            btn_ok = msg.addButton(QMessageBox.Ok)
            result = msg.exec_()            
            return False
        
        try:
            genv.v__app__config.read(genv.doxygen_project_file)
            if 'doxygen' in genv.v__app__config:
                doxyfile = genv.v__app__config['doxygen']['config']
                if not os.path.exists(doxyfile):
                    msg = QMessageBox()
                    msg.setWindowTitle(_("Error"))
                    msg.setText(_(
                    + "Error: Doxyfile configuration does not exists.\n"
                    + "Command aborted."))
                    msg.setIcon(QMessageBox.Warning)
                    msg.setStyleSheet(_("msgbox_css"))
                    
                    btn_ok = msg.addButton(QMessageBox.Ok)
                    result = msg.exec_()            
                    return
                
                parser = parserDoxyGen(doxyfile, self.parent)
        
        except Exception as e:
            showException(traceback.format_exc())
            return

class customScrollView_2(myCustomScrollArea):
    def __init__(self, parent, number, hid, name):
        super(customScrollView_2, self).__init__(number, hid, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        
        label_2 = self.addLabel(_("opti00"), True)
        label_2.setMinimumHeight(30)
        label_2.setMinimumWidth(200)
        
        try:
            group_box = QGroupBox("")
            group_layout = QVBoxLayout()
            
            self.rb1 = addRadioButton("o1",_("opti01"))
            self.rb2 = addRadioButton("o2",_("opti02"))
            self.cb1 = addCheckBox   ("o3",_("opti03"))
            
            self.rb1.setObjectName("doxygen_mode_document_entries_only")
            self.rb2.setObjectName("doxygen_mode_all_entries")
            self.cb1.setObjectName("doxygen_mode_cross_ref")
            
            self.rb1.clicked.connect(self.rb1_on_clicked)
            self.rb2.clicked.connect(self.rb2_on_clicked)
            self.cb1.clicked.connect(self.cb1_on_clicked)
            
            group_layout.addWidget(self.rb1)
            group_layout.addWidget(self.rb2)
            group_layout.addWidget(self.cb1)
            
            group_box.setLayout(group_layout)
            #
            widget = self.addLabel("Select programming language to optimize the results for:", True)
            
            self.layout.addWidget(group_box)
            self.layout.addWidget(widget)
                
            group_box = QGroupBox("")
            group_layout = QVBoxLayout()
            
            for x in range(4,11):
                widget = addRadioButton("mode_opti0" + str(x), _("opti0" + str(x)))
                widget.clicked.connect(self.radio_button_clicked)
                group_layout.addWidget(widget)
                
            group_box.setLayout(group_layout)
            self.layout.addWidget(group_box)
            
        except Exception as e:
            showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
            return False
    
    def rb1_on_clicked(self):
        if self.rb1.isChecked():
            genv.doc_entries = str(1)
        else:
            genv.doc_entries = str(0)
        genv.v__app_win.write_config_part()
            
    def rb2_on_clicked(self):
        if self.rb2.isChecked():
            genv.doc_entries = str(1)
        else:
            genv.doc_entries = str(0)
        genv.v__app_win.write_config_part()
            
    def cb1_on_clicked(self):
        if self.cb1.isChecked():
            genv.doc_cross = str(1)
        else:
            genv.doc_cross = str(0)
        genv.v__app_win.write_config_part()
    
    def radio_button_clicked(self):
        try:
            item = self.sender()
            opti = item.objectName()[-1]
            
            if not isinstance(item, QRadioButton):
                showError(_("Error:\nradio button internal error."))
                return False
            
            if genv.v__app__config_help == None:
                genv.v__app__config_help = configparser.ConfigParser()
                genv.v__app__config_help.read(genv.v__app__config_ini_help)
            
            genv.doc_optimize = str(int(opti) - 4)
            genv.v__app_win.write_config_part()
            
            return True
        except Exception as e:
            showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
            return False

# ------------------------------------------------------------------------
# create a scroll view for the output tab on left side of application ...
# ------------------------------------------------------------------------
class customScrollView_3(myCustomScrollArea):
    def __init__(self, parent, number, hid, name):
        super(customScrollView_3, self).__init__(number, hid, name)
        self.content_widget.setMinimumHeight(420)
        self.setWidgetResizable(True)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        
        label = self.addLabel(_("Select the output format(s) to generate:"), True)
        
        self.group_box1 = QGroupBox(" ")
        self.group_box1.setFont(QFont("Arial", 10))
        self.group_box1.setFixedHeight(120)
        
        self.group_layout1 = QVBoxLayout()
        
        # HTML
        self.w0 = addCheckBox("output_html","HTML", True)
        #
        self.w1 = addRadioButton("output_plain_html",  _("plain HTML"))
        self.w2 = addRadioButton("output_navi",        _("with navigation Panel"))
        self.w3 = addRadioButton("output_prepare_chm", _("prepare for compressed HTML .chm"))
        self.w4 = addCheckBox   ("output_search_func", _("with search function"))
        
        self.w1.setEnabled(False)
        self.w2.setEnabled(False)
        self.w3.setEnabled(False)
        self.w4.setEnabled(False)
        
        self.w0.clicked.connect(self.html_on_clicked)
        #
        self.w1.clicked.connect(self.html_on_clicked)
        self.w2.clicked.connect(self.html_on_clicked)
        self.w3.clicked.connect(self.html_on_clicked)
        self.w4.clicked.connect(self.html_on_clicked)
        
        self.group_layout1.addWidget(self.w0)
        self.group_layout1.addWidget(self.w1)
        self.group_layout1.addWidget(self.w2)
        self.group_layout1.addWidget(self.w3)
        self.group_layout1.addWidget(self.w4)
        #
        self.group_box1.setLayout(self.group_layout1)
        
        self.group_box2 = QGroupBox(" ")
        self.group_box2.setFont(self.font)
        
        self.group_layout2 = QVBoxLayout()
        
        # LaTeX
        self.l0 = addCheckBox("output_latex", "LaTeX", True)
        #
        self.l1 = addRadioButton("output_latex_pdf", _("an intermediate format for hyper-linked PDF"))
        self.l2 = addRadioButton("output_latex_imm", _("an intermediate format for PDF"))
        self.l3 = addRadioButton("output_latex_ps",  _("an intermediate format for PostScript"))
        
        self.l1.setEnabled(False)
        self.l2.setEnabled(False)
        self.l3.setEnabled(False)
        
        self.l0.clicked.connect(self.cbl0_on_clicked)
        self.l1.clicked.connect(self.cbl0_on_clicked)
        self.l2.clicked.connect(self.cbl0_on_clicked)
        self.l3.clicked.connect(self.cbl0_on_clicked)
        
        self.group_layout2.addWidget(self.l0)
        self.group_layout2.addWidget(self.l1)
        self.group_layout2.addWidget(self.l2)
        self.group_layout2.addWidget(self.l3)
        #
        self.group_box2.setLayout(self.group_layout2)
        
        self.group_box3 = QGroupBox(" ")
        self.group_box3.setFont(self.font)
        self.group_layout3 = QVBoxLayout()
        
        # misc
        self.m1 = addCheckBox("output_man", "Man pages")
        self.m2 = addCheckBox("output_rtf", "Rich Text Format - RTF")
        self.m3 = addCheckBox("output_xml", "XML")
        self.m4 = addCheckBox("output_doc", "DocBook")
        
        self.group_layout3.addWidget(self.m1)
        self.group_layout3.addWidget(self.m2)
        self.group_layout3.addWidget(self.m3)
        self.group_layout3.addWidget(self.m4)
        
        self.m1.clicked.connect(self.misc_on_clicked)
        self.m2.clicked.connect(self.misc_on_clicked)
        self.m3.clicked.connect(self.misc_on_clicked)
        self.m4.clicked.connect(self.misc_on_clicked)
        #
        self.group_box3.setLayout(self.group_layout3)
        
        #group_layout = QVBoxLayout()
        #
        self.layout.addWidget(label)
        self.layout.addWidget(self.group_box1)
        self.layout.addWidget(self.group_box2)
        self.layout.addWidget(self.group_box3)
        
        self.content_widget.setLayout(self.layout)
        self.setWidget(self.content_widget)
        
        #self.setLayout(group_layout)
    
    def misc_on_clicked(self):
        have_errors = False
        try:
            if self.sender().objectName() == "output_man":
                if self.sender().isChecked():
                    genv.doc_output_man = 1
                else:
                    genv.doc_output_man = 0
            
            if self.sender().objectName() == "output_rtf":
                if self.sender().isChecked():
                    genv.doc_output_rtf = 1
                else:
                    genv.doc_output_rtf = 0
            
            if self.sender().objectName() == "output_xml":
                if self.sender().isChecked():
                    genv.doc_output_xml = 1
                else:
                    genv.doc_output_xml = 0
            
            if self.sender().objectName() == "output_doc":
                if self.sender().isChecked():
                    genv.doc_output_doc = 1
                else:
                    genv.doc_output_doc = 0
            
            genv.v__app_win.write_config_part()
            
        except Exception as e:
            showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
            return False
        
    def html_decheck(self):
        genv.doc_output_plain_html  = 0
        genv.doc_output_navi        = 0
        genv.doc_output_prepare_chm = 0
        genv.doc_output_search_func = 0
            
    def html_on_clicked(self):
        have_errors = False
        try:
            if self.sender().objectName() == "output_html":
                if self.sender().isChecked():
                    self.w1.setEnabled(True)
                    self.w2.setEnabled(True)
                    self.w3.setEnabled(True)
                    self.w4.setEnabled(True)
                    
                    self.html_decheck()
                    genv.doc_output_html = 1
                else:
                    self.w1.setEnabled(False)
                    self.w2.setEnabled(False)
                    self.w3.setEnabled(False)
                    self.w4.setEnabled(False)
                    
                    self.html_decheck()
                    genv.doc_output_html = 0
                    
            elif self.sender().objectName() == "output_plain_html":
                if self.sender().isChecked():
                    self.html_decheck()
                    genv.doc_output_plain_html = 1
                else:
                    self.html_decheck()
                    genv.doc_output_plain_html = 0
                    
            elif self.sender().objectName() == "output_navi":
                if self.sender().isChecked():
                    self.html_decheck()
                    genv.doc_output_navi = 1
                else:
                    self.html_decheck()
                    genv.doc_output_navi = 0
                    
            elif self.sender().objectName() == "output_prepare_chm":
                if self.sender().isChecked():
                    self.html_decheck()
                    genv.doc_output_prepare_chm = 1
                else:
                    self.html_decheck()
                    genv.doc_output_prepare_chm = 0
                    
            elif self.sender().objectName() == "output_search_func":
                if self.sender().isChecked():
                    #self.html_decheck()
                    genv.doc_output_search_func = 1
                else:
                    #self.html_decheck()
                    genv.doc_output_search_func = 0
                    
            genv.v__app_win.write_config_part()
            
        except configparser.NoSectionError as e:
            have_errors = True
        except configparser.NoOptionError as e:
            have_errors = True
        
        if have_errors:
            genv.doc_output_html        = 0
            genv.doc_output_plain_html  = 0
            genv.doc_output_navi        = 0
            genv.doc_output_prepare_chm = 0
            genv.doc_output_search_func = 0
            
        genv.v__app_win.write_config_part()
    
    def cbl0_on_clicked(self):
        have_errors = False
        
        item0 = self.findChild(QCheckBox   , "output_latex")
        item1 = self.findChild(QRadioButton, "output_latex_pdf")
        item2 = self.findChild(QRadioButton, "output_latex_imm")
        item3 = self.findChild(QRadioButton, "output_latex_ps")
        
        try:
            genv.doc_output_latex     = int(genv.v__app__config_help.get("output", "doc_latex"))
            genv.doc_output_latex_pdf = int(genv.v__app__config_help.get("output", "doc_latex_pdf"))
            genv.doc_output_latex_imm = int(genv.v__app__config_help.get("output", "doc_latex_imm"))
            genv.doc_output_latex_ps  = int(genv.v__app__config_help.get("output", "doc_latex_ps"))
            
        except configparser.NoSectionError:
            have_errors = True
            
        except configparser.NoOptionError:
            have_errors = True
        
        if have_errors:
            genv.doc_output_latex_pdf = 0
            genv.doc_output_latex_imm = 0
            genv.doc_output_latex_ps  = 0
        
        genv.v__app_win.write_config_part()
        
        if item0.isChecked():
            genv.doc_output_latex = 1
            
            item1.setEnabled(True)
            item2.setEnabled(True)
            item3.setEnabled(True)
        else:
            genv.doc_output_latex = 0
            
            item1.setEnabled(False)
            item2.setEnabled(False)
            item3.setEnabled(False)
        
        if item1.isChecked():
            genv.doc_output_latex_pdf = 1
        else:
            genv.doc_output_latex_pdf = 0
        
        if item2.isChecked():
            genv.doc_output_latex_imm = 1
        else:
            genv.doc_output_latex_imm = 0
        
        if item3.isChecked():
            genv.doc_output_latex_ps = 1
        else:
            genv.doc_output_latex_ps = 0
            
        genv.v__app_win.write_config_part()

# ------------------------------------------------------------------------
# create a scroll view for the diagrams tab on left side of application ...
# ------------------------------------------------------------------------
class customScrollView_4(myCustomScrollArea):
    def __init__(self, parent, number, hid, name):
        super(customScrollView_4, self).__init__(number, hid, name)
        self.content_widget.setMinimumHeight(420)
        self.setWidgetResizable(True)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        
        lbl1 = self.addLabel(_("Diagrams to generate:"), True)
        #
        btn1 = addRadioButton("dia_not", _("No diagrams"))
        btn2 = addRadioButton("dia_txt", _("Text only"))
        btn3 = addRadioButton("dia_bin", _("Use built-in diagram generator"))
        btn4 = addRadioButton("dia_dot", _("Use Dot-Tool from the GrappVz package"))
        #
        lbl2 = self.addLabel(_("Dot graphs to generate:"), True)
        
        self.layout.addWidget(lbl1)
        self.layout.addWidget(btn1)
        self.layout.addWidget(btn2)
        self.layout.addWidget(btn3)
        self.layout.addWidget(btn4)
        self.layout.addWidget(lbl2)
        
        btn1.clicked.connect(self.radiobtn_on_click)
        btn2.clicked.connect(self.radiobtn_on_click)
        btn3.clicked.connect(self.radiobtn_on_click)
        btn4.clicked.connect(self.radiobtn_on_click)
        
        check_array = [
            ["graph_class" , _("Class graph")],
            ["graph_colab" , _("Colaboration diagram")],
            ["graph_overh" , _("Overall Class hiearchy")],
            ["graph_inc"   , _("Include dependcy graphs")],
            ["graph_incby" , _("Included by dependcy graphs")],
            ["graph_call"  , _("Call graphs")],
            ["graph_callby", _("Called-by graphs")]
        ]
        for chk in check_array:
            check_box = addCheckBox(chk[0], chk[1])
            check_box.clicked.connect(self.check_box_on_click)
            self.layout.addWidget(check_box)
        
        self.content_widget.setLayout(self.layout)
        self.setWidget(self.content_widget)
    
    def items_decheck(self):
        item1 = self.findChild(QRadioButton, "dia_not")
        item2 = self.findChild(QRadioButton, "dia_txt")
        item3 = self.findChild(QRadioButton, "dia_bin")
        item4 = self.findChild(QRadioButton, "dia_dot")
        
        item1.setChecked(False)
        item2.setChecked(False)
        item3.setChecked(False)
        item4.setChecked(False)
        
    def radiobtn_on_click(self):
        item1 = self.findChild(QRadioButton, "dia_not")
        item2 = self.findChild(QRadioButton, "dia_txt")
        item3 = self.findChild(QRadioButton, "dia_bin")
        item4 = self.findChild(QRadioButton, "dia_dot")
        
        if item1.isChecked():
            self.items_decheck()
            item1.setChecked(True)
            genv.doc_dia_not = 1
        else:
            genv.doc_dia_not = 0
            
        if item2.isChecked():
            self.items_decheck()
            item2.setChecked(True)
            genv.doc_dia_txt = 1
        else:
            genv.doc_dia_txt = 0
        
        if item3.isChecked():
            self.items_decheck()
            item3.setChecked(True)
            genv.doc_dia_bin = 1
        else:
            genv.doc_dia_bin = 0
        
        if item4.isChecked():
            self.items_decheck()
            item4.setChecked(True)
            genv.doc_dia_dot = 1
        else:
            genv.doc_dia_dot = 0
        
        genv.v__app_win.write_config_part()
    
    def check_box_on_click(self):
        if self.sender().objectName() == "graph_class":
            if self.sender().isChecked():
                genv.doc_dia_class = 1
            else:
                genv.doc_dia_class = 0
                
        if self.sender().objectName() == "graph_colab":
            if self.sender().isChecked():
                genv.doc_dia_colab = 1
            else:
                genv.doc_dia_colab = 0
                    
        if self.sender().objectName() == "graph_overh":
            if self.sender().isChecked():
                genv.doc_dia_overh = 1
            else:
                genv.doc_dia_overh = 0
                
        if self.sender().objectName() == "graph_inc":
            if self.sender().isChecked():
                genv.doc_dia_inc = 1
            else:
                genv.doc_dia_inc = 0
                
        if self.sender().objectName() == "graph_incby":
            if self.sender().isChecked():
                genv.doc_dia_incby = 1
            else:
                genv.doc_dia_incby = 0
                
        if self.sender().objectName() == "graph_call":
            if self.sender().isChecked():
                genv.doc_dia_call = 1
            else:
                genv.doc_dia_call = 0
                
        if self.sender().objectName() == "graph_callby":
            if self.sender().isChecked():
                genv.doc_dia_callby = 1
            else:
                genv.doc_dia_callby = 0
        
        genv.v__app_win.write_config_part()

class customScrollViewDoxygen(myCustomScrollArea):
    def __init__(self, number, hid, name):
        super(customScrollViewDoxygen, self).__init__(number, hid, name)
        
        self.number = number
        self.hid    = hid
        self.name   = name
        
        self.content_widget.setMinimumHeight(2380)
        self.setWidgetResizable(True)
        self.setStyleSheet(_("ScrollBarCSS"))
        print("-o-o")
        self.label_1.hide()
        ## 0xA0100
        label_elements = _("label_" + str(self.number) + "_elements")
        print("----")
        popo = self.addElements(number, label_elements, hid)
        print("popo " + str(number) + ": " + str(popo))
        
    # ----------------------------------------------
    # show help text when mouse move over the label
    # ----------------------------------------------
    def label_enter_event(self, text):
        genv.sv_help.setText(text)

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
        self.topic_counter = 1
        editor.setValue(self.topic_counter)
        self.topic_counter = self.topic_counter + 1
        return editor

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
        
        self.img_label = QLabel(self)
        self.img_label.setObjectName("doxygen-image")
        self.img_label.move(30,10)
        self.img_label.setMinimumHeight(70)
        self.img_label.setMinimumWidth(238)
        
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
        
        self.img_label.setStyleSheet(style.replace("\\","/"))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if genv.img_hlpndoc.state == 2:
                genv.img_hlpndoc.bordercolor = "lightgray"
                genv.img_hlpndoc.state = 0
                genv.img_hlpndoc.set_style()
            
            if self.state == 0:
                self.state = 2
                self.bordercolor = "lime";
                self.set_style()
                genv.doc_framework = genv.DOC_FRAMEWORK_DOXYGEN
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
                genv.doc_framework = -1
            genv.HelpAuthoringConverterMode = 0
            DebugPrint("doxygen")
    
    def enterEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "gray";
            self.set_style()
        self.img_label.setCursor(QCursor(Qt.PointingHandCursor))
    
    def leaveEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "lightgray";
            self.set_style()
        self.img_label.setCursor(QCursor(Qt.ArrowCursor))

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
            if genv.img_doxygen.state == 2:
                genv.img_doxygen.bordercolor = "lightgray"
                genv.img_doxygen.state = 0
                genv.img_doxygen.set_style()
            
            if self.state == 0:
                self.state = 2
                self.bordercolor = "lime";
                self.set_style()
                genv.doc_framework = genv.DOC_FRAMEWORK_HELPNDOC
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
                genv.doc_framework = -1
            genv.HelpAuthoringConverterMode = 1
            DebugPrint("helpNDoc")
    
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

class MyPushButton(QLabel):
    def __init__(self, parent, text="", mode=0, callback_func=None):
        super(MyPushButton, self).__init__(parent)
        self.parent = parent
        self.callback_func = callback_func
        #self.setText(text)
        
        self.setMaximumWidth(110)
        self.setMinimumWidth(110)
        self.setMinimumHeight(34)
        
        img_array = [
            "", "create", "open", "repro", "build"
        ]
        for img in img_array:
            if mode == img_array.index(img):
                self.btn_img_fg = genv.v__app__img__int__ + img + "1" + genv.v__app__img_ext__  #os.path.join(genv.v__app__img__int__, img + "1" + genv.v__app__img_ext__)
                self.btn_img_bg = genv.v__app__img__int__ + img + "2" + genv.v__app__img_ext__  #os.path.join(genv.v__app__img__int__, img + "2" + genv.v__app__img_ext__)
                break
        
        fg = self.btn_img_fg.replace("\\","/")
        bg = self.btn_img_bg.replace("\\","/")
        
        style = _("push_css") \
        .replace("{fg}",fg)   \
        .replace("{bg}",bg)
        
        self.setStyleSheet(style)
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            #if not self.func == None:
            self.callback_func()
        super().mousePressEvent(event)

class MyProjectOption():
    def __init__(self):
        msg = None
        msg = QMessageBox()
        msg.setWindowTitle("Information")
        msg.setText(_(genv.project_not_known))
        
        msg.setIcon(QMessageBox.Question)
        msg.setStyleSheet(_("msgbox_css"))
        
        btn_doxy = QPushButton("Doxygen")
        btn_help = QPushButton("HelpNDoc")
        btn_hide = QPushButton("Abort")
        
        btn_doxy.clicked.connect(self.on_doxy_clicked)
        btn_help.clicked.connect(self.on_help_clicked)
        btn_hide.clicked.connect(self.on_hide_clicked)
        
        msg.addButton(btn_doxy, QMessageBox.ActionRole)
        msg.addButton(btn_help, QMessageBox.ActionRole)
        msg.addButton(btn_hide, QMessageBox.ActionRole)
        
        result = msg.exec_()
        return
    
    def on_doxy_clicked(self):
        DebugPrint("doxy")
        genv.doc_framework = genv.DOC_FRAMEWORK_DOXYGEN
        return True
    
    def on_help_clicked(self):
        DebugPrint("help")
        genv.doc_framework = genv.DOC_FRAMEWORK_HELPNDOC
        return True
    
    def on_hide_clicked(self):
        return True

class OpenProjectButton(QPushButton):
    def __init__(self, parent=None, font=None):
        super(OpenProjectButton, self).__init__(parent)
        self.parent = parent
        self.setText("...")
        
        self.setFont(font)
        self.setMinimumHeight(36)
        self.setMinimumWidth (36)
        self.setMaximumWidth (36)
        
        self.clicked.connect(self.clicked_button)
    
    def clicked_button(self):
        dialog  = QFileDialog()
        file_path = ""
        icon_size = 20
        
        dialog.setWindowTitle(_("Open Project File"))
        dialog.setStyleSheet (_("QFileDlog"))
        
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setViewMode(QFileDialog.Detail)
        
        dialog.setOption  (QFileDialog.DontUseNativeDialog, True)
        dialog.setNameFilters(["Program Files (*.pro)", "Text Files (*.txt)", "All Files (*)"])
        
        list_views = dialog.findChildren(QListView)
        tree_views = dialog.findChildren(QTreeView)
        
        for view in list_views + tree_views:
            view.setIconSize(QSize(icon_size, icon_size))
        
        if dialog.exec_() == QFileDialog.Accepted:
            file_path = dialog.selectedFiles()[0]
        
        if not file_path:
            msg = QMessageBox()
            msg.setWindowTitle("Information")
            msg.setText(_("no source file given.\n"))
            msg.setIcon(QMessageBox.Question)
            msg.setStyleSheet(_("msgbox_css"))
            
            btn_ok = msg.addButton(QMessageBox.Ok)
            result = msg.exec_()            
            return
        
        if not os.path.isfile(file_path):
            msg = None
            msg = QMessageBox()
            msg.setWindowTitle("Information")
            msg.setText(_(
                "You selected a file, that can not be open.\n"
                "no file will be open."))
            msg.setIcon(QMessageBox.Question)
            msg.setStyleSheet(_("msgbox_css"))
            
            btn_ok = msg.addButton(QMessageBox.Ok)
            result = msg.exec_()
            return
        
        self.parent.tab0_fold_edit1.clear()
        self.parent.tab0_fold_edit1.setText(file_path)
        
        try:
            genv.v__app__config_ini = file_path
            genv.v__app__config.read( file_path )
        
            genv.doc_type = int(genv.v__app__config.get("project", "type"))
            
            if genv.doc_type == 0:
                genv.doc_framework = genv.DOC_FRAMEWORK_DOXYGEN
            elif genv.doc_type == 1:
                genv.doc_framework = genv.DOC_FRAMEWORK_HELPNDOC
            else:
                showError(_("Error:\ncan not determine doc type."))
                return False
        
        except configparser.NoOptionError as error:
            MyProjectOption()
        
        if genv.doc_type == 0:
            genv.doc_framework = genv.DOC_FRAMEWORK_DOXYGEN
            self.parent.trigger_mouse_press(genv.img_doxygen)
        elif genv.doc_type == 1:
            genv.doc_framework = genv.DOC_FRAMEWORK_HELPNDOC
            self.parent.trigger_mouse_press(genv.img_hlpndoc)
        else:
            showInfo(_("Error: help framework not known."))
            return False
        return True

class myExitDialog(QDialog):
    def __init__(self, title, parent=None):
        super(myExitDialog, self).__init__(parent)
        
        self.parent = parent
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
        
        self.helpButton.clicked.connect(self.help_click)
        self.prevButton.clicked.connect(self.prev_click)
        self.exitButton.clicked.connect(self.exit_click)
        
        self.finished.connect(self.on_finished)
        
        self.hexitText = QLabel(_("Would you realy exit the Application?"))
        
        self.hlayout.addLayout(self.vlayout)
        self.hlayout.addWidget(self.hexitText)
        
        self.setLayout(self.hlayout)
    
    def disconnectEvents(self):
        try:
            self.helpButton.clicked.disconnect(self.help_click)
            self.prevButton.clicked.disconnect(self.prev_click)
            self.exitButton.clicked.disconnect(self.exit_click)
        except TypeError as e:
            DebugPrint(e)
        except Exception as e:
            DebugPrint(e)
    
    def on_finished(self):
        self.disconnectEvents()
    
    def help_click(self):
        DebugPrint("help button")
        self.close()
        return
    def prev_click(self):
        DebugPrint("reje")
        self.close()
        return
    def exit_click(self):
        DebugPrint("exit")
        if not genv.worker_thread == None:
            genv.worker_thread.stop()
            
        #self.disconnectEvents()
        genv.v__app_win.write_config_part()
        
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
        DebugPrint("enter")
    
    def dropEvent(self, event):
        pos = event.pos()
        widget = event.source()
        event.accept()
        DebugPrint("drop")
    

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

class SourceCodeEditorBase(QSyntaxHighlighter):
    def __init__(self, document):
        super(SourceCodeEditorBase, self).__init__(document)
        
        self.dark_green = QColor(0,100,0)
        
        self.commentFormat = QTextCharFormat()
        self.commentFormat.setForeground(self.dark_green)
        self.commentFormat.setFontWeight(QFont.Normal)  # Set the comment font weight to normal
        
        self.boldFormat = QTextCharFormat()
        self.boldFormat.setFont(QFont(genv.v__app__font_edit, 12))  # Set the font for keywords
        self.boldFormat.setFontWeight(QFont.Bold)
        
        # Definiere die Muster für mehrzeilige Kommentare
        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(self.dark_green)

class BasicHighlighter(SourceCodeEditorBase):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []
        
        # Format für Schlüsselwörter
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("blue"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            r"\bDIM\b", r"\bPRINT\b", r"\bINPUT\b", r"\bIF\b", r"\bTHEN\b",
            r"\bELSE\b", r"\bFOR\b", r"\bTO\b", r"\bNEXT\b", r"\bWHILE\b",
            r"\bWEND\b", r"\bGOTO\b", r"\bREM\b", r"\bEND\b", r"\bSUB\b",
            r"\bFUNCTION\b", r"\bRETURN\b"
        ]
        self.highlighting_rules += [(re.compile(keyword), keyword_format) for keyword in keywords]
        
        # Format für Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("darkgreen"))
        self.highlighting_rules.append((re.compile(r'"[^"]*"'), string_format))
        
        # Format für Kommentare
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("darkgray"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r"'.*"), comment_format))
        
        # Format für Zahlen
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("darkred"))
        self.highlighting_rules.append((re.compile(r'\b\d+(\.\d+)?\b'), number_format))
    
    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                start, end = match.start(), match.end()
                self.setFormat(start, end - start, format)
        self.setCurrentBlockState(0)

class CppSyntaxHighlighter(SourceCodeEditorBase):
    def __init__(self, document):
        super(CppSyntaxHighlighter, self).__init__(document)
        self.highlighting_rules = []

        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("blue"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            r"\bint\b", r"\bfloat\b", r"\breturn\b", r"\bvoid\b", r"\bif\b",
            r"\belse\b", r"\bwhile\b", r"\bfor\b", r"\bclass\b", r"\bstruct\b"
        ]
        for keyword in keywords:
            self.highlighting_rules.append((re.compile(keyword), keyword_format))

        # Single-line comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("green"))
        self.highlighting_rules.append((re.compile(r"//.*"), comment_format))

        # Multi-line comments
        self.comment_start_expression = re.compile(r"/\*")
        self.comment_end_expression = re.compile(r"\*/")
        self.comment_format = QTextCharFormat()
        self.comment_format.setForeground(QColor("green"))

        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("magenta"))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("darkRed"))
        self.highlighting_rules.append((re.compile(r"\b[0-9]+\b"), number_format))

    def highlightBlock(self, text):
        # Apply single-line patterns
        for pattern, format in self.highlighting_rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, format)

        # Handle multi-line comments
        self.setCurrentBlockState(0)

        if self.previousBlockState() == 1:
            match = self.comment_end_expression.search(text)
            if match:
                start, end = match.span()
                self.setFormat(0, end, self.comment_format)
                self.setCurrentBlockState(0)
            else:
                self.setFormat(0, len(text), self.comment_format)
                self.setCurrentBlockState(1)

        start_match = self.comment_start_expression.search(text)
        if start_match:
            start = start_match.start()
            end_match = self.comment_end_expression.search(text, start)
            if end_match:
                end = end_match.end()
                self.setFormat(start, end - start, self.comment_format)
            else:
                self.setFormat(start, len(text) - start, self.comment_format)
                self.setCurrentBlockState(1)

class dBaseSyntaxHighlighter(SourceCodeEditorBase):
    def __init__(self, document):
        super(dBaseSyntaxHighlighter, self).__init__(document)
        
        # Definiere die Schlüsselwörter, die fettgedruckt sein sollen
        self.keywords = [
            ".AND.", ".OR.", ".NOR.", ".XOR.",
            "BREAK",
            "CASE",
            "CLASS",
            "COLOR",
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
            "OF",
            "RETURN",
            "SET",
            "TO",
            "WHILE", 
            "WITH"
        ]
        
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

class LispSyntaxHighlighter(SourceCodeEditorBase):
    def __init__(self, document):
        super(LispSyntaxHighlighter, self).__init__(document)
        self.highlighting_rules = []

        # Format for LISP keywords (e.g., defun, lambda)
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("blue"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = ["defun", "lambda", "setq", "let", "cond", "if", "progn", "car", "cdr"]
        for keyword in keywords:
            pattern = QRegExp(f"\\b{keyword}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # Format for numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("darkMagenta"))
        self.highlighting_rules.append((QRegExp("\\b[0-9]+\\b"), number_format))

        # Format for strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("darkGreen"))
        self.highlighting_rules.append((QRegExp("\".*\""), string_format))

        # Format for parentheses
        paren_format = QTextCharFormat()
        paren_format.setForeground(QColor("darkRed"))
        self.highlighting_rules.append((QRegExp("[()]"), paren_format))
        
        # Format for comments (starting with ; and continuing to the end of the line)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("green"))
        self.highlighting_rules.append((QRegExp(";[^\r\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, char_format in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, char_format)
                index = expression.indexIn(text, index + length)

class PythonSyntaxHighlighter(SourceCodeEditorBase):
    def __init__(self, document):
        super(PythonSyntaxHighlighter, self).__init__(document)
        self.highlighting_rules = []

        # Format für Schlüsselwörter
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("blue"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'False', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'None',
            'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'True', 'try', 'while', 'with', 'yield'
        ]
        for word in keywords:
            pattern = f'\b{word}\b'
            self.highlighting_rules.append((re.compile(pattern), keyword_format))

        # Format für Zeichenketten
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("darkGreen"))
        self.highlighting_rules.append((re.compile(r'(".*?"|\'.*?\')'), string_format))

        # Format für Kommentare
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("darkGray"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile(r'#.*'), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)
        self.setCurrentBlockState(0)

class JavaSyntaxHighlighter(SourceCodeEditorBase):
    def __init__(self, document):
        super(JavaSyntaxHighlighter, self).__init__(document)
        self.highlighting_rules = []
        
        # Keywords in Java
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("blue"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            r'\babstract\b', r'\bassert\b', r'\bboolean\b', r'\bbreak\b',
            r'\bbyte\b', r'\bcase\b', r'\bcatch\b', r'\bchar\b', r'\bclass\b',
            r'\bconst\b', r'\bcontinue\b', r'\bdefault\b', r'\bdo\b',
            r'\bdouble\b', r'\belse\b', r'\benum\b', r'\bextends\b', r'\bfinal\b',
            r'\bfinally\b', r'\bfloat\b', r'\bfor\b', r'\bgoto\b', r'\bif\b',
            r'\bimplements\b', r'\bimport\b', r'\binstanceof\b', r'\bint\b',
            r'\binterface\b', r'\blong\b', r'\bnative\b', r'\bnew\b', r'\bnull\b',
            r'\bpackage\b', r'\bprivate\b', r'\bprotected\b', r'\bpublic\b',
            r'\breturn\b', r'\bshort\b', r'\bstatic\b', r'\bstrictfp\b',
            r'\bsuper\b', r'\bswitch\b', r'\bsynchronized\b', r'\bthis\b',
            r'\bthrow\b', r'\bthrows\b', r'\btransient\b', r'\btry\b',
            r'\bvoid\b', r'\bvolatile\b', r'\bwhile\b'
        ]
        for keyword in keywords:
            self.highlighting_rules.append((re.compile(keyword), keyword_format))
        
        # Single-line comments
        single_line_comment_format = QTextCharFormat()
        single_line_comment_format.setForeground(QColor("green"))
        self.highlighting_rules.append((re.compile(r'//[^\n]*'), single_line_comment_format))
        
        # Multi-line comments
        self.multi_line_comment_format = QTextCharFormat()
        self.multi_line_comment_format.setForeground(QColor("green"))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("magenta"))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        
        # Characters
        char_format = QTextCharFormat()
        char_format.setForeground(QColor("orange"))
        self.highlighting_rules.append((re.compile(r"'.'"), char_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("darkCyan"))
        self.highlighting_rules.append((re.compile(r'\b\d+\b'), number_format))
    
    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            for match in pattern.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), fmt)
        self.setCurrentBlockState(0)
        
        # Multi-line comments
        start_comment = "/*"
        end_comment = "*/"
        
        if self.previousBlockState() != 1:
            start_index = text.find(start_comment)
        else:
            start_index = 0
        
        while start_index >= 0:
            end_index = text.find(end_comment, start_index)
            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + len(end_comment)
            self.setFormat(start_index, comment_length, self.multi_line_comment_format)
            start_index = text.find(start_comment, start_index + comment_length)

class PrologSyntaxHighlighter(SourceCodeEditorBase):
    def __init__(self, document):
        super(PrologSyntaxHighlighter, self).__init__(document)
        self.highlighting_rules = []

        # Format for Prolog keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("blue"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "is", "not", "true", "fail", "false", "repeat", "assert", "retract",
            "consult", "listing", "halt", "def"
        ]
        for word in keywords:
            pattern = QRegExp("\\b" + word + "\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # Format for single-line comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("green"))
        self.highlighting_rules.append((QRegExp("#.*[^\\r\\n]"), comment_format))

        # Format for strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("magenta"))
        self.highlighting_rules.append((QRegExp("'[^']*'"), string_format))

        # Format for variables (starting with an uppercase letter or _)
        variable_format = QTextCharFormat()
        variable_format.setForeground(QColor("darkRed"))
        self.highlighting_rules.append((QRegExp("\\b[A-Z_][a-zA-Z0-9_]*\\b"), variable_format))

        # Format for atoms (lowercase identifiers)
        atom_format = QTextCharFormat()
        atom_format.setForeground(QColor("black"))
        self.highlighting_rules.append((QRegExp("\\b[a-z][a-zA-Z0-9_]*\\b"), atom_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, fmt)
                index = expression.indexIn(text, index + length)

class PascalSyntaxHighlighter(SourceCodeEditorBase):
    def __init__(self, document):
        super(PascalSyntaxHighlighter, self).__init__(document)
        
        self.commentStartExpressions = [QRegExp(r"\(\*"), QRegExp(r"\{")]
        self.commentEndExpressions   = [QRegExp(r"\*\)"), QRegExp(r"\}")]
        
        self.highlighting_rules = []
        self.keywords = [
            "program", "unit", "library",
            "begin", "end", "var",
            "procedure", "function",
            "while", "with", "do", "else", "for",
            "case"
        ]
        
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))
        keyword_format.setFontWeight(QFont.Bold)
        
        for word in self.keywords:
            pattern = f'\b{word}\b'
            self.highlighting_rules.append((re.compile(pattern), keyword_format))
    
    def highlightBlock(self, text):
        # Entfernt vorherige Formatierungen
        self.setFormat(0, len(text), QTextCharFormat())

        # Muster für mehrzeilige Kommentare
        curly_comment_start_pattern = re.compile(r"\{")    # Beginn eines geschweiften Kommentars
        curly_comment_end_pattern   = re.compile(r"\}")    # Ende   eines geschweiften Kommentars
        multi_comment_start_pattern = re.compile(r"\(\*")  # Beginn eines (* ... *)-Kommentars
        multi_comment_end_pattern   = re.compile(r"\*\)")  # Ende   eines (* ... *)-Kommentars

        # Schritt 1: Verfolgen des Zustands für mehrzeilige Kommentare
        if self.previousBlockState() == 1:  # Mehrzeiliger Kommentar { ... }
            match_end = curly_comment_end_pattern.search(text)
            if match_end:
                end = match_end.end()
                self.setFormat(0, end, self.multiLineCommentFormat)
                self.setCurrentBlockState(0)
            else:
                self.setFormat(0, len(text), self.multiLineCommentFormat)
                self.setCurrentBlockState(1)
            return
        elif self.previousBlockState() == 2:  # Mehrzeiliger Kommentar (* ... *)
            match_end = multi_comment_end_pattern.search(text)
            if match_end:
                end = match_end.end()
                self.setFormat(0, end, self.multiLineCommentFormat)
                self.setCurrentBlockState(0)
            else:
                self.setFormat(0, len(text), self.multiLineCommentFormat)
                self.setCurrentBlockState(2)
            return

        # Schritt 2: Erkennung neuer mehrzeiliger Kommentare
        match_start = curly_comment_start_pattern.search(text)
        if match_start:
            start = match_start.start()
            match_end = curly_comment_end_pattern.search(text, start)
            if match_end:
                end = match_end.end()
                self.setFormat(start, end - start, self.multiLineCommentFormat)
            else:
                self.setFormat(start, len(text) - start, self.multiLineCommentFormat)
                self.setCurrentBlockState(1)
                return

        match_start = multi_comment_start_pattern.search(text)
        if match_start:
            start = match_start.start()
            match_end = multi_comment_end_pattern.search(text, start)
            if match_end:
                end = match_end.end()
                self.setFormat(start, end - start, self.multiLineCommentFormat)
            else:
                self.setFormat(start, len(text) - start, self.multiLineCommentFormat)
                self.setCurrentBlockState(2)
                return

        # Schritt 3: Einzeilige Kommentare formatieren
        single_line_comment_pattern = re.compile(r"//.*")
        for match in re.finditer(single_line_comment_pattern, text):
            start, end = match.start(), match.end()
            self.setFormat(start, end - start, self.commentFormat)

        # Schritt 4: Geschweifte Kommentare, auch innerhalb von Text
        curly_comment_pattern = re.compile(r"\{.*?\}")
        for match in re.finditer(curly_comment_pattern, text):
            start, end = match.start(), match.end()
            self.setFormat(start, end - start, self.multiLineCommentFormat)

        # Schritt 5: Mehrzeilige Kommentare (* ... *) innerhalb von Text
        multi_line_inline_comment_pattern = re.compile(r"\(\*.*?\*\)", re.DOTALL)
        for match in re.finditer(multi_line_inline_comment_pattern, text):
            start, end = match.start(), match.end()
            self.setFormat(start, end - start, self.multiLineCommentFormat)

        # Schritt 6: Keywords formatieren
        keyword_pattern = re.compile(r'\b(' + '|'.join(self.keywords) + r')\b', re.IGNORECASE)
        for match in re.finditer(keyword_pattern, text):
            start, end = match.start(), match.end()

            # Prüfen, ob das Keyword in einem Kommentar steht
            is_in_comment = any(
                start >= comment.start() and end <= comment.end()
                for comment in re.finditer(r"//.*|\(\*.*?\*\)|\{.*?\}", text, re.DOTALL)
            )
            if is_in_comment:
                # Innerhalb eines Kommentars: Kommentarfarbe anwenden
                self.setFormat(start, end - start, self.commentFormat)
            else:
                # Außerhalb eines Kommentars: Standard-Keyword-Format
                self.setFormat(start, end - start, self.boldFormat)

        self.setCurrentBlockState(0)


class JavaScriptHighlighter(SourceCodeEditorBase):
    def __init__(self, document):
        super().__init__(document)
        self.highlight_rules = []

        # Format für Schlüsselwörter
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "var", "let", "const", "function", "return", "if", "else", "while",
            "for", "break", "continue", "switch", "case", "default", "throw",
            "try", "catch", "finally", "new", "this", "typeof", "instanceof",
            "true", "false", "null", "undefined", "class", "extends", "constructor"
        ]
        for keyword in keywords:
            pattern = QRegularExpression(r"\b" + keyword + r"\b")
            self.highlight_rules.append((pattern, keyword_format))

        # Format für Zeichenketten
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#008000"))
        self.highlight_rules.append((QRegularExpression(r"\".*?\"|'.*?'"), string_format))

        # Format für Zahlen
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#FF4500"))
        self.highlight_rules.append((QRegularExpression(r"\b\d+\b"), number_format))

        # Format für einzeilige Kommentare
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))
        self.highlight_rules.append((QRegularExpression(r"//[^\n]*"), comment_format))

        # Format für mehrzeilige Kommentare
        multi_comment_format = QTextCharFormat()
        multi_comment_format.setForeground(QColor("#808080"))
        self.comment_start = QRegularExpression(r"/\*")
        self.comment_end = QRegularExpression(r"\*/")
        self.comment_format = multi_comment_format

    def highlightBlock(self, text):
        # Syntax-Hervorhebung mit den Regeln
        for pattern, format in self.highlight_rules:
            expression = QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        # Mehrzeilige Kommentare hervorheben
        self.setCurrentBlockState(0)
        start_index = 0 if self.previousBlockState() != 1 else self.comment_start.match(text).capturedStart()
        while start_index >= 0:
            match = self.comment_end.match(text, start_index)
            end_index = match.capturedStart() if match.hasMatch() else -1
            comment_length = (end_index - start_index + match.capturedLength()) if match.hasMatch() else len(text) - start_index
            self.setFormat(start_index, comment_length, self.comment_format)
            if end_index == -1:
                self.setCurrentBlockState(1)
                break
            start_index = self.comment_start.match(text, end_index).capturedStart()

class EditorTranslate(QWidget):
    def __init__(self, parent=None):
        super(EditorTranslate, self).__init__(parent)
        font = QFont(genv.v__app__font,11)
        
        self.setContentsMargins(0,0,0,0)
        self.setMinimumWidth(220)
        self.setMaximumWidth(220)
        self.setFont(font)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        
        self.group_box = QGroupBox(_(" Choose a Translation: "))
        self.group_box.setFont(font)
        self.group_layout = QVBoxLayout()
        
        #self.dummyl = QLabel(" ")
        self.radio1 = QRadioButton(_("Convert to FPC Pascal"))
        self.radio2 = QRadioButton(_("Convert to GNU C++"))
        self.radio3 = QRadioButton(_("Convert to Byte-Code"))
        
        self.radio1.setObjectName("pascal")
        self.radio2.setObjectName("gnucpp")
        self.radio3.setObjectName("bytecode")
        
        #self.dummyl.setFont(font)
        self.radio1.setFont(font)
        self.radio2.setFont(font)
        self.radio3.setFont(font)
        
        self.radio1.toggled.connect(self.on_radiobutton_clicked)
        self.radio2.toggled.connect(self.on_radiobutton_clicked)
        self.radio3.toggled.connect(self.on_radiobutton_clicked)
        
        self.radio3.setChecked(True)
        
        #self.group_layout.addWidget(self.dummyl)
        self.group_layout.addWidget(self.radio1)
        self.group_layout.addWidget(self.radio2)
        self.group_layout.addWidget(self.radio3)
        self.group_layout.addStretch()
        
        self.group_box.setLayout(self.group_layout)
        
        # file list
        self.files_layout = QVBoxLayout()
        self.files_list   = QListWidget()
        
        self.files_layout.addWidget(self.files_list)
        
        self.layout.addWidget(self.group_box)
        self.layout.addLayout(self.files_layout)
        
        self.setLayout(self.layout)
    
    def on_radiobutton_clicked(self):
        radio_button = self.sender()
        radio_name   = radio_button.objectName()
        print("rad: ", radio_name)
        #if radio_button.isChecked():
        #    #if radio_name == "gnucpp":
        #    #    #genv.editor.obj_2.setVisible(False)  # fpc
        #    #    #genv.editor.obj_3.setVisible(True)   # gnu cc
        #    #    #genv.editor.obj_3.clear()
        #    #elif radio_name == "pascal":
        #    #    #genv.editor.obj_2.setVisible(True)   # fpc
        #    #    #genv.editor.obj_3.setVisible(False)  # gnu c++
        #    #    #genv.editor.obj_2.clear()
        #    #elif radio_name == "bytecode":
        #    #    #genv.editor.obj_2.setVisible(False)  # fpc
        #    #    #genv.editor.obj_3.setVisible(False)  # gnu c++
        #    ###showInfo("radio_button:  " + radio_button.text())
    
# ----------------------------------------------------------------------------
# \brief This class stands for the source code input editors like: dBase, C
# ----------------------------------------------------------------------------
class EditorTextEdit(QPlainTextEdit):
    def __init__(self, parent, file_name, edit_type, mode=0):
        super(EditorTextEdit, self).__init__()
        
        self.mode   = mode
        self.parser = parent
        
        self.setStyleSheet(_("ScrollBarCSS"))
        self.setObjectName(file_name)
        
        self.file_name = file_name
        self.edit_type = edit_type
        self.bookmarks = set()
        
        self.parent = parent
        self.move(0,0)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged    .connect(self.updateLineNumberAreaWidth)
        self.updateRequest        .connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        
        if edit_type == "dbase":
            self.highlighter = dBaseSyntaxHighlighter       (self.document())
        elif edit_type == "pascal":
            self.highlighter = PascalSyntaxHighlighter      (self.document())
        elif edit_type == "isoc":
            self.highlighter = CppSyntaxHighlighter         (self.document())
        elif edit_type == "java":
            self.highlighter = JavaSyntaxHighlighter        (self.document())
        elif edit_type == "javascript":
            self.highlighter = JavaScriptSyntaxHighlighter  (self.document())
        elif edit_type == "basic":
            self.highlighter = BasicSyntaxHighlighter       (self.document())
        elif edit_type == "lisp":
            self.highlighter = LispSyntaxHighlighter        (self.document())
        elif edit_type == "prolog":
            self.highlighter = PrologSyntaxHighlighter      (self.document())
        elif edit_type == "python":
            self.highlighter = PythonSyntaxHighlighter      (self.document())
        
        # Schriftgröße und Schriftart setzen
        self.setFont(QFont(genv.v__app__font_edit, 12))
        
        if self.mode == 0:
            if not os.path.exists(file_name):
                showInfo(_(f"Error: file does not exists: {file_name}"))
                return
            
            # Datei einlesen und Text setzen
            self.load_file(file_name)
        
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
    
    # todo: check directory !
    def check_default(self):
        file_path = genv.default_file_path
        try:
            if genv.active_side_button == genv.SIDE_BUTTON_PASCAL:
                file_path = file_path + "pascal/default.pas"
                file_path = file_path.replace('\\', '/')
                
                if os.path.exists(file_path):
                    os.remove(file_path)
                        
            elif genv.active_side_button == genv.SIDE_BUTTON_DBASE:
                file_path = file_path + "dbase/default.prg"
                file_path = file_path.replace('\\', '/')
            
            showInfo("cd: " + file_path)
            os.chdir(os.path.dirname   (file_path))
            self.parent.open_new_editor(file_path, 1)
            
            return True
        except FileNotFoundError as e:
            self.showExceptionHandler(e)
            return False
            
        except PermissionError as e:
            self.showExceptionHandler(e)
            return False
            
        except Exception as e:
            self.showExceptionHandler(e)
            return False
        
    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space + 10  # Zusätzlicher Platz, um sicherzustellen, dass die Zeilennummern nicht den Text überlappen
    
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
                painter.drawText(0, int(top), self.lineNumberArea.width() - 5, self.fontMetrics().height(), Qt.AlignRight, number)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1
    
    def load_file(self, file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as file:
                text = file.read()
                self.setPlainText(text)
                file.close()
        except:
            showInfo("latin 11111")
            with open(file_name, 'r', encoding='latin-1') as file:
                text = file.read()
                self.setPlainText(text)
                file.close()
    
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
        self.setViewportMargins(self.lineNumberAreaWidth()+4, 0, 0, 0)
    
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
                rect = QRect(21, int(top), self.lineNumberArea.width() - 21, self.fontMetrics().height())
                painter.drawText(rect, Qt.AlignRight, number)
                
                # Zeichnen des Icons
                icon_rect = QRect(0, int(top), 21, self.fontMetrics().height())
                if blockNumber in self.bookmarks:
                    painter.setBrush(Qt.red)
                    painter.drawEllipse(icon_rect.center(), 5, 5)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            cursor        = self.cursorForPosition(event.pos())
            block         = cursor.block()
            block_number  = block.blockNumber()
            top           = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
            bottom        = top + self.blockBoundingRect(block).height()
            
            genv.current_focus = self
            
            # Überprüfen, ob der Klick innerhalb der Linie liegt
            if int(top) <= event.pos().y() <= int(bottom):
                if block_number in self.bookmarks:
                    self.bookmarks.remove(block_number)
                else:
                    self.bookmarks.add(block_number)
                self.lineNumberArea.update()
        
        super().mousePressEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            #if not genv.c64_parser.c64_exec_thread == None:
            #    genv.c64_parser.c64_exec_thread_stop()
            super().keyPressEvent(event)
            return None
        elif event.key() == Qt.Key.Key_F2:
            script_name = self.objectName()
            
            if self.edit_type == "c64":
                self.check_default()
                self.parse_source(genv.SIDE_BUTTON_C64, script_name)
                
            elif self.edit_type == "dbase":
                if script_name.endswith("/"):
                    script_name += "default.prg"
                    self.check_default()
                    with open(script_name, 'w',
                        encoding='utf-8') as file:
                        file.write(self.toPlainText())
                        file.close()
                        
                self.parse_source(genv.SIDE_BUTTON_DBASE, script_name)
                
            elif self.edit_type == "pascal":
                if not script_name:
                    if script_name.endswith("/"):
                        script_name += "/default.pas"
                        self.check_default()
                try:
                    with open(script_name,'w',encoding='utf-8') as file:
                        file.write(self.toPlainText())
                        file.close()
                        
                    self.parse_source(genv.SIDE_BUTTON_PASCAL, script_name)
                    return
                    
                except PermissionError as e:
                    showError(_(f"not enough permissions:\n{e}"))
                    return
                except Exception as e:
                    showError(_(f"A Common Exception occired:\n{w}"))
                    return
                
            elif self.edit_type == "lisp":
                self.parse_source(genv.SIDE_BUTTON_LISP, script_name)
                
            elif self.edit_type == "prolog":
                self.parse_source(genv.SIDE_BUTTON_PROLOG, script_name)
        
        elif event.key() == Qt.Key_S and event.modifiers() == Qt.ControlModifier:
            options = QFileDialog.Options()
            file_name, a = QFileDialog.getSaveFileName(self,
                _("Save Text"), "",
                _("Text files (*.prg);;All Files (*)"),
                options=options)
            if file_name:
                try:
                    # --------------------------------------------------
                    # Text aus QPlainTextEdit erhalten und in
                    # die Datei schreiben
                    # --------------------------------------------------
                    with open(file_name, 'w', encoding='utf-8') as file:
                        file.write(self.toPlainText())
                        file.close()
                    # --------------------------------------------------
                    # Bestätigung anzeigen
                    # --------------------------------------------------
                    QMessageBox.information(self,
                        _("Success"),
                        _("File successfully saved."))
                    return
                except Exception as e:
                    QMessageBox.critical(self,
                        _("Error"),
                        _("Error during saving file"))
                    return
            else:
                showInfo(_("something went wrong"))
                return
        elif event.key() == Qt.Key_O and event.modifiers() == Qt.ControlModifier:
            options = QFileDialog.Options()
            file_name, a = QFileDialog.getOpenFileName(self,
                _("Load Text"), "",
                _("Text files (*.prg);;All Files (*)"),
                options=options)
            if file_name:
                try:
                    with open(file_name, 'r', encoding='utf-8') as file:
                        self.setPlainText(file.read())
                        file.close()
                    QMessageBox.information(self,
                        _("Success"),
                        _("File successfully loaded."))
                    return
                except Exception as e:
                    QMessageBox.critical(self,
                        _("Error"),
                        _("Error during loading file"))
                    return
            else:
                showInfo(_("something went wrong"))
                return
        else:
            super().keyPressEvent(event)
    
    def parse_source(self, edit_type, script_name):
        try:
            if edit_type == genv.SIDE_BUTTON_C64:
                parser = C64BasicParser(script_name)
                parsed = parser.parse()
                
            elif edit_type == genv.SIDE_BUTTON_DBASE:
                parser = dBaseParser(script_name)
                parsed = parser.parse()
                
            elif edit_type == genv.SIDE_BUTTON_PASCAL:
                parser = PascalParser(script_name)
                parsed = parser.parse()
            
            self.display_comment_summary()
            
            python_code = parser.convert_to_python(parsed)
            
            if not python_code:
                showInfo(_(f"no code for parser."))
                return
                
            # ------------------------------------------
            # Speichere den Python-Code als Datei
            # ------------------------------------------
            file_path      = os.path.basename(script_name)
            directory_path = os.path.dirname (script_name) + "/tmp"
            
            directory_path = directory_path.replace('\\', '/')
            python_file    = directory_path + "/" + file_path + ".py"
            bytecode_file  = python_file + ".pyc"
            
            if not os.path.exists(directory_path):
                try:
                    os.makedirs(directory_path)
                except PermissionError as e:
                    showError(_("no permissions to create directory"))
                    return False
                except Exception as e:
                    showError(_(f"unexpected error occured:\n{e}"))
                    return False
            try:
                with open(python_file, "w") as f:
                    f.write(python_code)
                    f.close()
                    
            except PermissionError as e:
                showError(_(f"no permissions to open script file:\n{e}"))
                return
            except Exception as e:
                showError(_(f"unexpected error occured:\n{e}"))
                return
            
            # ------------------------------------------
            # Kompiliere den Python-Code in Bytecode
            # und speichere ihn ...
            # ------------------------------------------
            compiled_code = compile(python_code, python_file, "exec")
            try:
                with open(bytecode_file, "wb") as f:
                    marshal.dump(compiled_code, f)
            except PermissionError as e:
                showError(_("no permissions to write byte code file."))
                return
            except Exception as e:
                showError(_(f"unexpected error occured:\n{e}"))
                return
            
            print("Python Code:")
            print(python_code)
            
            parser.run_bytecode(bytecode_file)
            
        except Exception as e:
            self.showExceptionHandler(e)
            return
            
    # --------------------------------------
    # Extrahiere spezifische Informationen
    # Gehe zum letzten Traceback-Eintrag
    # --------------------------------------
    def showExceptionHandler(self, e):
        tb = e.__traceback__
        while tb.tb_next:
            tb = tb.tb_next
        
        err_line  = _(f"Error in File: {tb.tb_frame.f_code.co_filename}\n")
        err_line += _(f"Error in Line: {tb.tb_lineno}\n")
        err_line += _(f"Error Message: {str(e)}")
        
        showError(err_line)
        return
    
    # ----------------------
    # Ergebnisse anzeigen
    # ----------------------
    def display_comment_summary(self):
        showInfo(
            f"comments: {genv.source_comments}\n"
            f"tokens:   {genv.source_tokens}  \n"
            f"errors:   {genv.source_errors}  ")
        
        #one_liner = _("online comments:\n")
        #
        #for line_num, matches in result["single_line"]:
        #    one_liner += f"Line {line_num}: {', '.join(matches)}"
        #    one_liner += "\n"
        # 
        # two_liner = _("multie line comments:\n")
        # 
        # for start, end, comment in result["multi_line"]:
        #     two_liner += f"start line: {start} end line: {end}:\n{comment}"
        #     two_liner += f"\n"
        # 
        # err_liner = _("comments with error's:\n")
        # 
        # for start, end, error, comment in result["errors"]:
        #     err_liner += f"start line: {start} end line: {end}: "
        #     err_liner += f"{error}\n{comment}"
        #     err_liner += f"\n"
        #     
        # showInfo(
        #     one_liner + "\n" +
        #     two_liner + "\n" +
        #     err_liner)
 
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super(LineNumberArea, self).__init__(editor)
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
        evt_array = [
            [ lambda: setattr(self, 'evt_on_enter'      , None) or self.evt_on_enter       , "OnGotFocus"   ],
            [ lambda: setattr(self, 'evt_on_leave'      , None) or self.evt_on_leave       , "OnLeftFocus"  ],
            [ lambda: setattr(self, 'evt_on_key_down'   , None) or self.evt_on_key_down    , "OnKeyDown"    ],
            [ lambda: setattr(self, 'evt_on_key_press'  , None) or self.evt_on_key_press   , "OnKeyPress"   ],
            [ lambda: setattr(self, 'evt_on_key_up'     , None) or self.evt_on_key_up      , "OnKeyUp"      ],
            [ lambda: setattr(self, 'evt_on_mouse_down' , None) or self.evt_on_mouse_down  , "OnMouseDown"  ],
            [ lambda: setattr(self, 'evt_on_mouse_press', None) or self.evt_on_mouse_press , "OnMousePress" ],
            [ lambda: setattr(self, 'evt_on_mouse_up'   , None) or self.evt_on_mouse_up    , "OnMouseUp"    ],
            [ lambda: setattr(self, 'evt_on_form_create', None) or self.evt_on_form_create , "OnFormCreate" ],
            [ lambda: setattr(self, 'evt_on_form_close' , None) or self.evt_on_form_close  , "OnFormClose"  ],
            [ lambda: setattr(self, 'evt_on_form_show'  , None) or self.evt_on_form_show   , "OnFormShow"   ]
        ]
        for evt in evt_array:
            evt[0] = addEventField(self,evt[1])
            
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
        
        self.content = FormDesigner()
        #self.content = myGridViewerOverlay(self.parent)
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
        
        lay_array = [
            [ self.scroll_up    , 0,2 ],
            [ self.scroll_left  , 1,1 ],
            [ self.object_widget, 1,0 ],
            [ self.content      , 1,2 ],
            [ self.scroll_right , 1,3 ],
            [ self.scroll_down  , 2,2 ]
        ]
        for lay in lay_array:
            self.layout.addWidget(lay[0], lay[1], lay[2])
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
            DebugPrint("debug text")
    
    def start(self):
        self.running = True
        super().start()
    
    def stop(self):
        self.running = False
    

class c64Bildschirm(QWidget):
    def __init__(self, parent=None):
        super(c64Bildschirm, self).__init__(parent)
        #
        self.parent  = parent
        self.painter = QPainter()
        #
        self.setMinimumWidth ( 640 )
        self.setMaximumWidth ( 640 )
        #
        self.setMinimumHeight( 315 )
        self.setMaximumHeight( 315 )
        
        self.setStyleSheet("background-color:blue;")
        
        self.worker_thread = c64WorkerThread(self)
    
    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setBrush(QBrush(QColor(0, 158, 255)))
        self.painter.drawRect(1,1,320 + 64 + 20, 200 + 64 + 50)
        
        self.painter.setBrush(QBrush(QColor(0, 108, 255)))
        self.painter.drawRect(20,20,320 + 44, 200 + 64 + 14)
        
        font = QFont("C64 Elite Mono",9)
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

class C64GraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super(C64GraphicsView, self).__init__(parent)
        self.parent = parent
    
    def mouseMoveEvent(self, event):
        # Konvertiere die Mausposition in Szenenkoordinaten
        scene_pos = self.mapToScene(event.pos())
        self.parent.mouseMove(
            scene_pos.x(),
            scene_pos.y())
        super().mouseMoveEvent(event)

class C64GraphicScene(QGraphicsScene):
    def __init__(self, parent=None):
        super(C64GraphicScene, self).__init__(parent)
        self.parent = parent
    
    def mouseMoveEvent(self, event):
        # Mausposition direkt aus Szenenereignis
        scene_pos = event.scenePos()
        self.parent.mouseMove(
            scene_pos.x(),
            scene_pos.y())
        super().mouseMoveEvent(event)
        
class C64Keyboard(QWidget):
    def __init__(self, parent=None):
        super(C64Keyboard, self).__init__(parent)
        
        #self.setMouseTracking(True)
        layout = QVBoxLayout()
        
        self.setMinimumWidth(700)
        self.setMinimumHeight(270)
        #
        self.graphics_view  = C64GraphicsView(self)
        self.graphics_scene = C64GraphicScene(self)
        
        #
        self.graphics_view.setScene(self.graphics_scene)
        self.graphics_view.setSceneRect(0, 0, 1400, 270)
        #
        self.highlight_layer = None
        
        # ScrollArea erstellen
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.resize(900,310)
        #
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy  (Qt.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        content_widget.setMinimumWidth(1000)
        content_widget.setMinimumHeight(280)
        
        # Beispielhaftes Layout für Tasten der C64-Tastatur
        self.keys = [
            {"x":  10, "y": 10,           "w": 53, "h": 53, "label": "<-" , "ll": "" , "sub_chars": ["<-", ""] },
            {"x":  10+( 1 * 56), "y": 10, "w": 53, "h": 53, "label": "!"  , "ll": "1", "sub_chars": ["1", "BLK"] },
            {"x":  10+( 2 * 56), "y": 10, "w": 53, "h": 53, "label": "\"" , "ll": "2", "sub_chars": ["2", "WHT"]  },
            {"x":  10+( 3 * 56), "y": 10, "w": 53, "h": 53, "label": "#"  , "ll": "3", "sub_chars": ["3", "RED"]  },
            {"x":  10+( 4 * 56), "y": 10, "w": 53, "h": 53, "label": "$"  , "ll": "4", "sub_chars": ["4", "CYN"]  },
            {"x":  10+( 5 * 56), "y": 10, "w": 53, "h": 53, "label": "%"  , "ll": "5", "sub_chars": ["5", "PUR"]  },
            {"x":  10+( 6 * 56), "y": 10, "w": 53, "h": 53, "label": "&"  , "ll": "6", "sub_chars": ["6", "GRN"]  },
            {"x":  10+( 7 * 56), "y": 10, "w": 53, "h": 53, "label": "\'" , "ll": "7", "sub_chars": ["7", "BLU"]  },
            {"x":  10+( 8 * 56), "y": 10, "w": 53, "h": 53, "label": "("  , "ll": "8", "sub_chars": ["8", "YEL"]  },
            {"x":  10+( 9 * 56), "y": 10, "w": 53, "h": 53, "label": ")"  , "ll": "9", "sub_chars": ["9", "ON" ]  },
            {"x":  10+(10 * 56), "y": 10, "w": 53, "h": 53, "label": "RVS", "ll": "0", "sub_chars": ["0", "OFF"]  },
            
            {"x":  10+(11 * 56), "y": 10, "w": 53, "h": 53, "label": "+"        , "ll": "0", "sub_chars": [chr(0x00b2), chr(0x253c) ]  },
            {"x":  10+(12 * 56), "y": 10, "w": 53, "h": 53, "label": "-"        , "ll": "0", "sub_chars": [chr(0xe07c), chr(0x00b3) ]  },
            {"x":  10+(13 * 56), "y": 10, "w": 53, "h": 53, "label": chr(0x00a3), "ll": "0", "sub_chars": [chr(0xe0e8), chr(0x25e4) ]  },
            {"x":  10+(14 * 56), "y": 10, "w": 53, "h": 53, "label": "CLR\nHOME", "ll": "0", "sub_chars": ["!", "@"]  },
            {"x":  10+(15 * 56), "y": 10, "w": 53, "h": 53, "label": "INST\nDEL", "ll": "0", "sub_chars": ["!", "@"]  },
            
            {"x":  10+(16 * 56)+42, "y": 10, "w": 84, "h": 53, "label": "F1"  , "ll": "0", "sub_chars": ["!", "@"]  },
            
            #
            {"x":  10,           "y": 64, "w": 90, "h": 53, "label": "CTRL", "ll": "", "sub_chars": ["!", "@"]  },
            #
            {"x": 105,           "y": 64, "w": 53, "h": 53, "label": "Q" , "ll": "", "sub_chars": [chr(0xe0ab), chr(0xe071) ]  },
            {"x": 105+( 1 * 56), "y": 64, "w": 53, "h": 53, "label": "W" , "ll": "", "sub_chars": [chr(0xe0b3), chr(0xe077) ]  },
            {"x": 105+( 2 * 56), "y": 64, "w": 53, "h": 53, "label": "E" , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 105+( 3 * 56), "y": 64, "w": 53, "h": 53, "label": "R" , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 105+( 4 * 56), "y": 64, "w": 53, "h": 53, "label": "T" , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 105+( 5 * 56), "y": 64, "w": 53, "h": 53, "label": "Y" , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 105+( 6 * 56), "y": 64, "w": 53, "h": 53, "label": "U" , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 105+( 7 * 56), "y": 64, "w": 53, "h": 53, "label": "I" , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 105+( 8 * 56), "y": 64, "w": 53, "h": 53, "label": "O" , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 105+( 9 * 56), "y": 64, "w": 53, "h": 53, "label": "P" , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 105+(10 * 56), "y": 64, "w": 53, "h": 53, "label": "@" , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 105+(11 * 56), "y": 64, "w": 53, "h": 53, "label": "*" , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 105+(12 * 56), "y": 64, "w": 53, "h": 53, "label": "!" , "ll": "", "sub_chars": ["!", "@"]  },
            #
            {"x": 106+(13 * 56), "y": 64, "w": 84, "h": 53, "label": "RESTORE"   , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 106+(13 * 56)+84+30, "y": 64, "w": 84, "h": 53, "label": "F3"  , "ll": "0", "sub_chars": ["!", "@"]  },
            #
            {"x":  0, "y": 117, "w": 53, "h": 53, "label": "RUN\nSTOP"  , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 56, "y": 117, "w": 53, "h": 53, "label": "SHIFT\nLOCK", "ll": "", "sub_chars": ["!", "@"]  },
            #
            {"x": 56+( 1 * 56), "y": 117, "w": 53, "h": 53, "label": "A", "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 56+( 2 * 56), "y": 117, "w": 53, "h": 53, "label": "S", "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 56+( 3 * 56), "y": 117, "w": 53, "h": 53, "label": "D", "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 56+( 4 * 56), "y": 117, "w": 53, "h": 53, "label": "F", "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 56+( 5 * 56), "y": 117, "w": 53, "h": 53, "label": "G", "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 56+( 6 * 56), "y": 117, "w": 53, "h": 53, "label": "H", "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 56+( 7 * 56), "y": 117, "w": 53, "h": 53, "label": "J", "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 56+( 8 * 56), "y": 117, "w": 53, "h": 53, "label": "K", "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 56+( 9 * 56), "y": 117, "w": 53, "h": 53, "label": "L", "ll": "", "sub_chars": ["!", "@"]  },
            #
            {"x": 56+(10 * 56), "y": 117, "w": 53, "h": 53, "label": "[", "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 56+(11 * 56), "y": 117, "w": 53, "h": 53, "label": "]", "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 56+(12 * 56), "y": 117, "w": 53, "h": 53, "label": "=", "ll": "", "sub_chars": ["!", "@"]  },
            #
            {"x": 56+(13 * 56), "y": 117, "w": 129, "h": 53, "label": "RETURN", "ll": "", "sub_chars": ["!", "@"]  },
            {"x": 56+(13 * 56)+129+36, "y": 117, "w": 84, "h": 53, "label": "F5"  , "ll": "0", "sub_chars": ["!", "@"]  },
            #
            {"x":  0, "y": 117+54, "w": 53, "h": 53, "label": "CBM"  , "ll": "", "sub_chars": ["!", "@"] },
            {"x": 56, "y": 117+54, "w": 79, "h": 53, "label": "SHIFT"  , "ll": "", "sub_chars": ["!", "@"] },
            #
            {"x": ( 1 * 56)+80+3, "y": 117+54, "w": 53, "h": 53, "label": "Z"  , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": ( 2 * 56)+80+3, "y": 117+54, "w": 53, "h": 53, "label": "X"  , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": ( 3 * 56)+80+4, "y": 117+54, "w": 53, "h": 53, "label": "C"  , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": ( 4 * 56)+80+4, "y": 117+54, "w": 53, "h": 53, "label": "V"  , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": ( 5 * 56)+80+4, "y": 117+54, "w": 53, "h": 53, "label": "B"  , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": ( 6 * 56)+80+4, "y": 117+54, "w": 53, "h": 53, "label": "N"  , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": ( 7 * 56)+80+5, "y": 117+54, "w": 53, "h": 53, "label": "M"  , "ll": "", "sub_chars": ["!", "@"]  },
            #
            {"x": ( 8 * 56)+80+5, "y": 117+54, "w": 53, "h": 53, "label": "<"  , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": ( 9 * 56)+80+5, "y": 117+54, "w": 53, "h": 53, "label": ">"  , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": (10 * 56)+80+5, "y": 117+54, "w": 53, "h": 53, "label": "?"  , "ll": "", "sub_chars": ["!", "@"]  },
            #
            {"x": (11 * 56)+80+5, "y": 117+54, "w": 84, "h": 53, "label": "SHIFT"  , "ll": "", "sub_chars": ["!", "@"]  },
            #
            {"x": (11 * 56)+80+9+84, "y": 117+54, "w": 60, "h": 53, "label": "CRSR"  , "ll": "", "sub_chars": ["!", "@"]  },
            {"x": (11 * 56)+80+13+84+60, "y": 117+54, "w": 60, "h": 53, "label": "CRSR"  , "ll": "", "sub_chars": ["!", "@"]  },
            
            {"x": (11 * 56)+80+13+84+158, "y": 117+54, "w": 84, "h": 53, "label": "F7"  , "ll": "0", "sub_chars": ["!", "@"]  },
            #
            {"x": ( 1 * 56)+100+3, "y": 117+110, "w": 500, "h": 53, "label": "SPACE"  , "ll": "", "sub_chars": ["!", "@"]  },
        ]
        #
        self.load_c64_font()
        self.draw_keyboard()
        
        content_layout.addWidget(self.graphics_view)
        scroll_area.setWidget(content_widget)
        
        layout.addWidget(scroll_area)
    
    def load_c64_font(self):
        font_id = QFontDatabase.addApplicationFont("C64_Pro-STYLE.ttf")
        if font_id == -1:
            DebugPrint("Fehler beim Laden des C64 Pro Fonts.")
            sys.exit(1)
        else:
            self.c64_font = QFont("C64 Pro Mono", 12)
            self.ari_font = QFont("Arial", 8)
            DebugPrint("C64 Pro Font erfolgreich geladen.")
    
    def draw_keyboard(self):
        for i, key in enumerate(self.keys):
            self.draw_key(
                key["x"],
                key["y"],
                key["w"],
                key["h"],
                key["label"],
                key["sub_chars"], i)
    
    def draw_key(self, x, y, width, height, label, sub_chars, index):
        key_path = QPainterPath()
        key_path.addRoundedRect(QRectF(x, y, width, height), 5, 5)
        
        key_rect = QGraphicsPathItem(key_path)
        key_rect.setBrush(QBrush(QColor(200, 200, 200)))
        key_rect.setPen(QPen(QColor(0, 0, 0), 2))
        self.graphics_scene.addItem(key_rect)
        
        # Weißes Rechteck innerhalb der Taste mit präzisen Abständen
        small_rect_x      = x + 8
        small_rect_y      = y + 5
        #
        small_rect_width  = width - 9 - 5
        small_rect_height = height - 9 - 5
        
        small_rect_path = QPainterPath()
        small_rect_path.addRect(QRectF(
            small_rect_x,
            small_rect_y,
            small_rect_width,
            small_rect_height))
        
        small_rect = QGraphicsPathItem(small_rect_path)
        small_rect.setBrush(QBrush(QColor(255, 255, 255)))  # Weiß
        small_rect.setPen(QPen(Qt.NoPen))
        self.graphics_scene.addItem(small_rect)
        
        # Text für die Taste
        text = self.graphics_scene.addText(label)
        text.setDefaultTextColor(Qt.black)
        text.setFont(self.ari_font)
        text.setPos(x + 10, y + 5)
        
        # Zusätzliche Zeichen mit Rahmen
        sub_char_width   = 16  # Breite und Höhe eines Char-Rahmens
        sub_char_height  = 16
        sub_char_spacing =  5  # Abstand zwischen den beiden Zeichen
        
        lbl_list = [
            "<-", "CTRL", "RUN\nSTOP", "SHIFT\nLOCK", "CBM", "SHIFT",
            "SPACE", "RETURN", "RESTORE", "CLR\nHOME", "INST\nDEL",
            "F1","F2","F3","F4","F5","F6","F7","F8",
        ]
        if label in lbl_list:
            key_rect.setData(0, index)  # Speichert den Index im Datenfeld des Items
            return True
        try:
            achr = [
                "1","2","3","4","5","6","7","8","9","0",
                "BLK","WHT","RED","CYN","PUR","GRN","BLU","YEL","ON","OFF"
            ]
            for i, char in enumerate(sub_chars):
                if char in achr:
                    sub_char_spacing = 1
                    # Berechnen der Position
                    sub_x = x + 6  + i * (sub_char_width + sub_char_spacing)
                    sub_y = y + height - sub_char_height - 5
                    
                    sub_text = QGraphicsTextItem(char)
                    sub_text.setDefaultTextColor(Qt.black)
                    sub_text.setFont(QFont("C64 Pro Mono", 8))
                    sub_text.setPos(sub_x-6, sub_y - 3)
                    
                    self.graphics_scene.addItem(sub_text)
                    #
                else:
                    sub_char_spacing = 5
                    # Berechnen der Position
                    sub_x = x + 10 + i * (sub_char_width + sub_char_spacing)
                    sub_y = y + height - sub_char_height - 5
                    
                    # Rahmen zeichnen
                    sub_char_path = QPainterPath()
                    sub_char_path.addRect(QRectF(sub_x, sub_y, sub_char_width, sub_char_height))
                    
                    sub_char_rect = QGraphicsPathItem(sub_char_path)
                    sub_char_rect.setBrush(QBrush(QColor(255, 255, 255)))  # Weißer Hintergrund
                    sub_char_rect.setPen(QPen(QColor(0, 0, 0), 1))  # Schwarzer Rahmen
                    self.graphics_scene.addItem(sub_char_rect)
                    
                    # Zeichen im Rahmen
                    sub_text = QGraphicsTextItem(char)
                    sub_text.setDefaultTextColor(Qt.black)
                    sub_text.setFont(QFont("C64 Pro Mono", 8))
                    sub_text.setPos(sub_x-2, sub_y - 1)
                    
                    self.graphics_scene.addItem(sub_text)
                    #
        except Exception as e:
            showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
            return False
        
        # Speichern des Index im Key-Daten
        key_rect.setData(0, index)  # Speichert den Index im Datenfeld des Items
        return True
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            pos = event.pos()
            x, y = pos.x(), pos.y()
            
            # Prüfen, ob der Klick innerhalb einer Taste erfolgt ist
            for key_index, key in enumerate(self.keys):
                if key["x"] <= x <= key["x"] + key["w"] and key["y"] <= y <= key["y"] + key["h"]:
                    self.handle_key_press(key_index, key)
                    return
    
    # ------------------------------------------
    # Prüfen, ob die Maus über einer Taste ist
    # ------------------------------------------
    def mouseMove(self, x,y):
        for key in self.keys:
            if key["x"] <= x <= key["x"] + key["w"] and key["y"] <= y <= key["y"] + key["h"]:
                self.show_highlight(key["x"], key["y"], key["w"], key["h"], key["label"])
                return
        
        # --------------------------------------
        # Kein Treffer, Layer ausblenden
        # --------------------------------------
        self.hide_highlight()
    
    def show_highlight(self, x, y, width, height, label):
        if self.highlight_layer is None:
            # Initialisierung des Highlight-Layers
            highlight_path = QPainterPath()
            highlight_path.addRoundedRect(QRectF(x, y, width, height), 10, 10)
            
            self.highlight_layer = QGraphicsPathItem(highlight_path)
            self.highlight_layer.setBrush(QBrush(QColor(255, 255, 0, 128)))  # Gelb mit Transparenz
            self.highlight_layer.setPen(QPen(Qt.NoPen))  # Kein Rahmen
            self.graphics_scene.addItem(self.highlight_layer)
        else:
            # Highlight-Layer aktualisieren
            highlight_path = QPainterPath()
            highlight_path.addRoundedRect(QRectF(x, y, width, height), 10, 10)
            self.highlight_layer.setPath(highlight_path)
        
        # Text erneut zeichnen
        highlight_text = self.graphics_scene.addText(label)
        highlight_text.setDefaultTextColor(Qt.black)
        highlight_text.font().setBold(True)
        highlight_text.setPos(x + 10, y + 5)  # Zentriert über dem kleinen Rechteck
        highlight_text.setZValue(1)
    
    def hide_highlight(self):
        if self.highlight_layer is not None:
            self.graphics_scene.removeItem(self.highlight_layer)
            self.highlight_layer = None
        
        # Alle Texte des Highlight-Layers entfernen
        for item in self.graphics_scene.items():
            if isinstance(item, QGraphicsPathItem):
                continue
            if item.zValue() == 1:  # Entfernt nur Highlight-Texte
                self.graphics_scene.removeItem(item)
    
    def handle_key_press(self, index, key):
        DebugPrint(f"Taste {key['label']} gedrückt (Index: {index})")

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
        self.btn_move_add_2 = QPushButton(_("Add"))
        self.btn_move_clr_1 = QPushButton(_("Remove"))
        self.btn_move_clr_2 = QPushButton(_("Clear"))
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
        DebugPrint("add")
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
        DebugPrint("clr all")

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
            configfile.close()
    
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
            loc_array = [
                [ "name"            , 126, self.project_name             ],
                [ "author"          ,  64, self.project_author           ],
                [ "version"         ,  32, self.project_version          ],
                [ "e-mail"          ,  64, self.project_email            ],
                [ "lastmod"         ,  32, self.project_lastmod          ],
                [ "content-type"    ,  32, self.project_content_type     ],
                [ "content-encoding",  32, self.project_content_encoding ],
                [ "mime-type"       ,  32, self.project_mime_type        ],
                [ "language-team"   ,  32, self.project_language_team    ],
                [ "last-translater" ,  32, self.project_last_translater  ],
                [ "pot-create-date" ,  32, self.project_pot_create_date  ],
                [ "po-revision-date",  32, self.project_po_revision_date ]
            ]
            for loc in loc_array:
                try:
                    loc[2] = self.maxLength(genv.v__app__config[pro][loc[0]], loc[1])
                except Exception as e:
                    if e == loc[0]:
                        loc[2] = noan
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
        
        #DebugPrint(self.property_name + " : " + self.property_value)
        
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
            DebugPrint(f'Opening file: {selected_file}')
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

class CustomWidget0(QWidget):
    def __init__(self, parent_class, parent_tabs, parent_layout):
        super().__init__()
        self.parent_class  = parent_class
        self.parent_tabs   = parent_tabs
        self.parent_layout = parent_layout
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
        self.parent_class.javascript.hide()
        self.parent_class.python_tabs.hide()
        self.parent_class.prolog_tabs.hide()
        self.parent_class.fortran_tabs.hide()
        self.parent_class.lisp_tabs.hide()
        self.parent_class.basic_tabs.hide()
        self.parent_class.pe_windows_tabs.hide()
        self.parent_class.elf_linux_tabs.hide()
        self.parent_class.console_tabs.hide()
        self.parent_class.locale_tabs.hide()
        self.parent_class.setup_tabs.hide()
        self.parent_class.certssl_tabs.hide()
        self.parent_class.github_tabs.hide()
        self.parent_class.apache_tabs.hide()
        self.parent_class.mysql_tabs.hide()
        self.parent_class.squid_tabs.hide()
        self.parent_class.electro_tabs.hide()
        self.parent_class.c64_tabs.hide()
        self.parent_class.settings_tabs.hide()
        #
        tabser.show()
        
        self.set_null_state()
        self.parent_class.side_btn0.set_style()
        #self.parent_class.set_style()
    
    def set_null_state(self):
        parent = self.parent_class
        side_buttons = [
            parent.side_btn0,
            parent.side_btn1,
            parent.side_btn2,
            parent.side_btn3,
            parent.side_btn4,
            parent.side_btn5,
            parent.side_btn6,
            parent.side_btn7,
            parent.side_btn8,
            parent.side_btn9,
            parent.side_btn10,
            parent.side_btn11,
            parent.side_btn12,
            parent.side_btn13,
            parent.side_btn14,
            parent.side_btn15,
            parent.side_btn16,
            parent.side_btn17,
            parent.side_btn18,
            parent.side_btn19,
            parent.side_btn20,
            parent.side_btn21,
            parent.side_btn22,
            parent.side_btn23,
            parent.side_btn24
        ]
        for btn in side_buttons:
            btn.state = 0
            btn.set_style()
        return
        
    def show_context_menu(self):
        self.context_menu.exec_(self.mapToGlobal(self.arrow_button.pos()))

class scrollBoxTableCreatorDBF(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setLayout(QVBoxLayout())
        
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        
        scroll_content = QWidget()
        scroll_content.setLayout(QVBoxLayout())

        if genv.v_layout_f_edit == None:
            genv.v_layout_f_edit = QVBoxLayout()
            genv.v_layout_t_edit = QVBoxLayout()
            genv.v_layout_l_edit = QVBoxLayout()
            genv.v_layout_p_edit = QVBoxLayout()
            genv.v_layout_k_edit = QVBoxLayout()
            genv.v_layout_d_push = QVBoxLayout()
        
        hlayout = QHBoxLayout()
        vlayout = QVBoxLayout()
        
        le = QLineEdit(); l1 = QLabel(_("Name:"))
        cb = QComboBox(); l2 = QLabel(_("Type:"))
        fl = QLineEdit(); l3 = QLabel(_("Length:"))
        pr = QLineEdit(); l4 = QLabel(_("Prec:"))
        pk = QComboBox(); l5 = QLabel(_("Pry.Key:"))
        #
        db = QPushButton(_("DEL"))
        db.setMinimumWidth(32)
        db.setMinimumHeight(18)
        
        cb_array = [
            _("C CHAR"),
            _("N NUMERIK"),
            _("F FLOAT"),
            _("D DATE"),
            _("L LOGICAL"),
            _("M MEMO"),
            _("B BINARY"),
            _("G GENERAL"),
            _("P PICTURE"),
            _("I INTEGER"),
            _("Y CURRENCY")
        ]
        for item in cb_array:
            cb.addItem(item)
        
        pk.addItem(_("TRUE"))
        pk.addItem(_("FALSE"))
        
        genv.f_edit.append(le)
        genv.t_edit.append(cb)
        genv.l_edit.append(fl)
        genv.p_edit.append(pr)
        genv.k_edit.append(pk)
        #
        genv.d_push.append(db)
        
        if len(genv.f_edit) < 2:
            genv.v_layout_f_edit.addWidget(l1)
        if len(genv.t_edit) < 2:
            genv.v_layout_t_edit.addWidget(l2)
        if len(genv.l_edit) < 2:
            genv.v_layout_l_edit.addWidget(l3)
        if len(genv.p_edit) < 2:
            genv.v_layout_p_edit.addWidget(l4)
        if len(genv.k_edit) < 2:
            genv.v_layout_k_edit.addWidget(l5)
        
        tmp = 1
        for item in genv.f_edit:
            genv.v_layout_f_edit.addWidget(item)
        for item in genv.t_edit:
            genv.v_layout_t_edit.addWidget(item)
        for item in genv.l_edit:
            genv.v_layout_l_edit.addWidget(item)
        for item in genv.p_edit:
            genv.v_layout_p_edit.addWidget(item)
        for item in genv.k_edit:
            genv.v_layout_k_edit.addWidget(item)
        for item in genv.d_push:
            if tmp >= 2:
                genv.v_layout_d_push.addWidget(item)
                tmp = 3
            else:
                spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
                genv.v_layout_d_push.addItem(spacer)
                tmp = 2
        
        hlayout.addLayout(genv.v_layout_f_edit)
        hlayout.addLayout(genv.v_layout_t_edit)
        hlayout.addLayout(genv.v_layout_l_edit)
        hlayout.addLayout(genv.v_layout_p_edit)
        hlayout.addLayout(genv.v_layout_k_edit)
        #
        hlayout.addLayout(genv.v_layout_d_push)
        vlayout.addLayout(hlayout)
        
        scroll_content.layout().addLayout(vlayout)
        scroll_area.setWidget(scroll_content)
        
        self.layout().addWidget(scroll_area)

class clearChildTreeItems():
    def __init__(self, parent):
        self.parent = parent
    
    # --------------------------------------------------
    # remove project files from list, when double click
    # with mouse on a favorite item ...
    # --------------------------------------------------
    def remove(self):
        while self.parent.child_item_forms.rowCount() > 0:
            self.parent.child_item_forms.removeRow(0)
        
        while self.parent.child_item_reports.rowCount() > 0:
            self.parent.child_item_reports.removeRow(0)
        
        while self.parent.child_item_programs.rowCount() > 0:
            self.parent.child_item_programs.removeRow(0)
        
        while self.parent.child_item_images.rowCount() > 0:
            self.parent.child_item_images.removeRow(0)
        
        while self.parent.child_item_tables.rowCount() > 0:
            self.parent.child_item_tables.removeRow(0)
        
        while self.parent.child_item_queries.rowCount() > 0:
            self.parent.child_item_queries.removeRow(0)
        
        while self.parent.child_item_others.rowCount() > 0:
            self.parent.child_item_others.removeRow(0)

class CustomListWidget(QListWidget):
    def __init__(self, parent=None):
        super(CustomListWidget, self).__init__(parent)
        self.parent = parent
    
    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if not item:
            return
        
        file_path = item.text()
        
        # --------------------------------------------------
        # remove project files from list, when double click
        # with mouse on a favorite item ...
        # --------------------------------------------------
        i = clearChildTreeItems(self.parent)
        i.remove()
        
        self.parent.hlay_edit.clear()
        self.parent.hlay_edit.setText(file_path)
        self.parent.setup_favorites  (file_path)

class myProjectLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super(myProjectLineEdit, self).__init__(parent)
        self.parent = parent
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            folder = QFileDialog.getExistingDirectory(self, 'Ordner auswählen')
            if folder:
                DebugPrint(f"Ausgewählter Ordner: {folder}")
            
        super(myProjectLineEdit, self).mouseDoubleClickEvent(event)

class TableModelAll(QAbstractTableModel):
    def __init__(self, data):
        super(TableModelAll, self).__init__()
        self._data = data
    
    def rowCount(self, index):
        return len(self._data)
    
    def columnCount(self, index):
        return len(self._data[0])
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        headers = [
            _("Forms"),
            _("Programs"),
            _("Reports"),
            _("Tables"),
            _("Images"),
            _("SQL"),
            _("Other")
        ]
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return headers[section]
            if orientation == Qt.Vertical:
                return str(section)
    
    def updateData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()
        self.modelReset.emit()

class TableModelForms(QAbstractTableModel):
    modelReset = pyqtSignal()
    
    def __init__(self, data):
        super(TableModelForms, self).__init__()
        self._data = data
    
    def rowCount(self, index):
        return len(self._data)
    
    def columnCount(self, index):
        return len(self._data[0])
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
    
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False
    
    def flags(self, index):
        if index.column() == 1:  # Nur die zweite Spalte editierbar machen
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return     Qt.ItemIsSelectable | Qt.ItemIsEnabled
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        headers = [
            _("Forms"),
            _("Remarks")
        ]
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return headers[section]
            if orientation == Qt.Vertical:
                return str(section)
    
    def updateData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()
        self.modelReset.emit()

class TableModelPrograms(QAbstractTableModel):
    def __init__(self, data):
        super(TableModelPrograms, self).__init__()
        self._data = data
    
    def rowCount(self, index):
        return len(self._data)
    
    def columnCount(self, index):
        return len(self._data[0])
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        headers = [
            _("Programs"),
            _("Remarks")
        ]
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return headers[section]
            if orientation == Qt.Vertical:
                return str(section)
    
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False
    
    def flags(self, index):
        if index.column() == 1:  # Nur die zweite Spalte editierbar machen
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return     Qt.ItemIsSelectable | Qt.ItemIsEnabled
    
    def updateData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

class TableModelReports(QAbstractTableModel):
    def __init__(self, data):
        super(TableModelReports, self).__init__()
        self._data = data
    
    def rowCount(self, index):
        return len(self._data)
    
    def columnCount(self, index):
        return len(self._data[0])
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
    
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False
    
    def flags(self, index):
        if index.column() == 1:  # Nur die zweite Spalte editierbar machen
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return     Qt.ItemIsSelectable | Qt.ItemIsEnabled
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        headers = [
            _("Reports"),
            _("Remarks")
        ]
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return headers[section]
            if orientation == Qt.Vertical:
                return str(section)
    
    def updateData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

class TableModelTables(QAbstractTableModel):
    def __init__(self, data):
        super(TableModelTables, self).__init__()
        self._data = data
    
    def rowCount(self, index):
        return len(self._data)
    
    def columnCount(self, index):
        return len(self._data[0])
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
    
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False
    
    def flags(self, index):
        if index.column() == 1:  # Nur die zweite Spalte editierbar machen
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return     Qt.ItemIsSelectable | Qt.ItemIsEnabled
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        headers = [
            _("Tables"),
            _("Remarks")
        ]
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return headers[section]
            if orientation == Qt.Vertical:
                return str(section)
    
    def updateData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

class TableModelImages(QAbstractTableModel):
    def __init__(self, data):
        super(TableModelImages, self).__init__()
        self._data = data
    
    def rowCount(self, index):
        return len(self._data)
    
    def columnCount(self, index):
        return len(self._data[0])
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
    
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False
    
    def flags(self, index):
        if index.column() == 1:  # Nur die zweite Spalte editierbar machen
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return     Qt.ItemIsSelectable | Qt.ItemIsEnabled
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        headers = [
            _("Images"),
            _("Remarks")
        ]
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return headers[section]
            if orientation == Qt.Vertical:
                return str(section)
    
    def updateData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

class TableModelQueries(QAbstractTableModel):
    def __init__(self, data):
        super(TableModelQueries, self).__init__()
        self._data = data
    
    def rowCount(self, index):
        return len(self._data)
    
    def columnCount(self, index):
        return len(self._data[0])
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
    
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False
    
    def flags(self, index):
        if index.column() == 1:  # Nur die zweite Spalte editierbar machen
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return     Qt.ItemIsSelectable | Qt.ItemIsEnabled
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        headers = [
            _("Query"),
            _("Remarks")
        ]
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return headers[section]
            if orientation == Qt.Vertical:
                return str(section)
    
    def updateData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

class TableModelOthers(QAbstractTableModel):
    def __init__(self, data):
        super(TableModelOthers, self).__init__()
        self._data = data
    
    def rowCount(self, index):
        return len(self._data)
    
    def columnCount(self, index):
        return len(self._data[0])
    
    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
    
    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index, [Qt.DisplayRole, Qt.EditRole])
            return True
        return False
    
    def flags(self, index):
        if index.column() == 1:  # Nur die zweite Spalte editierbar machen
            return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
        return     Qt.ItemIsSelectable | Qt.ItemIsEnabled
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        headers = [
            _("Other"),
            _("Remarks")
        ]
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return headers[section]
            if orientation == Qt.Vertical:
                return str(section)
    
    def updateData(self, data):
        self.beginResetModel()
        self._data = data
        self.endResetModel()

class RotatedLabel(QLabel):
    def __init__(self, text, parent=None):
        super(RotatedLabel, self).__init__(text, parent)
        
        self.setMinimumSize(40, 100)  # Adjust the size as needed
        self.setMaximumWidth(40)
        self.setFont(QFont("Arial", 15, QFont.Bold))
        self.setStyleSheet("background: transparent;")  # Make the background transparent
    
    def sizeHint(self):
        fm = QFontMetrics(self.font())
        return QSize(fm.height(), fm.width(self.text()))
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # Create the gradient
        gradient = QLinearGradient(0, self.height(), 0, 0)
        gradient.setColorAt(0, QColor('blue'))
        gradient.setColorAt(1, QColor('navy'))
        painter.fillRect(self.rect(), gradient)
        
        # Draw the green line at the right edge
        pen = QPen(QColor('green'), 2)
        painter.setPen(pen)
        painter.drawLine(self.width() - 2, 0, self.width() - 2, self.parent().height())
        
        # Draw shadow
        shadow_pen = QPen(QColor(0, 0, 0, 160))
        shadow_pen.setWidth(3)
        painter.setPen(shadow_pen)
        transform = QTransform()
        transform.rotate(-90)
        painter.setTransform(transform)
        painter.drawText(-self.height() + 2, self.fontMetrics().height() + 2, self.text())
        
        # Draw text
        painter.setPen(QColor(Qt.white))
        painter.drawText(-self.height(), self.fontMetrics().height(), self.text())

class myCustomContextMenu(QMenu):
    def __init__(self, parent, item_text):
        super(myCustomContextMenu, self).__init__(parent)
        
        # Main horizontal layout for the custom menu
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 8)  # Add bottom margin to shift the label up
        self.main_layout.setSpacing(0)
        
        # Vertical label
        self.vertical_label = RotatedLabel(item_text + "..." + (' ' * 20), self)
        self.vertical_label.setStyleSheet("font: bold 15pt;")
        self.main_layout.addWidget(self.vertical_label, alignment=Qt.AlignBottom)
        
        # Vertical layout for menu items
        self.items_layout = QVBoxLayout()
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(0)
        self.main_layout.addLayout(self.items_layout)
        
        # Create a widget to hold the layout
        container_widget = QWidget(self)
        container_widget.setLayout(self.main_layout)
        
        # Add the container widget as a QWidgetAction to the menu
        action = QWidgetAction(self)
        action.setDefaultWidget(container_widget)
        self.addAction(action)
        
        self.setStyleSheet("""
            QMenu {
                background-color: navy;
                color: yellow;
                font-family: Arial;
                font-size: 11pt;
                font-style: italic;
                border: 2px outset gray;  /* Outset border */
            }
            QMenu::item {
                background-color: navy;
                font-weight: bold;
                font-style: italic;
            }
            QMenu::item:selected {
                background-color: green;
                color: yellow;
            }
        """)
        self.setMinimumWidth(200 + 84)  # Adjust the width to be 200 + 32 + 200 for text width
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        super(myCustomContextMenu, self).paintEvent(event)
    
    def addMenuAction(self, action, checked=False, enabled=True, shortcut=""):
        item_layout = QHBoxLayout()
        
        checkbox = QCheckBox(self)
        checkbox.setChecked(checked)
        item_layout.addWidget(checkbox)
        
        if enabled == True:
            self.bg_enabled = "navy"
            self.fg_enabled = "yellow"
            self.bg_hover   = "green"
            self.fg_hover   = "yellow"
        else:
            self.bg_enabled = "navy"
            self.fg_enabled = "darkgray"
            self.bg_hover   = "navy"
            self.fg_hover   = "darkgray"
            
        action_button = QPushButton(action.text(), self)
        action_button.setFixedWidth(200)  # Set the fixed width for the text
        action_button.clicked.connect(action.triggered)
        action_button.setFlat(True)
        action_button.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 5px;
                background: {self.bg_enabled};
                border: none;
                color: {self.fg_enabled};
                font-family: Arial;
                font-size: 11pt;
                font-style: italic;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: {self.bg_hover};
                color: {self.fg_hover};
            }}
        """)
        item_layout.addWidget(action_button)
        
        if shortcut:
            shortcut_label = QLabel(shortcut, self)
            shortcut_label.setStyleSheet("""
                QLabel {
                    text-align: left;
                    padding: 5px;
                    background: navy;
                    color: yellow;
                    font-family: Arial;
                    font-size: 11pt;
                    font-style: italic;
                    font-weight: bold;
                }
            """)
            item_layout.addWidget(shortcut_label)
        else:
            spacer = QWidget(self)
            item_layout.addWidget(spacer)
        
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(0)
        
        item_widget = QWidget(self)
        item_widget.setLayout(item_layout)
        self.items_layout.addWidget(item_widget)
        
        return action_button, checkbox
    
    def addMenuSeparator(self):
        separator = QFrame(self)
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: lightgray; min-height: 2px; max-height: 2px;")
        self.items_layout.addWidget(separator)

class applicationProjectWidget(QWidget):
    def __init__(self, parent=None):
        super(applicationProjectWidget, self).__init__(parent)
        
        self.setStyleSheet(_("ScrollBarCSS"))
        
        self.font   = QFont(genv.v__app__font, 11)
        self.model  = QStandardItemModel()
        self.result = QMessageBox.No        # default: no overwrite .pro file
        self.parent = parent
        
        self.newline1 = " = ./\n"
        self.newline2 = " = \n"
        
        self.db_path  = "paths"
        self.db_pro   = "dBaseProject"
        
        self.dbase_path    = "./"
        
        self.pro_files     = _("Project Files")
        self.pro_forms     = _("Forms")
        self.pro_reports   = _("Reports")
        self.pro_programs  = _("Programs")
        self.pro_tables    = _("Desktop Tables")
        self.pro_queries   = _("SQL")
        self.pro_images    = _("Images")
        self.pro_others    = _("Others")
        
        self.dbase_path_forms    = ""
        self.dbase_path_reports  = ""
        self.dbase_path_programs = ""
        self.dbase_path_tables   = ""
        self.dbase_path_images   = ""
        self.dbase_path_queries  = ""
        self.dbase_path_others   = ""
        
        self.child_item_forms    = None
        self.child_item_reports  = None
        self.child_item_programs = None
        self.child_item_tabless  = None
        self.child_item_queries  = None
        self.child_item_images   = None
        self.child_item_others   = None
        
        self.selected_item = None
        css_linestyle = _("editfield_css")
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        
        font3 = QFont(genv.v__app__font, 10)
        font3.setBold(True)
        
        font4 = QFont(genv.v__app__font, 10)

        splitter = QSplitter()
        splitter.setStyleSheet("QSplitter{width:4px;}")
        
        self.tree_view = QTreeView()
        self.tree_view.header().hide()
        self.tree_view.setMinimumWidth(180)
        self.tree_view.setFont(QFont(genv.v__app__font,11))
        self.tree_view.clicked.connect(self.on_item_clicked)
        
        # Enable custom context menu
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.open_context_menu)
        
        self.populate_tree()
        
        fav_layout = QHBoxLayout()
        fav_layout.setContentsMargins(0,0,0,0)
        
        fav_add = QPushButton("Add Favorite")
        fav_del = QPushButton("Remove Favorite")
        
        fav_add.setFont(font4)
        fav_del.setFont(font4)
        
        fav_add.setMinimumHeight(32)
        fav_del.setMinimumHeight(32)
        
        fav_add.clicked.connect(self.fav_add_clicked)
        fav_del.clicked.connect(self.fav_del_clicked)
        
        fav_layout.addWidget(fav_add)
        fav_layout.addWidget(fav_del)
        
        pro_layout = QHBoxLayout()
        pro_layout.setContentsMargins(0,0,0,0)
        
        pro_open   = QPushButton("Open Project")
        pro_clear  = QPushButton("Clear")
        pro_new    = QPushButton("New Project")
        
        pro_open .setMinimumHeight(36)
        pro_clear.setMinimumHeight(36)
        pro_new  .setMinimumHeight(36)
        
        pro_open .setFont(font3)
        pro_clear.setFont(font3)
        pro_new  .setFont(font3)
        
        pro_open .clicked.connect(self.pro_open_clicked)
        pro_clear.clicked.connect(self.pro_clear_clicked)
        pro_new  .clicked.connect(self.pro_new_clicked)
        
        pro_layout.addWidget(pro_open)
        pro_layout.addWidget(pro_clear)
        pro_layout.addWidget(pro_new)
        
        path_layout = QHBoxLayout()
        path_layout.setContentsMargins(0,0,0,0)
        #
        self.path_edit  = myProjectLineEdit()
        self.path_edit.setStyleSheet(css_linestyle)
        self.path_edit.setFont(font3)
        #
        self.path_push  = QPushButton(".X.")
        self.path_push.setMinimumWidth(30)
        self.path_push.setMinimumHeight(30)
        self.path_push.setFont(font3)
        self.path_push.clicked.connect(self.path_push_clicked)
        #
        path_layout.addWidget(self.path_edit)
        path_layout.addWidget(self.path_push)
        
        self.list_label = QLabel("Favorites:")
        self.list_label.setFont(font3)
        
        self.list_widget = CustomListWidget(self)
        self.list_widget.setMaximumHeight(150)
        self.list_widget.setFont(font4)
        
        self.icon_name = "open-folder-green.png"
        
        self.icon  = QIcon(os.path.join(genv.v__app__img__int__, self.icon_name))
        
        #item1 = QListWidgetItem(self.icon, 'Item 1')
        #item2 = QListWidgetItem(self.icon, 'Item 2')
        #item3 = QListWidgetItem(self.icon, 'Item 3')
        
        #self.list_widget.addItem(item1)
        #self.list_widget.addItem(item2)
        #self.list_widget.addItem(item3)

        hlay_pro = QHBoxLayout()
        hlay_pro.setContentsMargins(0,0,0,0)
        
        self.hlay_edit = QLineEdit()
        self.hlay_edit.setStyleSheet(css_linestyle)
        
        hlay_push = QPushButton(".A.")
        hlay_push.setMinimumWidth(30)
        hlay_push.setMinimumHeight(30)
        hlay_push.setFont(font3)
        #
        hlay_push.clicked.connect(self.pro_open_clicked)
        #
        hlay_pro.addWidget(self.hlay_edit)
        hlay_pro.addWidget(hlay_push)
        
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0,0,0,0)
        
        left_layout.addWidget(self.tree_view)
        left_layout.addLayout(path_layout)
        left_layout.addWidget(self.list_label)
        left_layout.addWidget(self.list_widget)
        
        left_layout.addLayout(hlay_pro)
        left_layout.addLayout(fav_layout)
        left_layout.addLayout(pro_layout)
        
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        
        
        self.data_all = [
            [1, 'A', 3.0, 'X', 'a', 'add', 'Alpha'],
            [2, 'B', 4.1, 'Y', 'b', 'sub', 'Beta'],
            [3, 'C', 5.2, 'Z', 'c', 'mul', 'Gamma'],
            [4, 'D', 6.3, 'W', 'd', 'div', 'Delta']
        ]
        
        self.data_forms    = [ ['name 1', 'remark 1'] ]
        self.data_reports  = [ ['name 2', 'remark 2'] ]
        self.data_programs = [ ['name 3', 'remark 3'] ]
        self.data_tables   = [ ['name 4', 'remark 4'] ]
        self.data_queries  = [ ['name 5', 'remark 5'] ]
        self.data_images   = [ ['name 6', 'remark 6'] ]
        self.data_others   = [ ['name 7', 'remark 7'] ]
                
        model = TableModelAll(self.data_all)
        
        self.list_view = QTableView()
        self.list_view.setModel(model)
        
        # Vertikale Header ausblenden
        self.list_view.verticalHeader().setVisible(False)
        self.list_view.setStyleSheet("QHeaderView::section{background-color:lightgreen;}")
        
        #self.list_view = QListView()
        self.list_view.setMinimumWidth(470)
        self.list_view.setFont(QFont(genv.v__app__font,11))
        
        self.lay_push = QHBoxLayout()
        self.add_push = QPushButton(_("Add"))
        self.clr_push = QPushButton(_("Clear All"))
        self.del_push = QPushButton(_("Remove"))
        #
        self.add_push.setStyleSheet(_(genv.css_button_style))
        self.clr_push.setStyleSheet(_(genv.css_button_style))
        self.del_push.setStyleSheet(_(genv.css_button_style))
        #
        self.add_push.setMinimumHeight(36)
        self.clr_push.setMinimumHeight(36)
        self.del_push.setMinimumHeight(36)
        #
        self.add_push.setFont(font3)
        self.clr_push.setFont(font3)
        self.del_push.setFont(font3)
        #
        self.lay_push.addWidget(self.add_push)
        self.lay_push.addWidget(self.clr_push)
        self.lay_push.addWidget(self.del_push)
        
        self.scroll_box_tab1 = scrollBoxTableCreatorDBF()
        
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.scroll_box_tab1, "dBase")
        self.tab_widget.addTab(QWidget(), "SQLite 3")
        self.tab_widget.addTab(QWidget(), "Tab 3")
        
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(0,0,0,0)
        
        right_layout.addWidget(self.list_view)
        right_layout.addLayout(self.lay_push)
        right_layout.addWidget(self.tab_widget)
        
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        
        main_layout.addWidget(splitter)
        
        # setup favorites ...
        try:
            genv.v__app__config.read(genv.v__app__favorites)
            for name, path in genv.v__app__config["dBaseFavorites"].items():
                item = QListWidgetItem(self.icon, path)
                self.list_widget.addItem(item)
        except Exception as e:
            self.messageBox(""
            + "Error: something went wrong during reading the Project paths."
            + "Command aborted.")
        
        self.setLayout(main_layout)
    
    def open_context_menu(self, position: QPoint):
        index = self.tree_view.indexAt(position)
        if index.isValid():
            item_text = self.model.itemFromIndex(index).text()
            
            # Context menu for tree items
            menu = myCustomContextMenu(self, item_text)
            
            action_array = [                      # check, open
                [ _("Run"),                       False, False, "F2"  ],
                [ _("Open in Designer"),          False, True,  ""    ],
                [ _("Open in Source Editor"),     False, True, ""    ],
                [ "--",                           False, True, ""    ],
                [ _("New"),                       False, True, ""    ],
                [ _("Add Files to Project..."),   False, True, ""    ],
                [ _("Delete"),                    True , True , "Del" ],
                [ "--",                           False, False, ""    ],
                [ _("New Folder"),                False, False, ""    ],
                [ "--",                           False, False, ""    ],
                [ _("Set as Main"),               False, False, ""    ],
                [ _("Exclude from Build"),        False, False, ""    ],
                [ _("Include in Target Image"),   False, False, ""    ],
                [ "--",                           False, False, ""    ],
                [ _("Project Properties"),        False, False, ""    ],
                [ _("File Properties"),           False, False, ""    ],
                [ _("Folder Properties"),         False, False, ""    ],
                [ "--",                           False, False, ""    ],
                [ _("Clear"),                     False, False, ""    ],
                [ _("Clear Items"),               False, False, ""    ]
            ]
            for act in action_array:
                action = QAction(act[0], self)
                if act[0] == "--":
                    menu.addMenuSeparator()
                else:
                    menu.addMenuAction(action, act[1], act[2], act[3])
        else:
            # Context menu for empty space
            menu = QMenu()
            menu.setStyleSheet(_("css_menu_button"))
            
            action1 = QAction(_("Add"), self)
            action2 = QAction(_("Clear"), self)
            action3 = QAction(_("Clear All"), self)
            
            menu.addAction(action1)
            menu.addSeparator()
            menu.addAction(action2)
            menu.addAction(action3)

        menu.exec_(self.tree_view.viewport().mapToGlobal(position))
    
    # -----------------------------------------------
    # search for item with <text> in the widget list.
    # if it present, then return True; else False...
    # -----------------------------------------------
    def isItemInList(self, text):
        for index in range(self.list_widget.count()):
            if self.list_widget.item(index).text() == text:
                return True
        return False
    
    # -----------------------------------------------
    # dialog, to open a new project file ...
    # -----------------------------------------------
    def pro_open_clicked(self):
        options  = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, file_pattern = QFileDialog.getOpenFileName(self,
            "Open File", "",
            "All Files (*);;Project Files (*.pro)",
            options=options)
        
        if len(file_path.strip()) < 1:
            self.messageBox("No Project file selected.")
            return
        
        if not os.path.isfile(file_path):
            messageBox("Selection is not a Project file.")
            return
        
        if os.path.isdir(file_path):
            self.messageBox(
            "Selection is a directory. But file expected.\n"
            "Command aborted.")
            return
        
        if not file_path.endswith(".pro"):
            self.messageBox(
            "Project files must have a postfix with .pro at end of name\n"
            "Command aborted.")
            return
            
        self.hlay_edit.setText(file_path)
        self.setup_favorites  (file_path)
    
    def setup_favorites(self, file_path):
        if not os.path.exists(file_path):
            try:
                with open(file_path, "w", encoding="utf-8") as configfile:
                    configfile.write(""
                    + "[paths]\n"
                    + "Path"       + self.newline1
                    + "Forms"      + self.newline1
                    + "Programs"   + self.newline1
                    + "Reports"    + self.newline1
                    + "Tables"     + self.newline1
                    + "Images"     + self.newline1
                    + "SQL"        + self.newline1
                    + "Other"      + self.newline1
                    + "\n"
                    + "[" + db_pro + "]\n"
                    + "Forms"      + self.newline2
                    + "Programs"   + self.newline2
                    + "Reports"    + self.newline2
                    + "Tables" + self.newline2
                    + "Images"     + self.newline2
                    + "SQL"        + self.newline2
                    + "Other"      + self.newline2)
                    configfile.close()
            except Exception as e:
                self.messageBox(""
                + "Error: file could not be open in write mode.\n"
                + file_path + "\n"
                + "Command aborted")
                return
        
        if not os.path.isfile(file_path):
            self.messageBox(""
            + "Error: You choose a file that is not a Project file.\n"
            + file_path + "\n"
            + "Command aborted.")
            return
        try:
            genv.v__app__config.read(file_path)
        except Exception as e:
            self.messageBox("Error: " + e)
            return
        try:
            self.dbase_path = genv.v__app__config[self.db_path]["Path"]
            #
            dbase_array = [
                [ self.child_item_forms,    self.dbase_forms_arr,    self.dbase_forms,    self.dbase_path_forms,    "Forms"    ],
                [ self.child_item_reports,  self.dbase_reports_arr,  self.dbase_reports,  self.dbase_path_reports,  "Reports"  ],
                [ self.child_item_programs, self.dbase_programs_arr, self.dbase_programs, self.dbase_path_programs, "Programs" ],
                [ self.child_item_images,   self.dbase_images_arr,   self.dbase_images,   self.dbase_path_images,   "Images"   ],
                [ self.child_item_tables,   self.dbase_tables_arr,   self.dbase_tables,   self.dbase_path_tables,   "Tables"   ],
                [ self.child_item_queries,  self.dbase_queries_arr,  self.dbase_queies,   self.dbase_path_queries,  "SQL"      ],
                [ self.child_item_others,   self.dbase_others_arr,   self.dbase_others,   self.dbase_path_others,   "Other"    ]
            ]
            for db in dbase_array:
                db[3] = genv.v__app__config[self.db_path][db[4]]
                db[2] = genv.v__app__config[self.db_pro ][db[4]]
                db[1] = []
                db[1].append(db[2])
                db[1] = db[1].replace("'","").split(", ")
                #
                if len(db[1]) > 0:
                    for file_name in db[1]:
                        file_name = file_name.replace("\"","")
                        if len(file_name.strip()) < 1:
                            return
                        child = QStandardItem(file_name)
                        if child:
                            db[0].appendRow(child)
        except Exception as e:
            DebugPrint(e)
            self.messageBox(""
            + "Error: .pro file have not the needed format.\n"
            + file_path + "\n"
            + "Command aborted.")
            self.hlay_edit.clear()
    
    # -----------------------------------------------
    # close the current opened project file ...
    # -----------------------------------------------
    def pro_clear_clicked(self):
        #self.list_widget.clear()

        # --------------------------------------------------
        # remove project files from list, when double click
        # with mouse on a favorite item ...
        # --------------------------------------------------
        i = clearChildTreeItems(self)
        i.remove()
        
        self.path_edit.clear()
        self.hlay_edit.clear()
        return
    
    # -----------------------------------------------
    # new project file ...
    # -----------------------------------------------
    def pro_new_clicked(self):
        self.dialog  = QDialog(self)
        dialog_font  = QFont(genv.v__app__font,10)
        dialog_font.setBold(True)
        
        dialog_vlay  = QVBoxLayout()
        dialog_label = QLabel("Please input the Project name:")
        dialog_label.setFont(dialog_font)
        
        self.dialog_edlay = QHBoxLayout()
        self.dialog_edit  = QLineEdit()
        self.dialog_edit.setStyleSheet(_("editfield_css"))
        
        dialog_push = QPushButton("...")
        dialog_push.setMinimumHeight(28)
        dialog_push.setFont(QFont(genv.v__app__font_edit,10))
        dialog_push.clicked.connect(self.dialog_push_clicked)
        #
        self.dialog_edlay.addWidget(self.dialog_edit)
        self.dialog_edlay.addWidget(dialog_push)
        #
        dialog_vlay.addLayout(self.dialog_edlay)
        
        dialog_hlay  = QHBoxLayout()
        dialog_push_ok = QPushButton("Ok.")
        dialog_push_ok.setMinimumHeight(32)
        dialog_push_ok.setFont(QFont(genv.v__app__font,11))
        dialog_push.clicked.connect(self.dialog_push_ok_clicked)
        
        dialog_push_cancel = QPushButton("Cancel")
        dialog_push_cancel.setMinimumHeight(32)
        dialog_push_cancel.setFont(QFont(genv.v__app__font,11))
        dialog_push.clicked.connect(self.dialog_push_cancel_clicked)
        
        dialog_hlay.addWidget(dialog_push_ok)
        dialog_hlay.addWidget(dialog_push_cancel)
        
        dialog_vlay.addWidget(dialog_label)
        dialog_vlay.addWidget(self.dialog_edit)
        dialog_vlay.addLayout(dialog_hlay)
        
        self.dialog.setLayout(dialog_vlay)
        self.dialog.setWindowTitle("New Project...")
        self.dialog.exec_()
        #
        return
    
    # ----------------------------------------------
    # dialog for new .pro file - cancel btn click:
    # ----------------------------------------------
    def dialog_push_cancel_clicked(self):
        self.dialog_edit.clear()
        self.dialog.close()
        return
    
    # ----------------------------------------------
    # dialog for new .pro file - ok button click ...
    # ----------------------------------------------
    def dialog_push_ok_clicked(self):
        file_path = self.dialog_edit.text().strip()
        if not file_path:
            self.messageBox(""
            + "Error: no project file given.\n"
            + "Command aborted.")
            return
        if not os.path.exists(file_path):
            self.messageBox(""
            + "Error: project file does not exists.\n"
            + "Command aborted.")
            return
        if not os.path.isfile(file_path):
            self.dialog_edit.clear()
            self.messageBox(""
            + "Error: project file is not a normal file object.\n"
            + "Command aborted.")
            return
        
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                file.close()
        except Exception as e:
            self.messageBox(""
            + "Error: file could not be open:\n"
            + file_path + "\n\n"
            + "Command aborted.")
        
        self.setup_favorites(file_path)
        return
    
    # -----------------------------------------------
    # dialog to open/create a .pro file ...
    # -----------------------------------------------
    def dialog_push_clicked(self):
        file_dialog = QFileDialog()
        file_dialog.setStyleSheet("QFileDialog * {font-size: 11pt;}")
        
        layout = self.layout()
        
        for i in range(layout.count()):
            item = layout.itemAt(i)
            widget = item.widget()
            if isinstance(widget, QPushButton):
                widget.setMinimumHeight(21)
        
        options  = file_dialog.Options()
        options |= file_dialog.DontUseNativeDialog
        file_path, file_pattern = file_dialog.getOpenFileName(self,
            "Create new Project File", "",
            "All Files (*);;Project Files (*.pro)",
            options=options)
        
        if file_path:
            if not file_path.endswith(".pro"):
                self.messageBox(""
                + "Error: Project file must have .pro as suffix in file name.\n"
                + "Command aborted.")
                return
            if not os.path.exists(file_path):
                self.messageBox(""
                + "Error: file does not exists:\n"
                + file_path + "\n"
                + "Command aborted.")
                return
            else:
                msg = QMessageBox()
                msg.setWindowTitle("Information")
                msg.setFont(self.font)
                msg.setText(""
                + "Info: the file you choose already exists.\n"
                + "Did you would like overwrite it ?")
                msg.setIcon(QMessageBox.Information)
                
                btn_nok = msg.addButton(QMessageBox.No)
                btn_yes = msg.addButton(QMessageBox.Yes)
                
                btn_nok.setFont(self.font)
                btn_yes.setFont(self.font)
                
                msg.setStyleSheet(_("msgbox_css"))
                self.result = msg.exec_()
                
            if not os.path.isfile(file_path):
                self.messageBox(""
                + "Error: you choose a file name that is not a file.\n"
                + "Maybe it is a directory ?\n"
                + "\n"
                + "Command aborted")
                return
            try:
                if self.result == QMessageBox.Yes:
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(""
                        + "[paths]\n"
                        + "Path"      + self.newline1
                        + "Forms"     + self.newline1
                        + "Programs"  + self.newline1
                        + "Reports"   + self.newline1
                        + "Tables"    + self.newline1
                        + "Images"    + self.newline1
                        + "SQL"       + self.newline1
                        + "Other"     + self.newline1
                        + "\n"
                        + "[dBaseProject]\n"
                        + "Forms"     + self.newline2
                        + "Programs"  + self.newline2
                        + "Reports"   + self.newline2
                        + "Tables"    + self.newline2
                        + "Images"    + self.newline2
                        + "SQL"       + self.newline2
                        + "Other"     + self.newline2)
                        file.close()
                
                self.dialog_edit.clear()
                self.dialog_edit.setText(file_path)
                
            except Exception as e:
                self.messageBox(""
                + "Error: file could not be open in write-mode:\n"
                + file_path + "\n"
                + "Command aborted.")
                return
        return
    
    # -----------------------------------------------
    # add project file name to favorite list ...
    # -----------------------------------------------
    def fav_add_clicked(self):
        txt = self.hlay_edit.text()
        if len(txt.strip()) > 0:
            if not self.isItemInList(txt):
                if txt.endswith(".pro"):
                    if os.path.exists(txt):
                        counter = 0
                        if not os.path.exists(genv.v__app__favorites):
                            self.messageBox(""
                            + "Info: favorite.ini file does not exists - I will fix this.")
                            try:
                                with open(genv.v__app__favorites, "w", encoding="utf-8") as configfile:
                                    configfile.write(""
                                    + "[dBaseFavorites]\n"
                                    + "1: " + txt + "\n")
                                    configfile.close()
                            except Exception as e:
                                self.messageBox(""
                                + "Error: favorite.ini file could not be open in write mode.\n"
                                + "maybe you don't have access permission's to this file.\n"
                                + "\n"
                                + "Command aborted.")
                                return
                        try:
                            genv.v__app__config.read(genv.v__app__favorites)
                            for name, path in genv.v__app__config["dBaseFavorites"].items():
                                item = QListWidgetItem(self.icon, path)
                                self.list_widget.addItem(item)
                        except Exception as e:
                            self.messageBox(""
                            + "Error: something went wrong during reading the Project paths."
                            + "Command aborted.")
                        return
                    else:
                        self.messageBox(
                        "File can not add to Favorite list.\n"
                        "Either, you have no access permission's. Or it was deleted.\n"
                        "Command aborted.")
                else:
                    self.messageBox(
                    "Project files must be end with .pro extension.\n"
                    "Command aborted.")
            else:
                self.messageBox(
                "No item is already in the Favorite list.\n"
                "Command aborted.")
        else:
            self.messageBox(
            "No text available for adding into the Favorite list.\n"
            "Command aborted.")
        return
    
    # -----------------------------------------------
    # delete selected favorite from the given list...
    # -----------------------------------------------
    def fav_del_clicked(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            self.list_widget.takeItem(self.list_widget.row(selected_item))
        else:
            self.messageBox(
            "No item is selected in the Favorite list.\n"
            "Command aborted.")
        return
    
    # -----------------------------------------------------------
    # to save code space, and minimaze maintain code, we use this
    # definition to display a message box with an ok button ...
    # -----------------------------------------------------------
    def messageBox(self, text):
        msg = QMessageBox()
        msg.setWindowTitle("Information")
        msg.setFont(self.font)
        msg.setText(text)
        msg.setIcon(QMessageBox.Information)
        
        btn_ok = msg.addButton(QMessageBox.Ok)
        btn_ok.setFont(self.font)
        
        msg.setStyleSheet(_("msgbox_css"))
        result = msg.exec_()
    
    # -----------------------------------------------
    # path changer (ellipse pushbutton)
    # -----------------------------------------------
    def path_push_clicked(self):
        old_text = self.path_edit.text()
        
        if len(self.hlay_edit.text().split()) < 1:
            self.messageBox(
            "You must open a Project before you can add Element's\n"
            "Command aborted.")
            self.path_edit.setText(old_text)
            return
                
        if self.selected_item == None:
            self.messageBox(
            "No project file section selected.\n"
            "Command aborted.")
            self.path_edit.setText(old_text)
            return
        
        new_text = QFileDialog.getExistingDirectory(self, "Select Folder:")
        if len(new_text.strip()) < 1:
            self.messageBox(
            "Something went wrong during selecting folder.\n"
            "set old value...\n"
            "Command aborted.")
            self.path_edit.setText(old_text)
            return
        
        if not os.path.isdir(new_text):
            self.path_edit.setText(new_text)
            self.messageBox(
            "Not a directory.\n"
            "aborted.")
            self.path_edit.setText(old_text)
            return
        
        if not self.hlay_edit.text().endswith(".pro"):
            self.messageBox(
            "Project files must be post fixed with .pro\n"
            "Command aborted.")
            self.path_edit.setText(old_text)
            return
        
        self.path_edit.setText(new_text)
        
        path_name = self.path_edit.text()
        hlay_name = self.hlay_edit.text()
        #
        path_mess = _("config file could not be write.")
        
        config_array = [
            [self.pro_forms,    "Form"    ],
            [self.pro_reports,  "Reüprt"  ],
            [self.pro_programs, "Program" ],
            [self.pro_tables,   "Tables"  ],
            [self.pro_queries,  "SQL"     ],
            [self.pro_images,   "Image"   ],
            [self.pro_other,    "Other"   ]
        ]
        for conf in config_array:
            try:
                genv.v__app__config.read(path_name)
                if self.selected_item.text() == _(conf[0]):
                    genv.v__app__config[self.db_pro][conf[1]] = path_name
                    try:
                        with open(hlay_name, "w", encoding="utf-8") as configfile:
                            genv.v__app__config.write(configfile)
                            configfile.close()
                    except Exception as e:
                        DebugPrint(e)
                        self.messageBox(path_mess)
                        return
                    DebugPrint("set " + conf[1] + " path")
            except Exception as e:
                DebugPrint(e)
                genv.v__app__config[self.db_pro] = {
                    conf[1]: path_name
                }
                try:
                    with open(hlay_name, "w", encoding="utf-8") as configfile:
                        genv.v__app__config.write(configfile)
                        configfile.close()
                except Exception as e:
                    DebugPrint("bbb")
                    DebugPrint(e)
                    self.messageBox(path_mess)
    
    # -----------------------------------------------
    # setup project file items list ...
    # -----------------------------------------------
    def populate_tree(self):
        root_node = self.model.invisibleRootItem()
        
        font1 = QFont(genv.v__app__font, 12)
        font1.setBold(True)
        #
        font2 = QFont(genv.v__app__font, 11)
        font2.setBold(True)
        font2.setItalic(True)
        
        icon1 = QIcon(os.path.join(genv.v__app__img__int__, "open-folder-blue.png"))
        icon2 = QIcon(os.path.join(genv.v__app__img__int__, "open-folder-yellow.png"))
        
        parent_item = QStandardItem(self.pro_files)
        parent_item.setFont(font1)
        parent_item.setIcon(icon1)
        
        self.child_item_forms    = QStandardItem(self.pro_forms)
        self.child_item_reports  = QStandardItem(self.pro_reports)
        self.child_item_programs = QStandardItem(self.pro_programs)
        self.child_item_tables   = QStandardItem(self.pro_tables)
        self.child_item_queries  = QStandardItem(self.pro_queries)
        self.child_item_images   = QStandardItem(self.pro_images)
        self.child_item_others   = QStandardItem(self.pro_others)
        
        item_array = [
            self.child_item_forms,
            self.child_item_reports,
            self.child_item_programs,
            self.child_item_tables,
            self.child_item_queries,
            self.child_item_images,
            self.child_item_others
        ]
        for item in item_array:
            item.setFont(font2)
            item.setIcon(icon2)
            parent_item.appendRow(item)
        #
        
        root_node.appendRow(parent_item)
        self.tree_view.setModel(self.model)
        
        self.expand_all_items(
            self.tree_view,
            self.model.indexFromItem(
            self.model.invisibleRootItem()))
    
    # -----------------------------------------------
    # get the item selected from the file item list.
    # -----------------------------------------------
    def on_item_clicked(self, index):
        liste = [
            self.pro_files,
            self.dbase_path_forms,
            self.dbase_path_reports,
            self.dbase_path_programs,
            self.dbase_path_tables,
            self.dbase_path_images,
            self.dbase_path_queries,
            self.dbase_path_others
        ]
        #for el in liste:
        #    if not el:
        #        return
        
        item = self.model.itemFromIndex(index)
        self.selected_item = item
        if not item == None:
            parent_item = item.parent()
            if not parent_item == None:
                if parent_item.text() == self.pro_files:
                    if item.text() == self.pro_forms:
                        self.path_edit.clear()
                        self.path_edit.setText(self.dbase_path_forms)
                        
                        try:
                            if not hasattr(self, model_forms):
                                pass
                        except NameError as e:
                            self.model_forms = TableModelForms(self.data_forms)
                            self.list_view.setModel(self.model_forms)
                        except AttributeError as e:
                            self.model_forms = TableModelForms(self.data_forms)
                            self.list_view.setModel(self.model_forms)
                        
                        self.model_forms.updateData(self.data_forms)
                        self.list_view.model().layoutChanged.emit()
                        return
                    elif item.text() == self.pro_reports:
                        self.path_edit.clear()
                        self.path_edit.setText(self.dbase_path_reports)
                        
                        try:
                            if not hasattr(self, model_reports):
                                pass
                        except NameError as e:
                            self.model_reports = TableModelReports(self.data_reports)
                            self.list_view.setModel(self.model_reports)
                        except AttributeError as e:
                            self.model_reports = TableModelReports(self.data_reports)
                            self.list_view.setModel(self.model_reports)
                        
                        self.model_reports.updateData(self.data_reports)
                        return
                    elif item.text() == self.pro_programs:
                        self.path_edit.clear()
                        self.path_edit.setText(self.dbase_path_programs)
                        
                        try:
                            if not hasattr(self, model_programs):
                                pass
                        except NameError as e:
                            self.model_programs = TableModelPrograms(self.data_programs)
                            self.list_view.setModel(self.model_programs)
                        except AttributeError as e:
                            self.model_programs = TableModelPrograms(self.data_programs)
                            self.list_view.setModel(self.model_programs)
                        
                        self.model_programs.updateData(self.data_programs)
                        return
                    elif item.text() == self.pro_tables:
                        self.path_edit.clear()
                        self.path_edit.setText(self.dbase_path_tables)
                        
                        try:
                            if not hasattr(self, model_tables):
                                pass
                        except NameError as e:
                            self.model_tables = TableModelTables(self.data_tables)
                            self.list_view.setModel(self.model_tables)
                        except AttributeError as e:
                            self.model_tables = TableModelTables(self.data_tables)
                            self.list_view.setModel(self.model_tables)
                        
                        self.model_tables.updateData(self.data_tables)
                        return
                    elif item.text() == self.pro_queries:
                        self.path_edit.clear()
                        self.path_edit.setText(self.dbase_path_queries)
                        
                        try:
                            if not hasattr(self, model_queries):
                                pass
                        except NameError as e:
                            self.model_queries = TableModelQueries(self.data_queries)
                            self.list_view.setModel(self.model_queries)
                        except AttributeError as e:
                            self.model_queries = TableModelQueries(self.data_queries)
                            self.list_view.setModel(self.model_queries)
                        
                        self.model_queries.updateData(self.data_queries)
                        return
                    elif item.text() == self.pro_images:
                        self.path_edit.clear()
                        self.path_edit.setText(self.dbase_path_images)
                        
                        try:
                            if not hasattr(self, model_images):
                                pass
                        except NameError as e:
                            self.model_images = TableModelImages(self.data_images)
                            self.list_view.setModel(self.model_images)
                        except AttributeError as e:
                            self.model_images = TableModelImages(self.data_images)
                            self.list_view.setModel(self.model_images)
                        
                        self.model_images.updateData(self.data_images)
                        return
                    elif item.text() == self.pro_others:
                        self.path_edit.clear()
                        self.path_edit.setText(self.dbase_path_others)
                        
                        try:
                            if not hasattr(self, model_others):
                                pass
                        except NameError as e:
                            self.model_others = TableModelOthers(self.data_others)
                            self.list_view.setModel(self.model_others)
                        except AttributeError as e:
                            self.model_others = TableModelOthers(self.data_others)
                            self.list_view.setModel(self.model_others)
                        
                        self.model_others.updateData(self.data_others)
                        return
                elif parent_item.text() == _(self.pro_forms):
                    self.path_edit.clear()
                    self.path_edit.setText(self.dbase_path_forms)
                    return
                elif parent_item.text() == self.pro_reports:
                    self.path_edit.clear()
                    self.path_edit.setText(self.dbase_path_reports)
                    return
                elif parent_item.text() == self.pro_programs:
                    self.path_edit.clear()
                    self.path_edit.setText(self.dbase_path_programs)
                    return
                elif parent_item.text() == self.pro_tables:
                    self.path_edit.clear()
                    self.path_edit.setText(self.dbase_path_tables)
                    return
                elif parent_item.text() == self.pro_queries:
                    self.path_edit.clear()
                    self.path_edit.setText(self.dbase_path_queries)
                    return
                elif parent_item.text() == self.pro_images:
                    self.path_edit.clear()
                    self.path_edit.setText(self.dbase_path_images)
                    return
                elif item.text() == self.pro_others:
                    self.path_edit.clear()
                    self.path_edit.setText(self.dbase_path_others)
                    return
            else:
                if item.text() == _(self.pro_files):
                    self.path_edit.clear()
                    self.path_edit.setText(self.dbase_path)
                    
                    try:
                        if not hasattr(self, model_all):
                            pass
                    except NameError as e:
                        self.model_all = TableModelAll(self.data_all)
                        self.list_view.setModel(self.model_all)
                    except AttributeError as e:
                        self.model_all = TableModelAll(self.data_all)
                        self.list_view.setModel(self.model_all)
                    
                    self.model_all.updateData(self.data_all)
                    self.list_view.model().layoutChanged.emit()
                    
                    return
    
    # -----------------------------------------------
    # expand all items in the tree view ...
    # -----------------------------------------------
    def expand_all_items(self, tree_view, index):
        tree_view.expand(index)
        model = tree_view.model()
        
        for row in range(model.rowCount(index)):
            child_index = model.index(row, 0, index)
            self.expand_all_items(tree_view, child_index)

class CustomTitleBar(QWidget):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.minimize_icon = QIcon(QPixmap(16, 16))  # Dummy icon, replace with actual icon
        self.maximize_icon = QIcon(QPixmap(16, 16))  # Dummy icon, replace with actual icon
        self.close_icon    = QIcon(QPixmap(16, 16))  # Dummy icon, replace with actual icon
        
        self.title = title
        self.initUI()
        
    def initUI(self):
        self.setFixedHeight(30)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.title_label = QLabel(self.title)
        self.title_label.setStyleSheet(_("DialogTitleBar"))
        
        self.minimize_button = QPushButton()
        self.minimize_button.setIcon(self.minimize_icon)
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("background: transparent;")
        
        self.maximize_button = QPushButton()
        self.maximize_button.setIcon(self.maximize_icon)
        self.maximize_button.setFixedSize(30, 30)
        self.maximize_button.setStyleSheet("background: transparent;")
        
        self.close_button = QPushButton()
        self.close_button.setIcon(self.close_icon)
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("background: transparent;")
        
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.minimize_button)
        layout.addWidget(self.maximize_button)
        layout.addWidget(self.close_button)
        
        self.setLayout(layout)
    
    # paint border: red
    def paintEvent(self, event):
        #super().paintEvent(event)
        painter = QPainter(self)
        painter.setBrush(Qt.NoBrush)
        #
        gradient = QLinearGradient(0, 0, self.width(), 0)
        # Create a gradient with 64 steps from yellow to red
        steps = 64
        for i in range(steps):
            t = i / (steps - 1)
            if t < 0.5:
                # Interpolate from black to yellow
                ratio = t / 0.5
                color = QColor(
                    int(255 * ratio),  # Red   component (linear interpolation)
                    int(255 * ratio),  # Green component (linear interpolation)
                    0                  # Blue  component (constant)
                )
            else:
                # Interpolate from yellow to red
                ratio = (t - 0.5) / 0.5
                color = QColor(
                    255,                     # Red   component (constant)
                    int(255 * (1 - ratio)),  # Green component (linear interpolation)
                    0                        # Blue  component (constant)
                )
            gradient.setColorAt(t, color)
        
        painter.fillRect(self.rect(), gradient)

    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent().mouse_press_pos = event.globalPos()
            self.parent().mouse_move_pos = event.globalPos() - self.parent().frameGeometry().topLeft()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.parent().move(event.globalPos() - self.parent().mouse_move_pos)
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent().toggleMaximizeRestore()

class ApplicationDesignPage():
    def __init__(self, parent, tabs_design, tabs):
        self.parent = parent
        self.main_layout = self.parent.main_layout
        self.tabs_designs_widget = tabs_design
        self.tabs = tabs
        
        self.designs_layout  = QVBoxLayout()
        self.designs_layout.setContentsMargins(2,2,2,2)
        self.designs_palette = QWidget()
        self.designs_palette.setStyleSheet(_("bggy"))
        self.designs_palette.setMinimumHeight(85)
        self.designs_palette.setMaximumHeight(85)
        #
        self.palette_layout  = QHBoxLayout()
        self.palette_layout.setContentsMargins(2,2,2,2)
        self.palette_widget_lhs  = QLabel ()
        self.palette_widget_mid  = QWidget()
        self.palette_widget_rhs  = QLabel ()
        #
        self.palette_widget_lhs.setMaximumWidth(20)
        self.palette_widget_rhs.setMaximumWidth(20)
        
        font = QFont("Times New Roman", 16)
        #font.setBold(True)
        
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        
        self.palette_widget_lhs.setFont(font)
        self.palette_widget_rhs.setFont(font)
        #
        self.palette_widget_lhs.setText(chr1)
        self.palette_widget_rhs.setText(chr2)
        #
        self.palette_widget_lhs.setStyleSheet(_("bglg"))
        self.palette_widget_mid.setStyleSheet(_("bggy"))
        self.palette_widget_rhs.setStyleSheet(_("bglg"))
        #
        #
        self.palette_widget_mid_layout = QHBoxLayout()
        self.palette_widget_mid_tabs   = QTabWidget()
        self.palette_widget_mid_tabs.setStyleSheet(_("designertab"))
        
        #######
        addDesignerTabs(self.palette_widget_mid_tabs)
        
        self.palette_widget_mid_layout.addWidget(self.palette_widget_mid_tabs)
        #
        self.palette_layout.addWidget(self.palette_widget_lhs)
        self.palette_layout.addLayout(self.palette_widget_mid_layout)
        self.palette_layout.addWidget(self.palette_widget_rhs)
        #
        self.designs_palette.setLayout(self.palette_layout)
        ####
        
        self.designs_viewer  = myGridViewer(self.parent)
        self.designs_viewer.setStyleSheet(_("bgwh"))
        
        self.designs_layout.addWidget(self.designs_palette)
        self.designs_layout.addWidget(self.designs_viewer)
        #
        
        self.tabs_designs_widget.setLayout(self.designs_layout)
        ####
        self.main_layout.addWidget(self.tabs)
        #################
        font = QFont(genv.v__app__font, 12)
        
        #self.btn1 = myMoveButton(" move me A ", self.designs_viewer.content)
        #self.btn2 = myMoveButton(" move me B ", self.designs_viewer.content)
        #self.btn3 = myMoveButton(" move me C ", self.designs_viewer.content)
        #
        #self.btn1.move(20,20)
        #self.btn2.move(40,40)
        #self.btn3.move(60,60)
        #
        #self.btn1.setFont(font)
        #self.btn2.setFont(font)
        #self.btn3.setFont(font)
        #
        #self.btn1.setStyleSheet("background-color:red;color:yellow;")
        #self.btn2.setStyleSheet("background-color:yellow;color:black;")
        #self.btn3.setStyleSheet("background-color:blue;color:white;")

class ButtonWidget(QWidget):
    def __init__(self, text, parent=None):
        super(ButtonWidget, self).__init__(parent)
        self.setContentsMargins(0,0,0,0)
        
        self.layout = QVBoxLayout()
        self.label  = QLabel(text)
        
        text = text.split(':')
        
        # --------------------------------------
        # Erstelle ein QPixmap mit transparentem
        # Hintergrund
        # --------------------------------------
        if text[0] == "label 0":
            self.label_pixmap = QPixmap("./_internal/img/newdoc2.png")
        
        elif text[0] == "label 1":
            self.label_pixmap = QPixmap("./_internal/img/open-folder.png")
        
        elif text[0] == "label 2":
            self.label_pixmap = QPixmap("./_internal/img/floppy-disk.png")
        
        elif text[0] == "label 3":
            self.label_pixmap = QPixmap("./_internal/img/play.png")
        
        self.label.setMinimumWidth (32)
        self.label.setMaximumWidth (32)
        
        self.label.setMinimumHeight(32)
        self.label.setMaximumHeight(32)
        
        self.label.setPixmap(self.label_pixmap)
        self.setObjectName(text[0] + ':' + text[1])
        
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

def add_item(parent, text):
    item = QStandardItem(text)
    parent.appendRow([item, QStandardItem(), QStandardItem()])
    return item

class IconDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.column() == 2:
            text = index.sibling(index.row(), 0).data()
            if text == "Complete":
                icon_path = os.path.join(genv.v__app__img__int__, "icon_white"  + genv.v__app__img_ext__)
            elif text == "Needs Review":
                icon_path = os.path.join(genv.v__app__img__int__, "icon_blue"   + genv.v__app__img_ext__)
            elif text == "In Progress":
                icon_path = os.path.join(genv.v__app__img__int__, "icon_yellow" + genv.v__app__img_ext__)
            elif text == "Out of Date":
                icon_path = os.path.join(genv.v__app__img__int__, "icon_red"    + genv.v__app__img_ext__)
            else:
                icon_path = os.path.join(genv.v__app__img__int__, "edit"        + genv.v__app__img_ext__)
            
            icon = QIcon(icon_path)
            icon.paint(painter, option.rect, Qt.AlignCenter)
        else:
            super().paint(painter, option, index)

# ---------------------------------------------------------------------------
# \brief Constructs a project page to create or modified projects.
#
# \param parent - ptr => the corresponding parent
# \param tabs   - ptr => the "tabs" component
# \param text   - str => for the object name, to gather information of obj.
# ---------------------------------------------------------------------------
class ApplicationProjectPage(QObject):
    def __init__(self, parent, tabs, text):
        super(ApplicationProjectPage, self).__init__(parent)
        self.parent = parent
        self.text   = text
        try:
            self.setObjectName(self.text)
            
            self.ProjectVLayout = QVBoxLayout()
            self.ProjectVLayout.setContentsMargins(0,0,0,0)
            self.ProjectVLayout.setSpacing(0)
            
            self.ProjectWidget  = applicationProjectWidget()
            self.ProjectVLayout.addWidget(self.ProjectWidget)
            tabs.setLayout(self.ProjectVLayout)
        except Exception as e:
            showException(traceback.format_exc())

# ---------------------------------------------------------------------------
# \brief Constructs a editor page for open, and write source code text's.
#
# \param parent - ptr => the corresponding parent
# \param tabs   - ptr => the "tabs" component
# \param text   - str => for the object name, to gather information of obj.
#
# \return ptr => the class object
# ---------------------------------------------------------------------------
class ApplicationEditorsPage(QObject):
    def __init__(self, parent, tabs, text):
        super(ApplicationEditorsPage, self).__init__(parent)
        self.parent = parent
        self.text   = text
        self.mode   = 0
        
        self.editor_object = None
        self.tabs_editor   = None
        
        try:
            self.setObjectName(self.text)
            
            self.tabs_editor_vlayout = QVBoxLayout(tabs)
            self.tabs_editor_vlayout.setSpacing(0)
            
            self.tabs_editor = QTabWidget()
            self.tabs_editor.setTabsClosable(True) 
            self.tabs_editor.tabCloseRequested.connect(self.close_tab) 
            self.tabs_editor.setStyleSheet(_(genv.css_tabs))
            self.tabs_editor.setContentsMargins(1,0,0,1)
            
            self.tabs_editor_menu = QListWidget()
            self.tabs_editor_menu.setContentsMargins(0,0,0,0)
            self.tabs_editor_menu.setFlow(QListWidget.LeftToRight)
            self.tabs_editor_menu.setStyleSheet("background-color:gray;")
            self.tabs_editor_menu.setMinimumHeight(64)
            self.tabs_editor_menu.setMaximumHeight(64)
            
            self.custom_widget0 = ButtonWidget("label 0:")
            self.custom_widget1 = ButtonWidget("label 1:")
            self.custom_widget2 = ButtonWidget("label 2:")
            self.custom_widget3 = ButtonWidget("label 3:")
            
            self.widget0_list_item = QListWidgetItem(self.tabs_editor_menu)
            self.widget0_list_item.setSizeHint(self.custom_widget0.sizeHint())
            
            self.widget1_list_item = QListWidgetItem(self.tabs_editor_menu)
            self.widget1_list_item.setSizeHint(self.custom_widget1.sizeHint())
            
            self.widget2_list_item = QListWidgetItem(self.tabs_editor_menu)
            self.widget2_list_item.setSizeHint(self.custom_widget2.sizeHint())
            
            self.widget3_list_item = QListWidgetItem(self.tabs_editor_menu)
            self.widget3_list_item.setSizeHint(self.custom_widget3.sizeHint())
            
            
            self.tabs_editor_menu.setItemWidget(self.widget0_list_item, self.custom_widget0)
            self.tabs_editor_menu.setItemWidget(self.widget1_list_item, self.custom_widget1)
            self.tabs_editor_menu.setItemWidget(self.widget2_list_item, self.custom_widget2)
            self.tabs_editor_menu.setItemWidget(self.widget3_list_item, self.custom_widget3)
            
            self.tabs_editor_menu.itemClicked.connect(self.on_editor_menu_item_clicked)
            
            self.tabs_editor_vlayout.addWidget(self.tabs_editor_menu)
            
            genv.editor_check = QCheckBox("Use old Syntax")
            genv.editor_check.setFont(QFont("Arial", 10))
            self.tabs_editor_vlayout.addWidget(genv.editor_check)
            
            self.tabs_translate = EditorTranslate()
            
            hlayout = QHBoxLayout()
            hlayout.addWidget(self.tabs_editor)
            hlayout.addWidget(self.tabs_translate)
            
            self.tabs_editor_vlayout.addLayout(hlayout)
            
        except Exception as e:
            showException(traceback.format_exc())
    
    def open_new_editor(self, file_path, mode=0):
        self.mode = mode
        
        file_layout_widget = QWidget()
        file_layout        = QHBoxLayout()
        file_layout.setSpacing(0)
        
        found = False
        
        if  genv.editor_counter == 0:
            genv.editor_counter = 1
            for entry in genv.editors_entries[self.text]:
                if  entry["name"].endswith(file_path):
                    entry["name"]   = ""
                    entry["object"] = None
                    break
        
        showInfo(f">> {genv.editors_entries[self.text]}")
        
        for entry in genv.editors_entries[self.text]:
            if entry["name"] == file_path:
                showInfo("already open.")
                found = True
                break
        if not found:
            #showInfo(f"---> {self.text}\n---> {file_path}")
            self.editor_object = EditorTextEdit(
                self,
                file_path,
                self.text,
                self.mode)
            
            self.editor_object.setContentsMargins(1,0,0,1)
            new_editor    = {
                "object": self.editor_object,
                "name":   file_path
            }
            
            genv.editors_entries[self.text].append(new_editor)
            
            showInfo(f"{genv.editors_entries}")
            
            file_layout_widget = QWidget()
            file_layout        = QVBoxLayout()
            file_layout.setSpacing(0)
            
            file_layout.addWidget(self.editor_object)
            file_layout_widget.setLayout(
            file_layout)
            
            file_layout_widget.setContentsMargins(1,0,0,1)
            self.tabs_editor.addTab(file_layout_widget, os.path.basename(file_path))
    
    def on_editor_menu_item_clicked(self, item):
        widget = self.tabs_editor_menu.itemWidget(item)
        if widget:
            text = widget.objectName()
            text = text.split(':')
            
            if text[0] == "label 0":
                if  self.editor_object == None:
                    self.editor_object = EditorTextEdit(
                        self,  "",
                        self.text,
                        self.mode)
                self.editor_object.check_default()
                return
                    
            elif text[0] == "label 1":
                file_path = self.open_dialog()
                filename  = os.path.basename(file_path)
                if len(filename) < 1:
                    showInfo("len < 1")
                    return
                widget.setObjectName('label 1:' + file_path)
                #
                self.open_new_editor(file_path)
                
                #try:
                #    pass
                #    #self.focused_widget = genv.editor.obj_1
                #except AttributError:
                #    self.showNoEditorMessage()
                #    return
            
            elif text[0] == "label 2":
                self.checkBeforeSave()
            elif text[0] == "label 3":
                prg = None
                try:
                    # ---------------------------------------
                    # todo: text editor focus !!
                    # ---------------------------------------
                    plain_text_edits = []
                    script_name = ""
                    
                    for index in range(self.tabs_editor.count()):
                        tab = self.tabs_editor.widget(index)
                        if tab:
                            edits = tab.findChildren(QPlainTextEdit)
                            plain_text_edits.extend(edits)
                    
                    # ---------------------------------------
                    # save source code before exec...
                    # ---------------------------------------
                    for i, edit in enumerate(plain_text_edits, start=0):
                        if genv.current_focus.objectName() == edit.objectName():
                            script_name = edit.objectName()
                            with open(script_name, 'w', encoding='utf-8') as file:
                                file.write(edit.toPlainText())
                                file.close()
                            break
                    
                    if genv.current_focus.edit_type == "dbase":
                        prg = interpreter_dBase(script_name)
                        prg.parse()
                        
                    elif genv.current_focus.edit_type == "pascal":
                        prg = interpreter_Pascal(script_name)
                        prg.parse()
                        
                    elif genv.current_focus.edit_type == "java":
                        prg = interpreter_Java(script_name)
                        prg.parse()
                        
                    elif genv.current_focus.edit_type == "isoc":
                        prg = interpreter_ISOC(script_name)
                        prg.parse()
                        
                    elif genv.current_focus.edit_type == "python":
                        prg = interpreter_Python(script_name)
                        prg.parse()
                        
                    elif genv.current_focus.edit_type == "javascript":
                        prg = interpreter_JavaScript(script_name)
                        prg.parse()
                        
                    elif genv.current_focus.edit_type == "prolog":
                        prg = interpreter_Prolog(script_name)
                        prg.parse()
                        
                    elif genv.current_focus.edit_type == "lisp":
                        prg = interpreter_LISP(script_name)
                        prg.parse()
                        
                    elif genv.current_focus.edit_type == "c64":
                        parser = C64BasicParser(script_name)
                        parsed = parser.parse()
                        translated = parser.translate(parsed)
                        
                        print("Parsed Program:", parsed)
                        print("Translated Program:", translated)
                        
                        #prg = interpreter_C64(script_name)
                        #prg.parse()
                    
                    DebugPrint("\nend of data\n")
                    
                    DebugPrint(genv.text_code)
                    prg.run()
                    
                except AttributeError as e:
                    showInfo(f"AttributeError:\n{e}\n\nMaybe no Focus to Editor.")
                    return
                except ENoSourceHeader as e:
                    showError(f"SourceReaderError:\n{e}")
                    return
                except Exception as e:
                    showError(f"Exception:\n{e}")
                    return
    
    def close_tab(self, index):
        # Schließt den Tab an der angegebenen Position
        if 0 <= index < self.tabs_editor.count():
            file_path = self.tabs_editor.tabText(index)
            try:
                for entry in genv.editors_entries["dbase"]:
                    if entry["name"].endswith(file_path):
                        entry["name"] = ""
                        entry["object"] = None
                        self.tabs_editor.removeTab(index)
                        return
            except KeyError as e:
                print("key error")
    
    def showNoEditorMessage(self):
        msg = QMessageBox()
        msg.setWindowTitle(_("Warning"))
        msg.setText(_("no editor focused - do nothing.\n"))
        msg.setIcon(QMessageBox.Warning)
        
        btn_ok = msg.addButton(QMessageBox.Ok)
        
        msg.setStyleSheet(_("msgbox_css"))
        msg.exec_()
    
    def checkBeforeSave(self):
        return
        try:
            if not self.focused_widget:
                self.showNoEditorMessage()
                return
        except AttributeError:
            self.showNoEditorMessage()
            return

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
            #self.focused_widget = QApplication.focusWidget()
            if self.focused_widget:
                if isinstance(self.focused_widget, QPlainTextEdit):
                    script_name = self.focused_widget.objectName()
                    DebugPrint(script_name)
                    if not os.path.exists(script_name):
                        msg = None
                        msg = QMessageBox()
                        msg.setWindowTitle("Warning")
                        msg.setText(_("Error: file could not be saved:") + f"\n{script_name}.")
                        msg.setIcon(QMessageBox.Warning)
                        btn_ok = msg.addButton(QMessageBox.Ok)
                        
                        msg.setStyleSheet(_("msgbox_css"))
                        result = msg.exec_()
                        DebugPrint(f"Error: file does not exists: {script_name}.")
                        return
                    file_path = script_name.replace("\\", "/")
                    #
                    with open(file_path, "w") as file:
                        file.write(self.focused_widget.toPlainText())
                        file.close()
    
    def open_dialog(self):
        file_path = ""
        icon_size = 20

        dialog   = QFileDialog (self.editor_object, _("Open file"))
        
        dialog.setWindowTitle(_("Open File"))
        dialog.setOption     (QFileDialog.DontUseNativeDialog, True)
        #dialog.setAcceptMode (QFileDialog.AcceptSave)
        dialog.setStyleSheet (_("QFileDlog"))
            
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setViewMode(QFileDialog.Detail)
        
        if self.objectName() == "dbase":
            dialog.setNameFilters([
                _("Program Files")  + " (*.prg)",
                _("Database Files") + " (*.dbf, *.db)",
                _("Query Files")    + " (*.sql)",
                _("Text Files")     + " (*.txt *.md)",
                _("All Files")      + " (*)"])
        elif self.objectName() == "pascal":
            dialog.setNameFilters([
                _("Pascal Files")  + " (*.pas *.pp)",
                _("Include Files") + " (*.inc)",
                _("Text Files")    + " (*.txt *.md)",
                _("All Files")     + " (*)"])
        elif self.objectName() == "isoc":
            dialog.setNameFilters([
                _("C++ Program Files") + " (*.c *.cc *.cpp *.c++)",
                _("C++ Header Files")  + " (*.h *.hh *.hpp *.h++)",
                _("C++ Include Files") + " (*.inc)",
                _("Text Files")        + " (*.txt *.md)",
                _("All Files")         + " (*)"])
        elif self.objectName() == "python":
            dialog.setNameFilters([
                _("Python Files") + " (*.py *.pyw)",
                _("Text Files")   + " (*.txt *.md)",
                _("All Files")    + " (*)"])
        elif self.objectName() == "lisp":
            dialog.setNameFilters([
                _("Lisp Files") + " (*.lisp *.lsp *.l *.el)",
                _("Text Files")   + " (*.txt *.md)",
                _("All Files")    + " (*)"])
        elif self.objectName() == "prolog":
            dialog.setNameFilters([
                _("Prolog Files") + " (*.pl *.pro)",
                _("Text Files")   + " (*.txt *.md)",
                _("All Files")    + " (*)"])
        elif self.objectName() == "java":
            dialog.setNameFilters([
                _("Java Files")   + " (*.java)",
                _("Text Files")   + " (*.txt *.md)",
                _("All Files")    + " (*)"])
        elif self.objectName() == "javascript":
            dialog.setNameFilters([
                _("JavaScript Files") + " (*.js)",
                _("HTML Files")       + " (*.html *.htm)",
                _("CSS Files")        + " (*.css)",
                _("XML Files")        + " (*.xml)",
                _("Text Files")       + " (*.txt *.md)",
                _("All Files")        + " (*)"])
        elif self.objectName() == "c64":
            dialog.setNameFilters([
                _("BASIC Files")  + " (*.bas)",
                _("All Files")    + " (*)"])
        else:
            dialog.setNameFilters([
                _("All Files") + " (*)"])
        
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        #if mode == 0:
        #    if dialog.exec_() == QFileDialog.Accepted:
        #        file_path = dialog.selectedFiles()[0]
        #        return self.check_file(file_path)
        
        #elif mode in [                  \
        #    genv.SIDE_BUTTON_DBASE,     \
        #    genv.SIDE_BUTTON_PASCAL,    \
        #    genv.SIDE_BUTTON_C64]:
            
        #    options  = QFileDialog.Options()
        #    options |= QFileDialog.DontConfirmOverwrite  
            
        default_file = "default"
        
        #if mode == genv.SIDE_BUTTON_DBASE:
        #    default_file += ".prg"
        #elif mode == genv.SIDE_BUTTON_PASCAL:
        #    default_file += ".pas"
        #else:
        #    default_file += ".txt"
        #
        if dialog.exec_() == QFileDialog.Accepted:
            # -----------------------------------
            # Gewählte Datei und Filter abrufen
            # -----------------------------------
            file_path = dialog.selectedFiles()[0]
            #showInfo("--->> " + file_path)
            
            if len(file_path) < 1:
                showInfo(_("no file name given"))
                return
                
            # -----------------------------------
            # Dateiendung aus dem Filter ableiten
            # -----------------------------------
            #if "(*." in selected_filter:
            #    file_extension = selected_filter.split("(*.")[-1].split(")")[0]
            #    if not file_path.endswith(f".{file_extension}"):
            #        file_path += f".{file_extension}"
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    file.close()
                return self.check_file(file_path)
                
            except PermissionError as e:
                showError(_(f"you have no permissions to write the " +
                f"file.\n{e}"))
                return ""
            except Exception as e:
                showError(_(f"unhandled exception occured."))
                return ""
                
    def check_file(self, file_path):
        if not file_path:
            msg = QMessageBox()
            msg.setWindowTitle("Information")
            msg.setText(_("no source file given.\n"))
            msg.setIcon(QMessageBox.Question)
            msg.setStyleSheet(_("msgbox_css"))
            
            btn_ok = msg.addButton(QMessageBox.Ok)
            result = msg.exec_()            
            return ""
        
        if not os.path.isfile(file_path):
            msg = None
            msg = QMessageBox()
            msg.setWindowTitle("Information")
            msg.setText(_(
                "You selected a file, that can not be open.\n"
                "no file will be open."))
            msg.setIcon(QMessageBox.Question)
            msg.setStyleSheet(_("msgbox_css"))
            
            btn_ok = msg.addButton(QMessageBox.Ok)
            result = msg.exec_()
            return ""
        return file_path
        
class ApplicationTabWidget(QTabWidget):
    def __init__(self, tabs, parent=None):
        super(ApplicationTabWidget, self).__init__(parent)
        
        self.setStyleSheet(_(genv.css_tabs))
        self.hide()
        
        self.tabs = []
        
        if len(tabs) < 1:
            return
            
        for index in tabs:
            widget = QWidget()
            self.tabs.append(widget)
            self.addTab(widget, index)
    
    def getTab(self, index:int):
        return self.tabs[index]

# ---------------------------------------------------------------------------
# \brief tree widget delegation: status codes
# ---------------------------------------------------------------------------
class ColorComboBoxDelegateTree(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Hintergrund zeichnen
        super().paint(painter, option, index)
        
        # Text abrufen
        column = index.column()
        text   = index.data()
        
        # Rechten Kreis zeichnen
        right_circle_color = QColor("red")
        if column == 5 and text == "F":
            right_circle_color = QColor("red")
        elif column == 5 and text == "S":
            right_circle_color = QColor("yellow")
            
        painter.setBrush(QBrush(right_circle_color))
        right_circle_rect = QRect(option.rect.left() + 25, option.rect.top() + 5, 10, 10)
        painter.drawEllipse(right_circle_rect)

# ---------------------------------------------------------------------------
# \brief combo box delegation for cert ssl tab ...
# ---------------------------------------------------------------------------
class ColorComboBoxDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Hintergrund zeichnen
        super().paint(painter, option, index)

        # Text abrufen
        text = index.data()
        
        # Rechten Kreis zeichnen
        right_circle_color = QColor("blue")
        if text == "256":
            right_circle_color = QColor("blue")
        if text == "512":
            right_circle_color = QColor("red")
        if text == "1024":
            right_circle_color = QColor("green")
        if text == "2048":
            right_circle_color = QColor("lime")
        if text == "4096":
            right_circle_color = QColor("yellow")
            
        painter.setBrush(QBrush(right_circle_color))
        right_circle_rect = QRect(option.rect.right() - 25, option.rect.top() + 5, 10, 10)
        painter.drawEllipse(right_circle_rect)

class GridGraphicsViewFormDesigner(QGraphicsView):
    def __init__(self, scene, window_size):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # Setze die Größe der Szene auf das Doppelte der Fenstergröße
        scene.setSceneRect(0, 0, window_size.width() * 2, window_size.height() * 2)
        self.selected_item = None  # Aktuell ausgewähltes Element
        self.resize_mode = None  # Speichert den aktiven Ziehpunkt
        self.last_resize_pos = None  # Speichert die letzte Position für die 10-Pixel-Schritte
        self.window_size = window_size  # Speichert die Fenstergröße, um die Mausbewegung zu begrenzen
    
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # Gitterabstand und Punktgröße festlegen
        grid_size  = 10  # Abstand zwischen den Punkten
        point_size =  2  # Punktgröße: 2x2 Pixel

        # Pinsel und Farbe für das Gitter definieren
        pen = QPen(QColor(200, 200, 200))  # Farbe der Punkte
        painter.setPen(pen)
        brush = QBrush(QColor(200, 200, 200))  # Füllfarbe der Punkte
        painter.setBrush(brush)

        # Start- und Endkoordinaten des sichtbaren Bereichs bestimmen
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        # Punkt-Gitter zeichnen als 2x2 Pixel Rechtecke
        for x in range(left, int(rect.right()), grid_size):
            for y in range(top, int(rect.bottom()), grid_size):
                painter.drawRect(x, y, point_size, point_size)
    
    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        
        if self.selected_item:
            pen = QPen(QColor("red"), 4, Qt.DashLine)
            painter.setPen(pen)
            item_rect = self.selected_item.sceneBoundingRect()
            painter.drawRect(item_rect)

            # Füllfarbe und Größe für die Ziehpunkte festlegen
            painter.setBrush(QBrush(QColor("red")))
            rect_size = 12

            # Berechne und zeichne die Positionen der Ziehpunkte auf jeder Seite
            for point in self.calculate_resize_handles(item_rect):
                painter.drawRect(int(point.x() - rect_size / 2), int(point.y() - rect_size / 2), rect_size, rect_size)

    def calculate_resize_handles(self, item_rect):
        """Berechnet die Positionen der Ziehpunkte an den Seiten des Rahmens."""
        left_center = QPointF(item_rect.left(), item_rect.center().y())
        right_center = QPointF(item_rect.right(), item_rect.center().y())
        top_center = QPointF(item_rect.center().x(), item_rect.top())
        bottom_center = QPointF(item_rect.center().x(), item_rect.bottom())
        return [left_center, right_center, top_center, bottom_center]

    def mousePressEvent(self, event):
        # Bestimme das ausgewählte Element und speichere es
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsItem):
            self.selected_item = item
            self.last_resize_pos = self.mapToScene(event.pos())  # Setze die Ausgangsposition
        else:
            self.selected_item   = None
            self.last_resize_pos = None
        
        # Prüfe, ob ein Ziehpunkt angeklickt wurde
        pos = self.mapToScene(event.pos())
        item_rect = self.selected_item.sceneBoundingRect() if self.selected_item else None
        handles = self.calculate_resize_handles(item_rect) if item_rect else []

        # Zuordnung der Ziehpunkte zu den Seiten mit einem Toleranzbereich von 10 Pixel
        if self.selected_item and self.is_near_point(pos, handles[0], threshold=10):
            self.resize_mode = 'left'
        elif self.selected_item and self.is_near_point(pos, handles[1], threshold=10):
            self.resize_mode = 'right'
        elif self.selected_item and self.is_near_point(pos, handles[2], threshold=10):
            self.resize_mode = 'top'
        elif self.selected_item and self.is_near_point(pos, handles[3], threshold=10):
            self.resize_mode = 'bottom'
        else:
            self.resize_mode = None  # Keine Ziehpunkte ausgewählt

        self.viewport().update()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # Begrenze die Mausbewegung auf die Fenstergröße
        if event.pos().x() < 0 or event.pos().y() < 0 or event.pos().x() > self.window_size.width() or event.pos().y() > self.window_size.height():
            return

        if self.selected_item and self.resize_mode:
            pos = self.mapToScene(event.pos())
            delta = pos - self.last_resize_pos  # Berechne die Verschiebung seit dem letzten Schritt

            # Anpassung des Rechtecks in 10-Pixel-Schritten
            if self.resize_mode == 'left' and abs(delta.x()) >= 10:
                adjustment = 10 * (-1 if delta.x() > 0 else 1)
                new_width = max(10, self.selected_item.rect().width() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x() - adjustment, 
                                           self.selected_item.rect().y(), 
                                           new_width, 
                                           self.selected_item.rect().height())
                self.last_resize_pos = pos  # Aktualisiere die Position

            elif self.resize_mode == 'right' and abs(delta.x()) >= 10:
                adjustment = 10 * (1 if delta.x() > 0 else -1)
                new_width = max(10, self.selected_item.rect().width() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x(), 
                                           self.selected_item.rect().y(), 
                                           new_width, 
                                           self.selected_item.rect().height())
                self.last_resize_pos = pos  # Aktualisiere die Position

            elif self.resize_mode == 'top' and abs(delta.y()) >= 10:
                adjustment = 10 * (-1 if delta.y() > 0 else 1)
                new_height = max(10, self.selected_item.rect().height() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x(), 
                                           self.selected_item.rect().y() - adjustment, 
                                           self.selected_item.rect().width(), 
                                           new_height)
                self.last_resize_pos = pos  # Aktualisiere die Position

            elif self.resize_mode == 'bottom' and abs(delta.y()) >= 10:
                adjustment = 10 * (1 if delta.y() > 0 else -1)
                new_height = max(10, self.selected_item.rect().height() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x(), 
                                           self.selected_item.rect().y(), 
                                           self.selected_item.rect().width(), 
                                           new_height)
                self.last_resize_pos = pos  # Aktualisiere die Position

            self.viewport().update()
        elif self.selected_item:
            # Snap-Funktion beim Bewegen des Elements
            grid_size = 10
            new_pos = self.mapToScene(event.pos())
            snapped_x = round(new_pos.x() / grid_size) * grid_size
            snapped_y = round(new_pos.y() / grid_size) * grid_size

            # Verschieben der Szene, wenn sich das Element an den Rand nähert
            buffer_zone = 20  # Abstand zum Rand, um die Szene zu verschieben
            move_offset = 10  # Verschiebung der Szene in Pixeln
            if new_pos.x() > self.window_size.width() - buffer_zone:
                self.setSceneRect(self.sceneRect().adjusted(-move_offset, 0, move_offset, 0))
            elif new_pos.x() < buffer_zone:
                self.setSceneRect(self.sceneRect().adjusted(move_offset, 0, -move_offset, 0))
            if new_pos.y() > self.window_size.height() - buffer_zone:
                self.setSceneRect(self.sceneRect().adjusted(0, -move_offset, 0, move_offset))
            elif new_pos.y() < buffer_zone:
                self.setSceneRect(self.sceneRect().adjusted(0, move_offset, 0, -move_offset))

            self.selected_item.setPos(snapped_x, snapped_y)
            self.viewport().update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Zurücksetzen des Resize-Modus nach dem Loslassen
        self.resize_mode = None
        super().mouseReleaseEvent(event)

    def is_near_point(self, pos, point, threshold=10):
        """Hilfsfunktion zur Überprüfung, ob die Position `pos` nahe an einem bestimmten Punkt `point` liegt."""
        return abs(pos.x() - point.x()) < threshold and abs(pos.y() - point.y()) < threshold

class DraggableComponentFormDesigner(QGraphicsRectItem):
    def __init__(self, name, x=0, y=0, width=50, height=50, view=None, label="", connections=[]):
        super().__init__(0, 0, width, height)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setPos(x, y)
        self.name = name
        self.label = label
        self.connections = connections  # Speichert relative Positionen der Verankerungen
        self.view = view
        self.last_snap_pos = QPointF(x, y)
        self.scroll_timer = QTimer()
        self.scroll_timer.setSingleShot(True)
        self.scroll_timer.timeout.connect(self.resume_movement)
        self.is_scrolling = False
        
    def resume_movement(self):
        self.is_scrolling = False
    
    def paint(self, painter, option, widget):
        # Hintergrundfarbe und Rahmen zeichnen
        painter.setBrush(QColor("skyblue"))
        painter.drawRect(self.rect())
        
        # Text im Zentrum des Bauteils zeichnen
        painter.setPen(QPen(Qt.black))
        painter.drawText(self.rect(), Qt.AlignCenter, self.label)


class GridGraphicsView(QGraphicsView):
    def __init__(self, scene, window_size):
        super().__init__(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        
        # Setze die Größe der Szene auf das Doppelte der Fenstergröße
        scene.setSceneRect(0, 0, window_size.width() * 2, window_size.height() * 2)
        self.selected_item = None  # Aktuell ausgewähltes Element
        self.resize_mode = None  # Speichert den aktiven Ziehpunkt
        self.last_resize_pos = None  # Speichert die letzte Position für die 10-Pixel-Schritte
    
    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        # Gitterabstand und Punktgröße festlegen
        grid_size  = 10  # Abstand zwischen den Punkten
        point_size =  2  # Punktgröße: 2x2 Pixel

        # Pinsel und Farbe für das Gitter definieren
        pen = QPen(QColor(200, 200, 200))  # Farbe der Punkte
        painter.setPen(pen)
        brush = QBrush(QColor(200, 200, 200))  # Füllfarbe der Punkte
        painter.setBrush(brush)

        # Start- und Endkoordinaten des sichtbaren Bereichs bestimmen
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)

        # Punkt-Gitter zeichnen als 2x2 Pixel Rechtecke
        for x in range(left, int(rect.right()), grid_size):
            for y in range(top, int(rect.bottom()), grid_size):
                painter.drawRect(x, y, point_size, point_size)
    
    def drawForeground(self, painter, rect):
        super().drawForeground(painter, rect)
        
        if self.selected_item:
            pen = QPen(QColor("red"), 4, Qt.DashLine)
            painter.setPen(pen)
            item_rect = self.selected_item.sceneBoundingRect()
            painter.drawRect(item_rect)

            # Füllfarbe und Größe für die Ziehpunkte festlegen
            painter.setBrush(QBrush(QColor("red")))
            rect_size = 12

            # Berechne und zeichne die Positionen der Ziehpunkte auf jeder Seite
            for point in self.calculate_resize_handles(item_rect):
                painter.drawRect(int(point.x() - rect_size / 2), int(point.y() - rect_size / 2), rect_size, rect_size)

    def calculate_resize_handles(self, item_rect):
        """Berechnet die Positionen der Ziehpunkte an den Seiten des Rahmens."""
        left_center = QPointF(item_rect.left(), item_rect.center().y())
        right_center = QPointF(item_rect.right(), item_rect.center().y())
        top_center = QPointF(item_rect.center().x(), item_rect.top())
        bottom_center = QPointF(item_rect.center().x(), item_rect.bottom())
        return [left_center, right_center, top_center, bottom_center]

    def mousePressEvent(self, event):
        # Bestimme das ausgewählte Element und speichere es
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsItem):
            self.selected_item = item
            self.last_resize_pos = self.mapToScene(event.pos())  # Setze die Ausgangsposition
        else:
            self.selected_item   = None
            self.last_resize_pos = None
        
        # Prüfe, ob ein Ziehpunkt angeklickt wurde
        pos = self.mapToScene(event.pos())
        item_rect = self.selected_item.sceneBoundingRect() if self.selected_item else None
        handles = self.calculate_resize_handles(item_rect) if item_rect else []

        # Zuordnung der Ziehpunkte zu den Seiten mit einem Toleranzbereich von 10 Pixel
        if self.selected_item and self.is_near_point(pos, handles[0], threshold=10):
            self.resize_mode = 'left'
        elif self.selected_item and self.is_near_point(pos, handles[1], threshold=10):
            self.resize_mode = 'right'
        elif self.selected_item and self.is_near_point(pos, handles[2], threshold=10):
            self.resize_mode = 'top'
        elif self.selected_item and self.is_near_point(pos, handles[3], threshold=10):
            self.resize_mode = 'bottom'
        else:
            self.resize_mode = None  # Keine Ziehpunkte ausgewählt

        self.viewport().update()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.selected_item and self.resize_mode:
            pos = self.mapToScene(event.pos())
            delta = pos - self.last_resize_pos  # Berechne die Verschiebung seit dem letzten Schritt

            # Anpassung des Rechtecks in 10-Pixel-Schritten
            if self.resize_mode == 'left' and abs(delta.x()) >= 10:
                adjustment = 10 * (-1 if delta.x() > 0 else 1)
                new_width = max(10, self.selected_item.rect().width() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x() - adjustment, 
                                           self.selected_item.rect().y(), 
                                           new_width, 
                                           self.selected_item.rect().height())
                self.last_resize_pos = pos  # Aktualisiere die Position

            elif self.resize_mode == 'right' and abs(delta.x()) >= 10:
                adjustment = 10 * (1 if delta.x() > 0 else -1)
                new_width = max(10, self.selected_item.rect().width() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x(), 
                                           self.selected_item.rect().y(), 
                                           new_width, 
                                           self.selected_item.rect().height())
                self.last_resize_pos = pos  # Aktualisiere die Position

            elif self.resize_mode == 'top' and abs(delta.y()) >= 10:
                adjustment = 10 * (-1 if delta.y() > 0 else 1)
                new_height = max(10, self.selected_item.rect().height() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x(), 
                                           self.selected_item.rect().y() - adjustment, 
                                           self.selected_item.rect().width(), 
                                           new_height)
                self.last_resize_pos = pos  # Aktualisiere die Position

            elif self.resize_mode == 'bottom' and abs(delta.y()) >= 10:
                adjustment = 10 * (1 if delta.y() > 0 else -1)
                new_height = max(10, self.selected_item.rect().height() + adjustment)
                self.selected_item.setRect(self.selected_item.rect().x(), 
                                           self.selected_item.rect().y(), 
                                           self.selected_item.rect().width(), 
                                           new_height)
                self.last_resize_pos = pos  # Aktualisiere die Position

            self.viewport().update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        # Zurücksetzen des Resize-Modus nach dem Loslassen
        self.resize_mode = None
        super().mouseReleaseEvent(event)

    def is_near_point(self, pos, point, threshold=10):
        """Hilfsfunktion zur Überprüfung, ob die Position `pos` nahe an einem bestimmten Punkt `point` liegt."""
        return abs(pos.x() - point.x()) < threshold and abs(pos.y() - point.y()) < threshold


class DraggableComponent(QGraphicsRectItem):
    def __init__(self, name, x=0, y=0, width=50, height=50, view=None, label="", connections=[]):
        super().__init__(0, 0, width, height)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setPos(x, y)
        self.name = name
        self.label = label
        self.connections = connections  # Speichert relative Positionen der Verankerungen
        self.view = view
        self.last_snap_pos = QPointF(x, y)
        self.scroll_timer = QTimer()
        self.scroll_timer.setSingleShot(True)
        self.scroll_timer.timeout.connect(self.resume_movement)
        self.is_scrolling = False
    
    def paint(self, painter, option, widget):
        # Hintergrundfarbe und Rahmen zeichnen
        painter.setBrush(QColor("skyblue"))
        painter.drawRect(self.rect())
        
        # Text im Zentrum des Bauteils zeichnen
        font = QFont("Arial", 10, QFont.Bold)
        painter.setFont(font)
        painter.setPen(Qt.black)
        text_rect = self.rect()
        painter.drawText(text_rect, Qt.AlignCenter, self.label)
        
        # Verankerungen relativ zur aktuellen Position zeichnen
        pen = QPen(Qt.black, 2)
        painter.setPen(pen)
        for connection in self.connections:
            start_offset, end_offset = connection
            start_point = self.rect().topLeft() + start_offset
            end_point = self.rect().topLeft() + end_offset
            painter.drawLine(start_point, end_point)

            # Kreis an den Endpunkten der Linie zeichnen
            painter.setBrush(Qt.black)
            painter.drawEllipse(start_point, 2, 2)  # Startpunkt Kreis
            painter.drawEllipse(end_point, 2, 2)    # Endpunkt Kreis

    def mouseMoveEvent(self, event):
        if not self.is_scrolling:
            delta = event.scenePos() - self.last_snap_pos
            snapped_x, snapped_y = self.last_snap_pos.x(), self.last_snap_pos.y()

            if abs(delta.x()) >= 10:
                snapped_x += 10 * (1 if delta.x() > 0 else -1)
            if abs(delta.y()) >= 10:
                snapped_y += 10 * (1 if delta.y() > 0 else -1)

            # Setze die neue Position und aktualisiere das Element und den View
            self.setPos(QPointF(snapped_x, snapped_y))
            self.last_snap_pos = QPointF(snapped_x, snapped_y)
            
            self.update()  # Aktualisiere nur das betroffene Element
            self.view.update()  # Aktualisiere den gesamten View, um Hintergrund und Verankerungen neu zu zeichnen
            
            self.snap_based_scroll()
            self.restrict_cursor_within_window()
        
    def snap_based_scroll(self):
        view_rect = self.view.viewport().rect()
        scene_pos = self.view.mapFromScene(self.scenePos())
        width_threshold = self.rect().width() * 0.75
        height_threshold = self.rect().height() * 0.75
        scroll_step = 10

        if scene_pos.x() + width_threshold > view_rect.width():
            self.is_scrolling = True
            self.view.horizontalScrollBar().setValue(
                self.view.horizontalScrollBar().value() + scroll_step
            )
            self.scroll_timer.start(25)
        elif scene_pos.x() < width_threshold:
            self.is_scrolling = True
            self.view.horizontalScrollBar().setValue(
                self.view.horizontalScrollBar().value() - scroll_step
            )
            self.scroll_timer.start(25)

        if scene_pos.y() + height_threshold > view_rect.height():
            self.is_scrolling = True
            self.view.verticalScrollBar().setValue(
            self.view.verticalScrollBar().value() + scroll_step
            )
            self.scroll_timer.start(25)
        elif scene_pos.y() < height_threshold:
            self.is_scrolling = True
            self.view.verticalScrollBar().setValue(
                self.view.verticalScrollBar().value() - scroll_step
            )
            self.scroll_timer.start(25)

        # Aktualisiere den gesamten View nach jedem Scrollschritt
        self.view.update()

    def resume_movement(self):
        self.is_scrolling = False

    def restrict_cursor_within_window(self):
        cursor_pos = self.view.mapFromGlobal(QCursor.pos())
        view_rect = self.view.viewport().rect()

        if cursor_pos.x() < 0:
            cursor_pos.setX(0)
        elif cursor_pos.x() > view_rect.width():
            cursor_pos.setX(view_rect.width())

        if cursor_pos.y() < 0:
            cursor_pos.setY(0)
        elif cursor_pos.y() > view_rect.height():
            cursor_pos.setY(view_rect.height())

        QCursor.setPos(self.view.mapToGlobal(cursor_pos))

class FormDesigner(QWidget):
    def __init__(self):
        super().__init__()
        
        # QGraphicsScene und GridGraphicsView erstellen
        window_size = QSize(800, 600)
        self.scene  = QGraphicsScene()
        self.view   = GridGraphicsViewFormDesigner(self.scene, window_size)
        
        # Layout für das QWidget
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        
        
        #self.setCentralWidget(self.view)
        #self.resize(window_size)
        self.init_components()

    def init_components(self):
        # Bauteile mit individuellen Beschriftungen und Verankerungen hinzufügen
        and_gate = DraggableComponentFormDesigner(
            "AND-Gate", x=100, y=100, view=self.view, label="AND",
            connections=[
                (QPointF(-10, 10), QPointF( 0, 10)),    # Linke obere Verankerung
                (QPointF(-10, 30), QPointF( 0, 30)),    # Linke untere Verankerung
                (QPointF( 50, 20), QPointF(60, 20))     # Rechte Verankerung
            ]
        )
        
        lamp = DraggableComponentFormDesigner(
            "Lamp", x=200, y=200, view=self.view, label="LED",
            connections=[
                (QPointF(-10, 20), QPointF( 0, 20)),    # Linke Verankerung
                (QPointF( 50, 20), QPointF(60, 20))     # Rechte Verankerung
            ]
        )
        
        battery = DraggableComponentFormDesigner(
            "Battery", x=300, y=300, view=self.view, label="SRC",
            connections=[
                (QPointF(-10, 20), QPointF( 0, 20)),    # Linke Verankerung
                (QPointF( 50, 20), QPointF(60, 20))     # Rechte Verankerung
            ]
        )
        
        wire1 = DraggableComponent(
            "Wire1", x=200, y=100, width=100, height=2, view=self.view,
            connections=[
                (QPointF(  0,0), QPointF(  0,0)),
                (QPointF(100,0), QPointF(100,0))
            ]
        )
        
        self.scene.addItem(and_gate)
        self.scene.addItem(lamp)
        self.scene.addItem(battery)
        self.scene.addItem(wire1)

class CircuitDesigner(QWidget):
    def __init__(self):
        super().__init__()
        
        # QGraphicsScene und GridGraphicsView erstellen
        window_size = QSize(800, 600)
        self.scene  = QGraphicsScene()
        self.view   = GridGraphicsView(self.scene, window_size)
        
        # Layout für das QWidget
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        self.setLayout(layout)
        
        
        #self.setCentralWidget(self.view)
        #self.resize(window_size)
        self.init_components()

    def init_components(self):
        # Bauteile mit individuellen Beschriftungen und Verankerungen hinzufügen
        and_gate = DraggableComponent(
            "AND-Gate", x=100, y=100, view=self.view, label="AND",
            connections=[
                (QPointF(-10, 10), QPointF(0, 10)),    # Linke obere Verankerung
                (QPointF(-10, 30), QPointF(0, 30)),    # Linke untere Verankerung
                (QPointF( 50, 20), QPointF(60, 20))     # Rechte Verankerung
            ]
        )
        
        lamp = DraggableComponent(
            "Lamp", x=200, y=200, view=self.view, label="LED",
            connections=[
                (QPointF(-10, 20), QPointF(0, 20)),    # Linke Verankerung
                (QPointF( 50, 20), QPointF(60, 20))     # Rechte Verankerung
            ]
        )
        
        battery = DraggableComponent(
            "Battery", x=300, y=300, view=self.view, label="SRC",
            connections=[
                (QPointF(-10, 20), QPointF(0, 20)),    # Linke Verankerung
                (QPointF( 50, 20), QPointF(60, 20))     # Rechte Verankerung
            ]
        )
        
        wire1 = DraggableComponent(
            "Wire1", x=200, y=100, width=100, height=2, view=self.view,
            connections=[
                (QPointF(  0,0), QPointF(  0,0)),
                (QPointF(100,0), QPointF(100,0))
            ]
        )
        
        self.scene.addItem(and_gate)
        self.scene.addItem(lamp)
        self.scene.addItem(battery)
        self.scene.addItem(wire1)

class GradientButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        
        self.setFont(QFont("Arial", 10))  # Textgröße 11 Pixel
        self.font().setBold(True)
        
        self.setMinimumSize(110, 30)
        self.setMaximumSize(110, 30)
        
        self.setStyleSheet("border:none;font-weight:bold;")
        self.clicked.connect(self.on_button_click)
        self.is_hovered = False
    
    def on_button_click(self):
        DebugPrint("jjjj")
    
    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
    
    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Farbverlauf oder Hover-Farbe
        if self.is_hovered:
            brush = QBrush(QColor("blue"))
        else:
            brush = QBrush(QColor("navy"))
        
        # Hintergrund zeichnen
        rect = QRectF(0, 0, self.width(), self.height())
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 15, 15)  # Runde Ecken
        
        # Text zeichnen
        if not self.is_hovered:
            painter.setPen(Qt.white)
        else:
            painter.setPen(Qt.yellow)
        painter.drawText(
            rect,
            Qt.AlignCenter,
            self.text()
        )

class ClickableImage(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setFont(QFont("Arial", 10))
        self.font().setBold(True)
        
        self.setMinimumSize(110, 30)
        self.setMaximumSize(110, 30)
        
        self.setStyleSheet("border:none;font-weight:bold;")
        self.setText(_("Donate"))
        
        self.clicked.connect(self.on_button_click)
        
        self.is_hovered = False  # Hover-Zustand
    
    def on_button_click(self):
        DebugPrint("jjjj")
        html_code = _("paypaldonate")
        with open("temp_form.html", "w") as file:
            file.write(html_code)
        webbrowser.open("temp_form.html")
    
    def enterEvent(self, event):
        self.is_hovered = True
        self.update()
    
    def leaveEvent(self, event):
        self.is_hovered = False
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Farbverlauf oder Hover-Farbe
        if self.is_hovered:
            brush = QBrush(QColor("blue"))
        else:
            brush = QBrush(QColor("navy"))
        
        # Hintergrund zeichnen
        rect = QRectF(0, 0, self.width(), self.height())
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, 15, 15)  # Runde Ecken
        
        # Text zeichnen
        if not self.is_hovered:
            painter.setPen(Qt.white)
        else:
            painter.setPen(Qt.yellow)
        painter.drawText(
            rect,
            Qt.AlignCenter,
            self.text()
        )

# Verschiebbares Icon
class MovableIcon(QWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("LogOut Icon")
        self.setFixedSize(100, 50)
        
        # Label als Text
        self.label = QLabel("LogOut", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(0, 0, 100, 50)
        
        # Mausbewegung initialisieren
        self.old_pos = QPoint()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            # Zurück zum Standard-Desktop wechseln
            try:
                switch_to_default_desktop()
                sys.exit()  # Beende die Anwendung
            except Exception as e:
                DebugPrint(f"Fehler beim Wechsel zurück: {e}")

class CustomMenuBar(QMenuBar):
    def __init__(self, parent=None):
        super(CustomMenuBar, self).__init__(parent)
        
        self.setStyleSheet(genv.css_menu_item_style)
        self.setMaximumHeight(28)
        self.setContentsMargins(0,0,0,0)
        self.parent = parent
        
        self.menu_list = [
            [_("&File"),
                [
                    [_("New Help")      , 1, "Ctrl+N", self.parent.menu_file_clicked_new_help   ],
                    [_("New dBase")     , 1, "Ctrl+N", self.parent.menu_file_clicked_new_dbase   ],
                    [_("New Pascal")    , 1, "Ctrl+N", self.parent.menu_file_clicked_new_pascal   ],
                    [_("New C/C++")     , 1, "Ctrl+N", self.parent.menu_file_clicked_new_cpp   ],
                    [_("New Java")      , 1, "Ctrl+N", self.parent.menu_file_clicked_new_java   ],
                    [_("New JavaScript"), 1, "Ctrl+N", self.parent.menu_file_clicked_new_javascript   ],
                    [_("New Python")    , 1, "Ctrl+N", self.parent.menu_file_clicked_new_python   ],
                    [_("New Fortran")   , 1, "Ctrl+N", self.parent.menu_file_clicked_new_fortran   ],
                    [_("New Prolog")    , 1, "Ctrl+N", self.parent.menu_file_clicked_new_prolog   ],
                    [_("New LISP")      , 1, "Ctrl+N", self.parent.menu_file_clicked_new_lisp   ],
                    #
                    [_("Open")          , 0, "Ctrl+O", self.parent.menu_file_clicked_open  ],
                    [_("Save")          , 0, "Ctrl+S", self.parent.menu_file_clicked_save  ],
                    [_("Save as...")    , 0, ""      , self.parent.menu_file_clicked_saveas],
                    [_("Exit")          , 0, "Ctrl+X", self.parent.menu_file_clicked_exit  ]
                ]
            ],
            [_("&Edit"),
                [
                    [_("Undo")     , 0, ""      , self.parent.menu_edit_clicked_undo     ],
                    [_("Redo")     , 0, ""      , self.parent.menu_edit_clicked_redo     ],
                    [_("Clear All"), 0, "Ctrl+0", self.parent.menu_edit_clicked_clearall ]
                ]
            ],
            [_("&Help"),
                [
                    [_("About..."), 0, "F1", self.parent.menu_help_clicked_about ]
                ]
            ]
        ]
        for item in self.menu_list:
            name = item[0]; menu = item[1]
            mbar = self.addMenu(name)
            mbar.setStyleSheet("background-color:navy;")
            mbar.setContentsMargins(0,0,0,0)
            for menu_item in menu:
                subs = menu_item
                self.parent.add_menu_item(subs[0], subs[1], subs[2], mbar, subs[3])
        
        self.parent.layout.addWidget(self)
        #self.menu_bar.show()
        
# ---------------------------------------------------------------------------
# \brief  This is the GUI-Entry point for our application.
# \param  nothing
# \return ptr => the class object pointer
# ---------------------------------------------------------------------------
class FileWatcherGUI(QDialog):
    def __init__(self, parent=None):
        super(FileWatcherGUI, self).__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setMouseTracking(True)
        
        global application_window
        application_window = self
        
        # Alle Qt-Warnungen stummschalten
        QLoggingCategory.setFilterRules("*.debug=false\n*.warning=false")
        
        genv.css_menu_item_style  = _("css_menu_item_style")
        genv.css_menu_label_style = _("css_menu_label_style")
        genv.css_menu_item        = _("css_menu_item")
        
        self.font = QFont(genv.v__app__font, 10)
        self.setFont(self.font)

        self.setContentsMargins(0,0,0,0)
        self.setWindowIcon(QIcon(genv.v__app__img__int__ + "/winico.png"))
        
        self.worker_hasFocus = False
        self.is_maximized    = False
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.windowtitle = 'HelpNDoc File Client - v0.0.1 - (c) 2024 Jens Kallup - paule32'
        
        self.setWindowTitle(self.windowtitle)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        
        self.my_list = MyItemRecord(0, QStandardItem(""))
        
        self.init_ui()
        
        genv.parent_array = [
            self.help_tabs,
            self.dbase_tabs,
            self.pascal_tabs,
            self.isoc_tabs,
            self.java_tabs,
            self.javascript_tabs,
            self.python_tabs,
            self.prolog_tabs,
            self.fortran_tabs,
            self.lisp_tabs,
            self.basic_tabs,
            self.pe_windows_tabs,
            self.elf_linux_tabs,
            self.console_tabs,
            self.locale_tabs,
            self.todo_tabs,
            self.setup_tabs,
            self.certssl_tabs,
            self.github_tabs,
            self.apache_tabs,
            self.mysql_tabs,
            self.squid_tabs,
            self.electro_tabs,
            self.c64_tabs,
            self.settings_tabs
        ]
        
    # --------------------
    # dialog exit ? ...
    # --------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F1:
            os.chdir("T:/a/Qt_FPC/doc/dox/chm")
            genv.help_dialog = HelpWindow(self,"http://help/index.html")
            genv.help_dialog.setAttribute(Qt.WA_DeleteOnClose, True)
        
        elif event.key() == Qt.Key_Escape:
            exitBox = myExitDialog(_("Exit Dialog"))
            exitBox.exec_()
        elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            if self.worker_hasFocus == True:
                # c64
                DebugPrint("xxx")
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
    
    def tab1_file_tree_clicked(self, index):
        self.tab1_path = self.tab1_dir_model.fileInfo(index).absoluteFilePath()
        self.tab1_file_list.setRootIndex(self.tab1_file_model.setRootPath(self.tab1_path))
        return
    
    def tab1_file_list_clicked(self, index):
        self.tab1_path_file = self.tab1_dir_model.fileInfo(index).absoluteFilePath()
        self.tab1_path_lineEdit.setText(f"{self.tab1_path_file}")
        return
    
    def on_treeview_clicked(self, index):
        row  = index.row()
        col  = index.column()
        item = self.tab2_tree_model.itemFromIndex(index)
        text = item.text()
        DebugPrint(f"Clicked row: {row}, col: {col}, text: {text}")
    
    def on_data_changed(self, top_left, bottom_right, roles):
        if Qt.EditRole in roles:
            for row in range(top_left.row(), bottom_right.row() + 1):
                for column in range(top_left.column(), bottom_right.column() + 1):
                    index = self.tab2_tree_model.index(row, column)
                    item  = self.tab2_tree_model.itemFromIndex(index)
                    text  = item.text()
                    
                    if text == "Complete":
                        icon_path = os.path.join(genv.v__app__img__int__, "icon_white"  + genv.v__app__img_ext__)
                    elif text == "Needs Review":
                        icon_path = os.path.join(genv.v__app__img__int__, "icon_blue"   + genv.v__app__img_ext__)
                    elif text == "In Progress":
                        icon_path = os.path.join(genv.v__app__img__int__, "icon_yellow" + genv.v__app__img_ext__)
                    elif text == "Out of Date":
                        icon_path = os.path.join(genv.v__app__img__int__, "icon_red"    + genv.v__app__img_ext__)
                    else:
                        icon_path = os.path.join(genv.v__app__img__int__, "edit"        + genv.v__app__img_ext__)
                    
                    item.setIcon(QIcon(icon_path))
    
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
                new_item.setIcon(QIcon(os.path.join(genv.v__app__img__int__, "open-folder" + genv.v__app__img_ext__)))
                
                try:
                    item1 = QStandardItem(str(self.topic_counter))
                    item2 = QStandardItem(" ") #; item2.setIcon(QIcon(icon))
                    item3 = QStandardItem(" ") #; item3.setIcon(QIcon(icon))
                    item4 = QStandardItem(" ") #; item4.setIcon(QIcon(icon))
                except Exception as e:
                    DebugPrint(e)
                
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
        DebugPrint("about")
        return
    
    def menu_file_clicked_new_help(self):
        DebugPrint("help")
        #
        genv.active_side_button = genv.SIDE_BUTTON_HELP
        parent = genv.parent_array[genv.SIDE_BUTTON_HELP]
        self.side_btn0.pix_label.set_null_state()
        self.side_btn0.pix_label.hide_tabs()
        self.side_btn0.pix_label.btn_clicked(self.side_btn0, parent)
        return True
    
    def menu_file_clicked_new_dbase(self):
        DebugPrint("dbase")
        #
        genv.active_side_button = genv.SIDE_BUTTON_DBASE
        parent = genv.parent_array[genv.SIDE_BUTTON_DBASE]
        self.side_btn1.pix_label.set_null_state()
        self.side_btn1.pix_label.hide_tabs()
        self.side_btn1.pix_label.btn_clicked(self.side_btn1, parent)
        return True
    
    def menu_file_clicked_new_pascal(self):
        DebugPrint("pascal")
        #
        genv.active_side_button = genv.SIDE_BUTTON_PASCAL
        parent = genv.parent_array[genv.SIDE_BUTTON_PASCAL]
        self.side_btn2.pix_label.set_null_state()
        self.side_btn2.pix_label.hide_tabs()
        self.side_btn2.pix_label.btn_clicked(self.side_btn2, parent)
        return True
    
    def menu_file_clicked_new_cpp(self):
        DebugPrint("cpp")
        #
        genv.active_side_button = genv.SIDE_BUTTON_CPP
        parent = genv.parent_array[genv.SIDE_BUTTON_CPP]
        self.side_btn3.pix_label.set_null_state()
        self.side_btn3.pix_label.hide_tabs()
        self.side_btn3.pix_label.btn_clicked(self.side_btn3, parent)
        return True
    
    def menu_file_clicked_new_java(self):
        DebugPrint("java")
        #
        genv.active_side_button = genv.SIDE_BUTTON_JAVA
        parent = genv.parent_array[genv.SIDE_BUTTON_JAVA]
        self.side_btn4.pix_label.set_null_state()
        self.side_btn4.pix_label.hide_tabs()
        self.side_btn4.pix_label.btn_clicked(self.side_btn4, parent)
        return True
    
    def menu_file_clicked_new_javascript(self):
        DebugPrint("java script")
        #
        genv.active_side_button = genv.SIDE_BUTTON_JAVASCRIPT
        parent = genv.parent_array[genv.SIDE_BUTTON_JAVASCRIPT]
        self.side_btn5.pix_label.set_null_state()
        self.side_btn5.pix_label.hide_tabs()
        self.side_btn5.pix_label.btn_clicked(self.side_btn5, parent)
        return True
    
    def menu_file_clicked_new_python(self):
        DebugPrint("python")
        #
        genv.active_side_button = genv.SIDE_BUTTON_PYTHON
        parent = genv.parent_array[genv.SIDE_BUTTON_PYTHON]
        self.side_btn6.pix_label.set_null_state()
        self.side_btn6.pix_label.hide_tabs()
        self.side_btn6.pix_label.btn_clicked(self.side_btn6, parent)
        return True
    
    def menu_file_clicked_new_prolog(self):
        #
        genv.active_side_button = genv.SIDE_BUTTON_PROLOG
        parent = genv.parent_array[genv.SIDE_BUTTON_PROLOG]
        self.side_btn7.pix_label.set_null_state()
        self.side_btn7.pix_label.hide_tabs()
        self.side_btn7.pix_label.btn_clicked(self.side_btn7, parent)
        return True
    
    def menu_file_clicked_new_fortran(self):
        DebugPrint("fortran")
        #
        genv.active_side_button = genv.SIDE_BUTTON_FORTRAN
        parent = genv.parent_array[genv.SIDE_BUTTON_FORTRAN]
        self.side_btn8.pix_label.set_null_state()
        self.side_btn8.pix_label.hide_tabs()
        self.side_btn8.pix_label.btn_clicked(self.side_btn8, parent)
        return True
    
    def menu_file_clicked_new_lisp(self):
        DebugPrint("lisp")
        #
        genv.active_side_button = genv.SIDE_BUTTON_LISP
        parent = genv.parent_array[genv.SIDE_BUTTON_LISP]
        self.side_btn9.pix_label.set_null_state()
        self.side_btn9.pix_label.hide_tabs()
        self.side_btn9.pix_label.btn_clicked(self.side_btn9, parent)
        return True
    
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
    def add_menu_item(self, name, state, shortcut, menu, callback):
        self.menu_action = QWidgetAction(menu)
        
        self.menu_widget = QWidget()
        self.menu_layout = QHBoxLayout(self.menu_widget)
        self.menu_layout.setContentsMargins(0,0,0,0)
        self.menu_widget.setContentsMargins(0,0,0,0)
        #
        self.menu_icon = QWidget()
        self.menu_icon.setFixedWidth(26)
        self.menu_icon.setContentsMargins(0,0,0,0)
        #
        pro_name = name
        if state == 1:
            pro_name += "\t" + _("Project")
        
        self.menu_label = QLabel(pro_name)
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
    
    def open_context_topics_menu(self, position: QPoint):
        index = self.tab2_tree_view.indexAt(position)
        if index.isValid():
            item_text = self.tab2_tree_model.itemFromIndex(index).text()
            DebugPrint(f"Item text: {item_text}")
            # Context menu for tree items
            menu = QMenu()
            menu.setStyleSheet(_("css_menu_button"))
            
            action1 = QAction(_("Add Topic"), self)
            action2 = QAction(_("Add Sub Topic"), self)
            action3 = QAction(_("Rename Topic"), self)
            #
            action4 = QAction(_("Move Up"), self)
            action5 = QAction(_("Move Down"), self)
            action6 = QAction(_("Move Left"), self)
            action7 = QAction(_("Move Right"), self)
            #
            action8 = QAction(_("Delete"), self)
            
            menu.addAction(action1)
            menu.addAction(action2)
            menu.addSeparator()
            menu.addAction(action3)
            menu.addSeparator()
            menu.addAction(action4)
            menu.addAction(action5)
            menu.addAction(action6)
            menu.addAction(action7)
            menu.addSeparator()
            menu.addAction(action8)
            
            menu.exec_(self.tab2_tree_view.viewport().mapToGlobal(position))
            
    def add_item_with_icon(self, parent, text, icon_path):
        item = QStandardItem(text)
        item.setIcon(QIcon(icon_path))
        parent.appendRow(item)
        return item
    
    def trigger_mouse_press(self, obj):
        # Erzeuge das QMouseEvent für einen linken Mausklick
        mouse_event = QMouseEvent(
            QMouseEvent.MouseButtonPress,
            QPoint(2,2),
            Qt.LeftButton,
            Qt.LeftButton,
            Qt.NoModifier)
        
        # Sende das Ereignis an den Button
        QApplication.postEvent(obj, mouse_event)
    
    def handle_right_bar_cpuview(self):
        # ScrollArea erstellen
        ####
        setattr(genv, "cpuview_scroll", QScrollArea())
        setattr(genv, "cpuview_widget", QWidget())
        setattr(genv, "cpuview_layout", QVBoxLayout())
        
        # Layout und Widget konfigurieren
        genv.cpuview_scroll.setMinimumWidth(230)
        genv.cpuview_scroll.setMaximumWidth(230)
        genv.cpuview_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        genv.cpuview_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        genv.cpuview_scroll.setWidgetResizable(True)
        
        genv.cpuview_widget.setMinimumWidth(230)
        genv.cpuview_widget.setMaximumWidth(230)
        genv.cpuview_widget.setContentsMargins(1, 0, 0, 1)
        
        genv.cpuview_layout.setContentsMargins(1, 0, 0, 1)
        
        # CPUView-Widget hinzufügen
        self.cpuview = CPUView()
        genv.cpuview_layout.addWidget(self.cpuview)
        
        # Layout dem Widget zuweisen
        genv.cpuview_widget.setLayout(genv.cpuview_layout)
        genv.cpuview_scroll.setWidget(genv.cpuview_widget)  # Set widget instead of layout
        
        # Hauptlayout konfigurieren
        dl2 = QVBoxLayout()
        dl2.setContentsMargins(1, 0, 0, 1)
        dl2.addWidget(genv.cpuview_scroll)
        
        # Zum Hauptlayout hinzufügen
        self.main_layout.addLayout(dl2)
        
        # ScrollArea ausblenden
        genv.cpuview_scroll.hide()
        
    def handle_right_bar_servers(self):
        # servers
        font = QFont(genv.v__app__font,14)
        font.setBold(True)
        
        ####
        #
        genv.servers_scroll.setMinimumWidth(100)
        genv.servers_widget.setMinimumWidth(100)
        #
        
        self.servers_label_servers = QPushButton(" Servers: ")
        self.servers_label_servers.setMinimumWidth(180)
        self.servers_label_servers.setMaximumWidth(180)
        self.servers_label_servers.setFont(font)
        genv.servers_layout.addWidget(self.servers_label_servers)
        #
        self.servers_list_servers = QListWidget()
        self.servers_list_servers.setIconSize(QSize(40,40))
        self.servers_list_servers.setFont(font)
        genv.servers_layout.addWidget(self.servers_list_servers)
        
        self.servers_add_button = QPushButton("Add")
        self.servers_del_button = QPushButton("Del")
        self.servers_con_button = QPushButton("Connect")
        #
        self.servers_add_button.setMinimumHeight(26)
        self.servers_del_button.setMinimumHeight(26)
        self.servers_con_button.setMinimumHeight(26)
        
        genv.servers_layout.addWidget(self.servers_add_button)
        genv.servers_layout.addWidget(self.servers_del_button)
        genv.servers_layout.addWidget(self.servers_con_button)
        
        genv.servers_widget.setLayout(genv.servers_layout)
        
        genv.servers_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        genv.servers_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        genv.servers_scroll.setWidgetResizable(True)
        genv.servers_scroll.setLayout(genv.servers_layout)
        
        #self.dl2 = QVBoxLayout()
        #self.dl2.setContentsMargins(1,0,0,1)
        #self.dl2.addWidget(genv.servers_scroll)
        ##
        #self.main_layout.addLayout(self.dl2)
        #genv.servers_scroll.hide()
        
    def handle_right_bar_devices(self):
        # devices
        font = QFont(genv.v__app__font,14)
        font.setBold(True)
        
        ####
        setattr(genv, "devices_scroll", QScrollArea())
        setattr(genv, "devices_widget", QWidget())
        setattr(genv, "devices_layout", QVBoxLayout())
        
        #
        genv.devices_scroll.setMinimumWidth(240)
        genv.devices_scroll.setMaximumWidth(240)
        #
        genv.devices_widget.setMinimumWidth(240)
        genv.devices_widget.setMaximumWidth(240)
        #
        genv.devices_widget.setContentsMargins(1,0,0,1)
        genv.devices_layout.setContentsMargins(1,0,0,1)
        
        self.devices_label_printers = QPushButton("  Printers:  ")
        self.devices_label_printers.setMinimumWidth(240)
        self.devices_label_printers.setMaximumWidth(240)
        self.devices_label_printers.setFont(font)
        genv.devices_layout.addWidget(self.devices_label_printers)
        #
        self.devices_list_printers = QListWidget()
        self.devices_list_printers.setIconSize(QSize(40,40))
        self.devices_list_printers.setFont(font)
        genv.devices_layout.addWidget(self.devices_list_printers)
        
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
        genv.devices_layout.addWidget(self.devices_tabs_storages)
        #
        self.devices_list_storages = QListWidget()
        self.devices_list_storages.move(0,264)
        self.devices_list_storages.setIconSize(QSize(40,40))
        self.devices_list_storages.setFont(font)
        genv.devices_layout.addWidget(self.devices_list_storages)
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
        genv.devices_layout.addWidget(self.devices_tabs_label3)
        #
        self.devices_list_widget3 = QListWidget()
        self.devices_list_widget3.setMaximumHeight(100)
        self.devices_list_widget3.setIconSize(QSize(40,40))
        self.devices_list_widget3.setFont(font)
        genv.devices_layout.addWidget(self.devices_list_widget3)
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
        
        genv.devices_widget.setLayout(genv.devices_layout)
        
        genv.devices_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        genv.devices_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        genv.devices_scroll.setWidgetResizable(True)
        genv.devices_scroll.setLayout(genv.devices_layout)
        
        self.dl = QVBoxLayout()
        self.dl.setContentsMargins(1,0,0,1)
        self.dl.addWidget(genv.devices_scroll)
        ##
        self.main_layout.addLayout(self.dl)
        genv.devices_scroll.hide()
            
    def init_ui(self):
        # Layout
        #self.setMaximumWidth(900)
        self.setMinimumWidth(900)
        
        #self.setContentsMargins(0,0,0,0)
        #self.setStyleSheet("padding:0px;margin:0px;") # wöö
        
        genv.active_side_button = genv.SIDE_BUTTON_HELP
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        
        # title bar
        self.title_bar = CustomTitleBar(self.windowtitle, self)
        self.title_bar.minimize_button.clicked.connect(self.showMinimized)
        self.title_bar.maximize_button.clicked.connect(self.showMaximized)
        self.title_bar.close_button.clicked.connect(self.close)
        
        # menu bar
        self.menu_bar = CustomMenuBar(self)
        
        # tool bar
        self.tool_bar = QToolBar()
        #self.tool_bar.hide()
        self.tool_bar.setMinimumHeight(26)
        self.tool_bar.setStyleSheet(_(genv.toolbar_css))
        self.tool_bar.setMaximumHeight(32)
        self.tool_bar.setContentsMargins(0,0,0,0)
        
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
        #self.tool_bar.show()
        
        # status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready", 0)
        self.status_bar.setStyleSheet("background-color:gray;")
        self.status_bar.setMaximumHeight(28)
        
        
        # side toolbar
        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(0)
        
        self.main_widget = QWidget()
        self.main_widget.setStyleSheet("padding:0px;margin:0px;")
        
        self.main_content_layout = QHBoxLayout()
        self.main_content_layout.setSpacing(0)
        
        self.side_scroll = QScrollArea()
        self.side_widget = QWidget()
        self.side_layout = QVBoxLayout()
        self.side_layout.setSpacing(0)
        #
        self.side_widget.setContentsMargins(0,0,0,0)
        self.side_scroll.setContentsMargins(0,0,0,0)
        
        self.side_btn0  = myIconButton(self,  0, _("Help")      , _("Help Authoring for/with:\no doxygen\no HelpNDoc"))
        self.side_btn1  = myIconButton(self,  1, _("dBASE")     , _("dBASE data base programming\nlike in the old days...\nbut with SQLite -- dBase keep alive !"))
        self.side_btn2  = myIconButton(self,  2, _("Pascal")    , _("Pascal old school programming\no Delphi\no FPC"))
        self.side_btn3  = myIconButton(self,  3, _("ISO C")     , _("C / C++ embeded programming\nor cross platform"))
        self.side_btn4  = myIconButton(self,  4, _("Java")      , _("Java modern cross programming\nfor any device"))
        self.side_btn5  = myIconButton(self,  5, _("JavaScript"), _("JavaScript programming"))
        self.side_btn6  = myIconButton(self,  6, _("Python")    , _("Python modern GUI programming\nlets rock AI\nand TensorFlow"))
        self.side_btn7  = myIconButton(self,  7, _("Prolog")    , _("Prolog - logical programming."))
        self.side_btn8  = myIconButton(self,  8, _("Fortran")   , _("Fortran old school"))
        self.side_btn9  = myIconButton(self,  9, _("LISP")      , _("LISP traditional programming\nultimate old school"))
        self.side_btn10 = myIconButton(self, 10, _("BASIC")     , _("Beginner programmer"))
        #
        self.side_btn11 = myIconButton(self, 11, _("PE-Win32")  , _("Microsoft Windows PE"))
        self.side_btn12 = myIconButton(self, 12, _("ELF-Linux") , _("ELF-Linux"))
        self.side_btn13 = myIconButton(self, 13, _("Console")   , _("Your classical style of commands"))
        #
        self.side_btn14 = myIconButton(self, 14, _("Locales"), _(""
            + "Localization your Application with different supported languages\n"
            + "around the World.\n"
            + "Used by tools like msgfmt - the Unix Tool for generationg .mo files.\n"))
        #
        self.side_btn15 = myIconButton(self, 15, "Todo / Tasks", "Your todo's")
        self.side_btn16 = myIconButton(self, 16, "Setup", "Setup your Project")
        self.side_btn17 = myIconButton(self, 17, "SSL Certs", "Setup SSL")
        self.side_btn18 = myIconButton(self, 18, "GitHub.com", "Publish Project")
        self.side_btn19 = myIconButton(self, 19, "Web Server", "Configure Web Server")
        self.side_btn20 = myIconButton(self, 20, "MySQL", "Configure MySQL")
        self.side_btn21 = myIconButton(self, 21, "Squid", "Configure Squid")
        self.side_btn22 = myIconButton(self, 22, "Electro", "electronic simulations")
        self.side_btn23 = myIconButton(self, 23, "C-64", "The most popular Commodore C-64\from int the 1980er")
        self.side_btn24 = myIconButton(self, 24, _("Settings")   , _("Settings for this Application\n\n"))
        
        self.side_btn0.bordercolor = "lime"
        self.side_btn0.state       = 2
        self.side_btn0.set_style()
        
        self.side_widget.setMaximumWidth(120)
        self.side_widget.setLayout(self.side_layout)
        
        self.side_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.side_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.side_scroll.setWidgetResizable(True)
        self.side_scroll.setMinimumWidth(130)
        self.side_scroll.setMaximumWidth(130)
        self.side_scroll.setStyleSheet(_("ScrollBarCSS"))
        self.side_scroll.setWidget(self.side_widget)
        
        #self.main_content_layout.addWidget(self.side_scroll)
        #self.main_content_layout.addStretch()
        
        ####
        self.front_scroll_area = QScrollArea(self)
        self.front_scroll_area.setWidgetResizable(True)
        
        self.front_content_widget = QWidget()
        self.front_content_layout = QHBoxLayout(self.front_content_widget)
        self.front_content_layout.setSpacing(0)

        genv.splitter = QSplitter(Qt.Horizontal)
        genv.splitter.addWidget(self.side_scroll)
        genv.splitter.addWidget(self.front_scroll_area)
        #
        self.main_content_layout.setSpacing(0)
        self.main_content_layout.addWidget(genv.splitter)
        
        self.handleDBase()
        self.handlePascal()
        self.handleIsoC()
        self.handleJava()
        self.handleJavaScript()
        self.handlePython()
        self.handleProlog()
        self.handleFortran()
        self.handleLISP()
        self.handleBasic()
        self.handlePEWindows()
        self.handleELFLinux()
        self.handleConsole()
        self.handleLocales()
        self.handleTodo()
        self.handleSetup()
        self.handleCertSSL()
        self.handleGitHub()
        self.handleApache()
        self.handleMySQL()
        self.handleSquid()
        self.handleElectro()
        self.handleCommodoreC64()
        self.handleSettings()
        
        # front view
        self.help_tabs = QTabWidget()
        self.help_tabs.setStyleSheet(_(genv.css_tabs))
        self.help_tabs.setMinimumWidth(800)
        
        # help
        self.help_layout = QHBoxLayout()
        
        self.tab0_0 = QWidget()
        self.tab1_0 = QWidget()
        self.tab2   = QWidget()
        self.tab3   = QWidget()
        self.tab4   = QWidget()
        self.tab5   = QWidget()
        
        # add tabs
        self.help_tabs.addTab(self.tab0_0, _("Help Project"))
        self.help_tabs.addTab(self.tab1_0, _("Pre-/Post Actions"))
        self.help_tabs.addTab(self.tab3,   _("DoxyGen"))
        self.help_tabs.addTab(self.tab5,   _("HelpNDoc"))
        self.help_tabs.addTab(self.tab4,   _("Content"))
        
        self.help_tabs.addTab(genv.servers_scroll, _("Servers"))
        
        self.tab_widget_tabs = QTabWidget(self.tab4)
        #self.tab_widget_tabs.setMinimumWidth(830)
        #self.tab_widget_tabs.setMinimumHeight(650)
        
        self.help_tabs.removeTab(4)
        self.help_tabs.removeTab(3)
        self.help_tabs.removeTab(2)
        self.help_tabs.removeTab(1)
        
        self.tab_html   = QWidget()
        
        self.tab_widget_tabs.addTab(self.tab2, _("Topics"))
        self.tab_widget_tabs.addTab(self.tab_html, "HTML"  )
        
        
        self.help_tabs.addTab(self.tab0_0, _("Help Project"))
        self.front_content_layout.addWidget(self.help_tabs)
        self.front_content_layout.setSpacing(0)
        self.front_content_layout.addStretch()
        
        # create project tab
        self.tab2_top_layout = QHBoxLayout(self.tab2)
        self.tab3_top_layout = QHBoxLayout(self.tab3)
        self.tab4_top_layout = QHBoxLayout(self.tab_widget_tabs)
        self.tab5_top_layout = QHBoxLayout(self.tab_html)
        
        self.tab2_top_layout.setSpacing(0)
        self.tab3_top_layout.setSpacing(0)
        self.tab4_top_layout.setSpacing(0)
        self.tab5_top_layout.setSpacing(0)
        
        self.handle_right_bar_devices()
        self.handle_right_bar_servers()
        self.handle_right_bar_cpuview()
        
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
        list_layout_a.setSpacing(0)
        
        list_layout_1 = QHBoxLayout()
        list_layout_1.setSpacing(0)
        
        genv.list_widget_1 = QListWidget()
        
        list_layout_a.addLayout(list_layout_1)
        
        genv.list_widget_1.setFocusPolicy(Qt.NoFocus)
        genv.list_widget_1.setStyleSheet(_(genv.css__widget_item))
        genv.list_widget_1.setMinimumHeight(300)
        genv.list_widget_1.setMaximumWidth(200)
        
        #
        #
        for element in genv.list_widget_1_elements:
            list_item = customQListWidgetItem(element, genv.list_widget_1)
        
        genv.list_widget_1.setCurrentRow(0)
        genv.list_widget_1.itemClicked.connect(self.handle_item_click_1)
        list_layout_1.addWidget(genv.list_widget_1)
        
        genv.scrollview_1 = customScrollView_1(self, 1, 0, _("Project"))
        genv.scrollview_2 = customScrollView_2(self, 2, 0, _("Mode"));     genv.scrollview_2.hide()
        genv.scrollview_3 = customScrollView_3(self, 3, 0, _("Output"));   genv.scrollview_3.hide()
        genv.scrollview_4 = customScrollView_4(self, 4, 0, _("Diagrams")); genv.scrollview_4.hide()
        
        list_layout_1.addWidget(genv.scrollview_1)
        list_layout_1.addWidget(genv.scrollview_2)
        list_layout_1.addWidget(genv.scrollview_3)
        list_layout_1.addWidget(genv.scrollview_4)
        
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
        genv.list_widget_2 = QListWidget()
        
        list_layout_b.addLayout(list_layout_2)
        
        genv.list_widget_2.setFocusPolicy(Qt.NoFocus)
        genv.list_widget_2.setStyleSheet(_(genv.css__widget_item))
        genv.list_widget_2.setMinimumHeight(300)
        genv.list_widget_2.setMaximumWidth(200)
        
        #
        #
        for element in genv.list_widget_2_elements:
            list_item = customQListWidgetItem(element, genv.list_widget_2)
        
        genv.list_widget_2.setCurrentRow(0)
        genv.list_widget_2.itemClicked.connect(self.handle_item_click_2)
        list_layout_2.addWidget(genv.list_widget_2)

        tab1_classes = []
        
        view_instance = None
        view_object   = None

        genv.scrollview_5  = customScrollViewDoxygen( 5, genv.tab_level[ 0], genv.list_widget_2_elements[ 0])
        genv.scrollview_6  = customScrollViewDoxygen( 6, genv.tab_level[ 1], genv.list_widget_2_elements[ 1])
        genv.scrollview_7  = customScrollViewDoxygen( 7, genv.tab_level[ 2], genv.list_widget_2_elements[ 2])
        genv.scrollview_8  = customScrollViewDoxygen( 8, genv.tab_level[ 3], genv.list_widget_2_elements[ 3])
        genv.scrollview_9  = customScrollViewDoxygen( 9, genv.tab_level[ 4], genv.list_widget_2_elements[ 4])
        genv.scrollview_10 = customScrollViewDoxygen(10, genv.tab_level[ 5], genv.list_widget_2_elements[ 5])
        genv.scrollview_11 = customScrollViewDoxygen(11, genv.tab_level[ 6], genv.list_widget_2_elements[ 6])
        genv.scrollview_12 = customScrollViewDoxygen(12, genv.tab_level[ 7], genv.list_widget_2_elements[ 7])
        genv.scrollview_13 = customScrollViewDoxygen(13, genv.tab_level[ 8], genv.list_widget_2_elements[ 8])
        genv.scrollview_14 = customScrollViewDoxygen(14, genv.tab_level[ 9], genv.list_widget_2_elements[ 9])
        genv.scrollview_15 = customScrollViewDoxygen(15, genv.tab_level[10], genv.list_widget_2_elements[10])
        genv.scrollview_16 = customScrollViewDoxygen(16, genv.tab_level[11], genv.list_widget_2_elements[11])
        genv.scrollview_17 = customScrollViewDoxygen(17, genv.tab_level[12], genv.list_widget_2_elements[12])
        genv.scrollview_18 = customScrollViewDoxygen(18, genv.tab_level[13], genv.list_widget_2_elements[13])
        genv.scrollview_19 = customScrollViewDoxygen(19, genv.tab_level[14], genv.list_widget_2_elements[14])
        genv.scrollview_20 = customScrollViewDoxygen(20, genv.tab_level[15], genv.list_widget_2_elements[15])
        genv.scrollview_21 = customScrollViewDoxygen(21, genv.tab_level[16], genv.list_widget_2_elements[16])
        genv.scrollview_22 = customScrollViewDoxygen(22, genv.tab_level[17], genv.list_widget_2_elements[17])
        
        genv.scrollers[ 0] = genv.scrollview_5
        genv.scrollers[ 1] = genv.scrollview_6
        genv.scrollers[ 2] = genv.scrollview_7
        genv.scrollers[ 3] = genv.scrollview_8
        genv.scrollers[ 4] = genv.scrollview_9
        genv.scrollers[ 5] = genv.scrollview_10
        genv.scrollers[ 6] = genv.scrollview_11
        genv.scrollers[ 7] = genv.scrollview_12
        genv.scrollers[ 8] = genv.scrollview_13
        genv.scrollers[ 9] = genv.scrollview_14
        genv.scrollers[10] = genv.scrollview_15
        genv.scrollers[11] = genv.scrollview_16
        genv.scrollers[12] = genv.scrollview_17
        genv.scrollers[13] = genv.scrollview_18
        genv.scrollers[14] = genv.scrollview_19
        genv.scrollers[15] = genv.scrollview_20
        genv.scrollers[16] = genv.scrollview_21
        genv.scrollers[17] = genv.scrollview_22
        
        genv.sv_help = customScrollView_help()
        genv.sv_help.setStyleSheet(_("ScrollBarCSS"))
        
        vl = QVBoxLayout()
        vl.setSpacing(0)
        
        for item in genv.scrollers:
            list_layout_2.addWidget(item)
            item.hide()

        vl.addLayout(list_layout_2)
        vl.addWidget(genv.sv_help)
        
        list_layout_b.addLayout(vl)
        genv.scrollview_5.show()    
        
        
        ########################
        self.tab3_top_layout.addWidget(self.tab_widget_1)
        
        self.tab2_file_path = os.path.join(genv.v__app__internal__, "topics.txt")
        if not os.path.exists(self.tab2_file_path):
            showError("Error: file does not exists:\n" + self.tab2_file_path)
            sys.exit(1)
        DebugPrint("---> " + self.tab2_file_path)
        
        self.tab2_tree_view = QTreeView()
        self.tab2_tree_view.setStyleSheet(_(genv.css_model_header) + _("ScrollBarCSS"))
        self.tab2_tree_view.clicked.connect(self.on_treeview_clicked)
        
        self.tab2_tree_model = QStandardItemModel()
        self.tab2_tree_model.setHorizontalHeaderLabels([_("Topic name"), "ID", "Status", "Help icon", "In Build"])
        self.tab2_tree_model.dataChanged.connect(self.on_data_changed)
        self.tab2_tree_view.setModel(self.tab2_tree_model)
        
        
        root_node = self.tab2_tree_model.invisibleRootItem()
        self.fold_icon = genv.v__app__internal__ + "/img/floppy-disk.png"
        
        self.tab2_tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tab2_tree_view.customContextMenuRequested.connect(self.open_context_topics_menu)
        
        self.tab2_pushbuttonAdd = QPushButton(_("Add"))
        self.tab2_pushbuttonAdd.setMinimumHeight(32)
        self.tab2_pushbuttonAdd.setStyleSheet(_(genv.css_button_style))
        
        self.tab2_pushbuttonAddSub = QPushButton(_("Add Sub Topic"))
        self.tab2_pushbuttonAddSub.setMinimumHeight(32)
        self.tab2_pushbuttonAddSub.setStyleSheet(_(genv.css_button_style))
        
        self.topics_layout = QVBoxLayout()
        
        self.tab2_pushbuttonRename    = QPushButton(_("Rename Topic"))
        self.tab2_pushbuttonRename.setMinimumHeight(32)
        self.tab2_pushbuttonRename.setStyleSheet(_(genv.css_button_style))
        
        self.tab2_pushbuttonMoveUp    = QPushButton(_("Move Up"))
        self.tab2_pushbuttonMoveUp.setMinimumHeight(32)
        self.tab2_pushbuttonMoveUp.setStyleSheet(_(genv.css_button_style))
        
        self.tab2_pushbuttonMoveDown  = QPushButton(_("Move Down"))
        self.tab2_pushbuttonMoveDown.setMinimumHeight(32)
        self.tab2_pushbuttonMoveDown.setStyleSheet(_(genv.css_button_style))
        
        self.tab2_pushbuttonMoveLeft  = QPushButton(_("Move Left"))
        self.tab2_pushbuttonMoveLeft.setMinimumHeight(32)
        self.tab2_pushbuttonMoveLeft.setStyleSheet(_(genv.css_button_style))
        
        self.tab2_pushbuttonMoveRight = QPushButton(_("Move Right"))
        self.tab2_pushbuttonMoveRight.setMinimumHeight(32)
        self.tab2_pushbuttonMoveRight.setStyleSheet(_(genv.css_button_style))
        
        self.tab2_pushbuttonRemove    = QPushButton(_("Delete"))
        self.tab2_pushbuttonRemove.setMinimumHeight(32)
        self.tab2_pushbuttonRemove.setStyleSheet(_(genv.css_button_style))
        
        top_array = [
            self.tab2_pushbuttonAdd,
            self.tab2_pushbuttonAddSub,
            self.tab2_pushbuttonRename,
            self.tab2_pushbuttonMoveUp,
            self.tab2_pushbuttonMoveDown,
            self.tab2_pushbuttonMoveLeft,
            self.tab2_pushbuttonMoveRight,
            self.tab2_pushbuttonRemove
        ]
        for topa in top_array:
            self.topics_layout.addWidget(topa)
        self.topics_layout.addStretch()
        
        self.tab2_top_layout.addWidget(self.tab2_tree_view)
        self.tab2_top_layout.addLayout(self.topics_layout)
        
        self.populate_tree_view(self.tab2_file_path,os.path.join(genv.v__app__img__int__, "edit" + genv.v__app__img_ext__))
        
        
        self.delegateID     = SpinEditDelegateID     (self.tab2_tree_view)
        self.delegateStatus = ComboBoxDelegateStatus (self.tab2_tree_view)
        self.delegateIcon   = ComboBoxDelegateIcon   (self.tab2_tree_view)
        self.delegateBuild  = ComboBoxDelegateBuild  (self.tab2_tree_view)
        
        self.tab2_tree_view.setItemDelegateForColumn(1, self.delegateID)
        self.tab2_tree_view.setItemDelegateForColumn(2, self.delegateStatus)
        self.tab2_tree_view.setItemDelegateForColumn(3, self.delegateIcon)
        self.tab2_tree_view.setItemDelegateForColumn(4, self.delegateBuild)
        
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
        self.tab0_topA_vlayout.setAlignment(Qt.AlignLeft)
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
        self.tab0_fold_text1 = QLabel(_("Project:"))
        self.tab0_fold_text1.setMaximumWidth(84)
        self.tab0_fold_text1.setFont(font)
        
        self.tab0_fold_edit1 = myLineEdit()
        self.tab0_fold_edit1.setMinimumWidth(274)
        self.tab0_fold_edit1.returnPressed.connect(self.tab0_fold_edit1_return)
        
        self.tab0_fold_push1 = OpenProjectButton(self, font)
        self.tab0_fold_userd = QDir.homePath()
        self.tab0_fold_userd = self.tab0_fold_userd.replace("\\",'/')
        
        if ' ' in self.tab0_fold_userd:
            self.tab0_fold_userd = '"' + self.tab0_fold_userd + '"' + "/unknown.pro"
        else:
            self.tab0_fold_userd = QDir.homePath() + "/unknown.pro"
        
        self.tab0_fold_edit1.setFont(font)
        self.tab0_fold_edit1.setText(self.tab0_fold_userd)
        
        self.tab0_fold_scroll1 = QScrollArea()
        self.tab0_fold_scroll1.setWidgetResizable(True)
        self.tab0_fold_scroll1.setMinimumWidth(300)
        self.tab0_fold_scroll1.setMaximumWidth(300)
        self.tab0_fold_scroll1.setMinimumHeight(215)
        
        self.tab0_fold_push11  = MyPushButton(self, "Create", 1, self.create_project_clicked)
        self.tab0_fold_push12  = MyPushButton(self, "Open"  , 2, self.open_project_clicked)
        self.tab0_fold_push13  = MyPushButton(self, "Repro" , 3, self.repro_project_clicked)
        self.tab0_fold_push14  = MyPushButton(self, "Build" , 4, self.build_project_clicked)
        #        
        #
        self.tab0_fold_scroll2 = QScrollArea()
        self.tab0_fold_scroll2.setWidgetResizable(True)
        self.tab0_fold_scroll2.setMinimumWidth(300)
        self.tab0_fold_scroll2.setMaximumWidth(300)
        #
        lyfont = QFont("Arial",10)
        
        update = QLabel(_("search for updates"))
        server = QLabel(_("connect to server"))
        
        update.setFont(lyfont)
        server.setFont(lyfont)
        
        update.setMinimumWidth(140)
        server.setMinimumWidth(140)
        #
        self.tab0_topB_vlayout.addWidget(update)
        self.tab0_topB_vlayout.addWidget(server)
        #
        image_path = genv.v__app__donate1__
        DebugPrint(image_path)
        #url = "https://kallup.dev/paypal/observer.html"
        
        donate = ClickableImage()
        button = GradientButton("Online Help", self)
                
        self.tab0_topB_vlayout.addWidget(donate)
        self.tab0_topB_vlayout.addWidget(button)
        #
        self.tab0_topB_hlayout.addWidget(self.tab0_fold_scroll2, alignment=Qt.AlignLeft)
        #
        self.tab0_top1_hlayout.addWidget(self.tab0_fold_text1, alignment=Qt.AlignLeft)
        self.tab0_top1_hlayout.addWidget(self.tab0_fold_edit1, alignment=Qt.AlignLeft)
        self.tab0_top1_hlayout.addWidget(self.tab0_fold_push1, alignment=Qt.AlignLeft)
        #
        #
        self.tab0_topA_vlayout.addWidget(self.tab0_fold_push11 , alignment=Qt.AlignLeft)
        self.tab0_topA_vlayout.addWidget(self.tab0_fold_push12 , alignment=Qt.AlignLeft)
        self.tab0_topA_vlayout.addWidget(self.tab0_fold_push13 , alignment=Qt.AlignLeft)
        self.tab0_topA_vlayout.addWidget(self.tab0_fold_push14 , alignment=Qt.AlignLeft)
        self.tab0_topA_hlayout.addWidget(self.tab0_fold_scroll1, alignment=Qt.AlignLeft)
        #
        self.tab0_topC_hlayout.addLayout(self.tab0_topA_vlayout)
        self.tab0_topC_hlayout.addLayout(self.tab0_topA_hlayout)
        #
        
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
        self.tab0_fold_scroll2_contentWidget = QWidget()
        #
        self.tab0_fold_scroll1.setWidget(self.tab0_fold_scroll1_contentWidget)
        self.tab0_fold_scroll2.setWidget(self.tab0_fold_scroll2_contentWidget)
        #
        #
        self.img_scroll1_layout = QVBoxLayout(self.tab0_fold_scroll1)
        self.img_scroll1_layout.addWidget(self.tab0_fold_scroll1)
        #
        genv.img_doxygen = doxygenImageTracker ()
        genv.img_hlpndoc = helpNDocImageTracker()
        #
        #
        self.img_scroll1_layout.addWidget(genv.img_doxygen)
        self.img_scroll1_layout.addWidget(genv.img_hlpndoc)
        #
        
        scro_layout = QVBoxLayout(self.tab0_fold_scroll2)
        
        # ScrollArea
        scroll_area = QScrollArea()
        scroll_area.setStyleSheet(_("ScrollBarCSS"))
        scroll_area.setWidgetResizable(True)
        scro_layout.addWidget(scroll_area)
        
        # Scrollbares Widget
        scrollable_widget = QWidget()
        scrollable_layout = QVBoxLayout(scrollable_widget)
        
        radio_font = QFont("Consolas",11)
        
        genv.radio_cpp        = QRadioButton("C++        Documentation")
        genv.radio_java       = QRadioButton("Java       Documentation")
        genv.radio_javascript = QRadioButton("JavaScript Documentation")
        genv.radio_python     = QRadioButton("Python     Documentation")
        genv.radio_php        = QRadioButton("PHP        Documentation")
        genv.radio_fortran    = QRadioButton("Fortran    Documentation")
        
        genv.radio_cpp       .setFont(radio_font)
        genv.radio_java      .setFont(radio_font)
        genv.radio_javascript.setFont(radio_font)
        genv.radio_python    .setFont(radio_font)
        genv.radio_php       .setFont(radio_font)
        genv.radio_fortran   .setFont(radio_font)
        
        genv.radio_cpp       .toggled.connect(self.radio_button_toggled)
        genv.radio_java      .toggled.connect(self.radio_button_toggled)
        genv.radio_javascript.toggled.connect(self.radio_button_toggled)
        genv.radio_python    .toggled.connect(self.radio_button_toggled)
        genv.radio_fortran   .toggled.connect(self.radio_button_toggled)
        
        scrollable_layout.addWidget(genv.radio_cpp)
        scrollable_layout.addWidget(genv.radio_java)
        scrollable_layout.addWidget(genv.radio_javascript)
        scrollable_layout.addWidget(genv.radio_python)
        scrollable_layout.addWidget(genv.radio_php)
        scrollable_layout.addWidget(genv.radio_fortran)
        
        # Scrollable Widget in die ScrollArea setzen
        scroll_area.setWidget(scrollable_widget)
        
        #wööö
        #
        self.tab0_top_layout.addLayout(self.tab0_topV_vlayout)
        
        self.tab0_file_text = QLabel("File:", self.tab0_0)
        
        self.tab0_left_layout.addWidget(self.tab0_file_text)
        self.tab0_path = QDir.homePath()
        
        self.tab0_help_list1   = QListWidget()
        self.tab0_help_list1.setStyleSheet(_("ScrollBarCSS"))
        self.tab0_help_list1.setMinimumWidth(320)
        self.tab0_help_list1.setMaximumWidth(320)
        self.tab0_help_list1.setMaximumHeight(150)
        self.tab0_help_list1.setIconSize(QSize(34,34))
        self.tab0_help_list1.setFont(QFont(genv.v__app__font, 12))
        self.tab0_help_list1.font().setBold(True)
        self.tab0_help_list1.itemClicked.connect(self.tab0_help_list1_item_click)
        
        self.list_blue_item1 = QListWidgetItem(_("Page Template:"))
        self.list_blue_item1.setBackground(QColor("navy"))
        self.list_blue_item1.setForeground(QColor("yellow"))
        self.list_blue_item1.setFlags(
        self.list_blue_item1.flags() & ~Qt.ItemIsSelectable)
        self.tab0_help_list1.addItem(self.list_blue_item1)
        
        liste = [
            [_("HTML WebSite Template")],
            [_("PDF  Portable Docuement Format")]
        ]
        for item in liste:
            self.list_item1 = QListWidgetItem(_(item[0]))
            self.list_item1.setFont(self.tab0_help_list1.font())
            self.tab0_help_list1.addItem(self.list_item1)
        
        self.list_blue_item2 = QListWidgetItem(_("empty"))
        self.list_blue_item2.setBackground(QColor("white"))
        self.list_blue_item2.setForeground(QColor("white"))
        self.list_blue_item2.setFlags(
        self.list_blue_item2.flags() & ~Qt.ItemIsSelectable)
        self.tab0_help_list1.addItem(self.list_blue_item2)
        
        ###
        self.tab0_help_list2   = QListWidget()
        self.tab0_help_list2.setStyleSheet(_("ScrollBarCSS"))
        self.tab0_help_list2.setMinimumWidth(320)
        self.tab0_help_list2.setMaximumWidth(320)
        self.tab0_help_list2.setIconSize(QSize(34,34))
        self.tab0_help_list2.setFont(QFont(genv.v__app__font, 12))
        self.tab0_help_list2.font().setBold(True)
        self.tab0_help_list2.itemClicked.connect(self.tab0_help_list2_item_click)
        
        self.list_blue_item3 = QListWidgetItem(_("Project Template:"))
        self.list_blue_item3.setBackground(QColor("navy"))
        self.list_blue_item3.setForeground(QColor("yellow"))
        self.list_blue_item3.setFlags(
        self.list_blue_item3.flags() & ~Qt.ItemIsSelectable)
        self.tab0_help_list2.addItem(self.list_blue_item3)
        
        liste = [
            [_("Empty Project")         , os.path.join("emptyproject" + genv.v__app__img_ext__) ],
            [_("Recipe")                , os.path.join("recipe"       + genv.v__app__img_ext__) ],
            [_("API Project")           , os.path.join("api"          + genv.v__app__img_ext__) ],
            [_("Software Documentation"), os.path.join("software"     + genv.v__app__img_ext__) ],
        ]
        for item in liste:
            self.list_item2 = QListWidgetItem(_(item[0]))
            self.list_item2.setIcon(QIcon(os.path.join(genv.v__app__img__int__, item[1])))
            self.list_item2.setFont(self.tab0_help_list2.font())
            self.tab0_help_list2.addItem(self.list_item2)
        
        ###
        self.tab0_help_list3   = QListWidget()
        self.tab0_help_list3.setStyleSheet(_("ScrollBarCSS"))
        self.tab0_help_list3.setMinimumWidth(320)
        self.tab0_help_list3.setMaximumWidth(320)
        self.tab0_help_list3.setIconSize(QSize(34,34))
        self.tab0_help_list3.setFont(QFont(genv.v__app__font, 12))
        self.tab0_help_list3.font().setBold(True)
        self.tab0_help_list3.itemDoubleClicked.connect(self.tab0_help_list3_item_click)
        
        self.list_blue_item3 = QListWidgetItem(_("Projects:"))
        self.list_blue_item3.setBackground(QColor("navy"))
        self.list_blue_item3.setForeground(QColor("yellow"))
        self.list_blue_item3.setFlags(
        self.list_blue_item3.flags() & ~Qt.ItemIsSelectable)
        self.tab0_help_list3.addItem(self.list_blue_item3)
        ##
        genv.v__app__config.read(genv.v__app__config_ini)
        genv.v__app__helprojects = []
        i = 1
        try:
            while True:
                if i == 10:
                    break
                item = genv.v__app__config.get("helprojects", "help" + str(i))
                genv.v__app__helprojects.append(item)
                list_item = QListWidgetItem(item)
                self.tab0_help_list3.addItem(list_item)
                i += 1
        except Exception as e:
            DebugPrint(e)
        
        self.tab0_help_layout = QVBoxLayout()
        self.tab0_help_layout.addWidget(self.tab0_help_list1)
        self.tab0_help_layout.addWidget(self.tab0_help_list2)
        self.tab0_help_layout.addWidget(self.tab0_help_list3)
        
        self.tab0_left_layout.addWidget(self.tab0_file_text)
        self.tab0_left_layout.addLayout(self.tab0_help_layout)
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
        self.tab1_fold_text = QLabel(_("Directory:"), self.tab1_0)
        self.tab1_file_text = QLabel(_("File:"), self.tab1_0)
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
        
        self.tab1_file_tree.setStyleSheet(_(genv.css_model_header) + _("ScrollBarCSS"))
        
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
        self.tab1_path_lineEdit.setStyleSheet(_(genv.css_button_style))
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
        self.tab1_startButton.setStyleSheet(_(genv.css_button_style))
        self.tab1_startButton.clicked.connect(self.startWatching)
        self.tab1_left_layout.addWidget(self.tab1_startButton)
        
        self.tab1_stopButton = QPushButton('Stop', self.tab1_0)
        self.tab1_stopButton.setStyleSheet(_(genv.css_button_style))
        self.tab1_stopButton.clicked.connect(self.stopWatching)
        self.tab1_left_layout.addWidget(self.tab1_stopButton)
        
        # ComboBox für Zeitangaben
        self.tab1_timeComboBox = QComboBox(self.tab1_0)
        self.tab1_timeComboBox.addItems(["10", "15", "20", "25", "30", "60", "120"])
        self.tab1_timeComboBox.setStyleSheet(_(genv.css_button_style))
        self.tab1_timeComboBox.setMaximumWidth(49)
        self.tab1_left_layout.addWidget(self.tab1_timeComboBox)
        
        # Label für den Countdown
        self.tab1_countdownLabel = QLabel('Select time:', self.tab1_0)
        self.tab1_left_layout.addWidget(self.tab1_countdownLabel)
        
        # mitte Seite
        self.tab1_preActionList = QListWidget(self.tab1_0)
        self.tab1_preActionList.setStyleSheet(_("ScrollBarCSS"))
        self.tab1_preActionList_Label  = QLabel(_("Content:"), self.tab1_0)
        self.tab1_preActionList_Editor = QPlainTextEdit()
        self.tab1_preActionList_Editor.setStyleSheet(_("ScrollBarCSS"))
        #
        self.tab1_middle_layout.addWidget(self.tab1_preActionList)
        self.tab1_middle_layout.addWidget(self.tab1_preActionList_Label)
        self.tab1_middle_layout.addWidget(self.tab1_preActionList_Editor)
        
        #
        self.tab1_preActionComboBox = QComboBox(self.tab1_0)
        self.tab1_preActionComboBox.addItems([_(" Message"), _(" Script"), " URL", " FTP"])
        self.tab1_preActionComboBox.setStyleSheet(_(css_combobox_style))
        self.tab1_timeComboBox.setMaximumWidth(49)
        self.tab1_middle_layout.addWidget(self.tab1_preActionComboBox)
        
        self.tab1_preEditLineLabel = QLabel("Text / File:", self.tab1_0)
        self.tab1_middle_layout.addWidget(self.tab1_preEditLineLabel)
        #
        self.tab1_pre_layout = QHBoxLayout()
        
        self.tab1_preEditLineText = QLineEdit(self.tab1_0)
        self.tab1_preEditLineText.setStyleSheet(_(genv.css_button_style))
     
        self.tab1_path_lineButton.setMaximumHeight(28)
        
        #
        self.tab1_pre_layout.addWidget(self.tab1_preEditLineText)
        
        self.tab1_middle_layout.addLayout(self.tab1_pre_layout)
        
        self.tab1_preAddButton = QPushButton(_("Add"))
        self.tab1_preAddButton.setStyleSheet(_(genv.css_button_style))
        #
        self.tab1_preDelButton = QPushButton(_("Delete"))
        self.tab1_preDelButton.setStyleSheet(_(genv.css_button_style))
        #            
        self.tab1_preClrButton = QPushButton(_("Clear All"))
        self.tab1_preClrButton.setStyleSheet(_(genv.css_button_style))
        
        self.tab1_preAddButton.clicked.connect(self.button_clicked_preadd)
        self.tab1_preDelButton.clicked.connect(self.button_clicked_preDel)
        self.tab1_preClrButton.clicked.connect(self.button_clicked_preClr)
        #
        self.tab1_middle_layout.addWidget(self.tab1_preAddButton)
        self.tab1_middle_layout.addWidget(self.tab1_preDelButton)
        self.tab1_middle_layout.addWidget(self.tab1_preClrButton)
        
        
        # rechte Seite
        self.tab1_postActionList = QListWidget(self.tab1_0)
        self.tab1_postActionList.setStyleSheet(_("ScrollBarCSS"))
        self.tab1_postActionList_Label  = QLabel(_("Content:"), self.tab1_0)
        self.tab1_postActionList_Editor = QPlainTextEdit()
        self.tab1_postActionList_Editor.setStyleSheet(_("ScrollBarCSS"))
        #
        self.tab1_right_layout.addWidget(self.tab1_postActionList)
        self.tab1_right_layout.addWidget(self.tab1_postActionList_Label)
        self.tab1_right_layout.addWidget(self.tab1_postActionList_Editor)
        
        self.tab1_postActionComboBox = QComboBox(self.tab1_0)
        self.tab1_postActionComboBox.addItems([_(" Message"), _(" Script"), " URL", " FTP"])
        self.tab1_postActionComboBox.setStyleSheet(_(css_combobox_style))
        self.tab1_right_layout.addWidget(self.tab1_postActionComboBox)
        
        self.tab1_postEditLineLabel = QLabel("Text / File:", self.tab1_0)
        self.tab1_right_layout.addWidget(self.tab1_postEditLineLabel)
        #
        self.tab1_post_layout = QHBoxLayout()
        
        self.tab1_postEditLineText = QLineEdit(self.tab1_0)
        self.tab1_postEditLineText.setStyleSheet(_(genv.css_button_style))
        #
        self.tab1_post_layout.addWidget(self.tab1_postEditLineText)
        self.tab1_right_layout.addLayout(self.tab1_post_layout)
        
        self.tab1_postAddButton = QPushButton(_("Add"))
        self.tab1_postAddButton.setStyleSheet(_(genv.css_button_style))
        #
        self.tab1_postDelButton = QPushButton(_("Delete"))
        self.tab1_postDelButton.setStyleSheet(_(genv.css_button_style))
        #
        self.tab1_postClrButton = QPushButton(_("Clear All"))
        self.tab1_postClrButton.setStyleSheet(_(genv.css_button_style))
        
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
        self.webView1.setHtml(_(genv.html_content), baseUrl = QUrl.fromLocalFile('.'))
        
        self.tab5_top_layout.addWidget(self.webView1);            
        self.tab0_top_layout.addLayout(self.tab0_left_layout)
        
        self.tab1_top_layout.addLayout(self.tab1_left_layout)
        self.tab1_top_layout.addLayout(self.tab1_middle_layout)
        self.tab1_top_layout.addLayout(self.tab1_right_layout)
 
        self.set_window_layout()
        
        #return
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateCountdown)
        
        self.interval = 0
        self.currentTime = 0
        
    def set_window_layout(self):
        
        self.front_content_widget.setLayout(self.front_content_layout)
        self.front_scroll_area   .setWidget(self.front_content_widget)
        
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.front_scroll_area)
        splitter.addWidget(genv.servers_scroll)
        #
        self.main_content_layout.addWidget(splitter)
        
        #self.main_content_layout.addWidget(self.front_scroll_area)
        #self.main_content_layout.addWidget(genv.servers_scroll)
        
        
        #genv.servers_layout.setStyleSheet("background-color:yellow;")
        genv.servers_scroll.show()
        
        self.main_layout.addWidget(self.title_bar)
        self.main_layout.addWidget(self.menu_bar)
        self.main_layout.addWidget(self.tool_bar)
        self.main_layout.addLayout(self.main_content_layout)
        self.main_layout.addWidget(self.status_bar)
        
        self.setLayout(self.main_layout)
        
    def radio_button_toggled(self):
        sender = self.sender()
        if sender.isChecked():
            showInfo(_("Attention:\nproject properties was changed."))
            text = sender.text()
            if text.startswith("C++"):
                genv.doc_lang = genv.DOC_LANG_CPP
            elif text.startswith("Java"):
                genv.doc_lang = genv.DOC_LANG_JAVA
            elif text.startswith("JavaScript"):
                genv.doc_lang = genv.DOC_LANG_JAVASCRIPT
            elif text.startswith("Python"):
                genv.doc_lang = genv.DOC_LANG_PYTHON
            elif text.startswith("PHP"):
                genv.doc_lang = genv.DOC_LANG_PHP
            elif text.startswith("Fortran"):
                genv.doc_lang = genv.DOC_LANG_FORTRAN
            else:
                showError(_("Error:\nunknown help project language."))
                return False
        
        genv.v__app_win.write_config_part()
        return True
    
    def write_config_part(self):
        try:
            if not genv.doc_project_open:
                return False
                
            genv.doc_author   = self.findChild(myLineEdit, "doxygen_project_author").text()
            genv.doc_name     = self.findChild(myLineEdit, "doxygen_project_name"  ).text()
            genv.doc_number   = self.findChild(myLineEdit, "doxygen_project_number").text()
            
            genv.doc_logo     = self.findChild(QLabel,     "doxygen_project_logo"  )
            genv.doc_recursiv = self.findChild(QCheckBox,  "doxygen_project_scan_recursiv")
            
            if not hasattr(genv.doc_logo, "pixmap_name"):
                showError(_("Error:\ncan not get pixmap name."))
                return False
            genv.doc_logo = genv.doc_logo.pixmap_name
            
            if not genv.doc_recursiv.isChecked():
                genv.doc_recursiv = "0"
            else:
                genv.doc_recursiv = "1"
            
            if genv.doc_framework == genv.DOC_FRAMEWORK_DOXYGEN:
                genv.doc_type = 0
            elif genv.doc_framework == genv.DOC_FRAMEWORK_HELPNDOC:
                genv.doc_type = 1
            else:
                genv.doc_type = -1
            
            genv.save_config_file()
            
        except configparser.DuplicateSectionError as e:
            showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
            return False
            
        except PermissionError as e:
            showError(_("Error:\nyou have no permissions to write config file."))
            return False
            
    def tab0_help_list3_item_click(self, item):
        found = False
        file  = item.text()
        for name in genv.v__app__helprojects:
            if file.lower() == name.lower():
                found = True
                break
        if not found:
            showError(_("Error:\nproject name item error."))
            return False
        
        file_path = item.text()
        _internal = False
        
        try:
            if not genv.doc_project_open:
                genv.doc_project_open = True
                genv.v__app__config_ini_help = file_path
                
                ## 0xA0100
                genv.save_config_file()
                    
                if genv.v__app__config_help == None:
                    genv.v__app__config_help = configparser.ConfigParser()
                    genv.v__app__config_help.read(genv.v__app__config_ini_help)
            else:
                genv.v__app_win.write_config_part()
                genv.v__app__config_help.read(genv.v__app__config_ini_help)
        
        except PermissionError:
            showError(_("Error:\nyou have not enough permissions to read/write files."))
            return False
            
        except configparser.NoSectionError as e:
            showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
            return False
            
        except configparser.NoOptionError as e:
            showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
            return False
        
        except configparser.DuplicateSectionError as e:
            if not genv.v__app_win.write_config_part():
                showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
                return False
            else:
                genv.v__app__config_help.read(genv.v__app__config_ini_help)
                
        except Exception as e:
            showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
            return False
            
        try:
            try:
                genv.doc_framework = int(genv.v__app__config_help.get("common" , "framework"))
                genv.doc_template  = int(genv.v__app__config_help.get("common" , "template"))
                genv.doc_type      = int(genv.v__app__config_help.get("project", "type"))
                genv.doc_type_out  = int(genv.v__app__config_help.get("project", "doc_out"))
                #
                item1 = self.tab0_help_list1.item(genv.doc_type_out + 1)
                item2 = self.tab0_help_list2.item(genv.doc_template + 1)
                #
                self.tab0_help_list1.setCurrentItem(item1)
                self.tab0_help_list2.setCurrentItem(item2)
                #
                genv.v__app_win.write_config_part()
                
                item1 = self.tab0_help_list1.item(genv.doc_type_out + 1)
                item2 = self.tab0_help_list2.item(genv.doc_template + 1)
                
            except configparser.NoOptionError as e:
                content = (""
                + _("Error:\nset default values\n\n")
                + "Error: " + str(e) + "\n"
                + "Details:\n"       + traceback.format_exc())
                showError(content)
                genv.doc_framework = genv.DOC_FRAMEWORK_DOXYGEN
                genv.doc_template  = 0
                
                if genv.doc_type_out == 0:
                    item = self.tab0_help_list1.item(0)
                    self.tab0_help_list1.setCurrentItem(item)
                elif genv.doc_type_out == 1:
                    item = self.tab0_help_list1.item(1)
                    self.tab0_help_list1.setCurrentItem(item)
                else:
                    item = self.tab0_help_list1.item(0)
                    self.tab0_help_list1.setCurrentItem(item)
                    genv.doc_type_out = -2
                
                if genv.doc_type == 0:
                    item = self.tab0_help_list2.item(0)
                    self.tab0_help_list2.setCurrentItem(item)
                elif genv.doc_type == 1:
                    item = self.tab0_help_list2.item(1)
                    self.tab0_help_list2.setCurrentItem(item)
                else:
                    item = self.tab0_help_list2.item(0)
                    self.tab0_help_list2.setCurrentItem(item)
                    genv.doc_type = -3
                #
                genv.v__app_win.write_config_part()
                
            except configparser.NoSectionError as e:
                content = (""
                + _("Error:\nset default values\n\n")
                + "Error: " + str(e) + "\n"
                + "Details:\n"       + traceback.format_exc())
                showError(content)
                genv.doc_framework = genv.DOC_FRAMEWORK_DOXYGEN
                genv.doc_template  = 0
                
                if genv.doc_type_out == 0:
                    item = self.tab0_help_list1.item(0)
                    self.tab0_help_list1.setCurrentItem(item)
                elif genv.doc_type_out == 1:
                    item = self.tab0_help_list1.item(1)
                    self.tab0_help_list1.setCurrentItem(item)
                else:
                    item = self.tab0_help_list1.item(0)
                    self.tab0_help_list1.setCurrentItem(item)
                    genv.doc_type_out = -4
                
                if genv.doc_type == 0:
                    item = self.tab0_help_list2.item(0)
                    self.tab0_help_list2.setCurrentItem(item)
                elif genv.doc_type == 1:
                    item = self.tab0_help_list2.item(1)
                    self.tab0_help_list2.setCurrentItem(item)
                else:
                    item = self.tab0_help_list2.item(0)
                    self.tab0_help_list2.setCurrentItem(item)
                    genv.doc_type = -5
                #
                genv.v__app_win.write_config_part()
                
            text1 = _("Error:\ncould not found object:\n")
            if genv.doc_framework == genv.DOC_FRAMEWORK_DOXYGEN:
                if genv.img_doxygen.bordercolor == "lime":
                    self.trigger_mouse_press(genv.img_doxygen)
                    self.trigger_mouse_press(genv.img_doxygen)
                else:
                    self.trigger_mouse_press(genv.img_doxygen)
                    #
                self.help_tabs.removeTab(3)
                self.help_tabs.removeTab(2)
                self.help_tabs.removeTab(1)
                self.help_tabs.insertTab(1, self.tab3, _("DoxyGen"))
                self.help_tabs.setCurrentIndex(1)
                #
                txt2 = "doxygen_project_name"
                item = self.findChild(myLineEdit, txt2)
                if item:
                    try:
                        genv.doc_name = genv.v__app__config_help.get("project", "name")
                        item.setText(genv.doc_name)
                        item.repaint()
                    except configparser.NoSectionError as e:
                        genv.v__app_win.write_config_part()
                        genv.v__app__config_help.read(genv.v__app__config_ini_help)
                    #
                else:
                    showError(text1 + txt2)
                    return False
                
                txt2 = "doxygen_project_author"
                item = self.findChild(myLineEdit, txt2)
                if item:
                    genv.doc_author = genv.v__app__config_help.get("project", "author")
                    item.setText(genv.doc_author)
                    item.repaint()
                    #
                else:
                    showError(text1 + txt2)
                    return False
                    
                txt2 = "doxygen_project_number"
                item = self.findChild(myLineEdit, txt2)
                if item:
                    name = genv.v__app__config_help.get("project", "number")
                    item.setText(name)
                    item.repaint()
                    #
                else:
                    showError(text1 + txt2)
                    return False
                    
                item1  = self.findChild(myLineEdit, "doxygen_project_srcdir")
                item2  = self.findChild(myLineEdit, "doxygen_project_dstdir")
                
                genv.doc_srcdir = genv.v__app__config_help.get("project", "srcdir")
                genv.doc_dstdir = genv.v__app__config_help.get("project", "dstdir")
                
                item1.setText(genv.doc_srcdir)
                item2.setText(genv.doc_dstdir)
                
                if len(genv.doc_srcdir.split()) < 1\
                or len(genv.doc_dstdir.split()) < 1:
                    return False
                
                found  = True
                if item1:
                    if not os.path.exists(genv.doc_srcdir):
                        msg = QMessageBox()
                        msg.setWindowTitle(_("Confirmation"))
                        msg.setText(_(""
                        + "Error:\nsource dir is not a valid directorie item.\n"
                        + "Either it is not a directory or the path to the\n"
                        + "directory does not exists.\n\n"
                        + "Would you create create the directory ?"))
                        
                        msg.setIcon(QMessageBox.Question)
                        
                        btn_yes = msg.addButton(QMessageBox.Yes)
                        btn_no  = msg.addButton(QMessageBox.No)
                        
                        msg.setStyleSheet(_("msgbox_css"))
                        result = msg.exec_()
                        
                        if result == QMessageBox.Yes:
                            try:
                                os.makedirs(genv.doc_srcdir, exist_ok=True)
                                item1.setText(genv.doc_srcdir)
                                item2.setText(genv.doc_dstdir)
                                #
                                item1.repaint()
                                item2.repaint()
                                #
                            except FileNotFoundError as e:
                                showError(_("Error:\nsource directory could not be found/created."))
                                item1.setText(genv.doc_srcdir)
                                item2.setText(genv.doc_dstdir)
                                #
                                item1.repaint()
                                item2.repaint()
                                #
                                return False
                            except PermissionError as e:
                                showError(_("Error:\nno permissions to create the source directory."))
                                item1.setText(genv.doc_srcdir)
                                item2.setText(genv.doc_dstdir)
                                #
                                item1.repaint()
                                item2.repaint()
                                #
                                return False
                            except Exception as e:
                                showError(_("Error:\nsource directory could not be created."))
                                item1.setText(genv.doc_srcdir)
                                item2.setText(genv.doc_dstdir)
                                #
                                item1.repaint()
                                item2.repaint()
                                #
                                return False
                                
                        elif result == QMessageBox.No:
                            showError(_("Error:\nuser aborted creeat the directory."))
                            found = False
                            
                    if (not os.path.isdir(genv.doc_srcdir)) or (os.path.isfile(genv.doc_srcdir)):
                        showError(_(""
                        + "Error:\nsource dir is not a valid directorie item.\n"
                        + "Either it is not a directory or the path to the\n"
                        + "directory does not exists."))
                        #
                        item1.setText("") ; item2.setText("")
                        item1.repaint()   ; item2.repaint()
                        return False
                        
                    item1.setText(genv.doc_srcdir)
                    item1.repaint()
                    #
                else:
                    showError(text1 + txt2)
                    return False
                    
                found = True
                if item2:
                    if not os.path.exists(genv.doc_dstdir):
                        msg = QMessageBox()
                        msg.setWindowTitle(_("Confirmation"))
                        msg.setText(_(""
                        + "Error:\ntarget dir is not a valid directorie item.\n"
                        + "Either it is not a directory or the path to the\n"
                        + "directory does not exists.\n\n"
                        + "Would you create create the directory ?"))
                        
                        msg.setIcon(QMessageBox.Question)
                        
                        btn_yes = msg.addButton(QMessageBox.Yes)
                        btn_no  = msg.addButton(QMessageBox.No)
                        
                        msg.setStyleSheet(_("msgbox_css"))
                        result = msg.exec_()
                        
                        if result == QMessageBox.Yes:
                            try:
                                os.makedirs  (genv.doc_dstdir, exist_ok=True)
                                item2.setText(genv.doc_dstdir)
                            except FileNotFoundError as e:
                                showError(_("Error:\ntarget directory could not be found/created."))
                                item1.setText(""); item1.repaint()
                                item2.setText(""); item2.repaint()
                                #
                                return False
                            except PermissionError as e:
                                showError(_("Error:\nno permissions to create the target directory."))
                                item1.setText(""); item1.repaint()
                                item2.setText(""); item2.repaint()
                                return False
                            except Exception as e:
                                showError(_("Error:\ntarget directory could not be created."))
                                item1.setText(""); item1.repaint()
                                item2.setText(""); item2.repaint()
                                return False
                                
                        elif result == QMessageBox.No:
                            showError(_("Error:\nuser aborted creeat the directory."))
                            found = False
                    else:
                        msg = QMessageBox()
                        msg.setWindowTitle(_("Confirmation"))
                        msg.setText(_(""
                        + "Error:\ntarget dir already exists.\n"
                        + "Would you DELETE and RE-CREATE the directory ?"))
                        
                        msg.setIcon(QMessageBox.Question)
                        
                        btn_yes = msg.addButton(QMessageBox.Yes)
                        btn_no  = msg.addButton(QMessageBox.No)
                        
                        msg.setStyleSheet(_("msgbox_css"))
                        result = msg.exec_()
                        
                        if result == QMessageBox.Yes:
                            try:
                                if "_internal" in genv.doc_dstdir \
                                or "_internal" in genv.doc_srcdir:
                                    showError(_("Error:\n_internal dir tree can not be delete."))
                                    _internal = True
                                else:
                                    _internal = False
                                    shutil.rmtree(genv.doc_dstdir)
                                    os.makedirs  (genv.doc_dstdir, exist_ok=True)
                                    
                            except FileNotFoundError as e:
                                showError(_("Error:\ndirectory could not be found/created."))
                                return False
                            except PermissionError as e:
                                showError(_("Error:\nno permissions to create the target directory."))
                                return False
                            except Exception as e:
                                showError(_("Error:\ntarget directory could not be created."))
                                return False
                        
                    if (not os.path.isdir(genv.doc_dstdir)) or (os.path.isfile(genv.doc_dstdir)):
                        showError(_(""
                        + "Error:\ntarget dir is not a valid directorie item.\n"
                        + "Either it is not a directory or the path to the\n"
                        + "directory does not exists."))
                        
                        item1.setText("") ; item2.setText("")
                        item1.repaint()   ; item2.repaint()
                        return False
                    
                    if "_internal" in genv.doc_dstdir \
                    or "_internal" in genv.doc_srcdir:
                        showError(_("Error:\n_internal dir tree can not be delete."))
                        _internal = True
                        return False
                    else:
                        item2.setText(genv.doc_dstdir)
                        item2.repaint()
                else:
                    showError(text1 + txt2)
                    return False
                
                radio_check = "0"
                combo_check = "0"
                radio_no    = "3"
                check_box   = "0"
                radio_item  = None
                #
                try:
                    if genv.v__app__config_help == None:
                        genv.v__app__config_help = configparser.ConfigParser()
                        genv.v__app__config_help.read(genv.v__app__config_ini_help)
                    
                    if not "mode" in genv.v__app__config_help:
                        raise configparser.NoSectionError
                    #
                    if not "project" in genv.v__app__config_help:
                        raise configparser.NoSectionError
                        
                    radio_check = genv.v__app__config_help.get("mode"   , "doc_entries")
                    combo_check = genv.v__app__config_help.get("mode"   , "cross")
                    radio_no    = genv.v__app__config_help.get("mode"   , "optimized")
                    check_box   = genv.v__app__config_help.get("project", "scan_recursiv")
                    #
                    genv.doc_optimize = int(radio_no)
                    #
                    radio_item  = self.findChild(QRadioButton, "mode_opti0" + str(int(radio_no) + 4))
                    if not radio_item:
                        showInfo("radio")
                    
                except configparser.NoOptionError as e:
                    genv.v__app_win.write_config_part()
                    genv.v__app__config_help.read(genv.v__app__config_ini_help)
                    
                    radio_item = self.findChild(
                        QRadioButton,
                        "mode_opti0" + str(int(radio_no) + 4))
                            
                except configparser.NoSectionError as e:
                    try:
                        if not genv.v__app_win.write_config_part():
                            return False
                        
                        genv.v__app__config_help.read(genv.v__app__config_ini_help)
                        radio_item = self.findChild(
                            QRadioButton,
                            "mode_opti0" + str(int(radio_no) + 4))
                            
                    except FileNotFoundError as e:
                        showError(_("Error:\nfile could not be found/created."))
                        return False
                    except PermissionError as e:
                        showError(_("Error:\nno permissions to read/write file."))
                        return False
                    except Exception as e:
                        showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
                        return False
                #
                textA = "doxygen_mode_document_entries_only"
                textB = "doxygen_mode_all_entries"
                textC = "doxygen_mode_cross_ref"
                textD = "doxygen_project_scan_recursiv"
                
                item1 = self.findChild(QRadioButton, textA)
                item2 = self.findChild(QRadioButton, textB)
                item3 = self.findChild(QCheckBox,    textC)
                item4 = self.findChild(QCheckBox,    textD)
                
                if item1 and item2:
                    if int(radio_check) == 0:
                        item1.setChecked(True)
                        genv.doc_entries = 0
                    elif int(radio_check) == 1:
                        item2.setChecked(True)
                        genv.doc_entries = 1
                    else:
                        showError(_("Error:\ndocument entries check logic error."))
                        return False
                else:
                    showError(text1 + textA + "\n" + textB)
                    return False
                
                if item3:
                    if int(combo_check) == 0:
                        item3.setChecked(False)
                        genv.doc_cross = 0
                        genv.v__app_win.write_config_part()
                    elif int(combo_check) == 1:
                        item3.setChecked(True)
                        genv.doc_cross = 1
                        genv.v__app_win.write_config_part()
                    else:
                        genv.doc_cross = -1
                        genv.v__app_win.write_config_part()
                        showError(_("Error:\ncross ref check logic error."))
                        return False
                else:
                    genv.doc_cross = -1
                    genv.v__app_win.write_config_part()
                    showError(text1 + textC)
                    return False
                
                if item4:
                    check_box = genv.v__app__config_help.get("project", "scan_recursiv")
                    if int(check_box) == 0:
                        item4.setChecked(False)
                        genv.doc_recursiv = 0
                        genv.v__app_win.write_config_part()
                    elif int(check_box) == 1:
                        item4.setChecked(True)
                        genv.doc_recursiv = 1
                        genv.v__app_win.write_config_part()
                    else:
                        genv.doc_recursiv = -1
                        genv.v__app_win.write_config_part()
                        showError(_("Error:\nscan recursiv check logic error."))
                        return False
                
                if not radio_item:
                    showError(_("Error:\ncan not get opti radio button"))
                    return False
                    
                radio_item.setChecked(True)
            
                # output
                have_errors = False
                
                try:
                    genv.doc_output_html        = int(genv.v__app__config_help.get("output", "doc_html"))
                    genv.doc_output_plain_html  = int(genv.v__app__config_help.get("output", "doc_plain_html"))
                    genv.doc_output_navi        = int(genv.v__app__config_help.get("output", "doc_navi"))
                    genv.doc_output_prepare_chm = int(genv.v__app__config_help.get("output", "doc_prepare_chm"))
                    genv.doc_output_search_func = int(genv.v__app__config_help.get("output", "doc_search_func"))
                    
                except configparser.NoSectionError as e:
                    have_errors = True
                    
                except configparser.NoOptionError as e:
                    have_errors = True
                
                if have_errors:
                    genv.doc_output_html        = 0
                    genv.doc_output_plain_html  = 0
                    genv.doc_output_navi        = 0
                    genv.doc_output_prepare_chm = 0
                    genv.doc_output_search_func = 0
                    #
                    genv.v__app_win.write_config_part()
                    
                    for item in items:
                        item.setChecked(False)
                
                genv.doc_output_html        = int(genv.v__app__config_help.get("output", "doc_html"))
                genv.doc_output_plain_html  = int(genv.v__app__config_help.get("output", "doc_plain_html"))
                genv.doc_output_navi        = int(genv.v__app__config_help.get("output", "doc_navi"))
                genv.doc_output_prepare_chm = int(genv.v__app__config_help.get("output", "doc_prepare_chm"))
                genv.doc_output_search_func = int(genv.v__app__config_help.get("output", "doc_search_func"))
                
                
                item0 = self.findChild(QCheckBox   , "output_html")
                item1 = self.findChild(QRadioButton, "output_plain_html")
                item2 = self.findChild(QRadioButton, "output_navi")
                item3 = self.findChild(QRadioButton, "output_prepare_chm")
                item4 = self.findChild(QCheckBox   , "output_search_func")
                
                if genv.doc_output_html == 1:
                    item0.setEnabled(True)
                    item1.setEnabled(True)
                    item2.setEnabled(True)
                    item3.setEnabled(True)
                    item4.setEnabled(True)
                    
                    item0.setChecked(True)
                else:
                    item0.setEnabled(False)
                    item1.setEnabled(False)
                    item2.setEnabled(False)
                    item3.setEnabled(False)
                    item4.setEnabled(False)
                
                if genv.doc_output_plain_html == 1:
                    if item0.isChecked():
                        item1.setChecked(True)
                else:
                    if item0.isChecked():
                        item1.setChecked(False)
                
                if genv.doc_output_navi == 1:
                    if item0.isChecked():
                        item2.setChecked(True)
                else:
                    if item0.isChecked():
                        item2.setChecked(False)
                
                if genv.doc_output_prepare_chm == 1:
                    if item0.isChecked():
                        item3.setChecked(True)
                else:
                    if item0.isChecked():
                        item3.setChecked(False)
                
                if genv.doc_output_search_func == 1:
                    if item0.isChecked():
                        item4.setChecked(True)
                else:
                    if item0.isChecked():
                        item4.setChecked(False)
                
                # output latex
                item0 = self.findChild(QCheckBox   , "output_latex")
                item1 = self.findChild(QRadioButton, "output_latex_pdf")
                item2 = self.findChild(QRadioButton, "output_latex_imm")
                item3 = self.findChild(QRadioButton, "output_latex_ps")
                
                have_errors = False
                try:
                    genv.doc_output_latex     = int(genv.v__app__config_help.get("output", "doc_latex"))
                    genv.doc_output_latex_pdf = int(genv.v__app__config_help.get("output", "doc_latex_pdf"))
                    genv.doc_output_latex_imm = int(genv.v__app__config_help.get("output", "doc_latex_imm"))
                    genv.doc_output_latex_ps  = int(genv.v__app__config_help.get("output", "doc_latex_ps"))
                except configparser.NoSectionError as e:
                    have_errors = True
                    
                except configparser.NoOptionError as e:
                    have_errors = True
                
                if have_errors:
                    genv.doc_output_latex     = 0
                    genv.doc_output_latex_pdf = 0
                    genv.doc_output_latex_imm = 0
                    genv.doc_output_latex_ps  = 0
                
                genv.v__app_win.write_config_part()
                
                if genv.doc_output_latex == 0:
                    item0.setChecked(False)
                    item1.setEnabled(False)
                    item2.setEnabled(False)
                    item3.setEnabled(False)
                else:
                    item0.setChecked(True)
                    item1.setEnabled(True)
                    item2.setEnabled(True)
                    item3.setEnabled(True)
                
                if item0.isChecked():
                    if genv.doc_output_latex == 0:
                        item0.setChecked(False)
                    else:
                        item0.setChecked(True)
                    
                    if genv.doc_output_latex_pdf == 0:
                        item1.setChecked(False)
                    else:
                        item1.setChecked(True)
                    
                    if genv.doc_output_latex_imm == 0:
                        item2.setChecked(False)
                    else:
                        item2.setChecked(True)
                    
                    if genv.doc_output_latex_ps == 0:
                        item3.setChecked(False)
                    else:
                        item3.setChecked(True)
                
                # out misc
                item1 = self.findChild(QCheckBox, "output_man")
                item2 = self.findChild(QCheckBox, "output_rtf")
                item3 = self.findChild(QCheckBox, "output_xml")
                item4 = self.findChild(QCheckBox, "output_doc")
                
                have_errors = False
                try:
                    genv.doc_output_man = int(genv.v__app__config_help.get("output", "doc_man"))
                    genv.doc_output_rtf = int(genv.v__app__config_help.get("output", "doc_rtf"))
                    genv.doc_output_xml = int(genv.v__app__config_help.get("output", "doc_xml"))
                    genv.doc_output_doc = int(genv.v__app__config_help.get("output", "doc_doc"))
                    
                except configparser.NoSectionError as e:
                    have_errors = True
                    
                except configparser.NoOptionError as e:
                    have_errors = True
                
                if have_errors:
                    genv.doc_output_man = 0
                    genv.doc_output_rtf = 0
                    genv.doc_output_xml = 0
                    genv.doc_output_doc = 0
                
                genv.v__app_win.write_config_part()
                
                if genv.doc_output_man == 1:
                    item1.setChecked(True)
                else:
                    item1.setChecked(False)
                
                if genv.doc_output_rtf == 1:
                    item2.setChecked(True)
                else:
                    item2.setChecked(False)
                
                if genv.doc_output_xml == 1:
                    item3.setChecked(True)
                else:
                    item3.setChecked(False)
                
                if genv.doc_output_doc == 1:
                    item4.setChecked(True)
                else:
                    item4.setChecked(False)
                
                # diagrams
                have_errors = False
                
                item1 = self.findChild(QRadioButton, "dia_not")
                item2 = self.findChild(QRadioButton, "dia_txt")
                item3 = self.findChild(QRadioButton, "dia_bin")
                item4 = self.findChild(QRadioButton, "dia_dot")
                
                try:
                    genv.doc_dia_not = int(genv.v__app__config_help.get("diagrams", "dia_not"))
                    genv.doc_dia_txt = int(genv.v__app__config_help.get("diagrams", "dia_txt"))
                    genv.doc_dia_bin = int(genv.v__app__config_help.get("diagrams", "dia_bin"))
                    genv.doc_dia_dot = int(genv.v__app__config_help.get("diagrams", "dia_dot"))
                    
                except configparser.NoSectionError:
                    have_errors = True
                    
                except configparser.NoOptionError:
                    have_errors = True
                
                if have_errors:
                    genv.doc_dia_not = 0
                    genv.doc_dia_txt = 0
                    genv.doc_dia_bin = 0
                    genv.doc_dia_dot = 0
                
                if genv.doc_dia_not == 0:
                    item1.setChecked(False)
                else:
                    item1.setChecked(True)
                
                if genv.doc_dia_txt == 0:
                    item2.setChecked(False)
                else:
                    item2.setChecked(True)
                
                if genv.doc_dia_bin == 0:
                    item3.setChecked(False)
                else:
                    item3.setChecked(True)
                
                if genv.doc_dia_dot == 0:
                    item4.setChecked(False)
                else:
                    item4.setChecked(True)
                    
                genv.v__app_win.write_config_part()
                
                # graphs
                have_errors = False
                try:
                    genv.doc_dia_class  = int(genv.v__app__config_help.get("graph", "class"))
                    genv.doc_dia_colab  = int(genv.v__app__config_help.get("graph", "colab"))
                    genv.doc_dia_overh  = int(genv.v__app__config_help.get("graph", "overh"))
                    genv.doc_dia_inc    = int(genv.v__app__config_help.get("graph", "inc"))
                    genv.doc_dia_incby  = int(genv.v__app__config_help.get("graph", "incby"))
                    genv.doc_dia_call   = int(genv.v__app__config_help.get("graph", "call"))
                    genv.doc_dia_callby = int(genv.v__app__config_help.get("graph", "callby"))
                    
                except configparser.NoSectionError:
                    have_errors = True
                    
                except configparser.NoOptionError:
                    have_errors = True
                
                if have_errors:
                    genv.doc_dia_class  = 0
                    genv.doc_dia_colab  = 0
                    genv.doc_dia_overh  = 0
                    genv.doc_dia_inc    = 0
                    genv.doc_dia_incby  = 0
                    genv.doc_dia_call   = 0
                    genv.doc_dia_callby = 0
                
                genv.v__app_win.write_config_part()
                
                item1 = self.findChild(QCheckBox, "graph_class")
                item2 = self.findChild(QCheckBox, "graph_colab")
                item3 = self.findChild(QCheckBox, "graph_overh")
                item4 = self.findChild(QCheckBox, "graph_inc")
                item5 = self.findChild(QCheckBox, "graph_incby")
                item6 = self.findChild(QCheckBox, "graph_call")
                item7 = self.findChild(QCheckBox, "graph_callby")
                
                if genv.doc_dia_class  == 0:
                    item1.setChecked(False)
                else:
                    item1.setChecked(True)
                    
                if genv.doc_dia_colab  == 0:
                    item2.setChecked(False)
                else:
                    item2.setChecked(True)
                    
                if genv.doc_dia_overh  == 0:
                    item3.setChecked(False)
                else:
                    item3.setChecked(True)
                    
                if genv.doc_dia_inc    == 0:
                    item4.setChecked(False)
                else:
                    item4.setChecked(True)
                    
                if genv.doc_dia_incby  == 0:
                    item5.setChecked(False)
                else:
                    item5.setChecked(True)
                    
                if genv.doc_dia_call   == 0:
                    item6.setChecked(False)
                else:
                    item6.setChecked(True)
                    
                if genv.doc_dia_callby == 0:
                    item7.setChecked(False)
                else:
                    item7.setChecked(True)
                
                ## 0xA0100
                hid = 0x100
                i   = 1
                for idx in range(5, 23):
                    try:
                        elements = eval(_("label_" + str(idx) + "_elements"))
                        helpID   = hid + i
                        tokenID  = _("A" + f"{helpID:04X}")
                        
                        hid += 0x100
                        i   += 1
                        
                        if hid == 0xa00:
                            hid = 0x1000
                        
                        tok_type   = getattr(genv, "doc_" + tokenID.lower() + "_type", 3)
                        tok_object = getattr(genv, "doc_" + tokenID.lower() + "_object", None)
                        
                        value = genv.v__app__config_help.get(f"expert_{idx}", tokenID)
                        
                        if tok_type == genv.type_check_box:
                            if value.strip() == "0":
                                #showInfo("checkbox: " + tokenID + "\nis not check")
                                setattr(genv, "doc_" + tokenID, 0)
                                tok_object.setChecked(False)
                                tok_object.setText(_(" NO"))
                            else:
                                #showInfo("checkbox: " + tokenID + "\nis checked")
                                setattr(genv, "doc_" + tokenID, 1)
                                tok_object.setChecked(True)
                                tok_object.setText(_(" YES 3"))
                        print(tokenID)
                        
                    except configparser.NoOptionError:
                        genv.v__app__config_help.set(f"expert_{idx}", tokenID.lower(), "0")
                        genv.v__app__config_help[f"expert_{idx}"][tokenID.lower()] = "0"
                        
                    except AttributeError as e:
                        showInfo("TODO: list3")
                        return False
                        ## 0xA0100
                        hid = 0
                        for idx in range(5, 23):
                            elements = eval(_("label_" + str(idx) + "_elements"))
                            hid     += 0x100
                            
                            if hid == 0xa00:
                                hid = 0x1000
                            
                            i = 0
                            for item in elements:
                                helpID  = hid + i + 1
                                tokenID = _("A" + f"{helpID:04X}")
                                
                                value = getattr(genv, "doc_" + tokenID + "_type")
                                
                                #if value == genv.type_check_box:
                                setattr(genv, "doc_" + tokenID, 3)
                                i += 1
                        
                genv.v__app_win.write_config_part()
                
            # framework
            elif genv.doc_framework == genv.DOC_FRAMEWORK_HELPNDOC:
                if genv.img_hlpndoc.bordercolor == "lime":
                    self.trigger_mouse_press(genv.img_doxygen)
                    self.trigger_mouse_press(genv.img_hlpndoc)
                else:
                    self.trigger_mouse_press(genv.img_hlpndoc)
                self.help_tabs.removeTab(2)
                self.help_tabs.removeTab(1)
                self.help_tabs.insertTab(1, self.tab1_0, _("Pre-/Post Actions"))
                self.help_tabs.insertTab(2, self.tab2  , _("Topics"))
                self.help_tabs.insertTab(3, self.tab4  , _("Content"))
            else:
                showError(_("Error:\nframework have no valid setting options."))
                return False
        except Exception as e:
            showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
            return False
            
        try:
            value = genv.v__app__config_help.get("common", "lang")
            if int(value) == genv.DOC_LANG_CPP:
                genv.radio_cpp.setChecked(True)
            
            elif int(value) == genv.DOC_LANG_JAVA:
                genv.radio_java.setChecked(True)
            
            elif int(value) == genv.DOC_LANG_JAVASCRIPT:
                genv.radio_javascript.setChecked(True)
            
            elif int(value) == genv.DOC_LANG_PYTHON:
                genv.radio_python.setChecked(True)
            
            elif int(value) == genv.DOC_LANG_PHP:
                genv.radio_php.setChecked(True)
            
            elif int(value) == genv.DOC_LANG_FORTRAN:
                genv.radio_fortran.setChecked(True)
        except Exception as e:
            showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
            return False
        
        try:
            value = genv.v__app__config_help.get("common", "template")
            item  = self.tab0_help_list2.item(int(value))
            self.tab0_help_list2.setCurrentItem(item)
            #item.setSelected(True)
        except Exception as e:
            showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
            return False
        
        try:
            genv.doc_type_out = int(genv.v__app__config_help.get("project", "doc_out"))
            item = self.tab0_help_list1.item(genv.doc_type_out)
            self.tab0_help_list1.setCurrentItem(item)
            #item.setSelected(True)
        except configparser.NoOptionError as e:
            genv.doc_type_out = 0
            genv.v__app_win.write_config_part()
            item = self.tab0_help_list1.item(genv.doc_type_out)
            self.tab0_help_list1.setCurrentItem(item)
        except Exception as e:
            showError(f"Error: {str(e)}\nDetails:\n{traceback.format_exc()}")
            return False
    
    def tab0_help_list1_item_click(self, item):
        text = item.text()
        DebugPrint("---> " + text)
        if text.startswith("HTML"):
            genv.doc_type_out = genv.DOC_DOCUMENT_HTML
            genv.v__app_win.write_config_part()
            return True
        elif text.startswith("PDF"):
            genv.doc_type_out = genv.DOC_DOCUMENT_PDF
            genv.v__app_win.write_config_part()
            return True
        else:
            genv.doc_type_out = -1
            genv.v__app_win.write_config_part()
            return False
    
    def tab0_help_list2_item_click(self, item):
        text = item.text()
        DebugPrint(text)
        if text == _("Empty Project"):
            genv.doc_template = genv.DOC_TEMPLATE_EMPTY
            genv.v__app_win.write_config_part()
            return True
        elif text == _("Recipe"):
            genv.doc_template = genv.DOC_TEMPLATE_RECIPE
            genv.v__app_win.write_config_part()
            return True
        elif text == _("API Project"):
            genv.doc_template = genv.DOC_TEMPLATE_API
            genv.v__app_win.write_config_part()
            return True
        elif text == _("Software Documentation"):
            genv.doc_template = genv.DOC_TEMPLATE_SOFTWARE
            genv.v__app_win.write_config_part()
            return True
        else:
            genv.doc_template = -1
            genv.v__app_win.write_config_part()
            return False
    
    def repro_project_clicked(self):
        showError("not implemented, yet.")
        return False
    
    def build_project_clicked(self):
        showError("not implemented, yet.")
        return False
    
    def create_project_clicked(self):
        bool_flagA = False
        bool_flagB = False
        bool_flagC = False
        bool_flagD = False
        
        path_error = _(""
        + "Warning:\nA project with the corresponding name already exists.\n"
        + "All data will be lost and override with new informations.")
        
        file_path = Path(self.tab0_fold_edit1.text())
        if not self.tab0_fold_edit1.text().endswith(".pro"):
            showError(_("Error:\nproject name does not fit the requirements."))
            return False
        if file_path.is_dir():
            showError(_("Error:\ngiven file not a file type (is dir)."))
            return False
        if file_path.exists():
            # ------------------------------------------
            # prüfe alle Einträge aus der QListWidget
            # ------------------------------------------
            items = []
            for i in range(self.tab0_help_list3.count()):
                items.append(self.tab0_help_list3.item(i))
            
            for item in items:
                if item.text() == genv.v__app__config_project_ini:
                    #showError(_("Error:\nproject already exists."))
                    showError(path_error)
                    return False
            
            list_item = QListWidgetItem(genv.v__app__config_project_ini)
            list_item.setIcon(QIcon(os.path.join(genv.v__app__img__int__, "project.png")))
            list_item.setFont(self.tab0_help_list2.font())
            self.tab0_help_list3.addItem(list_item)
            
        # ------------------------------
        if genv.radio_cpp.isChecked():
            genv.doc_lang = genv.DOC_LANG_CPP
            bool_flagA = True
        elif genv.radio_java.isChecked():
            genv.doc_lang = genv.DOC_LANG_JAVA
            bool_flagA = True
        elif genv.radio_javascript.isChecked():
            genv.doc_lang = genv.DOC_LANG_JAVASCRIPT
            bool_flagA = True
        elif genv.radio_python.isChecked():
            genv.doc_lang = genv.DOC_LANG_PYTHON
            bool_flagA = True
        elif genv.radio_php.isChecked():
            genv.doc_lang = genv.DOC_LANG_PHP
            bool_flagA = True
        elif genv.radio_fortran.isChecked():
            genv.doc_lang = genv.DOC_LANG_FORTRAN
            bool_flagA = True
        else:
            bool_flagA = False
        # ------------------------------
        if genv.doc_type_out >= 0:
            bool_flagB = True
        else:
            bool_flagB = False
        # ------------------------------
        if genv.doc_framework >= 0:
            bool_flagC = True
        else:
            bool_flagC = False
        # ------------------------------
        if genv.doc_template >= 0:
            bool_flagD = True
        else:
            bool_flagD = False
        # ------------------------------
        if not (bool_flagA == True) \
        or not (bool_flagB == True) \
        or not (bool_flagC == True) \
        or not (bool_flagD == True):
            showError(_("Error:\nNo project documentation selected."))
            return False
        # ------------------------------
        genv.v__app__config_project_ini = self.tab0_fold_edit1.text()
        pro = genv.v__app__config_project_ini
        new = pro.replace('"', '')
        pro = pro.lower()
        if not pro.endswith(".pro"):
            showError(_("Error:\nproject file does not fit requierements."))
            return False
        genv.v__app__config_project_ini = new
        DebugPrint(new)
        if not os.path.exists(new):
            try:
                with open(genv.v__app__config_project_ini, "w", encoding="utf-8") as f:
                    content = (""
                    + "[common]"
                    + "\ntype = helpdoc"
                    + "\nlanguage = en_us"
                    + "\ndoc_doctype = "    + str(genv.doc_type_out)
                    + "\ndoc_template = "   + str(genv.doc_template)
                    + "\ndoc_project = "    + str(genv.doc_project)
                    + "\ndoc_lang = "       + str(genv.doc_lang)
                    + "\n")
                    f.write(content)
                    f.close()
            except Exception as e:
                DebugPrint(e)
                showError(_("Error:\nproject file could not create."))
                genv.doc_project_open = False
                return False
        # -----------------------------------------------------------
        # forward initializations ...
        # -----------------------------------------------------------
        try:
            genv.v__app__pro_config = configparser.ConfigParser()
            genv.v__app__pro_config.read(genv.v__app__config_project_ini)
            
            genv.doc_project_open = True
            
        except Exception as e:
            DebugPrint(e)
            showError(_("Error:\ncofigparser module error."))
            genv.doc_project_open = False
            return False
        
        # ------------------------------------------
        # prüfe alle Einträge aus der QListWidget
        # ------------------------------------------
        items = []
        for i in range(self.tab0_help_list3.count()):
            items.append(self.tab0_help_list3.item(i))
        
        for item in items:
            if item.text() == genv.v__app__config_project_ini:
                showError(_("Error:\nproject already exists."))
                return False
            
        list_item = QListWidgetItem(genv.v__app__config_project_ini)
        list_item.setIcon(QIcon(os.path.join(genv.v__app__img__int__, "project.png")))
        list_item.setFont(self.tab0_help_list2.font())
        self.tab0_help_list3.addItem(list_item)
        
        return True
    
    # todo: if genv.v__app__config_help == None:
    #            genv.v__app__config_help = configparser.ConfigParser()
    #            genv.v__app__config_help.read(genv.v__app__config_ini_help)
    def open_project_clicked(self):
        dialog  = QFileDialog()
        file_path = ""
        icon_size = 20
        
        dialog.setWindowTitle(_("Open Project File"))
        dialog.setStyleSheet (_("QFileDlog"))
        
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setViewMode(QFileDialog.Detail)
        
        dialog.setOption  (QFileDialog.DontUseNativeDialog, True)
        dialog.setNameFilters(["Program Files (*.pro)", "Text Files (*.txt)", "All Files (*)"])
        
        list_views = dialog.findChildren(QListView)
        tree_views = dialog.findChildren(QTreeView)
        
        for view in list_views + tree_views:
            view.setIconSize(QSize(icon_size, icon_size))
        
        if dialog.exec_() == QFileDialog.Accepted:
            file_path = dialog.selectedFiles()[0]
        
        if not file_path:
            msg = QMessageBox()
            msg.setWindowTitle("Information")
            msg.setText(_("no source file given.\n"))
            msg.setIcon(QMessageBox.Question)
            msg.setStyleSheet(_("msgbox_css"))
            
            btn_ok = msg.addButton(QMessageBox.Ok)
            result = msg.exec_()            
            return
        
        if not os.path.isfile(file_path):
            msg = None
            msg = QMessageBox()
            msg.setWindowTitle("Information")
            msg.setText(_(
                "You selected a file, that can not be open.\n"
                "no file will be open."))
            msg.setIcon(QMessageBox.Question)
            msg.setStyleSheet(_("msgbox_css"))
            
            btn_ok = msg.addButton(QMessageBox.Ok)
            result = msg.exec_()
            return
        
        self.tab0_fold_edit1.clear()
        self.tab0_fold_edit1.setText(file_path)
        
        try:
            genv.v__app__config_ini = file_path
            genv.v__app__config.read( file_path )
        
            genv.doc_type = int(genv.v__app__config.get("project", "type"))
        except configparser.NoOptionError as error:
            MyProjectOption()
        
        if genv.doc_framework == genv.DOC_FRAMEWORK_DOXYGEN:
            self.trigger_mouse_press(genv.img_doxygen)
        elif genv.doc_framework == genv.DOC_FRAMEWORK_HELPNDOC:
            self.trigger_mouse_press(genv.img_hlpndoc)
        else:
            showInfo(_("Error: help framework not known."))
            return False
        return True
    
    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self.helper_positions)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.helper_positions()
    
    def helper_positions(self):
        return
        #control_pos  = self.tab0_fold_push2
        #control      = self.helper_overlay
        
        global_pos   = control_pos.mapToGlobal(QPoint(0, 0))
        relative_pos = control_pos.pos()
        
        xpos = relative_pos.x()+70
        ypos = relative_pos.y()+50
        
        control.setObjectName(f"X{xpos}:Y{ypos}")
        control.move(xpos, ypos)
    
    def expand_entry(self, tree_view, model, path):
        index = model.index(path)
        if index.isValid():
            tree_view.expand(index)
    
    def readFromFile(self, file_path):
        file_content = ""
        file = QFile(file_path)
        if file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(file)
            file_content = stream.readAll()
            file.close()
        return file_content
    
    # dbase
    def handleDBase(self):
        self.dbase_tabs = QTabWidget()
        self.dbase_tabs.setStyleSheet(_(genv.css_tabs))
        self.dbase_tabs.hide()
        
        self.dbase_tabs_project_widget = QWidget()
        self.dbase_tabs_editors_widget = QWidget()
        self.dbase_tabs_designs_widget = QWidget()
        self.dbase_tabs_builder_widget = QWidget()
        self.dbase_tabs_datatab_widget = myDataTabWidget(self)
        self.dbase_tabs_reports_widget = QWidget()
        #
        #
        self.dbase_tabs_project_widget.setContentsMargins(1,1,1,1)
        ####
        self.dbase_tabs.addTab(self.dbase_tabs_project_widget, _("dBASE Project"))
        self.dbase_tabs.addTab(self.dbase_tabs_editors_widget, _("dBASE Editor"))
        self.dbase_tabs.addTab(self.dbase_tabs_designs_widget, _("dBASE Designer"))
        self.dbase_tabs.addTab(self.dbase_tabs_builder_widget, _("dBASE SQL Builder"))
        self.dbase_tabs.addTab(self.dbase_tabs_datatab_widget, _("dBASE Data Tables"))
        self.dbase_tabs.addTab(self.dbase_tabs_reports_widget, _("dBASE Reports"))
        ####
        self.dbase_project = ApplicationProjectPage(self.front_content_widget, self.dbase_tabs_project_widget, "dbase")
        self.dbase_editors = ApplicationEditorsPage(self, self.dbase_tabs_editors_widget, "dbase")
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
        #
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
        self.dbase_designer = ApplicationDesignPage(
            self,
            self.dbase_tabs_designs_widget,
            self.dbase_tabs)
    
    def dbase_builder_btn1_clicked(self):
        tableDialog = myAddTableDialog(self)
        tableDialog.exec_()
    
    def dbase_builder_btn2_clicked(self):
        sourceDialog = addDataSourceDialog(self)
        sourceDialog.exec_()
    
    # Electro
    def handleElectro(self):
        self.electro_tabs = QTabWidget()
        self.electro_tabs.setStyleSheet(_(genv.css_tabs))
        self.electro_tabs.hide()
        
        self.electro_tabs_designer_widget = QWidget()
        
        hlayout = QHBoxLayout()
        component_list = QListWidget()
        component_list.addItems(["item1", "item2"])
        
        component_designer = CircuitDesigner()
        
        hlayout.addWidget(component_list)
        hlayout.addWidget(component_designer)
        
        #self.electro_tabs.addLayout(hlayout)
        self.electro_tabs_designer_widget.setLayout(hlayout)
        
        self.electro_tabs.addTab(self.electro_tabs_designer_widget, _("electro"))
        self.main_layout.addWidget(self.electro_tabs)
        return
            
    # pascal
    def handlePascal(self):
        self.pascal_tabs = ApplicationTabWidget([
            _("Pascal Project"),
            _("Pascal Editor"),
            _("Pascal Designer")])
        self.pascal_project  = ApplicationProjectPage(self, self.pascal_tabs.getTab(0), "pascal")
        self.pascal_editors  = ApplicationEditorsPage(self, self.pascal_tabs.getTab(1), "pascal")
        self.pascal_designer = ApplicationDesignPage(
            self,
            self.pascal_tabs.getTab(2),
            self.pascal_tabs)
    
    # isoc
    def handleIsoC(self):
        self.isoc_tabs = ApplicationTabWidget([
            _("ISO-C Project"),
            _("ISO-C Editor"),
            _("ISO-C Designer")])
        self.isoc_project  = ApplicationProjectPage(self, self.isoc_tabs.getTab(0), "isoc")
        self.isoc_editors  = ApplicationEditorsPage(self, self.isoc_tabs.getTab(1), "isoc")
        self.isoc_designer = ApplicationDesignPage(
            self,
            self.isoc_tabs.getTab(2),
            self.isoc_tabs)
    
    # java
    def handleJava(self):
        self.java_tabs = ApplicationTabWidget([
            _("Java Project"),
            _("Java Editor"),
            _("Java Designer")])
        self.java_project  = ApplicationProjectPage(self, self.java_tabs.getTab(0), "java")
        self.java_editors  = ApplicationEditorsPage(self, self.java_tabs.getTab(1), "java")
        self.java_designer = ApplicationDesignPage(
            self,
            self.java_tabs.getTab(2),
            self.java_tabs)
    
    # python
    def handlePython(self):
        self.python_tabs = ApplicationTabWidget([
            _("Python Project"),
            _("Python Editor"),
            _("Python Designer")])
        self.python_project  = ApplicationProjectPage(self, self.python_tabs.getTab(0), "python")
        self.python_editors  = ApplicationEditorsPage(self, self.python_tabs.getTab(1), "python")
        self.python_designer = ApplicationDesignPage(
            self,
            self.python_tabs.getTab(2),
            self.python_tabs)
    
    # prolog
    def handleProlog(self):
        self.prolog_tabs = ApplicationTabWidget([
            _("Prolog Project"),
            _("Prolog Editor"),
            _("Prolog Designer")])
        self.prolog_project  = ApplicationProjectPage(self, self.prolog_tabs.getTab(0), "prolog")
        self.prolog_editors  = ApplicationEditorsPage(self, self.prolog_tabs.getTab(1), "prolog")
        self.prolog_designer = ApplicationDesignPage(
            self,
            self.prolog_tabs.getTab(2),
            self.prolog_tabs)
    
    # fortran
    def handleFortran(self):
        self.fortran_tabs = ApplicationTabWidget([
            _("Fortran Project"),
            _("Fortran Editor"),
            _("Fortran Designer")])
        self.fortran_project  = ApplicationProjectPage(self, self.fortran_tabs.getTab(0), "fortran")
        self.fortran_editors  = ApplicationEditorsPage(self, self.fortran_tabs.getTab(1), "fortran")
        self.fortran_designer = ApplicationDesignPage(
            self,
            self.fortran_tabs.getTab(2),
            self.fortran_tabs)
    
    # lisp
    def handleLISP(self):
        self.lisp_tabs = ApplicationTabWidget([
            _("LISP Project"),
            _("LISP Editor"),
            _("LISP Designer")])
        self.lisp_project  = ApplicationProjectPage(self, self.lisp_tabs.getTab(0), "lisp")
        self.lisp_editors  = ApplicationEditorsPage(self, self.lisp_tabs.getTab(1), "lisp")
        self.lisp_designer = ApplicationDesignPage(
            self,
            self.lisp_tabs.getTab(2),
            self.lisp_tabs)
    
    # javascript
    def handleJavaScript(self):
        self.javascript_tabs = ApplicationTabWidget([
            _("JavaScript Project"),
            _("JavaScript Editor"),
            _("JavaScript Designer")])
        self.javascript_project  = ApplicationProjectPage(self, self.javascript_tabs.getTab(0), "javascript")
        self.javascript_editors  = ApplicationEditorsPage(self, self.javascript_tabs.getTab(1), "javascript")
        self.javascript_designer = ApplicationDesignPage(
            self,
            self.javascript_tabs.getTab(2),
            self.javascript_tabs)
    
    # locale
    def handleLocales(self):
        self.locale_tabs = QTabWidget()
        self.locale_tabs.setStyleSheet(_(genv.css_tabs))
        self.locale_tabs.hide()
        
        self.locale_tabs_project_widget = QWidget()
        self.locale_tabs_editors_widget = QWidget()
        self.locale_tabs_designs_widget = QWidget()
        #
        self.locale_tabs.addTab(self.locale_tabs_project_widget, _("Locales Project"))
        self.locale_tabs.addTab(self.locale_tabs_editors_widget, _("Locales Editor"))
        self.locale_tabs.addTab(self.locale_tabs_designs_widget, _("Locales Designer"))
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
        
        self.load_button = QPushButton(_("Load .mo File"))
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
    
    def downloadCHMTool(self):
        QDesktopServices.openUrl(QUrl("https://learn.microsoft.com/en-us/previous-versions/windows/desktop/htmlhelp/microsoft-html-help-downloads"))
    
    def handlePEWindows(self):
        self.pe_windows_tabs = QTabWidget()
        self.pe_windows_tabs.setStyleSheet(_(genv.css_tabs))
        self.pe_windows_tabs.hide()
        
        self.pe_windows_tabs_project_widget = QWidget()
        self.pe_windows_tabs_editors_widget = QWidget()
        self.pe_windows_tabs_designs_widget = QWidget()
        #
        self.pe_windows_tabs_exe_dll_viewer = ExecutableExplorer()
        #
        self.pe_windows_tabs.addTab(self.pe_windows_tabs_project_widget, _("Win32 Project"))
        self.pe_windows_tabs.addTab(self.pe_windows_tabs_editors_widget, _("Editor"))
        self.pe_windows_tabs.addTab(self.pe_windows_tabs_designs_widget, _("Console"))
        self.pe_windows_tabs.addTab(self.pe_windows_tabs_exe_dll_viewer, _("Tools"))
        ####
        self.main_layout.addWidget(self.pe_windows_tabs)
            
    def handleELFLinux(self):
        self.elf_linux_tabs = QTabWidget()
        self.elf_linux_tabs.setStyleSheet(_(genv.css_tabs))
        self.elf_linux_tabs.hide()
        
        self.elf_linux_tabs_project_widget = QWidget()
        self.elf_linux_tabs_editors_widget = QWidget()
        self.elf_linux_tabs_designs_widget = QWidget()
        #
        self.elf_linux_tabs.addTab(self.elf_linux_tabs_project_widget, _("ELF Project"))
        self.elf_linux_tabs.addTab(self.elf_linux_tabs_editors_widget, _("Editor"))
        self.elf_linux_tabs.addTab(self.elf_linux_tabs_designs_widget, _("Console"))
        ####
        self.main_layout.addWidget(self.elf_linux_tabs)
    
    def handleBasic(self):
        self.basic_tabs = ApplicationTabWidget([
            _("BASIC Project"),
            _("Editor"),
            _("Console")])
        self.basic_tabs_project_widget = ApplicationProjectPage(self, self.basic_tabs.getTab(0), "basic")
        self.basic_tabs_editors_widget = ApplicationEditorsPage(self, self.basic_tabs.getTab(1), "basic")
        self.basic_tabs_designs_widget = QWidget()
        ####
        self.main_layout.addWidget(self.basic_tabs)
        
    def handleConsole(self):
        self.console_tabs = QTabWidget()
        self.console_tabs.setStyleSheet(_(genv.css_tabs))
        self.console_tabs.hide()
        
        vlayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        
        font = QFont("Arial", 10)
        
        group_box = QGroupBox(_("Selecte OS: "))
        group_box.setFont(font)
        
        os_radio_button1 = QRadioButton("MS-DOS")
        os_radio_button2 = QRadioButton("Amiga 500")
        os_radio_button3 = QRadioButton("C-64")
        os_radio_button4 = QRadioButton("Linux")
        
        os_radio_button1.setFont(font)
        os_radio_button2.setFont(font)
        os_radio_button3.setFont(font)
        os_radio_button4.setFont(font)
        
        os_radio_button1.setChecked(True)
        
        dummy = QWidget()
        dummy.setMinimumHeight(32)
        
        vlayout.addWidget(dummy)
        vlayout.addWidget(os_radio_button1)
        vlayout.addWidget(os_radio_button2)
        vlayout.addWidget(os_radio_button3)
        vlayout.addWidget(os_radio_button4)
        vlayout.addStretch()
        
        group_box.setLayout(vlayout)
        
        user_console = DOSConsoleWindow(application_window)
        user_console.show()
        
        hlayout.addWidget(group_box)
        hlayout.addWidget(user_console)
        hlayout.addStretch()
        
        self.console_tabs_chm_widget = QWidget()
        self.console_tabs_chm_widget.setLayout(hlayout)
        self.console_tabs.addTab(self.console_tabs_chm_widget, _("Console"))
        ###
        self.main_layout.addWidget(self.console_tabs)
        return
    
    def handleTodo(self):
        self.todo_tabs = QTabWidget()
        self.todo_tabs.setStyleSheet(_(genv.css_tabs))
        self.todo_tabs.hide()
        
        self.todo_tabs_chm_widget = QWidget()
        self.todo_tabs.addTab(self.todo_tabs_chm_widget, _("Todo"))
        ###
        self.main_layout.addWidget(self.todo_tabs)
        return
    
    def handleSetup(self):
        self.setup_tabs = ApplicationTabWidget([
            _("Setup Project"),
            _("Setup Editor")])
        self.setup_project  = ApplicationProjectPage(self, self.setup_tabs.getTab(0), "setup")
        self.setup_editors  = ApplicationEditorsPage(self, self.setup_tabs.getTab(1), "setup")
        ###
        self.main_layout.addWidget(self.setup_tabs)
        return
    
    def handleCertSSL(self):
        self.certssl_tabs = ApplicationTabWidget([
            _("SSL Cert Project"),
            _("SSL Cert Editor")])
        
        font = QFont("Arial", 10)
        
        hlayout = QHBoxLayout()
        vlayout = QVBoxLayout()
        
        self.tree_widget = QTreeWidget()
        self.tree_widget.setColumnCount(6)
        self.tree_widget.setHeaderLabels(["Name", "CA-Name", "Owner", "Start Valid.", "End Valid.", "Status"])
        
        root = QTreeWidgetItem(self.tree_widget)
        root.setText(0, "root CA")
        root.setText(1, "Super Root CA")
        root.setText(2, "The CA Root Owner")
        root.setText(3, "01.01.2000")
        root.setText(4, "31.12.2000")
        root.setText(5, "S")
        
        child1 = QTreeWidgetItem(root)
        child1.setText(0,"Child1")
        child1.setText(1,"beschre bbb")
        
        root_delegate = ColorComboBoxDelegateTree(self.tree_widget)
        self.tree_widget.setItemDelegateForColumn(5, root_delegate)
        
        self.cert_tab = QTabWidget()
        tab1 = QWidget()
        tab1_layout = QVBoxLayout()
        
        tab1_scroll_area = QScrollArea(tab1)
        tab1_scroll_area.setWidgetResizable(True)
        tab1_content_widget = QWidget()
        tab1_content_layout = QVBoxLayout()
        
        tab1_content_widget.setLayout(tab1_content_layout)
        tab1_scroll_area   .setWidget(tab1_content_widget)
        
        tab1_hlayout_1 = QHBoxLayout()
        tab1_label_1 = QLabel(_("Display Name:"))
        tab1_label_1.setMinimumWidth(120)
        tab1_label_1.setFont(font)
        #
        tab1_edit = QLineEdit()
        tab1_edit.setFont(font)
        
        tab1_hlayout_2 = QHBoxLayout()
        #
        tab1_label_2   = QLabel(_("Usage:"))
        tab1_label_2.setMinimumWidth(120)
        tab1_label_2.setFont(font)
        #
        tab1_combo = QComboBox()
        tab1_combo.setFont(font)
        tab1_combo.addItem(_("Personel"))
        tab1_combo.addItem(_("Web Hosting"))
        
        tab1_hlayout_1.addWidget(tab1_label_1)
        tab1_hlayout_1.addWidget(tab1_edit)
        tab1_hlayout_1.addStretch()
        #
        tab1_hlayout_2.addWidget(tab1_label_2)
        tab1_hlayout_2.addWidget(tab1_combo)
        tab1_hlayout_2.addStretch()
        
        tab1_button_layout = QHBoxLayout()
        
        tab1_button_cert_new = QPushButton(_("Create Cert"))
        tab1_button_cert_add = QPushButton(_("Append Cert"))
        tab1_button_cert_del = QPushButton(_("Delete Cert"))
        
        tab1_button_cert_new.clicked.connect(self.on_click_cert_new)
        tab1_button_cert_add.clicked.connect(self.on_click_cert_add)
        tab1_button_cert_del.clicked.connect(self.on_click_cert_del)
        
        tab1_button_cert_new.setMinimumHeight(32)
        tab1_button_cert_add.setMinimumHeight(32)
        tab1_button_cert_del.setMinimumHeight(32)
        
        tab1_button_cert_new.setMinimumWidth(180)
        tab1_button_cert_add.setMinimumWidth(180)
        tab1_button_cert_del.setMinimumWidth(180)
        
        tab1_button_layout.addWidget(tab1_button_cert_new)
        tab1_button_layout.addWidget(tab1_button_cert_add)
        tab1_button_layout.addWidget(tab1_button_cert_del)
        tab1_button_layout.addStretch()
        
        tab1_content_layout.addLayout(tab1_hlayout_1)
        tab1_content_layout.addLayout(tab1_hlayout_2)
        tab1_content_layout.addLayout(tab1_button_layout)
        tab1_content_layout.addStretch()
        #
        tab1_layout.addWidget(tab1_scroll_area)
        tab1.setLayout(tab1_layout)
        
        #
        tab2 = QWidget()
        tab2_layout = QVBoxLayout()
        
        tab2_scroll_area = QScrollArea(tab1)
        tab2_scroll_area.setWidgetResizable(True)
        #
        tab2_content_widget = QWidget()
        tab2_content_layout = QVBoxLayout()
        
        #
        linedits = [
            [ _("CA Name"),                 "trashserver.net"          ],      # 0
            [ _("Organization Name"),       "Internet Widgits Pty Ltd" ],      # 1
            [ _("Unit Name"),               "IT"                       ],      # 2
            [ _("Localy Name"),             "Landshut"                 ],      # 3
            [ _("State or Province"),       "BY"                       ],      # 4
            [ _("Country (2 letter code)"), "DE"                       ],      # 5
            [ _("E-Mail"),                  "ssl@master@domain.com"    ],      # 6
            [ _("Valide Date"),             1                          ],      # 7
            [ _("CA key File"),             "ca-key.pem"               ],      # 8
            [ _("CA csr File"),             "ca-csr.pem"               ],      # 9
            [ _("Password"),                "xyz"                      ],      # 10
            [ _("Chiper Bits"),             1                          ]       # 11
        ]
        #
        v_layout = QVBoxLayout()
        #
        i = -1
        for linedit in linedits:
            i = i + 1
            h_layout = QHBoxLayout()
            h_label  = QLabel(linedit[0])
            h_label.setFont(font)
            h_label.setMinimumWidth(180)
            if i == 7:
                h_labl_beg = QLabel(_("Begin: "))
                h_labl_beg.setFont(font)
                #
                h_edit_beg = QDateEdit()
                h_edit_beg.setCalendarPopup(True)
                h_edit_beg.setDate(QDate.currentDate())
                h_edit_beg.setFont(font)
                #
                h_labl_end = QLabel(_(" End: "))
                h_labl_end.setFont(font)
                #
                h_edit_end = QDateEdit()
                h_edit_end.setCalendarPopup(True)
                h_edit_end.setDate(QDate.currentDate())
                h_edit_end.setFont(font)
                #
                h_layout.addWidget(h_label)
                h_layout.addWidget(h_labl_beg)
                h_layout.addWidget(h_edit_beg)
                h_layout.addWidget(h_labl_end)
                h_layout.addWidget(h_edit_end)
                #
                h_layout.addStretch()
            elif i == 8 or i == 9:
                h_push = QPushButton("  -x-  ")
                h_push.setMinimumHeight(26)
                h_push.setMaximumWidth(64)
                h_push.setFont(font)
                #
                h_edit = QLineEdit(linedit[1])
                h_edit.setFont(font)
                #
                h_layout.addWidget(h_label)
                h_layout.addWidget(h_edit)
                h_layout.addWidget(h_push)
            elif i == 11:
                h_combo = QComboBox()
                h_combo.setMinimumWidth(64)
                h_combo.addItem("256")
                h_combo.addItem("512")
                h_combo.addItem("1024")
                h_combo.addItem("2048")
                h_combo.addItem("4096")
                h_combo.setFont(font)
                #
                delegate = ColorComboBoxDelegate(h_combo)
                h_combo.setItemDelegate(delegate)
                #
                h_layout.addWidget(h_label)
                h_layout.addWidget(h_combo)
                h_layout.addStretch()
            else:
                h_edit = QLineEdit(linedit[1])
                h_edit.setFont(font)
                h_layout.addWidget(h_label)
                h_layout.addWidget(h_edit)
            v_layout.addLayout(h_layout)
        
        tab2_content_layout.addLayout(v_layout)
        #
        push_saveca = QPushButton(_("Save CA Data"))
        push_create = QPushButton(_("Create CA"))
        push_delete = QPushButton(_("Delete CA"))
        push_cleara = QPushButton(_("Clear All"))
        
        push_saveca.clicked.connect(self.on_click_saveca_ca)
        push_create.clicked.connect(self.on_click_create_ca)
        push_delete.clicked.connect(self.on_click_delete_ca)
        push_cleara.clicked.connect(self.on_click_cleara_ca)
        
        push_saveca.setFont(font)
        push_create.setFont(font)
        push_delete.setFont(font)
        push_cleara.setFont(font)
        
        push_saveca.setMinimumHeight(32)
        push_create.setMinimumHeight(32)
        push_delete.setMinimumHeight(32)
        push_cleara.setMinimumHeight(32)
        
        push_saveca.setMinimumWidth(180)
        push_create.setMinimumWidth(180)
        push_delete.setMinimumWidth(180)
        push_cleara.setMinimumWidth(180)
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(push_saveca)
        btn_layout.addWidget(push_create)
        btn_layout.addWidget(push_delete)
        btn_layout.addWidget(push_cleara)
        btn_layout.addStretch()
        
        dummy_layout = QVBoxLayout()
        dummy_widget = QWidget()
        dummy_widget.setMinimumHeight(32)
        dummy_layout.addWidget(dummy_widget)
               
        tab2_content_layout.addLayout(btn_layout)
        tab2_content_layout.addLayout(dummy_layout)
        #
        tab2_content_widget.setLayout(tab2_content_layout)
        tab2_scroll_area   .setWidget(tab2_content_widget)
        
        tab2_layout.addWidget(tab2_scroll_area)
        tab2.setLayout(tab2_layout)
        
        self.cert_tab.addTab(tab1, _("Create SSL"))
        self.cert_tab.addTab(tab2, _("Create CA"))
        
        vlayout.addWidget(self.tree_widget)
        vlayout.addWidget(self.cert_tab)
        #
        hlayout.addLayout(vlayout)
        
        tab = self.certssl_tabs.getTab(0)
        tab.setLayout(hlayout)
        
        #self.certssl_project  = ApplicationProjectPage(self, self.certssl_tabs.getTab(0), "ssl")
        #self.certssl_editors  = ApplicationEditorsPage(self, self.certssl_tabs.getTab(1), "ssl")
        ###
        self.main_layout.addWidget(self.certssl_tabs)
        return
    
    def on_click_cert_new(self):
        DebugPrint("cert new")
    def on_click_cert_add(self):
        DebugPrint("cert add")
    def on_click_cert_del(self):
        DebugPrint("cert del")
    
    def on_click_saveca_ca(self):
        DebugPrint("saveca ca")
    
    def on_click_create_ca(self):
        DebugPrint("create ca")
    
    def on_click_delete_ca(self):
        DebugPrint("delete ca")
    
    def on_click_cleara_ca(self):
        DebugPrint("clear all ca")
    
    def handleGitHub(self):
        self.github_tabs = ApplicationTabWidget([
            _("GitHub Project"),
            _("GitHub Editor")])
        self.github_project  = ApplicationProjectPage(self, self.github_tabs.getTab(0), "github")
        self.github_editors  = ApplicationEditorsPage(self, self.github_tabs.getTab(1), "github")
        ###
        self.main_layout.addWidget(self.github_tabs)
        return
    
    def iis_server_start(self):
        DebugPrint("start iis")
    
    def apache_server_start(self):
        DebugPrint("start apache")
    
    def tomcat_server_start(self):
        DebugPrint("start tomcat")
    
    def iis_server_stop(self):
        DebugPrint("stop iis")
    
    def apache_server_stop(self):
        DebugPrint("stop apache")
    
    def tomcat_server_stop(self):
        DebugPrint("stop tomcat")
    
    def iis_send_clients(self):
        DebugPrint("send to iis clients")
    
    def apache_send_clients(self):
        DebugPrint("send to apache clients")
    
    def tomcat_send_clients(self):
        DebugPrint("send to tomcat clients")
    
    def handleApache(self):
        self.apache_tabs = ApplicationTabWidget([
            _("Web Server Configuration")])
        
        main_layout = QHBoxLayout()
        splitter = QSplitter(Qt.Horizontal)
        
        tree_widget  = QTreeWidget()
        tree_widget.setColumnCount(1)
        tree_widget.setHeaderLabels(["Server"])
        
        root1 = QTreeWidgetItem(tree_widget)
        root1.setText(0, "Root1")
        
        child1 = QTreeWidgetItem(root1)
        child1.setText(0, "Child 1.1")
        
        splitter.addWidget(tree_widget)
        
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        
        tab_widget_1 = QTabWidget()
        
        tab1_1 = QWidget()
        tab2_1 = QWidget()
        tab3_1 = QWidget()
        
        font = QFont("Arial", 10)
        tab_layout  = QHBoxLayout()
        
        tab1_layout = QVBoxLayout()     # iis
        tab2_layout = QVBoxLayout()     # apache 2.4
        tab3_layout = QVBoxLayout()     # tomcat
        
        # iis
        push_layout_iis = QHBoxLayout()
        push_start_iis  = QPushButton(_("Start Server"))
        push_stop_iis   = QPushButton(_("Stop Server"))
        #
        push_start_iis.clicked.connect(self.iis_server_start)
        push_stop_iis .clicked.connect(self.iis_server_stop)
        #
        push_start_iis.setFont(font)
        push_stop_iis .setFont(font)
        #
        push_start_iis.setMinimumHeight(26)
        push_stop_iis .setMinimumHeight(26)
        #
        push_layout_iis.addWidget(push_start_iis)
        push_layout_iis.addWidget(push_stop_iis)
        
        
        # apache 2.4
        push_layout_apache = QHBoxLayout()
        push_start_apache  = QPushButton(_("Start Server"))
        push_stop_apache   = QPushButton(_("Stop Server"))
        #
        push_start_apache.clicked.connect(self.apache_server_start)
        push_stop_apache .clicked.connect(self.apache_server_stop)
        #
        push_start_apache.setFont(font)
        push_stop_apache .setFont(font)
        #
        push_start_apache.setMinimumHeight(26)
        push_stop_apache .setMinimumHeight(26)
        #
        push_layout_apache.addWidget(push_start_apache)
        push_layout_apache.addWidget(push_stop_apache)
        
        
        # tomcat
        push_layout_tomcat = QHBoxLayout()
        push_start_tomcat  = QPushButton(_("Start Server"))
        push_stop_tomcat   = QPushButton(_("Stop Server"))
        #
        push_start_tomcat.clicked.connect(self.tomcat_server_start)
        push_stop_tomcat .clicked.connect(self.tomcat_server_stop)
        #
        push_start_tomcat.setFont(font)
        push_stop_tomcat .setFont(font)
        #
        push_start_tomcat.setMinimumHeight(26)
        push_stop_tomcat .setMinimumHeight(26)
        #
        push_layout_tomcat.addWidget(push_start_tomcat)
        push_layout_tomcat.addWidget(push_stop_tomcat)
        
        
        tab1_layout.addLayout(push_layout_iis)
        tab2_layout.addLayout(push_layout_apache)
        tab3_layout.addLayout(push_layout_tomcat)
        
        
        # iis
        label_layout_iis = QHBoxLayout()
        label_clients_iis = QLabel(_("Client's Connected: 0"))
        label_clients_iis.setFont(font)
        pushr_clients_iis = QPushButton(_("Send Repair Message"))
        pushr_clients_iis.setMinimumHeight(26)
        pushr_clients_iis.setMinimumWidth(210)
        pushr_clients_iis.setFont(font)
        pushr_clients_iis.clicked.connect(self.iis_send_clients)
        
        label_layout_iis.addWidget(label_clients_iis)
        label_layout_iis.addWidget(pushr_clients_iis)
        label_layout_iis.addStretch()
        
        
        # apache 2.4
        label_layout_apache = QHBoxLayout()
        label_clients_apache = QLabel(_("Client's Connected: 0"))
        label_clients_apache.setFont(font)
        pushr_clients_apache = QPushButton(_("Send Repair Message"))
        pushr_clients_apache.setMinimumHeight(26)
        pushr_clients_apache.setMinimumWidth(210)
        pushr_clients_apache.setFont(font)
        pushr_clients_apache.clicked.connect(self.apache_send_clients)
        
        label_layout_apache.addWidget(label_clients_apache)
        label_layout_apache.addWidget(pushr_clients_apache)
        label_layout_apache.addStretch()
        
        
        # tomcat
        label_layout_tomcat = QHBoxLayout()
        label_clients_tomcat = QLabel(_("Client's Connected: 0"))
        label_clients_tomcat.setFont(font)
        pushr_clients_tomcat = QPushButton(_("Send Repair Message"))
        pushr_clients_tomcat.setMinimumHeight(26)
        pushr_clients_tomcat.setMinimumWidth(210)
        pushr_clients_tomcat.setFont(font)
        pushr_clients_tomcat.clicked.connect(self.tomcat_send_clients)
        
        label_layout_tomcat.addWidget(label_clients_tomcat)
        label_layout_tomcat.addWidget(pushr_clients_tomcat)
        label_layout_tomcat.addStretch()
        
        
        tab1_1.setLayout(tab1_layout)
        tab2_1.setLayout(tab2_layout)
        tab3_1.setLayout(tab3_layout)
        
        tab_widget_1.addTab(tab1_1, "IIS")
        tab_widget_1.addTab(tab2_1, "Apache 2")
        tab_widget_1.addTab(tab3_1, "Tomcat")
        
        tab_layout.addWidget(tab_widget_1)
        
        right_layout.addLayout(tab_layout)
        right_widget.setLayout(right_layout)
        
        splitter.addWidget(right_widget)
        splitter.setSizes([200, 600])
        
        main_layout.addWidget(splitter)
        
        
        help_widget = QListWidget()
        help_widget.setMaximumWidth(180)
        
        items = ["Element 1", "Element 2", "Element 3", "Element 4", "Element 5"]
        for item in items:
            QListWidgetItem(item, help_widget)
        
        # microsoft internet information server
        icon_list_iis = QListWidget()
        icon_list_iis.setViewMode(QListWidget.IconMode)
        icon_list_iis.setIconSize(QSize(32, 32))
        
        icon_items_iis = [
            [_("Connection"),      genv.v__app__img__int__ + "/earth.ico"],
            [_("SSL Certs"),       genv.v__app__img__int__ + "/certmgr.ico"],
            [_("Network Adapter"), genv.v__app__img__int__ + "/nic.ico"]
        ]
        strings_iss = [_("Connection"), _("SSL Certs"), _("Network Adapter")]
        max_length_iss = max(len(s)+3 for s in strings_iss)
        padded_strings_iis = [s.center(max_length_iss) for s in strings_iss]
        i = 0
        for s in padded_strings_iis:
            DebugPrint(s)
            icon_items_iis[i][0] = s
            i = i + 1
        for item_text, item_icon in icon_items_iis:
            icon = QListWidgetItem(QIcon(item_icon), item_text)
            icon.setSizeHint(QSize(120, 64))
            icon_list_iis.addItem(icon)
        
        tab1_layout.addWidget(icon_list_iis)
        tab1_layout.addLayout(label_layout_iis)
        
        
        # apache 2.4
        icon_list_apache = QListWidget()
        icon_list_apache.setViewMode(QListWidget.IconMode)
        icon_list_apache.setIconSize(QSize(32, 32))
        
        icon_items_apache = [
            [_("Connection"),      genv.v__app__img__int__ + "/earth.ico"],
            [_("SSL Certs"),       genv.v__app__img__int__ + "/certmgr.ico"],
            [_("Network Adapter"), genv.v__app__img__int__ + "/nic.ico"]
        ]
        strings_apache = [_("Connection"), _("SSL Certs"), _("Network Adapter")]
        max_length_apache = max(len(s)+3 for s in strings_apache)
        padded_strings_apache = [s.center(max_length_apache) for s in strings_apache]
        i = 0
        for s in padded_strings_apache:
            DebugPrint(s)
            icon_items_apache[i][0] = s
            i = i + 1
        for item_text, item_icon in icon_items_apache:
            icon = QListWidgetItem(QIcon(item_icon), item_text)
            icon.setSizeHint(QSize(120, 64))
            icon_list_apache.addItem(icon)
        
        tab2_layout.addWidget(icon_list_apache)
        tab2_layout.addLayout(label_layout_apache)
        
        
        # tomcat
        icon_list_tomcat = QListWidget()
        icon_list_tomcat.setViewMode(QListWidget.IconMode)
        icon_list_tomcat.setIconSize(QSize(32, 32))
        
        icon_items_tomcat = [
            [_("Connection"),      genv.v__app__img__int__ + "/earth.ico"],
            [_("SSL Certs"),       genv.v__app__img__int__ + "/certmgr.ico"],
            [_("Network Adapter"), genv.v__app__img__int__ + "/nic.ico"]
        ]
        strings_tomcat = [_("Connection"), _("SSL Certs"), _("Network Adapter")]
        max_length_tomcat = max(len(s)+3 for s in strings_tomcat)
        padded_strings_tomcat = [s.center(max_length_tomcat) for s in strings_tomcat]
        i = 0
        for s in padded_strings_tomcat:
            icon_items_tomcat[i][0] = s
            i = i + 1
        for item_text, item_icon in icon_items_tomcat:
            icon = QListWidgetItem(QIcon(item_icon), item_text)
            icon.setSizeHint(QSize(120, 64))
            icon_list_tomcat.addItem(icon)
        
        tab3_layout.addWidget(icon_list_tomcat)
        tab3_layout.addLayout(label_layout_tomcat)
        
        
        main_layout.addWidget(help_widget)
        
        tab = self.apache_tabs.getTab(0)
        tab.setLayout(main_layout)
        
        ###
        self.main_layout.addWidget(self.apache_tabs)
        return
    
    def handleMySQL(self):
        self.mysql_tabs = ApplicationTabWidget([
            _("MySQL Project"),
            _("MySQL Editor")])
        self.mysql_project  = ApplicationProjectPage(self, self.mysql_tabs.getTab(0), "mysql")
        self.mysql_editors  = ApplicationEditorsPage(self, self.mysql_tabs.getTab(1), "mysql")
        ###
        self.main_layout.addWidget(self.mysql_tabs)
        return
    
    def handleSquid(self):
        self.squid_tabs = ApplicationTabWidget([
            _("Squid Project"),
            _("Squid Editor")])
        self.squid_project  = ApplicationProjectPage(self, self.squid_tabs.getTab(0), "squid")
        self.squid_editors  = ApplicationEditorsPage(self, self.squid_tabs.getTab(1), "squid")
        ###
        self.main_layout.addWidget(self.squid_tabs)
        return
    
    def handleSettings(self):
        self.settings_tabs = QTabWidget()
        self.settings_tabs.setStyleSheet(_(genv.css_tabs))
        self.settings_tabs.hide()
        
        self.settings_tabs_chm_widget = QWidget()
        #
        self.settings_tabs.addTab(self.settings_tabs_chm_widget, _("Settings"))
        ###
        self.main_layout.addWidget(self.settings_tabs)
        
        vlay = QVBoxLayout()
        chm_fnt1 = QFont("Arial"   , 10)
        chm_fnt2 = QFont("Consolas", 10)
        
        chm_down = QPushButton("download HTML-Workshop...")
        chm_down.setFont(chm_fnt1)
        chm_down.setMinimumHeight(32)
        chm_down.clicked.connect(self.downloadCHMTool)
        
        chm_edit = QLineEdit()
        chm_edit.setFont(chm_fnt2)
        chm_edit.setMinimumHeight(32)
        
        chm_seld = QPushButton("Select Directory")
        chm_seld.setFont(chm_fnt1)
        chm_seld.setMinimumHeight(32)
        
        vlay.addWidget(chm_down)
        vlay.addWidget(chm_edit)
        vlay.addWidget(chm_seld)
        vlay.addStretch()
        
        self.settings_tabs_chm_widget.setLayout(vlay)
    
    def load_mo_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, _("Open .mo file"), '', 'MO Files (*.mo)')
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
        DebugPrint(el)
    
    def handleLocalesProject(self):
        edit_css = _("edit_css")
        
        font = QFont(genv.v__app__font, 10)
        self.locale_tabs_project_widget.setFont(font)
        
        vlayout0 = QVBoxLayout()
        templateLabel = QLabel("Templates:")
        templateLabel.setFont(font)
        
        push1 = MyPushButton(self, "Create", 1, None)
        push2 = MyPushButton(self, "Open"  , 2, None)
        push3 = MyPushButton(self, "Repro" , 3, None)
        push4 = MyPushButton(self, "Build" , 4, None)
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
        edit1.setObjectName("doxygen_project_name")
        edit1.setFont(font2)
        edit1.setStyleSheet(edit_css)
        edit1.setPlaceholderText(_("Example Project"))
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
        self.drives_treeLocales.setHeaderLabels([_("Drive"), _("Available Space"), _("Total Size")])
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
                            DebugPrint("file: " + file_name + " is packed.")
                        else:
                            DebugPrint("file: " + file_name + " is not packed.")
                        file.close()
                    #DebugPrint(self.localeliste[0][0].text())
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
        DebugPrint(filepath)
        return
    def openexLocales(self, filepath):
        DebugPrint(filepath)
        return
    def renameLocales(self, filepath):
        DebugPrint(filepath)
        return
    def tempelLocales(self, filepath):
        DebugPrint(filepath)
        return
    
    def openFile(self, file_path):
        DebugPrint(f"Opening file: {file_path}")
        # Hier können Sie den Code hinzufügen, um die Datei zu öffnen
    
    def deleteFile(self, file_path):
        DebugPrint(f"Deleting file: {file_path}")
        # Hier können Sie den Code hinzufügen, um die Datei zu löschen
    
    
    def btnOpenLocales_clicked(self):
        DebugPrint("open locales")
        return
    
    def btnSaveLocales_clicked(self):
        DebugPrint("save locales")
        return
    
    # commodore c64
    def onC64TabChanged(self, index):
        if index == 0 or index == 1 or index == 3:
            DebugPrint("end")
            if not genv.worker_thread == None:
                genv.worker_thread.stop()
            self.worker_hasFocus = False
        elif index == 2:
            DebugPrint("start")
            if not genv.worker_thread == None:
                genv.worker_thread.stop()
            genv.worker_thread = None
            genv.worker_thread = c64WorkerThread(self)
            genv.worker_thread.start()
            self.worker_hasFocus = True
    
    def handleCommodoreC64(self):
        self.c64_tabs = QTabWidget()
        self.c64_tabs.setStyleSheet(_(genv.css_tabs))
        self.c64_tabs.hide()
        
        
        self.c64_tabs_project_widget = QWidget()
        self.c64_tabs_basic___widget = QWidget()
        self.c64_tabs_editors_widget = QWidget()
        self.c64_tabs_designs_widget = QWidget()
        #
        self.c64_tabs.addTab(self.c64_tabs_project_widget, _("C-64 Project"))
        self.c64_tabs.addTab(self.c64_tabs_basic___widget, _("C-64 Editor"))
        self.c64_tabs.addTab(self.c64_tabs_editors_widget, _("C-64 Editor (Sceen)"))
        self.c64_tabs.addTab(self.c64_tabs_designs_widget, _("C-64 Designer"))
        ####
        self.c64_project = ApplicationProjectPage(self, self.c64_tabs_project_widget, "c64")
        self.c64_editors = ApplicationEditorsPage(self, self.c64_tabs_basic___widget, "c64")
        ####
        
        #self.c64_tabs_editors_widget.setMinimumWidth(1050)
        
        
        
        clayout = QVBoxLayout()
        hlayout = QHBoxLayout()
        #
        self.c64_screen = c64Bildschirm()
        #
        
        hpLayout = QHBoxLayout()
        #
        apps = QPushButton(_("Applications"))
        game = QPushButton(_("Games"))
        #
        apps.setMinimumHeight(32)
        game.setMinimumHeight(32)
        #
        hpLayout.addWidget(apps)
        hpLayout.addWidget(game)
        #
        vlayout = QVBoxLayout()
        listbox = QListWidget()
        #
        listbox.setViewMode  (QListView.IconMode)
        listbox.setResizeMode(QListView.Adjust)
        listbox.setStyleSheet("background-color:white;")
        listbox.setMaximumHeight(300)
        #
        dhLayout = QHBoxLayout()
        
        c64_disc1_label  = QLabel()
        c64_disc1_pixmap = QPixmap(genv.v__app__discc64__)
        c64_disc1_label.setPixmap(c64_disc1_pixmap)
        c64_disc1_label.setMaximumHeight(100)
        #
        c64_disc2_label  = QLabel()
        c64_disc2_pixmap = QPixmap(genv.v__app__discc64__)
        c64_disc2_label.setPixmap(c64_disc2_pixmap)
        c64_disc2_label.setMaximumHeight(100)
        #
        c64_mc1_label  = QLabel()
        c64_mc1_pixmap = QPixmap(genv.v__app__datmc64__)
        c64_mc1_label.setPixmap(c64_mc1_pixmap)
        c64_mc1_label.setMaximumHeight(100)
        #
        dhLayout.addWidget(c64_disc1_label)
        dhLayout.addWidget(c64_disc2_label)
        dhLayout.addWidget(c64_mc1_label)
        
        vlayout.addLayout(hpLayout)
        vlayout.addWidget(listbox)
        vlayout.addLayout(dhLayout)
        
        hlayout.addWidget(self.c64_screen)
        hlayout.addLayout(vlayout)
        
        self.c64_keyboard = C64Keyboard()
        self.c64_keyboard.graphics_view.scale(1/1.2, 1/1.2)
        
        clayout.addLayout(hlayout)
        clayout.addWidget(self.c64_keyboard)
        
        self.c64_tabs_editors_widget.setLayout(clayout)
        self.c64_tabs.currentChanged.connect(self.onC64TabChanged)
        
        ####
        self.main_layout.addWidget(self.c64_tabs)
    
    def closeEvent(self, event):
        msg = QMessageBox()
        msg.setWindowTitle(_("Confirmation"))
        msg.setText(_("Would you close the Application?"))
        msg.setIcon(QMessageBox.Question)
        
        btn_yes = msg.addButton(QMessageBox.Yes)
        btn_no  = msg.addButton(QMessageBox.No)
        
        msg.setStyleSheet(_("msgbox_css"))
        result = msg.exec_()
        
        if result == QMessageBox.Yes:
            if not genv.worker_thread == None:
                genv.worker_thread.stop()
            event.accept()
        else:
            event.ignore()
    
    # ------------------------------------------------------------------------
    # class member to get the widget item from list_widget_1 or list_widget_2.
    # The application script will stop, if an internal error occur ...
    # ------------------------------------------------------------------------
    def handle_item_click_1(self, item):
        tab_index = genv.list_widget_1.row(item)
        scrollers = [
            genv.scrollview_1, genv.scrollview_2,
            genv.scrollview_3, genv.scrollview_4
        ]
        
        for page in scrollers:
            page.hide()
        
        scrollers[tab_index].show()
    
    def handle_item_click_2(self, item):
        tab_index = genv.list_widget_2.row(item)
        for page in genv.scrollers:
            page.hide()
        genv.scrollers[tab_index].show()
    
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
            self.tab0_fold_edit1.setText(self.tab0_fold_userd)
        else:
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
            DebugPrint(f"File {filePath} exists.")
            # weitere Aktionen durchführen, wenn die Datei existiert
        else:
            DebugPrint(f"File {filePath} not found.")
            # ktionen durchführen, wenn die Datei nicht existiert
    
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_press_pos = event.globalPos()
            self.mouse_move_pos = event.globalPos() - self.frameGeometry().topLeft()
            self.resizing = self.getCursorPosition(event.pos())
    
    def mouseMoveEvent(self, event):
        try:
            if event.buttons() == Qt.LeftButton:
                if self.resizing:
                    self.resizeWindow(event.globalPos())
                else:
                    self.move(event.globalPos() - self.mouse_move_pos)
            else:
                self.updateCursor(event.pos())
        except Exception as e:
            pass
    
    def mouseReleaseEvent(self, event):
        self.resizing = None
    
    def updateCursor(self, pos):
        cursor_pos = self.getCursorPosition(pos)
        if cursor_pos:
            self.setCursor(cursor_pos)
        else:
            self.setCursor(Qt.ArrowCursor)
    
    def getCursorPosition(self, pos):
        rect = self.rect()
        margin = 10
        
        if pos.x() < margin and pos.y() < margin:
            return Qt.SizeFDiagCursor
        elif pos.x() > rect.width() - margin and pos.y() > rect.height() - margin:
            return Qt.SizeFDiagCursor
        elif pos.x() > rect.width() - margin and pos.y() < margin:
            return Qt.SizeBDiagCursor
        elif pos.x() < margin and pos.y() > rect.height() - margin:
            return Qt.SizeBDiagCursor
        elif pos.x() < margin:
            return Qt.SizeHorCursor
        elif pos.x() > rect.width() - margin:
            return Qt.SizeHorCursor
        elif pos.y() < margin:
            return Qt.SizeVerCursor
        elif pos.y() > rect.height() - margin:
            return Qt.SizeVerCursor
        else:
            return None
    
    def resizeWindow(self, global_pos):
        rect = self.frameGeometry()
        diff = global_pos - self.mouse_press_pos
        self.mouse_press_pos = global_pos
        
        if self.resizing == Qt.SizeFDiagCursor:
            rect.setTopLeft(rect.topLeft() + diff)
        elif self.resizing == Qt.SizeBDiagCursor:
            rect.setBottomRight(rect.bottomRight() + diff)
        elif self.resizing == Qt.SizeHorCursor:
            if self.mouse_press_pos.x() < rect.center().x():
                rect.setLeft(rect.left() + diff.x())
            else:
                rect.setRight(rect.right() + diff.x())
        elif self.resizing == Qt.SizeVerCursor:
            if self.mouse_press_pos.y() < rect.center().y():
                rect.setTop(rect.top() + diff.y())
            else:
                rect.setBottom(rect.bottom() + diff.y())
        self.setGeometry(rect)
    
    def toggleMaximizeRestore(self):
        if self.is_maximized:
            self.setGeometry(self.normal_geometry)
            self.is_maximized = False
        else:
            self.normal_geometry = self.geometry()
            self.setGeometry(QApplication.desktop().availableGeometry(self))
            self.is_maximized = True
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 0, 0))
        
        # Use the standard background color from the widget's palette
        standard_background_color = self.palette().color(QPalette.Window)
        adjusted_rect = self.rect().adjusted(10, 10, -10, -10)
        painter.fillRect(adjusted_rect, standard_background_color)
        
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QColor(255, 0, 0))
        painter.drawRect(10, 10, self.width() - 1, self.height() - 1)

# ------------------------------------------------------------------------
# inform the user about the rules/license of this application script ...
# ------------------------------------------------------------------------
class licenseWindow(QDialog):
    def __init__(self, parent=None):
        super(licenseWindow, self).__init__(parent)
        
        self.returnCode = 0
        
        self.setWindowTitle("LICENSE - Please read, before you start.")
        self.setWindowIcon(QIcon(genv.v__app__img__int__ + "/winico.png"))
        self.setMinimumWidth(600)
        
        font = QFont("Arial", 10)
        self.setFont(font)
        
        layout = QVBoxLayout()
        
        button1 = QPushButton(_("Accept"))
        button2 = QPushButton(_("Decline"))
        
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
        textfield.setPlainText(_("LICENSE"))
    
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
    DebugPrint("Thank's for using.")
    return

#class CustomWebEnginePage(QWebEnginePage):
#    def __init__(self, parent=None):
#        super().__init__(parent)
#        self.parent_view = None
#
#    def set_parent_view(self, parent_view):
#        self.parent_view = parent_view
#
#    def acceptNavigationRequest(self, url, _type, isMainFrame):
#        if _type == QWebEnginePage.NavigationTypeLinkClicked:
#            if self.parent_view:
#                # Link-Klick abfangen und an die zweite WebView weitergeben
#                self.parent_view.setUrl(url)
#                return False
#        return super().acceptNavigationRequest(url, _type, isMainFrame)

# ------------------------------------------------------------------------
# chm help window ...
# ------------------------------------------------------------------------
class HelpWindow(QMainWindow):
    def __init__(self, parent=None, file="index.html"):
        
        #genv.saved_style = genv.window_login.styleSheet()
        #genv.window_login.setStyleSheet("")
        
        super(HelpWindow, self).__init__(parent)
        
        self.file = QUrl(file)
        
        # Splitter erstellen
        splitter = QSplitter(Qt.Horizontal)
        
        self.hide()
        self.setContentsMargins(0,0,0,0)
        self.setStyleSheet("background-color:gray;")
        self.setWindowTitle(_("Help Dialog"))
        self.setGeometry(100, 100, 700, 600)
        
        # Hauptlayout des Dialogs
        layout = QVBoxLayout()
        layout.setContentsMargins(1,0,0,1)
        
        # Navigation Panel erstellen
        navigation_container = QVBoxLayout()
        navigation_widget = QWidget()
        navigation_layout = QHBoxLayout()
        #
        navigation_widget.setMaximumHeight(56)
        navigation_widget.setContentsMargins(1,1,1,1)
        
        # Buttons: Home, Prev, Next
        self.home_button = QPushButton(_("Home"))
        self.prev_button = QPushButton(_("Prev"))
        self.next_button = QPushButton(_("Next"))
        
        self.home_button.setMinimumHeight(40)
        self.prev_button.setMinimumHeight(40)
        self.next_button.setMinimumHeight(40)
        
        self.home_button.setCursor(Qt.PointingHandCursor)
        self.prev_button.setCursor(Qt.PointingHandCursor)
        self.next_button.setCursor(Qt.PointingHandCursor)
        
        font = QFont("Arial", 12)
        #
        self.home_button.setFont(font)
        self.prev_button.setFont(font)
        self.next_button.setFont(font)
        
        self.home_button.clicked.connect(self.home_click)
        self.prev_button.clicked.connect(self.prev_click)
        self.next_button.clicked.connect(self.next_click)
        
        navigation_widget.setStyleSheet("background-color:lightgray;")
        navigation_layout.setAlignment(Qt.AlignTop)
        
        # Buttons dem Layout hinzufügen
        navigation_layout.addWidget(self.home_button)
        navigation_layout.addWidget(self.prev_button)
        navigation_layout.addWidget(self.next_button)
        
        # Setze das Layout für das Navigations-Widget
        navigation_widget.setLayout(navigation_layout)
        
        # Erstes Widget
        widget1 = QWidget()
        #widget1.setContentsMargins(0,0,0,0)
        
        layout1 = QVBoxLayout()
        #layout1.setContentsMargins(0,0,0,0)
        
        self.browser = QWebEngineView()
        #self.browser.setContentsMargins(0,0,0,0)
        #self.browser.setStyleSheet("background-color: black;")
        
        layout1.addWidget(self.browser)
        widget1.setLayout(layout1)
        
        self.browser.load(self.file)
        
        # Zweites Widget
        #widget2 = QWidget()
        #widget2.setContentsMargins(0,0,0,0)
        
        #layout2 = QVBoxLayout()
        #layout2.setContentsMargins(1,0,0,1)
        
        #layout2.addWidget(self.browser)
        #layout2.setContentsMargins(0,0,0,0)
        #widget2.setLayout(layout2)
        
        # Widgets zum Splitter hinzufügen
        #splitter.addWidget(widget1)
        #splitter.addWidget(widget2)
        
        layout.addWidget(navigation_widget)
        layout.addWidget(widget1)
        
        # Schließen-Button
        button_widget = QWidget()
        button_layout = QHBoxLayout()
        
        button_widget.setMaximumHeight(84)
        
        # PNG-Grafik
        image_label = QLabel()
        image_label.setMinimumHeight(64)
        image_label.setMaximumHeight(64)
        image_label.setMaximumWidth (64)
        
        image_label.setStyleSheet("""
        background-color: orange;
        background-image: url('./_internal/img/py.png');
        background-repeat: no-repeat;
        border: 1px solid red;
        """)
        
        # Text "Made with Python"
        text_label = QLabel(_("Made with Python\n(c) 2024 by paule32"))
        text_label.setStyleSheet("""
        background-color: navy;
        border: 1px solid red;
        font-size: 14px;
        font-weight: bold;
        color: yellow;
        """)
        
        # Zum Button-Layout hinzufügen
        button_layout.addWidget(image_label)
        button_layout.addWidget(text_label)
        button_layout.setAlignment(Qt.AlignVCenter)
        
        button_widget.setLayout(button_layout)
        layout.addWidget(button_widget)
        
        #if not genv.window_login == None:
        #genv.window_login.setStyleSheet(genv.saved_style)
        
        container = QWidget()
        container.setContentsMargins(0,0,0,0)
        container.setLayout(layout)
        
        self.setCentralWidget(container)
        self.show()
    
    def home_click(self):
        pass
    
    def next_click(self):
        pass
    
    def prev_click(self):
        pass
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
    
    def closeEvent(self, event):
        #if not genv.window_login == None:
        #    genv.window_login.setStyleSheet(genv.saved_style)
        if not self.browser == None:
            self.browser.deleteLater()
        event.accept()
    
    def on_close(self):
        self.close()
    
    def paintEvent(self, event):
        # Zeichnet einen Rahmen um das Hauptfenster
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(Qt.green)  # Grün
        pen.setWidth(5)  # Rahmenbreite
        painter.setPen(pen)

        # Rechteck für den Rahmen definieren
        rect = self.rect()
        rect = rect.adjusted(2, 2, -2, -2)  # Den Rahmen leicht nach innen verschieben
        painter.drawRect(rect)

class CustomWindow(QWidget):
    def __init__(self, parent=None):
        super(CustomWindow, self).__init__(parent)
        self._start_pos = None  # Startposition für das Ziehen
        self.parent = parent
        
        self.embedded_label      = None  # Platzhalter für das eingebettete Label
        self.close_button_coords = None  # Koordinaten des Close-Buttons

        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)  # Entfernt die Standardfensterdekoration
        self.setStyleSheet("border: 1px solid black; background-color: rgb(236, 233, 216);")

        # Titelleiste erstellen
        self.title_bar = QWidget(self)
        self.title_bar.setStyleSheet("background-color: rgb(0, 120, 215);")
        self.title_bar.setFixedHeight(30)

        # Titeltext hinzufügen
        title_label = QLabel("A Window", self.title_bar)
        title_label.setStyleSheet("color: white; font-family: Tahoma; font-size: 14px;")
        title_label.setAlignment(Qt.AlignCenter)

        # Layout für Titelleiste
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.addWidget(title_label)
        title_layout.setContentsMargins(0, 0, 0, 0)

        # Hauptinhalt
        content = QLabel("Hauptinhalt des Fensters")
        content.setStyleSheet("background-color: rgb(236, 233, 216); padding: 10px;")
        content.setAlignment(Qt.AlignCenter)

        # Eingebettetes Label erstellen
        self.embedded_label = QLabel("Eingebettetes Label", self)
        self.embedded_label.setGeometry(50, 50, 200, 50)
        self.embedded_label.setStyleSheet("background-color: rgba(255, 255, 255, 0.8); border: 1px solid black;")
        self.embedded_label.setAlignment(Qt.AlignCenter)

        # Gesamt-Layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.title_bar)
        main_layout.addWidget(content)
        main_layout.setContentsMargins(0, 0, 0, 0)

    def mousePressEvent(self, event):
        """Ermöglicht das Starten einer Verschiebung beim Klicken auf die Titelleiste."""
        if event.button() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            self._start_pos = event.globalPos() - self.frameGeometry().topLeft()
            
            # Setze das eingebettete Label in den Vordergrund
            if self.embedded_label:
                self.embedded_label.raise_()
            
            event.accept()

    def mouseMoveEvent(self, event):
        """Ermöglicht das Verschieben des Fensters."""
        if self._start_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._start_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Beendet die Verschiebung."""
        if event.button() == Qt.LeftButton:
            self._start_pos = None
            event.accept()

class InteractiveWindow(QLabel):
    def __init__(self, pixmap, parent=None):
        super(InteractiveWindow, self).__init__(parent)
        
        self.setPixmap(pixmap)
        
        self._start_pos = None
        self.parent = parent
        
        self.setStyleSheet("border: 1px solid black;")
        self.setFixedSize(pixmap.size())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start_pos = event.globalPos() - self.frameGeometry().topLeft()
            self.raise_()
            # Widget-Eigenschaften setzen
            update_copy_notice(self.parent)
            event.accept()

    def mouseMoveEvent(self, event):
        if self._start_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._start_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._start_pos = None
            event.accept()

def update_copy_notice(self_ptr):
    genv.copy_overlay_label_1.setParent(self_ptr)
    genv.copy_overlay_label_2.setParent(self_ptr)
    
    genv.copy_overlay_label_1.raise_()
    genv.copy_overlay_label_2.raise_()

def render_widget_to_pixmap(widget):
    """Erstellt eine Pixmap des gegebenen Widgets."""
    widget.setFixedSize(widget.size())  # Stelle sicher, dass die Größe fix ist
    pixmap = QPixmap(widget.size())
    pixmap.fill(widget.palette().color(widget.backgroundRole()))  # Hintergrundfarbe setzen
    painter = QPainter(pixmap)
    widget.render(painter)  # Rendere das Widget in die Pixmap
    painter.end()
    return pixmap
    
class DraggableIconWidget(QWidget):
    def __init__(self, icon_path, title, parent=None):
        super().__init__(parent)
        
        self.parent = parent
        self.resize(130, 140)
        
        # Setze das Widget als fensterlos, damit es frei bewegt werden kann
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        
        # Hauptlayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        # ---------------------------------------
        # QLabel für das Icon
        # ---------------------------------------
        self.icon_label = QLabel(self)
        self.icon_label.setStyleSheet("background-color: rgba(255,0,0, 0.2);")
        
        # ---------------------------------------
        # Netzwerkmanager zum Laden des Bildes
        # ---------------------------------------
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_image_loaded)
        
        url = QUrl(icon_path)
        req = QNetworkRequest(url)
        # ---------------------------------------
        self.network_manager.get(req)
        
        # QLabel für den Titel (Hintergrund)
        self.title_label_bg = QLabel(self)
        self.title_label_bg.setText(title)
        self.title_label_bg.setAlignment(Qt.AlignCenter)

        # QLabel für den Titel (Vordergrund)
        self.title_label_fg = QLabel(self)
        self.title_label_fg.setText(title)
        self.title_label_fg.setAlignment(Qt.AlignCenter)

        # Schriftart für beide Labels
        font = QFont("Arial", 10, QFont.Bold)
        self.title_label_bg.setFont(font)
        self.title_label_fg.setFont(font)

        # Farben und Transparenz für die Labels
        self.title_label_bg.setStyleSheet("background: transparent; color: white;")
        self.title_label_fg.setStyleSheet("background: transparent; color: black;")

        # Widgets zum Layout hinzufügen
        layout.addWidget(self.icon_label)

        # Wrapper für die überlagerten Labels
        title_wrapper = QWidget(self)
        title_wrapper.setFixedHeight(20)  # Höhe für den Titelbereich
        title_wrapper.setAttribute(Qt.WA_TranslucentBackground, True)

        # Positioniere die Labels mittig
        wrapper_width = self.width() - 84
        title_width = wrapper_width

        self.title_label_bg.setParent(title_wrapper)
        self.title_label_fg.setParent(title_wrapper)

        self.title_label_bg.setGeometry(2, 2, title_width, 20)  # Hintergrund leicht versetzt
        self.title_label_fg.setGeometry(0, 0, title_width, 20)  # Vordergrund exakt oben

        layout.addWidget(title_wrapper)

        # Dragging-Initialisierung
        self.dragging = False
        self.offset = QPoint()

        # Feste Begrenzung für den Bereich
        self.bound_width = 1020
        self.bound_height = 758
    
    def on_image_loaded(self, reply):
        if reply.error() == reply.NoError:
            pixmap = QPixmap()
            pixmap.loadFromData(reply.readAll())
            #
            self.icon_label.setPixmap(pixmap)
            self.icon_label.setScaledContents(True)
            
            self.icon_label.setAlignment(Qt.AlignCenter)
            self.icon_label.setScaledContents(True)
            self.icon_label.setFixedSize(100, 100)
        else:
            showError(_("Error:\ncould not load desktop icon image."))
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            QMessageBox.information(self, "Doppelklick", "Das Widget wurde doppelt angeklickt!")
            
            # -----------------------------------
            # Unsichtbares Widget erstellen
            # -----------------------------------
            hidden_window = CustomWindow(self.parent)
            hidden_window.resize(300, 300)
            
            # -----------------------------------
            # Pixmap des Widgets erstellen
            # -----------------------------------
            pixmap = render_widget_to_pixmap(hidden_window)
            
            # -----------------------------------
            # QLabel erstellen und Pixmap setzen
            # -----------------------------------
            movable_window = InteractiveWindow(pixmap, self.parent)
            movable_window.setGeometry(
                100,
                100,
                pixmap.width (),
                pixmap.height())
            movable_window.show()
    
    def resizeEvent(self, event):
        """Sorgt dafür, dass die Titel-Labels bei Größenänderungen mittig bleiben."""
        wrapper_width = self.width() - 28
        self.title_label_bg.setGeometry(2, 2, wrapper_width, 20)
        self.title_label_fg.setGeometry(0, 0, wrapper_width, 20)
        super().resizeEvent(event)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.pos()
    
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            new_pos = event.globalPos() - self.offset
            self.move(self.get_bounded_position(new_pos))
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
    
    def get_bounded_position(self, new_pos):
        """Begrenzt die Position des Widgets auf die festen Grenzen."""
        widget_size = self.size()
        
        bounded_x = max(0, min(new_pos.x(), self.bound_width - widget_size.width()))
        bounded_y = max(0, min(new_pos.y(), self.bound_height - widget_size.height()))
        
        return QPoint(bounded_x, bounded_y)

class CustomDesktop(QLabel):
    def __init__(self, parent=None):
        super(CustomDesktop, self).__init__(parent)
        
        self.setMouseTracking(True)  # Aktiviert Mausverfolgung
        self.start_point   = None
        self.current_point = None
        self.drawing       = False   # Ob momentan gezeichnet wird
        self.alpha_layer   = QColor(0, 0, 0, 50)  # Halbtransparenter Layer
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.start_point   = event.pos()
            self.current_point = event.pos()
            
            self.setParent(self.parent())
            self.lower ()
            self.update()  # Auslöser für Neuzeichnung
    
    def mouseMoveEvent(self, event):
        if self.drawing and event.buttons() == Qt.LeftButton:
            self.current_point = event.pos()
            self.update()  # Auslöser für Neuzeichnung
            self.raise_()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.start_point = None
            self.current_point = None
            self.update()  # Entfernt den Layer
    
    def paintEvent(self, event):
        super(CustomDesktop, self).paintEvent(event)
        if self.drawing and self.start_point and self.current_point:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Zeichne halbtransparenten Layer
            pen = QPen(Qt.red, 2)
            painter.setPen(pen)
            painter.setBrush(self.alpha_layer)
            
            rect = self.get_rect()
            painter.drawRoundedRect(rect, 10, 10)  # Runde Ecken mit Radius 10
    
    def get_rect(self):
        """Berechnet das Rechteck basierend auf Start- und aktuellem Punkt."""
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = self.current_point.x(), self.current_point.y()
        return QRect(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))

class WindowsXPdesktop(QWidget):
    def __init__(self, parent=None):
        super(WindowsXPdesktop, self).__init__(parent)
        self.parent = parent
        self.init_ui()
    
    def init_ui(self):
        self.desktop_widget = QWidget()
        self.taskbar_widget = QWidget()
        
        self.taskbar_widget.setMaximumHeight(42)
        self.desktop_widget.setMinimumHeight(730)
        
        self.desktop_widget.setStyleSheet("background-color:gray;")
        self.taskbar_widget.setStyleSheet("background-color:blue;")

        #self.desktop_bg = QLabel(self.desktop_widget)
        self.desktop_bg = CustomDesktop(self.desktop_widget)
        self.desktop_bg.setMinimumWidth (1020)
        self.desktop_bg.setMaximumWidth (1020)
        self.desktop_bg.setMinimumHeight( 730)
        self.desktop_bg.setMaximumHeight( 730)
        
        file_path = os.getcwd() + "/_internal/bootstrap/xp/assets/images/bg/desktop-800x600.jpg"
        file_path = "file:///"  + file_path.replace('\\', '/')
        
        # Netzwerkmanager zum Laden des Bildes
        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self.on_image_loaded)
        
        url = QUrl(file_path)
        req = QNetworkRequest(url)
        
        self.network_manager.get(req)
        #
        self.parent.content_layout.addWidget(self.desktop_widget)
        self.parent.content_layout.addWidget(self.taskbar_widget)
        #
        #
        icon_1_path  = os.getcwd() + "/_internal/bootstrap/xp/assets/images/icon1.png"
        icon_1_path  = "file:///"  + icon_1_path.replace('\\', '/')
        #
        icon_2_path  = os.getcwd() + "/_internal/bootstrap/xp/assets/images/icon0.png"
        icon_2_path  = "file:///"  + icon_2_path.replace('\\', '/')
        #
        icon_1_title = "Icon A"
        icon_2_title = "Icon B"
        
        icon_1 = DraggableIconWidget(icon_1_path, icon_1_title, self.desktop_bg)
        icon_2 = DraggableIconWidget(icon_2_path, icon_2_title, self.desktop_bg)
        
        icon_1.show()
        icon_2.show()
    
    def on_image_loaded(self, reply):
        if reply.error() == reply.NoError:
            pixmap = QPixmap()
            pixmap.loadFromData(reply.readAll())
            #
            self.desktop_bg.setPixmap(pixmap)
            self.desktop_bg.setScaledContents(True)
            self.addTextLayer()
        else:
            showError(_("Error:\ncould not load desktop background image."))
    
    # Ein Label als oberstes Layer
    def addTextLayer(self):
        copy_text = (""
            + "This is a private build Version\n"
            + "(c) 2025 by paule32")
            
        css_text_1 = (""
            + "background-color: rgba(0,0,0,0);"
            + "color: white;"
            + "font-size: 16px;"
            + "border: 0;")
        css_text_2 = (""
            + "background-color: rgba(0,0,0,0);"
            + "color: black;"
            + "font-size: 16px;"
            + "border: 0;")
            
        title_width = self.width() - 84
        
        genv.copy_overlay_label_1 = QLabel(copy_text)
        genv.copy_overlay_label_2 = QLabel(copy_text)
        
        genv.copy_overlay_label_1.setStyleSheet(css_text_1)
        genv.copy_overlay_label_2.setStyleSheet(css_text_2)
        
        genv.copy_overlay_label_1.setAlignment(Qt.AlignRight)
        genv.copy_overlay_label_2.setAlignment(Qt.AlignRight)
        
        #genv.copy_overlay_label_1.setGeometry(2, 2, title_width, 20)
        #genv.copy_overlay_label_2.setGeometry(0, 0, title_width, 20)
        
        #genv.copy_overlay_label.setFixedSize(230, 50)
        
        # Widget-Eigenschaften setzen
        genv.copy_overlay_label_1.setParent(self.desktop_bg)
        genv.copy_overlay_label_2.setParent(self.desktop_bg)
        
        genv.copy_overlay_label_2.raise_()  # Immer im Vordergrund
        genv.copy_overlay_label_1.raise_()  # Immer im Vordergrund
        
        self.update_overlay_position()
    
    def resizeEvent(self, event):
        """Overlay-Position beim Resizen des Fensters aktualisieren"""
        super().resizeEvent(event)
        self.update_overlay_position()
    
    def update_overlay_position(self):
        """Position des Overlays in der rechten unteren Ecke"""
        #x = self.width () - self.overlay_label.width () - 10  # 10px Abstand vom Rand
        #y = self.height() - self.overlay_label.height() - 10
        #self.overlay_label.move(x, y)
        x = (1020 - 240)
        y = ( 800 - 42 - 84)
        genv.copy_overlay_label_1.move(x,y)
        x += 2
        y += 2
        genv.copy_overlay_label_2.move(x,y)

class Bridge(QObject):
    # Signal, das gesendet wird, wenn ein Element angeklickt wurde
    elementClicked     = pyqtSignal(str)
    inputValueReceived = pyqtSignal(str)
    on_key_up          = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super(Bridge, self).__init__(parent)
        self.last_key = ''
    
    @pyqtSlot(str, str)
    def report_key(self, key, text):
        self.last_key = key
        self.on_key_up.emit(key, text)
    
    @pyqtSlot(str)
    def report_element_id(self, element_id):
        # Signal mit der ID des angeklickten Elements senden
        print(f"Element mit ID '{element_id}' wurde angeklickt.")
        self.elementClicked.emit(element_id)
    
    @pyqtSlot(str)
    def report_input_value(self, value):
        print(f"empfangener Wert: {value}")
        print("last key: " + self.last_key)
        self.inputValueReceived.emit(value)

class ClientSocketWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent, flags=Qt.FramelessWindowHint | Qt.WindowSystemMenuHint)

        self._mouse_press_pos = None
        self._is_dragging = False
        
        self.check_pass = False
        self.current_value = ""
        
        self.setWindowTitle("Remote Desktop")
        self.setStyleSheet("background-color:navyblue;")
        self.resize(1020, 800)

        # --- Titelzeilen-Widget erstellen (als Container für Layout und Styles) ---
        self.title_bar_widget = QWidget()
        self.title_bar_widget.setObjectName("TitleBar")  # Für gezieltes Styling
        self.title_bar_widget.setStyleSheet("background-color:navy;")
        self.title_bar_widget.setMaximumHeight(32)

        # Layout für die Titelzeile erzeugen und ins Widget setzen
        self.title_layout = QHBoxLayout(self.title_bar_widget)
        self.title_layout.setContentsMargins(10, 1, 1, 1)
        self.title_layout.setSpacing(2)

        # Titel-Label
        self.title_label = QLabel("Remote Desktop")
        self.title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        # Buttons
        self.btn_minimize = QPushButton("-")
        self.btn_close    = QPushButton("x")
        
        self.btn_minimize.setFixedSize(26, 26)
        self.btn_close.setFixedSize   (26, 26)
        
        self.btn_minimize.clicked.connect(self.showMinimized)
        self.btn_close.clicked   .connect(self.close)

        # Titelzeilen-Layout zusammenbauen
        self.title_layout.addWidget(self.title_label, 1)
        self.title_layout.addWidget(self.btn_minimize)
        self.title_layout.addWidget(self.btn_close)
        
        # Statusleiste
        #self.statusbar = QWidget()
        #self.statusbar.setMaximumHeight(28)

        # --- Hauptinhalt (zentraler Bereich) ---
        self.content_layout = QVBoxLayout()
        
        file_path = os.getcwd() + "/_internal/bootstrap/xp/index.html"
        file_path = "file:///"  + file_path.replace('\\', '/')
        
        self.browser = QWebEngineView()
        self.browser.setContentsMargins(0,0,0,0)
        self.browser.setStyleSheet("background-color: black;")
        
        try:
            self.channel = QWebChannel()
            self.bridge  = Bridge()
            
            self.bridge.elementClicked    .connect(self.handle_element_click)
            self.bridge.inputValueReceived.connect(self.handle_input_value)
            self.bridge.on_key_up         .connect(self.handle_key_up)
            
            # Verbinde die WebChannel-Schnittstelle mit Python
            self.channel.registerObject("bridge", self.bridge)
            self.browser.page().setWebChannel(self.channel)
            
            # HTML-Seite mit WebChannel-Integration
            self.browser.setUrl(QUrl(file_path))
            
        except Exception as e:
            print(e)
        
        self.scale_factor = 0.84
        self.browser.setZoomFactor(self.scale_factor)
        
        #self.browser.load(QUrl(file_path))
        
        
        self.content_layout.addWidget(self.browser)
        #ontent_layout.addWidget(self.statusbar)

        # --- Gesamtlayout auf QDialog anwenden ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self.title_bar_widget)  # Titelbereich oben
        main_layout.addLayout(self.content_layout)         # Inhalt darunter
        
        self.setLayout(main_layout)

        # --- Stylesheet für navy-blaue Titelleiste mit gelber Schrift und vertieftem Rahmen ---
        self.title_bar_widget.setStyleSheet("""
            QWidget#TitleBar {
                background-color: navy;
                border: 2px inset #555;        /* Vertiefter (inset) 3D-Rahmen */
            }
            QWidget#TitleBar QLabel {
                color: yellow;                 /* Schriftfarbe Label */
                font-size: 14px;
                font-weight: bold;
            }
            QWidget#TitleBar QPushButton {
                color: yellow;                 /* Schriftfarbe Buttons */
                background-color: navy;        /* Gleiche Hintergrundfarbe */
                border: none;
            }
            QWidget#TitleBar QPushButton:hover {
                background-color: #001f5b;     /* Leicht dunkler beim Hover */
            }
        """)
    
    def handle_key_up(self, key, text):
        print("key: " + key + ", value: " + text)
        if self.checkpass():
            pass
    
    def handle_input_value(self, value):
        self.current_value = value
    
    def checkpass(self) -> bool:
        if self.current_value == "test123":
            self.content_layout.removeWidget(self.browser)
            self.browser.deleteLater()
            self.browser = None
            genv.desktop = WindowsXPdesktop(self)
            return True
        else:
            self.current_value = ""
            return False
            
    def handle_element_click(self, element_id):
        print(f"Das angeklickte Element hat die ID: {element_id}")
        if element_id == "userpass_1":
            if self.checkpass() == True:
                pass
            
        elif element_id == "btn_logout":
            self.close()
            return True
        
        elif element_id == "btn_green_1":
            print("login: Blacky Cat")
            if self.checkpass():
                pass
    
    # --- Methoden für Fensterbewegung (Titelbereich) ---
    def mousePressEvent(self, event):
        """ Speichert die Position der Maus beim Drücken für ein Verschieben. """
        if event.button() == Qt.LeftButton:
            # Prüfen, ob in der Titelzeile gedrückt wurde (nicht auf Buttons)
            # => boundingRect des title_bar_widget vs. event.pos()?
            # In diesem einfachen Beispiel nehmen wir an, dass überall verschoben werden kann.
            self._mouse_press_pos = event.globalPos() - self.frameGeometry().topLeft()
            self._is_dragging = True
            event.accept()

    def mouseMoveEvent(self, event):
        """ Verschiebt das Fenster, wenn linke Maustaste gedrückt gehalten wird. """
        if self._is_dragging and event.buttons() & Qt.LeftButton:
            new_pos = event.globalPos() - self._mouse_press_pos
            self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """ Setzt die Variable zurück, wenn die Maus losgelassen wird. """
        if event.button() == Qt.LeftButton:
            self._is_dragging = False
            event.accept()

class ClickableComboBox(QComboBox):
    # Neues Signal definieren
    clicked = pyqtSignal()
    
    def mousePressEvent(self, event):
        # Signal vor dem "normalen" Verhalten auslösen
        self.clicked.emit()
        # Original-Implementierung weiterhin aufrufen,
        # damit das Dropdown korrekt funktioniert
        super().mousePressEvent(event)

class LandingPage(QDialog):
    def __init__(self, parent=None):
        super(LandingPage, self).__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Layout
        layout = QVBoxLayout()
        
        # Buttons
        button1 = QPushButton("Application")
        button1.clicked.connect(self.on_button1_click)
        
        button2 = QPushButton("Windows XP")
        button2.clicked.connect(self.on_button2_click)
        
        # Buttons zum Layout hinzufügen
        layout.addWidget(button1)
        layout.addWidget(button2)
        
        # Layout dem Fenster hinzufügen
        self.setLayout(layout)
        
        # Fenster-Einstellungen
        self.setWindowTitle("Landing Page")
        self.resize(300, 200)

    def on_button1_click(self):
        self.hide()
        if genv.v__app_object == None:
            genv.v__app_object = QApplication(sys.argv)
            
        genv.v__app_win = FileWatcherGUI()
        genv.v__app_win.move(100, 100)
        genv.v__app_win.exec_()
        
        self.exit(0)

    def on_button2_click(self):
        self.hide()
        self.client_window = ClientSocketWindow()
        self.client_window.exec_()
        sys.exit(0)

# ------------------------------------------------------------------------
# this is our "main" entry point, where the application will start.
# ------------------------------------------------------------------------
def EntryPoint(arg1=None):
    atexit.register(ApplicationAtExit)
    
    genv.v__app__comment_hdr  = ("# " + ("-"*78) + "\n")
    
    global conn
    global conn_cursor
    
    error_fail    = False
    error_result  = 0
    
    genv.topic_counter = 1
    
    #if not arg1 == None:
    #    genv.v__app__scriptname__ = arg1
    #    print("--> " + genv.v__app__scriptname__)
    #    if not os.path.exists(genv.v__app__scriptname__):
    #        print("script does not exists !")
    #        error_result = 1
    #        sys.exit(1)
    
    # ---------------------------------------------------------
    # splash screen ...
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
    
    genv.servers_scroll = QScrollArea()
    genv.servers_widget = QWidget()
    genv.servers_layout = QVBoxLayout()
    
    genv.splitter = QSplitter()
    
    # ---------------------------------------------------------
    # doxygen.exe directory path ...
    # ---------------------------------------------------------
    if not genv.doxy_env in os.environ:
        if genv.v__app__debug == True:
            os.environ["DOXYGEN_PATH"] = "E:/doxygen/bin"
        else:
            try:
                DebugPrint(genv.v__app__config.get("doxygen","path"))
            except Exception as e:
                # -------------------------------
                # close tje splash screen ...
                # -------------------------------
                time.sleep(1)
                if getattr(sys, 'frozen', False):
                    pyi_splash.close()
                    
                win32api.MessageBox(0,(""
                + "Error: no section: 'doxygen' or option: 'path'\n"
                + "(missing) in observer.ini\n\n"
                + "Application is shuting down..."),_("Error:"),
                win32con.MB_OK or
                win32con.MB_ICONINFORMATION or
                win32con.MB_TOPMOST)
                
                sys.exit(1)
            
            file_path = genv.v__app__config["doxygen"]["path"]
            
            if len(file_path) < 1:
                if getattr(sys, 'frozen', False):
                    pyi_splash.close()
                    
                win32api.MessageBox(0,(""
                + "Error: "
                + genv.doxy_env
                + " is not set in your system settings."),
                _("Error:"),
                win32con.MB_OK or
                win32con.MB_ICONINFORMATION or
                win32con.MB_TOPMOST)
                
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
                if getattr(sys, 'frozen', False):
                    pyi_splash.close()
                    
                win32api.MessageBox(0,(""
                + "Error: no section: 'doxygen' or option: 'hhc'\n"
                + "(missing) in observer.ini\n\n"
                + "Application is shuting down..."),_("Error:"),
                win32con.MB_OK or
                win32con.MB_ICONINFORMATION or
                win32con.MB_TOPMOST)
                
                sys.exit(1)
            
            file_path = genv.v__app__config["doxygen"]["hhc"]
            
            if len(file_path) < 1:
                if getattr(sys, 'frozen', False):
                    pyi_splash.close()
                    
                win32api.MessageBox(0,(""
                + "Error: "
                + genv.doxy_hhc
                + " is not set in your system settings."),
                _("Error:"),
                win32con.MB_OK or
                win32con.MB_ICONINFORMATION or
                win32con.MB_TOPMOST)
                
                sys.exit(genv.EXIT_FAILURE)
            else:
                os.environ["DOXYHHC_PATH"] = file_path
    else:
        genv.hhc__path = os.environ[genv.doxy_hhc]
    
    # -------------------------------
    # close tje splash screen ...
    # -------------------------------
    if getattr(sys, 'frozen', False):
        pyi_splash.close()
    
    window_license = licenseWindow()
    window_license.exec_()
    
    window = LandingPage()
    window.exec_()
    #genv.window_login = LoginDialog()
    #genv.window_login.exec_()
    
    # ------------------------------------------------------------------------
    # selected list of flags for translation localization display ...
    # ------------------------------------------------------------------------
    cdn_host = genv.v__app__cdn_host + "/observer/img/flags/"
    cdn_suff = ".gif"
    genv.v__app__cdn_flags = _("moped_list")
    #
    pattern_host = r"cdn_host"
    pattern_suff = r"cdn_suff"
    #
    processed_string = re.sub(pattern_host, repr(cdn_host), genv.v__app__cdn_flags)
    processed_string = re.sub(pattern_suff, repr(cdn_suff), processed_string)
    #
    genv.v__app__cdn_flags = eval(processed_string)
    
    
    # ---------------------------------------------------------
    # when config file not exists, then spite a info message,
    # and create a default template for doxygen 1.10.0
    # ---------------------------------------------------------
    if not os.path.exists(genv.doxyfile):
        DebugPrint("info: config: '" \
        + f"{genv.doxyfile}" + "' does not exists. I will fix this by create a default file.")
        
        file_content      = json.loads(_("doxyfile_content"))
        #DebugPrint(file_content)
        
        try:
            file_content_warn = json.loads(_("doxyfile_content_warn"))
            #DebugPrint(file_content_warn)
        except Exception as e:
            DebugPrint(e)
        DebugPrint(">>>")
        #DebugPrint(file_content)
        DebugPrint("<<<")
        with open(genv.doxyfile, 'w') as file:
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
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H:%M:%S")
    
    conn = sqlite3.connect(os.path.join(genv.v__app__internal__, "data.db"))
    conn_cursor = conn.cursor()
    conn.close()
    
    #öööö
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
            DebugPrint(f"Exception: {e}")
            DebugPrint(f"Error occurred in file: {filename}")
            DebugPrint(f"Function: {funcname}")
            DebugPrint(f"Line number: {lineno}")
            DebugPrint(f"Line text: {text}")
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

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        
        #window = LandingPage(EntryPoint)
        #window.exec_()
        #self.close()
        #sys.exit(0)

# ---------------------------------------------------------------------------
# parse dBase script ...
# ---------------------------------------------------------------------------
class parserDBasePoint:
    def __init__(self, script_name):
        try:
            showInfo("oooppppp")
            prg = dBaseDSL(script_name)
        except configparser.NoOptionError as e:
            err = _("Exception: option 'language' not found.") + "\n" + _("abort")
            showException(err)
        except configparser.NoSectionError as e:
            err = _("Exception: section not found.") + "\n" + e + _("abort.")
            showException(err)
        except configparser.Error as e:
            err = _("Exception: config error occur.") + "\n" + _("abort.")
            showException(err)
        except SyntaxError as e:
            exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
            tb = traceback.extract_tb(e.__traceback__)[-1]
            
            err = (_("Exception occur at module import:") +
            f"type : {exc_type.__name__}" +
            f"value: {exc_value}"     +   ("-"*40)  +
            f"file : {tb.filename}\n" +
            f"line : {tb.lineno}")
            
            showException(err)
        except Exception as e:
            exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
            tb = traceback.extract_tb(e.__traceback__)[-1]
            #
            if exc_type.__name__ == "NoOptionError":
                #genv.v__app__locales = os.path.join(genv.v__app__locales, genv.v__locale__sys[0])
                #genv.v__app__locales = os.path.join(genv.v__app__locales, "LC_MESSAGES")
                #genv.v__app__locales = os.path.join(genv.v__app__locales, genv.v__app__name_mo)
                pass
            else:
                err = (
                _("Exception occur at module import:") + "\n" +
                f"type : {exc_type.__name__}\n" +
                f"value: {exc_value}\n"         + ("-"*40) +
                f"file : {tb.filename}\n"       +
                f"line : {tb.lineno}\n")
                showException(err)

# ---------------------------------------------------------------------------
# parse Doxyfile script ...
# ---------------------------------------------------------------------------
class parserDoxyGen:
    def __init__(self, script_name, parent_gui=None):
        self.parent_gui = parent_gui
        prg = doxygenDSL(script_name, parent_gui)

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
            DebugPrint("\nend of data")

def analyze_pe(file_path):
    try:
        # PE-Datei öffnen
        pe = pefile.PE(file_path)
        
        DebugPrint("\n--- PE-Header Informationen ---")
        DebugPrint(f"Machine: 0x{pe.FILE_HEADER.Machine:04x}")
        DebugPrint(f"Number of Sections: {pe.FILE_HEADER.NumberOfSections}")
        DebugPrint(f"TimeDateStamp: {pe.FILE_HEADER.TimeDateStamp}")
        DebugPrint(f"PointerToSymbolTable: {pe.FILE_HEADER.PointerToSymbolTable}")
        DebugPrint(f"Characteristics: 0x{pe.FILE_HEADER.Characteristics:04x}")
        
        DebugPrint("\n--- Optional Header ---")
        DebugPrint(f"ImageBase: 0x{pe.OPTIONAL_HEADER.ImageBase:x}")
        DebugPrint(f"EntryPoint: 0x{pe.OPTIONAL_HEADER.AddressOfEntryPoint:x}")
        DebugPrint(f"SectionAlignment: {pe.OPTIONAL_HEADER.SectionAlignment}")
        DebugPrint(f"FileAlignment: {pe.OPTIONAL_HEADER.FileAlignment}")
        DebugPrint(f"Subsystem: {pe.OPTIONAL_HEADER.Subsystem}")
        
        DebugPrint("\n--- Sektionen ---")
        for section in pe.sections:
            DebugPrint(f"Name: {section.Name.decode().strip()}")
            DebugPrint(f"Virtual Address: 0x{section.VirtualAddress:x}")
            DebugPrint(f"Size of Raw Data: 0x{section.SizeOfRawData:x}")
            DebugPrint(f"Pointer to Raw Data: 0x{section.PointerToRawData:x}")
            DebugPrint("Characteristics: 0x{:08x}".format(section.Characteristics))
            DebugPrint("-" * 30)
        
        DebugPrint("\n--- Importierte DLLs und Funktionen ---")
        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                DebugPrint(f"Library: {entry.dll.decode()}")
                for imp in entry.imports:
                    DebugPrint(f"  {hex(imp.address)}: {imp.name.decode() if imp.name else 'N/A'}")
        
        DebugPrint("\n--- Exportierte Funktionen (falls vorhanden) ---")
        if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
            for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                DebugPrint(f"{hex(pe.OPTIONAL_HEADER.ImageBase + exp.address)}: {exp.name.decode() if exp.name else 'N/A'}")
    
    except FileNotFoundError:
        DebugPrint("Datei wurde nicht gefunden. Bitte den Dateipfad überprüfen.")
    except Exception as e:
        DebugPrint(f"Ein Fehler ist aufgetreten: {str(e)}")

# ---------------------------------------------------------------------------
# the mother of all: the __main__ start point ...
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    
    # The Python 3+ or 3.12+ is required.
    major = sys.version_info[0]
    minor = sys.version_info[1]
    if (major < 3 and minor < 12):
        DebugPrint("Python 3.12+ are required for the script")
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
        DebugPrint("no arguments given.")
        #DebugPrint(genv.v__app__parameter)
        sys.exit(1)
        
    idx = 1
    if len(sys.argv) >= 1:
        for item in sys.argv:
            if item == "--gui":
                handleExceptionApplication(EntryPoint)
                sys.exit(0)
            elif item == "--doxygen":
                idx += 1
                if sys.argv[idx]:
                    sys.argv.append("Doxyfile")
                    genv.v__app__scriptname__ = sys.argv[idx]
                    handleExceptionApplication(parserDoxyGen,sys.argv[idx])
                    sys.exit(0)
            elif item == "--exec":
                idx += 1
                genv.v__app__scriptname__ = sys.argv[idx + 1]
                handleExceptionApplication(parserBinary,sys.argv[idx])
            elif item == "--dbase":
                idx += 1
                DebugPrint(genv.v__app__tmp3)
                try:
                    handleExceptionApplication(parserDBasePoint,sys.argv[idx])
                    sys.exit(0)
                except Exception as ex:
                    sys.exit(1)
            elif item == "--pascal":
                idx += 1
                DebugPrint(genv.v__app__tmp3)
                genv.v__app__scriptname__ = sys.argv[2]
                handleExceptionApplication(parserPascalPoint,sys.argv[idx])
                sys.exit(0)
            else:
                if item.endswith(".exe"):
                    DebugPrint("check: " + item)
                    analyze_pe(item)
                    sys.exit(1)
        else:
            DebugPrint("parameter unknown.")
            DebugPrint(genv.v__app__parameter)
            sys.exit(1)
        
# ----------------------------------------------------------------------------
# E O F  -  End - Of - File
# ----------------------------------------------------------------------------
