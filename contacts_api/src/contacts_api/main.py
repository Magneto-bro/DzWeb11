from fastapi import FastAPI
from .routers import contacts
app =FastAPI()

app.include_router(contacts.router)