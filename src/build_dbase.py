from __future__ import annotations
import argparse
import re
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"\[\:\:(?P<name>.+?)\:\:\]")

def safe_join(base_dir: Path, rel_path: str) -> Path:
    """
    Join base_dir + rel_path, normalisiere und verhindere Pfad-Ausbruch (.. nach oben).
    Erlaubt Unterordner, aber nur innerhalb von base_dir.
    """
    # Windows-Backslashes erlauben
    rel_path = rel_path.replace("\\", "/").strip()

    # Absolute Pfade blockieren (optional; kannst du erlauben, wenn du willst)
    p = Path(rel_path)
    if p.is_absolute():
        raise ValueError(f"Absolute Pfade sind nicht erlaubt im Platzhalter: {rel_path}")

    candidate = (base_dir / p).resolve()
    base_resolved = base_dir.resolve()

    # Prüfen, ob candidate innerhalb base_dir liegt
    try:
        candidate.relative_to(base_resolved)
    except ValueError:
        raise ValueError(f"Pfad-Ausbruch nicht erlaubt: {rel_path}")

    return candidate

def expand_placeholders(master_text: str, include_base: Path, fail_on_missing: bool) -> str:
    cache: dict[Path, str] = {}

    def repl(match: re.Match) -> str:
        raw_name = match.group("name").strip()
        include_path = safe_join(include_base, raw_name)

        if not include_path.exists():
            if fail_on_missing:
                raise FileNotFoundError(
                    f"Include-Datei nicht gefunden: {include_path} (Platzhalter: {match.group(0)})"
                )
            return match.group(0)  # Platzhalter stehen lassen

        if include_path not in cache:
            cache[include_path] = include_path.read_text(encoding="utf-8", errors="replace")
        return cache[include_path]

    return PLACEHOLDER_RE.sub(repl, master_text)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Ersetzt Platzhalter [::relativer/pfad::] in einer Masterdatei "
                    "durch Datei-Inhalte und schreibt eine neue Kinddatei."
    )
    ap.add_argument("master", type=Path, help="Pfad zur Masterdatei")
    ap.add_argument("output", type=Path, help="Pfad zur Kinddatei (Ausgabe)")
    ap.add_argument(
        "--include-dir",
        type=Path,
        default=None,
        help="Basisordner für Include-Dateien (Default: Ordner der Masterdatei)",
    )
    ap.add_argument(
        "--keep-missing",
        action="store_true",
        help="Fehlende Include-Dateien NICHT als Fehler behandeln (Platzhalter bleibt stehen)",
    )
    args = ap.parse_args()

    master_path: Path = args.master
    out_path: Path = args.output

    if not master_path.exists():
        raise FileNotFoundError(f"Masterdatei nicht gefunden: {master_path}")

    include_base = args.include_dir if args.include_dir is not None else master_path.parent
    include_base = include_base.resolve()

    master_text = master_path.read_text(encoding="utf-8", errors="replace")

    result = expand_placeholders(
        master_text=master_text,
        include_base=include_base,
        fail_on_missing=not args.keep_missing,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(result, encoding="utf-8")

    print(f"OK: Kinddatei erstellt -> {out_path}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
    