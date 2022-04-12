# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


import valid_db_requests as db_validated
from config import API_PREFIX, API_SUBCLASS_PREFIX
from config import DEFAULT_LOGGER as logger
from config import Access, get_session
from extra import create_logger_dependency
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels, get_current_service
from extra.tags import SUBCLASS, WEBSITE
from fastapi import APIRouter, Depends, HTTPException
from models import database
from models.web import incoming, outgoing, updating


allowed = AllowLevels(Access.Admin, Access.Parser)

router = APIRouter(
    prefix=API_PREFIX + API_SUBCLASS_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger)), Depends(allowed)],
    route_class=LoggingRouter,
)
logger.info(f"Subclass fouter created on {API_PREFIX + API_SUBCLASS_PREFIX}")


@router.post("/new", tags=[SUBCLASS], response_model=outgoing.Subclass)
async def create_subclass(subclass: incoming.Subclass, session=Depends(get_session)):
    school = db_validated.get_school_by_id(session, subclass.school_id)
    logger.info(
        f"Adding subclass '{subclass.educational_level}{subclass.identificator}{subclass.additional_identificator}' to school '{school.name}' "
    )
    candidate = (
        session.query(database.Subclass)
        .filter_by(
            educational_level=subclass.educational_level,
            identificator=subclass.identificator,
            additional_identificator=subclass.additional_identificator,
            school_id=subclass.school_id,
        )
        .first()
    )
    if candidate:
        logger.debug(
            f"Raised an exception because subclass with identificators {subclass.educational_level} {subclass.identificator} {subclass.additional_identificator} is already exists"
        )
        raise HTTPException(
            status_code=409,
            detail=f"Subclass with identificators {subclass.educational_level} {subclass.identificator} {subclass.additional_identificator} is already exists",
        )
    subclass = database.Subclass(
        educational_level=subclass.educational_level,
        identificator=subclass.identificator,
        additional_identificator=subclass.additional_identificator,
    )
    school.subclasses.append(subclass)
    session.add(subclass)
    session.add(school)
    session.commit()
    logger.debug(f"Subclass acquired id {subclass.id}")
    return outgoing.Subclass.from_orm(subclass)


@router.put("/update", tags=[SUBCLASS], response_model=outgoing.Subclass)
async def update_subclass(request: updating.Subclass, session=Depends(get_session)):
    subclass = db_validated.get_subclass_by_id(session, request.subclass_id)

    if request.educational_level is not None:
        candidate = (
            session.query(database.Subclass)
            .filter_by(
                educational_level=request.educational_level,
                identificator=subclass.identificator,
                additional_identificator=subclass.additional_identificator,
                school_id=subclass.school_id,
            )
            .first()
        )
        if candidate is not None:
            logger.debug(
                f"Raised an exception because subclass with identificators {request.educational_level} {subclass.identificator} {subclass.additional_identificator} is already exists"
            )
            raise HTTPException(
                status_code=409,
                detail=f"Subclass with identificators {request.educational_level} {subclass.identificator} {subclass.additional_identificator} is already exists",
            )
        subclass.educational_level = request.educational_level

    if request.identificator is not None:
        candidate = (
            session.query(database.Subclass)
            .filter_by(
                educational_level=subclass.educational_level,
                identificator=request.identificator,
                additional_identificator=subclass.additional_identificator,
                school_id=subclass.school_id,
            )
            .first()
        )
        if candidate:
            logger.debug(
                f"Raised an exception because subclass with identificators {subclass.educational_level} {request.identificator} {subclass.additional_identificator} is already exists"
            )
            raise HTTPException(
                status_code=409,
                detail=f"Subclass with identificators {subclass.educational_level} {request.identificator} {subclass.additional_identificator} is already exists",
            )
        subclass.identificator = request.identificator

    if request.additional_identificator is not None:
        candidate = (
            session.query(database.Subclass)
            .filter_by(
                educational_level=subclass.educational_level,
                identificator=subclass.identificator,
                additional_identificator=request.additional_identificator,
                school_id=subclass.school_id,
            )
            .all()
        )
        if candidate != []:
            logger.debug(
                f"Raised an exception because subclass with identificators {subclass.educational_level} {subclass.identificator} {request.additional_identificator} is already exists"
            )
            raise HTTPException(
                status_code=409,
                detail=f"Subclass with identificators {subclass.educational_level} {subclass.identificator} {request.additional_identificator} is already exists",
            )
        subclass.additional_identificator = request.additional_identificator

    session.add(subclass)
    session.commit()

    return outgoing.Subclass.from_orm(subclass)
