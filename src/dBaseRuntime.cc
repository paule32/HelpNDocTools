// ----------------------------------------------------------------------------
// \file  dBaseRuntime.cc
// \note  (c) 2025, 2026 by Jens Kallup - paule32
//        all rights reserved.
// ----------------------------------------------------------------------------
#pragma once

#include <string>
#include <vector>
#include <stdexcept>
#include <variant>
#include <iostream>

class TRT {
public:
    using V = std::variant<std::monostate, bool, int64_t, double, std::string>;

    static V Null() { return std::monostate{}; }

    // --- I/O ---
    void WRITE(const V& v) {
        std::cout << to_string(v) << std::endl;
    }

    // --- scope / this ---
    V GET_THIS() { return Null(); } // TODO
  
    V    GET_NAME(const std::string& name) { (void)name; return Null(); } // TODO
    void SET_NAME(const std::string& name, const V& value) { (void)name; (void)value; } // TODO

    // --- members / calls ---
    V      GET(const V& base, const std::vector<std::string>& path) { (void)base; (void)path; return Null(); } // TODO
    void   SET(const V& base, const std::vector<std::string>& path, const V& value) { (void)base; (void)path; (void)value; } // TODO
  
    V GET_ATTR(const V& base, const std::string& name) { (void)base; (void)name; return Null(); } // TODO
    V CALL_ANY(const V& base, const std::vector<V>& args) { (void)base; (void)args; return Null(); } // TODO
  
    V NEW(const std::string& className, const std::vector<V>& args) { (void)className; (void)args; return Null(); } // TODO

    // --- WITH ---
    void PUSH_WITH(const V& base) { withBase = base; }
    void  POP_WITH() { withBase = Null(); }

    void WITH_SET(const std::vector<std::string>& path, const V& value) {
        if (std::holds_alternative<std::monostate>(withBase))
            throw std::runtime_error("WITH_SET ohne aktives WITH");
        SET(withBase, path, value);
    }

    // --- ops / truth ---
    V BINOP(const V& a, const std::string& op, const V& b) { (void)a; (void)op; (void)b; return Null(); } // TODO
    V  UNOP(const std::string& op, const V& a) { (void)op; (void)a; return Null(); } // TODO
  
    bool TRUE(const V& v) { return !std::holds_alternative<std::monostate>(v); } // TODO

    // --- FOR cond helper ---
    bool FOR_COND(const V& i, const V& e, const V& step) { (void)i; (void)e; (void)step; return true; } // TODO

    // --- PARAMETER / RETURN ---
    void PARAMETER(const std::vector<std::string>& names) { (void)names; } // TODO
    void    RETURN(const V& v) { (void)v; } // TODO (z.B. Exception werfen)

private:
    V withBase = Null();
    
    static std::string to_string(const V& v) {
        if (std::holds_alternative<std::monostate>(v)) return "NULL";
        
        if (auto p = std::get_if<bool       >(&v)) return *p ? "TRUE" : "FALSE";
        if (auto p = std::get_if<int64_t    >(&v)) return std::to_string(*p);
        if (auto p = std::get_if<double     >(&v)) return std::to_string(*p);
        if (auto p = std::get_if<std::string>(&v)) return *p;
        
        return "?";
    }
};
