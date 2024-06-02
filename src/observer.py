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
global topic_counter; topic_counter = 1

global debugMode

import os            # operating system stuff
import sys

if getattr(sys, 'frozen', False):
    import pyi_splash

# ---------------------------------------------------------------------------
# under the windows console, python paths can make problems ...
# ---------------------------------------------------------------------------
if 'PYTHONHOME' in os.environ:
    del os.environ['PYTHONHOME']
if 'PYTHONPATH' in os.environ:
    del os.environ['PYTHONPATH']

# ---------------------------------------------------------------------------
# extent the search paths for supported interpreters and tools ...
# ---------------------------------------------------------------------------
__app__inter__ = "./interpreter/"
#
sys.path.append(__app__inter__ + "pascal")
sys.path.append(__app__inter__ + "dbase")
sys.path.append(__app__inter__ + "doxygen")
sys.path.append("./tools")

# -----------------------------------------------------------------------
# global used application stuff ...
# -----------------------------------------------------------------------
from appcollection import *
img = "/img/"

__app__name         = "observer"
__app__internal__   = "./_internal"
__app__config_ini   = __app__internal__ + "/observer.ini"
__app__img__int__   = __app__internal__ + img

__app__doxygen__    = __app__img__int__ + "doxygen"
__app__hlpndoc__    = __app__img__int__ + "helpndoc"
__app__helpdev__    = __app__img__int__ + "help"
__app__pythonc__    = __app__img__int__ + "python"
__app__lispmod__    = __app__img__int__ + "lisp"
__app__ccpplus__    = __app__img__int__ + "cpp"
__app__cpp1dev__    = __app__img__int__ + "c"
__app__dbasedb__    = __app__img__int__ + "dbase"
__app__javadev__    = __app__img__int__ + "java"
__app__javadoc__    = __app__img__int__ + "javadoc"
__app__freepas__    = __app__img__int__ + "freepas"
__app__locales__    = __app__img__int__ + "locales"

__app__img_ext__    = ".png"

__app__framework    = "PyQt5.QtWidgets.QApplication"
__app__exec_name    = sys.executable

__app__error_level  = "0"
__app__comment_hdr  = ("# " + misc.StringRepeat("-",78) + "\n")

__app__scriptname__ = ""

global css_model_header, css_tabs, css__widget_item, css_button_style

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
__locale__    = __app__internal__ + "/locales"
__locale__enu = "en_us"
__locale__deu = "de_de"

basedir = os.path.dirname(__file__)

# ------------------------------------------------------------------------
# style sheet definition's:
# ------------------------------------------------------------------------
css_model_header   = "model_hadr"
css_combobox_style = "combo_actn"
    
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
def getLangIDText(text):
    return _(text)

def handle_language(lang):
    try:
        system_lang, _ = locale.getlocale()
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
        self.setMinimumHeight(26)
        self.setMaximumWidth(250)
        self.setText(self.name)
        self.cssColor = _("edit_css")
        self.setStyleSheet(self.cssColor)

class myDBaseTextEditor(QTextEdit):
    def __init__(self, name=None):
        super().__init__()
        font = QFont("Courier New", 10)
        self.setFont(font)
        self.setMaximumHeight(545)
        self.setMinimumHeight(545)
        self.setLineWrapMode(QTextEdit.NoWrap)
        try:
            if not name == None:
                self.script_name = __app__scriptname__
                with open(self.script_name, "r") as file:
                    text = file.read()
                    self.setText(text)
                    file.close()
        except:
            print("file not found.")
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F2:
            print("\a")
        else:
            super().keyPressEvent(event)

# ------------------------------------------------------------------------
#
# ------------------------------------------------------------------------
class myTextEdit(QTextEdit):
    def __init__(self, name=""):
        super().__init__()
        self.name = name
        self.cssColor = _("text_css")
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

# ------------------------------------------------------------------------
#
# ------------------------------------------------------------------------
class OverlayWidget(QWidget):
    def __init__(self, parent, text):
        super().__init__(parent, Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.ToolTip)
        
        self.xpos = 100
        self.ypos = 100
        
        self.setGeometry(
        self.xpos,
        self.ypos, 250, 120)
        self.setStyleSheet(_("overlaycss"))
        
        self.caption = text
        
        font = QFont("Arial")
        font.setPointSize(11)
        font.setBold(True)
        
        self.vlayout = QVBoxLayout  ()
        self.label1  = QLabel(self.caption)
        self.label1.setMinimumHeight(100)
        self.label1.setAlignment(Qt.AlignBottom)
        self.label1.setFont(font)
        
        self.vlayout.addWidget(self.label1)
        self.setLayout(self.vlayout)

class myIconLabel(QLabel):
    def __init__(self, parent, text, mode):
        super().__init__(parent)
        
        self.overlay = OverlayWidget(self, text)
        self.caption = text
        self.mode    = mode
        self.parent  = parent
    
    def show_overlay(self):
        self.overlay.move(
            QCursor().pos().x()+50,
            QCursor().pos().y())
        self.overlay.show()
    
    def hide_overlay(self):
        self.overlay.hide()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            #print(self.caption)
            if self.mode == 0:
                self.btn_clicked(self.parent,self.parent.parent.help_tabs)
            elif self.mode == 1:
                self.btn_clicked(self.parent,self.parent.parent.dbase_tabs)
            elif self.mode == 2:
                self.btn_clicked(self.parent,self.parent.parent.pascal_tabs)
            elif self.mode == 3:
                self.btn_clicked(self.parent,self.parent.parent.isoc_tabs)
            elif self.mode == 4:
                self.btn_clicked(self.parent,self.parent.parent.java_tabs)
            elif self.mode == 5:
                self.btn_clicked(self.parent,self.parent.parent.python_tabs)
            elif self.mode == 6:
                self.btn_clicked(self.parent,self.parent.parent.lisp_tabs)
            elif self.mode == 10:
                self.btn_clicked(self.parent,self.parent.parent.locale_tabs)
    
    def enterEvent(self, event):
        self.show_overlay()
    
    def leaveEvent(self, event):
        self.hide_overlay()
    
    def hide_tabs(self):
        self.parent.parent.help_tabs.hide()
        self.parent.parent.dbase_tabs.hide()
        self.parent.parent.pascal_tabs.hide()
        self.parent.parent.isoc_tabs.hide()
        self.parent.parent.java_tabs.hide()
        self.parent.parent.python_tabs.hide()
        self.parent.parent.lisp_tabs.hide()
        self.parent.parent.locale_tabs.hide()
    
    def btn_clicked(self,btn,tabs):
        self.hide_tabs()
        tabs.show()
        
        self.set_null_state()
        btn.state = 2
        btn.set_style()
    
    def set_null_state(self):
        self.parent.parent.side_btn1.state = 0
        self.parent.parent.side_btn2.state = 0
        self.parent.parent.side_btn3.state = 0
        self.parent.parent.side_btn4.state = 0
        self.parent.parent.side_btn5.state = 0
        self.parent.parent.side_btn6.state = 0
        self.parent.parent.side_btn7.state = 0
        self.parent.parent.side_btnA.state = 0
        #
        self.parent.parent.side_btn1.set_style()
        self.parent.parent.side_btn2.set_style()
        self.parent.parent.side_btn3.set_style()
        self.parent.parent.side_btn4.set_style()
        self.parent.parent.side_btn5.set_style()
        self.parent.parent.side_btn6.set_style()
        self.parent.parent.side_btn7.set_style()
        self.parent.parent.side_btnA.set_style()

class myIconButton(QWidget):
    def __init__(self, parent, mode, label_text, text):
        super().__init__()
        
        self.vl = QVBoxLayout()
        self.pix_label = myIconLabel(self, text, mode)
        
        self.txt_fonda = QFont("Arial",10)
        self.txt_fonda.setBold(True)
        #
        self.txt_label = QLabel(label_text)
        self.txt_label.setAlignment(Qt.AlignCenter)
        self.txt_label.setFont(self.txt_fonda)
        
        self.pix_label.setObjectName("lbl-image")
        self.txt_label.setObjectName("lbl-text")
        
        self.vl.addWidget(self.pix_label)
        self.vl.addWidget(self.txt_label)
        #
        self.setLayout(self.vl)
        
        self.caption = text
        self.mode    = mode
        self.parent  = parent
        self.state   = 0
        
        self.bordercolor = "lightgray"
        self.parent      = parent
        self.state       = 0
        
        fg = str(1) + __app__img_ext__
        bg = str(2) + __app__img_ext__
        
        self.pix_label.setMinimumWidth (79)
        self.pix_label.setMinimumHeight(79)
        #
        self.pix_label.setMaximumWidth (79)
        self.pix_label.setMaximumHeight(79)
        
        self.image_fg = __app__helpdev__ + fg
        self.image_bg = __app__helpdev__ + bg
        
        parent.side_layout.addWidget(self)
        
        if mode == 0:
            self.image_fg = __app__helpdev__ + fg
            self.image_bg = __app__helpdev__ + bg
            
        elif mode == 1:
            self.image_fg = __app__dbasedb__ + fg
            self.image_bg = __app__dbasedb__ + bg
            
        elif mode == 2:
            self.image_fg = __app__freepas__ + fg
            self.image_bg = __app__freepas__ + bg
            
        elif mode == 3:
            self.image_fg = __app__cpp1dev__ + fg
            self.image_bg = __app__cpp1dev__ + bg
            
        elif mode == 4:
            self.image_fg = __app__javadev__ + fg
            self.image_bg = __app__javadev__ + bg
            
        elif mode == 5:
            self.image_fg = __app__pythonc__ + fg
            self.image_bg = __app__pythonc__ + bg
            
        elif mode == 6:
            self.image_fg = __app__lispmod__ + fg
            self.image_bg = __app__lispmod__ + bg
            
        if mode == 10:
            self.image_fg = __app__locales__ + fg
            self.image_bg = __app__locales__ + bg
        
        self.set_style()
    
    def set_style(self):
        if self.state == 2:
            self.bordercolor = "lime"
        else:
            self.bordercolor = "lightgray"
        
        style = _("labelico_css")        \
        .replace("{fg}", self.image_fg)  \
        .replace("{bg}", self.image_bg)  \
        .replace("{bc}", self.bordercolor)
        
        self.pix_label.setStyleSheet(style)
    
    def enterEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "gray";
            self.set_style()
        self.setCursor(QCursor(Qt.PointingHandCursor))
    
    def leaveEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "lightgray";
            self.set_style()
        self.setCursor(QCursor(Qt.ArrowCursor))

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
class iconComboBox(QComboBox):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(event.rect(), Qt.white)
        
        for i in range(self.count()):
            item_rect = self.view().visualRect(
            self.model().index(i, 0))
            
            icon = self.itemIcon(i)
            text = self.itemText(i)
            
            if not item_rect.isNull():
                if not icon.isNull():
                    icon_size = icon.actualSize(
                        QSize(
                            item_rect.height(),
                            item_rect.height()))
                    icon_rect = QRect(
                        item_rect.left() + 4,
                        item_rect.top(), 56,
                        item_rect.height())
                    icon.paint(painter,
                        icon_rect,
                        Qt.AlignCenter,
                        QIcon.Normal,
                        QIcon.Off)
                if not icon.isNull():
                    right_icon_rect = QRect(
                        item_rect.right() - item_rect.height(),
                        item_rect.top(),
                        icon_size.width(),
                        icon_size.height())
                    icon.paint(painter,
                        right_icon_rect,
                        Qt.AlignCenter,
                        QIcon.Normal,
                        QIcon.Off)
        
        arrow_icon = self.style().standardIcon(self.style().SP_ArrowDown)
        arrow_rect = QRect(
            self.width() - 20,  0, 20,
            self.height())
        arrow_icon.paint(painter,
            arrow_rect,
            Qt.AlignCenter,
            QIcon.Normal,
            QIcon.Off)
        
        boxrect = event.rect()
        boxrect.setWidth(boxrect.width() - 22)
        
        painter.setPen(Qt.black)
        painter.fillRect(boxrect, Qt.white)
        painter.drawRect(boxrect)
        
        selected_text = self.currentText()
        if selected_text:
            selected_text_rect = QRect(14, 0,
                self.width() - 24,
                self.height())
            painter.drawText(
                selected_text_rect, Qt.AlignLeft | Qt.AlignVCenter,
                selected_text)

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
        
        #self.setWidgetResizable(False)
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
            tokennum = _("A" + f"{helpID:04X}")
            
            vw_1 = self.addHelpLabel(   \
                tokennum,  \
                helpID,    \
                helpText,  \
                lh_0)
            vw_1.setMinimumHeight(14)
            vw_1.setMinimumWidth(200)
            
            if elements[i][1] == self.type_edit:
                self.addLineEdit("",lh_0)
                                    
                if elements[i][2] == 1:
                    self.addPushButton("+",lh_0)
                    
                elif elements[i][2] == 3:
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
                vw_2.setChecked(elements[i][3])
                lh_0.addWidget(vw_2)
            
            elif elements[i][1] == self.type_combo_box:
                vw_2 = iconComboBox(self)
                vw_2.setMinimumHeight(26)
                vw_2.setFont(self.font)
                vw_2.font().setPointSize(14)
                lh_0.addWidget(vw_2)
                
                if elements[i][2] == 4:
                    data = json.loads(self.supported_langs)
                    elements[i][3] = data
                    for j in range(0, len(data)):
                        img = __app__img__int__ + "flag_"  \
                        + elements[i][3][j] \
                        + __app__img_ext__
                        img = img.lower()
                        
                        vw_2.addItem(QIcon(img), elements[i][3][j-1])
                        #vw_2.setStyleSheet("""
                        #QComboBox QAbstractItemView {
                        #    selection-background-color: lightGray;
                        #    selection-color: black;
                        #    color: black;
                        #}
                        #""")
                
                elif elements[i][2] == 2:
                    for j in range(0, len(elements[i][3])):
                        vw_2.addItem(elements[i][3][j])
            
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
        widget_4_licon_1.setPixmap(QIcon(
            os.path.join(basedir,__app__img__int__,
            "floppy-disk" + __app__img_ext__))
            .pixmap(42,42))
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
        
        #self.setWidgetResizable(False)
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
        
        ## 0xA0100
        label_1_elements = [
            # <text>,                  <type 1>,             <help>, <type 2>,  <list 1>
            [0xA0101, self.type_edit,       0],
            
            [0xA0102, self.type_edit,       0, "My Project"],
            [0xA0103, self.type_edit,       0],
            [0xA0104, self.type_edit,       0],
            [0xA0105, self.type_edit,       1],
            [0xA0106, self.type_edit,       1],
            
            [0xA0107, self.type_edit,       1],
            [0xA0108, self.type_check_box,  0, True],
            [0xA0109, self.type_spin,       0],
            
            [0xA010A, self.type_check_box,  0, False],
            [0xA010B, self.type_combo_box,  4, [] ],
            
            [0xA010C, self.type_check_box,   0, True],
            [0xA010D, self.type_check_box,   0, True],
            [0xA010E, self.type_edit,       3],
            [0xA010F, self.type_check_box,   0, True],
            [0xA0110, self.type_check_box,   0, True],
            
            [0xA0111, self.type_check_box,   0, True],
            [0xA0112, self.type_edit,        3],
            [0xA0113, self.type_edit,        3],
            
            [0xA0114, self.type_check_box,   0, False],
            
            [0xA0115, self.type_check_box,   0, True ],
            [0xA0116, self.type_check_box,   0, False],
            
            [0xA0117, self.type_check_box,   0, False],
            
            [0xA0118, self.type_check_box,   0, False],
            [0xA0119, self.type_check_box,   0, True ],
            [0xA011A, self.type_check_box,   0, True ],
            [0xA011B, self.type_check_box,   0, False],
            
            [0xA011C, self.type_spin,        0],
            [0xA011D, self.type_edit,        3],
            
            [0xA011E, self.type_check_box,   0, True ],
            [0xA011F, self.type_check_box,   0, False],
            [0xA0120, self.type_check_box,   0, False],
            [0xA0121, self.type_check_box,   0, False],
            [0xA0122, self.type_check_box,   0, False],
            
            [0xA0123, self.type_edit,        3],
            
            [0xA0124, self.type_check_box,   0, True ],
            [0xA0125, self.type_spin,        0],
            [0xA0126, self.type_combo_box,   2, ["DOXYGEN", "CIT"]],
            [0xA0127, self.type_check_box,   0, True ],
            
            [0xA0128, self.type_check_box,   0, True ],
            [0xA0129, self.type_check_box,   0, True ],
            [0xA012A, self.type_check_box,   0, False],
            [0xA012B, self.type_check_box,   0, True ],
            
            [0xA012C, self.type_check_box,   0, False],
            [0xA012D, self.type_check_box,   0, False],
            [0xA012E, self.type_check_box,   0, True ],
            
            [0xA012F, self.type_check_box,   0, False],
            [0xA0130, self.type_check_box,   0, False],
            [0xA0131, self.type_check_box,   0, False],
            
            [0xA0132, self.type_spin,        0],
            [0xA0133, self.type_spin,        0],
            
            [0xA0134, self.type_combo_box,   2, ["NO","YES"]]
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
        
        ## 0xA0200
        label_1_elements = [
            [0xA0201, self.type_check_box, 0, False ],
            [0xA0202, self.type_check_box, 0, False ],
            [0xA0203, self.type_check_box, 0, False ],
            [0xA0204, self.type_check_box, 0, False ],
            [0xA0205, self.type_check_box, 0, True  ],
            [0xA0206, self.type_check_box, 0, True  ],
            [0xA0207, self.type_check_box, 0, True  ],
            [0xA0208, self.type_check_box, 0, True  ],
            [0xA0209, self.type_check_box, 0, True  ],
            [0xA020A, self.type_check_box, 0, False ],
            [0xA020B, self.type_check_box, 0, False ],
            [0xA020C, self.type_check_box, 0, False ],
            [0xA020D, self.type_check_box, 0, False ],
            [0xA020E, self.type_check_box, 0, True  ],
            
            [0xA020F, self.type_combo_box, 2, ["SYSTEM", "NO", "YES"] ],
            
            [0xA0210, self.type_check_box, 0, False ],
            [0xA0211, self.type_check_box, 0, False ],
            
            [0xA0212, self.type_check_box, 0, True  ],
            [0xA0213, self.type_check_box, 0, True  ],
            
            [0xA0214, self.type_check_box, 0, False ],
            [0xA0215, self.type_check_box, 0, False ],
            [0xA0216, self.type_check_box, 0, False ],
            [0xA0217, self.type_check_box, 0, False ],
            [0xA0218, self.type_check_box, 0, False ],
            [0xA0219, self.type_check_box, 0, False ],
            
            [0xA021A, self.type_check_box, 0, False ],
            [0xA021B, self.type_check_box, 0, False ],
            [0xA021C, self.type_check_box, 0, False ],
            
            [0xA021D, self.type_check_box, 0, False ],
            [0xA021E, self.type_check_box, 0, False ],
            [0xA021F, self.type_check_box, 0, False ],
            [0xA0220, self.type_check_box, 0, False ],
            
            [0xA0221, self.type_edit,      3 ],
            [0xA0222, self.type_spin,      0 ],
            
            [0xA0223, self.type_check_box, 0, True  ],
            [0xA0224, self.type_check_box, 0, True  ],
            [0xA0225, self.type_check_box, 0, True  ],
            
            [0xA0226, self.type_edit,      1 ],
            [0xA0227, self.type_edit,      1 ],
            [0xA0228, self.type_edit,      3 ]
        ]
        self.addElements(label_1_elements, 0x200)

class customScrollView_7(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA0300
        label_1_elements = [
            [0xA0301, self.type_check_box, 0, True  ],
            [0xA0302, self.type_check_box, 0, True  ],
            
            [0xA0303, self.type_check_box, 0, False ],
            [0xA0304, self.type_check_box, 0, True  ],
            [0xA0305, self.type_check_box, 0, True  ],
            
            [0xA0306, self.type_check_box, 0, False ],
            [0xA0307, self.type_check_box, 0, False ],
            
            [0xA0308, self.type_spin,      0 ],
            
            [0xA0309, self.type_edit,      0 ],
            [0xA030A, self.type_edit,      0 ],
            [0xA030B, self.type_edit,      1 ]
        ]
        self.addElements(label_1_elements, 0x0300)

class customScrollView_8(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1700)
        
        ## 0xA0400
        label_1_elements = [
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      0],
            [0xA0401, self.type_edit,      1],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_check_box, 0, True  ],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_check_box, 0, False ],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      0, False ],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      1],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_check_box, 0, False ],
            [0xA0401, self.type_edit,      3],
            [0xA0401, self.type_edit,      0],
            [0xA0401, self.type_spin,      0]
        ]
        self.addElements(label_1_elements, 0x0400)

