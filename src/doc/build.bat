python encodehelp.py -o help.po files files/css files/img files/js files/lib
python convert_toc.py

copy /y index.html .\files\index.html

python encodehelp.py -o help.po files files/css files/img files/js files/lib
python convert_toc.py

copy /y help.po      ..\__pycache__\_internal\locales\en_us\LC_HELP\help.po
copy /y help.mo      ..\__pycache__\_internal\locales\en_us\LC_HELP\help.mo
copy /y help.mo.zlib ..\__pycache__\_internal\locales\en_us\LC_HELP\help.mo.zlib
