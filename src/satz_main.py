
import sys, os, re, json, io
from datetime import datetime
from typing import List, Tuple, Dict
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore, QtPrintSupport
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import satz_main_analyse_de_v5 as analyzer

DEFAULT_CSV = os.path.join(HERE, "satz_de_woerterbuch.csv")

COLORS = {
    "unknown": "#d32f2f",
    "casing": "#f57c00",
    "fixed_phrase": "#1976d2",
    "verb_position": "#7b1fa2",
    "double_negation": "#c2185b",
    "conjunction_repeat": "#512da8",
    "conjunction_repeat_spaced": "#9575cd",
    "comma_hint": "#455a64",
    "recognized": "#2e7d32",
}

class IssueChart(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(4, 2.6), dpi=100)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.fig.tight_layout()

    def update_counts(self, counts: dict):
        self.ax.clear()
        if not counts:
            self.ax.set_title("Keine Issues")
            self.draw()
            return
        keys = list(counts.keys())
        vals = [counts[k] for k in keys]
        self.ax.bar(keys, vals)
        self.ax.set_ylabel("Anzahl")
        self.ax.set_xticklabels(keys, rotation=30, ha="right")
        self.ax.set_title("Issue-Übersicht")
        self.fig.tight_layout()
        self.draw()

    def save_png(self, path: str):
        self.fig.savefig(path, dpi=144, bbox_inches="tight")

def tokenize_positions(text: str):
    return [(m.group(0), m.start(), m.end()) for m in re.finditer(r"[A-Za-zÄÖÜäöüß\-]+", text)]

def html_escape(s: str) -> str:
    return (s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
              .replace('"',"&quot;").replace("'","&#39;"))

def build_ranges(text: str, step1, step2, step3, step4, step5):
    positions = tokenize_positions(text)
    ranges = []  # (start, end, color, tooltip, cls)
    # Unknowns
    for uw in step1.get("unknown", []):
        key = uw.lower()
        for (tok, s, e) in positions:
            if tok.lower() == key:
                ranges.append((s, e, COLORS["unknown"], f"Unbekannt: {uw}", "unknown"))
    # Casing
    for cw in step1.get("casing_warnings", []):
        tok = cw.get("token","")
        for (t, s, e) in positions:
            if t == tok:
                ranges.append((s, e, COLORS["casing"], f"Casing: {tok} → {cw.get('suggest')}", "casing"))
    # Step2 issues
    for issue in step2.get("issues", []):
        if issue.get("type") == "verb_position":
            if len(positions) >= 2:
                s, e = positions[1][1], positions[1][2]
                ranges.append((s, e, COLORS["verb_position"], "Verb-2-Heuristik: prüfen", "verb_position"))
        elif issue.get("type") == "casing":
            ranges.append((0, 1, COLORS["casing"], "Satzanfang groß", "casing"))
        elif issue.get("type") == "fixed_phrase":
            for m in re.finditer(r"\bnach hause\b", text, flags=re.IGNORECASE):
                ranges.append((m.start(), m.end(), COLORS["fixed_phrase"], "Feste Wendung: nach Hause", "fixed_phrase"))
    # Step3 fixed phrases
    for iss in step3.get("issues", []):
        span = iss.get("span","")
        if span:
            for m in re.finditer(re.escape(span), text, flags=re.IGNORECASE):
                ranges.append((m.start(), m.end(), COLORS["fixed_phrase"], f"Feste Wendung: {iss.get('suggest')}", "fixed_phrase"))
    # Step4
    for iss in step4.get("issues", []):
        t = iss.get("type")
        if t in ("conjunction_repeat","conjunction_repeat_spaced"):
            for m in re.finditer(r"\b(und|oder)\b", text, flags=re.IGNORECASE):
                ranges.append((m.start(), m.end(), COLORS[t], "Mögliche Konjunktionsdopplung", t))
                break
        elif t == "double_negation":
            span = iss.get("span","")
            if span:
                for m in re.finditer(re.escape(span), text, flags=re.IGNORECASE):
                    ranges.append((m.start(), m.end(), COLORS["double_negation"], "Mögliche doppelte Negation", "double_negation"))
    # Step5 recognized
    for rec in step5.get("recognized", []):
        tok = rec.get("token",""); base = rec.get("base","")
        for (t, s, e) in positions:
            if t == tok:
                ranges.append((s, e, COLORS["recognized"], f"{rec.get('class')}: Basis {base}", "recognized"))
    ranges.sort(key=lambda x: (x[0], x[1]))
    return ranges

