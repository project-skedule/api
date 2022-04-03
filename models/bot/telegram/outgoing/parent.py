from typing import List

from models.bot.telegram.outgoing.child import Child
from config import BaseModel
from pydantic import Field


class Parent(BaseModel):
    id: int = Field(ge=0, le=2147483647, alias="parent_id")
    children: List[Child]
