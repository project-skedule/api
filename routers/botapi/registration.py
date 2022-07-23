# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


import valid_db_requests as db_validated
from config import API_PREFIX, API_REGISTRATION_PREFIX
from config import DEFAULT_LOGGER as logger
from config import Access, get_session
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels
from extra.tags import ADMINISTRATION, PARENT, STUDENT, TEACHER
from fastapi import APIRouter, Depends
from models import database
from models.bot.telegram import incoming, outgoing

allowed = AllowLevels(Access.Admin, Access.Telegram)

router = APIRouter(
    prefix=API_PREFIX + API_REGISTRATION_PREFIX,
    dependencies=[Depends(allowed)],
    route_class=LoggingRouter,
)
logger.info(f"Registation router created on {API_PREFIX+API_REGISTRATION_PREFIX}")


@router.post("/student", tags=[STUDENT], response_model=outgoing.Account)
async def register_student(request: incoming.Student, session=Depends(get_session)):
    db_validated.check_unique_account_by_telegram_id(session, request.telegram_id)
    subclass = db_validated.get_subclass_by_id(session, request.subclass_id)
    school = db_validated.get_school_by_id(session, subclass.school_id)

    account = database.Account(
        telegram_id=request.telegram_id,
        premium_status=0,
        last_payment_data=None,
        subscription_until=None,
    )

    student = database.Student(school=school, subclass=subclass)

    role = database.Role(
        is_main_role=True,
        role_type=database.RoleEnum.STUDENT,
        student=student,
        teacher=None,
        parent=None,
        administration=None,
    )
    account.roles.append(role)
    session.add(student)
    session.add(account)
    session.add(role)
    session.commit()

    return outgoing.Account.from_orm(account)


@router.post("/teacher", tags=[TEACHER], response_model=outgoing.Account)
async def register_teacher(request: incoming.Teacher, session=Depends(get_session)):
    db_validated.check_unique_account_by_telegram_id(session, request.telegram_id)
    teacher = db_validated.get_teacher_by_id(session, request.teacher_id)

    account = database.Account(
        telegram_id=request.telegram_id,
        premium_status=0,
        last_payment_data=None,
        subscription_until=None,
    )

    role = database.Role(
        is_main_role=True,
        role_type=database.RoleEnum.TEACHER,
        student=None,
        teacher=teacher,
        parent=None,
        administration=None,
    )

    account.roles.append(role)
    session.add(account)
    session.add(role)
    session.commit()

    return outgoing.Account.from_orm(account)


@router.post("/administration", tags=[ADMINISTRATION], response_model=outgoing.Account)
async def register_administration(
    request: incoming.Administration, session=Depends(get_session)
):
    db_validated.check_unique_account_by_telegram_id(session, request.telegram_id)
    school = db_validated.get_school_by_id(session, request.school_id)
    account = database.Account(
        telegram_id=request.telegram_id,
        premium_status=0,
        last_payment_data=None,
        subscription_until=None,
    )

    administration = database.Administration(school=school)

    role = database.Role(
        is_main_role=True,
        role_type=database.RoleEnum.ADMINISTRATION,
        student=None,
        teacher=None,
        parent=None,
        administration=administration,
    )

    account.roles.append(role)
    session.add(administration)
    session.add(account)
    session.add(role)
    session.commit()

    return outgoing.Account.from_orm(account)


@router.post("/parent", tags=[PARENT], response_model=outgoing.Account)
async def register_parent(request: incoming.Parent, session=Depends(get_session)):
    db_validated.check_unique_account_by_telegram_id(session, request.telegram_id)

    account = database.Account(
        telegram_id=request.telegram_id,
        premium_status=0,
        last_payment_data=None,
        subscription_until=None,
    )

    parent = database.Parent()

    role = database.Role(
        is_main_role=True,
        role_type=database.RoleEnum.PARENT,
        student=None,
        teacher=None,
        parent=parent,
        administration=None,
    )

    account.roles.append(role)
    session.add(parent)
    session.add(account)
    session.add(role)
    session.commit()

    return outgoing.Account.from_orm(account)
