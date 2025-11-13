; -----------------------------------------------------------------------------
; \file  Str16Len.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%define DOS_SHELL 1

; -----------------------------------------------------------------------------
; \brief  get the 16 bit length of a 0-terminated string
; \param  Input:  ES:SI -> "0"-terminierter String
; \return Output: CX = Länge (ohne '0')
; -----------------------------------------------------------------------------
DOSStrLen:
    push    di
    mov     di, si
    mov     al, 0x00
    cld
    mov     cx, 0FFFFh
    repne   scasb          ; search '0x00'
    mov     ax, 0FFFFh
    sub     ax, cx         ; AX = Anzahl verglichener Bytes inkl. '0x00'
    dec     ax             ; ohne Terminierer
    sub     ax, 2
    mov     cx, ax
    pop     di
    ret
