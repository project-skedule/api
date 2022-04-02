# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


from typing import List

import aiohttp
import valid_db_requests as db_validated
from config import API_ANNOUNCEMENTS_PREFIX, API_PREFIX, MAX_HISTORY_RESULTS
from config import DEFAULT_LOGGER as logger
from config import TRANSMITTER_HOST, TRANSMITTER_PORT, Access, get_session
from extra import create_logger_dependency
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels, get_current_service
from extra.tags import ANNOUNCEMENTS, WEBSITE
from api_types import ID
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from models import database
from models.web import incoming, outgoing
from pydantic import BaseModel

router = APIRouter(
    prefix=API_PREFIX + API_ANNOUNCEMENTS_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
    route_class=LoggingRouter,
)

announcements_allowed = AllowLevels(Access.Admin, Access.Website)


@router.post(
    "/create",
    tags=[ANNOUNCEMENTS, WEBSITE],
    response_model=outgoing.AnnouncementsPreview,
)
async def post_new_announcement(
    request: incoming.Announcement,
    session=Depends(get_session),
    _=Depends(announcements_allowed),
):
    teachers, subclasses, telegram_ids = process_announcement(
        request, session, save_to_database=True
    )

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
        teachers=[teacher.name for teacher in teachers],
        subclasses=[
            outgoing.preview.Subclass(
                educational_level=s.educational_level,
                identificator=s.identificator,
                additional_identificator=s.additional_identificator,
            )
            for s in subclasses
        ],
        sent_to_parents=request.resend_to_parents,
        sent_only_to_parents=request.sent_only_to_parents,
    )


@router.post(
    "/preview",
    tags=[ANNOUNCEMENTS, WEBSITE],
    response_model=outgoing.AnnouncementsPreview,
)
async def preview_announcement(
    request: incoming.Announcement,
    session=Depends(get_session),
    _=Depends(announcements_allowed),
):
    teachers, subclasses, _ = process_announcement(request, session)

    return outgoing.AnnouncementsPreview(
        teachers=[teacher.name for teacher in teachers],
        subclasses=[
            outgoing.preview.Subclass(
                educational_level=s.educational_level,
                identificator=s.identificator,
                additional_identificator=s.additional_identificator,
            )
            for s in subclasses
        ],
        sent_to_parents=request.resend_to_parents,
        sent_only_to_parents=request.sent_only_to_parents,
    )


def process_announcement(request, session, save_to_database=False):
    school = db_validated.get_school_by_id(session, request.school_id)

    teachers = set()
    subclasses = set()
    parents = set()
    telegram_ids = set()
    roles = set()

    for filter_object in request.filters:
        if isinstance(filter_object, incoming.announcement.Teacher):
            teachers_objects = (
                session.query(database.Teacher)
                .filter_by(school_id=school.id, name=filter_object.name)
                .all()
            )
            for teacher in teachers_objects:
                teachers.add(teacher)
        elif isinstance(filter_object, incoming.announcement.Subclass):
            filtered = False
            subclasses_db = session.query(database.Subclass).filter_by(
                school_id=school.id
            )

            if filter_object.educational_level is not None:
                filtered = True
                subclasses_db = subclasses_db.filter_by(
                    educational_level=filter_object.educational_level
                )

            if filter_object.additional_identificator is not None:
                filtered = True
                subclasses_db = subclasses_db.filter_by(
                    additional_identificator=filter_object.additional_identificator
                )

            if filter_object.identificator is not None:
                filtered = True
                subclasses_db = subclasses_db.filter_by(
                    identificator=filter_object.identificator
                )

            if filtered:
                subclasses_db = subclasses_db.all()
            else:
                subclasses_db = []

            for subclass in subclasses_db:
                subclasses.add(subclass)

    teacher_names = [teacher.name for teacher in teachers]

    teacher_roles_db = (
        session.query(database.Role)
        .filter_by(role_type=database.RoleEnum.TEACHER)
        .all()
    )

    teachers_roles = [(role.teacher, role) for role in teacher_roles_db]
    teachers_roles = list(
        filter(lambda pair: pair[0].name in teacher_names, teachers_roles)
    )

    account_ids = [role.account_id for _, role in teachers_roles]
    accounts_db = session.query(database.Account).all()
    accounts_db = list(filter(lambda account: account.id in account_ids, accounts_db))

    for account in accounts_db:
        telegram_ids.add(account.telegram_id)

    for _, role in teachers_roles:
        roles.add(role)

    student_roles_db = (
        session.query(database.Role)
        .filter_by(role_type=database.RoleEnum.STUDENT)
        .all()
    )

    if request.sent_only_to_parents:
        student_roles = []
    else:
        student_roles = [(role.student, role) for role in student_roles_db]

    student_roles = list(
        filter(lambda pair: pair[0].subclass in subclasses, student_roles)
    )

    account_ids = [role.account_id for _, role in student_roles]

    accounts_db = session.query(database.Account).all()
    accounts_db = list(filter(lambda account: account.id in account_ids, accounts_db))

    for account in accounts_db:
        telegram_ids.add(account.telegram_id)

    for _, role in student_roles:
        roles.add(role)

    if request.resend_to_parents:
        parents_db = (
            session.query(database.Role)
            .filter_by(role_type=database.RoleEnum.PARENT)
            .all()
        )

        for parent in parents_db:
            if any(child.subclass in subclasses for child in parent.parent.children):
                parents.add(parent)

        account_ids = [role.account_id for role in parents]

        accounts_db = session.query(database.Account).all()
        accounts_db = list(
            filter(lambda account: account.id in account_ids, accounts_db)
        )

        for account in accounts_db:
            telegram_ids.add(account.telegram_id)

        for role in parents:
            roles.add(role)

    if save_to_database:
        announcement = database.Announcement(link=request.text, school_id=school.id)
        for role in roles:
            announcement.roles.append(role)

        session.add(announcement)
        session.commit()
    return teachers, subclasses, telegram_ids


@router.post(
    "/toall",
    tags=[ANNOUNCEMENTS, WEBSITE],
    response_model=List[int],
)
async def send_to_all(
    request: incoming.SimpleAnnouncement,
    session=Depends(get_session),
    _=Depends(AllowLevels(Access.Admin)),
):
    telegram_ids = [acc.telegram_id for acc in session.query(database.Account).all()]
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
    return telegram_ids


@router.get(
    "/history",
    tags=[ANNOUNCEMENTS, WEBSITE],
    response_model=outgoing.HistoryAnnouncement,
)
async def get_history(
    role_id: ID,
    session=Depends(get_session),
    _=Depends(AllowLevels(Access.Admin, Access.Telegram)),
):
    role = db_validated.get_role_by_id(session, role_id)
    data = list(sorted(role.announcements, key=lambda x: -x.id))[:MAX_HISTORY_RESULTS]
    return outgoing.HistoryAnnouncement(
        data=[outgoing.history.HistoryEntity(link=x.link) for x in data]
    )
