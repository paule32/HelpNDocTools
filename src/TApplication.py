# ---------------------------------------------------------------------------
# File:   TApplication.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import sys
import os

from TObject     import *
from TMainWindow import *

import TMenuBar
import TStatusBar
        
class TApplication(TObject):
    # --------------------------------------------------------------------
    # ctor for class TApplication
    # --------------------------------------------------------------------
    def Create(self, parent=None):
        super(TApplication, self).__init__(parent)
        #
        self.ParamCount = len(sys.argv)
        self.Params     = sys.argv
        self.app        = QApplication(sys.argv)
        self.dialog     = TMainWindow()
        #
        self.ExeName         = self.ParamStr(0)
        self.ApplicationName = "Python Application"
        #
        self.bar_menu   = TMenuBar.TMenuBar(self)
        self.bar_status = TStatusBar.TStatusBar(self)
        
    # --------------------------------------------------------------------
    # this definition member returns the n'th program argument parameter
    # --------------------------------------------------------------------
    def ParamStr(self, index):
        if index < len(self.Params):
            return self.Params[index]
        else:
            return ""
    
    # --------------------------------------------------------------------
    # dtor for class TApplication
    # --------------------------------------------------------------------
    def Destroy(self):
        if hasattr(super(), 'Destroy'):
            super().Destroy()
        pass
    
    # --------------------------------------------------------------------
    # runner def inition entry point.
    # --------------------------------------------------------------------
    def run(self):
        try:
            self.dialog.show()
            self.app.exec_()
        finally:
            self.bar_menu  .Free()
            self.bar_status.Free()
            #
            sys.exit(0)
    
    # --------------------------------------------------------------------
    # we re-assign the constructor and destructor for Turbo-Pascal feeling
    # --------------------------------------------------------------------
    __init__ = Create       # constructor - ctor
    __del__  = Destroy      # destructor  - dtor
