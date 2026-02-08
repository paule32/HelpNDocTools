
import sys
import re
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Set

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QFileDialog, QPlainTextEdit, QMessageBox, QLabel, QSplitter,
    QComboBox, QCheckBox, QTextEdit
)
from PyQt5.QtGui import (
    QFont, QFontMetrics, QColor, QPainter, QTextFormat, QTextCharFormat, QSyntaxHighlighter
)
from PyQt5.QtCore import Qt, QRect, QSize, QEvent

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

ALIASES = {"BNZ": "BNE", "BZ": "BEQ", ".BYT": ".BYTE", ".ASC": ".TEXT", "DB": ".BYTE", "DW": ".WORD"}
BRANCHES = {"BPL","BMI","BVC","BVS","BCC","BCS","BNE","BEQ"}

class AsmHighlighter(QSyntaxHighlighter):
    def __init__(self, parent):
        super().__init__(parent)
        self.fmt_comment = QTextCharFormat()
        self.fmt_comment.setForeground(QColor(0,150,0))
        self.fmt_comment.setFontWeight(QFont.Bold)

        self.fmt_mnemonic = QTextCharFormat()
        self.fmt_mnemonic.setForeground(Qt.black)
        self.fmt_mnemonic.setFontWeight(QFont.Bold)

        self.fmt_label = QTextCharFormat()
        self.fmt_label.setForeground(Qt.darkBlue)

        import re as _re
        self.re_label = _re.compile(r'^\s*([A-Za-z_][\w]*)\s*:', _re.ASCII)
        self.re_mnemonic = _re.compile(r'^\s*(?:[A-Za-z_][\w]*\s*:)?\s*([.A-Za-z]{2,8})\b', _re.ASCII)

    def highlightBlock(self, text: str):
        if not text:
            return
        cpos = text.find(';')
        code_part = text if cpos < 0 else text[:cpos]
        if cpos >= 0:
            self.setFormat(cpos, len(text) - cpos, self.fmt_comment)
        m = self.re_label.match(code_part)
        if m:
            self.setFormat(m.start(1), m.end(1)-m.start(1), self.fmt_label)
        m2 = self.re_mnemonic.match(code_part)
        if m2:
            self.setFormat(m2.start(1), m2.end(1)-m2.start(1), self.fmt_mnemonic)

