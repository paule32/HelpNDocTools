; -----------------------------------------------------------------------------
; \file  code16.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
    ; AX=1600h: Windows-Check
    mov ax, 0x1600
    int 0x2F
    or  al, al
    jnz .exit_ok              ; AL!=0 => irgendein Windows aktiv

    ; Kein Windows -> Meldung ausgeben
    push cs
    pop  ds
    mov  dx, msg2
    mov  ah, 0x09
    int  0x21
    mov  ax, 0x4C01           ; ExitCode=1
    int  0x21

.exit_ok:
    mov  ax, 0x4C00           ; ExitCode=0
    int  0x21

msg2:    db "This program requieres MS-Windows.",13,10,"$",0
