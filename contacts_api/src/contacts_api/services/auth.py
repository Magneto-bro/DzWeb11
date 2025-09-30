from typing import Optional

from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from ..database import get_db
from ..repository import users as repository_users


class Auth:
    """
    Клас для роботи з автентифікацією користувачів:
    хешування паролів, створення та перевірка JWT токенів.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = "secret_key"
    ALGORITHM = "HS256"
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

    def verify_password(self, plain_password, hashed_password):
        """
        Перевіряє, чи введений пароль збігається з хешованим.

        Параметри:
        - plain_password (str): Звичайний (незахешований) пароль користувача.
        - hashed_password (str): Хешований пароль, збережений у базі.

        Повертає:
        - bool: True, якщо паролі збігаються, інакше False.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Хешує пароль користувача.

        Параметри:
        - password (str): Звичайний пароль.

        Повертає:
        - str: Хешований пароль.
        """
        return self.pwd_context.hash(password)

    # define a function to generate a new access token
    async def create_access_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Створює JWT access-токен.

        Параметри:
        - data (dict): Дані для включення у токен (наприклад email).
        - expires_delta (float, optional): Тривалість дії токена у секундах.
          Якщо None — стандартно 15 хв.

        Повертає:
        - str: Зашифрований access-токен.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_access_token

    # define a function to generate a new refresh token
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Створює JWT refresh-токен.

        Параметри:
        - data (dict): Дані для включення у токен (наприклад email).
        - expires_delta (float, optional): Тривалість дії токена у секундах.
          Якщо None — стандартно 7 днів.

        Повертає:
        - str: Зашифрований refresh-токен.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Декодує refresh-токен і перевіряє його дійсність.

        Параметри:
        - refresh_token (str): JWT refresh-токен.

        Повертає:
        - str: email користувача, якщо токен валідний.

        Викидає:
        - HTTPException 401: якщо токен недійсний або scope неправильний.
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'refresh_token':
                email = payload['sub']
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Invalid scope for token')
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        Отримує поточного користувача з JWT access-токена.

        Параметри:
        - token (str): JWT access-токен.
        - db (Session): Сесія бази даних.

        Повертає:
        - User: Об'єкт користувача.

        Викидає:
        - HTTPException 401: якщо токен недійсний.
        - HTTPException 403: якщо email не підтверджено.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            # Decode JWT
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload['scope'] == 'access_token':
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = await repository_users.get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        if not user.is_verified: 
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Action forbidden."
        )


        return user
    
    async def create_email_token(self,data:dict,expires_delta:Optional[float] = None):
        """
        Створює токен для підтвердження email.

        Параметри:
        - data (dict): Дані для включення у токен (наприклад email).
        - expires_delta (float, optional): Тривалість дії токена у секундах.
          Якщо None — стандартно 24 години.

        Повертає:
        - str: Зашифрований email-токен.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds= expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(hours=24)
        to_encode.update({"iat":datetime.utcnow(),"exp":expire,"scope":"email_verify"})
        encoded = jwt.encode(to_encode,self.SECRET_KEY,algorithm=self.ALGORITHM)
        return encoded
    
    async def decode_email_token(self,token:str):
        """
        Декодує токен для підтвердження email.

        Параметри:
        - token (str): JWT email-токен.

        Повертає:
        - str: email користувача, якщо токен валідний.

        Викидає:
        - HTTPException 401: якщо токен недійсний або scope неправильний.
        """
        try:
            payload = jwt.decode(token,self.SECRET_KEY,algorithms=[self.ALGORITHM])
            if payload.get("scope") !="email_verify":
                raise HTTPException(status_code=401,detail="Invalid token scope")
            return payload.get("sub")
        except JWTError            :
            raise HTTPException(status_code=401,detail="Could not validate token")
auth_service = Auth()

