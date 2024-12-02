# ---------------------------------------------------------------------------
# File:   client.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# global used application stuff. try to catch import exceptions ...
# ---------------------------------------------------------------------------

# Dictionary to store the mapping from object instances to variable names
instance_names = {}

import importlib
import subprocess
import sys           # system specifies
import os            # operating system stuff

try:
    # -----------------------------------------------------------------------
    # under the windows console, python paths can make problems ...
    # -----------------------------------------------------------------------
    if 'PYTHONHOME' in os.environ:
        del os.environ['PYTHONHOME']
    if 'PYTHONPATH' in os.environ:
        del os.environ['PYTHONPATH']
    
    # ------------------------------------------------------------------------
    # before we start the application core, we try to update the pip installer
    # ------------------------------------------------------------------------
    try:
        result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)
        print("pip is up to date.")
    except subprocess.CalledProcessError as ex:
        print(f"error: pip installer update fail. {ex.returncode}")
        sys.exit(1)
    
    # ------------------------------------------------------------------------
    # check for installed modules ...
    # ------------------------------------------------------------------------
    def check_and_install_module():
        required_modules = [
            "dbf", "polib", "requests", "timer", "datetime", "gmpy2",
            "locale", "io", "random", "string",
            "ctypes", "sqlite3", "configparser", "traceback", "marshal", "inspect",
            "logging", "PyQt5", "pathlib", "rich", "string", "codecs" ]
        
        for module in required_modules:
            try:
                importlib.import_module(module)
                print(f"{module} is already installed.")
            except ImportError:
                try:
                    print(f"error: {module} not found. Installing...")
                    result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--user", module],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
                    print(f"{module} installed successfully.")
                except:
                    try:
                        print(f"error: upgrade pip...")
                        result = subprocess.run(
                        [sys.executable, "-m", "pip", "--upgrade", "pip"],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                        print(f"info: pip installer upgrade ok.")
                        #
                        result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--user", module],
                        check=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE)
                        print(f"{module} installed successfully.")
                    except:
                        print(f"error: module: install fail.")
                        sys.exit(1)
    check_and_install_module()
except Exception as e:
    exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
    tb = traceback.extract_tb(e.__traceback__)[-1]
    
    print(f"Exception occur:")
    print(f"type : {exc_type.__name__}")
    print(f"value: {exc_value}")
    print(("-" * 40))
    #
    print(f"file : {tb.filename}")
    print(f"line : {tb.lineno}")
    sys.exit(1)
        
# ------------------------------------------------------------------------
# this is a double check for application imports ...
# ------------------------------------------------------------------------
import re             # regular expression handling
import requests       # get external url stuff
import traceback

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

import textwrap
import marshal        # bytecode exec
import inspect        # stack
import gc             # garbage collector

import logging
import dbf            # good old data base file

# ------------------------------------------------------------------------
# windows os stuff ...
# ------------------------------------------------------------------------
import win32api
import win32con

# ------------------------------------------------------------------------
# gnu multi precision version 2 (gmp2 for python)
# ------------------------------------------------------------------------
import gmpy2
from   gmpy2 import mpz, mpq, mpfr, mpc

# ------------------------------------------------------------------------
# Qt5 gui framework
# ------------------------------------------------------------------------
from PyQt5.QtWebEngineWidgets   import *
from PyQt5.QtWidgets            import *
from PyQt5.QtCore               import *
from PyQt5.QtGui                import *
from PyQt5.QtNetwork            import *

if getattr(sys, 'frozen', False):
    import pyi_splash

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
# message box code place holder ...
# ------------------------------------------------------------------------
class showMessage(QDialog):
    def __init__(self, text="", msgtype=0):
        super(showMessage, self).__init__()
        
        if not isApplicationInit():
            genv.v__app_object = QApplication(sys.argv)
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
        self.v__app__logging      = None
        
        self.v__app__img__int__   = os.path.join(self.v__app__internal__, "img")
        
        im_path = self.v__app__img__int__ + "/"
        
        self.isGuiApplication = False
        
        self.start_idx = 1
        self.end_idx   = 1
        
        self.header_code = ""

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
        
        # ---------------------------------------------------------------------------
        # \brief currently onle two converters are supported:
        #        0 - not sprecified => unknown
        #        1 - doxygen
        #        2 - helpndoc.com
        # ---------------------------------------------------------------------------
        self.HelpAuthoringConverterMode = 0
        
        self.v__app__doxygen__  = im_path + "doxygen"
        self.v__app__hlpndoc__  = im_path + "helpndoc"
        self.v__app__helpdev__  = im_path + "help"
        self.v__app__pythonc__  = im_path + "python"
        self.v__app__lispmod__  = im_path + "lisp"
        self.v__app__prologm__  = im_path + "prolog"
        self.v__app__ccpplus__  = im_path + "cpp"
        self.v__app__cpp1dev__  = im_path + "c"
        self.v__app__dbasedb__  = im_path + "dbase"
        self.v__app__javadev__  = im_path + "java"
        self.v__app__javascr__  = im_path + "javascript"
        self.v__app__javadoc__  = im_path + "javadoc"
        self.v__app__freepas__  = im_path + "freepas"
        self.v__app__locales__  = im_path + "locales"
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

        # ------------------------------------------------------------------------
        # dBase parser error code's:
        # ------------------------------------------------------------------------
        self.DBASE_EXPR_SYNTAX_ERROR   = 1000
        self.DBASE_EXPR_KEYWORD_ERROR  = 1001
        self.DBASE_EXPR_IS_EMPTY_ERROR = 1002
        
        self.code_error     = 0
        self.counter_if     = 0
        self.counter_endif  = 0

        self.char_prev = ''
        self.char_curr = ''
        self.char_next = ''
        
        self.temp_token = ""
        self.TOKEN_TEMP = 4000
        
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
            "lisp": []
        }
        
        self.radio_cpp          = None
        self.radio_java         = None
        self.radio_javascript   = None
        self.radio_python       = None
        self.radio_php          = None
        
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
        
        self.editor_check = None
        self.editor_saveb = None
        
        self.current_focus = None
        
        self.img_doxygen = None
        self.img_hlpndoc = None
        
        #self.img_ccpplus = None
        #self.img_javadoc = None
        #self.img_freepas = None

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
        self.v__app__config   = None
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
        
        self.doc_project  = ""
        self.doc_template = -1
        self.doc_type     = -1
        
        self.DOC_TEMPLATE_API      = 0
        self.DOC_TEMPLATE_EMPTY    = 1
        self.DOC_TEMPLATE_RECIPE   = 2
        self.DOC_TEMPLATE_SOFTWARE = 3
        
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

        self.project_type = ""
        self.error_fail = False
        self.byte_code = None
        
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
            raise unexpectedParserException(self.message, genv.code_error)
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
# read a file into memory ...
# ------------------------------------------------------------------------
def read_gzfile_to_memory(file_path):
    check_file = Path(file_path)
    if not check_file.exists():
        print("Error: gzfile directory exists, but file could not found.")
        print("abort.")
        sys.exit(1)
    if not check_file.is_file():
        print("Error: gzfile is not a file.")
        print("abort.")
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
                print("Error: language mo file could not be load.")
                print("abort.")
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
        
        print(f"Exception occur during handle language:")
        print(f"type : {exc_type.__name__}")
        print(f"value: {exc_value}")
        print(("-" * 40))
        #
        print(f"file : {tb.filename}")
        print(f"llline : {tb.lineno}")
        #
        sys.exit(genv.EXIT_FAILURE)
 
def handle_help(lang):
    try:
        _h = read_gzfile_to_memory(genv.v__app__locales_help)
        return _h
    except Exception as e:
        exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
        tb = traceback.extract_tb(e.__traceback__)[-1]
        
        print(f"Exception occur during handle language:")
        print(f"type : {exc_type.__name__}")
        print(f"value: {exc_value}")
        print(("-" * 40))
        #
        print(f"file : {tb.filename}")
        print(f"llline : {tb.lineno}")
        #
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
        print("run in terminal")
    if genv.run_in_gui:
        print("run in gui")
    
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
        print("Error: loacles directory not found.")
        print("abort.")
        sys.exit(1)

    print(genv.v__app__config["common"]["language"])
    genv.v__app__locales = os.path.join(genv.v__app__internal__, "locales")
    genv.v__app__locales = os.path.join(genv.v__app__locales, genv.v__app__config["common"]["language"])
    
    genv.v__app__locales_messages = os.path.join(genv.v__app__locales, "LC_MESSAGES")
    genv.v__app__locales_help     = os.path.join(genv.v__app__locales, "LC_HELP")
    
    genv.v__app__locales_messages = os.path.join(genv.v__app__locales_messages, genv.v__app__name_mo + ".gz")
    genv.v__app__locales_help     = os.path.join(genv.v__app__locales_help    , genv.v__app__help_mo + ".gz")
    #
    if len(genv.v__app__locales) < 5:
        print("Error: locale out of seed.")
        print("abort.")
        sys.exit(1)
        
    _  = handle_language(ini_lang)
    _h = handle_help    (ini_lang)
    
    # ------------------------------------------------------------------------
    # determine on which operating the application script runs ...
    # ------------------------------------------------------------------------
    genv.os_name = platform.system()
    print("OS: ", genv.os_name)
    if genv.os_name == 'Windows':
        print("The Application runs under Windows.")
    elif genv.os_name == 'Linux':
        print("The Application runs under Linux.")
    elif genv.os_name == 'Darwin':
        print("The Application runs under macOS.")
    else:
        print(f"Unknown Operating System: {genv.os_name}")
    
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
        print(_("windll error"))
    except Exception:
        print(_("common exception occur"))

except IgnoreOuterException:
    print(genv.v__app__locales)
    pass
except configparser.NoOptionError as e:
    print("Exception: option 'language' not found.")
    print("abort.")
    sys.exit(1)
except configparser.NoSectionError as e:
    print("Exception: section not found.\n")
    print(e)
    print("abort.")
    sys.exit(1)
except configparser.Error as e:
    print("Exception: config error occur.")
    print("abort.")
    sys.exit(1)
except SyntaxError as e:
    exc_type, exc_value, exc_traceback = traceback.sys.exc_info()
    tb = traceback.extract_tb(e.__traceback__)[-1]
    
    print(f"Exception occur at module import:")
    print(f"type : {exc_type.__name__}")
    print(f"value: {exc_value}")
    print(("-" * 40))
    #
    print(f"file : {tb.filename}")
    print(f"line : {tb.lineno}")
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
        print(f"Exception occur at module import:")
        print(f"type : {exc_type.__name__}")
        print(f"value: {exc_value}")
        print(("-"*40))
        #
        print(f"file : {tb.filename}")
        print(f"line : {tb.lineno}")
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
        print(ClassObjects[0]["class"]["hash"])
        print(ClassObjects[1]["class"]["hash"])
    
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
                print("error during element del.")
        
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
            raise E_Error(_("stream could not save."))
    
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
                print("item is string")
                return True
            elif isinstance(AItem, int):
                print("item is integer")
                return True
            elif isinstance(AItem, float):
                print("item is float")
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

class SSLClient:
    def __init__(
        self,
        host          = 'localhost',
        port          = 1234,
        crt_file      = './ssl/client.crt',
        key_file      = './ssl/client.key'):
        self.socket   = QSslSocket()
        
        self.crt_file = crt_file
        self.key_file = key_file
        
        self.host     = host
        self.port     = port
    
    def set_host(self, addr):
        self.host = addr
        return True
    
    def set_port(self, port):
        self.port = port
        return True
    
    def set_crt_file(self, crt_file):
        self.crt_file = crt_file
        return True
    
    def set_key_file(self, key_file):
        self.key_file = key_file
        return True
    
    def get_host(self):
        return self.host
    def get_port(self):
        return self.port
    def get_crt_file(self):
        return self.crt_file
    def get_key_file(self):
        return self.key_file
    
    def connect(self):
        # SSL-Konfiguration
        certificates = QSslCertificate.fromPath(cert_file)
        if not certificates:
            showInfo(_("Error:\nThe 'client.csr' file could not be found or it is wrong."))
            return False
        
        cert = certificates[0]
        self.socket.setLocalCertificate(cert)

        with open(self.key_file, "rb") as key_file:
            key = QSslKey(
            key_file.read(),
            QSsl.KeyAlgorithm.Rsa,
            QSsl.EncodingFormat.Pem,
            QSsl.PrivateKey)
            key_file.close()
        
        self.socket.setPrivateKey(key)
        self.socket.connectToHostEncrypted(self.host, self.port)

        if not self.socket.waitForEncrypted():
            showInfo(f"SSL Error:\n{self.socket.errorString()}")
            return False
        else:
            showInfo(_("SSL encrypted connection established."))
            
        # Signal-Verbindungen
        self.socket.readyRead.connect(self.read_data)

    def send(self, message):
        self.socket.write(message.encode())
        self.socket.flush()

    def read(self):
        data = self.socket.readAll().data().decode()
        print(f"Empfangene Daten vom Server: {data}")


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
    """a help project is a collection of topics and options that will be compiled
    to a HTMLHelp file (.chm)"""
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
                print(f"Warning, link '{link_to}' invalid or external.")
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
            print("DATEINAME=" + filename)
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
            print(f"Warning, link '{token}' is used more than once.")
            
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
            print(e)
    
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
        print(parent);
        return
    def add(self, menu_list):
        self.struct.append(menu_list)
        return
    def show(self, make_visible=True):
        if make_visible:
            print(self.struct);
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
        
        str_font   = "fint"
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

