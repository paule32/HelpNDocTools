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
    
    class ClientHandlerThread(QThread):
        new_data = pyqtSignal(QTcpSocket, str)
        client_disconnected = pyqtSignal(QTcpSocket)

        def __init__(self, client_socket):
            super().__init__()
            self.client_socket = client_socket
            self.client_socket.readyRead.connect(self.read_data)
            self.client_socket.disconnected.connect(lambda: self.handle_disconnection(self.client_socket))

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

    class NonBlockingServer(QMainWindow):
        def __init__(self, port=1234):
            super().__init__()
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

        def handle_new_connection(self):
            # Hole den eingehenden Socket
            client_socket = self.server.nextPendingConnection()
            client_address = client_socket.peerAddress().toString()
            client_port = client_socket.peerPort()
            
            # Überprüfen, ob eine Verbindung von derselben Adresse bereits existiert
            if client_address in self.connections:
                print(f"Vorhandene Verbindung von {client_address} erkannt. Öffne virtuellen Port.")
                virtual_port = client_port + 1  # Öffne einen virtuellen Port
                self.connections[(client_address, virtual_port)] = client_socket
            else:
                # Speichere die neue Verbindung
                self.connections[(client_address, client_port)] = client_socket
            
            # Neues MDI-Fenster für die Verbindung
            genv.sub_window = QTextEdit()
            genv.sub_window.setWindowTitle(f"Verbindung von {client_address}:{client_port}")
            self.mdi_area.addSubWindow(genv.sub_window)
            genv.sub_window.show()
            client_socket.sub_window_ref = genv.sub_window
            
            client_socket.text_edit = genv.sub_window  # Verknüpfen Sie das Textfeld mit dem Socket

            # Erstelle und starte einen neuen Thread zur Bearbeitung des Clients
            thread = ClientHandlerThread(client_socket)
            thread.new_data.connect(self.display_data)
            thread.client_disconnected.connect(self.handle_disconnection)
            thread.start()
            self.threads.append(thread)

        def display_data(self, client_socket, data):
            try:
                # Überprüfe, ob das Fenster existiert und nicht gelöscht wurde
                if client_socket.sub_window_ref is None:
                    # Fenster wurde gelöscht, erstelle es neu
                    genv.sub_window = QTextEdit()
                    genv.sub_window.setWindowTitle(f"Verbindung von {client_socket.peerAddress().toString()}:{client_socket.peerPort()}")
                    self.mdi_area.addSubWindow(genv.sub_window)
                    genv.sub_window.show()
                    client_socket.sub_window_ref = genv.sub_window
                    print("Neues Verbindungsfenster erstellt.")
                
                
                print(f"Empfangene Daten: {data}")
                
                # Ausgabe im MDI-Fenster
                #if client_socket.sub_window_ref is not None:
                #    if genv.sub_window == None:
                #        genv.sub_window = QTextEdit()
                #        genv.sub_window.hide()
                #        self.mdi_area.addSubWindow(genv.sub_window)
                #        genv.sub_window.show()
                #        client_socket.sub_window_ref.append(f"Empfangen: {data}")
                
                # Sende eine Antwort zurück
                response = f"Server: Deine Nachricht war '{data}'"
                client_socket.write(response.encode())
                client_socket.flush()
                
                #if client_socket.sub_window_ref is not None:
                #    genv.sub_window = QTextEdit()
                #    genv.sub_window.hide()
                #    self.mdi_area.addSubWindow(genv.sub_window)
                #    genv.sub_window.show()
                #    print("----121212")
                        
                #client_socket.sub_window_ref = genv.sub_window   
                #client_socket.sub_window_ref.append(f"Gesendet: {response}")
                    
            except Exception as e:
                print(f"Fehler beim Verarbeiten der Daten: {e}")
                print(f"Empfangene Daten: {data}")
                
                # Ausgabe im MDI-Fenster
                client_socket.sub_window_ref.append(f"Empfangen: {data}")
                
                # Sende eine Antwort zurück
                response = f"Server: Deine Nachricht war '{data}'"
                client_socket.write(response.encode())
                client_socket.flush()
                client_socket.sub_window_ref.append(f"Gesendet: {response}")
            except Exception as e:
                print(f"Fehler beim Verarbeiten der Daten: {e}")
            print(f"Empfangene Daten: {data}")
            
            # Ausgabe im MDI-Fenster
            try:
                client_socket.sub_window_ref.append(f"Empfangen: {data}")
                
                # Sende eine Antwort zurück
                response = f"Server: Deine Nachricht war '{data}'"
                client_socket.write(response.encode())
                client_socket.flush()
                client_socket.sub_window_ref.append(f"Gesendet: {response}")
            except Exception as err:
                print(err)
                # Fenster wurde gelöscht, erstelle es neu
                genv.sub_window = QTextEdit()
                genv.sub_window.setWindowTitle(f"Verbindung von {client_socket.peerAddress().toString()}:{client_socket.peerPort()}")
                self.mdi_area.addSubWindow(genv.sub_window)
                genv.sub_window.show()
                client_socket.sub_window_ref = genv.sub_window
                client_socket.sub_window_ref.append(f"Empfangen: {data}")
                
                # Sende eine Antwort zurück
                response = f"Server: Deine Nachricht war '{data}'"
                client_socket.write(response.encode())
                client_socket.flush()
                client_socket.sub_window_ref.append(f"Gesendet: {response}")

        def handle_disconnection(self, client_socket):
            try:
                # Entferne die Verbindung aus der Liste
                client_address = client_socket.peerAddress().toString()
                client_port = client_socket.peerPort()
                
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
                client_socket.sub_window_ref = None
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
