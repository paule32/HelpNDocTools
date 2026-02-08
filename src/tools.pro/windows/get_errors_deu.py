#!/usr/bin/env python3
"""
Generate a text file of ALL Windows System Error Codes in the format:

msgid "<number>"
msgstr "<ERROR_MACRO>\n"
"<escaped English description>"

Rules:
- Escape double quotes (") as \"
- Escape single quotes (') as \'
- Replace real line breaks in the description with \n
- Wrap the description in double quotes
"""

import re
import sys
import time
import requests
import subprocess
from bs4 import BeautifulSoup

INDEX_URL = "https://learn.microsoft.com/de-de/windows/win32/debug/system-error-codes"

def print_header():
    content  = ("msgid \"\"\n")
    content += ("msgstr \"\"\n")
    content += ("\"Project-Id-Version: 1.0.0\\n\"\n")
    content += ("\"POT-Creation-Date: 2024-04-06 20:33+0100\\n\"\n")
    content += ("\"PO-Revision-Date: 2024-04-06 20:15+0100\\n\"\n")
    content += ("\"Last-Translator: Jens Kallup <paule32.jk@gmail.com>\\n\"\n")
    content += ("\"Language-Team: German <paule32.jk@gmail.com>\\n\"\n")
    content += ("\"MIME-Version: 1.0\\n\"\n")
    content += ("\"Content-Type: text/plain; charset=utf-8\\n\"\n")
    content += ("\"Content-Transfer-Encoding: 8bit\\n\"\n")
    content += ("\n")
    return content

def get_range_urls(session: requests.Session):
    resp = session.get(INDEX_URL, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        if "system-error-codes--" in href:
            if not href.startswith("http"):
                if href.startswith("/"):
                    href = "https://learn.microsoft.com" + href
                else:
                    href = "https://learn.microsoft.com/de-de/windows/win32/debug/" + href
            links.append(href)
    seen = set()
    ordered = []
    for u in links:
        if u not in seen:
            ordered.append(u)
            seen.add(u)
    if not ordered:
        raise RuntimeError("No range URLs found on index page; the page structure might have changed.")
    return ordered

RE_HEADING = re.compile(r"^[A-Z0-9_]+$")
RE_NUMLINE = re.compile(r"^(\d+)\s*\(0x[0-9A-Fa-f]+\)\s*$")

def parse_range_page(session: requests.Session, url: str):
    resp = session.get(url, timeout=60)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    lines = []
    for el in soup.find_all(["h1","h2","h3","h4","h5","p","li","pre"]):
        t = el.get_text("\n", strip=True)
        if t:
            for part in t.split("\n"):
                s = part.strip()
                if s:
                    lines.append(s)

    results = []
    i = 0
    while i < len(lines):
        name = lines[i]
        if not RE_HEADING.match(name):
            i += 1
            continue
        if i + 1 >= len(lines):
            break
        numline = lines[i+1]
        m = RE_NUMLINE.match(numline)
        if not m:
            i += 1
            continue
        code_num = m.group(1)

        j = i + 2
        desc_parts = []
        while j < len(lines):
            if RE_HEADING.match(lines[j]) and (j + 1 < len(lines)) and RE_NUMLINE.match(lines[j+1]):
                break
            desc_parts.append(lines[j])
            j += 1
        english = "\n".join(desc_parts).strip()
        results.append((code_num, name, english))
        i = j
    if not results:
        raise RuntimeError(f"No entries parsed from {url}. The page layout may have changed.")
    return results

def escape_text(text: str) -> str:
    text = text.replace("\\", "\\\\")  # Backslash escapen
    text = text.replace('"', '\\"')    # Doppelte Anführungszeichen escapen
    text = text.replace("\n", "\\n")   # Zeilenumbrüche zu \n
    return text

def main(output_path: str):
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WinErrorScraper/1.0"
    })
    urls = get_range_urls(session)

    def url_key(u: str):
        m = re.search(r"--(\d+)-(\d+)-", u)
        return int(m.group(1)) if m else 0
    urls = sorted(urls, key=url_key)

    total = 0
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(print_header())
        for url in urls:
            print(f"Fetching {url} ...", file=sys.stderr)
            entries = parse_range_page(session, url)
            for code_num, macro, english in entries:
                english_escaped = escape_text(english)
                f.write(f'msgid "{code_num}"\n')
                f.write(f'msgstr "{macro}"\n')
                f.write(f'"{english_escaped}"\n\n')
                total += 1
            time.sleep(0.6)
    print(f"Done. Wrote {total} entries to {output_path}", file=sys.stderr)

if __name__ == "__main__":
    out = "win_errors_DEU_ALL.po" if len(sys.argv) < 2 else sys.argv[1]
    main(out)
