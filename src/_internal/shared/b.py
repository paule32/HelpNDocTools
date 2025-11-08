import subprocess
import sys

cmd = ["./dos.exe"]

try:
    result = subprocess.run(cmd)
    code = result.returncode
    print(f"Exit-Code (dec): {code}")
    print(f"Exit-Code (hex): 0x{code:02X}")
except FileNotFoundError:
    print("Error: Application not found")
    sys.exit(1)
 