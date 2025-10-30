;---------------------------------------------------
; \file  stdlib.inc
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
;---------------------------------------------------

;---------------------------------------
; Routine: IntToString
; Eingabe: RAX = Zahl
;          RDI = Pufferadresse
; Ausgabe: Puffer enthält ASCII-Zeichen
;---------------------------------------
IntToStr:
    ; save stack pointer
    FUNC_ENTER
    
        mov   rcx, 10          ; divisor (remainder = Rest)
        mov   r10, rdi         ; scan Pointer = Anfang des Puffers
        mov   rbx, rdi         ; wir merken uns den Puffer
        
    .find_end:
        cmp   byte [r10], 0
        je    .end_found
        inc   r10
        jmp   .find_end
    .end_found:
        ; rbx zeigt jetzt auf das Nullterminator-Byte
    .convert:
        dec   r10              ; r10 -> letztes belegbares Byte (vor Terminator)
        
        ; Sonderfall: falls Zahl == 0, schreibe '0' und springe zum Ende
        test  rax, rax
        jnz   .convert_loop
        
        mov   byte [r10], '0'
        dec   r10
        jmp   .copy_back
    
    .convert_loop:
        xor   rdx, rdx
        div   rcx
        add   dl, '0'
        mov   [r10], dl         ; schreibe Ziffer
        dec   r10
        test  rax, rax
        jnz   .convert_loop
        
    .copy_back:
        ; nach der Schleife steht rbx *unter* dem ersten Ziffernbyte (oder auf Anfang-1)
        ; setze source = rbx+1, dest = rdi (Anfang des Puffers)
        lea   r8, [r10 + 1]    ; r8 = Quelle (erste Ziffer)
        mov   r9, rdi          ; r9 = Ziel (Anfang des Puffers) in rdx temporär
        
    .copy_loop:
        mov   al, [r8]
        mov   [r9], al
        inc   r8
        inc   r9
        cmp   al, 0
        jne   .copy_loop

.done:
    FUNC_LEAVE

;--------------------------------------
; Hilfsfunktion: strlen
; RCX = string
;--------------------------------------
strlen:
    xor     rax, rax
.next_char:
    cmp     byte [rcx+rax], 0
    je      .done
    inc     rax
    jmp     .next_char
.done:
    ret

%include 'windos.inc'
