# Fügt ein Standard-Modul mit deinem VBA-Code ein und speichert als .docm.
# Voraussetzungen:
# Windows
# Microsoft Word
# pip install pywin32
#
# In Word: Datei -> Optionen -> Sicherheitscenter -> Einstellungen
# -> Makroeinstellungen -> "Zugriff auf das VBA-Projektmodell vertrauen"
#    aktivieren (sonst COM error).
import sys
import pathlib
import win32com.client as win32
from pywintypes import com_error

# Konfiguration
DOCX_PATH = r"Dokument.docx"     # Eingabe (docx)
DOCM_PATH = r"Dokument.docm"     # Ausgabe (docm)
VBA_CODE_FILE = r"Code.bas"      # Textdatei mit VBA-Code (oder .txt)

# Word-Konstanten
wdFormatXMLDocumentMacroEnabled = 13   # .docm
vbext_ct_StdModule = 1                 # Standard-Modul

def read_text(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return f.read()

def main():
    vba_code = read_text(VBA_CODE_FILE)

    word = win32.gencache.EnsureDispatch("Word.Application")
    word.Visible = False

    try:
        # 1) DOCX öffnen und als DOCM speichern
        doc = word.Documents.Open(DOCX_PATH)
        doc.SaveAs(DOCM_PATH, FileFormat=wdFormatXMLDocumentMacroEnabled)

        # 2) Modul anlegen + Code einfügen
        try:
            vbproj = doc.VBProject  # erfordert "Zugriff auf das VBA-Projektmodell vertrauen"
        except com_error as e:
            raise RuntimeError(
                "Kein Zugriff auf VBProject. In Word: "
                "Datei > Optionen > Sicherheitscenter > Einstellungen > "
                "Makroeinstellungen > 'Zugriff auf das VBA-Projektmodell vertrauen' aktivieren."
            ) from e

        vbcomp = vbproj.VBComponents.Add(vbext_ct_StdModule)
        vbcomp.Name = "InjectedMacros"
        vbcomp.CodeModule.AddFromString(vba_code)

        # 3) Speichern
        doc.Save()
        print(f"Fertig. Makros in: {DOCM_PATH}")

    finally:
        # sauber schließen
        try:
            doc.Close(SaveChanges=False)
        except Exception:
            pass
        word.Quit()

if __name__ == "__main__":
    main()
