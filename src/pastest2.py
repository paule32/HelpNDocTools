import ply.yacc as yacc
    
from paslex  import tokens
from pasyacc import parser  # Importiere deinen Parser

test_input = "PROGRAM test; var xy: integer; BEGIN END."

print("\n--- PARSER TEST ---")
result = parser.parse(test_input)
print("Parsing abgeschlossen.")
