from typing import List

from pydantic import BaseModel, Field, validator


class Parallels(BaseModel):
    data: List[int]
