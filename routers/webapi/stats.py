from fastapi import APIRouter, Depends, HTTPException
from collections import defaultdict
import valid_db_requests as db_validated
from config import API_PREFIX, API_STATISTICS_PREFIX
from config import DEFAULT_LOGGER as logger
from config import get_session
from extra import create_logger_dependency
from extra.tags import STATS
from models import database
from api_types import ID
from models.web import incoming, outgoing, updating
from pydantic import BaseModel

router = APIRouter(
    prefix=API_PREFIX + API_STATISTICS_PREFIX,
    dependencies=[Depends(create_logger_dependency(logger))],
)
logger.info(f"Statistics router created on {API_PREFIX + API_STATISTICS_PREFIX}")


class Count(BaseModel):
    count: int


@router.get("/teachers", tags=[STATS], response_model=Count)
async def get_teachers_count() -> Count:
    with get_session() as session:
        teachers = (
            session.query(database.Role)
            .filter_by(role_type=database.RoleEnum.TEACHER)
            .all()
        )
        return Count(count=len(teachers))


@router.get("/parents", tags=[STATS], response_model=Count)
async def get_parents_count() -> Count:
    with get_session() as session:
        parents = (
            session.query(database.Role)
            .filter_by(role_type=database.RoleEnum.PARENT)
            .all()
        )
        return Count(count=len(parents))


@router.get("/students", tags=[STATS], response_model=Count)
async def get_students_count() -> Count:
    with get_session() as session:
        students = (
            session.query(database.Role)
            .filter_by(role_type=database.RoleEnum.STUDENT)
            .filter(database.Role.account_id is not None)
            .all()
        )
        return Count(count=len(students))


@router.get("/administrations", tags=[STATS], response_model=Count)
async def get_administrations_count() -> Count:
    with get_session() as session:
        administrations = (
            session.query(database.Role)
            .filter_by(role_type=database.RoleEnum.ADMINISTRATION)
            .all()
        )
        return Count(count=len(administrations))


@router.get("/parallel", tags=[STATS], response_model=outgoing.Statistics)
async def get_parallel_count():
    with get_session() as session:
        students = (
            session.query(database.Role)
            .filter_by(role_type=database.RoleEnum.STUDENT)
            .all()
        )
        data = defaultdict(lambda: 0)
        for student in students:
            data[student.student.subclass.educational_level] += 1

        return outgoing.Statistics(
            data=[outgoing.Stat(number=ed, occurrences=num) for ed, num in data.items()]
        )


@router.get("/children", tags=[STATS], response_model=outgoing.Statistics)
async def get_children_count():
    with get_session() as session:
        parents = (
            session.query(database.Role)
            .filter_by(role_type=database.RoleEnum.PARENT)
            .all()
        )
        data = defaultdict(lambda: 0)
        for parent in parents:
            data[len(parent.parent.children)] += 1

        return outgoing.Statistics(
            data=[
                outgoing.Stat(number=children, occurrences=cnt)
                for children, cnt in data.items()
            ]
        )


@router.get("/teacherparallel", tags=[STATS], response_model=outgoing.Statistics)
async def get_teacher_parallel():
    with get_session() as session:
        teachers = (
            session.query(database.Role)
            .filter_by(role_type=database.RoleEnum.TEACHER)
            .all()
        )

        data = defaultdict(lambda: 0)

        for teacher in teachers:
            lessons = (
                session.query(database.Lesson)
                .filter_by(teacher_id=teacher.teacher.id)
                .all()
            )

            subclasses = set()

            for lesson in lessons:
                for subclass in lesson.subclasses:
                    subclasses.add(subclass.educational_level)

            for subclass in subclasses:
                data[subclass] += 1

        return outgoing.Statistics(
            data=[
                outgoing.Stat(number=parallel, occurrences=cnt)
                for parallel, cnt in data.items()
            ]
        )
