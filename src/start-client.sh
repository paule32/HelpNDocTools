#!/bin/bash
# ---------------------------------------------------------------------------
# File:   build.bat - Linux Batch file
# Author: Jens Kallup - paule32
#
# Rechte: (c) 2024, 2025 by kallup non-profit software
#         all rights reserved
#
# only for education, and for non-profit usage !!!
# commercial use is not allowed.
# ---------------------------------------------------------------------------

PYTHON=python3.13

## sudo apt install --reinstall python3-pip
## sudo apt install python3-pyqt5

sudo apt update
sudo apt install build-essential libstdc++5
sudo apt install build-essential libstdc++6

sudo apt update
sudo apt install qtbase-dev qtWebEngine-dev

sudo apt update
sudo apt install libssl-dev qtbase5-dev qt5-qmake

sudo apt install openssl

sudo apt update
sudo apt install libqtwebengine5 qtwebemgine-dev

sudo apt update
sudo apt install libqt5webengine5 libqtwebenginewidgets5 qtwebengine5-dev

# install latest python version
pip3 install --upgrade pip3

# uninstall all
pip3 uninstall PyQt5
pip3 uninstall PyQt5-sip
pip3 uninstall PyQtWebEmgine

sudo apt update

# install all
pip3 install PyQt5
pip3 install PyQt5-sip
pip3 install PyQtWebEmgine

pip3 install --upgrade PyQt5 PyQtWebEngine

sudo apt update
pip3 install --upgrade PyQt5

$PYTHON -m pip install PyQt5
$PYTHON -m pip install PyQtWebEngine

sudo apt install libgmp-dev

$PYTHON -m pip install polib
$PYTHON -m pip install dbf
$PYTHON -m pip install pefile
$PYTHON -m pip install capstone
$PYTHON -m pip install win32api
$PYTHON -m pip install screeninfo
$PYTHON -m pip install gmpy2

pip3 install PyQt5==5.15.7
pip3 install PyQt5==5.15.7 PyQtWebEngine==5.15.7
pip3 install PyQt5==5.15.7 PyQtWebEngineWidgets==5.15.7

$PYTHON -m compileall client-linux.py
cd ./__pycache__
$PYTHON client-linux.cpython-313.pyc --gui
cd ..

