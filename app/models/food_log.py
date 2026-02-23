from datetime import datetime, date
from pydantic import BaseModel


class FoodLogModel(BaseModel):
    id: str
    user_id: str
    food_name: str
    protein_grams: float
    quantity: float
    unit: str
    log_date: date
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
