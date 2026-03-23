import streamlit as st
import pandas as pd
import numpy as np
import os

# 웹 페이지 설정 (탭 이름과 넓은 화면)
st.set_page_config(page_title="한양대 ERICA | 기초과학 수강관리", layout="wide")

st.markdown("<h1 style='text-align: center; color: #15397C;'>🦁 기초과학 교과목 수강현황 관리포털</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>모든 과목 수강률 90% 이상 달성을 목표로 합니다.</p>", unsafe_allow_html=True)
st.divider()

# 말씀하신 7개 과목 리스트 (Power BI의 페이지 역할)
subjects = [
    "파이썬(최기환)", "파이썬(조상욱)", "화학(박경호)", 
    "물리학(손승우)", "미적분(김은상)", "통계(이우주)", "기하와벡터(김은상)"
]

# 상단에 탭(페이지) 생성
tabs = st.tabs(subjects)

# 각 탭(과목)별로 똑같은 대시보드 구조를 반복해서 생성
for i, subject in enumerate(subjects):
    with tabs[i]:
        st.subheader(f"📘 {subject} 대시보드")
        
        # 과목별로 데이터를 따로 저장할 파일 이름 지정
        file_path = f"data_{subject}.csv"
        
        # 파일 업로드 (해당 과목의 멘토가 최신화할 때 사용)
        uploaded_file = st.file_uploader(f"[{subject}] 최신 LMS 파일 업로드 (업데이트용)", type=['csv'], key=f"upload_{subject}")
        
        # 누군가 파일을 올렸다면? -> 서버에 저장해서 계속 기억하게 만듦
        if uploaded_file is not None:
            try:
                df_new = pd.read_csv(uploaded_file, header=3)
                df_new.to_csv(file_path, index=False) # 파일을 서버에 저장
                st.success(f"✅ {subject} 데이터가 업데이트되었습니다! 이제 창을 닫아도 최신 상태가 유지됩니다.")
            except Exception as e:
                st.error("파일 양식이 맞지 않습니다. 올바른 LMS 출결 파일을 올려주세요.")

        # 저장된 데이터가 있는지 확인하고 대시보드 그리기
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            
            if '출석' in df.columns:
                df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
                total_students = len(df)
                
                # 지표 계산
                zero_students = df[df['출석'] == 0]
                zero_count = len(zero_students)
                zero_ratio = (zero_count / total_students) * 100 if total_students else 0
                
                total_lectures = 15 # 총 강의 수 고정
                target_ratio = 0.90 # 목표 90% 고정
                threshold_attendance = int(np.ceil(total_lectures * target_ratio))
                
                achieved_students = df[df['출석'] >= threshold_attendance]
                achieved_count = len(achieved_students)
                achieved_ratio = (achieved_count / total_students) * 100 if total_students else 0
                
                avg_attendance_count = df['출석'].mean()
                avg_completion_ratio = (avg_attendance_count / total_lectures) * 100
                
                # KPI 카드 출력
                col1, col2, col3 = st.columns(3)
                col1.metric("현재 전체 평균 수강률", f"{avg_completion_ratio:.1f}%")
                col2.metric("목표(90%) 달성 학생", f"{achieved_ratio:.1f}%", f"{achieved_count}명 / {threshold_attendance}강 이상")
                col3.metric("아직 1강도 수강 안 한 학생", f"{zero_ratio:.1f}%", f"-{zero_count}명 / 위험", delta_color="inverse")
                
                st.divider()
                
                # 명단 출력
                display_cols = ['순번', '이름', '학번', '학과', '출석', '결석']
                existing_cols = [col for col in display_cols if col in df.columns]
                
                tab_zero, tab_under = st.tabs(["🆘 0강 수강 (즉시 연락)", "⚠️ 90% 미달성"])
                with tab_zero:
                    if zero_count > 0:
                        st.dataframe(zero_students[existing_cols].reset_index(drop=True), use_container_width=True)
                    else:
                        st.success("대단합니다! 모든 학생이 수강을 시작했습니다.")
                with tab_under:
                    under_target_students = df[(df['출석'] > 0) & (df['출석'] < threshold_attendance)]
                    if len(under_target_students) > 0:
                        styled_df = under_target_students[existing_cols].reset_index(drop=True).style.background_gradient(cmap='YlOrRd', subset=['출석'])
                        st.dataframe(styled_df, use_container_width=True)
                    else:
                        st.success("🎉 해당하는 모든 학생이 목표 수강률을 달성했습니다!")
            else:
                st.error("데이터 오류: 업로드된 파일에 '출석' 열이 없습니다.")
                
        else:
            # 📌 누군가 자료를 넣지 않았을 때 뜨는 화면 (대시보드 형태는 유지)
            st.info("📂 자료가 없어요... 담당 멘토님이 데이터를 업로드해주세요!")
            
            # 빈 KPI 카드 출력 (숫자 대신 '-' 표시)
            col1, col2, col3 = st.columns(3)
            col1.metric("현재 전체 평균 수강률", "- %")
            col2.metric("목표(90%) 달성 학생", "- %", "- 명")
            col3.metric("아직 1강도 수강 안 한 학생", "- %", "- 명")
