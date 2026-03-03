from datetime import datetime
from pydantic import BaseModel, EmailStr
from bson import ObjectId

from app.schemas.user import LifestyleGoal


class UserModel(BaseModel):
    id: str
    public_id: str
    email: EmailStr
    full_name: str
    daily_protein_target: int
    weight_kg: float | None = None
    height_cm: float | None = None
    lifestyle: LifestyleGoal | None = None
    created_at: datetime
    updated_at: datetime


class User(BaseModel):
    id: ObjectId
    fullName: str
    email: EmailStr
