# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


from fastapi import APIRouter, Depends, HTTPException

import valid_db_requests as db_validated
from config import API_PREFIX, API_SCHOOL_PREFIX
from config import DEFAULT_LOGGER as logger
from config import get_session
from extra import create_logger_dependency
from extra.tags import SCHOOL, WEBSITE
from models import database
from models.web import incoming, outgoing, updating

router = APIRouter(
    prefix=API_PREFIX + API_SCHOOL_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
)
logger.info(f"School router created on {API_PREFIX+API_SCHOOL_PREFIX}")


@router.post("/new", tags=[SCHOOL, WEBSITE], response_model=outgoing.School)
async def create_new_school(school: incoming.School) -> outgoing.School:
    with get_session() as session:
        logger.debug(f'Searching school with name "{school.name}"')
        check_unique = session.query(database.School).filter_by(name=school.name).all()
        if check_unique != []:
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
        return outgoing.School(id=school.id)


@router.put("/update", tags=[SCHOOL, WEBSITE], response_model=outgoing.School)
async def update_school(request: updating.School):
    with get_session() as session:
        school = db_validated.get_school_by_id(session, request.school_id)

        if request.name is not None:
            logger.debug(f'Searching school with name "{request.name}"')
            check_unique = (
                session.query(database.School).filter_by(name=request.name).first()
            )
            if check_unique is not None:
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

        return outgoing.School(id=school.id)
