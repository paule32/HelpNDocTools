# ---------------------------------------------------------------------------
# File:   TApplication.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import sys
import os

class TApplication(TObject):
    # --------------------------------------------------------------------
    # ctor for class TApplication
    # --------------------------------------------------------------------
    def __init__(self):
        super(TApplication, self).__init__()
        #
        self.ParamCount = 1
        self.Params     = sys.argv
        #
        self.ExeName         = self.ParamStr(0)
        self.ApplicationName = "Python Application"
    
    # --------------------------------------------------------------------
    # dtor for class TApplication
    # --------------------------------------------------------------------
    def __del__(self):
        pass
    
    def ParamStr(self, AIndex):
        if AIndex != self.ParamCount-1:
            raise Exception("error: parameter out of bounds.")
            return "None"
        elif self.Params[AIndex] == "":
            raise Exception("error: parameter string is empty,")
            return "None"
        else:
            return self.Params[AIndex]
            