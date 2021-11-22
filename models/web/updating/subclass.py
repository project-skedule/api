from typing import Optional

from pydantic import BaseModel, Field


class Subclass(BaseModel):
    educational_level: Optional[int] = Field(None, ge=0, le=12)
    identificator: Optional[str] = Field(None, max_length=50)
    additional_identificator: Optional[str] = Field(None, max_length=50)
    subclass_id: int = Field(ge=1, le=2147483647)
