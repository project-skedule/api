from pydantic import BaseModel, Field
from typing import List, Optional, Union
from typing_extensions import Annotated


class Subclass(BaseModel):
    educational_level: Optional[Annotated[int, Field(ge=1, le=12)]]
    identificator: Optional[Annotated[str, Field(max_length=50)]]
    additional_identificator: Optional[Annotated[str, Field(max_length=50)]]


class Teacher(BaseModel):
    name: Optional[Annotated[str, Field(max_length=200, min_length=1)]]


class Announcement(BaseModel):
    text: str = Field(max_length=4000)
    school_id: int = Field(ge=1, le=2147483647)
    filters: Optional[List[Union[Subclass, Teacher]]]
