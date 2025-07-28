import streamlit as st
import pandas as pd
import os
import re

st.title("🗣️ 연구 논의 및 질문 정리")

# 파일 경로
file_paths = {
    "초등학교": "data/2025년도_학교 현황(초)_충청남도교육청.csv",
    "중학교": "data/2025년도_학교 현황(중)_충청남도교육청.csv",
    "고등학교": "data/2025년도_학교 현황(고)_충청남도교육청.csv",
}

# 데이터 저장 딕셔너리
summaries = {}

# 각 파일 불러와서 요약
for label, path in file_paths.items():
    if os.path.exists(path):
        df = pd.read_csv(path)
        # 학생수(계) 분리
        df[['학생수', '특수학생수']] = df['학생수(계)'].str.extract(r'(\d+)\((\d+)\)').astype(int)
        total_schools = len(df)
        special_needs_schools = (df['특수학생수'] > 0).sum()
        average_students = round(df['학생수'].mean(), 1)

        summaries[label] = {
            "총 학교 수": total_schools,
            "특수학생 있는 학교 수": special_needs_schools,
            "평균 학생 수": average_students
        }
    else:
        summaries[label] = {
            "총 학교 수": "파일 없음",
            "특수학생 있는 학교 수": "-",
            "평균 학생 수": "-"
        }

# 요약 정보 표시
st.header("✅ 데이터 요약")

for label in ["초등학교", "중학교", "고등학교"]:
    st.subheader(f"📌 {label}")
    st.write(f"- 총 학교 수: **{summaries[label]['총 학교 수']}개** "
             f"(특수학생 포함 학교: **{summaries[label]['특수학생 있는 학교 수']}개**)")
    st.write(f"- 평균 학생 수: **{summaries[label]['평균 학생 수']}명**")


# 논의 질문 제시
st.header("📝 설문 및 표본 설계 관련 논의")

st.markdown("""
**1. 현재 예산으로 설문은 최대 몇 명까지 가능한가요?**  
- 인쇄 비용, 온라인 툴 라이선스, 연구자 수 등을 고려했을 때 실질적으로 가능한 학생 수는 몇 명인가요?

**2. 한 학교를 정할 경우 전교생을 대상으로 할 것인가요?**  
- 학년/학급 단위로 설문할 수도 있는데, 학교 측 협조가 가능한지 확인이 필요합니다.

**3. 무작위로 뽑는 기준이 정해져 있나요?**  
- 지역별 균형, 학교급 비율, 성별 등을 고려한 표본 추출 기준이 마련되어 있나요?
""")
