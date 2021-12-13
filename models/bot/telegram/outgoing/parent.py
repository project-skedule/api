from typing import List

from pydantic import BaseModel, Field


from models.bot.telegram.outgoing.child import Child


class Parent(BaseModel):
    parent_id: int = Field(ge=0, le=2147483647)
    children: List[Child]
