# streamlit run streamlit_app.py

import sqlite3
import pandas as pd
import streamlit as st
from PIL import Image
import datetime
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait, A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from contextlib import closing
import plotly.express as px
import base64
import qrcode
from pdf2image import convert_from_path
from reportlab.pdfbase.ttfonts import TTFont
import pytesseract

import fitz  # PyMuPDFをインポート
import tempfile
import os

# mitsu_web03 commit

# フォントの登録 MSGothic product30
pdfmetrics.registerFont(TTFont('MSGothic', 'msgothic.ttc'))

# データベースに接続
db_name = './data/product30.db'
conn = sqlite3.connect(db_name)
c = conn.cursor()

menu = ["総合生産管理", "受注管理1", "出荷管理2", "在庫管理3", "注文管理4", "顧客管理5"]
submenu1 = ["受注1検索0", "受注1追加1", "受注1編集2", "受注1削除3"]
submenu2 = ["出荷2検索0", "出荷2追加1", "出荷2編集2", "出荷2削除3", "出荷2金額表示4"]
submenu3 = ["在庫3検索0", "在庫3追加1", "在庫3編集2", "在庫3削除3"]
submenu4 = ["注文4検索0_品番_注番", "注文4追加1_日付", '期間別請求書表示', 'invoice表示']
submenu5 = ["顧客5検索0", "顧客5追加1", "顧客5編集2", "顧客5削除3"]

# サイドバーにメニューを表示
choice = st.sidebar.selectbox("Menu", menu)

# Streamlitアプリケーションの設定
def findings10():
    st.title('受注1検索0')
    st.subheader('受注1検索0は品番で表示します。')

    db_name = './data/product30.db'
    conn = sqlite3.connect(db_name)
    c.execute("SELECT * FROM t_受注Data")
    rows = c.fetchall()
    pd.DataFrame(rows, columns=['番号', '品番', '納期', '受注数', '納入数', '注番', '納入日', '注残'])

    # 品番を入力する
    search_term = st.text_input('品番を入力してください')

    # 品番でフィルタリングする
    if search_term:
        query = f"SELECT * FROM t_受注Data WHERE 品番 LIKE '%{search_term}%'"
    else:
        query = "SELECT * FROM t_受注Data"
    df = pd.read_sql(query, conn)
    conn.close()

    # データフレームを表示
    st.write(df)


def addings11():
    st.title('受注1追加1')
    st.subheader('受注1追加1は品番で追加します。')
    image = Image.open('./data/猫.png')
    st.image(image, width=70)

    # SQLite3 DBに接続する
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # テーブルが存在しなければ、テーブルを作成する
    cur.execute('''CREATE TABLE IF NOT EXISTS t_受注Data
                (番号 INTEGER PRIMARY KEY,
                品番 TEXT,
                納期 TEXT,
                受注数 INTEGER,
                納入数 INTEGER,
                注番 TEXT,
                納入日 TEXT,
                注残 INTEGER);''')

    # 品番を入力する
    search_term = st.text_input('品番を入力してください')

    # 品番でフィルタリングする
    if search_term:
        query = f"SELECT * FROM t_受注Data WHERE 品番 LIKE '%{search_term}%'"
        df = pd.read_sql_query(query, conn)
    else:
        query = "SELECT * FROM t_受注Data"
        df = pd.read_sql_query(query, conn)

    # 最後の番号を取得する
    cur.execute("SELECT MAX(番号) FROM t_受注Data")
    last_row = cur.fetchone()[0]
    last_row = last_row if last_row is not None else 0

    # 追加フォームを作成する
    today = datetime.datetime.today().strftime("%Y/%m/%d")

    new_data = {}
    col1, col2, col3 = st.columns(3)
    new_data['番号'] = col1.text_input('番号', value=last_row + 1)
    new_data['品番'] = col1.text_input('品番', search_term)
    new_data['納期'] = col1.text_input('納期')
    new_data['受注数'] = col1.text_input('受注数')
    new_data['納入数'] = col1.text_input('納入数', value=0)
    new_data['注番'] = col2.text_input('注番')
    new_data['納入日'] = col2.text_input('納入日', value=today)
    new_data['注残'] = col2.text_input('注残')

    # 追加ボタンを押したら、DBに書き込む
    if st.button('追加'):
        if search_term:
            query_sql = 'SELECT * FROM t_在庫Data WHERE 品番=?'
            search11 = conn.execute(query_sql, [search_term, ]).fetchall()
            conn.commit()

            if search11 == []:
                st.write(f'{search_term}が見つかりませんでした。在庫登録して下さい。')
                return
            else:
                st.write(f'{search_term}が見つかりました。')

                # 受注データを登録す。
                values = [new_data['番号'], new_data['品番'], new_data['納期'], new_data['受注数'],
                          new_data['納入数'], new_data['注番'], new_data['納入日'], new_data['注残']]
                cur.execute("INSERT INTO t_受注Data VALUES (?, ?, ?, ?, ?, ?, ?, ?)", values)
                conn.commit()

                if search_term:
                    sql = 'SELECT * FROM t_在庫Data'

                    st.write(f"[{new_data['品番']}] [{new_data['注番']}]が追加されました")
                else:
                    st.write('在庫に登録されていません。')

    # データを表示する
    st.write(df)

    # DBをクローズする
    cur.close()
    conn.close()


