; -----------------------------------------------------------------------------
; \file  bss16.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

bss16_start:

; -----------------------------------------------------------------------------
; \brief hold DOS command line argument information's ...
; -----------------------------------------------------------------------------
%define MAX_ARGS    7
struc _cA_COMMAND_LINE
    .arg_count      resb 1            ; max. 255 arguments
    .arg_str        resb 64           ; max. length = 64 bytes
endstruc
_cA_command_args:   resb 64 * MAX_ARGS
_cA_command_arglen: resb 64
arg_total:          resb 1

_cA_cmd_buf:        resb 256          ; CMD string
_cA_cmd_buffer:     resb 130

fdescbuf:           resb 4096

buf_hex:            resb 6            ; 4 Hex-Zeichen + '$' + Reserve
buf_dec:            resb 7            ; 5 Dezimal-Zeichen + '$' + Reserve

filename:           resb 128
_cA_fdbuf:
fdbuf:              resb 2048
_cA_namebuf:        resb 16

hFile:              resw 0
; -----------------------------------------------------------------------------
g_type:             resw 0
g_cmd:              resb 0
g_ftype:            resb 0
g_ftype_mapped:     resb 0
g_flen:             resw 0
g_year:             resw 0
g_month:            resb 0
g_day:              resb 0
; -----------------------------------------------------------------------------
verByte:            resb 0
yy:                 resb 0
mm:                 resb 0
dd:                 resb 0
mdx:                resb 0
lang:               resb 0
rec32:              resd 0

tokbuf:             resb 64
fldname:            resb 12

header:             resb 32
fdbuf_size:         resw 0
tempdesc:           resb 32

; -----------------------------------------------------------------------------

buf_seg:            resw 0
size_lo:            resw 0
size_hi:            resw 0

bss16_end:
