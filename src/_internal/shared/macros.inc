; -----------------------------------------------------------------------------
; \file  macros.inc
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

%ifndef PTR
%define PTR(sym) (IMAGE_BASE + RVA_DATA(sym))
%endif

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
; \brief initialize a console application ...
; \param nothing
; -----------------------------------------------------------------------------
%macro INIT_CONSOLE 0
    call init_app
    call init_console
%endmacro
