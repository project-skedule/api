from pydantic import BaseModel, Field


class Corpuses(BaseModel):
    school_id: int = Field(ge=1, le=2147483647)
