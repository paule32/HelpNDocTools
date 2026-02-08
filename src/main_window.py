# main_window.py (Auszug)
import html as htmlmod
from PyQt5 import QtWidgets, QtGui, QtCore
from asm_highlighter import AsmHighlighter
from basic_compiler import compile_basic_to_asm
from c6510_spec import C6510Spec
from code_editor import CodeEditor
from settings import Settings
from settings_dialog import SettingsDialog
from mini_assembler import MiniAssembler, build_prg_with_basic_autostart
from hex_listing import format_dual_hex, disassemble_listing
from prg_builder import build_single_segment_prg
from runner import ensure_build_dir, write_prg_file, make_d64_and_run

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = Settings.load()
        self._init_ui()
        self._init_toolbar()
        self._init_menu()
        
        self.act_rtpre_load.triggered .connect(self.load_runtime_pre )
        self.act_rtpre_save.triggered .connect(self.save_runtime_pre )
        self.act_rtpost_load.triggered.connect(self.load_runtime_post)
        self.act_rtpost_save.triggered.connect(self.save_runtime_post)
        
        # Sets für Breakpoints
        self._bp_asm   = set()
        self._bp_basic = set()
        
        # Mapping: srcline (1-based, aus Assembler.rows) -> (start_pos, length) im Listing-Dokument
        self._listing_pos_by_srcline = {}
        # Welcher Editor lieferte das aktuelle Listing?
        self._last_listing_source = "asm"  # oder "basic"

        self.asm_hl      = AsmHighlighter(self.asm_editor.document())
        self.asm_out_hl  = AsmHighlighter(self.asm_out_editor.document())
        self.asm_hl_pre  = AsmHighlighter(self.runtime_pre_editor.document())
        self.asm_hl_post = AsmHighlighter(self.runtime_post_editor.document())

        self.spec = C6510Spec.from_json("6510_with_illegal_flags.json")
        self.assembler = MiniAssembler(self.spec)
        
        self._last_payload = None
        self._last_rows = []
        
        self._apply_c64_font()

    def _apply_c64_font(self):
        for fam in ("C64 Pro Mono", "C64 Pro", "C64-Pro-Mono"):
            f = QtGui.QFont(fam, 12)
            if "c64" in QtGui.QFontInfo(f).family().lower():
                for w in (self.basic_editor, self.asm_editor, self.asm_out_editor,
                          self.runtime_pre_editor, self.runtime_post_editor,
                          self.hex_view, self.listings_view):
                    w.setFont(f)
                return
        # fallback
        mono = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        mono.setPointSize(8)
        for w in (self.hex_view, self.listings_view, self.basic_editor,
                  self.asm_editor, self.asm_out_editor):
            w.setFont(mono)
            
    def _html_pre(self, inner: str) -> str:
        fam = self.hex_view.font().family().replace("'", "\\'")
        size_pt = self.hex_view.font().pointSize() or 8
        return f"<pre style=\"font-family:'{fam}', monospace;font-size:{size_pt}pt;margin:0;\">{inner}</pre>"

    def _glyph_for_byte(self, b: int) -> str:
        b &= 0xFF
        if b >= 0x20:
            ch = chr(b)
            if 'a' <= ch <= 'z': ch = ch.upper()
            return ch
        return '·'
        
    def _compose_final_asm(self) -> str:
        # Reihenfolge: Runtime (vor) + erzeugter ASM + Runtime (nach)
        pre  = self.runtime_pre_editor.toPlainText().rstrip()
        gen  = self.asm_out_editor.toPlainText().rstrip()
        post = self.runtime_post_editor.toPlainText().rstrip()
        parts = []
        if pre:  parts += ["; === RUNTIME PRE ===", pre]
        if gen:  parts += ["; === GENERATED ASM ===", gen]
        if post: parts += ["; === RUNTIME POST ===", post]
        return "\n".join(parts) + "\n"
        
    def _refresh_hex_main(self, base_addr: int, data: bytes):
        lines = []
        lines.append("ADDR  00 01 02 03 | 04 05 06 07  TEXT(8)")
        lines.append("-"*64)
        for i in range(0, len(data), 8):
            chunk = data[i:i+8]
            left  = " ".join(f"{b:02X}" for b in chunk[:4]).ljust(11)
            right = " ".join(f"{b:02X}" for b in chunk[4:8]).ljust(11)
            txt_raw = "".join(self._glyph_for_byte(b) for b in chunk)[:8].ljust(8)
            txt = htmlmod.escape(txt_raw)
            addr = base_addr + i
            lines.append(f"{addr:04X}  {left} | {right}  {txt}")
        self.hex_view.setHtml(self._html_pre("\n".join(lines)))

    def _resolve_operand_numeric(self, operand_str: str) -> str:
        # gleiche Logik wie im Upload, kurzgefasst:
        if not operand_str: return ""
        return operand_str  # (optional schönformatieren – kann später identisch wie in deiner Datei ergänzt werden)

    def _refresh_hex_instr(self, rows):
        lines = ["<b>ADDR  BYTES(max4)    MNEMONIC</b>", "-"*60]
        for addr_str, bytes_list, mnemonic_str, _src_line in rows:
            bytes_tokens = " ".join(f"{b:02X}" for b in bytes_list[:4]).ljust(11)
            line = f"{int(addr_str,16):04X}  {bytes_tokens}  {mnemonic_str}"
            lines.append(line)
        self.listings_view.setHtml(self._html_pre("\n".join(lines)))

    def _init_ui(self):
        central = QtWidgets.QWidget()
        root_vbox = QtWidgets.QVBoxLayout(central)

        # --- linker Bereich: vertikaler Splitter mit HexView (oben) + ListingsView (unten) ---
        self.left_split = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.hex_view = QtWidgets.QTextEdit()
        self.hex_view.setReadOnly(True)
        self.hex_view.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.hex_view.setPlaceholderText("HexView …")
        
        self.listings_view = QtWidgets.QTextEdit()
        self.listings_view.setReadOnly(True)
        self.listings_view.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.listings_view.setPlaceholderText("ListingsView …")

        self.left_split.addWidget(self.hex_view)
        self.left_split.addWidget(self.listings_view)
        self.left_split.setStretchFactor(0, 1)
        self.left_split.setStretchFactor(1, 1)

        # --- rechter Bereich: Tabs mit Code-Editoren (mit Gutter + gelbe Current-Line) ---
        self.tabs = QtWidgets.QTabWidget()

        # Tab "Assembler" (unverändert)
        asm_tab = QtWidgets.QWidget()
        asm_layout = QtWidgets.QVBoxLayout(asm_tab)
        self.asm_editor = CodeEditor()
        asm_layout.addWidget(self.asm_editor)
        self.tabs.addTab(asm_tab, "Assembler")

        # Tab "BASIC → ASM" (NEU: unten QTabWidget mit 3 Reitern)
        bas_tab = QtWidgets.QWidget()
        bas_layout = QtWidgets.QVBoxLayout(bas_tab)

        # oberer BASIC-Editor
        self.basic_editor = CodeEditor()
        self.basic_editor.setPlaceholderText('BASIC hier eingeben… (z. B. 10 PRINT "HI")')

        # unten: Container mit Tabs
        bottom_container = QtWidgets.QWidget()
        bottom_v = QtWidgets.QVBoxLayout(bottom_container)
        bottom_v.setContentsMargins(0, 0, 0, 0)

        self.bottom_tabs = QtWidgets.QTabWidget()

        # Tab 1: ASM-Output (nur Editor, keine Toolbar)
        tab1 = QtWidgets.QWidget()
        t1_layout = QtWidgets.QVBoxLayout(tab1)
        self.asm_out_editor = CodeEditor()
        self.asm_out_editor.setPlaceholderText("Erzeugter Assembler-Code …")
        t1_layout.addWidget(self.asm_out_editor)
        self.bottom_tabs.addTab(tab1, "Assembler-Code")

        # Tab 2: Runtime (vor BASIC) + Toolbar
        tab2 = QtWidgets.QWidget()
        t2_layout = QtWidgets.QVBoxLayout(tab2)
        self.tb_runtime_pre = QtWidgets.QToolBar("Runtime (vor BASIC)")
        self.act_rtpre_load = self.tb_runtime_pre.addAction("Load")
        self.act_rtpre_save = self.tb_runtime_pre.addAction("Save")
        t2_layout.addWidget(self.tb_runtime_pre)

        self.runtime_pre_editor = CodeEditor()
        self.runtime_pre_editor.setPlaceholderText("Runtime-Code (wird OBERHALB des BASIC-ASM eingefügt) …")
        t2_layout.addWidget(self.runtime_pre_editor)

        self.bottom_tabs.addTab(tab2, "Runtime ↑ (vor BASIC)")

        # Tab 3: Runtime (nach BASIC) + Toolbar
        tab3 = QtWidgets.QWidget()
        t3_layout = QtWidgets.QVBoxLayout(tab3)
        self.tb_runtime_post = QtWidgets.QToolBar("Runtime (nach BASIC)")
        self.act_rtpost_load = self.tb_runtime_post.addAction("Load")
        self.act_rtpost_save = self.tb_runtime_post.addAction("Save")
        t3_layout.addWidget(self.tb_runtime_post)

        self.runtime_post_editor = CodeEditor()
        self.runtime_post_editor.setPlaceholderText("Runtime-Code (wird UNTERHALB des BASIC-ASM eingefügt) …")
        t3_layout.addWidget(self.runtime_post_editor)

        self.bottom_tabs.addTab(tab3, "Runtime ↓ (nach BASIC)")

        bottom_v.addWidget(self.bottom_tabs)

        # vertikaler Splitter: oben BASIC, unten Tabs (ASM-Output + Runtime)
        vertical_split = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        vertical_split.addWidget(self.basic_editor)
        vertical_split.addWidget(bottom_container)
        vertical_split.setStretchFactor(0, 1)
        vertical_split.setStretchFactor(1, 1)

        bas_layout.addWidget(vertical_split)
        self.tabs.addTab(bas_tab, "BASIC → ASM")

        # horizontaler Splitter: links (Hex+Listing) | rechts (Tabs)
        self.main_split = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self.main_split.addWidget(self.left_split)
        self.main_split.addWidget(self.tabs)
        self.main_split.setStretchFactor(0, 0)
        self.main_split.setStretchFactor(1, 1)

        root_vbox.addWidget(self.main_split)
        self.setCentralWidget(central)
    
    def _on_bp_toggled(self, source_kind: str, line: int, active: bool):
        s = self._bp_asm if source_kind == "asm" else self._bp_basic
        if active: s.add(line)
        else: s.discard(line)
        # Listing nur highlighten, wenn es vom selben Source kommt
        if self._last_listing_source == source_kind:
            self._apply_listing_highlights()

    def _apply_listing_highlights(self):
        # Erzeugt ExtraSelections für alle aktiven BP des aktuellen Sources
        doc = self.listings_view.document()
        sels = []

        active_set = self._bp_asm if self._last_listing_source == "asm" else self._bp_basic
        for srcline in active_set:
            if srcline in self._listing_pos_by_srcline:
                start, length = self._listing_pos_by_srcline[srcline]
                cursor = QtGui.QTextCursor(doc)
                cursor.setPosition(start)
                cursor.setPosition(start + length, QtGui.QTextCursor.KeepAnchor)

                sel = QtWidgets.QTextEdit.ExtraSelection()
                sel.cursor = cursor
                sel.format.setBackground(QtGui.QColor("#d62626"))  # rot
                sel.format.setForeground(QtGui.QBrush(QtCore.Qt.white))
                sels.append(sel)

        # Bestehende andere Selections (z. B. Current-Line) im ListingView sind egal → wir setzen nur hier
        self.listings_view.setExtraSelections(sels)

    def _set_listing_text_with_map(self, listing_lines_with_srcline):
        """
        listing_lines_with_srcline: Iterable von Tupeln:
          (text_line: str, srcline: int | None)
        """
        # Wir verwenden PLAIN TEXT im QTextEdit für stabiles Position-Highlighting
        # (kein HTML, keine <b>-Header). Einen Header geben wir als erste Textzeile.
        header = "ADDR  BYTES(max3)   MNEMONIC"
        lines = [header]
        self._listing_pos_by_srcline.clear()

        # Compute offsets
        # Jeder Zeile endet mit '\n'
        offset = len(header) + 1
        buf = [header]

        for text, src_line in listing_lines_with_srcline:
            buf.append(text)
            if src_line is not None:
                self._listing_pos_by_srcline[src_line] = (offset, len(text))
            offset += len(text) + 1  # + '\n'

        full_text = "\n".join(buf)
        self.listings_view.setPlainText(full_text)
        
        # Nach dem Setzen: Highlights gemäß aktiven Breakpoints anwenden
        self._apply_listing_highlights()
        self._apply_c64_font()

    def _init_menu(self):
        bar = self.menuBar()
        m_file = bar.addMenu("&Datei")
        m_file.addAction(self.actLoad)
        m_file.addAction(self.actSave)

        m_proj = bar.addMenu("&Projekt")
        m_proj.addAction(self.actCompileBasic)
        m_proj.addAction(self.actAssemble)
        m_proj.addAction(self.actExportD64)
        m_proj.addAction(self.actRunVice)

        m_edit = bar.addMenu("&Einstellungen")
        self.actSettings = m_edit.addAction("Settings…")
        self.actSettings.triggered.connect(self.open_settings_dialog)
        
    def _init_toolbar(self):
        tb = QtWidgets.QToolBar("Main")
        tb.setIconSize(QtCore.QSize(16, 16))
        self.addToolBar(QtCore.Qt.TopToolBarArea, tb)

        # Buttons ohne Icons
        self.actLoad   = tb.addAction("Load")
        self.actSave   = tb.addAction("Save")
        tb.addSeparator()
        self.actCompileBasic = tb.addAction("Compile BASIC→ASM")
        self.actAssemble     = tb.addAction("Assemble")
        tb.addSeparator()
        self.actExportD64    = tb.addAction("Export D64")
        self.actRunVice      = tb.addAction("Run in VICE")
        
        self.actSettingsTB = self.addToolBar("Config").addAction("Settings…")
        self.actSettingsTB.triggered.connect(self.open_settings_dialog)

        # Callbacks
        self.actLoad.triggered.connect(self.load_cb)
        self.actSave.triggered.connect(self.save_cb)
        self.actCompileBasic.triggered.connect(self.compile_basic_cb)
        self.actAssemble.triggered.connect(self.assemble_cb)
        self.actExportD64.triggered.connect(self.export_d64_cb)
        self.actRunVice.triggered.connect(self.run_vice_cb)

    def open_settings_dialog(self):
        dlg = SettingsDialog(self.settings, self)
        dlg.exec_()
        
    # --- Datei-IO (minimal) ---
    def load_cb(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Load ASM", "", "ASM (*.asm);;All (*.*)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.asm_editor.setPlainText(f.read())
            self._apply_c64_font()
    def save_cb(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save ASM", "", "ASM (*.asm);;All (*.*)")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.asm_editor.toPlainText())

    def load_runtime_pre(self):
        s = self.settings
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
        self, "Runtime (vor BASIC) laden",
        s.runtime_pre_file(), "ASM (*.asm);;All (*.*)")
        if path:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                self.runtime_pre_editor.setPlainText(f.read())

    def save_runtime_pre(self):
        s = self.settings
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Runtime (vor BASIC) speichern",
            s.runtime_pre_file(),
            "ASM (*.asm);;All (*.*)"
        )
        if not path:
            return
        # Overwrite-Dialog manuell
        if os.path.exists(path):
            ret = QtWidgets.QMessageBox.question(
                self, "Überschreiben?",
                f"Datei existiert bereits:\n{path}\n\nÜberschreiben?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if ret != QtWidgets.QMessageBox.Yes:
                return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.runtime_pre_editor.toPlainText())

    def load_runtime_post(self):
        s = self.settings
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
        self, "Runtime (nach BASIC) laden",
        s.runtime_post_file(), "ASM (*.asm);;All (*.*)")
        if path:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                self.runtime_post_editor.setPlainText(f.read())

    def save_runtime_post(self):
        s = self.settings
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Runtime (nach BASIC) speichern",
            s.runtime_pre_file(),
            "ASM (*.asm);;All (*.*)"
        )
        if not path:
            return
        # Overwrite-Dialog manuell
        if os.path.exists(path):
            ret = QtWidgets.QMessageBox.question(
                self, "Überschreiben?",
                f"Datei existiert bereits:\n{path}\n\nÜberschreiben?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No
            )
            if ret != QtWidgets.QMessageBox.Yes:
                return
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.runtime_post_editor.toPlainText())
    
    # --- BASIC→ASM Compiler-Callback (Platzhalter) ---
    def compile_basic_cb(self):
        """
        Hier rufst du deinen BASIC→ASM-Mini-Compiler auf.
        Erwartet: asm_output:str
        Optional: du kannst auch direkt 'self.asm_editor' befüllen, wenn du möchtest.
        """
        src = self.basic_editor.toPlainText()
        asm_text, lblmap = compile_basic_to_asm(src)
        self.asm_out_editor.setPlainText(asm_text)
        # optional: merken, dass Listing aus BASIC stammt
        self._last_listing_source = "asm"  # bleibt „asm“, da wir ASM-Text erzeugen
        
        #basic_src = self.basic_editor.toPlainText()
        # TODO: DEIN Compiler
        #asm_output = self._mock_basic_to_asm(basic_src)
        #self.asm_out_editor.setPlainText(asm_output)
        self._apply_c64_font()

    def _mock_basic_to_asm(self, basic_src: str) -> str:
        # Minimal-Dummy: generiert ein kleines RTS-Programm
        return "; generated from BASIC (mock)\n* = $0000\n  rts\n"

    # self.assembler.rows: List[ (addr_str, bytes_list, mnemonic_str, srcline) ]
    def _rows_to_listing_lines(self, rows):
        # Baue die Zeilen im Format: "AAAA: BB BB BB  MNEMONIC ..."
        out = []
        for addr_str, bytes_list, mnemonic_str, srcline in rows:
            bytes_txt = " ".join(f"{b:02X}" for b in bytes_list[:3]).ljust(8)  # max3 für Spaltenbild
            line_txt = f"{int(addr_str,16):04X}: {bytes_txt}  {mnemonic_str}"
            out.append((line_txt, srcline))
        return out
    
    def assemble_cb(self):
        # Quelle: nehme ASM aus ASM-Output (falls vorhanden), sonst aus ASM-Editor
        #asm_text = self.asm_out_editor.toPlainText() or self.asm_editor.toPlainText()
        asm_text = self._compose_final_asm()
        # .org erzwingen? (falls du im UI ein Toggle hast)
        # self.assembler.ignore_org = True/False
        # self.assembler.org = gewünschter Start (bei „Variante A“ später egal)
        payload, org, listing_lines = self.assembler.assemble(asm_text)
        self._last_payload = payload
        self._last_rows = self.assembler.rows
        self._last_listing_source = "asm"  # <— wichtig

        # Anzeige: Code-Start = BASIC-Stub-Ende (wird beim PRG-Build bestimmt)
        # Hier fürs Listing/Hex erstmal org oder 0x0801 anzeigen:
        #code_start_for_view = org  # oder 0x0801, je nach Wunsch
        #self._refresh_hex_main(code_start_for_view, payload)
        #self._refresh_hex_instr(self._last_rows)
        
        # Hex links (wie gehabt)
        self._refresh_hex_main(org, payload)
        # Listing unten: aus rows → Text + Mapping
        lines_with_src = self._rows_to_listing_lines(self._last_rows)
        self._set_listing_text_with_map(lines_with_src)
        
        self._apply_c64_font()

    # --- Export D64 (Variante A) ---
    def export_d64_cb(self):
        try:
            assembled = getattr(self, "_last_payload", None)
            if not assembled:
                QtWidgets.QMessageBox.warning(self, "Export", "Bitte erst 'Assemble' ausführen.")
                return
                
            prg = build_prg_with_basic_autostart(assembled)
            write_prg_file(self.settings.prg_file(), prg)  # aus deinem runner/settings
            
            QtWidgets.QMessageBox.information(self, "Export",
                    f"PRG geschrieben: {s.prg_file()}\nSYS {code_start} (Variante A)")
        
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Export Fehler", str(e))
            
        # Für die Anzeige kann man jetzt die **echte** Code-Startadresse nehmen,
        # wenn du sie nach dem PRG-Build messen willst; hier belassen wir es simpel.

    def _mock_assemble(self, asm_text: str) -> bytes:
        # Dummy: 3 Bytes RTS ($60)
        return bytes([0x60])

    # --- Run in VICE (baut D64 davor) ---
    def run_vice_cb(self):
        try:
            s = self.settings
            ensure_build_dir(s)
            assembled = getattr(self, "_last_bytes", None)
            if not assembled:
                QtWidgets.QMessageBox.warning(self, "Run", "Bitte erst 'Assemble' ausführen.")
                return

            prg, code_start = build_single_segment_prg(assembled)
            write_prg_file(s.prg_file(), prg)

            rc, cmdline = make_d64_and_run(s)
            if rc == 0:
                QtWidgets.QMessageBox.information(
                    self, "VICE gestartet",
                    f"D64: {s.d64_file()}\nSYS {code_start}\n\n{cmdline}"
                )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Run Fehler", str(e))
