; -----------------------------------------------------------------------------
; \file  code16.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%define DOS_SHELL 1

    ; AX=1600h: Windows-Check
    mov ax, 0x1600
    int 0x2F
    or  al, al
    jnz .windows_ok              ; AL!=0 => irgendein Windows aktiv

    ; Kein Windows -> Meldung ausgeben
    push cs
    pop  ds

    WRITE_CON_A msg
    
    mov  ax, 0x4C01           ; ExitCode=1
    int  0x21

.windows_ok:
    WRITE_CON_A msg2
    
    mov  ax, 0x4C00           ; ExitCode=0
    int  0x21

%define DOS_SHELL 0
