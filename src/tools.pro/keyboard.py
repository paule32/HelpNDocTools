# \file keyboard.py
# \note (c) 2025 by Jens Kallup - paule32
#       all rights reserved.
#
# Was macht dieses Skript ?
#
# - os.path.relpath() wird genutzt, um den Teil relativ zum Startverzeichnis zu ermitteln.
# - Pfadtrenner werden in / umgewandelt (für XML sauber).
# - Ausgabe sieht so aus:
#   <RCC>
#     <file>_internal/img/unterordner1/bildname.jpg</file>
#     <file>_internal/img/unterordner2/weiterebilder/test.png</file>
#   </RCC>
import os
import re

def finde_bilder(verzeichnis, rekursiv=False, ausschluss_regex=None):
    """
    Sucht alle Bilder im Verzeichnis und schließt Dateien aus, die auf ein Regex-Muster passen.
    
    :param verzeichnis: Startverzeichnis
    :param rekursiv: True = Unterordner durchsuchen
    :param ausschluss_regex: Liste von Regex-Mustern für den Ausschluss
    """
    bild_endungen = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    bilder_liste = []

    if ausschluss_regex is None:
        ausschluss_regex = []

    if rekursiv:
        for wurzel, _, dateien in os.walk(verzeichnis):
            for datei in dateien:
                ext = os.path.splitext(datei)[1].lower()
                if ext in bild_endungen and not any(re.search(muster, datei) for muster in ausschluss_regex):
                    bilder_liste.append(os.path.join(wurzel, datei))
    else:
        for datei in os.listdir(verzeichnis):
            ext = os.path.splitext(datei)[1].lower()
            if ext in bild_endungen and not any(re.search(muster, datei) for muster in ausschluss_regex):
                bilder_liste.append(os.path.join(verzeichnis, datei))
    
    return bilder_liste

def erstelle_qrc_datei(bilder_liste, basis_verzeichnis, ausgabe_datei="resources.qrc"):
    with open(ausgabe_datei, "w", encoding="utf-8") as f:
        f.write("<RCC>\n")
        f.write('    <qresource prefix="/images">\n')
        
        for bild in bilder_liste:
            relativer_pfad = os.path.relpath(bild, basis_verzeichnis)
            relativer_pfad = relativer_pfad.replace(os.sep, '/')
            f.write(f'        <file>_internal/img/{relativer_pfad}</file>\n')
        
        f.write("    </qresource>\n")
        f.write("</RCC>\n")
    print(f".qrc-Datei erstellt: {ausgabe_datei}")

if __name__ == "__main__":
    pfad = "../img"  # Verzeichnis anpassen
    
    # Regex-Ausschluss:
    ausschluss = [
        r"^screen0.*\.png$",    # alle PNGs, die mit 'logo' anfangen
        r"test\d+\.jpg",        # alle 'test' + Zahl + .jpg
        r"windesk.png",
        r"windesk2.png",
        r"squid.png",
        r"pascal.png",
        r"login.png",
        r"linux001.png",
        r"electro.png",
        r"desktop.pbg",
        r"desktop002.png",
        r"dbase.png",
        r"basic.png"
    ]
    
    bilder = finde_bilder(pfad, rekursiv=True, ausschluss_regex=ausschluss)
    
    print(f"Gefundene Bilder (nach Ausschluss): {len(bilder)}")
    erstelle_qrc_datei(bilder, pfad, "resources.qrc")
