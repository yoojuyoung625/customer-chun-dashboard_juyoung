"""
대시보드 전역에서 재사용하는 색상 상수, 차트 레이아웃, 공통 렌더링 함수.
DESIGN.md 원칙: 색은 여기 COLOR_* 상수만 쓰고 새로 만들지 않는다.
"""

import streamlit as st

# ------------------------- 색상 상수 -------------------------
# 기존 이탈 대시보드 차트에서 쓰던 색
COLOR_BASE = "#8a8f98"
COLOR_HIGHLIGHT = "#d03b3b"
COLOR_CSAT = "#2a78d6"
COLOR_RECONTACT = "#d03b3b"
COLOR_MAP_CHURN = {"Y": "#d03b3b", "N": "#2a78d6"}

# 차트 배경/텍스트/그리드 공통 색
COLOR_SURFACE = "#fcfcfb"
COLOR_INK = "#0b0b0b"
COLOR_MUTED = "#52514e"
COLOR_GRID = "#e1e0d9"

# 상태 강조용 (채널 효율 등 "최악/나머지" 구분에 사용)
COLOR_CRITICAL = "#d03b3b"
COLOR_NEUTRAL = "#8a8f98"
COLOR_BAR = "#2a78d6"

# 마케팅 채널 카테고리컬 팔레트 (dataviz 스킬 검증 팔레트, slot 1~6 고정 순서)
CHANNEL_ORDER = ["SNS광고", "검색광고", "오프라인매장", "자사앱푸시", "제휴사", "지인추천"]
COLOR_CHANNEL = {
    "SNS광고": "#2a78d6",
    "검색광고": "#eb6834",
    "오프라인매장": "#1baf7a",
    "자사앱푸시": "#eda100",
    "제휴사": "#e87ba4",
    "지인추천": "#008300",
}

# ------------------------- 차트 공통 레이아웃 -------------------------
# 주의(DESIGN.md): go.Indicator(게이지)에 이 dict를 그대로 스프레드하면
# 빈 title 객체가 생겨 "undefined"가 렌더링된다. 게이지 차트는 title_font 등을
# 별도로 지정하고 이 dict를 쓰지 말 것.
CHART_LAYOUT = dict(
    plot_bgcolor=COLOR_SURFACE,
    paper_bgcolor=COLOR_SURFACE,
)

# st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)로 호출
PLOTLY_CONFIG = {"displayModeBar": False, "scrollZoom": False}


# ------------------------- 공통 렌더링 함수 -------------------------

def render_hero(title, subtitle=""):
    """페이지 상단 히어로 영역 — 굵은 제목(좌측 컬러 바) + муted 부제."""
    st.markdown(
        f"""
        <div style="border-left: 4px solid {COLOR_BAR}; padding-left: 16px; margin-bottom: 8px;">
            <div style="font-size: 1.6rem; font-weight: 700; color: {COLOR_INK};">{title}</div>
            <div style="font-size: 0.95rem; color: {COLOR_MUTED}; margin-top: 4px;">{subtitle}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)


def render_stat_tile(label, value, caption=""):
    """KPI 카드 하나. st.columns(N) 안에서 호출하면 카드 크기가 자동으로 균등해진다."""
    with st.container(border=True):
        st.markdown(
            f"<div style='font-size:0.82rem; color:{COLOR_MUTED};'>{label}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<div style='font-size:1.6rem; font-weight:700; color:{COLOR_INK};'>{value}</div>",
            unsafe_allow_html=True,
        )
        if caption:
            st.markdown(
                f"<div style='font-size:0.78rem; color:{COLOR_MUTED};'>{caption}</div>",
                unsafe_allow_html=True,
            )
