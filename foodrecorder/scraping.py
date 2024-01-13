#scraping.py
import streamlit as st
from database import session
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions

#スクレイピング
def get_nutrient_values(recipe_name, servings):
    # Chromeドライバーのパスを設定
    chromedriver_path = "chromedriver.exe"

    # ChromeドライバーのServiceオブジェクトを作成
    service = Service(chromedriver_path)

    # Chromeドライバーを起動
    driver = webdriver.Chrome(service=service)

    # Webページにアクセス
    driver.get("https://www.eatsmart.jp/do/caloriecheck/index")

    # レシピ名の入力
    recipe_name_input = driver.find_element(By.XPATH, "//input[@name='searchKey']")
    recipe_name_input.send_keys(recipe_name)

    # 検索
    search_button = driver.find_element(By.XPATH, "//input[@type='image']")
    search_button.click()

    # 検索結果から一番上のリンクをクリック
    try:
        wait = WebDriverWait(driver, 1)
        top_result_link = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[contains(text(),'{recipe_name}')]")))
        top_result_link.click()
    except selenium.common.exceptions.TimeoutException:
        st.write("要素が見つかりませんでした。")

    sleep(1)

    # BeautifulSoupオブジェクトを作成
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # エネルギー、タンパク質、脂質、炭水化物の値を取得
    nutrients = soup.select("td.item > a")
    values = soup.select("td.capa")

    data = {}
    for nutrient, value in zip(nutrients, values):
        nutrient_name = nutrient.text.strip()
        nutrient_value = value.text.strip()
        data[nutrient_name] = nutrient_value

    # エネルギー、タンパク質、脂質、炭水化物の値を取り出す
    energy = data.get("エネルギー", "")
    energy = energy.replace("kcal", "")
    protein = data.get("たんぱく質", "")
    fat = data.get("脂質", "")
    carbohydrate = data.get("炭水化物", "")
    
    # 1人分の栄養素値を計算
    energy_per_serving = float(energy)
    protein_per_serving = float(protein.replace("g", ""))
    fat_per_serving = float(fat.replace("g", ""))
    carbohydrate_per_serving = float(carbohydrate.replace("g", ""))

    # 合計の栄養素値を計算
    total_energy = energy_per_serving * servings
    total_protein = protein_per_serving * servings
    total_fat = fat_per_serving * servings
    total_carbohydrate = carbohydrate_per_serving * servings

    session.rollback()

    # Streamlitで値を表示
    st.write("1人分の栄養素量:")
    st.write("エネルギー:", energy)
    st.write("タンパク質:", protein)
    st.write("脂質:", fat)
    st.write("炭水化物:", carbohydrate)
    st.write("-----")
    st.write("食べた分の栄養素量:")
    st.write("総エネルギー:", round(total_energy, 1))
    st.write("総タンパク質:", round(total_protein, 1))
    st.write("総脂質:", round(total_fat, 1))
    st.write("総炭水化物:", round(total_carbohydrate, 1))

    session.remove()
    driver.quit()
    return data