def changes12():
    st.title('受注1編集2')
    st.subheader('受注1編集2は項目で編集します。')

    image = Image.open('./data/猫.png')
    st.image(image, width=70)

    # テーブルからデータを読み込む
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    df = pd.read_sql('SELECT * FROM t_受注Data', conn)

    # 編集する行を選択する
    row_index = st.number_input('編集する行のindex(薄い数字)を入力してください。', min_value=0, max_value=len(df) - 1,
                                value=0)

    # 編集する項目を選択する
    columns = ['番号', '品番', '納期', '受注数', '納入数', '注番', '納入日', '注残']
    selected_column = st.selectbox('編集する項目を選択してください。', columns)

    # 編集する値を入力する
    new_value = st.text_input('新しい値を入力してください。', value=str(df.loc[row_index, selected_column]))

    # データフレームを表示
    st.write(df)

    # 編集ボタンを押したら、DBを更新する
    if st.button('編集'):
        c.execute(
            f"UPDATE t_受注Data SET {selected_column}='{new_value}' WHERE 番号={df.loc[row_index, '番号']}")
        conn.commit()
        st.success('データが更新されました。')


# ////////// 受注削除[受注1削除3] //////////
def deletes13():
    st.title('受注1削除3')
    st.subheader('受注1削除3は[注番]で削除します。')

    image = Image.open('./data/猫.png')
    st.image(image, width=70)

    # 受注Dataの一覧表を表示する
    conn = sqlite3.connect(db_name)
    df = pd.read_sql('SELECT * FROM t_受注Data', conn)
    st.write(df)

    # 品番を選択して削除する
    # 注番を入力する
    search_term = st.text_input('注番を入力してください')
    dd_注番 = search_term

    if st.button('削除'):
        # SQLite3 DBに接続する
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        dd_注番 = search_term
        cur.execute('DELETE FROM t_受注Data WHERE 注番 = ?', [dd_注番])
        conn.commit()
        st.success(f'[{dd_注番}]データが削除されました。')

        # 削除後のデータを取得
        cur.execute('SELECT * FROM t_受注Data')
        df = pd.DataFrame(cur.fetchall(),
                          columns=['番号', '品番', '納期', '受注数', '納入数', '注番', '納入日', '注残'])

        conn.close()

        # データフレームを表示
        st.write(df)


def findings20():
    # 出荷2検索0
    st.title('出荷2検索0')
    st.subheader('出荷2検索0は品番で表示します。')

    image = Image.open('./data/牛.png')
    st.image(image, width=70)

    # SQLite DBを読み込む
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # 品番を入力する
    search_term = st.text_input('品番を入力してください')

    # 品番でフィルタリングする
    if search_term:
        query = f"SELECT * FROM t_出荷Data WHERE 品番 LIKE '%{search_term}%'"
    else:
        query = "SELECT * FROM t_出荷Data"
    df = pd.read_sql(query, conn)
    conn.close()

    # データフレームを表示
    st.write(df)


