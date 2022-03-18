# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


from fastapi import APIRouter, Depends, HTTPException
from extra.api_router import LoggingRouter
from extra.service_auth import get_current_service

import valid_db_requests as db_validated
from config import API_PREFIX, API_TEACHER_PREFIX
from config import DEFAULT_LOGGER as logger
from config import get_session
from extra import create_logger_dependency
from extra.tags import TEACHER, WEBSITE
from models import database
from models.web import incoming, outgoing, updating

router = APIRouter(
    prefix=API_PREFIX + API_TEACHER_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
    route_class=LoggingRouter,
)
logger.info(f"Teacher router created on {API_PREFIX+API_TEACHER_PREFIX}")


@router.post("/new", tags=[TEACHER, WEBSITE], response_model=outgoing.Teacher)
async def create_new_teacher(
    teacher: incoming.Teacher,
    _=Depends(get_current_service),
    session=Depends(get_session),
) -> outgoing.Teacher:
    school = db_validated.get_school_by_id(session, teacher.school_id)
    logger.debug(
        f"Searching teacher with name {teacher.name} in school with id {teacher.school_id}"
    )
    check_unique = (
        session.query(database.Teacher)
        .filter_by(name=teacher.name, school_id=teacher.school_id)
        .all()
    )
    if check_unique:
        logger.debug(
            f"Raise an expection because the teacher with name {teacher.name} already exists in school with id {school.id}"
        )
        raise HTTPException(
            status_code=409,
            detail=f"Teacher with name {teacher.name} is already exists",
        )
    teacher = database.Teacher(name=teacher.name)
    logger.info(
        f"Adding teacher with name {teacher.name} to school with id {school.id}"
    )
    school.teachers.append(teacher)
    session.add(teacher)
    session.add(school)
    session.commit()
    logger.debug(f"Teacher with name {teacher.name} acquired id {teacher.id}")
    return outgoing.Teacher(id=teacher.id)


@router.put("/update", tags=[TEACHER, WEBSITE], response_model=outgoing.Teacher)
async def update_teacher(
    request: updating.Teacher,
    _=Depends(get_current_service),
    session=Depends(get_session),
):
    teacher = db_validated.get_teacher_by_id(session, request.teacher_id)

    if request.name is not None:
        check_unique = (
            session.query(database.Teacher)
            .filter_by(name=request.name, school_id=teacher.school_id)
            .first()
        )
        if check_unique is not None:
            logger.debug(
                f"Raise an expection because the teacher with name {request.name} already exists in school with id {teacher.school_id}"
            )
            raise HTTPException(
                status_code=409,
                detail=f"Teacher with name {request.name} is already exists",
            )
        teacher.name = request.name

    session.add(teacher)
    session.commit()

    return outgoing.Teacher(id=teacher.id)
