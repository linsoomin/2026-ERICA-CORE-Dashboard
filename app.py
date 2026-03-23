import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import re

# --- 1️⃣ 페이지 설정 (🐣 병아리 파비콘 & 넓은 레이아웃) ---
st.set_page_config(page_title="2026 CORE 수강률 대시보드", page_icon="🐣", layout="wide")

# 🌟 젠스파크의 예쁜 UI와 기존의 완벽한 반응형 CSS를 합쳤습니다.
st.markdown("""
<style>
    /* 🌟 [오류 원천 차단] 기기 다크모드 감지 코드 삭제 -> 스트림릿 기본 테마 변수 100% 활용 */
    .header-container { margin-top: -35px; margin-bottom: 20px; border-bottom: 1px solid rgba(128,128,128,0.2); padding-bottom: 15px; }
    .main-title { font-size: 28px; font-weight: 800; color: var(--text-color); margin: 0; letter-spacing: -0.5px; }
    .sub-desc { font-size: 14px; color: gray; margin: 5px 0 0 0; font-weight: 500; }
    .section-title { font-size: 18px; font-weight: 800; color: var(--text-color); margin-bottom: 12px; margin-top: 15px; }
    .section-desc { font-size: 13px; color: gray; margin-top: -8px; margin-bottom: 14px; }
    
    /* 🌟 탭 밑줄 및 글씨 파란색 강제 고정 */
    button[data-baseweb="tab"] * { font-size: 15px !important; font-weight: bold !important; }
    button[data-baseweb="tab"][aria-selected="true"] * { color: #2980B9 !important; }
    div[data-baseweb="tab-highlight"] { background-color: #2980B9 !important; }

    /* 🌟 젠스파크의 고급 메트릭 카드 UI (다크모드 호환 적용) */
    .metric-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px; }
    .metric-card {
        background-color: var(--secondary-background-color); 
        border: 1px solid rgba(128, 128, 128, 0.2); 
        border-radius: 12px;
        padding: 18px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        transition: transform 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); border-color: #2980B9; }
    
    .metric-top { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
    .metric-label { font-size: 14px; font-weight: 700; color: var(--text-color); opacity: 0.85; }
    .metric-icon { font-size: 18px; background: rgba(128,128,128,0.1); padding: 5px 8px; border-radius: 8px; }
    .metric-value { font-size: 28px; font-weight: 900; line-height: 1; margin-bottom: 5px; }
    .metric-sub { font-size: 12px; color: gray; font-weight: 600; }
    
    .progress-wrap { width: 100%; height: 6px; border-radius: 4px; background: rgba(128,128,128,0.15); margin-top: 12px; overflow: hidden; }
    .progress-bar { height: 100%; border-radius: 4px; transition: width 1s ease; }

    /* 🌟 젠스파크 랭킹 리스트 UI (다크모드 호환) */
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

    /* 🌟 젠스파크 뱃지(Chip) UI */
    .info-band { margin-bottom: 15px; }
    .inline-chip { display: inline-flex; align-items: center; font-size: 13px; padding: 6px 12px; border-radius: 20px; font-weight: 800; margin-right: 8px; margin-bottom: 8px; }
    .chip-blue { background: rgba(41,128,185,0.1); color: #3498DB; }
    .chip-green { background: rgba(39,174,96,0.1); color: #2ECC71; }
    .chip-red { background: rgba(231,76,60,0.1); color: #E74C3C; }
    .chip-amber { background: rgba(243,156,18,0.1); color: #F1C40F; }
    .chip-gray { background: rgba(128,128,128,0.1); color: var(--text-color); }

    /* 🌟 모바일 환경 제목 1줄 고정 & 2칸 배열 */
    @media (max-width: 768px) {
        .main-title { font-size: 18px; white-space: nowrap; letter-spacing: -0.5px; }
        .sub-desc { font-size: 12px; word-break: keep-all; }
        .metric-grid { grid-template-columns: repeat(2, 1fr); gap: 10px; }
        .metric-value { font-size: 24px; }
    }

    [data-testid="stFileUploader"] { padding: 0 !important; }
    [data-testid="stFileUploaderDropzone"] { padding: 5px 15px !important; min-height: 40px !important; background-color: transparent !important; border: 1px dashed gray !important; border-radius: 8px; }
    [data-testid="stFileUploaderDropzone"] div[data-testid="stMarkdownContainer"], [data-testid="stFileUploaderIcon"], [data-testid="stFileUploaderDropzone"] svg { display: none !important; }
    .stButton>button { width: 100%; font-weight: bold; border-radius: 8px; border-color: #2980B9; color: #2980B9; }
    .stButton>button:hover { background-color: #2980B9; color: white; }
</style>
""", unsafe_allow_html=True)