# ---------------------------------------------------------------------------
# \brief A dos-console Qt5 Dialog - used by dBase console Applications.
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
            print(e)
    
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
                print("info: current scope without "
                + "comments initialized.")
            # --------------------------
            # argument type is a class
            # --------------------------
            elif argument == ParserDSL:
                self.parent = argument
                if self.parent.name != argument.name:
                    print("info: current scope with: "
                    + argument.name
                    + " comments overwrite.")
                    self.parent.name = argument.name
                else:
                    print("info: current scope not touched, because"
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
                    print("info: current scope with: "
                    + argument
                    + " comments initialized.")
                    self.parent.name = argument
                # --------------------------
                # dsl not in supported list
                # --------------------------
                else:
                    print("info: current scope with custom "
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
        showInfo("destructor")
    
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
        
        genv.v__app__logging.info("start parse: " + self.script_name)
        
        self.err_commentNC = _("comment not closed.")
        self.err_commandNF = _("command sequence not finished.")
        self.err_unknownCS = _("unknown command or syntax error.")
        
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
        print("source: ", self.source)
    
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
        
        if self.pos >= len(self.source):
            raise e_no_more_data(_("getChar"))
        else:
            c = self.source[self.pos]
            if c == '\n':
                genv.line_col  = 1
                genv.line_row += 1
                return '\n'
            elif c == '\r':
                if self.pos >= len(self.source):
                    genv.unexpectedError(_("line ending error."))
                self.pos += 1
                c = self.source[self.pos]
                if c == '\n':
                    genv.line_col  = 1
                    genv.line_row += 1
                    return '\n'
                else:
                    genv.unexpectedEndOfLine(genv.line_row)
            elif (c == '\t') or (c == ' '):
                return c
            else:
                return c
    
    def ungetChar(self, num):
        genv.line_col -= num
        self.pos -= num
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
            genv.char_curr = self.getChar()
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
        return False;
    
    def check_token_digit(self, ch):
        if ch.isdigit():
            self.token_str = ch
            self.getNumber()
            return True
        return False
    
    def getIdent(self):
        self.token_str = genv.char_curr
        while True:
            genv.char_prev = genv.char_curr
            genv.char_curr = self.getChar()
            self.check_token_no_more_data()
            if self.check_token_white_spaces():
                return TOKEN_IDENT
            if self.check_token_alpha():
                self.token_str += genv.char_curr
                continue
            genv.have_errors = True
            genv.unexpectedError(_("getIdent"))
            return False
    
    def getNumber(self):
        have_point = False
        while True:
            genv.char_prev = genv.char_curr
            genv.char_curr = self.getChar()
            if genv.char_curr.isdigit():
                self.token_str += genv.char_curr
                continue
            elif genv.char_curr == '.':
                if have_point == True:
                    genv.have_errors = True
                    genv.unexpectedChar(c)
                    return False
                else:
                    have_point = True
                    continue
            else:
                self.ungetChar(1)
                return self.token_str
    
    def expect_ident(self, token=""):
        c = self.skip_white_spaces(self.dbase_parser)
        if c.isalpha() or c == '_':
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
        c = self.skip_white_spaces(self.dbase_parser)
        if c in genv.parser_op:
            genv.temp_code += c
            return True
        else:
            self.ungetChar(1)
            return False
    
    def expect_expr(self):
        c = self.skip_white_spaces(self.dbase_parser)
        if c.isdigit():
            self.token_str = c
            self.getNumber()
            #showInfo("token: " + self.token_str)
            genv.temp_code += self.token_str
            if self.expect_op():
                return self.expect_expr()
            else:
                return True
        elif c.isalpha() or c == '_':
            self.getIdent()
            genv.text_code += self.token_str
            return True
        elif self.expect_op():
            return self.expect_expr()
        elif c == '(':
            genv.text_code += '('
            return '('
        elif c == ')':
            self.ungetChar(1)
            return ')'
        else:
            return False
    
    def expect_assign(self):
        c = self.skip_white_spaces(self.dbase_parser)
        if not c == '=':
            genv.unexpectedError(_("assign sign expected."))
            return '\0'
        return True
    
    def check_null(self, c):
        if self.pos >= len(self.source):
            raise e_no_more_data()
        if c == '\0':
            return True
        else:
            return False
    
    def check_spaces(self, c):
        if c == '\t' or c  == ' ':
            genv.line_col += 1
            result = True
        return False
    
    def check_newline(self, c):
        result = False
        if c == '\n':
            genv.line_col  = 1
            genv.line_row += 1
            result = True
        elif c == '\r':
            c = self.getChar()
            if not c == '\n':
                genv.unexpectedEndOfLine(genv.line_row)
                return result
            genv.line_col  = 1
            genv.line_row += 1
            result = True
        return result
    
    def check_digit(self, c):
        if c.isdigit():
            self.ungetChar(1)
            self.getNumber()
            return True
        else:
            self.unexpectedError(_("expect a digit"))
        return False
        
    def check_alpha(self, ch):
        result = False
        if ch.isalpha():
            self.getIdent()
            result = True
        else:
            genv.unexpectedChar(ch)
            result = False
        return result
    
    def handle_pascal_comment_1(self):
        while True:
            c = self.getChar()
            self.check_null(c)
            if self.check_newline(c):
                continue
            if c == '*':
                c = self.getChar()
                self.check_null(c)
                if c == ')':
                    return True
                elif self.check_newline(c):
                    continue
                continue
        if not c == ')':
            genv.unexpectedError(_("comment not closed"))
            return False
        return False
    
    def handle_pascal_comment_2(self):
        while True:
            c = self.getChar()
            self.check_null(c)
            if self.check_newline(c):
                continue
            if c == '}':
                genv.line_col += 1
                self.in_comment -= 1
                break
            elif c == '$':
                c = self.getChar()
                self.check_null(c)
                if self.check_token_ident(c):
                    if len(self.token_str) > 64:
                        genv.have_errors = True
                        genv.unexpectedError(_("macro name too long"))
                        return False
                    elif self.check_token_ident_macro(self.token_str):
                        pass
                else:
                    genv.unexpectedError(_("unknown macro symbol"))
                    return '\0'
            else:
                genv.line_col += 1
                continue
        if not c == '}':
            genv.unexpectedError(_("comment not closed"))
            return
    
    # -----------------------------------------------------------------------
    # \brief skip all whitespaces. whitespaces are empty lines, lines with
    #        one or more spaces (0x20): " ", \t, "\n".
    # -----------------------------------------------------------------------
    def skip_white_spaces(self, parser_type):
        self.pascal_comment_open = False
        while True:
            genv.char_prev = genv.char_curr
            genv.char_curr = self.getChar()
            self.check_token_no_more_data(_("skip white spaces"))
            if self.check_token_char(')'):
                genv.open_paren -= 1
                if genv.open_paren < 0:
                    genv.have_errors = True
                    genv.unexpectedError(_("paren underflow."))
                    return False
                else:
                    genv.text_code += ')'
                    return True
            if self.check_token_char('('):
                genv.open_paren += 1
                genv.text_code  += genv.char_curr
                genv.char_prev   = genv.char_curr
                genv.char_curr   = self.getChar()
                if self.check_token_char('*'):
                    if parser_type == self.pascal_parser:
                        while True:
                            genv.char_prev = genv.char_curr
                            genv.char_curr = self.getChar()
                            self.check_token_no_more_data(_("comment not terminated."))
                            if self.check_token_white_spaces():
                                continue
                            if self.check_token_char('*'):
                                genv.char_prev = genv.char_curr
                                genv.char_curr = self.getChar()
                                if self.check_token_char(')'):
                                    break
                            else:
                                continue
                        continue
                    else:
                        genv.have_errors = True
                        genv.unexpectedError(_("pascal comment not allowed"))
                        return
                else:
                    continue
            
            if self.check_token_alpha():
                if self.getIdent() == genv.TOKEN_IDENT:
                    return genv.TOKEN_IDENT
                else:
                    genv.have_errors = True
                    genv.unexpectedError(_("alpha ident error."))
                    return False
            
            if self.check_token_newline():
                continue
            elif c == '{':
                if parser_type == self.pascal_parser:
                    while True:
                        genv.char_prev = genv.char_curr
                        genv.char_curr = self.getChar()
                        if genv.char_curr == genv.ptNoMoreData:
                            genv.have_errors = True
                            genv.unexpectedError(_("unterminated comment."))
                            return False
                        elif genv.char_curr == '}':
                            break
                        continue
                else:
                    genv.have_errors = True
                    genv.unexpectedError(_("pascal comment not allowed"))
                    return
            elif genv.char_curr == '*':
                genv.char_prev = genv.char_curr
                genv.char_curr = self.getChar()
                self.check_token_no_more_data(_("comment not terminated."))
                if self.check_token_char('*'):
                    if parser_type == self.dbase_parser:
                        while True:
                            genv.char_prev = genv.char_curr
                            genv.char_curr = self.getChar()
                            self.check_token_no_more_data(_("comment not terminated."))
                            if genv.char_curr == '\n':
                                break
                            elif genv.char_curr == '\r':
                                genv.char_prev = genv.char_curr
                                genv.char_curr = self.getChar()
                                if not genv.char_curr == '\n':
                                    genv.have_errors = True
                                    genv.unexpectedError(_("line end error."))
                                    return False
                                else:
                                    break
                        continue
                    else:
                        genv.have_errors = True
                        genv.unexpectedError(_("dbase comment not allowed."))
                        return False
                else:
                    return genv.char_curr
            elif c == '&':
                c = self.getChar()
                if c == genv.ptNoMoreData:
                    return c
                elif c == '&':
                    if parser_type == self.dbase_parser:
                        while True:
                            c = self.getChar()
                            if c == genv.ptNoMoreData:
                                return c
                            elif c == '\n':
                                break
                            elif c == '\r':
                                c = self.getChar()
                                if not c == '\n':
                                    genv.have_errors = True
                                    genv.unexpectedError(_("line end error."))
                                else:
                                    break
                        continue
                    else:
                        genv.have_errors = True
                        genv.unexpectedError(_("dbase comment not allowed."))
                        return
                else:
                    return c
            elif c == '/':
                c = self.getChar()
                if c == genv.ptNoMoreData:
                    return genv.ptNoMoreData
                elif c == '*':
                    if parser_type == self.dbase_parser:
                        self.in_comment += 1
                        while True:
                            c = self.getChar()
                            if c == genv.ptNoMoreData:
                                genv.have_errors = True
                                genv.unexpectedError(_("unterminated comment."))
                            elif c == '*':
                                c = self.getChar()
                                if c == '/':
                                    #showInfo("closed C Comment: "  + str(genv.line_row))
                                    self.in_comment -= 1
                                    break
                                else:
                                    continue
                            else:
                                continue
                        if self.in_comment > 0:
                            #showInfo("comment großer")
                            genv.have_errors = True
                            genv.unexpectedError(_("self.err_commentNC"))
                    else:
                        genv.have_errors = True
                        genv.unexpectedError(_("C comment not allowrd"))
                        return
                elif c == '/':
                    #showInfo("C++ comment: "  + str(genv.open_paren))
                    while True:
                        c = self.getChar()
                        if c == genv.ptNoMoreData:
                            genv.have_errors = True
                            genv.unexpectedError(_("unterminated comment."))
                        elif c == '\n':
                            break
                        elif c == '\r':
                            c = self.getChar()
                            if not c == '\n':
                                genv.have_errors = True
                                genv.unexpectedError(_("line end error."))
                            else:
                                break
                        else:
                            continue
                    #showInfo("closed C++ comment: " + str(genv.line_row))
                    continue
                else:
                    self.ungetChar(1)
                    return '/'
            elif (c == '\r'):
                c = self.getChar()
                if not c == '\n':
                    genv.have_errors = True
                    raise e_expr_error(
                        message=_("line end syntax error"),
                        line=genv.line_row,
                        code=1200
                        )
                    return 0
                continue
            elif (c == '\n') or (c == '\t') or (c == ' '):
                continue
            elif c.isalpha() or c == '_':
                return c
            else:
                return c
    
    def check_token_newline(self):
        if genv.char_curr == '\n':
            return True
        if genv.char_curr == '\r':
            genv.char_prev = genv.char_curr
            genv.char_curr = self.getChar()
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
            c = self.getChar()
            if self.check_null(c):
                return '\0'
            if self.check_spaces(c):
                continue
            if self.check_newline(c):
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
            c = self.skip_white_spaces(self.dbase_parser)
            if c == '(':
                c = self.skip_white_spaces(self.dbase_parser)
                if c == ')':
                    genv.text_code += ('\t' * genv.counter_indent)
                    genv.text_code += ("console.win.gotoxy(" +
                    str(self.xpos) + ","   +
                    str(self.ypos) + ")\n" +
                    ('\t' * genv.counter_indent) + "console.win.print_date()\n")
                    
                    self.command_ok = True
                else:
                    genv.unexpectedChar(c)
            else:
                genv.unexpectedChar(c)
        elif self.token_str.lower() == "str":
            c = self.skip_white_spaces(self.dbase_parser)
            if c == '(':
                c = self.skip_white_spaces(self.dbase_parser)
                if c == ')':
                    print("strrr")
                    self.command_ok = True
                else:
                    genv.unexpectedChar(c)
            else:
                genv.unexpectedChar(c)
        else:
            genv.unexpectedToken(self.token_str)
    
    def handle_string(self, mode=0):
        c = self.skip_white_spaces(self.dbase_parser)
        if c == '"':
            self.temp_code += '"'
            while True:
                c = self.getChar()
                if c == genv.ptNoMoreData:
                    return c
                elif c == '"':
                    self.temp_code += '"'
                    c = self.skip_white_spaces(self.dbase_parser)
                    if c == '+':
                        self.temp_code += " + "
                        return self.handle_string()
                    else:
                        self.ungetChar(1)
                        return self.temp_code
                elif c == '\\':
                    c = self.getChar()
                    if c == "\n" or c == "\r":
                        genv.unexpectedEndOfLine(genv.line_row)
                    elif c == " ":
                        genv.unexpectedEscapeSign(genv.line_row)
                    elif c == '\\':
                        self.temp_code += "\\"
                    elif c == 't':
                        self.temp_code += "\t"
                    elif c == 'n':
                        self.temp_code += "\n"
                    elif c == 'r':
                        self.temp_code += "\r"
                    elif c == 'a':
                        self.temp_code += "\a"
                    else:
                        self.temp_code += c
                    continue
                else:
                    self.temp_code += c
                    continue
            return self.temp_code
    
    def handle_parens(self):
        c = self.skip_white_spaces(self.dbase_parser)
        if c == '(':
            self.open_paren += 1
            genv.temp_code  += c
            c = self.skip_white_spaces(self.dbase_parser)
            if c == genv.ptNoMoreData:
                genv.unexpectedError(_("no more data."))
            elif c == '(':
                self.ungetChar(1)
                self.handle_parens()
                return self.temp_code # todo !!!
            return self.get_brace_code()
        elif c == ')':
            genv.open_paren -= 1
            genv.temp_code  += c
            if genv.open_paren < 1:
                return genv.temp_code
        elif c in genv.parser_op:
            genv.temp_code += c
            return handle_parens()
        elif c.isdigit():
            self.token_str = c
            self.getNumber()
            genv.temp_code += self.token_str
            return self.get_brace_code()
        elif c.isalpha():
            self.token_str = c
            self.getIdent()
            genv.text_code += self.token_str
            return self.get_brace_code()
        elif c in genv.parser_op:
            genv.text_code += c
            return self.get_brace_code()
        elif c == ',':
            return c
        else:
            if genv.counter_brace > 0:
                raise unexpectedParserException(_("missing closed parens"), genv.line_row)
                return '\0'
        return False
    
    def handle_numalpha(self):
        while True:
            c = self.skip_white_spaces(self.dbase_parser)
            if c.isdigit():
                self.token_str = c
                self.getNumber()
                genv.text_code += self.token_str
                continue
            elif c.isalpha() or c == '_':
                self.token_str = c
                self.getIdent()
                genv.text_code += self.token_str
                continue
            elif c in genv.parser_op:
                genv.text_code += c
                continue
            elif c == '(':
                genv.counter_brace += 1
                genv.text_code += c
                continue
            elif c == ')':
                genv.counter_brace -= 1
                if self.second_part:
                    return c
                continue
            elif c == ',':
                return c
        return '\0'
    
    def tokenString(self):
        self.token_str = ""
        c = self.skip_white_spaces(self.dbase_parser)
        if c == '\"':
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
            c = self.skip_white_spaces(self.dbase_parser)
            if c.isdigit():
                self.token_str = c
                self.getNumber()
                genv.text_code += ('\t' * genv.counter_indent)
                genv.text_code += "console.win.gotoxy("
                genv.text_code += self.token_str
                #
                #showInfo("digit:\n" + genv.text_code)
                c = self.skip_white_spaces(self.dbase_parser)
                if c == ',':
                    genv.text_code += ","
                    c = self.skip_white_spaces(self.dbase_parser)
                    if c.isdigit():
                        self.token_str = c
                        self.getNumber()
                        genv.text_code += self.token_str
                        genv.text_code += ")\n"
                        c = self.skip_white_spaces(self.dbase_parser)
                        if c.isalpha() or c == '_':
                            self.token_str = c
                            self.getIdent()
                            if self.token_str.lower() == "say":
                                c = self.skip_white_spaces(self.dbase_parser)
                                if c == '"':
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
                c = self.skip_white_spaces(self.dbase_parser)
                if c in['-','+','*','/']:
                    self.temp_code += c
                    self.prev_sign = True
                    continue
                elif c == ',':
                    c = self.skip_white_spaces(self.dbase_parser)
                    if c.isdigit():
                        self.token_str = c
                        self.getNumber()
                        genv.temp_code += "," + self.token_str + ")\n"
                        c = self.skip_white_spaces(self.dbase_parser)
                        if c.isalpha():
                            self.token_str = c
                            self.getIdent()
                            if self.token_str == "say":
                                genv.text_code += ('\t' * genv.counter_indent)
                                genv.text_code += "console.win.print("
                                c = self.skip_white_spaces(self.dbase_parser)
                                if c == '"':
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
            elif c.isalpha() or c == '_':
                #showInfo("a identerig")
                self.token_str = c
                self.getIdent()
                c = self.skip_white_spaces(self.dbase_parser)
                if c in['-','+','*','/']:
                    #showInfo("alpaha")
                    self.temp_code += c
                    self.prev_sign = True
                    continue
                elif c == ',':
                    if self.prev_expr:
                        genv.unexpectedError(_("comma prevv"))
                    self.prev_expr = True
                    continue
                else:
                    genv.unexpectedError(_("unexpected character found 2."))
            elif c == '(':
                genv.open_paren += 1
                genv.temp_code += '('
                continue
            elif c == ')':
                genv.open_paren -= 1
                if genv.open_paren < 1:
                    c = self.skip_white_spaces(self.dbase_parser)
                    if c in['-','+','*','/']:
                        continue
                    elif c.isalpha() or c == '_':
                        self.token_str = c
                        self.getIdent()
                        if self.token_str.lower() == "say":
                            #showInfo("saaayyyyer 111")
                            break
                        elif self.token_str.lower() == "get":
                            #showInfo("getter")
                            break
                    elif c.isdigit():
                        self.token_str = c
                        self.getNumber()
                        c = self.skip_white_spaces(self.dbase_parser)
                        if c in['-','+','*','/']:
                            self.temp_code += c
                            self.prev_sign = True
                            continue
                        elif c == ',':
                            if self.prev_expr:
                                genv.unexpectedError(_("comma prevv"))
                            self.prev_expr = True
                            continue
                        else:
                            genv.unexpectedError(_("loliutz"))
                else:
                    continue
            elif c == ',':
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
                c = self.skip_white_spaces(self.dbase_parser)
                if c == genv.ptNoMoreData:
                    raise e_no_more_data()
                if c.isalpha():
                    self.token_str = c
                    self.getIdent()
                    if self.token_str.lower() == "class":
                        genv.class_code += "class ";
                        self.token_str = ""
                        c = self.skip_white_spaces(self.dbase_parser)
                        if c == genv.ptNoMoreData:
                            raise e_no_more_data()
                        if c.isalpha():
                            self.token_str = c
                            self.getIdent()
                            ClassName = self.token_str
                            genv.class_code += self.token_str + "("
                            # class ClassName(
                            c = self.skip_white_spaces(self.dbase_parser)
                            if c == genv.ptNoMoreData:
                                raise e_no_more_data()
                            elif c.isalpha():
                                self.token_str = c
                                self.getIdent()
                                if self.token_str.lower() == "of":
                                    c = self.skip_white_spaces(self.dbase_parser)
                                    if c == genv.ptNoMoreData:
                                        raise e_no_more_data()
                                    elif c.isalpha():
                                        self.token_str = c
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
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if not c == '(':
                                                genv.have_errors = True
                                                genv.unexpectedChar(c)
                                                return
                                            showInfo("oooooooooooooooooo")
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if not c == ')':
                                                genv.have_errors = True
                                                genv.unexpectedChar(c)
                                                return
                                            elif c.isalpha():
                                                self.token_str = c
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
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if not c == '(':
                                                genv.have_errors = True
                                                genv.unexpectedChar(c)
                                                return
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if not c == ')':
                                                genv.have_errors = True
                                                genv.unexpectedChar(c)
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
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if not c == '(':
                                                genv.have_errors = True
                                                genv.unexpectedChar(c)
                                                return
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if not c == ')':
                                                genv.have_errors = True
                                                genv.unexpectedChar(c)
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
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if not c == '(':
                                                genv.have_errors = True
                                                genv.unexpectedChar(c)
                                                return
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if not c == ')':
                                                genv.have_errors = True
                                                genv.unexpectedChar(c)
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
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if not c == '(':
                                                genv.have_errors = True
                                                genv.unexpectedChar(c)
                                                return
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if not c == ')':
                                                genv.have_errors = True
                                                genv.unexpectedChar(c)
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
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if not c == '(':
                                                genv.have_errors = True
                                                genv.unexpectedChar(c)
                                                return
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if not c == ')':
                                                genv.have_errors = True
                                                genv.unexpectedChar(c)
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
                                    
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if c == genv.ptNoMoreData:
                                                raise e_no_more_data(_("endclass expected"))
                                            if c.isalpha():
                                                self.token_str = c
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
            c = self.skip_white_spaces(self.dbase_parser)
            #showInfo('----> ' + str(c))
            if c == genv.ptNoMoreData:
                return c
            elif c == '\n':
                continue
            elif c.isalpha() or c == '_':
                self.getIdent(c)
                if self.token_str.lower() == "class":
                    #showInfo("---------class------")
                    genv.class_code += "class "
                    self.handle_class()
                    return
                    
                elif self.token_str.lower() == "set":
                    #showInfo("token:  " + self.token_str)
                    self.token_str = ""
                    c = self.skip_white_spaces(self.dbase_parser)
                    if c.isalpha() or c == '_':
                        self.token_str = c
                        self.getIdent(c)
                        #showInfo("22 token:  " + self.token_str)
                        if self.token_str.lower() == "color":
                            self.token_str = ""
                            c = self.skip_white_spaces(self.dbase_parser)
                            if c.isalpha() or c == '_':
                                self.token_str = c
                                self.getIdent(c)
                                #showInfo("33 token:  " + self.token_str)
                                if self.token_str.lower() == "to":
                                    #showInfo("TTOOOOO")
                                    # ------------------------------------
                                    # fg / bg color: 1 / 2
                                    # ------------------------------------
                                    c = self.check_color_token(1)
                                    if c == 1000:
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
                    c = self.skip_white_spaces(self.dbase_parser)
                    if c == genv.ptNoMoreData:
                        #showInfo(_("temp code"))
                        #showInfo(genv.class_code)
                        raise e_no_more_data("temp code")
                    if c == '=':
                        genv.temp_code += " = "
                        genv.text_code += genv.temp_code
                        genv.temp_code = ""
                        #showInfo(genv.text_code)
                        while True:
                            c = self.getChar()
                            if c == '\n':
                                break
                            elif c in genv.ascii_charset:
                                self.token_str += c
                                continue
                            #else:
                            #    break
                        genv.text_code += self.token_str
                        genv.text_code += '\n'
                        #showInfo("variable:  " + self.token_str)
                        #showInfo(genv.text_code)
                    elif c == '(':
                        # todo: callee
                        #showInfo("todo callee")
                        pass
                    elif c.isalpha():
                        self.token_str = c
                        self.getIdent(c)
                        #showInfo('oo\n' + self.token_str)
                    else:
                        genv.unexpectedError(_("variable can not assign."))
                        return '\0'
            elif c == '@':
                #showInfo('sayer')
                self.handle_say()
                #showInfo("next sayer")
                continue
            elif c == '?':
                genv.text_code += ('\t' * genv.counter_indent)
                genv.text_code += "console.win.print_line("
                genv.last_command = False
                #
                self.token_str = ""
                #
                c = self.skip_white_spaces(self.dbase_parser)
                if c == '[':
                    c = self.skip_white_spaces(self.dbase_parser)
                    if c == '\"' or c == '\'':
                        self.ungetChar(1)
                        self.handle_string()
                        c = self.skip_white_spaces(self.dbase_parser)
                        if not c == ']':
                            genv.unexpectedError(_("] expected."))
                        else:
                            break
                        #showInfo("STRING: ", self.token_str)
                    else:
                        genv.unexpectedError(self.err_unknownCS)
                        return '\0'
                elif (c == '\"') or (c == '\''):
                    self.ungetChar(1)
                    self.handle_string(0)
            else:
                genv.unexpectedChar(c)
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
            #if not genv.editor_check.isChecked():
            #    self.handle_scoped_commands()
            #    return
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
        except:
            showException(traceback.format_exc())
    
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
            c = self.skip_white_spaces(self.dbase_parser)
            if c == genv.ptNoMoreData:
                genv.have_errors = True
                raise e_expr_error(
                    message=_("syntax error."),
                    line=genv.line_row,
                    code=genv.DBASE_EXPR_SYNTAX_ERROR
                    )
            elif c == '(':
                genv.text_code += c
                continue
            elif c == ')':
                genv.text_code += '):'
                break
            elif c.isnumeric():
                self.token_str = c
                self.getNumber()
                genv.text_code += self.token_str
                c = self.skip_white_spaces(self.dbase_parser)
                if c in['-','+','*','/']:
                    genv.text_code += c
                    c = self.skip_white_spaces(self.dbase_parser)
                    if c == genv.ptNoMoreData:
                        genv.have_errors = True
                        raise e_expr_error(
                            message=_("data out."),
                            line=genv.line.row,
                            code=genv.DBASE_EXPR_SYNTAX_ERROR
                            )
                        return 0
                    c = self.skip_white_spaces(self.dbase_parser)
                    if c == '(':
                        genv.text_code += c
                        continue
                    elif c.isnumeric():
                        self.token_str = c
                        self.getNumber()
                        genv.text_code += self.token_str
                        continue
                    elif c.isalpha() or c == '_':
                        self.token_str = c
                        self.getIdent(c)
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
                elif c == ')':
                    genv.text_code += c
                    continue
            elif c.isalpha() or c == '_':
                self.token_str = c
                self.getIdent(c)
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
                c = self.skip_white_spaces(self.dbase_parser)
                if c == genv.ptNoMoreData:
                    raise e_no_more_data();
                    return
                elif c.isalpha():
                    self.getIdent(c)
                    if self.token_str.lower() == "parameter":
                        self.temp_code = ""
                        while True:
                            c = self.skip_white_spaces(self.dbase_parser)
                            if c == genv.ptNoMoreData:
                                raise e_no_more_data();
                            elif c.isalpha():
                                self.getIdent(c)
                                if self.token_str.lower() in genv.dbase_keywords:
                                    genv.have_errors = True
                                    genv.unexpectedError(_("keywords can not be used as variable"))
                                    return
                                genv.temp_code += self.token_str
                                c = self.skip_white_spaces(self.dbase_parser)
                                if c == genv.ptNoMoreData:
                                    raise e_no_more_data();
                                elif c == ',':
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
                        showInfo("lokaler " + self.token_str + "\n>" + str(c))
                        genv.text_code += ('\t' * genv.counter_indent)
                        while True:
                            c = self.skip_white_spaces(self.dbase_parser)
                            if c == genv.ptNoMoreData:
                                raise e_no_more_data();
                            if c.isalpha():
                                self.getIdent(c)
                                if self.token_str.lower() in genv.dbase_keywords:
                                    genv.have_errors = True
                                    genv.unexpectedError(_("keywords can not be used as variable"))
                                    return
                                genv.text_code += self.token_str
                                c = self.skip_white_spaces(self.dbase_parser)
                                if c == genv.ptNoMoreData:
                                    raise e_no_more_data();
                                elif c == ',':
                                    genv.text_code += ","
                                    continue
                                else:
                                    self.ungetChar(1)
                                    genv.text_code += " = None\n"
                                    break
                        showInfo("local:\n" + genv.text_code)
                        #showInfo("parss: "  + self.token_str + "\n>" + str(c))
                        continue
                    elif self.token_str.lower() == "if":
                        genv.text_code += "if "
                        self.dbase_expr()
                        
                        genv.text_code += '\n'
                        
                        showInfo("if: ------\n" + genv.text_code)
                    elif self.token_str.lower() == "else":
                        genv.text_code += "\relse:\r\t"
                        c = self.skip_white_spaces(self.dbase_parser)
                        if c == genv.ptNoMoreData:
                            raise e_no_more_data()
                        elif c.isalpha():
                            self.getIdent(c)
                            genv.text_code += ('\t' * genv.counter_indent)
                            genv.text_code += self.token_str
                            c = self.skip_white_spaces(self.dbase_parser)
                            if c == genv.ptNoMoreData:
                                raise e_no_more_data();
                            elif c == '.':
                                genv.text_code += "."
                                c = self.skip_white_spaces(self.dbase_parser)
                                if c == genv.ptNoMoreData:
                                    raise e_no_more_data();
                                if c.isalpha():
                                    self.getIdent(c)
                                    if self.token_str.lower() == "open":
                                        genv.text_code += "open"
                                        c = self.skip_white_spaces(self.dbase_parser)
                                        if c == genv.ptNoMoreData:
                                            raise e_no_more_data();
                                        elif c == '(':
                                            genv.text_code += "("
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if c == genv.ptNoMoreData:
                                                raise e_no_more_data();
                                            elif c == ')':
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
                            elif c == '(':
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
                        self.check_token_ident(c)
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
                        elif c == '=':
                            showInfo("===\n" + genv.text_code)
                            genv.text_code += " = "
                            c = self.skip_white_spaces(self.dbase_parser)
                            if c == genv.ptNoMoreData:
                                genv.have_errors = True
                                raise e_no_more_data();
                            elif c.isalpha() or c == '_':
                                self.getIdent(c)
                                if self.token_str.lower() == "new":
                                    showInfo("new er")
                                    c = self.skip_white_spaces(self.dbase_parser)
                                    if c == genv.ptNoMoreData:
                                        genv.have_errors = True
                                        genv.unexpectedError(_("new expected."))
                                        return
                                    elif c.isalpha() or c == '_':
                                        self.getIdent(c)
                                        if self.token_str.lower() in genv.dbase_keywords:
                                            genv.have_errors = True
                                            genv.unexpectedError(_("keywords not allowed there"))
                                            return
                                        genv.text_code += self.token_str
                                        c = self.skip_white_spaces(self.dbase_parser)
                                        if c == genv.ptNoMoreData:
                                            genv.have_errors = True
                                            genv.unexpectedError(_("open paren expected."))
                                            return
                                        elif c == '(':
                                            genv.text_code += '('
                                            c = self.skip_white_spaces(self.dbase_parser)
                                            if c == genv.ptNoMoreData:
                                                genv.have_errors = True
                                                genv.unexpectedError(_("open paren expected."))
                                                return
                                            elif c == ')':
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
    
    def check_token_no_more_data(self, message=""):
        if genv.char_curr == genv.ptNoMoreData:
            genv.have_errors = True
            raise e_no_more_data(message)
        else:
            return False
    
    def check_point(self):
        c = self.check_token_no_more_data(_("check point"))
        if c == '.':
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
        else:
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
        c = self.skip_white_spaces(self.dbase_parser)
        if c.isalpha():
            self.token_str = c
            c = self.getChar()
            if c == '+':
                self.token_str += c
                fg_color = self.token_str
                if self.token_str in genv.concolors:
                    index    = genv.concolors.index(self.token_str)
                    fg_color = genv.convalues[index]
                    fg_found = True
                c = self.skip_white_spaces(self.dbase_parser)
                if c == '/':
                    c = self.skip_white_spaces(self.dbase_parser)
                    if c.isalpha():
                        self.token_str = c
                        c = self.getChar()
                        if c == '+':
                            self.token_str += c
                        elif c.isalpha():
                            self.token_str += c
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
            elif c == '/':
                fg_color = self.token_str
                if self.token_str in genv.concolors:
                    index    = genv.concolors.index(self.token_str)
                    fg_color = genv.convalues[index]
                    fg_found = True
                c = self.skip_white_spaces(self.dbase_parser)
                if c.isalpha():
                    self.token_str = c
                    c = self.getChar()
                    if c == '+':
                        self.token_str += c
                    elif c.isalpha():
                        self.token_str += c
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
            elif c.isalpha():
                self.token_str += c
                fg_color = self.token_str
                if self.token_str in genv.concolors:
                    index    = genv.concolors.index(self.token_str)
                    fg_color = genv.convalues[index]
                    fg_found = True
                    c = self.skip_white_spaces(self.dbase_parser)
                    if c == '/':
                        c = self.skip_white_spaces(self.dbase_parser)
                        if c.isalpha() or c == '_':
                            self.getIdent(c)
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
        try:
            genv.counter_digits = 0
            genv.counter_indent = 1
            genv.counter_for    = 0
            genv.counter_brace  = 0
            
            genv.first_part  = False
            genv.second_part = False
            
            genv.line_row  = 1
            genv.line_col  = 1
            
            self.counter_begin = 0
            self.counter_end   = 0
            
            if len(self.source) < 1:
                genv.unexpectedError(_("no data available."))
                return
            
            self.token_str = ""            
            self.found = False
            
            ident_name = ""
            
            c = self.skip_white_spaces(self.pascal_parser)
            if c == genv.ptNoMoreData:
                raise e_no_more_data()
                return
            elif c.isalpha():
                self.getIdent(c)
                if self.token_str.lower() == "program":
                    pass
                elif self.token_str.lower() == "unit":
                    pass
                elif self.token_str.lower() == "library":
                    pass
                    
                c = self.skip_white_spaces(self.pascal_parser)
                if c == genv.ptNoMoreData:
                    raise e_no_more_data()
                    return
                elif c.isalpha():
                    self.getIdent(c)
                    ident_name = self.token_str
                    self.token_str = ""
                
                if len(ident_name) > 0:
                    c = self.skip_white_spaces(self.pascal_parser)
                    if c == genv.ptNoMoreData:
                        raise e_no_more_data()
                        return
                    if not c == ';':
                        genv.have_errors = True
                        genv.unexpectedError(_("semicolon expected"))
                        return
                else:
                    genv.have_errors = True
                    genv.unexpectedError(_("module ident name expected."))
                    return
                    
                c = self.skip_white_spaces(self.pascal_parser)
                if c == genv.ptNoMoreData:
                    raise e_no_more_data()
                    return
                elif c.isalpha():
                    self.getIdent(c)
                    
                    if self.token_str.lower() == "interface":
                        pass
                    self.handle_pascal_code(self.token_str.lower())
                else:
                    genv.have_errors = True
                    genv.unexpectedError(_("alpha ident expected"))
                    return
            else:
                genv.have_errors = True
                genv.unexpectedError(_("alpha ident expected"))
                return
        except e_no_more_data as noerr:
            showInfo("A no Error Exception")
    
    def handle_pascal_code(self, token):
        self.ungetChar(len(self.token_str)+1)
        while True:
            c = self.skip_white_spaces(self.pascal_parser)
            if c == genv.ptNoMoreData:
                raise e_no_more_data()
                return
            elif c.isalpha():
                self.getIdent(c)
                if self.token_str.lower() == "procedure":
                    c = self.skip_white_spaces(self.pascal_parser)
                    if c == genv.ptNoMoreData:
                        raise e_no_more_data()
                        return
                    if c.isalpha():
                        self.getIdent(c)
                        ident_name = self.token_str
                        c = self.skip_white_spaces(self.pascal_parser)
                        if c == genv.ptNoMoreData:
                            raise e_no_more_data()
                            return
                        if c == '(':
                            c = self.skip_white_spaces(self.pascal_parser)
                            if c == genv.ptNoMoreData:
                                raise e_no_more_data()
                                return
                            elif c == ')':
                                c = self.skip_white_spaces(self.pascal_parser)
                                if c == genv.ptNoMoreData:
                                    raise e_no_more_data()
                                    return
                                elif c == ';':
                                    c = self.skip_white_spaces(self.pascal_parser)
                                    if c == genv.ptNoMoreData:
                                        raise e_no_more_data()
                                        return
                                    elif c.isalpha():
                                        self.getIdent(c)
                                        if self.token_str == "var":
                                            pass
                                        elif self.token_str == "begin":
                                            c = self.skip_white_spaces(self.pascal_parser)
                                            if c == genv.ptNoMoreData:
                                                raise e_no_more_data()
                                                return
                                            elif c.isalpha():
                                                self.getIdent(c)
                                                if self.token_str == "end":
                                                    c = self.skip_white_spaces(self.pascal_parser)
                                                    if c == genv.ptNoMoreData:
                                                        raise e_no_more_data()
                                                        return
                                                    elif c == ';':
                                                        continue
                                                    else:
                                                        genv.have_errors = True
                                                        genv.unexpectedError(_("semicolon expected"))
                                                        return
                                                else:
                                                    genv.have_errors = True
                                                    genv.unexpectedError(_("END expected"))
                                                    return
                                            else:
                                                genv.have_errors = True
                                                genv.unexpectedError(_("alpha ident expected"))
                                                return
                                        else:
                                            genv.have_errors = True
                                            genv.unexpectedError(_("BEGIN, VAR expected"))
                                            return
                                    else:
                                        genv.have_errors = True
                                        genv.unexpectedError(_("alpha ident expected"))
                                        return
                                else:
                                    genv.have_errors = True
                                    genv.unexpectedError(_("semicolon expected"))
                                    return
                            else:
                                genv.have_errors = True
                                genv.unexpectedError(_("closed paren expected"))
                                return
                        else:
                            genv.have_errors = True
                            genv.unexpectedError(_("open paren expected"))
                            return
                    else:
                        genv.have_errors = True
                        genv.unexpectedError(_("alpha ident expected"))
                        return
                        
                elif self.token_str.lower() == "function":
                    c = self.skip_white_spaces(self.pascal_parser)
                    if c == genv.ptNoMoreData:
                        raise e_no_more_data()
                        return
                    elif c.isalpha():
                        self.getIdent(c)
                        ident_name = self.token_str
                        c = self.skip_white_spaces(self.pascal_parser)
                        if c == genv.ptNoMoreData:
                            raise e_no_more_data()
                            return
                        elif c == '(':
                            c = self.skip_white_spaces(self.pascal_parser)
                            if c == genv.ptNoMoreData:
                                raise e_no_more_data()
                                return
                            elif c == ')':
                                c = self.skip_white_spaces(self.pascal_parser)
                                if c == genv.ptNoMoreData:
                                    raise e_no_more_data()
                                    return
                                elif c == ':':
                                    c = self.skip_white_spaces(self.pascal_parser)
                                    if c == genv.ptNoMoreData:
                                        raise e_no_more_data()
                                        return
                                    elif c.isalpha():
                                        self.getIdent(c)
                                        resultName = self.token_str
                                        c = self.skip_white_spaces(self.pascal_parser)
                                        if c == genv.ptNoMoreData:
                                            raise e_no_more_data()
                                            return
                                        elif c == ';':
                                            c = self.skip_white_spaces(self.pascal_parser)
                                            if c == genv.ptNoMoreData:
                                                raise e_no_more_data()
                                                return
                                            elif c.isalpha():
                                                self.getIdent(c)
                                                if self.token_str == "var":
                                                    pass
                                                elif self.token_str == "begin":
                                                    c = self.skip_white_spaces(self.pascal_parser)
                                                    if c == genv.ptNoMoreData:
                                                        raise e_no_more_data()
                                                        return
                                                    elif c.isalpha():
                                                        self.getIdent(c)
                                                        if self.token_str == "end":
                                                            c = self.skip_white_spaces(self.pascal_parser)
                                                            if c == genv.ptNoMoreData:
                                                                raise e_no_more_data()
                                                                return
                                                            elif c == ';':
                                                                continue
                                                            else:
                                                                genv.have_errors = True
                                                                genv.unexpectedError(_("semicolon expected"))
                                                                return
                                                        else:
                                                            genv.have_errors = True
                                                            genv.unexpectedError(_("END expected"))
                                                            return
                                                    else:
                                                        genv.have_errors = True
                                                        genv.unexpectedError(_("alpha ident expected"))
                                                        return
                                                else:
                                                    genv.have_errors = True
                                                    genv.unexpectedError(_("BEGIN, VAR expected"))
                                                    return
                                            else:
                                                genv.have_errors = True
                                                genv.unexpectedError(_("alpha ident expected"))
                                                return
                                        else:
                                            genv.have_errors = True
                                            genv.unexpectedError(_("semicolon expected"))
                                            return
                                    else:
                                        genv.have_errors = True
                                        genv.unexpectedError(_("alpha ident expected"))
                                        return
                                else:
                                    genv.have_errors = True
                                    genv.unexpectedError(_("colom expected"))
                                    return
                            else:
                                genv.have_errors = True
                                genv.unexpectedError(_("closed paren expected"))
                                return
                        else:
                            genv.have_errors = True
                            genv.unexpectedError(_("open paren expected"))
                            return
                    else:
                        genv.have_errors = True
                        genv.unexpectedError(_("alpha ident expected"))
                        return
                
                elif self.token_str.lower() == "begin":
                    c = self.skip_white_spaces(self.pascal_parser)
                    if c == genv.ptNoMoreData:
                        raise e_no_more_data()
                        return
                    elif c.isalpha():
                        self.getIdent(c)
                        if self.token_str.lower() == "end":
                            c = self.skip_white_spaces(self.pascal_parser)
                            if not c == '.':
                                genv.have_errors = True
                                genv.unexpectedError(_("end-point expected"))
                                return
                            else:
                                raise e_no_more_data()
                                return
                        else:
                            genv.have_errors = True
                            genv.unexpectedError(_("END expected"))
                            return
                    else:
                        genv.have_errors = True
                        genv.unexpectedError(_("alpha ident expected"))
                        return
                else:
                    genv.have_errors = True
                    genv.unexpectedToken(self.token_str)
                    return
            else:
                genv.have_errors = True
                genv.unexpectedToken(self.token_str)
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

class interpreter_Lisp(interpreter_base):
    def __init__(self, file_name):
        super(interpreter_Lisp, self).__init__(file_name)
    
    def skip_white_spaces(self):
        while True:
            c = self.getChar()
            if c == genv.ptNoMoreData:
                return c
            elif c == '\n':
                continue
            elif c == '\r':
                c = self.getChar()
                if not c == '\n':
                    genv.have_errors = True
                    genv.unexpectedError(_("line end error"))
                continue
            elif c == ';':
                showInfo("lisp comment: " + str(genv.line_row))
                while True:
                    c = self.getChar()
                    if c == '\n':
                        break
                    elif c == '\r':
                        c = self.getChar()
                        if not c == '\n':
                            genv.have_errors = True
                            genv.unexpectedError(_("line end error"))
                        break
                    else:
                        continue
                continue
            elif c == ' ' or c == '\t':
                continue
            else:
                return c
    
    def handle_defun_head(self):
        while True:
            c = self.skip_white_spaces()
            if c == genv.ptNoMoreData:
                genv.have_errors = True
                genv.unexpectedError(_("syntax error."))
                return
            elif c.isalpha():
                return c
            elif c == '(':
                while True:
                    c = self.skip_white_spaces()
                    if c == genv.ptNoMoreData:
                        genv.have_errors = True
                        genv.unexpectedError(_("syntax error"))
                        return
                    elif c == ')':
                        break
                    else:
                        continue
                break
            else:
                genv.have_errors = True
                genv.unexpectedError(_("open paren expected at defun."))
                return
    
    def parse(self):
        genv.line_col = 1
        genv.line_row = 1
        #
        open_paren    = 0
        while True:
            c = self.skip_white_spaces()
            if c == genv.ptNoMoreData:
                return c
            elif c.isalpha():
                self.getIdent(c)
                if self.token_str.lower() == "defun":
                    showInfo("a defune")
                    c = self.skip_white_spaces()
                    if c == genv.ptNoMoreData:
                        genv.have_errors = True
                        genv.unexpectedError(_("syntax error."))
                        return
                    elif c.isalpha():
                        self.getIdent(c)
                        self.handle_defun_head()
                        continue
            elif c == '(':
                open_paren += 1
                showInfo("((((( 1111")
                c = self.skip_white_spaces()
                if c == '(':
                    showInfo("3333 )))))")
                    open_paren += 1
                    continue
                elif c == ')':
                    showInfo("2222 )))))")
                    open_paren -= 1
                    if open_paren < 1:
                        break
                    continue
                elif c == genv.ptNoMoreData:
                    if open_paren > 0:
                        genv.have_errors = True
                        genv.unexpectedError(_("closed1 paren expected."))
                        return
                    return c
                else:
                    genv.have_errors = True
                    genv.unexpectedError(_("closed2 paren expected."))
                    return
            elif c == ')':
                showInfo(")))))) 000")
                open_paren -= 1
                if open_paren >= 0:
                    continue
                else:
                    genv.have_errors = True
                    genv.unexpectedError(_("open paren expected."))
                    return
            else:
                genv.have_errors = True
                genv.unexpectedError(_("unknown char. found"))
                return

class lispDSL():
    def __init__(self, script_name):
        self.script = None
        
        self.parser = None
        self.parser = interpreter_Lisp(script_name)
        self.parser.parse()

class interpreter_C64(interpreter_base):
    def __init__(self, file_name):
        super(interpreter_C64, self).__init__(file_name)
        
    def parse(self):
        self.token_str = ""

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
            c = self.source[self.pos]
            return c
    
    def ungetChar(self, num):
        genv.line_col -= num;
        self.pos -= num;
        c = self.source[self.pos]
        return c
    
    def getIdent(self, ch):
        self.token_str = ch
        while True:
            c = self.getChar()
            if c.isalnum() or c == '_':    # 0-9 todo
                self.token_str += c
                continue
            elif c == '\t' or c == ' ':
                continue
            elif c == '\r':
                c = self.getChar()
                if not c == '\n':
                    genv.unexpectedToken("newline")
                    return 0
                genv.line_col  = 1
                genv.line_row += 1
                break
            elif c == '\n':
                genv.line_col  = 1
                genv.line_row += 1
                break
            elif c == '=':
                self.ungetChar(1)
                break
            else:
                genv.unexpectedChar(c)
                return 0
        return self.token_str
    
    def getNumber(self):
        while True:
            c = self.getChar()
            if c in genv.octal_digits:
                self.token_str += octal_to_ascii(c)
            else:
                self.ungetChar(1)
                return self.token_str
    
    # -----------------------------------------------------------------------
    # \brief skip all whitespaces. whitespaces are empty lines, lines with
    #        one or more spaces (0x20): " ", \t, "\n".
    # -----------------------------------------------------------------------
    def skip_white_spaces(self):
        while True:
            c = self.getChar()
            if c == '\0':
                return '\0'
            elif c == "\t" or c == " ":
                genv.line_col += 1
                continue
            elif c == "\r":
                c = self.getChar()
                if not c == "\n":
                    genv.unexpectedEndOfLine(genv.line_row)
                genv.line_col  = 1
                genv.line_row += 1
                continue
            elif c == '\n':
                genv.line_col  = 1
                genv.line_row += 1
                continue
            elif c == '#':
                while True:
                    c = self.getChar()
                    if c == '\r':
                        c = self.getChar()
                        if not c == '\n':
                            genv.unexpectedToken("newline")
                            return 0
                        genv.line_col  = 1
                        genv.line_row += 1
                        break
                    elif c == "\n":
                        genv.line_col  = 1
                        genv.line_row += 1
                        break
                continue
            else:
                return c
    
    # -----------------------------------------------------------------------
    # \brief parse a one line comment: // for c++, ** and && for dBase ...
    # -----------------------------------------------------------------------
    def handle_oneline_comment(self):
        while True:
            c = self.getChar()
            if c == '\r':
                c = self.getChar()
                if not c == '\n':
                    genv.unexpectedToken("newline")
                    return 0
                genv.line_row += 1
                genv.line_col  = 1
                break
            if c == "\n":
                genv.line_row += 1
                genv.line_col  = 1
                break
    
    def parse(self):
        if len(self.source) < 1:
            print("no data available.")
            return
        
        while True:
            c = self.getChar()
            if c.isalpha() or c == '_':
                self.getIdent(c)
                print("token: ", self.token_str)
                if self.check_token():
                    print("OK")
            elif c == '\r':
                c = self.getChar()
                if not c == '\n':
                    genv.unexpectedToken("newline")
                    return 0
                genv.line_row += 1
                genv.line_col  = 1
                continue
            elif c == '\n':
                genv.line_row += 1
                genv.line_col  = 1
                continue
            elif c == '\t' or c == ' ':
                continue
            elif c == '#':
                self.handle_oneline_comment()
    
    def getConfigLine(self):
        self.token_str = ""
        self.close_str = False
        while True:
            c = self.getChar()
            if c == '"':
                while True:
                    c = self.getChar()
                    if c == '"':
                        self.close_str = True
                        break
                    elif c == '\r':
                        c = self.getChar()
                        if not c == '\n':
                            genv.unexpectedToken("newline")
                            return 0
                        else:
                            if self.close_str == False:
                                genv.unexpectedToken(_("string not terminated."))
                                return 0
                            genv.line_col  = 1
                            genv.line_row += 1
                            break
                    elif c == '\n':
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
            elif c == '\t' or c == ' ':
                genv.line_col += 1
                continue
            elif c == '\r':
                c = self.getChar()
                if not c == '\n':
                    genv.unexpectedToken("newline")
                    return 0
                genv.line_col  = 1
                genv.line_row += 1
                break
            elif c == '\n':
                genv.line_col  = 1
                genv.line_row += 1
                break
            elif c.isdigit():
                self.token_str += c
                continue
            elif c.isalpha():
                self.token_str += c
                while True:
                    c = self.getChar()
                    if c.isalpha():
                        self.token_str += c
                        continue
                    elif c.isdigit():
                        self.token_str += c
                        continue
                    elif c == '\t' or c == ' ':
                        continue
                    elif c == '\r':
                        c = self,getChar()
                        if not c == '\n':
                            genv.unexpectedToken("newline")
                            return 0
                        genv.line_col  = 1
                        genv.line_row += 1
                        break
                    elif c == '\n':
                        genv.line_col  = 1
                        genv.line_row += 1
                        break
                if c == '\n':
                    break
            else:
                genv.unexpectedToken("qoute")
                return 0
    
    def check_token(self):
        res = json.loads(_("doxytoken"))
        result = False
        if self.token_str in res:
            print(f"token: {self.token_str} is okay.")
            result = True
            c = self.getChar()
            if c == '=':
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
            print("\nend of data")
            chm = createHTMLproject()
    
    def parse(self):
        return
    
    def run(self):
        return

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
def showApplicationInformation(text):
    if isApplicationInit() == False:
        genv.v__app_object = QApplication(sys.argv)
        showInfo(text)
    else:
        print(text)

# ------------------------------------------------------------------------
# methode to show error about this application script ...
# ------------------------------------------------------------------------
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
        print("no ption error")
        #genv.v__app__locales = os.path.join(genv.v__app__locales, genv.v__locale__sys[0])
        #genv.v__app__locales = os.path.join(genv.v__aoo__locales, "LC_MESSAGES")
        #genv.v__app__locales = os.path.join(genv.v__app__locales, genv.v__app__name_mo)
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
        print(("-"*40))
        #
        print(f"file : {tb.filename}")
        print(f"line : {tb.lineno}")
        #
        print(("-"*40))
        
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
            print(e)

# ------------------------------------------------------------------------
#
# ------------------------------------------------------------------------
class myLineEdit(QLineEdit):
    def __init__(self, name="", name_object=""):
        super().__init__()
        
        if name_object:
            self.setObjectName(name_object)
            #register_instance(self, name_object)
            #print(">> " + self.objectName())
        
        self.name = name
        self.init_ui()
    
    def init_ui(self):
        self.setMinimumHeight(26)
        self.setMaximumWidth(250)
        self.setText(self.name)
        self.cssColor = _("edit_css")
        self.setStyleSheet(self.cssColor)

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
            parent_array = [
                parent.help_tabs,
                parent.dbase_tabs,
                parent.pascal_tabs,
                parent.isoc_tabs,
                parent.java_tabs,
                parent.python_tabs,
                parent.javascript_tabs,
                parent.prolog_tabs,
                parent.lisp_tabs,
                parent.locale_tabs,
                parent.console_tabs,
                parent.todo_tabs,
                parent.setup_tabs,
                parent.certssl_tabs,
                parent.github_tabs,
                parent.apache_tabs,
                parent.mysql_tabs,
                parent.squid_tabs,
                parent.electro_tabs,
                parent.c64_tabs,
                parent.settings_tabs
            ]
            self.btn_clicked(self.parent,
                parent_array[self.mode])
    
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
        parent.javascript_tabs.hide()
        parent.prolog_tabs.hide()
        parent.lisp_tabs.hide()
        parent.locale_tabs.hide()
        parent.console_tabs.hide()
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
        ]
        for btn in side_buttons:
            btn.state = 0
            btn.set_style()

class myIconButton(QWidget):
    def __init__(self, parent, mode, label_text, text):
        super().__init__()
        
        genv.v__app__devmode = mode
        
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
            genv.v__app__pythonc__,
            genv.v__app__javascr__,
            genv.v__app__prologm__,
            genv.v__app__lispmod__,
            genv.v__app__locales__,
            genv.v__app__console__,
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
        self.helpText   = helpText
        
        self.helpToken  = _("A" + f"{helpID:04X}")
        self.helpAnchor = 'https://doxygen.nl/manual/config.html#cfg_' + self.helpToken.lower()
    
    def enterEvent(self, event):
        genv.sv_help.setText(self.helpText)
    
    def mousePressEvent(self, event):
        QApplication.setOverrideCursor(Qt.PointingHandCursor)
        return
    
    def mouseReleaseEvent(self, event):
        QDesktopServices.openUrl(QUrl(self.helpAnchor))
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        return

class myCustomScrollArea(QScrollArea):
    def __init__(self, parent, number, name):
        super().__init__()
        #print(name)
        
        self.number = number
        self.name   = name
        self.font   = QFont(genv.v__app__font)
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
    
    def addCheckBox(self, object_name = "", text = "", bold=False):
        w = QCheckBox(text)
        w.setObjectName(object_name + ':QCheckBox')
        
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
    
    def addComboBox(self, object_name = ""):
        w = QComboBox()
        w.setObjectName(object_name + ':QComboBox')
        self.layout.addWidget(w)
        return w
    
    def addLineEdit(self, object_name = "", text = "", lh = None):
        w = myLineEdit(text, object_name)
        w.setMinimumHeight(21)
        w.setFont(self.font_a)
        if not lh == None:
            lh.addWidget(w)
        else:
            self.layout.addWidget(w)
        return w
    
    def addElements(self, number, elements, hid):
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
                w = self.addLineEdit(tokennum, "",lh_0)
                w.setObjectName(tokennum + ':' + str(number))
                genv.DoxyGenElementLayoutList.append(w)
                
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
                vw_2 = self.addCheckBox(tokennum, "", False)
                vw_2.setMinimumHeight(21)
                vw_2.setFont(self.font_a)
                vw_2.setChecked(elements[i][3])
                lh_0.addWidget(vw_2)
            
            elif elements[i][1] == self.type_combo_box:
                vw_2 = self.addComboBox(tokennum)
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
    def __init__(self, parent, name="uuuu"):
        super(customScrollView_1, self).__init__(parent, 1, name)
        
        self.parent = parent
        self.name   = name
        
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
        
        e_field_1 = self.addLineEdit("PROJECT_NAME:1"  , "", v_layout_2)
        e_field_2 = self.addLineEdit("PROJECT_AUTHOR:1", "", v_layout_2)
        e_field_3 = self.addLineEdit("PROJECT_NUMBER:1", "", v_layout_2)
        
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
        #
        widget_4_licon_1 = self.addLabel("", False, layout_4)
        widget_4_licon_1.setPixmap(QIcon(os.path.join(
            genv.v__app__img__int__,
            "floppy-disk" + genv.v__app__img_ext__)).pixmap(42,42))
        widget_4_licon_1.setObjectName("PROJECT_LOGO:1")
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
        widget_6_edit_1  = self.addLineEdit("SOURCE_DIR:1",
            os.path.join(genv.v__app__app_dir__, "/examples/doxygen/"),
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
        ##
        layout.addLayout(layout_6)
        
        layout_7 = QHBoxLayout()
        layout_7.setAlignment(Qt.AlignLeft)
        widget_7_label_1 = self.addLabel(_("Destination dir:"), False, layout_7)
        widget_7_label_1.setMinimumWidth(100)
        widget_7_label_1.setMaximumWidth(100)
        widget_7_label_1.setFont(font)
        #
        widget_7_edit_1  = self.addLineEdit("DEST_DIR:1","E:/temp/src/html", layout_7)
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
        widget_9_checkbutton_1 = self.addCheckBox(" ",_("Scan recursive"))
        widget_9_checkbutton_1.setMaximumWidth(300)
        widget_9_checkbutton_1.setFont(font)
        layout_9.addWidget(widget_9_checkbutton_1)
        layout.addLayout(layout_9)
        
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
            return
        if len(genv.doxygen_project_file) < 2:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText(_("no project file given."))
            msg.setIcon(QMessageBox.Warning)
            msg.setStyleSheet(_("msgbox_css"))
            
            btn_ok = msg.addButton(QMessageBox.Ok)
            result = msg.exec_()            
            return
        
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
    def __init__(self, parent, name):
        super(customScrollView_2, self).__init__(parent, 2, name)
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        
        label_2 = self.addLabel(_("opti00"), True)
        label_2.setMinimumHeight(30)
        label_2.setMinimumWidth(200)
        
        self.addRadioButton(_("opti01"))
        self.addRadioButton(_("opti02"))
        self.addCheckBox   (" ",_("opti03"))
        
        self.addFrame()
        
        self.addLabel("Select programming language to optimize the results for:", True)
        
        for x in range(2,9):
            self.addRadioButton(_("opti0" + str(x+1)))

# ------------------------------------------------------------------------
# create a scroll view for the output tab on left side of application ...
# ------------------------------------------------------------------------
class customScrollView_3(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_3, self).__init__(parent, 3, name)
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        
        self.addLabel(_("Select the output format(s) to generate:"), True)
        
        # HTML
        self.addCheckBox(" ","HTML", True)
        #
        self.addRadioButton(_("plain HTML"))
        self.addRadioButton(_("with navigation Panel"))
        self.addRadioButton(_("prepare for compressed HTML .chm"))
        self.addCheckBox(" ",_("with search function"))
        
        self.addFrame()
        
        # LaTeX
        self.addCheckBox(" ","LaTeX", True)
        #
        self.addRadioButton(_("an intermediate format for hyper-linked PDF"))
        self.addRadioButton(_("an intermediate format for PDF"))
        self.addRadioButton(_("an intermediate format for PostScript"))
        
        self.addFrame()
        
        # misc
        self.addCheckBox(" ","Man pages")
        self.addCheckBox(" ","Rich Text Format - RTF")
        self.addCheckBox(" ","XML")
        self.addCheckBox(" ","DocBook")

# ------------------------------------------------------------------------
# create a scroll view for the diagrams tab on left side of application ...
# ------------------------------------------------------------------------
class customScrollView_4(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_4, self).__init__(parent, 4, name)
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        
        self.addLabel(_("Diagrams to generate:"), True)
        
        self.addRadioButton(_("No diagrams"))
        self.addRadioButton(_("Text only"))
        self.addRadioButton(_("Use built-in diagram generator"))
        self.addRadioButton(_("Use Dot-Tool from the GrappVz package"))
        
        self.addFrame()
        
        self.addLabel(_("Dot graphs to generate:"), True)
        
        check_array = [
            _("Class graph"),
            _("Colaboration diagram"),
            _("Overall Class hiearchy"),
            _("Include dependcy graphs"),
            _("Included by dependcy graphs"),
            _("Call graphs"),
            _("Called-by graphs")
        ]
        for chk in check_array:
            self.addCheckBox(" ", chk)

class customScrollView_5(myCustomScrollArea):
    def __init__(self, parent, name):
        super().__init__(parent, 5, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(2000)
        
        ## 0xA0100
        label_5_elements = eval(_("label_5_elements"))
        self.addElements(5, label_5_elements, 0x100)
    
    # ----------------------------------------------
    # show help text when mouse move over the label
    # ----------------------------------------------
    def label_enter_event(self, text):
        genv.sv_help.setText(text)

class customScrollView_6(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_6, self).__init__(parent, 6, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1400)
        
        ## 0xA0200
        label_6_elements = eval(_("label_6_elements"))
        self.addElements(6, label_6_elements, 0x200)

class customScrollView_7(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_7, self).__init__(parent, 7, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA0300
        label_7_elements = eval(_("label_7_elements"))
        self.addElements(7, label_7_elements, 0x0300)

class customScrollView_8(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_8, self).__init__(parent, 8, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1700)
        
        ## 0xA0400
        label_8_elements = eval(_("label_8_elements"))
        self.addElements(8, label_8_elements, 0x0400)

class customScrollView_9(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_9, self).__init__(parent, 9, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(560)
        
        ## 0xA0500
        label_9_elements = eval(_("label_9_elements"))
        self.addElements(9, label_9_elements, 0x0500)

class customScrollView_10(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_10, self).__init__(parent, 10, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA0600
        label_10_elements = [
            [0xA0601, self.type_check_box, 0, True ],
            [0xA0602, self.type_edit,      3 ]
        ]
        self.addElements(10, label_10_elements, 0x0600)

class customScrollView_11(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_11, self).__init__(parent, 11, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(2380)
        
        ## 0xA0700
        label_11_elements = eval(_("label_11_elements"))
        self.addElements(11, label_11_elements, 0x0700)

class customScrollView_12(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_12, self).__init__(parent, 12, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1000)
        
        ## 0xA0800
        label_12_elements = eval(_("label_12_elements"))
        self.addElements(12, label_12_elements, 0x0800)

class customScrollView_13(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_13, self).__init__(parent, 13, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA0900
        label_13_elements = eval(_("label_13_elements"))
        self.addElements(13, label_13_elements, 0x0900)

class customScrollView_14(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_14, self).__init__(parent, 14, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1000
        label_14_elements = eval(_("label_14_elements"))
        self.addElements(14, label_14_elements, 0x1000)

class customScrollView_15(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_15, self).__init__(parent, 15, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1100
        label_15_elements = eval(_("label_15_elements"))
        self.addElements(15, label_15_elements, 0x1100)

class customScrollView_16(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_16, self).__init__(parent, 16, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1400)
        
        ## 0xA1200
        label_16_elements = [
            [0xA1201, self.type_check_box, 0, False ],
            [0xA1202, self.type_edit,      1 ],
        ]
        self.addElements(16, label_16_elements, 0x1200)

class customScrollView_17(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_17, self).__init__(parent, 17, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1300
        label_17_elements = [
            [0xA1301,  self.type_check_box, 0, False ]
        ]
        self.addElements(17, label_17_elements, 0x1300)

class customScrollView_18(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_18, self).__init__(parent, 18, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1400
        label_18_elements = [
            [0xA1401, self.type_check_box, 0, False ],
            [0xA1402, self.type_edit,      1 ],
            [0xA1403, self.type_check_box, 0, True  ],
        ]
        self.addElements(18, label_18_elements, 0x1400)

class customScrollView_19(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_19, self).__init__(parent, 19, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1500
        label_19_elements = eval(_("label_19_elements"))
        self.addElements(19, label_19_elements, 0x1500)

class customScrollView_20(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_20, self).__init__(parent, 20, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(800)
        
        ## 0xA1600
        label_20_elements = eval(_("label_20_elements"))
        self.addElements(20, label_20_elements, 0x1600)

class customScrollView_21(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_21, self).__init__(parent, 21, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1700
        label_21_elements = eval(_("label_21_elements"))
        self.addElements(21, label_21_elements, 0x1700)

class customScrollView_22(myCustomScrollArea):
    def __init__(self, parent, name):
        super(customScrollView_22, self).__init__(parent, 22, name)
        self.setStyleSheet(_("ScrollBarCSS"))
        self.init_ui()
    
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1800)
        
        ## 0xA1800
        label_22_elements = eval(_("label_22_elements"))
        self.addElements(22, label_22_elements, 0x1800)

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
                genv.doc_project = "doxygen"
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
                genv.doc_project = ""
            genv.HelpAuthoringConverterMode = 1
            print("doxygen")
    
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
                genv.doc_project = "helpndoc"
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
                genv.doc_project = ""
            genv.HelpAuthoringConverterMode = 2
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
                self.btn_img_fg = os.path.join(genv.v__app__img__int__, img + "1" + genv.v__app__img_ext__)
                self.btn_img_bg = os.path.join(genv.v__app__img__int__, img + "2" + genv.v__app__img_ext__)
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
        print("doxy")
        genv.project_type = "doxygen"
        return True
    
    def on_help_clicked(self):
        print("help")
        genv.project_type = "helpndoc"
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
        
            genv.project_type = genv.v__app__config.get("common", "type")
        except configparser.NoOptionError as error:
            MyProjectOption()
        
        if genv.project_type.lower() == "doxygen":
            genv.doc_project = "doxygen"
            self.parent.trigger_mouse_press(genv.img_doxygen)
        elif genv.project_type.lower() == "helpndoc":
            genv.doc_project = "helpndoc"
            self.parent.trigger_mouse_press(genv.img_hlpndoc)
        else:
            showInfo(_("Error: help framework not known."))
            return False
        return True

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
            print(e)
        except Exception as e:
            print(e)
    
    def on_finished(self):
        self.disconnectEvents()
    
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
        self.disconnectEvents()
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
        
        self.keywords = [
            "program", "unit", "library",
            "begin", "end", "var",
            "procedure", "function",
            "while", "with", "do", "else", "for",
            "case"
        ]
    
    def highlightBlock(self, text):
        # Mehrzeilige Kommentare markieren
        self.setCurrentBlockState(0)
        
        for startExpr, endExpr in zip(self.commentStartExpressions, self.commentEndExpressions):
            startIndex = 0
            if self.previousBlockState() != 1:
                startIndex = startExpr.indexIn(text)
            
            while startIndex >= 0:
                endIndex = endExpr.indexIn(text, startIndex)
                if endIndex == -1:
                    self.setCurrentBlockState(1)
                    commentLength = len(text) - startIndex
                else:
                    commentLength = endIndex - startIndex + endExpr.matchedLength()
                    self.setCurrentBlockState(0)  # Reset state after ending comment
                self.setFormat(startIndex, commentLength, self.multiLineCommentFormat)
                startIndex = startExpr.indexIn(text, startIndex + commentLength)
        
        # Einzeilige Kommentare markieren
        single_line_comment_patterns = [r"//"]
        comment_positions = []
        
        for pattern in single_line_comment_patterns:
            for match in re.finditer(pattern, text):
                start = match.start()
                self.setFormat(start, len(text) - start, self.commentFormat)
                comment_positions.append((start, len(text) - start))
        
        # Keywords markieren
        for word in self.keywords:
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                in_comment = any(start >= pos[0] and start < pos[0] + pos[1] for pos in comment_positions)
                
                if self.previousBlockState() != 1 and not in_comment:
                    self.setFormat(start, length, self.boldFormat)

class EditorTranslate(QWidget):
    def __init__(self, parent):
        super().__init__()
        font = QFont(genv.v__app__font,11)
        
        self.setContentsMargins(0,0,0,0)
        self.setMinimumWidth(220)
        self.setMaximumWidth(220)
        self.setFont(font)
        
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        
        self.group_box = QGroupBox(_(" Choose a Translation: "))
        self.group_box.setFont(font)
        self.group_layout = QVBoxLayout()
        
        self.dummyl = QLabel(" ")
        self.radio1 = QRadioButton(_("Convert to FPC Pascal"))
        self.radio2 = QRadioButton(_("Convert to GNU C++"))
        self.radio3 = QRadioButton(_("Convert to Byte-Code"))
        
        self.radio1.setObjectName("pascal")
        self.radio2.setObjectName("gnucpp")
        self.radio3.setObjectName("bytecode")
        
        self.dummyl.setFont(font)
        self.radio1.setFont(font)
        self.radio2.setFont(font)
        self.radio3.setFont(font)
        
        self.radio1.toggled.connect(self.on_radiobutton_clicked)
        self.radio2.toggled.connect(self.on_radiobutton_clicked)
        self.radio3.toggled.connect(self.on_radiobutton_clicked)
        
        self.radio3.setChecked(True)
        
        self.group_layout.addWidget(self.dummyl)
        self.group_layout.addWidget(self.radio1)
        self.group_layout.addWidget(self.radio2)
        self.group_layout.addWidget(self.radio3)
        self.group_layout.addStretch()
        
        self.group_box.setLayout(self.group_layout)
        
        # file list
        self.files_layout = QVBoxLayout()
        self.files_list   = QListWidget()
        
        self.files_layout.addWidget(self.files_list)
        
        # text mini map
        self.mini_map = MiniMap(self)
        
        # QScrollArea for MiniMap
        self.scroll_area = QScrollArea()
        self.scroll_area.setMaximumWidth(210)
        self.scroll_area.setWidget(self.mini_map)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.layout.addWidget(self.group_box)
        self.layout.addLayout(self.files_layout)
        self.layout.addWidget(self.scroll_area)
        
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
    def __init__(self, parent, file_name, edit_type):
        super(EditorTextEdit, self).__init__()
        
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
            self.highlighter = dBaseSyntaxHighlighter (self.document())
        elif edit_type == "pascal":
            self.highlighter = PascalSyntaxHighlighter(self.document())
        elif edit_type == "isoc":
            self.highlighter = CppSyntaxHighlighter   (self.document())
        elif edit_type == "java":
            self.highlighter = JavaSyntaxHighlighter  (self.document())
        elif edit_type == "lisp":
            self.highlighter = LispSyntaxHighlighter  (self.document())
        elif edit_type == "prolog":
            self.highlighter = PrologSyntaxHighlighter(self.document())
        elif edit_type == "python":
            self.highlighter = PythonSyntaxHighlighter(self.document())
        
        # Schriftgröße und Schriftart setzen
        self.setFont(QFont(genv.v__app__font_edit, 12))
        
        if not os.path.exists(file_name):
            print(f"Error: file does not exists: {file_name}")
            return
        
        # Datei einlesen und Text setzen
        self.load_file(file_name)
        
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
    
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
        if event.key() == Qt.Key.Key_F2:
            script_name = self.file_name
            try:
                # ---------------------------------------
                # save source code before exec...
                # ---------------------------------------
                if genv.editor_saveb.isChecked() == True:
                    with open(script_name, 'w', encoding='utf-8') as file:
                        file.write(self.toPlainText())
                        file.close()
            except Exception as e:
                showException(traceback.format_exc())
                return
            
            if self.edit_type == "dbase":
                showInfo("dbase <---")
                prg = interpreter_dBase(script_name)
                try:
                    try:
                        prg.parse()
                        prg.run()
                    except ENoSourceHeader as e:
                        showError(_("source missing correct header style."))
                        prg = None
                        return
                finally:
                    prg = None
            
            elif self.edit_type == "pascal":
                showInfo("pascal <---")
                prg = interpreter_Pascal(script_name)
                try:
                    prg.parse()
                    prg.run()
                finally:
                    prg = None
            
            elif self.edit_type == "prolog":
                showInfo("prolog <---")
        
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
        self.parent_class.python_tabs.hide()
        self.parent_class.javascript.hide()
        self.parent_class.prolog_tabs.hide()
        self.parent_class.lisp_tabs.hide()
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

class MiniMap(QFrame):
    def __init__(self, parent=None):
        super(MiniMap, self).__init__(parent)
        
        self.setFrameStyle(QFrame.Box)
        self.setFixedWidth(100)
        self.setMaximumWidth(200)
        
        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.label.setWordWrap(True)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        
        self.setLayout(layout)
    
    def set_text(self, text):
        self.label.setText(text)
        self.label.adjustSize()
    
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
                print(f"Ausgewählter Ordner: {folder}")
            
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
            print(e)
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
                        print(e)
                        self.messageBox(path_mess)
                        return
                    print("set " + conf[1] + " path")
            except Exception as e:
                print(e)
                genv.v__app__config[self.db_pro] = {
                    conf[1]: path_name
                }
                try:
                    with open(hlay_name, "w", encoding="utf-8") as configfile:
                        genv.v__app__config.write(configfile)
                        configfile.close()
                except Exception as e:
                    print("bbb")
                    print(e)
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
        
        if text[0] == "label 1":
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
        try:
            self.setObjectName(self.text)
            
            self.tabs_editor_vlayout = QVBoxLayout(tabs)
            self.tabs_editor = QTabWidget()
            self.tabs_editor.setStyleSheet(_(genv.css_tabs))
            
            self.tabs_editor_menu = QListWidget()
            self.tabs_editor_menu.setContentsMargins(0,0,0,0)
            self.tabs_editor_menu.setFlow(QListWidget.LeftToRight)
            self.tabs_editor_menu.setStyleSheet("background-color:gray;")
            self.tabs_editor_menu.setMinimumHeight(64)
            self.tabs_editor_menu.setMaximumHeight(64)
            
            self.custom_widget0 = ButtonWidget("label 1:")
            self.custom_widget1 = ButtonWidget("label 2:")
            self.custom_widget2 = ButtonWidget("label 3:")
            
            self.widget0_list_item = QListWidgetItem(self.tabs_editor_menu)
            self.widget0_list_item.setSizeHint(self.custom_widget0.sizeHint())
            
            self.widget1_list_item = QListWidgetItem(self.tabs_editor_menu)
            self.widget1_list_item.setSizeHint(self.custom_widget1.sizeHint())
            
            self.widget2_list_item = QListWidgetItem(self.tabs_editor_menu)
            self.widget2_list_item.setSizeHint(self.custom_widget2.sizeHint())
            
            self.tabs_editor_menu.setItemWidget(self.widget0_list_item, self.custom_widget0)
            self.tabs_editor_menu.setItemWidget(self.widget1_list_item, self.custom_widget1)
            self.tabs_editor_menu.setItemWidget(self.widget2_list_item, self.custom_widget2)
            
            self.tabs_editor_menu.itemClicked.connect(self.on_editor_menu_item_clicked)
            
            self.tabs_editor_vlayout.addWidget(self.tabs_editor_menu)
            self.tabs_editor_vlayout.addWidget(self.tabs_editor)
        except Exception as e:
            showException(traceback.format_exc())
    
    def on_editor_menu_item_clicked(self, item):
        print("self: ", self.objectName())
        widget = self.tabs_editor_menu.itemWidget(item)
        if widget:
            text = widget.objectName()
            text = text.split(':')
            if text[0] == "label 1":
                file_path = self.open_dialog()
                filename  = os.path.basename(file_path)
                if len(filename) < 1:
                    return
                widget.setObjectName('label 1:' + file_path)
                #
                for entry in genv.editors_entries[self.text]:
                    if entry["name"] == file_path:
                        showInfo("already open.")
                        return
                
                file_layout_widget = QWidget()
                file_layout        = QHBoxLayout()
                
                editor_object = EditorTextEdit(self, file_path, self.text)
                new_editor    = {
                    "object": editor_object,
                    "name":   file_path
                }
                genv.editors_entries[self.text].append(new_editor)
                
                file_layout_widget = QWidget()
                file_layout        = QVBoxLayout()
                
                file_layout.addWidget(editor_object)
                file_layout_widget.setLayout(
                file_layout)
                
                self.tabs_editor.addTab(file_layout_widget, filename)
                
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
                        prg = interpreter_Lisp(script_name)
                        prg.parse()
                        
                    elif genv.current_focus.edit_type == "c64":
                        prg = interpreter_C64(script_name)
                        prg.parse()
                    
                    print("\nend of data\n")
                    
                    print(genv.text_code)
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
    
    def showNoEditorMessage(self):
        msg = QMessageBox()
        msg.setWindowTitle(_("Warning"))
        msg.setText(_("no editor open - do nothing.\n"))
        msg.setIcon(QMessageBox.Warning)
        
        btn_ok = msg.addButton(QMessageBox.Ok)
        
        msg.setStyleSheet(_("msgbox_css"))
        msg.exec_()
    
    def checkBeforeSave(self):
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
                    print(script_name)
                    if not os.path.exists(script_name):
                        msg = None
                        msg = QMessageBox()
                        msg.setWindowTitle("Warning")
                        msg.setText(_("Error: file could not be saved:") + f"\n{script_name}.")
                        msg.setIcon(QMessageBox.Warning)
                        btn_ok = msg.addButton(QMessageBox.Ok)
                        
                        msg.setStyleSheet(_("msgbox_css"))
                        result = msg.exec_()
                        print(f"Error: file does not exists: {script_name}.")
                        return
                    file_path = script_name.replace("\\", "/")
                    #
                    with open(file_path, "w") as file:
                        file.write(self.focused_widget.toPlainText())
                        file.close()
    
    def open_dialog(self):
        dialog  = QFileDialog()
        file_path = ""
        icon_size = 20
        
        dialog.setWindowTitle(_("Open File"))
        dialog.setStyleSheet (_("QFileDlog"))
        
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setViewMode(QFileDialog.Detail)
        
        dialog.setOption  (QFileDialog.DontUseNativeDialog, True)
        
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
        else:
            dialog.setNameFilters([
                _("All Files") + " (*)"])
                
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

# ---------------------------------------------------------------------------
# \brief  This is the GUI-Entry point for our application.
# \param  nothing
# \return ptr => the class object pointer
# ---------------------------------------------------------------------------
class FileWatcherGUI(QDialog):
    def __init__(self, parent=None):
        super(FileWatcherGUI, self).__init__(parent)
        #self.setAttribute(Qt.WA_DeleteOnClose, True)
        
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
        self.setStyleSheet("padding:0px;margin:0px;")
        self.setWindowIcon(QIcon(genv.v__app__img__int__ + "/winico.png"))
        
        self.worker_hasFocus = False
        self.is_maximized    = False
        
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.windowtitle = 'HelpNDoc File Watcher Client - v0.0.1 - (c) 2024 Jens Kallup - paule32'
        
        self.my_list = MyItemRecord(0, QStandardItem(""))
        
        self.init_ui()
        
    # --------------------
    # dialog exit ? ...
    # --------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F1:
            genv.help_dialog = HelpWindow(self)
            genv.help_dialog.setAttribute(Qt.WA_DeleteOnClose, True)
            #help_chm = "help.chm"
            #if os.path.exists(help_chm):
            #    os.startfile(help_chm)
            #else:
            #    msg = QMessageBox()
            #    msg.setWindowTitle("Warnin")
            #    msg.setText(
            #        _("The help file for the Application\n"
            #        + "Could not be found !"))
            #    msg.setIcon(QMessageBox.Warning)
            #    
            #    btn_ok = msg.addButton(QMessageBox.Ok)
            #    
            #    msg.setStyleSheet(_("msgbox_css"))
            #    result = msg.exec_()
        
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
        print(f"Clicked row: {row}, col: {col}, text: {text}")
    
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
                    print(e)
                
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
    
    def open_context_topics_menu(self, position: QPoint):
        index = self.tab2_tree_view.indexAt(position)
        if index.isValid():
            item_text = self.tab2_tree_model.itemFromIndex(index).text()
            print(f"Item text: {item_text}")
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
        
        layout = QVBoxLayout()
                        
        self.title_bar = CustomTitleBar(self.windowtitle, self)
        self.title_bar.minimize_button.clicked.connect(self.showMinimized)
        self.title_bar.maximize_button.clicked.connect(self.showMaximized)
        self.title_bar.close_button.clicked.connect(self.close)
        
        content = QWidget()
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0,0,0,0)
        content.setLayout(content_layout)
        
        # menu bar
        self.menu_bar = QMenuBar(self)
        self.menu_bar.setStyleSheet(genv.css_menu_item_style)
        
        self.menu_style_bg = "background-color:navy;"
        menu_list = [
            [_("&File"),
                [
                    [_("New...")    , "Ctrl+N", self.menu_file_clicked_new   ],
                    [_("Open")      , "Ctrl+O", self.menu_file_clicked_open  ],
                    [_("Save")      , "Ctrl+S", self.menu_file_clicked_save  ],
                    [_("Save as..."), ""      , self.menu_file_clicked_saveas],
                    [_("Exit")      , "Ctrl+X", self.menu_file_clicked_exit  ]
                ]
            ],
            [_("&Edit"),
                [
                    [_("Undo")     , ""      , self.menu_edit_clicked_undo     ],
                    [_("Redo")     , ""      , self.menu_edit_clicked_redo     ],
                    [_("Clear All"), "Ctrl+0", self.menu_edit_clicked_clearall ]
                ]
            ],
            [_("&Help"),
                [
                    [_("About..."), "F1", self.menu_help_clicked_about ]
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
        
        #self.layout.addWidget( self.menu_bar )
        #self.menu_bar.show()
        
        # tool bar
        self.tool_bar = QToolBar()
        self.tool_bar.setContentsMargins(0,0,0,0)
        self.tool_bar.setMinimumHeight(36)
        self.tool_bar.setStyleSheet(_(genv.toolbar_css))
        
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
        
        #self.layout.addWidget(self.tool_bar)
        #self.tool_bar.show()
        
        # status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready", 0)
        self.status_bar.setStyleSheet("background-color:gray;")
        
        
        # side toolbar
        self.main_layout = QHBoxLayout()
        self.main_widget = QWidget()
        
        self.main_widget.setStyleSheet("padding:0px;margin:0px;")
        
        self.side_scroll = QScrollArea()
        self.side_widget = QWidget()
        self.side_layout = QVBoxLayout()
        #
        self.side_widget.setContentsMargins(0,0,0,0)
        self.side_scroll.setContentsMargins(0,0,0,0)
        
        self.side_btn0 = myIconButton(self,   0, _("Help")      , _("Help Authoring for/with:\no doxygen\no HelpNDoc"))
        self.side_btn1 = myIconButton(self,   1, _("dBASE")     , _("dBASE data base programming\nlike in the old days...\nbut with SQLite -- dBase keep alive !"))
        self.side_btn2 = myIconButton(self,   2, _("Pascal")    , _("Pascal old school programming\no Delphi\no FPC"))
        self.side_btn3 = myIconButton(self,   3, _("ISO C")     , _("C / C++ embeded programming\nor cross platform"))
        self.side_btn4 = myIconButton(self,   4, _("Java")      , _("Java modern cross programming\nfor any device"))
        self.side_btn5 = myIconButton(self,   5, _("Python")    , _("Python modern GUI programming\nlets rock AI\nand TensorFlow"))
        self.side_btn6 = myIconButton(self,   6, _("JavaScript"), _("JavaScript programming"))
        self.side_btn7 = myIconButton(self,   7, _("Prolog")    , _("Prolog - logical programming."))
        self.side_btn8 = myIconButton(self,   8, _("LISP")      , _("LISP traditional programming\nultimate old school"))
        #
        self.side_btn9 = myIconButton(self,   9, _("Locales"), _(""
            + "Localization your Application with different supported languages\n"
            + "around the World.\n"
            + "Used by tools like msgfmt - the Unix Tool for generationg .mo files.\n"))
        #
        self.side_btn10 = myIconButton(self, 10, "Console", "Your classical style of commands")
        self.side_btn11 = myIconButton(self, 11, "Todo / Tasks", "Your todo's")
        self.side_btn12 = myIconButton(self, 12, "Setup", "Setup your Project")
        self.side_btn13 = myIconButton(self, 13, "SSL Certs", "Setup SSL")
        self.side_btn14 = myIconButton(self, 14, "GitHub.com", "Publish Project")
        self.side_btn15 = myIconButton(self, 15, "Web Server", "Configure Web Server")
        self.side_btn16 = myIconButton(self, 16, "MySQL", "Configure MySQL")
        self.side_btn17 = myIconButton(self, 17, "Squid", "Configure Squid")
        self.side_btn18 = myIconButton(self, 18, "Electro", "electronic simulations")
        self.side_btn19 = myIconButton(self, 19, "C-64", "The most popular Commodore C-64\from int the 1980er")
        self.side_btn20 = myIconButton(self, 20, _("Settings")   , _("Settings for this Application\n\n"))
        
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
        
        ####
               
        self.main_layout.addWidget(self.side_scroll)
                
        self.handleDBase()
        self.handlePascal()
        self.handleIsoC()
        self.handleJava()
        self.handlePython()
        self.handleJavaScript()
        self.handleProlog()
        self.handleLISP()
        self.handleLocales()
        self.handleConsole()
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
        
        
        # first register card - action's ...
        self.help_tabs = QTabWidget()
        self.help_tabs.setStyleSheet(_(genv.css_tabs))
        
        # help
        self.tab0_0 = QWidget()
        self.tab1_0 = QWidget()
        self.tab2   = QWidget()
        self.tab3   = QWidget()
        self.tab4   = QWidget()
        
        # add tabs
        self.help_tabs.addTab(self.tab0_0, _("Help Project"))
        self.help_tabs.addTab(self.tab1_0, _("Pre-/Post Actions"))
        self.help_tabs.addTab(self.tab3,   _("HelpNDoc"))
        self.help_tabs.addTab(self.tab4,   _("Content"))
        
        self.tab_widget_tabs = QTabWidget(self.tab4)
        self.tab_widget_tabs.setMinimumWidth(830)
        self.tab_widget_tabs.setMinimumHeight(650)
        self.tab_html   = QWidget()
        self.tab_widget_tabs.addTab(self.tab2, "Topics")
        self.tab_widget_tabs.addTab(self.tab_html  , "HTML"  )
        
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
        list_widget_1.setStyleSheet(_(genv.css__widget_item))
        list_widget_1.setMinimumHeight(300)
        list_widget_1.setMaximumWidth(200)
        self.list_widget_1_elements = [_("Project"), _("Mode"), _("Output"), _("Diagrams") ]
        #
        #
        for element in self.list_widget_1_elements:
            list_item = customQListWidgetItem(element, list_widget_1)
        
        list_widget_1.setCurrentRow(0)
        list_widget_1.itemClicked.connect(self.handle_item_click)
        list_layout_1.addWidget(list_widget_1)
        
        self.sv_1_1 = customScrollView_1(self, _("Project"))
        self.sv_1_2 = customScrollView_2(self, _("Mode"));     self.sv_1_2.hide()
        self.sv_1_3 = customScrollView_3(self, _("Output"));   self.sv_1_3.hide()
        self.sv_1_4 = customScrollView_4(self, _("Diagrams")); self.sv_1_4.hide()
        
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
        list_widget_2.setStyleSheet(_(genv.css__widget_item))
        list_widget_2.setMinimumHeight(300)
        list_widget_2.setMaximumWidth(200)
        
        self.list_widget_2_elements = [                                     \
            _("Project"), _("Build"), _("Messages"), _("Input"), _("Source Browser"),      \
            "Index", "HTML", "LaTeX", "RTF", "Man", "XML", "DocBook",       \
            "AutoGen", "SQLite3", "PerlMod", "Preprocessor", _("External"),    \
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
            #print("sv_2: ", item)
            v1 = eval(item + "(self,'')")
            v1.setName(self.list_widget_2_elements[i])
            v1.setObjectName(self.list_widget_2_elements[i])
            objs.append(v1)
            setattr(self, s, v1)
            list_layout_2.addWidget(v1)
            v1.hide()
            i += 1
        
        self.sv_2_1.show()
        self.hw_2 = QWidget()
        
        list_layout_b.addWidget(genv.sv_help)
        ########################
        self.tab3_top_layout.addWidget(self.tab_widget_1)
        
        
        self.tab2_file_path = os.path.join(genv.v__app__internal__, "topics.txt")
        if not os.path.exists(self.tab2_file_path):
            showError("Error: file does not exists:\n" + self.tab2_file_path)
            sys.exit(1)
        print("---> " + self.tab2_file_path)
        
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
        self.tab0_fold_scroll1.setMinimumWidth(300)
        self.tab0_fold_scroll1.setMaximumWidth(300)
        
        self.tab0_fold_push11  = MyPushButton(self, "Create", 1, self.create_project_clicked)
        self.tab0_fold_push12  = MyPushButton(self, "Open"  , 2, self.open_project_clicked)
        self.tab0_fold_push13  = MyPushButton(self, "Repro" , 3, self.repro_project_clicked)
        self.tab0_fold_push14  = MyPushButton(self, "Build" , 4, self.build_project_clicked)
        #        
        #
        self.tab0_fold_scroll2 = QScrollArea()
        self.tab0_fold_scroll2.setMaximumWidth(300)
        self.tab0_fold_push21  = MyPushButton(self, "Create", 1, None)
        self.tab0_fold_push22  = MyPushButton(self, "Open"  , 2, None)
        self.tab0_fold_push23  = MyPushButton(self, "Repro" , 3, None)
        self.tab0_fold_push24  = MyPushButton(self, "Build" , 4, None)
        #
        self.tab0_top1_hlayout.addWidget(self.tab0_fold_text1)
        self.tab0_top1_hlayout.addWidget(self.tab0_fold_edit1)
        self.tab0_top1_hlayout.addWidget(self.tab0_fold_push1)
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
        genv.img_doxygen = doxygenImageTracker ()
        genv.img_hlpndoc = helpNDocImageTracker()
        #
        #
        self.img_scroll1_layout.addWidget(genv.img_doxygen)
        self.img_scroll1_layout.addWidget(genv.img_hlpndoc)
        #

        self.img_scroll2_layout = QVBoxLayout(self.tab0_fold_scroll2)
        
        radio_font = QFont("Consolas",11)
        genv.radio_cpp        = QRadioButton("C++        Documentation")
        genv.radio_java       = QRadioButton("Java       Documentation")
        genv.radio_javascript = QRadioButton("JavaScript Documentation")
        genv.radio_python     = QRadioButton("Python     Documentation")
        genv.radio_php        = QRadioButton("PHP        Documentation")
        
        genv.radio_cpp.setFont(radio_font)
        genv.radio_java.setFont(radio_font)
        genv.radio_javascript.setFont(radio_font)
        genv.radio_python.setFont(radio_font)
        genv.radio_php.setFont(radio_font)
        
        self.img_scroll2_layout.addWidget(genv.radio_cpp)
        self.img_scroll2_layout.addWidget(genv.radio_java)
        self.img_scroll2_layout.addWidget(genv.radio_javascript)
        self.img_scroll2_layout.addWidget(genv.radio_python)
        self.img_scroll2_layout.addWidget(genv.radio_php)
        
        #
        #
        self.tab0_top_layout.addLayout(self.tab0_topV_vlayout)
        
        self.tab0_file_text = QLabel("File:", self.tab0_0)
        
        self.tab0_left_layout.addWidget(self.tab0_file_text)
        self.tab0_path = QDir.homePath()
        
        self.tab0_help_list   = QListWidget()
        self.tab0_help_list.setMinimumWidth(260)
        self.tab0_help_list.setIconSize(QSize(34,34))
        self.tab0_help_list.setFont(QFont(genv.v__app__font, 12))
        self.tab0_help_list.font().setBold(True)
        self.tab0_help_list.itemClicked.connect(self.tab0_help_list_item_click)
        
        self.list_blue_item = QListWidgetItem(_("Page Template:"))
        self.list_blue_item.setBackground(QColor("navy"))
        self.list_blue_item.setForeground(QColor("yellow"))
        self.list_blue_item.setFlags(
        self.list_blue_item.flags() & ~Qt.ItemIsSelectable)
        self.tab0_help_list.addItem(self.list_blue_item)
        
        liste = [
            [_("HTML WebSite Template")],
            [_("PDF  Portable Docuement Format")]
        ]
        for item in liste:
            self.list_item1 = QListWidgetItem(_(item[0]))
            self.list_item1.setFont(self.tab0_help_list.font())
            self.tab0_help_list.addItem(self.list_item1)
        
        self.list_blue_item = QListWidgetItem(_("empty"))
        self.list_blue_item.setBackground(QColor("white"))
        self.list_blue_item.setForeground(QColor("white"))
        self.list_blue_item.setFlags(
        self.list_blue_item.flags() & ~Qt.ItemIsSelectable)
        self.tab0_help_list.addItem(self.list_blue_item)
        
        self.list_blue_item = QListWidgetItem(_("Project Template:"))
        self.list_blue_item.setBackground(QColor("navy"))
        self.list_blue_item.setForeground(QColor("yellow"))
        self.list_blue_item.setFlags(
        self.list_blue_item.flags() & ~Qt.ItemIsSelectable)
        self.tab0_help_list.addItem(self.list_blue_item)
        
        liste = [
            [_("Empty Project")         , os.path.join("emptyproject" + genv.v__app__img_ext__) ],
            [_("Recipe")                , os.path.join("recipe"       + genv.v__app__img_ext__) ],
            [_("API Project")           , os.path.join("api"          + genv.v__app__img_ext__) ],
            [_("Software Documentation"), os.path.join("software"     + genv.v__app__img_ext__) ],
        ]
        for item in liste:
            self.list_item1 = QListWidgetItem(_(item[0]))
            self.list_item1.setIcon(QIcon(os.path.join(genv.v__app__img__int__, item[1])))
            self.list_item1.setFont(self.tab0_help_list.font())
            self.tab0_help_list.addItem(self.list_item1)
        
        self.list_blue_item = QListWidgetItem(_("Projects:"))
        self.list_blue_item.setBackground(QColor("navy"))
        self.list_blue_item.setForeground(QColor("yellow"))
        self.list_blue_item.setFlags(
        self.list_blue_item.flags() & ~Qt.ItemIsSelectable)
        self.tab0_help_list.addItem(self.list_blue_item)
        
        self.tab0_help_layout = QHBoxLayout()
        self.tab0_help_layout.addWidget(self.tab0_help_list)
        
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
        
        layout.addWidget(self.title_bar  )
        layout.addWidget(self.menu_bar   )
        layout.addWidget(self.tool_bar   )
        layout.addLayout(self.main_layout)
        layout.addWidget(self.status_bar )
        
        #
        #self.layout.addLayout(self.main_layout)
        #self.layout.addWidget(self.status_bar)
        
        self.setLayout(layout)
        self.setWindowTitle(self.windowtitle)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateCountdown)
        
        self.interval = 0
        self.currentTime = 0
    
    def tab0_help_list_item_click(self, item):
        text = item.text()
        if text == _("Empty Project"):
            genv.doc_template = genv.DOC_TEMPLATE_EMPTY
            return True
        elif text == _("Recipe"):
            genv.doc_template = genv.DOC_TEMPLATE_RECIPE
            return True
        elif text == _("API Project"):
            genv.doc_template = genv.DOC_TEMPLATE_API
            return True
        elif text == _("Software Documentation"):
            genv.doc_template = genv.DOC_TEMPLATE_SOFTWARE
            return True
        else:
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
            showError(path_error)
            return False
        # ------------------------------
        if genv.radio_cpp.isChecked():
            bool_flagA = True
        elif genv.radio_java.isChecked():
            bool_flagA = True
        elif genv.radio_javascript.isChecked():
            bool_flagA = True
        elif genv.radio_python.isChecked():
            bool_flagA = True
        elif genv.radio_php.isChecked():
            bool_flagA = True
        # ------------------------------
        if genv.doc_project == "doxygen":
            bool_flagB = True
        elif genv.doc_project == "helpndoc":
            bool_flagB = True
        else:
            bool_flagB = False
        # ------------------------------
        if genv.doc_template >= 0:
            bool_flagC = True
        else:
            bool_flagC = False
        # ------------------------------
        if not (bool_flagA == True) \
        or not (bool_flagB == True) \
        or not (bool_flagC == True):
            showError(_("Error:\nNo project documentation selected."))
            return False
        # ------------------------------
        return True
    
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
        
            genv.project_type = genv.v__app__config.get("common", "type")
        except configparser.NoOptionError as error:
            MyProjectOption()
        
        if genv.project_type.lower() == "doxygen":
            self.trigger_mouse_press(genv.img_doxygen)
        elif genv.project_type.lower() == "helpndoc":
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
        self.dbase_project = ApplicationProjectPage(self, self.dbase_tabs_project_widget, "dbase")
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
        
        self.electro_tabs.addTab(self.electro_tabs_designer_widget, _("Electro Project"))
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
        print("cert new")
    def on_click_cert_add(self):
        print("cert add")
    def on_click_cert_del(self):
        print("cert del")
    
    def on_click_saveca_ca(self):
        print("saveca ca")
    
    def on_click_create_ca(self):
        print("create ca")
    
    def on_click_delete_ca(self):
        print("delete ca")
    
    def on_click_cleara_ca(self):
        print("clear all ca")
    
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
        print("start iis")
    
    def apache_server_start(self):
        print("start apache")
    
    def tomcat_server_start(self):
        print("start tomcat")
    
    def iis_server_stop(self):
        print("stop iis")
    
    def apache_server_stop(self):
        print("stop apache")
    
    def tomcat_server_stop(self):
        print("stop tomcat")
    
    def iis_send_clients(self):
        print("send to iis clients")
    
    def apache_send_clients(self):
        print("send to apache clients")
    
    def tomcat_send_clients(self):
        print("send to tomcat clients")
    
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
            print(s)
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
            print(s)
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
        print(el)
    
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
                            print("file: " + file_name + " is packed.")
                        else:
                            print("file: " + file_name + " is not packed.")
                        file.close()
                    #print(self.localeliste[0][0].text())
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
        if index == 0 or index == 1 or index == 3:
            print("end")
            if not self.c64_screen.worker_thread == None:
                self.c64_screen.worker_thread.stop()
            self.worker_hasFocus = False
        elif index == 2:
            print("start")
            if not self.c64_screen.worker_thread == None:
                self.c64_screen.worker_thread.stop()
            self.c64_screen.worker_thread = None
            self.c64_screen.worker_thread = c64WorkerThread(self)
            self.c64_screen.worker_thread.start()
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
        
        _listpush_apps = QPushButton(_("Applications"))
        _listpush_game = QPushButton(_("Games"))
        
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
        msg.setWindowTitle(_("Confirmation"))
        msg.setText(_("Would you close the Application?"))
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
            print(f"File {filePath} exists.")
            # weitere Aktionen durchführen, wenn die Datei existiert
        else:
            print(f"File {filePath} not found.")
            # ktionen durchführen, wenn die Datei nicht existiert
    
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouse_press_pos = event.globalPos()
            self.mouse_move_pos = event.globalPos() - self.frameGeometry().topLeft()
            self.resizing = self.getCursorPosition(event.pos())
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            if self.resizing:
                self.resizeWindow(event.globalPos())
            else:
                self.move(event.globalPos() - self.mouse_move_pos)
        else:
            self.updateCursor(event.pos())
    
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
        self.setMinimumWidth(820)
        
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
    print("Thank's for using.")
    return

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_view = None

    def set_parent_view(self, parent_view):
        self.parent_view = parent_view

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            if self.parent_view:
                # Link-Klick abfangen und an die zweite WebView weitergeben
                self.parent_view.setUrl(url)
                return False
        return super().acceptNavigationRequest(url, _type, isMainFrame)

# ------------------------------------------------------------------------
# chm help window ...
# ------------------------------------------------------------------------
class HelpWindow(QMainWindow):
    def __init__(self, parent=None):
        genv.saved_style = genv.window_login.styleSheet()
        genv.window_login.setStyleSheet("")
        
        super(HelpWindow, self).__init__(parent)
        
        self.hide()
        self.setWindowTitle(_("CHM Help Dialog"))
        self.setGeometry(100, 100, 700, 600)
        
        # Hauptlayout des Dialogs
        layout = QVBoxLayout()
        
        # Navigation Panel erstellen
        navigation_container = QVBoxLayout()
        navigation_widget = QWidget()
        navigation_layout = QHBoxLayout()
        
        # Buttons: Home, Prev, Next
        self.home_button = QPushButton("Home")
        self.prev_button = QPushButton("Prev")
        self.next_button = QPushButton("Next")
        
        self.home_button.setMinimumHeight(49)
        self.prev_button.setMinimumHeight(49)
        self.next_button.setMinimumHeight(49)
        
        self.home_button.setCursor(Qt.PointingHandCursor)
        self.prev_button.setCursor(Qt.PointingHandCursor)
        self.next_button.setCursor(Qt.PointingHandCursor)
        
        self.home_button.setFont(QFont("Arial", 12))
        self.prev_button.setFont(QFont("Arial", 12))
        self.next_button.setFont(QFont("Arial", 12))
        
        navigation_widget.setStyleSheet("background-color:lightgray;")
        navigation_layout.setAlignment(Qt.AlignTop)
        
        # Buttons dem Layout hinzufügen
        navigation_layout.addWidget(self.home_button)
        navigation_layout.addWidget(self.prev_button)
        navigation_layout.addWidget(self.next_button)
        
        # Setze das Layout für das Navigations-Widget
        navigation_widget.setLayout(navigation_layout)
        
        hlayout = QHBoxLayout()
        
        # WebView Widget zum Anzeigen der CHM-Datei
        self.browser = QWebEngineView()
        self.topics  = QWebEngineView()
        
        self.topics.setMinimumWidth(180)
        self.topics.setMaximumWidth(180)
        
        self.topics.setStyleSheet("""
        background-color: white;
        """)

        page = CustomWebEnginePage(self.topics)
        page.set_parent_view(self.browser)
        self.topics.setPage(page)
        
        
        # table of contents - TOC
        html_content = _h("TOC")
        self.topics.setHtml(html_content)
        
        
        hlayout.addWidget(self.topics)
        hlayout.addWidget(self.browser)
        
        navigation_container.addWidget(navigation_widget)
        navigation_container.addLayout(hlayout)
        
        layout.addLayout(navigation_container)
        
        
        # topic content
        html_content = _h("home")
        self.browser.setHtml(html_content)
        
        #self.browser.setUrl(QUrl(chm_file_url))
        #layout.addWidget(self.browser)
        
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
        genv.window_login.setStyleSheet(genv.saved_style)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.show()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
    
    def closeEvent(self, event):
        if not genv.window_login == None:
            genv.window_login.setStyleSheet(genv.saved_style)
        if not self.browser == None:
            self.browser.deleteLater()
        event.accept()
    
    def on_close(self):
        self.close()

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 450, 400)
        self.setStyleSheet(_("login_dialog_style"))

        # Hauptlayout des Dialogs
        layout = QVBoxLayout()

        # Titel: Login
        self.title_label = QLabel("Login")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.title_label.setStyleSheet("color: #ffffff;")
        self.title_label.setMaximumHeight(100)
        layout.addWidget(self.title_label)

        # ComboBox zur Auswahl
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Option 1", "Option 2", "Option 3"])
        self.combo_box.setStyleSheet(_("login_dialog_combobox"))
        
        layout.addWidget(self.combo_box)

        # Eingabefeld unter der ComboBox
        self.additional_field = QLineEdit()
        self.additional_field.setPlaceholderText(_("type in server"))
        self.additional_field.setStyleSheet(_("login_dialog_edit1"))
        self.additional_field.mouseDoubleClickEvent = self.open_additional_dialog
        
        layout.addWidget(self.additional_field)

        # Eingabe für Benutzername
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText(_("type in username"))
        self.username_field.setStyleSheet(_("login_dialog_edit2"))
        
        layout.addWidget(self.username_field)

        # Eingabe für Passwort
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText(_("type in password"))
        self.password_field.setEchoMode(QLineEdit.Password)
        self.password_field.setStyleSheet(_("login_dialog_pass"))
        layout.addWidget(self.password_field)

        # Login-Button
        self.login_button = QPushButton(_("Login into the System"))
        self.login_button.setStyleSheet(_("login_dialog_push"))
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.on_close)
        layout.addWidget(self.login_button)

        # Setze das Layout
        self.setLayout(layout)

    def open_additional_dialog(self, event):
        additional_dialog = QDialog(self)
        additional_dialog.setWindowTitle("Zusätzlicher Dialog")
        additional_dialog.setGeometry(150, 150, 300, 200)
        additional_dialog.exec_()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            sys.exit(0)
        elif event.key() == Qt.Key_F1:
            genv.help_dialog = HelpWindow(self)
            genv.help_dialog.setAttribute(Qt.WA_DeleteOnClose, True)
    
    def on_close(self):
        self.close()

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
    
    genv.window_login = LoginDialog()
    genv.window_login.exec_()
    
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
        print("info: config: '" \
        + f"{genv.doxyfile}" + "' does not exists. I will fix this by create a default file.")
        
        file_content      = json.loads(_("doxyfile_content"))
        #print(file_content)
        
        try:
            file_content_warn = json.loads(_("doxyfile_content_warn"))
            #print(file_content_warn)
        except Exception as e:
            print(e)
        print(">>>")
        #print(file_content)
        print("<<<")
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
    
    genv.sv_help = customScrollView_help()
    genv.sv_help.setStyleSheet(_("ScrollBarCSS"))
    
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
            print("\nend of data")

# ---------------------------------------------------------------------------
# the mother of all: the __main__ start point ...
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    
    # The Python 3+ or 3.12+ is required.
    major = sys.version_info[0]
    minor = sys.version_info[1]
    if (major < 3 and minor < 12):
        print("Python 3.12+ are required for the script")
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
        #print(genv.v__app__parameter)
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
                print(genv.v__app__tmp3)
                try:
                    handleExceptionApplication(parserDBasePoint,sys.argv[idx])
                    sys.exit(0)
                except Exception as ex:
                    sys.exit(1)
            elif item == "--pascal":
                idx += 1
                print(genv.v__app__tmp3)
                genv.v__app__scriptname__ = sys.argv[2]
                handleExceptionApplication(parserPascalPoint,sys.argv[idx])
                sys.exit(0)
        else:
            print("parameter unknown.")
            print(genv.v__app__parameter)
            sys.exit(1)
        
# ----------------------------------------------------------------------------
# E O F  -  End - Of - File
# ----------------------------------------------------------------------------