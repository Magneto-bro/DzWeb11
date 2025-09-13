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
    