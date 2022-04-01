from contextlib import contextmanager
from enum import Enum, auto
from os import getenv as config
from pathlib import Path
from typing import Callable, ContextManager

import sqlalchemy
from extra.custom_logger import CustomizeLogger
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm.session import Session

ROOT_DIR = Path(__file__).parent
LOGGER_CONFIG = ROOT_DIR / "logger_config.json"
ENV_PATH = ROOT_DIR / ".env"
API_PREFIX = "/api"
API_SCHOOL_PREFIX = "/school"
API_CORPUS_PREFIX = "/corpus"
API_CABINET_PREFIX = "/cabinet"
API_SUBCLASS_PREFIX = "/subclass"
API_TEACHER_PREFIX = "/teacher"
API_STUDENT_PREFIX = "/student"
API_PARENT_PREFIX = "/parent"
API_LESSON_PREFIX = "/lesson"
API_LESSON_NUMBER_PREFIX = "/lessontimetable"
API_INFO_PREFIX = "/info"
API_REGISTRATION_PREFIX = "/registration"
API_LESSON_GETTER_PREFIX = "/lesson/get"
API_ROLE_MANAGEMENT_PREFIX = "/rolemanagement"
API_ID_GETTER_PREFIX = "/idgetter"
API_ANNOUNCEMENTS_PREFIX = "/announcements"
API_STATISTICS_PREFIX = "/stats"

API_AUTH_PREFIX = "/auth"
API_SERVICE_AUTH_PREFIX = "/service"

MAX_LEVENSHTEIN_RESULTS = 5
MAX_HISTORY_RESULTS = 10

API_HOST = "api"
API_PORT = 8009

TRANSMITTER_HOST = "transmitter"
TRANSMITTER_PORT = 8998

DATABASE_USER = config("DATABASE_USER")
DATABASE_PASSWORD = config("DATABASE_PASSWORD")
DATABASE_HOST = config("DATABASE_HOST")
DATABASE_PORT = config("DATABASE_PORT")
DATABASE_NAME = config("DATABASE_NAME")
WEBSITE_HOST = config("WEBSITE_HOST")
WEBSITE_PORT = config("WEBSITE_PORT")
DATABASE_ENGINE = "mariadb"
DATABASE_CONNECTOR = "mariadbconnector"

JWT_SECRET = config("JWT_SECRET")
JWT_ALGORITHM = "HS256"

JWT_SERVICE_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_SERVICE_REFRESH_TOKEN_EXPIRE_MINUTES = 15 * 24 * 60
JWT_USER_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_USER_REFRESH_TOKEN_EXPIRE_MINUTES = 15 * 24 * 60


DEFAULT_LOGGER = CustomizeLogger.make_logger(LOGGER_CONFIG)


BASIC_STATUS_MAX_CHILDREN = 1

__connect_address__ = (
    "{engine}+{connector}://{user}:{password}@{host}:{port}/{name}".format(
        engine=DATABASE_ENGINE,
        connector=DATABASE_CONNECTOR,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        host=DATABASE_HOST,
        port=DATABASE_PORT,
        name=DATABASE_NAME,
    )
)

ENGINE = create_engine(__connect_address__)
DEFAULT_LOGGER.debug(f"Connecting to database with {__connect_address__}")
SESSION_FACTORY: Callable[..., ContextManager[Session]] = scoped_session(
    sessionmaker(bind=ENGINE, autocommit=False)
)


class Access(Enum):
    Admin = 5
    Telegram = 4
    Parser = 3
    Website = 2


def get_session():
    session: Session = SESSION_FACTORY()
    try:
        for _ in range(10):
            try:
                session.execute("SELECT 1")
            except sqlalchemy.exc.InterfaceError as error:  # type: ignore
                session: Session = SESSION_FACTORY()
                continue
            else:
                yield session
                break
    except HTTPException as error:
        raise error from error
    except Exception as error:
        DEFAULT_LOGGER.error(error)
        session.rollback()
        raise HTTPException(status_code=500, detail="SQL Error")
    finally:
        session.close()
