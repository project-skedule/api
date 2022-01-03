from typing import Any, Dict

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


from fastapi import APIRouter, Depends, HTTPException

import valid_db_requests as db_validated
from config import API_LESSON_GETTER_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import SESSION_FACTORY
from extra import create_logger_dependency
from extra.tags import LESSON, TELEGRAM
from models import database
from models.bot import incoming, info, item

router = APIRouter(
    prefix=API_PREFIX + API_LESSON_GETTER_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
)
logger.info(f"Lesson Getter router created on {API_PREFIX+API_LESSON_GETTER_PREFIX}")


@router.get("/day", tags=[LESSON, TELEGRAM], response_model=info.LessonsForDay)
async def get_lesson_for_day(request: incoming.LessonsForDay) -> info.LessonsForDay:
    with SESSION_FACTORY() as session:
        school = db_validated.get_school_by_id(session, request.school_id)
        if isinstance(request.data, incoming.Teacher):
            teacher = db_validated.get_teacher_by_id(session, request.data.teacher_id)
            lessons = (
                session.query(database.Lesson)
                .filter_by(
                    day_of_week=request.day_of_week,
                    teacher_id=teacher.id,
                    school_id=school.id,
                )
                .all()
            )
        else:
            subclass = db_validated.get_subclass_by_id(
                session, request.data.subclass_id
            )
            lessons = (
                session.query(database.Lesson)
                .filter_by(day_of_week=request.day_of_week, school_id=school.id)
                .filter(database.Lesson.subclasses.contains(subclass))
                .all()
            )

        returned_lesson = [
            item.Lesson(
                lesson_number=item.LessonNumber(
                    id=lesson.lesson_number.id,
                    number=lesson.lesson_number.number,
                    time_start=lesson.lesson_number.time_start,
                    time_end=lesson.lesson_number.time_end,
                ),
                day_of_week=lesson.day_of_week,
                subject=lesson.subject,
                teacher=item.Teacher(
                    name=lesson.teacher.name,
                    id=lesson.teacher.id,
                ),
                subclasses=[
                    item.Subclass(
                        id=subclass.id,
                        educational_level=subclass.educational_level,
                        identificator=subclass.identificator,
                        additional_identificator=subclass.additional_identificator,
                    )
                    for subclass in lesson.subclasses
                ],
                cabinet=item.Cabinet(
                    id=lesson.cabinet.id,
                    floor=lesson.cabinet.floor,
                    name=lesson.cabinet.name,
                ),
                corpus=item.Corpus(
                    address=lesson.corpus.address,
                    name=lesson.corpus.name,
                    id=lesson.corpus.id,
                ),
            )
            for lesson in lessons
        ]
        return info.LessonsForDay(
            day_of_week=request.day_of_week, lessons=returned_lesson
        )


@router.get("/range", tags=[LESSON, TELEGRAM], response_model=info.LessonsForRange)
async def get_lesson_for_range(
    request: incoming.LessonsForRange,
) -> info.LessonsForRange:
    with SESSION_FACTORY() as session:
        school = db_validated.get_school_by_id(session, request.school_id)

        logger.debug(
            f"Checking if start_index ({request.start_index}) < end_index ({request.end_index})"
        )

        if request.start_index > request.end_index:
            logger.debug(
                "Raised an exception because start_index must be less than or equal to end_index"
            )
            raise HTTPException(
                status_code=422,
                detail="Invalid start_index and and end_index. start_index must be less than or equal to start_index",
            )

        if isinstance(request.data, incoming.Teacher):
            teacher = db_validated.get_teacher_by_id(session, request.data.teacher_id)
            lessons = session.query(database.Lesson).filter_by(
                teacher_id=teacher.id, school_id=school.id
            )
        else:
            subclass = db_validated.get_subclass_by_id(
                session, request.data.subclass_id
            )

            lessons = (
                session.query(database.Lesson)
                .filter_by(school_id=school.id)
                .filter(database.Lesson.subclasses.contains(subclass))
            )
        days = list(range(request.start_index, request.end_index + 1))
        lessons = lessons.filter(database.Lesson.day_of_week.in_(days)).all()

        returned_lesson: Dict[int, Any] = {}

        for lesson in lessons:
            returned_lesson[lesson.day_of_week] = returned_lesson.get(
                lesson.day_of_week, []
            ) + [
                item.Lesson(
                    lesson_number=item.LessonNumber(
                        id=lesson.lesson_number.id,
                        number=lesson.lesson_number.number,
                        time_start=lesson.lesson_number.time_start,
                        time_end=lesson.lesson_number.time_end,
                    ),
                    day_of_week=lesson.day_of_week,
                    subject=lesson.subject,
                    teacher=item.Teacher(
                        name=lesson.teacher.name,
                        id=lesson.teacher.id,
                    ),
                    subclasses=[
                        item.Subclass(
                            id=subclass.id,
                            educational_level=subclass.educational_level,
                            identificator=subclass.identificator,
                            additional_identificator=subclass.additional_identificator,
                        )
                        for subclass in lesson.subclasses
                    ],
                    cabinet=item.Cabinet(
                        floor=lesson.cabinet.floor,
                        name=lesson.cabinet.name,
                        id=lesson.cabinet.id,
                    ),
                    corpus=item.Corpus(
                        id=lesson.corpus.id,
                        address=lesson.corpus.address,
                        name=lesson.corpus.name,
                    ),
                )
            ]

        return info.LessonsForRange(
            data=[
                info.LessonsForDay(
                    day_of_week=day_of_week, lessons=returned_lesson[day_of_week]
                )
                for day_of_week in returned_lesson
            ]
        )


