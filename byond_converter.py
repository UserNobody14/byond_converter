import re
from pathlib import Path

from after_db_processing.process import convert_from_database_to_output, is_empty
from before_db_processing.process import final_process_split


# def initialize_db():
#     engine = create_engine('sqlite:///:memory:', echo=True)
#     Session = sessionmaker(bind=engine)
#     pass

# macro additions:
# ^\h*#define\h+([A-Z_]+)(?:\(((?:\w+\s*,?\s*)+)\))?(?:\h+((?:[^\\\/\n]|\/(?!\/))+))?(\\?)(\/\/.+)?$
# group 1 name of the macro
# group 2 is the args list (if it exists)
# group 3 value of the macro
# group 4 is whether its multiline (if it exists)
# group 5 is the comment (if it exists)

# idea: regex reader returns a function

# standard UNDEF regex:
# ^\s*#undef\s*([A-Z_]+)\s*(\/\/.+)?$
# 1 is the name of macro removed
# 2 is the comment text

# comment regex: ^\s*(\/\/.+)?$
# comment is just group 1
from initialize_db import Session


def define_macro_regex(line):
    return re.search(
        r'^\s*#define\s+([A-Z_]+)(?:\(((?:\w+\s*,?\s*)+)\))?(?:\s+((?:[^\\/\n]|/(?!/))+))?(\\?)(//.+)?$',
        line
    )


def determine_regex_use(line, current_mode):
    matches = matches_proc_verb_or_class(line)
    new_mode = 'any'
    if current_mode == 'multiline_define':
        matches = False
        new_mode = 'any' if not re.match(r'.+\\.*', line) else 'multiline_define'
    elif current_mode == 'any':
        macro_match = define_macro_regex(line)
        matches = matches_proc_verb_or_class(line) or macro_match
        if macro_match and is_empty(macro_match.group(4)):
            new_mode = 'any'
        elif macro_match and not is_empty(macro_match.group(4)):
            new_mode = 'multiline_define'
        else:
            new_mode = 'any'
    return matches, new_mode


def test_split_dm():
    session = Session()
    counter = 0
    infile = './testinput/testcode/document.dm'
    for elem in split_dm_file(infile):
        processed_item = final_process_split(elem, infile, counter)
        process_and_save_each(processed_item, session)
        print(elem)
        print(processed_item)
        counter = counter + len(elem)


def matches_proc_verb_or_class(line):
    return re.match(r'^\s*(/(\w+/)*)(\w+)\s*$', line) or re.match(
        r'^\s*(/(\w+/)+)proc/(\w+)\((.+)\)\s*$', line) or re.match(
        r'^\s*(/(\w+/)+)(\w+)\((.+)\)\s*$', line) or re.match(
        r'^\s*#undef\s*([A-Z_]+)\s*(//.+)?$', line
    )


# function 2 takes the filename & where it was in the tree
# if the file is *.dm it opens up the file & splits it into seperate items via fn 2.5
# fn 2.5 = split_dm_file
def split_dm_file(instring):
    objFile_loop = open(instring, "r")
    list_of_lists = []
    new_list_exp = []
    counter = 0
    current_mode = 'any'
    for line in objFile_loop:
        counter = counter + 1
        (matches, current_mode) = determine_regex_use(line, current_mode)
        if matches:
            if new_list_exp:
                list_of_lists.append(new_list_exp)
            new_list_exp = [line]
        else:
            new_list_exp.append(line)
            # print(line)
        # print(line)
    # print(list_of_lists)
    # print(counter)
    if new_list_exp:
        list_of_lists.append(new_list_exp)
    objFile_loop.close()
    return list_of_lists


# if theres more than one item, it creates a new folder w/ the name of the old file.
# then it passes each of the split items along wit the name/path of the new folder
# ...to function3
# fn2 = apply_conversion_to_file
# def apply_conversion_to_file(inpath, outpath):
#     my_list = split_dm_file(inpath)
#     for list in my_list:
#         process_and_save_result(list, outpath, 1)
#     pass


