;---------------------------------------------------
; \file  wim16NEhdr.inc
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
;---------------------------------------------------

%ifidni PLATFORM,NE
org 0
bits 16
section .text
; ---- Header-Layout-Marker
mz_hdr:
    db 'M','Z'                          ; e_magic
    dw ( stub_end - $$) % 512           ; e_cblp
    dw ((stub_end - $$) + 511) / 512    ; e_cp
    dw 0                                ; e_crlc (keine Relocs)
    dw ((stub_entry  - $$) +  15) / 16  ; e_cparhdr (Headergröße in Paragraphen)
    dw 0                                ; e_minalloc
    dw 0xFEFE                           ; e_maxalloc (so viel wie möglich)
    dw 0                                ; e_ss
    dw 0xFFFE                           ; e_sp (kleiner Stack)
    dw 0                                ; e_csum
    dw 0                                ; e_ip  (Code startet bei 0 im Image)
    dw 0                                ; e_cs
    dw mz_reloc - $$                    ; e_lfarlc (Reloc-Tabelle: leer)
    ;dw 0x0040                          ; e_lfarlc  <-- fest im Header
    dw 0                                ; e_ovno
    times     4  dw 0                   ; e_res[4]
    dw    7274, 8279                    ; e_oemid, e_oeminfo
    times    10  dw 0                   ; e_res2[10]
    dd ne_hdr - mz_hdr                  ; e_lfanew -> Offset des PE-Headers
    
end_dos_header equ ($ - mz_hdr)
; Reloc-Tabelle (leer), aber im Headerbereich!
mz_reloc:                               ; == 0x40

;---------------------------------------------------
; DOS 16 bit stub
;---------------------------------------------------
align 16                                ; <-- sicherstellen, dass mz_image auf Absatzgrenze startet
mz_image:

;---------------------------------------------------
; 16-bit Stub-Entry bei e_cs:e_ip = 0:0 (ab mz_image)
;---------------------------------------------------
incbin 'kernel.bin'

stub_entry:

;---------------------------------------------------
; Windows 3.1 16 bit stub
;---------------------------------------------------
align 16

; ---------------------------
; NE header
; ---------------------------
ne_hdr:
    db 'N','E'              ; Signature
    db 5,1                  ; Linker ver/rev (beliebig konsistent)
    dw entry_table - ne_hdr ; Offset EntryTable (relativ zu ne_hdr)
    dw entry_table_len      ; Länge EntryTable
    dw 0                    ; File flags (TODO: Windows-App, etc.)
    dw 0                    ; Autodata seg index (TODO: z.B. 2 für DGROUP)
    dw heap_size            ; Initial heap size (TODO)
    dw stack_size           ; Initial stack size (TODO)
    dw ip_start             ; IP
    dw cs_start             ; CS (Segmentindex-1? Achtung: NE nutzt Selector-Index, nicht File-Offset!)
    dw sp_start             ; SP
    dw ss_start             ; SS (Segmentindex-1)
    dw seg_count            ; Anzahl Segmente
    dw modref_count         ; Anzahl Modul-Refs
    dw nonres_tab_len       ; Länge NonResTable
    dw seg_table_off        ; Offset Segmenttabelle (rel. zu ne_hdr)
    dw res_table_off        ; Offset ResourceTable (rel.)
    dw restab_off           ; Offset ResidentNameTable (rel.)
    dw modref_off           ; Offset ModuleRefTable (rel.)
    dw impname_off          ; Offset ImportedNames (rel.)
    dw entry_table - ne_hdr ; EntryTable off (nochmal, je nach Doku)
    dd nonres_tab_file_off  ; Dateioffset NonResTable
    dw 0                    ; nmovent (movable entries) – meist 0 ok
    dw align_shift          ; Alignment shift count (z.B. 4 => 16 Bytes)
    dw 0,0,0,0              ; weitere Felder (Target OS Flags etc., je nach Bedarf 0)

