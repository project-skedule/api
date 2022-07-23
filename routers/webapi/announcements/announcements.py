# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


from typing import List
from routers.webapi.announcements.utils import (
    process_announcement,
    publish_to_telegraph,
    send_to_transmitter,
)
import valid_db_requests as db_validated
from config import API_ANNOUNCEMENTS_PREFIX, API_PREFIX, MAX_HISTORY_RESULTS
from config import DEFAULT_LOGGER as logger
from config import Access, get_session
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels
from extra.tags import ANNOUNCEMENTS, WEBSITE
from api_types import ID
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from models import database
from models.web import incoming, outgoing

allowed = AllowLevels(Access.Admin, Access.Website)

router = APIRouter(
    prefix=API_PREFIX + API_ANNOUNCEMENTS_PREFIX,
    dependencies=[Depends(allowed)],
    route_class=LoggingRouter,
)


@router.post(
    "/create",
    tags=[ANNOUNCEMENTS, WEBSITE],
    response_model=outgoing.AnnouncementsPreview,
)
async def post_new_announcement(
    request: incoming.Announcement, session=Depends(get_session)
):
    teachers, subclasses = await process_announcement(session, request, save=True)
    return outgoing.AnnouncementsPreview(
        teachers=[outgoing.preview.Teacher.from_orm(t) for t in teachers],
        subclasses=[outgoing.preview.Subclass.from_orm(s) for s in subclasses],
        sent_to_parents=request.resend_to_parents,
        sent_only_to_parents=request.send_only_to_parents,
        silent=request.silent,
    )


@router.post(
    "/preview",
    tags=[ANNOUNCEMENTS, WEBSITE],
    response_model=outgoing.AnnouncementsPreview,
)
async def preview_announcement(
    request: incoming.Announcement, session=Depends(get_session)
):
    teachers, subclasses = await process_announcement(session, session, save=False)
    return outgoing.AnnouncementsPreview(
        teachers=[outgoing.preview.Teacher.from_orm(t) for t in teachers],
        subclasses=[outgoing.preview.Subclass.from_orm(s) for s in subclasses],
        sent_to_parents=request.resend_to_parents,
        sent_only_to_parents=request.send_only_to_parents,
        silent=request.silent,
    )


@router.post(
    "/toall",
    tags=[ANNOUNCEMENTS, WEBSITE],
    response_model=List[int],
    dependencies=[Depends(AllowLevels(Access.Admin))],
)
async def send_to_all(
    request: incoming.SimpleTelegraphAnnouncement, session=Depends(get_session)
):
    link = await publish_to_telegraph(request.title, request.text)
    accounts = session.query(database.Account).all()
    roles = []
    for acc in accounts:
        roles.extend(acc.roles)
    announcement = database.Announcement(link=link, title=request.title)
    for role in roles:
        announcement.roles.append(role)

    session.add(announcement)
    session.commit()

    telegram_ids = [acc.telegram_id for acc in accounts]

    await send_to_transmitter(link, telegram_ids, silent=request.silent)
    return telegram_ids


@router.post("/text/toall", tags=[ANNOUNCEMENTS], response_model=List[int])
async def send_text_to_all(
    request: incoming.SimpleTextAnnouncement,
    session=Depends(get_session),
    _=Depends(AllowLevels(Access.Admin)),
):
    accounts = session.query(database.Account).all()
    telegram_ids = [acc.telegram_id for acc in accounts]
    await send_to_transmitter(request.text, telegram_ids, silent=request.silent)
    return telegram_ids


@router.get(
    "/history",
    tags=[ANNOUNCEMENTS, WEBSITE],
    response_model=outgoing.HistoryAnnouncement,
    dependencies=[Depends(AllowLevels(Access.Admin, Access.Telegram))],
)
async def get_history(role_id: ID, session=Depends(get_session)):
    role = db_validated.get_role_by_id(session, role_id)
    data = list(sorted(role.announcements, key=lambda x: -x.id))[:MAX_HISTORY_RESULTS]
    return outgoing.HistoryAnnouncement(
        data=[outgoing.history.HistoryEntity(link=x.link, title=x.title) for x in data]
    )
