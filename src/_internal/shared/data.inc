fmtHello: WSTR "abde fg", 13, 10, 0
fmtHello_length equ ($-fmtHello)-1
written: dd 0

align 4
last_error: dd 0

; Puffer für CONSOLE_SCREEN_BUFFER_INFO (>= 22 Bytes; wir nehmen 32 zur Sicherheit)
csbi:        times 32 db 0
orig_attr:   dw 0

fmtW:   WSTR "Win32-Fehler: 0x%08X (%u)", 0      ; Format-String (UTF-16)
wbuf:   times 256 dw 0                           ; Ausgabepuffer (128 WCHAR)
ErrTitleW: WSTR "Fehler", 0

pMsg:   dq 0                          ; LPWSTR, wird von FormatMessageW allokiert
errmsgW: WSTR 'RegisterClassExW failed'
titleW: WSTR 'NASM PE64 GUI without Linker'
winclassW: WSTR 'NasmWndClass'

; SMALL_RECT {Left,Top,Right,Bottom} = {0,0,79,24}
Rect80x25:  dw 0, 0, 79, 24

hWndCon: dq 0
hMenu: dq 0

caption:     db "Eingabe",0
src     times 256 db 0
dst     times 512 db 0
bytesRead:   dq 0                 ; DWORD64 für Anzahl gelesener Zeichen

charswritten: dd 0               ; LPDWORD für WriteConsoleA (Anzahl Zeichen)
MessageErrorTextW: WSTR "message error text"

fmt:     db "%6d", 0      ; Limitiert die Eingabe für %s auf 63 Zeichen
outfmt:  db "Eingabe: %s", 13,10, 0
num:     dd 0

msg_down    db "KEYDOWN: VK=%04X CH='%c'", 13,10, 0
msg_up      db "KEYUP  : VK=%04X CH='%c'", 13,10, 0

hIn:        dq 0
hOut:       dq 0
prompt:     db "Eingabe: ",0
read: dd 0

; Wir lesen ein Array von 32 INPUT_RECORDs (je 20 Bytes → 640 Bytes)
; Layout (x64, gepackt wie WinAPI, jeweils 2-Byte-aligned):
; INPUT_RECORD {
;   WORD  EventType;                      ; +0
;   WORD  Padding;                        ; +2 (Ausgleich)
;   union {
;     KEY_EVENT_RECORD {                  ; +4
;       BOOL  bKeyDown;                   ; +4  (4)
;       WORD  wRepeatCount;               ; +8  (2)
;       WORD  wVirtualKeyCode;            ; +10 (2)
;       WORD  wVirtualScanCode;           ; +12 (2)
;       WCHAR UnicodeChar;                ; +14 (2)  (wir nutzen W-Variante)
;       DWORD dwControlKeyState;          ; +16 (4)
;     }                                   ; Größe 20 Bytes insgesamt
;   }
; }
; == Gesamtgröße INPUT_RECORD: 20 Bytes
records:     times 32*20 db 0
readCount:   dd 1
tmpConsoleMode: dd 0
