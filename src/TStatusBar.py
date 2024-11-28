# ---------------------------------------------------------------------------
# File:   TStatusBar.py
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

class TStatusBar(TObject):
    def Create(self, parent=None):
        super(TStatusBar, self).Create(parent)
        
        if not parent == None:
            if not isinstance(parent, TApplication.TApplication):
                QMessageBox.information(self,
                "Information",
                "parent must be TApplication")
        else:
            QMessageBox.information(self,
            "Information",
            "parent must be given")
            return
        
        self.status_bar = parent.dialog.mainwindow.statusBar()
        self.status_bar.showMessage("Ready.")
        self.status_bar.setStyleSheet("background-color:lightgray;")
    
    def show(self):
        self.status_bar.show()
    
    def hide(self):
        self.status_bar.hide()
    
    def Destroy(self):
        super().Destroy()
    
    # --------------------------------------------------------------------
    # we re-assign the constructor and destructor for Turbo-Pascal feeling
    # --------------------------------------------------------------------
    __init__ = Create       # constructor - ctor
    __del__  = Destroy      # destructor  - dtor