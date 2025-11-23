;---------------------------------------------------
; \file  stdlib.inc
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
;---------------------------------------------------
%if DOS_MODE == 64
; -------------------------------------------------------------------
; \brief initialize the application ...
; -------------------------------------------------------------------
; --- Prolog ---
init_app:
    FUNC_ENTER
    
    mov      ecx, DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
    CALL_IAT SetProcessDpiAwarenessContext
    
    FUNC_LEAVE

; -------------------------------------------------------------------
; \brief init_console - initialize a text console under the Windows
;        gui desktop.
; \param nothing
; -------------------------------------------------------------------
; --- Prolog ---
init_console:
    FUNC_ENTER

    ; --- Konsole öffnen ---
    CALL_IAT AllocConsole
    GET_CON_O_HANDLE r12

    mov      rcx, r12
    lea      rdx, [rel mode_out]
    CALL_IAT GetConsoleMode              ; mode_out
    
    mov     eax, [rel mode_out]          ; Wert laden (NICHT die Adresse!)
    or      eax, ENABLE_VIRTUAL_TERMINAL_PROCESSING
    or      eax, DISABLE_NEWLINE_AUTO_RETURN     ; optional
    mov     edx, eax                     ; SetConsoleMode(hOut, newMode)
    mov     rcx, r12
    CALL_IAT SetConsoleMode

    ; --- INPUT: VT-Input optional aktivieren ---
    ; hIn besorgen (falls nicht schon vorhanden)
    GET_CON_I_HANDLE r13                 ; r13 = hIn   (oder mov ecx, STD_INPUT_HANDLE / GetStdHandle)

    mov     rcx, r13
    lea     rdx, [rel mode_in]
    CALL_IAT GetConsoleMode
    
    ; RCX=hOut, RDX=packed COORD
    mov      rcx, r12
    mov      edx, (25 << 16) | 80
    CALL_IAT SetConsoleScreenBufferSize
    
    ; RCX=hOut, RDX=TRUE, R8=&Rect
    mov      rcx, r12
    mov      edx, 1
    mov      r8,  IMAGE_BASE
    add      r8,  RVA_DATA(Rect80x25)
    CALL_IAT SetConsoleWindowInfo
    
    ; old mode holen
    mov  rcx, [hIn]
    lea  rdx, [rel tmpConsoleMode]
    CALL_IAT GetConsoleMode
    mov  eax, [rel tmpConsoleMode]

    or   eax, ENABLE_PROCESSED_INPUT             | \
              ENABLE_EXTENDED_FLAGS              | \
              ENABLE_VIRTUAL_TERMINAL_PROCESSING | \
              DISABLE_NEWLINE_AUTO_RETURN
    and  eax, ~(ENABLE_LINE_INPUT | ENABLE_ECHO_INPUT | ENABLE_QUICK_EDIT_MODE)

    mov  edx, eax
    mov  rcx, [hIn]
    CALL_IAT SetConsoleMode

    CALL_IAT GetConsoleWindow
    mov      rbx, rax                   ; rbx = hwnd
    test     rax, rax
    jz       .done                      ; no console available
    ; HMENU m = GetSystemMenu(h, FALSE);
    mov      rcx, rbx                   ; hWnd
    xor      edx, edx                   ; FALSE
    CALL_IAT GetSystemMenu
    test     rax, rax
    jz       .done
    mov      rdi, rax                   ; rdi = HMENU
    ; EnableMenuItem(m, SC_CLOSE, MF_BYCOMMAND | MF_GRAYED);
    mov      rcx, rdi                   ; HMENU
    mov      edx, SC_CLOSE              ; uIDEnableItem
    mov      r8d, MF_BYCOMMAND | MF_GRAYED
    CALL_IAT EnableMenuItem
    ; Neuzeichnen der Titelleiste/Buttons
    mov      rcx, rbx
    CALL_IAT DrawMenuBar
    .after_menu:
    .done:
    
    ; default color for the console:
    mov ax, ATTR_BG_BLACK
    mov [_cA_console_bg], ax
    ;
    mov ax, ATTR_FG_LIGHT_YELLOW
    mov [_cA_console_fg], ax
    
; --- Epilog ---
    FUNC_LEAVE

