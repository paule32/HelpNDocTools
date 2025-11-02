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
                    27,'[48;5;4m'   ,\
                    27,'[38;5;14m'  ,\
                    27,'[2J'        ,\
                    27,'[H'

_cA_src_length:     dw 256
_cA_dst_length:     dw 512

Rect80x25:          dw 0, 0, 79, 24         ; SMALL_RECT {Left,Top,Right,Bottom} = {0,0,79,24}
pMsg:               dq 0                    ; LPWSTR, wird von FormatMessageW allokiert
spaceW:             db 'o'                  ; wide char ' '

;_cW_wbuf:           times 256 dw 0          ; Ausgabepuffer (128 WCHAR)
_cA_src:            times 256 db 0
_cA_dst:            times 256 db 0

mode_in:            dd 0
mode_out:           dd 0

hIn:                dq 0
hOut:               dq 0
read:               dd 0
tmpConsoleMode:     dd 0
last_error:         dd 0

written:            dq 0

data_end:
times (ALIGN_UP($-$$,FILEALIGN)-($-$$)) db 0
