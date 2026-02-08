using System;

// TODO item: ItemContext
// TODO item: ItemContext
// TODO item: ItemContext
// TODO item: ItemContext
// TODO item: ItemContext
// TODO item: ItemContext
// TODO item: ItemContext
// TODO item: ItemContext
// TODO item: ItemContext
// TODO item: ItemContext
// TODO item: ItemContext
public class ParentForm : FORM {
    public object width;
    public object top;
    // TODO class body child: ClassMemberContext
    // TODO class body child: ClassMemberContext
    // TODO class body child: ClassMemberContext
    // TODO class body child: ClassMemberContext
    // TODO class body child: ClassMemberContext
    // TODO class body child: ClassMemberContext
    // TODO class body child: ClassMemberContext
    // TODO class body child: StatementContext
    public object Init(object a, object c) {{
        Console.WriteLine();
        Console.WriteLine();
        Console.WriteLine();
        Console.WriteLine();
        I = 1;
        E = 42;
        for (int I = 1; I <= 3; I += 1) {
                    Console.WriteLine();
                    E = E+1;
                    Console.WriteLine();
                    Console.WriteLine();
                    Console.WriteLine();
                    if (I==3) {
                        return null;
                    }
                    break;
                }
        Console.WriteLine();
        return null;
    }
    
    public object TestProc(object Sender) {{
        Console.WriteLine();
        return 324;
        return null;
    }
    
    public object ParentForm_onClick(object Sender) {{
        Console.WriteLine();
        x = 5;
        Console.WriteLine();
        /* TODO stmt: StatementContext */;
        Console.WriteLine();
        /* TODO stmt: StatementContext */;
        return null;
    }
    
    public object PushButton1_onClick_1(object Sender) {{
        Console.WriteLine();
        Console.WriteLine();
        /* TODO stmt: StatementContext */;
        if (THIS.PushButton1.Text=="Click Me") {
                    THIS.PushButton2.Text = "Click Me";
                    Console.WriteLine();
                    /* TODO stmt: StatementContext */;
                }
                else {
                    THIS.PushButton2.Text = "Click Me, too";
                    Sender.Text = "Click Me";
                    Sender.Font.bold = .F.;
                    Sender.Font.Size = 11;
                }
        return null;
    }
    
    public object PushButton1_onClick_2(object Sender) {{
        Console.WriteLine();
        return null;
    }
    
    public object PushButton1_onClick_3(object Sender) {{
        Console.WriteLine();
        return null;
    }
    
    public object PushButton1_onMouseRButton(object Sender) {{
        Console.WriteLine();
        return null;
    }
    
    public object PushButton1_onMouseMove(object Sender) {{
        Console.WriteLine();
        return null;
    }
    
    public object PushButton2_onClick(object Sender) {{
        Console.WriteLine();
        Console.WriteLine();
        if (THIS.PushButton2.Text=="Click Me, too") {
                    THIS.PushButton1.Text = "Click Me";
                    Sender.Text = "Click Me";
                }
                else {
                    THIS.PushButton1.Text = "Click Me";
                    Sender.Text = "Click Me, too";
                }
        return null;
    }
    
}
