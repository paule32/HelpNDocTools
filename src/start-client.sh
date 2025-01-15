#!/bin/bash
# ---------------------------------------------------------------------------
# File:   build.bat - Linux Batch file
# Author: Jens Kallup - paule32
#
# Rechte: (c) 2024, 2025 by kallup non-profit software
#         all rights reserved
#
# only for education, and for non-profit usage !!!
# commercial use is not allowed.
# ---------------------------------------------------------------------------

PYTHON=python3.13

$PYTHON -m compileall client-linux.py
cd ./__pycache__
$PYTHON client-linux.cpython-313.pyc --gui
cd ..
