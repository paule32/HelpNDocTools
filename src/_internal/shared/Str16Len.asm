; -----------------------------------------------------------------------------
; \file  Str16Len.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

; -----------------------------------------------------------------------------
; \brief  get the 16 bit length of a 0-terminated string
; \param  Input:  ES:SI -> "0"-terminierter String
; \return Output: AX = Länge (ohne '0')
; -----------------------------------------------------------------------------
DOSStrLen:
    push di             ; save DI
    mov  di, si         ; DI = SI
    mov  ax, 0          ; reset counter
    
    next:
    mov  al, [si]       ; get character
    cmp  al, 0          ; found 0-terminator ?
    je   done           ; yes -> .done
    
    inc  si
    inc  ax
    jmp  next
    
    done:
    pop     di
    ret