# ////////// 出荷検索[出荷2追加1] //////////
def addings21():
    # title表示
    st.title('出荷2追加1')
    st.subheader('出荷2追加1は品番で追加します。')

    image = Image.open('./data/牛.png')
    st.image(image, width=70)

    # SQLite3 DBに接続する
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # 品番を入力する
    search_term = st.text_input('品番を入力してください')
    dd_品番 = search_term

    tanka3_sql = conn.execute('select * from t_在庫Data where 品番=?', [dd_品番, ]).fetchall()
    if not tanka3_sql:
        st.write('品番が見つかりません')
    else:
        dd_単価 = tanka3_sql[0][5]
        conn.commit()
        st.write(f'単価：{dd_単価}')

    # 品番でフィルタリングする
    if search_term:
        query = f"SELECT * FROM t_出荷Data WHERE 品番 LIKE '%{search_term}%'"
        df = pd.read_sql_query(query, conn)
    else:
        query = "SELECT * FROM t_出荷Data"
        df = pd.read_sql_query(query, conn)

    # 最後の番号を取得する
    cur.execute("SELECT MAX(番号) FROM t_出荷Data")
    last_row = cur.fetchone()[0]
    last_row = last_row if last_row is not None else 0

    # 追加フォームを作成する
    new_data = {}

    col1, col2, col3 = st.columns(3)

    # 変数の取得[dd_出荷数][dd_出荷金額]
    dd_出荷数 = col1.text_input('出荷数')
    dd_出荷金額 = dd_単価 * float(dd_出荷数) if dd_出荷数 else 0.0

    today = datetime.date.today().strftime("%Y/%m/%d")
    today = datetime.date.today().strftime("%Y/%m/%d")

    # データを追加入力する
    new_data['番号'] = col1.text_input('番号', value=last_row + 1)
    new_data['品番'] = col1.text_input('品番', value=search_term)
    new_data['出荷数'] = dd_出荷数
    new_data['注番'] = col1.text_input('注番')
    new_data['出荷日'] = col1.text_input('出荷日', value=today)
    new_data['出荷金額'] = col2.text_input('出荷金額', value=str(dd_出荷金額))

    # 追加ボタンを押したら、DBに書き込む
    if st.button('追加'):
        values = [new_data['番号'], new_data['品番'], new_data['出荷数'], new_data['注番'],
                  new_data['出荷日'], new_data['出荷金額']]
        cur.execute("INSERT INTO t_出荷Data VALUES (?, ?, ?, ?, ?, ?)", values)
        conn.commit()

        # 受注Dataから注番をキーに検索する
        Tyuban01 = new_data['注番']
        conn = sqlite3.connect(db_name)
        Tyuban01_sql = conn.execute('select * from t_受注Data where 注番=?',
                                    [Tyuban01, ]).fetchall()
        conn.commit()

        # sd1_受注数,sd1_納入計,sd1_注残を検索する
        sd1_受注数 = Tyuban01_sql[0][3]
        sd1_納入計 = Tyuban01_sql[0][4]
        sd1_注残 = Tyuban01_sql[0][7]

        # New_納入計を生産する
        New_納入計 = int(sd1_納入計) + int(new_data['出荷数'])
        st.success(f'データがが追加されました。')

        # new_data['品番'], new_data['注番']をキーに納入数を書き換える
        update01_sql = 'update t_受注Data set 納入数 = ? where 品番 = ? AND 注番 =?'
        conn.execute(update01_sql, [New_納入計, new_data['品番'], new_data['注番']])
        conn.commit()

        # new_data['品番'], new_data['注番']をキーに納入日を書き換える
        update01_sq2 = 'update t_受注Data set 納入日 = ? where 品番 = ? AND 注番 =?'
        conn.execute(update01_sq2, [new_data['出荷日'], new_data['品番'], new_data['注番']])
        conn.commit()

        # New_注残を算出する
        New_注残0 = int(sd1_受注数) - int(New_納入計)

        # New_注残が[完納]か[注残]のメッセージのコメントを記入する
        if sd1_受注数 == New_納入計:
            New_注残 = f'{New_注残0} [[完納]]'
        else:
            New_注残 = f'{New_注残0} [注残]'

        # 出荷入力時に、在庫Dataの在庫数から、出荷数を差し引く。
        Hindan01 = dd_品番
        conn = sqlite3.connect(db_name)
        Tyuban01_sql_sql = conn.execute('select * from t_在庫Data where 品番=?',
                                        [Hindan01, ]).fetchall()
        conn.commit()

        # sd1_受注数,sd1_納入計,sd1_注残を検索する
        dd_在庫数 = Tyuban01_sql_sql[0][3]
        New在庫数 = int(dd_在庫数) - int(dd_出荷数)
        st.success(New在庫数)
        st.success(new_data['品番'])

        # New在庫数のsqlを実施する[t_在庫Data]
        update01_sq1 = 'update t_在庫Data set 在庫数 = ? where 品番 = ?'
        conn.execute(update01_sq1, [f'{New在庫数}', new_data['品番'], ])
        conn.commit()

        # New_注残の_sqlを実施する[t_受注Data]
        update02_sq2 = 'update t_受注Data set 注残 = ? where 品番 = ? AND 注番 =?'
        conn.execute(update02_sq2, [f'{New_注残}', new_data['品番'], new_data['注番']])
        conn.commit()

    # データを表示する
    st.write(df)
    st.success(new_data['注番'])

    # DBをクローズする
    cur.close()
    conn.close()


# ////////// 出荷編集[出荷2編集2] //////////
def changes22():
    st.title('出荷2編集2')
    st.subheader('出荷2編集2は項目で編集します。')

    image = Image.open('./data/牛.png')
    st.image(image, width=70)

    # テーブルからデータを読み込む
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    df = pd.read_sql('SELECT * FROM t_出荷Data', conn)

    # 編集する行を選択する
    row_index = st.number_input('編集する行のindex(薄い数字)を入力してください。', min_value=0, max_value=len(df) - 1,
                                value=0)

    # 編集する項目を選択する
    columns = ['番号', '品番', '出荷数', '注番', '出荷日', '出荷金額']
    selected_column = st.selectbox('編集する項目を選択してください。', columns)

    # 編集する値を入力する
    new_value = st.text_input('新しい値を入力してください。', value=str(df.loc[row_index, selected_column]))

    # 編集ボタンを押したら、DBを更新する
    if st.button('編集'):
        c.execute(
            f"UPDATE t_出荷Data SET {selected_column}='{new_value}' WHERE 番号={df.loc[row_index, '番号']}")
        conn.commit()
        st.success('データが更新されました。')

    # データフレームを表示
    st.write(df)

    # DBをクローズする
    conn.close()


