# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false, reportGeneralTypeIssues=false

from typing import List, Optional
from typing_extensions import Annotated
from pydantic import Field
import Levenshtein  # pyright: reportMissingTypeStubs=false
from fastapi import APIRouter, Depends
from extra.auth import get_current_user
from api_types import ID, TID
import valid_db_requests as db_validated
from config import API_INFO_PREFIX, API_PREFIX
from config import DEFAULT_LOGGER as logger
from config import MAX_LEVENSHTEIN_RESULTS, get_session
from extra import create_logger_dependency
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
)
from models import database
from models.bot import incoming, info, item, telegram

router = APIRouter(
    prefix=API_PREFIX + API_INFO_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
)
logger.info(f"Info router created on {API_PREFIX+API_INFO_PREFIX}")


@router.get(
    "/subclasses/all",
    tags=[INFO, SUBCLASS, WEBSITE, TELEGRAM],
    response_model=info.Subclasses,
)
async def get_subclasses(school_id: ID, _=Depends(get_current_user)) -> info.Subclasses:
    with get_session() as session:
        school = db_validated.get_school_by_id(session, school_id)
        return info.Subclasses(
            data=[
                item.Subclass(
                    id=subclass.id,
                    educational_level=subclass.educational_level,
                    identificator=subclass.identificator,
                    additional_identificator=subclass.additional_identificator,
                )
                for subclass in school.subclasses
            ]
        )


@router.get(
    "/teachers/all",
    tags=[INFO, TEACHER, WEBSITE, TELEGRAM],
    response_model=info.Teachers,
)
async def get_teachers(school_id: ID, _=Depends(get_current_user)) -> info.Teachers:
    with get_session() as session:
        school = db_validated.get_school_by_id(session, school_id)
        return info.Teachers(
            data=[
                item.Teacher(
                    name=teacher.name,
                    id=teacher.id,
                )
                for teacher in school.teachers
            ]
        )


@router.get(
    "/parallels/all",
    tags=[INFO, SUBCLASS, WEBSITE, TELEGRAM],
    response_model=info.Parallels,
)
async def get_parallels(school_id: ID, _=Depends(get_current_user)) -> info.Parallels:
    with get_session() as session:
        school = db_validated.get_school_by_id(session, school_id)
        return info.Parallels(
            data=list({i.educational_level for i in school.subclasses})
        )


@router.get(
    "/teachers/distance", tags=[INFO, TEACHER, TELEGRAM], response_model=info.Teachers
)
async def get_teacher_by_levenshtein(
    school_id: ID,
    name: Annotated[str, Field(max_length=200, min_length=1)],
    _=Depends(get_current_user),
) -> info.Teachers:
    with get_session() as session:
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
        return info.Teachers(
            data=[
                item.Teacher(
                    name=teacher.name,
                    id=teacher.id,
                )
                for teacher in teachers
            ]
        )


@router.get(
    "/letters/all",
    tags=[INFO, SUBCLASS, WEBSITE, TELEGRAM],
    response_model=info.Letters,
)
async def get_letters(
    school_id: ID,
    educational_level: Annotated[int, Field(ge=0, le=12)],
    _=Depends(get_current_user),
) -> info.Letters:
    with get_session() as session:
        school = db_validated.get_school_by_id(session, school_id)
        data = []
        for i in school.subclasses:
            if i.educational_level == educational_level:
                l = i.identificator
                if l not in data:
                    data.append(l)
        return info.Letters(data=data)


@router.get(
    "/groups/all",
    tags=[INFO, SUBCLASS, WEBSITE, TELEGRAM],
    response_model=info.Groups,
)
async def get_groups(
    school_id: ID,
    educational_level: Annotated[int, Field(ge=0, le=12)],
    identificator: Annotated[str, Field(max_length=50)],
    _=Depends(get_current_user),
) -> info.Groups:
    with get_session() as session:
        school = db_validated.get_school_by_id(session, school_id)
        data = []
        for i in school.subclasses:
            if (
                i.educational_level == educational_level
                and i.identificator == identificator
            ):
                g = i.additional_identificator
                if g not in data:
                    data.append(g)

        return info.Groups(data=data)


