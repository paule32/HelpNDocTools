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

cap2A: db "ein Text",13,10,0
cap2A_length equ ($ - cap2A)

fmtW:           WSTR "Win32-Fehler: 0x%08X (%u)", 0      ; Format-String (UTF-16)
ErrTitleW:      WSTR "Fehler", 0

errmsgW:        WSTR 'RegisterClassExW failed'
titleW:         WSTR 'NASM PE64 GUI without Linker'
winclassW:      WSTR 'NasmWndClass'
prompt:         db "Eingabe: ",0

; SMALL_RECT {Left,Top,Right,Bottom} = {0,0,79,24}
Rect80x25:      dw 0, 0, 79, 24
pMsg:           dq 0                    ; LPWSTR, wird von FormatMessageW allokiert

wbuf:           times 256 dw 0          ; Ausgabepuffer (128 WCHAR)
src:            times 256 db 0
dst:            times 512 db 0

hIn:            dq 0
hOut:           dq 0
read:           dd 0
tmpConsoleMode: dd 0
last_error:     dd 0

data_end:
times (ALIGN_UP($-$$,FILEALIGN)-($-$$)) db 0
