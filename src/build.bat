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
:start
:: ---------------------------------------------------------------------------
:: set application stuff ...
:: ---------------------------------------------------------------------------
set SRVAPP=server.py
set CLTAPP=client.py
:: ---------------------------------------------------------------------------
:: the USERPROFILE directory contains the standard default installation of
:: Python 3.1.0 - there should be a Tools directory which comes with the
:: official installation files.
:: ---------------------------------------------------------------------------
set PY=python.exe
set PO=msgfmt.exe

:: ---------------------------------------------------------------------------
:: First, check if python is installed. If not, try to install it, else try to
:: create the application.
:: ---------------------------------------------------------------------------
::if exists E:\Python310\python.exe goto buildApp
::if not exists %PY%\python.exe goto pythonSetup
:buildApp
set BASEDIR=%cd%

::set PYTHONPATH=
::%PY%\Lib;%PY%\Lib\site-packagesss
::set PYTHONHOME=
set SRC=%BASEDIR%/src
set VPA=%BASEDIR%/venv

:: ---------------------------------------------------------------------------
:: check, if Python is installed ...
:: ---------------------------------------------------------------------------
echo try to setup develop system...
python3 --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b 1
)

:: ---------------------------------------------------------------------------
:: create virtual user environment...
:: ---------------------------------------------------------------------------
python3 -m venv venv
if errorlevel 1 (
    echo "Error: can not setup the virtual environment."
    pause
    exit /b 1
)

for /f "tokens=2 delims=:." %%a in ('"%SystemRoot%\System32\chcp.com"') do (
    set _OLD_CODEPAGE=%%a
)
if defined _OLD_CODEPAGE (
    "%SystemRoot%\System32\chcp.com" 65001 > nul
)

set VIRTUAL_ENV=%BASEDIR%\venv

if not defined PROMPT set PROMPT=$P$G

if defined _OLD_VIRTUAL_PROMPT     set PROMPT=%_OLD_VIRTUAL_PROMPT%
if defined _OLD_VIRTUAL_PYTHONHOME set PYTHONHOME=%_OLD_VIRTUAL_PYTHONHOME%

set "_OLD_VIRTUAL_PROMPT=%PROMPT%"
set "PROMPT=(venv) %PROMPT%"

if defined PYTHONHOME set _OLD_VIRTUAL_PYTHONHOME=%PYTHONHOME%
set PYTHONHOME=

if defined _OLD_VIRTUAL_PATH set PATH=%_OLD_VIRTUAL_PATH%
if not defined _OLD_VIRTUAL_PATH set _OLD_VIRTUAL_PATH=%PATH%

set PATH=%VIRTUAL_ENV%\Scripts;%PATH%
set VIRTUAL_ENV_PROMPT=venv

cd %BASEDIR%\venv\Scripts
dir

:: ---------------------------------------------------------------------------
:: check, if pip3 is installed ...
:: ---------------------------------------------------------------------------
python -m pip install --upgrade pip >nul 2>&1
if errorlevel 1 (
    echo pip is not installed. Try to install pip...
    python -m ensurepip
    if errorlevel 1 (
        echo Error: could not install pip. Please install it manually.
        pause
        exit /b 1
    )
)
python -m pip install --upgrade pip
python -m pip install ast >nul 2>&1

echo install requirements...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo Error: could not install requirement's.
    pause
    exit /b 1
)

:: ---------------------------------------------------------------------------
:: install windows stuff ...
:: ---------------------------------------------------------------------------
pip install pywin32
python -m   pywin32_postinstall -install

echo remove old data...
cd venv

rm -rf build
rm -rf dist

::echo install packages...
::pip install regex

::pip install PyQt5
::pip install PyQtWebEngine

::pip install pyinstaller
::pip install --upgrade pyinstaller

cd %BASEDIR%
build_loc.bat

