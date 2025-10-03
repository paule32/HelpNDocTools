:: ---------------------------------------------------------------------------
:: Datei:  build_loc.bat - Windows MS-DOS Batch file
:: Author: Jens Kallup - paule32
::
:: Rechte: (c) 2024, 2ß25 by kallup non-profit software
::         all rights reserved
:: ---------------------------------------------------------------------------
@echo off
setlocal EnableExtensions DisableDelayedExpansion

set "PS=%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe"
:: ---------------------------------------------------------------------------
:: Optional: PowerShell 7 bevorzugen, falls vorhanden
:: ---------------------------------------------------------------------------
if exist "%ProgramFiles%\PowerShell\7\pwsh.exe" set "PS=%ProgramFiles%\PowerShell\7\pwsh.exe"

"%PS%" -NoProfile -ExecutionPolicy Bypass -NonInteractive -File "%~dp0setup.ps1" --mode GUI --version 3.13 > nul
exit /b %errorlevel%
