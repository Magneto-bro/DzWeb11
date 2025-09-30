from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import contacts ,auth
from .utils.limiter import limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
original =[
    "http://localhost:8000",
     "http://127.0.0.1:5500",
]

app =FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = original,
    allow_credentials =True,
    allow_methods =["*"],
    allow_headers =["*"],
)

app.state.limiter =limiter

app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(contacts.router)
app.include_router(auth.router)
