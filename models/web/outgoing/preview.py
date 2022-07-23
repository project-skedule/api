from typing import List

from config import BaseModel
from pydantic import Field


class Subclass(BaseModel):
    educational_level: int = Field(ge=1, le=12)
    identificator: str = Field(max_length=50)
    additional_identificator: str = Field(max_length=50)


class Teacher(BaseModel):
    name: str


class AnnouncementsPreview(BaseModel):
    teachers: List[Teacher]
    subclasses: List[Subclass]
    sent_to_parents: bool = Field(False)
    silent: bool = Field(False)
    sent_only_to_parents: bool = Field(False)
