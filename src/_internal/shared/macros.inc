; -----------------------------------------------------------------------------
; \file  macros.inc
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

; -----------------------------------------------------------------------------
; \brief some pre-defines, to make maintain easier ...
; -----------------------------------------------------------------------------
%define ERROR_Win32API 'this macro can only be use with win32api (Windows).'

; -----------------------------------------------------------------------------
; \brief DOS error codes for int 0x21 - 3Dh
; -----------------------------------------------------------------------------
%define ERROR_INVALID_FUNCTION      0x01
%define ERROR_FILE_NOT_FOUND        0x02
%define ERROR_PATH_NOT_FOUND        0x03
%define ERROR_TOO_MANY_OPEN_FILES   0x04
%define ERROR_ACCESS_DENIED         0x05
%define ERROR_INVALID_HANDLE        0x06
%define ERROR_ARENA_TRASHED         0x07
%define ERROR_NOT_ENOUGH_MEMORY     0x08
%define ERROR_INVALID_ACCESS        0x0C
%define ERROR_INVALID_DRIVE         0x0F
%define ERROR_CURRENT_DIRECTORY     0x10
%define ERROR_NOT_SAME_DEVICE       0x11
%define ERROR_NO_MORE_FILES         0x12
%define ERROR_SEEK                  0x1D
%define ERROR_NOT_DOS_DISK          0x1E

; -----------------------------------------------------------------------------
; \brief DOS file open modes ...
; -----------------------------------------------------------------------------
%define DOS_READ_ONLY   0x00    ; read  only
%define DOS_WRITE_ONLY  0x01    ; write only
%define DOS_READWRITE   0x02    ; read/write

; -----------------------------------------------------------------------------
; \brief DOS file seek constants ...
; -----------------------------------------------------------------------------
%define SEEK_BEGIN      0x00    ; begin of file
%define SEEK_SET        0x01    ; current position
%define SEEK_END        0x02    ; file end

; -----------------------------------------------------------------------------
; \brief DOS console settings ...
; -----------------------------------------------------------------------------
%define ATTR_DOS_ERROR              0x0E | 0x10     ; yeloow on blue bakcground

%ifndef PTR16
%define PTR16(sym) (sym-code16_start+0x100)
%endif

%ifndef PTR64
%define PTR64(sym) (IMAGE_BASE + RVA_DATA(sym))
%endif

; -----------------------------------------------------------------------------
; \brief perform a system call (in this case a DOS int 0x21 call)
; -----------------------------------------------------------------------------
%macro SysCall 0
%if DOS_SHELL == 1
    int 0x21        ; DOS interrupt 0x21
%endif
%endmacro
%macro VideoCall 0
%if DOS_SHELL == 1
    int 0x10
%else
    %error 'only DOS supports interrupts.'
%endif
%endmacro

; -----------------------------------------------------------------------------
; add win64 abi shadow ...
; -----------------------------------------------------------------------------
%macro AddShadow 0-1
%if %0 == 1
    sub     rsp, %1
%else
    sub     rsp, SW_SHADOW
%endif
%endmacro

; -----------------------------------------------------------------------------
; delete added win64 abi shadow ...
; -----------------------------------------------------------------------------
%macro DelShadow 0-1
%if %0 == 1
    add     rsp, %1
%else
    add     rsp, SW_SHADOW
%endif
%endmacro

; -----------------------------------------------------------------------------
; MAKE_INT <Label>, <Func1>, <Func2>, ...
; -----------------------------------------------------------------------------
%macro MAKE_INT 2-*
%1:
%assign __n %0-1
%rep __n
    dq RVA_IDATA(HN_win32_%2)
    %rotate 1
%endrep
    dq 0
%endmacro

; -----------------------------------------------------------------------------
; MAKE_IAT <Label>, <Func1>, <Func2>, ...
; -----------------------------------------------------------------------------
%macro MAKE_IAT 2-*
iat_win32_%1:
%assign __n %0-1
%rep __n
IAT_win32_%2: dq RVA_IDATA(HN_win32_%2)
    %rotate 1
%endrep
    dq 0
%endmacro

; -----------------------------------------------------------------------------
; HNSTR <Func1>, <Func2>, ...
; -----------------------------------------------------------------------------
%macro HNSTR 1-*
%assign __n %0
%rep __n
HN_win32_%1: dw 0
    db %str(%1), 0
