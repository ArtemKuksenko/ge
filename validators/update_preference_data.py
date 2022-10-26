from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UpdatePreferenceData(BaseModel):
    recipient_id: int
    personal_package: Optional[bool]
    marketing_package: Optional[bool]
    timestamp: datetime
