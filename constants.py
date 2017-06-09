import re

VER = '0.1'

INCLUDE_MODULES = ('aud', 'bgl', 'blf', 'bmesh', 'bpy', 'bpy_extras', 'gpu', 'mathutils')
DEFAULT_OUTPUT_DIR = 'BADPy_OutPut'

SEPARATOR = ' ' * 4

re_arg = re.compile(r'^:arg\s(.+):\s(.+)$')
re_type = re.compile(r'^:type\s(.+):\s(.+)$')
re_built_in_function = re.compile(r'.*(<built-in function .+>).*')
re_return_from_doc = re.compile(r':rtype:(\s|\s:.+:)`?([\w|\.]+)`?')
re_value = re.compile(r':?type:(\s|\s:\w+:)`?([\w\.]+)`?')

DOC_FORMAT = '{sep}""" {doc}\n{sep}"""\n\n'
DOC_CLASS_FORMAT = '{sep}"""\n{sep}{doc}\n{sep}"""\n'
CONSTANT_FORMAT = "%s%s = %s   # constant value\n\n"
CLASSMETHOD_FORMAT = "%s@classmethod\n%sdef %s:\n%s%s%s\n\n"
FUNCTION_FORMAT = "\n%sdef %s:\n%s%s%s\n\n"
METHOD_DESCRIPTOR_FORMAT = "%sdef %s:\n%s%s%s\n\n"
ATTRIBUTE_FORMAT = "%s%s = %s\n%s"
CLASS_FORMAT = "\n%sclass %s:\n%s\n"
UNKNOWN_FORMAT = "#%s%s (%s)\n"
PASS_FORMAT = '%spass\n\n'
NEW_FILE_DOC_FORMAT = '"""\n    %s\n"""\n\n\n'

REPLACE_TO_EMPTY_STR = [':class:', '`', ':attr:', ':meth:', ':func:', '.. function::', '.. method::', '.. include::',
                        '.. classmethod::', '   ']
REPLACE_TO_LIST = ['list of tuples', 'list of ints', 'list of floats', 'list of strings', 'list of BMLoop tuples',
                   'return the buffer as a list']
REPLACE_TO_ANOTHER = {'tuple of 2 floats': '(float, float)', 'integer': 'int', 'string': 'str', 'boolean': 'bool',
                      'BMVert or None': 'BMVert'}

TYPE_CONSTANT = "CONSTANT"
TYPE_CLASSMETHOD = "CLASSMETHOD"
TYPE_FUNCTION = "FUNCTION"
TYPE_METHOD_DESCRIPTOR = "METHOD_DESCRIPTOR"
TYPE_ATTRIBUTE = "ATTRIBUTE"
TYPE_CLASS = "CLASS"
TYPE_MODULE = "MODULE"
TYPE_UNKNOWN = "UNKNOWN"
CLASS_HEAD = 'HEAD'
CLASS_BODY = 'BODY'