%rotate 1
%endrep
%endmacro

; -----------------------------------------------------------------------------
; MAKE_IMPORT <dir_label>, <mod1>, <mod2>, ...
; erzeugt:
; dir_label:
;   dd RVA_IDATA(INT_<mod>), 0,0, RVA_IDATA(dll_<mod>), RVA_IDATA(iat_<mod>) ...
;   dd 0,0,0,0,0
; dir_label_end:
; -----------------------------------------------------------------------------
%macro MAKE_IMPORT 1-*
    %define __DIR %1
    %1:
    %assign __n %0-1
    %rep __n
        dd RVA_IDATA(INT_win32_%2)
        dd 0,0
        dd RVA_IDATA(dll_win32_%2)
        dd RVA_IDATA(iat_win32_%2)
        %rotate 1
    %endrep
        dd 0,0,0,0,0
    __DIR %+ _end:
    %undef __DIR
%endmacro

; -----------------------------------------------------------------------------
; mini helper ...
; -----------------------------------------------------------------------------
%macro WIN64_PROLOG 0
    mov rbp, rsp
    and rsp, -16
    AddShadow 32         ; Shadow Space
%endmacro

%macro CALL_IAT 1        ; CALL_IAT ExitProcess / RegisterClassExW / ...
    AddShadow
    mov     rax, IMAGE_BASE + RVA_IDATA(IAT_win32_%1)
    call    [rax]
    DelShadow
%endmacro

; -----------------------------------------------------------------------------
; zero register's
; -----------------------------------------------------------------------------
%macro Zero 1
    xor %1, %1
%endmacro

; -----------------------------------------------------------------------------
; UTF-16LE aus ASCII (<=0x7F) schnell schreiben
; -----------------------------------------------------------------------------
%ifndef WSTR_DEBUG
    %define WSTR_DEBUG 0
%endif

; -----------------------------------------------------------------------------
; WSTR <name>, <items...>
; items: Strings ("..."), Zahlen (123, 0x41) oder Ausdrücke/Labels
; erzeugt:
;   _cW_<name>:              dw ... , 0
;   _cW_<name>_end:
;   _cW_<name>_length_bytes  equ (_cW_<name>_end - _cW_<name> - 2) ; ohne Terminator
;   _cW_<name>_length_words  equ (_cW_<name>_length_bytes/2)
; -----------------------------------------------------------------------------
%macro WSTR 2+
    %push WSTR

    ; Namen sichern, damit %rotate keine Probleme macht
    %define _WSTR_LBL   _cW_%1
    %define _WSTR_END   _cW_%1_end
    %define _WSTR_LENB  _cW_%1_length_bytes
    %define _WSTR_LENW  _cW_%1_length_words

_WSTR_LBL:
    ; restliche Argumente abarbeiten
    %assign %$nargs %0-1
    %rotate 1

    %rep %$nargs
        %ifstr %1
            %strlen %$n %1
            %assign %$i 0
            %rep %$n
                %substr %$c %1 %$i+1,1
                dw %$c                      ; eine 16-bit Code Unit 0x00xx
                %assign %$i %$i+1
            %endrep
        %elifnum %1
            dw %1                           ; Zahl/Konstante
        %else
            dw %1                           ; Label/Equate/Expression
        %endif
        %rotate 1
    %endrep

    dw 0                                    ; Null-Terminator (1 Word)

_WSTR_END:
_WSTR_LENB  equ (_WSTR_END - _WSTR_LBL - 2) ; Länge in BYTES (ohne Terminator)
_WSTR_LENW  equ (_WSTR_LENB/2)              ; Länge in WORDS

    ; Aufräumen
    %undef _WSTR_LBL
    %undef _WSTR_END
    %undef _WSTR_LENB
    %undef _WSTR_LENW
    %pop
