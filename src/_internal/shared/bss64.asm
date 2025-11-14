; -----------------------------------------------------------------------------
; \file  bss64.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

bss_start:

; -----------------------------------------------------------------------------
; Strukturen (kompakt modelliert)
; -----------------------------------------------------------------------------
struc COORD
    .X                  resw 1
    .Y                  resw 1
endstruc

struc SMALL_RECT
    .Left               resw 1
    .Top                resw 1
    .Right              resw 1
    .Bot                resw 1
endstruc

; -----------------------------------------------------------------------------
; CONSOLE_SCREEN_BUFFER_INFO (Layout wie in WinSDK; 22 Bytes + Padding)
; -----------------------------------------------------------------------------
struc CSBI
    .dwSize             resw 2      ; COORD
    .dwCursorPos        resw 2      ; COORD
    .wAttributes        resw 1
    .srWindow           resw 4      ; SMALL_RECT
    .dwMaxWindowSize    resw 2      ; COORD
    ._pad               resw 1      ; pad to 24 bytes (alignment)
endstruc
; -----------------------------------------------------------------------------
csbi:               resb CSBI_size

_cA_buffer_dst:     resb 128

_cA_buffer_A:       resb 128
_cA_buffer_B:       resb 128

;_cA_src_length:     resb 256
;_cA_dst_length:     resb 512

_cA_src:            resb 128
_cA_dst:            resb 128

mode_in:            resd 1
mode_out:           resd 1
; -----------------------------------------------------------------------------
_cA_empty:          resb 1

_cA_buf:            resb 64

hIn:                resq 1
hOut:               resq 1
read:               resd 1
tmpConsoleMode:     resd 1
last_error:         resd 1

written:            resq 1
bss_end:

