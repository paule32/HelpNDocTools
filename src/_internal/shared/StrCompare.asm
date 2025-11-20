; -----------------------------------------------------------------------------
; \file  StrCompare.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

; -----------------------------------------------------------------------------
; \brief strcmp - compares two 0-terminated strings: DS:SI vs. ES:DI.
; \param 1. dst > DI
; \param 2. src > SI
; \return AL = 1 (found/same)
;         AL = 0 (not same)
; -----------------------------------------------------------------------------
string_compare:
    push si             ; save src > si
    push di             ; save dst > di
    
    SET_CURSOR 1, 1
    PUTS_COLOR SI, 6
    PUTS_COLOR DI, 1

    .next:
    mov  al, [si]       ; get src byte
    mov  bl, [di]       ; get dst byte
    
    test al, al         ; found terminator ?
    jz   .term          ; yes -> end
    test bl, bl         ; found terminator ?
    jz   .term          ; yes -> end
    
    cmp  al, bl         ; dst == src ?
    jne  .not_equal     ; no ?
    
    inc  si             ; next src pos.
    inc  di             ; next dst pos.
    jmp  .next          ; check
    
    .term:
    mov  al, 0          ; found/same, ret
    pop  di             ; restore di
    pop  si             ; restore si
    ret                 ; return to caller
    
    .not_equal:
    mov  al, 1          ; not found, ret
    pop  di             ; restore < di
    pop  si             ; restore < si
    ret                 ; return to caller
