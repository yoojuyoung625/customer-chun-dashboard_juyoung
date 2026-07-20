import os

import pandas as pd
import plotly.express as px

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")

COLOR_BASE = "#8a8f98"       # 전체 고객: 중립 회색
COLOR_HIGHLIGHT = "#d03b3b"  # 서비스불만 부정 VOC 고객: 강조 빨강


def compute_churn_rates():
    voc = pd.read_csv(os.path.join(DATA_DIR, "data_voc.csv"), encoding="utf-8-sig")
    customers = pd.read_csv(os.path.join(DATA_DIR, "data_customers.csv"), encoding="utf-8-sig")

    target = voc[(voc["category"] == "서비스불만") & (voc["sentiment"] == "부정")]
    target_ids = target["customer_id"].unique()
    target_customers = customers[customers["customer_id"].isin(target_ids)]

    total_n = len(customers)
    total_churn_n = int((customers["churn_yn"] == "Y").sum())
    total_churn_rate = total_churn_n / total_n * 100

    target_n = len(target_customers)
    target_churn_n = int((target_customers["churn_yn"] == "Y").sum())
    target_churn_rate = target_churn_n / target_n * 100

    return pd.DataFrame([
        {"구분": "전체 고객", "고객수": total_n, "이탈고객수": total_churn_n, "이탈율": total_churn_rate},
        {"구분": "서비스불만 부정\nVOC 이력 있음", "고객수": target_n, "이탈고객수": target_churn_n, "이탈율": target_churn_rate},
    ])


def main():
    df = compute_churn_rates()

    fig = px.bar(
        df,
        x="구분",
        y="이탈율",
        color="구분",
        color_discrete_map={
            "전체 고객": COLOR_BASE,
            "서비스불만 부정\nVOC 이력 있음": COLOR_HIGHLIGHT,
        },
        custom_data=["고객수", "이탈고객수"],
        title="전체 고객 vs 서비스불만 부정 VOC 고객 이탈율 비교",
        labels={"이탈율": "이탈율 (%)", "구분": ""},
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>"
            "고객 수: %{customdata[0]}명<br>"
            "이탈 고객 수: %{customdata[1]}명<br>"
            "이탈율: %{y:.1f}%<extra></extra>"
        ),
        texttemplate="%{y:.1f}%",
        textposition="outside",
    )

    fig.update_layout(
        showlegend=False,
        yaxis_range=[0, df["이탈율"].max() * 1.35],
        plot_bgcolor="#fcfcfb",
        paper_bgcolor="#fcfcfb",
    )

    fig.show()


if __name__ == "__main__":
    main()
