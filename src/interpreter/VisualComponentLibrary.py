# ---------------------------------------------------------------------------
# File:   dbase.py
# Author: (c) 2024 Jens Kallup - paule32
# All rights reserved
# ---------------------------------------------------------------------------
class TMenu:
    struct = [];
    def __init__(self,parent):
        print(parent);
        return
    def add(self, menu_list):
        self.struct.append(menu_list)
        return
    def show(self, make_visible=True):
        if make_visible:
            print(self.struct);
        return

# ---------------------------------------------------------------------------
# \brief this class provides accessible menubar for the application on the
#        top upper part line.
# ---------------------------------------------------------------------------
class TMenuBar(TMenu):
    def __init__(self,parent):
        super().__init__(parent)
        font_name  = "Arial"
        font_size  = 10
        
        font_color = "white"
        back_color = "navy"
        back_str   = "background-color"
        
        str_font   = "fint"
        str_size   = "size"
        str_color  = "color"
        
        self.standardMenuBar = {
        "File": [{
            "subitem": [{
                "New" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color }
                ],
                "Open" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color }
                ],
                "Save" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color }
                ],
                "Save As" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color }
                ],
                "Print" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color }
                ],
                "Exit" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color }
                ],
            }]
        }],
        "Edit": [{
            "subitem": [{
                "Undo" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color },
                ],
                "Redo" : [
                    { str_font : font_name  },
                    { str_size : font_size  },
                    { back_str : back_color },
                ],
            }]
        }],
        "Help": [{
            "subitem": [{
                "Online" : [
                    { str_font  : font_name  },
                    { str_size  : font_size  },
                    { str_color : font_color },
                    { back_str  : back_color },
                ],
                "About"  : [
                    { str_font  : font_name  },
                    { str_size  : font_size  },
                    { str_color : font_color },
                    { back_str  : back_color }
                ]
            }]
        }]  }
        
        super().add(self.standardMenuBar)
        super().show(self)
        return
