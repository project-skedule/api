# type: ignore

from enum import Enum as EnumClass
from typing import Dict

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Table,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship

Base = declarative_base()


def mod(status: int) -> Dict[str, bool]:
    """
    | Byte | Meaning |
    |:----:|-------|
    |1|Primary key|
    |2|Nullable|
    |3|Autoincrement|
    |4|Unique|
    """
    codes = (0b1000, 0b0100, 0b0010, 0b0001)
    keys = ("primary_key", "nullable", "autoincrement", "unique")
    data = {}
    for code, key in zip(codes, keys):
        flag, status = divmod(status, code)
        data[key] = bool(flag)
    return data


# ==================================================================================================
lesson_subclass_association = Table(
    "lesson_subclass_association",
    Base.metadata,
    Column("lesson_id", Integer, ForeignKey("lesson.id")),
    Column("subclass_id", Integer, ForeignKey("subclass.id")),
)
# ==================================================================================================


class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, **mod(0b1011))
    label = Column(String(length=50), **mod(0b0001))


# ==================================================================================================

cabinet_tag_association = Table(
    "cabinet_tag_association",
    Base.metadata,
    Column("cabinet_id", Integer, ForeignKey("cabinet.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)

# ==================================================================================================
teacher_tag_association = Table(
    "teacher_tag_association",
    Base.metadata,
    Column("teacher_id", Integer, ForeignKey("teacher.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
)
# ==================================================================================================


class Account(Base):
    __tablename__ = "account"
    id = Column(Integer, **mod(0b1011))
    telegram_id = Column(BigInteger, **mod(0b0001))
    premium_status = Column(SmallInteger, default=0, **mod(0b0000))
    last_payment_data = Column(DateTime, **mod(0b0100))
    subscription_until = Column(DateTime, **mod(0b0100))
    roles = relationship("Role", backref=backref("account"))


# ==================================================================================================


class RoleEnum(EnumClass):
    STUDENT = 0
    TEACHER = 1
    PARENT = 2
    ADMINISTRATION = 3


class Role(Base):
    __tablename__ = "role"
    id = Column(Integer, **mod(0b1011))
    is_main_role = Column(Boolean, default=False, **mod(0b0000))
    role_type = Column(Enum(RoleEnum), **mod(0b0000))
    account_id = Column(Integer, ForeignKey("account.id"), **mod(0b0000))
    student_id = Column(Integer, ForeignKey("student.id"), default=None, **mod(0b0100))
    student = relationship("Student")
    teacher_id = Column(Integer, ForeignKey("teacher.id"), default=None, **mod(0b0100))
    teacher = relationship("Teacher")
    administration_id = Column(
        Integer, ForeignKey("administration.id"), default=None, **mod(0b0100)
    )
    administration = relationship("Administration")
    parent_id = Column(Integer, ForeignKey("parent.id"), default=None, **mod(0b0100))
    parent = relationship("Parent")


# ==================================================================================================


class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, **mod(0b1011))
    school_id = Column(Integer, ForeignKey("school.id"), **mod(0b0000))
    subclass_id = Column(Integer, ForeignKey("subclass.id"), **mod(0b0000))
    parent_id = Column(Integer, ForeignKey("parent.id"), **mod(0b0100))


# ==================================================================================================


class Teacher(Base):
    __tablename__ = "teacher"
    id = Column(Integer, **mod(0b1011))
    name = Column(String(length=200), **mod(0b0000))
    school_id = Column(Integer, ForeignKey("school.id"), **mod(0b0000))
    lessons = relationship("Lesson", backref=backref("teacher"))
    tags = relationship(
        "Tag",
        secondary=teacher_tag_association,
        backref=backref("teachers", lazy="dynamic"),
    )


# ==================================================================================================


class Parent(Base):
    __tablename__ = "parent"
    id = Column(Integer, **mod(0b1011))
    children = relationship("Student", backref=backref("parents"))


# ==================================================================================================


class Administration(Base):
    __tablename__ = "administration"
    id = Column(Integer, **mod(0b1011))
    school_id = Column(Integer, ForeignKey("school.id"), **mod(0b0000))


# ==================================================================================================


class Subclass(Base):
    __tablename__ = "subclass"
    id = Column(Integer, **mod(0b1011))
    educational_level = Column(SmallInteger, **mod(0b0000))
    identificator = Column(String(length=50), **mod(0b0000))
    additional_identificator = Column(String(length=50), **mod(0b0100))
    school_id = Column(Integer, ForeignKey("school.id"), **mod(0b0000))
    student_id = relationship("Student", backref=backref("subclass"))


# ==================================================================================================


class Corpus(Base):
    __tablename__ = "corpus"
    id = Column(Integer, **mod(0b1011))
    address = Column(String(length=250), **mod(0b0000))
    canteen_text = Column(String(length=500), **mod(0b0100))
    name = Column(String(length=100), **mod(0b0000))
    school_id = Column(Integer, ForeignKey("school.id"), **mod(0b0000))
    cabinets = relationship("Cabinet", backref=backref("corpus"))
    lessons = relationship("Lesson", backref=backref("corpus"))


# ==================================================================================================


class Cabinet(Base):
    __tablename__ = "cabinet"
    id = Column(Integer, **mod(0b1011))
    floor = Column(SmallInteger, **mod(0b0000))
    name = Column(String(length=100), **mod(0b0000))
    corpus_id = Column(Integer, ForeignKey("corpus.id"), **mod(0b0000))
    lessons = relationship("Lesson", backref=backref("cabinet"))
    school_id = Column(Integer, ForeignKey("school.id"), **mod(0b0100))
    tags = relationship(
        "Tag",
        secondary=cabinet_tag_association,
        backref=backref("cabinets", lazy="dynamic"),
    )


# ==================================================================================================


class School(Base):
    __tablename__ = "school"
    id = Column(Integer, **mod(0b1011))
    name = Column(String(length=200), **mod(0b0001))
    students = relationship("Student", backref=backref("school"))
    teachers = relationship("Teacher", backref=backref("school"))
    administrations = relationship("Administration", backref=backref("school"))
    subclasses = relationship("Subclass", backref=backref("school"))
    corpuses = relationship("Corpus", backref=backref("school"))
    lessons = relationship("Lesson", backref=backref("school"))
    lesson_numbers = relationship("Lesson_number", backref=backref("school"))
    cabinets = relationship("Cabinet", backref=backref("school"))


# ==================================================================================================


class Lesson_number(Base):
    __tablename__ = "lesson_number"
    id = Column(Integer, **mod(0b1011))
    number = Column(SmallInteger, **mod(0b0000))
    time_start = Column(String(length=5), **mod(0b0000))
    time_end = Column(String(length=5), **mod(0b0000))
    school_id = Column(Integer, ForeignKey("school.id"), **mod(0b0000))
    lessons = relationship("Lesson", backref=backref("lesson_number"))


# ==================================================================================================


class Lesson(Base):
    __tablename__ = "lesson"
    id = Column(Integer, **mod(0b1011))
    day_of_week = Column(SmallInteger, **mod(0b0000))
    subject = Column(String(length=200), **mod(0b0000))
    lesson_number_id = Column(Integer, ForeignKey("lesson_number.id"), **mod(0b0000))
    teacher_id = Column(Integer, ForeignKey("teacher.id"), **mod(0b0000))
    subclasses = relationship(
        "Subclass",
        secondary=lesson_subclass_association,
        backref=backref("lessons", lazy="dynamic"),
    )
    corpus_id = Column(Integer, ForeignKey("corpus.id"), **mod(0b0000))
    cabinet_id = Column(Integer, ForeignKey("cabinet.id"), **mod(0b0000))
    school_id = Column(Integer, ForeignKey("school.id"), **mod(0b0000))


# ==================================================================================================

role_announcement_association = Table(
    "role_announcement_association",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("role.id")),
    Column("announcement_id", Integer, ForeignKey("announcement.id")),
)

# ==================================================================================================


class Announcement(Base):
    __tablename__ = "announcement"
    id = Column(Integer, **mod(0b1011))
    link = Column(String(length=500), **mod(0b0000))
    title = Column(String(length=150), **mod(0b0000))
    roles = relationship(
        "Role",
        secondary=role_announcement_association,
        backref=backref("announcements", lazy="dynamic"),
    )


# ==================================================================================================


class Service(Base):
    __tablename__ = "service"
    id = Column(Integer, **mod(0b1011))
    name = Column(String(length=50), **mod(0b0001))
    password = Column(String(length=60), **mod(0b0000))
    access_level = Column(Integer, **mod(0b0000))


# ==================================================================================================


class HarvestUser(Base):
    __tablename__ = "harvest_user"
    uuid = Column(String(length=36), **mod(0b1001))
    name = Column(String(length=30), **mod(0b0000))
    surname = Column(String(length=50), **mod(0b0000))
    email = Column(String(length=2000), **mod(0b0001))
    password = Column(String(length=60), **mod(0b0000))
    activation_link = Column(String(length=300), **mod(0b0100))
    access_token = Column(String(length=300), **mod(0b0000))
    refresh_token = Column(String(length=300), **mod(0b0000))
    logged_in = Column(Boolean, **mod(0b0000))
    activated = Column(Boolean, **mod(0b0000))
    image = Column(String(length=300), **mod(0b0000))


# ==================================================================================================
