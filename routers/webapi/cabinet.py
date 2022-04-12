# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


import valid_db_requests as db_validated
from config import API_CABINET_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import Access, get_session
from extra import create_logger_dependency
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels, get_current_service
from extra.tags import CABINET, WEBSITE, get_tags
from fastapi import APIRouter, Depends, HTTPException
from models import database
from models.web import incoming, outgoing, updating


allowed = AllowLevels(Access.Admin, Access.Parser)

router = APIRouter(
    prefix=API_PREFIX + API_CABINET_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger)), Depends(allowed)],
    route_class=LoggingRouter,
)
logger.info(f"Cabinet router created on {API_PREFIX+API_CABINET_PREFIX}")


@router.post("/new", tags=[CABINET], response_model=outgoing.Cabinet)
async def create_new_cabinet(
    request: incoming.Cabinet, session=Depends(get_session)
) -> outgoing.Cabinet:
    corpus = db_validated.get_corpus_by_id(session, request.corpus_id)
    school = db_validated.get_school_by_id(session, corpus.school_id)
    logger.debug(
        f"Searching cabinet with name {request.name} and corpus_id {request.corpus_id}"
    )
    candidate = (
        session.query(database.Cabinet)
        .filter_by(name=request.name, corpus_id=request.corpus_id)
        .first()
    )
    if candidate:
        logger.debug(
            f"Raised an expection because the cabinet with name {request.name} already exists in corpus with id {request.corpus_id}"
        )
        raise HTTPException(
            status_code=409,
            detail=f"Cabinet with name {request.name} already exists",
        )
    cabinet = database.Cabinet(
        floor=request.floor,
        name=request.name,
        tags=get_tags(session, request.tags),
        corpus_id=corpus.id,
        school_id=school.id,
    )
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
    return outgoing.Cabinet.from_orm(cabinet)


@router.put("/update", tags=[CABINET], response_model=outgoing.Cabinet)
async def update_cabinet(request: updating.Cabinet, session=Depends(get_session)):
    cabinet = db_validated.get_cabinet_by_id(session, request.cabinet_id)

    if request.floor is not None:
        cabinet.floor = request.floor

    if request.name is not None:
        logger.debug(
            f"Searching cabinet with name {request.name} and corpus_id {cabinet.corpus_id}"
        )
        candidate = (
            session.query(database.Cabinet)
            .filter_by(name=request.name, corpus_id=cabinet.corpus_id)
            .first()
        )
        if candidate is not None:
            logger.debug(
                f"Raised an expection because the cabinet with name {request.name} already exists in corpus with id {cabinet.corpus_id}"
            )
            raise HTTPException(
                status_code=409,
                detail=f"Cabinet with name {request.name} already exists",
            )
        cabinet.name = request.name

    if request.tags:
        cabinet.tags = get_tags(session, request.tags)

    session.add(cabinet)
    session.commit()

    return outgoing.Cabinet.from_orm(cabinet)
