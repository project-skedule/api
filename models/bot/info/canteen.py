from config import BaseModel
from pydantic import Field


class Canteen(BaseModel):
    data: str = Field(
        "Ваша школа не предоставила расписание столовой для этого корпуса"
    )
