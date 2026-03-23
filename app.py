import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime

# --- 1️⃣ 페이지 설정 및 테마 CSS ---
st.set_page_config(page_title="2026 CORE 수강률 관리", layout="wide")

st.markdown("""
<style>
    :root { --theme-color: #15397C; }
    @media (prefers-color-scheme: dark) { :root { --theme-color: #5DADE2; } }
    
    .main-title { text-align: center; font-weight: 900; color: var(--theme-color); margin-bottom: 0px; }
    .sub-title { color: var(--theme-color); margin-bottom: 15px; font-weight: bold; }
    
    /* 탭 스타일 */
    .stTabs [data-baseweb="tab"] { font-size: 16px; font-weight: bold; }
    .stTabs [aria-selected="true"], .stTabs [data-baseweb="tab"]:hover { color: var(--theme-color) !important; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: var(--theme-color) !important; }

    /* 업로드 섹션 텍스트 정렬 */
    .upload-info { font-size: 12px; color: gray; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🦁 2026 CORE 수강률 관리 대시보드</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray; margin-bottom: 30px;'>모든 과목 수강률 90% 이상 달성을 목표로 합니다.</p>", unsafe_allow_html=True)

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
        sorted_by_comp = sorted(ranking_data, key=lambda x: x['이수율'], reverse=True)
        for i in range(len(subjects)):
            if i < len(sorted_by_comp):
                st.info(f"**{i+1}위** | {sorted_by_comp[i]['과목']} ({sorted_by_comp[i]['이수율']:.1f}%)")
            else: st.markdown(f"<div style='padding: 10px; border: 1px dashed #ccc; border-radius: 5px; color: #888; margin-bottom: 10px;'>{i+1}위 | ⬜ 자료 없음</div>", unsafe_allow_html=True)
                
    with col2:
        st.markdown("<h3 class='sub-title'>🚨 위험도 랭킹 (미수강 비율 순)</h3>", unsafe_allow_html=True)
        sorted_by_zero = sorted(ranking_data, key=lambda x: x['미수강비율'], reverse=True)
        for i in range(len(subjects)):
            if i < len(sorted_by_zero):
                st.warning(f"**{i+1}위** | {sorted_by_zero[i]['과목']} ({sorted_by_zero[i]['미수강비율']:.1f}%)")
            else: st.markdown(f"<div style='padding: 10px; border: 1px dashed #ccc; border-radius: 5px; color: #888; margin-bottom: 10px;'>{i+1}위 | ⬜ 자료 없음</div>", unsafe_allow_html=True)

# --- 3️⃣ 개별 과목 ---
for i, subject in enumerate(subjects):
    with tabs[i+1]:
        file_path = f"data_{subject}.csv"
        date_path = f"date_{subject}.txt"
        history_path = f"history_{subject}.csv"

        # 🌟 [업데이트 섹션 숨기기] expander로 감싸서 메인에서 치움
        with st.expander("🔄 데이터 업데이트 (어시스턴트 및 멘토 전용)"):
            uploaded_file = st.file_uploader(f"[{subject}] LMS 엑셀 파일(.xlsx) 업로드", type=['xlsx'], key=f"up_{subject}")
            if uploaded_file is not None:
                try:
                    # 날짜 추출
                    raw_xlsx = pd.read_excel(uploaded_file, header=None, nrows=1)
                    date_val = str(raw_xlsx.iloc[0, 0]).replace("최종 내보내기 :", "").strip()
                    with open(date_path, "w", encoding="utf-8") as f: f.write(date_val)
                    
                    uploaded_file.seek(0)
                    df_new = pd.read_excel(uploaded_file, header=3)
                    df_new.to_csv(file_path, index=False)
                    
                    # 🌟 이수율(2/3 이상) 히스토리 저장
                    df_new['출석'] = pd.to_numeric(df_new['출석'], errors='coerce').fillna(0)
                    current_rate = (len(df_new[df_new['출석'] >= 10]) / len(df_new)) * 100
                    new_hist = pd.DataFrame([{'업데이트 일시': date_val, '이수율(%)': current_rate}])
                    
                    if os.path.exists(history_path):
                        h_df = pd.read_csv(history_path)
                        if date_val not in h_df['업데이트 일시'].values:
                            pd.concat([h_df, new_history], ignore_index=True).to_csv(history_path, index=False)
                    else: new_hist.to_csv(history_path, index=False)
                    st.success("데이터가 업데이트되었습니다!")
                    st.rerun()
                except Exception as e: st.error(f"오류: {e}")

        if os.path.exists(file_path):
            if os.path.exists(date_path):
                with open(date_path, "r", encoding="utf-8") as f: s_date = f.read()
                st.markdown(f"<p style='text-align: right; color: #E67E22; font-weight: bold;'>🕒 기준일: {s_date}</p>", unsafe_allow_html=True)
            
            # --- 그래프 섹션 (Power BI 스타일) ---
            if os.path.exists(history_path):
                h_df = pd.read_csv(history_path)
                st.markdown("<h4 class='sub-title'>📈 주차별 이수율 추이 (2/3 이상 수강자)</h4>", unsafe_allow_html=True)
                if len(h_df) >= 2:
                    st.line_chart(h_df.set_index('업데이트 일시')[['이수율(%)']])
                else:
                    # 데이터가 1개일 때는 막대그래프로 보여줌
                    st.bar_chart(h_df.set_index('업데이트 일시')[['이수율(%)']])
                    st.caption("💡 데이터가 2개 이상 쌓이면 자동으로 선 그래프로 변경됩니다.")

            # 지표 카드
            df = pd.read_csv(file_path)
            df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
            z_df, m_df, h_df_list = df[df['출석']==0], df[(df['출석']>0) & (df['출석']<10)], df[df['출석']>=10]
            
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("평균 수강률", f"{(df['출석'].mean()/15)*100:.1f}%")
            c2.metric("안정권 (2/3↑)", f"{(len(h_df_list)/len(df))*100:.1f}%", f"{len(h_df_list)}명")
            c3.metric("전면 미수강 (0강)", f"{(len(z_df)/len(df))*100:.1f}%", f"{len(z_df)}명", delta_color="inverse")
            
            t_z, t_m, t_h = st.tabs([f"🆘 미수강({len(z_df)})", f"⚠️ 주의({len(m_df)})", f"✅ 안정({len(h_df_list)})"])
            d_cols = [c for c in ['순번','이름','학번','학과','출석'] if c in df.columns]
            with t_z: st.dataframe(z_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_m: st.dataframe(m_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
            with t_h: st.dataframe(h_df_list[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True)
        else: st.info("📂 어시스턴트 및 멘토님이 데이터를 업로드해주세요!")

st.markdown("<br><div style='text-align: center; color: #888; font-size: 12px;'>&copy; 2026 한양대학교 ERICA 기초과학교육센터</div>", unsafe_allow_html=True)
