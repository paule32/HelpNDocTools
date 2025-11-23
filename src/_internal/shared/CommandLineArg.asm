; -----------------------------------------------------------------------------
; \file  CommandLineArg.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

; -----------------------------------------------------------------------------
; \brief  Sucht den n-ten (1-basiert) Token im ASCIIZ-String bei DS:SI,
;         ersetzt das erste Leerzeichen NACH dem Token durch 0 und
;         liefert SI auf den Tokenstart (C-String).
; \param  Eingabe:
;         DS:SI -> 0-terminierter String (muss schreibbar sein!)
;         BL    = n (1 = erster Token)
; \return Ausgabe bei Erfolg (CF=0):
;         SI    = Startadresse des Tokens (in DS)
;         CX    = Länge des Tokens
; \error  Bei Misserfolg (CF=1): CX=0, SI undefiniert
; \note   Verändert: AX, CX, DX, SI, DI, FLAGS
; -----------------------------------------------------------------------------
%if ((DOS_SHELL == 1) && (DOS_MODE == 16))
getCommandLine_Arg:
    ;push di
    test bl, bl
    jnz .start
    stc
    jmp .ret

    .start:
    ; führende Leerzeichen überspringen
    .skip_spaces_lead:
    lodsb                      ; AL=[SI], SI++
    cmp  al, ' '
    je   .skip_spaces_lead
    cmp  al, 0
    je   .not_found

    ; AL ist erstes Zeichen eines Tokens
    mov  dx, si
    dec  dx                    ; DX = Start dieses Tokens
    mov  di, 1                 ; di = aktueller Tokenindex (1-basiert)

    cmp  di, bx
    je   .measure_this

    ; aktuellen Token bis zum Leerzeichen/0 überspringen
    .skip_this_token:
    lodsb
    cmp  al, 0
    je   .not_found
    cmp  al, ' '
    jne  .skip_this_token

    ; Folge-Leerzeichen überspringen
    .skip_spaces_mid:
    lodsb
    cmp  al, 0
    je   .not_found
    cmp  al, ' '
    je   .skip_spaces_mid

    ; Beginn des nächsten Tokens
    inc  di
    mov  dx, si
    dec  dx
    cmp  di, bx
    je   .measure_this
    jmp  .skip_this_token

    .measure_this:
    ; SI steht bereits auf 2. Zeichen des Tokens (erstes war in AL)
    mov  cx, 1                 ; bisher 1 Zeichen gezählt
    .len_loop:
    lodsb
    cmp  al, 0
    je   .done_len             ; Token endet am Stringende (bereits 0-terminiert)
    cmp  al, ' '
    je   .done_len             ; Token endet am Leerzeichen
    inc  cx
    jmp  .len_loop

    .done_len:
    ; Wenn das Ende durch Leerzeichen kam, dieses in 0 verwandeln.
    cmp  al, ' '
    jne  .keep_zt              ; AL==0 -> bereits 0-terminiert
    mov  byte [si-1], 0        ; letztes gelesenes Zeichen (Leerzeichen) überschreiben
    .keep_zt:
    mov  si, dx                ; SI = Start des Tokens
    clc
    jmp  .ret

    .not_found:
    xor  cx, cx
    stc

    .ret:
    ;pop  di
    ret
%endif
