# ---------------------------------------------------------------------------
# \file   ParserDSL.py
# \author (c) 2024 Jens Kallup - paule32
#         all rights reserved
#
# \brief  this class provides a common interface for producing DSL (domain
#         source language's) written in Python 3.12.
# ---------------------------------------------------------------------------
from appcollection import *

# ---------------------------------------------------------------------------
# \brief A parser generator class to create a DSL (domain source language)
#        parser with Python 3.12.
#
# \field files - an array of used script files
# \field data  - an array of used script files data
# \field info  - information about the parse processor (encoding, ...)
# \field stat  - for statistics
# \field rtl   - a link reference to the runtime library for this class
# ---------------------------------------------------------------------------
class ParserDSL:
    # -----------------------------------------------------------------------
    # \brief __init__ is the initializator - maybe uneeded, because __new__
    #        is the constructor ...
    # -----------------------------------------------------------------------
    def __init__(self):
        self.files  = []
        self.data   = []
        
        self.name   = ""
        
        self.info   = None
        self.stat   = None
        self.this   = None
        
        self.rtl    = None
        
        self.AST    = []
        
        self.initialized = False
    
    # -----------------------------------------------------------------------
    # \brief this is the constructor of class "ParserDSL" ...
    # -----------------------------------------------------------------------
    def __new__(self, script_name, lang="dbase"):
        self.name   = lang.lower()
        self.paeser = self
        self.rtl    = RunTimeLibrary()
        self.AST    = []
        self.files  = [
            [ "root.src", "dbase", "** comment" ]
        ]
        self.initialized = True
        self.addFile(self, script_name)
        return self
    
    def __enter__(self):
        return self
    
    # -----------------------------------------------------------------------
    # \brief destructor for parser generator class ...
    # -----------------------------------------------------------------------
    def __del__(self):
        self.files.clear()
        self.data.clear()
    
    # -----------------------------------------------------------------------
    # \brief Add new script file to self.file array [].
    #
    # \param name - the file name of the script.
    # -----------------------------------------------------------------------
    def addFile(self, name):
        if not self.rtl.FileExists(self, name):
            raise EParserError(10000)
        else:
            data = []
            code = self.rtl.ReadFile(self, name)
            
            data.append(name)
            data.append(self.name)
            data.append(code)
            
            self.files.append(data)
            print(self.files)
        return True
    
    # -------------------------------------------------------------------
    # \brief add comment types to the AST of a DSL parser.
    #        currently the following types are available:
    #
    #        dBase:
    #        ** one liner comment
    #        && one liner
    #        // one liner comment
    #        /* block */ dbase multi line comment block
    #
    #        C/C++:
    #        // C(C++ comment one liner
    #        /* block */ C++ multi line comment block
    #
    #        Bash, misc:
    #        # comment one liner
    #
    #        Assembly, LISP:
    #        ; one line comment
    # -------------------------------------------------------------------
    def add(self, object_type):
        if type(object_type) == ParserDSL.comment:
            which = ParserDSL.name.lower()
            
            # --------------------------
            # no syntax comments
            # --------------------------
            if which == "":
                comment = [[None,None]]
                comment_object = self.comment("unknown")
                comment_object.set(comment)
                self.AST.append(comment_object)
            # --------------------------
            # dBase 7 syntax comments
            # --------------------------
            if which == "dbase":
                comment = [
                    [ "**", None ],
                    [ "&&", None ],
                    [ "//", None ],
                    [ "/*", "*/" ],
                ]
                comment_object = self.comment(which)
                comment_object.set(comment)
                self.AST.append(comment_object)
            # --------------------------
            # modern C syntax comments
            # --------------------------
            elif which == "c":
                comment = [
                    ["/*", "*/" ],
                    ["//", None ],
                ]
                comment_object = self.comment(which)
                comment_object.set(comment)
                self.AST.append(comment_object)
            # --------------------------
            # modern C++ syntax comments
            # --------------------------
            elif self.rtl.StringCompare(which, ["c++","cc","cpp"]):
                comment = [
                    ["/*", "*/" ],
                    ["//", None ],
                ]
                comment_object = self.comment(which)
                comment_object.set(comment)
                self.AST.append(comment_object)
            # --------------------------
            # modern Pascal comments
            # --------------------------
            elif which == "pascal":
                comment = [
                    ["(*", "*)" ],
                    ["{" , "}"  ],
                    ["//", None ],
                ]
                comment_object = self.comment(which)
                comment_object.set(comment)
                self.AST.append(comment_object)
            # --------------------------
            # old ASM, and LISP comments
            # --------------------------
            elif self.rtl.StringCompare(which, ["asm","lisp"]):
                comment = [
                    [";", None ],
                ]
                comment_object = self.comment(which)
                comment_object.set(comment)
                self.AST.append(comment_object)
            # --------------------------
            # *nix tool style comments
            # --------------------------
            elif which == "bash":
                comment = [
                    ["#", None ],
                ]
                comment_object = self.comment(which)
                comment_object.set(comment)
                self.AST.append(comment_object)
            else:
                #"no known comment type"
                raise EParserError(1100)
    
    # -------------------------------------------------------------------
    # \brief class is used to mark a AST scope using comment type  ...
    # -------------------------------------------------------------------
    class comment:
        def __init__(self, argument=None):
            self.data   = []
            self.name   = "s"
            self.parent = ParserDSL
            
            # --------------------------
            # no argument given.
            # --------------------------
            if argument == None:
                print("info: current scope without "
                + "comments initialized.")
            # --------------------------
            # argument type is a class
            # --------------------------
            elif argument == ParserDSL:
                self.parent = argument
                if self.parent.name != argument.name:
                    print("info: current scope with: "
                    + argument.name
                    + " comments overwrite.")
                    self.parent.name = argument.name
                else:
                    print("info: current scope not touched, because"
                    + " comments already initialized with: "
                    + argument.name
                    + ".")
            # --------------------------
            # argument type is a string
            # --------------------------
            elif type(argument) == str:
                supported_dsl = [
                    "dbase", "pascal", "c", "c++", "cpp", "cc",
                    "asm", "bash", "lisp"
                ]
                # --------------------------
                # dsl is in supported list:
                # --------------------------
                if argument in supported_dsl:
                    print("info: current scope with: "
                    + argument
                    + " comments initialized.")
                    self.parent.name = argument
                # --------------------------
                # dsl not in supported list
                # --------------------------
                else:
                    print("info: current scope with custom "
                    + "comments initialized.")
                    self.parent.name = argument
        
        # ---------------------------------------------------------------
        # \brief  add a comment type to the existing comment scope ...
        #
        # \param  name  - the name for the parser DSL
        # \param  kind  - a list with supported comment styles.
        #                 the format is: [ <start>, <end> ]; if None set
        #                 for <end>, then it is a one liner comment.
        # \return True  - if the kind list is append successfully to the
        #                 available data list.
        #         False - when other event was occured.
        # ---------------------------------------------------------------
        def add(self, name, kind):
            self.name = name
            self.data.append(kind)
            return True
        
        # ---------------------------------------------------------------
        # \brief set a new comment type to the existing comment scope ...
        #
        # \param name - the DSL parser language
        # \param kind - the comment styles that are available for <name>
        # ---------------------------------------------------------------
        def set(self, name, kind):
            self.name = name
            self.data = kind
            return True
        
        # ---------------------------------------------------------------
        # \brief  set the parser name for which the comments are ...
        #
        # \param  name - a string for parser name
        # \return True - boolean if successfully; else False
        # ---------------------------------------------------------------
        def set(self, name):
            self.name = name
            return True
        
        # ---------------------------------------------------------------
        # \brief  get the comment data list for the given comment scope.
        #
        # \param  nothing
        # \return data - the self.data list
        # ---------------------------------------------------------------
        def get(self):
            return self.data
        
        # ---------------------------------------------------------------
        # \brief  returns the name which comments stands for DSL name
        #
        # \param  nothing
        # \return string - the parser name
        # ---------------------------------------------------------------
        def getName(self):
            return self.name
    
    # -----------------------------------------------------------------------
    # \brief A class that act as record, to hold the informations about a
    #        decent parser...
    #
    # \field name     - a name for the parser
    # \field encoding - the source encoding of script file
    # -----------------------------------------------------------------------
    class parser_info:
        # -------------------------------------------------------------------
        # \brief __init__ is the initializator - maybe uneeded, because
        #        __new__  is the constructor ...
        # -------------------------------------------------------------------
        def __init__(self, name=None, encoding="utf-8"):
            self.name     = name
            self.encoding = encoding
        
        # -------------------------------------------------------------------
        # \brief this is the constructor of class "parser_info" ...
        # -------------------------------------------------------------------
        def __new__(self):
            return self
        
        def __enter__(self):
            return self
        
        # -------------------------------------------------------------------
        # \brief destructor for class "parser_info" ...
        # -------------------------------------------------------------------
        def __del__(self):
            self.name = ""
        
        # -------------------------------------------------------------------
        # setters for parser informations ...
        # -------------------------------------------------------------------
        def setName(self, name):
            self.name = name
        
        # -------------------------------------------------------------------
        # getters for parser informations ...
        # -------------------------------------------------------------------
        def getName(self):
            return self.name
    
    # -----------------------------------------------------------------------
    # \brief A class that act as record, to hold the statistically infos of a
    #        parse run...
    # \field time_start - time of start processing
    # \field time_end   - time of end   processing
    # -----------------------------------------------------------------------
    class parser_stat:
        # -------------------------------------------------------------------
        # \brief __init__ is the initializator - maybe uneeded, because
        #        __new__  is the constructor ...
        # -------------------------------------------------------------------
        def __init__(self):
            self.time_start = None
            self.time_end   = None
            self.encoding   = None
        
        # -------------------------------------------------------------------
        # \brief this is the constructor of class "parser_stat" ...
        # -------------------------------------------------------------------
        def __new__(self):
            return self
        
        def __enter__(self):
            return self
        
        # -------------------------------------------------------------------
        # \brief destructor for class "parser_stat" ...
        # -------------------------------------------------------------------
        def __del__(self):
            self.time_start = None
            self.time_end   = None
        
        # -------------------------------------------------------------------
        # setters for statistically informations ...
        # -------------------------------------------------------------------
        def setStart(self, time):
            self.time_start = time
        def setEnd(self, time):
            self.time_end   = time
        def setEncoding(self, encoding="utf-8"):
            self.encoding   = encoding
        
        # -------------------------------------------------------------------
        # getters for statistically informations ...
        # -------------------------------------------------------------------
        def getStart(self):
            return self.time_start
        def getEnd(self):
            return self.time_end
        def getEncoding(self):
            return self.encoding
    
    # -----------------------------------------------------------------------
    # \brief A class that act as record, to hold the script file data infos
    #        for used files...
    #
    # \field name    - the script name
    # \field size    - the size of the script in bytes
    # \field date    - the date of creation
    # \field datemod - the date of last modification
    # -----------------------------------------------------------------------
    class parser_file:
        # -------------------------------------------------------------------
        # \brief __init__ is the initializator - maybe uneeded, because
        #        __new__  is the constructor ...
        # -------------------------------------------------------------------
        def __init__(self, name):
            self.name    = name
            self.size    = 0
            self.date    = None
            self.datemod = None
        
        # -------------------------------------------------------------------
        # \brief this is the constructor of class "parser_file" ...
        # -------------------------------------------------------------------
        def __new__(self):
            return self
        
        def __enter__(self):
            return self
        
        # -------------------------------------------------------------------
        # \brief destructor for class "parser_file" ...
        # -------------------------------------------------------------------
        def __del__(self):
            self.name = None
    
    # -----------------------------------------------------------------------
    # \brief A class that act as record, to hold the data of a script file.
    #
    # \field name  - the script name
    # \field data  - the script data/source
    # \field lines - the lines of the script
    # -----------------------------------------------------------------------
    class parser_data:
        # -------------------------------------------------------------------
        # \brief __init__ is the initializator - maybe uneeded, because
        #        __new__  is the constructor ...
        # -------------------------------------------------------------------
        def __init__(self, name, data="", lines=0):
            self.name  = name
            self.data  = data
            self.lines = lines
        
        # -------------------------------------------------------------------
        # \brief this is the constructor of class "parser_data" ...
        # -------------------------------------------------------------------
        def __new__(self):
            return self
        
        def __enter__(self):
            return self
        
        # -------------------------------------------------------------------
        # \brief destructor for class "parser_data" ...
        # -------------------------------------------------------------------
        def __del__(self):
            self.name = None
        
        # -------------------------------------------------------------------
        # setters
        # -------------------------------------------------------------------
        def setLines(self, lines):
            self.lines = lines
        def setName(self, name):
            self.name  = name
        def setData(self, data):
            self.data  = data
        
        # -------------------------------------------------------------------
        # getters
        # -------------------------------------------------------------------
        def getLines(self):
            return self.lines
        def getName(self):
            return self.name
        def getData(self):
            return self.data
