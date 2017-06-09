import importlib
import inspect
import os
import sys

from collections import defaultdict


def make_replace_for_doc(text):
    for to_replace in REPLACE_TO_EMPTY_STR:
        text = text.replace(to_replace, '')

    return text


def make_replace_for_response_and_value(text):
    for to_replace in REPLACE_TO_LIST:
        text = text.replace(to_replace, 'list')

    for _from, to in REPLACE_TO_ANOTHER.items():
        text = text.replace(_from, to)

    return text


def make_replace_for_constant(text):
    text = str(text)
    if '<built-in function' in text:
        matched = re_built_in_function.match(text)
        text = text.replace(matched.group(1), matched.group(1)[19:-1])

    return text


def prepare_doc(doc, level):
    if not doc:
        return ''
    sep_1 = SEPARATOR * (level + 1)
    sep_2 = SEPARATOR * (level + 2)
    return DOC_FORMAT.format(sep=sep_1, doc=doc.strip().replace('\n', '\n'+sep_2))


def get_return_from_doc(doc):
    _return = 'pass'
    if ':rtype:' not in doc:
        return _return

    search_obj = re_return_from_doc.search(doc)
    if search_obj:
        _return = 'return ' + search_obj.group(2)

    return make_replace_for_response_and_value(_return)


def add_self(name_and_arg):
    position = name_and_arg.find('(') + 1

    if len(name_and_arg) - position == 1:
        self = 'self'
    else:
        self = 'self, '

    return name_and_arg[:position] + self + name_and_arg[position:]


def pars_function_doc(doc, level, member, in_class=False):
    if not doc:
        return '%s(*args)' % member, '', 'pass'

    doc = make_replace_for_doc(doc)

    search_obj = re.search(re.escape(member) + r'\((.*)\)', doc)
    if search_obj:
        name_and_args = search_obj.group(0)
        doc = doc.replace(name_and_args, '')
    else:
        name_and_args = '%s(*args)' % member
    if in_class:
        name_and_args = add_self(name_and_args)

    _return = get_return_from_doc(doc)
    doc = prepare_doc(doc, level)
    return name_and_args, doc, _return


def pars_class_doc(doc, level):
    sep = SEPARATOR * (level+1)

    if doc:
        doc = make_replace_for_doc(doc)
        doc = doc.replace('\n', '\n{sep}'.format(sep=sep))
        return DOC_CLASS_FORMAT.format(doc=doc, sep=sep)

    return ''


def get_value_or_none(docstring):
    search_obj = re_value.search(docstring)

    if search_obj:
        return make_replace_for_response_and_value(search_obj.group(2))

    return None


