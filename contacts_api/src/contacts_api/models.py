from sqlalchemy import Column ,String ,Integer,Date,func ,ForeignKey
from .database import Base
from sqlalchemy.orm import  relationship
from sqlalchemy.sql.sqltypes import DateTime
class Contacts(Base):
    __tablename__  ='contacts'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String , nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String,nullable=False)
    birthday = Column(Date , nullable=True)
    about = Column(String(250))

    owner_id =Column(Integer,ForeignKey("users.id"),nullable=False)

    owner = relationship("User",back_populates="contacts")
    


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)

    contacts = relationship("Contacts",back_populates="owner")
    