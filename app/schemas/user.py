from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class LifestyleGoal(str, Enum):
    SEDENTARY = "sedentary"
    LIGHTLY_ACTIVE = "lightly_active"
    REGULAR_EXERCISE = "regular_exercise"
    RECOMPOSITION = "recomposition"
    MUSCLE_BUILDING = "muscle_building"
    AGGRESSIVE_BODYBUILDING = "aggressive_bodybuilding"


# Protein multipliers (g/kg/day) - midpoint of each range
LIFESTYLE_PROTEIN_MULTIPLIER: dict["LifestyleGoal", float] = {
    LifestyleGoal.SEDENTARY: 0.8,
    LifestyleGoal.LIGHTLY_ACTIVE: 1.1,
    LifestyleGoal.REGULAR_EXERCISE: 1.4,
    LifestyleGoal.RECOMPOSITION: 1.6,
    LifestyleGoal.MUSCLE_BUILDING: 1.9,
    LifestyleGoal.AGGRESSIVE_BODYBUILDING: 2.3,
}


def calculate_protein_target(weight_kg: float, lifestyle: LifestyleGoal) -> int:
    multiplier = LIFESTYLE_PROTEIN_MULTIPLIER[lifestyle]
    return round(weight_kg * multiplier)


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    daily_protein_target: int
    weight_kg: float | None = None
    height_cm: float | None = None
    lifestyle: LifestyleGoal | None = None
    created_at: datetime
    updated_at: datetime


class UpdateProfileRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    daily_protein_target: int = Field(ge=30, le=450)
    weight_kg: float | None = Field(default=None, gt=20, le=300)
    height_cm: float | None = Field(default=None, gt=50, le=300)
    lifestyle: LifestyleGoal | None = None


class CreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    weight_kg: float = Field(gt=20, le=300, description="Weight in kilograms")
    height_cm: float = Field(gt=50, le=300, description="Height in centimeters")
    lifestyle: LifestyleGoal
