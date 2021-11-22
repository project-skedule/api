from typing import List

from pydantic import BaseModel, Field, validator

from models.bot.item import Group


class Groups(BaseModel):
    data: List[Group]
