import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import re

# --- 1️⃣ 페이지 설정 및 라이트/다크모드 완벽 호환 CSS ---
st.set_page_config(page_title="2026 CORE 수강률 관리", layout="wide")

st.markdown("""
<style>
    :root { --theme-color: #15397C; }
    @media (prefers-color-scheme: dark) { :root { --theme-color: #5DADE2; } }
    
    .main-title { text-align: center; font-weight: 900; color: var(--theme-color); margin-bottom: 5px; }
    .sub-title { color: var(--theme-color); margin-bottom: 15px; font-weight: bold; }
    
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    .stTabs [aria-selected="true"], .stTabs [data-baseweb="tab"]:hover { color: var(--theme-color) !important; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: var(--theme-color) !important; }

    /* 🌟 숫자 메트릭 패널 테두리 (가장 깔끔하고 안정적인 형태) */
    [data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 8px;
        padding: 15px 20px;
        background-color: transparent;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.02);
    }

    /* 업로더 슬림화 */
    [data-testid="stFileUploader"] { padding: 0 !important; }
    [data-testid="stFileUploaderDropzone"] {
        padding: 5px 15px !important; min-height: 40px !important;
        background-color: transparent !important; border: 1px dashed var(--theme-color) !important;
    }
    [data-testid="stFileUploaderDropzone"] div[data-testid="stMarkdownContainer"], 
    [data-testid="stFileUploaderIcon"], [data-testid="stFileUploaderDropzone"] svg { display: none !important; }
    .stButton>button { width: 100%; font-weight: bold; border-color: var(--theme-color); color: var(--theme-color); }
    .stButton>button:hover { background-color: var(--theme-color); color: white; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🦁 2026 CORE 수강률 관리 대시보드</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>모든 과목 수강률 90% 이상 달성을 목표로 합니다.</p>", unsafe_allow_html=True)
st.divider()

subjects = [
    "파이썬(최기환)", "파이썬(조상욱)", "화학(박경호)", 
    "물리학(손승우)", "미적분(김은상)", "통계(이우주)", "기하와벡터(김은상)"
]

def style_attendance(s, threshold_2_3):
    colors = []
    for val in s:
        if val == 0: colors.append('background-color: #FFCDD2; color: #900C3F; font-weight: bold;') 
        elif val >= threshold_2_3: colors.append('background-color: #4CAF50; color: white; font-weight: bold;') 
        else: colors.append('background-color: #C8E6C9; color: #1E8449; font-weight: bold;') 
    return colors

tabs = st.tabs(["🏆 종합 랭킹"] + subjects)

# --- 2️⃣ 종합 랭킹 ---
with tabs[0]:
    # 요청하신 "🏆 전체 과목 수강률 종합 랭킹" 글자 삭제 완료
    ranking_data = []
    all_dept_data = []
    
    for subj in subjects:
        file_path = f"data_{subj}.csv"
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                if '출석' in df.columns:
                    df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
                    total = len(df)
                    if total > 0:
                        high_count = len(df[df['출석'] >= 10])
                        ranking_data.append({'과목': subj, '이수율': (high_count / total) * 100, '미수강비율': (len(df[df['출석'] == 0]) / total) * 100})
                    if '학과' in df.columns:
                        all_dept_data.append(df[['학과', '출석']])
            except: pass

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<h3 class='sub-title'>📈 전체 이수율 랭킹 (2/3 이상 수강)</h3>", unsafe_allow_html=True)
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['이수율'], reverse=True)):
            st.info(f"**{i+1}위** | {item['과목']} ({item['이수율']:.1f}%)")
    with col2:
        st.markdown("<h3 class='sub-title'>🚨 위험도 랭킹 (미수강 비율 순)</h3>", unsafe_allow_html=True)
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['미수강비율'], reverse=True)):
            st.warning(f"**{i+1}위** | {item['과목']} ({item['미수강비율']:.1f}%)")

    st.divider()
    st.markdown("<h3 class='sub-title'>🏫 학과별 수강 현황 (전 과목 종합)</h3>", unsafe_allow_html=True)
    if all_dept_data:
        combined_dept_df = pd.concat(all_dept_data).dropna(subset=['학과'])
        dept_stats = combined_dept_df.groupby('학과').agg(
            수강생수=('출석', 'count'), 평균수강률=('출석', lambda x: (x.mean() / 15) * 100), 안정권비율=('출석', lambda x: (len(x[x >= 10]) / len(x)) * 100)
        ).reset_index().sort_values(by='평균수강률', ascending=False).reset_index(drop=True)
        st.success(f"🎉 현재 평균 수강률 가장 높은 학과: **[{dept_stats.iloc[0]['학과']}]** ({dept_stats.iloc[0]['평균수강률']:.1f}%)")
        st.dataframe(dept_stats.style.format({'평균수강률': '{:.1f}%', '안정권비율': '{:.1f}%'}).background_gradient(cmap='Blues', subset=['평균수강률']), use_container_width=True, hide_index=True)

# --- 3️⃣ 개별 과목 ---
for i, subject in enumerate(subjects):
    with tabs[i+1]:
        file_path, date_path = f"data_{subject}.csv", f"date_{subject}.txt"
        
        with st.expander("🔄 엑셀 파일 업데이트 (어시스턴트 및 멘토 전용)"):
            uploaded_file = st.file_uploader(f"[{subject}] 파일 업로드", type=['xlsx'], key=f"up_{subject}")
            
            if uploaded_file is not None:
                if st.button(f"🚀 {subject} 데이터 반영하기", key=f"btn_{subject}"):
                    try:
                        raw_xlsx = pd.read_excel(uploaded_file, header=None, nrows=1)
                        raw_str = str(raw_xlsx.iloc[0, 0]) if not raw_xlsx.empty else ""
                        date_match = re.search(r'\d{4}-\d{2}-\d{2}', raw_str)
                        clean_date = date_match.group(0) if date_match else datetime.datetime.now().strftime('%Y-%m-%d')
                        
                        with open(date_path, "w", encoding="utf-8") as f: f.write(clean_date)
                        
                        uploaded_file.seek(0)
                        df_new = pd.read_excel(uploaded_file, header=3)
                        df_new.to_csv(file_path, index=False)
                            
                        st.success("✅ 파일 처리가 완료되었습니다!")
                        st.rerun() 
                    except Exception as e: st.error(f"오류: {e}")

        # --- 메인 대시보드 화면 ---
        if os.path.exists(file_path):
            if os.path.exists(date_path):
                with open(date_path, "r", encoding="utf-8") as f: s_date = f.read()
                d_match = re.search(r'\d{4}-\d{2}-\d{2}', s_date)
                clean_s_date = d_match.group(0) if d_match else s_date
                st.markdown(f"<div style='text-align: right; color: #15397C; font-weight: 900; font-size: 16px; margin-bottom: 15px;'>🕒 업데이트 기준일: {clean_s_date}</div>", unsafe_allow_html=True)
            
            df = pd.read_csv(file_path)
            df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
            total_cnt = len(df)
            
            zero_df = df[df['출석']==0]
            mid_df = df[(df['출석']>0) & (df['출석']<10)]
            high_df = df[df['출석']>=10]
            
            st.markdown("<h4 class='sub-title'>📊 핵심 수강 지표</h4>", unsafe_allow_html=True)
            
            # 🌟 [디자인 핵심] 그래프/도넛 전부 제거, 아주 반듯한 3x2 패널 레이아웃 적용
            # 1행: 수치 (명)
            m1, m2, m3 = st.columns(3)
            with m1: st.metric("👥 전체 수강생", f"{total_cnt}명")
            with m2: st.metric("✅ 안정권 학생 (10강↑)", f"{len(high_df)}명")
            with m3: st.metric("🚨 전면 미수강 (0강)", f"{len(zero_df)}명")
            
            st.write("") # 줄바꿈 간격
            
            # 2행: 비율 (%) 및 하단 설명 텍스트
            m4, m5, m6 = st.columns(3)
            with m4: 
                avg_rate = (df['출석'].mean()/15)*100 if total_cnt > 0 else 0
                st.metric("📊 평균 수강률", f"{avg_rate:.1f}%", "전체 출석수 ÷ (전체 인원 × 15강)", delta_color="off")
            with m5:
                high_rate = (len(high_df)/total_cnt)*100 if total_cnt > 0 else 0
                st.metric("✅ 안정권 비율", f"{high_rate:.1f}%", "안정권 학생수 ÷ 전체 수강생", delta_color="off")
            with m6:
                zero_rate = (len(zero_df)/total_cnt)*100 if total_cnt > 0 else 0
                st.metric("🚨 미수강 비율", f"{zero_rate:.1f}%", "미수강 학생수 ÷ 전체 수강생", delta_color="off")
            
            st.divider()
            
            t_z, t_m, t_h = st.tabs([f"🚨 전면 미수강({len(zero_df)}명)", f"⚠️ 일부 수강({len(mid_df)}명)", f"✅ 안정권({len(high_df)}명)"])
            d_cols = [c for c in ['순번','이름','학번','학과','출석'] if c in df.columns]
            with t_z: st.dataframe(zero_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_m: st.dataframe(mid_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_h: st.dataframe(high_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
        else: 
            st.info("📂 어시스턴트 및 멘토님이 데이터를 업로드해주세요!")

st.markdown("<br><br><div style='text-align: center; color: #888; font-size: 13px;'>&copy; 2026 한양대학교 ERICA 기초과학교육센터</div>", unsafe_allow_html=True)
