from typing import List

from pydantic import BaseModel, Field, validator

from models.bot.item import Teacher


class Teachers(BaseModel):
    data: List[Teacher]
