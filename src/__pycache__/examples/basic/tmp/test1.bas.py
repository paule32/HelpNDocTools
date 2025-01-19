def line_10():
    next_line = None
    print('HELLO WORLD')
    if next_line is None: next_line = 40
    return next_line
def line_40():
    next_line = None
    print('ENDE')
    if next_line is None: next_line = 50
    return next_line
def line_50():
    next_line = None
    next_line = 10
    return next_line

current_line = 10  # Start des Programms
while current_line is not None:
    func = globals().get(f'line_{current_line}')
    if func:
        current_line = func()
    else:
        current_line = None