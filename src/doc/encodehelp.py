# ----------------------------------------------------------------------------------
# \file   encodehelp.py
# \author Jens Kallup - paule32
# \note   (c) 2025 all rights reserved.
#
# \desc
# Erstellt aus HTML- und CSS-Dateien Base64-Texte und schreibt sie als Paare
# msgid/msgstr in eine Ausgabedatei. Erkennt MIME-Typ, um Text/Binär zu markieren.
#
# Format pro Eintrag:
#     # TYPE: TEXT
#     msgid "<dateiname>"
#     msgstr "<base64>"
#
# Nutzung:
#     python encode.py -o output.txt pfad1 [pfad2 ...]
#
# ----------------------------------------------------------------------------------
import argparse
import base64
import mimetypes
import subprocess
import zlib

from pathlib  import Path
from typing   import Iterable
from datetime import datetime

ALLOWED_EXTS = {".html", ".htm", ".css", ".js", ".gif", ".png", ".jpg", ".jpeg"}
index = []

def iter_input_files(paths: Iterable[str]) -> list[Path]:
    files: set[Path] = set()
    for p in map(Path, paths):
        if p.is_dir():
            # Rekursiv alle Dateien im Verzeichnis prüfen
            for f in p.rglob("*"):
                if f.is_file() and f.suffix.lower() in ALLOWED_EXTS:
                    files.add(f.resolve())  # Voller Pfad
        elif p.is_file() and p.suffix.lower() in ALLOWED_EXTS:
            files.add(p.resolve())
    return sorted(files)
    
def build_file_list(paths: Iterable[str]):
    files = iter_input_files(paths)
    # Liste: [voller Pfad, Dateiname, MIME-Typ]
    file_list = [[str(f), f.name, detect_mime(f)] for f in files]
    return file_list

def compress_and_base64(data: bytes) -> tuple[str, int]:
    compressed = zlib.compress(data, level=9)
    return base64.b64encode(compressed).decode("ascii"), len(compressed)

def detect_type(file_path: Path) -> str:
    txt_ext = [".js", ".css", ".htm", ".html"]
    bin_ext = [".png", ".gif", ".jpg", ".jpeg"]
    if str(file_path).endswith(tuple(txt_ext)):
        return "TEXT"
    mime_type, _ = mimetypes.guess_type(file_path.as_posix())
    if mime_type and mime_type.startswith("text/"):
        return "TEXT"
    if str(file_path).endswith(tuple(bin_ext)):
        return "BINARY"
    return "UNKNOWN"

def write_header(out) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M%z")
    header = (
        f'msgid ""\n'
        f'msgstr ""\n'
        f'"Project-Id-Version: 1.0.0\\n"\n'
        f'"POT-Creation-Date: {now}\\n"\n'
        f'"PO-Revision-Date: {now}\\n"\n'
        f'"Last-Translator: Jens Kallup <paule32.jk@gmail.com>\\n"\n'
        f'"Language-Team: German <paule32.jk@gmail.com>\\n"\n'
        f'"MIME-Version: 1.0\\n"\n'
        f'"Content-Type: text/plain; charset=utf-8\\n"\n'
        f'"Content-Transfer-Encoding: 8bit\\n"\n\n'
    )
    out.write(header)
    
    # PO-Katalog Index
    out.write(f'# TYPE: INDEX\n')
    out.write(f'msgid "index"\n')
    out.write(f'msgstr "{str(index)}"\n\n')

def write_catalog(files: list[Path], out_path: Path, base_path: Path) -> None:
    total_original = total_compressed = total_base64 = 0
    
    # file_stats enthält jetzt den **vollen Pfad**:
    file_stats = []
    for f in files:
        raw_data = f.read_bytes()
        orig_size = len(raw_data)
        compressed_data = zlib.compress(raw_data, level=9)
        compressed_size = len(compressed_data)
        b64_data = base64.b64encode(compressed_data).decode("ascii")
        base64_size = len(b64_data.encode("ascii"))
        file_stats.append((f, f.name, orig_size, compressed_size, base64_size, b64_data))
        
        total_original += orig_size
        total_compressed += compressed_size
        total_base64 += base64_size
    
    max_name_len = max(len(name) for _, name, *_ in file_stats)
    # file_stats: (full_path, name, orig_size, compressed_size, base64_size, b64_data)
    all_numbers = [orig_size       for _, _,       orig_size      , _, _, _ in file_stats] + \
                  [compressed_size for _, _, _,    compressed_size, _,    _ in file_stats] + \
                  [base64_size     for _, _, _, _, base64_size    ,       _ in file_stats] + \
                  [total_original, total_compressed, total_base64]
    max_number_len = max(len(f"{n:,}".replace(",", ".")) for n in all_numbers)
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="\n") as out:
        write_header(out)
        
        for full_path, name, orig_size, compressed_size, base64_size, b64_data in file_stats:
            file_type = detect_type(full_path)
            rel_path = full_path.relative_to(base_path).as_posix()
            
            # Zahlen mit Punkt-Trennzeichen
            orig_str = f"{orig_size:,}".replace(",", ".")
            comp_str = f"{compressed_size:,}".replace(",", ".")
            b64_str = f"{base64_size:,}".replace(",", ".")
            
            # Tabellarische Ausgabe
            print(
                f"[INFO] {name.ljust(max_name_len)} | "
                f"Orig:   {orig_str.rjust(max_number_len)} B | "
                f"Kompr.: {comp_str.rjust(max_number_len)} B | "
                f"Base64: {b64_str.rjust(max_number_len)} B"
            )
            
            # PO-Katalog schreiben
            out.write(f'# TYPE: {file_type}\n')
            out.write(f'msgid "{rel_path}|{file_type}"\n')
            out.write(f'msgstr "{b64_data}"\n\n')
    
        # Gesamt-Benchmark
        total_orig_str = f"{total_original:,}".replace(",", ".")
        total_comp_str = f"{total_compressed:,}".replace(",", ".")
        total_b64_str  = f"{total_base64:,}".replace(",", ".")
        
        print("\n===== BENCHMARK GESAMT =====")
        print(f"Original:    {total_orig_str.rjust(max_number_len)} Bytes")
        print(f"Komprimiert: {total_comp_str.rjust(max_number_len)} Bytes")
        print(f"Base64:      {total_b64_str.rjust(max_number_len)} Bytes")
        print(f"Ersparnis:   {(1 - total_compressed / total_original) * 100:.2f}% (nach Kompression)")
        print("=============================\n")


