# sudoku_qt5_pro.py
# Python 3.x + PyQt5
import sys
import json
import random
import time
from pathlib import Path

from PyQt5.QtCore import Qt, QTimer, QTime, QDateTime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QGridLayout, QHBoxLayout, QVBoxLayout,
    QLabel, QSpinBox, QMessageBox, QFrame, QInputDialog, QDialog, QTableWidget,
    QTableWidgetItem, QHeaderView, QFileDialog, QSizePolicy
)
from PyQt5.QtGui import QFont

HIGHSCORE_PATH = Path("sudoku_highscores.json")
MAX_HIGHSCORES = 50

# ------------------ Sudoku-Logik und Solver ------------------
class Sudoku:
    def __init__(self, seed=None):
        if seed is not None:
            random.seed(seed)
        self.solution = [[0]*9 for _ in range(9)]
        self.puzzle = [[0]*9 for _ in range(9)]

    # Vollständiges Board generieren (Backtracking)
    def generate_full(self):
        self.solution = [[0]*9 for _ in range(9)]
        nums = list(range(1, 10))

        def valid(r, c, n, grid):
            br, bc = (r//3)*3, (c//3)*3
            if any(grid[r][x] == n for x in range(9)): return False
            if any(grid[y][c] == n for y in range(9)): return False
            for rr in range(br, br+3):
                for cc in range(bc, bc+3):
                    if grid[rr][cc] == n:
                        return False
            return True

        def backtrack(pos=0):
            if pos == 81:
                return True
            r, c = divmod(pos, 9)
            if self.solution[r][c] != 0:
                return backtrack(pos+1)
            random.shuffle(nums)
            for n in nums:
                if valid(r, c, n, self.solution):
                    self.solution[r][c] = n
                    if backtrack(pos+1):
                        return True
                    self.solution[r][c] = 0
            return False

        # Beschleunigung: zufällige erste Zeile
        base = list(range(1, 10))
        random.shuffle(base)
        self.solution[0] = base[:]
        backtrack(1)

    # Zählt Lösungen (bis max 2), um Eindeutigkeit zu prüfen
    @staticmethod
    def count_solutions(board, limit=2):
        grid = [row[:] for row in board]
        nums = list(range(1, 10))

        # Finde nächstes leeres Feld (heuristik: mit min. Kandidaten)
        def find_empty_with_fewest():
            best = None
            best_len = 10
            best_cands = []
            for r in range(9):
                for c in range(9):
                    if grid[r][c] == 0:
                        cands = []
                        for n in nums:
                            if Sudoku.is_valid_move(grid, r, c, n):
                                cands.append(n)
                        if not cands:
                            return (r, c, [])  # Sackgasse
                        if len(cands) < best_len:
                            best = (r, c)
                            best_len = len(cands)
                            best_cands = cands
                            if best_len == 1:
                                return (r, c, best_cands)
            if best is None:
                return None  # voll
            return (*best, best_cands)

        count = 0

        def backtrack():
            nonlocal count
            if count >= limit:
                return
            step = find_empty_with_fewest()
            if step is None:
                count += 1
                return
            r, c, cands = step
            if not cands:
                return
            # kleine Zufallsstreuung
            random.shuffle(cands)
            for n in cands:
                grid[r][c] = n
                backtrack()
                if count >= limit:
                    grid[r][c] = 0
                    return
                grid[r][c] = 0

        backtrack()
        return count

    @staticmethod
    def is_valid_move(board, r, c, n):
        if n == 0:
            return True
        # Zeile/Spalte
        for i in range(9):
            if i != c and board[r][i] == n:
                return False
            if i != r and board[i][c] == n:
                return False
        # Block
        br, bc = (r//3)*3, (c//3)*3
        for rr in range(br, br+3):
            for cc in range(bc, bc+3):
                if (rr, cc) != (r, c) and board[rr][cc] == n:
                    return False
        return True

    @staticmethod
    def is_complete_and_correct(board, solution):
        return all(board[r][c] == solution[r][c] for r in range(9) for c in range(9))

    def make_unique_puzzle(self, level):
        """Generiert Puzzle mit **eindeutiger** Lösung. Level 1-100 steuert Anzahl der leeren Felder."""
        self.generate_full()
        full = [row[:] for row in self.solution]
        grid = [row[:] for row in full]

        # Zielanzahl "Löcher" aus Level ableiten (wie zuvor, aber nur grobe Zielgröße)
        empty_min, empty_max = 35, 59  # 46..22 Hinweise
        target_holes = int(empty_min + (empty_max - empty_min) * (level - 1) / 99.0)
        target_holes = max(empty_min, min(empty_max, target_holes))

        positions = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(positions)

        removed = 0
        for (r, c) in positions:
            if removed >= target_holes:
                break
            if grid[r][c] == 0:
                continue

            # Symmetrisches Entfernen (optional)
            r2, c2 = 8 - r, 8 - c
            saved1 = grid[r][c]
            saved2 = grid[r2][c2]
            grid[r][c] = 0
            if (r2, c2) != (r, c):
                grid[r2][c2] = 0

            # Prüfe Eindeutigkeit
            sol_count = Sudoku.count_solutions(grid, limit=2)
            if sol_count != 1:
                # Rückgängig machen
                grid[r][c] = saved1
                if (r2, c2) != (r, c):
                    grid[r2][c2] = saved2
            else:
                if (r2, c2) != (r, c):
                    removed += 2
                else:
                    removed += 1

        # Falls wegen Eindeutigkeits-Constraint nicht genug Löcher möglich, akzeptieren wir weniger.
        self.puzzle = grid


# ------------------ Highscore-Handling ------------------
def load_highscores(path=HIGHSCORE_PATH):
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_highscores(data, path=HIGHSCORE_PATH):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False


# ------------------ GUI ------------------
class SudokuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sudoku (PyQt5) – Eindeutige Lösung, Undo/Redo, Hinweise & Highscore")
        self.setMinimumSize(900, 620)

        self.sudoku = Sudoku()
        self.level = 1
        self.selected = None  # (r, c)

        self.board_btns = [[None]*9 for _ in range(9)]
        self.current_board = [[0]*9 for _ in range(9)]
        self.given_mask = [[False]*9 for _ in range(9)]

        # Undo/Redo-Stacks: Einträge = (r, c, alt, neu)
        self.undo_stack = []
        self.redo_stack = []

        # Timer / Stats
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self._tick)
        self.elapsed_seconds = 0
        self.hints_used = 0
        self.game_active = False

        self._build_ui()
        self.new_game()

    # ---------- UI-Aufbau ----------
    def _build_ui(self):
        ui_bold_font = QFont("Arial", 11, QFont.Bold)
        
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(12)

        # Linke Seitenleiste
        side = QVBoxLayout()
        side.setSpacing(8)

        # Kopfzeile: Level, Neues Spiel
        header = QHBoxLayout()
        level_lbl = QLabel("Level:")
        level_lbl.setFont(ui_bold_font)
        header.addWidget(level_lbl)
        
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 100)
        self.level_spin.setValue(1)
        self.level_spin.setToolTip("1 = leicht, 100 = schwer")
        self.level_spin.setFont(ui_bold_font)
        self.level_spin.valueChanged.connect(lambda v: setattr(self, "level", v))
        
        new_btn = QPushButton("Neues Spiel")
        new_btn.setFont(ui_bold_font)
        new_btn.clicked.connect(self.new_game)
        
        header.addWidget(self.level_spin)
        header.addWidget(new_btn)
        header.addStretch(1)
        side.addLayout(header)

        # Timer / Info
        info_row = QHBoxLayout()
        self.time_lbl = QLabel("Zeit: 00:00"); self.time_lbl.setFont(ui_bold_font)
        self.hint_lbl = QLabel("Hinweise: 0"); self.hint_lbl.setFont(ui_bold_font)
        
        info_row.addWidget(self.time_lbl)
        info_row.addWidget(self.hint_lbl)
        
        info_row.addStretch(1)
        side.addLayout(info_row)

        # Linien
        side.addWidget(self._hline())

        # Zahlen-Pad (3x3 Grid)
        zlbl = QLabel("Zahlen:")
        zlbl.setFont(ui_bold_font)
        side.addWidget(zlbl)
        
        self.num_buttons = []
        num_grid = QGridLayout()
        num_grid.setSpacing(6)
        
        for n in range(1, 10):
            btn = QPushButton(str(n))
            # Buttons sollen schön mitwachsen
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setMinimumSize(40, 40)
            btn.setFont(ui_bold_font)
            btn.clicked.connect(lambda _, x=n: self._place_number(x))
            self.num_buttons.append(btn)
            r = (n - 1) // 3
            c = (n - 1) % 3
            num_grid.addWidget(btn, r, c)
        
        side.addLayout(num_grid)
        
        clear_btn = QPushButton("Löschen")
        clear_btn.setMinimumHeight(34)
        clear_btn.setFont(ui_bold_font)
        clear_btn.clicked.connect(lambda: self._place_number(0))
        side.addWidget(clear_btn)
        
        side.addSpacing(6)
        side.addWidget(self._hline())

        # Aktionen: Hinweis / Undo / Redo / Highscores
        actions = QVBoxLayout()
        hint_btn = QPushButton("Hinweis")
        hint_btn.setFont(ui_bold_font)  
        hint_btn.clicked.connect(self._hint)

        undo_btn = QPushButton("Rückgängig")
        undo_btn.setFont(ui_bold_font)  
        undo_btn.clicked.connect(self._undo)

        redo_btn = QPushButton("Wiederholen")
        redo_btn.setFont(ui_bold_font)  
        redo_btn.clicked.connect(self._redo)

        highs_btn = QPushButton("Highscores anzeigen")
        highs_btn.setFont(ui_bold_font)  
        highs_btn.clicked.connect(self._show_highscores)

        export_btn = QPushButton("Highscores exportieren…")
        export_btn.setFont(ui_bold_font)  
        export_btn.clicked.connect(self._export_highscores)

        for w in (hint_btn, undo_btn, redo_btn, highs_btn, export_btn):
            w.setFixedHeight(32)
            actions.addWidget(w)

        actions.addStretch(1)
        side.addLayout(actions)

        root.addLayout(side, 0)

        # Spielfeld (rechts)
        board_container = QVBoxLayout()
        board_container.setSpacing(6)
        title = QLabel("Spielfeld:")
        title.setFont(ui_bold_font)
        board_container.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(0)

        font = QFont()
        font.setPointSize(16)
        font.setBold(True)

        for r in range(9):
            for c in range(9):
                btn = QPushButton("")
                btn.setCheckable(True)
                btn.setAutoExclusive(True)
                btn.setFont(font)
                btn.setFixedSize(56, 56)
                btn.clicked.connect(lambda _, rr=r, cc=c: self._select_cell(rr, cc))
                self._style_cell_border(btn, r, c)
                grid.addWidget(btn, r, c)
                self.board_btns[r][c] = btn

        board_container.addLayout(grid)
        board_container.addStretch(1)
        root.addLayout(board_container, 1)

    def _hline(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def _style_cell_border(self, btn, r, c):
        t = 3 if r % 3 == 0 else 1
        b = 3 if r % 3 == 2 else 1
        l = 3 if c % 3 == 0 else 1
        rgt = 3 if c % 3 == 2 else 1
        style = (
            f"QPushButton {{"
            f"  border-top: {t}px solid #333;"
            f"  border-bottom: {b}px solid #333;"
            f"  border-left: {l}px solid #333;"
            f"  border-right: {rgt}px solid #333;"
            f"  background: #fafafa;"
            f"}}"
            f"QPushButton:checked {{"
            f"  background: #d7ebff;"
            f"}}"
        )
        btn.setStyleSheet(style)

    # ---------- Spielsteuerung ----------
    def new_game(self):
        self.sudoku.make_unique_puzzle(self.level)
        self.current_board = [row[:] for row in self.sudoku.puzzle]
        self.given_mask = [[self.sudoku.puzzle[r][c] != 0 for c in range(9)] for r in range(9)]
        self.selected = None
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.hints_used = 0
        self.elapsed_seconds = 0
        self._update_status_labels()
        self._refresh_board_ui()
        self.game_active = False  # startet bei erster Eingabe
        self.timer.stop()

    def _refresh_board_ui(self):
        for r in range(9):
            for c in range(9):
                btn = self.board_btns[r][c]
                val = self.current_board[r][c]
                given = self.given_mask[r][c]
                btn.setChecked(False)
                btn.setText("" if val == 0 else str(val))
                if given:
                    btn.setEnabled(False)
                    self._style_cell_border(btn, r, c)
                    btn.setStyleSheet(btn.styleSheet() + " QPushButton{ color:#111; background:#f0f0f0; } QPushButton:checked{ background:#d7ebff; }")
                else:
                    btn.setEnabled(True)
                    self._style_cell_border(btn, r, c)
                    btn.setStyleSheet(btn.styleSheet() + " QPushButton{ color:#0a0a0a; } QPushButton:checked{ background:#d7ebff; }")
        self._recolor_conflicts()

    def _select_cell(self, r, c):
        if not self.given_mask[r][c]:
            self.selected = (r, c)
        else:
            self.selected = None

    def _start_timer_if_needed(self):
        if not self.game_active:
            self.game_active = True
            self.timer.start()

    def _tick(self):
        self.elapsed_seconds += 1
        self._update_status_labels()

    def _update_status_labels(self):
        m, s = divmod(self.elapsed_seconds, 60)
        self.time_lbl.setText(f"Zeit: {m:02d}:{s:02d}")
        self.hint_lbl.setText(f"Hinweise: {self.hints_used}")

    # ---------- Eingaben / Undo / Redo ----------
    def _place_number(self, n):
        if not self.selected:
            return
        r, c = self.selected
        if self.given_mask[r][c]:
            return
        old = self.current_board[r][c]
        if old == n:
            return
        self._start_timer_if_needed()
        self.current_board[r][c] = n
        self.board_btns[r][c].setText("" if n == 0 else str(n))
        # Stack aktualisieren
        self.undo_stack.append((r, c, old, n))
        self.redo_stack.clear()
        self._recolor_conflicts()
        self._check_win()

    def _undo(self):
        if not self.undo_stack:
            return
        r, c, old, new = self.undo_stack.pop()
        self.current_board[r][c] = old
        self.board_btns[r][c].setText("" if old == 0 else str(old))
        self.redo_stack.append((r, c, old, new))
        self._recolor_conflicts()

    def _redo(self):
        if not self.redo_stack:
            return
        r, c, old, new = self.redo_stack.pop()
        self.current_board[r][c] = new
        self.board_btns[r][c].setText("" if new == 0 else str(new))
        self.undo_stack.append((r, c, old, new))
        self._recolor_conflicts()
        self._check_win()

    # ---------- Hinweise ----------
    def _hint(self):
        # Hinweis nur, wenn Zelle ausgewählt + nicht Vorgabe
        if not self.selected:
            QMessageBox.information(self, "Hinweis", "Bitte zuerst eine leere Zelle auswählen.")
            return
        r, c = self.selected
        if self.given_mask[r][c]:
            return
        correct = self.sudoku.solution[r][c]
        old = self.current_board[r][c]
        if old == correct:
            return
        self._start_timer_if_needed()
        self.current_board[r][c] = correct
        self.board_btns[r][c].setText(str(correct))
        self.hints_used += 1
        self._update_status_labels()
        # Undo/Redo registrieren
        self.undo_stack.append((r, c, old, correct))
        self.redo_stack.clear()
        self._recolor_conflicts()
        self._check_win()

    # ---------- Darstellung Konflikte ----------
    def _recolor_conflicts(self):
        for r in range(9):
            for c in range(9):
                btn = self.board_btns[r][c]
                val = self.current_board[r][c]
                given = self.given_mask[r][c]
                base = "#111" if given else "#0a0a0a"
                color = base
                if val != 0:
                    saved = self.current_board[r][c]
                    self.current_board[r][c] = 0
                    ok = Sudoku.is_valid_move(self.current_board, r, c, saved)
                    self.current_board[r][c] = saved
                    if not ok:
                        color = "#c01616"
                self._style_cell_border(btn, r, c)
                btn.setStyleSheet(btn.styleSheet() + f" QPushButton{{ color:{color}; }} QPushButton:checked{{ background:#d7ebff; }}")

    # ---------- Siegprüfung / Scoring / Highscores ----------
    def _check_win(self):
        if all(self.current_board[r][c] != 0 for r in range(9) for c in range(9)):
            if Sudoku.is_complete_and_correct(self.current_board, self.sudoku.solution):
                self.timer.stop()
                self.game_active = False
                score = self._compute_score(self.level, self.elapsed_seconds, self.hints_used)
                m, s = divmod(self.elapsed_seconds, 60)
                # Name erfragen
                name, ok = QInputDialog.getText(self, "Geschafft!", 
                    f"Glückwunsch! Sudoku korrekt gelöst.\nZeit: {m:02d}:{s:02d}\nHinweise: {self.hints_used}\nPunkte: {score}\n\nDein Name für die Highscore-Liste?")
                if ok:
                    self._store_highscore(name.strip() or "Anonym", score)
                else:
                    # trotzdem speichern als "Anonym"
                    self._store_highscore("Anonym", score)
                QMessageBox.information(self, "Ergebnis", f"Zeit: {m:02d}:{s:02d}\nHinweise: {self.hints_used}\nPunkte: {score}")
            # sonst: voll aber falsch -> nichts, Konfliktfärbung zeigt Fehler

    def _compute_score(self, level, seconds, hints):
        # Beispiel-Formel:
        # Basis wächst mit Level; Zeitabzug; starker Hinweisabzug
        base = 800 + level * 25
        time_penalty = int(seconds * 1.2)  # 1.2 Punkte je Sekunde
        hint_penalty = hints * 150         # 150 Punkte je Hinweis
        score = max(0, base - time_penalty - hint_penalty)
        return score

    def _store_highscore(self, name, score):
        entry = {
            "name": name,
            "date": QDateTime.currentDateTime().toString(Qt.ISODate),
            "level": int(self.level),
            "seconds": int(self.elapsed_seconds),
            "hints": int(self.hints_used),
            "score": int(score)
        }
        data = load_highscores()
        data.append(entry)
        # Sortierung: zuerst Score absteigend, dann Zeit aufsteigend
        data.sort(key=lambda e: (-e["score"], e["seconds"]))
        # Kürzen
        if len(data) > MAX_HIGHSCORES:
            data = data[:MAX_HIGHSCORES]
        ok = save_highscores(data)
        if not ok:
            QMessageBox.warning(self, "Fehler", f"Konnte Highscores nicht speichern: {HIGHSCORE_PATH}")

    def _show_highscores(self):
        data = load_highscores()
        dlg = QDialog(self)
        dlg.setWindowTitle("Highscores")
        dlg.resize(600, 420)
        layout = QVBoxLayout(dlg)

        tbl = QTableWidget(dlg)
        tbl.setColumnCount(6)
        tbl.setHorizontalHeaderLabels(["Name", "Datum", "Level", "Zeit", "Hinweise", "Punkte"])
        tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tbl.setRowCount(len(data))

        for i, e in enumerate(data):
            m, s = divmod(int(e.get("seconds", 0)), 60)
            row = [
                e.get("name", ""),
                e.get("date", ""),
                str(e.get("level", "")),
                f"{m:02d}:{s:02d}",
                str(e.get("hints", 0)),
                str(e.get("score", 0)),
            ]
            for j, val in enumerate(row):
                item = QTableWidgetItem(val)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                tbl.setItem(i, j, item)

        layout.addWidget(tbl)

        # Buttons unten
        btn_row = QHBoxLayout()
        close_btn = QPushButton("Schließen")
        close_btn.clicked.connect(dlg.accept)
        btn_row.addStretch(1)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        dlg.exec_()

    def _export_highscores(self):
        data = load_highscores()
        if not data:
            QMessageBox.information(self, "Export", "Keine Highscores vorhanden.")
            return
        fn, _ = QFileDialog.getSaveFileName(self, "Highscores exportieren", "highscores.json", "JSON (*.json)")
        if not fn:
            return
        try:
            with open(fn, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Export", f"Highscores exportiert nach:\n{fn}")
        except Exception as e:
            QMessageBox.warning(self, "Export-Fehler", str(e))


# ------------------ main ------------------
def main():
    app = QApplication(sys.argv)
    w = SudokuWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
