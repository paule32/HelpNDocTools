// ----------------------------------------------------------------------------
// \file  dBaseRuntime.java
// \note  (c) 2025, 2026 by Jens Kallup - paule32
//        all rights reserved.
// ----------------------------------------------------------------------------
import java.util.*;

public class TRT {
    public static Object Null() { return null; }
    public static Object V(Object v) { return v; }

    // IO
    public void WRITE(Object v) {
        System.out.println(String.valueOf(v));
    }

    // scope / this
    public Object GET_THIS() { return null; }                      // TODO
    
    public Object GET_NAME(String name) { return null; }           // TODO
    public void   SET_NAME(String name, Object value) { }          // TODO

    // member / calls
    public Object GET(Object base, List<String> path) { return null; } // TODO
    public void   SET(Object base, List<String> path, Object value) { } // TODO
    
    public Object GET_ATTR(Object base, String name) { return null; } // TODO
    public Object CALL_ANY(Object base, List<Object> args) { return null; } // TODO
    
    public Object NEW(String className, List<Object> args) { return null; } // TODO

    // WITH
    private Object withBase = null;
    
    public void PUSH_WITH(Object base) { withBase = base; }
    public void  POP_WITH() { withBase = null; }
    
    public void WITH_SET(List<String> path, Object value) {
        if (withBase == null) throw new RuntimeException("WITH_SET ohne aktives WITH");
        SET(withBase, path, value);
    }

    // ops / truth
    public Object BINOP(Object a, String op, Object b) { return null; } // TODO
    public Object UNOP(String op, Object a) { return null; }            // TODO
    public boolean TRUE(Object v) { return v != null; }                 // TODO

    // FOR helper
    public boolean FOR_COND(Object i, Object e, Object step) { return true; } // TODO

    // PARAMETER/RETURN
    public void PARAMETER(List<String> names) { /* TODO */ }
    public void RETURN(Object v) { /* TODO: z.B. Exception werfen */ }
}
