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
    Zero    ecx             ; hWnd = NULL
    mov     rdx, PTR64(%1)  ; lpText
    mov     r8,  PTR64(%2)  ; lpCaption    
%if %0 == 2                 ; %0 = argument count
    xor     r9d, r9d        ; uType = MB_OK
%else
    mov     r9d, %3         ; uType = argument exists
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
%macro WRITE_CON_A 1-2
%if DOS_SHELL == 1
    %if %0 == 2
        PUTS_COLOR %1, %2
    %else
        PUTS_COLOR %1, 0x07
    %endif
%else
    ; prepare
    xor      eax, eax
    mov      rcx, PTR64(_cA_%1)
    call     GET_STR_LEN
    mov      r14, rax
    GET_CON_O_HANDLE r12
    mov      rcx, r12
    mov      rdx, PTR64(_cA_%1)
    mov      r8 , r14
    xor      r9d, r9d
    mov      qword [rsp+32], 0
    CALL_IAT WriteConsoleA
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief read utf-8 text on the text Windows console ...
; \param dst -> buffer for the "readln" text
; -----------------------------------------------------------------------------
%macro READL_CON_A 0-1
%if DOS_SHELL == 1
    %if  %0 == 1
        mov  dx, PTR16(_cA_%1)
        call DOSReadLn
    %else
        mov  dx, PTR16(_cA_dos_buffer)
        call DOSReadLn
    %endif
%else
    ; prepare
    GET_CON_I_HANDLE  r13
    ; ReadConsoleA(hIn, inbuf, maxChars, &read, NULL)
    mov      rcx, r13
    mov      rdx, PTR64(_cA_%1)
    mov      r8d, 127           ; maxChars (Reserviere 1 Byte für NUL)
    mov      r9 , PTR64(written)
    xor      rax, rax           ; lpReserved = NULL (über Shadow Space)
    mov      [rsp+32], rax
    CALL_IAT ReadConsoleA
%endif
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
; \brief concatenate two strings (%2, %3) to a given string destionation (%1).
; \param dst  -> string buffer
; \param src1 -> string 0-terminated
; \param src2 -> string 0-terminated
; -----------------------------------------------------------------------------
%macro STRCPY_ANSI 3
    mov     rcx, IMAGE_BASE + RVA_DATA(_cA_%1)
    mov     rdx, IMAGE_BASE + RVA_DATA(_cA_%2)
    mov     r8 , IMAGE_BASE + RVA_DATA(_cA_%3)
    call    concat_ansi
%endmacro
%macro STRCAT_ANSI 2-*
    %xdefine __DSTSYM (_cA_%1 + 4)

    %rotate 1                     ; ab hier ist %1 der erste src
    %rep %0-1
        ; --- Ende von dst finden: RDI zeigt nach REPNZ SCASB auf Byte NACH '\0'
        mov     rdi, IMAGE_BASE
        add     rdi, RVA_DATA(__DSTSYM)
        xor     eax, eax          ; AL = 0
        mov     rcx, -1
        repne   scasb
        lea     rcx, [rdi - 1]    ; RCX -> Position des '\0' (Schreibposition)

        ; einen Source anhängen: (s1 = aktueller, s2 = leer)
        mov     rdx, PTR64(_cA_%1)
        mov     r8 , PTR64(_cA_empty)
        call    concat_ansi

        %rotate 1                 ; nächster src
    %endrep
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
%if DOS_SHELL == 1
    call dos_screen_clear
%else
    GET_CON_O_HANDLE r12
    STRCPY_ANSI buffer_B, consoleColor_3, empty
    WRITE_CON_A buffer_B
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief set the cursor position in dos console ...
; \param xpos - int
; \param ypos - int
; -----------------------------------------------------------------------------
%macro SET_CURSOR 2
%if %0 == 0
    %error 2 argument missiong
%endif
%if DOS_SHELL == 1
    mov  ah, 0x02
    mov  bh, 0x00
    %ifidni %2, DH
        inc  dh
    %else
        mov  dh, %2         ; row
    %endif
    %ifidni %1, DL
        inc  dl
    %else
        mov  dl, %1         ; col
    %endif
    int  0x10
