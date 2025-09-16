from sqlalchemy.orm import Session
from . import models, schemas
from .schemas import ContactCreate, Contact 
def get_contacts(db:Session,skip: int = 0, limit:int =100):
    return db.query(models.Contacts).offset(skip).limit(limit).all()


def create_contact(body: ContactCreate, db: Session, current_user: models.User):
    new_contact = models.Contacts(
        name=body.name,
        email=body.email,
        phone=body.phone,
        birthday=body.birthday,
        about=body.about,
        owner_id=current_user.id 
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


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
def get_contacts_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Contacts).filter(models.Contacts.owner_id == user_id).offset(skip).limit(limit).all()
