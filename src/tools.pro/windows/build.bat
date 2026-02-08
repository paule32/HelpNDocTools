@echo on
rm -f win_errors_DEU_ALL.po
rm -f win_errors_ENG_ALL.po

python get_errors_deu.py
python get_errors_eng.py

T:\msys64\usr\bin\msgfmt.exe -o .\out\win_errors_DEU_ALL.mo win_errors_DEU_ALL.po
T:\msys64\usr\bin\msgfmt.exe -o .\out\win_errors_ENG_ALL.mo win_errors_ENG_ALL.po

T:\msys64\usr\bin\gzip.exe -9 -f .\out\win_errors_DEU_ALL.mo
T:\msys64\usr\bin\gzip.exe -9 -f .\out\win_errors_ENG_ALL.mo
