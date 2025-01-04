:: ---------------------------------------------------------------------------
:: Datei:  build.bat - Windows MS-DOS Batch file
:: Author: Jens Kallup - paule32
::
:: Rechte: (c) 2024 by kallup non-profit software
::         all rights reserved
::
:: only for education, and for non-profit usage !!!
:: commercial use ist not allowed.
:: ---------------------------------------------------------------------------
@echo off
set PY=python.exe
set BASEDIR=%cd%

python.exe client.cpython-313.pyc --gui
::python.exe client.cpython-313.pyc test.exe
