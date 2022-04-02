from typing import List
from config import BaseModel
from pydantic import Field


class HistoryEntity(BaseModel):
    link: str
    title: str


class HistoryAnnouncement(BaseModel):
    data: List[HistoryEntity]
