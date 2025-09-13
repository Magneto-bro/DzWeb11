from sqlalchemy import Column ,String ,Integer,Date
from .database import Base

class Contacts(Base):
    __tablename__  ='contacts'

    id = Column(Integer , primary_key=True)
    name = Column(String , nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String,nullable=False)
    birthday = Column(Date , nullable=True)
    about = Column(String(250))
    