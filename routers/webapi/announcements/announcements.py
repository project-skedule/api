# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false


from typing import List
from routers.webapi.announcements.utils import process_announcement, send_to_transmitter
import valid_db_requests as db_validated
from config import API_ANNOUNCEMENTS_PREFIX, API_PREFIX, MAX_HISTORY_RESULTS
from config import DEFAULT_LOGGER as logger
from config import Access, get_session
from extra import create_logger_dependency
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels
from extra.tags import ANNOUNCEMENTS, WEBSITE
from api_types import ID
from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from models import database
from models.web import incoming, outgoing


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
    teachers, subclasses, ids = process_announcement(session, request, save=True)
    await send_to_transmitter(request.text, ids)
    return outgoing.AnnouncementsPreview(
        teachers=[outgoing.preview.Teacher.from_orm(t) for t in teachers],
        subclasses=[outgoing.preview.Subclass.from_orm(s) for s in subclasses],
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
    teachers, subclasses, _ = process_announcement(session, session)
    return outgoing.AnnouncementsPreview(
        teachers=[outgoing.preview.Teacher.from_orm(t) for t in teachers],
        subclasses=[outgoing.preview.Subclass.from_orm(s) for s in subclasses],
        sent_to_parents=request.resend_to_parents,
        sent_only_to_parents=request.sent_only_to_parents,
    )


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
    await send_to_transmitter(request.text, telegram_ids)
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