%endmacro
; -----------------------------------------------------------------------------
; WSTRU <name>, <items...>
; items:
;   - "ASCII/Latin-1-Strings"  -> jedes Zeichen als 16-bit Code Unit 0x00xx
;   - Zahlen/Expressions        -> als Unicode-Codepoint interpretiert:
;                                 <=0xFFFF (außer Surrogatbereich) -> 1 Word
;                                 >0xFFFF -> Surrogatpaar (2 Words)
; erzeugt:
;   _cW_<name>:              dw ..., 0
;   _cW_<name>_end:
;   _cW_<name>_length_bytes  equ (_cW_<name>_end - _cW_<name> - 2) ; ohne Terminator
;   _cW_<name>_length_words  equ (_cW_<name>_length_bytes/2)
; -----------------------------------------------------------------------------
; --- Helper: einen Unicode-Codepoint als UTF-16 ausgeben ---
; -----------------------------------------------------------------------------
%macro __WSTR_EMIT_CP 1
    %assign __cp (%1)

    %if __cp < 0
        %error "WSTR: negativer Codepoint"
    %elif __cp <= 0xFFFF
        ; verbiete explizite Surrogat-Codepoints
        %if __cp >= 0xD800 && __cp <= 0xDFFF
            %error "WSTR: Codepoint im Surrogatbereich ist ungueltig"
        %else
            dw __cp
        %endif
    %elif __cp <= 0x10FFFF
        %assign __tmp (__cp - 0x10000)
        %assign __hi  (0xD800 + (__tmp >> 10))
        %assign __lo  (0xDC00 + (__tmp & 0x3FF))
        dw __hi, __lo
    %else
        %error "WSTR: Codepoint > U+10FFFF"
    %endif
%endmacro

; --- Hauptmakro ---
%macro WSTRU 2+
    %push WSTRU

    %define _WSTR_LBL   _cW_%1
    %define _WSTR_END   _cW_%1_end
    %define _WSTR_LENB  _cW_%1_length_bytes
    %define _WSTR_LENW  _cW_%1_length_words

_WSTR_LBL:
    %assign %$nargs %0-1
    %rotate 1

    %rep %$nargs
        %ifstr %1
            ; String: byteweise -> 0x00xx
            %strlen %$n %1
            %assign %$i 0
            %rep %$n
                %substr %$c %1 %$i+1,1
                dw %$c
                %assign %$i %$i+1
            %endrep
        %elifnum %1
            ; Zahl/Expression als Unicode-Scalar
            __WSTR_EMIT_CP %1
        %else
            ; Label/Expression, zur Sicherheit ebenfalls als Codepoint behandeln
            __WSTR_EMIT_CP %1
        %endif
        %rotate 1
    %endrep

    dw 0

_WSTR_END:
_WSTR_LENB  equ (_WSTR_END - _WSTR_LBL - 2)
_WSTR_LENW  equ (_WSTR_LENB/2)

    %undef _WSTR_LBL
    %undef _WSTR_END
    %undef _WSTR_LENB
    %undef _WSTR_LENW
    %pop
%endmacro

; -----------------------------------------------------------------------------
; WSTRUL  <name>, <args...>   -> definiert <name> und <name>_len
; (in Codeunits, ohne Null)
; -----------------------------------------------------------------------------
%macro WSTR_AND_LEN 2-*
    %push WSTRUL
    %define %$name %1
%1:
    WSTRU %2
%$name %+ _end:
    %xdefine %$name %+ _len ( ((%$name %+ _end) - (%$name))/2 - 1 )
    %pop
%endmacro

; -----------------------------------------------------------------------------
; Nach JEDEM vorhandenen Stringlabel einfach:
;   <label>_end:   (direkt nach dem String)
; und dann:
; -----------------------------------------------------------------------------
%macro WSTR_LENGTH 1
    %xdefine %1_len ( ((%1_end) - (%1))/2 - 1 )
%endmacro

%macro AWSTR 1
%push
%strlen __n %1
%assign __i 0
%rep __n
    %substr __c %1 __i+1,1
    dw __c
    %assign __i __i+1
%endrep
    dw 0
%pop
%endmacro

; -----------------------------------------------------------------------------
; \brief String-Definition mit auto *_length (ohne 0-Byte)
; \desc  section .data
;        ZSTR cap2A, "Hallo", 13, 10
;
;        ergibt automatisch:
;        cap2A          db "Hallo",13,10,0
;        cap2A_end:
;        %define cap2A_length (cap2A_end - cap2A - 1)
; -----------------------------------------------------------------------------
%macro ASTR 2+                    ; ASTR <name>, <bytes...>
_cA_%1:       db %2, 0
_cA_%1_end:
_cA_%1_length equ (_cA_%1_end - _cA_%1 - 1)
%endmacro

