import sys
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,
    QGraphicsSimpleTextItem, QMessageBox
)
from PyQt5.QtGui import QBrush, QPen, QColor, QPainter
from PyQt5.QtCore import Qt, QPointF

# -----------------------------
# Spiel-Parameter
# -----------------------------
BOARD_STEPS = 40           # Felder auf dem Rundkurs
HOME_PATH_LEN = 4          # Länge des Zielfelds je Farbe
TOKENS_PER_PLAYER = 4
RADIUS_OUTER = 240
RADIUS_HOME = 120
TOKEN_RADIUS = 12

PLAYER_COLORS = {
    0: QColor(220, 50, 47),   # Rot
    1: QColor(38, 139, 210),  # Blau
    2: QColor(133, 153, 0),   # Grün
    3: QColor(181, 137, 0),   # Gelb
}

PLAYER_NAMES = {
    0: "Rot",
    1: "Blau",
    2: "Grün",
    3: "Gelb",
}

START_INDEX = {0: 0, 1: 10, 2: 20, 3: 30}
SAFE_FIELDS = {0, 10, 20, 30}  # Startfelder sind sichere Felder

# -----------------------------
# Datenmodelle
# -----------------------------
@dataclass
class Token:
    player: int
    index_main: int = -1   # -1 = im Haus (Start), 0..39 = Rundkurs
    index_home: int = -1   # 0..HOME_PATH_LEN-1 = im Zielweg, -1 sonst
    item: Optional[QGraphicsEllipseItem] = None

    def is_in_base(self) -> bool:
        return self.index_main == -1 and self.index_home == -1

    def is_on_main(self) -> bool:
        return self.index_main >= 0 and self.index_home == -1

    def is_in_home(self) -> bool:
        return self.index_home >= 0

@dataclass
class PlayerState:
    pid: int
    tokens: List[Token] = field(default_factory=list)

    def all_home(self) -> bool:
        return all(t.index_home == HOME_PATH_LEN - 1 for t in self.tokens)

# -----------------------------
# Hilfsfunktionen Koordinaten
# -----------------------------

def polar_to_point(radius: float, angle_deg: float) -> QPointF:
    from math import cos, sin, radians
    a = radians(angle_deg)
    return QPointF(radius * cos(a), radius * sin(a))


def board_position_to_point(step: int) -> QPointF:
    # Verteile 40 Felder rund um den Kreis (0° rechts, gegen den Uhrzeigersinn)
    angle_per_step = 360.0 / BOARD_STEPS
    angle = -step * angle_per_step
    return polar_to_point(RADIUS_OUTER, angle)


def base_spots(pid: int) -> List[QPointF]:
    # Vier Parkplätze in der Ecke jeder Farbe
    base_angles = {
        0: 45,
        1: 135,
        2: 225,
        3: 315,
    }
    center = polar_to_point(RADIUS_OUTER + 70, -base_angles[pid])
    offs = [QPointF(-20, -20), QPointF(20, -20), QPointF(-20, 20), QPointF(20, 20)]
    return [center + o for o in offs]


def home_position_to_point(pid: int, idx: int) -> QPointF:
    # Ziellinie verläuft von Startfeld Richtung Zentrum
    start_step = START_INDEX[pid]
    start_pt = board_position_to_point(start_step)
    center = QPointF(0, 0)
    # linear interpolieren zwischen Startfeld und Zentrum
    t = (idx + 1) / (HOME_PATH_LEN + 1)
    return start_pt * (1 - t) + center * t

