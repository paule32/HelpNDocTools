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
from PyQt5.QtCore import *

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

global topic_counter

def get_current_time():
    return datetime.datetime.now().strftime("%H_%M")

def get_current_date():
    return datetime.datetime.now().strftime("%Y_%m_%d")

class CustomModel(QAbstractItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.root_item = None
    
    def index(self, row, column, parent):
        if not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()
        
        if parent_item is None or row < 0 or column < 0 or row >= len(parent_item[1]):
            return QModelIndex()
        
        return self.createIndex(row, column, parent_item[1][row])
    
    def parent(self, index):
        # Hier wird der Elternindex des Elements zurückgegeben
        pass
    
    def rowCount(self, parent=QModelIndex()):
        if not parent.isValid():
            return 1  # Anzahl der Hauptknoten
        item = parent.internalPointer()
        if item:
            return len(item[1])  # Anzahl der Unterknoten
        return 0
    
    def columnCount(self, parent=QModelIndex()):
        # Hier wird die Anzahl der Spalten unter einem gegebenen Index zurückgegeben
        return 1
    
    def data(self, index, role):
        # Hier werden Daten für das gegebene Indexelement und Rolle zurückgegeben
        pass

class ComboBoxDelegateStatus(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        # Add items to the combobox
        editor.addItem(QIcon("../img/icon_white.png" ), "Complete"     )
        editor.addItem(QIcon("../img/icon_blue.png"  ), "Needs Review" )
        editor.addItem(QIcon("../img/icon_yellow.png"), "In Progress"  )
        editor.addItem(QIcon("../img/icon_red.png"   ), "Out of Date"  )
        
        #editor.activated.connect(self.on_activated)
        editor.currentTextChanged.connect(self.on_current_text_changed)
        editor.currentIndexChanged.connect(self.on_current_index_changed)
        return editor
    
    # index is text/string
    def on_current_index_changed(self, index):
        if type(index) == str:
            index = index.strip()
            if index == "Complete":
                return
            elif index == "Needs Review":
                return
            elif index == "In Progress":
                return
            elif index == "Out of Date":
                return
        return
    
    # index is number
    def on_current_text_changed(self, index):
        self.on_current_index_changed(index)
        return
    
    # index is number
    def on_activated(self, index):
        self.on_current_index_changed(index)
        return

class ComboBoxDelegateIcon(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        # Add items to the combobox
        editor.addItem("Option 1")
        editor.addItem("Option 2")
        editor.addItem("Option 3")
        return editor

class CheckableComboBox(QComboBox):
    def __init__(self, parent):
        super(CheckableComboBox, self).__init__(parent)
        self.view().pressed.connect(self.handleItemPressed)
        self.setModel(QStandardItemModel(self))

    def handleItemPressed(self, index):
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            item.setCheckState(Qt.Unchecked)
        else:
            item.setCheckState(Qt.Checked)

class ComboBoxDelegateBuild(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = CheckableComboBox(parent); i = 1
        i = 1
        editor.addItem(QIcon("../img/icon_yellow.png" ), "CHM " + str(i))
        item1 = editor.model().item(i-1, 0); item1.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon("../img/icon_yellow.png" ), "HTML " + str(i))
        item2 = editor.model().item(i-1, 0); item2.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon("../img/icon_yellow.png" ), "Word " + str(i))
        item3 = editor.model().item(i-1, 0); item3.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon("../img/icon_yellow.png" ), "PDF " + str(i))
        item4 = editor.model().item(i-1, 0); item4.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon("../img/icon_yellow.png" ), "EPub " + str(i))
        item5 = editor.model().item(i-1, 0); item5.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon("../img/icon_yellow.png" ), "Kindle " + str(i))
        item6 = editor.model().item(i-1, 0); item6.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon("../img/icon_yellow.png" ), "Qt Help " + str(i))
        item7 = editor.model().item(i-1, 0); item7.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon("../img/icon_yellow.png" ), "Markdown " + str(i))
        item8 = editor.model().item(i-1, 0); item8.setCheckState(Qt.Unchecked); i = i + 1
        
        return editor

