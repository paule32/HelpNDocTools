;---------------------------------------------------
; \file  config.inc
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
;---------------------------------------------------
; Configuration file
;---------------------------------------------------
%ifndef DOS_SHELL
    %assign DOS_SHELL 1     ; 1 indicates a console application.
%endif

%ifndef DOS_MODE
    %assign DOS_MODE 16     ; set this to 16 for 16 bit DOS or 64 for win32pe+
%endif
