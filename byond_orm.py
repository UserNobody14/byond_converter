from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey

Base = declarative_base()


class ByondVerb(Base):
    __tablename__ = 'byond_verb'

    # id = Column(Integer, primary_key=True)
    full_heritage_id = Column(String, primary_key=True)
    name = Column(String)
    byondclass_id = Column(String, ForeignKey('byond_class.full_heritage_id'))
    line_number = Column(Integer)
    path_first_found_in = Column(String)
    arguments = Column(String)
    # vars and other items?
    text = Column(String)
    by_class = relationship("ByondClass", back_populates="verbs")

    def __repr__(self):
        return "<ByondVerb(full_heritage_id='%s', name='%s', text='%s')>" % \
               (self.full_heritage_id, self.name, self.text)


class ByondProc(Base):
    __tablename__ = 'byond_proc'

    # id = Column(Integer, primary_key=True)
    full_heritage_id = Column(String, primary_key=True)
    name = Column(String)
    byondclass_id = Column(String, ForeignKey('byond_class.full_heritage_id'))
    line_number = Column(Integer)
    path_first_found_in = Column(String)
    arguments = Column(String)
    # vars and other items?
    text = Column(String)
    by_class = relationship("ByondClass", back_populates="procs")

    def __repr__(self):
        return "<ByondProc(full_heritage_id='%s', name='%s', text='%s')>" % \
               (self.full_heritage_id, self.name, self.text)


class ByondClass(Base):
    __tablename__ = 'byond_class'

    # id = Column(Integer, primary_key=True)
    full_heritage_id = Column(String, primary_key=True)
    # the original name (plain, lower case)
    name = Column(String)
    verbs = relationship("ByondVerb", order_by=ByondVerb.full_heritage_id, back_populates="by_class")
    procs = relationship("ByondProc", order_by=ByondProc.full_heritage_id, back_populates="by_class")
    # vars and other items?
    text = Column(String)
    line_number = Column(Integer)
    # updated name(Unique):
    new_name = Column(String)
    # name of item being extended:
    class_extends = Column(String)
    # path where this class was first found.
    path_first_found_in = Column(String)

    def __repr__(self):
        return "<ByondClass(full_heritage_id='%s', name='%s', text='%s')>" % \
               (self.full_heritage_id, self.name, self.text)


class ByondMacro(Base):
    __tablename__ = 'byond_macro'

    id = Column(Integer, primary_key=True)
    # full_heritage_id = Column(String, primary_key=True)
    name = Column(String)
    path_first_found_in = Column(String)
    line_number = Column(Integer)
    # byondclass_id = Column(String, ForeignKey('byond_class.full_heritage_id'))
    arguments = Column(String)
    value = Column(String)
    extra_text = Column(String)
    # vars and other items?
    comment = Column(String)
    # by_class = relationship("ByondClass", back_populates="verbs")

    def __repr__(self):
        return "<ByondMacro(id='%s', name='%s', comment='%s', args='%s')>" % \
               (self.id, self.name, self.comment, self.arguments)


class ByondUndefMacro(Base):
    __tablename__ = 'byond_undef_macro'

    id = Column(Integer, primary_key=True)
    # full_heritage_id = Column(String, primary_key=True)
    name = Column(String)
    path_first_found_in = Column(String)
    line_number = Column(Integer)
    # byondclass_id = Column(String, ForeignKey('byond_class.full_heritage_id'))
    # arguments = Column(String)
    # value = Column(String)
    extra_text = Column(String)
    # vars and other items?
    comment = Column(String)
    # by_class = relationship("ByondClass", back_populates="verbs")

    def __repr__(self):
        return "<ByondUndefMacro(id='%s', name='%s', comment='%s')>" % \
               (self.id, self.name, self.comment)

# macro additions:
# ^\h*#define\h+([A-Z_]+)(?:\(((?:\w+\s*,?\s*)+)\))?(?:\h+((?:[^\\\/\n]|\/(?!\/))+))?(\\?)(\/\/.+)?$
# group 1 name of the macro
# group 2 is the args list (if it exists)
# group 3 value of the macro
# group 4 is whether its multiline (if it exists)
# group 5 is the comment (if it exists)


class ByondComment(Base):
    __tablename__ = 'byond_comment'

    id = Column(Integer, primary_key=True)
    # full_heritage_id = Column(String, primary_key=True)
    # name = Column(String)
    path_first_found_in = Column(String)
    line_number = Column(Integer)
    # # byondclass_id = Column(String, ForeignKey('byond_class.full_heritage_id'))
    # arguments = Column(String)
    # value = Column(String)
    # extra_text = Column(String)
    # vars and other items?
    comment = Column(String)
    # by_class = relationship("ByondClass", back_populates="verbs")

    def __repr__(self):
        return "<ByondComment(line_num='%s', comment='%s')>" % \
               (self.line_number, self.comment)

# verbseeker regex 0.0.1
#
#
# ^\s*(\/(\w+\/)+)(\w+)\((.+)\)
#
#
# group 1 is full heritage
#
# group 2 = irrelevant
#
# group 3 = procname
#
# group 4 = arguments being supplied to said proc.
#
#
# procseeker regex 0.0.1
#
#
# ^\s*(\/(\w+\/)+)proc\/(\w+)\((.+)\)
#
#
# group 1 is full heritage
#
# group 2 itemname plus a slash
#
# group 3 procname
#
# group 4 procargs
#
#
# objectseeker 0.0.1
#
#
# ^\s*(\/(\w+\/)*)(\w+)$
#
#
# group 1 is full heritage
#
# group 2 is second to last
#
# group 3 is last/object name.