import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")

COLOR_CSAT = "#2a78d6"       # 팔레트 categorical slot 1 (blue) — 막대(CSAT)
COLOR_RECONTACT = "#d03b3b"  # 팔레트 status critical (red) — 꺾은선(재문의율)


def compute_channel_stats():
    sat = pd.read_csv(os.path.join(DATA_DIR, "data_satisfaction.csv"), encoding="utf-8-sig")
    cons = pd.read_csv(os.path.join(DATA_DIR, "data_consultations.csv"), encoding="utf-8-sig")

    merged = sat.merge(cons[["consult_id", "channel", "is_repeat"]], on="consult_id", how="left")

    g = merged.groupby("channel").agg(
        CSAT평균=("score", "mean"),
        재문의율=("is_repeat", lambda s: (s == "Y").mean() * 100),
        n=("consult_id", "count"),
    )
    return g.sort_values("CSAT평균").reset_index()


def main():
    df = compute_channel_stats()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(
        go.Bar(
            x=df["channel"],
            y=df["CSAT평균"],
            name="CSAT 평균",
            marker_color=COLOR_CSAT,
            customdata=df[["재문의율", "n"]],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "CSAT 평균: %{y:.2f}점<br>"
                "재문의율: %{customdata[0]:.1f}%<br>"
                "상담 건수: %{customdata[1]}건<extra></extra>"
            ),
        ),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(
            x=df["channel"],
            y=df["재문의율"],
            name="재문의율",
            mode="lines+markers",
            line=dict(color=COLOR_RECONTACT, width=3),
            marker=dict(size=9, color=COLOR_RECONTACT),
            customdata=df[["CSAT평균", "n"]],
            hovertemplate=(
                "<b>%{x}</b><br>"
                "재문의율: %{y:.1f}%<br>"
                "CSAT 평균: %{customdata[0]:.2f}점<br>"
                "상담 건수: %{customdata[1]}건<extra></extra>"
            ),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        title="채널별 CSAT 평균(막대) vs 재문의율(꺾은선) — CSAT 낮은 순 정렬",
        hovermode="x unified",
        plot_bgcolor="#fcfcfb",
        paper_bgcolor="#fcfcfb",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(title_text="채널")
    fig.update_yaxes(title_text="CSAT 평균 (점)", secondary_y=False)
    fig.update_yaxes(title_text="재문의율 (%)", secondary_y=True, showgrid=False)

    fig.show()


if __name__ == "__main__":
    main()
