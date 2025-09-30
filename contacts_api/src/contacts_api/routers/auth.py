from typing import List

from fastapi import APIRouter, HTTPException,File, Depends, status, Security ,UploadFile
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import UserModel, UserResponse, TokenModel
from ..repository import users as repository_users
from ..services.auth import auth_service

from fastapi import BackgroundTasks
from ..services.auth import auth_service
from ..utils.email_sender import send_verification_email
from urllib.parse import urlencode

from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

import cloudinary.uploader
from ..services import cloudinary_config

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()

BASE_DIR = Path(__file__).resolve().parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(BASE_DIR)), autoescape=True)


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(body: UserModel, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """ 
    Реэстрація користувача
    Argus: 
        body (ContactCreate): Дані нового контакту.
        background_tasks (BackgroundTasks): Список фонових задач .
        db (Session, optional): Поточний користувач.
        

    Returns:
        dict: Інформація про користувача та повідомлення про перевірку пошти.

    Raises:
        HTTPException: 409, якщо користувач з таким email вже існує.

        """
    
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)

    
    token = await auth_service.create_email_token(data={"sub": new_user.email})
    
    verify_link = f"http://localhost:8000/auth/verify?token={token}"   # в прод — домен

   
    background_tasks.add_task(send_verification_email, new_user.email, verify_link)

    return {"user": new_user, "detail": "User successfully created. Check email for verification"}
@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    """
    Вхід користувача (авторизація).

    Args:
        body (OAuth2PasswordRequestForm): Логін і пароль.
        db (Session, optional): Сесія бази даних.

    Returns:
        dict: JWT токени (access і refresh).

    Raises:
        HTTPException: 401, якщо email або пароль невірні.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    Оновлення токенів доступу.

    Args:
        credentials (HTTPAuthorizationCredentials): Токен авторизації.
        db (Session, optional): Сесія бази даних.

    Returns:
        dict: Нові JWT токени.

    Raises:
        HTTPException: 401, якщо refresh-токен недійсний.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get("/verify", response_class=HTMLResponse)
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Підтвердження email через токен.

    Args:
        token (str): Токен з email.
        db (Session, optional): Сесія бази даних.

    Returns:
        HTMLResponse: HTML сторінка з результатом перевірки.

    Raises:
        HTTPException: 404, якщо користувач не знайдений.
    """
    email = await auth_service.decode_email_token(token)
    user = await repository_users.get_user_by_email(email, db)

    if not user:
        return HTMLResponse(content="<h1>User not found</h1>", status_code=404)

    if not user.is_verified:
        user.is_verified = True
        db.add(user)
        db.commit()
        db.refresh(user)

    template = env.get_template("email_verify.html")
    html_content = template.render(verify_link=f"http://localhost:8000")
    return HTMLResponse(content=html_content)

@router.post("/resend-verify")
async def resend_verification(body:dict,background_tasks:BackgroundTasks,db:Session =Depends(get_db)):
    """
    Повторна відправка листа для підтвердження email.

    Args:
        body (dict): Словник з ключем "email".
        background_tasks (BackgroundTasks): Список фонових задач.
        db (Session, optional): Сесія бази даних.

    Returns:
        dict: Повідомлення про відправку листа.

    Raises:
        HTTPException: 404, якщо користувач не знайдений.
    """
    email =body.get("email")
    user = await repository_users.get_user_by_email(email,db)
    if not user:
        raise HTTPException(status_code=404)
    if user.is_verified:
        return{"detail": "Already verified"}
    token = await auth_service.create_email_token({'sub':user.email})
    verify_link = f"http://localhost:8000/api/auth/verify?token={token}"
    background_tasks.add_task(send_verification_email,user.email , verify_link )
    return {"detail": "Verification email sent"}

@router.post("/avatar")
async def update_avatar(
    file: UploadFile =File(...),
    current_user =Depends(auth_service.get_current_user),
    db: Session =Depends(get_db)
):
    """
    Оновлення аватара користувача.

    Args:
        file (UploadFile): Завантажений файл зображення.
        current_user (User): Поточний користувач.
        db (Session, optional): Сесія бази даних.

    Returns:
        dict: URL нового аватара.

    Raises:
        HTTPException: 400, якщо виникла помилка при завантаженні.
    """
    try:
        result = cloudinary_config.cloudinary.uploader.upload(
            file.file,
            folder ="avatars"
        )
        avatar_url = result.get("secure_url")
        current_user.avatar =avatar_url
        db.add(current_user)
        db.commit()
        db.refresh(current_user)

        return {"avatar_url":avatar_url}
    except Exception  as e:
        raise HTTPException(status_code=400,detail =str(e))