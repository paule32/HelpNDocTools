;---------------------------------------------------
; \file  winproc.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
;---------------------------------------------------
%if DOS_MODE == 64
bits 64

WndProc:
    AddShadow
    MESSAGE WM_CLOSE,wm_close
    MESSAGE WM_ERASEBKGND,wm_erasebkgnd
    DefWindowProcW
    DelShadow
    jmp [rax]
.wm_erasebkgnd:
    AddShadow 48
    mov [rsp+32],rcx
    mov [rsp+40],r8
    lea rdx,[rsp+16]
    mov rcx,[rsp+32]
    CALL_IAT GetClientRect
    mov rcx,[rsp+32]
    mov rdx,GCLP_HBRBACKGROUND
    CALL_IAT GetClassLongPtrW
    mov rcx,[rsp+40]
    lea rdx,[rsp+16]
    mov r8,rax
    CALL_IAT FillRect
    Return 1
    DelShadow 48
    DelShadow
    ret
.wm_close:
    Zero ecx
    CALL_IAT PostQuitMessage
    DelShadow
    Zero eax
    ret
%endif
