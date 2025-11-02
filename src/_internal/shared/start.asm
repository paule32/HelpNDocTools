; -----------------------------------------------------------------------------; \file  start.asm; \note  (c) 2025 by Jens Kallup - paule32;        all rights reserved.;; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.; -----------------------------------------------------------------------------%include 'basexx.inc'%include 'windows.inc'%include 'winfunc.inc'%include 'usefunc.inc'
%include 'macros.inc'
; -----------------------------------------------------------------------------; DOS and PE-Header; -----------------------------------------------------------------------------%include 'doshdr.inc'%include 'winhdr.inc'
; -----------------------------------------------------------------------------; .text (Code); -----------------------------------------------------------------------------    times (TEXT_RAW_PTR - ($ - $$)) db 0section_text_start:
%include 'winproc.asm'%include 'code64.asm'%include 'text64.asm'%include 'stdlib.inc'
section_text_end:
%include 'imports.inc'%include 'data64.asm'%include 'bss64.asm'
; -----------------------------------------------------------------------------file_end: