from typing import List, Set, Tuple, Union
from sqlalchemy.orm.session import Session
from models import database
from sqlalchemy import Column
import valid_db_requests as db_validated
from models import database
from models.web import incoming
from sqlalchemy import Column
import aiohttp
from fastapi.exceptions import HTTPException
from config import TRANSMITTER_HOST, TRANSMITTER_PORT
from config import DEFAULT_LOGGER as logger
from telegraph.aio import Telegraph
from telegraph.exceptions import InvalidHTML


def get_students(
    session: Session, subclasses: Set[database.Subclass]
) -> Tuple[Set[Column], Set[database.Role]]:
    telegram_ids = set()
    roles = set()

    student_query = (
        session.query(database.Role)
        .filter_by(role_type=database.RoleEnum.STUDENT)
        .join((database.Student, database.Role.student))
        .join((database.Subclass, database.Student.subclass))
        .filter(database.Subclass.id.in_([s.id for s in subclasses]))
        .all()
    )

    for role in student_query:
        telegram_ids.add(role.account.telegram_id)
        roles.add(role)

    return telegram_ids, roles


def get_teachers(
    session, teachers: Set[database.Teacher]
) -> Tuple[Set[Column], Set[database.Role]]:
    telegram_ids = set()
    roles = set()

    teachers_query: List[database.Role] = (
        session.query(database.Role)
        .filter_by(role_type=database.RoleEnum.TEACHER)
        .join((database.Teacher, database.Role.teacher))
        .filter(database.Teacher.id.in_([t.id for t in teachers]))
        .all()
    )

    for role in teachers_query:
        telegram_ids.add(role.account.telegram_id)
        roles.add(role)

    return telegram_ids, roles


def get_parents(
    session: Session, subclasses: Set[database.Subclass]
) -> Tuple[Set[Column], Set[database.Parent]]:
    telegram_ids = set()
    roles = set()

    parents_query = (
        session.query(database.Role).filter_by(role_type=database.RoleEnum.PARENT).all()
    )

    for parent in parents_query:
        if any(child.subclass in subclasses for child in parent.parent.children):
            roles.add(parent)

    for role in roles:
        telegram_ids.add(role.account.telegram_id)

    return telegram_ids, roles


async def process_announcement(
    session, request, save=False
) -> Tuple[Set[database.Teacher], Set[database.Subclass]]:
    school = db_validated.get_school_by_id(session, request.school_id)

    teachers = set()
    subclasses = set()

    telegram_ids = set()
    roles = set()

    for _filter in request.filters:
        if isinstance(_filter, incoming.announcement.Teacher):
            teachers.add(
                db_validated.get_teacher_by_name(
                    session, _filter.name, request.school_id
                )
            )
        elif isinstance(_filter, incoming.announcement.Subclass):
            filtered = False
            sc_query = session.query(database.Subclass).filter_by(school_id=school.id)

            if _filter.educational_level is not None:
                filtered = True
                sc_query = sc_query.filter_by(
                    educational_level=_filter.educational_level
                )

            if _filter.additional_identificator is not None:
                filtered = True
                sc_query = sc_query.filter_by(
                    additional_identificator=_filter.additional_identificator
                )

            if _filter.identificator is not None:
                filtered = True
                sc_query = sc_query.filter_by(identificator=_filter.identificator)

            if filtered:
                for subclass in sc_query.all():
                    subclasses.add(subclass)
    if teachers:
        teacher_telegram_ids, teacher_roles = get_teachers(session, teachers)
    else:
        teacher_telegram_ids, teacher_roles = set(), set()

    if not request.send_only_to_parents:
        students_telegram_ids, students_roles = get_students(session, subclasses)
    else:
        students_telegram_ids, students_roles = set(), set()

    if request.resend_to_parents:
        parent_telegram_ids, parent_roles = get_parents(session, subclasses)
    else:
        parent_telegram_ids, parent_roles = set(), set()

    roles = teacher_roles | students_roles | parent_roles
    telegram_ids = teacher_telegram_ids | students_telegram_ids | parent_telegram_ids

    if save:
        link = await publish_to_telegraph(request.title, request.text)
        logger.info(link)
        announcement = database.Announcement(title=request.title, link=link)
        for role in roles:
            announcement.roles.append(role)

        session.add(announcement)
        session.commit()

        await send_to_transmitter(link, telegram_ids, silent=request.silent)

    return teachers, subclasses


async def send_to_transmitter(
    text: str, telegram_ids: Union[List[Column], Set[Column]], silent: bool = False
):
    async with aiohttp.ClientSession() as http_session:
        async with http_session.post(
            f"http://{TRANSMITTER_HOST}:{TRANSMITTER_PORT}/api/trans/redirect/telegram",
            json={"text": text, "telegram_ids": list(telegram_ids), "silent": silent},
        ) as response:
            if response.status != 200:
                logger.error(
                    f"Can not post announcement to {TRANSMITTER_HOST}:{TRANSMITTER_PORT}. More: {await response.text()}"
                )
                raise HTTPException(
                    status_code=500, detail="Can not post your announcement"
                )


async def publish_to_telegraph(title: str, text: str) -> str:
    client = Telegraph()
    await client.create_account(
        short_name="skedule_bot",
        author_name="Skedule Publisher",
        author_url="https://t.me/skedule_bot",
        replace_token=True,
    )
    try:
        page = await client.create_page(
            title,
            html_content=text,
            author_name="Skedule Publisher",
            author_url="https://t.me/skedule_bot",
        )
    except InvalidHTML as e:
        raise HTTPException(status_code=404, detail=f"Invalid HTML: {e}")

    return page["url"]
