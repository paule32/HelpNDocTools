# ---------------------------------------------------------------------------
# File:   observer.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
# try catch import exceptions ...
# ---------------------------------------------------------------------------
global EXIT_SUCCESS; EXIT_SUCCESS = 0
global EXIT_FAILURE; EXIT_FAILURE = 1

global error_result; error_result = 0

global debugMode

import os            # operating system stuff
import sys

if 'PYTHONHOME' in os.environ:
    del os.environ['PYTHONHOME']
if 'PYTHONPATH' in os.environ:
    del os.environ['PYTHONPATH']

sys.path.append("./interpreter/pascal")
sys.path.append("./tools")

# -----------------------------------------------------------------------
# global used application stuff ...
# -----------------------------------------------------------------------
from appcollection import *

__app__name        = "observer"
__app__config_ini  = ".\\_internal\\observer.ini"

__app__framework   = "PyQt5.QtWidgets.QApplication"
__app__exec_name   = sys.executable

__app__error_level = "0"
__app__comment_hdr = ("# " + misc.StringRepeat("-",78) + "\n")


global topic_counter
global css_model_header, css_tabs, css__widget_item, css_button_style

if getattr(sys, 'frozen', False):
    import pyi_splash

# ------------------------------------------------------------------------
# branding water marks ...
# ------------------------------------------------------------------------
__version__ = "Version 0.0.1"
__authors__ = "paule32"

__date__    = "2024-01-04"

debugMode = True

# ------------------------------------------------------------------------
# when the user start the application script under Windows 7 and higher:
# ------------------------------------------------------------------------
try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'kallup-nonprofit.helpndoc.observer.1'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    print("windll error")

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
__locale__    = ".\\_internal\\locales"
__locale__enu = "en_us"
__locale__deu = "de_de"

basedir = os.path.dirname(__file__)

# ------------------------------------------------------------------------
# style sheet definition's:
# ------------------------------------------------------------------------
css_model_header = "QHeaderView::section{background-color:lightblue;color:black;font-weight:bold;}"

css_combobox_style = (""
    + "font-family:'Arial';font-size:12pt;height:30px;"
    + "font-weight:600;background-color:yellow;"
    )
    
# ------------------------------------------------------------------------
# date / time week days
# ------------------------------------------------------------------------
class Weekday:
    def __init__(self):
        self.MONDAY    = 1
        self.TUESDAY   = 2
        self.WEDNESDAY = 3
        self.THURSDAY  = 4
        self.FRIDAY    = 5
        self.SATURDAY  = 6
        self.SUNDAY    = 7
    
    def today(cls):
        print('today is %s' % cls(date.today().isoweekday()).name)

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
                _ = gettext.translation(
                __app__name,
                localedir=__locale__,
                languages=[__locale__enu])  # english
            elif lang.lower() == __locale__deu:
                _ = gettext.translation(
                __app__name,
                localedir=__locale__,
                languages=[__locale__deu])  # german
        elif system_lang.lower() == __locale__deu:
            if lang.lower() == __locale__deu:
                _ = gettext.translation(
                __app__name,
                localedir=__locale__,
                languages=[__locale__deu])  # german
            elif lang.lower() == __locale__enu:
                _ = gettext.translation(
                __app__name,
                localedir=__locale__,
                languages=[__locale__enu])  # english
        else:
            _ = gettext.translation(
            __app__name,
            localedir=__locale__,
            languages=[__locale__enu])  # fallback - english
        
        _.install()
        return _
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

# ------------------------------------------------------------------------
# custom widget for QListWidgetItem element's ...
# ------------------------------------------------------------------------
class customQListWidgetItem(QListWidgetItem):
    def __init__(self, name, parent):
        super().__init__()
        
        self.name = name
        self.parent = parent
        
        element = QListWidgetItem(name, parent)
        
        self.setSizeHint(element.sizeHint())
        self.setData(0, self.name)

# ------------------------------------------------------------------------
#
# ------------------------------------------------------------------------
class myLineEdit(QLineEdit):
    def __init__(self, name=""):
        super().__init__()
        self.name = name
        self.init_ui()
    
    def init_ui(self):
        self.setText(self.name)
        self.cssColor = "QLineEdit{background-color:white;}QLineEdit:hover{background-color:yellow;}"
        self.setStyleSheet(self.cssColor)
    
# ------------------------------------------------------------------------
#
# ------------------------------------------------------------------------
class myTextEdit(QTextEdit):
    def __init__(self, name=""):
        super().__init__()
        self.name = name
        self.cssColor = "QTextEdit{background-color:#bdbfbf;}QTextEdit:hover{background-color:yellow;}"
        self.setStyleSheet(self.cssColor)
        self.setText(self.name)
    
    def mousePressEvent(self, event):
        self.anchor = self.anchorAt(event.pos())
        if self.anchor:
            QApplication.setOverrideCursor(Qt.PointingHandCursor)
    
    def mouseReleaseEvent(self, event):
        if self.anchor:
            QDesktopServices.openUrl(QUrl(self.anchor))
            QApplication.setOverrideCursor(Qt.ArrowCursor)
            self.anchor = None

class myCustomLabel(QLabel):
    def __init__(self, text, helpID, helpText):
        super().__init__(text)
        
        self.helpID     = helpID
        self.helpText   = helpText
        
        self.helpAnchor = "pupu"
    
    def enterEvent(self, event):
        sv_help.setText(self.helpText)
    
    def mousePressEvent(self, event):
        QApplication.setOverrideCursor(Qt.PointingHandCursor)
        return
    
    def mouseReleaseEvent(self, event):
        QDesktopServices.openUrl(QUrl(self.helpAnchor))
        QApplication.setOverrideCursor(Qt.ArrowCursor)
        return

# ------------------------------------------------------------------------
# create a scroll view for the mode tab on left side of application ...
# ------------------------------------------------------------------------
class myCustomScrollArea(QScrollArea):
    def __init__(self, name):
        super().__init__()
        
        self.name = name
        self.font = QFont("Arial")
        self.font.setPointSize(10)
        
        self.type_label        = 1
        self.type_edit         = 2
        self.type_spin         = 3
        self.type_combo_box    = 4
        self.type_check_box    = 5
        self.type_push_button  = 6
        self.type_radio_button = 7
        
        font_primary   = "Consolas"
        font_secondary = "Courier New"
        
        self.font_a = QFont("Consolas"); self.font_a.setPointSize(11)
        self.font_b = QFont("Arial");    self.font_a.setPointSize(10)
        
        self.font_a.setFamily(font_primary)
        font_id = QFontDatabase.addApplicationFont(self.font_a.family())
        if font_id != -1:
            self.font_a.setFamily(font_primary)
            self.font_a.setPointSize(11)
        else:
            self.font_a.setFamily(font_secondary)
            self.font_a.setPointSize(11)
        
        self.supported_langs = _("supported_langs")
        
        self.content_widget = QWidget(self)
        self.content_widget.setMinimumHeight(self.height()-150)
        self.content_widget.setMinimumWidth (self.width()-50)
        self.content_widget.setFont(self.font)
        
        self.layout = QVBoxLayout(self.content_widget)
        self.layout.setAlignment(Qt.AlignTop)
        self.label_1 = QLabel(self.name)
        
        self.layout.addWidget(self.label_1)
        self.content_widget.setLayout(self.layout)
        
        self.setWidgetResizable(False)
        self.setWidget(self.content_widget)
    
    def setName(self, name):
        self.name = name
        self.label_1.setText(self.name)
    
    def setElementBold(self, w):
        self.font.setBold(True); w.setFont(self.font)
        self.font.setBold(False)
        
    def addPushButton(self, text, l = None):
        w = QPushButton(text)
        w.setFont(self.font_a)
        w.font().setPointSize(14)
        w.font().setBold(True)
        w.setMinimumWidth(32)
        w.setMinimumHeight(32)
        if not l == None:
            l.addWidget(w)
        else:
            self.layout.addWidget(w)
        return w
    
    def addCheckBox(self, text, bold=False):
        w = QCheckBox(text)
        if bold == True:
            self.setElementBold(w)
        else:
            w.setFont(self.font)
        self.layout.addWidget(w)
        return w
    
    def addRadioButton(self, text):
        w = QRadioButton(text)
        w.setFont(self.font)
        self.layout.addWidget(w)
        return w
    
    def addFrame(self, lh = None):
        w = QFrame()
        w.setFrameShape (QFrame.HLine)
        w.setFrameShadow(QFrame.Sunken)
        if not lh == None:
            lh.addWidget(w)
        else:
            self.layout.addWidget(w)
        return w
    
    def addHelpLabel(self, text, helpID, helpText, lh=None):
        w = myCustomLabel( text, helpID, helpText)
        if not lh == None:
            w.setFont(self.font_a)
            lh.addWidget(w)
        else:
            self.layout.addWidget(w)
        return w
    
    def addLabel(self, text, bold=False, lh=None):
        w = QLabel(text)
        if bold == True:
            self.setElementBold(w)
        else:
            w.setFont(self.font)
        if not lh == None:
            w.setFont(self.font_a)
            lh.addWidget(w)
        else:
            self.layout.addWidget(w)
        return w
    
    def addLineEdit(self, text = "", lh = None):
        w = myLineEdit(text)
        w.setMinimumHeight(21)
        w.setFont(self.font_a)
        if not lh == None:
            lh.addWidget(w)
        else:
            self.layout.addWidget(w)
        return w
    
    def addElements(self, elements, hid):
        for i in range(0, len(elements)):
            lv_0 = QVBoxLayout()
            lh_0 = QHBoxLayout()
            
            # -----------------------------------------
            # the help string for a doxygen tag ...
            # -----------------------------------------
            helpID   = hid + i + 1
            helpText = _("h" + f"{helpID:04X}")
            
            vw_1 = self.addHelpLabel(   \
                elements[i][0], \
                helpID,         \
                helpText,       \
                lh_0)
            vw_1.setMinimumHeight(14)
            vw_1.setMinimumWidth(200)
            
            if elements[i][1] == self.type_edit:
                self.addLineEdit("",lh_0)
                                    
                if elements[i][3] == 1:
                    self.addPushButton("+",lh_0)
                    
                elif elements[i][3] == 3:
                    self.addPushButton("+",lh_0)
                    self.addPushButton("-",lh_0)
                    self.addPushButton("R",lh_0)
                    
                    vw_3 = myTextEdit()
                    vw_3.setFont(self.font_a)
                    vw_3.setMinimumHeight(96)
                    vw_3.setMaximumHeight(96)
                    lv_0.addWidget(vw_3)
            
            elif elements[i][1] == self.type_check_box:
                vw_2 = QCheckBox()
                vw_2.setMinimumHeight(21)
                vw_2.setFont(self.font_a)
                vw_2.setChecked(elements[i][4])
                lh_0.addWidget(vw_2)
            
            elif elements[i][1] == self.type_combo_box:
                vw_2 = QComboBox()
                vw_2.setMinimumHeight(26)
                vw_2.setFont(self.font)
                vw_2.font().setPointSize(14)
                lh_0.addWidget(vw_2)
                
                if elements[i][3] == 4:
                    data = json.loads(self.supported_langs)
                    elements[i][4] = data
                    for j in range(0, len(data)):
                        img = ".\\_internal\\img\\flag_"  \
                        + elements[i][4][j] \
                        + ".png".lower()
                        vw_2.insertItem(0, elements[i][4][j])
                        vw_2.setItemIcon(0, QIcon(os.path.join(basedir,"img",img)))
                
                elif elements[i][3] == 2:
                    for j in range(0, len(elements[i][4])):
                        vw_2.addItem(elements[i][4][j])
            
            elif elements[i][1] == self.type_spin:
                vw_2 = QSpinBox()
                vw_2.setFont(self.font_a)
                vw_2.setMinimumHeight(21)
                lh_0.addWidget(vw_2)
            
            lv_0.addLayout(lh_0)
            self.layout.addLayout(lv_0)

