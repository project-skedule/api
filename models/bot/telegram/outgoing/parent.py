from typing import List

from pydantic import BaseModel

from models.bot.telegram.outgoing.child import Child


class Parent(BaseModel):
    children: List[Child]
