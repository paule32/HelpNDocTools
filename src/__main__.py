# ---------------------------------------------------------------------------
# File:   __main__.py
# Author: (c) 2024, 2025 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------

import sys
import client as starter

if __name__ == "__main__":
    # The Python 3+ or 3.12+ is required.
    major = sys.version_info[0]
    minor = sys.version_info[1]
    if (major < 3 and minor < 12):
        print("Python 3.12+ are required for the application")
        sys.exit(1)   
    sys.exit(starter.main(sys.args))
 