# ------------------------------------------------------------------------
# create a scroll view for the project tab on left side of application ...
# ------------------------------------------------------------------------
class customScrollView_1(myCustomScrollArea):
    def __init__(self, name="uuuu"):
        super().__init__(name)
        
        self.name = name
        self.init_ui()
    
    def init_ui(self):
        content_widget = QWidget(self)
        content_widget.setMaximumWidth(500)
        
        layout = QVBoxLayout(content_widget)
        layout.setAlignment(Qt.AlignLeft)
        
        font = QFont("Arial")
        font.setPointSize(10)
        
        w_layout_0 = QHBoxLayout()
        w_layout_0.setAlignment(Qt.AlignLeft)
        widget_1_label_1 = self.addLabel("Provide some informations about the Project you are documenting", True)
        widget_1_label_1.setMinimumWidth(250)
        widget_1_label_1.setMaximumWidth(450)
        w_layout_0.addWidget(widget_1_label_1)
        layout.addLayout(w_layout_0)
        
        h_layout_1 = QHBoxLayout()
        h_widget_1 = QWidget()
        #h_widget_1.setMinimumWidth(300)
        
        v_layout_1 = QVBoxLayout()
        v_widget_1 = QWidget()
        
        l_label_1 = self.addLabel("Project name:"           , False, v_layout_1)
        l_label_2 = self.addLabel("Project author:"         , False, v_layout_1)
        l_label_3 = self.addLabel("Project version or id:  ", False, v_layout_1)
        
        l_label_1.setFont(font)
        l_label_2.setFont(font)
        l_label_3.setFont(font)
        ##
        v_layout_2 = QVBoxLayout()
        v_widget_2 = QWidget()
        
        e_field_1 = self.addLineEdit("", v_layout_2)
        e_field_2 = self.addLineEdit("", v_layout_2)
        e_field_3 = self.addLineEdit("", v_layout_2)
        
        ##
        h_layout_1.addLayout(v_layout_1)
        h_layout_1.addLayout(v_layout_2)
        
        layout.addLayout(h_layout_1)
        
        
        
        layout_4 = QHBoxLayout()
        layout_4.setAlignment(Qt.AlignLeft)
        widget_4_label_1 = self.addLabel("Project logo:", False, layout_4)
        widget_4_label_1.setFont(font)
        widget_4_label_1.setMaximumWidth(160)
        layout_4.addWidget(widget_4_label_1)
        #
        widget_4_pushb_1 = self.addPushButton("Select", layout_4)
        widget_4_pushb_1.setMinimumHeight(32)
        widget_4_pushb_1.setMinimumWidth(84)
        widget_4_pushb_1.setMaximumWidth(84)  ; font.setBold(True)
        widget_4_pushb_1.setFont(font)        ; font.setBold(False)
        #
        widget_4_licon_1 = self.addLabel("", False, layout_4)
        widget_4_licon_1.setPixmap(QIcon(os.path.join(basedir,".\\_internal\\img","floppy-disk.png")).pixmap(42,42))
        #
        layout.addLayout(layout_4)
        
        layout_5 = QHBoxLayout()
        layout_5.setAlignment(Qt.AlignLeft)
        frame_5 = self.addFrame(layout_5)
        frame_5.setMinimumWidth(460)
        frame_5.setMaximumWidth(460)
        layout_5.addWidget(frame_5)
        #
        layout.addLayout(layout_5)
        
        
        layout_6 = QHBoxLayout()
        layout_6.setAlignment(Qt.AlignLeft)
        widget_6_label_1 = self.addLabel("Source dir:", False, layout_6)
        widget_6_label_1.setMinimumWidth(100)
        widget_6_label_1.setMaximumWidth(100)
        widget_6_label_1.setFont(font)
        #
        widget_6_edit_1  = self.addLineEdit("E:\\temp\\src", layout_6)
        widget_6_edit_1.setMinimumWidth(280)
        widget_6_edit_1.setMaximumWidth(280)
        widget_6_edit_1.setFont(font)
        #
        widget_6_pushb_1 = self.addPushButton("Select", layout_6)
        widget_6_pushb_1.setMinimumHeight(40)
        widget_6_pushb_1.setMaximumHeight(40)
        widget_6_pushb_1.setMinimumWidth(84)
        widget_6_pushb_1.setMaximumWidth(84) ; font.setBold(True)
        widget_6_pushb_1.setFont(font)       ; font.setBold(False)
        ##
        layout.addLayout(layout_6)
        
        layout_7 = QHBoxLayout()
        layout_7.setAlignment(Qt.AlignLeft)
        widget_7_label_1 = self.addLabel("Destination dir:", False, layout_7)
        widget_7_label_1.setMinimumWidth(100)
        widget_7_label_1.setMaximumWidth(100)
        widget_7_label_1.setFont(font)
        #
        widget_7_edit_1  = self.addLineEdit("E:\\temp\\src\\html", layout_7)
        widget_7_edit_1.setMinimumWidth(280)
        widget_7_edit_1.setMaximumWidth(280)
        widget_7_edit_1.setFont(font)
        #
        widget_7_pushb_1 = self.addPushButton("Select", layout_7)
        widget_7_pushb_1.setMinimumHeight(40)
        widget_7_pushb_1.setMaximumHeight(40)
        widget_7_pushb_1.setMinimumWidth(84)
        widget_7_pushb_1.setMaximumWidth(84) ; font.setBold(True)
        widget_7_pushb_1.setFont(font)       ; font.setBold(False)
        ##
        layout.addLayout(layout_7)
        
        
        layout_61 = QHBoxLayout()
        layout_61.setAlignment(Qt.AlignLeft)
        frame_61 = self.addFrame(layout_61)
        frame_61.setMinimumWidth(460)
        frame_61.setMaximumWidth(460)
        layout_61.addWidget(frame_61)
        #
        layout.addLayout(layout_61)
        
        
        layout_9 = QHBoxLayout()
        layout_9.setAlignment(Qt.AlignLeft)
        widget_9_checkbutton_1 = self.addCheckBox("Scan recursive")
        widget_9_checkbutton_1.setMaximumWidth(300)
        widget_9_checkbutton_1.setFont(font)
        layout_9.addWidget(widget_9_checkbutton_1)
        layout.addLayout(layout_9)
        
        layout_10 = QVBoxLayout()
        widget_10_button_1 = QPushButton("Convert" ,self); widget_10_button_1.setStyleSheet(css_button_style)
        widget_10_button_2 = QPushButton("HelpNDoc",self); widget_10_button_2.setStyleSheet(css_button_style)
        #
        layout_10.addWidget(widget_10_button_1)
        layout_10.addWidget(widget_10_button_2)
        #
        layout.addLayout(layout_10)
        
        self.setWidgetResizable(False)
        self.setWidget(content_widget)
    
    def btn_clicked_3(self):
        print("HelpNDoc")

