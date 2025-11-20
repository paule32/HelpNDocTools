; -----------------------------------------------------------------------------
; \file  code16.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%define DOS_SHELL 1
%define MAX_ARGS  7
bits 16
code16_start:
    INIT_COMMAND_LINE
    INIT_CONSOLE
        
    READL_CON_A dos_buffer
    SET_CURSOR  10, 5
    PUTS_COLOR  dos_buffer, 0x02 | 0x10
    
    ; text + prompt ausgeben
    ;SET_CURSOR 2, 10
    ;PUTS_COLOR dos_prompt, 0x0E | 0x10
    
    ;SET_CURSOR 10, 10
    ;READL_CON_A dos_buffer
    
    ;SET_CURSOR 10, 3
    ;PUTS_COLOR dos_buffer, 0x0E | 0x10
    
    ;SET_CURSOR 10, 7
    ;PUTS_COLOR cmd_buf, 0x0E | 0x10
    
    ;SET_CURSOR 20, 7
    ;PUTS_COLOR DBFNAME, 0x0E
;    DOS_Exit 0

; -----------------------------------------------------------------------------
; dbfmake.asm  - Create/Append field into dBASE III/IV DBF by INT 21h
; Build:  nasm -f bin dbfmake.asm -o DBFMAKE.COM
; Run:    DBFMAKE <type> <cmd> <feldtype> <feldname> <feldlaenge>
; Example:
;   DBFMAKE 3 CREATE C NAME 20
;   DBFMAKE 4 APPEND I AGE 3
; Type: 3 (dBASE III), 4 (dBASE IV)
; Cmd:  CREATE | APPEND
; Feldtype: C,I,F,B,D,T  (T only for type 4)
; Feldname: max 10 Zeichen (dBASE-Beschränkung, 11. Byte = 0)
; Feldlaenge: Dezimal (z.B. 20)
; -----------------------------------------------------------------------------

    GET_CURSOR
    SET_CURSOR 20, 7
    PUTS_COLOR 'schärpfel', 2
    
    SET_CURSOR 20, 8
    PUTS_COLOR 'schupfel', 3

    CMP_CHR ARGV_1, 3, '5', is_three
    CMP_STR 'zuza', 'zuza', is_okk
        
    SET_CURSOR 20, 3
    PUTS_COLOR ARGV_2, 1
    DOS_Exit 0
    
    is_three:
    SET_CURSOR 20, 5
    PUTS_COLOR SI, 0x0F
    DOS_Exit   0
    
    is_okk:
    SET_CURSOR 40, 5
    PUTS_COLOR 'mufti', 0x1C
    DOS_Exit   0
    ;ret
jmp usage
    .token_done:
    DOS_Exit 0
        
    ; -------- <type> --------
    call next_token
    jc  usage
    mov dx, PTR16(tokbuf)
    call parse_u16
    jc  badargs
    cmp ax, 3
    je  .have_type
    cmp ax, 4
    jne badargs
    .have_type:
    mov [PTR16(g_type)], ax

    ; -------- <cmd> --------
    call next_token
    jc  usage
    call upper_inplace_dx
    mov si, dx
    mov di, PTR16(str_CREATE)
    call strcmp
    test ax, ax
    jz  .cmd_create
    mov di, PTR16(str_APPEND)
    mov si, dx
    call strcmp
    test ax, ax
    jz  .cmd_append
    jmp badargs
    .cmd_create:
    mov byte [PTR16(g_cmd)], 1
    jmp .got_cmd
    .cmd_append:
    mov byte [PTR16(g_cmd)], 2
    .got_cmd:

    ; -------- <feldtype> --------
    call next_token
    jc  usage
    mov si, dx
    mov al, [si]          ; erstes Zeichen des Tokens
    call to_upper
    mov [PTR16(g_ftype)], al

    ; -------- <feldname> (max 10) --------
    mov di, PTR16(fldname)
    call copy_token_max_10
    jc  usage
    mov byte [di], 0      ; Nullterminierung (Routine schreibt sie ohnehin)

    ; -------- <feldlaenge> --------
    call next_token
    jc  usage
    mov dx, PTR16(tokbuf)
    call parse_u16
    jc  badargs
    mov [PTR16(g_flen)], ax

    ; --- Feldtyp mappen + Länge validieren ---
    mov al, [PTR16(g_ftype)]
    call map_fieldtype      ; AL=DBF Type, BL=fixedLen(0/const), BH=only4
    jc  badargs
    cmp bh, 1
    jne .ok_ftyp
    cmp word [PTR16(g_type)], 4
    jne not_supported
    .ok_ftyp:
    cmp bl, 0
    je  .keep_len
    mov byte [PTR16(g_flen)    ], bl   ; fixe Länge erzwingen
    mov byte [PTR16(g_flen) + 1], 0
    .keep_len:
    mov ax, [PTR16(g_flen)]
    mov dl, [PTR16(g_ftype)]
    call validate_length
    jc  badargs

    ; Datum für Header holen
    mov ah, 2Ah
    int 21h
    mov [PTR16(g_year)], cx
    mov [PTR16(g_month)], dh
    mov [PTR16(g_day)], dl

    ; --- Dispatch nach CMD ---
