from pathlib import Path
import re
from initialize_db import Session
from byond_orm import ByondClass, ByondVerb, ByondProc


def line_by_line_conversion(instring):
    pass


def args_conversion(instring: str):
    split = instring.split(',')
    new_args = []
    for line in split:
        new_args.append(extract_from_parameter(line))
    return new_args


def process_each_arg_in_db(arg):
    if not arg['no_inheritors']:
        if replace_common_typings(arg):
            return replace_common_typings(arg)
        session = Session()
        session.query(ByondClass).filter(ByondClass.full_heritage_id == arg['full_hierarchy'])


def replace_common_typings(arg):
    # TODO: expand this? Add something similar for other known conditions?
    switcher = {
        '/mob/user': 'user: ByondUser',

    }
    return switcher.get(arg['full_hierarchy'], False)


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
            "full_hierarchy": "/" + has_obj_hierarchy,
            "var_name": variable_name_possibly,
            "no_inheritors": (has_obj_hierarchy == 'placeholder'),
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
            "no_inheritors": (has_obj_hierarchy == 'placeholder'),
            "has_default_value": False,
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
        print("out_dir: ", out_dir)
        print("pt: ", final_output_file)
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
    return """
# formerly a byond verb
# add ability to call from menu?
func {}({}):
{}""".format(
        verb.name,
        verb.arguments,
        verb.text
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
    return class_text