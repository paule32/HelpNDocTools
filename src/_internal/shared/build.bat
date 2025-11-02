:: ---------------------------------------------------
:: \file  build.bat
:: \note  (c) 2025 by Jens Kallup - paule32
::        all rights reserved.
::
:: \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
:: ---------------------------------------------------
nasm.exe -fbin -o start.exe start.asm -w-zeroing
copy /b           start.exe start.bin
upx.exe           start.exe
