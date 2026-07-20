import os

import pandas as pd
import plotly.express as px

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")

COLOR_BASE = "#8a8f98"
COLOR_HIGHLIGHT = "#d03b3b"
HIGHLIGHT_PLAN = "LTE베이직"  # 실제 데이터상 이탈율 1위 요금제


def compute_plan_churn():
    customers = pd.read_csv(os.path.join(DATA_DIR, "data_customers.csv"), encoding="utf-8-sig")
    g = customers.groupby("plan_type").agg(
        고객수=("churn_yn", "count"),
        이탈고객수=("churn_yn", lambda s: (s == "Y").sum()),
    )
    g["이탈율"] = g["이탈고객수"] / g["고객수"] * 100
    return g.sort_values("이탈율", ascending=False).reset_index()


def main():
    df = compute_plan_churn()

    fig = px.bar(
        df,
        x="plan_type",
        y="이탈율",
        color="plan_type",
        color_discrete_map={p: (COLOR_HIGHLIGHT if p == HIGHLIGHT_PLAN else COLOR_BASE) for p in df["plan_type"]},
        custom_data=["고객수", "이탈고객수"],
        title="요금제별 이탈율 (이탈율 높은 순 정렬, 강조: LTE베이직)",
        labels={"이탈율": "이탈율 (%)", "plan_type": "요금제"},
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
    )

    fig.show()


if __name__ == "__main__":
    main()
