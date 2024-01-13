#main.py
import threading
from matplotlib import pyplot as plt
import matplotlib.font_manager as fm
from sqlalchemy import func
import streamlit as st
from fastapi import APIRouter, Depends, FastAPI
from datetime import date
from typing import List
import crud, models
from database import Base, Session, session, engine, SessionLocal


app = FastAPI()

# データベースセッションの依存関係
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ユーザー関連のルーター
user_router = APIRouter()

@user_router.get("/", response_model=List[models.UserResponse])
def get_users(db: Session = Depends(get_db)):
    db_users = crud.get_all_users(db)
    return crud.create_user_responses(db_users)

@user_router.post("/", response_model=models.UserResponse)
def create_user(user: models.UserCreate, db: Session = Depends(get_db)):
    crud.check_existing_user(user.username, db)
    db_user = crud.create_and_save_user(user, db)
    return crud.create_user_response(db_user)

@user_router.put("/{username}/", response_model=models.UserResponse)
def update_user(username: str, user: models.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(username, db)
    db_user = crud.update_user_in_db(db_user, user.username, db)
    return models.UserResponse(id=db_user.id, username=db_user.username)

from fastapi import HTTPException

@user_router.delete("/{username}/", response_model=models.UserResponse)
def delete_user(username: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(username, db)
    crud.delete_user_from_db(db, db_user)
    return models.UserResponse(id=db_user.id, username=db_user.username)

app.include_router(user_router, tags=["Users"], prefix="/users")

# 食事関連のルーター
food_router = APIRouter()

@food_router.get("/{username}/food_records/", response_model=List[models.FoodRecordResponse])
def get_food_records(username: str, date: date, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(username, db)
    db_food_records = crud.get_food_records_from_db(db, db_user, date)
    food_records = crud.create_food_record_responses(db_food_records)
    return food_records

@food_router.post("/{username}/food_records/", response_model=models.FoodRecordResponse)
def create_food_record(username: str, food_record: models.FoodRecordCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(username, db)
    today = date.today()
    db_food_record = crud.create_food_record_in_db(db, db_user, food_record, today)
    return crud.create_food_record_response(db_food_record)

app.include_router(food_router, tags=["Food Records"], prefix="/users")






# データベースの初期化
def init_db():
    Base.metadata.create_all(bind=engine)

# FastAPIイベントハンドラでデータベースの初期化を実行
@app.on_event("startup")
def startup_event():
    init_db()


def get_nutrient_summary(date):
    nutrient_summary = session.query(
        func.sum(models.FoodRecord.energy).label("total_energy"),
        func.sum(models.FoodRecord.protein).label("total_protein"),
        func.sum(models.FoodRecord.fat).label("total_fat"),
        func.sum(models.FoodRecord.carbohydrate).label("total_carbohydrate")
    ).filter(models.FoodRecord.date == date).first()

    nutrient_summary = models.NutrientSummary(
        total_energy=nutrient_summary.total_energy or 0,
        total_protein=nutrient_summary.total_protein or 0,
        total_fat=nutrient_summary.total_fat or 0,
        total_carbohydrate=nutrient_summary.total_carbohydrate or 0
    )
    return nutrient_summary


# 円グラフの表示
def plot_pfc_ratio(nutrient_summary):
    labels = ["Protein", "Fat", "Carbohydrate"]
    sizes = [nutrient_summary.total_protein * 4, nutrient_summary.total_fat * 9, nutrient_summary.total_carbohydrate * 4]
    explode = (0.03, 0.03, 0.03)  # 各要素を少し引き出すために指定

    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")  # アスペクト比を保持して円形に表示

    st.pyplot(fig)




# 本日の総カロリー量とPFC比のグラフを表示する関数
def display_summary(user, date):
    # 本日の総カロリー量を取得
    nutrient_summary = get_nutrient_summary(date)

    # 食事記録を取得
    food_records = get_daily_food_records(user, date)

    # 合計の栄養素量を計算
    total_energy = sum(record.energy for record in food_records)
    total_protein = sum(record.protein for record in food_records)
    total_fat = sum(record.fat for record in food_records)
    total_carbohydrate = sum(record.carbohydrate for record in food_records)

    # PFC比の円グラフを表示
    nutrient_summary = models.NutrientSummary(
        total_energy=total_energy,
        total_protein=total_protein,
        total_fat=total_fat,
        total_carbohydrate=total_carbohydrate
    )
    st.write("合計の栄養素量:")
    st.write("総エネルギー:", round(total_energy, 1))
    st.write("総タンパク質:", round(total_protein, 1))
    st.write("総脂質:", round(total_fat, 1))
    st.write("総炭水化物:", round(total_carbohydrate, 1))
    st.write("-----")
    st.write(f"{date}のPFC比率:")
    plot_pfc_ratio(nutrient_summary)


# スレッドごとにデータベースセッションを作成する
def create_session():
    session = Session()  # データベースセッションの作成
    return session

# データベースセッションをスレッドごとに保存する辞書
sessions = threading.local()

# データベースセッションを取得する
def get_session():
    if not hasattr(sessions, "session"):
        sessions.session = create_session()
    return sessions.session

# 本日の食事記録を取得する関数
def get_daily_food_records(user, date):
    date_str = date.strftime("%Y-%m-%d")  # dateオブジェクトを文字列に変換
    food_records = (
        get_session()
        .query(models.FoodRecord)
        .join(models.User)  # Userモデルとの関連を考慮して結合する
        .filter(models.User.username == user, models.FoodRecord.date == date_str)

        .all()
    )
    return food_records

# フォントファミリを指定（文字化けしたため）
font_family = 'Yu Gothic'

# フォントパスを取得
font_path = fm.findfont(fm.FontProperties(family=font_family))

# フォント設定を変更
plt.rcParams['font.family'] = font_family
plt.rcParams['font.sans-serif'] = font_family
plt.rcParams['pdf.fonttype'] = 42  # PDF出力時にフォントを埋め込むための設定






# 食事記録と合計の栄養素量、PFC比を表示する関数
def display_daily_summary(user, date):
    # 選択された日付を表示
    st.write(f"{date}の食事記録:")

    # 食事記録を取得
    food_records = get_daily_food_records(user, date)

    if len(food_records) == 0:
        st.error("記録がありません")
        return

    # 合計の栄養素量を計算
    total_energy = sum(record.energy for record in food_records)
    total_protein = sum(record.protein for record in food_records)
    total_fat = sum(record.fat for record in food_records)
    total_carbohydrate = sum(record.carbohydrate for record in food_records)

    st.write("合計の栄養素量:")
    st.write("総エネルギー:", round(total_energy, 1))
    st.write("総タンパク質:", round(total_protein, 1))
    st.write("総脂質:", round(total_fat, 1))
    st.write("総炭水化物:", round(total_carbohydrate, 1))
    st.write("-----")

    # 本日のPFC比率を計算
    pfc_ratio = calculate_pfc_ratio(total_protein, total_fat, total_carbohydrate)

    # 理想のPFC比率を定義
    ideal_pfc_ratio = {'タンパク質': 0.15, '脂質': 0.25, '炭水化物': 0.6}

    # グラフのデータとラベルを準備
    categories = list(pfc_ratio.keys())
    values = list(pfc_ratio.values())
    ideal_values = list(ideal_pfc_ratio.values())

    # グラフの描画
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

    # ラベルの順序を調整
    reordered_labels = ['タンパク質', '脂質', '炭水化物']

    # 本日のPFC比の円グラフを描画
    _, _, text = ax1.pie(
        values, labels=reordered_labels, autopct='%1.1f%%', startangle=90, labeldistance=1.1,
        textprops={'fontsize': 15}  # ラベルの文字の大きさを設定
    )
    ax1.set_title(f'{date}のPFC比率', fontsize=20)  # タイトルの文字の大きさを設定

    # 理想のPFC比の円グラフを描画
    _, _, text = ax2.pie(
        ideal_values, labels=reordered_labels, autopct='%1.1f%%', startangle=90, labeldistance=1.1,
        textprops={'fontsize': 15}  # ラベルの文字の大きさを設定
    )
    ax2.set_title('理想のPFC比率', fontsize=20)  # タイトルの文字の大きさを設定

    # グラフの表示
    st.pyplot(fig)

    # 食事記録の一覧表を表示
    for record in food_records:
        st.write("食べたもの:", record.recipe_name)
        st.write("食べた量:", record.servings)
        st.write("エネルギー:", round(record.energy, 1))
        st.write("タンパク質:", round(record.protein, 1))
        st.write("脂質:", round(record.fat, 1))
        st.write("炭水化物:", round(record.carbohydrate, 1))
        st.write("-----")


# PFC比率を計算する関数
def calculate_pfc_ratio(protein, fat, carbohydrate):
    protein_energy = protein * 4
    fat_energy = fat * 9
    carbohydrate_energy = carbohydrate * 4
    total = protein_energy + fat_energy + carbohydrate_energy
    pfc_ratio = {        
        'タンパク質': protein_energy / total,
        '脂質': fat_energy / total,
        '炭水化物': carbohydrate_energy / total
    }
    return pfc_ratio

def display_ideal_pfc_ratio():
    # 理想のPFC比を計算するロジックを追加
    total_calories = 2000  # 1日の総カロリー摂取量（例として2000カロリーを設定）

    ideal_protein_percentage = 15
    ideal_fat_percentage = 25
    ideal_carbohydrate_percentage = 60

    # カロリーに換算した理想のPFC比を計算
    ideal_protein_calories = total_calories * (ideal_protein_percentage / 100)
    ideal_fat_calories = total_calories * (ideal_fat_percentage / 100)
    ideal_carbohydrate_calories = total_calories * (ideal_carbohydrate_percentage / 100)

    # 理想のPFC比の円グラフを表示
    labels = ["たんぱく質", "脂質", "炭水化物"]
    sizes = [ideal_protein_calories, ideal_fat_calories, ideal_carbohydrate_calories]
    explode = (0.03, 0.03, 0.03)

    fig, ax = plt.subplots()
    ax.pie(sizes, explode=explode, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")

    st.pyplot(fig)

    # 一日の摂取量の目安の表示
    st.write("一日の摂取量の目安:")
    st.write("たんぱく質:")
    st.write("運動習慣あり：自身の体重 (kg) × 2g")
    st.write("運動習慣なし：自身の体重 (kg) × 1g")
    st.write("脂質:")
    st.write("男性（2650kcal）60~90g")
    st.write("女性（2000kcal）45~70g")
    st.write("炭水化物:")
    st.write("男性（2650kcal）330~430g")
    st.write("女性（2000kcal）250~325g")