; -----------------------------------------------------------------------------
; \file  code16.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%define DOS_SHELL 1
code16_start:
nop
nop
    ; Kein Windows -> Meldung ausgeben
    push cs
    pop  ds

    ; AX=1600h: Windows-Check
    mov ax, 0x1600
    int 0x2F
    or  al, al
    jnz .ok              ; AL!=0 => irgendein Windows aktiv
    
    WRITE_CON_A msg
    WRITE_CON_A msg
    
    .ok:
    mov  ax, 0x4C00      ; ExitCode=0
    int  0x21

code16_end:

kernell_mem: times 512-48 db 0

%define DOS_SHELL 0
