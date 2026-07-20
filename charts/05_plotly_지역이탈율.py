import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")

COLOR_BASE = "#8a8f98"
COLOR_HIGHLIGHT = "#d03b3b"
HIGHLIGHT_REGIONS = {"대구", "인천"}  # 실제 데이터상 이탈율 상위 2개 지역


def compute_region_churn():
    customers = pd.read_csv(os.path.join(DATA_DIR, "data_customers.csv"), encoding="utf-8-sig")
    g = customers.groupby("region").agg(
        고객수=("churn_yn", "count"),
        이탈고객수=("churn_yn", lambda s: (s == "Y").sum()),
    )
    g["이탈율"] = g["이탈고객수"] / g["고객수"] * 100
    return g.sort_values("이탈율", ascending=False).reset_index()


def main():
    df = compute_region_churn()
    busan = df[df["region"] == "부산"].iloc[0]

    fig = px.bar(
        df,
        x="region",
        y="이탈율",
        color="region",
        color_discrete_map={r: (COLOR_HIGHLIGHT if r in HIGHLIGHT_REGIONS else COLOR_BASE) for r in df["region"]},
        custom_data=["고객수", "이탈고객수"],
        title="지역별 이탈율 (이탈율 높은 순 정렬, 강조: 대구·인천)",
        labels={"이탈율": "이탈율 (%)", "region": "지역"},
        text=df["이탈율"].map(lambda v: f"{v:.1f}%"),
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "고객 수: %{customdata[0]}명<br>"
            "이탈 고객 수: %{customdata[1]}명<br>"
            "이탈율: %{y:.1f}%<extra></extra>"
        ),
        textposition="outside",
    )

    fig.update_layout(
        showlegend=False,
        yaxis_range=[0, df["이탈율"].max() * 1.3],
        plot_bgcolor="#fcfcfb",
        paper_bgcolor="#fcfcfb",
        margin=dict(b=90),
    )
    fig.add_annotation(
        text=(
            f"※ 부산은 표본 {int(busan['고객수'])}건 중 이탈 {int(busan['이탈고객수'])}건뿐이라 "
            f"이탈율({busan['이탈율']:.1f}%)이 매우 낮게 나타남 — 이탈 건수 자체가 적어 해석에 주의 필요"
        ),
        showarrow=False,
        xref="paper", yref="paper",
        x=0, y=-0.28,
        align="left",
        font=dict(size=11, color="#52514e"),
    )

    fig.show()


if __name__ == "__main__":
    main()
