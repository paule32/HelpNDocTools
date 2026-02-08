; -----------------------------------------------------------------------------
; \file  data64.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%if DOS_SHELL == 64
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
ASTR consoleColor_0,  27,'[0m'
ASTR consoleColor_1,  27,'[1;'
ASTR consoleColor_2,  "m"
ASTR consoleColor_3,  27,'[H',27,'[2J',27,'[H'
ASTR buffer_semi, ";"
; -----------------------------------------------------------------------------
; DOS ANSI foreground color's   0..15
; -----------------------------------------------------------------------------
ASTR console_color_30 , "30"
ASTR console_color_31 , "31"
ASTR console_color_32 , "32"
ASTR console_color_33 , "33"
ASTR console_color_34 , "34"
ASTR console_color_35 , "35"
ASTR console_color_36 , "36"
ASTR console_color_37 , "37"
; -----------------------------------------------------------------------------
ASTR console_color_90 , "90"
ASTR console_color_91 , "91"
ASTR console_color_92 , "92"
ASTR console_color_93 , "93"
ASTR console_color_94 , "94"
ASTR console_color_95 , "95"
ASTR console_color_96 , "96"
ASTR console_color_97 , "97"

; -----------------------------------------------------------------------------
; DOS ANSI background color's   0..15
; -----------------------------------------------------------------------------
ASTR console_color_40 , "40"
ASTR console_color_41 , "41"
ASTR console_color_42 , "42"
ASTR console_color_43 , "43"
ASTR console_color_44 , "44"
ASTR console_color_45 , "45"
ASTR console_color_46 , "46"
ASTR console_color_47 , "47"

ASTR console_color_100, "100"
ASTR console_color_101, "101"
ASTR console_color_102, "102"
ASTR console_color_103, "103"
ASTR console_color_104, "104"
ASTR console_color_105, "105"
ASTR console_color_106, "106"
ASTR console_color_107, "107"

Rect80x25:          dw 0, 0, 79, 24         ; SMALL_RECT {Left,Top,Right,Bottom} = {0,0,79,24}
pMsg:               dq 0                    ; LPWSTR, wird von FormatMessageW allokiert
spaceW:             db 'o'                  ; wide char ' '

; -----------------------------------------------------------------------------
; default console values ...
; -----------------------------------------------------------------------------
_cA_console_bg:     db ATTR_BG_BLACK, 0
_cA_console_fg:     db ATTR_FG_LIGHT_YELLOW, 0

_fmt: db "%s", 0

ASTR buffer , ATTR_BG_BLACK, ATTR_FG_LIGHT_YELLOW
ASTR buffer2, " oI_01", 0

ASTR buffer_2, "moin", 0
ASTR buffer_1, "Hello %s", 0
ASTR buffer_3, " smile"  , 13, 10, 0

data_end:
times (ALIGN_UP($-$$,FILEALIGN)-($-$$)) db 0

%endif
