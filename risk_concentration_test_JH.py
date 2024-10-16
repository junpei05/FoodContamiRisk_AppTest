import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm

# ページの設定
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# CSVファイルのパス（適宜変更してください）
csv_url = "https://raw.githubusercontent.com/kento-koyama/food_micro_data_risk/main/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E6%BF%83%E5%BA%A6.csv"
csv_url_gui = "https://github.com/kento-koyama/food_micro_data_risk/blob/main/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E6%BF%83%E5%BA%A6.csv"

# フォントファイルのパスを設定
font_path = 'NotoSansCJKjp-Regular.otf'

# Streamlit のアプリケーション
st.title('食中毒細菌の汚染濃度の統計値')
st.write("[食中毒細菌汚染実態_汚染濃度.csv](%s)の可視化です。" % csv_url_gui)
st.write('各表をcsvファイルとしてダウンロードできます。')
st.write('-----------')

# サイドバーにタイトルを追加
st.sidebar.title("検索")

# フォントの設定
fm.fontManager.addfont(font_path)
font_prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = font_prop.get_name()

# データの読み込み
df = pd.read_csv(csv_url, encoding='utf-8-sig')

# log CFU/g のみ、汚染濃度が '不検出' または '-' のものを除外
df = df[~((df['汚染濃度'] == '不検出') | (df['汚染濃度'] == '-') | (df['汚染濃度'] == np.nan))]
df = df[df['単位'] == 'log CFU/g']

# サイドバーに選択オプションを追加
st.sidebar.header('フィルターオプション')
selected_group = st.sidebar.selectbox('食品カテゴリを選択してください:', ['すべて'] + list(df['食品カテゴリ'].unique()))

# 選択された食品カテゴリに基づいて食品名を動的に変更
if selected_group != 'すべて':
    df_filtered = df[df['食品カテゴリ'] == selected_group]
else:
    df_filtered = df

selected_food = st.sidebar.selectbox('食品名を選択してください:', ['すべて'] + list(df_filtered['食品名'].unique()))

# 選択された食品カテゴリと食品名でデータをフィルタリング
if selected_group != 'すべて':
    df_filtered = df[df['食品カテゴリ'] == selected_group]
else:
    df_filtered = df

if selected_food != 'すべて':
    df_filtered = df_filtered[df_filtered['食品名'] == selected_food]

# 表示対象となる細菌リスト
bacteria_list = [
    ("Campylobacter", "カンピロバクターの汚染濃度（すべての食品）"),
    ("Listeria", "リステリアの汚染濃度（すべての食品）"),
    ("Escherichia coli", "腸管出血性大腸菌の汚染濃度（すべての食品）"),
    ("Salmonella", "サルモネラの汚染濃度（すべての食品）")
]

# 細菌ごとのデータを取得してデータ数の多い順にソート
bacteria_counts = []
for bacteria, title in bacteria_list:
    df_bacteria = df_filtered[df_filtered['細菌名'].str.contains(bacteria)]
    if not df_bacteria.empty:
        bacteria_counts.append((df_bacteria, title, len(df_bacteria)))

# データ数の多い順にソート
bacteria_counts.sort(key=lambda x: x[2], reverse=True)

# ソートされた順にセクションを表示
for df_bacteria, title, count in bacteria_counts:
    st.write('-----------')
    st.subheader(title)
    col5, col6 = st.columns(2)

    with col5:
        df_bacteria_display = df_bacteria.iloc[:, [0, 8, 9, 5, 6]]
        df_bacteria_display.columns = ['調査年', '細菌名', '汚染濃度', '食品名', '食品詳細']
        st.dataframe(df_bacteria_display)

    with col6:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(df_bacteria['汚染濃度'].astype(float), bins=range(int(df_bacteria['汚染濃度'].astype(float).min()), int(df_bacteria['汚染濃度'].astype(float).max()) + 2, 1), color='lightgreen', edgecolor='black')
        ax.set_xlabel('汚染濃度 [log CFU/g]', fontsize=18)
        ax.set_ylabel('頻度', fontsize=18)
        ax.set_title(f'{title}', fontsize=20)
        ax.tick_params(axis='both', which='major', labelsize=14)
        plt.grid(True)
        st.pyplot(fig)

# 選択された食品カテゴリと食品名に該当するデータを表示
st.write('-----------')
st.subheader('選択された食品カテゴリと食品名に該当するデータ （すべての食品カテゴリと食品名）')
st.dataframe(df_filtered)