# ////////// 出荷削除[出荷2削除3] //////////
def deletes23():
    # title表示する
    st.title('出荷2削除3')
    st.subheader('出荷1削除3は[index(薄い数字)]で削除します。')

    # Image画像の指定
    image = Image.open('./data/牛.png')
    st.image(image, width=70)

    # SQLite3 DBに接続する
    conn = sqlite3.connect(db_name)
    df = pd.read_sql('SELECT * FROM t_出荷Data', conn)

    # 編集する行を選択する
    row_index = st.number_input('編集する行のindex(薄い数字)を入力してください。', min_value=0, max_value=len(df) - 1,
                                value=0)
    # データフレームを表示
    st.write(df)

    # SQLite3 DBに接続する
    conn = sqlite3.connect(db_name)
    df = pd.read_sql('SELECT * FROM t_出荷Data', conn)

    if st.button('削除'):
        # SQLite3 DBに接続する
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        dd_番号 = row_index
        cur.execute('DELETE FROM t_出荷Data WHERE 番号 = ?', [dd_番号])
        conn.commit()
        st.success(f'{dd_番号}データが削除されました。')

        # 削除後のデータを取得
        cur.execute('SELECT * FROM t_出荷Data')
        df = pd.DataFrame(cur.fetchall(),
                          columns=['番号', '品番', '納入数', '注番', '納入日', '納入金額'])
        # 番号,品番,納入数,注番,納入日,納入金額
        conn.close()

        # データフレームを表示
        st.write(df)


# ////////// 出荷追加[出荷Dataの金額表示] //////////
def showamount24():
    # title表示する
    st.title('出荷2金額表示表示4')
    st.subheader('出荷Dataの金額表示します。')

    image = Image.open('./data/牛.png')
    st.image(image, width=70)

    conn = sqlite3.connect(db_name)
    df = pd.read_sql('SELECT * FROM t_出荷Data', conn)

    # 注番を入力する
    search_term = st.text_input('注番を入力してください')

    # 注番でフィルタリングする
    if search_term:
        query = f"SELECT * FROM t_出荷Data WHERE 注番 LIKE '%{search_term}%'"
        df = pd.read_sql_query(query, conn)

    # データフレームを表示
    st.write(df)


# ////////// 在庫検索[在庫3検索0] //////////
def finding30():
    # title表示する
    st.title('在庫3検索0')
    st.subheader('在庫3検索0は品番で表示します。')

    image = Image.open('./data/犬.png')
    st.image(image, width=70)

    # SQLite DBを読み込む
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # 品番を入力する
    search_term = st.text_input('品番を入力してください')

    # 品番でフィルタリングする
    if search_term:
        query = f"SELECT * FROM t_在庫Data WHERE 品番 LIKE '%{search_term}%'"
    else:
        query = "SELECT * FROM t_在庫Data"
    df = pd.read_sql(query, conn)
    conn.close()

    # データフレームを表示
    st.write(df)


def adding31():
    # title表示する
    st.title('在庫3追加1')
    st.subheader('在庫3追加1は品番で追加します。')

    image = Image.open('./data/犬.png')
    st.image(image, width=70)

    # SQLite3 DBに接続する
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # 品番を入力する
    search_term = st.text_input('品番を入力してください')
    dd_品番 = search_term
    tanka3_sql = conn.execute('select * from t_在庫Data where 品番=?', [dd_品番, ]).fetchall()

    if not tanka3_sql:
        st.write('在庫追加を続けて下さい＞')
        new_data = {}
    else:
        st.write('品番が重複しています。確認してください。')

    # 品番でフィルタリングする
    if search_term:
        query = f"SELECT * FROM t_在庫Data WHERE 品番 LIKE '%{search_term}%'"
        df = pd.read_sql_query(query, conn)
    else:
        query = "SELECT * FROM t_在庫Data"
        df = pd.read_sql_query(query, conn)

    # 最後の番号を取得する
    cur.execute("SELECT MAX(番号) FROM t_在庫Data")
    last_row = cur.fetchone()[0]
    last_row = last_row if last_row is not None else 0

    # 追加フォームを作成する
    new_data = {}
    col1, col2, col3 = st.columns(3)
    new_data['番号'] = col1.text_input('番号', value=last_row + 1)
    new_data['品番'] = col1.text_input('品番', value=search_term)
    new_data['名称'] = col1.text_input('名称')
    new_data['在庫数'] = col1.text_input('在庫数')
    new_data['作成日'] = col1.text_input('作成日')
    new_data['単価'] = col1.text_input('単価')
    new_data['在庫日'] = col2.text_input('在庫日')

    # 追加ボタンを押したら、DBに書き込む
    if st.button('追加'):
        values = [new_data['番号'], new_data['品番'], new_data['名称'], new_data['在庫数'],
                  new_data['作成日'],
                  new_data['単価'], new_data['在庫日']]
        cur.execute("INSERT INTO t_在庫Data VALUES (?, ?, ?, ?, ?, ?, ?)", values)
        conn.commit()

        st.success('データが追加されました。')

    # データを表示する
    st.write(df)

    # DBをクローズする
    cur.close()
    conn.close()


