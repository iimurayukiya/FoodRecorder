from datetime import date
from typing import List
from fastapi import HTTPException
from database import Session
import models

#Read
# 全てのユーザーを取得
def get_all_users(db: Session):
    return db.query(models.User).all()

# ユーザーのレスポンスモデルのリストを作成
def create_user_responses(users: List[models.User]):
    user_responses = []
    for user in users:
        user_response = models.UserResponse(id=user.id, username=user.username)
        user_responses.append(user_response)
    return user_responses

#Create
def check_existing_user(username: str, db: Session):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")

# ユーザーを作成して保存
def create_and_save_user(user: models.UserCreate, db: Session):
    db_user = models.User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# ユーザーのレスポンスモデルを作成
def create_user_response(user: models.User):
    return models.UserResponse(id=user.id, username=user.username)

#Update
def get_user_by_username(username: str, db: Session):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

def update_user_in_db(db_user: models.User, username: str, db: Session):
    db_user.username = username
    db.commit()
    db.refresh(db_user)
    return db_user

#Delete
def get_user_by_username(username: str, db: Session) -> models.User:
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

def delete_user_from_db(db: Session, user: models.User):
    db.delete(user)
    db.commit()

#foodrecord_get
def get_user_by_username(username: str, db: Session) -> models.User:
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def get_food_records_from_db(db: Session, user: models.User, date: date) -> List[models.FoodRecord]:
    db_food_records = db.query(models.FoodRecord).filter(
        models.FoodRecord.user_id == user.id,
        models.FoodRecord.date == date
    ).all()
    return db_food_records


def create_food_record_responses(db_food_records: List[models.FoodRecord]) -> List[models.FoodRecordResponse]:
    food_records = []
    for db_food_record in db_food_records:
        food_record = models.FoodRecordResponse(
            id=db_food_record.id,
            date=db_food_record.date,
            recipe_name=db_food_record.recipe_name,
            servings=db_food_record.servings,
            energy=db_food_record.energy,
            protein=db_food_record.protein,
            fat=db_food_record.fat,
            carbohydrate=db_food_record.carbohydrate
        )
        food_records.append(food_record)
    return food_records

#foodrecord_create
def get_user_by_username(username: str, db: Session) -> models.User:
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def create_food_record_in_db(db: Session, user: models.User, food_record: models.FoodRecordCreate, today: date) -> models.FoodRecord:
    db_food_record = models.FoodRecord(
        user_id=user.id,
        date=today,
        recipe_name=food_record.recipe_name,
        servings=food_record.servings,
        energy=food_record.energy,
        protein=food_record.protein,
        fat=food_record.fat,
        carbohydrate=food_record.carbohydrate
    )
    db.add(db_food_record)
    db.commit()
    db.refresh(db_food_record)
    return db_food_record


def create_food_record_response(db_food_record: models.FoodRecord) -> models.FoodRecordResponse:
    return models.FoodRecordResponse(
        id=db_food_record.id,
        date=db_food_record.date,
        recipe_name=db_food_record.recipe_name,
        servings=db_food_record.servings,
        energy=db_food_record.energy,
        protein=db_food_record.protein,
        fat=db_food_record.fat,
        carbohydrate=db_food_record.carbohydrate
    )
