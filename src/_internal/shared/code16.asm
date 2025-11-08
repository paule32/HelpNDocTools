; -----------------------------------------------------------------------------
; \file  code16.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
%define DOS_SHELL 1
code16_start:

STACK32_TOP  EQU 0x200000
KERNEL_START EQU 0x110000
KERNEL_SIZE  EQU 8192

%define CODESEL32 (gdt_code - gdt_start)
%define DATASEL32 (gdt_data - gdt_start)

%define CODESEL16 (gdt16_code - gdt_start)
%define DATASEL16 (gdt16_data - gdt_start)

    ; Kein Windows -> Meldung ausgeben
    push cs
    pop  ds              ; data segment == code segment

    mov dx, kernel_file
    int 0x21                    ; Open KERNEL.BIN
    mov bx, ax                  ; BX = file handle
    jnc .read                   ; No Error? Read file
    
    
    ; AX=1600h: Windows-Check
    mov ax, 0x1600
    int 0x2F
    or  al, al
    jnz .ok              ; AL!=0 => irgendein Windows aktiv
    
    .read:
    WRITE_CON_A msg
    WRITE_CON_A msg
    
    .ok:
    .exit:
    mov  ax, 0x4C00      ; ExitCode=0
    int  0x21

; -----------------------------------------------------------------------------
; 16-bit protected mode entry point and code
; -----------------------------------------------------------------------------
pm16_entry:
    mov ax, DATASEL16           ; Set all data segments to 16-bit data selector
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax

    mov eax, cr0                ; Disable protected mode
    and eax, ~0x80000001        ; Disable paging (bit 31) and protected mode (bit 0)
                                ; The kernel will have to make sure the GDT is in
                                ;     a 1:1 (identity mapped page) as well as lower memory
                                ;     where the DOS program resides before returning
                                ;     to us with a RETF
    mov cr0, eax

    push cx                     ; Return to the real_mode code
    push real_mode_entry        ;     with the original CS value (in CX)
    retf

; -----------------------------------------------------------------------------
; 16-bit real mode entry point
; -----------------------------------------------------------------------------
real_mode_entry:
    xor esp, esp                ; Clear all bits in ESP
    mov ss, dx                  ; Restore the real mode stack segment
    lea sp, [bp+8]              ; Restore real mode SP
                                ; (+8 to skip over 32-bit entry point and Selector that
                                ;     was pushed on the stack in real mode)
    pop gs                      ; Restore the rest of the real mode data segment
    pop fs
    pop es
    pop ds
    lidt [idtr]                 ; Restore the real mode interrupt table
    sti                         ; Enable interrupts
    
; -----------------------------------------------------------------------------
; Code that will run in 32-bit protected mode
;
; Upon entry the registers contain:
;     EDI = 16-bit protected mode entry (linear address)
;     ESI = Kernel memory buffer (linear address)
;     EBX = code_32bit (linear address)
;     ECX = DOS real mode code segment
; -----------------------------------------------------------------------------
align 4
bits 32

code_32bit:
    mov ebp, esp                ; Get current SS:ESP
    mov edx, ss

    cld                         ; Direction flag forward
    mov eax, DATASEL32          ; Set protected mode selectors to 32-bit 4gb flat
    mov ds, ax
    mov es, ax
    mov fs, ax
    mov gs, ax
    mov ss, ax
    mov esp, STACK32_TOP        ; Should set ESP to a usable memory location
                                ; Stack will be grow down from this location

    ; Build linear address and selector on stack for RETF to return to
    push CODESEL16              ; Put 16-bit protected mode far entry point 0x18:pm16_entry
    push edi                    ;     on stack as a return address (linear address)

    push edx                    ; Save EDX, EBP, ECX
    push ebp
    push ecx

    mov edi, KERNEL_START       ; EDI = linear address where PM code will be copied
    mov ecx, KERNEL_SIZE        ; ECX = number of bytes to copy
    rep movsb                   ; Copy all code/data from kernel buffer to KERNEL_START
    call CODESEL32:KERNEL_START ; Absolute jump to relocated code

    pop ecx                     ; ECX = Real mode code segment
    pop ebp                     ; Recover old SS:SP into EDX:EBP
    pop edx
    retf

code16_end:

;kernell_mem: times 1024 db 0
