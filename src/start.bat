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

echo Create Byte-Code...
%PY% -m compileall %BASEDIR%\observer.py
if errorlevel 1 ( goto error_bytecode )
::goto end
cd __pycache__
%PY% %BASEDIR%\__pycache__\observer.cpython-313.pyc --gui
if errorlevel 1 ( goto error_observer)
cd ..
goto all_done
:error_observer:
echo could not successfully run observer.py
echo aborted.
goto end 
:error_bytecode
echo could not create byte-code.
echo aborted.
goto end
:all_done
echo built and run successfull.
goto end
:end
