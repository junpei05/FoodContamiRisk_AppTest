import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.font_manager as fm
from io import BytesIO

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

# タイトルに選択された食品カテゴリと食品名を記載
group_title = f"（{selected_group} - {selected_food}）" if selected_group != 'すべて' and selected_food != 'すべて' else \
              f"（{selected_group}）" if selected_group != 'すべて' else "（すべての食品カテゴリと食品名）"

# 細菌ごとの検体数の合計を表示
st.subheader(f'細菌ごとの検体数の合計{group_title}')
col1, col2 = st.columns(2)

with col1:
    bacteria_samplesize = df_filtered['細菌名'].value_counts().reset_index()
    bacteria_samplesize.columns = ['細菌名', '検体数の合計']
    st.dataframe(bacteria_samplesize)

with col2:
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.barh(bacteria_samplesize['細菌名'], bacteria_samplesize['検体数の合計'], color='skyblue')
    ax.set_xlabel('検体数の合計', fontsize=14)
    ax.set_ylabel('細菌名', fontsize=14)
    ax.set_title(f'細菌ごとの検体数{group_title}', fontsize=16)
    ax.grid(True)
    st.pyplot(fig)

st.write('-----------')

# すべての細菌の汚染濃度を表示
st.subheader(f'すべての細菌の汚染濃度{group_title}')
col3, col4 = st.columns(2)

with col3:
    df_bacteria_counts = df_filtered.copy()
    df_bacteria_counts = df_bacteria_counts.iloc[:, [0, 8, 9, 5, 6]]
    df_bacteria_counts.columns = ['調査年', '細菌名', '汚染濃度', '食品名', '食品詳細']
    st.dataframe(df_bacteria_counts)
    st.write("*現在報告書から取得した統計処理済みの文献値（最大値・最小値・平均値など）が混在しているためグラフは参考。今後データ収集を行い分布を可視化していく")

with col4:
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(df_filtered['汚染濃度'].astype(float), bins=range(int(df_filtered['汚染濃度'].astype(float).min()), int(df_filtered['汚染濃度'].astype(float).max()) + 2, 1), color='lightgreen', edgecolor='black')
    ax.set_xlim([0,10])
    ax.set_xlabel('汚染濃度 [log CFU/g]', fontsize=18)
    ax.set_ylabel('頻度', fontsize=18)
    ax.set_title(f'汚染濃度の分布{group_title}', fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=14)
    plt.grid(True)
    st.pyplot(fig)

# 特定の細菌のデータを取得
df_Campylobacter_counts = df_filtered[df_filtered['細菌名'].str.contains('Campylobacter')]
df_Listeria_counts = df_filtered[df_filtered['細菌名'].str.contains('Listeria')]
df_EHEC_counts = df_filtered[df_filtered['細菌名'].str.contains('Escherichia coli')]
df_Salmonella_counts = df_filtered[df_filtered['細菌名'].str.contains('Salmonella')]

# 各細菌のデータフレームとその行数をリストに格納
bacteria_data = [
    ('カンピロバクター', df_Campylobacter_counts),
    ('リステリア', df_Listeria_counts),
    ('腸管出血性大腸菌', df_EHEC_counts),
    ('サルモネラ', df_Salmonella_counts)
]

# 行数が多い順にソート
bacteria_data.sort(key=lambda x: len(x[1]), reverse=True)

# データ数が多い順に表示
for bacteria_name, df_bacteria in bacteria_data:
    if not df_bacteria.empty:
        st.write('-----------')
        st.subheader(f'{bacteria_name}の汚染濃度{group_title}')
        col5, col6 = st.columns(2)

        with col5:
            df_bacteria = df_bacteria.iloc[:, [0, 8, 9, 5, 6]]
            df_bacteria.columns = ['調査年', '細菌名', '汚染濃度', '食品名', '食品詳細']
            st.dataframe(df_bacteria)

        with col6:
            fig, ax = plt.subplots(figsize=(8, 6))
            ax.set_xlim([0,10])
            ax.hist(df_bacteria['汚染濃度'].astype(float), bins=range(int(df_bacteria['汚染濃度'].astype(float).min()), int(df_bacteria['汚染濃度'].astype(float).max()) + 2, 1), color='lightgreen', edgecolor='black')
            ax.set_xlabel('汚染濃度 [log CFU/g]', fontsize=18)
            ax.set_ylabel('頻度', fontsize=18)
            ax.set_title(f'{bacteria_name}の汚染濃度の分布{group_title}', fontsize=20)
            ax.tick_params(axis='both', which='major', labelsize=14)
            plt.grid(True)
            st.pyplot(fig)

# 選択された食品カテゴリと食品名に該当するデータを表示
st.write('-----------')
st.subheader('選択された食品カテゴリと食品名に該当するデータ （すべての食品カテゴリと食品名）')
st.dataframe(df_filtered)
