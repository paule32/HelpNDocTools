import java.util.*;

public class GenProg {
  public static void main(String[] args) {
    TRT rt = new TRT();
    try {
      rt.SET_NAME("Y", TRT.Null());
      rt.WRITE(rt.BINOP(TRT.V("Hello"), "+", TRT.V("World")));
      rt.SET_NAME("X", TRT.Null());
      rt.SET_NAME("X", rt.BINOP(TRT.Null(), "+", TRT.Null()));
      if (rt.TRUE(rt.BINOP(TRT.Null(), "==", TRT.Null()))) {
        rt.WRITE(rt.BINOP(TRT.V("X := "), "+", rt.GET(rt.GET_NAME("X"), java.util.List.of())));
      }
      if (rt.TRUE(rt.BINOP(TRT.Null(), "==", (rt.BINOP(TRT.Null(), "+", TRT.Null()))))) {
        rt.WRITE(TRT.V("falsch"));
      }
      else {
        if (rt.TRUE(rt.BINOP(TRT.Null(), "<", TRT.Null()))) {
          rt.WRITE(rt.BINOP(rt.BINOP(TRT.V("huch"), "+", TRT.V(" hach")), "+", TRT.V('xxxx')));
        }
        else {
          rt.WRITE(TRT.V("sonst"));
        }
        rt.WRITE(TRT.V("naja"));
        if (rt.TRUE(rt.BINOP(TRT.Null(), "==", TRT.Null()))) {
          rt.WRITE(TRT.V("2222"));
        }
        rt.SET_NAME("X", rt.BINOP(TRT.Null(), "+", TRT.Null()));
        if (rt.TRUE(rt.BINOP(TRT.Null(), "==", TRT.Null()))) {
          rt.WRITE(TRT.V("OKAY"));
        }
      }
      rt.PARAMETER(java.util.List.of("bmodal"));
      rt.SET_NAME("B", TRT.Null());
      rt.SET_NAME("B", rt.NEW("ParentForm", java.util.List.of(TRT.Null(), TRT.Null())));
      rt.CALL_ANY(TRT.Null(), java.util.List.of(TRT.Null(), TRT.Null()));
      rt.CALL_ANY(TRT.Null(), java.util.List.of());
      // TODO classDecl not implemented in Java backend
    } catch (Exception e) {
      System.err.println("ERROR: " + e.getMessage());
      e.printStackTrace();
    }
  }
}