; -------------------------------------------------------------------
; UTF-8 -> UTF-16
; -------------------------------------------------------------------
ascii_to_utf8:
    ;FUNC_ENTER
    push    rbx
    
    ; Eingaben sichern
    mov     r10, rcx        ; save src (UTF-8)
    mov     r11, rdx        ; save dst (LPWSTR)
    
    ; MultiByteToWideChar(CodePage=65001, Flags=0, src, -1, dst, cch)
    mov     ecx, 65001      ; CodePage = CP_UTF8
    xor     edx, edx        ; dwFlags = 0           (Achtung: edx nullt rdx!)
    mov     r8,  r10        ; lpMultiByteStr = saved src
    mov     r9d, -1         ; cbMultiByte = -1 (NUL-terminiert)
    
    sub     rsp, 40               ; shadow space
    mov     [rsp+24], r11         ; lpWideCharStr
    mov     dword [rsp+32], 256   ; cchWideChar
    
    CALL_IAT MultiByteToWideChar
    
    add     rsp, 40
    pop     rbx
    ret
    ;FUNC_LEAVE
    
; -------------------------------------------------------------------
; \brief routine to handle win32api GetLastError ...
; -------------------------------------------------------------------
HandleLastError:
    ; --- Prolog ---
    FUNC_ENTER 64
    
    ; FormatMessageW(FM_FLAGS, NULL, err, LANGID_DEFAULT, (LPWSTR)&pMsg, 0, NULL)
    mov     ecx, FM_FLAGS                       ; rcx = dwFlags
    xor     edx, edx                            ; rdx = lpSource = NULL
    mov     r8d, eax                            ; 3th dwMessageId
    mov     r9d, LANGID_DEFAULT                 ; 4th dwLanguageId
    
    AddShadow (32 + (3 * 8) + 8)                ; 32 shadow + 3 stack-args (5th,6th,7th) + 8 padding
    mov     rax, IMAGE_BASE
    add     rax, RVA_DATA(pMsg)                 ; rax = &pmsg
    mov     [rsp+32], rax                       ; 5th: lpBuffer (as LPWSTR*) because of ALLOCATE_BUFFER
    mov     dword [rsp+40], 0                   ; 6th: nSize = 0 (Min-Größe)
    mov     qword [rsp+48], 0                   ; 7th: Arguments = NULL

    ;AddShadow
    call_FormatMessageW
    DelShadow (32 + (3 * 8) + 8)
    test    eax, eax
    jz      .no_text                                    ; 0 = Fehler (kein Text verfügbar)

    ; MessageBoxW(NULL, pMsg, titleW, MB_ICONERROR)
    xor     ecx, ecx
    mov     rdx, IMAGE_BASE
    add     rdx, RVA_DATA(pMsg)                 ; lpText = pMsg (LPWSTR)
    GETEXT  r8 , ErrTitleW
    mov     r9d, MB_ICONERROR
    call_MessageBoxW

    ; LocalFree(pMsg)
    mov     rcx, IMAGE_BASE
    add     rcx, RVA_DATA(pMsg)
    mov     rcx, [rcx]
    call_LocalFree

    jmp     .done
    
.no_text:
    call HandleLastErrorHexCode
.done:
    FUNC_LEAVE 64

; -------------------------------------------------------------------
; rcx = BYTE buffer[20]
; edx = DWORD number
; return:
; rax = BYTE * start
; -------------------------------------------------------------------
u32_to_dec:
	mov     eax, edx        ; number
	lea     r8, [rcx + 20]  ; end of buffer
	dec     r8
	mov     byte [r8], 0    ; null terminate
    .loop:
    mov     rcx, 10
    mov     rdx, 0
    div     rcx
    add     dl, '0'         ; convert remainder to ascii
    dec     r8
    mov     byte [r8], dl
    cmp     rax, 0
    ja      .loop
    mov     rax, r8         ; pointer to start of number
    ret
    
