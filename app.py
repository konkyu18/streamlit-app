import streamlit as st
import pandas as pd
import plotly.express as px

#UI1 ページ設定
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

    num_cols = ['総数', '有業者', '無業者', '求職者']
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
st.sidebar.header("条件指定")
target_prefs = ['東京都', '長野県', '静岡県']

selected_pref = st.sidebar.selectbox("地域を選択", target_prefs, index=0)

genders = df[df['男女'] != '総数']['男女'].unique()
selected_gender = st.sidebar.radio("性別", ['総数'] + list(genders))

df_filtered = df[
    (df['地域'] == selected_pref) & 
    (df['男女'] == selected_gender) &
    (df['年齢'] == '総数')
]

df_student_total = df_filtered[df_filtered['教育'] == '在学者']

if df_student_total.empty:
    st.warning("データが見つかりません")
    st.stop()

total_students = df_student_total['総数'].values[0]
working_students = df_student_total['有業者'].values[0]
job_seeking_students = df_student_total['求職者'].values[0]
work_rate = (working_students / total_students * 100) if total_students > 0 else 0

st.markdown(f"### 📈 {selected_pref}の学生データ ハイライト")
col1, col2, col3 = st.columns(3)
#UI2 メトリクス
col1.metric("在学者数 (15歳以上)", f"{total_students:,}人")
col2.metric("働く学生数 (有業者)", f"{working_students:,}人", f"有業率 {work_rate:.1f}%")
col3.metric("就活・求職中の学生", f"{job_seeking_students:,}人")

st.caption(f"学生の有業率: {work_rate:.1f}%")
st.progress(min(int(work_rate), 100))

st.divider()

tab1, tab2, tab3 = st.tabs([" 学校別内訳", " 3都県を比較", "データダウンロード"])

with tab1:
    st.subheader(f"{selected_pref} の学校種別 就業状況")
     #抽出   
    df_schools = df_filtered[
        df_filtered['教育'].str.contains('（在学者）')
    ].copy()
    
    if not df_schools.empty:
        df_schools['学校種別'] = df_schools['教育'].apply(lambda x: x.replace('（在学者）', ''))
        df_schools['有業率'] = df_schools.apply(lambda row: (row['有業者'] / row['総数'] * 100) if row['総数'] > 0 else 0, axis=1)
        
        fig_school = px.bar(
            df_schools, 
            x='学校種別', 
            y='有業率', 
            color='学校種別',
            title='学校種別ごとの有業率（％）',
            text_auto='.1f'
        )
        fig_school.update_layout(showlegend=False)
        st.plotly_chart(fig_school, use_container_width=True)

with tab2:
    st.subheader("東京都・長野県・静岡県の比較")
    
    compare_school = st.selectbox(
        "比較する学校種別", 
        ["在学者", "大学（在学者）", "高校（在学者）"],
        index=0
    )
#比較
    df_compare = df[
        (df['地域'].isin(target_prefs)) &   # ここで3つに絞る
        (df['男女'] == '総数') & 
        (df['年齢'] == '総数') & 
        (df['教育'] == compare_school)
    ].copy()
    
    df_compare['有業率'] = df_compare.apply(lambda row: (row['有業者'] / row['総数'] * 100) if row['総数'] > 0 else 0, axis=1)
    