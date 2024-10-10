import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from io import BytesIO

# ページの設定
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# CSVファイルのパス（適宜変更してください）
csv_url = "https://github.com/kento-koyama/food_micro_data_risk/blob/47e3ffaccfc2b2fce2aef0a49812df23a091f8c2/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E6%BF%83%E5%BA%A6.csv"

# フォントファイルのパスを設定
font_path = 'NotoSansCJKjp-Regular.otf'

# Streamlit のアプリケーション
st.title('食中毒細菌の汚染濃度の統計値')
st.write("[食中毒細菌汚染実態_汚染濃度.csv](%s)の可視化です。" % csv_url)
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
df = df[~((df['汚染濃度'] == '不検出') | (df['汚染濃度'] == '-'))]
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

# データフィルタリングと表示
def filter_and_display_data(selected_group, selected_food):
    if selected_group != 'すべて':
        df_filtered = df[df['食品カテゴリ'] == selected_group]
    else:
        df_filtered = df

    if selected_food != 'すべて':
        df_filtered = df_filtered[df_filtered['食品名'] == selected_food]

    # 細菌ごとの検体数と陽性数の合計を計算
    bacteria_samplesize = df_filtered['細菌名'].value_counts().reset_index()
    bacteria_samplesize.columns = ['細菌名', '検体数の合計']
    st.dataframe(bacteria_samplesize)

    # 検体数の合計を水平棒グラフで可視化
    st.subheader('細菌ごとの検体数の合計')
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(bacteria_samplesize['細菌名'], bacteria_samplesize['検体数の合計'], color='skyblue')
    ax.set_xlabel('検体数の合計', fontsize=14)
    ax.set_ylabel('細菌名', fontsize=14)
    ax.set_title('細菌ごとの検体数の合計', fontsize=16)
    ax.grid(True)
    st.pyplot(fig)

    # フィルタリングされたデータを表示
    # st.subheader('細菌ごとの検体数の合計')
    df_bacteria_counts = df_filtered.copy()
    df_bacteria_counts = df_bacteria_counts.iloc[:,[0,8,9,6]]
    df_bacteria_counts.columns = ['調査年', '細菌名', '汚染濃度', '食品詳細']
    st.dataframe(df_bacteria_counts)

    # 汚染濃度の分布をヒストグラムで可視化（刻み幅1）
    st.subheader('汚染濃度の分布')
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(df_filtered['汚染濃度'].astype(float), bins=range(int(df_filtered['汚染濃度'].astype(float).min()), int(df_filtered['汚染濃度'].astype(float).max()) + 2, 1), color='lightgreen', edgecolor='black')
    ax.set_xlabel('汚染濃度 [log CFU/g]', fontsize=18)
    ax.set_ylabel('頻度', fontsize=18)
    ax.set_title('汚染濃度の分布', fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=14)
    plt.grid(True)
    st.pyplot(fig)

# 選択されたフィルターを使用してデータを表示
filter_and_display_data(selected_group, selected_food)