do_dispatch:
    cmp byte [PTR16(g_cmd)], 1
    je  do_create
    jmp do_append

; --- Hex-Ausgabe (AX -> XXXXh, nutzt int 21h/AH=02h) ---
print_hex16:
    push ax
    push bx
    push cx
    push dx
    mov  bx, ax
    mov  cx, 4
    .next_nibble:
    rol  bx, 4
    mov  dl, bl
    and  dl, 0Fh
    add  dl, '0'
    cmp  dl, '9'
    jbe  .out
    add  dl, 7          ; 'A'..'F'
    .out:
    mov  ah, 02h
    int  21h
    loop .next_nibble
    mov  dl, 'h'
    mov  ah, 02h
    int  21h
    mov  dl, 13         ; CR LF
    int  21h
    mov  dl, 10
    int  21h
    pop  dx
    pop  cx
    pop  bx
    pop  ax
    ret
; ---------------- CREATE ----------------
do_create:
    ; vorhandene Datei (ignoriert Fehler) löschen
    mov dx, PTR16(_cA_DBFNAME)
    mov ah, 41h
    int 21h

    ; neu anlegen
    mov dx, PTR16(_cA_DBFNAME)
    mov cx, 0
    mov ah, 3Ch
    int 21h
    jc  io_error
    mov [PTR16(hFile)], ax

    ; Header + 1 Feld bauen und schreiben
    call build_header_for_new
    call write_full_header

    ; schließen
    mov bx, [PTR16(hFile)]
    mov ah, 3Eh
    int 21h
    
;todo paule32
;    DOS_WriteLn msg_ok_create

    ;lea dx, PTR16(msg_ok_create)

    call print_$
    DOS_crlf
    jmp exit0

; ---------------- APPEND ----------------
do_append:
    ; RDWR öffnen
    mov dx, PTR16(_cA_DBFNAME)
    mov ax, 3D02h
    int 21h
    jc  open_fail
    mov [PTR16(hFile)], ax

    ; Header lesen (32)
    mov bx, [PTR16(hFile)]
    mov dx, PTR16(header)
    mov cx, 32
    mov ah, 3Fh
    int 21h
    jc  io_error
    cmp ax, 32
    jne io_error

    ; Typ prüfen
    mov al, [PTR16(header)+0]
    cmp word [PTR16(g_type)], 3
    jne .chk4
    cmp al, 03h
    jne ver_mismatch
    jmp .t_ok
    .chk4:
    cmp al, 04h
    jne ver_mismatch
    .t_ok:

    ; Records==0?
    mov ax, [PTR16(header)+4]
    mov dx, [PTR16(header)+6]
    or  ax, ax
    or  dx, dx
    jnz append_with_records_not_supported

    ; Header-/Recordlänge
    mov ax, [PTR16(header)+8]
    mov [PTR16(hdr_len)], ax
    mov ax, [PTR16(header)+10]
    mov [PTR16(rec_len)], ax

    ; Felddeskriptoren laden (hdr_len - 32)
    mov ax, [PTR16(hdr_len)]
    sub ax, 32
    jbe bad_header
    mov bx, [PTR16(hFile)]
    mov dx, PTR16(fdescbuf)
    mov cx, ax
    mov ah, 3Fh
    int 21h
    jc  io_error
    mov [PTR16(fdbuf_size)], ax

    ; existiert Feld?
    call field_exists
    jc  field_already

    ; Terminator finden
    mov si, PTR16(fdescbuf)
    mov cx, [PTR16(fdbuf_size)]
    .find_term:
    cmp cx, 0
    je  bad_header
    cmp byte [si], 0Dh
    je  .term_found
    add si, 32
    sub cx, 32
    jmp .find_term
    .term_found:
    ; neuen FD in tempdesc bauen
    call build_one_descriptor_to_temp
    ; 32 Byte an Terminatorstelle kopieren
    push si
    mov di, si
    mov si, PTR16(tempdesc)
    mov cx, 32
    rep movsb
    pop si
    ; neuen Terminator hinterher
    mov byte [si], 0Dh

    ; Header anpassen
    mov ax, [PTR16(hdr_len)]
    add ax, 32
    mov [PTR16(hdr_len)], ax
    mov [PTR16(header)+8], ax
    mov ax, [PTR16(rec_len)]
    add ax, [PTR16(g_flen)]
    mov [PTR16(rec_len)], ax
    mov [PTR16(header)+10], ax

    ; an BOF seeken
    mov bx, [PTR16(hFile)]
    xor dx, dx
    xor cx, cx
    mov ax, 4200h
    int 21h

    ; Header schreiben (32)
    mov bx, [PTR16(hFile)]
    mov dx, PTR16(header)
    mov cx, 32
    mov ah, 40h
    int 21h
    jc  io_error

    ; FD-Region schreiben (hdr_len - 32)
    mov ax, [PTR16(hdr_len)]
    sub ax, 32
    mov cx, ax
    mov dx, PTR16(fdescbuf)
    mov bx, [hFile]
    mov ah, 40h
    int 21h
    jc  io_error

    ; schließen
    mov bx, [PTR16(hFile)]
    mov ah, 3Eh
    int 21h

    mov dx, PTR16(msg_ok_append)
    call print_$
    DOS_crlf
    jmp exit0

