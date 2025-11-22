; -----------------------------------------------------------------------------
; \file  ConsoleCursor.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
dos_set_cursor:
    mov  [PTR16(dos_xpos)], dl   ; column
    mov  [PTR16(dos_ypos)], dh   ; row
    ;---
    mov  bh, 0                   ; todo
    mov  [PTR16(dos_page)], bh   ; video page
    ;---
    mov  ah, 02h
    VideoCall
    ret

dos_get_cursor:
    push di
    push si
    push bx
    push dx
    
    mov  bh, 0                   ; todo
    mov  ah, 0x03
    VideoCall
    mov  [PTR16(dos_xpos)], dl   ; column
    mov  [PTR16(dos_ypos)], dh   ; row
    mov  [PTR16(dos_page)], bh   ; video page
    
    pop  dx
    pop  bx
    pop  si
    pop  di
    ret
