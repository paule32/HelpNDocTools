; -----------------------------------------------------------------------------
; \file  winfunc.inc
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

; -----------------------------------------------------------------------------
; \brief allocate/open a text console window under Windows 11 desktop.
; \param ok  -> label
; \param err -> label
; \since 1.0
;
; \return bool - 0 no Error; else Error
; -----------------------------------------------------------------------------
%macro call_AllocConsole 2
    CALL_IAT AllocConsole
%if %0 == 2
    CHECK_NZ %1, %2
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief
; -----------------------------------------------------------------------------
%macro call_ExitProcess 0-1
%if %0 == 1
    mov rax, %1
%else
    mov rax, 0
%endif
    CALL_IAT ExitProcess
%endmacro

; -----------------------------------------------------------------------------
; \brief helper function to save source code space for win32api FormatMessageW.
; -----------------------------------------------------------------------------
%macro call_FormatMessageW 0
    CALL_IAT FormatMessageW
%endmacro

; -----------------------------------------------------------------------------
; \brief
; -----------------------------------------------------------------------------
;macro call_GetConsoleScreenBufferInfo
;endmacro

; -----------------------------------------------------------------------------
; \brief  this macro call the win32api function GetLastError.
; \param  nothing
; \return ExitCode - int
; -----------------------------------------------------------------------------
%macro call_GetLastError 0
    CALL_IAT GetLastError
    test rax, rax
    jnz  %%ok
    AddShadow
    call HandleLastError
    DelShadow
%%ok:
;ShowMessageW ShowLastW,capW
%endmacro

; -----------------------------------------------------------------------------
; \brief  get the standard output device.
; \param  ok     -> label
; \param  error  -> label
; \param  handle -> int
; \see    AllocConsole
; \since  1.0
; \return ?
; -----------------------------------------------------------------------------
%macro call_GetStdHandle 3
    mov ecx, %3
    CALL_IAT GetStdHandle
    cmp   rax, -1     ; INVALID_HANDLE_VALUE ?
    je    %%error     ; yes -> error
    test  rax, rax    ; 0 ?
    jz    %%error     ; yes -> error
    ;
    mov   r12, rax    ; valid handle in rax
    jmp   %%ok
%%error:
    call HandleLastError
    jmp  %2
%%ok:
    jmp  %1
%endmacro

%macro call_LoadCursorW 0
    CALL_IAT LoadCursorW
    ;ShowMessageW ShowHelloW,capW
    ;call_GetLastError
%endmacro

%macro call_LocalFree 0
    CALL_IAT MessageBoxW
%endmacro

; -----------------------------------------------------------------------------
; \brief helper macro to shorten code, and call the win32api MessageBox W
; -----------------------------------------------------------------------------
%macro call_MessageBoxW 0
    CALL_IAT MessageBoxW
%endmacro

; -----------------------------------------------------------------------------
; \brief helper macro to shorten code, and call the win32api function wsprintfW
; -----------------------------------------------------------------------------
%macro call_wsprintfW 0
    CALL_IAT wsprintfW
%endmacro

%macro call_WriteConsoleA 0
    CALL_IAT WriteConsoleA
%endmacro

; -----------------------------------------------------------------------------
; \brief Write - display text on the Windows Console.
; \param 1 -> label -> on error
; \param 2 -> label -> text to display
; \param 3 -> label -> output handle; default is: STD_OUTPUT_HANDLE
; \see   AllocConsole
; \since 1.0
; -----------------------------------------------------------------------------
%macro call_User_Write 2-3
%if %0 == 2
    call_GetStdHandle %%ok, %1, STD_OUTPUT_HANDLE
%else
    call_GetStdHandle %%ok, %1, %3
%endif
%%ok:
    ; --- WriteConsoleA(hOut, fmtHello, hello_len, NULL, NULL) ---
    mov     rcx, r12                       ; 1. Arg: HANDLE hConsoleOutput
    mov     rdx, IMAGE_BASE
    add     rdx, RVA_DATA(%2)              ; 2. Arg: LPCVOID lpBuffer
    mov     r8d, %2_length                 ; 3. Arg: DWORD nNumberOfCharsToWrite
    xor     r9d, r9d                       ; lpNumberOfCharsWritten = NULL
    AddShadow 32 + 8
    mov     qword [rsp+32], 0              ; 5. Arg: LPVOID lpReserved = NULL
    call_WriteConsoleA
    DelShadow 32 + 8
