# main.py
from PyQt5 import QtWidgets
from main_window import MainWindow
import sys

def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.resize(1100, 700)
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
