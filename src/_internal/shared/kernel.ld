/* ---------------------------------------------------------------------------
// \file kernel.c – A simple freestanding C-Kernel
// \note  (c) 2025 by Jens Kallup - paule32
//        all rights reserved.
//
// \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
// ---------------------------------------------------------------------------
// kernel.ld – 32-Bit Flat Binary, entry point at kmain
// ---------------------------------------------------------------------------
*/
ENTRY(_kmain)

SECTIONS {
    /* loader address for KERNEL.BIN */
    . = 0x40000;

    .text : {
        *(.text*)
    }

    .rodata : {
        *(.rodata*)
    }

    .data : {
        *(.data*)
    }

    .bss : {
        *(.bss*)
        *(COMMON)
    }
}