# 🌟 타이틀 영역 (좌측 정렬 모던 스타일 유지)
st.markdown("""
<div class='header-container'>
    <h1 class='main-title'>2026 CORE 수강률 대시보드</h1>
    <p class='sub-desc'>한양대학교 ERICA 기초과학교육센터 | 목표 수강률 90% 이상</p>
</div>
""", unsafe_allow_html=True)

subjects = ["파이썬(최기환)", "파이썬(조상욱)", "화학(박경호)", "물리학(손승우)", "미적분(김은상)", "통계(이우주)", "기하와벡터(김은상)"]

# 젠스파크가 추가한 과목별 귀여운 아이콘
SUBJECT_ICONS = {
    "파이썬(최기환)": "🐍", "파이썬(조상욱)": "💻", "화학(박경호)": "🧪", 
    "물리학(손승우)": "⚛️", "미적분(김은상)": "📐", "통계(이우주)": "📊", "기하와벡터(김은상)": "📏"
}

# 🌟 젠스파크의 세련된 카드 + 안정적인 테마 적용
def create_metric_card(title, value, color, icon, subtitle="", progress=None):
    # '전체 수강생' 처럼 회색을 넘길 경우 다크모드에서 흰색으로 보이도록 var(--text-color) 강제 적용
    text_color = "var(--text-color)" if color == "gray" else color
    
    p_html = ""
    if progress is not None:
        safe_prog = max(0, min(float(progress), 100))
        p_html = f'<div class="progress-wrap"><div class="progress-bar" style="width:{safe_prog:.1f}%; background:{color};"></div></div>'
    
    return f"""
    <div class="metric-card">
        <div class="metric-top">
            <div class="metric-label">{title}</div>
            <div class="metric-icon">{icon}</div>
        </div>
        <div class="metric-value" style="color: {text_color};">{value}</div>
        <div class="metric-sub">{subtitle}</div>
        {p_html}
    </div>
    """

# 🌟 젠스파크의 랭킹 아이템
def create_rank_item(rank, name, value_text, tone="blue", desc=""):
    tone_map = {
        "blue": ("#3498DB", "linear-gradient(135deg, #3B82F6, #2980B9)"),
        "green": ("#2ECC71", "linear-gradient(135deg, #2ECC71, #27AE60)"),
        "red": ("#E74C3C", "linear-gradient(135deg, #E74C3C, #C0392B)"),
        "amber": ("#F1C40F", "linear-gradient(135deg, #F1C40F, #F39C12)")
    }
    text_color, bg = tone_map.get(tone, tone_map["blue"])
    return f'<div class="rank-item"><div class="rank-left"><div class="rank-num" style="background:{bg};">{rank}</div><div><div class="rank-name">{name}</div><div class="rank-desc">{desc}</div></div></div><div class="rank-score" style="color:{text_color};">{value_text}</div></div>'

def style_attendance(s, threshold_2_3):
    colors = []
    for val in s:
        if val == 0: colors.append('background-color: #FDEDEC; color: #E74C3C; font-weight: bold;') 
        elif val >= threshold_2_3: colors.append('background-color: #E8F6F3; color: #27AE60; font-weight: bold;') 
        else: colors.append('background-color: #F9E79F; color: #D35400; font-weight: bold;') 
    return colors

