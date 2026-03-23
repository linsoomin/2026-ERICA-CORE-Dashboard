import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime

# --- 1️⃣ 웹 페이지 설정 및 한양대 테마 컬러 CSS 적용 ---
st.set_page_config(page_title="2026 CORE 수강률 관리", layout="wide")

HYU_BLUE = "#15397C" # 한양대학교 ERICA 메인 블루 컬러

st.markdown(f"""
<style>
    /* 탭(메뉴) 글씨 크기 및 여백 설정 */
    .stTabs [data-baseweb="tab"] {{
        font-size: 16px;
        font-weight: bold;
        padding-top: 15px;
        padding-bottom: 15px;
    }}
    /* 클릭되어 선택된 탭의 색상 (한양대 블루) */
    .stTabs [aria-selected="true"] {{
        color: {HYU_BLUE} !important;
        border-bottom: 3px solid {HYU_BLUE} !important;
    }}
    /* 마우스 올렸을 때(호버) 색상 변경 */
    .stTabs [data-baseweb="tab"]:hover {{
        color: {HYU_BLUE} !important;
    }}
</style>
""", unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align: center; color: {HYU_BLUE}; font-weight: 900;'>🦁 2026 CORE 수강률 관리 대시보드</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>모든 과목 수강률 90% 이상 달성을 목표로 합니다.</p>", unsafe_allow_html=True)
st.divider()

subjects = [
    "파이썬(최기환)", "파이썬(조상욱)", "화학(박경호)", 
    "물리학(손승우)", "미적분(김은상)", "통계(이우주)", "기하와벡터(김은상)"
]

def style_attendance(s, threshold_2_3):
    colors = []
    for val in s:
        if val == 0:
            colors.append('background-color: #FFCDD2; color: #900C3F; font-weight: bold;') 
        elif val >= threshold_2_3:
            colors.append('background-color: #4CAF50; color: white; font-weight: bold;') 
        else:
            colors.append('background-color: #C8E6C9; color: #1E8449; font-weight: bold;') 
    return colors

tabs = st.tabs(["🏆 종합 랭킹"] + subjects)

# --- 2️⃣ 종합 랭킹 메인 페이지 ---
with tabs[0]:
    st.subheader("🏆 전체 과목 수강률 종합 랭킹")
    # 📌 호칭 수정
    st.write("각 과목 어시스턴트 및 멘토님들이 데이터를 업로드하면 실시간으로 랭킹이 변동됩니다.")
    
    ranking_data = []
    for subj in subjects:
        file_path = f"data_{subj}.csv"
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                if '출석' in df.columns:
                    df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
                    total = len(df)
                    if total > 0:
                        avg_comp = (df['출석'].mean() / 15) * 100
                        zero_r = (len(df[df['출석'] == 0]) / total) * 100
                        ranking_data.append({'과목': subj, '평균수강률': avg_comp, '미수강비율': zero_r})
            except:
                pass

    st.divider()
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"<h3 style='color: {HYU_BLUE};'>📈 전체 평균 수강률 랭킹 (이수율 순)</h3>", unsafe_allow_html=True)
        sorted_by_comp = sorted(ranking_data, key=lambda x: x['평균수강률'], reverse=True)
        for i in range(len(subjects)):
            if i < len(sorted_by_comp):
                item = sorted_by_comp[i]
                if i == 0:
                    st.success(f"**{i+1}위** | 🥇 {item['과목']} ({item['평균수강률']:.1f}%)")
                else:
                    st.info(f"**{i+1}위** | {item['과목']} ({item['평균수강률']:.1f}%)")
            else:
                st.markdown(f"<div style='padding: 12px; border: 2px dashed #ccc; border-radius: 8px; color: #888; margin-bottom: 12px; background-color: #fafafa;'><b>{i+1}위</b> | ⬜ 아직 자료가 없어요</div>", unsafe_allow_html=True)
                
    with col2:
        st.markdown(f"<h3 style='color: {HYU_BLUE};'>🚨 위험도 랭킹 (미수강 학생 비율 순)</h3>", unsafe_allow_html=True)
        sorted_by_zero = sorted(ranking_data, key=lambda x: x['미수강비율'], reverse=True)
        for i in range(len(subjects)):
            if i < len(sorted_by_zero):
                item = sorted_by_zero[i]
                if i == 0:
                    st.error(f"**{i+1}위** | 💥 {item['과목']} ({item['미수강비율']:.1f}%) - 밀착 관리 필요!")
                else:
                    st.warning(f"**{i+1}위** | {item['과목']} ({item['미수강비율']:.1f}%)")
            else:
                st.markdown(f"<div style='padding: 12px; border: 2px dashed #ccc; border-radius: 8px; color: #888; margin-bottom: 12px; background-color: #fafafa;'><b>{i+1}위</b> | ⬜ 아직 자료가 없어요</div>", unsafe_allow_html=True)

