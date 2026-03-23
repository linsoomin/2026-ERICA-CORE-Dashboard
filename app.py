import streamlit as st
import pandas as pd
import numpy as np
import os
import datetime
import re

# -----------------------------
# 1) 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="2026 CORE 수강률 대시보드",
    page_icon="🐣",
    layout="wide"
)

# -----------------------------
# 2) 스타일
# -----------------------------
st.markdown("""
<style>
:root {
    --brand: #2563EB;
    --brand-2: #1D4ED8;
    --mint: #10B981;
    --danger: #EF4444;
    --warning: #F59E0B;
    --violet: #7C3AED;
    --card-bg: rgba(255,255,255,0.78);
    --border: rgba(15,23,42,0.08);
    --shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
    --radius: 18px;
}

html, body, [data-testid="stAppViewContainer"] {
    background:
        radial-gradient(circle at top left, rgba(37,99,235,0.08), transparent 28%),
        radial-gradient(circle at top right, rgba(16,185,129,0.07), transparent 24%),
        linear-gradient(180deg, #F8FAFC 0%, #F3F6FB 100%);
}

.main .block-container {
    padding-top: 1.6rem;
    padding-bottom: 2rem;
    max-width: 1400px;
}

.hero {
    position: relative;
    overflow: hidden;
    padding: 28px 30px;
    border-radius: 24px;
    background:
        linear-gradient(135deg, rgba(37,99,235,0.95) 0%, rgba(29,78,216,0.92) 45%, rgba(124,58,237,0.88) 100%);
    box-shadow: 0 18px 45px rgba(37,99,235,0.18);
    margin-bottom: 18px;
}

.hero:before {
    content: "";
    position: absolute;
    right: -80px;
    top: -80px;
    width: 220px;
    height: 220px;
    background: rgba(255,255,255,0.12);
    border-radius: 50%;
}

.hero:after {
    content: "";
    position: absolute;
    right: 120px;
    bottom: -70px;
    width: 180px;
    height: 180px;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
}

.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(255,255,255,0.14);
    border: 1px solid rgba(255,255,255,0.18);
    color: white;
    padding: 7px 12px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 14px;
    backdrop-filter: blur(10px);
}

.hero-title {
    color: white;
    font-size: 34px;
    font-weight: 900;
    letter-spacing: -0.8px;
    margin: 0;
    line-height: 1.15;
}

.hero-sub {
    color: rgba(255,255,255,0.88);
    font-size: 14px;
    margin-top: 8px;
    font-weight: 500;
}

.section-title {
    font-size: 20px;
    font-weight: 800;
    letter-spacing: -0.3px;
    margin: 8px 0 14px 0;
    color: #0F172A;
}

.section-desc {
    font-size: 13px;
    color: #64748B;
    margin-top: -6px;
    margin-bottom: 14px;
}

.subtle-divider {
    height: 1px;
    border: none;
    background: linear-gradient(to right, transparent, rgba(100,116,139,0.18), transparent);
    margin: 18px 0;
}

.metric-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 16px;
    margin: 12px 0 8px 0;
}

.metric-card {
    background: var(--card-bg);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.55);
    box-shadow: var(--shadow);
    border-radius: var(--radius);
    padding: 18px;
    transition: all 0.25s ease;
    min-height: 132px;
}

.metric-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 36px rgba(15, 23, 42, 0.12);
}

.metric-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}

.metric-label {
    font-size: 13px;
    font-weight: 700;
    color: #475569;
}

.metric-icon {
    width: 38px;
    height: 38px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    background: rgba(37,99,235,0.10);
}

.metric-value {
    font-size: 30px;
    line-height: 1;
    font-weight: 900;
    letter-spacing: -1px;
    margin-bottom: 8px;
}

.metric-sub {
    font-size: 12px;
    color: #64748B;
    font-weight: 600;
}

.progress-wrap {
    width: 100%;
    height: 8px;
    border-radius: 999px;
    background: rgba(148,163,184,0.18);
    overflow: hidden;
    margin-top: 14px;
}

.progress-bar {
    height: 100%;
    border-radius: 999px;
}

.rank-card {
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(255,255,255,0.6);
    box-shadow: var(--shadow);
    border-radius: 18px;
    padding: 18px;
    height: 100%;
}

.rank-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    padding: 12px 14px;
    border-radius: 14px;
    background: rgba(248,250,252,0.9);
    border: 1px solid rgba(148,163,184,0.15);
    margin-bottom: 10px;
    transition: 0.2s ease;
}

.rank-item:hover {
    transform: translateX(2px);
    background: white;
}

.rank-left {
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
}

.rank-num {
    width: 34px;
    height: 34px;
    border-radius: 11px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 900;
    font-size: 13px;
    color: white;
    flex-shrink: 0;
}

.rank-name {
    font-size: 14px;
    font-weight: 800;
    color: #0F172A;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.rank-desc {
    font-size: 12px;
    color: #64748B;
    margin-top: 2px;
}

.rank-score {
    font-size: 16px;
    font-weight: 900;
    letter-spacing: -0.4px;
    flex-shrink: 0;
}

.info-band {
    background: linear-gradient(180deg, rgba(255,255,255,0.8), rgba(255,255,255,0.65));
    border: 1px solid rgba(15,23,42,0.06);
    box-shadow: var(--shadow);
    padding: 14px 16px;
    border-radius: 16px;
    margin-bottom: 12px;
}

.inline-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    padding: 7px 11px;
    border-radius: 999px;
    font-weight: 800;
    border: 1px solid transparent;
    margin-right: 8px;
    margin-bottom: 8px;
}

.chip-blue {
    background: rgba(37,99,235,0.10);
    color: #1D4ED8;
    border-color: rgba(37,99,235,0.12);
}
.chip-green {
    background: rgba(16,185,129,0.10);
    color: #059669;
    border-color: rgba(16,185,129,0.12);
}
.chip-red {
    background: rgba(239,68,68,0.10);
    color: #DC2626;
    border-color: rgba(239,68,68,0.12);
}
.chip-amber {
    background: rgba(245,158,11,0.12);
    color: #D97706;
    border-color: rgba(245,158,11,0.12);
}
.chip-violet {
    background: rgba(124,58,237,0.10);
    color: #6D28D9;
    border-color: rgba(124,58,237,0.14);
}

.subject-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 10px;
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(255,255,255,0.58);
    box-shadow: var(--shadow);
    padding: 18px 20px;
    border-radius: 18px;
}

.subject-title {
    font-size: 24px;
    font-weight: 900;
    letter-spacing: -0.5px;
    color: #0F172A;
    margin: 0;
}

.subject-sub {
    font-size: 13px;
    color: #64748B;
    margin-top: 6px;
}

.update-chip {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 9px 12px;
    font-size: 12px;
    font-weight: 800;
    color: #334155;
    background: rgba(241,245,249,0.9);
    border: 1px solid rgba(148,163,184,0.18);
    border-radius: 999px;
    white-space: nowrap;
}

div[data-baseweb="tab-list"] {
    gap: 10px;
    background: transparent;
    padding-bottom: 4px;
}

button[data-baseweb="tab"] {
    background: rgba(255,255,255,0.72) !important;
    border: 1px solid rgba(148,163,184,0.14) !important;
    border-radius: 999px !important;
    padding: 8px 16px !important;
    box-shadow: 0 4px 14px rgba(15,23,42,0.04);
}

button[data-baseweb="tab"] * {
    font-size: 14px !important;
    font-weight: 800 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #2563EB, #1D4ED8) !important;
    border-color: transparent !important;
}

button[data-baseweb="tab"][aria-selected="true"] * {
    color: white !important;
}

div[data-baseweb="tab-highlight"] {
    display: none !important;
}

.streamlit-expanderHeader {
    font-weight: 800 !important;
    border-radius: 14px !important;
}

[data-testid="stExpander"] {
    border: 1px solid rgba(148,163,184,0.14) !important;
    border-radius: 16px !important;
    background: rgba(255,255,255,0.65);
    overflow: hidden;
}

[data-testid="stFileUploader"] {
    padding: 0 !important;
}

[data-testid="stFileUploaderDropzone"] {
    padding: 12px 16px !important;
    min-height: 56px !important;
    background: rgba(248,250,252,0.8) !important;
    border: 1.5px dashed rgba(37,99,235,0.35) !important;
    border-radius: 14px !important;
}

.stButton > button {
    width: 100%;
    border-radius: 12px;
    font-weight: 800;
    border: 1px solid rgba(37,99,235,0.2);
    color: white;
    background: linear-gradient(135deg, #2563EB, #1D4ED8);
    box-shadow: 0 8px 18px rgba(37,99,235,0.18);
}

.stButton > button:hover {
    border-color: transparent;
    color: white;
    background: linear-gradient(135deg, #1D4ED8, #1E40AF);
}

[data-testid="stDataFrame"] {
    border: 1px solid rgba(148,163,184,0.16);
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 8px 20px rgba(15,23,42,0.05);
    background: white;
}

footer {
    visibility: hidden;
}

.dashboard-footer {
    margin-top: 34px;
    text-align: center;
    color: #94A3B8;
    font-size: 12px;
    font-weight: 600;
}

@media (max-width: 900px) {
    .hero-title { font-size: 28px; }
    .metric-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .subject-head { flex-direction: column; }
}

@media (max-width: 640px) {
    .metric-grid { grid-template-columns: 1fr; }
    .hero { padding: 22px 18px; }
    .hero-title { font-size: 24px; }
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 3) 상단 히어로
# -----------------------------
st.markdown("""
<div class="hero">
    <div class="hero-badge">🐣 2026 CORE Dashboard</div>
    <h1 class="hero-title">2026 CORE 수강률 대시보드</h1>
    <div class="hero-sub">한양대학교 ERICA 기초과학교육센터 · 목표 수강률 90% 이상 · 과목별 위험군과 안정권을 한눈에 확인</div>
</div>
""", unsafe_allow_html=True)

subjects = [
    "파이썬(최기환)",
    "파이썬(조상욱)",
    "화학(박경호)",
    "물리학(손승우)",
    "미적분(김은상)",
    "통계(이우주)",
    "기하와벡터(김은상)"
]

SUBJECT_ICONS = {
    "파이썬(최기환)": "🐍",
    "파이썬(조상욱)": "💻",
    "화학(박경호)": "🧪",
    "물리학(손승우)": "⚛️",
    "미적분(김은상)": "📐",
    "통계(이우주)": "📊",
    "기하와벡터(김은상)": "📏"
}

# -----------------------------
# 4) 유틸 함수
# -----------------------------
def create_metric_card(title, value, color, icon="📌", subtitle="", progress=None):
    progress_html = ""
    if progress is not None:
        safe_progress = max(0, min(float(progress), 100))
        progress_html = f"""
        <div class="progress-wrap">
            <div class="progress-bar" style="width:{safe_progress:.1f}%; background:{color};"></div>
        </div>
        """
    return f"""
    <div class="metric-card">
        <div class="metric-top">
            <div class="metric-label">{title}</div>
            <div class="metric-icon">{icon}</div>
        </div>
        <div class="metric-value" style="color:{color};">{value}</div>
        <div class="metric-sub">{subtitle}</div>
        {progress_html}
    </div>
    """

def create_rank_item(rank, name, value_text, tone="blue", desc=""):
    tone_map = {
        "blue": ("#2563EB", "linear-gradient(135deg, #3B82F6, #2563EB)"),
        "green": ("#10B981", "linear-gradient(135deg, #34D399, #10B981)"),
        "red": ("#EF4444", "linear-gradient(135deg, #F87171, #EF4444)"),
        "amber": ("#F59E0B", "linear-gradient(135deg, #FBBF24, #F59E0B)"),
        "violet": ("#7C3AED", "linear-gradient(135deg, #8B5CF6, #7C3AED)")
    }
    text_color, bg = tone_map.get(tone, tone_map["blue"])
    return f"""
    <div class="rank-item">
        <div class="rank-left">
            <div class="rank-num" style="background:{bg};">{rank}</div>
            <div>
                <div class="rank-name">{name}</div>
                <div class="rank-desc">{desc}</div>
            </div>
        </div>
        <div class="rank-score" style="color:{text_color};">{value_text}</div>
    </div>
    """

def style_attendance(s, threshold_2_3):
    colors = []
    for val in s:
        if val == 0:
            colors.append('background-color: #FEE2E2; color: #B91C1C; font-weight: 700;')
        elif val >= threshold_2_3:
            colors.append('background-color: #DCFCE7; color: #15803D; font-weight: 700;')
        else:
            colors.append('background-color: #FEF3C7; color: #B45309; font-weight: 700;')
    return colors

def load_clean_history(path):
    if not os.path.exists(path):
        return pd.DataFrame(columns=['업데이트 날짜', '이수율(%)'])
    try:
        df = pd.read_csv(path)
        for c in df.columns:
            if '일시' in c or '시간' in c or '날짜' in c or '최종' in c:
                df.rename(columns={c: '업데이트 날짜'}, inplace=True)
            if '평균' in c or '이수율' in c or '수강률' in c or '비율' in c:
                df.rename(columns={c: '이수율(%)'}, inplace=True)
        if '업데이트 날짜' not in df.columns or '이수율(%)' not in df.columns:
            return pd.DataFrame(columns=['업데이트 날짜', '이수율(%)'])
        return df
    except:
        return pd.DataFrame(columns=['업데이트 날짜', '이수율(%)'])

def safe_rate(numerator, denominator):
    return (numerator / denominator * 100) if denominator > 0 else 0

# -----------------------------
# 5) 탭
# -----------------------------
tabs = st.tabs(["종합 랭킹"] + [f"{SUBJECT_ICONS.get(s, '📘')} {s}" for s in subjects])

# -----------------------------
# 6) 종합 랭킹 탭
# -----------------------------
with tabs[0]:
    ranking_data = []
    all_dept_data = []
    total_students_all = 0
    total_high_all = 0
    total_zero_all = 0

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
                        zero_count = len(df[df['출석'] == 0])

                        ranking_data.append({
                            '과목': subj,
                            '이수율': safe_rate(high_count, total),
                            '미수강비율': safe_rate(zero_count, total),
                            '전체인원': total
                        })

                        total_students_all += total
                        total_high_all += high_count
                        total_zero_all += zero_count

                    if '학과' in df.columns:
                        all_dept_data.append(df[['학과', '출석']])
            except:
                pass

    avg_completion = safe_rate(total_high_all, total_students_all)
    avg_zero_rate = safe_rate(total_zero_all, total_students_all)

    best_subject = max(ranking_data, key=lambda x: x['이수율'])['과목'] if ranking_data else "-"
    best_subject_rate = max([x['이수율'] for x in ranking_data], default=0)

    risk_subject = max(ranking_data, key=lambda x: x['미수강비율'])['과목'] if ranking_data else "-"
    risk_subject_rate = max([x['미수강비율'] for x in ranking_data], default=0)

    st.markdown("<div class='section-title'>전체 요약</div>", unsafe_allow_html=True)
    summary_cards = "".join([
        create_metric_card("전체 대상 인원", f"{total_students_all}명", "#2563EB", "👥", "등록된 모든 과목 기준"),
        create_metric_card("평균 안정권 비율", f"{avg_completion:.1f}%", "#10B981", "🟢", "출석 10강 이상 기준", avg_completion),
        create_metric_card("평균 미수강 비율", f"{avg_zero_rate:.1f}%", "#EF4444", "🚨", "출석 0강 기준", avg_zero_rate),
        create_metric_card("최고 이수율 과목", best_subject, "#7C3AED", "🏆", f"{best_subject_rate:.1f}%"),
        create_metric_card("최고 위험 과목", risk_subject, "#F59E0B", "⚠️", f"{risk_subject_rate:.1f}%"),
        create_metric_card("관리 목표", "90%+", "#1D4ED8", "🎯", "센터 목표 수강률")
    ])
    st.markdown(f"<div class='metric-grid'>{summary_cards}</div>", unsafe_allow_html=True)

    st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<div class='section-title'>전체 이수율 랭킹</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-desc'>출석 10강 이상 학생 비율 기준</div>", unsafe_allow_html=True)

        box = "<div class='rank-card'>"
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['이수율'], reverse=True), start=1):
            tone = "green" if i == 1 else "blue"
            box += create_rank_item(
                i,
                item['과목'],
                f"{item['이수율']:.1f}%",
                tone=tone,
                desc=f"전체 {item['전체인원']}명 중 안정권 비율"
            )
        box += "</div>"
        st.markdown(box, unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='section-title'>위험도 랭킹</div>", unsafe_allow_html=True)
        st.markdown("<div class='section-desc'>출석 0강 학생 비율 기준</div>", unsafe_allow_html=True)

        box = "<div class='rank-card'>"
        for i, item in enumerate(sorted(ranking_data, key=lambda x: x['미수강비율'], reverse=True), start=1):
            tone = "red" if i == 1 else "amber"
            box += create_rank_item(
                i,
                item['과목'],
                f"{item['미수강비율']:.1f}%",
                tone=tone,
                desc=f"전체 {item['전체인원']}명 중 전면 미수강 비율"
            )
        box += "</div>"
        st.markdown(box, unsafe_allow_html=True)

    st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>학과별 수강 현황 (전 과목 종합)</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-desc'>학과 단위 평균 수강률과 안정권 비율을 함께 확인합니다.</div>", unsafe_allow_html=True)

    if all_dept_data:
        combined_dept_df = pd.concat(all_dept_data).dropna(subset=['학과'])
        dept_stats = combined_dept_df.groupby('학과').agg(
            수강생수=('출석', 'count'),
            평균수강률=('출석', lambda x: (x.mean() / 15) * 100),
            안정권비율=('출석', lambda x: (len(x[x >= 10]) / len(x)) * 100)
        ).reset_index().sort_values(by='평균수강률', ascending=False).reset_index(drop=True)

        top_dept = dept_stats.iloc[0]
        st.markdown(f"""
        <div class="info-band">
            <span class="inline-chip chip-violet">🏅 최고 학과 · {top_dept['학과']}</span>
            <span class="inline-chip chip-blue">평균 수강률 {top_dept['평균수강률']:.1f}%</span>
            <span class="inline-chip chip-green">안정권 비율 {top_dept['안정권비율']:.1f}%</span>
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(
            dept_stats.style
            .format({'평균수강률': '{:.1f}%', '안정권비율': '{:.1f}%'})
            .background_gradient(cmap='Blues', subset=['평균수강률'])
            .background_gradient(cmap='Greens', subset=['안정권비율']),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("학과 데이터가 아직 없습니다.")

# -----------------------------
# 7) 개별 과목 탭
# -----------------------------
for i, subject in enumerate(subjects):
    with tabs[i + 1]:
        file_path = f"data_{subject}.csv"
        date_path = f"date_{subject}.txt"
        history_path = f"history_{subject}.csv"

        # 업로드 섹션
        with st.expander("엑셀 파일 업데이트 (어시스턴트 및 멘토 전용)"):
            uploaded_file = st.file_uploader(
                f"[{subject}] 파일 업로드",
                type=['xlsx'],
                key=f"up_{subject}"
            )

            if uploaded_file is not None:
                if st.button(f"{subject} 데이터 반영하기", key=f"btn_{subject}"):
                    try:
                        raw_xlsx = pd.read_excel(uploaded_file, header=None, nrows=1)
                        raw_str = str(raw_xlsx.iloc[0, 0]) if not raw_xlsx.empty else ""
                        date_match = re.search(r'\\d{4}-\\d{2}-\\d{2}', raw_str)
                        clean_date = date_match.group(0) if date_match else datetime.datetime.now().strftime('%Y-%m-%d')

                        with open(date_path, "w", encoding="utf-8") as f:
                            f.write(clean_date)

                        uploaded_file.seek(0)
                        df_new = pd.read_excel(uploaded_file, header=3)
                        df_new.to_csv(file_path, index=False)

                        df_new['출석'] = pd.to_numeric(df_new['출석'], errors='coerce').fillna(0)
                        current_rate = safe_rate(len(df_new[df_new['출석'] >= 10]), len(df_new))

                        h_df = load_clean_history(history_path)
                        h_df['업데이트 날짜'] = h_df['업데이트 날짜'].astype(str).apply(
                            lambda x: re.search(r'\\d{4}-\\d{2}-\\d{2}', x).group(0)
                            if re.search(r'\\d{4}-\\d{2}-\\d{2}', x) else x
                        )

                        new_row = pd.DataFrame([{
                            '업데이트 날짜': clean_date,
                            '이수율(%)': round(current_rate, 1)
                        }])

                        h_df = pd.concat([h_df, new_row], ignore_index=True)
                        h_df.drop_duplicates(subset=['업데이트 날짜'], keep='last', inplace=True)
                        h_df.to_csv(history_path, index=False)

                        st.success("파일 처리가 완료되었습니다!")
                        st.rerun()

                    except Exception as e:
                        st.error(f"오류: {e}")

        # 메인 화면
        if os.path.exists(file_path):
            clean_s_date = "-"
            if os.path.exists(date_path):
                with open(date_path, "r", encoding="utf-8") as f:
                    s_date = f.read()
                d_match = re.search(r'\\d{4}-\\d{2}-\\d{2}', s_date)
                clean_s_date = d_match.group(0) if d_match else s_date

            df = pd.read_csv(file_path)
            df['출석'] = pd.to_numeric(df['출석'], errors='coerce').fillna(0)

            total_cnt = len(df)
            zero_df = df[df['출석'] == 0]
            mid_df = df[(df['출석'] > 0) & (df['출석'] < 10)]
            high_df = df[df['출석'] >= 10]

            avg_rate = (df['출석'].mean() / 15) * 100 if total_cnt > 0 else 0
            high_rate = safe_rate(len(high_df), total_cnt)
            zero_rate = safe_rate(len(zero_df), total_cnt)
            partial_rate = safe_rate(len(mid_df), total_cnt)

            st.markdown(f"""
            <div class="subject-head">
                <div>
                    <h2 class="subject-title">{SUBJECT_ICONS.get(subject, "📘")} {subject}</h2>
                    <div class="subject-sub">과목별 수강 현황, 위험군, 안정권 학생을 한 번에 확인할 수 있습니다.</div>
                </div>
                <div class="update-chip">🗓️ 업데이트 기준일: {clean_s_date}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="info-band">
                <span class="inline-chip chip-blue">평균 수강률 {avg_rate:.1f}%</span>
                <span class="inline-chip chip-green">안정권 {len(high_df)}명 · {high_rate:.1f}%</span>
                <span class="inline-chip chip-amber">일부 수강 {len(mid_df)}명 · {partial_rate:.1f}%</span>
                <span class="inline-chip chip-red">전면 미수강 {len(zero_df)}명 · {zero_rate:.1f}%</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div class='section-title'>핵심 수강 지표</div>", unsafe_allow_html=True)

            cards = "".join([
                create_metric_card("전체 수강생", f"{total_cnt}명", "#0F172A", "👥", "현재 데이터 기준"),
                create_metric_card("안정권 학생", f"{len(high_df)}명", "#10B981", "🟢", "출석 10강 이상"),
                create_metric_card("전면 미수강", f"{len(zero_df)}명", "#EF4444", "🚨", "출석 0강"),
                create_metric_card("평균 수강률", f"{avg_rate:.1f}%", "#2563EB", "📈", "15강 기준 평균", avg_rate),
                create_metric_card("안정권 비율", f"{high_rate:.1f}%", "#10B981", "✅", "목표 달성 가능군", high_rate),
                create_metric_card("미수강 비율", f"{zero_rate:.1f}%", "#EF4444", "⚠️", "즉시 관리 필요", zero_rate)
            ])
            st.markdown(f"<div class='metric-grid'>{cards}</div>", unsafe_allow_html=True)

            st.markdown("<hr class='subtle-divider'>", unsafe_allow_html=True)
            st.markdown("<div class='section-title'>학생 구간별 명단</div>", unsafe_allow_html=True)

            t_z, t_m, t_h = st.tabs([
                f"🚨 전면 미수강 ({len(zero_df)}명)",
                f"🟠 일부 수강 ({len(mid_df)}명)",
                f"🟢 안정권 ({len(high_df)}명)"
            ])

            d_cols = [c for c in ['순번', '이름', '학번', '학과', '출석'] if c in df.columns]

            with t_z:
                st.dataframe(
                    zero_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']),
                    use_container_width=True,
                    hide_index=True
                )

            with t_m:
                st.dataframe(
                    mid_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']),
                    use_container_width=True,
                    hide_index=True
                )

            with t_h:
                st.dataframe(
                    high_df[d_cols].style.apply(style_attendance, threshold_2_3=10, subset=['출석']),
                    use_container_width=True,
                    hide_index=True
                )

        else:
            st.markdown(f"""
            <div class="info-band">
                <span class="inline-chip chip-amber">📂 아직 업로드된 데이터가 없습니다</span>
                <span class="inline-chip chip-blue">상단의 엑셀 파일 업데이트 영역에서 데이터를 등록해주세요</span>
            </div>
            """, unsafe_allow_html=True)

# -----------------------------
# 8) 푸터
# -----------------------------
st.markdown("""
<div class="dashboard-footer">
    © 2026 한양대학교 ERICA 기초과학교육센터
</div>
""", unsafe_allow_html=True)
