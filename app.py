import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import re
import altair as alt # 🌟 고퀄리티 파워 BI 스타일 그래프를 위한 도구 (기본 내장)

# --- 1️⃣ 웹 페이지 설정 및 현대적인 다크모드/카드 UI CSS ---
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

    /* 🌟 [핵심] 숫자 패널 6개를 현대적인 '독립된 카드' 형태로 디자인 */
    [data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 2px 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 10px;
    }
    @media (prefers-color-scheme: dark) {
        [data-testid="stMetric"] { background-color: #1e1e1e; border: 1px solid #333; }
    }

    /* 초슬림 업로더 */
    [data-testid="stFileUploader"] { padding: 0 !important; }
    [data-testid="stFileUploaderDropzone"] {
        padding: 5px 15px !important; min-height: 40px !important;
        background-color: transparent !important; border: 1px dashed var(--theme-color) !important;
    }
    [data-testid="stFileUploaderDropzone"] div[data-testid="stMarkdownContainer"], 
    [data-testid="stFileUploaderIcon"], [data-testid="stFileUploaderDropzone"] svg { display: none !important; }
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
    st.subheader("🏆 전체 과목 수강률 종합 랭킹")
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
                        high_count = len(df[df['출석'] >= 10])
                        ranking_data.append({'과목': subj, '이수율': (high_count / total) * 100, '미수강비율': (len(df[df['출석'] == 0]) / total) * 100})
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

# --- 3️⃣ 개별 과목 ---
for i, subject in enumerate(subjects):
    with tabs[i+1]:
        file_path, date_path, history_path = f"data_{subject}.csv", f"date_{subject}.txt", f"history_{subject}.csv"
        
        with st.expander("🔄 엑셀 파일 업데이트 (어시스턴트 및 멘토 전용)"):
            uploaded_file = st.file_uploader(f"[{subject}] 파일 업로드", type=['xlsx'], key=f"up_{subject}")
            
            if uploaded_file is not None:
                if st.button(f"🚀 {subject} 데이터 업데이트하기", key=f"btn_{subject}"):
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
                        
                        # 🌟 [과거 지저분한 장부 영구 세탁 로직]
                        if os.path.exists(history_path):
                            h_df = pd.read_csv(history_path)
                            if '업데이트 일시' in h_df.columns: h_df.rename(columns={'업데이트 일시': '업데이트 날짜'}, inplace=True)
                            if '평균수강률(%)' in h_df.columns: h_df.rename(columns={'평균수강률(%)': '이수율(%)'}, inplace=True)
                            
                            # 과거의 "최종내보내기.." 텍스트를 강제로 YYYY-MM-DD로 전부 뜯어고침
                            h_df['업데이트 날짜'] = h_df['업데이트 날짜'].astype(str).apply(lambda x: re.search(r'\d{4}-\d{2}-\d{2}', x).group(0) if re.search(r'\d{4}-\d{2}-\d{2}', x) else x)
                            
                            new_row = pd.DataFrame([{'업데이트 날짜': clean_date, '이수율(%)': round(current_rate, 1)}])
                            h_df = pd.concat([h_df, new_row], ignore_index=True)
                            h_df.drop_duplicates(subset=['업데이트 날짜'], keep='last', inplace=True)
                            h_df.to_csv(history_path, index=False)
                        else: 
                            pd.DataFrame([{'업데이트 날짜': clean_date, '이수율(%)': round(current_rate, 1)}]).to_csv(history_path, index=False)
                            
                        st.success("✅ 파일 처리 및 그래프 최적화가 완료되었습니다!")
                        st.rerun() 
                    except Exception as e: st.error(f"오류: {e}")

        # --- 메인 대시보드 화면 ---
        if os.path.exists(file_path):
            # 🌟 1. 상단: 날짜 표기 및 공유/다운로드 버튼
            col_date, col_share, col_down = st.columns([6, 2, 2])
            
            with col_date:
                if os.path.exists(date_path):
                    with open(date_path, "r", encoding="utf-8") as f: s_date = f.read()
                    d_match = re.search(r'\d{4}-\d{2}-\d{2}', s_date)
                    clean_s_date = d_match.group(0) if d_match else s_date
                    st.markdown(f"<div style='text-align: left; color: #15397C; font-weight: 900; font-size: 20px;'>🕒 업데이트 기준일: {clean_s_date}</div>", unsafe_allow_html=True)
            
            df = pd.read_csv(file_path)
            with col_share:
                if st.button("🔗 대시보드 링크 복사", key=f"share_{subject}"):
                    st.toast("대시보드 링크가 복사되었습니다! (Ctrl+V로 단톡방에 붙여넣어 주세요)")
            with col_down:
                st.download_button(label="📥 현재 명단 다운로드", data=df.to_csv(index=False).encode('utf-8-sig'), file_name=f"{subject}_{clean_s_date}.csv", mime="text/csv", key=f"down_{subject}")
            
            st.divider()

            # 데이터 처리
            df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
            zero_df, mid_df, high_df = df[df['출석']==0], df[(df['출석']>0) & (df['출석']<10)], df[df['출석']>=10]
            
            # 🌟 2. 좌/우 레이아웃 (좌: 카드형 숫자 6개 / 우: 명품 그래프)
            col_metrics, col_graph = st.columns([4, 6])
            
            with col_metrics:
                st.markdown("<h4 class='sub-title'>📊 핵심 수강 지표</h4>", unsafe_allow_html=True)
                m1, m2 = st.columns(2)
                m1.metric("전체 수강생", f"{len(df)}명")
                m2.metric("평균 수강률", f"{(df['출석'].mean()/15)*100:.1f}%")
                
                m3, m4 = st.columns(2)
                m3.metric("✅ 안정권 (10강↑)", f"{len(high_df)}명")
                m4.metric("✅ 안정권 비율", f"{(len(high_df)/len(df))*100:.1f}%")
                
                m5, m6 = st.columns(2)
                m5.metric("🚨 전면 미수강", f"{len(zero_df)}명")
                m6.metric("🚨 미수강 비율", f"{(len(zero_df)/len(df))*100:.1f}%", delta_color="off") # 마이너스 기호 없는 회색 텍스트
            
            with col_graph:
                st.markdown("<h4 class='sub-title'>📈 주차별 이수율(2/3 이상 수강) 추이</h4>", unsafe_allow_html=True)
                if os.path.exists(history_path):
                    h_df = pd.read_csv(history_path)
                    if len(h_df) >= 2:
                        # 🌟 [디자인 하이라이트] Altair를 사용한 파워 BI 스타일 그라데이션 그래프 (X, Y축 이름 완벽 표기)
                        base = alt.Chart(h_df).encode(
                            x=alt.X('업데이트 날짜:N', title='업데이트 날짜 (X축)', axis=alt.Axis(labelAngle=-45)),
                            y=alt.Y('이수율(%):Q', title='안정권 이수율 (%) (Y축)', scale=alt.Scale(domain=[0, 100]))
                        )
                        # 한양대 블루(#15397C) 라인과 하단 연한 그라데이션 채우기
                        line = base.mark_line(color='#15397C', point=True, strokeWidth=3)
                        area = base.mark_area(
                            color=alt.Gradient(
                                gradient='linear',
                                stops=[alt.GradientStop(color='#15397C', offset=0), alt.GradientStop(color='rgba(255,255,255,0)', offset=1)],
                                x1=1, x2=1, y1=1, y2=0
                            ),
                            opacity=0.5
                        )
                        # 그래프 렌더링
                        st.altair_chart((area + line).interactive(), use_container_width=True)
                    else: 
                        st.info("📌 첫 번째 데이터가 저장되었습니다. 다음 주에 파일이 한 번 더 올라오면 꺾은선 추이 그래프가 그려집니다!")
            
            st.divider()
            
            t_z, t_m, t_h = st.tabs([f"🆘 전면 미수강({len(zero_df)}명)", f"⚠️ 일부 수강({len(mid_df)}명)", f"✅ 안정권({len(high_df)}명)"])
            d_cols = [c for c in ['순번','이름','학번','학과','출석'] if c in df.columns]
            with t_z: st.dataframe(zero_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_m: st.dataframe(mid_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_h: st.dataframe(high_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
        else: 
            st.info("📂 어시스턴트 및 멘토님이 데이터를 업로드해주세요!")

st.markdown("<br><br><div style='text-align: center; color: #888; font-size: 13px;'>&copy; 2026 한양대학교 ERICA 기초과학교육센터</div>", unsafe_allow_html=True)
