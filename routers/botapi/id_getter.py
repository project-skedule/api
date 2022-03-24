# pyright: reportUnknownMemberType=false

import valid_db_requests as db_validated
from api_types import ID
from config import API_ID_GETTER_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import Access, get_session
from extra import create_logger_dependency
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels, get_current_service
from extra.tags import (
    CABINET,
    CORPUS,
    INFO,
    LESSON,
    LESSON_NUMBER,
    SCHOOL,
    SUBCLASS,
    TEACHER,
)
from fastapi import APIRouter, Depends
from models.bot import item

id_getter_allowed = AllowLevels(Access.Admin, Access.Telegram, Access.Parser)

router = APIRouter(
    prefix=API_PREFIX + API_ID_GETTER_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
    route_class=LoggingRouter,
)
logger.info(f"ID getter router created on {API_PREFIX+API_ID_GETTER_PREFIX}")


@router.get("/subclass/{id}", tags=[SUBCLASS, INFO], response_model=item.Subclass)
async def get_subclass(
    id: ID,
    session=Depends(get_session),
    _=Depends(id_getter_allowed),
):
    subclass = db_validated.get_subclass_by_id(session, id)

    return item.Subclass(
        id=subclass.id,
        educational_level=subclass.educational_level,
        identificator=subclass.identificator,
        additional_identificator=subclass.additional_identificator,
    )


@router.get("/teacher/{id}", tags=[TEACHER, INFO], response_model=item.Teacher)
async def get_teacher(
    id: ID,
    session=Depends(get_session),
    _=Depends(id_getter_allowed),
):
    teacher = db_validated.get_teacher_by_id(session, id)

    return item.Teacher(
        name=teacher.name,
        id=teacher.id,
        tags=[tag.label for tag in teacher.tags],
    )


@router.get("/school/{id}", tags=[SCHOOL, INFO], response_model=item.School)
async def get_school(
    id: ID,
    session=Depends(get_session),
    _=Depends(id_getter_allowed),
):
    school = db_validated.get_school_by_id(session, id)

    return item.School(
        name=school.name,
        id=school.id,
    )


@router.get("/corpus/{id}", tags=[CORPUS, INFO], response_model=item.Corpus)
async def get_corpus(
    id: ID,
    session=Depends(get_session),
    _=Depends(id_getter_allowed),
):
    corpus = db_validated.get_corpus_by_id(session, id)

    return item.Corpus(
        address=corpus.address,
        name=corpus.name,
        id=corpus.id,
    )


@router.get("/lesson/{id}", tags=[LESSON, INFO], response_model=item.Lesson)
async def get_lesson(
    id: ID,
    session=Depends(get_session),
    _=Depends(id_getter_allowed),
):
    lesson = db_validated.get_lesson_by_id(session, id)

    return item.Lesson(
        id=lesson.id,
        lesson_number=item.LessonNumber(
            id=lesson.lesson_number.id,
            number=lesson.lesson_number.number,
            time_start=lesson.lesson_number.time_start,
            time_end=lesson.lesson_number.time_end,
        ),
        subject=lesson.subject,
        day_of_week=lesson.day_of_week,
        subclasses=[
            item.Subclass(
                id=subclass.id,
                educational_level=subclass.educational_level,
                identificator=subclass.identificator,
                additional_identificator=subclass.additional_identificator,
            )
            for subclass in lesson.subclasses  # pyright: reportUnknownVariableType=false
        ],
        teacher=item.Teacher(
            name=lesson.teacher.name,
            id=lesson.teacher.id,
            tags=[tag.label for tag in lesson.teacher.tags],
        ),
        cabinet=item.Cabinet(
            id=lesson.cabinet.id,
            floor=lesson.cabinet.floor,
            name=lesson.cabinet.name,
            tags=[tag.label for tag in lesson.cabinet.tags],
            corpus=item.Corpus(
                address=lesson.corpus.address,
                name=lesson.corpus.name,
                id=lesson.corpus.id,
            ),
        ),
        school=item.School(
            name=lesson.school.name,
            id=lesson.school.id,
        ),
    )


@router.get("/cabinet/{id}", tags=[CABINET, INFO], response_model=item.Cabinet)
async def get_cabinet(
    id: ID,
    session=Depends(get_session),
    _=Depends(id_getter_allowed),
):
    cabinet = db_validated.get_cabinet_by_id(session, id)

    return item.Cabinet(
        id=cabinet.id,
        floor=cabinet.floor,
        name=cabinet.name,
        tags=[tag.label for tag in cabinet.tags],
        corpus=item.Corpus(
            address=cabinet.corpus.address,
            name=cabinet.corpus.name,
            id=cabinet.corpus.id,
        ),
    )


@router.get(
    "/lessontimetable/{id}",
    tags=[LESSON_NUMBER, INFO],
    response_model=item.LessonNumber,
)
async def get_lesson_number(
    id: ID,
    session=Depends(get_session),
    _=Depends(id_getter_allowed),
):
    lesson_number = db_validated.get_lesson_number_by_id(session, id)

    return item.LessonNumber(
        id=lesson_number.id,
        number=lesson_number.number,
        time_start=lesson_number.time_start,
        time_end=lesson_number.time_end,
    )
