from pydantic import BaseModel, Field


class Teacher(BaseModel):
    id: int = Field(ge=1, le=2147483647)
