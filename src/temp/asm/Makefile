CROSS    ?= 
AS       := nasm
CC       := $(CROSS)gcc
LD       := $(CROSS)ld
OBJCOPY  := $(CROSS)objcopy

CFLAGS   := -m32 -O2 -ffreestanding -fno-builtin -nostdlib -nostartfiles \
            -Wall -Wextra -Wno-unused-value -Wno-unused-parameter
            
LDFLAGS  := -nostdlib -T kernel.ld
ASMFLAGS := -f win32 -DDOS_MODE=32

SRCC := kernel.c util.c math.c
OBJS := $(SRCC:.c=.o) code32.o isr.o

all: LOADER.COM KERNEL.BIN

# 16-Bit DOS-Loader (.COM)
LOADER.COM: loader.asm
	$(AS) -f bin $< -o $@

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

%.o: %.asm
	$(AS) $(ASMFLAGS) $< -o $@

# link Kernel with linker script:
kernel.coff: $(OBJS) kernel.ld
	$(LD) $(LDFLAGS) -m i386pe -o $@ $(OBJS)

# convert COFF-Kernel into flat Binary:
KERNEL.BIN: kernel.coff
	$(OBJCOPY) -O binary $< $@

clean:
	rm -f *.o *.coff *.BIN *.COM
