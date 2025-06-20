# ---------------------------------------------------------------------------
# File:   status.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
# tool for write windows last error csv
# ---------------------------------------------------------------------------
import sys
import os
import csv
import subprocess

def print_header():
    content  = ("msgid \"\"\n")
    content += ("msgstr \"\"\n")
    content += ("\"Project-Id-Version: 1.0.0\\n\"\n")
    content += ("\"POT-Creation-Date: 2024-04-06 20:33+0100\\n\"\n")
    content += ("\"PO-Revision-Date: 2024-04-06 20:15+0100\\n\"\n")
    content += ("\"Last-Translator: Jens Kallup <paule32@gmail.com>\\n\"\n")
    content += ("\"Language-Team: German <paule32@gmail.com>\\n\"\n")
    content += ("\"MIME-Version: 1.0\\n\"\n")
    content += ("\"Content-Type: text/plain; charset=utf-8\\n\"\n")
    content += ("\"Content-Transfer-Encoding: 8bit\\n\"\n")
    content += ("\n")
    return content

line = 1
try:
    if os.path.exists("./out/WinLastError.po"):
        os.remove("./out/WinLastError.po")
    #
    content = print_header()
    with open("./data/WinLastError.db", newline='', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            content += ("msgid \""  + row["code"] + "\"\n")
            content += ("msgstr \"" + row["text"] + "\"\n")
            content += ("\n")
            line += 1
        csv_file.close()
        with open("./out/WinLastError.po", "w", encoding="utf-8") as file:
            file.write(content)
            file.close()
            
    result = subprocess.run([
        "msgfmt.exe",
        "-o",
        "./out/WinLastError.mo",
        "./out/WinLastError.po"], check = True)
    #
    result = subprocess.run([
        "gzip.exe", "-9",
        "./out/WinLastError.mo"], check = True)
        
except PermissionError as e:
    print("file permission error.")
    sys.exit(1)
except subprocess.CalledProcessError as e:
    print("msgfmt.exe could not be start.")
    sys.exit(1)
except FileNotFoundError as e:
    print("file error could not found.")
    sys.exit(1)
except Exception as e:
    print("error at line: " + str(line))
    sys.exit(1)

line = 1
try:
    if os.path.exists("./out/WinLastStatus.po"):
        os.remove("./out/WinLastStatus.po")
    #
    content = print_header()
    with open("./data/WinLastStatus.db", newline='', encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            content += ("msgid \""  + row["code"] + "\"\n")
            content += ("msgstr \"" + row["text"] + "\"\n")
            content += ("\n")
        csv_file.close()
        with open("./out/WinLastStatus.po", "w", encoding="utf-8") as file:
            file.write(content)
            file.close()
    
    result = subprocess.run([
        "msgfmt",
        "-o",
        "./out/WinLastStatus.mo",
        "./out/WinLastStatus.po"], check = True)
    #
    result = subprocess.run([
        "gzip.exe", "-9",
        "./out/WinLastStatus.mo"], check = True)
        
except PermissionError as e:
    print("file permission error.")
    sys.exit(1)
except subprocess.CalledProcessError as e:
    print("msgfmt.exe could not be start.")
    sys.exit(1)
except FileNotFoundError as e:
    print("status file could not found.")
    sys.exit()
except Exception as e:
    print("status error at line: " + str(line))
    print(e)
    sys.exit(1)
