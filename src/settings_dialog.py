# settings_dialog.py
from PyQt5 import QtWidgets, QtCore
import os
from settings import Settings

class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.settings = settings
        self._build_ui()
        self._load_values()

    def _build_ui(self):
        form = QtWidgets.QFormLayout()

        # Felder
        self.ed_c1541 = QtWidgets.QLineEdit()
        self.btn_c1541 = QtWidgets.QPushButton("Durchsuchen…")
        self.btn_c1541.clicked.connect(self._choose_c1541)
        row1 = self._row(self.ed_c1541, self.btn_c1541)
        form.addRow("c1541:", row1)

        self.ed_x64sc = QtWidgets.QLineEdit()
        self.btn_x64sc = QtWidgets.QPushButton("Durchsuchen…")
        self.btn_x64sc.clicked.connect(self._choose_x64sc)
        row2 = self._row(self.ed_x64sc, self.btn_x64sc)
        form.addRow("x64sc:", row2)

        self.ed_build = QtWidgets.QLineEdit()
        self.btn_build = QtWidgets.QPushButton("Durchsuchen…")
        self.btn_build.clicked.connect(self._choose_build_dir)
        row3 = self._row(self.ed_build, self.btn_build)
        form.addRow("Build-Ordner:", row3)

        self.ed_disk_name = QtWidgets.QLineEdit()
        form.addRow("Disk-Name:", self.ed_disk_name)

        self.ed_prg_name = QtWidgets.QLineEdit()
        form.addRow("PRG-Name (Directory):", self.ed_prg_name)

        self.ed_prg_file = QtWidgets.QLineEdit()
        form.addRow("PRG-Datei (Dateiname):", self.ed_prg_file)

        self.ed_d64_file = QtWidgets.QLineEdit()
        form.addRow("D64-Datei (Dateiname):", self.ed_d64_file)

        # Buttons
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self._accept)
        btn_box.rejected.connect(self.reject)

        lay = QtWidgets.QVBoxLayout(self)
        lay.addLayout(form)
        lay.addWidget(btn_box)

    def _row(self, widget, btn):
        w = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(w)
        h.setContentsMargins(0,0,0,0)
        h.addWidget(widget)
        h.addWidget(btn)
        return w

    def _load_values(self):
        d = self.settings.data
        self.ed_c1541.setText(d["paths"]["c1541"])
        self.ed_x64sc.setText(d["paths"]["x64sc"])
        self.ed_build.setText(d["output"]["build_dir"])
        self.ed_disk_name.setText(d["output"]["disk_name"])
        self.ed_prg_name.setText(d["output"]["prg_name"])
        self.ed_prg_file.setText(d["output"]["prg_file"])
        self.ed_d64_file.setText(d["output"]["d64_file"])

    # --- Browser ---
    def _choose_c1541(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "c1541 auswählen", "", "Programme (*)")
        if path: self.ed_c1541.setText(path)

    def _choose_x64sc(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "x64sc auswählen", "", "Programme (*)")
        if path: self.ed_x64sc.setText(path)

    def _choose_build_dir(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Build-Ordner wählen", "")
        if path: self.ed_build.setText(path)

    # --- Validierung & Speichern ---
    def _accept(self):
        c1541 = self.ed_c1541.text().strip()
        x64sc = self.ed_x64sc.text().strip()
        build = self.ed_build.text().strip()

        errors = []
        if not (c1541 and os.path.isfile(c1541)): errors.append("c1541: Datei nicht gefunden.")
        if not (x64sc and os.path.isfile(x64sc)): errors.append("x64sc: Datei nicht gefunden.")
        if not build: errors.append("Build-Ordner: darf nicht leer sein.")
        if build and not os.path.isdir(build):
            try:
                os.makedirs(build, exist_ok=True)
            except Exception as e:
                errors.append(f"Build-Ordner: {e}")

        if errors:
            QtWidgets.QMessageBox.warning(self, "Eingabefehler", "\n".join(errors))
            return

        d = self.settings.data
        d["paths"]["c1541"] = c1541
        d["paths"]["x64sc"] = x64sc
        d["output"]["build_dir"] = build
        d["output"]["disk_name"] = self.ed_disk_name.text().strip() or d["output"]["disk_name"]
        d["output"]["prg_name"] = self.ed_prg_name.text().strip() or d["output"]["prg_name"]
        d["output"]["prg_file"] = self.ed_prg_file.text().strip() or d["output"]["prg_file"]
        d["output"]["d64_file"] = self.ed_d64_file.text().strip() or d["output"]["d64_file"]

        self.settings.save()
        self.accept()
