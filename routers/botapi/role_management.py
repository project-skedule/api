# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


from typing import List

import valid_db_requests as db_validated
from api_types.types import TID
from config import API_PREFIX, API_ROLE_MANAGEMENT_PREFIX, BASIC_STATUS_MAX_CHILDREN
from config import DEFAULT_LOGGER as logger
from config import Access, get_session
from extra import create_logger_dependency
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels
from extra.tags import ADMINISTRATION, PARENT, STUDENT, TEACHER, TELEGRAM
from fastapi import APIRouter, Depends, HTTPException
from models import database
from models.bot import incoming as bot_incoming
from models.bot.telegram import incoming, outgoing

router = APIRouter(
    prefix=API_PREFIX + API_ROLE_MANAGEMENT_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
    route_class=LoggingRouter,
)
logger.info(
    f"Role management router created on {API_PREFIX+API_ROLE_MANAGEMENT_PREFIX}"
)

allowed = AllowLevels(Access.Admin, Access.Telegram)


@router.get("/get", tags=[TELEGRAM], response_model=outgoing.Account)
async def get_by_id(telegram_id: TID, session=Depends(get_session), _=Depends(allowed)):
    account = db_validated.get_account_by_telegram_id(session, telegram_id)
    return outgoing.Account.from_orm(account)


