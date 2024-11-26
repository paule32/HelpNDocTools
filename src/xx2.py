from PyQt5.QtCore import QCoreApplication, QIODevice, QThread, pyqtSignal
from PyQt5.QtNetwork import QTcpServer, QSslSocket, QSslKey, QSslCertificate, QHostAddress
from PyQt5.QtWidgets import QApplication, QMainWindow, QMdiArea, QTextEdit, QAction
import sys
import ssl
from PyQt5.QtNetwork import QSsl

class ClientHandlerThread(QThread):
    new_data = pyqtSignal(QSslSocket, str)
    client_disconnected = pyqtSignal(QSslSocket)

    def __init__(self, client_socket):
        super().__init__()
        self.client_socket = client_socket
        self.client_socket.readyRead.connect(self.read_data)
        self.client_socket.disconnected.connect(lambda: self.handle_disconnection(self.client_socket))

    def read_data(self):
        try:
            if self.client_socket.state() == QSslSocket.ConnectedState:
                if self.client_socket.bytesAvailable() > 0:
                    data = self.client_socket.readAll().data().decode()
                    self.new_data.emit(self.client_socket, data)
                else:
                    print("Keine Daten verfügbar, schließe die Verbindung.")
                    self.client_socket.disconnectFromHost()
        except Exception as e:
            print(f"Fehler beim Lesen der Daten: {e}")

    def handle_disconnection(self):
        self.client_disconnected.emit(self.client_socket)

class NonBlockingSSLServer(QMainWindow):
    def handle_window_closure(self, sub_window, event):
        # Entferne die Verbindung, wenn das Verbindungsfenster geschlossen wird
        client_socket = sub_window.client_socket
        if client_socket:
            self.remove_connection(client_socket)
        event.accept()

    def remove_connection(self, client_socket):
        try:
            # Entferne die Verbindung aus der Liste
            client_address = client_socket.peerAddress().toString()
            client_port = client_socket.peerPort()
            
            # Finde die richtige Verbindung und entferne sie
            for key in list(self.connections.keys()):
                if key[0] == client_address and self.connections[key] == client_socket:
                    print(f"Verbindung von {client_address} wurde getrennt.")
                    del self.connections[key]
                    break
            
            # Entferne den zugehörigen Thread aus der Thread-Liste
            for thread in self.threads:
                if thread.client_socket == client_socket:
                    self.threads.remove(thread)
                    thread.quit()
                    thread.wait()
                    break
            
            client_socket.deleteLater()
            client_socket.sub_window_ref = None
            client_socket.disconnectFromHost()
            print("Client-Socket erfolgreich gelöscht und der Server bleibt in Betrieb.")
            self.statusBar().showMessage("Verbindung geschlossen. Warte auf neue Verbindungen...")
        except Exception as e:
            print(f"Fehler beim Verarbeiten der Trennung: {e}")
    
    def __init__(self, port=1234, cert_file='./ssl/server.crt', key_file='./ssl/server.key'):
        super().__init__()
        self.init_ui()
        
        # Erstelle einen TCP Server
        self.server = QTcpServer()
        self.server.listen(QHostAddress.Any, port)
        self.server.newConnection.connect(self.handle_new_connection)
        
        # SSL Konfiguration
        certificates = QSslCertificate.fromPath(cert_file)
        if not certificates:
            raise FileNotFoundError(f"Das Zertifikat '{cert_file}' wurde nicht gefunden oder ist ungültig.")
        self.cert = certificates[0]
        try:
            with open(key_file, "rb") as key_file:
                            key = QSslKey(key_file.read(), QSsl.KeyAlgorithm.Rsa, QSsl.EncodingFormat.Pem, QSsl.PrivateKey)
        except FileNotFoundError:
            raise FileNotFoundError(f"Der private Schlüssel '{key_file}' wurde nicht gefunden oder ist ungültig.")
        self.key = key
        
        # Speichert die Verbindungen nach Adresse und Port
        self.connections = {}
        self.threads = []
        
        print(f"SSL-Server gestartet. Lauscht auf Port {port}...")

    def init_ui(self):
        self.setWindowTitle("MDI SSL Server")
        self.setGeometry(100, 100, 800, 600)
        
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        
        self.statusBar().showMessage("Server bereit...")
        
        # Menü und Aktionen
        menubar = self.menuBar()
        file_menu = menubar.addMenu("&Datei")
        exit_action = QAction("Beenden", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def handle_new_connection(self):
        # Hole den eingehenden Socket
        client_socket = self.server.nextPendingConnection()
        if isinstance(client_socket, QSslSocket):
            client_socket.setPrivateKey(self.key)
            client_socket.setLocalCertificate(self.cert)
            client_socket.startServerEncryption()
            
        client_address = client_socket.peerAddress().toString()
        client_port = client_socket.peerPort()
        
        # Überprüfen, ob eine Verbindung von derselben Adresse bereits existiert
        if client_address in self.connections:
            print(f"Vorhandene Verbindung von {client_address} erkannt. Öffne virtuellen Port.")
            virtual_port = client_port + 1  # Öffne einen virtuellen Port
            self.connections[(client_address, virtual_port)] = client_socket
        else:
            # Speichere die neue Verbindung
            self.connections[(client_address, client_port)] = client_socket
        
        # Neues MDI-Fenster für die Verbindung
        sub_window = QTextEdit()
        sub_window.setWindowTitle(f"Verbindung von {client_address}:{client_port}")
        self.mdi_area.addSubWindow(sub_window)
        sub_window.show()
        client_socket.sub_window_ref = sub_window
        sub_window.client_socket = client_socket
        sub_window.closeEvent = lambda event: self.handle_window_closure(sub_window, event)
        
        client_socket.text_edit = sub_window  # Verknüpfen Sie das Textfeld mit dem Socket

        # Erstelle und starte einen neuen Thread zur Bearbeitung des Clients
        thread = ClientHandlerThread(client_socket)
        thread.new_data.connect(self.display_data)
        thread.client_disconnected.connect(self.handle_disconnection)
        thread.start()
        self.threads.append(thread)

    def display_data(self, client_socket, data):
        try:
            # Überprüfe, ob das Fenster existiert und nicht gelöscht wurde
            if client_socket.sub_window_ref is None or not isinstance(client_socket.sub_window_ref, QTextEdit) or client_socket.sub_window_ref.isHidden():
                # Fenster wurde gelöscht, erstelle es neu
                sub_window = QTextEdit()
                sub_window.setWindowTitle(f"Verbindung von {client_socket.peerAddress().toString()}:{client_socket.peerPort()}")
                self.mdi_area.addSubWindow(sub_window)
                sub_window.show()
                client_socket.sub_window_ref = sub_window
                print("Neues Verbindungsfenster erstellt.")
            
            print(f"Empfangene Daten: {data}")
            
            # Ausgabe im MDI-Fenster
            client_socket.sub_window_ref.append(f"Empfangen: {data}")
            
            # Sende eine Antwort zurück
            response = f"Server: Deine Nachricht war '{data}'"
            client_socket.write(response.encode())
            client_socket.flush()
            client_socket.sub_window_ref.append(f"Gesendet: {response}")
        except Exception as e:
            print(f"Fehler beim Verarbeiten der Daten: {e}")

    def handle_disconnection(self, client_socket):
        self.remove_connection(client_socket)

    def run(self):
        # Starte die Qt Event Schleife
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    server = NonBlockingSSLServer(port=1234)
    server.run()
    sys.exit(app.exec_())
