# pyright: reportUnknownMemberType=false

from config import LOGGER_CONFIG
from extra.custom_logger import CustomizeLogger
from fastapi import HTTPException
from models import database
from sqlalchemy.orm.session import Session

logger = CustomizeLogger.make_logger(LOGGER_CONFIG)


def get_school_by_name(session: Session, name: str) -> database.School:
    logger.debug(f"Searching school with name {name}")
    school = session.query(database.School).filter_by(name=name).first()
    if school is None:
        logger.debug(
            f"Raised an exception because school with name {name} does not exist"
        )
        raise HTTPException(
            status_code=404,
            detail=f"School with name {name} does not exist",
        )
    logger.debug(f"Successfully found school with name {name}")
    return school


def get_school_by_id(session: Session, uid: int) -> database.School:
    logger.debug(f"Searching school with id {uid}")
    school = session.query(database.School).filter_by(id=uid).first()
    if school is None:
        logger.debug(
            f"Raised an exception because school with id {uid} does not exists"
        )
        raise HTTPException(
            status_code=404,
            detail=f"School with id {uid} does not exist",
        )
    logger.debug(f"Successfully found school with id {uid}")
    return school


def get_tag_by_id(session: Session, uid: int) -> database.Tag:
    logger.debug(f"Searching tag with id {uid}")
    tag = session.query(database.Tag).filter_by(id=uid).first()
    if tag is None:
        logger.debug(f"Raised an exception because tag with id {uid} does not exists")
        raise HTTPException(
            status_code=404,
            detail=f"Tag with id {uid} does not exist",
        )
    logger.debug(f"Successfully found tag with id {uid}")
    return tag


def get_corpus_by_id(session: Session, uid: int) -> database.Corpus:
    logger.debug(f"Searchin corpus with id {uid}")
    corpus = session.query(database.Corpus).filter_by(id=uid).first()
    if corpus is None:
        logger.debug(
            f"Raised an exception because corpus with id {uid} does not exists"
        )
        raise HTTPException(
            status_code=404,
            detail=f"Corpus with id {uid} does not exists",
        )
    logger.debug(f"Successfully found corpus with id {uid}")
    return corpus


def get_teacher_by_id(session: Session, uid: int) -> database.Teacher:
    logger.debug(f"Searching for teacher with id {uid}")
    teacher = session.query(database.Teacher).filter_by(id=uid).first()
    if teacher is None:
        logger.debug("Raised an exception because teacher with id {id} does not exists")
        raise HTTPException(
            status_code=404,
            detail=f"Teacher with id {uid} does not exists",
        )
    logger.debug(f"Successfully found teacher with id {uid}")
    return teacher


def get_teacher_by_name(
    session: Session, name: str, school_id: int
) -> database.Teacher:
    logger.debug(f"Searching for teacher with name {name}")
    teacher = (
        session.query(database.Teacher)
        .filter_by(name=name, school_id=school_id)
        .first()
    )
    if teacher is None:
        logger.debug(
            f"Raised an exception because teacher with name {name} does not exists"
        )
        raise HTTPException(
            status_code=404, detail=f"Teacher with name {name} does not exists"
        )
    logger.debug(f"Successfully found teacher with name {name}")
    return teacher


def get_lesson_number_by_id(session: Session, uid: int) -> database.Lesson_number:
    logger.debug(f"Searching for lesson_number with id {uid}")
    lesson_number = session.query(database.Lesson_number).filter_by(id=uid).first()
    if lesson_number is None:
        logger.debug(
            f"Raised an exception because lesson number with id {uid} does not exists"
        )
        raise HTTPException(
            status_code=404,
            detail=f"Lesson number with id {uid} does not exists",
        )
    logger.debug(f"Successfully found lesson number with id {uid}")
    return lesson_number


