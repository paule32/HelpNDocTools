import os
import sys
import configparser

file_path = "pro.pro"
db_pro = "dBaseProject"

v__app__config =  configparser.ConfigParser()
v__app__config.read(file_path)

try:
    with open(file_path, "r", encoding="utf-8") as configfile:
        v__app__config.read(configfile)
        configfile.close()
except Exception as e:
    print("Error: " + e)
    sys.exit(1)

try:
    print("oooooo")
    forms    = v__app__config[db_pro]["Forms"     ]
    print("000000")
    print(forms)
    reports  = v__app__config[db_pro]["Reports"   ]
    programs = v__app__config[db_pro]["Programs"  ]
    tables   = v__app__config[db_pro]["DeskTables"]
    images   = v__app__config[db_pro]["Images"    ]
    sql      = v__app__config[db_pro]["SQL"       ]
    other    = v__app__config[db_pro]["Other"     ]
except Exception as e:
    print(e)
