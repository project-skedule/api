# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


from fastapi import APIRouter, Depends, HTTPException
from extra.api_router import LoggingRouter
from extra.auth import get_current_user

import valid_db_requests as db_validated
from config import API_CABINET_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import get_session
from extra import create_logger_dependency
from extra.tags import CABINET, WEBSITE
from models import database
from models.web import incoming, outgoing, updating

router = APIRouter(
    prefix=API_PREFIX + API_CABINET_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
    route_class=LoggingRouter,
)
logger.info(f"Cabinet router created on {API_PREFIX+API_CABINET_PREFIX}")


@router.post("/new", tags=[CABINET, WEBSITE], response_model=outgoing.Cabinet)
async def create_new_cabinet(
    cabinet: incoming.Cabinet, _=Depends(get_current_user), session=Depends(get_session)
) -> outgoing.Cabinet:
    corpus = db_validated.get_corpus_by_id(session, cabinet.corpus_id)
    school = db_validated.get_school_by_id(session, corpus.school_id)
    logger.debug(
        f"Searching cabinet with name {cabinet.name} and corpus_id {cabinet.corpus_id}"
    )
    check_unique = (
        session.query(database.Cabinet)
        .filter_by(name=cabinet.name, corpus_id=cabinet.corpus_id)
        .all()
    )
    if check_unique:
        logger.debug(
            f"Raised an expection because the cabinet with name {cabinet.name} already exists in corpus with id {cabinet.corpus_id}"
        )
        raise HTTPException(
            status_code=409,
            detail=f"Cabinet with name {cabinet.name} already exists",
        )
    cabinet = database.Cabinet(floor=cabinet.floor, name=cabinet.name)
    logger.info(
        f"Adding cabinet with name {cabinet.name} on floor {cabinet.floor} to corpus with id {corpus.id}"
    )
    corpus.cabinets.append(cabinet)
    school.cabinets.append(cabinet)
    session.add(cabinet)
    session.add(corpus)
    session.add(school)
    session.commit()
    logger.debug(f"Cabinet with name {cabinet.name} acquired id {cabinet.id}")
    return outgoing.Cabinet(id=cabinet.id)


@router.put("/update", tags=[CABINET, WEBSITE], response_model=outgoing.Cabinet)
async def update_cabinet(
    request: updating.Cabinet, _=Depends(get_current_user), session=Depends(get_session)
):
    cabinet = db_validated.get_cabinet_by_id(session, request.cabinet_id)

    if request.floor is not None:
        cabinet.floor = request.floor

    if request.name is not None:
        logger.debug(
            f"Searching cabinet with name {request.name} and corpus_id {cabinet.corpus_id}"
        )
        check_unique = (
            session.query(database.Cabinet)
            .filter_by(name=request.name, corpus_id=cabinet.corpus_id)
            .first()
        )
        if check_unique is not None:
            logger.debug(
                f"Raised an expection because the cabinet with name {request.name} already exists in corpus with id {cabinet.corpus_id}"
            )
            raise HTTPException(
                status_code=409,
                detail=f"Cabinet with name {request.name} already exists",
            )
        cabinet.name = request.name

    session.add(cabinet)
    session.commit()

    return outgoing.Cabinet(id=cabinet.id)
