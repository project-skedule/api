from typing import List

from models.bot.item import Corpus
from config import BaseModel


class Corpuses(BaseModel):
    data: List[Corpus]
