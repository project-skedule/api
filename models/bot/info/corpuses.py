from typing import List

from pydantic import BaseModel, Field, validator

from models.bot.item import Corpus


class Corpuses(BaseModel):
    data: List[Corpus]