stub_end:
; ---------------------------
; Segment table (seg_count Einträge)
; Jeder Eintrag: Offset(in units), Größe(bytes), Flags, MinAlloc
; ---------------------------
seg_table:
seg1_code:
    dw seg1_off_units       ; Offset des CODE-Images / alignment units
    dw seg1_len_bytes       ; Länge in Bytes (0 => 64k)
    dw seg1_flags           ; Flags (CODE, FIXED/MOVEABLE, PRELOAD usw.)
    dw 0                    ; MinAlloc

seg2_data:
    dw seg2_off_units
    dw seg2_len_bytes
    dw seg2_flags           ; DATA, evtl. PRELOAD, SHARED?
    dw 0

; ---------------------------
; (Optional) Resource table
; ---------------------------
res_table:
    ; leer -> einfach 0

; ---------------------------
; Resident Name Table (z.B. Modulname)
; Format: len, chars..., len=0
; ---------------------------
resident_names:
    db 5, 'H','E','L','L','O'
    db 0
    
; ---------------------------
; Module Reference Table (Indizes in Imported Names)
; ---------------------------
modref_table:
    ; z.B. 1 -> "KERNEL", 2 -> "USER", 3 -> "GDI"
    dw 1
    dw 2
    dw 3

; ---------------------------
; Imported Names Table (Längenpräfixe)
; ---------------------------
impnames:
    db 6,'K','E','R','N','E','L'
    db 4,'U','S','E','R'
    db 3,'G','D','I'
    ; danach Funktionsnamen (z.B. 11,'M','e','s','s','a','g','e','B','o','x',0?) – je nach Konvention ohne 0-Terminierung, sondern mit Längenbyte

; ---------------------------
; Entry Table (Bundles + Terminator)
; ---------------------------
entry_table:
    ; Bundle: 1 Eintrag, für Segment 1 (CODE), Offset ip_entry
    ; (Striktes Format beachten – hier nur Platzhalter!)
    db 1, 1, 0              ; Count, SegIndex, Flags (Platzhalter)
    dw ip_entry             ; Offset im Seg1
entry_table_end:
    db 0                    ; Terminator
entry_table_len equ entry_table_end - entry_table

; ---------------------------
; Non-Resident Name Table (am Dateiende)
; ---------------------------
nonres_start:
    db 0                    ; leer

; ---------------------------
; Segment-Images (ausgerichtet)
; ---------------------------
align 16
seg1_image:
ip_entry:
    ; Hier beginnt deine Startadresse (CS:IP)
    ; Beispiel: direkt zum Ende (keine API)
    mov ax, 0
    ; ... normalerweise: WinInit / WinMain rufen (dazu Imports + Fixups!)
    retf                    ; Platzhalter

seg1_end:
seg1_len_bytes  equ seg1_end - seg1_image
seg1_off_units  equ (seg1_image - mz_hdr) >> align_shift

align 16
seg2_image:
    ; DATA / DGROUP
seg2_end:
seg2_len_bytes  equ seg2_end - seg2_image
seg2_off_units  equ (seg2_image - mz_hdr) >> align_shift

; ---------------------------
; Konstanten/Felder (Beispielwerte – rechne sie sauber aus)
; ---------------------------
align_shift     equ 4
seg_count       equ 2
modref_count    equ 3
heap_size       equ 1024
stack_size      equ 2048
cs_start        equ 0          ; (Segmentindex-1) -> für seg1 = 0
ss_start        equ 1          ; (Segmentindex-1) -> für seg2 = 1
ip_start        equ ip_entry
sp_start        equ stack_size  ; oder Offset in DATA
nonres_tab_len  equ 0
nonres_tab_file_off equ nonres_start - mz_hdr

seg1_flags      equ 0           ; TODO: CODE|FIXED/PRELOAD etc.
seg2_flags      equ 0           ; TODO: DATA|PRELOAD etc.

seg_table_off   equ seg_table - ne_hdr
res_table_off   equ res_table - ne_hdr
restab_off      equ resident_names - ne_hdr
modref_off      equ modref_table - ne_hdr
impname_off     equ impnames - ne_hdr

%endif
