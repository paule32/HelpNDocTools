; -----------------------------------------------------------------------------
; \file  bss64.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
times (BSS_RAW_PTR-($-$$)) db 0
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
csbi                resb CSBI_size

bss_end:
times (ALIGN_UP($-$$,FILEALIGN)-($-$$)) db 0
