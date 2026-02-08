# PyQt5 Halma mit einfacher KI (greedy, 1-Ply) für Rot.

from PyQt5 import QtWidgets, QtGui, QtCore
import sys

PLAYER_NONE = 0
PLAYER_A = 1  # Mensch (blau) standardmäßig
PLAYER_B = 2  # KI (rot)

DIRS = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if not (dx == 0 and dy == 0)]

def in_bounds(x, y, n):
    return 0 <= x < n and 0 <= y < n

def make_triangle_coords(n, size):
    coords = []
    for s in range(size):
        for i in range(s + 1):
            coords.append((i, s - i))
    return coords

class GameState(QtCore.QObject):
    state_changed = QtCore.pyqtSignal()

    def __init__(self, n=8, tri_size=4, parent=None):
        super().__init__(parent)
        self.n = n
        self.tri_size = tri_size
        self.camp_A = set(make_triangle_coords(n, tri_size))
        self.camp_B = set((n - 1 - x, n - 1 - y) for (x, y) in self.camp_A)
        self.board = [[PLAYER_NONE for _ in range(n)] for _ in range(n)]
        for (x, y) in self.camp_A:
            self.board[y][x] = PLAYER_A
        for (x, y) in self.camp_B:
            self.board[y][x] = PLAYER_B
        self.to_move = PLAYER_A
        self.selected = None
        self.legal_targets = set()

    # --- Board helpers ---
    def piece_at(self, pos):
        x, y = pos
        return self.board[y][x]

    def set_piece(self, pos, val):
        x, y = pos
        self.board[y][x] = val

    def reset_selection(self):
        self.selected = None
        self.legal_targets = set()
        self.state_changed.emit()

    def is_win(self, player):
        camp_target = self.camp_B if player == PLAYER_A else self.camp_A
        for (x, y) in camp_target:
            if self.board[y][x] != player:
                return False
        return True

    # --- Move generation ---
    def simple_steps(self, pos):
        x0, y0 = pos
        res = set()
        for dx, dy in DIRS:
            x, y = x0 + dx, y0 + dy
            if in_bounds(x, y, self.n) and self.board[y][x] == PLAYER_NONE:
                res.add((x, y))
        return res

    def jump_targets_from(self, start):
        visited = set()
        results = set()
        def dfs(p):
            visited.add(p)
            x0, y0 = p
            for dx, dy in DIRS:
                xm, ym = x0 + dx, y0 + dy
                x2, y2 = x0 + 2*dx, y0 + 2*dy
                if not in_bounds(x2, y2, self.n) or not in_bounds(xm, ym, self.n):
                    continue
                if self.board[ym][xm] in (PLAYER_A, PLAYER_B) and self.board[y2][x2] == PLAYER_NONE:
                    if (x2, y2) not in results:
                        results.add((x2, y2))
                    if (x2, y2) not in visited:
                        dfs((x2, y2))
        dfs(start)
        results.discard(start)
        return results

    def compute_legal_targets(self, pos):
        if self.piece_at(pos) != self.to_move:
            return set()
        return self.simple_steps(pos) | self.jump_targets_from(pos)

    def all_moves_for(self, player):
        """Liste aller legalen (src, dst)-Züge für 'player' im aktuellen Zustand."""
        moves = []
        save_to_move = self.to_move
        self.to_move = player  # für compute_legal_targets
        for y in range(self.n):
            for x in range(self.n):
                if self.board[y][x] == player:
                    src = (x, y)
                    for dst in self.simple_steps(src) | self.jump_targets_from(src):
                        moves.append((src, dst))
        self.to_move = save_to_move
        return moves

    # --- Interaction ---
    def try_select(self, pos):
        if not in_bounds(pos[0], pos[1], self.n):
            return
        if self.piece_at(pos) == self.to_move:
            self.selected = pos
            self.legal_targets = self.compute_legal_targets(pos)
            self.state_changed.emit()

    def try_move(self, target):
        if self.selected is None:
            return False
        if target not in self.legal_targets:
            return False
        src = self.selected
        moving = self.piece_at(src)
        self.set_piece(src, PLAYER_NONE)
        self.set_piece(target, moving)
        self.selected = None
        self.legal_targets = set()
        self.to_move = PLAYER_B if self.to_move == PLAYER_A else PLAYER_A
        self.state_changed.emit()
        return True

    # --- Simulation (für KI) ---
    def simulate_after(self, src, dst):
        """Erzeuge einen simulierten Zustand nach (src->dst) ohne deepcopy/QObject-Pickling."""
        # Neues GameState-Gerüst mit identischen Parametern
        new_state = GameState(n=self.n, tri_size=self.tri_size)

        # Aktuelles Board kopieren (flache Kopie pro Zeile reicht)
        new_state.board = [row[:] for row in self.board]

        # Zugrecht übernehmen
        new_state.to_move = self.to_move

        # Auswahl/Targets leeren (nicht relevant in der Simulation)
        new_state.selected = None
        new_state.legal_targets = set()

        # Zug anwenden
        moving = new_state.piece_at(src)
        new_state.set_piece(src, PLAYER_NONE)
        new_state.set_piece(dst, moving)

        # Spielerwechsel
        new_state.to_move = PLAYER_B if self.to_move == PLAYER_A else PLAYER_A

        return new_state

    # --- Heuristik ---
    def camp_of(self, player):
        return self.camp_A if player == PLAYER_A else self.camp_B

    def target_camp_of(self, player):
        return self.camp_B if player == PLAYER_A else self.camp_A

    def manhattan(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def naive_goal_pos(self, player):
        """Ein fester Zielpunkt (Eckpunkt des Zielcamps) für grobe Distanz."""
        return (self.n - 1, self.n - 1) if player == PLAYER_A else (0, 0)

    def distance_sum_to_goal(self, player):
        """Summe der Manhattan-Distanzen aller Steine zu einem Eckziel.
        Schnell, grob, funktioniert vernünftig als greedy-Heuristik.
        """
        goal = self.naive_goal_pos(player)
        total = 0
        for y in range(self.n):
            for x in range(self.n):
                if self.board[y][x] == player:
                    total += self.manhattan((x, y), goal)
        # Bonus für Steine, die schon im Zielcamp sind (kleiner machen ist besser)
        in_target = sum(1 for (x, y) in self.target_camp_of(player) if self.board[y][x] == player)
        return total - in_target * 0.5  # leichter Anreiz, das Camp zu füllen

class BoardWidget(QtWidgets.QWidget):
    square_clicked = QtCore.pyqtSignal(tuple)   # (x, y)

    def __init__(self, game: GameState, parent=None):
        super().__init__(parent)
        self.game = game
        self.setMinimumSize(520, 520)
        self.setMouseTracking(True)
        self.hover_cell = None
        self.game.state_changed.connect(self.update)

    def sizeHint(self):
        return QtCore.QSize(560, 560)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        cell = self._pos_to_cell(event.pos())
        if cell != self.hover_cell:
            self.hover_cell = cell
            self.update()

    def leaveEvent(self, _):
        self.hover_cell = None
        self.update()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            cell = self._pos_to_cell(event.pos())
            if cell and in_bounds(cell[0], cell[1], self.game.n):
                self.square_clicked.emit(cell)

    def _pos_to_cell(self, pos: QtCore.QPoint):
        n = self.game.n
        w = self.width()
        h = self.height()
        size = min(w, h)
        offx = (w - size) // 2
        offy = (h - size) // 2
        cell = size / n
        x = int((pos.x() - offx) // cell)
        y = int((pos.y() - offy) // cell)
        if 0 <= x < n and 0 <= y < n:
            return (x, y)
        return None

    def paintEvent(self, _):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        n = self.game.n
        w = self.width()
        h = self.height()
        size = min(w, h)
        offx = (w - size) // 2
        offy = (h - size) // 2
        cell = size / n

        painter.fillRect(self.rect(), QtGui.QColor("#2B2B2B"))

        def draw_camp(coords, color):
            brush = QtGui.QBrush(QtGui.QColor(color))
            for (x, y) in coords:
                painter.fillRect(QtCore.QRectF(offx + x*cell, offy + y*cell, cell, cell), brush)

        draw_camp(self.game.camp_A, "#334455")
        draw_camp(self.game.camp_B, "#553333")

        pen_grid = QtGui.QPen(QtGui.QColor("#888"))
        pen_grid.setWidth(1)
        painter.setPen(pen_grid)
        for i in range(n + 1):
            y = int(offy + i * cell)
            painter.drawLine(int(offx), y, int(offx + size), y)
            x = int(offx + i * cell)
            painter.drawLine(x, int(offy), x, int(offy + size))

        if self.game.selected:
            painter.setBrush(QtGui.QColor(70, 160, 90, 140))
            painter.setPen(QtCore.Qt.NoPen)
            for (x, y) in self.game.legal_targets:
                r = QtCore.QRectF(offx + x*cell+cell*0.15, offy + y*cell+cell*0.15, cell*0.7, cell*0.7)
                painter.drawEllipse(r)

        if self.hover_cell and in_bounds(self.hover_cell[0], self.hover_cell[1], n):
            painter.setPen(QtGui.QPen(QtGui.QColor("#DDD")))
            painter.setBrush(QtCore.Qt.NoBrush)
            x, y = self.hover_cell
            painter.drawRect(QtCore.QRectF(offx + x*cell, offy + y*cell, cell, cell))

        if self.game.selected:
            painter.setPen(QtGui.QPen(QtGui.QColor("#FFD54F"), 3))
            sx, sy = self.game.selected
            painter.drawRect(QtCore.QRectF(offx + sx*cell, offy + sy*cell, cell, cell))

        for y in range(n):
            for x in range(n):
                p = self.game.board[y][x]
                if p != PLAYER_NONE:
                    if p == PLAYER_A:
                        color = QtGui.QColor("#4FC3F7")
                        edge = QtGui.QColor("#01579B")
                    else:
                        color = QtGui.QColor("#EF9A9A")
                        edge = QtGui.QColor("#B71C1C")
                    cx = offx + (x + 0.5)*cell
                    cy = offy + (y + 0.5)*cell
                    r = cell * 0.35
                    painter.setBrush(QtGui.QBrush(color))
                    painter.setPen(QtGui.QPen(edge, 2))
                    painter.drawEllipse(QtCore.QPointF(cx, cy), r, r)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Halma – PyQt5 + KI")
        self.game = GameState(n=8, tri_size=4)
        self.board = BoardWidget(self.game)
        self.setCentralWidget(self.board)
        
        self.ai_enabled = False  # Togglebar steuert das
        self.ai_player = PLAYER_B
        
        self.status = self.statusBar()
        self._update_status()

        self.board.square_clicked.connect(self.on_square_clicked)
        self.game.state_changed.connect(self._update_status)
        
        self._make_toolbar()

        self.resize(720, 760)
        self.show()

    def _make_toolbar(self):
        tb = QtWidgets.QToolBar("Aktionen")
        self.addToolBar(tb)

        new_act = QtWidgets.QAction("Neu", self)
        new_act.triggered.connect(self.new_game)
        tb.addAction(new_act)

        swap_act = QtWidgets.QAction("Tausch Seiten", self)
        swap_act.triggered.connect(self.swap_sides)
        tb.addAction(swap_act)

        rules_act = QtWidgets.QAction("Regeln", self)
        rules_act.triggered.connect(self.show_rules)
        tb.addAction(rules_act)

        tb.addSeparator()
        self.ai_act = QtWidgets.QAction("KI an/aus (Rot)", self)
        self.ai_act.setCheckable(True)
        self.ai_act.toggled.connect(self.toggle_ai)
        tb.addAction(self.ai_act)

        step_ai = QtWidgets.QAction("KI-Zug jetzt", self)
        step_ai.triggered.connect(self.ai_make_move)
        tb.addAction(step_ai)

    def new_game(self):
        self.game = GameState(n=8, tri_size=4)
        self.board.game = self.game
        self.game.state_changed.connect(self.board.update)
        self.game.state_changed.connect(self._update_status)
        self.board.update()
        self._update_status()

    def swap_sides(self):
        for y in range(self.game.n):
            for x in range(self.game.n):
                p = self.game.board[y][x]
                if p == PLAYER_A:
                    self.game.board[y][x] = PLAYER_B
                elif p == PLAYER_B:
                    self.game.board[y][x] = PLAYER_A
        self.game.to_move = PLAYER_A
        self.game.reset_selection()

    def show_rules(self):
        QtWidgets.QMessageBox.information(self, "Regeln", (
            "Ziel: Bewege alle deine Steine ins gegenüberliegende Startdreieck.\n\n"
            "Zugarten:\n"
            "• Schritt: 1 Feld in eine der 8 Richtungen auf ein leeres Feld.\n"
            "• Sprung: Über einen benachbarten Stein (egal welche Farbe) auf das direkt dahinter liegende freie Feld.\n"
            "  Sprünge dürfen zu einer Kette kombiniert werden. Klicke dazu direkt das gewünschte Endfeld an –\n"
            "  alle erreichbaren Endfelder einer Sprungkette werden grün markiert.\n\n"
            "Spieler: Blau beginnt. Die optionale KI spielt Rot."
        ))

    def _update_status(self):
        player = "Blau" if self.game.to_move == PLAYER_A else "Rot"
        postfix = " (KI)" if self.ai_enabled and self.game.to_move == self.ai_player else ""
        self.status.showMessage(f"Am Zug: {player}{postfix}")
        if self.game.is_win(PLAYER_A):
            QtWidgets.QMessageBox.information(self, "Spielende", "Blau hat gewonnen!")
            self.new_game()
        elif self.game.is_win(PLAYER_B):
            QtWidgets.QMessageBox.information(self, "Spielende", "Rot hat gewonnen!")
            self.new_game()

    def on_square_clicked(self, cell):
        if self.game.selected is None:
            if self.game.piece_at(cell) == self.game.to_move:
                self.game.try_select(cell)
            else:
                return
        else:
            if self.game.piece_at(cell) == self.game.to_move:
                self.game.try_select(cell)
                return
            moved = self.game.try_move(cell)
            if not moved:
                if self.game.piece_at(cell) != self.game.to_move:
                    self.game.reset_selection()

        # Wenn jetzt die KI dran ist und aktiviert wurde, Zug ausführen
        if self.ai_enabled and self.game.to_move == self.ai_player:
            QtCore.QTimer.singleShot(200, self.ai_make_move)

    def toggle_ai(self, checked):
        self.ai_enabled = checked
        # Wenn gerade die KI-Seite am Zug ist, sofort handeln
        if self.ai_enabled and self.game.to_move == self.ai_player:
            QtCore.QTimer.singleShot(150, self.ai_make_move)

    # ---------------- KI ----------------
    def ai_make_move(self):
        if not (self.ai_enabled and self.game.to_move == self.ai_player):
            return

        # Alle legalen Züge der KI
        moves = self.game.all_moves_for(self.ai_player)
        if not moves:
            # Nichts möglich -> "passe"
            self.game.to_move = PLAYER_A
            self.game.state_changed.emit()
            return

        # Greedy-Auswahl: minimaler Heuristikwert im Nachzustand
        best_score = float('inf')
        best_moves = []
        for (src, dst) in moves:
            # Simulationszustand
            sim = self.game.simulate_after(src, dst)
            score = sim.distance_sum_to_goal(self.ai_player)

            # leichte Bevorzugung von Sprüngen (schneller Fortschritt)
            is_jump = max(abs(dst[0]-src[0]), abs(dst[1]-src[1])) == 2
            if is_jump:
                score -= 0.25

            if score < best_score - 1e-9:
                best_score = score
                best_moves = [(src, dst)]
            elif abs(score - best_score) <= 1e-9:
                best_moves.append((src, dst))

        # deterministische, aber simple Auswahl
        src, dst = sorted(best_moves)[0]

        # Auf dem echten Spiel ausführen (über try_move zur Validierung/Hervorhebung)
        self.game.selected = src
        self.game.legal_targets = self.game.simple_steps(src) | self.game.jump_targets_from(src)
        if dst in self.game.legal_targets:
            self.game.try_move(dst)
        else:
            # Fallback: sollte nicht passieren, aber zur Sicherheit
            self.game.reset_selection()

    # -------------- Ende KI -------------

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
