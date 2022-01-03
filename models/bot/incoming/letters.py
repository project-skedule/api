from pydantic import BaseModel, Field


class Letters(BaseModel):
    school_id: int = Field(ge=1, le=2147483647)
    educational_level: int = Field(ge=0, le=12)
