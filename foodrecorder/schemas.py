#schemas.py
from pydantic import BaseModel

# リクエストボディのモデル
class FoodRecordRequest(BaseModel):
    date: str
    recipe_name: str
    servings: float

# レスポンスボディのモデル
class NutrientSummary(BaseModel):
    date: str
    total_energy: float
    total_protein: float
    total_fat: float
    total_carbohydrate: float