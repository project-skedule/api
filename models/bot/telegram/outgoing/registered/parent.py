from datetime import datetime
from typing import Optional

from models.bot.telegram.outgoing.parent_role import ParentRole
from config import BaseModel
from pydantic import Field


class Parent(BaseModel):
    premium_status: int = Field(ge=0, le=255)
    last_payment_data: Optional[datetime]
    subscription_until: Optional[datetime]
    main_role: ParentRole
