from models import database
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException
from datetime import datetime, timedelta
from config import (
    DEFAULT_LOGGER as logger,
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_SECRET,
    OAUTH2_SCHEME,
    JWT_ALGORITHM,
    API_TOKEN_URl,
    get_session,
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    username: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    with get_session() as session:
        return session.query(database.OAuthUsers).filter_by(name=username).first()


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(OAUTH2_SCHEME)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if not isinstance(payload, dict):
            raise credentials_exception
        username: str = payload.get("sub")  # type: ignore
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user
