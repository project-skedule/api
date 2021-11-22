from pydantic import BaseModel, Field, validator
from typing import List, Optional, Union
from typing_extensions import Annotated


# class Announcement(BaseModel):
#     text: str = Field(max_length=1000)
#     school_id: int = Field(ge=1, le=2147483647)
#     teacher_ids: Optional[List[Annotated[int, Field(ge=1, le=2147483647)]]] = None
#     parallels: Optional[List[Annotated[int, Field(ge=0, le=12)]]] = None
#     letters: Optional[List[Annotated[str, Field(max_length=50)]]] = None
#     groups: Optional[List[Annotated[str, Field(max_length=50)]]] = None
#     corpus_ids: Optional[List[Annotated[int, Field(ge=1, le=2147483647)]]] = None


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
