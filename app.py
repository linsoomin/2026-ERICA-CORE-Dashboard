import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import re

# --- 1️⃣ 페이지 설정 및 라이트/다크모드 & 모바일 완벽 호환 CSS ---
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

    /* 🌟 [핵심] CSS Grid를 활용한 반응형 카드 레이아웃 (PC는 3칸, 모바일은 2칸) */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 15px;
        margin-bottom: 20px;
    }
    .metric-card {
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 8px;
        padding: 15px 20px;
        background-color: transparent;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.02);
    }
    .metric-label { font-size: 14px; color: gray; margin-bottom: 5px; font-weight: 600; }
    .metric-value { font-size: 1.8rem; font-weight: bold; line-height: 1.2; }
    .metric-desc { font-size: 12px; color: gray; margin-top: 5px; }

    /* 📱 모바일 전용 UI 세팅 */
    @media (max-width: 768px) {
        .main-title { 
            font-size: 24px !important; 
            word-break: keep-all; /* '대시보드' 글자가 쪼개지지 않도록 방지 */
        }
        .metric-grid {
            grid-template-columns: repeat(2, 1fr); /* 모바일에서는 무조건 2칸씩 정렬 */
            gap: 10px;
        }
        .metric-card { padding: 12px 10px; }
        .metric-value { font-size: 1.5rem; }
        .metric-label { font-size: 12px; }
        .metric-desc { font-size: 10px; letter-spacing: -0.5px; }
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
            
            # 🌟 [반응형 해결] 스트림릿 st.metric 대신 직접 HTML/CSS Grid로 짜서 모바일에서도 2칸 유지!
            avg_rate = (df['출석'].mean()/15)*100 if total_cnt > 0 else 0
            high_rate = (len(high_df)/total_cnt)*100 if total_cnt > 0 else 0
            zero_rate = (len(zero_df)/total_cnt)*100 if total_cnt > 0 else 0
            
            metric_html = f"""
            <div class="metric-grid">
                <div class="metric-card">
                    <div class="metric-label">👥 전체 수강생</div>
                    <div class="metric-value">{total_cnt}명</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">✅ 안정권 (10강↑)</div>
                    <div class="metric-value">{len(high_df)}명</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">🚨 전면 미수강</div>
                    <div class="metric-value">{len(zero_df)}명</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">📊 평균 수강률</div>
                    <div class="metric-value">{avg_rate:.1f}%</div>
                    <div class="metric-desc">전체 출석 ÷ (인원×15강)</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">✅ 안정권 비율</div>
                    <div class="metric-value">{high_rate:.1f}%</div>
                    <div class="metric-desc">안정권 학생 ÷ 전체</div>
                </div>
                <div class="metric-card">
                    <div class="metric-label">🚨 미수강 비율</div>
                    <div class="metric-value">{zero_rate:.1f}%</div>
                    <div class="metric-desc">미수강 학생 ÷ 전체</div>
                </div>
            </div>
            """
            st.markdown(metric_html, unsafe_allow_html=True)
            
            st.divider()
            
            t_z, t_m, t_h = st.tabs([f"🚨 전면 미수강({len(zero_df)}명)", f"⚠️ 일부 수강({len(mid_df)}명)", f"✅ 안정권({len(high_df)}명)"])
            d_cols = [c for c in ['순번','이름','학번','학과','출석'] if c in df.columns]
            with t_z: st.dataframe(zero_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_m: st.dataframe(mid_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_h: st.dataframe(high_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
        else: 
            st.info("📂 어시스턴트 및 멘토님이 데이터를 업로드해주세요!")

st.markdown("<br><br><div style='text-align: center; color: #888; font-size: 13px;'>&copy; 2026 한양대학교 ERICA 기초과학교육센터</div>", unsafe_allow_html=True)
