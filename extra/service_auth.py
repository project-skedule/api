from datetime import datetime, timedelta
from typing import List

from config import API_PREFIX, API_SERVICE_AUTH_PREFIX
from config import DEFAULT_LOGGER as logger
from config import (
    JWT_ALGORITHM,
    JWT_SECRET,
    JWT_SERVICE_ACCESS_TOKEN_EXPIRE_MINUTES,
    Access,
    get_session,
)
from extra import create_logger_dependency
from extra.api_router import LoggingRouter
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from jose import JWTError, jwt
from models import database
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

# do not user logging middlewhere here
router = APIRouter(
    prefix=API_PREFIX + API_SERVICE_AUTH_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
)
logger.info(f"Service auth router created on {API_PREFIX + API_SERVICE_AUTH_PREFIX}")

OAUTH2_SERVICE_SCHEME = OAuth2PasswordBearer(
    tokenUrl=API_PREFIX + API_SERVICE_AUTH_PREFIX + "/login",
    scheme_name="service_oauth",
    # description="Login operation to get service access token",
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    username: str
    scopes: List[str] = []


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(service_name: str, session: Session):
    return session.query(database.Service).filter_by(name=service_name).first()


def authenticate_user(service_name: str, password: str, session: Session):
    user = get_user(service_name, session)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=JWT_SERVICE_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "type": "service"})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def get_current_service(
    _: SecurityScopes,
    token: str = Depends(OAUTH2_SERVICE_SCHEME),
    session=Depends(get_session),
):

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
    user = get_user(token_data.username, session)
    if user is None:
        raise credentials_exception
    return user


class AllowLevels:
    def __init__(self, *levels: Access):
        self.levels = [level.value for level in levels]

    def __call__(self, service=Depends(get_current_service)):
        if service.access_level not in self.levels:
            raise HTTPException(
                status_code=401,
                detail="Not allowed for this service",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return True


@router.post("/login")
async def service_login(
    form_data: OAuth2PasswordRequestForm = Depends(), session=Depends(get_session)
):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(data={"sub": user.name}),
        "token_type": "Bearer",
    }
