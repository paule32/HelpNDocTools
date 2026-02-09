import { WRITE, NEWOBJ, ParentForm } from "./rt.js";

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
export class GenProg extends FORM {
  constructor() {
    super();
    this.width = null;
    this.top = null;
  }
  
  Init(a, c) {
    WRITE();
    WRITE();
    WRITE();
    WRITE();
    I = 1;
    E = 42;
    for (let I = 0; I <= 0; I += 1) {
          WRITE();
          E = E+1;
          WRITE();
          WRITE();
          WRITE();
          if (I==3) {
            return;
          }
          break;
        }
    WRITE();
  }
  
  TestProc(Sender) {
    WRITE();
    return 324;
  }
  
  ParentForm_onClick(Sender) {
    WRITE();
    x = 5;
    WRITE();
    // TODO stmt: StatementContext
    WRITE();
    // TODO stmt: StatementContext
  }
  
  PushButton1_onClick_1(Sender) {
    WRITE();
    WRITE();
    // TODO stmt: StatementContext
    if (THIS.PushButton1.Text=="Click Me") {
          THIS.PushButton2.Text = "Click Me";
          WRITE();
          // TODO stmt: StatementContext
        }
        else {
          THIS.PushButton2.Text = "Click Me, too";
          Sender.Text = "Click Me";
          Sender.Font.bold = .F.;
          Sender.Font.Size = 11;
        }
  }
  
  PushButton1_onClick_2(Sender) {
    WRITE();
  }
  
  PushButton1_onClick_3(Sender) {
    WRITE();
  }
  
  PushButton1_onMouseRButton(Sender) {
    WRITE();
  }
  
  PushButton1_onMouseMove(Sender) {
    WRITE();
  }
  
  PushButton2_onClick(Sender) {
    WRITE();
    WRITE();
    if (THIS.PushButton2.Text=="Click Me, too") {
          THIS.PushButton1.Text = "Click Me";
          Sender.Text = "Click Me";
        }
        else {
          THIS.PushButton1.Text = "Click Me";
          Sender.Text = "Click Me, too";
        }
  }
  
}


// --- optional quick test ---
// const app = new GenProg();
// if (app.Init) app.Init();