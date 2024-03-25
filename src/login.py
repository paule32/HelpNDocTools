# ---------------------------------------------------------------------------
# File:   login.py - login into the server user account ...
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
try:
    from appcollection import *
    # ------------------------------------------------------------------------
    # external created data (packed, and base64 encoded) ...
    # ------------------------------------------------------------------------
    module_path = "./tools"
    sys.path.append(module_path)
    
    # ------------------------------------------------------------------------
    # global used application stuff ...
    # ------------------------------------------------------------------------
    __app__name        = "observer"
    __app__config_ini  = "observer.ini"
    
    __app__framework   = "PyQt5.QtWidgets.QApplication"
    __app__exec_name   = sys.executable
    
    # ------------------------------------------------------------------------
    # branding water marks ...
    # ------------------------------------------------------------------------
    __version__ = "Version 0.0.1"
    __authors__ = "paule32"
    
    __date__    = "2024-01-04"
    
    debugMode = True
    
    # ------------------------------------------------------------------------
    # when the user start the application script under Windows 7 and higher:
    # ------------------------------------------------------------------------
    try:
        from ctypes import windll  # Only exists on Windows.
        myappid = 'kallup-nonprofit.helpndoc.observer.1'
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except ImportError:
        pass
    
    # ------------------------------------------------------------------------
    # constants, and varibales that are used multiple times ...
    # ------------------------------------------------------------------------
    __copy__ = (""
        + "HelpNDoc.com FileWatcher 0.0.1\n"
        + "(c) 2024 by paule32\n"
        + "all rights reserved.\n")
    
    # ------------------------------------------------------------------------
    # global used locales constants ...
    # ------------------------------------------------------------------------
    __locale__    = "locales"
    __locale__enu = "en_us"
    __locale__deu = "de_de"
    
    basedir = os.path.dirname(__file__)
    
    # ------------------------------------------------------------------------
    # atexit: callback when sys.exit() is handled, and come back to console...
    # ------------------------------------------------------------------------
    def ApplicationAtExit():
        print("Thank's for using.")
        return
    
    # ------------------------------------------------------------------------
    # this is our "main" entry point, where the application will start.
    # ------------------------------------------------------------------------
    def EntryPoint():
        atexit.register(ApplicationAtExit)
        return
    if __name__ == '__main__':
        global error_fail, error_result
        global app
        
        handleExceptionApplication(EntryPoint)
        print("End")
        sys.exit(0)
        
except OSError:
    print("OS error:", err)
except ValueError:
    print("Could not convert data.")
except ImportError as ex:
    print("error: import module missing:", ex, ":", type(ex))
except Exception as ex:
    print(ex)
finally:
    if error_result > 0:
        print(error_ex)
        print("abort.")
    sys.exit(error_result)
# ----------------------------------------------------------------------------
# E O F  -  End - Of - File
# ----------------------------------------------------------------------------
