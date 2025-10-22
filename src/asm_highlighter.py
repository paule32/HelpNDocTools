# asm_highlighter.py
from PyQt5 import QtGui, QtCore

class AsmHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent_document: QtGui.QTextDocument):
        super().__init__(parent_document)

        # ----- Farben & Formate -----
        self.fmt_comment = QtGui.QTextCharFormat()
        self.fmt_comment.setForeground(QtGui.QColor(0, 170, 0))  # dunkelgrün

        self.fmt_mnemonic = QtGui.QTextCharFormat()
        self.fmt_mnemonic.setForeground(QtGui.QColor(0, 90, 200))  # blau
        self.fmt_mnemonic.setFontWeight(QtGui.QFont.Bold)

        self.fmt_number = QtGui.QTextCharFormat()
        self.fmt_number.setForeground(QtGui.QColor(200, 120, 0))  # orange

        self.fmt_label_def = QtGui.QTextCharFormat()
        self.fmt_label_def.setForeground(QtGui.QColor(80, 140, 255))  # helles Blau

        self.fmt_label_ref = QtGui.QTextCharFormat()
        self.fmt_label_ref.setForeground(QtGui.QColor(80, 140, 255))  # gleich wie def.

        # ----- Regexe (QRegularExpression) -----
        # 1) Kommentar: ab erstem ';' bis Zeilenende
        self.rx_comment = QtCore.QRegularExpression(r";.*$",
            QtCore.QRegularExpression.CaseInsensitiveOption |
            QtCore.QRegularExpression.MultilineOption)

        # 2) Label-Definition am Zeilenanfang:   label:
        self.rx_label_def = QtCore.QRegularExpression(
            r"^(?P<lbl>[A-Za-z_]\w*)\s*:",
            QtCore.QRegularExpression.MultilineOption
        )

        # 3) Mnemonic: nach optionalem Label + Leerraum am Zeilenanfang
        #    .BYTE/.WORD etc. ODER 2–4 Buchstaben (LDA, JSR, BEQ, NOP, …)
        self.rx_mnemonic = QtCore.QRegularExpression(
            r"^(?:[A-Za-z_]\w*\s*:)?\s*(?P<m>\.[A-Za-z]+|[A-Za-z]{2,4})\b",
            QtCore.QRegularExpression.CaseInsensitiveOption |
            QtCore.QRegularExpression.MultilineOption
        )

        # 4) Zahlen/Adressen: $HH.., %.., #$.., #10, nackte Dezimalzahlen
        self.rx_numbers = [
            QtCore.QRegularExpression(r"#\s*\$[0-9A-Fa-f]+"),      # #$0F
            QtCore.QRegularExpression(r"#\s*\d+"),                 # #10
            QtCore.QRegularExpression(r"\$[0-9A-Fa-f]+"),          # $C000
            QtCore.QRegularExpression(r"%[01]+"),                  # %1010
            QtCore.QRegularExpression(r"\b\d+\b"),                 # 1234
            QtCore.QRegularExpression(r"'[^']'"),                  # 'A'
        ]

        # 5) Label-Referenzen in Operanden (ein Wort, das nicht Zahl/Prefix ist)
        #    Achtung: sehr simpel gehalten; gute Trefferquote in typischem 6502-ASM
        self.rx_label_ref = QtCore.QRegularExpression(
            r"\b(?!A\b)(?!X\b)(?!Y\b)(?![0-9]+\b)(?!\$[0-9A-Fa-f]+)(?!%[01]+)"
            r"[A-Za-z_]\w+\b"
        )

    def highlightBlock(self, text: str):
        # Reihenfolge: erst Label-Def, Mnemonic, Zahlen/Label-Ref, zuletzt Kommentar (überdeckt alles dahinter)
        # Label-Def
        it = self.rx_label_def.globalMatch(text)
        while it.hasNext():
            m = it.next()
            self.setFormat(m.capturedStart("lbl"), m.capturedLength("lbl"), self.fmt_label_def)

        # Mnemonic
        m = self.rx_mnemonic.match(text)
        if m.hasMatch():
            start = m.capturedStart("m")
            length = m.capturedLength("m")
            self.setFormat(start, length, self.fmt_mnemonic)

        # Zahlen/Adressen
        for rx in self.rx_numbers:
            it = rx.globalMatch(text)
            while it.hasNext():
                mm = it.next()
                self.setFormat(mm.capturedStart(), mm.capturedLength(), self.fmt_number)

        # Label-Referenzen (einfach; Kommentar wird danach drüber gemalt)
        it = self.rx_label_ref.globalMatch(text)
        while it.hasNext():
            mm = it.next()
            self.setFormat(mm.capturedStart(), mm.capturedLength(), self.fmt_label_ref)

        # Kommentar (zum Schluss, damit er „dominiert“)
        it = self.rx_comment.globalMatch(text)
        while it.hasNext():
            mm = it.next()
            self.setFormat(mm.capturedStart(), mm.capturedLength(), self.fmt_comment)
