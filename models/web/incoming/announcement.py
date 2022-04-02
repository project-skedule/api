from typing import List, Optional, Union

from config import BaseModel
from pydantic import Field


class Subclass(BaseModel):
    educational_level: Optional[int] = Field(ge=1, le=12)
    identificator: Optional[str] = Field(max_length=50)
    additional_identificator: Optional[str] = Field(max_length=50)


class Teacher(BaseModel):
    name: str = Field(max_length=200, min_length=1)


class Announcement(BaseModel):
    text: str = Field(max_length=2500, min_length=20)
    school_id: int = Field(ge=1, le=2147483647)
    filters: List[Union[Teacher, Subclass]]
    resend_to_parents: bool
    sent_only_to_parents: bool