:: ---------------------------------------------------------------------------
:: Python can produce byte-code, and executable files to speed up the loading
:: and for information hidding ...
:: ---------------------------------------------------------------------------
cd %BASEDIR%
echo Create Byte-Code...
::cd tools
::python -m compileall tool001.py
::if errorlevel 1 (
::    echo fail tool001.pyc
::    goto error_bytecode)  else ( echo tool001.pyc created )
::python tool001.py
::if errorlevel 1 (
::    echo fail tool001 batch
::    goto error_bytecode ) else ( echo tool001.py exec ok )
::python -m compileall collection.py
::if errorlevel 1 (
::    echo fail collection.pyc
::    goto error_bytecode ) else ( echo collection.pyc created )
::python collection.py
::if errorlevel 1 (
::    echo fail collection batch
::    goto error_bytecode ) else ( echo collection.py exec ok )
::cd ..
python -m compileall %BASEDIR%\%SRVAPP%
if errorlevel 1 ( goto error_bytecode )
python -m compileall %BASEDIR%\%CLTAPP%
if errorlevel 1 ( goto error_bytecode )
exit
echo installer...
pyinstaller --noupx --noconfirm --console  ^
    --icon="%PRJ%/_internal/img/floppy-disk.ico"  ^
    --clean       ^
    --exclude-module tkinter ^
    --exclude-module tk      ^
    --exclude-module tk86t      ^
    --exclude-module tcl86t     ^
    --log-level="WARN"   ^
    --splash="%PRJ%/_internal/img/splash.png"     ^
    --strip                                 ^
    --hide-console="minimize-late"          ^
    --version-file="%PRJ%/version.info" ^
    ^
    --paths=./                              ^
    --paths="C:/Windows/System32"           ^
    --paths="C:/Windows/SysWOW64"           ^
    ^
    --paths="%PRJ%/src"                     ^
    ^
    --collect-submodules="%PRJ%/src/__init__.py"         ^
    ^
    --hidden-import="shutil"          ^
    --hidden-import="types"           ^
    --hidden-import="_ctypes"         ^
    --hidden-import="encodings"       ^
    --hidden-import="ctypes.util"     ^
    --hidden-import="collections"     ^
    --hidden-import="operator"        ^
    --hidden-import="reprlib"         ^
    --hidden-import="functools"       ^
    --hidden-import="enum"            ^
    --hidden-import="sip"             ^
    --hidden-import="collections.abc" ^
    --hidden-import="warnings"        ^
    --hidden-import="linecache"       ^
    --hidden-import="re"              ^
    --hidden-import="sre_compile"     ^
    --hidden-import="sre_parse"       ^
    --hidden-import="sre_constants"   ^
    --hidden-import="copyreg"         ^
    ^
    "%PRJ%/observer.py"
goto TheEnd
:: ---------------------------------------------------------------------------
:: to create Windows executables, you have to install pyinstaller seperatly.
:: after pyinstaller success the executable resides in ./dist folder.
:: ---------------------------------------------------------------------------
echo|set /p="create ExEcutable...          ["
pyinstaller %BASEDIR%\observer.spec
:: >nul 2>&1
if errorlevel 1 (
    echo  fail ]
    goto error_executable
)   else (
    echo  ok   ]
    goto TheEnd
    echo|set /p="create Certificate...       ["
    :: -----------------------------------------------------------------------
    :: finally, try to sign the executable with a certificate, that we will
    :: create with powershell, and the MS-SDK signtool.
    :: this reqauire, that you have powershell access on modern Windows.
    :: -----------------------------------------------------------------------
    powershell.exe -executionpolicy remotesigned -File %BASEDIR%\gencert.cmd
    if errorlevel 1 (
        echo  ok   ]
    )   else (
        echo  fail ]
    )
)
goto TheEnd
:: ---------------------------------------------------------------------------
:: todo: python setup !
:: ---------------------------------------------------------------------------
:pythonSetup
echo python 3.10 is not installed, yet
goto TheEnd
:: ---------------------------------------------------------------------------
:: no errors was detected - normal exit.
:: ---------------------------------------------------------------------------
:TheEnd
if exist "dist" (
    cd dist
    if exist "observer" (
        cd observer
        mkdir _internal\_internal
        mkdir _internal\_internal\img\flags
        mkdir _internal\_internal\locales\de_de\LC_MESSAGES
        mkdir _internal\_internal\locales\en_us\LC_MESSAGES
        copy ..\..\locales\de_de\LC_MESSAGES\observer.mo.gz _internal\_internal\locales\de_de\LC_MESSAGES\observer.mo.gz
        copy ..\..\locales\en_us\LC_MESSAGES\observer.mo.gz _internal\_internal\locales\en_us\LC_MESSAGES\observer.mo.gz
        copy ..\..\observer.ini _internal\_internal\observer.ini
        copy ..\..\__pycache__\_internal\img\flags\*.gif _internal\_internal\img\flags\
        copy ..\..\__pycache__\_internal\img\*.gif _internal\_internal\img\
        copy ..\..\__pycache__\_internal\img\*.png _internal\_internal\img\
        copy ..\..\__pycache__\_internal\img\*.bmp _internal\_internal\img\
        copy ..\..\__pycache__\_internal\img\*.ico _internal\_internal\img\
        copy ..\..\__pycache__\_internal\favorites.ini _internal\_internal\favorites.ini
        copy ..\..\topics.txt _internal\_internal\topics.txt
        touch test.txt
    )   else (
        echo observer directory does not exists.
        goto error
    )
)   else (
    goto endstep
    echo dist directory does not exists.
    goto error
)
:endstep
cd %BASEDIR%
echo.
echo exit without error's, done.
goto skipper

:: ---------------------------------------------------------------------------
:: all other cases that produce errors - inform the user with nice messages:
:: ---------------------------------------------------------------------------
:error_bytecode
echo.
echo Error: can't create Byte-Code
goto error

:error_executable
echo.
echo Error: could not create executable.
goto error

:error_lc_messages
echo.
echo Error occured: LC_MESSAGES
goto error

:error
echo.
echo "process, fail"
goto skipper

:skipper

:: ---------------------------------------------------------------------------
:: E - O - F   End of File
:: ---------------------------------------------------------------------------
