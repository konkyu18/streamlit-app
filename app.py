import streamlit as st
import pandas as pd
import plotly.express as px

# ページ設定
st.set_page_config(
    page_title="3都県 学生就業データ分析", 
    page_icon="📚",
    layout="wide"
)

st.title("📚 在学中の学生の就業状況")
st.markdown("""本アプリではe-Stat「就業状態等基本集計」のデータより、**在学中の学生**の就業状況を可視化します。  
**東京都・長野県・静岡県**の学生の就業状況を比較・分析します。""")

@st.cache_data
def load_data():
    df = pd.read_csv('b004.csv', encoding='utf-8', header=None)
    
    col_mapping = {
        1: '地域', 3: '男女', 5: '年齢', 7: '教育',
        8: '総数', 9: '有業者', 10: '無業者', 11: '求職者'
    }
    
    clean_df = df.iloc[9:].copy()
    clean_df = clean_df.rename(columns=col_mapping)
    clean_df = clean_df[col_mapping.values()]
   
    def to_int(x):
        try:
            return int(str(x).replace(',', '').replace('-', '0'))
        except:
            return 0

    num_cols = ['総数', '働いている人', '無業者', '求職者']
    for col in num_cols:
        clean_df[col] = clean_df[col].astype(str).apply(to_int)
#
    str_cols = ['地域', '男女', '年齢', '教育']
    for col in str_cols:
        clean_df[col] = clean_df[col].astype(str).apply(lambda x: x.split('_')[1] if '_' in x else x)

    return clean_df

try:
    df = load_data()
except Exception as e:
    st.error(f"データ読み込みエラー: {e}")
    st.stop()
#サイドバーの機能
st.sidebar.header("🔍 分析条件")
target_prefs = ['東京都', '長野県', '静岡県']

selected_pref = st.sidebar.selectbox("地域を選択", target_prefs, index=0)

genders = df[df['男女'] != '総数']['男女'].unique()
selected_gender = st.sidebar.radio("性別", ['総数'] + list(genders))

df_filtered = df[
    (df['地域'] == selected_pref) & 
    (df['男女'] == selected_gender) &
    (df['年齢'] == '総数')
]