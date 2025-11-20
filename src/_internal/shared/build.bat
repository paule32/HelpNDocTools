:: ---------------------------------------------------
:: \file  build.bat
:: \note  (c) 2025 by Jens Kallup - paule32
::        all rights reserved.
::
:: \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
:: ---------------------------------------------------
::nasm.exe -f bin -o kernel.bin kernel.asm
::nasm.exe -f bin -o modul1.bin modul1.asm

nasm.exe -E kernel.asm > kernel.pre
nasm.exe -E start.asm  > start.pre

nasm.exe -f bin -o kernel.bin kernel.asm -l kernel.lst
nasm.exe -f bin -o start.exe  start.asm  -l start.lst

::-w-zeroing
copy /b           start.exe start.bin
copy /b           start.exe dos.exe
upx.exe           start.exe

nasm -f bin getlang.asm -o getlang.com
