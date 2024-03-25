# ---------------------------------------------------------------------------
# File:   pascal.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
# interpreter for a pascal subset language:
# ---------------------------------------------------------------------------
from appcollection import *
class pascal:
    # -----------------------------------------
    # symbols for the tokenizer ...
    # -----------------------------------------
    class TSymbol:
        def __init(self):
            self.sUnknown      = [  0, ''           ]
            self.sIdent        = [  1, ''           ]
            self.sInteger      = [  2, ''           ]
            self.sPlus         = [  3, '+'          ]
            self.sMinus        = [  4, '-'          ]
            self.sStar         = [  5, '*'          ]
            self.sSlash        = [  6, '/'          ]
            self.sEqual        = [  7, '='          ]
            self.sSmaller      = [  8, '<'          ]
            self.sBigger       = [  9, '>'          ]
            self.sBiggerEqual  = [ 10, '>='         ]
            self.sSmallerEqual = [ 11, '<='         ]
            self.sUnEqual      = [ 12, '#'          ]
            self.sOpenBracket  = [ 13, '('          ]
            self.sCloseBracket = [ 14, ')'          ]
            self.sComma        = [ 15, ','          ]
            self.sDot          = [ 16, '.'          ]
            self.sSemiColon    = [ 17, ';'          ]
            self.sBecomes      = [ 18, ':='         ]
            self.sVar          = [ 19, 'VAR'        ]
            self.sConst        = [ 20, 'CONST'      ]
            self.sProcedure    = [ 21, 'PROCEDURE'  ]
            self.sBegin        = [ 22, 'BEGIN'      ]
            self.sEnd          = [ 23, 'END'        ]
            self.sIf           = [ 24, 'IF'         ]
            self.sThen         = [ 25, 'THEN'       ]
            self.sElseIf       = [ 26, 'ELSEIF'     ]
            self.sElse         = [ 27, 'ELSE'       ]
            self.sWhile        = [ 28, 'WHILE'      ]
            self.sDo           = [ 29, 'DO'         ]
            self.sModule       = [ 30, 'MODULE'     ]
            self.sWrite        = [ 31, 'WRITE'      ]
            self.sNone         = [ 32, ''           ]
            return
    
    # -----------------------------------------
    # define the set of available op-codes ...
    # -----------------------------------------
    class OpCode:
        def __init__(self):
            #
            self.current = 0
            #
            self.OpCode_ILL = 0
            self.OpCode_LIT = 1
            self.OpCode_LOD = 2
            self.OpCode_STO = 3
            self.OpCode_CAL = 4
            self.OpCode_NUM = 5
            self.OpCode_JMP = 6
            self.OpCode_JPC = 7
            self.OpCode_WRI = 8
            self.OpCode_OPR = 9
            #
            self.ill = [ self.OpCode_ILL, ""    ]  # illegal
            self.lit = [ self.OpCode_LIT, "lit" ]  # literal
            self.lod = [ self.OpCode_LOD, "lod" ]  # load
            self.sto = [ self.OpCode_STO, "sto" ]  # store
            self.cal = [ self.OpCode_CAL, "cal" ]  # call
            self.num = [ self.OpCode_NUM, "num" ]  # integer / number
            self.jmp = [ self.OpCode_JMP, "jmp" ]  # jump
            self.jpc = [ self.OpCode_JPC, "jpc" ] 
            self.wri = [ self.OpCode_WRI, "wri" ]  # write
            self.opr = [ self.OpCode_OPR, "opr" ]
            return
        # -----------------------------------------
        # get the current op code ...
        # -----------------------------------------
        def getCurrent(self):
            return self.current
    
    class IdentConstant:
        def __init__(self):
            self.value = 0
            return
    
    class IdentVariable:
        def __init__(self):
            self.lebel = 0
            self.addr  = 0
            self.size  = 0
            self.value = 0
            return
    
    class IdentProcedure:
        def __init__(self):
            self.level = 0
            self.addr  = 0
            self.size  = 0
            self.value = 0
            return
    
    class IdentType:
        def __init__(self):
            self.itConstant  = self.IdentConstant ()
            self.itVariable  = self.IdentVariable ()
            self.itProcedure = self.IdentProcedure()
            return
        def IdentConstant(self):
            return
        def IdentVariable(self):
            return
        def IdentProcedure(self):
            return
    
    class Ident:
        def __init__(self):
            self.name = ""
            self.kind = pascal.IdentType()
            return
    
    class IdentList:
        def __init__(self):
            self.items = pascal.Ident()
            return
        def __del__(self):
            print("dtor: IdentList, clean-up...")
            return
    
    # -----------------------------------------
    # represents a item of a "instruction" ...
    # -----------------------------------------
    class InstructionItem:
        def __init__(self):
            self.opcode = pascal.OpCode()
            self.lhs = 0
            self.rhs = 0  # a
            return
    
    # -----------------------------------------
    # hold the "instructions" ...
    # -----------------------------------------
    class InstructionsClass:
        # -------------------------------------
        # ctor - constructor
        # -------------------------------------
        def __init__(self):
            if debugMode == True:
                print("ctor: InstructionsClass")
            self.items = []
            return
        # -------------------------------------
        # dtor - destructor
        # -------------------------------------
        def __del__(self):
            if debugMode == True:
                print("dtor: InstructionsClass, clean-up...")
            self.items.clear()
            return
        # -------------------------------------
        # add instruction item to the item list
        # -------------------------------------
        def add(self, inst = None):
            if inst == None:
                raise ListInstructionError
            if not type(inst) == pascal.InstructionItem:
                raise ListMustBeInstructionError
            print("==>", inst.opcode.current)
            self.items.append(inst)
            return
        # -------------------------------------
        # delete nth instruction from item list
        # -------------------------------------
        def delete(self, inst = -1):
            if inst < 0:
                raise ListIndexOutOfBounds
            if inst > -1:
                if inst != len(self.items):
                    raise ListIndexOutOfBounds
                else:
                    self.items,pop(inst)
            return
    
    # -----------------------------------------
    # constructor for: interpreter_Pascal
    # -----------------------------------------
    def __init__(self):
        #
        self.IdentConstant  = 1
        self.IdentVariable  = 2
        self.IdentProcedure = 3
        #
        self.identList    = self.IdentList()
        self.instructions = self.InstructionsClass()
        
        self.stacksize = 1024
        
        self.p = -1
        self.b = 1
        self.t = 0
        self.s = [0, 0, 0]
        
        self.eof = False
        
        self.file_name = "test.byte"
        self.file_stat = os.stat(self.file_name)
        self.file_size = self.file_stat.st_size
        
        with open(self.file_name, 'r') as file:
            for line in file:
                cols = line.strip().split(' ')
                inst = self.InstructionItem()
                inst.opcode.current = cols[0]
                inst.lhs = cols[1]
                inst.rhs = cols[2]
                print("--->")
                self.instructions.add(inst)
            file.close()
        
        # -------------------------------------------------
        # convert the string values in the cols to integer
        # -------------------------------------------------
        for row in self.instructions.items:
            row[0] = row[0].split()
            row[0][0:] = [int(value) for value in row[0][0:]] # string to int
            #row[0][0] = self.OpCodeText[ row[0][0] ]
            print(">", row[0])
        return
    
    def Base(self, i, b, s):
        b1 = b
        if i == 0:
            self.eof = True
            return None
        while i > 0:
            b1 = s[b1]
            i  = i - 1
        return b1
    
    def Emulate(self):
        print("Interpreting Code:")
        self.ModuleCommand()
        t = 0
        b = 1
        p = 0
        s = [0, 0, 0]
        print("Start...")
        while True:
            if p >= len(self.instructions.items):
                break
            if self.eof == True:
                break
            i = self.instructions.items[p]
            i = i[0]
            p = p + 1
            z = i[0]
            if z == self.OpCode_LIT:
                print(self.OpCodeText[z])
                t = t + 1
                s[t] = i[2]
            elif z == self.OpCode_LOD:
                print(self.OpCodeText[z])
                t = t + 1
                r = self.Base(i[1], b, s)
                if not r == None:
                    s[t] = s[r + i[2]]
                else:
                    break
            elif z == self.OpCode_STO:
                r = self.Base(i[1], b, s)
                if not r == None:
                    s[r + i[2]] = s[t]
                else:
                    break
                t = t - 1
            elif z == self.OpCode_CAL:
                r = self.Base(i[1], b, s)
                if not r == None:
                    s[t + 1] = r
                    s[t + 2] = b
                    s[t + 3] = p
                    b = t + 1
                    p = i[2]
                else:
                    break
            elif z == self.OpCode_INT:
                t = t + i[2]
            elif z == self.OpCode_JMP:
                p = i[2]
            elif z == self.OpCode_JPC:
                if s[t] == 0:
                    p = i[2]
                t = t - 1
            elif z == self.OpCode_WRI:
                print("wri: ", int(s[t]))
                t = t - 1
            elif z == self.OpCode_OPR:
                z = i[2]
                if z == 0:
                    t = b - 1
                    p = s[t + 3]
                    b = s[t + 2]
                if z == 1:
                    s[t] = 0 - s[t]
                if z == 2:
                    t = t - 1
                    s[t] = s[t] + s[t + 1]
                if z == 3:
                    t = t - 1
                    s[t] = s[t] - s[t + 1]
                if z == 4:
                    t = t - 1
                    s[t] = s[t] * s[t + 1]
                if z == 5:
                    t = t - 1
                    s[t] = s[t] // s[t + 1]
                if z == 8:
                    t = t - 1
                    if s[t] == s[t + 1]:
                        s[t] = True
                    else:
                        s[t] = False
                if z == 9:
                    t = t - 1
                    if s[t] != s[t + 1]:
                        s[t] = True
                    else:
                        s[t] = False
                if z == 10:
                    t = t - 1
                    if s[t] < s[t + 1]:
                        s[t] = True
                    else:
                        s[t] = False
                if z == 11:
                    t = t - 1
                    if s[t] > s[t + 1]:
                        s[t] = True
                    else:
                        s[t] = False
                if z == 12:
                    self.t = self.t - 1
                    if s[t] >= s[t + 1]:
                        s[t] = True
                    else:
                        s[t] = False
                if z == 13:
                    t = t - 1
                    if s[t] <= s[t + 1]:
                        s[t] = True
                    else:
                        s[t] = False
                else:
                    print("Unknown Operand")
                    break
            else:
                print("Unknown opcode")
                break
        print("Done...")
        return
    
    def ShowInstructions(self):
        print("Instructions:")
        for row in self.instructions.items:
            print(row)
        self.GenCode(3, 1, 5)
    
    def Expect(self, Expected):
        if Symbol != Expected:
            ErrorExpected([Expected], Symbol)
        return
    
    def GenCode(self, f, l, a):
        acode = [f, l, a]
        self.instructions.add(acode)
        return
    
    def ModuleCommand(self):
        print("oo-oo")
        return
        def Position(self, ID, TablePosition):
            print("1")
            return
        def StatementSequence(self, TablePosition, level):
            print("2")
            return
            def Statement(self):
                print("21")
                return
                def Expression(self):
                    print("212")
                    return
                    def Term(self):
                        print("2121")
                        return
                        def Factor(self):
                            print("21231")
                            return
                def Condition(self):
                    print("322")
                    return
        def Declarations(self, TablePosition, level):
            print("3")
            return
            def Enter(self, typ):
                TablePosition = TablePosition + 1
                return
            def ProcedureDecl(self):
                print("32")
                return
            def ConstDecl(self):
                print("33")
                return
            def VarDecl(self):
                print("34")
                return
# ----------------------------------------------------------------------------
# E O F  -  End - Of - File
# ----------------------------------------------------------------------------
