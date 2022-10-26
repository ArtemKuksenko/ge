from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from validators.allow_package_types import allow_package_types_list


class SendPackageData(BaseModel):
    sender_id: int
    recipient_id: int
    package_id: int
    package_type: Literal[tuple(allow_package_types_list)]
    timestamp: datetime
