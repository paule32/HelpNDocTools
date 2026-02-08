# TCP <-> Serial Bridge mit IP-Auswahl & Caller-ID (PyQt5)
# Voraussetzungen:
#   pip install PyQt5
#
# Start:
#   python tcp_serial_bridge_clip.py
#
# Features:
#   - Bind-IP wählbar (0.0.0.0 / 127.0.0.1 / lokale Interfaces)
#   - TCP-Port frei wählbar, optional mehrere Clients
#   - Raw-Byte-Bridge in beide Richtungen
#   - Caller-ID Parsing (+CLIP / NMBR/NAME/DATE/TIME)
#   - Option: AT+VCID=1 beim Öffnen senden

import sys
import re
from datetime import datetime
from PyQt5.QtCore import Qt, QIODevice, QTimer
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QGridLayout, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QComboBox, QPlainTextEdit, QMessageBox, QSpinBox,
    QCheckBox, QListWidget, QListWidgetItem, QGroupBox, QLineEdit, QPushButton,
    QHBoxLayout
)
from PyQt5.QtNetwork import (
    QTcpServer, QHostAddress, QNetworkInterface, QAbstractSocket
)
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo


class TcpSerialBridgeCLIP(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TCP ↔ Serial Bridge (IP-Auswahl & Caller-ID)")
        self.resize(1000, 680)

        # ---- Devices / State ----
        self.serial = QSerialPort(self)
        self.serial.readyRead.connect(self.on_serial_ready_read)
        self.serial.errorOccurred.connect(self.on_serial_error)

        self.server = QTcpServer(self)
        self.server.newConnection.connect(self.on_new_connection)

        self.clients = []  # Liste verbundener QTcpSocket
        self.line_accu = ""  # Textpuffer für Zeilen vom Modem

        # Letzte Caller-ID
        self.last_number = ""
        self.last_name = ""
        self.last_dt = None

        # ---- UI: Top-Leiste Serial + TCP ----
        self.port_combo = QComboBox()
        self.refresh_ports()

        self.baud_combo = QComboBox()
        for b in [300, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400, 460800]:
            self.baud_combo.addItem(str(b))
        self.baud_combo.setCurrentText("115200")

        self.open_btn = QPushButton("COM öffnen")
        self.open_btn.clicked.connect(self.toggle_serial)

        self.clip_chk = QCheckBox("CLIP beim Öffnen aktivieren (AT+VCID=1)")
        self.clip_chk.setChecked(True)
        self.clip_alt_chk = QCheckBox("Alternative (AT#CID=1) zusätzlich")
        self.clip_alt_chk.setChecked(False)

        self.bind_combo = QComboBox()
        self.populate_bind_addresses()

        self.listen_port = QSpinBox()
        self.listen_port.setRange(1, 65535)
        self.listen_port.setValue(5000)

        self.listen_btn = QPushButton("TCP lauschen")
        self.listen_btn.clicked.connect(self.toggle_listen)

        self.allow_multi_chk = QCheckBox("Mehrere TCP-Clients erlauben")
        self.allow_multi_chk.setChecked(False)

        self.status_lbl_1 = QLabel("Status: Serial geschlossen")
        self.status_lbl_2 = QLabel("TCP stoppt")
        self.status_lbl_3 = QLabel("Clients: 0")
        
        self.status_lbl_1.setStyleSheet("font-weight: 600;")
        self.status_lbl_2.setStyleSheet("font-weight: 600;")
        self.status_lbl_3.setStyleSheet("font-weight: 600;")

        # Layout Top
        top1 = QHBoxLayout()
        top1.addWidget(QLabel("COM:"))
        top1.addWidget(self.port_combo, 1)
        top1.addWidget(QLabel("Baud:"))
        top1.addWidget(self.baud_combo)
        top1.addWidget(self.open_btn)
        top1.addStretch(1)

        top2 = QHBoxLayout()
        top2.addWidget(QLabel("Bind-IP:"))
        top2.addWidget(self.bind_combo, 2)
        top2.addWidget(QLabel("TCP-Port:"))
        top2.addWidget(self.listen_port)
        top2.addStretch(1)

        top3 = QVBoxLayout()
        top3.addWidget(self.listen_btn)
        top3.addWidget(self.allow_multi_chk)
        top3.addWidget(self.clip_chk)
        top3.addWidget(self.clip_alt_chk)
        top3.addStretch(1)
        top3.addWidget(self.status_lbl_1)
        top3.addWidget(self.status_lbl_2)
        top3.addWidget(self.status_lbl_3)

        # ---- Caller-ID Anzeige ----
        cid_group = QGroupBox("Caller-ID")
        self.cid_number_lbl = QLabel("Nummer: –")
        self.cid_name_lbl = QLabel("Name: –")
        self.cid_time_lbl = QLabel("Zeit: –")
        cid_info = QVBoxLayout()
        cid_info.addWidget(self.cid_number_lbl)
        cid_info.addWidget(self.cid_name_lbl)
        cid_info.addWidget(self.cid_time_lbl)
        cid_group.setLayout(cid_info)

        self.cid_history = QListWidget()
        self.cid_history.setSelectionMode(self.cid_history.NoSelection)

        self.clients_list = QListWidget()
        self.clients_list.setSelectionMode(self.clients_list.SingleSelection)

        self.cli_send_edit = QLineEdit()
        self.cli_send_edit.setPlaceholderText("Nachricht an Client(s) – Enter = senden")
        self.cli_send_btn = QPushButton("An Client senden")
        self.cli_send_all_btn = QPushButton("An alle senden")

        hl_cli = QHBoxLayout()
        hl_cli.addWidget(self.cli_send_btn)
        hl_cli.addWidget(self.cli_send_all_btn)

        self.cli_send_edit.returnPressed.connect(self._ui_send_to_selected)
        self.cli_send_btn.clicked.connect(self._ui_send_to_selected)
        self.cli_send_all_btn.clicked.connect(self._ui_send_to_all)

        # ---- Log ----
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setPlaceholderText("Log-Ausgaben erscheinen hier …")

        # ---- Root Layout ----
        root = QWidget()
        grid = QGridLayout(root)
        grid.addLayout(top1,              0, 0, 1, 2)
        grid.addLayout(top2,              1, 0, 1, 2)
        grid.addLayout(top3,              2, 0, 1, 2)
        grid.addWidget(cid_group,         3, 0, 1, 1)
        grid.addWidget(self.cid_history,  3, 1, 1, 1)
        grid.addWidget(self.log,          4, 0, 1, 2)
        grid.setRowStretch(4, 1)
        
        grid.addWidget(self.clients_list,  3, 0, 1, 1)       # links
        grid.addWidget(cid_group,          3, 1, 1, 1)       # rechts
        grid.addWidget(self.cli_send_edit, 4, 0, 1, 2)
        grid.addLayout(hl_cli,             5, 0, 1, 2)
        grid.addWidget(self.log,           6, 0, 1, 2)
        grid.setRowStretch(6, 1)
        
        self.ser_cmd_chk = QCheckBox("Serielle Server-Befehle erlauben (Präfix ##)")
        self.ser_cmd_chk.setChecked(True)
        top3.insertWidget(0, self.ser_cmd_chk)  # z. B. ganz links in der dritten Zeile

        self.setCentralWidget(root)
        self.update_ui()

    # ---------- Helpers / UI ----------
    def log_msg(self, text: str):
        self.log.moveCursor(self.log.textCursor().End)
        self.log.insertPlainText(text + "\n")
        self.log.moveCursor(self.log.textCursor().End)

    def update_ui(self):
        ser_open = self.serial.isOpen()
        listening = self.server.isListening()

        self.open_btn.setText("COM schließen" if ser_open else "COM öffnen")
        self.port_combo.setEnabled(not ser_open)
        self.baud_combo.setEnabled(not ser_open)
        self.clip_chk.setEnabled(not ser_open)
        self.clip_alt_chk.setEnabled(not ser_open)

        self.listen_btn.setText("TCP stoppen" if listening else "TCP lauschen")
        self.bind_combo.setEnabled(not listening)
        self.listen_port.setEnabled(not listening)

        client_count = len(self.clients)
        ser_state = "offen" if ser_open else "geschlossen"
        if listening:
            addr_text = self.bind_combo.currentText()
            tcp_state = f"lauscht auf {addr_text}:{self.listen_port.value()}"
        else:
            tcp_state = "stoppt"

        self.status_lbl_1.setText(f"Status: Serial {ser_state}")
        self.status_lbl_2.setText(f"TCP {tcp_state}")
        self.status_lbl_3.setText(f"Clients: {client_count}")

    def refresh_ports(self):
        self.port_combo.clear()
        for p in QSerialPortInfo.availablePorts():
            label = f"{p.portName()} — {p.description() or 'Serial'}"
            self.port_combo.addItem(label, p.portName())
        if self.port_combo.count() == 0:
            self.port_combo.addItem("(keine Ports gefunden)", "")

    def populate_bind_addresses(self):
        self.bind_combo.clear()
        # Standardoptionen
        self.bind_combo.addItem("Alle Schnittstellen (0.0.0.0)", "0.0.0.0")
        self.bind_combo.addItem("Nur lokal (127.0.0.1)", "127.0.0.1")
        seen = set(["0.0.0.0", "127.0.0.1"])
        # Lokale IPv4-Adressen auflisten
        for iface in QNetworkInterface.allInterfaces():
            if iface.flags() & QNetworkInterface.IsLoopBack:
                pass  # Loopback ist schon drin
            for entry in iface.addressEntries():
                ip = entry.ip()
                if ip.protocol() != QAbstractSocket.IPv4Protocol:
                    continue
                s = ip.toString()
                if s in seen:
                    continue
                seen.add(s)
                name = iface.humanReadableName() or "Interface"
                self.bind_combo.addItem(f"{name} ({s})", s)

    # ---------- Serial ----------
    def toggle_serial(self):
        if self.serial.isOpen():
            self.serial.close()
            self.log_msg("[SER] Port geschlossen.")
            self.update_ui()
            return

        port_name = self.port_combo.currentData()
        if not port_name:
            QMessageBox.warning(self, "Kein COM-Port", "Bitte zuerst einen gültigen COM-Port auswählen.")
            return

        # (Optional) Busy-Check, falls Qt-Build das unterstützt
        try:
            info = next((p for p in QSerialPortInfo.availablePorts() if p.portName() == port_name), None)
            if info and hasattr(info, "isBusy") and info.isBusy():
                self.log_msg(f"[SER] Hinweis: {port_name} meldet busy – vermutlich von einem anderen Prozess geöffnet.")
        except Exception:
            pass

        # Grundeinstellungen
        try:
            baud = int(self.baud_combo.currentText())
        except ValueError:
            baud = 115200

        self.serial.setPortName(port_name)
        self.serial.setBaudRate(baud)
        self.serial.setDataBits(QSerialPort.Data8)
        self.serial.setParity(QSerialPort.NoParity)
        self.serial.setStopBits(QSerialPort.OneStop)
        self.serial.setFlowControl(QSerialPort.NoFlowControl)

        if not self.serial.open(QIODevice.ReadWrite):
            err = self.serial.error()
            err_str = self.serial.errorString()
            QMessageBox.critical(self, "COM-Fehler",
                                 f"Konnte {port_name} nicht öffnen.\n\nFehlercode: {int(err)}\n{err_str}\n\n"
                                 "Tipp: Ist der Port bereits von einem anderen Programm belegt?")
            self.log_msg(f"[SER][OpenError] {port_name}: code={int(err)} msg='{err_str}'")
            return

        self.log_msg(f"[SER] Geöffnet: {port_name} @ {baud}.")

        # CLIP-Setup leicht verzögert (manche Modems mögen eine kurze Pause)
        def _send_clip():
            if not self.serial.isOpen():
                return
            if self.clip_chk.isChecked():
                self._send_serial(b"AT+VCID=1\r")
                self.log_msg("[SER] -> AT+VCID=1")
            if self.clip_alt_chk.isChecked():
                self._send_serial(b"AT#CID=1\r")
                self.log_msg("[SER] -> AT#CID=1")

        QTimer.singleShot(1000, _send_clip)
        self.update_ui()

    def _send_serial(self, data: bytes):
        if self.serial.isOpen():
            self.serial.write(data)
            self.serial.flush()

    def on_serial_error(self, err):
        if err == QSerialPort.NoError:
            return
        self.log_msg(f"[SER][Error] {self.serial.errorString()}")
        if self.serial.isOpen():
            self.serial.close()
        self.update_ui()

    def on_serial_ready_read(self):
        if not self.serial.isOpen():
            return
        data = bytes(self.serial.readAll())

        # Broadcast an TCP-Clients
        for sock in list(self.clients):
            if sock.state() == sock.ConnectedState:
                sock.write(data)
                sock.flush()

        # Text-Puffer zum Parsen (Caller-ID etc.)
        # Modem-Antworten sind typ. ASCII mit CR/LF
        text = data.decode("utf-8", errors="replace")
        self.line_accu += text
        self._parse_lines()

        # Log Preview
        preview = text[:64].replace("\r", "\\r").replace("\n", "\\n")
        more = "…" if len(text) > 64 else ""
        self.log_msg(f"[SER→TCP] {len(data)} B  '{preview}{more}'")

    def _handle_serial_command(self, cmdline: str):
        parts = cmdline.split()
        if not parts:
            return
        cmd = parts[0].upper()

        def write_back(msg: str):
            self._send_serial((msg + "\r\n").encode("utf-8"))

        if cmd == "BCAST":
            payload = cmdline[len("BCAST"):].lstrip()
            count = 0
            for s in self.clients:
                if s.state() == s.ConnectedState:
                    count += s.write(payload.encode("utf-8"))
                    s.flush()
            self.log_msg(f"[SER-CMD] BCAST {len(payload)} B -> {count} B gesendet")
            write_back(f"OK BCAST {len(payload)}B")

        elif cmd == "TO" and len(parts) >= 3:
            try:
                idx = int(parts[1])
                payload = cmdline.split(None, 2)[2]
            except Exception:
                write_back("ERR TO usage: ##TO <idx> <text>")
                return
            if 0 <= idx < len(self.clients) and self.clients[idx].state() == self.clients[idx].ConnectedState:
                n = self.clients[idx].write(payload.encode("utf-8"))
                self.clients[idx].flush()
                self.log_msg(f"[SER-CMD] TO#{idx} {len(payload)} B -> {n} B")
                write_back(f"OK TO {idx} {n}B")
            else:
                write_back(f"ERR TO {idx} not connected")

        elif cmd == "HEX" and len(parts) >= 3:
            # ##HEX <idx> <hexstring>
            idx = int(parts[1]) if parts[1].isdigit() else -1
            hexstr = parts[2]
            try:
                data = bytes.fromhex(hexstr)
            except ValueError:
                write_back("ERR HEX invalid")
                return
            if 0 <= idx < len(self.clients) and self.clients[idx].state() == self.clients[idx].ConnectedState:
                n = self.clients[idx].write(data); self.clients[idx].flush()
                self.log_msg(f"[SER-CMD] HEX#{idx} {len(data)} B")
                write_back(f"OK HEX {idx} {n}B")
            else:
                write_back(f"ERR HEX {idx} not connected")

        elif cmd == "KICK" and len(parts) >= 2:
            idx = int(parts[1]) if parts[1].isdigit() else -1
            if 0 <= idx < len(self.clients):
                try:
                    peer = f"{self.clients[idx].peerAddress().toString()}:{self.clients[idx].peerPort()}"
                    self.clients[idx].close()
                    self.log_msg(f"[SER-CMD] KICK #{idx} ({peer})")
                    write_back(f"OK KICK {idx}")
                except Exception as e:
                    write_back(f"ERR KICK {idx} {e}")
            else:
                write_back(f"ERR KICK {idx} out of range")

        elif cmd == "LIST":
            for i, s in enumerate(self.clients):
                state = "up" if s.state() == s.ConnectedState else "down"
                peer = f"{s.peerAddress().toString()}:{s.peerPort()}"
                write_back(f"CLIENT {i} {state} {peer}")
            write_back("OK LIST")

        else:
            write_back("ERR unknown cmd")

    # --- Zeilen parser ---
    def _parse_lines(self):
        # Aufsplitten in volle Zeilen; Rest stehen lassen
        parts = re.split(r'[\r\n]+', self.line_accu)
        # Wenn die Originalzeichenkette mit CR/LF endete, ist letztes Element leer -> dann keine Restzeile
        if self.line_accu.endswith("\n") or self.line_accu.endswith("\r"):
            lines, rest = parts[:-1], ""
        else:
            lines, rest = parts[:-1], parts[-1]
        self.line_accu = rest

        for raw in lines:
            line = raw.strip()
            if not line:
                continue
            U = line.upper()

            # Statusindikationen (optional)
            if U == "RING":
                # Nächster Caller kann kommen
                self._maybe_append_history_if_new_session()
                continue

            # --- Server-Kommandos vom COM ---
            if self.ser_cmd_chk.isChecked() and line.startswith("##"):
                self._handle_serial_command(line[2:].strip())
                continue
                        
            # +CLIP: "49123...",145,"",0,"",0
            m = re.match(r'^\+CLIP:\s*"([^"]+)"(.*)$', line, flags=re.IGNORECASE)
            if m:
                number = m.group(1).strip()
                name = self._extract_name_from_clip_tail(m.group(2))
                self._set_caller(number, name, datetime.now())
                continue

            # Bellcore/ETSI Key-Value
            m = re.match(r'^\s*(DATE)\s*=\s*(\d+)\s*$', line, flags=re.IGNORECASE)
            if m:
                # nur merken; final wird bei NMBR oder NAME gesetzt
                self._pending_date = m.group(2)
                continue
            m = re.match(r'^\s*(TIME)\s*=\s*(\d+)\s*$', line, flags=re.IGNORECASE)
            if m:
                self._pending_time = m.group(2)
                continue
            m = re.match(r'^\s*(NMBR)\s*=\s*(.+)\s*$', line, flags=re.IGNORECASE)
            if m:
                number = m.group(2).strip()
                ts = self._compose_dt_from_pending()
                self._set_caller(number, self.last_name or "", ts)
                continue
            m = re.match(r'^\s*(NAME)\s*=\s*(.+)\s*$', line, flags=re.IGNORECASE)
            if m:
                name = m.group(2).strip()
                ts = self._compose_dt_from_pending()
                self._set_caller(self.last_number or "", name, ts)
                continue

            # Manche Modems: "CALLER NUMBER: ..." / "CALLER NAME: ..."
            m = re.match(r'^\s*CALLER\s+NUMBER\s*:\s*(.+)\s*$', line, flags=re.IGNORECASE)
            if m:
                self._set_caller(m.group(1).strip(), self.last_name or "", datetime.now())
                continue
            m = re.match(r'^\s*CALLER\s+NAME\s*:\s*(.+)\s*$', line, flags=re.IGNORECASE)
            if m:
                self._set_caller(self.last_number or "", m.group(1).strip(), datetime.now())
                continue

            # Sonstige Zeilen ignorieren

    def _extract_name_from_clip_tail(self, tail: str) -> str:
        # In manchen Implementierungen steht der Name in weiteren Feldern in Anführungszeichen.
        # Wir suchen das nächste "..."-Segment (ohne Gewähr).
        if not tail:
            return ""
        q = re.findall(r'"([^"]+)"', tail)
        if len(q) >= 2:
            # oft: "+CLIP: "num",..., "name", ..."
            return q[1].strip()
        return ""

    def _compose_dt_from_pending(self):
        # Pending DATE/TIME (z. B. DATE=0914, TIME=1203) -> heutiges Jahr
        d = getattr(self, "_pending_date", None)
        t = getattr(self, "_pending_time", None)
        now = datetime.now()
        try:
            if d and t and len(d) in (4, 8) and len(t) in (3, 4):
                # DATE=MMDD oder YYYYMMDD; TIME=HHMM
                if len(d) == 4:
                    month = int(d[:2]); day = int(d[2:])
                    year = now.year
                else:
                    year = int(d[:4]); month = int(d[4:6]); day = int(d[6:8])
                hh = int(t[:-2]); mm = int(t[-2:])
                return datetime(year, month, day, hh, mm)
        except Exception:
            pass
        return now

    def _maybe_append_history_if_new_session(self):
        # Bei neuem RING ggf. vorherigen Eintrag finalisieren (hier: nichts zu tun)
        pass

    def _set_caller(self, number: str, name: str, when: datetime):
        if number:
            self.last_number = number
        if name:
            self.last_name = name
        self.last_dt = when or datetime.now()

        # UI aktualisieren
        self.cid_number_lbl.setText(f"Nummer: {self.last_number or '–'}")
        self.cid_name_lbl.setText(f"Name: {self.last_name or '–'}")
        ts = self.last_dt.strftime("%Y-%m-%d %H:%M")
        self.cid_time_lbl.setText(f"Zeit: {ts}")

        # Verlauf ergänzen (kompakte Zeile)
        item = QListWidgetItem(f"[{ts}] {self.last_number or '–'}  {('— '+self.last_name) if self.last_name else ''}")
        self.cid_history.addItem(item)
        self.cid_history.scrollToBottom()

    def _refresh_clients_list(self):
        self.clients_list.clear()
        for i, s in enumerate(self.clients):
            if s.state() == s.ConnectedState:
                peer = f"{s.peerAddress().toString()}:{s.peerPort()}"
                self.clients_list.addItem(f"#{i}  {peer}")

    def _ui_send_to_selected(self):
        text = self.cli_send_edit.text()
        if not text:
            return
        idx = self.clients_list.currentRow()
        if 0 <= idx < len(self.clients) and self.clients[idx].state() == self.clients[idx].ConnectedState:
            n = self.clients[idx].write(text.encode("utf-8"))
            self.clients[idx].flush()
            self.log_msg(f"[UI→TCP sel] {n} B")
        else:
            self.log_msg("[UI] Kein Client ausgewählt/verbunden.")
        self.cli_send_edit.clear()

    def _ui_send_to_all(self):
        text = self.cli_send_edit.text()
        if not text:
            return
        total = 0
        for s in self.clients:
            if s.state() == s.ConnectedState:
                total += s.write(text.encode("utf-8"))
                s.flush()
        self.log_msg(f"[UI→TCP all] {total} B")
        self.cli_send_edit.clear()

    # ---------- TCP ----------
    def toggle_listen(self):
        if self.server.isListening():
            self._stop_listening()
            return

        ip = self.bind_combo.currentData()
        port = int(self.listen_port.value())
        addr = QHostAddress(ip) if ip not in ("0.0.0.0", "127.0.0.1") else (
            QHostAddress.AnyIPv4 if ip == "0.0.0.0" else QHostAddress.LocalHost)
        if not self.server.listen(addr, port):
            QMessageBox.critical(self, "TCP-Fehler",
                                 f"Konnte {ip}:{port} nicht öffnen: {self.server.errorString()}")
            return
        self.log_msg(f"[TCP] Lauscht auf {ip}:{port}")
        self.update_ui()

    def _stop_listening(self):
        for c in list(self.clients):
            try:
                c.close()
            except Exception:
                pass
        self.clients.clear()
        self.server.close()
        self.log_msg("[TCP] Lauschen gestoppt, Clients getrennt.")
        self.update_ui()

    def on_new_connection(self):
        while self.server.hasPendingConnections():
            sock = self.server.nextPendingConnection()
            if not self.allow_multi_chk.isChecked() and any(
                s.state() == s.ConnectedState for s in self.clients
            ):
                self.log_msg("[TCP] Neuer Client abgewiesen (bereits ein Client verbunden).")
                sock.close()
                continue

            sock.readyRead.connect(lambda s=sock: self.on_socket_ready_read(s))
            sock.disconnected.connect(lambda s=sock: self.on_socket_disconnected(s))
            sock.errorOccurred.connect(lambda _e, s=sock: self.on_socket_error(s))
            self.clients.append(sock)

            peer = f"{sock.peerAddress().toString()}:{sock.peerPort()}"
            self.log_msg(f"[TCP] Client verbunden: {peer}")
        self._refresh_clients_list()
        self.update_ui()

    def on_socket_ready_read(self, sock):
        data = bytes(sock.readAll())
        if self.serial.isOpen():
            n = self.serial.write(data)
            self.serial.flush()
        else:
            n = 0
        preview = data[:64].decode("utf-8", errors="replace").replace("\r", "\\r").replace("\n", "\\n")
        more = "…" if len(data) > 64 else ""
        self.log_msg(f"[TCP→SER] {len(data)} B  '{preview}{more}'  (geschrieben {n} B)")

    def on_socket_disconnected(self, sock):
        peer = f"{sock.peerAddress().toString()}:{sock.peerPort()}"
        self.log_msg(f"[TCP] Client getrennt: {peer}")
        try:
            self.clients.remove(sock)
        except ValueError:
            pass
        sock.deleteLater()
        self._refresh_clients_list()
        self.update_ui()

    def on_socket_error(self, sock):
        self.log_msg(f"[TCP][Error] {sock.errorString()}")

    # ---------- Close Event ----------
    def closeEvent(self, e):
        try:
            self._stop_listening()
            if self.serial.isOpen():
                self.serial.close()
        finally:
            e.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = TcpSerialBridgeCLIP()
    w.show()
    sys.exit(app.exec_())
