from sqlalchemy.orm import Session
from . import models, schemas

def get_contacts(db:Session,skip: int = 0, limit:int =100):
    return db.query(models.Contacts).offset(skip).limit(limit).all()


def create_contact(db: Session, contact: schemas.ContactBase):
    db_contact = models.Contacts(**contact.dict())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contact(db: Session, contact_id: int):
    return db.query(models.Contacts).filter(models.Contacts.id == contact_id).first()

def update_contact(db:Session,contact_id:int,contact:schemas.ContactCreate):
    db_contact = db.query(models.Contacts).filter(models.Contacts.id==contact_id).first()
    if db_contact:
        for key, value in contact.dict().items():
            setattr(db_contact,key,value)
        db.commit()
        db.refresh(db_contact)
    return db_contact

def delete_contact(db:Session,contact_id:int):
    db_contact = db.query(models.Contacts).filter(models.Contacts.id==contact_id).first()
    if db_contact:
        db.delete(db_contact)
        db.commit()
    return db_contact