; -------------------------------------------------------------------
; \brief  concatenate two ANSI string's to a single one string dest-
;         ination. The dst buffer must be big enough !
;
; \desc   int concat_ansi(char *dst, const char *s1, const char *s2)
;
; \param  RCX -> string buffer = dst
;
; \param  RDX -> string = src1
; \param  R8  -> string = src2
;
; \return RAX -> bool   = 1 if 0x00 found, else 0
; -------------------------------------------------------------------
concat_ansi:
    ; -----------------------------------------
    ; iterate over first string
    ; -----------------------------------------
    .loop_s1:
    mov     al, [rdx]   ; get character on current src1 position
    test    al, al      ; 0x00 found ?
    jz      .loop_s2    ; yes, then exit .loop
    
    mov     [rcx], al   ; move al character to dst buffer
    inc     rdx         ; increment position of src1 buffer
    inc     rcx         ; ... of dst buffer
    jmp     .loop_s1    ; next character
    
    ; -----------------------------------------
    ; iterate over second string
    ; -----------------------------------------
    .loop_s2:
    mov     al, [r8]    ; get character on current src2 position
    test    al, al      ; 0x00 found ?
    jz      .finish     ; yes, then exit .loop
    
    mov     [rcx], al   ; move al character to dst buffer
    inc     r8          ; increment position of src2 buffer
    inc     rcx         ; ... of dst buffer
    jmp     .loop_s2    ; next char
    
    .finish:
    xor     eax, eax    ; AL = 0
    mov     [rcx], al   ; null-terminator
    mov     eax, 1      ; return true, found end
    ret
    
GET_STR_LEN:
    xor     eax, eax            ; RAX = 0 (counter)
    .loop:
    mov     dl, byte [rcx+rax]  ; get character on current src1 position
    test    dl, dl              ; 0x00 found ?
    jz      .loop_end           ; yes, then exit .loop
    inc     rax                 ; ... of dst buffer
    jmp     .loop               ; next character
    .loop_end:
    ret

HandleLastErrorHexCode:
    ; --- Prolog ---
    FUNC_ENTER 64
    
    ; -----------------------------------------------------------
    ; write: work around for: mov [rel last_error], eax
    ;
    ; 1. load abs Virtual Address into register
    ; 2. access through this register
    ; -----------------------------------------------------------
    mov   rdx, IMAGE_BASE + RVA_DATA(last_error)
    mov   dword [rdx], eax
    
;    mov   rcx, IMAGE_BASE + RVA_DATA(_cW_wbuf)
;    mov   rdx, IMAGE_BASE + RVA_DATA(_cW_fmtW)
    
    ; wsprintfW(wbuf, fmtW, err, err)
    ; (variadisch: AL = 0, Shadow Space 32B)
    mov     r8d, ecx                     ; 1. varg
    mov     r9d, edx                     ; 2. varg
    xor     eax, eax                     ; AL=0 (keine XMM-Args)
    
    call_wsprintfW
        
    ; MessageBoxW(NULL, wbuf, titleW, MB_ICONERROR)
    xor     ecx, ecx
;    mov     rdx, IMAGE_BASE + RVA_DATA(_cW_wbuf)
;    mov     r8,  IMAGE_BASE + RVA_DATA(_cW_ErrTitleW)
    mov     r9d, 0x10                    ; MB_ICONERROR
    
    call_MessageBoxW

    FUNC_LEAVE 64

