import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

import common as c

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORT_DIR = os.path.join(BASE_DIR, "report")

CUTOFF_DATE = pd.Timestamp("2024-12-31")
BUCKET_ORDER = ["0회", "1회", "2회 이상"]
HIGHLIGHT_PLAN = "LTE베이직"          # 실제 데이터상 이탈율 1위 요금제
HIGHLIGHT_REGIONS = {"대구", "인천"}   # 실제 데이터상 이탈율 상위 2개 지역


# ------------------------- 데이터 로딩 -------------------------

@st.cache_data
def load_customers():
    return pd.read_csv(os.path.join(DATA_DIR, "data_customers.csv"), encoding="utf-8-sig")


@st.cache_data
def load_voc():
    return pd.read_csv(os.path.join(DATA_DIR, "data_voc.csv"), encoding="utf-8-sig")


@st.cache_data
def load_consultations():
    return pd.read_csv(os.path.join(DATA_DIR, "data_consultations.csv"), encoding="utf-8-sig")


@st.cache_data
def load_satisfaction():
    return pd.read_csv(os.path.join(DATA_DIR, "data_satisfaction.csv"), encoding="utf-8-sig")


@st.cache_data
def load_usage():
    return pd.read_csv(os.path.join(DATA_DIR, "data_usage_history.csv"), encoding="utf-8-sig")


@st.cache_data
def load_marketing_spend():
    return pd.read_csv(os.path.join(DATA_DIR, "data_marketing_spend.csv"))


@st.cache_data
def load_ad_performance():
    return pd.read_csv(os.path.join(DATA_DIR, "data_검색광고성과_상세.csv"), encoding="utf-8-sig")


@st.cache_data
def load_signup_revenue():
    return pd.read_csv(os.path.join(DATA_DIR, "data_가입매출.csv"), encoding="utf-8-sig")


# ------------------------- 상단 지표 -------------------------

def compute_overview_metrics(customers):
    total_n = len(customers)
    churn_n = int((customers["churn_yn"] == "Y").sum())
    churn_rate = churn_n / total_n * 100
    return total_n, churn_n, churn_rate


# ------------------------- ① VOC로 본 이탈 -------------------------

def build_chart1_voc(customers, voc):
    target = voc[(voc["category"] == "서비스불만") & (voc["sentiment"] == "부정")]
    target_ids = target["customer_id"].unique()
    target_customers = customers[customers["customer_id"].isin(target_ids)]

    total_n = len(customers)
    total_churn_n = int((customers["churn_yn"] == "Y").sum())
    total_churn_rate = total_churn_n / total_n * 100

    target_n = len(target_customers)
    target_churn_n = int((target_customers["churn_yn"] == "Y").sum())
    target_churn_rate = target_churn_n / target_n * 100 if target_n else 0

    df = pd.DataFrame([
        {"구분": "전체 고객", "고객수": total_n, "이탈고객수": total_churn_n, "이탈율": total_churn_rate},
        {"구분": "서비스불만 부정\nVOC 이력 있음", "고객수": target_n, "이탈고객수": target_churn_n, "이탈율": target_churn_rate},
    ])

    fig = px.bar(
        df, x="구분", y="이탈율", color="구분",
        color_discrete_map={"전체 고객": c.COLOR_BASE, "서비스불만 부정\nVOC 이력 있음": c.COLOR_HIGHLIGHT},
        custom_data=["고객수", "이탈고객수"],
        title="전체 고객 vs 서비스불만 부정 VOC 고객 이탈율 비교",
        labels={"이탈율": "이탈율 (%)", "구분": ""},
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>고객 수: %{customdata[0]}명<br>"
            "이탈 고객 수: %{customdata[1]}명<br>이탈율: %{y:.1f}%<extra></extra>"
        ),
        texttemplate="%{y:.1f}%", textposition="outside",
    )
    fig.update_layout(
        showlegend=False, yaxis_range=[0, df["이탈율"].max() * 1.35],
        **c.CHART_LAYOUT,
    )
    return fig


# ------------------------- ② 채널·만족도로 본 이탈 -------------------------

def build_chart2_channel_csat(consultations, satisfaction):
    merged = satisfaction.merge(
        consultations[["consult_id", "channel", "is_repeat"]], on="consult_id", how="left"
    )
    g = merged.groupby("channel").agg(
        CSAT평균=("score", "mean"),
        재문의율=("is_repeat", lambda s: (s == "Y").mean() * 100),
        n=("consult_id", "count"),
    ).sort_values("CSAT평균").reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Bar(
            x=g["channel"], y=g["CSAT평균"], name="CSAT 평균", marker_color=c.COLOR_CSAT,
            customdata=g[["재문의율", "n"]],
            hovertemplate=(
                "<b>%{x}</b><br>CSAT 평균: %{y:.2f}점<br>"
                "재문의율: %{customdata[0]:.1f}%<br>상담 건수: %{customdata[1]}건<extra></extra>"
            ),
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=g["channel"], y=g["재문의율"], name="재문의율", mode="lines+markers",
            line=dict(color=c.COLOR_RECONTACT, width=3), marker=dict(size=9, color=c.COLOR_RECONTACT),
            customdata=g[["CSAT평균", "n"]],
            hovertemplate=(
                "<b>%{x}</b><br>재문의율: %{y:.1f}%<br>"
                "CSAT 평균: %{customdata[0]:.2f}점<br>상담 건수: %{customdata[1]}건<extra></extra>"
            ),
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title="채널별 CSAT 평균(막대) vs 재문의율(꺾은선) — CSAT 낮은 순 정렬",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        **c.CHART_LAYOUT,
    )
    fig.update_xaxes(title_text="채널")
    fig.update_yaxes(title_text="CSAT 평균 (점)", secondary_y=False)
    fig.update_yaxes(title_text="재문의율 (%)", secondary_y=True, showgrid=False)
    return fig


# ------------------------- ③ 재문의 반복으로 본 이탈 -------------------------

def bucket_recontact(n):
    if n == 0:
        return "0회"
    if n == 1:
        return "1회"
    return "2회 이상"


def build_chart3_recontact_bucket(customers, consultations):
    recontact_n = consultations[consultations["is_repeat"] == "Y"].groupby("customer_id").size()
    merged = customers.set_index("customer_id").join(recontact_n.rename("recontact_n")).fillna(0)
    merged["recontact_n"] = merged["recontact_n"].astype(int)
    merged["구간"] = merged["recontact_n"].apply(bucket_recontact)

    g = merged.groupby("구간").agg(
        고객수=("churn_yn", "count"),
        이탈고객수=("churn_yn", lambda s: (s == "Y").sum()),
    )
    g["이탈율"] = g["이탈고객수"] / g["고객수"] * 100
    g = g.reindex(BUCKET_ORDER).reset_index()

    overall_rate = (customers["churn_yn"] == "Y").mean() * 100

    fig = px.bar(
        g, x="구간", y="이탈율", color="구간",
        color_discrete_map={"0회": c.COLOR_BASE, "1회": c.COLOR_BASE, "2회 이상": c.COLOR_HIGHLIGHT},
        category_orders={"구간": BUCKET_ORDER},
        custom_data=["고객수", "이탈고객수"],
        title="재문의 횟수 구간별 이탈율 (점선 = 전체 평균 이탈율)",
        labels={"이탈율": "이탈율 (%)", "구간": "재문의 횟수"},
        text=g["이탈율"].map(lambda v: f"{v:.1f}%"),
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>고객 수: %{customdata[0]}명<br>"
            "이탈 고객 수: %{customdata[1]}명<br>이탈율: %{y:.1f}%<extra></extra>"
        ),
        textposition="outside",
    )
    fig.add_hline(
        y=overall_rate, line_dash="dot", line_color=c.COLOR_INK,
        annotation_text=f"전체 평균 이탈율 {overall_rate:.1f}%", annotation_position="top left",
    )
    fig.update_layout(
        showlegend=False, yaxis_range=[0, max(g["이탈율"].max(), overall_rate) * 1.3],
        **c.CHART_LAYOUT,
    )
    return fig


# ------------------------- ④ 요금제로 본 이탈 -------------------------

