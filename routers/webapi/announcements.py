# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
import valid_db_requests as db_validated
from config import API_ANNOUNCEMENTS_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import get_session, TRANSMITTER_HOST, TRANSMITTER_PORT
from extra import create_logger_dependency
from extra.tags import ANNOUNCEMENTS, WEBSITE
from models import database
from models.web import incoming, outgoing
import aiohttp

router = APIRouter(
    prefix=API_PREFIX + API_ANNOUNCEMENTS_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
)


@router.post(
    "/create",
    tags=[ANNOUNCEMENTS, WEBSITE],
    response_model=outgoing.AnnouncementsPreview,
)
async def post_new_announcement(request: incoming.Announcement):
    with get_session() as session:
        school = db_validated.get_school_by_id(session, request.school_id)

        teachers = set()
        subclasses = set()
        telegram_ids = set()

        roles = set()

        if request.filters is not None:

            for filter_object in request.filters:
                if isinstance(filter_object, incoming.announcement.Teacher):
                    teacher_roles = (
                        session.query(database.Role)
                        .join(database.Teacher)
                        .filter_by(role_type=database.RoleEnum.TEACHER)
                        .filter(database.Role.teacher.name == filter_object.name)
                        .all()
                    )
                    for teacher_role in teacher_roles:
                        teachers.add(teacher_role.teacher.name)
                        telegram_ids.add(teacher_role.account.id)

                else:
                    student_roles = session.query(database.Role).filter_by(
                        role_type=database.RoleEnum.STUDENT
                    )
                    students = session.query(database.Student).filter_by(
                        school_id=school.id
                    )

                    if filter_object.educational_level is not None:
                        student_roles = student_roles.filter(
                            database.Role.student.subclass.educational_level
                            == filter_object.educational_level
                        )
                        students = students.filter(
                            database.Student.subclass.educational_level
                            == filter_object.educational_level
                        )
                    if filter_object.identificator is not None:
                        student_roles = student_roles.filter(
                            database.Role.student.subclass.identificator
                            == filter_object.identificator
                        )
                        students = students.filter(
                            database.Student.subclass.identificator
                            == filter_object.identificator
                        )
                    if filter_object.additional_identificator is not None:
                        student_roles = student_roles.filter(
                            database.Role.student.subclass.additional_identificator
                            == filter_object.additional_identificator
                        )
                        students = students.filter(
                            database.Student.subclass.additional_identificator
                            == filter_object.additional_identificator
                        )

                    student_roles = student_roles.all()

                    for student_role in student_roles:
                        subclasses.add(
                            outgoing.Subclass(
                                educational_level=student_role.student.subclass.educational_level,
                                identificator=student_role.student.subclass.identificator,
                                additional_identificator=student_role.student.subclass.additional_identificator,
                            )
                        )
                        telegram_ids.add(student_role.account.id)

                    students = students.all()

                    for student in students:
                        if student.parent is not None:
                            telegram_ids.add(student.parent.account.telegram_id)

        else:
            student_roles = (
                session.query(database.Role)
                .join(database.Student)
                .filter(database.Role.student.school.id == school.id)
                .all()
            )

            teachers_roles = (
                session.query(database.Teacher).filter_by(school_id=school.id).all()
            )

            children = (
                session.query(database.Student).filter_by(school_id=school.id).all()
            )

            for child in children:
                if child.parent is not None:
                    telegram_ids.add(child.parent.account.telegram_id)

            for teacher_role in teachers_roles:
                teachers.add(teacher_role.teacher.name)
                telegram_ids.add(teacher_role.account.telegram_id)

            for student_role in student_roles:
                subclasses.add(
                    outgoing.Subclass(
                        educational_level=student_role.student.subclass.educational_level,
                        identificator=student_role.student.subclass.identificator,
                        additional_identificator=student_role.student.subclass.additional_identificator,
                    )
                )
                telegram_ids.add(student_role.account.telegram_id)

        async with aiohttp.ClientSession() as http_session:
            async with http_session.post(
                f"http://{TRANSMITTER_HOST}:{TRANSMITTER_PORT}/api/trans/redirect/telegram",
                json={"text": request.text, "telegram_ids": list(telegram_ids)},
            ) as response:
                if response.status != 200:
                    logger.error(
                        f"Can not post announcement to {TRANSMITTER_HOST}:{TRANSMITTER_PORT}. More: {await response.text()}"
                    )
                    raise HTTPException(
                        status_code=500, detail="Can not post your announcement"
                    )

        return outgoing.AnnouncementsPreview(
            teachers=list(teachers), subclasses=list(subclasses)
        )
