#   Copyright 2011, 2012 David Malcolm <dmalcolm@redhat.com>
#   Copyright 2011, 2012 Red Hat, Inc.
#
#   This is free software: you can redistribute it and/or modify it
#   under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see
#   <http://www.gnu.org/licenses/>.

from cpybuilder import *
from wrapperbuilder import PyGccWrapperTypeObject

cu = CompilationUnit()
cu.add_include('gcc-python.h')
cu.add_include('gcc-python-wrappers.h')
cu.add_include('gcc-plugin.h')
cu.add_include("function.h")
cu.add_include("gcc-c-api/gcc-function.h")
cu.add_include("gcc-c-api/gcc-declaration.h")
cu.add_include("gcc-c-api/gcc-tree.h")

modinit_preinit = ''
modinit_postinit = ''

def generate_function():
    #
    # Generate the gcc.Function class:
    #
    global modinit_preinit
    global modinit_postinit
    cu.add_defn("\n"
                "static PyObject *\n"
                "PyGccFunction_get_cfg(struct PyGccFunction *self, void *closure)\n"
                "{\n"
                "    return PyGccCfg_New(gcc_function_get_cfg(self->fun));\n"
                "}\n"
                "\n")
    getsettable = PyGetSetDefTable('PyGccFunction_getset_table',
                                   [PyGetSetDef('cfg', 'PyGccFunction_get_cfg', None,
                                                'Instance of gcc.Cfg for this function (or None for early passes)'),
                                    ],
                                   identifier_prefix='PyGccFunction',
                                   typename='PyGccFunction')
    getsettable.add_simple_getter(cu,
                                  'decl', 
                                  'PyGccTree_New(gcc_function_decl_as_gcc_tree(gcc_function_get_decl(self->fun)))',
                                  'The declaration of this function, as a gcc.FunctionDecl instance')
    getsettable.add_simple_getter(cu,
                                  'local_decls',
                                  'VEC_tree_as_PyList(self->fun.inner->local_decls)',
                                  "List of gcc.VarDecl for the function's local variables")
    getsettable.add_simple_getter(cu,
                                  'funcdef_no',
                                  'PyGccInt_FromLong(gcc_function_get_index(self->fun))',
                                  'Function sequence number for profiling, debugging, etc.')
    getsettable.add_simple_getter(cu,
                                  'start',
                                  'PyGccLocation_New(gcc_function_get_start(self->fun))',
                                  'Location of the start of the function')
    getsettable.add_simple_getter(cu,
                                  'end',
                                  'PyGccLocation_New(gcc_function_get_end(self->fun))',
                                  'Location of the end of the function')
    cu.add_defn(getsettable.c_defn())

    pytype = PyGccWrapperTypeObject(identifier = 'PyGccFunction_TypeObj',
                          localname = 'Function',
                          tp_name = 'gcc.Function',
                          tp_dealloc = 'PyGccWrapper_Dealloc',
                          struct_name = 'PyGccFunction',
                          tp_new = 'PyType_GenericNew',
                          tp_repr = '(reprfunc)PyGccFunction_repr',
                          tp_str = '(reprfunc)PyGccFunction_repr',
                          tp_hash = '(hashfunc)PyGccFunction_hash',
                          tp_richcompare = 'PyGccFunction_richcompare',
                          tp_getset = getsettable.identifier,
                                    )
    cu.add_defn(pytype.c_defn())
    modinit_preinit += pytype.c_invoke_type_ready()
    modinit_postinit += pytype.c_invoke_add_to_module()

generate_function()

cu.add_defn("""
int autogenerated_function_init_types(void)
{
""" + modinit_preinit + """
    return 1;

error:
    return 0;
}
""")

cu.add_defn("""
void autogenerated_function_add_types(PyObject *m)
{
""" + modinit_postinit + """
}
""")



print(cu.as_str())
