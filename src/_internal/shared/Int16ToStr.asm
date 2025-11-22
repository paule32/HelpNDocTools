; -----------------------------------------------------------------------------
; \file  Int16ToStr.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

; ----------------------------------------------------------------------------
; \brief  convert number from AX register to a string.
; \param  AX: 16-Bit value
; \param  DI: destination buffer
; \return ASCII-decimal without trailing zeros.
;         (min. onr digit, and '0' at end.
;
; \note   destroy's: AX,BX,CX,DX (internal saved)
; \note   buffer: max. 5 digits + '$' => min. 6 bytes
; ----------------------------------------------------------------------------
DOSIntToStr:
    push ax
    push bx
    push cx
    push dx
    push di

    mov bx, 10
    xor cx, cx                 ; Zähler für gepushte Reste

    cmp ax, 0
    jne .div_loop
    mov byte [di], '0'
    inc di
    jmp short .finish

    .div_loop:
    xor dx, dx                 ; DX:AX / 10
    div bx                     ; AX = Quotient, DX = Rest (0..9)
    push dx
    inc cx
    test ax, ax
    jne .div_loop

    .write_loop:
    pop dx
    add dl, '0'
    mov [di], dl
    inc di
    loop .write_loop

    .finish:
    mov byte [di], 0x00

    pop di
    pop dx
    pop cx
    pop bx
    pop ax
    ret
