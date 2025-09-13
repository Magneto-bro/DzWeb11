from pydantic import BaseModel
from datetime import date
from typing import Optional


class ContactBase(BaseModel):
    name: str
    email: str
    phone: str
    birthday: Optional[date] = None
    about: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class Contact(ContactBase):
    id: int

    model_config = {
        "from_attributes": True
    }
