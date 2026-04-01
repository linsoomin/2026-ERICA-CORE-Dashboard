import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import re
import time

# --- 1. Page Configuration ---
st.set_page_config(page_title="2026 CORE 수강률 대시보드", page_icon="🐣", layout="wide")

# ==========================================
# 🔒 세션 유지 (URL 파라미터 기반 24시간)
# ==========================================
SESSION_TOKEN_KEY = "auth_token"
VALID_TOKEN = "core2026_authed"

params = st.query_params
token_from_url = params.get(SESSION_TOKEN_KEY, "")

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'auth_time' not in st.session_state:
    st.session_state['auth_time'] = 0

# URL 토큰으로 자동 재인증 (24시간 이내)
if token_from_url == VALID_TOKEN and not st.session_state['authenticated']:
    auth_time = int(params.get("t", "0"))
    if time.time() - auth_time < 86400:
        st.session_state['authenticated'] = True
        st.session_state['auth_time'] = auth_time

# ==========================================
# 🔐 로그인 페이지
# ==========================================
if not st.session_state['authenticated']:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700;900&display=swap');

    html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif !important; }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container { padding-top: 3rem !important; }

    /* ━━━━ 배경 ━━━━ */
    /* 라이트 모드 */
    .stApp { background: #f0f4ff !important; }

    /* 다크 모드 */
    @media (prefers-color-scheme: dark) {
        .stApp { background: #0d1117 !important; }
    }

    /* ━━━━ 배지 ━━━━ */
    .login-badge {
        display: inline-block;
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        color: #fff !important;
        font-size: 16px;
        font-weight: 700;
        padding: 8px 22px;
        border-radius: 999px;
        margin-bottom: 14px;
        letter-spacing: 0.05em;
        box-shadow: 0 3px 12px rgba(37,99,235,0.30);
    }

    /* ━━━━ 컬럼 카드 영역 ━━━━ */
    /* 라이트 */
    [data-testid="column"]:nth-child(2) > div {
        background: #ffffff;
        border: 1px solid #dde5f5;
        border-radius: 20px;
        padding: 36px 36px 32px;
        box-shadow: 0 8px 40px rgba(37,99,235,0.10), 0 1px 4px rgba(0,0,0,0.04);
    }
    /* 다크 */
    @media (prefers-color-scheme: dark) {
        [data-testid="column"]:nth-child(2) > div {
            background: #161b27;
            border: 1px solid #1e2636;
            box-shadow: 0 8px 40px rgba(0,0,0,0.50);
        }
    }

    /* ━━━━ 인풋 라벨 ━━━━ */
    div[data-testid="stTextInput"] label {
        font-size: 13px !important;
        font-weight: 600 !important;
        letter-spacing: 0.02em !important;
    }
    /* 라이트 */
    div[data-testid="stTextInput"] label { color: #475569 !important; }
    /* 다크 */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stTextInput"] label { color: #64748b !important; }
    }

    /* ━━━━ 인풋 박스 ━━━━ */
    /* 라이트 */
    div[data-testid="stTextInput"] > div:first-child {
        border: 1.5px solid #dde5f5 !important;
        border-radius: 12px !important;
        background: #f8faff !important;
        outline: none !important;
        box-shadow: none !important;
        transition: border-color 0.2s, box-shadow 0.2s !important;
    }
    div[data-testid="stTextInput"] > div:first-child:focus-within {
        border: 1.5px solid #2563eb !important;
        background: #ffffff !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
    }
    /* 다크 */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stTextInput"] > div:first-child {
            border: 1.5px solid #1e2636 !important;
            background: #0d1117 !important;
        }
        div[data-testid="stTextInput"] > div:first-child:focus-within {
            border: 1.5px solid #3b82f6 !important;
            background: #0d1117 !important;
            box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
        }
    }

    /* ━━━━ 인풋 텍스트 ━━━━ */
    div[data-testid="stTextInput"] input {
        border: none !important;
        background: transparent !important;
        outline: none !important;
        box-shadow: none !important;
        font-size: 14px !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    div[data-testid="stTextInput"] input:hover,
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextInput"] input:active {
        border: none !important;
        background: transparent !important;
        outline: none !important;
        box-shadow: none !important;
    }
    /* 라이트 */
    div[data-testid="stTextInput"] input { color: #1e293b !important; }
    /* 다크 */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stTextInput"] input { color: #e2e8f0 !important; }
    }

    /* ━━━━ 눈 아이콘 버튼 ━━━━ */
    div[data-testid="stTextInput"] button {
        background: transparent !important;
        border: none !important;
        padding: 0 8px !important;
        cursor: pointer !important;
    }
    div[data-testid="stTextInput"] button { color: #94a3b8 !important; }
    div[data-testid="stTextInput"] button:hover { color: #2563eb !important; background: transparent !important; }
    div[data-testid="stTextInput"] > div { width: 100% !important; }

    /* ━━━━ 로그인 버튼 ━━━━ */
    div[data-testid="stFormSubmitButton"] button {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        font-family: 'Noto Sans KR', sans-serif !important;
        width: 100% !important;
        padding: 13px !important;
        box-shadow: 0 4px 16px rgba(37,99,235,0.30) !important;
        letter-spacing: 0.03em !important;
        transition: opacity 0.2s, transform 0.15s !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        opacity: 0.90 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 22px rgba(37,99,235,0.38) !important;
    }
    div[data-testid="stFormSubmitButton"] button:active {
        transform: translateY(0) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
        <div style="text-align:center; margin-bottom:24px;">
            <div class="login-badge">🐣 CORE Mentor Login</div>
            <div style="font-size:13px; color:#94a3b8; margin-top:10px; font-weight:500;">
                한양대학교 ERICA 기초과학교육센터
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            input_id = st.text_input("아이디 (Mentor ID)")
            input_pw = st.text_input("비밀번호 (Password)", type="password")
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("로그인", use_container_width=True)

        if submitted:
            if input_id == st.secrets["login"]["id"] and input_pw == st.secrets["login"]["pw"]:
                st.session_state['authenticated'] = True
                st.session_state['auth_time'] = int(time.time())
                st.query_params[SESSION_TOKEN_KEY] = VALID_TOKEN
                st.query_params["t"] = str(int(time.time()))
                st.rerun()
            else:
                st.error("❌ 아이디 또는 비밀번호가 일치하지 않습니다.")

        st.markdown("""
        <div style="text-align:center; margin-top:20px; font-size:11.5px; color:#b0bac8; font-weight:500;">
            © 2026 한양대학교 ERICA 기초과학교육센터
        </div>
        """, unsafe_allow_html=True)

    st.stop()

# ==========================================
# 🏆 2. 대시보드 본문
# ==========================================

st.markdown("""
<style>
    .main .block-container { padding-bottom: 1rem !important; }
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
    .hero-title {
        font-size: 32px; font-weight: 900; letter-spacing: -1px; margin: 0; line-height: 1.1;
        background: linear-gradient(135deg, #ffffff 0%, rgba(255,255,255,0.85) 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    }
    .hero-sub { color: rgba(255,255,255,0.9) !important; font-size: 14px; margin-top: 8px; font-weight: 500; }
    .section-title { font-size: 18px; font-weight: 700; color: var(--text-color); margin-bottom: 12px; margin-top: 15px; }
    .section-desc { font-size: 13px; color: gray; margin-top: -8px; margin-bottom: 14px; }
    button[data-baseweb="tab"] * { font-size: 15px !important; font-weight: bold !important; }
    button[data-baseweb="tab"][aria-selected="true"] * { color: #2563eb !important; }
    div[data-baseweb="tab-highlight"] { background-color: #2563eb !important; }
    .metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
    .metric-card {
        background-color: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px; padding: 18px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); border-color: #2563eb; }
    .metric-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
    .metric-label { font-size: 14px; font-weight: 600; opacity: 0.8; }
    .metric-value { font-size: 28px; font-weight: 800; line-height: 1; }
    .metric-sub { font-size: 12px; color: gray; font-weight: 600; }
    .progress-wrap { width: 100%; height: 6px; border-radius: 4px; background: rgba(128,128,128,0.15); margin-top: 12px; overflow: hidden; }
    .progress-bar { height: 100%; border-radius: 4px; transition: width 1s ease; }
    .rank-card { background-color: transparent; padding: 5px 0; }
    .rank-item {
        display: flex; align-items: center; justify-content: space-between;
        padding: 12px 15px; border-radius: 10px;
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.2);
        margin-bottom: 10px; transition: 0.2s ease;
    }
    .rank-item:hover { transform: translateX(3px); border-color: #2563eb; }
    .rank-left { display: flex; align-items: center; gap: 12px; }
    .rank-num { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 13px; color: white; flex-shrink: 0; }
    .rank-name { font-size: 15px; font-weight: 800; color: var(--text-color); }
    .rank-desc { font-size: 12px; color: gray; margin-top: 2px; }
    .rank-score { font-size: 18px; font-weight: 900; }
    .info-band { margin-bottom: 15px; }
    .inline-chip { display: inline-flex; align-items: center; font-size: 13px; padding: 6px 12px; border-radius: 20px; font-weight: 800; margin-right: 8px; margin-bottom: 8px; }
    .chip-blue { background: rgba(37,99,235,0.08); color: #2563eb; }
    .chip-gray { background: rgba(128,128,128,0.1); color: var(--text-color); }
    @media (max-width: 768px) {
        .hero { padding: 20px 15px; }
        .hero-title { font-size: 19px !important; white-space: nowrap; letter-spacing: -0.5px; }
        .hero-sub { font-size: 11px; }
        .metric-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .metric-card { padding: 15px 12px; }
        .metric-label { font-size: 13px; letter-spacing: -0.5px; white-space: nowrap; }
        .metric-value { font-size: 22px; }
    }
    .dashboard-footer { margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(128,128,128,0.1); text-align: center; color: gray; font-size: 12px; font-weight: 500; }
    [data-testid="stFileUploaderDropzone"] { padding: 5px 15px !important; background-color: transparent !important; border: 1px dashed gray !important; border-radius: 8px; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; border-color: #2563eb; color: #2563eb; }
</style>
""", unsafe_allow_html=True)

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
    b_html = f'<span style="font-size:11px; padding:2px 8px; border-radius:12px; font-weight:700; background:rgba(128,128,128,0.1); color:{color}; white-space:nowrap;">{badge}</span>' if badge else ""
    p_html = f'<div class="progress-wrap"><div class="progress-bar" style="width:{progress:.1f}%; background:{color};"></div></div>' if progress is not None else ""
    return f'<div class="metric-card"><div class="metric-header"><span class="metric-label">{icon} {title}</span>{b_html}</div><div class="metric-value" style="color: {color if color != "gray" else "var(--text-color)"};">{value}</div>{p_html}<div class="metric-sub" style="margin-top:8px;">{desc}</div></div>'

def create_rank_item(rank, name, value_text, tone="blue", desc=""):
    tone_map = {
        "blue": ("#3498DB", "linear-gradient(135deg, #3B82F6, #2980B9)"),
        "green": ("#2ECC71", "linear-gradient(135deg, #2ECC71, #27AE60)"),
        "red": ("#E74C3C", "linear-gradient(135deg, #E74C3C, #C0392B)"),
        "amber": ("#F1C40F", "linear-gradient(135deg, #F1C40F, #F39C12)")
    }
    text_color, bg = tone_map.get(tone, tone_map["blue"])
    return f'<div class="rank-item"><div class="rank-left"><div class="rank-num" style="background:{bg};">{rank}</div><div><div class="rank-name">{name}</div><div class="rank-desc">{desc}</div></div></div><div class="rank-score" style="color:{text_color};">{value_text}</div></div>'

tabs = st.tabs(["🏆 종합 랭킹"] + [f"{SUBJECT_ICONS.get(s, '📘')} {s}" for s in subjects])

with tabs[0]:
    ranking_data = []
    all_dept_data = []
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
                if '학과' in df.columns:
                    all_dept_data.append(df[['학과', '출석']])
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
        box = "<div class='rank-card'>"
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['이수율'], reverse=True), 1):
            tone = "green" if i == 1 else "blue"
            box += create_rank_item(i, item['과목'], f"{item['이수율']:.1f}%", tone, f"전체 {item['인원']}명 중 안정권 비율")
        box += "</div>"
        st.markdown(box, unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='section-title'>🚩 위험도 순위 (0강)</div>", unsafe_allow_html=True)
        box = "<div class='rank-card'>"
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['미수강비율'], reverse=True), 1):
            tone = "red" if i == 1 else "amber"
            box += create_rank_item(i, item['과목'], f"{item['미수강비율']:.1f}%", tone, f"전체 {item['인원']}명 중 0강 비율")
        box += "</div>"
        st.markdown(box, unsafe_allow_html=True)

    st.markdown("<div class='section-title' style='margin-top: 30px;'>🏫 학과별 수강 현황 (전 과목 종합)</div>", unsafe_allow_html=True)
    if all_dept_data:
        combined_dept_df = pd.concat(all_dept_data).dropna(subset=['학과'])
        dept_stats = combined_dept_df.groupby('학과').agg(
            수강생수=('출석', 'count'), 평균수강률=('출석', lambda x: (x.mean() / 15) * 100), 안정권비율=('출석', lambda x: (len(x[x >= 10]) / len(x)) * 100)
        ).reset_index().sort_values(by='평균수강률', ascending=False).reset_index(drop=True)
        top_dept = dept_stats.iloc[0]
        st.markdown(f"""
        <div class="info-band">
            <span class="inline-chip chip-blue">🏅 최고 학과: {top_dept['학과']}</span>
            <span class="inline-chip chip-gray">평균 수강률 {top_dept['평균수강률']:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)
        st.dataframe(dept_stats.style.format({'평균수강률': '{:.1f}%', '안정권비율': '{:.1f}%'}).background_gradient(cmap='Blues', subset=['평균수강률']), use_container_width=True, hide_index=True)
    else:
        st.info("현재 학과 통계 데이터가 없습니다.")

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
            if os.path.exists(date_path):
                with open(date_path, "r", encoding="utf-8") as f: s_date = f.read()
            else:
                s_date = "날짜 정보 없음"
            st.markdown(f"<div style='text-align: right; color: gray; font-size: 13px;'>기준일: {s_date}</div>", unsafe_allow_html=True)
            df = pd.read_csv(file_path)
            df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
            t_cnt = len(df)
            z_df = df[df['출석']==0]
            h_df = df[df['출석']>=10]
            mid_df = df[(df['출석']>0) & (df['출석']<10)]
            avg_r = (df['출석'].mean()/15*100) if t_cnt > 0 else 0
            h_r = (len(h_df)/t_cnt*100) if t_cnt > 0 else 0
            z_r = (len(z_df)/t_cnt*100) if t_cnt > 0 else 0
            st.markdown("<div class='section-title'>핵심 수강 지표</div>", unsafe_allow_html=True)
            cards = "".join([
                create_card("👥", "전체 수강생", f"{t_cnt}명", "현재 인원", color="gray"),
                create_card("✅", "안정권 학생", f"{len(h_df)}명", "10강 이상", badge="10강↑", color="#27AE60"),
                create_card("🚨", "전면 미수강", f"{len(z_df)}명", "수강 없음", badge="0강", color="#E74C3C"),
                create_card("📊", "평균 수강률", f"{avg_r:.1f}%", "15강 기준", progress=avg_r, color="#2980B9"),
                create_card("🎯", "안정권 비율", f"{h_r:.1f}%", "전체 대비", progress=h_r, color="#27AE60"),
                create_card("⚠️", "미수강 비율", f"{z_r:.1f}%", "전체 대비", progress=z_r, color="#E74C3C")
            ])
            st.markdown(f"<div class='metric-grid'>{cards}</div>", unsafe_allow_html=True)
            st.divider()
            t_z, t_m, t_h = st.tabs([f"🚨 전면 미수강({len(z_df)}명)", f"⚠️ 일부 수강({len(mid_df)}명)", f"✅ 안정권({len(h_df)}명)"])
            with t_z: st.dataframe(z_df[['이름','출석']], use_container_width=True, hide_index=True)
            with t_m: st.dataframe(mid_df[['이름','출석']], use_container_width=True, hide_index=True)
            with t_h: st.dataframe(h_df[['이름','출석']], use_container_width=True, hide_index=True)
        else: st.info("파일을 업로드해주세요.")

st.markdown("<div class='dashboard-footer'>© 2026 한양대학교 ERICA 기초과학교육센터</div>", unsafe_allow_html=True)
