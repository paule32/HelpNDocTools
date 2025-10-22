# hex_listing.py
from __future__ import annotations

def _is_printable_ascii(b: int) -> bool:
    # C64-Pro-Font stellt ASCII dar; wir mappen 32..126 als "druckbar"
    return 32 <= b <= 126

def format_dual_hex(data: bytes, base_addr: int = 0x0000) -> str:
    """
    Dual-Hex (8 Bytes/Zeile): 'AAAA: HH HH HH HH HH HH HH HH  ASCII....'
    Mit Mittenspace zwischen den 4er-Gruppen.
    """
    lines = []
    for i in range(0, len(data), 8):
        chunk = data[i:i+8]
        addr = base_addr + i

        left4  = " ".join(f"{b:02X}" for b in chunk[:4])
        right4 = " ".join(f"{b:02X}" for b in chunk[4:8])
        if len(chunk) < 4:
            left4 += " " * (3 * (4 - len(chunk)))  # aufbreiten
            right4 = ""
        elif len(chunk) < 8:
            right_count = len(chunk) - 4
            right4 += " " * (3 * (4 - max(0, right_count)))

        hex_part = f"{left4} {right4}".rstrip()

        ascii_part = "".join(chr(b) if _is_printable_ascii(b) else "." for b in chunk)

        lines.append(f"{addr:04X}: {hex_part:<23}  {ascii_part}")
    return "\n".join(lines)


# ---------- Mini-Disassembler (teilweise Abdeckung, erweiterbar) ----------

# (mnemonic, size, kind)
# kind steuert Adress-/Operandendarstellung (abs, imm, zp, rel, imp, abx, aby, zpx, zpy, indx, indy)
OPC = {
    0xA9: ("LDA", 2, "imm"), 0xA5: ("LDA", 2, "zp"),  0xAD: ("LDA", 3, "abs"),
    0xB5: ("LDA", 2, "zpx"), 0xBD: ("LDA", 3, "abx"), 0xB9: ("LDA", 3, "aby"),
    0xA1: ("LDA", 2, "indx"),0xB1: ("LDA", 2, "indy"),

    0xA2: ("LDX", 2, "imm"), 0xA6: ("LDX", 2, "zp"),  0xAE: ("LDX", 3, "abs"),
    0xB6: ("LDX", 2, "zpy"), 0xBE: ("LDX", 3, "aby"),

    0xA0: ("LDY", 2, "imm"), 0xA4: ("LDY", 2, "zp"),  0xAC: ("LDY", 3, "abs"),
    0xB4: ("LDY", 2, "zpx"), 0xBC: ("LDY", 3, "abx"),

    0x85: ("STA", 2, "zp"),  0x8D: ("STA", 3, "abs"), 0x95: ("STA", 2, "zpx"),
    0x9D: ("STA", 3, "abx"), 0x99: ("STA", 3, "aby"), 0x81: ("STA", 2, "indx"),
    0x91: ("STA", 2, "indy"),

    0x69: ("ADC", 2, "imm"), 0x65: ("ADC", 2, "zp"),  0x6D: ("ADC", 3, "abs"),
    0xE9: ("SBC", 2, "imm"), 0xE5: ("SBC", 2, "zp"),  0xED: ("SBC", 3, "abs"),

    0x29: ("AND", 2, "imm"), 0x09: ("ORA", 2, "imm"), 0x49: ("EOR", 2, "imm"),

    0x4C: ("JMP", 3, "abs"), 0x6C: ("JMP", 3, "ind"),
    0x20: ("JSR", 3, "abs"), 0x60: ("RTS", 1, "imp"), 0x00: ("BRK", 1, "imp"),

    0xD0: ("BNE", 2, "rel"), 0xF0: ("BEQ", 2, "rel"), 0x90: ("BCC", 2, "rel"),
    0xB0: ("BCS", 2, "rel"), 0x10: ("BPL", 2, "rel"), 0x30: ("BMI", 2, "rel"),

    0x18: ("CLC", 1, "imp"), 0x38: ("SEC", 1, "imp"),
    0xE8: ("INX", 1, "imp"), 0xCA: ("DEX", 1, "imp"),
    0xC8: ("INY", 1, "imp"), 0x88: ("DEY", 1, "imp"),

    0xEA: ("NOP", 1, "imp"),
}

def _word(lo: int, hi: int) -> int:
    return lo | (hi << 8)

def _fmt_operand(kind: str, pc: int, b: bytes) -> str:
    if kind == "imm":
        return f"#{b[0]:02X}h"
    if kind == "zp":
        return f"{b[0]:02X}h"
    if kind == "zpx":
        return f"{b[0]:02X}h,X"
    if kind == "zpy":
        return f"{b[0]:02X}h,Y"
    if kind == "abs":
        return f"${_word(b[0], b[1]):04X}"
    if kind == "abx":
        return f"${_word(b[0], b[1]):04X},X"
    if kind == "aby":
        return f"${_word(b[0], b[1]):04X},Y"
    if kind == "ind":
        return f"(${_word(b[0], b[1]):04X})"
    if kind == "indx":
        return f"({b[0]:02X}h,X)"
    if kind == "indy":
        return f"({b[0]:02X}h),Y"
    if kind == "rel":
        off = b[0] if b[0] < 0x80 else b[0] - 0x100
        target = (pc + 2 + off) & 0xFFFF
        return f"${target:04X}"
    if kind == "imp":
        return ""
    return "??"

def disassemble_listing(data: bytes, base_addr: int = 0x0000) -> str:
    """
    Gibt Zeilen: 'AAAA: BB BB [...]  MNEMONIC [OPERAND]'
    Bytes pro Zeile = Instruktionslänge (1..3). Unbekannt → '.byte $HH'
    """
    i = 0
    out = []
    while i < len(data):
        addr = (base_addr + i) & 0xFFFF
        op = data[i]
        if op in OPC:
            mnem, size, kind = OPC[op]
            inst = data[i:i+size]
            # Bytes formatieren (genau size, Lücke auffüllen für Spalten-Ausrichtung)
            bytes_txt = " ".join(f"{b:02X}" for b in inst)
            pad = " " * (11 - len(bytes_txt))  # 11 = max "HH HH HH"
            operand = _fmt_operand(kind, addr, inst[1:])
            sp = " " if operand else ""
            out.append(f"{addr:04X}: {bytes_txt}{pad}  {mnem}{sp}{operand}")
            i += size
        else:
            # unbekannt: ein Byte ausgeben
            bytes_txt = f"{op:02X}"
            pad = " " * (11 - len(bytes_txt))
            out.append(f"{addr:04X}: {bytes_txt}{pad}  .byte ${op:02X}")
            i += 1
    return "\n".join(out)
