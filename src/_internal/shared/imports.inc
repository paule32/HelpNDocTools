; -----------------------------------------------------------------------------
; \file  imports.inc
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a tiny MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
; .idata (Imports)
; -----------------------------------------------------------------------------
    times (IDATA_RAW_PTR - ($ - $$)) db 0
idata_start:

; -----------------------------------------------------------------------------
; Import Directory (KERNEL32 + USER32) + Terminator
; -----------------------------------------------------------------------------
MAKE_IMPORT import_dir, kernel32, user32, msvcrt

; -----------------------------------------------------------------------------
; INTs (OriginalFirstThunk)
; -----------------------------------------------------------------------------
MAKE_INT INT_win32_kernel32, KERNEL32_FUNCS
MAKE_INT INT_win32_user32, USER32_FUNCS
MAKE_INT INT_win32_msvcrt, MSVCRT_FUNCS

; -----------------------------------------------------------------------------
; IATs (FirstThunk)
; -----------------------------------------------------------------------------
iat_start:
MAKE_IAT kernel32, KERNEL32_FUNCS
MAKE_IAT user32, USER32_FUNCS
MAKE_IAT msvcrt, MSVCRT_FUNCS
iat_end:

; -----------------------------------------------------------------------------
; hintnames (ASCII)
; -----------------------------------------------------------------------------
HNSTR KERNEL32_FUNCS
HNSTR USER32_FUNCS
HNSTR MSVCRT_FUNCS

; -----------------------------------------------------------------------------
; DLL names
; -----------------------------------------------------------------------------
dll_win32_kernel32: db 'kernel32.dll',0
dll_win32_user32:   db 'user32.dll',0
dll_win32_msvcrt:   db 'msvcrt.dll',0

idata_end:
; -----------------------------------------------------------------------------
