# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false

from typing import List, Optional

import Levenshtein  # pyright: reportMissingTypeStubs=false
import valid_db_requests as db_validated
from api_types import ID, TID
from config import API_INFO_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import MAX_LEVENSHTEIN_RESULTS, Access, get_session
from extra import create_logger_dependency
from extra.api_router import LoggingRouter
from extra.service_auth import AllowLevels, get_current_service
from extra.tags import (
    CABINET,
    CORPUS,
    INFO,
    LESSON,
    LESSON_NUMBER,
    SCHOOL,
    SUBCLASS,
    TEACHER,
    TELEGRAM,
    WEBSITE,
    TAG,
)
from fastapi import APIRouter, Depends, HTTPException
from models import database
from models.bot import incoming, info, item, telegram
from pydantic import Field
from typing_extensions import Annotated

allowed = AllowLevels(Access.Admin, Access.Telegram, Access.Parser)

router = APIRouter(
    prefix=API_PREFIX + API_INFO_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger)), Depends(allowed)],
    route_class=LoggingRouter,
)
logger.info(f"Info router created on {API_PREFIX+API_INFO_PREFIX}")


@router.get("/subclasses/all", tags=[SUBCLASS], response_model=info.Subclasses)
async def get_subclasses(school_id: ID, session=Depends(get_session)):
    school = db_validated.get_school_by_id(session, school_id)
    return info.Subclasses(data=[item.Subclass.from_orm(s) for s in school.subclasses])


@router.get("/tags/all", tags=[TAG], response_model=info.Tags)
async def get_all_tags(session=Depends(get_session)):
    tags = session.query(database.Tag).all()
    return info.Tags(data=[item.Tag.from_orm(t) for t in tags])


@router.get("/teachers/all", tags=[TEACHER], response_model=info.Teachers)
async def get_teachers(school_id: ID, session=Depends(get_session)):
    school = db_validated.get_school_by_id(session, school_id)
    return info.Teachers(data=[item.Teacher.from_orm(t) for t in school.teachers])


@router.get("/parallels/all", tags=[SUBCLASS], response_model=info.Parallels)
async def get_parallels(school_id: ID, session=Depends(get_session)):
    school = db_validated.get_school_by_id(session, school_id)
    return info.Parallels(data=list({i.educational_level for i in school.subclasses}))


@router.get("/teachers/distance", tags=[TEACHER], response_model=info.Teachers)
async def get_teacher_by_levenshtein(
    school_id: ID,
    name: Annotated[str, Field(max_length=200, min_length=1)],
    session=Depends(get_session),
):
    school = db_validated.get_school_by_id(session, school_id)
    name = name.lower()
    teachers = list(school.teachers)
    teachers.sort(
        key=lambda teacher: (
            name not in teacher.name.lower(),
            teacher.name.lower().find(name)
            if teacher.name.lower().find(name) != -1
            else len(teacher.name) + 1,
            Levenshtein.distance(teacher.name.lower(), name),
        )
    )
    teachers = teachers[:MAX_LEVENSHTEIN_RESULTS]
    return info.Teachers(data=[item.Teacher.from_orm(teacher) for teacher in teachers])


@router.get("/teachers/tag", tags=[TAG], response_model=info.Teachers)
async def get_teachers_by_tag(school_id: ID, tag: str, session=Depends(get_session)):
    tag = db_validated.get_tag_by_label(session, tag)
    teachers = (
        session.query(database.Teacher)
        .filter_by(school_id=school_id)
        .filter(database.Teacher.tags.contains(tag))
        .all()
    )
    return info.Teachers(data=[item.Teacher.from_orm(teacher) for teacher in teachers])


@router.get("/letters/all", tags=[SUBCLASS], response_model=info.Letters)
async def get_letters(
    school_id: ID,
    educational_level: Annotated[int, Field(ge=0, le=12)],
    session=Depends(get_session),
):
    school = db_validated.get_school_by_id(session, school_id)
    data = filter(lambda s: s.educational_level == educational_level, school.subclasses)
    return info.Letters(data=sorted(set([s.identificator for s in data])))


@router.get("/groups/all", tags=[SUBCLASS], response_model=info.Groups)
async def get_groups(
    school_id: ID,
    educational_level: Annotated[int, Field(ge=0, le=12)],
    identificator: Annotated[str, Field(max_length=50)],
    session=Depends(get_session),
):
    school = db_validated.get_school_by_id(session, school_id)
    data = filter(
        lambda s: s.educational_level == educational_level
        and s.identificator == identificator,
        school.subclasses,
    )
    return info.Groups(data=sorted(set([s.additional_identificator for s in data])))


@router.get("/schools/all", tags=[SCHOOL], response_model=info.Schools)
async def get_school(session=Depends(get_session)):
    schools = session.query(database.School).all()
    return info.Schools(data=[item.School.from_orm(school) for school in schools])


@router.get("/corpuses/all", tags=[CORPUS], response_model=info.Corpuses)
async def get_corpuses(school_id: ID, session=Depends(get_session)):
    school = db_validated.get_school_by_id(session, school_id)
    return info.Corpuses(data=[item.Corpus.from_orm(c) for c in school.corpuses])


