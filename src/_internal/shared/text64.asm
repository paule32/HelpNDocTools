PASCALMAIN:
; -------------------------------------------------------------------
; 64 Bytes reservieren:
;  - 32 B Shadow Space (Pflicht als Caller vor jedem call)
;  - 32 B "lokal" (hier ungenutzt, dient auch dem Alignment)
; Nach push rbp ist rsp 16-Byte aligned; 64 hält das Alignment.
; -------------------------------------------------------------------
    FUNC_ENTER 64

    ; --- Konsole öffnen ---
    call init_console
    
    call_User_Write .error, cap2A
    .error:
    
    mov     ecx, STD_OUTPUT_HANDLE
    CALL_IAT    GetStdHandle
    mov     r12, rax         ; hOut

    mov     ecx, STD_INPUT_HANDLE
    CALL_IAT    GetStdHandle
    mov     r13, rax         ; hIn

    ; prompt ausgeben
    mov     rcx, r12
    mov     rdx, IMAGE_BASE
    add     rdx, RVA_DATA(prompt)
    mov     r8d, 9
    xor     r9d, r9d
    mov     qword [rsp+32], 0
    CALL_IAT    WriteConsoleA

    ; ReadConsoleA(hIn, inbuf, maxChars, &read, NULL)
    mov      rcx, r13
    mov      rdx, IMAGE_BASE
    add      rdx, RVA_DATA(src)
    mov      r8d, 127            ; maxChars (Reserviere 1 Byte für NUL)
    mov      r9,  IMAGE_BASE
    add      r9,  RVA_DATA(read)
    sub      rsp, 40
    xor      rax, rax           ; lpReserved = NULL (über Shadow Space)
    mov      [rsp+32], rax
    CALL_IAT ReadConsoleW
    add      rsp, 40
    
    GETDATA  rcx, src
    GETDATA  rdx, dst

    call utf8_to_cp1252

    ShowMessageW dst,src
; --- Exit ---
    .exit:
    xor     ecx, ecx
    CALL_IAT ExitProcess
    
    FUNC_LEAVE 64
