HandleLastError:
    ; --- Prolog ---
    push    rbp
    mov     rbp, rsp
    sub     rsp, 64
    
    call_GetLastError
    
    mov     r8d, eax                      ; r8d = dwMessageId (3. Param)
    mov     r9d, LANGID_DEFAULT           ; r9d = dwLanguageId (4. Param)
    
    ; FormatMessageW(FM_FLAGS, NULL, err, LANGID_DEFAULT, (LPWSTR)&pMsg, 0, NULL)
    mov     ecx, FM_FLAGS                       ; rcx = dwFlags
    xor     edx, edx                            ; rdx = lpSource = NULL
    AddShadow 56                                ; 32 shadow + 3 stack-args (5th,6th,7th)
    mov     rdx, IMAGE_BASE
    add     rdx, RVA_DATA(pMsg)
    mov     rdx, [rdx]
    mov     [rsp+32], rax                       ; 5th: lpBuffer (as LPWSTR*) because of ALLOCATE_BUFFER
    mov     dword [rsp+40], 0                   ; 6th: nSize = 0 (Min-Größe)
    mov     qword [rsp+48], 0                   ; 7th: Arguments = NULL
    call_FormatMessageW
    DelShadow 56
    ;test    eax, eax
    ;jz      .no_text                                    ; 0 = Fehler (kein Text verfügbar)

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
call_AllocConsole ok_1, pdone

; --- WriteConsoleA(hOut, fmtHello, hello_len, NULL, NULL) ---
ok_1:
call_ShowMessageW ok_2, pdone, text11W, capW, 0
ok_2:
call_GetStdHandle ok_3, pdone, STD_OUTPUT_HANDLE
ok_3:
call_ShowMessageW ok_4, pdone, text22W, capW, 0

ok_4:
call_ShowMessageW ok_5, pdone, text33W, capW, 0
ok_5:
mov     rcx, r12                      ; 1. Arg: HANDLE hConsoleOutput
;lea     rdx, [rel fmtHello]           ; 2. Arg: LPCVOID lpBuffer
;mov     r8d, [rel fmtHello_length]    ; 3. Arg: DWORD nNumberOfCharsToWrite
;xor     r9d, r9d                      ; lpNumberOfCharsWritten = NULL

;AddShadow 40
;mov     qword [rsp+32], 0             ; 5. Arg: LPVOID lpReserved = NULL
;CALL_IAT WriteConsoleA
;DelShadow 40
call_ShowMessageW pdone, pdone, text44W, capW, 0
; --- Epilog ---
pdone:
add     rsp, 64
pop     rbp
ret
