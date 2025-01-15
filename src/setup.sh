#!/bin/bash
# ---------------------------------------------------------------------------
# File:   build.bat - Linux bash file
# Author: Jens Kallup - paule32
#
# Rechte: (c) 2024, 2025 by kallup non-profit software
#         all rights reserved
#
# only for education, and for non-profit usage !!!
# commercial use is not allowed.
#
# this script install the needed Python3.13 packages on Ubuntu 24.10.1.
# it can take a while to install it...
# ---------------------------------------------------------------------------
PYTHON=python3.13

$PYTHON -m venv venv
source venv/bin/activate

#sudo apt install        \
#    python3-httpx       \
#    python3-network     \
#    python3-numpy       \
#    python3-polib       \
#                        \
#    python3-pyqt5.qtwebchannel          \
#    python3-pyqt5.qtwebengine           \
#    python3-pyqt5.qtwebkit              \
#    python3-pyqt5.qtwebsockets          \
#    python3-pyqt5.qtx11extras           \
#                                        \
#    python3-pyside2.qtcore              \
#    python3-pyside2.qtnetwork           \
#    python3-pyside2.qtgui               \
#    python3-pyside2.qtwebengine         \
#    python3-pyside2.qtwebenginecore     \
#    python3-pyside2.qtwebenginewidgets  \
#    python3-pyside2.qtwebsockets        \
#    python3-pyside2.qtwidgets           \
#                                \
#    python3-sip-dev             \
#                                \
#    python3-webview             \
#    python3-ws4py               \
#    python3-websockets          \
#    python3-websocket           \
#                                \
#    libqt5pdfwidgets5           \
#    libqt5webchannel5-dev       \
#    libqt5webengine-data        \
#    libqt5webenginecore5        \
#    libqt5webengine5            \
#    libqt5webenginewidgets5     \
#    libqt5webkit5-dev           \
#    libqt5websockets5-dev       \
#    libqt5webchannel5           \
#    libqt5webchannel5-dev       \
#    libqt5websockets5-dev       \
#    libqt5webview5-dev          \
#    libqt5networkauth5-dev

#sudo add-apt-repository ppa:deadsnakes/ppa
#sudo apt install python3.13-full

python3.13 -m ensurepip    --upgrade
python3.13 -m pip3 install --upgrade pip3

#sudo apt install --reinstall python3-pip
sudo apt install python3-pyqt5

sudo apt update
sudo apt install build-essential libstdc++6 openssl libssl-dev

sudo apt update
sudo apt install libqtwebengine5
sudo apt install qtbase5-dev qtwebengine5-dev qtwebengine5-dev-tools

sudo apt update
sudo apt install libqt5webengine5 libqtwebenginewidgets5 qtwebengine5-dev

# install latest python version
pip3 install --upgrade pip3

# uninstall all
#pip3 uninstall PyQt5
#pip3 uninstall PyQt5-sip
#pip3 uninstall PyQtWebEngine

#sudo apt update

# install all
$PYTHON -m pip install PyQt5          --break-system-packages
$PYTHON -m pip install PyQt5-sip      --break-system-packages
$PYTHON -m pip install PyQtWebEngine  --break-system-packages

#sudo apt update
#sudo apt install python3-sip

#pip3 install --upgrade PyQt5 PyQtWebEngine

#sudo apt update
#pip3 install --upgrade PyQt5

#$PYTHON -m pip install PyQt5          --break-system-packages
#$PYTHON -m pip install PyQtWebEngine  --break-system-packages

sudo apt install shiboken2
sudo apt install libshiboken2-dev libshiboken2-py3-5.15
sudo apt install libgmp-dev

$PYTHON -m pip install polib       --break-system-packages
$PYTHON -m pip install dbf         --break-system-packages
$PYTHON -m pip install ipapi       --break-system-packages
$PYTHON -m pip install pefile      --break-system-packages
$PYTHON -m pip install capstone    --break-system-packages
$PYTHON -m pip install screeninfo  --break-system-packages
$PYTHON -m pip install gmpy2       --break-system-packages

#pip install PyQt5
#pip install PyQt5sip
#pip install PyQt5WebEngine
#pip install PyQt5WebEngineWidgets

echo "done."
deactivate
