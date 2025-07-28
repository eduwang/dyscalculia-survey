import streamlit as st
import pandas as pd
import os
import random

st.title("🎯 무작위 표본 추출기 (초/중/고등학교)")

# 📁 파일 경로
file_paths = {
    "초등학교": "data/2025년도_학교 현황(초)_충청남도교육청.csv",
    "중학교": "data/2025년도_학교 현황(중)_충청남도교육청.csv",
    "고등학교": "data/2025년도_학교 현황(고)_충청남도교육청.csv",
}

@st.cache_data
def load_and_preprocess(filepath):
    df = pd.read_csv(filepath)
    df[['학생수', '특수학생수']] = df['학생수(계)'].str.extract(r'(\d+)\((\d+)\)').astype(int)
    df['학급수'] = df['학급수(계)'].str.extract(r'(\d+)').astype(int)
    df['학교급'] = os.path.basename(filepath).split('(')[1].split(')')[0]
    return df

# 📊 필터 슬라이더
min_students = st.slider("학생 수 최소 기준", min_value=0, max_value=500, step=20, value=100)
include_special = st.checkbox("특수학생이 있는 학교만 포함", value=False)
sample_percent = st.slider("표본 비율 (%)", min_value=5, max_value=30, step=1, value=10)

# ✅ 필터 적용 후 데이터 저장
filtered_data = {}
total_eligible = {}

for label, path in file_paths.items():
    if os.path.exists(path):
        df = load_and_preprocess(path)
        condition = df['학생수'] >= min_students
        if include_special:
            condition &= (df['특수학생수'] > 0)
        df_filtered = df[condition].copy()
        filtered_data[label] = df_filtered
        total_eligible[label] = len(df_filtered)

# 📈 필터 결과 요약
st.subheader("📋 필터 조건에 따른 대상 학교 수")
for level in ["초등학교", "중학교", "고등학교"]:
    st.write(f"- {level}: {total_eligible.get(level, 0)}개")

# 🎯 표본 추출
if st.button("표본 추출하기"):
    st.subheader("🎓 추출된 학교 목록")
    sampled_total = pd.DataFrame()

    for level, df in filtered_data.items():
        n_sample = max(1, round(len(df) * (sample_percent / 100))) if len(df) > 0 else 0
        df_sampled = df.sample(n=n_sample, random_state=42) if n_sample > 0 else pd.DataFrame()
        sampled_total = pd.concat([sampled_total, df_sampled], ignore_index=True)

    if sampled_total.empty:
        st.warning("조건을 만족하는 표본이 없습니다.")
    else:
        sampled_total_view = sampled_total[[
            '학교급', '학교명', '설립구분', '학생수', '특수학생수', '학급당학생수'
        ]]
        st.dataframe(sampled_total_view)

        # 📥 CSV 다운로드
        csv = sampled_total_view.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 CSV로 다운로드",
            data=csv,
            file_name='표본추출_학교목록.csv',
            mime='text/csv'
        )