class MiniAssembler:
    def __init__(self, spec: C6510Spec):
        self.spec = spec
        self.org = 0x1000
        self.pc = self.org
        self.symbols: Dict[str,int] = {}
        self.rows: List[Tuple[str, List[int], str, int]] = []  # for instr view
        self.ignore_org: bool = False

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
        # simple + / -
        m=re.fullmatch(r"(.+)\s*([+-])\s*(.+)",expr)
        if m:
            a=self.eval_expr(m.group(1)); b=self.eval_expr(m.group(3))
            return (a+b)&0xFFFF if m.group(2)== '+' else (a-b)&0xFFFF
        raise ValueError(f"Unbekannter Ausdruck/Label: {expr}")

    def detect_mode_and_operand_bytes(self, mnem: str, operand: Optional[str], pc: int) -> Tuple[str,List[int]]:
        if operand is None or operand.strip()=="": return "imp", []
        op = operand.strip()
        if op.upper() == "A": return "acc", []
        if op.startswith("#"): v=self.eval_expr(op[1:])&0xFF; return "imm",[v]
        # (zp,X)
        if re.fullmatch(r"\(\s*[^)]+\s*,\s*X\s*\)", op, flags=re.IGNORECASE):
            inner=op[1:-1]; lhs=inner.split(",")[0]; v=self._try_eval(lhs); return "indx", [0xFF & (v if v is not None else 0)]
        # (zp),Y
        if re.fullmatch(r"\(\s*[^)]+\s*\)\s*,\s*Y", op, flags=re.IGNORECASE):
            inner=op.split(")")[0][1:]; v=self._try_eval(inner); return "indy", [0xFF & (v if v is not None else 0)]
        # (abs)
        if re.fullmatch(r"\(\s*[^)]+\s*\)", op):
            v=self._try_eval(op[1:-1]); vv=0 if v is None else v; return "ind", [vv&0xFF,(vv>>8)&0xFF]
        m = re.fullmatch(r"(.+)\s*,\s*([XY])", op, re.IGNORECASE)
        if m:
            val=self._try_eval(m.group(1)); idx=m.group(2).upper()
            if val is not None and val<=0xFF:
                return ("zpx",[val&0xFF]) if idx=="X" else ("zpy",[val&0xFF])
            vv=0 if val is None else val
            return ("absx",[vv&0xFF,(vv>>8)&0xFF]) if idx=="X" else ("absy",[vv&0xFF,(vv>>8)&0xFF])
        val=self._try_eval(op)
        if val is not None and val<=0xFF: return "zp",[val&0xFF]
        vv=0 if val is None else val
        return "abs",[vv&0xFF,(vv>>8)&0xFF]

    def _try_eval(self, expr: str) -> Optional[int]:
        try: return self.eval_expr(expr)
        except Exception: return None

    @staticmethod
    def rel_branch_offset(pc: int, target: int) -> int:
        diff = (target - (pc + 2)) & 0xFFFF
        if diff & 0x8000: diff = -((~diff + 1) & 0xFFFF)
        if diff < -128 or diff > 127: raise ValueError("Branch außerhalb Reichweite")
        return diff & 0xFF

    def assemble(self, text: str) -> Tuple[bytes,int,List[str]]:
        listing: List[str] = []
        lines = self.parse(text)
        self.rows.clear()

        # Pass 1
        self.pc = self.org; self.symbols.clear()
        for ln in lines:
            if ln.label:
                if ln.label in self.symbols: raise ValueError(f"Label doppelt definiert: {ln.label} (Zeile {ln.lineno})")
                self.symbols[ln.label]=self.pc
            if not ln.mnemonic: continue
            mnem = ALIASES.get(ln.mnemonic.upper(), ln.mnemonic.upper())
            if mnem == ".ORG":
                if self.ignore_org:
                    # ignore source .org in pass1 sizing
                    continue
                if not ln.operand: raise ValueError(f".org ohne Adresse (Zeile {ln.lineno})")
                self.org = self.eval_expr(ln.operand); self.pc = self.org; continue
            if mnem in (".EQU",".SET"):
                if not ln.label or not ln.operand: raise ValueError(f"{mnem} braucht Label + Wert (Zeile {ln.lineno})")
                self.symbols[ln.label] = self.eval_expr(ln.operand)&0xFFFF; continue
            if mnem in (".BYTE",".BYT",".TEXT",".ASC"):
                for p in self._split_args(ln.operand):
                    if p.startswith('"') and p.endswith('"'): self.pc += len(p[1:-1])
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
                if self.ignore_org:
                    # ignore applying .org in pass2
                    continue
                self.org = self.eval_expr(ln.operand); self.pc = self.org; out = bytearray(); continue
            if mnem in (".EQU",".SET"):
                self.symbols[ln.label] = self.eval_expr(ln.operand)&0xFFFF; continue
            if mnem in (".BYTE",".BYT",".TEXT",".ASC"):
                start_pc = self.pc; bytes_here=[]
                for p in self._split_args(ln.operand):
                    if p.startswith('"') and p.endswith('"'):
                        s=bytes(p[1:-1],"latin1","replace"); out.extend(s); bytes_here.extend(list(s)); self.pc += len(s)
                    else:
                        v=self.eval_expr(p)&0xFF; out.append(v); bytes_here.append(v); self.pc += 1
                listing.append(f"{start_pc:04X}: " + " ".join(f"{b:02X}" for b in bytes_here) + f"    {mnem} {ln.operand or ''}")
                self.rows.append((f"{start_pc:04X}", bytes_here, f"{mnem} {ln.operand or ''}".strip(), ln.lineno))
                continue
            if mnem == ".WORD":
                start_pc = self.pc; bytes_here=[]
                for p in self._split_args(ln.operand):
                    v=self.eval_expr(p)&0xFFFF; out.extend([v & 0xFF,(v>>8)&0xFF]); bytes_here.extend([v & 0xFF,(v>>8)&0xFF]); self.pc += 2
                listing.append(f"{start_pc:04X}: " + " ".join(f"{b:02X}" for b in bytes_here) + f"    {mnem} {ln.operand or ''}")
                self.rows.append((f"{start_pc:04X}", bytes_here, f"{mnem} {ln.operand or ''}".strip(), ln.lineno))
                continue
            if mnem in BRANCHES:
                opcode = self.spec.get_opcode(mnem,"rel")
                target = self.eval_expr(ln.operand)
                off = MiniAssembler.rel_branch_offset(self.pc, target)
                out.extend([opcode, off])
                listing.append(f"{self.pc:04X}: {opcode:02X} {off:02X}    {mnem} ${target:04X}")
                self.rows.append((f"{self.pc:04X}", [opcode, off], f"{mnem} ${target:04X}", ln.lineno))
                self.pc += 2
                continue
            mode, ob = self.detect_mode_and_operand_bytes(mnem, ln.operand, self.pc)
            opcode = self.spec.get_opcode(mnem, mode)
            out.append(opcode); out.extend(ob)
            listing.append(f"{self.pc:04X}: " + " ".join(f"{b:02X}" for b in [opcode]+ob) + f"    {mnem} {ln.operand or ''}")
            self.rows.append((f"{self.pc:04X}", [opcode]+ob, f"{mnem} {ln.operand or ''}".strip(), ln.lineno))
            self.pc += 1+len(ob)

        return bytes(out), self.org, listing