@router.get("/certain", tags=[LESSON, TELEGRAM], response_model=item.Lesson)
async def get_certain_lesson(request: incoming.CertainLesson) -> item.Lesson:
    with SESSION_FACTORY() as session:
        school = db_validated.get_school_by_id(session, request.school_id)
        logger.debug(
            f"Searching lesson number with number {request.lesson_number} and school id {request.school_id}"
        )
        lesson_number = session.query(database.Lesson_number).filter_by(
            school_id=school.id, number=request.lesson_number
        )
        if lesson_number is None:
            logger.debug(
                f"Raised an exception because lesson number with number {request.lesson_number} and school id {request.school_id} does not exist"
            )
            raise HTTPException(
                status_code=409,
                detail=f"Lesson number with number {request.lesson_number} and school id {request.school_id} does not exist",
            )
        if isinstance(request.data, incoming.Teacher):
            teacher = db_validated.get_teacher_by_id(session, request.data.teacher_id)
            lessons = session.query(database.Lesson).filter_by(
                teacher_id=teacher.id, school_id=school.id
            )
        else:
            subclass = db_validated.get_subclass_by_id(
                session, request.data.subclass_id
            )
            lessons = session.query(database.Lesson).filter_by(
                school_id=school.id, subclass_id=subclass.id
            )

        lesson = lessons.filter_by(
            day_of_week=request.day_of_week,
            lesson_number_id=lesson_number.id,
        ).first()
        if lesson is None:
            logger.debug(
                f"Raised an exception because lesson with params {request.day_of_week=} {request.lesson_number=} {request.data=} {request.school_id=} does not exist"
            )
            raise HTTPException(
                status_code=422,
                detail=f"Lesson with params {request.day_of_week=} {request.lesson_number=} {request.data=} {request.school_id=} does not exist",
            )
        return item.Lesson(
            lesson_number=item.LessonNumber(
                id=lesson.lesson_number.id,
                number=lesson.lesson_number.number,
                time_start=lesson.lesson_number.time_start,
                time_end=lesson.lesson_number.time_end,
            ),
            day_of_week=lesson.day_of_week,
            subject=lesson.subject,
            cabinet=item.Cabinet(
                name=lesson.cabinet.name,
                floor=lesson.cabinet.floor,
                id=lesson.cabinet.id,
            ),
            teacher=item.Teacher(
                name=lesson.teacher.name,
                id=lesson.teacher.id,
            ),
            corpus=item.Corpus(
                name=lesson.corpus.name,
                address=lesson.corpus.address,
                id=lesson.corpus.id,
            ),
            subclasses=[
                item.Subclass(
                    id=subclass.id,
                    educational_level=subclass.educational_level,
                    identificator=subclass.identificator,
                    additional_identificator=subclass.additional_identificator,
                )
                for subclass in lesson.subclasses
            ],
        )