# function3 takes a split item(string?) and a path as inputs
# first, it takes the /obj/whatever/whatever string, and saves it as a var.
# then it searches the 'already completed' hashmap/table/whatever for that string.
# if there is no result it creates a godot file (.gd) and adds the result of applying fn4.
# ...and then
# if there is a result, it runs fn5 on the split item & the result_path

# def process_and_save_result(spl, path, db):
#     savepath = Path(path)
#     finalsplit = final_process_split(spl)
#     # process and save to database
#     # process_and_save_to_database(finalsplit)
# 
#     # savetxt = '/n'.join(finalsplit)
#     # savepath.write_txt(savetxt)
#     pass


# def process_and_save_to_database(list_of_byond_items, session):
#     # session = Session()
#     for elem in list_of_byond_items:
#         session.add(elem)
#     session.commit()
#     pass


#     write class string to new file in output/path/new name.gd


class GdOutput(object):
    """docstring for GdOutput."""
    gd_class_name = ""
    orig_inherit_tree = ""
    path_original_file = ""
    path_new_file = ""
    class_extends = ""
    list_of_class_vars_n_consts = ""
    list_of_functions = ""

    def __init__(self, arg):
        super(GdOutput, self).__init__()
        self.arg = arg


def process_and_save_each(item, session):
    local_object = session.merge(item)
    session.add(local_object)
    session.commit()


# TODO: create a wrapper that takes the results of final_process_split and saves it into the sqlite database
# Check for whether its adding an existing class?
# Model inheritance in DB?
# idea: just rewrite all byond code to have no possible out of file experiences?
# Then process mappings reg? (meh)
# TODO: macros?

def test_apply_conversion_to_file(infile, input_dir, outfile, session):
    # initialize_db()
    split = split_dm_file(infile)
    # processed_classes = map(lambda a: final_process_split(a, infile), split)
    counter = 0
    for a in split:
        process_and_save_each(
            final_process_split(a, infile, counter),
            session
        )
        counter = counter + len(a)
    # process_and_save_to_database(processed_classes, session)
    convert_from_database_to_output(input_dir, outfile)
    pass


# def process_object():
#     return
#
#
# def process_proc():
#     return
#
#
# def process_verb():
#     return



# fn5 combines the 2 entries.

# watch out for global procs?
# watch out for . = ..()? replace ..() with gdscript's .procname() syntax figure out single . later...
# possibly 'parent' has different meaning in this context?
# datum.dm inher by everything?
# obj variables indicated w/ objectname/var/varname
# src = 'this' for verb refs
# usr keyword = the current user
# warn about <<, may cause compile w/o runtime success (works diff in both langs)
# remove list(stuff) or replace?
# can also define by var slash inside procs and w/ var/const/varname
# datum & friends are just objects defined at the root!

# paths have 2 references in dm, create & supply types.
# paths can also work via : or . operators

# funtion taking 2 inputs in-folder & out-folder name.
# first, take a tree of all the items in in-folder
# second, submit to function2 the filename & where it was in the tree.
def map_files_from(in_folder, out_folder):
    # initialize_db()
    for filename in Path(in_folder).glob('**/*.dm'):
        # p = filename.relative_to(in_folder)
        # pt = Path(out_folder) / p
        # out_dir = pt.parent / pt.name.replace(".dm", "")
        # out_dir.mkdir(parents=True, exist_ok=True)
        # final_output_file = out_dir / ("madeupNewFile" + ".gd")
        # print("name: ", pt.name)
        # print("parts: ", pt.parts)
        # print("anchor: ", pt.anchor)
        # print("replace: ", pt.name.replace(".dm", ""))
        # print(stringcase.pascalcase("maid"))
        # print("pt: ", pt)
        print(filename)
    pass

# finally this is for testing:

# split_dm_file("./document.dm", initialize_db())
# map_files_from('testinput', 'testoutput', initialize_db())
