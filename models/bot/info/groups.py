from typing import List

from config import BaseModel


class Groups(BaseModel):
    data: List[str]
