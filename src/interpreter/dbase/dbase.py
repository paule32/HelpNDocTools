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
# class for interpreting dBase related stuff ...
# ---------------------------------------------------------------------------
class interpreter_dBase():
    def __init__(self, fname):
        self.script_name = fname;
        
        self.line = ""
        
        global con
        con = consoleApp()
        
        # Regular expression for recognizing identifiers.
        self.rexid = re.compile(r'^[a-zA-Z]\w*$')
        
        self.lineno      = 1
        self.pos         = 0
        
        self.token_id    = ""
        self.token_prev  = ""
        
        self.parse_data  = []
        
        self.token_macro_counter = 0
        self.token_comment_flag  = 0
        
        self.AST = []
        
        self.byte_code = ""
        self.text_code = "#con.cls();\n"
        
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
    # finalize checks and cleaning stuff ...
    # -----------------------------------------------------------------------
    def finalize(self):
        self.log.debug("macro   : " + str(self.token_macro_counter))
        self.log.debug("comment : " + str(self.token_comment_flag))
        if self.token_macro_counter < 0:
            self.log.debug("\aerror: unbound macro.")
            sys.exit(1)
    
    # -----------------------------------------------------------------------
    # open a script file, and append the readed lines to the parse_data obj.
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
        bytecode_text = compile(
            self.text_code,
            "<string>",
            "exec")
        self.byte_code = marshal.dumps(bytecode_text)
        bytecode = marshal.loads(self.byte_code)
        exec(bytecode)
    
    # -----------------------------------------------------------------------
    # get one char from the input stream/source line ...
    # -----------------------------------------------------------------------
    def getChar(self):
        self.pos += 1
        if self.lineno <= self.total_lines:
            if self.pos >= len(self.line):
                raise ENoParserError("end of file reached.")
            else:
                c = self.line[self.pos]
                return c
        else:
            c = self.line[self.pos]
            return c
    
    # -----------------------------------------------------------------------
    # parse a C like comment block over multiple lines: /* ... */
    # -----------------------------------------------------------------------
    def handle_c_comment(self):
        while True:
            c = self.getChar()
            if c == "\n":
                self.lineno += 1
                self.pos = 0
                self.line = self.file.readline()
                self.linelen = len(self.line)
                c = self.line[self.pos]
            elif c == "*":
                c = self.getChar()
                if c == "/":
                    self.token_comment_flag -= 1
                    c = self.skip_white_spaces()
                    return c
    
    def check_comment(self):
        while True:
            c = self.getChar()
            if c.isspace():
                pass
            elif c == "/":
                self.pos += 1
                if self.pos >= self.linelen:
                    self.__unexpectedEndOfLine()
                c = self.line[self.pos]
                if c == "*":
                    self.log.debug("C commentl")
                    self.token_comment_flag += 1
                    c = self.handle_c_comment()
                elif c == "/":
                    self.log.debug("C++ comment 222")
                    c = self.handle_oneline_comment()
                    self.log.debug("-->>>> " + c)
                    if c == "#":
                        c = self.handle_macro_command()
                        self.log.debug("----" + c)
                        return c
                    if c.isalpha():
                        self.tokenstr = c
                        #self.getIdent()
                        self.log.debug("-xcxs--> " + self.tokenstr)
                        self.tokenstr = ""
                    #return c
                else:
                    self.log.debug("2222")
                    self.pos -= 1
                    c = self.line[self.pos]
                    return c
            else:
                return c
    
    def ungetChar(self, num):
        self.pos -= num;
    
    def getIdent(self):
        while True:
            c = self.getChar()
            if c.isspace():
                return self.tokenstr
            elif c.isalnum():
                self.tokenstr += c
            else:
                self.pos -= 1
                return self.tokenstr
    
    def getNumber(self):
        while True:
            c = self.getChar()
            if c.isspace():
                return self.tokenstr
            elif c.isdigit():
                self.tokenstr += c
            else:
                self.pos -= 1
                return self.tokenstr
    
    def skip_white_spaces(self):
        while True:
            c = self.getChar()
            if not c.isspace():
                print("======> " + c)
                return c
    
    def handle_lang_commands(self):
        self.log.debug("ccc=> " + self.tokenstr)
        if self.tokenstr == "set":
            cmd = dbase_command(self, "set")
            self.token_command = cmd.add()
            self.tokenstr = ""
            self.handle_command_set()
    
    # -----------------------------------------------------------------------
    # parse a one line comment: // for c++, ** and && for dBase ...
    # -----------------------------------------------------------------------
    def handle_oneline_comment(self):
        while True:
            c = self.getChar()
            if c == "\n":
                self.lineno += 1
                self.pos = 0
                break
    
    def handle_macro_command(self):
        c = self.skip_white_spaces()
        self.log.debug("----->>> " + c)
        if c == "/":
            c = self.getChar()
            if c == "*":
                self.token_comment_flag += 1
                self.handle_c_comment()
            elif c == "/":
                self.handle_oneline_comment()
            else:
                self.ungetChar(1)
                return
        elif c.isalpha():
            self.tokenstr = c
            self.getIdent()
            self.log.debug("---> " + self.tokenstr)
            if self.tokenstr == "ifdef":
                self.token_macro_counter += 1
                c = self.skip_white_spaces()
                if c.isalpha():
                    self.tokenstr = c
                    self.getIdent()
                    self.log.debug("o--> " + self.tokenstr)
                    c = self.skip_white_spaces()
                    if c == "\n":
                        c = self.skip_white_spaces()
                        if c == "#":
                            self.log.debug("sharp")
                            c = self.handle_macro_command()
                    elif c == "#":
                        c = self.skip_white_spaces()
                        return c
                    elif c.isalpha():
                        self.tokenstr = c
                        self.getIdent()
                        self.log.debug("a--> " + self.tokenstr);
                        if self.tokenstr == "endif":
                            self.token_macro_counter -= 1
                        #else:
                        #    #self.token_macro_counter += 1
                        c = self.skip_white_spaces()
                        return c
                    elif c.isdigit():
                        self.getIdent()
                        self.log.debug("b--> " + self.tokenstr);
                    elif c == "\n":
                        self.tokenlineno = self.lineno
                        self.__unexpectedEndOfLine()
                elif c == "\n":
                    self.tokenlineno = self.lineno
                    self.__unexpectedEndOfLine()
                else:
                    self.__unexpectedChar(c)
                return
            elif self.tokenstr == "if":
                self.token_macro_counter += 1
                c = self.skip_white_spaces()
                if c == "\n":
                    c = self.skip_white_spaces()
                if c.isdigit():
                    self.tokenstr = c
                    self.getNumber()
                    self.log.debug("digi: " + self.tokenstr)
                    c = self.skip_white_spaces()
                    self.tokenstr = ""
                    if c == "\n":
                        c = self.skip_white_spaces()
                    if c == "=":
                        c = self.getChar()
                        if c == "=":
                            c = self.skip_white_spaces()
                            if c == "\n":
                                self.__unexpectedEndOfLine()
                            self.log.debug("---->>>> " + c)
                            if c.isdigit():
                                self.tokenstr = c
                                self.getNumber()
                                self.log.debug(">digi: " + self.tokenstr)
                                c = self.skip_white_spaces()
                                self.log.debug("c-->o> " + c)
                                if c == "#":
                                    c = self.handle_macro_command()
                                if c == "\n":
                                    c = self.skip_white_spaces()
                                #return
                            else:
                                self.__unexpectedChar(c)
                        elif c == "<":
                            c = self.skip_white_spaces()
                            if c == "\n":
                                self.__unexpectedEndOfLine()
                            c = self.skip_white_spaces()
                            if c.isdigit():
                                self.getNumber()
                                self.log.debug("digi: " + self.tokenstr)
                            else:
                                self.__unexpectedChar(c)
                        else:
                            self.__unexpectedChar(c)
                    elif c == ">":
                        c = self.getChar()
                        if c == "=":
                            c = self.skip_white_spaces()
                            if c == "\n":
                                self.__unexpectedEndOfLine()
                            c = self.skip_white_spaces()
                            if c.isdigit():
                                self.getNumber()
                                self.log.debug("digi: " + self.tokenstr)
                            else:
                                self.__unexpectedChar(c)
                        else:
                            self.__unexpectedChar(c)
                    elif c == "!":
                        c = self.getChar()
                        if c == "=":
                            c = self.skip_white_spaces()
                            if c == "\n":
                                self.__unexpectedEndOfLine()
                            c = self.skip_white_spaces()
                            if c.isdigit():
                                self.getNumber()
                                self.log.debug("digi: " + self.tokenstr)
                            else:
                                self.__unexpectedChar(c)
                        else:
                            self.__unexpectedChar(c)
                    elif c == "<":
                        c = self.getChar()
                        if c == ">":
                            c = self.skip_white_spaces()
                            if c == "\n":
                                self.__unexpectedEndOfLine()
                            c == self.skip_white_spaces()
                            if c.isdigit():
                                self.getNumber()
                                self.log.debug("digi: " + self.tokenstr)
                            else:
                                self.__unexpectedChar(c)
                        elif c == "=":
                            c = self.skip_white_spaces()
                            if c == "\n":
                                self.__unexpectedEndOfLine()
                            c = self.skip_white_spaces()
                            if c.isdigit():
                                self.getNumber()
                                self.log.debug("digi: " + self.tokenstr)
                            else:
                                self.__unexpectedChar(c)
                        else:
                            self,__unexpectedChar(c)
                    self.log.debug("==> " + c)
                    if c == "#":
                        c = self.handle_macro_command()
                        c = self.skip_white_spaces()
                        self.log.debug("OO=> " + c)
                        if c.isalpha():
                            self.tokenstr = c
                            self.getIdent()
                            if self.tokenstr == "endif":
                                self.log.debug("oiouo")
                                self.token_macro_counter -= 1
                            else:
                                self.log.debug("zuzu")
                                return
                        else:
                            self.log.debug("todo")
                            return c
                    self.log.debug("tuz")
                self.log.debug("muz")
            elif self.tokenstr == "endif":
                self.log.debug("ENDIF 11")
                self.token_macro_counter -= 1
                self.log.debug("ccc> " + str(self.token_macro_counter))
                c = self.skip_white_spaces()
                if c == "#":
                    self.log.debug("aaa> " + c)
                    self.log.debug("ccc> " + str(self.token_macro_counter))
                    c = self.handle_macro_command()
                    return c
        elif c.isdigit():
            self.tokenstr = c
            c = self.getNumber()
            self.log.debug("num--> " + self.tokenstr);
        elif c == "\n":
            self.tokenlineno = self.lineno
            self.__unexpectedEndOfLine()
        else:
            self.__unexpectedChar(c)
    
    def handle_command_set(self):
        self.getIdent()
        self.log.debug("zz:" + self.tokenstr + ":uu")
        if self.tokenstr == "color":
            print("color")
            self.log.debug("===> " + self.tokenstr)
            cmd = dbase_command(self, "color", self.token_command)
            self.token_command = cmd.add()
            self.tokenstr = ""
            self.getIdent()
            print("----> " + self.tokenstr)
            self.log.debug("zz:" + self.tokenstr + ":uu")
            if self.tokenstr == "to":
                cmd = dbase_command(self, "to", self.token_command)
                self.token_command = cmd.add()
                self.tokenstr = ""
                c = self.skip_white_spaces()
                if c.isalpha():
                    print("ooo> " + c)
                    c = self.getChar()
                    print("ooo> " + c)
                    if c.isspace():
                        c = self.skip_white_spaces()
                        print("ooo> " + c)
                    self.getIdent()
                    print("===> " + self.tokenstr)
                
                self.tokenstr = ""
                self.getIdent()
                self.log.debug("p1:" + self.tokenstr + ":uu")
                cmd = dbase_command(self, self.tokenstr, self.token_command)
                self.token_command = cmd.add()
                c = self.skip_white_spaces()
                print("==> " + c)
                if c == "/":
                    c = self.getChar()
                    if c.isspace():
                        c = self.skip_white_spaces()
                        print("==> " + c)
                        return c
                    elif c == "*":
                        c = self.handle_c_comment()
                        return c
                    elif c == "/":
                        print("c++ commenter")
                        c = self.handle_oneline_comment()
                        return c
                    elif c.isalpha():
                        self.token_str = c
                        self.getIdent()
                        self.log.debug("===> " + c)
                        self.log.debug("===> " + self.token_str)
                    else:
                        self.__unexpectedChar(c)
                else:
                    self.__unexpectedChar("oooo")
            else:
                self.__unexpectedToken()
        else:
            self.__unexpectedToken()

    def handle_commands(self):
        #self.log.debug("zz:" + self.tokenstr + ":uu")
        if self.tokenstr == "&":
            c = self.getChar()
            if c == "&":
                self.log.debug("dBase Comment 3 ----> &&")
                c = self.handle_oneline_comment()
                if c == "\n":
                    c = self.skip_white_spaces()
                    if c == "#":
                        self.handle_macro_command()
            else:
                self.pos -= 1
                c = "&"
        elif self.tokenstr == "set":
            print("setter")
            self.token_command = dbase_command(self, "set", None)
            self.token_command.prev = self.token_command
            
            self.tokenstr = ""
            self.handle_command_set()
    
    def parse(self):
        with open(self.script_name, 'r', encoding="utf-8") as self.file:
            self.file.seek(0)
            self.total_lines = len(self.file.readlines())
            self.file.seek(0)
            self.source = self.file.read()
            self.log.debug("-----> " + str(self.total_lines))
            self.file.close()
        
        if len(self.source) < 1:
            print("no data available.")
            return
        # ------------------------------------
        # get the next character.
        # read next line first, if neccassary
        # ------------------------------------
        while True:
            c = self.getChar()
            if c.isspace():
                continue
            elif c.isdigit():
                self.tokenid = "num"
            elif c.isalpha():
                print("alpja")
                self.tokenid = "id"
                if self.tokenstr == "set":
                    print("SETTER")
                    self.handle_commands()
                elif self.tokenstr == "clear":
                    self.log.debug("Token: " + self.tokenstr)
                    self.previd  = "clear"
                    self.tokenid = self.previd
                    self.tokenlineno = self.lineno
                    self.status = 0
                elif (self.tokenstr == "all") and (self.previd == "clear"):
                    #self.text_code += "con.cls();"
                    self.previd = ""
                    self.status = 0
                else:
                    self.log.debug("------> " + self.tokenstr)
                    if self.tokenstr == "atzi":
                        self.tokenstr = ""
                        self.status = 0
                    else:
                        self.__unexpectedToken()
                    self.__unexpectedToken()
                
                if c.isspace():
                    pass
                elif c == "/":
                    c = self.getChar()
                    if c == "*":
                        self.token_comment_flag += 1
                        c = self.handle_c_comment()
                    elif c == "/":
                        self.log.debug("C++ comment 111")
                        c = self.handle_oneline_comment()
                        print("oooooo>>>> " + c)
                        self.tokenstr = c
                        self.getIdent()
                        
                        self.previd = self.tokenstr
                        self.handle_commands()
                        self.status = 0
                    else:
                        self.tokenstr = c
                        self.getIdent()
                        #self.log.debug("zz: " + c + " :usssu") # atzi
                        
                        self.status = 0
                elif c == "*":
                    c = self.getChar()
                    if c == "*":
                        self.log.debug("dBase Comment 1 ----> **")
                        c = self.handle_oneline_comment()
                        if self.lineno >= self.total_lines:
                            break
                    else:
                        self.log.debug("todo")
                elif c == "&":
                    c = self.getChar()
                    if c == "&":
                        self.log.debug("dBase Comment 2 ----> &&")
                        c = self.handle_oneline_comment()
                        if self.lineno >= self.total_lines:
                            break
                    else:
                        self.log.debug("todo")
                elif c == "#":
                    self.log.debug("preproc")
                    self.handle_macro_command()
                else:
                    self.tokenstr = c
                    self.tokenlineno = self.lineno
                    self.status = 333
                
                if self.pos >= self.linelen:
                    #self.log.debug("1111111111")
                    break
                self.pos += 1
            
            elif c == "/":
                c = self.getChar()
                if c == "/":
                    self.log.debug("C++ comment 333")
                    self.handle_oneline_comment()
                    continue
                elif c == "*":
                    self.log.debug("C comment 3421")
                    self.handle_c_comment()
                elif c.isspace():
                    continue
            elif c == "&":
                c = self.getChar()
                if c == "&":
                    self.log.debug("dBASE comment 11")
                    self.handle_oneline_comment()
                    continue
                else:
                    self.__unexpectedChar(c)
            elif c == "*":
                c = self.getChar()
                if c == "*":
                    print("dddddd")
                    self.log.debug("dBASE comment 22")
                    self.handle_oneline_comment()
                    continue
                    print("ddBB>> " + c)
                else:
                    self.__unexpectedChar(c)
    
    def __unexpectedToken(self):
        calledFrom = inspect.stack()[1][3]
        msg = "\a\nunexpected token: '%s' on line: '%d' in: '%s'.\n"
        msg = msg % (self.token_id, self.lineno, self.script_name)
        if self.status != -1:
            msg += "status = %d in %s()\n" % (self.status, calledFrom)
        print(msg)
        sys.exit(1)
    
    def __unexpectedChar(self, chr):
        calledFrom = inspect.stack()[1][3]
        msg = "\a\nunexpected character: '%c' on line: '%d' in: '%s'.\n"
        msg = msg % (chr, self.lineno, self.script_name)
        if self.status != -1:
            msg += "status = %d in %s()\n" % (self.status, calledFrom)
        print(msg)
        sys.exit(1)
    
    def __unexpectedEndOfLine(self):
        calledFrom = inspect.stack()[1][3]
        msg = "\a\nunexpected end of line: line: '%d' in: '%s'.\n"
        msg = msg % (self.lineno, self.script_name)
        if self.status != -1:
            msg += "status = %d in %s()\n" % (self.status, calledFrom)
        print(msg)
        sys.exit(1)

class dBaseDSL:
    def __init__(self):
        self.script = None
    
    def __new__(self, script_name):
        self.script = script_name
        self.parser = ParserDSL(self.script, "dbase")
        
        parser_comment = self.parser.comment(self.parser)
        #self.parser.add("sttr")
        return self
    
    def parse(self):
        return
    
    def run(self):
        return
