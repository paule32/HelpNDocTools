; -----------------------------------------------------------------------------
; \file  kernel32.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%include 'config.inc'
; -----------------------------------------------------------------------------
bits 32
org 0
%include 'windows.inc'
%include 'macros.inc'

kernel32_start:
kernel32:
section .text
%include 'code32.asm'
; -----------------------------------------------------------------------------
%include 'ScreenClear.asm'
%include 'PutStrColor.asm'

;section .data
;%include 'data32.inc'

;section .bss
;%include 'bss32.asm'
kernel32_end:
