from typing import List

from models.bot.item import Cabinet
from pydantic import BaseModel


class Cabinets(BaseModel):
    data: List[Cabinet]
