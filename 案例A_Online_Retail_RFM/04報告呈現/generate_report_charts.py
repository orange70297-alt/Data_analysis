# -*- coding: utf-8 -*-
"""
靜態分析報告圖表產出腳本
依據：圖表設計建議_v2.md、色系風格.md（深海洞察）
讀取 02數據分析 之 RFM 摘要與漏斗數據，產出 5 張圖表至本資料夾。
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# 路徑：腳本在 04報告呈現，資料在 02數據分析
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "02數據分析")
OUTPUT_DIR = SCRIPT_DIR

# 色系風格：深海洞察 (Deep Sea Insight)
PALETTE = {
    "primary": "#003366",      # 深海藍
    "highlight1": "#007BFF",   # 海洋藍
    "highlight2": "#FD7E14",   # 珊瑚橙
    "neutral_light": "#CED4DA", # 淺灰
    "neutral_mid": "#6C757D",  # 中灰
    "teal": "#20C997",         # 水鴨綠
    "amber": "#FFC107",        # 陽光黃
}

# 客群顯示順序（依營收佔比由高到低）
SEGMENT_ORDER = ["活躍 VIP", "沈睡 VIP", "一般流失", "一般活躍", "潛力新客"]


def load_segment_summary():
    path = os.path.join(DATA_DIR, "rfm_segment_summary.csv")
    df = pd.read_csv(path, encoding="utf-8")
    df = df.set_index("Segment").loc[SEGMENT_ORDER].reset_index()
    return df


def setup_style(ax, title=None, subtitle=None):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", colors=PALETTE["neutral_mid"])
    if title and subtitle:
        ax.set_title(f"{title}\n{subtitle}", fontsize=12, fontweight="bold", color=PALETTE["primary"])
    elif title:
        ax.set_title(title, fontsize=14, fontweight="bold", color=PALETTE["primary"], pad=8)


def chart1_grouped_bar(df):
    """設計建議一：客群人數 vs 營收貢獻 — 分組柱狀圖"""
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(df))
    w = 0.35
    bars1 = ax.bar(x - w/2, df["CustomerPct"], w, label="人數佔比", color=PALETTE["neutral_light"], edgecolor=PALETTE["neutral_mid"])
    bars2 = ax.bar(x + w/2, df["RevenuePct"], w, label="營收佔比",
                   color=[PALETTE["highlight1"] if s == "活躍 VIP" else (PALETTE["highlight2"] if s == "沈睡 VIP" else PALETTE["primary"]) for s in df["Segment"]],
                   edgecolor=PALETTE["neutral_mid"])
    ax.set_xticks(x)
    ax.set_xticklabels(df["Segment"], fontsize=10)
    ax.set_ylabel("百分比 (%)", fontsize=10, color=PALETTE["neutral_mid"])
    ax.set_ylim(0, 85)
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    for i, (_, row) in enumerate(df.iterrows()):
        if row["Segment"] in ("活躍 VIP", "沈睡 VIP"):
            ax.annotate(f"{row['RevenuePct']}%", xy=(i + w/2, row["RevenuePct"] + 1), ha="center", fontsize=9, fontweight="bold", color=PALETTE["primary"])
    ax.axhline(y=0, color=PALETTE["neutral_mid"], linewidth=0.5)
    setup_style(ax,
        "客群人數 vs 營收貢獻 — 少數 VIP 撐起大半營收",
        "RFM 五區隔之人數佔比與營收佔比（有效客戶 5,877 人，總營收 £17.72M）")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "chart1_客群人數與營收佔比.png"), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("已產出: chart1_客群人數與營收佔比.png")


def chart2_combo(df):
    """設計建議二：各客群營收與平均客單價 — 柱狀 + 折線"""
    fig, ax1 = plt.subplots(figsize=(10, 5))
    x = np.arange(len(df))
    ax1.bar(x - 0.2, df["TotalRevenue"] / 1e6, 0.4, label="總營收 (百萬 £)", color=PALETTE["highlight1"], alpha=0.85)
    ax1.set_ylabel("總營收 (百萬 £)", fontsize=10, color=PALETTE["highlight1"])
    ax1.set_ylim(0, 15)
    ax1.tick_params(axis="y", labelcolor=PALETTE["highlight1"])
    ax2 = ax1.twinx()
    ax2.plot(x, df["AvgMonetary"], "o-", color=PALETTE["highlight2"], linewidth=2, markersize=8, label="平均客單價 (£)")
    ax2.set_ylabel("平均客單價 (£)", fontsize=10, color=PALETTE["highlight2"])
    ax2.tick_params(axis="y", labelcolor=PALETTE["highlight2"])
    ax2.set_ylim(0, 10000)
    for i, (_, row) in enumerate(df.iterrows()):
        if row["Segment"] in ("沈睡 VIP", "一般流失"):
            ax2.annotate(f"£{int(row['AvgMonetary'])}", xy=(i, row["AvgMonetary"]), xytext=(0, 8), textcoords="offset points", ha="center", fontsize=8, color=PALETTE["highlight2"])
    ax1.set_xticks(x)
    ax1.set_xticklabels(df["Segment"], fontsize=10)
    ax1.legend(loc="upper right", frameon=False, fontsize=9)
    ax2.legend(loc="upper left", frameon=False, fontsize=9)
    setup_style(ax1,
        "各客群營收與平均客單價",
        "營收（柱狀）與平均客單價 £（折線），供行銷預算與優惠力度參考")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "chart2_營收與平均客單價.png"), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("已產出: chart2_營收與平均客單價.png")


def chart3_waterfall():
    """設計建議三：有效分析樣本漏斗 — 階梯式（明細筆數）"""
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = ["原始明細", "排除 CustomerID 缺失", "排除無效交易"]
    heights = [1067371, 824364, 805547]
    sublabels = ["1,067,371 筆", "824,364 筆", "805,547 筆\n(5,877 人)"]
    x = np.arange(len(labels))
    bar_colors = [PALETTE["primary"], PALETTE["neutral_light"], PALETTE["teal"]]
    bars = ax.bar(x, heights, color=bar_colors, edgecolor=PALETTE["neutral_mid"])
    ax.set_xticks(x)
    ax.set_xticklabels([f"{lb}\n{sub}" for lb, sub in zip(labels, sublabels)], fontsize=9)
    ax.set_ylabel("明細筆數", fontsize=10, color=PALETTE["neutral_mid"])
    ax.set_ylim(0, 1.12 * 1067371)
    for i, h in enumerate(heights):
        ax.annotate(f"{h:,}", xy=(i, h + 25000), ha="center", fontsize=10, fontweight="bold", color=PALETTE["primary"])
    setup_style(ax,
        "有效分析樣本如何從 106 萬筆到 5,877 人",
        "依明細筆數篩選階段；805,547 筆對應 5,877 位不重複客戶（RFM 分析單位為客戶）")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "chart3_樣本漏斗.png"), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("已產出: chart3_樣本漏斗.png")


def chart4_sleep_vip_kpi(df):
    """設計建議四：沈睡 VIP 關鍵指標 — KPI 卡 + 條形對比"""
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    sleep = df[df["Segment"] == "沈睡 VIP"].iloc[0]
    lost = df[df["Segment"] == "一般流失"].iloc[0]
    # 左：KPI 文字卡
    ax1 = axes[0]
    ax1.axis("off")
    kpis = [
        ("沈睡 VIP 人數", f"{int(sleep['CustomerCount']):,} 人", f"({sleep['CustomerPct']}%)"),
        ("營收貢獻", f"£{sleep['TotalRevenue']/1e6:.2f}M", f"({sleep['RevenuePct']}%)"),
        ("平均客單價", f"£{sleep['AvgMonetary']:,.0f}", ""),
    ]
    y_pos = 0.85
    ax1.text(0.5, 0.95, "沈睡 VIP 關鍵指標", ha="center", fontsize=14, fontweight="bold", color=PALETTE["primary"])
    ax1.text(0.5, 0.88, "回歸優惠券優先名單（基準日 2011-12-09）", ha="center", fontsize=9, color=PALETTE["neutral_mid"])
    for label, val, sub in kpis:
        ax1.text(0.1, y_pos, label, fontsize=11, color=PALETTE["neutral_mid"])
        ax1.text(0.7, y_pos, val, ha="right", fontsize=11, fontweight="bold", color=PALETTE["highlight1"])
        if sub:
            ax1.text(0.95, y_pos, sub, ha="right", fontsize=9, color=PALETTE["neutral_mid"])
        y_pos -= 0.2
    ax1.text(0.5, 0.05, "7.5% 客戶貢獻逾 10% 營收，建議優先發券並提高優惠力度。", ha="center", fontsize=9, style="italic", color=PALETTE["primary"])
    # 右：沈睡 VIP vs 一般流失 平均客單價
    ax2 = axes[1]
    segs = ["沈睡 VIP", "一般流失"]
    avgs = [sleep["AvgMonetary"], lost["AvgMonetary"]]
    colors_bar = [PALETTE["highlight2"], PALETTE["neutral_light"]]
    bars = ax2.barh(segs, avgs, color=colors_bar, edgecolor=PALETTE["neutral_mid"])
    ax2.set_xlabel("平均客單價 (£)", fontsize=10, color=PALETTE["neutral_mid"])
    for i, (s, v) in enumerate(zip(segs, avgs)):
        ax2.annotate(f"£{v:,.0f}", xy=(v + 50, i), va="center", fontsize=10, fontweight="bold", color=PALETTE["primary"])
    setup_style(ax2, "沈睡 VIP vs 一般流失 平均客單價", None)
    plt.suptitle("沈睡 VIP 關鍵指標 — 回歸優惠券優先名單", fontsize=12, fontweight="bold", color=PALETTE["primary"], y=1.02)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "chart4_沈睡VIP關鍵指標.png"), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("已產出: chart4_沈睡VIP關鍵指標.png")


def chart5_donut(df):
    """設計建議五：營收來源結構 — 環圈圖"""
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = [PALETTE["highlight1"], PALETTE["highlight2"], PALETTE["neutral_light"], PALETTE["teal"], PALETTE["amber"]]
    wedges, texts, autotexts = ax.pie(
        df["RevenuePct"], labels=df["Segment"], autopct="%1.1f%%",
        colors=colors, startangle=90, pctdistance=0.75,
        wedgeprops=dict(width=0.5, edgecolor="white", linewidth=1.5),
        textprops=dict(fontsize=10, color=PALETTE["primary"]),
    )
    for t in autotexts:
        t.set_fontweight("bold")
        t.set_color("white")
    ax.text(0, 0, "總營收\n£17.72M", ha="center", va="center", fontsize=11, fontweight="bold", color=PALETTE["primary"])
    setup_style(ax,
        "營收來源結構 — 五客群貢獻佔比",
        "總營收 £17,722,007，依 RFM 區隔")
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "chart5_營收構成環圈圖.png"), dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print("已產出: chart5_營收構成環圈圖.png")


def main():
    mpl.rcParams["font.sans-serif"] = ["Microsoft JhengHei", "SimHei", "DejaVu Sans"]
    mpl.rcParams["axes.unicode_minus"] = False
    df = load_segment_summary()
    chart1_grouped_bar(df)
    chart2_combo(df)
    chart3_waterfall()
    chart4_sleep_vip_kpi(df)
    chart5_donut(df)
    print("圖表已全部產出至:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
