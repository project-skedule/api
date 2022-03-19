from typing import List

from models.bot.telegram.outgoing.child import Child
from pydantic import BaseModel, Field


class Parent(BaseModel):
    parent_id: int = Field(ge=0, le=2147483647)
    children: List[Child]
