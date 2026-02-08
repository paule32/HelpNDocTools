// generated dBase -> GNU C++ (runtime-backed)
#include <iostream>
#include <vector>
#include <string>
#include "dBaseRT.hpp"

int main() {
  TRT rt;
  try {
    rt.SET_NAME("Y", TRT::Null());
    rt.WRITE(rt.BINOP(TRT::V("Hello"), "+", TRT::V("World")));
    rt.SET_NAME("X", TRT::Null());
    rt.SET_NAME("X", rt.BINOP(TRT::Null(), "+", TRT::Null()));
    if (rt.TRUE(rt.BINOP(TRT::Null(), "==", TRT::Null()))) {
      rt.WRITE(rt.BINOP(TRT::V("X := "), "+", rt.GET(rt.GET_NAME("X"), {  })));
    }
    if (rt.TRUE(rt.BINOP(TRT::Null(), "==", (rt.BINOP(TRT::Null(), "+", TRT::Null()))))) {
      rt.WRITE(TRT::V("falsch"));
    }
    else {
      if (rt.TRUE(rt.BINOP(TRT::Null(), "<", TRT::Null()))) {
        rt.WRITE(rt.BINOP(rt.BINOP(TRT::V("huch"), "+", TRT::V(" hach")), "+", TRT::V('xxxx')));
      }
      else {
        rt.WRITE(TRT::V("sonst"));
      }
      rt.WRITE(TRT::V("naja"));
      if (rt.TRUE(rt.BINOP(TRT::Null(), "==", TRT::Null()))) {
        rt.WRITE(TRT::V("2222"));
      }
      rt.SET_NAME("X", rt.BINOP(TRT::Null(), "+", TRT::Null()));
      if (rt.TRUE(rt.BINOP(TRT::Null(), "==", TRT::Null()))) {
        rt.WRITE(TRT::V("OKAY"));
      }
    }
    rt.PARAMETER({ "bmodal" });
    rt.SET_NAME("B", TRT::Null());
    rt.SET_NAME("B", rt.NEW("ParentForm", { TRT::Null(), TRT::Null() }));
    (void)rt.CALL_ANY(TRT::Null(), { TRT::Null(), TRT::Null() });
    (void)rt.CALL_ANY(TRT::Null(), {  });
    // TODO classDecl not implemented in C++ backend
  } catch (const std::exception& e) {
    std::cerr << "ERROR: " << e.what() << std::endl;
    return 1;
  }
  return 0;
}
