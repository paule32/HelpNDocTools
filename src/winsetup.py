# ---------------------------------------------------------------------------
# File:   winsetup.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import importlib
import subprocess
import sys           # system specifies
import os            # operating system stuff

# -----------------------------------------------------------------------
# under the windows console, python paths can make problems ...
# -----------------------------------------------------------------------
if 'PYTHONHOME' in os.environ:
    del os.environ['PYTHONHOME']
if 'PYTHONPATH' in os.environ:
    del os.environ['PYTHONPATH']
    
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

# ------------------------------------------------------------------------
# message box code place holder ...
# ------------------------------------------------------------------------
def showMessage(text, msgtype=0):
    if not isApplicationInit():
        genv.v__app_object = QApplication(sys.argv)
    #
    msgtypes = [
        [ QMessageBox.Information, _("Information") ],
        [ QMessageBox.Warning,     _("Warning") ],
        [ QMessageBox.Critical,    _("Error") ],
        [ QMessageBox.Critical,    _("Exception") ]
    ]
    
    if not application_window == None:
        dialog = QDialog(application_window)
    else:
        dialog = QDialog()
    
    dialog.setWindowTitle(msgtypes[msgtype][1])
    dialog.setMinimumWidth(700)
    
    text_lay = QVBoxLayout()
    text_box = QPlainTextEdit()
    text_box.setFont(QFont("Consolas", 10))
    text_box.document().setPlainText(text)
    
    text_btn = QPushButton(_("Close"))
    text_btn.setMinimumHeight(32)
    text_btn.setStyleSheet(_("msgbox_css"))
    text_btn.clicked.connect(lambda: dialog.close())
    
    text_lay.addWidget(text_box)
    text_lay.addWidget(text_btn)
    
    dialog.setLayout(text_lay)
    dialog.exec_()

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
    showMessage(text, 2)
    return

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

