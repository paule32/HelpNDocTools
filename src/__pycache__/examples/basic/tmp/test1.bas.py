class main(QObject):
    def __init__(self):
        super().__init__()
        self.current_line = 1
        self.running = 0
        self.xpos = 1
        self.ypos = 1
        self.console = DOSConsole()
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
    def line_10(self):
        self.current_line = None
        self.console.win.print_line("Hello World !!!1234")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 12
        return self.current_line
    def line_12(self):
        self.current_line = None
        self.console.win.print_line("xx 12")
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
        self.console.win.print_line("")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        if self.current_line is None: self.current_line = 40
        return self.current_line
    def line_40(self):
        self.current_line = None
        self.console.win.print_line("ssss")
        self.ypos += 1
        self.console.win.gotoxy(self.xpos, self.ypos)
        return self.current_line
main_func = main()
main_func.console.exec_()