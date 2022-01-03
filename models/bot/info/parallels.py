from typing import List

from pydantic import BaseModel


class Parallels(BaseModel):
    data: List[int]