# ////////// 在庫編集[在庫3編集2] //////////
def changes32():
    # title表示する
    st.title('在庫3編集2')
    st.subheader('在庫3編集2は項目で編集します。')

    image = Image.open('./data/犬.png')
    st.image(image, width=70)

    # テーブルからデータを読み込む
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    df = pd.read_sql('SELECT * FROM t_在庫Data', conn)

    # 編集する行を選択する
    row_index = st.number_input('編集する行のindex(薄い数字)を入力してください。', min_value=0, max_value=len(df) - 1,
                                value=0)

    # 編集する項目を選択する
    columns = ['番号', '品番', '名称', '在庫数', '作成日', '単価', '在庫日']
    selected_column = st.selectbox('編集する項目を選択してください。', columns)

    # 編集する値を入力する
    new_value = st.text_input('新しい値を入力してください。', value=str(df.loc[row_index, selected_column]))

    # 編集ボタンを押したら、DBを更新する
    if st.button('編集'):
        c.execute(
            f"UPDATE t_在庫Data SET {selected_column}='{new_value}' WHERE 番号={df.loc[row_index, '番号']}")
        conn.commit()
        st.success('データが削除されました。')

    # データフレームを表示
    st.write(df)

    # DBをクローズする
    conn.close()


# ////////// 在庫編集[在庫3削除3] //////////
def delete33():
    # title表示する
    st.title('在庫3編集3')
    st.subheader('在庫3削除3は[注番]で削除します。')

    # Image画像の指定
    image = Image.open('./data/犬.png')
    st.image(image, width=70)

    # SQLite3 DBに接続する
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()

    # 品番を選択して削除する
    st.subheader('在庫データを削除します。')

    # 品番を入力する
    search_term = st.text_input('品番を入力してください')

    # 品番でフィルタリングする
    if search_term:
        query = f"SELECT * FROM t_在庫Data WHERE 品番 LIKE '%{search_term}%'"
    else:
        query = "SELECT * FROM t_在庫Data"
    df = pd.read_sql(query, conn)
    conn.close()

    # データフレームを表示
    st.write(df)

    if st.button('削除'):
        # SQLite3 DBに接続する
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        dd_品番 = search_term
        delete_sql = conn.execute('delete from t_在庫Data where 品番 =?',
                                  [dd_品番, ]).fetchall()
        conn.commit()
        st.success(f'{dd_品番}データが削除されました。')

        # データフレームを表示
        st.write(df)


# ////////// 受注出荷[受注4削除3] //////////
def findings40():
    # title表示する
    st.title('受注出荷')
    st.subheader('受注出荷Dataは品番で検索し、注番で絞り込みます。')

    image = Image.open('./data/猪.png')
    st.image(image, width=70)

    conn = sqlite3.connect(db_name)

    # 品番を入力する
    search_term = st.text_input('品番を入力してください')

    # 品番でフィルタリングする
    if search_term:
        df1 = pd.read_sql(f"SELECT * FROM t_受注Data WHERE 品番 LIKE '%{search_term}%'", conn)
        df2 = pd.read_sql(f"SELECT * FROM t_出荷Data WHERE 品番 LIKE '%{search_term}%'", conn)
    else:
        df1 = pd.read_sql("SELECT * FROM t_受注Data", conn)
        df2 = pd.read_sql("SELECT * FROM t_出荷Data", conn)

    # 注番を入力する
    search_term2 = st.text_input('注番を入力してください')

    # 注番でフィルタリングする
    if search_term2:
        df1 = df1[df1['注番'].str.contains(search_term2)]
        df2 = df2[df2['注番'].str.contains(search_term2)]

    # 二つのカラムを用意する
    col1, col2 = st.columns(2)

    # 左側のカラムにテーブル1を表示
    with col1:
        st.write(df1)

    # 右側のカラムにテーブル2を表示
    with col2:
        st.write(df2)

    st.write('全画面データを表示します。')
    st.write(df1)
    st.write(df2)

    conn.close()


# ////////// 出荷[注文4追加1_日付] //////////
def addings41():
    # title表示する
    st.title('受注出荷')
    st.subheader('出荷Dataは出荷日で検索し絞り込みます。')

    image = Image.open('./data/猪.png')
    st.image(image, width=70)

    conn = sqlite3.connect(db_name)

    # 品番を入力する
    search_term = st.text_input('出荷日を入力してください')

    # 品番でフィルタリングする
    if search_term:
        query = f"SELECT * FROM t_出荷Data WHERE 出荷日 LIKE '%{search_term}%'"
    else:
        query = "SELECT * FROM t_出荷Data"
    df = pd.read_sql(query, conn)
    conn.close()

    st.write(df)


def show_data42():
    # title表示する
    st.title('カレンダー選択表示42')
    st.subheader('期間別に、カレンダーでデータを抽出します。')

    image = Image.open('./data/猪.png')
    st.image(image, width=70)

    # SQLite3に接続
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # ユーザーからの入力を受け取る
    start_date = st.date_input("開始日を選択してください")
    end_date = st.date_input("終了日を選択してください")

    # クエリを実行
    if st.button('実行'):
        # クエリを実行
        if start_date and end_date:
            # クエリを作成

            query = f"SELECT * FROM t_受注Data WHERE 納期 BETWEEN '{start_date.strftime('%Y/%m/%d')}" \
                    f"' AND '{end_date.strftime('%Y/%m/%d')}'"

            # SQLite3にクエリを実行して、データフレームに変換
            df = pd.read_sql(query, conn)

            # 結果を表示
            if df.empty:
                st.warning("該当するデータがありません。")
            else:
                st.warning(f'{start_date}から{end_date}までの受注Dataを表示します。')
                st.write(df)

        # 接続を閉じる
        cursor.close()
        conn.close()


