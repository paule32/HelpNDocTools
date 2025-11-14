:: ---------------------------------------------------
:: \file  build.bat
:: \note  (c) 2025 by Jens Kallup - paule32
::        all rights reserved.
::
:: \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
:: ---------------------------------------------------
nasm.exe -f bin -o kernel.bin kernel.asm
nasm.exe -f bin -o start.exe  start.asm

::-w-zeroing
copy /b           start.exe start.bin
copy /b           start.exe dos.exe
upx.exe           start.exe

nasm -f bin getlang.asm -o getlang.com