; ---------------- Helper: Build/Write ----------------

; build_header_for_new: header + 1 FD in fdescbuf (mit 0Dh) erzeugen
build_header_for_new:
    push ax
    push bx
    push cx
    push dx

    ; clear header (32) + fdescbuf
    mov di, PTR16(header)
    mov cx, 16
    xor ax, ax
    rep stosw
    mov di, PTR16(fdescbuf)
    mov cx, 2048
    rep stosw

    ; version
    mov ax, [PTR16(g_type)]
    cmp ax, 3
    jne .v4
    mov byte [PTR16(header)+0], 03h
    jmp .v_ok
    .v4:
    mov byte [PTR16(header)+0], 04h
    .v_ok:
    ; date YY,MM,DD
    mov ax, [PTR16(g_year)]
    mov bx, 100
    xor dx, dx
    div bx            ; AX=year/100, DX=YY
    mov al, dl
    mov [PTR16(header)+1], al
    mov al, [PTR16(g_month)]
    mov [PTR16(header)+2], al
    mov al, [PTR16(g_day)]
    mov [PTR16(header)+3], al

    ; num records = 0
    mov dword [PTR16(header)+4], 0

    ; record length = 1 (delete flag) + field len
    mov ax, [PTR16(g_flen)]
    add ax, 1
    mov [PTR16(header)+10], ax
    mov [PTR16(rec_len)], ax

    ; header length = 32 + 32 (one FD) + 1 (0Dh)
    mov ax, 32+32+1
    mov [PTR16(header)+8], ax
    mov [PTR16(hdr_len)], ax

    ; MDX/langid = 0

    ; FD in fdescbuf und Terminator
    mov di, PTR16(fdescbuf)
    call build_one_descriptor_at_di
    mov byte [PTR16(fdescbuf)+32], 0Dh

    pop dx
    pop cx
    pop bx
    pop ax
    ret

; write_full_header: schreibt Header (32) + FD-Region (hdr_len-32)
write_full_header:
    ; seek BOF
    mov bx, [PTR16(hFile)]
    xor dx, dx
    xor cx, cx
    mov ax, 4200h
    int 21h
    ; header
    mov bx, [PTR16(hFile)]
    mov dx, PTR16(header)
    mov cx, 32
    mov ah, 40h
    int 21h
    jc  io_error
    ; FD region
    mov ax, [PTR16(hdr_len)]
    sub ax, 32
    mov cx, ax
    mov dx, PTR16(fdescbuf)
    mov bx, [PTR16(hFile)]
    mov ah, 40h
    int 21h
    jc  io_error
    ret

; build_one_descriptor_at_di: DI->32 Byte Ziel
build_one_descriptor_at_di:
    push si
    push ax
    push cx

    ; name (max 10 + 0) in 11 Bytes
    mov si, PTR16(fldname)
    mov cx, 11
    .ncopy:
    lodsb
    cmp al, 0
    je  .padz
    stosb
    loop .ncopy
    jmp .name_done
    .padz:
    stosb
    dec cx
    jz  .name_done
    mov al, 0
    rep stosb
    .name_done:

    ; type char
    mov al, [PTR16(g_ftype)]
    call map_fieldtype_char_only
    stosb

    ; data address (4) = 0
    xor ax, ax
    mov cx, 4
    rep stosb

    ; length (1)
    mov ax, [PTR16(g_flen)]
    mov al, al
    stosb

    ; decimals (1) = 0
    mov al, 0
    stosb

    ; reserved(2)
    stosb
    stosb

    ; flags(1)=0
    mov al, 0
    stosb

    ; autoinc next(4)+step(1)+reserved(6)=0
    mov cx, 11
    mov al, 0
    rep stosb

    pop cx
    pop ax
    pop si
    ret

