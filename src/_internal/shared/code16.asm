; -----------------------------------------------------------------------------
; \file  code16.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%define DOS_SHELL 1
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
code16_start:
    INIT_COMMAND_LINE
    INIT_CONSOLE

    call PROC_CHECK
    call CHECK_MODE
    
    cli                    ; Interrupts aus

    ; Segmentregister vorbereiten (Real Mode)
    xor ax, ax
    mov ds, ax
    mov es, ax
    mov ss, ax
    mov sp, 0x7C00         ; einfachen Stack setzen
    
    ; -----------------------------
    ; GDT-Deskriptor vorbereiten
    ; -----------------------------
    ; Wir müssen die lineare Basisadresse der GDT in den GDTR schreiben
    ; In Real Mode können wir trotzdem 32-Bit Register benutzen (mit 66h Prefix)
    
    ; CS-Segmentbasis berechnen (Segment << 4)
    mov   ax, cs
    movzx eax, ax          ; EAX = CS (Zero-extend)
    shl   eax, 4           ; EAX = CS * 16 = lineare Basis des Codesegments
    
    add eax, PTR16(_cA_gdt) ; GDT liegt irgendwo in unserem Code, also Basis + Offset
    mov  [PTR16(_cA_gdt_descriptor)+2], eax  ; GDT-Basis in Descriptor schreiben
    
    lgdt [PTR16(_cA_gdt_descriptor)]  ; GDTR laden
    
    ; -----------------------------
    ; Protected Mode einschalten
    ; -----------------------------
    mov eax, cr0
    or  eax, 1             ; PE-Bit (Bit 0) setzen
    mov cr0, eax
    
    ; Weit-Sprung in 32-Bit Code-Segment, um Pipeline zu leeren und CS zu setzen
    jmp 0x08:protected_mode_entry  ; 0x08 = 1. GDT-Code-Deskriptor
    
; --------------------------------
; Ab hier 32-Bit Code
; --------------------------------
[BITS 32]

protected_mode_entry:
    ; Segmentregister auf 32-Bit-Data-Deskriptor setzen
    mov ax, 0x10           ; 0x10 = 2. GDT-Eintrag = Data-Segment
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax

    ; Stack für 32-Bit setzen
    mov esp, 0x9FC00       ; irgendeine hohe Adresse im Low-Memory-Bereich

    ; Kleine Demo: Text direkt in den VGA-Textmodus-Speicher schreiben (0xB8000)
    mov edi, 0xB8000       ; VGA-Textmodus-Adresse
    mov eax, 0x1F201F20    ; zwei Zeichen ' ' (Space) mit Attribut 0x1F (weiß auf blau)
                           ; hier nur als Dummy, um Format zu zeigen

    ; Beispieltext "PM32" schreiben
    mov byte [edi], 'P'
    mov byte [edi+1], 0x1F
    mov byte [edi+2], 'M'
    mov byte [edi+3], 0x1F
    mov byte [edi+4], '3'
    mov byte [edi+5], 0x1F
    mov byte [edi+6], '2'
    mov byte [edi+7], 0x1F

    .hang:
    jmp .hang              ; Endlosschleife, damit man den Zustand sieht
    
    ret

; -----------------------------------------------------------------------------
; \brief check, if a compatible 80386 CPU is present on the system ...
; -----------------------------------------------------------------------------
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

; -----------------------------------------------------------------------------
; \brief check, if we in real mode or not ...
; -----------------------------------------------------------------------------
CHECK_MODE
    mov eax, cr0            ; get CR0 to EAX
    and al, 1               ; check if PM bit is set
    jnz not_real_mode		; yes, it is, so exit
    ret                     ; no, it isn't, return
    
    not_real_mode:
    PUTS_COLOR norealmode, 3
    DOS_Exit 1
    ret
    
is_version_1:
    ;mov [PTR16(_cA_db_version)], byte 3
    SET_CURSOR 10, 1
    PUTS_COLOR 'argv1 == argv1', 0x0F
    ret
is_version_2:
    ;mov [PTR16(_cA_db_version)], byte 4
    SET_CURSOR 10, 2
    PUTS_COLOR 'argv1 == argv2', 0x0E
    ret
is_version_3:
    ;mov [PTR16(_cA_db_version)], byte 5
    SET_CURSOR 10, 3
    PUTS_COLOR 'argv1 == "abcd"', 0x0F
    ret
is_version_4:
    ;mov [PTR16(_cA_db_version)], byte 6
    SET_CURSOR 10, 4
    PUTS_COLOR 'argv2 == 1234', 0xF
    ret
is_version_5:    
    ;mov [PTR16(_cA_db_version)], byte 6
    SET_CURSOR 10, 5
    PUTS_COLOR '"abcd" == "abcd"', 0xF
    ret

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
