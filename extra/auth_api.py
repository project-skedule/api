from datetime import datetime, timedelta
from uuid import uuid4

import ujson
from config import API_AUTH_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import (
    JWT_ALGORITHM,
    JWT_SECRET,
    JWT_USER_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_USER_REFRESH_TOKEN_EXPIRE_MINUTES,
    get_session,
)
from extra import create_logger_dependency
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from models import database
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

# do not user logging middlewhere here
router = APIRouter(
    prefix=API_PREFIX + API_AUTH_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
)
logger.info(f"User auth router created on {API_PREFIX + API_AUTH_PREFIX}")

OAUTH2_AUTH_SCHEME = OAuth2PasswordBearer(
    tokenUrl=API_PREFIX + API_AUTH_PREFIX + "/login",
    scheme_name="user_oauth",
    description="Login operation to get user access token",
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    username: str


class UserSchema(BaseModel):
    name: str
    surname: str
    email: EmailStr
    password: str


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(session, email: str, password: str):
    user = session.query(database.HarvestUser).filter_by(email=email).first()
    if not user:
        return None
    if not verify_password(password, user.password):
        return None
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_USER_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=JWT_USER_REFRESH_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def get_harvest_user(
    token: str = Depends(OAUTH2_AUTH_SCHEME), session=Depends(get_session)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        uuid: str = payload.get("sub")  # type: ignore
        if uuid is None:
            raise credentials_exception
        token_data = TokenData(username=uuid)
    except JWTError:
        raise credentials_exception

    user = session.query(database.HarvestUser).filter_by(uuid=uuid).first()
    if user is None:
        raise credentials_exception
    if not user.activated:
        raise credentials_exception
    if not user.logged_in:
        raise credentials_exception
    return user


@router.post("/signup")
async def signup_user(form_data: UserSchema = Body(None), session=Depends(get_session)):
    password = get_password_hash(form_data.password)
    user_uuid = str(uuid4())
    access_token = create_access_token({"sub": user_uuid, "type": "user"})
    refresh_token = create_refresh_token({"sub": user_uuid})

    candidate = (
        session.query(database.HarvestUser).filter_by(email=form_data.email).first()
    )

    if candidate is not None:
        raise HTTPException(
            status_code=401,
            detail="This email is already in use",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = database.HarvestUser(
        uuid=user_uuid,
        name=form_data.name,
        surname=form_data.surname,
        email=form_data.email,
        password=password,
        active_link="",  # TODO: link
        access_token=access_token,
        refresh_token=refresh_token,
        logged_in=True,
        activated=True,  # TODO: post
        image="",  # TODO: path
    )

    session.add(user)
    session.commit()

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "refresh_token": refresh_token,
    }


@router.post("/login")
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session=Depends(get_session),
):
    # username == email
    user = authenticate_user(session, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user.logged_in = True
    user.access_token = create_access_token(data={"sub": user.uuid})
    user.refresh_token = create_refresh_token(data={"sub": user.uuid})

    session.add(user)
    session.commit()

    return {
        "access_token": user.access_token,
        "token_type": "Bearer",
        "refresh_token": user.refresh_token,
    }


@router.post("/logout")
async def logout_user(
    user=Depends(get_harvest_user),
    session=Depends(get_session),
):
    user.logged_in = False

    session.add(user)
    session.commit()

    return {"uuid": user.uuid}


@router.post("/refresh")
async def refresh_token_user(
    user=Depends(get_harvest_user),
    session=Depends(get_session),
):
    user.access_token = create_access_token(data={"sub": user.uuid})
    session.add(user)
    session.commit()

    return {
        "access_token": user.access_token,
        "token_type": "Bearer",
        "refresh_token": user.refresh_token,
    }
