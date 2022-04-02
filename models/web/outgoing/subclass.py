from config import BaseModel
from pydantic import Field


class Subclass(BaseModel):
    id: int = Field(ge=1, le=2147483647)