; -----------------------------------------------------------------------------
; \brief set the string label from %2 to register %1 ...
; -----------------------------------------------------------------------------
%macro GETEXT 2
    mov     %1, IMAGE_BASE
    add     %1, RVA_DATA(_cW_%2)
%endmacro

; ------------------------------------------------------------
; ---- RVA-Helfer: bleibt wie bei dir ----
; %define RVA_DATA(L)   (DATA_VA  + ((L) - data_start))
; ------------------------------------------------------------
; Optional: einfacher Alias ohne Klammern/EXPR:
; ------------------------------------------------------------
%imacro DATA_ABS 1
    IMAGE_BASE + RVA_DATA(%1)
%endmacro
; ------------------------------------------------------------
; Helfer: absolute VA einer Data-Variable bauen
; ------------------------------------------------------------
%macro DATA_PTR 1
    (IMAGE_BASE + RVA_DATA(%1))
%endmacro
; ---------------------------------------------------------------------------
;; SETDATA <name>, <src> [, <size>]
;  - Schreibt <src> an Datenlabel <name>
;  - Wenn <size> fehlt, wird die Größe aus <src>-Register abgeleitet
;    (al/ax/eax/rax → 8/16/32/64 Bit). Bei Immediate bitte <size> angeben.
;  - <size> darf BYTE/WORD/DWORD/QWORD oder 8/16/32/64 sein.
; ---------------------------------------------------------------------------
;; Beispiele:
; last_error: dd 0
; orig_attr:  dw 0
; flag8:      db 0
; ---------------------------------------------------------------------------
;; schreiben (Registergröße bestimmt Breite)
; mov   eax, 0xDEADBEEF
; SETDATA last_error, eax          ; dword write
; ---------------------------------------------------------------------------
;; schreiben (Immediate -> Größe angeben)
; SETDATA orig_attr, 0x000F, WORD  ; word write
; SETDATA flag8,     1,      BYTE  ; byte write
; ---------------------------------------------------------------------------
;; lesen (Registergröße passt)
; GETDATA eax, last_error          ; dword read → eax
; ---------------------------------------------------------------------------
;; lesen (Größe erzwingen)
; GETDATA ax,  orig_attr, WORD     ; word read → ax
; GETDATA al,  flag8,     BYTE     ; byte read → al
; ---------------------------------------------------------------------------
%macro SETDATA 2-3
    push    rdx
    mov     rdx, IMAGE_BASE
    add     rdx, RVA_DATA(%1)
    %if %0 = 2
        mov     [%2], rdx
        pop     rdx
    %else
        pop     rdx
      %ifidni %3, BYTE
        mov     byte  [rdx], %2
      %elifidni %3, WORD
        mov     word  [rdx], %2
      %elifidni %3, DWORD
        mov     dword [rdx], %2
      %elifidni %3, QWORD
        mov     qword [rdx], %2
      %elif %3 = 8
        mov     byte  [rdx], %2
      %elif %3 = 16
        mov     word  [rdx], %2
      %elif %3 = 32
        mov     dword [rdx], %2
      %elif %3 = 64
        mov     qword [rdx], %2
      %else
        %error "SETDATA: 3rd arg must be BYTE/WORD/DWORD/QWORD or 8/16/32/64"
      %endif
    %endif
%endmacro

; ------------------------------------------------------------
; GETDATA <dst>, <name> [, <size>]
;  - Liest aus Datenlabel <name> in Register <dst>
;  - Wenn <size> fehlt, muss <dst> die passende Größe haben
;    (al/ax/eax/rax). Sonst <size> angeben (BYTE/WORD/DWORD/QWORD oder 8/16/32/64).
; ------------------------------------------------------------
%macro GETDATA 2-3
    mov     %1, IMAGE_BASE
    add     %1, RVA_DATA(%2)
    %if %0 = 2
        ;mov     %1, [rdx]
    %else
      %ifidni %3, BYTE
        mov     %1, byte  [rdx]
      %elifidni %3, WORD
        mov     %1, word  [rdx]
      %elifidni %3, DWORD
        mov     %1, dword [rdx]
      %elifidni %3, QWORD
        mov     %1, qword [rdx]
      %elif %3 = 8
        mov     %1, byte  [rdx]
      %elif %3 = 16
        mov     %1, word  [rdx]
      %elif %3 = 32
        mov     %1, dword [rdx]
      %elif %3 = 64
        mov     %1, qword [rdx]
      %else
        %error "GETDATA: 3rd arg must be BYTE/WORD/DWORD/QWORD or 8/16/32/64"
      %endif
    %endif
