:: ----------------------------------------------------------------------------
:: setup: (c) 2024 Jens Kallup - paule32
:: all rights reserved.
::
:: This barch file try to help to automate some steps for a setup of an running
:: system of this Project. The scripts are developer machiene optimized. So, it
:: can be that not all path's are correct nor all applications are available.
:: ----------------------------------------------------------------------------
@echo off
set ThisScriptsDirectory=%~dp0
set ScriptPath_001=%ThisScriptsDirectory%AddHostsEntry.ps1
set ScriptPath_002=%ThisScriptsDirectory%CheckHostsEntry.ps1

set pwsh=powershell -NoProfile -ExecutionPolicy Bypass -Command

%pwsh% "& '%ScriptPath_002%'"
%pwsh% "& '%PowerShellScriptPath%' fd01:1:1:10:: help"