build_one_descriptor_to_temp:
    mov di, PTR16(tempdesc)
    call build_one_descriptor_at_di
    ret

; field_exists: CF=1 wenn Name bereits vorhanden
field_exists:
    push si
    push di
    push cx
    push ax
    mov si, PTR16(fdescbuf)
    mov cx, [PTR16(fdbuf_size)]
    .floop:
    cmp cx, 0
    je  .no
    cmp byte [si], 0Dh
    je  .no
    ; vergleiche 0-term feldname (bis 11)
    push si
    mov di, PTR16(fldname)
    mov bx, 11
    mov dx, 1          ; assume match
    .cmpn:
    mov al, [si]
    mov ah, [di]
    cmp ah, 0
    je  .endcmp
    cmp al, ah
    jne .not
    inc si
    inc di
    dec bx
    jnz .cmpn
    .endcmp:
    ; wenn bis 0 gleich -> match
    jmp .match
    .not:
    mov dx, 0
    .match:
    pop si
    cmp dx, 1
    je  .yes
    add si, 32
    sub cx, 32
    jmp .floop
    .yes:
    stc
    pop ax
    pop cx
    pop di
    pop si
    ret
    .no:
    clc
    pop ax
    pop cx
    pop di
    pop si
    ret

; ---------------- Token/Parsing ----------------

; next_token: PSP tail -> tokbuf, DX=tokbuf, CF=1 wenn keins
next_token:
    push ax
    push di
    ; skip ws
    .nt_skip:
    cmp bl, 0
    je  .none
    mov al, [si]
    inc si
    dec bl
    cmp al, 13
    je  .none
    cmp al, ' '
    je  .nt_skip
    cmp al, 9
    je  .nt_skip
    dec si
    inc bl
    ; copy
    mov di, PTR16(_cA_cmd_buf)
    .nt_copy:
    cmp bl, 0
    je  .done
    mov al, [si]
    cmp al, 13
    je  .done
    cmp al, ' '
    je  .done
    cmp al, 9
    je  .done
    mov [di], al
    inc di
    inc si
    dec bl
    jmp .nt_copy
    .done:
    mov byte [di], 0
    mov dx, PTR16(_cA_cmd_buf)
    clc
    pop di
    pop ax
    ret
    .none:
    stc
    pop di
    pop ax
    ret

; copy_token_max_10: SI/BL => [DI], max 10, 0-term, CF wie oben
copy_token_max_10:
    push ax
    push cx
    ; skip ws
    .ct10_skip:
    cmp bl, 0
    je  .none
    mov al, [si]
    inc si
    dec bl
    cmp al, 13
    je  .none
    cmp al, ' '
    je  .ct10_skip
    cmp al, 9
    je  .ct10_skip
    dec si
    inc bl
    ; copy up to 10
    mov cx, 10
    .ct10_copy:
    cmp bl, 0
    je  .end
    mov al, [si]
    cmp al, 13
    je  .end
    cmp al, ' '
    je  .end
    cmp al, 9
    je  .end
    cmp cx, 0
    je  .skip_rest
    mov [di], al
    inc di
    inc si
    dec bl
    dec cx
    jmp .ct10_copy
    .skip_rest:
    cmp bl, 0
    je  .end
    mov al, [si]
    inc si
    dec bl
    cmp al, 13
    je  .end
    cmp al, ' '
    jne .skip_rest
    .end:
    mov byte [di], 0
    clc
    pop cx
    pop ax
    ret
    .none:
    stc
    pop cx
    pop ax
    ret

; strcmp: SI=str1, DI=str2, AX=0 bei Gleichheit (ZF=1)
strcmp:
    push si
    push di
    .sc_loop:
    lodsb
    mov ah, [di]
    inc di
    call to_upper_al
    call to_upper_ah
    cmp al, ah
    jne .ne
    test al, al
    jnz .sc_loop
    xor ax, ax
    or  ax, ax
    pop di
    pop si
    ret
    .ne:
    mov ax, 1
    or  ax, ax
    pop di
    pop si
    ret

