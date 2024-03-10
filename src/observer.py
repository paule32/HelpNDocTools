# ---------------------------------------------------------------------------
# File:   observer.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import os            # operating system stuff
import sys           # system specifies
import datetime      # date, and time routines

import random        # randome numbers
import string

import sqlite3       # database: sqlite
import configparser  # .ini files

import traceback     # stack exception trace back

from PyQt5.QtWidgets import *
from PyQt5.QtCore    import QTimer, QDir

from PyQt5.QtWidgets import *  # Qt5 widgets
from PyQt5.QtGui     import *  # Qt5 gui
from PyQt5.QtCore    import *  # Qt5 core

def get_current_time():
    return datetime.datetime.now().strftime("%H_%M")

def get_current_date():
    return datetime.datetime.now().strftime("%Y_%m_%d")

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
        self.tab1_file_list.setRootIndex(self.file_model.setRootPath(self.path))
        return

    def file_list_clicked(self, index):
        self.path_file = self.dir_model.fileInfo(index).absoluteFilePath()
        print(f"path: {self.path}  | file: {self.path_file}")
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
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        #self.tabs.resize(300,200)
        
        # add tabs
        self.tabs.addTab(self.tab1, "Actions")
        self.tabs.addTab(self.tab2, "Tab 2")
        
        # create first tab
        self.tab1_top_layout    = QHBoxLayout(self.tab1)
        self.tab1_left_layout   = QVBoxLayout(self.tab1)
        self.tab1_middle_layout = QVBoxLayout(self.tab1)
        self.tab1_right_layout  = QVBoxLayout(self.tab1)
        
        # ------------------
        # left, top part ...
        # ------------------
        self.tab1_fold_text = QLabel('Directory:', self.tab1)
        self.tab1_file_text = QLabel("File:", self.tab1)
        #
        self.tab1_left_layout.addWidget(self.tab1_fold_text)
        
        # pre
        self.tab1_pre_action_label = QLabel('Pre-Actions:', self.tab1)
        self.tab1_middle_layout.addWidget(self.tab1_pre_action_label);
        
        # post
        self.tab1_post_action_label = QLabel('Post-Actions:', self.tab1)
        self.tab1_right_layout.addWidget(self.tab1_post_action_label);
        
        # ----------------------------
        # left side directory view ...
        # ----------------------------
        self.path = QDir.homePath()
        
        self.dir_model = QFileSystemModel()
        self.dir_model.setRootPath(self.path)
        self.dir_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        
        self.file_model = QFileSystemModel()
        self.file_model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        
        self.tab1_file_tree = QTreeView()
        self.tab1_file_list = QListView()
        
        self.tab1_file_tree.setModel(self.dir_model)
        self.tab1_file_list.setModel(self.file_model)
        
        self.tab1_file_tree.setRootIndex(self. dir_model.index(self.path))
        self.tab1_file_list.setRootIndex(self.file_model.index(self.path))
        
        self.tab1_left_layout.addWidget(self.tab1_file_tree)
        self.tab1_left_layout.addWidget(self.tab1_file_text)
        self.tab1_left_layout.addWidget(self.tab1_file_list)
        
        self.tab1_file_tree.clicked.connect(self.file_tree_clicked)
        self.tab1_file_list.clicked.connect(self.file_list_clicked)
        
        
        # Eingabezeile für den Pfad
        self.tab1_path_lineEdit = QLineEdit(self.tab1)
        self.tab1_path_lineButton = QPushButton("...")
        self.tab1_path_lineButton.setMaximumWidth(32)
        
        self.tab1_path_layout = QHBoxLayout()
        
        self.tab1_path_layout.addWidget(self.tab1_path_lineEdit)
        self.tab1_path_layout.addWidget(self.tab1_path_lineButton)
        #
        self.tab1_left_layout.addLayout(self.tab1_path_layout)
        
        # Start und Stop Buttons
        self.tab1_startButton = QPushButton('Start', self.tab1)
        self.tab1_startButton.clicked.connect(self.startWatching)
        self.tab1_left_layout.addWidget(self.tab1_startButton)
        
        self.tab1_stopButton = QPushButton('Stop', self.tab1)
        self.tab1_stopButton.clicked.connect(self.stopWatching)
        self.tab1_left_layout.addWidget(self.tab1_stopButton)
        
        # ComboBox für Zeitangaben
        self.tab1_timeComboBox = QComboBox(self.tab1)
        self.tab1_timeComboBox.addItems(["10", "15", "20", "25", "30", "60", "120"])
        self.tab1_timeComboBox.setMaximumWidth(49)
        self.tab1_left_layout.addWidget(self.tab1_timeComboBox)
        
        # Label für den Countdown
        self.tab1_countdownLabel = QLabel('Select time:', self.tab1)
        self.tab1_left_layout.addWidget(self.tab1_countdownLabel)
        
        # mitte Seite
        self.tab1_preActionList = QListWidget(self.tab1)
        self.tab1_preActionList_Label  = QLabel("Content:", self.tab1)
        self.tab1_preActionList_Editor = QPlainTextEdit()
        #
        self.tab1_middle_layout.addWidget(self.tab1_preActionList)
        self.tab1_middle_layout.addWidget(self.tab1_preActionList_Label)
        self.tab1_middle_layout.addWidget(self.tab1_preActionList_Editor)
        
        #
        self.tab1_preActionComboBox = QComboBox(self.tab1)
        self.tab1_preActionComboBox.addItems(["Message", "Script", "URL", "FTP"])
        self.tab1_timeComboBox.setMaximumWidth(49)
        self.tab1_middle_layout.addWidget(self.tab1_preActionComboBox)
        
        self.tab1_preEditLineLabel = QLabel("Text / File:", self.tab1)
        self.tab1_middle_layout.addWidget(self.tab1_preEditLineLabel)
        #
        self.tab1_pre_layout = QHBoxLayout()
        
        self.tab1_preEditLineText = QLineEdit(self.tab1)
        self.tab1_preEditLineTextButton = QPushButton("...")
        self.tab1_preEditLineTextButton.setMaximumWidth(32)
        
        self.tab1_preEditLineFile = QLineEdit(self.tab1)
        self.tab1_preEditLineFileButton = QPushButton("...")
        self.tab1_preEditLineFileButton.setMaximumWidth(32)
        #
        self.tab1_pre_layout.addWidget(self.tab1_preEditLineText)
        self.tab1_pre_layout.addWidget(self.tab1_preEditLineTextButton)
        
        self.tab1_pre_layout.addWidget(self.tab1_preEditLineFile)
        self.tab1_pre_layout.addWidget(self.tab1_preEditLineFileButton)
        
        self.tab1_middle_layout.addLayout(self.tab1_pre_layout)
        
        self.tab1_preAddButton = QPushButton("Add")
        self.tab1_preDelButton = QPushButton("Delete")
        self.tab1_preClrButton = QPushButton("Clear All")
        #
        self.tab1_preAddButton.clicked.connect(self.button_clicked_preadd)
        self.tab1_preDelButton.clicked.connect(self.button_clicked_preDel)
        self.tab1_preClrButton.clicked.connect(self.button_clicked_preClr)
        #
        self.tab1_middle_layout.addWidget(self.tab1_preAddButton)
        self.tab1_middle_layout.addWidget(self.tab1_preDelButton)
        self.tab1_middle_layout.addWidget(self.tab1_preClrButton)
        
        
        # rechte Seite
        self.tab1_postActionList = QListWidget(self.tab1)
        self.tab1_postActionList_Label  = QLabel("Content:", self.tab1)
        self.tab1_postActionList_Editor = QPlainTextEdit()
        #
        self.tab1_right_layout.addWidget(self.tab1_postActionList)
        self.tab1_right_layout.addWidget(self.tab1_postActionList_Label)
        self.tab1_right_layout.addWidget(self.tab1_postActionList_Editor)
        
        self.tab1_postActionComboBox = QComboBox(self.tab1)
        self.tab1_postActionComboBox.addItems(["Message", "Script", "URL", "FTP"])
        self.tab1_right_layout.addWidget(self.tab1_postActionComboBox)
        
        self.tab1_postEditLineLabel = QLabel("Text / File:", self.tab1)
        self.tab1_right_layout.addWidget(self.tab1_postEditLineLabel)
        #
        self.tab1_post_layout = QHBoxLayout()
        
        self.tab1_postEditLineText = QLineEdit(self.tab1)
        self.tab1_postEditLineTextButton = QPushButton("...")
        self.tab1_postEditLineTextButton.setMaximumWidth(32)
        
        self.tab1_postEditLineFile = QLineEdit(self.tab1)
        self.tab1_postEditLineFileButton = QPushButton("...")
        self.tab1_postEditLineFileButton.setMaximumWidth(32)
        #
        self.tab1_post_layout.addWidget(self.tab1_postEditLineText)
        self.tab1_post_layout.addWidget(self.tab1_postEditLineTextButton)
        #
        self.tab1_post_layout.addWidget(self.tab1_postEditLineFile)
        self.tab1_post_layout.addWidget(self.tab1_postEditLineFileButton)
        #
        self.tab1_right_layout.addLayout(self.tab1_post_layout)
        
        self.tab1_postAddButton = QPushButton("Add")
        self.tab1_postDelButton = QPushButton("Delete")
        self.tab1_postClrButton = QPushButton("Clear All")
        #
        self.tab1_postAddButton.clicked.connect(self.button_clicked_postadd)
        self.tab1_postDelButton.clicked.connect(self.button_clicked_postDel)
        self.tab1_postClrButton.clicked.connect(self.button_clicked_postClr)
        #
        self.tab1_right_layout.addWidget(self.tab1_postAddButton)
        self.tab1_right_layout.addWidget(self.tab1_postDelButton)
        self.tab1_right_layout.addWidget(self.tab1_postClrButton)
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateCountdown)
        
        # ------------------
        # alles zusammen ...
        # ------------------
        self.tab1_top_layout.addLayout(self.tab1_left_layout)
        self.tab1_top_layout.addLayout(self.tab1_middle_layout)
        self.tab1_top_layout.addLayout(self.tab1_right_layout)
        
        
        self.layout.addWidget(self.tabs)
        self.layout.addWidget(self.status_bar)
        
        self.setLayout(self.layout)
        self.setWindowTitle('HelpNDoc File Watcher v0.0.1 - (c) 2024 Jens Kallup - paule32')
        
        self.interval = 0
        self.currentTime = 0

    def generate_random_string(self, length):
        characters = string.ascii_uppercase + string.digits
        random_string = ''.join(random.sample(characters, length))
        return random_string

    # pre-fixed
    def button_clicked_preadd(self):
        random_string = self.generate_random_string(random.randint(8,32))
        item = QListWidgetItem(random_string)
        self.tab1_preActionList.addItem(item)
        return

    def button_clicked_preDel(self):
        listItems = self.tab1_preActionList.selectedItems()
        if not listItems: return        
        for item in listItems:
            self.tab1_preActionList.takeItem(self.tab1_preActionList.row(item))
        return

    def button_clicked_preClr(self):
        self.tab1_preActionList.clear()
        return

    # post-fixed
    def button_clicked_postadd(self):
        random_string = self.generate_random_string(random.randint(8,32))
        item = QListWidgetItem(random_string)
        self.tab1_postActionList.addItem(item)
        return

    def button_clicked_postDel(self):
        listItems = self.tab1_postActionList.selectedItems()
        if not listItems: return        
        for item in listItems:
            self.tab1_postActionList.takeItem(self.tab1_postActionList.row(item))
        return

    def button_clicked_postClr(self):
        self.tab1_postActionList.clear()
        return

    def startWatching(self):
        # Timer starten
        self.interval = int(self.tab1_timeComboBox.currentText())
        self.currentTime = self.interval
        self.updateCountdownLabel()
        self.timer.start(1000)

    def stopWatching(self):
        # Timer stoppen
        self.timer.stop()
        self.tab1_countdownLabel.setText('Select time.')

    def updateCountdown(self):
        self.currentTime -= 1
        if self.currentTime <= 0:
            self.currentTime = self.interval
            # Dateiüberwachung ausführen
            self.checkFileExistence()
        self.updateCountdownLabel()

    def updateCountdownLabel(self):
        self.tab1_countdownLabel.setText(f'Next check in: {self.currentTime} Seconds')

    def checkFileExistence(self):
        filePath = self.tab1_path_lineEdit.text()
        if os.path.exists(filePath):
            print(f"File {filePath} exists.")
            # weitere Aktionen durchführen, wenn die Datei existiert
        else:
            print(f"File {filePath} not found.")
            # ktionen durchführen, wenn die Datei nicht existiert

if __name__ == '__main__':
    global conn
    global conn_cursor
    
    try:
        app = QApplication(sys.argv)
        
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        
        conn = sqlite3.connect("data.db")
        conn_cursor = conn.cursor()
        conn.close()
        
        ex = FileWatcherGUI()
        ex.show()
    except Exception as ex:
        print("Exception occur: " + f"{ex}")
        sys.exit(1)
    finally:
        sys.exit(app.exec_())
