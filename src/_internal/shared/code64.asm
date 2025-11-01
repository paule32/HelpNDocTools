bits 64

_start:
    mov rbp,rsp
    and rsp,-16
    sub rsp,32

    AddShadow
    call PASCALMAIN
    DelShadow

    ; hInstance holen
    xor     ecx, ecx
    CALL_IAT GetModuleHandleW         ; rcx = NULL
    mov     r14, rax                  ; HINSTANCE in callee-saved Reg

    ; ----- WNDCLASSEXW auf dem Stack füllen -----
    ; Layout (Win64, 80 Bytes):
    ;  0 cbSize         (4) 
    ;  4 style          (4)  1
    ;  8 lpfnWndProc    (8)  2
    ; 16 cbClsExtra     (4)
    ; 20 cbWndExtra     (4)  3
    ; 24 hInstance      (8)  4
    ; 32 hIcon          (8)  5
    ; 40 hCursor        (8)  6
    ; 48 hbrBackground  (8)  7
    ; 56 lpszMenuName   (8)  8 
    ; 64 lpszClassName  (8)  9
    ; 72 hIconSm        (8) 10
    AddShadow (8 * 10)                  ; size of WNDCLASSEXW
    mov     rdi, rsp                    ; rdi = &wc

    ; Zero init
    cld                                 ; (sicherstellen, dass DF=0 ist)
    xor     eax, eax                    ; rax = 0
    mov     ecx, 10                     ; 10 qwords
    rep     stosq
;.fillwc:
;    mov     [rdi + ((rcx*8) - 8)], rax
;    loop    .fillwc

    mov     dword [rdi + 0], 80                           ; cbSize
    mov     dword [rdi + 4], CS_HREDRAW | CS_VREDRAW      ; style

    ; lpfnWndProc = &WndProc (absolute VA)
    mov     rax, IMAGE_BASE
    add     rax, RVA_TEXT(WndProc)
    mov     [rdi + 8], rax

    ; cbClsExtra/cbWndExtra = 0
    ;mov     dword [rdi + 16], 0
    ;mov     dword [rdi + 20], 0

    ; hInstance
    mov     [rdi + 24], r14

    ; hIcon = NULL
    ;mov     qword [rdi + 32], 0

    ; hCursor = LoadCursorW(NULL, IDC_ARROW)
    ; --- Aufruf: Systemcursor laden
    ; (hInstance   = NULL,
    ; lpCursorName = MAKEINTRESOURCEW(IDC_ARROW)) ---
    xor     ecx, ecx
    mov     edx, IDC_ARROW
    sub     rsp, 32
    ;call_LoadCursorW
    mov     rax, IMAGE_BASE
    add     rax, RVA_IDATA(IAT_win32_LoadCursorW)
    call    [rax]
    add     rsp, 32
    mov     [rdi + 40], rax

    ; hbrBackground = (HBRUSH)(COLOR_WINDOW+1)
    mov     qword [rdi + 48], COLOR_WINDOW + 1

    ; lpszMenuName = NULL
    mov     qword [rdi + 56], 0

    ; lpszClassName = &winclassW (UTF-16)
    mov     rax, IMAGE_BASE
    add     rax, RVA_DATA(winclassW)
    mov     [rdi + 64], rax

    ; hIconSm = NULL
    ;mov     qword [rdi + 72], 0

    ; RegisterClassExW(&wc)
    mov     rcx, rdi
    sub     rsp, 32
    ;CALL_IAT RegisterClassExW
    mov     rax, IMAGE_BASE
    add     rax, RVA_IDATA(IAT_win32_RegisterClassExW)
    call    [rax]
    add     rsp, 32
    test    eax, eax
    jz      .reg_fail

