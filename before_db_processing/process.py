import re

import stringcase

from initialize_db import Session
from byond_orm import ByondProc, ByondVerb, ByondClass, ByondMacro, ByondUndefMacro


def final_process_split(insplit, infile="", line_number=0):
    line = insplit[0]
    remaining_lines = ''.join(insplit[1:])

    # if var/proc/other top level
    if re.match("^\\s*(/(\\w+/)*)(\\w+)$", line):
        match_value = re.search("^\\s*(/(\\w+/)*)(\\w+)$", line)
        (full_heritage, direct_inheritor, item_name) = match_value.groups()
        result = byond_class_with_proper_name(full_heritage, infile, item_name, remaining_lines, line_number)
    # if proc
    elif re.match("^\\s*(/(\\w+/)+)proc/(\\w+)\\((.+)\\)", line):
        match_value = re.search("^\\s*(/(\\w+/)+)proc/(\\w+)\\((.+)\\)", line)
        (full_heritage, item_name_plus_slash, proc_name, proc_args) = match_value.groups()
        result = ByondProc(
            full_heritage_id=full_heritage + proc_name + '/',
            arguments=proc_args,
            line_number=line_number,
            path_first_found_in=infile,
            name=proc_name,
            text=remaining_lines,
            byondclass_id=full_heritage
        )
        # convert the types & args inside verb parentheses
        # convert each of the items inside the statement
    # if verb
    elif re.match("^\\s*(/(\\w+/)+)(\\w+)\\((.+)\\)", line):
        match_value = re.search("^\\s*(/(\\w+/)+)(\\w+)\\((.+)\\)", line)
        (full_heritage, item_name_plus_slash, proc_name, proc_args) = match_value.groups()
        result = ByondVerb(
            full_heritage_id=full_heritage + proc_name + '/',
            arguments=proc_args,
            line_number=line_number,
            path_first_found_in=infile,
            name=proc_name,
            text=remaining_lines,
            byondclass_id=full_heritage
        )
    elif re.match(
            r'^\s*#define\s+([A-Z_]+)(?:\(((?:\w+\s*,?\s*)+)\))?(?:\s+((?:[^\\/\n]|/(?!/))+))?(\\?)(//.+)?$',
            line):
        match_value = re.search(
            r'^\s*#define\s+([A-Z_]+)(?:\(((?:\w+\s*,?\s*)+)\))?(?:\s+((?:[^\\/\n]|/(?!/))+))?(\\?)(//.+)?$',
            line
        )
        (macro_name, args_list, macro_value, is_multiline, comment) = match_value.groups('')
        result = ByondMacro(
            name=macro_name,
            comment=comment,
            arguments=args_list,
            value=macro_value,
            path_first_found_in=infile,
            extra_text=remaining_lines,
            line_number=line_number
        )
    elif re.match(
            r'^\s*#undef\s*([A-Z_]+)\s*(//.+)?$',
            line):
        match_value = re.search(
            r'^\s*#undef\s*([A-Z_]+)\s*(//.+)?$',
            line
        )
        (macro_name, comment) = match_value.groups('')
        result = ByondUndefMacro(
            name=macro_name,
            comment=comment,
            path_first_found_in=infile,
            extra_text=remaining_lines,
            line_number=line_number
        )
    # if neither
    else:
        pass
    return result


# group 1 name of the macro
# group 2 is the args list (if it exists)
# group 3 value of the macro
# group 4 is whether its multiline (if it exists)
# group 5 is the comment (if it exists)


def byond_class_with_proper_name(full_heritage: str, infile: str, item_name: str, remaining_lines: str, line_number):
    # TODO: ensure the 'extends' value is good and present
    # In order to do this: search for ByondClasses with this item's 'full_heritage' as their
    # full_heritage_id. Then, get the 'new_name' from that item and add it.
    # if the item to be inherited from hasn't been added, simply add 'placeholder' as the newname.
    # also consider doing a search and update for any already done that inherit from this item?
    # Also: consider checking if any procs or verbs for this process have already been added?
    # also: check that name hasn't been used.
    session = Session()
    this_items_full_heritage_id = full_heritage + item_name + '/'
    extends_name: (str, str) = session.query(ByondClass.new_name, ByondClass.full_heritage_id).filter(
        ByondClass.full_heritage_id == full_heritage).one_or_none()
    (extends_name_value, extending_inheritance) = ('placeholder', '') if (extends_name is None) else extends_name
    new_name = stringcase.pascalcase(item_name)
    print("extends name: ", extends_name)
    ensure_unique_name = session.query(ByondClass).filter(
        ByondClass.name == item_name
    ).all()
    counter = 0
    other: ByondClass
    for other in ensure_unique_name:
        if other.full_heritage_id == this_items_full_heritage_id:
            other.text = other.text + "\n# from another locale\n" + remaining_lines
            session.commit()
            return other
        counter = counter + 1
        new_name = stringcase.pascalcase(item_name) + str(counter)
    print("new name: ", new_name)
    return ByondClass(full_heritage_id=this_items_full_heritage_id,
                      name=item_name,
                      class_extends=extends_name_value,
                      line_number=line_number,
                      new_name=new_name,
                      path_first_found_in=infile,
                      text=remaining_lines,
                      verbs=[], procs=[])


def to_other_byond(other, other_text):
    return ByondClass(full_heritage_id=other.full_heritage_id,
                      name=other.name,
                      class_extends=other.class_extends,
                      new_name=other.new_name,
                      path_first_found_in=other.path_first_found_in,
                      text=other_text,
                      verbs=other.verbs, procs=other.procs)
