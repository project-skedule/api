from config import BaseModel
from pydantic import Field


class SimpleAnnouncement(BaseModel):
    title: str = Field(max_length=128)
    text: str = Field(max_length=2500, min_length=5)
