CROSS   ?= 
CC      := $(CROSS)gcc
LD      := $(CROSS)ld
OBJCOPY := $(CROSS)objcopy

CFLAGS  := -m32 -ffreestanding -fno-builtin -nostdlib -nostartfiles -Wall -Wextra
LDFLAGS := -nostdlib -T kernel.ld

all: LOADER.COM KERNEL.BIN

# 16-Bit DOS-Loader (.COM)
LOADER.COM: loader.asm
	nasm -f bin loader.asm -o LOADER.COM

# compile C-Kernel:
kernel.o: kernel.c
	$(CC) $(CFLAGS) -c kernel.c -o kernel.o

# link Kernel with linker script:
kernel.coff: kernel.o kernel.ld
	$(LD) $(LDFLAGS) -m i386pe -o kernel.coff kernel.o

# convert COFF-Kernel into flat Binary:
KERNEL.BIN: kernel.coff
	$(OBJCOPY) -O binary kernel.coff KERNEL.BIN

clean:
	rm -f *.o *.coff *.BIN *.COM
