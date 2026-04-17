from pydantic import BaseModel
from typing import Optional

class RiskRequest(BaseModel):
    age: int
    sex: str
    sys_bp: Optional[int] = None
    dia_bp: Optional[int] = None
    diabetes: str
