from typing import List
from pydantic import BaseModel, Field


class HistoryEntity(BaseModel):
    link: str


class HistoryAnnouncement(BaseModel):
    data: List[HistoryEntity]
