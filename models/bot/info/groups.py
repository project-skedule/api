from typing import List

from pydantic import BaseModel


class Groups(BaseModel):
    data: List[str]
