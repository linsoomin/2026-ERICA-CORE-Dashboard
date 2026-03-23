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
    /* 🌟 [수정] 푸터 및 전체 여백 최적화 */
    .main .block-container { padding-bottom: 1rem !important; }

    /* 🌟 [깐지 타이틀] 히어로 섹션 */
    .hero {
        position: relative; overflow: hidden; padding: 25px 25px; border-radius: 20px;
        background: linear-gradient(135deg, rgba(37,99,235,0.95) 0%, rgba(29,78,216,0.95) 45%, rgba(124,58,237,0.9) 100%);
        box-shadow: 0 10px 30px rgba(37,99,235,0.15); margin-bottom: 25px; margin-top: -30px;
    }
    .hero-badge {
        display: inline-flex; align-items: center; background: rgba(255,255,255,0.15);
        border: 1px solid rgba(255,255,255,0.2); color: white !important; padding: 5px 12px;
        border-radius: 999px; font-size: 11px; font-weight: 700; margin-bottom: 12px;
    }
    /* 🌟 [수정] 라이트모드에서도 무조건 흰색으로 나오도록 !important 추가 */
    .hero-title { color: white !important; font-size: 32px; font-weight: 900; letter-spacing: -1px; margin: 0; line-height: 1.1; }
    .hero-sub { color: rgba(255,255,255,0.9) !important; font-size: 14px; margin-top: 8px; font-weight: 500; }

    /* 🌟 일반 섹션 및 탭 디자인 */
    .section-title { font-size: 18px; font-weight: 700; color: var(--text-color); margin-bottom: 12px; margin-top: 15px; }
    button[data-baseweb="tab"] * { font-size: 14px !important; font-weight: 800 !important; }
    button[data-baseweb="tab"][aria-selected="true"] * { color: #2980B9 !important; }
    div[data-baseweb="tab-highlight"] { background-color: #2980B9 !important; }

    /* 🌟 반응형 카드 */
    .metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
    .metric-card {
        background-color: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 12px; padding: 18px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    .metric-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
    .metric-label { font-size: 14px; font-weight: 600; opacity: 0.8; }
    .metric-value { font-size: 28px; font-weight: 800; line-height: 1; }

    /* 📱 [모바일 최적화] */
    @media (max-width: 768px) {
        .hero { padding: 20px 15px; }
        .hero-title { font-size: 19px !important; white-space: nowrap; letter-spacing: -0.5px; }
        .hero-sub { font-size: 11px; }
        .metric-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .metric-value { font-size: 22px; }
    }

    /* 🌟 [수정] 푸터 여백 줄이기 */
    .dashboard-footer {
        margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(128,128,128,0.1);
        text-align: center; color: gray; font-size: 12px; font-weight: 500;
    }

    [data-testid="stFileUploaderDropzone"] { padding: 5px 15px !important; background-color: transparent !important; border: 1px dashed gray !important; border-radius: 8px; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; border-color: #2980B9; color: #2980B9; }
</style>
""", unsafe_allow_html=True)

# 🌟 상단 히어로 섹션
st.markdown("""
<div class="hero">
    <div class="hero-badge">🐣 2026 CORE Dashboard</div>
    <h1 class="hero-title">2026 CORE 수강률 대시보드</h1>
    <div class="hero-sub">한양대학교 ERICA 기초과학교육센터 · 목표 수강률 90% 이상</div>
</div>
""", unsafe_allow_html=True)

subjects = ["파이썬(최기환)", "파이썬(조상욱)", "화학(박경호)", "물리학(손승우)", "미적분(김은상)", "통계(이우주)", "기하와벡터(김은상)"]
SUBJECT_ICONS = {"파이썬(최기환)": "🐍", "파이썬(조상욱)": "💻", "화학(박경호)": "🧪", "물리학(손승우)": "⚛️", "미적분(김은상)": "📐", "통계(이우주)": "📊", "기하와벡터(김은상)": "📏"}

def create_card(icon, title, value, desc, badge="", progress=None, color="#2980B9"):
    b_html = f'<span style="font-size:11px; padding:2px 8px; border-radius:12px; font-weight:700; background:rgba(128,128,128,0.1); color:{color};">{badge}</span>' if badge else ""
    p_html = f'<div style="width:100%; background:rgba(128,128,128,0.2); height:6px; border-radius:4px; margin-top:12px; overflow:hidden;"><div style="width:{progress:.1f}%; background:{color}; height:100%;"></div></div>' if progress is not None else ""
    return f'<div class="metric-card"><div class="metric-header"><span class="metric-label">{icon} {title}</span>{b_html}</div><div class="metric-value" style="color: {color if color != "gray" else "var(--text-color)"};">{value}</div>{p_html}<div style="font-size:11px; opacity:0.6; margin-top:8px;">{desc}</div></div>'

def load_clean_history(path):
    if not os.path.exists(path): return pd.DataFrame(columns=['업데이트 날짜', '이수율(%)'])
    try:
        df = pd.read_csv(path)
        for c in df.columns:
            if any(k in c for k in ['일시', '시간', '날짜', '최종']): df.rename(columns={c: '업데이트 날짜'}, inplace=True)
            if any(k in c for k in ['평균', '이수율', '수강률', '비율']): df.rename(columns={c: '이수율(%)'}, inplace=True)
        return df
    except: return pd.DataFrame(columns=['업데이트 날짜', '이수율(%)'])

tabs = st.tabs(["🏆 종합 랭킹"] + [f"{SUBJECT_ICONS.get(s, '📘')} {s}" for s in subjects])

# --- 2️⃣ 종합 랭킹 ---
with tabs[0]:
    ranking_data = []
    total_stu, total_high, total_zero = 0, 0, 0
    for subj in subjects:
        file_path = f"data_{subj}.csv"
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
                t_len = len(df)
                if t_len > 0:
                    h_cnt, z_cnt = len(df[df['출석'] >= 10]), len(df[df['출석'] == 0])
                    ranking_data.append({'과목': subj, '이수율': h_cnt/t_len*100, '미수강비율': z_cnt/t_len*100, '인원': t_len})
                    total_stu += t_len; total_high += h_cnt; total_zero += z_cnt
            except: pass

    st.markdown("<div class='section-title'>📊 모든 과목 요약</div>", unsafe_allow_html=True)
    avg_comp = (total_high/total_stu*100) if total_stu > 0 else 0
    avg_zero = (total_zero/total_stu*100) if total_stu > 0 else 0
    sum_cards = "".join([
        create_card("👥", "총 관리 학생", f"{total_stu}명", "등록된 모든 인원", color="gray"),
        create_card("🟢", "안정권 비율", f"{avg_comp:.1f}%", "10강 이상 (평균)", progress=avg_comp, color="#27AE60"),
        create_card("🚨", "미수강 비율", f"{avg_zero:.1f}%", "0강 (평균)", progress=avg_zero, color="#E74C3C")
    ])
    st.markdown(f"<div class='metric-grid'>{sum_cards}</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-title'>📈 이수율 순위 (10강↑)</div>", unsafe_allow_html=True)
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['이수율'], reverse=True), 1):
            st.info(f"**{i}위** | {item['과목']} ({item['이수율']:.1f}%)")
    with col2:
        st.markdown("<div class='section-title'>🚩 위험도 순위 (0강)</div>", unsafe_allow_html=True)
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['미수강비율'], reverse=True), 1):
            st.warning(f"**{i}위** | {item['과목']} ({item['미수강비율']:.1f}%)")

# --- 3️⃣ 개별 과목 ---
for i, subject in enumerate(subjects):
    with tabs[i+1]:
        file_path, date_path = f"data_{subject}.csv", f"date_{subject}.txt"
        with st.expander("엑셀 업데이트"):
            uploaded_file = st.file_uploader(f"[{subject}] 업로드", type=['xlsx'], key=f"up_{subject}")
            if uploaded_file and st.button(f"반영하기", key=f"btn_{subject}"):
                try:
                    raw_xlsx = pd.read_excel(uploaded_file, header=None, nrows=1)
                    date_match = re.search(r'\d{4}-\d{2}-\d{2}', str(raw_xlsx.iloc[0, 0]))
                    clean_date = date_match.group(0) if date_match else datetime.datetime.now().strftime('%Y-%m-%d')
                    with open(date_path, "w", encoding="utf-8") as f: f.write(clean_date)
                    df_new = pd.read_excel(uploaded_file, header=3)
                    df_new.to_csv(file_path, index=False)
                    st.success("완료!"); st.rerun()
                except Exception as e: st.error(f"오류: {e}")

        if os.path.exists(file_path):
            with open(date_path, "r", encoding="utf-8") as f: s_date = f.read()
            st.markdown(f"<div style='text-align: right; color: gray; font-size: 13px;'>기준일: {s_date}</div>", unsafe_allow_html=True)
            df = pd.read_csv(file_path)
            df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
            t_cnt = len(df); z_df, h_df = df[df['출석']==0], df[df['출석']>=10]
            avg_r = (df['출석'].mean()/15*100); h_r = (len(h_df)/t_cnt*100); z_r = (len(z_df)/t_cnt*100)

            cards = "".join([
                create_card("👥", "전체 수강생", f"{t_cnt}명", "현재 인원", color="gray"),
                create_card("✅", "안정권 학생", f"{len(h_df)}명", "10강 이상", badge="10강↑", color="#27AE60"),
                create_card("🚨", "전면 미수강", f"{len(z_df)}명", "수강 없음", badge="0강", color="#E74C3C"),
                create_card("📊", "평균 수강률", f"{avg_r:.1f}%", "15강 기준", progress=avg_r, color="#2980B9"),
                create_card("🎯", "안정권 비율", f"{h_r:.1f}%", "전체 대비", progress=h_r, color="#27AE60"),
                create_card("⚠️", "미수강 비율", f"{z_r:.1f}%", "전체 대비", progress=z_r, color="#E74C3C")
            ])
            st.markdown(f"<div class='metric-grid'>{cards}</div>", unsafe_allow_html=True)
            t_z, t_m, t_h = st.tabs([f"🚨 전면 미수강({len(z_df)})", f"⚠️ 일부 수강", f"✅ 안정권({len(h_df)})"])
            with t_z: st.dataframe(z_df[['이름','학번','학과','출석']], use_container_width=True, hide_index=True)
            with t_h: st.dataframe(h_df[['이름','학번','학과','출석']], use_container_width=True, hide_index=True)
        else: st.info("파일을 업로드해주세요.")

# 🌟 [수정] 푸터 영역 깔끔하게 마무리
st.markdown("<div class='dashboard-footer'>© 2026 한양대학교 ERICA 기초과학교육센터</div>", unsafe_allow_html=True)
