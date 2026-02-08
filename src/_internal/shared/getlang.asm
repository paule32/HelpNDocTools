; -----------------------------------------------------------------------------
; \file  getlang.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
org 100h
bits 16

start:
    push   ds
    pop    es             ; ES=DS
    lea    dx, buf
    mov    ah, 38h        ; Get country info
    mov    al, 00h        ; aktuelles Land
    int    21h
    jc     is_error

    mov    dx, 0x4C00     ; Fehlercode sichern
    mov    ax, bx         ; Country-Code in BX

    add     dx, ax
    mov     ax, dx
    int     0x21
    jmp     done

is_error:
    mov     dx, 0x4C00
    add     dx, 255
    int     0x21
done:
    mov    ax, dx
    int    21h

buf: times 64 db 0
