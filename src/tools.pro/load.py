import gzip
import marshal
import types

def execute_pyc_from_gzip(gzip_path):
    # Gzip-Datei öffnen und den Bytecode lesen
    with gzip.open(gzip_path, 'rb') as gz_file:
        # Überspringe den Header der PYC-Datei (Magic Number, Timestamp)
        gz_file.read(16)  # Magic number (4 bytes) + Timestamp (4 bytes) + Padding (8 bytes)
        # Lese den Bytecode
        bytecode = marshal.load(gz_file)

    # Erstelle ein neues Modul, in dem der Bytecode ausgeführt wird
    module = types.ModuleType("loaded_module")
    exec(bytecode, module.__dict__)
    return module

# Beispielaufruf:
# Der Pfad zur Gzip-Datei, die die PYC-Datei enthält
gzip_path = "start.gz"

loaded_module = execute_pyc_from_gzip(gzip_path)

# Falls das Modul eine Funktion `main()` hat, kannst du sie aufrufen:
if hasattr(loaded_module, "main"):
    loaded_module.main()
