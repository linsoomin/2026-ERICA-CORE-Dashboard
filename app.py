import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import re

# --- 1️⃣ 페이지 설정 및 하이엔드 UI/UX CSS ---
st.set_page_config(page_title="2026 CORE 수강률 관리", layout="wide")

st.markdown("""
<style>
    :root { 
        --theme-color: #15397C; 
        --success-color: #2E7D32;
        --danger-color: #C62828;
        --bg-color: #ffffff;
        --text-main: #2C3E50;
        --text-sub: #7F8C8D;
        --border-color: #EAEDED;
        --progress-bg: #F2F3F4;
        --badge-bg: #E8F8F5;
        --hover-shadow: rgba(21, 57, 124, 0.15);
    }
    @media (prefers-color-scheme: dark) { 
        :root { 
            --theme-color: #5DADE2; 
            --success-color: #81C784;
            --danger-color: #E57373;
            --bg-color: #1E1E1E;
            --text-main: #F2F3F4;
            --text-sub: #BDC3C7;
            --border-color: #333333;
            --progress-bg: #2C3E50;
            --badge-bg: #2C3E50;
            --hover-shadow: rgba(93, 173, 226, 0.2);
        } 
    }
    
    .main-title { text-align: center; font-weight: 900; color: var(--theme-color); margin-bottom: 5px; letter-spacing: -1px; }
    .sub-title { color: var(--theme-color); margin-bottom: 15px; font-weight: 800; border-bottom: 2px solid var(--theme-color); padding-bottom: 5px; display: inline-block; }
    
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; transition: all 0.2s; }
    .stTabs [aria-selected="true"], .stTabs [data-baseweb="tab"]:hover { color: var(--theme-color) !important; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: var(--theme-color) !important; height: 3px; border-radius: 3px 3px 0 0; }

    /* 🌟 [디자인 핵심] 하이엔드 카드 레이아웃 & 호버 액션 */
    .metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; margin-bottom: 25px; }
    .metric-card {
        background-color: var(--bg-color); border: 1px solid var(--border-color); border-radius: 12px;
        padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    .metric-card:hover {
        transform: translateY(-4px); 
        box-shadow: 0 8px 15px var(--hover-shadow); border-color: var(--theme-color);
    }
    
    .metric-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 8px; }
    .metric-label { font-size: 14px; color: var(--text-sub); font-weight: 700; letter-spacing: -0.3px; }
    .badge { font-size: 11px; padding: 3px 8px; border-radius: 12px; background-color: var(--badge-bg); color: var(--theme-color); font-weight: 600; }
    .metric-value { font-size: 28px; font-weight: 900; color: var(--text-main); line-height: 1.1; margin-bottom: 5px; }
    .metric-desc { font-size: 12px; color: var(--text-sub); margin-top: 8px; font-weight: 500; }
    
    .progress-track { width: 100%; background-color: var(--progress-bg); height: 6px; border-radius: 4px; margin: 10px 0; overflow: hidden; }
    .progress-fill { height: 100%; border-radius: 4px; transition: width 1s ease-in-out; }

    @media (max-width: 768px) {
        .main-title { font-size: 24px !important; word-break: keep-all; }
        .metric-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
        .metric-card { padding: 15px; }
        .metric-value { font-size: 22px; }
        .metric-desc { font-size: 11px; letter-spacing: -0.5px; }
    }

    [data-testid="stFileUploader"] { padding: 0 !important; }
    [data-testid="stFileUploaderDropzone"] { padding: 5px 15px !important; min-height: 40px !important; background-color: transparent !important; border: 1px dashed var(--theme-color) !important; border-radius: 8px; }
    [data-testid="stFileUploaderDropzone"] div[data-testid="stMarkdownContainer"], [data-testid="stFileUploaderIcon"], [data-testid="stFileUploaderDropzone"] svg { display: none !important; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; border-color: var(--theme-color); color: var(--theme-color); }
    .stButton>button:hover { background-color: var(--theme-color); color: white; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🦁 2026 CORE 수강률 관리 대시보드</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; font-weight: 500;'>모든 과목 수강률 90% 이상 달성을 목표로 합니다.</p>", unsafe_allow_html=True)
st.divider()

subjects = ["파이썬(최기환)", "파이썬(조상욱)", "화학(박경호)", "물리학(손승우)", "미적분(김은상)", "통계(이우주)", "기하와벡터(김은상)"]

# 🌟 [오류 해결] 스트림릿이 헷갈리지 않도록 모든 HTML을 줄바꿈 없이 한 줄로 압축!
def create_card(icon, title, value, desc, badge="", progress=None, color="var(--theme-color)"):
    badge_html = f'<span class="badge">{badge}</span>' if badge else ""
    progress_html = f'<div class="progress-track"><div class="progress-fill" style="width: {progress:.1f}%; background-color: {color};"></div></div>' if progress is not None else ""
    return f'<div class="metric-card"><div class="metric-header"><span class="metric-label">{icon} {title}</span>{badge_html}</div><div class="metric-value" style="color: {color};">{value}</div>{progress_html}<div class="metric-desc">{desc}</div></div>'

def style_attendance(s, threshold_2_3):
    colors = []
    for val in s:
        if val == 0: colors.append('background-color: #FFCDD2; color: #900C3F; font-weight: bold;') 
        elif val >= threshold_2_3: colors.append('background-color: #4CAF50; color: white; font-weight: bold;') 
        else: colors.append('background-color: #C8E6C9; color: #1E8449; font-weight: bold;') 
    return colors

def load_clean_history(path):
    if not os.path.exists(path): return None
    df = pd.read_csv(path)
    rename_map = {}
    if '업데이트 일시' in df.columns: rename_map['업데이트 일시'] = '업데이트 날짜'
    if '평균수강률(%)' in df.columns: rename_map['평균수강률(%)'] = '이수율(%)'
    if rename_map:
        df.rename(columns=rename_map, inplace=True)
        try: df.to_csv(path, index=False)
        except: pass
    return df

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
        st.markdown("<div class='sub-title'>📈 전체 이수율 랭킹 (2/3 이상 수강)</div>", unsafe_allow_html=True)
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['이수율'], reverse=True)):
            st.info(f"**{i+1}위** | {item['과목']} ({item['이수율']:.1f}%)")
    with col2:
        st.markdown("<div class='sub-title'>🚨 위험도 랭킹 (미수강 비율 순)</div>", unsafe_allow_html=True)
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['미수강비율'], reverse=True)):
            st.warning(f"**{i+1}위** | {item['과목']} ({item['미수강비율']:.1f}%)")

    st.divider()
    st.markdown("<div class='sub-title'>🏫 학과별 수강 현황 (전 과목 종합)</div>", unsafe_allow_html=True)
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
                st.markdown(f"<div style='text-align: right; color: var(--theme-color); font-weight: 800; font-size: 15px; margin-bottom: 20px; letter-spacing: -0.5px;'>🕒 업데이트 기준일: {clean_s_date}</div>", unsafe_allow_html=True)
            
            df = pd.read_csv(file_path)
            df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
            total_cnt = len(df)
            zero_df = df[df['출석']==0]
            mid_df = df[(df['출석']>0) & (df['출석']<10)]
            high_df = df[df['출석']>=10]
            
            avg_rate = (df['출석'].mean()/15)*100 if total_cnt > 0 else 0
            high_rate = (len(high_df)/total_cnt)*100 if total_cnt > 0 else 0
            zero_rate = (len(zero_df)/total_cnt)*100 if total_cnt > 0 else 0
            
            st.markdown("<div class='sub-title'>📊 핵심 수강 지표</div>", unsafe_allow_html=True)
            
            # 🌟 [오류 박멸] 모든 카드를 한 줄의 문자열로 묶어서 HTML 렌더링
            c1 = create_card("👥", "전체 수강생", f"{total_cnt}명", "이번 학기 등록 인원", "Total", color="var(--text-main)")
            c2 = create_card("✅", "안정권 학생", f"{len(high_df)}명", "10강 이상 수강 완료", "10강↑", color="var(--success-color)")
            c3 = create_card("🚨", "전면 미수강", f"{len(zero_df)}명", "수강 이력 없음 (밀착관리)", "0강", color="var(--danger-color)")
            c4 = create_card("📊", "평균 수강률", f"{avg_rate:.1f}%", "전체 출석 ÷ (인원×15강)", progress=avg_rate, color="var(--theme-color)")
            c5 = create_card("🎯", "안정권 비율", f"{high_rate:.1f}%", "안정권 학생 ÷ 전체 수강생", progress=high_rate, color="var(--success-color)")
            c6 = create_card("⚠️", "미수강 비율", f"{zero_rate:.1f}%", "미수강 학생 ÷ 전체 수강생", progress=zero_rate, color="var(--danger-color)")
            
            html_cards = f'<div class="metric-grid">{c1}{c2}{c3}{c4}{c5}{c6}</div>'
            st.markdown(html_cards, unsafe_allow_html=True)
            
            st.divider()
            
            t_z, t_m, t_h = st.tabs([f"🚨 전면 미수강({len(zero_df)}명)", f"⚠️ 일부 수강({len(mid_df)}명)", f"✅ 안정권({len(high_df)}명)"])
            d_cols = [c for c in ['순번','이름','학번','학과','출석'] if c in df.columns]
            with t_z: st.dataframe(zero_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_m: st.dataframe(mid_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_h: st.dataframe(high_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
        else: 
            st.info("📂 어시스턴트 및 멘토님이 데이터를 업로드해주세요!")

st.markdown("<br><br><div style='text-align: center; color: var(--text-sub); font-size: 13px; font-weight: 500;'>&copy; 2026 한양대학교 ERICA 기초과학교육센터</div>", unsafe_allow_html=True)
