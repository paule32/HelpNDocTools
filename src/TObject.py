# ---------------------------------------------------------------------------
# File:   TObject.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import sys
import os

import hashlib
from   datetime import datetime

# ---------------------------------------------------------------------------
# \brief ClassObjects holds the TObject classes. TObject is the base of all
#        classes that used this framework. The array will be delete its
#        objects with the destructor definition __del__.
#
# \note  do not use this varuable directly - it is used for internal things.
# \since version 0.0.1
# ---------------------------------------------------------------------------
ClassObjects   = []
ClassObjetcsID = ""

# ---------------------------------------------------------------------------
# \brief TObject is the base class of all classes that used this framework.
#        You can use "Create" for __init__ and "Destroy" for __del__.
#        For each TObject, we use/save a hash string to unufy the object.
#        This makes it possible to search for objects.
#
# \since version 0.0.1
# ---------------------------------------------------------------------------
class TObject:
    # --------------------------------------------------------------------
    # constructor of class TObject
    # --------------------------------------------------------------------
    def Create(self, parent=None):
        # ----------------------------------------------------------------
        # ClassName returns the class name for the current class.
        # ----------------------------------------------------------------
        self.ClassName = str(__class__.__name__)
        
        # ----------------------------------------------------------------
        # to get the hash, we get the class name and the current date and
        # time will be add at end of string. But this is not enough so we
        # add a reference counter at finally string end.
        # the counter is simple the length of the ClassObjects container.
        # ----------------------------------------------------------------
        self.hashstring  = self.__class__.__name__
        self.hashstring += datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.hashstring += str(len(ClassObjects) + 1)
        
        self.hashString  = hashlib        \
        .sha256(self.hashstring.encode()) \
        .hexdigest()
        
        if parent == None:
            self.ParentHashCode = self.hashString
        else:
            self.ParentHashCode = parent.GetHashCode()
        
        ClassObjects.append({
        "class": {
            "parent": {
                "name": parent.__class__.__name__,
                "addr": parent,
                "hash": self.ParentHashCode
                },
            "owner": {
                "name": self.__class__.__name__,
                "addr": self,
                "hash": self.GetHashCode()
                }
        }   }   )
        
        print("")
        print(ClassObjects)
        pass
    
    # --------------------------------------------------------------------
    # dtor of class TObject
    # --------------------------------------------------------------------
    def Destroy(self):
        pass
    
    # --------------------------------------------------------------------
    # check for None and call destructor
    # --------------------------------------------------------------------
    def Free(self):
        pass
    
    # --------------------------------------------------------------------
    # return a hash code for the object
    # --------------------------------------------------------------------
    def GetHashCode(self):
        return self.hashString
    
    # --------------------------------------------------------------------
    # internal function: for add object informations to self.Objects.
    # --------------------------------------------------------------------
    def AddInternalObject(self, AItem):
        self.Objects.append(AItem)
        pass
    # --------------------------------------------------------------------
    # internal function: for add object informations to self.Objects.
    # --------------------------------------------------------------------
    def DelInternalObject(self, AItem):
        #self.Objects.append(AItem)
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

    # --------------------------------------------------------------------
    # we re-assign the constructor and destructor for Turbo-Pascal feeling
    # --------------------------------------------------------------------
    __init__ = Create       # constructor - ctor
    __del__  = Destroy      # destructor  - dtor
