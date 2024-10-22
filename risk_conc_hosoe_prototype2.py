import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ページの設定
st.set_page_config(layout="wide", initial_sidebar_state="expanded")

# 翻訳リストをCSVから読み込む
csv_url_trans = 'https://raw.githubusercontent.com/junpei05/FoodContamiRisk_AppTest/main/trans_dict.csv'
translation_df = pd.read_csv(csv_url_trans, encoding='shift-jis')  # リストのCSVファイルをロード
translation_dict = dict(zip(translation_df['日本語'], translation_df['English']))  # 辞書に変換

# 言語選択オプションをサイドバーに追加
lang_option = st.sidebar.radio("言語を選択してください (Choose Language):", ('日本語', 'English'))

# 翻訳関数を定義（必要な部分のみ翻訳）
def translate(text, lang_option):
    if lang_option == 'English':
        return translation_dict.get(text, text)  # 英語が存在する場合は変換、無ければそのまま
    else:
        return text  # 日本語の場合はそのまま表示

# 表示用のデータフレームを翻訳する関数（英語のみ翻訳）
def translate_dataframe_for_display(df, lang_option):
    if lang_option == 'English':
        translated_df = df.copy()  # 元のdfはそのまま残しておく
        # 列名の翻訳
        translated_df.columns = [translate(col, lang_option) for col in df.columns]
        # 各セルの翻訳（必要なら）
        for col in translated_df.columns:
            translated_df[col] = translated_df[col].apply(lambda x: translate(x, lang_option) if x in translation_dict else x)
        return translated_df
    else:
        return df  # 日本語の場合は翻訳せずにそのまま返す

# CSVファイルのパス（適宜変更してください）
csv_url = "https://raw.githubusercontent.com/kento-koyama/food_micro_data_risk/main/%E9%A3%9F%E4%B8%AD%E6%AF%92%E7%B4%B0%E8%8F%8C%E6%B1%9A%E6%9F%93%E5%AE%9F%E6%85%8B_%E6%B1%9A%E6%9F%93%E6%BF%83%E5%BA%A6.csv"

# データの読み込み（操作は日本語のまま）
df = pd.read_csv(csv_url, encoding='utf-8-sig')

# サイドバーに選択オプションを追加
st.sidebar.header(translate('フィルターオプション', lang_option))
selected_group = st.sidebar.selectbox(translate('食品カテゴリを選択してください:', lang_option), 
                                      ['すべて'] + list(df['食品カテゴリ'].unique()))

# 選択された食品カテゴリに基づいて食品名を動的に変更
if selected_group != 'すべて':
    df_filtered = df[df['食品カテゴリ'] == selected_group]
else:
    df_filtered = df

selected_food = st.sidebar.selectbox(translate('食品名を選択してください:', lang_option), 
                                     ['すべて'] + list(df_filtered['食品名'].unique()))

# タイトルに選択された食品カテゴリと食品名を記載
group_title = f"（{selected_group} - {selected_food}）" if selected_group != 'すべて' and selected_food != 'すべて' else \
              f"（{selected_food}）" if selected_group == 'すべて' and selected_food != 'すべて' else \
              f"（{selected_group}）" if selected_group != 'すべて' else translate("（すべての食品カテゴリと食品名）", lang_option)

# タイトルを表示
st.title(translate('食中毒細菌の汚染濃度の統計値', lang_option))
st.subheader(f'{translate("細菌ごとの検体数", lang_option)} {group_title}')

# '不検出' や '-' のデータを除外し、float型に変換
df_filtered_clean = df_filtered[df_filtered['汚染濃度'].apply(lambda x: x not in ['不検出', '-', np.nan])]
df_filtered_clean['汚染濃度'] = pd.to_numeric(df_filtered_clean['汚染濃度'], errors='coerce')

# 汚染濃度の分布を表示
st.subheader(f'{translate("すべての細菌の汚染濃度", lang_option)} {group_title}')
col3, col4 = st.columns(2)

with col3:
    df_bacteria_counts = df_filtered_clean[['調査年', '細菌名', '汚染濃度', '食品名', '食品詳細']]
    translated_df_bacteria_counts = translate_dataframe_for_display(df_bacteria_counts, lang_option)
    st.dataframe(translated_df_bacteria_counts)

with col4:
    # 最小値と最大値が適切か確認する
    min_val = df_filtered_clean['汚染濃度'].min()
    max_val = df_filtered_clean['汚染濃度'].max()

    # 最小値と最大値が正常に取れているか確認
    if pd.notna(min_val) and pd.notna(max_val) and min_val != max_val:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.hist(df_filtered_clean['汚染濃度'].dropna(), 
                bins=range(int(min_val), int(max_val) + 2, 1), 
                color='lightgreen', edgecolor='black')
        ax.set_xlim([0,10])
        ax.set_xlabel(translate('汚染濃度 [log CFU/g]', lang_option))
        ax.set_ylabel(translate('頻度', lang_option))
        ax.set_title(translate('汚染濃度の分布', lang_option))
        st.pyplot(fig)
    else:
        st.write(translate("適切な汚染濃度データがありません。", lang_option))

# 選択された食品カテゴリと食品名に該当するデータを表示
st.subheader(f'{translate("選択された食品カテゴリと食品名に該当するデータ", lang_option)} {group_title}')
translated_df_filtered_clean = translate_dataframe_for_display(df_filtered_clean, lang_option)
st.dataframe(translated_df_filtered_clean)
