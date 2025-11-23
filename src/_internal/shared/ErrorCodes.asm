; -----------------------------------------------------------------------------
; \file  ErrorCodes.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

; -----------------------------------------------------------------------------
; \brief dispatch: search the handler and jump to it ...
; -----------------------------------------------------------------------------
DOS_handle_error_code:
%if DOS_SHELL == 1
    ; AX enthält den DOS-Fehlercode
    mov   bx, ax             ; bx = gesuchter Code
    mov   si, _cA_error_dispatch
    .next:
    lodsw                    ; ax = Tabellencode, si zeigt nun auf Handler-Wort
    test  ax, ax
    jz    .default           ; 0 -> Ende: Default
    cmp   ax, bx
    je    .match
    add   si, 2              ; Handlerwort überspringen
    jmp   .next
    .match:
    jmp   word [si]          ; indirekter Sprung zum Handler
    .default:
    jmp   _cA_open_error_nd
    
    ; ----------------------------------------
    ; Handler minimal & einheitlich per Makro
    ; ----------------------------------------
    DEF_ERROR 01h, open_error_01    ; ungültige Funktiob
    DEF_ERROR 02h, open_error_02
    DEF_ERROR 03h, open_error_03
    DEF_ERROR 04h, open_error_04
    DEF_ERROR 05h, open_error_05
    DEF_ERROR 06h, open_error_06    ; ungültiger Handle
    DEF_ERROR 07h, open_error_07    ; korrupte Speicherverwaltung
    DEF_ERROR 08h, open_error_08    ; nicht genügend Speicher
    DEF_ERROR 09h, open_error_09
    DEF_ERROR 0Ah, open_error_0A
    DEF_ERROR 0Bh, open_error_0B
    DEF_ERROR 0Ch, open_error_0C
    DEF_ERROR 0Dh, open_error_0D
    DEF_ERROR 0Eh, open_error_0E
    DEF_ERROR 0Fh, open_error_0F
    DEF_ERROR 10h, open_error_10
    DEF_ERROR 11h, open_error_11
    DEF_ERROR 12h, open_error_12
    DEF_ERROR 15h, open_error_15
    DEF_ERROR 1Dh, open_error_1D    ; Seek-Fehler
    DEF_ERROR 1Eh, open_error_1E    ; kein DOS-Datenträger
    DEF_ERROR 1Fh, open_error_1F
    DEF_ERROR 20h, open_error_20
    DEF_ERROR 21h, open_error_21
    DEF_ERROR 27h, open_error_27

    ERR_HANDLER 0x01, 0x02, 0x03, 0x04
    ERR_HANDLER 0x05, 0x06, 0x07, 0x08
    ERR_HANDLER 0x09, 0x0A, 0x0B, 0x0C
    ERR_HANDLER 0x0D, 0x0E, 0x0F, 0x10
    ERR_HANDLER 0x11, 0x12, 0x15
    ERR_HANDLER 0x1D, 0x1E, 0x1F, 0x20
    ERR_HANDLER 0x21
    ERR_HANDLER 0x27

_cA_errhnd:
    PUTS_COLOR open_error_nd, ATTR_DOS_ERROR
    mov   cx, 32
    jmp _open_exit

_open_exit:
    DOS_Exit cx
%endif
