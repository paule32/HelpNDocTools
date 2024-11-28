# ---------------------------------------------------------------------------
# File:   TObject.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import sys
import os
import gc

import hashlib

from datetime import datetime

# ---------------------------------------------------------------------------
# \brief ClassObjects holds the TObject classes. TObject is the base of all
#        classes that used this framework. The array will be delete its
#        objects with the destructor definition __del__.
#
# \note  do not use this varuable directly - it is used for internal things.
# \since version 0.0.1
# ---------------------------------------------------------------------------
global ClassObjects
ClassObjects = []

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
        
        self.parentNode = {
            "class": {
                "parent": None,
                "name": self.__class__.__name__,
                "addr": self,
                "hash": self.hashString,
                "date": datetime.now()
            }
        }
        self.Add()
    
    # --------------------------------------------------------------------
    # dtor of class TObject
    # --------------------------------------------------------------------
    def Destroy(self):
        pass
    
    # --------------------------------------------------------------------
    # internal function: for add object informations to ClassObjects.
    # --------------------------------------------------------------------
    def Add(self):
        # ----------------------------------------------------------------
        # create a new child
        # ----------------------------------------------------------------
        child_node = {
            "class": {
                "parent": self.parentNode,
                "name": self.__class__.__name__,
                "addr": self,
                "obj_name": type(self).__name__,
                "hash": self.hashString,
                "date": datetime.now()
            }
        }
        # ----------------------------------------------------------------
        # append object informations ...
        # ----------------------------------------------------------------
        self.parentNode = child_node
        ClassObjects.append(child_node)
    
    def test(self):
        print(ClassObjects[0]["class"]["hash"])
        print(ClassObjects[1]["class"]["hash"])
    
    # --------------------------------------------------------------------
    # check for None and call destructor
    # --------------------------------------------------------------------
    def Free(self):
        current_node = ClassObjects[-1]
        while current_node is not None:
            try:
                addr = current_node["class"]["addr"]
                if addr is not None:
                    del addr
                
                current_node["class"]["addr"] = None
                parent_node = current_node["class"]["parent"]
                
                del current_node
                current_node = parent_node
                
                if current_node is None:
                    break
                
            except Exception as err:
                print("error during element del.")
        
        # force garbage collector to remove allocated memory space
        gc.collect()
        self.Destroy()
    
    # --------------------------------------------------------------------
    # return a hash code for the object
    # --------------------------------------------------------------------
    def GetHashCode(self):
        return self.hashstring
    
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

# ---------------------------------------------------------------------------
# \brief A wrapper class to TObject.
# ---------------------------------------------------------------------------
class TClass(TObject):
    def Create(self, parent=None):
        super().Create(parent)
    
    def Destroy(self):
        if hasattr(super(), 'Destroy'):
            super().Destroy()
    
    # --------------------------------------------------------------------
    # we re-assign the constructor and destructor for Turbo-Pascal feeling
    # --------------------------------------------------------------------
    __init__ = Create       # constructor - ctor
    __del__  = Destroy      # destructor  - dtor
