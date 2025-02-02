import ply.lex as lex
from paslex import lexer  # Importiere deinen Lexer

test_input = "var x, y: integer;"
lexer.input(test_input)

print("\n--- TOKEN LIST ---")
for tok in lexer:
    print(tok)