%endmacro

%macro Return 0-1
%if %0 == 1
    mov eax, %1
%else
    ret
%endif
%endmacro

; -----------------------------------------------------------------------------
; condition jump's after function call -> test eax, eax
; -----------------------------------------------------------------------------
%macro CHECK_NZ 1-2
%if %0 == 2
    test eax, eax
    jnz %1
    jmp %2
%else
    test eax, eax
    jnz %1
%endif
%endmacro

; -----------------------------------------------------------------------------
%macro CHECK_NE 1-2
%if %0 == 2
    test eax, eax
    jne %1
    jmp %2
%else
    test eax, eax
    jne %1
%endif
%endmacro

; -----------------------------------------------------------------------------
%macro CHECK_E 1-2
%if %0 == 2
    test eax, eax
    je  %1
    jmp %2
%else
    test eax, eax
    je  %1
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief prolog of a assembler routine + 32 Windows 64 Bit shadow
; \param optional shadow at start -> int
; -----------------------------------------------------------------------------
%macro FUNC_ENTER 0-1
%if %0 == 1
    AddShadow %1
%else
    AddShadow
%endif
    push    rbp
    mov     rbp, rsp
%endmacro

; -----------------------------------------------------------------------------
; \brief epilog of a assembler routine - 32 Windows 64 Bit shadow
; \param optional shadow at end -> int
; -----------------------------------------------------------------------------
%macro FUNC_LEAVE 0-1
%if %0 == 1
    DelShadow %1
%else
    DelShadow
%endif
    pop     rbp
    ret
%endmacro

; -----------------------------------------------------------------------------
; \brief allocate/open a text console window under Windows 11 desktop.
; \param ok  -> label
; \param err -> label
; \since 1.0
;
; \return bool - 0 no Error; else Error
; -----------------------------------------------------------------------------
%macro call_AllocConsole 2
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    CALL_IAT AllocConsole
    %if %0 == 2
        CHECK_NZ %1, %2
    %endif
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief call the Windows 10 win32api function ExitProcess, to close the thread
; -----------------------------------------------------------------------------
%macro call_ExitProcess 0-1
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    %if %0 == 1
        mov rax, %1
    %else
        mov rax, 0
    %endif
    CALL_IAT ExitProcess
%endif
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
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    CALL_IAT GetLastError
    test rax, rax
    jnz  %%ok
    AddShadow
    call HandleLastError
    DelShadow
%%ok:
;ShowMessageW ShowLastW,capW
%endif
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
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
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
%endif
%endmacro

%macro call_LoadCursorW 0
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    CALL_IAT LoadCursorW
    ;ShowMessageW ShowHelloW,capW
    ;call_GetLastError
%endif
%endmacro

%macro call_LocalFree 0
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    CALL_IAT MessageBoxW
%endif
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
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    CALL_IAT WriteConsoleA
%endif
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
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
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
%endif
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
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    mov     rax, IMAGE_BASE
    add     rax, RVA_IDATA(IAT_win32_CreateWindowExW)
    call    [rax]
%endif
%endmacro
; -----------------------------------------------------------------------------

; -----------------------------------------------------------------------------
; \brief  DispatchMessageW
; \since  1.0
; -----------------------------------------------------------------------------
%macro DispatchMessageW 0
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    mov     rcx, rsi
    CALL_IAT DispatchMessageW
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief  ExitProcess terminate the given application thread.
; \since  1.0
; \param  exitcode -> integer
; \return exitcode -> rax
; -----------------------------------------------------------------------------
%macro ExitProcess 0-1 0
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    nop
    ;AddShadow (32 + 16)           ; Shadow Space + 16 B Align
    mov     ecx,%1
    CALL_IAT ExitProcess
    ; no return
    ;DelShadow (32 + 16)
