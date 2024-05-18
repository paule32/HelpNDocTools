# ---------------------------------------------------------------------------
# File:   dbase.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
from appcollection import *

class consoleApp():
    def __init__(self):
        init(autoreset = True)
        sys.stdout.write(Fore.RESET + Back.RESET + Style.RESET_ALL)
        return
    
    def cls(self):
        sys.stdout.write("\033[H\033[2J")
        sys.stdout.flush()

class dbase_function:
    def __init__(self, src, name):
        self.what   = "func"
        self.owner  = src
        self.name   = name
        self.result = "tztz"
        self.add(src)
    def add(self):
        self.owner.AST.append(self)
        return self

class dbase_val_variable:
    def __init__(self, src, value=0):
        self.what  = "val"
        self.owner = src
        self.value = value
        self.add(src)
    def add(self):
        self.owner.AST.append(self)
        return self

class dbase_str_variable:
    def __init__(self, src, value=""):
        self.what  = "str"
        self.owner = src
        self.value = value
        self.add(src)
    def add(self):
        self.owner.AST.append(self)
        return self

class dbase_symbol:
    def __init__(self, src, name, link=None):
        self.what  = "symbol"
        self.owner = src
        self.name  = name
        self.link  = link
        self.add(src)
    def add(self):
        self.owner.AST.append(self)
        return self

class dbase_loop:
    def __init__(self, src, start, end):
        self.what  = "loop"
        seöf.owner = src
        self.start = start
        self.end   = end
        self.add(src)
    def add(self):
        self.owner.AST.append(self)
        return self

class dbase_command:
    def __init__(self, src, name, link=None):
        print("---> " + name)
        self.what  = "keyword"
        self.owner = src
        self.name  = name
        self.proc  = None
        self.prev  = None
        self.link  = link
    def add(self):
        self.owner.AST.append(self)
        return self

# ---------------------------------------------------------------------------
# only for testing ...
# ---------------------------------------------------------------------------
class dbase_test_array_struct:
    def __init__(self):
        test_proc = dbase_function(self, "test")
        test_loop = dbase_loop(self, 1,5)
        #
        test_var1 = dbase_val_variable(self, 1234)
        test_var2 = dbase_str_variable(self, "fuzzy")
        #
        test_sym1 = dbase_symbol(self, "foo", test_var1)
        test_sym2 = dbase_symbol(self, "bar", test_var2)
        test_sym3 = dbase_symbol(self, "baz", test_proc)
        #
        test_symA = dbase_symbol(self, "L", test_loop)
        
        self.AST = [
            test_sym1,
            test_sym2,
            test_sym3,
            test_symA
        ]
        for obj in self.AST:
            if isinstance(obj, dbase_symbol):
                print("dbase:")
                print("\tObject: " + obj.name)
                #print("--> " + str(obj.what))
            if isinstance(obj.link, dbase_function):
                #print("gfun")
                print("\t\tfunc type  : " + obj.link.what)
                print("\t\tfunc name  : " + obj.link.name)
                print("\t\tfunc result: " + obj.link.result)
            elif isinstance(obj.link, dbase_val_variable):
                print("\t\tfunc type  : " + obj.link.what)
                print("\t\tfunc value : " + str(obj.link.value))
            elif isinstance(obj.link, dbase_str_variable):
                print("\t\tfunc type  : " + obj.link.what)
                print("\t\tfunc value : " + obj.link.value)
            elif isinstance(obj.link, dbase_loop):
                print("\t\tfunc type  : " + obj.link.what)
                print("\t\tfunc start : " + str(obj.link.start))
                print("\t\tfunc end   : " + str(obj.link.end))
        
        sys.exit(20)

