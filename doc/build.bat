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
cd src
copy /B /Y dummy.hnd help.hnd
hnd9.exe help.hnd ^
    script ^
    -file=".\demo.pas"
copy /B /Y help.hnd ..\help.hnd
cd ..
::-verysilent