def get_subclass_by_id(session: Session, uid: int) -> database.Subclass:
    logger.debug(f"Searching for subclass with id {uid}")
    subclass = session.query(database.Subclass).filter_by(id=uid).first()
    if subclass is None:
        logger.debug(
            f"Raised an exception because subclass with id {uid} does not exists"
        )
        raise HTTPException(
            status_code=404, detail=f"Subclass with id {uid} does not exists"
        )
    logger.debug(f"Successfully found subclass with id {uid}")
    return subclass


def get_subclass_by_params(
    session: Session,
    school_id: int,
    educational_level: int,
    identificator: str,
    additional_identificator: str,
) -> database.Subclass:
    logger.debug(
        f"Searching for subclass with params {educational_level=} {identificator=} {additional_identificator=} in school with {school_id=}"
    )
    subclass = (
        session.query(database.Subclass)
        .filter_by(
            school_id=school_id,
            educational_level=educational_level,
            identificator=identificator,
            additional_identificator=additional_identificator,
        )
        .first()
    )
    if subclass is None:
        logger.debug(
            f"Raised an exception because subclass with params {educational_level=} {identificator=} {additional_identificator=} does not exists in school with {school_id=}"
        )
        raise HTTPException(
            status_code=404,
            detail=f"Subclass with params {educational_level=} {identificator=} {additional_identificator=} does not exists in school with id {school_id}",
        )
    logger.debug(
        f"Successfully found subclass with params {educational_level=} {identificator=} {additional_identificator=} in school with id {school_id}"
    )
    return subclass


def get_cabinet_by_id(session: Session, uid: int) -> database.Cabinet:
    logger.debug(f"Searching for cabinter with id {uid}")
    cabinet = session.query(database.Cabinet).filter_by(id=uid).first()
    if cabinet is None:
        logger.debug(
            f"Raised an exception because cabinet with id {uid} does not exists"
        )
        raise HTTPException(
            status_code=404, detail=f"Cabinet with id {uid} does not exists"
        )
    logger.debug(f"Successfully found cabinet with id {uid}")
    return cabinet


def check_unique_account_by_telegram_id(session: Session, telegram_id: int):
    logger.debug(f"Searching account with telegram id {telegram_id}")
    account = session.query(database.Account).filter_by(telegram_id=telegram_id).first()

    if account is not None:
        logger.debug(
            f"Raised an exception because account with telegram id {telegram_id} is already exists"
        )
        raise HTTPException(
            status_code=409,
            detail=f"Account with telegram id {telegram_id} is already exists",
        )
    logger.debug(f"Account with telegram id {telegram_id} does not exists")


def get_lesson_by_id(session: Session, uid: int) -> database.Lesson:
    logger.debug(f"Searching lesson with id {uid}")
    lesson = session.query(database.Lesson).filter_by(id=uid).first()

    if lesson is None:
        logger.debug(
            f"Raised an exception because lesson with id {uid} does not exists"
        )
        raise HTTPException(
            status_code=404, detail=f"Lesson with id {uid} does not exists"
        )
    logger.debug(f"Successfully found lesson with id {uid}")
    return lesson


def get_account_by_telegram_id(session: Session, telegram_id: int) -> database.Account:
    logger.debug(f"Searching account with telegram id {telegram_id}")
    account = session.query(database.Account).filter_by(telegram_id=telegram_id).first()

    if account is None:
        logger.debug(
            f"Raised an exception because account with telegram id {telegram_id} does not exists"
        )
        raise HTTPException(
            status_code=404,
            detail=f"Account with telegram id {telegram_id} does not exists",
        )
    logger.debug(f"Successfully found account with telegram id {telegram_id}")

    return account


def get_role_by_id(session: Session, uid: int) -> database.Role:
    logger.debug(f"Searching role with id {uid}")
    role = session.query(database.Role).filter_by(id=uid).first()

    if role is None:
        logger.debug(
            f"Raised an exception because account with role id {uid} does not exists"
        )
        raise HTTPException(
            status_code=404,
            detail=f"Role with role id {uid} does not exists",
        )
    logger.debug(f"Successfully found role with id {uid}")

    return role