def show_invoice43():
    # title表示する
    st.title('月単位請求項目表示4')
    st.subheader('月単位請求を抽出します。')

    image = Image.open('./data/猪.png')
    st.image(image, width=70)

    # データベースに接続
    db_name = './data/product30.db'
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # 日付選択
    start_date = st.date_input("開始日を選択してください")
    end_date = st.date_input("終了日を選択してください")

    if st.button('実行'):
        # global qd_会社id
        # SQLクエリの作成と実行
        sql = """
            select t_出荷Data.品番, t_在庫Data.名称, t_在庫Data.単価, t_出荷Data.出荷数, t_出荷Data.出荷日, t_在庫Data.Tax, t_出荷Data.出荷金額
            FROM t_出荷Data INNER JOIN t_在庫Data
            ON t_出荷Data.品番 = t_在庫Data.品番
            WHERE t_出荷Data.出荷日 BETWEEN ? AND ?
        """
        c.execute(sql, (start_date.strftime('%Y/%m/%d'), end_date.strftime('%Y/%m/%d')))

        # SELECT COUNT(*) FROM t_出荷Data

        # 結果をデータフレームに変換して表示
        df = pd.DataFrame(c.fetchall(),
                          columns=['品番', '名称', '単価', '出荷数', '出荷日', 'Tax', '出荷金額'])
        st.write(df)

        # query_totalクエリを実行して、データフレームに変換
        query_total = f"SELECT sum(出荷金額) FROM t_出荷Data WHERE 出荷日 BETWEEN '" \
                      f"{start_date.strftime('%Y/%m/%d')}' AND '{end_date.strftime('%Y/%m/%d')}'"
        dd_出荷合計 = conn.execute(query_total).fetchone()[0]
        # st.write(f'出荷合計額: {dd_出荷合計:,}円')

        dd_請求金額 = int(dd_出荷合計) * 1.1
        dd_消費税額 = int(dd_出荷合計) * 0.1

        # st.write(f'10%選択しました。消費税額：{int(dd_消費税額):,} 円です。')
        # st.write(f'10%選択しました。請求金額：{int(dd_請求金額):,} 円です。')

        # カーソルを作成
        cursor = conn.cursor()

        # SQLクエリを実行して結果を取得
        query_count = f"SELECT COUNT(*) FROM t_出荷Data WHERE 出荷日 BETWEEN '" \
                      f"{start_date.strftime('%Y/%m/%d')}' AND '{end_date.strftime('%Y/%m/%d')}'"
        cursor.execute(query_count)
        result43 = cursor.fetchone()[0]
        st.write(result43)

        # データベースとの接続を閉じる
        conn.close()

        ###### Invoice帳票 And QRコードを作成 ######################################################################
        qr = qrcode.QRCode(
            version=10,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=2,
            border=8
        )

        # q_data = 'https://engineer-lifestyle-blog.com/'
        q_data = 'df'

        qr.add_data(q_data)
        qr.make()
        _img = qr.make_image(fill_color="black", back_color="#ffffff")
        _img.save('./data/qrcode45.png')
        img = Image.open('./data/qrcode45.png')
        img.show()

        ###### Invoice_issue を発行######################################################################
        # 縦型A4のCanvasを準備
        # PDFファイルの保存先ディレクトリ "C:\Users\marom\Invoice"
        # pdf_directory = r"C:\Users\Invoice"
        pdf_directory = r"C:\Users\marom\Invoice"

        # 日付をYYYYMMDD形式に変換し、ファイル名に使用する
        today = date.today()
        today_str_cnv = today.strftime('%Y%m%d')

        # PDFファイルのパス
        pdf_path = f"{pdf_directory}\\Invoice_{today_str_cnv}.pdf"

        # PDFを作成する
        cv = canvas.Canvas(pdf_path, pagesize=portrait(A4))

        # フォントサイズ定義
        font_size1 = 20
        font_size2 = 14
        # cv.setFont('HeiseiKakuGo-W5', font_size2)
        cv.setFont('MSGothic', font_size2)

        # 日付をYYYYMMDD形式に変換し、ファイル名に使用する
        # today = date.today()
        # today_str_cnv = today.strftime('%Y%m%d')
        # cv = canvas.Canvas(f'Invoice_{today_str_cnv}.pdf', pagesize=portrait(A4))

        # フォント登録
        # pdfmetrics.registerFont(UnicodeCIDFont('HeiseiKakuGo-W5'))

        # フォントサイズ定義
        font_size1 = 20
        font_size2 = 14
        font_size3 = 10
        # cv.setFont('HeiseiKakuGo-W5', font_size2)
        cv.setFont('MSGothic', font_size2)

        # 表題欄 (x座標, y座標, 文字)を指定
        # cv.setFont('HeiseiKakuGo-W5', font_size1)
        cv.setFont('MSGothic', font_size1)
        cv.drawString(50, 760, 'Invoice(期間別[月/日/任意]請求書)')

        # cv.setFont('HeiseiKakuGo-W5', font_size2)
        cv.setFont('MSGothic', font_size2)
        cv.drawString(450, 760, f'Inv- {today_str_cnv}')

        # 画像挿入(画像パス、始点x、始点y、幅、高さ) watermark.jpg
        cv.drawInlineImage('./data/com_logo01.png', 470, 670, 80, 80)
        cv.drawInlineImage('./data/qrcode45.png', 40, 25, 100, 100)

        # 顧客Dataより、[会社名][Email]][TEL][担当者]を抽出する
        conn = sqlite3.connect(db_name)
        c = conn.cursor()

        # query_totalクエリを実行して、データフレームに変換 qd_会社id
        # dd_会社ID = '1'
        # Comid_sql = conn.execute('SELECT * FROM t_顧客Data WHERE 会社ID = ?', (dd_会社ID,)).fetchall()
        qd_会社id = '1'
        Comid_sql = conn.execute('SELECT * FROM t_顧客Data WHERE 会社ID = ?', (qd_会社id,)).fetchall()

        # 顧客Dataの抽出
        dd_会社名 = Comid_sql[0][1]
        dd_Email = Comid_sql[0][2]
        dd_TEL = Comid_sql[0][5]
        dd_担当者 = Comid_sql[0][7]

        conn.commit()
        conn.close()

        # 見出し表題を記入する
        cv.drawString(50, 695, f'{dd_会社名} 御中　{dd_担当者}　様')
        cv.drawString(50, 680, dd_Email)
        cv.drawString(50, 665, dd_TEL)
        cv.drawString(430, 655, '（株）仁志田製作所')
        cv.drawString(405, 640, '東京都板橋区中台1-3-5')
        cv.drawString(385, 625, 'Supplier5678@gmail.com')
        cv.drawString(450, 610, '03(3111)1200')
        # cv.setFont('HeiseiKakuGo-W5', font_size2)
        cv.setFont('MSGothic', font_size2)

        # 期間の表材の作成
        string11 = f'{start_date} から{end_date}'
        cv.drawString(100, 570, f'{string11}納入分 請求金額:￥{int(dd_請求金額):,}円')

        cv.setLineWidth(1.5)
        # 線を描画(始点x、始点y、終点x、終点y)
        cv.line(95, 562, 520, 562)
        cv.line(45, 755, 560, 755)

        # cv.setFont('HeiseiKakuGo-W5', font_size3)
        cv.setFont('MSGothic', font_size3)

        # ヘッター欄
        cv.drawString(52, 534, '品  番')
        cv.drawString(132, 534, '名  称')
        cv.drawString(262, 534, '単  価')
        cv.drawString(312, 534, '出荷数')
        cv.drawString(367, 534, '出荷日')
        cv.drawString(447, 534, 'Tax')
        cv.drawString(492, 534, '出荷金額')

        # 一列目[品番]
        for i in range(len(df)):
            cv.drawString(42, 514 - (i * 20), str(df.iloc[i, 0]))

        # 二列目[名称]
        for i in range(len(df)):
            cv.drawString(122, 514 - (i * 20), str(df.iloc[i, 1]))

        # 三列目[単価]
        for i in range(len(df)):
            cv.drawString(252, 514 - (i * 20), "{:.2f}".format(df.iloc[i, 2]))

        # 四列目[出荷数]
        for i in range(len(df)):
            cv.drawString(307, 514 - (i * 20), "{:,}".format(df.iloc[i, 3]))

        # 五列目[出荷日]
        for i in range(len(df)):
            cv.drawString(357, 514 - (i * 20), str(df.iloc[i, 4]))

        # 六列目[Tax]
        for i in range(len(df)):
            cv.drawString(447, 514 - (i * 20), "{:,}".format(df.iloc[i, 5]))

        # 七列目[出荷金額]
        for i in range(len(df)):
            cv.drawString(477, 514 - (i * 20), "{:,}".format(df.iloc[i, 6]))

        # 表の作成[6列21行] # cv.showPage()  改行ページ
        cv.setLineWidth(1)
        xlist = (40, 120, 250, 300, 350, 440, 470, 575)  # 差分　80,160,80,80,100       6列21行
        ylist = (
            130, 150, 170, 190, 210, 230, 250, 270, 290, 310, 330, 350, 370, 390, 410, 430, 450, 470, 490,
            510, 530, 550)  # 差分　20(21行)
        cv.grid(xlist, ylist)

        # 小計額/消費税/合計額の表題
        cv.drawString(370, 104, '小計額')
        cv.drawString(340, 85, '消費税(10%)')
        cv.drawString(340, 65, '消費税( 8%)')
        cv.drawString(370, 45, '合計額')

        # 小計額/消費税/合計額のData
        cv.drawString(460, 105, f'￥{int(dd_出荷合計):,}円')
        cv.drawString(460, 85, f'￥{int(dd_消費税額):,}円')
        cv.drawString(460, 65, f'￥0円')
        cv.drawString(460, 45, f'￥{int(dd_請求金額):,}円')

        # 表の作成[1列4行]
        cv.setLineWidth(1)
        xlist = (410, 560)
        ylist = (40, 60, 80, 100, 120)
        cv.grid(xlist, ylist)

        # # PDFファイルを保存
        # cv.save()

        # PDFファイルを保存する
        cv.save()

        # Streamlitにファイルの保存を通知する
        st.write('保存ファイル')
        st.write(f"PDF file saved at: {pdf_path}")