; parse_u16: DX->zstr, AX=result, CF=1 bei Fehler
parse_u16:
    push bx
    push si
    mov si, dx
    xor ax, ax
    .pu_loop:
    lodsb
    test al, al
    jz  .ok
    cmp al, '0'
    jb  .err
    cmp al, '9'
    ja  .err
    sub al, '0'         ; digit in AL
    mov bx, ax          ; BX = acc
    shl ax, 1           ; acc*2
    mov dx, ax
    shl ax, 2           ; acc*8
    add ax, dx          ; acc*10
    add ax, bx          ; +digit
    jc  .err
    jmp .pu_loop
    .ok:
    clc
    pop si
    pop bx
    ret
    .err:
    stc
    pop si
    pop bx
    ret

; upper_inplace_dx: DX->zstr upper-case
upper_inplace_dx:
    push ax
    push dx
    mov si, dx
    .upl:
    lodsb
    test al, al
    jz  .done
    call to_upper
    mov [si-1], al
    jmp .upl
    .done:
    pop dx
    pop ax
    ret

; to_upper helpers
to_upper:
    cmp al, 'a'
    jb  .ret
    cmp al, 'z'
    ja  .ret
    sub al, 32
    .ret:
    ret
to_upper_al:
    call to_upper
    ret
to_upper_ah:
    xchg al, ah
    call to_upper
    xchg al, ah
    ret

; map_fieldtype: AL=CLI(C/I/F/B/D/T)-> DBF Typ in [g_ftype_mapped]
; out: AL=dbfType, BL=fixedLen(0/const), BH=only4(1=T), CF=1 on error
map_fieldtype:
    push ax
    call to_upper_al
    cmp al, 'C'
    je .C
    cmp al, 'I'
    je .I
    cmp al, 'F'
    je .F
    cmp al, 'B'
    je .B
    cmp al, 'D'
    je .D
    cmp al, 'T'
    je .T
    stc
    jmp .out
    .C: mov al, 'C'   ; 1..254
    xor bl, bl
    xor bh, bh
    jmp .ok
    .I: mov al, 'N'   ; 1..20
    xor bl, bl
    xor bh, bh
    jmp .ok
    .F: mov al, 'F'   ; 1..20
    xor bl, bl
    xor bh, bh
    jmp .ok
    .B: mov al, 'L'   ; exakt 1
    mov bl, 1
    xor bh, bh
    jmp .ok
    .D: mov al, 'D'   ; exakt 8
    mov bl, 8
    xor bh, bh
    jmp .ok
    .T: mov al, 'T'   ; exakt 8, nur Typ 4
    mov bl, 8
    mov bh, 1
    jmp .ok
    .ok:
    mov [PTR16(g_ftype_mapped)], al
    clc
    .out:
    pop ax
    ret

map_fieldtype_char_only:
    push bx
    call map_fieldtype
    mov al, [PTR16(g_ftype_mapped)]
    pop bx
    ret

; validate_length: AX=len, DL=CLI type (upper), CF=1 invalid
validate_length:
    push ax
    push dx
    call to_upper_dl
    cmp dl, 'B'       ; 1
    jne .nB
        cmp ax, 1
        jne .bad
        jmp .ok
    .nB:
    cmp dl, 'D'       ; 8
    jne .nD
        cmp ax, 8
        jne .bad
        jmp .ok
    .nD:
    cmp dl, 'T'       ; 8
    jne .nT
        cmp ax, 8
        jne .bad
        jmp .ok
    .nT:
    cmp dl, 'C'       ; 1..254
    jne .nC
        cmp ax, 1
        jb .bad
        cmp ax, 254
        ja .bad
        jmp .ok
    .nC:
    cmp dl, 'I'       ; 1..20
    jne .nI
        cmp ax, 1
        jb .bad
        cmp ax, 20
        ja .bad
        jmp .ok
    .nI:
    cmp dl, 'F'       ; 1..20 (konservativ)
    jne .bad
        cmp ax, 1
        jb .bad
        cmp ax, 20
        ja .bad
        jmp .ok
    .ok:
    clc
    pop dx
    pop ax
    ret
    .bad:
    stc
    pop dx
    pop ax
    ret

to_upper_dl:
    xchg al, dl
    call to_upper
    xchg al, dl
    ret

; --------- Ausgabe & Exit ---------
print_$:
    mov ah, 09h
    int 21h
    ret

field_already:
    ; Datei schließen und Hinweis ausgeben
    mov bx, [hFile]
    mov ah, 3Eh
    int 21h
    mov dx, PTR16(msg_fieldexists)
    call print_$
    DOS_crlf
    jmp exit0

usage:
    PUTS_COLOR msg_usage, 0x02
    jmp exit1

