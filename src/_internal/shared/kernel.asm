;---------------------------------------------------
; \file  kernel.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
;---------------------------------------------------
bits 16
org 0
%include 'macros.inc'

kernel_start:
section .text
%include 'code16.asm'

section .data
%include 'data16.inc'

section .bss
%include 'bss16.asm'
kernel_end:
