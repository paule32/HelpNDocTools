; -----------------------------------------------------------------------------
; \file  SetConsoleCursor.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%define DOS_SHELL 1

SetConsoleCursor:
    mov ah, 02h
    int 10h
    ret
