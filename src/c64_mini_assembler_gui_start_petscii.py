
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

# ----------------- PETSCII view -----------------
def petscii_char(byte: int, mode: str = "upper"):
    """Return a printable char for the hex view.
    mode: "upper" approximates C64 default UPPER/GRAPHICS: lowercase shown as uppercase,
          and non-printables mapped to block/space.
    """
    b = byte & 0xFF
    # printable ASCII range
    if 0x20 <= b <= 0x7E:
        ch = chr(b)
        if mode == "upper":
            # C64 default shows uppercase; map ascii lowercase to uppercase for the look
            if 'a' <= ch <= 'z':
                ch = ch.upper()
            # map braces and backtick to simple approximations
            if ch in "{}[]`":
                ch = "·"
        return ch
    # A few graphic approximations for PETSCII control/graphics
    if b in (0xA0, 0x00):  # space
        return " "
    # Use medium shade block for many graphics
    return "·"

def hexdump_rows(data: bytes, base_addr: int = 0x0000, view_mode: str = "petscii") -> List[str]:
    rows = []
    for i in range(0, len(data), 8):
        chunk = data[i:i+8]
        left = " ".join(f"{b:02X}" for b in chunk[:4]).ljust(11)
        right = " ".join(f"{b:02X}" for b in chunk[4:8]).ljust(11)
        if view_mode == "petscii":
            ascii_part = "".join(petscii_char(b, "upper") for b in chunk)
        else:
            ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
        addr = base_addr + i
        rows.append(f"{addr:04X}  {left} | {right}  {ascii_part}")
    return rows

# ----------------- Assembler (same as previous, trimmed) -----------------
@dataclass
class AsmLine:
    label: Optional[str]
    mnemonic: Optional[str]
    operand: Optional[str]
    raw: str
    lineno: int

