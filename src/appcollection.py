# ---------------------------------------------------------------------------
# File:   appcollection.py - import modules for observer application ...
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
global EXIT_SUCCESS; EXIT_SUCCESS = 0
global EXIT_FAILURE; EXIT_FAILURE = 1

global basedir
global tr
global sv_help

global error_fail, error_result
global app
global byte_code

global debugMode

# ---------------------------------------------------------------------------
# application imports ...
# ---------------------------------------------------------------------------
try:
    import os            # operating system stuff
    
    if 'PYTHONHOME' in os.environ:
        del os.environ['PYTHONHOME']
    if 'PYTHONPATH' in os.environ:
        del os.environ['PYTHONPATH']
    
    import re            # regular expression handling
    
    import sys           # system specifies
    import time          # thread count
    import datetime      # date, and time routines
    
    import threading     # multiple action simulator
    
    # ------------------------------------------------------------------------
    # developers own module paths...
    # ------------------------------------------------------------------------
    __app__inter__ = "./interpreter/"
    #
    sys.path.append(__app__inter__ + "doxygen")
    sys.path.append(__app__inter__ + "pascal")
    sys.path.append(__app__inter__ + "dbase")
    sys.path.append(__app__inter__ )
    #
    sys.path.append("./tools")
    
    import glob           # directory search
    import atexit         # clean up
    import subprocess     # start sub processes
    import platform       # Windows ?
    
    import gzip           # pack/de-pack data
    import base64         # base64 encoded data
    import shutil         # shell utils

    import pkgutil        # attached binary data utils
    import json           # json lists
    
    import gettext        # localization
    import locale         # internal system locale
    
    import random         # randome numbers
    import string
    
    import ctypes         # windows ip info
    
    import sqlite3        # database: sqlite
    import configparser   # .ini files
    
    import traceback      # stack exception trace back
    
    import textwrap
    import marshal        # bytecode exec
    import inspect        # stack
    
    # ------------------------------------------------------------------------
    # Qt5 gui framework
    # ------------------------------------------------------------------------
    from PyQt5.QtWidgets          import *
    from PyQt5.QtWebEngineWidgets import *
    from PyQt5.QtCore             import *
    from PyQt5.QtGui              import *
    
    from logging    import *
    
    # ------------------------------------------------------------------------
    # developers own modules ...
    # ------------------------------------------------------------------------
    from collection import *     # exception: templates
    
    from VisualComponentLibrary import *
    
    from dbaseConsole     import *
    from EParserException import *     # exception handling for use with parser
    from RunTimeLibrary   import *     # rtl functions for parser
    
    from ParserDSL        import *
    
    from colorama   import init, Fore, Back, Style  # ANSI escape
    from pascal     import *     # pascal interpreter
    from dbase      import *     # dbase ...
    from doxygen    import *     # doxygen script
    
except Exception as err:
    print(err)
    sys.exit(1)
