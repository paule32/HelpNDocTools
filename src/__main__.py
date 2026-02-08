# ---------------------------------------------------------------------------
# File:   __main__.py
# Author: (c) 2024, 2025 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import sys
import os
import shlex
import html
import time

from PyQt5 import QtCore, QtGui, QtWidgets

os.environ.setdefault(
    "QTWEBENGINE_CHROMIUM_FLAGS",
    "--disable-gpu --disable-software-rasterizer"
)

class SplashWindow(QtWidgets.QWidget):
    done = QtCore.pyqtSignal(int)
    
    def __init__(self, image_path: str = None, parent=None):
        super().__init__(parent)
        self.setWindowFlag(QtCore.Qt.SplashScreen, True)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        
        # --- UI ---
        self._build_ui(image_path)
        self._apply_style()
        QtCore.QTimer.singleShot(0, self._center_on_screen)
        
        # Prozess/Parser
        self.proc = None
        self._buffer = b""
        self._finished = False  # via DONE/_on_finished
        self._anims = []        # Animationen am Leben halten
    
    def _build_ui(self, image_path):
        outer = QtWidgets.QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)
        
        card = QtWidgets.QFrame()
        card.setObjectName("card")
        card.setFrameShape(QtWidgets.QFrame.NoFrame)
        card_layout = QtWidgets.QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)
        
        # Bild
        self.image = QtWidgets.QLabel(alignment=QtCore.Qt.AlignCenter)
        self.image.setObjectName("image")
        if image_path and os.path.exists(image_path):
            pix = QtGui.QPixmap(image_path)
            self.image.setPixmap(pix.scaled(420, 220, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        else:
            self.image.setText("<i>(kein Bild gefunden)</i>")
        card_layout.addWidget(self.image)
        
        # Status-Text
        self.status = QtWidgets.QLabel("Starte...")
        self.status.setObjectName("status")
        self.status.setAlignment(QtCore.Qt.AlignCenter)
        card_layout.addWidget(self.status)
        
        # ProgressBar
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(True)
        card_layout.addWidget(self.progress)
        
        outer.addWidget(card)
    
    def _apply_style(self):
        self.setFixedSize(520, 380)
        self.setStyleSheet(
            """
            #card { background: rgba(30,30,34, 230); border-radius: 16px; }
            QLabel#status { color: #EAEAEA; font-size: 14px; }
            QLabel#image { color: #B0B0B0; }
            QProgressBar { height: 16px; border-radius: 8px; background: #2c2c2f; color: #EAEAEA; }
            QProgressBar::chunk { border-radius: 8px; background: #4C8BF5; }
            """
        )
    
    def _center_on_screen(self):
        screen = QtWidgets.QApplication.primaryScreen()
        if screen:
            geo = screen.availableGeometry()
            self.move(geo.center() - self.rect().center())
    
    # ---------- Prozess starten & verbinden ----------
    def start_process(self, cmd_args):
        """Startet die 2. Anwendung via QProcess und verdrahtet stdout->Parser."""
        if not cmd_args:
            raise RuntimeError("Keine Kommandozeile für die 2. Anwendung übergeben.")
        
        self.proc = QtCore.QProcess(self)
        # Wichtig: Ungepufferte Ausgabe im Kindprozess sicherstellen (python -u / fflush)
        self.proc.setProcessChannelMode(QtCore.QProcess.MergedChannels)
        self.proc.readyReadStandardOutput.connect(self._on_ready_read)
        self.proc.finished.connect(self._on_finished)
        self.proc.errorOccurred.connect(self._on_error)
        
        # Environment (optional anpassbar)
        env = QtCore.QProcessEnvironment.systemEnvironment()
        env.insert("SPLASH_PID", str(os.getpid()))
        self.proc.setProcessEnvironment(env)
        
        # Start
        self.status.setText("Starte Anwendung...")
        self.show()
        self.raise_()
        
        program = cmd_args[0]
        arguments = cmd_args[1:]
        self.proc.start(program, arguments)
        if not self.proc.waitForStarted(5000):
            self._fail(f"Start fehlgeschlagen: {self.proc.errorString()}")
    
    # ---------- Parser für stdout-Kommandos ----------
    def _on_ready_read(self):
        self._buffer += self.proc.readAllStandardOutput().data()
        while b"\n" in self._buffer:
            line, self._buffer = self._buffer.split(b"\n", 1)
            try:
                self._handle_command(line.decode("utf-8", errors="replace").strip())
            except Exception as e:
                # Fehler im Kommando nicht kritisch, nur anzeigen
                self.status.setText(f"Parserfehler: {e}")
    
    # --- Utilities: Fade/Show/Hide ---
    def _animate_opacity(self, start, end, duration_ms, finished_cb=None):
        anim = QtCore.QPropertyAnimation(self, b"windowOpacity", self)
        anim.setDuration(duration_ms)
        anim.setStartValue(start)
        anim.setEndValue(end)
        def _on_finished():
            try:
                if finished_cb:
                    finished_cb()
            finally:
                # aufräumen
                if anim in self._anims:
                    self._anims.remove(anim)
        anim.finished.connect(_on_finished)
        self._anims.append(anim)
        anim.start(QtCore.QAbstractAnimation.DeleteWhenStopped)
    
    def show_with_fade(self, text: str = None, force_front: bool = True):
        if text:
            self.status.setText(text)

        # kurz on-top setzen, danach wieder entfernen, damit der Fokus sicher zu uns springt
        if force_front and not (self.windowFlags() & QtCore.Qt.WindowStaysOnTopHint):
            self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)

        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        if self.windowHandle():
            self.windowHandle().requestActivate()
        self.activateWindow()
        QtWidgets.QApplication.setActiveWindow(self)

        def _after_show():
            # on-top wieder entfernen, damit der Splash nicht dauerhaft über allem bleibt
            if force_front and (self.windowFlags() & QtCore.Qt.WindowStaysOnTopHint):
                self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, False)
                self.show()  # Flags anwenden

        self._animate_opacity(0.0, 1.0, 250, _after_show)
        
        QtCore.QTimer.singleShot(150, lambda: self.windowHandle() and self.windowHandle().requestActivate())
        QtCore.QTimer.singleShot(300, self.raise_)
        QtCore.QTimer.singleShot(300, self.activateWindow)
    
    def hide_with_fade(self):
        def _after():
            self.hide()
            self.setWindowOpacity(1.0)  # zurücksetzen für späteres SHOW
        self._animate_opacity(1.0, 0.0, 250, _after)

    def exit_with_fade(self):
        self._animate_opacity(1.0, 0.0, 250, QtWidgets.QApplication.quit)
    
    # -----------------------------------------------------------
    ## Einfache Text-Protokoll-Kommandos:
    # PROGRESS <0-100>
    # TEXT <frei>
    # HIDE / SHOW / DONE
    # FAIL <nachricht>
    # -----------------------------------------------------------
    def _handle_command(self, line: str):
        if not line:
            return
        parts = line.split(" ", 2)
        spl = parts[0].upper()
        cmd = parts[1].upper()
        arg = parts[2] if len(parts) > 2 else ""
        
        if spl == "SPLASH":
            if cmd == "PROGRESS":
                try:
                    val = max(0, min(100, int(arg)))
                    self.progress.setValue(val)
                    if val >= 100:
                        self.status.setText("Fertig…")
                except ValueError:
                    self.status.setText(f"Ungültiger PROGRESS: {arg}")
                return
            elif cmd == "HIDE":
                self.hide_with_fade()
                return
            elif cmd == "SHOW":
                self.show_with_fade(arg or None)
                return
            elif cmd == "TEXT":
                self.status.setText(arg)
                return
            elif cmd == "DONE":
                self._finished = True
                if arg:
                    self.status.seText(arg)
                self.progress.setValue(100)
                self.status.setText("Done.")
                self.exit_with_fade()
                return
            elif cmd == "FAIL":
                self._fail(arg or "Fehler gemeldet")
                return
            
        # Unbekanntes Kommando -> als Text anzeigen
        self.status.setText(line)
    
    def _on_finished(self, exitCode, exitStatus):
        # Wenn die App ohne DONE endet, schließen wir dennoch (soft)
        if not self._finished:
            self.status.setText("Thanks for using")
            if  self.progress.value() < 100:
                self.progress.setValue(100)
            self.exit_with_fade()
    
    def _on_error(self, err):
        self._fail(f"Prozessfehler: {self.proc.errorString()}")
    
    def _fail(self, message: str):
        self.status.setText(f"<span style='color:#ff6b6b'>Fehler: {html.escape(message)}</span>")
        # Nach kurzer Zeit trotzdem schließen
        QtCore.QTimer.singleShot(2800, self._fade_and_close)