class MiniAssembler:
    def __init__(self, spec: C6510Spec):
        self.spec = spec
        self.org = 0x1000
        self.pc = self.org
        self.symbols: Dict[str, int] = {}

    def parse(self, text: str) -> List[AsmLine]:
        lines: List[AsmLine] = []
        for lineno, rawline in enumerate(text.splitlines(), start=1):
            line = rawline.split(";",1)[0].rstrip()
            if not line.strip():
                continue
            label = None; mnemonic=None; operand=None
            if ":" in line:
                before, after = line.split(":", 1)
                if before.strip(): label = before.strip()
                line = after.strip()
            if line:
                parts = line.split(None, 1)
                mnemonic = parts[0].upper()
                operand = parts[1].strip() if len(parts) > 1 else None
            lines.append(AsmLine(label, mnemonic, operand, rawline, lineno))
        return lines

    def eval_expr(self, expr: str) -> int:
        expr = expr.strip()
        m = re.fullmatch(r"'(.)'", expr)
        if m: return ord(m.group(1))
        if expr.startswith("$"): return int(expr[1:], 16)
        if expr.startswith("%"): return int(expr[1:], 2)
        if expr.isdigit(): return int(expr, 10)
        if expr in self.symbols: return self.symbols[expr]
        raise ValueError(f"Unbekannter Ausdruck/Label: {expr}")

    def detect_mode_and_operand_bytes(self, mnem: str, operand: Optional[str], pc: int) -> Tuple[str, List[int]]:
        if operand is None: return "imp", []
        op = operand.strip()
        if op.upper() == "A": return "acc", []
        if op.startswith("#"):
            v = self.eval_expr(op[1:]) & 0xFF; return "imm", [v]
        if re.fullmatch(r"\(\s*\$?[0-9A-Fa-f]+\s*,\s*X\s*\)", op):
            inner = op[1:-1].replace(" ",""); addr = self.eval_expr(inner.split(",")[0]); return "indx", [addr & 0xFF]
        if re.fullmatch(r"\(\s*\$?[0-9A-Fa-f]+\s*\)\s*,\s*Y", op):
            inner = op.split(")")[0][1:]; addr = self.eval_expr(inner); return "indy", [addr & 0xFF]
        if re.fullmatch(r"\(\s*\$?[0-9A-Fa-f]+\s*\)", op):
            addr = self.eval_expr(op[1:-1]); return "ind", [addr & 0xFF, (addr >> 8) & 0xFF]
        m = re.fullmatch(r"(.+)\s*,\s*X", op, re.IGNORECASE)
        if m:
            val = self.eval_expr(m.group(1)); 
            return ("zpx",[val&0xFF]) if val<=0xFF else ("absx",[val&0xFF,(val>>8)&0xFF])
        m = re.fullmatch(r"(.+)\s*,\s*Y", op, re.IGNORECASE)
        if m:
            val = self.eval_expr(m.group(1)); 
            return ("zpy",[val&0xFF]) if val<=0xFF else ("absy",[val&0xFF,(val>>8)&0xFF])
        val = self.eval_expr(op); 
        return ("zp",[val&0xFF]) if val<=0xFF else ("abs",[val&0xFF,(val>>8)&0xFF])

    def assemble(self, text: str) -> Tuple[bytes, int, List[str]]:
        listing: List[str] = []
        lines = self.parse(text)
        self.pc = self.org; self.symbols.clear()

        # pass 1
        for ln in lines:
            if ln.label:
                if ln.label in self.symbols: raise ValueError(f"Label doppelt definiert: {ln.label} (Zeile {ln.lineno})")
                self.symbols[ln.label] = self.pc
            if not ln.mnemonic: continue
            mnem = ln.mnemonic.upper()
            if mnem == ".ORG":
                if not ln.operand: raise ValueError(f".org ohne Adresse (Zeile {ln.lineno})")
                self.org = self.eval_expr(ln.operand); self.pc = self.org; continue
            if mnem in (".BYTE",".BYT"):
                if ln.operand:
                    for part in ln.operand.split(","):
                        p = part.strip()
                        if p.startswith('"') and p.endswith('"'):
                            s = bytes(p[1:-1], "latin1", "replace"); self.pc += len(s)
                        else: self.pc += 1
                continue
            if mnem == ".WORD":
                if ln.operand:
                    cnt = len([_ for _ in ln.operand.split(",") if _.strip()]); self.pc += 2*cnt
                continue
            if mnem in (".TEXT",".ASC"):
                if not ln.operand or not (ln.operand.startswith('"') and ln.operand.endswith('"')):
                    raise ValueError(f'.text erwartet "String" (Zeile {ln.lineno})')
                s = bytes(ln.operand[1:-1], "latin1", "replace"); self.pc += len(s); continue
            if mnem in {"BPL","BMI","BVC","BVS","BCC","BCS","BNE","BEQ"}:
                self.pc += 2; continue
            try:
                mode, ob = self.detect_mode_and_operand_bytes(mnem, ln.operand, self.pc)
                _ = self.spec.get_opcode(mnem, mode)
                self.pc += 1 + len(ob)
            except Exception:
                self.pc += 3

        # pass 2
        self.pc = self.org; out = bytearray()
        for ln in lines:
            if not ln.mnemonic: continue
            mnem = ln.mnemonic.upper()
            if mnem == ".ORG":
                self.org = self.eval_expr(ln.operand); self.pc = self.org; out = bytearray(); continue
            if mnem in (".BYTE",".BYT"):
                if ln.operand:
                    for part in ln.operand.split(","):
                        p = part.strip()
                        if p.startswith('"') and p.endswith('"'):
                            s = bytes(p[1:-1], "latin1", "replace"); out.extend(s); self.pc += len(s)
                        else:
                            v = self.eval_expr(p) & 0xFF; out.append(v); self.pc += 1
                continue
            if mnem == ".WORD":
                if ln.operand:
                    for part in ln.operand.split(","):
                        p = part.strip(); if not p: continue
                        v = self.eval_expr(p) & 0xFFFF; out.extend([v & 0xFF, (v>>8)&0xFF]); self.pc += 2
                continue
            if mnem in (".TEXT",".ASC"):
                s = bytes(ln.operand[1:-1], "latin1", "replace"); out.extend(s); self.pc += len(s); continue
            if mnem in {"BPL","BMI","BVC","BVS","BCC","BCS","BNE","BEQ"}:
                opcode = self.spec.get_opcode(mnem, "rel"); target = self.eval_expr(ln.operand)
                off = C6510Spec.rel_branch_offset(self.pc, target); out.extend([opcode, off]); self.pc += 2; continue
            mode, ob = self.detect_mode_and_operand_bytes(mnem, ln.operand, self.pc)
            opcode = self.spec.get_opcode(mnem, mode); out.append(opcode); out.extend(ob); self.pc += 1 + len(ob)
        return bytes(out), self.org, listing

