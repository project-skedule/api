# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


import valid_db_requests as db_validated
from config import API_PREFIX, API_TEACHER_PREFIX
from config import DEFAULT_LOGGER as logger
from config import Access, get_session
from extra import create_logger_dependency
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels, get_current_service
from extra.tags import TEACHER, WEBSITE, get_tags
from fastapi import APIRouter, Depends, HTTPException
from models import database
from models.web import incoming, outgoing, updating

allowed = AllowLevels(Access.Admin, Access.Parser)

router = APIRouter(
    prefix=API_PREFIX + API_TEACHER_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger)), Depends(allowed)],
    route_class=LoggingRouter,
)
logger.info(f"Teacher router created on {API_PREFIX+API_TEACHER_PREFIX}")


@router.post("/new", tags=[TEACHER], response_model=outgoing.Teacher)
async def create_new_teacher(request: incoming.Teacher, session=Depends(get_session)):
    school = db_validated.get_school_by_id(session, request.school_id)
    logger.debug(
        f"Searching teacher with name {request.name} in school with id {request.school_id}"
    )
    candidate = (
        session.query(database.Teacher)
        .filter_by(name=request.name, school_id=request.school_id)
        .first()
    )
    if candidate:
        logger.debug(
            f"Raise an expection because the teacher with name {request.name} already exists in school with id {school.id}"
        )
        raise HTTPException(
            status_code=409,
            detail=f"Teacher with name {request.name} is already exists",
        )
    tags = get_tags(session, request.tags)

    teacher = database.Teacher(name=request.name, tags=tags, school_id=school.id)

    logger.info(
        f"Adding teacher with name {teacher.name} to school with id {school.id}"
    )
    school.teachers.append(teacher)
    session.add(teacher)
    session.add(school)
    session.commit()
    logger.debug(f"Teacher with name {teacher.name} acquired id {teacher.id}")
    return outgoing.Teacher.from_orm(teacher)


@router.put("/update", tags=[TEACHER], response_model=outgoing.Teacher)
async def update_teacher(request: updating.Teacher, session=Depends(get_session)):
    teacher = db_validated.get_teacher_by_id(session, request.teacher_id)

    if request.name is not None:
        candidate = (
            session.query(database.Teacher)
            .filter_by(name=request.name, school_id=teacher.school_id)
            .first()
        )
        if candidate:
            logger.debug(
                f"Raise an expection because the teacher with name {request.name} already exists in school with id {teacher.school_id}"
            )
            raise HTTPException(
                status_code=409,
                detail=f"Teacher with name {request.name} is already exists",
            )
        teacher.name = request.name
    if request.tags:
        teacher.tags = get_tags(session, request.tags)

    session.add(teacher)
    session.commit()

    return outgoing.Teacher.from_orm(teacher)
