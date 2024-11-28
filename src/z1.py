from TObject      import *
from TApplication import *
#from TMenuBar     import *
#from TStatusBar   import *

if __name__ == "__main__":
    app = TApplication()
    #bar_menu   = TMenuBar(app)
    #bar_status = TStatusBar(app)
    try:
        print(f"ExeName: {app.ExeName}")
        app.run()
    finally:
        print("finally: app.free")
        #bar_menu  .Free()
        #bar_status.Free()
        app       .Free()
    

#    o1   = TObject()
#    test = TObject(o1)

#    test.test()
#    test.Free()
