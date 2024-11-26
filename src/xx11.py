from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 450, 400)
        self.setStyleSheet("""
            background: qlineargradient(
                x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #000080,
                stop: 1 #000000
            );
            border: 4px solid red;
            border-radius: 8px;
        """)

        # Hauptlayout des Dialogs
        layout = QVBoxLayout()

        # Titel: Login
        self.title_label = QLabel("Login")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.title_label.setStyleSheet("color: #ffffff;")
        self.title_label.setMaximumHeight(100)
        layout.addWidget(self.title_label)

        # ComboBox zur Auswahl
        self.combo_box = QComboBox()
        self.combo_box.addItems(["Option 1", "Option 2", "Option 3"])
        self.combo_box.setStyleSheet("""
            background-color: #fff;
            padding: 6px;
            font-size: 14px;
            line-height: 20px;
            border: 2px solid #ffffff;
            border-radius: 4px;
            margin: 8px 0;
            font-family: monospace;
        """)
        layout.addWidget(self.combo_box)

        # Eingabefeld unter der ComboBox
        self.additional_field = QLineEdit()
        self.additional_field.setPlaceholderText("Doppelklicken für weiteren Dialog")
        self.additional_field.setStyleSheet("""
            background-color: #fff;
            padding: 6px;
            font-size: 14px;
            line-height: 20px;
            border: 2px solid #ffffff;
            border-radius: 4px;
            margin: 8px 0;
            font-family: monospace;
        """)
        self.additional_field.mouseDoubleClickEvent = self.open_additional_dialog
        layout.addWidget(self.additional_field)

        # Eingabe für Benutzername
        self.username_field = QLineEdit()
        self.username_field.setPlaceholderText("Benutzername eingeben")
        self.username_field.setStyleSheet("""
            background-color: #fff;
            padding: 6px;
            font-size: 14px;
            line-height: 20px;
            border: 2px solid #ffffff;
            border-radius: 4px;
            margin: 8px 0;
            font-family: monospace;
        """)
        layout.addWidget(self.username_field)

        # Eingabe für Passwort
        self.password_field = QLineEdit()
        self.password_field.setPlaceholderText("Passwort eingeben")
        self.password_field.setEchoMode(QLineEdit.Password)
        self.password_field.setStyleSheet("""
            background-color: #fff;
            padding: 6px;
            font-size: 14px;
            line-height: 20px;
            border: 2px solid #ffffff;
            border-radius: 4px;
            margin: 8px 0;
            font-family: monospace;
        """)
        layout.addWidget(self.password_field)

        # Login-Button
        self.login_button = QPushButton("Login into the System")
        self.login_button.setStyleSheet("""
            padding: 8px;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #243949, stop: 1 #517fa4);
            color: #ffffff;
            font-size: 14px;
            line-height: 20px;
            font-weight: 500;
            text-transform: uppercase;
            border: none;
            border-radius: 4px;
        """)
        self.login_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.login_button)

        # Setze das Layout
        self.setLayout(layout)

    def open_additional_dialog(self, event):
        additional_dialog = QDialog(self)
        additional_dialog.setWindowTitle("Zusätzlicher Dialog")
        additional_dialog.setGeometry(150, 150, 300, 200)
        additional_dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_dialog = LoginDialog()
    login_dialog.exec_()
    sys.exit(0)
