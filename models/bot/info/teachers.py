from typing import List

from pydantic import BaseModel

from models.bot.item import Teacher


class Teachers(BaseModel):
    data: List[Teacher]
