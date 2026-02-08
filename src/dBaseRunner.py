# ---------------------------------------------------------------------------
# File:   dBaseRunner.py
# Author: (c) 2024, 2025, 2026 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
from __future__  import annotations

from antlr4      import (
     InputStream, FileStream, CommonTokenStream, Token,
     ParserRuleContext)

from dataclasses import dataclass, field
from typing      import Dict, List, Optional, Union, Any
from pathlib     import Path
from copy        import deepcopy

from gen.dBaseLexer         import dBaseLexer
from gen.dBaseParser        import dBaseParser
from gen.dBaseParserVisitor import dBaseParserVisitor

import traceback
import sys
import os
import re
import pprint

# ---------------------------------------------------------------------------
# Qt Backend Factory + Property Mapping
# ---------------------------------------------------------------------------
from PyQt5.QtCore    import (
    QObject, Qt, QSocketNotifier, pyqtSignal, QEvent, QRect, QSize, QRegExp,
    QFileInfo, QPoint
)
from PyQt5.QtGui     import (
    QFont, QPainter, QFontMetrics, QSyntaxHighlighter, QTextCharFormat,
    QColor, QStandardItemModel, QStandardItem
)
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QPushButton, QVBoxLayout,
    QTextEdit, QToolBar, QStatusBar, QMessageBox, QPlainTextEdit, QAction,
    QFileDialog, QMenuBar, QMdiArea, QMdiSubWindow, QTreeView, QSplitter,
    QHBoxLayout, QComboBox, QTabWidget, QListWidget, QListWidgetItem,
    QMenu, QFileDialog, QFileIconProvider, QListWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QStyledItemDelegate, QGroupBox, QLabel,
    QLineEdit, QCheckBox, QRadioButton, QSpacerItem, QGridLayout, QSpinBox,
    QSizePolicy
)

TYPE_VALUES = [
    "Character",
    "Numeric",
    "Float",
    "Integer",
    "Date",
    "DateTime",
    "Logical",
    "Memo",
]

NATIVE_BASES = {
    "FORM": QDialog,          # oder QDialog, wenn FORM per default Dialog sein soll
    "DIALOG": QDialog,
    "PUSHBUTTON": QPushButton,
}

@dataclass
class FontValue:
    obj      : QFont
    family   : str  = "Arial"
    size     : int  = 10
    bold     : bool = False
    italic   : bool = False
    underline: bool = False
    
def ensure_qt_app():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    return app

# ---------------------------------------------------------------------------
# Runtime Datenstrukturen
# ---------------------------------------------------------------------------
@dataclass
class CompileError:
    line: int
    column: int
    message: str

@dataclass
class MethodDef:
    params: list[str]
    block_ctx: object   # BlockContext

@dataclass
class PPFrame:
    parent_active: bool
    this_active: bool
    saw_else: bool = False
    start_file: Path | None = None
    start_line: int | None = None
    kind: str | None = None
    name: str | None = None

@dataclass
class Frame:
    name: str = "<anon>"
    vars: dict[str, Any] = field(default_factory=dict)
    args: list[Any] = field(default_factory=list)     # DO ... WITH Argumente

@dataclass
class Macro:
    name: str
    params: list[str] | None  # None => object-like
    body: str

@dataclass
class Instance:
    class_name: str
    backend: Any = None   # Qt Object
    props: Dict[str, object] = field(default_factory=dict)
    children: Dict[str, "Instance"] = field(default_factory=dict)
    
    def get_prop(self, name: str) -> Any:
        return self.props.get(name.upper())

    def set_prop(self, name: str, value: Any):
        self.props[name.upper()] = value
        
@dataclass
class Delegate:
    target: "Instance"
    method_name: str
    runner: Optional[object] = None

    def __call__(self, *args):
        if self.runner is None:
            raise RuntimeError("Delegate hat keinen runner")
        return self.runner.invoke_method(self.target, self.method_name, list(args), None)

@dataclass
class ClassDef:
    name: str
    parent: str | None = None
    methods: dict[str, object] = field(default_factory = dict)        # methodname -> MethodDeclContext
    default_props: dict[str, object] = field(default_factory = dict)  # defaults
    inits: list[object] = field(default_factory = list)
    
@dataclass
class BoundMethod:
    target: "Instance"
    name: str
#    obj: object
#    method: MethodDef
#    runner: object  # z.B. dein Visitor/Runner, der Blöcke ausführt
#
#    def __call__(self, *args):
#        # self/this vorne dran, wenn du OOP so modellierst:
#        return self.runner.call_method(self.obj, self.method, list(args))
        
# ---- Exceptions -------------------------------------------------------------
class ReturnSignal(Exception):
    def __init__(self, value=None, has_value: bool = False):
        super().__init__(self, value)
        self.value = value
        self.has_value = has_value

class UnterminatedBlockCommentError(Exception):
    def __init__(self, line, column, message="unterminated block comment"):
        super().__init__(f"{line}:{column}: {message}")
        self.line    = line
        self.column  = column
        self.message = message

class KeyError(Exception):
    def __init__(self, name, message="Zuordnungs-Fehler"):
        super().__init__(self, name)
        self.name    = name
        self.message = message

class BreakSignal(Exception):
    """Interner Control-Flow für BREAK (nur Schleifen fangen das ab)."""
    pass

class PreprocessorError(Exception):
    pass

# Interner Control-Flow für RETURN aus einer Methode.
class RuntimeReturn(Exception):
    def __init__(self, value=None):
        self.value = value

def create_backend_for_base(base_name: str, parent_backend=None):
    QtClass = NATIVE_BASES.get(base_name.upper())
    if QtClass is None:
        raise RuntimeError(f"Unbekannte native Basisklasse: {base_name}")
    return QtClass(parent_backend) if parent_backend is not None else QtClass()

def apply_property_to_qt(inst: Instance, prop: str, value: Any):
    if inst.backend is None:
        return
        
    p = prop.upper()
    s = str(value)
    
    # normalisiere Zahlen (dein Interpreter nutzt evtl. float)
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    
    # Geometry: Qt braucht Left/Top/Width/Height gemeinsam
    if p in ("LEFT", "TOP", "WIDTH", "HEIGHT"):
        left   = int(inst.props.get("LEFT",    0) or   0)
        top    = int(inst.props.get("TOP",     0) or   0)
        width  = int(inst.props.get("WIDTH", 100) or 100)
        height = int(inst.props.get("HEIGHT",100) or 100)

        # update den einen Wert
        if p == "LEFT":   left   = int(value)
        if p == "TOP":    top    = int(value)
        if p == "WIDTH":  width  = int(value)
        if p == "HEIGHT": height = int(value)

        inst.props["LEFT"] = left
        inst.props["TOP"] = top
        inst.props["WIDTH"] = width
        inst.props["HEIGHT"] = height

        inst.backend.setGeometry(left, top, width, height)
        return
    
    # Text / Caption für Buttons
    if p in ("TEXT", "CAPTION"):
        if hasattr(inst.backend, "setText"):
            inst.backend.setText(s)
            return
        # Fenster/Dialog Titel
        if hasattr(inst.backend, "setWindowTitle"):
            inst.backend.setWindowTitle(s)
            return
    
    # optional: TITLE explizit
    if p == "TITLE":
        if hasattr(inst.backend, "setWindowTitle"):
            inst.backend.setWindowTitle(s)
        return
    
    # Font setzen
    if p == "FONT":
        if isinstance(value, FontValue):
            f = QFont(value.family, int(value.size))
            f.setBold(bool(value.bold))
            f.setItalic(bool(value.italic))
            f.setUnderline(bool(value.underline))
            if hasattr(inst.backend, "setFont"):
                inst.backend.setFont(f)
            return

def set_prop_runtime(inst: Instance, name: str, value: Any):
    inst.set_prop(name, value)
    apply_property_to_qt(inst, name, value)

def form_open(inst: Instance):
    if inst.backend is None:
        return
    modal = bool(inst.props.get("modal", False))

    # QDialog
    if hasattr(inst.backend, "show"):
        if modal:
            if hasattr(inst.backend, "show"):
                inst.backend.setModal(False)
                inst.backend.setWindowModality(Qt.NonModal) 
                sub = MAINAPP.mdi.addSubWindow(inst.backend)
                sub.resize(360,400)
                sub.show()
            else:
                inst.backend.setModal(False)
                inst.backend.setWindowModality(Qt.NonModal) 
                sub = MAINAPP.mdi.addSubWindow(inst.backend)
                sub.resize(360,400)
                sub.show()
        else:
            # todo: remove 2 lines below
            if hasattr(inst.backend, "show"):
                inst.backend.setModal(False)
                inst.backend.setWindowModality(Qt.NonModal) 
                sub = MAINAPP.mdi.addSubWindow(inst.backend)
                sub.resize(360,400)
                sub.show()
                
            #inst.backend.show()
        return

    # QWidget
    # todo: remove 2 lines below
    if hasattr(inst.backend, "show"):
        inst.backend.setModal(False)
        sub = MAINAPP.mdi.addSubWindow(inst.backend)
        sub.resize(360,400)
        sub.show()
        
    #inst.backend.show()

class Preprocessor:
    include_re = re.compile(r'^\s*#include\s+"([^"]+)"\s*$')
    define_re  = re.compile(r'^\s*#define\s+([A-Za-z_]\w*)(.*)\s*$')
    ifdef_re   = re.compile(r'^\s*#ifdef\s+([A-Za-z_]\w*)\s*$')
    ifndef_re  = re.compile(r'^\s*#ifndef\s+([A-Za-z_]\w*)\s*$')
    else_re    = re.compile(r'^\s*#else\s*$')
    endif_re   = re.compile(r'^\s*#endif\s*$')

    def __init__(self, *, include_paths: list[Path] | None = None):
        self.include_paths = include_paths or []
        self.macros: dict[str, Macro] = {}
        self.defined: set[str] = set()
        self._include_stack: list[Path] = []

    def _split_args(self, s: str) -> list[str]:
        # s ist Inhalt zwischen den äußeren (...) eines Calls
        args = []
        cur = []
        depth = 0
        i = 0
        while i < len(s):
            ch = s[i]
            if ch == "(":
                depth += 1
                cur.append(ch)
            elif ch == ")":
                depth -= 1
                cur.append(ch)
            elif ch == "," and depth == 0:
                args.append("".join(cur).strip())
                cur = []
            else:
                cur.append(ch)
            i += 1
        if cur or s.strip() == "":
            args.append("".join(cur).strip())
        return args

    def _stringize(self, arg_text: str) -> str:
        # Whitespace normalisieren wie C-ish
        norm = " ".join(arg_text.split())
        norm = norm.replace("\\", "\\\\").replace('"', '\\"')
        return f"\"{norm}\""

    def _expand_function_macro(self, macro: Macro, call_args: list[str]) -> str:
        if macro.params is None:
            raise PreprocessorError("internal: not a function macro")

        if len(call_args) != len(macro.params):
            raise PreprocessorError(
                f"macro {macro.name} expects {len(macro.params)} args, got {len(call_args)}"
            )

        argmap = dict(zip(macro.params, call_args))

        # body als Arbeitsstring
        body = macro.body

        # 1) stringize: #param  (nur wenn param direkt folgt)
        #    Beispiel: #x
        for p in macro.params:
            body = re.sub(rf'#\s*{re.escape(p)}\b',
                          lambda m, p=p: self._stringize(argmap[p]),
                          body)

        # 2) token paste: a ## b  (pragmatisch: Strings zusammenkleben)
        #    Wir machen das iterativ, solange es '##' gibt.
        #    Dabei erlauben wir links/rechts: param oder direktes Wort/Token
        while "##" in body:
            m = re.search(r'(\S+)\s*##\s*(\S+)', body)
            if not m:
                break
            left = m.group(1)
            right = m.group(2)

            # param ersetzen, falls es param ist
            left_val = argmap.get(left, left)
            right_val = argmap.get(right, right)

            # Wenn left_val ein Stringliteral ist ("..."), quotes entfernen und concat
            if left_val.startswith('"') and left_val.endswith('"'):
                left_inner = left_val[1:-1]
                # right_val: wenn auch string, ohne quotes
                if right_val.startswith('"') and right_val.endswith('"'):
                    right_part = right_val[1:-1]
                else:
                    right_part = right_val
                glued = f"\"{left_inner}{right_part}\""
            else:
                glued = f"{left_val}{right_val}"

            body = body[:m.start()] + glued + body[m.end():]

        # 3) normale param substitution (für verbleibende params im body)
        for p in macro.params:
            body = re.sub(rf'\b{re.escape(p)}\b', argmap[p], body)

        return body

    def _expand_macros_in_line(self, line: str) -> str:
        # Sehr einfache, iterative Expansion (mit Limit gegen Endlosschleifen)
        out = line
        for _ in range(50):
            changed = False

            # 1) function-like macros: NAME(...)
            #    Suche NAME( ... ) und expandiere
            for name, macro in list(self.macros.items()):
                if macro.params is None:
                    continue

                # finde "name(" in der Zeile
                idx = out.find(name + "(")
                while idx != -1:
                    # parse bis passendes ')'
                    j = idx + len(name) + 1
                    depth = 1
                    while j < len(out) and depth > 0:
                        if out[j] == "(":
                            depth += 1
                        elif out[j] == ")":
                            depth -= 1
                        j += 1
                    if depth != 0:
                        # unbalanciert -> abbrechen
                        break

                    inside = out[idx + len(name) + 1 : j - 1]
                    args = self._split_args(inside)
                    repl = self._expand_function_macro(macro, args)

                    out = out[:idx] + repl + out[j:]
                    changed = True

                    idx = out.find(name + "(", idx + len(repl))
                # next macro

            # 2) object-like macros: \bNAME\b
            for name, macro in list(self.macros.items()):
                if macro.params is not None:
                    continue
                # ganzes Wort ersetzen
                new_out = re.sub(rf'\b{re.escape(name)}\b', macro.body, out)
                if new_out != out:
                    out = new_out
                    changed = True

            if not changed:
                break

        return out

    def process(self, filename: str | Path) -> str:
        #data = Path(filename).read_text(encoding="utf-8")
        #data = re.sub(r'(?i)\bNEW(?=[A-Za-z_])', 'NEW ', data)
        #data = re.sub(r'(?i)\bCALL(?=[A-Za-z_])', 'CALL ', data)
        #with open(filename,"w",encoding="utf-8") as f:
        #    f.write(data)
        #    f.close()
            
        entry = Path(filename).resolve()
        return self._process_file(entry)

    def _resolve_include(self, current_file: Path, name: str) -> Path:
        # 1) relativ zum aktuellen file
        cand = (current_file.parent / name).resolve()
        if cand.exists():
            return cand

        # 2) include_paths
        for base in self.include_paths:
            cand2 = (base / name).resolve()
            if cand2.exists():
                return cand2

        raise PreprocessorError(f'include file not found: "{name}" (from {current_file})')
        
    # Schneidet trailing Kommentare ab: &&, **, //, /* ...
    # (Nur bis Zeilenende; Blockkommentar-Mehrzeiligkeit ist für Direktiven egal,
    # weil nach der Direktive sowieso nichts mehr ausgewertet werden soll.)
    def _strip_trailing_comment(self, s: str) -> str:
        markers = ["&&", "**", "//", "/*"]
        cut = None
        for m in markers:
            pos = s.find(m)
            if pos != -1 and (cut is None or pos < cut):
                cut = pos
        return s if cut is None else s[:cut]
        
    def _process_file(self, path: Path) -> str:
        if path in self._include_stack:
            chain = " -> ".join(str(p) for p in self._include_stack + [path])
            raise PreprocessorError(f"circular include detected: {chain}")

        self._include_stack.append(path)
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            out_lines: list[str] = []
            frames: list[PPFrame] = [PPFrame(parent_active=True, this_active=True)]

            def active() -> bool:
                return frames[-1].parent_active and frames[-1].this_active

            lines = text.splitlines(keepends=True)
            for i, line in enumerate(lines, start=1):
                # Direktiven erkennen (immer), aber nur ausführen wenn "active"
                raw_line = line
                line = self._strip_trailing_comment(line).rstrip("\r\n")
                m = self.include_re.match(line)
                if m:
                    if active():
                        inc_name = m.group(1)
                        inc_path = self._resolve_include(path, inc_name)
                        out_lines.append(f'**line 1 "{inc_path}"*/\n')
                        out_lines.append(self._process_file(inc_path))
                        out_lines.append(f'**line {i+1} "{path}"*/\n')
                    continue
                    
                m = self.define_re.match(line)
                if m:
                    if active():
                        name = m.group(1)
                        tail = (m.group(2) or "").strip()

                        # function-like: direkt nach Name "("
                        if tail.startswith("("):
                            close = tail.find(")")
                            if close == -1:
                                raise PreprocessorError(f"{path}:{i}: malformed function-like #define")
                            params_part = tail[1:close].strip()
                            body = tail[close+1:].lstrip()

                            params = [p.strip() for p in params_part.split(",")] if params_part else []
                            self.macros[name] = Macro(name=name, params=params, body=body)
                        else:
                            self.macros[name] = Macro(name=name, params=None, body=tail)

                        self.defined.add(name)
                    continue
                
                m = self.ifdef_re.match(line)
                if m:
                    name = m.group(1)
                    parent = active()
                    cond = name in self.defined
                    frames.append(PPFrame(
                        parent_active=parent,
                        this_active=cond,
                        start_file=path,
                        start_line=i,
                        kind="#ifdef",
                        name=name
                    ))
                    continue

                m = self.ifndef_re.match(line)
                if m:
                    name = m.group(1)
                    parent = active()
                    cond = name not in self.defined
                    frames.append(PPFrame(
                        parent_active=parent,
                        this_active=cond,
                        start_file=path,
                        start_line=i,
                        kind="#ifndef",
                        name=name
                    ))
                    continue

                if self.else_re.match(line):
                    if len(frames) == 1:
                        raise PreprocessorError(f"{path}:{i}: #else without #if")
                    top = frames[-1]
                    if top.saw_else:
                        raise PreprocessorError(f"{path}:{i}: multiple #else")
                    top.saw_else = True
                    # else invertiert nur die "this_active" Ebene, parent bleibt gleich
                    top.this_active = not top.this_active
                    continue

                if self.endif_re.match(line):
                    if len(frames) == 1:
                        raise PreprocessorError(f"{path}:{i}: #endif without #if")
                    frames.pop()
                    continue

                # Normale Zeile: nur ausgeben wenn aktiv
                if active():
                     out_lines.append(self._expand_macros_in_line(raw_line))

            if len(frames) != 1:
                top = frames[-1]
                raise PreprocessorError(
                    f"{path}: EOF: missing #endif for {top.kind} {top.name} "
                    f"(opened at {top.start_file}:{top.start_line})"
                )
                
            return "".join(out_lines)
        finally:
            self._include_stack.pop()
            
class Symbols:
    def __init__(self) -> None:
        self.classes: Dict[str, object] = {}

    def has_class(self, name: str) -> bool:
        # dBase ist oft case-insensitive -> normalisieren:
        return name.upper() in self.classes

    def add_class(self, name: str, node: object) -> None:
        self.classes[name.upper()] = node

class SemanticVisitor(dBaseParserVisitor):
    def __init__(self):
        super().__init__()
        self.symbols = Symbols()
        self.classes = self.symbols.classes   # <- Alias
        self.errors: List[CompileError] = []
        self._current_class = None

    def error(self, ctx, msg: str):
        tok = ctx.start
        self.errors.append(CompileError(tok.line, tok.column, msg))
    
    def visitClassBody(self, ctx):
        # NUR member besuchen
        for m in ctx.classMember():
            self.visit(m)
        return None

def analyze(tree, parser):
    sema = SemanticVisitor()
    sema.visit(tree)

    if sema.errors:
        for e in sema.errors:
            print(f"{e.line}:{e.column}: error: {e.message}")
        raise SystemExit(1)

    return sema

class ScopeStack:
    def __init__(self):
        self._scopes = [{}]  # global scope

    def push(self):
        self._scopes.append({})

    def pop(self):
        if len(self._scopes) == 1:
            raise RuntimeError("Cannot pop global scope")
        self._scopes.pop()

    def set(self, name: str, value):
        self._scopes[-1][name] = value

    def get(self, name: str):
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        raise KeyError(name)

    def has(self, name: str) -> bool:
        for scope in reversed(self._scopes):
            if name in scope:
                return True
        return False

# ---------------------------------------------------------------------------
# Ein EventFilter pro Widget-Instance.
# Ruft Wrapper-Funktionen auf, die du in inst.props hinterlegst.
# ---------------------------------------------------------------------------
class _QtEventFilter(QObject):
    def __init__(self, runner, inst):
        super().__init__()
        self.runner = runner
        self.inst = inst

    def eventFilter(self, obj, event):
        t = event.type()

        if t == QEvent.FocusIn:
            cb = self.inst.props.get("_ONFOCUSIN_WRAPPER")
            if cb:
                cb(event)

        elif t == QEvent.FocusOut:
            cb = self.inst.props.get("_ONFOCUSOUT_WRAPPER")
            if cb:
                cb(event)

        elif t == QEvent.MouseMove:
            cb = self.inst.props.get("_ONMOUSEMOVE_WRAPPER")
            if cb:
                cb(event)

        elif t == QEvent.MouseButtonPress:
            cb = self.inst.props.get("_ONMOUSEDOWN_WRAPPER")
            if cb:
                cb(event)

        elif t == QEvent.MouseButtonRelease:
            cb = self.inst.props.get("_ONMOUSEUP_WRAPPER")
            if cb:
                cb(event)

            # Rechts/Links-Button Events
            try:
                if event.button() == Qt.LeftButton:
                    cb = self.inst.props.get("_ONMOUSELBUTTON_WRAPPER")
                    if cb:
                        cb(event)

                    # Click-Fallback NUR links (und nur wenn nicht via Qt.clicked)
                    if not self.inst.props.get("_ONCLICK_VIA_SIGNAL"):
                        cb = self.inst.props.get("_ONCLICK_WRAPPER")
                        if cb:
                            cb(event)

                elif event.button() == Qt.RightButton:
                    # onClick darf hier NICHT laufen!
                    cb = self.inst.props.get("_ONMOUSERBUTTON_WRAPPER")
                    if cb:
                        cb(event)

            except Exception:
                pass
        
        elif t == QEvent.KeyPress:
            cb = self.inst.props.get("_ONKEYDOWN_WRAPPER")
            if cb:
                cb(event)

        elif t == QEvent.KeyRelease:
            cb = self.inst.props.get("_ONKEYUP_WRAPPER")
            if cb:
                cb(event)

        elif t == QEvent.MouseButtonDblClick:
            cb = self.inst.props.get("_ONDBLCLICK_WRAPPER")
            if cb:
                cb(event)

        return False

class PyEmitter:
    def __init__(self):
        self.lines = []
        self.level = 0

    def emit(self, line=""):
        self.lines.append(("    " * self.level) + line)

    def indent(self): self.level += 1
    def dedent(self): self.level = max(0, self.level - 1)

    def text(self):
        return "\n".join(self.lines) + "\n"

class PasEmitter:
    def __init__(self):
        self.lines = []
        self.level = 0

    def emit(self, line=""):
        self.lines.append(("  " * self.level) + line)

    def indent(self): self.level += 1
    def dedent(self): self.level = max(0, self.level - 1)

    def text(self):
        return "\n".join(self.lines) + "\n"

class CppEmitter:
    def __init__(self):
        self.lines = []
        self.level = 0

    def emit(self, line=""):
        self.lines.append(("  " * self.level) + line)

    def indent(self): self.level += 1
    def dedent(self): self.level = max(0, self.level - 1)

    def text(self):
        return "\n".join(self.lines) + "\n"

class JavaEmitter:
    def __init__(self):
        self.lines = []
        self.level = 0

    def emit(self, line=""):
        self.lines.append(("  " * self.level) + line)

    def indent(self): self.level += 1
    def dedent(self): self.level = max(0, self.level - 1)

    def text(self):
        return "\n".join(self.lines) + "\n"

class DBaseToJava:
    def __init__(self, parser, classes=None, class_name="GenProg", package=None):
        self.p = parser
        self.out = JavaEmitter()
        self.classes = classes or {}
        self.class_name = class_name
        self.package = package
        self._tmp_i = 0

    def new_temp(self):
        self._tmp_i += 1
        return f"t{self._tmp_i}"

    def jstr(self, s: str) -> str:
        s = s.replace("\\", "\\\\").replace('"', '\\"')
        return f"\"{s}\""

    def jstr_list(self, items):
        # java.util.List.of("A","B")
        inner = ", ".join(self.jstr(x) for x in items)
        return f"java.util.List.of({inner})"

    def jval_list(self, exprs):
        # java.util.List.of(a, b, c)
        inner = ", ".join(exprs)
        return f"java.util.List.of({inner})"

    def generate(self, tree, out_path: str):
        o = self.out
        if self.package:
            o.emit(f"package {self.package};")
            o.emit("")
        o.emit("import java.util.*;")
        o.emit("")
        o.emit("public class " + self.class_name + " {")
        o.indent()
        o.emit("public static void main(String[] args) {")
        o.indent()
        o.emit("TRT rt = new TRT();")
        o.emit("try {")
        o.indent()

        self.gen_input(tree)

        o.dedent()
        o.emit("} catch (Exception e) {")
        o.indent()
        o.emit('System.err.println("ERROR: " + e.getMessage());')
        o.emit("e.printStackTrace();")
        o.dedent()
        o.emit("}")
        o.dedent()
        o.emit("}")
        o.dedent()
        o.emit("}")
        Path(out_path).write_text(o.text(), encoding="utf-8")

    # input : item* EOF
    def gen_input(self, ctx):
        for it in ctx.item():
            self.gen_item(it)

    # item : classDecl | methodDecl | statement
    def gen_item(self, it):
        if it.statement():
            return self.gen_stmt(it.statement())
        if it.classDecl():
            self.out.emit("// TODO classDecl not implemented in Java backend")
            return
        if it.methodDecl():
            self.out.emit("// TODO methodDecl not implemented in Java backend")
            return
        self.out.emit("// TODO unhandled item")

    # statement dispatcher (erweitern wie bei Python/Pascal)
    def gen_stmt(self, st):
        if st.writeStmt():         return self.gen_write(st.writeStmt())
        if st.assignStmt():        return self.gen_assign(st.assignStmt())
        if st.localDeclStmt():     return self.gen_local_decl(st.localDeclStmt())
        if st.localAssignStmt():   return self.gen_local_assign(st.localAssignStmt())
        if st.ifStmt():            return self.gen_if(st.ifStmt())
        if st.forStmt():           return self.gen_for(st.forStmt())
        if st.breakStmt():         return self.gen_break(st.breakStmt())
        if st.returnStmt():        return self.gen_return(st.returnStmt())
        if st.withStmt():          return self.gen_with(st.withStmt())
        if st.parameterStmt():     return self.gen_parameter(st.parameterStmt())
        if st.exprStmt():          return self.gen_expr_stmt(st.exprStmt())

        self.out.emit("// TODO unhandled statement: " + type(st.getChild(0)).__name__)

    # writeStmt : WRITE writeArg (PLUS writeArg)* ;
    def gen_write(self, ctx):
        parts = [self.gen_write_arg(a) for a in ctx.writeArg()]
        if not parts:
            self.out.emit("rt.WRITE(TRT.Null());")
            return

        expr = parts[0]
        for p in parts[1:]:
            expr = f"rt.BINOP({expr}, \"+\", {p})"
        self.out.emit(f"rt.WRITE({expr});")

    # writeArg : STRING | dottedRef | expr ;
    def gen_write_arg(self, actx):
        if actx.STRING():
            # actx.STRING().getText() liefert schon Anführungszeichen aus dem Lexer
            return f"TRT.V({actx.STRING().getText()})"
        if actx.dottedRef():
            base, path = self.gen_dotted_ref_parts(actx.dottedRef())
            return f"rt.GET({base}, {path})"
        if actx.expr():
            return self.gen_expr(actx.expr())
        return "TRT.Null()"

    def gen_local_decl(self, ctx):
        name = ctx.name.text if hasattr(ctx, "name") else ctx.IDENT().getText()
        self.out.emit(f"rt.SET_NAME({self.jstr(name)}, TRT.Null());")

    def gen_local_assign(self, ctx):
        name = ctx.name.text if hasattr(ctx, "name") else ctx.IDENT().getText()
        rhs = self.gen_expr(ctx.expr())
        self.out.emit(f"rt.SET_NAME({self.jstr(name)}, {rhs});")

    # lvalue : postfixExpr | dottedRef ;
    def gen_assign(self, ctx):
        rhs = self.gen_expr(ctx.expr())
        lv = ctx.lvalue()

        if lv.dottedRef():
            base, path = self.gen_dotted_ref_parts(lv.dottedRef())
            self.out.emit(f"rt.SET({base}, {path}, {rhs});")
            return

        pe = lv.postfixExpr()
        if pe:
            chain = self.lvalue_chain_from_postfix(pe)

            if len(chain) == 1:
                self.out.emit(f"rt.SET_NAME({self.jstr(chain[0])}, {rhs});")
                return

            head = chain[0]
            if head.upper() == "THIS":
                base = "rt.GET_THIS()"
                path = self.jstr_list(chain[1:])
            else:
                base = f"rt.GET_NAME({self.jstr(head)})"
                path = self.jstr_list(chain[1:])

            self.out.emit(f"rt.SET({base}, {path}, {rhs});")
            return

        self.out.emit("// TODO unsupported lvalue: " + lv.getText())

    # ifStmt : IF expr block (ELSE block)? ENDIF ;
    def gen_if(self, ctx):
        cond = self.gen_expr(ctx.expr())
        self.out.emit(f"if (rt.TRUE({cond})) {{")
        self.out.indent()

        then_block = ctx.block(0)
        for st in then_block.statement():
            self.gen_stmt(st)

        self.out.dedent()
        self.out.emit("}")

        if ctx.ELSE():
            self.out.emit("else {")
            self.out.indent()
            else_block = ctx.block(1)
            for st in else_block.statement():
                self.gen_stmt(st)
            self.out.dedent()
            self.out.emit("}")

    # forStmt : FOR IDENT ASSIGN numberExpr TO numberExpr (STEP numberExpr)? block ENDFOR ;
    def gen_for(self, ctx):
        var = ctx.IDENT().getText()
        start = ctx.numberExpr(0).getText()
        end   = ctx.numberExpr(1).getText()
        step  = ctx.numberExpr(2).getText() if ctx.STEP() else "1"

        self.out.emit(f"rt.SET_NAME({self.jstr(var)}, TRT.V({start}));")
        self.out.emit(f"while (rt.TRUE(rt.FOR_COND(rt.GET_NAME({self.jstr(var)}), TRT.V({end}), TRT.V({step})))) {{")
        self.out.indent()

        for st in ctx.block().statement():
            self.gen_stmt(st)

        self.out.emit(f"rt.SET_NAME({self.jstr(var)}, rt.BINOP(rt.GET_NAME({self.jstr(var)}), \"+\", TRT.V({step})));")
        self.out.dedent()
        self.out.emit("}")

    def gen_break(self, ctx):
        self.out.emit("break;")

    def gen_return(self, ctx):
        # Top-level main: delegiere an Runtime (z.B. Exception oder Flag)
        if ctx.expr():
            self.out.emit(f"rt.RETURN({self.gen_expr(ctx.expr())});")
        else:
            self.out.emit("rt.RETURN(TRT.Null());")

    # parameterStmt : PARAMETER paramNames ;  paramNames : IDENT (',' IDENT)* ;
    def gen_parameter(self, ctx):
        p = ctx.paramNames()
        names = [t.getText() for t in p.IDENT()]
        self.out.emit(f"rt.PARAMETER({self.jstr_list(names)});")

    # exprStmt : postfixExpr ;
    def gen_expr_stmt(self, ctx):
        e = self.gen_postfix(ctx.postfixExpr())
        self.out.emit(e + ";")

    # WITH
    def gen_with(self, ctx):
        base = self.gen_with_target(ctx.withTarget())
        tmp = self.new_temp()
        self.out.emit(f"Object {tmp} = {base};")
        self.out.emit(f"rt.PUSH_WITH({tmp});")

        body = ctx.withBody()
        for ch in list(getattr(body, "children", []) or []):
            t = type(ch).__name__
            if t.endswith("WithAssignStmtContext"):
                self.gen_with_assign(ch)
            elif t.endswith("WithStmtContext"):
                self.gen_with(ch)
            elif t.endswith("StatementContext"):
                self.gen_stmt(ch)

        self.out.emit("rt.POP_WITH();")

    def gen_with_target(self, ctx):
        if ctx.THIS():
            return "rt.GET_THIS()"
        if ctx.dottedRef():
            base, path = self.gen_dotted_ref_parts(ctx.dottedRef())
            return f"rt.GET({base}, {path})"
        if ctx.IDENT():
            return f"rt.GET_NAME({self.jstr(ctx.IDENT().getText())})"
        if ctx.postfixExpr():
            return self.gen_postfix(ctx.postfixExpr())
        return "TRT.Null()"

    def gen_with_assign(self, ctx):
        path = [t.getText() for t in ctx.withLvalue().IDENT()]
        rhs = self.gen_expr(ctx.expr())
        self.out.emit(f"rt.WITH_SET({self.jstr_list(path)}, {rhs});")

    # ----- expr/postfix/primary (runtime-backed) -----
    def gen_expr(self, ctx):
        return self.gen_logical_or(ctx.logicalOr())

    def gen_logical_or(self, ctx):
        parts = [self.gen_logical_and(x) for x in ctx.logicalAnd()]
        out = parts[0]
        for rhs in parts[1:]:
            out = f"rt.BINOP({out}, \"OR\", {rhs})"
        return out

    def gen_logical_and(self, ctx):
        parts = [self.gen_logical_not(x) for x in ctx.logicalNot()]
        out = parts[0]
        for rhs in parts[1:]:
            out = f"rt.BINOP({out}, \"AND\", {rhs})"
        return out

    def gen_logical_not(self, ctx):
        if ctx.NOT():
            inner = self.gen_logical_not(ctx.logicalNot())
            return f"rt.UNOP(\"NOT\", {inner})"
        return self.gen_comparison(ctx.comparison())

    def gen_comparison(self, ctx):
        left = self.gen_additive(ctx.additiveExpr(0))
        if ctx.compareOp():
            op = ctx.compareOp().getText()
            right = self.gen_additive(ctx.additiveExpr(1))
            return f"rt.BINOP({left}, {self.jstr(op)}, {right})"
        return left

    def gen_additive(self, ctx):
        terms = [self.gen_multiplicative(x) for x in ctx.multiplicativeExpr()]
        out = terms[0]
        kids = list(ctx.getChildren())
        i = 1
        while i < len(kids):
            op = kids[i].getText()
            rhs = terms[(i + 1) // 2]
            out = f"rt.BINOP({out}, {self.jstr(op)}, {rhs})"
            i += 2
        return out

    def gen_multiplicative(self, ctx):
        factors = [self.gen_postfix(x) for x in ctx.postfixExpr()]
        out = factors[0]
        kids = list(ctx.getChildren())
        i = 1
        while i < len(kids):
            op = kids[i].getText()
            rhs = factors[(i + 1) // 2]
            out = f"rt.BINOP({out}, {self.jstr(op)}, {rhs})"
            i += 2
        return out

    def gen_postfix(self, ctx):
        cur = self.gen_primary(ctx.primary())
        kids = list(ctx.getChildren())
        k = 1
        while k < len(kids):
            t = kids[k].getText()
            if t == "(":
                args = []
                if kids[k+1].getText() != ")":
                    argctx = kids[k+1]
                    args = [self.gen_expr(e) for e in argctx.expr()]
                    k += 1
                cur = f"rt.CALL_ANY({cur}, {self.jval_list(args)})"
                k += 2
                continue
            if t in (".", "::"):
                name = kids[k+1].getText()
                cur = f"rt.GET_ATTR({cur}, {self.jstr(name)})"
                k += 2
                continue
            k += 1
        return cur

    def gen_primary(self, ctx):
        if ctx.THIS():
            return "rt.GET_THIS()"
        if ctx.STRING():
            return f"TRT.V({ctx.STRING().getText()})"
        if ctx.NUMBER():
            return f"TRT.V({ctx.NUMBER().getText()})"
        if ctx.FLOAT():
            return f"TRT.V({ctx.FLOAT().getText()})"
        if ctx.IDENT():
            return f"rt.GET_NAME({self.jstr(ctx.IDENT().getText())})"
        if ctx.newExpr():
            return self.gen_new(ctx.newExpr())
        if ctx.expr():
            return "(" + self.gen_expr(ctx.expr()) + ")"
        return "TRT.Null()"

    def gen_new(self, ctx):
        class_name = ctx.IDENT().getText()
        args = []
        if ctx.argList():
            args = [self.gen_expr(e) for e in ctx.argList().expr()]
        return f"rt.NEW({self.jstr(class_name)}, {self.jval_list(args)})"

    def gen_dotted_ref_parts(self, dctx):
        parts = [t.getText() for t in dctx.IDENT()]
        head = parts[0]
        if head.upper() == "THIS":
            base = "rt.GET_THIS()"
            path = self.jstr_list(parts[1:])
        else:
            base = f"rt.GET_NAME({self.jstr(head)})"
            path = self.jstr_list(parts[1:])
        return base, path

    def lvalue_chain_from_postfix(self, pe):
        chain = [pe.primary().getText()]
        i = 1
        while i < pe.getChildCount():
            ch = pe.getChild(i).getText()
            if ch == ".":
                chain.append(pe.getChild(i+1).getText())
                i += 2
                continue
            if ch == "(":
                raise RuntimeError(f"LVALUE darf keinen Call enthalten: {pe.getText()}")
            i += 1
        return chain
        
class DBaseToCpp:
    def __init__(self, parser, classes=None, prog_name="genprog"):
        self.p = parser
        self.out = CppEmitter()
        self.classes = classes or {}
        self.prog_name = prog_name
        self._tmp_i = 0

    def new_temp(self):
        self._tmp_i += 1
        return f"t{self._tmp_i}"

    # ---------- helpers ----------
    def cpp_str(self, s: str) -> str:
        return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'

    def cpp_str_vec(self, items):
        # {"A","B"}
        inner = ", ".join(self.cpp_str(x) for x in items)
        return "{ " + inner + " }"

    def cpp_val_vec(self, exprs):
        # { a, b, c }
        inner = ", ".join(exprs)
        return "{ " + inner + " }"

    def norm_local(self, name: str) -> str:
        return "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in name).lower()

    # ---------- entry ----------
    def generate(self, tree, out_path: str):
        o = self.out
        o.emit("// generated dBase -> GNU C++ (runtime-backed)")
        o.emit("#include <iostream>")
        o.emit("#include <vector>")
        o.emit("#include <string>")
        o.emit("#include \"dBaseRT.hpp\"")
        o.emit("")
        o.emit("int main() {")
        o.indent()
        o.emit("TRT rt;")
        o.emit("try {")
        o.indent()

        self.gen_input(tree)

        o.dedent()
        o.emit("} catch (const std::exception& e) {")
        o.indent()
        o.emit('std::cerr << "ERROR: " << e.what() << std::endl;')
        o.emit("return 1;")
        o.dedent()
        o.emit("}")
        o.emit("return 0;")
        o.dedent()
        o.emit("}")
        Path(out_path).write_text(o.text(), encoding="utf-8")

    # ---------- root ----------
    def gen_input(self, ctx):
        for it in ctx.item():
            self.gen_item(it)

    def gen_item(self, it):
        if it.statement():
            return self.gen_stmt(it.statement())
        if it.classDecl():
            self.out.emit("// TODO classDecl not implemented in C++ backend")
            return
        if it.methodDecl():
            self.out.emit("// TODO methodDecl not implemented in C++ backend")
            return
        self.out.emit("// TODO unhandled item")

    # ---------- statements ----------
    def gen_stmt(self, st):
        if st.writeStmt():         return self.gen_write(st.writeStmt())
        if st.assignStmt():        return self.gen_assign(st.assignStmt())
        if st.localDeclStmt():     return self.gen_local_decl(st.localDeclStmt())
        if st.localAssignStmt():   return self.gen_local_assign(st.localAssignStmt())
        if st.ifStmt():            return self.gen_if(st.ifStmt())
        if st.forStmt():           return self.gen_for(st.forStmt())
        if st.breakStmt():         return self.gen_break(st.breakStmt())
        if st.returnStmt():        return self.gen_return(st.returnStmt())
        if st.withStmt():          return self.gen_with(st.withStmt())
        if st.parameterStmt():     return self.gen_parameter(st.parameterStmt())
        if st.exprStmt():          return self.gen_expr_stmt(st.exprStmt())

        self.out.emit("// TODO unhandled statement: " + type(st.getChild(0)).__name__)

    def gen_write(self, ctx):
        # writeStmt : WRITE writeArg (PLUS writeArg)* ;
        parts = [self.gen_write_arg(a) for a in ctx.writeArg()]
        if not parts:
            self.out.emit("rt.WRITE(TRT::Null());")
            return

        expr = parts[0]
        for p in parts[1:]:
            expr = f"rt.BINOP({expr}, \"+\", {p})"

        self.out.emit(f"rt.WRITE({expr});")

    def gen_write_arg(self, actx):
        if actx.STRING():
            return f"TRT::V({actx.STRING().getText()})"  # String-Literal inkl. Quotes kommt aus Lexer
        if actx.dottedRef():
            base, path = self.gen_dotted_ref_parts(actx.dottedRef())
            return f"rt.GET({base}, {path})"
        if actx.expr():
            return self.gen_expr(actx.expr())
        return "TRT::Null()"

    def gen_local_decl(self, ctx):
        name = ctx.name.text if hasattr(ctx, "name") else ctx.IDENT().getText()
        self.out.emit(f"rt.SET_NAME({self.cpp_str(name)}, TRT::Null());")

    def gen_local_assign(self, ctx):
        name = ctx.name.text if hasattr(ctx, "name") else ctx.IDENT().getText()
        rhs = self.gen_expr(ctx.expr())
        self.out.emit(f"rt.SET_NAME({self.cpp_str(name)}, {rhs});")

    def gen_assign(self, ctx):
        rhs = self.gen_expr(ctx.expr())
        lv = ctx.lvalue()

        if lv.dottedRef():
            base, path = self.gen_dotted_ref_parts(lv.dottedRef())
            self.out.emit(f"rt.SET({base}, {path}, {rhs});")
            return

        pe = lv.postfixExpr()
        if pe:
            chain = self.lvalue_chain_from_postfix(pe)

            if len(chain) == 1:
                self.out.emit(f"rt.SET_NAME({self.cpp_str(chain[0])}, {rhs});")
                return

            head = chain[0]
            if head.upper() == "THIS":
                base = "rt.GET_THIS()"
                path = self.cpp_str_vec(chain[1:])
            else:
                base = f"rt.GET_NAME({self.cpp_str(head)})"
                path = self.cpp_str_vec(chain[1:])

            self.out.emit(f"rt.SET({base}, {path}, {rhs});")
            return

        self.out.emit("// TODO unsupported lvalue: " + lv.getText())

    def gen_if(self, ctx):
        # ifStmt : IF expr block (ELSE block)? ENDIF ;
        cond = self.gen_expr(ctx.expr())
        self.out.emit(f"if (rt.TRUE({cond})) {{")
        self.out.indent()

        then_block = ctx.block(0)
        for st in then_block.statement():
            self.gen_stmt(st)

        self.out.dedent()
        self.out.emit("}")

        if ctx.ELSE():
            self.out.emit("else {")
            self.out.indent()
            else_block = ctx.block(1)
            for st in else_block.statement():
                self.gen_stmt(st)
            self.out.dedent()
            self.out.emit("}")

    def gen_for(self, ctx):
        # forStmt : FOR IDENT ASSIGN numberExpr TO numberExpr (STEP numberExpr)? block ENDFOR ;
        var = ctx.IDENT().getText()
        start = ctx.numberExpr(0).getText()
        end   = ctx.numberExpr(1).getText()
        step  = ctx.numberExpr(2).getText() if ctx.STEP() else "1"

        # Wir halten "i" als Runtime-Variable, damit Semantik identisch bleibt
        self.out.emit(f"rt.SET_NAME({self.cpp_str(var)}, TRT::V({start}));")
        self.out.emit(f"while (rt.TRUE(rt.FOR_COND(rt.GET_NAME({self.cpp_str(var)}), TRT::V({end}), TRT::V({step})))) {{")
        self.out.indent()

        for st in ctx.block().statement():
            self.gen_stmt(st)

        self.out.emit(f"rt.SET_NAME({self.cpp_str(var)}, rt.BINOP(rt.GET_NAME({self.cpp_str(var)}), \"+\", TRT::V({step})));")
        self.out.dedent()
        self.out.emit("}")

    def gen_break(self, ctx):
        self.out.emit("break;")

    def gen_return(self, ctx):
        # Top-level main(): wir delegieren an runtime (oder du kannst return 0/1 machen)
        if ctx.expr():
            self.out.emit(f"rt.RETURN({self.gen_expr(ctx.expr())});")
        else:
            self.out.emit("rt.RETURN(TRT::Null());")

    def gen_parameter(self, ctx):
        p = ctx.paramNames()
        names = [t.getText() for t in p.IDENT()]
        self.out.emit(f"rt.PARAMETER({self.cpp_str_vec(names)});")

    def gen_expr_stmt(self, ctx):
        # exprStmt : postfixExpr ;
        e = self.gen_postfix(ctx.postfixExpr())
        self.out.emit(f"(void){e};")

    # ---------- WITH ----------
    def gen_with(self, ctx):
        base = self.gen_with_target(ctx.withTarget())
        tmp = self.new_temp()
        self.out.emit(f"auto {tmp} = {base};")
        self.out.emit(f"rt.PUSH_WITH({tmp});")

        body = ctx.withBody()
        for ch in list(getattr(body, "children", []) or []):
            t = type(ch).__name__
            if t.endswith("WithAssignStmtContext"):
                self.gen_with_assign(ch)
            elif t.endswith("WithStmtContext"):
                self.gen_with(ch)
            elif t.endswith("StatementContext"):
                self.gen_stmt(ch)

        self.out.emit("rt.POP_WITH();")

    def gen_with_target(self, ctx):
        if ctx.THIS():
            return "rt.GET_THIS()"
        if ctx.dottedRef():
            base, path = self.gen_dotted_ref_parts(ctx.dottedRef())
            return f"rt.GET({base}, {path})"
        if ctx.IDENT():
            return f"rt.GET_NAME({self.cpp_str(ctx.IDENT().getText())})"
        if ctx.postfixExpr():
            return self.gen_postfix(ctx.postfixExpr())
        return "TRT::Null()"

    def gen_with_assign(self, ctx):
        path = [t.getText() for t in ctx.withLvalue().IDENT()]
        rhs = self.gen_expr(ctx.expr())
        self.out.emit(f"rt.WITH_SET({self.cpp_str_vec(path)}, {rhs});")

    # ---------- expr / postfix / primary ----------
    # Hier kannst du (fast) genau deine Python-Version übernehmen, nur dass
    # du C++-Strings und TRT::V(...) nutzt. Ich mach’s minimal:

    def gen_expr(self, ctx):
        # expr : logicalOr ;
        return self.gen_logical_or(ctx.logicalOr())

    def gen_logical_or(self, ctx):
        parts = [self.gen_logical_and(x) for x in ctx.logicalAnd()]
        out = parts[0]
        for rhs in parts[1:]:
            out = f"rt.BINOP({out}, \"OR\", {rhs})"
        return out

    def gen_logical_and(self, ctx):
        parts = [self.gen_logical_not(x) for x in ctx.logicalNot()]
        out = parts[0]
        for rhs in parts[1:]:
            out = f"rt.BINOP({out}, \"AND\", {rhs})"
        return out

    def gen_logical_not(self, ctx):
        if ctx.NOT():
            inner = self.gen_logical_not(ctx.logicalNot())
            return f"rt.UNOP(\"NOT\", {inner})"
        return self.gen_comparison(ctx.comparison())

    def gen_comparison(self, ctx):
        left = self.gen_additive(ctx.additiveExpr(0))
        if ctx.compareOp():
            op = ctx.compareOp().getText()
            right = self.gen_additive(ctx.additiveExpr(1))
            return f"rt.BINOP({left}, {self.cpp_str(op)}, {right})"
        return left

    def gen_additive(self, ctx):
        terms = [self.gen_multiplicative(x) for x in ctx.multiplicativeExpr()]
        out = terms[0]
        kids = list(ctx.getChildren())
        i = 1
        while i < len(kids):
            op = kids[i].getText()
            rhs = terms[(i + 1) // 2]
            out = f"rt.BINOP({out}, {self.cpp_str(op)}, {rhs})"
            i += 2
        return out

    def gen_multiplicative(self, ctx):
        factors = [self.gen_postfix(x) for x in ctx.postfixExpr()]
        out = factors[0]
        kids = list(ctx.getChildren())
        i = 1
        while i < len(kids):
            op = kids[i].getText()
            rhs = factors[(i + 1) // 2]
            out = f"rt.BINOP({out}, {self.cpp_str(op)}, {rhs})"
            i += 2
        return out

    def gen_postfix(self, ctx):
        cur = self.gen_primary(ctx.primary())
        kids = list(ctx.getChildren())
        k = 1
        while k < len(kids):
            t = kids[k].getText()
            if t == "(":
                args = []
                if kids[k+1].getText() != ")":
                    argctx = kids[k+1]
                    args = [self.gen_expr(e) for e in argctx.expr()]
                    k += 1
                cur = f"rt.CALL_ANY({cur}, {self.cpp_val_vec(args)})"
                k += 2
                continue
            if t in (".", "::"):
                name = kids[k+1].getText()
                cur = f"rt.GET_ATTR({cur}, {self.cpp_str(name)})"
                k += 2
                continue
            k += 1
        return cur

    def gen_primary(self, ctx):
        if ctx.THIS():
            return "rt.GET_THIS()"
        if ctx.STRING():
            return f"TRT::V({ctx.STRING().getText()})"
        if ctx.NUMBER():
            return f"TRT::V({ctx.NUMBER().getText()})"
        if ctx.FLOAT():
            return f"TRT::V({ctx.FLOAT().getText()})"
        if ctx.IDENT():
            return f"rt.GET_NAME({self.cpp_str(ctx.IDENT().getText())})"
        if ctx.newExpr():
            return self.gen_new(ctx.newExpr())
        if ctx.expr():
            return "(" + self.gen_expr(ctx.expr()) + ")"
        return "TRT::Null()"

    def gen_new(self, ctx):
        class_name = ctx.IDENT().getText()
        args = []
        if ctx.argList():
            args = [self.gen_expr(e) for e in ctx.argList().expr()]
        return f"rt.NEW({self.cpp_str(class_name)}, {self.cpp_val_vec(args)})"

    def gen_dotted_ref_parts(self, dctx):
        parts = [t.getText() for t in dctx.IDENT()]
        head = parts[0]
        if head.upper() == "THIS":
            base = "rt.GET_THIS()"
            path = self.cpp_str_vec(parts[1:])
        else:
            base = f"rt.GET_NAME({self.cpp_str(head)})"
            path = self.cpp_str_vec(parts[1:])
        return base, path

    def lvalue_chain_from_postfix(self, pe):
        chain = [pe.primary().getText()]
        i = 1
        while i < pe.getChildCount():
            ch = pe.getChild(i).getText()
            if ch == ".":
                chain.append(pe.getChild(i+1).getText())
                i += 2
                continue
            if ch == "(":
                raise RuntimeError(f"LVALUE darf keinen Call enthalten: {pe.getText()}")
            i += 1
        return chain
        
class DBaseToPascal:
    def __init__(self, parser, classes=None, unit_name="GenProg"):
        self.p = parser
        self.out = PasEmitter()
        self.classes = classes or {}
        self.unit_name = unit_name
        self._tmp_i = 0

    def new_temp(self):
        self._tmp_i += 1
        return f"t{self._tmp_i}"

    # ----------------- ENTRY -----------------
    def generate(self, tree, out_path: str):
        o = self.out

        # Minimal-Programm. Du kannst auch "unit" generieren, wenn du willst.
        o.emit(f"program {self.unit_name};")
        o.emit("")
        o.emit("{$mode objfpc}{$H+}")
        o.emit("")
        o.emit("uses")
        o.indent()
        o.emit("SysUtils, Variants, dBaseRT;")
        o.dedent()
        o.emit(";")
        o.emit("")
        o.emit("var")
        o.indent()
        o.emit("rt: TRT;")
        o.dedent()
        o.emit("")
        o.emit("begin")
        o.indent()
        o.emit("rt := TRT.Create;")
        o.emit("try")
        o.indent()

        self.gen_input(tree)

        o.dedent()
        o.emit("finally")
        o.indent()
        o.emit("rt.Free;")
        o.dedent()
        o.emit("end;")
        o.dedent()
        o.emit("end.")
        Path(out_path).write_text(o.text(), encoding="utf-8")

    # ----------------- ROOT -----------------
    def gen_input(self, ctx):
        # input : item* EOF
        for it in ctx.item():
            self.gen_item(it)

    def gen_item(self, it):
        # item : classDecl | methodDecl | statement
        if it.statement():
            return self.gen_stmt(it.statement())
        if it.classDecl():
            return self.gen_class(it.classDecl())   # optional später
        if it.methodDecl():
            return self.gen_method(it.methodDecl()) # optional später
        self.out.emit("{ TODO unhandled item }")

    # ----------------- STATEMENTS -----------------
    def gen_stmt(self, st):
        # Passe das an die Stmt-Alternativen an, die du schon in Python eingebaut hast.
        if st.writeStmt():         return self.gen_write(st.writeStmt())
        if st.assignStmt():        return self.gen_assign(st.assignStmt())
        if st.localDeclStmt():     return self.gen_local_decl(st.localDeclStmt())
        if st.localAssignStmt():   return self.gen_local_assign(st.localAssignStmt())
        if st.ifStmt():            return self.gen_if(st.ifStmt())
        if st.forStmt():           return self.gen_for(st.forStmt())
        if st.returnStmt():        return self.gen_return(st.returnStmt())
        if st.breakStmt():         return self.gen_break(st.breakStmt())
        if st.withStmt():          return self.gen_with(st.withStmt())
        if st.parameterStmt():     return self.gen_parameter(st.parameterStmt())
        # … Schritt für Schritt erweitern …
        self.out.emit("{ TODO unhandled statement: " + type(st.getChild(0)).__name__ + " }")

    def gen_write(self, ctx):
        # writeStmt : WRITE writeArg (PLUS writeArg)* ;
        parts = [self.gen_write_arg(a) for a in ctx.writeArg()]
        if not parts:
            self.out.emit("rt.WRITE('');")
            return

        # dBase-Plus soll runtime-semantisch bleiben -> BINOP kaskadieren
        expr = parts[0]
        for p in parts[1:]:
            expr = f"rt.BINOP({expr}, '+', {p})"

        self.out.emit(f"rt.WRITE({expr});")

    def gen_write_arg(self, actx):
        # writeArg : STRING | dottedRef | expr ;
        if actx.STRING():
            return actx.STRING().getText()
        if actx.dottedRef():
            base_expr, path = self.gen_dotted_ref_parts(actx.dottedRef())
            return f"rt.GET({base_expr}, {path})"
        if actx.expr():
            return self.gen_expr(actx.expr())
        return f"Null"

    def gen_local_decl(self, ctx):
        # LOCAL IDENT
        name = ctx.name.text if hasattr(ctx, "name") else ctx.IDENT().getText()
        self.out.emit(f"rt.SET_NAME('{name}', Null);")

    def gen_local_assign(self, ctx):
        name = ctx.name.text if hasattr(ctx, "name") else ctx.IDENT().getText()
        rhs = self.gen_expr(ctx.expr())
        self.out.emit(f"rt.SET_NAME('{name}', {rhs});")

    def gen_assign(self, ctx):
        rhs = self.gen_expr(ctx.expr())
        lv = ctx.lvalue()

        # lvalue : postfixExpr | dottedRef ;
        if lv.dottedRef():
            base_expr, path = self.gen_dotted_ref_parts(lv.dottedRef())
            self.out.emit(f"rt.SET_({base_expr}, {path}, {rhs});")
            return

        pe = lv.postfixExpr()
        if pe:
            chain = self.lvalue_chain_from_postfix(pe)  # ["Y"] oder ["THIS","X","Y"]

            if len(chain) == 1:
                self.out.emit(f"rt.SET_NAME('{chain[0]}', {rhs});")
                return

            head = chain[0]
            if head.upper() == "THIS":
                base_expr = "rt.GET_THIS()"
                path = chain[1:]
            else:
                base_expr = f"rt.GET_NAME('{head}')"
                path = chain[1:]

            self.out.emit(f"rt.SET_({base_expr}, {self.pas_str_array(path)}, {rhs});")
            return

        self.out.emit("{ TODO unsupported lvalue }")

    def gen_if(self, ctx):
        # ifStmt : IF expr block (ELSE block)? ENDIF ;
        cond = self.gen_expr(ctx.expr())
        self.out.emit(f"if rt.TRUE_({cond}) then")
        self.out.emit("begin")
        self.out.indent()

        then_block = ctx.block(0)
        for st in then_block.statement():
            self.gen_stmt(st)

        self.out.dedent()
        self.out.emit("end")

        if ctx.ELSE():
            self.out.emit("else")
            self.out.emit("begin")
            self.out.indent()

            else_block = ctx.block(1)
            for st in else_block.statement():
                self.gen_stmt(st)

            self.out.dedent()
            self.out.emit("end;")
        else:
            self.out.emit(";")

    def gen_for(self, ctx):
        # forStmt : FOR IDENT ASSIGN numberExpr TO numberExpr (STEP numberExpr)? block ENDFOR ;
        varname = self.norm_local(ctx.IDENT().getText())
        start = ctx.numberExpr(0).getText()
        end   = ctx.numberExpr(1).getText()
        step  = ctx.numberExpr(2).getText() if ctx.STEP() else "1"

        # STEP != 1 -> while-Schleife (FPC for kann keinen Step)
        if step == "1":
            self.out.emit(f"rt.SET_NAME('{varname}', {start});")
            self.out.emit(f"while rt.TRUE_(rt.BINOP(rt.GET_NAME('{varname}'), '<=', {end})) do")
            self.out.emit("begin")
            self.out.indent()
            # Body
            for st in ctx.block().statement():
                self.gen_stmt(st)
            # Increment
            self.out.emit(f"rt.SET_NAME('{varname}', rt.BINOP(rt.GET_NAME('{varname}'), '+', {step}));")
            self.out.dedent()
            self.out.emit("end;")
        else:
            # allgemein: i := start; while cond: body; i += step
            self.out.emit(f"rt.SET_NAME('{varname}', {start});")
            self.out.emit(f"while rt.TRUE_(rt.FOR_COND(rt.GET_NAME('{varname}'), {end}, {step})) do")
            self.out.emit("begin")
            self.out.indent()
            for st in ctx.block().statement():
                self.gen_stmt(st)
            self.out.emit(f"rt.SET_NAME('{varname}', rt.BINOP(rt.GET_NAME('{varname}'), '+', {step}));")
            self.out.dedent()
            self.out.emit("end;")

    def gen_break(self, ctx):
        # in Pascal: break;
        self.out.emit("break;")

    def gen_return(self, ctx):
        # Im Program-Level gibt es kein "return". In Methoden später: Exit(value).
        # Hier delegieren wir:
        if ctx.expr():
            self.out.emit(f"rt.RETURN_({self.gen_expr(ctx.expr())});")
        else:
            self.out.emit("rt.RETURN_(Null);")

    def gen_parameter(self, ctx):
        # parameterStmt : PARAMETER paramNames ;
        p = ctx.paramNames()
        names = [t.getText() for t in p.IDENT()]
        self.out.emit(f"rt.PARAMETER({self.pas_str_array(names)});")

    # ----------------- WITH -----------------
    def gen_with(self, ctx):
        # withStmt : WITH '(' withTarget ')' withBody ENDWITH ;
        base = self.gen_with_target(ctx.withTarget())
        tmp = self.new_temp()
        self.out.emit(f"var {tmp}: Variant; {tmp} := {base};")  # simpel, du kannst var-block auch global machen
        self.out.emit(f"rt.PUSH_WITH({tmp});")
        body = ctx.withBody()
        for ch in list(getattr(body, "children", []) or []):
            t = type(ch).__name__
            if t.endswith("WithAssignStmtContext"):
                self.gen_with_assign(ch)
            elif t.endswith("WithStmtContext"):
                self.gen_with(ch)
            elif t.endswith("StatementContext"):
                self.gen_stmt(ch)
        self.out.emit("rt.POP_WITH();")

    def gen_with_target(self, ctx):
        # withTarget : THIS | dottedRef | IDENT | postfixExpr ;
        if ctx.THIS():
            return "rt.GET_THIS()"
        if ctx.dottedRef():
            base_expr, path = self.gen_dotted_ref_parts(ctx.dottedRef())
            return f"rt.GET({base_expr}, {path})"
        if ctx.IDENT():
            name = ctx.IDENT().getText()
            return f"rt.GET_NAME('{name}')"
        if ctx.postfixExpr():
            return self.gen_postfix(ctx.postfixExpr())
        return "Null"

    def gen_with_assign(self, ctx):
        # withAssignStmt : withLvalue ASSIGN expr ;
        path = [t.getText() for t in ctx.withLvalue().IDENT()]
        rhs = self.gen_expr(ctx.expr())
        self.out.emit(f"rt.WITH_SET({self.pas_str_array(path)}, {rhs});")

    # ----------------- EXPRESSIONS -----------------
    # Hier: nutze deine bereits angepassten gen_expr/gen_postfix/gen_primary-Methoden,
    # aber gib Pascal-Ausdrücke zurück, die auf rt.* basieren.

    def gen_expr(self, ctx):
        # expr : logicalOr ;
        return self.gen_logical_or(ctx.logicalOr())

    def gen_logical_or(self, ctx):
        parts = [self.gen_logical_and(x) for x in ctx.logicalAnd()]
        out = parts[0]
        for rhs in parts[1:]:
            out = f"rt.BINOP({out}, 'OR', {rhs})"
        return out

    def gen_logical_and(self, ctx):
        parts = [self.gen_logical_not(x) for x in ctx.logicalNot()]
        out = parts[0]
        for rhs in parts[1:]:
            out = f"rt.BINOP({out}, 'AND', {rhs})"
        return out

    def gen_logical_not(self, ctx):
        if ctx.NOT():
            inner = self.gen_logical_not(ctx.logicalNot())
            return f"rt.UNOP('NOT', {inner})"
        return self.gen_comparison(ctx.comparison())

    def gen_comparison(self, ctx):
        left = self.gen_additive(ctx.additiveExpr(0))
        if ctx.compareOp():
            op = ctx.compareOp().getText()
            right = self.gen_additive(ctx.additiveExpr(1))
            return f"rt.BINOP({left}, '{op}', {right})"
        return left

    def gen_additive(self, ctx):
        terms = [self.gen_multiplicative(x) for x in ctx.multiplicativeExpr()]
        out = terms[0]
        kids = list(ctx.getChildren())
        i = 1
        while i < len(kids):
            op = kids[i].getText()
            rhs = terms[(i + 1) // 2]
            out = f"rt.BINOP({out}, '{op}', {rhs})"
            i += 2
        return out

    def gen_multiplicative(self, ctx):
        factors = [self.gen_postfix(x) for x in ctx.postfixExpr()]
        out = factors[0]
        kids = list(ctx.getChildren())
        i = 1
        while i < len(kids):
            op = kids[i].getText()
            rhs = factors[(i + 1) // 2]
            out = f"rt.BINOP({out}, '{op}', {rhs})"
            i += 2
        return out

    def gen_postfix(self, ctx):
        # postfixExpr : primary ( '(' argList? ')' | ('.'|'::') IDENT )* ;
        cur = self.gen_primary(ctx.primary())
        kids = list(ctx.getChildren())
        k = 1
        while k < len(kids):
            t = kids[k].getText()
            if t == "(":
                args = []
                if kids[k+1].getText() != ")":
                    argctx = kids[k+1]
                    args = [self.gen_expr(e) for e in argctx.expr()]
                    k += 1
                cur = f"rt.CALL_ANY({cur}, {self.pas_expr_array(args)})"
                k += 2
                continue
            if t in (".", "::"):
                name = kids[k+1].getText()
                cur = f"rt.GET_ATTR({cur}, '{name}')"
                k += 2
                continue
            k += 1
        return cur
    
    def gen_new(self, ctx):
        # newExpr : NEW IDENT LPAREN argList? RPAREN ;
        class_name = ctx.IDENT().getText()
        args = []
        if ctx.argList():
            args = [self.gen_expr(e) for e in ctx.argList().expr()]
        
        # Pascal: array of Variant -> wir geben einen Pascal-Array-Ausdruck zurück
        return f"rt.NEW('{class_name}', {self.pas_expr_array(args)})"
    
    def gen_class(self, ctx):
        self.out.emit("{ TODO gen_class: " + ctx.name.text + " }")

    def gen_method(self, ctx):
        self.out.emit("{ TODO gen_method: " + ctx.IDENT().getText() + " }")
        
    def gen_primary(self, ctx):
        if ctx.THIS():    return "rt.GET_THIS()"
        if ctx.STRING():  return ctx.STRING().getText()
        if ctx.NUMBER():  return ctx.NUMBER().getText()
        if ctx.FLOAT():   return ctx.FLOAT().getText()
        if ctx.IDENT():
            name = ctx.IDENT().getText()
            return f"rt.GET_NAME('{name}')"
        if ctx.newExpr():
            return self.gen_new(ctx.newExpr())
        if ctx.expr():
            return f"({self.gen_expr(ctx.expr())})"
        return "Null"

    # ----------------- dottedRef / lvalue helpers -----------------
    def gen_dotted_ref_parts(self, dctx):
        parts = [t.getText() for t in dctx.IDENT()]
        head = parts[0]
        if head.upper() == "THIS":
            base = "rt.GET_THIS()"
            path = parts[1:]
        else:
            base = f"rt.GET_NAME('{head}')"
            path = parts[1:]
        return base, self.pas_str_array(path)

    def lvalue_chain_from_postfix(self, pe):
        chain = [pe.primary().getText()]
        i = 1
        while i < pe.getChildCount():
            ch = pe.getChild(i).getText()
            if ch == ".":
                chain.append(pe.getChild(i+1).getText())
                i += 2
                continue
            if ch == "(":
                raise RuntimeError(f"LVALUE darf keinen Call enthalten: {pe.getText()}")
            i += 1
        return chain

    # ----------------- small utils -----------------
    def pas_str_array(self, items):
        # ["A","B"] -> ['A','B']
        inner = ", ".join("'" + s.replace("'", "''") + "'" for s in items)
        return f"[{inner}]"

    def pas_expr_array(self, exprs):
        # ["rt.GET_NAME('X')", "5"] -> [rt.GET_NAME('X'), 5]
        inner = ", ".join(exprs)
        return f"[{inner}]"

    def norm_local(self, name: str) -> str:
        # optional (wenn du Namen in Pascal-Var-IDs brauchst)
        return "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in name).lower()
        
class DBaseToPython:
    """
    ParseTree -> Python source (calls into your runtime 'rt').
    - No direct attribute access; all member ops go through rt.GET/rt.SET/rt.CALL
    - Keeps dBase semantics in runtime, not in generated python.
    """

    def __init__(self, parser, classes=None):
        self.p = parser
        self.out = PyEmitter()
        self.classes = classes or {}  # optional: your collected ClassDefs, if you want structure

    # ---------- public ----------
    def generate(self, tree, out_path: str):
        self.out.emit("# generated by dBaseToPython (runtime-backed)")
        self.out.emit("from dBaseRuntimeFacade import RT")
        self.out.emit("")
        self.out.emit("rt = RT()")
        self.out.emit("")
        self.out.emit("def main():")
        self.out.indent()

        self.gen_input(tree)  # adapt name to your root rule

        self.out.dedent()
        self.out.emit("")
        self.out.emit("if __name__ == '__main__':")
        self.out.indent()
        self.out.emit("main()")
        self.out.dedent()

        Path(out_path).write_text(self.out.text(), encoding="utf-8")

    # ---------- root / statements ----------
    def gen_input(self, ctx):
        # input : item* EOF
        for it in ctx.item():
            self.gen_item(it)

    def gen_item(self, it):
        # Dispatch by available child rule; adapt to your grammar structure
        # item : classDecl | methodDecl | statement
        if it.statement():
            return self.gen_stmt(it.statement())
        if it.classDecl():
            return self.gen_class(it.classDecl())
        if it.methodDecl():
            return self.gen_method(it.methodDecl())

        # fallback:
        self.out.emit(f"# TODO unhandled stmt: {type(it).__name__}")

    def gen_stmt(self, st):
        if st.ifStmt():            return self.gen_if(st.ifStmt())
        if st.forStmt():           return self.gen_for(st.forStmt())
        if st.doWhileStatement():  return self.gen_do_while(st.doWhileStatement())

        if st.writeStmt():         return self.gen_write(st.writeStmt())
        if st.assignStmt():        return self.gen_assign(st.assignStmt())
        if st.localDeclStmt():     return self.gen_local_decl(st.localDeclStmt())
        if st.localAssignStmt():   return self.gen_local_assign(st.localAssignStmt())

        if st.callStmt():          return self.gen_call_stmt(st.callStmt())
        if st.exprStmt():          return self.gen_expr_stmt(st.exprStmt())

        if st.parameterStmt():     return self.gen_parameter(st.parameterStmt())
        if st.createFileStmt():    return self.gen_create_file(st.createFileStmt())
        if st.deleteStmt():        return self.gen_delete(st.deleteStmt())

        if st.withStmt():          return self.gen_with(st.withStmt())
        if st.doStmt():            return self.gen_do(st.doStmt())

        if st.returnStmt():        return self.gen_return(st.returnStmt())
        if st.breakStmt():         return self.gen_break(st.breakStmt())

        if st.classDecl():         return self.gen_class(st.classDecl())

        # bessere Debug-Ausgabe: zeig, was wirklich drinsteckt
        child0 = st.getChild(0)
        self.out.emit(f"# TODO unhandled statement: {type(child0).__name__}  text={st.getText()!r}")
    
    def gen_local_decl(self, ctx):
        # localDeclStmt : LOCAL name=IDENT ;
        name = ctx.name.text
        self.out.emit(f"rt.SET_NAME({name!r}, None)")

    def gen_local_assign(self, ctx):
        # localAssignStmt : LOCAL name=IDENT ASSIGN expr ;
        name = ctx.name.text
        rhs  = self.gen_expr(ctx.expr())
        self.out.emit(f"rt.SET_NAME({name!r}, {rhs})")

    def gen_expr_stmt(self, ctx):
        # exprStmt : postfixExpr ;
        e = self.gen_postfix(ctx.postfixExpr())
        self.out.emit(e)

    def gen_call_stmt(self, ctx):
        # callStmt : CALL callTarget ;
        # callTarget : (SUPER DCOLON)? IDENT LPAREN argList? RPAREN ;
        # simplest: delegiere als "exprStmt" (Call ist Effekt)
        txt = ctx.callTarget().getText()
        self.out.emit(f"rt.CALL_STMT({txt!r})  # TODO: map callTarget sauber")

    def gen_do_while(self, ctx):
        # doWhileStatement : DO WHILE condition block ENDDO ;
        cond = self.gen_logical_or(ctx.condition().logicalOr())
        self.out.emit(f"while rt.TRUE({cond}):")
        self.out.indent()
        for st in ctx.block().statement():
            self.gen_stmt(st)
        self.out.dedent()

    def gen_delete(self, ctx):
        # deleteStmt : DELETE IDENT ;
        self.out.emit(f"rt.DELETE_NAME({ctx.IDENT().getText()!r})")

    def gen_create_file(self, ctx):
        # createFileStmt : CREATE FILE (expr)? ;
        arg = self.gen_expr(ctx.expr()) if ctx.expr() else "None"
        self.out.emit(f"rt.CREATE_FILE({arg})")
        
    def gen_break(self, ctx):
        self.out.emit("break")
        
    def gen_parameter(self, ctx):
        p = ctx.paramNames()
        names = [t.getText() for t in p.IDENT()]
        self.out.emit(f"rt.PARAMETER({names!r})")
    
    def new_temp(self):
        n = getattr(self, "_tmp_i", 0) + 1
        self._tmp_i = n
        return f"_t{n}"

    def gen_with(self, ctx):
        # withStmt : WITH LPAREN withTarget RPAREN withBody ENDWITH ;

        base = self.gen_with_target(ctx.withTarget())
        tmp = self.new_temp()

        # base einmal auswerten (wichtig, falls es ein Call/Expr ist)
        self.out.emit(f"{tmp} = {base}")
        self.out.emit(f"rt.PUSH_WITH({tmp})")

        # body: (withAssignStmt | withStmt | statement)*
        body = ctx.withBody()
        for ch in list(getattr(body, "children", []) or []):
            # ANTLR liefert "TerminalNode" auch als children, die ignorieren wir
            if hasattr(ch, "withAssignStmt") and ch.withAssignStmt():
                self.gen_with_assign(ch.withAssignStmt())
            elif hasattr(ch, "withStmt") and ch.withStmt():
                self.gen_with(ch.withStmt())
            elif hasattr(ch, "statement") and ch.statement():
                self.gen_stmt(ch.statement())
            else:
                # manchmal ist ch direkt der Context-Typ
                t = type(ch).__name__
                if t.endswith("WithAssignStmtContext"):
                    self.gen_with_assign(ch)
                elif t.endswith("WithStmtContext"):
                    self.gen_with(ch)
                elif t.endswith("StatementContext"):
                    self.gen_stmt(ch)
                else:
                    pass

        self.out.emit("rt.POP_WITH()")


    def gen_with_target(self, ctx):
        # withTarget : THIS | dottedRef | IDENT | postfixExpr ;
        if ctx.THIS():
            return "this"

        if ctx.dottedRef():
            base_expr, path = self.gen_dotted_ref_parts(ctx.dottedRef())
            return f"rt.GET({base_expr}, {path})"

        if ctx.IDENT():
            # Variablenzugriff: runtime-semantisch (Scoping/WITH)
            name = ctx.IDENT().getText()
            return f"rt.GET_NAME({name!r})"

        if ctx.postfixExpr():
            # postfix kann call/member enthalten -> dein gen_postfix liefert runtime-Ausdruck
            return self.gen_postfix(ctx.postfixExpr())

        return f"rt.PRIMARY({ctx.getText()!r})"


    def gen_with_assign(self, ctx):
        # withAssignStmt : withLvalue ASSIGN expr ;
        path = [t.getText() for t in ctx.withLvalue().IDENT()]  # z.B. ["top"] oder ["pushbutton1","width"]
        rhs = self.gen_expr(ctx.expr())
        self.out.emit(f"rt.WITH_SET({path!r}, {rhs})")
    # ---------- WRITE ----------
    def gen_write_arg(self, actx):
        # writeArg : STRING | dottedRef | expr ;
        if actx.STRING():
            return actx.STRING().getText()
        if actx.dottedRef():
            base_expr, path = self.gen_dotted_ref_parts(actx.dottedRef())
            return f"rt.GET({base_expr}, {path})"
        if actx.expr():
            return self.gen_expr(actx.expr())
        return f"rt.PRIMARY({actx.getText()!r})"
        
    def gen_write(self, ctx):
        # writeStmt : WRITE writeArg (PLUS writeArg)* ;
        parts = [self.gen_write_arg(a) for a in ctx.writeArg()]

        if not parts:
            self.out.emit("rt.WRITE('')")   # sollte praktisch nie passieren
            return

        # WRITE a + b + c  -> runtime-konforme Verkettung
        expr = parts[0]
        for p in parts[1:]:
            expr = f"rt.BINOP({expr}, '+', {p})"

        self.out.emit(f"rt.WRITE({expr})")

    # ---------- assignment ----------
    def lvalue_chain_from_postfix(self, pe):
        # postfixExpr : primary ( '(' ... ')' | ('.'|'::') IDENT )*
        chain = [pe.primary().getText()]
        i = 1
        while i < pe.getChildCount():
            ch = pe.getChild(i).getText()

            if ch == '.':
                chain.append(pe.getChild(i + 1).getText())
                i += 2
                continue

            if ch == '(':
                raise Exception(f"LVALUE darf keinen Call enthalten: {pe.getText()}")

            i += 1
        return chain
        
    def gen_assign(self, ctx):
        rhs = self.gen_expr(ctx.expr())
        lv = ctx.lvalue()

        # 1) dottedRef direkt (THIS.X.Y ...)
        if lv.dottedRef():
            base_expr, path = self.gen_dotted_ref_parts(lv.dottedRef())
            self.out.emit(f"rt.SET({base_expr}, {path}, {rhs})")
            return

        # 2) postfixExpr als LHS: kann "Y" oder "THIS.X.Y" sein
        pe = lv.postfixExpr()
        if pe:
            chain = self.lvalue_chain_from_postfix(pe)   # z.B. ["Y"] oder ["THIS","PushButton1","Text"]

            if len(chain) == 1:
                # wichtig: über Runtime setzen, damit WITH/Scopes wie im Interpreter funktionieren
                self.out.emit(f"rt.SET_NAME({chain[0]!r}, {rhs})")
                return

            # Kette: base + path
            head = chain[0]
            if head.upper() == "THIS":
                base_expr = "this"
                path = chain[1:]
            else:
                base_expr = self.norm_local(head)
                path = chain[1:]

            self.out.emit(f"rt.SET({base_expr}, {path!r}, {rhs})")
            return

        self.out.emit(f"# TODO unsupported lvalue: {lv.getText()}")

    # ---------- IF ----------
    def gen_if(self, ctx):
        # ifStmt : IF expr block (ELSE block)? ENDIF ;
        cond = self.gen_expr(ctx.expr())
        self.out.emit(f"if rt.TRUE({cond}):")
        self.out.indent()

        # then-block
        then_block = ctx.block(0)
        for st in then_block.statement():
            self.gen_stmt(st)

        self.out.dedent()

        # else-block (optional)
        if ctx.ELSE():
            self.out.emit("else:")
            self.out.indent()

            else_block = ctx.block(1)
            for st in else_block.statement():
                self.gen_stmt(st)

            self.out.dedent()

    # ---------- FOR ----------
    def gen_for(self, ctx):
        # forStmt : FOR IDENT ASSIGN expr TO expr (STEP expr)? block ENDFOR ;
        
        var = self.norm_local(ctx.IDENT().getText())
        
        start = ctx.numberExpr(0).getText()
        end   = ctx.numberExpr(1).getText()
        step  = ctx.numberExpr(2).getText() if ctx.STEP() else "1"
        
        # dBase TO ist inklusiv -> Runtime-Helper
        self.out.emit(f"for {var} in rt.RANGE_INCL({start}, {end}, {step}):")
        self.out.indent()
        for st in ctx.block().statement():
            self.gen_stmt(st)
        self.out.dedent()

    # ---------- RETURN ----------
    def gen_return(self, ctx):
        if ctx.expr():
            self.out.emit(f"return {self.gen_expr(ctx.expr())}")
        else:
            self.out.emit("return")

    # ---------- CLASS / METHOD ----------
    def gen_class(self, ctx):
        cname = ctx.name.text  # adapt
        parent = ctx.parent.text if ctx.parent else "OBJECT"

        self.out.emit(f"class {self.norm_class(cname)}({self.norm_class(parent)}):")
        self.out.indent()
        self.out.emit("def __init__(self, *args):")
        self.out.indent()
        self.out.emit("super().__init__()")
        self.out.emit("self._instance = rt.MAKE_INSTANCE(self, args)")  # or however you represent instances
        self.out.dedent()
        self.out.emit("")

        # properties/methods in body: adapt to your classBody structure
        body = ctx.classBody()
        for ch in list(getattr(body, "children", []) or []):
            if hasattr(ch, "methodDecl") and ch.methodDecl():
                self.gen_method(ch.methodDecl())
            else:
                # propertyDecl / init statements -> put into __init__ or Init method
                pass

        self.out.dedent()
        self.out.emit("")

    def gen_method(self, mctx):
        mname = mctx.IDENT().getText()
        params = [p.getText() for p in mctx.paramList().IDENT()] if mctx.paramList() else []
        pyparams = ", ".join(["self"] + [self.norm_local(p) for p in params])

        self.out.emit(f"def {self.norm_method(mname)}({pyparams}):")
        self.out.indent()
        # inside methods, dBase THIS maps to `self` (or `this`)
        self.out.emit("this = self")
        # method statements:
        for st in mctx.block().statement():
            self.gen_stmt(st)
        self.out.dedent()
        self.out.emit("")


    def gen_new(self, ctx):
        class_name = ctx.IDENT().getText()
        args = [self.gen_expr(e) for e in ctx.argList().expr()] if ctx.argList() else []
        return f"rt.NEW({class_name!r}, {', '.join(args)})"

    def gen_call(self, ctx):
        # something like dottedRef '(' args ')'
        base_expr, path = self.gen_dotted_ref_parts(ctx.dottedRef())
        args = [self.gen_expr(e) for e in ctx.argList().expr()] if ctx.argList() else []
        return f"rt.CALL({base_expr}, {path}, [{', '.join(args)}])"

    def gen_dotted_ref_parts(self, dctx):
        # e.g. THIS.PushButton1.Text -> base=this, path=["PushButton1","Text"]
        parts = [t.getText() for t in dctx.IDENT()]

        head = parts[0]
        if head.upper() == "THIS":
            base = "this"
            path = parts[1:]
        else:
            base = self.norm_local(head)
            path = parts[1:]

        return base, repr(path)

    # ---------- naming ----------
    def norm_local(self, name: str) -> str:
        # conservative: keep letters/digits/_ and lower it
        return "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in name).lower()

    def norm_class(self, name: str) -> str:
        # keep it simple; you can make PascalCase if you like
        return "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in name)

    def norm_method(self, name: str) -> str:
        return self.norm_local(name)
        
        
    def gen_expr(self, ctx):
        # expr : logicalOr ;
        return self.gen_logical_or(ctx.logicalOr())

    def gen_logical_or(self, ctx):
        # logicalOr : logicalAnd (OR logicalAnd)* ;
        parts = [self.gen_logical_and(x) for x in ctx.logicalAnd()]
        out = parts[0]
        for rhs in parts[1:]:
            out = f"rt.BINOP({out}, 'OR', {rhs})"
        return out

    def gen_logical_and(self, ctx):
        # logicalAnd : logicalNot (AND logicalNot)* ;
        parts = [self.gen_logical_not(x) for x in ctx.logicalNot()]
        out = parts[0]
        for rhs in parts[1:]:
            out = f"rt.BINOP({out}, 'AND', {rhs})"
        return out

    def gen_logical_not(self, ctx):
        # logicalNot : NOT logicalNot | comparison ;
        if ctx.NOT():
            inner = self.gen_logical_not(ctx.logicalNot())
            return f"rt.UNOP('NOT', {inner})"
        return self.gen_comparison(ctx.comparison())

    def gen_comparison(self, ctx):
        # comparison : additiveExpr (compareOp additiveExpr)? ;
        left = self.gen_additive(ctx.additiveExpr(0))
        if ctx.compareOp():
            op = ctx.compareOp().getText()
            right = self.gen_additive(ctx.additiveExpr(1))
            return f"rt.BINOP({left}, {op!r}, {right})"
        return left

    def gen_additive(self, ctx):
        # additiveExpr : multiplicativeExpr ((PLUS|MINUS) multiplicativeExpr)* ;
        terms = [self.gen_multiplicative(x) for x in ctx.multiplicativeExpr()]
        out = terms[0]
        # Operatoren stehen als Token zwischen den Termen -> über getChildren laufen
        # Einfacher: Text-basiert paaren (robust genug für Start)
        # Wir bauen anhand der Kindersequenz: term (op term)*.
        children = list(ctx.getChildren())
        i = 1
        while i < len(children):
            op = children[i].getText()
            rhs = terms[(i + 1) // 2]
            out = f"rt.BINOP({out}, {op!r}, {rhs})"
            i += 2
        return out

    def gen_multiplicative(self, ctx):
        # multiplicativeExpr : postfixExpr ((STAR|SLASH) postfixExpr)* ;
        factors = [self.gen_postfix(x) for x in ctx.postfixExpr()]
        out = factors[0]
        children = list(ctx.getChildren())
        i = 1
        while i < len(children):
            op = children[i].getText()
            rhs = factors[(i + 1) // 2]
            out = f"rt.BINOP({out}, {op!r}, {rhs})"
            i += 2
        return out

    def gen_postfix(self, ctx):
        # postfixExpr : primary ( LPAREN argList? RPAREN | (DOT|DCOLON) IDENT )* ;
        cur = self.gen_primary(ctx.primary())

        # Wir laufen über die restlichen Kinder und erkennen Muster:
        # ( ... )  oder . IDENT / :: IDENT
        kids = list(ctx.getChildren())
        k = 1
        while k < len(kids):
            t = kids[k].getText()

            if t == "(":
                # call: ( argList? )
                # argList ist optional und sitzt zwischen '(' und ')'
                args = []
                # wenn nächstes Kind nicht ')', ist es argList
                if kids[k + 1].getText() != ")":
                    # kids[k+1] ist der argList-Context
                    argctx = kids[k + 1]
                    args = [self.gen_expr(e) for e in argctx.expr()]
                    k += 1  # argList "verbraucht"
                cur = f"rt.CALL_ANY({cur}, [{', '.join(args)}])"
                k += 2  # überspringe ')'
                continue

            if t in (".", "::"):
                name = kids[k + 1].getText()
                cur = f"rt.GET_ATTR({cur}, {name!r})"
                k += 2
                continue

            # fallback (sollte selten passieren)
            k += 1

        return cur

    def gen_primary(self, ctx):
        # primary:
        # handlerList | newExpr | memberExpr | literal | THIS | SUPER | FLOAT | NUMBER
        # | IDENT | STRING | BRACKET_STRING | '(' expr ')'
        if ctx.THIS():
            return "this"

        if ctx.SUPER():
            return "super_obj"  # falls du es nutzt; sonst an runtime delegieren

        if ctx.STRING():
            return ctx.STRING().getText()

        if ctx.BRACKET_STRING():
            return ctx.BRACKET_STRING().getText()

        if ctx.NUMBER():
            return ctx.NUMBER().getText()

        if ctx.FLOAT():
            return ctx.FLOAT().getText()

        if ctx.IDENT():
            return self.norm_local(ctx.IDENT().getText())

        if ctx.literal():
            return ctx.literal().getText()

        if ctx.newExpr():
            return self.gen_new(ctx.newExpr())

        # ( expr )
        if ctx.expr():
            return self.gen_expr(ctx.expr())

        # memberExpr/handlerList erstmal roh:
        return f"rt.PRIMARY({ctx.getText()!r})"
        
# ---------------------------------------------------------------------------
# Qt application stuff: Editor ...
# ---------------------------------------------------------------------------
class DBaseHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        # --- Formate ---
        self.fmt_keyword = QTextCharFormat()
        self.fmt_keyword.setFontWeight(QFont.Bold)
        self.fmt_keyword.setForeground(QColor(0, 0, 0))  # schwarz

        self.fmt_comment = QTextCharFormat()
        self.fmt_comment.setForeground(QColor(0, 128, 0))  # grün

        # --- Keywords (nach Bedarf erweitern) ---
        keywords = [
            "FOR", "ENDFOR", "CLASS", "ENDCLASS", "METHOD", "ENDMETHOD",
            "IF", "ENDIF", "ELSE", "DO", "WHILE", "ENDDO",
            "RETURN", "LOCAL", "PARAMETER", "WITH", "ENDWITH",
            "NEW", "OF", "OBJECT", "THIS", "SUPER", "TRUE", "FALSE"
        ]

        self.rules = []
        for kw in keywords:
            # \bKW\b = ganzes Wort, case-insensitive
            rx = QRegExp(rf"\b{kw}\b", Qt.CaseInsensitive)
            self.rules.append((rx, self.fmt_keyword))

        # --- Line comments: //, **, && bis Zeilenende ---
        self.rules.append((QRegExp(r"//[^\n]*"), self.fmt_comment))
        self.rules.append((QRegExp(r"\*\*[^\n]*"), self.fmt_comment))
        self.rules.append((QRegExp(r"&&[^\n]*"), self.fmt_comment))

        # --- Block comments: /* ... */ (mehrzeilig) ---
        self.block_start = QRegExp(r"/\*")
        self.block_end   = QRegExp(r"\*/")

    def highlightBlock(self, text: str):
        # 1) normale Regeln (Keywords + Single-line comments)
        for rx, fmt in self.rules:
            i = rx.indexIn(text, 0)
            while i >= 0:
                length = rx.matchedLength()
                self.setFormat(i, length, fmt)
                i = rx.indexIn(text, i + length)

        # 2) Block comments mehrzeilig
        self.setCurrentBlockState(0)

        start = 0
        if self.previousBlockState() != 1:
            start = self.block_start.indexIn(text, 0)
        else:
            start = 0

        while start >= 0:
            end = self.block_end.indexIn(text, start)
            if end == -1:
                # Kommentar geht in nächste Zeile weiter
                self.setCurrentBlockState(1)
                length = len(text) - start
            else:
                length = (end - start) + self.block_end.matchedLength()

            self.setFormat(start, length, self.fmt_comment)

            if end == -1:
                break
            start = self.block_start.indexIn(text, start + length)

class LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor"):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)

class CodeEditor(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self._update_line_number_area_width)
        self.updateRequest.connect(self._update_line_number_area)
        self.cursorPositionChanged.connect(self._highlight_current_line)

        self._update_line_number_area_width(0)
        self._highlight_current_line()

        # Optional: Monospace
        # self.setFont(QFont("Consolas", 10))

    def line_number_area_width(self) -> int:
        digits = len(str(max(1, self.blockCount())))
        fm = QFontMetrics(self.font())
        space = 12 + fm.horizontalAdvance("9") * digits
        return space

    def _update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def _update_line_number_area(self, rect, dy):
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self._update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event):
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor(245, 245, 245))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        fm = QFontMetrics(self.font())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor(120, 120, 120))
                painter.drawText(0, top, self._line_number_area.width() - 4, fm.height(),
                                 Qt.AlignRight, number)

            block = block.next()
            block_number += 1
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())

    def _highlight_current_line(self):
        # Light highlight current line
        extra = []
        if not self.isReadOnly():
            sel = QTextEdit.ExtraSelection()
            line_color = QColor(235, 245, 255)
            sel.format.setBackground(line_color)
            sel.format.setProperty(sel.format.FullWidthSelection, True)
            sel.cursor = self.textCursor()
            sel.cursor.clearSelection()
            extra.append(sel)
        self.setExtraSelections(extra)

    def line_number_area(self):
        return self._line_number_area

class FileEditorWindow(QDialog):
    def __init__(self, parent, initial_path: str = "", initial_text: str = ""):
        super().__init__(parent)
        self.parent = parent
        
        self.setModal(False)
        self.setWindowModality(Qt.NonModal)
        
        # Splitter: links Tree, rechts Editor
        self.splitter = QSplitter(Qt.Horizontal, self)
        
        # --- TreeView links ---
        self.tree = QTreeView(self.splitter)
        
        # Dummy Model (später kannst du hier Klassen/Methoden/etc. einfüllen)
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Struktur"])
        
        root = model.invisibleRootItem()
        
        root.appendRow(QStandardItem("CLASS ParentForm"))
        root.appendRow(QStandardItem("METHOD Init"))
        
        self.tree.setModel(model)
        self.tree.expandAll()
        
        vlayout = QVBoxLayout(self)

        self.ed = self._create_editor()
        self.ed.setFont(QFont("Consolas", 10))

        if initial_path:
            try:
                with open(initial_path, "r", encoding="utf-8") as f:
                    initial_text = f.read()
                    f.close()
            except Exception as e:
                raise Exception(e)
                
        self.highlighter = DBaseHighlighter(self.ed.document())
        
        # Splitter-Verhältnisse
        self.splitter.setStretchFactor(0, 0)  # Tree
        self.splitter.setStretchFactor(1, 1)  # Editor
        self.splitter.setSizes([220, 800])
        
        self._path = initial_path or ""
        self._set_text(initial_text or "")
        self._update_title()
        
        self._create_actions()
        
        self.mb = self._create_menus()
        self.tb = self._create_toolbar()
        self.sb = self._create_statusbar()
        
        vlayout.addWidget(self.mb)
        vlayout.addWidget(self.tb)
        vlayout.addWidget(self.splitter)
        vlayout.addWidget(self.sb)

        vlayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(vlayout)
        
        self.ed.cursorPositionChanged.connect(self._update_cursor_status)
        self.ed.document().modificationChanged.connect(lambda _: self._update_title())
        self._update_cursor_status()

    # ---------- UI building ----------
    def _create_editor(self):
        editor = CodeEditor(self.splitter)
        return editor
        
    def _create_actions(self):
        # File
        self.act_new = QAction("Neu", self)
        self.act_new.setShortcut("Ctrl+N")
        self.act_new.triggered.connect(self.file_new)

        self.act_save = QAction("Speichern", self)
        self.act_save.setShortcut("Ctrl+S")
        self.act_save.triggered.connect(self.file_save)

        self.act_save_as = QAction("Speichern unter…", self)
        self.act_save_as.setShortcut("Ctrl+Shift+S")
        self.act_save_as.triggered.connect(self.file_save_as)

        self.act_exit = QAction("Beenden", self)
        self.act_exit.setShortcut("Alt+F4")
        self.act_exit.triggered.connect(self.close)

        # Edit
        self.act_undo = QAction("Undo", self)
        self.act_undo.setShortcut("Ctrl+Z")
        self.act_undo.triggered.connect(self.ed.undo)

        self.act_redo = QAction("Redo", self)
        self.act_redo.setShortcut("Ctrl+Y")
        self.act_redo.triggered.connect(self.ed.redo)

        self.act_cut = QAction("Cut", self)
        self.act_cut.setShortcut("Ctrl+X")
        self.act_cut.triggered.connect(self.ed.cut)

        self.act_copy = QAction("Copy", self)
        self.act_copy.setShortcut("Ctrl+C")
        self.act_copy.triggered.connect(self.ed.copy)

        self.act_paste = QAction("Paste", self)
        self.act_paste.setShortcut("Ctrl+V")
        self.act_paste.triggered.connect(self.ed.paste)

        self.act_select_all = QAction("Select All", self)
        self.act_select_all.setShortcut("Ctrl+A")
        self.act_select_all.triggered.connect(self.ed.selectAll)

        # Help
        self.act_about = QAction("Über", self)
        self.act_about.triggered.connect(self.help_about)

    def _create_menus(self):
        mb = QMenuBar(self)

        m_file = mb.addMenu("Datei")
        m_file.addAction(self.act_new)
        m_file.addSeparator()
        m_file.addAction(self.act_save)
        m_file.addAction(self.act_save_as)
        m_file.addSeparator()
        m_file.addAction(self.act_exit)

        m_edit = mb.addMenu("Bearbeiten")
        m_edit.addAction(self.act_undo)
        m_edit.addAction(self.act_redo)
        m_edit.addSeparator()
        m_edit.addAction(self.act_cut)
        m_edit.addAction(self.act_copy)
        m_edit.addAction(self.act_paste)
        m_edit.addSeparator()
        m_edit.addAction(self.act_select_all)

        m_help = mb.addMenu("Hilfe")
        m_help.addAction(self.act_about)
        
        return mb

    def _create_toolbar(self):
        tb = QToolBar("Datei", self)
        tb.setMovable(False)
        tb.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        
        tb.addAction(self.act_new)
        tb.addAction(self.act_save)
        tb.addAction(self.act_save_as)
        
        return tb

    def _create_statusbar(self):
        sb = QStatusBar(self)
        sb.showMessage("Bereit")
        return sb

    # ---------- File operations ----------
    def maybe_save(self) -> bool:
        if not self.ed.document().isModified():
            return True
        res = QMessageBox.question(
            self,
            "Ungespeicherte Änderungen",
            "Du hast ungespeicherte Änderungen. Speichern?",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        )
        if res == QMessageBox.Yes:
            return self.file_save()
        if res == QMessageBox.No:
            return True
        return False

    def file_new(self):
        if not self.maybe_save():
            return
        self._path = ""
        self._set_text("")
        self.ed.document().setModified(False)
        self._update_title()

    def file_save(self) -> bool:
        if not self._path:
            return self.file_save_as()
        try:
            with open(self._path, "w", encoding="utf-8") as f:
                f.write(self.ed.toPlainText())
            self.ed.document().setModified(False)
            self.sb.showMessage(f"Gespeichert: {self._path}", 3000)
            self._update_title()
            return True
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Konnte nicht speichern:\n{e}")
            return False

    def file_save_as(self) -> bool:
        path, _ = QFileDialog.getSaveFileName(self, "Speichern unter", self._path or "", "Alle Dateien (*.*)")
        if not path:
            return False
        self._path = path
        return self.file_save()

    def closeEvent(self, event):
        if self.maybe_save():
            event.accept()
        else:
            event.ignore()

    # ---------- Helpers ----------
    def _set_text(self, text: str):
        self.ed.setPlainText(text)

    def _update_title(self):
        name = self._path if self._path else "Unbenannt"
        star = " *" if self.ed.document().isModified() else ""
        self.setWindowTitle(f"{name}{star} - Editor")

    def _update_cursor_status(self):
        tc = self.ed.textCursor()
        line = tc.blockNumber() + 1
        col = tc.positionInBlock() + 1
        self.sb.showMessage(f"Zeile {line}, Spalte {col}")

    def help_about(self):
        QMessageBox.information(self, "Über", "Einfacher QPlainTextEdit-Editor mit Zeilennummern.\n(Generiert im dBaseRunner)")
        
# ---------------------------------------------------------------------------
# ExecVisitor - Interpreter for dBase DSL ...
# ---------------------------------------------------------------------------
class ExecVisitor(dBaseParserVisitor):
    def __init__(self):
        super().__init__()
        self.output  = []  # sammelt Ausgaben (statt direkt printen)
        self._mode = ""
        
        self.vars: Dict[str, object] = {}   # normale Variablen
        self.this_obj: object | None = None # aktuelles "this"
        
        self.globals = {}
        self._scopes = [{}]        # stack of dicts
        
        self.env = ScopeStack()
        self.classes = {}          # className -> {"parent": str, "methods": {methodName: MethodDef}}
        
        self.classes["OBJECT"] = ClassDef(
            parent     = None,
            name       = "OBJECT",
            methods    = {"POPS": ""}
        )
        
        self.classes["PUSHBUTTON"] = ClassDef(
            parent     = "OBJECT",
            name       = "PUSHBUTTON",
            methods    = {"MOPS": ""},
            default_props = {       # <-- neu
                "path": "",
                "handle": None,
                "isopen": False,
                "mode": "",
                "eof": False,
                "pos": 0,
            }
        )
        
        self.frames: list[Frame] = [Frame(name="<global>")]  # globaler Frame
        self._current_class = None
        
        self.this_stack = []
        self.with_stack      : list[object] = []
        self.with_stack_owner: list[object] = []

    @property
    def current_frame(self) -> Frame:
        return self.frames[-1]
    
    @property
    def current_with_base(self):
        return self.with_stack[-1] if self.with_stack else None

    def push_frame(self, name: str, args: list[Any] | None = None) -> None:
        self.frames.append(Frame(name=name, args=list(args or [])))

    def pop_frame(self) -> Frame:
        if len(self.frames) <= 1:
            raise RuntimeError("Cannot pop global frame")
        return self.frames.pop()
    
    def push_this(self, inst: Instance):
        self.this_stack.append(inst)

    def pop_this(self):
        self.this_stack.pop()

    def cur_this(self) -> Instance:
        if not self.this_stack:
            raise RuntimeError("THIS ist nicht gesetzt")
        return self.this_stack[-1]

    def bind_child(self, owner: Instance, name: str, child: Instance):
        key = name.upper()
        
        # wenn Parent eine Font hat und Kind noch nicht: übernehmen
        if "FONT" in owner.props and "FONT" not in child.props:
            self.set_prop(child, "FONT", owner.props["FONT"], None)
            
        owner.children[key] = child
        owner.props[key] = child   # THIS.PushButton1 soll wie Property funktionieren

    def assign_name(self, name: str, value: Any):
        target = self.cur_with_target() or self.cur_this()
        set_prop_runtime(target, name, value)
    
    def cur_with_target(self) -> Optional[Instance]:
        return self.with_stack[-1] if self.with_stack else None
        
    def resolve_dotted(self, parts: list[str], ctx):
        if not parts:
            return None

        if parts[0].upper() == "THIS":
            obj = self.get_var("THIS", ctx)
        else:
            obj = self.get_var(parts[0], ctx)

        for member in parts[1:]:
            obj = self.get_member(obj, member, ctx)

        return obj
    
    def _need_value(self, v, ctx, what="Ausdruck"):
        if v is None:
            raise Exception(f"{ctx.start.line}:{ctx.start.column}: {what} ist None")
        return v

    def visitAdditiveExpr(self, ctx):
        # multiplicativeExpr ( (PLUS|MINUS) multiplicativeExpr )*
        res = self._need_value(self.visit(ctx.multiplicativeExpr(0)), ctx, "additiveExpr")
        n = len(ctx.multiplicativeExpr())
        for i in range(1, n):
            op = ctx.getChild(2*i - 1).getText()          # '+' oder '-'
            rhs = self._need_value(self.visit(ctx.multiplicativeExpr(i)), ctx, "additiveExpr rhs")
            if op == '+':
                res = res + rhs
            else:
                res = res - rhs
        return res

    def visitMultiplicativeExpr(self, ctx):
        # postfixExpr ( (STAR|SLASH) postfixExpr )*
        res = self._need_value(self.visit(ctx.postfixExpr(0)), ctx, "multiplicativeExpr")
        n = len(ctx.postfixExpr())
        for i in range(1, n):
            op = ctx.getChild(2*i - 1).getText()          # '*' oder '/'
            rhs = self._need_value(self.visit(ctx.postfixExpr(i)), ctx, "multiplicativeExpr rhs")
            if op == '*':
                res = res * rhs
            else:
                res = res / rhs
        return res

    def visitComparison(self, ctx):
        left = self._need_value(self.visit(ctx.additiveExpr(0)), ctx, "comparison left")
        if ctx.additiveExpr(1) is None:
            return left

        right = self._need_value(self.visit(ctx.additiveExpr(1)), ctx, "comparison right")
        op = ctx.compareOp().getText()

        if op == "<":  return left < right
        if op == "<=": return left <= right
        if op == ">":  return left > right
        if op == ">=": return left >= right
        if op == "==": return left == right
        if op == "!=": return left != right
        raise Exception(f"{ctx.start.line}:{ctx.start.column}: unbekannter Vergleichs-Operator {op}")

    def visitLogicalNot(self, ctx):
        # NOT logicalNot | comparison
        if ctx.NOT():
            return not bool(self._need_value(self.visit(ctx.logicalNot()), ctx, "logicalNot"))
        return self.visit(ctx.comparison())

    def visitLogicalAnd(self, ctx):
        result = self.visit(ctx.logicalNot(0))
        for i in range(1, len(ctx.logicalNot())):
            if not bool(result):      # short-circuit
                return result         # <-- NICHT False
            result = self.visit(ctx.logicalNot(i))
        return result

    def visitLogicalOr(self, ctx):
        result = self.visit(ctx.logicalAnd(0))
        for i in range(1, len(ctx.logicalAnd())):
            if bool(result):          # short-circuit
                return result         # <-- NICHT True
            result = self.visit(ctx.logicalAnd(i))
        return result

    def visitBreakStmt(self, ctx):
        raise BreakSignal()
    
    def visitExpr(self, ctx):
        # expr : logicalOr ;
        return self.visit(ctx.logicalOr())
    
    def visitWithBody(self, ctx):
        for ch in (ctx.children or []):
            if isinstance(ch, ParserRuleContext):
                self.visit(ch)
        return None
    
    def visitWithAssignStmt(self, ctx):
        value = self.visit(ctx.expr())
        parts = [t.getText() for t in ctx.withLvalue().IDENT()]

        target = self.with_stack[-1]
        owner  = self.with_stack_owner[-1]  # None oder Instance (z.B. Sender)

        # 1) Einfach: bold = .T.   oder   Text = "x"
        if len(parts) == 1:
            name = parts[0]

            if isinstance(target, Instance):
                self.set_prop(target, name.upper(), value, ctx)
                return None

            # z.B. WITH(Font) bold = .T.
            self.set_member(target, name, value, ctx)

            # wenn WITH(Font): neu anwenden
            if owner is not None and isinstance(target, FontValue):
                self.set_prop(owner, "FONT", target, ctx)

            return None

        # 2) Kette: Font.bold = .T.   innerhalb WITH(Sender)
        cur = target
        for seg in parts[:-1]:
            cur = self.get_member(cur, seg, ctx)

        self.set_member(cur, parts[-1], value, ctx)

        # wenn innerhalb WITH(Sender): Font.* geändert -> auf Sender neu setzen
        if isinstance(target, Instance) and parts and parts[0].upper() == "FONT":
            fv = target.props.get("FONT")
            if isinstance(fv, FontValue):
                self.set_prop(target, "FONT", fv, ctx)

        # wenn wir in WITH(Font) sind: owner neu setzen
        if owner is not None and isinstance(target, FontValue):
            self.set_prop(owner, "FONT", target, ctx)

        return None

    def set_property(self, obj, prop_name: str, value, ctx=None):
        key = prop_name.upper()

        # Wenn obj ein Qt-Widget ist:
        if hasattr(obj, "setFont") and key == "FONT":
            if isinstance(value, QFont):
                obj.setFont(value)
                return value
                
    def set_property_path(self, base_obj, path, value, ctx):
        obj = base
        for seg in path[:-1]:
            obj = self.get_member(obj, seg, ctx)

        last = path[-1]

        # Wir brauchen den "container" des letzten Members:
        container = base
        for seg in path[:-2]:
            container = self.get_member(container, seg, ctx)
            
        # obj ist jetzt das Zielobjekt (z.B. QFont), last ist "bold"
        self.set_member(obj, last, value, ctx)
        
        # -----------------------------------------
        # Wenn wir gerade Font.* geändert haben,
        # Font erneut ans Widget binden
        # -----------------------------------------
        if len(path) >= 2 and path[-2].upper() == "FONT":
            # -----------------------------------------------------
            # container ist dann das Objekt, das die Font-Property
            # besitzt falls das ein Qt-Widget ist:
            # -----------------------------------------------------
            qt_obj = getattr(container, "qt_obj", None)
            if qt_obj is not None and hasattr(qt_obj, "setFont"):
                qt_obj.setFont(obj)
            elif hasattr(container, "setFont"):
                container.setFont(obj)
                
        return value
        
    def push_scope(self):
        if not hasattr(self, "_scopes"):
            self._scopes = []
        self._scopes.append({})

    def pop_scope(self):
        self._scopes.pop()
    
    def visitStatement(self, ctx):
        if self._mode == "collect":
            # im Sammelpass Statements ignorieren
            return None
        return self.visitChildren(ctx)
    
    def ctx_text_token(ctx, token_name: str) -> str | None:
        fn = getattr(ctx, token_name, None)
        if callable(fn):
            t = fn()
            return t.getText() if t else None
        return None
        
    def eval_expr(self, ctx):
        text = ctx.getText()
        
        if getattr(ctx, "BRACKET_STRING", None) and ctx.BRACKET_STRING():
            tok = ctx.BRACKET_STRING().getSymbol()
            return self._unescape_bracket_string(tok.text)
            
        if self.is_simple_reference(text):
            return self.eval_reference_text(text)
        # Fallback: normale Expr-Auswertung über Visitor
        return self.visit(ctx)
    
    def is_simple_reference(self, s: str) -> bool:
        # erlaubt: X, this.width, a.b.c
        # (ohne Klammern/Operatoren)
        import re
        return re.fullmatch(r'(this|[A-Za-z_]\w*)(\.[A-Za-z_]\w*)*', s, re.IGNORECASE) is not None

    def eval_reference_text(self, s: str):
        parts = s.split('.')
        head = parts[0].upper()

        if head == "this":
            obj = self.this_object
            idx = 1
        else:
            obj = self._get_name(parts[0])
            idx = 1

        for name in parts[idx:]:
            obj = self.get_member(obj, name)
        return obj
        
    def visitBooleanLiteral(self, ctx):
        if ctx.TRUE():
            return True
        return False
        
    def eval_primary(self, ctx):
        if ctx.getText().upper() == "THIS":
            return self.this_object
        if ctx.NUMBER():
            return float(ctx.NUMBER().getText())
        if ctx.STRING():
            return self._unquote(ctx.STRING().getText())
        if ctx.identifier():
            name = ctx.identifier().getText()
            return self._get_name(name)   # <-- HIER
        if ctx.TRUE():
            return True
        if ctx.FALSE():
            return False
        if ctx.expr():
            return self.visit(ctx.expr())
            
        raise NotImplementedError(type(ctx).__name__)
    
    def has_method(self, obj, name: str) -> bool:
        # an dein Objektmodell anpassen:
        try:
            return name.upper() in obj.klass.methods
        except Exception:
            return False

    def resolve_method(self, start_class: str, method_name: str, ctx):
        c = start_class.upper()
        m = method_name.upper()

        while c is not None:
            cdef = self.classes.get(c)
            if cdef is None:
                raise Exception(f"{ctx.start.line}:{ctx.start.column}: Klasse '{c}' ist nicht definiert")

            # ClassDef statt dict
            if m in cdef.methods:
                return c, cdef.methods[m]

            c = cdef.parent.upper() if cdef.parent else None

        raise Exception(f"{ctx.start.line}:{ctx.start.column}: Methode '{m}' nicht gefunden (ab '{start_class}')")


    def resolve_method_silent(self, class_name: str, method_name: str):
        c = class_name
        m = method_name.upper()

        while c:
            cdef = self.classes.get(c)
            if not cdef:
                return None

            hit = cdef.methods.get(m)
            if hit:
                return hit

            c = cdef.parent.upper() if cdef.parent else None

        return None

    def in_local_scope(self) -> bool:
        return bool(self._scopes)

    def visitLocalDeclStmt(self, ctx):
        var_name = ctx.name.text  # IDENT token text
        # Deklaration ohne Wert -> None
        self.set_var(var_name, None)
        return None
        
    def visitLocalAssignStmt(self, ctx):
        var_name = ctx.name.text
        value = self.visit(ctx.expr())
        self.set_var(var_name, value)
        return value
    
    def _resolve_root(self, name: str, ctx):
        n = name.upper()
        if n == "THIS":
            # ist THIS irgendwo gesetzt?
            try:
                return self.get_var("THIS", ctx)
            except Exception:
                raise Exception(f"{ctx.start.line}:{ctx.start.column}: 'this' ist nur innerhalb einer Instanzmethode gültig")
        return self.get_var(n, ctx)

    def loc(self, ctx):
        if ctx is not None and hasattr(ctx, "start") and ctx.start is not None:
            return f"{ctx.start.line}:{ctx.start.column}"
        return "<unknown>"

    def _normalize_handlers(self, value, ctx, event_name: str):
        # erlaubt: einzelner Delegate oder Liste/Tuple davon
        if value is None:
            return []
        if isinstance(value, (list, tuple)):
            handlers = list(value)
        else:
            handlers = [value]

        out = []
        for h in handlers:
            if not isinstance(h, Delegate):
                raise RuntimeError(
                    f"{self.loc(ctx)}: {event_name} erwartet Methode(n) (Delegate), bekam {type(h).__name__}"
                )
            out.append(h)
        return out

    def _bind_event(self, inst, prop_key: str, value, ctx=None):
        key = prop_key.upper()

        # welche Events gibt's?
        # (pass_event = ob Qt-event als 2s-Arg an Handler geht)
        EVENT_MAP = {
            "ONCLICK"       : ("_ONCLICK_WRAPPER",     "_ONCLICK_HANDLERS",     False),
            "ONDBLCLICK"    : ("_ONDBLCLICK_WRAPPER",  "_ONDBLCLICK_HANDLERS",  False),
            
            "ONMOUSEDOWN"   : ("_ONMOUSEDOWN_WRAPPER", "_ONMOUSEDOWN_HANDLERS", True),
            "ONMOUSEUP"     : ("_ONMOUSEUP_WRAPPER",   "_ONMOUSEUP_HANDLERS",   True),
            "ONMOUSEMOVE"   : ("_ONMOUSEMOVE_WRAPPER", "_ONMOUSEMOVE_HANDLERS", True),
            
            "ONMOUSELBUTTON": ("_ONMOUSELBUTTON_WRAPPER", "_ONMOUSELBUTTON_HANDLERS", True),
            "ONMOUSERBUTTON": ("_ONMOUSERBUTTON_WRAPPER", "_ONMOUSERBUTTON_HANDLERS", True),

            "ONKEYDOWN"     : ("_ONKEYDOWN_WRAPPER", "_ONKEYDOWN_HANDLERS", True),
            "ONKEYUP"       : ("_ONKEYUP_WRAPPER",   "_ONKEYUP_HANDLERS",   True),
        }

        if key not in EVENT_MAP:
            return False

        wrapper_prop, handlers_prop, pass_event = EVENT_MAP[key]
        handlers = self._normalize_handlers(value, ctx, key)

        # "löschen" erlauben: onX = NIL -> entfernt Handler
        if not handlers:
            inst.props.pop(wrapper_prop, None)
            inst.props.pop(handlers_prop, None)

            # bei Click auch Signal trennen
            if key == "ONCLICK" and hasattr(inst.backend, "clicked"):
                old = inst.props.get("_ONCLICK_WRAPPER")
                if old is not None:
                    try:
                        inst.backend.clicked.disconnect(old)
                    except Exception:
                        pass
            return True

        wrapper = self._make_multi_wrapper(inst, handlers, pass_event)
        inst.props[wrapper_prop] = wrapper
        inst.props[handlers_prop] = handlers

        # Click: lieber Qt-Signal (wie du’s schon hast)
        if key == "ONCLICK" and hasattr(inst.backend, "clicked"):
            old = inst.props.get("_ONCLICK_WRAPPER")
            if old is not None:
                try:
                    inst.backend.clicked.disconnect(old)
                except Exception:
                    pass

            inst.props["_ONCLICK_VIA_SIGNAL"] = True
            inst.backend.clicked.connect(wrapper)
            return True

        # Rest: EventFilter sicherstellen
        self._ensure_event_filter(inst, ctx)
        return True

    def _make_multi_wrapper(self, inst, handlers, pass_event: bool):
        def wrapper(ev=None):
            for h in handlers:
                try:
                    # dBase-Semantik: Sender ist inst
                    args = [inst]
                    if pass_event:
                        args.append(ev)
                    self.invoke_method(h.target, h.method_name, args, None)
                except ReturnSignal:
                    # RETURN in Handler -> nur diesen Handler beenden, nächste weiter
                    continue
            return None
        return wrapper
    
    def get_member(self, obj, prop: str, ctx=None):
        key = prop.upper()
        
        # --- QFont support ---
        if isinstance(obj, FontValue):
            if key == "BOLD":
                return bool(obj.bold)
            if key == "ITALIC":
                return bool(obj.italic)
            if key == "UNDERLINE":
                return bool(obj.underline)
            if key == "NAME":
                return str(obj.family)
            if key == "SIZE":
                return int(obj.size)
            
        if isinstance(obj, Instance):
            # 1) Property?
            if key in obj.props:
                return obj.props[key]
            
            if key == "FONT" and getattr(obj, "backend", None) is not None and hasattr(obj.backend, "font"):
                qf = obj.backend.font()  # QFont vom Widget
                fv = FontValue(
                    family      = qf.family(),
                    size        = qf.pointSize(),
                    bold        = qf.bold(),
                    italic      = qf.italic(),
                    underline   = qf.underline(),
                    obj         = qf,     # wichtig: gleicher QFont
                )
                obj.props["FONT"] = fv
                return fv

            cls_name = getattr(obj, "class_name", None)

            # 2) DSL-Methode? -> als Delegate zurückgeben
            if cls_name:
                cls_def = self.classes.get(cls_name.upper())
                if cls_def and key in cls_def.methods:
                    return Delegate(target=obj, method_name=key, runner=self)

            # ✅ 3) Native Methode: OPEN (für FORM und alles was davon erbt)
            if key == "OPEN" and cls_name and self.is_descendant_of(cls_name.upper(), "FORM"):
                return Delegate(target=obj, method_name="OPEN", runner=self)

            raise RuntimeError(f"{self.loc(ctx)}: Member '{prop}' in {cls_name} nicht gefunden")

    def set_member(self, obj, prop: str, value, ctx):
        key = prop.upper()
        
        # --- QFont support ---
        if isinstance(obj, FontValue):
            if key == "BOLD":
                obj.bold = bool(value)
                obj.obj.setBold(obj.bold)
                return value
            if key == "ITALIC":
                obj.italic = bool(value)
                obj.obj.setItalic(obj.italic)
                return value
            if key == "UNDERLINE":
                obj.underline = bool(value)
                obj.obj.setUnderline(obj.underline)
                return value
            if key == "NAME":
                obj.family = str(value)
                obj.obj.setFamily(obj.family)
                return value
            if key == "SIZE":
                obj.size = int(value)
                obj.obj.setPointSize(obj.size)
                return value

        if not isinstance(obj, Instance):
            raise RuntimeError(f"{self.loc(ctx)}: '{prop}' setzen auf Nicht-Objekt")
        
        # Hauptspeicher: props
        self.set_prop(obj, key, value, ctx)
        return value

    def class_chain_base_to_derived(self, class_name: str) -> list[str]:
        chain = []
        c = class_name.upper()
        while c:
            if c not in self.classes:
                break
            chain.append(c)
            parent = self.classes[c].parent
            c = parent.upper() if parent else None
        return list(reversed(chain))  # base zuerst
        
    def eval_member(self, obj, name: str, ctx):
        key = name.upper()

        # Nur Beispiel: anpassen an deine Instance-Struktur!
        if isinstance(obj, Instance):
            # 1) Field/Property?
            # falls du z.B. obj.fields als dict hast:
            if hasattr(obj, "props") and key in obj.props:
                return obj.props[key]

            # 2) Methode?
            res = self.resolve_method_silent(obj.class_name.upper(), key)
            if res is not None:
                # Delegate ist bei dir offenbar genau das, was CallExpr ausführen kann
                return Delegate(target=obj, method_name=key, runner=self)

            raise RuntimeError(f"{ctx.start.line}:{ctx.start.column}: Member '{name}' nicht gefunden")

        raise RuntimeError(f"{ctx.start.line}:{ctx.start.column}: Memberzugriff auf Nicht-Objekt: {type(obj).__name__}")
    
    def call_delegate(self, d: Delegate, args: list, ctx):
        # d.target ist deine Instance, d.method_name z.B. "INIT"
        return self.invoke_method(d.target, d.method_name, args, ctx)
        
    def visitCallExpr(self, ctx):
        callee = self.visit(ctx.expr())  # oder ctx.callee o.ä.
        args = []
        if ctx.argList() is not None:
            args = [self.visit(a) for a in ctx.argList().expr()]

        # ✅ Delegate direkt ausführen
        if isinstance(callee, Delegate):
            return self.call_delegate(callee, args, ctx)

        # normale Python-callables
        if not callable(callee):
            raise RuntimeError(f"{ctx.start.line}:{ctx.start.column}: Ausdruck ist nicht aufrufbar: {ctx.getText()}")

        return callee(*args)
    
    def try_get_var(self, name, ctx):
        try:
            return self.get_var(name, ctx)
        except Exception:
            return None
        
    def get_chain(self, parts: list[str], ctx):
        parts = [p.upper() for p in parts]
        
        # --- SUPER::Method(...) ---
        if parts and parts[0] == "SUPER":
            if len(parts) < 2:
                raise RuntimeError(f"{ctx.start.line}:{ctx.start.column}: SUPER ohne Methodenname")
            
            this_obj = self.get_var("THIS", ctx)          # THIS muss gesetzt sein
            if not isinstance(this_obj, Instance):
                raise RuntimeError(f"{self.loc(ctx)}: SUPER nur innerhalb einer Instanzmethode gültig")
            
            cur_class = this_obj.class_name.upper()
            cdef = self.classes.get(cur_class)
            parent = cdef.parent.upper() if (cdef and cdef.parent) else None
            
            if not parent:
                raise RuntimeError(f"{self.loc(ctx)}: SUPER nicht möglich (keine Parent-Klasse)")
            
            mname = parts[1].upper()
            
            # Existiert die Methode irgendwo im Parent-Chain?
            if self.resolve_method_silent(parent, mname) is None:
                raise RuntimeError(f"{self.loc(ctx)}: SUPER-Methode '{mname}' nicht gefunden ab '{parent}'")
            
            # Delegate zurückgeben -> visitPostfixExpr ruft das dann auf
            return Delegate(target=this_obj, method_name=mname, runner=self)
            
        if parts[0].upper() == "THIS":
            cur = self.get_var("THIS", ctx)
        else:
            cur = self.get_var(parts[0], ctx)
        
        if cur is None:
            raise RuntimeError(f"{ctx.start.line}:{ctx.start.column}: '{parts[0]}' ist None")
        
        for name in parts[1:]:
            key = name.upper()

            if isinstance(cur, Instance):
                if hasattr(cur, "props") and key in cur.props:
                    cur = cur.props[key]
                    continue

                if self.resolve_method_silent(cur.class_name.upper(), key) is not None:
                    cur = Delegate(target=cur, method_name=key, runner=self)
                    continue
                    
                # 1) Property/Child?
                val = cur.props.get(name.upper())
                if val is not None:
                    cur = val
                    continue

                # 2) Methode?
                mctx = self.resolve_method_silent(cur.class_name.upper(), name.upper())
                if mctx is not None:
                    return Delegate(target=cur, method_name=name.upper(), runner=self)

                # 3) Fallback: zentrale Member-Logik benutzen (inkl. native OPEN)
                try:
                    cur = self.get_member(cur, name, ctx)   # <-- name ist "Open" im Original
                    continue
                except RuntimeError:
                    pass
                    
                # 4) sonst Fehler
                raise RuntimeError(f"{ctx.start.line}:{ctx.start.column}: Member '{name}' nicht gefunden")

            raise RuntimeError(f"{ctx.start.line}:{ctx.start.column}: '{parts[0]}' ist kein Objekt (ist {type(cur).__name__})")

        return cur

    def set_chain(self, dotted_ctx, value):
        parts = [t.getText() for t in dotted_ctx.IDENT()]  # z.B. ["THIS", "PushButton1"]
        if not parts:
            raise RuntimeError(f"{dotted_ctx.start.line}:{dotted_ctx.start.column}: leere dottedRef")

        # Startobjekt bestimmen
        head = parts[0].upper()
        if head == "THIS":
            cur = self.this_obj
            if cur is None:
                cur = self.get_var(parts[0], dotted_ctx)
                #raise RuntimeError(f"{dotted_ctx.start.line}:{dotted_ctx.start.column}: THIS ist nicht gesetzt")
        else:
            # z.B. A.B = ...
            cur = self.get_var(parts[0], dotted_ctx)

        # bis zum vorletzten Member entlanglaufen
        for name in parts[1:-1]:
            cur = self.get_member(cur, name, dotted_ctx)  # muss Instance zurückgeben, wenn weiter gekettet wird
        
        # letztes Member setzen
        last = parts[-1].upper()
        if isinstance(cur, Instance):
            self.set_prop(cur, last, value, dotted_ctx)
            #cur.props[last] = value
            #cur.fields[last] = value
            return

        raise RuntimeError(f"{dotted_ctx.start.line}:{dotted_ctx.start.column}: Ziel ist kein Objekt für Member-Set")
        
    def new_instance(self, class_name: str, args: list[Any]):
        cn = class_name.upper()
        
        # 1) FONT ist builtin -> zuerst abfangen
        if cn == "FONT":
            family    = str(args[0]) if len(args) > 0 else "Arial"
            size      = int(args[1]) if len(args) > 1 else 10
            
            bold      = bool(args[2]) if len(args) > 2 else False
            italic    = bool(args[3]) if len(args) > 3 else False
            underline = bool(args[4]) if len(args) > 4 else False
            
            font_obj = QFont(family, size)
            font_obj.setBold(bold)
            font_obj.setItalic(italic)
            font_obj.setUnderline(underline)
            
            return FontValue(
                obj         = font_obj,
                family      = family,
                size        = size,
                bold        = bold,
                italic      = italic,
                underline   = underline)

        # 2) native Qt-Klassen (FORM, PUSHBUTTON, ...)
        if cn in NATIVE_BASES:
            parent_inst = args[0] if args else None
            parent_backend = parent_inst.backend if isinstance(parent_inst, Instance) else None

            inst = Instance(class_name=cn)
            inst.backend = create_backend_for_base(cn, parent_backend)
            return inst

        # 3) user-defined Klassen
        cdef = self.classes.get(cn)
        if cdef is None:
            known = ", ".join(sorted(self.classes.keys()))
            raise RuntimeError(
                f"{self.loc(None)}: Klasse '{cn}' ist nicht definiert. "
                f"Bekannte Klassen: {known}"
            )
        
        classdef = cdef
        inst = Instance(class_name=classdef.name)
        
        # base backend (FORM etc.)
        if classdef.parent:
            inst.backend = create_backend_for_base(classdef.parent, None)
        
        # defaults apply
        #for k,v in getattr(classdef, "default_props", {}).items():
        #    set_prop_runtime(inst, k, v)
        for k, v in classdef.default_props.items():
            self.set_prop(inst, k, v)
        
        # execute class body with THIS = inst
        self.push_this(inst)
        self.push_scope()
        try:
            self._scopes[-1]["THIS"] = inst
            self._scopes[-1]["SELF"] = inst
            self.exec_class_body(classdef)
        finally:
            self.pop_scope()
            self.pop_this()
        
        if "INIT" in classdef.methods:
            self.invoke_method(inst, "INIT", args, None)
        
        return inst

    def set_prop(self, inst: Instance, name: str, value: Any, ctx=None):
        key = name.upper()
        
        # 1) normal speichern
        inst.props[key] = value
        
        # 2) MouseMove/Focus (Events => EventFilter)
        # MouseMove nur zuverlässig mit MouseTracking
        if hasattr(inst.backend, "setMouseTracking"):
            inst.backend.setMouseTracking(True)
            
        # 2) Event hooks
        if key == "ONGOTFOCUS":
            self._bind_ongotfocus(inst, value, ctx)
            return
        if key == "ONLOSTFOCUS":
            self._bind_onlostfocus(inst, value, ctx)
            return
        
        # Event-Properties?
        if self._bind_event(inst, key, value, ctx):
            return
            
        # 3) normale Qt properties
        apply_property_to_qt(inst, key, value)
    
    def _ensure_event_filter(self, inst: Instance, ctx=None):
        if inst.backend is None:
            return

        # Focus möglich machen
        try:
            inst.backend.setFocusPolicy(Qt.StrongFocus)
        except Exception:
            pass

        # MouseMove auch ohne gedrückte Taste
        try:
            inst.backend.setMouseTracking(True)
        except Exception:
            pass

        if not inst.props.get("_QT_EVENT_FILTER"):
            f = _QtEventFilter(self, inst)
            inst.props["_QT_EVENT_FILTER"] = f
            inst.backend.installEventFilter(f)

    def _bind_onkeydown(self, inst: Instance, handler: Any, ctx=None):
        if inst.backend is None:
            return
        if not isinstance(handler, Delegate):
            raise RuntimeError(f"{self.loc(ctx)}: onKeyDown erwartet eine Methode (Delegate), bekam {type(handler).__name__}")

        self._ensure_event_filter(inst, ctx)

        def wrapper(qt_event=None):
            try:
                return self.invoke_method(handler.target, handler.method_name, [inst], None)
            except ReturnSignal:
                return None

        inst.props["_ONKEYDOWN_WRAPPER"] = wrapper

    def _bind_onkeyup(self, inst: Instance, handler: Any, ctx=None):
        if inst.backend is None:
            return
        if not isinstance(handler, Delegate):
            raise RuntimeError(f"{self.loc(ctx)}: onKeyUp erwartet eine Methode (Delegate), bekam {type(handler).__name__}")

        self._ensure_event_filter(inst, ctx)

        def wrapper(qt_event=None):
            try:
                return self.invoke_method(handler.target, handler.method_name, [inst], None)
            except ReturnSignal:
                return None

        inst.props["_ONKEYUP_WRAPPER"] = wrapper

    def _bind_ondblclick(self, inst: Instance, handler: Any, ctx=None):
        if inst.backend is None:
            return
        if not isinstance(handler, Delegate):
            raise RuntimeError(f"{self.loc(ctx)}: onDblClick erwartet eine Methode (Delegate), bekam {type(handler).__name__}")

        self._ensure_event_filter(inst, ctx)

        def wrapper(qt_event=None):
            try:
                return self.invoke_method(handler.target, handler.method_name, [inst], None)
            except ReturnSignal:
                return None

        inst.props["_ONDBLCLICK_WRAPPER"] = wrapper
        
    def _bind_onclick(self, inst: Instance, handler: Any, ctx=None):
        if inst.backend is None:
            return
        
        # NEU: Liste/Tuple erlauben
        handlers = handler
        if isinstance(handler, (list, tuple)):
            handlers = list(handler)
        else:
            handlers = [handler]
        
        # Alle müssen Delegate sein
        for h in handlers:
            if not isinstance(h, Delegate):
                raise RuntimeError(
                    f"{self.loc(ctx)}: onClick erwartet Methode(n) (Delegate), bekam {type(h).__name__}"
                )
        
        def wrapper(*qt_args):
            try:
                # nacheinander ausführen
                for h in handlers:
                    try:
                        self.invoke_method(h.target, h.method_name, [inst], None)
                    except ReturnSignal:
                        # Return aus Handler ignorieren -> weiter zum nächsten
                        pass
            except ReturnSignal:
                return None
                
        # nur für Buttons (erstmal)
        if hasattr(inst.backend, "clicked"):
            old = inst.props.get("_ONCLICK_WRAPPER")
            try:
                if old is not None:
                    inst.backend.clicked.disconnect(old)
            except Exception:
                pass
            #raise RuntimeError(f"{self.loc(ctx)}: onClick nicht unterstützt für {inst.class_name}")
            #return
            
            inst.props["_ONCLICK_WRAPPER"   ] = wrapper
            inst.props["_ONCLICK_VIA_SIGNAL"] = True
            
            inst.backend.clicked.connect(wrapper)
            return
            
        inst.props["_ONCLICK_VIA_SIGNAL"] = False
        
        # Alles andere (z.B. FORM/QDialog): EventFilter via MouseRelease
        self._ensure_event_filter(inst, ctx)
        inst.props["_ONCLICK_WRAPPER"] = wrapper
        
    def _bind_onmousedown(self, inst: Instance, handler: Any, ctx=None):
        if inst.backend is None:
            return
        
        # nur für Buttons (erstmal)
        if not hasattr(inst.backend, "pressed"):
            raise RuntimeError(f"{self.loc(ctx)}: onMouseDown nicht unterstützt für {inst.class_name}")
        
        # Handler muss Delegate sein (oder notfalls BoundMethod)
        if not isinstance(handler, Delegate):
            raise RuntimeError(f"{self.loc(ctx)}: onMouseDown erwartet eine Methode (Delegate), bekam {type(handler).__name__}")
        
        # alten wrapper ggf. disconnecten
        old = inst.props.get("_ONMOUSEDOWN_WRAPPER")
        try:
            if old is not None:
                inst.backend.pressed.disconnect(old)
        except Exception:
            pass
        
        def wrapper(*qt_args):
            # Sender: inst (dBase-Instance)
            try:
                # Wenn dein Handler Sender erwartet:
                return self.invoke_method(handler.target, handler.method_name, [inst], None)
            except ReturnSignal:
                # click-handler ignoriert return meistens
                return None
        
        inst.props["_ONMOUSEDOWN_WRAPPER"] = wrapper
        inst.backend.pressed.connect(wrapper)
    
    def _bind_onmouseup(self, inst: Instance, handler: Any, ctx=None):
        if inst.backend is None:
            return
        
        # nur für Buttons (erstmal)
        if not hasattr(inst.backend, "released"):
            raise RuntimeError(f"{self.loc(ctx)}: onMouseUp nicht unterstützt für {inst.class_name}")
        
        # Handler muss Delegate sein (oder notfalls BoundMethod)
        if not isinstance(handler, Delegate):
            raise RuntimeError(f"{self.loc(ctx)}: onMouseUp erwartet eine Methode (Delegate), bekam {type(handler).__name__}")
        
        # alten wrapper ggf. disconnecten
        old = inst.props.get("_ONMOUSEUP_WRAPPER")
        try:
            if old is not None:
                inst.backend.released.disconnect(old)
        except Exception:
            pass
        
        def wrapper(*qt_args):
            # Sender: inst (dBase-Instance)
            try:
                # Wenn dein Handler Sender erwartet:
                return self.invoke_method(handler.target, handler.method_name, [inst], None)
            except ReturnSignal:
                # click-handler ignoriert return meistens
                return None
        
        inst.props["_ONMOUSEUP_WRAPPER"] = wrapper
        inst.backend.released.connect(wrapper)

    def _bind_onmousemove(self, inst: Instance, handler: Any, ctx=None):
        if inst.backend is None:
            return

        if not isinstance(handler, Delegate):
            raise RuntimeError(
                f"{self.loc(ctx)}: onMouseMove erwartet eine Methode (Delegate), bekam {type(handler).__name__}"
            )

        self._ensure_event_filter(inst, ctx)

        def wrapper(qt_event=None):
            try:
                # Minimal: nur Sender
                return self.invoke_method(handler.target, handler.method_name, [inst], None)
            except ReturnSignal:
                return None

        inst.props["_ONMOUSEMOVE_WRAPPER"] = wrapper

    def _bind_ongotfocus(self, inst: Instance, handler: Any, ctx=None):
        if inst.backend is None:
            return

        if not isinstance(handler, Delegate):
            raise RuntimeError(f"{self.loc(ctx)}: onGotFocus erwartet eine Methode (Delegate), bekam {type(handler).__name__}")

        self._ensure_event_filter(inst, ctx)

        def wrapper(qt_event=None):
            try:
                return self.invoke_method(handler.target, handler.method_name, [inst], None)
            except ReturnSignal:
                return None

        inst.props["_ONFOCUSIN_WRAPPER"] = wrapper

    def _bind_onlostfocus(self, inst: Instance, handler: Any, ctx=None):
        if inst.backend is None:
            return

        if not isinstance(handler, Delegate):
            raise RuntimeError(f"{self.loc(ctx)}: onLostFocus erwartet eine Methode (Delegate), bekam {type(handler).__name__}")

        self._ensure_event_filter(inst, ctx)

        def wrapper(qt_event=None):
            try:
                return self.invoke_method(handler.target, handler.method_name, [inst], None)
            except ReturnSignal:
                return None

        inst.props["_ONFOCUSOUT_WRAPPER"] = wrapper
    
    def exec_class_body(self, cdef: ClassDef):
        """
        Führt die Init-Statements aus, die beim Collect-Pass gesammelt wurden.
        Das sind z.B. WITH(...), THIS.PushButton1 = NEW ..., WRITE ..., usw.
        """
        # Primär: gesammelt in cdef.inits
        if getattr(cdef, "inits", None):
            for st in cdef.inits:
                self.visit(st)
            return

        # Fallback: alter Weg über body_ctx (falls du den später setzt)
        body = getattr(cdef, "body_ctx", None)
        if body is None:
            return

        for item in body.classBodyItem():
            if item.propertyDecl() is not None:
                continue
            if item.methodDecl() is not None:
                continue
            st = item.statement()
            if st is not None:
                self.visit(st)
            
    def collect_default_props(self, class_name: str) -> dict:
        cname = class_name.upper()

        # Klassenkette sammeln: derived -> base
        chain = []
        c = cname
        while c:
            cdef = self.classes.get(c)
            if not cdef:
                break
            chain.append(cdef)
            c = cdef.parent.upper() if cdef.parent else None

        # base -> derived mergen (Kind überschreibt)
        out = {}
        for cdef in reversed(chain):
            for k, v in (cdef.default_props or {}).items():
                out[k.upper()] = deepcopy(v)
        return out
        
    # Wert für PROPERTY ... = <expr> auswerten.
    # Läuft in einem frischen Scope und setzt THIS/SELF auf die neue Instanz.
    def _eval_property_default(self, expr_ctx, this_obj: Instance):
        local = {"THIS": this_obj, "SELF": this_obj}
        self._scopes.append(local)
        try:
            return self.visit(expr_ctx)
        finally:
            self._scopes.pop()
    
    def _norm(self, name: str) -> str:
        return name.upper()

    def _ensure_classdef(self, class_name: str) -> dict:
        k = self._norm(class_name.upper())
        if k not in self.classes:
            self.classes[k] = {
                "props": set(),
                "methods": {},
                "inits": [],
                # optional: "base": None,
            }
        else:
            # falls Klasse schon existiert, aber alt aufgebaut ist:
            self.classes[k].setdefault("props", set())
            self.classes[k].setdefault("methods", {})
            self.classes[k].setdefault("inits", [])
        return self.classes[k]
        
    def _vkey(self, name: str) -> str:
        return name.upper()

    def has_var(self, name: str) -> bool:
        key = self._vkey(name)
        return any(key in s for s in reversed(self._scopes))

    def get_var(self, name: str, ctx=None):
        key = self._vkey(name)
        for s in reversed(self._scopes):
            if key in s:
                return s[key]
        if ctx:
            raise RuntimeError(f"{ctx.start.line}:{ctx.start.column}: Variable '{key}' ist nicht definiert")
        raise RuntimeError(f"Variable '{key}' ist nicht definiert")

    def set_var(self, name: str, value):
        key = self._vkey(name)

        # wenn vorhanden: im nächstliegenden Scope updaten
        for s in reversed(self._scopes):
            if key in s:
                s[key] = value
                return

        # sonst: neu im aktuellen Scope anlegen
        self._scopes[-1][key] = value
    
    # ---------- Statements ----------
    def visitInput(self, ctx):
        # Pass 1: Klassen registrieren
        if self._mode == "collect":
            for it in ctx.item():
                if it.classDecl():
                    self.visit(it.classDecl())
            return None

        # Pass 2: Statements ausführen
        for it in ctx.item():
            if it.statement():
                self.visit(it.statement())

        return None
    
    def visitCallStmt(self, ctx):
        # callee irgendwie holen – z.B.:
        callee = self.visit(ctx.memberExpr())   # je nach Grammar: memberExpr/MemberExpr/etc.

        args = []
        if hasattr(ctx, "argList") and ctx.argList() is not None:
            args = [self.visit(e) for e in ctx.argList().expr()]

        # Delegate kann man "aufrufen", indem man die Methode im DSL ausführt
        if isinstance(callee, Delegate):
            return self.invoke_method(callee.target, callee.method_name, args, ctx)

        # normale Python-Funktionen
        if not callable(callee):
            raise RuntimeError(f"{ctx.start.line}:{ctx.start.column}: Ausdruck ist nicht aufrufbar: {ctx.getText()}")

        return callee(*args)
            
    def visitDoWhileStatement(self, ctx):
        #print("DEBUG: enter DO WHILE")
        guard = 0
        while True:
            cond = self.visit(ctx.condition())
            #print("DEBUG: condition =", cond)
            
            if not cond:
                #print("DEBUG: leave DO WHILE (cond false)")
                break
            
            try:
                self.visit(ctx.block())
            except BreakSignal:
                break   # beendet Schleife
                
            guard += 1
            if guard > 1_000_000:
                raise RuntimeError("DO WHILE: Endlosschleife?")
            
    def visitNewExpr(self, ctx):
        class_name = ctx.IDENT().getText().upper()

        args = []
        if ctx.argList() is not None:
            args = [self.visit(e) for e in ctx.argList().expr()]

        # WICHTIG: benutze die robuste Instanz-Erzeugung
        return self.new_instance(class_name.upper(), args)
    
    def visitDeleteStmt(self, ctx):
        name = ctx.IDENT().getText().upper()

        # zuerst in lokalen Scopes suchen (innerstes zuerst)
        for scope in reversed(self._scopes):
            if name in scope:
                obj = scope[name]
                self._maybe_destroy(obj, ctx)
                del scope[name]
                return None

        # dann globals
        if name in self.globals:
            obj = self.globals[name]
            self._maybe_destroy(obj, ctx)
            del self.globals[name]
            return None

        raise Exception(f"{ctx.start.line}:{ctx.start.column}: DELETE: Variable '{name}' existiert nicht")


    def _maybe_destroy(self, obj, ctx):
        if not isinstance(obj, Instance):
            return
        # falls du sowas willst:
        try:
            owner_class, mctx = self.resolve_method(obj.class_name.upper(), "DESTROY", ctx)
        except Exception:
            return
        self.execute_method(owner_class, mctx, [], this_obj=obj)
    
    def execute_method(self, owner_class_name: str, method_ctx, arg_values, this_obj):
        prev_this = self.this_obj
        self.this_obj = this_obj
        self.push_scope()
        try:
            self.set_var("THIS", this_obj)
            params = self._get_method_params(method_ctx)
            for i, pname in enumerate(params):
                self.set_var(pname.upper(), arg_values[i] if i < len(arg_values) else None)
            return self.visit(method_ctx.block())
        finally:
            self.pop_scope()
            self.this_obj = prev_this
    
    def visitVarRef(self, ctx):
        name = ctx.IDENT().getSymbol().text
        return self._get_name(name)
    
    def _get_class_members(self, ctx):
        # probiere typische Namen in Reihenfolge
        for name in ("classBody", "classMembers", "classItems", "classItem", "classStmt", "classStatement", "member"):
            if hasattr(ctx, name):
                node = getattr(ctx, name)()
                if node is None:
                    continue
                # wenn node selbst die Liste hat:
                for list_name in ("classMember", "member", "classItem", "statement", "stmt"):
                    if hasattr(node, list_name):
                        return getattr(node, list_name)()
                # manchmal ist node schon eine Liste
                if isinstance(node, list):
                    return node
        return []
    
    def visitPropertyDecl(self, ctx):
        # PROPERTY <ident> = <expr>
        # zur Laufzeit: in THIS.props schreiben
        this_obj = self.get_var("THIS", ctx)

        if not isinstance(this_obj, Instance):
            raise RuntimeError(f"{self.loc(ctx)}: PROPERTY nur innerhalb einer Instanz gültig")

        pname = ctx.IDENT().getText().upper()
        pval  = self.visit(ctx.expr()) if ctx.expr() else None

        this_obj.props[pname] = pval
        return None
    
    def _handle_property_decl(self, pctx, cdef: ClassDef):
        # pctx ist propertyDeclContext
        pname = pctx.IDENT().getText().upper()
        pval  = self.visit(pctx.expr())   # Expression auswerten
        cdef.default_props[pname] = pval
        
    def visitClassDecl(self, ctx):
        if getattr(self, "_mode", "") != "collect":
            return None
        
        class_name  = ctx.name.text.upper()
        parent_name = ctx.parent.text.upper() if ctx.parent else None
        
        cdef = ClassDef(name=class_name.upper(), parent=parent_name)
        body = ctx.classBody()
        
        # WICHTIG: alles in Original-Reihenfolge einsammeln
        for ch in list(getattr(body, "children", []) or []):
            tname = type(ch).__name__

            # PROPERTY
            if hasattr(ch, "propertyDecl") and ch.propertyDecl():
                self._handle_property_decl(ch.propertyDecl(), cdef)
                # optional: auch in inits aufnehmen, wenn du propertyDecl zur Laufzeit ausführen willst
                # cdef.inits.append(ch)

            # METHOD
            elif hasattr(ch, "methodDecl") and ch.methodDecl():
                mctx = ch.methodDecl()
                mname = mctx.IDENT().getText().upper()
                cdef.methods[mname] = mctx

            # direkte Init-Statements (Assign / WITH / normale Statements)
            elif hasattr(ch, "assignStmt") and ch.assignStmt():
                cdef.inits.append(ch.assignStmt())
            elif hasattr(ch, "withStmt") and ch.withStmt():
                cdef.inits.append(ch.withStmt())
            elif tname.endswith("StatementContext"):
                cdef.inits.append(ch)

        self.classes[class_name] = cdef
        return None

    # Basisklasse -> Kind-Reihenfolge, damit Kind überschreiben könnte (später).
    def collect_props(self, class_name: str) -> list[str]:
        out = []
        seen = set()

        c = class_name.upper()
        chain = []

        while c:
            if c not in self.classes:
                break
            chain.append(c)
            parent = self.classes[c].parent
            c = parent.upper() if parent else None

        for cname in reversed(chain):  # base zuerst
            for p in self.classes[cname].get("props", set()):
                if p not in seen:
                    seen.add(p)
                    out.append(p)

        return out
 
    def _method_name(self, ctx):
        # Label: name=IDENT
        if hasattr(ctx, "name") and ctx.name is not None:
            return ctx.name.text

        # Token getter: IDENT() oder ID()
        for tok in ("IDENT", "ID"):
            fn = getattr(ctx, tok, None)
            if callable(fn):
                t = fn()
                if t:
                    return t.getText()

        # Rule getter: identifier()
        fn = getattr(ctx, "identifier", None)
        if callable(fn):
            sub = fn()
            if sub:
                return sub.getText()

        # Fallback
        return ctx.getText()

    def visitMethodDecl(self, ctx):
        method_name = ctx.name.text.upper()

        params = []
        pl = ctx.paramList()
        if pl is not None:
            params = [t.getText().upper() for t in pl.IDENT()]

        # block besuchen / speichern / was auch immer du tust
        body = ctx.block()

        # Beispiel: speichern
        self.methods[method_name] = {
            "params": params,
            "ctx": body,
        }

        return None

    def visitMemberExpr(self, ctx):
        idents = [t.getText() for t in ctx.IDENT()]

        # THIS vorkommt
        if ctx.THIS() is not None:
            parts = ["THIS"] + idents
        else:
            parts = idents

        # Sonderfall: einzelner Name (z.B. "Font" oder "Sender")
        # -> MUSS über _get_name laufen, damit WITH-Context/Props funktionieren
        if len(parts) == 1 and parts[0].upper() != "THIS":
            return self._get_name(parts[0])

        # Sonderfall: nur "THIS"
        if parts == ["THIS"]:
            if self.this_stack:
                return self.cur_this()
            return self.get_var("THIS", ctx)

        # Optional: schneller Pfad THIS.Method => Delegate
        if len(parts) == 2 and parts[0].upper() == "THIS":
            this_obj = self.get_var("THIS", ctx)
            if isinstance(this_obj, Instance):
                key = parts[1].upper()
                if self.resolve_method_silent(this_obj.class_name.upper(), key) is not None:
                    return Delegate(target=this_obj, method_name=key, runner=self)

        return self.get_chain(parts, ctx)

    
    def visitPostfixExpr(self, ctx):
        # Basis auswerten
        cur = self.visit(ctx.primary())
        expr_list = []
        #print("===> ", cur)
        # Alle argLists einsammeln (für jeden '(' ... ')'-Call)
        arglists = ctx.argList() or []
        if not isinstance(arglists, list):
            arglists = [arglists]
        call_i = 0
        #print("--> ", ctx.argList())
        
        pending_member = None  # merkt sich den Namen nach '.'

        i = 1  # child(0) ist primary
        while i < ctx.getChildCount():
            t = ctx.getChild(i).getText()

            # Member-Start: ".Name"
            if t == '.':
                pending_member = ctx.getChild(i + 1).getText()
                i += 2
                continue

            # Call: "( ... )"
            if t == '(':
                # Argumente zur passenden argList
                if call_i < len(arglists):
                    al = arglists[call_i]

                    exprs = al.expr()
                    if exprs is None:
                        expr_list = []
                    elif isinstance(exprs, list):
                        expr_list = exprs
                    else:
                        # WICHTIG: einzelner ExprContext ist iterierbar -> sonst "Child-Liste"
                        expr_list = [exprs]
                        
                args = [self.visit(e) for e in expr_list]

                call_i += 1

                # Call ausführen
                if pending_member is None:
                    # direkter Call: Foo(...)
                    # dBase-Methoden-Objekte auch aufrufbar machen
                    if isinstance(cur, Delegate):
                        cur = self.invoke_method(cur.target, cur.method_name, args, ctx)
                    elif isinstance(cur, BoundMethod):
                        cur = self.invoke_method(cur.target, cur.name, args, ctx)
                    elif callable(cur):
                        cur = cur(*args)
                    else:
                        raise Exception(
                            f"{ctx.start.line}:{ctx.start.column}: Ausdruck ist nicht aufrufbar: {ctx.getText()}"
                        )
                else:
                    # Methoden-/Membercall: obj.Member(...)
                    name = pending_member
                    pending_member = None

                    if isinstance(cur, Instance):
                        # resolve_method NICHT separat aufrufen (Altlast / falscher Zugriff bei ClassDef)
                        cur = self.invoke_method(cur, name, args, ctx)
                    else:
                        fn = self.get_member(cur, name, ctx)
                        if callable(fn):
                            cur = fn(*args)
                        else:
                            raise Exception(
                                f"{ctx.start.line}:{ctx.start.column}: Member '{name}' ist nicht aufrufbar"
                            )

                i += 1
                continue

            # Falls noch ein Member "steht" und kein '(' folgt: obj.Member
            if pending_member is not None:
                cur = self.get_member(cur, pending_member, ctx)
                pending_member = None
                continue

            i += 1

        # falls am Ende noch ".X"
        if pending_member is not None:
            cur = self.get_member(cur, pending_member, ctx)

        return cur

    def visitLvalue(self, ctx):
        pe = ctx.postfixExpr()

        # Basis (primary) als Text
        base = pe.primary().getText()

        # Suffixe iterieren: children enthalten '.' IDENT oder '(' ... ')'
        parts = [base]
        i = 1  # child 0 ist primary
        while i < pe.getChildCount():
            ch = pe.getChild(i).getText()

            if ch == '.':
                ident = pe.getChild(i + 1).getText()
                parts.append(ident)
                i += 2
                continue

            if ch == '(':
                # Call in LHS ist nicht erlaubt
                raise Exception(f"{ctx.start.line}:{ctx.start.column}: LVALUE darf keinen Call enthalten: {pe.getText()}")

            i += 1

        # z.B. "THIS.width" -> ["THIS","width"]
        return parts
    
    def _lvalue_chain_from_postfix(self, pe, ctx):
        # pe ist postfixExpr-Context
        chain = [pe.primary().getText()]

        i = 1  # child 0 ist primary
        while i < pe.getChildCount():
            ch = pe.getChild(i).getText()

            if ch == '.':
                chain.append(pe.getChild(i + 1).getText())
                i += 2
                continue

            if ch == '(':
                raise Exception(
                    f"{ctx.start.line}:{ctx.start.column}: "
                    f"Assignment-Ziel darf keinen Call enthalten: {pe.getText()}"
                )

            i += 1

        return [s.upper() for s in chain]
    
    def set_chain_on_object(self, base_obj, chain: list[str], value, ctx):
        if base_obj is None:
            raise RuntimeError("WITH base object is None")

        if not chain:
            raise RuntimeError("empty chain in assignment")

        obj = base_obj
        # bis vor die letzte Property laufen
        for name in chain[:-1]:
            # hier brauchst du irgendeine Art get_member (oder du nutzt fields direkt)
            obj = self.get_member(obj, name, ctx)  # <- falls du das hast
            if obj is None:
                raise RuntimeError(f"WITH chain member '{name}' is None")

        return self.set_member(obj, chain[-1], value, ctx)
    
    def visitAssignment(self, ctx):
        value = self.visit(ctx.expr())
        self.set_chain(ctx.dottedRef(), value)
        return value
        
    def _set_chain_parts(self, parts, value, ctx):
        head = parts[0].upper()

        if head == "THIS":
            cur = self.get_var("THIS", ctx)
            if cur is None:
                raise RuntimeError(f"{ctx.start.line}:{ctx.start.column}: THIS ist nicht gesetzt")
        else:
            cur = self.get_var(parts[0], ctx)  # z.B. Sender, obj, etc.

        if cur is None:
            raise RuntimeError(f"{ctx.start.line}:{ctx.start.column}: '{parts[0]}' ist nicht definiert")

        # Merker: wenn wir gerade Font.* ändern, brauchen wir den "Besitzer" (z.B. Sender)
        font_container = None

        # bis zum vorletzten auflösen
        for name in parts[1:-1]:
            # Wenn das nächste Segment "Font" ist und cur ein Instance ist,
            # dann ist cur der Container (z.B. Sender), dessen Font wir später neu anwenden müssen.
            if name.upper() == "FONT" and isinstance(cur, Instance):
                font_container = cur

            cur = self.get_member(cur, name, ctx)

        last = parts[-1]  # NICHT uppern, set_member macht eh upper intern (oder du machst's dort)

        # 1) normales Instance-Property setzen (Sender.Text = ..., Sender.Font = NEW FONT(...))
        if isinstance(cur, Instance):
            self.set_prop(cur, last.upper(), value, ctx)  # aktualisiert props + Qt (setText etc.)
            return

        # 2) Unter-Property auf "value object" setzen (z.B. Sender.Font.bold = .T.)
        #    -> cur ist dann z.B. FontValue
        self.set_member(cur, last, value, ctx)

        # Wenn wir Font.* geändert haben: Font erneut auf den Container anwenden,
        # damit Qt das wirklich übernimmt.
        if font_container is not None:
            try:
                fv = self.get_member(font_container, "FONT", ctx)  # liefert FontValue
            except Exception:
                fv = font_container.props.get("FONT")

            if fv is not None:
                # set_prop sorgt bei dir dafür, dass Qt aktualisiert wird
                self.set_prop(font_container, "FONT", fv, ctx)

        return
        
    def assign_lvalue(self, lctx, value, ctx):
        # häufig: lvalue : IDENT ('.' IDENT)* ;
        if hasattr(lctx, "IDENT") and lctx.IDENT():
            toks = lctx.IDENT()
            parts = [t.getText() for t in (toks if isinstance(toks, list) else [toks])]

            # nur X = ...
            if len(parts) == 1:
                self._set_name(parts[0], value, ctx)   # WITH-aware: setzt Var oder Property
                return

            # THIS.PushButton1 = ...
            self._set_chain_parts(parts, value, ctx)
            return
        
        # fallback: Text parsen (quick&dirty, aber funktioniert)
        text = lctx.getText()  # z.B. THIS.PushButton1
        parts = text.split(".")
        if len(parts) == 1:
            self._set_name(parts[0], value, ctx)
        else:
            self._set_chain_parts(parts, value, ctx)
            
    def visitAssignStmt(self, ctx):
        value = self.visit(ctx.expr())
        pe = ctx.lvalue().postfixExpr()
        idents_u = self._lvalue_chain_from_postfix(pe, ctx)

        # ✅ WITH zuerst behandeln, bevor du returnst
        base = self.current_with_base
        if base is not None:
            # relative Zuweisung im WITH: "watch = 123" oder "a.b = 1"
            if len(idents_u) >= 1 and idents_u[0] != "THIS":
                return self.set_chain_on_object(base, idents_u, value, ctx)

        # danach normaler Assign
        if ctx.lvalue():
            self.assign_lvalue(ctx.lvalue(), value, ctx)
            return None
    
    def visitForStmt(self, ctx):
        var_name = ctx.IDENT().getText()
        start = float(ctx.numberExpr(0).getText())
        end = float(ctx.numberExpr(1).getText())

        # klassisch inklusiv (wie in vielen Basics/xBase)
        step = 1.0
        i = start
        
        # STEP optional
        if ctx.STEP() is not None:
            step = float(self.visit(ctx.numberExpr(2)))
            if step == 0:
                raise RuntimeError(f"{self.loc(ctx)}: STEP darf nicht 0 sein")
        else:
            # sinnvoller Default: Richtung automatisch
            step = 1.0 if end >= start else -1.0

        def cond(x):
            return x <= end if step > 0 else x >= end

        while cond(i):
            self.set_var(var_name.upper(), i)

            try:
                # block ausführen: statement*
                for st in ctx.block().statement():
                    self.visit(st)
            except BreakSignal:
                break

            i += step

        return None
        
    def visitWriteStmt(self, ctx):
        #print("DEBUG writeStmt text:", ctx.getText())
        #print("DEBUG writeArg count:", len(ctx.writeArg()))
        #for i, a in enumerate(ctx.writeArg()):
            #print(f"DEBUG arg[{i}] text:", a.getText(),
            #      "STRING?", a.STRING() is not None,
            #      "dottedRef?", a.dottedRef() is not None,
            #      "expr?", a.expr() is not None)

        parts = [self.eval_writeArg(a) for a in ctx.writeArg()]
        print("".join(parts))
        return None
    
    def eval_writeArg(self, arg_ctx):
        if arg_ctx.STRING():
            s = arg_ctx.STRING().getText()
            return s[1:-1]

        if arg_ctx.dottedRef():
            val = self.visit(arg_ctx.dottedRef())
            return "" if val is None else str(val)

        if arg_ctx.expr():
            val = self.visit(arg_ctx.expr())
            return "" if val is None else str(val)

        raise RuntimeError("writeArg enthält weder STRING noch dottedRef noch expr")

    def visitDottedRef(self, ctx):
        # dottedRef : (THIS | IDENT) (DOT IDENT)+ ;
        idents = [t.getText() for t in ctx.IDENT()]

        if ctx.THIS() is not None:
            head = "THIS"
        else:
            head = idents[0]  # erster IDENT ist der Kopf

        # ✅ Startobjekt über _get_name holen (kennt WITH + Variablen)
        if head.upper() == "THIS":
            cur = self.get_var("THIS", ctx)
            tail = idents
        else:
            cur = self._get_name(head)      # <-- wichtig!
            tail = idents[1:]               # Rest nach dem Kopf

        # Restliche Member auflösen
        for name in tail:
            cur = self.get_member(cur, name, ctx)

        return cur

        
    def _format_value(self, val):
        # optional hübscher: 3.0 -> "3"
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        return str(val)

    def visitIfStmt(self, ctx):
        cond_val = self.visit(ctx.expr())
        cond_true = (cond_val != 0)

        blocks = ctx.block()
        then_block = blocks[0]
        else_block = blocks[1] if len(blocks) > 1 else None

        if cond_true:
            self.visit(then_block)
        elif else_block is not None:
            self.visit(else_block)

        return None

    def visitBlock(self, ctx):
        for st in ctx.statement():
            self.visit(st)
        return None

    # ---------- Expression Evaluation ----------
    def visitAddExpr(self, ctx):
        value = self.visit(ctx.mulExpr(0))
        for i in range(1, len(ctx.mulExpr())):
            op = ctx.getChild(2*i-1).getText()
            rhs = self.visit(ctx.mulExpr(i))
            value = value + rhs if op == '+' else value - rhs
        return value

    def visitMulExpr(self, ctx):
        value = self.visit(ctx.unaryExpr(0))
        for i in range(1, len(ctx.unaryExpr())):
            op = ctx.getChild(2*i-1).getText()
            rhs = self.visit(ctx.unaryExpr(i))
            value = value * rhs if op == '*' else value / rhs
        return value

    def visitUnaryExpr(self, ctx):
        if ctx.getChildCount() == 2:
            op = ctx.getChild(0).getText()
            val = self.visit(ctx.unaryExpr(0))
            return +val if op == '+' else -val
        return self.visit(ctx.primary())

    def visitLiteral(self, ctx):
        if ctx.TRUE():
            return True
        if ctx.FALSE():
            return False
        if ctx.NUMBER():
            return float(ctx.NUMBER().getText())
        if ctx.STRING():
            s = ctx.STRING().getText()
            return s[1:-1] if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'") else s
        raise Exception(f"{ctx.start.line}:{ctx.start.column}: Unbekanntes literal")

    def visitPrimary(self, ctx):
        if hasattr(ctx, "handlerList") and ctx.handlerList():
            return self.visit(ctx.handlerList())
            
        if ctx.literal():
            return self.visit(ctx.literal())
            
        if ctx.newExpr():
            return self.visit(ctx.newExpr())

        if ctx.memberExpr():
            return self.visit(ctx.memberExpr())
        
        if ctx.THIS():
            return self.get_var("THIS", ctx)
        
        if ctx.SUPER():
            return "SUPER"
            
        if ctx.FLOAT():
            return float(ctx.FLOAT().getText())

        if ctx.NUMBER():
            return float(ctx.NUMBER().getText())

        if ctx.STRING():
            s = ctx.STRING().getText()
            return s[1:-1] if len(s) >= 2 and s[0] == s[-1] and s[0] in ('"', "'") else s

        if ctx.IDENT():
            name = ctx.IDENT().getSymbol().text  # Token-Text
            return self._get_name(name)       # <-- HIER ist der Lookup!
        
        if getattr(ctx, "BRACKET_STRING", None) and ctx.BRACKET_STRING():
            return self._unescape_bracket_string(ctx.BRACKET_STRING().getText())
            
        # ( expr )
        if ctx.expr():
            return self.visit(ctx.expr())
        
        raise Exception(f"{ctx.start.line}:{ctx.start.column}: Unbekanntes primary")
    
    def visitExprStmt(self, ctx):
        # expr ausführen, Ergebnis ignorieren
        self.visit(ctx.postfixExpr())
        return None

    def _get_name(self, name: str):
        key = name.upper()

        # 1) normale Variablen (aus _scopes!)
        try:
            return self.get_var(key, None)
        except Exception:
            pass

        # 2) WITH-Kontext: als Property des aktuellen WITH-Objekts behandeln
        if self.with_stack:
            base = self.with_stack[-1]
            if isinstance(base, Instance):
                if key in base.props:
                    return base.props[key]
                try:
                    return self.get_member(base, key, None)
                except Exception:
                    raise RuntimeError(f"Unbekanntes WITH-Property '{name}'")
            if isinstance(base, dict):
                # case-insensitive
                for k, v in base.items():
                    if k.upper() == key:
                        return v
                raise RuntimeError(f"Unbekanntes WITH-Property '{name}'")

        # 3) nicht gefunden
        raise RuntimeError(f"Unbekannter Name '{name}'")


    def _set_name(self, name: str, value, ctx=None):
        key = name.upper()

        # 1) wenn Variable irgendwo existiert -> updaten (in _scopes)
        for s in reversed(self._scopes):
            if key in s:
                s[key] = value
                return

        # 2) WITH aktiv? -> Property setzen
        if self.with_stack:
            base = self.with_stack[-1]
            if isinstance(base, Instance):
                base.props[key] = value
                self.set_prop(base, key, value, ctx)
                return
            if isinstance(base, dict):
                # vorhandenen key (case-insensitiv) treffen oder neu anlegen
                for k in list(base.keys()):
                    if k.upper() == key:
                        base[k] = value
                        return
                base[name] = value
                return

        # 3) sonst: neue Variable im aktuellen Scope anlegen
        self._scopes[-1][key] = value

    def visitWithStmt(self, ctx):
        # WITH ( withTarget ) withBody ENDWITH
        obj = self.visit(ctx.withTarget())
        
        if obj is None:
            raise RuntimeError(f"{ctx.start.line}:{ctx.start.column}: WITH target ist None")
        
        owner = None
        if isinstance(obj, FontValue) and self.with_stack and isinstance(self.with_stack[-1], Instance):
            owner = self.with_stack[-1]
        
        self.with_stack.append(obj)
        self.with_stack_owner.append(owner)
        try:
            self.visit(ctx.withBody())
        finally:
            self.with_stack_owner.pop()
            self.with_stack.pop()
        
        return None

    def set_child(self, owner: Instance, name: str, child: Instance):
        owner.children[name.upper()] = child
        owner.props[name.upper()] = child  # damit THIS.PushButton1 als Property funktioniert

    def visitWithTarget(self, ctx):
        # withTarget
        #   : THIS
        #   | dottedRef
        #   | IDENT
        #   | postfixExpr
        #   ;

        if ctx.THIS():
            if ctx.THIS():
                return self.get_var("THIS", ctx)   # oder self.cur_this() wenn du das nutzt

        if ctx.dottedRef():
            return self.visit(ctx.dottedRef())

        if ctx.IDENT():
            # Variable/Objektname (case-insensitiv handled by _get_name)
            return self._get_name(ctx.IDENT().getText())

        if ctx.postfixExpr():
            return self.visit(ctx.postfixExpr())

        return None

    def visitCompareExpr(self, ctx):
        left = self.visit(ctx.addExpr(0))

        # kein Vergleich, nur Zahl -> direkt zurück
        if ctx.getChildCount() == 1:
            return left

        op = ctx.getChild(1).getText()
        right = self.visit(ctx.addExpr(1))

        if op == "==": return 1 if left == right else 0
        if op == "!=": return 1 if left != right else 0
        if op == "<":  return 1 if left <  right else 0
        if op == "<=": return 1 if left <= right else 0
        if op == ">":  return 1 if left >  right else 0
        if op == ">=": return 1 if left >= right else 0

        raise ValueError(f"Unknown comparison operator: {op}")

    # ---------- Helpers ----------
    def _unescape_string(self, raw: str) -> str:
        quote = raw[0]
        s     = raw[1:-1]  # äußere Quotes weg
        out   = []
        i     = 0
        while i < len(s):
            if s[i] == '\\' and i + 1 < len(s):
                c = s[i+1]
                if c == 'n':
                    out.append('\n')
                elif c == 't':
                    out.append('\t')
                elif c == '\\':
                    out.append('\\')
                elif c == '"':
                    out.append('"')
                elif c == "'":
                    out.append("'")
                else:
                    out.append(c)
                i += 2
            else:
                out.append(s[i])
                i += 1
        return ''.join(out)
        
    def _unescape_bracket_string(self, tok_text: str) -> str:
        # tok_text enthält inklusive [ ... ]
        s = tok_text[1:-1]           # äußere Klammern weg
        s = s.replace("]]", "]")     # Escape wieder zurück
        return s
        
    def visitClassBody(self, ctx):
        # NUR member besuchen
        for m in ctx.classMember():
            self.visit(m)
        return None

    def _methoddef_from_methoddecl(self, decl_ctx):
        # 1) Parameterliste finden
        params = []

        # Häufig: decl_ctx.paramList() -> hat IDENT()
        if hasattr(decl_ctx, "paramList") and decl_ctx.paramList() is not None:
            pl = decl_ctx.paramList()
            if hasattr(pl, "IDENT"):
                params = [t.getText() for t in pl.IDENT()]

        # Alternativ: decl_ctx.IDENT() enthält [methodName, p1, p2, ...]
        if not params and hasattr(decl_ctx, "IDENT"):
            idents = [t.getText() for t in decl_ctx.IDENT()]
            if len(idents) >= 2:
                params = idents[1:]  # erstes ist meist der Methodenname

        # 2) Block/Body finden (je nach Grammar-Namen)
        block_ctx = None
        for cand in ("block", "stmtBlock", "compoundStmt", "methodBlock"):
            if hasattr(decl_ctx, cand):
                fn = getattr(decl_ctx, cand)
                try:
                    tmp = fn()
                except TypeError:
                    tmp = None
                if tmp is not None:
                    block_ctx = tmp
                    break

        # Wenn nix gefunden: nimm notfalls den decl_ctx selbst (und visit() muss damit klarkommen)
        if block_ctx is None:
            block_ctx = decl_ctx

        return MethodDef(params=params, block_ctx=block_ctx)

    def _get_method_params(self, method_ctx):
        # method_ctx ist MethodDeclContext
        pl = method_ctx.paramList()
        if not pl:
            return []

        # Häufige Fälle:
        # 1) paramList : IDENT (',' IDENT)* ;
        if hasattr(pl, "IDENT"):
            toks = pl.IDENT()
            if toks:
                if isinstance(toks, list):
                    return [t.getText() for t in toks]
                return [toks.getText()]

        # 2) paramList : identifier (',' identifier)* ;
        if hasattr(pl, "identifier"):
            ids = pl.identifier()
            if ids:
                if isinstance(ids, list):
                    return [x.getText() for x in ids]
                return [ids.getText()]

        # Fallback (zur Not): Text parsen
        txt = pl.getText()  # z.B. "a,c" oder "a,c,d"
        return [p.strip() for p in txt.split(",") if p.strip()]
        
    def invoke_method(self, target, method_name: str, args: list, ctx):
        mname = method_name.upper()

        # Native OPEN
        if mname == "OPEN" and self.is_descendant_of(target.class_name.upper(), "FORM"):
            return form_open(target)

        # resolve_method liefert (owner_class, method_ctx)
        owner_class, mctx = self.resolve_method(target.class_name, mname, ctx)

        self.push_this(target)
        self.push_scope()
        try:
            self._scopes[-1]["THIS"] = target
            self._scopes[-1]["SELF"] = target

            # ✅ Parameter binden (DAS fehlt!)
            params = self._get_method_params(mctx)
            for i, pname in enumerate(params):
                self.set_var(pname, args[i] if i < len(args) else None)

            try:
                self.visit(mctx.block())
                return None
            except ReturnSignal as rs:
                return rs.value

        finally:
            self.pop_scope()
            self.pop_this()
        
    # für Events ... -> FireClick(button)
    def invoke_delegate(self, d: Delegate, args: list, ctx):
        res = self.resolve_method(d.target.class_name.upper(), d.method_name, ctx)
        owner_class, method_ctx = res
        return self.execute_method(owner_class, method_ctx, args, this_obj=d.target)

    def visitCondition(self, ctx):
        return self.visit(ctx.logicalOr())

    def visitDoStmt(self, ctx):
        target = ctx.doTarget().getText()
        args = []
        if ctx.argList():
            for e in ctx.argList().expr():
                args.append(self.eval_expr(e))

        # 1) Program?
        if self.looks_like_program(target):   # z.B. enthält '.' oder endet auf .PRG
            self.run_program(target, args)
        else:
            self.call_procedure(target, args)

    def visitParameterStmt(self, ctx):
        names = [t.getText() for t in ctx.paramNames().IDENT()]
        incoming = self.current_frame.args if self.current_frame.args else []

        for i, name in enumerate(names):
            self.current_frame.vars[name.upper()] = incoming[i] if i < len(incoming) else None
    
    def visitReturnStmt(self, ctx):
        val = self.visit(ctx.expr()) if ctx.expr() else None
        raise ReturnSignal(val)

    def visitHandlerList(self, ctx):
        # ctx.expr() ist eine Liste: erstes expr + alle (SEMI expr)*
        items = []
        for e in ctx.expr():
            items.append(self.eval_expr(e))
        return items
        
    def is_descendant_of(self, class_name: str, base_name: str) -> bool:
        cn = class_name.upper()
        base = base_name.upper()
        while True:
            if cn == base:
                return True
            cdef = self.classes.get(cn)
            if not cdef or not cdef.parent:
                return False
            cn = cdef.parent.upper()

    def _bool_arg(self, args, idx, default=False):
        if idx >= len(args):
            return default
        v = args[idx]
        # robust: akzeptiere auch 0/1, "true"/"false"
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        if isinstance(v, str):
            return v.strip().upper() in ("TRUE", "T", ".T.", "1", "YES", "Y")
        return default

    def fire_event(self, inst, event_name: str, qt_event=None):
        # event_name z.B. "ONMOUSEDOWN"
        handler = inst.props.get(event_name)
        if handler is None:
            return False

        # 1) Delegate-Fall (dein System)
        #    z.B. Delegate(target=thisObj, method_name="PUSHBUTTON1_ONMOUSEDOWN", runner=self)
        if isinstance(handler, Delegate):
            # Signatur: METHOD ... (Sender)   oder (Sender, Event)
            try:
                return handler.call([inst])  # minimal: Sender
            except TypeError:
                return handler.call([inst, qt_event])  # optional: Qt-Event durchreichen

        # 2) Wenn du Handler als MethodDef / Callable speicherst:
        if callable(handler):
            return handler(inst, qt_event)

        return False

    def attach_events_to_widget(self, inst):
        w = inst.backend
        if w is None:
            return

        # MouseMove kommt nur, wenn MouseTracking an ist
        if hasattr(w, "setMouseTracking"):
            w.setMouseTracking(True)

        # Focus events kommen nur, wenn das Widget Fokus bekommen darf
        # PushButton kann das, aber sicher ist sicher:
        try:
            from PyQt5.QtCore import Qt
            w.setFocusPolicy(Qt.StrongFocus)
        except Exception:
            pass

        filt = WidgetEventFilter(self, inst)
        inst._qt_event_filter = filt      # <-- Referenz halten!
        w.installEventFilter(filt)

    def call_method(self, inst: Instance, name: str, args):
        name = name.upper()

        # native OPEN
        if name == "OPEN" and self.is_descendant_of(inst.class_name.upper(), "FORM"):
            return form_open(inst)

        cdef = self.classes.get(inst.class_name.upper())
        if not cdef or name not in cdef.methods:
            raise RuntimeError(f"Methode {name} nicht gefunden")

        mctx = cdef.methods[name]

        self.push_this(inst)
        self.push_scope()
        try:
            self._scopes[-1]["THIS"] = inst
            self._scopes[-1]["SELF"] = inst

            params = self._get_method_params(mctx)
            for i, pname in enumerate(params):
                self.set_var(pname, args[i] if i < len(args) else None)

            self.visit(mctx.block())
        finally:
            self.pop_scope()
            self.pop_this()

    def visitCreateFileStmt(self, ctx):
        # Beispiel: CREATE FILE oder CREATE FILE <expr>
        path = ""
        if hasattr(ctx, "expr") and ctx.expr():
            path = str(self.eval_expr(ctx.expr()))
        
        self.open_file_editor(path=path, text="")
        return None
        
    def open_file_editor(self, path: str = "", text: str = ""):
        text = ""
        # wenn path gesetzt ist und text leer: Datei laden
        if path and text == "":
            try:
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
            except FileNotFoundError:
                print("file not found.")
                pass
        try:
            win = FileEditorWindow(parent=MAINAPP, initial_path=path, initial_text=text)
            sub = MAINAPP.mdi.addSubWindow(win)
            win.resize(500, 450)
            
            # 1) immer sichtbar + Vordergrund
            win.show()
            win.raise_()
            win.activateWindow()

            # 2) falls minimiert: wieder herstellen
            win.setWindowState(win.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

            # 3) optional: "Always on top"
            win.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            win.show()  # nach setWindowFlag nochmal show()!
            win.raise_()
            win.activateWindow()
    
            # Referenz halten (gegen GC)
            self._open_windows = getattr(self, "_open_windows", [])
            self._open_windows.append(win)
        except Exception as e:
            print(e)

# ---------------------------------------------------------------------------
# parser stuff ...
# ---------------------------------------------------------------------------        
def parse(filename: str):
    # 0 pre-procession
    pp = Preprocessor(include_paths=[Path("includes")])
    pre = pp.process(filename)
    
    #source = FileStream(filename, encoding="utf-8")
    source = InputStream(pre)
    lexer  = dBaseLexer(source)
    tokens = CommonTokenStream(lexer)
    tokens.fill();
    parser = dBaseParser(tokens)

    tree   = parser.input_()
    sema   = analyze(tree, parser)
    
    # 1. lexer check
    while True:
        tok = lexer.nextToken()   # HIER wird dein Override aufgerufen
        if tok.type == Token.EOF:
            depth = getattr(lexer, "_cmtDepth", 0)
            if depth > 0:
                line = lexer.line
                col  = lexer.column
                raise UnterminatedBlockCommentError(line, col)
            break
    
    global VISITOR
    VISITOR = ExecVisitor()
    
    # PASS 1: Klassen sammeln
    VISITOR._mode = "collect"
    VISITOR.visit(tree)

    # PASS 2: Statements ausführen
    VISITOR._mode = "exec"
    VISITOR.visit(tree)
    
    for line in VISITOR.output:
        print(line)
    
    #print("Tree  :", tree.toStringTree(recog=parser))
    return tree

# ---------------------------------------------------------------------------
# Qt5 Application stuff ...
# ---------------------------------------------------------------------------
class showException(QDialog):
    def __init__(self, parent=None, etype: str="Ausnahme", message: str=""):
        super().__init__(parent)
        self.setWindowTitle("Demo: " + etype)
        self.resize(320, 200)
        self.message = message
        
        layout = QVBoxLayout(self)
        
        self.text = QTextEdit(self)
        self.text.setText(self.message)
        
        layout.addWidget(self.text)
        
        self.btn = QPushButton("Schließen", self)
        self.btn.clicked.connect(self.on_button_clicked)
        
        layout.addWidget(self.btn)
        
    def on_button_clicked(self):
        self.close()

class SourceAliasesTab(QWidget):
    """
    Tab 'Quell-Aliases' wie Screenshot, inkl. Add/Remove/Edit + nicht-nativer Folder-Dialog.
    model: dict[str, str]  (alias -> path)
    """
    def __init__(self, parent=None, initial=None):
        super().__init__(parent)

        self._model = dict(initial or {})
        self._updating_ui = False

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # ---- Oben: Liste ----
        gb_list = QGroupBox("Definierte Quell-Aliases", self)
        v_list = QVBoxLayout(gb_list)

        self.lst = QListWidget()
        self.lst.setMinimumHeight(210)
        v_list.addWidget(self.lst)

        # ---- Unten: Editor ----
        gb_edit = QGroupBox("Quell-Alias bearbeiten", self)
        e = QGridLayout(gb_edit)
        e.setHorizontalSpacing(10)
        e.setVerticalSpacing(8)

        e.addWidget(QLabel("Alias:"), 0, 0)
        self.ed_alias = QLineEdit()
        self.ed_alias.setMinimumWidth(220)
        e.addWidget(self.ed_alias, 0, 1)

        self.btn_add = QPushButton("Hinzufügen")
        self.btn_remove = QPushButton("Entfernen")
        self.btn_add.setFixedWidth(95)
        self.btn_remove.setFixedWidth(95)
        e.addWidget(self.btn_add, 0, 2)
        e.addWidget(self.btn_remove, 0, 3)

        e.addWidget(QLabel("Pfad:"), 1, 0)
        self.ed_path = QLineEdit()
        e.addWidget(self.ed_path, 1, 1, 1, 2)

        self.btn_browse = QPushButton("…")
        self.btn_browse.setFixedWidth(30)
        e.addWidget(self.btn_browse, 1, 3, alignment=Qt.AlignLeft)

        root.addWidget(gb_list)
        root.addWidget(gb_edit)
        root.addStretch(1)

        # Demo / initial
        if not self._model:
            self._model.update({
                "CoreShared": r"T:\Programme\dBASE\dBASE2019\Bin\dBLCore\Shared",
                "dBStartup": r"T:\Programme\dBASE\dBASE2019\Bin\dBStartup",
                "Examples": r"T:\Programme\dBASE\dBASE2019\Examples",
                "Forms": r"T:\Programme\dBASE\dBASE2019\Forms",
                "Images": r"T:\Programme\dBASE\dBASE2019\Images",
            })

        self._reload_list(select_first=True)

        # Signals
        self.lst.currentItemChanged.connect(self._on_list_changed)
        self.btn_add.clicked.connect(self._on_add)
        self.btn_remove.clicked.connect(self._on_remove)
        self.btn_browse.clicked.connect(self._on_browse)

        # optional: Live-Update ins Modell, wenn man Felder verlässt
        self.ed_alias.editingFinished.connect(self._on_edit_finished)
        self.ed_path.editingFinished.connect(self._on_edit_finished)

    # ---------- Public ----------
    def model(self) -> dict:
        """Gibt eine Kopie des Modells zurück."""
        return dict(self._model)

    # ---------- Intern ----------
    def _reload_list(self, select_first=False, select_alias=None):
        self._updating_ui = True
        try:
            self.lst.clear()
            for alias in sorted(self._model.keys(), key=lambda s: s.lower()):
                self.lst.addItem(QListWidgetItem(alias))

            if select_alias:
                items = self.lst.findItems(select_alias, Qt.MatchFixedString)
                if items:
                    self.lst.setCurrentItem(items[0])
            elif select_first and self.lst.count() > 0:
                self.lst.setCurrentRow(0)
        finally:
            self._updating_ui = False

        # falls leer
        self._sync_editor_enabled()

    def _sync_editor_enabled(self):
        has = self.lst.currentItem() is not None
        self.btn_remove.setEnabled(has)

    def _on_list_changed(self, cur, prev):
        if self._updating_ui:
            return
        self._sync_editor_enabled()

        if not cur:
            self.ed_alias.setText("")
            self.ed_path.setText("")
            return

        alias = cur.text()
        path = self._model.get(alias, "")

        self._updating_ui = True
        try:
            self.ed_alias.setText(alias)
            self.ed_path.setText(path)
        finally:
            self._updating_ui = False

    def _normalized_alias(self, s: str) -> str:
        return (s or "").strip()

    def _on_add(self):
        alias = self._normalized_alias(self.ed_alias.text())
        path = (self.ed_path.text() or "").strip()

        if not alias:
            QMessageBox.warning(self, "Fehler", "Bitte einen Alias-Namen eingeben.")
            self.ed_alias.setFocus()
            return

        if not path:
            QMessageBox.warning(self, "Fehler", "Bitte einen Pfad eingeben oder auswählen.")
            self.ed_path.setFocus()
            return

        if alias in self._model:
            r = QMessageBox.question(
                self,
                "Alias existiert bereits",
                f"Der Alias '{alias}' existiert schon.\nSoll der Pfad überschrieben werden?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if r != QMessageBox.Yes:
                return

        self._model[alias] = path
        self._reload_list(select_alias=alias)

    def _on_remove(self):
        cur = self.lst.currentItem()
        if not cur:
            return

        alias = cur.text()
        r = QMessageBox.question(
            self,
            "Entfernen",
            f"Alias '{alias}' wirklich entfernen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if r != QMessageBox.Yes:
            return

        self._model.pop(alias, None)
        self._reload_list(select_first=True)

    def _on_browse(self):
        start_dir = (self.ed_path.text() or "").strip() or ""
        dlg = QFileDialog(self, "Pfad auswählen", start_dir)
        dlg.setFileMode(QFileDialog.Directory)
        dlg.setOption(QFileDialog.ShowDirsOnly, True)
        dlg.setOption(QFileDialog.DontUseNativeDialog, True)  # <- NICHT NATIV

        if dlg.exec_():
            dirs = dlg.selectedFiles()
            if dirs:
                self.ed_path.setText(dirs[0])

    def _on_edit_finished(self):
        """
        Optional: wenn ein bestehender Alias ausgewählt ist,
        sollen Änderungen an Pfad/Alias (vorsichtig) ins Modell übernommen werden.
        """
        if self._updating_ui:
            return

        cur = self.lst.currentItem()
        if not cur:
            return

        old_alias = cur.text()
        new_alias = self._normalized_alias(self.ed_alias.text())
        new_path = (self.ed_path.text() or "").strip()

        # Nur Pfad geändert?
        if new_alias == old_alias:
            if new_path and self._model.get(old_alias) != new_path:
                self._model[old_alias] = new_path
            return

        # Alias umbenennen (mit Kollisionscheck)
        if not new_alias:
            # revert
            self._updating_ui = True
            try:
                self.ed_alias.setText(old_alias)
            finally:
                self._updating_ui = False
            return

        if new_alias in self._model:
            QMessageBox.warning(self, "Fehler", f"Alias '{new_alias}' existiert bereits.")
            self._updating_ui = True
            try:
                self.ed_alias.setText(old_alias)
            finally:
                self._updating_ui = False
            return

        # rename im model
        old_path = self._model.pop(old_alias, "")
        self._model[new_alias] = new_path or old_path
        self._reload_list(select_alias=new_alias)

class TypeComboDelegate(QStyledItemDelegate):
    """ComboBox-Editor nur für die Type-Spalte."""

    def __init__(self, type_column: int, parent=None):
        super().__init__(parent)
        self.type_column = type_column

    def createEditor(self, parent, option, index):
        if index.column() != self.type_column:
            return super().createEditor(parent, option, index)

        cb = QComboBox(parent)
        cb.addItems(TYPE_VALUES)
        cb.setEditable(False)
        return cb

    def setEditorData(self, editor, index):
        if index.column() != self.type_column or not isinstance(editor, QComboBox):
            return super().setEditorData(editor, index)

        current = (index.data(Qt.DisplayRole) or "").strip()
        i = editor.findText(current, Qt.MatchFixedString)
        editor.setCurrentIndex(i if i >= 0 else 0)

    def setModelData(self, editor, model, index):
        if index.column() != self.type_column or not isinstance(editor, QComboBox):
            return super().setModelData(editor, model, index)

        model.setData(index, editor.currentText(), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class TableDesignerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Phonebook.dbf - Table Designer")
        self.setModal(False)
        self.setWindowModality(Qt.NonModal)

        layout = QVBoxLayout(self)

        self.table = QTableWidget(self)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Field", "Name", "Type", "Width", "Decimal", "Index"])

        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)

        self.table.setColumnWidth(0, 55)
        self.table.setColumnWidth(1, 160)
        self.table.setColumnWidth(2, 130)
        self.table.setColumnWidth(3, 70)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 120)

        layout.addWidget(self.table)
        self.resize(520, 320)

        self._fill_demo_data()

        # Delegate: Type-Spalte (Index 2) als ComboBox editierbar
        self.table.setItemDelegateForColumn(2, TypeComboDelegate(type_column=2, parent=self.table))

        self.table.selectRow(0)

    def _fill_demo_data(self):
        rows = [
            (1,  "First_Name",    "Character", 25, 0, "None"),
            (2,  "Last_Name",     "Character", 35, 0, "None"),
            (3,  "Sex",           "Character",  1, 0, "None"),
            (4,  "Address",       "Character", 40, 0, "None"),
            (5,  "City",          "Character", 25, 0, "None"),
            (6,  "State_Prov",    "Character", 17, 0, "None"),
            (7,  "Zip_Code",      "Character",  7, 0, "Ascend"),
            (8,  "Long_Distance", "Logical",    1, 0, "None"),
            (9,  "Phone",         "Character", 10, 0, "None"),
            (10, "Fax",           "Character", 10, 0, "None"),
            (11, "Email",         "Character", 40, 0, "None"),
            (12, "Notes",         "Memo",      10, 0, ""),
        ]

        self.table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(str(val))

                if c in (0, 3, 4):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

                # Field-Spalte nicht editierbar (wie Index/Nummer)
                if c == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                self.table.setItem(r, c, item)

                
class EditorWidget(QDialog):
    def __init__(self, text="abcdef"):
        super().__init__()
        self.setWindowTitle("Demo: dBase 2026")
        self.resize(500, 300)

        self.setModal(False)
        self.setWindowModality(Qt.NonModal)
        
        # Splitter: links Tree, rechts Editor
        self.splitter = QSplitter(Qt.Horizontal, self)
        
        # --- TreeView links ---
        self.tree = QTreeView(self.splitter)
        
        # Dummy Model (später kannst du hier Klassen/Methoden/etc. einfüllen)
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Struktur"])
        
        root = model.invisibleRootItem()
        
        root.appendRow(QStandardItem("CLASS ParentForm"))
        root.appendRow(QStandardItem("METHOD Init"))
        
        self.tree.setModel(model)
        self.tree.expandAll()
        
        layout = QVBoxLayout(self)

        # Mehrzeiliges Eingabefeld
        self.text = CodeEditor(self.splitter)
        self.text.setPlaceholderText("Schreib hier was rein…")
        self.text.setLineWrapMode(self.text.NoWrap)
        self.text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.text.setLineWrapMode(self.text.NoWrap)
        self.text.setFont(QFont("Consolas", 10))
        
        self.highlighter = DBaseHighlighter(self.text.document())
        
        # Splitter-Verhältnisse
        self.splitter.setStretchFactor(0, 0)  # Tree
        self.splitter.setStretchFactor(1, 1)  # Editor
        self.splitter.setSizes([220, 800])
        
        layout.addWidget(self.splitter)

        # Button
        self.btn_run = QPushButton("Ausführen" , self)
        self.btn_run.clicked.connect(self.on_button_run_clicked)
        
        layout.addWidget(self.btn_run)
        
        hlayout = QHBoxLayout()
        self.btn_gen_python = QPushButton("Generate Python Code" , self)
        self.btn_gen_pascal = QPushButton("Generate Pascal Code" , self)
        self.btn_gen_javout = QPushButton("Generate Jave Code"   , self)
        self.btn_gen_gnucpp = QPushButton("Generate GNU C++ Code", self)
        
        self.btn_gen_python.clicked.connect(self.on_button_gen_python_clicked)
        self.btn_gen_pascal.clicked.connect(self.on_button_gen_pascal_clicked)
        self.btn_gen_javout.clicked.connect(self.on_button_gen_javout_clicked)
        self.btn_gen_gnucpp.clicked.connect(self.on_button_gen_gnucpp_clicked)
        
        hlayout.addWidget(self.btn_gen_python)
        hlayout.addWidget(self.btn_gen_pascal)
        hlayout.addWidget(self.btn_gen_javout)
        hlayout.addWidget(self.btn_gen_gnucpp)
        
        layout.addLayout(hlayout)
        
        with open("dbase.prg", "r", encoding="utf-8") as f:
            content = f.read()
            f.close()
            
        self.text.setPlainText(content)
        
    def close_tracked_windows(self):
        for w in getattr(self, "_open_windows", []):
            if w:
                w.close()
        self._open_windows = []
    
    def closeEvent(self, event):
        self.close_tracked_windows()

    def on_button_gen_javout_clicked(self):
        # 0 pre-procession
        pp = Preprocessor(include_paths=[Path("includes")])
        pre = pp.process("dbase.prg")
        
        #source = FileStream(filename, encoding="utf-8")
        source  = InputStream(pre)
        lexer   = dBaseLexer(source)
        tokens  = CommonTokenStream(lexer)
        tokens.fill();
        parser  = dBaseParser(tokens)
        tree    = parser.input_()
        codegen = DBaseToJava(parser, class_name="GenProg", package=None) #, classes=VISITOR.classes)
        codegen.generate(tree, "dbase.java")
        print("gen java ok.")

    def on_button_gen_python_clicked(self):
        # 0 pre-procession
        pp = Preprocessor(include_paths=[Path("includes")])
        pre = pp.process("dbase.prg")
        
        #source = FileStream(filename, encoding="utf-8")
        source  = InputStream(pre)
        lexer   = dBaseLexer(source)
        tokens  = CommonTokenStream(lexer)
        tokens.fill();
        parser  = dBaseParser(tokens)
        tree    = parser.input_()
        codegen = DBaseToPython(parser) #, classes=VISITOR.classes)
        codegen.generate(tree, "dbase.py")
        print("gen py ok.")
    
    def on_button_gen_gnucpp_clicked(self):
        # 0 pre-procession
        pp = Preprocessor(include_paths=[Path("includes")])
        pre = pp.process("dbase.prg")
        
        #source = FileStream(filename, encoding="utf-8")
        source  = InputStream(pre)
        lexer   = dBaseLexer(source)
        tokens  = CommonTokenStream(lexer)
        tokens.fill();
        parser  = dBaseParser(tokens)
        tree    = parser.input_()
        codegen = DBaseToCpp(parser, prog_name="genprog")
        codegen.generate(tree, "dbase.cc")
        print("gen c++ ok.")
    
    def on_button_gen_pascal_clicked(self):
        # 0 pre-procession
        pp = Preprocessor(include_paths=[Path("includes")])
        pre = pp.process("dbase.prg")
        
        #source = FileStream(filename, encoding="utf-8")
        source  = InputStream(pre)
        lexer   = dBaseLexer(source)
        tokens  = CommonTokenStream(lexer)
        tokens.fill();
        parser  = dBaseParser(tokens)
        tree    = parser.input_()
        codegen = DBaseToPascal(parser, unit_name="GenProg")
        codegen.generate(tree, "dbase.pas")
        print("gen pas ok.")
    
    def on_button_run_clicked(self):
        # Das ist die Funktion, die beim Klick ausgeführt wird
        content = self.text.toPlainText().strip()
        if not content:
            QMessageBox.information(self, "Info", "Bitte erst Text eingeben.")
            return
        try:
            with open("dbase.prg", "w", encoding="utf-8") as f:
                f.write(content)
                f.close()
            res = parse("dbase.prg")
        except UnterminatedBlockCommentError as e:
            tb_str = (f"error: {e.line}:{e.column}: {e.message}\n")
            tb_str = (tb_str + "".join(traceback.TracebackException.from_exception(e).format()))

            dlg = showException(self,
            "Kommentar-Fehler" + type(e).__name__, tb_str)
            dlg.exec_()
        except KeyError as e:
            tb_str = (f"error: {e.name}: {e.message}\n")
            tb_str = (tb_str + "".join(traceback.TracebackException.from_exception(e).format()))
            
            dlg = showException(self,
            "Internal-Fehler" + type(e).__name__, tb_str)
            dlg.exec_()
        except PermissionError as e:
            tb_str = (f"error: Zugriff verweigert\n")
            tb_str = (tb_str + "".join(traceback.TracebackException.from_exception(e).format()))
            
            dlg = showException(self,
            "Zugriff-Fehler" + type(e).__name__, tb_str)
            dlg.exec_()
        except FileNotFoundError as e:
            tb_str = (f"error: Datei nicht gefunden.\n")
            tb_str = (tb_str + "".join(traceback.TracebackException.from_exception(e).format()))
            
            dlg = showException(self,
            "Datei-Fehler" + type(e).__name__, tb_str)
            dlg.exec_()
        except NameError as e:
            msg = str(e)
            m = re.search(r"name '([^']+)' is not defined", msg)
            missing = m.group(1) if m else "<?>"
            message = "Internal Error (Python NameError)\n"
            message = message + f"{missing}: {msg}"
            
            tb_str = (f"Fehler: {message}\n")
            tb_str = (tb_str + "".join(traceback.TracebackException.from_exception(e).format()))
            
            dlg = showException(self,
            "Fehler: " + type(e).__name__, tb_str)
            dlg.exec_()
        except AttributeError as e:
            tb_str = ("".join(traceback.TracebackException.from_exception(e).format()))
            
            dlg = showException(self,
            "Attribut-Fehler: " + type(e).__name__, tb_str)
            dlg.exec_()
        except RuntimeError as e:
            tb_str = ("".join(traceback.TracebackException.from_exception(e).format()))
            
            dlg = showException(self,
            "Laufzeit-Fehler" + type(e).__name__, tb_str)
            dlg.exec_()
        except SyntaxError as e:
            tb_str = ("".join(traceback.TracebackException.from_exception(e).format()))
            
            dlg = showException(self,
            "Syntax-Fehler: " + type(e).__name__, tb_str)
            dlg.exec_()
        except Exception as e:
            tb_str = ("".join(traceback.TracebackException.from_exception(e).format()))
            
            traceback.print_exc()
            dlg = showException(self,
            "Allgemeiner Fehler: " + type(e).__name__, tb_str)
            dlg.exec_()

class IconTab(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setViewMode(QListWidget.IconMode)
        self.setResizeMode(QListWidget.Adjust)
        self.setMovement(QListWidget.Static)
        self.setWrapping(True)
        self.setWordWrap(True)
        self.setTextElideMode(Qt.ElideRight)

        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._on_context_menu)

    def _is_binary_file(self, path: str) -> bool:
        # simple + schnell: NUL-Byte oder sehr viele "komische" bytes
        try:
            with open(path, "rb") as f:
                data = f.read(2048)
            if b"\x00" in data:
                return True
            # Heuristik: Anteil nicht-printbarer Bytes
            # (tab/newline/CR zulassen)
            allowed = set(b"\t\r\n") | set(range(32, 127))
            non = sum(1 for b in data if b not in allowed)
            return len(data) > 0 and (non / max(1, len(data))) > 0.30
        except Exception:
            # wenn wir nicht lesen können → lieber "binär/unknown"
            return True

    def _file_policy(self, path: str):
        # gibt (full_menu: bool) zurück
        ext = os.path.splitext(path)[1].lower()
        if ext in (".txt", ".prg"):
            return True
        # unbekannt oder binär => nur Info
        return False

    def _on_context_menu(self, pos: QPoint):
        item = self.itemAt(pos)
        if not item:
            return

        path = item.data(Qt.UserRole) or ""
        name = item.text()  # Name unter dem Icon

        full_menu = self._file_policy(path)

        menu = QMenu(self)

        act_run   = menu.addAction("Starten / Ausführen")
        act_edit  = menu.addAction("Editieren")
        menu.addSeparator()
        act_ren   = menu.addAction("Umbenennen")
        act_copy  = menu.addAction("Kopieren")
        act_del   = menu.addAction("Löschen")
        menu.addSeparator()
        act_info  = menu.addAction("Dateiinfo")

        # Aktivierung je nach Policy
        act_run.setEnabled(full_menu)
        act_edit.setEnabled(full_menu)
        act_ren.setEnabled(full_menu)
        act_copy.setEnabled(full_menu)
        act_del.setEnabled(full_menu)
        act_info.setEnabled(True)

        chosen = menu.exec_(self.mapToGlobal(pos))
        if not chosen:
            return

        # Aktionen dispatchen:
        if chosen is act_info:
            self._show_file_info(path)
        elif chosen is act_run:
            self._run_file(path)
        elif chosen is act_edit:
            self._edit_file(name, path)
        elif chosen is act_ren:
            self._rename_item(item, path)
        elif chosen is act_copy:
            self._copy_file(path)
        elif chosen is act_del:
            self._delete_file(item, path)

    def _show_file_info(self, path: str):
        try:
            st = os.stat(path)
            QMessageBox.information(
                self,
                "Dateiinfo",
                f"{path}\n\n"
                f"Größe: {st.st_size} Bytes\n"
                f"Ext: {os.path.splitext(path)[1]}\n"
            )
        except Exception as e:
            QMessageBox.warning(self, "Dateiinfo", f"Konnte Info nicht lesen:\n{e}")

    def _run_file(self, path: str):
        # Windows: os.startfile, sonst xdg-open/open
        try:
            if os.name == "nt":
                os.startfile(path)  # noqa
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            QMessageBox.warning(self, "Ausführen", f"Konnte Datei nicht starten:\n{e}")

    def _edit_file(self, name: str, path: str):
        # hier: "name unter icon verwenden" -> name = item.text()
        # real öffnest du aber natürlich über den Pfad.
        # Übergabe an Parent (DirectoryIconDialog), der den CodeEditor öffnen kann:
        
        #dlg = self.window()  # Top-Level window (dein DirectoryIconDialog oder MDI Container)
        #dlg.mdi_open_editor(name, path)
        
        win = FileEditorWindow(parent=MAINAPP, initial_path=path, initial_text="")
        sub = MAINAPP.mdi.addSubWindow(win)
        win.resize(500, 450)
        
        # 1) immer sichtbar + Vordergrund
        win.show()
        win.raise_()
        win.activateWindow()

        # 2) falls minimiert: wieder herstellen
        win.setWindowState(win.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)

        # 3) optional: "Always on top"
        win.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        win.show()  # nach setWindowFlag nochmal show()!
        win.raise_()
        win.activateWindow()

        # Referenz halten (gegen GC)
        self._open_windows = getattr(self, "_open_windows", [])
        self._open_windows.append(win)
        #if hasattr(dlg, "open_in_code_editor"):
        #   dlg.open_in_code_editor(name, path)
        #else:
        #    QMessageBox.warning(self, "Editieren", "open_in_code_editor(...) ist nicht implementiert.")

    def _rename_item(self, item, path: str):
        # minimal: du kannst hier später eine Eingabebox bauen
        QMessageBox.information(self, "Umbenennen", "TODO: Umbenennen implementieren")

    def _copy_file(self, path: str):
        QMessageBox.information(self, "Kopieren", "TODO: Kopieren implementieren")

    def _delete_file(self, item, path: str):
        res = QMessageBox.question(self, "Löschen?", f"Wirklich löschen?\n{path}")
        if res != QMessageBox.Yes:
            return
        try:
            os.remove(path)
            row = self.row(item)
            self.takeItem(row)
        except Exception as e:
            QMessageBox.warning(self, "Löschen", f"Konnte nicht löschen:\n{e}")
            
class DirectoryIconDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Directory Icon Browser")
        self.setModal(False)
        self.setWindowModality(Qt.NonModal)

        self.icon_provider = QFileIconProvider()

        # --- Top controls ---
        self.combo = QComboBox()
        self.combo.setEditable(True)
        self.combo.setInsertPolicy(QComboBox.NoInsert)
        self.combo.currentTextChanged.connect(self._on_dir_changed)

        self.btn_pick = QPushButton("Verzeichnis…")
        self.btn_pick.clicked.connect(self.pick_directory_non_native)

        top = QHBoxLayout()
        top.addWidget(self.combo, 1)
        top.addWidget(self.btn_pick, 0)

        # --- Tabs ---
        self.tabs = QTabWidget()
        self.icon_lists = []

        for i in range(7):
            lw = IconTab()
            self.icon_lists.append(lw)
            self.tabs.addTab(lw, f"Tab {i+1}")

        # --- Layout ---
        root = QVBoxLayout(self)
        root.addLayout(top)
        root.addWidget(self.tabs, 1)

        self.resize(980, 640)

    def open_in_code_editor(self, display_name: str, path: str):
        # display_name ist der Text unter dem Icon (z.B. "foo.prg")
        # path ist der volle Pfad -> den solltest du wirklich öffnen
        # Beispiel: MDI-Variante
        if hasattr(self, "mdi_open_editor"):
            self.mdi_open_editor(title=display_name, text=open(path, "r", encoding="utf-8", errors="replace").read())
            return

        # oder normale Fenster-Variante:
        if hasattr(self, "open_file_editor"):
            self.open_file_editor(path=path, text="")
            return
            
    def pick_directory_non_native(self):
        dlg = QFileDialog(self, "Verzeichnis auswählen")
        dlg.setFileMode(QFileDialog.Directory)
        dlg.setOption(QFileDialog.ShowDirsOnly, True)
        dlg.setOption(QFileDialog.DontUseNativeDialog, True)

        if dlg.exec_():
            selected = dlg.selectedFiles()
            if selected:
                path = selected[0]
                self._add_and_select_dir(path)

    def _add_and_select_dir(self, path: str):
        path = os.path.normpath(path)

        # Wenn schon drin -> nur markieren
        idx = self.combo.findText(path, Qt.MatchExactly)
        if idx < 0:
            self.combo.addItem(path)
            idx = self.combo.findText(path, Qt.MatchExactly)

        self.combo.setCurrentIndex(idx)  # markiert/selektiert
        # _on_dir_changed() wird automatisch ausgelöst

    def _on_dir_changed(self, path: str):
        path = path.strip()
        if not path or not os.path.isdir(path):
            # Tabs ggf. leeren
            for lw in self.icon_lists:
                lw.clear()
            return
        
        self._fill_all_tabs(path)

    def _fill_all_tabs(self, directory: str):
        # gleiche Anzeige in allen 7 Tabs (kannst du später tab-spezifisch filtern)
        entries = []
        try:
            for name in os.listdir(directory):
                full = os.path.join(directory, name)
                entries.append((name, full))
        except Exception:
            entries = []
        
        for lw in self.icon_lists:
            lw.setUpdatesEnabled(False)
            lw.clear()
            
            for name, full in entries:
                info = QFileInfo(full)
                icon = self.icon_provider.icon(info)
                item = QListWidgetItem(icon, name)
                item.setToolTip(full)
                item.setData(Qt.UserRole, full)
                lw.addItem(item)
            
            lw.setUpdatesEnabled(True)
            
class UserBdeAliasesTab(QWidget):
    """
    Tab 'Benutzer BDE Aliases' wie Screenshot, inkl. Add/Remove/Edit + nicht-native Dialoge.
    Model: dict[str, dict]  alias -> {"driver": str, "options": str}
    """
    def __init__(self, parent=None, initial=None):
        super().__init__(parent)

        self._model = dict(initial or {})
        self._updating_ui = False

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # -------- Oben: Liste --------
        gb_list = QGroupBox("Definiert ein BDE Anschluss aller", self)
        v_list = QVBoxLayout(gb_list)

        self.lst = QListWidget()
        self.lst.setMinimumHeight(220)
        v_list.addWidget(self.lst)

        # -------- Unten: Editor --------
        gb_edit = QGroupBox("Benutzer BDE Alias bearbeiten", self)
        e = QGridLayout(gb_edit)
        e.setHorizontalSpacing(10)
        e.setVerticalSpacing(8)

        e.addWidget(QLabel("Alias:"), 0, 0)
        self.ed_alias = QLineEdit()
        self.ed_alias.setMinimumWidth(230)
        e.addWidget(self.ed_alias, 0, 1)

        self.btn_add = QPushButton("Hinzufügen")
        self.btn_remove = QPushButton("Entfernen")
        self.btn_add.setFixedWidth(95)
        self.btn_remove.setFixedWidth(95)
        e.addWidget(self.btn_add, 0, 2)
        e.addWidget(self.btn_remove, 0, 3)

        e.addWidget(QLabel("Driver:"), 1, 0)
        self.cb_driver = QComboBox()
        self.cb_driver.setMinimumWidth(260)
        self.cb_driver.addItems([
            "dBASE", "PARADOX", "DB2", "ORACLE", "ODBC", "SQL", "FIREBIRD"
        ])
        e.addWidget(self.cb_driver, 1, 1, 1, 3)

        e.addWidget(QLabel("Options:"), 2, 0)
        self.ed_options = QLineEdit()
        e.addWidget(self.ed_options, 2, 1, 1, 2)

        self.btn_options = QPushButton("…")
        self.btn_options.setFixedWidth(30)
        e.addWidget(self.btn_options, 2, 3, alignment=Qt.AlignLeft)

        root.addWidget(gb_list)
        root.addWidget(gb_edit)
        root.addStretch(1)

        # Demo / initial
        if not self._model:
            self._model.update({
                "dBASEContax": {
                    "driver": "dBASE",
                    "options": r"PATH:C:\Users\Jens Kallup\Documents\Programme\dBASE\dBA..."
                },
                "dBASESamples": {
                    "driver": "dBASE",
                    "options": r"PATH:C:\dBASE\Samples"
                },
                "dBASESignup": {
                    "driver": "dBASE",
                    "options": r"PATH:C:\dBASE\Signup"
                },
                "dBASETemp": {
                    "driver": "dBASE",
                    "options": r"PATH:C:\Temp"
                },
                "DmdDesnTemp": {
                    "driver": "dBASE",
                    "options": r"PATH:C:\Temp\Dmd"
                },
            })

        self._reload_list(select_first=True)

        # Signals
        self.lst.currentItemChanged.connect(self._on_list_changed)
        self.btn_add.clicked.connect(self._on_add)
        self.btn_remove.clicked.connect(self._on_remove)
        self.btn_options.clicked.connect(self._on_options_browse)

        # optional: live update bei editingFinished
        self.ed_alias.editingFinished.connect(self._on_edit_finished)
        self.ed_options.editingFinished.connect(self._on_edit_finished)
        self.cb_driver.currentIndexChanged.connect(lambda *_: self._on_edit_finished())

    # ---------- Public ----------
    def model(self) -> dict:
        return {k: dict(v) for k, v in self._model.items()}

    # ---------- Intern ----------
    def _reload_list(self, select_first=False, select_alias=None):
        self._updating_ui = True
        try:
            self.lst.clear()
            for alias in sorted(self._model.keys(), key=lambda s: s.lower()):
                self.lst.addItem(QListWidgetItem(alias))

            if select_alias:
                items = self.lst.findItems(select_alias, Qt.MatchFixedString)
                if items:
                    self.lst.setCurrentItem(items[0])
            elif select_first and self.lst.count() > 0:
                self.lst.setCurrentRow(0)
        finally:
            self._updating_ui = False

        self._sync_editor_enabled()

    def _sync_editor_enabled(self):
        has = self.lst.currentItem() is not None
        self.btn_remove.setEnabled(has)

    def _on_list_changed(self, cur, prev):
        if self._updating_ui:
            return
        self._sync_editor_enabled()

        if not cur:
            self._updating_ui = True
            try:
                self.ed_alias.setText("")
                self.cb_driver.setCurrentIndex(0)
                self.ed_options.setText("")
            finally:
                self._updating_ui = False
            return

        alias = cur.text()
        rec = self._model.get(alias, {"driver": "dBASE", "options": ""})

        self._updating_ui = True
        try:
            self.ed_alias.setText(alias)
            # Driver setzen
            i = self.cb_driver.findText(rec.get("driver", "dBASE"), Qt.MatchFixedString)
            self.cb_driver.setCurrentIndex(i if i >= 0 else 0)
            self.ed_options.setText(rec.get("options", ""))
        finally:
            self._updating_ui = False

    def _norm(self, s: str) -> str:
        return (s or "").strip()

    def _on_add(self):
        alias = self._norm(self.ed_alias.text())
        driver = self.cb_driver.currentText()
        options = self._norm(self.ed_options.text())

        if not alias:
            QMessageBox.warning(self, "Fehler", "Bitte einen Alias-Namen eingeben.")
            self.ed_alias.setFocus()
            return

        if alias in self._model:
            r = QMessageBox.question(
                self,
                "Alias existiert bereits",
                f"Der Alias '{alias}' existiert schon.\nSoll er überschrieben werden?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if r != QMessageBox.Yes:
                return

        self._model[alias] = {"driver": driver, "options": options}
        self._reload_list(select_alias=alias)

    def _on_remove(self):
        cur = self.lst.currentItem()
        if not cur:
            return
        alias = cur.text()

        r = QMessageBox.question(
            self,
            "Entfernen",
            f"Alias '{alias}' wirklich entfernen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if r != QMessageBox.Yes:
            return

        self._model.pop(alias, None)
        self._reload_list(select_first=True)

    def _on_options_browse(self):
        """
        Im Screenshot ist 'Options' meist PATH:... -> sinnvoll ist ein Directory Picker.
        Wir setzen dann automatisch 'PATH:<dir>'.
        """
        current = self._norm(self.ed_options.text())
        start_dir = ""
        if current.upper().startswith("PATH:"):
            start_dir = current[5:].strip()

        dlg = QFileDialog(self, "Verzeichnis auswählen", start_dir)
        dlg.setFileMode(QFileDialog.Directory)
        dlg.setOption(QFileDialog.ShowDirsOnly, True)
        dlg.setOption(QFileDialog.DontUseNativeDialog, True)  # <- NICHT NATIV

        if dlg.exec_():
            dirs = dlg.selectedFiles()
            if dirs:
                self.ed_options.setText(f"PATH:{dirs[0]}")

    def _on_edit_finished(self):
        """
        Änderungen am aktuell selektierten Alias ins Model übernehmen.
        Alias-Umbenennung mit Kollisionscheck.
        """
        if self._updating_ui:
            return
        cur = self.lst.currentItem()
        if not cur:
            return

        old_alias = cur.text()
        new_alias = self._norm(self.ed_alias.text())
        driver = self.cb_driver.currentText()
        options = self._norm(self.ed_options.text())

        # nur Werte aktualisieren
        if new_alias == old_alias:
            self._model[old_alias] = {"driver": driver, "options": options}
            return

        if not new_alias:
            # revert
            self._updating_ui = True
            try:
                self.ed_alias.setText(old_alias)
            finally:
                self._updating_ui = False
            return

        if new_alias in self._model:
            QMessageBox.warning(self, "Fehler", f"Alias '{new_alias}' existiert bereits.")
            self._updating_ui = True
            try:
                self.ed_alias.setText(old_alias)
            finally:
                self._updating_ui = False
            return

        # rename
        self._model.pop(old_alias, None)
        self._model[new_alias] = {"driver": driver, "options": options}
        self._reload_list(select_alias=new_alias)

class SourceAliasesTab(QWidget):
    """
    Tab 'Quell-Aliases' wie Screenshot, inkl. Add/Remove/Edit + nicht-nativer Folder-Dialog.
    model: dict[str, str]  (alias -> path)
    """
    def __init__(self, parent=None, initial=None):
        super().__init__(parent)

        self._model = dict(initial or {})
        self._updating_ui = False

        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # ---- Oben: Liste ----
        gb_list = QGroupBox("Definierte Quell-Aliases", self)
        v_list = QVBoxLayout(gb_list)

        self.lst = QListWidget()
        self.lst.setMinimumHeight(210)
        v_list.addWidget(self.lst)

        # ---- Unten: Editor ----
        gb_edit = QGroupBox("Quell-Alias bearbeiten", self)
        e = QGridLayout(gb_edit)
        e.setHorizontalSpacing(10)
        e.setVerticalSpacing(8)

        e.addWidget(QLabel("Alias:"), 0, 0)
        self.ed_alias = QLineEdit()
        self.ed_alias.setMinimumWidth(220)
        e.addWidget(self.ed_alias, 0, 1)

        self.btn_add = QPushButton("Hinzufügen")
        self.btn_remove = QPushButton("Entfernen")
        self.btn_add.setFixedWidth(95)
        self.btn_remove.setFixedWidth(95)
        e.addWidget(self.btn_add, 0, 2)
        e.addWidget(self.btn_remove, 0, 3)

        e.addWidget(QLabel("Pfad:"), 1, 0)
        self.ed_path = QLineEdit()
        e.addWidget(self.ed_path, 1, 1, 1, 2)

        self.btn_browse = QPushButton("…")
        self.btn_browse.setFixedWidth(30)
        e.addWidget(self.btn_browse, 1, 3, alignment=Qt.AlignLeft)

        root.addWidget(gb_list)
        root.addWidget(gb_edit)
        root.addStretch(1)

        # Demo / initial
        if not self._model:
            self._model.update({
                "CoreShared": r"T:\Programme\dBASE\dBASE2019\Bin\dBLCore\Shared",
                "dBStartup": r"T:\Programme\dBASE\dBASE2019\Bin\dBStartup",
                "Examples": r"T:\Programme\dBASE\dBASE2019\Examples",
                "Forms": r"T:\Programme\dBASE\dBASE2019\Forms",
                "Images": r"T:\Programme\dBASE\dBASE2019\Images",
            })

        self._reload_list(select_first=True)

        # Signals
        self.lst.currentItemChanged.connect(self._on_list_changed)
        self.btn_add.clicked.connect(self._on_add)
        self.btn_remove.clicked.connect(self._on_remove)
        self.btn_browse.clicked.connect(self._on_browse)

        # optional: Live-Update ins Modell, wenn man Felder verlässt
        self.ed_alias.editingFinished.connect(self._on_edit_finished)
        self.ed_path.editingFinished.connect(self._on_edit_finished)

    # ---------- Public ----------
    def model(self) -> dict:
        """Gibt eine Kopie des Modells zurück."""
        return dict(self._model)

    # ---------- Intern ----------
    def _reload_list(self, select_first=False, select_alias=None):
        self._updating_ui = True
        try:
            self.lst.clear()
            for alias in sorted(self._model.keys(), key=lambda s: s.lower()):
                self.lst.addItem(QListWidgetItem(alias))

            if select_alias:
                items = self.lst.findItems(select_alias, Qt.MatchFixedString)
                if items:
                    self.lst.setCurrentItem(items[0])
            elif select_first and self.lst.count() > 0:
                self.lst.setCurrentRow(0)
        finally:
            self._updating_ui = False

        # falls leer
        self._sync_editor_enabled()

    def _sync_editor_enabled(self):
        has = self.lst.currentItem() is not None
        self.btn_remove.setEnabled(has)

    def _on_list_changed(self, cur, prev):
        if self._updating_ui:
            return
        self._sync_editor_enabled()

        if not cur:
            self.ed_alias.setText("")
            self.ed_path.setText("")
            return

        alias = cur.text()
        path = self._model.get(alias, "")

        self._updating_ui = True
        try:
            self.ed_alias.setText(alias)
            self.ed_path.setText(path)
        finally:
            self._updating_ui = False

    def _normalized_alias(self, s: str) -> str:
        return (s or "").strip()

    def _on_add(self):
        alias = self._normalized_alias(self.ed_alias.text())
        path = (self.ed_path.text() or "").strip()

        if not alias:
            QMessageBox.warning(self, "Fehler", "Bitte einen Alias-Namen eingeben.")
            self.ed_alias.setFocus()
            return

        if not path:
            QMessageBox.warning(self, "Fehler", "Bitte einen Pfad eingeben oder auswählen.")
            self.ed_path.setFocus()
            return

        if alias in self._model:
            r = QMessageBox.question(
                self,
                "Alias existiert bereits",
                f"Der Alias '{alias}' existiert schon.\nSoll der Pfad überschrieben werden?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if r != QMessageBox.Yes:
                return

        self._model[alias] = path
        self._reload_list(select_alias=alias)

    def _on_remove(self):
        cur = self.lst.currentItem()
        if not cur:
            return

        alias = cur.text()
        r = QMessageBox.question(
            self,
            "Entfernen",
            f"Alias '{alias}' wirklich entfernen?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if r != QMessageBox.Yes:
            return

        self._model.pop(alias, None)
        self._reload_list(select_first=True)

    def _on_browse(self):
        start_dir = (self.ed_path.text() or "").strip() or ""
        dlg = QFileDialog(self, "Pfad auswählen", start_dir)
        dlg.setFileMode(QFileDialog.Directory)
        dlg.setOption(QFileDialog.ShowDirsOnly, True)
        dlg.setOption(QFileDialog.DontUseNativeDialog, True)  # <- NICHT NATIV

        if dlg.exec_():
            dirs = dlg.selectedFiles()
            if dirs:
                self.ed_path.setText(dirs[0])

    def _on_edit_finished(self):
        """
        Optional: wenn ein bestehender Alias ausgewählt ist,
        sollen Änderungen an Pfad/Alias (vorsichtig) ins Modell übernommen werden.
        """
        if self._updating_ui:
            return

        cur = self.lst.currentItem()
        if not cur:
            return

        old_alias = cur.text()
        new_alias = self._normalized_alias(self.ed_alias.text())
        new_path = (self.ed_path.text() or "").strip()

        # Nur Pfad geändert?
        if new_alias == old_alias:
            if new_path and self._model.get(old_alias) != new_path:
                self._model[old_alias] = new_path
            return

        # Alias umbenennen (mit Kollisionscheck)
        if not new_alias:
            # revert
            self._updating_ui = True
            try:
                self.ed_alias.setText(old_alias)
            finally:
                self._updating_ui = False
            return

        if new_alias in self._model:
            QMessageBox.warning(self, "Fehler", f"Alias '{new_alias}' existiert bereits.")
            self._updating_ui = True
            try:
                self.ed_alias.setText(old_alias)
            finally:
                self._updating_ui = False
            return

        # rename im model
        old_path = self._model.pop(old_alias, "")
        self._model[new_alias] = new_path or old_path
        self._reload_list(select_alias=new_alias)
        
class DesktopPropertiesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

        self.setWindowTitle("Desktop Properties")
        self.setModal(False)
        self.setWindowModality(Qt.NonModal)

        root = QVBoxLayout(self)

        # Tabs
        self.tabs = QTabWidget(self)
        root.addWidget(self.tabs)

        # Platzhalter-Tabs (wie im Bild)
        self.tabs.addTab(self._build_tab_country (), "Country")
        self.tabs.addTab(self._build_tab_table   (), "Table")
        self.tabs.addTab(self._build_tab_data    (), "Data Entry")
        self.tabs.addTab(self._build_tab_files   (), "Files")
        self.tabs.addTab(self._build_tab_app     (), "Application")
        self.tabs.addTab(self._build_tab_prog    (), "Programming")
        self.tabs.addTab(self._build_tab_aliase  (), "Source Aliases")
        self.tabs.addTab(self._build_tab_usrbde  (), "User-BDE-Aliases")
        
        # Bottom buttons: OK / Abbrechen / Hilfe / Übernehmen
        btn_row = QHBoxLayout()
        btn_row.addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.btn_ok     = QPushButton("OK")
        self.btn_cancel = QPushButton("Abbrechen")
        self.btn_help   = QPushButton("Hilfe")
        self.btn_apply  = QPushButton("Übernehmen")

        for b in (self.btn_ok, self.btn_cancel, self.btn_help, self.btn_apply):
            b.setFixedWidth(95)

        self.btn_ok    .clicked.connect(self.onbtn_accept)
        self.btn_cancel.clicked.connect(self.onbtn_cancel)
        self.btn_help  .clicked.connect(lambda: None)   # später füllen
        self.btn_apply .clicked.connect(lambda: None)  # später füllen

        btn_row.addWidget(self.btn_ok)
        btn_row.addWidget(self.btn_cancel)
        btn_row.addWidget(self.btn_help)
        btn_row.addWidget(self.btn_apply)

        root.addLayout(btn_row)

        self.resize(520, 360)
    
    def onbtn_accept(self):
        self.accept()
        self.mdi.close()
        
    def onbtn_cancel(self):
        self.reject()
        self.mdi.close()

    def _build_tab_aliase(self) -> QWidget:
        tab = QWidget()
        SourceAliasesTab(tab)
        return tab
    
    def _build_tab_usrbde(self) -> QWidget:
        tab = QWidget()
        UserBdeAliasesTab(tab)
        return tab

    def _build_tab_country(self) -> QWidget:
        tab = QWidget()
        g = QGridLayout(tab)
        g.setContentsMargins(12, 12, 12, 12)
        g.setHorizontalSpacing(18)
        g.setVerticalSpacing(12)

        # --- Zahlenwerte ---
        gb_num = QGroupBox("Zahlenwerte", tab)
        num = QGridLayout(gb_num)
        num.setHorizontalSpacing(10)
        num.setVerticalSpacing(8)

        num.addWidget(QLabel("Trennzeichen:"), 0, 0)
        self.ed_thousand = QLineEdit(".")
        self.ed_thousand.setFixedWidth(34)
        num.addWidget(self.ed_thousand, 0, 1, alignment=Qt.AlignLeft)

        num.addWidget(QLabel("Dezimalzeichen:"), 1, 0)
        self.ed_decimal = QLineEdit(",")
        self.ed_decimal.setFixedWidth(34)
        num.addWidget(self.ed_decimal, 1, 1, alignment=Qt.AlignLeft)

        num.addWidget(QLabel("Muster:"), 2, 0)
        num.addWidget(QLabel("1.000.000,00"), 2, 1, 1, 2)

        # --- Währungssymbol ---
        gb_cur = QGroupBox("Währungssymbol", tab)
        cur = QGridLayout(gb_cur)
        cur.setHorizontalSpacing(10)
        cur.setVerticalSpacing(8)

        cur.addWidget(QLabel("Position:"), 0, 0)
        self.rb_left = QRadioButton("Links")
        self.rb_right = QRadioButton("Rechts")
        self.rb_right.setChecked(True)
        cur.addWidget(self.rb_left, 0, 1)
        cur.addWidget(self.rb_right, 1, 1)

        cur.addWidget(QLabel("Symbol:"), 2, 0)
        self.ed_currency = QLineEdit("€")
        self.ed_currency.setFixedWidth(50)
        cur.addWidget(self.ed_currency, 2, 1, alignment=Qt.AlignLeft)

        cur.addWidget(QLabel("Muster:"), 3, 0)
        cur.addWidget(QLabel("129,99 €"), 3, 1, 1, 2)

        # --- Datum ---
        gb_date = QGroupBox("Datum", tab)
        date = QGridLayout(gb_date)
        date.setHorizontalSpacing(10)
        date.setVerticalSpacing(8)

        date.addWidget(QLabel("Datumsformat:"), 0, 0)
        self.cb_datefmt = QComboBox()
        self.cb_datefmt.addItems(["DMY", "MDY", "YMD", "ISO"])
        self.cb_datefmt.setCurrentText("DMY")
        self.cb_datefmt.setFixedWidth(120)
        date.addWidget(self.cb_datefmt, 0, 1, alignment=Qt.AlignLeft)

        date.addWidget(QLabel("Datumszeichen:"), 1, 0)
        self.ed_datesep = QLineEdit(".")
        self.ed_datesep.setFixedWidth(34)
        date.addWidget(self.ed_datesep, 1, 1, alignment=Qt.AlignLeft)

        self.chk_century = QCheckBox("Jahrhundert")
        self.chk_century.setChecked(True)
        date.addWidget(self.chk_century, 2, 0, 1, 2)

        date.addWidget(QLabel("Muster:"), 3, 0)
        date.addWidget(QLabel("08.02.2026"), 3, 1, 1, 2)

        # --- Umgebungssprache ---
        gb_ui = QGroupBox("Umgebungssprache", tab)
        ui = QGridLayout(gb_ui)
        self.cb_lang = QComboBox()
        self.cb_lang.addItems(["DE - Deutsch", "EN - English", "FR - Français"])
        self.cb_lang.setCurrentText("DE - Deutsch")
        self.cb_lang.setFixedWidth(160)
        ui.addWidget(self.cb_lang, 0, 0)

        # --- Sprachtreiber ---
        gb_drv = QGroupBox("Sprachtreiber", tab)
        drv = QGridLayout(gb_drv)
        self.chk_mismatch = QCheckBox("Warnung bei Konflikten")
        drv.addWidget(self.chk_mismatch, 0, 0)

        # Positionierung wie Screenshot
        g.addWidget(gb_num, 0, 0)
        g.addWidget(gb_date, 0, 1)
        g.addWidget(gb_cur, 1, 0)
        g.addWidget(gb_ui, 1, 1)
        g.addWidget(gb_drv, 2, 1)

        g.setRowStretch(3, 1)
        return tab
    
    def _build_tab_table(self) -> QWidget:
        tab = QWidget()
        g = QGridLayout(tab)
        g.setContentsMargins(12, 12, 12, 12)
        g.setHorizontalSpacing(18)
        g.setVerticalSpacing(12)

        # --- Mehrplatz (links oben) ---
        gb_multi = QGroupBox("Mehrplatz", tab)
        l_multi = QGridLayout(gb_multi)
        l_multi.setHorizontalSpacing(10)
        l_multi.setVerticalSpacing(8)

        self.chk_lock = QCheckBox("Sperren")
        self.chk_exclusive = QCheckBox("Exklusiv")

        l_multi.addWidget(self.chk_lock, 0, 0, 1, 2)
        l_multi.addWidget(self.chk_exclusive, 1, 0, 1, 2)

        l_multi.addWidget(QLabel("Aktualisieren:"), 2, 0)
        self.spin_refresh = QSpinBox()
        self.spin_refresh.setRange(0, 9999)
        self.spin_refresh.setFixedWidth(70)
        l_multi.addWidget(self.spin_refresh, 2, 1, alignment=Qt.AlignLeft)

        l_multi.addWidget(QLabel("Wiederholen:"), 3, 0)
        self.spin_retry = QSpinBox()
        self.spin_retry.setRange(0, 9999)
        self.spin_retry.setFixedWidth(70)
        l_multi.addWidget(self.spin_retry, 3, 1, alignment=Qt.AlignLeft)

        # default wie Screenshot
        self.chk_lock.setChecked(True)

        # --- Standardtabellentyp (links mitte) ---
        gb_default = QGroupBox("Standardtabellentyp", tab)
        l_def = QVBoxLayout(gb_default)
        
        self.rb_dbase   = QRadioButton("dBASE")
        self.rb_paradox = QRadioButton("Paradox")
        self.rb_sqlite3 = QRadioButton("SQLite 3")
        self.rb_mysql   = QRadioButton("MySQL")
        
        self.rb_dbase.setChecked(True)
        
        l_def.addWidget(self.rb_dbase)
        l_def.addWidget(self.rb_paradox)
        l_def.addWidget(self.rb_sqlite3)
        l_def.addWidget(self.rb_mysql)

        # --- Systemtabellen (links unten) ---
        gb_system = QGroupBox("Systemtabellen", tab)
        l_sys = QVBoxLayout(gb_system)
        self.chk_system_show = QCheckBox("Anzeigen")
        l_sys.addWidget(self.chk_system_show)

        # --- Blockgrößen (rechts oben) ---
        gb_blocks = QGroupBox("Blockgrößen", tab)
        l_blocks = QGridLayout(gb_blocks)
        l_blocks.setHorizontalSpacing(10)
        l_blocks.setVerticalSpacing(8)

        l_blocks.addWidget(QLabel("Indexblock:"), 0, 0)
        self.spin_indexblock = QSpinBox()
        self.spin_indexblock.setRange(1, 9999)
        self.spin_indexblock.setFixedWidth(80)
        self.spin_indexblock.setValue(1)
        l_blocks.addWidget(self.spin_indexblock, 0, 1, alignment=Qt.AlignLeft)

        l_blocks.addWidget(QLabel("Memoblock:"), 1, 0)
        self.spin_memoblock = QSpinBox()
        self.spin_memoblock.setRange(1, 9999)
        self.spin_memoblock.setFixedWidth(80)
        self.spin_memoblock.setValue(8)
        l_blocks.addWidget(self.spin_memoblock, 1, 1, alignment=Qt.AlignLeft)

        # --- Andere (rechts mitte) ---
        gb_other = QGroupBox("Andere", tab)
        l_other = QGridLayout(gb_other)
        l_other.setHorizontalSpacing(10)
        l_other.setVerticalSpacing(6)

        self.chk_autosave = QCheckBox("Automatische Speicherung")
        self.chk_deleted = QCheckBox("Löschmarken")
        self.chk_encrypt = QCheckBox("Verschlüsselung")
        self.chk_ident = QCheckBox("Identisch")
        self.chk_approx = QCheckBox("Annähernd")
        self.chk_autonull = QCheckBox("AutoNullFields")

        # wie Screenshot: Löschmarken + Verschlüsselung + AutoNullFields aktiv
        self.chk_deleted.setChecked(True)
        self.chk_encrypt.setChecked(True)
        self.chk_autonull.setChecked(True)

        l_other.addWidget(self.chk_autosave, 0, 0, 1, 2)
        l_other.addWidget(self.chk_deleted, 1, 0, 1, 2)
        l_other.addWidget(self.chk_encrypt, 2, 0, 1, 2)
        l_other.addWidget(self.chk_ident, 3, 0)
        l_other.addWidget(self.chk_approx, 4, 0)
        l_other.addWidget(self.chk_autonull, 3, 1)

        self.btn_components = QPushButton("Komponententypen zuordnen...")
        self.btn_components.setFixedWidth(220)
        l_other.addWidget(self.btn_components, 5, 0, 1, 2, alignment=Qt.AlignLeft)

        # Positionen im Grid wie im Bild
        g.addWidget(gb_multi,   0, 0)
        g.addWidget(gb_blocks,  0, 1)
        g.addWidget(gb_default, 1, 0)
        g.addWidget(gb_other,   1, 1)
        g.addWidget(gb_system,  2, 0)

        # etwas Luft nach unten/rechts
        g.setRowStretch(3, 1)
        g.setColumnStretch(2, 1)
        
        return tab
    
    def _build_tab_app(self) -> QWidget:
        tab = QWidget()
        g = QGridLayout(tab)
        g.setContentsMargins(12, 12, 12, 12)
        g.setHorizontalSpacing(18)
        g.setVerticalSpacing(12)

        # --- Experten anzeigen (links oben) ---
        gb_exp = QGroupBox("Experten anzeigen", tab)
        exp = QVBoxLayout(gb_exp)
        exp.setSpacing(6)

        chk_form = QCheckBox("Formular")
        chk_report = QCheckBox("Report")
        chk_labels = QCheckBox("Etiketten")
        chk_datamodule = QCheckBox("Datenmodul")
        chk_table = QCheckBox("Tabelle")

        # wie Screenshot: alle an
        for c in (chk_form, chk_report, chk_labels, chk_datamodule, chk_table):
            c.setChecked(True)
            exp.addWidget(c)

        # --- Dateimenü (links unten) ---
        gb_file = QGroupBox("Dateimenü", tab)
        fm = QGridLayout(gb_file)
        fm.setHorizontalSpacing(10)
        fm.setVerticalSpacing(8)

        fm.addWidget(QLabel("Anzahl Dateien:"), 0, 0)
        sp_files = QSpinBox()
        sp_files.setRange(0, 99)
        sp_files.setValue(5)
        sp_files.setFixedWidth(80)
        fm.addWidget(sp_files, 0, 1, alignment=Qt.AlignLeft)

        fm.addWidget(QLabel("Anzahl Projekte:"), 1, 0)
        sp_projects = QSpinBox()
        sp_projects.setRange(0, 99)
        sp_projects.setValue(5)
        sp_projects.setFixedWidth(80)
        fm.addWidget(sp_projects, 1, 1, alignment=Qt.AlignLeft)

        # --- Datenbank (rechts oben) ---
        gb_db = QGroupBox("Datenbank", tab)
        db = QVBoxLayout(gb_db)
        db.setSpacing(6)

        chk_login = QCheckBox("Anmeldungen sichern")
        chk_sqltrace = QCheckBox("SQL-Ablaufverfolgung")
        chk_login.setChecked(True)
        db.addWidget(chk_login)
        db.addWidget(chk_sqltrace)

        # --- Fenster (rechts mitte) ---
        gb_win = QGroupBox("Fenster", tab)
        win = QVBoxLayout(gb_win)
        win.setSpacing(6)

        chk_fit = QCheckBox("Fenstergröße an Inhalt anpassen")
        chk_anim = QCheckBox("Animationen endlos abspielen")
        chk_ole = QCheckBox("Objekte als OLE 2.0 speichern")

        # wie Screenshot: alle 3 an
        chk_fit.setChecked(True)
        chk_anim.setChecked(True)
        chk_ole.setChecked(True)

        win.addWidget(chk_fit)
        win.addWidget(chk_anim)
        win.addWidget(chk_ole)

        # --- Andere (rechts unten) ---
        gb_other = QGroupBox("Andere", tab)
        other = QVBoxLayout(gb_other)
        other.setSpacing(6)

        chk_splash = QCheckBox("Startbildschirm")
        chk_splash.setChecked(True)
        other.addWidget(chk_splash)

        # Layout wie im Screenshot:
        # links: Experten anzeigen + Dateimenü
        # rechts: Datenbank + Fenster + Andere
        g.addWidget(gb_exp,   0, 0)
        g.addWidget(gb_db,    0, 1)
        g.addWidget(gb_file,  1, 0)
        g.addWidget(gb_win,   1, 1)
        g.addWidget(gb_other, 2, 1)

        g.setRowStretch(3, 1)
        return tab
    
    def _build_tab_files(self) -> QWidget:
        tab = QWidget()
        g = QGridLayout(tab)
        g.setContentsMargins(12, 12, 12, 12)
        g.setHorizontalSpacing(18)
        g.setVerticalSpacing(12)

        # ---------- Pfad (links oben) ----------
        gb_path = QGroupBox("Pfad", tab)
        path = QGridLayout(gb_path)
        path.setHorizontalSpacing(10)
        path.setVerticalSpacing(8)

        path.addWidget(QLabel("Aktuelles Verzeichnis:"), 0, 0, 1, 2)

        # Zeile: Combo/Text + Folder Button
        self_cur_dir = QLineEdit(r"F:\Heinz\ext\irgl\...")
        self_cur_dir.setMinimumWidth(240)
        btn_cur_browse = QPushButton("📁")
        btn_cur_browse.setFixedWidth(30)

        path.addWidget(self_cur_dir, 1, 0)
        path.addWidget(btn_cur_browse, 1, 1, alignment=Qt.AlignLeft)

        path.addWidget(QLabel("Suchpfad:"), 2, 0, 1, 2)

        self_search_path = QLineEdit("")
        btn_search_browse = QPushButton("📁")
        btn_search_browse.setFixedWidth(30)

        path.addWidget(self_search_path, 3, 0)
        path.addWidget(btn_search_browse, 3, 1, alignment=Qt.AlignLeft)

        # ---------- Ausgabeprotokoll (links unten) ----------
        gb_log = QGroupBox("Ausgabeprotokoll", tab)
        log = QGridLayout(gb_log)
        log.setHorizontalSpacing(10)
        log.setVerticalSpacing(8)

        chk_enable_log = QCheckBox("Protokoll anlegen")
        log.addWidget(chk_enable_log, 0, 0, 1, 2)

        log.addWidget(QLabel("Name der Protokolldatei:"), 1, 0, 1, 2)

        ed_logfile = QLineEdit("")
        ed_logfile.setEnabled(False)
        btn_logfile = QPushButton("✎")
        btn_logfile.setFixedWidth(30)
        btn_logfile.setEnabled(False)

        log.addWidget(ed_logfile, 2, 0)
        log.addWidget(btn_logfile, 2, 1, alignment=Qt.AlignLeft)

        rb_overwrite = QRadioButton("Überschreiben")
        rb_append = QRadioButton("Anhängen")
        rb_overwrite.setEnabled(False)
        rb_append.setEnabled(False)
        rb_overwrite.setChecked(True)

        log.addWidget(rb_overwrite, 3, 0, 1, 2)
        log.addWidget(rb_append, 4, 0, 1, 2)

        # Enable/Disable abhängig von Checkbox
        def _toggle_log(on: bool):
            ed_logfile.setEnabled(on)
            btn_logfile.setEnabled(on)
            rb_overwrite.setEnabled(on)
            rb_append.setEnabled(on)

        chk_enable_log.toggled.connect(_toggle_log)

        # ---------- Editor (rechts oben) ----------
        gb_editor = QGroupBox("Editor", tab)
        ed = QGridLayout(gb_editor)
        ed.setHorizontalSpacing(10)
        ed.setVerticalSpacing(8)

        ed.addWidget(QLabel("Externer Quelltext-Editor:"), 0, 0, 1, 2)

        ed_editor = QLineEdit("")
        btn_editor = QPushButton("✎")
        btn_editor.setFixedWidth(30)

        ed.addWidget(ed_editor, 1, 0)
        ed.addWidget(btn_editor, 1, 1, alignment=Qt.AlignLeft)

        # ---------- Andere (rechts mitte) ----------
        gb_other = QGroupBox("Andere", tab)
        other = QVBoxLayout(gb_other)
        other.setSpacing(6)

        chk_backup = QCheckBox("Sicherungsdateien")
        chk_sessions = QCheckBox("Arbeitssitzungen")
        other.addWidget(chk_backup)
        other.addWidget(chk_sessions)

        # Layout wie Screenshot
        g.addWidget(gb_path,   0, 0)
        g.addWidget(gb_editor, 0, 1)
        g.addWidget(gb_log,    1, 0)
        g.addWidget(gb_other,  1, 1)

        g.setRowStretch(2, 1)
        return tab
    
    def _build_tab_data(self) -> QWidget:
        tab = QWidget()
        g = QGridLayout(tab)
        g.setContentsMargins(12, 12, 12, 12)
        g.setHorizontalSpacing(18)
        g.setVerticalSpacing(12)

        # ---------- Tastatur (links oben) ----------
        gb_kbd = QGroupBox("Tastatur", tab)
        kbd = QGridLayout(gb_kbd)
        kbd.setHorizontalSpacing(10)
        kbd.setVerticalSpacing(8)

        chk_confirm = QCheckBox("Bestätigung")
        chk_cua = QCheckBox("CUA-Eingabe")
        chk_esc = QCheckBox("Escape")

        # wie Screenshot: alle 3 an
        chk_confirm.setChecked(True)
        chk_cua.setChecked(True)
        chk_esc.setChecked(True)

        kbd.addWidget(chk_confirm, 0, 0, 1, 2)
        kbd.addWidget(chk_cua,     1, 0, 1, 2)
        kbd.addWidget(chk_esc,     2, 0, 1, 2)

        kbd.addWidget(QLabel("Tastaturpuffer:"), 3, 0)
        sp_buf = QSpinBox()
        sp_buf.setRange(0, 9999)
        sp_buf.setValue(49)
        sp_buf.setFixedWidth(90)
        kbd.addWidget(sp_buf, 3, 1, alignment=Qt.AlignLeft)

        # ---------- Andere (links unten) ----------
        gb_other = QGroupBox("Andere", tab)
        other = QGridLayout(gb_other)
        other.setHorizontalSpacing(10)
        other.setVerticalSpacing(8)

        other.addWidget(QLabel("Epoche:"), 0, 0)
        sp_epoch = QSpinBox()
        sp_epoch.setRange(0, 9999)
        sp_epoch.setValue(1950)
        sp_epoch.setFixedWidth(90)
        other.addWidget(sp_epoch, 0, 1, alignment=Qt.AlignLeft)

        # ---------- Signalton (rechts) ----------
        gb_beep = QGroupBox("Signalton", tab)
        beep = QGridLayout(gb_beep)
        beep.setHorizontalSpacing(10)
        beep.setVerticalSpacing(8)

        chk_beep = QCheckBox("Einschalten")
        chk_beep.setChecked(True)
        beep.addWidget(chk_beep, 0, 0, 1, 2)

        beep.addWidget(QLabel("Frequenz:"), 1, 0)
        sp_freq = QSpinBox()
        sp_freq.setRange(0, 20000)
        sp_freq.setValue(512)
        sp_freq.setFixedWidth(90)
        beep.addWidget(sp_freq, 1, 1, alignment=Qt.AlignLeft)

        beep.addWidget(QLabel("Dauer:"), 2, 0)
        sp_dur = QSpinBox()
        sp_dur.setRange(0, 10000)
        sp_dur.setValue(50)
        sp_dur.setFixedWidth(90)
        beep.addWidget(sp_dur, 2, 1, alignment=Qt.AlignLeft)

        btn_test = QPushButton("Prüfen")
        btn_test.setFixedWidth(95)
        beep.addWidget(btn_test, 3, 0, 1, 2, alignment=Qt.AlignLeft)

        # Aktivieren/Deaktivieren je nach Einschalten
        def _toggle_beep(on: bool):
            sp_freq.setEnabled(on)
            sp_dur.setEnabled(on)
            btn_test.setEnabled(on)

        chk_beep.toggled.connect(_toggle_beep)
        _toggle_beep(True)

        # Optional: wirklich piepen
        def _do_beep():
            # QApplication.beep() ist plattformabhängig, reicht aber als "Test"
            from PyQt5.QtWidgets import QApplication
            QApplication.beep()

        btn_test.clicked.connect(_do_beep)

        # Layout wie Screenshot
        g.addWidget(gb_kbd,   0, 0)
        g.addWidget(gb_beep,  0, 1, 2, 1)
        g.addWidget(gb_other, 1, 0)

        g.setRowStretch(2, 1)
        return tab
    
    def _build_tab_prog(self) -> QWidget:
        tab = QWidget()
        g = QGridLayout(tab)
        g.setContentsMargins(12, 12, 12, 12)
        g.setHorizontalSpacing(18)
        g.setVerticalSpacing(12)

        # --- Befehlsausgabe (links oben) ---
        gb_out = QGroupBox("Befehlsausgabe", tab)
        out = QGridLayout(gb_out)
        out.setHorizontalSpacing(10)
        out.setVerticalSpacing(8)

        out.addWidget(QLabel("Dezimalstellen:"), 0, 0)
        sp_dec = QSpinBox()
        sp_dec.setRange(0, 20)
        sp_dec.setValue(2)
        sp_dec.setFixedWidth(80)
        out.addWidget(sp_dec, 0, 1, alignment=Qt.AlignLeft)

        out.addWidget(QLabel("Genauigkeit:"), 1, 0)
        sp_prec = QSpinBox()
        sp_prec.setRange(0, 20)
        sp_prec.setValue(10)
        sp_prec.setFixedWidth(80)
        out.addWidget(sp_prec, 1, 1, alignment=Qt.AlignLeft)

        out.addWidget(QLabel("Rand:"), 2, 0)
        sp_margin = QSpinBox()
        sp_margin.setRange(0, 999)
        sp_margin.setValue(0)
        sp_margin.setFixedWidth(80)
        out.addWidget(sp_margin, 2, 1, alignment=Qt.AlignLeft)

        chk_blank = QCheckBox("Leerzeichen")
        chk_trace = QCheckBox("Ablaufverfolgung")
        chk_fieldnames = QCheckBox("Feldnamen")

        # wie Screenshot: Leerzeichen + Feldnamen an
        chk_blank.setChecked(True)
        chk_fieldnames.setChecked(True)

        out.addWidget(chk_blank, 3, 0, 1, 2)
        out.addWidget(chk_trace, 4, 0, 1, 2)
        out.addWidget(chk_fieldnames, 5, 0, 1, 2)

        # --- Programmentwicklung (rechts oben) ---
        gb_dev = QGroupBox("Programmentwicklung", tab)
        dev = QGridLayout(gb_dev)
        dev.setHorizontalSpacing(10)
        dev.setVerticalSpacing(8)

        chk_fulltest = QCheckBox("Volltest")
        chk_buildtime = QCheckBox("Erstellungszeit")
        chk_buildtime.setChecked(True)

        dev.addWidget(chk_fulltest, 0, 0, 1, 2)
        dev.addWidget(chk_buildtime, 1, 0, 1, 2)

        # --- Andere (rechts mitte) ---
        gb_other = QGroupBox("Andere", tab)
        other = QGridLayout(gb_other)
        other.setHorizontalSpacing(10)
        other.setVerticalSpacing(8)

        chk_design = QCheckBox("Design")
        chk_hiprec = QCheckBox("High Precision")
        chk_protect = QCheckBox("Änderungsschutz")
        chk_fullpath = QCheckBox("Vollständige Pfadangabe")

        # wie Screenshot: Design + Änderungsschutz an
        chk_design.setChecked(True)
        chk_protect.setChecked(True)

        other.addWidget(chk_design, 0, 0)
        other.addWidget(chk_hiprec, 0, 1)
        other.addWidget(chk_protect, 1, 0, 1, 2)
        other.addWidget(chk_fullpath, 2, 0, 1, 2)

        # --- Error Handling (unten, über beide Spalten) ---
        gb_err = QGroupBox("Error Handling", tab)
        err = QGridLayout(gb_err)
        err.setHorizontalSpacing(10)
        err.setVerticalSpacing(8)

        err.addWidget(QLabel("Error Action:"), 0, 0)
        cb_action = QComboBox()
        cb_action.addItems([
            "0 - Ignore",
            "1 - Message",
            "2 - Log",
            "3 - Abort",
            "4 - Show Error Dialog",
        ])
        cb_action.setCurrentText("4 - Show Error Dialog")
        cb_action.setMinimumWidth(260)
        err.addWidget(cb_action, 0, 1, 1, 2)

        # Error Log File + browse button
        err.addWidget(QLabel("Error Log File:"), 1, 0)
        ed_log = QLineEdit("PLUSerr.log")
        err.addWidget(ed_log, 1, 1)
        btn_log = QPushButton("...")
        btn_log.setFixedWidth(28)
        err.addWidget(btn_log, 1, 2, alignment=Qt.AlignLeft)

        # Maximum Size + unit label
        err.addWidget(QLabel("Maximum Size:"), 2, 0)
        sp_max = QSpinBox()
        sp_max.setRange(0, 999999)
        sp_max.setValue(100)
        sp_max.setFixedWidth(90)
        err.addWidget(sp_max, 2, 1, alignment=Qt.AlignLeft)
        err.addWidget(QLabel("Kilobytes"), 2, 2, alignment=Qt.AlignLeft)

        # HTML Error Template + browse button
        err.addWidget(QLabel("HTML Error Template:"), 3, 0)
        ed_tpl = QLineEdit("error.htm")
        err.addWidget(ed_tpl, 3, 1)
        btn_tpl = QPushButton("...")
        btn_tpl.setFixedWidth(28)
        err.addWidget(btn_tpl, 3, 2, alignment=Qt.AlignLeft)

        # Layout wie Screenshot
        g.addWidget(gb_out,   0, 0)
        g.addWidget(gb_dev,   0, 1)
        g.addWidget(gb_other, 1, 1)
        g.addWidget(gb_err,   2, 0, 1, 2)

        g.setRowStretch(3, 1)
        return tab

    def _help(self):
        QMessageBox.information(self, "Help", "Hier könnte deine Hilfe stehen :)")

    # Damit Esc auch sauber schließt
    def reject(self):
        super().reject()
        
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.mdi = QMdiArea(self)
        self.setCentralWidget(self.mdi)

        # Beispiel-Menü "Fenster"
        # Menü: Eigenschaften -> Arbeitsplatz
        menubar = self.menuBar()
        menu_properties = menubar.addMenu("Eigenschaften")
        menu_windows    = menubar.addMenu("Fenster")
        
        action_workplace = QAction("Arbeitsplatz", self)
        action_workplace.triggered.connect(self.open_workplace_properties)
        
        menu_properties.addAction(action_workplace)
        
        action_cascade = QAction("Kaskadieren",   self, triggered = self.mdi.cascadeSubWindows)
        action_tile    = QAction("Nebeneinander", self, triggered = self.mdi.tileSubWindows)
        
        menu_windows.addAction(action_cascade)
        menu_windows.addAction(action_tile)

        self._dlg_workplace = None  # Dialog-Instanz merken (nicht jedes Mal neu)
        
        dlg = DirectoryIconDialog()
        sub = self.mdi.addSubWindow(dlg)
        sub.show()
        
        self.mdi_open_editor()
        self.mdi_open_table_designer()
        
    def mdi_open_editor(self, title="Unbenannt", text=""):
        w = EditorWidget(text)
        sub = self.mdi.addSubWindow(w)     # Qt erzeugt ein QMdiSubWindow
        sub.setWindowTitle(title)
        sub.resize(900, 650)
        w.show()
        sub.show()
        
        self.mdi.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mdi.setVerticalScrollBarPolicy  (Qt.ScrollBarAsNeeded)
        
        self.mdi.setActiveSubWindow(sub)
        return sub

    def mdi_open_table_designer(self):
        dlg = TableDesignerDialog()
        sub = self.mdi.addSubWindow(dlg)
        sub.show()
    
    def open_workplace_properties(self):
        if self._dlg_workplace is None:
            self._dlg_workplace = DesktopPropertiesDialog(self)
            sub = MAINAPP.mdi.addSubWindow(self._dlg_workplace)
            # Wenn Benutzer das Fenster schließt, Instanz wieder freigeben
            self._dlg_workplace.mdi = sub
            self._dlg_workplace.finished.connect(lambda _=0: setattr(self, "_dlg_workplace", None))

        self._dlg_workplace.show()
        self._dlg_workplace.raise_()
        self._dlg_workplace.activateWindow()
        
def main():
    app = ensure_qt_app()
    if app is not None:
        global MAINAPP
        MAINAPP = MainWindow()
        MAINAPP.show()
        sys.exit(app.exec_())
    else:
        print("Qt5 kann nicht gestartet werden.")
        sys.exit(1)

if __name__ == "__main__":
    main()
