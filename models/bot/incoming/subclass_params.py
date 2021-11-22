from pydantic import BaseModel, Field


class SubclassParams(BaseModel):
    educational_level: int = Field(ge=0, le=12)
    identificator: str = Field(max_length=50)
    additional_identificator: str = Field(max_length=50)
