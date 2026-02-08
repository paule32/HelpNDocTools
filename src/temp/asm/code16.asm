; -----------------------------------------------------------------------------
; \file  code16.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%define MAX_ARGS  7
bits 16
; -----------------------------------------------------------------------------
; \brief  Create/Append field into dBASE III/IV DBF by INT 21h
; \note   Build:  nasm -f bin dbfmake.asm -o DBFMAKE.COM
;         Run:    DBFMAKE <type> <cmd> <fieldtype> <feldname> <feldlength>
;         Example:
;             DBFMAKE 3 CREATE C NAME 20
;             DBFMAKE 4 APPEND I AGE 3
;
; \note   Type: 3 (dBASE III), 4 (dBASE IV)
; \note   Cmd:  CREATE | APPEND
; \note   Fieldtype: C,I,F,B,D,T  (T only for type 4)
; \note   Fieldname: max 10 chars (dBASE-limit, 11. Byte = 0)
; \note   Fiedlength: decimal (e.g.. 20)
; -----------------------------------------------------------------------------
%if ((DOS_SHELL == 16) && ((DOS_MODE == 16) || (DOS_MODE == 32)))
code16_start:
    INIT_COMMAND_LINE
    INIT_CONSOLE
    
    SCREEN_CLEAR
    SET_CURSOR 0, 1
    
    %if DOS_MODE == 32
        call PROC_CHECK
        call CHECK_MODE
        
        cli                    ; Interrupts aus

        ; DS-Segmentbasis berechnen (Segment << 4)
        mov   dx, ds
        movzx edx, dx
        shl   edx, 4           ; EDX = DS * 16 = lineare Basis des datasegments

        lea eax, [edx + PTR16(_cA_gdt)] ; GDT liegt irgendwo in unserem data, also Basis + Offset
        mov  [PTR16(_cA_gdt_descriptor)+2], eax   ; GDT-Basis in Descriptor schreiben

        lgdt [PTR16(_cA_gdt_descriptor)]  ; GDTR laden

        ; -----------------------------
        ; Protected Mode einschalten
        ; -----------------------------
        mov eax, cr0
        or  eax, 1             ; PE-Bit (Bit 0) setzen
        mov cr0, eax

        ; Weit-Sprung in 32-Bit Code-Segment, um Pipeline zu leeren und CS zu setzen
        push 0x08
        add edx, PTR16(go_pm)
        push edx
        mov bp, sp
        jmp far dword [bp]
    %else
        DOS_Exit 0
    %endif
%endif

%if ((DOS_SHELL == 16) && (DOS_MODE == 32))
bits 32
go_pm:
section .text
    incbin 'kernel32.bin'
    spin:   jmp spin        ; Loop
%endif

; -----------------------------------------------------------------------------
; \brief check, if a compatible 80386 CPU is present on the system ...
; -----------------------------------------------------------------------------
%if ((DOS_SHELL == 16) && ((DOS_MODE == 16) || (DOS_MODE == 32)))
bits 16
PROC_CHECK:
    pushf                   ; save flags
    xor  ah, ah             ; clear high byte
    push ax                 ; push AX onto the stack
    popf                    ; pop this value into the flag register
    pushf                   ; push flags onto the stack
    pop  ax                 ; ...and get flags into AX
    and  ah, 0xF0           ; try to set the high nibble
    cmp  ah, 0xF0           ; the high nibble is never 0f0h on a
    je   no386              ; 80386!
    mov  ah, 70h            ; now try to set NT and IOPL
    push ax
    popf
    pushf
    pop  ax
    and  ah, 70h            ; if they couldn't be modified, there
    jz   no386              ; is no 80386 installed
    popf                    ; restore the flags
    ret                     ; ...and return
    
    no386:                  ; if there isn't a 80386, put a msg
    PUTS_COLOR no386e, 3    ; and exit
    DOS_Exit 1
    ret
%endif
; -----------------------------------------------------------------------------
; \brief check, if we in real mode or not ...
; -----------------------------------------------------------------------------
%if ((DOS_SHELL == 16) && ((DOS_MODE == 16) || (DOS_MODE == 32)))
bits 16
CHECK_MODE:
    mov eax, cr0            ; get CR0 to EAX
    and al, 1               ; check if PM bit is set
    jnz not_real_mode		; yes, it is, so exit
    ret                     ; no, it isn't, return
    
    not_real_mode:
    PUTS_COLOR norealmode, 3
    DOS_Exit 1
    ret
%endif

; -----------------------------------------------------------------------------
; \brief include DOS 16-bit stdlib function's ...
; -----------------------------------------------------------------------------
%include 'CommandLineArg.asm'       ; get command line arguments
%include 'ConsoleCursor.asm'        ; set the teletype video text cursor
%include 'ErrorCodes.asm'           ; get last error
%include 'InitConsole.asm'          ; initialize the DOS console
%include 'Int16ToStr.asm'           ; convert integer number to string
%include 'PutStrColor.asm'          ; put colored text onto the DOS screen
%include 'ReadLn16.asm'             ; read a line of text
%include 'ScreenClear.asm'          ; clear the screen
%include 'Str16Len.asm'             ; get the length of a string
%include 'StrCompare.asm'           ; string compare
%include 'StrCopy.asm'              ; copy a string

code16_end:
