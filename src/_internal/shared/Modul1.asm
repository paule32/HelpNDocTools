; -----------------------------------------------------------------------------
; \file  Modul1.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

; -----------------------------------------------------------------------------
; mod1.asm (RAW BIN)
; NASM: nasm -f bin -o MOD1.BIN mod1.asm
; -----------------------------------------------------------------------------

use16
org 0

; Eintritt bei Offset 0000h
entry:
    ; Erwartung: CS=DS=ES=Modul-Segment
    ; Übergabe: ES:BX -> Buffer, CX = Länge
    push ds
    push es

    ; Status 0 = OK
    xor ax, ax

    pop es
    pop ds
    retf            ; far return zum Loader