def safe_rate(num, den):
    return (num / den * 100) if den > 0 else 0

# --- 탭 구성 (젠스파크의 과목 아이콘 삽입) ---
tabs = st.tabs(["🏆 종합 랭킹"] + [f"{SUBJECT_ICONS.get(s, '')} {s}" for s in subjects])

# --- 2️⃣ 종합 랭킹 (젠스파크의 전체 요약 기능 퓨전) ---
with tabs[0]:
    ranking_data = []
    all_dept_data = []
    total_stu, total_high, total_zero = 0, 0, 0
    
    for subj in subjects:
        file_path = f"data_{subj}.csv"
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                if '출석' in df.columns:
                    df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
                    t_len = len(df)
                    if t_len > 0:
                        h_cnt = len(df[df['출석'] >= 10])
                        z_cnt = len(df[df['출석'] == 0])
                        ranking_data.append({'과목': subj, '이수율': safe_rate(h_cnt, t_len), '미수강비율': safe_rate(z_cnt, t_len), '인원': t_len})
                        total_stu += t_len
                        total_high += h_cnt
                        total_zero += z_cnt
                    if '학과' in df.columns:
                        all_dept_data.append(df[['학과', '출석']])
            except: pass

    # 젠스파크의 상단 요약 카드 패널
    st.markdown("<div class='section-title'>📊 모든 과목 전체 요약</div>", unsafe_allow_html=True)
    avg_comp = safe_rate(total_high, total_stu)
    avg_zero = safe_rate(total_zero, total_stu)
    best_s = max(ranking_data, key=lambda x: x['이수율'])['과목'] if ranking_data else "-"
    risk_s = max(ranking_data, key=lambda x: x['미수강비율'])['과목'] if ranking_data else "-"
    
    sum_cards = "".join([
        create_metric_card("총 관리 대상", f"{total_stu}명", "gray", "👥", "등록된 모든 과목 총합"),
        create_metric_card("평균 안정권 비율", f"{avg_comp:.1f}%", "#27AE60", "🟢", "출석 10강 이상 (전체)", avg_comp),
        create_metric_card("평균 미수강 비율", f"{avg_zero:.1f}%", "#E74C3C", "🚨", "출석 0강 (전체)", avg_zero),
        create_metric_card("최고 이수율 과목", best_s, "#8E44AD", "🏆", "가장 수강률이 높은 과목"),
        create_metric_card("최대 위험 과목", risk_s, "#F39C12", "⚠️", "0강 비율이 가장 높은 과목"),
        create_metric_card("센터 목표", "90% 이상", "#2980B9", "🎯", "안정권 90% 달성 목표")
    ])
    st.markdown(f"<div class='metric-grid'>{sum_cards}</div>", unsafe_allow_html=True)
    st.markdown("<hr style='margin: 30px 0; border: none; border-top: 1px dashed rgba(128,128,128,0.2);'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='section-title'>📈 전체 이수율 랭킹</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-desc'>출석 10강 이상 학생 비율 기준</div>", unsafe_allow_html=True)
        box = "<div class='rank-card'>"
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['이수율'], reverse=True), start=1):
            tone = "green" if i == 1 else "blue"
            box += create_rank_item(i, item['과목'], f"{item['이수율']:.1f}%", tone, f"전체 {item['인원']}명 중 안정권 비율")
        box += "</div>"
        st.markdown(box, unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='section-title'>🚨 위험도 랭킹</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-desc'>출석 0강 학생 비율 기준</div>", unsafe_allow_html=True)
        box = "<div class='rank-card'>"
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['미수강비율'], reverse=True), start=1):
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

