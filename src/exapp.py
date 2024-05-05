# ---------------------------------------------------------------------------
# File:   exapp.py - login into the server user account ...
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
from appcollection import *

def handleExceptionApplication(func):
    global error_fail, error_result
    error_fail = False
    error_result = 0
    try:
        func()
    except ListInstructionError as ex:
        ex.add_note("Did you miss a parameter ?")
        ex.add_note("Add more information.")
        print("List instructions error.")
        error_result = 1
    except ZeroDivisionError as ex:
        ex.add_note("1/0 not allowed !")
        print("Handling run-time error:", ex)
        error_result = 1
    except OSError as ex:
        print("OS error:", ex)
        error_result = 1
    except ValueError as ex:
        print("Could not convert data:", ex)
        error_result = 1
    except Exception as ex:
        s = f"{ex.args}"
        parts = [part.strip() for part in s.split("'") if part.strip()]
        parts.pop( 0)   # delete first element
        parts.pop(-1)   # delete last  element
        
        err = "error: Exception occured: "
        if type(ex) == NameError:
            err += "NameError\n"
            err += "text: '" + parts[0]+"' not defined\n"
        elif type(ex) == AttributeError:
            err += "AttributeError\n"
            err += "class: " + parts[0]+"\n"
            err += "text : " + parts[2]+": "+parts[1]+"\n"
        else:
            err += "type  : " + "default  \n"
        
        error_ex = err
        
        error_result = 1
        error_fail   = True
        print(ex)
    finally:
        # ---------------------------------------------------------
        # when all is gone, stop the running script ...
        # ---------------------------------------------------------
        if error_result > 0:
            print("abort.")
            sys.exit(error_result)
        
        print("Done.")
        sys.exit(0)