badargs:
    PUTS_COLOR msg_badargs, 0x02
    ;DOS_crlf
    jmp exit1

open_fail:
    PUTS_COLOR msg_openfail, 0x02
    jmp exit1

ver_mismatch:
    PUTS_COLOR msg_ver_mismatch, 0x02
    jmp exit1

append_with_records_not_supported:
    PUTS_COLOR msg_append_recs, 0x02
    jmp exit1

not_supported:
    PUTS_COLOR msg_not_supported, 0x02
    jmp exit1

io_error:
    PUTS_COLOR msg_ioerr, 0x02
    jmp exit1

bad_header:
    PUTS_COLOR msg_badheader, 0x02
    jmp exit1

exit0:
    DOS_Exit 0
exit1:
    DOS_Exit 1

;------------------------------------------------------------------------------
; dbfhead.asm - dBASE IV DBF-Header anzeigen (DOS .COM)
; Assemble: nasm -f bin dbfhead.asm -o DBFHEAD.COM
; Lauf:      DBFHEAD TEST.DBF
; -----------------------------------------------------------------------------
    ; Kommandozeile aus PSP:80h holen -> Dateiname parsen
    mov si, 80h            ; PSP:80h = Längenbyte gefolgt vom Tail
    lodsb                  ; AL = Länge
    mov bl, al             ; BL = verbleibende Zeichen
    jz  .usage
    mov di, PTR16(filename)
    call skip_spaces_2
    jc  .usage
    call copy_token_to_di_2  ; kopiert bis Space/CR
    mov byte [di], 0       ; 0-terminiert

    ; Datei öffnen (INT 21h, 3Dh)
    mov dx, PTR16(filename)
    mov ax, 3D00h          ; AH=3Dh open, AL=0 read-only
    int 21h
    jc  .open_fail
    mov [PTR16(hFile)], ax

    ; 32 Bytes Header lesen
    mov bx, [PTR16(hFile)]
    mov dx, PTR16(header)
    mov cx, 32
    mov ah, 3Fh
    int 21h
    jc  .read_fail
    cmp ax, 32
    jne .read_fail

    ; Headerfelder auswerten
    ; Version
    mov al, [PTR16(header) + 0]
    mov [PTR16(verByte)], al

    ; Datum: YY, MM, DD (Bytes 1..3)
    mov al, [PTR16(header) + 1]
    mov [PTR16(yy)], al
    mov al, [PTR16(header) + 2]
    mov [PTR16(mm)], al
    mov al, [PTR16(header) + 3]
    mov [PTR16(dd)], al

    ; Anzahl Datensätze (4..7) -> 32-bit LE in regs: DX:AX
    mov ax, [PTR16(header) + 4]
    mov dx, [PTR16(header) + 6]
    mov [PTR16(rec32) + 0], ax
    mov [PTR16(rec32) + 2], dx

    ; Headerlänge (8..9), Satzlänge (10..11)
    mov ax, [PTR16(header) +  8]
    mov [PTR16(hdr_len)], ax
    mov ax, [PTR16(header) + 10]
    mov [PTR16(rec_len)], ax

    ; MDX-Flag (28), Languagedriver (29)
    mov al, [PTR16(header)+28]
    mov [PTR16(mdx)], al
    mov al, [PTR16(header)+29]
    mov [PTR16(lang)], al

    ; Ausgabe Header-Info
    mov dx, PTR16(msgTitle)
    call print_$

    mov dx, PTR16(msgVer)
    call print_$
    mov al, [PTR16(verByte)]
    call print_hex8
    DOS_crlf

    mov dx, PTR16(msgDate)
    call print_$
    mov al, [PTR16(yy)]
    call print_dec8
    mov al, '-'
    call putc
    mov al, [PTR16(mm)]
    call print_dec8
    mov al, '-'
    call putc
    mov al, [PTR16(dd)]
    call print_dec8
    DOS_crlf

    mov dx, PTR16(msgRecs)
    call print_$
    ; 32-bit hex ausgeben: DX:AX aus rec32
    mov ax, [PTR16(rec32) + 0]
    mov dx, [PTR16(rec32) + 2]
    call print_hex32
    DOS_crlf

    mov dx, PTR16(msgHdr)
    call print_$
    mov ax, [PTR16(hdr_len)]
    call print_dec16
    DOS_crlf

    mov dx, PTR16(msgRec)
    call print_$
    mov ax, [PTR16(rec_len)]
    call print_dec16
    DOS_crlf

    mov dx, PTR16(msgMDX)
    call print_$
    mov al, [PTR16(mdx)]
    call print_hex8
    DOS_crlf

    mov dx, PTR16(msgLang)
    call print_$
    mov al, [PTR16(lang)]
    call print_hex8
    DOS_crlf
    DOS_crlf

    ; Feld-Deskriptoren lesen:
    ; Anzahl Bytes bis Terminator = hdr_len - 32
    mov ax, [PTR16(hdr_len)]
    sub ax, 32
    jbe .no_fields
    mov bx, [PTR16(hFile)]
    mov dx,  PTR16(fdbuf)
    mov cx, ax
    mov ah, 3Fh
    int 21h
    jc  .read_fail
    ; AX = tatsächlich gelesene Bytes

    mov dx, PTR16(msgFields)
    call print_$
    DOS_crlf

    ; Durch fdbuf iterieren: 32-Byte Blöcke bis 0Dh
    mov si, PTR16(fdbuf)
    mov cx, ax           ; CX = bytes available
    xor bp, bp           ; BP = Feldindex

    .next_field:
    cmp cx, 0
    jbe .done_fields
    ; Terminator?
    cmp byte [si], 0Dh
    je  .done_fields

    ; Feldnummer ausgeben
    inc bp
    mov dx, PTR16(msgFieldN)
    call print_$
    mov ax, bp
    call print_dec16
    mov dx, PTR16(msgColonSp)
    call print_$

    ; Feldname (11 Byte, 0-terminiert)
    ; Wir kopieren/normalisieren in namebuf
    push si
    mov di, PTR16(_cA_namebuf)
    mov bx, 11
    .copy_name:
    mov al, [si]
    cmp al, 0
    je  .pad_zero
    ; Nur druckbare? Einfach übernehmen
    mov [di], al
    inc di
    inc si
    dec bx
    jnz .copy_name
    jmp short .name_done
    .pad_zero:
    mov [di], al
    .name_done:
    mov byte [di], 0
    ; Ausgabe Name
    DOS_Write namebuf
    mov dx, PTR16(msgCommaSp)
    call print_$

    ; Feldtyp (Byte 11)
    pop si               ; si zurück auf Start des FD
    mov al, [si+11]
    call putc
    mov dx, PTR16(msgCommaSp)
    call print_$

    ; Länge (Byte 16), Dezimal (Byte 17)
    mov al, [si+16]
    mov ah, 0
    call print_dec16
    mov dx, PTR16(msgSlash)
    call print_$
    mov al, [si+17]
    mov ah, 0
    call print_dec16
    DOS_crlf

    ; Nächster Descriptor
    add si, 32
    sub cx, 32
    jmp .next_field

    .done_fields:
    jmp .close_and_exit

    .no_fields:
    mov dx, PTR16(msgNoFields)
    call print_$
    DOS_crlf
    jmp .close_and_exit

