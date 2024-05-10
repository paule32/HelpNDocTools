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
    def __init__(self, name):
        self.what = "func"
        self.name = name
        self.result = "tztz"

class dbase_val_variable:
    def __init__(self, value=0):
        self.what  = "val"
        self.value = value

class dbase_str_variable:
    def __init__(self, value=""):
        self.what  = "str"
        self.value = value

class dbase_symbol:
    def __init__(self, name, link=None):
        self.what = "symbol"
        self.name = name
        self.link = link

class dbase_loop:
    def __init__(self, start, end):
        self.what  = "loop"
        self.start = start
        self.end   = end

class dbase_command_set:
    def __init__(self):
        self.what = "keyword"
        self.link = None
class dbase_command_color:
    def __init__(self):
        self.what = "keyword"
        self.prev = None
        self.link = None
class dbase_command_to:
    def __init__(self):
        self.what = "keyword"
        self.prev = None
        self.link = None

class dbase_test_array_struct:
    def __init__(self):
        test_proc = dbase_function("test")
        test_loop = dbase_loop(1,5)
        #
        test_var1 = dbase_val_variable(1234)
        test_var2 = dbase_str_variable("fuzzy")
        #
        test_sym1 = dbase_symbol("foo", test_var1)
        test_sym2 = dbase_symbol("bar", test_var2)
        test_sym3 = dbase_symbol("baz", test_proc)
        #
        test_symA = dbase_symbol("L", test_loop)
        
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

