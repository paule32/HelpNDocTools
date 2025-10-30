fmtHello: db "abde fg", 13, 10, 0
fmtHello_length equ ($-fmtHello)-1
written: dd 0

align 4
last_error: dd 0

; Puffer für CONSOLE_SCREEN_BUFFER_INFO (>= 22 Bytes; wir nehmen 32 zur Sicherheit)
csbi:        times 32 db 0
orig_attr:   dw 0

fmtW:   WSTR "Win32-Fehler: 0x%08X (%u)", 0      ; Format-String (UTF-16)
wbuf:   times 128 dw 0                           ; Ausgabepuffer (128 WCHAR)
ErrTitleW: WSTR "Fehler", 0

pMsg:   dq 0                          ; LPWSTR, wird von FormatMessageW allokiert
