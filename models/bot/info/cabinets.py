from typing import List

from pydantic import BaseModel, Field, validator

from models.bot.item import Cabinet


class Cabinets(BaseModel):
    data: List[Cabinet]
