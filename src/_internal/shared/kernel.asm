VIDEO_MEM EQU 0x0b8000

org 0x110000                    ; Set ORG to address kernel is loaded at

bits 32
kernel_entry:
    ; Write MDP in white on magenta starting on second row, column 0
    mov eax, 0x5f SHL 8 OR 'M'
    mov [VIDEO_MEM+80*2], ax
    mov eax, 0x5f SHL 8 OR 'D'
    mov [VIDEO_MEM+80*2+2], ax
    mov eax, 0x5f SHL 8 OR 'P'
    mov [VIDEO_MEM+80*2+4], ax

    ret
 