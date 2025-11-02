nasm.exe -fbin -o start.exe start.asm
copy /b           start.exe start.bin
 upx.exe          start.exe