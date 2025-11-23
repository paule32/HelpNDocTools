; -----------------------------------------------------------------------------
; \file  kernel64.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%include 'config.inc'
; -----------------------------------------------------------------------------
bits 64
org 0
%include 'macros.inc'

kernel64_start:
section .text
%include 'code64.asm'

section .data
%include 'data64.asm'

section .bss
%include 'bss64.asm'
kernel64_end:
