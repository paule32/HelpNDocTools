// ---------------------------------------------------------------------------
// \file kernel.c – A simple freestanding C-Kernel
// \note  (c) 2025 by Jens Kallup - paule32
//        all rights reserved.
//
// \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// no standard library, no syscalls, nothing.
// loader jumps directly to kmain() (Linkerscript ENTRY).
// ---------------------------------------------------------------------------

extern void k_display(void) __asm__("_k_display");

// ---------------------------------------------------------------------------
// \brief kernel PM-DOS screen clear function with default 80x25 dimension.
// ---------------------------------------------------------------------------
void k_clear_screen()
{
    char* vidmem = (char*) 0xb8000;
    unsigned int i=0;
    while(i<(80*2*25)) {
        vidmem[i] = ' '; ++i;
        vidmem[i] = 0x07;
        ++i;
    }
}

void kmain(void) {
    k_clear_screen();
    k_display();
    for (;;) {
    }
}
