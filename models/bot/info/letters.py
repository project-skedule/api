from typing import List

from pydantic import BaseModel, Field, validator

from models.bot.item import Letter


class Letters(BaseModel):
    data: List[str]
