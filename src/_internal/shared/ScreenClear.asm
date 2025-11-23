; -----------------------------------------------------------------------------
; \file  ScreenClear.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%define TEXT_VRAM 0xb8000

dos_screen_clear:
%if DOS_SHELL == 1
    bits 16
    section .text
    push ds
    mov  ax, 0xb800
    mov  es, ax

    xor  di, di         ; Offset 0
    
    ; default size is:  80x25
    mov  al, bl         ; AL = 25
    mul  bh             ; AX = AL * BH = 25 * 80 = 2000 (0x07D0)
    mov  cx, ax         ; 2000 chars
    
    ; color
    mov  ax, 0x0720     ; AL=' ' (20h), AH=07h (hellgrau auf schwarz)

    .fill:
    stosw               ; schreibt AX -> ES:[DI], DI+=2
    loop .fill

    pop  ds

    SET_CURSOR 0, 0
    
    ret
%elif DOS_SHELL == 32
    bits 32
    section .text
    mov edi, 0xb8000
    mov [PutStr_Ptr], edi
    mov ecx, 40 * 25
    mov eax, 0x07200720
    rep stosd
    ret
%endif
