from fastapi import APIRouter, Depends, HTTPException
import valid_db_requests as db_validated
from config import API_ANNOUNCEMENTS_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import SESSION_FACTORY
from extra import create_logger_dependency
from extra.tags import ANNOUNCEMENTS, WEBSITE
from models import database
from models.web import incoming, outgoing

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
    with SESSION_FACTORY() as session:
        school = db_validated.get_school_by_id(session, request.school_id)

        teachers = set()
        subclasses = set()
        telegram_ids = set()

        for filter_object in request.filters:
            if isinstance(filter_object, incoming.announcement.Teacher):
                teacher_roles = (
                    session.query(database.Role)
                    .filter_by(role_type=database.RoleEnum.TEACHER)
                    .filter(database.Role.teacher.name == filter_object.name)
                    .all()
                )
                for teacher_role in teacher_roles:
                    teachers.add(teacher_role.teacher.name)
                    telegram_ids.add(teacher_role.account.id)

            elif isinstance(filter_object, incoming.announcement.Subclass):
                student_roles = session.query(database.Role).filter_by(
                    role_type=database.RoleEnum.STUDENT
                )
                students = session.query(database.Student)

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

                for student_role in student_roles:
                    subclasses.add(
                        outgoing.Subclass(
                            educational_level=student_role.student.subclass.educational_level,
                            identificator=student_role.student.subclass.identificator,
                            additional_identificator=student_role.student.subclass.additional_identificator,
                        )
                    )
                    telegram_ids.add(student_role.account.id)

                for student in students:
                    if student.parent is not None:
                        telegram_ids.add(student.parent.account.telegram_id)
        return outgoing.AnnouncementsPreview(
            teachers=list(teachers), subclasses=list(subclasses)
        )
