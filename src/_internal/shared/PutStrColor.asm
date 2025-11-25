; -----------------------------------------------------------------------------
; \file  PutStrColor.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%include 'windows.inc'

; --- String per BIOS-Teletype (AH=0Eh) ausgeben ---
; putc: AL -> Zeichen ausgeben
%if ((DOS_SHELL == 16) && (DOS_MODE == 16))
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
%if ((DOS_SHELL == 16) && (DOS_MODE == 32))
; -----------------------------------------------------------------------------
; unsigned int k_printf(char* message, unsigned int line)
; {
;     char* vidmem = (char*) 0xb8000;
;     unsigned int i = line * 80 * 2;
; 
;     while  (*message != 0) {
;         if (*message == '\\') {
;             *message++;
;             if (*message == 'n') { 
;                 *message++;
;                 line++;
;                 i = (line*80*2);
;                 if (*message == 0) {
;                     return(1);
;                 }
;             }
;         }
;         vidmem[i] = *message; *message++; ++i;
;         vidmem[i] = 0x07;
;         ++i;
;     }
;     return 1;
; }
; -----------------------------------------------------------------------------
PutStrColor:
k_printf:
    push    edi
    push    esi
    push    ebx
    mov     edx, DWORD [esp + 16]
    mov     ebx, DWORD [esp + 20]
    mov     cl , BYTE  [edx]
    lea     eax, [ebx + ebx * 4]
    sal     eax, 5
    test    cl, cl
    jne     .L12
    jmp     .L8
.L21:
    mov     edi, esi
    mov     cl, BYTE [edx]
    mov     esi, edx
    mov     edx, edi
.L10:
    mov     BYTE [eax + TEXT_VRAM    ], cl  ; character
    mov     BYTE [eax + TEXT_VRAM + 1], 7   ; color
    mov     cl, BYTE [esi + 1]
    add     eax, 2
    test    cl, cl
    je      .L8
.L12:
    lea     esi, [edx+1]
    cmp     cl, 92
    jne     .L21
    mov     cl, BYTE [edx + 1]
    cmp     cl, 110
    je      .L11
    add     edx, 2
    jmp     .L10
.L11:
    inc     ebx
    mov     cl, BYTE [edx + 2]
    lea     esi, [edx + 2]
    lea     eax, [ebx + ebx * 4]
    sal     eax, 5
    test    cl, cl
    je      .L8
    add     edx, 3
    jmp     .L10
.L8:
    pop     ebx
    mov     eax, 1
    pop     esi
    pop     edi
    ret
%endif
