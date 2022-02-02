from pydantic import BaseModel, Field
from typing import List


class Subclass(BaseModel):
    educational_level: int = Field(ge=1, le=12)
    identificator: str = Field(max_length=50)
    additional_identificator: str = Field(max_length=50)


class AnnouncementsPreview(BaseModel):
    teachers: List[str]
    subclasses: List[Subclass]
    sent_to_parents: bool
