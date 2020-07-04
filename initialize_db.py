from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:', echo=True)
Session = sessionmaker(bind=engine)

