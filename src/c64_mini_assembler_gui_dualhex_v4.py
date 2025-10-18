
import sys
import os
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFileDialog, QPlainTextEdit, QMessageBox, QLabel, QSplitter,
    QComboBox, QCheckBox
)
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtCore import Qt

from c6510_spec import C6510Spec

# ----------------- PETSCII mapping -----------------
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
}
def petscii_text_char(b: int) -> str:
    b &= 0xFF
    if 0x20 <= b <= 0x7E:
        if b in SPECIALS: return SPECIALS[b]
        ch = chr(b)
        if 'a' <= ch <= 'z': ch = ch.upper()
        if ch in "{}[]`": return '·'
        return ch
    if b in GRAPHICS: return GRAPHICS[b]
    if b in (0x00,0xA0): return ' '
    return '·'

# ----------------- Assembler core -----------------
@dataclass
class AsmLine:
    label: Optional[str]; mnemonic: Optional[str]; operand: Optional[str]; raw: str; lineno: int

ALIASES = {"BNZ": "BNE", "BZ": "BEQ"}

class MiniAssembler:
    def __init__(self, spec: C6510Spec):
        self.spec = spec
        self.org = 0x1000
        self.pc = self.org
        self.symbols: Dict[str,int] = {}

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

    def _split_args(self, operand: Optional[str]) -> List[str]:
        if not operand: return []
        s = operand; out=[]; buf=[]; in_str=False; i=0
        while i<len(s):
            c=s[i]
            if c=='"':
                in_str=not in_str; buf.append(c); i+=1; continue
            if c==',' and not in_str:
                part="".join(buf).strip()
                if part: out.append(part)
                buf=[]; i+=1; continue
            buf.append(c); i+=1
        part="".join(buf).strip()
        if part: out.append(part)
        return out

    def eval_expr(self, expr: str) -> int:
        expr=expr.strip()
        m=re.fullmatch(r"'(.)'",expr)
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
        BRANCHES = {"BPL","BMI","BVC","BVS","BCC","BCS","BNE","BEQ"}

        # Pass 1
        self.pc = self.org; self.symbols.clear()
        for ln in lines:
            if ln.label:
                if ln.label in self.symbols: raise ValueError(f"Label doppelt definiert: {ln.label} (Zeile {ln.lineno})")
                self.symbols[ln.label]=self.pc
            if not ln.mnemonic: continue
            mnem = ALIASES.get(ln.mnemonic.upper(), ln.mnemonic.upper())
            if mnem == ".ORG":
                if not ln.operand: raise ValueError(f".org ohne Adresse (Zeile {ln.lineno})")
                self.org = self.eval_expr(ln.operand); self.pc = self.org; continue
            if mnem in (".BYTE",".BYT",".TEXT",".ASC"):
                for p in self._split_args(ln.operand):
                    if p.startswith('"') and p.endswith('"'):
                        s=bytes(p[1:-1],"latin1","replace"); self.pc += len(s)
                    else: self.pc += 1
                continue
            if mnem == ".WORD":
                self.pc += 2*len(self._split_args(ln.operand)); continue
            if mnem in BRANCHES:
                self.pc += 2; continue
            try:
                mode, ob = self.detect_mode_and_operand_bytes(mnem, ln.operand, self.pc)
                _ = self.spec.get_opcode(mnem, mode)
                self.pc += 1+len(ob)
            except Exception:
                self.pc += 3

        # Pass 2
        self.pc = self.org; out = bytearray()
        for ln in lines:
            if not ln.mnemonic: continue
            mnem = ALIASES.get(ln.mnemonic.upper(), ln.mnemonic.upper())
            if mnem == ".ORG":
                self.org = self.eval_expr(ln.operand); self.pc = self.org; out = bytearray(); continue
            if mnem in (".BYTE",".BYT",".TEXT",".ASC"):
                for p in self._split_args(ln.operand):
                    if p.startswith('"') and p.endswith('"'):
                        s=bytes(p[1:-1],"latin1","replace"); out.extend(s); self.pc += len(s)
                    else:
                        v=self.eval_expr(p)&0xFF; out.append(v); self.pc += 1
                continue
            if mnem == ".WORD":
                for p in self._split_args(ln.operand):
                    v=self.eval_expr(p)&0xFFFF; out.extend([v & 0xFF,(v>>8)&0xFF]); self.pc += 2
                continue
            if mnem in BRANCHES:
                opcode = self.spec.get_opcode(mnem,"rel")
                target = self.eval_expr(ln.operand)
                off = C6510Spec.rel_branch_offset(self.pc, target)
                out.extend([opcode, off])
                listing.append(f"{self.pc:04X}: {opcode:02X} {off:02X}    {mnem} ${target:04X}")
                self.pc += 2
                continue
            mode, ob = self.detect_mode_and_operand_bytes(mnem, ln.operand, self.pc)
            opcode = self.spec.get_opcode(mnem, mode)
            out.append(opcode); out.extend(ob)
            # Keep original operand for non-branches
            listing.append(f"{self.pc:04X}: " + " ".join(f"{b:02X}" for b in [opcode]+ob) + f"    {mnem} {ln.operand or ''}")
            self.pc += 1+len(ob)

        return bytes(out), self.org, listing