@router.put("/add/parent", tags=[PARENT], response_model=outgoing.Account)
def add_parent_role(
    request: incoming.Parent, session=Depends(get_session), _=Depends(allowed)
):
    account = db_validated.get_account_by_telegram_id(session, request.telegram_id)

    if any(role.role_type == database.RoleEnum.PARENT for role in account.roles):
        logger.debug(
            f"Raised an exception because user with telegram id {request.telegram_id} already has parent role"
        )
        raise HTTPException(
            status_code=409,
            detail=f"User with telegram id {request.telegram_id} already has parent role",
        )

    parent = database.Parent()

    role = database.Role(
        is_main_role=False,
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


@router.put("/add/student", tags=[STUDENT], response_model=outgoing.Account)
def add_student_role(
    request: incoming.Student, session=Depends(get_session), _=Depends(allowed)
):
    account = db_validated.get_account_by_telegram_id(session, request.telegram_id)

    if any(role.role_type == database.RoleEnum.STUDENT for role in account.roles):
        logger.debug(
            f"Raised an exception because user with telegram id {request.telegram_id} already has student role"
        )
        raise HTTPException(
            status_code=409,
            detail=f"User with telegram id {request.telegram_id} already has student role",
        )

    subclass = db_validated.get_subclass_by_id(session, request.subclass_id)
    school = db_validated.get_school_by_id(session, subclass.school_id)

    student = database.Student(school=school, subclass=subclass)

    role = database.Role(
        is_main_role=False,
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


@router.put("/add/teacher", tags=[TEACHER], response_model=outgoing.Account)
def add_teacher_role(
    request: incoming.Teacher, session=Depends(get_session), _=Depends(allowed)
):
    account = db_validated.get_account_by_telegram_id(session, request.telegram_id)

    if any(role.role_type == database.RoleEnum.TEACHER for role in account.roles):
        logger.debug(
            f"Raised an exception because user with telegram id {request.telegram_id} already has teacher role"
        )
        raise HTTPException(
            status_code=409,
            detail=f"User with telegram id {request.telegram_id} already has teacher role",
        )
    teacher = db_validated.get_teacher_by_id(session, request.teacher_id)

    role = database.Role(
        is_main_role=False,
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


@router.put(
    "/add/administration", tags=[ADMINISTRATION], response_model=outgoing.Account
)
def add_administration_role(
    request: incoming.Administration, session=Depends(get_session), _=Depends(allowed)
):
    account = db_validated.get_account_by_telegram_id(session, request.telegram_id)

    if any(
        role.role_type == database.RoleEnum.ADMINISTRATION for role in account.roles
    ):
        logger.debug(
            f"Raised an exception because user with telegram id {request.telegram_id} already has administration role"
        )
        raise HTTPException(
            status_code=409,
            detail=f"User with telegram id {request.telegram_id} already has administration role",
        )
    school = db_validated.get_school_by_id(session, request.school_id)

    administration = database.Administration(school=school)

    role = database.Role(
        is_main_role=False,
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


@router.put("/add/child", tags=[PARENT], response_model=outgoing.Account)
async def add_child(
    request: incoming.Child, session=Depends(get_session), _=Depends(allowed)
):
    account = db_validated.get_account_by_telegram_id(session, request.telegram_id)

    for role in account.roles:
        if role.role_type == database.RoleEnum.PARENT:
            break
    else:
        logger.debug(
            f"Raised an exception because user {account.telegram_id} does not have parent role"
        )
        raise HTTPException(
            status_code=409,
            detail=f"User {account.telegram_id} does not have parent role",
        )

    if (
        account.premium_status == 0
        and len(role.parent.children) == BASIC_STATUS_MAX_CHILDREN
    ):
        logger.debug(
            f"Raised an exception because user {account.telegram_id} has premium status {account.premium_status} which allow having only {BASIC_STATUS_MAX_CHILDREN} child(ren)"
        )
        raise HTTPException(
            status_code=409,
            detail=f"User {account.telegram_id} has premium status {account.premium_status} which allow having only {BASIC_STATUS_MAX_CHILDREN} child(ren)",
        )

    subclass = db_validated.get_subclass_by_id(session, request.subclass_id)

    child = database.Student(subclass=subclass, school=subclass.school)

    role.parent.children.append(child)

    session.add(child)
    session.add(account)
    session.commit()

    return outgoing.Account.from_orm(account)


@router.put("/delete/child", tags=[PARENT], response_model=outgoing.Account)
async def remove_child(
    request: bot_incoming.Child, session=Depends(get_session), _=Depends(allowed)
):
    account = db_validated.get_account_by_telegram_id(session, request.telegram_id)

    for role in account.roles:
        if role.role_type == database.RoleEnum.PARENT:
            break
    else:
        logger.debug(
            f"Raised an exception because user {account.telegram_id} does not have parent role"
        )
        raise HTTPException(
            status_code=409,
            detail=f"User {account.telegram_id} does not have parent role",
        )

    parent_id = role.parent.id

    child = (
        session.query(database.Student)
        .filter_by(parent_id=parent_id, id=request.child_id)
        .first()
    )

    session.delete(child)
    session.add(role)
    session.commit()

    return outgoing.Account.from_orm(account)


@router.put("/change/teacher", tags=[TEACHER], response_model=outgoing.Account)
async def change_role_to_teacher(
    request: incoming.Teacher, session=Depends(get_session), _=Depends(allowed)
):
    account = db_validated.get_account_by_telegram_id(session, request.telegram_id)
    teacher = db_validated.get_teacher_by_id(session, request.teacher_id)

    main_role = None
    teacher_role = None

    for role in account.roles:
        if role.role_type == database.RoleEnum.TEACHER:
            teacher_role = role
        if role.is_main_role:
            main_role = role

    if main_role is None:
        logger.critical(f"Found user without main role {request.telegram_id}")
        raise HTTPException(
            status_code=409, detail=f"Invalid user {request.telegram_id}"
        )

    if teacher_role is not None and account.premium_status == 0:
        new_role = database.Role(
            is_main_role=True,
            role_type=database.RoleEnum.TEACHER,
            student=None,
            teacher=teacher,
            parent=None,
            administration=None,
        )
        main_role.is_main_role = False
        session.delete(teacher_role)

        if main_role.student is not None:
            session.delete(main_role.student)
        elif main_role.administration is not None:
            session.delete(main_role.administration)
        elif main_role.parent is not None:
            session.delete(main_role.parent)
        session.delete(main_role)

        account.roles = [new_role]
        session.add(new_role)
        session.add(account)
        session.commit()

        return outgoing.Account.from_orm(account)

        # raise HTTPException(
        #    status_code=409,
        #    detail=f"User {request.telegram_id} already has teacher role",
        # )

    if teacher_role is not None and account.premium_status >= 1:
        main_role.is_main_role = False
        teacher_role.is_main_role = True

        session.add(main_role)
        session.add(teacher_role)
        session.add(account)
        session.commit()

        return outgoing.Account.from_orm(account)

    if account.premium_status >= 1:
        new_role = database.Role(
            is_main_role=True,
            role_type=database.RoleEnum.TEACHER,
            student=None,
            teacher=teacher,
            parent=None,
            administration=None,
        )
        main_role.is_main_role = False
        account.roles.append(new_role)
        session.add(main_role)
    else:
        new_role = database.Role(
            is_main_role=True,
            role_type=database.RoleEnum.TEACHER,
            student=None,
            teacher=teacher,
            parent=None,
            administration=None,
        )

        if main_role.student is not None:
            session.delete(main_role.student)
        elif main_role.administration is not None:
            session.delete(main_role.administration)
        elif main_role.parent is not None:
            session.delete(main_role.parent)
        session.delete(main_role)

        account.roles = [new_role]

    session.add(new_role)
    session.add(account)
    session.commit()

    return outgoing.Account.from_orm(account)


@router.put("/change/parent", tags=[PARENT], response_model=outgoing.Account)
async def change_role_to_parent(
    request: incoming.Parent, session=Depends(get_session), _=Depends(allowed)
):
    account = db_validated.get_account_by_telegram_id(session, request.telegram_id)

    main_role = None
    parent_role = None

    for role in account.roles:
        if role.role_type == database.RoleEnum.PARENT:
            parent_role = role
        if role.is_main_role:
            main_role = role

    if main_role is None:
        logger.critical(f"Found user without main role {request.telegram_id}")
        raise HTTPException(
            status_code=409, detail=f"Invalid user {request.telegram_id}"
        )

    parent = database.Parent()
    if parent_role is not None and account.premium_status == 0:
        new_role = database.Role(
            is_main_role=True,
            role_type=database.RoleEnum.PARENT,
            student=None,
            teacher=None,
            parent=parent,
            administration=None,
        )
        main_role.is_main_role = False

        session.delete(parent_role.parent)
        session.delete(parent_role)

        if main_role.student is not None:
            session.delete(main_role.student)
        elif main_role.administration is not None:
            session.delete(main_role.administration)
        elif main_role.teacher is not None:
            session.delete(main_role.teacher)
        session.delete(main_role)

        account.roles = [new_role]
        session.add(new_role)
        session.add(account)
        session.commit()

        return outgoing.Account.from_orm(account)
        # raise HTTPException(
        #     status_code=409,
        #     detail=f"User {request.telegram_id} already has parent role",
        # )

    if parent_role is not None and account.premium_status >= 1:
        main_role.is_main_role = False
        parent_role.is_main_role = True

        session.add(main_role)
        session.add(parent_role)
        session.add(account)
        session.commit()

        return outgoing.Account.from_orm(account)

    if account.premium_status >= 1:
        new_role = database.Role(
            is_main_role=True,
            role_type=database.RoleEnum.PARENT,
            student=None,
            teacher=None,
            parent=parent,
            administration=None,
        )
        main_role.is_main_role = False
        account.roles.append(new_role)
        session.add(main_role)
    else:
        new_role = database.Role(
            is_main_role=True,
            role_type=database.RoleEnum.PARENT,
            student=None,
            teacher=None,
            parent=parent,
            administration=None,
        )

        if main_role.student is not None:
            session.delete(main_role.student)
        elif main_role.administration is not None:
            session.delete(main_role.administration)
        elif main_role.parent is not None:
            session.delete(main_role.parent)
        session.delete(main_role)

        account.roles = [new_role]

    session.add(new_role)
    session.add(account)
    session.commit()

    return outgoing.Account.from_orm(account)


@router.put("/change/student", tags=[STUDENT], response_model=outgoing.Account)
async def change_role_to_student(
    request: incoming.Student,
    session=Depends(get_session),
    _=Depends(allowed),
):
    account = db_validated.get_account_by_telegram_id(session, request.telegram_id)
    subclass = db_validated.get_subclass_by_id(session, request.subclass_id)

    main_role = None
    student_role = None

    for role in account.roles:
        if role.role_type == database.RoleEnum.STUDENT:
            student_role = role
        if role.is_main_role:
            main_role = role

    if main_role is None:
        logger.critical(f"Found user without main role {request.telegram_id}")
        raise HTTPException(
            status_code=409, detail=f"Invalid user {request.telegram_id}"
        )

    student = database.Student(subclass=subclass, school=subclass.school)
    if student_role is not None and account.premium_status == 0:
        new_role = database.Role(
            is_main_role=True,
            role_type=database.RoleEnum.STUDENT,
            student=student,
            teacher=None,
            parent=None,
            administration=None,
        )
        main_role.is_main_role = False

        session.delete(student_role.student)
        session.delete(student_role)

        if main_role.parent is not None:
            session.delete(main_role.parent)
        elif main_role.administration is not None:
            session.delete(main_role.administration)
        elif main_role.teacher is not None:
            session.delete(main_role.teacher)
        session.delete(main_role)

        account.roles = [new_role]

        session.add(new_role)
        session.add(account)
        session.commit()

        return outgoing.Account.from_orm(account)
        # raise HTTPException(
        #     status_code=409,
        #     detail=f"User {request.telegram_id} already has student role",
        # )

    if student_role is not None and account.premium_status >= 1:
        main_role.is_main_role = False
        student_role.is_main_role = True

        session.add(main_role)
        session.add(student_role)
        session.add(account)
        session.commit()

        return outgoing.Account.from_orm(account)

    if account.premium_status >= 1:
        new_role = database.Role(
            is_main_role=True,
            role_type=database.RoleEnum.STUDENT,
            student=student,
            teacher=None,
            parent=None,
            administration=None,
        )
        main_role.is_main_role = False
        account.roles.append(new_role)
        session.add(main_role)
    else:
        new_role = database.Role(
            is_main_role=True,
            role_type=database.RoleEnum.STUDENT,
            student=student,
            teacher=None,
            parent=None,
            administration=None,
        )

        if main_role.student is not None:
            session.delete(main_role.student)
        elif main_role.administration is not None:
            session.delete(main_role.administration)
        elif main_role.parent is not None:
            session.delete(main_role.parent)
        session.delete(main_role)

        account.roles = [new_role]

    session.add(new_role)
    session.add(account)
    session.commit()

    return outgoing.Account.from_orm(account)


@router.put(
    "/change/administration", tags=[ADMINISTRATION], response_model=outgoing.Account
)
async def change_role_to_administration(
    request: incoming.Administration, session=Depends(get_session), _=Depends(allowed)
):
    account = db_validated.get_account_by_telegram_id(session, request.telegram_id)
    school = db_validated.get_subclass_by_id(session, request.school_id)

    main_role = None
    administration_role = None

    for role in account.roles:
        if role.role_type == database.RoleEnum.ADMINISTRATION:
            administration_role = role
        if role.is_main_role:
            main_role = role

    if main_role is None:
        logger.critical(f"Found user without main role {request.telegram_id}")
        raise HTTPException(
            status_code=409, detail=f"Invalid user {request.telegram_id}"
        )

    administration = database.Administration(school_id=school.id)
    if administration_role is not None and account.premium_status == 0:
        new_role = database.Role(
            is_main_role=True,
            role_type=database.RoleEnum.ADMINISTRATION,
            student=None,
            teacher=None,
            parent=None,
            administration=administration,
        )
        main_role.is_main_role = False

        session.delete(administration_role.administration)
        session.delete(administration_role)

        if main_role.parent is not None:
            session.delete(main_role.parent)
        elif main_role.student is not None:
            session.delete(main_role.student)
        elif main_role.teacher is not None:
            session.delete(main_role.teacher)
        session.delete(main_role)

        account.roles = [new_role]

        session.add(new_role)
        session.add(account)
        session.commit()

        return outgoing.Account.from_orm(account)
        # raise HTTPException(
        #     status_code=409,
        #     detail=f"User {request.telegram_id} already has administration role",
        # )

    if administration_role is not None and account.premium_status >= 1:
        main_role.is_main_role = False
        administration_role.is_main_role = True

        session.add(main_role)
        session.add(administration_role)
        session.add(account)
        session.commit()

        return outgoing.Account.from_orm(account)

    if account.premium_status >= 1:
        new_role = database.Role(
            is_main_role=True,
            role_type=database.RoleEnum.ADMINISTRATION,
            student=None,
            teacher=None,
            parent=None,
            administration=administration,
        )
        main_role.is_main_role = False
        account.roles.append(new_role)
        session.add(main_role)
    else:
        new_role = database.Role(
            is_main_role=True,
            role_type=database.RoleEnum.ADMINISTRATION,
            student=None,
            teacher=None,
            parent=None,
            administration=administration,
        )

        if main_role.student is not None:
            session.delete(main_role.student)
        elif main_role.administration is not None:
            session.delete(main_role.administration)
        elif main_role.parent is not None:
            session.delete(main_role.parent)
        session.delete(main_role)

        account.roles = [new_role]

    session.add(new_role)
    session.add(account)
    session.commit()

    return outgoing.Account.from_orm(account)
