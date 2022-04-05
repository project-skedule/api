# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


import valid_db_requests as db_validated
from api_types import ID
from config import API_LESSON_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import Access, get_session
from extra import create_logger_dependency
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels, get_current_service
from extra.tags import LESSON, WEBSITE
from fastapi import APIRouter, Depends, HTTPException
from models import database
from models.web import incoming, outgoing, updating

router = APIRouter(
    prefix=API_PREFIX + API_LESSON_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
    route_class=LoggingRouter,
)
logger.info(f"Lesson router created on {API_PREFIX+API_LESSON_PREFIX}")

allowed = AllowLevels(Access.Admin, Access.Parser)


@router.post("/new", tags=[LESSON], response_model=outgoing.Lesson)
async def create_new_lesson(
    lesson: incoming.Lesson, session=Depends(get_session), _=Depends(allowed)
):
    cabinet = db_validated.get_cabinet_by_id(session, lesson.cabinet_id)
    corpus = db_validated.get_corpus_by_id(session, cabinet.corpus_id)
    school = db_validated.get_school_by_id(session, corpus.school_id)
    teacher = db_validated.get_teacher_by_id(session, lesson.teacher_id)
    lesson_number = db_validated.get_lesson_number_by_id(
        session, lesson.lesson_number_id
    )
    subclasses = [
        db_validated.get_subclass_by_id(session, s_id) for s_id in lesson.subclasses
    ]

    candidate = (
        session.query(database.Lesson)
        .filter_by(
            school_id=school.id,
            corpus_id=corpus.id,
            cabinet_id=cabinet.id,
            lesson_number_id=lesson_number.id,
            day_of_week=lesson.day_of_week,
            teacher_id=teacher.id,
        )
        .first()
    )

    if candidate:
        logger.debug(
            f"Raised an exception because lesson is already exists: {candidate}"
        )
        raise HTTPException(status_code=409, detail="Lesson is already exists")
    lesson = database.Lesson(
        day_of_week=lesson.day_of_week,
        subject=lesson.subject,
        lesson_number_id=lesson_number.id,
        teacher_id=teacher.id,
        corpus_id=corpus.id,
        cabinet_id=cabinet.id,
        school_id=school.id,
        subclasses=subclasses,
    )
    school.lessons.append(lesson)

    session.add(lesson)
    session.add(school)
    session.commit()
    logger.debug(f"Lesson acquired id {lesson.id}")
    return outgoing.Lesson.from_orm(lesson)


@router.put("/update", tags=[LESSON], response_model=outgoing.Lesson)
async def update_lesson(
    request: updating.Lesson, session=Depends(get_session), _=Depends(allowed)
):
    lesson = db_validated.get_lesson_by_id(session, request.lesson_id)

    if request.day_of_week is not None:
        lesson.day_of_week = request.day_of_week

    if request.subject is not None:
        lesson.subject = request.subject

    if request.lesson_number_id is not None:
        lesson_number = db_validated.get_lesson_number_by_id(
            session, request.lesson_number_id
        )
        if lesson_number.school_id != lesson.school_id:
            logger.debug(
                f"Raised an exception because lesson number is in another school (ID: {lesson_number.school_id}) from lesson (ID: {lesson.school_id})"
            )
            raise HTTPException(
                status_code=409, detail="Lesson number is in another school"
            )
        lesson.lesson_number_id = lesson_number.id

    if request.teacher_id is not None:
        teacher = db_validated.get_teacher_by_id(session, request.teacher_id)
        if teacher.school_id != lesson.school_id:
            logger.debug(
                f"Raised an exception because teacher is in another school (ID: {teacher.school_id}) from lesson (ID: {lesson.school_id})"
            )
            raise HTTPException(status_code=409, detail="Teacher is in another school")
        lesson.teacher_id = teacher.id

    if request.subclasses is not None:
        subclasses = [
            db_validated.get_subclass_by_id(session, s_id)
            for s_id in request.subclasses
        ]
        if any(subclass.school_id != lesson.school_id for subclass in subclasses):
            logger.debug(
                f"Raised an exception because subclass is in another school from lesson (ID: {lesson.school_id})"
            )
            raise HTTPException(status_code=409, detail="Subclass is in another school")
        lesson.subclasses = subclasses

    if request.cabinet_id is not None:
        cabinet = db_validated.get_cabinet_by_id(session, request.cabinet_id)
        if cabinet.school_id != lesson.school_id:
            logger.debug(
                f"Raised an exception because cabinet is in another school (ID: {cabinet.school_id}) from lesson (ID: {lesson.school_id})"
            )
            raise HTTPException(status_code=409, detail="Cabinet is in another school")
        lesson.cabinet_id = cabinet.id

    session.add(lesson)
    session.commit()

    return outgoing.Lesson.from_orm(lesson)


@router.delete("/delete", tags=[LESSON], response_model=outgoing.Lesson)
async def delete_lesson(
    lesson_id: ID, _=Depends(allowed), session=Depends(get_session)
):
    lesson = db_validated.get_lesson_by_id(session, lesson_id)
    logger.info(f"Deleting lesson with id {lesson_id}")
    session.delete(lesson)
    session.commit()
    return outgoing.Lesson.from_orm(lesson)
