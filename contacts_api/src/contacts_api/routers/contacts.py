from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud
from ..schemas import ContactCreate, Contact 
from ..database import get_db 
from .. import models, schemas
from fastapi import HTTPException

router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.post('/', response_model=Contact)
def create_contacts(contact: ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact)

@router.get("/", response_model=list[Contact])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_contacts(db, skip, limit)

@router.get("/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = crud.get_contact(db, contact_id)  # окремий метод для одного контакту
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=schemas.Contact)
def update_contact(contact_id: int, contact: schemas.ContactCreate, db: Session = Depends(get_db)):
    db_contact = crud.update_contact(db, contact_id, contact)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@router.delete("/{contact_id}", response_model=schemas.Contact)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    db_contact = crud.delete_contact(db, contact_id)
    if not db_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact