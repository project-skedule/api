from typing import Any, Dict, Optional, Union
from typing_extensions import Annotated

# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field
from extra.auth import get_current_user
from api_types.types import ID
import valid_db_requests as db_validated
from config import API_LESSON_GETTER_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import get_session
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
async def get_lesson_for_day(
    school_id: ID,
    day_of_week: Annotated[int, Field(ge=1, le=7)],
    teacher_id: Optional[ID] = None,
    subclass_id: Optional[ID] = None,
    _=Depends(get_current_user),
) -> info.LessonsForDay:
    with get_session() as session:
        if teacher_id is not None and subclass_id is not None:
            raise HTTPException(
                status_code=422, detail="You must specify a subclass_id or a teacher_id"
            )

        if teacher_id is None and subclass_id is None:
            raise HTTPException(
                status_code=422, detail="You must specify a subclass_id or a teacher_id"
            )

        school = db_validated.get_school_by_id(session, school_id)
        if teacher_id is not None:
            teacher = db_validated.get_teacher_by_id(session, teacher_id)
            lessons = (
                session.query(database.Lesson)
                .filter_by(
                    day_of_week=day_of_week,
                    teacher_id=teacher.id,
                    school_id=school.id,
                )
                .all()
            )
        else:
            subclass = db_validated.get_subclass_by_id(session, subclass_id)
            lessons = (
                session.query(database.Lesson)
                .filter_by(day_of_week=day_of_week, school_id=school.id)
                .filter(database.Lesson.subclasses.contains(subclass))
                .all()
            )

        lessons = sorted(lessons, key=lambda x: x.lesson_number.number)

        returned_lesson = [
            item.Lesson(
                id=lesson.id,
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
                    corpus=item.Corpus(
                        address=lesson.corpus.address,
                        name=lesson.corpus.name,
                        id=lesson.corpus.id,
                    ),
                ),
            )
            for lesson in lessons
        ]
        return info.LessonsForDay(day_of_week=day_of_week, lessons=returned_lesson)


@router.get("/range", tags=[LESSON, TELEGRAM], response_model=info.LessonsForRange)
async def get_lesson_for_range(
    school_id: ID,
    start_index: Annotated[int, Field(ge=1, le=7)],
    end_index: Annotated[int, Field(ge=1, le=7)],
    teacher_id: Optional[ID] = None,
    subclass_id: Optional[ID] = None,
    _=Depends(get_current_user),
) -> info.LessonsForRange:
    with get_session() as session:
        if teacher_id is not None and subclass_id is not None:
            raise HTTPException(
                status_code=422, detail="You must specify a subclass_id or a teacher_id"
            )

        if teacher_id is None and subclass_id is None:
            raise HTTPException(
                status_code=422, detail="You must specify a subclass_id or a teacher_id"
            )

        school = db_validated.get_school_by_id(session, school_id)

        logger.debug(
            f"Checking if start_index ({start_index}) < end_index ({end_index})"
        )

        if start_index > end_index:
            logger.debug(
                "Raised an exception because start_index must be less than or equal to end_index"
            )
            raise HTTPException(
                status_code=422,
                detail="Invalid start_index and and end_index. start_index must be less than or equal to start_index",
            )

        if teacher_id is not None:
            teacher = db_validated.get_teacher_by_id(session, teacher_id)
            lessons = session.query(database.Lesson).filter_by(
                teacher_id=teacher.id, school_id=school.id
            )
        else:
            subclass = db_validated.get_subclass_by_id(session, subclass_id)

            lessons = (
                session.query(database.Lesson)
                .filter_by(school_id=school.id)
                .filter(database.Lesson.subclasses.contains(subclass))
            )
        days = list(range(start_index, end_index + 1))
        lessons = lessons.filter(database.Lesson.day_of_week.in_(days)).all()

        lessons = sorted(lessons, key=lambda x: x.lesson_number.number)

        returned_lesson: Dict[int, Any] = {}

        for lesson in lessons:
            returned_lesson[lesson.day_of_week] = returned_lesson.get(
                lesson.day_of_week, []
            ) + [
                item.Lesson(
                    id=lesson.id,
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
                        corpus=item.Corpus(
                            id=lesson.corpus.id,
                            address=lesson.corpus.address,
                            name=lesson.corpus.name,
                        ),
                    ),
                )
            ]

        days = sorted(returned_lesson.keys())

        return info.LessonsForRange(
            data=[
                info.LessonsForDay(
                    day_of_week=day_of_week, lessons=returned_lesson[day_of_week]
                )
                for day_of_week in days
            ]
        )


@router.get("/certain", tags=[LESSON, TELEGRAM], response_model=item.Lesson)
async def get_certain_lesson(
    school_id: ID,
    lesson_number: Annotated[int, Field(ge=0, le=20)],
    day_of_week: Annotated[int, Field(ge=1, le=7)],
    teacher_id: Optional[ID] = None,
    subclass_id: Optional[ID] = None,
    _=Depends(get_current_user),
) -> item.Lesson:
    with get_session() as session:
        if teacher_id is not None and subclass_id is not None:
            raise HTTPException(
                status_code=422, detail="You must specify a subclass_id or a teacher_id"
            )

        if teacher_id is None and subclass_id is None:
            raise HTTPException(
                status_code=422, detail="You must specify a subclass_id or a teacher_id"
            )

        school = db_validated.get_school_by_id(session, school_id)
        logger.debug(
            f"Searching lesson number with number {lesson_number} and school id {school_id}"
        )
        lesson_number = session.query(database.Lesson_number).filter_by(
            school_id=school.id, number=lesson_number
        )
        if lesson_number is None:
            logger.debug(
                f"Raised an exception because lesson number with number {lesson_number} and school id {school_id} does not exist"
            )
            raise HTTPException(
                status_code=409,
                detail=f"Lesson number with number {lesson_number} and school id {school_id} does not exist",
            )
        if teacher_id is not None:
            teacher = db_validated.get_teacher_by_id(session, teacher_id)
            lessons = session.query(database.Lesson).filter_by(
                teacher_id=teacher.id, school_id=school.id
            )
        else:
            subclass = db_validated.get_subclass_by_id(session, subclass_id)
            lessons = session.query(database.Lesson).filter_by(
                school_id=school.id, subclass_id=subclass.id
            )

        lesson = lessons.filter_by(
            day_of_week=day_of_week,
            lesson_number_id=lesson_number.id,
        ).first()
        if lesson is None:
            logger.debug(
                f"Raised an exception because lesson with params {day_of_week=} {lesson_number=} {(teacher_id, subclass_id)=} {school_id=} does not exist"
            )
            raise HTTPException(
                status_code=422,
                detail=f"Lesson with params {day_of_week=} {lesson_number=} {(teacher_id, subclass_id)=} {school_id=} does not exist",
            )
        return item.Lesson(
            id=lesson.id,
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
                corpus=item.Corpus(
                    name=lesson.corpus.name,
                    address=lesson.corpus.address,
                    id=lesson.corpus.id,
                ),
            ),
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
        )
