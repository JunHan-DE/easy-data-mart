from pydantic import BaseModel
from typing import Optional


class user_data(BaseModel):
    id: str
    name: str
    gender: str
    # event_name: Optional[str] = None  # optional
