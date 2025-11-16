; -----------------------------------------------------------------------------
; \file  StrCopy.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

; -----------------------------------------------------------------------------
; Quelle: DS:SI (ASCIIZ)
; Ziel:   ES:DI   (hier setzen wir ES=DS für Daten im selben Segment)
; Rückgabe: SI = Zielstart (damit PUTS_COLOR direkt funktioniert)
; Clobbers: AX, CX, DI, ES, BX, FLAGS
; -----------------------------------------------------------------------------
string_copy:
    push    bx
    push    si

    ; ES = DS (falls Ziel im selben Segment)
    push    ds
    pop     es

    mov     bx, di          ; Zielstart merken
    mov     cx, 63          ; (optional) max. 63 Zeichen + 0

    .copy:
    lodsb
    stosb
    test    al, al
    jz      .done
    loop    .copy
    mov     byte [es:di], 0

    .done:
    mov     si, bx          ; <- WICHTIG: SI auf Zielstart setzen
    pop     bx              ; ursprüngliches SI verwerfen (gewollt)
    pop     bx              ; wiederherstellen von BX
    ret
