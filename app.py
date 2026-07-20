import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

COLOR_BASE = "#8a8f98"
COLOR_HIGHLIGHT = "#d03b3b"
COLOR_CSAT = "#2a78d6"
COLOR_RECONTACT = "#d03b3b"
COLOR_MAP_CHURN = {"Y": "#d03b3b", "N": "#2a78d6"}
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
        color_discrete_map={"전체 고객": COLOR_BASE, "서비스불만 부정\nVOC 이력 있음": COLOR_HIGHLIGHT},
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
        plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb",
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
            x=g["channel"], y=g["CSAT평균"], name="CSAT 평균", marker_color=COLOR_CSAT,
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
            line=dict(color=COLOR_RECONTACT, width=3), marker=dict(size=9, color=COLOR_RECONTACT),
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
        hovermode="x unified", plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
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
        color_discrete_map={"0회": COLOR_BASE, "1회": COLOR_BASE, "2회 이상": COLOR_HIGHLIGHT},
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
        y=overall_rate, line_dash="dot", line_color="#0b0b0b",
        annotation_text=f"전체 평균 이탈율 {overall_rate:.1f}%", annotation_position="top left",
    )
    fig.update_layout(
        showlegend=False, yaxis_range=[0, max(g["이탈율"].max(), overall_rate) * 1.3],
        plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb",
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
        color_discrete_map={p: (COLOR_HIGHLIGHT if p == HIGHLIGHT_PLAN else COLOR_BASE) for p in g["plan_type"]},
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
        plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb",
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
        color_discrete_map={r: (COLOR_HIGHLIGHT if r in HIGHLIGHT_REGIONS else COLOR_BASE) for r in g["region"]},
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
        plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb", margin=dict(b=90),
    )
    fig.add_annotation(
        text=(
            f"※ 부산은 표본 {int(busan['고객수'])}건 중 이탈 {int(busan['이탈고객수'])}건뿐이라 "
            f"이탈율({busan['이탈율']:.1f}%)이 매우 낮게 나타남 — 이탈 건수 자체가 적어 해석에 주의 필요"
        ),
        showarrow=False, xref="paper", yref="paper", x=0, y=-0.28, align="left",
        font=dict(size=11, color="#52514e"),
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
        color_discrete_map=COLOR_MAP_CHURN,
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
    fig.update_layout(plot_bgcolor="#fcfcfb", paper_bgcolor="#fcfcfb", legend_title_text="이탈 여부")
    return fig


# ------------------------- 앱 조립 -------------------------

def main():
    st.set_page_config(page_title="고객은 왜 이탈하는가", layout="wide")
    st.title("고객은 왜 이탈하는가 — 이탈 원인 진단 대시보드")

    customers = load_customers()
    voc = load_voc()
    consultations = load_consultations()
    satisfaction = load_satisfaction()
    usage = load_usage()

    total_n, churn_n, churn_rate = compute_overview_metrics(customers)
    col1, col2, col3 = st.columns(3)
    col1.metric("전체 고객 수", f"{total_n}명")
    col2.metric("이탈 고객 수", f"{churn_n}명")
    col3.metric("전체 이탈율", f"{churn_rate:.1f}%")

    st.subheader("① VOC로 본 이탈")
    st.plotly_chart(build_chart1_voc(customers, voc), use_container_width=True)

    st.subheader("② 채널·만족도로 본 이탈")
    st.plotly_chart(build_chart2_channel_csat(consultations, satisfaction), use_container_width=True)

    st.subheader("③ 재문의 반복으로 본 이탈")
    st.plotly_chart(build_chart3_recontact_bucket(customers, consultations), use_container_width=True)

    st.subheader("④ 요금제로 본 이탈")
    st.plotly_chart(build_chart4_plan(customers), use_container_width=True)

    st.subheader("⑤ 지역으로 본 이탈")
    st.plotly_chart(build_chart5_region(customers), use_container_width=True)

    st.subheader("⑥ 가입기간·이용량으로 본 이탈")
    st.plotly_chart(build_chart6_tenure_usage(customers, usage), use_container_width=True)


if __name__ == "__main__":
    main()
