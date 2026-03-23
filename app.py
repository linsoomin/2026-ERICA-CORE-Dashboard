import streamlit as st
import pandas as pd
import numpy as np

# 웹 페이지 설정 (제목, 와이드 모드)
st.set_page_config(page_title="한양대 ERICA | CORE 수강관리포털", layout="wide")

# 로고 대신 깔끔한 제목
st.markdown("<h1 style='text-align: center; color: #15397C;'>🦁 CORE 과목 수강현황 관리포털 </h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>모든 학생의 수강률 90% 이상 달성을 목표로 합니다.</p>", unsafe_allow_html=True)
st.divider()

# --- 사이드바 설정 (설정 값 조정 공간) ---
with st.sidebar:
    st.header("⚙️ 대시보드 설정")
    st.write("과목별로 정보를 설정해 주세요.")
    
    # 총 강의 수 설정 (기본값 15강)
    total_lectures = st.number_input("해당 과목의 총 강의 수", min_value=1, value=15)
    
    # 우리 팀의 목표 수강률 (기본값 90%)
    target_ratio_input = st.slider("궁극적인 목표 수강률 (%)", min_value=10, max_value=100, value=90)
    target_ratio = target_ratio_input / 100

st.write("### ✅ 수강 현황 데이터를 업로드해 주세요")
uploaded_file = st.file_uploader("", type=['csv'])

if uploaded_file is not None:
    try:
        # 데이터 로드 및 전처리 (4번째 줄 헤더)
        df = pd.read_csv(uploaded_file, header=3)
        
        if '출석' in df.columns:
            total_students = len(df)
            
            # --- 필수 KPI 데이터 계산 ---
            
            # 1. 1강도 수강하지 않은 학생 (출석 0)
            zero_students = df[df['출석'] == 0]
            zero_count = len(zero_students)
            zero_ratio = (zero_count / total_students) * 100
            
            # 2. 우리 목표(90% 이상)를 달성한 학생
            threshold_attendance = int(np.ceil(total_lectures * target_ratio)) # 예: 15강의 90% = 13.5 -> 14강 이상
            achieved_students = df[df['출석'] >= threshold_attendance]
            achieved_count = len(achieved_students)
            achieved_ratio = (achieved_count / total_students) * 100
            
            # 3. 평균 수강률
            avg_attendance_count = df['출석'].mean()
            avg_completion_ratio = (avg_attendance_count / total_lectures) * 100
            
            # --- KPI 대시보드 시각화 ---
            
            # Streamlit의 metric을 사용하여 세련된 카드 UI 구성
            st.divider()
            st.subheader(f"📊 실시간 주요 지표 (총 {total_students}명)")
            
            col1, col2, col3, col4 = st.columns(4)
            
            # 전체 평균 수강률
            col1.metric(label="현재 전체 평균 수강률", value=f"{avg_completion_ratio:.1f}%")
            
            # 목표 달성 학생 비율 (초록색 화살표)
            col2.metric(
                label=f"목표 수강률({target_ratio_input}%) 달성 학생", 
                value=f"{achieved_ratio:.1f}%",
                delta=f"{achieved_count}명 / {threshold_attendance}강 이상"
            )
            
            # 미수강 학생 (빨간색 화살표)
            col3.metric(
                label="아직 1강도 수강 안 한 학생", 
                value=f"{zero_ratio:.1f}%",
                delta=f"-{zero_count}명 / 위험",
                delta_color="inverse"
            )
            
            # 목표 달성까지 필요한 추가 수강생 수
            st.warning(f"💡 현재 목표 달성률은 {achieved_ratio:.1f}%입니다. 모든 학생 수강률 90% 이상을 위해 멘토링이 필요합니다.")
            
            st.divider()
            
            # --- 멘토를 위한 행동 가이드 및 명단 시각화 ---
            
            st.subheader("📋 멘토링 집중 관리 명단")
            
            # 탭 구성 (위험군, 전체 명단)
            tab1, tab2 = st.tabs(["🆘 즉시 연락 필요 학생 (0강 수강)", "⚠️ 수강률 90% 미만 미달성군"])
            
            # 주요 표시 컬럼
            display_cols = ['순번', '이름', '학번', '학과', 'e-mail', '출석', '결석']
            
            with tab1:
                st.write(f"아직 한 강의도 수강하지 않은 학생 **{zero_count}명**입니다. 즉시 연락하여 독려해 주세요.")
                if zero_count > 0:
                    st.dataframe(zero_students[display_cols].reset_index(drop=True), use_container_width=True)
                else:
                    st.success("대단합니다! 모든 학생이 수강을 시작했습니다.")
                    
            with tab2:
                # 90% 미만 학생 필터링
                under_target_students = df[(df['출석'] > 0) & (df['출석'] < threshold_attendance)]
                under_count = len(under_target_students)
                st.write(f"수강은 시작했으나 목표 수강률({target_ratio_input}%)에 도달하지 못한 학생 **{under_count}명**입니다. 밀착 관리가 필요합니다.")
                
                # 표에 색상 추가 (스타일링) - pandas styler 사용
                if under_count > 0:
                    styled_df = under_target_students[display_cols].reset_index(drop=True).style.background_gradient(cmap='YlOrRd', subset=['출석'])
                    st.dataframe(styled_df, use_container_width=True)
                else:
                    st.success("🎉 환상적입니다! 조건에 해당하는 모든 학생이 목표 수강률을 달성했습니다!")

        else:
            st.error("파일 양식이 맞지 않습니다. 올바른 LMS 출결 파일을 올려주세요.")
            
    except Exception as e:
        st.error(f"파일을 처리하는 중 오류가 발생했습니다: {e}")
