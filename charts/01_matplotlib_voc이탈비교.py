import os
import platform

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")

COLOR_BASE = "#8a8f98"     # 전체 고객: 중립 회색
COLOR_HIGHLIGHT = "#d03b3b"  # 서비스불만 부정 VOC 고객: 강조 빨강
COLOR_MUTED_TEXT = "#52514e"
COLOR_AXIS = "#c3c2b7"
COLOR_GRID = "#e1e0d9"


def set_korean_font():
    system = platform.system()
    if system == "Windows":
        candidates = ["Malgun Gothic"]
    elif system == "Darwin":
        candidates = ["AppleGothic", "Apple SD Gothic Neo"]
    else:
        candidates = ["NanumGothic", "Noto Sans KR", "Noto Sans CJK KR"]

    available = {f.name for f in fm.fontManager.ttflist}
    chosen = next((name for name in candidates if name in available), None)
    if chosen is None:
        raise RuntimeError(
            f"'{system}'에서 사용 가능한 한글 폰트를 찾지 못함. 후보: {candidates}"
        )
    plt.rcParams["font.family"] = chosen
    plt.rcParams["axes.unicode_minus"] = False


def compute_churn_rates():
    voc = pd.read_csv(os.path.join(DATA_DIR, "data_voc.csv"), encoding="utf-8-sig")
    customers = pd.read_csv(os.path.join(DATA_DIR, "data_customers.csv"), encoding="utf-8-sig")

    target = voc[(voc["category"] == "서비스불만") & (voc["sentiment"] == "부정")]
    target_ids = target["customer_id"].unique()
    target_customers = customers[customers["customer_id"].isin(target_ids)]

    total_n = len(customers)
    total_churn_rate = (customers["churn_yn"] == "Y").mean() * 100

    target_n = len(target_customers)
    target_churn_rate = (target_customers["churn_yn"] == "Y").mean() * 100

    return {
        "전체 고객": (total_n, total_churn_rate),
        "서비스불만 부정\nVOC 이력 있음": (target_n, target_churn_rate),
    }


def main():
    set_korean_font()
    stats = compute_churn_rates()

    labels = list(stats.keys())
    rates = [v[1] for v in stats.values()]
    ns = [v[0] for v in stats.values()]
    colors = [COLOR_BASE, COLOR_HIGHLIGHT]

    fig, ax = plt.subplots(figsize=(6, 5.5), facecolor="#fcfcfb")
    ax.set_facecolor("#fcfcfb")

    bars = ax.bar(labels, rates, color=colors, width=0.5)

    for bar, rate, n in zip(bars, rates, ns):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(rates) * 0.02,
            f"{rate:.1f}%",
            ha="center", va="bottom",
            fontsize=13, fontweight="bold", color="#0b0b0b",
        )
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 2,
            f"n={n}",
            ha="center", va="center",
            fontsize=9, color="white",
        )

    ax.set_ylabel("이탈율 (%)")
    ax.set_ylim(0, max(rates) * 1.35)
    ax.set_title("전체 고객 vs 서비스불만 부정 VOC 고객 이탈율 비교", fontsize=12, color="#0b0b0b")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color(COLOR_AXIS)
    ax.tick_params(colors=COLOR_MUTED_TEXT)
    ax.yaxis.grid(True, color=COLOR_GRID, linewidth=0.8)
    ax.set_axisbelow(True)

    fig.tight_layout()

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(OUTPUT_DIR, "01_matplotlib_voc이탈비교.png")
    fig.savefig(out_path, dpi=150)
    print(f"저장 완료: {out_path}")


if __name__ == "__main__":
    main()
