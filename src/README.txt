PETSCHII 4er-Paket (aus C64 chargen ROM)
=======================================

Dieses Paket erzeugt vier Sätze (jeweils 8x8, MSB links, $00–$FF):
  1) Upper/Graphics (normal)
  2) Upper/Graphics (inverse)
  3) Lower/Upper  (normal)
  4) Lower/Upper  (inverse)

Voraussetzungen:
  - Python 3
  - Pillow (pip install pillow)
  - C64 chargen ROM (4KB oder 8KB), z.B. 'chargen.901225-01.bin'

Benutzung:
  1) Lege das chargen-ROM in den selben Ordner.
  2) Ausführen:
       python make_all_sets.py <chargen.bin>
  3) Ergebnis: JSON + PNG für alle vier Sätze
