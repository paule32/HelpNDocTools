# ---------------------------------------------------------------------------
# File:   server.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------

import importlib
import subprocess
import sys           # system specifies
import os            # operating system stuff

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
from PyQt5.QtNetwork            import QTcpServer, QTcpSocket, QHostAddress 

try:
    # -----------------------------------------------------------------------
    # under the windows console, python paths can make problems ...
    # -----------------------------------------------------------------------
    def check_windows():
        result = False
        if 'PYTHONHOME' in os.environ:
            del os.environ['PYTHONHOME']
            result = True
        if 'PYTHONPATH' in os.environ:
            del os.environ['PYTHONPATH']
            result = True
        return result
    
    # ------------------------------------------------------------------------
    # before we start the application core, we try to update the pip installer
    # ------------------------------------------------------------------------
    def check_pip():
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
    
    class globalEnv:
        def __init__(self):
            self.app = None
            self.sub_window = None
    global genv
    genv = globalEnv()

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
    
    class SSLServer(QTcpServer):
        def __init__(self, cert_file, key_file, parent=None):
            super().__init__(parent)
            self.cert_file = cert_file
            self.key_file = key_file
            
            # Hier speichern wir unsere verbundenen Sockets:
            # Key: eine eindeutige ID (z.B. socketDescriptor oder einfach ein int-Counter)
            # Value: das jeweilige QSslSocket-Objekt
            self.clients = {}

            # Zähler, um jedem neuen Socket eine eindeutige ID zu geben
            self.client_counter = 0

        def incomingConnection(self, socketDescriptor):
            """Wird von Qt aufgerufen, wenn eine neue Verbindung reinkommt."""
            sslSocket = QSslSocket(self)

            # Zertifikat und Schlüssel laden
            certificate = QSslCertificate.fromPath(self.cert_file)[0]
            sslSocket.setLocalCertificate(certificate)

            with open(self.key_file, "rb") as f:
                key = QSslKey(
                    f.read(),
                    QSslKey.Rsa,
                    QSslKey.Pem,
                    QSslSocket.PrivateKey
                )
            sslSocket.setPrivateKey(key)

            # Socket-Descriptor übernehmen
            if not sslSocket.setSocketDescriptor(socketDescriptor):
                sslSocket.deleteLater()
                return

            # SSL-Handshake starten
            sslSocket.startServerEncryption()

            # Unsere interne ID vergeben:
            client_id = self.client_counter
            self.client_counter += 1

            # Im Dictionary speichern
            self.clients[client_id] = sslSocket

            # Signals verbinden
            sslSocket.encrypted.connect(lambda: self.on_encrypted(client_id))
            sslSocket.readyRead.connect(lambda: self.on_ready_read(client_id))
            sslSocket.disconnected.connect(lambda: self.on_disconnected(client_id))
            sslSocket.sslErrors.connect(self.on_ssl_errors)

            print(f"Neuer Client verbunden: {client_id}")

        def on_encrypted(self, client_id):
            print(f"Client {client_id} ist nun verschlüsselt verbunden.")

        def on_ready_read(self, client_id):
            sslSocket = self.clients.get(client_id)
            if not sslSocket:
                return

            data = sslSocket.readAll().data().decode()
            print(f"Server hat von Client {client_id} empfangen: {data}")
            # Hier kann man z. B. eine Antwort schicken
            # sslSocket.write("Nachricht an den Client".encode())

        def on_disconnected(self, client_id):
            """Wird aufgerufen, wenn der Client die Verbindung trennt."""
            sslSocket = self.clients.pop(client_id, None)
            if sslSocket:
                print(f"Client {client_id} disconnected.")
                sslSocket.deleteLater()

        def on_ssl_errors(self, errors):
            """Wird aufgerufen, wenn SSL-Fehler auftreten."""
            for err in errors:
                print(f"SSL Error: {err.errorString()}")
            # sslSocket.ignoreSslErrors() wäre eine Möglichkeit, bestimmte Fehler zu ignorieren
    
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
        
        check_windows()
        check_pip()
        check_and_install_module()
        
        genv.app = QApplication(sys.argv)
        server = NonBlockingServer()
        server.run()
        sys.exit(genv.app.exec_())
    
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
# ----------------------------------------------------------------------------
# E O F  -  End - Of - File
# ----------------------------------------------------------------------------
