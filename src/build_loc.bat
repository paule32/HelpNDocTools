:: ---------------------------------------------------------------------------
:: Datei:  build_loc.bat - Windows MS-DOS Batch file
:: Author: Jens Kallup - paule32
::
:: Rechte: (c) 2024 by kallup non-profit software
::         all rights reserved
::
:: only for education, and for non-profit usage !!!
:: commercial use ist not allowed.
:: ---------------------------------------------------------------------------
@echo off
echo create directories...

:: ---------------------------------------------------------------------------
:: for default, the neccassary localization directories, and file are already
:: exists. But I add a "mkdir" command, and return value check for future use
:: new languages can be add into the for range block.
:: ---------------------------------------------------------------------------
:: en => English
:: de => German
:: ---------------------------------------------------------------------------
mkdir __pycache__\_internal\locales\de_de\LC_MESSAGES
mkdir __pycache__\_internal\locales\en_us\LC_MESSAGES

set BASEDIR=%cd%

::set PYTHONPATH=
::%PY%\Lib;%PY%\Lib\site-packagesss
::set PYTHONHOME=
set SRC=%BASEDIR%/src
set VPA=%BASEDIR%/venv

cd %BASEDIR%\locales\de_de\LC_MESSAGES
rm -rf observer.mo.gz
msgfmt -o observer.mo observer.po
gzip -9 observer.mo
copy observer.mo.gz %BASEDIR%\__pycache__\_internal\locales\de_de\LC_MESSAGES

cd %BASEDIR%\locales\en_us\LC_MESSAGES
rm -rf observer.mo.gz
msgfmt -o observer.mo observer.po
gzip -9 observer.mo
copy observer.mo.gz %BASEDIR%\__pycache__\_internal\locales\en_us\LC_MESSAGES