def ranges_to_html(text: str, ranges):
    out = []
    last = 0
    for (s, e, color, tip, cls) in ranges:
        if s > last:
            out.append(html_escape(text[last:s]))
        seg = html_escape(text[s:e])
        out.append('<span class="%s" title="%s" style="background:%s22; border-bottom:2px solid %s;">%s</span>' % (
            cls, html_escape(tip), color, color, seg
        ))
        last = e
    if last < len(text):
        out.append(html_escape(text[last:]))
    return "".join(out)

def full_html_document(content_body: str, title: str, chart_path: str = None) -> str:
    chart_html = ""
    if chart_path and os.path.exists(chart_path):
        chart_html = '<h3>Übersicht</h3><p><img src="%s" alt="Chart" /></p>' % os.path.basename(chart_path)
    css = (
        "body{font-family:Segoe UI, Helvetica, Arial, sans-serif; padding:20px; color:#222}"
        "h1,h2,h3{color:#333}"
        ".meta{color:#666; font-size:12px}"
        "pre{white-space:pre-wrap}"
        ".block{margin-bottom:28px; padding:12px; border:1px solid #eee; border-radius:8px; background:#fafafa}"
    )
    head = "<!doctype html><html><head><meta charset='utf-8'><title>%s</title><style>%s</style></head><body>" % (html_escape(title), css)
    head += "<h1>%s</h1><div class='meta'>Erzeugt am %s</div>%s" % (html_escape(title), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), chart_html)
    return head + content_body + "</body></html>"

class IssueChartStandalone(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(6, 3), dpi=120)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)

    def make_chart(self, counts: dict, path: str):
        self.ax.clear()
        if counts:
            keys = list(counts.keys())
            vals = [counts[k] for k in keys]
            self.ax.bar(keys, vals)
            self.ax.set_ylabel("Anzahl")
            self.ax.set_xticklabels(keys, rotation=30, ha="right")
            self.ax.set_title("Issue-Übersicht")
        else:
            self.ax.set_title("Keine Issues")
        self.fig.tight_layout()
        self.fig.savefig(path, dpi=144, bbox_inches="tight")

class IssueChart(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(4, 2.6), dpi=100)
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111)
        self.fig.tight_layout()

    def update_counts(self, counts: dict):
        self.ax.clear()
        if not counts:
            self.ax.set_title("Keine Issues")
            self.draw()
            return
        keys = list(counts.keys())
        vals = [counts[k] for k in keys]
        self.ax.bar(keys, vals)
        self.ax.set_ylabel("Anzahl")
        self.ax.set_xticklabels(keys, rotation=30, ha="right")
        self.ax.set_title("Issue-Übersicht")
        self.fig.tight_layout()
        self.draw()

    def save_png(self, path: str):
        self.fig.savefig(path, dpi=144, bbox_inches="tight")

