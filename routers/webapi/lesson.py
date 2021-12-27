from fastapi import APIRouter, Depends, HTTPException

import valid_db_requests as db_validated
from config import API_LESSON_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import SESSION_FACTORY
from extra import create_logger_dependency
from extra.tags import LESSON, WEBSITE
from models import database
from models.web import incoming, outgoing, updating

router = APIRouter(
    prefix=API_PREFIX + API_LESSON_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
)
logger.info(f"Lesson router created on {API_PREFIX+API_LESSON_PREFIX}")


@router.post("/new", tags=[LESSON, WEBSITE], response_model=outgoing.Lesson)
async def create_new_lesson(lesson: incoming.Lesson) -> outgoing.Lesson:
    with SESSION_FACTORY() as session:
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

        check_unique = (
            session.query(database.Lesson)
            .filter_by(
                school_id=school.id,
                corpus_id=corpus.id,
                cabinet_id=cabinet.id,
                lesson_number_id=lesson_number.id,
                day_of_week=lesson.day_of_week,
            )
            .all()
        )

        if check_unique != []:
            logger.debug(
                f"Raised an exception because lesson is already exists: {check_unique}"
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
        return outgoing.Lesson(id=lesson.id)


@router.put("/update", tags=[LESSON, WEBSITE], response_model=outgoing.Lesson)
async def update_lesson(request: updating.Lesson):
    with SESSION_FACTORY() as session:
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
                    f"Raised an exception because teacher is in another school (ID: {lesson_number.school_id}) from lesson (ID: {lesson.school_id})"
                )
                raise HTTPException(
                    status_code=409, detail="Teacher is in another school"
                )
            lesson.teacher_id = teacher.id

        if request.subclasses is not None:
            subclasses = [
                db_validated.get_subclass_by_id(session, s_id)
                for s_id in request.subclasses
            ]
            if any(subclass.school_id != lesson.school_id for subclass in subclasses):
                logger.debug(
                    f"Raised an exception because subclass is in another school (ID: {lesson_number.school_id}) from lesson (ID: {lesson.school_id})"
                )
                raise HTTPException(
                    status_code=409, detail="Subclass is in another school"
                )
            lesson.subclasses = subclasses

        if request.cabinet_id is not None:
            cabinet = db_validated.get_cabinet_by_id(session, request.cabinet_id)
            lesson.cabinet_id = cabinet.id

        session.add(lesson)
        session.commit()

        return outgoing.Lesson(id=lesson.id)
