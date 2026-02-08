CROSS    ?= 
CC       := $(CROSS)gcc
LD       := $(CROSS)ld
OBJCOPY  := $(CROSS)objcopy

CFLAGS   := -m32 -ffreestanding -fno-builtin -nostdlib -nostartfiles \
            -Wall -Wextra -Wno-unused-value -Wno-unused-parameter
            
LDFLAGS  := -nostdlib -T kernel.ld
ASMFLAGS := -f win32 -DDOS_MODE=32

all: Makefile LOADER.COM KERNEL.BIN

# 16-Bit DOS-Loader (.COM)
LOADER.COM: loader.asm
	nasm -f bin loader.asm -o LOADER.COM

code32.o: code32.asm
	nasm $(ASMFLAGS) code32.asm -o code32.o

isr.o: isr.asm
	nasm $(ASMFLAGS) isr.asm -o isr.o

# compile C-Kernel:
kernel.o: kernel.c
	$(CC) $(CFLAGS) -c kernel.c -o kernel.o
    
util.o: util.c
	$(CC) $(CFLAGS) -c util.c -o util.o

# link Kernel with linker script:
kernel.coff: kernel.o code32.o isr.o util.o kernel.ld
	$(LD) $(LDFLAGS) -m i386pe -o kernel.coff \
    code32.o isr.o kernel.o util.o

# convert COFF-Kernel into flat Binary:
KERNEL.BIN: kernel.coff
	$(OBJCOPY) -O binary kernel.coff KERNEL.BIN

clean:
	rm -f *.o *.coff *.BIN *.COM
