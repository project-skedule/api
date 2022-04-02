from datetime import datetime
from typing import List, Optional

from models.bot.telegram.outgoing.role import Role
from config import BaseModel
from pydantic import Field


class Account(BaseModel):
    premium_status: int = Field(ge=0, le=255)
    last_payment_data: Optional[datetime]
    subscription_until: Optional[datetime]
    roles: List[Role]
