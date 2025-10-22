# code_editor.py
from PyQt5 import QtWidgets, QtCore, QtGui

class LineNumberArea(QtWidgets.QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.codeEditor = editor

    def sizeHint(self):
        return QtCore.QSize(self.codeEditor.lineNumberAreaWidth(), 0)

    def mousePressEvent(self, event):
        # Gutter-Klick → Breakpoint toggeln
        y = event.pos().y()
        self.codeEditor.toggleBreakpointAtY(y)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        self.codeEditor.lineNumberAreaPaintEvent(event)


class CodeEditor(QtWidgets.QPlainTextEdit):
    breakpointToggled = QtCore.pyqtSignal(int, bool)  # (line1based, active)

    def __init__(self, parent=None, editor_name=""):
        super().__init__(parent)
        self.editor_name = editor_name
        self._lineNumberArea = LineNumberArea(self)
        self.breakpoints = set()  # 1-basierte Zeilennummern

        # Signale
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)

        self.updateLineNumberAreaWidth(0)
        self.highlightCurrentLine()

        # Monospace fallback – dein C64-Pro wird später gesetzt
        mono = QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont)
        self.setFont(mono)

    # ---------- Gutter-Breite inkl. Marker-Spalte ----------
    def lineNumberAreaWidth(self):
        digits = len(str(max(1, self.blockCount())))
        charw  = self.fontMetrics().width('9')
        marker = 14  # Platz für roten Punkt
        padding = 8
        return marker + digits * charw + padding

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self._lineNumberArea.scroll(0, dy)
        else:
            self._lineNumberArea.update(0, rect.y(), self._lineNumberArea.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._lineNumberArea.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    # ---------- Marker + Nummern zeichnen ----------
    def lineNumberAreaPaintEvent(self, event):
        painter = QtGui.QPainter(self._lineNumberArea)
        painter.fillRect(event.rect(), self.palette().window().color().darker(102))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        lh = self.fontMetrics().height()

        # Marker-Spalte links
        marker_x = 3
        text_right = self._lineNumberArea.width() - 4

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                line1 = blockNumber + 1

                # roter Punkt, wenn Breakpoint
                if line1 in self.breakpoints:
                    r = QtCore.QRect(marker_x, top + (lh//2 - 4), 8, 8)
                    painter.setBrush(QtGui.QBrush(QtCore.Qt.red))
                    painter.setPen(QtCore.Qt.red)
                    painter.drawEllipse(r)
                else:
                    # dezenter leerer Kreis (optional)
                    pass

                # Zeilennummer
                painter.setPen(self.palette().text().color())
                painter.drawText(0, top, text_right, lh, QtCore.Qt.AlignRight, str(line1))

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    # ---------- aktuelle Zeile gelb ----------
    def highlightCurrentLine(self):
        if self.isReadOnly():
            self.setExtraSelections([])
            return
        sel = QtWidgets.QTextEdit.ExtraSelection()
        color = QtGui.QColor(QtCore.Qt.yellow).lighter(160)
        sel.format.setBackground(color)
        sel.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
        sel.cursor = self.textCursor()
        sel.cursor.clearSelection()
        self.setExtraSelections([sel])

    # ---------- Gutter-Klick-Helfer ----------
    def _lineFromY(self, y: int) -> int:
        # 1-basierte Zeilennummer am Gutter-Y ermitteln
        block = self.firstVisibleBlock()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        line = block.blockNumber() + 1
        while block.isValid() and top <= y:
            if y < bottom:
                return line
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            line += 1
        return max(1, min(line, self.blockCount()))

    def toggleBreakpointAtY(self, y: int):
        line1 = self._lineFromY(y)
        active = False
        if line1 in self.breakpoints:
            self.breakpoints.remove(line1)
            active = False
        else:
            self.breakpoints.add(line1)
            active = True
        self._lineNumberArea.update()
        self.breakpointToggled.emit(line1, active)
