import gcc

from PyArg_ParseTuple import check_pyargs, log
from refcounts import check_refcounts

def on_pass_execution(optpass, fun):
    # Only run in one pass
    # FIXME: should we be adding our own pass for this?
    if optpass.name != '*warn_function_return':
        return

    log(fun)
    if fun:
        check_pyargs(fun)

def get_all_PyMethodDef_methods():
    # Locate all initializers for PyMethodDef, returning a list of
    # (gcc.Declaration, gcc.Location) for the relevant callback functions
    # (the ml_meth field, and the location of the initializer)
    log('get_all_PyMethodDef_methods')

    def get_ml_meth_decl(methoddef_initializer):
         for idx2, value2 in value.elements:
             if isinstance(idx2, gcc.Declaration):
                 if idx2.name == 'ml_meth':
                     if isinstance(value2, gcc.AddrExpr):
                         log('    GOT A PyMethodDef.ml_meth initializer declaration: %s' % value2)
                         log('      value2.operand: %r' % value2.operand) # gcc.Declaration
                         log('      value2.operand: %s' % value2.operand)
                         log('      value2.operand.function: %s' % value2.operand.function)
                         return (value2.operand, value2.location)
    result = []
    vars = gcc.get_variables()
    for var in vars:
        if isinstance(var.decl, gcc.VarDecl):
            if isinstance(var.decl.type, gcc.ArrayType):
                if str(var.decl.type.type) == 'struct PyMethodDef':
                    if var.decl.initial:
                        for idx, value in var.decl.initial.elements:
                            decl = get_ml_meth_decl(value)
                            if decl:
                                result.append(decl)
    return result

def main():
    gcc.register_callback(gcc.PLUGIN_PASS_EXECUTION,
                          on_pass_execution)