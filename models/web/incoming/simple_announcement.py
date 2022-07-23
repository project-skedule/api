from config import BaseModel
from pydantic import Field


class SimpleTelegraphAnnouncement(BaseModel):
    title: str = Field(max_length=128)
    text: str = Field(max_length=2500, min_length=5)
    silent: bool = Field(False)


class SimpleTextAnnouncement(BaseModel):
    text: str = Field(max_length=2500, min_length=5)
    silent: bool = Field(False)
