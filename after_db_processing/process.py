from pathlib import Path
import re
from initialize_db import Session
from byond_orm import ByondClass, ByondVerb, ByondProc


def line_by_line_conversion(instring, is_object: bool):
    # check if item follows the following regex
    # ^\s*(var/(list/)?)?((?:[\w\d]+\/)*)([\w\d]+)\s*=\s*(.+)$
    # group 1 is if it's a var or not
    # group 2 is the hierarchy/type whether a var or not.
    # group 3 is the variable name
    # group 4 is the result
    # Deal with lists?
    # Deal with
    if re.match(r'^(\s*)(var/(list/)?)?((?:[\w\d]+/)*)([\w\d]+)\s*=\s*(.+)$', instring):
        (whitespace, is_var_or_not, is_list_or_not, full_hierarchy, var_name, result) = re.search(
            r'^(\s*)(var/(list/)?)?((?:[\w\d]+/)*)([\w\d]+)\s*=\s*(.+)$',
            instring
        ).groups()
        if is_empty(is_var_or_not):
            if is_empty(full_hierarchy):
                return '{}{} = {}'.format(whitespace, var_name, result)
            else:
                return '{}{} = {}'.format(whitespace, var_name, result)
        elif not is_empty(full_hierarchy):
            type_name = get_new_name_for_full_hierarchy('/' + full_hierarchy)
            return '{}var {}: {} = {}'.format(whitespace, var_name, type_name, result)
        else:
            return '{}var {} = {}'.format(whitespace, var_name, result)
    else:
        return instring


def particular_regex_conversions(str_item, verb_name="placeholder"):
    # Add more of these.
    str1 = re.sub(
        r'istype\((\w+)\s*,\s*/?((\w+/)*)(\w+)\)',
        lambda a: replace_is_type(a),
        str_item,
        flags=re.MULTILINE
    )
    str2 = re.sub(
        r'^(\s*)(?:(else)|(else)?\s*if\s*\((.+)\))\s*(//.+)?$',
        lambda a: replace_if_statements(a),
        str1,
        flags=re.MULTILINE
    )
    str3 = replace_automatic_return_val(str2)
    # replaces the ..() syntax for calling a parent override of a function/proc
    str4 = re.sub(
        r'\.\.\((.*)\)',
        lambda a: '.{}({})'.format(verb_name, a.group(1)),
        str3
    )
    # to_chat regex? combine with symbol?
    # to_chat\((\w+), \"<span class='(\w+)'>(.+)</span>\"\)
    str5 = re.sub(
        r'to_chat\((\w+), \"<span class=\'(\w+)\'>(.+)</span>\"\)',
        lambda a: 'to_simple_chat_message({}, "{}", "{}")'.format(a.group(1), a.group(2), a.group(3)),
        str4
    )
    # regex for strings
    str6 = re.sub(
        r'\"((?:(?:[^\"\\\[]|\\.)*|\[(?:[^\[\]]+)\])*)\"',
        lambda a: replace_quoted_interpolation_string(a),
        str5,
        flags=re.MULTILINE
    )
    return str6


def replace_automatic_return_val(str2):
    str3 = re.sub(
        r'^(\s*)\.\s*=(.+)',
        lambda a: '{}byond_return_val = {}'.format(a.group(1), a.group(2)),
        str2,
        flags=re.MULTILINE
    )
    return str3 + '\n\treturn byond_return_val' if re.search(r'^(\s*)\.\s*=(.+)', str2) else str3


def replace_quoted_interpolation_string(matchobj):
    core_string = matchobj.group(1)
    values_arr = re.finditer(r'\[([^\[\]]+)\]', core_string)
    values_string = ' % [' + ', '.join(map(lambda a: a.group(1), values_arr)) + ']'
    split_arr = re.split(r'\[(?:[^\[\]]+)\]', core_string)
    if re.search(r'\[([^\[\]]+)\]', core_string):
        return '"' + '%s'.join(split_arr) + '"' + values_string
    else:
        return '"' + '%s'.join(split_arr) + '"'


def replace_if_statements(matchobj):
    (whitespace, is_else, is_else_if, if_value, comment) = matchobj.groups()
    comment_val = " " + comment if not is_empty(comment) else ""
    if is_empty(is_else) & is_empty(is_else_if):
        return '{}if {}:{}'.format(whitespace, if_value, comment_val)
    elif not is_empty(is_else):
        return '{}else:{}'.format(whitespace, comment_val)
    else:
        return '{}elif {}:{}'.format(whitespace, if_value, comment_val)


def replace_is_type(matchobj):
    (object_in_question, full_hierarchy, _, last_element) = matchobj.groups()
    if is_empty(full_hierarchy):
        return '{} is {}'.format(object_in_question, last_element)
    else:
        name = get_new_name_for_full_hierarchy(full_hierarchy + last_element + '/')
        return '{} is {}'.format(object_in_question, name)


def is_empty(str_item: str):
    return str_item is None or str_item == ''


def args_conversion(instring: str):
    split = instring.split(',')
    new_args = []
    for line in split:
        new_args.append(
            process_each_arg_in_db(extract_from_parameter(line))
        )
    return new_args


def process_each_arg_in_db(arg) -> str:
    print('processing arg: ', arg)
    default_value_addition = '' if not arg['has_default_value'] else ' = ' + arg['default_value']
    if not arg['no_inheritors']:
        # if replace_common_typings(arg):
        #     return replace_common_typings(arg)
        is_var_name_improper = arg['var_name'].isdigit()
        proper_var_name: str = 'variable' if arg['var_name'] == "0" else "variable" + arg["var_name"]
        new_var_name = proper_var_name if is_var_name_improper else arg['var_name']
        extends_name_value = get_arg_from_db(arg['full_hierarchy'] + arg['var_name'], arg['full_hierarchy'])
        return "{}: {}".format(
                new_var_name, extends_name_value) + default_value_addition
    else:
        return arg['var_name'] + default_value_addition


