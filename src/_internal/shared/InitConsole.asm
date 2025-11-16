; -----------------------------------------------------------------------------
; \file  InitConsole.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

dos_init_console:
    call dos_get_cols               ; get DOS screen columns
    call dos_get_rows               ; get DOS screen rows
    
    SCREEN_CLEAR
    
    call dos_get_command_line
    ret

; -----------------------------------------------------------------------------
; \brief get DOS screen columns
; -----------------------------------------------------------------------------
dos_get_cols:
    mov  ah, 0Fh
    VideoCall
    ; AL = aktueller Videomodus
    ; AH = Spaltenzahl
    ; BH = aktive Seite
    mov  bl, ah           ; BL = Spalten
    ret

; -----------------------------------------------------------------------------
; \brief get DOS screen rows
; -----------------------------------------------------------------------------
dos_get_rows:
    mov  ax, 1130h
    mov  bh, 00h          ; aktuelle Font/Block
    VideoCall
    mov  dl, dl           ; DL = Zeilen-1
    inc  dl               ; DL = Zeilen
    mov  bh, dl           ; BH = Zeilen
    ret

; -----------------------------------------------------------------------------
; \brief DOS - get command line arguments from PSP ...
; -----------------------------------------------------------------------------
dos_get_command_line:
    xor  ax, ax
    mov  si, 81h          ; SI -> Beginn der Kommandozeile im PSP
    mov  cl, [80h]        ; CL = Länge
    xor  ch, ch           ; CX = Länge

    jcxz .no_args       ; nichts übergeben?
    ; Zielpuffer vorbereiten
    mov  di, PTR16(_cA_cmd_buf) ; DI -> Ziel
    .copy:
    lodsb                 ; AL = [DS:SI], SI++
    cmp   al, 0x0D        ; CR markiert das Ende (Sicherheit)
    je   .done_copy
    stosb                 ; [ES:DI]=AL (ES=DS in .COM), DI++
    loop .copy

    .done_copy:
    mov  al, 0
    stosb
    
    ; Trim: nachlaufende Spaces entfernen
    .trim:
    cmp  di, PTR16(_cA_cmd_buf)
    jbe  .make_dos_str
    dec  di
    cmp  byte [di], ' '
    je   .trim
    inc  di

    .make_dos_str:
    mov  byte [di], 0     ; für DOS-Funktion 09h Stringabschluss
    jmp  .next
    
    .no_args:
    SCREEN_CLEAR
    SET_CURSOR 0, 1
    PUTS_COLOR noargs_msg, 0x02 | 0x10
    SET_CURSOR 0, 2
    DOS_Exit   0          ; exit - no args.
    
    .next:
    SET_CURSOR 0, 0
    ret
