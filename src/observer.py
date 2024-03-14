# ---------------------------------------------------------------------------
# File:   observer.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
global EXIT_SUCCESS; EXIT_SUCCESS = 0
global EXIT_FAILURE; EXIT_FAILURE = 1

global basedir
global tr

try:
    import os            # operating system stuff
    import sys           # system specifies
    import time          # thread count
    import datetime      # date, and time routines
    import re            # regular expression handling
    
    import glob          # directory search
    import subprocess    # start sub processes
    import platform      # Windows ?
    
    import shutil        # shell utils
    import pkgutil       # attached binary data utils
    import json          # json lists
    
    import gettext       # localization
    import locale        # internal system locale
    
    import random        # randome numbers
    import string
    
    import sqlite3       # database: sqlite
    import configparser  # .ini files
    
    import traceback     # stack exception trace back
    
    # ------------------------------------------------------------------------
    # Qt5 gui framework
    # ------------------------------------------------------------------------
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore    import *
    from PyQt5.QtGui     import *
    
    # ------------------------------------------------------------------------
    # global used application stuff ...
    # ------------------------------------------------------------------------
    __app__name        = "observer"
    __app__config_ini  = "observer.ini"
    
    __app__framework   = "PyQt5.QtWidgets.QApplication"
    __app__exec_name   = sys.executable
    
    __app__error_level = "0"
    
    
    global topic_counter
    global css_model_header, css_tabs
    
    if getattr(sys, 'frozen', False):
        import pyi_splash
    
    # ------------------------------------------------------------------------
    # branding water marks ...
    # ------------------------------------------------------------------------
    __version__ = "Version 0.0.1"
    __authors__ = "paule32"
    
    __date__    = "2024-01-04"
    
    # ------------------------------------------------------------------------
    # when the user start the application script under Windows 7 and higher:
    # ------------------------------------------------------------------------
    try:
        from ctypes import windll  # Only exists on Windows.
        myappid = 'kallup-nonprofit.helpndoc.observer.1'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass
    
    # ------------------------------------------------------------------------
    # constants, and varibales that are used multiple times ...
    # ------------------------------------------------------------------------
    __copy__ = (""
        + "HelpNDoc.com FileWatcher 0.0.1\n"
        + "(c) 2024 by paule32\n"
        + "all rights reserved.\n")
    
    __error__os__error = (""
        + "can not determine operating system.\n"
        + "start aborted.")
    
    __error__locales_error = "" \
        + "no locales file for this application."

    # ------------------------------------------------------------------------
    # global used locales constants ...
    # ------------------------------------------------------------------------
    __locale__    = "locales"
    __locale__enu = "en_us"
    __locale__deu = "de_de"
    
    basedir = os.path.dirname(__file__)
    
    # ------------------------------------------------------------------------
    # style sheet definition's:
    # ------------------------------------------------------------------------
    css_model_header = "QHeaderView::section{background-color:lightblue;color:black;font-weight:bold;}"
    css_tabs = (""
        + "QTabWidget::pane{border-top:2px solid #C2C7CB;}"
        + "QTabWidget::tab-bar{left:5px;}"
        + "QTabBar::tab{"
        + "font-family:'Arial';"
        + "font-size:11pt;"
        + "background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
        + "stop:0 #E1E1E1,stop:0.4 #DDDDDD,"
        + "stop:0.5 #D8D8D8,stop:1.0 #D3D3D3);"
        + "border:2px solid #C4C4C3;"
        + "border-bottom-color:#C2C7CB;"
        + "border-top-left-radius:4px;"
        + "border-top-right-radius:4px;"
        + "min-width:35ex;"
        + "padding:2px;}"
        + "QTabBar::tab:selected,QTabBar::tab:hover{"
        + "background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
        + "stop:0 #fafafa,stop:0.4 #f4f4f4,"
        + "stop:0.5 #e7e7e7,stop:1.0 #fafafa);}"
        + "QTabBar::tab:selected{"
        + "border-color:#9B9B9B;"
        + "border-bottom-color:#C2C7CB;}"
        + "QTabBar::tab:!selected{margin-top:2px;}")
    
    css_menu_item_style = (""
        + "QMenuBar{"
        + "background-color:navy;"
        + "padding:2px;margin:0px;"
        + "color:yellow;"
        + "font-size:11pt;"
        + "font-weight:bold;}"
        + "QMenuBar:item:selected{"
        + "background-color:#3366CC;"
        + "color:white;}")
    
    css_menu_label_style = (""
        + "QLabel{background-color:navy;color:yellow;"
        + "font-weight:bold;font-size:11pt;padding:4px;margin:0px;}"
        + "QLabel:hover{background-color:green;color:yellow;}")
    
    css_menu_item = (""
        + "background-color:navy;color:white;padding:0px;font-family:'Arial';font-size:11pt;")
    
    # ------------------------------------------------------------------------
    # convert the os path seperator depend ond the os system ...
    # ------------------------------------------------------------------------
    def convertPath(text):
        if os_type == os_type_windows:
            result = text.replace("/", "\\")
        elif os_type == os_type_linux:
            result = text.replace("\\", "/")
        else:
            showApplicationError(__error__os__error)
            sys.exit(EXIT_FAILURE)
        return result
    
    # ------------------------------------------------------------------------
    # get the locale, based on the system locale settings ...
    # ------------------------------------------------------------------------
    def handle_language(lang):
        try:
            system_lang, _ = locale.getdefaultlocale()
            if system_lang.lower() == __locale__enu:
                if lang.lower() == __locale__enu:
                    tr = gettext.translation(
                    __app__name,
                    localedir=__locale__,
                    languages=[__locale__enu])  # english
                elif lang.lower() == __locale__deu:
                    tr = gettext.translation(
                    __app__name,
                    localedir=__locale__,
                    languages=[__locale__deu])  # german
            elif system_lang.lower() == __locale__deu:
                if lang.lower() == __locale__deu:
                    tr = gettext.translation(
                    __app__name,
                    localedir=__locale__,
                    languages=[__locale__deu])  # english
                elif lang.lower() == __locale__enu:
                    tr = gettext.translation(
                    __app__name,
                    localedir=__locale__,
                    languages=[__locale__enu])  # german
            else:
                print("ennnn")
                tr = gettext.translation(
                __app__name,
                localedir=__locale__,
                languages=[__locale__enu])  # fallback - english
            
            tr.install()
            return tr
        except Exception as ex:
            print(f"{ex}")
            sys.exit(EXIT_FAILURE)
            return None
    
    # ------------------------------------------------------------------------
    # check, if the gui application is initialized by an instance of app ...
    # ------------------------------------------------------------------------
    def isApplicationInit():
        app_instance = QApplication.instance()
        return app_instance is not None
    
    # ------------------------------------------------------------------------
    # methode to show information about this application script ...
    # ------------------------------------------------------------------------
    def showInfo(text):
        infoWindow = QMessageBox()
        infoWindow.setIcon(QMessageBox.Information)
        infoWindow.setWindowTitle("Information")
        infoWindow.setText(text)
        infoWindow.exec_()
    
    def showApplicationInformation(text):
        if isApplicationInit() == False:
            app = QApplication(sys.argv)
            showInfo(text)
        else:
            print(text)
    
    # ------------------------------------------------------------------------
    # methode to show error about this application script ...
    # ------------------------------------------------------------------------
    def showError(text):
        infoWindow = QMessageBox()
        infoWindow.setIcon(QMessageBox.Critical)
        infoWindow.setWindowTitle("Error")
        infoWindow.setText(text)
        infoWindow.show()
        infoWindow.exec_()
    
    def showApplicationError(text):
        if isApplicationInit() == False:
            app = QApplication(sys.argv)
            showError(text)
        else:
            print(text)
    
    # ------------------------------------------------------------------------
    # get current time, and date measured on "now" ...
    # ------------------------------------------------------------------------
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
            editor.addItem(QIcon("img/icon_white.png" ), "Complete"     )
            editor.addItem(QIcon("img/icon_blue.png"  ), "Needs Review" )
            editor.addItem(QIcon("img/icon_yellow.png"), "In Progress"  )
            editor.addItem(QIcon("img/icon_red.png"   ), "Out of Date"  )
            
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
            editor.addItem(QIcon("img/icon_yellow.png" ), "CHM " + str(i))
            item1 = editor.model().item(i-1, 0); item1.setCheckState(Qt.Unchecked); i = i + 1
            
            editor.addItem(QIcon("img/icon_yellow.png" ), "HTML " + str(i))
            item2 = editor.model().item(i-1, 0); item2.setCheckState(Qt.Unchecked); i = i + 1
            
            editor.addItem(QIcon("img/icon_yellow.png" ), "Word " + str(i))
            item3 = editor.model().item(i-1, 0); item3.setCheckState(Qt.Unchecked); i = i + 1
            
            editor.addItem(QIcon("img/icon_yellow.png" ), "PDF " + str(i))
            item4 = editor.model().item(i-1, 0); item4.setCheckState(Qt.Unchecked); i = i + 1
            
            editor.addItem(QIcon("img/icon_yellow.png" ), "EPub " + str(i))
            item5 = editor.model().item(i-1, 0); item5.setCheckState(Qt.Unchecked); i = i + 1
            
            editor.addItem(QIcon("img/icon_yellow.png" ), "Kindle " + str(i))
            item6 = editor.model().item(i-1, 0); item6.setCheckState(Qt.Unchecked); i = i + 1
            
            editor.addItem(QIcon("img/icon_yellow.png" ), "Qt Help " + str(i))
            item7 = editor.model().item(i-1, 0); item7.setCheckState(Qt.Unchecked); i = i + 1
            
            editor.addItem(QIcon("img/icon_yellow.png" ), "Markdown " + str(i))
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
            
            self.font().setFamily("Arial")
            self.font().setPointSize(12)
            
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
        
        def helpMenuClicked_about(self):
            print("about")
            return
        
        def menu_file_clicked_new(self):
            return
        def menu_file_clicked_open(self):
            return
        def menu_file_clicked_save(self):
            return
        def menu_file_clicked_saveas(self):
            return
        def menu_file_clicked_exit(self):
            return
        def menu_edit_clicked_undo(self):
            return
        def menu_edit_clicked_redo(self):
            return
        def menu_edit_clicked_clearall(self):
            return
        
        # --------------------------------------------------------------------
        # add sub menu item to the menuBar menu item.
        # --------------------------------------------------------------------
        def add_menu_item(self, name, shortcut, menu, callback):
            self.menu_action = QWidgetAction(menu)
            
            self.menu_widget = QWidget()
            self.menu_layout = QHBoxLayout(self.menu_widget)
            self.menu_layout.setContentsMargins(0,0,0,0)
            #
            self.menu_icon = QWidget()
            self.menu_icon.setFixedWidth(26)
            self.menu_icon.setContentsMargins(0,0,0,0)
            #
            self.menu_label = QLabel(name)
            self.menu_label.setContentsMargins(0,0,0,0)
            self.menu_label.setStyleSheet(css_menu_label_style)
            self.menu_label.setMinimumWidth(160)
            #
            self.menu_shortcut = QLabel(shortcut)
            self.menu_shortcut.setContentsMargins(0,0,0,0)
            self.menu_shortcut.setMinimumWidth(100)
            self.menu_shortcut.setStyleSheet(css_menu_item)
            
            self.menu_layout.addWidget(self.menu_icon)
            self.menu_layout.addWidget(self.menu_label)
            self.menu_layout.addWidget(self.menu_shortcut)
            
            self.menu_action.setDefaultWidget(self.menu_widget)
            self.menu_action.triggered.connect(callback)
            
            menu.addAction(self.menu_action)
            return
            
        def initUI(self):
            # Layout
            self.setMaximumWidth (800)
            self.setMaximumHeight(600)
            
            self.setContentsMargins(0,0,0,0)
            self.setStyleSheet("padding:0px;margin:0px;")
            
            self.layout = QVBoxLayout()
            self.layout.setContentsMargins(0,0,0,0)
            
            # menu bar
            self.menu_bar = QMenuBar(self)
            self.menu_bar.setStyleSheet(css_menu_item_style)
            
            self.menu_file = self.menu_bar.addMenu("&File")
            self.menu_edit = self.menu_bar.addMenu("&Edit")
            self.menu_help = self.menu_bar.addMenu("&Help")
            
            self.menu_style_bg = "background-color:navy;"
            
            self.menu_file.setStyleSheet(self.menu_style_bg)
            self.menu_edit.setStyleSheet(self.menu_style_bg)
            self.menu_help.setStyleSheet(self.menu_style_bg)
            
            # file menu ...
            self.add_menu_item("New",        "Ctrl+N", self.menu_file, self.menu_file_clicked_new)
            self.add_menu_item("Open",       "Ctrl+O", self.menu_file, self.menu_file_clicked_open)
            self.add_menu_item("Save",       "Ctrl+S", self.menu_file, self.menu_file_clicked_save)
            self.add_menu_item("Save As...", ""      , self.menu_file, self.menu_file_clicked_saveas)
            self.add_menu_item("Exit"      , "Ctrl+X", self.menu_file, self.menu_file_clicked_exit)
            
            # edit menu ...
            self.add_menu_item("Undo"      , ""      , self.menu_edit, self.menu_edit_clicked_undo)
            self.add_menu_item("Redo"      , ""      , self.menu_edit, self.menu_edit_clicked_redo)
            self.add_menu_item("Clear All" , "Ctrl+D", self.menu_edit, self.menu_edit_clicked_clearall)
            
            # help menu ...
            self.add_menu_item("About...", "F1", self.menu_help, self.menu_help_clicked_about)
            
            
            self.layout.addWidget( self.menu_bar )
            self.menu_bar.show()
            
            # tool bar
            self.tool_bar = QToolBar()
            self.tool_bar.setStyleSheet("background-color:gray;font-size:11pt;height:38px;")
            
            self.tool_bar_button_exit = QToolButton()
            self.tool_bar_button_exit.setText("Clear")
            self.tool_bar_button_exit.setCheckable(True)
            
            self.tool_bar_action_new1 = QAction(QIcon("img/floppy-disk.png"), "Flopp", self)
            self.tool_bar_action_new2 = QAction(QIcon("img/floppy-disk.png"), "Flopp", self)
            self.tool_bar_action_new3 = QAction(QIcon("img/floppy-disk.png"), "Flopp", self)
            
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
            
            self.side_btn1.setStyleSheet("height:56px;width:56px;")
            self.side_btn2.setStyleSheet("height:56px;width:56px;")
            self.side_btn3.setStyleSheet("height:56px;width:56px;")
            
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
            self.tabs.setStyleSheet(css_tabs)
            
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
            #self.tab2_left_layout   = QVBoxLayout(self.tab2)
            
            #self.tab2_fold_text = QLabel('Directory:', self.tab2)
            #self.tab2_file_text = QLabel("File:", self.tab2)
            
            #self.tab2_left_layout.addWidget(self.tab2_fold_text)
            
            self.tab2_file_path = 'topics.txt'
            
            global tab2_tree_view
            tab2_tree_view = QTreeView()
            tab2_tree_view.setStyleSheet(css_model_header)
            self.tab2_tree_model = QStandardItemModel()
            self.tab2_tree_model.setHorizontalHeaderLabels(["Topic name", "ID", "Status", "Help icon", "In Build"])
            tab2_tree_view.setModel(self.tab2_tree_model)
            
            self.tab2_top_layout.addWidget(tab2_tree_view)
            self.populate_tree_view(self.tab2_file_path, "img/open-folder.png")
            
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
            self.tab0_left_layout   = QVBoxLayout()
            
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
            
            self.tab0_file_tree.setStyleSheet(css_model_header)
            
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
            self.tab1_left_layout   = QVBoxLayout()
            self.tab1_middle_layout = QVBoxLayout()
            self.tab1_right_layout  = QVBoxLayout()
            
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
            
            self.tab1_file_tree.setStyleSheet(css_model_header)
            
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
    
    # ------------------------------------------------------------------------
    # inform the user about the rules/license of this application script ...
    # ------------------------------------------------------------------------
    class licenseWindow(QDialog):
        def __init__(self):
            super().__init__()
            
            self.returnCode = 0
            
            self.file_content = ""
            self.file_path = "LICENSE"
            try:
                with open(self.file_path, "r") as file:
                    self.file_content = file.read()
                
            except FileNotFoundError:
                print("error: license file not found.")
                print("abort.")
                sys.exit(EXIT_FAILURE)
                
            except Exception as ex:
                print("error: exception:", ex)
                sys.exit(EXIT_FAILURE)
            
            self.setWindowTitle("LICENSE - Please read, before you start.")
            self.setMinimumWidth(820)
            
            font = QFont("Courier New", 10)
            self.setFont(font)
            
            layout = QVBoxLayout()
            
            button1 = QPushButton("Accept")
            button2 = QPushButton("Decline")
            
            button1.clicked.connect(self.button1_clicked)
            button2.clicked.connect(self.button2_clicked)
            
            textfield = QTextEdit(self)
            textfield.setReadOnly(True)
            
            layout.addWidget(textfield)
            layout.addWidget(button1)
            layout.addWidget(button2)
            
            self.setLayout(layout)
            
            # ---------------------------------------------------------
            # get license to front, before the start shot ...
            # ---------------------------------------------------------
            textfield.setPlainText(self.file_content)
        
        def button1_clicked(self):
            #self.returnCode = 0
            self.close()
        
        def button2_clicked(self):
            #self.returnCode = 1
            #self.close()
            sys.exit(EXIT_FAILURE)

    # ------------------------------------------------------------------------
    # this is our "main" entry point, where the application will start, if you
    # type the name of the script into the console, or by mouse click at the
    # file explorer under a GUI system (Windows) ...
    # ------------------------------------------------------------------------
    if __name__ == '__main__':
        global has_error, result_error
        global app
        
        global conn
        global conn_cursor
        
        has_error    = False
        result_error = 0
        try:
            topic_counter = 1
            
            # ---------------------------------------------------------
            # first, we check the operating system platform:
            # 0 - unknown
            # 1 - Windows
            # 2 - Linux
            # ---------------------------------------------------------
            global os_type, os_type_windows, os_type_linux
            
            os_type_unknown = 0
            os_type_windows = 1
            os_type_linux   = 2
            
            os_type         = os_type_unknown
            # ---------------------------------------------------------
            if platform.system() == "Windows":
                os_type = os_type_windows
            elif platform.system() == "Linux":
                os_type = os_type_linux
            else:
                os_type = os_type_unknown
                if isPythonWindows():
                    if not isApplicationInit():
                        app = QApplication(sys.argv)
                    showApplicationError(__error__os__error)
                elif "python" in __app__exec_name:
                    print(__error__os_error)
                sys.exit(EXIT_FAILURE)
            
            # -----------------------------------------------------
            # show a license window, when readed, and user give a
            # okay, to accept it, then start the application ...
            # -----------------------------------------------------
            app = QApplication(sys.argv)
            
            license_window = licenseWindow()
            license_window.exec_()
            
            
            # ---------------------------------------------------------
            # when config.ini does not exists, then create a small one:
            # ---------------------------------------------------------
            if not os.path.exists(__app__config_ini):
                with open(__app__config_ini, "w", encoding="utf-8") as output_file:
                    content = (""
                    + "[common]\n"
                    + "language = en_us\n")
                    output_file.write(content)
                    output_file.close()
                    ini_lang = "en_us" # default is english; en_us
            else:
                config = configparser.ConfigParser()
                config.read(__app__config_ini)
                ini_lang = config.get("common", "language")
            
            tr = handle_language(ini_lang)
            if not tr == None:
                tr  = tr.gettext
            
            # ---------------------------------------------------------
            # combine the puzzle names, and folders ...
            # ---------------------------------------------------------
            po_file_name = ("./locales/"
                + f"{ini_lang}"    + "/LC_MESSAGES/"
                + f"{__app__name}" + ".po")
            
            print("po: " + po_file_name)
            if not os.path.exists(convertPath(po_file_name)):
                print(__error__locales_error)
                sys.exit(EXIT_FAILURE)
            
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            time_str = datetime.datetime.now().strftime("%H:%M:%S")
            
            conn = sqlite3.connect("data.db")
            conn_cursor = conn.cursor()
            conn.close()
            
            ex = FileWatcherGUI()
            
            # close tje splash screen ...
            if getattr(sys, 'frozen', False):
                pyi_splash.close()
                
            ex.show()
            
            result_error = app.exec_()
        except Exception as ex:
            s = f"{ex.args}"
            parts = [part.strip() for part in s.split("'") if part.strip()]
            parts.pop( 0)   # delete first element
            parts.pop(-1)   # delete last  element
            
            err = "error: Exception occured: "
            
            if type(ex) == AttributeError:
                err += "AttributeError\n"
                err += "class: " + parts[0]+"\n"
                err += "text : " + parts[2]+": "+parts[1]+"\n"
            else:
                err += "type  : " + "default  \n"
            
            print(err)
            result_error = 1
            has_error = True
        finally:
            # ---------------------------------------------------------
            # when all is gone, stop the running script ...
            # ---------------------------------------------------------
            print("Done.")
            sys.exit(result_error)

except ImportError as ex:
    print("error: import module missing: " + f"{ex}")
    sys.exit(EXIT_FAILURE)

# ----------------------------------------------------------------------------
# E O F  -  End - Of - File
# ----------------------------------------------------------------------------