.class_ok:
;ShowMessageW ClassOkW,capW
    ; ------------------------------------------------------------------------
    ; CreateWindowExW(
    ;   0, class, title, WS_OVERLAPPEDWINDOW,
    ;   CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT, CW_USEDEFAULT,
    ;   NULL, NULL, hInstance, NULL)
    ; ------------------------------------------------------------------------
    ;AddShadow 32 + 8*8                                  ; 32 Shadow + 8 Args
    xor     ecx, ecx                                    ;  1. dwExStyle = 0
    mov     rdx, IMAGE_BASE
    add     rdx, RVA_DATA(winclassW)                    ;  2. lpClassName
    mov     r8,  IMAGE_BASE
    add     r8,  RVA_DATA(titleW)                       ;  3. lpWindowName
    mov     r9d, WS_OVERLAPPEDWINDOW                    ;  4. dwStyle

    ; 5.–12. Parameter auf den Stack (in der Reihenfolge!)
    ;AddShadow 32 + 8*8
    sub     rsp, 32 + 8*8
    mov     dword [rsp+32], 100 ;CW_USEDEFAULT             ;  5. X
    mov     dword [rsp+40], 100 ; CW_USEDEFAULT             ;  6. Y
    mov     dword [rsp+48], 329 ;CW_USEDEFAULT             ;  7. nWidth
    mov     dword [rsp+56], 200 ;CW_USEDEFAULT             ;  8, nHeight
    mov     qword [rsp+64], 0                         ;  9. hWndParent
    mov     qword [rsp+72], 0                         ; 10. hMenu
    mov     [rsp+80], r14                             ; 11. hInstance
    mov     qword [rsp+88], 0                         ; 12. lpParam
    
    mov     rax, IMAGE_BASE
    add     rax, RVA_IDATA(IAT_win32_CreateWindowExW)
    call    [rax]
    
    add     rsp, 32 + 8*8
    
    test    rax, rax
    jz      .cw_fail                  ; <--- here jump
    
    mov    rsi, rax
    
; Show / Update
mov     rcx, rsi
mov     edx, 5                            ; SW_SHOW
sub     rsp, 32
mov     rax, IMAGE_BASE
add     rax, RVA_IDATA(IAT_win32_ShowWindow)
call    [rax]
add     rsp, 32

mov     rcx, rsi
sub     rsp, 32
mov     rax, IMAGE_BASE
add     rax, RVA_IDATA(IAT_win32_UpdateWindow)
call    [rax]
add     rsp, 32

; --- Message loop (MSG=48B) ---
sub     rsp, 48
mov     rbx, rsp
.msg:
    mov     rcx, rbx
    xor     edx, edx
    xor     r8d, r8d
    xor     r9d, r9d
    sub     rsp, 32
    mov     rax, IMAGE_BASE
    add     rax, RVA_IDATA(IAT_win32_GetMessageW)
    call    [rax]
    add     rsp, 32
    test    eax, eax
    jz      .quit

    mov     rcx, rbx
    sub     rsp, 32
    mov     rax, IMAGE_BASE
    add     rax, RVA_IDATA(IAT_win32_TranslateMessage)
    call    [rax]
    add     rsp, 32

    mov     rcx, rbx
    sub     rsp, 32
    mov     rax, IMAGE_BASE
    add     rax, RVA_IDATA(IAT_win32_DispatchMessageW)
    call    [rax]
    add     rsp, 32
    jmp     .msg
.quit:
add     rsp, 48

; Aufräumen WNDCLASSEXW-Reserve
add     rsp, 80
jmp     .ok

.reg_fail:
    ; GetLastError + anzeigen (du hast die Routine schon)
    sub     rsp,32
    mov     rax, IMAGE_BASE
    add     rax, RVA_IDATA(IAT_win32_GetLastError)
    call    [rax]
    add     rsp,32
    ; eax -> deine Fehleranzeige
    add     rsp, 80
    jmp     .done
    
.cw_fail:
    sub     rsp,32
    mov     rax, IMAGE_BASE
    add     rax, RVA_IDATA(IAT_win32_GetLastError)
    call    [rax]
    add     rsp,32
    ; eax -> deine Fehleranzeige
    add     rsp, 80
    jmp     .done
    
.ok:
.done:
    call_ExitProcess 2
