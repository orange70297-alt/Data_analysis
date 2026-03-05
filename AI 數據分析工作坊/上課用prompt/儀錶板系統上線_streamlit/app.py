# -*- coding: utf-8 -*-
"""
RFM 客群與沈睡 VIP 召回監控儀表板
依據：動態儀表板藍圖_RFM沈睡VIP.md × Streamlit_App_Generator_Prompt.md
"""

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 色系：深海洞察
PALETTE = {
    "primary": "#003366",
    "highlight1": "#007BFF",
    "highlight2": "#FD7E14",
    "neutral_light": "#CED4DA",
    "neutral_mid": "#6C757D",
    "teal": "#20C997",
    "amber": "#FFC107",
}

SEGMENT_ORDER = ["活躍 VIP", "沈睡 VIP", "一般流失", "一般活躍", "潛力新客"]

# 路徑：app 在 儀錶板系統上線_streamlit，資料在 02數據分析
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "02數據分析")


@st.cache_data
def load_segment_summary():
    path = os.path.join(DATA_DIR, "rfm_segment_summary.csv")
    df = pd.read_csv(path, encoding="utf-8")
    df = df.set_index("Segment").reindex(SEGMENT_ORDER).reset_index()
    return df


@st.cache_data
def load_sleep_vip_list():
    path = os.path.join(DATA_DIR, "sleep_vip_list.csv")
    return pd.read_csv(path, encoding="utf-8")


def render_kpi_cards(df_summary: pd.DataFrame):
    """核心 KPI 卡片：有效客戶數、總營收、沈睡 VIP 人數／營收佔比／平均客單價"""
    total_customers = int(df_summary["CustomerCount"].sum())
    total_revenue = df_summary["TotalRevenue"].sum()
    sleep_row = df_summary[df_summary["Segment"] == "沈睡 VIP"]
    sleep_count = int(sleep_row["CustomerCount"].iloc[0]) if len(sleep_row) else 0
    sleep_revenue_pct = sleep_row["RevenuePct"].iloc[0] if len(sleep_row) else 0
    sleep_avg = sleep_row["AvgMonetary"].iloc[0] if len(sleep_row) else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("有效客戶數", f"{total_customers:,}", help="不重複客戶數（RFM 分析樣本）")
    col2.metric("總營收 (£)", f"£{total_revenue/1e6:.2f}M", help="分析範圍內總營收")
    col3.metric("沈睡 VIP 人數", f"{sleep_count:,}", help="回歸優惠券優先名單規模")
    col4.metric("沈睡 VIP 營收佔比", f"{sleep_revenue_pct:.1f}%", help="歷史營收貢獻佔比")
    col5.metric("沈睡 VIP 平均客單價", f"£{sleep_avg:,.0f}", help="優惠力度參考")


def render_grouped_bar(df: pd.DataFrame):
    """客群人數 vs 營收貢獻 — 分組柱狀圖"""
    df = df.copy()
    df["人數佔比"] = df["CustomerPct"]
    df["營收佔比"] = df["RevenuePct"]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="人數佔比", x=df["Segment"], y=df["人數佔比"], marker_color=PALETTE["neutral_light"], text=df["人數佔比"].round(1).astype(str) + "%", textposition="outside"))
    fig.add_trace(go.Bar(name="營收佔比", x=df["Segment"], y=df["營收佔比"], marker_color=[PALETTE["highlight1"] if s == "活躍 VIP" else (PALETTE["highlight2"] if s == "沈睡 VIP" else PALETTE["primary"]) for s in df["Segment"]], text=df["營收佔比"].round(1).astype(str) + "%", textposition="outside"))
    fig.update_layout(barmode="group", title="客群人數 vs 營收貢獻 — 少數 VIP 撐起大半營收", title_font_size=14, xaxis_title="", yaxis_title="百分比 (%)", yaxis_range=[0, 85], legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), margin=dict(t=60), template="none", font=dict(size=11), paper_bgcolor="white", plot_bgcolor="white")
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=True, gridcolor=PALETTE["neutral_light"])
    st.plotly_chart(fig, use_container_width=True)


