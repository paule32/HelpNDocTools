# prg_builder.py
from __future__ import annotations

LOAD_ADDR = 0x0801  # BASIC-Start in Variante A

def _le16(x: int) -> bytes:
    return bytes((x & 0xFF, (x >> 8) & 0xFF))

def build_basic_sys_stub(code_start: int, line_number: int = 10) -> bytes:
    """
    Baut ein einzeiliges BASIC-Programm:
      10 SYS <code_start>
    Rückgabe: reiner BASIC-Inhalt (ohne PRG-Header-Zweibyte-Ladeadresse).
    """
    # Inhalt: [TOKEN_SYS=0x9E] " " Ziffern ... 0x00 (Zeilenende)
    text = f" SYS {code_start}"  # führendes Leerzeichen ist ok/üblich
    content = bytes([0x9E]) + text.encode("ascii") + b"\x00"

    # Link zur nächsten Zeile berechnen: LOAD_ADDR + (Zeilenkopf + Inhalt)
    # Zeilenformat: [link_lo, link_hi, line_lo, line_hi, <content>, 0x00]
    body_len = 2 + 2 + len(content)  # link + line + content
    next_addr = LOAD_ADDR + body_len

    line = bytearray()
    line += _le16(next_addr)
    line += _le16(line_number)
    line += content

    # Programmende: Null-Link (0x0000)
    end = b"\x00\x00"
    return bytes(line) + end

def build_single_segment_prg(assembled_code: bytes) -> bytes:
    """
    Erzeugt ein .prg mit:
      - BASIC @ $0801: 10 SYS <code_start>
      - Code direkt dahinter (gleiche Ladeadresse $0801)
    Achtung: PRG-Header (2 Bytes Ladeadresse) nur EINMAL vorne!
    """
    basic = build_basic_sys_stub(code_start=0)  # Platzhalter; wir berechnen gleich neu
    # Erstmal nur BASIC bauen, um Länge zu kennen:
    basic_len = len(basic)
    code_start = LOAD_ADDR + basic_len  # reale Startadresse des Codes im RAM

    # BASIC erneut, jetzt mit korrekter SYS-Zahl:
    basic = build_basic_sys_stub(code_start=code_start)

    # Endgültig:
    prg = bytearray()
    prg += _le16(LOAD_ADDR)   # PRG-Header (Ladeadresse)
    prg += basic
    prg += assembled_code     # Code liegt direkt dahinter
    return bytes(prg), code_start