class SpinEditDelegateID(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        global topic_counter
        editor = QSpinBox(parent)
        editor.setValue(topic_counter)
        topic_counter = topic_counter + 1
        return editor

class CustomItem(QStandardItem):
    def __init__(self, text, icon):
        super().__init__(text)
        self.icon = icon
    
    def paint(self, painter, option, index):
        super().paint(painter, option, index)
        
        icon_rect = option.rect.adjusted(4, 4, 20, -4)
        painter.drawPixmap(icon_rect, self.icon.pixmap(16, 16))

class MyItemRecord:
    def __init__(self, item_attr1, item_attr2):
        self.record_array = []
        
        self.attr1 = item_attr1
        self.attr2 = item_attr2
        
        self.add(self.attr1, self.attr2)
        return
    
    def add(self, item_attr1, item_attr2):
        self.record_array.insert(item_attr1, item_attr2)
        return

class FileWatcherGUI(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        
        self.my_list = MyItemRecord(0, QStandardItem(""))
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
    
    def tab0_file_tree_clicked(self, index):
        self.tab0_path = self.tab0_dir_model.fileInfo(index).absoluteFilePath()
        self.tab0_file_list.setRootIndex(self.tab0_file_model.setRootPath(self.tab0_path))
        return
    
    def tab1_file_tree_clicked(self, index):
        self.tab1_path = self.tab1_dir_model.fileInfo(index).absoluteFilePath()
        self.tab1_file_list.setRootIndex(self.tab1_file_model.setRootPath(self.tab1_path))
        return
    
    def tab0_file_list_clicked(self, index):
        self.tab0_path_file = self.tab0_dir_model.fileInfo(index).absoluteFilePath()
        return
    
    def tab1_file_list_clicked(self, index):
        self.tab1_path_file = self.tab1_dir_model.fileInfo(index).absoluteFilePath()
        self.tab1_path_lineEdit.setText(f"{self.tab1_path_file}")
        return
    
    def populate_tree_view(self, file_path, icon):
        with open(file_path, 'r') as file:
            roots = []
            stack = [self.tab2_tree_model.invisibleRootItem()]
            
            topic_counter = 1
            
            for line in file:
                line = line.rstrip('\n')
                num_plus = 0
                while line[num_plus] == '+':
                    num_plus += 1
                
                item_name = line.strip('+').strip()
                
                new_item = QStandardItem(item_name)
                new_item.setIcon(QIcon(icon))
                
                global item2
                item1 = QStandardItem(str(topic_counter))
                item2 = QStandardItem(" ") #item2.setIcon(QIcon(icon))
                item3 = QStandardItem(" ")
                item4 = QStandardItem(" ")
                
                self.my_list.add(topic_counter, item1)
                
                topic_counter = topic_counter + 1
                
                while len(stack) > num_plus + 1:
                    stack.pop()
                
                stack[-1].appendRow([new_item, item1, item2, item3, item4])
                stack.append(new_item)
    
    def add_tree_item(self, parent_item, item_name):
        new_item = QStandardItem(item_name)
        parent_item.appendRow(new_item)
    
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
        
        
        # side toolbar
        self.main_layout = QHBoxLayout()
        self.main_widget = QWidget()
        
        self.side_layout = QVBoxLayout()
        self.side_widget = QWidget()
        
        self.side_btn1 = QPushButton("1", self.side_widget)
        self.side_btn2 = QPushButton("2", self.side_widget)
        self.side_btn3 = QPushButton("3", self.side_widget)
        
        self.side_btn1.setStyleSheet("height:49px;")
        self.side_btn2.setStyleSheet("height:49px;")
        self.side_btn3.setStyleSheet("height:49px;")
        
        self.side_lbl0 = QLabel()
        self.side_lbl0.setAlignment(Qt.AlignTop)
        
        self.side_layout.addWidget(self.side_btn1)
        self.side_layout.addWidget(self.side_btn2)
        self.side_layout.addWidget(self.side_btn3)
        
        self.side_layout.addWidget(self.side_lbl0)
        
        self.side_widget.setLayout(self.side_layout)
        self.main_layout.addWidget(self.side_widget)
                
        # first register card - action's ...
        self.tabs = QTabWidget()
        self.tab0 = QWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        
        # add tabs
        self.tabs.addTab(self.tab0, "Project")
        self.tabs.addTab(self.tab1, "Pre-/Post Actions")
        self.tabs.addTab(self.tab2, "Topics")
        self.tabs.addTab(self.tab3, "Content")
        
        self.main_layout.addWidget(self.tabs)
        
        # create project tab
        self.tab2_top_layout    = QHBoxLayout(self.tab2)
        self.tab2_left_layout   = QVBoxLayout(self.tab2)
        
        #self.tab2_fold_text = QLabel('Directory:', self.tab2)
        #self.tab2_file_text = QLabel("File:", self.tab2)
        
        #self.tab2_left_layout.addWidget(self.tab2_fold_text)
        
        self.tab2_file_path = 'topics.txt'
        
        global tab2_tree_view
        tab2_tree_view = QTreeView()
        tab2_tree_view.setStyleSheet("QHeaderView::section{background-color:lightblue;color:black;font-weight:bold;}")
        self.tab2_tree_model = QStandardItemModel()
        self.tab2_tree_model.setHorizontalHeaderLabels(["Topic name", "ID", "Status", "Help icon", "In Build"])
        tab2_tree_view.setModel(self.tab2_tree_model)
        
        self.tab2_top_layout.addWidget(tab2_tree_view)
        self.populate_tree_view(self.tab2_file_path, "../img/open-folder.png")
        
        self.delegateID     = SpinEditDelegateID     (tab2_tree_view)
        self.delegateStatus = ComboBoxDelegateStatus (tab2_tree_view)
        self.delegateIcon   = ComboBoxDelegateIcon   (tab2_tree_view)
        self.delegateBuild  = ComboBoxDelegateBuild  (tab2_tree_view)
        
        tab2_tree_view.setItemDelegateForColumn(1, self.delegateID)
        tab2_tree_view.setItemDelegateForColumn(2, self.delegateStatus)
        tab2_tree_view.setItemDelegateForColumn(3, self.delegateIcon)
        tab2_tree_view.setItemDelegateForColumn(4, self.delegateBuild)
        
        #self.tab2_top_layout.
        
        
        # create project tab
        self.tab0_top_layout    = QHBoxLayout(self.tab0)
        self.tab0_left_layout   = QVBoxLayout(self.tab0)
        
        self.tab0_fold_text = QLabel('Directory:', self.tab0)
        self.tab0_file_text = QLabel("File:", self.tab0)
        
        self.tab0_left_layout.addWidget(self.tab0_fold_text)
        self.tab0_path = QDir.homePath()
        
        self.tab0_dir_model = QFileSystemModel()
        self.tab0_dir_model.setRootPath(self.tab0_path)
        self.tab0_dir_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        
        self.tab0_file_model = QFileSystemModel()
        self.tab0_file_model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        
        self.tab0_file_tree = QTreeView()
        self.tab0_file_list = QListView()
        
        self.tab0_file_tree.setModel(self.tab0_dir_model)
        self.tab0_file_list.setModel(self.tab0_file_model)
        
        self.tab0_file_tree.setRootIndex(self.tab0_dir_model.index(self.tab0_path))
        self.tab0_file_list.setRootIndex(self.tab0_file_model.index(self.tab0_path))
        
        self.tab0_left_layout.addWidget(self.tab0_file_tree)
        self.tab0_left_layout.addWidget(self.tab0_file_text)
        self.tab0_left_layout.addWidget(self.tab0_file_list)
        
        self.tab0_file_tree.clicked.connect(self.tab0_file_tree_clicked)
        self.tab0_file_list.clicked.connect(self.tab0_file_list_clicked)
        
        
        
        
        # create action tab
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
        self.tab1_path = QDir.homePath()
        
        self.tab1_dir_model = QFileSystemModel()
        self.tab1_dir_model.setRootPath(self.tab1_path)
        self.tab1_dir_model.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs)
        
        self.tab1_file_model = QFileSystemModel()
        self.tab1_file_model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        
        self.tab1_file_tree = QTreeView()
        self.tab1_file_list = QListView()
        
        self.tab1_file_tree.setModel(self.tab1_dir_model)
        self.tab1_file_list.setModel(self.tab1_file_model)
        
        self.tab1_file_tree.setRootIndex(self.tab1_dir_model.index(self.tab1_path))
        self.tab1_file_list.setRootIndex(self.tab1_file_model.index(self.tab1_path))
        
        self.tab1_left_layout.addWidget(self.tab1_file_tree)
        self.tab1_left_layout.addWidget(self.tab1_file_text)
        self.tab1_left_layout.addWidget(self.tab1_file_list)
        
        self.tab1_file_tree.clicked.connect(self.tab1_file_tree_clicked)
        self.tab1_file_list.clicked.connect(self.tab1_file_list_clicked)
        
        
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
        
        
        # ------------------
        # alles zusammen ...
        # ------------------
        self.tab0_top_layout.addLayout(self.tab0_left_layout)
        
        self.tab1_top_layout.addLayout(self.tab1_left_layout)
        self.tab1_top_layout.addLayout(self.tab1_middle_layout)
        self.tab1_top_layout.addLayout(self.tab1_right_layout)
        
        self.layout.addLayout(self.main_layout)
        self.layout.addWidget(self.status_bar)
        
        self.setLayout(self.layout)
        self.setWindowTitle('HelpNDoc File Watcher v0.0.1 - (c) 2024 Jens Kallup - paule32')
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateCountdown)

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
        topic_counter = 1
        
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
