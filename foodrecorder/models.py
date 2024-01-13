#models.py
from sqlalchemy import Column, ForeignKey, Integer, Float, String, Date
from datetime import date
from pydantic import BaseModel
from typing import Optional

from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)


class UserCreate(BaseModel):
    username: str


class UserResponse(BaseModel):
    id: int
    username: str


class FoodRecord(Base):
    __tablename__ = "food_records"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(Date)
    recipe_name = Column(String)
    servings = Column(Float)
    energy = Column(Float)
    protein = Column(Float)
    fat = Column(Float)
    carbohydrate = Column(Float)


class FoodRecordCreate(BaseModel):
    recipe_name: str
    servings: float
    energy: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbohydrate: Optional[float] = None


class FoodRecordResponse(BaseModel):
    id: int
    date: date
    recipe_name: str
    servings: float
    energy: Optional[float] = None
    protein: Optional[float] = None
    fat: Optional[float] = None
    carbohydrate: Optional[float] = None


class NutrientSummary(BaseModel):
    total_energy: float
    total_protein: float
    total_fat: float
    total_carbohydrate: float