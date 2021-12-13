from typing import List

from fastapi import APIRouter, Depends, HTTPException

import valid_db_requests as db_validated
from config import (
    API_PREFIX,
    API_ROLE_MANAGEMENT_PREFIX,
    BASIC_STATUS_MAX_CHILDREN,
)
from config import DEFAULT_LOGGER as logger
from config import SESSION_FACTORY
from extra import create_logger_dependency
from extra.tags import ADMINISTRATION, PARENT, STUDENT, TEACHER, TELEGRAM
from models import database
from models.bot import item
from models.bot.telegram import incoming, outgoing

router = APIRouter(
    prefix=API_PREFIX + API_ROLE_MANAGEMENT_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
)
logger.info(
    f"Role management router created on {API_PREFIX+API_ROLE_MANAGEMENT_PREFIX}"
)


def account_with_roles(account: database.Account) -> outgoing.Account:
    roles: List[outgoing.Role] = []
    for role in account.roles:
        if role.role_type == database.RoleEnum.STUDENT:
            roles.append(
                outgoing.StudentRole(
                    is_main_role=role.is_main_role,
                    role_type=role.role_type,
                    data=outgoing.Student(
                        subclass_id=role.student.subclass.id,
                        subclass=item.Subclass(
                            educational_level=role.student.subclass.educational_level,
                            identificator=role.student.subclass.identificator,
                            additional_identificator=role.student.subclass.additional_identificator,
                        ),
                        school_id=role.student.school.id,
                        school=item.School(name=role.student.school.name),
                    ),
                )
            )
        elif role.role_type == database.RoleEnum.TEACHER:
            roles.append(
                outgoing.TeacherRole(
                    is_main_role=role.is_main_role,
                    role_type=role.role_type,
                    data=outgoing.Teacher(
                        teacher_id=role.teacher.id,
                        name=role.teacher.name,
                        school=item.School(
                            name=role.teacher.school.name, id=role.teacher.school.id
                        ),
                    ),
                )
            )
        elif role.role_type == database.RoleEnum.PARENT:
            roles.append(
                outgoing.ParentRole(
                    is_main_role=role.is_main_role,
                    role_type=role.role_type,
                    data=outgoing.Parent(
                        children=[
                            outgoing.Child(
                                subclass_id=child.subclass.id,
                                subclass=item.Subclass(
                                    educational_level=child.subclass.educational_level,
                                    identificator=child.subclass.identificator,
                                    additional_identificator=child.subclass.additional_identificator,
                                ),
                                school=item.School(name=child.subclass.school.name),
                            )
                            for child in role.parent.children
                        ]
                    ),
                )
            )
        elif role.role_type == database.RoleEnum.ADMINISTRATION:
            roles.append(
                outgoing.AdministrationRole(
                    is_main_role=role.is_main_role,
                    role_type=role.role_type,
                    data=outgoing.Administration(
                        school_id=role.administration.school.id,
                        school=item.School(name=role.administration.school.name),
                    ),
                )
            )
    return outgoing.Account(
        premium_status=account.premium_status,
        last_payment_data=account.last_payment_data,
        subscription_until=account.subscription_until,
        roles=roles,
    )


@router.get("/get", tags=[TELEGRAM], response_model=outgoing.Account)
async def get_by_id(request: incoming.Account):
    with SESSION_FACTORY() as session:
        account = db_validated.get_account_by_telegram_id(session, request.telegram_id)
        return account_with_roles(account)


@router.put("/add/parent", tags=[TELEGRAM, PARENT], response_model=outgoing.Account)
def add_parent_role(request: incoming.Parent):
    with SESSION_FACTORY() as session:
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

        return account_with_roles(account)


@router.put("/add/student", tags=[TELEGRAM, STUDENT], response_model=outgoing.Account)
def add_student_role(request: incoming.Student):
    with SESSION_FACTORY() as session:
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

        return account_with_roles(account)


@router.put("/add/teacher", tags=[TELEGRAM, TEACHER], response_model=outgoing.Account)
def add_teacher_role(request: incoming.Teacher):
    with SESSION_FACTORY() as session:
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

        return account_with_roles(account)


@router.put(
    "/add/administration",
    tags=[TELEGRAM, ADMINISTRATION],
    response_model=outgoing.Account,
)
def add_administration_role(request: incoming.Administration):
    with SESSION_FACTORY() as session:
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

        return account_with_roles(account)


@router.put("/add/child", tags=[TELEGRAM, PARENT], response_model=outgoing.Account)
async def add_child(request: incoming.Child):
    with SESSION_FACTORY() as session:
        account = db_validated.get_account_by_telegram_id(session, request.parent_id)

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

        return account_with_roles(account)


@router.put(
    "/change/teacher", tags=[TEACHER, TELEGRAM], response_model=outgoing.Account
)
async def change_role_to_teacher(request: incoming.Teacher):
    with SESSION_FACTORY() as session:
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
            raise HTTPException(
                status_code=409,
                detail=f"User {request.telegram_id} already has teacher role",
            )

        if teacher_role is not None and account.premium_status >= 1:
            main_role.is_main_role = False
            teacher_role.is_main_role = True

            session.add(main_role)
            session.add(teacher_role)
            session.add(account)
            session.commit()

            return account_with_roles(account)

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

        return account_with_roles(account)


@router.put("/change/parent", tags=[PARENT, TELEGRAM], response_model=outgoing.Account)
async def change_role_to_parent(request: incoming.Parent):
    with SESSION_FACTORY() as session:
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

        if parent_role is not None and account.premium_status == 0:
            raise HTTPException(
                status_code=409,
                detail=f"User {request.telegram_id} already has parent role",
            )

        if parent_role is not None and account.premium_status >= 1:
            main_role.is_main_role = False
            parent_role.is_main_role = True

            session.add(main_role)
            session.add(parent_role)
            session.add(account)
            session.commit()

            return account_with_roles(account)

        parent = database.Parent()

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

        return account_with_roles(account)


@router.put(
    "/change/student", tags=[STUDENT, TELEGRAM], response_model=outgoing.Account
)
async def change_role_to_student(request: incoming.Student):
    with SESSION_FACTORY() as session:
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

        if student_role is not None and account.premium_status == 0:
            raise HTTPException(
                status_code=409,
                detail=f"User {request.telegram_id} already has student role",
            )

        if student_role is not None and account.premium_status >= 1:
            main_role.is_main_role = False
            student_role.is_main_role = True

            session.add(main_role)
            session.add(student_role)
            session.add(account)
            session.commit()

            return account_with_roles(account)

        student = database.Student(subclass=subclass, school=subclass.school)

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

        return account_with_roles(account)


@router.put(
    "/change/administration",
    tags=[ADMINISTRATION, TELEGRAM],
    response_model=outgoing.Account,
)
async def change_role_to_administration(request: incoming.Administration):
    with SESSION_FACTORY() as session:
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

        if administration_role is not None and account.premium_status == 0:
            raise HTTPException(
                status_code=409,
                detail=f"User {request.telegram_id} already has administration role",
            )

        if administration_role is not None and account.premium_status >= 1:
            main_role.is_main_role = False
            administration_role.is_main_role = True

            session.add(main_role)
            session.add(administration_role)
            session.add(account)
            session.commit()

            return account_with_roles(account)

        administration = database.Administration(school_id=school.id)

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

        return account_with_roles(account)