@router.get("/schools/distance", tags=[SCHOOL], response_model=info.Schools)
async def get_schools_by_levenshtein(
    name: Annotated[str, Field(max_length=200, min_length=1)],
    session=Depends(get_session),
):
    schools = (
        session.query(database.School)
        .filter(database.School.name.contains(name))
        .limit(MAX_LEVENSHTEIN_RESULTS)
        .all()
    )
    return info.Schools(data=[item.School.from_orm(school) for school in schools])


@router.get("/cabinets/all", tags=[CABINET], response_model=info.Cabinets)
async def get_cabinets(school_id: ID, session=Depends(get_session)):
    school = db_validated.get_school_by_id(session, school_id)
    return info.Cabinets(data=[item.Cabinet.from_orm(c) for c in school.cabinets])


@router.get("/cabinets/tag", tags=[TAG], response_model=info.Cabinets)
async def get_cabinets_by_tag(school_id: ID, tag: str, session=Depends(get_session)):
    tag = db_validated.get_tag_by_label(tag)
    cabinets = (
        session.query(database.Cabinet)
        .filter_by(school_id=school_id)
        .filter(database.Cabinet.tags.contains(tag))
        .all()
    )
    return info.Cabinets(data=[item.Cabinet.from_orm(cabinet) for cabinet in cabinets])


@router.get("/lessons/all", tags=[LESSON], response_model=info.Lessons)
async def get_lessons(school_id: ID, session=Depends(get_session)):
    school = db_validated.get_school_by_id(session, school_id)
    return info.Lessons(data=[item.Lesson.from_orm(l) for l in school.lessons])


@router.get(
    "/lessontimetables/all", tags=[LESSON_NUMBER], response_model=info.LessonNumbers
)
async def get_all_timetables(school_id: ID, session=Depends(get_session)):
    school = db_validated.get_school_by_id(session, school_id)
    return info.LessonNumbers(
        data=[item.LessonNumber.from_orm(ln) for ln in school.lesson_numbers]
    )


@router.get("/cabinets/free", tags=[CABINET], response_model=info.Cabinets)
async def get_free_cabinet(
    corpus_id: ID,
    day_of_week: Annotated[int, Field(ge=1, le=7)],
    lesson_number: Optional[Annotated[int, Field(ge=0, le=20)]] = None,
    floor: Optional[Annotated[int, Field(ge=-10, le=100)]] = None,
    session=Depends(get_session),
):
    corpus = db_validated.get_corpus_by_id(session, corpus_id)
    cabinet_query = session.query(database.Cabinet).filter_by(corpus_id=corpus.id)

    if floor is not None:
        cabinet_query = cabinet_query.filter_by(floor=floor)
    cabinets = cabinet_query.all()

    cabinets_ids = {cabinet.id for cabinet in cabinets}

    lesson_query = session.query(database.Lesson).filter_by(
        corpus_id=corpus.id, day_of_week=day_of_week
    )

    if lesson_number is not None:
        lesson_query = lesson_query.join(
            (database.Lesson_number, database.Lesson.lesson_number)
        ).filter(database.Lesson_number.number == lesson_number)
    lessons = lesson_query.all()
    for lesson in lessons:
        cabinets_ids.discard(lesson.cabinet_id)
    cabinets = filter(lambda c: c.id in cabinets_ids, cabinets)
    return info.Cabinets(data=[item.Cabinet.from_orm(cabinet) for cabinet in cabinets])


@router.get("/corpus/canteen", tags=[CORPUS], response_model=info.Canteen)
async def get_canteen_text(corpus_id: ID, session=Depends(get_session)):
    return info.Canteen.from_orm(db_validated.get_corpus_by_id(session, corpus_id))


@router.get("/subclass/params", tags=[SUBCLASS], response_model=item.Subclass)
async def get_subclass_by_params(
    school_id: ID,
    educational_level: Annotated[int, Field(ge=0, le=12)],
    identificator: Annotated[str, Field(max_length=50)],
    additional_identificator: Annotated[str, Field(max_length=50)],
    session=Depends(get_session),
) -> item.Subclass:
    school = db_validated.get_school_by_id(session, school_id)
    subclass = db_validated.get_subclass_by_params(
        session,
        school.id,
        educational_level,
        identificator,
        additional_identificator,
    )
    return item.Subclass.from_orm(subclass)


@router.get(
    "/check/telegramid",
    tags=[TELEGRAM],
    response_model=item.Result,
    dependencies=[Depends(AllowLevels(Access.Admin, Access.Telegram))],
)
async def check_existence(telegram_id: TID, session=Depends(get_session)):
    account = session.query(database.Account).filter_by(telegram_id=telegram_id).first()
    return item.Result(data=account is not None)


@router.get(
    "/telegramid/all",
    tags=[TELEGRAM],
    response_model=List[int],
    dependencies=[Depends(AllowLevels(Access.Admin))],
)
async def get_all_users(session=Depends(get_session)):
    return [acc.telegram_id for acc in session.query(database.Account).all()]
