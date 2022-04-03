# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


import valid_db_requests as db_validated
from config import API_PREFIX, API_SCHOOL_PREFIX
from config import DEFAULT_LOGGER as logger
from config import Access, get_session
from extra import create_logger_dependency
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels, get_current_service
from extra.tags import SCHOOL, WEBSITE
from fastapi import APIRouter, Depends, HTTPException
from models import database
from models.web import incoming, outgoing, updating

router = APIRouter(
    prefix=API_PREFIX + API_SCHOOL_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
    route_class=LoggingRouter,
)
logger.info(f"School router created on {API_PREFIX+API_SCHOOL_PREFIX}")

allowed = AllowLevels(Access.Admin, Access.Parser)


@router.post("/new", tags=[SCHOOL], response_model=outgoing.School)
async def create_new_school(
    school: incoming.School, session=Depends(get_session), _=Depends(allowed)
):
    logger.debug(f'Searching school with name "{school.name}"')
    candidate = session.query(database.School).filter_by(name=school.name).first()
    if candidate:
        logger.debug(
            "Raised an exception because school with the same name is already exists"
        )
        raise HTTPException(
            status_code=409,
            detail=f"School with name {school.name} is already exists",
        )
    logger.debug(f'Adding school with name "{school.name}" to database')
    school = database.School(name=school.name)
    session.add(school)
    session.commit()
    logger.debug(f"School acquired id {school.id}")
    return outgoing.School.from_orm(school)


@router.put("/update", tags=[SCHOOL, WEBSITE], response_model=outgoing.School)
async def update_school(
    request: updating.School, session=Depends(get_session), _=Depends(allowed)
):
    school = db_validated.get_school_by_id(session, request.school_id)

    if request.name is not None:
        logger.debug(f'Searching school with name "{request.name}"')
        candidate = session.query(database.School).filter_by(name=request.name).first()
        if candidate:
            logger.debug(
                "Raised an exception because school with the same name is already exists"
            )
            raise HTTPException(
                status_code=409,
                detail=f"School with name {request.name} is already exists",
            )
        school.name = request.name

    session.add(school)
    session.commit()

    return outgoing.School.from_orm(school)
