# ----------------------------------------------------------------------------
# \file  dBaseRuntime.py
# \note  (c) 2025, 2026 by Jens Kallup - paule32
#        all rights reserved.
# ----------------------------------------------------------------------------
class RT:
    def __init__(self, runner=None):
        self.runner = runner  # optional: reuse your dBaseRunner instance

    def WRITE(self, *args):
        # map to your current WRITE behavior
        print(*args)

    def NEW(self, class_name: str, *args):
        return self.runner.new_instance(class_name.upper(), list(args))

    def GET(self, base, path):
        cur = base
        for p in path:
            cur = self.runner.get_member(cur, p, None)
        return cur

    def SET(self, base, path, value):
        self.runner.set_property_path(base, path, value, None)
        return value

    def PARAMETER(self, names):
        # mappe das auf deine Runner-Logik (Scope-Setup)
        return self.runner._parameter(names)
    
    def CALL(self, base, path, args):
        # if last segment is method name, resolve then call your runner logic
        # (depends on how your runner currently calls methods)
        return self.runner.call_path(base, path, args)

    def BINOP(self, a, op, b):
        return self.runner.binop(a, op, b)

    def TRUE(self, v):
        return bool(v)

    def SET_NAME(self, name, value):
        return self.runner._set_name(name, value)

    def GET_NAME(self, name):
        return self.runner.get_name(name)  # oder wie deine Lookup-Funktion heißt

    def DELETE_NAME(self, name):
        return self.runner._delete_name(name)

    def PUSH_WITH(self, base):
        # du hast im Runner bereits current_with_base benutzt
        self.runner.current_with_base = base

    def POP_WITH(self):
        self.runner.current_with_base = None

    def WITH_SET(self, path, value):
        base = self.runner.current_with_base
        if base is None:
            raise RuntimeError("WITH_SET ohne aktives WITH")
        self.runner.set_property_path(base, path, value, None)
        return value

    def CREATE_FILE(self, arg):
        return self.runner._create_file(arg)
        
    def RANGE_INCL(self, start, end, step):
        # inclusive range (works for ints; for floats define policy)
        start = int(start); end = int(end); step = int(step)
        if step == 0: raise ValueError("step=0")
        if step > 0:
            return range(start, end + 1, step)
        else:
            return range(start, end - 1, step)

    def MAKE_INSTANCE(self, py_obj, args):
        # optional hook if you want Python class instances to wrap your Instance
        return None
 