%endif
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
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    CALL_IAT GetLastError
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief  GetMessageW
; -----------------------------------------------------------------------------
%macro GetMessageW 0
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    mov  rcx, rsi
    Zero edx
    Zero r8d
    Zero r9d
    CALL_IAT GetMessageW
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief  LoadCursorW
; \since  1.0
; \param  id - integer: resource id
; -----------------------------------------------------------------------------
%macro LoadCursorW 1
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    Zero ecx
    mov  edx, %1
    CALL_IAT LoadCursorW
%endif
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
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    Zero    ecx             ; hWnd = NULL
    mov     rdx, PTR64(%1)  ; lpText
    mov     r8,  PTR64(%2)  ; lpCaption    
%if %0 == 2                 ; %0 = argument count
    xor     r9d, r9d        ; uType = MB_OK
%else
    mov     r9d, %3         ; uType = argument exists
%endif
    CALL_IAT MessageBoxW
%endif
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
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    Zero    ecx
    mov     rdx, IMAGE_BASE + RVA_DATA(_cA_%1)  ; "MessageBoxW failed"
    mov     r8,  IMAGE_BASE + RVA_DATA(_cA_%2)  ; "User32"
%if %0 == 2                                     ; %0 = argument count
    xor     r9d, r9d                            ; uType = MB_OK
%else
    mov     r9d, %3                             ; uType = argument exists
%endif
    CALL_IAT MessageBoxA
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief  ShowWindow shows the window witht the hwnd id in r13.
; \since  1.0
; \param  hwnd -> HWND handle window
; \param  (optional) flag -> integer: default = SW_SHOWDEFAULT
; -----------------------------------------------------------------------------
%macro ShowWindow 1-2
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
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
%endif
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
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    mov     rcx, rsi
    CALL_IAT TranslateMessage
%endif
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
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    mov     rcx, %1
    CALL_IAT UpdateWindow
%endif
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
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    mov      ecx, STD_OUTPUT_HANDLE
    CALL_IAT GetStdHandle
    mov      %1, rax         ; hOut
%endif
%endmacro
; -----------------------------------------------------------------------------
; \brief get the input handle of allocated/open console ...
; \param register to store input handle
; -----------------------------------------------------------------------------
%macro GET_CON_I_HANDLE 1
%if DOS_SHELL == 1
    %error ERROR_Win32API
%else
    mov      ecx, STD_INPUT_HANDLE
    CALL_IAT GetStdHandle
    mov      %1, rax         ; hIn
%endif
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
; \param xpos - <imm>
; \param ypos - <imm>
; -----------------------------------------------------------------------------
%macro SET_CURSOR 2
%if %0 == 0
    %error 2 argument missing
%endif
%if DOS_SHELL == 1
    mov  dl, %1         ; column
    mov  dh, %2         ; row
    call dos_set_cursor
%else
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief get the cursor position in dos console ...
; -----------------------------------------------------------------------------
%macro GET_CURSOR 0
%if DOS_SHELL == 1
    call dos_get_cursor
%else
    %error 'todo: windows'
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
    STRCAT_ANSI buffer_B,                     \
                console_color_%1, buffer_semi,\
                console_color_%2, consoleColor_2
    WRITE_CON_A buffer_B
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief 
; -----------------------------------------------------------------------------
%macro ARG_CURSOR 2
%if DOS_SHELL == 1
    GET_ARG  %1             ; save command line argument 1
    mov  bl, %2             ; color
    call PutStrColor        ; DOS screen
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief macro to put a colored string to the DOS console ...
; -----------------------------------------------------------------------------
%macro PUTS_COLOR 2
%if DOS_SHELL == 1
    GET_CURSOR              ; move cursor to col:row
    %ifidni %1, SI              ; text is already in SI
        mov  bl, %2             ; color
        call PutStrColor        ; DOS screen
    %elifidni %1, ARGV_1
        ARG_CURSOR 1, %2        ; save command line argument 1
    %elifidni %1, ARGV_2
        ARG_CURSOR 2, %2        ; save command line argument 2
    %elifidni %1, ARGV_3
        ARG_CURSOR 3, %2        ; save command line argument 3
    %elifidni %1, ARGV_4
        ARG_CURSOR 4, %2        ; save command line argument 4
    %elifidni %1, ARGV_5
        ARG_CURSOR 5, %2        ; save command line argument 5
    %elifidni %1, ARGV_6
        ARG_CURSOR 6, %2        ; save command line argument 6
    %elifidni %1, ARGV_7
        ARG_CURSOR 7, %2        ; save command line argument 7
    %else
        mov  bl, %2             ; color
        lea  si, PTR16(_cA_%1)  ; text 0-terminated
        call PutStrColor        ; DOS screen
    %endif