def build_chart4_plan(customers):
    g = customers.groupby("plan_type").agg(
        고객수=("churn_yn", "count"),
        이탈고객수=("churn_yn", lambda s: (s == "Y").sum()),
    )
    g["이탈율"] = g["이탈고객수"] / g["고객수"] * 100
    g = g.sort_values("이탈율", ascending=False).reset_index()

    fig = px.bar(
        g, x="plan_type", y="이탈율", color="plan_type",
        color_discrete_map={p: (c.COLOR_HIGHLIGHT if p == HIGHLIGHT_PLAN else c.COLOR_BASE) for p in g["plan_type"]},
        custom_data=["고객수", "이탈고객수"],
        title="요금제별 이탈율 (이탈율 높은 순 정렬, 강조: LTE베이직)",
        labels={"이탈율": "이탈율 (%)", "plan_type": "요금제"},
        text=g["이탈율"].map(lambda v: f"{v:.1f}%"),
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>고객 수: %{customdata[0]}명<br>"
            "이탈 고객 수: %{customdata[1]}명<br>이탈율: %{y:.1f}%<extra></extra>"
        ),
        textposition="outside",
    )
    fig.update_layout(
        showlegend=False, yaxis_range=[0, g["이탈율"].max() * 1.3],
        **c.CHART_LAYOUT,
    )
    return fig


# ------------------------- ⑤ 지역으로 본 이탈 -------------------------

def build_chart5_region(customers):
    g = customers.groupby("region").agg(
        고객수=("churn_yn", "count"),
        이탈고객수=("churn_yn", lambda s: (s == "Y").sum()),
    )
    g["이탈율"] = g["이탈고객수"] / g["고객수"] * 100
    g = g.sort_values("이탈율", ascending=False).reset_index()
    busan = g[g["region"] == "부산"].iloc[0]

    fig = px.bar(
        g, x="region", y="이탈율", color="region",
        color_discrete_map={r: (c.COLOR_HIGHLIGHT if r in HIGHLIGHT_REGIONS else c.COLOR_BASE) for r in g["region"]},
        custom_data=["고객수", "이탈고객수"],
        title="지역별 이탈율 (이탈율 높은 순 정렬, 강조: 대구·인천)",
        labels={"이탈율": "이탈율 (%)", "region": "지역"},
        text=g["이탈율"].map(lambda v: f"{v:.1f}%"),
    )
    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>고객 수: %{customdata[0]}명<br>"
            "이탈 고객 수: %{customdata[1]}명<br>이탈율: %{y:.1f}%<extra></extra>"
        ),
        textposition="outside",
    )
    fig.update_layout(
        showlegend=False, yaxis_range=[0, g["이탈율"].max() * 1.3],
        margin=dict(b=90), **c.CHART_LAYOUT,
    )
    fig.add_annotation(
        text=(
            f"※ 부산은 표본 {int(busan['고객수'])}건 중 이탈 {int(busan['이탈고객수'])}건뿐이라 "
            f"이탈율({busan['이탈율']:.1f}%)이 매우 낮게 나타남 — 이탈 건수 자체가 적어 해석에 주의 필요"
        ),
        showarrow=False, xref="paper", yref="paper", x=0, y=-0.28, align="left",
        font=dict(size=11, color=c.COLOR_MUTED),
    )
    return fig


# ------------------------- ⑥ 가입기간·이용량으로 본 이탈 -------------------------

def compute_tenure_months(join_date):
    return (CUTOFF_DATE.year - join_date.dt.year) * 12 + (CUTOFF_DATE.month - join_date.dt.month)


def build_chart6_tenure_usage(customers, usage):
    customers = customers.copy()
    customers["join_date"] = pd.to_datetime(customers["join_date"])
    customers["가입기간_개월"] = compute_tenure_months(customers["join_date"])

    avg_usage_gb = (usage.groupby("customer_id")["data_usage_mb"].mean() / 1024).rename("평균데이터사용량_GB")
    merged = customers.merge(avg_usage_gb, on="customer_id", how="left")

    fig = px.scatter(
        merged, x="가입기간_개월", y="평균데이터사용량_GB", color="churn_yn",
        color_discrete_map=c.COLOR_MAP_CHURN,
        custom_data=["customer_id", "가입기간_개월", "평균데이터사용량_GB", "churn_yn"],
        title="가입기간 vs 평균 데이터 사용량 (색상 = 이탈 여부)",
        labels={
            "가입기간_개월": "가입기간 (개월, 2024-12-31 기준)",
            "평균데이터사용량_GB": "평균 데이터 사용량 (GB)",
            "churn_yn": "이탈 여부",
        },
        opacity=0.7,
    )
    fig.update_traces(
        hovertemplate=(
            "customer_id: %{customdata[0]}<br>가입기간: %{customdata[1]}개월<br>"
            "평균 데이터 사용량: %{customdata[2]:.2f}GB<br>이탈 여부: %{customdata[3]}<extra></extra>"
        ),
        marker=dict(size=8),
    )
    fig.update_layout(legend_title_text="이탈 여부", **c.CHART_LAYOUT)
    return fig


