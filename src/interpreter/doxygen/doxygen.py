# ---------------------------------------------------------------------------
# File:   observer.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
from appcollection import *

# ---------------------------------------------------------------------------
# \brief  class for interpreting DoxyGen related stuff ...
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
class interpreter_DoxyGen:
    def __init__(self, filename):
        self.script_name = filename
        
        self.line_row    = 1
        self.line_col    = 1
        
        self.pos         = -1
        
        self.token_id    = ""
        self.token_prev  = ""
        self.token_str   = ""
        
        self.parse_data  = []
        
        self.parse_open(self.script_name)
        self.source = self.parse_data[0]
    
    def parse_open(self, file_name):
        with open(self.script_name, 'r', encoding="utf-8") as self.file:
            self.file.seek(0)
            lines  = len(self.file.readlines())
            self.file.seek(0)
            source = self.file.read()
            self.file.close()
        self.parse_data.append(source)
    
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
            elif c == '#':
                while True:
                    c = self.getChar()
                    if c == "\n":
                        self.line_col  = 1
                        self.line_row += 1
                        break
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
    
    def parse(self):
        with open(self.script_name, 'r', encoding="utf-8") as self.file:
            self.file.seek(0)
            self.total_lines = len(self.file.readlines())
            self.file.seek(0)
            self.source = self.file.read()
            self.file.close()
        
        if len(self.source) < 1:
            print("no data available.")
            return
        
        while True:
            c = self.skip_white_spaces()
            if c.isalpha():
                self.token_str = c
                self.getIdent()
                if not self.check_token():
                    break
    
    def check_token(self):
        return
    
    def __unexpectedToken(self):
        __msg = "unexpected token: '" + self.token_str + "'"
        __unexpectedError(__msg)
    
    def __unexpectedChar(self, chr):
        __msg = "unexpected character: '" + chr + "'"
        __unexpectedError(__msg)
    
    def __unexpectedEndOfLine(self):
        __unexpectedError("unexpected end of line")
    
    def __unexpectedEscapeSign(self):
        __unexpectedError("nunexpected escape sign")
    
    def __unexpectedError(self, message):
        calledFrom = inspect.stack()[1][3]
        msg = "\a\n" + message + " at line: '%d' in: '%s'.\n"
        msg = msg % (
            self.line_row,
            self.script_name)
        print(msg)
        sys.exit(1)

class doxygenDSL:
    def __init__(self):
        self.script = None
    
    def __new__(self, script_name):
        parser = interpreter_DoxyGen(script_name)
        try:
            parser.parse()
        except Exception as e:
            #parser.run()
            pass
        return self
    
    def parse(self):
        return
    
    def run(self):
        return
