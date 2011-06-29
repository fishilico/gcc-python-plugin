#   Copyright 2011 David Malcolm <dmalcolm@redhat.com>
#   Copyright 2011 Red Hat, Inc.
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

cu = CompilationUnit()
cu.add_include('gcc-python.h')
cu.add_include('gcc-python-wrappers.h')
cu.add_include('gcc-plugin.h')
cu.add_include("diagnostic.h")

# FIXME: need to participate in the GC, to ensure ownership of the underlying
# diag object

modinit_preinit = ''
modinit_postinit = ''

def generate_option():
    #
    # Generate the gcc.Option class:
    #
    global modinit_preinit
    global modinit_postinit

    getsettable = PyGetSetDefTable('gcc_Option_getset_table', [],
                                   identifier_prefix='gcc_Option',
                                   typename='PyGccOption')
    def add_simple_getter(name, c_expression, doc):
        getsettable.add_simple_getter(cu, name, c_expression, doc)

    add_simple_getter('text',
      'gcc_python_string_or_none(gcc_python_option_to_cl_option(self)->opt_text)',
      '(string) The command-line text used to set this option')
    add_simple_getter('help',
      'gcc_python_string_or_none(gcc_python_option_to_cl_option(self)->help)',
      '(string) The help text shown for this option')

    for flag, helptext in (
        ('CL_WARNING', '(bool) Does this option control a warning message?'),
        ('CL_OPTIMIZATION', '(bool) Does this option control an optimization?'),
        ('CL_DRIVER', '(bool) Is this a driver option?'),
        ('CL_TARGET', '(bool) Is this a target-specific option?'),
      ):
        add_simple_getter('is_%s' % flag[3:].lower(),
                          'PyBool_FromLong(gcc_python_option_to_cl_option(self)->flags & %s)' % flag,
                          helptext)

    cu.add_defn(getsettable.c_defn())

    pytype = PyTypeObject(identifier = 'gcc_OptionType',
                          localname = 'Option',
                          tp_name = 'gcc.Option',
                          struct_name = 'struct PyGccOption',
                          tp_init = 'gcc_Option_init',
                          tp_getset = getsettable.identifier,
                          tp_repr = '(reprfunc)gcc_Option_repr',
                          #tp_str = '(reprfunc)gcc_Option_str',
                          #tp_richcompare = 'gcc_Option_richcompare'
                          )
    cu.add_defn(pytype.c_defn())
    modinit_preinit += pytype.c_invoke_type_ready()
    modinit_postinit += pytype.c_invoke_add_to_module()

generate_option()

cu.add_defn("""
int autogenerated_option_init_types(void)
{
""" + modinit_preinit + """
    return 1;

error:
    return 0;
}
""")

cu.add_defn("""
void autogenerated_option_add_types(PyObject *m)
{
""" + modinit_postinit + """
}
""")



print(cu.as_str())