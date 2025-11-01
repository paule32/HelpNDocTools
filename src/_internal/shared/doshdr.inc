;---------------------------------------------------
; \file  doshdr.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
;---------------------------------------------------
; DOS-Header
;---------------------------------------------------

;---------------------------------------------------
; Größen des reinen Stubs (Header+Code) – 'stub_end'
; steht ganz unten
;---------------------------------------------------
%define STUB_SIZE   (stub_end - $$)
%define STUB_PAGES  ((STUB_SIZE + 511) / 512)
%define STUB_LAST   (STUB_SIZE % 512)   ; 0 => "512"
%define HDR_PARAS   (((mz_image - $$) + 15) / 16)

dos_start:
    db 'M','Z'                ; e_magic
    dw STUB_LAST              ; e_cblp
    dw STUB_PAGES             ; e_cp
    dw 0                      ; e_crlc (keine Relocs)
    dw HDR_PARAS              ; e_cparhdr (Headergröße in Paragraphen)
    dw 0                      ; e_minalloc
    dw 0xFFFF                 ; e_maxalloc (so viel wie möglich)
    dw 0                      ; e_ss
    dw 0xFFFE                 ; e_sp (kleiner Stack)
    dw 0                      ; e_csum
    dw 0                      ; e_ip  (Code startet bei 0 im Image)
    dw 0                      ; e_cs
    dw mz_reloc - $$          ; e_lfarlc (Reloc-Tabelle: leer)
    dw 0                      ; e_ovno
    times 4 dw 0              ; e_res[4]
    dw 0, 0                   ; e_oemid, e_oeminfo
    times 10 dw 0             ; e_res2[10]
    dd pe_header              ; e_lfanew -> Offset des PE-Headers

mz_reloc:                     ; (keine Einträge)
mz_image:

;%include 'code16.asm'
;%include 'data16.inc'

stub_end:
