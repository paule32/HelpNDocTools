
import sys
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFileDialog, QPlainTextEdit, QMessageBox, QLabel, QSplitter,
    QComboBox, QCheckBox
)
from PyQt5.QtGui import QFont, QTextCharFormat, QColor
from PyQt5.QtCore import Qt

from c6510_spec import C6510Spec

# ===================== Helpers =====================
def split_args(operand: str) -> List[str]:
    """Split a comma-separated operand list, honoring quoted strings."""
    if operand is None or operand.strip() == "":
        return []
    s = operand
    out = []
    buf = []
    in_str = False
    i = 0
    while i < len(s):
        c = s[i]
        if c == '"':
            in_str = not in_str
            buf.append(c)
            i += 1
            continue
        if c == ',' and not in_str:
            part = "".join(buf).strip()
            if part:
                out.append(part)
            buf = []
            i += 1
            continue
        buf.append(c); i += 1
    part = "".join(buf).strip()
    if part:
        out.append(part)
    return out

# ===================== PETSCII mapping (same as previous) =====================
SPECIALS = {0x5E: '↑', 0x5F: '←', 0x7E: 'π'}
GRAPHICS = {
    0x60:'◆',0x61:'▒',0x62:'⎺',0x63:'⎻',0x64:'─',0x65:'⎼',0x66:'⎽',0x67:'▔',
    0x68:'┐',0x69:'┌',0x6A:'└',0x6B:'┘',0x6C:'┼',0x6D:'┤',0x6E:'┴',0x6F:'┬',
    0x70:'├',0x71:'─',0x72:'│',0x73:'█',0x74:'▄',0x75:'▌',0x76:'▐',0x77:'▀',
    0x78:'◥',0x79:'◤',0x7A:'◣',0x7B:'◢',0x7C:'◻',0x7D:'◼',
    0xA0:' ',0xA1:'◆',0xA2:'▒',0xA3:'⎺',0xA4:'⎻',0xA5:'─',0xA6:'⎼',0xA7:'⎽',
    0xA8:'▔',0xA9:'┐',0xAA:'┌',0xAB:'└',0xAC:'┘',0xAD:'┼',0xAE:'┤',0xAF:'┴',
    0xB0:'┬',0xB1:'├',0xB2:'─',0xB3:'│',0xB4:'█',0xB5:'▄',0xB6:'▌',0xB7:'▐',
    0xB8:'▀',0xB9:'◥',0xBA:'◤',0xBB:'◣',0xBC:'◢',0xBD:'◻',0xBE:'◼',0xBF:'★',
    0xC0:'◆',0xC1:'▒',0xC2:'⎺',0xC3:'⎻',0xC4:'─',0xC5:'⎼',0xC6:'⎽',0xC7:'▔',
    0xC8:'┐',0xC9:'┌',0xCA:'└',0xCB:'┘',0xCC:'┼',0xCD:'┤',0xCE:'┴',0xCF:'┬',
    0xD0:'├',0xD1:'─',0xD2:'│',0xD3:'█',0xD4:'▄',0xD5:'▌',0xD6:'▐',0xD7:'▀',
    0xD8:'◥',0xD9:'◤',0xDA:'◣',0xDB:'◢',0xDC:'◻',0xDD:'◼',0xDE:'✚',0xDF:'⚑',
}
def petscii_text_char(b: int, bank: str = "upper_graphics") -> str:
    b &= 0xFF
    if 0x20 <= b <= 0x7E:
        if b in SPECIALS: return SPECIALS[b]
        ch = chr(b)
        if bank == "upper_graphics":
            if 'a' <= ch <= 'z': ch = ch.upper()
        if ch in "{}[]`": return '·'
        return ch
    if b in GRAPHICS: return GRAPHICS[b]
    if b in (0x00,0xA0): return ' '
    return '·'

def hexdump_rows(data: bytes, base_addr: int = 0x0000, bank: str = "upper_graphics") -> List[str]:
    rows = []
    for i in range(0, len(data), 8):
        chunk = data[i:i+8]
        left = " ".join(f"{b:02X}" for b in chunk[:4]).ljust(11)
        right = " ".join(f"{b:02X}" for b in chunk[4:8]).ljust(11)
        txt = "".join(petscii_text_char(b, bank) for b in chunk)
        rows.append(f"{(base_addr+i):04X}  {left} | {right}  {txt}")
    return rows

# ===================== Assembler =====================
@dataclass
class AsmLine:
    label: Optional[str]; mnemonic: Optional[str]; operand: Optional[str]; raw: str; lineno: int

class MiniAssembler:
    def __init__(self, spec: C6510Spec):
        self.spec = spec
        self.org = 0x1000; self.pc = self.org; self.symbols: Dict[str,int] = {}

    def parse(self, text: str) -> List[AsmLine]:
        lines: List[AsmLine] = []
        for lineno, rawline in enumerate(text.splitlines(), start=1):
            line = rawline.split(";",1)[0].rstrip()
            if not line.strip(): continue
            label=None; mnemonic=None; operand=None
            if ":" in line:
                before, after = line.split(":",1)
                if before.strip(): label = before.strip()
                line = after.strip()
            if line:
                parts = line.split(None,1)
                mnemonic = parts[0].upper()
                operand = parts[1].strip() if len(parts)>1 else None
            lines.append(AsmLine(label,mnemonic,operand,rawline,lineno))
        return lines

    def eval_expr(self, expr: str) -> int:
        expr = expr.strip()
        m = re.fullmatch(r"'(.)'", expr)
        if m: return ord(m.group(1))
        if expr.startswith("$"): return int(expr[1:],16)
        if expr.startswith("%"): return int(expr[1:],2)
        if expr.isdigit(): return int(expr,10)
        if expr in self.symbols: return self.symbols[expr]
        raise ValueError(f"Unbekannter Ausdruck/Label: {expr}")

    def detect_mode_and_operand_bytes(self, mnem: str, operand: Optional[str], pc: int) -> Tuple[str,List[int]]:
        if operand is None: return "imp", []
        op = operand.strip()
        if op.upper() == "A": return "acc", []
        if op.startswith("#"): v=self.eval_expr(op[1:])&0xFF; return "imm",[v]
        if re.fullmatch(r"\(\s*\$?[0-9A-Fa-f]+\s*,\s*X\s*\)", op):
            inner = op[1:-1].replace(" ",""); addr=self.eval_expr(inner.split(",")[0]); return "indx",[addr&0xFF]
        if re.fullmatch(r"\(\s*\$?[0-9A-Fa-f]+\s*\)\s*,\s*Y", op):
            inner = op.split(")")[0][1:]; addr=self.eval_expr(inner); return "indy",[addr&0xFF]
        if re.fullmatch(r"\(\s*\$?[0-9A-Fa-f]+\s*\)", op):
            addr=self.eval_expr(op[1:-1]); return "ind",[addr&0xFF,(addr>>8)&0xFF]
        m = re.fullmatch(r"(.+)\s*,\s*X", op, re.IGNORECASE)
        if m:
            val=self.eval_expr(m.group(1)); 
            return ("zpx",[val&0xFF]) if val<=0xFF else ("absx",[val&0xFF,(val>>8)&0xFF])
        m = re.fullmatch(r"(.+)\s*,\s*Y", op, re.IGNORECASE)
        if m:
            val=self.eval_expr(m.group(1)); 
            return ("zpy",[val&0xFF]) if val<=0xFF else ("absy",[val&0xFF,(val>>8)&0xFF])
        val=self.eval_expr(op); 
        return ("zp",[val&0xFF]) if val<=0xFF else ("abs",[val&0xFF,(val>>8)&0xFF])

    def assemble(self, text: str) -> Tuple[bytes,int,List[str]]:
        listing: List[str] = []
        lines = self.parse(text)
        self.pc = self.org; self.symbols.clear()

        # pass 1
        for ln in lines:
            if ln.label:
                if ln.label in self.symbols: raise ValueError(f"Label doppelt definiert: {ln.label} (Zeile {ln.lineno})")
                self.symbols[ln.label]=self.pc
            if not ln.mnemonic: continue
            mnem = ln.mnemonic.upper()
            if mnem == ".ORG":
                if not ln.operand: raise ValueError(f".text/.org erwartet Argument(e) (Zeile {ln.lineno})")
                self.org = self.eval_expr(ln.operand); self.pc = self.org; continue
            if mnem in (".BYTE",".BYT",".TEXT",".ASC"):
                parts = split_args(ln.operand or "")
                for p in parts:
                    p = p.strip()
                    if p.startswith('"') and p.endswith('"'):
                        s = bytes(p[1:-1], "latin1", "replace"); self.pc += len(s)
                    else:
                        self.pc += 1  # one byte
                continue
            if mnem == ".WORD":
                parts = split_args(ln.operand or "")
                self.pc += 2*len(parts); continue

            if mnem in {"BPL","BMI","BVC","BVS","BCC","BCS","BNE","BEQ"}:
                self.pc += 2; continue
            try:
                mode, ob = self.detect_mode_and_operand_bytes(mnem, ln.operand, self.pc)
                _ = self.spec.get_opcode(mnem, mode); self.pc += 1+len(ob)
            except Exception:
                self.pc += 3

        # pass 2
        self.pc = self.org; out = bytearray()
        for ln in lines:
            if not ln.mnemonic: continue
            mnem = ln.mnemonic.upper()
            if mnem == ".ORG":
                self.org = self.eval_expr(ln.operand); self.pc = self.org; out = bytearray(); continue
            if mnem in (".BYTE",".BYT",".TEXT",".ASC"):
                parts = split_args(ln.operand or "")
                for p in parts:
                    p = p.strip()
                    if p.startswith('"') and p.endswith('"'):
                        s = bytes(p[1:-1], "latin1", "replace"); out.extend(s); self.pc += len(s)
                    else:
                        v = self.eval_expr(p) & 0xFF; out.append(v); self.pc += 1
                continue
            if mnem == ".WORD":
                parts = split_args(ln.operand or "")
                for p in parts:
                    v = self.eval_expr(p) & 0xFFFF; out.extend([v & 0xFF, (v>>8)&0xFF]); self.pc += 2
                continue
            if mnem in {"BPL","BMI","BVC","BVS","BCC","BCS","BNE","BEQ"}:
                opcode = self.spec.get_opcode(mnem, "rel"); target = self.eval_expr(ln.operand)
                off = C6510Spec.rel_branch_offset(self.pc, target); out.extend([opcode, off]); self.pc += 2; continue
            mode, ob = self.detect_mode_and_operand_bytes(mnem, ln.operand, self.pc)
            opcode = self.spec.get_opcode(mnem, mode); out.append(opcode); out.extend(ob); self.pc += 1 + len(ob)
        return bytes(out), self.org, listing

# ===================== PRG writers =====================
def build_prg_raw(payload: bytes, load_addr: int) -> bytes:
    prg = bytearray([load_addr & 0xFF, (load_addr >> 8) & 0xFF]); prg.extend(payload); return bytes(prg)

def build_prg_with_basic_autostart(payload: bytes, start_addr: int) -> bytes:
    LOAD_BASIC = 0x0801
    sysline = bytes([0x9E]) + b" " + str(start_addr).encode("ascii") + b"\x00"
    next_addr = LOAD_BASIC + 2 + 2 + len(sysline)
    basic = bytes([next_addr & 0xFF, next_addr >> 8, 10, 0]) + sysline + b"\x00\x00"
    prg = bytearray()
    prg.extend([LOAD_BASIC & 0xFF, LOAD_BASIC >> 8])
    prg.extend(basic)
    prg.extend([start_addr & 0xFF, start_addr >> 8])
    prg.extend(payload)
    return bytes(prg)

# ===================== GUI (trimmed) =====================
SAMPLE = r"""; Demo ('.text' erlaubt Mix)
        LDX #$00
loop:   LDA msg,X
        BEQ done
        JSR $FFD2
        INX
        BNE loop
done:   RTS
msg:    .text "HELLO, C64!", 0, $0A, "OK", 0
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("C64 Mini Assembler — Full PETSCII + .text fix")
        self.resize(1260, 800)

        self.spec = C6510Spec.from_json("6510_with_illegal_flags.json")
        self.assembler = MiniAssembler(self.spec)

        self.editor = QPlainTextEdit(); self.editor.setPlainText(SAMPLE); self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFont("C64 Pro Mono"); 
        if font.family() != "C64 Pro Mono": font = QFont("Consolas"); font.setStyleHint(QFont.Monospace)
        font.setPointSize(12); self.editor.setFont(font)

        self.hexview = QPlainTextEdit(); self.hexview.setReadOnly(True); self.hexview.setLineWrapMode(QPlainTextEdit.NoWrap); self.hexview.setFont(font)

        self.btn_compile = QPushButton("Compile"); self.btn_save_prg = QPushButton("PRG speichern")
        self.autostart_chk = QCheckBox("BASIC-Autostart"); self.autostart_chk.setChecked(True)

        self.btn_compile.clicked.connect(self.compile_source); self.btn_save_prg.clicked.connect(self.save_prg)

        self.org_combo = QComboBox(); self.org_combo.addItems(["$0801 (BASIC)","$1000","$2000","$4000","$6000","$C000"]); self.org_combo.setEditable(True); self.org_combo.setCurrentText("$1000")
        self.override_org = QCheckBox("Startadresse erzwingen"); self.override_org.setChecked(True)

        self.bank_combo = QComboBox(); self.bank_combo.addItems(["Upper/Graphics","Lower/Upper"])

        topbar = QHBoxLayout()
        topbar.addWidget(QLabel("Start:")); topbar.addWidget(self.org_combo); topbar.addWidget(self.override_org)
        topbar.addSpacing(12); topbar.addWidget(self.autostart_chk); topbar.addSpacing(12)
        topbar.addWidget(QLabel("PETSCII:")); topbar.addWidget(self.bank_combo)
        topbar.addStretch(1); topbar.addWidget(self.btn_compile); topbar.addWidget(self.btn_save_prg)

        splitter = QSplitter(); splitter.setOrientation(Qt.Horizontal); splitter.addWidget(self.hexview); splitter.addWidget(self.editor); splitter.setSizes([580,700])

        central = QWidget(); v = QVBoxLayout(central); v.addLayout(topbar); v.addWidget(splitter); self.setCentralWidget(central)

        self._last_prg=None; self._last_payload=None; self._last_org=None
        self.compile_source()

    def parse_org_combo(self) -> int:
        text = self.org_combo.currentText().split()[0]
        if text.startswith("$"): return int(text[1:],16)
        if text.isdigit(): return int(text)
        return 0x1000

    def compile_source(self):
        try:
            if self.override_org.isChecked(): self.assembler.org = self.parse_org_combo()
            payload, org, _ = self.assembler.assemble(self.editor.toPlainText())
            if self.autostart_chk.isChecked():
                prg = build_prg_with_basic_autostart(payload, start_addr=org); load_addr=0x0801; body=prg[2:]
            else:
                prg = build_prg_raw(payload, load_addr=org); load_addr=org; body=prg[2:]
            bank = "upper_graphics" if self.bank_combo.currentIndex()==0 else "lower_upper"
            rows = hexdump_rows(body, base_addr=load_addr, bank=bank)
            header = "ADDR   00 01 02 03   |  04 05 06 07   TEXT\n" + "-"*60
            self.hexview.setPlainText(header + "\n" + "\n".join(rows))
            self._last_prg=prg; self._last_payload=payload; self._last_org=org
            self.statusBar().showMessage(f"Compiled: {len(payload)} bytes @ ${org:04X}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))

    def save_prg(self):
        if not self._last_prg:
            QMessageBox.information(self, "Hinweis", "Erst kompilieren (Compile)."); return
        path, _ = QFileDialog.getSaveFileName(self, "PRG speichern", "program.prg", "C64 PRG (*.prg);;Alle Dateien (*)")
        if not path: return
        with open(path, "wb") as f: f.write(self._last_prg)
        self.statusBar().showMessage(f"PRG gespeichert: {path}", 5000)

def main():
    app = QApplication(sys.argv)
    w = MainWindow(); w.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
