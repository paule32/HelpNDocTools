; -----------------------------------------------------------------------------
; \file  data64.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
times (DATA_RAW_PTR-($-$$)) db 0
data_start:

%include 'data.inc'

ASTR cap2A          , "ein Text", 13,10,0

WSTR fmtW           , "Win32-Fehler: 0x%08X (%u)", 0      ; Format-String (UTF-16)
WSTR ErrTitleW      , "Fehler"

WSTR errmsgW        , 'RegisterClassExW failed'
WSTR titleW         , 'NASM PE64 GUI without Linker'
WSTR winclassW      , 'NasmWndClass'

ASTR prompt         , "Eingabe: ",0
; -----------------------------------------------------------------------------
; Setze: Reset, Cursor Home, Farbe (helles Cyan auf blau), löschen, wieder Home
;  - ESC[0m       -> Attribute reset
;  - ESC[48;5;4m  -> Hintergrund Blau (xterm 256)
;  - ESC[38;5;14m -> Vordergrund Hell-Cyan
;  - ESC[2J       -> Bildschirm löschen (mit Spaces + aktuellen Attributen)
;  - ESC[H        -> Cursor 1;1
; -----------------------------------------------------------------------------
ASTR screen_clear,  27,'[0m'        ,\
                    27,'[H'         ,\
                    27,'[1;%d;%dm'  ,\
                    27,'[2J'        ,\
                    27,'[H'         ,0

Rect80x25:          dw 0, 0, 79, 24         ; SMALL_RECT {Left,Top,Right,Bottom} = {0,0,79,24}
pMsg:               dq 0                    ; LPWSTR, wird von FormatMessageW allokiert
spaceW:             db 'o'                  ; wide char ' '

; -----------------------------------------------------------------------------
; default console values ...
; -----------------------------------------------------------------------------
_cA_console_bg:     dq ATTR_BG_BLACK
_cA_console_fg:     dq ATTR_FG_LIGHT_YELLOW

_cA_src:            times 256 db 0
_cA_dst:            times 256 db 0

_cA_src_length:     dw 256
_cA_dst_length:     dw 512

_cA_buf:            times  64 db 0

mode_in:            dd 0
mode_out:           dd 0

hIn:                dq 0
hOut:               dq 0
read:               dd 0
tmpConsoleMode:     dd 0
last_error:         dd 0

written:            dq 0

; -----------------------------------------------------------------------------
; 10 GET's each 256 Nytes ...
; -----------------------------------------------------------------------------
_cA_get_buffer_0:       times 256 db 0
_cA_get_buffer_length_0 equ   ($ - _cA_get_buffer_0)
_cA_get_buffer_1:       times 256 db 0
_cA_get_buffer_length_1 equ   ($ - _cA_get_buffer_1)
_cA_get_buffer_2:       times 256 db 0
_cA_get_buffer_length_2 equ   ($ - _cA_get_buffer_2)
_cA_get_buffer_3:       times 256 db 0
_cA_get_buffer_length_3 equ   ($ - _cA_get_buffer_3)
_cA_get_buffer_4:       times 256 db 0
_cA_get_buffer_length_4 equ   ($ - _cA_get_buffer_4)
_cA_get_buffer_5:       times 256 db 0
_cA_get_buffer_length_5 equ   ($ - _cA_get_buffer_5)
_cA_get_buffer_6:       times 256 db 0
_cA_get_buffer_length_6 equ   ($ - _cA_get_buffer_6)
_cA_get_buffer_7:       times 256 db 0
_cA_get_buffer_length_7 equ   ($ - _cA_get_buffer_7)
_cA_get_buffer_8:       times 256 db 0
_cA_get_buffer_length_8 equ   ($ - _cA_get_buffer_8)
_cA_get_buffer_9:       times 256 db 0
_cA_get_buffer_length_9 equ   ($ - _cA_get_buffer_9)


data_end:
times (ALIGN_UP($-$$,FILEALIGN)-($-$$)) db 0
