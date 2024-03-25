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

global debugMode

# ---------------------------------------------------------------------------
# application imports ...
# ---------------------------------------------------------------------------
import os            # operating system stuff
import sys           # system specifies
import time          # thread count
import datetime      # date, and time routines
import re            # regular expression handling

import glob          # directory search
import atexit        # clean up
import subprocess    # start sub processes
import platform      # Windows ?

import gzip          # pack/de-pack data
import base64        # base64 encoded data

import shutil        # shell utils
import pkgutil       # attached binary data utils
import json          # json lists

import gettext       # localization
import locale        # internal system locale

import random        # randome numbers
import string

import sqlite3       # database: sqlite
import configparser  # .ini files

import traceback     # stack exception trace back

# ------------------------------------------------------------------------
# Qt5 gui framework
# ------------------------------------------------------------------------
from PyQt5.QtWidgets          import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore             import *
from PyQt5.QtGui              import *

# ------------------------------------------------------------------------
# developers own modules ...
# ------------------------------------------------------------------------
from exclasses import *     # exception: templates
from exapp     import *     # exception: application block placeholder
