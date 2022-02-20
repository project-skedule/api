# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


from fastapi import APIRouter, Depends
import valid_db_requests as db_validated
from config import API_PREFIX, API_REGISTRATION_PREFIX
from config import DEFAULT_LOGGER as logger
from config import get_session
from extra import create_logger_dependency
from extra.tags import ADMINISTRATION, PARENT, STUDENT, TEACHER, TELEGRAM
from models import database
from models.bot import item
from models.bot.telegram import incoming, outgoing
from models.bot.telegram.outgoing import registered

router = APIRouter(
    prefix=API_PREFIX + API_REGISTRATION_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
)
logger.info(f"Registation router created on {API_PREFIX+API_REGISTRATION_PREFIX}")


@router.post("/student", tags=[TELEGRAM, STUDENT], response_model=registered.Student)
async def register_student(request: incoming.Student):
    with get_session() as session:
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

        return registered.Student(
            premium_status=account.premium_status,
            last_payment_data=account.last_payment_data,
            subscription_until=account.subscription_until,
            main_role=outgoing.StudentRole(
                is_main_role=role.is_main_role,
                role_type=role.role_type,
                data=outgoing.Student(
                    subclass=item.Subclass(
                        id=role.student.subclass.id,
                        educational_level=role.student.subclass.educational_level,
                        identificator=role.student.subclass.identificator,
                        additional_identificator=role.student.subclass.additional_identificator,
                    ),
                    school=item.School(
                        name=role.student.school.name,
                        id=role.student.school.id,
                    ),
                ),
            ),
        )


@router.post("/teacher", tags=[TEACHER, TELEGRAM], response_model=registered.Teacher)
async def register_teacher(request: incoming.Teacher):
    with get_session() as session:
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

        return registered.Teacher(
            premium_status=account.premium_status,
            last_payment_data=account.last_payment_data,
            subscription_until=account.subscription_until,
            main_role=outgoing.TeacherRole(
                is_main_role=True,
                role_type=role.role_type,
                data=outgoing.Teacher(
                    teacher_id=role.teacher.id,
                    name=role.teacher.name,
                    school=item.School(
                        name=role.teacher.school.name,
                        id=role.teacher.school.id,
                    ),
                ),
            ),
        )


@router.post(
    "/administration",
    tags=[ADMINISTRATION, TELEGRAM],
    response_model=registered.Administration,
)
async def register_administration(request: incoming.Administration):
    with get_session() as session:
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

        return registered.Administration(
            premium_status=account.premium_status,
            last_payment_data=account.last_payment_data,
            subscription_until=account.subscription_until,
            main_role=outgoing.AdministrationRole(
                is_main_role=True,
                role_type=role.role_type,
                data=outgoing.Administration(
                    school=item.School(
                        name=role.administration.school.name,
                        id=role.administration.school.id,
                    ),
                ),
            ),
        )


@router.post("/parent", tags=[PARENT, TELEGRAM], response_model=registered.Parent)
async def register_parent(request: incoming.Parent):
    with get_session() as session:
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

        return registered.Parent(
            premium_status=account.premium_status,
            last_payment_data=account.last_payment_data,
            subscription_until=account.subscription_until,
            main_role=outgoing.ParentRole(
                is_main_role=role.is_main_role,
                role_type=role.role_type,
                data=outgoing.Parent(
                    parent_id=role.parent.id,
                    children=[
                        outgoing.Child(
                            child_id=student.id,
                            subclass=item.Subclass(
                                id=student.subclass.id,
                                educational_level=student.subclass.educational_level,
                                identificator=student.subclass.identificator,
                                additional_identificator=student.subclass.additional_identificator,
                            ),
                            school=item.School(
                                name=student.subclass.school.name,
                                id=student.subclass.school.id,
                            ),
                        )
                        for student in role.parent.children
                    ],
                ),
            ),
        )
