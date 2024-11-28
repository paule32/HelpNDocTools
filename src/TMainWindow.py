# ---------------------------------------------------------------------------
# File:   TApplication.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import sys
import os

from TObject                  import *

from PyQt5.QtWidgets          import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore             import *

class TMainWindow(TObject):
    def Create(self, parent=None):
        super(TMainWindow, self).Create(parent)
        
        self.app = None
        
        # ----------------------------------------------------------------
        # create a application main window.
        # ----------------------------------------------------------------
        self.mainwindow = QMainWindow()
        
        layout     = QVBoxLayout()
        container  = QWidget()
        
        container.setLayout(layout)
        self.mainwindow.setCentralWidget(container)
        
    def show(self):
        self.mainwindow.show()
    
    def exec_(self):
        self.mainwindow.exec_()
    
    def Destroy(self):
        super().Destroy()
    
    # --------------------------------------------------------------------
    # we re-assign the constructor and destructor for Turbo-Pascal feeling
    # --------------------------------------------------------------------
    __init__ = Create       # constructor - ctor
    __del__  = Destroy      # destructor  - dtor
