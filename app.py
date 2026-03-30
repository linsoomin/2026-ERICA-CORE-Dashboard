import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import re

# --- 1. Page Configuration ---
st.set_page_config(page_title="2026 CORE 수강률 대시보드", page_icon="🐣", layout="wide")

st.markdown("""
<style>
    /* Global Container */
    .main .block-container { padding-bottom: 1rem !important; }
    
    /* Hero Section - 제거됨 */
    
    /* Section Typography */
    .section-title { font-size: 18px; font-weight: 700; color: var(--text-color); margin-bottom: 12px; margin-top: 15px; }
    .section-desc { font-size: 13px; color: gray; margin-top: -8px; margin-bottom: 14px; }
    
    /* Tab Styling */
    button[data-baseweb="tab"] * { font-size: 15px !important; font-weight: bold !important; }
    button[data-baseweb="tab"][aria-selected="true"] * { color: #2980B9 !important; }
    div[data-baseweb="tab-highlight"] { background-color: #2980B9 !important; }

    /* Metric Cards */
    .metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
    .metric-card {
        background-color: var(--secondary-background-color); border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 12px; padding: 18px; box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); border-color: #2980B9; }
    .metric-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
    .metric-label { font-size: 14px; font-weight: 600; opacity: 0.8; }
    .metric-icon { font-size: 18px; background: rgba(128,128,128,0.1); padding: 5px 8px; border-radius: 8px; }
    .metric-value { font-size: 28px; font-weight: 800; line-height: 1; }
    .metric-sub { font-size: 12px; color: gray; font-weight: 600; }
    
    /* Progress Bar */
    .progress-wrap { width: 100%; height: 6px; border-radius: 4px; background: rgba(128,128,128,0.15); margin-top: 12px; overflow: hidden; }
    .progress-bar { height: 100%; border-radius: 4px; transition: width 1s ease; }

    /* Rank List */
    .rank-card { background-color: transparent; padding: 5px 0; }
    .rank-item {
        display: flex; align-items: center; justify-content: space-between;
        padding: 12px 15px; border-radius: 10px;
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.2);
        margin-bottom: 10px; transition: 0.2s ease;
    }
    .rank-item:hover { transform: translateX(3px); border-color: #2980B9; }
    .rank-left { display: flex; align-items: center; gap: 12px; }
    .rank-num { width: 32px; height: 32px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: 900; font-size: 13px; color: white; flex-shrink: 0; }
    .rank-name { font-size: 15px; font-weight: 800; color: var(--text-color); }
    .rank-desc { font-size: 12px; color: gray; margin-top: 2px; }
    .rank-score { font-size: 18px; font-weight: 900; }

    /* Info Chips */
    .info-band { margin-bottom: 15px; }
    .inline-chip { display: inline-flex; align-items: center; font-size: 13px; padding: 6px 12px; border-radius: 20px; font-weight: 800; margin-right: 8px; margin-bottom: 8px; }
    .chip-blue { background: rgba(41,128,185,0.1); color: #3498DB; }
    .chip-gray { background: rgba(128,128,128,0.1); color: var(--text-color); }

    /* Mobile Optimization - FIXED LABEL WRAPPING */
    @media (max-width: 768px) {
        .metric-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .metric-card { padding: 15px 12px; } /* Adjust padding for mobile */
        .metric-label { font-size: 13px; letter-spacing: -0.5px; white-space: nowrap; } /* Prevent label wrap */
        .metric-value { font-size: 22px; }
    }

    /* Footer & UI Components */
    .dashboard-footer { margin-top: 15px; padding-top: 10px; border-top: 1px solid rgba(128,128,128,0.1); text-align: center; color: gray; font-size: 12px; font-weight: 500; }
    [data-testid="stFileUploaderDropzone"] { padding: 5px 15px !important; background-color: transparent !important; border: 1px dashed gray !important; border-radius: 8px; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; border-color: #2980B9; color: #2980B9; }

    /* ==========================================
       🔒 로그인 전용 스타일 (완벽 중앙 정렬 및 미니멀화)
       ========================================== */
    .login-wrapper {
        display: flex; justify-content: center; align-items: center; min-height: 100vh; /* 화면 가득 채움 */
    }
    .login-form {
        display: flex; flex-direction: column; align-items: center;
        max-width: 300px; width: 100%; /* 너비 제한 */
    }
    /* 카드 배경 제거 및 테두리만 남김 */
    .login-input-container {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 12px; padding: 30px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        width: 100%; margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- 로그인 화면 (맨 앞으로 이동) ---
# ==========================================
# 🔒 Hardcoded Authentication Logic (미니멀 정렬 버전)
# ==========================================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    # 완벽한 중앙 배치를 위한 CSS 래퍼
    st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])  # 수평 중앙 배치
    with col2:
        # 입력창을 감싸는 카드 테두리만 유지
        with st.container():
            st.markdown('<div class="login-input-container">', unsafe_allow_html=True)
            input_id = st.text_input("아이디 (Mentor ID)", key="login_id_input")
            input_pw = st.text_input("비밀번호 (Password)", type="password", key="login_pw_input")
            st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("로그인"):
            # 요청하신 정보와 대조
            if input_id == "2026ericacore" and input_pw == "2026ericacore@@":
                st.session_state['authenticated'] = True
                st.rerun()  # 성공 시 대시보드 화면으로 새로고침
            else:
                st.markdown('<div style="color: #E74C3C; font-weight: bold; text-align: center; margin-top: 10px;">❌ 정보가 일치하지 않습니다.</div>', unsafe_allow_html=True)
    
    # 로그인 화면용 하단 푸터 제거

    st.markdown('</div>', unsafe_allow_html=True) # login-wrapper 닫기
    st.stop()  # 로그인 성공 전까지 코드 중단

# ==========================================
# 🏆 로그인 성공 시에만 아래 내용 실행
# ==========================================

# --- 2. Hero Section (제거됨 - 로그인 성공 후에도 안 나오게) ---

subjects = ["파이썬(최기환)", "파이썬(조상욱)", "화학(박경호)", "물리학(손승우)", "미적분(김은상)", "통계(이우주)", "기하와벡터(김은상)"]
SUBJECT_ICONS = {"파이썬(최기환)": "🐍", "파이썬(조상욱)": "💻", "화학(박경호)": "🧪", "물리학(손승우)": "⚛️", "미적분(김은상)": "📐", "통계(이우주)": "📊", "기하와벡터(김은상)": "📏"}

# --- 3. UI Component Functions ---
def create_card(icon, title, value, desc, badge="", progress=None, color="#2980B9"):
    # Prevent badge wrapping internally
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

def load_clean_history(path):
    if not os.path.exists(path): return pd.DataFrame(columns=['업데이트 날짜', '이수율(%)'])
    try:
        df = pd.read_csv(path)
        for c in df.columns:
            if any(k in c for k in ['일시', '시간', '날짜', '최종']): df.rename(columns={c: '업데이트 날짜'}, inplace=True)
            if any(k in c for k in ['평균', '이수율', '수강률', '비율']): df.rename(columns={c: '이수율(%)'}, inplace=True)
        return df
    except: return pd.DataFrame(columns=['업데이트 날짜', '이수율(%)'])

def style_attendance(s, threshold_2_3):
    colors = []
    for val in s:
        if val == 0: colors.append('background-color: #FDEDEC; color: #E74C3C; font-weight: bold;') 
        elif val >= threshold_2_3: colors.append('background-color: #E8F6F3; color: #27AE60; font-weight: bold;') 
        else: colors.append('background-color: #F9E79F; color: #D35400; font-weight: bold;') 
    return colors

# --- 4. Main Application ---
tabs = st.tabs(["🏆 종합 랭킹"] + [f"{SUBJECT_ICONS.get(s, '📘')} {s}" for s in subjects])

# Dashboard Overview Tab
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
        
        # 최고 학과 띠 제거 (로그인 화면 제거와 함께 디자인 최소화)
        st.dataframe(dept_stats.style.format({'평균수강률': '{:.1f}%', '안정권비율': '{:.1f}%'}).background_gradient(cmap='Blues', subset=['평균수강률']), use_container_width=True, hide_index=True)
    else:
        st.info("현재 학과 통계 데이터가 없습니다.")

# Individual Subject Tabs
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
            
            # 개인정보 최소화를 위해 이름/출석만 나오도록 유지
            with t_z: st.dataframe(z_df[['이름','출석']], use_container_width=True, hide_index=True)
            with t_m: st.dataframe(mid_df[['이름','출석']], use_container_width=True, hide_index=True) 
            with t_h: st.dataframe(h_df[['이름','출석']], use_container_width=True, hide_index=True)
            
        else: st.info("파일을 업로드해주세요.")

# 하단 푸터도 최소화
