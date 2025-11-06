;---------------------------------------------------
; \file  doshdr.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
;---------------------------------------------------
; DOS-Header
;---------------------------------------------------

org 0
bits 16

; ---- Header-Layout-Marker
dos_start:
    db 'M','Z'                          ; e_magic
    dw ( file_end - $$) % 512          ; e_cblp
    dw ((file_end - $$) + 511) / 512   ; e_cp
    dw 0                                ; e_crlc (keine Relocs)
    dw ((stub_entry  - $$) +  15) / 16    ; e_cparhdr (Headergröße in Paragraphen)
    dw 0                                ; e_minalloc
    dw 0xFFFF                           ; e_maxalloc (so viel wie möglich)
    dw 0                                ; e_ss
    dw 0xFFFE                           ; e_sp (kleiner Stack)
    dw 0                                ; e_csum
    dw 0                                ; e_ip  (Code startet bei 0 im Image)
    dw 0                                ; e_cs
    ;dw mz_reloc - $$                   ; e_lfarlc (Reloc-Tabelle: leer)
    dw 0x0040                           ; e_lfarlc  <-- fest im Header
    dw 0                                ; e_ovno
    times 4 dw 0                        ; e_res[4]
    dw 0, 0                             ; e_oemid, e_oeminfo
    times 10 dw 0                       ; e_res2[10]
    dd pe_header                        ; e_lfanew -> Offset des PE-Headers
    
end_dos_header equ ($ - dos_start)

; Reloc-Tabelle (leer), aber im Headerbereich!
times (0x40 - ($ - $$)) db 0                   ; bis 0x40 auffüllen
mz_reloc:                                      ; == 0x40
    
;align 16                                ; <-- sicherstellen, dass mz_image auf Absatzgrenze startet
mz_image:

; ---- 16-bit Stub-Entry bei e_cs:e_ip = 0:0 (ab mz_image)
stub_entry:
    
%include 'code16.asm'
%include 'data16.inc'

align 16
stub_end:
