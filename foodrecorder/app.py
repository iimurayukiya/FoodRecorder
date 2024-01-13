#app.py
from datetime import datetime, date
import re
import streamlit as st
from sqlalchemy.orm import sessionmaker
import main, models, scraping
from database import engine, session

Session = sessionmaker(bind=engine)

# ユーザー一覧を取得
def get_users():
    with Session() as session:
        users = session.query(models.User).all()
        return [user.username for user in users]

# ユーザーの登録
def register_user(username):
    with Session() as session:
        # 既存のユーザー名の重複をチェック
        existing_user = session.query(models.User).filter(models.User.username == username).first()
        if existing_user:
            return False  # ユーザー名が既に存在する場合は登録失敗

        # 新しいユーザーを作成して保存
        user = models.User(username=username)
        session.add(user)
        session.commit()
        return True  # 登録成功

# ユーザーの変更
def update_user(old_username, new_username):
    with Session() as session:
        # 変更前のユーザーを取得
        user = session.query(models.User).filter(models.User.username == old_username).first()
        if user:
            # ユーザー名の重複をチェック
            existing_user = session.query(models.User).filter(models.User.username == new_username).first()
            if existing_user:
                return False  # ユーザー名が既に存在する場合は変更失敗

            # ユーザー名を更新
            user.username = new_username
            session.commit()
            return True  

        return False  

# ユーザーの削除
def delete_user(username):
    with Session() as session:
        # ユーザーを取得
        user = session.query(models.User).filter(models.User.username == username).first()
        if user:
            # ユーザーを削除
            session.delete(user)
            session.commit()
            return True  # 削除成功

        return False  # 削除失敗

# サイドバーでの選択肢
page = st.sidebar.selectbox('初めにユーザー名を入れてください！', ['ユーザー管理画面', '食事を記録する'])

if page == "ユーザー管理画面":
    st.header("ユーザー管理画面")

    # ユーザー登録フォーム
    st.subheader("ユーザー登録")
    new_username = st.text_input("ユーザー名")
    if st.button("登録"):
        if new_username:
            if register_user(new_username):
                st.success("ユーザーが登録されました。")
            else:
                st.warning("ユーザー名が既に存在します。別のユーザー名を入力してください。")
        else:
            st.warning("ユーザー名を入力してください。")

    # ユーザー編集フォーム
    st.subheader("ユーザー名変更")
    users = get_users()
    selected_user = st.selectbox("ユーザーを選択", [""] + users, key="update_user")
    new_username = st.text_input("新しいユーザー名")
    if st.button("編集"):
        if selected_user and new_username:
            if update_user(selected_user, new_username):
                st.success("ユーザー名が変更されました。")
            else:
                st.warning("ユーザー名が既に存在します。別のユーザー名を入力してください。")
        else:
            st.warning("ユーザーを選択し、新しいユーザー名を入力してください。")

    # ユーザー削除フォーム
    st.subheader("ユーザー削除")
    selected_user_delete = st.selectbox("ユーザーを選択", [""] + users, key="delete_user")

    if selected_user_delete:
        confirmed = st.checkbox(f"本当に '{selected_user_delete}' を削除しますか？")
        if confirmed and st.button("削除"):
            if delete_user(selected_user_delete):
                st.success("ユーザーが削除されました。")
            else:
                st.warning("ユーザーの削除に失敗しました。")


elif page == "食事を記録する":
    selected_user = st.sidebar.selectbox("ユーザーを選択してください", [""] + get_users())
    
    # 各機能のボタン表示
    page = st.sidebar.selectbox('機能を選択してください', ['食事を記録する', '今日食べたもの', '栄養素の摂取目安', '過去の記録'])
    
    # 各機能の処理
    if page == '食事を記録する':
        st.title("フードレコーダー")

        if not selected_user:
            st.warning("ユーザーを選択してください。")
            st.stop()

        # 料理名の入力
        recipe_name = st.text_input("食べたものを入力してください")

        # 人数の入力
        servings = st.number_input("何人前食べましたか？", min_value=0.1, step=0.1, value=1.0, format="%.1f")

        # 日付の入力
        date = st.date_input("日付を選択してください")

        # 追加ボタンの表示
        add_button = st.button("追加")

        if add_button:
            if recipe_name and servings and date:
                # 料理名と人数に基づいて栄養素値を取得・保存
                nutrient_values = scraping.get_nutrient_values(recipe_name, servings)

                # 栄養素値をデータベースに保存
                energy_value = float(re.findall(r"\d+", nutrient_values['エネルギー'])[0])
                protein_value = float(re.findall(r"\d+", nutrient_values['たんぱく質'])[0])
                fat_value = float(re.findall(r"\d+", nutrient_values['脂質'])[0])
                carbohydrate_value = float(re.findall(r"\d+", nutrient_values['炭水化物'])[0])

                # 食べた分の栄養素量を計算
                energy_value *= servings
                protein_value *= servings
                fat_value *= servings
                carbohydrate_value *= servings

                # 指定されたユーザー名が存在するかどうかを確認
                user = session.query(models.User).filter(models.User.username == selected_user).first()
                if not user:
                    st.error("指定されたユーザーが見つかりません。ユーザーを選択し直してください。")

                # FoodRecordオブジェクトを作成して保存
                food_record = models.FoodRecord(
                    recipe_name=recipe_name,
                    servings=servings,
                    date=date,
                    energy=energy_value,
                    protein=protein_value,
                    fat=fat_value,
                    carbohydrate=carbohydrate_value,
                    user_id=user.id 
                )

                session.add(food_record)  # 新しいレコードをセッションに追加
                session.commit()  # セッションをコミット

                st.success("食事を記録しました。")

                # 保存した栄養素値の合計を取得
                nutrient_summary = main.get_nutrient_summary(date.strftime("%Y-%m-%d"))

                # 本日の総カロリー量とPFC比のグラフを表示
                main.display_summary(selected_user, date)

    elif page == '今日食べたもの':
        st.title("今日食べたもの")

        if selected_user:
            today = datetime.now().date()
            main.display_daily_summary(selected_user, today)  # 選択されたユーザーの本日の食事記録を表示

        else:
            st.info("今日の食事記録はありません。")

    elif page == '栄養素の摂取目安':
        st.title("摂取量の目安")
        st.write("理想のPFC比")
        main.display_ideal_pfc_ratio()

    elif page == '過去の記録':
        st.title("過去の記録")

        if selected_user:
            # 過去の日付の選択
            selected_date = st.date_input("日付を選択してください")

            # 選択された日付の食事記録を表示
            if selected_date:
                main.display_daily_summary(selected_user, selected_date)