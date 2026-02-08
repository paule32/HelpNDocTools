
# Qt5 Satzanalyse (Python, PyQt5)

## Installation
```bash
pip install PyQt5 matplotlib pandas
```

Wörterbuch-CSV "satz_de_woerterbuch.csv` in dieses Verzeichnis legen,
oder im der GUI über **Wörterbuch laden“** aus laden.
Optional "satz_analyse_config.json" daneben legen, um Regeln anzupassen.

## Start
```bash
python main.py
```

## Hinweise
- Farbliche Markierungen:
  - Rot: unbekannte Wörter
  - Orange: Groß-/Kleinschreibung (Heuristik)
  - Blau: feste Wendungen
  - Lila: Verb Heuristik
  - Magenta: doppelte Negation
  - Violett: Konjunktionsdopplung
  - Grau: Komma-Hinweis (nur in der Übersicht)
  - Grün: erkannte Flexionsformen (Verb/Nomen)
- Rechtsklick/Tooltip über markierten Bereichen zeigt eine Kurzinfo.