class interpreter_dBase():
    def __init__(self, fname):
        self.script_name = fname;
        self.tokendic = {
            "class": "class",
            ":"    : "colon",
            "|"    : "pipe" ,
        }
        
        global con
        con = consoleApp()
        
        # Regular expression for recognizing identifiers.
        self.rexid = re.compile(r'^[a-zA-Z]\w*$')
        
        self.lineno    = 0
        self.status    = 0
        self.pos       = 100
        self.line      = ""
        self.linelen   = 0
        
        self.tokenlineno = 0
        self.tokenid     = None
        self.total_lines = 0
        
        self.tokenstr  = ""
        self.previd    = ""
        
        self.token_macro_counter = 0
        self.token_comment_flag  = 0
        
        self.dbaseAST  = []
        
        self.byte_code = ""
        self.text_code = "#con.cls();\n"
        
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
        
        self.log.debug("init ok: session start...")
    
    def finalize(self):
        self.log.debug("macro   : " + str(self.token_macro_counter))
        self.log.debug("comment : " + str(self.token_comment_flag))
        if self.token_macro_counter < 0:
            self.log.debug("\aerror: unbound macro.")
            sys.exit(1)
    
    def run(self):
        self.finalize()
        bytecode_text = compile(
            self.text_code,
            "<string>",
            "exec")
        self.byte_code = marshal.dumps(bytecode_text)
        bytecode = marshal.loads(self.byte_code)
        exec(bytecode)
    
    def getChar(self):
        self.pos += 1
        if self.pos >= self.linelen:
            self.lineno += 1
            if self.lineno >= self.total_lines:
                self.log.debug("EOF: " + self.script_name)
                self.check_finalize()
                raise ENoParserError("EOF: " + self.script_name)
            self.pos = 0
            self.line = self.file.readline()
            self.linelen = len(self.line)
        c = self.line[self.pos]
        return c
    
    def handle_c_comment(self):
        try:
            flag = False
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
                        if c == " ":
                            continue
                        elif c == "\n":
                            continue
                        elif c == "/":
                            flag = True
                            break
                        elif c.isalpha():
                            self.tokenstr = c
                            break
                        elif c.isdigit():
                            break
                        else:
                            self.__unexpectedChar(c)
            if c.isalpha():
                self.getIdent()
                self.log.debug("====> " + self.tokenstr)
            return c
        except:
            self.__unexpectedEndOfLine()
    
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
            if c == "/":
                self.pos -= 1
                self.tokenstr = ""
                c = self.check_comment()
                return c
            elif not c.isspace():
                self.pos -= 1
                c = self.check_comment()
                return c
    
    def handle_oneline_comment(self):
        while True:
            c = self.getChar()
            if c == "\n":
                self.lineno += 1
                self.pos += 1
                if self.lineno >= self.total_lines:
                    break
                if self.pos >= self.linelen:
                    self.line = self.file.readline()
                    self.linelen = len(self.line)
                    self.pos = 0
                    break
                break
        if c == "\n":
            self.log.debug("nwwww")
            c = self.skip_white_spaces()
            if c.isalpha():
                self.tokenstr = c
                self.getIdent()
                self.log.debug("ccc=> " + self.tokenstr)
        if c.isalpha():
            return c
        elif c == "&":
            c = self.getChar()
            if c == "&":
                c = self.handle_oneline_comment()
                self.log.debug("oooi--> " + c)
                if c.isalpha():
                    self.tokenstr = ""
                    self.getIdent()
                    self.log.debug("aaa>>> " + self.tokenstr)
                    if self.total_lines >= self.lineno:
                        raise ENoParserError("EOF")
            else:
                self.log.debug("todo")
        elif c == "#":
            self.log.debug("sharp")
            return c
        elif c == "\n":
            c = self.skip_white_spaces()
            if c == "&":
                c = self.getChar()
                if c == "&":
                    c = self.handle_oneline_comment()
                    return c
                else:
                    self.log.debug("todo")
            elif c == "/":
                c = self.getChar()
                if c == "*":
                    self.token_comment_flag += 1
                    self.handle_c_comment()
                elif c == "/":
                    c = self.handle_oneline_comment()
                    return c
            else:
                self.ungetChar(1)
        else:
            self.__unexpectedChar(c)
        return c
    
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
            self.tokenstr = ""
            self.getIdent()
            self.log.debug("zz:" + self.tokenstr + ":uu")
            if self.tokenstr == "to":
                self.tokenstr = ""
                self.getIdent()
                self.log.debug("p1:" + self.tokenstr + ":uu")
                c = self.skip_white_spaces()
                if c == "/":
                    self.ungetChar(1)
                    self.tokenstr = ""
                    c = self.check_comment()
                    self.log.debug("===> " + c)
                else:
                    c = self.check_comment()
                    #self.log.debug("--> " + c + "<-- <y<")
                    #self.__unexpectedChar("c")
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
            self.tokenstr = ""
            self.handle_command_set()
    
    def parse(self):
        with open(self.script_name, 'r', encoding="utf-8") as self.file:
            self.total_lines = len(self.file.readlines())
            self.log.debug("-----> " + str(self.total_lines))
        self.file.close()
        with open(self.script_name, 'r', encoding="utf-8") as self.file:
            while self.status != 1111:
                # ------------------------------------
                # get the next character.
                # read next line first, if neccassary
                # ------------------------------------
                if self.pos < self.linelen:
                    c = self.line[self.pos]
                else:
                    self.lineno += 1
                    self.line = self.file.readline()
                    self.linelen = len(self.line)
                    self.pos = 0
                    if self.line == "":  # eof
                        self.status = 1111
                    else:
                        c = self.line[self.pos]
                if self.status == 0:
                    if self.tokenid:
                        if self.tokenstr.isdigit():
                            self.tokenid = "num"
                        elif self.rexid.match(self.tokenstr):
                            self.tokenid = "id"
                            if self.tokenstr == "set":
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
                            if self.lineno >= self.total_lines:
                                break
                            c = self.check_comment()
                            
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
                
                elif self.status == 1:
                    if c == "/":
                        self.log.debug("C++ comment 333")
                        self.tokenid = "comment"
                        self.tokenstr += c
                        self.pos += 1
                        self.status = 0
                    elif c == "*":
                        #self.log.debug("C comment")
                        self.token_comment_flag += 1
                        self.tokenid = "comment"
                        self.tokenstr += c
                        self.pos += 1
                        self.status = 3
                    else:
                        self.status = 0
                
                elif self.status == 2:
                    if c == "\n":
                        self.status = 0
                    else:
                        self.tokenstr += c
                    self.pos += 1
                
                elif self.status == 3:
                    if c == "*":
                        self.tokenstr += c
                        self.status = 4
                    else:
                        self.tokenstr += c
                        self.status = 3
                    self.pos += 1
                
                elif self.status == 4:
                    if c == "/":
                        self.tokenstr += c
                        self.status = 0
                    elif c == "*":
                        self.tokenstr += c
                    else:
                        self.tokenstr += c
                        self.status = 3
                    self.pos += 1
                
                elif self.status == 5:
                    if c == "\n":
                        self.status = 0
                    else:
                        self.tokenstr += c
                    self.pos += 1
                
                elif self.status == 6:
                    if c == "\\":
                        self.tokenstr += c
                        self.status = 7
                    elif c == '"':
                        self.tokenstr += c
                        self.status = 0
                    else:
                        self.tokenstr += c
                    self.pos += 1
                
                elif self.status == 7:
                    self.tokenstr += c
                    self.status = 6
                    self.pos += 1
                
                elif self.status == 8:
                    self.tokenstr += c
                    self.status = 9
                    self.pos += 1
                
                elif self.status == 9:
                    if c == "'":
                        self.tokenstr += c
                        self.status = 0
                        self.pos += 1
                    else:
                        self.tokenid = "error"
                        self.tokenstr += c
                        self.status = 0
                
                elif self.status == 333:
                    if c.isspace():
                        self.pos += 1
                        self.status = 0
                    elif c in self.tokendic:
                        self.status = 0
                    else:
                        self.tokenstr += c
                        self.pos += 1
            
            if self.tokenid:
                self.tokenid = None
                self.tokenstr = ""
                self.tokenlineno = 0
            
        self.file.close()
    
    def __unexpectedToken(self):
        calledFrom = inspect.stack()[1][3]
        msg = "\a\nunexpected token: '%s' on line: '%d' in: '%s'.\n"
        msg = msg % (self.tokenstr, self.tokenlineno, self.script_name)
        if self.status != -1:
            msg += "status = %d in %s()\n" % (self.status, calledFrom)
        print(msg)
        sys.exit(1)
    
    def __unexpectedChar(self, chr):
        calledFrom = inspect.stack()[1][3]
        msg = "\a\nunexpected character: '%c' on line: '%d' in: '%s'.\n"
        msg = msg % (chr, self.tokenlineno, self.script_name)
        if self.status != -1:
            msg += "status = %d in %s()\n" % (self.status, calledFrom)
        print(msg)
        sys.exit(1)
    
    def __unexpectedEndOfLine(self):
        calledFrom = inspect.stack()[1][3]
        msg = "\a\nunexpected end of line: line: '%d' in: '%s'.\n"
        msg = msg % (self.tokenlineno, self.script_name)
        if self.status != -1:
            msg += "status = %d in %s()\n" % (self.status, calledFrom)
        print(msg)
        sys.exit(1)