# --- 3️⃣ 개별 과목 ---
for i, subject in enumerate(subjects):
    with tabs[i+1]:
        file_path, date_path = f"data_{subject}.csv", f"date_{subject}.txt"
        
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
                        st.success("파일 처리가 완료되었습니다!")
                        st.rerun() 
                    except Exception as e: st.error(f"오류: {e}")

        if os.path.exists(file_path):
            if os.path.exists(date_path):
                with open(date_path, "r", encoding="utf-8") as f: s_date = f.read()
                d_match = re.search(r'\d{4}-\d{2}-\d{2}', s_date)
                clean_s_date = d_match.group(0) if d_match else s_date
            else:
                clean_s_date = "-"
            
            df = pd.read_csv(file_path)
            df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)
            total_cnt = len(df)
            zero_df = df[df['출석']==0]
            mid_df = df[(df['출석']>0) & (df['출석']<10)]
            high_df = df[df['출석']>=10]
            
            avg_rate = safe_rate(df['출석'].sum(), total_cnt * 15)
            high_rate = safe_rate(len(high_df), total_cnt)
            zero_rate = safe_rate(len(zero_df), total_cnt)
            mid_rate = safe_rate(len(mid_df), total_cnt)
            
            # 우측 상단 업데이트 일자 + 젠스파크 정보 칩
            st.markdown(f"<div style='text-align: right; color: gray; font-size: 14px; font-weight: 600; margin-bottom: 10px;'>🕒 업데이트 기준일: {clean_s_date}</div>", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="info-band">
                <span class="inline-chip chip-blue">전체 평균 {avg_rate:.1f}%</span>
                <span class="inline-chip chip-green">안정권 {len(high_df)}명 ({high_rate:.1f}%)</span>
                <span class="inline-chip chip-amber">일부 수강 {len(mid_df)}명 ({mid_rate:.1f}%)</span>
                <span class="inline-chip chip-red">미수강 {len(zero_df)}명 ({zero_rate:.1f}%)</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div class='section-title'>핵심 수강 지표</div>", unsafe_allow_html=True)
            
            # 🌟 [수정 완료] 전체 수강생의 색상을 gray로 넘겨 -> 내부에서 var(--text-color)로 처리!
            c1 = create_metric_card("전체 수강생", f"{total_cnt}명", "gray", "👥", "이번 학기 등록 인원")
            c2 = create_metric_card("안정권 학생", f"{len(high_df)}명", "#27AE60", "✅", "10강 이상 수강")
            c3 = create_metric_card("전면 미수강", f"{len(zero_df)}명", "#E74C3C", "🚨", "수강 이력 없음")
            c4 = create_metric_card("평균 수강률", f"{avg_rate:.1f}%", "#2980B9", "📊", "15강 기준 평균", progress=avg_rate)
            c5 = create_metric_card("안정권 비율", f"{high_rate:.1f}%", "#27AE60", "🎯", "전체 인원 대비", progress=high_rate)
            c6 = create_metric_card("미수강 비율", f"{zero_rate:.1f}%", "#E74C3C", "⚠️", "전체 인원 대비", progress=zero_rate)
            
            st.markdown(f'<div class="metric-grid">{c1}{c2}{c3}{c4}{c5}{c6}</div>', unsafe_allow_html=True)
            
            st.divider()
            
            t_z, t_m, t_h = st.tabs([f"🚨 전면 미수강 ({len(zero_df)}명)", f"⚠️ 일부 수강 ({len(mid_df)}명)", f"✅ 안정권 ({len(high_df)}명)"])
            d_cols = [c for c in ['순번','이름','학번','학과','출석'] if c in df.columns]
            with t_z: st.dataframe(zero_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True, hide_index=True)
            with t_m: st.dataframe(mid_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True, hide_index=True)
            with t_h: st.dataframe(high_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']), use_container_width=True, hide_index=True)
        else: 
            st.info("상단 영역에서 엑셀 데이터를 업로드해주세요.")

st.markdown("<br><br><div style='text-align: center; color: gray; font-size: 13px;'>&copy; 2026 한양대학교 ERICA 기초과학교육센터</div>", unsafe_allow_html=True)
