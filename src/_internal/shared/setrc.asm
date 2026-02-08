; build: nasm -f bin setrc.asm -o setrc.com
org 100h
bits 16

start:
    ; PSP:80h = Länge der Kommandozeile (0..127)
    ; PSP:81h.. = Kommandozeile (ohne CR), meist vorangestelltes Space
    mov   si, 81h
    mov   cl, [80h]     ; Länge
    jcxz  .noarg

    ; Skip leading spaces/tabs
.skip_ws:
    cmp   cl, 0
    jz    .noarg
    lodsb
    cmp   al, ' '
    je    .skip_ws
    cmp   al, 9
    je    .skip_ws
    dec   si           ; wir sind 1 zu weit -> zurück
    inc   cl

    ; Dezimalzahl parsen (0..255)
    xor   bx, bx       ; BX = akkumulierte Zahl
.parse:
    cmp   cl, 0
    jz    .have_num
    lodsb
    cmp   al, 13       ; CR?
    je    .have_num
    cmp   al, ' '
    je    .have_num
    cmp   al, 9
    je    .have_num
    sub   al, '0'
    jc    .have_num
    cmp   al, 9
    ja    .have_num
    ; BX = BX*10 + AL
    mov   ah, 0
    mov   dx, bx
    shl   bx, 1        ; *2
    mov   ax, dx
    shl   ax, 1        ; *2
    shl   ax, 1        ; *4
    add   bx, ax       ; *2 + *8 = *10
    add   bl, al
    jmp   .parse

.have_num:
    ; clamp auf 0..255 (BL reicht)
    ; BX enthält Wert; BL ist Low-Byte

    ; "ERRORLEVEL=" ausgeben
    mov   dx, msg
    mov   ah, 09h
    int   21h

    ; Wert als Dezimal drucken (BL)
    mov   al, bl
    call  print_u8_dec

    ; CRLF
    mov   dx, crlf
    mov   ah, 09h
    int   21h

    ; mit AL=BL beenden (AH=4Ch)
    mov   al, bl
    mov   ah, 4Ch
    int   21h

.noarg:
    ; Kein Parameter -> zeige 0 an und exit 0
    mov   dx, msg
    mov   ah, 09h
    int   21h
    mov   al, 0
    call  print_u8_dec
    mov   dx, crlf
    mov   ah, 09h
    int   21h
    mov   ax, 4C00h
    int   21h

; ------- Hilfsroutinen ----------------------------------------
; print_u8_dec: AL = 0..255, gibt Dezimal aus (ohne führende Nullen)
; zerstört: AX,BX,CX,DX
print_u8_dec:
    push si
    xor   ah, ah        ; AX = Wert
    lea   si, [digits+3] ; Buffer von hinten
    mov   cx, 0

.next_div:
    xor   dx, dx
    mov   bx, 10
    div   bx            ; AX / 10, Rest in DX
    add   dl, '0'
    mov   [si], dl
    dec   si
    inc   cx
    cmp   ax, 0
    jne   .next_div

    inc   si
    mov   dx, si
    mov   ah, 09h
    int   21h
    pop   si
    ret

; Daten
msg    db 'ERRORLEVEL=', '$'
crlf   db 13,10,'$'
digits db '0000'      ; Puffer (max 3 Stellen, wir nehmen 4 zur Sicherheit)