# -----------------------------
# Spiellogik
# -----------------------------
class Game:
    def __init__(self, num_players: int = 4):
        self.num_players = num_players
        self.players: List[PlayerState] = [PlayerState(pid=i) for i in range(num_players)]
        for p in self.players:
            p.tokens = [Token(player=p.pid) for _ in range(TOKENS_PER_PLAYER)]
        self.current_player = 0
        self.die: Optional[int] = None
        self.extra_turn = False

    def reset_die(self):
        self.die = None
        self.extra_turn = False

    def roll_die(self) -> int:
        self.die = random.randint(1, 6)
        return self.die

    def start_square(self, pid: int) -> int:
        return START_INDEX[pid]

    def entry_square(self, pid: int) -> int:
        return self.start_square(pid)

    def main_to_player_relative(self, pid: int, main_idx: int) -> int:
        # Distanz vom Startfeld dieses Spielers entlang des Rundkurses
        if main_idx < 0:
            return -1
        s = self.start_square(pid)
        d = (main_idx - s) % BOARD_STEPS
        return d

    def player_relative_to_main(self, pid: int, rel: int) -> int:
        return (self.start_square(pid) + rel) % BOARD_STEPS

    def can_enter_home(self, token: Token, steps: int) -> Tuple[bool, int]:
        # Prüfe, ob Figur mit 'steps' in den Zielweg einbiegt
        rel = self.main_to_player_relative(token.player, token.index_main)
        if rel == -1:
            return False, -1
        target_rel = rel + steps
        if target_rel <= BOARD_STEPS:
            # Nur wenn wir exakt über START_INDEX + 40 hinaus in den Zielweg kommen
            if target_rel > BOARD_STEPS:
                return False, -1
            if target_rel == BOARD_STEPS:
                # genau auf Ziellinien-Eingang -> home index 0
                return True, 0
            return False, -1
        return False, -1

    def occupied_on_main(self) -> Dict[int, List[Token]]:
        occ: Dict[int, List[Token]] = {}
        for p in self.players:
            for t in p.tokens:
                if t.is_on_main():
                    occ.setdefault(t.index_main, []).append(t)
        return occ

    def token_at_main(self, idx: int) -> List[Token]:
        return self.occupied_on_main().get(idx, [])

    def is_safe(self, idx: int) -> bool:
        return idx in SAFE_FIELDS

    def valid_moves(self, pid: int, die: int) -> List[Tuple[Token, str, int]]:
        moves: List[Tuple[Token, str, int]] = []
        ps = self.players[pid]
        # 1) Aus dem Haus ziehen (nur bei 6)
        if die == 6:
            for t in ps.tokens:
                if t.is_in_base():
                    entry = self.entry_square(pid)
                    blockers = self.token_at_main(entry)
                    if not blockers or (len(blockers) == 1 and blockers[0].player == pid):
                        moves.append((t, "enter", entry))
        # 2) Auf dem Rundkurs bewegen
        for t in ps.tokens:
            if t.is_on_main():
                rel = self.main_to_player_relative(pid, t.index_main)
                target_rel = rel + die
                # Einbiegen ins Ziel genau auf BOARD_STEPS
                if target_rel == BOARD_STEPS:
                    moves.append((t, "to_home", 0))
                elif target_rel < BOARD_STEPS:
                    target_main = self.player_relative_to_main(pid, target_rel)
                    blockers = self.token_at_main(target_main)
                    # Eigene Blockade von 2+ gleichen Figuren verhindern
                    if not (len(blockers) >= 1 and blockers[0].player == pid and len(blockers) >= 2):
                        moves.append((t, "move", target_main))
        # 3) Im Ziel bewegen
        for t in ps.tokens:
            if t.is_in_home():
                target = t.index_home + die
                if target < HOME_PATH_LEN:
                    moves.append((t, "home", target))
        return moves

    def apply_move(self, token: Token, kind: str, target: int) -> Tuple[bool, Optional[Token]]:
        # Rückgabe: (extra_turn, geschlagener_Gegner)
        beaten: Optional[Token] = None
        if kind == "enter":
            token.index_main = target
            self.extra_turn = True  # 6 -> Extra-Zug
            blockers = self.token_at_main(target)
            for b in blockers:
                if b is not token and b.player != token.player and not self.is_safe(target):
                    # schlagen
                    b.index_main = -1
                    b.index_home = -1
                    beaten = b
        elif kind == "move":
            blockers = self.token_at_main(target)
            token.index_main = target
            for b in blockers:
                if b is not token and b.player != token.player and not self.is_safe(target):
                    b.index_main = -1
                    b.index_home = -1
                    beaten = b
            self.extra_turn = (self.die == 6)
        elif kind == "to_home":
            token.index_main = -1
            token.index_home = 0
            self.extra_turn = (self.die == 6)
        elif kind == "home":
            token.index_home = target
            self.extra_turn = (self.die == 6)
        else:
            self.extra_turn = False
        return self.extra_turn, beaten

    def next_player(self):
        if not self.extra_turn:
            self.current_player = (self.current_player + 1) % self.num_players
        self.reset_die()

