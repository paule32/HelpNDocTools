import ply.lex as lex

# Pascal-Tokenliste
tokens = (
    'IDENTIFIER', 'NUMBER', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'ASSIGN',
    'LPAREN', 'RPAREN', 'SEMICOLON', 'COLON', 'COMMA', 'DOT',
    'BEGIN', 'END', 'VAR', 'PROGRAM', 'INTEGER', 'REAL'
)

# Reguläre Ausdrücke für einfache Token
t_PLUS     = r'\+'
t_MINUS    = r'-'
t_TIMES    = r'\*'
t_DIVIDE   = r'/'
t_ASSIGN   = r':='
t_LPAREN   = r'\('
t_RPAREN   = r'\)'
t_SEMICOLON = r';'
t_COLON    = r':'
t_COMMA    = r','
t_DOT      = r'\.'

# Pascal-Schlüsselwörter (Groß-/Kleinschreibung ignorieren)
reserved = {
    'begin': 'BEGIN',
    'end': 'END',
    'var': 'VAR',
    'program': 'PROGRAM',
    'integer': 'INTEGER',
    'real': 'REAL'
}

# Erkennung von Identifiern
def t_IDENTIFIER(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(), 'IDENTIFIER')  # Prüft, ob es ein Schlüsselwort ist
    return t
    
# Erkennung von Zahlen
def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

# Ignorierte Zeichen (Whitespace und Tabs)
t_ignore = ' \t\r'

# Fehlerbehandlung
def t_error(t):
    print(f"Ungültiges Zeichen '{t.value[0]}'")
    t.lexer.skip(1)

# Lexer erstellen
lexer = lex.lex()

# Beispiel für das Einlesen einer Datei
def lex_pascal_file(filename):
    with open(filename, 'r', encoding="utf-8") as file:
        data = file.read()
        lexer.input(data)
        for token in lexer:
            print(token)

# Beispielaufruf
lex_pascal_file("pascal.pas")
