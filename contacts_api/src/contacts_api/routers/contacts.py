from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud
from ..schemas import ContactCreate, Contact 
from ..database import get_db  

router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.post('/', response_model=Contact)
def create_contacts(contact: ContactCreate, db: Session = Depends(get_db)):
    return crud.create_contact(db, contact)

@router.get("/", response_model=list[Contact])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_contacts(db, skip, limit)