class customScrollView_9(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(560)
        
        ## 0xA0500
        label_1_elements = [
            [0xA0501, self.type_check_box, 0, True  ],
            [0xA0502, self.type_check_box, 0, False ],
            [0xA0503, self.type_check_box, 0, False ],
            
            [0xA0504, self.type_check_box, 0, True  ],
            [0xA0505, self.type_check_box, 0, True  ],
            [0xA0506, self.type_check_box, 0, True  ],
            
            [0xA0507, self.type_check_box, 0, True  ],
            [0xA0508, self.type_check_box, 0, False ],
            [0xA0509, self.type_check_box, 0, True  ],
            
            [0xA050A, self.type_check_box, 0, False ],
            [0xA050B, self.type_check_box, 0, False ],
            [0xA050C, self.type_edit     , 3 ],
            [0xA050D, self.type_edit     , 1 ]
        ]
        self.addElements(label_1_elements, 0x0500)

class customScrollView_10(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA0600
        label_1_elements = [
            [0xA0601, self.type_check_box, 0, True ],
            [0xA0602, self.type_edit,      3 ]
        ]
        self.addElements(label_1_elements, 0x0600)

class customScrollView_11(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(2380)
        
        ## 0xA0700
        label_1_elements = [
            [0xA0701, self.type_check_box, 0, True  ],
            [0xA0702, self.type_edit,      1 ],
            [0xA0703, self.type_edit,      0 ],
            
            [0xA0704, self.type_edit,      1 ],
            [0xA0705, self.type_edit,      1 ],
            
            [0xA0706, self.type_edit,      1 ],
            [0xA0707, self.type_edit,      3 ],
            [0xA0708, self.type_edit,      3 ],
            
            [0xA0709, self.type_combo_box, 2, [ "LIGHT", "DARK", "AUTO_LIGHT", "AUTO_DARK", "TOOGLE" ] ],
            [0xA070A, self.type_spin,      0 ],
            [0xA070B, self.type_spin,      0 ],
            [0xA070C, self.type_spin,      0 ],
            [0xA070D, self.type_check_box, 0, True  ],
            [0xA070E, self.type_check_box, 0, False ],
            
            [0xA070F, self.type_check_box, 0, True  ],
            [0xA0710, self.type_check_box, 0, True  ],
            [0xA0711, self.type_edit,      0 ],
            [0xA0712, self.type_spin,      0 ],
            
            [0xA0713, self.type_check_box, 0, False ],
            [0xA0714, self.type_edit,      0 ],
            [0xA0715, self.type_edit,      0 ],
            [0xA0716, self.type_edit,      0 ],
            [0xA0717, self.type_edit,      0 ],
            [0xA0718, self.type_edit,      0 ],
            
            [0xA0719, self.type_check_box, 0, True  ],
            [0xA071A, self.type_edit,      1 ],
            [0xA071B, self.type_edit,      1 ],
            [0xA071C, self.type_check_box, 0, False ],
            [0xA071D, self.type_edit,      0 ],
            [0xA071E, self.type_check_box, 0, False ],
            [0xA071F, self.type_check_box, 0, False ],
            [0xA0720, self.type_edit,      0 ],
            
            [0xA0721, self.type_check_box, 0, False ],
            [0xA0722, self.type_edit,      1 ],
            [0xA0723, self.type_edit,      0 ],
            [0xA0724, self.type_edit,      0 ],
            [0xA0725, self.type_edit,      0 ],
            [0xA0726, self.type_edit,      0 ],
            [0xA0727, self.type_edit,      1 ],
            
            [0xA0728, self.type_check_box, 0, False ],
            [0xA0729, self.type_edit,      0 ],
            [0xA072A, self.type_check_box, 0, False ],
            
            [0xA072B, self.type_check_box, 0, True  ],
            [0xA072C, self.type_check_box, 0, False ],
            
            [0xA072D, self.type_spin,      0 ],
            [0xA072E, self.type_spin,      0 ],
            
            [0xA072F, self.type_check_box, 0, False ],
            [0xA0730, self.type_check_box, 0, True  ],
            
            [0xA0731, self.type_combo_box, 2, [ "png", "svg" ] ],
            [0xA0732, self.type_spin,      0 ],
            [0xA0733, self.type_edit,      1 ],
            
            [0xA0734, self.type_check_box, 0, False ],
            [0xA0735, self.type_combo_box, 2, [ "MathJax_2", "MathJax_3" ] ],
            [0xA0736, self.type_combo_box, 2, [ "HTML + CSS", "NativeXML", "chtml", "SVG" ] ],
            
            [0xA0737, self.type_edit,      1 ],
            [0xA0738, self.type_edit,      3 ],
            [0xA0739, self.type_edit,      0 ],
            
            [0xA073A, self.type_check_box, 0, False ],
            [0xA073B, self.type_check_box, 0, False ],
            [0xA073C, self.type_check_box, 0, False ],
            [0xA073D, self.type_edit,      0 ],
            [0xA073E, self.type_edit,      1 ],
            [0xA073F, self.type_edit,      0 ],
            [0xA0740, self.type_edit,      3 ]
        ]
        self.addElements(label_1_elements, 0x0700)

class customScrollView_12(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1000)
        
        ## 0xA0800
        label_1_elements = [
            [0xA0801, self.type_check_box, 0, False ],
            [0xA0802, self.type_edit,      1 ],
            [0xA0803, self.type_edit,      1 ],
            [0xA0804, self.type_edit,      0 ],
            [0xA0805, self.type_check_box, 0, False ],
            [0xA0806, self.type_combo_box, 2, [ "a4", "letter", "executive" ] ],
            [0xA0807, self.type_edit,      3 ],
            [0xA0808, self.type_edit,      1 ],
            [0xA0809, self.type_edit,      1 ],
            [0xA080A, self.type_edit,      3 ],
            [0xA080B, self.type_edit,      3 ],
            [0xA080C, self.type_check_box, 0, True  ],
            [0xA080D, self.type_check_box, 0, True  ],
            [0xA080E, self.type_combo_box, 2, [ "NO", "YWS", "BATCH", "NON-STOP", "SCROLL", "ERROR_STOP" ] ],
            [0xA080F, self.type_check_box, 0, False ],
            [0xA0810, self.type_edit,      0 ],
            [0xA0811, self.type_edit,      1 ]
        ]
        self.addElements(label_1_elements, 0x0800)

class customScrollView_13(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA0900
        label_1_elements = [
            [0xA0901, self.type_check_box, 0, False ],
            [0xA0902, self.type_edit,      1 ],
            [0xA0903, self.type_check_box, 0, False ],
            [0xA0904, self.type_check_box, 0, False ],
            [0xA0905, self.type_edit,      1 ],
            [0xA0906, self.type_edit,      1 ]
        ]
        self.addElements(label_1_elements, 0x0900)

class customScrollView_14(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1000
        label_1_elements = [
            [0xA1001, self.type_check_box, 0, False ],
            [0xA1002, self.type_edit,      1 ],
            [0xA1003, self.type_edit,      0 ],
            [0xA1004, self.type_edit,      0 ],
            [0xA1005, self.type_check_box, 0, False ],
        ]
        self.addElements(label_1_elements, 0x1000)

class customScrollView_15(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1100
        label_1_elements = [
            [0xA1101, self.type_check_box, 0, False ],
            [0xA1102, self.type_edit,      1 ],
            [0xA1103, self.type_check_box, 0, False ],
            [0xA1104, self.type_check_box, 0, False ]
        ]
        self.addElements(label_1_elements, 0x1100)

class customScrollView_16(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1400)
        
        ## 0xA1200
        label_1_elements = [
            [0xA1201, self.type_check_box, 0, False ],
            [0xA1202, self.type_edit,      1 ],
        ]
        self.addElements(label_1_elements, 0x1200)

class customScrollView_17(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1300
        label_1_elements = [
            [0xA1301,  self.type_check_box, 0, False ]
        ]
        self.addElements(label_1_elements, 0x1300)

class customScrollView_18(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1400
        label_1_elements = [
            [0xA1401, self.type_check_box, 0, False ],
            [0xA1402, self.type_edit,      1 ],
            [0xA1403, self.type_check_box, 0, True  ],
        ]
        self.addElements(label_1_elements, 0x1400)

class customScrollView_19(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1500
        label_1_elements = [
            [0xA1501, self.type_check_box, 0, False ],
            [0xA1502, self.type_check_box, 0, False ],
            [0xA1503, self.type_check_box, 0, False ],
            [0xA1504, self.type_edit,      1 ]
        ]
        self.addElements(label_1_elements, 0x1500)

class customScrollView_20(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(800)
        
        ## 0xA1600
        label_1_elements = [
            [0xA1601, self.type_check_box, 0, True  ],
            [0xA1602, self.type_check_box, 0, True  ],
            [0xA1603, self.type_check_box, 0, False ],
            [0xA1604, self.type_check_box, 0, False ],
            [0xA1605, self.type_edit,      3 ],
            [0xA1606, self.type_edit,      3 ],
            [0xA1607, self.type_edit,      3 ],
            [0xA1608, self.type_edit,      3 ],
            [0xA1609, self.type_check_box, 0, True  ]
        ]
        self.addElements(label_1_elements, 0x1600)

class customScrollView_21(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(400)
        
        ## 0xA1700
        label_1_elements = [
            [0xA1701, self.type_edit,  3 ],
            [0xA1702, self.type_edit,  1 ],
            [0xA1703, self.type_check_box, 0, False ],
            [0xA1704, self.type_check_box, 0, True  ],
            [0xA1705, self.type_check_box, 0, True  ]
        ]
        self.addElements(label_1_elements, 0x1700)

class customScrollView_22(myCustomScrollArea):
    def __init__(self, name):
        super().__init__(name)
        self.init_ui()
    def init_ui(self):
        self.label_1.hide()
        self.content_widget.setMinimumHeight(1800)
        
        ## 0xA1800
        label_1_elements = [
            [0xA1801, self.type_check_box, 0, False ],
            [0xA1802, self.type_check_box, 0, False ],
            [0xA1803, self.type_spin     , 0 ],
            
            [0xA1804, self.type_edit, 0 ],
            [0xA1805, self.type_edit, 0 ],
            [0xA1806, self.type_edit, 0 ],
            [0xA1807, self.type_edit, 1 ],
            
            [0xA1808, self.type_combo_box, 2, [ "YES", "NO" ] ],
            [0xA1809, self.type_check_box, 0, True  ],
            [0xA180A, self.type_check_box, 0, True  ],
            [0xA180B, self.type_check_box, 0, False ],
            [0xA180C, self.type_spin     , 0 ],
            [0xA180D, self.type_combo_box, 2, [ "NO", "YES" ] ],
            [0xA180E, self.type_spin     , 0 ],
            
            [0xA180F, self.type_check_box, 0, False ],
            [0xA1810, self.type_check_box, 0, False ],
            [0xA1811, self.type_check_box, 0, False ],
            [0xA1812, self.type_check_box, 0, False ],
            [0xA1813, self.type_check_box, 0, False ],
            [0xA1814, self.type_check_box, 0, False ],
            [0xA1815, self.type_check_box, 0, False ],
            
            [0xA1816, self.type_spin     , 0 ],
            [0xA1817, self.type_combo_box, 2, [ "png", "svg" ] ],
            
            [0xA1818, self.type_check_box, 0, False ],
            
            [0xA1819, self.type_edit     , 1 ],
            [0xA181A, self.type_edit     , 3 ],
            
            [0xA181B, self.type_edit     , 1 ],
            [0xA181C, self.type_edit     , 3 ],
            
            [0xA181D, self.type_edit     , 1 ],
            [0xA181E, self.type_edit     , 1 ],
            [0xA181F, self.type_edit     , 3 ],
            
            [0xA1820, self.type_spin     , 0 ],
            [0xA1821, self.type_spin     , 0 ],
            
            [0xA1822, self.type_check_box, 0, False ],
            [0xA1823, self.type_check_box, 0, False ],
            [0xA1824, self.type_check_box, 0, True  ],
            [0xA1825, self.type_edit     , 1 ],
            [0xA1826, self.type_edit     , 3 ]
        ]
        self.addElements(label_1_elements, 0x1800)

class customScrollView_help(QTextEdit):
    def __init__(self):
        super().__init__()
        
        font = QFont("Arial")
        font.setPointSize(11)
        
        self.setFont(font)
        self.setMinimumHeight(100)
        self.setMaximumHeight(100)

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
        editor.addItem(QIcon(__app__img__int__ + "icon_white"  + __app__img_ext__), "Complete"     )
        editor.addItem(QIcon(__app__img__int__ + "icon_blue"   + __app__img_ext__), "Needs Review" )
        editor.addItem(QIcon(__app__img__int__ + "icon_yellow" + __app__img_ext__), "In Progress"  )
        editor.addItem(QIcon(__app__img__int__ + "icon_red"    + __app__img_ext__), "Out of Date"  )
        
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
        ico_yellow = "icon_yellow" + __app__img_ext__
        
        liste = ["CHM", "HTML", "Word", "PDF", "EPub", "Kindle", "Qt Help", "MarkDown"]
        for item in liste:
            editor.addItem(QIcon(__app__img__int__ + ico_yellow ), item + " " + str(i))
            it1 = editor.model().item(i-1, 0)
            it1.setCheckState(Qt.Unchecked)
            i = i + 1
        return editor

class SpinEditDelegateID(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        self.topic_counter = topic_counter
        editor.setValue(self.topic_counter)
        self.topic_counter = self.topic_counter + 1
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

class doxygenImageTracker(QWidget):
    def __init__(self, parent=None):
        super(doxygenImageTracker, self).__init__(parent)
        
        self.img_origin_doxygen_label = QLabel(self)
        self.img_origin_doxygen_label.setObjectName("doxygen-image")
        self.img_origin_doxygen_label.move(30,10)
        self.img_origin_doxygen_label.setMinimumHeight(70)
        self.img_origin_doxygen_label.setMinimumWidth(238)
        
        self.bordercolor = "lightgray"
        self.parent      = parent
        self.state       = 0
        self.set_style()
    
    def set_style(self):
        style = _("doxtrack_css") \
        .replace("{1i}",__app__doxygen__ + str(1) + __app__img_ext__) \
        .replace("{1b}",self.bordercolor ) \
        .replace("{2i}",__app__doxygen__ + str(2) + __app__img_ext__) \
        .replace("{2b}",self.bordercolor )
        
        self.img_origin_doxygen_label.setStyleSheet(style)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if img_hlpndoc.state == 2:
                img_hlpndoc.bordercolor = "lightgray"
                img_hlpndoc.state = 0
                img_hlpndoc.set_style()
            
            if self.state == 0:
                self.state = 2
                self.bordercolor = "lime";
                self.set_style()
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
            print("doxygen")
    
    def enterEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "gray";
            self.set_style()
        self.img_origin_doxygen_label.setCursor(QCursor(Qt.PointingHandCursor))
    
    def leaveEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "lightgray";
            self.set_style()
        self.img_origin_doxygen_label.setCursor(QCursor(Qt.ArrowCursor))

class helpNDocImageTracker(QWidget):
    def __init__(self, parent=None):
        super(helpNDocImageTracker, self).__init__(parent)
        
        self.img_origin_hlpndoc_label = QLabel(self)
        self.img_origin_hlpndoc_label.setObjectName("hlpndoc-image")
        self.img_origin_hlpndoc_label.move(32,24)
        self.img_origin_hlpndoc_label.setMinimumHeight(70)
        self.img_origin_hlpndoc_label.setMinimumWidth(230)
        
        self.bordercolor = "lightgray"
        self.parent      = parent
        self.state       = 0
        self.set_style()
    
    def set_style(self):
        style = _("doxtrack_css") \
        .replace("{1i}",__app__hlpndoc__ + str(1) + __app__img_ext__).replace("{1b}",self.bordercolor ) \
        .replace("{2i}",__app__hlpndoc__ + str(2) + __app__img_ext__).replace("{2b}",self.bordercolor )
        
        self.img_origin_hlpndoc_label.setStyleSheet(style)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if img_doxygen.state == 2:
                img_doxygen.bordercolor = "lightgray"
                img_doxygen.state = 0
                img_doxygen.set_style()
            
            if self.state == 0:
                self.state = 2
                self.bordercolor = "lime";
                self.set_style()
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
            print("helpNDoc")
    
    def enterEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "gray";
            self.set_style()
        self.img_origin_hlpndoc_label.setCursor(QCursor(Qt.PointingHandCursor))
    
    def leaveEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "lightgray";
            self.set_style()
        self.img_origin_hlpndoc_label.setCursor(QCursor(Qt.ArrowCursor))

class ccpplusImageTracker(QWidget):
    def __init__(self, parent=None):
        super(ccpplusImageTracker, self).__init__(parent)
        
        #self.setMinimumHeight(120)
        #self.setMinimumWidth(120)
        self.img_origin_ccpplus_label = QLabel(self)
        self.img_origin_ccpplus_label.setObjectName("ccpplus-image")
        self.img_origin_ccpplus_label.move(15,0)
        self.img_origin_ccpplus_label.setMinimumHeight(107)
        self.img_origin_ccpplus_label.setMinimumWidth(104)
        
        self.bordercolor = "lightgray"
        self.parent      = parent
        self.state       = 0
        self.set_style()
    
    def set_style(self):
        style = _("doxtrack_css") \
        .replace("{1i}",__app__cpp1dev__ + str(1) + __app__img_ext__).replace("{1b}",self.bordercolor ) \
        .replace("{2i}",__app__cpp1dev__ + str(2) + __app__img_ext__).replace("{2b}",self.bordercolor )
        
        self.img_origin_ccpplus_label.setStyleSheet(style)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if img_javadoc.state == 2:
                img_javadoc.bordercolor = "lightgray"
                img_javadoc.set_style()
                img_javadoc.state = 0
            #
            if img_freepas.state == 2:
                img_freepas.bordercolor = "lightgray"
                img_freepas.set_style()
                img_freepas.state = 0
            
            if self.state == 0:
                self.state = 2
                self.bordercolor = "lime";
                self.set_style()
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
            print("javadoc")
    
    def enterEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "gray";
            self.set_style()
        self.img_origin_ccpplus_label.setCursor(QCursor(Qt.PointingHandCursor))
    
    def leaveEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "lightgray";
            self.set_style()
        self.img_origin_ccpplus_label.setCursor(QCursor(Qt.ArrowCursor))

class javadocImageTracker(QWidget):
    def __init__(self, parent=None):
        super(javadocImageTracker, self).__init__(parent)
        
        self.img_origin_javadoc_label = QLabel(self)
        self.img_origin_javadoc_label.setObjectName("javadoc-image")
        self.img_origin_javadoc_label.move(14,0)
        self.img_origin_javadoc_label.setMinimumHeight(107)
        self.img_origin_javadoc_label.setMinimumWidth(104)
        
        self.bordercolor = "lightgray";
        self.parent      = parent
        self.state       = 0
        
        self.set_style()
        
    def set_style(self):
        style = _("doxtrack_css") \
        .replace("{1i}",__app__javadoc__ + str(1) + __app__img_ext__) \
        .replace("{1b}",self.bordercolor ) \
        .replace("{2i}",__app__javadoc__ + str(2) + __app__img_ext__) \
        .replace("{2b}",self.bordercolor )
        
        self.img_origin_javadoc_label.setStyleSheet(style)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if img_ccpplus.state == 2:
                img_ccpplus.bordercolor = "lightgray"
                img_ccpplus.set_style()
                img_ccpplus.state = 0
            #
            if img_freepas.state == 2:
                img_freepas.bordercolor = "lightgray"
                img_freepas.set_style()
                img_freepas.state = 0
            
            if self.state == 0:
                self.state = 2
                self.bordercolor = "lime";
                self.set_style()
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
            print("javadoc")
    
    def enterEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "gray";
            self.set_style()
        self.img_origin_javadoc_label.setCursor(QCursor(Qt.PointingHandCursor))
    
    def leaveEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "lightgray";
            self.set_style()
        self.img_origin_javadoc_label.setCursor(QCursor(Qt.ArrowCursor))

class freepasImageTracker(QWidget):
    def __init__(self, parent=None):
        super(freepasImageTracker, self).__init__(parent)
        
        self.bordercolor = "lightgray"
        self.parent      = parent
        self.state       = 0
        
        self.img_origin_freepas_label = QLabel(self)
        self.img_origin_freepas_label.setObjectName("freepas-image")
        self.img_origin_freepas_label.move(30,10)
        self.img_origin_freepas_label.setMinimumHeight(70)
        self.img_origin_freepas_label.setMinimumWidth(218)
        
        self.set_style()
        
    def set_style(self):
        style = _("doxtrack_css") \
        .replace("{1i}",__app__freepas__ + str(1) + __app__img_ext__) \
        .replace("{1b}",self.bordercolor ) \
        .replace("{2i}",__app__freepas__ + str(2) + __app__img_ext__) \
        .replace("{2b}",self.bordercolor )
        
        self.img_origin_freepas_label.setStyleSheet(style)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if img_javadoc.state == 2:
                img_javadoc.bordercolor = "lightgray"
                img_javadoc.set_style()
                img_javadoc.state = 0
            #
            if img_ccpplus.state == 2:
                img_ccpplus.bordercolor = "lightgray"
                img_ccpplus.set_style()
                img_ccpplus.state = 0
                
            if self.state == 0:
                self.state = 2
                self.bordercolor = "lime";
                self.set_style()
            else:
                self.state = 0
                self.bordercolor = "lightgray";
                self.set_style()
            print("freepas")
    
    def enterEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "gray";
            self.set_style()
        self.img_origin_freepas_label.setCursor(QCursor(Qt.PointingHandCursor))
    
    def leaveEvent(self, event):
        if self.state == 2:
            self.bordercolor = "lime";
            self.set_style()
        else:
            self.bordercolor = "lightgray";
            self.set_style()
        self.img_origin_freepas_label.setCursor(QCursor(Qt.ArrowCursor))

class MyPushButton(QLabel):
    def __init__(self, parent, mode):
        super().__init__("")
        self.setMaximumWidth(110)
        self.setMinimumWidth(110)
        self.setMinimumHeight(34)
        
        if mode == 1:
            self.btn_img_fg = __app__img__int__ + "create1" + __app__img_ext__
            self.btn_img_bg = __app__img__int__ + "create2" + __app__img_ext__
        elif mode == 2:
            self.btn_img_fg = __app__img__int__ + "open1"   + __app__img_ext__
            self.btn_img_bg = __app__img__int__ + "open2"   + __app__img_ext__
        elif mode == 3:
            self.btn_img_fg = __app__img__int__ + "repro1"  + __app__img_ext__
            self.btn_img_bg = __app__img__int__ + "repro2"  + __app__img_ext__
        elif mode == 4:
            self.btn_img_fg = __app__img__int__ + "build1"  + __app__img_ext__
            self.btn_img_bg = __app__img__int__ + "build2"  + __app__img_ext__
        
        style = _("push_css") \
        .replace("{fg}",self.btn_img_fg) \
        .replace("{bg}",self.btn_img_bg)
        
        self.setStyleSheet(style)

class MyEllipseButton(QPushButton):
    def __init__(self, font):
        super().__init__("...")
        self.setFont(font)
        self.setMinimumHeight(36)
        self.setMinimumWidth (36)
        self.setMaximumWidth (36)

class myExitDialog(QDialog):
    def __init__(self, title, parent=None):
        super(myExitDialog, self).__init__(parent)
        
        self.setWindowTitle(title)
        
        font = QFont("Arial", 10)
        font.setBold(True)
        self.setFont(font)
        
        self.hlayout    = QHBoxLayout()
        
        self.vlayout    = QVBoxLayout()
        self.helpButton = QPushButton(_("&Help"))
        self.prevButton = QPushButton(_("&Cancel"))
        self.exitButton = QPushButton(_("&Exit"))
        
        self.helpButton.setDefault(True)
        self.prevButton.setDefault(True)
        self.exitButton.setDefault(True)
        
        self.helpButton.clicked.connect(self.help_click)
        self.prevButton.clicked.connect(self.prev_click)
        self.exitButton.clicked.connect(self.exit_click)
        
        self.vlayout.addWidget(self.helpButton)
        self.vlayout.addWidget(self.prevButton)
        self.vlayout.addWidget(self.exitButton)
        
        self.hexitText = QLabel(_("Would you realy exit the Application"))
        
        self.hlayout.addLayout(self.vlayout)
        self.hlayout.addWidget(self.hexitText)
        
        self.setLayout(self.hlayout)
    
    def help_click(self):
        print("help button")
        self.close()
        return
    def prev_click(self):
        print("reje")
        self.close()
        return
    def exit_click(self):
        sys.exit(0)

class myMoveButton(QPushButton):
    def __init__(self, text, parent=None):
        super(myMoveButton, self).__init__(text, parent)
        
        self.parent = parent
        
        self.setMinimumWidth (84)
        self.setMinimumHeight(21)
        
        #self.parent.setAcceptDrops(True)
        
    def mouseMoveEvent(self, event):
        drag = QDrag(self)
        mime = QMimeData()
        drag.setMimeData(mime)
        drag.exec_(Qt.MoveAction)
    
    def dragEnterEvent(self, event):
        event.accept()
        print("enter")
    
    def dropEvent(self, event):
        pos = event.pos()
        widget = event.source()
        event.accept()
        print("drop")

class myGridViewerOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
    
    def dragEnterEvent(self, event):
        event.accept()
        
    def dropEvent(self, event):
        pos = event.pos()
        widget = event.source()
        widget.move(pos.x(), pos.y())
        
        event.accept()
    def paintEvent(self, event):
        pen = QPen()
        
        painter = QPainter(self)
        painter.setPen(pen)
        
        points      = []
        gridSize    = 10
        
        x      = y  = -10
        
        width  = self.width()
        height = self.height()
        
        while y <= height:
            y += gridSize
            while x <= width:
                x += gridSize
                points.append(QPoint(x,y))
            x = 0
            points.append(QPoint(x,y))
        painter.drawPoints(points)

class addEventField(QLabel):
    def __init__(self, parent, text):
        super().__init__(text, parent)
        
        font1 = QFont("Arial", 10); font1.setBold(True)
        font2 = QFont("Arial", 10); font2.setBold(False)
        
        self.hlayout = QHBoxLayout()
        self.lhs     = self
        
        self.setMinimumWidth(112)
        self.setMaximumWidth(112)
        #
        self.setStyleSheet("margin:0px;border: 1px solid black;")
        self.setFont(font1)
        
        self.btn = QPushButton("E")
        self.btn.setMinimumWidth (15)
        self.btn.setMaximumWidth (15)
        #
        self.btn.setMaximumHeight(15)
        self.btn.setMaximumHeight(15)
        
        css_rhs = _("edit_css")
        
        self.rhs = QLineEdit()
        self.rhs.setMaximumWidth((self.width()+92)//2)
        self.rhs.setStyleSheet(css_rhs)
        self.rhs.setFont(font2)
        
        self.hlayout.addWidget(self.lhs)
        self.hlayout.addWidget(self.rhs)
        self.hlayout.addWidget(self.btn)
        
        parent.evt_vbox_layout.addLayout(self.hlayout)

class addPropertyCat(QLabel):
    def __init__(self, parent, text):
        super().__init__(text, parent)
        
        font = QFont("Arial",12)
        font.setBold(True)
        
        self.setContentsMargins(2,0,0,2)
        self.setStyleSheet("background-color:gray;color:white")
        self.setMinimumHeight(16)
        self.resize(parent.pos_scroll_widget.width(),22)
        self.setFont(font)
        
        parent.pos_vbox_layout.addWidget(self)

class closeLabelX(QLabel):
    def __init__(self, text, parent):
        super().__init__(text, parent.close_btn)
        self.parent = parent
    
    def mousePressEvent(self, event):
        self.parent.close()

class addProperty(QLabel):
    def __init__(self, parent, kind, text):
        super().__init__(text, parent)
        
        font1 = QFont("Arial", 10)
        font1.setBold(True)
        font2 = QFont("Arial", 10)
        font2.setBold(False)
        
        self.hlayout = QHBoxLayout()
        self.lhs     = self
        
        if kind == 1:
            css_rhs = _("spin_css")
        
        elif kind == 2:
            css_rhs = _("edit_css")
        
        elif kind == 3:
            css_rhs = _("check_css")
        
        elif kind == 4:
            css_rhs = _("combo_css")
        
        self.ftext_spacer = ' ' * 9
        self.ttext_spacer = ' ' * 15
        
        if kind == 1:
            self.rhs = QSpinBox()
            self.rhs.setMaximumWidth((self.width()+100)//2)
        elif kind == 2:
            self.rhs = QLineEdit()
            self.rhs.setMaximumWidth((self.width()+100)//2)
            self.btn = QPushButton("E")
        elif kind == 3:
            self.rhs = QCheckBox()
            self.rhs.setText("FALSE" + self.ftext_spacer)
            self.rhs.setMaximumWidth((self.width()+100)//2)
            self.rhs.stateChanged.connect(self.checkbox_changed)
        elif kind == 4:
            self.rhs = QComboBox()
            self.rhs.setMaximumWidth((self.width()+100)//2)
            self.rhs.addItem("black")
            self.rhs.addItem("white")
            self.rhs.addItem("red")
            self.rhs.addItem("green")
            self.rhs.addItem("yellow")
            self.rhs.addItem("blue")
        
        self.rhs.setStyleSheet(css_rhs)
        self.rhs.setFont(font2)
        
        self.hlayout.addWidget(self.lhs)
        self.hlayout.addWidget(self.rhs)
        
        if kind == 2:
            self.hlayout.addWidget(self.btn)
        
        self.setMinimumWidth(102)
        self.setMaximumWidth(102)
        #
        self.setStyleSheet("margin:0px;border: 1px solid black;")
        self.setFont(font1)
        
        parent.pos_vbox_layout.addLayout(self.hlayout)
    
    def checkbox_changed(self, int):
        if self.rhs.isChecked():
            self.rhs.setText("TRUE"  + self.ttext_spacer)
        else:
            self.rhs.setText("FALSE" + self.ftext_spacer)

class addInspectorItem():
    def __init__(self, parent, text, value):
        item = QTreeWidgetItem()
        item.setText(0,text)
        item.setText(1,str(value))
        #
        test1 = QTreeWidgetItem(item)
        test2 = QTreeWidgetItem(item)
        
        test1.setText(0,"TEST_A")
        test2.setText(0,"TEST_B")
        #
        parent.object_inspector.addTopLevelItem(item)


class CppSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        
        dark_green = QColor(0,100,0)
        
        self.commentFormat = QTextCharFormat()
        self.commentFormat.setForeground(dark_green)
        self.commentFormat.setFontWeight(QFont.Normal)  # Set the comment font weight to normal
        
        self.boldFormat = QTextCharFormat()
        self.boldFormat.setFont(QFont("Consolas", 12))  # Set the font for keywords
        self.boldFormat.setFontWeight(QFont.Bold)
        
        # Definiere die Schlüsselwörter, die fettgedruckt sein sollen
        self.keywords = [
            ".AND.", ".OR.", ".NOR.", ".XOR.",
            "BREAK",
            "CASE",
            "CLASS",
            "DO",
            "IF",
            "ELSE",
            "ENDCASE",
            "ENDCLASS",
            "ENDFOR",
            "ENDIF",
            "ENDWHILE",
            "ENDWITH",
            "FOR",
            "RETURN",
            "TO",
            "WHILE", 
            "WITH"
        ]
        
        # Definiere die Muster für mehrzeilige Kommentare
        self.multiLineCommentFormat = QTextCharFormat()
        self.multiLineCommentFormat.setForeground(dark_green)
        self.commentStartExpression = QRegExp(r"/\*")
        self.commentEndExpression   = QRegExp(r"\*/")
    
    def highlightBlock(self, text):
        # Mehrzeilige Kommentare markieren
        self.setCurrentBlockState(0)
        
        startIndex = 0
        if self.previousBlockState() != 1:
            startIndex = self.commentStartExpression.indexIn(text)
        
        while startIndex >= 0:
            endIndex = self.commentEndExpression.indexIn(text, startIndex)
            if endIndex == -1:
                self.setCurrentBlockState(1)
                commentLength = len(text) - startIndex
            else:
                commentLength = endIndex - startIndex + self.commentEndExpression.matchedLength()
            self.setFormat(startIndex, commentLength, self.multiLineCommentFormat)
            startIndex = self.commentStartExpression.indexIn(text, startIndex + commentLength)
        
        # Highlight single line comments
        single_line_comment_patterns = [r"//", r"\*\*", r"&&"]
        comment_positions = []
        
        # Suche nach einzeiligen Kommentaren und markiere sie
        for pattern in single_line_comment_patterns:
            for match in re.finditer(pattern, text):
                start = match.start()
                self.setFormat(start, len(text) - start, self.commentFormat)
                comment_positions.append((start, len(text) - start))
        
        # Suche nach Keywords und markiere sie
        for word in self.keywords:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            for match in pattern.finditer(text):
                start = match.start()
                length = match.end() - start
                
                # Prüfen, ob das Keyword in einem Kommentar steht
                in_comment = any(start >= pos[0] and start < pos[0] + pos[1] for pos in comment_positions)
                
                # Prüfen, ob das Keyword in einem mehrzeiligen Kommentar steht
                if self.previousBlockState() != 1 and not in_comment:
                    self.setFormat(start, length, self.boldFormat)

class EditorTextEdit(QPlainTextEdit):
    def __init__(self, file_name):
        super().__init__()
        self.lineNumberArea = LineNumberArea(self)
        self.bookmarks = set()
        self.highlighter = CppSyntaxHighlighter(self.document())
        
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        
        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()
        
        # Schriftgröße und Schriftart setzen
        self.setFont(QFont("Consolas", 12))
        
        with open(file_name, 'r') as file:
            text = file.read()
            file.close()
        
        self.setPlainText(text)
    
    def lineNumberAreaWidth(self):
        digits = 1
        max_num = max(1, self.blockCount())
        while max_num >= 10:
            max_num /= 10
            digits += 1
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        icon_space = 20  # Platz für die Icons
        return space + icon_space
    
    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)
    
    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())
        
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))
    
    def highlightCurrentLine(self):
        extraSelections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            
            lineColor = QColor(Qt.yellow).lighter(160)
            
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)
        
        self.setExtraSelections(extraSelections)
    
    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), Qt.lightGray)
        
        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(Qt.black)
                rect = QRect(20, int(top), self.lineNumberArea.width() - 20, self.fontMetrics().height())
                painter.drawText(rect, Qt.AlignRight, number)
                
                # Zeichnen des Icons
                icon_rect = QRect(0, int(top), 20, self.fontMetrics().height())
                if blockNumber in self.bookmarks:
                    painter.setBrush(Qt.red)
                    painter.drawEllipse(icon_rect.center(), 5, 5)
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            blockNumber += 1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            cursor = self.cursorForPosition(event.pos())
            block = cursor.block()
            block_number = block.blockNumber()
            top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
            bottom = top + self.blockBoundingRect(block).height()
            
            # Überprüfen, ob der Klick innerhalb der Linie liegt
            if int(top) <= event.pos().y() <= int(bottom):
                if block_number in self.bookmarks:
                    self.bookmarks.remove(block_number)
                else:
                    self.bookmarks.add(block_number)
                self.lineNumberArea.update()
        
        super().mousePressEvent(event)

class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
    
    def sizeHint(self):
        return QSize(self.editor.lineNumberAreaWidth(), 0)
    
    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)
        self.setFont(QFont("Consolas", 12))  # Schriftgröße und Schriftart für Zeilennummerbereich setzen


class myGridViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.parent = parent
        positions   = [(i, j) for i in range(3) for j in range(3)]
        
        self.layout           = QGridLayout()
        self.property_layout  = QVBoxLayout()
        
        self.layout         .setContentsMargins(0,0,0,0)
        self.property_layout.setContentsMargins(0,0,0,0)
        
        font1 = QFont("Arial", 10); font1.setBold(False)
        font2 = QFont("Arial", 10); font2.setBold(True)
        
        self.object_inspector = QTreeWidget()
        self.object_inspector.setIconSize(QSize(20,20))
        self.object_inspector.setFont(font1)
        self.object_inspector.setStyleSheet(_("inspect_css"))
        
        headerLabel = ["Name", "Count"]
        self.object_inspector.setColumnCount(len(headerLabel))
        self.object_inspector.setHeaderLabels(headerLabel)
        #
        addInspectorItem(self,"Objects's"  ,   0)
        addInspectorItem(self,"Classes"    ,   0)
        addInspectorItem(self,"Procedure's", 100)
        addInspectorItem(self,"Function's" , 200)
        addInspectorItem(self,"Variable's" , 300)
        
        
        self.property_page  = QTabWidget()
        self.property_page.setContentsMargins(0,0,0,0)
        self.property_page.setMinimumWidth(244)
        self.property_page.setMaximumWidth(244)
        self.property_page.setStyleSheet(_("tab_widget_2"))
        #
        self.property_tabs1 = QWidget()
        self.property_tabs2 = QWidget()
        #
        self.property_tabs1.setContentsMargins(0,0,0,0)
        self.property_tabs2.setContentsMargins(0,0,0,0)
        #
        self.property_tabs1.setMinimumWidth(244)
        self.property_tabs1.setMaximumWidth(244)
        #
        self.property_tabs2.setMinimumWidth(244)
        self.property_tabs2.setMaximumWidth(244)
        #
        self.property_tabs1.setStyleSheet("background-color:lightgray;")
        self.property_tabs2.setStyleSheet("background-color:lightgray;")
        #
        
        self.property_page.addTab(self.property_tabs1,"Properties")
        self.property_page.addTab(self.property_tabs2,"Events")
        
        self.pos_scroll_widget = QWidget()
        self.pos_scroll_widget.setContentsMargins(0,0,0,0)
        #
        self.evt_scroll_widget = QWidget()
        self.evt_scroll_widget.setContentsMargins(0,0,0,0)
                
        self.pos_vbox_layout = QVBoxLayout(); self.pos_vbox_layout.setContentsMargins(0,0,0,0)
        self.evt_vbox_layout = QVBoxLayout(); self.evt_vbox_layout.setContentsMargins(0,0,0,0)
        
        ### hier
        self.pos_cat1 = addPropertyCat(self,"Position")
        self.pos_cat1_prop_width  = addProperty(self, 1,"Width")
        self.pos_cat1_prop_height = addProperty(self, 1,"Height")
        self.pos_cat1_prop_top    = addProperty(self, 1,"Top")
        self.pos_cat1_prop_left   = addProperty(self, 1,"Left")
        
        self.pos_cat2 = addPropertyCat(self,"Font")
        self.pos_cat2_font_name      = addProperty(self,2,"Name")
        self.pos_cat2_font_size      = addProperty(self,1,"Size")
        self.pos_cat2_font_color_fg  = addProperty(self,4,"Foreground")
        self.pos_cat2_font_color_bg  = addProperty(self,4,"Background")
        self.pos_cat2_font_bold      = addProperty(self,3,"Bold")
        self.pos_cat2_font_italic    = addProperty(self,3,"Italic")
        self.pos_cat2_font_underline = addProperty(self,3,"Underline")
        self.pos_cat2_font_strike    = addProperty(self,3,"Strike")
        
        self.pos_cat3 = addPropertyCat(self,"Text")
        self.pos_cat3_object_name = addProperty(self,2,"Caption")
        self.pos_cat3_object_id   = addProperty(self,2,"Name")
        
        self.pos_cat4 = addPropertyCat(self,"Appearence")
        self.pos_cat4_background_color = addProperty(self,4,"BackColor")
        self.pos_cat4_border_color     = addProperty(self,4,"Border Color")
        self.pos_cat4_border_size      = addProperty(self,1,"Border Size")
        self.pos_cat4_border_radius    = addProperty(self,1,"Border Radius")
        self.pos_cat4_border_type      = addProperty(self,4,"Border Type")
        
        self.pos_cat5 = addPropertyCat(self,"Application")
        self.pos_cat4_app_name     = addProperty(self,2,"Name")
        self.pos_cat4_app_helpfile = addProperty(self,2,"Helpfile")
        self.pos_cat5_aüü_helpstr  = addProperty(self,2,"Help URL")
        self.pos_cat5_app_helpid   = addProperty(self,2,"Help ID")
        ####
        
        self.evt_on_enter       = addEventField(self,"OnGotFocus")
        self.evt_on_leave       = addEventField(self,"OnLeftFocus")
        self.evt_on_key_down    = addEventField(self,"OnKeyDown")
        self.evt_on_key_press   = addEventField(self,"OnKeyPress")
        self.evt_on_key_up      = addEventField(self,"OnKeyUp")
        self.evt_on_mouse_down  = addEventField(self,"OnMouseDown")
        self.evt_on_mouse_press = addEventField(self,"OnMousePress")
        self.evt_on_mouse_up    = addEventField(self,"OnMouseUp")
        
        self.evt_on_form_create = addEventField(self,"OnFormCreate")
        self.evt_on_form_close  = addEventField(self,"OnFormClose")
        self.evt_on_form_show   = addEventField(self,"OnFormShow")
        ### da
        #
        self.pos_scroll_widget.setLayout(self.pos_vbox_layout)
        self.evt_scroll_widget.setLayout(self.evt_vbox_layout)
        
        self.scroll = QScrollArea()
        self.scroll.setContentsMargins(0,0,0,0)
        self.scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll.setWidgetResizable(True)
        self.scroll.setWidget(self.pos_scroll_widget)
        #
        self.scroll2 = QScrollArea()
        self.scroll2.setContentsMargins(0,0,0,0)
        self.scroll2.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll2.setMinimumWidth(244)
        self.scroll2.setMaximumWidth(244)
        self.scroll2.setWidgetResizable(True)
        self.scroll2.setWidget(self.evt_scroll_widget)
        
        self.vl = QVBoxLayout()
        self.vl.setContentsMargins(0,0,0,0)
        self.vl.addWidget(self.scroll)
        self.property_tabs1.setLayout(self.vl)
        #
        self.vl2 = QVBoxLayout()
        self.vl2.setContentsMargins(0,0,0,0)
        self.vl2.addWidget(self.scroll2)
        self.property_tabs2.setLayout(self.vl2)
        
        
        self.property_top    = QLabel("Object Inspector:")
        self.property_bottom = QLabel("B")
        #
        self.set_style(self.property_top)
        self.set_style(self.property_bottom)
        ####
        
        self.scroll_up    = QLabel("A"); self.scroll_up   .setFont(font1)
        self.scroll_down  = QLabel("B"); self.scroll_down .setFont(font1)
        self.scroll_left  = QLabel("C"); self.scroll_left .setFont(font1)
        self.scroll_right = QLabel("D"); self.scroll_right.setFont(font1)
        
        self.set_style(self.scroll_right)
        self.set_style(self.scroll_up)
        self.set_style(self.scroll_down)
        self.set_style(self.scroll_left)
        
        self.scroll_up   .setMaximumHeight(16)
        self.scroll_down .setMaximumHeight(16)
        #
        self.scroll_right.setMaximumWidth (16)
        self.scroll_left .setMaximumWidth (16)
        #
        self.content = myGridViewerOverlay(self.parent)
        #
        self.layout.addWidget(self.property_top   , 0,0)
        self.layout.addWidget(self.property_bottom, 2,0)
        #
        
        self.property_object = QGridLayout()
        self.property_object.setContentsMargins(0,0,0,0)
        self.property_object.addWidget(self.object_inspector,0,0)
        self.property_object.addWidget(self.property_page   ,1,0)
        #
        self.object_widget = QWidget()
        self.object_widget.setMaximumWidth(245)
        self.object_widget.setLayout(self.property_object)
        
        self.layout.addWidget(self.scroll_up    , 0,2)
        self.layout.addWidget(self.scroll_left  , 1,1)
        self.layout.addWidget(self.object_widget, 1,0)
        self.layout.addWidget(self.content      , 1,2)
        self.layout.addWidget(self.scroll_right , 1,3)
        self.layout.addWidget(self.scroll_down  , 2,2)
        #
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        #
        chr3 = "{0}".format(u'\u25c4')  # /\
        chr4 = "{0}".format(u'\u25ba')  # \/
        #
        self.scroll_right.setText(chr2)
        self.scroll_left .setText(chr1)
        self.scroll_up   .setText(chr3)
        self.scroll_down .setText(chr4)
        #
        self.scroll_down .setAlignment(Qt.AlignCenter)
        self.scroll_up   .setAlignment(Qt.AlignCenter)
        #
        self.setLayout(self.layout)
    
    def set_style(self, obj):
        obj.setStyleSheet("background-color:lightgray;")

class MySQLDialog(QFrame):
    def __init__(self, text):
        super().__init__()
        
        font = QFont("Arial", 10)
        font.setBold(True)
        
        self.setFrameShape(QFrame.StyledPanel)
        self.setContentsMargins(1,1,1,1)
        self.setMouseTracking(True)
        self.dragging = False
        
        self.setMaximumHeight(200)
        self.setMaximumWidth (100)
        
        self.titlebar = QWidget(self)
        self.titlebar.move(0,0)
        self.titlebar.resize(200,21)
        self.titlebar.setMaximumHeight(21)
        self.titlebar.setStyleSheet("border:1px solid black;background-color:yellow;")
        
        self.title = QLabel(text, self.titlebar)
        self.title.setStyleSheet("border:0px solid yellow;")
        self.title.setFont(font)
        self.title.move(3,3)
        
        self.close_btn = QWidget(self.titlebar)
        self.close_btn.setStyleSheet("background-color:red;")
        self.close_btn.move(74,2)
        self.close_btn.resize(20,20)
        
        self.close_btn_lbl = closeLabelX(" X ", self)
        self.close_btn_lbl.setStyleSheet("color: white;font-weight:bold;")
        
        
        self.textw = QWidget()
        self.setStyleSheet("background-color:white;")
        
        self.hlayout = QVBoxLayout()
        self.check_box_1 = QCheckBox("FiELD A")
        self.check_box_2 = QCheckBox("FiELD B")
        #
        self.hlayout.addWidget(self.check_box_1)
        self.hlayout.addWidget(self.check_box_2)
        
        
        layout = QVBoxLayout()
        layout.setContentsMargins(1,1,1,1)
        layout.addWidget(self.titlebar)
        layout.addLayout(self.hlayout)
        layout.addWidget(self.textw)
        
        
        self.setLayout(layout)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = QPoint(event.globalPos() - self.mapToGlobal(self.drag_start_position))
            self.move(self.x() + delta.x(), self.y() + delta.y())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

class addDesignerTabs():
    def __init__(self, tab):
        self.tab = tab
        liste = [
            ["Standard", [
                "tmouse","tmainmenu","tpopupmenu","tlabel","tbutton","tedit","tmemo",
                "tlistbox","ttreeview","tcombobox","tradiobutton"
                ],
            ],
            ["System", [
                ],
            ],
            ["Data Controls", [
                ],
            ],
            ["Dialogs", [
                ],
            ],
            ["Indy Client", [
                ],
            ],
            ["Indy Server", [
                ],
            ],
        ]
        for tabitem in liste:
            tab_widget = QWidget()
            self.tab.addTab(tab_widget,tabitem[0])
            self._listwidget = QListWidget(tab_widget)
            self._listwidget.setViewMode(QListView.IconMode)
            self._listwidget.setResizeMode(QListView.Adjust)
            self._listwidget.setMinimumWidth(500)
            if len(tabitem[1]) > 0:
                for item in tabitem[1]:
                    list_item = QListWidgetItem("", self._listwidget)
                    list_item.setIcon(QIcon(__app__img__int__ + item + "_150.bmp"))

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
    
    # --------------------
    # dialog exit ? ...
    # --------------------
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            exitBox = myExitDialog(_("Exit Dialog"))
            exitBox.exec_()
        else:
            super().keyPressEvent(event)
    
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
        print("---> " + self.tab0_path_file)
        return
    
    def tab1_file_list_clicked(self, index):
        self.tab1_path_file = self.tab1_dir_model.fileInfo(index).absoluteFilePath()
        self.tab1_path_lineEdit.setText(f"{self.tab1_path_file}")
        return
    
    def populate_tree_view(self, file_path, icon):
        with open(file_path, 'r') as file:
            roots = []
            stack = [self.tab2_tree_model.invisibleRootItem()]
            
            self.topic_counter = 1
            
            for line in file:
                line = line.rstrip('\n')
                num_plus = 0
                while line[num_plus] == '+':
                    num_plus += 1
                
                item_name = line.strip('+').strip()
                
                new_item = QStandardItem(item_name)
                new_item.setIcon(QIcon(icon))
                
                global item2
                item1 = QStandardItem(str(self.topic_counter))
                item2 = QStandardItem(" ") #item2.setIcon(QIcon(icon))
                item3 = QStandardItem(" ")
                item4 = QStandardItem(" ")
                
                self.my_list.add(self.topic_counter, item1)
                
                self.topic_counter = self.topic_counter + 1
                
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
        
    def init_ui(self):
        # mouse tracking
        self.setMouseTracking(True)
        # Layout
        #self.setMaximumWidth (1024)
        self.setMinimumWidth (1200)
        #
        #self.setMaximumHeight(730)
        #self.setMaximumHeight(730)
        
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
        
        self.tool_bar_action_new1 = QAction(QIcon(__app__img__int__ + "floppy-disk" + __app__img_ext__), "Flopp", self)
        self.tool_bar_action_new2 = QAction(QIcon(__app__img__int__ + "floppy-disk" + __app__img_ext__), "Flopp", self)
        self.tool_bar_action_new3 = QAction(QIcon(__app__img__int__ + "floppy-disk" + __app__img_ext__), "Flopp", self)
        
        self.tool_bar.addAction(self.tool_bar_action_new1)
        self.tool_bar.addAction(self.tool_bar_action_new2)
        self.tool_bar.addAction(self.tool_bar_action_new3)
        
        self.tool_bar.addWidget(self.tool_bar_button_exit)
        
        self.layout.addWidget(self.tool_bar)
        self.tool_bar.show()
        
        # status bar
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Ready", 0)
        self.status_bar.setStyleSheet("background-color:gray;")
        
        
        # side toolbar
        self.main_layout = QHBoxLayout()
        self.main_widget = QWidget()
        
        self.main_widget.setContentsMargins(0,0,0,0)
        self.main_widget.setStyleSheet("padding:0px;margin:0px;")
        
        
        self.side_scroll = QScrollArea()
        self.side_widget = QWidget()
        self.side_layout = QVBoxLayout()
        #
        self.side_widget.setContentsMargins(0,0,0,0)
        self.side_scroll.setContentsMargins(0,0,0,0)
        
        self.side_btn1 = myIconButton(self,  0, "Help"   , "Help Authoring for/with:\no doxygen\no HelpNDoc")
        self.side_btn2 = myIconButton(self,  1, "dBASE"  , "dBASE data base programming\nlike in the old days...\nbut with SQLite -- dBase keep alive !")
        self.side_btn3 = myIconButton(self,  2, "Pascal" , "Pascal old school programming\no Delphi\no FPC")
        self.side_btn4 = myIconButton(self,  3, "ISO C"  , "C / C++ embeded programming\nor cross platform")
        self.side_btn5 = myIconButton(self,  4, "Java"   , "Java modern cross programming\nfor any device")
        self.side_btn6 = myIconButton(self,  5, "Python" , "Python modern GUI programming\nlets rock AI\nand TensorFlow")
        self.side_btn7 = myIconButton(self,  6, "LISP"   , "LISP traditional programming\nultimate old school")
        #
        self.side_btnA = myIconButton(self, 10, "Locales", "" \
            + "Localization your Application with different supported languages\n" \
            + "around the World.\n" \
            + "Used tools are msgfmt - the Unix Tool for generationg .mo files.")
        #
        
        self.side_btn1.bordercolor = "lime"
        self.side_btn1.state       = 2
        self.side_btn1.set_style()
        
        self.side_widget.setMaximumWidth(120)
        self.side_widget.setLayout(self.side_layout)
        
        self.side_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.side_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.side_scroll.setWidgetResizable(True)
        self.side_scroll.setMinimumWidth(130)
        self.side_scroll.setMaximumWidth(130)
        self.side_scroll.setWidget(self.side_widget)
        
        ####
        self.main_layout.addWidget(self.side_scroll)
        
        
        
        # dbase
        self.dbase_tabs = QTabWidget()
        self.dbase_tabs.setStyleSheet(css_tabs)
        self.dbase_tabs.hide()
        
        self.dbase_tabs_project_widget = QWidget()
        self.dbase_tabs_editors_widget = QWidget()
        self.dbase_tabs_designs_widget = QWidget()
        self.dbase_tabs_builder_widget = QWidget()
        self.dbase_tabs_datatab_widget = QWidget()
        self.dbase_tabs_reports_widget = QWidget()
        #
        self.dbase_tabs.addTab(self.dbase_tabs_project_widget, "dBASE Project")
        self.dbase_tabs.addTab(self.dbase_tabs_editors_widget, "dBASE Editor")
        self.dbase_tabs.addTab(self.dbase_tabs_designs_widget, "dBASE Designer")
        self.dbase_tabs.addTab(self.dbase_tabs_builder_widget, "dBASE SQL Builder")
        self.dbase_tabs.addTab(self.dbase_tabs_datatab_widget, "dBASE Data Tables")
        self.dbase_tabs.addTab(self.dbase_tabs_reports_widget, "dBASE Reports")
        ####
        self.dbase_tabs_editors_layout = QVBoxLayout()
        self.dbase_tabs_editors_layout.setContentsMargins(2,2,2,2)
        
        self.dbase_tabs_editor_menu = QWidget()
        self.dbase_tabs_editor_menu.setStyleSheet("background-color:gray;")
        self.dbase_tabs_editor_menu.setMinimumHeight(64)
        #
        ####
        self.dbase_tabs_data_tables_layout = QVBoxLayout()
        self.dbase_tabs_data_tables_layout.setContentsMargins(2,2,2,2)
        
        self.dbase_tabs_data_tables_menu = QWidget()
        self.dbase_tabs_data_tables_menu.setStyleSheet("background-color:gray;")
        self.dbase_tabs_data_tables_menu.setMinimumHeight(64)
        #
        ####
        self.dbase_tabs_reports_layout = QVBoxLayout()
        self.dbase_tabs_reports_layout.setContentsMargins(2,2,2,2)
        
        self.dbase_tabs_reports_menu = QWidget()
        self.dbase_tabs_reports_menu.setStyleSheet("background-color:gray;")
        self.dbase_tabs_reports_menu.setMinimumHeight(64)
        #
        
        self.dbase_file_layout1 = QVBoxLayout()
        self.dbase_file_layout1.setContentsMargins(1,0,0,1)
        self.dbase_file_widget1 = QWidget()
        ####
        self.dbase_tabs_editor1 = EditorTextEdit("Example1.prg")
        self.dbase_file_layout1.addWidget(self.dbase_tabs_editor1)
        self.dbase_file_widget1.setLayout(self.dbase_file_layout1)
        #
        ####
        self.dbase_file_layout2 = QVBoxLayout()
        self.dbase_file_layout2.setContentsMargins(1,0,0,1)
        self.dbase_file_widget2 = QWidget()
        ####
        self.dbase_tabs_editor2 = EditorTextEdit("Example2.prg")
        self.dbase_file_layout2.addWidget(self.dbase_tabs_editor2)
        self.dbase_file_widget2.setLayout(self.dbase_file_layout2)
        #
        self.dbase_tabs_files  = QTabWidget()
        self.dbase_tabs_files.setStyleSheet(css_tabs)
        self.dbase_tabs_files.addTab(self.dbase_file_widget1, "Example1.prg")
        self.dbase_tabs_files.addTab(self.dbase_file_widget2, "Example2.prg")
        
        self.dbase_tabs_editors_layout.addWidget(self.dbase_tabs_editor_menu)
        self.dbase_tabs_editors_layout.addWidget(self.dbase_tabs_files)
        
        
        self.dbase_tabs_editors_widget.setLayout(self.dbase_tabs_editors_layout)
        ####
        self.dbase_builder_layout = QVBoxLayout()
        self.dbase_builder_layout.setContentsMargins(2,2,2,2)
        
        self.dbase_builder_widget_table = QWidget()
        self.dbase_builder_widget_table.setStyleSheet(_("bggy"))
        self.dbase_builder_widget_table.setMaximumHeight(56)
        
        self.dbase_builder_widget_view = myGridViewerOverlay(self.dbase_tabs_builder_widget)
        self.dbase_builder_widget_view.setLayout(QVBoxLayout())
        
        
        self.dbase_builder_window_1 = MySQLDialog("Table A")
        self.dbase_builder_window_2 = MySQLDialog("Table B")
        #
        self.dbase_builder_widget_view.layout().addWidget(self.dbase_builder_window_1)
        self.dbase_builder_widget_view.layout().addWidget(self.dbase_builder_window_2)
        
        self.dbase_builder_widget_join = QTableWidget()
        self.dbase_builder_widget_join.setStyleSheet(_("join_build"))
        
        self.dbase_builder_widget_join.horizontalHeader().setStretchLastSection(True) 
        self.dbase_builder_widget_join.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) 
        
        self.dbase_builder_widget_join.setRowCount(4)
        self.dbase_builder_widget_join.setColumnCount(4)
        
        self.dbase_builder_widget_join.setMinimumHeight(180)
        self.dbase_builder_widget_join.setMaximumHeight(180)
        
        
        self.dbase_builder_widget_join.setHorizontalHeaderLabels(["Table 1","Table2","TableA","TableB"])
        self.dbase_builder_widget_join.setVerticalHeaderLabels([" ID  "," ROW1  "," NAME  "," TEXT  "])
        
        header = self.dbase_builder_widget_join.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        
        self.dbase_builder_layout.addWidget(self.dbase_builder_widget_table)
        self.dbase_builder_layout.addWidget(self.dbase_builder_widget_view)
        self.dbase_builder_layout.addWidget(self.dbase_builder_widget_join)
        
        self.dbase_tabs_builder_widget.setLayout(self.dbase_builder_layout)
        
        ####
        self.dbase_designs_layout  = QVBoxLayout()
        self.dbase_designs_layout.setContentsMargins(2,2,2,2)
        self.dbase_designs_palette = QWidget()
        self.dbase_designs_palette.setStyleSheet(_("bggy"))
        self.dbase_designs_palette.setMinimumHeight(85)
        self.dbase_designs_palette.setMaximumHeight(85)
        #
        self.dbase_palette_layout  = QHBoxLayout()
        self.dbase_palette_layout.setContentsMargins(2,2,2,2)
        self.dbase_palette_widget_lhs  = QLabel ()
        self.dbase_palette_widget_mid  = QWidget()
        self.dbase_palette_widget_rhs  = QLabel ()
        #
        self.dbase_palette_widget_lhs.setMaximumWidth(20)
        self.dbase_palette_widget_rhs.setMaximumWidth(20)
        
        font = QFont("Times New Roman", 16)
        #font.setBold(True)
        
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        
        self.dbase_palette_widget_lhs.setFont(font)
        self.dbase_palette_widget_rhs.setFont(font)
        #
        self.dbase_palette_widget_lhs.setText(chr1)
        self.dbase_palette_widget_rhs.setText(chr2)
        #
        self.dbase_palette_widget_lhs.setStyleSheet(_("bglg"))
        self.dbase_palette_widget_mid.setStyleSheet(_("bggy"))
        self.dbase_palette_widget_rhs.setStyleSheet(_("bglg"))
        #
        #
        self.dbase_palette_widget_mid_layout = QHBoxLayout()
        self.dbase_palette_widget_mid_tabs   = QTabWidget()
        self.dbase_palette_widget_mid_tabs.setStyleSheet(_("designertab"))
        
        #######
        addDesignerTabs(self.dbase_palette_widget_mid_tabs)
        
        self.dbase_palette_widget_mid_layout.addWidget(self.dbase_palette_widget_mid_tabs)
        #
        self.dbase_palette_layout.addWidget(self.dbase_palette_widget_lhs)
        self.dbase_palette_layout.addLayout(self.dbase_palette_widget_mid_layout)
        self.dbase_palette_layout.addWidget(self.dbase_palette_widget_rhs)
        #
        self.dbase_designs_palette.setLayout(self.dbase_palette_layout)
        ####
        
        self.dbase_designs_viewer  = myGridViewer(self)
        self.dbase_designs_viewer.setStyleSheet(_("bgwh"))
        
        self.dbase_designs_layout.addWidget(self.dbase_designs_palette)
        self.dbase_designs_layout.addWidget(self.dbase_designs_viewer)
        #
        self.dbase_tabs_designs_widget.setLayout(self.dbase_designs_layout)
        ####
        self.main_layout.addWidget(self.dbase_tabs)
        #################
        font = QFont("Arial", 12)
        self.dbase_btn1 = myMoveButton(" move me A ", self.dbase_designs_viewer.content)
        self.dbase_btn2 = myMoveButton(" move me B ", self.dbase_designs_viewer.content)
        self.dbase_btn3 = myMoveButton(" move me C ", self.dbase_designs_viewer.content)
        #
        self.dbase_btn1.move(20,20)
        self.dbase_btn2.move(40,40)
        self.dbase_btn3.move(60,60)
        #
        self.dbase_btn1.setFont(font)
        self.dbase_btn2.setFont(font)
        self.dbase_btn3.setFont(font)
        #
        self.dbase_btn1.setStyleSheet("background-color:red;color:yellow;")
        self.dbase_btn2.setStyleSheet("background-color:yellow;color:black;")
        self.dbase_btn3.setStyleSheet("background-color:blue;color:white;")
        
        
        # pascal
        self.pascal_tabs = QTabWidget()
        self.pascal_tabs.setStyleSheet(css_tabs)
        self.pascal_tabs.hide()
        
        self.pascal_tabs_project_widget = QWidget()
        self.pascal_tabs_editors_widget = QWidget()
        self.pascal_tabs_designs_widget = QWidget()
        #
        self.pascal_tabs.addTab(self.pascal_tabs_project_widget, "Pascal Project")
        self.pascal_tabs.addTab(self.pascal_tabs_editors_widget, "Pascal Editor")
        self.pascal_tabs.addTab(self.pascal_tabs_designs_widget, "Pascal Designer")
        
        self.pascal_designs_layout  = QVBoxLayout()
        self.pascal_designs_layout.setContentsMargins(2,2,2,2)
        self.pascal_designs_palette = QWidget()
        self.pascal_designs_palette.setStyleSheet(_("bggy"))
        self.pascal_designs_palette.setMaximumHeight(80)
        #
        self.pascal_palette_layout  = QHBoxLayout()
        self.pascal_palette_layout.setContentsMargins(2,2,2,2)
        self.pascal_palette_widget_lhs  = QLabel ()
        self.pascal_palette_widget_mid  = QWidget()
        self.pascal_palette_widget_rhs  = QLabel ()
        #
        self.pascal_palette_widget_lhs.setMaximumWidth(20)
        self.pascal_palette_widget_rhs.setMaximumWidth(20)
        
        font = QFont("Times New Roman", 16)
        #font.setBold(True)
        
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        
        self.pascal_palette_widget_lhs.setFont(font)
        self.pascal_palette_widget_rhs.setFont(font)
        #
        self.pascal_palette_widget_lhs.setText(chr1)
        self.pascal_palette_widget_rhs.setText(chr2)
        #
        self.pascal_palette_widget_lhs.setStyleSheet(_("bglg"))
        self.pascal_palette_widget_mid.setStyleSheet(_("bgwh"))
        self.pascal_palette_widget_rhs.setStyleSheet(_("bglg"))
        #
        #
        self.pascal_palette_widget_mid_layout = QHBoxLayout()
        self.pascal_palette_widget_mid_tabs   = QTabWidget()
        self.pascal_palette_widget_mid_tabs.setStyleSheet(_("designertab"))
        
        #######
        addDesignerTabs(self.pascal_palette_widget_mid_tabs)
        
        self.pascal_palette_widget_mid_layout.addWidget(self.pascal_palette_widget_mid_tabs)
        #
        self.pascal_palette_layout.addWidget(self.pascal_palette_widget_lhs)
        self.pascal_palette_layout.addLayout(self.pascal_palette_widget_mid_layout)
        self.pascal_palette_layout.addWidget(self.pascal_palette_widget_rhs)
        #
        self.pascal_designs_palette.setLayout(self.pascal_palette_layout)
        ####
        
        self.pascal_designs_viewer  = myGridViewer(self)
        self.pascal_designs_viewer.setStyleSheet("background-color:cyan;")
        
        self.pascal_designs_layout.addWidget(self.pascal_designs_palette)
        self.pascal_designs_layout.addWidget(self.pascal_designs_viewer)
        #
        self.pascal_tabs_designs_widget.setLayout(self.pascal_designs_layout)
        ####
        self.main_layout.addWidget(self.pascal_tabs)
        #################
        self.pascal_btn1 = myMoveButton("move me D", self.pascal_designs_viewer)
        self.pascal_btn2 = myMoveButton("move me E", self.pascal_designs_viewer)
        self.pascal_btn3 = myMoveButton("move me F", self.pascal_designs_viewer)
        #
        self.pascal_btn1.move(120,20)
        self.pascal_btn2.move(140,40)
        self.pascal_btn3.move(160,60)
        
        # isoc
        self.isoc_tabs = QTabWidget()
        self.isoc_tabs.setStyleSheet(css_tabs)
        self.isoc_tabs.hide()
        
        self.isoc_tabs_project_widget = QWidget()
        self.isoc_tabs_editors_widget = QWidget()
        self.isoc_tabs_designs_widget = QWidget()
        #
        self.isoc_tabs.addTab(self.isoc_tabs_project_widget, "ISO C Project")
        self.isoc_tabs.addTab(self.isoc_tabs_editors_widget, "ISO C Editor")
        self.isoc_tabs.addTab(self.isoc_tabs_designs_widget, "ISO C Designer")
        
        self.isoc_designs_layout  = QVBoxLayout()
        self.isoc_designs_layout.setContentsMargins(2,2,2,2)
        self.isoc_designs_palette = QWidget()
        self.isoc_designs_palette.setStyleSheet(_("bggy"))
        self.isoc_designs_palette.setMaximumHeight(80)
        #
        self.isoc_palette_layout  = QHBoxLayout()
        self.isoc_palette_layout.setContentsMargins(2,2,2,2)
        self.isoc_palette_widget_lhs  = QLabel ()
        self.isoc_palette_widget_mid  = QWidget()
        self.isoc_palette_widget_rhs  = QLabel ()
        #
        self.isoc_palette_widget_lhs.setMaximumWidth(20)
        self.isoc_palette_widget_rhs.setMaximumWidth(20)
        
        font = QFont("Times New Roman", 16)
        #font.setBold(True)
        
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        
        self.isoc_palette_widget_lhs.setFont(font)
        self.isoc_palette_widget_rhs.setFont(font)
        #
        self.isoc_palette_widget_lhs.setText(chr1)
        self.isoc_palette_widget_rhs.setText(chr2)
        #
        self.isoc_palette_widget_lhs.setStyleSheet(_("bglg"))
        self.isoc_palette_widget_mid.setStyleSheet(_("bgwh"))
        self.isoc_palette_widget_rhs.setStyleSheet(_("bglg"))
        #
        #
        self.isoc_palette_widget_mid_layout = QHBoxLayout()
        self.isoc_palette_widget_mid_tabs   = QTabWidget()
        self.isoc_palette_widget_mid_tabs.setStyleSheet(_("designertab"))
        
        #######
        addDesignerTabs(self.isoc_palette_widget_mid_tabs)
        
        
        self.isoc_palette_widget_mid_layout.addWidget(self.isoc_palette_widget_mid_tabs)
        #
        self.isoc_palette_layout.addWidget(self.isoc_palette_widget_lhs)
        self.isoc_palette_layout.addLayout(self.isoc_palette_widget_mid_layout)
        self.isoc_palette_layout.addWidget(self.isoc_palette_widget_rhs)
        #
        self.isoc_designs_palette.setLayout(self.isoc_palette_layout)
        ####
        
        self.isoc_designs_viewer  = myGridViewer(self)
        self.isoc_designs_viewer.setStyleSheet("background-color:cyan;")
        
        self.isoc_designs_layout.addWidget(self.isoc_designs_palette)
        self.isoc_designs_layout.addWidget(self.isoc_designs_viewer)
        #
        self.isoc_tabs_designs_widget.setLayout(self.isoc_designs_layout)
        ####
        self.main_layout.addWidget(self.isoc_tabs)
        
        # java
        self.java_tabs = QTabWidget()
        self.java_tabs.setStyleSheet(css_tabs)
        self.java_tabs.hide()
        
        self.java_tabs_project_widget = QWidget()
        self.java_tabs_editors_widget = QWidget()
        self.java_tabs_designs_widget = QWidget()
        #
        self.java_tabs.addTab(self.java_tabs_project_widget, "Java Project")
        self.java_tabs.addTab(self.java_tabs_editors_widget, "Java Editor")
        self.java_tabs.addTab(self.java_tabs_designs_widget, "Java Designer")
        
        self.java_designs_layout  = QVBoxLayout()
        self.java_designs_layout.setContentsMargins(2,2,2,2)
        self.java_designs_palette = QWidget()
        self.java_designs_palette.setStyleSheet(_("bggy"))
        self.java_designs_palette.setMaximumHeight(80)
        #
        self.java_palette_layout  = QHBoxLayout()
        self.java_palette_layout.setContentsMargins(2,2,2,2)
        self.java_palette_widget_lhs  = QLabel ()
        self.java_palette_widget_mid  = QWidget()
        self.java_palette_widget_rhs  = QLabel ()
        #
        self.java_palette_widget_lhs.setMaximumWidth(20)
        self.java_palette_widget_rhs.setMaximumWidth(20)
        
        font = QFont("Times New Roman", 16)
        #font.setBold(True)
        
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        
        self.java_palette_widget_lhs.setFont(font)
        self.java_palette_widget_rhs.setFont(font)
        #
        self.java_palette_widget_lhs.setText(chr1)
        self.java_palette_widget_rhs.setText(chr2)
        #
        self.java_palette_widget_lhs.setStyleSheet(_("bglg"))
        self.java_palette_widget_mid.setStyleSheet(_("bgwh"))
        self.java_palette_widget_rhs.setStyleSheet(_("bglg"))
        #
        #
        self.java_palette_widget_mid_layout = QHBoxLayout()
        self.java_palette_widget_mid_tabs   = QTabWidget()
        self.java_palette_widget_mid_tabs.setStyleSheet(_("designertab"))
        
        #######
        addDesignerTabs(self.java_palette_widget_mid_tabs)
        
        
        self.java_palette_widget_mid_layout.addWidget(self.java_palette_widget_mid_tabs)
        #
        self.java_palette_layout.addWidget(self.java_palette_widget_lhs)
        self.java_palette_layout.addLayout(self.java_palette_widget_mid_layout)
        self.java_palette_layout.addWidget(self.java_palette_widget_rhs)
        #
        self.java_designs_palette.setLayout(self.java_palette_layout)
        ####
        
        self.java_designs_viewer  = myGridViewer(self)
        self.java_designs_viewer.setStyleSheet("background-color:cyan;")
        
        self.java_designs_layout.addWidget(self.java_designs_palette)
        self.java_designs_layout.addWidget(self.java_designs_viewer)
        #
        self.java_tabs_designs_widget.setLayout(self.java_designs_layout)
        ####
        self.main_layout.addWidget(self.java_tabs)
        
        # python
        self.python_tabs = QTabWidget()
        self.python_tabs.setStyleSheet(css_tabs)
        self.python_tabs.hide()
        
        self.python_tabs_project_widget = QWidget()
        self.python_tabs_editors_widget = QWidget()
        self.python_tabs_designs_widget = QWidget()
        #
        self.python_tabs.addTab(self.python_tabs_project_widget, "Python Project")
        self.python_tabs.addTab(self.python_tabs_editors_widget, "Python Editor")
        self.python_tabs.addTab(self.python_tabs_designs_widget, "Python Designer")
        
        self.python_designs_layout  = QVBoxLayout()
        self.python_designs_layout.setContentsMargins(2,2,2,2)
        self.python_designs_palette = QWidget()
        self.python_designs_palette.setStyleSheet(_("bggy"))
        self.python_designs_palette.setMaximumHeight(80)
        #
        self.python_palette_layout  = QHBoxLayout()
        self.python_palette_layout.setContentsMargins(2,2,2,2)
        self.python_palette_widget_lhs  = QLabel ()
        self.python_palette_widget_mid  = QWidget()
        self.python_palette_widget_rhs  = QLabel ()
        #
        self.python_palette_widget_lhs.setMaximumWidth(20)
        self.python_palette_widget_rhs.setMaximumWidth(20)
        
        font = QFont("Times New Roman", 16)
        #font.setBold(True)
        
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        
        self.python_palette_widget_lhs.setFont(font)
        self.python_palette_widget_rhs.setFont(font)
        #
        self.python_palette_widget_lhs.setText(chr1)
        self.python_palette_widget_rhs.setText(chr2)
        #
        self.python_palette_widget_lhs.setStyleSheet(_("bglg"))
        self.python_palette_widget_mid.setStyleSheet(_("bgwh"))
        self.python_palette_widget_rhs.setStyleSheet(_("bglg"))
        #
        #
        self.python_palette_widget_mid_layout = QHBoxLayout()
        self.python_palette_widget_mid_tabs   = QTabWidget()
        self.python_palette_widget_mid_tabs.setStyleSheet(_("designertab"))
        
        #######
        addDesignerTabs(self.python_palette_widget_mid_tabs)
        
        self.python_palette_widget_mid_layout.addWidget(self.python_palette_widget_mid_tabs)
        #
        self.python_palette_layout.addWidget(self.python_palette_widget_lhs)
        self.python_palette_layout.addLayout(self.python_palette_widget_mid_layout)
        self.python_palette_layout.addWidget(self.python_palette_widget_rhs)
        #
        self.python_designs_palette.setLayout(self.python_palette_layout)
        ####
        
        self.python_designs_viewer  = myGridViewer(self)
        self.python_designs_viewer.setStyleSheet("background-color:cyan;")
        
        self.python_designs_layout.addWidget(self.python_designs_palette)
        self.python_designs_layout.addWidget(self.python_designs_viewer)
        #
        self.python_tabs_designs_widget.setLayout(self.python_designs_layout)
        ####
        self.main_layout.addWidget(self.python_tabs)
        
        
        # lisp
        self.lisp_tabs = QTabWidget()
        self.lisp_tabs.setStyleSheet(css_tabs)
        self.lisp_tabs.hide()
        
        self.lisp_tabs_project_widget = QWidget()
        self.lisp_tabs_editors_widget = QWidget()
        self.lisp_tabs_designs_widget = QWidget()
        #
        self.lisp_tabs.addTab(self.lisp_tabs_project_widget, "LISP Project")
        self.lisp_tabs.addTab(self.lisp_tabs_editors_widget, "LISP Editor")
        self.lisp_tabs.addTab(self.lisp_tabs_designs_widget, "LISP Designer")
        
        self.lisp_designs_layout  = QVBoxLayout()
        self.lisp_designs_layout.setContentsMargins(2,2,2,2)
        self.lisp_designs_palette = QWidget()
        self.lisp_designs_palette.setStyleSheet(_("bggy"))
        self.lisp_designs_palette.setMaximumHeight(80)
        #
        self.lisp_palette_layout  = QHBoxLayout()
        self.lisp_palette_layout.setContentsMargins(2,2,2,2)
        self.lisp_palette_widget_lhs  = QLabel ()
        self.lisp_palette_widget_mid  = QWidget()
        self.lisp_palette_widget_rhs  = QLabel ()
        #
        self.lisp_palette_widget_lhs.setMaximumWidth(20)
        self.lisp_palette_widget_rhs.setMaximumWidth(20)
        
        font = QFont("Times New Roman", 16)
        #font.setBold(True)
        
        chr1 = "{0}".format(u'\u25c4')  # <<
        chr2 = "{0}".format(u'\u25ba')  # >>
        
        self.lisp_palette_widget_lhs.setFont(font)
        self.lisp_palette_widget_rhs.setFont(font)
        #
        self.lisp_palette_widget_lhs.setText(chr1)
        self.lisp_palette_widget_rhs.setText(chr2)
        #
        self.lisp_palette_widget_lhs.setStyleSheet(_("bglg"))
        self.lisp_palette_widget_mid.setStyleSheet(_("bgwh"))
        self.lisp_palette_widget_rhs.setStyleSheet(_("bglg"))
        #
        #
        self.lisp_palette_widget_mid_layout = QHBoxLayout()
        self.lisp_palette_widget_mid_tabs   = QTabWidget()
        self.lisp_palette_widget_mid_tabs.setStyleSheet(_("designertab"))
        
        #######
        addDesignerTabs(self.lisp_palette_widget_mid_tabs)
        
        self.lisp_palette_widget_mid_layout.addWidget(self.lisp_palette_widget_mid_tabs)
        #
        self.lisp_palette_layout.addWidget(self.lisp_palette_widget_lhs)
        self.lisp_palette_layout.addLayout(self.lisp_palette_widget_mid_layout)
        self.lisp_palette_layout.addWidget(self.lisp_palette_widget_rhs)
        #
        self.lisp_designs_palette.setLayout(self.lisp_palette_layout)
        ####
        
        self.lisp_designs_viewer  = myGridViewer(self)
        self.lisp_designs_viewer.setStyleSheet("background-color:cyan;")
        
        self.lisp_designs_layout.addWidget(self.lisp_designs_palette)
        self.lisp_designs_layout.addWidget(self.lisp_designs_viewer)
        #
        self.lisp_tabs_designs_widget.setLayout(self.lisp_designs_layout)
        ####
        self.main_layout.addWidget(self.lisp_tabs)
        
        
        
        # locale
        self.locale_tabs = QTabWidget()
        self.locale_tabs.setStyleSheet(css_tabs)
        self.locale_tabs.hide()
        
        self.locale_tabs_project_widget = QWidget()
        self.locale_tabs_editors_widget = QWidget()
        self.locale_tabs_designs_widget = QWidget()
        #
        self.locale_tabs.addTab(self.locale_tabs_project_widget, "Locales Project")
        self.locale_tabs.addTab(self.locale_tabs_editors_widget, "Locales Editor")
        self.locale_tabs.addTab(self.locale_tabs_designs_widget, "Locales Designer")
        ####
        self.main_layout.addWidget(self.locale_tabs)
        
        
        
        # first register card - action's ...
        self.help_tabs = QTabWidget()
        self.help_tabs.setStyleSheet(css_tabs)
        
        # help
        self.tab0_0 = QWidget()
        self.tab1_0 = QWidget()
        self.tab2   = QWidget()
        self.tab3   = QWidget()
        self.tab4   = QWidget()
        
        # add tabs
        self.help_tabs.addTab(self.tab0_0, "Help Project")
        self.help_tabs.addTab(self.tab1_0, "Pre-/Post Actions")
        self.help_tabs.addTab(self.tab2, "Topics")
        self.help_tabs.addTab(self.tab3, "DoxyGen")
        self.help_tabs.addTab(self.tab4, "Content")
        
        self.tab_widget_tabs = QTabWidget(self.tab4)
        self.tab_widget_tabs.setMinimumWidth(830)
        self.tab_widget_tabs.setMinimumHeight(650)
        self.tab_dbase  = QWidget()
        self.tab_pascal = QWidget()
        self.tab_html   = QWidget()
        self.tab_widget_tabs.addTab(self.tab_dbase , "dBase" )
        self.tab_widget_tabs.addTab(self.tab_pascal, "Pascal")
        self.tab_widget_tabs.addTab(self.tab_html  , "HTML"  )
        
        
        self.tab_dbase_layout = QVBoxLayout(self.tab_dbase)
        self.tab_dbase_layout.setAlignment(Qt.AlignTop)
        self.tab_dbase_editor = myDBaseTextEditor(self)
        self.tab_dbase_layout.addWidget(self.tab_dbase_editor)
        
        #
        self.main_layout.addWidget(self.help_tabs)
        
        self.tab_html.setMinimumWidth(500)
        self.tab_html.setMaximumHeight(500)
        
        # create project tab
        self.tab2_top_layout = QHBoxLayout(self.tab2)
        self.tab3_top_layout = QHBoxLayout(self.tab3)
        self.tab4_top_layout = QHBoxLayout(self.tab_widget_tabs)
        self.tab5_top_layout = QHBoxLayout(self.tab_html)
        
        ####
        # devices
        font = QFont("Arial",14)
        font.setBold(True)
        
        ####
        self.devices_scroll = QScrollArea()
        self.devices_widget = QWidget()
        self.devices_layout = QVBoxLayout()
        
        #
        self.devices_scroll.setMinimumWidth(240)
        self.devices_scroll.setMaximumWidth(240)
        #
        self.devices_widget.setMinimumWidth(240)
        self.devices_widget.setMaximumWidth(240)
        #
        self.devices_widget.setContentsMargins(1,0,0,1)
        self.devices_layout.setContentsMargins(1,0,0,1)
        
        self.devices_label_printers = QPushButton("  Printers:  ")
        self.devices_label_printers.setMinimumWidth(240)
        self.devices_label_printers.setMaximumWidth(240)
        self.devices_label_printers.setFont(font)
        self.devices_layout.addWidget(self.devices_label_printers)
        #
        self.devices_list_printers = QListWidget()
        self.devices_list_printers.setIconSize(QSize(40,40))
        self.devices_list_printers.setFont(font)
        self.devices_layout.addWidget(self.devices_list_printers)
        
        #
        items = [
            {"text": "Printer p:1", "icon": __app__img__int__ + "printer" + __app__img_ext__ },
            {"text": "Printer p:2", "icon": __app__img__int__ + "printer" + __app__img_ext__ },
            {"text": "Printer p:3", "icon": __app__img__int__ + "printer" + __app__img_ext__ }
        ]
        for item in items:
            devices_list_item = QListWidgetItem(item["text"])
            devices_list_item.setIcon(QIcon(item["icon"]))
            self.devices_list_printers.addItem(devices_list_item)
        #
        
        
        self.devices_tabs_storages = QPushButton()
        self.devices_tabs_storages.setText("  Storages:  ")
        self.devices_tabs_storages.setFont(font)
        self.devices_layout.addWidget(self.devices_tabs_storages)
        #
        self.devices_list_storages = QListWidget()
        self.devices_list_storages.move(0,264)
        self.devices_list_storages.setIconSize(QSize(40,40))
        self.devices_list_storages.setFont(font)
        self.devices_layout.addWidget(self.devices_list_storages)
        #
        items = [
            {"text": "Storage  s:1", "icon": __app__img__int__ + "storage"  + __app__img_ext__ },
            {"text": "Database d:2", "icon": __app__img__int__ + "database" + __app__img_ext__ },
            {"text": "Database d:3", "icon": __app__img__int__ + "database" + __app__img_ext__ }
        ]
        for item in items:
            devices_list_item = QListWidgetItem(item["text"])
            devices_list_item.setIcon(QIcon(item["icon"]))
            self.devices_list_storages.addItem(devices_list_item)
        #
        
        
        self.devices_tabs_label3 = QPushButton()
        self.devices_tabs_label3.setText("  Team Server:  ")
        self.devices_tabs_label3.setFont(font)
        self.devices_layout.addWidget(self.devices_tabs_label3)
        #
        self.devices_list_widget3 = QListWidget()
        self.devices_list_widget3.setMaximumHeight(100)
        self.devices_list_widget3.setIconSize(QSize(40,40))
        self.devices_list_widget3.setFont(font)
        self.devices_layout.addWidget(self.devices_list_widget3)
        #
        items = [
            {"text": "Meeting m:1", "icon": __app__img__int__ + "meeting" + __app__img_ext__ },
            {"text": "Session c:2", "icon": __app__img__int__ + "session" + __app__img_ext__ }
        ]
        for item in items:
            devices_list_item = QListWidgetItem(item["text"])
            devices_list_item.setIcon(QIcon(item["icon"]))
            self.devices_list_widget3.addItem(devices_list_item)
        #
        
        self.devices_widget.setLayout(self.devices_layout)
        
        self.devices_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.devices_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.devices_scroll.setWidgetResizable(True)
        self.devices_scroll.setLayout(self.devices_layout)
        #
        #
        self.dl = QVBoxLayout()
        self.dl.setContentsMargins(1,0,0,1)
        self.dl.addWidget(self.devices_scroll)
        ####
        self.main_layout.addLayout(self.dl)
        
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
        
        tab1_classes = []
        i = 5
        while i < 23:
            s = "customScrollView_" + str(i)
            i = i + 1
            tab1_classes.append(s)
        
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
        
        self.sv_2_1.show()
        self.hw_2 = QWidget()
        
        list_layout_b.addWidget(sv_help)
        ########################
        self.tab3_top_layout.addWidget(self.tab_widget_1)
        
        
        self.tab2_file_path = __app__internal__ + "/topics.txt"
        
        global tab2_tree_view
        tab2_tree_view = QTreeView()
        tab2_tree_view.setStyleSheet(_(css_model_header))
        self.tab2_tree_model = QStandardItemModel()
        self.tab2_tree_model.setHorizontalHeaderLabels(["Topic name", "ID", "Status", "Help icon", "In Build"])
        tab2_tree_view.setModel(self.tab2_tree_model)
        
        self.tab2_top_layout.addWidget(tab2_tree_view)
        self.populate_tree_view(self.tab2_file_path, __app__img__int__ + "open-folder" + __app__img_ext__)
        
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
        self.tab0_top_layout    = QHBoxLayout(self.tab0_0)
        self.tab0_left_layout   = QVBoxLayout()
        
        #
        self.tab0_topV_vlayout = QVBoxLayout()
        #
        self.tab0_topA_hlayout = QHBoxLayout()
        self.tab0_topB_hlayout = QHBoxLayout()
        self.tab0_topC_hlayout = QHBoxLayout()
        self.tab0_topD_hlayout = QHBoxLayout()
        #
        self.tab0_topA_hlayout = QHBoxLayout()
        self.tab0_topA_vlayout = QVBoxLayout()
        #
        self.tab0_topB_hlayout = QHBoxLayout()
        self.tab0_topB_vlayout = QVBoxLayout()
        #
        self.tab0_top0_vlayout = QVBoxLayout()
        #
        self.tab0_top1_vlayout = QVBoxLayout()
        self.tab0_top2_vlayout = QVBoxLayout()
        #
        self.tab0_top1_hlayout = QHBoxLayout()
        self.tab0_top2_hlayout = QHBoxLayout()
        #
        #
        self.tab0_top1_vlayout.setAlignment(Qt.AlignTop)
        self.tab0_top2_vlayout.setAlignment(Qt.AlignTop)
        #
        self.tab0_topA_vlayout.setAlignment(Qt.AlignTop)
        self.tab0_topB_vlayout.setAlignment(Qt.AlignTop)
        #
        #
        font = QFont("Arial", 11)
        font.setPointSize(11)
        #
        self.tab0_fold_text1 = QLabel("Directory:")
        self.tab0_fold_text1.setMaximumWidth(84)
        self.tab0_fold_text1.setFont(font)
        
        self.tab0_fold_edit1 = myLineEdit()
        self.tab0_fold_edit1.returnPressed.connect(self.tab0_fold_edit1_return)
        
        self.tab0_fold_push1 = MyEllipseButton(font)
        self.tab0_fold_userd = QDir.homePath()
        
        if (self.tab0_fold_userd[1:1] == ":") or (":" in self.tab0_fold_userd):
            self.tab0_fold_userd = ("/" +
            self.tab0_fold_userd[0:1]   +
            self.tab0_fold_userd[2:])
        
        self.tab0_fold_push1.clicked.connect(self.tab0_fold_push1_clicked)
        self.tab0_fold_edit1.setFont(font)
        self.tab0_fold_edit1.setText(self.tab0_fold_userd)
        
        self.tab0_fold_scroll1 = QScrollArea()
        self.tab0_fold_scroll1.setMinimumWidth(300)
        self.tab0_fold_scroll1.setMaximumWidth(300)
        self.tab0_fold_push11  = MyPushButton("Create", 1)
        self.tab0_fold_push12  = MyPushButton("Open"  , 2)
        self.tab0_fold_push13  = MyPushButton("Repro" , 3)
        self.tab0_fold_push14  = MyPushButton("Build" , 4)
        #
        self.tab0_fold_text2   = QLabel("Project-Name:")
        self.tab0_fold_text2.setMaximumWidth(84)
        self.tab0_fold_text2.setFont(font)
        self.tab0_fold_edit2   = myLineEdit()
        self.tab0_fold_push2   = MyEllipseButton(font)

        self.tab0_fold_scroll2 = QScrollArea()
        self.tab0_fold_scroll2.setMaximumWidth(300)
        self.tab0_fold_push21  = MyPushButton("Create", 1)
        self.tab0_fold_push22  = MyPushButton("Open"  , 2)
        self.tab0_fold_push23  = MyPushButton("Repro" , 3)
        self.tab0_fold_push24  = MyPushButton("Build" , 4)
        
        #
        self.tab0_top1_hlayout.addWidget(self.tab0_fold_text1)
        self.tab0_top1_hlayout.addWidget(self.tab0_fold_edit1)
        self.tab0_top1_hlayout.addWidget(self.tab0_fold_push1)
        #
        #
        self.tab0_top2_hlayout.addWidget(self.tab0_fold_text2)
        self.tab0_top2_hlayout.addWidget(self.tab0_fold_edit2)
        self.tab0_top2_hlayout.addWidget(self.tab0_fold_push2)
        #
        #
        self.tab0_topA_vlayout.addWidget(self.tab0_fold_push11)
        self.tab0_topA_vlayout.addWidget(self.tab0_fold_push12)
        self.tab0_topA_vlayout.addWidget(self.tab0_fold_push13)
        self.tab0_topA_vlayout.addWidget(self.tab0_fold_push14)
        self.tab0_topA_hlayout.addWidget(self.tab0_fold_scroll1)
        #
        self.tab0_topC_hlayout.addLayout(self.tab0_topA_vlayout)
        self.tab0_topC_hlayout.addLayout(self.tab0_topA_hlayout)
        #
        self.tab0_topB_vlayout.addWidget(self.tab0_fold_push21)
        self.tab0_topB_vlayout.addWidget(self.tab0_fold_push22)
        self.tab0_topB_vlayout.addWidget(self.tab0_fold_push23)
        self.tab0_topB_vlayout.addWidget(self.tab0_fold_push24)
        self.tab0_topB_hlayout.addWidget(self.tab0_fold_scroll2)
        #
        self.tab0_topD_hlayout.addLayout(self.tab0_topB_vlayout)
        self.tab0_topD_hlayout.addLayout(self.tab0_topB_hlayout)
        #
        self.tab0_top0_vlayout.addLayout(self.tab0_topC_hlayout)
        self.tab0_top0_vlayout.addLayout(self.tab0_topD_hlayout)
        #
        self.tab0_topV_vlayout.addLayout(self.tab0_top1_hlayout)
        self.tab0_topV_vlayout.addLayout(self.tab0_top0_vlayout)
        self.tab0_topV_vlayout.addLayout(self.tab0_top2_hlayout)
        self.tab0_topV_vlayout.addLayout(self.tab0_top0_vlayout)
        #
        #
        self.tab0_fold_scroll1_contentWidget = QWidget()
        #self.tab0_fold_scroll1_contentWidget.setGeometry(QRect(10,10,297,235))
        #self.tab0_fold_scroll1_contentWidget.setStyleSheet("background-color:gray;")
        #
        #
        #
        self.tab0_fold_scroll2_contentWidget = QWidget()
        #self.tab0_fold_scroll2_contentWidget.setGeometry(QRect(10,10,297,235))
        #self.tab0_fold_scroll2_contentWidget.setStyleSheet("background-color:gray;")
        #
        self.tab0_fold_scroll1.setWidget(self.tab0_fold_scroll1_contentWidget)
        self.tab0_fold_scroll2.setWidget(self.tab0_fold_scroll2_contentWidget)
        #
        #
        self.img_scroll1_layout = QVBoxLayout(self.tab0_fold_scroll1)
        self.img_scroll1_layout.addWidget(self.tab0_fold_scroll1)
        #
        global img_doxygen
        global img_hlpndoc
        #
        img_doxygen = doxygenImageTracker ()
        img_hlpndoc = helpNDocImageTracker()
        #
        #
        self.img_scroll1_layout.addWidget(img_doxygen)
        self.img_scroll1_layout.addWidget(img_hlpndoc)
        #
        self.img_scroll2_layout = QGridLayout(self.tab0_fold_scroll2)
        #
        #self.img_scroll2_layout.addWidget(self.tab0_fold_scroll2)
        #
        global img_ccpplus
        global img_javadoc
        global img_freepas
        #
        img_ccpplus = ccpplusImageTracker()
        img_javadoc = javadocImageTracker()
        img_freepas = freepasImageTracker()
        #
        #
        self.img_scroll2_layout.addWidget(img_ccpplus, 0, 0)
        self.img_scroll2_layout.addWidget(img_javadoc, 0, 1)
        self.img_scroll2_layout.addWidget(img_freepas, 2, 0, 1, 2)
        #
        #
        self.tab0_top_layout.addLayout(self.tab0_topV_vlayout)
        
        
        self.tab0_file_text = QLabel("File:", self.tab0_0)
        
        self.tab0_left_layout.addWidget(self.tab0_file_text)
        self.tab0_path = QDir.homePath()
        
        self.tab0_dir_model = QFileSystemModel()
        self.tab0_dir_model.setRootPath(self.tab0_path)
        self.tab0_dir_model.setFilter(QDir.NoDotAndDotDot | QDir.Dirs)
        
        self.tab0_file_model = QFileSystemModel()
        self.tab0_file_model.setNameFilters(['*.pro'])
        self.tab0_file_model.setNameFilterDisables(False)
        self.tab0_file_model.setFilter(QDir.NoDotAndDotDot | QDir.Files)
        
        
        self.tab0_file_tree = QTreeView()
        self.tab0_file_list = QListView()
        
        self.tab0_file_tree.setStyleSheet(_(css_model_header))
        
        self.tab0_file_tree.setModel(self.tab0_dir_model)
        self.tab0_file_list.setModel(self.tab0_file_model)
        
        self.tab0_file_tree.setRootIndex(self.tab0_dir_model.index(self.tab0_path))
        self.tab0_file_list.setRootIndex(self.tab0_file_model.index(self.tab0_path))
        
        self.tab0_help_list   = QListWidget()
        self.tab0_help_list.setMinimumWidth(260)
        self.tab0_help_list.setIconSize(QSize(34,34))
        self.tab0_help_list.setFont(QFont("Arial", 12))
        self.tab0_help_list.font().setBold(True)
        
        liste = [
            ["Empty Project"         , "emptyproject" + __app__img_ext__],
            ["Recipe"                , "recipe"       + __app__img_ext__],
            ["API Project"           , "api"          + __app__img_ext__],
            ["Software Documentation", "software"     + __app__img_ext__],
        ]
        for item in liste:
            self.list_item1 = QListWidgetItem(_(item[0]),self.tab0_help_list)
            self.list_item1.setIcon(QIcon(__app__img__int__ + item[1]))
            self.list_item1.setFont(self.tab0_help_list.font())
        
        self.tab0_help_layout = QHBoxLayout()
        self.tab0_help_layout.addWidget(self.tab0_file_list)
        self.tab0_help_layout.addWidget(self.tab0_help_list)
        
        self.tab0_left_layout.addWidget(self.tab0_file_tree)
        self.tab0_left_layout.addWidget(self.tab0_file_text)
        self.tab0_left_layout.addLayout(self.tab0_help_layout)
        
        self.tab0_file_tree.clicked.connect(self.tab0_file_tree_clicked)
        self.tab0_file_list.clicked.connect(self.tab0_file_list_clicked)
        
        
        #####
        # help templates
        
        
        # create action tab
        self.tab1_top_layout    = QHBoxLayout(self.tab1_0)
        self.tab1_left_layout   = QVBoxLayout()
        self.tab1_middle_layout = QVBoxLayout()
        self.tab1_right_layout  = QVBoxLayout()
        
        # ------------------
        # left, top part ...
        # ------------------
        self.tab1_fold_text = QLabel('Directory:', self.tab1_0)
        self.tab1_file_text = QLabel("File:", self.tab1_0)
        #
        self.tab1_left_layout.addWidget(self.tab1_fold_text)
        
        # pre
        self.tab1_pre_action_label = QLabel('Pre-Actions:', self.tab1_0)
        self.tab1_middle_layout.addWidget(self.tab1_pre_action_label);
        
        # post
        self.tab1_post_action_label = QLabel('Post-Actions:', self.tab1_0)
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
        
        self.tab1_file_tree.setStyleSheet(_(css_model_header))
        
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
        self.tab1_path_lineEdit = QLineEdit(self.tab1_0)
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
        self.tab1_startButton = QPushButton("Start", self.tab1_0)
        self.tab1_startButton.setStyleSheet(css_button_style)
        self.tab1_startButton.clicked.connect(self.startWatching)
        self.tab1_left_layout.addWidget(self.tab1_startButton)
        
        self.tab1_stopButton = QPushButton('Stop', self.tab1_0)
        self.tab1_stopButton.setStyleSheet(css_button_style)
        self.tab1_stopButton.clicked.connect(self.stopWatching)
        self.tab1_left_layout.addWidget(self.tab1_stopButton)
        
        # ComboBox für Zeitangaben
        self.tab1_timeComboBox = QComboBox(self.tab1_0)
        self.tab1_timeComboBox.addItems(["10", "15", "20", "25", "30", "60", "120"])
        self.tab1_timeComboBox.setStyleSheet(css_button_style)
        self.tab1_timeComboBox.setMaximumWidth(49)
        self.tab1_left_layout.addWidget(self.tab1_timeComboBox)
        
        # Label für den Countdown
        self.tab1_countdownLabel = QLabel('Select time:', self.tab1_0)
        self.tab1_left_layout.addWidget(self.tab1_countdownLabel)
        
        # mitte Seite
        self.tab1_preActionList = QListWidget(self.tab1_0)
        self.tab1_preActionList_Label  = QLabel("Content:", self.tab1_0)
        self.tab1_preActionList_Editor = QPlainTextEdit()
        #
        self.tab1_middle_layout.addWidget(self.tab1_preActionList)
        self.tab1_middle_layout.addWidget(self.tab1_preActionList_Label)
        self.tab1_middle_layout.addWidget(self.tab1_preActionList_Editor)
        
        #
        self.tab1_preActionComboBox = QComboBox(self.tab1_0)
        self.tab1_preActionComboBox.addItems([" Message", " Script", " URL", " FTP"])
        self.tab1_preActionComboBox.setStyleSheet(_(css_combobox_style))
        self.tab1_timeComboBox.setMaximumWidth(49)
        self.tab1_middle_layout.addWidget(self.tab1_preActionComboBox)
        
        self.tab1_preEditLineLabel = QLabel("Text / File:", self.tab1_0)
        self.tab1_middle_layout.addWidget(self.tab1_preEditLineLabel)
        #
        self.tab1_pre_layout = QHBoxLayout()
        
        self.tab1_preEditLineText = QLineEdit(self.tab1_0)
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
        self.tab1_postActionList = QListWidget(self.tab1_0)
        self.tab1_postActionList_Label  = QLabel("Content:", self.tab1_0)
        self.tab1_postActionList_Editor = QPlainTextEdit()
        #
        self.tab1_right_layout.addWidget(self.tab1_postActionList)
        self.tab1_right_layout.addWidget(self.tab1_postActionList_Label)
        self.tab1_right_layout.addWidget(self.tab1_postActionList_Editor)
        
        self.tab1_postActionComboBox = QComboBox(self.tab1_0)
        self.tab1_postActionComboBox.addItems([" Message", " Script", " URL", " FTP"])
        self.tab1_postActionComboBox.setStyleSheet(_(css_combobox_style))
        self.tab1_right_layout.addWidget(self.tab1_postActionComboBox)
        
        self.tab1_postEditLineLabel = QLabel("Text / File:", self.tab1_0)
        self.tab1_right_layout.addWidget(self.tab1_postEditLineLabel)
        #
        self.tab1_post_layout = QHBoxLayout()
        
        self.tab1_postEditLineText = QLineEdit(self.tab1_0)
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
        
        
        # ------------------
        # alles zusammen ...
        # ------------------
        self.webView1 = QWebEngineView(self.tab_html)
        self.profile1 = QWebEngineProfile("storage1", self.webView1)
        self.page1    = QWebEnginePage(self.profile1, self.webView1)
        self.webView1.setPage(self.page1)
        self.webView1.setHtml(html_content, baseUrl = QUrl. fromLocalFile('.'))
        
        self.tab5_top_layout.addWidget(self.webView1);            
        self.tab0_top_layout.addLayout(self.tab0_left_layout)
        
        self.tab1_top_layout.addLayout(self.tab1_left_layout)
        self.tab1_top_layout.addLayout(self.tab1_middle_layout)
        self.tab1_top_layout.addLayout(self.tab1_right_layout)
        
        self.layout.addLayout(self.main_layout)
        self.layout.addWidget(self.status_bar)
        
        self.setLayout(self.layout)
        self.setWindowTitle('HelpNDoc File Watcher v0.0.1 - (c) 2024 Jens Kallup - paule32')
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateCountdown)
        
        self.interval = 0
        self.currentTime = 0
        
    
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
    
    # project tab: top push
    def tab0_fold_push1_clicked(self):
        oldtext = self.tab0_fold_userd
        openDir = str(QFileDialog.getExistingDirectory(self,
        "Select Directory"))
        if len(openDir.strip()) < 1:
            self.tab0_fold_edit1.setText(self.tab0_fold_userd)
            self.tab0_fold_edit1_return()
        else:
            self.tab0_fold_userd = openDir
            self.tab0_fold_edit1_return()
    
    def tab0_fold_edit1_return(self):
        oldtext = self.tab0_fold_userd.strip()
        
        self.tab0_fold_userd = self.tab0_fold_userd \
        .replace(":" ,"/") \
        .replace("\\","/") \
        .replace("//","/")
        
        if not self.tab0_fold_userd.startswith("/"):
            self.tab0_fold_userd = "/" + self.tab0_fold_userd
        
        is_windows = any(platform.win32_ver())
        if is_windows:
            windowsdir = self.tab0_fold_userd[1:2] + ":" + self.tab0_fold_userd[2:]
            windowsdir = windowsdir.replace("/", "\\")
        else:
            windowsdir = self.tab0_fold_userd
        
        if os.path.exists(windowsdir) and os.path.isdir(windowsdir):
            self.tab0_dir_model .setRootPath(windowsdir)
            self.tab0_file_model.setRootPath(windowsdir)
            #
            self.tab0_file_tree.setRootIndex(self.tab0_dir_model.index(windowsdir))
            #self.tab0_file_list.setRootIndex(self.tab0_file_model_proxy.index(windowsdir))
            #
            self.tab0_fold_edit1.setText(self.tab0_fold_userd)
        else:
            self.tab0_fold_userd = oldtext
            self.tab0_dir_model .setRootPath(oldtext)
            self.tab0_file_model.setRootPath(oldtext)
            #
            self.tab0_file_tree.setRootIndex(self.tab0_dir_model.index(oldtext))
            self.tab0_file_list.setRootIndex(self.tab0_file_model_proxy.mapFromSource(self.tab0_file_model.index(oldtext)))
            #
            self.tab0_fold_edit1.setText(self.tab0_fold_userd)
    
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
        self.file_path = __app__internal__ + "/LICENSE"
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
def EntryPoint(arg1=None):
    atexit.register(ApplicationAtExit)
    
    global conn
    global conn_cursor
    
    error_fail    = False
    error_result  = 0
    
    topic_counter = 1
    
    if not arg1 == None:
        __app__scriptname__ = arg1
        if not os.path.exists(__app__scriptname__):
            print("script does not exists !")
            error_result = 1
            sys.exit(1)
    
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
    
    doxy_path  = __app__internal__
    hhc__path  = ""
    
    doxyfile   = __app__internal__ + "/Doxyfile"
    
    
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
    po_file_name = (__app__internal__ + "/locales/"
        + f"{ini_lang}"    + "/LC_MESSAGES/"
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
    
    conn = sqlite3.connect(__app__internal__ + "/data.db")
    conn_cursor = conn.cursor()
    conn.close()
    
    if app == None:
        app = QApplication(sys.argv)
    
    appwin = FileWatcherGUI()
    appwin.move(100, 100)
    
    appwin.exec_()
    
    #error_result = app.exec_()
    return

# ---------------------------------------------------------------------------
# parse binary data:
# --------------------------------------------------------------------------
class parserBinary:
    def __init__(self, script_name):
        try:
            # ---------------------
            # load binary code ...
            # ---------------------
            with open(script_name,"rb") as self.bytefile:
                self.bytecode = self.bytefile.read()
                self.bytefile.close()
            # ---------------------
            # execute binary code:
            # ---------------------
            self.byte_code = marshal.loads(self.bytecode)
            exec(self.byte_code)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise

# ---------------------------------------------------------------------------
# parse dBase script ...
# ---------------------------------------------------------------------------
class parserDBasePoint:
    def __init__(self, script_name):
        prg = dBaseDSL(script_name)
        try:
            prg.parse(self)
            prg.run(self)
        except ENoParserError as noerror:
            prg.finalize()
            print("\nend of data")

# ---------------------------------------------------------------------------
# parse Doxyfile script ...
# ---------------------------------------------------------------------------
class parserDoxyGen:
    def __init__(self, script_name):
        prg = doxygenDSL(script_name)
        try:
            prg.parse(self)
            prg.run(self)
        except ENoParserError as noerror:
            prg.finalize()
            print("\nend of data")

# ---------------------------------------------------------------------------
# parse Pascal script ...
# ---------------------------------------------------------------------------
class parserPascalPoint:
    def __init__(self, script_name):
        self.prg = interpreter_Pascal(script_name)
        try:
            self.prg.parse()
            self.prg.run()
        except ENoParserError as noerror:
            self.finalize()
            print("\nend of data")

# ---------------------------------------------------------------------------
# the mother of all: the __main__ start point ...
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    
    # The Python 2.7+ or 3.3+ is required.
    major = sys.version_info[0]
    minor = sys.version_info[1]
    if (major == 2 and minor < 7) or (major == 3 and minor < 0):
        print("Python 2.7+ or Python 3.0+ are required for the script")
        sys.exit(1)
    
    # Determine the path to the script and its name.
    script = os.path.abspath(sys.argv[0])
    script_path, script_name = os.path.split(script)
    script_path = os.path.abspath(script_path)
    
    __app__observers = "observer --"
    __app__file__    = "file."
    __app__space__   = "       "
    __app__parameter = (""
    + "Usage: "      + __app__observers + "dbase   " + __app__file__ + "prg\n"
    + __app__space__ + __app__observers + "pascal  " + __app__file__ + "pas\n"
    + __app__space__ + __app__observers + "doxygen " + __app__file__ + "dox\n"
    + __app__space__ + __app__observers + "exec    " + __app__file__ + "bin\n"
    + __app__space__ + __app__observers + "gui\n")
    
    __app__tmp3 = "parse..."
    
    if len(sys.argv) < 2:
        print("no arguments given.")
        print(__app__parameter)
        sys.exit(1)
    
    if len(sys.argv) >= 1:
        if sys.argv[1] == "--gui":
            if len(sys.argv) == 2:
                sys.argv.append("test.txt")
            __app__scriptname__ = sys.argv[2]
            handleExceptionApplication(EntryPoint,__app__scriptname__)
            sys.exit(0)
        elif sys.argv[1] == "--doxygen":
            if len(sys.argv) == 2:
                sys.argv.append("Doxyfile")
            __app__scriptname__ = sys.argv[2]
            handleExceptionApplication(parserDoxyGen,sys.argv[2])
            sys.exit(0)
        elif sys.argv[1] == "--exec":
            __app__scriptname__ = sys.argv[2]
            handleExceptionApplication(parserBinary,sys.argv[2])
        elif sys.argv[1] == "--dbase":
            print(__app__tmp3)
            try:
                handleExceptionApplication(parserDBasePoint,sys.argv[2])
                sys.exit(0)
            except Exception as ex:
                sys.exit(1)
        elif sys.argv[1] == "--pascal":
            print(__app__tmp3)
            __app__scriptname__ = sys.argv[2]
            handleExceptionApplication(parserPascalPoint,sys.argv[2])
            sys.exit(0)
        else:
            print("parameter unknown.")
            print(__app__parameter)
            sys.exit(1)
        
# ----------------------------------------------------------------------------
# E O F  -  End - Of - File
# ----------------------------------------------------------------------------
