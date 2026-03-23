import streamlit as st
import pandas as pd
import numpy as np
import os

# 1️⃣ 웹 페이지 탭 설정 (제목 변경)
st.set_page_config(page_title="2026 CORE 수강률 관리", layout="wide")

# 2️⃣ 대시보드 메인 제목 변경
st.markdown("<h1 style='text-align: center; color: #15397C;'>🦁 2026 CORE 수강률 관리 대시보드</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>모든 과목 수강률 90% 이상 달성을 목표로 합니다.</p>", unsafe_allow_html=True)
st.divider()

subjects = [
    "파이썬(최기환)", "파이썬(조상욱)", "화학(박경호)", 
    "물리학(손승우)", "미적분(김은상)", "통계(이우주)", "기하와벡터(김은상)"
]

tabs = st.tabs(subjects)

for i, subject in enumerate(subjects):
    with tabs[i]:
        st.subheader(f"📘 {subject} 대시보드")
        
        # 내부 저장용 파일 (가볍고 빠른 csv로 내부 관리)
        file_path = f"data_{subject}.csv"
        
        # 3️⃣ 파일 업로드 형식을 csv에서 xlsx로 변경
        uploaded_file = st.file_uploader(f"[{subject}] 최신 LMS 엑셀 파일(.xlsx) 업로드", type=['xlsx'], key=f"upload_{subject}")
        
        if uploaded_file is not None:
            try:
                # 4️⃣ 엑셀 파일을 읽어오도록 pd.read_excel 사용
                df_new = pd.read_excel(uploaded_file, header=3)
                df_new.to_csv(file_path, index=False) # 서버에는 처리하기 쉬운 csv로 저장
                st.success(f"✅ {subject} 데이터가 업데이트되었습니다! 이제 창을 닫아도 최신 상태가 유지됩니다.")
            except Exception as e:
                st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")

        # 아래는 기존 대시보드 출력 로직과 동일
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            
            if '출석' in df.columns:
                df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
                total_students = len(df)
                
                zero_students = df[df['출석'] == 0]
                zero_count = len(zero_students)
                zero_ratio = (zero_count / total_students) * 100 if total_students else 0
                
                total_lectures = 15
                target_ratio = 0.90
                threshold_attendance = int(np.ceil(total_lectures * target_ratio))
                
                achieved_students = df[df['출석'] >= threshold_attendance]
                achieved_count = len(achieved_students)
                achieved_ratio = (achieved_count / total_students) * 100 if total_students else 0
                
                avg_attendance_count = df['출석'].mean()
                avg_completion_ratio = (avg_attendance_count / total_lectures) * 100
                
                col1, col2, col3 = st.columns(3)
                col1.metric("현재 전체 평균 수강률", f"{avg_completion_ratio:.1f}%")
                col2.metric("목표(90%) 달성 학생", f"{achieved_ratio:.1f}%", f"{achieved_count}명 / {threshold_attendance}강 이상")
                col3.metric("아직 1강도 수강 안 한 학생", f"{zero_ratio:.1f}%", f"-{zero_count}명 / 위험", delta_color="inverse")
                
                st.divider()
                
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
            st.info("📂 자료가 없어요... 담당 멘토님이 데이터를 업로드해주세요!")
            col1, col2, col3 = st.columns(3)
            col1.metric("현재 전체 평균 수강률", "- %")
            col2.metric("목표(90%) 달성 학생", "- %", "- 명")
            col3.metric("아직 1강도 수강 안 한 학생", "- %", "- 명")
