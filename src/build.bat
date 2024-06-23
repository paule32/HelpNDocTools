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
:: set observer application stuff ...
:: ---------------------------------------------------------------------------
set APP=observer
:: ---------------------------------------------------------------------------
:: the USERPROFILE directory contains the standard default installation of
:: Python 3.1.0 - there should be a Tools directory which comes with the
:: official installation files.
:: ---------------------------------------------------------------------------
set PY=E:\Python312
set PO=%PY%\Tools\i18n\msgfmt.py
set PX=%PY%\python.exe
::set PATH=%PY%;%PATH%
:: ---------------------------------------------------------------------------
:: First, check if python is installed. If not, try to install it, else try to
:: create the application.
:: ---------------------------------------------------------------------------
::if exists E:\Python310\python.exe goto buildApp
::if not exists %PY%\python.exe goto pythonSetup
:buildApp
set BASEDIR=%cd%
%PX% -V

::set PYTHONPATH=
::%PY%\Lib;%PY%\Lib\site-packagesss
::set PYTHONHOME=
set PRJ=E:/Projekte/HelpNDocTools

echo remove old data...
rm -rf build
rm -rf dist

::echo install packages...
::pip install regex

::pip install PyQt5
::pip install PyQtWebEngine

::pip install pyinstaller
::pip install --upgrade pyinstaller

echo create directories...  [

:: ---------------------------------------------------------------------------
:: for default, the neccassary localization directories, and file are already
:: exists. But I add a "mkdir" command, and return value check for future use
:: new languages can be add into the for range block.
:: ---------------------------------------------------------------------------
:: en => English
:: de => German
:: ---------------------------------------------------------------------------
for %%A in (en_us, de_de) do (
    cd %BASEDIR%
    dir /A:D %BASEDIR%\locales  >nul 2>&1
    if errorlevel 0 (
        mkdir %BASEDIR%\locales >nul 2>&1
        dir /A:D %BASEDIR%\locales\%%A  >nul 2>&1
        if errorlevel 0 (
            echo|set /p="%%A => "
            mkdir %BASEDIR%\locales\%%A >nul 2>&1
            dir /A:D locales\%%A\LC_MESSAGES >nul 2>&1
            if errorlevel 0 (
                echo|set /p="ok, "
                mkdir locales\%%A\LC_MESSAGES >nul 2>&1
                cd %BASEDIR%\locales\%%A\LC_MESSAGES
                echo|set /p="locales compiled => "
                msgfmt -o ^
                %BASEDIR%\locales\%%A\LC_MESSAGES\observer.mo ^
                %BASEDIR%\locales\%%A\LC_MESSAGES\observer.po
                if errorlevel 0 (
                    echo|set /p="[ ok   ], "
                )   else (
                    echo|set /p="[ fail ], "
                )
            )
        )
    )
)
echo ]
goto TheEnd
:: ---------------------------------------------------------------------------
:: Python can produce byte-code, and executable files to speed up the loading
:: and for information hidding ...
:: ---------------------------------------------------------------------------
cd %BASEDIR%
echo Create Byte-Code...
cd tools
python -m compileall tool001.py
if errorlevel 1 (
    echo fail tool001.pyc
    goto error_bytecode)  else ( echo tool001.pyc created )
python tool001.py
if errorlevel 1 (
    echo fail tool001 batch
    goto error_bytecode ) else ( echo tool001.py exec ok )
python -m compileall collection.py
if errorlevel 1 (
    echo fail collection.pyc
    goto error_bytecode ) else ( echo collection.pyc created )
python collection.py
if errorlevel 1 (
    echo fail collection batch
    goto error_bytecode ) else ( echo collection.py exec ok )
cd ..
%PY%\python.exe -m compileall %BASEDIR%\observer.py
if errorlevel 1 ( goto error_bytecode )
echo  ok   ]
pyinstaller --noconfirm --console  ^
    --icon="%PRJ%/src/img/floppy-disk.ico"  ^
    --clean       ^
    --log-level="WARN"   ^
    --splash="%PRJ%/src/img/splash.png"     ^
    --strip                                 ^
    --hide-console="minimize-late"          ^
    --version-file="%PRJ%/src/version.info" ^
    ^
    --paths=./                              ^
    --paths="C:/Windows/System32"           ^
    --paths="C:/Windows/SysWOW64"           ^
    ^
    --paths="%PRJ%/src/interpreter/doxygen" ^
    --paths="%PRJ%/src/interpreter/pascal"  ^
    --paths="%PRJ%/src/interpreter/dbase"   ^
    --paths="%PRJ%/src/interpreter"         ^
    --paths="%PRJ%/src/tools"               ^
    --paths="%PRJ%/src"                     ^
    ^
    --add-data="%PRJ%/src/locales;locales/" ^
    --add-data="%PRJ%/src/img;img/"         ^
    --add-data="%PRJ%/LICENSE;."            ^
    --add-data="%PRJ%/README.md;."          ^
    --add-data="%PRJ%/CONTRIBUTING.md;."    ^
    --add-data="%PRJ%/CODE_OF_CONDUCT.md;." ^
    --add-data="%PRJ%/src/topics.txt;."     ^
    --add-data="%PRJ%/src/test.byte;."      ^
    --add-data="%PRJ%/src/test.txt;."       ^
    ^
    --collect-submodules="%PRJ%/src/exapp.py"            ^
    --collect-submodules="%PRJ%/src/exclasses.py"        ^
    --collect-submodules="%PRJ%/src/appcollection.py"    ^
    --collect-submodules="%PRJ%/src/__init__.py"         ^
    --collect-submodules="%PRJ%/src/tools/collection.py" ^
    --collect-submodules="%PRJ%/src/tools/data001.py"    ^
    --collect-submodules="%PRJ%/src/tools/data002.py"    ^
    --collect-submodules="%PRJ%/src/tools/data003.py"    ^
    --collect-submodules="%PRJ%/src/tools/data004.py"    ^
    --collect-submodules="%PRJ%/src/tools/data005.py"    ^
    --collect-submodules="%PRJ%/src/tools/misc.py"       ^
    --collect-submodules="%PRJ%/src/tools/__init__.py"   ^
    --collect-submodules="%PRJ%/src/interpreter/EParserException.py" ^
    --collect-submodules="%PRJ%/src/interpreter/ParserDSL.py"        ^
    --collect-submodules="%PRJ%/src/interpreter/RunTimeLibrary.py"   ^
    --collect-submodules="%PRJ%/src/interpreter/VisualComponentLibrary.py" ^
    --collect-submodules="%PRJ%/src/interpreter/doxygen/doxygen.py"        ^
    --collect-submodules="%PRJ%/src/interpreter/dbase/dbaseConsole.py"     ^
    --collect-submodules="%PRJ%/src/interpreter/dbase/dbase.py"   ^
    --collect-submodules="%PRJ%/src/interpreter/pascal/pascal.py" ^
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
    "%PRJ%/src/observer.py"
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
echo,
echo exit without error's, done.

cd dist\observer
touch test.txt
cd ..\..
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


::auto-py-to-exe 
