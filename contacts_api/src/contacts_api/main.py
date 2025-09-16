from fastapi import FastAPI
from .routers import contacts ,auth
app =FastAPI()

app.include_router(contacts.router)
app.include_router(auth.router)
