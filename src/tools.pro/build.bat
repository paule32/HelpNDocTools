:: ----------------------------------------------------------------------
:: \file   zipfiles.py
:: \author (c) 2024 by Jens Kallup - paule32
:: \copy   all rights reserved.
::
:: \since  Version 0.0.1
::
:: \desc   This file is part of my application project "observer". This
::         is a Windows DOS-Batch file which can be execute in the CLI.
::         It was tested with Python 3.12.0
::
::         NO WARRANTIES - USE IT AT YOUR OWN RISK !!!
:: ----------------------------------------------------------------------
:: compile the stub, and add images to the temp.pyc ...
python -m compileall stub.py
copy __pycache__\stub.cpython-312.pyc .\stub.pyc
python zipfiles.py

:: to test the application...
python app.pyc
