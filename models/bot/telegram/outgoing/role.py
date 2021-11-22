from typing import Union

from pydantic import BaseModel, Field

from models.bot.telegram.outgoing.administration_role import (
    AdministrationRole,
)
from models.bot.telegram.outgoing.parent_role import ParentRole
from models.bot.telegram.outgoing.student_role import StudentRole
from models.bot.telegram.outgoing.teacher_role import TeacherRole

Role = Union[StudentRole, TeacherRole, AdministrationRole, ParentRole]
