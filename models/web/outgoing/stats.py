from typing import List
from pydantic import BaseModel, Field


class Stat(BaseModel):
    number: int
    occurrences: int


class Statistics(BaseModel):
    data: List[Stat]
