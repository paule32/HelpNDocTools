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
        self.tokenid   = None
        self.total_lines = 0
        
        self.tokenstr  = ""
        self.previd    = ""
        
        self.byte_code = ""
        self.text_code = "#con.cls();\n"
    
    def run(self):
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
            self.pos = 0
            self.line = self.file.readline()
            self.linelen = len(self.line)
        c = self.line[self.pos]
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
                    #print("C commentl")
                    try:
                        while True:
                            c = self.getChar()
                            if c == "\n":
                                #print("ne")
                                self.lineno += 1
                                self.pos = 0
                                self.line = self.file.readline()
                                self.linelen = len(self.line)
                                c = self.line[self.pos]
                            elif c == "*" and self.getChar() == "/":
                                #print("222222")
                                #self.pos += 1
                                c = self.getChar()
                                break
                        #print(">--" + c + "--")
                        #c = self.skip_white_spaces()
                        c = self.getIdent()
                        #print("--" + c + "--")
                        if c.isspace():
                            print("spacer")
                            #print("--" + c + "--")
                        return c
                    except:
                        self.__unexpectedEndOfLine()
                elif c == "/":
                    #print("C++ comment 222")
                    while True:
                        c = self.getChar()
                        if c == "":
                            break
                        elif c == "\n":
                            break
                    #print("111111")
                    c = self.skip_white_spaces()
                    if not c.isspace():
                        self.pos -= 1
                        c = self.line[self.pos]
                        #print(">>>" + c + "<<<")
                        #print(self.tokenstr)
                        return c
                else:
                    print("2222")
                    self.pos -= 1
                    c = self.line[self.pos]
                    return c
            else:
                return c
    
    def ungetChar(self, num):
        self.pos -= num;

    def getIdent(self):
        while True:
            self.pos += 1
            if self.pos >= self.linelen:
                self.lineno += 1
                self.pos = 0
                self.line = self.file.readline()
                self.linelen = len(self.line)
            c = self.line[self.pos]
            if c.isspace():
                return self.tokenstr
            elif c.isalnum():
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
    def handle_commands(self):
        print("zz:" + self.tokenstr + ":uu")
        if self.tokenstr == "set":
            self.tokenstr = ""
            self.getIdent()
            print("zz:" + self.tokenstr + ":uu")
            if self.tokenstr == "color":
                self.tokenstr = ""
                self.getIdent()
                print("zz:" + self.tokenstr + ":uu")
                if self.tokenstr == "to":
                    self.tokenstr = ""
                    self.getIdent()
                    print("p1:" + self.tokenstr + ":uu")
                    c = self.skip_white_spaces()
                    if c == "/":
                        self.ungetChar(1)
                        self.tokenstr = ""
                        c = self.check_comment()
                        print("===> " + c)
                    else:
                        c = self.check_comment()
                        #print("--> " + c + "<-- <y<")
                        #self.__unexpectedChar("c")
    
    def parse(self):
        with open(self.script_name, 'r', encoding="utf-8") as self.file:
            self.total_lines = len(self.file.readlines())
            print("-----> " + str(self.total_lines))
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
                        if self.tokenid == "unknown":
                            if self.tokenstr.isdigit():
                                self.tokenid = "num"
                            elif self.rexid.match(self.tokenstr):
                                self.tokenid = "id"
                                if self.tokenstr == "set":
                                    self.handle_commands()
                                    #self.pos += 1
                                    #self.tokenstr = c
                                    self.previd = "set"
                                    self.status = 0
                                elif self.tokenstr == "clear":
                                    print("Token: " + self.tokenstr)
                                    self.previd  = "clear"
                                    self.tokenid = self.previd
                                    self.tokenlineno = self.lineno
                                    self.status = 0
                                elif (self.tokenstr == "all") and (self.previd == "clear"):
                                    #self.text_code += "con.cls();"
                                    self.previd = ""
                                    self.status = 0
                                else:
                                    print("------> " + self.tokenstr)
                                    if self.tokenstr == "atzi":
                                        self.tokenstr = ""
                                        self.status = 0
                                    else:
                                        self.__unexpectedToken()
                    
                    if c.isspace():
                        pass
                    elif c == "/":
                        c = self.getChar()
                        if c == "*":
                            while True:
                                c = self.getChar()
                                if c == "\n":
                                    #print("ne")
                                    self.lineno += 1
                                    self.pos = 0
                                    self.line = self.file.readline()
                                    self.linelen = len(self.line)
                                    c = self.line[self.pos]
                                elif c == "*" and self.getChar() == "/":
                                    #print("1111")
                                    self.pos += 1
                                    c = self.getChar()
                                    break
                            #c = self.check_comment()
                            #print("zz:" + c + ":zz")
                        elif c == "/":
                            #print("C++ comment 111")
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
                                    else:
                                        c = self.line[self.pos]
                                        self.lineno += 1
                                        break
                            if self.lineno >= self.total_lines:
                                break
                            c = self.check_comment()
                            self.tokenstr = c
                            c = self.getIdent()
                            #print(">>---> " + self.tokenstr)
                            #self.tokenstr += c
                            self.previd = self.tokenstr
                            self.handle_commands()
                            self.status = 0
                        else:
                            self.tokenstr = c
                            c = self.getIdent()
                            #print("zz: " + c + " :usssu") # atzi
                            
                            self.status = 0
                    elif c == "#":
                        #print("preproc")
                        self.tokenstr = c
                        self.tokenlineno = self.lineno
                        self.status = 0
                    else:
                        self.tokenid = "unknown"
                        self.tokenstr = c
                        self.tokenlineno = self.lineno
                        self.status = 333
                    
                    if self.pos >= self.linelen:
                        print("1111111111")
                        break
                    self.pos += 1
                
                elif self.status == 1:
                    if c == "/":
                        print("C++ comment 333")
                        self.tokenid = "comment"
                        self.tokenstr += c
                        self.pos += 1
                        self.status = 0
                    elif c == "*":
                        #print("C comment")
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