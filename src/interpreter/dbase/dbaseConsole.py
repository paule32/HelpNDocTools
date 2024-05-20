# ---------------------------------------------------------------------------
# File:   dbaseConsole.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
import sys           # system specifies
import time          # thread count
import datetime      # date, and time routines

from  colorama import init, Fore, Back, Style  # ANSI escape

class consoleApp():
    def __init__(self):
        init(autoreset = True)
        sys.stdout.write(Fore.RESET + Back.RESET + Style.RESET_ALL)
        return
    
    def cls(self):
        sys.stdout.write("\033[H\033[2J")
        sys.stdout.flush()
        return
    
    def gotoxy(self, xpos, ypos):
        sys.stdout.write("\033["
        + str(ypos) + ";"
        + str(xpos) + "H")
        sys.stdout.flush()
        return
    
    def print(self, data):
        sys.stdout.write(data)
        sys.stdout.flush()
        return
    
    def print_date(self):
        dat = datetime.datetime.now()
        sys.stdout.write(dat.strftime("%Y-%m-%d"))
        sys.stdout.flush()
