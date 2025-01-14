import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# ページの設定
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# CSVファイルのURL
csv_url = "https://raw.githubusercontent.com/kento-koyama/food_micro_data_risk/main/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E7%8E%87.csv"

# フォントファイルのパスを設定
font_path = 'NotoSansCJKjp-Regular.otf'

# Streamlit のアプリケーション
st.title('食中毒細菌の陽性率の統計値')
st.write("[食中毒細菌汚染実態_汚染率.csv](%s)の可視化です。" % csv_url)
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

# 必要なカラムの欠損値を削除
df = df[df['検体数'].notna() & df['陽性数'].notna()]

# 細菌名を"Campylobacter spp."でまとめる
df['細菌名_詳細'] = df['細菌名']
df['細菌名'] = df['細菌名'].apply(lambda x: 'Campylobacter spp.' if 'Campylobacter' in str(x) else x)

# 初期状態の選択肢
food_groups = [""] + ["すべて"] + list(df['食品カテゴリ'].unique())
food_names = [""] + ["すべて"] + list(df['食品名'].unique())
bacteria_names = [""] + ["すべて"] + list(df['細菌名'].unique())
institutions = [""] + ["すべて"] + list(df['実施機関'].unique())

# サイドバーで各項目を選択
selected_group = st.sidebar.selectbox('食品カテゴリを入力 または 選択してください:', food_groups, key="group_selected")
selected_food = st.sidebar.selectbox('食品名を入力 または 選択してください:', food_names, key="food_selected")
selected_bacteria = st.sidebar.selectbox('細菌名を入力 または 選択してください:', bacteria_names, key="bacteria_selected")
selected_institution = st.sidebar.selectbox('実施機関を入力 または 選択してください:', institutions, key="institution_selected")

# フィルタリング処理
if selected_group and selected_group != "すべて":
    df = df[df['食品カテゴリ'] == selected_group]

if selected_food and selected_food != "すべて":
    df = df[df['食品名'] == selected_food]

if selected_bacteria and selected_bacteria != "すべて":
    df = df[df['細菌名'] == selected_bacteria]

if selected_institution and selected_institution != "すべて":
    df = df[df['実施機関'] == selected_institution]

# フィルタリング結果のタイトル作成
group_title = f"（{selected_group or 'すべて'} - {selected_food or 'すべて'} - {selected_bacteria or 'すべて'} - {selected_institution or 'すべて'}）"

# 結果を表示
if df.empty:
    st.warning("該当するデータがありません。条件を変更してください。")
else:
    st.write(f'選択された条件に該当するデータ {group_title}')
    st.dataframe(df, hide_index=True)

    st.write('-----------')

    # 細菌ごとの検体数と陽性数の合計
    bacteria_counts = df.groupby('細菌名').agg({'検体数': 'sum', '陽性数': 'sum'}).reset_index()
    bacteria_counts.columns = ['バクテリア名', '検体数', '陽性数']
    bacteria_counts['陽性率 (%)'] = (bacteria_counts['陽性数'] / bacteria_counts['検体数']) * 100

    # 表示
    col1, col2 = st.columns(2)

    with col1:
        st.write(f'細菌別の検体数 {group_title}')
        st.dataframe(bacteria_counts[['バクテリア名', '検体数']], hide_index=True)

    with col2:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.barh(bacteria_counts['バクテリア名'], bacteria_counts['検体数'], color='skyblue')
        ax.set_xlabel('検体数')
        ax.set_ylabel('細菌名')
        ax.set_title('細菌別の検体数')
        st.pyplot(fig)

    st.write('-----------')

    col3, col4 = st.columns(2)

    with col3:
        st.write(f'細菌別の陽性率 {group_title}')
        st.dataframe(bacteria_counts[['バクテリア名', '陽性率 (%)']], hide_index=True)

    with col4:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.barh(bacteria_counts['バクテリア名'], bacteria_counts['陽性率 (%)'], color='skyblue')
        ax.set_xlabel('陽性率 (%)')
        ax.set_ylabel('細菌名')
        ax.set_title('細菌別の陽性率')
        st.pyplot(fig)