%endmacro

; -----------------------------------------------------------------------------
; \brief read a string line in console window ...
; -----------------------------------------------------------------------------
%macro call_User_ReadLn 1
    call user_Console_ReadLn
%endmacro

; -----------------------------------------------------------------------------
%macro DefWindowProcW 0
    mov     rax, IMAGE_BASE + RVA_IDATA(IAT_win32_DefWindowProcW)
%endmacro

%macro IAT_CreateWindowExW 0
    mov     rax, IMAGE_BASE
    add     rax, RVA_IDATA(IAT_win32_CreateWindowExW)
    call    [rax]
%endmacro
; -----------------------------------------------------------------------------

; -----------------------------------------------------------------------------
; \brief  DispatchMessageW
; \since  1.0
; -----------------------------------------------------------------------------
%macro DispatchMessageW 0
    mov     rcx, rsi
    CALL_IAT DispatchMessageW
%endmacro

; -----------------------------------------------------------------------------
; \brief  ExitProcess terminate the given application thread.
; \since  1.0
; \param  exitcode -> integer
; \return exitcode -> rax
; -----------------------------------------------------------------------------
%macro ExitProcess 0-1 0
    nop
    ;AddShadow (32 + 16)           ; Shadow Space + 16 B Align
    mov     ecx,%1
    CALL_IAT ExitProcess
    ; no return
    ;DelShadow (32 + 16)
%endmacro

; -----------------------------------------------------------------------------
; \brief  GetLastError catches the last error that was occured during win32api
;         function call.
; \since  1.0
; \param  nothing
; \return ?
; -----------------------------------------------------------------------------
%macro GETLASTERROR 2
    test    eax, eax
    %1      %2
%endmacro

%macro GetLastError 0
    CALL_IAT GetLastError
%endmacro

; -----------------------------------------------------------------------------
; \brief  GetMessageW
; -----------------------------------------------------------------------------
%macro GetMessageW 0
    mov  rcx, rsi
    Zero edx
    Zero r8d
    Zero r9d
    CALL_IAT GetMessageW
%endmacro

; -----------------------------------------------------------------------------
; \brief  LoadCursorW
; \since  1.0
; \param  id - integer: resource id
; -----------------------------------------------------------------------------
%macro LoadCursorW 1
    Zero ecx
    mov  edx, %1
    CALL_IAT LoadCursorW
%endmacro

; -----------------------------------------------------------------------------
; \brief  MESSAGE is a style shortner for better read expierences ...
; -----------------------------------------------------------------------------
%macro MESSAGE 2
    cmp     edx, %1
    je      .%2
%endmacro

; -----------------------------------------------------------------------------
; \brief ShowMessageW display a wide string message on the desktop screen per
;        the wn32api.
; \since 1.0
; \see   ShowMessageA
;
; \param text_str  -> landet in rdx
; \param title_str -> landet in r8
;
; \param mb_flags  -> optional ( r9d ), default: 0 (MB_OK)
; -----------------------------------------------------------------------------
%macro ShowMessageW 2-3
    Zero    ecx                                     ; hWnd = NULL
    mov     rdx, (IMAGE_BASE + RVA_DATA(_cA_%1))    ; lpText
    mov     r8,  (IMAGE_BASE + RVA_DATA(_cA_%2))    ; lpCaption    
%if %0 == 2                                         ; %0 = argument count
    xor     r9d, r9d                                ; uType = MB_OK
%else
    mov     r9d, %3                                 ; uType = argument exists
%endif
    CALL_IAT MessageBoxW
%endmacro

; -----------------------------------------------------------------------------
; \brief ShowMessageA display a ansi string message on the desktop screen per
;        the wn32api.
; \since 1.0
; \see   ShowMessageW
;
; \param text_str  -> landet in rdx
; \param title_str -> landet in r8
;
; \param mb_flags  -> optional ( r9d ), default: 0 (MB_OK)
; -----------------------------------------------------------------------------
%macro ShowMessageA 2-3
    Zero    ecx
    mov     rdx, IMAGE_BASE + RVA_DATA(_cA_%1)  ; "MessageBoxW failed"
    mov     r8,  IMAGE_BASE + RVA_DATA(_cA_%2)  ; "User32"
