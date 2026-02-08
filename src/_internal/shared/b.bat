@echo off
setlocal EnableExtensions EnableDelayedExpansion

.\dos.exe
echo s32 dez: %ERRORLEVEL%

set "CODE=%ERRORLEVEL%"

if %ERRORLEVEL% LSS 0 (
    rem 2^32 add: 4294967296
    set /a CODE=%ERRORLEVEL% + 4294967296
)

echo u32 dez: !CODE!

for /f %%H in ('powershell -NoP -C "('{0:X8}' -f %CODE%)"') do set "HEX=%%H"
echo hex: 0x%HEX%

endlocal
