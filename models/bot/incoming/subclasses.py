from pydantic import BaseModel, Field, validator


class Subclasses(BaseModel):
    school_id: int = Field(ge=1, le=2147483647)
