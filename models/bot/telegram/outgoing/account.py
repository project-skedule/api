from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from models.bot.telegram.outgoing.role import Role


class Account(BaseModel):
    premium_status: int = Field(ge=0, le=255)
    last_payment_data: Optional[datetime]
    subscription_until: Optional[datetime]
    roles: List[Role]