%if %0 == 2                                     ; %0 = argument count
    xor     r9d, r9d                            ; uType = MB_OK
%else
    mov     r9d, %3                             ; uType = argument exists
%endif
    CALL_IAT MessageBoxA
%endmacro

; -----------------------------------------------------------------------------
; \brief  ShowWindow shows the window witht the hwnd id in r13.
; \since  1.0
; \param  hwnd -> HWND handle window
; \param  (optional) flag -> integer: default = SW_SHOWDEFAULT
; -----------------------------------------------------------------------------
%macro ShowWindow 1-2
    nop
    ;AddShadow (32 + 16)           ; Shadow Space + 16 B Align
    mov     rcx, %1
%if %0 == 2
    mov     edx, %2
%else
    mov     edx, SW_SHOWDEFAULT
%endif
    CALL_IAT ShowWindow
    ;DelShadow (32 + 16)
%endmacro

; -----------------------------------------------------------------------------
; \brief display a message box on top of the Windows 11 desktop.
; \param text   -> str
; \param title  -> str
; \param button -> int
; -----------------------------------------------------------------------------
%macro call_ShowMessageW 5
    ShowMessageW %3, %4, %5
    CHECK_NZ %1, %2
%endmacro

; -----------------------------------------------------------------------------
; \brief  TranslateMessage
; \since  1.0
; -----------------------------------------------------------------------------
%macro TranslateMessage 0
    mov     rcx, rsi
    CALL_IAT TranslateMessage
%endmacro

; -----------------------------------------------------------------------------
; \brief  UpdateWindow refresh the window properties and draw.
; \since  1.0
;
; \see    Invalidate
; \see    Repaint
;
; \param  hwnd -> HWND handle of window to update
; -----------------------------------------------------------------------------
%macro UpdateWindow 1
    mov     rcx, %1
    CALL_IAT UpdateWindow
%endmacro

; -----------------------------------------------------------------------------
; \brief set the length of a given ASCII string to register ...
; -----------------------------------------------------------------------------
%macro SETLEN 2
    mov      %1, %2_length
%endmacro

; -----------------------------------------------------------------------------
; \brief write ASCII text on the text Windows console ...
; -----------------------------------------------------------------------------
%macro WRITE_CON_A 1
    ; prepare
    GET_CON_O_HANDLE r12
    GETDATA  rdx, _cA_%1
    SETLEN   r8d, _cA_%1
    mov      rcx, r12
    xor      r9d, r9d
    mov      qword [rsp+32], 0
    CALL_IAT WriteConsoleA
%endmacro

; -----------------------------------------------------------------------------
; \brief read utf-8 text on the text Windows console ...
; \param dst -> buffer for the "readln" text
; -----------------------------------------------------------------------------
%macro READL_CON_A 1
    ; prepare
    GET_CON_I_HANDLE  r13
    ; ReadConsoleA(hIn, inbuf, maxChars, &read, NULL)
    GETDATA  rdx, _cA_src
    GETDATA  r9 , _cA_%1
    mov      rcx, r13
    mov      r8d, 127           ; maxChars (Reserviere 1 Byte für NUL)
    xor      rax, rax           ; lpReserved = NULL (über Shadow Space)
    mov      [rsp+32], rax
    CALL_IAT ReadConsoleA
%endmacro

; -----------------------------------------------------------------------------
; \brief concatenate two strings (%2, %3) to a given string destionation (%1).
; \param dst  -> string buffer
; \param src1 -> string 0-terminated
; \param src2 -> string 0-terminated
; -----------------------------------------------------------------------------
%macro CONCATE_ANSI 3
    mov     rcx, IMAGE_BASE + RVA_DATA(_cA_%1)
    mov     rdx, IMAGE_BASE + RVA_DATA(_cA_%2)
    mov     r8 , IMAGE_BASE + RVA_DATA(_cA_%3)
    call    concat_ansi
%endmacro

; -----------------------------------------------------------------------------
; \brief integer to string
;
; \param number -> register (number to convert)
; \param buffer -> destination buffer
; -----------------------------------------------------------------------------
%macro INT2STR 2
    mov     edx, %2                             ; number to convert
    mov     rcx, IMAGE_BASE + RVA_DATA(_cA_%1)  ; destination buffer
    call    u32_to_dec                          ; buffer -> "12345",0 ; RAX = 5