# ------------------------- 채널 효율 (마케팅집행 데이터) -------------------------

def build_channel_efficiency_bar(spend_df):
    """차트① — 채널별 유입 1건당 비용. 최악 채널만 COLOR_CRITICAL, 나머지 COLOR_NEUTRAL."""
    summary = spend_df.groupby("channel").agg(
        총실집행=("spend", "sum"), 총유입=("signups", "sum")
    ).reset_index()
    summary["단가"] = summary["총실집행"] / summary["총유입"]
    summary = summary.sort_values("단가")
    worst_channel = summary.loc[summary["단가"].idxmax(), "channel"]

    color_map = {ch: (c.COLOR_CRITICAL if ch == worst_channel else c.COLOR_NEUTRAL) for ch in summary["channel"]}

    fig = px.bar(
        summary, x="channel", y="단가", color="channel",
        color_discrete_map=color_map,
        text=summary["단가"].map(lambda v: f"{v:,.0f}원"),
        title="채널별 유입 1건당 비용 (누적, 강조: 최악 채널)",
        labels={"단가": "유입 1건당 비용 (원)", "channel": "채널"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, yaxis=dict(gridcolor=c.COLOR_GRID), **c.CHART_LAYOUT)
    return fig


def build_channel_efficiency_compare(spend_df):
    """차트② — 같은 채널의 3개월 단가 vs 누적 단가 그룹 막대."""
    months_sorted = sorted(spend_df["month"].unique())
    recent_3m = months_sorted[-3:]

    cum = spend_df.groupby("channel").agg(spend=("spend", "sum"), signups=("signups", "sum")).reset_index()
    cum["단가"] = cum["spend"] / cum["signups"]
    cum["구분"] = "누적"

    recent = spend_df[spend_df["month"].isin(recent_3m)].groupby("channel").agg(
        spend=("spend", "sum"), signups=("signups", "sum")
    ).reset_index()
    recent["단가"] = recent["spend"] / recent["signups"]
    recent["구분"] = f"최근 3개월({recent_3m[0]}~{recent_3m[-1]})"

    combined = pd.concat([recent[["channel", "단가", "구분"]], cum[["channel", "단가", "구분"]]], ignore_index=True)
    combined["channel"] = pd.Categorical(combined["channel"], categories=c.CHANNEL_ORDER, ordered=True)
    combined = combined.sort_values("channel")

    fig = px.bar(
        combined, x="channel", y="단가", color="구분", barmode="group",
        color_discrete_map={recent["구분"].iloc[0]: c.COLOR_NEUTRAL, "누적": c.COLOR_BAR},
        text=combined["단가"].map(lambda v: f"{v:,.0f}"),
        title="채널별 유입 1건당 비용 — 최근 3개월 vs 누적",
        labels={"단가": "유입 1건당 비용 (원)", "channel": "채널"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        yaxis=dict(gridcolor=c.COLOR_GRID), **c.CHART_LAYOUT,
    )
    return fig


# ------------------------- 페이지 1: 대시보드 -------------------------

def dashboard_page():
    c.render_hero("고객은 왜 이탈하는가", "이탈 원인 진단 대시보드")

    customers = load_customers()
    voc = load_voc()
    consultations = load_consultations()
    satisfaction = load_satisfaction()
    usage = load_usage()

    total_n, churn_n, churn_rate = compute_overview_metrics(customers)
    col1, col2, col3 = st.columns(3)
    with col1:
        c.render_stat_tile("전체 고객 수", f"{total_n}명")
    with col2:
        c.render_stat_tile("이탈 고객 수", f"{churn_n}명")
    with col3:
        c.render_stat_tile("전체 이탈율", f"{churn_rate:.1f}%")

    st.subheader("① VOC로 본 이탈")
    st.plotly_chart(build_chart1_voc(customers, voc), width="stretch", config=c.PLOTLY_CONFIG)

    st.subheader("② 채널·만족도로 본 이탈")
    st.plotly_chart(build_chart2_channel_csat(consultations, satisfaction), width="stretch", config=c.PLOTLY_CONFIG)

    st.subheader("③ 재문의 반복으로 본 이탈")
    st.plotly_chart(build_chart3_recontact_bucket(customers, consultations), width="stretch", config=c.PLOTLY_CONFIG)

    st.subheader("④ 요금제로 본 이탈")
    st.plotly_chart(build_chart4_plan(customers), width="stretch", config=c.PLOTLY_CONFIG)

    st.subheader("⑤ 지역으로 본 이탈")
    st.plotly_chart(build_chart5_region(customers), width="stretch", config=c.PLOTLY_CONFIG)

    st.subheader("⑥ 가입기간·이용량으로 본 이탈")
    st.plotly_chart(build_chart6_tenure_usage(customers, usage), width="stretch", config=c.PLOTLY_CONFIG)


# ------------------------- 페이지 2: 개선 제안 리포트 -------------------------

def markdown_to_pdf_bytes(md_text, title):
    from fpdf import FPDF

    font_path = os.path.join(BASE_DIR, "assets", "NanumSquare_acR.ttf")
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Nanum", "", font_path)
    pdf.set_font("Nanum", size=11)
    pdf.set_title(title)

    for raw_line in md_text.split("\n"):
        line = raw_line.rstrip()
        pdf.set_x(pdf.l_margin)
        if line.startswith("# "):
            pdf.set_font("Nanum", size=18)
            pdf.multi_cell(0, 10, line[2:])
            pdf.set_font("Nanum", size=11)
        elif line.startswith("## "):
            pdf.ln(2)
            pdf.set_x(pdf.l_margin)
            pdf.set_font("Nanum", size=14)
            pdf.multi_cell(0, 8, line[3:])
            pdf.set_font("Nanum", size=11)
        elif line.startswith("|"):
            continue  # 마크다운 표는 PDF에서는 생략 (본문 텍스트 위주로 변환)
        elif line.startswith("- ") or line.startswith(("1. ", "2. ", "3. ")):
            pdf.multi_cell(0, 7, "- " + line.lstrip("-123456789. "))
        elif line.strip() == "":
            pdf.ln(3)
        else:
            pdf.multi_cell(0, 7, line)

    return bytes(pdf.output())


def report_page():
    c.render_hero("개선 제안 리포트", "이탈 원인 분석을 바탕으로 한 고객서비스 만족도 개선 제안")

    report_path = os.path.join(REPORT_DIR, "고객서비스_만족도개선_리포트.md")
    if not os.path.exists(report_path):
        st.warning(f"리포트 파일이 없습니다: {report_path}")
        return

    with open(report_path, encoding="utf-8") as f:
        md_text = f.read()

    st.markdown(md_text)

    pdf_bytes = markdown_to_pdf_bytes(md_text, "고객서비스 만족도 개선 제안 리포트")
    st.download_button(
        "📄 PDF 다운로드", data=pdf_bytes,
        file_name="고객서비스_만족도개선_리포트.pdf", mime="application/pdf",
    )


# ------------------------- 페이지 3: 채널 효율 -------------------------

def channel_efficiency_page():
    c.render_hero("채널 효율", "채널별 유입 1건당 비용 — 다음 분기 예산 배분의 근거")

    spend_df = load_marketing_spend()
    total_spend = spend_df["spend"].sum()
    total_signups = spend_df["signups"].sum()
    avg_cost = total_spend / total_signups

    col1, col2, col3 = st.columns(3)
    with col1:
        c.render_stat_tile("총 집행액", f"{total_spend:,.0f}원")
    with col2:
        c.render_stat_tile("총 유입", f"{total_signups:,}건")
    with col3:
        c.render_stat_tile("평균 유입단가", f"{avg_cost:,.0f}원")

    st.plotly_chart(build_channel_efficiency_bar(spend_df), width="stretch", config=c.PLOTLY_CONFIG)
    st.plotly_chart(build_channel_efficiency_compare(spend_df), width="stretch", config=c.PLOTLY_CONFIG)


# ------------------------- 페이지 4: 검색광고 성과 -------------------------

def build_ad_device_ctr(media_df):
    """디바이스별 CTR 비교. CTR이 더 낮은(비효율) 디바이스만 COLOR_HIGHLIGHT로 강조."""
    g = media_df.groupby("디바이스").agg(노출수=("노출수", "sum"), 클릭수=("클릭수", "sum")).reset_index()
    g["CTR"] = g["클릭수"] / g["노출수"] * 100
    worst_device = g.loc[g["CTR"].idxmin(), "디바이스"]

    fig = px.bar(
        g, x="디바이스", y="CTR", color="디바이스",
        color_discrete_map={d: (c.COLOR_HIGHLIGHT if d == worst_device else c.COLOR_BASE) for d in g["디바이스"]},
        custom_data=["노출수", "클릭수"],
        title=f"디바이스별 CTR (강조: {worst_device})",
        labels={"CTR": "CTR (%)", "디바이스": ""},
        text=g["CTR"].map(lambda v: f"{v:.2f}%"),
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>노출수: %{customdata[0]:,}<br>클릭수: %{customdata[1]:,}<br>CTR: %{y:.2f}%<extra></extra>",
        textposition="outside",
    )
    fig.update_layout(showlegend=False, yaxis_range=[0, g["CTR"].max() * 1.3], **c.CHART_LAYOUT)
    return fig


def build_ad_campaign_cpa(media_df, signup_df):
    """캠페인별 CPA(광고비÷가입건수) 비교. 가장 비효율적인 캠페인만 강조."""
    spend = media_df.groupby("캠페인")["광고비"].sum()
    signups = signup_df.groupby("캠페인")["가입건수"].sum()
    g = pd.concat([spend, signups], axis=1).reset_index().rename(columns={"index": "캠페인"})
    g = g[g["가입건수"] > 0].copy()
    g["CPA"] = g["광고비"] / g["가입건수"]
    g = g.sort_values("CPA", ascending=False)
    worst_campaign = g.iloc[0]["캠페인"]

    fig = px.bar(
        g, x="캠페인", y="CPA", color="캠페인",
        color_discrete_map={p: (c.COLOR_HIGHLIGHT if p == worst_campaign else c.COLOR_BASE) for p in g["캠페인"]},
        custom_data=["광고비", "가입건수"],
        title="캠페인별 CPA (광고비÷가입건수, 비효율 높은 순 정렬)",
        labels={"CPA": "CPA (원)", "캠페인": ""},
        text=g["CPA"].map(lambda v: f"{v:,.0f}원"),
    )
    fig.update_traces(
        hovertemplate="<b>%{x}</b><br>광고비: %{customdata[0]:,}원<br>가입건수: %{customdata[1]:,}건<br>CPA: %{y:,.0f}원<extra></extra>",
        textposition="outside",
    )
    fig.update_layout(showlegend=False, yaxis_range=[0, g["CPA"].max() * 1.3], **c.CHART_LAYOUT)
    return fig


def ad_performance_page():
    c.render_hero("검색광고 성과", "자동차보험 검색광고 — 디바이스·캠페인별 효율 (오늘 정제한 합성 데이터 기준)")

    media_df = load_ad_performance()
    signup_df = load_signup_revenue()

    total_spend = media_df["광고비"].sum()
    total_clicks = media_df["클릭수"].sum()
    total_signups = signup_df["가입건수"].sum()

    col1, col2, col3 = st.columns(3)
    with col1:
        c.render_stat_tile("총 광고비", f"{total_spend:,.0f}원")
    with col2:
        c.render_stat_tile("총 클릭수", f"{total_clicks:,}회")
    with col3:
        c.render_stat_tile("총 가입건수", f"{total_signups:,}건")

    st.plotly_chart(build_ad_device_ctr(media_df), width="stretch", config=c.PLOTLY_CONFIG)
    st.plotly_chart(build_ad_campaign_cpa(media_df, signup_df), width="stretch", config=c.PLOTLY_CONFIG)

    st.caption(
        "⚠️ 합성 연습 데이터 기준입니다 (data_messy_검색광고성과.csv, data_messy_가입매출.csv를 오늘 정제). "
        "실제 회사 데이터가 아니므로 수치는 참고용입니다."
    )


# ------------------------- 앱 조립 (st.navigation) -------------------------

st.set_page_config(page_title="고객은 왜 이탈하는가", layout="wide")

pages = [
    st.Page(dashboard_page, title="대시보드", default=True),
    st.Page(report_page, title="개선 제안 리포트"),
    st.Page(channel_efficiency_page, title="채널 효율"),
    st.Page(ad_performance_page, title="검색광고 성과"),
]
pg = st.navigation(pages)
pg.run()
