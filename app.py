import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import re

# --- 1️⃣ 페이지 설정 ---
st.set_page_config(page_title="2026 CORE 수강률 대시보드", page_icon="🐣", layout="wide")

st.markdown("""
<style>
    .header-container { margin-top: -35px; margin-bottom: 25px; border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 15px; }
    .main-title { font-size: 28px; font-weight: 800; color: var(--text-color); margin: 0; letter-spacing: -0.5px; }
    .sub-desc { font-size: 14px; color: gray; margin: 5px 0 0 0; font-weight: 500; }
    .section-title { font-size: 18px; font-weight: 700; color: var(--text-color); margin-bottom: 12px; margin-top: 15px; }
    
    button[data-baseweb="tab"] * { font-size: 15px !important; font-weight: bold !important; }
    button[data-baseweb="tab"][aria-selected="true"] * { color: #2980B9 !important; }
    div[data-baseweb="tab-highlight"] { background-color: #2980B9 !important; }

    .metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
    .metric-card {
        background-color: var(--secondary-background-color); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 8px;
        padding: 18px; 
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }
    .metric-label { font-size: 14px; font-weight: 600; color: var(--text-color); opacity: 0.8; }
    .metric-value { font-size: 28px; font-weight: 800; line-height: 1; margin-bottom: 8px; }

    @media (max-width: 768px) {
        .main-title { font-size: 22px; }
        .metric-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .metric-value { font-size: 22px; }
    }

    [data-testid="stFileUploader"] { padding: 0 !important; }
    [data-testid="stFileUploaderDropzone"] { padding: 5px 15px !important; min-height: 40px !important; background-color: transparent !important; border: 1px dashed gray !important; border-radius: 8px; }
    [data-testid="stFileUploaderDropzone"] div[data-testid="stMarkdownContainer"], [data-testid="stFileUploaderIcon"], [data-testid="stFileUploaderDropzone"] svg { display: none !important; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; border-color: #2980B9; color: #2980B9; }
    .stButton>button:hover { background-color: #2980B9; color: white; }
</style>
""", unsafe_allow_html=True)

# 🌟 타이틀 영역
st.markdown("""
<div class='header-container'>
    <h1 class='main-title'>2026 CORE 수강률 대시보드</h1>
    <p class='sub-desc'>한양대학교 ERICA 기초과학교육센터 | 목표 수강률 90% 이상</p>
</div>
""", unsafe_allow_html=True)

subjects = ["파이썬(최기환)", "파이썬(조상욱)", "화학(박경호)", "물리학(손승우)", "미적분(김은상)", "통계(이우주)", "기하와벡터(김은상)"]

def create_card(title, value, color, badge_text="", progress=None):
    b_html = f'<span style="font-size:12px; padding:3px 8px; border-radius:12px; font-weight:700; background-color:rgba(128,128,128,0.1); color:{color};">{badge_text}</span>' if badge_text else ""
    p_html = f'<div style="width:100%; background-color:rgba(128,128,128,0.2); height:6px; border-radius:4px; margin-top:10px;"><div style="width:{progress:.1f}%; background-color:{color}; height:100%; border-radius:4px;"></div></div>' if progress is not None else ""
    return f'<div class="metric-card"><div class="metric-header"><span class="metric-label">{title}</span>{b_html}</div><div class="metric-value" style="color: {color};">{value}</div>{p_html}</div>'

def style_attendance(s, threshold_2_3):
    colors = []
    for val in s:
        if val == 0: colors.append('background-color: #FDEDEC; color: #E74C3C; font-weight: bold;') 
        elif val >= threshold_2_3: colors.append('background-color: #E8F6F3; color: #27AE60; font-weight: bold;') 
        else: colors.append('background-color: #F9E79F; color: #D35400; font-weight: bold;') 
    return colors

def load_clean_history(path):
    if not os.path.exists(path): return pd.DataFrame(columns=['업데이트 날짜', '이수율(%)'])
    try:
        df = pd.read_csv(path)
        for c in df.columns:
            if '일시' in c or '시간' in c or '날짜' in c or '최종' in c: df.rename(columns={c: '업데이트 날짜'}, inplace=True)
            if '평균' in c or '이수율' in c or '수강률' in c or '비율' in c: df.rename(columns={c: '이수율(%)'}, inplace=True)
        if '업데이트 날짜' not in df.columns or '이수율(%)' not in df.columns:
            return pd.DataFrame(columns=['업데이트 날짜', '이수율(%)'])
        return df
    except:
        return pd.DataFrame(columns=['업데이트 날짜', '이수율(%)'])

