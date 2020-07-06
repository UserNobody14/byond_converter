from byond_orm import ByondUndefMacro, ByondMacro, ByondProc, ByondVerb, ByondClass
from initialize_db import Session


def extract_effected_lists(macro: ByondMacro, undef_line_number: int):
    session = Session()
    # given a ByondMacro and a ByondUndefMacro pair, get all procs that could have been affected
    proc_list = session.query(ByondProc).filter(ByondProc.line_number > macro.line_number,
                                                ByondProc.line_number < undef_line_number,
                                                ByondProc.path_first_found_in == macro.path_first_found_in
                                                ).order_by(ByondProc.line_number)
    # given a ByondMacro and a ByondUndefMacro pair, get all verbs that could have been affected
    verb_list = session.query(ByondVerb).filter(ByondVerb.line_number > macro.line_number,
                                                ByondVerb.line_number < undef_line_number,
                                                ByondVerb.path_first_found_in == macro.path_first_found_in
                                                ).order_by(ByondVerb.line_number)
    # given a ByondMacro and a ByondUndefMacro pair, get all classes that could have been affected
    class_list = session.query(ByondClass).filter(ByondClass.line_number > macro.line_number,
                                                 ByondClass.line_number < undef_line_number,
                                                 ByondClass.path_first_found_in == macro.path_first_found_in
                                                 ).order_by(ByondClass.line_number)
#     TODO: make something that checks if the relevant macro refers to something simple (most should) and
# just adds them to the relevant class as a constant.


def get_macro_undef_pairs():
    session = Session()
    macro_undef_pairs = session.query(ByondMacro, ByondUndefMacro.line_number).join(
        ByondMacro,
        ByondMacro.name == ByondUndefMacro.name,
    ).filter(
        ByondUndefMacro.line_number > ByondMacro.line_number,
        ByondUndefMacro.path_first_found_in == ByondMacro.path_first_found_in
    )
    for macro, undef in macro_undef_pairs:
        print('pair: ')
        print(macro)
        print(undef)
