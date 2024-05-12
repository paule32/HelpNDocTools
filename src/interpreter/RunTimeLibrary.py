# ---------------------------------------------------------------------------
# \file   RunTimeLibrary.py
# \author (c) 2024 Jens Kallup - paule32
#         all rights reserved
#
# \brief  This class provides a common interface for producing DSL (domain
#         source language's) written in Python 3.12.
#         This file provides a small runtime library for using with the DSL
#         parser.
#         Feel free to use it in your projects with the MIT license and the
#         following promise:
#
#         only for education, and non-profit !
# ---------------------------------------------------------------------------
from appcollection import *

# ---------------------------------------------------------------------------
# \brief A small runtime library that is used within the "ParserDSL" class
#        library for code reuse.
# ---------------------------------------------------------------------------
class RunTimeLibrary:
    # -----------------------------------------------------------------------
    # \brief __init__ is the initializator - maybe uneeded, because __new__
    #        is the constructor ...
    # -----------------------------------------------------------------------
    def __init__(self):
        self.version     = "1.0.0"
        self.author      = "paule32"
        self.initialized = False
    
    # -----------------------------------------------------------------------
    # \brief  this is the constructor of class "RunTimeLibrary" ...
    #         The return value is the created object pointer in memory space.
    #
    # \param  nothing
    # \return Object - a pointer to this class object
    # -----------------------------------------------------------------------
    def __new__(self):
        self.initialized = True
        return self
    
    def __enter__(self):
        return self
    
    # -----------------------------------------------------------------------
    # \brief  destructor for class "RunTimeLibrary" ...
    #
    # \param  nothing
    # \return nothing - destructors doesnt return values.
    # -----------------------------------------------------------------------
    def __del__(self):
        self.check_initialized(self)
        self.initialized = False
    
    # -----------------------------------------------------------------------
    # \brief  This function returns True if a file with "name" exists on the
    #         disk, False otherwise. On Microsoft Windows, the function will
    #         return False if a directory is passed as "name"
    #
    # \param  name  - the script file name to check.
    # \return False - when the checks fails
    #         True  - when the file checks success
    # -----------------------------------------------------------------------
    def FileExists(self, name):
        self.rtl.check_initialized(self)
        if not os.path.exists(name):
            return False
        elif os.path.isdir(name):
            return False
        elif os.path.isfile(name):
            return True
    
    # -----------------------------------------------------------------------
    # \brief  This function read the content of a text file, and return the
    #         readed content.
    #
    # \param  name - the file name that content should read
    # \return encoding text string content that was read from file.
    # -----------------------------------------------------------------------
    def ReadFile(self, name):
        self.rtl.check_initialized(self)
        if not self.rtl.FileExists(self, name):
            raise EParserError(10000)
        with open(name, "r", encoding="utf-8") as file:
            file.seek(0)
            data = file.read()
            file.close()
        return data
    
    # -----------------------------------------------------------------------
    # \brief  StringCompare compare the string "str" with the occurences of
    #         strings in the list. The string_list can contain multiple
    #         strings separated by a comma.
    #
    # \param  str  - the string to be check
    # \param  list - the list of strings which can contain "str"
    # \return True - if check is okay, True is the return value, else False
    # -----------------------------------------------------------------------
    def StringCompare(self, string, string_list):
        result = False
        if string in string_list:
            return True
        else:
            return False
    
    # -----------------------------------------------------------------------
    # \brief raise an exception, if the runtime libaray is not initialized...
    # -----------------------------------------------------------------------
    def check_initialized(self):
        if not self.initialized:
            raise EParserError(1000)
