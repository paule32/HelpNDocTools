;---------------------------------------------------
; \file  doshdr.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
;---------------------------------------------------
; DOS-Header
;---------------------------------------------------
%if DOS_SHELL == 1
bits 16
org 0
section .text
; ---- Header-Layout-Marker
dos_start:
    db 'M','Z'                          ; e_magic
    dw ( stub_end - $$) % 512           ; e_cblp
    dw ((stub_end - $$) + 511) / 512    ; e_cp
    dw 0                                ; e_crlc (keine Relocs)
    dw ((stub_entry  - $$) +  15) / 16  ; e_cparhdr (Headergröße in Paragraphen)
    dw 0                                ; e_minalloc
    dw 0x1000                           ; e_maxalloc (so viel wie möglich)
    dw 0                                ; e_ss
    dw 0xFEFE                           ; e_sp (kleiner Stack)
    dw 1105                             ; e_csum
    dw 0                                ; e_ip  (Code startet bei 0 im Image)
    dw 0                                ; e_cs
    dw mz_reloc - $$                    ; e_lfarlc (Reloc-Tabelle: leer)
    dw 700                              ; e_ovno
    ; ----
    dw 1932
    dw 1949
    dw 1956
    dw 1989
    ;times    4  dw 0                   ; e_res[4]
    ; ----
    
    dw    7274, 8279                    ; e_oemid, e_oeminfo
    
    ; ----
    dw 49152
    dw 31710
    dw 580
    dw 820
    dw 817
    dw 834
    dw 49369
    dw 2234
    dw 326
    dw 0xFEFE
    ;times    10  dw 0                  ; e_res2[10]
    ; ----
    
    %if DOS_SHELL == 64
        dd pe_header                    ; e_lfanew -> Offset des PE-Headers
    %endif
    
end_dos_header equ ($ - dos_start)

; Reloc-Tabelle (leer), aber im Headerbereich!
mz_reloc:                               ; == 0x40

;---------------------------------------------------
; DOS 16 bit stub
;---------------------------------------------------
align 16                                ; <-- sicherstellen, dass mz_image auf Absatzgrenze startet
mz_image:

; ---- 16-bit Stub-Entry bei e_cs:e_ip = 0:0 (ab mz_image)
stub_entry:
incbin 'kernel16.bin'

;align 16
stub_end:
%endif