def compile_po_to_mo(po_file: Path, mo_file: Path) -> None:
    """
    Ruft msgfmt.exe auf, um eine .po-Datei in eine .mo-Datei zu übersetzen.
    """
    if not po_file.exists():
        raise FileNotFoundError(f"PO-Datei nicht gefunden: {po_file}")
    
    # msgfmt.exe aufrufen
    cmd = ["msgfmt.exe", str(po_file), "-o", str(mo_file)]
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"[INFO] Erfolgreich kompiliert: {po_file} -> {mo_file}")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] msgfmt fehlgeschlagen:\n{e.stderr}")
        raise

def compress_catalog_file(input_path: str, output_path: str) -> None:
    """
    Liest eine Textdatei (Katalog), komprimiert sie mit zlib
    und schreibt die komprimierte Version als Binärdatei.
    """
    # Datei einlesen
    data = Path(input_path).read_bytes()
    
    # zlib-Kompression (maximale Stufe)
    compressed = zlib.compress(data, level=9)
    
    # Komprimierte Datei schreiben
    Path(output_path).write_bytes(compressed)
    print(f"[INFO] Katalog erfolgreich komprimiert: {output_path} ({len(compressed)} Bytes)")

def build_relative_file_list(paths: Iterable[str], base_path: Path = None):
    """
    Erstellt eine Liste: [relativer Pfad, Dateiname]
    base_path: Basis für relative Pfade, Standard: aktuelles Verzeichnis
    """
    if base_path is None:
        base_path = Path.cwd()
    
    files = iter_input_files(paths)
    rel_list = []
    for f in files:
        try:
            rel_path = f.relative_to(base_path).as_posix()  # '/' als Trenner
        except ValueError:
            # Wenn Datei nicht unter base_path liegt, vollen Pfad nehmen
            rel_path = f.as_posix()
        rel_list.append([rel_path])
    return rel_list

# ----------------------------------------------------------------------------------
# Prüft, ob die angegebene Ausgabedatei auf '.po' endet.
# Falls nicht, wird '.po' angehängt.
# ----------------------------------------------------------------------------------
def ensure_po_suffix(output_file: str) -> Path:
    out_path = Path(output_file)
    if out_path.suffix != ".po":
        out_path = out_path.with_suffix(out_path.suffix + ".po") \
        if out_path.suffix else out_path.with_suffix(".po")
    return out_path

def main():
    ap = argparse.ArgumentParser(description="HTML/CSS komprimieren & Base64-Katalog mit Benchmark")
    ap.add_argument("paths", nargs="+", help="Dateien oder Ordner.")
    ap.add_argument("-o", "--output", required=True, help="Ausgabedatei.")
    args = ap.parse_args()
    
    # alle Dateien in einen Verzeichnis:
    relative_list = build_relative_file_list(args.paths)
    for entry in relative_list:
        index.append(entry)

    files = iter_input_files(args.paths)
    base_path = Path(args.paths[0]).resolve()
    if not files:
        raise SystemExit("Keine passenden Dateien (.html/.htm/.css) gefunden.")
    
    # Katalog schreiben:
    write_catalog(files, Path(args.output), base_path)
    
    # Katalog von .po nach .mo
    po_file = Path(Path(args.output))
    mo_file = po_file.with_suffix(".mo")
    compile_po_to_mo(po_file, mo_file)
    
    # Nach write_catalog abgeschlossen
    compress_catalog_file(str(mo_file), str(mo_file)+".zlib")

if __name__ == "__main__":
    main()