@router.get(
    "/schools/all",
    tags=[INFO, SCHOOL, WEBSITE, TELEGRAM],
    response_model=info.Schools,
)
async def get_school(_=Depends(get_current_user)) -> info.Schools:
    with get_session() as session:
        schools = session.query(database.School).all()
        return info.Schools(
            data=[item.School(name=school.name, id=school.id) for school in schools]
        )


@router.get(
    "/corpuses/all",
    tags=[INFO, CORPUS, WEBSITE, TELEGRAM],
    response_model=info.Corpuses,
)
async def get_corpuses(school_id: ID, _=Depends(get_current_user)) -> info.Corpuses:
    with get_session() as session:
        school = db_validated.get_school_by_id(session, school_id)
        return info.Corpuses(
            data=[
                item.Corpus(name=corpus.name, address=corpus.address, id=corpus.id)
                for corpus in school.corpuses
            ]
        )


@router.get(
    "/schools/distance",
    tags=[INFO, SCHOOL, TELEGRAM],
    response_model=info.Schools,
)
async def get_schools_by_levenshtein(
    name: Annotated[str, Field(max_length=200, min_length=1)],
    _=Depends(get_current_user),
) -> info.Schools:
    with get_session() as session:
        schools = (
            session.query(database.School)
            .filter(database.School.name.contains(name))
            .limit(MAX_LEVENSHTEIN_RESULTS)
            .all()
        )
        return info.Schools(
            data=[item.School(name=school.name, id=school.id) for school in schools]
        )


@router.get(
    "/cabinets/all", tags=[INFO, CABINET, TELEGRAM], response_model=info.Cabinets
)
async def get_cabinets(school_id: ID, _=Depends(get_current_user)) -> info.Cabinets:
    with get_session() as session:
        school = db_validated.get_school_by_id(session, school_id)
        return info.Cabinets(
            data=[
                item.Cabinet(
                    name=cabinet.name,
                    floor=cabinet.floor,
                    id=cabinet.id,
                    corpus=item.Corpus(
                        address=cabinet.corpus.address,
                        name=cabinet.corpus.name,
                        id=cabinet.corpus.id,
                    ),
                )
                for cabinet in school.cabinets
            ]
        )


@router.get("/lessons/all", tags=[INFO, LESSON, TELEGRAM], response_model=info.Lessons)
async def get_lessons(school_id: ID, _=Depends(get_current_user)) -> info.Lessons:
    with get_session() as session:
        school = db_validated.get_school_by_id(session, school_id)
        return info.Lessons(
            data=[
                item.Lesson(
                    id=lesson.id,
                    lesson_number=item.LessonNumber(
                        id=lesson.lesson_number.id,
                        number=lesson.lesson_number.number,
                        time_start=lesson.lesson_number.time_start,
                        time_end=lesson.lesson_number.time_end,
                    ),
                    subject=lesson.subject,
                    teacher=item.Teacher(
                        name=lesson.teacher.name, id=lesson.teacher.id
                    ),
                    day_of_week=lesson.day_of_week,
                    subclasses=[
                        item.Subclass(
                            id=subclass.id,
                            educational_level=subclass.educational_level,
                            identificator=subclass.identificator,
                            additional_identificator=subclass.additional_identificator,
                        )
                        for subclass in lesson.subclasses
                    ],
                    cabinet=item.Cabinet(
                        id=lesson.cabinet.id,
                        floor=lesson.cabinet.floor,
                        name=lesson.cabinet.name,
                        corpus=item.Corpus(
                            address=lesson.corpus.address,
                            name=lesson.corpus.name,
                            id=lesson.corpus.id,
                        ),
                    ),
                    school=item.School(
                        name=lesson.school.name,
                        id=lesson.school.id,
                    ),
                )
                for lesson in session.query(database.Lesson)
                .filter_by(school_id=school.id)
                .all()
            ]
        )


