import ply.yacc as yacc

# Token-Liste aus lex übernehmen
from paslex import tokens

# Regel für ein vollständiges Pascal-Programm
def p_program(p):
    '''program : PROGRAM IDENTIFIER SEMICOLON block DOT'''
    print("Ein gültiges Pascal-Programm erkannt.")

# Block mit Variablendeklaration und Anweisungen
def p_block(p):
    '''block : var_declaration BEGIN statement_list_or_empty END'''
    print("Block erkannt.")

# Variablendeklaration (optional)
def p_var_declaration(p):
    '''var_declaration : VAR var_list SEMICOLON
                       | empty'''
    print("Variablendeklaration erkannt.")

# Liste von Variablen
def p_var_list(p):
    '''var_list : IDENTIFIER COLON type
                | var_list COMMA IDENTIFIER COLON type'''
    if len(p) == 4:  # Einzelne Variable
        print(f"Variable erkannt: {p[1]} mit Typ {p[3]}")
    else:  # Mehrere Variablen
        print(f"Weitere Variable erkannt: {p[3]} mit Typ {p[5]}")
    
# Datentypen (z.B. Integer, Real)
def p_type(p):
    '''type : INTEGER
            | REAL'''
    p[0] = p[1]
    print("Datentyp:", p[1])

# Block ohne Anweisungen
def p_statement_list_or_empty(p):
    '''statement_list_or_empty : statement_list
                               | empty'''
    print("keine Zuweisung.")
    
# Liste von Anweisungen
def p_statement_list(p):
    '''statement_list : statement SEMICOLON
                      | statement_list statement SEMICOLON'''

# Einfache Anweisung (z.B. Zuweisung)
def p_statement(p):
    '''statement : IDENTIFIER ASSIGN expression'''
    print("Zuweisung erkannt:", p[1], "=", p[3])

# Ausdruck (z.B. arithmetische Operationen)
def p_expression(p):
    '''expression : expression PLUS term
                  | expression MINUS term
                  | term'''
    if len(p) == 4:
        print("Rechenoperation:", p[1], p[2], p[3])
        p[0] = eval(f"{p[1]} {p[2]} {p[3]}")
    else:
        p[0] = p[1]

# Term (Multiplikation, Division)
def p_term(p):
    '''term : term TIMES factor
            | term DIVIDE factor
            | factor'''
    if len(p) == 4:
        print("Multiplikation/Division:", p[1], p[2], p[3])
        p[0] = eval(f"{p[1]} {p[2]} {p[3]}")
    else:
        p[0] = p[1]

# Faktor (Zahl oder Klammerausdruck)
def p_factor(p):
    '''factor : NUMBER
              | LPAREN expression RPAREN'''
    if len(p) == 2:
        p[0] = p[1]
    else:
        p[0] = p[2]

# Leere Produktion (optional)
def p_empty(p):
    '''empty :'''
    pass

# Fehlerbehandlung
def p_error(p):
    if p:
        print(f"Syntaxfehler bei Token {p.value} (Zeile {p.lineno})")
    else:
        print("SYntaxfehler: Unbekanntes Token")

# Parser erstellen
parser = yacc.yacc()

# Beispiel für das Einlesen einer Datei und Parsen
def parse_pascal_file(filename):
    with open(filename, 'r', encoding="utf-8") as file:
        data = file.read()
        result = parser.parse(data)
        print("Parsing abgeschlossen.")

# Beispielaufruf
parse_pascal_file("pascal.pas")
