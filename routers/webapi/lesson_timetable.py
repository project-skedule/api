# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


from datetime import datetime

import valid_db_requests as db_validated
from config import API_LESSON_NUMBER_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import Access, get_session
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels, get_current_service
from extra.tags import LESSON_NUMBER, WEBSITE
from fastapi import APIRouter, Depends, HTTPException
from models import database
from models.web import incoming, outgoing, updating

allowed = AllowLevels(Access.Admin, Access.Parser)

router = APIRouter(
    prefix=API_PREFIX + API_LESSON_NUMBER_PREFIX,
    dependencies=[Depends(allowed)],
    route_class=LoggingRouter,
)
logger.info(f"Lesson_number router created on {API_PREFIX+API_LESSON_NUMBER_PREFIX}")


@router.post("/new", tags=[LESSON_NUMBER], response_model=outgoing.LessonNumber)
async def create_new_lesson_number(
    lesson_number: incoming.LessonNumber, session=Depends(get_session)
):
    school = db_validated.get_school_by_id(session, lesson_number.school_id)

    logger.debug(
        f"Checking if time_start ({lesson_number.time_start}) < time_end ({lesson_number.time_end})"
    )
    if datetime.strptime(lesson_number.time_start, "%H:%M") >= datetime.strptime(
        lesson_number.time_end, "%H:%M"
    ):
        logger.debug(
            "Raised an exception because time_start must be less than time_end"
        )
        raise HTTPException(
            status_code=422,
            detail="Invalid time_start and time_end. time_start must be less than time_end",
        )
    logger.debug(
        f"Searching lesson_number with number {lesson_number.number} and school_id {lesson_number.school_id}"
    )
    candidate = (
        session.query(database.Lesson_number)
        .filter_by(school_id=lesson_number.school_id, number=lesson_number.number)
        .first()
    )
    if candidate:
        logger.debug(
            f"Raised an exception because the lesson_number with number {lesson_number.number} is already exists in school with id {lesson_number.school_id}"
        )
        raise HTTPException(
            status_code=409,
            detail=f"Lesson_number with number {lesson_number.number} is already exists",
        )
    lesson_number = database.Lesson_number(
        number=lesson_number.number,
        time_start=lesson_number.time_start,
        time_end=lesson_number.time_end,
    )
    logger.info(
        f"Adding lesson_number {lesson_number.number} from {lesson_number.time_start} to {lesson_number.time_end} to school with id {lesson_number.school_id}"
    )
    school.lesson_numbers.append(lesson_number)
    session.add(school)
    session.add(school)
    session.commit()
    logger.debug(f"Lesson_number acquired id {lesson_number.id}")
    return outgoing.LessonNumber.from_orm(lesson_number)


@router.put("/update", tags=[LESSON_NUMBER], response_model=outgoing.LessonNumber)
async def update_timetable(
    request: updating.LessonNumber, session=Depends(get_session)
):
    lesson_number = db_validated.get_lesson_number_by_id(
        session, request.lesson_number_id
    )
    if request.time_start is not None and request.time_end is not None:
        if datetime.strptime(request.time_start, "%H:%M") >= datetime.strptime(
            request.time_end, "%H:%M"
        ):
            logger.debug(
                "Raised an exception because time_start must be less than time_end"
            )
            raise HTTPException(
                status_code=422,
                detail="Invalid time_start and time_end. time_start must be less than time_end",
            )
        lesson_number.time_start = request.time_start
        lesson_number.time_end = request.time_end
    elif request.time_start is not None:
        if datetime.strptime(request.time_start, "%H:%M") >= datetime.strptime(
            lesson_number.time_end, "%H:%M"
        ):
            logger.debug(
                "Raised an exception because time_start must be less than time_end"
            )
            raise HTTPException(
                status_code=422,
                detail="Invalid time_start and time_end. time_start must be less than time_end",
            )
        lesson_number.time_start = request.time_start

    elif request.time_end is not None:
        if datetime.strptime(lesson_number.time_start, "%H:%M") >= datetime.strptime(
            request.time_end, "%H:%M"
        ):
            logger.debug(
                "Raised an exception because time_start must be less than time_end"
            )
            raise HTTPException(
                status_code=422,
                detail="Invalid time_start and time_end. time_start must be less than time_end",
            )
        lesson_number.time_end = request.time_end

    if request.number is not None:
        lesson_number.number = request.number

    session.add(lesson_number)
    session.commit()

    return outgoing.LessonNumber.from_orm(lesson_number)
