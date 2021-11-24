from pydantic import BaseModel
from typing import List
from models.web.outgoing.subclass import Subclass


class AnnouncementsPreview(BaseModel):
    teachers: List[str]
    subclasses: List[Subclass]
