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
    DEF_ERROR 0Ch, open_error_0C
    DEF_ERROR 0Fh, open_error_0F
    DEF_ERROR 10h, open_error_10
    DEF_ERROR 11h, open_error_11
    DEF_ERROR 1Dh, open_error_1D    ; Seek-Fehler
    DEF_ERROR 1Eh, open_error_1E    ; kein DOS-Datenträger

_cA_errh01:
    PUTS_COLOR open_error_01, ATTR_DOS_ERROR
    mov   cx, 01h
    jmp _open_exit
_cA_errh02:
    PUTS_COLOR open_error_02, ATTR_DOS_ERROR
    mov   cx, 02h
    jmp _open_exit
_cA_errh03:
    PUTS_COLOR open_error_03, ATTR_DOS_ERROR
    mov   cx, 03h
    jmp _open_exit
_cA_errh04:
    PUTS_COLOR open_error_04, ATTR_DOS_ERROR
    mov   cx, 04h
    jmp _open_exit
_cA_errh05:
    PUTS_COLOR open_error_05, ATTR_DOS_ERROR
    mov   cx, 05h
    jmp _open_exit
_cA_errh06:
    PUTS_COLOR open_error_06, ATTR_DOS_ERROR
    mov   cx, 06h
    jmp _open_exit
_cA_errh0C:
    PUTS_COLOR open_error_0C, ATTR_DOS_ERROR
    mov   cx, 0Ch
    jmp _open_exit
_cA_errh0F:
    PUTS_COLOR open_error_0F, ATTR_DOS_ERROR
    mov   cx, 0Fh
    jmp _open_exit
_cA_errh10:
    PUTS_COLOR open_error_10, ATTR_DOS_ERROR
    mov   cx, 10h
    jmp _open_exit
_cA_errh11:
    PUTS_COLOR open_error_11, ATTR_DOS_ERROR
    mov   cx, 11h
    jmp _open_exit
_cA_errh12:
    PUTS_COLOR open_error_12, ATTR_DOS_ERROR
    mov   cx, 12h
    jmp _open_exit
_cA_errh1D:
    PUTS_COLOR open_error_1D, ATTR_DOS_ERROR
    mov   cx, 1Dh
    jmp _open_exit
_cA_errh1E:
    PUTS_COLOR open_error_1E, ATTR_DOS_ERROR
    mov   cx, 1Eh
    jmp _open_exit
_cA_errhnd:
    PUTS_COLOR open_error_nd, ATTR_DOS_ERROR
    mov   cx, 32
    jmp _open_exit

_open_exit:
    DOS_Exit cx

