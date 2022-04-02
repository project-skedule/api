from config import BaseModel
from pydantic import Field


class Groups(BaseModel):
    school_id: int = Field(ge=1, le=2147483647)
    educational_level: int = Field(ge=0, le=12)
    identificator: str = Field(max_length=50)
