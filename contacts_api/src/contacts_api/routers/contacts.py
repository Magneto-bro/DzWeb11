from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import crud
from ..schemas import ContactCreate, Contact 
from ..database import get_db 
from .. import models, schemas
from fastapi import HTTPException
import asyncio
from ..services.auth import auth_service
from ..utils.limiter import limiter
from fastapi import Request
router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.post('/', response_model=Contact)
@limiter.limit("5/minute")  
async def create_contact(
    request: Request,
    body: ContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_service.get_current_user)  
):  
    """
    Створює контакт у базі даних з обмеженням по кількості запитів.

    Args:
        request (Request): HTTP-запит.
        body (ContactCreate): Дані нового контакту.
        db (Session, optional): Сесія бази даних.
        current_user (models.User, optional): Поточний користувач.

    Returns:
        Contact: Створений контакт.
    """
    return crud.create_contact(body, db, current_user)

@router.get("/{contact_id}", response_model=schemas.Contact)
def read_contact(contact_id: int, db: Session = Depends(get_db)):
    """
    Отримує контакт за його ID.

    Args:
        contact_id (int): ID контакту.
        db (Session, optional): Сесія бази даних.

    Returns:
        Contact: Знайдений контакт.

    Raises:
        HTTPException: 404, якщо контакт не знайдено.
    """
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
    """
    Оновлює створиного контата в базі даних.
    Args:
        contact_id (int): id контакту
        contact (ContactCreate): контакт
        db (Session, optional): сесія бази даних
        current_user (models.User, optional): поточний користувач
    Returns:
        Contact: Оновлений контакт
    Raises:
        HTTPException 404: якщо контакт не знайдено
    """
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
    """
    Видаляє створиного контакту.

    Args:
        body (ContactCreate): дані нового контакту
        db (Session, optional): сесія бази даних
        current_user (models.User, optional): поточний користувач

    Returns:
    - Contact: видалає контакт
    Raises:
        HTTPException 404: якщо контакт не знайдено
    """
    db_contact = crud.get_contact(db, contact_id)
    if not db_contact or db_contact.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found or not authorized")
    return crud.delete_contact(db, contact_id)