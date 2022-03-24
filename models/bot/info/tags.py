from typing import List
from pydantic import BaseModel, Field


class Tags(BaseModel):
    data: List[str]