class Highlighter:
    def __init__(self, text_edit: QtWidgets.QTextEdit):
        self.text_edit = text_edit

    def highlight_ranges(self, ranges):
        doc = self.text_edit.document()
        cursor = QtGui.QTextCursor(doc)
        for start, end, color_hex, tooltip, cls in ranges:
            cursor.setPosition(start)
            cursor.setPosition(end, QtGui.QTextCursor.KeepAnchor)
            fmt = QtGui.QTextCharFormat()
            color = QtGui.QColor(color_hex)
            fmt.setBackground(QtGui.QBrush(color.lighter(160)))
            fmt.setToolTip(tooltip)
            cursor.mergeCharFormat(fmt)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Deutsche Satzanalyse (Qt5)")
        self.resize(1200, 750)

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        # Widgets
        self.inputEdit = QtWidgets.QPlainTextEdit()
        self.inputEdit.setPlaceholderText("Gib hier deinen Text ein…")
        self.outputEdit = QtWidgets.QTextEdit()
        self.outputEdit.setReadOnly(True)

        self.btnAnalyze = QtWidgets.QPushButton("Analysieren")
        self.btnLoadCSV = QtWidgets.QPushButton("Wörterbuch laden…")
        self.btnExportHtml = QtWidgets.QPushButton("Export HTML…")
        self.btnExportPdf = QtWidgets.QPushButton("Export PDF…")
        self.btnBatch = QtWidgets.QPushButton("Batch-Analyse (CSV)…")

        self.lblCSV = QtWidgets.QLabel(f"Wörterbuch: {DEFAULT_CSV if os.path.exists(DEFAULT_CSV) else '— bitte wählen —'}")

        self.chart = IssueChart()

        # Layouts
        left = QtWidgets.QVBoxLayout()
        left.addWidget(QtWidgets.QLabel("Eingabetext"))
        left.addWidget(self.inputEdit, 2)
        left_buttons = QtWidgets.QHBoxLayout()
        left_buttons.addWidget(self.btnAnalyze)
        left_buttons.addWidget(self.btnLoadCSV)
        left.addLayout(left_buttons)
        left2 = QtWidgets.QHBoxLayout()
        left2.addWidget(self.btnExportHtml)
        left2.addWidget(self.btnExportPdf)
        left.addLayout(left2)
        left.addWidget(self.btnBatch)
        left.addWidget(self.lblCSV)

        right = QtWidgets.QVBoxLayout()
        right.addWidget(QtWidgets.QLabel("Analyse & Hervorhebungen"))
        right.addWidget(self.outputEdit, 3)
        right.addWidget(QtWidgets.QLabel("Diagramm"))
        right.addWidget(self.chart, 2)

        lay = QtWidgets.QHBoxLayout(central)
        lay.addLayout(left, 1)
        lay.addLayout(right, 1)

        # State
        self.csv_path = DEFAULT_CSV if os.path.exists(DEFAULT_CSV) else None
        self.vocab = None
        if self.csv_path:
            try:
                df = pd.read_csv(self.csv_path)
                self.vocab = analyzer.build_vocab(df)
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Warnung", f"Konnte CSV nicht laden:\n{e}")
        self.last_ranges = []
        self.last_counts = {}
        self.last_text = ""

        # Signals
        self.btnAnalyze.clicked.connect(self.analyze)
        self.btnLoadCSV.clicked.connect(self.pick_csv)
        self.btnExportHtml.clicked.connect(self.export_html_current)
        self.btnExportPdf.clicked.connect(self.export_pdf_current)
        self.btnBatch.clicked.connect(self.batch_analyze_csv)

    def pick_csv(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Wörterbuch CSV wählen", "", "CSV (*.csv)")
        if path:
            try:
                df = pd.read_csv(path)
                self.vocab = analyzer.build_vocab(df)
                self.csv_path = path
                self.lblCSV.setText(f"Wörterbuch: {path}")
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Fehler", f"CSV konnte nicht geladen werden:\n{e}")

    def analyze(self):
        text = self.inputEdit.toPlainText()
        if not text.strip():
            self.outputEdit.setPlainText("Bitte Text eingeben.")
            return
        if self.vocab is None:
            self.outputEdit.setPlainText("Kein Wörterbuch geladen. Bitte CSV wählen.")
            return

        step1 = analyzer.analyze_sentence_step1(text, self.vocab)
        step2 = analyzer.analyze_sentence_step2(text)
        step3 = analyzer.analyze_sentence_step3_fixed(text)
        step4 = analyzer.analyze_sentence_step4_syntax(text)
        step5 = analyzer.analyze_sentence_step5_flex(text, self.vocab)

        self.outputEdit.clear()
        self.outputEdit.setPlainText(text)

        ranges = build_ranges(text, step1, step2, step3, step4, step5)
        Highlighter(self.outputEdit).highlight_ranges(ranges)

        # counts for chart
        counts = {}
        counts["unknown"] = len(step1.get("unknown", []))
        counts["casing"] = len(step1.get("casing_warnings", []))
        for iss in step3.get("issues", []):
            counts["fixed"] = counts.get("fixed",0) + 1
        for iss in step4.get("issues", []):
            counts[iss["type"]] = counts.get(iss["type"], 0) + 1
        counts["recognized"] = len(step5.get("recognized", []))
        self.chart.update_counts(counts)

        # store for export
        self.last_ranges = ranges
        self.last_counts = counts
        self.last_text = text

    def export_html_current(self):
        if not self.last_text:
            QtWidgets.QMessageBox.information(self, "Hinweis", "Bitte zuerst analysieren.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "HTML exportieren", "analyse.html", "HTML (*.html)")
        if not path:
            return
        chart_png = os.path.splitext(path)[0] + "_chart.png"
        self.chart.save_png(chart_png)
        body = '<div class="block"><pre>%s</pre></div>' % (ranges_to_html(self.last_text, self.last_ranges))
        html = full_html_document(body, "Analyse – Einzeltext", chart_png)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        QtWidgets.QMessageBox.information(self, "Export", f"HTML gespeichert:\n{path}")

    def export_pdf_current(self):
        if not self.last_text:
            QtWidgets.QMessageBox.information(self, "Hinweis", "Bitte zuerst analysieren.")
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "PDF exportieren", "analyse.pdf", "PDF (*.pdf)")
        if not path:
            return
        chart_png = os.path.splitext(path)[0] + "_chart.png"
        self.chart.save_png(chart_png)
        body = '<div class="block"><pre>%s</pre></div>' % (ranges_to_html(self.last_text, self.last_ranges))
        html = full_html_document(body, "Analyse – Einzeltext", chart_png)

        doc = QtGui.QTextDocument()
        doc.setHtml(html)
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.HighResolution)
        printer.setOutputFormat(QtPrintSupport.QPrinter.PdfFormat)
        printer.setOutputFileName(path)
        doc.print_(printer)
        QtWidgets.QMessageBox.information(self, "Export", f"PDF gespeichert:\n{path}")

    def batch_analyze_csv(self):
        if self.vocab is None:
            QtWidgets.QMessageBox.information(self, "Hinweis", "Bitte zuerst Wörterbuch laden.")
            return
        csv_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Batch-CSV wählen", "", "CSV (*.csv)")
        if not csv_path:
            return
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Fehler", f"CSV konnte nicht geladen werden:\n{e}")
            return
        if "text" not in df.columns:
            QtWidgets.QMessageBox.critical(self, "Fehler", "Spalte 'text' nicht gefunden.")
            return

        sections = []
        overall_counts = {}
        for idx, row in df.iterrows():
            text = str(row["text"]) if not pd.isna(row["text"]) else ""
            if not text.strip():
                continue
            step1 = analyzer.analyze_sentence_step1(text, self.vocab)
            step2 = analyzer.analyze_sentence_step2(text)
            step3 = analyzer.analyze_sentence_step3_fixed(text)
            step4 = analyzer.analyze_sentence_step4_syntax(text)
            step5 = analyzer.analyze_sentence_step5_flex(text, self.vocab)
            ranges = build_ranges(text, step1, step2, step3, step4, step5)

            c = {"unknown": len(step1.get("unknown", [])),
                 "casing": len(step1.get("casing_warnings", [])),
                 "recognized": len(step5.get("recognized", []))}
            for iss in step3.get("issues", []):
                c["fixed"] = c.get("fixed",0) + 1
                overall_counts["fixed"] = overall_counts.get("fixed",0) + 1
            for iss in step4.get("issues", []):
                t = iss["type"]
                c[t] = c.get(t,0) + 1
                overall_counts[t] = overall_counts.get(t,0) + 1
            overall_counts["unknown"] = overall_counts.get("unknown",0) + c["unknown"]
            overall_counts["casing"] = overall_counts.get("casing",0) + c["casing"]
            overall_counts["recognized"] = overall_counts.get("recognized",0) + c["recognized"]

            body_html = ranges_to_html(text, ranges)
            sections.append('<div class="block"><h3>#%d</h3><pre>%s</pre></div>' % (idx+1, body_html))

        save_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Batch-Report speichern (HTML)", "batch_report.html", "HTML (*.html)")
        if not save_path:
            return
        chart_png = os.path.splitext(save_path)[0] + "_chart.png"
        IssueChartStandalone().make_chart(overall_counts, chart_png)
        doc_html = full_html_document("".join(sections), "Batch-Analyse", chart_png)
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(doc_html)
        QtWidgets.QMessageBox.information(self, "Batch", "HTML-Report gespeichert:\n%s\n\nTipp: Zum PDF-Export HTML im Browser drucken oder den Einzel-PDF-Export nutzen." % save_path)

def main():
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
