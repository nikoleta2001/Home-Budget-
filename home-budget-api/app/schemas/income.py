from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class IncomeBase(BaseModel):
    description: str
    amount: float

    model_config = {
        "json_schema_extra": {
            "example": {"description": "salary", "amount": 1500.00}
        }
    }

class IncomeCreate(IncomeBase):
    pass

class IncomeOut(IncomeBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
