from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .category import CategoryOut

class ExpenseBase(BaseModel):
    description: str
    amount: float
    category_id: Optional[int] = None

    model_config = {
        "json_schema_extra": {
            "example": {"description": "pizza", "amount": 50.0, "category_id": 1}
        }
    }

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseOut(ExpenseBase):
    id: int
    created_at: datetime
    category: Optional[CategoryOut] = None
    model_config = ConfigDict(from_attributes=True)
