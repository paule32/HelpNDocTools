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

dos_xpos:        db 0
dos_ypos:        db 0
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

msg_usage:          db 'Usage: DBFMAKE <type:3|4> <CREATE|APPEND> <C|I|F|B|D|T> <feldname> <feldlaenge>', 0
msg_badargs:        db 'Fehler: Argumente ungueltig.',0
msg_openfail:       db 'Fehler: Datei kann nicht geoeffnet/erstellt werden.',0
msg_ver_mismatch:   db 'Fehler: DBF-Typ passt nicht zur Datei.',0
msg_append_recs:    db 'APPEND abgelehnt: Datei enthaelt Datensaetze (nicht unterstuetzt).',0
msg_ioerr:          db 'I/O-Fehler.',0
msg_badheader:      db 'Fehler: ungueltiger Header/Felddeskriptor.',0
msg_not_supported:  db 'Nicht unterstuetzt: Feldtyp nur mit Typ 4.',0
_cA_msg_alloc_error: db 'memory fail.', 0
_cA_msg_ok_create:      db 'OK: Neue DBF mit einem Feld erstellt (DATA.DBF).',0
msg_ok_append:      db 'OK: Feld an bestehende leere DBF angehaengt.',0
msg_fieldexists:    db 'Hinweis: Feld bereits vorhanden; keine Aenderung vorgenommen.',0

str_CREATE:         db 'CREATE',0
str_APPEND:         db 'APPEND',0

; ---- Daten ----
_cA_noargs_msg:     db 'no args.', 0
_cA_cmd_buf:        times 130 db 0             ; max. 127 + '$' + Reserve

hFile:              dw 0
g_type:             dw 0
g_cmd:              db 0
g_ftype:            db 0
g_ftype_mapped:     db 0
g_flen:             dw 0
g_year:             dw 0
g_month:            db 0
g_day:              db 0

hdr_len:            dw 0
rec_len:            dw 0

tokbuf:             db 64   dup(0)
fldname:            db 12   dup(0)

header:             db 32   dup(0)
;fdescbuf:           db 4096 dup(0)
fdbuf_size:         dw 0
tempdesc:           db 32   dup(0)

verByte:     db 0
yy:          db 0
mm:          db 0
dd:          db 0
mdx:         db 0
lang:        db 0
rec32:       dw 0,0

buf_hex:    db 6 dup(0)            ; 4 Hex-Zeichen + '$' + Reserve
buf_dec:    db 7 dup(0)            ; 5 Dezimal-Zeichen + '$' + Reserve

filename:    db 128  dup (0)
_cA_fdbuf:
fdbuf:       db 2048 dup (0)
_cA_namebuf: db 16   dup (0)
; -----------------------------------------------------------------------------

buf_seg:   dw 0
size_lo:   dw 0
size_hi:   dw 0

data16_end:

%define DOS_SHELL 0
