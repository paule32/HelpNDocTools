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
            self.sub_window_list = []
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
    
    class ClientHandlerThread(QThread):
        new_data = pyqtSignal(QTcpSocket, str)
        client_disconnected = pyqtSignal(QTcpSocket)

        def __init__(self, client_socket):
            super().__init__()
            self.client_socket = client_socket
            self.client_socket.readyRead.connect(self.read_data)
            self.client_socket.disconnected.connect(self.handle_disconnection)

        def read_data(self):
            try:
                if self.client_socket.state() == QTcpSocket.ConnectedState:
                    if self.client_socket.bytesAvailable() > 0:
                        data = self.client_socket.readAll().data().decode()
                        self.new_data.emit(self.client_socket, data)
                    else:
                        print("Keine Daten verfügbar, schließe die Verbindung.")
                        self.client_socket.disconnectFromHost()
            except Exception as e:
                print(f"Fehler beim Lesen der Daten: {e}")

        def handle_disconnection(self):
            self.client_disconnected.emit(self.client_socket)
            
    class DataWindow(QMdiSubWindow):
        def __init__(self, parent=None, socket=None, title=""):
            super(DataWindow, self).__init__(parent)
            
            self.parent    = parent
            self.socket    = socket
            
            self.client_address = socket.peerAddress().toString()
            self.client_port    = socket.peerPort()
            
            self.text_edit = QTextEdit()
            
            self.setWidget(self.text_edit)
            self.setWindowTitle(title)
            self.setObjectName(f"client:{socket.peerAddress().toString()}:{socket.peerPort()}")
            
        def add_text(self, text):
            self.text_edit.append(f"{text}")
    
    class NonBlockingServer(QMainWindow):
        def __init__(self, port=1234):
            super().__init__()
            
            self.crt_file = os.getcwd() + "/_internal/server.crt"
            self.key_file = os.getcwd() + "/_internal/server.key"
            
            # Zertifikat und Schlüssel laden
            #certificate = QSslCertificate.fromPath(self.cert_file)[0]
            #sslSocket.setLocalCertificate(certificate)
        
            self.init_ui()
            
            # Erstelle einen TCP Server
            self.server = QTcpServer()
            self.server.listen(QHostAddress.Any, port)
            self.server.newConnection.connect(self.handle_new_connection)
            
            # Speichert die Verbindungen nach Adresse und Port
            self.connections = {}
            self.threads = []
            
            print(f"Server gestartet. Lauscht auf Port {port}...")

        def init_ui(self):
            self.setWindowTitle("MDI Server")
            self.setGeometry(100, 100, 800, 600)
            
            self.mdi_area = QMdiArea()
            self.setCentralWidget(self.mdi_area)
            
            self.statusBar().showMessage("Server bereit...")
            
            # Menü und Aktionen
            menubar = self.menuBar()
            file_menu = menubar.addMenu("&Datei")
            exit_action = QAction("Beenden", self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
        
        def delete_subwindow(self, title):
            # Alle Subfenster ermitteln
            for sub_window in self.mdi_area.subWindowList():
                # Vergleich mit dem gesuchten Titel
                if sub_window.windowTitle() == title:
                    sub_window.close()
                    # Wenn Sie nur das erste gefundene Fenster schließen möchten,
                    # beenden Sie hier die Schleife
                    break
            
        def handle_new_connection(self):
            # Hole den eingehenden Socket
            
            client_socket  = self.server.nextPendingConnection()
            client_address = client_socket.peerAddress().toString()
            client_port    = client_socket.peerPort()
            
            # -------------------------------------
            # Neues MDI-Fenster für die Verbindung
            # -------------------------------------
            sub_window = DataWindow(self,
                client_socket,
                f"Client: {client_address}:{client_port}")
            
            # Überprüfen, ob eine Verbindung von derselben Adresse bereits existiert
            if client_address in self.connections:
                print(f"Vorhandene Verbindung von {client_address} erkannt. Öffne virtuellen Port.")
                virtual_port = client_port + 1
                self.connections[(client_address, virtual_port)] = client_socket
            else:
                # Speichere die neue Verbindung
                self.connections[(client_address, client_port )] = client_socket
            
            # SubWindow dem MdiArea hinzufügen
            self.mdi_area.addSubWindow(sub_window)
            sub_window.show()
            
            # Erstelle und starte einen neuen Thread zur Bearbeitung des Clients
            thread = ClientHandlerThread(client_socket)
            thread.new_data.connect(self.display_data)
            thread.client_disconnected.connect(self.handle_disconnection)
            thread.start()
            self.threads.append(thread)
        
        def display_data(self, client_socket, data):
            try:
                # Überprüfe, ob das Fenster existiert und nicht gelöscht wurde
                #if client_socket is None:
                # Fenster wurde gelöscht, erstelle es neu
                sub_window = DataWindow(self, client_socket)
                
                found = False
                for win in genv.sub_window_list:
                    if win.socket == client_socket:
                        found = True
                        break
                if not found:
                    genv.sub_window_list.append(sub_window)
                    print("Neues Verbindungsfenster erstellt.")
                
                # -----------------------
                # Ausgabe im MDI-Fenster
                # -----------------------
                for win in self.mdi_area.subWindowList():
                    if win.objectName() == f"client:{client_socket.peerAddress().toString()}:{client_socket.peerPort()}":
                        for res in genv.sub_window_list:
                            if res.objectName() == win.objectName():
                                print(f"11Empfangen: {data}")
                                win.text_edit.append(f"Empfangen: {data}")
                                break
                
                # Sende eine Antwort zurück
                #response = f"Server: Deine Nachricht war '{data}'"
                #client_socket.write(response.encode())
                #client_socket.flush()
                
                
            except Exception as e:
                print(f"Fehler beim Verarbeiten der Daten: {e}")
                print(f"22Empfangene Daten: {data}")
                
                # Ausgabe im MDI-Fenster
                data = f"22Empfangen: {data}"
                client_socket.write(data.encode())
                client_socket.flush()
                
                # Sende eine Antwort zurück
                #response = f"Server: Deine Nachricht war '{data}'"
                #client_socket.write(response.encode())
                #client_socket.flush()
                #client_socket.sub_window_ref.append(f"Gesendet: {response}")
        
        def handle_disconnection(self, client_socket):
            try:
                # Entferne die Verbindung aus der Liste
                client_address = client_socket.peerAddress().toString()
                client_port    = client_socket.peerPort()
                
                self.delete_subwindow(f"Client: {client_address}:{client_port}")
                
                # Finde die richtige Verbindung und entferne sie
                for key in list(self.connections.keys()):
                    if key[0] == client_address and self.connections[key] == client_socket:
                        print(f"Verbindung von {client_address} wurde getrennt.")
                        del self.connections[key]
                        break
                
                # Entferne den zugehörigen Thread aus der Thread-Liste
                for thread in self.threads:
                    if thread.client_socket == client_socket:
                        self.threads.remove(thread)
                        thread.quit()
                        thread.wait()
                        break
                
                client_socket.deleteLater()
                #client_socket.sub_window_ref = None
                print("Client-Socket erfolgreich gelöscht und der Server bleibt in Betrieb.")
                self.statusBar().showMessage("Verbindung geschlossen. Warte auf neue Verbindungen...")
            except Exception as e:
                print(f"Fehler beim Verarbeiten der Trennung: {e}")

        def run(self):
            # Starte die Qt Event Schleife
            self.show()
    
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
