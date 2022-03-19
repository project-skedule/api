from typing import List

from models.bot.item import Subclass
from pydantic import BaseModel


class Subclasses(BaseModel):
    data: List[Subclass]