# --- 3️⃣ 개별 과목 대시보드 ---
for i, subject in enumerate(subjects):
    with tabs[i+1]:
        st.subheader(f"📘 {subject} 대시보드")
        
        file_path = f"data_{subject}.csv"
        date_path = f"date_{subject}.txt"
        
        uploaded_file = st.file_uploader(f"[{subject}] 최신 LMS 엑셀 파일(.xlsx) 업로드", type=['xlsx'], key=f"upload_{subject}")
        
        if uploaded_file is not None:
            try:
                uploaded_file.seek(0)
                date_df = pd.read_excel(uploaded_file, header=None, nrows=1)
                update_str = str(date_df.iloc[0, 0])
                
                if "최종" not in update_str:
                    now = datetime.datetime.now()
                    update_str = f"업데이트 기준: {now.strftime('%Y-%m-%d %H:%M:%S')}"
                    
                with open(date_path, "w", encoding="utf-8") as f:
                    f.write(update_str)
                
                uploaded_file.seek(0)
                df_new = pd.read_excel(uploaded_file, header=3)
                df_new.to_csv(file_path, index=False)
                st.success(f"✅ {subject} 데이터가 업데이트되었습니다! '종합 랭킹'에도 즉시 반영됩니다.")
            except Exception as e:
                st.error(f"엑셀 파일을 읽는 중 오류가 발생했습니다: {e}")

        if os.path.exists(file_path):
            if os.path.exists(date_path):
                with open(date_path, "r", encoding="utf-8") as f:
                    saved_date = f.read()
                st.markdown(f"<p style='text-align: right; color: #E67E22; font-weight: bold;'>🕒 {saved_date}</p>", unsafe_allow_html=True)
            
            df = pd.read_csv(file_path)
            
            if '출석' in df.columns:
                df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
                total_students = len(df)
                
                zero_students = df[df['출석'] == 0]
                zero_count = len(zero_students)
                zero_ratio = (zero_count / total_students) * 100 if total_students else 0
                
                total_lectures = 15
                target_ratio = 0.90
                
                threshold_90 = int(np.ceil(total_lectures * target_ratio))
                threshold_2_3 = int(np.ceil(total_lectures * (2/3)))
                
                achieved_students = df[df['출석'] >= threshold_90]
                achieved_count = len(achieved_students)
                achieved_ratio = (achieved_count / total_students) * 100 if total_students else 0
                
                avg_attendance_count = df['출석'].mean()
                avg_completion_ratio = (avg_attendance_count / total_lectures) * 100
                
                col1, col2, col3 = st.columns(3)
                col1.metric("현재 전체 평균 수강률", f"{avg_completion_ratio:.1f}%")
                col2.metric("목표(90%) 달성 학생", f"{achieved_ratio:.1f}%", f"{achieved_count}명 / {threshold_90}강 이상")
                col3.metric("미수강 학생 (0강)", f"{zero_ratio:.1f}%", f"{zero_count}명 (밀착관리 필요)", delta_color="inverse")
                
                st.divider()
                
                display_cols = ['순번', '이름', '학번', '학과', '출석']
                existing_cols = [col for col in display_cols if col in df.columns]
                
                tab_zero, tab_under = st.tabs(["🆘 전면 미수강 (즉시 연락)", "⚠️ 90% 미달성"])
                
                with tab_zero:
                    if zero_count > 0:
                        df_zero = zero_students[existing_cols].reset_index(drop=True)
                        styled_zero = df_zero.style.apply(style_attendance, threshold_2_3=threshold_2_3, subset=['출석'])
                        st.dataframe(styled_zero, use_container_width=True)
                    else:
                        st.success("대단합니다! 모든 학생이 수강을 시작했습니다.")
                        
                with tab_under:
                    under_target_students = df[(df['출석'] > 0) & (df['출석'] < threshold_90)]
                    if len(under_target_students) > 0:
                        df_under = under_target_students[existing_cols].reset_index(drop=True)
                        styled_under = df_under.style.apply(style_attendance, threshold_2_3=threshold_2_3, subset=['출석'])
                        st.dataframe(styled_under, use_container_width=True)
                    else:
                        st.success("🎉 해당하는 모든 학생이 목표 수강률을 달성했습니다!")
            else:
                st.error("데이터 오류: 업로드된 파일에 '출석' 열이 없습니다.")
                
        else:
            # 📌 호칭 수정
            st.info("📂 자료가 없어요... 담당 어시스턴트 및 멘토님이 데이터를 업로드해주세요!")
            col1, col2, col3 = st.columns(3)
            col1.metric("현재 전체 평균 수강률", "- %")
            col2.metric("목표(90%) 달성 학생", "- %", "- 명")
            col3.metric("미수강 학생 (0강)", "- %", "- 명")

# --- 4️⃣ 하단 저작권 푸터 (Footer) ---
st.markdown("""
<br><br><br>
<div style='text-align: center; padding: 20px; border-top: 1px solid #eaeaea; color: #888; font-size: 14px;'>
    &copy; 2026 All rights reserved. <b>한양대학교 ERICA 기초과학교육센터</b>
</div>
""", unsafe_allow_html=True)