def pdf_to_images(file_path):
    images = []
    with fitz.open(file_path) as pdf_document:
        for page_num in range(pdf_document.page_count):
            page = pdf_document.load_page(page_num)
            pixmap = page.get_pixmap()
            img = Image.frombytes("RGB", [pixmap.width, pixmap.height], pixmap.samples)
            images.append(img)
    return images

def invoice_show44():
    st.title("PDF Viewer")

    uploaded_file = st.file_uploader("PDFファイルをアップロードしてください", type=["pdf"])

    if uploaded_file:
        # 一時ファイルをディスクに保存してからパスを取得
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(uploaded_file.read())
            temp_file_path = temp_file.name

        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": uploaded_file.size}
        st.write(file_details)

        # PDFを画像に変換
        images = pdf_to_images(temp_file_path)

        # 画像を表示
        for image in images:
            st.image(image, use_column_width=True)

        # 一時ファイルを削除
        os.remove(temp_file_path)


# ///////////////////////////////////////////////////////////////////////////////////////////////////
# 選択されたメニューに応じて、選択肢を表示
if choice == "受注管理1":
    # st.sidebar.markdown("Select a submenu:")
    submenu_choice = st.sidebar.selectbox("", submenu1)

    # 選択されたサブメニューの情報を表示
    if submenu_choice == "受注1検索0":
        findings10()
    elif submenu_choice == "受注1追加1":
        addings11()
    elif submenu_choice == "受注1編集2":
        changes12()
    elif submenu_choice == "受注1削除3":
        deletes13()

