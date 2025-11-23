; -----------------------------------------------------------------------------
; \file  bss16.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%if DOS_SHELL == 1
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
arg_total:          resw 1

_cA_cmd_arg_1:      resb 64
_cA_cmd_arg_2:      resb 64
_cA_cmd_arg_3:      resb 64
_cA_cmd_arg_4:      resb 64
_cA_cmd_arg_5:      resb 64
_cA_cmd_arg_6:      resb 64
_cA_cmd_arg_7:      resb 64

_cA_cmd_buf:        resb 256          ; CMD string
_cA_cmd_buffer:     resb 130

; EXEC-Parameterblock (14 Bytes)
_cA_ExecBlk:        resb 14

; -----------------------------------------------------------------------------
; command line holders ...
; -----------------------------------------------------------------------------
_cA_db_version:     resb 1   ; 3 -> dBase3, 4 -> dBase4
_cA_db_op:          resb 1   ; 0 -> CREATE, 1 -> APPEND
_cA_db_type:        resb 1   ; C|I|F|B|D
_cA_db_have_token:  resb 1

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
%endif
