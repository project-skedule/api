from config import BaseModel
from pydantic import Field


class TeacherByDistance(BaseModel):
    name: str = Field(max_length=200, min_length=1)
    school_id: int = Field(ge=1, le=2147483647)
