; -----------------------------------------------------------------------------
; \file  data16.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
data16_start:

msg:            db "This program requieres MS-Windows.$"
kernel_file:    db "kernel.bin", 0
file_not_fnd:   db "KERNEL.BIN not found - exiting", 0x0a, 0x0d, "$"
file_read_err:  db "Can't read KERNEL.BIN - exiting", 0x0a, 0x0d, "$"
in_pmode_str:   db "Processor already in protected mode - exiting", 0x0a, 0x0d, "$"

align 4
; Real mode interrupt vector table (IDTR)
idtr:
    dw 0x3ff
    dd 0

align 4
gdtr:
    dw gdt_end-gdt_start-1
    dd gdt_start

align 4
gdt_start:
    ; First entry is always the Null Descriptor
    dd 0
    dd 0

gdt_code:
    ; 32-bit 4gb flat r/w/executable code descriptor
    dw 0xFFFF                   ; limit low
    dw 0                        ; base low
    db 0                        ; base middle
    db 10011010b                ; access
    db 11001111b                ; granularity
    db 0                        ; base high

gdt_data:
    ; 32-bit 4gb flat r/w data descriptor
    dw 0xFFFF                   ; limit low
    dw 0                        ; base low
    db 0                        ; base middle
    db 10010010b                ; access
    db 11001111b                ; granularity
    db 0                        ; base high

gdt16_code:
    ; 16-bit 4gb flat r/w/executable code descriptor
    dw 0xFFFF                   ; limit low
    dw 0                        ; base low
    db 0                        ; base middle
    db 10011010b                ; access
    db 10001111b                ; granularity
    db 0                        ; base high

gdt16_data:
    ; 16-bit 4gb flat r/w data descriptor
    dw 0xFFFF                   ; limit low
    dw 0                        ; base low
    db 0                        ; base middle
    db 10010010b                ; access
    db 10001111b                ; granularity
    db 0                        ; base high
gdt_end:

kernel_mem: times KERNEL_SIZE db 0x0
data16_end:

%define DOS_SHELL 0
