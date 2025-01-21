class main(QObject):
    def __init__(self):
        super().__init__()
        self.current_line = 10
        self.running = 0
        self.xpos = 1
        self.ypos = 1
        self.console = DOSConsole()
        self.console.win.print_line('holladiho')
        self.worker_thread = C64BasicWorkerThread()
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.start()
    def update_progress(self, value):
        while True:
            func_name = f'line_{self.current_line}'
            if hasattr(self, func_name):
                self.console.win.gotoxy(self.xpos, self.ypos)
                self.ypos += 1
                method = getattr(self, func_name)
                self.current_line = method()
                if not self.current_line == None:
                    self.current_line += 1
            else:
                showError(f"methode: {func_name} not found.")
                if self.worker_thread.isRunning():
                    self.worker_thread.terminate()
                break
    def line_10(self):
        next_line = None
        self.console.win.print_line("   HELLO WORLD")
        self.console.win.gotoxy(self.xpos, self.ypos)
        self.ypos += 1
        if next_line is None: next_line = 40
        return next_line
    def line_40(self):
        next_line = None
        self.console.win.print_line("ENDE")
        self.console.win.gotoxy(self.xpos, self.ypos)
        self.ypos += 1
        if next_line is None: next_line = 41
        return next_line
    def line_41(self):
        next_line = None
        self.console.win.print_line("OLA")
        self.console.win.gotoxy(self.xpos, self.ypos)
        self.ypos += 1
        return next_line
main_func = main()
main_func.console.exec_()