# ---------------------------------------------------------------------------
# File:   observer.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import sys
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore    import QTimer, QDir

from PyQt5.QtWidgets import *  # Qt5 widgets
from PyQt5.QtGui     import *  # Qt5 gui
from PyQt5.QtCore    import *  # Qt5 core

class FileWatcherGUI(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.initUI()
    
    def menu_help_clicked_about(self):
        QMessageBox.information(self,
        "About...",
        "This is HelpNDoc.com FileChecker v.0.0.1\n" +
        "(c) 2024 by Jens Kallup - paule32\n" +
        "all rights reserved.")
        return

    def menu_edit_clicked_clearall(self):
        return

    def file_tree_clicked(self, index):
        self.path = self.dir_model.fileInfo(index).absoluteFilePath()
        self.file_list.setRootIndex(self.file_model.setRootPath(self.path))
        return

    def initUI(self):
        # Layout
        self.setMaximumWidth (800)
        self.setMaximumHeight(600)
        
        self.layout = QVBoxLayout()
        
        # menu bar
        self.menu_bar = QMenuBar(self)
        
        self.fileMenu = self.menu_bar.addMenu("&File")
        self.editMenu = self.menu_bar.addMenu("&Edit")
        self.helpMenu = self.menu_bar.addMenu("&Help")
        
        self.fileMenuExitAction  = QAction("Exit", self)
        self.fileMenuExitAction.setShortcut('Alt-X')
        self.fileMenuExitAction.triggered.connect(self.close)
        
        self.editMenuClearAction = QAction("Clear All", self)
        self.editMenuClearAction.setShortcut("Ctrl+D")
        self.editMenuClearAction.triggered.connect(self.menu_edit_clicked_clearall)
        
        self.helpMenuAboutAction = QAction("About ...", self)
        self.helpMenuAboutAction.setShortcut("F1")
        self.helpMenuAboutAction.triggered.connect(self.menu_help_clicked_about)
        
        self.fileMenu.addAction(self.fileMenuExitAction)
        self.editMenu.addAction(self.editMenuClearAction)
        self.helpMenu.addAction(self.helpMenuAboutAction)
        
        self.layout.addWidget( self.menu_bar )
        self.menu_bar.show()
        
        # tool bar
        self.tool_bar = QToolBar()
        self.tool_bar_button_exit = QToolButton()
        self.tool_bar_button_exit.setText("Clear")
        self.tool_bar_button_exit.setCheckable(True)
        
        self.tool_bar_action_new1 = QAction(QIcon("../img/floppy-disk.png"), "Flopp", self)
        self.tool_bar_action_new2 = QAction(QIcon("../img/floppy-disk.png"), "Flopp", self)
        self.tool_bar_action_new3 = QAction(QIcon("../img/floppy-disk.png"), "Flopp", self)
        
        self.tool_bar.addAction(self.tool_bar_action_new1)
        self.tool_bar.addAction(self.tool_bar_action_new2)
        self.tool_bar.addAction(self.tool_bar_action_new3)
        
        self.tool_bar.addWidget(self.tool_bar_button_exit)
        
        self.layout.addWidget(self.tool_bar)
        self.tool_bar.show()
        
        
        # status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready", 0)
        
                
        # first register card - action's ...
        
        
        # components
        self.top_layout    = QHBoxLayout()
        self.left_layout   = QVBoxLayout()
        self.middle_layout = QVBoxLayout()
        self.right_layout  = QVBoxLayout()
        
        # ------------------
        # left, top part ...
        # ------------------
        self.fold_text = QLabel('Directory:', self)
        self.file_text = QLabel("File:", self)
        #
        self.left_layout.addWidget(self.fold_text)
        
        # pre
        self.pre_action_label = QLabel('Pre-Actions:', self)
        self.middle_layout.addWidget(self.pre_action_label);
        
        # post
        self.post_action_label = QLabel('Post-Actions:', self)
        self.right_layout.addWidget(self.post_action_label);
        
        # ----------------------------
        # left side directory view ...
        # ----------------------------
        self.path = QDir.homePath()
        
        self.dir_model = QFileSystemModel()
        self.dir_model.setRootPath(self.path)
        self.dir_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        
        self.file_tree = QTreeView()
        self.file_list = QListView()
        
        self.file_tree.setModel(self.dir_model)
        self.file_list.setModel(self.file_model)
        
        self.file_tree.setRootIndex(self. dir_model.index(self.path))
        self.file_list.setRootIndex(self.file_model.index(self.path))
        
        self.left_layout.addWidget(self.file_tree)
        self.left_layout.addWidget(self.file_text)
        self.left_layout.addWidget(self.file_list)
        
        self.file_tree.clicked.connect(self.file_tree_clicked)
        
        
        # Eingabezeile für den Pfad
        self.path_lineEdit = QLineEdit(self)
        self.path_lineButton = QPushButton("...")
        self.path_lineButton.setMaximumWidth(32)
        
        self.path_layout = QHBoxLayout()
        
        self.path_layout.addWidget(self.path_lineEdit)
        self.path_layout.addWidget(self.path_lineButton)
        #
        self.left_layout.addLayout(self.path_layout)
        
        # Start und Stop Buttons
        self.startButton = QPushButton('Start', self)
        self.startButton.clicked.connect(self.startWatching)
        self.left_layout.addWidget(self.startButton)
        
        self.stopButton = QPushButton('Stop', self)
        self.stopButton.clicked.connect(self.stopWatching)
        self.left_layout.addWidget(self.stopButton)
        
        # ComboBox für Zeitangaben
        self.timeComboBox = QComboBox(self)
        self.timeComboBox.addItems(["10", "15", "20", "25", "30", "60", "120"])
        self.timeComboBox.setMaximumWidth(49)
        self.left_layout.addWidget(self.timeComboBox)
        
        # Label für den Countdown
        self.countdownLabel = QLabel('Select time:', self)
        self.left_layout.addWidget(self.countdownLabel)
        
        # mitte Seite
        self.preActionList = QListWidget(self)
        self.preActionList_Label  = QLabel("Content:", self)
        self.preActionList_Editor = QPlainTextEdit()
        #
        self.middle_layout.addWidget(self.preActionList)
        self.middle_layout.addWidget(self.preActionList_Label)
        self.middle_layout.addWidget(self.preActionList_Editor)
        
        #
        self.preActionComboBox = QComboBox(self)
        self.preActionComboBox.addItems(["Message", "Script", "URL", "FTP"])
        self.timeComboBox.setMaximumWidth(49)
        self.middle_layout.addWidget(self.preActionComboBox)
        
        self.preEditLineLabel = QLabel("Text / File:", self)
        self.middle_layout.addWidget(self.preEditLineLabel)
        #
        self.pre_layout = QHBoxLayout()
        
        self.preEditLineText = QLineEdit(self)
        self.preEditLineTextButton = QPushButton("...")
        self.preEditLineTextButton.setMaximumWidth(32)
        
        self.preEditLineFile = QLineEdit(self)
        self.preEditLineFileButton = QPushButton("...")
        self.preEditLineFileButton.setMaximumWidth(32)
        #
        self.pre_layout.addWidget(self.preEditLineText)
        self.pre_layout.addWidget(self.preEditLineTextButton)
        
        self.pre_layout.addWidget(self.preEditLineFile)
        self.pre_layout.addWidget(self.preEditLineFileButton)
        
        self.middle_layout.addLayout(self.pre_layout)
        
        self.preAddButton = QPushButton("Add")
        self.preDelButton = QPushButton("Delete")
        self.preClrButton = QPushButton("Clear All")
        #
        self.middle_layout.addWidget(self.preAddButton)
        self.middle_layout.addWidget(self.preDelButton)
        self.middle_layout.addWidget(self.preClrButton)
        
        
        # rechte Seite
        self.postActionList = QListWidget(self)
        self.postActionList_Label  = QLabel("Content:", self)
        self.postActionList_Editor = QPlainTextEdit()
        #
        self.right_layout.addWidget(self.postActionList)
        self.right_layout.addWidget(self.postActionList_Label)
        self.right_layout.addWidget(self.postActionList_Editor)
        
        self.postActionComboBox = QComboBox(self)
        self.postActionComboBox.addItems(["Message", "Script", "URL", "FTP"])
        self.right_layout.addWidget(self.postActionComboBox)
        
        self.postEditLineLabel = QLabel("Text / File:", self)
        self.right_layout.addWidget(self.postEditLineLabel)
        #
        self.post_layout = QHBoxLayout()
        
        self.postEditLineText = QLineEdit(self)
        self.postEditLineTextButton = QPushButton("...")
        self.postEditLineTextButton.setMaximumWidth(32)
        
        self.postEditLineFile = QLineEdit(self)
        self.postEditLineFileButton = QPushButton("...")
        self.postEditLineFileButton.setMaximumWidth(32)
        #
        self.post_layout.addWidget(self.postEditLineText)
        self.post_layout.addWidget(self.postEditLineTextButton)
        #
        self.post_layout.addWidget(self.postEditLineFile)
        self.post_layout.addWidget(self.postEditLineFileButton)
        #
        self.right_layout.addLayout(self.post_layout)
        
        self.postAddButton = QPushButton("Add")
        self.postDelButton = QPushButton("Delete")
        self.postClrButton = QPushButton("Clear All")
        #
        self.right_layout.addWidget(self.postAddButton)
        self.right_layout.addWidget(self.postDelButton)
        self.right_layout.addWidget(self.postClrButton)
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateCountdown)

        # alles zusammen ...
        self.layout.addLayout(self.top_layout)
        
        self.top_layout.addLayout(self.left_layout)
        self.top_layout.addLayout(self.middle_layout)
        self.top_layout.addLayout(self.right_layout)
        
        self.layout.addWidget(self.status_bar)
        
        self.setLayout(self.layout)
        self.setWindowTitle('HelpNDoc File Watcher v0.0.1 - by paule32')

        self.interval = 0
        self.currentTime = 0

    def startWatching(self):
        # Timer starten
        self.interval = int(self.timeComboBox.currentText())
        self.currentTime = self.interval
        self.updateCountdownLabel()
        self.timer.start(1000)

    def stopWatching(self):
        # Timer stoppen
        self.timer.stop()
        self.countdownLabel.setText('Select time.')

    def updateCountdown(self):
        self.currentTime -= 1
        if self.currentTime <= 0:
            self.currentTime = self.interval
            # Dateiüberwachung ausführen
            self.checkFileExistence()
        self.updateCountdownLabel()

    def updateCountdownLabel(self):
        self.countdownLabel.setText(f'Next check in: {self.currentTime} Seconds')

    def checkFileExistence(self):
        filePath = self.path_lineEdit.text()
        if os.path.exists(filePath):
            print(f"File {filePath} exists.")
            # Hier könnten Sie weitere Aktionen durchführen, wenn die Datei existiert
        else:
            print(f"File {filePath} not found.")
            # Hier könnten Sie Aktionen durchführen, wenn die Datei nicht existiert

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = FileWatcherGUI()
    ex.show()
    sys.exit(app.exec_())
