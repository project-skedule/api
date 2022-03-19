from typing import List

from models.bot.item import Corpus
from pydantic import BaseModel


class Corpuses(BaseModel):
    data: List[Corpus]
