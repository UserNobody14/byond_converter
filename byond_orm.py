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
    # updated name(Unique):
    new_name = Column(String)
    # name of item being extended:
    class_extends = Column(String)
    # path where this class was first found.
    path_first_found_in = Column(String)

    def __repr__(self):
        return "<ByondClass(full_heritage_id='%s', name='%s', text='%s')>" % \
               (self.full_heritage_id, self.name, self.text)


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