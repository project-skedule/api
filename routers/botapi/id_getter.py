# type: ignore

import valid_db_requests as db_validated
from api_types import ID
from config import API_ID_GETTER_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import Access, get_session
from extra import create_logger_dependency
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels
from extra.tags import (
    CABINET,
    CORPUS,
    LESSON,
    LESSON_NUMBER,
    SCHOOL,
    SUBCLASS,
    TEACHER,
)
from fastapi import APIRouter, Depends
from models.bot import item

allowed = AllowLevels(Access.Admin, Access.Telegram, Access.Parser)

router = APIRouter(
    prefix=API_PREFIX + API_ID_GETTER_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger)), Depends(allowed)],
    route_class=LoggingRouter,
)
logger.info(f"ID getter router created on {API_PREFIX+API_ID_GETTER_PREFIX}")


@router.get("/subclass/{id}", tags=[SUBCLASS], response_model=item.Subclass)
async def get_subclass(id: ID, session=Depends(get_session)):
    return item.Subclass.from_orm(db_validated.get_subclass_by_id(session, id))


@router.get("/teacher/{id}", tags=[TEACHER], response_model=item.Teacher)
async def get_teacher(id: ID, session=Depends(get_session)):
    return item.Teacher.from_orm(db_validated.get_teacher_by_id(session, id))


@router.get("/school/{id}", tags=[SCHOOL], response_model=item.School)
async def get_school(id: ID, session=Depends(get_session)):
    return item.School.from_orm(db_validated.get_school_by_id(session, id))


@router.get("/corpus/{id}", tags=[CORPUS], response_model=item.Corpus)
async def get_corpus(id: ID, session=Depends(get_session)):
    return item.Corpus.from_orm(db_validated.get_corpus_by_id(session, id))


@router.get("/lesson/{id}", tags=[LESSON], response_model=item.Lesson)
async def get_lesson(id: ID, session=Depends(get_session)):
    return item.Lesson.from_orm(db_validated.get_lesson_by_id(session, id))


@router.get("/cabinet/{id}", tags=[CABINET], response_model=item.Cabinet)
async def get_cabinet(id: ID, session=Depends(get_session)):
    return item.Cabinet.from_orm(db_validated.get_cabinet_by_id(session, id))


@router.get(
    "/lessontimetable/{id}", tags=[LESSON_NUMBER], response_model=item.LessonNumber
)
async def get_lesson_number(id: ID, session=Depends(get_session)):
    return item.LessonNumber.from_orm(db_validated.get_lesson_number_by_id(session, id))
