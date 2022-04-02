from config import BaseModel
from pydantic import Field


class Teachers(BaseModel):
    school_id: int = Field(ge=1, le=2147483647)
