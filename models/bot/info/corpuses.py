from typing import List

from pydantic import BaseModel

from models.bot.item import Corpus


class Corpuses(BaseModel):
    data: List[Corpus]
