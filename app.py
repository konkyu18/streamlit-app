import streamlit as st
import pandas as pd
import plotly.express as px

# ページ設定
st.set_page_config(
    page_title="学生就業データ分析", 
    page_icon="📚",
    layout="wide"
)

st.title("📚 在学中の学生の就業状況")
st.markdown("""本アプリではe-Stat「就業状態等基本集計」のデータより、**在学中の学生**の就業状況を可視化します。  
学校種別による違いや、地域ごとの学生の働く割合を分析できます。""")

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