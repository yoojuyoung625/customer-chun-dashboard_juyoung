import os

import pandas as pd
import plotly.express as px

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")

CUTOFF_DATE = pd.Timestamp("2024-12-31")
COLOR_MAP = {"Y": "#d03b3b", "N": "#2a78d6"}  # 이탈=빨강, 유지=파랑


def compute_tenure_months(join_date):
    return (CUTOFF_DATE.year - join_date.dt.year) * 12 + (CUTOFF_DATE.month - join_date.dt.month)


def build_dataset():
    customers = pd.read_csv(os.path.join(DATA_DIR, "data_customers.csv"), encoding="utf-8-sig")
    usage = pd.read_csv(os.path.join(DATA_DIR, "data_usage_history.csv"), encoding="utf-8-sig")

    customers["join_date"] = pd.to_datetime(customers["join_date"])
    customers["가입기간_개월"] = compute_tenure_months(customers["join_date"])

    avg_usage_gb = (
        usage.groupby("customer_id")["data_usage_mb"].mean() / 1024
    ).rename("평균데이터사용량_GB")

    merged = customers.merge(avg_usage_gb, on="customer_id", how="left")
    return merged


def main():
    df = build_dataset()

    fig = px.scatter(
        df,
        x="가입기간_개월",
        y="평균데이터사용량_GB",
        color="churn_yn",
        color_discrete_map=COLOR_MAP,
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
            "customer_id: %{customdata[0]}<br>"
            "가입기간: %{customdata[1]}개월<br>"
            "평균 데이터 사용량: %{customdata[2]:.2f}GB<br>"
            "이탈 여부: %{customdata[3]}<extra></extra>"
        ),
        marker=dict(size=8),
    )

    fig.update_layout(
        plot_bgcolor="#fcfcfb",
        paper_bgcolor="#fcfcfb",
        legend_title_text="이탈 여부",
    )

    fig.show()


if __name__ == "__main__":
    main()