; -------------------------------------------------------------------
; int utf8_to_cp1252_char(const uint8_t* src, uint8_t* dst)
; RCX = src (UTF-8), RDX = dst (CP1252)
; Rückgabe:
;   RAX = Anzahl gelesener UTF-8-Bytes (1..2), 0 bei NUL
;   AL  = geschriebenes CP1252-Byte
;   CF  = 1, wenn unmappbar -> '?' geschrieben
; Hinweis: mapped werden ASCII und: äöüÄÖÜß
; -------------------------------------------------------------------
utf8_to_cp1252_char:
    ;FUNC_ENTER 64
    push    rbx

    mov     bl, [rcx]
    test    bl, bl
    jz      .nul               ; Stringende

    ; ASCII (00..7F) 1:1
    cmp     bl, 0x7F
    jbe     .ascii

    ; --- 2-Byte UTF-8, die mit C3 beginnen (äöüÄÖÜß) ---
    cmp     bl, 0xC3
    jne     .unmap
    mov     bh, [rcx+1]        ; zweites Byte
    ; Tabelle:
    ; C3 84 -> Ä (C4)
    ; C3 96 -> Ö (D6)
    ; C3 9C -> Ü (DC)
    ; C3 A4 -> ä (E4)
    ; C3 B6 -> ö (F6)
    ; C3 BC -> ü (FC)
    ; C3 9F -> ß (DF)

    ; upper-case
    cmp     bh, 0x84
    je      .emit_C4
    cmp     bh, 0x96
    je      .emit_D6
    cmp     bh, 0x9C
    je      .emit_DC
    ; lower-case
    cmp     bh, 0xA4
    je      .emit_E4
    cmp     bh, 0xB6
    je      .emit_F6
    cmp     bh, 0xBC
    je      .emit_FC
    cmp     bh, 0x9F
    je      .emit_DF

    jmp     .unmap

    .ascii:
    mov     [rdx], bl
    mov     al, bl
    mov     rax, 1
    clc
    pop     rbx
    FUNC_LEAVE 64

    .emit_C4:   mov byte [rdx], 0xC4  ; Ä
                mov al, 0xC4
                mov rax, 2
                clc
                pop rbx
                FUNC_LEAVE 64
    .emit_D6:   mov byte [rdx], 0xD6  ; Ö
                mov al, 0xD6
                mov rax, 2
                clc
                pop rbx
                FUNC_LEAVE 64
    .emit_DC:   mov byte [rdx], 0xDC  ; Ü
                mov al, 0xDC
                mov rax, 2
                clc
                pop rbx
                FUNC_LEAVE 64
    .emit_E4:   mov byte [rdx], 0xE4  ; ä
                mov al, 0xE4
                mov rax, 2
                clc
                pop rbx
                FUNC_LEAVE 64
    .emit_F6:   mov byte [rdx], 0xF6  ; ö
                mov al, 0xF6
                mov rax, 2
                clc
                pop rbx
                FUNC_LEAVE 64
    .emit_FC:   mov byte [rdx], 0xFC  ; ü
                mov al, 0xFC
                mov rax, 2
                clc
                pop rbx
                FUNC_LEAVE 64
    .emit_DF:   mov byte [rdx], 0xDF  ; ß
                mov al, 0xDF
                mov rax, 2
                clc
                pop rbx
                FUNC_LEAVE 64
    .unmap:
    ; Unbekannt -> '?'
    mov     byte [rdx], '?'
    mov     al, '?'
    stc
    ; grob: falls Startbyte >= C2 und < E0, konsumieren wir 2 Bytes,
    ; sonst 1 (damit der Aufrufer weiterkommt).
    mov     rax, 1
    cmp     bl, 0xC2
    jb      .ret_unmap
    cmp     bl, 0xE0
    jae     .ret_unmap
    mov     rax, 2
    .ret_unmap:
    pop     rbx
    FUNC_LEAVE 64

    .nul:
    xor     eax, eax            ; RAX=0, AL=0
    clc
    .exit:
    pop     rbx
    FUNC_LEAVE 64
; -------------------------------------------------------------------
; size_t utf8_to_cp1252(const uint8_t* src, uint8_t* dst)
; RCX=src, RDX=dst -> RAX = geschriebene Bytes, dst ist NUL-terminiert
; -------------------------------------------------------------------
utf8_to_cp1252:
    ;FUNC_ENTER 64
    push    rsi
    push    rdi
    mov     rsi, rcx         ; s = src
    mov     rdi, rdx         ; d = dst
    xor     rax, rax         ; count = 0
    
    .next:
    movzx   eax, byte [rsi]  ; RCX bleibt unverändert
    jmp .done
    test    eax, eax
    jz      .done

    ; pro Zeichen mappen
    mov     rcx, rsi
    mov     rdx, rdi
    call    utf8_to_cp1252_char
    
    ; RAX = konsumierte UTF-8-Bytes
    add     rsi, rax
    inc     rdi
    inc     rax              ; count++
    jmp     .next
    .done:
    ;push    rcx
    ;ShowMessageW titleW,capW
    ;pop     rcx
    mov     byte [rdi], 0
    pop     rdi
    pop     rsi
    ret
    FUNC_LEAVE 64
%endif
