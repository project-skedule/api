from typing import List

from models.bot.item import Teacher
from config import BaseModel


class Teachers(BaseModel):
    data: List[Teacher]
