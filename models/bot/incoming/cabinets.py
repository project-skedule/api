from pydantic import BaseModel, Field


class Cabinets(BaseModel):
    school_id: int = Field(ge=1, le=2147483647)
