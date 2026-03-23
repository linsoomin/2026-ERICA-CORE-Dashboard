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
    :root { 
        --theme-color: #15397C; 
        --text-color: #31333F;
        --border-color: rgba(49, 51, 63, 0.2);
    }
    @media (prefers-color-scheme: dark) { 
        :root { 
            --theme-color: #5DADE2; 
            --text-color: #FAFAFA;
            --border-color: rgba(250, 250, 250, 0.2);
        } 
    }
    
    .main-title { text-align: center; font-weight: 900; color: var(--theme-color); margin-bottom: 5px; }
    .sub-title { color: var(--theme-color); margin-bottom: 15px; font-weight: bold; }
    
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    .stTabs [aria-selected="true"], .stTabs [data-baseweb="tab"]:hover { color: var(--theme-color) !important; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: var(--theme-color) !important; }

    /* 🌟 숫자 메트릭 패널 테두리 (다크/라이트 자동 호환) */
    [data-testid="stMetric"] {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 15px;
        background-color: transparent;
    }

    /* 🌟 커스텀 도넛 차트 패널 */
    .donut-card {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        background-color: transparent;
        height: 100%;
    }
    .donut-title { font-size: 14px; font-weight: 600; margin-bottom: 8px; color: var(--text-color); opacity: 0.8; }
    .donut-value { font-size: 22px; font-weight: bold; margin-top: 5px; }

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

# 🌟 심플하고 에러 없는 도넛 차트 생성기
def get_donut(title, percentage, color):
    return f"""
    <div class="donut-card">
        <div class="donut-title">{title}</div>
        <svg viewBox="0 0 36 36" style="width: 60px; height: 60px; display: block; margin: 0 auto;">
            <path fill="none" stroke="rgba(128,128,128,0.2)" stroke-width="3.5" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" />
            <path fill="none" stroke="{color}" stroke-width="3.5" stroke-dasharray="{percentage}, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" stroke-linecap="round" />
        </svg>
        <div class="donut-value" style="color: {color};">{percentage:.1f}%</div>
    </div>
    """

def style_attendance(s, threshold_2_3):
    colors = []
    for val in s:
        if val == 0: colors.append('background-color: #FFCDD2; color: #900C3F; font-weight: bold;') 
        elif val >= threshold_2_3: colors.append('background-color: #4CAF50; color: white; font-weight: bold;') 
        else: colors.append('background-color: #C8E6C9; color: #1E8449; font-weight: bold;') 
    return colors

# 🌟 [에러 완벽 차단] 과거 기록 불러올 때 자동으로 이름 고쳐주는 힐러 함수
def load_clean_history(path):
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    rename_map = {}
    if '업데이트 일시' in df.columns: rename_map['업데이트 일시'] = '업데이트 날짜'
    if '평균수강률(%)' in df.columns: rename_map['평균수강률(%)'] = '이수율(%)'
    
    if rename_map:
        df.rename(columns=rename_map, inplace=True)
        try: df.to_csv(path, index=False) # 고친 김에 파일 덮어쓰기
        except: pass
        
    return df

tabs = st.tabs(["🏆 종합 랭킹"] + subjects)

# --- 2️⃣ 종합 랭킹 ---
with tabs[0]:
    st.subheader("🏆 전체 과목 수강률 종합 랭킹")
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
        file_path, date_path, history_path = f"data_{subject}.csv", f"date_{subject}.txt", f"history_{subject}.csv"
        
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
                        
                        df_new['출석'] = pd.to_numeric(df_new['출석'], errors='coerce').fillna(0)
                        current_rate = (len(df_new[df_new['출석'] >= 10]) / len(df_new)) * 100
                        
                        # 🌟 힐러 함수 적용
                        h_df = load_clean_history(history_path)
                        if h_df is not None:
                            h_df['업데이트 날짜'] = h_df['업데이트 날짜'].astype(str).apply(lambda x: re.search(r'\d{4}-\d{2}-\d{2}', x).group(0) if re.search(r'\d{4}-\d{2}-\d{2}', x) else x)
                            new_row = pd.DataFrame([{'업데이트 날짜': clean_date, '이수율(%)': round(current_rate, 1)}])
                            h_df = pd.concat([h_df, new_row], ignore_index=True)
                            h_df.drop_duplicates(subset=['업데이트 날짜'], keep='last', inplace=True)
                            h_df.to_csv(history_path, index=False)
                        else: 
                            pd.DataFrame([{'업데이트 날짜': clean_date, '이수율(%)': round(current_rate, 1)}]).to_csv(history_path, index=False)
                            
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
            
            col_metrics, col_graph = st.columns([5, 5])
            
            with col_metrics:
                st.markdown("<h4 class='sub-title'>📊 핵심 수강 지표</h4>", unsafe_allow_html=True)
                
                # 1행: 전체 수강생(숫자) / 평균수강률(도넛)
                m1, m2 = st.columns(2)
                with m1: st.metric("👥 전체 수강생", f"{total_cnt}명")
                with m2: 
                    avg_rate = (df['출석'].mean()/15)*100 if total_cnt > 0 else 0
                    st.markdown(get_donut("평균 수강률", avg_rate, "#15397C"), unsafe_allow_html=True)
                
                # 2행: 안정권(숫자) / 안정권비율(도넛)
                m3, m4 = st.columns(2)
                with m3: st.metric("✅ 안정권 (10강↑)", f"{len(high_df)}명")
                with m4:
                    high_rate = (len(high_df)/total_cnt)*100 if total_cnt > 0 else 0
                    st.markdown(get_donut("안정권 비율", high_rate, "#4CAF50"), unsafe_allow_html=True)
                
                # 3행: 미수강(숫자) / 미수강비율(도넛)
                m5, m6 = st.columns(2)
                with m5: st.metric("🚨 전면 미수강 (0강)", f"{len(zero_df)}명")
                with m6:
                    zero_rate = (len(zero_df)/total_cnt)*100 if total_cnt > 0 else 0
                    st.markdown(get_donut("미수강 비율", zero_rate, "#E74C3C"), unsafe_allow_html=True)
            
            with col_graph:
                st.markdown("<h4 class='sub-title'>📈 주차별 이수율(2/3 이상 수강) 추이</h4>", unsafe_allow_html=True)
                
                h_df = load_clean_history(history_path)
                if h_df is not None and len(h_df) > 0:
                    chart_data = h_df.set_index('업데이트 날짜')[['이수율(%)']]
                    # 🌟 [오류 박멸] 가장 안정적인 스트림릿 순정 Area Chart 적용
                    st.area_chart(chart_data, color="#15397C", use_container_width=True)
                else: 
                    st.info("📌 첫 번째 데이터가 저장되었습니다. 다음 주에 파일이 한 번 더 올라오면 꺾은선 추이 그래프가 그려집니다!")
            
            st.divider()
            
            t_z, t_m, t_h = st.tabs([f"🚨 전면 미수강({len(zero_df)}명)", f"⚠️ 일부 수강({len(mid_df)}명)", f"✅ 안정권({len(high_df)}명)"])
            d_cols = [c for c in ['순번','이름','학번','학과','출석'] if c in df.columns]
            with t_z: st.dataframe(zero_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_m: st.dataframe(mid_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_h: st.dataframe(high_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
        else: 
            st.info("📂 어시스턴트 및 멘토님이 데이터를 업로드해주세요!")

st.markdown("<br><br><div style='text-align: center; color: #888; font-size: 13px;'>&copy; 2026 한양대학교 ERICA 기초과학교육센터</div>", unsafe_allow_html=True)
