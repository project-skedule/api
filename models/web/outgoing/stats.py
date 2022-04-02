from typing import Dict, List

from config import BaseModel
from pydantic import Field


class Statistics(BaseModel):
    data: Dict[int, int]
