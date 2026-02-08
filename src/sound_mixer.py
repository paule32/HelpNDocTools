"""
PyQt5 Audio-Mixer (12 Kanäle) – Mixer + Timeline
- 12 Regler (6 oben / 6 unten), Master links (fix 42 px)
- Equalizer (12 x 32 LEDs) mittig zwischen den Reglerreihen
- NEU: Timeline **rechts neben** dem Equalizer (gleiche Reihe), EQ max. 200 px Breite
- Rechte Seitenleiste: Effekt-Schnellauswahl (aus config.json)
- Menüleiste (Datei/Bearbeiten/...)
- Timeline mit 8 Spuren: Clips hinzufügen/verschieben/duplizieren/kopieren/ausschneiden/einfügen/löschen
Hinweis: Audio/DSP ist als TODO vorgesehen – hier geht es um UI/Interaktion.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from PyQt5.QtCore import (
    Qt,
    QTimer,
    QSize,
    QRectF,
)
from PyQt5.QtGui import (
    QColor,
    QPainter,
    QPen,
    QBrush,
)
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSlider,
    QSplitter,
    QToolButton,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QSizePolicy,
)

# -------------------------- Konfiguration & Datenmodell --------------------------

DEFAULT_CONFIG = {
    "ui": {
        "active_color": "#22c55e",  # grün
        "inactive_color": "#334155",  # slate-700
        "separator_color": "#1f2937",  # grau
        "led_on": "#10b981",  # teal/grün
        "led_off": "#0b1220",
    },
    "effects": {
        "list": ["drum", "clap", "tick"],
        "colors": {
            "drum": "#ef4444",
            "clap": "#eab308",
            "tick": "#3b82f6"
        }
    },
    "channels": {
        # Beispiel-Vorbelegung einzelner Kanäle
        # "1": {"envelope": "linear", "effects": ["drum"], "sample": "samples/kick.wav"}
    },
    "envelopes": ["linear", "exponential", "s-curve"]
}

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config(path: str = CONFIG_PATH) -> dict:
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        return DEFAULT_CONFIG.copy()
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg: dict, path: str = CONFIG_PATH) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


@dataclass
class ChannelState:
    index: int
    volume: int = 50  # 0..100
    envelope: str = "linear"
    active_effects: List[str] = field(default_factory=list)
    sample_path: Optional[str] = None


# -------------------------- Equalizer Widget (LED-Matrix) --------------------------

class LEDMatrixEQ(QWidget):
    def __init__(self, columns: int = 12, rows: int = 32, cfg: Optional[dict] = None, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.rows = rows
        self.cfg = cfg or DEFAULT_CONFIG
        self.matrix = [[0.0 for _ in range(rows)] for _ in range(columns)]  # 0..1 Intensität
        self.setMinimumHeight(200)
        self.setMinimumWidth(120)
        self._led_on = QColor(self.cfg["ui"].get("led_on", "#10b981"))
        self._led_off = QColor(self.cfg["ui"].get("led_off", "#0b1220"))
        self._grid_margin = 8
        self._led_spacing = 2

    def sizeHint(self) -> QSize:
        return QSize(200, 240)

    def set_column_levels(self, col: int, levels: List[float]):
        if 0 <= col < self.columns and len(levels) == self.rows:
            self.matrix[col] = [max(0.0, min(1.0, v)) for v in levels]
            self.update()

    def set_full_matrix(self, m: List[List[float]]):
        if len(m) == self.columns and all(len(r) == self.rows for r in m):
            self.matrix = [[max(0.0, min(1.0, v)) for v in col] for col in m]
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width() - 2 * self._grid_margin
        h = self.height() - 2 * self._grid_margin
        col_w = w / self.columns
        row_h = h / self.rows

        for c in range(self.columns):
            for r in range(self.rows):
                x = self._grid_margin + c * col_w + self._led_spacing
                y = self._grid_margin + (self.rows - 1 - r) * row_h + self._led_spacing
                rect = QRectF(x, y, col_w - 2 * self._led_spacing, row_h - 2 * self._led_spacing)
                val = self.matrix[c][r]
                color = QColor(self._led_off)
                if val > 0.02:
                    color = QColor(self._led_on)
                    color.setAlphaF(0.35 + 0.65 * float(val))
                painter.fillRect(rect, QBrush(color))

        pen = QPen(QColor(0, 0, 0, 50))
        pen.setWidthF(1.0)
        painter.setPen(pen)
        rect = QRectF(self.rect())
        rect = rect.adjusted(0.5, 0.5, -0.5, -0.5)
        painter.drawRect(rect)


# -------------------------- Kanal-Widget (Regler + Envelope + Effekte) --------------------------

class ChannelWidget(QWidget):
    def __init__(self, state: ChannelState, cfg: dict, effects: List[str], parent=None):
        super().__init__(parent)
        self.state = state
        self.cfg = cfg
        self.effects = effects
        self.effect_buttons: Dict[str, QToolButton] = {}

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(6)

        title = QLabel(f"CH {state.index:02d}")
        title.setAlignment(Qt.AlignHCenter)
        title.setStyleSheet("font-weight:600; letter-spacing:0.5px;")
        root.addWidget(title)

        self.slider = QSlider(Qt.Vertical)
        self.slider.setRange(0, 100)
        self.slider.setValue(self.state.volume)
        self.slider.setTickPosition(QSlider.TicksBothSides)
        self.slider.setTickInterval(10)
        self.slider.valueChanged.connect(self.on_volume_changed)
        root.addWidget(self.slider, 1)

        self.envelope = QComboBox()
        self.envelope.addItems(self.cfg.get("envelopes", ["linear", "exponential", "s-curve"]))
        if self.state.envelope in [self.envelope.itemText(i) for i in range(self.envelope.count())]:
            self.envelope.setCurrentText(self.state.envelope)
        self.envelope.currentTextChanged.connect(self.on_envelope_changed)
        root.addWidget(self.envelope)

        eff_box = QHBoxLayout()
        eff_box.setSpacing(4)
        for eff in self.effects:
            btn = QToolButton()
            btn.setText(eff)
            btn.setCheckable(True)
            btn.setChecked(eff in self.state.active_effects)
            color = self.cfg["effects"]["colors"].get(eff, "#475569")
            btn.setStyleSheet(self._btn_style(color, btn.isChecked()))
            btn.toggled.connect(lambda checked, e=eff, b=btn: self.on_effect_toggled(e, b, checked))
            btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
            self.effect_buttons[eff] = btn
            eff_box.addWidget(btn)
        root.addLayout(eff_box)

        self.sample_btn = QPushButton("Sample…")
        self.sample_btn.clicked.connect(self.choose_sample)
        root.addWidget(self.sample_btn)

        btn_row = QHBoxLayout()
        self.mute_btn = QToolButton()
        self.mute_btn.setText("Mute")
        self.mute_btn.setCheckable(True)
        self.mute_btn.toggled.connect(self.on_mute)
        btn_row.addWidget(self.mute_btn)

        self.solo_btn = QToolButton()
        self.solo_btn.setText("Solo")
        self.solo_btn.setCheckable(True)
        self.solo_btn.toggled.connect(self.on_solo)
        btn_row.addWidget(self.solo_btn)
        root.addLayout(btn_row)

    def _btn_style(self, base_color: str, active: bool) -> str:
        if active:
            return (
                f"QToolButton{{background:{base_color}; color:white; border:none; padding:4px 8px;"
                f"border-radius:6px; font-weight:600;}}"
            )
        else:
            return (
                "QToolButton{background: #111827; color: #e5e7eb; border: 1px solid #1f2937;"
                "padding:4px 8px; border-radius:6px;}"
                "QToolButton:hover{background:#0b1220;}"
            )

    # --- Slots ---
    def on_volume_changed(self, val: int):
        self.state.volume = val
        # TODO: Audio-Engine: Gain setzen

    def on_envelope_changed(self, text: str):
        self.state.envelope = text
        # TODO: Audio-Engine: Hüllkurve binden

    def on_effect_toggled(self, effect: str, btn: QToolButton, checked: bool):
        color = self.cfg["effects"]["colors"].get(effect, "#475569")
        btn.setStyleSheet(self._btn_style(color, checked))
        if checked and effect not in self.state.active_effects:
            self.state.active_effects.append(effect)
        elif not checked and effect in self.state.active_effects:
            self.state.active_effects.remove(effect)
        # TODO: Audio-Engine: Effekt-Kette aktualisieren

    def choose_sample(self):
        path, _ = QFileDialog.getOpenFileName(self, "Sample auswählen", "", "Audio (*.wav *.mp3 *.flac)")
        if path:
            self.state.sample_path = path
            # TODO: Sample in Player laden

    def on_mute(self, checked: bool):
        pass

    def on_solo(self, checked: bool):
        pass


# -------------------------- Timeline Widget (8 Spuren, Clips bewegbar) --------------------------

@dataclass
class TimelineClip:
    track: int          # 0..7
    start: float        # Sekunden
    duration: float     # Sekunden
    label: str
    color: str = "#3b82f6"
    sample_path: Optional[str] = None

class TimelineWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(260)
        self.tracks = 8
        self.sec_per_pixel = 0.02  # Zoom-Faktor (kleiner = weiter rausgezoomt)
        self.pixels_per_sec = 1.0 / self.sec_per_pixel
        self.max_time = 120.0  # Sekunden
        self.track_height = 26
        self.track_gap = 8
        self.left_margin = 50  # Zeitlineal Beschriftung
        self.top_margin = 24   # Lineal oben
        self.bg_alt = QColor("#0e1624")
        self.bg = QColor("#0b1220")
        self.grid = QColor("#1f2937")
        self.ruler_fg = QColor("#9ca3af")
        self.selection_color = QColor(59, 130, 246, 60)
        self.dragging = False
        self.drag_offset = 0.0
        self.selected: Optional[int] = None
        self.clip_hover: Optional[int] = None
        self.copy_buffer: List[TimelineClip] = []
        self.clips: List[TimelineClip] = []
        self.setMouseTracking(True)

    def time_to_x(self, t: float) -> float:
        return self.left_margin + t * self.pixels_per_sec

    def x_to_time(self, x: float) -> float:
        return max(0.0, (x - self.left_margin) * self.sec_per_pixel)

    def add_clip(self, clip: TimelineClip):
        self.clips.append(clip)
        self.update()

    def set_zoom(self, sec_per_pixel: float):
        self.sec_per_pixel = max(0.002, min(0.2, sec_per_pixel))
        self.pixels_per_sec = 1.0 / self.sec_per_pixel
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        p.fillRect(rect, self.bg)

        for tr in range(self.tracks):
            y = self.top_margin + tr * (self.track_height + self.track_gap)
            h = self.track_height
            if tr % 2 == 1:
                p.fillRect(QRectF(0, y, rect.width(), h), self.bg_alt)

        p.setPen(self.grid)
        for sec in range(int(self.max_time) + 1):
            x = self.time_to_x(sec)
            if x > rect.right():
                break
            p.drawLine(int(x), self.top_margin, int(x), rect.bottom())

        p.setPen(self.ruler_fg)
        p.drawLine(self.left_margin, self.top_margin - 1, rect.right(), self.top_margin - 1)
        for sec in range(int(self.max_time) + 1):
            x = self.time_to_x(sec)
            if x > rect.right():
                break
            p.drawLine(int(x), 0, int(x), self.top_margin - 4)
            if sec % 5 == 0:
                p.drawText(int(x) + 2, 14, f"{sec}s")

        for idx, c in enumerate(self.clips):
            y = self.top_margin + c.track * (self.track_height + self.track_gap) + 2
            x = self.time_to_x(c.start)
            w = max(12, c.duration * self.pixels_per_sec)
            h = self.track_height - 4
            r = QRectF(x, y, w, h)
            col = QColor(c.color)
            p.fillRect(r, col)
            p.setPen(QColor(0, 0, 0, 120))
            p.drawRect(r)
            p.setPen(QColor("white"))
            p.drawText(r.adjusted(4, 0, -4, 0), Qt.AlignVCenter | Qt.AlignLeft, c.label)
            if self.selected == idx:
                p.fillRect(r, self.selection_color)

    def clip_at(self, pos) -> Optional[int]:
        for idx, c in enumerate(self.clips):
            y = self.top_margin + c.track * (self.track_height + self.track_gap) + 2
            x = self.time_to_x(c.start)
            w = max(12, c.duration * self.pixels_per_sec)
            h = self.track_height - 4
            r = QRectF(x, y, w, h)
            if r.contains(pos):
                return idx
        return None

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            idx = self.clip_at(e.pos())
            if idx is not None:
                self.selected = idx
                c = self.clips[idx]
                self.dragging = True
                self.drag_offset = self.x_to_time(e.x()) - c.start
            else:
                self.selected = None
            self.update()
        elif e.button() == Qt.RightButton:
            self._open_context_menu(e)

    def mouseMoveEvent(self, e):
        if self.dragging and self.selected is not None:
            c = self.clips[self.selected]
            new_start = self.x_to_time(e.x()) - self.drag_offset
            c.start = max(0.0, round(new_start, 3))
            self.update()
        else:
            self.clip_hover = self.clip_at(e.pos())

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.dragging = False

    def mouseDoubleClickEvent(self, e):
        track = int(max(0, min(self.tracks - 1, (e.y() - self.top_margin) // (self.track_height + self.track_gap))))
        start = self.x_to_time(e.x())
        self._add_clip_dialog(track, start)

    def _open_context_menu(self, e):
        from PyQt5.QtWidgets import QMenu
        menu = QMenu(self)
        act_add = menu.addAction("Clip hinzufügen…")
        act_dup = menu.addAction("Duplizieren")
        act_cut = menu.addAction("Ausschneiden")
        act_copy = menu.addAction("Kopieren")
        act_paste = menu.addAction("Einfügen")
        act_del = menu.addAction("Löschen")
        chosen = menu.exec_(self.mapToGlobal(e.pos()))
        if chosen == act_add:
            track = int(max(0, min(self.tracks - 1, (e.y() - self.top_margin) // (self.track_height + self.track_gap))))
            start = self.x_to_time(e.x())
            self._add_clip_dialog(track, start)
        elif chosen == act_dup:
            self.duplicate_selected()
        elif chosen == act_cut:
            self.cut_selected()
        elif chosen == act_copy:
            self.copy_selected()
        elif chosen == act_paste:
            self.paste_at(self.x_to_time(e.x()))
        elif chosen == act_del:
            self.delete_selected()

    def _add_clip_dialog(self, track: int, start: float):
        path, _ = QFileDialog.getOpenFileName(self, "Sample wählen", "", "Audio (*.wav *.mp3 *.flac)")
        if path:
            label = os.path.basename(path)
            color = "#22c55e"
            self.add_clip(TimelineClip(track=track, start=start, duration=2.0, label=label, color=color, sample_path=path))

    def copy_selected(self):
        if self.selected is not None:
            c = self.clips[self.selected]
            self.copy_buffer = [TimelineClip(**c.__dict__)]

    def cut_selected(self):
        if self.selected is not None:
            c = self.clips.pop(self.selected)
            self.copy_buffer = [TimelineClip(**c.__dict__)]
            self.selected = None
            self.update()

    def paste_at(self, t: float):
        if not self.copy_buffer:
            return
        base = self.copy_buffer[0]
        pasted = TimelineClip(track=base.track, start=t, duration=base.duration, label=base.label, color=base.color, sample_path=base.sample_path)
        self.clips.append(pasted)
        self.selected = len(self.clips) - 1
        self.update()

    def duplicate_selected(self):
        if self.selected is not None:
            c = self.clips[self.selected]
            dup = TimelineClip(track=c.track, start=c.start + c.duration * 0.1, duration=c.duration, label=c.label, color=c.color, sample_path=c.sample_path)
            self.clips.append(dup)
            self.selected = len(self.clips) - 1
            self.update()

    def delete_selected(self):
        if self.selected is not None:
            self.clips.pop(self.selected)
            self.selected = None
            self.update()


# -------------------------- Hauptfenster --------------------------

class MixerMainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PyQt5 Mixer (12ch)")
        self.resize(1280, 800)
        self.cfg = load_config()

        # --- Menüleiste ---
        menubar = self.menuBar()
        menu_file = menubar.addMenu("&Datei")
        menu_edit = menubar.addMenu("&Bearbeiten")
        menubar.addMenu("&Ansicht")
        menubar.addMenu("&Hilfe")

        act_new = menu_file.addAction("Neu")
        act_open = menu_file.addAction("Öffnen…")
        act_save = menu_file.addAction("Speichern")
        menu_file.addSeparator()
        act_quit = menu_file.addAction("Beenden")
        act_quit.triggered.connect(self.close)

        act_cut = menu_edit.addAction("Ausschneiden")
        act_copy = menu_edit.addAction("Kopieren")
        act_paste = menu_edit.addAction("Einfügen")
        act_dup = menu_edit.addAction("Duplizieren")
        act_del = menu_edit.addAction("Löschen")
        act_unselect = menu_edit.addAction("Auswahl aufheben")
        self._pending_edit_actions = (act_cut, act_copy, act_paste, act_dup, act_del, act_unselect)

        # Kanäle
        self.effects = self.cfg.get("effects", {}).get("list", ["drum", "clap", "tick"])
        self.channels: List[ChannelState] = []
        for i in range(1, 13):
            ch_cfg = self.cfg.get("channels", {}).get(str(i), {})
            self.channels.append(
                ChannelState(
                    index=i,
                    volume=50,
                    envelope=ch_cfg.get("envelope", "linear"),
                    active_effects=list(ch_cfg.get("effects", [])),
                    sample_path=ch_cfg.get("sample"),
                )
            )

        central = QWidget()
        self.setCentralWidget(central)
        root_h = QHBoxLayout(central)
        root_h.setContentsMargins(8, 8, 8, 8)
        root_h.setSpacing(8)

        splitter = QSplitter(Qt.Horizontal)
        root_h.addWidget(splitter)

        # ---- Linke Seite: Master + Regler + EQ|Timeline (nebeneinander) ----
        left_container = QWidget()
        left_h = QHBoxLayout(left_container)
        left_h.setContentsMargins(0, 0, 0, 0)
        left_h.setSpacing(8)

        # Master (fix 42px Breite)
        master_group = QGroupBox("Master")
        master_group.setMaximumWidth(42)
        master_group.setMinimumWidth(42)
        mg_lay = QVBoxLayout(master_group)
        mg_lay.setContentsMargins(6, 12, 6, 12)
        mg_lay.setSpacing(6)
        self.master_slider = QSlider(Qt.Vertical)
        self.master_slider.setRange(0, 100)
        self.master_slider.setValue(80)
        mg_lay.addWidget(self.master_slider)
        left_h.addWidget(master_group)

        # Trennlinie
        sep_left = QFrame(); sep_left.setFrameShape(QFrame.VLine)
        sep_left.setStyleSheet(f"color: {self.cfg['ui'].get('separator_color', '#1f2937')};")
        left_h.addWidget(sep_left)

        mixer_panel = QWidget()
        grid = QGridLayout(mixer_panel)
        grid.setSpacing(8)
        grid.setContentsMargins(8, 8, 8, 8)

        self.channel_widgets: List[ChannelWidget] = []
        # Top row (0..5), bottom row (6..11)
        for idx, ch in enumerate(self.channels):
            col = idx % 6
            row = 0 if idx < 6 else 2
            cw = ChannelWidget(ch, self.cfg, self.effects)
            self.channel_widgets.append(cw)
            grid.addWidget(cw, row, col)

        # Mittlere Zeile: EQ (links, max 200px) | Timeline (rechts, expand)
        mid_row = QWidget()
        mid_h = QHBoxLayout(mid_row)
        mid_h.setContentsMargins(0, 0, 0, 0)
        mid_h.setSpacing(8)

        eq_group = QGroupBox("Equalizer 12 x 32")
        eq_lay = QVBoxLayout(eq_group)
        self.eq = LEDMatrixEQ(columns=12, rows=32, cfg=self.cfg)
        # Maximale Breite auf 200 beschränken
        self.eq.setMaximumWidth(200)
        eq_group.setMaximumWidth(200)
        # SizePolicy: Breite fix/Begrenzung, Höhe expandiert
        eq_group.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.eq.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        eq_lay.addWidget(self.eq)
        mid_h.addWidget(eq_group)

        timeline_group = QGroupBox("Timeline – 8 Spuren")
        tl_v = QVBoxLayout(timeline_group)
        tl_toolbar = QHBoxLayout()
        btn_zoom_out = QToolButton(); btn_zoom_out.setText("-")
        btn_zoom_in  = QToolButton();  btn_zoom_in.setText("+")
        tl_toolbar.addWidget(QLabel("Zoom"))
        tl_toolbar.addWidget(btn_zoom_out)
        tl_toolbar.addWidget(btn_zoom_in)
        tl_toolbar.addStretch(1)
        tl_v.addLayout(tl_toolbar)

        self.timeline = TimelineWidget()
        self.timeline.setMinimumWidth(int(self.timeline.time_to_x(self.timeline.max_time) + 200))
        sa = QScrollArea(); sa.setWidgetResizable(True); sa.setWidget(self.timeline)
        tl_v.addWidget(sa, 1)

        # Timeline expandiert horizontal
        timeline_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mid_h.addWidget(timeline_group, 1)

        grid.addWidget(mid_row, 1, 0, 1, 6)

        left_h.addWidget(mixer_panel, 1)
        splitter.addWidget(left_container)
        splitter.setStretchFactor(0, 3)

        # ---- Rechte Seite: Effekte ----
        right_panel = QWidget()
        right_v = QVBoxLayout(right_panel)
        right_v.setContentsMargins(8, 8, 8, 8)
        right_v.setSpacing(6)

        right_v.addWidget(QLabel("Effekte pro Kanal (Schnellauswahl)"))
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        inner = QWidget(); inner_v = QVBoxLayout(inner); inner_v.setSpacing(6)

        for ch in self.channels:
            roww = QWidget()
            row_h = QHBoxLayout(roww); row_h.setContentsMargins(0, 0, 0, 0); row_h.setSpacing(6)
            row_h.addWidget(QLabel(f"CH {ch.index:02d}"))
            for eff in self.effects:
                btn = QPushButton(eff)
                btn.setCheckable(True)
                btn.setChecked(eff in ch.active_effects)
                color = self.cfg["effects"]["colors"].get(eff, "#475569")
                btn.setStyleSheet(self._pill_btn_style(color, btn.isChecked()))
                btn.toggled.connect(self._make_right_effect_handler(ch.index, eff))
                row_h.addWidget(btn)
            inner_v.addWidget(roww)

        inner_v.addStretch(1)
        scroll.setWidget(inner)
        right_v.addWidget(scroll, 1)

        cfg_row = QHBoxLayout()
        load_btn = QPushButton("Konfig laden"); cfg_row.addWidget(load_btn)
        save_btn = QPushButton("Konfig speichern"); cfg_row.addWidget(save_btn)
        load_btn.clicked.connect(self.reload_config)
        save_btn.clicked.connect(self.persist_config)
        right_v.addLayout(cfg_row)

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(1, 2)

        # Menü „Bearbeiten“ mit Timeline verknüpfen
        act_cut, act_copy, act_paste, act_dup, act_del, act_unselect = self._pending_edit_actions
        act_cut.triggered.connect(self.timeline.cut_selected)
        act_copy.triggered.connect(self.timeline.copy_selected)
        act_paste.triggered.connect(lambda: self.timeline.paste_at(0.0))
        act_dup.triggered.connect(self.timeline.duplicate_selected)
        act_del.triggered.connect(self.timeline.delete_selected)
        act_unselect.triggered.connect(lambda: setattr(self.timeline, 'selected', None) | self.timeline.update())

        # Demo-Animation für EQ
        self.demo_timer = QTimer(self)
        self.demo_timer.setInterval(60)
        self.demo_timer.timeout.connect(self._demo_eq_step)
        self.demo_timer.start()

        self.apply_dark_palette()

    # ----------------- UI Helpers -----------------
    def _pill_btn_style(self, base_color: str, active: bool) -> str:
        if active:
            return (
                f"QPushButton{{background:{base_color}; color:white; border:none; padding:6px 10px;"
                f"border-radius:12px; font-weight:600;}}"
            )
        else:
            return (
                "QPushButton{background: #0b1220; color: #e5e7eb; border: 1px solid #1f2937;"
                "padding:6px 10px; border-radius:12px;}"
                "QPushButton:hover{background:#111827;}"
            )

    def _make_right_effect_handler(self, ch_index: int, effect: str):
        def handler(checked: bool):
            chw = self.channel_widgets[ch_index - 1]
            left_btn = chw.effect_buttons.get(effect)
            if left_btn:
                left_btn.setChecked(checked)
            color = self.cfg["effects"]["colors"].get(effect, "#475569")
            sender = self.sender()
            if isinstance(sender, QPushButton):
                sender.setStyleSheet(self._pill_btn_style(color, checked))
        return handler

    def apply_dark_palette(self):
        self.setStyleSheet(
            """
            QWidget{background:#0b1220; color:#e5e7eb;}
            QGroupBox{border:1px solid #1f2937; border-radius:10px; margin-top:16px;}
            QGroupBox::title{subcontrol-origin: margin; left:10px; padding: 2px 4px;}
            QLabel{color:#e5e7eb;}
            QSlider::groove:vertical{background:#1f2937; width:8px; border-radius:4px;}
            QSlider::handle:vertical{background:#22c55e; height:18px; margin:-4px; border-radius:6px;}
            QSlider::sub-page:vertical{background:#16a34a; border-radius:4px;}
            QFrame{color:#1f2937;}
            QPushButton{font-weight:500;}
            QToolTip{background:#111827; color:#e5e7eb; border:1px solid #1f2937;}
            """
        )

    def _demo_eq_step(self):
        import random
        for c in range(12):
            peak = random.randint(2, 28)
            col = [0.0] * 32
            for r in range(peak):
                val = max(0.0, 1.0 - (r / max(1, peak)))
                col[r] = val
            self.eq.set_column_levels(c, col)

    def reload_config(self):
        try:
            self.cfg = load_config()
            QMessageBox.information(self, "Konfiguration", "config.json neu geladen.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Konfiguration konnte nicht geladen werden: {e}")

    def persist_config(self):
        try:
            ch_cfg: Dict[str, dict] = {}
            for ch in self.channels:
                ch_cfg[str(ch.index)] = {
                    "envelope": ch.envelope,
                    "effects": ch.active_effects,
                    "sample": ch.sample_path,
                }
            self.cfg["channels"] = ch_cfg
            save_config(self.cfg)
            QMessageBox.information(self, "Konfiguration", "config.json gespeichert.")
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Konfiguration konnte nicht gespeichert werden: {e}")

def main():
    import sys
    app = QApplication(sys.argv)
    win = MixerMainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
