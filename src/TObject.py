# ---------------------------------------------------------------------------
# File:   TObject.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import string

class TObject:
    # --------------------------------------------------------------------
    # ctor of class TObject
    # --------------------------------------------------------------------
    def __init__(self):
        # ----------------------------------------------------------------
        # ClassName returns the class name for the current class.
        # ----------------------------------------------------------------
        self.ClassName = str(__class__.__name__)
        pass
    
    # --------------------------------------------------------------------
    # dtor of class TObject
    # --------------------------------------------------------------------
    def __del__(self):
        pass
    
    # --------------------------------------------------------------------
    # check for None and call destructor
    # --------------------------------------------------------------------
    def Free(self):
        pass
    
    # --------------------------------------------------------------------
    # Equals returns True if the object instance pointer (Self) equals
    # the instance pointer Obj.
    # --------------------------------------------------------------------
    def Equals(self, AObject):
        if AObject == self:
            return True
        else:
            return False
    
    # --------------------------------------------------------------------
    # ClassNameIs checks whether Name equals the class name. It takes of
    # case sensitivity.
    # --------------------------------------------------------------------
    def ClassNameIs(self, name):
        if self.ClassName == name:
            return True
        else:
            return False
    
    def ToString(self):
        return str(self.ClassName)
