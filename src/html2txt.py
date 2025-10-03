import os
import re

INPUT_DIR = "html_files"
OUTPUT_DIR = os.path.join(INPUT_DIR, "escaped")

UMLAUT_MAP = {
    "ä": "&auml;",
    "ö": "&ouml;",
    "ü": "&uuml;",
    "Ä": "&Auml;",
    "Ö": "&Ouml;",
    "Ü": "&Uuml;",
    "ß": "&szlig;",
}

def normalize_whitespace(line: str) -> str:
    result = []
    in_single = False
    in_double = False
    buffer = ""
    for char in line:
        if char == "'" and not in_double:
            in_single = not in_single
            result.append(char)
        elif char == '"' and not in_single:
            in_double = not in_double
            result.append(char)
        elif in_single or in_double:
            if char == "\t":
                result.append(" " * 9)
            else:
                result.append(char)
        else:
            if char.isspace():
                buffer += char
            else:
                if buffer:
                    result.append(" ")
                    buffer = ""
                result.append(char)
    return "".join(result)

def convert_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r">\s+<", "><", line)
    line = re.sub(r"\s*=\s*", "=", line)
    line = normalize_whitespace(line)
    for char, entity in UMLAUT_MAP.items():
        line = line.replace(char, entity)
    line = line.replace('"', '\\"')
    line = line.replace("'", "\\'")
    return f"\"{line}\""

def process_files_recursive():
    for root, dirs, files in os.walk(INPUT_DIR):
        # Zielverzeichnis analog zum Input-Pfad erstellen
        rel_path = os.path.relpath(root, INPUT_DIR)
        out_dir = os.path.join(OUTPUT_DIR, rel_path)
        os.makedirs(out_dir, exist_ok=True)

        for filename in files:
            if filename.lower().endswith((".html", ".htm")):
                input_path = os.path.join(root, filename)
                output_path = os.path.join(out_dir, filename)

                with open(input_path, "r", encoding="utf-8") as infile, \
                     open(output_path, "w", encoding="utf-8") as outfile:
                    for line in infile:
                        if line.strip():
                            converted = convert_line(line)
                            outfile.write(converted + "\n")
                print(f"✔ {input_path} → {output_path}")

if __name__ == "__main__":
    process_files_recursive()
