; -----------------------------------------------------------------------------
; \file  macros.inc
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

; -----------------------------------------------------------------------------
; add win64 abi shadow ...
; -----------------------------------------------------------------------------
%macro AddShadow 0-1
%if %0 == 1
    sub     rsp, %1
%else
    sub     rsp, 32
%endif
%endmacro

; -----------------------------------------------------------------------------
; delete added win64 abi shadow ...
; -----------------------------------------------------------------------------
%macro DelShadow 0-1
%if %0 == 1
    add     rsp, %1
%else
    add     rsp, 32
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

%macro WSTR 1-*
    %push WSTR                  ; Kontext für %$-Variablen bereitstellen
    %assign %$arg 0
    %rep %0
        %assign %$arg %$arg+1
        %if %$arg > 1
            %rotate 1           ; nächstes Macro-Argument in %1 schieben
        %endif
        %ifstr %1
            %strlen %$n %1
            %assign %$i 0
            %rep %$n
                %substr %$c %1 %$i+1,1
                dw %$c          ; 1 Code Unit (0x00xx) ausgeben
                %assign %$i %$i+1
            %endrep
        %elifnum %1
            dw %1               ; Zahl/Konstante
        %else
            dw %1               ; Label/Equate/Expression
        %endif
    %endrep
    dw 0                        ; Nullterminator
    %pop                        ; Kontext verlassen
%endmacro

; WSTRU  <args...>   (ASCII-Stücke + U+codepoints)
%macro WSTRU 1-*
    %push WSTRU
    %assign %$k 0
    %rep %0
        %assign %$k %$k+1
        %if %$k > 1
            %rotate 1
        %endif
        %ifstr %1
            ; ASCII-Stück → wie WSTR
            %strlen %$n %1
            %assign %$i 0
            %rep %$n
                %substr %$c %1 %$i+1,1
                dw %$c
                %assign %$i %$i+1
            %endrep
        %else
            ; Ansonsten Codepoints/Numbers → WU
            WU %1
        %endif
    %endrep
    dw 0
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
;; schreiben (Immediate → Größe angeben)
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
    mov     rdx, IMAGE_BASE
    add     rdx, RVA_DATA(%1)
    %if %0 = 2
        mov     [rdx], %2
    %else
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
    mov     rdx, IMAGE_BASE
    add     rdx, RVA_DATA(%2)
    %if %0 = 2
        mov     %1, [rdx]
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
