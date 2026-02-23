from pydantic import BaseModel
from app.schemas.food_log import FoodLogResponse


class DailyProgress(BaseModel):
    target_protein_grams: int
    consumed_protein_grams: float
    remaining_protein_grams: float


class DashboardResponse(BaseModel):
    progress: DailyProgress
    logs: list[FoodLogResponse]