def get_arg_from_db(full_hierarchy_in, type_in):
    if replace_common_typings(full_hierarchy_in):
        return replace_common_typings(full_hierarchy_in)
    else:
        return get_new_name_for_full_hierarchy(type_in)


def get_new_name_for_full_hierarchy(type_in):
    session = Session()
    print("trying to find new name for: ", type_in)
    extends_name: (str, str) = session.query(ByondClass.new_name, ByondClass.full_heritage_id).filter(
        ByondClass.full_heritage_id == type_in).one_or_none()
    (extends_name_value, extending_inheritance) = ('placeholder', '') if (extends_name is None) else extends_name
    return extends_name_value


def replace_common_typings(arg):
    # TODO: expand this? Add something similar for other known conditions?
    switcher = {
        '/mob/user': 'ByondUser',
        '/obj/item/O': 'ByondItem'

    }
    return switcher.get(arg, False)


def extract_from_parameter(line):
    print("line: '{}'".format(line))
    search = re.search(
        "^\\s*(([\\w\\d]+/)*)([\\w\\d]+)\\s*,?\\s*$",
        line
    )
    # print(search)
    if search is not None:
        (object_hierarchy, _, variable_name_possibly) = search.groups()
        # print("object hierarchy: '{}'".format(object_hierarchy))
        # print("var_name_possibly: '{}'".format(variable_name_possibly))
        has_obj_hierarchy: str = 'placeholder' if object_hierarchy is None else object_hierarchy
        return {
            "full_hierarchy": "/" + has_obj_hierarchy.strip(),
            "var_name": variable_name_possibly.strip(),
            "no_inheritors": object_hierarchy is None or has_obj_hierarchy.strip() == '',
            "has_default_value": False,
            "default_value": ""
        }
    elif re.match("^\\s*(([\\w\\d]+/)*)([\\w\\d]+)\\s*=\\s*(.+)$", line):
        (object_hierarchy, _, variable_name_possibly, default_value) = re.search(
            "^\\s*(([\\w\\d]+/)*)([\\w\\d]+)\\s*=\\s*(.+)$", line).groups()
        # print("object hierarchy: '{}'".format(object_hierarchy))
        # print("var_name_possibly: '{}'".format(variable_name_possibly))
        # print("default_value: '{}'".format(default_value))
        has_obj_hierarchy: str = 'placeholder' if object_hierarchy is None else object_hierarchy
        trimmed_default_value: str = default_value
        return {
            "full_hierarchy": "/" + has_obj_hierarchy.strip(),
            "var_name": variable_name_possibly.strip(),
            "no_inheritors": object_hierarchy is None or has_obj_hierarchy.strip() == '',
            "has_default_value": True,
            "default_value": trimmed_default_value.strip()
        }


def get_godot_parameter_for_inputs(object_hierarchy: str, variable_name):
    pass


def convert_from_database_to_output(input_folder, out_folder):
    #     get list of byond classes from db.
    # run byondclass to file conversion.
    session = Session()
    for instance in session.query(ByondClass).order_by(ByondClass.full_heritage_id):
        class_string = convert_byond_class_to_godot_file(instance)
        filename = Path(instance.path_first_found_in)
        p: Path = filename.relative_to(input_folder)
        pt: Path = Path(out_folder) / p
        out_dir = pt.parent / pt.name.replace(".dm", "")
        out_dir.mkdir(parents=True, exist_ok=True)
        final_output_file = out_dir / (instance.new_name + ".gd")
        # pt.
        # print("out_dir: ", out_dir)
        # print("pt: ", final_output_file)
        final_output_file.write_text(data=class_string)
    pass


def convert_byond_class_to_godot_file(instance: ByondClass):
    return """
# extends the other class:
extends {}
# this class is named: 
class_name {}
# member variables:
{}
# verb functions:
{}
# proc functions:
{}""".format(instance.class_extends,
             instance.new_name,
             convert_byond_class_text_to_godot(instance.text),
             ''.join(map(lambda a: convert_byond_verbs_to_godot(a), instance.verbs)),
             ''.join(map(lambda a: convert_byond_procs_to_godot(a), instance.procs)))


def convert_byond_verbs_to_godot(verb: ByondVerb):
    args_result = args_conversion(verb.arguments)
    # text: str = verb.text
    # for each_param in args_result:
    #     if each_param['needs_replacement']:
    #         text = text.replace(each_param['original_name'], each_param['replacement_var'])
    arg_string = ', '.join(args_result)
    split_text = particular_regex_conversions(verb.text, verb_name=verb.name).split('\n')
    text = '\n'.join(map(lambda a: line_by_line_conversion(a, False), split_text))
    return """
# formerly a byond verb
# add ability to call from menu?
func {}({}):
{}""".format(
        verb.name,
        arg_string,
        text
    )


def convert_byond_procs_to_godot(proc: ByondProc):
    return """
# formerly a byond proc
func {}({}):
{}""".format(
        proc.name,
        proc.arguments,
        proc.text
    )


def convert_byond_class_text_to_godot(class_text):
    split_text = class_text.split('\n')
    text = '\n'.join(map(lambda a: line_by_line_conversion(a, True), split_text))
    return text