tabs = st.tabs(["종합 랭킹"] + subjects)

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
        st.markdown("<div class='section-title'>전체 이수율 랭킹 (2/3 이상 수강)</div>", unsafe_allow_html=True)
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['이수율'], reverse=True)):
            st.info(f"**{i+1}위** | {item['과목']} ({item['이수율']:.1f}%)")
    with col2:
        st.markdown("<div class='section-title'>위험도 랭킹 (미수강 비율 순)</div>", unsafe_allow_html=True)
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['미수강비율'], reverse=True)):
            st.warning(f"**{i+1}위** | {item['과목']} ({item['미수강비율']:.1f}%)")

    st.markdown("<div class='section-title'>학과별 수강 현황 (전 과목 종합)</div>", unsafe_allow_html=True)
    if all_dept_data:
        combined_dept_df = pd.concat(all_dept_data).dropna(subset=['학과'])
        dept_stats = combined_dept_df.groupby('학과').agg(
            수강생수=('출석', 'count'), 평균수강률=('출석', lambda x: (x.mean() / 15) * 100), 안정권비율=('출석', lambda x: (len(x[x >= 10]) / len(x)) * 100)
        ).reset_index().sort_values(by='평균수강률', ascending=False).reset_index(drop=True)
        st.success(f"현재 평균 수강률 가장 높은 학과: **[{dept_stats.iloc[0]['학과']}]** ({dept_stats.iloc[0]['평균수강률']:.1f}%)")
        st.dataframe(dept_stats.style.format({'평균수강률': '{:.1f}%', '안정권비율': '{:.1f}%'}).background_gradient(cmap='Blues', subset=['평균수강률']), use_container_width=True, hide_index=True)

# --- 3️⃣ 개별 과목 ---
for i, subject in enumerate(subjects):
    with tabs[i+1]:
        file_path, date_path, history_path = f"data_{subject}.csv", f"date_{subject}.txt", f"history_{subject}.csv"
        
        with st.expander("엑셀 파일 업데이트 (어시스턴트 및 멘토 전용)"):
            uploaded_file = st.file_uploader(f"[{subject}] 파일 업로드", type=['xlsx'], key=f"up_{subject}")
            if uploaded_file is not None:
                if st.button(f"{subject} 데이터 반영하기", key=f"btn_{subject}"):
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
                        
                        h_df = load_clean_history(history_path)
                        h_df['업데이트 날짜'] = h_df['업데이트 날짜'].astype(str).apply(lambda x: re.search(r'\d{4}-\d{2}-\d{2}', x).group(0) if re.search(r'\d{4}-\d{2}-\d{2}', x) else x)
                        new_row = pd.DataFrame([{'업데이트 날짜': clean_date, '이수율(%)': round(current_rate, 1)}])
                        h_df = pd.concat([h_df, new_row], ignore_index=True)
                        h_df.drop_duplicates(subset=['업데이트 날짜'], keep='last', inplace=True)
                        h_df.to_csv(history_path, index=False)
                            
                        st.success("파일 처리가 완료되었습니다!")
                        st.rerun() 
                    except Exception as e: st.error(f"오류: {e}")

        # --- 메인 대시보드 화면 ---
        if os.path.exists(file_path):
            if os.path.exists(date_path):
                with open(date_path, "r", encoding="utf-8") as f: s_date = f.read()
                d_match = re.search(r'\d{4}-\d{2}-\d{2}', s_date)
                clean_s_date = d_match.group(0) if d_match else s_date
                st.markdown(f"<div style='text-align: right; color: gray; font-size: 14px; margin-bottom: 10px;'>업데이트 기준일: {clean_s_date}</div>", unsafe_allow_html=True)
            
            df = pd.read_csv(file_path)
            df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
            total_cnt = len(df)
            zero_df = df[df['출석']==0]
            mid_df = df[(df['출석']>0) & (df['출석']<10)]
            high_df = df[df['출석']>=10]
            
            avg_rate = (df['출석'].mean()/15)*100 if total_cnt > 0 else 0
            high_rate = (len(high_df)/total_cnt)*100 if total_cnt > 0 else 0
            zero_rate = (len(zero_df)/total_cnt)*100 if total_cnt > 0 else 0
            
            st.markdown("<div class='section-title'>핵심 수강 지표</div>", unsafe_allow_html=True)
            
            # 🌟 [수정 완료] 다크/라이트 모드에서 완벽하게 보이도록 "var(--text-color)" 적용
            c1 = create_card("전체 수강생", f"{total_cnt}명", "var(--text-color)", "Total")
            c2 = create_card("안정권 학생", f"{len(high_df)}명", "#27AE60", "10강↑")
            c3 = create_card("전면 미수강", f"{len(zero_df)}명", "#E74C3C", "0강")
            c4 = create_card("평균 수강률", f"{avg_rate:.1f}%", "#2980B9", progress=avg_rate)
            c5 = create_card("안정권 비율", f"{high_rate:.1f}%", "#27AE60", progress=high_rate)
            c6 = create_card("미수강 비율", f"{zero_rate:.1f}%", "#E74C3C", progress=zero_rate)
            
            html_cards = f'<div class="metric-grid">{c1}{c2}{c3}{c4}{c5}{c6}</div>'
            st.markdown(html_cards, unsafe_allow_html=True)
            
            st.divider()
            
            t_z, t_m, t_h = st.tabs([f"전면 미수강 ({len(zero_df)}명)", f"일부 수강 ({len(mid_df)}명)", f"안정권 ({len(high_df)}명)"])
            d_cols = [c for c in ['순번','이름','학번','학과','출석'] if c in df.columns]
            with t_z: st.dataframe(zero_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_m: st.dataframe(mid_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_h: st.dataframe(high_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
        else: 
            st.info("데이터를 업로드해주세요.")

st.markdown("<br><br><div style='text-align: center; color: gray; font-size: 13px;'>&copy; 2026 한양대학교 ERICA 기초과학교육센터</div>", unsafe_allow_html=True)
