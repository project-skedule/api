from typing import List

from pydantic import BaseModel, Field, validator

from models.bot.item import Subclass


class Subclasses(BaseModel):
    data: List[Subclass]
