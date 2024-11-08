

** END HEADER -- do not remove this line
//
// Generated on 02/06/2024
//
parameter bModal
local f
f = new Form1()
if (bModal)
    f.mdi = false  // ensure not MDI
    f.readModal()
else
    f.op_en()
endif


CLASS Form1 OF FORM

ENDCLASS
