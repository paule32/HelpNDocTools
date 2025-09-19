:: ---------------------------------------------------------------------------
:: Datei:  build_loc.bat - Windows MS-DOS Batch file
:: Author: Jens Kallup - paule32
::
:: Rechte: (c) 2024, 2ß25 by kallup non-profit software
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

mkdir __pycache__\_internal\locales\de_de\LC_HELP
mkdir __pycache__\_internal\locales\en_us\LC_HELP

mkdir __pycache__\_internal\locales\en_us\LC_STYLE
mkdir __pycache__\_internal\locales\de_de\LC_STYLE

mkdir __pycache__\_internal\locales\en_us\LC_META
mkdir __pycache__\_internal\locales\de_de\LC_META

set BASEDIR=%cd%

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
:: ----------------------------------

::cd %BASEDIR%\locales\de_de\LC_HELP
::rm -rf help.mo.gz
::msgfmt -o help.mo help.po
::gzip -9 help.mo
::copy help.mo.gz %BASEDIR%\__pycache__\_internal\locales\de_de\LC_HELP

::cd %BASEDIR%\locales\en_us\LC_HELP
::rm -rf help.mo.gz
::msgfmt -o help.mo help.po
::gzip -9 help.mo
::copy help.mo.gz %BASEDIR%\__pycache__\_internal\locales\en_us\LC_HELP
:: ----------------------------------

cd %BASEDIR%\locales\de_de\LC_STYLE
rm -rf observer.mo.gz
msgfmt -o observer.mo observer.po
gzip -9 observer.mo
copy observer.mo.gz %BASEDIR%\__pycache__\_internal\locales\de_de\LC_STYLE

cd %BASEDIR%\locales\en_us\LC_STYLE
rm -rf observer.mo.gz
msgfmt -o observer.mo observer.po
gzip -9 observer.mo
copy observer.mo.gz %BASEDIR%\__pycache__\_internal\locales\en_us\LC_STYLE
:: ----------------------------------

cd %BASEDIR%\locales\de_de\LC_META
rm -rf pcbios.mo.gz
rm -rf parser.mo.gz
rm -rf electro.mo.gz
rm -rf keyboard.mo.gz

msgfmt -o pcbios.mo   pcbios.po
msgfmt -o parser.mo   parser.po
msgfmt -o electro.mo  electro.po
msgfmt -o keyboard.mo keyboard.po

gzip -9 pcbios.mo
gzip -9 parser.mo
gzip -9 electro.mo
gzip -9 keyboard.mo

copy pcbios.mo.gz   %BASEDIR%\__pycache__\_internal\locales\de_de\LC_META
copy parser.mo.gz   %BASEDIR%\__pycache__\_internal\locales\de_de\LC_META
copy electro.mo.gz  %BASEDIR%\__pycache__\_internal\locales\de_de\LC_META
copy keyboard.mo.gz %BASEDIR%\__pycache__\_internal\locales\de_de\LC_META

cd %BASEDIR%\locales\en_us\LC_META
rm -rf pcbios.mo.gz
rm -rf parser.mo.gz
rm -rf electro.mo.gz
rm -rf keyboard.mo.gz

msgfmt -o pcbios.mo   pcbios.po
msgfmt -o parser.mo   parser.po
msgfmt -o electro.mo  electro.po
msgfmt -o keyboard.mo keyboard.po

gzip -9 pcbios.mo
gzip -9 parser.mo
gzip -9 electro.mo
gzip -9 keyboard.mo

copy pcbios.mo.gz   %BASEDIR%\__pycache__\_internal\locales\en_us\LC_META
copy parser.mo.gz   %BASEDIR%\__pycache__\_internal\locales\en_us\LC_META
copy electro.mo.gz  %BASEDIR%\__pycache__\_internal\locales\en_us\LC_META
copy keyboard.mo.gz %BASEDIR%\__pycache__\_internal\locales\en_us\LC_META
:: ----------------------------------
cd %BASEDIR%
pyrcc5 resources.qrc -o resources_rc.py
python -m compileall    resources_rc.py

python -m compileall  client-windows.py

exit
python -m compileall TObject.py
python -m compileall TStream.py
python -m compileall TMemory.py
python -m compileall TException.py

python -m compileall client-windows.py
python -m compileall start-client.py
