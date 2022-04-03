from typing import List
from sqlalchemy.orm.session import Session
from models import database

INFO = "#info"
SUBCLASS = "#subclass"
TELEGRAM = "#telegram"
WEBSITE = "#website"
REGISTRATION = "#registration"
CABINET = "#cabinet"
CORPUS = "#corpus"
LESSON = "#lesson"
LESSON_NUMBER = "#lesson_number"
SCHOOL = "#school"
TEACHER = "#teacher"
STUDENT = "#student"
ADMINISTRATION = "#administration"
PARENT = "#parent"
ANNOUNCEMENTS = "#announcements"
STATS = "#stats"
TAG = "#tags"


def get_tags(session: Session, request: List[str]) -> List[database.Tag]:
    tags = []
    for request_tag in request:
        tag = session.query(database.Tag).filter_by(label=request_tag.lower()).first()
        if tag is None:
            tag = database.Tag(label=request_tag.lower())
            session.add(tag)
        tags.append(tag)
    return tags