def render_combo_chart(df: pd.DataFrame):
    """各客群營收與平均客單價 — 柱狀 + 折線"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(name="總營收 (百萬 £)", x=df["Segment"], y=df["TotalRevenue"] / 1e6, marker_color=PALETTE["highlight1"], text= (df["TotalRevenue"]/1e6).round(2), textposition="outside"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["Segment"], y=df["AvgMonetary"], name="平均客單價 (£)", mode="lines+markers", line=dict(color=PALETTE["highlight2"], width=2), marker=dict(size=10)), secondary_y=True)
    fig.update_layout(title="各客群營收與平均客單價", title_font_size=14, margin=dict(t=60), template="none", paper_bgcolor="white", plot_bgcolor="white", legend=dict(orientation="h", yanchor="bottom", y=1.02))
    fig.update_xaxes(title_text="", showgrid=False)
    fig.update_yaxes(title_text="總營收 (百萬 £)", secondary_y=False, showgrid=True, gridcolor=PALETTE["neutral_light"])
    fig.update_yaxes(title_text="平均客單價 (£)", secondary_y=True, showgrid=False)
    st.plotly_chart(fig, use_container_width=True)


def render_funnel():
    """有效分析樣本漏斗 — 階梯式"""
    labels = ["原始明細", "排除 CustomerID 缺失", "排除無效交易"]
    values = [1067371, 824364, 805547]
    colors = [PALETTE["primary"], PALETTE["neutral_light"], PALETTE["teal"]]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors, text=[f"{v:,}" for v in values], textposition="outside"))
    fig.update_layout(title="有效分析樣本：106 萬筆 → 5,877 人", title_font_size=14, xaxis_title="", yaxis_title="明細筆數", margin=dict(t=60), template="none", paper_bgcolor="white", plot_bgcolor="white", annotations=[dict(text="805,547 筆對應 5,877 位不重複客戶", x=2, y=805547+30000, showarrow=False, font=dict(size=10))])
    fig.update_xaxes(tickvals=[0,1,2], ticktext=["1,067,371 筆", "824,364 筆", "805,547 筆<br>(5,877 人)"])
    st.plotly_chart(fig, use_container_width=True)


def render_donut(df: pd.DataFrame):
    """營收構成 — 環圈圖"""
    fig = go.Figure(data=[go.Pie(labels=df["Segment"], values=df["RevenuePct"], hole=0.5, marker_colors=[PALETTE["highlight1"], PALETTE["highlight2"], PALETTE["neutral_light"], PALETTE["teal"], PALETTE["amber"]], textinfo="label+percent", textposition="outside", hovertemplate="%{label}<br>%{value:.1f}%<extra></extra>")])
    fig.update_layout(title="營收來源結構 — 五客群貢獻佔比", title_font_size=14, margin=dict(t=60), showlegend=True, legend=dict(orientation="h", yanchor="bottom"), annotations=[dict(text="£17.72M", x=0.5, y=0.5, font_size=14, showarrow=False)], paper_bgcolor="white", plot_bgcolor="white")
    st.plotly_chart(fig, use_container_width=True)


def render_sleep_vs_lost_bar(df: pd.DataFrame):
    """沈睡 VIP vs 一般流失 平均客單價"""
    sub = df[df["Segment"].isin(["沈睡 VIP", "一般流失"])][["Segment", "AvgMonetary"]]
    fig = px.bar(sub, x="Segment", y="AvgMonetary", color="Segment", color_discrete_map={"沈睡 VIP": PALETTE["highlight2"], "一般流失": PALETTE["neutral_light"]}, text=sub["AvgMonetary"].apply(lambda x: f"£{x:,.0f}"))
    fig.update_layout(title="沈睡 VIP vs 一般流失 平均客單價", title_font_size=14, xaxis_title="", yaxis_title="平均客單價 (£)", showlegend=False, margin=dict(t=60), template="none", paper_bgcolor="white", plot_bgcolor="white")
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)


def main():
    st.set_page_config(page_title="RFM 客群與沈睡 VIP 召回監控", page_icon="📊", layout="wide")

    st.title("📊 RFM 客群與沈睡 VIP 召回監控")
    st.caption("分析基準日 2011-12-09｜有效客戶 5,877 人｜總營收 £17.72M")

    df_summary = load_segment_summary()
    df_sleep = load_sleep_vip_list()

    # --- 側邊欄篩選 ---
    st.sidebar.header("篩選器")
    segments_selected = st.sidebar.multiselect("客群", SEGMENT_ORDER, default=SEGMENT_ORDER, help="圖表僅顯示所選客群")
    sort_sleep = st.sidebar.selectbox("沈睡 VIP 名單排序", ["營收 (TotalAmount) 高→低", "Recency 高→低"], index=0)
    n_display = st.sidebar.selectbox("名單顯示筆數", [50, 100, 200, "全部"], index=1)

    df_summary_f = df_summary[df_summary["Segment"].isin(segments_selected)] if segments_selected else df_summary

    # 名單排序：營收高→低 或 Recency 高→低（愈久未購愈前）
    df_sleep_sorted = df_sleep.sort_values("TotalAmount", ascending=False) if sort_sleep.startswith("營收") else df_sleep.sort_values("Recency", ascending=False)
    n_show = None if n_display == "全部" else (int(n_display) if isinstance(n_display, str) else n_display)
    df_sleep_display = df_sleep_sorted.head(n_show) if n_show else df_sleep_sorted

    # --- KPI 卡片（依全量資料計算，不受客群篩選影響）---
    render_kpi_cards(df_summary)

    st.divider()

    # --- 左欄：分組柱狀、組合圖、漏斗 ---
    col_left, col_right = st.columns([3, 2])

    with col_left:
        render_grouped_bar(df_summary_f)
        render_combo_chart(df_summary_f)
        render_funnel()

    with col_right:
        render_donut(df_summary_f)
        render_sleep_vs_lost_bar(df_summary_f)
        st.info("7.5% 客戶貢獻逾 10% 營收，建議優先發券並提高優惠力度。")

    st.divider()
    st.subheader("沈睡 VIP 名單（回歸優惠券優先名單）")

    st.dataframe(df_sleep_display, use_container_width=True, column_config={"CustomerID": st.column_config.NumberColumn(format="%d"), "Recency": "距今天數", "Frequency": "訂單次數", "TotalAmount": st.column_config.NumberColumn("總消費 (£)", format="£%.2f")})

    csv = df_sleep_display.to_csv(index=False).encode("utf-8-sig")
    st.download_button("下載沈睡 VIP 名單 CSV", data=csv, file_name="sleep_vip_list.csv", mime="text/csv")


if __name__ == "__main__":
    main()
