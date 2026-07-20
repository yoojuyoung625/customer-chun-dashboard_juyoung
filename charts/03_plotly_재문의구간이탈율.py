import os

import pandas as pd
import plotly.express as px

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")

COLOR_BASE = "#8a8f98"       # 0회/1회: 중립 회색
COLOR_HIGHLIGHT = "#d03b3b"  # 2회 이상: 강조 빨강
BUCKET_ORDER = ["0회", "1회", "2회 이상"]


def bucket_recontact(n):
    if n == 0:
        return "0회"
    if n == 1:
        return "1회"
    return "2회 이상"


def compute_bucket_churn():
    cons = pd.read_csv(os.path.join(DATA_DIR, "data_consultations.csv"), encoding="utf-8-sig")
    customers = pd.read_csv(os.path.join(DATA_DIR, "data_customers.csv"), encoding="utf-8-sig")

    recontact_n = cons[cons["is_repeat"] == "Y"].groupby("customer_id").size()
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
    return g, overall_rate


def main():
    df, overall_rate = compute_bucket_churn()

    fig = px.bar(
        df,
        x="구간",
        y="이탈율",
        color="구간",
        color_discrete_map={
            "0회": COLOR_BASE,
            "1회": COLOR_BASE,
            "2회 이상": COLOR_HIGHLIGHT,
        },
        category_orders={"구간": BUCKET_ORDER},
        custom_data=["고객수", "이탈고객수"],
        title="재문의 횟수 구간별 이탈율 (점선 = 전체 평균 이탈율)",
        labels={"이탈율": "이탈율 (%)", "구간": "재문의 횟수"},
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

    fig.add_hline(
        y=overall_rate,
        line_dash="dot",
        line_color="#0b0b0b",
        annotation_text=f"전체 평균 이탈율 {overall_rate:.1f}%",
        annotation_position="top left",
    )

    fig.update_layout(
        showlegend=False,
        yaxis_range=[0, max(df["이탈율"].max(), overall_rate) * 1.3],
        plot_bgcolor="#fcfcfb",
        paper_bgcolor="#fcfcfb",
    )

    fig.show()


if __name__ == "__main__":
    main()
