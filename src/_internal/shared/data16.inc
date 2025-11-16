; -----------------------------------------------------------------------------
; \file  data16.asm
; \note  (c) 2025 by Jens Kallup - paule32
;        all rights reserved.
;
; \desc  Create a dBASE MS-Windows 11 64-bit Pro EXE.
; -----------------------------------------------------------------------------
data16_start:

msg:            db "This program requieres MS-Windows.$",0
msgErr:         db 'Open error AX=', '$'


ASTR dos_cap2A,  "ein Text", 0
ASTR dos_prompt, "Eingabe:       ", 0

crlf:            db 13,10,'$'
dos_color:       db 0x07

; -----------------------------------------------------------------------------
; Buffer-Struktur für AH=0Ah:
; [0] = maxlen, [1] = len(out), [2..] = Text, danach CR
; -----------------------------------------------------------------------------
BUFSZ            equ 64
_cA_dos_buffer:  db BUFSZ-2       ; Max. Eingabezeichen (ohne die 2 Verwaltungsbytes)
                 db 0             ; tatsächliche Länge (OUT)
                 times BUFSZ-2 db 0
dos_readln_flag: db 0

; -----------------------------------------------------------------------------
; \brief DOS console settings ...
; -----------------------------------------------------------------------------
dos_xpos:           db 0      ; current text cursor column
dos_ypos:           db 0      ; current text cursor row
dos_page:           db 0      ; current video page

; -----------------------------------------------------------------------------
; dBASE data ...
; -----------------------------------------------------------------------------
_cA_DBFNAME:        db 'DATA.DBF',0

msgTitle:           db 'dBASE IV DBF Header',13,10,'$'
msgUsage:           db 'Usage: DBFHEAD <datei.dbf>',13,10,'$'
msgOpenErr:         db 'Fehler: Datei kann nicht geoeffnet werden.',13,10,'$'
msgReadErr:         db 'Fehler: Lesen fehlgeschlagen.',13,10,'$'
msgVer:             db 'Version (hex): $'
msgDate:            db 'Datum (YY-MM-DD): $'
msgRecs:            db 'Anzahl Datensaetze (hex): $'
msgHdr:             db 'Headerlaenge (bytes): $'
msgRec:             db 'Satzlaenge (bytes): $'
msgMDX:             db 'MDX-Flag (hex): $'
msgLang:            db 'Language Driver ID (hex): $'
msgFields:          db 'Felder:',13,10,'$'
msgNoFields:        db 'Keine Felder gefunden.',13,10,'$'
msgFieldN:          db '  Feld #$'
msgColonSp:         db ': $'
msgCommaSp:         db ', $'
msgSlash:           db ' / $'

msg_usage:          db 'Usage: DBFMAKE <type:3|4> <CREATE|APPEND> <C|I|F|B|D|T> <feldname> <feldlaenge>$', 0
msg_badargs:        db 'Fehler: Argumente ungueltig.$',0
msg_openfail:       db 'Fehler: Datei kann nicht geoeffnet/erstellt werden.$',0
msg_ver_mismatch:   db 'Fehler: DBF-Typ passt nicht zur Datei.$',0
msg_append_recs:    db 'APPEND abgelehnt: Datei enthaelt Datensaetze (nicht unterstuetzt).$',0
msg_ioerr:          db 'I/O-Fehler.$',0
msg_badheader:      db 'Fehler: ungueltiger Header/Felddeskriptor.$',0
msg_not_supported:  db 'Nicht unterstuetzt: Feldtyp nur mit Typ 4.$',0
_cA_msg_ok_create:      db 'OK: Neue DBF mit einem Feld erstellt (DATA.DBF).$',0
msg_ok_append:      db 'OK: Feld an bestehende leere DBF angehaengt.$',0
msg_fieldexists:    db 'Hinweis: Feld bereits vorhanden; keine Aenderung vorgenommen.$',0

str_CREATE:         db 'CREATE',0
str_APPEND:         db 'APPEND',0

; ---- Daten ----
_cA_noargs_msg:     db 'no args.', 0

; --- Daten ---
mod_filename:    db 'MODUL1.BIN',0
mod_hFile:       dw 0
mod_seg_ovl:     dw 0
mod_fsize_lo:    dw 0
mod_fsize_hi:    dw 0

mod_msg:         db 'Hallo vom Loader!$'
mod_msg_len:     equ ($ - msg)

hdr_len:            dw 0
rec_len:            dw 0

data16_end:

%define DOS_SHELL 0