%else
    %error 'this macro is only for DOS programming.'
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
    %elifidni %1, CX
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
    mov es, ax
    mov ah, 0x49
    SysCall
%else
    %error 'todo: windows'
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief COMPARE <reg>, <imm>, <label>
; \param 1. <reg>
; \param 2. <imm>
; \param 3. <label>
; \note  example: COMPARE al, 0x0a, printed
;        result:  cmp <reg>, <imm>  /  je <label>
; -----------------------------------------------------------------------------
%macro COMPARE 3
    cmp %1, %2
    je  %3
%endmacro

; -----------------------------------------------------------------------------
; \brief  get the n-th command line ...
; \param  1. <imm>
; \return SI = text (=argument)
; \note   example: GET_ARG 2
;         result:  <text> in SI
; -----------------------------------------------------------------------------
%macro GET_ARG 1
%if DOS_SHELL == 1
    lea  si, [PTR16(_cA_cmd_buf)]
    mov  bl, %1
    call getCommandLine_Arg
%else
    %error 'todo: windows'
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief save the n-th command line argument to the <label>
; \param 1. <imm> -> n-th argument number
; \param 2. <label>
; \note  example: SET_ARG <imm>, <label>
; -----------------------------------------------------------------------------
%macro SET_ARG 1-2
%if DOS_SHELL == 1
    %if %0 == 1
        GET_ARG  %1
        STR_COPY _cA_cmd_arg_%1
    %else
        GET_ARG  %1
        STR_COPY _cA_%2
    %endif
%else
    %error 'todo: windows'
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief copy a string from source index SI to DI <label>
; \param 1. <label>
; \note  example: STR_COPY <label>
; -----------------------------------------------------------------------------
%macro STR_COPY 1
%if DOS_SHELL == 1
    lea  di, [%1]       ; ES wird in string_copy gesetzt
    call string_copy    ; kommt zurück mit SI = Zielstart
%else
    %error 'todo: windows'
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief short'ner to get the command line arguments given by the user input.
; \brief initialize a console application ...
; \param nothing
; -----------------------------------------------------------------------------
%macro INIT_COMMAND_LINE 0
%if DOS_SHELL == 1
    call dos_get_command_line
%else
    %error 'todo: windows'
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief call the DOS console initialize routine ...
; -----------------------------------------------------------------------------
%macro INIT_CONSOLE 0
%if DOS_SHELL == 1
    call dos_init_console
%else
    call init_app
    call init_console
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief generischer Handler für einen Fehlercode ...
; -----------------------------------------------------------------------------
%macro DEF_ERROR 2
_h%1:
    PUTS_COLOR %2, ATTR_DOS_ERROR
    mov   cx, %1
    jmp   _open_exit
%endmacro

; -----------------------------------------------------------------------------
; \brief DOS seek to <origin> in file <handle> ...
; \param 1. <file handle>
; \param 2. <origin> 0 - begin of file, 1 - current position, 2 - end of file
; -----------------------------------------------------------------------------
%macro DOS_Seek 2
%if DOS_SHELL == 1
    mov  bx, [PTR16(_cA_%1)]
    xor  cx, cx
    xor  dx, dx
    mov  ah, 0x42               ; move to ...
    mov  al, %2
    SysCall
%else
    %error 'todo: windows'
%endif
%endmacro

; -----------------------------------------------------------------------------
; \brief DOS open existing <file name>
; \param 1. <file name>
; \param 2. <open mode> - DOS_READ_ONLY, DOW_WRITE_ONLY, DOS_READWRITE
; -----------------------------------------------------------------------------
%macro DOS_Open 2
%if DOS_SHELL == 1
    mov  dx, PTR16(_cA_%1)
    mov  ah, 0x3D               ; open existing file
    mov  al, %2                 ; read-only
    SysCall
%else
    %error 'todo: windows'
%endif
%endmacro

%macro DOS_Close 0
%if DOS_SHELL == 1
    mov  ah, 3Eh
    SysCall
%else
    %error 'todo: windows'
%endif
%endmacro