%endmacro

; -----------------------------------------------------------------------------
; \brief get the output handle of allocated/open console ...
; \param register to store output handle
; -----------------------------------------------------------------------------
%macro GET_CON_O_HANDLE 1
    mov      ecx, STD_OUTPUT_HANDLE
    CALL_IAT GetStdHandle
    mov      %1, rax         ; hOut
%endmacro
; -----------------------------------------------------------------------------
; \brief get the input handle of allocated/open console ...
; \param register to store input handle
; -----------------------------------------------------------------------------
%macro GET_CON_I_HANDLE 1
    mov      ecx, STD_INPUT_HANDLE
    CALL_IAT GetStdHandle
    mov      %1, rax         ; hIn
%endmacro

%macro SCREEN_CLEAR 0
    GET_CON_O_HANDLE r12
    call user_clear_screen
%endmacro

; -----------------------------------------------------------------------------
; \brief set the color for console window text
; \param 1. background -> int 0..255
; \param 2. foreground -> int 0..255
;
; \desc  color values > 127 == blink chars
; -----------------------------------------------------------------------------
%macro SET_COLOR_TO 0-2
%if %0 == 2
    ; sprintf(buf, "%d %d", ATTR_BG_BLACK, ATTR_FG_YELLOW)
    mov      rax, %1
    mov      rbx, %2
    ;
    mov      rcx, IMAGE_BASE
    add      rcx, RVA_DATA(_cA_buf)          ; buf
    mov      rdx, IMAGE_BASE
    add      rdx, RVA_DATA(_cA_screen_clear) ; fmt
    ;
    mov      r8, rax
    mov      r9, rbx
    CALL_IAT sprintf                        ; EAX = Anzahl geschriebener Zeichen (ohne NUL)
    
    ; WriteFile(hOut, escseq, escsz, &written, NULL)
    GET_CON_O_HANDLE r12
    
    mov      rcx, r12
    lea      rdx, [rel _cA_screen_clear]
    mov      r8d, _cA_buf
    lea      r9,  [written]
    xor      rax, rax
    CALL_IAT WriteFile
%endif
%if %0 == 1
    ; sprintf(buf, "%d %d", ATTR_BG_BLACK, ATTR_FG_YELLOW)
    mov      rax, ATTR_BG_BLACK
    mov      rbx, %1
    ;
    mov      rcx, IMAGE_BASE
    add      rcx, RVA_DATA(_cA_buf)          ; buf
    mov      rdx, IMAGE_BASE
    add      rdx, RVA_DATA(_cA_screen_clear) ; fmt
    ;
    mov      r8, rax
    mov      r9, rbx
    CALL_IAT sprintf                        ; EAX = Anzahl geschriebener Zeichen (ohne NUL)
    
    ; WriteFile(hOut, escseq, escsz, &written, NULL)
    GET_CON_O_HANDLE r12
    
    mov      rcx, r12
    lea      rdx, [rel _cA_screen_clear]
    mov      r8d, _cA_buf
    lea      r9,  [written]
    xor      rax, rax
    CALL_IAT WriteFile
%endif
%if %0 == 0
; sprintf(buf, "%d %d", ATTR_BG_BLACK, ATTR_FG_YELLOW)
    mov      rax, ATTR_BG_BLACK
    mov      rbx, ATTR_FG_WHITE
    ;
    mov      rcx, IMAGE_BASE
    add      rcx, RVA_DATA(_cA_buf)          ; buf
    mov      rdx, IMAGE_BASE
    add      rdx, RVA_DATA(_cA_screen_clear) ; fmt
    ;
    mov      r8, rax
    mov      r9, rbx
    CALL_IAT sprintf                        ; EAX = Anzahl geschriebener Zeichen (ohne NUL)
    
    ; WriteFile(hOut, escseq, escsz, &written, NULL)
    GET_CON_O_HANDLE r12
    
    mov      rcx, r12
    lea      rdx, [rel _cA_screen_clear]
    mov      r8d, _cA_buf
    lea      r9,  [written]
    xor      rax, rax
    CALL_IAT WriteFile
%endif
%endmacro
