; -----------------------------------------------------------------------------
; \file  StrCompare.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

; -----------------------------------------------------------------------------
; strcmp.asm  —  16-Bit, NASM
; Vergleicht zwei 0-terminierte Strings: DS:SI vs. ES:DI
; Rückgabe: AL=1 (gleich), AL=0 (ungleich)
; -----------------------------------------------------------------------------
string_compare:
    push si
    push di
    .next:
    mov     al, [si]        ; Zeichen aus String1
    mov     bl, [es:di]     ; Zeichen aus String2
    inc     si
    inc     di
    cmp     al, bl
    jne     .not_equal      ; Unterschied gefunden -> 0
    or      al, al
    jne     .next           ; noch nicht am Terminator -> weiter
    mov     al, 1           ; beide 0 erreicht -> gleich
    jmp     short .done
    .not_equal:
    xor     al, al          ; 0
    .done:
    pop     di
    pop     si
    ret
