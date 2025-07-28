import streamlit as st
import pandas as pd
import os

# 파일 리스트
file_paths = {
    "초등학교": "data/2025년도_학교 현황(초)_충청남도교육청.csv",
    "중학교": "data/2025년도_학교 현황(중)_충청남도교육청.csv",
    "고등학교": "data/2025년도_학교 현황(고)_충청남도교육청.csv",
    "특수학교": "data/2025년도_학교 현황(특)_충청남도교육청.csv",
    "각종학교": "data/2025년도_학교 현황(각)_충청남도교육청.csv",
    "기타학교": "data/2025년도_학교 현황(그)_충청남도교육청.csv",
}

st.title("📊 2025년도 충청남도교육청 학교 현황 조회")

# 사이드바에서 학교급 선택
selected_school_level = st.sidebar.selectbox("학교급 선택", list(file_paths.keys()))

# 해당 CSV 파일 불러오기
file_path = file_paths[selected_school_level]

if os.path.exists(file_path):
    df = pd.read_csv(file_path)
    total_rows = len(df)

    # ✅ 데이터 수 포함하여 제목 출력
    st.subheader(f"{selected_school_level} 데이터 미리보기 ({total_rows}건)")
    st.dataframe(df)
else:
    st.warning(f"{file_path} 파일을 찾을 수 없습니다.")