# ---------------------------------------------------------------------------
# \brief  class for interpreting dBase related stuff ...
#         the constructor need a string based script name that shall be read
#         and execute from memory.
#
# \param  filename - a named string for the script name
# \return objref - ctor's return the created object referenz from an memory
#         internal address that is managed by the operating system logic.
#
# \author paule32
# \since  1.0.0
# ---------------------------------------------------------------------------
class interpreter_dBase:
    def __init__(self, fname):
        self.script_name = fname;
        
        self.line = ""
        
        global con
        con = consoleApp()
        
        # Regular expression for recognizing identifiers.
        self.rexid = re.compile(r'^[a-zA-Z]\w*$')
        
        self.line_row    = 1
        self.line_col    = 1
        
        self.pos         = -1
        
        self.token_id    = ""
        self.token_prev  = ""
        self.token_str   = ""
        
        self.parse_data  = []
        
        self.token_macro_counter = 0
        self.token_comment_flag  = 0
        
        self.in_comment = 0
        
        self.AST = []
        
        self.byte_code = ""
        self.text_code = ""
        #self.text_code = "#con.cls();\n"
        
        # -------------------------------------------------------------------
        # for debuging, we use python logging library ...
        # -------------------------------------------------------------------
        try:
            self.log = logging.getLogger(__name__)
            logging.basicConfig(
                format="%(asctime)s: %(levelname)s: %(message)s",
                filename="observer.log",
                encoding="utf-8",
                filemode="w",
                level=logging.DEBUG)
        except:
            print("log file could not be open.")
        
        self.log.info("init ok: session start...")
        self.log.info("start parse: " + self.script_name)
        
        self.parse_open(self.script_name)
        self.source = self.parse_data[0]
    
    # -----------------------------------------------------------------------
    # \brief finalize checks and cleaning stuff ...
    # -----------------------------------------------------------------------
    def finalize(self):
        self.log.debug("macro   : " + str(self.token_macro_counter))
        self.log.debug("comment : " + str(self.token_comment_flag))
        if self.token_macro_counter < 0:
            self.log.debug("\aerror: unbound macro.")
            sys.exit(1)
    
    # -----------------------------------------------------------------------
    # \brief open a script file, and append the readed lines to the source
    #        object of this class. step one read the lines (maybe not need
    #        in future releases. step two read the content of the given file
    #        as one dimensional list which is used to parse the memory stream
    #        quicker than reading from storage disks.
    #        this function have a little payload, yes - but the time of read-
    #        ing the source data informations into the memory is quantitative
    #        better as doing read/write operations by the operation system.
    #
    # \param  filename - a string that identify the file/script that should
    #                    be loaded and parsed.
    # \author paule32
    # \since  1.0.0
    # -----------------------------------------------------------------------
    def parse_open(self, file_name):
        with open(self.script_name, 'r', encoding="utf-8") as self.file:
            self.file.seek(0)
            lines  = len(self.file.readlines())
            self.file.seek(0)
            source = self.file.read()
            self.file.close()
        self.parse_data.append(source)
    
    def add_command(self, name, link):
        self.token_command = dbase_command(self, name, link)
        return self.token_command
    
    def run(self):
        self.finalize()
        print("----------------------")
        print(self.text_code)
        input("press enter to start...")
        bytecode_text = compile(
            self.text_code,
            "<string>",
            "exec")
        self.byte_code = marshal.dumps(bytecode_text)
        bytecode = marshal.loads(self.byte_code)
        exec(bytecode)
    
    # -----------------------------------------------------------------------
    # \brief  get one char from the input stream/source line.
    #         the internal position cursor self.pos for the self.source will
    #         be incdrement by 1 character. for statistics, the line column
    #         position wull be updated.
    #         if the sel.pos cursor is greater as self.source codem then the
    #         end of data is marked, and python raise a silent "no errpr"
    #         exception to stop the processing of data (to prevent data/buffer
    #         overflow.
    #
    # \param  nothing
    # \return char - The "non" whitespace character that was found between
    #                existing comment types.
    # \author paule32
    # \since  1.0.0
    # -----------------------------------------------------------------------
    def getChar(self):
        self.line_col += 1
        self.pos += 1

        if self.pos >= len(self.source):
            if self.in_comment > 0:
                raise EParserErrorEOF("\aunterminated string reached EOF.")
            else:
                raise ENoParserError("\aend of file reached.")
        else:
            c = self.source[self.pos]
            return c
    
    def ungetChar(self, num):
        self.line_col -= num;
        self.pos -= num;
        c = self.source[self.pos]
        return c
    
    def getIdent(self):
        while True:
            c = self.getChar()
            if c.isspace():
                return self.token_str
            elif c.isalnum():
                self.token_str += c
            else:
                self.pos -= 1
                return self.token_str
    
    def getNumber(self):
        while True:
            c = self.getChar()
            if c.isdigit():
                self.token_str += c
            else:
                self.pos -= 1
                return self.token_str
    
    # -----------------------------------------------------------------------
    # \brief skip all whitespaces. whitespaces are empty lines, lines with
    #        one or more spaces (0x20): " ", \t, "\n".
    # -----------------------------------------------------------------------
    def skip_white_spaces(self):
        while True:
            c = self.getChar()
            if c == "\t" or c == " ":
                self.line_col += 1
                continue
            elif c == "\n" or c == "\r":
                self.line_col  = 1
                self.line_row += 1
                continue
            elif c == '/':
                c = self.getChar()
                if c == '*':
                    self.in_comment += 1
                    while True:
                        c = self.getChar()
                        if c == "\n":
                            self.line_col  = 1
                            self.line_row += 1
                            continue
                        if c == '*':
                            c = self.getChar()
                            if c == '/':
                                self.in_comment -= 1
                                break
                    return self.skip_white_spaces()
                elif c == '/':
                    self.handle_oneline_comment()
                    continue
                else:
                    self.ungetChar(1)
                    c = "/"
                    return c
            elif c == '&':
                c = self.getChar()
                if c == '&':
                    self.handle_oneline_comment()
                    continue
                else:
                    self.__unexpectedChar('&')
            elif c == '*':
                c = self.getChar()
                if c == '*':
                    self.handle_oneline_comment()
                    continue
                else:
                    self.__unexpectedChar('*')
            else:
                return c
    
    # -----------------------------------------------------------------------
    # \brief parse a one line comment: // for c++, ** and && for dBase ...
    # -----------------------------------------------------------------------
    def handle_oneline_comment(self):
        while True:
            c = self.getChar()
            if c == "\n":
                self.line_row += 1
                self.line_col  = 1
                break
    
    def handle_say(self):
        c = self.skip_white_spaces()
        print("==> " + c)
        if c.isdigit():
            self.token_str = c
            self.getNumber()
            print("col: " + self.token_str)
            c = self.skip_white_spaces()
            if c == ',':
                c = self.skip_white_spaces()
                if c.isdigit():
                    self.token_str = c
                    self.getNumber()
                    print("row: " + self.token_str)
                else:
                    raise Exception("xxxxx")
            else:
                raise Exception("sayy22")
    
    def parse(self):
        with open(self.script_name, 'r', encoding="utf-8") as self.file:
            self.file.seek(0)
            self.total_lines = len(self.file.readlines())
            self.file.seek(0)
            self.source = self.file.read()
            self.log.debug("lines: " + str(self.total_lines))
            self.file.close()
        
        if len(self.source) < 1:
            print("no data available.")
            return
        
        # ------------------------------------
        # ------------------------------------
        while True:
            c = self.skip_white_spaces()
            if c == '@':
                self.handle_say()
            elif c.isalpha():
                self.token_str = c
                self.getIdent()
                if self.token_str == "clear":
                    print("clear")
                    c = self.skip_white_spaces()
                    if c.isalpha():
                        self.token_str = c
                        self.getIdent()
                        if self.token_str == "screen":
                            print("scre")
                            self.text_code += "#con.cls()\n";
                        elif self.token_str == "memory":
                            print("mem")
                        else:
                            print("--> " + self.token_str)
                            self.ungetChar(len(self.token_str))
                    else:
                        self.ungetChar(1)
                        continue
                if self.token_str == "show":
                    print("--> " + self.token_str)
    
    def __unexpectedToken(self):
        calledFrom = inspect.stack()[1][3]
        msg = "\a\nunexpected token: '%s' on line: '%d' in: '%s'.\n"
        msg = msg % (
            self.token_str,
            self.line_row,
            self.script_name)
        print(msg)
        sys.exit(1)
    
    def __unexpectedChar(self, chr):
        calledFrom = inspect.stack()[1][3]
        msg = "\a\nunexpected character: '%c' on line: '%d' in: '%s'.\n"
        msg = msg % (chr,
            self.line_row,
            self.script_name)
        print(msg)
        sys.exit(1)
    
    def __unexpectedEndOfLine(self):
        calledFrom = inspect.stack()[1][3]
        msg = "\a\nunexpected end of line: line: '%d' in: '%s'.\n"
        msg = msg % (
            self.line_row,
            self.script_name)
        print(msg)
        sys.exit(1)
# ---------------------------------------------------------------------------
# \brief  provide dBase DSL (domain source language)- dBL (data base language
#         class for handling and programming database applications.
#
# \param  filename - a string based file/script that shall be handled.
# \return objref - ctor's return the created object referenz from an memory
#         internal address that is managed by the operating system logic.
#
# \author paule32
# \since  1.0.0
# ---------------------------------------------------------------------------
class dBaseDSL:
    def __init__(self):
        self.script = None
    
    def __new__(self, script_name):
        try:
            parser  = interpreter_dBase(script_name)
            parser.parse()
        except Exception as e:
            parser.run()
        return self
    
    def parse(self):
        return
    
    def run(self):
        return
