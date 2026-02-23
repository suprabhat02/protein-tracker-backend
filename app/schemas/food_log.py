from datetime import date, datetime
from pydantic import BaseModel, Field


class FoodLogCreateRequest(BaseModel):
    food_name: str = Field(min_length=1, max_length=120)
    protein_grams: float = Field(gt=0, le=500)
    quantity: float = Field(gt=0, le=10000)
    unit: str = Field(min_length=1, max_length=24)
    log_date: date
    notes: str | None = Field(default=None, max_length=500)


class FoodLogUpdateRequest(BaseModel):
    food_name: str = Field(min_length=1, max_length=120)
    protein_grams: float = Field(gt=0, le=500)
    quantity: float = Field(gt=0, le=10000)
    unit: str = Field(min_length=1, max_length=24)
    log_date: date
    notes: str | None = Field(default=None, max_length=500)


class FoodLogResponse(BaseModel):
    id: str
    food_name: str
    protein_grams: float
    quantity: float
    unit: str
    log_date: date
    notes: str | None = None
    created_at: datetime
    updated_at: datetime
