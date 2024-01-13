アプリ名：フードレコーダー
====

## アプリの機能：
　自分の食事内容を日付ごとに記録し、摂取したカロリー、たんぱく質、脂質、炭水化物を
見ることができ、食事のバランスが取れているか簡単に確認できる。

   ★レコーディングダイエットがしたい方などにお薦め

---
## 開発環境:
Windows10\
VS_Code\
Python3

---
## インストールするライブラリ:

$ pip install ＜ライブラリ名＞

---
## ライブラリ名一覧：

pydantic\
sqlalchemy\
fastapi\
matplotlib\
streamlit\
selenium\
beautifulsoup4

＋ChromeDriverのダウンロード（Google Chromeのバージョンと同じもの）→https://chromedriver.chromium.org/downloads

---
## 実行方法

1． VS_codeでターミナルを開き、streamlit run app.pyを入力\
2．http://localhost:8501/ にアクセス \
3．食べたもの、食べた量、食べた日付を入力して、追加ボタンを押す\
4．機能を選択するのセレクトボックスから、今日食べたものを選択すると、食べたもの一覧が表示される\
5．機能を選択するのセレクトボックスから、栄養素の摂取目安を選択すると、一日の栄養摂取の目安が表示される\
6．機能を選択するのセレクトボックスから、過去の記録を選択し、日付を選択すると、選択した日に食べたものが表示される

## 参考URL
スクレイピングしているwebページ→https://www.eatsmart.jp/
