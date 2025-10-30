; -----------------------------------------------------------------------------
; \file  data16.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
data16_start:

counter:    dq 0                  ; 8-Byte Zähler (initial 0)
greeting:   db "Hallo, Welt!",0   ; änderbarer String
buffer256:  times 256 db 0

data16_end:
