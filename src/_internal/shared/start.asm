; -----------------------------------------------------------------------------
; \file  start.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%include 'basexx.inc'
%include 'windows.inc'
%include 'usefunc.inc'

%include 'macros.inc'

; -----------------------------------------------------------------------------
; DOS and PE-Header
; -----------------------------------------------------------------------------
%include 'doshdr.inc'
%include 'winhdr.inc'

; -----------------------------------------------------------------------------
; .text (Code)
; -----------------------------------------------------------------------------
section .text
text_start:

%include 'code64.asm'
%include 'winproc.asm'
%include 'text64.asm'
%include 'stdlib.inc'

text_end:

%include 'imports.inc'
%include 'data64.asm'

section .bss
%include 'bss64.asm'

; -----------------------------------------------------------------------------
section .text
file_end:
