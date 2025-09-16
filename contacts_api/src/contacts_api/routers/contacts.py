from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud
from ..schemas import ContactCreate, Contact 
from ..database import get_db 
from .. import models, schemas
from fastapi import HTTPException
import asyncio
from ..services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])

@router.post('/', response_model=Contact)
async def create_contact(
    body: ContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user)  
):  
    return crud.create_contact(body, db, current_user)


@router.get("/", response_model=list[Contact])
def read_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(auth_service.get_current_user)):
    return crud.get_contacts_by_user(db, current_user.id, skip, limit)

@router.get("/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = crud.get_contact(db, contact_id)  
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id}", response_model=schemas.Contact)
def update_contact(
    contact_id: int,
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user)
):
    db_contact = crud.get_contact(db, contact_id)
    if not db_contact or db_contact.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found or not authorized")
    return crud.update_contact(db, contact_id, contact)

@router.delete("/{contact_id}", response_model=schemas.Contact)
def delete_contact(    
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user)
):
    db_contact = crud.get_contact(db, contact_id)
    if not db_contact or db_contact.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found or not authorized")
    return crud.delete_contact(db, contact_id)