def build_cmd(worker:str):
    extra  = sys.argv[1:]  # alles, was du splash.py übergibst
    # Fall A: Du hast KEIN explizites Programm übergeben -> nimm client.py + extra
    # Fall B: Erstes Arg sieht NICHT nach Programmdatei aus (z.B. "gui") -> nimm client.py + extra
    first = extra[0] if extra else ""
    is_prog = first.endswith(".py") or first.endswith(".exe") or os.path.sep in first or os.path.exists(first)
    
    if not extra or not is_prog:
        # Default: Python + client.py + alle extra-Args (z.B. "gui" usw.)
        return [sys.executable, "-u", worker] + extra
    else:
        # Du übergibst explizit ein Programm; dann unverändert weiterreichen
        return extra

def main():
    app = QtWidgets.QApplication(sys.argv)
    
    # Optional: Bildpfad aus ENV oder fester Pfad
    os.environ["SPLASH_IMAGE"] = "./logo.png"
    image_path = os.environ.get("SPLASH_IMAGE", None)
    
    splash = SplashWindow(image_path=image_path)
    worker = os.path.join(os.path.dirname(__file__), "client.py")
    cmd    = build_cmd(worker)
    
    env = os.environ.copy()
    os.environ["BJKID"] = r"\x08\x02\x79"
    
    splash.start_process(cmd)
    sys.exit(app.exec_())

if __name__ == "__main__":
    major = sys.version_info[0]
    minor = sys.version_info[1]
    if (major < 3 and minor < 12):
        print("Python 3.12+ are required for the application")
        sys.exit(1)
    main()
    sys.exit(0)
 