@router.get(
    "/lessontimetables/all",
    tags=[INFO, LESSON_NUMBER, TELEGRAM],
    response_model=info.LessonNumbers,
)
async def get_all_timetables(
    school_id: ID, _=Depends(get_current_user)
) -> info.LessonNumbers:
    with get_session() as session:
        school = db_validated.get_school_by_id(session, school_id)
        timetables = (
            session.query(database.Lesson_number).filter_by(school_id=school.id).all()
        )
        return info.LessonNumbers(
            data=[
                item.LessonNumber(
                    id=lesson_number.id,
                    number=lesson_number.number,
                    time_start=lesson_number.time_start,
                    time_end=lesson_number.time_end,
                )
                for lesson_number in timetables
            ]
        )


@router.get(
    "/cabinets/free", tags=[INFO, CABINET, TELEGRAM], response_model=info.Cabinets
)
async def get_free_cabinet(
    corpus_id: ID,
    day_of_week: Annotated[int, Field(ge=1, le=7)],
    lesson_number: Optional[Annotated[int, Field(ge=0, le=20)]] = None,
    floor: Optional[Annotated[int, Field(ge=-10, le=100)]] = None,
    _=Depends(get_current_user),
) -> info.Cabinets:
    with get_session() as session:
        corpus = db_validated.get_corpus_by_id(session, corpus_id)

        cabinets = session.query(database.Cabinet).filter_by(corpus_id=corpus.id)

        if floor is not None:
            cabinets = cabinets.filter_by(floor=floor)
        cabinets = cabinets.all()

        cabinets_ids = {cabinet.id for cabinet in cabinets}

        lessons = (
            session.query(database.Lesson)
            .filter_by(corpus_id=corpus.id, day_of_week=day_of_week)
            .all()
        )

        if lesson_number is not None:
            lessons = filter(
                lambda lesson: lesson.lesson_number.number == lesson_number,
                lessons,
            )
        lessons = list(lessons)

        for lesson in lessons:
            cabinets_ids.discard(lesson.cabinet_id)

        cabinets = [cabinet for cabinet in cabinets if cabinet.id in cabinets_ids]

        return info.Cabinets(
            data=[
                item.Cabinet(
                    id=cabinet.id,
                    floor=cabinet.floor,
                    name=cabinet.name,
                    corpus=item.Corpus(
                        address=cabinet.corpus.address,
                        name=cabinet.corpus.name,
                        id=cabinet.corpus.id,
                    ),
                )
                for cabinet in cabinets
            ]
        )


@router.get("/corpus/canteen", tags=[CORPUS, TELEGRAM], response_model=info.Canteen)
async def get_canteen_text(corpus_id: ID, _=Depends(get_current_user)) -> info.Canteen:
    with get_session() as session:
        corpus = db_validated.get_corpus_by_id(session, corpus_id)

        if corpus.canteen_text is None:
            text = "Ваша школа не предоставила расписание столовой для этого корпуса"
        else:
            text = corpus.canteen_text

        return info.Canteen(data=text)


@router.get("/subclass/params", tags=[SUBCLASS, TELEGRAM], response_model=item.Subclass)
async def get_subclass_by_params(
    school_id: ID,
    educational_level: Annotated[int, Field(ge=0, le=12)],
    identificator: Annotated[str, Field(max_length=50)],
    additional_identificator: Annotated[str, Field(max_length=50)],
    _=Depends(get_current_user),
) -> item.Subclass:
    with get_session() as session:
        school = db_validated.get_school_by_id(session, school_id)
        subclass = db_validated.get_subclass_by_params(
            session,
            school.id,
            educational_level,
            identificator,
            additional_identificator,
        )
        return item.Subclass(
            educational_level=subclass.educational_level,
            identificator=subclass.identificator,
            additional_identificator=subclass.additional_identificator,
            id=subclass.id,
        )


@router.get("/check/telegramid", tags=[TELEGRAM], response_model=item.Result)
async def check_existence(telegram_id: TID, _=Depends(get_current_user)) -> item.Result:
    with get_session() as session:
        account = (
            session.query(database.Account).filter_by(telegram_id=telegram_id).first()
        )
        if account is None:
            return item.Result(data=False)
        return item.Result(data=True)


@router.get("/telegramid/all", tags=[TELEGRAM], response_model=List[int])
async def get_all_users(_=Depends(get_current_user)) -> List[int]:
    with get_session() as session:
        return [acc.telegram_id for acc in session.query(database.Account).all()]
