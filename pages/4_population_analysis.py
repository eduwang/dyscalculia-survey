# 4_population_analysis.py
import pandas as pd
import os
import streamlit as st

FILE_PATHS = {
    "초등학교": "data/2025년도_학교 현황(초)_충청남도교육청.csv",
    "중학교": "data/2025년도_학교 현황(중)_충청남도교육청.csv",
    "고등학교": "data/2025년도_학교 현황(고)_충청남도교육청.csv",
}

OUTPUT_CSV = "data/aggregated_population_by_region.csv"

def load_and_process_level(filepath: str, level_name: str) -> pd.DataFrame:
    df = pd.read_csv(filepath)

    # '충청남도' 제거
    df['지역'] = df['지역'].astype(str).str.replace(r'^충청남도\s*', '', regex=True).str.strip()

    # 학생수(계)에서 전체 학생수 추출 (콤마 제거 후 정규식)
    s = df['학생수(계)'].astype(str).str.replace(',', '', regex=False)
    extracted = s.str.extract(r'(\d+)\((\d+)\)')
    extracted = extracted.fillna(0).astype(int)
    df['학생수'] = extracted[0]  # 전체 학생수

    # 지역별 집계
    grouped = df.groupby('지역', dropna=False).agg(
        **{
            f'{level_name}_학교수': ('지역', 'size'),
            f'{level_name}_학생수': ('학생수', 'sum'),
        }
    ).reset_index()

    return grouped

def aggregate_data() -> pd.DataFrame:
    by_elem = load_and_process_level(FILE_PATHS["초등학교"], "초등")
    by_mid  = load_and_process_level(FILE_PATHS["중학교"], "중")
    by_high = load_and_process_level(FILE_PATHS["고등학교"], "고")

    merged = by_elem.merge(by_mid, on='지역', how='outer').merge(by_high, on='지역', how='outer')
    # 숫자형 채우기/변환
    for col in merged.columns:
        if col != '지역':
            merged[col] = merged[col].fillna(0).astype(int)

    merged = merged.sort_values('지역').reset_index(drop=True)

    # 합계 행 추가
    total_row = {'지역': '합계'}
    for col in merged.columns:
        if col != '지역':
            total_row[col] = merged[col].sum()
    merged = pd.concat([merged, pd.DataFrame([total_row])], ignore_index=True)

    # 열 순서 정리
    ordered_cols = [
        '지역',
        '초등_학교수', '중_학교수', '고_학교수',
        '초등_학생수', '중_학생수', '고_학생수',
    ]
    merged = merged[ordered_cols]

    return merged

def build_level_distribution(merged: pd.DataFrame, level_prefix: str) -> pd.DataFrame:
    """
    반환: [지역, 학교수, 학교수_비율, 학생수, 학생수_비율]
    ('합계' 행 제외, 비율은 0~1)
    """
    df_no_total = merged[merged['지역'] != '합계'].copy()

    school_col = f'{level_prefix}_학교수'
    stud_col   = f'{level_prefix}_학생수'

    total_schools = df_no_total[school_col].sum()
    total_students = df_no_total[stud_col].sum()

    out = df_no_total[['지역', school_col, stud_col]].rename(columns={
        school_col: '학교수',
        stud_col: '학생수'
    })

    out['학교수_비율'] = (out['학교수'] / total_schools).fillna(0)
    out['학생수_비율'] = (out['학생수'] / total_students).fillna(0)

    # 보기 좋게 정렬 (학생수, 학교수 내림차순)
    out = out.sort_values(['학생수', '학교수'], ascending=[False, False]).reset_index(drop=True)
    return out

def main():
    merged = aggregate_data()

    # CSV 저장
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    merged.to_csv(OUTPUT_CSV, index=False, encoding='utf-8-sig')

    # 콘솔 출력
    print("\n[지역별 학교/학생 집계표]")
    print(merged.to_string(index=False))
    print(f"\nCSV 저장 완료: {OUTPUT_CSV}")

    # Streamlit UI
    st.title("📊 지역별 학교/학생 수 집계 (충청남도)")
    st.markdown("초·중·고 학교 수와 학생 수를 지역별로 집계한 표입니다.")
    st.dataframe(merged)

    # 전체 집계 CSV 다운로드
    csv = merged.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 전체 집계 CSV 다운로드",
        data=csv,
        file_name="aggregated_population_by_region.csv",
        mime="text/csv",
    )

    st.markdown("---")

    # 초/중/고 탭으로 분리해 분포표 표시
    tabs = st.tabs(["초등학교 분포", "중학교 분포", "고등학교 분포"])
    for tab, (prefix, label) in zip(tabs, [("초등", "초등학교"), ("중", "중학교"), ("고", "고등학교")]):
        # (탭 루프 안) 표시/다운로드 부분 교체
        with tab:
            dist_df = build_level_distribution(merged, prefix)

            st.subheader(f"📍 {label} — 지역별 학교수·학생수 분포 (상대도수 포함)")

            # ✅ 비율은 숫자(float) 상태 유지 + 화면 표시만 퍼센트 포맷
            st.dataframe(
                dist_df,
                hide_index=True,
                column_config={
                    "학교수_비율": st.column_config.NumberColumn("학교수 비율", format="%.2f", help="전체 학교수 대비 비율"),
                    "학생수_비율": st.column_config.NumberColumn("학생수 비율", format="%.2f", help="전체 학생수 대비 비율"),
                    "학교수": st.column_config.NumberColumn("학교수", format="%d"),
                    "학생수": st.column_config.NumberColumn("학생수", format="%d"),
                },
                use_container_width=True,
            )

            # CSV 다운로드: 비율은 그대로 0~1 실수값
            download_csv = dist_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label=f"📥 {label} 분포표 CSV 다운로드",
                data=download_csv,
                file_name=f"{prefix}_distribution_by_region.csv",
                mime="text/csv",
            )


if __name__ == "__main__":
    main()
