;---------------------------------------------------
; \file  bitsXX.inc
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
;---------------------------------------------------
default rel

%define IMAGEBASE    0x0000000140000000
%define FILEALIGN    0x200      ; 512
%define SECTALIGN    0x1000

%define IMAGE_BASE   IMAGEBASE