# ----------------- PRG writers -----------------
def build_prg_raw(payload: bytes, load_addr: int) -> bytes:
    prg = bytearray([load_addr & 0xFF, (load_addr >> 8) & 0xFF])
    prg.extend(payload); return bytes(prg)

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

# ----------------- GUI -----------------
SAMPLE = r"""; Demo
        LDX #$00
loop:   LDA msg,X
        BEQ done
        JSR $FFD2
        INX
        BNE loop
done:   RTS
msg:    .text "HELLO, C64!", 0
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("C64 Mini Assembler (PyQt5) — Start & PETSCII")
        self.resize(1240, 780)

        self.spec = C6510Spec.from_json("6510_with_illegal_flags.json")
        self.assembler = MiniAssembler(self.spec)

        # Widgets
        self.editor = QPlainTextEdit()
        self.editor.setPlainText(SAMPLE)
        self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFont("C64 Pro Mono")
        if font.family() != "C64 Pro Mono":
            font = QFont("Consolas"); font.setStyleHint(QFont.Monospace)
        font.setPointSize(12)
        self.editor.setFont(font)

        self.hexview = QPlainTextEdit()
        self.hexview.setReadOnly(True)
        self.hexview.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.hexview.setFont(font)

        # Controls
        self.btn_load = QPushButton("Laden")
        self.btn_save = QPushButton("Speichern")
        self.btn_compile = QPushButton("Compile")
        self.btn_save_prg = QPushButton("PRG speichern")
        self.btn_start_vice = QPushButton("Start")
        self.autostart_chk = QCheckBox("BASIC-Autostart")
        self.autostart_chk.setChecked(True)

        self.btn_load.clicked.connect(self.load_source)
        self.btn_save.clicked.connect(self.save_source)
        self.btn_compile.clicked.connect(self.compile_source)
        self.btn_save_prg.clicked.connect(self.save_prg)
        self.btn_start_vice.clicked.connect(self.start_in_vice)

        # Startaddr Combo
        self.org_combo = QComboBox()
        presets = ["$0801 (BASIC)","$1000","$2000","$4000","$6000","$C000"]
        self.org_combo.addItems(presets); self.org_combo.setEditable(True); self.org_combo.setCurrentText("$1000")
        self.override_org = QCheckBox("Startadresse erzwingen"); self.override_org.setChecked(True)

        # View mode
        self.view_combo = QComboBox()
        self.view_combo.addItems(["PETSCII (C64-Style)","ASCII"])

        # Top layout
        topbar = QHBoxLayout()
        topbar.addWidget(self.btn_load); topbar.addWidget(self.btn_save)
        topbar.addSpacing(12)
        topbar.addWidget(QLabel("Start:")); topbar.addWidget(self.org_combo); topbar.addWidget(self.override_org)
        topbar.addSpacing(12)
        topbar.addWidget(self.autostart_chk)
        topbar.addSpacing(12)
        topbar.addWidget(QLabel("View:")); topbar.addWidget(self.view_combo)
        topbar.addStretch(1)
        topbar.addWidget(self.btn_compile); topbar.addWidget(self.btn_save_prg); topbar.addWidget(self.btn_start_vice)

        splitter = QSplitter(); splitter.setOrientation(Qt.Horizontal)
        splitter.addWidget(self.hexview); splitter.addWidget(self.editor); splitter.setSizes([560, 680])

        central = QWidget(); v = QVBoxLayout(central); v.addLayout(topbar); v.addWidget(splitter); self.setCentralWidget(central)

        self._last_prg = None; self._last_payload = None; self._last_org = None
        self.compile_source()

    # -------- Helpers --------
    def parse_org_combo(self) -> int:
        text = self.org_combo.currentText().split()[0]
        if text.startswith("$"): return int(text[1:], 16)
        if text.isdigit(): return int(text)
        return 0x1000

    def set_error_markers(self, line_numbers: List[int]):
        extra = []
        fmt = QTextCharFormat(); fmt.setBackground(QColor("#ffdddd"))
        for ln in line_numbers:
            sel = QPlainTextEdit.ExtraSelection(); cursor = self.editor.textCursor()
            cursor.movePosition(cursor.Start); 
            for _ in range(ln-1): cursor.movePosition(cursor.Down)
            cursor.select(cursor.LineUnderCursor); sel.cursor = cursor; sel.format = fmt; extra.append(sel)
        self.editor.setExtraSelections(extra)

    def clear_error_markers(self):
        self.editor.setExtraSelections([])

    # -------- Actions --------
    def load_source(self):
        path, _ = QFileDialog.getOpenFileName(self, "Assembler laden", "", "ASM/Text (*.asm *.s *.txt);;Alle Dateien (*)")
        if not path: return
        with open(path, "r", encoding="utf-8") as f: self.editor.setPlainText(f.read())

    def save_source(self):
        path, _ = QFileDialog.getSaveFileName(self, "Assembler speichern", "source.asm", "ASM (*.asm);;Alle Dateien (*)")
        if not path: return
        with open(path, "w", encoding="utf-8") as f: f.write(self.editor.toPlainText())

    def compile_source(self):
        self.clear_error_markers()
        try:
            if self.override_org.isChecked(): self.assembler.org = self.parse_org_combo()
            payload, org, listing = self.assembler.assemble(self.editor.toPlainText())
            if self.autostart_chk.isChecked():
                prg = build_prg_with_basic_autostart(payload, start_addr=org)
                load_addr = 0x0801; body = prg[2:]  # BASIC block is viewable too
            else:
                prg = build_prg_raw(payload, load_addr=org)
                load_addr = org; body = prg[2:]
            rows = hexdump_rows(body, base_addr=load_addr, view_mode="petscii" if self.view_combo.currentIndex()==0 else "ascii")
            header = "ADDR   00 01 02 03   |  04 05 06 07   TEXT\n" + "-"*60
            self.hexview.setPlainText(header + "\n" + "\n".join(rows))
            self._last_prg = prg; self._last_payload = payload; self._last_org = org
            mode = "Autostart" if self.autostart_chk.isChecked() else "RAW"
            self.statusBar().showMessage(f"Compiled ({mode}): {len(payload)} bytes @ ${org:04X} | PRG size {len(prg)}", 5000)
        except Exception as e:
            msg = str(e); m = re.search(r"Zeile\s+(\d+)", msg)
            if m: self.set_error_markers([int(m.group(1))])
            QMessageBox.critical(self, "Fehler", msg)

    def save_prg(self):
        if not self._last_prg:
            QMessageBox.information(self, "Hinweis", "Erst kompilieren (Compile)."); return
        path, _ = QFileDialog.getSaveFileName(self, "PRG speichern", "program.prg", "C64 PRG (*.prg);;Alle Dateien (*)")
        if not path: return
        with open(path, "wb") as f: f.write(self._last_prg)
        self.statusBar().showMessage(f"PRG gespeichert: {path}", 5000)

    def start_in_vice(self):
        if not self._last_prg:
            self.compile_source()
            if not self._last_prg: return
        # find VICE (x64sc preferred)
        vice = shutil.which("x64sc") or shutil.which("x64") or shutil.which("x64sc.exe") or shutil.which("x64.exe")
        if vice is None:
            QMessageBox.information(self, "VICE benötigt", "Bitte VICE-Executable (x64sc/x64) auswählen.")
            vice, _ = QFileDialog.getOpenFileName(self, "VICE auswählen", "", "Executable (*)")
            if not vice: return
        with tempfile.TemporaryDirectory() as td:
            prg_path = os.path.join(td, "program.prg")
            with open(prg_path, "wb") as f: f.write(self._last_prg)
            # Use VICE autostart
            cmd = [vice, "-autostart", prg_path]
            # For RAW (no BASIC stub), we still autostart; VICE will load and run if it's a PRG with load addr.
            # For absolute control, one could pass monitor commands; for now autostart suffices.
            try:
                subprocess.Popen(cmd)  # do not block GUI
                self.statusBar().showMessage("VICE gestartet (Autostart).", 5000)
            except Exception as e:
                QMessageBox.critical(self, "VICE-Start fehlgeschlagen", str(e))

def main():
    app = QApplication(sys.argv)
    w = MainWindow(); w.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
