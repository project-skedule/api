# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


from fastapi import APIRouter, Depends, HTTPException
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels, get_current_service

import valid_db_requests as db_validated
from config import API_CORPUS_PREFIX, API_PREFIX, Access
from config import DEFAULT_LOGGER as logger
from config import get_session
from extra import create_logger_dependency
from extra.tags import CORPUS, WEBSITE
from models import database
from models.web import incoming, outgoing, updating

router = APIRouter(
    prefix=API_PREFIX + API_CORPUS_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
    route_class=LoggingRouter,
)
logger.info(f"Corpus router created on {API_PREFIX+API_CORPUS_PREFIX}")

corpus_allowed = AllowLevels(Access.Admin, Access.Parser)


@router.post("/new", tags=[CORPUS, WEBSITE], response_model=outgoing.Corpus)
async def create_new_corpus(
    corpus: incoming.Corpus,
    session=Depends(get_session),
    _=Depends(corpus_allowed),
) -> outgoing.Corpus:
    school = db_validated.get_school_by_id(session, corpus.school_id)
    logger.debug(
        f"Searching corpus with name {corpus.name} and school_id {corpus.school_id}"
    )
    check_unique = (
        session.query(database.Corpus)
        .filter_by(name=corpus.name, school_id=corpus.school_id)
        .all()
    )
    if check_unique:
        logger.debug(
            f"Raised an exception because the corpus with name {corpus.name} is already exists in school with id {corpus.school_id}"
        )
        raise HTTPException(
            status_code=409,
            detail=f"Corpus with name {corpus.name} is already exists",
        )
    check_unique = (
        session.query(database.Corpus)
        .filter_by(address=corpus.address, school_id=corpus.school_id)
        .all()
    )
    if check_unique:
        logger.debug(
            f"Raised an exception because the corpus with address {corpus.address} is already exists in school with id {corpus.school_id}"
        )
        raise HTTPException(
            status_code=409,
            detail=f"Corpus with address {corpus.address} is already exists",
        )
    corpus = database.Corpus(
        name=corpus.name, address=corpus.address, canteen_text=corpus.canteen_text
    )
    logger.info(
        f"Adding corpus with name {corpus.name} and address {corpus.address} to school with name {school.name}"
    )
    school.corpuses.append(corpus)
    session.add(corpus)
    session.add(school)
    session.commit()
    logger.debug(f"Corpus acquired id {corpus.id}")
    return outgoing.Corpus(id=corpus.id)


@router.put("/update", tags=[CORPUS, WEBSITE], response_model=outgoing.Corpus)
async def update_corpus(
    request: updating.Corpus,
    session=Depends(get_session),
    _=Depends(corpus_allowed),
):
    corpus = db_validated.get_corpus_by_id(session, request.corpus_id)

    if request.address is not None:
        check_unique = (
            session.query(database.Corpus)
            .filter_by(address=request.address, school_id=corpus.school_id)
            .first()
        )
        if check_unique is not None:
            logger.debug(
                f"Raised an exception because the corpus with address {request.address} is already exists in school with id {corpus.school_id}"
            )
            raise HTTPException(
                status_code=409,
                detail=f"Corpus with address {request.address} is already exists",
            )
        corpus.address = request.address

    if request.name is not None:
        check_unique = (
            session.query(database.Corpus)
            .filter_by(name=request.name, school_id=corpus.school_id)
            .first()
        )
        if check_unique is not None:
            logger.debug(
                f"Raised an exception because the corpus with name {request.name} is already exists in school with id {corpus.school_id}"
            )
            raise HTTPException(
                status_code=409,
                detail=f"Corpus with name {request.name} is already exists",
            )
        corpus.name = request.name

    if request.canteen_text is not None:
        corpus.canteen_text = request.canteen_text

    session.add(corpus)
    session.commit()

    return outgoing.Corpus(id=corpus.id)