# ----------------- PRG writer -----------------
# Variante A (empfohlen):
# - Kein zusätzlicher Startadress-Marker vor dem Code.
# - BASIC-Zeile: 10 SYS <dezimal(end_of_basic+2)>
# - Direkt im Anschluss an die zwei Nullbytes (BASIC-Ende) folgt der Maschinencode.
# Hinweis: start_addr wird hier ignoriert; die Startadresse ergibt sich aus der BASIC-Zeile.
def build_prg_with_basic_autostart(payload: bytes, start_addr: int) -> bytes:
    LOAD_BASIC = 0x0801

    # Iterativ bestimmen, weil die Stellenanzahl der Dezimalzahl die Position beeinflusst
    while True:
        code_start = LOAD_BASIC  # Platzhalter
        dec = str(code_start).encode("ascii")
        sysline = bytes([0x9E]) + b" " + dec + b"\x00"      # SYS <dec>\0
        next_addr = LOAD_BASIC + 2 + 2 + len(sysline)       # Link + LineNo + Inhalt
        new_code_start = next_addr + 2                      # + zwei 0-Bytes (BASIC-Ende)
        if new_code_start == code_start:
            break
        # ein zweiter Durchlauf reicht in der Praxis
        code_start = new_code_start
        dec = str(code_start).encode("ascii")
        sysline = bytes([0x9E]) + b" " + dec + b"\x00"
        next_addr = LOAD_BASIC + 2 + 2 + len(sysline)
        final_code_start = next_addr + 2
        if final_code_start == code_start:
            break

    # finaler Aufbau mit stabilem code_start
    dec = str(code_start).encode("ascii")
    sysline = bytes([0x9E]) + b" " + dec + b"\x00"
    next_addr = LOAD_BASIC + 2 + 2 + len(sysline)

    basic = bytearray()
    basic.extend([next_addr & 0xFF, next_addr >> 8])  # Link zur nächsten Zeile
    basic.extend([10, 0])                             # Zeilennummer 10
    basic.extend(sysline)                             # SYS <dezimal>
    basic.extend([0x00, 0x00])                        # BASIC-Ende

    prg = bytearray()
    prg.extend([LOAD_BASIC & 0xFF, LOAD_BASIC >> 8])  # Datei-Ladeadresse
    prg.extend(basic)
    prg.extend(payload)                               # direkt anschließend: ML-Payload
    return bytes(prg)

# ----------------- Editor with gutter/breakpoints -----------------
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor
    def sizeHint(self):
        return QSize(self.codeEditor.lineNumberAreaWidth(), 0)
    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._breakpoints: Set[int] = set()
        self._lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        self._highlighter = AsmHighlighter(self.document())

    def lineNumberAreaWidth(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        fm = QFontMetrics(self.font())
        return 12 + fm.horizontalAdvance('9') * digits + 10

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self._lineNumberArea.scroll(0, dy)
        else:
            self._lineNumberArea.update(0, rect.y(), self._lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self._lineNumberArea)
        painter.fillRect(event.rect(), QColor(245, 245, 245))
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        fm = QFontMetrics(self.font())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                dot_rect = QRect(2, top, 10, fm.height())
                if blockNumber in self._breakpoints:
                    painter.setBrush(QColor(200, 0, 0))
                    painter.setPen(Qt.NoPen)
                    r = min(dot_rect.width(), dot_rect.height()) // 2
                    cx = dot_rect.left() + 5
                    cy = top + fm.ascent() // 2 + 4
                    painter.drawEllipse(cx - r//2, cy - r//2, r, r)
                number = str(blockNumber + 1)
                painter.setPen(QColor(120, 120, 120))
                right = self._lineNumberArea.width() - 6
                painter.drawText(0, top, right, fm.height(), Qt.AlignRight | Qt.AlignVCenter, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def mouseDoubleClickEvent(self, event):
        if event.pos().x() < self.lineNumberAreaWidth():
            cursor = self.cursorForPosition(event.pos())
            block_num = cursor.blockNumber()
            if block_num in self._breakpoints: self._breakpoints.remove(block_num)
            else: self._breakpoints.add(block_num)
            self._lineNumberArea.update()
            mw = self.window()
            if hasattr(mw, "_refresh_hex_instr"):
                mw._refresh_hex_instr(mw._last_rows or [])
            event.accept(); return
        super().mouseDoubleClickEvent(event)

    def highlightCurrentLine(self):
        from PyQt5.QtWidgets import QTextEdit as _QTextEdit
        selection = _QTextEdit.ExtraSelection()
        lineColor = QColor(255, 255, 170)
        selection.format.setBackground(lineColor)
        selection.format.setProperty(QTextFormat.FullWidthSelection, True)
        selection.cursor = self.textCursor()
        selection.cursor.clearSelection()
        self.setExtraSelections([selection])

# ----------------- GUI -----------------
SAMPLE = r"""; Dual-Hex + Editor Gutter/Highlight Demo
.org $1000
start:  LDX #$00
loop:   LDA msg,X     ; load next char
        BEQ done      ; end on 0
        JSR $FFD2     ; print char
        INX
        BNE loop
done:   RTS
msg:    .text "HELLO, C64!", 0
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("C64 Mini Assembler — Dual Hex + Gutter/Breakpoints + Highlight")
        self.resize(1280, 880)

        self.spec = C6510Spec.from_json("6510_with_illegal_flags.json")
        self.assembler = MiniAssembler(self.spec)

        # Consolas 10pt überall
        base_font = QFont("Consolas"); base_font.setStyleHint(QFont.Monospace); base_font.setPointSize(10)

        # Editor
        self.editor = CodeEditor()
        self.editor.setPlainText(SAMPLE)
        self.editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.editor.setFont(base_font)

        # Zwei Views als QTextEdit (Rich Text Header, monospace pre)
        self.hexview_main = QTextEdit(); self.hexview_main.setReadOnly(True); self.hexview_main.setLineWrapMode(QTextEdit.NoWrap); self.hexview_main.setFont(base_font)
        self.hexview_instr = QTextEdit(); self.hexview_instr.setReadOnly(True); self.hexview_instr.setLineWrapMode(QTextEdit.NoWrap); self.hexview_instr.setFont(base_font)

        self.lower_splitter = QSplitter(Qt.Vertical)
        self.lower_splitter.addWidget(self.hexview_main)
        self.lower_splitter.addWidget(self.hexview_instr)
        self.lower_splitter.setSizes([520, 320])

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.lower_splitter)
        self.splitter.addWidget(self.editor)
        self.splitter.setSizes([600, 680])

        # Controls + neue Buttons
        self.btn_load = QPushButton("Laden")
        self.btn_save = QPushButton("Speichern")
        self.btn_compile = QPushButton("Compile")
        self.btn_save_prg = QPushButton("PRG speichern")
        self.btn_save_lst = QPushButton("Listing speichern")

        self.btn_load.clicked.connect(self.load_source)
        self.btn_save.clicked.connect(self.save_source)
        self.btn_compile.clicked.connect(self.compile_source)
        self.btn_save_prg.clicked.connect(self.save_prg)
        self.btn_save_lst.clicked.connect(self.save_listing)

        self.org_combo = QComboBox()
        self.org_combo.addItems(["$0801 (BASIC)","$1000","$2000","$4000","$6000","$C000"])
        self.org_combo.setEditable(True); self.org_combo.setCurrentText("$1000")
        self.override_org = QCheckBox("Startadresse erzwingen"); self.override_org.setChecked(True)

        # Auto-Recompile on changes
        try: self.org_combo.currentTextChanged.connect(self.on_org_changed)
        except Exception: pass
        try: self.org_combo.editTextChanged.connect(self.on_org_changed)
        except Exception: pass
        self.override_org.toggled.connect(self.on_override_toggled)

        topbar = QHBoxLayout()
        topbar.addWidget(self.btn_load); topbar.addWidget(self.btn_save)
        topbar.addSpacing(12)
        topbar.addWidget(QLabel("Start:")); topbar.addWidget(self.org_combo); topbar.addWidget(self.override_org)
        topbar.addStretch(1)
        topbar.addWidget(self.btn_compile); topbar.addWidget(self.btn_save_prg); topbar.addWidget(self.btn_save_lst)

        central = QWidget(); v = QVBoxLayout(central)
        v.addLayout(topbar); v.addWidget(self.splitter)
        self.setCentralWidget(central)

        self._last_prg=None; self._last_payload=None; self._last_org=None; self._last_listing=[]
        self._last_rows: List[Tuple[str,List[int],str,int]] = []
        self.hexview_main.installEventFilter(self)

        self.compile_source()

    def eventFilter(self, obj, ev):
        if obj is self.hexview_main and ev.type() == QEvent.Resize:
            if self._last_payload is not None and self._last_org is not None:
                self._refresh_hex_main(self._last_org, self._last_payload)
        return super().eventFilter(obj, ev)

    def parse_org_combo(self) -> int:
        text = self.org_combo.currentText().split()[0]
        if text.startswith("$"): return int(text[1:],16)
        if text.isdigit(): return int(text)
        return 0x1000

    def on_org_changed(self, *_):
        if self.override_org.isChecked():
            self.compile_source()

    def on_override_toggled(self, checked: bool):
        self.compile_source()

    def load_source(self):
        path, _ = QFileDialog.getOpenFileName(self, "Assembler laden", "", "ASM/Text (*.asm *.s *.txt);;Alle Dateien (*)")
        if not path: return
        with open(path, "r", encoding="utf-8") as f:
            self.editor.setPlainText(f.read())
        self.compile_source()

    def save_source(self):
        path, _ = QFileDialog.getSaveFileName(self, "Assembler speichern", "source.asm", "ASM (*.asm);;Alle Dateien (*)")
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.editor.toPlainText())

    def save_prg(self):
        if self._last_prg is None:
            QMessageBox.warning(self, "Hinweis", "Bitte zuerst kompilieren.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "PRG speichern", "program.prg", "C64 Program (*.prg);;Alle Dateien (*)")
        if not path: return
        try:
            with open(path, "wb") as f:
                f.write(self._last_prg)
            self.statusBar().showMessage(f"PRG gespeichert: {path}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Fehler beim Speichern", str(e))

    def save_listing(self):
        if not self._last_listing:
            QMessageBox.warning(self, "Hinweis", "Kein Listing vorhanden. Bitte zuerst kompilieren.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Listing speichern", "listing.txt", "Text (*.txt);;Alle Dateien (*)")
        if not path: return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(self._last_listing))
            self.statusBar().showMessage(f"Listing gespeichert: {path}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Fehler beim Speichern", str(e))

    def compile_source(self):
        try:
            # honor override
            self.assembler.ignore_org = self.override_org.isChecked()
            if self.override_org.isChecked():
                self.assembler.org = self.parse_org_combo()
            payload, org, listing = self.assembler.assemble(self.editor.toPlainText())
            self._last_payload = payload; self._last_org = org; self._last_listing = listing
            self._last_rows = self.assembler.rows

            prg = build_prg_with_basic_autostart(payload, start_addr=org)
            self._last_prg = prg

            # View 1 now shows ONLY the machine code payload at current org
            self._refresh_hex_main(org, payload)
            self._refresh_hex_instr(self._last_rows)
            self.statusBar().showMessage(f"Compiled: {len(payload)} bytes @ ${org:04X}", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))

    # ------ View 1: PRG-Hex (addr + hex + text with width 4/8, bold header + rule) ------
    def _calc_text_width(self) -> int:
        fm = QFontMetrics(self.hexview_main.font())
        view_w = self.hexview_main.viewport().width()
        char_w = fm.horizontalAdvance('0')
        reserved_px = char_w * 35
        remain = max(0, view_w - reserved_px)
        return 8 if remain >= char_w*8 else 4

    def _html_pre(self, inner: str) -> str:
        return f"<pre style='font-family: Consolas, monospace; font-size:10pt; margin:0;'>{inner}</pre>"

    def _refresh_hex_main(self, base_addr: int, data: bytes):
        text_cols = self._calc_text_width()
        lines = []
        header = f"<b>ADDR  00 01 02 03 | 04 05 06 07  TEXT({text_cols})</b>"
        lines.append(header); lines.append("-"*64)
        for i in range(0, len(data), 8):
            chunk = data[i:i+8]
            left = " ".join(f"{b:02X}" for b in chunk[:4]).ljust(11)
            right = " ".join(f"{b:02X}" for b in chunk[4:8]).ljust(11)
            txt = "".join(petscii_text_char(b) for b in chunk)[:text_cols].ljust(text_cols)
            addr = base_addr + i
            lines.append(f"{addr:04X}  {left} | {right}  {txt}")
        html = self._html_pre("\n".join(lines))
        self.hexview_main.setHtml(html)

    # ------ Helpers for operand resolve ------
    def _format_addr4(self, value: int) -> str:
        return f"${value & 0xFFFF:04X}"

    def _resolve_operand_numeric(self, operand_str: str) -> str:
        if not operand_str: return operand_str
        s = operand_str.strip()
        if s.startswith("#") or s.upper() == "A": return s
        m_hex = re.fullmatch(r"\$[0-9A-Fa-f]{1,4}(?:\s*,\s*[XY])?$", s)
        m_hex_indir = re.fullmatch(r"\(\s*\$[0-9A-Fa-f]{1,4}\s*\)(?:\s*,\s*Y)?$", s)
        m_hex_indx  = re.fullmatch(r"\(\s*\$[0-9A-Fa-f]{1,2}\s*,\s*X\s*\)$", s)
        if m_hex or m_hex_indir or m_hex_indx:
            s = s.replace(",X", ", X").replace(",Y", ", Y")
            s = re.sub(r"\s+", " ", s).replace("( ", "(").replace(" )", ")")
            return s
        def try_eval(expr: str):
            try: return self.assembler.eval_expr(expr)
            except Exception: return None
        m = re.fullmatch(r"\(\s*(.+?)\s*,\s*X\s*\)", s, flags=re.IGNORECASE)
        if m:
            val = try_eval(m.group(1))
            if val is not None: return f"({self._format_addr4(val)}, X)"
            return s
        m = re.fullmatch(r"\(\s*(.+?)\s*\)\s*,\s*Y", s, flags=re.IGNORECASE)
        if m:
            val = try_eval(m.group(1))
            if val is not None: return f"({self._format_addr4(val)}), Y"
            return s
        m = re.fullmatch(r"\(\s*(.+?)\s*\)", s, flags=re.IGNORECASE)
        if m:
            val = try_eval(m.group(1))
            if val is not None: return f"({self._format_addr4(val)})"
            return s
        m = re.fullmatch(r"(.+?)\s*,\s*([XY])", s, flags=re.IGNORECASE)
        if m:
            val = try_eval(m.group(1))
            if val is not None: return f"{self._format_addr4(val)}, {m.group(2).upper()}"
            return s
        val = try_eval(s)
        if val is not None: return f"{self._format_addr4(val)}"
        return s

    # ------ View 2: instruction hex (bold header + rule; .TEXT chunking; BP highlight) ------
    def _refresh_hex_instr(self, rows: List[Tuple[str,List[int],str,int]]):
        lines = ["<b>ADDR  BYTES(max4)    MNEMONIC</b>", "-"*60]
        bp_blocks = getattr(self.editor, "_breakpoints", set()) or set()
        bp_src_lines = {b+1 for b in bp_blocks}

        for addr_str, bytes_list, mnemonic_str, src_lineno in rows:
            parts = mnemonic_str.split(None, 1)
            mnem = parts[0] if parts else ""
            operand_str = parts[1] if len(parts) > 1 else ""
            mnem_upper = mnem.upper()

            if mnem_upper in (".TEXT", ".ASC"):
                data = list(bytes_list)
                base = int(addr_str, 16)
                # determine string part (before first zero) for quote placement
                zero_idx = data.index(0x00) if 0x00 in data else len(data)
                str_bytes = data[:zero_idx]
                # ascii helper
                def bytes_to_ascii(bseq):
                    out = []
                    for b in bseq:
                        if 32 <= b <= 126 and b != 34:
                            out.append(chr(b))
                        elif b == 34:
                            out.append('\\"')
                        elif b == 0x20:
                            out.append(' ')
                        else:
                            out.append('.')
                    return "".join(out)
                str_text = bytes_to_ascii(str_bytes)
                str_idx = 0
                off = 0
                while off < len(data):
                    chunk = data[off:off+4]
                    chunk_addr = (base + off) & 0xFFFF
                    bytes_tokens = " ".join(f"{b:02X}" for b in chunk)
                    if len(chunk) < 4:
                        bytes_tokens = bytes_tokens.ljust(11)
                    # figure out how many chars of str_text belong to this chunk (before zero)
                    within_str = 0
                    for _ in chunk:
                        if str_idx + within_str < len(str_text):
                            within_str += 1
                        else:
                            break
                    segment = str_text[str_idx:str_idx+within_str]
                    str_idx += within_str
                    contains_zero = any(b == 0x00 for b in chunk) and (off <= zero_idx < off+4 if zero_idx < len(data) else False)
                    open_q = (off == 0)
                    close_q = (str_idx >= len(str_text))
                    if open_q:
                        seg_text = f'.TEXT "{segment}'
                    else:
                        seg_text = f'.TEXT "{segment}' if segment else ".TEXT"
                    if close_q:
                        seg_text += '"'
                        if contains_zero:
                            seg_text += ", 0"
                    display_mnemonic = seg_text
                    line = f"{chunk_addr:04X}  {bytes_tokens}  {display_mnemonic}"
                    if src_lineno in bp_src_lines:
                        line = f"<span style='background:#B00000;color:#FFF'>{line}</span>"
                    lines.append(line)
                    off += 4
                continue

            # Non-text rows: 4-byte max
            bytes_tokens = [f"{b:02X}" for b in bytes_list][:4]
            bytes_str = " ".join(bytes_tokens).ljust(11)
            # branches: absolute target
            if mnem in BRANCHES and len(bytes_list) >= 2:
                a = int(addr_str, 16)
                off_rel = bytes_list[1]
                if off_rel >= 0x80: off_rel -= 0x100
                target = (a + 2 + off_rel) & 0xFFFF
                display_mnemonic = f"{mnem} ${target:04X}"
            else:
                display_mnemonic = f"{mnem} {self._resolve_operand_numeric(operand_str)}".strip()
            line = f"{int(addr_str,16):04X}  {bytes_str}  {display_mnemonic}"
            if src_lineno in bp_src_lines:
                line = f"<span style='background:#B00000;color:#FFF'>{line}</span>"
            lines.append(line)

        html = self._html_pre("\n".join(lines))
        self.hexview_instr.setHtml(html)

def main():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