# -----------------------------
# Rendering / UI
# -----------------------------
class TokenItem(QGraphicsEllipseItem):
    def __init__(self, token: Token, color: QColor):
        super().__init__(-TOKEN_RADIUS, -TOKEN_RADIUS, TOKEN_RADIUS*2, TOKEN_RADIUS*2)
        self.setBrush(QBrush(color))
        self.setPen(QPen(Qt.black, 1))
        self.setZValue(2)
        self.token = token
        self.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)
        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        self.setPen(QPen(Qt.white, 2))
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.setPen(QPen(Qt.black, 1))
        super().hoverLeaveEvent(event)


class BoardView(QGraphicsView):
    def __init__(self, game: Game, move_callback):
        super().__init__()
        self.setRenderHint(QPainter.Antialiasing)
        self.scene = QGraphicsScene(-350, -350, 700, 700)
        self.setScene(self.scene)
        self.game = game
        self.move_callback = move_callback
        self.field_items: Dict[int, QGraphicsEllipseItem] = {}
        self.info_labels: List[QGraphicsSimpleTextItem] = []
        self.highlighted: List[QGraphicsEllipseItem] = []
        self.draw_board()
        self.place_tokens()

    def draw_board(self):
        # Hintergrund
        self.scene.addRect(-320, -320, 640, 640, QPen(Qt.NoPen), QBrush(QColor(245, 245, 245)))
        # Rundkurs-Felder
        for i in range(BOARD_STEPS):
            p = board_position_to_point(i)
            r = 16
            item = self.scene.addEllipse(p.x()-r, p.y()-r, 2*r, 2*r, QPen(Qt.black, 1), QBrush(Qt.white))
            if i in SAFE_FIELDS:
                # sichere Felder farbig markieren
                col = PLAYER_COLORS[(i // 10) % 4]
                item.setBrush(QBrush(col.lighter(150)))
            self.field_items[i] = item
        # Homes
        for pid in range(self.game.num_players):
            for j in range(HOME_PATH_LEN):
                hp = home_position_to_point(pid, j)
                r = 14
                self.scene.addEllipse(hp.x()-r, hp.y()-r, 2*r, 2*r, QPen(Qt.black, 1), QBrush(PLAYER_COLORS[pid].lighter(160)))
        # Bases
        for pid in range(self.game.num_players):
            for bp in base_spots(pid):
                r = 14
                self.scene.addEllipse(bp.x()-r, bp.y()-r, 2*r, 2*r, QPen(Qt.black, 1), QBrush(PLAYER_COLORS[pid].lighter(180)))
        # Zentrum + Label
        c = self.scene.addEllipse(-40, -40, 80, 80, QPen(Qt.black, 1), QBrush(Qt.white))
        txt = self.scene.addSimpleText("MÄDN")
        txt.setPos(-22, -10)
        txt.setZValue(1)

    def place_tokens(self):
        # Alle Figuren positionieren (je nach Status)
        for p in self.game.players:
            spots = base_spots(p.pid)
            for idx, t in enumerate(p.tokens):
                if t.item is None:
                    itm = TokenItem(t, PLAYER_COLORS[p.pid])
                    t.item = itm
                    self.scene.addItem(itm)
                    itm.mousePressEvent = self._make_click_handler(t)
                if t.is_in_base():
                    pos = spots[idx]
                elif t.is_on_main():
                    pos = board_position_to_point(t.index_main)
                else:  # home
                    pos = home_position_to_point(t.player, t.index_home)
                # leicht versetzen, wenn mehrere auf demselben Feld
                pos = self._offset_for_stack(pos, t)
                t.item.setPos(pos)

    def _offset_for_stack(self, pos: QPointF, token: Token) -> QPointF:
        # Schätze Stack-Größe auf diesem Feld
        stack = []
        if token.is_on_main():
            stack = [t for p in self.game.players for t in p.tokens if t.is_on_main() and t.index_main == token.index_main]
        return pos + QPointF(0, -6 * (stack.index(token) if token in stack else 0))

    def _make_click_handler(self, token: Token):
        def handler(event):
            self.move_callback(token)
            event.accept()
        return handler

    def clear_highlights(self):
        for it in self.highlighted:
            it.setPen(QPen(Qt.black, 1))
        self.highlighted.clear()

    def highlight_tokens(self, tokens: List[Token]):
        self.clear_highlights()
        for t in tokens:
            if t.item:
                t.item.setPen(QPen(QColor(255, 255, 255), 3))
                self.highlighted.append(t.item)

    def refresh(self):
        self.place_tokens()

# -----------------------------
# Hauptfenster
# -----------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mensch ärgere dich nicht – PyQt5")
        self.game = Game(num_players=4)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)

        # Board
        self.board_view = BoardView(self.game, self.on_token_clicked)
        root.addWidget(self.board_view, 3)

        # Sidebar
        side = QVBoxLayout()
        root.addLayout(side, 1)

        self.lbl_turn = QLabel()
        self.lbl_die = QLabel("Würfel: –")
        self.btn_roll = QPushButton("Würfeln")
        self.btn_roll.clicked.connect(self.on_roll)

        side.addWidget(self.lbl_turn)
        side.addWidget(self.lbl_die)
        side.addWidget(self.btn_roll)
        side.addStretch(1)

        self.update_turn_label()
        self.resize(980, 720)

        # Initial zeichnen
        self.board_view.refresh()

    # ---- UI Helpers ----
    def update_turn_label(self):
        pid = self.game.current_player
        self.lbl_turn.setText(f"Am Zug: {PLAYER_NAMES[pid]}")
        col = PLAYER_COLORS[pid]
        self.lbl_turn.setStyleSheet(f"font-weight: bold; color: rgb({col.red()}, {col.green()}, {col.blue()});")

    def on_roll(self):
        if self.game.die is not None:
            return
        d = self.game.roll_die()
        self.lbl_die.setText(f"Würfel: {d}")
        moves = self.game.valid_moves(self.game.current_player, d)
        if not moves:
            # Keine Züge -> Nächster Spieler
            QMessageBox.information(self, "Kein Zug", "Keine gültigen Züge. Zug wird übersprungen.")
            self.game.next_player()
            self.lbl_die.setText("Würfel: –")
            self.update_turn_label()
            return
        # Falls nur eine Option existiert, automatisch ziehen
        # Eindeutig nach Objektidentität (Token ist nicht hashbar)
        seen_ids = set()
        tokens_with_moves = []
        for t, _, _ in moves:
            if id(t) not in seen_ids:
                seen_ids.add(id(t))
                tokens_with_moves.append(t)
        self.board_view.highlight_tokens(tokens_with_moves)
        if len(tokens_with_moves) == 1:
            self.apply_best_for_token(tokens_with_moves[0], moves)

    def token_moves(self, token: Token) -> List[Tuple[Token, str, int]]:
        return [m for m in self.game.valid_moves(self.game.current_player, self.game.die or 0) if m[0] is token]

    def apply_best_for_token(self, token: Token, all_moves: Optional[List[Tuple[Token, str, int]]] = None):
        if all_moves is None:
            all_moves = self.game.valid_moves(self.game.current_player, self.game.die or 0)
        options = [m for m in all_moves if m[0] is token]
        if not options:
            return
        # Simple Heuristik: priorisiere Schlagen > ins Ziel > aus dem Haus > normal
        def score(m):
            kind = m[1]
            if kind == "move":
                target = m[2]
                enemy_here = [t for t in self.game.players for t in t.tokens if t.is_on_main() and t.index_main == target and t.player != token.player]
                return 3 if enemy_here else 1
            return {"to_home": 4, "enter": 2, "home": 2}.get(kind, 0)
        best = max(options, key=score)
        self.execute_move(best)

    def on_token_clicked(self, token: Token):
        if self.game.die is None:
            return
        if token.player != self.game.current_player:
            return
        moves = self.token_moves(token)
        if not moves:
            return
        if len(moves) == 1:
            self.execute_move(moves[0])
        else:
            # Bei mehreren Optionen nimm unsere Heuristik
            self.apply_best_for_token(token, all_moves=self.game.valid_moves(self.game.current_player, self.game.die or 0))

    def execute_move(self, move: Tuple[Token, str, int]):
        token, kind, target = move
        extra, beaten = self.game.apply_move(token, kind, target)
        self.board_view.clear_highlights()
        self.board_view.refresh()

        # Sieg prüfen
        if self.game.players[token.player].all_home():
            QMessageBox.information(self, "Spielende", f"{PLAYER_NAMES[token.player]} hat gewonnen!")
            self.close()
            return

        # Nächster
        self.game.next_player()
        self.lbl_die.setText("Würfel: –")
        self.update_turn_label()

# -----------------------------
# main
# -----------------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
