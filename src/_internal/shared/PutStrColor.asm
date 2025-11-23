; -----------------------------------------------------------------------------
; \file  PutStrColor.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

; --- String per BIOS-Teletype (AH=0Eh) ausgeben ---
; putc: AL -> Zeichen ausgeben
%if DOS_SHELL == 1
putc:
    push dx
    mov dl, al
    mov ah, 02h
    SysCall
    pop dx
    ret

; crlf: \r\n
DOSrncrlf:
    mov al, 13
    call putc
    mov al, 10
    call putc
    ret

DOSPutStrColor:
    mov  ah, 09h
    SysCall
    ret

print_z:
    push dx             ; save DX
    mov si, dx
    .find_end:
    lodsb               ; AL = [SI], SI++
    cmp  al, 0
    jne .find_end       ; repeat, till 0x00 is found
    dec si              ; SI points to 0x00
    
    mov al, '$'         ; set DOS String end mark
    mov [si], al        ; append AL
    inc si
    mov byte [si], 0    ; end of C-String
    
    mov [PTR16(fdbuf)], si
    DOS_Write fdbuf
    pop dx              ; restore DX
    ret

; DX -> 0-terminierte Zeichenkette
DOS_ConsoleWrite:
    push ax
    push dx
    push si
    mov si, dx
    .print_z_loop:
    lodsb
    cmp al, '$'
    je .pe_done
    call putc
    inc si
    jmp .print_z_loop
    .pe_done:
    pop si
    pop dx
    pop ax
    ret

PutStrColor:
    push bx
    
    mov  bh, [PTR16(dos_readln_flag)]
    cmp  bh, 0
    je   .no_length
    add  si, 2
    mov  bh, 0
    mov  [PTR16(dos_readln_flag)], bh
    .no_length:
    pop  bx
    
    mov  dx, [PTR16(dos_xpos)]
    ; -------------------
    .print_loop:
    lodsb                ; AL := [SI], SI++
    
    COMPARE al, 0x00, .printed  ; reach end  ?
    COMPARE al, 0x0d, .printed
    COMPARE al, 0x0a, .printed
    
    test al, al
    jz   .printed
    mov  ah, 09h         ; Teletype-Ausgabe
    mov  bh, 0           ; page 0 todo
    mov  cx, 1           ; mim
    VideoCall
    
    mov ah, 0x02
    mov bh, 0
    inc dx
    VideoCall
    
    jmp  .print_loop

    .printed:
    ;call  DOS_getCursor
    ret
    
; --- Cursorposition lesen (AH=03h) ---
DOS_getCursor:
    push dx
    push di
    push si
    
    mov  ah, 03h         ; Read Cursor Position
    mov  bh, 0           ; Videoseite 0
    VideoCall            ; Rückgabe: DH=Zeile, DL=Spalte (0-basiert)
    
    mov  [PTR16(dos_ypos)], dh
    mov  [PTR16(dos_xpos)], dl
    
    pop  si
    pop  di
    pop  dx
    ret
%endif
