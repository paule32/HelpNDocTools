class main(QObject):
    def __inir__(self):
        super().__init__()
        self.current_line = 10
        self.rinning = 0
        self.worker_thread = C64BasicWorkerThread()
        self.worker_thread.progress.connect(self.update_progress)
        self.worker_thread.start()
    def update_progress(value):
        if self.running == 2:
            return
        func = globals().get(f'line_{self.current_line}')
        if func:
            self.current_line = func()
        else:
            self.current_line = None
            if self.worker_thread.isRinning():
                self.worker_thread.terminate()
    def line_10():
        next_line = None
        console.win.print_line("HELLO WORLD")
        if next_line is None: next_line = 40
        return next_line
    def line_40():
        next_line = None
        console.win.print_line("ENDE")
        if next_line is None: next_line = 80
        return next_line
    def line_80():
        next_line = None
        genv.c64_parser.c64_exec_thread_stop()
        next_line = None
        return next_line
console = DOSConsole()
console.win.print_line('holla')
main_func = main()
console.exec_()