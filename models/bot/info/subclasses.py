from typing import List

from pydantic import BaseModel

from models.bot.item import Subclass


class Subclasses(BaseModel):
    data: List[Subclass]
