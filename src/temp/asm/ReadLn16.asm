; -----------------------------------------------------------------------------
; \file  ReadLn16.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

; -----------------------------------------------------------------------------
; \brief Eingabe holen (DOS Zeileneingabe, mit eigenem Editor/Echo)
; \param DX - buffer
; -----------------------------------------------------------------------------
%if DOS_SHELL == 1
DOSReadLn:
    mov ah, 0Ah
    int 21h              ; Rückkehr nach ENTER; [buf+1]=len, [buf+2..]=Text, [buf+2+len]=0Dh

    ; SI = &Textanfang, BL = len
    mov bx, dx
    lea si, [bx + 2]
    mov bl, [bx + 1]

    ; CR hinter dem Text durch 0x00 ersetzen -> sauber terminierter String
    mov byte [si + bx], 0x00
    
    ; set flag for puts_color
    mov bh, 1
    mov [PTR16(dos_readln_flag)], bh

    ; neue Zeile
    ;mov dx, PTR16(crlf)
    ;mov ah, 09h
    ;int 21h
    
    ret
%endif