class customScrollView_2(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        
        label_2 = self.addLabel(_("opti00"), True)
        label_2.setMinimumHeight(30)
        label_2.setMinimumWidth(200)
        
        self.addRadioButton(_("opti01"))
        self.addRadioButton(_("opti02"))
        self.addCheckBox   (_("opti03"))
        
        self.addFrame()
        
        self.addLabel("Select programming language to optimize the results for:", True)
        
        for x in range(2,9):
            self.addRadioButton(_("opti0" + str(x+1)))

# ------------------------------------------------------------------------
# create a scroll view for the output tab on left side of application ...
# ------------------------------------------------------------------------
class customScrollView_3(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        
        self.addLabel("Select the output format(s) to generate:", True)
        
        # HTML
        self.addCheckBox("HTML", True)
        #
        self.addRadioButton("plain HTML")
        self.addRadioButton("with navigation Panel")
        self.addRadioButton("prepare for compressed HTML .chm")
        self.addCheckBox("with search function")
        
        self.addFrame()
        
        # LaTeX
        self.addCheckBox("LaTeX", True)
        #
        self.addRadioButton("an intermediate format for hypter-linked PDF")
        self.addRadioButton("an intermediate format for PDF")
        self.addRadioButton("an intermediate format for PostScript")
        
        self.addFrame()
        
        # misc
        self.addCheckBox("Man pages")
        self.addCheckBox("Rich Text Format - RTF")
        self.addCheckBox("XML")
        self.addCheckBox("DocBook")

# ------------------------------------------------------------------------
# create a scroll view for the diagrams tab on left side of application ...
# ------------------------------------------------------------------------
class customScrollView_4(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        
        self.addLabel("Diagrams to generate:", True)
        
        self.addRadioButton("No diagrams")
        self.addRadioButton("Text only")
        self.addRadioButton("Use built-in diagram generator")
        self.addRadioButton("Use Dot-Tool from the GrappVz package")
        
        self.addFrame()
        
        self.addLabel("Dot graphs to generate:", True)
        
        self.addCheckBox("Class graph")
        self.addCheckBox("Colaboration diagram")
        self.addCheckBox("Overall Class hiearchy")
        self.addCheckBox("Include dependcy graphs")
        self.addCheckBox("Included by dependcy graphs")
        self.addCheckBox("Call graphs")
        self.addCheckBox("Called-by graphs")
        

class customScrollView_5(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(2000)
        label_1_elements = [
            # <text>,                  <type 1>,             <help>, <type 2>,  <list 1>
            ["DOXYFILE_ENCODING",      self.type_edit,       100, 0],
            
            ["PROJECT_NAME",           self.type_edit,       101, 0, "My Project"],
            ["PROJECT_NUMBER",         self.type_edit,       102, 0],
            ["PROJECT_BRIEF",          self.type_edit,       103, 0],
            ["PROJECT_LOGO",           self.type_edit,       104, 1],
            ["PROJECT_ICON",           self.type_edit,       105, 1],
            
            ["OUTPUT_DIRECTORY",       self.type_edit,       106, 1],
            ["CREATE_SUBDIRS",         self.type_check_box,  107, 0, True],
            ["CREATE_SUBDIRS_LEVEL",   self.type_spin,       108, 0],
            
            ["ALLOW_UNICODE_NAMES",    self.type_check_box,  109, 0, False],
            ["OUTPUT_LANGUAGE",        self.type_combo_box,  110, 4, [] ],
            
            ["BRIEF_MEMBER_DESC",      self.type_check_box,  111, 0, True],
            ["REPEAT_BRIEF",           self.type_check_box,  112, 0, True],
            ["ABBREVIATE_BRIEF",       self.type_edit,       113, 3],
            ["ALWAYS_DETAILED_SEC",    self.type_check_box,  114, 0, True],
            ["INLINE_INHERITED_MEMB",  self.type_check_box,  115, 0, True],
            
            ["FULL_PATH_NAMES",        self.type_check_box,  116, 0, True],
            ["STRIP_FROM_PATH",        self.type_edit,       117, 3],
            ["STRIP_FROM_INC_PATH",    self.type_edit,       118, 3],
            
            ["SHORT_NAMES",            self.type_check_box,  119, 0, False],
            
            ["JAVADOC_AUTOBRIEF",      self.type_check_box,  120, 0, True ],
            ["JAVADOC_BANNER",         self.type_check_box,  121, 0, False],
            
            ["QT_AUTOBRIEF",           self.type_check_box,  122, 0, False],
            
            ["MULTILINE_CPP_IS_BRIEF", self.type_check_box,  123, 0, False],
            ["PYTHON_DOCSTRING",       self.type_check_box,  124, 0, True ],
            ["INHERITED_DOCS",         self.type_check_box,  125, 0, True ],
            ["SEPERATE_MEMBER_PAGES",  self.type_check_box,  126, 0, False],
            
            ["TAB_SIZE",               self.type_spin,       127, 0],
            ["ALIASES",                self.type_edit,       128, 3],
            
            ["OPTIMIZE_OUTPUT_FOR_C",  self.type_check_box,  129, 0, True ],
            ["OPTIMIZE_OUTPUT_JAVA",   self.type_check_box,  130, 0, False],
            ["OPTIMIZE_FOR_FORTRAN",   self.type_check_box,  131, 0, False],
            ["OPTIMIZE_OUTPUT_VHCL",   self.type_check_box,  132, 0, False],
            ["OPTIMIZE_OUTPUT_SLICE",  self.type_check_box,  133, 0, False],
            
            ["EXTERNAL_MAPPING",       self.type_edit,       134, 3],
            
            ["MARKDOWN_SUPPORT",       self.type_check_box,  135, 0, True ],
            ["MARKDOWN_ID_STYLE",      self.type_combo_box,  136, 2, ["DOXYGEN", "CIT"]],
            
            ["TOC_INCLUDE_HEADINGS",   self.type_spin,       137, 0],
            ["AUTOLINK_SUPPORT",       self.type_check_box,  138, 0, True ],
            
            ["BUILTIN_STL_SUPPORT",    self.type_check_box,  139, 0, True ],
            ["CPP_CLI_SUPPORT",        self.type_check_box,  140, 0, True ],
            ["SIP_SUPPORT",            self.type_check_box,  141, 0, False],
            ["IDL_PROPERTY_SUPPORT",   self.type_check_box,  142, 0, True ],
            
            ["DESTRIBUTE_GROUP_DOC",   self.type_check_box,  143, 0, False],
            ["GROUP_NESTED_COMPOUNDS", self.type_check_box,  144, 0, False],
            ["SUBGROUPING",            self.type_check_box,  145, 0, True ],
            
            ["INLINE_GROUPED_CLASSES", self.type_check_box,  146, 0, False],
            ["INLINE_SIMPLE_STRUCTS",  self.type_check_box,  147, 0, False],
            ["TYPEDEF_HIDES_STRUCT",   self.type_check_box,  148, 0, False],
            
            ["LOOKUP_CACHE_SIZE",      self.type_spin,       149, 0],
            ["NUM_PROC_THREADS",       self.type_spin,       150, 0],
            
            ["TIMESTAMP",              self.type_combo_box,  151, 2, ["NO","YES"]]
        ]
        self.addElements(label_1_elements, 0x100)
    
    # ----------------------------------------------
    # show help text when mouse move over the label
    # ----------------------------------------------
    def label_enter_event(self, text):
        sv_help.setText(text)

class customScrollView_6(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1400)
        
        label_1_elements = [
            ["EXTRACT_ALL",              self.type_check_box, 0x200, 0, False ],
            ["EXTRACT_PRIVATE",          self.type_check_box, 0x201, 0, False ],
            ["EXTRACT_PRIV_VIRTUAL",     self.type_check_box, 0x202, 0, False ],
            ["EXTRACT_PACKAGE",          self.type_check_box, 0x203, 0, False ],
            ["EXTRACT_STATIC",           self.type_check_box, 0x204, 0, True  ],
            ["EXTRACT_LOCAL_CLASSES",    self.type_check_box, 0x205, 0, True  ],
            ["EXTRACT_LOCAL_METHODS",    self.type_check_box, 0x206, 0, True  ],
            ["EXTRACT_ANON_NSPACES",     self.type_check_box, 0x207, 0, True  ],
            ["RECURSIVE_UNNAMED_PARAMS", self.type_check_box, 0x208, 0, True  ],
            ["HIDE_UNDOC_MEMBERS",       self.type_check_box, 0x209, 0, False ],
            ["HIDE_UNDOC_CLASSES",       self.type_check_box, 0x20A, 0, False ],
            ["HIDE_FRIEND_COMPOUNDS",    self.type_check_box, 0x20B, 0, False ],
            ["HIDE_IN_BODY_DOCS",        self.type_check_box, 0x20C, 0, False ],
            ["INTERNAL_DOCS",            self.type_check_box, 0x20D, 0, True  ],
            
            ["CASE_SENSE_NAMES",         self.type_combo_box, 0x20E, 2, ["SYSTEM", "NO", "YES"] ],
            
            ["HIDE_SCOPE_NAMES",         self.type_check_box, 0x20E, 0, False ],
            ["HIDE_COMPOUND_REFERENCE",  self.type_check_box, 0x20F, 0, False ],
            
            ["SHOW_HEADERFILE",          self.type_check_box, 0x210, 0, True  ],
            ["SHOW_INCLUDE_FILES",       self.type_check_box, 0x210, 0, True  ],
            
            ["SHOW_GROUPED_MEMB_INC",    self.type_check_box, 0x210, 0, False ],
            ["FORCE_LOCAL_INCLUDES",     self.type_check_box, 0x210, 0, False ],
            ["INLINE_INFO",              self.type_check_box, 0x210, 0, False ],
            ["SORT_MEMBER_DOCS",         self.type_check_box, 0x210, 0, False ],
            ["SORT_BRIEF_DOCS",          self.type_check_box, 0x210, 0, False ],
            ["SORT_MEMBERS_CTORS_1ST",   self.type_check_box, 0x210, 0, False ],
            
            ["SORT_GROUP_NAMES",         self.type_check_box, 0x210, 0, False ],
            ["SORT_BY_SCOPE_NAME",       self.type_check_box, 0x210, 0, False ],
            ["STRICT_PROTO_MATCHING",    self.type_check_box, 0x210, 0, False ],
            
            ["GENERATE_TODOLIST",        self.type_check_box, 0x210, 0, False ],
            ["GENERATE_TESTLIST",        self.type_check_box, 0x210, 0, False ],
            ["GENERATE_BUGLIST",         self.type_check_box, 0x210, 0, False ],
            ["GENERATE_DEPRECATEDLIST",  self.type_check_box, 0x210, 0, False ],
            
            ["ENABLED_SECTIONS",         self.type_edit,      0x210, 3 ],
            ["MAX_INITIALIZER_LINES",    self.type_spin,      0x210, 0 ],
            
            ["SHOW_USED_FILES",          self.type_check_box, 0x210, 0, True  ],
            ["SHOW_FILES",               self.type_check_box, 0x210, 0, True  ],
            ["SHOW_NAMESPACES",          self.type_check_box, 0x210, 0, True  ],
            
            ["FILE_VERSION_FILTER",      self.type_edit,      0x210, 1 ],
            ["LAYOUT_FILE",              self.type_edit,      0x210, 1 ],
            ["CITE_BIB_FILES",           self.type_edit,      0x210, 3 ]
        ]
        self.addElements(label_1_elements, 0x200)

class customScrollView_7(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        label_1_elements = [
            ["QUIET",                    self.type_check_box, 0x300, 0, True  ],
            ["WARNINGS",                 self.type_check_box, 0x200, 0, True  ],
            
            ["WARN_IF_UNDOCUMENTED",     self.type_check_box, 0x200, 0, False ],
            ["WARN_IF_DOC_ERROR",        self.type_check_box, 0x200, 0, True  ],
            ["WARN_IF_INCOMPLETE_DOC",   self.type_check_box, 0x200, 0, True  ],
            
            ["WARN_NO_PARAMDOC",         self.type_check_box, 0x200, 0, False ],
            ["WARN_IF_UNDOC_ENUM_VAL",   self.type_check_box, 0x200, 0, False ],
            
            ["WARN_AS_ERROR",            self.type_spin,      0x200, 0 ],
            
            ["WARN_FORMAT",              self.type_edit,      0x200, 0 ],
            ["WARN_LINE_FORMAT",         self.type_edit,      0x200, 0 ],
            ["WARN_LOGFILE",             self.type_edit,      0x200, 1 ]
        ]
        self.addElements(label_1_elements, 0x0300)

class customScrollView_8(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1700)
        
        label_1_elements = [
            ["INPUT",                  self.type_edit,      0x400, 3],
            ["INPUT_ENCODING",         self.type_edit,      0x400, 0],
            ["INPUT_FILE_ENCODING",    self.type_edit,      0x400, 1],
            ["FILE_PATTERNS",          self.type_edit,      0x400, 3],
            ["RECURSIVE",              self.type_check_box, 0x400, 0, True  ],
            ["EXCLUDE",                self.type_edit,      0x400, 3],
            ["EXCLUDE_SYMLINKS",       self.type_check_box, 0x400, 0, False ],
            ["EXCLUDE_PATTERNS",       self.type_edit,      0x400, 3],
            ["EXCLUDE_SYMBOLS",        self.type_edit,      0x400, 3],
            ["EXAMPLE_PATH",           self.type_edit,      0x400, 3],
            ["EXAMPLE_PATTERNS",       self.type_edit,      0x400, 3],
            ["EXAMPLE_RECURSIVE",      self.type_edit,      0x400, 0, False ],
            ["IMAGE_PATH",             self.type_edit,      0x400, 3],
            ["INPUT_FILTER",           self.type_edit,      0x400, 1],
            ["FILTER_PATTERNS",        self.type_edit,      0x400, 3],
            ["FILTER_SOURCE_FILES",    self.type_check_box, 0x400, 0, False ],
            ["FILTER_SOURCE_PATTERNS", self.type_edit,      0x400, 3],
            ["USE_MDFILE_AS_MAINPAGE", self.type_edit,      0x400, 0],
            ["FORTRAN_COMMENT_AFTER",  self.type_spin,      0x400, 0]
        ]
        self.addElements(label_1_elements, 0x0400)

class customScrollView_9(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(560)
        
        label_1_elements = [
            ["SOURCE_BROWSER",          self.type_check_box, 0x500, 0, True  ],
            ["INLINE_SOURCES",          self.type_check_box, 0x200, 0, False ],
            ["STRIP_CODE_COMMENTS",     self.type_check_box, 0x200, 0, False ],
            
            ["REFERENCED_BY_RELATION",  self.type_check_box, 0x200, 0, True  ],
            ["REFERENCES_RELATION",     self.type_check_box, 0x200, 0, True  ],
            ["REFERENCES_LINK_SOURCE",  self.type_check_box, 0x200, 0, True  ],
            
            ["SOURCE_TOOLTIPS",         self.type_check_box, 0x200, 0, True  ],
            ["USE_HTAGS",               self.type_check_box, 0x200, 0, False ],
            ["VERBATIM_HEADERS",        self.type_check_box, 0x200, 0, True  ],
            
            ["CLANG_ASSISTED_PARSING",  self.type_check_box, 0x200, 0, False ],
            ["CLANG_ADD_INC_PATHS",     self.type_check_box, 0x200, 0, False ],
            ["CLANG_OPTIONS",           self.type_edit     , 0x200, 3 ],
            ["CLANG_DATABASE_PATH",     self.type_edit     , 0x200, 1 ]
        ]
        self.addElements(label_1_elements, 0x0500)

class customScrollView_10(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        label_1_elements = [
            ["ALPHABETICAL_INDEX", self.type_check_box, 0x600, 0, True ],
            ["IGNORE_PREFIX",      self.type_edit,      0x601, 3 ]
        ]
        self.addElements(label_1_elements, 0x0600)

class customScrollView_11(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(2380)
        
        label_1_elements = [
            ["GENERATE_HTML",          self.type_check_box, 0x200, 0, True  ],
            ["HTML_OUTPUT",            self.type_edit,      0x200, 1 ],
            ["HTML_FILE_EXTENSION",    self.type_edit,      0x200, 0 ],
            
            ["HTML_HEADER",            self.type_edit,      0x200, 1 ],
            ["HTML_FOOTER",            self.type_edit,      0x200, 1 ],
            
            ["HTML_STYLESHEET",        self.type_edit,      0x200, 1 ],
            ["HTML_EXTRA_STYLESHEET",  self.type_edit,      0x200, 3 ],
            ["HTML_EXTRA_FILES",       self.type_edit,      0x200, 3 ],
            
            ["HTML_COLORSTYLE",        self.type_combo_box, 0x200, 2, [ "LIGHT", "DARK", "AUTO_LIGHT", "AUTO_DARK", "TOOGLE" ] ],
            ["HTML_COLORSTYLE_HUE",    self.type_spin,      0x200, 0 ],
            ["HTML_COLORSTYLE_SAT",    self.type_spin,      0x200, 0 ],
            ["HTML_COLORSTYLE_GAMMA",  self.type_spin,      0x200, 0 ],
            ["HTML_DYNAMIC_MENUS",     self.type_check_box, 0x200, 0, True  ],
            ["HTML_DYNAMIC_SECTIONS",  self.type_check_box, 0x200, 0, False ],
            
            ["HTML_CODE_FOLDING",      self.type_check_box, 0x200, 0, True  ],
            ["HTML_COPY_CLIPBOARD",    self.type_check_box, 0x200, 0, True  ],
            ["HTML_PROJECT_COOKIE",    self.type_edit,      0x200, 0 ],
            ["HTML_INDEX_NUM_ENTRIES", self.type_spin,      0x200, 0 ],
            
            ["GENERATE_DOCSET",        self.type_check_box, 0x200, 0, False ],
            ["DOCSET_FEEDNAME",        self.type_edit,      0x200, 0 ],
            ["DOCSET_FEEDURL",         self.type_edit,      0x200, 0 ],
            ["DOCSET_BUNDLE_ID",       self.type_edit,      0x200, 0 ],
            ["DOCSET_PUBLISHER_ID",    self.type_edit,      0x200, 0 ],
            ["DOCSET_PUBLISHER_NAME",  self.type_edit,      0x200, 0 ],
            
            ["GENERATE_HTMLHELP",      self.type_check_box, 0x200, 0, True  ],
            ["CHM_FILE",               self.type_edit,      0x200, 1 ],
            ["HHC_LOCATION",           self.type_edit,      0x200, 1 ],
            ["GENERATE_CHI",           self.type_check_box, 0x200, 0, False ],
            ["CHM_INDEX_ENCODING",     self.type_edit,      0x200, 0 ],
            ["BINARY_TOC",             self.type_check_box, 0x200, 0, False ],
            ["TOC_EXPAND",             self.type_check_box, 0x200, 0, False ],
            ["SITEMAP_URL",            self.type_edit,      0x200, 0 ],
            
            ["GENERATE_QHP",           self.type_check_box, 0x200, 0, False ],
            ["QCH_FILE",               self.type_edit,      0x200, 1 ],
            ["QHP_VIRTUAL_FOLDER",     self.type_edit,      0x200, 0 ],
            ["QHP_CUST_FILTER_NAME",   self.type_edit,      0x200, 0 ],
            ["QHP_CUST_FILTER_ATTRS",  self.type_edit,      0x200, 0 ],
            ["QHP_SECT_FILTER_ATTRS",  self.type_edit,      0x200, 0 ],
            ["QHG_LOCATION",           self.type_edit,      0x200, 1 ],
            
            ["GENERATE_ECLIPSEHELP",   self.type_check_box, 0x200, 0, False ],
            ["ECLIPSE_DOC_ID",         self.type_edit,      0x200, 0 ],
            ["DISABLE_INDEX",          self.type_check_box, 0x200, 0, False ],
            
            ["GENERATE_TREEVIEW",      self.type_check_box, 0x200, 0, True  ],
            ["FULL_SIDEBAR",           self.type_check_box, 0x200, 0, False ],
            
            ["ENUM_VALUES_PER_LINE",   self.type_spin,      0x200, 0 ],
            ["TREEVIEW_WIDTH",         self.type_spin,      0x200, 0 ],
            
            ["EXT_LINKS_IN_WINDOW",    self.type_check_box, 0x200, 0, False ],
            ["OBFUSCATE_EMAILS",       self.type_check_box, 0x200, 0, True  ],
            
            ["HTML_FORMULA_FORMAT",    self.type_combo_box, 0x200, 2, [ "png", "svg" ] ],
            ["FORMULA_FONTSIZE",       self.type_spin,      0x200, 0 ],
            ["FORMULA_MACROFILE",      self.type_edit,      0x200, 1 ],
            
            ["USE_MATHJAX",            self.type_check_box, 0x200, 0, False ],
            ["MATHJAX_VERSION",        self.type_combo_box, 0x200, 2, [ "MathJax_2", "MathJax_3" ] ],
            ["MATHJAX_FORMAT",         self.type_combo_box, 0x200, 2, [ "HTML + CSS", "NativeXML", "chtml", "SVG" ] ],
            
            ["MATHJAX_RELPATH",        self.type_edit,      0x200, 1 ],
            ["MATHJAX_EXTENSIONS",     self.type_edit,      0x200, 3 ],
            ["MATHJAX_CODEFILE",       self.type_edit,      0x200, 0 ],
            
            ["SEARCHENGINE",           self.type_check_box, 0x200, 0, False ],
            ["SERVER_BASED_SEARCH",    self.type_check_box, 0x200, 0, False ],
            ["EXTERNAL_SEARCH",        self.type_check_box, 0x200, 0, False ],
            ["SEARCHENGINE_URL",       self.type_edit,      0x200, 0 ],
            ["SEARCHDATA_FILE",        self.type_edit,      0x200, 1 ],
            ["EXTERNAL_SEARCH_ID",     self.type_edit,      0x200, 0 ],
            ["EXTRA_SEARCH_MAPPINGS",  self.type_edit,      0x200, 3 ]
        ]
        self.addElements(label_1_elements, 0x0700)

class customScrollView_12(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1000)
        
        label_1_elements = [
            ["GENERATE_LATEX",          self.type_check_box, 0x200, 0, False ],
            ["LATEX_OUTPUT",            self.type_edit,      0x200, 1 ],
            ["LATEX_CMD_NAMET",         self.type_edit,      0x200, 1 ],
            ["LATEX_MAKEINDEX_CMDT",    self.type_edit,      0x200, 0 ],
            ["COMPACT_LATEX",           self.type_check_box, 0x200, 0, False ],
            ["PAPER_TYPE",              self.type_combo_box, 0x200, 2, [ "a4", "letter", "executive" ] ],
            ["EXTRA_PACKAGES",          self.type_edit,      0x200, 3 ],
            ["LATEX_HEADER",            self.type_edit,      0x200, 1 ],
            ["LATEX_FOOTER",            self.type_edit,      0x200, 1 ],
            ["LATEX_EXTRA_STYLESHEET",  self.type_edit,      0x200, 3 ],
            ["LATEX_EXTRA_FILES",       self.type_edit,      0x200, 3 ],
            ["PDF_HYPERLINKS",          self.type_check_box, 0x200, 0, True  ],
            ["USE_PDFLATEX",            self.type_check_box, 0x200, 0, True  ],
            ["LATEX_BATCHMODE",         self.type_combo_box, 0x200, 2, [ "NO", "YWS", "BATCH", "NON-STOP", "SCROLL", "ERROR_STOP" ] ],
            ["LATEX_HIDE_INDICES",      self.type_check_box, 0x200, 0, False ],
            ["LATEX_BIB_STYLE",         self.type_edit,      0x200, 0 ],
            ["LATEX_EMOJI_DIRECTORY",   self.type_edit,      0x200, 1 ]
        ]
        self.addElements(label_1_elements, 0x0800)

class customScrollView_13(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        label_1_elements = [
            ["GENERATE_RTF",         self.type_check_box, 0x200, 0, False ],
            ["RTF_OUTPUT",           self.type_edit,      0x200, 1 ],
            ["COMPACT_RTF",          self.type_check_box, 0x200, 0, False ],
            ["RTF_HYPERLINKS",       self.type_check_box, 0x200, 0, False ],
            ["RTF_STYLESHEET_FILE",  self.type_edit,      0x200, 1 ],
            ["RTF_EXTENSIONS_FILE",  self.type_edit,      0x200, 1 ]
        ]
        self.addElements(label_1_elements, 0x0900)

class customScrollView_14(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        label_1_elements = [
            ["GENERATE_MAN",   self.type_check_box, 0x200, 0, False ],
            ["MAN_OUTPUT",     self.type_edit,      0x200, 1 ],
            ["MAN_EXTENSION",  self.type_edit,      0x200, 0 ],
            ["MAN_SUBDIR",     self.type_edit,      0x200, 0 ],
            ["MAN_LINKS",      self.type_check_box, 0x200, 0, False ],
        ]
        self.addElements(label_1_elements, 0x0A00)

class customScrollView_15(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        label_1_elements = [
            ["GENERATE_XML",            self.type_check_box, 0x200, 0, False ],
            ["XML_OUTPUT",              self.type_edit,      0x200, 1 ],
            ["XML_PROGRAMLISTING",      self.type_check_box, 0x200, 0, False ],
            ["XML_NS_MEMB_FILE_SCOPE",  self.type_check_box, 0x200, 0, False ]
        ]
        self.addElements(label_1_elements, 0x0B00)

class customScrollView_16(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1400)
        
        label_1_elements = [
            ["GENERATE_DOCBOOK",  self.type_check_box, 0x200, 0, False ],
            ["DOCBOOK_OUTPUT",    self.type_edit,      0x200, 1 ],
        ]
        self.addElements(label_1_elements, 0x0C00)

class customScrollView_17(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        label_1_elements = [
            ["GENERATE_AUTOGEN_DEF",  self.type_check_box, 0x200, 0, False ]
        ]
        self.addElements(label_1_elements, 0x0D00)

class customScrollView_18(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        label_1_elements = [
            ["GENERATE_SQLITE3",     self.type_check_box, 0x200, 0, False ],
            ["SQLITE3_OUTPUT",       self.type_edit,      0x200, 1 ],
            ["SQLITE3_RECREATE_DB",  self.type_check_box, 0x200, 0, True  ],
        ]
        self.addElements(label_1_elements, 0x0E00)

class customScrollView_19(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        label_1_elements = [
            ["GENERATE_PERLMOD",        self.type_check_box, 0x200, 0, False ],
            ["PERLMOD_LATEX",           self.type_check_box, 0x200, 0, False ],
            ["PERLMOD_PRETTY",          self.type_check_box, 0x200, 0, False ],
            ["PERLMOD_MAKEVAR_PREFIX",  self.type_edit,      0x200, 1 ]
        ]
        self.addElements(label_1_elements, 0x0F00)

class customScrollView_20(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(800)
        
        label_1_elements = [
            ["ENABLE_PREPROCESSING",   self.type_check_box, 0x200, 0, True  ],
            ["MACRO_EXPANSION",        self.type_check_box, 0x200, 0, True  ],
            ["EXPAND_ONLY_PREDEF",     self.type_check_box, 0x200, 0, False ],
            ["SEARCH_INCLUDES",        self.type_check_box, 0x200, 0, False ],
            ["INCLUDE_PATH",           self.type_edit,      0x200, 3 ],
            ["INCLUDE_FILE_PATTERNS",  self.type_edit,      0x200, 3 ],
            ["PREDEFINED",             self.type_edit,      0x200, 3 ],
            ["EXPAND_AS_DEFINED",      self.type_edit,      0x200, 3 ],
            ["SKIP_FUNCTION_MACROS",   self.type_check_box, 0x200, 0, True  ]
        ]
        self.addElements(label_1_elements, 0x1000)

class customScrollView_21(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        label_1_elements = [
            ["TAGFILES",          self.type_edit, 0x200, 3 ],
            ["GENERATE_TAGFILE",  self.type_edit, 0x200, 1 ],
            ["ALLEXTERNALS",      self.type_check_box, 0x200, 0, False ],
            ["EXTERNAL_GROUPS",   self.type_check_box, 0x200, 0, True  ],
            ["EXTERNAL_PAGES",    self.type_check_box, 0x200, 0, True  ]
        ]
        self.addElements(label_1_elements, 0x1100)

class customScrollView_22(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1600)
        
        label_1_elements = [
            ["HIDE_UNDOC_RELATIONS",   self.type_check_box, 0x200, 0, False ],
            ["HAVE_DOT",               self.type_check_box, 0x200, 0, False ],
            ["DOT_NUM_THREADS",        self.type_spin     , 0x200, 0 ],
            
            ["DOT_COMMON_ATTR",        self.type_edit, 0x200, 0 ],
            ["DOT_EDGE_ATTR",          self.type_edit, 0x200, 0 ],
            ["DOT_NODE_ATTR",          self.type_edit, 0x200, 0 ],
            ["DOT_FONTPATH",           self.type_edit, 0x200, 1 ],
            
            ["CLASS_GRAPH",            self.type_combo_box, 0x200, 2, [ "YES", "NO" ] ],
            ["COLLABORATION_GRAPH",    self.type_check_box, 0x200, 0, True  ],
            ["GROUP_GRAPHS",           self.type_check_box, 0x200, 0, True  ],
            ["UML_LOOK",               self.type_check_box, 0x200, 0, False ],
            ["UML_LIMIT_NUM_FIELDS",   self.type_spin     , 0x200, 0 ],
            ["DOT_UML_DETAILS",        self.type_combo_box, 0x200, 2, [ "NO", "YES" ] ],
            ["DOT_WRAP_THRESHOLD",     self.type_spin     , 0x200, 0 ],
            
            ["TEMPLATE_RELATIONS",     self.type_check_box, 0x200, 0, False ],
            ["INCLUDE_GRAPH",          self.type_check_box, 0x200, 0, False ],
            ["INCLUDED_BY_GRAPH",      self.type_check_box, 0x200, 0, False ],
            ["CALL_GRAPH",             self.type_check_box, 0x200, 0, False ],
            ["CALLER_GRAPH",           self.type_check_box, 0x200, 0, False ],
            ["IGRAPHICAL_HIERARCHY",   self.type_check_box, 0x200, 0, False ],
            ["DIRECTORY_GRAPH",        self.type_check_box, 0x200, 0, False ],
            
            ["DIR_GRAPH_MAX_DEPTH",    self.type_spin     , 0x200, 0 ],
            ["DOT_IMAGE_FORMAT",       self.type_combo_box, 0x200, 2, [ "png", "svg" ] ],
            
            ["INTERACTIVE_SVG",        self.type_check_box, 0x200, 0, False ],
            
            ["DOT_PATH",               self.type_edit     , 0x200, 1 ],
            ["DOTFILE_DIRS",           self.type_edit     , 0x200, 3 ],
            
            ["DIA_PATH",               self.type_edit     , 0x200, 1 ],
            ["DIAFILE_DIRS",           self.type_edit     , 0x200, 3 ],
            
            ["PLANTUML_JAR_PATH",      self.type_edit     , 0x200, 1 ],
            ["PLANTUML_CFG_FILE",      self.type_edit     , 0x200, 1 ],
            ["PLANTUML_INCLUDE_PATH",  self.type_edit     , 0x200, 3 ],
            
            ["DOT_GRAPH_MAX_NODES",    self.type_spin     , 0x200, 0 ],
            ["MAX_DOT_GRAPH_DEPTH",    self.type_spin     , 0x200, 0 ],
            
            ["DOT_MULTI_TARGETS",      self.type_check_box, 0x200, 0, False ],
            ["GENERATE_LEGEND",        self.type_check_box, 0x200, 0, False ],
            ["DOT_CLEANUP",            self.type_check_box, 0x200, 0, True  ],
            ["MSCGEN_TOOL",            self.type_edit     , 0x200, 1 ],
            ["MSCFILE_DIRS",           self.type_edit     , 0x200, 3 ]
        ]
        self.addElements(label_1_elements, 0x1200)

class customScrollView_23(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1400)
        
        label_1_elements = [
            ["EXTRACT_ALL",              self.type_check_box, 0x200, 0, False ],
        ]
        self.addElements(label_1_elements, 0x1300)

class customScrollView_24(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1400)
        
        label_1_elements = [
            ["EXTRACT_ALL",              self.type_check_box, 0x200, 0, False ],
        ]
        self.addElements(label_1_elements, 0x1400)

class customScrollView_help(QTextEdit):
    def __init__(self):
        super().__init__()
        
        font = QFont("Arial")
        font.setPointSize(11)
        
        self.setFont(font)
        self.setMinimumHeight(100)
        self.setMaximumHeight(100)

class MyCustomClass():
    def __init__(self, name, number):
        super().__init__()
        
        if number == 1:
            customScrollView_5()

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
        editor.addItem(QIcon(".\\_internal\\img\\icon_white.png" ), "Complete"     )
        editor.addItem(QIcon(".\\_internal\\img\\icon_blue.png"  ), "Needs Review" )
        editor.addItem(QIcon(".\\_internal\\img\\icon_yellow.png"), "In Progress"  )
        editor.addItem(QIcon(".\\_internal\\img\\icon_red.png"   ), "Out of Date"  )
        
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
        editor.addItem(QIcon(".\\_internal\\img\\icon_yellow.png" ), "CHM " + str(i))
        item1 = editor.model().item(i-1, 0); item1.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon(".\\_internal\\img\\icon_yellow.png" ), "HTML " + str(i))
        item2 = editor.model().item(i-1, 0); item2.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon(".\\_internal\\img\\icon_yellow.png" ), "Word " + str(i))
        item3 = editor.model().item(i-1, 0); item3.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon(".\\_internal\\img\\icon_yellow.png" ), "PDF " + str(i))
        item4 = editor.model().item(i-1, 0); item4.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon(".\\_internal\\img\\icon_yellow.png" ), "EPub " + str(i))
        item5 = editor.model().item(i-1, 0); item5.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon(".\\_internal\\img\\icon_yellow.png" ), "Kindle " + str(i))
        item6 = editor.model().item(i-1, 0); item6.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon(".\\_internal\\img\\icon_yellow.png" ), "Qt Help " + str(i))
        item7 = editor.model().item(i-1, 0); item7.setCheckState(Qt.Unchecked); i = i + 1
        
        editor.addItem(QIcon(".\\_internal\\img\\icon_yellow.png" ), "Markdown " + str(i))
        item8 = editor.model().item(i-1, 0); item8.setCheckState(Qt.Unchecked); i = i + 1
        
        return editor

class SpinEditDelegateID(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
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

class FileWatcherGUI(QDialog):
    def __init__(self):
        super().__init__()
        
        global css_menu_item
        global css_menu_label_style
        global css_menu_item_style
        
        css_menu_item_style  = _("css_menu_item_style")
        css_menu_label_style = _("css_menu_label_style")
        css_menu_item        = _("css_menu_item")
        
        self.font = QFont("Arial", 10)
        self.setFont(self.font)
        self.setContentsMargins(0,0,0,0)
        self.setStyleSheet("padding:0px;margin:0px;")
        #self.setStyleSheet("font-family:'Arial';font-size:12pt;")
        
        self.my_list = MyItemRecord(0, QStandardItem(""))
        self.init_ui()
    
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
                print("33333")
                stack[-1].appendRow([new_item, item1, item2, item3, item4])
                stack.append(new_item)
                print("55555")
    
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
        
    def init_ui(self):
        # Layout
        self.setMaximumWidth (936)
        self.setMinimumWidth (936)
        #
        self.setMaximumHeight(730)
        self.setMaximumHeight(730)
        
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
        self.tool_bar.setContentsMargins(0,0,0,0)
        self.tool_bar.setStyleSheet("background-color:gray;font-size:11pt;height:38px;padding:0px;margin:0px;")
        
        self.tool_bar_button_exit = QToolButton()
        self.tool_bar_button_exit.setText("Clear")
        self.tool_bar_button_exit.setCheckable(True)
        
        self.tool_bar_action_new1 = QAction(QIcon(".\\_internal\\img\\floppy-disk.png"), "Flopp", self)
        self.tool_bar_action_new2 = QAction(QIcon(".\\_internal\\img\\floppy-disk.png"), "Flopp", self)
        self.tool_bar_action_new3 = QAction(QIcon(".\\_internal\\img/\\loppy-disk.png"), "Flopp", self)
        
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
        
        self.main_widget.setContentsMargins(0,0,0,0)
        self.main_widget.setStyleSheet("padding:0px;margin:0px;")
        
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
        self.tab4 = QWidget()
        
        # add tabs
        self.tabs.addTab(self.tab0, "Project")
        self.tabs.addTab(self.tab1, "Pre-/Post Actions")
        self.tabs.addTab(self.tab2, "Topics")
        self.tabs.addTab(self.tab3, "DoxyGen")
        self.tabs.addTab(self.tab4, "Content")
        
        self.main_layout.addWidget(self.tabs)
        
        # create project tab
        self.tab2_top_layout = QHBoxLayout(self.tab2)
        self.tab3_top_layout = QHBoxLayout(self.tab3)
        self.tab4_top_layout = QHBoxLayout(self.tab4)
        
        ################
        ##self.tab1_layout = QHBoxLayout()
        ##self.tab1_widget = QWidget()
        
        self.widget_font = QFont("Arial", 12)
        self.widget_font.setBold(True)
        
        self.tab_widget_1 = QTabWidget()
        
        tab_1 = QWidget()
        tab_2 = QWidget()
        tab_3 = QWidget()
        
        tab_1.setFont(self.widget_font)
        tab_2.setFont(self.widget_font)
        tab_3.setFont(self.widget_font)
        
        self.tab_widget_1.addTab(tab_1, "Wizard")
        self.tab_widget_1.addTab(tab_2, "Expert")
        self.tab_widget_1.addTab(tab_3, "Run")
        
        list_layout_a = QVBoxLayout(tab_1)
        
        list_layout_1 = QHBoxLayout()
        list_widget_1 = QListWidget()
        
        list_layout_a.addLayout(list_layout_1)
        
        list_widget_1.setFocusPolicy(Qt.NoFocus)
        list_widget_1.setStyleSheet(css__widget_item)
        list_widget_1.setMinimumHeight(300)
        list_widget_1.setMaximumWidth(200)
        self.list_widget_1_elements = ["Project", "Mode", "Output", "Diagrams" ]
        #
        #
        for element in self.list_widget_1_elements:
            list_item = customQListWidgetItem(element, list_widget_1)
        
        list_widget_1.setCurrentRow(0)
        list_widget_1.itemClicked.connect(self.handle_item_click)
        list_layout_1.addWidget(list_widget_1)
        
        self.sv_1_1 = customScrollView_1("Project")
        self.sv_1_2 = customScrollView_2("Mode");     self.sv_1_2.hide()
        self.sv_1_3 = customScrollView_3("Output");   self.sv_1_3.hide()
        self.sv_1_4 = customScrollView_4("Diagrams"); self.sv_1_4.hide()
        
        for i in range(1, 5):
            s = "sv_1_" + str(i)
            list_layout_1.addWidget(getattr(self, f"{s}"))
        
        # progress bar
        self.lv_1 = QVBoxLayout()
        self.hw_1 = QWidget()
        
        hlp = customScrollView_help()
        bar = QProgressBar()
        bar.setTextVisible(False)
        #
        bar.setMinimum(1)
        bar.setMaximum(100)
        #
        bar.setValue(18)
        
        self.lv_1.addWidget(hlp)
        self.lv_1.addWidget(bar)
        
        list_layout_a.addLayout(self.lv_1)
        ########################
        list_layout_b = QVBoxLayout(tab_2)
        
        list_layout_2 = QHBoxLayout()
        list_widget_2 = QListWidget()
        
        list_layout_b.addLayout(list_layout_2)
        
        list_widget_2.setFocusPolicy(Qt.NoFocus)
        list_widget_2.setStyleSheet(css__widget_item)
        list_widget_2.setMinimumHeight(300)
        list_widget_2.setMaximumWidth(200)
        self.list_widget_2_elements = [                                     \
            "Project", "Build", "Messages", "Input", "Source Browser",      \
            "Index", "HTML", "LaTeX", "RTF", "Man", "XML", "DocBook",       \
            "AutoGen", "SQLite3", "PerlMod", "Preprocessor", "External",    \
            "Dot" ]
        #
        #
        for element in self.list_widget_2_elements:
            list_item = customQListWidgetItem(element, list_widget_2)
        
        list_widget_2.setCurrentRow(0)
        list_widget_2.itemClicked.connect(self.handle_item_click)
        list_layout_2.addWidget(list_widget_2)
        
        tab1_classes = [
        "customScrollView_5" , "customScrollView_6" , "customScrollView_7" , "customScrollView_8" ,
        "customScrollView_9" , "customScrollView_10", "customScrollView_11", "customScrollView_12",
        "customScrollView_13", "customScrollView_14", "customScrollView_15", "customScrollView_16",
        "customScrollView_17", "customScrollView_18", "customScrollView_19", "customScrollView_20",
        "customScrollView_21", "customScrollView_22"  ]
        
        objs = []
        i    = 0
        for item in tab1_classes:
            s = "sv_2_" + str(i+1)
            v1 = eval(item+"('')")
            v1.setName(self.list_widget_2_elements[i])
            objs.append(v1)
            setattr(self, s, v1)
            list_layout_2.addWidget(v1)
            v1.hide()
            i += 1
        print("1111111")
        self.sv_2_1.show()
        self.hw_2 = QWidget()
        
        list_layout_b.addWidget(sv_help)
        ########################
        self.tab3_top_layout.addWidget(self.tab_widget_1)
        
        
        self.tab2_file_path = '.\\_internal\\topics.txt'
        
        global tab2_tree_view
        tab2_tree_view = QTreeView()
        tab2_tree_view.setStyleSheet(css_model_header)
        self.tab2_tree_model = QStandardItemModel()
        self.tab2_tree_model.setHorizontalHeaderLabels(["Topic name", "ID", "Status", "Help icon", "In Build"])
        tab2_tree_view.setModel(self.tab2_tree_model)
        print("2222222")
        self.tab2_top_layout.addWidget(tab2_tree_view)
        self.populate_tree_view(self.tab2_file_path, ".\\_internal\\img\\open-folder.png")
        
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
        self.tab1_path_lineEdit.setStyleSheet(css_button_style)
        self.tab1_path_lineButton = QPushButton("...")
        self.tab1_path_lineButton.setMinimumWidth(28)
        self.tab1_path_lineButton.setMaximumHeight(28)
        self.tab1_path_lineButton.setMaximumWidth(32)
        
        self.tab1_path_layout = QHBoxLayout()
        
        self.tab1_path_layout.addWidget(self.tab1_path_lineEdit)
        self.tab1_path_layout.addWidget(self.tab1_path_lineButton)
        #
        self.tab1_left_layout.addLayout(self.tab1_path_layout)
        
        # Start und Stop Buttons
        self.tab1_startButton = QPushButton("Start", self.tab1)
        self.tab1_startButton.setStyleSheet(css_button_style)
        self.tab1_startButton.clicked.connect(self.startWatching)
        self.tab1_left_layout.addWidget(self.tab1_startButton)
        
        self.tab1_stopButton = QPushButton('Stop', self.tab1)
        self.tab1_stopButton.setStyleSheet(css_button_style)
        self.tab1_stopButton.clicked.connect(self.stopWatching)
        self.tab1_left_layout.addWidget(self.tab1_stopButton)
        
        # ComboBox für Zeitangaben
        self.tab1_timeComboBox = QComboBox(self.tab1)
        self.tab1_timeComboBox.addItems(["10", "15", "20", "25", "30", "60", "120"])
        self.tab1_timeComboBox.setStyleSheet(css_button_style)
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
        self.tab1_preActionComboBox.addItems([" Message", " Script", " URL", " FTP"])
        self.tab1_preActionComboBox.setStyleSheet(css_combobox_style)
        self.tab1_timeComboBox.setMaximumWidth(49)
        self.tab1_middle_layout.addWidget(self.tab1_preActionComboBox)
        
        self.tab1_preEditLineLabel = QLabel("Text / File:", self.tab1)
        self.tab1_middle_layout.addWidget(self.tab1_preEditLineLabel)
        #
        self.tab1_pre_layout = QHBoxLayout()
        
        self.tab1_preEditLineText = QLineEdit(self.tab1)
        self.tab1_preEditLineText.setStyleSheet(css_button_style)
     
        self.tab1_path_lineButton.setMaximumHeight(28)
        
        #
        self.tab1_pre_layout.addWidget(self.tab1_preEditLineText)
        
        self.tab1_middle_layout.addLayout(self.tab1_pre_layout)
        
        self.tab1_preAddButton = QPushButton("Add")
        self.tab1_preAddButton.setStyleSheet(css_button_style)
        #
        self.tab1_preDelButton = QPushButton("Delete")
        self.tab1_preDelButton.setStyleSheet(css_button_style)
        #            
        self.tab1_preClrButton = QPushButton("Clear All")
        self.tab1_preClrButton.setStyleSheet(css_button_style)
        
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
        self.tab1_postActionComboBox.addItems([" Message", " Script", " URL", " FTP"])
        self.tab1_postActionComboBox.setStyleSheet(css_combobox_style)
        self.tab1_right_layout.addWidget(self.tab1_postActionComboBox)
        
        self.tab1_postEditLineLabel = QLabel("Text / File:", self.tab1)
        self.tab1_right_layout.addWidget(self.tab1_postEditLineLabel)
        #
        self.tab1_post_layout = QHBoxLayout()
        
        self.tab1_postEditLineText = QLineEdit(self.tab1)
        self.tab1_postEditLineText.setStyleSheet(css_button_style)
        #
        self.tab1_post_layout.addWidget(self.tab1_postEditLineText)
        self.tab1_right_layout.addLayout(self.tab1_post_layout)
        
        self.tab1_postAddButton = QPushButton("Add")
        self.tab1_postAddButton.setStyleSheet(css_button_style)
        #
        self.tab1_postDelButton = QPushButton("Delete")
        self.tab1_postDelButton.setStyleSheet(css_button_style)
        #
        self.tab1_postClrButton = QPushButton("Clear All")
        self.tab1_postClrButton.setStyleSheet(css_button_style)
        
        self.tab1_postAddButton.clicked.connect(self.button_clicked_postadd)
        self.tab1_postDelButton.clicked.connect(self.button_clicked_postDel)
        self.tab1_postClrButton.clicked.connect(self.button_clicked_postClr)
        #
        self.tab1_right_layout.addWidget(self.tab1_postAddButton)
        self.tab1_right_layout.addWidget(self.tab1_postDelButton)
        self.tab1_right_layout.addWidget(self.tab1_postClrButton)
        
        print("0000112121212")
        # ------------------
        # alles zusammen ...
        # ------------------
        self.webView1 = QWebEngineView(self.tab4)
        self.profile1 = QWebEngineProfile("storage1", self.webView1)
        self.page1    = QWebEnginePage(self.profile1, self.webView1)
        self.webView1.setPage(self.page1)
        self.webView1.setHtml(html_content, baseUrl = QUrl. fromLocalFile('.'))
        print("5566778889888")
        self.tab4_top_layout.addWidget(self.webView1);            
        self.tab0_top_layout.addLayout(self.tab0_left_layout)
        
        self.tab1_top_layout.addLayout(self.tab1_left_layout)
        self.tab1_top_layout.addLayout(self.tab1_middle_layout)
        self.tab1_top_layout.addLayout(self.tab1_right_layout)
        
        self.layout.addLayout(self.main_layout)
        self.layout.addWidget(self.status_bar)
        
        self.setLayout(self.layout)
        self.setWindowTitle('HelpNDoc File Watcher v0.0.1 - (c) 2024 Jens Kallup - paule32')
        print("mmmmmmm")
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateCountdown)
        print("tttttttt")
        self.interval = 0
        self.currentTime = 0
        print("+++++++++")
    
    # ------------------------------------------------------------------------
    # class member to get the widget item from list_widget_1 or list_widget_2.
    # The application script will stop, if an internal error occur ...
    # ------------------------------------------------------------------------
    def handle_item_click(self, item):
        tab_index = self.tab_widget_1.currentIndex()
        if tab_index == 1:
            for i in range(0, len(self.list_widget_2_elements)):
                if item.data(0) == self.list_widget_2_elements[i]:
                    print("t: " + str(i) + ": " + self.list_widget_2_elements[i])
                    self.hideTabItems_2(i)
                    s = "sv_2_" + str(i+1)
                    w = getattr(self, f"{s}")
                    w.show()
                    break
        elif tab_index == 0:
            for i in range(0, len(self.list_widget_1_elements)):
                if item.data(0) == self.list_widget_1_elements[i]:
                    self.hideTabItems_1(i)
                    s = "sv_1_" + str(i+1)
                    w = getattr(self, f"{s}")
                    w.show()
                    return
    
    def hideTabItems_1(self, it):
        for i in range(0, len(self.list_widget_1_elements)):
            s = "sv_1_" + str(i+1)
            w = getattr(self, f"{s}")
            w.hide()
            if i == it:
                w.show()
    
    def hideTabItems_2(self, it):
        for i in range(0, len(self.list_widget_2_elements)):
            s = "sv_2_" + str(i+1)
            w = getattr(self, f"{s}")
            w.hide()
            if i == it:
                w.show()
    
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
        self.file_path = ".\\_internal\\LICENSE"
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
# atexit: callback when sys.exit() is handled, and come back to console...
# ------------------------------------------------------------------------
def ApplicationAtExit():
    print("Thank's for using.")
    return

# ------------------------------------------------------------------------
# this is our "main" entry point, where the application will start.
# ------------------------------------------------------------------------
def EntryPoint():
    atexit.register(ApplicationAtExit)
    
    global conn
    global conn_cursor
    
    error_fail   = False
    error_result = 0
    
    topic_counter = 1
    
    # ---------------------------------------------------------
    # init pascal interpreter ...
    # ---------------------------------------------------------
    #pas = interpreter_Pascal()
    #pas.ShowInstructions()
    #pas.Emulate()
    
    #sys.exit(1)
    
    # ---------------------------------------------------------
    # scoped global stuff ...
    # ---------------------------------------------------------
    global doxyfile, hhc__path
    
    pcount     = len(sys.argv) - 1
    
    doxy_env   = "DOXYGEN_PATH"  # doxygen.exe
    doxy_hhc   = "DOXYHHC_PATH"  # hhc.exe
    
    doxy_path  = ".\\_internal\\"
    hhc__path  = ""
    
    doxyfile   = ".\\_internal\\Doxyfile"
    
    
    # ---------------------------------------------------------
    # doxygen.exe directory path ...
    # ---------------------------------------------------------
    if not doxy_env in os.environ:
        if debugMode == True:
            os.environ["DOXYGEN_PATH"] = "E:\\doxygen\\bin"
        else:
            print(("error: " + f"{doxy_env}"
            + " is not set in your system settings."))
            sys.exit(EXIT_FAILURE)
    else:
        doxy_path = os.environ[doxy_env]
    
    # ---------------------------------------------------------
    # Microsoft Help Workshop path ...
    # ---------------------------------------------------------
    if not doxy_hhc in os.environ:
        if debugMode == True:
            os.environ["DOXYHHC_PATH"] = "E:\\doxygen\\hhc"
        else:
            print((""
                + "error: " + f"{doxy_hhc}"
                + " is not set in your system settings."))
            sys.exit(EXIT_FAILURE)
    else:
        hhc__path = os.environ[doxy_hhc]
    
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
    
    os_type = os_type_windows
    
    # -----------------------------------------------------
    # show a license window, when readed, and user give a
    # okay, to accept it, then start the application ...
    # -----------------------------------------------------
    app = QApplication(sys.argv)
    
    license_window = licenseWindow()
    # -------------------------------
    # close tje splash screen ...
    # -------------------------------
    if getattr(sys, 'frozen', False):
        pyi_splash.close()
        
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
    
    _ = handle_language(ini_lang)
    
    # ---------------------------------------------------------
    # combine the puzzle names, and folders ...
    # ---------------------------------------------------------
    po_file_name = (".\\_internal\\locales\\"
        + f"{ini_lang}"    + "\\LC_MESSAGES\\"
        + f"{__app__name}" + ".po")
    
    if not os.path.exists(convertPath(po_file_name)):
        print(__error__locales_error)
        sys.exit(EXIT_FAILURE)
    
    # ---------------------------------------------------------
    # when config file not exists, then spite a info message,
    # and create a default template for doxygen 1.10.0
    # ---------------------------------------------------------
    if not os.path.exists(doxyfile):
        print("info: config: '" \
        + f"{doxyfile}" + "' does not exists. I will fix this by create a default file.")
        
        file_content_warn = [
            ["QUIET", "YES"],
            ["WARNINGS", "YES"],
            ["",""],
            ["WARN_IF_UNDOCUMENTED", "NO"],
            ["WARN_IF_UNDOC_ENUM_VAL", "NO"],
            ["WARN_IF_DOC_ERROR", "YES"],
            ["WARN_IF_INCOMPLETE_DOC", "YES"],
            ["WARN_AS_ERROR", "NO"],
            ["WARN_FORMAT", "\"$file:$line: $text\""],
            ["WARN_LINE_FORMAT", "\"at line $line of file $file\""],
            ["WARN_LOGFILE", "warnings.log"]
        ]
        with open(doxyfile, 'w') as file:
            file.write(__app__comment_hdr)
            file.write("# File: Doxyfile\n")
            file.write("# Author: (c) 2024 Jens Kallup - paule32 non-profit software\n")
            file.write("#"  + (" " *  9) + "all rights reserved.\n")
            file.write("#\n")
            file.write("# optimized for: # Doxyfile 1.10.1\n")
            file.write(__app__comment_hdr)
            
            for i in range(0, len(file_content)):
                if len(file_content[i][0]) > 1:
                    file.write("{0:<32} = {1:s}\n".format( \
                    file_content[i][0],\
                    file_content[i][1]))
                else:
                    file.write("\n")
            
            file.write(__app__comment_hdr)
            file.write("# warning settings ...\n")
            file.write(__app__comment_hdr)
            
            for i in range(0, len(file_content_warn)):
                if len(file_content_warn[i][0]) > 1:
                    file.write("{0:<32} = {1:s}\n".format( \
                    file_content_warn[i][0],\
                    file_content_warn[i][1]))
                else:
                    file.write("\n")
            
            file.close()
    
    global sv_help
    sv_help = customScrollView_help()
    
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.datetime.now().strftime("%H:%M:%S")
    
    conn = sqlite3.connect(".\\_internal\\data.db")
    conn_cursor = conn.cursor()
    conn.close()
    
    if app == None:
        app = QApplication(sys.argv)
    
    appwin = FileWatcherGUI()
    appwin.move(100, 100)
    print("vvvvvvv")
    appwin.exec_()
    print("xxxxxxssssss")
    #error_result = app.exec_()
    return

if __name__ == '__main__':
    handleExceptionApplication(EntryPoint)
    print("End2")
    sys.exit(0)
        
# ----------------------------------------------------------------------------
# E O F  -  End - Of - File
# ----------------------------------------------------------------------------
