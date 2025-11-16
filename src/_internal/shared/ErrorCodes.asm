; -----------------------------------------------------------------------------
; \file  ErrorCodes.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------

DOS_handle_error_code:
    COMPARE ax, 0x01, _open_error_01
    COMPARE ax, 0x02, _open_error_02
    COMPARE ax, 0x03, _open_error_03
    COMPARE ax, 0x04, _open_error_04
    COMPARE ax, 0x05, _open_error_05
    COMPARE ax, 0x06, _open_error_06
    COMPARE ax, 0x0C, _open_error_0C
    COMPARE ax, 0x0F, _open_error_0F
    COMPARE ax, 0x10, _open_error_10
    COMPARE ax, 0x11, _open_error_11
    COMPARE ax, 0x12, _open_error_12
    ; ----
    _open_error_01:
        PUTS_COLOR open_error_01, ATTR_DOS_ERROR
        mov   cx, 0x01
        jmp _open_exit
    _open_error_02:
        PUTS_COLOR open_error_02, ATTR_DOS_ERROR
        mov   cx, 0x02
        jmp _open_exit
    _open_error_03:
        PUTS_COLOR open_error_03, ATTR_DOS_ERROR
        mov   cx, 0x03
        jmp _open_exit
    _open_error_04:
        PUTS_COLOR open_error_04, ATTR_DOS_ERROR
        mov   cx, 0x04
        jmp _open_exit
    _open_error_05:
        PUTS_COLOR open_error_05, ATTR_DOS_ERROR
        mov   cx, 0x05
        jmp _open_exit
    _open_error_06:
        PUTS_COLOR open_error_06, ATTR_DOS_ERROR
        mov   cx, 0x06
        jmp _open_exit
    _open_error_0C:
        PUTS_COLOR open_error_0C, ATTR_DOS_ERROR
        mov   cx, 0x0C
        jmp _open_exit
    _open_error_0F:
        PUTS_COLOR open_error_0F, ATTR_DOS_ERROR
        mov   cx, 0x0F
        jmp _open_exit
    _open_error_10:
        PUTS_COLOR open_error_10, ATTR_DOS_ERROR
        mov   cx, 0x10
        jmp _open_exit
    _open_error_11:
        PUTS_COLOR open_error_11, ATTR_DOS_ERROR
        mov   cx, 0x11
        jmp _open_exit
    _open_error_12:
        PUTS_COLOR open_error_12, ATTR_DOS_ERROR
        mov   cx, 0x12
        jmp _open_exit
        
        PUTS_COLOR open_error_nd, ATTR_DOS_ERROR
        mov   cx, 0x32
    _open_exit:
        DOS_Exit cx
    ret
