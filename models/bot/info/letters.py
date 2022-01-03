from typing import List

from pydantic import BaseModel


class Letters(BaseModel):
    data: List[str]
