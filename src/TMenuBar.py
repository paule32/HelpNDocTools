# ---------------------------------------------------------------------------
# File:   TMenuBar.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import sys
import os

from TObject      import *
import TApplication

from PyQt5.QtWidgets          import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore             import *

class TMenuBar(TObject):
    def Create(self, parent=None):
        super(TMenuBar, self).Create(parent)
        
        if not parent == None:
            if not isinstance(parent, TApplication.TApplication):
                QMessageBox.information(self,
                "Information",
                "parent must be TApplication")
                return
        else:
            QMessageBox.information(self,
            "Information",
            "parent must be given")
            return
        
        self.parent      = parent
        self.menu_bar    = parent.dialog.mainwindow.menuBar()
        
        self.file_menu   = self.menu_bar.addMenu("File")
        self.exit_action = QAction("Exit", parent.dialog.mainwindow)
        self.file_menu.addAction(self.exit_action)
    
    def show(self):
        self.menu_bar.show()
    
    def hide(self):
        self.menu_bar.hide()
    
    def Destroy(self):
        super().Destroy()
    
    # --------------------------------------------------------------------
    # we re-assign the constructor and destructor for Turbo-Pascal feeling
    # --------------------------------------------------------------------
    __init__ = Create       # constructor - ctor
    __del__  = Destroy      # destructor  - dtor
