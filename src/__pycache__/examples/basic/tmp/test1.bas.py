class main(QObject):
    def __init__(self):
        super().__init__()
        self.current_line = 1
        self.running = 0
        self.xpos = 1
        self.ypos = 1
        self.console = C64Console(None)
        self.console.win.print_line('holladiho')
        self.worker_thread = C64BasicWorkerThread()
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.start()
    def update_progress(self,value):
        while True:
            func_name = f'line_{self.current_line}'
            if hasattr(self,func_name):
                self.console.win.gotoxy(self.xpos,self.ypos)
                method = getattr(self,func_name)
                self.current_line = method()
                if not self.current_line == None:
                    continue
                else:
                    break
            else:
                self.current_line += 1
    def line_5(self):
        self.current_line = None
        self.console.win.print_line("1234567890123456789012345678901234567890")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 10
        return self.current_line
    def line_10(self):
        self.current_line = None
        self.console.win.print_line("2Hello World !!!1234")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 12
        return self.current_line
    def line_12(self):
        self.current_line = None
        self.console.win.print_line("3xx 12")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 20
        return self.current_line
    def line_20(self):
        self.current_line = None
        self.console.win.print_line("DEF")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 30
        return self.current_line
    def line_30(self):
        self.current_line = None
        self.console.win.print_line("5")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 40
        return self.current_line
    def line_40(self):
        self.current_line = None
        self.console.win.print_line("6 ssss")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 41
        return self.current_line
    def line_41(self):
        self.current_line = None
        self.console.win.print_line("7")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 42
        return self.current_line
    def line_42(self):
        self.current_line = None
        self.console.win.print_line("8")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 43
        return self.current_line
    def line_43(self):
        self.current_line = None
        self.console.win.print_line("9")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 44
        return self.current_line
    def line_44(self):
        self.current_line = None
        self.console.win.print_line("10")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 45
        return self.current_line
    def line_45(self):
        self.current_line = None
        self.console.win.print_line("11")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 46
        return self.current_line
    def line_46(self):
        self.current_line = None
        self.console.win.print_line("12")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 47
        return self.current_line
    def line_47(self):
        self.current_line = None
        self.console.win.print_line("13")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 48
        return self.current_line
    def line_48(self):
        self.current_line = None
        self.console.win.print_line("14")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 49
        return self.current_line
    def line_49(self):
        self.current_line = None
        self.console.win.print_line("15")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 50
        return self.current_line
    def line_50(self):
        self.current_line = None
        self.console.win.print_line("16")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 51
        return self.current_line
    def line_51(self):
        self.current_line = None
        self.console.win.print_line("17")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 52
        return self.current_line
    def line_52(self):
        self.current_line = None
        self.console.win.print_line("18")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 53
        return self.current_line
    def line_53(self):
        self.current_line = None
        self.console.win.print_line("19")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 54
        return self.current_line
    def line_54(self):
        self.current_line = None
        self.console.win.print_line("20")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 55
        return self.current_line
    def line_55(self):
        self.current_line = None
        self.console.win.print_line("21")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 56
        return self.current_line
    def line_56(self):
        self.current_line = None
        self.console.win.print_line("22")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 57
        return self.current_line
    def line_57(self):
        self.current_line = None
        self.console.win.print_line("23")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 58
        return self.current_line
    def line_58(self):
        self.current_line = None
        self.console.win.print_line("24")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 59
        return self.current_line
    def line_59(self):
        self.current_line = None
        self.console.win.print_line("25")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        return self.current_line
main_func = main()
main_func.console.exec_()