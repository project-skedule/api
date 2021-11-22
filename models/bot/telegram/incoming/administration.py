from pydantic import BaseModel, Field


class Administration(BaseModel):
    telegram_id: int = Field(ge=1, le=9223372036854775807)
    school_id: int = Field(ge=1, le=2147483647)