%else
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief set the color for console window text
; \param 1. background -> int 0..255
; \param 2. foreground -> int 0..255
;
; \desc  color values > 127 == blink chars
; -----------------------------------------------------------------------------
%macro SET_COLOR_TO 2
%if %0 == 2
    STRCPY_ANSI buffer_B, consoleColor_1, empty
    STRCAT_ANSI buffer_B,                         \
                console_color_%1, buffer_semi,\
                console_color_%2, consoleColor_2
    WRITE_CON_A buffer_B
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief macro to put a colored string to the DOS console ...
; -----------------------------------------------------------------------------
%macro PUTS_COLOR 2
%if DOS_SHELL == 1
    mov  bl, %2             ; color
    lea  si, PTR16(_cA_%1)  ; text 0-terminated
    call PutStrColor
%else
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief  get the length of given label string
; \param  1. label name/addr
; \return CX = length of string
; -----------------------------------------------------------------------------
%macro STRLEN 1
%if %0 == 1
    mov  si, PTR16(_cA_%1)
    call DOSStrLen
    mov  ax, cx             ; AX = length
    add  cx, 1              ; CX = length + 1
%else
    %error 'exactly one argument expected.'
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief  helper macro save code resources.
; \desc   return to DOS with exit code
; \param  1. exit code value (0..255).
; \return nothing
; -----------------------------------------------------------------------------
%macro DOS_Exit 1
%if DOS_SHELL == 1
    %ifidni   %1, ax
        %error 'AX not allowed here.'
    %elifidni %1, bx
        mov ax, 0x4C00
        or  ax, bx
        SysCall
    %elifidni %1, cx
        mov ax, 0x4C00
        or  ax, cx
        SysCall
    %elifidni %1, dx
        mov ax, 0x4C00
        or  ax, dx
        SysCall
    %elifnum  %1
        mov  ax, 0x4C00 | %1
        SysCall
    %else
        %error 'BX, CX, DX or <NUM> expected.'
    %endif
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief  print a CRLF on DOS console
; \param  nothing
; \return nothing
; -----------------------------------------------------------------------------
%macro DOS_crlf 0
    call DOSrncrlf
%endmacro

; -----------------------------------------------------------------------------
; \brief write a string in DX to DOS console without "lf", and no "cr" ...
; \param 1. DX - src label
; \see   DOS_WriteLn
; -----------------------------------------------------------------------------
%macro DOS_Write 1
    lea  dx, [PTR16(_cA_%1)]
    call DOS_ConsoleWrite
%endmacro

; -----------------------------------------------------------------------------
; \brief write a string in DX to DOS console with "lf", and "cr" ...
; \param 1. DX - src label
; \see   DOS_Write
; -----------------------------------------------------------------------------
%macro DOS_WriteLn 1
    DOS_Write %1
    DOS_crlf
%endmacro

; -----------------------------------------------------------------------------
; \brief allocate memory for/in the DOS console ...
; \param 1. count paragraphs
; \note  calculate with: 4096 / 16 = 256 (4096 is a example !)
; -----------------------------------------------------------------------------
%macro DOS_AllocMem 1
%if DOS_SHELL == 1
    mov  ax, 4800h      ; AH = 48h -> Allocate Memory Block
    mov  bx, %1         ; Paragraph-Anzahl
    SysCall
    
    sbb  ax, ax
    cmp  ax, 0
    je   %%.successful
    
    cmp  ax, 0xFF
    je   %%.fail        ; CF = 1 -> error, AX = error code
    
    jmp  %%.fail
    
    %%.successful:
    ; AX = Segment des Blocks
    mov  es, ax
    xor  di, di
    
    ; Block mit 0x00 füllen
    mov  cx, 4096
    mov  al, 0x00
    rep  stosb          ; write to ES:DI
    
    ; demo read access: AL = ES:[1234]
    ;mov  di, 1234
    ;mov  al, [es:di]
    
    jmp   %%.next
    
    %%.fail:
    DOS_WriteLn msg_alloc_error
    DOS_Exit    1
    
    %%.next:
%endif
%endmacro

%macro DOS_FreeMem 0
%if DOS_SHELL == 1
    mov ax, 0x4900
    SysCall
%endif
%endmacro