; ----- Fehlerpfade & Exit -----
    .usage:
    mov dx, PTR16(msgUsage)
    call print_$
    jmp .exit

    .open_fail:
    mov dx, PTR16(msgOpenErr)
    call print_$
    jmp .exit

    .read_fail:
    mov dx, PTR16(msgReadErr)
    call print_$
    jmp .close_and_exit

    .close_and_exit:
    mov bx, [PTR16(hFile)]
    mov ah, 3Eh
    int 21h
    .exit:
    mov ax, 4C00h
    int 21h

; ======== Hilfsroutinen ========
; print_$: DX -> '$'-terminierte Zeichenkette
print_$_2:
    mov ah, 09h
    int 21h
    ret

; print_hex8: AL -> 2 HEX
print_hex8:
    push ax
    push bx
    mov bl, al
    mov bh, al
    shr bl, 4
    and bh, 0Fh
    mov al, bl
    call hex_nibble
    mov al, bh
    call hex_nibble
    pop bx
    pop ax
    ret

hex_nibble:
    and al, 0Fh
    cmp al, 9
    jbe .digit
    add al, 7
    .digit:
    add al, '0'
    call putc
    ret

; print_hex32: DX:AX -> 8 HEX
print_hex32:
    push ax
    push dx
    mov ax, dx
    call print_hex16
    pop dx
    pop ax
    call print_hex16
    ret

; print_dec8: AL (0..255) ohne führende Nullen
print_dec8:
    push ax
    xor ah, ah
    call print_dec16
    pop ax
    ret