elif choice == "出荷管理2":
    st.sidebar.markdown("Select a submenu:")
    submenu_choice = st.sidebar.selectbox("", submenu2)

    # 選択されたサブメニューの情報を表示
    if submenu_choice == "出荷2検索0":
        findings20()
    elif submenu_choice == "出荷2追加1":
        addings21()
    elif submenu_choice == "出荷2編集2":
        changes22()
    elif submenu_choice == "出荷2削除3":
        deletes23()
    elif submenu_choice == "出荷2金額表示4":
        showamount24()

elif choice == "在庫管理3":
    st.sidebar.markdown("Select a submenu:")
    submenu_choice = st.sidebar.selectbox("", submenu3)

    # 選択されたサブメニューの情報を表示
    if submenu_choice == "在庫3検索0":
        finding30()
    elif submenu_choice == "在庫3追加1":
        adding31()
    elif submenu_choice == "在庫3編集2":
        changes32()
    elif submenu_choice == "在庫3削除3":
        delete33()

if choice == "注文管理4":
    st.sidebar.markdown("Select a submenu:")
    submenu_choice = st.sidebar.selectbox("", submenu4)

    # 選択されたサブメニューの情報を表示
    if submenu_choice == "注文4検索0_品番_注番":
        # st.title('findings40()')
        findings40()
    elif submenu_choice == "注文4追加1_日付":
        # st.title('addings41()')
        addings41()
    elif submenu_choice == "受注データ表示":
        # st.title('show_data42()')
        show_data42()
    elif submenu_choice == "期間別請求書表示":
        show_invoice43()
    elif submenu_choice == "invoice表示":
        # st.title('invoice_show44()')
        invoice_show44()

elif choice == "顧客管理5":
    st.sidebar.markdown("Select a submenu:")
    submenu_choice = st.sidebar.selectbox("", submenu5)

    # 選択されたサブメニューの情報を表示
    if submenu_choice == "顧客5検索0":
        findings50()
    elif submenu_choice == "顧客5追加1":
        addings51()
    elif submenu_choice == "顧客5編集2":
        changes52()
    elif submenu_choice == "顧客5削除3":
        deletes53()


if choice == "総合生産管理":
    # global qd_会社id

    # title‘画像を表示する
    # st.title("総合生産管理(販売/生産に適用)")
    #
    # # SQLite3 DBに接続する
    # conn = sqlite3.connect(db_name)
    # c = conn.cursor()
    #
    # # 会社名のリストを取得する
    # c.execute('SELECT 会社名 FROM t_顧客Data')
    # company_names = [row[0] for row in c.fetchall()]
    #
    # # ユーザーに会社名を選択させる
    # selected_company_name = st.selectbox('Select a company name:', company_names)
    #
    # selected_company_index = company_names.index(selected_company_name)
    # qd_会社id = selected_company_index + 1
    # st.write(qd_会社id)

    # 選択された会社名を表示する
    # st.write('You selected:', selected_company_name)

    # title‘画像を表示する
    st.caption("受注管理1:")
    image = Image.open('./data/猫.png')
    st.image(image, width=70)

    st.caption("出荷管理2:")
    image1 = Image.open('./data/牛.png')
    st.image(image1, width=70)

    st.caption("在庫管理3:")
    image1 = Image.open('./data/犬.png')
    st.image(image1, width=70)

    st.caption("注文管理4:")
    image1 = Image.open('./data/猪.png')
    st.image(image1, width=70)

    st.caption("顧客管理5:")
    image1 = Image.open('./data/狐.png')
    st.image(image1, width=70)

    # streamlit run streamlit_app121.py
