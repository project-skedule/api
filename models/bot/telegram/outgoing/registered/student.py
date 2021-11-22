from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from models.bot.telegram.outgoing.student_role import StudentRole


class Student(BaseModel):
    premium_status: int = Field(ge=0, le=255)
    last_payment_data: Optional[datetime]
    subscription_until: Optional[datetime]
    main_role: StudentRole
