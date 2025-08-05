import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px  # 📌 plotly 추가
import os

st.title("🧪 학교급별 탐색적 분석 (초/중/고)")

# 파일 경로
file_paths = {
    "초등학교": "data/2025년도_학교 현황(초)_충청남도교육청.csv",
    "중학교": "data/2025년도_학교 현황(중)_충청남도교육청.csv",
    "고등학교": "data/2025년도_학교 현황(고)_충청남도교육청.csv",
}

def load_and_process_data(filepath):
    df = pd.read_csv(filepath)

    # 학생수(계) 분리 → 전체, 특수학생
    df[['학생수', '특수학생수']] = df['학생수(계)'].str.extract(r'(\d+)\((\d+)\)').astype(int)

    # 학급수(계) 괄호 제거
    df['학급수'] = df['학급수(계)'].str.extract(r'(\d+)').astype(int)

    # 필요한 열만 선택
    columns = ['지역', '학교명', '설립구분', '학급수', '학생수', '특수학생수', '학급당학생수']
    df = df[columns]

    return df

# 선택 박스에서 학교급 선택
school_level = st.selectbox("학교급 선택", list(file_paths.keys()))
file_path = file_paths[school_level]

# 데이터 불러오기 및 전처리
if os.path.exists(file_path):
    df_result = load_and_process_data(file_path)
    st.subheader(f"📋 {school_level} 데이터 요약")
    st.dataframe(df_result)
    st.markdown(f"총 {len(df_result)}개 학교 표시됨")

    # 📊 히스토그램 1: 학생 수 구간별 학교 수 (Plotly)
    st.subheader("🎓 학생 수 구간별 학교 수")
    fig1 = px.histogram(
        df_result,
        x="학생수",
        nbins=40,
        labels={"학생수": "학생 수"},
        title="학생 수 히스토그램",
    )
    fig1.update_layout(bargap=0.1)
    st.plotly_chart(fig1, use_container_width=True)

    # 📊 히스토그램 2: 학급당 학생 수 (Plotly)
    st.subheader("📐 학급당 학생 수 분포")
    fig2 = px.histogram(
        df_result,
        x="학급당학생수",
        nbins=20,
        labels={"학급당학생수": "학급당 학생 수"},
        title="학급당 학생 수 히스토그램",
    )
    fig2.update_layout(bargap=0.1)
    st.plotly_chart(fig2, use_container_width=True)


    # 📊 히스토그램 3: 지역별 학교 수 분포 (Plotly)
    st.subheader("🏫 지역별 학교 수 분포")
    # 지역별 학교 개수를 집계
    region_counts = df_result['지역'].value_counts().reset_index()
    region_counts.columns = ['지역', '학교수']

    fig3 = px.bar(
        region_counts,
        x="지역",
        y="학교수",
        labels={"학교수": "학교 수", "지역": "지역"},
        title="지역별 학교 수 분포",
        text="학교수",  # 막대 위에 숫자 표시
    )
    fig3.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig3, use_container_width=True)


else:
    st.error(f"{file_path} 파일을 찾을 수 없습니다.")