; print_dec16: AX -> dezimal ohne führende Nullen
; einfache Division durch 10
print_dec16:
    push ax
    push bx
    push dx
    push cx
    mov cx, 0          ; Zähler Ziffern im Stack
    cmp ax, 0
    jne .pd_loop
    mov al, '0'
    call putc
    jmp .pd_done
    .pd_loop:
    xor dx, dx
    mov bx, 10
    div bx            ; AX = AX/10, DX = Rest
    push dx           ; Rest (Ziffer)
    inc cx
    cmp ax, 0
    jne .pd_loop
    .pd_out:
    pop dx
    add dl, '0'
    mov al, dl
    call putc
    loop .pd_out
    .pd_done:
    pop cx
    pop dx
    pop bx
    pop ax
    ret

; --- Kommandozeilen-Parsing ---
; skip_spaces: SI->Tail, BL=Restlänge. Setzt ZF=1 wenn nichts übrig.
skip_spaces_2:
    push ax
    .ss_loop:
    cmp bl, 0
    jz  .ss_empty
    mov al, [si]
    inc si
    dec bl
    cmp al, ' '
    jz  .ss_loop
    cmp al, 9
    jz  .ss_loop
    ; ein Nicht-Leerzeichen gesehen -> SI eine Position zurück
    dec si
    inc bl
    clc
    pop ax
    ret
    .ss_empty:
    stc
    pop ax
    ret

; copy_token_to_di: kopiert ab SI bis Space/CR nach DI, aktualisiert SI/BL
copy_token_to_di_2:
    push ax
    .ct_loop:
    cmp bl, 0
    jz  .ct_done
    mov al, [si]
    cmp al, 13         ; CR
    je  .ct_done
    cmp al, ' '
    je  .ct_done
    mov [di], al
    inc di
    inc si
    dec bl
    jmp .ct_loop
    .ct_done:
    pop ax
    ret
    
; ---- Hilfen ---------------------------------------------------
MAXLEN equ 63

; Zeigt "Open error AX=xxxx" (bx enthält Fehlercode)
print_err_ax_bx:
    push ax
    push cx
    push dx
    mov  dx, PTR16(msgErr)
    mov  ah, 0x09
    int  0x21
    mov  ax, bx
    call print_ax_hex
    mov  dx, PTR16(crlf)
    mov  ah, 0x09
    int  0x21
    pop  dx
    pop  cx
    pop  ax
    ret

; AX als 4 hex-Zeichen ausgeben
print_ax_hex:
    push ax
    push bx
    push cx
    push dx
    mov  bx, ax
    mov  cx, 4
    .hexloop:
    rol  bx, 4
    mov  al, bl
    and  al, 0x0F
    add  al, '0'
    cmp  al, '9'
    jbe  .put
    add  al, 7
    .put:
    mov  dl, al
    mov  ah, 0x02
    int  0x21
    loop .hexloop
    pop  dx
    pop  cx
    pop  bx
    pop  ax
    ret

; ------------------------------------------------------------
; Hilfsroutine: ein Zeichen an aktuelles arg_str anhängen,
;               maximal 63 Nutzzeichen. Bei Overflow werden
;               zusätzliche Zeichen bis zum nächsten Separator
;               verworfen (wir schreiben einfach nicht mehr).
; IN:
;   AL = Zeichen
;   DI = Schreibzeiger (zeigt immer auf nächste freie Stelle)
;   CX = aktuelle Länge (0..63)
; OUT:
;   DI/CX aktualisiert
; Zerstört: nichts weiter (AX benutzt)
; ------------------------------------------------------------
put_char_maybe:
    cmp     cx, 63
    jae     .skip_write
    stosb                   ; [DI] = AL, DI++
    inc     cx
    ret
.skip_write:
    ; Zeichen verwerfen (nichts schreiben)
    ret

; DS:SI -> ASCIIZ
print_z0:
    .loop:
    lodsb
    test    al, al
    jz      .done
    mov     dl, al
    mov     ah, 02h
    SysCall
    jmp     .loop
    .done:
    ret

; -----------------------------------------------------------------------------
; \brief include DOS 16-bit stdlib function's ...
; -----------------------------------------------------------------------------
%include 'CommandLineArg.asm'       ; get command line arguments
%include 'ConsoleCursor.asm'        ; set the teletype video text cursor
%include 'ErrorCodes.asm'           ; get last error
%include 'InitConsole.asm'          ; initialize the DOS console
%include 'Int16ToStr.asm'           ; convert integer number to string
%include 'PutStrColor.asm'          ; put colored text onto the DOS screen
%include 'ReadLn16.asm'             ; read a line of text
%include 'ScreenClear.asm'          ; clear the screen
%include 'Str16Len.asm'             ; get the length of a string
%include 'StrCompare.asm'           ; string compare
%include 'StrCopy.asm'              ; copy a string

code16_end:
