# ----------------------------------------------------------------------------
# \file  dBaseRuntime.py
# \note  (c) 2025, 2026 by Jens Kallup - paule32
#        all rights reserved.
# ----------------------------------------------------------------------------
import os
import re
import sys

from PyQt5.QtCore    import Qt, QSocketNotifier, QThread, pyqtSignal, QObject
from PyQt5.QtGui     import QFont, QTextCursor, QTextCharFormat, QColor
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit

_SGR_RE = re.compile(r"\x1b\[([0-9;]*)m")

# ----------------------------------------------------------------------------
# 16 foreground ANSI terminal color values ...
# ----------------------------------------------------------------------------
FG_16 = {
     30: "#000000",  31: "#cc0000",  32: "#00aa00",  33: "#aa8800",
     34: "#0000cc",  35: "#aa00aa",  36: "#00aaaa",  37: "#cccccc",
     90: "#555555",  91: "#ff5555",  92: "#55ff55",  93: "#ffff55",
     94: "#5555ff",  95: "#ff55ff",  96: "#55ffff",  97: "#ffffff",
}
# ----------------------------------------------------------------------------
# 16 background ANSI terminal color values ...
# ----------------------------------------------------------------------------
BG_16 = {
     40: "#000000",  41: "#550000",  42: "#005500",  43: "#554400",
     44: "#000055",  45: "#550055",  46: "#005555",  47: "#777777",
    100: "#555555", 101: "#ff5555", 102: "#55ff55", 103: "#ffff55",
    104: "#5555ff", 105: "#ff55ff", 106: "#55ffff", 107: "#ffffff",
}

# ----------------------------------------------------------------------------
# ANSI states ...
# ----------------------------------------------------------------------------
class AnsiState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.bold = False
        self.inverse = False
        self.fg = QColor("#00ff66")
        self.bg = QColor("#000000")

    def to_format(self) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fg = self.bg if self.inverse else self.fg
        bg = self.fg if self.inverse else self.bg
        fmt.setForeground(fg)
        fmt.setBackground(bg)
        fmt.setFontWeight(QFont.Bold if self.bold else QFont.Normal)
        return fmt

    def apply_sgr(self, params):
        if not params:
            params = [0]
        i = 0
        while i < len(params):
            p = params[i]
            if p == 0:
                self.reset()
            elif p == 1:
                self.bold = True
            elif p == 22:
                self.bold = False
            elif p == 7:
                self.inverse = True
            elif p == 27:
                self.inverse = False
            elif p == 39:
                self.fg = QColor("#00ff66")
            elif p == 49:
                self.bg = QColor("#000000")
            elif p in FG_16:
                self.fg = QColor(FG_16[p])
            elif p in BG_16:
                self.bg = QColor(BG_16[p])
            i += 1

def iter_ansi_chunks(text: str, state: AnsiState):
    pos = 0
    for m in _SGR_RE.finditer(text):
        if m.start() > pos:
            yield text[pos:m.start()], state.to_format()
        raw = m.group(1)
        params = [int(x) for x in raw.split(";") if x.strip().isdigit()] if raw else []
        state.apply_sgr(params)
        pos = m.end()
    if pos < len(text):
        yield text[pos:], state.to_format()

# ----------------------------------------------------------------------------
# command router - the commands ...
# ----------------------------------------------------------------------------
class CommandRouter(QObject):
    output = pyqtSignal(str)  # ANSI text output

    def execute(self, line: str) -> None:
        # WICHTIG: NICHT strip() benutzen, wenn du Spaces erhalten willst.
        # Nur Zeilenende entfernen (Enter liefert oft kein \n hier, aber sicher ist sicher):
        line = line.rstrip("\r\n")

        # "leer?" prüfen, ohne Original zu zerstören
        if not line.strip():
            self.output.emit("")
            return

        # Command-Name extrahieren, ohne Zwischenräume zu normalisieren
        lstripped = line.lstrip()
        # name = erstes "Wort", rest = alles danach (inkl. Spaces)
        first_space = lstripped.find(" ")
        if first_space == -1:
            name = lstripped.lower()
            rest = ""
        else:
            name = lstripped[:first_space].lower()
            rest = lstripped[first_space + 1:]   # <-- bleibt exakt (auch "   " und mehrfach)

        if name in ("help", "?"):
            self.output.emit(
                "\x1b[1mCommands:\x1b[0m\n"
                "  \x1b[92mhelp\x1b[0m              show help\n"
                "  \x1b[92mclear\x1b[0m             clear screen\n"
                "  \x1b[92mecho <text>\x1b[0m        print text (keeps spaces)\n"
                "  \x1b[92mcalc <expr>\x1b[0m        eval simple math\n"
            )
        elif name == "clear":
            self.output.emit("\x1b[2J\x1b[H")
        elif name == "echo":
            # rest 1:1 ausgeben, ohne "join" oder split
            self.output.emit(rest)
        elif name == "calc":
            expr = rest  # auch hier: rest nutzen
            self.output.emit(self._calc(expr))
        else:
            #self.output.emit(f"\x1b[91mUnknown command:\x1b[0m {name}")
            self.output.emit(line)

    def _calc(self, expr: str) -> str:
        # kleiner, sicherer Mathe-Evaluator (nur Zahlen + Operatoren)
        if not expr or re.search(r"[^0-9\.\+\-\*\/\(\)\s]", expr):
            return "\x1b[91mcalc: invalid expression\x1b[0m"
        try:
            val = eval(expr, {"__builtins__": {}}, {})
            return f"\x1b[96m{val}\x1b[0m"
        except Exception as e:
            return f"\x1b[91mcalc error:\x1b[0m {e}"


# ----------------------------------------------------------------------------
# input terminal widget ...
# ----------------------------------------------------------------------------
class TerminalWidget(QTextEdit):
    def __init__(self, router: CommandRouter, cols=80, rows=25, parent=None):
        super().__init__(parent)
        self.cols = cols
        self.rows = rows
        self.router = router
        self.router.output.connect(self.on_output)
        
        # History
        self.history = []          # list[str]
        self.history_index = 0     # 0..len(history); len(history) = "blank/new"
        self._draft = ""           # what user typed before browsing history

        font = QFont("Consolas")
        if not font.exactMatch():
            font = QFont("Courier New")
        font.setStyleHint(QFont.Monospace)
        font.setFixedPitch(True)
        font.setPointSize(11)
        self.setFont(font)

        self.setStyleSheet("""
            QTextEdit { background: #000; color: #00ff66; border: 1px solid #444; padding: 6px; }
        """)
        #self.setLineWrapMode(QTextEdit.NoWrap)
        
        # Wrap exakt an "cols" Zeichen (z.B. 80)
        self.setLineWrapMode(QTextEdit.FixedColumnWidth)
        self.setLineWrapColumnOrWidth(self.cols)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.setAcceptRichText (False)
        self.setUndoRedoEnabled(False)

        self.ansi_state = AnsiState()
        self._input_pos = 0

        self._apply_fixed_size()
        self._vscroll_visible = False
        
        self.verticalScrollBar().rangeChanged.connect(self._on_vscroll_range_changed)

        self.append_ansi("\x1b[1mCustom Terminal\x1b[0m  (type \x1b[92mhelp\x1b[0m)\n\n")
        self.prompt()

    def _apply_fixed_size(self):
        fm = self.fontMetrics()
        w = fm.horizontalAdvance("M") * self.cols + 22
        h = fm.height() * self.rows + 22
        self.setMinimumSize(w, h)
        self.setMaximumSize(w, h)

    # --- output ---
    def _on_vscroll_range_changed(self, _min, _max):
        # Scrollbar ist "aktiv", wenn sie etwas zu scrollen hat
        visible_now = (self.verticalScrollBar().maximum() > 0)

        if visible_now == self._vscroll_visible:
            return
        self._vscroll_visible = visible_now

        # MainWindow informieren (wenn vorhanden)
        w = self.window()
        if hasattr(w, "on_terminal_vscroll_toggled"):
            w.on_terminal_vscroll_toggled(visible_now)
            
    def append_ansi(self, text: str):
        # minimal support for "clear screen" sequence from router
        if "\x1b[2J" in text and "\x1b[H" in text:
            self.clear()
            self.ansi_state.reset()
            return

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        for chunk, fmt in iter_ansi_chunks(text, self.ansi_state):
            if chunk:
                cursor.setCharFormat(fmt)
                cursor.insertText(chunk)
        self.setTextCursor(cursor)
        self.ensureCursorVisible()

    def on_output(self, text: str):
        if text:
            self.append_ansi(text)
        self.append_ansi("\n")
        self.prompt()

    # --- prompt / input ---
    def prompt(self):
        self.append_ansi("\x1b[92m> \x1b[0m")
        self._input_pos = self.textCursor().position()

        # History browsing resets to "new line"
        self.history_index = len(self.history)
        self._draft = ""

    def _current_input(self) -> str:
        full = self.document().toPlainText()
        return full[self._input_pos:]

    def _protect_cursor(self):
        if self.textCursor().position() < self._input_pos:
            c = self.textCursor()
            c.setPosition(self.document().characterCount() - 1)
            self.setTextCursor(c)

    def _replace_input(self, text: str):
        """Replace current input (from _input_pos to end) with given text."""
        cur = self.textCursor()
        cur.movePosition(QTextCursor.End)
        end_pos = cur.position()

        cur.setPosition(self._input_pos)
        cur.setPosition(end_pos, QTextCursor.KeepAnchor)
        cur.removeSelectedText()
        cur.insertText(text)

        self.setTextCursor(cur)
        self.ensureCursorVisible()

    def _history_up(self):
        if not self.history:
            return

        # first time entering history: store draft
        if self.history_index == len(self.history):
            self._draft = self._current_input()

        if self.history_index > 0:
            self.history_index -= 1
            self._replace_input(self.history[self.history_index])

    def _history_down(self):
        if not self.history:
            return

        if self.history_index < len(self.history):
            self.history_index += 1

            if self.history_index == len(self.history):
                # back to draft/new
                self._replace_input(self._draft)
            else:
                self._replace_input(self.history[self.history_index])

    def keyPressEvent(self, event):
        self._protect_cursor()

        # Backspace nur im Input-Bereich
        if event.key() == Qt.Key_Backspace and self.textCursor().position() <= self._input_pos:
            return

        # History navigation
        if event.key() == Qt.Key_Up:
            self._history_up()
            return
        if event.key() == Qt.Key_Down:
            self._history_down()
            return

        # Enter -> ausführen
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            line = self._current_input()
            self.append_ansi("\n")

            # Für "ist leer?" nur testen, aber NICHT die Zeile verändern:
            if line.strip():  # enthält irgendwas außer whitespace
                # Originalzeile (inkl. Leerzeichen) speichern:
                if not self.history or self.history[-1] != line:
                    self.history.append(line)

            # History-Index zurück auf "neu"
            self.history_index = len(self.history)
            self._draft = ""

            self.router.execute(line)
            self._input_pos = self.textCursor().position()
            return

        # Navigation in alten Output blocken (optional)
        if event.key() in (Qt.Key_Left, Qt.Key_Home, Qt.Key_PageUp):
            if self.textCursor().position() <= self._input_pos:
                return

        super().keyPressEvent(event)
        self._protect_cursor()

# ----------------------------------------------------------------------------
# container main window ...
# ----------------------------------------------------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("80x25 Custom Terminal")
        
        self.router = CommandRouter()
        self.term = TerminalWidget(self.router, cols=80, rows=25)

        self.setCentralWidget(self.term)
        
        # Basisgröße (ohne Scrollbar) festnageln
        base = self.term.sizeHint()
        self._base_w = base.width()
        self._base_h = base.height()

        # Scrollbar-Breite ermitteln (Style-konform)
        self._sb_w = self.term.verticalScrollBar().sizeHint().width()
        if self._sb_w <= 0:
            self._sb_w = QApplication.style().pixelMetric(QApplication.style().PM_ScrollBarExtent)

        # Nicht resizable
        self.setFixedSize(self._base_w, self._base_h)
        
        # Minimize erlauben, Maximize verbieten:
        flags = self.windowFlags()
        flags |= Qt.WindowMinimizeButtonHint
        flags &= ~Qt.WindowMaximizeButtonHint
        self.setWindowFlags(flags)
        
        self.setMinimumWidth(662)
        self.setMinimumHeight(470)
        
    def on_terminal_vscroll_toggled(self, visible: bool):
        #extra = self._sb_w if visible else 0
        #self.setFixedSize(self._base_w + extra, self._base_h)
        if visible:
            self.term.setMinimumWidth(680)
            self.setMinimumWidth(660)
            self.setMinimumHeight(470)
        else:
            self.setMinimumWidth(662)
            self.setMinimumHeight(470)

# ----------------------------------------------------------------------------
# entry point of each Qt5 application ...
# ----------------------------------------------------------------------------
def EntryPoint():
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
    
# ----------------------------------------------------------------------------
# run time library house keeper ...
# ----------------------------------------------------------------------------
var_registry = {
    "info": [           # source informations
        "var"   : 0,    # count variabl's
        "class" : 0,    # count class's
        "method": 0,    # count method's
    ],
    "var": [ {          # table dictionary for variables
        "name"  : "_app", # dbase default application variable
        "type"  : None,
        "parent": None,
        "value" : None,
        } ],
    } ],
    "class": [          # table dictionary for classes
        {
        # base class informations
        "name": "FORM", # std. Form class
        "parent": None, # parent class
        
        # FORN event handlers
        "onClick"       : None,
        "onGotFocus"    : None,
        "onLostFocus"   : None,
        },
    ]
}            
# ----------------------------------------------------------------------------
# run time library functionality ...
# ----------------------------------------------------------------------------
class RT:
    def __init__(self, runner=None):
        self.runner = runner  # optional: reuse your dBaseRunner instance

    # -----------------------------------------------------------------------
    # \brief  write text into the terminal window
    # \param  args - dynamic argument list
    # \return True, if execute fine, else rause exception
    # \since  version 0.0.1
    # -----------------------------------------------------------------------
    def WRITE(self, *args):
        if len(args) <= 0:
            return
        sz = ""
        for v in args:
            if isinstance(v, str):
                sz += "String: " + v
            if isinstance(v, int):
                sz += "Int: " + v
            if isinstance(v, float):
                sz += "Float: " + v
            else:
                sz += "Other: " + type(v) + " " + v
        print(sz)

    def NEW(self, class_name: str, *args):
        return self.runner.new_instance(class_name.upper(), list(args))

    def GET(self, base, path):
        cur = base
        for p in path:
            cur = self.runner.get_member(cur, p, None)
        return cur

    def SET(self, base, path, value):
        self.runner.set_property_path(base, path, value, None)
        return value

    def PARAMETER(self, names):
        # mappe das auf deine Runner-Logik (Scope-Setup)
        return self.runner._parameter(names)
    
    def CALL(self, base, path, args):
        # if last segment is method name, resolve then call your runner logic
        # (depends on how your runner currently calls methods)
        return self.runner.call_path(base, path, args)

    def BINOP(self, a, op, b):
        return self.runner.binop(a, op, b)

    def TRUE(self, v):
        return bool(v)

    # -----------------------------------------------------------------------
    # \brief set the name of a variable "name" with the "value"
    # \see   GET_NAME
    # \since version 0.0.1
    # -----------------------------------------------------------------------
    def SET_NAME(self, name, value):
        try:
            name = strip(name[:32]).rstrip().upper()
            if name in var_registry:
                var_registry["info"]["var"] += 1
            # ---------------------------------------
            # set the properties of an dict. item ...
            # ---------------------------------------
            prop = {
                "type"  : type(value),
                "parent": None,
                "name"  : name,
                "value" : value,
            }
            var_registry["var"].append(prop)
        except:
            raise Exception("SET_NAME: ", name)
        return True
    
    # -----------------------------------------------------------------------
    # \brief  get the "value" of a variable "name"
    # \param  name - str
    # \return any saved type, else exception if name ist not registered.
    # \see    SET_NAME
    # \since  version 0.0.1
    # -----------------------------------------------------------------------
    def GET_NAME(self, name):
        try:
        except:
            rause Exception("GET_NAME: could not get value of:", name)
        return True

    def DELETE_NAME(self, name):
        return self.runner._delete_name(name)

    def PUSH_WITH(self, base):
        # du hast im Runner bereits current_with_base benutzt
        self.runner.current_with_base = base

    def POP_WITH(self):
        self.runner.current_with_base = None

    def WITH_SET(self, path, value):
        base = self.runner.current_with_base
        if base is None:
            raise RuntimeError("WITH_SET ohne aktives WITH")
        self.runner.set_property_path(base, path, value, None)
        return value

    def CREATE_FILE(self, arg):
        return self.runner._create_file(arg)
        
    def RANGE_INCL(self, start, end, step):
        # inclusive range (works for ints; for floats define policy)
        start = int(start); end = int(end); step = int(step)
        if step == 0: raise ValueError("step=0")
        if step > 0:
            return range(start, end + 1, step)
        else:
            return range(start, end - 1, step)

    def MAKE_INSTANCE(self, py_obj, args):
        # optional hook if you want Python class instances to wrap your Instance
        return None
 