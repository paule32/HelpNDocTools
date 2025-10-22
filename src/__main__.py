# ---------------------------------------------------------------------------
# File:   __main__.py
# Author: (c) 2024, 2025 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------

import sys
import os
import client as starter

os.environ.setdefault(
    "QTWEBENGINE_CHROMIUM_FLAGS",
    "--disable-gpu --disable-software-rasterizer"
)
if __name__ == "__main__":
    # The Python 3+ or 3.12+ is required.
    print("Hallo Python from __main__")
    major = sys.version_info[0]
    minor = sys.version_info[1]
    if (major < 3 and minor < 12):
        print("Python 3.12+ are required for the application")
        sys.exit(1)   
    starter.main()
    sys.exit(0)
 