from typing import List

from pydantic import BaseModel, Field, validator

from models.bot.item import School


class Schools(BaseModel):
    data: List[School]
