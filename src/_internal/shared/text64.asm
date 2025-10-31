HandleLastError:
    ; --- Prolog ---
    push    rbp
    mov     rbp, rsp
    sub     rsp, 64
    
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
ShowMessageW ShowLast2W,capW
    ; MessageBoxW(NULL, pMsg, titleW, MB_ICONERROR)
    xor     ecx, ecx
    mov     rdx, IMAGE_BASE
    add     rdx, RVA_DATA(pMsg)                 ; lpText = pMsg (LPWSTR)
    mov     r8,  IMAGE_BASE
    add     r8,  RVA_DATA(ErrTitleW)
    mov     r9d, 0x10                           ; MB_ICONERROR
    call_MessageBoxW

    ; LocalFree(pMsg)
    mov     rcx, IMAGE_BASE
    add     rcx, RVA_DATA(pMsg)
    mov     rcx, [rcx]
    call_LocalFree

    jmp     .done
    
.no_text:
ShowMessageW ShowLastW,capW
    call HandleLastErrorHexCode
.done:
    add     rsp, 64
    pop     rbp
    ret

HandleLastErrorHexCode:
    ; --- Prolog ---
    push    rbp
    mov     rbp, rsp
    sub     rsp, 64
    
    ; -----------------------------------------------------------
    ; write: work around for: mov [rel last_error], eax
    ;
    ; 1. load abs Virtual Address into register
    ; 2. access through this register
    ; -----------------------------------------------------------
    mov   rdx, IMAGE_BASE + RVA_DATA(last_error)
    mov   dword [rdx], eax
    
    mov   rcx, IMAGE_BASE + RVA_DATA(wbuf)
    mov   rdx, IMAGE_BASE + RVA_DATA(fmtW)
    
    ; wsprintfW(wbuf, fmtW, err, err)
    ; (variadisch: AL = 0, Shadow Space 32B)
    mov     r8d, ecx                     ; 1. varg
    mov     r9d, edx                     ; 2. varg
    xor     eax, eax                     ; AL=0 (keine XMM-Args)
    
    call_wsprintfW
        
    ; MessageBoxW(NULL, wbuf, titleW, MB_ICONERROR)
    xor     ecx, ecx
    mov     rdx, IMAGE_BASE + RVA_DATA(wbuf)
    mov     r8,  IMAGE_BASE + RVA_DATA(ErrTitleW)
    mov     r9d, 0x10                    ; MB_ICONERROR
    
    call_MessageBoxW
    
    add     rsp, 64
    pop     rbp
    ret

PASCALMAIN:

; --- Prolog ---
print_line_1:
    push    rbp
    mov     rbp, rsp

; -------------------------------------------------------------------
; 64 Bytes reservieren:
;  - 32 B Shadow Space (Pflicht als Caller vor jedem call)
;  - 32 B "lokal" (hier ungenutzt, dient auch dem Alignment)
; Nach push rbp ist rsp 16-Byte aligned; 64 hält das Alignment.
; -------------------------------------------------------------------
    sub     rsp, 64

    ; --- Konsole öffnen ---
    call_AllocConsole ok_1, prg_done

    ; --- WriteConsoleA(hOut, fmtHello, hello_len, NULL, NULL) ---
ok_1:
    call_GetStdHandle ok_2, prg_done, STD_OUTPUT_HANDLE
ok_2:
    mov     rcx, r12                       ; 1. Arg: HANDLE hConsoleOutput
    mov     rdx, IMAGE_BASE
    add     rdx, RVA_DATA(cap2A)           ; 2. Arg: LPCVOID lpBuffer
    mov     r8, IMAGE_BASE
    add     r8, RVA_DATA(cap2A_length)     ; 3. Arg: DWORD nNumberOfCharsToWrite
    mov     r8d, cap2A_length
    xor     r9d, r9d                       ; lpNumberOfCharsWritten = NULL

    AddShadow 32 + 8
    mov     qword [rsp+32], 0              ; 5. Arg: LPVOID lpReserved = NULL
    call_WriteConsoleA
    DelShadow 32 + 8

    ; --- Epilog ---
prg_done:
    add     rsp, 64
    pop     rbp
    ret