# ----------------- PRG writer -----------------
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
SAMPLE = r"""; Dual-Hex Demo
.org $1000
start:  LDX #$00
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
        self.setWindowTitle("C64 Mini Assembler — Dual Hex Views (branches show $ADDR)")
        self.resize(1280, 820)

        self.spec = C6510Spec.from_json("6510_with_illegal_flags.json")
        self.assembler = MiniAssembler(self.spec)

        # Right: editor
        self.editor = QPlainTextEdit()
        self.editor.setPlainText(SAMPLE)
        self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFont("C64 Pro Mono")
        if font.family() != "C64 Pro Mono":
            font = QFont("Consolas"); font.setStyleHint(QFont.Monospace)
        font.setPointSize(12)
        self.editor.setFont(font)

        # Left: container with vertical splitter (two hex views)
        self.hexview_main = QPlainTextEdit()
        self.hexview_main.setReadOnly(True)
        self.hexview_main.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.hexview_main.setFont(font)

        self.hexview_instr = QPlainTextEdit()
        self.hexview_instr.setReadOnly(True)
        self.hexview_instr.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.hexview_instr.setFont(font)

        self.lower_splitter = QSplitter(Qt.Vertical)  # horizontal bar between two views
        self.lower_splitter.addWidget(self.hexview_main)
        self.lower_splitter.addWidget(self.hexview_instr)
        self.lower_splitter.setSizes([500, 300])

        # Global splitter: left (dual hex) | right (editor)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.lower_splitter)
        self.splitter.addWidget(self.editor)
        self.splitter.setSizes([600, 680])

        # Controls
        self.btn_load = QPushButton("Laden")
        self.btn_save = QPushButton("Speichern")
        self.btn_compile = QPushButton("Compile")
        self.btn_load.clicked.connect(self.load_source)
        self.btn_save.clicked.connect(self.save_source)
        self.btn_compile.clicked.connect(self.compile_source)

        self.org_combo = QComboBox()
        self.org_combo.addItems(["$0801 (BASIC)","$1000","$2000","$4000","$6000","$C000"])
        self.org_combo.setEditable(True); self.org_combo.setCurrentText("$1000")
        self.override_org = QCheckBox("Startadresse erzwingen"); self.override_org.setChecked(True)

        topbar = QHBoxLayout()
        topbar.addWidget(self.btn_load); topbar.addWidget(self.btn_save)
        topbar.addSpacing(12)
        topbar.addWidget(QLabel("Start:")); topbar.addWidget(self.org_combo); topbar.addWidget(self.override_org)
        topbar.addStretch(1)
        topbar.addWidget(self.btn_compile)

        central = QWidget(); v = QVBoxLayout(central)
        v.addLayout(topbar); v.addWidget(self.splitter)
        self.setCentralWidget(central)

        self._last_prg=None; self._last_payload=None; self._last_org=None; self._last_listing=[]
        self.hexview_main.installEventFilter(self)

        self.compile_source()

    def eventFilter(self, obj, ev):
        if obj is self.hexview_main and ev.type() == ev.Resize:
            if self._last_prg is not None:
                load_addr = 0x0801
                body = self._last_prg[2:]
                self._refresh_hex_main(load_addr, body)
        return super().eventFilter(obj, ev)

    def parse_org_combo(self) -> int:
        text = self.org_combo.currentText().split()[0]
        if text.startswith("$"): return int(text[1:],16)
        if text.isdigit(): return int(text)
        return 0x1000

    def load_source(self):
        path, _ = QFileDialog.getOpenFileName(self, "Assembler laden", "", "ASM/Text (*.asm *.s *.txt);;Alle Dateien (*)")
        if not path: return
        with open(path, "r", encoding="utf-8") as f:
            self.editor.setPlainText(f.read())
        self.compile_source()  # refresh both views

    def save_source(self):
        path, _ = QFileDialog.getSaveFileName(self, "Assembler speichern", "source.asm", "ASM (*.asm);;Alle Dateien (*)")
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.editor.toPlainText())

    def compile_source(self):
        try:
            if self.override_org.isChecked():
                self.assembler.org = self.parse_org_combo()
            payload, org, listing = self.assembler.assemble(self.editor.toPlainText())
            self._last_payload = payload; self._last_org = org; self._last_listing = listing

            prg = build_prg_with_basic_autostart(payload, start_addr=org)
            load_addr = 0x0801; body = prg[2:]
            self._last_prg = prg

            self._refresh_hex_main(load_addr, body)
            self._refresh_hex_instr(listing)
            self.statusBar().showMessage(f"Compiled: {len(payload)} bytes @ ${org:04X}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))

    # ------ View 1: main hex view (addr + hex + text with width 4 or 8) ------
    def _calc_text_width(self) -> int:
        fm = QFontMetrics(self.hexview_main.font())
        view_w = self.hexview_main.viewport().width()
        char_w = fm.horizontalAdvance('0')
        reserved_px = char_w * 35  # rough estimate for fixed columns
        remain = max(0, view_w - reserved_px)
        return 8 if remain >= char_w*8 else 4

    
# --- PATCH START: resolve label operands to $ADDR in instruction view ---
    def _format_addr4(self, value: int) -> str:
        return f"${value & 0xFFFF:04X}"

    def _resolve_operand_numeric(self, operand_str: str) -> str:
        """Return operand with labels replaced by $HHHH where possible.
        Handles forms: expr, expr,X  expr,Y  (expr)  (expr,X)  (expr),Y
        Leaves immediate (#$..) and accumulator A untouched.
        """
        if not operand_str:
            return operand_str

        s = operand_str.strip()

        # Immediate or accumulator -> unchanged
        if s.startswith("#") or s.upper() == "A":
            return s

        # Already a hex literal? normalize spacing but keep as-is
        m_hex = re.fullmatch(r"\$[0-9A-Fa-f]{1,4}(?:\s*,\s*[XY])?$", s)
        m_hex_indir = re.fullmatch(r"\(\s*\$[0-9A-Fa-f]{1,4}\s*\)(?:\s*,\s*Y)?$", s)
        m_hex_indx  = re.fullmatch(r"\(\s*\$[0-9A-Fa-f]{1,2}\s*,\s*X\s*\)$", s)
        if m_hex or m_hex_indir or m_hex_indx:
            # Normalize commas/spaces
            s = s.replace(",X", ", X").replace(",Y", ", Y")
            s = re.sub(r"\s+", " ", s)
            s = s.replace("( ", "(").replace(" )", ")")
            return s

        # Try patterns and evaluate inner expression via assembler
        def try_eval(expr: str) -> Optional[int]:
            try:
                return self.assembler.eval_expr(expr)
            except Exception:
                return None

        # (expr,X)
        m = re.fullmatch(r"\(\s*(.+?)\s*,\s*X\s*\)", s, flags=re.IGNORECASE)
        if m:
            val = try_eval(m.group(1))
            if val is not None:
                return f"({self._format_addr4(val)}, X)"
            return s

        # (expr),Y
        m = re.fullmatch(r"\(\s*(.+?)\s*\)\s*,\s*Y", s, flags=re.IGNORECASE)
        if m:
            val = try_eval(m.group(1))
            if val is not None:
                return f"({self._format_addr4(val)}), Y"
            return s

        # (expr)
        m = re.fullmatch(r"\(\s*(.+?)\s*\)", s, flags=re.IGNORECASE)
        if m:
            val = try_eval(m.group(1))
            if val is not None:
                return f"({self._format_addr4(val)})"
            return s

        # expr, X  |  expr, Y
        m = re.fullmatch(r"(.+?)\s*,\s*([XY])", s, flags=re.IGNORECASE)
        if m:
            val = try_eval(m.group(1))
            if val is not None:
                return f"{self._format_addr4(val)}, {m.group(2).upper()}"
            return s

        # plain expr
        val = try_eval(s)
        if val is not None:
            return f"{self._format_addr4(val)}"

        return s
    # --- PATCH END ---
    def _refresh_hex_main(self, base_addr: int, data: bytes):
        text_cols = self._calc_text_width()
        lines = []
        header = f"ADDR  00 01 02 03 | 04 05 06 07  TEXT({text_cols})\n" + "-"*64
        lines.append(header)
        for i in range(0, len(data), 8):
            chunk = data[i:i+8]
            left = " ".join(f"{b:02X}" for b in chunk[:4]).ljust(11)
            right = " ".join(f"{b:02X}" for b in chunk[4:8]).ljust(11)
            txt = "".join(petscii_text_char(b) for b in chunk)[:text_cols].ljust(text_cols)
            addr = base_addr + i
            lines.append(f"{addr:04X}  {left} | {right}  {txt}")
        self.hexview_main.setPlainText("\n".join(lines))

    # ------ View 2: instruction hex (<=4 bytes per opcode + mnemonic; branches show $ADDR) ------
    def _refresh_hex_instr(self, listing: List[str]):
        BRANCHES = {"BPL","BMI","BVC","BVS","BCC","BCS","BNE","BEQ"}
        out = ["ADDR  BYTES(max4)    MNEMONIC", "-"*60]
        for line in listing:
            try:
                addr_part, rest = line.split(":", 1)
                addr_str = addr_part.strip()
                parts = rest.strip().split()
                # parse bytes up to first non-hex token
                byte_tokens = []
                mnem_start_idx = 0
                for idx, tok in enumerate(parts):
                    if re.fullmatch(r"[0-9A-Fa-f]{2}", tok):
                        byte_tokens.append(tok.upper())
                    else:
                        mnem_start_idx = idx
                        break
                if mnem_start_idx == 0:
                    out.append(line); continue
                mnem_tokens = parts[mnem_start_idx:]
                mnem = mnem_tokens[0].upper() if mnem_tokens else ""
                operand_str = " ".join(mnem_tokens[1:]) if len(mnem_tokens) > 1 else ""

                # Show bytes (max 4)
                bytes_str = " ".join(byte_tokens[:4])

                # Branch operand override: show absolute $HHHH
                display_mnemonic = f"{mnem} {self._resolve_operand_numeric(operand_str)}".strip()
                if mnem in BRANCHES and len(byte_tokens) >= 2:
                    # derive address literal from relative offset
                    addr = int(addr_str, 16)
                    off = int(byte_tokens[1], 16)
                    if off >= 0x80: off -= 0x100
                    target = (addr + 2 + off) & 0xFFFF
                    display_mnemonic = f"{mnem} ${target:04X}"

                out.append(f"{addr_str:>4}  {bytes_str:<11}  {display_mnemonic}")
            except Exception:
                out.append(line)
        self.hexview_instr.setPlainText("\n".join(out))

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
