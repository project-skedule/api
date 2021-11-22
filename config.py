from os import getenv as config
from pathlib import Path

# import zmq
# import zmq.asyncio
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from extra.custom_logger import CustomizeLogger

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
LEVENSHTEIN_RESULTS = 5
API_HOST = "172.0.0.2"
# if changed here, should also be changed in docker file and docker compose
API_PORT = 8009
# ZMQ_PORT = 8199
# load_dotenv(dotenv_path=ENV_PATH)
DATABASE_USER = config("DATABASE_USER")
DATABASE_PASSWORD = config("DATABASE_PASSWORD")
DATABASE_HOST = config("DATABASE_HOST")
DATABASE_PORT = config("DATABASE_PORT")
DATABASE_NAME = config("DATABASE_NAME")
DATABASE_ENGINE = "mariadb"
DATABASE_CONNECTOR = "mariadbconnector"
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
SESSION_FACTORY = scoped_session(sessionmaker(bind=ENGINE))
# ZMQ_CONTEXT = zmq.asyncio.Context()
# ZMQ_SOCKET = ZMQ_CONTEXT.socket(zmq.PULL)
# ZMQ_SOCKET.bind(f"tcp://{API_HOST}:{ZMQ_PORT}")