def digger(base_mod, object, level=0, in_class=False):
    sep = SEPARATOR * level
    sep_return = SEPARATOR + sep
    data_per_type = defaultdict(list)

    for member in object:
        mod_attr = getattr(base_mod, member)

        if member.startswith('_'):
            logging.debug("Skip: %s in %s", member, base_mod)

        elif isinstance(mod_attr, (str, int, float, list, tuple, dict)):
            mod_attr = make_replace_for_constant(mod_attr)
            data_per_type[TYPE_CONSTANT].append(CONSTANT_FORMAT % (sep, member, mod_attr))

        elif inspect.isbuiltin(mod_attr):
            name_and_arg, docstring, _return = pars_function_doc(mod_attr.__doc__, level, member, in_class)

            if in_class and 'built-in method' in str(mod_attr):
                name_and_arg = name_and_arg.replace("self", "cls")
                to_write = CLASSMETHOD_FORMAT % (sep, sep, name_and_arg, docstring, sep_return, _return)
                data_per_type[TYPE_CLASSMETHOD].append(to_write)
            else:
                data_per_type[TYPE_FUNCTION].append(
                    FUNCTION_FORMAT % (sep, name_and_arg, docstring, sep_return, _return)
                )

        elif inspect.isfunction(mod_attr):
            name_and_arg, docstring, _return = pars_function_doc(mod_attr.__doc__, level, member, in_class)
            data_per_type[TYPE_FUNCTION].append(
                FUNCTION_FORMAT % (sep, name_and_arg, docstring, sep_return, _return)
            )

        elif inspect.ismethoddescriptor(mod_attr):
            if in_class and 'BaseException' in str(mod_attr):
                logging.debug('Skip: %s', mod_attr)
            else:
                name_and_arg, docstring, _return = pars_function_doc(mod_attr.__doc__, level, member, in_class)
                data_per_type[TYPE_METHOD_DESCRIPTOR].append(
                    METHOD_DESCRIPTOR_FORMAT % (sep, name_and_arg, docstring, sep_return, _return)
                )

        elif inspect.isgetsetdescriptor(mod_attr):
            docstring = prepare_doc(mod_attr.__doc__, level - 1)  # -1 because it is attribute
            value = get_value_or_none(docstring)
            data_per_type[TYPE_ATTRIBUTE].append(ATTRIBUTE_FORMAT % (sep, member, value, docstring))

        elif inspect.isclass(mod_attr):
            docstring = pars_class_doc(mod_attr.__doc__, level)
            data_per_type[TYPE_CLASS].append(
                {
                    CLASS_HEAD: CLASS_FORMAT % (sep, member, docstring),
                    CLASS_BODY: digger(mod_attr, dir(mod_attr), level+1, in_class=True)
                }
            )

        elif inspect.ismodule(mod_attr):
            data_per_type[TYPE_MODULE].append(mod_attr)

        else:
            logging.debug("Unknown type: %s %s", member, type(mod_attr))
            data_per_type[TYPE_UNKNOWN].append(UNKNOWN_FORMAT % (sep+SEPARATOR, member, type(mod_attr)))

    if TYPE_UNKNOWN in data_per_type:
        logging.warning("%s unknown types for %s", len(data_per_type[TYPE_UNKNOWN]), base_mod)

    return data_per_type


def writer(file, data_per_type):
    for _type in [TYPE_CONSTANT, TYPE_CLASSMETHOD, TYPE_FUNCTION, TYPE_METHOD_DESCRIPTOR, TYPE_ATTRIBUTE]:
        for data in data_per_type[_type]:
            file.write(data)
    for _class in data_per_type[TYPE_CLASS]:
        file.write(_class[CLASS_HEAD])
        if _class[CLASS_BODY]:
            writer(file, _class[CLASS_BODY])
        else:
            file.write(PASS_FORMAT % SEPARATOR)
    if TYPE_UNKNOWN in data_per_type:
        file.write("\n#TODO: Unknown data\n")
        for unknown in data_per_type[TYPE_UNKNOWN]:
            file.write(unknown)


def fetch_modules(output_dir, modules, level=0):
    logging.info("Fetch modules (on level %s): %s", level, modules)
    for module in modules:
        logging.info("Fetch module: %s", module)
        if level == 0:
            try:
                module = importlib.import_module(module)
            except ImportError as e:
                logging.warning(e)
                continue

        module_path = module.__name__.replace('.', '/')
        logging.debug("Module path: %s", module_path)
        module_dir = dir(module)
        logging.debug("Module dir: %s", module_dir)
        module_doc = module.__doc__
        logging.debug("Module doc: %s", module_doc)

        data_per_type = digger(module, module_dir)

        if TYPE_MODULE in data_per_type:
            os.makedirs(os.path.join(output_dir, module_path), exist_ok=True)
            file_name = module_path + '/__init__.py'
        else:
            file_name = module_path + '.py'

        logging.info("Create file: %s", file_name)
        with open(os.path.join(output_dir, file_name), "w") as new_file:
            if module_doc:
                new_file.write(NEW_FILE_DOC_FORMAT % module_doc)
            writer(new_file, data_per_type)

        if TYPE_MODULE in data_per_type:
            fetch_modules(output_dir, data_per_type[TYPE_MODULE], level=level + 1)


if __name__ == "__main__":
    sys.path.append(os.getcwd())
    from constants import *
    from logger_init import *

    initialize_logger()
    logging.getLogger('badpy')

    if sys.argv[0] == 'blender' and len(sys.argv) == 7:
        output, modules = sys.argv[-2:]
        logging.info("BadPy has been run with args: '%s', '%s'", output, modules)

        os.makedirs(output, exist_ok=True)

        fetch_modules(output, modules.split(', '))
    else:
        logging.info("Please use run_badpy.py, or blender with -P option:\n"
                     "blender -b -P badpy.py -- [output] [modules]")
